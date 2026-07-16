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
# NOTE: FN_Color_Code_Master.xlsx (2026 format) has TWO header rows: row 1 is a merged
# group label ('OG PRICE'/'CP'/'TAG' repeated over each country), row 2 has the real
# column names ('Item Barcode', 'Color Code', ... 'UAE', 'KUWAIT', ...). header=1 skips
# the group-label row so pandas reads the real names. Without this, pandas reads the
# group-label row as headers and every column lookup below fails with a KeyError.
key = pd.read_excel(U+'FN_Color_Code_Master.xlsx', dtype=str, header=1); key.columns=[c.strip() for c in key.columns]
key['Item Barcode']=key['Item Barcode'].str.strip()
b2k = key.dropna(subset=['Color Code']).drop_duplicates('Item Barcode').set_index('Item Barcode')['Color Code'].to_dict()

# UAE OG price (AED) per barcode, for markdown/discount tracking. With header=1 the duplicate
# country columns land as OG PRICE (base name e.g. 'UAE'), CP ('UAE.1'), TAG ('UAE.2'); the
# base 'UAE' column is the OG PRICE. Both this and the sales feed are in AED, so they compare
# directly. UAE price is used as the single reference for all countries (per stakeholder).
og_uae = {}
if 'UAE' in key.columns:
    _oguae = pd.to_numeric(key['UAE'], errors='coerce')
    og_uae = {bc: v for bc, v in zip(key['Item Barcode'], _oguae) if pd.notna(v)}
print('UAE OG price loaded for %d barcodes' % len(og_uae))

# ---- WH/DC locations from the StoreDc Master tab (Location Type == 'WH') ----
# Used for warehouse-stock visibility. Matched to inventory Locations by a whitespace-
# collapsed, upper-cased key so minor formatting differences don't break the join.
def _canon(x): return ' '.join(str(x).split()).upper()
wh_locs = set()
try:
    _sd = pd.read_excel(U+'FN_Color_Code_Master.xlsx', sheet_name='StoreDc Master')
    _sd.columns=[str(c).strip() for c in _sd.columns]
    _nmc = next((c for c in _sd.columns if c.strip().lower() in ('store name','location','name')), _sd.columns[0])
    _tyc = next((c for c in _sd.columns if c.strip().lower()=='location type'), None)
    if _tyc is not None:
        for _n,_t in zip(_sd[_nmc], _sd[_tyc]):
            if pd.notna(_n) and str(_t).strip().upper()=='WH':
                wh_locs.add(_canon(_n))
    print('WH/DC locations from StoreDc Master: %d' % len(wh_locs))
except Exception as ex:
    print('StoreDc Master tab not read (WH stock disabled):', ex)

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

# Barcode -> FP/MD tag from the master, PER COUNTRY (2026 format). Each barcode now carries
# a separate tag for UAE / KUWAIT / SAUDI ARABIA / BAHRAIN / QATAR (an item can be MD in one
# country and FP in another). Basis of calculation is the barcode itself; rollups by color
# code, category, or store are aggregations over these barcode-level tags — never inferred.
#
# View resolution (confirmed with stakeholder):
#   - A specific store, or a specific country's combined view -> use that country's OWN
#     tag column (the row's real country; unambiguous).
#   - The "All Countries / All Stores" combined view -> use the UAE tag column as the
#     agreed representative default (mixed-country stock has no single true tag).
#
# Master rows are excluded from every FP/MD lookup when they have no barcode, or no
# Category/Sub category (non-merchandise placeholder rows — confirmed with stakeholder).
# A tag cell of '#N/A' or blank is treated as "no tag" for that barcode/country, identical
# to a barcode absent from the master entirely.
TAG_COUNTRIES = ['UAE','KUWAIT','SAUDI ARABIA','BAHRAIN','QATAR']
ALL_COUNTRIES_DEFAULT_TAGCOL = 'UAE'
# Real Country values (as found in the inventory/sales files) -> the master's tag-column
# header. Add variants here if a refresh shows an unmapped country in the log warning below.
COUNTRY_TO_TAGCOL = {
    'UNITED ARAB EMIRATES': 'UAE', 'UAE': 'UAE',
    'KUWAIT': 'KUWAIT',
    'SAUDI ARABIA': 'SAUDI ARABIA', 'KSA': 'SAUDI ARABIA',
    'BAHRAIN': 'BAHRAIN',
    'QATAR': 'QATAR',
}
def tagcol_for_country(country):
    return COUNTRY_TO_TAGCOL.get(str(country).strip().upper())

def fpmd_for(lookup_dict, key_val, country, all_countries=False):
    """Resolve one FP/MD tag from a {key: {tagcol: 'FP'/'MD'}} dict. all_countries=True
    forces the UAE-default (the All-Countries combined view); otherwise resolves against
    the row's own real country. Returns None if untagged or the country doesn't map."""
    tags = lookup_dict.get(key_val)
    if not tags:
        return None
    if all_countries:
        return tags.get(ALL_COUNTRIES_DEFAULT_TAGCOL)
    col = tagcol_for_country(country)
    return tags.get(col) if col else None

bc2fpmd_cty = {}   # barcode -> {tagcol: 'FP'/'MD'}
cc2fpmd_cty = {}   # color code -> {tagcol: 'FP'/'MD'}  (first-occurrence per code; tag is
                   # documented as consistent per color code across its size barcodes)
_valid_fp = key.dropna(subset=['Item Barcode','Category','Sub category']).copy()
_valid_fp = _valid_fp[(_valid_fp['Category'].str.strip()!='') & (_valid_fp['Sub category'].str.strip()!='')]
_valid_fp = _valid_fp.drop_duplicates('Item Barcode')
# The header repeats UAE/KUWAIT/... three times (OG PRICE, CP, TAG groups); pandas
# disambiguates duplicate names as UAE, UAE.1, UAE.2 in column order. The TAG group is
# always the LAST occurrence of each country name.
_tag_col_map = {}
for _cty in TAG_COUNTRIES:
    _matches = [c for c in _valid_fp.columns if c.split('.')[0].strip().upper() == _cty]
    if _matches:
        _tag_col_map[_cty] = _matches[-1]
if len(_tag_col_map) == len(TAG_COUNTRIES):
    # Defensive check: confirm each detected TAG column actually holds FP/MD/#N/A values
    # (not prices) before trusting it — catches a master whose column layout shifted.
    _tagcols_ok = True
    for _cty, _col in _tag_col_map.items():
        _seen = set(_valid_fp[_col].dropna().astype(str).str.strip().str.upper().unique())
        _bad = _seen - {'FP','MD','#N/A'}
        if _bad:
            print(f'FP/MD tag column for {_cty} ({_col}) has unexpected values {sorted(_bad)[:5]} '
                  f'- master column layout may have shifted; FP/MD will be empty')
            _tagcols_ok = False
    if _tagcols_ok:
        for _cty, _col in _tag_col_map.items():
            _valid_fp[f'_tag_{_cty}'] = _valid_fp[_col].astype(str).str.strip().str.upper()
        _tagcolnames = [f'_tag_{c}' for c in TAG_COUNTRIES]
        for _bc, _rowvals in zip(_valid_fp['Item Barcode'], _valid_fp[_tagcolnames].values):
            _tags = {cty: t for cty, t in zip(TAG_COUNTRIES, _rowvals) if t in ('FP','MD')}
            if _tags:
                bc2fpmd_cty[_bc.strip()] = _tags
        print(f'FP/MD per-country tags loaded from master: {len(bc2fpmd_cty)} barcodes '
              f'x {len(_tag_col_map)} countries')
        if 'Color Code' in _valid_fp.columns:
            _ccvalid = _valid_fp.dropna(subset=['Color Code'])
            for _cc, _rowvals in zip(_ccvalid['Color Code'], _ccvalid[_tagcolnames].values):
                if _cc in cc2fpmd_cty:
                    continue
                _tags = {cty: t for cty, t in zip(TAG_COUNTRIES, _rowvals) if t in ('FP','MD')}
                if _tags:
                    cc2fpmd_cty[_cc] = _tags
            print(f'FP/MD per-country tags by color code: {len(cc2fpmd_cty)} codes')
else:
    print(f'FP/MD per-country tag columns not fully found (found {sorted(_tag_col_map)}); '
          f'expected {TAG_COUNTRIES} - FP/MD will be empty')
# Sanity check: warn if any real country actually present in this master maps to nothing,
# so a mismatch surfaces in the refresh log instead of silently producing blank FP/MD.
_unmapped_note = ('If FN inventory/sales Country values differ from '
                   f'{sorted(set(COUNTRY_TO_TAGCOL))}, add the variant to COUNTRY_TO_TAGCOL.')
print(_unmapped_note)

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

# ---------------- KPI Targets tab (store x date daily operational targets) ----------------
# Daily per-store targets for ASP, Sales Qty, Conversion Rate, Footfall, Invoices
# (transactions), UPT, ATV (=AOV), and optionally GP% / FP Sales% (may be blank/absent
# until populated). Sales Amount's own target keeps coming from the Budget tab above,
# unchanged — this sheet covers the OTHER KPI tiles.
# Additive components (qty, footfall, invoices, and a derived per-day "target revenue" =
# ATV Targ x Target Invoice) are banked per day; ratio targets (ASP/CR/UPT/AOV/GP/FP) for
# any period are RE-DERIVED from the summed components, never averaged day-by-day — same
# "totals, not averages of daily ratios" principle agg_window() already uses for actuals.
kpi_target_daily = {}   # normalised store name -> {date: {qty,foot,inv,rev,gp,fp}}
try:
    kt = pd.read_excel(U+'FN_Color_Code_Master.xlsx', sheet_name='KPI Targets')
    kt.columns=[c.strip() for c in kt.columns]
    kt['Date']=pd.to_datetime(kt['Date'],errors='coerce')
    _loc_col = 'Location' if 'Location' in kt.columns else kt.columns[2]
    kt['_loc']=kt[_loc_col].map(norm_store)
    for c in ['Target Sales Qty','CR targ','Target Footfall','Target Invoice','UPT Targ','ATV tar','ASP Targ']:
        if c in kt.columns: kt[c]=pd.to_numeric(kt[c],errors='coerce')
    # GP% / FP Sales% are optional — either column may be entirely absent (not yet added
    # to the sheet) or present but fully blank (added as a placeholder, not yet populated).
    # Auto-detect 0-1 vs 0-100 scale the same way the KPI file's percent columns are read.
    def _pct_col(colnames):
        for cn in colnames:
            if cn in kt.columns:
                v = pd.to_numeric(kt[cn], errors='coerce')
                _med = v.dropna().median()
                if pd.notna(_med) and _med > 1.5: v = v/100.0
                return v
        return pd.Series([None]*len(kt))
    kt['_gp']  = _pct_col(['GP%','GP %'])
    kt['_fp']  = _pct_col(['FP Sales%','FP Sales %','FP%','FP %'])
    kt['_rev'] = kt['ATV tar'] * kt['Target Invoice']   # derived per-day target revenue
    def _num(v):
        return float(v) if pd.notna(v) else 0.0
    for _, r in kt.dropna(subset=['Date','_loc']).iterrows():
        d = kpi_target_daily.setdefault(r['_loc'], {})
        dte = r['Date'].date()
        d[dte] = {
            'qty':  _num(r.get('Target Sales Qty')),
            'foot': _num(r.get('Target Footfall')),
            'inv':  _num(r.get('Target Invoice')),
            'rev':  _num(r.get('_rev')),
            'gp':   (float(r['_gp']) if pd.notna(r.get('_gp')) else None),
            'fp':   (float(r['_fp']) if pd.notna(r.get('_fp')) else None),
        }
    _has_gp = kt['_gp'].notna().any() if '_gp' in kt.columns else False
    _has_fp = kt['_fp'].notna().any() if '_fp' in kt.columns else False
    print(f'KPI Targets loaded: {len(kpi_target_daily)} stores | GP% populated: {bool(_has_gp)} | FP Sales% populated: {bool(_has_fp)}')
except Exception as ex:
    print('KPI Targets tab not loaded:', ex)

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

# ---------------- Shipment tracker ('Shipment Tracker' tab in FN_Color_Code_Master) -------------
# Inbound shipments with an ETA at Jebel Ali, bucketed into forward ISO weeks (Monday start,
# matching the weekly-trend panel) for the next SHIP_HORIZON weeks.
#
# DESIGN NOTES:
#  * HEADER ROW IS DETECTED, NOT ASSUMED. FN's tab puts the header on row 1; SM's has a title
#    row above it. The header is found by scanning for the row containing 'ETA', so the same
#    code reads both without a per-brand fork.
#  * COLUMNS ARE MATCHED BY NAME, NOT POSITION. FN's order is SHIP NO / CRTNS / QTY / ETA;
#    SM's is Remarks / SHIP NO / ETA / CRTNS / QTY. Name-matching absorbs the difference, and
#    tolerates the stray punctuation in the real headers ('SHIP NO:', 'ETA @ JABAL Ali').
#  * A SHIPMENT IS A DISTINCT 'SHIP NO:', not a row -- counting rows would overstate the number
#    of shipments if a ship number ever spans multiple lines.
#  * NO LOCATION KEY. The tracker cannot be attributed to a store or country, so it is a GLOBAL
#    figure and the dashboard renders it only on the All-Countries / All-Stores view.
#  * DIFFERENT SUPPLY-CHAIN STAGE FROM THE ERP's 'In Transit Qty'. This is vessels inbound to
#    PORT (not landed, not in the WH, not allocated). In Transit Qty is stock already moving
#    between locations. They must never be presented as the same measure or compared.
#  * OVERDUE AND NO-ETA GET THEIR OWN ROWS -- never silently dropped; they are the ones that matter.
SHIP_HORIZON = 10   # forward weeks shown
shipments = None
try:
    _sh = None
    for _sn2 in ('Shipment Tracker', 'shipment_tracker', 'Shipment_Tracker', 'shipment tracker'):
        try:
            _sh = pd.read_excel(U+'FN_Color_Code_Master.xlsx', sheet_name=_sn2, header=None); break
        except Exception:
            _sh = None
    if _sh is None or _sh.empty:
        print('Shipment tracker: tab not found (card will hide).')
    else:
        _hr = None
        for _i in range(min(10, len(_sh))):
            _vals = [str(v).strip().upper() for v in _sh.iloc[_i].tolist()]
            if any('ETA' in v for v in _vals):
                _hr = _i; break
        if _hr is None:
            raise ValueError("no header row containing 'ETA' found in Shipment Tracker")
        _sh.columns = [str(c).strip() for c in _sh.iloc[_hr]]
        _sh = _sh.iloc[_hr + 1:].reset_index(drop=True)
        def _shcol(*tokens):
            for c in _sh.columns:
                cl = str(c).strip().lower()
                if all(t in cl for t in tokens):
                    return c
            return None
        _c_ship = _shcol('ship')
        _c_eta  = _shcol('eta')
        _c_qty  = _shcol('qty')
        _c_crt  = _shcol('crtn') or _shcol('carton')
        _c_sta  = _shcol('status')
        if not (_c_ship and _c_eta and _c_qty):
            raise ValueError('Shipment Tracker missing Ship No / ETA / QTY columns; found: %s' % list(_sh.columns))
        _sh = _sh.rename(columns={_c_ship: 'ship', _c_eta: 'eta', _c_qty: 'qty'})
        _sh['crtns']  = pd.to_numeric(_sh[_c_crt], errors='coerce') if _c_crt else 0
        _sh['status'] = _sh[_c_sta].astype(str).str.strip() if _c_sta else ''
        _sh['ship']   = _sh['ship'].astype(str).str.strip()
        _sh = _sh[(_sh['ship'] != '') & (_sh['ship'].str.lower() != 'nan')]
        _sh['qty']   = pd.to_numeric(_sh['qty'], errors='coerce').fillna(0)
        _sh['crtns'] = pd.to_numeric(_sh['crtns'], errors='coerce').fillna(0)
        # ETA is written DD/MM/YYYY. Excel may hand it over as a real datetime or as text;
        # handle both, and parse text dayfirst.
        _eta_num = pd.to_numeric(_sh['eta'], errors='coerce')
        _eta_serial = pd.to_datetime(_eta_num.where((_eta_num >= 1) & (_eta_num <= 60000)),
                                     unit='D', origin='1899-12-30', errors='coerce')
        _eta_real = pd.to_datetime(_sh['eta'], errors='coerce', dayfirst=True)
        _sh['_eta'] = _eta_serial.fillna(_eta_real)

        def _shagg(sub):
            return {'n': int(sub['ship'].nunique()),
                    'qty': int(round(float(sub['qty'].sum()))),
                    'crtns': int(round(float(sub['crtns'].sum())))}

        _mon = AS_OF - dt.timedelta(days=AS_OF.weekday())   # Monday of the current week
        _swk = []
        for _i in range(SHIP_HORIZON):
            _ws = _mon + dt.timedelta(weeks=_i)
            _we = _ws + dt.timedelta(days=6)
            _m = _sh['_eta'].notna() & (_sh['_eta'].dt.date >= _ws) & (_sh['_eta'].dt.date <= _we)
            _iso = _ws.isocalendar()
            _swk.append({'iso': '%d-W%02d' % (_iso[0], _iso[1]), 'label': 'Wk %d' % _iso[1],
                         'start': _ws.isoformat(), 'end': _we.isoformat(),
                         'range': '%s \u2013 %s' % (_ws.strftime('%d %b'), _we.strftime('%d %b')),
                         'current': bool(_i == 0), **_shagg(_sh[_m])})
        _hz_end = _mon + dt.timedelta(weeks=SHIP_HORIZON) - dt.timedelta(days=1)
        shipments = {
            'weeks':   _swk,
            'overdue': _shagg(_sh[_sh['_eta'].notna() & (_sh['_eta'].dt.date < _mon)]),
            'noeta':   _shagg(_sh[_sh['_eta'].isna()]),
            'beyond':  _shagg(_sh[_sh['_eta'].notna() & (_sh['_eta'].dt.date > _hz_end)]),
            'total':   _shagg(_sh),
            'horizon': SHIP_HORIZON,
            'week_start': _mon.isoformat(),
            'scope': 'global',
        }
        print('Shipments: %d ship nos | %s units | horizon %dw from %s | overdue=%d no-ETA=%d beyond=%d'
              % (shipments['total']['n'], f"{shipments['total']['qty']:,}", SHIP_HORIZON, _mon,
                 shipments['overdue']['n'], shipments['noeta']['n'], shipments['beyond']['n']))
except Exception as _shex:
    import traceback as _shtb
    print('Shipment tracker SKIPPED (payload still ships):', _shex)
    print(_shtb.format_exc())
    shipments = None

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
# FP/MD is NOT tagged globally here anymore — inventory_snapshot() resolves it per call
# (real country for a store/country view, UAE-default for the All-Countries view),
# since the same inv rows are reused across all three kinds of call.
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
# Capture WH/DC rows BEFORE the physical-store filter removes them (merchandise filter applied below).
_whinv = inv[inv['Location'].map(lambda l: _canon(l) in wh_locs)].copy()
inv = inv[inv['Location'].map(is_physical)].copy()
# Scope to core merchandise. FN is apparel: exclude only NON MERCHANDISE and SHOPPING BAGS
# (hangers, garment/jewellery bags, packaging). Everything else (womens-wear depts,
# Accessories, Bags) is core.
EXCL_GROUPS = {'NON MERCHANDISE','NON-MERCHANDISE'}
EXCL_DEPTS  = {'NON MERCHANDISE','NON-MERCHANDISE','SHOPPING BAGS'}
inv = inv[~inv['Item Group'].str.upper().isin(EXCL_GROUPS)]
inv = inv[~inv['Item Department'].str.upper().isin(EXCL_DEPTS)].copy()
# WH stock = merchandise only (same exclusion), aggregated by country and by (country, color code).
if len(_whinv):
    _whinv = _whinv[~_whinv['Item Group'].astype(str).str.upper().isin(EXCL_GROUPS)]
    _whinv = _whinv[~_whinv['Item Department'].astype(str).str.upper().isin(EXCL_DEPTS)].copy()
    _whinv['_wq'] = pd.to_numeric(_whinv['Inventory Qty'], errors='coerce').fillna(0)
    wh_country_qty = _whinv.groupby('Country')['_wq'].sum().to_dict()
    wh_cc_qty = _whinv.groupby(['Country','Key'])['_wq'].sum().to_dict()   # (country, colorcode) -> qty
    wh_total_qty = float(_whinv['_wq'].sum())
    print('WH stock (merchandise): total=%d | countries=%s' % (int(wh_total_qty), sorted(wh_country_qty)))
else:
    wh_country_qty = {}; wh_cc_qty = {}; wh_total_qty = 0.0
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
yd['_og'] = pd.to_numeric(yd['Item Barcode'].map(og_uae), errors='coerce')
yd['MDogvYest'] = pd.to_numeric(yd['Net Sales Qty'],errors='coerce') * yd['_og']
yd['MDamtYest'] = pd.to_numeric(yd['Net Sales Amt'],errors='coerce').where(yd['_og'].notna(), 0.0)

# ---- Tag-based yesterday FP metrics, per store (from master FP/MD tag) ----
# Authoritative FP/MD comes from the master. For each store's yesterday sales:
#   FP Sales %  = FP-tagged sales amount / total sales amount   (by AMOUNT)
#   FP units %  = FP-tagged units / total units                (shown alongside)
# Computed from the datewise sales file (single day = yesterday). Other periods fall back
# to the KPI file's FP% (which has no unit count).
#
# Every sale genuinely happened in one real store/country, so per-store fp_yest[loc] always
# tags using that sale's OWN real country (never the All-Countries UAE-default — that default
# only applies to the combined All-Countries KPI figure, computed separately in combine_kpis).
loc2country = inv.groupby('Location')['Country'].first().to_dict()
fp_yest = {}   # location -> {'amt_pct':0-1, 'unit_pct':0-1, 'fp_units':int, 'tot_units':int}
_yt = yd.copy()
if 'Country' in _yt.columns:
    _yt['_cty'] = _yt['Country']
else:
    _yt['_cty'] = _yt['Location'].map(loc2country)
_unmapped_ctys = sorted(set(_yt['_cty'].dropna().unique()) - set(COUNTRY_TO_TAGCOL))
if _unmapped_ctys:
    print(f'Sales-file countries with no FP/MD tag-column mapping (FP/MD will be blank for '
          f'these rows): {_unmapped_ctys} - add to COUNTRY_TO_TAGCOL if this is unexpected')
_yt['_tagcol'] = _yt['_cty'].map(tagcol_for_country)
def _bc_tag(bc, tagcol):
    tags = bc2fpmd_cty.get(bc)
    return tags.get(tagcol) if (tags and tagcol) else None
# real-country tag (used for every per-store and per-country figure)
_yt['_tag_real'] = [_bc_tag(bc, tc) for bc, tc in zip(_yt['Item Barcode'], _yt['_tagcol'])]
# UAE-default tag (used ONLY for the All-Countries combined figure, in combine_kpis below)
_yt['_tag_alldef'] = _yt['Item Barcode'].map(
    lambda bc: (bc2fpmd_cty.get(bc) or {}).get(ALL_COUNTRIES_DEFAULT_TAGCOL))
_yt['_isfp_real']   = (_yt['_tag_real']=='FP')
_yt['_isfp_alldef'] = (_yt['_tag_alldef']=='FP')
_yt['_fp_amt']  = _yt['_isfp_real'] * _yt['Net Sales Amt']
_yt['_fp_qty']  = _yt['_isfp_real'] * _yt['Net Sales Qty']
_yt['_fp_amt_alldef'] = _yt['_isfp_alldef'] * _yt['Net Sales Amt']
_yt['_fp_qty_alldef'] = _yt['_isfp_alldef'] * _yt['Net Sales Qty']
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

# yesterday cost for category-level GP% (0 when the datewise file carries no cost column;
# runs after gp_store above so it doesn't change that block's behaviour).
if 'Cost Amt' not in yd.columns: yd['Cost Amt'] = 0
yd['Cost Amt'] = pd.to_numeric(yd['Cost Amt'], errors='coerce').fillna(0)
yd_key = yd.groupby(['Location','Key']).agg(YestAmt=('Net Sales Amt','sum'),
                                            YestQty=('Net Sales Qty','sum'),
                                            YestCost=('Cost Amt','sum'),
                                            MDamtYest=('MDamtYest','sum'),
                                            MDogvYest=('MDogvYest','sum')).reset_index()

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

# ---- markdown inputs: UAE OG price (AED) vs AED net sales -> discount% = 1 - sales/(qty*og)
# Per barcode, per period, emit paired sums: MDamt<P> (og-known net sales) and MDogv<P>
# (qty * og). og-unknown barcodes contribute to neither, keeping the ratio consistent.
inv['_og'] = pd.to_numeric(inv['Item Barcode'].map(og_uae), errors='coerce')
for _sfx,_qc,_ac in [('W','Net Sales Qty (WTD)','Net Sales Amt (WTD)'),
                     ('M','Net Sales Qty (MTD)','Net Sales Amt (MTD)'),
                     ('Y','Net Sales Qty (YTD)','Net Sales Amt (YTD)')]:
    inv['MDogv'+_sfx] = pd.to_numeric(inv[_qc],errors='coerce') * inv['_og']
    inv['MDamt'+_sfx] = pd.to_numeric(inv[_ac],errors='coerce').where(inv['_og'].notna(), 0.0)

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
        MDamtW=('MDamtW','sum'), MDogvW=('MDogvW','sum'),
        MDamtM=('MDamtM','sum'), MDogvM=('MDogvM','sum'),
        MDamtY=('MDamtY','sum'), MDogvY=('MDogvY','sum'),
    ).reset_index()
# Relabel group (Category) and dept (Sub category) from the FN_Color_Code_Master, keyed by
# Color Code (== Key). Inventory's Item Group/Department remain only as a fallback when a
# color code has no master Category/Sub. Exclusion was already applied on inventory above.
g['Group'] = [cat_for(k, fg) for k, fg in zip(g['Key'], g['Group'])]
g['Dept']  = [sub_for(k, fd) for k, fd in zip(g['Key'], g['Dept'])]
g = g.merge(yd_key, on=['Location','Key'], how='left')
g[['YestAmt','YestQty','YestCost','MDamtYest','MDogvYest']] = g[['YestAmt','YestQty','YestCost','MDamtYest','MDogvYest']].fillna(0)

# ---- markdown KPI: avg discount per store / country / All Countries, per period ----
# discount% = 1 - (og-known net sales) / (qty * UAE og price), summed over the scope.
def _md_ratio(amt_sum, ogv_sum):
    # Self-contained rounding: this block runs before round2() is defined in this script.
    if not (ogv_sum and ogv_sum > 0): return None
    _v = (1 - amt_sum/ogv_sum) * 100
    if _v != _v or _v in (float('inf'), float('-inf')): return None
    return round(float(_v), 2)
_MD_PER = [('yesterday','Yest'),('wtd','W'),('mtd','M'),('ytd','Y')]
def _md_scope(sub):
    return {p: _md_ratio(sub['MDamt'+sfx].sum(), sub['MDogv'+sfx].sum()) for p,sfx in _MD_PER}
markdown_kpi = {}
for _loc,_sub in g.groupby('Location'): markdown_kpi[_loc]=_md_scope(_sub)
for _cty,_sub in g.groupby('Country'): markdown_kpi[_cty]=_md_scope(_sub)
markdown_kpi['All Countries']=_md_scope(g)

# ---- GP% KPI: gross profit % per store / country / All Countries, per period (Total-row source) ----
def _gp_ratio(cost_sum, sales_sum):
    if not (sales_sum and sales_sum > 0 and cost_sum and cost_sum > 0): return None
    _v = (1 - cost_sum/sales_sum) * 100
    if _v != _v or _v in (float('inf'), float('-inf')): return None
    return round(float(_v), 2)
_GP_COLS = [('yesterday','YestCost','YestAmt'),('wtd','WTDcost','WTDamt'),
            ('mtd','MTDcost','MTDamt'),('ytd','YTDcost','YTDamt')]
def _gp_scope(sub):
    return {p: _gp_ratio(sub[cc].sum(), sub[ac].sum()) for p,cc,ac in _GP_COLS}
gp_kpi = {}
for _loc,_sub in g.groupby('Location'): gp_kpi[_loc]=_gp_scope(_sub)
for _cty,_sub in g.groupby('Country'): gp_kpi[_cty]=_gp_scope(_sub)
gp_kpi['All Countries']=_gp_scope(g)

# ---- Store area (sq ft) from the 'Productivity' tab + Productivity KPI ----
# productivity = (period sales / days elapsed) * 365 / sq ft, converted AED->USD (always USD).
# Physical stores only: ecom and any store without a sq-ft entry are excluded from both sides.
def _load_sqft():
    try:
        sd = pd.read_excel(U+'FN_Color_Code_Master.xlsx', sheet_name='Productivity')
        sd.columns=[str(c).strip() for c in sd.columns]
        _lc = next((c for c in sd.columns if c.strip().lower() in ('location','store','store name')), sd.columns[0])
        _ac = next((c for c in sd.columns if 'area' in str(c).lower() or 'sq' in str(c).lower()), None)
        if _ac is None: return {}
        out={}
        for _n,_a in zip(sd[_lc], sd[_ac]):
            if pd.notna(_n) and pd.notna(_a):
                try: out[str(_n).strip()] = float(_a)
                except Exception: pass
        return out
    except Exception as ex:
        print('Productivity tab not read (productivity disabled):', ex); return {}
STORE_SQFT=_load_sqft()
print('Productivity sq-ft loaded: %d stores' % len(STORE_SQFT))
_AEDUSD = 3.6725
_PDAYS = {'yesterday':1, 'wtd':DAYS_ELAPSED, 'mtd':DAYS_IN_MONTH, 'ytd':DAYS_IN_YEAR}
_PAMT  = {'yesterday':'YestAmt','wtd':'WTDamt','mtd':'MTDamt','ytd':'YTDamt'}
_gstores = set(g['Location'].unique())
_sqft = {L:a for L,a in STORE_SQFT.items() if L in _gstores}
_unm  = [L for L in STORE_SQFT if L not in _gstores]
if _unm: print('Productivity: %d sq-ft store(s) unmatched to sales (ignored): %s' % (len(_unm), _unm[:10]))
_store_sales = {pp: g.groupby('Location')[c].sum().to_dict() for pp,c in _PAMT.items()}
_store_cty   = g.groupby('Location')['Country'].first().to_dict()
def _prod(sqft_sum, sales_sum, period):
    d = _PDAYS[period]
    if not (sqft_sum and sqft_sum>0 and d and d>0): return None
    ann = (sales_sum / d) * 365.0
    return int(round((ann / sqft_sum) / _AEDUSD))
productivity_kpi = {}
for L,a in _sqft.items():
    productivity_kpi[L] = {pp:_prod(a,_store_sales[pp].get(L,0.0),pp) for pp in _PDAYS}
_cty_sqft={}; _cty_sales={pp:{} for pp in _PDAYS}
for L,a in _sqft.items():
    c=_store_cty.get(L)
    if c is None: continue
    _cty_sqft[c]=_cty_sqft.get(c,0.0)+a
    for pp in _PDAYS: _cty_sales[pp][c]=_cty_sales[pp].get(c,0.0)+_store_sales[pp].get(L,0.0)
for c,a in _cty_sqft.items():
    productivity_kpi[c] = {pp:_prod(a,_cty_sales[pp][c],pp) for pp in _PDAYS}
_all_sqft=sum(_sqft.values())
productivity_kpi['All Countries'] = {pp:_prod(_all_sqft, sum(_store_sales[pp].get(L,0.0) for L in _sqft), pp) for pp in _PDAYS}
print('Productivity KPI: %d scopes (All-Countries YTD = $%s /sqft/yr)' % (len(productivity_kpi), productivity_kpi.get('All Countries',{}).get('ytd')))

# ---- WH stock KPI: warehouse/DC qty for the current scope (current snapshot, not per-period) ----
# Country / All Countries -> that country's (or all) merchandise WH qty.
# Single store -> the store's country DC qty, restricted to the color codes the store holds.
def _r0(x):
    try: return int(round(float(x)))
    except: return None
wh_kpi = {'All Countries': _r0(wh_total_qty)}
for _cty,_q in wh_country_qty.items():
    wh_kpi[_cty] = _r0(_q)
if wh_cc_qty:
    for _loc,_sub in g.groupby('Location'):
        _cty = _sub['Country'].iloc[0] if len(_sub) else None
        _held = set(_sub[_sub['InvQty']>0]['Key'])
        _t = 0.0
        for _k in _held:
            _t += wh_cc_qty.get((_cty,_k), 0.0)
        wh_kpi[_loc] = _r0(_t)

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

def item_row(r, country=None):
    """Full attributes for one Key at one store, for client-side ranking/filtering.
    country=None means the All-Countries view -> resolve FP/MD via the UAE default;
    otherwise resolve against that country's own real tag."""
    gm = gm_freshest(r)
    _mt = fpmd_for(cc2fpmd_cty, r['Key'], country, all_countries=(country is None))
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

def item_list(sub, country=None):
    return [item_row(r, country=country) for _,r in sub.iterrows()]

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

def candidate_items(sub, country=None):
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
    return item_list(sub.loc[sorted(keep_idx)], country=country)

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
        _hasmd = 'MDogvYest' in sub.columns
        def _mdp(ac,oc):
            if not _hasmd: return None
            a=sub[ac].sum(); o=sub[oc].sum()
            return round2((1-a/o)*100) if (o and o>0) else None
        def _gpp(cc,ac):
            if cc not in sub.columns: return None
            c=sub[cc].sum(); a=sub[ac].sum()
            return round2((1-c/a)*100) if (a and a>0 and c and c>0) else None
        return {
            'gp':{'yesterday':_gpp('YestCost','YestAmt'),'wtd':_gpp('WTDcost','WTDamt'),
                  'mtd':_gpp('MTDcost','MTDamt'),'ytd':_gpp('YTDcost','YTDamt')},
            'md':{'yesterday':_mdp('MDamtYest','MDogvYest'),'wtd':_mdp('MDamtW','MDogvW'),
                  'mtd':_mdp('MDamtM','MDogvM'),'ytd':_mdp('MDamtY','MDogvY')},
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
import re as _re
_CORE_SET = {8,10,12,14,16}
def _core_size(s):
    m = _re.search(r'size\s*(\d+)', str(s), _re.I)
    if m:
        n = int(m.group(1))
        if n in _CORE_SET: return n
    return None
# Size-set completeness is an apparel concept (the 8-16 size run). Restrict it to the women's
# apparel categories that use that run; non-apparel (bags, jewellery, girls-wear, belts,
# hangers/packaging, and other runs) is excluded from BOTH size-set logics and the total.
APPAREL_CATS = {'DRESSES','TOPS','OUTERWEAR','SKIRTS','PANTS','PETITE'}
def _is_apparel(cat): return str(cat).strip().upper() in APPAREL_CATS
SIZESET_FULL_MIN = 4
def inventory_snapshot(df, country=None):
    """Build the 4-part inventory snapshot for an inventory sub-frame (a store or a
    combined set). All sections use in-stock rows (Inventory Qty > 0). Both a units basis
    (Inventory Qty) and a value basis (Inventory Value) are emitted so the dashboard can
    toggle between them client-side.
    country=None means the All-Countries combined view -> FP/MD resolves via the UAE
    default. Otherwise FP/MD resolves against that country's own real tag. The frame passed
    in (inv_sub / inv_c / _allinv) is always homogeneous w.r.t. this rule at the call site:
    a single store or single country's rows for the real-country case, or every country's
    rows together for the All-Countries case."""
    sub = df[df['Inventory Qty'] > 0].copy()
    if sub.empty:
        return {'fpmd':[],'season':[],'style':[],'size':[],'sizeset':[],'total_cc':0,
                'total_units':0,'total_value':0}
    _all_ctry = (country is None)
    sub['FPMD'] = sub['Item Barcode'].map(
        lambda bc: fpmd_for(bc2fpmd_cty, bc, country, all_countries=_all_ctry))
    _cc_tag_cache = {}
    def _cc_tag(cc):
        if cc not in _cc_tag_cache:
            _cc_tag_cache[cc] = fpmd_for(cc2fpmd_cty, cc, country, all_countries=_all_ctry)
        return _cc_tag_cache[cc]
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
    # master per-color-code tag (cc2fpmd_cty, resolved per this call's country); untagged
    # color codes still count toward the overall.
    def _setcomp(frame):
        if 'Item Size' not in frame.columns or frame.empty:
            return {'comp':None,'total_cc':0,'full_cc':0,'fp_comp':None,'fp_cc':0,'md_comp':None,'md_cc':0,
                    'comp2':None,'fp_comp2':None,'md_comp2':None}
        nsizes = frame.groupby('Key')['Item Size'].nunique()
        # alt logic: count of DISTINCT in-stock CORE sizes (8,10,12,14,16) per color code
        core_cnt = frame.groupby('Key')['Item Size'].apply(
            lambda s: len({_core_size(x) for x in s} - {None}))
        a_full=a_tot=fp_full=fp_tot=md_full=md_tot=0
        b_full=bfp_full=bmd_full=0
        for cc, n in nsizes.items():
            full = 1 if (n >= SIZESET_FULL_MIN or (cc_total_sizes.get(cc) and n >= cc_total_sizes.get(cc))) else 0
            full_b = 1 if core_cnt.get(cc,0) >= 3 else 0
            a_tot+=1; a_full+=full; b_full+=full_b
            tag = _cc_tag(cc)
            if tag=='FP': fp_tot+=1; fp_full+=full; bfp_full+=full_b
            elif tag=='MD': md_tot+=1; md_full+=full; bmd_full+=full_b
        _pct=lambda f,t: round2(100*f/t) if t else None
        return {'comp':_pct(a_full,a_tot),'total_cc':int(a_tot),'full_cc':int(a_full),
                'fp_comp':_pct(fp_full,fp_tot),'fp_cc':int(fp_tot),
                'md_comp':_pct(md_full,md_tot),'md_cc':int(md_tot),
                'comp2':_pct(b_full,a_tot),'fp_comp2':_pct(bfp_full,fp_tot),'md_comp2':_pct(bmd_full,md_tot)}
    sizeset=[]
    for cat, c in sub.groupby('Cat'):
        if not _is_apparel(cat): continue   # size-set completeness = apparel categories only
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
    tot_sizeset=_setcomp(sub[sub['Cat'].map(_is_apparel)])  # overall size-set completeness — apparel categories only

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
    def sum_kpi_targets(locs, s, e):
        """Sum daily KPI-target components over [s,e] for a store or list of stores, then
        derive period ratio targets from the SUMMED totals — never an average of daily
        ratio values (same principle as agg_window's actuals). Returns None if no target
        rows exist in the window for any of the stores."""
        if isinstance(locs, str): locs=[locs]
        qty=foot=inv=rev=0.0
        gp_rev=gp_w=0.0; fp_rev=fp_w=0.0
        found=False
        for loc in locs:
            days = kpi_target_daily.get(loc)
            if not days: continue
            for dte, d in days.items():
                if not (s<=dte<=e): continue
                found=True
                qty+=d['qty']; foot+=d['foot']; inv+=d['inv']; rev+=d['rev']
                if d['gp'] is not None:
                    gp_rev+=d['rev']; gp_w+=d['gp']*d['rev']
                if d['fp'] is not None:
                    fp_rev+=d['rev']; fp_w+=d['fp']*d['rev']
        if not found: return None
        return {
            'qty':qty, 'foot':foot, 'inv':inv, 'rev':rev,
            'asp':  (rev/qty) if qty else None,
            'cr':   (inv/foot) if foot else None,
            'upt':  (qty/inv) if inv else None,
            'aov':  (rev/inv) if inv else None,
            'gp':   (gp_w/gp_rev) if gp_rev else None,
            'fp':   (fp_w/fp_rev) if fp_rev else None,
        }
    def _attach_kpi_targets(ty, _kt):
        """Attach target_<metric> and target_<metric>_pct fields onto a ty dict from a
        sum_kpi_targets() result. Only sets a field when its target is actually available,
        so a metric with no target data (e.g. GP%/FP% before they're populated) simply has
        no target_ key and the dashboard hides that comparison automatically — no code
        change needed once the sheet is filled in."""
        if not _kt: return
        pairs = [('qty','target_qty'), ('foot','target_footfall'), ('cr','target_conv'),
                 ('upt','target_upt'), ('aov','target_aov'), ('asp','target_asp'),
                 ('gp','target_gp'), ('fp','target_fp')]
        actual_key = {'qty':'qty','foot':'footfall','cr':'conv','upt':'upt','aov':'aov',
                      'asp':'asp','gp':'gp','fp':'fullprice'}
        for src, dst in pairs:
            v = _kt.get(src)
            if v is None: continue
            is_pct = src in ('cr','gp','fp')
            tv = round2(v*100) if is_pct else round2(v)
            ty[dst] = tv
            av = ty.get(actual_key[src])
            if av is not None and tv:
                ty[dst+'_pct'] = round2(av/tv*100)
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
                # KPI Targets (Sales Qty / Footfall / Conversion / UPT / AOV / ASP, plus
                # GP% / FP% once populated). Sales Amount's own target is the Budget line
                # above — unrelated to this block, which covers the other metrics.
                _attach_kpi_targets(ty, sum_kpi_targets(loc, s, e))
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
    def combine_kpis(locs, lfl=False, all_countries=False):
        """Sum KPIs across store locations, per period, TY and LY.
        When lfl=True, restrict to like-for-like: a store counts if it traded during last
        year's window at all (opened on/before the LY window end). For each such store the
        TY and LY windows are clipped to the span where it traded in BOTH years, then summed
        across the comparable cohort — so partially-open stores still contribute their
        comparable portion rather than being dropped entirely.
        all_countries=True is used ONLY for the All-Countries combined KPI figure: the
        yesterday FP Sales % override below then reads the UAE-default tag columns instead
        of each sale's own real-country tag (every other view always uses the real tag)."""
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
                    _fpcol = '_fp_amt_alldef' if all_countries else '_fp_amt'
                    _fqcol = '_fp_qty_alldef' if all_countries else '_fp_qty'
                    _fpa=_m[_fpcol].sum(); _ta=_m['Net Sales Amt'].sum()
                    _fpq=_m[_fqcol].sum(); _tq=_m['Net Sales Qty'].sum()
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
                _attach_kpi_targets(ty, sum_kpi_targets(locs, s, e))
            blob_extra={'lfl_stores':len(mem)} if lfl else {}
            out[p]={'ty':ty,'ly':ly, **blob_extra}
        return out
except Exception as ex:
    print('KPI load skipped:', ex)
    def combine_kpis(locs, lfl=False, all_countries=False): return None

# ---------------- ECOM sales KPI (Forever New ecom report, dated) ----------------
# Drives two Stores-view tiles: ECOM Sales and Share of Business. Dated per Day Date, so it
# responds to the Yesterday/WTD/MTD/YTD period selector, and (spanning last year) yields an
# LY delta. Aggregated per Shipping Country + an All-Countries roll-up. The FN report is
# Forever New only, so no brand filter is applied. Source: newest FN_Ecom_Sales_*.xlsx
# dropped by the Zap; if absent, the tiles simply show "accruing"/"—".
ecom_kpi = {}
try:
    # Find the newest ecom file with a LOCAL glob import — the module-level `_g`/`_newest`
    # helper gets shadowed by a DataFrame earlier in this script, so we must not rely on it here.
    import glob as _eglob
    _ecands = sorted(_eglob.glob(U + 'FN_Ecom_Sales_*.xlsx'), key=os.path.getmtime)
    if not _ecands:
        raise FileNotFoundError('FN_Ecom_Sales_*.xlsx')
    ECOM_FILE = _ecands[-1]
    print('Using ecom   :', os.path.basename(ECOM_FILE))
    # Title row + blank row precede the real header, so detect the header row ('Order No').
    _probe = pd.read_excel(ECOM_FILE, sheet_name=0, header=None, nrows=8)
    _hrow = 0
    for _i in range(len(_probe)):
        if (_probe.iloc[_i].astype(str).str.strip() == 'Order No').any():
            _hrow = _i; break
    edf = pd.read_excel(ECOM_FILE, sheet_name=0, header=_hrow)
    edf.columns=[str(c).strip() for c in edf.columns]
    edf['_date']=pd.to_datetime(edf['Day Date'],errors='coerce')
    edf['_country']=edf['Shipping Country'].astype(str).str.strip()
    for _c in ['Net Sales','Ordered Qty','Cost Amount','No of orders']:
        edf[_c]=pd.to_numeric(edf.get(_c),errors='coerce')
    edf=edf.dropna(subset=['_date'])
    # Anchor windows to the ecom report's own latest date (capped at AS_OF).
    _edates=edf['_date'].dt.date
    ECOM_ASOF=min(AS_OF, _edates.max()) if len(_edates) else AS_OF
    def _ewin(period):
        if period=='yesterday': return ECOM_ASOF, ECOM_ASOF
        if period=='wtd': return ECOM_ASOF - dt.timedelta(days=ECOM_ASOF.weekday()), ECOM_ASOF
        if period=='mtd': return ECOM_ASOF.replace(day=1), ECOM_ASOF
        return ECOM_ASOF.replace(month=1, day=1), ECOM_ASOF
    def _eagg(sub, s, e):
        w=sub[(sub['_date'].dt.date>=s)&(sub['_date'].dt.date<=e)]
        if w.empty: return None
        sales=w['Net Sales'].sum(); qty=w['Ordered Qty'].sum()
        cost=w['Cost Amount'].sum(); orders=w['No of orders'].sum()
        return {'sales':round2(sales),'qty':round2(qty),
                'gp':round2((1-cost/sales)*100) if (sales and sales!=0) else None,
                'orders':round2(orders)}
    def _ebuild(sub):
        out={}
        for p in ['yesterday','wtd','mtd','ytd']:
            s,e=_ewin(p)
            try: ls,le=s.replace(year=s.year-1), e.replace(year=e.year-1)
            except ValueError: ls,le=s.replace(year=s.year-1,day=28), e.replace(year=e.year-1)
            out[p]={'ty':_eagg(sub,s,e),'ly':_eagg(sub,ls,le)}
        return out
    for _c,_csub in edf.groupby('_country'):
        ecom_kpi[_c]=_ebuild(_csub)
    ecom_kpi['All Countries']=_ebuild(edf)
    _ec=sorted([c for c in ecom_kpi if c!='All Countries'])
    print('Ecom KPI loaded: %d rows | countries=%s | ecom as-of %s' % (len(edf), _ec, ECOM_ASOF))
except FileNotFoundError:
    print('Ecom sales report not present (FN_Ecom_Sales_*.xlsx) - ECOM tiles will show as accruing.')
    ecom_kpi={}
except Exception as ex:
    print('Ecom KPI load skipped:', ex)
    ecom_kpi={}

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
          'items':candidate_items(sub[(sub['InvQty']>0)|(sub['YTDqty']>0)|(sub['YestQty']>0)], country=country)
                  + xcat_item_rows(loc=loc),
          'cat_pivot':cat_pivot(sub),
          'in_transit':in_transit(inv_sub),
          'transit_items':transit_items(loc),
          'inv_snapshot':inventory_snapshot(inv_sub, country=country),
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
          'inv_snapshot':inventory_snapshot(inv_c, country=country),
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
        YestCost=('YestCost','sum'),
        MDamtYest=('MDamtYest','sum'),MDogvYest=('MDogvYest','sum'),
        MDamtW=('MDamtW','sum'),MDogvW=('MDogvW','sum'),
        MDamtM=('MDamtM','sum'),MDogvM=('MDogvM','sum'),
        MDamtY=('MDamtY','sum'),MDogvY=('MDogvY','sum'),
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
    blob['items']=candidate_items(cg[(cg['InvQty']>0)|(cg['YTDqty']>0)|(cg['YestQty']>0)], country=country) \
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
            'inv_snapshot':inventory_snapshot(_allinv, country=None),
            'kpi':None}
acg = g.groupby('Key').agg(
    Desc=('Desc','first'),Group=('Group','first'),Dept=('Dept','first'),Cls=('Cls','first'),
    Season=('Season','first'), LastRecv=('LastRecv','max'),
    YestAmt=('YestAmt','sum'),YestQty=('YestQty','sum'),
    WTDamt=('WTDamt','sum'),WTDqty=('WTDqty','sum'),WTDcost=('WTDcost','sum'),
    MTDamt=('MTDamt','sum'),MTDqty=('MTDqty','sum'),MTDcost=('MTDcost','sum'),
    YTDamt=('YTDamt','sum'),YTDqty=('YTDqty','sum'),YTDcost=('YTDcost','sum'),
    InvQty=('InvQty','sum'),StockCost=('StockCost','sum'),Image=('Image','first'),
    YestCost=('YestCost','sum'),
    MDamtYest=('MDamtYest','sum'),MDogvYest=('MDogvYest','sum'),
    MDamtW=('MDamtW','sum'),MDogvW=('MDogvW','sum'),
    MDamtM=('MDamtM','sum'),MDogvM=('MDogvM','sum'),
    MDamtY=('MDamtY','sum'),MDogvY=('MDogvY','sum'),
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
all_blob['items']=candidate_items(acg[(acg['InvQty']>0)|(acg['YTDqty']>0)|(acg['YestQty']>0)], country=None)
if kpi_store:
    alllocs=[l for l in _alllocs if l in kpi_store]
    all_blob['kpi']=combine_kpis(alllocs, all_countries=True)
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
# WTD per store — sourced from the KPI FILE so the store ranking matches the KPI TILES exactly.
# Previously WTD ranked by the inventory feed's WTD QTY, which disagreed with the tiles (they read
# WTD sales from agg_window over the KPI file, a different as-of). We now rank by KPI-file WTD
# SALES over the tiles' own window (win('wtd')). Any store present in inventory but missing from
# the KPI file falls back to its inventory WTD qty so it never silently drops from the ranking.
def _kpi_wtd_by_store():
    out = {}
    try:
        _s, _e = win('wtd')
        _w = kdf[(kdf['Date'].dt.date >= _s) & (kdf['Date'].dt.date <= _e)]
        if not _w.empty and 'Net Sales Amt' in _w.columns:
            out = _w.groupby('Location')['Net Sales Amt'].sum().to_dict()
    except Exception as _kex:
        print('WTD-by-store from KPI file unavailable, using inventory WTD:', _kex)
    return out
_kpi_wtd = _kpi_wtd_by_store()
_inv_wtd_qty = inv.groupby('Location')['Net Sales Qty (WTD)'].sum()
if _kpi_wtd:
    _missing = sorted(set(_inv_wtd_qty.index) - set(_kpi_wtd.keys()))
    if _missing:
        print('WTD ranking: %d store(s) not in KPI file -> inventory-WTD fallback: %s'
              % (len(_missing), _missing[:10]))
    wtd_store = pd.Series({L: _kpi_wtd.get(L, float(_inv_wtd_qty.get(L, 0.0))) for L in _inv_wtd_qty.index})
    _WTD_IS_QTY = False   # now KPI sales amount
    print('WTD ranking source: KPI file (%d stores) + inventory fallback (%d)'
          % (len(_kpi_wtd), len(_missing)))
else:
    wtd_store = _inv_wtd_qty
    _WTD_IS_QTY = True    # fell back to inventory qty
    print('WTD ranking source: inventory feed qty (KPI file unavailable)')
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
    'wtd':build_store_rank(wtd_store, is_qty=_WTD_IS_QTY),
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
         'markdown_kpi':markdown_kpi,
         'productivity_kpi':productivity_kpi,
         'gp_kpi':gp_kpi,
         'wh_kpi':wh_kpi,
         'ecom_kpi':ecom_kpi,
         'weekly':weekly,
         'shipments':shipments,
         'stores':stores}

json.dump(summary, open(OUT,'w'), separators=(',',':'))
sz=os.path.getsize(OUT)/1024
print(f'Wrote {OUT}  ({sz:.0f} KB)  | stores={len(stores)} | as_of={AS_OF} days_elapsed={DAYS_ELAPSED}')
print('Country rank:', [(c["country"],c["rank"],c["pct"]) for c in country_rank])
