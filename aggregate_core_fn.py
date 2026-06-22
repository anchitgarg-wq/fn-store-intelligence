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
# Color Code -> Category / Sub category (used for merchandise naming if needed)
cc2cat = key.dropna(subset=['Color Code']).drop_duplicates('Color Code').set_index('Color Code')['Category'].to_dict() if 'Category' in key.columns else {}

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
_OPTIONAL = ['Region','Unit Cost','Last recieved date store',
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

# Some stores appear under more than one record (e.g. a relocation or a duplicate POS entry).
# Alias the secondary record onto the single live store name so inventory, sales AND KPI all
# roll up together. 'FN Doha Festival City 1' is a secondary record for 'FN Doha Festival City'
# (the live store); its KPI rows fill the gaps on the live store.
STORE_ALIASES = {
    'FN DOHA FESTIVAL CITY 1': 'FN Doha Festival City',
}
def norm_store(loc):
    if not isinstance(loc,str): return loc
    return STORE_ALIASES.get(loc.upper().strip(), loc)
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

# ---- ORP-based yesterday FP% (units), per store: fallback for bad KPI FP% ----
# The KPI file's Full Price Sales % occasionally has corrupt rows (e.g. 2699%, -900%).
# As a fallback we derive FP% from the sales file itself: a sold unit is "full price" when
# its actual unit price (Net Sales Amt / Qty) is within 5% of its Original Retail Price
# (i.e. discount < 5%). FP% = full-price units / total units, per store. Yesterday only,
# since the datewise sales file covers a single day.
orp_fp_yest = {}   # location -> FP fraction (0-1) for yesterday, by units
_ORP_COL = next((c for c in yd.columns if c.strip().lower() in
                 ('original retail price','orp','original price','original retail')), None)
if _ORP_COL:
    _o = yd.copy()
    _o['_orp'] = pd.to_numeric(_o[_ORP_COL], errors='coerce')
    _o = _o[(_o['Net Sales Qty']>0) & (_o['_orp']>0)]
    _o['_unit'] = _o['Net Sales Amt'] / _o['Net Sales Qty']
    _o['_disc'] = 1.0 - (_o['_unit'] / _o['_orp'])
    _o['_fpunits'] = (_o['_disc'] < 0.05) * _o['Net Sales Qty']   # full-price units (disc < 5%)
    grp = _o.groupby('Location').agg(fpu=('_fpunits','sum'), tot=('Net Sales Qty','sum'))
    orp_fp_yest = {loc: (r['fpu']/r['tot']) for loc, r in grp.iterrows() if r['tot']>0}
    print(f'ORP-based yesterday FP% computed for {len(orp_fp_yest)} stores (fallback ready)')

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
g = g.merge(yd_key, on=['Location','Key'], how='left')
g[['YestAmt','YestQty']] = g[['YestAmt','YestQty']].fillna(0)

# ---- per-period weeks-cover with cascade (selected period -> next -> next) ----
# weekly rate from a period: (qty / days_elapsed_in_period) * 7
rate_wtd = np.where(g['WTDqty'] > 0, (g['WTDqty'] / DAYS_ELAPSED) * 7, np.nan)
rate_mtd = np.where(g['MTDqty'] > 0, (g['MTDqty'] / DAYS_IN_MONTH) * 7, np.nan)
rate_ytd = np.where(g['YTDqty'] > 0, (g['YTDqty'] / DAYS_IN_YEAR) * 7, np.nan)

def cover_from_rate(rate):
    return np.where((rate > 0) & np.isfinite(rate), g['InvQty'] / rate, np.nan)

# cascade order per selected period:
#   wtd/yesterday: WTD -> MTD -> YTD ; mtd: MTD -> YTD ; ytd: YTD
casc_week  = np.where(np.isfinite(rate_wtd), rate_wtd,
              np.where(np.isfinite(rate_mtd), rate_mtd, rate_ytd))
casc_month = np.where(np.isfinite(rate_mtd), rate_mtd, rate_ytd)
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
    fpmd = None if gm is None else ('FP' if gm>=75 else 'MD')
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
        out.append({
            'key':r['Key'],'desc':name,'group':str(r['Group']).title(),'dept':str(r['Dept']).title(),
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
    """Group -> Dept -> Class tree with raw rev/qty/stock_cost/inv_qty per node.
    Frontend computes parent-relative and grand-total % and applies the Value/Qty toggle."""
    def node_vals(sub):
        return {'rev':round2(sub['MTDamt'].sum()),'qty':round2(sub['MTDqty'].sum()),
                'scost':round2(sub['StockCost'].sum()),'sqty':round2(sub['InvQty'].sum())}
    tree=[]
    for grp, gsub in df.groupby('Group'):
        gnode={'name':grp, **node_vals(gsub), 'children':[]}
        for dept, dsub in gsub.groupby('Dept'):
            dnode={'name':dept, **node_vals(dsub), 'children':[]}
            for cls, csub2 in dsub.groupby('Cls'):
                dnode['children'].append({'name':cls, **node_vals(csub2)})
            dnode['children'].sort(key=lambda x:-(x['rev'] or 0))
            gnode['children'].append(dnode)
        gnode['children'].sort(key=lambda x:-(x['rev'] or 0))
        tree.append(gnode)
    tree.sort(key=lambda x:-(x['rev'] or 0))
    return tree

# ---------------- in-transit by group/dept ----------------
def in_transit(df):
    it = df.groupby(['Item Group','Item Department'])['In Transit Qty'].sum().reset_index()
    it = it[it['In Transit Qty']>0].sort_values('In Transit Qty',ascending=False)
    return [{'group':r['Item Group'],'dept':r['Item Department'],'qty':round2(r['In Transit Qty'])}
            for _,r in it.iterrows()]

# ---------------- per-store summary ----------------
# KPI source (daily, dated) — footfall/conversion/qty/full-price/UPT with LY comparison
KPI_FILE = U+'04__Store_KPI__For_Live_Dashboard_-_Anchit_.xlsx'
kpi_store = {}
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
    for c in ['Net Sales Amt','Net Sales Qty','Footfall','UPT']:
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
        # FP% revenue-weighted from valid rows only. Corrupt KPI rows (e.g. 2699%, -900%)
        # are excluded; if no valid rows remain, fp is None and the ORP fallback applies
        # (yesterday) downstream.
        _fpvalid = w[(w['Full Price Sales %']>=0) & (w['Full Price Sales %']<=1)]
        _fpsales = _fpvalid['Net Sales Amt'].sum()
        fp = ((_fpvalid['Full Price Sales %']*_fpvalid['Net Sales Amt']).sum()/_fpsales
              if _fpsales else None)
        return {'sales':round2(sales),'qty':round2(qty),'footfall':round2(foot),
                'conv':round2(convp*100 if convp is not None else None),
                'fullprice':round2(fp*100 if fp is not None else None),
                'upt':round2(upt),'aov':round2(aov)}
    for loc, sub in kdf.groupby('Location'):
        per={}
        for p in ['yesterday','wtd','mtd','ytd']:
            s,e=win(p); ls,le=s.replace(year=s.year-1), e.replace(year=e.year-1)
            ty=agg_window(sub,s,e); ly=agg_window(sub,ls,le)
            # Fallback: if the KPI file gave no valid FP% for YESTERDAY, use the ORP-derived
            # FP% (by units) computed from the sales file. Only yesterday can be recomputed
            # (the datewise sales file is single-day); other periods keep None if invalid.
            if p=='yesterday' and ty is not None and ty.get('fullprice') is None:
                _orp = orp_fp_yest.get(loc)
                if _orp is not None:
                    ty['fullprice'] = round2(_orp*100)
                    ty['fp_source'] = 'orp'
            per[p]={'ty':ty,'ly':ly}
        kpi_store[loc]=per
    print(f'KPI loaded for {len(kpi_store)} stores')

    def combine_kpis(locs):
        """Sum KPIs across a list of store locations, per period, TY and LY."""
        csub = kdf[kdf['Location'].isin(locs)]
        if csub.empty: return None
        out={}
        for p in ['yesterday','wtd','mtd','ytd']:
            s,e=win(p); ls,le=s.replace(year=s.year-1), e.replace(year=e.year-1)
            ty=agg_window(csub,s,e); ly=agg_window(csub,ls,le)
            # Combined ORP FP% fallback for yesterday: aggregate full-price units and total
            # units across the member stores (units-weighted), not an average of percents.
            if p=='yesterday' and ty is not None and ty.get('fullprice') is None and _ORP_COL:
                _m = _o[_o['Location'].isin(locs)] if _ORP_COL else None
                if _m is not None and len(_m):
                    _fpu=_m['_fpunits'].sum(); _tot=_m['Net Sales Qty'].sum()
                    if _tot>0:
                        ty['fullprice']=round2(_fpu/_tot*100); ty['fp_source']='orp'
            out[p]={'ty':ty,'ly':ly}
        return out
except Exception as ex:
    print('KPI load skipped:', ex)
    def combine_kpis(locs): return None

# ---------------- top-10 in-transit ITEMS with images ----------------
inv['ImgKey']=inv['Key']
it_all = inv[inv['In Transit Qty']>0].copy()
def transit_items_df(sub):
    sub=sub[sub['In Transit Qty']>0]
    if sub.empty: return []
    g2=sub.groupby('Key').agg(qty=('In Transit Qty','sum'),
            desc=('Item Description','first'),grp=('Item Group','first'),
            dept=('Item Department','first')).reset_index()
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
          'kpi':kpi_store.get(loc)}
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
    cg['WC_week']=np.where(np.isfinite(rwk),cg['InvQty']/rwk,np.where(np.isfinite(rmo),cg['InvQty']/rmo,np.where(np.isfinite(ryr),cg['InvQty']/ryr,np.nan)))
    cg['WC_month']=np.where(np.isfinite(rmo),cg['InvQty']/rmo,np.where(np.isfinite(ryr),cg['InvQty']/ryr,np.nan))
    cg['WC_year']=np.where(np.isfinite(ryr),cg['InvQty']/ryr,np.nan)
    blob['items']=candidate_items(cg[(cg['InvQty']>0)|(cg['YTDqty']>0)|(cg['YestQty']>0)]) \
                  + xcat_item_rows(country=country)
    if kpi_store:
        clocs=[l for l in csub['Location'].unique() if l in kpi_store]
        blob['kpi']=combine_kpis(clocs)
    country_blobs[country]=blob

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

summary={'meta':{'as_of':AS_OF.isoformat(),'days_elapsed_week':DAYS_ELAPSED,
                 'days_elapsed_month':DAYS_IN_MONTH,'days_elapsed_year':DAYS_IN_YEAR,
                 'generated':dt.datetime.now().isoformat(timespec='seconds'),
                 'periods':['yesterday','wtd','mtd','ytd'],
                 'note_wtd':'WTD ranks by qty (no WTD revenue in source).'},
         'filters':filters,'country_rank':country_rank,'store_rank':store_rank,
         'store_country':store_country,
         'country_blobs':country_blobs,
         'stores':stores}

json.dump(summary, open(OUT,'w'), separators=(',',':'))
sz=os.path.getsize(OUT)/1024
print(f'Wrote {OUT}  ({sz:.0f} KB)  | stores={len(stores)} | as_of={AS_OF} days_elapsed={DAYS_ELAPSED}')
print('Country rank:', [(c["country"],c["rank"],c["pct"]) for c in country_rank])
