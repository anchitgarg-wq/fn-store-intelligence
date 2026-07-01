#!/usr/bin/env python3
"""
Steve Madden Store Dashboard - Backend Aggregation
---------------------------------------------------
Reads the 4 raw inputs, rolls everything up to the summary the frontend needs,
and writes summary.json.

Run this whenever data refreshes:
    python aggregate.py

Inputs (same folder unless overridden):
    001__Barcodewise_Sales_and_Stock-Inventory.xlsx   (master: inventory + WTD/MTD/YTD sales)
    01__Barcodewise_Sales_-_Datewise.xlsx             (yesterday snapshot)
    Key_Reference_SM.xlsx                             (barcode -> NEW Key)
    Image_URL_s_Part_1/2/3.xlsx                       (key/barcode -> image url)

Output:
    summary.json   (compact; what the dashboard embeds or fetches)

Key business rules (locked with stakeholder):
  * Rollup level = NEW Key (style-colour). Barcodes with no Key fall back to BC-<barcode>.
  * Period selector = Yesterday / WTD / MTD / YTD.
  * Weeks cover = Inventory Qty / weekly_rate ; weekly_rate = (WTD qty / days_elapsed)*7
        week starts Monday; days_elapsed computed from AS_OF_DATE (Mon=1..Sun=7).
        zero WTD qty -> weeks cover = None (shown as 'No sales').
  * Stock cost = Unit Cost * Inventory Qty. Stock mix(cost) and stock mix(qty) per category level.
  * Bottom 10: prefer SKUs (Keys) with sales history but lowest sales; if a store has >10 Keys
        with zero sales, pick the zero-sellers with highest inventory COST.
  * Images attach at Key level; missing -> placeholder handled by frontend.
"""
import pandas as pd, numpy as np, json, datetime as dt, warnings, sys, os
warnings.simplefilter('ignore')

U = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'summary.json'

# AS_OF_DATE: the data's as-of day (the "yesterday" the pull represents).
# Set/override at refresh time. Defaults to today-1.
AS_OF_DATE = os.environ.get('AS_OF_DATE')
AS_OF = dt.date.fromisoformat(AS_OF_DATE) if AS_OF_DATE else dt.date.today() - dt.timedelta(days=1)
DAYS_ELAPSED = AS_OF.weekday() + 1   # Monday=0 -> 1 ... Sunday=6 -> 7  (week, Monday start)
DAYS_IN_MONTH = AS_OF.day            # calendar days elapsed this month, incl. as-of date
DAYS_IN_YEAR = (AS_OF - dt.date(AS_OF.year, 1, 1)).days + 1  # calendar days elapsed this year
TOP_N = 10

def num(df, cols):
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    return df

# Store name normalisation (defined early so budget/LFL loaders can use it). Some stores
# appear under more than one record; alias the secondary onto the single live store name.
STORE_ALIASES = {
    'FN DOHA FESTIVAL CITY 1': 'FN Doha Festival City',
}
def norm_store(loc):
    if not isinstance(loc,str): return loc
    return STORE_ALIASES.get(loc.upper().strip(), loc)

# ---------------- barcode -> Color Code (FN's "key") ----------------
# Forever New rolls up at COLOR CODE level (style-colour), the analogue of SM's NEW Key.
key = pd.read_excel(U+'FN_Color_Code_Master.xlsx', dtype=str); key.columns=[c.strip() for c in key.columns]
key['Item Barcode']=key['Item Barcode'].str.strip()
b2k = key.dropna(subset=['Color Code']).drop_duplicates('Item Barcode').set_index('Item Barcode')['Color Code'].to_dict()

# Color Code -> clean display name. FN master has Item Description + Item Color; build
# "Description · Colour" (size-free), falling back to inventory Item Description downstream.
def clean_name(sn, col):
    sn = (sn or '').strip(); col=(col or '').strip()
    if sn and col: return f'{sn} · {col}'
    return sn or col or ''
knames = key.dropna(subset=['Color Code']).copy()
_desc = knames['Item Description'] if 'Item Description' in knames.columns else ['']*len(knames)
_col  = knames['Item Color'] if 'Item Color' in knames.columns else ['']*len(knames)
knames['disp'] = [clean_name(a,b) for a,b in zip(_desc, _col)]
key2name = knames[knames['disp']!=''].drop_duplicates('Color Code').set_index('Color Code')['disp'].to_dict()
# Color Code -> Category / Sub category from the master. These become the displayed
# group (Category) and dept (Sub category) on the dashboard, replacing the coarser
# inventory Item Group / Item Department for LABELLING only. Merchandise-scope EXCLUSION
# still uses the inventory Item Department (NON MERCHANDISE / SHOPPING BAGS) untouched.
_kc = key.dropna(subset=['Color Code']).drop_duplicates('Color Code').set_index('Color Code')
cc2cat = _kc['Category'].to_dict() if 'Category' in key.columns else {}
cc2sub = _kc['Sub category'].to_dict() if 'Sub category' in key.columns else {}
def cat_for(code, fallback_group=None):
    v = cc2cat.get(code)
    return v if (isinstance(v,str) and v.strip()) else (fallback_group or 'Uncategorized')
def sub_for(code, fallback_dept=None):
    v = cc2sub.get(code)
    return v if (isinstance(v,str) and v.strip()) else (fallback_dept or 'Uncategorized')

# Barcode -> FP/MD tag from the master. This authoritative tag (per the merchant) drives the
# FP Sales metric: FP Sales % = FP-tagged sales amount / total sales amount, and the units
# figure shown alongside = FP-tagged units / total units. Tag is consistent per color code.
_fpmd_col = next((c for c in key.columns if c.strip().upper().replace(' ','') in ('FP/MD','FPMD')), None)
bc2fpmd = {}
if _fpmd_col:
    _kf = key.dropna(subset=['Item Barcode']).copy()
    _kf['_tag'] = _kf[_fpmd_col].astype(str).str.strip().str.upper()
    _kf = _kf[_kf['_tag'].isin(['FP','MD'])]
    bc2fpmd = _kf.drop_duplicates('Item Barcode').set_index('Item Barcode')['_tag'].to_dict()
    print(f'FP/MD tags loaded from master: {len(bc2fpmd)} barcodes')
cc2fpmd = {}
if _fpmd_col and 'Color Code' in key.columns:
    _cf = key.dropna(subset=['Color Code']).copy()
    _cf['_tag'] = _cf[_fpmd_col].astype(str).str.strip().str.upper()
    _cf = _cf[_cf['_tag'].isin(['FP','MD'])]
    cc2fpmd = _cf.drop_duplicates('Color Code').set_index('Color Code')['_tag'].to_dict()
    print(f'FP/MD tags by color code: {len(cc2fpmd)} codes')

# Color Code -> total number of distinct sizes that exist for it in the system (master).
# Drives size-availability = (distinct sizes in stock) / (total distinct sizes in system).
cc_total_sizes = {}
if 'Item Size' in key.columns and 'Color Code' in key.columns:
    _ks = key.dropna(subset=['Color Code','Item Size'])
    cc_total_sizes = _ks.groupby('Color Code')['Item Size'].nunique().to_dict()
    print(f'Size-system map built for {len(cc_total_sizes)} color codes')

# ---------------- Budget tab (store x date sales targets) ----------------
# Budget achievement = actual sales / budget target, summed over the selected period.
budget_by_loc_date = {}     # (normalised store name) -> {date: target}
try:
    bud = pd.read_excel(U+'FN_Color_Code_Master.xlsx', sheet_name='Budget')
    bud.columns=[c.strip() for c in bud.columns]
    bud['Date']=pd.to_datetime(bud['Date'],errors='coerce')
    bud['Sales Target']=pd.to_numeric(bud['Sales Target'],errors='coerce')
    _nm_col = 'Loc Name' if 'Loc Name' in bud.columns else ('Location' if 'Location' in bud.columns else bud.columns[1])
    bud['_loc']=bud[_nm_col].map(norm_store)   # align to merged/live store names
    for (loc,dte), grp in bud.dropna(subset=['Date']).groupby(['_loc', bud['Date'].dt.date]):
        budget_by_loc_date.setdefault(loc, {})[dte] = grp['Sales Target'].sum()
    print(f'Budget loaded: {len(budget_by_loc_date)} stores')
except Exception as ex:
    print('Budget tab not loaded:', ex)

# ---------------- LFL Dates tab (store opening dates) ----------------
# Like-for-like: a store is "comparable" for a period only if it was open for the ENTIRE
# corresponding period one year earlier (open on/before the LY window start). Used by the
# LFL toggle to restrict combined totals to comparable stores.
store_open = {}   # normalised store name -> opening date (date)
try:
    lfl = pd.read_excel(U+'FN_Color_Code_Master.xlsx', sheet_name='LFL Dates')
    lfl.columns=[c.strip() for c in lfl.columns]
    _sn = next((c for c in lfl.columns if 'store' in c.lower() and 'name' in c.lower()), lfl.columns[1])
    _od = next((c for c in lfl.columns if 'opening' in c.lower() or 'open' in c.lower()), None)
    lfl['_open']=pd.to_datetime(lfl[_od],errors='coerce')
    for _,r in lfl.dropna(subset=['_open']).iterrows():
        store_open[norm_store(str(r[_sn]).strip())] = r['_open'].date()
    print(f'LFL opening dates loaded: {len(store_open)} stores')
except Exception as ex:
    print('LFL Dates tab not loaded:', ex)

# ---------------- image lookup (FN: color code -> Image Link) ----------------
key2img = {}
try:
    im = pd.read_excel(U+'FN_Image_Master.xlsx', dtype=str)
    im.columns=[c.strip() for c in im.columns]
    _cc = next((c for c in im.columns if c.lower().replace(' ','')=='colorcode'), im.columns[0])
    _ln = next((c for c in im.columns if any(t in c.lower() for t in ['link','url','image','src'])), im.columns[-1])
    im[_cc]=im[_cc].astype(str).str.strip()
    key2img = im.dropna(subset=[_cc,_ln]).drop_duplicates(_cc).set_index(_cc)[_ln].to_dict()
except FileNotFoundError:
    print('FN_Image_Master.xlsx not found - images will be blank')

# ---- override with independently-hosted links, EXACT COLOR-CODE MATCH ONLY ----
import glob as _glob
existing_keys = set(key2img.keys())
_upd_applied = 0
_upd_files = _glob.glob('independent_links_cumulative.xlsx') + _glob.glob(U+'Link_Update*.xlsx')
for upath in _upd_files:
    ud = pd.read_excel(upath, dtype=str)
    idc = ud.columns[0]
    urlc = next((ud.columns[i] for i,c in enumerate(ud.columns)
                 if any(t in c.lower() for t in ['link','url','image','src'])), ud.columns[-1])
    ud[idc] = ud[idc].astype(str).str.strip()
    for _, rr in ud.dropna(subset=[idc, urlc]).iterrows():
        k = rr[idc]
        if k in existing_keys or k in key2name:
            key2img[k] = rr[urlc]; _upd_applied += 1
print(f'Independent-link overrides applied (exact color-code match): {_upd_applied}')

# ---------------- master inventory ----------------
import glob as _g
def _newest(*patterns):
    cands=[]
    for p in patterns: cands += _g.glob(U+p)
    if not cands: raise FileNotFoundError(patterns)
    return max(cands, key=os.path.getmtime)
MASTER_FILE = _newest('Inventory*.xlsx','001__Barcodewise_Sales_and_Stock-*.xlsx')
DATEWISE_FILE = _newest('Yest_Sales*.xlsx','01__Barcodewise_Sales_-_Datewise*.xlsx','Sales_*.xlsx')
print('Using master :', os.path.basename(MASTER_FILE))
print('Using datewise:', os.path.basename(DATEWISE_FILE))
import gc
# Read only the columns that are actually present, so a trimmed ERP extract still works.
# Required for core logic; optional ones are derived or defaulted below if absent.
_REQUIRED = ['Country','Location','Item Group','Item Department','Item Class',
             'Item Barcode','Item Description','Season',
             'Net Sales Amt (WTD)','Net Sales Qty (WTD)',
             'Net Sales Amt (MTD)','Net Sales Qty (MTD)',
             'Net Sales Amt (YTD)','Net Sales Qty (YTD)',
             'Inventory Qty','Inventory Value','In Transit Qty']
_OPTIONAL = ['Region','Unit Cost','Last recieved date store','Item Size','Item Style Code',
             'Item Subclass',
             'Cost Amt (WTD)','Cost Amt (MTD)','Cost Amt (YTD)',
             'Ageing Days','Unit Price','Original Price']
_avail = set(pd.read_excel(MASTER_FILE, nrows=0).columns)
_missing_req = [c for c in _REQUIRED if c not in _avail]
if _missing_req:
    raise SystemExit(f'Inventory file is missing REQUIRED columns: {_missing_req}')
_usecols = [c for c in (_REQUIRED + _OPTIONAL) if c in _avail]
inv = pd.read_excel(MASTER_FILE, dtype={'Item Barcode':str}, usecols=_usecols)
# Default any optional columns that weren't in the extract.
if 'Region' not in inv.columns:           inv['Region'] = 'All regions'
if 'Unit Cost' not in inv.columns:
    # derive an approximate unit cost from YTD cost/qty when the cost column is absent
    if 'Cost Amt (YTD)' in inv.columns:
        _q = pd.to_numeric(inv['Net Sales Qty (YTD)'],errors='coerce')
        inv['Unit Cost'] = pd.to_numeric(inv['Cost Amt (YTD)'],errors='coerce') / _q.where(_q>0)
    else:
        inv['Unit Cost'] = pd.NA
for _c in ['Cost Amt (WTD)','Cost Amt (MTD)','Cost Amt (YTD)']:
    if _c not in inv.columns: inv[_c] = pd.NA
inv['Item Barcode']=inv['Item Barcode'].str.strip()
inv['Key']=inv['Item Barcode'].map(b2k).fillna('BC-'+inv['Item Barcode'])
# Master-driven Category / Sub category (keyed by color code = Key), with the coarse
# inventory Item Group / Item Department as fallback. Used for stock-in-transit grouping
# so it matches the category taxonomy shown elsewhere on the dashboard.
inv['Cat'] = [cat_for(k, g) for k, g in zip(inv['Key'], inv['Item Group'])]
inv['Sub'] = [sub_for(k, d) for k, d in zip(inv['Key'], inv['Item Department'])]
# FP/MD tag per row from the authoritative master barcode map (for the inventory snapshot).
inv['FPMD'] = inv['Item Barcode'].map(bc2fpmd)
# Last-received date drives the "exclude last-30-day arrivals" rule on bottom sellers.
# If the date column is absent, fall back to Ageing Days (>30 days => not a new arrival).
if 'Last recieved date store' in inv.columns:
    inv['LastRecv']=pd.to_datetime(inv['Last recieved date store'],errors='coerce')
elif 'Ageing Days' in inv.columns:
    inv['LastRecv']=pd.Timestamp(AS_OF) - pd.to_timedelta(
        pd.to_numeric(inv['Ageing Days'],errors='coerce'), unit='D')
else:
    inv['LastRecv']=pd.NaT
# Physical stores only. Forever New stores are prefixed "FN ". Exclude online/marketplace
# (ECOMM / 6th Street) and Outlet ("OL"/"OUTLET") locations that aren't physical full-price stores.
def is_physical(loc):
    if not isinstance(loc,str): return False
    u=loc.upper().strip()
    if not u.startswith('FN '): return False
    if 'ECOMM' in u or '6TH STREET' in u or '6 STREET' in u: return False
    if u.startswith('FN OL') or 'OUTLET' in u or u.startswith('OL '): return False
    if 'WAREHOUSE' in u or 'DISTRIBUTION' in u or ' WH' in u or '-VWH' in u or 'FZCO' in u: return False
    if 'DEBENHAM' in u: return False   # FN concessions inside Debenhams (no standalone KPI/footfall)
    return True

inv['Location'] = inv['Location'].map(norm_store)
inv = inv[inv['Location'].map(is_physical)].copy()
# Scope to core merchandise. FN is apparel: exclude only NON MERCHANDISE and SHOPPING BAGS
# (hangers, garment/jewellery bags, packaging). Everything else (womens-wear depts,
# Accessories, Bags) is core.
EXCL_GROUPS = {'NON MERCHANDISE','NON-MERCHANDISE'}
EXCL_DEPTS  = {'NON MERCHANDISE','NON-MERCHANDISE','SHOPPING BAGS'}
inv = inv[~inv['Item Group'].str.upper().isin(EXCL_GROUPS)]
inv = inv[~inv['Item Department'].str.upper().isin(EXCL_DEPTS)].copy()
gc.collect()  # free the pre-filter frame's memory before heavy aggregation
inv = num(inv, ['Unit Cost','Net Sales Amt (WTD)','Net Sales Qty (WTD)','Cost Amt (WTD)',
                'Net Sales Amt (MTD)','Net Sales Qty (MTD)','Cost Amt (MTD)',
                'Net Sales Amt (YTD)','Net Sales Qty (YTD)','Cost Amt (YTD)',
                'Inventory Qty','Inventory Value','In Transit Qty'])
inv['StockCost'] = inv['Unit Cost'] * inv['Inventory Qty']

# ---------------- yesterday snapshot ----------------
yd = pd.read_excel(DATEWISE_FILE, dtype={'Item Barcode':str})
if 'Store Brand' in yd.columns:
    yd = yd[yd['Store Brand']!='Total'].copy()
yd['Item Barcode']=yd['Item Barcode'].str.strip()
yd['Location']=yd['Location'].map(norm_store)
yd = yd[yd['Location'].map(is_physical)].copy()
yd['Key']=yd['Item Barcode'].map(b2k).fillna('BC-'+yd['Item Barcode'])
yd = num(yd, ['Net Sales Amt','Net Sales Qty'])

# ---- Tag-based yesterday FP metrics, per store (from master FP/MD tag) ----
# Authoritative FP/MD comes from the master. For each store's yesterday sales:
#   FP Sales %  = FP-tagged sales amount / total sales amount   (by AMOUNT)
#   FP units %  = FP-tagged units / total units                (shown alongside)
# Computed from the datewise sales file (single day = yesterday). Other periods fall back
# to the KPI file's FP% (which has no unit count).
fp_yest = {}   # location -> {'amt_pct':0-1, 'unit_pct':0-1, 'fp_units':int, 'tot_units':int}
_yt = yd.copy()
_yt['_tag'] = _yt['Item Barcode'].map(bc2fpmd)            # FP / MD / None
_yt['_isfp'] = (_yt['_tag']=='FP')
_yt['_fp_amt']  = _yt['_isfp'] * _yt['Net Sales Amt']
_yt['_fp_qty']  = _yt['_isfp'] * _yt['Net Sales Qty']
_g = _yt.groupby('Location').agg(fp_amt=('_fp_amt','sum'), tot_amt=('Net Sales Amt','sum'),
                                 fp_qty=('_fp_qty','sum'), tot_qty=('Net Sales Qty','sum'))
for loc, r in _g.iterrows():
    _amt_pct = (r['fp_amt']/r['tot_amt']) if r['tot_amt'] else None
    _unit_pct = (r['fp_qty']/r['tot_qty']) if r['tot_qty'] else None
    # Returns can shrink total net amount to near-zero/negative, making the amount-based %
    # explode (e.g. 2699%). When the amount% is implausible (outside 0-1) or the denominator
    # is non-positive, fall back to the robust unit-based % for display.
    if _amt_pct is None or not (0 <= _amt_pct <= 1):
        _amt_pct = _unit_pct
    fp_yest[loc] = {
        'amt_pct':  _amt_pct,
        'unit_pct': _unit_pct,
        'fp_units': int(round(r['fp_qty'])), 'tot_units': int(round(r['tot_qty'])),
    }
print(f'Tag-based yesterday FP metrics computed for {len(fp_yest)} stores')

# ---- GP% per store per period: 1 - (cost/sales) ----
# Yesterday cost/sales come from the datewise sales file; WTD/MTD/YTD from the inventory
# file's period cost & sales columns. Stored as gp_store[loc][period] = gp fraction (0-1).
gp_store = {}
def _gp(cost, sales):
    return (1 - cost/sales) if (sales and sales!=0) else None
# yesterday from yd (sales file) - needs Cost Amt
if 'Cost Amt' in yd.columns:
    yd = num(yd, ['Cost Amt'])
    _yg = yd.groupby('Location').agg(c=('Cost Amt','sum'), s=('Net Sales Amt','sum'))
    for loc, r in _yg.iterrows():
        gp_store.setdefault(loc, {})['yesterday'] = _gp(r['c'], r['s'])
# WTD/MTD/YTD from inventory period columns
_invp = inv.groupby('Location').agg(
    cW=('Cost Amt (WTD)','sum'), sW=('Net Sales Amt (WTD)','sum'),
    cM=('Cost Amt (MTD)','sum'), sM=('Net Sales Amt (MTD)','sum'),
    cY=('Cost Amt (YTD)','sum'), sY=('Net Sales Amt (YTD)','sum'))
for loc, r in _invp.iterrows():
    d = gp_store.setdefault(loc, {})
    d['wtd']=_gp(r['cW'],r['sW']); d['mtd']=_gp(r['cM'],r['sM']); d['ytd']=_gp(r['cY'],r['sY'])
print(f'GP% computed for {len(gp_store)} stores')

yd_key = yd.groupby(['Location','Key']).agg(YestAmt=('Net Sales Amt','sum'),
                                            YestQty=('Net Sales Qty','sum')).reset_index()

# ---------------- excluded-category yesterday sellers (Top-list fallback) ----------------
# The dashboard scopes merchandise to core categories (footwear/handbags/accessories/bags),
# dropping HOME & UNISEX / IMPULSE / etc. before aggregation. But when a store's core items
# don't fill the "Yesterday" Top-10 with ACTUAL sellers, we want to fill the remaining slots
# with items that genuinely sold from any category (e.g. an Impulse sunglass) rather than
# padding with zero-sale core items. Here we capture those excluded-but-sold rows from the
# datewise file (which carries its own Item Group/Department). They are tagged xcat=True and
# appended to each store's item list; the client ranks core first and only surfaces these to
# fill empty actual-seller slots in the TOP list (bottom list and KPIs are unaffected).
_GRP_COL = next((c for c in yd.columns if c.strip().lower() in ('item group','group')), None)
_DEP_COL = next((c for c in yd.columns if c.strip().lower() in ('item department','department','dept')), None)
xcat_rows = pd.DataFrame()
if _GRP_COL and _DEP_COL:
    _gx = yd[_GRP_COL].astype(str).str.upper().str.strip()
    _dx = yd[_DEP_COL].astype(str).str.upper().str.strip()
    excluded_mask = _gx.isin(EXCL_GROUPS) | _dx.isin(EXCL_DEPTS)
    yx = yd[excluded_mask & (yd['Net Sales Qty'] > 0)].copy()
    if len(yx):
        _desc_col = next((c for c in yx.columns if c.strip().lower() in
                          ('item description','item style','description','item style code')), None)
        agg = {'YestAmt':('Net Sales Amt','sum'),'YestQty':('Net Sales Qty','sum'),
               'Group':(_GRP_COL,'first'),'Dept':(_DEP_COL,'first')}
        if _desc_col: agg['Desc']=(_desc_col,'first')
        xcat_rows = yx.groupby(['Location','Key']).agg(**agg).reset_index()
        if 'Desc' not in xcat_rows.columns: xcat_rows['Desc']=xcat_rows['Key']
        print(f"Excluded-category yesterday sellers captured (Top-list fallback): {len(xcat_rows)} rows")

# ---------------- store x Key aggregation ----------------
g = inv.groupby(['Country','Region','Location','Key']).agg(
        Desc=('Item Description','first'),
        Group=('Item Group','first'), Dept=('Item Department','first'), Cls=('Item Class','first'),
        Season=('Season','first'), LastRecv=('LastRecv','max'),
        WTDamt=('Net Sales Amt (WTD)','sum'), WTDqty=('Net Sales Qty (WTD)','sum'), WTDcost=('Cost Amt (WTD)','sum'),
        MTDamt=('Net Sales Amt (MTD)','sum'), MTDqty=('Net Sales Qty (MTD)','sum'), MTDcost=('Cost Amt (MTD)','sum'),
        YTDamt=('Net Sales Amt (YTD)','sum'), YTDqty=('Net Sales Qty (YTD)','sum'), YTDcost=('Cost Amt (YTD)','sum'),
        InvQty=('Inventory Qty','sum'), InvValue=('Inventory Value','sum'),
        StockCost=('StockCost','sum'), UnitCost=('Unit Cost','mean'),
    ).reset_index()
# Relabel group (Category) and dept (Sub category) from the FN_Color_Code_Master, keyed by
# Color Code (== Key). Inventory's Item Group/Department remain only as a fallback when a
# color code has no master Category/Sub. Exclusion was already applied on inventory above.
g['Group'] = [cat_for(k, fg) for k, fg in zip(g['Key'], g['Group'])]
g['Dept']  = [sub_for(k, fd) for k, fd in zip(g['Key'], g['Dept'])]
g = g.merge(yd_key, on=['Location','Key'], how='left')
g[['YestAmt','YestQty']] = g[['YestAmt','YestQty']].fillna(0)

# ---- per-period weeks-cover with cascade (selected period -> next -> next) ----
# weekly rate from a period: (qty / days_elapsed_in_period) * 7
# Guard: a period whose elapsed window is too short produces an unstable, inflated run-rate
# (e.g. on Monday the WTD window is 1 day, so (qty/1)*7 overstates the weekly rate ~7x and
# makes cover read far too low). When the current period hasn't accumulated enough days, fall
# through to the next-longer period's rate, which is more representative.
MIN_WK_DAYS = 4   # need >=4 days in the week before trusting the WTD rate
MIN_MO_DAYS = 7   # need >=7 days in the month before trusting the MTD rate
rate_wtd = np.where(g['WTDqty'] > 0, (g['WTDqty'] / DAYS_ELAPSED) * 7, np.nan)
rate_mtd = np.where(g['MTDqty'] > 0, (g['MTDqty'] / DAYS_IN_MONTH) * 7, np.nan)
rate_ytd = np.where(g['YTDqty'] > 0, (g['YTDqty'] / DAYS_IN_YEAR) * 7, np.nan)
# If too few days have elapsed in a period, treat its rate as unavailable so the cascade
# uses the longer, more stable window instead.
wtd_ok = DAYS_ELAPSED >= MIN_WK_DAYS
mtd_ok = DAYS_IN_MONTH >= MIN_MO_DAYS

def cover_from_rate(rate):
    return np.where((rate > 0) & np.isfinite(rate), g['InvQty'] / rate, np.nan)

# cascade order per selected period:
#   wtd/yesterday: WTD -> MTD -> YTD ; mtd: MTD -> YTD ; ytd: YTD
# but skip a period's rate when its window is too short to be reliable.
_wtd = rate_wtd if wtd_ok else np.full(len(g), np.nan)
_mtd = rate_mtd if mtd_ok else np.full(len(g), np.nan)
casc_week  = np.where(np.isfinite(_wtd), _wtd,
              np.where(np.isfinite(_mtd), _mtd, rate_ytd))
casc_month = np.where(np.isfinite(_mtd), _mtd, rate_ytd)
casc_year  = rate_ytd

g['WC_week']  = cover_from_rate(casc_week)   # yesterday + wtd views
g['WC_month'] = cover_from_rate(casc_month)  # mtd view
g['WC_year']  = cover_from_rate(casc_year)   # ytd view

PERIOD_WC = {'yesterday':'WC_week','wtd':'WC_week','mtd':'WC_month','ytd':'WC_year'}
g['Image'] = g['Key'].map(key2img)

PERIODS = {'yesterday':('YestAmt','YestQty'),'wtd':('WTDamt_NA','WTDqty'),
           'mtd':('MTDamt','MTDqty'),'ytd':('YTDamt','YTDqty')}
# WTD has no amt in master; approximate WTD amt via ASP not available -> use qty only for wtd ranking
g['WTDamt_NA'] = np.nan

def round2(x):
    try:
        if x is None or (isinstance(x,float) and (np.isnan(x) or np.isinf(x))): return None
        return round(float(x),2)
    except: return None

CURRENT_SEASON = 'SPRING 2026'
RECENT_DAYS = 30
recent_cutoff = AS_OF - dt.timedelta(days=RECENT_DAYS)

def gm_freshest(r):
    """Freshest available GM%: WTD -> MTD -> YTD, whichever bucket has a sale."""
    for amt,cost,qty in [('WTDamt','WTDcost','WTDqty'),('MTDamt','MTDcost','MTDqty'),('YTDamt','YTDcost','YTDqty')]:
        if r[qty] and r[qty]>0 and r[amt] and r[amt]>0:
            return (r[amt]-r[cost])/r[amt]*100
    return None

def _wcstatus(r,col):
    wc=round2(r[col])
    if wc is not None: return 'ok'
    if r['InvQty'] and r['InvQty']>0: return 'dead'
    return 'none'

def item_row(r):
    """Full attributes for one Key at one store, for client-side ranking/filtering."""
    gm = gm_freshest(r)
    _mt = cc2fpmd.get(r['Key'])
    fpmd = _mt if _mt in ('FP','MD') else (None if gm is None else ('FP' if gm>=75 else 'MD'))
    lr = r['LastRecv']
    recent = bool(pd.notna(lr) and lr.date()>recent_cutoff)
    name = key2name.get(r['Key']) or strip_size(r['Desc'], r['Key'])
    def asp(a,q): return round2(a/q) if q else None
    return {
        'key':r['Key'],'desc':name,'group':r['Group'],'dept':r['Dept'],'cls':r['Cls'],
        'season':r['Season'],'cur_season':bool(r['Season']==CURRENT_SEASON),
        'gm':round2(gm),'fpmd':fpmd,'recent':recent,
        'inv_qty':round2(r['InvQty']),'stock_cost':round2(r['StockCost']),
        'img':r['Image'] if pd.notna(r['Image']) else None,
        'p':{
            'yesterday':[round2(r['YestAmt']),round2(r['YestQty']),asp(r['YestAmt'],r['YestQty']),round2(r['WC_week']),_wcstatus(r,'WC_week')],
            'wtd':[round2(r['WTDamt']),round2(r['WTDqty']),asp(r['WTDamt'],r['WTDqty']),round2(r['WC_week']),_wcstatus(r,'WC_week')],
            'mtd':[round2(r['MTDamt']),round2(r['MTDqty']),asp(r['MTDamt'],r['MTDqty']),round2(r['WC_month']),_wcstatus(r,'WC_month')],
            'ytd':[round2(r['YTDamt']),round2(r['YTDqty']),asp(r['YTDamt'],r['YTDqty']),round2(r['WC_year']),_wcstatus(r,'WC_year')],
        }
    }

def item_list(sub):
    return [item_row(r) for _,r in sub.iterrows()]

def xcat_item_rows(loc=None, country=None):
    """Build minimal item dicts for excluded-category items that SOLD yesterday, tagged
    xcat=True so the client can use them only to fill empty actual-seller slots in the TOP
    list. Only yesterday sales are known for these (they were dropped before period agg), so
    their non-yesterday periods are empty. Filtered by store (loc) or country."""
    if xcat_rows.empty: return []
    df = xcat_rows
    if loc is not None:
        df = df[df['Location']==loc]
    elif country is not None:
        _locs = set(g[g['Country']==country]['Location'].unique())
        df = df[df['Location'].isin(_locs)]
        if len(df):
            df = df.groupby('Key').agg(YestAmt=('YestAmt','sum'),YestQty=('YestQty','sum'),
                                       Group=('Group','first'),Dept=('Dept','first'),
                                       Desc=('Desc','first')).reset_index()
    out=[]
    for _,r in df.iterrows():
        ya=round2(r['YestAmt']); yq=round2(r['YestQty'])
        asp=round2(r['YestAmt']/r['YestQty']) if r['YestQty'] else None
        name=key2name.get(r['Key']) or strip_size(str(r['Desc']), r['Key'])
        _grp = cat_for(r['Key'], str(r['Group']).title())
        _dpt = sub_for(r['Key'], str(r['Dept']).title())
        out.append({
            'key':r['Key'],'desc':name,'group':_grp,'dept':_dpt,
            'cls':None,'season':None,'cur_season':False,'gm':None,'fpmd':None,'recent':False,
            'inv_qty':None,'stock_cost':None,'img':key2img.get(r['Key']),'xcat':True,
            'p':{'yesterday':[ya,yq,asp,None,'none'],
                 'wtd':[None,None,None,None,'none'],
                 'mtd':[None,None,None,None,'none'],
                 'ytd':[None,None,None,None,'none']}
        })
    return out

def candidate_items(sub):
    """Trim to items that could appear in a top/bottom-10 under any filter combo.
    For each Group (the finest seller filter), keep the top 15 + bottom 15 by YTD sales,
    plus top/bottom by inventory cost for dead-stock bottom lists. Union across periods
    is approximated by YTD ranking (most inclusive). Guarantees correct top/bottom-10
    for any Season/Group/Dept/FP-MD combination because dept⊂group and season/fpmd only
    shrink the set."""
    keep_idx=set()
    work=sub.copy()
    work['_sales']=work[['YestAmt','WTDamt','MTDamt','YTDamt']].max(axis=1)
    # ALWAYS retain any item that sold in a SHORT period (yesterday / WTD). These are the
    # periods where concentrated single-period sales were getting trimmed out by the
    # cross-period max ranking, which made the "Yesterday" top-seller list drop real
    # sellers. Short-period seller sets are tiny (a day/week of distinct sellers per store),
    # so payload size stays small. MTD/YTD have many sellers and the per-group/dept top-N
    # ranking below already guarantees their top-10, so we do NOT bulk-retain those.
    for qcol in ['YestQty','WTDqty']:
        if qcol in work.columns:
            keep_idx.update(work.index[work[qcol].fillna(0)>0])
    for grp, gsub in work.groupby('Group'):
        # top sellers in group (by best period sales)
        keep_idx.update(gsub.sort_values('_sales',ascending=False).head(20).index)
        # bottom: lowest sellers with stock + highest-stock-cost zero sellers
        sold=gsub[gsub['YTDqty']>0]
        zero=gsub[gsub['YTDqty']<=0]
        keep_idx.update(sold.sort_values('_sales',ascending=True).head(20).index)
        keep_idx.update(zero.sort_values('StockCost',ascending=False).head(20).index)
        # also ensure dept-level coverage: top/bottom per dept
        for dept, dsub in gsub.groupby('Dept'):
            keep_idx.update(dsub.sort_values('_sales',ascending=False).head(12).index)
            keep_idx.update(dsub.sort_values('_sales',ascending=True).head(12).index)
    return item_list(sub.loc[sorted(keep_idx)])

import re
def strip_size(desc, k):
    """Fallback display when key has no reference name: remove a -<size>- segment from desc."""
    d = (desc or k or '').strip()
    # remove patterns like -38-, -40-, -38.5-, -45- (numeric size between dashes)
    d = re.sub(r'-\d+(\.\d+)?-', '-', d)
    return d

def seller_row(r, amt_col, qty_col, wc_col):
    amt = r.get(amt_col); amt = None if pd.isna(amt) else round2(amt)
    qty = round2(r[qty_col])
    asp = round2(r[amt_col]/r[qty_col]) if (amt_col in r and not pd.isna(r[amt_col]) and r[qty_col]) else None
    name = key2name.get(r['Key']) or strip_size(r['Desc'], r['Key'])
    wc = round2(r[wc_col])
    # status: 'ok' has a cover number; 'dead' = inventory but no sales anywhere; 'none' = no inventory
    if wc is not None: status='ok'
    elif r['InvQty'] and r['InvQty']>0: status='dead'   # stock but zero sales in all periods
    else: status='none'
    return {'key':r['Key'],'desc':name,'group':r['Group'],'dept':r['Dept'],'cls':r['Cls'],
            'amt':amt,'qty':qty,'asp':asp,'inv_qty':round2(r['InvQty']),
            'stock_cost':round2(r['StockCost']),'weeks_cover':wc,'wc_status':status,
            'img':r['Image'] if pd.notna(r['Image']) else None}

# ---------------- category mix helper ----------------
def cat_mix(df, level):
    rev = df.groupby(level)['MTDamt'].sum()
    qty = df.groupby(level)['MTDqty'].sum()
    scost = df.groupby(level)['StockCost'].sum()
    sqty = df.groupby(level)['InvQty'].sum()
    out=[]
    tR,tQ,tSC,tSQ = rev.sum(),qty.sum(),scost.sum(),sqty.sum()
    for k in sorted(set(df[level].dropna())):
        out.append({'name':k,
            'sales_mix_rev': round2(100*rev.get(k,0)/tR) if tR else 0,
            'stock_mix_cost': round2(100*scost.get(k,0)/tSC) if tSC else 0,
            'sales_mix_qty': round2(100*qty.get(k,0)/tQ) if tQ else 0,
            'stock_mix_qty': round2(100*sqty.get(k,0)/tSQ) if tSQ else 0,
            'rev':round2(rev.get(k,0)),'stock_cost':round2(scost.get(k,0))})
    return sorted(out, key=lambda x:-(x['sales_mix_rev'] or 0))

def cat_pivot(df):
    """Group -> Dept -> Class tree. Sales (rev/qty) are emitted PER PERIOD so the dashboard's
    period selector (Yesterday/WTD/MTD/YTD) drives the sales columns; stock (scost/sqty) is a
    single CURRENT snapshot and is intentionally period-independent.
    NOTE: WTD revenue IS real in FN's source, so rev['wtd'] is emitted (unlike SM). Frontend
    reads rev[period]/qty[period] and
    recomputes mix % within the selected period's grand total. Node ordering uses YTD revenue
    (populated for every node) so the tree's sort is stable across period switches."""
    def node_vals(sub):
        return {
            'rev':{'yesterday':round2(sub['YestAmt'].sum()),
                   'wtd':round2(sub['WTDamt'].sum()),
                   'mtd':round2(sub['MTDamt'].sum()),
                   'ytd':round2(sub['YTDamt'].sum())},
            'qty':{'yesterday':round2(sub['YestQty'].sum()),
                   'wtd':round2(sub['WTDqty'].sum()),
                   'mtd':round2(sub['MTDqty'].sum()),
                   'ytd':round2(sub['YTDqty'].sum())},
            'scost':round2(sub['StockCost'].sum()),'sqty':round2(sub['InvQty'].sum())}
    def _sk(n): return -(n['rev'].get('ytd') or 0)
    tree=[]
    for grp, gsub in df.groupby('Group'):
        gnode={'name':grp, **node_vals(gsub), 'children':[]}
        for dept, dsub in gsub.groupby('Dept'):
            dnode={'name':dept, **node_vals(dsub), 'children':[]}
            for cls, csub2 in dsub.groupby('Cls'):
                dnode['children'].append({'name':cls, **node_vals(csub2)})
            dnode['children'].sort(key=_sk)
            gnode['children'].append(dnode)
        gnode['children'].sort(key=_sk)
        tree.append(gnode)
    tree.sort(key=_sk)
    return tree

# ---------------- in-transit by category/sub category (from master) ----------------
def in_transit(df):
    it = df.groupby(['Cat','Sub'])['In Transit Qty'].sum().reset_index()
    it = it[it['In Transit Qty']>0].sort_values('In Transit Qty',ascending=False)
    return [{'group':r['Cat'],'dept':r['Sub'],'qty':round2(r['In Transit Qty'])}
            for _,r in it.iterrows()]

# ---------------- inventory snapshot (FP/MD mix, season mix, style counts, size avail) ----------------
# Season bucketing: named current/recent seasons kept; everything else -> "Older".
_SEASON_KEEP = [('SPRING 2026','Spring 2026'),('SUMMER 2026','Summer 2026'),
                ('AUTUMN 2025','Autumn 2025'),('WINTER 2025','Winter 2025')]
def _season_bucket(s):
    u=str(s).upper()
    for k,lab in _SEASON_KEEP:
        if k in u: return lab
    return 'Older'
_SEASON_ORDER = ['Spring 2026','Summer 2026','Autumn 2025','Winter 2025','Older']

# Size-set completeness threshold: a color code counts as a "full set" when it has at least
# this many DISTINCT in-stock sizes; fewer (1..N-1) is "broken". Tune here if the apparel
# size run changes. NOTE: one-size / very-short-run styles read as "broken" under an absolute
# threshold — see the size-set card notes.
SIZESET_FULL_MIN = 4
def inventory_snapshot(df):
    """Build the 4-part inventory snapshot for an inventory sub-frame (a store or a
    combined set). All sections use in-stock rows (Inventory Qty > 0). Both a units basis
    (Inventory Qty) and a value basis (Inventory Value) are emitted so the dashboard can
    toggle between them client-side."""
    sub = df[df['Inventory Qty'] > 0].copy()
    if sub.empty:
        return {'fpmd':[],'season':[],'style':[],'size':[],'sizeset':[],'total_cc':0,
                'total_units':0,'total_value':0}
    sub['_sb'] = sub['Season'].map(_season_bucket)
    qcol = pd.to_numeric(sub['Inventory Qty'],errors='coerce').fillna(0)
    vcol = pd.to_numeric(sub['Inventory Value'],errors='coerce').fillna(0)
    sub['_q']=qcol; sub['_v']=vcol

    # 1) FP/MD stock mix by category — units and value, FP vs MD
    fpmd=[]
    for cat, c in sub.groupby('Cat'):
        fp=c[c['FPMD']=='FP']; md=c[c['FPMD']=='MD']
        fpmd.append({'cat':cat,
                     'fp_q':round2(fp['_q'].sum()),'md_q':round2(md['_q'].sum()),
                     'fp_v':round2(fp['_v'].sum()),'md_v':round2(md['_v'].sum()),
                     'tot_q':round2(c['_q'].sum()),'tot_v':round2(c['_v'].sum())})
    fpmd.sort(key=lambda x:-x['tot_q'])

    # 2) Season mix — units and value per bucket (fixed order)
    season=[]
    sg=sub.groupby('_sb').agg(q=('_q','sum'),v=('_v','sum'))
    for s in _SEASON_ORDER:
        if s in sg.index:
            season.append({'s':s,'q':round2(sg.loc[s,'q']),'v':round2(sg.loc[s,'v'])})
        else:
            season.append({'s':s,'q':0,'v':0})

    # 3) Active style-code count by category (distinct color codes with stock)
    style=[]
    for cat, c in sub.groupby('Cat'):
        style.append({'cat':cat,'n':int(c['Key'].nunique())})
    style.sort(key=lambda x:-x['n'])

    # 4) Size availability by category + sub category.
    # Per color code: (distinct sizes in stock) / (total distinct sizes in system from master),
    # capped at 1.0. Rolled up as the equal-weighted mean across color codes (one vote per style).
    def _avail(frame):
        if 'Item Size' not in frame.columns: return None
        instock = frame.groupby('Key')['Item Size'].nunique()
        ratios=[]
        for cc in frame['Key'].unique():
            tot = cc_total_sizes.get(cc)
            if tot and tot>0:
                ratios.append(min(instock.get(cc,0)/tot, 1.0))
        return round2(100*sum(ratios)/len(ratios)) if ratios else None
    size=[]
    for cat, c in sub.groupby('Cat'):
        subs=[]
        for sname, cc in c.groupby('Sub'):
            av=_avail(cc)
            if av is not None:
                subs.append({'sub':sname,'av':av,'cc':int(cc['Key'].nunique())})
        subs.sort(key=lambda x:-x['cc'])
        size.append({'cat':cat,'av':_avail(c),'cc':int(c['Key'].nunique()),'subs':subs})
    size=[s for s in size if s['av'] is not None]
    size.sort(key=lambda x:-x['cc'])

    # 5) Size-set completeness by category + sub category, split FP vs MD.
    # Per color code: count DISTINCT in-stock sizes (sub is already Inventory Qty>0). A color
    # code is a "full set" when it has >= SIZESET_FULL_MIN distinct in-stock sizes, OR has all of
    # its system sizes in stock (so one-size / short-run styles aren't unfairly marked broken).
    # comp = % of in-stock color codes that are full sets (higher = better). FP/MD split uses the
    # master per-color-code tag (cc2fpmd); untagged color codes still count toward the overall.
    def _setcomp(frame):
        if 'Item Size' not in frame.columns or frame.empty:
            return {'comp':None,'total_cc':0,'full_cc':0,'fp_comp':None,'fp_cc':0,'md_comp':None,'md_cc':0}
        nsizes = frame.groupby('Key')['Item Size'].nunique()
        a_full=a_tot=fp_full=fp_tot=md_full=md_tot=0
        for cc, n in nsizes.items():
            full = 1 if (n >= SIZESET_FULL_MIN or (cc_total_sizes.get(cc) and n >= cc_total_sizes.get(cc))) else 0
            a_tot+=1; a_full+=full
            tag = cc2fpmd.get(cc)
            if tag=='FP': fp_tot+=1; fp_full+=full
            elif tag=='MD': md_tot+=1; md_full+=full
        _pct=lambda f,t: round2(100*f/t) if t else None
        return {'comp':_pct(a_full,a_tot),'total_cc':int(a_tot),'full_cc':int(a_full),
                'fp_comp':_pct(fp_full,fp_tot),'fp_cc':int(fp_tot),
                'md_comp':_pct(md_full,md_tot),'md_cc':int(md_tot)}
    sizeset=[]
    for cat, c in sub.groupby('Cat'):
        subs=[]
        for sname, cc in c.groupby('Sub'):
            row=_setcomp(cc)
            if row['total_cc']>0: subs.append({'sub':sname, **row})
        subs.sort(key=lambda x:-x['total_cc'])
        crow=_setcomp(c)
        if crow['total_cc']>0:
            sizeset.append({'cat':cat, **crow, 'subs':subs})
    sizeset.sort(key=lambda x:-x['total_cc'])

    # ---- overall totals (one row per table), respecting the same in-stock filter ----
    fp_all=sub[sub['FPMD']=='FP']; md_all=sub[sub['FPMD']=='MD']
    tot_fpmd={'fp_q':round2(fp_all['_q'].sum()),'md_q':round2(md_all['_q'].sum()),
              'fp_v':round2(fp_all['_v'].sum()),'md_v':round2(md_all['_v'].sum()),
              'tot_q':round2(sub['_q'].sum()),'tot_v':round2(sub['_v'].sum())}
    tot_season={'q':round2(sub['_q'].sum()),'v':round2(sub['_v'].sum())}
    tot_style=int(sub['Key'].nunique())
    tot_size=_avail(sub)   # overall equal-weighted size availability across every stocked style
    tot_sizeset=_setcomp(sub)  # overall size-set completeness (FP/MD split) across all stocked color codes

    return {'fpmd':fpmd,'season':season,'style':style,'size':size,'sizeset':sizeset,
            'totals':{'fpmd':tot_fpmd,'season':tot_season,'style':tot_style,'size':tot_size,'sizeset':tot_sizeset},
            'total_cc':int(sub['Key'].nunique()),
            'total_units':round2(sub['_q'].sum()),
            'total_value':round2(sub['_v'].sum())}

# ---------------- per-store summary ----------------
# KPI source (daily, dated) — footfall/conversion/qty/full-price/UPT with LY comparison
KPI_FILE = U+'04__Store_KPI__For_Live_Dashboard_-_Anchit_.xlsx'
kpi_store = {}
kpi_lfl_store = {}
try:
    kdf = pd.read_excel(KPI_FILE, header=0)
    kdf.columns=[c.strip() for c in kdf.columns]
    # Normalize FN-style header variants to the canonical names this block expects.
    _rename={}
    for c in list(kdf.columns):
        cl=c.lower().replace(' ','')
        if cl=='footfallconversion%': _rename[c]='Footfall Conversion %'
        elif cl=='footfallconversion': _rename[c]='Footfall Conversion %'
        elif cl in ('fullpricesales%','fpsales%'): _rename[c]='Full Price Sales %'
        elif cl=='footfall' or cl=='ff': _rename[c]='Footfall'
        elif cl=='location(group)': _rename[c]='Location'
    kdf = kdf.rename(columns=_rename)
    if 'Store Brand' in kdf.columns:
        kdf = kdf[kdf['Store Brand']!='Total'].copy()
    kdf['Date'] = pd.to_datetime(kdf['Date'])
    # Keep only physical stores in the KPI rollup too (FN KPI may include ecomm/outlet).
    if 'Location' in kdf.columns:
        kdf['Location'] = kdf['Location'].map(norm_store)
        kdf = kdf[kdf['Location'].map(is_physical)].copy()
    # Percent columns may arrive as 0-100 or 0-1; the math below expects fractions (0-1).
    # Use the MEDIAN to detect scale so a few bad outlier rows (e.g. a 2699% or -900% row)
    # don't wrongly trigger a divide-by-100 on the whole column.
    for c in ['Full Price Sales %','Footfall Conversion %']:
        if c in kdf.columns:
            kdf[c] = pd.to_numeric(kdf[c], errors='coerce')
            _med = kdf[c].dropna().median()
            if pd.notna(_med) and _med > 1.5:   # typical value looks like 0-100 -> to 0-1
                kdf[c] = kdf[c] / 100.0
    for c in ['Net Sales Amt','Net Sales Qty','Footfall','UPT','Cost Amt']:
        if c in kdf.columns:
            kdf[c] = pd.to_numeric(kdf[c], errors='coerce')
    # The KPI/footfall export commonly lags the sales/inventory pull by a day or more.
    # Anchor KPI windows to the LATEST date actually present in the KPI file (capped at
    # AS_OF so we never look into the future), so "yesterday" = most recent KPI day available
    # and wtd/mtd/ytd end on that same day. This self-corrects for any KPI export lag.
    _kpi_dates = kdf['Date'].dt.date.dropna()
    KPI_ASOF = min(AS_OF, _kpi_dates.max()) if not _kpi_dates.empty else AS_OF
    print(f'KPI as-of (latest KPI date used): {KPI_ASOF}  (sales as-of {AS_OF})')
    def win(period):
        if period=='yesterday': return KPI_ASOF, KPI_ASOF
        if period=='wtd': return KPI_ASOF - dt.timedelta(days=KPI_ASOF.weekday()), KPI_ASOF
        if period=='mtd': return KPI_ASOF.replace(day=1), KPI_ASOF
        return KPI_ASOF.replace(month=1, day=1), KPI_ASOF
    def sum_budget(locs, s, e):
        """Sum daily Sales Target between s and e (inclusive) for a store or list of stores."""
        if isinstance(locs, str): locs=[locs]
        tot=0.0; found=False
        for loc in locs:
            bd=budget_by_loc_date.get(loc)
            if not bd: continue
            for dte,val in bd.items():
                if s<=dte<=e and val==val:
                    tot+=val; found=True
        return tot if found else None
    def agg_window(sub, s, e):
        m = (sub['Date'].dt.date>=s) & (sub['Date'].dt.date<=e)
        w = sub[m]
        if w.empty: return None
        sales=w['Net Sales Amt'].sum(); qty=w['Net Sales Qty'].sum(); foot=w['Footfall'].sum()
        # transactions per day = footfall * conversion% ; sum for the window
        txn=(w['Footfall']*w['Footfall Conversion %']).sum()
        # ratio KPIs from TOTALS, not averages of daily ratios:
        convp = (txn/foot) if foot else None            # conversion% = total txns / total footfall
        upt   = (qty/txn) if txn else None              # UPT = total units / total transactions
        aov   = (sales/txn) if txn else None            # AOV = total sales / total transactions
        asp   = (sales/qty) if qty else None            # ASP = total sales / total units
        # FP% revenue-weighted from valid rows only. Corrupt KPI rows (e.g. 2699%, -900%)
        # are excluded; if no valid rows remain, fp is None and the ORP fallback applies
        # (yesterday) downstream.
        _fpvalid = w[(w['Full Price Sales %']>=0) & (w['Full Price Sales %']<=1)]
        _fpsales = _fpvalid['Net Sales Amt'].sum()
        fp = ((_fpvalid['Full Price Sales %']*_fpvalid['Net Sales Amt']).sum()/_fpsales
              if _fpsales else None)
        # GP% = 1 - cost/sales, from the KPI file's Cost Amt column. Because agg_window runs
        # for both the TY and LY windows, this yields GP% for last year automatically, enabling
        # the vs-LY comparison on the GP tile. Falls back to None if cost is absent.
        gp = None
        if 'Cost Amt' in w.columns:
            _cost = pd.to_numeric(w['Cost Amt'],errors='coerce').sum()
            gp = (1 - _cost/sales) if (sales and sales!=0) else None
        return {'sales':round2(sales),'qty':round2(qty),'footfall':round2(foot),
                'conv':round2(convp*100 if convp is not None else None),
                'fullprice':round2(fp*100 if fp is not None else None),
                'gp':round2(gp*100 if gp is not None else None),
                'upt':round2(upt),'aov':round2(aov),'asp':round2(asp)}
    for loc, sub in kdf.groupby('Location'):
        per={}
        for p in ['yesterday','wtd','mtd','ytd']:
            s,e=win(p); ls,le=s.replace(year=s.year-1), e.replace(year=e.year-1)
            ty=agg_window(sub,s,e); ly=agg_window(sub,ls,le)
            # YESTERDAY FP from the authoritative master FP/MD tag (computed from the sales
            # file): FP Sales % = FP-tagged amount / total amount; plus FP unit % and counts
            # shown alongside. This overrides the KPI file's FP% for yesterday. Other periods
            # keep the KPI file's FP% (no per-unit tag history available there).
            if p=='yesterday' and ty is not None:
                _f = fp_yest.get(loc)
                if _f and _f.get('amt_pct') is not None:
                    ty['fullprice']   = round2(_f['amt_pct']*100)    # by amount
                    ty['fp_unit_pct'] = round2(_f['unit_pct']*100)   # by units
                    ty['fp_units']    = _f['fp_units']
                    ty['tot_units']   = _f['tot_units']
                    ty['fp_source']   = 'tag'
            # GP% now comes from agg_window (KPI file Cost Amt), computed for BOTH ty and ly,
            # so the vs-LY comparison works. No inventory-based override needed.
            # Budget achievement: actual sales / sum of daily targets over the period window
            if ty is not None:
                _bt = sum_budget(loc, s, e)
                ty['budget'] = round2(_bt) if _bt else None
                ty['budget_pct'] = round2(ty['sales']/_bt*100) if (_bt and ty.get('sales') is not None) else None
            per[p]={'ty':ty,'ly':ly}
        kpi_store[loc]=per
        # Store-level like-for-like. A naive LY comparison is unfair for a store that opened
        # part-way through last year's window (TY spans the full period; LY only from the open
        # date). True LFL clips BOTH years to the window where the store actually traded in
        # last year too: from max(period start, opening anniversary-agnostic open date) .. period end.
        # i.e. LY window = [max(LYstart, open) .. LYend]; TY window = the SAME calendar span
        # shifted forward one year, so the two spans are equal length and directly comparable.
        per_lfl={}
        _open=store_open.get(loc)
        for p in ['yesterday','wtd','mtd','ytd']:
            s,e=win(p); ls,le=s.replace(year=s.year-1), e.replace(year=e.year-1)
            if _open is None:
                # no opening date on record -> behave like the standard comparison
                per_lfl[p]={'ty':per.get(p,{}).get('ty'),'ly':per.get(p,{}).get('ly'),'comparable':True}
                continue
            if _open > le:
                # store didn't exist at all during last year's window -> no LY comparison
                per_lfl[p]={'ty':per.get(p,{}).get('ty'),'ly':None,'comparable':False}
                continue
            # clip LY window to when the store was open; mirror the same span in TY
            ly_s = max(ls, _open)
            ly_e = le
            # equal-length TY span ending at the period end (shift the clipped LY span +1yr)
            ty_s = ly_s.replace(year=ly_s.year+1)
            ty_e = e
            ty_l = agg_window(sub, ty_s, ty_e)
            ly_l = agg_window(sub, ly_s, ly_e)
            per_lfl[p]={'ty':ty_l,'ly':ly_l,'comparable':True,
                        'lfl_window':{'ty':[str(ty_s),str(ty_e)],'ly':[str(ly_s),str(ly_e)]}}
        kpi_lfl_store[loc]=per_lfl
    print(f'KPI loaded for {len(kpi_store)} stores')

    def _gp_combined(locs, salescol, costcol):
        sub=inv[inv['Location'].isin(locs)]
        s=pd.to_numeric(sub[salescol],errors='coerce').sum(); c=pd.to_numeric(sub[costcol],errors='coerce').sum()
        return (1-c/s) if s else None
    def combine_kpis(locs, lfl=False):
        """Sum KPIs across store locations, per period, TY and LY.
        When lfl=True, restrict to like-for-like: a store counts if it traded during last
        year's window at all (opened on/before the LY window end). For each such store the
        TY and LY windows are clipped to the span where it traded in BOTH years, then summed
        across the comparable cohort — so partially-open stores still contribute their
        comparable portion rather than being dropped entirely."""
        out={}
        for p in ['yesterday','wtd','mtd','ytd']:
            s,e=win(p); ls,le=s.replace(year=s.year-1), e.replace(year=e.year-1)
            if not lfl:
                csub = kdf[kdf['Location'].isin(locs)]
                if csub.empty:
                    out[p]={'ty':None,'ly':None}; continue
                ty=agg_window(csub,s,e); ly=agg_window(csub,ls,le)
            else:
                # comparable cohort = stores open on/before the LY window END (traded last year)
                mem=[l for l in locs if (store_open.get(l) is not None and store_open[l] <= le)]
                if not mem:
                    out[p]={'ty':None,'ly':None,'lfl_stores':0}; continue
                # sum per-store, each clipped to its own comparable window
                def _sum_clipped(year_offset):
                    parts=[]
                    for l in mem:
                        op=store_open[l]
                        ly_s=max(ls,op); ly_e=le
                        if year_offset==0:           # last year window (clipped to open)
                            ws,we=ly_s,ly_e
                        else:                        # this year: same span shifted +1yr
                            ws,we=ly_s.replace(year=ly_s.year+1), e
                        sub_l=kdf[kdf['Location']==l]
                        a=agg_window(sub_l,ws,we)
                        if a is not None: parts.append(a)
                    return parts
                def _agg_parts(parts):
                    if not parts: return None
                    sales=sum(x['sales'] for x in parts); qty=sum(x['qty'] for x in parts)
                    foot=sum(x['footfall'] for x in parts)
                    # rebuild ratio KPIs from summed components where possible
                    conv=None; upt=None; aov=None
                    return {'sales':round2(sales),'qty':round2(qty),'footfall':round2(foot),
                            'conv':None,'fullprice':None,'gp':None,'upt':None,'aov':None,
                            'asp':round2((sales/qty) if qty else None)}
                ty=_agg_parts(_sum_clipped(1)); ly=_agg_parts(_sum_clipped(0))
                # recompute GP, conv, upt, aov for the clipped cohort from raw rows
                def _ratios(parts_year):
                    rows=[]
                    for l in mem:
                        op=store_open[l]; ly_s=max(ls,op)
                        if parts_year==1: ws,we=ly_s.replace(year=ly_s.year+1), e
                        else: ws,we=ly_s, le
                        sub_l=kdf[(kdf['Location']==l)&(kdf['Date'].dt.date>=ws)&(kdf['Date'].dt.date<=we)]
                        if len(sub_l): rows.append(sub_l)
                    if not rows: return
                    w=pd.concat(rows)
                    sales=w['Net Sales Amt'].sum(); qty=w['Net Sales Qty'].sum(); foot=w['Footfall'].sum()
                    txn=(w['Footfall']*w['Footfall Conversion %']).sum()
                    tgt = ty if parts_year==1 else ly
                    if tgt is None: return
                    tgt['conv']=round2((txn/foot)*100) if foot else None
                    tgt['upt']=round2(qty/txn) if txn else None
                    tgt['aov']=round2(sales/txn) if txn else None
                    if 'Cost Amt' in w.columns:
                        c=pd.to_numeric(w['Cost Amt'],errors='coerce').sum()
                        tgt['gp']=round2((1-c/sales)*100) if sales else None
                _ratios(1); _ratios(0)
            if p=='yesterday' and ty is not None and not lfl:
                _m = _yt[_yt['Location'].isin(locs)]
                if len(_m):
                    _fpa=_m['_fp_amt'].sum(); _ta=_m['Net Sales Amt'].sum()
                    _fpq=_m['_fp_qty'].sum(); _tq=_m['Net Sales Qty'].sum()
                    _apct=(_fpa/_ta) if _ta else None; _upct=(_fpq/_tq) if _tq else None
                    if _apct is None or not (0<=_apct<=1): _apct=_upct
                    if _apct is not None:
                        ty['fullprice']=round2(_apct*100); ty['fp_unit_pct']=round2(_upct*100 if _upct is not None else None)
                        ty['fp_units']=int(round(_fpq)); ty['tot_units']=int(round(_tq)); ty['fp_source']='tag'
            # GP% (both ty and ly) already set by agg_window from the KPI Cost Amt column.
            # Only the budget figures need to be added at the combined level.
            if ty is not None and not lfl:
                _bt=sum_budget(locs,s,e)
                ty['budget']=round2(_bt) if _bt else None
                ty['budget_pct']=round2(ty['sales']/_bt*100) if (_bt and ty.get('sales') is not None) else None
            blob_extra={'lfl_stores':len(mem)} if lfl else {}
            out[p]={'ty':ty,'ly':ly, **blob_extra}
        return out
except Exception as ex:
    print('KPI load skipped:', ex)
    def combine_kpis(locs, lfl=False): return None

# ---------------- top-10 in-transit ITEMS with images ----------------
inv['ImgKey']=inv['Key']
it_all = inv[inv['In Transit Qty']>0].copy()
def transit_items_df(sub):
    sub=sub[sub['In Transit Qty']>0]
    if sub.empty: return []
    g2=sub.groupby('Key').agg(qty=('In Transit Qty','sum'),
            desc=('Item Description','first'),grp=('Cat','first'),
            dept=('Sub','first')).reset_index()
    g2=g2.sort_values('qty',ascending=False).head(TOP_N)
    out=[]
    for _,r in g2.iterrows():
        out.append({'key':r['Key'],'desc':key2name.get(r['Key']) or strip_size(r['desc'],r['Key']),
                    'qty':round2(r['qty']),'group':r['grp'],'dept':r['dept'],
                    'img':key2img.get(r['Key'])})
    return out
def transit_items(loc):
    return transit_items_df(it_all[it_all['Location']==loc])

stores={}
for loc, sub in g.groupby('Location'):
    inv_sub = inv[inv['Location']==loc]
    country = sub['Country'].iloc[0]; region = sub['Region'].iloc[0]
    blob={'country':country,'region':region,
          'items':candidate_items(sub[(sub['InvQty']>0)|(sub['YTDqty']>0)|(sub['YestQty']>0)])
                  + xcat_item_rows(loc=loc),
          'cat_pivot':cat_pivot(sub),
          'in_transit':in_transit(inv_sub),
          'transit_items':transit_items(loc),
          'inv_snapshot':inventory_snapshot(inv_sub),
          'kpi':kpi_store.get(loc),
          'kpi_lfl':kpi_lfl_store.get(loc)}
    stores[loc]=blob

# ---------------- COUNTRY-COMBINED ("All Stores") blobs ----------------
# Re-aggregate across all physical stores in each country.
country_blobs={}
for country, csub in g.groupby('Country'):
    inv_c = inv[inv['Country']==country]
    region_label = 'All regions'
    blob={'country':country,'region':region_label,'is_combined':True,
          'cat_pivot':cat_pivot(csub),
          'in_transit':in_transit(inv_c),
          'transit_items':transit_items_df(inv_c),
          'inv_snapshot':inventory_snapshot(inv_c),
          'kpi':None}
    # country-wide: aggregate the same Key across all stores in the country
    cg = csub.groupby('Key').agg(
        Desc=('Desc','first'),Group=('Group','first'),Dept=('Dept','first'),Cls=('Cls','first'),
        Season=('Season','first'), LastRecv=('LastRecv','max'),
        YestAmt=('YestAmt','sum'),YestQty=('YestQty','sum'),
        WTDamt=('WTDamt','sum'),WTDqty=('WTDqty','sum'),WTDcost=('WTDcost','sum'),
        MTDamt=('MTDamt','sum'),MTDqty=('MTDqty','sum'),MTDcost=('MTDcost','sum'),
        YTDamt=('YTDamt','sum'),YTDqty=('YTDqty','sum'),YTDcost=('YTDcost','sum'),
        InvQty=('InvQty','sum'),StockCost=('StockCost','sum'),Image=('Image','first'),
    ).reset_index()
    rwk=np.where(cg['WTDqty']>0,(cg['WTDqty']/DAYS_ELAPSED)*7,np.nan)
    rmo=np.where(cg['MTDqty']>0,(cg['MTDqty']/DAYS_IN_MONTH)*7,np.nan)
    ryr=np.where(cg['YTDqty']>0,(cg['YTDqty']/DAYS_IN_YEAR)*7,np.nan)
    # short-window guard (same as per-store): ignore an unreliable rate from a period that
    # hasn't accumulated enough days, falling through to the next-longer window.
    _rwk = rwk if wtd_ok else np.full(len(cg), np.nan)
    _rmo = rmo if mtd_ok else np.full(len(cg), np.nan)
    cg['WC_week']=np.where(np.isfinite(_rwk),cg['InvQty']/_rwk,np.where(np.isfinite(_rmo),cg['InvQty']/_rmo,np.where(np.isfinite(ryr),cg['InvQty']/ryr,np.nan)))
    cg['WC_month']=np.where(np.isfinite(_rmo),cg['InvQty']/_rmo,np.where(np.isfinite(ryr),cg['InvQty']/ryr,np.nan))
    cg['WC_year']=np.where(np.isfinite(ryr),cg['InvQty']/ryr,np.nan)
    blob['items']=candidate_items(cg[(cg['InvQty']>0)|(cg['YTDqty']>0)|(cg['YestQty']>0)]) \
                  + xcat_item_rows(country=country)
    if kpi_store:
        clocs=[l for l in csub['Location'].unique() if l in kpi_store]
        blob['kpi']=combine_kpis(clocs)
        blob['kpi_lfl']=combine_kpis(clocs, lfl=True)   # like-for-like (comparable stores only)
    country_blobs[country]=blob

# ---------------- ALL COUNTRIES (consolidated GCC) blob ----------------
# Grand total across every physical store, for the default "All Countries" view.
_alllocs = sorted(g['Location'].unique().tolist())
_allinv = inv
all_blob = {'country':'All Countries','region':'All regions','is_combined':True,'is_allcountries':True,
            'cat_pivot':cat_pivot(g),
            'in_transit':in_transit(_allinv),
            'transit_items':transit_items_df(_allinv),
            'inv_snapshot':inventory_snapshot(_allinv),
            'kpi':None}
acg = g.groupby('Key').agg(
    Desc=('Desc','first'),Group=('Group','first'),Dept=('Dept','first'),Cls=('Cls','first'),
    Season=('Season','first'), LastRecv=('LastRecv','max'),
    YestAmt=('YestAmt','sum'),YestQty=('YestQty','sum'),
    WTDamt=('WTDamt','sum'),WTDqty=('WTDqty','sum'),WTDcost=('WTDcost','sum'),
    MTDamt=('MTDamt','sum'),MTDqty=('MTDqty','sum'),MTDcost=('MTDcost','sum'),
    YTDamt=('YTDamt','sum'),YTDqty=('YTDqty','sum'),YTDcost=('YTDcost','sum'),
    InvQty=('InvQty','sum'),StockCost=('StockCost','sum'),Image=('Image','first'),
).reset_index()
rwk=np.where(acg['WTDqty']>0,(acg['WTDqty']/DAYS_ELAPSED)*7,np.nan)
rmo=np.where(acg['MTDqty']>0,(acg['MTDqty']/DAYS_IN_MONTH)*7,np.nan)
ryr=np.where(acg['YTDqty']>0,(acg['YTDqty']/DAYS_IN_YEAR)*7,np.nan)
# short-window guard (same as per-store / per-country)
_rwk = rwk if wtd_ok else np.full(len(acg), np.nan)
_rmo = rmo if mtd_ok else np.full(len(acg), np.nan)
acg['WC_week']=np.where(np.isfinite(_rwk),acg['InvQty']/_rwk,np.where(np.isfinite(_rmo),acg['InvQty']/_rmo,np.where(np.isfinite(ryr),acg['InvQty']/ryr,np.nan)))
acg['WC_month']=np.where(np.isfinite(_rmo),acg['InvQty']/_rmo,np.where(np.isfinite(ryr),acg['InvQty']/ryr,np.nan))
acg['WC_year']=np.where(np.isfinite(ryr),acg['InvQty']/ryr,np.nan)
all_blob['items']=candidate_items(acg[(acg['InvQty']>0)|(acg['YTDqty']>0)|(acg['YestQty']>0)])
if kpi_store:
    alllocs=[l for l in _alllocs if l in kpi_store]
    all_blob['kpi']=combine_kpis(alllocs)
    all_blob['kpi_lfl']=combine_kpis(alllocs, lfl=True)
country_blobs['All Countries']=all_blob

# ---------------- country revenue ranking (MTD) ----------------
crev = inv.groupby('Country')['Net Sales Amt (MTD)'].sum().sort_values(ascending=False)
tot = crev.sum()
country_rank=[]
for i,(c,v) in enumerate(crev.items(),1):
    country_rank.append({'country':c,'rev':round2(v),'rank':i,'pct':round2(100*v/tot) if tot else 0})

# ---------------- store revenue ranking WITHIN each country, per period ----------------
# revenue per store per period. WTD has no revenue in source -> use qty for wtd ranking.
store_rev = inv.groupby(['Country','Location']).agg(
    yesterday=('Location','size')  # placeholder, replaced below
).reset_index()[['Country','Location']]

# yesterday revenue per store (from datewise file)
yd_store = yd.groupby('Location')['Net Sales Amt'].sum()
# wtd: qty only
wtd_store = inv.groupby('Location')['Net Sales Qty (WTD)'].sum()
mtd_store = inv.groupby('Location')['Net Sales Amt (MTD)'].sum()
ytd_store = inv.groupby('Location')['Net Sales Amt (YTD)'].sum()
loc_country = inv.groupby('Location')['Country'].first()

def build_store_rank(series, is_qty=False):
    """Return {country: [ {store,val,rank,pct}... ranked desc ]}."""
    df = pd.DataFrame({'val':series}).reset_index().rename(columns={series.index.name or 'index':'Location'})
    df.columns=['Location','val']
    df['Country']=df['Location'].map(loc_country)
    df['val']=df['val'].fillna(0)
    out={}
    for c, sub in df.groupby('Country'):
        sub=sub.sort_values('val',ascending=False).reset_index(drop=True)
        tot=sub['val'].sum()
        rows=[]
        for i,r in sub.iterrows():
            rows.append({'store':r['Location'],'val':round2(r['val']),'rank':i+1,
                         'pct':round2(100*r['val']/tot) if tot else 0})
        out[c]=rows
    # All-Countries roll-up: every physical store ranked across the whole GCC, so the
    # default "All Countries" view has a populated store-ranking table.
    allsub=df.sort_values('val',ascending=False).reset_index(drop=True)
    tot=allsub['val'].sum()
    rows=[]
    for i,r in allsub.iterrows():
        rows.append({'store':r['Location'],'val':round2(r['val']),'rank':i+1,
                     'pct':round2(100*r['val']/tot) if tot else 0})
    out['All Countries']=rows
    return out

store_rank={
    'yesterday':build_store_rank(yd_store),
    'wtd':build_store_rank(wtd_store, is_qty=True),
    'mtd':build_store_rank(mtd_store),
    'ytd':build_store_rank(ytd_store),
}

# store -> country lookup for the infographic
store_country = g.groupby('Location')['Country'].first().to_dict()

# ---------------- filter trees ----------------
geo = g[['Country','Region','Location']].drop_duplicates().sort_values(['Country','Region','Location'])
filters={'countries':sorted(geo['Country'].unique().tolist()),
         'regions':sorted(geo['Region'].unique().tolist()),
         'tree':{}}
for c,sc in geo.groupby('Country'):
    filters['tree'][c]={}
    for r,sr in sc.groupby('Region'):
        filters['tree'][c][r]=sorted(sr['Location'].unique().tolist())

# ---------------- weekly trend (last 8 ISO weeks) — Weekly Sales + Multi-Week KPI ----------------
# Mirrors SM. Uses the dated KPI file (kdf) + agg_window; only runs if KPI data loaded.
# Per-week series, read by the charts as weekly['all' | 'country'[cn] | 'store'[loc]].
# Wrapped in try/except so a KPI hiccup hides the charts instead of breaking the refresh.
WEEKLY_N = 8
weekly = {'weeks':[], 'all':{}, 'country':{}, 'store':{}}
try:
    if kpi_store:
        _METRICS = ['conv','upt','footfall','aov','asp']
        _end_week_monday = KPI_ASOF - dt.timedelta(days=KPI_ASOF.weekday())
        _weeks=[]
        for i in range(WEEKLY_N-1, -1, -1):
            wmon = _end_week_monday - dt.timedelta(weeks=i)
            wsun = wmon + dt.timedelta(days=6)
            iso = wmon.isocalendar()
            _weeks.append({'iso':f'{iso[0]}-W{iso[1]:02d}','label':f'Wk {iso[1]}',
                           'start':wmon.isoformat(),'end':wsun.isoformat(),
                           '_mon':wmon,'_sun':wsun})
        weekly['weeks']=[{k:w[k] for k in ('iso','label','start','end')} for w in _weeks]
        def _series_for(sub):
            out={'sales_ty':[], 'sales_ly':[], 'sales_bud':[]}
            for m in _METRICS: out[m]=[]
            for w in _weeks:
                s,e=w['_mon'],w['_sun']
                ls,le=s.replace(year=s.year-1), e.replace(year=e.year-1)
                ty=agg_window(sub,s,e); ly=agg_window(sub,ls,le)
                out['sales_ty'].append(round2(ty['sales']) if ty else None)
                out['sales_ly'].append(round2(ly['sales']) if ly else None)
                for m in _METRICS:
                    out[m].append((ty.get(m) if ty else None))
            return out
        def _bud_series(locs):
            arr=[]
            for w in _weeks:
                bs=sum_budget(locs, w['_mon'], w['_sun'])     # FN: single-budget 3-arg signature
                arr.append(round2(bs) if bs else None)
            return arr
        _all_locs=list(kdf['Location'].dropna().unique())
        _a=_series_for(kdf); _a['sales_bud']=_bud_series(_all_locs)
        weekly['all']=_a
        for _cn in sorted(set(store_country.values())):
            _locs=[l for l in _all_locs if store_country.get(l)==_cn]
            if not _locs: continue
            _csub=kdf[kdf['Location'].isin(_locs)]
            _s=_series_for(_csub); _s['sales_bud']=_bud_series(_locs)
            weekly['country'][_cn]=_s
        for _loc in _all_locs:
            _ssub=kdf[kdf['Location']==_loc]
            _s=_series_for(_ssub); _s['sales_bud']=_bud_series([_loc])
            weekly['store'][_loc]=_s
    else:
        print('weekly trend skipped: no KPI data')
except Exception as _wex:
    print('weekly trend build failed (charts will hide):', _wex)
    weekly = {'weeks':[], 'all':{}, 'country':{}, 'store':{}}
# ---------------- country-level performance (per period) ----------------
# Mirrors the SM country_perf block. Margin TY/LY are DERIVED (sales*gp/100) via _abs_margin,
# not read from a budget-margin tab, so FN needs only sales+gp+footfall from its KPI window
# (all present in agg_window) plus its single-budget fields. FN differences vs SM:
#   * budget fields are 'budget' / 'budget_pct' (single budget), not 'bud_rebudget_sales'.
#   * no margin-budget in FN, and the card never renders one, so no margin_bud key is emitted.
def _abs_margin(d):
    if not d: return None
    s=d.get('sales'); gp=d.get('gp')
    if s is None or gp is None: return None
    return round2(s*gp/100.0)
country_perf={}
for _p in ['yesterday','wtd','mtd','ytd']:
    rows=[]
    for _cn, _blob in country_blobs.items():
        if _cn=='All Countries': continue
        _k=(_blob.get('kpi') or {}).get(_p) or {}
        _ty=_k.get('ty') or {}; _ly=_k.get('ly') or {}
        if not _ty and not _ly: continue
        rows.append({
            'country':_cn,
            'sales_ty':_ty.get('sales'),
            'sales_ly':_ly.get('sales'),
            'sales_bud':_ty.get('budget'),
            'sales_bud_pct':_ty.get('budget_pct'),
            'margin_ty':_abs_margin(_ty),
            'margin_ly':_abs_margin(_ly),
            'footfall_ty':_ty.get('footfall'),
            'footfall_ly':_ly.get('footfall'),
        })
    rows.sort(key=lambda r:-(r['sales_ty'] or 0))
    country_perf[_p]=rows
summary={'meta':{'as_of':AS_OF.isoformat(),'days_elapsed_week':DAYS_ELAPSED,
                 'days_elapsed_month':DAYS_IN_MONTH,'days_elapsed_year':DAYS_IN_YEAR,
                 'generated':dt.datetime.now().isoformat(timespec='seconds'),
                 'periods':['yesterday','wtd','mtd','ytd'],
                 'note_wtd':'WTD revenue is week-to-date; store rank still ranks WTD by units.'},
         'filters':filters,'country_rank':country_rank,'store_rank':store_rank,
         'store_country':store_country,
         'country_blobs':country_blobs,
         'country_perf':country_perf,
         'weekly':weekly,
         'stores':stores}

json.dump(summary, open(OUT,'w'), separators=(',',':'))
sz=os.path.getsize(OUT)/1024
print(f'Wrote {OUT}  ({sz:.0f} KB)  | stores={len(stores)} | as_of={AS_OF} days_elapsed={DAYS_ELAPSED}')
print('Country rank:', [(c["country"],c["rank"],c["pct"]) for c in country_rank])
