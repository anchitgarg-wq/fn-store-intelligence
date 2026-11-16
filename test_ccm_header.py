import os, re, sys
import pandas as pd
src = open('/home/claude/fn-store-intelligence/aggregate_core_fn.py', encoding='utf-8').read()
i = src.index('def _find_header('); j = src.index('_ccm_sheet, _ccm_hrow', i)
ns = {'pd': pd, 'os': os}
exec(src[i:j], ns)
_find_header = ns['_find_header']

OUT = '/tmp/claude-0/-home-claude/876e200e-9117-534f-842a-fe213ee8035a/scratchpad/hdrtest'
fails = []
def check(c, w):
    print(('  ok   ' if c else '  FAIL ') + w)
    if not c: fails.append(w)

NAMES = ['Item Barcode','Color Code','Item Style Code','Item Description','Category',
         'Sub category','Item Size','Item Color','UAE','KUWAIT','SAUDI ARABIA','BAHRAIN','QATAR']
GROUP = ['']*8 + ['OG PRICE']*5
DATA  = ['9351746085464','25461102','JA5616','Josephine Coat','Outerwear','Coats','Size 6',
         'VAPOR GREY','510','43','520','53','510']

def write(path, sheets):
    with pd.ExcelWriter(path, engine='openpyxl') as w:
        for name, rows in sheets.items():
            pd.DataFrame(rows).to_excel(w, sheet_name=name, index=False, header=False)
    return path

print('\n# the documented two-row header (today\'s file)')
p = write(OUT+'/a.xlsx', {'Sheet1': [GROUP, NAMES, DATA], 'Budget': [['x']]})
check(_find_header(p) == ('Sheet1', 1), f'detects row 1 -> {_find_header(p)}')

print('\n# a blank row prepended - what a hard-coded header=1 cannot survive')
p = write(OUT+'/b.xlsx', {'Sheet1': [['']*13, GROUP, NAMES, DATA]})
check(_find_header(p) == ('Sheet1', 2), f'detects row 2 -> {_find_header(p)}')

print('\n# a single header row, no group labels')
p = write(OUT+'/c.xlsx', {'Sheet1': [NAMES, DATA]})
check(_find_header(p) == ('Sheet1', 0), f'detects row 0 -> {_find_header(p)}')

print('\n# a title row above the group labels')
p = write(OUT+'/d.xlsx', {'Sheet1': [['FN Color Code Master — Nov 2026']+['']*12, GROUP, NAMES, DATA]})
check(_find_header(p) == ('Sheet1', 2), f'detects row 2 -> {_find_header(p)}')

print('\n# a sheet inserted in front of the data sheet')
p = write(OUT+'/e.xlsx', {'ReadMe': [['notes']], 'Sheet1': [GROUP, NAMES, DATA]})
got = _find_header(p)
check(got == ('Sheet1', 1), f'finds the data sheet, not sheet 0 -> {got}')

print('\n# sheet 0 wins when more than one sheet qualifies')
p = write(OUT+'/f.xlsx', {'Sheet1': [GROUP, NAMES, DATA], 'Copy': [GROUP, NAMES, DATA]})
check(_find_header(p) == ('Sheet1', 1), 'unchanged workbooks read exactly as before')

print('\n# no Item Barcode anywhere: a message that names the problem')
p = write(OUT+'/g.xlsx', {'Sheet1': [['a','b']], 'Budget': [['c']]})
try:
    _find_header(p); check(False, 'should have raised')
except KeyError as e:
    m = str(e)
    check('no sheet has' in m and 'Sheet1' in m and 'Budget' in m,
          'names the sheets it searched: ' + m[:120].replace('\\n',' '))

print('\n# the detected header actually yields a usable frame')
p = write(OUT+'/b.xlsx', {'Sheet1': [['']*13, GROUP, NAMES, DATA]})
sh, hr = _find_header(p)
df = pd.read_excel(p, dtype=str, sheet_name=sh, header=hr)
df.columns = [str(c).strip() for c in df.columns]
check('Item Barcode' in df.columns, 'Item Barcode present')
check(df['Item Barcode'].iloc[0] == '9351746085464', 'first barcode reads correctly')
check('UAE' in df.columns, 'UAE price column present')

print('\n' + (f'{len(fails)} FAILED' if fails else 'all passed'))
sys.exit(1 if fails else 0)
