# Modern dashboard for the FULL-portfolio Table 5 (all ~733 ASINs).
# Input : data_all.json   Output: Table5_Weekly_Stock_Check_Thuwaraga_ALL.html
import json, os
from datetime import date
from collections import Counter

rows = json.load(open("data_all.json", encoding="utf-8"))
TODAY = date.today().strftime("%Y-%m-%d")
FILE_PATH = os.path.abspath("Table5_Weekly_Stock_Check_Thuwaraga_ALL.html")

# refined category splits the SQL's "No Stock / Critical" into real stockouts vs dead listings
def refine(r):
    st = r["stock_status"]; sold = (r["order_count_90"] or 0) > 0; stock = (r["uk_warehouse"] or 0) > 0
    if st == "No Stock / Critical":      return "stockout" if sold else "inactive"
    if st == "No Recent Sales (Idle Stock)": return "idle"
    if st == "Going Out of Stock":       return "going"
    return "healthy"
for r in rows:
    r["cat"] = refine(r)

DATA_JSON = json.dumps(rows, ensure_ascii=False)
counts = Counter(r["cat"] for r in rows)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Weekly Stock Check — Thuwaraga (All ASINs)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --peacock:#13B4CF; --peacock-d:#0B7C90; --ink:#132a30; --muted:#697c82; --faint:#9aabb0;
  --line:#e7ecee; --bg:#eef2f4; --card:#fff;
  --healthy:#13B4CF; --going:#FFEB84; --crit:#F4A6A6; --idle:#9fb3ba; --inactive:#c8ced1;
  --heal-t:#ffffff; --going-t:#fffbe8; --crit-t:#fdeeee; --idle-t:#eef3f5; --inact-t:#f6f7f8;
  --shadow:0 1px 2px rgba(16,40,46,.04),0 8px 24px rgba(16,40,46,.06);
}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(1200px 500px at 90% -10%,rgba(19,180,207,.10),transparent 60%),var(--bg);
  color:var(--ink);font-family:'Inter',-apple-system,Segoe UI,Roboto,Arial,sans-serif;font-size:13px;
  -webkit-font-smoothing:antialiased;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.wrap{max-width:1620px;margin:0 auto;padding:26px 22px 70px;}
h1{font-family:'Poppins';}

.head{position:relative;overflow:hidden;border-radius:18px;color:#fff;padding:24px 30px;
  background:linear-gradient(120deg,#0B7C90,#13B4CF 55%,#3fd0e6);box-shadow:0 10px 30px rgba(11,124,144,.28);}
.head::after{content:"";position:absolute;right:-60px;top:-60px;width:260px;height:260px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.18),transparent 70%);}
.head .tag{display:inline-flex;align-items:center;gap:7px;background:rgba(255,255,255,.16);padding:5px 12px;
  border-radius:20px;font-size:11px;font-weight:600;letter-spacing:.4px;text-transform:uppercase;}
.head .tag .dot{width:7px;height:7px;border-radius:50%;background:#b6ffd9;box-shadow:0 0 0 3px rgba(182,255,217,.25)}
.head h1{margin:13px 0 6px;font-size:22px;font-weight:700;letter-spacing:-.2px;}
.head p{margin:0;opacity:.94;font-size:12.5px;font-weight:400;max-width:820px;}
.head .meta{margin-top:14px;display:flex;flex-wrap:wrap;gap:8px 10px;}
.head .meta span{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.14);padding:5px 11px;
  border-radius:9px;font-size:11.5px;font-weight:500;}
.head .meta b{font-weight:700;opacity:.85;}

.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0;}
.kpi{background:var(--card);border-radius:15px;padding:15px 16px;border:1px solid var(--line);box-shadow:var(--shadow);
  position:relative;transition:transform .15s;}
.kpi[data-f]{cursor:pointer} .kpi[data-f]:hover{transform:translateY(-2px)}
.kpi.active{outline:2px solid var(--peacock);outline-offset:-2px;box-shadow:0 0 0 4px rgba(19,180,207,.12),var(--shadow);}
.kpi .ic{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:15px;background:rgba(19,180,207,.12);}
.kpi.k-stock .ic{background:rgba(214,69,69,.13)} .kpi.k-idle .ic{background:rgba(105,124,130,.14)}
.kpi.k-inact .ic{background:rgba(150,160,165,.16)} .kpi.k-heal .ic{background:rgba(19,180,207,.13)}
.kpi .n{font-size:25px;font-weight:800;line-height:1;margin-top:11px;font-family:'Poppins';letter-spacing:-.5px;}
.kpi .l{font-size:10.5px;color:var(--muted);margin-top:5px;font-weight:600;text-transform:uppercase;letter-spacing:.3px;}
.kpi .bar{height:4px;border-radius:4px;margin-top:10px;background:var(--peacock);opacity:.9;}
.kpi.k-stock .bar{background:#d64545}.kpi.k-idle .bar{background:var(--idle)}
.kpi.k-inact .bar{background:var(--inactive)}.kpi.k-heal .bar{background:var(--healthy)}

.actions{display:flex;flex-wrap:wrap;gap:9px 14px;align-items:center;background:var(--card);border:1px solid var(--line);
  border-radius:14px;padding:12px 18px;margin-bottom:16px;box-shadow:var(--shadow);}
.actions .lead{display:inline-flex;align-items:center;gap:8px;font-weight:700;font-size:13px;}
.actions .pill{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:20px;font-size:11.5px;font-weight:700;cursor:pointer;transition:.12s;}
.actions .pill:hover{filter:brightness(.97);transform:translateY(-1px)}
.actions .pill .d{width:7px;height:7px;border-radius:50%}
.actions .p-stock{background:var(--crit-t);color:#a11b1b}.actions .p-stock .d{background:#a11b1b}
.actions .p-going{background:var(--going-t);color:#7a5c00}.actions .p-going .d{background:#b58900}
.actions .p-idle{background:var(--idle-t);color:#3f5860}.actions .p-idle .d{background:var(--idle)}
.actions .p-leg{background:#fff4dd;color:#8a5a12}.actions .p-leg .d{background:#c78a1e}

.callout{display:flex;gap:13px;background:linear-gradient(90deg,#fffaf0,#fff);border:1px solid #f2e3c4;border-left:5px solid #E0A13C;
  border-radius:14px;padding:13px 18px;margin-bottom:16px;box-shadow:var(--shadow);}
.callout .ai{font-size:19px}.callout h3{margin:0 0 4px;font-size:13.5px;font-weight:600;color:#8a5a12}
.callout p{margin:0;font-size:12.5px;color:#5a5145;line-height:1.55}
.callout code{background:#fff;border:1px solid #eadcbe;padding:1px 6px;border-radius:6px;font-weight:600}

.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:12px;position:sticky;top:0;z-index:5;
  padding:10px;background:rgba(238,242,244,.86);backdrop-filter:blur(8px);border-radius:14px;}
.search{flex:1;min-width:220px;position:relative}
.search input{width:100%;padding:11px 14px 11px 38px;border:1px solid var(--line);border-radius:11px;font-family:inherit;font-size:13px;background:#fff;box-shadow:var(--shadow)}
.search input:focus{outline:none;border-color:var(--peacock);box-shadow:0 0 0 3px rgba(19,180,207,.16)}
.search svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);width:16px;height:16px;fill:#9aabb0}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{border:1px solid var(--line);background:#fff;padding:9px 13px;border-radius:22px;cursor:pointer;font-family:inherit;font-size:12px;font-weight:600;color:var(--muted);transition:.13s;box-shadow:var(--shadow)}
.chip:hover{border-color:var(--peacock);color:var(--ink)} .chip.active{background:var(--ink);color:#fff;border-color:var(--ink)}
.chip .d{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle}
.chip .c{opacity:.6;font-weight:700;margin-left:5px}
.btn{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);background:#fff;padding:9px 14px;border-radius:11px;cursor:pointer;font-family:inherit;font-size:12px;font-weight:600;color:var(--ink);transition:.13s;box-shadow:var(--shadow)}
.btn:hover{border-color:var(--peacock);color:var(--peacock-d)} .btn svg{width:15px;height:15px;fill:currentColor}
.btn.primary{background:var(--ink);color:#fff;border-color:var(--ink)} .btn.primary:hover{background:#0d2126}
.count{font-size:12px;color:var(--muted);margin-left:6px;font-weight:600}

.tablecard{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--shadow)}
.scroll{overflow:auto;max-height:76vh}
table{border-collapse:separate;border-spacing:0;width:100%;min-width:1240px}
thead th{position:sticky;top:0;z-index:2;background:#f0f4f5;color:var(--ink);text-align:left;padding:11px 12px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.3px;border-bottom:2px solid #dbe2e4;white-space:nowrap;cursor:pointer;user-select:none}
thead th:hover{background:#e7edef} thead th .ar{opacity:.3;font-size:9px;margin-left:3px} thead th.sorted{color:var(--peacock-d)} thead th.sorted .ar{opacity:1}
td{padding:9px 12px;border-bottom:1px solid var(--line);font-size:12.5px;white-space:nowrap;vertical-align:middle}
tbody tr:hover td{background:rgba(19,180,207,.06)!important}
.num{text-align:right;font-variant-numeric:tabular-nums}
.sku{font-family:'SFMono-Regular',Consolas,Menlo,monospace;font-size:11.5px;letter-spacing:-.2px}
.dim{color:#9aabb0}.key{font-weight:700}
tr.c-healthy td{background:var(--heal-t)} tr.c-going td{background:var(--going-t)}
tr.c-stockout td{background:var(--crit-t)} tr.c-idle td{background:var(--idle-t)} tr.c-inactive td{background:var(--inact-t);color:#8a969b}
.badge{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;white-space:nowrap}
.badge .bd{width:7px;height:7px;border-radius:50%}
.b-healthy{background:var(--healthy);color:#053b45}.b-healthy .bd{background:#0b7c90}
.b-going{background:var(--going);color:#7a5c00}.b-going .bd{background:#b58900}
.b-stockout{background:var(--crit);color:#6b1414}.b-stockout .bd{background:#a11b1b}
.b-idle{background:#dbe4e7;color:#3f5860}.b-idle .bd{background:var(--idle)}
.b-inactive{background:#e9ecee;color:#6b767b}.b-inactive .bd{background:var(--inactive)}
.days-warn{color:#c0392b;font-weight:800}.days-cap{color:var(--muted);font-weight:600}
.po{display:inline-block;background:#e7f8fb;color:#0b7c90;border:1px solid #bfeaf1;padding:1px 8px;border-radius:20px;font-weight:700;font-size:11px}
.flag{display:inline-block;margin-left:6px;font-size:9px;font-weight:800;color:#8a5a12;background:#fff4dd;border:1px solid #f0d9a8;padding:1px 5px;border-radius:5px;vertical-align:middle}
.foot{margin-top:16px;font-size:11px;color:var(--muted);line-height:1.7}.foot b{font-weight:700;color:#556}
.empty{padding:44px;text-align:center;color:var(--muted)}
@media print{@page{size:A4 landscape;margin:8mm}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .toolbar{display:none}.scroll{max-height:none;overflow:visible}thead th{position:static}.head{border-radius:0}
  .wrap{max-width:none;padding:0}td,thead th{font-size:8.5px;padding:4px 6px}table{min-width:0}}
</style>
</head>
<body>
<div class="wrap">
  <div class="head">
    <span class="tag"><span class="dot"></span>T5 · High Priority · Full Portfolio · Weekly (Mondays)</span>
    <h1>Weekly Stock Check — Thuwaraga · All Amazon UK ASINs</h1>
    <p>Every ASIN with a live FBM listing or a sale in the last 90 days. Real UK-warehouse stock for all; velocity &amp; days-of-stock only where there are sales; items with stock but no recent sales are flagged idle.</p>
    <div class="meta">
      <span><b>PH</b> Thuwaraga</span><span><b>Channel</b> Amazon UK · FBM</span>
      <span><b>Window</b> Last 90 days</span><span><b>Generated</b> __TODAY__</span>
      <span><b>UK stock feed</b> location_wise_inv_stock</span>
    </div>
  </div>

  <div class="kpis" id="kpis"></div>
  <div class="actions" id="actions"></div>

  <div class="callout">
    <div class="ai">&#9888;&#65039;</div>
    <div>
      <h3>Red = two different things — read carefully</h3>
      <p>The stock feed marks any ASIN with UK stock 0 as critical. This dashboard splits that into
         <b>Stockout</b> (sold recently but out of stock — <b>reorder now</b>) and
         <b>Inactive Listing</b> (no stock <i>and</i> no recent sales — dead listing, usually ignorable).
         A few 0-stock rows are also legacy SKU aliases (<code>LDMA60E274</code>→<code>LDMA60E274WW</code>) tagged <span class="flag">LEGACY?</span>.</p>
    </div>
  </div>

  <div class="toolbar">
    <div class="search">
      <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 10-.7.7l.27.28v.79l5 5 1.5-1.5-5-5zm-6 0a4.5 4.5 0 110-9 4.5 4.5 0 010 9z"/></svg>
      <input id="q" type="text" placeholder="Search ASIN, SKU, account, supplier, container…"/>
    </div>
    <div class="chips" id="chips">
      <button class="chip active" data-f="all">All <span class="c" id="c-all"></span></button>
      <button class="chip" data-f="stockout"><span class="d" style="background:var(--crit)"></span>Stockout <span class="c" id="c-stockout"></span></button>
      <button class="chip" data-f="going"><span class="d" style="background:var(--going)"></span>Going Out <span class="c" id="c-going"></span></button>
      <button class="chip" data-f="healthy"><span class="d" style="background:var(--healthy)"></span>Healthy <span class="c" id="c-healthy"></span></button>
      <button class="chip" data-f="idle"><span class="d" style="background:var(--idle)"></span>Idle Stock <span class="c" id="c-idle"></span></button>
      <button class="chip" data-f="inactive"><span class="d" style="background:var(--inactive)"></span>Inactive <span class="c" id="c-inactive"></span></button>
    </div>
    <button class="btn" id="csvBtn"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>Export CSV</button>
    <button class="btn primary" id="printBtn"><svg viewBox="0 0 24 24"><path d="M19 8H5a3 3 0 00-3 3v6h4v4h12v-4h4v-6a3 3 0 00-3-3zm-3 11H8v-5h8v5zm3-7a1 1 0 110-2 1 1 0 010 2zM18 3H6v4h12V3z"/></svg>Print / PDF</button>
    <span class="count" id="count"></span>
  </div>

  <div class="tablecard"><div class="scroll">
    <table><thead><tr id="hrow"></tr></thead><tbody id="tbody"></tbody></table>
  </div></div>

  <div class="foot">
    <b>Notes.</b> Real fulfillable stock = UK Warehouse from <b>location_wise_inv_stock</b>. <b>Order Count</b> = units sold on Completed FBM orders in the last 90 days; <b>Velocity</b> = that ÷ 90 (blank for no-sales rows). <b>Days</b> = UK stock ÷ velocity. Container reaching date not stored (“–”).
    Categories: <b>Stockout</b> = sold, 0 stock · <b>Going Out</b> ≤60 days · <b>Healthy</b> · <b>Idle Stock</b> = stock, no recent sales · <b>Inactive</b> = no stock, no sales. Default sort: urgent first.
  </div>
</div>

<script>
const DATA = __DATA__;
const TODAY = "__TODAY__";
const COLS=[
 {k:"asin",t:"ASIN",cls:"sku"},{k:"account",t:"Account",cls:""},
 {k:"listing_sku",t:"Listing SKU",cls:"sku"},{k:"master_sku",t:"Correct SKU (Master)",cls:"sku key"},
 {k:"amazon_fbm",t:"Amazon Qty (FBM)",cls:"num dim",num:true},{k:"uk_warehouse",t:"UK Warehouse (Real)",cls:"num key",num:true},
 {k:"order_count_90",t:"90d Units Sold",cls:"num",num:true},{k:"velocity",t:"Velocity /day",cls:"num",num:true},
 {k:"days_remaining",t:"Days Remaining",cls:"num",num:true},{k:"suppliers",t:"Upcoming Supplier",cls:""},
 {k:"po_qty",t:"PO Qty (Incoming)",cls:"num",num:true},{k:"containers",t:"Container #",cls:""},
 {k:"cat",t:"Stock Status",cls:""}];
const LABEL={healthy:"Healthy Stock",going:"Going Out of Stock",stockout:"Stockout — Reorder",idle:"Idle Stock",inactive:"Inactive Listing"};
const nf=n=>Number(n).toLocaleString("en-GB");
function isLegacy(r){if((r.uk_warehouse||0)!==0)return false;const ls=(r.listing_sku||"").toUpperCase(),ms=(r.master_sku||"").toUpperCase();return ls.includes("WW")&&!ms.includes("WW");}
let filter="all",query="",sortK=null,sortDir=1;

function view(){
  let rows=DATA.filter(r=>{
    if(filter!=="all"&&r.cat!==filter)return false;
    if(query){const s=(r.asin+" "+r.account+" "+r.listing_sku+" "+r.master_sku+" "+(r.suppliers||"")+" "+(r.containers||"")).toLowerCase();if(!s.includes(query))return false;}
    return true;});
  if(sortK){const c=COLS.find(x=>x.k===sortK);
    rows.sort((a,b)=>{let x=a[sortK],y=b[sortK];
      if(c.num){x=(x===null||x===undefined||x==="")?-1:Number(x);y=(y===null||y===undefined||y==="")?-1:Number(y);return (x-y)*sortDir;}
      return String(x??"").localeCompare(String(y??""))*sortDir;});}
  return rows;
}
function kpi(){
  const t=DATA.length,heal=DATA.filter(r=>r.cat==="healthy").length,going=DATA.filter(r=>r.cat==="going").length,
    stock=DATA.filter(r=>r.cat==="stockout").length,idle=DATA.filter(r=>r.cat==="idle").length,
    inact=DATA.filter(r=>r.cat==="inactive").length,sellers=DATA.filter(r=>(r.order_count_90||0)>0).length,
    units=DATA.reduce((s,r)=>s+(Number(r.uk_warehouse)||0),0);
  const cards=[
    {n:t,l:"Total ASINs",ic:"&#128202;",f:"all"},
    {n:sellers,l:"Active sellers",ic:"&#128666;",cls:"k-heal",f:null},
    {n:stock,l:"Stockouts · reorder",ic:"&#128308;",cls:"k-stock",f:"stockout"},
    {n:heal,l:"Healthy",ic:"&#9989;",cls:"k-heal",f:"healthy"},
    {n:idle,l:"Idle stock",ic:"&#128164;",cls:"k-idle",f:"idle"},
    {n:inact,l:"Inactive listings",ic:"&#128683;",cls:"k-inact",f:"inactive"},
    {n:nf(units),l:"UK units on hand",ic:"&#128230;",f:null},
  ];
  document.getElementById("kpis").innerHTML=cards.map(c=>
    `<div class="kpi ${c.cls||''}" ${c.f?`data-f="${c.f}"`:""}><div class="ic">${c.ic}</div><div class="n">${c.n}</div><div class="l">${c.l}</div><div class="bar"></div></div>`).join("");
  document.querySelectorAll(".kpi[data-f]").forEach(k=>k.onclick=()=>setFilter(k.dataset.f));
  ["all","stockout","going","healthy","idle","inactive"].forEach(k=>{
    const el=document.getElementById("c-"+k);if(el)el.textContent=(k==="all")?t:DATA.filter(r=>r.cat===k).length;});
}
function actions(){
  const stock=DATA.filter(r=>r.cat==="stockout").length,going=DATA.filter(r=>r.cat==="going").length,
    idle=DATA.filter(r=>r.cat==="idle").length,leg=DATA.filter(isLegacy).length,
    po=DATA.filter(r=>r.cat==="stockout"&&(r.po_qty||0)>0).length;
  const p=[`<span class="pill p-stock" data-f="stockout"><span class="d"></span>${stock} reorder now${po?` (${po} PO inbound)`:""}</span>`];
  if(going)p.push(`<span class="pill p-going" data-f="going"><span class="d"></span>${going} going out</span>`);
  if(idle)p.push(`<span class="pill p-idle" data-f="idle"><span class="d"></span>${idle} idle — review</span>`);
  if(leg)p.push(`<span class="pill p-leg"><span class="d"></span>${leg} legacy? verify</span>`);
  const el=document.getElementById("actions");
  el.innerHTML=`<span class="lead">&#9889; Priority</span>`+p.join("");
  el.querySelectorAll(".pill[data-f]").forEach(x=>x.onclick=()=>setFilter(x.dataset.f));
}
function head(){
  document.getElementById("hrow").innerHTML=COLS.map(c=>{
    const s=sortK===c.k?"sorted":"",ar=sortK===c.k?(sortDir===1?"&#9650;":"&#9660;"):"&#8645;",al=c.num?'style="text-align:right"':'';
    return `<th data-k="${c.k}" class="${s}" ${al}>${c.t}<span class="ar">${ar}</span></th>`;}).join("");
  document.querySelectorAll("thead th").forEach(th=>th.onclick=()=>{const k=th.dataset.k;if(sortK===k)sortDir*=-1;else{sortK=k;sortDir=1;}head();body();});
}
function cell(r,c){
  let v=r[c.k];
  if(c.num)v=(v===null||v===undefined||v==="")?'<span class="dim">–</span>':nf(v);
  if(c.k==="days_remaining"){
    if(r.days_remaining===null||r.days_remaining===undefined)v='<span class="dim">–</span>';
    else if(r.days_remaining>365)v=`<span class="days-cap" title="${nf(r.days_remaining)} days">365+</span>`;
    else v=`<span class="${r.days_remaining<15?'days-warn':''}">${nf(r.days_remaining)}</span>`;
  }
  if(c.k==="velocity")v=(r.velocity===null||r.velocity===undefined)?'<span class="dim">–</span>':nf(r.velocity);
  if(c.k==="po_qty")v=(r.po_qty||0)>0?`<span class="po">+${nf(r.po_qty)}</span>`:'<span class="dim">0</span>';
  if(c.k==="master_sku")v=`${r.master_sku}${isLegacy(r)?'<span class="flag">LEGACY?</span>':''}`;
  if(c.k==="cat")v=`<span class="badge b-${r.cat}"><span class="bd"></span>${LABEL[r.cat]}</span>`;
  if((c.k==="suppliers"||c.k==="containers")&&(v===null||v===undefined||v===""))v='<span class="dim">–</span>';
  return `<td class="${c.cls}">${v}</td>`;
}
function body(){
  const rows=view(),tb=document.getElementById("tbody");
  if(!rows.length)tb.innerHTML=`<tr><td colspan="${COLS.length}" class="empty">No rows match.</td></tr>`;
  else tb.innerHTML=rows.map(r=>`<tr class="c-${r.cat}">${COLS.map(c=>cell(r,c)).join("")}</tr>`).join("");
  document.getElementById("count").textContent=`${rows.length} of ${DATA.length} ASINs`;
}
function setFilter(f){filter=f;
  document.querySelectorAll(".chip").forEach(c=>c.classList.toggle("active",c.dataset.f===f));
  document.querySelectorAll(".kpi").forEach(k=>k.classList.toggle("active",k.dataset.f===f));body();}
function exportCSV(){
  const rows=view(),head=COLS.map(c=>c.k==="cat"?"Stock Status":c.t),
    esc=s=>{s=String(s??"");return /[",\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;},lines=[head.join(",")];
  rows.forEach(r=>lines.push(COLS.map(c=>{let v=c.k==="cat"?LABEL[r.cat]:r[c.k];if(c.k==="master_sku"&&isLegacy(r))v=r.master_sku+" (LEGACY?)";return esc(v);}).join(",")));
  const b=new Blob(["﻿"+lines.join("\r\n")],{type:"text/csv;charset=utf-8"}),a=document.createElement("a");
  a.href=URL.createObjectURL(b);a.download=`Table5_ALL_Thuwaraga_${TODAY}.csv`;a.click();URL.revokeObjectURL(a.href);
}
document.getElementById("q").addEventListener("input",e=>{query=e.target.value.trim().toLowerCase();body();});
document.querySelectorAll(".chip").forEach(ch=>ch.onclick=()=>setFilter(ch.dataset.f));
document.getElementById("csvBtn").onclick=exportCSV;
document.getElementById("printBtn").onclick=()=>window.print();
kpi();actions();head();body();
</script>
</body></html>
"""

HTML = HTML.replace("__TODAY__", TODAY).replace("__DATA__", DATA_JSON)
out = "Table5_Weekly_Stock_Check_Thuwaraga_ALL.html"
open(out, "w", encoding="utf-8").write(HTML)
print("saved", out, "| rows", len(rows), "| categories", dict(counts))
