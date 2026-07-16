{% raw %}


<div id="smdash">
<style>
#smdash{
--ink:#1a1a1a; --paper:#faf8f5; --card:#ffffff; --line:#e6e1d8;
--muted:#8a8278; --accent:#b8362f; --accent2:#1f6f5c; --gold:#caa24a;
--pos:#1f6f5c; --neg:#b8362f; --shadow:0 1px 3px rgba(40,25,30,.06),0 6px 24px rgba(40,25,30,.05);
--mono:'JetBrains Mono',ui-monospace,'SF Mono',Menlo,monospace;
--sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
all:initial; font-family:var(--sans); color:var(--ink);
display:block; background:var(--paper); line-height:1.45;
-webkit-font-smoothing:antialiased; box-sizing:border-box;
}
#smdash *,#smdash *::before,#smdash *::after{box-sizing:border-box; margin:0; padding:0;}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&display=swap');
#smdash .wrap{max-width:1280px;margin:0 auto;padding:24px 20px 64px;}
#smdash .head{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;
padding-bottom:18px;border-bottom:2px solid var(--ink);flex-wrap:wrap;}
#smdash .brand{font-family:'Fraunces',serif;font-weight:700;font-size:30px;letter-spacing:-.02em;}
#smdash .brand b{color:var(--accent);}
#smdash .sub{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.14em;margin-top:3px;}
#smdash .asof{font-family:var(--mono);font-size:11px;color:var(--muted);text-align:right;}
#smdash .cursel{display:inline-flex;gap:4px;margin-bottom:6px;}
#smdash .curbtn{font:600 10px var(--sans);letter-spacing:.04em;cursor:pointer;padding:3px 10px;
border-radius:7px;border:1px solid var(--line);background:none;color:var(--muted);}
#smdash .curbtn.on{background:var(--accent);color:#fff;border-color:var(--accent);}
#smdash .curnote{font-size:10px;color:var(--muted);font-family:var(--mono);margin-top:3px;}
#smdash .asof b{color:var(--ink);font-weight:600;}
#smdash .filters{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0 8px;align-items:flex-end;}
#smdash .fg{display:flex;flex-direction:column;gap:5px;}
#smdash .fg label{font-size:10px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);font-weight:600;}
#smdash select{font-family:var(--sans);font-size:13px;font-weight:500;color:var(--ink);
background:var(--card);border:1px solid var(--line);border-radius:8px;padding:9px 30px 9px 12px;
min-width:170px;cursor:pointer;appearance:none;
background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%238a8278' fill='none' stroke-width='1.5'/%3E%3C/svg%3E");
background-repeat:no-repeat;background-position:right 12px center;transition:border-color .15s;}
#smdash select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(184,54,47,.1);}
#smdash .periods{display:flex;gap:6px;background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:4px;}
#smdash .pill{font-family:var(--sans);font-size:12px;font-weight:600;letter-spacing:.02em;
padding:7px 14px;border-radius:7px;border:none;background:transparent;color:var(--muted);
cursor:pointer;transition:all .15s;text-transform:uppercase;}
#smdash .pill:hover{color:var(--ink);}
#smdash .pill.on{background:var(--ink);color:#fff;}
#smdash .strip{display:flex;align-items:center;gap:14px;margin:22px 0 6px;flex-wrap:wrap;}
#smdash .strip h2{font-family:'Fraunces',serif;font-weight:600;font-size:22px;letter-spacing:-.01em;}
#smdash .chip{font-family:var(--mono);font-size:11px;font-weight:500;color:var(--muted);
border:1px solid var(--line);border-radius:20px;padding:3px 11px;background:var(--card);}
#smdash .chip.rk{color:var(--accent);border-color:rgba(184,54,47,.3);}
#smdash .grid{display:grid;gap:16px;margin-top:16px;}
#smdash .g2{grid-template-columns:1fr 1fr;}
#smdash .card{background:var(--card);border:1px solid var(--line);border-radius:14px;
box-shadow:var(--shadow);overflow:hidden;}
#smdash .card>h3{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
padding:15px 18px 12px;border-bottom:1px solid var(--line);display:flex;
align-items:center;justify-content:space-between;gap:8px;}
#smdash .card>h3 .tag{font-weight:500;letter-spacing:.04em;color:var(--muted);font-size:10px;}
#smdash .card>h3 .dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:7px;}
#smdash .dot.top{background:var(--accent2);} #smdash .dot.bot{background:var(--accent);}
#smdash .seller{display:grid;grid-template-columns:26px 46px 1fr auto;gap:11px;align-items:center;
padding:9px 18px;border-bottom:1px solid var(--paper);transition:background .12s;}
#smdash .seller:hover{background:var(--paper);} #smdash .seller:last-child{border-bottom:none;}
#smdash .rank{font-family:var(--mono);font-size:12px;font-weight:600;color:var(--muted);text-align:center;}
#smdash .ph{width:46px;height:46px;border-radius:8px;object-fit:cover;background:#f0ece4;border:1px solid var(--line);}
#smdash .phx{width:46px;height:46px;border-radius:8px;background:#1a1a1a;display:flex;align-items:center;
justify-content:center;color:#fff;font-family:'Fraunces',serif;font-weight:700;font-size:9px;letter-spacing:.04em;text-align:center;line-height:1;position:relative;}
#smdash .phx.failed{background:#2b2320;box-shadow:inset 0 0 0 2px var(--gold);}
#smdash .phx.failed::after{content:'';position:absolute;top:-3px;right:-3px;width:10px;height:10px;
border-radius:50%;background:var(--gold);border:2px solid var(--card);}
#smdash img.ph{cursor:zoom-in;transition:transform .12s ease,box-shadow .12s ease;}
#smdash img.ph:hover{transform:scale(1.06);box-shadow:0 2px 10px rgba(40,25,30,.18);}
#smdash .hovprev{position:fixed;z-index:99999;display:none;width:260px;background:var(--card);
border-radius:12px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.32);
border:1px solid var(--line);pointer-events:none;}
#smdash .hovprev img{width:100%;height:auto;max-height:320px;object-fit:contain;background:#f0ece4;display:block;}
#smdash .hovprev-cap{padding:9px 12px;font-size:12.5px;color:var(--ink);border-top:1px solid var(--line);}
#smdash .hovprev-cap b{display:block;font-weight:600;margin-bottom:2px;line-height:1.3;}
#smdash .hovprev-cap span{color:var(--muted);font-size:11px;font-family:var(--mono);}
#smdash .hovstats{margin-top:8px;padding-top:8px;border-top:1px solid var(--line);display:flex;flex-direction:column;gap:4px;}
#smdash .hovstats .hsr{display:flex;justify-content:space-between;gap:12px;font-size:11.5px;}
#smdash .hovstats .hsr span:first-child{color:var(--muted);}
#smdash .hovstats .hsr span:last-child{font-family:var(--mono);font-weight:600;color:var(--ink);}
#smdash .diagbar{display:none;align-items:center;gap:10px;margin:10px 0 0;padding:8px 14px;
background:rgba(202,162,74,.1);border:1px solid rgba(202,162,74,.35);border-radius:9px;
font-size:11.5px;color:#7a5e17;font-family:var(--mono);}
#smdash .diagbar.show{display:flex;}
#smdash .diagbar b{font-weight:600;}
#smdash .diagkey{display:inline-flex;align-items:center;gap:5px;}
#smdash .diagkey .sw{width:11px;height:11px;border-radius:3px;display:inline-block;}
#smdash .diagkey .sw.logo{background:#1a1a1a;} #smdash .diagkey .sw.fail{background:#2b2320;box-shadow:inset 0 0 0 2px var(--gold);}
#smdash .sname{font-size:13px;font-weight:600;letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:230px;}
#smdash .smeta{font-size:10.5px;color:var(--muted);font-family:var(--mono);margin-top:2px;display:flex;gap:9px;flex-wrap:wrap;}
#smdash .smeta b{color:var(--ink);font-weight:600;}
#smdash .sval{text-align:right;font-family:var(--mono);}
#smdash .sval .amt{font-size:14px;font-weight:600;}
#smdash .sval .q{font-size:10.5px;color:var(--muted);margin-top:2px;}
#smdash .wc{display:inline-block;font-family:var(--mono);font-size:10px;font-weight:600;
padding:1px 6px;border-radius:5px;}
#smdash .wc.lo{background:rgba(31,111,92,.12);color:var(--accent2);}
#smdash .wc.hi{background:rgba(202,162,74,.16);color:#8a6d1e;}
#smdash .wc.xx{background:rgba(184,54,47,.1);color:var(--accent);}
#smdash .wc.na{background:#f0ece4;color:var(--muted);}
#smdash .snaphdr{display:flex;align-items:center;gap:10px;margin:18px 0 2px;}
#smdash .snaphdr h2{font-size:15px;font-weight:600;color:var(--ink);margin:0;}
#smdash .snapsub{font-size:11px;color:var(--muted);margin:0 0 8px;}
#smdash .basisbtn{font:600 10px var(--sans);text-transform:uppercase;letter-spacing:.06em;cursor:pointer;
padding:3px 9px;border-radius:7px;border:1px solid var(--line);background:none;color:var(--muted);}
#smdash .basisbtn.on{background:var(--accent);color:#fff;border-color:var(--accent);}
#smdash .snapbody{padding:14px 18px 16px;}
#smdash .snaprow{margin-bottom:11px;}
#smdash .snaprow .lab{display:flex;justify-content:space-between;gap:10px;font-size:12px;margin-bottom:4px;}
#smdash .snaprow .lab .nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
#smdash .snaprow .lab .v{color:var(--muted);white-space:nowrap;flex-shrink:0;font-variant-numeric:tabular-nums;}
#smdash .splitbar{display:flex;height:11px;border-radius:4px;overflow:hidden;background:#f0ece4;}
#smdash .splitbar .fp{background:var(--accent2);} #smdash .splitbar .md{background:#d8804f;}
#smdash .trackbar{height:11px;border-radius:4px;background:#f0ece4;overflow:hidden;}
#smdash .trackbar i{display:block;height:11px;border-radius:4px;}
#smdash .snaplegend{display:flex;gap:14px;margin-top:10px;font-size:11px;color:var(--muted);}
#smdash .snaplegend span{display:flex;align-items:center;gap:4px;}
#smdash .sw9{width:9px;height:9px;border-radius:2px;display:inline-block;}
#smdash .styrow{display:flex;align-items:center;gap:10px;margin-bottom:9px;}
#smdash .styrow .nm{font-size:12px;width:96px;flex-shrink:0;color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
#smdash .styrow .n{font-size:12px;font-weight:600;width:40px;flex-shrink:0;text-align:right;font-variant-numeric:tabular-nums;}
#smdash .sizesub{margin:2px 0 10px 18px;padding-left:10px;border-left:2px solid var(--line);}
#smdash .sizecat{cursor:pointer;border-radius:6px;padding:3px 4px;margin:0 -4px 6px;transition:background .12s;}
#smdash .sizecat:hover{background:rgba(184,54,47,.06);}
#smdash .sizecat .nm{display:flex;align-items:center;gap:6px;}
#smdash .car{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;
border-radius:4px;background:#f0ece4;color:var(--accent);font-size:11px;flex-shrink:0;}
#smdash .car.no{visibility:hidden;}
#smdash .snaptot{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:12px;
padding-top:10px;border-top:1px solid var(--line);font-size:12px;font-weight:600;color:var(--ink);}
#smdash .snaptot .v{color:var(--accent);font-family:var(--mono);font-size:11.5px;text-align:right;}
#smdash table{width:100%;border-collapse:collapse;font-size:12.5px;}
#smdash thead th{font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);
font-weight:600;text-align:right;padding:10px 14px 9px;border-bottom:1px solid var(--line);white-space:nowrap;}
#smdash thead th:first-child{text-align:left;}
#smdash tbody td{padding:9px 14px;border-bottom:1px solid var(--paper);text-align:right;font-family:var(--mono);}
#smdash tbody td:first-child{text-align:left;font-family:var(--sans);font-weight:600;}
#smdash tbody tr:last-child td{border-bottom:none;}
#smdash .bar{position:relative;height:5px;border-radius:3px;background:#f0ece4;margin-top:4px;overflow:hidden;}
#smdash .bar i{position:absolute;left:0;top:0;bottom:0;border-radius:3px;}
#smdash .bar.s i{background:var(--accent);} #smdash .bar.k i{background:var(--accent2);}
#smdash .mixcell{min-width:84px;}
#smdash .mixscroll{overflow-x:auto;-webkit-overflow-scrolling:touch;}
#smdash table.mixwide{min-width:760px;width:100%;}
#smdash table.mixwide th.num,#smdash table.mixwide td.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;}
#smdash table.mixwide td.pct{color:var(--muted);font-size:11px;}
#smdash table.mixwide td.num{font-family:var(--mono);font-size:11.5px;}
#smdash table.mixwide tr.lvl1 td{font-weight:700;background:#faf7f2;}
#smdash table.mixwide tr.lvl1 .cn.g{font-weight:800;}
#smdash table.mixwide tr.lvl2 td,#smdash table.mixwide tr.lvl3 td{font-weight:400;}
#smdash table.cperf{min-width:980px;width:100%;border-collapse:collapse;}
#smdash table.cperf th,#smdash table.cperf td{padding:8px 10px;border-bottom:1px solid var(--line);}
#smdash table.cperf th.num,#smdash table.cperf td.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;}
#smdash table.cperf td.num{font-family:var(--mono);font-size:11.5px;}
#smdash table.cperf td.cname,#smdash table.cperf th:first-child{text-align:left;font-weight:600;white-space:nowrap;}
#smdash table.cperf thead th{background:#1f2937;color:#fff;font:600 10px var(--sans);text-transform:uppercase;letter-spacing:.05em;position:sticky;top:0;}
#smdash table.cperf tr.total td{font-weight:700;background:#faf7f2;border-top:2px solid var(--ink);}
#smdash table.cperf td.pos{color:var(--pos);} #smdash table.cperf td.neg{color:var(--neg);}
#smdash .trendwrap{width:100%;overflow-x:auto;}
#smdash .trendsvg{width:100%;min-width:520px;height:auto;display:block;}
#smdash .trendsvg .cgrid{stroke:var(--line);stroke-width:1;}
#smdash .trendsvg .cyl{fill:var(--muted);font:10px var(--mono);text-anchor:end;}
#smdash .trendsvg .cxl{fill:var(--muted);font:10px var(--sans);text-anchor:middle;}
#smdash .trendsvg .cleg{fill:var(--ink);font:600 11px var(--sans);}
#smdash .trendsvg .cvlab rect{fill:#fff;stroke:var(--line);stroke-width:1;}
#smdash .trendsvg .cvtext{fill:var(--ink);font:700 9.5px var(--mono);text-anchor:middle;}
#smdash select.kpisel{font:600 11px var(--sans);padding:6px 10px;border:1px solid var(--line);border-radius:8px;background:#fff;color:var(--ink);max-width:230px;}
#smdash table.brk td.strong{font-weight:700;color:var(--ink);}
#smdash table.brk{min-width:840px;}
#smdash .mixnum{display:flex;justify-content:flex-end;gap:6px;align-items:baseline;}
#smdash .mixnum span{font-size:9.5px;color:var(--muted);}
#smdash .seg{display:flex;gap:4px;}
#smdash .seg button{font-family:var(--sans);font-size:10px;font-weight:600;text-transform:uppercase;
letter-spacing:.06em;padding:4px 9px;border:1px solid var(--line);background:var(--card);
color:var(--muted);border-radius:6px;cursor:pointer;}
#smdash .seg button.on{background:var(--ink);color:#fff;border-color:var(--ink);}
#smdash .it{display:flex;align-items:center;gap:12px;padding:8px 18px;border-bottom:1px solid var(--paper);}
#smdash .it:last-child{border-bottom:none;}
#smdash .itg{font-size:12px;font-weight:600;min-width:120px;}
#smdash .itd{font-size:11px;color:var(--muted);flex:1;}
#smdash .itbar{flex:2;height:6px;background:#f0ece4;border-radius:3px;overflow:hidden;}
#smdash .itbar i{display:block;height:100%;background:linear-gradient(90deg,var(--gold),#e0c378);border-radius:3px;}
#smdash .itq{font-family:var(--mono);font-size:13px;font-weight:600;min-width:40px;text-align:right;}
#smdash .country{background:var(--ink);color:#fff;border-radius:14px;padding:20px 22px;box-shadow:var(--shadow);}
#smdash .country h3{font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:rgba(255,255,255,.6);font-weight:600;margin-bottom:4px;}
#smdash .chero{display:flex;align-items:baseline;gap:12px;margin:10px 0 18px;flex-wrap:wrap;}
#smdash .chero .big{font-family:'Fraunces',serif;font-size:46px;font-weight:700;line-height:1;}
#smdash .chero .lbl{font-size:13px;color:rgba(255,255,255,.7);}
#smdash .chero .rkbadge{margin-left:auto;font-family:var(--mono);font-size:12px;font-weight:600;
background:var(--accent);padding:5px 12px;border-radius:20px;}
#smdash .crow{display:flex;align-items:center;gap:10px;padding:6px 0;font-size:12px;}
#smdash .crow .cn{min-width:130px;color:rgba(255,255,255,.85);}
#smdash .crow.me .cn{color:var(--gold);font-weight:700;}
#smdash .crow .cbar{flex:1;height:8px;background:rgba(255,255,255,.1);border-radius:4px;overflow:hidden;}
#smdash .crow .cbar i{display:block;height:100%;border-radius:4px;background:rgba(255,255,255,.4);}
#smdash .crow.me .cbar i{background:var(--gold);}
#smdash .crow .cp{font-family:var(--mono);font-size:11px;min-width:80px;text-align:right;color:rgba(255,255,255,.7);}
#smdash .crow.me .cp{color:#fff;font-weight:600;}
#smdash .kpis{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;margin:18px 0 4px;}
#smdash .kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 13px;box-shadow:var(--shadow);}
#smdash .kpi .klabel{font-size:9px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:600;white-space:nowrap;}
#smdash .kpi .kval{font-family:var(--mono);font-size:18px;font-weight:600;margin-top:6px;letter-spacing:-.02em;}
#smdash .kpi .kly{font-size:10px;font-family:var(--mono);color:var(--muted);margin-top:5px;display:flex;align-items:center;gap:4px;flex-wrap:wrap;}
#smdash .kpi .kfp{font-size:9.5px;font-family:var(--mono);color:var(--accent);margin-top:3px;font-weight:500;letter-spacing:-.01em;}
#smdash .kpi .kfp.up{color:var(--pos);}
#smdash .kpi .kfp.down{color:var(--neg);}
#smdash .lflbtn{font:600 10px var(--sans);text-transform:uppercase;letter-spacing:.06em;cursor:pointer;
padding:4px 11px;border-radius:20px;border:1px solid var(--line);background:var(--card);color:var(--muted);}
#smdash .lflbtn.on{background:var(--accent);color:#fff;border-color:var(--accent);}
#smdash .kpi .delta{font-weight:600;padding:1px 5px;border-radius:5px;font-size:9.5px;}
#smdash .delta.up{background:rgba(31,111,92,.12);color:var(--pos);}
#smdash .delta.down{background:rgba(184,54,47,.1);color:var(--neg);}
#smdash .delta.flat{background:#f0ece4;color:var(--muted);}
#smdash .kpi .lyval{color:var(--muted);}
@media(max-width:1100px){#smdash .kpis{grid-template-columns:repeat(4,1fr);}}
@media(max-width:680px){#smdash .kpis{grid-template-columns:repeat(2,1fr);}}
#smdash .titem{display:grid;grid-template-columns:26px 44px 1fr auto;gap:11px;align-items:center;padding:8px 18px;border-bottom:1px solid var(--paper);}
#smdash .titem:last-child{border-bottom:none;}
#smdash .titem .tq{font-family:var(--mono);font-size:15px;font-weight:600;text-align:right;}
#smdash .titem .tq span{font-size:10px;color:var(--muted);font-weight:400;display:block;}
#smdash .sfilters{display:flex;gap:18px;flex-wrap:wrap;align-items:flex-end;margin:14px 0 2px;padding:12px 14px;background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);}
#smdash .sfg{display:flex;flex-direction:column;gap:5px;}
#smdash .sflabel{font-size:9px;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);font-weight:700;}
#smdash .badge{font-size:9px;font-weight:700;padding:1px 5px;border-radius:4px;letter-spacing:.03em;}
#smdash .caret{display:inline-block;width:14px;color:var(--muted);font-size:10px;}
#smdash .caret.no{opacity:0;}
#smdash tbody td .cn{font-weight:500;}
#smdash tbody td .cn.g{font-weight:700;}
#smdash tbody tr.lvl1 td{background:rgba(26,26,26,.02);}
#smdash tbody tr.lvl3 td{font-size:11.5px;color:#555;}
#smdash .gpct{font-size:9px;color:var(--muted);font-weight:400;}
#smdash .badge.fp{background:rgba(31,111,92,.14);color:var(--accent2);}
#smdash .badge.md{background:rgba(202,162,74,.18);color:#8a6d1e;}
#smdash .empty{padding:26px 18px;text-align:center;color:var(--muted);font-size:12px;}
#smdash .foot{margin-top:30px;padding-top:16px;border-top:1px solid var(--line);
font-size:10.5px;color:var(--muted);font-family:var(--mono);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;}
@media(max-width:860px){#smdash .g2{grid-template-columns:1fr;}#smdash .sname{max-width:160px;}}
/* ===== Mobile optimisation (phones ≤ 600px). Desktop & tablet unaffected. ===== */
@media(max-width:600px){
  #smdash .wrap{padding:16px 12px 56px;}
  #smdash .head{flex-direction:column;align-items:stretch;gap:14px;padding-bottom:16px;}
  #smdash .brand{font-size:21px;line-height:1.2;}
  #smdash .sub{margin-top:5px;}
  #smdash .asof{text-align:right;line-height:1.5;margin-top:6px;}
  #smdash .cursel{margin-bottom:0;}
  #smdash .curbtn{padding:7px 18px;font-size:12px;}
  #smdash .filters{flex-direction:column;align-items:stretch;gap:14px;margin:18px 0 10px;}
  #smdash .fg{width:100%;}
  #smdash .fg label{font-size:11px;}
  #smdash select{width:100%;min-width:0;font-size:16px;padding:13px 34px 13px 14px;}
  #smdash .periods{width:100%;}
  #smdash .pill{flex:1;text-align:center;padding:12px 6px;font-size:13px;}
  #smdash .sfilters{flex-direction:column;align-items:stretch;gap:14px;padding:14px;}
  #smdash .sfg{width:100%;}
  #smdash .seg{flex-wrap:wrap;}
  #smdash .seg button{flex:1 1 auto;min-width:0;padding:9px 10px;font-size:11px;white-space:nowrap;}
  /* Currency toggle + as-of date: own full-width row below the brand, right-aligned */
  #smdash .head>div:last-child{align-self:stretch;text-align:right;}
  #smdash .cursel{justify-content:flex-end;}
  #smdash .lflbtn,#smdash .basisbtn{padding:8px 14px;font-size:11px;}
  #smdash .kpis{grid-template-columns:repeat(2,1fr);gap:8px;}
  #smdash .kpi{padding:12px 12px;}
  #smdash .kpi .kval{font-size:20px;}
  #smdash .kpi .klabel{font-size:9.5px;white-space:normal;}
  #smdash .strip{gap:8px;}
  #smdash .strip h2{font-size:19px;}
  #smdash .seller{grid-template-columns:22px 40px 1fr auto;gap:9px;padding:9px 14px;}
  #smdash .titem{grid-template-columns:22px 40px 1fr auto;gap:9px;padding:9px 14px;}
  #smdash .sname{max-width:none;white-space:normal;}
  #smdash .ph,#smdash .phx{width:40px;height:40px;}
  #smdash .country{padding:16px 16px;}
  #smdash .chero .big{font-size:38px;}
  #smdash .crow .cn{min-width:104px;font-size:11px;}
  #smdash .crow .cp{min-width:68px;font-size:10px;}
  #smdash table{font-size:12px;}
  #smdash thead th,#smdash tbody td{padding:8px 9px;}
  #smdash .foot{flex-direction:column;gap:4px;}
}

/* ===================== PI:START — Competitor Intelligence (EDITED) ===================== */
/* Self-contained competitor benchmarking. Deliberately lives in its own drawer and NEVER
   sits beside the ERP's Avg Markdown tile: EDITED's discount is a cut off ticket price
   across listed options on 6th Street / Namshi, while Avg Markdown is revenue-weighted
   actual markdown from the ERP. Different metrics, different populations — never compared. */
#smdash .pi-pill{font:700 11px var(--sans);text-transform:uppercase;letter-spacing:.08em;cursor:pointer;
padding:9px 16px;border-radius:10px;border:1px solid var(--ink);background:var(--ink);color:#fff;
display:inline-flex;align-items:center;gap:7px;white-space:nowrap;}
#smdash .pi-pill:hover{opacity:.88;}
#smdash .pi-pill .pi-dot{width:6px;height:6px;border-radius:50%;background:var(--gold);}
#smdash .pi-scrim{position:fixed;inset:0;background:rgba(26,20,22,.45);z-index:99990;opacity:0;
pointer-events:none;transition:opacity .22s ease;}
#smdash .pi-scrim.on{opacity:1;pointer-events:auto;}
#smdash .pi-drawer{position:fixed;top:0;right:0;bottom:0;width:min(920px,100%);background:var(--paper);
z-index:99991;transform:translateX(100%);transition:transform .26s cubic-bezier(.4,0,.2,1);
overflow-y:auto;-webkit-overflow-scrolling:touch;box-shadow:-8px 0 40px rgba(40,25,30,.18);}
#smdash .pi-drawer.on{transform:translateX(0);}
#smdash .pi-hd{position:sticky;top:0;background:var(--paper);border-bottom:2px solid var(--ink);
padding:18px 22px 14px;display:flex;align-items:flex-start;justify-content:space-between;gap:14px;z-index:2;}
#smdash .pi-ttl{font-family:'Fraunces',serif;font-weight:700;font-size:22px;letter-spacing:-.01em;}
#smdash .pi-sub{font-size:10px;text-transform:uppercase;letter-spacing:.14em;color:var(--muted);margin-top:4px;}
#smdash .pi-x{font:400 24px var(--sans);line-height:1;cursor:pointer;border:none;background:none;
color:var(--muted);padding:2px 6px;}
#smdash .pi-x:hover{color:var(--ink);}
#smdash .pi-bar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:12px 22px 0;}
#smdash .pi-fresh{font:600 10px var(--mono);padding:3px 10px;border-radius:20px;letter-spacing:.03em;}
#smdash .pi-fresh.ok{background:rgba(31,111,92,.12);color:var(--pos);}
#smdash .pi-fresh.old{background:rgba(184,54,47,.12);color:var(--neg);}
#smdash .pi-mkt{display:flex;gap:4px;}
#smdash .pi-mkt button{font:600 10px var(--sans);letter-spacing:.06em;cursor:pointer;padding:5px 13px;
border-radius:7px;border:1px solid var(--line);background:var(--card);color:var(--muted);}
#smdash .pi-mkt button.on{background:var(--accent);color:#fff;border-color:var(--accent);}
#smdash .pi-tabs{display:flex;gap:4px;overflow-x:auto;padding:12px 22px 0;}
#smdash .pi-tabs button{font:600 11px var(--sans);cursor:pointer;padding:8px 13px;border:none;
background:none;color:var(--muted);border-bottom:2px solid transparent;white-space:nowrap;}
#smdash .pi-tabs button.on{color:var(--ink);border-bottom-color:var(--accent);}
#smdash .pi-body{padding:16px 22px 40px;}
#smdash .pi-kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-bottom:16px;}
#smdash .pi-kpi{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:11px 12px;}
#smdash .pi-kpi .l{font:600 8.5px var(--sans);text-transform:uppercase;letter-spacing:.08em;color:var(--muted);}
#smdash .pi-kpi .v{font:600 19px var(--mono);margin-top:5px;letter-spacing:-.02em;}
#smdash .pi-kpi .s{font:400 9.5px var(--mono);color:var(--muted);margin-top:3px;}
#smdash .pi-kpi .v.bad{color:var(--neg);}
#smdash .pi-card{background:var(--card);border:1px solid var(--line);border-radius:13px;
box-shadow:var(--shadow);margin-bottom:14px;overflow:hidden;}
#smdash .pi-card h4{font:700 11px var(--sans);text-transform:uppercase;letter-spacing:.1em;
padding:14px 16px 11px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;
align-items:center;gap:8px;}
#smdash .pi-card h4 .t{font:500 9.5px var(--sans);letter-spacing:.03em;color:var(--muted);text-transform:none;}
#smdash .pi-cb{padding:14px 16px 16px;}
#smdash .pi-hl{display:flex;gap:10px;padding:11px 16px;border-bottom:1px solid var(--paper);align-items:flex-start;}
#smdash .pi-hl:last-child{border-bottom:none;}
#smdash .pi-sev{width:7px;height:7px;border-radius:50%;margin-top:6px;flex-shrink:0;}
#smdash .pi-sev.high{background:var(--neg);} #smdash .pi-sev.watch{background:var(--gold);}
#smdash .pi-sev.ok{background:var(--pos);}   #smdash .pi-sev.info{background:var(--muted);}
#smdash .pi-hl .k{font:700 10px var(--sans);text-transform:uppercase;letter-spacing:.06em;
color:var(--ink);margin-bottom:2px;}
#smdash .pi-hl .x{font-size:12.5px;color:#4a4247;line-height:1.5;}
#smdash .pi-lad{display:flex;align-items:center;gap:9px;margin-bottom:9px;}
#smdash .pi-lad .nm{font-size:11.5px;width:104px;flex-shrink:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
#smdash .pi-lad .nm.me{font-weight:700;color:var(--accent);}
#smdash .pi-lad .st{flex:1;display:flex;height:15px;border-radius:4px;overflow:hidden;background:#f0ece4;}
#smdash .pi-lad .st i{display:block;height:15px;}
#smdash .pi-lad .dv{font:600 11px var(--mono);width:52px;text-align:right;flex-shrink:0;}
#smdash .pi-lad .dv.me{color:var(--neg);}
#smdash .pi-leg{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;font-size:10px;color:var(--muted);}
#smdash .pi-leg span{display:flex;align-items:center;gap:4px;}
#smdash .pi-leg i{width:9px;height:9px;border-radius:2px;display:inline-block;}
#smdash table.pi-t{width:100%;border-collapse:collapse;font-size:12px;}
#smdash table.pi-t th{font:600 9px var(--sans);text-transform:uppercase;letter-spacing:.07em;
color:var(--muted);text-align:right;padding:9px 10px;border-bottom:1px solid var(--line);white-space:nowrap;}
#smdash table.pi-t th:first-child{text-align:left;}
#smdash table.pi-t td{padding:9px 10px;border-bottom:1px solid var(--paper);text-align:right;
font-family:var(--mono);font-size:11.5px;white-space:nowrap;}
#smdash table.pi-t td:first-child{text-align:left;font-family:var(--sans);font-weight:600;}
#smdash table.pi-t tr.me td{background:rgba(184,54,47,.05);}
#smdash table.pi-t tr.me td:first-child{color:var(--accent);}
#smdash table.pi-t td.bad{color:var(--neg);font-weight:600;}
#smdash .pi-pbar{display:flex;align-items:center;gap:9px;margin-bottom:10px;}
#smdash .pi-pbar .nm{font-size:11.5px;width:104px;flex-shrink:0;}
#smdash .pi-pbar .nm.me{font-weight:700;color:var(--accent);}
#smdash .pi-pbar .tr{flex:1;position:relative;height:15px;background:#f0ece4;border-radius:4px;}
#smdash .pi-pbar .tr i{position:absolute;top:0;bottom:0;left:0;border-radius:4px;background:#cfc7c0;}
#smdash .pi-pbar .tr b{position:absolute;top:0;bottom:0;left:0;border-radius:4px;background:var(--accent2);}
#smdash .pi-pbar .vv{font:600 10.5px var(--mono);width:112px;text-align:right;flex-shrink:0;color:var(--muted);}
#smdash .pi-note{font-size:11px;color:var(--muted);line-height:1.6;padding:12px 16px;
background:rgba(202,162,74,.08);border:1px solid rgba(202,162,74,.28);border-radius:10px;margin-bottom:14px;}
#smdash .pi-fail{padding:40px 20px;text-align:center;color:var(--neg);font-size:13px;font-weight:600;
background:rgba(184,54,47,.06);border:1px solid rgba(184,54,47,.3);border-radius:12px;}
#smdash .pi-fail span{display:block;font-weight:400;color:var(--muted);font-size:11.5px;margin-top:8px;}
#smdash .pi-ft{margin-top:22px;padding-top:14px;border-top:1px solid var(--line);
font:400 10px var(--mono);color:var(--muted);line-height:1.7;}
@media(max-width:700px){
  #smdash .pi-kpis{grid-template-columns:repeat(2,1fr);}
  #smdash .pi-lad .nm,#smdash .pi-pbar .nm{width:76px;font-size:10.5px;}
  #smdash .pi-body,#smdash .pi-bar,#smdash .pi-tabs,#smdash .pi-hd{padding-left:14px;padding-right:14px;}
}
/* ===================== PI:END ===================== */

/* ---- Inbound shipments (shipment_tracker) ---- */
#smdash table.ship{width:100%;border-collapse:collapse;}
#smdash table.ship th{font:600 9px var(--sans);text-transform:uppercase;letter-spacing:.07em;
color:var(--muted);text-align:right;padding:9px 12px;border-bottom:1px solid var(--line);white-space:nowrap;}
#smdash table.ship th:first-child,#smdash table.ship th:nth-child(2){text-align:left;}
#smdash table.ship td{padding:8px 12px;border-bottom:1px solid var(--paper);text-align:right;
font-family:var(--mono);font-size:11.5px;white-space:nowrap;}
#smdash table.ship td:first-child{text-align:left;font-family:var(--sans);font-weight:600;font-size:12px;}
#smdash table.ship td:nth-child(2){text-align:left;color:var(--muted);font-size:11px;}
#smdash table.ship tr.now td{background:rgba(202,162,74,.10);}
#smdash table.ship tr.now td:first-child::after{content:' · this week';font-weight:400;color:var(--muted);font-size:9.5px;}
#smdash table.ship tr.warn td{background:rgba(184,54,47,.06);}
#smdash table.ship tr.warn td:first-child{color:var(--accent);}
#smdash table.ship tr.tot td{font-weight:700;background:#faf7f2;border-top:2px solid var(--ink);}
#smdash table.ship td .qb{display:block;height:4px;border-radius:2px;background:var(--gold);margin-top:4px;}
#smdash .shipnote{padding:10px 16px 14px;font-size:10.5px;color:var(--muted);line-height:1.6;}

/* ---- Loading skeleton -------------------------------------------------------------
   Shown from first paint until the payload arrives. The service sleeps when idle, so a
   cold start can take 30-60s: a blank page for that long reads as "broken". The skeleton
   mirrors the real layout (KPI strip, charts, seller cards) so the page doesn't jump when
   the data lands, and the status line escalates honestly rather than spinning forever. */
#smdash .sk{background:linear-gradient(90deg,#efeae3 25%,#f7f4ef 50%,#efeae3 75%);
background-size:200% 100%;animation:skshim 1.5s ease-in-out infinite;border-radius:6px;}
@keyframes skshim{0%{background-position:200% 0}100%{background-position:-200% 0}}
@media(prefers-reduced-motion:reduce){#smdash .sk{animation:none;background:#efeae3;}}
#smdash .skbar{display:flex;align-items:center;gap:10px;margin:18px 0 4px;
font:500 12px var(--sans);color:var(--muted);}
#smdash .skspin{width:13px;height:13px;border-radius:50%;border:2px solid var(--line);
border-top-color:var(--accent);animation:skspin .8s linear infinite;flex-shrink:0;}
@keyframes skspin{to{transform:rotate(360deg)}}
@media(prefers-reduced-motion:reduce){#smdash .skspin{animation:none;}}
#smdash .skkpis{display:grid;grid-template-columns:repeat(7,1fr);gap:10px;margin:14px 0 4px;}
#smdash .skkpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 13px;}
#smdash .skkpi .a{height:8px;width:62%;margin-bottom:9px;}
#smdash .skkpi .b{height:16px;width:80%;margin-bottom:8px;}
#smdash .skkpi .c{height:7px;width:48%;}
#smdash .skcard{background:var(--card);border:1px solid var(--line);border-radius:14px;
box-shadow:var(--shadow);overflow:hidden;}
#smdash .skcard .h{height:11px;width:150px;margin:16px 18px 14px;}
#smdash .skcard .hr{border-top:1px solid var(--line);}
#smdash .skchart{height:180px;margin:16px 18px;}
#smdash .skrow{display:grid;grid-template-columns:26px 46px 1fr auto;gap:11px;align-items:center;
padding:10px 18px;border-bottom:1px solid var(--paper);}
#smdash .skrow .r{height:9px;} #smdash .skrow .t{height:46px;width:46px;border-radius:8px;}
#smdash .skrow .m .l1{height:10px;width:62%;margin-bottom:6px;}
#smdash .skrow .m .l2{height:8px;width:88%;}
#smdash .skrow .v{height:13px;width:66px;}
@media(max-width:1100px){#smdash .skkpis{grid-template-columns:repeat(4,1fr);}}
@media(max-width:680px){#smdash .skkpis{grid-template-columns:repeat(2,1fr);}}
</style>

<div class="wrap">
  <div class="head">
    <div>
      <div class="brand">STEVE <b>MADDEN</b> · Store Intelligence</div>
      <div class="sub">Sales &amp; Inventory Performance · GCC</div>
    </div>
    <div style="text-align:right;">
      <div class="cursel" id="curSel">
        <button class="curbtn on" data-cur="AED">AED</button>
        <button class="curbtn" data-cur="USD">USD</button>
        <button class="curbtn" data-cur="LOCAL" id="curLocalBtn" style="display:none">Local</button>
      </div>
      <div class="asof" id="asof"></div>
    </div>
  </div>

  <div class="filters">
    <div class="fg"><label>View</label><select id="fView"></select></div>
    <div class="fg"><label>Country</label><select id="fCountry"></select></div>
    <div class="fg"><label id="storeLabel">Store</label><select id="fStore"></select></div>
    <div class="fg"><label>Period</label>
      <div class="periods" id="fPeriod">
        <button class="pill on" data-p="yesterday">Yesterday</button>
        <button class="pill" data-p="wtd">WTD</button>
        <button class="pill" data-p="mtd">MTD</button>
        <button class="pill" data-p="ytd">YTD</button>
      </div>
    </div>
    <div class="fg" id="piPillHost"></div>
  </div>

  <div class="strip" id="strip"></div>
  <div id="body">
  <div id="skel">
    <div class="skbar"><span class="skspin"></span><span id="skmsg">Loading store data…</span></div>
    <div class="skkpis">
      <div class="skkpi"><div class="sk a"></div><div class="sk b"></div><div class="sk c"></div></div>
      <div class="skkpi"><div class="sk a"></div><div class="sk b"></div><div class="sk c"></div></div>
      <div class="skkpi"><div class="sk a"></div><div class="sk b"></div><div class="sk c"></div></div>
      <div class="skkpi"><div class="sk a"></div><div class="sk b"></div><div class="sk c"></div></div>
      <div class="skkpi"><div class="sk a"></div><div class="sk b"></div><div class="sk c"></div></div>
      <div class="skkpi"><div class="sk a"></div><div class="sk b"></div><div class="sk c"></div></div>
      <div class="skkpi"><div class="sk a"></div><div class="sk b"></div><div class="sk c"></div></div>
    </div>
    <div class="grid g2">
      <div class="skcard"><div class="sk h"></div><div class="hr"></div><div class="sk skchart"></div></div>
      <div class="skcard"><div class="sk h"></div><div class="hr"></div><div class="sk skchart"></div></div>
    </div>
    <div class="grid g2">
      <div class="skcard"><div class="sk h"></div><div class="hr"></div>
        <div class="skrow"><div class="sk r"></div><div class="sk t"></div><div class="m"><div class="sk l1"></div><div class="sk l2"></div></div><div class="sk v"></div></div>
        <div class="skrow"><div class="sk r"></div><div class="sk t"></div><div class="m"><div class="sk l1"></div><div class="sk l2"></div></div><div class="sk v"></div></div>
        <div class="skrow"><div class="sk r"></div><div class="sk t"></div><div class="m"><div class="sk l1"></div><div class="sk l2"></div></div><div class="sk v"></div></div>
        <div class="skrow"><div class="sk r"></div><div class="sk t"></div><div class="m"><div class="sk l1"></div><div class="sk l2"></div></div><div class="sk v"></div></div>
      </div>
      <div class="skcard"><div class="sk h"></div><div class="hr"></div>
        <div class="skrow"><div class="sk r"></div><div class="sk t"></div><div class="m"><div class="sk l1"></div><div class="sk l2"></div></div><div class="sk v"></div></div>
        <div class="skrow"><div class="sk r"></div><div class="sk t"></div><div class="m"><div class="sk l1"></div><div class="sk l2"></div></div><div class="sk v"></div></div>
        <div class="skrow"><div class="sk r"></div><div class="sk t"></div><div class="m"><div class="sk l1"></div><div class="sk l2"></div></div><div class="sk v"></div></div>
        <div class="skrow"><div class="sk r"></div><div class="sk t"></div><div class="m"><div class="sk l1"></div><div class="sk l2"></div></div><div class="sk v"></div></div>
      </div>
    </div>
  </div>
  </div>


<!-- PI:START — competitor intelligence drawer -->
<div class="pi-scrim" id="piScrim"></div>
<div class="pi-drawer" id="piDrawer" role="dialog" aria-label="Competitor Intelligence">
  <div class="pi-hd">
    <div>
      <div class="pi-ttl">Competitor Intelligence</div>
      <div class="pi-sub">EDITED · 6th Street + Namshi · listed options</div>
    </div>
    <button class="pi-x" id="piClose" aria-label="Close">&times;</button>
  </div>
  <div class="pi-bar" id="piBar"></div>
  <div class="pi-tabs" id="piTabs"></div>
  <div class="pi-body" id="piBody"></div>
</div>
<!-- PI:END -->

  <div class="foot">
    <span id="footmeta"></span>
    <span>Weeks cover = Inventory Qty ÷ weekly rate of sale · rate follows selected period (WTD→MTD→YTD cascade if no sales) · week starts Monday</span>
  </div>
</div>
</div>

<script>
const DATA_URL = "https://sm-store-intelligence.onrender.com/payload.js";
(function(){
  const $ = (s,r=document)=>r.querySelector(s);
  function showHoverPreview(src, name, key, ev, stats){
    let pop=document.getElementById('hovPrev');
    if(!pop){
      pop=el('div'); pop.id='hovPrev'; pop.className='hovprev';
      pop.innerHTML='<img id="hovPrevImg" src="" alt=""><div class="hovprev-cap" id="hovPrevCap"></div>';
      document.getElementById('smdash').appendChild(pop);
    }
    pop.querySelector('#hovPrevImg').src=src;
    let cap=(name?('<b>'+name+'</b>'):'')+(key?('<span>'+key+'</span>'):'');
    if(stats){
      cap+='<div class="hovstats">'
        + '<div class="hsr"><span>Net Sales</span><span>'+stats.sales+'</span></div>'
        + '<div class="hsr"><span>Net Qty</span><span>'+stats.qty+'</span></div>'
        + '<div class="hsr"><span>Inv Qty</span><span>'+stats.invq+'</span></div>'
        + '<div class="hsr"><span>Inv Value</span><span>'+stats.invv+'</span></div>'
        + '</div>';
    }
    pop.querySelector('#hovPrevCap').innerHTML=cap;
    pop.style.display='block';
    moveHoverPreview(ev);
  }
  function moveHoverPreview(ev){
    const pop=document.getElementById('hovPrev'); if(!pop||pop.style.display!=='block') return;
    const pad=16, w=pop.offsetWidth||260, h=pop.offsetHeight||300;
    let x=ev.clientX+pad, y=ev.clientY+pad;
    if(x+w>window.innerWidth-8)  x=ev.clientX-w-pad;     // flip left if off-screen
    if(y+h>window.innerHeight-8) y=window.innerHeight-h-8;
    if(y<8) y=8;
    pop.style.left=x+'px'; pop.style.top=y+'px';
  }
  function hideHoverPreview(){ const pop=document.getElementById('hovPrev'); if(pop) pop.style.display='none'; }
  let _touchUsed=false;   // once we see a touch, ignore the synthetic mouse/click events that follow
  // Touch: dismiss the preview when tapping anywhere outside a product image.
  // Uses touchend so it runs AFTER the image's own handler, and the image handler
  // stops propagation so an on-image tap never reaches this dismiss handler.
  document.addEventListener('touchend',function(ev){
    const pop=document.getElementById('hovPrev');
    const onImg = ev.target && ev.target.classList && ev.target.classList.contains('ph');
    if(pop && pop.style.display==='block' && !onImg){ hideHoverPreview(); }
  },{passive:true});
  function attachPreview(im, src, name, key, stats){
    // Desktop hover
    im.onmouseenter=(e)=>{ if(_touchUsed) return; showHoverPreview(src,name,key,e,stats); };
    im.onmousemove=(e)=>{ if(_touchUsed) return; moveHoverPreview(e); };
    im.onmouseleave=()=>{ if(_touchUsed) return; hideHoverPreview(); };
    // Touch: a single tap toggles the preview; stop the event so the document
    // dismiss handler doesn't also fire on the same tap.
    im.addEventListener('touchend',function(e){
      _touchUsed=true;
      e.preventDefault();
      e.stopPropagation();
      const pop=document.getElementById('hovPrev');
      if(pop && pop.style.display==='block'){ hideHoverPreview(); }
      else {
        const t=(e.changedTouches&&e.changedTouches[0])||{clientX:window.innerWidth/2,clientY:window.innerHeight/2};
        showHoverPreview(src,name,key,t,stats);
      }
    },{passive:false});
    // Click fallback for non-touch environments only
    im.onclick=(e)=>{ if(_touchUsed) return;
      const pop=document.getElementById('hovPrev');
      if(pop && pop.style.display==='block'){ hideHoverPreview(); }
      else { showHoverPreview(src,name,key,e,stats); } };
  }
  const el = (t,c,h)=>{const e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e;};
  const AED_PER_USD = 3.6725;
  const FX={cur:'AED', rate:1/AED_PER_USD, loaded:true};   // AED base; rate = AED->USD (fixed 1 USD = 3.6725 AED)
  // Per-country local currency. GCC pegs are vs USD (local_per_AED = local_per_USD / AED_per_USD);
  // KWD is NOT a hard USD peg so it's live-fetched. "Local" shows only when a specific non-UAE
  // country is selected — it has no single meaning in the All-Countries combined view.
  const LOCAL_CCY = {
    'United Arab Emirates': {code:'AED', ratePerUSD:AED_PER_USD, live:false},
    'Saudi Arabia':         {code:'SAR', ratePerUSD:3.75,        live:false},
    'Qatar':                 {code:'QAR', ratePerUSD:3.64,        live:false},
    'Oman':                  {code:'OMR', ratePerUSD:0.3845,      live:false},
    'Bahrain':               {code:'BHD', ratePerUSD:0.376,       live:false},
    'Kuwait':                {code:'KWD', ratePerUSD:null,        live:true},
  };
  FX.localCode=null; FX.localRate=null; FX.localLoaded=false; FX.localLive=false;
  const fmtMoney = v => {
    if(v==null) return '—';
    if(FX.cur==='USD'){ return '$ '+Math.round(v*FX.rate).toLocaleString('en-US'); }
    if(FX.cur==='LOCAL' && FX.localRate!=null){ return FX.localCode+' '+Math.round(v*FX.localRate).toLocaleString('en-US'); }
    return 'AED '+Math.round(v).toLocaleString('en-US');
  };
  const fmtNum = v => v==null?'—':Number(v).toLocaleString('en-US');
  const slug = x => x.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  let D, state={view:'Stores',country:'',region:'',store:'__ALL__',period:'yesterday',mixMode:'value',mixDepth:'2',mixOpen:{},topSort:'rev',
                season:'all',fpmd:'all',group:'all',dept:'all',lfl:false,
                snapBasis:'qty',snapOpen:{},budgetBasis:'rebudget',showStores:false,kpiMetric:'asp'};
  let DIAG={failed:0};
  function updateDiag(){
    const bar=$('#diagbar'); if(!bar)return;
    if(DIAG.failed>0){ bar.classList.add('show');
      $('#diagcount').textContent=DIAG.failed; }
  }
  function boot(data){
    skStop();                     // data has landed -> drop the skeleton and kill its timers
    D=data;
    updateAsof();
    $('#footmeta').textContent = `Generated ${D.meta.generated} · ${Object.keys(D.stores).length} stores · ${D.meta.note_wtd}`;
    initFilters();
    bindPeriods();
    bindCurrency();
    piBind();
    render();
  }
  // ---- view routing (Stores uses the existing structures; others use view_blobs) ----
  const VIEW_LIST=['Stores','Ecom','3P','WH','Wholesale'];
  const VIEW_LABEL={Stores:'Stores',Ecom:'Ecom','3P':'3P',WH:'Warehouse',Wholesale:'Wholesale'};
  const VIEW_NOUN ={Stores:'stores',Ecom:'locations','3P':'locations',WH:'DCs',Wholesale:'locations'};
  function isStores(){ return state.view==='Stores'; }
  function vb(){ return (D.view_blobs && D.view_blobs[state.view]) || null; }
  function isSelling(){ return isStores() || !!(vb() && vb().selling); }
  function viewCountries(){
    if(isStores()){
      const a=[]; if(D.country_blobs && D.country_blobs['All Countries']) a.push('All Countries');
      return a.concat(D.filters.countries);
    }
    const b=vb(); if(!b) return [];
    return ['All Countries'].concat(b.filters.countries);
  }
  function viewLocs(country){
    if(isStores()){
      const t=(D.filters.tree||{})[country]||{}; let s=[];
      Object.keys(t).forEach(r=>{ s=s.concat(t[r]); }); return s.sort();
    }
    const b=vb(); if(!b) return []; return ((b.filters.tree||{})[country]||[]).slice().sort();
  }
  function getBlob(){
    const combined=state.store==='__ALL__';
    if(isStores()) return combined ? (D.country_blobs && D.country_blobs[state.country]) : (D.stores && D.stores[state.store]);
    const b=vb(); if(!b) return null;
    return combined ? (b.combined && b.combined[state.country]) : (b.locations && b.locations[state.store]);
  }
  function getRankRows(){
    // {rows:[{store,val,rank,pct}], isQty, money}
    if(isStores()){ const p=state.period;
      return {rows:(D.store_rank && D.store_rank[p] && D.store_rank[p][state.country])||[], isQty:(p==='wtd'), money:true}; }
    const b=vb(); if(!b) return {rows:[],isQty:false,money:false};
    return {rows:(b.rank && b.rank[state.country])||[], isQty:false, money:!!b.selling};
  }
  function initFilters(){
    const fv=$('#fView'); fv.innerHTML='';
    VIEW_LIST.forEach(v=>{ if(v==='Ecom') return;  // Ecom view hidden for now (still generated)
      if(v==='Stores' || (D.view_blobs && D.view_blobs[v])) fv.append(new Option(VIEW_LABEL[v],v)); });
    fv.value=state.view;
    fv.onchange=()=>{
      state.view=fv.value; state.store='__ALL__'; state.showStores=false;
      if(!isStores() && state.period==='yesterday'){ state.period='wtd'; }
      if(state.view==='3P'){ state.period='ytd'; }   // 3P defaults to YTD
      initCountries(); render();
    };
    initCountries();
  }
  function initCountries(){
    const fc=$('#fCountry'); fc.innerHTML='';
    const cs=viewCountries();
    cs.forEach(c=>fc.append(new Option(c,c)));
    if(!cs.includes(state.country)) state.country=cs[0]||'';
    fc.value=state.country;
    updateLocalCurrencyForCountry();
    fc.onchange=()=>{state.country=fc.value;state.region='';state.store='__ALL__';state.showStores=false;updateLocalCurrencyForCountry();fillStores();render();};
    fillStores();
  }
  function fillRegions(){  }
  function fillStores(){
    const fs=$('#fStore'); fs.innerHTML='';
    const noun = isStores()?'Stores':VIEW_LABEL[state.view];
    fs.append(new Option('▸ All '+noun+' (combined)','__ALL__'));
    const stores=viewLocs(state.country);
    stores.forEach(s=>fs.append(new Option(s,s)));
    if(state.store!=='__ALL__' && !stores.includes(state.store)) state.store='__ALL__';
    fs.value=state.store;
    const lbl=$('#storeLabel'); if(lbl) lbl.textContent = isStores()?'Store':'Location';
    fs.onchange=()=>{state.store=fs.value;render();};
  }
  function bindPeriods(){
    $('#fPeriod').querySelectorAll('.pill').forEach(b=>{
      b.onclick=()=>{state.period=b.dataset.p;
        $('#fPeriod').querySelectorAll('.pill').forEach(x=>x.classList.remove('on'));
        b.classList.add('on'); render();};
    });
  }
  function bindCurrency(){
    const sel=$('#curSel'); if(!sel) return;
    sel.querySelectorAll('.curbtn').forEach(b=>{
      b.onclick=()=>{
        FX.cur=b.dataset.cur;
        sel.querySelectorAll('.curbtn').forEach(x=>x.classList.remove('on'));
        b.classList.add('on');
        if(FX.cur==='LOCAL' && FX.localLive && !FX.localLoaded){ fetchLocalRate(); }
        else { render(); updateAsof(); }
      };
    });
  }
  function fetchRate(){
    const eps=[
      ['https://api.frankfurter.app/latest?from=AED&to=AUD', d=>d&&d.rates&&d.rates.AUD],
      ['https://open.er-api.com/v6/latest/AED', d=>d&&d.rates&&d.rates.AUD],
      ['https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/aed.json', d=>d&&d.aed&&d.aed.aud]
    ];
    let i=0;
    const tryNext=()=>{
      if(i>=eps.length){ FX.loaded=true; render(); updateAsof(); return; }
      const [url,pick]=eps[i++];
      fetch(url).then(r=>r.json()).then(d=>{
        const rt=pick(d);
        if(rt && rt>0){ FX.rate=rt; FX.loaded=true; render(); updateAsof(); }
        else tryNext();
      }).catch(tryNext);
    };
    tryNext();
  }
  // Resolve/refresh the Local button for the selected country. Hides it (and reverts to AED
  // if active) when no country is selected or the local currency IS AED (UAE).
  function updateLocalCurrencyForCountry(){
    const btn=document.getElementById('curLocalBtn'); if(!btn) return;
    const cfg = LOCAL_CCY[state.country];
    if(!cfg || cfg.code==='AED'){
      btn.style.display='none';
      if(FX.cur==='LOCAL'){
        FX.cur='AED';
        const sel=$('#curSel');
        if(sel){ sel.querySelectorAll('.curbtn').forEach(x=>x.classList.remove('on'));
          const aedBtn=sel.querySelector('[data-cur="AED"]'); if(aedBtn) aedBtn.classList.add('on'); }
      }
      return;
    }
    btn.style.display='';
    btn.textContent=cfg.code;
    const wasLocal=(FX.cur==='LOCAL');
    const codeChanged=(FX.localCode!==cfg.code);
    FX.localCode=cfg.code; FX.localLive=cfg.live;
    if(cfg.live){
      if(codeChanged){ FX.localRate=null; FX.localLoaded=false; }
      if(wasLocal && !FX.localLoaded){ fetchLocalRate(); }
    } else {
      FX.localRate = cfg.ratePerUSD / AED_PER_USD;   // AED -> local, via USD
      FX.localLoaded = true;
      if(wasLocal){ render(); updateAsof(); }
    }
  }
  function fetchLocalRate(){
    const code=FX.localCode; if(!code) return;
    const eps=[
      ['https://api.frankfurter.app/latest?from=AED&to='+code, d=>d&&d.rates&&d.rates[code]],
      ['https://open.er-api.com/v6/latest/AED', d=>d&&d.rates&&d.rates[code]],
      ['https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/aed.json', d=>d&&d.aed&&d.aed[code.toLowerCase()]]
    ];
    let i=0;
    const tryNext=()=>{
      if(i>=eps.length){ FX.localLoaded=true; render(); updateAsof(); return; }
      const [url,pick]=eps[i++];
      fetch(url).then(r=>r.json()).then(d=>{
        const rt=pick(d);
        if(rt && rt>0 && FX.localCode===code){ FX.localRate=rt; FX.localLoaded=true; render(); updateAsof(); }
        else if(FX.localCode===code) tryNext();
      }).catch(()=>{ if(FX.localCode===code) tryNext(); });
    };
    tryNext();
  }
  function updateAsof(){
    if(!D||!D.meta) return;
    let line=`As of <b>${D.meta.as_of}</b><br>Day ${D.meta.days_elapsed_week}/7 of week · Mon-start`;
    if(FX.cur==='USD'){ line+=`<div class="curnote">1 USD = 3.6725 AED</div>`; }
    else if(FX.cur==='LOCAL' && FX.localCode){ line+=`<div class="curnote">1 AED = ${(FX.localRate||0).toFixed(4)} ${FX.localCode}${FX.localLive&&!FX.localLoaded?' · loading…':''}</div>`; }
    $('#asof').innerHTML=line;
  }
  const periodLabel={yesterday:'Yesterday',wtd:'Week-to-date',mtd:'Month-to-date',ytd:'Year-to-date'};
  function wcClass(w){ if(w==null)return 'na'; if(w<4)return 'lo'; if(w<=12)return 'hi'; return 'xx'; }
  function pv(it){ return it.p[state.period]||[null,null,null,null,'none']; }
  function wcDisplay(it){
    const [,,,wc,stt]=pv(it);
    if(wc!=null) return {cls:wcClass(wc), txt:(wc>=100?Math.round(wc):wc)+'w'};
    if(stt==='dead') return {cls:'xx', txt:'Dead stock'};
    return {cls:'na', txt:'No sales'};
  }
  function applyFilters(items){
    return items.filter(it=>{
      if(state.season==='current' && !it.cur_season) return false;
      if(state.group!=='all' && it.group!==state.group) return false;
      if(state.dept!=='all' && it.dept!==state.dept) return false;
      if(state.fpmd!=='all' && it.fpmd!==state.fpmd) return false;
      return true;
    });
  }
  function rankTop(items){
    const f=applyFilters(items);
    const amt=it=>(pv(it)[0]??pv(it)[1]??0);
    const qty=it=>(pv(it)[1]||0);
    const metric=(state.topSort==='qty')?qty:amt;   // toggle: revenue vs qty
    const sold=it=>(pv(it)[1]||0)>0;
    const coreSold = f.filter(it=>!it.xcat && sold(it)).sort((a,b)=>metric(b)-metric(a));
    const xcatSold = f.filter(it=> it.xcat && sold(it)).sort((a,b)=>metric(b)-metric(a));
    const coreZero = f.filter(it=>!it.xcat && !sold(it)).sort((a,b)=>metric(b)-metric(a));
    return coreSold.concat(xcatSold).concat(coreZero).slice(0,10);
  }
  function rankBottom(items){
    const pool=applyFilters(items).filter(it=>!it.recent && !it.xcat);
    const sold=pool.filter(it=>(pv(it)[1]||0)>0).sort((a,b)=>((pv(a)[0]??pv(a)[1]??0)-(pv(b)[0]??pv(b)[1]??0)));
    const zero=pool.filter(it=>(pv(it)[1]||0)<=0).sort((a,b)=>((b.stock_cost||0)-(a.stock_cost||0)));
    return (zero.length>10 ? zero : zero.concat(sold)).slice(0,10);
  }
  function sellerRow(it,i){
    const [amt,qty,asp]=pv(it);
    const row=el('div','seller');
    row.append(el('div','rank',(i+1)));
    if(it.img){ const im=el('img','ph'); im.src=it.img; im.loading='lazy';
      attachPreview(im, it.img, (it.desc||it.key), it.key, {sales:(amt==null?'—':fmtMoney(amt)),qty:fmtNum(qty),invq:fmtNum(it.inv_qty),invv:fmtMoney(it.stock_cost)});
      im.onerror=()=>{const x=el('div','phx failed','STEVE<br>MADDEN');x.title='Image link failed locally; loads on Shopify.';im.replaceWith(x);DIAG.failed++;updateDiag();}; row.append(im); }
    else { row.append(el('div','phx','STEVE<br>MADDEN')); }
    const mid=el('div');
    const fp=it.fpmd?` <span class="badge ${it.fpmd.toLowerCase()}">${it.fpmd}</span>`:'';
    mid.append(el('div','sname',(it.desc||it.key)));
    const meta=el('div','smeta');
    const wc=wcDisplay(it);
    meta.innerHTML=`ASP <b>${asp==null?'—':Math.round(asp)}</b>`+
      ` · Inv <b>${fmtNum(it.inv_qty)}</b>`+
      ` · GM <b>${it.gm==null?'—':it.gm+'%'}</b>${fp}`+
      ` · <span class="wc ${wc.cls}">${wc.txt}</span>`;
    mid.append(meta); row.append(mid);
    const val=el('div','sval');
    val.innerHTML=`<div class="amt">${amt==null?fmtNum(qty)+' u':fmtMoney(amt)}</div>`+
      `<div class="q">${fmtNum(qty)} units</div>`;
    row.append(val);
    return row;
  }
  function sellerCard(title,cls,list){
    const c=el('div','card');
    if(cls==='top'){
      const h=el('h3');
      h.innerHTML=`<span><span class="dot ${cls}"></span>${title}</span>`;
      const seg=el('div','seg');
      [['rev','Revenue'],['qty','Qty']].forEach(([k,lab])=>{
        const b=el('button',(state.topSort||'rev')===k?'on':'',lab);
        b.onclick=()=>{state.topSort=k;render();}; seg.append(b);
      });
      h.append(seg); c.append(h);
    } else {
      c.append(el('h3',null,`<span><span class="dot ${cls}"></span>${title}</span><span class="tag">lowest · excl. last-30d arrivals</span>`));
    }
    if(!list||!list.length){c.append(el('div','empty','No items match the current filters.'));return c;}
    list.forEach((r,i)=>c.append(sellerRow(r,i)));
    return c;
  }
  function sellerFilterBar(st){
    const bar=el('div','sfilters');
    const groups=[...new Set((st.items||[]).filter(i=>!i.xcat).map(i=>i.group).filter(Boolean))].sort();
    const depts = (state.group==='all') ? []
      : [...new Set((st.items||[]).filter(i=>!i.xcat && i.group===state.group).map(i=>i.dept).filter(Boolean))].sort();
    function seg(label,opts,cur,onpick){
      const g=el('div','sfg');
      g.append(el('span','sflabel',label));
      const row=el('div','seg');
      opts.forEach(([v,lab])=>{ const b=el('button',cur===v?'on':'',lab); b.onclick=()=>onpick(v); row.append(b); });
      g.append(row); return g;
    }
    bar.append(seg('Season',[['all','Overall'],['current','Spring 2026']],state.season,v=>{state.season=v;render();}));
    bar.append(seg('Margin',[['all','All'],['FP','FP'],['MD','MD']],state.fpmd,v=>{state.fpmd=v;render();}));
    bar.append(seg('Group',[['all','All']].concat(groups.map(x=>[x,x])),state.group,v=>{state.group=v;state.dept='all';render();}));
    if(state.group==='all'){
      bar.append(seg('Dept',[['all','All']],'all',()=>{}));
    } else if(depts.length>1){
      bar.append(seg('Dept',[['all','All']].concat(depts.map(x=>[x,x])),state.dept,v=>{state.dept=v;render();}));
    } else {
      bar.append(seg('Dept',[['all','All']],'all',()=>{}));
    }
    return bar;
  }
  function mixCard(st, selling){
    selling=(selling!==false);
    const c=el('div','card');
    const head=el('h3');
    head.innerHTML=`<span>${selling?'Category Performance':'Category Stock Mix'}</span>`;
    const ctrl=el('div',null,'');ctrl.style.display='flex';ctrl.style.gap='10px';
    const depth=el('div','seg');
    [['2','+Dept'],['3','+Class']].forEach(([k,lab])=>{
      const b=el('button',state.mixDepth===k?'on':'',lab);
      b.onclick=()=>{state.mixDepth=k;render();}; depth.append(b);
    });
    ctrl.append(depth); head.append(ctrl); c.append(head);
    const tree=st.cat_pivot||[];
    const maxDepth=parseInt(state.mixDepth||'2');
    const P=state.period||'mtd';                              // selected period drives the sales columns
    const qOf=n=>{const v=n.qty&&n.qty[P]; return v==null?0:v;};      // period net sales qty
    const rOf=n=>{const v=n.rev&&n.rev[P]; return v==null?null:v;};   // period net sales amt (null => N/A, e.g. WTD)
    // grand totals across top-level groups (denominators for the mix % columns)
    const gQty   = tree.reduce((a,n)=>a+qOf(n),0)||1;          // net sales qty (period)
    const gRev   = tree.reduce((a,n)=>a+(rOf(n)||0),0)||1;     // net sales amt (period)
    const gSqty  = tree.reduce((a,n)=>a+(n.sqty||0),0)||1;     // inventory qty (snapshot)
    const gScost = tree.reduce((a,n)=>a+(n.scost||0),0)||1;    // inventory value (snapshot)
    const tbl=el('table','mixwide');
    const salesCols = selling
      ? `<th class="num">Net Sales Qty</th><th class="num">Qty Mix %</th><th class="num">Net Sales Amt</th><th class="num">Sales Mix %</th><th class="num">Avg Markdown</th><th class="num">GP %</th>` : '';
    tbl.innerHTML=`<thead><tr>
      <th>Category</th>${salesCols}
      <th class="num">Inventory Qty</th><th class="num">Inv Qty Mix %</th>
      <th class="num">Inventory Value</th><th class="num">Stock Mix %</th>
    </tr></thead>`;
    const tb=el('tbody');
    const pc=(v,tot)=> (tot? (100*v/tot):0).toFixed(1)+'%';
    function addRow(node, depth, path){
      const tr=el('tr'); tr.className='lvl'+depth;
      const hasKids=node.children&&node.children.length&&depth<maxDepth;
      const open=state.mixOpen[path]!==undefined?state.mixOpen[path]:(depth<2);
      const name=el('td',null,'');
      name.style.paddingLeft=(10+(depth-1)*16)+'px';
      name.innerHTML=(hasKids?`<span class="caret">${open?'▾':'▸'}</span>`:`<span class="caret no"></span>`)+
        `<span class="cn${depth===1?' g':''}">${node.name}</span>`;
      if(hasKids){ name.style.cursor='pointer'; name.onclick=()=>{state.mixOpen[path]=!open;render();}; }
      tr.append(name);
      const q=qOf(node), r=rOf(node);
      const revTxt  = r==null ? '—' : fmtMoney(r);
      const smixTxt = r==null ? '—' : pc(r,gRev);
      const cells=[];
      const _ngp=(node.gp&&node.gp[P]!=null)?node.gp[P]+'%':'—';
      const _nmd=(node.md&&node.md[P]!=null)?node.md[P]+'%':'—';
      if(selling){ cells.push([fmtNum(q),'num'],[pc(q,gQty),'num pct'],[revTxt,'num'],[smixTxt,'num pct'],[_nmd,'num'],[_ngp,'num']); }
      cells.push([fmtNum(node.sqty||0),'num'],[pc(node.sqty||0,gSqty),'num pct'],
                 [fmtMoney(node.scost||0),'num'],[pc(node.scost||0,gScost),'num pct']);
      cells.forEach(([txt,cls])=>{ const td=el('td',cls,txt); tr.append(td); });
      tb.append(tr);
      if(hasKids&&open){
        node.children.forEach(ch=>addRow(ch,depth+1,path+'>'+ch.name));
      }
    }
    tree.forEach(g=>addRow(g,1,g.name));
    tbl.append(tb);
    const scroll=el('div','mixscroll'); scroll.append(tbl); c.append(scroll);
    return c;
  }
  function transitCard(st){
    const c=el('div','card');
    c.append(el('h3',null,`<span>Store to Store In-Transit</span><span class="tag">to this store · by category</span>`));
    const list=st.in_transit||[];
    if(!list.length){c.append(el('div','empty','No stock currently in transit.'));return c;}
    const max=Math.max(...list.map(x=>x.qty));
    list.slice(0,12).forEach(r=>{
      const row=el('div','it');
      row.append(el('div','itg',r.group));
      row.append(el('div','itd',r.dept));
      const bar=el('div','itbar'); bar.append(el('i',null,'')); bar.firstChild.style.width=(100*r.qty/max)+'%';
      row.append(bar);
      row.append(el('div','itq',fmtNum(r.qty)));
      c.append(row);
    });
    return c;
  }
  function countryRankCard(){
    const c=el('div','country');
    const ranks=(D.country_rank||[]).slice().sort((a,b)=>a.rank-b.rank);
    const head=el('h3'); head.style.cssText='display:flex;align-items:center;justify-content:space-between;gap:10px;';
    head.innerHTML=`<span>Countries Ranked · All Countries · ${periodLabel[state.period]}</span>`;
    const btn=el('button',null,'Show stores');
    btn.style.cssText='font:600 9px var(--sans);text-transform:uppercase;letter-spacing:.06em;cursor:pointer;padding:5px 11px;border-radius:7px;border:1px solid rgba(255,255,255,.3);background:transparent;color:#fff;white-space:nowrap;';
    btn.onclick=()=>{ state.showStores=true; render(); };
    head.append(btn); c.append(head);
    const hero=el('div','chero');
    const totV=ranks.reduce((a,r)=>a+(r.rev||0),0);
    hero.innerHTML=`<span class="big">${ranks.length}</span>`+
      `<span class="lbl">countries<br>total revenue ${fmtMoney(totV)}</span>`;
    c.append(hero);
    if(!ranks.length){return c;}
    const max=Math.max(...ranks.map(x=>x.rev),1);
    ranks.forEach(r=>{
      const row=el('div','crow');
      row.innerHTML=`<span class="cn">${r.rank}. ${r.country}</span>`+
        `<span class="cbar"><i style="width:${100*r.rev/max}%"></i></span>`+
        `<span class="cp">${r.pct}% · ${fmtMoney(r.rev)}</span>`;
      c.append(row);
    });
    return c;
  }
  function storesRankCard(st){
    const c=el('div','country');
    const period=state.period, isQty=false;   // WTD revenue now available
    const ranks=(D.store_rank&&D.store_rank[period]&&D.store_rank[period][st.country])||[];
    const fmtV=v=>isQty?fmtNum(v):fmtMoney(v);
    const head=el('h3'); head.style.cssText='display:flex;align-items:center;justify-content:space-between;gap:10px;';
    head.innerHTML=`<span>Stores Ranked · ${st.country} · ${periodLabel[period]}</span>`;
    if(state.country==='All Countries'){
      const btn=el('button',null,'Hide stores');
      btn.style.cssText='font:600 9px var(--sans);text-transform:uppercase;letter-spacing:.06em;cursor:pointer;padding:5px 11px;border-radius:7px;border:1px solid rgba(255,255,255,.3);background:transparent;color:#fff;white-space:nowrap;';
      btn.onclick=()=>{ state.showStores=false; render(); };
      head.append(btn);
    }
    c.append(head);
    const hero=el('div','chero');
    const totV=ranks.reduce((a,r)=>a+(r.val||0),0);
    hero.innerHTML=`<span class="big">${ranks.length}</span>`+
      `<span class="lbl">stores in ${st.country}<br>total ${isQty?'units':'revenue'} ${fmtV(totV)}</span>`;
    c.append(hero);
    if(!ranks.length){return c;}
    const max=Math.max(...ranks.map(x=>x.val),1);
    ranks.forEach(r=>{
      const short=r.store.replace(/^SM /,'').replace(/^ECOMM - /,'EC ');
      const row=el('div','crow');
      row.innerHTML=`<span class="cn">${r.rank}. ${short}</span>`+
        `<span class="cbar"><i style="width:${100*r.val/max}%"></i></span>`+
        `<span class="cp">${r.pct}% · ${fmtV(r.val)}</span>`;
      c.append(row);
    });
    return c;
  }
  function rankCard(st){
    const c=el('div','country');
    const period=state.period, isQty=false;   // WTD revenue now available
    const ranks=(D.store_rank&&D.store_rank[period]&&D.store_rank[period][st.country])||[];
    const mine=ranks.find(x=>x.store===state.store);
    const unit = isQty?'units':'AED';
    const fmtV = v => isQty?fmtNum(v):fmtMoney(v);
    c.append(el('h3',null,`Store Revenue Rank · ${st.country} · ${periodLabel[period]}`));
    const hero=el('div','chero');
    if(mine){
      hero.innerHTML=`<span class="big">#${mine.rank}</span>`+
        `<span class="lbl">of ${ranks.length} ${st.country} stores<br>${mine.pct}% of country ${isQty?'units':'revenue'}</span>`+
        `<span class="rkbadge">${fmtV(mine.val)}${isQty?' units':''}</span>`;
    } else {
      hero.innerHTML=`<span class="lbl">No ranking data for this store/period.</span>`;
    }
    c.append(hero);
    if(!ranks.length){return c;}
    const max=Math.max(...ranks.map(x=>x.val),1);
    let show=ranks.slice(0,10);
    if(mine && mine.rank>10){ show=show.concat([{__sep:true}, mine]); }
    show.forEach(r=>{
      if(r.__sep){ const sep=el('div','crow'); sep.style.opacity='.4';
        sep.innerHTML=`<span class="cn">⋯</span>`; c.append(sep); return; }
      const me=r.store===state.store;
      const row=el('div','crow'+(me?' me':''));
      const short=r.store.replace(/^SM /,'').replace(/^ECOMM - /,'EC ');
      row.innerHTML=`<span class="cn">${r.rank}. ${short}</span>`+
        `<span class="cbar"><i style="width:${100*r.val/max}%"></i></span>`+
        `<span class="cp">${r.pct}% · ${fmtV(r.val)}</span>`;
      c.append(row);
    });
    return c;
  }
  function kpiStrip(st){
    const wrap=el('div','kpis');
    const useLfl = state.lfl && st.kpi_lfl;
    const k=(useLfl?st.kpi_lfl:st.kpi)&&(useLfl?st.kpi_lfl:st.kpi)[state.period];
    const bb=state.budgetBasis||'rebudget';                    // 'rebudget' | 'original'
    const budKey=`bud_${bb}_sales`, budPctKey=`bud_${bb}_sales_pct`, budMgnKey=`bud_${bb}_margin`;
    const defs=[
      ['Sales Amount','sales',v=>fmtMoney(v),false],
      ['Sales Qty','qty',v=>fmtNum(v),false],
      ['GP %','gp',v=>v==null?'—':v+'%',false],
      ['FP Sales','fullprice',v=>v==null?'—':v+'%',false],
      ['Footfall','footfall',v=>fmtNum(v),false],
      ['Conversion','conv',v=>v==null?'—':v+'%',false],
      ['UPT','upt',v=>v==null?'—':v,false],
      ['AOV','aov',v=>fmtMoney(v),false],
      ['ASP','asp',v=>fmtMoney(v),false],
    ];
    if(!k||!k.ty){
      defs.forEach(([lab])=>{const c=el('div','kpi');c.innerHTML=`<div class="klabel">${lab}</div><div class="kval">—</div><div class="kly">No KPI data</div>`;wrap.append(c);});
      ['Avg Markdown','Productivity','WH Stock','Ecom Sales'].forEach(lab=>{const c=el('div','kpi');c.innerHTML=`<div class="klabel">${lab}</div><div class="kval">—</div><div class="kly"><span class="lyval">—</span></div>`;wrap.append(c);});
      return wrap;
    }
    defs.forEach(([lab,key,fmt,inv])=>{
      const ty=k.ty?k.ty[key]:null, ly=k.ly?k.ly[key]:null;
      let delta='',dcls='flat';
      const noLY = (key===budPctKey);
      if(!noLY && ty!=null&&ly!=null&&ly!=0){
        const pct=((ty-ly)/Math.abs(ly))*100;
        const good = inv? pct<0 : pct>0;
        dcls = Math.abs(pct)<0.5?'flat':(good?'up':'down');
        delta=`<span class="delta ${dcls}">${pct>0?'+':''}${pct.toFixed(1)}%</span>`;
      }
      const c=el('div','kpi');
      let extra='';
      if(key==='fullprice' && k.ty && k.ty.fp_units!=null && k.ty.tot_units!=null){
        const up=(k.ty.fp_unit_pct!=null)?` · ${k.ty.fp_unit_pct}% units`:'';
        extra=`<div class="kfp">${fmtNum(k.ty.fp_units)} / ${fmtNum(k.ty.tot_units)} units FP${up}</div>`;
      }
      let lyLine = `<div class="kly">${delta} <span class="lyval">LY ${ly==null?'—':fmt(ly)}</span></div>`;
      if(key==='sales' && k.ty){
        const bt=k.ty[budKey], bp=k.ty[budPctKey];
        if(bt!=null && bp!=null){
          const bcls=bp>=100?'up':'down';
          extra=`<div class="kfp ${bcls}">${bp>=100?'▲':'▼'} ${bp}% of ${bb==='rebudget'?'re-budget':'orig budget'} · target ${fmtMoney(bt)}</div>`;
        }
      }
      // Operational KPI target line (from the budget tab matching the toggle). Only tiles that
      // don't already carry an extra line (Sales / Budget / FP) get one; a missing target (e.g.
      // FP Sales, or GP% before it's populated) simply renders nothing.
      // GP% achievement is computed on GP VALUE, not rate-vs-rate. GP value = GP% × sales, so
      // target GP value = target_gp% × sales target, and achievement = actual GP value / target
      // GP value. The tile shows the target as BOTH a value and a %. (A rate/rate ratio ignores
      // the sales the margin was earned on, which is why it was misleading.)
      if(!extra && key==='gp' && k.ty){
        const _tgpPct = k.ty[`target_gp_${bb}`];               // target GP% (rate)
        const _tsales = k.ty[budKey];                          // sales target (value, same tab)
        const _agp    = k.ty['gp'];                            // actual GP%
        const _asales = k.ty['sales'];                         // actual sales
        if(_tgpPct!=null && _tsales!=null){
          const _tgpVal = _tgpPct/100*_tsales;                 // target GP VALUE
          const _agpVal = (_agp!=null && _asales!=null) ? _agp/100*_asales : null;
          const _pct = (_agpVal!=null && _tgpVal) ? (_agpVal/_tgpVal*100) : null;
          const _tc=(_pct!=null&&_pct>=100)?'up':'down';
          const _ar=(_pct!=null)?((_pct>=100?'▲':'▼')+' '):'';
          extra=`<div class="kfp ${_pct!=null?_tc:'flat'}">${_ar}target ${fmtMoney(_tgpVal)} · ${_tgpPct}%${_pct!=null?` · ${_pct.toFixed(1)}%`:''}</div>`;
        }
      }
      const _TGT_FMT = {qty:v=>fmtNum(v), footfall:v=>fmtNum(v), conv:v=>v+'%', upt:v=>v,
                        aov:v=>fmtMoney(v), asp:v=>fmtMoney(v)};   // gp handled above (value basis)
      if(!extra && _TGT_FMT[key] && k.ty){
        const _tv=k.ty[`target_${key}_${bb}`], _tp=k.ty[`target_${key}_${bb}_pct`];
        if(_tv!=null){
          const _tc=(_tp!=null&&_tp>=100)?'up':'down';
          const _ar=(_tp!=null)?((_tp>=100?'▲':'▼')+' '):'';
          extra=`<div class="kfp ${_tp!=null?_tc:'flat'}">${_ar}target ${_TGT_FMT[key](_tv)}${_tp!=null?` · ${_tp}%`:''}</div>`;
        }
      }
      c.innerHTML=`<div class="klabel">${lab}</div><div class="kval">${fmt(ty)}</div>`+extra+lyLine;
      wrap.append(c);
    });
    // --- Avg Markdown: from the KPI file's Markdown% column (current scope + period) ---
    {
      const md = (k && k.ty && k.ty.md!=null) ? k.ty.md : null;
      const c=el('div','kpi');
      c.innerHTML=`<div class="klabel">Avg Markdown</div><div class="kval">${md!=null?md+'%':'—'}</div>`+
        `<div class="kly"><span class="lyval">avg discount · ${periodLabel[state.period]}</span></div>`;
      wrap.append(c);
    }
    // --- Productivity: annualized store sales per sq ft, in USD (always USD, ignores the currency toggle) ---
    {
      const pScope = (state.store!=='__ALL__') ? state.store : state.country;
      const pv = (D.productivity_kpi && D.productivity_kpi[pScope]) ? D.productivity_kpi[pScope][state.period] : null;
      const c=el('div','kpi');
      c.innerHTML=`<div class="klabel">Productivity</div><div class="kval">${pv!=null?'$ '+Number(pv).toLocaleString('en-US'):'—'}</div>`+
        `<div class="kly"><span class="lyval">USD / sqft / yr · ${periodLabel[state.period]}</span></div>`;
      wrap.append(c);
    }
    // --- WH Stock: warehouse/DC merchandise qty for the current scope (current snapshot) ---
    // Country / All Countries: that country's (or all) merchandise WH qty. Single store:
    // that store's country DC qty, restricted to the styles the store holds.
    {
      const whScope = (state.store!=='__ALL__') ? state.store : state.country;
      const _wh = (D.wh_kpi && D.wh_kpi[whScope]!=null) ? D.wh_kpi[whScope] : null;
      // wh_kpi entries are now {qty, value}. Fall back to treating a bare number as qty, so a
      // stale payload served mid-deploy still renders (value simply shows as unavailable then).
      const wqv = (_wh && typeof _wh==='object') ? _wh : (_wh!=null ? {qty:_wh, value:null} : null);
      const sub = (state.store!=='__ALL__') ? "country DC · this store's styles" : 'country DC · merchandise';
      const c=el('div','kpi');
      // Value is the headline (money basis, matches store stock value); units sit underneath.
      const headline = (wqv && wqv.value!=null) ? fmtMoney(wqv.value)
                       : (wqv && wqv.qty!=null) ? fmtNum(wqv.qty) : '—';
      const unitsLine = (wqv && wqv.qty!=null) ? `${fmtNum(wqv.qty)} units · ${sub}` : sub;
      c.innerHTML=`<div class="klabel">WH Stock</div><div class="kval">${headline}</div>`+
        `<div class="kly"><span class="lyval">${unitsLine}</span></div>`;
      wrap.append(c);
    }
    // --- ECOM Sales + Share of Business (Stores view) ---
    // Populated on combined / per-country views (ecom isn't attributable to one physical
    // store, so a single-store selection shows "—"). Reads the separate ecom_kpi feed and
    // responds to the period selector; Share = ecom / (stores + ecom) for the same period.
    {
      const combinedView = state.store==='__ALL__';
      const e = (combinedView && D.ecom_kpi && D.ecom_kpi[state.country]) ? (D.ecom_kpi[state.country][state.period]||{}) : {};
      const ety=e.ty||null, ely=e.ly||null;
      const sTy=(st.kpi&&st.kpi[state.period]&&st.kpi[state.period].ty)?st.kpi[state.period].ty.sales:null;
      const sLy=(st.kpi&&st.kpi[state.period]&&st.kpi[state.period].ly)?st.kpi[state.period].ly.sales:null;
      // Ecom Sales (Share of Business folded in as a sub-line)
      { const c=el('div','kpi'); let delta='';
        if(ety&&ely&&ely.sales){ const p=((ety.sales-ely.sales)/Math.abs(ely.sales))*100;
          const cls=Math.abs(p)<0.5?'flat':(p>0?'up':'down'); delta=`<span class="delta ${cls}">${p>0?'+':''}${p.toFixed(1)}%</span>`; }
        const shTy=(ety&&ety.sales!=null&&sTy!=null&&(sTy+ety.sales)>0)?100*ety.sales/(sTy+ety.sales):null;
        const shLine = shTy!=null ? `<div class="kfp">${shTy.toFixed(1)}% share of business</div>` : '';
        c.innerHTML=`<div class="klabel">Ecom Sales</div><div class="kval">${ety&&ety.sales!=null?fmtMoney(ety.sales):'—'}</div>`+
          shLine +
          `<div class="kly">${delta} <span class="lyval">LY ${ely&&ely.sales!=null?fmtMoney(ely.sales):'—'}</span></div>`;
        wrap.append(c); }
    }
    return wrap;
  }
  function transitItemsCard(st){
    const c=el('div','card');
    c.append(el('h3',null,`<span>Store to Store In-Transit · Top 10 Items</span><span class="tag">to this store · by qty</span>`));
    const list=st.transit_items||[];
    if(!list.length){c.append(el('div','empty','No stock currently in transit.'));return c;}
    list.forEach((r,i)=>{
      const row=el('div','titem');
      row.append(el('div','rank',i+1));
      if(r.img){const im=el('img','ph');im.src=r.img;im.loading='lazy';
        attachPreview(im, r.img, (r.desc||r.key), r.key, {sales:'—',qty:'—',invq:fmtNum(r.inv_qty),invv:(r.stock_cost!=null?fmtMoney(r.stock_cost):'—')});
        im.onerror=()=>{const x=el('div','phx failed','STEVE<br>MADDEN');im.replaceWith(x);DIAG.failed++;updateDiag();};row.append(im);}
      else row.append(el('div','phx','STEVE<br>MADDEN'));
      const mid=el('div');
      mid.append(el('div','sname',r.desc||r.key));
      mid.append(el('div','smeta',`${r.group||''} · ${r.dept||''}`));
      row.append(mid);
      row.append(el('div','tq',`${fmtNum(r.qty)}<span>in transit</span>`));
      c.append(row);
    });
    return c;
  }
  function snapSection(st){
    const snap=st.inv_snapshot;
    const wrap=el('div');
    if(!snap || !snap.total_cc){ return wrap; }
    const isV=state.snapBasis==='value';
    const fmtV=v=>isV?fmtMoney(v):fmtNum(v);
    const hdr=el('div','snaphdr');
    hdr.append(el('h2',null,'Inventory Snapshot'));
    const basis=el('div',null,''); basis.style.cssText='display:flex;gap:6px;margin-left:auto;';
    ['qty','value'].forEach(k=>{
      const b=el('button','basisbtn'+(state.snapBasis===k?' on':''), k==='qty'?'Units':'Value');
      b.onclick=()=>{state.snapBasis=k;render();}; basis.append(b);
    });
    hdr.append(basis); wrap.append(hdr);
    wrap.append(el('div','snapsub',
      `${fmtNum(snap.total_cc)} active color codes · ${fmtNum(snap.total_units)} units · ${fmtMoney(snap.total_value)} stock value`));
    const grid=el('div','grid g2');
    const c1=el('div','card');
    c1.append(el('h3',null,`<span>FP / MD Stock Mix</span><span class="tag">by ${isV?'value':'units'}</span>`));
    const b1=el('div','snapbody');
    const fq=isV?'fp_v':'fp_q', mq=isV?'md_v':'md_q', tq=isV?'tot_v':'tot_q';
    (snap.fpmd||[]).filter(r=>r[tq]>0).slice(0,8).forEach(r=>{
      const fpp=r[tq]?Math.round(100*r[fq]/r[tq]):0, mdp=100-fpp;
      const row=el('div','snaprow');
      row.innerHTML=`<div class="lab"><span class="nm">${r.cat}</span><span class="v">${fmtV(r[tq])} · ${fpp}% FP</span></div>`+
        `<div class="splitbar"><div class="fp" style="width:${fpp}%"></div><div class="md" style="width:${mdp}%"></div></div>`;
      b1.append(row);
    });
    const tf=(snap.totals&&snap.totals.fpmd)||null;
    if(tf){
      const tfpp=tf[tq]?Math.round(100*tf[fq]/tf[tq]):0;
      const tr=el('div','snaptot');
      tr.innerHTML=`<span>Total</span><span class="v">${fmtV(tf[tq])} · ${tfpp}% FP / ${100-tfpp}% MD</span>`;
      b1.append(tr);
    }
    const lg=el('div','snaplegend');
    lg.innerHTML=`<span><span class="sw9" style="background:var(--accent2)"></span>Full price</span>`+
      `<span><span class="sw9" style="background:#d8804f"></span>Markdown</span>`;
    b1.append(lg); c1.append(b1); grid.append(c1);
    const c2=el('div','card');
    c2.append(el('h3',null,`<span>Season Mix</span><span class="tag">by ${isV?'value':'units'}</span>`));
    const b2=el('div','snapbody');
    const sk=isV?'v':'q';
    const smax=Math.max(...(snap.season||[]).map(x=>x[sk]),1);
    const scol={'Spring 2026':'#5a7d74','Summer 2026':'#c9a96a','Autumn 2025':'#d8804f','Winter 2025':'#6b8cae','Older':'#8f8389'};
    (snap.season||[]).forEach(r=>{
      const row=el('div','snaprow');
      row.innerHTML=`<div class="lab"><span class="nm">${r.s}</span><span class="v">${fmtV(r[sk])}</span></div>`+
        `<div class="trackbar"><i style="width:${Math.round(100*r[sk]/smax)}%;background:${scol[r.s]||'#8f8389'}"></i></div>`;
      b2.append(row);
    });
    const ts=(snap.totals&&snap.totals.season)||null;
    if(ts){
      const tr=el('div','snaptot');
      tr.innerHTML=`<span>Total stock</span><span class="v">${fmtV(ts[sk])}</span>`;
      b2.append(tr);
    }
    c2.append(b2); grid.append(c2);
    wrap.append(grid);
    const grid2=el('div','grid g2');
    const c3=el('div','card');
    c3.append(el('h3',null,`<span>Active Style Codes</span><span class="tag">color codes · inv &gt; 0</span>`));
    const b3=el('div','snapbody');
    const nmax=Math.max(...(snap.style||[]).map(x=>x.n),1);
    (snap.style||[]).slice(0,9).forEach(r=>{
      const row=el('div','styrow');
      row.innerHTML=`<span class="nm">${r.cat}</span>`+
        `<div class="trackbar" style="flex:1"><i style="width:${Math.round(100*r.n/nmax)}%;background:#7a6f95"></i></div>`+
        `<span class="n">${fmtNum(r.n)}</span>`;
      b3.append(row);
    });
    const tst=(snap.totals&&snap.totals.style!=null)?snap.totals.style:null;
    if(tst!=null){
      const tr=el('div','snaptot');
      tr.innerHTML=`<span>Total active</span><span class="v">${fmtNum(tst)} codes</span>`;
      b3.append(tr);
    }
    c3.append(b3); grid2.append(c3);
    const c4=el('div','card');
    c4.append(el('h3',null,`<span>Size Availability</span><span class="tag">in stock / total sizes</span>`));
    const b4=el('div','snapbody');
    const szcol=av=>av>=80?'#5a7d74':av>=60?'#c9a96a':'#d8804f';
    (snap.size||[]).slice(0,8).forEach(r=>{
      const has=r.subs&&r.subs.length;
      const open=state.snapOpen[r.cat];
      const head=el('div','styrow'+(has?' sizecat':''));
      head.innerHTML=`<span class="nm"><span class="car${has?'':' no'}">${has?(open?'▾':'▸'):''}</span>${r.cat}</span>`+
        `<div class="trackbar" style="flex:1"><i style="width:${r.av}%;background:${szcol(r.av)}"></i></div>`+
        `<span class="n">${r.av}%</span>`;
      if(has){ head.onclick=()=>{state.snapOpen[r.cat]=!open;render();}; }
      b4.append(head);
      if(open && r.subs){
        const box=el('div','sizesub');
        r.subs.forEach(t=>{
          const sr=el('div','styrow');
          sr.innerHTML=`<span class="nm" style="width:88px;font-size:11px;color:var(--muted)">${t.sub}</span>`+
            `<div class="trackbar" style="flex:1"><i style="width:${t.av}%;background:${szcol(t.av)}"></i></div>`+
            `<span class="n" style="font-size:11px">${t.av}%</span>`;
          box.append(sr);
        });
        b4.append(box);
      }
    });
    const tz=(snap.totals&&snap.totals.size!=null)?snap.totals.size:null;
    if(tz!=null){
      const tr=el('div','snaptot');
      tr.innerHTML=`<span>Overall availability</span><span class="v">${tz}%</span>`;
      b4.append(tr);
      // Footwear-only availability: cc-weighted across every group's FOOTWEAR sub-row
      let fwNum=0, fwDen=0;
      (snap.size||[]).forEach(r=>{(r.subs||[]).forEach(s=>{
        if((s.sub||'').toUpperCase()==='FOOTWEAR' && s.cc){ fwNum+=s.av*s.cc; fwDen+=s.cc; }
      });});
      if(fwDen>0){
        const fw=(fwNum/fwDen);
        const tr2=el('div','snaptot');
        tr2.innerHTML=`<span>Overall availability (Footwear only)</span><span class="v">${fw.toFixed(1)}%</span>`;
        b4.append(tr2);
      }
    }
    c4.append(b4); grid2.append(c4);
    wrap.append(grid2);
    return wrap;
  }
  function countryPerfCard(){
    const lflOn = !!state.lfl;
    const bb=state.budgetBasis||'rebudget';
    // Non-LFL uses the precomputed country_perf. The generator now emits the budget columns for
    // BOTH tabs (sales_bud_original / sales_bud_rebudget + their _pct), so the Re-Budget /
    // Original-Budget toggle picks the right pair here; the legacy single-value keys are used as
    // a fallback if an older payload is still live. LFL rebuilds per country from its kpi_lfl
    // (comparable-stores cohort) so the YoY is like-for-like; budget is left blank in LFL mode
    // because LFL sales are a store subset, not comparable to the full budget.
    let rows;
    if(!lflOn){
      rows=((D.country_perf&&D.country_perf[state.period])||[]).map(function(r){
        const o=Object.assign({},r);
        if(r['sales_bud_'+bb]!==undefined)     o.sales_bud     = r['sales_bud_'+bb];
        if(r['sales_bud_pct_'+bb]!==undefined) o.sales_bud_pct = r['sales_bud_pct_'+bb];
        return o;
      });
    } else {
      const cb=D.country_blobs||{};
      const absM=d=>{ if(!d) return null; const s=d.sales, gp=d.gp; return (s==null||gp==null)?null:s*gp/100; };
      rows=[];
      Object.keys(cb).forEach(cn=>{
        if(cn==='All Countries') return;
        const k=(cb[cn].kpi_lfl&&cb[cn].kpi_lfl[state.period])||{};
        const ty=k.ty||{}, ly=k.ly||{};
        if(ty.sales==null && ly.sales==null) return;
        rows.push({country:cn,
          sales_ty:(ty.sales==null?null:ty.sales), sales_ly:(ly.sales==null?null:ly.sales),
          sales_bud:null, sales_bud_pct:null,
          margin_ty:absM(ty), margin_ly:absM(ly),
          footfall_ty:(ty.footfall==null?null:ty.footfall), footfall_ly:(ly.footfall==null?null:ly.footfall)});
      });
      rows.sort((a,b)=>(b.sales_ty||0)-(a.sales_ty||0));
    }
    const c=el('div','card');
    const head=el('h3');
    head.innerHTML=`<span>Country Level Performance — ${periodLabel[state.period]}${lflOn?' · LFL':''}</span>`+
      `<span class="tag">${lflOn?'':(bb==='rebudget'?'re-budget':'original budget')}</span>`;
    c.append(head);
    c.append(el('div','sub', lflOn
      ? 'Like-for-like — comparable stores only (traded both years) · budget hidden in LFL view'
      : 'Sales, budget, margin and footfall by country'));
    if(!rows.length){ c.append(el('div','empty', lflOn?'No like-for-like data for this period.':'No country KPI data for this period.')); return c; }
    const yo=(ty,ly)=> (ty!=null&&ly!=null&&ly!=0)? ((ty-ly)/Math.abs(ly)*100):null;
    const yoCell=(v)=>{ if(v==null) return '<td class="num">—</td>';
      const cls=v>=0?'pos':'neg'; return `<td class="num ${cls}">${v>=0?'+':''}${v.toFixed(1)}%</td>`; };
    const budCell=(v)=>{ if(v==null) return '<td class="num">—</td>';
      const cls=v>=100?'pos':'neg'; return `<td class="num ${cls}">${v.toFixed(1)}%</td>`; };
    const tbl=el('table','cperf');
    tbl.innerHTML=`<thead><tr>
      <th>Country</th>
      <th class="num">Sales TY</th><th class="num">Sales LY</th><th class="num">+/- YoY</th>
      <th class="num">Sales Budget</th><th class="num">Bud %</th>
      <th class="num">Margin TY</th><th class="num">Margin LY</th><th class="num">+/- YoY</th>
      <th class="num">Footfall TY</th><th class="num">Footfall LY</th><th class="num">+/- YoY</th>
    </tr></thead>`;
    const tb=el('tbody');
    const T={sty:0,sly:0,sbud:0,mty:0,mly:0,fty:0,fly:0};
    rows.forEach(r=>{
      T.sty+=r.sales_ty||0; T.sly+=r.sales_ly||0; T.sbud+=r.sales_bud||0;
      T.mty+=r.margin_ty||0; T.mly+=r.margin_ly||0; T.fty+=r.footfall_ty||0; T.fly+=r.footfall_ly||0;
      const tr=el('tr');
      tr.innerHTML=`<td class="cname">${r.country}</td>`
        +`<td class="num">${r.sales_ty==null?'—':fmtMoney(r.sales_ty)}</td>`
        +`<td class="num">${r.sales_ly==null?'—':fmtMoney(r.sales_ly)}</td>`
        +yoCell(yo(r.sales_ty,r.sales_ly))
        +`<td class="num">${r.sales_bud==null?'—':fmtMoney(r.sales_bud)}</td>`
        +budCell(r.sales_bud_pct)
        +`<td class="num">${r.margin_ty==null?'—':fmtMoney(r.margin_ty)}</td>`
        +`<td class="num">${r.margin_ly==null?'—':fmtMoney(r.margin_ly)}</td>`
        +yoCell(yo(r.margin_ty,r.margin_ly))
        +`<td class="num">${r.footfall_ty==null?'—':fmtNum(r.footfall_ty)}</td>`
        +`<td class="num">${r.footfall_ly==null?'—':fmtNum(r.footfall_ly)}</td>`
        +yoCell(yo(r.footfall_ty,r.footfall_ly));
      tb.append(tr);
    });
    const budpct = T.sbud? (100*T.sty/T.sbud):null;
    const tr=el('tr','total');
    tr.innerHTML=`<td class="cname">Total</td>`
      +`<td class="num">${fmtMoney(T.sty)}</td><td class="num">${fmtMoney(T.sly)}</td>`
      +yoCell(yo(T.sty,T.sly))
      +`<td class="num">${fmtMoney(T.sbud)}</td>`+budCell(budpct)
      +`<td class="num">${fmtMoney(T.mty)}</td><td class="num">${fmtMoney(T.mly)}</td>`
      +yoCell(yo(T.mty,T.mly))
      +`<td class="num">${fmtNum(T.fty)}</td><td class="num">${fmtNum(T.fly)}</td>`
      +yoCell(yo(T.fty,T.fly));
    tb.append(tr);
    tbl.append(tb);
    const scroll=el('div','mixscroll'); scroll.append(tbl); c.append(scroll);
    return c;
  }
  // ---- #2/#3 weekly trend charts (inline SVG) ----
  function weeklyForSelection(){
    const wk=D.weekly; if(!wk||!wk.weeks||!wk.weeks.length) return null;
    let series;
    if(state.store!=='__ALL__') series=wk.store&&wk.store[state.store];
    else if(state.country && state.country!=='All Countries') series=wk.country&&wk.country[state.country];
    else series=wk.all;
    if(!series) return null;
    return {weeks:wk.weeks, s:series};
  }
  function svgLineChart(labels, lines, opts){
    // lines: [{name,color,data:[...],dash?:bool}]; opts:{fmt, h, money}
    opts=opts||{};
    const W=680, padL=64, padR=18, padT=(opts.labels?30:18);
    // ---- legend layout ----
    // Entries are MEASURED and laid out sequentially, then wrapped onto extra rows if they'd
    // run past the right edge. The old code stamped them at a fixed 120px stride, so any name
    // longer than ~120px (e.g. 'ASP (Average Selling Price)') was overprinted by the next entry.
    // Bottom padding and height grow with the number of legend rows, so nothing is clipped.
    const LEG_H=16, LEG_SW=22, LEG_GAP=7, LEG_PAD=22, CHAR_W=6.0;
    const legW = l => LEG_SW + LEG_GAP + Math.ceil(String(l.name).length*CHAR_W) + LEG_PAD;
    const legRows=[]; let _cur=[], _curW=0;
    lines.forEach(l=>{
      const w=legW(l);
      if(_cur.length && (_curW+w) > (W-padL-padR)){ legRows.push(_cur); _cur=[]; _curW=0; }
      _cur.push(l); _curW+=w;
    });
    if(_cur.length) legRows.push(_cur);
    const legTotal = legRows.length*LEG_H;
    const padB = 26 + legTotal;                 // x-axis labels + legend rows
    const H = opts.h || (244 + legTotal);       // single-row legend => 260, as before
    const iw=W-padL-padR, ih=H-padT-padB;
    const all=[]; lines.forEach(l=>l.data.forEach(v=>{ if(v!=null) all.push(v); }));
    if(!all.length) return '<div class="empty">No data for this view.</div>';
    let mn=Math.min(...all), mx=Math.max(...all);
    if(mn===mx){ mn=mn-1; mx=mx+1; }
    const pad=(mx-mn)*0.08; mn=Math.max(0,mn-pad); mx=mx+pad;
    const n=labels.length;
    const x=i=> padL + (n<=1?iw/2:(iw*i/(n-1)));
    const y=v=> padT + ih - ih*((v-mn)/(mx-mn));
    const fmt=opts.fmt||(v=>Math.round(v).toLocaleString());
    // gridlines (4)
    let grid='', ticks=4;
    for(let t=0;t<=ticks;t++){
      const gv=mn+(mx-mn)*t/ticks, gy=y(gv);
      grid+=`<line x1="${padL}" y1="${gy.toFixed(1)}" x2="${W-padR}" y2="${gy.toFixed(1)}" class="cgrid"/>`;
      grid+=`<text x="${padL-8}" y="${(gy+3).toFixed(1)}" class="cyl">${fmt(gv)}</text>`;
    }
    // x labels
    let xlab='';
    labels.forEach((lb,i)=>{ xlab+=`<text x="${x(i).toFixed(1)}" y="${H-padB+18}" class="cxl">${lb}</text>`; });
    // paths
    let paths='', dots='', vlabels='';
    const labelFmt = opts.labelFmt || fmt;
    lines.forEach((l,li)=>{
      let d='', started=false;
      l.data.forEach((v,i)=>{ if(v==null){started=false;return;}
        d+=(started?' L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1); started=true;
        dots+=`<circle cx="${x(i).toFixed(1)}" cy="${y(v).toFixed(1)}" r="3" fill="${l.color}"/>`;
        // data labels: on single-line charts label every point; on multi-line, only the primary (first) line
        if(opts.labels && (lines.length===1 || li===0)){
          const _t=String(labelFmt(v));
          const _w=Math.max(34, _t.length*6.4+10);          // fit the text, don't clip it
          let _cx=x(i);
          _cx=Math.max(padL+_w/2, Math.min(W-padR-_w/2, _cx));   // keep the box inside the plot
          const ly=Math.max(padT+11, y(v)-12);                    // don't ride above the top edge
          vlabels+=`<g class="cvlab"><rect x="${(_cx-_w/2).toFixed(1)}" y="${(ly-11).toFixed(1)}" width="${_w.toFixed(1)}" height="15" rx="4"/>`+
                   `<text x="${_cx.toFixed(1)}" y="${(ly).toFixed(1)}" class="cvtext">${_t}</text></g>`;
        }
      });
      paths+=`<path d="${d}" fill="none" stroke="${l.color}" stroke-width="2.5"${l.dash?' stroke-dasharray="5 4"':''} stroke-linejoin="round" stroke-linecap="round"/>`;
    });
    // legend — sequential x within each measured row; rows stack upward from the baseline
    let leg='';
    legRows.forEach((row,ri)=>{
      const ly = H - legTotal + (ri*LEG_H) + 11;
      let lx = padL;
      row.forEach(l=>{
        leg+=`<line x1="${lx}" y1="${ly}" x2="${lx+LEG_SW}" y2="${ly}" stroke="${l.color}" stroke-width="3"${l.dash?' stroke-dasharray="5 4"':''}/>`;
        leg+=`<text x="${lx+LEG_SW+LEG_GAP}" y="${ly+4}" class="cleg">${l.name}</text>`;
        lx += legW(l);
      });
    });
    return `<svg viewBox="0 0 ${W} ${H}" class="trendsvg" preserveAspectRatio="xMidYMid meet">${grid}${xlab}${paths}${dots}${vlabels}${leg}</svg>`;
  }
  function weeklySalesCard(){
    const wd=weeklyForSelection();
    const c=el('div','card');
    c.append(el('h3',null,`<span>Weekly Sales Trend</span><span class="tag">this year vs last year vs budget</span>`));
    if(!wd){ c.append(el('div','empty','Weekly data not available yet.')); return c; }
    const labels=wd.weeks.map(w=>w.label);
    // Budget line follows the Re-Budget / Original-Budget toggle. The generator emits a weekly
    // series per tab (sales_bud_original / sales_bud_rebudget); sales_bud is the legacy
    // re-budget alias, used as a fallback if an older payload is still live.
    const bb=state.budgetBasis||'rebudget';
    const budData=wd.s['sales_bud_'+bb]||wd.s.sales_bud||[];
    const lines=[
      {name:'This Year',color:'var(--ink)',data:wd.s.sales_ty||[]},
      {name:'Last Year',color:'#9aa0a6',data:wd.s.sales_ly||[],dash:true},
      {name:(bb==='rebudget'?'Re-Budget':'Orig Budget'),color:'var(--gold)',data:budData,dash:true},
    ];
    const wrap=el('div','trendwrap'); wrap.innerHTML=svgLineChart(labels,lines,{fmt:v=>fmtMoneyShort(v),money:true,labels:true});
    c.append(wrap); return c;
  }
  const KPI_METRICS=[['asp','ASP (Average Selling Price)'],['aov','AOV (Average Transaction Value)'],
                     ['upt','UPT (Units Per Transaction)'],['conv','Conversion Rate (%)'],['footfall','Footfall']];
  function weeklyKpiCard(){
    const wd=weeklyForSelection();
    const c=el('div','card');
    const head=el('h3');
    head.innerHTML=`<span>Multi-Week KPI Trend</span>`;
    const sel=el('select','kpisel');
    KPI_METRICS.forEach(([k,lab])=>{ const o=new Option(lab,k); if(k===state.kpiMetric)o.selected=true; sel.append(o); });
    sel.onchange=()=>{ state.kpiMetric=sel.value; render(); };
    head.append(sel); c.append(head);
    if(!wd){ c.append(el('div','empty','Weekly data not available yet.')); return c; }
    const m=state.kpiMetric||'asp';
    const labels=wd.weeks.map(w=>w.label);
    const isMoney=(m==='aov'||m==='asp');
    const isPct=(m==='conv');
    const isDec=(m==='upt');
    const fmt = isMoney? (v=>fmtMoneyShort(v)) : (isPct? (v=>v.toFixed(1)+'%') : (isDec? (v=>v.toFixed(1)) : (v=>Math.round(v).toLocaleString())));
    // The generator emits a weekly TARGET series per metric per budget tab (tgt_<metric>_<tab>),
    // derived from the budget tabs' additive target columns. Draw it alongside the actual so the
    // Re-Budget / Original-Budget toggle switches this chart too. A metric with no target column
    // populated simply renders the actual line alone.
    const bb=state.budgetBasis||'rebudget';
    const lines=[{name:(KPI_METRICS.find(x=>x[0]===m)||['',m])[1],color:'var(--accent2)',data:wd.s[m]||[]}];
    const tgt=wd.s['tgt_'+m+'_'+bb];
    if(tgt && tgt.some(v=>v!=null)){
      lines.push({name:(bb==='rebudget'?'Re-Budget target':'Orig target'),color:'var(--gold)',data:tgt,dash:true});
    }
    const wrap=el('div','trendwrap'); wrap.innerHTML=svgLineChart(labels,lines,{fmt,labels:true});
    c.append(wrap); return c;
  }
  function fmtMoneyShort(v){
    if(v==null) return '—';
    let n=v, cur='';
    if(FX.cur==='USD'){ n=v*FX.rate; cur='$'; }
    else if(FX.cur==='LOCAL' && FX.localRate!=null){ n=v*FX.localRate; cur=FX.localCode+' '; }
    const abs=Math.abs(n);
    if(abs>=1e6) return cur+(n/1e6).toFixed(1)+'M';
    if(abs>=1e3) return cur+(n/1e3).toFixed(0)+'k';
    return cur+Math.round(n).toLocaleString('en-US');
  }
  function brokenSizeCard(){
    const rows=(D.broken_size||[]);
    const c=el('div','card');
    c.append(el('h3',null,`<span>DS-Broken Size % By Store — Steve Madden</span><span class="tag">current week · style with only 1–3 sizes in stock · tap a country to expand</span>`));
    if(!rows.length){ c.append(el('div','empty','Broken-size data not available yet.')); return c; }
    // scope to current selection: store -> that store; country -> that country; all -> all
    let view=rows;
    if(state.store!=='__ALL__'){ view=rows.filter(r=>r.location===state.store); }
    else if(state.country && state.country!=='All Countries'){ view=rows.filter(r=>r.country===state.country); }
    if(!view.length){ c.append(el('div','empty','No broken-size rows for this view.')); return c; }
    const cmap={'United Arab Emirates':'UAE','Saudi Arabia':'KSA','Qatar':'QAT','Kuwait':'KWT','Bahrain':'BHR','Oman':'OMN'};
    const pct=v=> v==null?'—':v.toFixed(1)+'%';
    const groups=[]; const gmap={};
    view.forEach(r=>{ const k=r.country||'—'; if(!gmap[k]){ gmap[k]={country:k,rows:[]}; groups.push(gmap[k]); } gmap[k].rows.push(r); });
    const tbl=el('table','cperf brk');
    tbl.innerHTML=`<thead><tr>
      <th>Country</th><th>Location Type</th><th>Location Name</th>
      <th class="num">% Full Price Styles</th><th class="num">% PMD Styles</th>
      <th class="num">Full Price Broken % (1–3 sizes)</th><th class="num">PMD Broken % (1–3 sizes)</th>
    </tr></thead>`;
    const tb=el('tbody');
    groups.forEach((grp,gi)=>{
      const childRows=[];
      const htr=el('tr','brk-grphead');
      htr.style.cursor='pointer';
      htr.style.background='#faf7f2';
      htr.innerHTML=`<td colspan="7" class="cname" style="font-weight:700;"><span class="brk-caret" style="display:inline-block;width:14px;color:var(--accent);">▸</span>${cmap[grp.country]||grp.country} <span class="tag" style="font-weight:500;color:var(--muted);font-size:10px;">(${grp.rows.length} ${grp.rows.length===1?'store':'stores'})</span></td>`;
      tb.append(htr);
      grp.rows.forEach(r=>{
        const tr=el('tr','brk-grprow');
        tr.style.display='none';
        tr.innerHTML=`<td class="cname">${cmap[r.country]||r.country}</td>`
          +`<td>${r.loc_type||'MAIN'}</td>`
          +`<td class="cname">${r.location}</td>`
          +`<td class="num">${pct(r.fp_pct)}</td>`
          +`<td class="num">${pct(r.pmd_pct)}</td>`
          +`<td class="num strong">${pct(r.fp_broken_pct)}</td>`
          +`<td class="num strong">${pct(r.pmd_broken_pct)}</td>`;
        tb.append(tr);
        childRows.push(tr);
      });
      htr.addEventListener('click',()=>{
        const open=htr.classList.toggle('open');
        htr.querySelector('.brk-caret').textContent=open?'▾':'▸';
        childRows.forEach(tr=>{ tr.style.display=open?'':'none'; });
      });
    });
    tbl.append(tb);
    const scroll=el('div','mixscroll'); scroll.append(tbl); c.append(scroll);
    return c;
  }
  // ---- reduced sales strip for Ecom / 3P (Sales / Qty / ASP / GP%) ----
  function channelStrip(st){
    const wrap=el('div','kpis'); wrap.style.gridTemplateColumns='repeat(4,1fr)';
    const s=(st.sales && st.sales[state.period])||{};
    const defs=[['Sales Amount',s.sales,v=>fmtMoney(v)],['Sales Qty',s.qty,v=>fmtNum(v)],
                ['ASP',s.asp,v=>fmtMoney(v)],['GP %',s.gp,v=>v==null?'—':v+'%']];
    defs.forEach(([lab,val,fmt])=>{
      const c=el('div','kpi');
      c.innerHTML=`<div class="klabel">${lab}</div><div class="kval">${val==null?'—':fmt(val)}</div>`+
        `<div class="kly"><span class="lyval">${periodLabel[state.period]}</span></div>`;
      wrap.append(c);
    });
    return wrap;
  }
  // ---- inventory strip for WH / Wholesale (replaces the sales KPI strip) ----
  function inventoryStrip(st){
    const wrap=el('div','kpis'); wrap.style.gridTemplateColumns='repeat(4,1fr)';
    const snap=st.inv_snapshot||{};
    const transitUnits=(st.in_transit||[]).reduce((a,r)=>a+(r.qty||0),0);
    const defs=[['Total Units',snap.total_units,v=>fmtNum(v)],['Inventory Value',snap.total_value,v=>fmtMoney(v)],
                ['In-Transit Units',transitUnits,v=>fmtNum(v)],['Active Style Codes',snap.total_cc,v=>fmtNum(v)]];
    defs.forEach(([lab,val,fmt])=>{
      const c=el('div','kpi');
      c.innerHTML=`<div class="klabel">${lab}</div><div class="kval">${val==null?'—':fmt(val)}</div>`+
        `<div class="kly"><span class="lyval">current stock</span></div>`;
      wrap.append(c);
    });
    return wrap;
  }
  // ---- Ecom available-to-sell (pooled fulfilment stock, threshold applied) ----
  function ecomAvailabilityCard(){
    const av=vb()&&vb().availability;
    const c=el('div','card');
    c.append(el('h3',null,`<span>Ecom Available-to-Sell</span><span class="tag">pooled fulfilment stock · threshold applied</span>`));
    if(!av){ c.append(el('div','empty','Availability accruing — Available Qty not in this extract yet.')); return c; }
    const b=el('div','snapbody');
    b.append(el('div','snapsub',`${fmtNum(av.total)} units available across ${(av.by_location||[]).length} fulfilment locations`));
    const groups=(av.by_group||[]).slice(0,8);
    const max=Math.max(...groups.map(x=>x.units),1);
    groups.forEach(r=>{
      const row=el('div','styrow');
      row.innerHTML=`<span class="nm">${r.cat}</span>`+
        `<div class="trackbar" style="flex:1"><i style="width:${Math.round(100*r.units/max)}%;background:#5a7d74"></i></div>`+
        `<span class="n">${fmtNum(r.units)}</span>`;
      b.append(row);
    });
    c.append(b); return c;
  }
  // ---- location ranking for non-store views (by sales for selling, by stock otherwise) ----
  function viewRankCard(){
    const c=el('div','country');
    const {rows,money}=getRankRows();
    const combined=state.store==='__ALL__';
    const fmtV=v=>money?fmtMoney(v):fmtNum(v);
    c.append(el('h3',null,`${state.country} — ${VIEW_LABEL[state.view]} Ranked · by ${money?'sales (MTD)':'stock (units)'}`));
    const hero=el('div','chero');
    const totV=rows.reduce((a,r)=>a+(r.val||0),0);
    hero.innerHTML=`<span class="big">${rows.length}</span>`+
      `<span class="lbl">${VIEW_NOUN[state.view]}<br>total ${money?'sales':'units'} ${fmtV(totV)}</span>`;
    c.append(hero);
    if(!rows.length){ return c; }
    const max=Math.max(...rows.map(x=>x.val),1);
    rows.forEach(r=>{
      const me=(!combined && r.store===state.store);
      const short=r.store.replace(/^SM /,'').replace(/^ECOMM - /,'EC ').replace(/^3PEC /,'3P ');
      const row=el('div','crow'+(me?' me':''));
      row.innerHTML=`<span class="cn">${r.rank}. ${short}</span>`+
        `<span class="cbar"><i style="width:${100*r.val/max}%"></i></span>`+
        `<span class="cp">${r.pct}% · ${fmtV(r.val)}</span>`;
      c.append(row);
    });
    return c;
  }

  // ===================== PI:START — Competitor Intelligence (EDITED) =====================
  // Reads D.product_intel, built by product_intel.py in the generator. SELF-CONTAINED: no ERP
  // number is read or rendered in here, and the drawer never sits beside the Avg Markdown tile.
  // EDITED's discount = cut off ticket price across LISTED OPTIONS on 6th Street / Namshi;
  // the dashboard's Avg Markdown = revenue-weighted ACTUAL markdown from the ERP. Different
  // metrics on different populations — never subtracted, blended, or shown as a delta.
  const PI = {mkt:null, tab:'hl'};
  // ERP country -> EDITED market. Countries absent here are NOT TRACKED in the export
  // (EDITED returned data for AE and SA only) and must say so rather than render empty charts.
  const PI_CTRY = {'United Arab Emirates':'AE','Saudi Arabia':'SA'};
  const PI_TABS = [['hl','Highlights'],['md','Markdown'],['pr','Price architecture'],
                   ['rm','Range & mix'],['st','Sell-through']];
  // Bin colours ramp cool -> hot; the 70%+ tail is red, because that tail IS the headline risk.
  const PI_BIN = {'0-10%':'#cfe0da','10-20%':'#b3cec5','20-30%':'#96bcb0','30-40%':'#7aaa9b',
                  '40-50%':'#d9c48a','50-60%':'#caa24a','60-70%':'#d8804f',
                  '70-80%':'#c9483f','80-90%':'#a83229','90-100%':'#7d201a'};
  const piDeep = b => (b==='70-80%'||b==='80-90%'||b==='90-100%');
  function piData(){ return (D && D.product_intel) || null; }
  function piMkts(){ const p=piData(); return (p && p.meta && p.meta.markets) || []; }
  function piOwn(){ const p=piData(); return (p && p.meta && p.meta.own) || 'Steve Madden'; }
  function piCur(){ const p=piData(); if(!p) return null; return (p.data||{})[PI.mkt]||null; }
  // Default the drawer's market to whatever country the dashboard is scoped to, when that
  // country is tracked; otherwise fall back to the first tracked market.
  function piDefaultMkt(){
    const ms=piMkts(); if(!ms.length) return null;
    const m=PI_CTRY[state.country];
    return (m && ms.indexOf(m)>=0) ? m : ms[0];
  }
  function piAge(){
    const p=piData(); const d=p&&p.meta&&p.meta.pulled; if(!d) return null;
    const t=Date.parse(d+'T00:00:00Z'); if(isNaN(t)) return null;
    return Math.floor((Date.now()-t)/86400000);
  }
  function piRenderBar(){
    const bar=$('#piBar'); bar.innerHTML='';
    const p=piData(); if(!p) return;
    // Freshness keys off the EDITED export's OWN pull date, never the payload build date —
    // the generator runs daily, so a build-date chip would sit green while the data rotted.
    const age=piAge();
    const chip=el('span','pi-fresh '+((age!=null&&age<10)?'ok':'old'),
      age==null ? 'pull date unknown'
                : (age<10 ? ('Current · '+age+'d old') : (age+' days old — refresh due')));
    bar.append(chip);
    const ms=piMkts();
    if(ms.length>1){
      const g=el('div','pi-mkt');
      ms.forEach(m=>{ const b=el('button',PI.mkt===m?'on':'',m);
        b.onclick=()=>{PI.mkt=m;piRender();}; g.append(b); });
      bar.append(g);
    }
    bar.append(el('span','chip', (p.meta.options||0).toLocaleString('en-US')+' options · '+
      (p.meta.brands||[]).length+' brands · '+(p.meta.weeks||0)+'w history'));
  }
  function piRenderTabs(){
    const t=$('#piTabs'); t.innerHTML='';
    PI_TABS.forEach(([k,lab])=>{ const b=el('button',PI.tab===k?'on':'',lab);
      b.onclick=()=>{PI.tab=k;piRender();}; t.append(b); });
  }
  function piKpis(d){
    const wrap=el('div','pi-kpis');
    const me=(d.scorecard||[]).find(r=>r.brand===piOwn());
    const lad=(d.ladder||[]).find(r=>r.brand===piOwn());
    const peers=(d.scorecard||[]).filter(r=>r.brand!==piOwn());
    const avgCut=peers.length? peers.reduce((a,r)=>a+(r.avg_disc||0),0)/peers.length : null;
    const defs=[
      ['Options', me? me.options.toLocaleString('en-US'):'—', me? me.share+'% of tracked range':'', false],
      ['Avg cut', me&&me.avg_disc!=null? me.avg_disc+'%':'—',
        avgCut!=null? ('peers '+avgCut.toFixed(1)+'%'):'', me&&avgCut!=null&&me.avg_disc>avgCut],
      ['70%+ tail', lad&&lad.deep!=null? lad.deep+'%':'—', 'of discounted lines', lad&&lad.deep>15],
      ['Sellout', me&&me.sellout!=null? me.sellout+'%':'—',
        (d.scorecard||[]).length? ('best '+Math.max.apply(null,(d.scorecard||[]).map(r=>r.sellout||0)).toFixed(1)+'%'):'', false],
    ];
    defs.forEach(([l,v,s,bad])=>{
      const c=el('div','pi-kpi');
      c.innerHTML='<div class="l">'+l+'</div><div class="v'+(bad?' bad':'')+'">'+v+'</div><div class="s">'+(s||'')+'</div>';
      wrap.append(c);
    });
    return wrap;
  }
  function piLadder(d){
    const c=el('div','pi-card');
    c.append(el('h4',null,'<span>Markdown depth ladder</span><span class="t">how each brand\'s discounted lines split by depth · 70%+ in red</span>'));
    const b=el('div','pi-cb');
    const rows=d.ladder||[];
    if(!rows.length){ b.append(el('div','empty','No discount data for this market.')); c.append(b); return c; }
    rows.forEach(r=>{
      const row=el('div','pi-lad');
      const isMe=r.brand===piOwn();
      row.append(el('div','nm'+(isMe?' me':''),r.brand));
      const st=el('div','st');
      (r.bins||[]).forEach(bn=>{
        if(!bn.pct) return;
        const i=el('i'); i.style.width=bn.pct+'%';
        i.style.background=PI_BIN[bn.bin]||'#cfc7c0';
        i.title=r.brand+' · '+bn.bin+' off: '+bn.pct+'% of its discounted lines';
        st.append(i);
      });
      row.append(st);
      row.append(el('div','dv'+(isMe?' me':''), (r.deep==null?'—':r.deep+'%')));
      b.append(row);
    });
    const lg=el('div','pi-leg');
    Object.keys(PI_BIN).forEach(k=>{
      lg.innerHTML+='<span><i style="background:'+PI_BIN[k]+'"></i>'+k+(piDeep(k)?'':'')+'</span>';
    });
    b.append(lg);
    b.append(el('div','pi-leg','<span style="color:var(--neg);font-weight:600">Right-hand figure = share of that brand\'s discounted lines sitting at 70%+ off.</span>'));
    c.append(b); return c;
  }
  function piTrend(d){
    const c=el('div','pi-card');
    c.append(el('h4',null,'<span>Advertised discount over time</span><span class="t">weekly · '+((d.trend&&d.trend.weeks)||0)+' weeks</span>'));
    const t=d.trend||{};
    if(!t.dates||!t.dates.length){ c.append(el('div','empty','No trend history for this market.')); return c; }
    // Thin the x labels so 29 weeks don't collide.
    const step=Math.ceil(t.dates.length/8);
    const labels=t.dates.map((x,i)=> (i%step===0||i===t.dates.length-1)? x : '');
    const pal={};
    const cols=['#9aa0a6','#5a7d74','#caa24a','#6b8cae','#8f8389'];
    let ci=0;
    const lines=[];
    Object.keys(t.series).sort().forEach(b=>{
      const isMe=b===piOwn();
      lines.push({name:b, color:isMe?'var(--accent)':cols[ci++ % cols.length],
                  data:t.series[b], dash:!isMe});
    });
    lines.sort((a,b)=> (a.name===piOwn()? -1 : b.name===piOwn()? 1 : 0));
    const w=el('div','trendwrap');
    w.innerHTML=svgLineChart(labels,lines,{fmt:v=>v.toFixed(0)+'%', h:300});
    c.append(w);
    return c;
  }
  function piScorecard(d, cols){
    const c=el('div','pi-card');
    c.append(el('h4',null,'<span>Brand scorecard</span><span class="t">'+PI.mkt+' · live in-stock options</span>'));
    const t=el('table','pi-t');
    t.innerHTML='<thead><tr><th>Brand</th>'+cols.map(x=>'<th>'+x[1]+'</th>').join('')+'</tr></thead>';
    const tb=el('tbody');
    (d.scorecard||[]).forEach(r=>{
      const tr=el('tr', r.brand===piOwn()?'me':'');
      tr.innerHTML='<td>'+r.brand+'</td>'+cols.map(x=>{
        const v=r[x[0]]; const bad=x[2]&&x[2](r);
        return '<td class="'+(bad?'bad':'')+'">'+(v==null?'—':x[3]?x[3](v):v)+'</td>';
      }).join('');
      tb.append(tr);
    });
    t.append(tb);
    const s=el('div','mixscroll'); s.append(t); c.append(s);
    return c;
  }
  function piPrice(d){
    const c=el('div','pi-card');
    c.append(el('h4',null,'<span>Ticket vs shelf</span><span class="t">volume-weighted across listed options · AED</span>'));
    const b=el('div','pi-cb');
    const rows=d.price||[];
    if(!rows.length){ b.append(el('div','empty','No price data for this market.')); c.append(b); return c; }
    const max=Math.max.apply(null,rows.map(r=>r.full||0))||1;
    rows.forEach(r=>{
      const isMe=r.brand===piOwn();
      const row=el('div','pi-pbar');
      row.append(el('div','nm'+(isMe?' me':''),r.brand));
      const tr=el('div','tr');
      const full=el('i'); full.style.width=(100*(r.full||0)/max)+'%';
      const cur=el('b'); cur.style.width=(100*(r.cur||0)/max)+'%';
      if(isMe) cur.style.background='var(--accent)';
      tr.append(full); tr.append(cur);
      row.append(tr);
      row.append(el('div','vv', (r.full?('AED '+r.full):'—')+' → '+(r.cur?('AED '+r.cur):'—')));
      b.append(row);
    });
    const lg=el('div','pi-leg');
    lg.innerHTML='<span><i style="background:#cfc7c0"></i>Full (ticket) price</span>'+
                 '<span><i style="background:var(--accent2)"></i>Current (shelf) price</span>'+
                 '<span><i style="background:var(--accent)"></i>'+piOwn()+' shelf</span>';
    b.append(lg);
    c.append(b); return c;
  }
  function piMix(d){
    const c=el('div','pi-card');
    c.append(el('h4',null,'<span>Category mix</span><span class="t">share of each brand\'s listed range</span>'));
    const a=d.assort||{};
    const cats=(a.cats||[]).slice();
    const rows=(a.rows||[]).slice();
    if(!cats.length||!rows.length){ c.append(el('div','empty','No assortment data for this market.')); return c; }
    // Order categories by how much of OUR range they hold, so the gaps read top-down.
    const mine=(rows.find(r=>r.brand===piOwn())||{}).mix||{};
    cats.sort((x,y)=>(mine[y]||0)-(mine[x]||0));
    rows.sort((x,y)=> x.brand===piOwn()? -1 : y.brand===piOwn()? 1 : x.brand.localeCompare(y.brand));
    const t=el('table','pi-t');
    t.innerHTML='<thead><tr><th>Brand</th>'+cats.map(x=>'<th>'+x+'</th>').join('')+'</tr></thead>';
    const tb=el('tbody');
    rows.forEach(r=>{
      const tr=el('tr', r.brand===piOwn()?'me':'');
      tr.innerHTML='<td>'+r.brand+'</td>'+cats.map(cn=>{
        const v=r.mix[cn];
        const lead=Math.max.apply(null,rows.map(z=>z.mix[cn]||0));
        // Flag only OUR row, and only where we're materially behind the category leader.
        const bad=(r.brand===piOwn() && v!=null && lead && v < lead*0.75);
        return '<td class="'+(bad?'bad':'')+'">'+(v==null?'—':v+'%')+'</td>';
      }).join('');
      tb.append(tr);
    });
    t.append(tb);
    const s=el('div','mixscroll'); s.append(t); c.append(s);
    return c;
  }
  function piHighlights(d){
    const c=el('div','pi-card');
    c.append(el('h4',null,'<span>What the data says</span><span class="t">derived from this week\'s export</span>'));
    const hs=d.highlights||[];
    if(!hs.length){ c.append(el('div','empty','No highlights could be derived for this market.')); return c; }
    hs.forEach(h=>{
      const r=el('div','pi-hl');
      r.append(el('div','pi-sev '+(h.sev||'info')));
      const x=el('div');
      x.append(el('div','k',h.k));
      x.append(el('div','x',h.t));
      r.append(x);
      c.append(r);
    });
    return c;
  }
  function piFooter(){
    const p=piData(); if(!p) return el('div');
    const f=el('div','pi-ft');
    f.innerHTML='Source: '+(p.meta.source||'—')+' · pulled '+(p.meta.pulled||'—')+
      '<br>'+(p.meta.basis||'')+
      '<br>Keep the EDITED view\'s brand and retailer filters stable week to week, or the trend lines will step for a reason that isn\'t the market.';
    return f;
  }
  function piRender(){
    const body=$('#piBody'); body.innerHTML='';
    const p=piData();
    // LOUD failure — never silently show stale or empty numbers.
    if(!p){
      body.append(el('div','pi-fail','Competitor data unavailable'+
        '<span>No EDITED export was found in this build. Drop EDITED_SM_View_&lt;date&gt;.xlsx into the SM Drive folder and re-run the refresh.</span>'));
      $('#piBar').innerHTML=''; $('#piTabs').innerHTML=''; return;
    }
    if(!PI.mkt || piMkts().indexOf(PI.mkt)<0) PI.mkt=piDefaultMkt();
    piRenderBar(); piRenderTabs();
    const d=piCur();
    if(!d){ body.append(el('div','pi-fail','No data for this market.')); return; }
    // Honest "not tracked" note when the dashboard's country isn't in the EDITED view.
    if(state.country && state.country!=='All Countries' && !PI_CTRY[state.country]){
      body.append(el('div','pi-note','<b>'+state.country+' is not tracked in this EDITED view.</b> '+
        'The export returned data for '+piMkts().join(' and ')+' only — the other GCC markets came back empty. '+
        'Showing '+PI.mkt+' instead; these figures do not describe '+state.country+'.'));
    }
    body.append(piKpis(d));
    const pctf=v=>v+'%';
    if(PI.tab==='hl'){
      body.append(piHighlights(d));
      body.append(piLadder(d));
    } else if(PI.tab==='md'){
      body.append(piLadder(d));
      body.append(piTrend(d));
      body.append(piScorecard(d,[['disc_pct','% of range discounted',null,pctf],
                                 ['avg_disc','Avg cut',r=>r.brand===piOwn(),pctf]]));
    } else if(PI.tab==='pr'){
      body.append(piPrice(d));
      body.append(piScorecard(d,[['p_min','Min',null,v=>'AED '+v],
                                 ['p_med','Median',null,v=>'AED '+v],
                                 ['p_max','Max',null,v=>'AED '+v]]));
    } else if(PI.tab==='rm'){
      body.append(piMix(d));
      body.append(piScorecard(d,[['options','Options',null,v=>v.toLocaleString('en-US')],
                                 ['share','Share of range',null,pctf]]));
    } else if(PI.tab==='st'){
      body.append(piScorecard(d,[['sellout','Sellout',r=>r.brand===piOwn(),pctf],
                                 ['replen','Replenished',r=>r.brand===piOwn(),pctf],
                                 ['disc_pct','% discounted',null,pctf],
                                 ['avg_disc','Avg cut',null,pctf]]));
      body.append(piHighlights(d));
    }
    body.append(piFooter());
  }
  function piOpen(){ $('#piScrim').classList.add('on'); $('#piDrawer').classList.add('on'); piRender(); }
  function piClose(){ $('#piScrim').classList.remove('on'); $('#piDrawer').classList.remove('on'); }
  function piBind(){
    const s=$('#piScrim'), x=$('#piClose');
    if(s) s.onclick=piClose;
    if(x) x.onclick=piClose;
    document.addEventListener('keydown',e=>{ if(e.key==='Escape') piClose(); });
    window.SMProductIntel={open:piOpen, close:piClose,
      setMarket:m=>{ if(piMkts().indexOf(m)>=0){ PI.mkt=m; piRender(); } },
      reload:piRender};
  }
  // Trigger pill, mounted beside the PERIOD toggle. Only shown on the Stores view — the
  // EDITED set benchmarks physical/marketplace ranges, not the DC or wholesale views.
  function piMountPill(){
    const host=$('#piPillHost'); if(!host) return;
    host.innerHTML='';
    if(!isStores()) return;
    const b=el('button','pi-pill','<span class="pi-dot"></span>Competitors');
    b.onclick=piOpen;
    host.append(b);
  }
  // ===================== PI:END =====================


  // ---- Inbound shipments (shipment_tracker tab) ----------------------------------------
  // Forward ISO-week view (Monday start, same convention as the weekly trend) of inbound
  // shipments by ETA at Jebel Ali. A shipment = a distinct SHIP NO, not a row.
  //
  // GLOBAL, NOT LOCATION-SCOPED. The tracker's Remarks column mixes a destination hint
  // ('KSA SHIPMENT') with supplier names ('CHINA HOUSE', 'SENGCHEN', 'HAO LAI'), so there is
  // no reliable store/country key. The card therefore shows the SAME figures whatever country
  // or store is selected, and says so on its face rather than appearing to respect the
  // selector while quietly ignoring it.
  function shipmentCard(){
    const s=D.shipments;
    const c=el('div','card');
    c.append(el('h3',null,'<span>Inbound Shipments · Port &rarr; WH</span>'+
      '<span class="tag">by ETA · next '+((s&&s.horizon)||10)+' weeks · Jebel Ali</span>'));
    if(!s || !s.weeks || !s.weeks.length){
      c.append(el('div','empty','Shipment tracker not available in this build.'));
      return c;
    }
    const t=el('table','ship');
    t.innerHTML='<thead><tr><th>Week</th><th>ETA range</th>'+
      '<th>Shipments</th><th>Cartons</th><th>Units</th></tr></thead>';
    const tb=el('tbody');
    const maxq=Math.max.apply(null, s.weeks.map(w=>w.qty||0).concat([1]));
    // Overdue first — an ETA that has already passed is the row people most need to see.
    const flag=(lab,o,note)=>{
      if(!o || !o.n) return;
      const tr=el('tr','warn');
      tr.innerHTML='<td>'+lab+'</td><td>'+note+'</td>'+
        '<td>'+fmtNum(o.n)+'</td><td>'+fmtNum(o.crtns)+'</td><td>'+fmtNum(o.qty)+'</td>';
      tb.append(tr);
    };
    flag('Overdue', s.overdue, 'ETA already passed');
    flag('No ETA',  s.noeta,   'no ETA on file');
    s.weeks.forEach(w=>{
      const tr=el('tr', w.current?'now':'');
      const bar=w.qty? '<span class="qb" style="width:'+Math.max(2,Math.round(100*w.qty/maxq))+'%"></span>':'';
      tr.innerHTML='<td>'+w.label+'</td><td>'+w.range+'</td>'+
        '<td>'+(w.n?fmtNum(w.n):'—')+'</td>'+
        '<td>'+(w.crtns?fmtNum(w.crtns):'—')+'</td>'+
        '<td>'+(w.qty?fmtNum(w.qty):'—')+bar+'</td>';
      tb.append(tr);
    });
    if(s.beyond && s.beyond.n){
      const tr=el('tr');
      tr.innerHTML='<td>Later</td><td>beyond the '+s.horizon+'-week horizon</td>'+
        '<td>'+fmtNum(s.beyond.n)+'</td><td>'+fmtNum(s.beyond.crtns)+'</td><td>'+fmtNum(s.beyond.qty)+'</td>';
      tb.append(tr);
    }
    if(s.total){
      const tr=el('tr','tot');
      tr.innerHTML='<td>Total</td><td>all shipments on file</td>'+
        '<td>'+fmtNum(s.total.n)+'</td><td>'+fmtNum(s.total.crtns)+'</td><td>'+fmtNum(s.total.qty)+'</td>';
      tb.append(tr);
    }
    t.append(tb);
    const sc=el('div','mixscroll'); sc.append(t); c.append(sc);
    c.append(el('div','shipnote',
      '<b>Not the same measure as Store to Store In-Transit.</b> These are vessels inbound to port &mdash; '+
      'not yet landed, not yet in the warehouse, not yet allocated to a store. The two figures cover '+
      'different stages of the supply chain, will not tie, and should not be compared. Counts are distinct '+
      'ship numbers; the tracker carries no location key, so it is shown only on the All Countries view.'));
    return c;
  }


  // ---- loading skeleton --------------------------------------------------------------
  // The data service sleeps when idle, so the first load of the day can block for 30-60s on a
  // cold start. Rather than spin silently (which reads as "broken"), the message escalates and
  // names the real reason. Timers are always cleared, on success AND on failure, so a stale
  // "still waking up" line can never sit on top of a rendered dashboard or an error.
  let SKT=[];
  function skStop(){ SKT.forEach(clearTimeout); SKT=[]; const s=$('#skel'); if(s) s.remove(); }
  function skStart(){
    const set=(t)=>{ const m=$('#skmsg'); if(m) m.textContent=t; };
    SKT.push(setTimeout(()=>set('Waking the data service \u2014 first load of the day can take up to a minute\u2026'), 6000));
    SKT.push(setTimeout(()=>set('Still waking up. Hang on\u2026'), 25000));
    SKT.push(setTimeout(()=>set('Taking longer than usual \u2014 the service may be under load.'), 50000));
  }
  function skFail(msg){
    skStop();
    $('#body').innerHTML='<div class="empty">'+msg+'</div>';
  }

  function render(){
    // period pills: channels have no 'yesterday'
    $('#fPeriod').querySelectorAll('.pill').forEach(b=>{ if(b.dataset.p==='yesterday') b.style.display=isStores()?'':'none'; });
    if(!isStores() && state.period==='yesterday'){
      state.period='wtd';
    }
    // keep the period pills' active state in sync with state.period (covers 3P->YTD etc.)
    $('#fPeriod').querySelectorAll('.pill').forEach(b=>{ b.classList.toggle('on', b.dataset.p===state.period); });
    const stores_view=isStores(), selling=isSelling();
    const combined = state.store==='__ALL__';
    const st = getBlob();
    const strip=$('#strip'); strip.innerHTML='';
    if(!st){strip.append(el('h2',null,'No data'));$('#body').innerHTML='';return;}
    strip.append(el('h2',null, combined ? `${state.country} — All ${stores_view?'Stores':VIEW_LABEL[state.view]}` : state.store));
    if(combined){
      const n=getRankRows().rows.length;
      strip.append(el('span','chip',`${n} ${VIEW_NOUN[state.view]} combined`));
    }
    strip.append(el('span','chip',st.country||state.country));
    strip.append(el('span','chip rk',`${periodLabel[state.period]}`));
    if(!stores_view){ strip.append(el('span','chip', selling?'sales · inventory':'inventory only')); }
    // budget + LFL toggles: Stores only
    if(stores_view){
      const bb=state.budgetBasis||'rebudget';
      const bt=el('button','lflbtn'+(bb==='original'?' on':''), bb==='rebudget'?'Re-Budget':'Orig Budget');
      bt.title='Toggle budget basis: Re-Budget (revised) vs Original Budget';
      bt.onclick=()=>{ state.budgetBasis = (bb==='rebudget'?'original':'rebudget'); render(); };
      strip.append(bt);
      if(st.kpi_lfl){
        const lblOn = state.lfl;
        const t=el('button','lflbtn'+(lblOn?' on':''), lblOn?'LFL ✓':'LFL');
        t.title='Like-for-like: compare only against periods where the store(s) were trading last year';
        t.onclick=()=>{ state.lfl=!state.lfl; render(); };
        strip.append(t);
        if(lblOn){
          const kl=st.kpi_lfl[state.period]||{};
          if(combined){ const ls=kl.lfl_stores; if(ls!=null) strip.append(el('span','chip',`${ls} comparable stores`)); }
          else { strip.append(el('span','chip', kl.comparable ? 'comparable to LY' : 'no LY comparison')); }
        }
      }
    }
    piMountPill();
    DIAG.failed=0;
    const body=$('#body'); body.innerHTML='';
    // ---- KPI / sales / inventory strip ----
    if(stores_view){ body.append(kpiStrip(st)); }
    else if(selling){ body.append(channelStrip(st)); }
    else { body.append(inventoryStrip(st)); }
    // ---- country performance (Stores · All Countries only) ----
    if(stores_view && combined && state.country==='All Countries'){
      const cp=el('div','grid'); cp.append(countryPerfCard()); body.append(cp);
    }
    // ---- weekly trend charts (Stores only) ----
    if(stores_view){
      const tg=el('div','grid g2'); tg.append(weeklySalesCard()); tg.append(weeklyKpiCard()); body.append(tg);
    }
    // ---- Ecom availability ----
    if(state.view==='Ecom'){ const av=el('div','grid'); av.append(ecomAvailabilityCard()); body.append(av); }
    let diag=$('#diagbar');
    if(!diag){ diag=el('div','diagbar'); diag.id='diagbar';
      diag.innerHTML=`<span>⚠ <b id="diagcount">0</b> product image(s) have a valid link but couldn't load in this preview — this is a local-file limitation; they load normally on Shopify.</span>`+
        `<span class="diagkey"><span class="sw fail"></span>link failed here</span>`+
        `<span class="diagkey"><span class="sw logo"></span>no link on file</span>`;
      $('#strip').after(diag);
    }
    diag.classList.remove('show');
    // ---- sellers: selling views only ----
    if(selling){
      body.append(sellerFilterBar(st));
      const g1=el('div','grid g2');
      const scope = stores_view ? 'Country' : VIEW_LABEL[state.view];
      g1.append(sellerCard(combined?'Top 10 Sellers — '+scope:'Top 10 Sellers','top',rankTop(st.items||[])));
      g1.append(sellerCard(combined?'Bottom 10 Sellers — '+scope:'Bottom 10 Sellers','bot',rankBottom(st.items||[])));
      body.append(g1);
    }
    // ---- Category Performance: OWN full-width row ----
    // At half width the 10-column period table overflowed and had to be scrolled sideways to
    // read Avg Markdown / GP% / the stock columns. Full width fits them all.
    const gmix=el('div','grid');
    gmix.append(mixCard(st, selling));
    body.append(gmix);
    // ---- the two Store-to-Store In-Transit views, SIDE BY SIDE ----
    // Same ERP source (In Transit Qty), two lenses: by category, and the top 10 individual items.
    // They belong beside each other so a category spike can be read against the styles driving it.
    const gtr=el('div','grid g2');
    gtr.append(transitCard(st));
    gtr.append(transitItemsCard(st));
    body.append(gtr);
    // ---- location ranking + inbound shipments ----
    // Inbound Shipments is ADDITIVE — it never replaces an in-transit card. It renders ONLY on
    // All Countries / All Stores: the tracker carries no location key, so under any narrower
    // selection it would show global figures while appearing to be scoped. It is also a DIFFERENT
    // SUPPLY-CHAIN STAGE from Store-to-Store In-Transit (vessels not yet landed vs stock already
    // moving between locations) — roughly 25x apart — hence the distinct title and caption.
    const allAll = stores_view && combined && state.country==='All Countries';
    const showShip = !!(allAll && D.shipments);
    const g3=el('div','grid'+(showShip?' g2':''));
    if(stores_view){
      if(combined && state.country==='All Countries' && !state.showStores){ g3.append(countryRankCard()); }
      else { g3.append(combined ? storesRankCard(st) : rankCard(st)); }
    } else {
      g3.append(viewRankCard());
    }
    if(showShip) g3.append(shipmentCard());
    body.append(g3);
    // ---- inventory snapshot ----
    body.append(snapSection(st));
    // ---- broken size (Stores only) ----
    if(stores_view){ const bk=el('div','grid'); bk.append(brokenSizeCard()); body.append(bk); }
  }
  if(DATA_URL && DATA_URL.indexOf('PASTE_YOUR')===-1){
    skStart();
    var bust = (DATA_URL.indexOf('?')===-1?'?':'&')+'t='+Date.now();
    fetch(DATA_URL+bust,{cache:'no-store'}).then(r=>{ if(!r.ok) throw new Error('HTTP '+r.status); return r.text(); })
      .then(txt=>{
        try{
          var t=txt.trim();
          var i=t.indexOf('{');
          if(t.slice(-1)===';') t=t.slice(0,-1);
          var jsonStr=(i>0)? t.slice(i) : t;
          var data=JSON.parse(jsonStr);
          boot(data);
        }catch(e){ skFail('Data parse error: '+e.message); }
      })
      .catch(e=>{ skFail('Could not load data file ('+e.message+'). Check the Files URL.'); });
  } else if(window.DASHBOARD_DATA){ boot(window.DASHBOARD_DATA); }
  else { skFail('No data source. Include payload.js or set DATA_URL.'); }
})();
</script>

{% endraw %}
