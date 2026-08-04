# -*- coding: utf-8 -*-
"""REQ-23-D01 Fast Moving Products — self-contained HTML dashboard generator.
Reads the governed payload JSON, computes the same derived fields as the Excel builder,
and emits one standalone light-theme HTML (no external requests)."""
import json, os

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

def enrich_channel(rows):
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

DATA = {"shopify": enrich_channel(P["shopify"]), "amazon": enrich_channel(P["amazon"]),
        "ebay": enrich_channel(P["ebay"]), "combined": enrich_combined(P["combined"])}
BLOB = json.dumps(DATA, ensure_ascii=False)

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fast Moving Products — Germany · REQ-23-D01</title>
<style>
:root{
  --bg:#f2f6f4; --card:#ffffff; --ink:#152b2a; --muted:#5f7472; --line:#e3ece9;
  --brand:#0d9488; --brand2:#14b8a6; --sky:#0891b2; --accent:#f59e0b;
  --grow:#047857; --growbg:#d4f5e4; --stab:#b45309; --stabbg:#fdeecb;
  --slow:#e11d48; --slowbg:#ffe1e8; --oos:#e11d48; --oosbg:#fff0f3;
  --zebra:#f5faf8; --hover:#eafaf4;
  --shadow:0 10px 34px rgba(15,60,55,.09),0 2px 8px rgba(15,60,55,.05); --radius:14px;
}
*{box-sizing:border-box} html,body{margin:0}
body{font-family:'Segoe UI',Roboto,Helvetica,Arial,system-ui,sans-serif;color:var(--ink);
  background:radial-gradient(1000px 460px at 8% -10%,rgba(20,184,166,.16),transparent 55%),
    radial-gradient(900px 460px at 100% -6%,rgba(245,158,11,.12),transparent 52%),var(--bg);
  background-attachment:fixed;min-height:100vh;padding:14px clamp(12px,2vw,30px);-webkit-font-smoothing:antialiased}
.wrap{width:100%;max-width:none;margin:0}
header.hero{background:linear-gradient(115deg,#134e4a 0%,#0f766e 38%,#0d9488 70%,#14b8a6 108%);
  color:#fff;border-radius:16px;padding:14px 22px;box-shadow:0 12px 34px rgba(13,148,136,.30);
  position:relative;overflow:hidden;animation:drop .5s ease;display:flex;align-items:center;
  justify-content:space-between;gap:16px;flex-wrap:wrap}
.hero h1{margin:0;font-size:20px;font-weight:800;letter-spacing:.2px}
.hero .sub{font-size:11.5px;opacity:.9;margin-top:2px;max-width:660px}
.badges{display:flex;gap:7px;flex-wrap:wrap;margin-top:7px}
.pill{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.30);padding:3px 10px;
  border-radius:999px;font-size:11px;font-weight:600}
.fsbtn{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.42);color:#fff;border-radius:10px;
  padding:8px 14px;font-size:12px;font-weight:700;cursor:pointer;transition:.2s;white-space:nowrap}
.fsbtn:hover{background:rgba(255,255,255,.32)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:12px 0}
.kpi{border-radius:12px;padding:11px 15px;color:#fff;position:relative;overflow:hidden;box-shadow:var(--shadow);
  display:flex;flex-direction:column;justify-content:center;min-height:64px;animation:rise .45s ease both}
.kpi.k0{background:linear-gradient(135deg,#0f766e,#14b8a6)}
.kpi.k1{background:linear-gradient(135deg,#0e7490,#22d3ee)}
.kpi.k2{background:linear-gradient(135deg,#b45309,#f59e0b)}
.kpi.k3{background:linear-gradient(135deg,#be123c,#fb7185)}
.kpi:nth-child(2){animation-delay:.05s}.kpi:nth-child(3){animation-delay:.1s}.kpi:nth-child(4){animation-delay:.15s}
.kpi .lab{font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;opacity:.9}
.kpi .val{font-size:23px;font-weight:800;line-height:1.15;font-variant-numeric:tabular-nums}
.kpi .sub{font-size:10.5px;opacity:.82}
.tabs{display:flex;gap:7px;flex-wrap:wrap;margin:2px 0 10px}
.tab{background:var(--card);border:1px solid var(--line);color:var(--muted);padding:8px 18px;border-radius:11px;
  font-weight:700;font-size:13px;cursor:pointer;transition:.18s;box-shadow:0 1px 4px rgba(31,41,80,.05)}
.tab:hover{color:var(--brand);border-color:var(--brand2)}
.tab.active{background:linear-gradient(120deg,var(--brand),var(--brand2));color:#fff;border-color:transparent;
  box-shadow:0 8px 18px rgba(13,148,136,.32)}
.filters{display:flex;gap:9px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
.search{flex:1;min-width:220px;position:relative}
.search input{width:100%;padding:10px 14px 10px 38px;border:1px solid var(--line);border-radius:11px;font-size:13.5px;
  background:var(--card);color:var(--ink);outline:none;transition:.2s;box-shadow:0 1px 4px rgba(31,41,80,.04)}
.search input:focus{border-color:var(--brand2);box-shadow:0 0 0 3px rgba(20,184,166,.18)}
.search svg{position:absolute;left:13px;top:11px;opacity:.5}
select.fil{padding:10px 12px;border:1px solid var(--line);border-radius:11px;font-size:13px;background:var(--card);
  color:var(--ink);cursor:pointer;outline:none;transition:.2s;font-weight:600}
select.fil:focus{border-color:var(--brand2);box-shadow:0 0 0 3px rgba(20,184,166,.18)}
.clr{padding:10px 14px;border:1px solid var(--line);border-radius:11px;font-size:12.5px;font-weight:700;
  background:var(--card);color:var(--muted);cursor:pointer;transition:.2s}
.clr:hover{color:var(--brand);border-color:var(--brand2)}
.panel{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);border:1px solid var(--line);
  overflow:hidden;animation:fade .35s ease}
.scroll{overflow-x:auto;max-height:calc(100vh - 232px)}
:fullscreen .scroll{max-height:calc(100vh - 208px)}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{position:sticky;top:0;z-index:1;background:linear-gradient(180deg,#0f766e,#0d9488);color:#eafff9;
  text-align:left;padding:12px 12px;font-weight:700;font-size:11.5px;white-space:nowrap;cursor:pointer;
  user-select:none;border-bottom:2px solid #0b6157}
thead th:hover{background:#0b6157} thead th .ar{opacity:.7;font-size:9px;margin-left:3px}
tbody td{padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:middle}
tbody tr{animation:fade .25s ease both}
tbody tr:nth-child(even){background:var(--zebra)}
tbody tr:hover{background:var(--hover)}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.sku{font-family:'Consolas','SF Mono',monospace;font-size:11.5px;color:#0d9488;font-weight:600}
.pid{font-family:'Consolas','SF Mono',monospace;font-size:11px;color:var(--muted)}
.title{max-width:340px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rank{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:8px;
  background:#d6f3ec;color:#0b6157;font-weight:800;font-size:12px}
.rank.top{background:linear-gradient(135deg,#f59e0b,#14b8a6);color:#fff;box-shadow:0 3px 8px rgba(13,148,136,.30)}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:700;white-space:nowrap}
.b-grow{background:var(--growbg);color:var(--grow)} .b-stab{background:var(--stabbg);color:var(--stab)}
.b-slow{background:var(--slowbg);color:var(--slow)} .b-new{background:#d6f3ec;color:var(--brand)}
.act{font-size:12px;font-weight:600;white-space:nowrap;color:#334b49}
tr.oos td{background:var(--oosbg) !important} tr.oos .stockcell{color:var(--oos);font-weight:800}
.chip{display:inline-block;padding:2px 9px;border-radius:7px;background:#e4f4f0;color:#0b6157;font-size:10.5px;font-weight:600}
.count{font-size:12px;color:var(--muted);padding:10px 14px;border-top:1px solid var(--line);
  background:linear-gradient(180deg,#f8fbfa,#f1f8f5)}
footer{margin:14px 4px 6px;color:var(--muted);font-size:11.5px;line-height:1.55}
@keyframes drop{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.kpis{grid-template-columns:1fr}}
</style></head>
<body><div class="wrap">
<header class="hero">
  <div>
    <h1>Fast Moving Products — Germany 🇩🇪</h1>
    <div class="sub">Channel-wise top sellers · Shopify / Amazon / eBay DE + combined · ranked by 30-day units · EUR</div>
    <div class="badges">
      <span class="pill">REQ-23-D01 · fmp</span>
      <span class="pill">30d __W30__ → __WE__</span>
      <span class="pill">90d __W90__ → __WE__</span>
      <span class="pill">Data __GEN__</span>
    </div>
  </div>
  <button class="fsbtn" onclick="fs()">⛶ Full screen</button>
</header>
<div class="kpis" id="kpis"></div>
<div class="tabs" id="tabs"></div>
<div class="filters">
  <div class="search"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
    <input id="q" placeholder="Search SKU, product name, product ID…"></div>
  <select class="fil" id="fCat"><option value="">All categories</option></select>
  <select class="fil" id="fTrend"><option value="">All trends</option><option>Growing</option><option>Stable</option><option>Slowing</option></select>
  <select class="fil" id="fStock"><option value="">All stock</option><option value="in">In stock</option><option value="out">Out of stock</option><option value="low">Low cover (&lt;30d)</option></select>
  <button class="clr" onclick="clearFilters()">Clear</button>
</div>
<div class="panel"><div class="scroll"><table><thead id="thead"></thead><tbody id="tbody"></tbody></table></div>
  <div class="count" id="count"></div></div>
<footer>
  <b>Sources:</b> order_management.orders + order_item_info + sub_source/source · inventory.products + local_inventory_current_stock_location_wise (raw mcp.ledsone DB, read-only). Product Name &amp; Category are curated catalog labels carried by SKU. <b>Revenue</b> = item_price × quantity (EUR). <b>Cover Days</b> = Stock ÷ (30-day units ÷ 30). <b>Trend/Action</b> = documented default rules pending Mahima's sign-off.
</footer>
</div>
<script>
const DATA=__BLOB__;
const TABS=[{k:'shopify',label:'Shopify DE'},{k:'amazon',label:'Amazon DE'},{k:'ebay',label:'eBay DE'},{k:'combined',label:'Combined'}];
const COLS={
 channel:[['rank','#','n'],['sku','SKU','t'],['pid','Product ID','t'],['title','Product Name','t'],['cat','Category','t'],['q30','Sold 30d','n'],['q90','Sold 90d','n'],['rev','Revenue €','m'],['orders','Orders','n'],['aoq','Avg Ord Qty','n'],['stock','Stock','n'],['scd','Cover Days','n'],['trend','Trend','badge'],['action','Action','act']],
 combined:[['rank','#','n'],['sku','SKU','t'],['title','Product Name','t'],['cat','Category','t'],['amz','Amazon','n'],['ebay','eBay','n'],['shop','Shopify','n'],['units','Total Units','n'],['rev','Total Rev €','m'],['stock','Stock','n'],['scd','Cover Days','n'],['decision','Final Decision','act']]};
let cur='shopify',sortKey=null,sortDir=1;
const eur=v=>'€'+Number(v).toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const isCombined=()=>cur==='combined';
function cols(){return isCombined()?COLS.combined:COLS.channel}
function badge(t){const m={Growing:['b-grow','↑ Growing'],Stable:['b-stab','Stable'],Slowing:['b-slow','↓ Slowing'],New:['b-new','New']};const x=m[t]||m.New;return '<span class="badge '+x[0]+'">'+x[1]+'</span>';}
function kpis(){
 const rows=DATA[cur],box=document.getElementById('kpis'),uKey=isCombined()?'units':'q30';
 const units=rows.reduce((a,r)=>a+r[uKey],0),rev=rows.reduce((a,r)=>a+r.rev,0),oos=rows.filter(r=>r.stock===0).length;
 const K=[['Products (top)',rows.length,'ranked SKUs'],['Units sold (30d)',units.toLocaleString('en-GB'),'shown products'],['Revenue (30d)',eur(rev),'item revenue, EUR'],['Out of stock',oos,'need restock']];
 box.innerHTML=K.map((k,i)=>`<div class="kpi k${i}"><div class="lab">${k[0]}</div><div class="val">${k[1]}</div><div class="sub">${k[2]}</div></div>`).join('');
}
function populateFilters(){
 const cats=[...new Set(DATA[cur].map(r=>r.cat).filter(Boolean))].sort();
 document.getElementById('fCat').innerHTML='<option value="">All categories</option>'+cats.map(c=>`<option>${esc(c)}</option>`).join('');
 document.getElementById('fTrend').style.display=isCombined()?'none':'';
}
function head(){
 document.getElementById('thead').innerHTML='<tr>'+cols().map(c=>{
   const ar=sortKey===c[0]?(sortDir>0?'▲':'▼'):'';const cls=(c[2]==='n'||c[2]==='m')?'num':'';
   return `<th class="${cls}" onclick="sortBy('${c[0]}')">${c[1]}<span class="ar">${ar}</span></th>`;}).join('')+'</tr>';
}
function rowsFiltered(){
 let r=DATA[cur].slice();
 const q=document.getElementById('q').value.toLowerCase().trim();
 const cat=document.getElementById('fCat').value,tr=document.getElementById('fTrend').value,st=document.getElementById('fStock').value;
 if(q)r=r.filter(o=>[o.sku,o.title,o.pid].filter(Boolean).some(v=>String(v).toLowerCase().includes(q)));
 if(cat)r=r.filter(o=>o.cat===cat);
 if(tr&&!isCombined())r=r.filter(o=>o.trend===tr);
 if(st==='out')r=r.filter(o=>o.stock===0);
 else if(st==='in')r=r.filter(o=>o.stock>0);
 else if(st==='low')r=r.filter(o=>o.scd!==null&&o.scd<30);
 if(sortKey)r.sort((a,b)=>{let x=a[sortKey],y=b[sortKey];if(x===null)x=-1;if(y===null)y=-1;
   if(typeof x==='number'&&typeof y==='number')return (x-y)*sortDir;return String(x).localeCompare(String(y))*sortDir;});
 return r;
}
function body(){
 const rs=rowsFiltered();
 document.getElementById('tbody').innerHTML=rs.map((o,i)=>{
   const oos=o.stock===0?' class="oos"':'';
   const tds=cols().map(c=>{const k=c[0],ty=c[2];let v=o[k];
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
     return `<td>${esc(v)}</td>`;}).join('');
   return `<tr${oos} style="animation-delay:${Math.min(i*15,400)}ms">${tds}</tr>`;}).join('');
 document.getElementById('count').textContent=`Showing ${rs.length} of ${DATA[cur].length} products`;
}
function render(){kpis();head();body();}
function sortBy(k){if(sortKey===k)sortDir*=-1;else{sortKey=k;sortDir=(k==='rank')?1:-1;}head();body();}
function clearFilters(){['q','fCat','fTrend','fStock'].forEach(id=>document.getElementById(id).value='');body();}
function setTab(k){cur=k;sortKey=null;sortDir=1;document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t.dataset.k===k));populateFilters();['q','fCat','fTrend','fStock'].forEach(id=>document.getElementById(id).value='');render();}
function fs(){const e=document.documentElement;if(!document.fullscreenElement)e.requestFullscreen&&e.requestFullscreen();else document.exitFullscreen();}
document.getElementById('tabs').innerHTML=TABS.map((t,i)=>`<div class="tab ${i===0?'active':''}" data-k="${t.k}" onclick="setTab('${t.k}')">${t.label}</div>`).join('');
['q','fCat','fTrend','fStock'].forEach(id=>document.getElementById(id).addEventListener('input',body));
populateFilters();render();
</script>
</body></html>"""

HTML = (HTML.replace("__BLOB__", BLOB).replace("__W30__", M["win30_start"]).replace("__W90__", M["win90_start"])
        .replace("__WE__", M["win_end"]).replace("__GEN__", M["generated"]))
out = os.path.join(HERE, "REQ-23-D01_fast_moving_products.html")
open(out, "w", encoding="utf-8").write(HTML)
print("saved:", out, len(HTML), "bytes")
