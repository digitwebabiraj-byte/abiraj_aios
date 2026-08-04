# -*- coding: utf-8 -*-
"""REQ-23-D01 Fast Moving Products — self-contained HTML dashboard generator.
Reads the governed payload JSON, computes the same derived fields as the Excel builder,
and emits one standalone light-theme HTML (no external requests)."""
import json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "fmp_payload.json"), encoding="utf-8"))
M = P["meta"]

def aoq(q, o): return round(q / o, 2) if o else 0.0
def scd(stock, q):
    d = q / 30.0
    return None if d <= 0 else round(stock / d)
def trend(q30, q90):
    d30, d90 = q30 / 30.0, q90 / 90.0
    if d90 <= 0: return "New"
    r = d30 / d90
    return "Growing" if r >= 1.30 else ("Stable" if r >= 0.80 else "Slowing")
def action(stock, s, t):
    if stock == 0: return "Restock immediately"
    if s is not None and s < 30: return "Reorder soon"
    if s is not None and s <= 90: return "Promote / keep stock" if t == "Growing" else "Maintain stock"
    if s is not None and s > 365: return "Overstocked – review"
    if t == "Slowing" and s is not None and s > 180: return "Slow – reduce buying"
    return "Monitor"
def decision(stock, s):
    if stock == 0: return "Restock immediately"
    if s is not None and s < 30: return "Restock soon"
    if s is not None and s <= 90: return "Maintain stock"
    if s is not None and s > 365: return "Overstocked – review"
    return "Sufficient stock"

def enrich_channel(rows, id_label):
    out = []
    for i, r in enumerate(rows, 1):
        s = scd(r["current_stock"], r["qty30"]); t = trend(r["qty30"], r["qty90"])
        out.append({"rank": i, "sku": r["sku"], "pid": r["product_id"], "title": r["title"] or "",
                    "cat": r["category"], "q30": r["qty30"], "q90": r["qty90"], "rev": float(r["rev30"]),
                    "orders": r["orders30"], "aoq": aoq(r["qty30"], r["orders30"]),
                    "stock": r["current_stock"], "scd": s, "trend": t,
                    "action": action(r["current_stock"], s, t)})
    return out

def enrich_combined(rows):
    out = []
    for i, r in enumerate(rows, 1):
        s = scd(r["current_stock"], r["total_units"])
        out.append({"rank": i, "sku": r["sku"], "title": r["title"] or "", "cat": r["category"],
                    "amz": r["amz"], "ebay": r["ebay"], "shop": r["shop"], "units": r["total_units"],
                    "rev": float(r["total_rev"]), "stock": r["current_stock"], "scd": s,
                    "decision": decision(r["current_stock"], s)})
    return out

DATA = {
    "shopify": enrich_channel(P["shopify"], "Product ID"),
    "amazon":  enrich_channel(P["amazon"], "ASIN"),
    "ebay":    enrich_channel(P["ebay"], "Listing ID"),
    "combined": enrich_combined(P["combined"]),
}
BLOB = json.dumps(DATA, ensure_ascii=False)

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fast Moving Products — Germany · REQ-23-D01</title>
<style>
:root{
  --bg1:#eef3fb; --bg2:#f7f9fd; --card:#ffffff; --ink:#1f2d3d; --muted:#67788c;
  --line:#e4ebf5; --brand:#2e5496; --brand2:#4f7fd6; --accent:#0ea5a4;
  --grow:#1a9e5f; --growbg:#e6f7ee; --stab:#8a6d1d; --stabbg:#fbf3dc;
  --slow:#c2410c; --slowbg:#fdeadf; --oos:#c62839; --oosbg:#fde8ea;
  --shadow:0 10px 30px rgba(31,45,61,.08),0 2px 6px rgba(31,45,61,.05);
  --radius:16px;
}
*{box-sizing:border-box}
html,body{margin:0}
body{font-family:'Segoe UI',Roboto,Helvetica,Arial,system-ui,sans-serif;color:var(--ink);
  background:linear-gradient(135deg,var(--bg1),var(--bg2) 60%);min-height:100vh;padding:26px;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1320px;margin:0 auto}
header.hero{background:linear-gradient(120deg,var(--brand),var(--brand2));color:#fff;border-radius:22px;
  padding:26px 30px;box-shadow:var(--shadow);position:relative;overflow:hidden;animation:drop .6s ease}
header.hero::after{content:"";position:absolute;right:-60px;top:-60px;width:240px;height:240px;
  background:radial-gradient(circle,rgba(255,255,255,.18),transparent 70%);border-radius:50%}
.hero h1{margin:0;font-size:26px;letter-spacing:.2px;font-weight:800}
.hero p{margin:8px 0 0;opacity:.92;font-size:13.5px;max-width:820px;line-height:1.5}
.badges{margin-top:14px;display:flex;gap:8px;flex-wrap:wrap}
.pill{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.28);padding:5px 12px;
  border-radius:999px;font-size:12px;font-weight:600;backdrop-filter:blur(4px)}
.fsbtn{position:absolute;right:22px;top:22px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.35);
  color:#fff;border-radius:10px;padding:8px 14px;font-size:12.5px;font-weight:600;cursor:pointer;transition:.2s}
.fsbtn:hover{background:rgba(255,255,255,.30)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:22px 0}
.kpi{background:var(--card);border-radius:var(--radius);padding:18px 20px;box-shadow:var(--shadow);
  border:1px solid var(--line);position:relative;animation:rise .5s ease both}
.kpi:nth-child(2){animation-delay:.06s}.kpi:nth-child(3){animation-delay:.12s}.kpi:nth-child(4){animation-delay:.18s}
.kpi .lab{font-size:12px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.kpi .val{font-size:30px;font-weight:800;margin-top:6px;color:var(--brand);font-variant-numeric:tabular-nums}
.kpi .sub{font-size:12px;color:var(--muted);margin-top:2px}
.kpi .bar{height:4px;border-radius:4px;margin-top:12px;background:linear-gradient(90deg,var(--brand),var(--accent));
  transform-origin:left;animation:grow .8s ease both}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:4px 0 16px}
.tab{background:var(--card);border:1px solid var(--line);color:var(--muted);padding:10px 18px;border-radius:12px;
  font-weight:700;font-size:13.5px;cursor:pointer;transition:.2s;box-shadow:0 1px 3px rgba(31,45,61,.05)}
.tab:hover{color:var(--brand);border-color:var(--brand2)}
.tab.active{background:linear-gradient(120deg,var(--brand),var(--brand2));color:#fff;border-color:transparent;
  box-shadow:0 6px 16px rgba(46,84,150,.28)}
.toolbar{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px;flex-wrap:wrap}
.search{flex:1;min-width:220px;position:relative}
.search input{width:100%;padding:11px 14px 11px 38px;border:1px solid var(--line);border-radius:12px;font-size:14px;
  background:var(--card);color:var(--ink);outline:none;transition:.2s}
.search input:focus{border-color:var(--brand2);box-shadow:0 0 0 3px rgba(79,127,214,.15)}
.search svg{position:absolute;left:12px;top:11px;opacity:.5}
.hint{font-size:12px;color:var(--muted)}
.panel{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);border:1px solid var(--line);
  overflow:hidden;animation:fade .4s ease}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{position:sticky;top:0;background:#f2f6fc;color:var(--brand);text-align:left;padding:12px 12px;
  font-weight:700;font-size:12px;white-space:nowrap;cursor:pointer;user-select:none;border-bottom:2px solid var(--line)}
thead th:hover{background:#e8f0fb}
thead th .ar{opacity:.4;font-size:10px;margin-left:4px}
tbody td{padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:middle}
tbody tr{animation:fade .3s ease both}
tbody tr:hover{background:#f7faff}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.sku{font-family:'Consolas','SF Mono',monospace;font-size:12px;color:var(--brand)}
.pid{font-family:'Consolas','SF Mono',monospace;font-size:11.5px;color:var(--muted)}
.title{max-width:340px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rank{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:8px;
  background:#eef3fb;color:var(--brand);font-weight:800;font-size:12px}
.rank.top{background:linear-gradient(120deg,var(--brand),var(--brand2));color:#fff}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:11.5px;font-weight:700;white-space:nowrap}
.b-grow{background:var(--growbg);color:var(--grow)} .b-stab{background:var(--stabbg);color:var(--stab)}
.b-slow{background:var(--slowbg);color:var(--slow)} .b-new{background:#eef3fb;color:var(--brand)}
.act{font-size:12px;font-weight:600;white-space:nowrap}
tr.oos td{background:var(--oosbg) !important}
tr.oos .stockcell{color:var(--oos);font-weight:800}
.chip{display:inline-block;padding:2px 8px;border-radius:6px;background:#eef3fb;color:var(--muted);font-size:11px}
footer{margin:22px 2px 6px;color:var(--muted);font-size:12px;line-height:1.6}
.count{font-size:12px;color:var(--muted);padding:10px 14px;border-top:1px solid var(--line);background:#fafcff}
@keyframes drop{from{opacity:0;transform:translateY(-14px)}to{opacity:1;transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
:fullscreen .wrap{max-width:1600px}
@media(max-width:820px){.kpis{grid-template-columns:repeat(2,1fr)}body{padding:14px}}
</style></head>
<body><div class="wrap">
<header class="hero">
  <button class="fsbtn" onclick="fs()">⛶ Full screen</button>
  <h1>Fast Moving Products — Germany 🇩🇪</h1>
  <p>Channel-wise top-selling products across Shopify DE, Amazon DE and eBay DE, plus a combined all-channel roll-up. Ranked by 30-day units sold; live warehouse data, per-product revenue in EUR.</p>
  <div class="badges">
    <span class="pill">REQ-23-D01 · code fmp</span>
    <span class="pill">30-day: __W30__ → __WE__</span>
    <span class="pill">90-day: __W90__ → __WE__</span>
    <span class="pill">Currency €</span>
    <span class="pill">Data pulled __GEN__</span>
  </div>
</header>
<div class="kpis" id="kpis"></div>
<div class="tabs" id="tabs"></div>
<div class="toolbar">
  <div class="search"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
    <input id="q" placeholder="Search SKU, product name, category, product ID…"></div>
  <div class="hint">Click any column header to sort · out-of-stock rows in red</div>
</div>
<div class="panel"><div class="scroll"><table><thead id="thead"></thead><tbody id="tbody"></tbody></table></div>
  <div class="count" id="count"></div></div>
<footer>
  <b>Sources:</b> public.order_transaction · listing_data · inv_products · location_wise_inv_stock (curated warehouse, read-only). <b>Revenue</b> = item_price × quantity (EUR, per-product). <b>Stock Cover Days</b> = Current Stock ÷ (30-day units ÷ 30). <b>Trend</b> = 30-day daily rate vs 90-day daily rate (≥1.30 Growing · 0.80–1.30 Stable · &lt;0.80 Slowing). <b>Action / Final Decision</b> = documented default rules pending Mahima's sign-off. Category coverage ~74%; some eBay/Shopify variant titles are short labels.
</footer>
</div>
<script>
const DATA=__BLOB__;
const TABS=[
 {k:'shopify',label:'Shopify DE'},{k:'amazon',label:'Amazon DE'},
 {k:'ebay',label:'eBay DE'},{k:'combined',label:'Combined'}];
const COLS={
 channel:[['rank','#','n'],['sku','SKU','t'],['pid','Product ID','t'],['title','Product Name','t'],
   ['cat','Category','t'],['q30','Sold 30d','n'],['q90','Sold 90d','n'],['rev','Revenue €','m'],
   ['orders','Orders','n'],['aoq','Avg Ord Qty','n'],['stock','Stock','n'],['scd','Cover Days','n'],
   ['trend','Trend','badge'],['action','Action','act']],
 combined:[['rank','#','n'],['sku','SKU','t'],['title','Product Name','t'],['cat','Category','t'],
   ['amz','Amazon','n'],['ebay','eBay','n'],['shop','Shopify','n'],['units','Total Units','n'],
   ['rev','Total Rev €','m'],['stock','Stock','n'],['scd','Cover Days','n'],['decision','Final Decision','act']]};
let cur='shopify', sortKey=null, sortDir=1;
const eur=v=>'€'+Number(v).toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function cols(){return cur==='combined'?COLS.combined:COLS.channel}
function badge(t){const m={Growing:['b-grow','↑ Growing'],Stable:['b-stab','Stable'],Slowing:['b-slow','↓ Slowing'],New:['b-new','New']};const x=m[t]||m.New;return '<span class="badge '+x[0]+'">'+x[1]+'</span>';}
function kpis(){
 const rows=DATA[cur]; const box=document.getElementById('kpis');
 const uKey=cur==='combined'?'units':'q30';
 const units=rows.reduce((a,r)=>a+r[uKey],0);
 const rev=rows.reduce((a,r)=>a+r.rev,0);
 const oos=rows.filter(r=>r.stock===0).length;
 const K=[['Products (top)',rows.length,'ranked SKUs'],
   ['Units sold (30d)',units.toLocaleString('en-GB'),'across shown products'],
   ['Revenue (30d)',eur(rev),'item revenue, EUR'],
   ['Out of stock',oos,'need restock']];
 box.innerHTML=K.map(k=>`<div class="kpi"><div class="lab">${k[0]}</div><div class="val">${k[1]}</div><div class="sub">${k[2]}</div><div class="bar"></div></div>`).join('');
}
function head(){
 document.getElementById('thead').innerHTML='<tr>'+cols().map(c=>{
   const ar=sortKey===c[0]?(sortDir>0?'▲':'▼'):'';
   const cls=(c[2]==='n'||c[2]==='m')?'num':'';
   return `<th class="${cls}" onclick="sortBy('${c[0]}')">${c[1]}<span class="ar">${ar}</span></th>`;}).join('')+'</tr>';
}
function rowsFiltered(){
 let r=DATA[cur].slice(); const q=document.getElementById('q').value.toLowerCase().trim();
 if(q) r=r.filter(o=>[o.sku,o.title,o.cat,o.pid].filter(Boolean).some(v=>String(v).toLowerCase().includes(q)));
 if(sortKey){r.sort((a,b)=>{let x=a[sortKey],y=b[sortKey];
   if(x===null)x=-1;if(y===null)y=-1;
   if(typeof x==='number'&&typeof y==='number')return (x-y)*sortDir;
   return String(x).localeCompare(String(y))*sortDir;});}
 return r;
}
function body(){
 const rs=rowsFiltered();
 document.getElementById('tbody').innerHTML=rs.map((o,i)=>{
   const oos=o.stock===0?' class="oos"':'';
   const tds=cols().map(c=>{
     const k=c[0],ty=c[2];let v=o[k];
     if(k==='rank')return `<td><span class="rank ${o.rank<=3?'top':''}">${o.rank}</span></td>`;
     if(k==='sku')return `<td><span class="sku">${esc(v)}</span></td>`;
     if(k==='pid')return `<td><span class="pid">${esc(v)}</span></td>`;
     if(k==='title')return `<td class="title" title="${esc(v)}">${esc(v)}</td>`;
     if(k==='cat')return `<td><span class="chip">${esc(v)}</span></td>`;
     if(ty==='badge')return `<td>${badge(v)}</td>`;
     if(ty==='act')return `<td class="act">${esc(v)}</td>`;
     if(ty==='m')return `<td class="num">${eur(v)}</td>`;
     if(k==='stock')return `<td class="num stockcell">${v.toLocaleString('en-GB')}</td>`;
     if(k==='scd')return `<td class="num">${v===null?'—':v.toLocaleString('en-GB')}</td>`;
     if(ty==='n')return `<td class="num">${typeof v==='number'?v.toLocaleString('en-GB'):esc(v)}</td>`;
     return `<td>${esc(v)}</td>`;
   }).join('');
   return `<tr${oos} style="animation-delay:${Math.min(i*18,500)}ms">${tds}</tr>`;
 }).join('');
 document.getElementById('count').textContent=`Showing ${rs.length} of ${DATA[cur].length} products`;
}
function render(){kpis();head();body();}
function sortBy(k){if(sortKey===k)sortDir*=-1;else{sortKey=k;sortDir=(k==='rank')?1:-1;}render();}
function setTab(k){cur=k;sortKey=null;sortDir=1;
 document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t.dataset.k===k));render();}
function fs(){const e=document.documentElement;if(!document.fullscreenElement)e.requestFullscreen&&e.requestFullscreen();else document.exitFullscreen();}
document.getElementById('tabs').innerHTML=TABS.map((t,i)=>`<div class="tab ${i===0?'active':''}" data-k="${t.k}" onclick="setTab('${t.k}')">${t.label}</div>`).join('');
document.getElementById('q').addEventListener('input',body);
render();
</script>
</body></html>"""

HTML = (HTML.replace("__BLOB__", BLOB).replace("__W30__", M["win30_start"]).replace("__W90__", M["win90_start"])
        .replace("__WE__", M["win_end"]).replace("__GEN__", M["generated"]))
out = os.path.join(HERE, "REQ-23-D01_fast_moving_products.html")
open(out, "w", encoding="utf-8").write(HTML)
print("saved:", out, len(HTML), "bytes")
