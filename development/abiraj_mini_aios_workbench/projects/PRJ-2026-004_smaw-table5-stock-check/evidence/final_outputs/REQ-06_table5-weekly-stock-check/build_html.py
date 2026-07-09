# Builds a modern self-contained interactive HTML report from dataset.py
# Usage: python build_html.py  ->  Table5_Weekly_Stock_Check_Thuwaraga.html
import json, os
from datetime import date
from dataset import DATA

TODAY = os.environ.get("REPORT_DATE") or date.today().strftime("%Y-%m-%d")
OUT = "Table5_Weekly_Stock_Check_Thuwaraga.html"
FILE_PATH = os.path.abspath(OUT)

def compute(d):
    wh = d["uk_warehouse"]; oc = d["order_count_90"]
    vel = oc / 90 if oc else 0
    days = 0 if (wh == 0 or vel == 0) else round(wh / vel)
    if wh == 0:      st = "No Stock / Critical"
    elif days < 15:  st = "No Stock / Critical"
    elif days <= 60: st = "Going Out of Stock"
    else:            st = "Healthy Stock"
    return vel, days, st

rows = []
for d in DATA:
    vel, days, st = compute(d)
    rows.append({
        "asin": d["asin"], "account": d["account"],
        "listing_sku": d["listing_sku"], "master_sku": d["master_sku"],
        "amazon_fbm": d["amazon_fbm"], "uk_warehouse": d["uk_warehouse"],
        "order_count_90": d["order_count_90"], "velocity": round(vel, 2),
        "days": days, "status": st,
        "suppliers": d["suppliers"] or "", "po_qty": d["po_qty"] or 0,
        "containers": d["containers"] or "",
    })
rows.sort(key=lambda r: (0 if r["uk_warehouse"] == 0 else 1, r["days"]))
DATA_JSON = json.dumps(rows, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Table 5 — Weekly Stock Check · Thuwaraga</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --peacock:#13B4CF; --peacock-d:#0B7C90; --peacock-l:#5fd3e6;
  --ink:#132a30; --muted:#697c82; --faint:#9aabb0;
  --line:#e7ecee; --bg:#eef2f4; --card:#ffffff;
  --crit:#F4A6A6; --going:#FFEB84; --healthy:#13B4CF;
  --crit-t:#fdeeee; --going-t:#fffbe8; --heal-t:#ffffff;
  --shadow:0 1px 2px rgba(16,40,46,.04),0 8px 24px rgba(16,40,46,.06);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:
  radial-gradient(1200px 500px at 90% -10%,rgba(19,180,207,.10),transparent 60%),
  var(--bg);
  color:var(--ink);font-family:'Inter',-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
  font-size:13px;-webkit-font-smoothing:antialiased;
  -webkit-print-color-adjust:exact;print-color-adjust:exact;}
.wrap{max-width:1560px;margin:0 auto;padding:26px 22px 70px;}
h1,h2,h3{font-family:'Poppins',Inter,sans-serif;}

/* ---- header ---- */
.head{position:relative;overflow:hidden;border-radius:18px;color:#fff;padding:26px 30px;
  background:linear-gradient(120deg,#0B7C90 0%,#13B4CF 55%,#3fd0e6 100%);
  box-shadow:0 10px 30px rgba(11,124,144,.28);}
.head::after{content:"";position:absolute;right:-60px;top:-60px;width:260px;height:260px;border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.18),transparent 70%);}
.head .tag{display:inline-flex;align-items:center;gap:7px;background:rgba(255,255,255,.16);
  padding:5px 12px;border-radius:20px;font-size:11px;font-weight:600;letter-spacing:.4px;
  text-transform:uppercase;backdrop-filter:blur(4px);}
.head .tag .dot{width:7px;height:7px;border-radius:50%;background:#b6ffd9;box-shadow:0 0 0 3px rgba(182,255,217,.25)}
.head h1{margin:14px 0 6px;font-size:23px;font-weight:700;letter-spacing:-.2px;max-width:900px;}
.head p{margin:0;opacity:.94;font-size:13px;font-weight:400;max-width:760px;}
.head .meta{margin-top:16px;display:flex;flex-wrap:wrap;gap:9px 10px;}
.head .meta span{background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.14);
  padding:5px 11px;border-radius:9px;font-size:11.5px;font-weight:500;}
.head .meta b{font-weight:700;opacity:.85;}

/* ---- kpis ---- */
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:13px;margin:18px 0;}
.kpi{background:var(--card);border-radius:15px;padding:16px 17px;border:1px solid var(--line);
  box-shadow:var(--shadow);position:relative;transition:transform .15s ease;}
.kpi:hover{transform:translateY(-2px);}
.kpi .top{display:flex;align-items:center;justify-content:space-between;}
.kpi .ic{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:15px;
  background:rgba(19,180,207,.12);}
.kpi.k-crit .ic{background:rgba(214,69,69,.13)} .kpi.k-going .ic{background:rgba(224,161,60,.15)}
.kpi.k-heal .ic{background:rgba(19,180,207,.13)} .kpi.k-zero .ic{background:rgba(214,69,69,.13)}
.kpi .n{font-size:27px;font-weight:800;line-height:1;margin-top:12px;font-family:'Poppins';letter-spacing:-.5px;}
.kpi .l{font-size:11px;color:var(--muted);margin-top:6px;font-weight:600;text-transform:uppercase;letter-spacing:.4px;}
.kpi .bar{height:4px;border-radius:4px;margin-top:11px;background:var(--peacock);opacity:.9;}
.kpi.k-crit .bar{background:#d64545}.kpi.k-going .bar{background:#E0A13C}
.kpi.k-heal .bar{background:var(--healthy)}.kpi.k-zero .bar{background:#b02a2a}
.kpi[data-f]{cursor:pointer;}
.kpi.active{outline:2px solid var(--peacock);outline-offset:-2px;box-shadow:0 0 0 4px rgba(19,180,207,.12),var(--shadow);}
@media(max-width:1100px){.kpis{grid-template-columns:repeat(3,1fr)}}
@media(max-width:640px){.kpis{grid-template-columns:repeat(2,1fr)}}

/* ---- priority actions bar ---- */
.actions{display:flex;flex-wrap:wrap;gap:9px 14px;align-items:center;background:var(--card);
  border:1px solid var(--line);border-radius:14px;padding:12px 18px;margin-bottom:18px;box-shadow:var(--shadow);}
.actions .lead{display:inline-flex;align-items:center;gap:8px;font-weight:700;font-size:13px;color:var(--ink);}
.actions .pill{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:20px;
  font-size:11.5px;font-weight:700;cursor:pointer;transition:.12s;}
.actions .pill:hover{filter:brightness(.97);transform:translateY(-1px);}
.actions .pill .d{width:7px;height:7px;border-radius:50%;}
.actions .p-crit{background:var(--crit-t);color:#a11b1b;} .actions .p-crit .d{background:#a11b1b;}
.actions .p-zero{background:#fdeeee;color:#b02a2a;} .actions .p-zero .d{background:#b02a2a;}
.actions .p-leg{background:#fff4dd;color:#8a5a12;} .actions .p-leg .d{background:#c78a1e;}
.actions .p-po{background:#e7f8fb;color:#0b7c90;} .actions .p-po .d{background:#0b7c90;}
.actions .ok{color:#0b7c90;font-weight:700;}

/* ---- alert ---- */
.alert{display:flex;gap:14px;background:linear-gradient(90deg,#fffaf0,#fff);border:1px solid #f2e3c4;
  border-left:5px solid #E0A13C;border-radius:14px;padding:15px 18px;margin-bottom:18px;box-shadow:var(--shadow);}
.alert .ai{font-size:20px;line-height:1;}
.alert h3{margin:0 0 5px;font-size:14px;font-weight:600;color:#8a5a12;}
.alert p{margin:0;font-size:12.5px;color:#5a5145;line-height:1.55;}
.alert code{background:#fff;border:1px solid #eadcbe;padding:1px 6px;border-radius:6px;font-size:11.5px;font-weight:600;color:var(--ink);}

/* ---- toolbar ---- */
.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:13px;
  position:sticky;top:0;z-index:5;padding:10px;background:rgba(238,242,244,.85);
  backdrop-filter:blur(8px);border-radius:14px;}
.search{flex:1;min-width:230px;position:relative;}
.search input{width:100%;padding:11px 14px 11px 38px;border:1px solid var(--line);border-radius:11px;
  font-family:inherit;font-size:13px;background:#fff;box-shadow:var(--shadow);}
.search input:focus{outline:none;border-color:var(--peacock);box-shadow:0 0 0 3px rgba(19,180,207,.16);}
.search svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);width:16px;height:16px;fill:#9aabb0;}
.chips{display:flex;gap:6px;flex-wrap:wrap;}
.chip{border:1px solid var(--line);background:#fff;padding:9px 14px;border-radius:22px;cursor:pointer;
  font-family:inherit;font-size:12px;font-weight:600;color:var(--muted);transition:.13s;box-shadow:var(--shadow);}
.chip:hover{border-color:var(--peacock);color:var(--ink);}
.chip.active{background:var(--ink);color:#fff;border-color:var(--ink);}
.chip .d{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle;}
.chip .c{opacity:.6;font-weight:700;margin-left:5px;}
.btn{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);background:#fff;
  padding:9px 14px;border-radius:11px;cursor:pointer;font-family:inherit;font-size:12px;font-weight:600;
  color:var(--ink);transition:.13s;box-shadow:var(--shadow);}
.btn:hover{border-color:var(--peacock);color:var(--peacock-d);}
.btn svg{width:15px;height:15px;fill:currentColor;}
.btn.primary{background:var(--ink);color:#fff;border-color:var(--ink);}
.btn.primary:hover{background:#0d2126;color:#fff;}
.count{font-size:12px;color:var(--muted);margin-left:6px;font-weight:600;}

/* ---- table ---- */
.tablecard{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;box-shadow:var(--shadow);}
.scroll{overflow:auto;max-height:74vh;}
table{border-collapse:separate;border-spacing:0;width:100%;min-width:1200px;}
thead th{position:sticky;top:0;z-index:2;background:#f0f4f5;color:var(--ink);text-align:left;
  padding:12px 13px;font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;
  border-bottom:2px solid #dbe2e4;white-space:nowrap;cursor:pointer;user-select:none;}
thead th:hover{background:#e7edef;}
thead th .ar{opacity:.3;font-size:9px;margin-left:3px;}
thead th.sorted{color:var(--peacock-d);}thead th.sorted .ar{opacity:1;}
td{padding:10px 13px;border-bottom:1px solid var(--line);font-size:12.5px;white-space:nowrap;vertical-align:middle;}
tbody tr{transition:background .1s;}
tbody tr:hover td{background:rgba(19,180,207,.06)!important;}
.num{text-align:right;font-variant-numeric:tabular-nums;}
.sku{font-family:'SFMono-Regular',Consolas,Menlo,monospace;font-size:11.5px;letter-spacing:-.2px;}
.dim{color:#9aabb0;}
.key{font-weight:700;}
tr.st-crit td{background:var(--crit-t);}
tr.st-going td{background:var(--going-t);}
tr.st-heal td{background:#fff;}
.badge{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;white-space:nowrap;}
.badge .bd{width:7px;height:7px;border-radius:50%;}
.b-crit{background:var(--crit);color:#6b1414;}.b-crit .bd{background:#a11b1b;}
.b-going{background:var(--going);color:#7a5c00;}.b-going .bd{background:#b58900;}
.b-heal{background:var(--healthy);color:#053b45;}.b-heal .bd{background:#0b7c90;}
.days-warn{color:#c0392b;font-weight:800;}
.days-cap{color:var(--muted);font-weight:600;}
.po{display:inline-block;background:#e7f8fb;color:#0b7c90;border:1px solid #bfeaf1;
  padding:1px 8px;border-radius:20px;font-weight:700;font-size:11px;}
.flag{display:inline-block;margin-left:6px;font-size:9px;font-weight:800;color:#8a5a12;
  background:#fff4dd;border:1px solid #f0d9a8;padding:1px 5px;border-radius:5px;vertical-align:middle;letter-spacing:.3px;}

.foot{margin-top:18px;font-size:11px;color:var(--muted);line-height:1.7;font-weight:400;}
.foot b{font-weight:700;color:#556;}
.empty{padding:46px;text-align:center;color:var(--muted);}
@media print{
  @page{size:A4 landscape;margin:9mm}
  *{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  body{background:#fff}.toolbar{display:none}.scroll{max-height:none;overflow:visible}
  thead th{position:static}.head{box-shadow:none;border-radius:0}.kpi:hover{transform:none}
  .wrap{max-width:none;padding:0}.tablecard{box-shadow:none}
  td,thead th{font-size:9.5px;padding:5px 7px}table{min-width:0}
}
</style>
</head>
<body>
<div class="wrap">

  <div class="head">
    <span class="tag"><span class="dot"></span>T5 · High Priority · Weekly (every Monday)</span>
    <h1>Weekly Stock Check — Stock Management Across All ASINs &amp; Warehouses</h1>
    <p>Real fulfillable stock = UK Warehouse · Days Remaining = UK Stock ÷ Sales Velocity (last 90 days, FBM).</p>
    <div class="meta">
      <span><b>PH</b> Thuwaraga</span>
      <span><b>Channel</b> Amazon UK · FBM · Completed</span>
      <span><b>Window</b> Last 90 days</span>
      <span><b>Generated</b> __TODAY__</span>
      <span><b>Inventory feed</b> location_wise_inv_stock (UK) · 2026-05-04</span>
      <span title="Saved location of this file"><b>File</b> __FILEPATH__</span>
    </div>
  </div>

  <div class="kpis" id="kpis"></div>

  <div class="actions" id="actions"></div>

  <div class="alert">
    <div class="ai">&#9888;&#65039;</div>
    <div>
      <h3>Known data caveat — some &ldquo;0 stock&rdquo; rows may be legacy aliases</h3>
      <p>A few ASINs record sales under a <b>drained legacy SKU</b> while real stock sits on the canonical variant.
         Example: <code>LDMA60E274</code> reads <b>0</b>, but canonical <code>LDMA60E274WW</code> holds
         <b>3,233</b> units. <b id="legcount">0</b> row(s) match this pattern and are tagged
         <span class="flag">LEGACY?</span> below — verify the master SKU before treating them as true stockouts.</p>
    </div>
  </div>

  <div class="toolbar">
    <div class="search">
      <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 10-.7.7l.27.28v.79l5 5 1.5-1.5-5-5zm-6 0a4.5 4.5 0 110-9 4.5 4.5 0 010 9z"/></svg>
      <input id="q" type="text" placeholder="Search ASIN, SKU, account, supplier, container…"/>
    </div>
    <div class="chips" id="chips">
      <button class="chip active" data-f="all">All <span class="c" id="c-all"></span></button>
      <button class="chip" data-f="No Stock / Critical"><span class="d" style="background:var(--crit)"></span>Critical <span class="c" id="c-crit"></span></button>
      <button class="chip" data-f="Going Out of Stock"><span class="d" style="background:var(--going)"></span>Going Out <span class="c" id="c-going"></span></button>
      <button class="chip" data-f="Healthy Stock"><span class="d" style="background:var(--healthy)"></span>Healthy <span class="c" id="c-heal"></span></button>
    </div>
    <button class="btn" id="csvBtn"><svg viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>Export CSV</button>
    <button class="btn primary" id="printBtn"><svg viewBox="0 0 24 24"><path d="M19 8H5a3 3 0 00-3 3v6h4v4h12v-4h4v-6a3 3 0 00-3-3zm-3 11H8v-5h8v5zm3-7a1 1 0 110-2 1 1 0 010 2zM18 3H6v4h12V3z"/></svg>Print / PDF</button>
    <span class="count" id="count"></span>
  </div>

  <div class="tablecard">
    <div class="scroll">
      <table>
        <thead><tr id="hrow"></tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
  </div>

  <div class="foot">
    <b>Notes.</b> Real fulfillable stock = UK Warehouse total from <b>location_wise_inv_stock</b> (matches the live inventory system); Days &amp; Status derive from it.
    <b>Amazon Listing Qty (FBM)</b> is the merchant-declared count on Amazon (mostly a flat default) — reference only.
    <b>Order Count</b> = units sold on Completed FBM orders in the last 90 days; <b>Velocity</b> = that ÷ 90.
    <b>Container Reaching Date</b> is not stored in the DB (&ldquo;–&rdquo;).
    Status thresholds: warehouse 0 or &lt; 15 days &rarr; Critical; &le; 60 days &rarr; Going Out; else Healthy. Default sort: stockouts first.
    <br><b>File location:</b> <code style="background:#eef2f4;border:1px solid var(--line);padding:1px 6px;border-radius:5px;font-size:11px;">__FILEPATH__</code>
  </div>

</div>

<script>
const DATA = __DATA__;
const TODAY = "__TODAY__";
const COLS = [
  {k:"asin",       t:"ASIN",              cls:"sku"},
  {k:"account",    t:"Account",           cls:""},
  {k:"listing_sku",t:"Listing SKU",       cls:"sku"},
  {k:"master_sku", t:"Correct SKU (Master)", cls:"sku key"},
  {k:"amazon_fbm", t:"Amazon Qty (FBM)",  cls:"num dim", num:true},
  {k:"uk_warehouse",t:"UK Warehouse (Real)", cls:"num key", num:true},
  {k:"order_count_90",t:"90d Order Count",cls:"num", num:true},
  {k:"velocity",   t:"Velocity /day",     cls:"num", num:true},
  {k:"days",       t:"Days Remaining",    cls:"num", num:true},
  {k:"suppliers",  t:"Upcoming Supplier", cls:""},
  {k:"po_qty",     t:"PO Qty (Incoming)", cls:"num", num:true},
  {k:"containers", t:"Container #",       cls:""},
  {k:"status",     t:"Stock Status",      cls:""},
];
const BADGE={"No Stock / Critical":"b-crit","Going Out of Stock":"b-going","Healthy Stock":"b-heal"};
const ROWC ={"No Stock / Critical":"st-crit","Going Out of Stock":"st-going","Healthy Stock":"st-heal"};
const nf=n=>Number(n).toLocaleString("en-GB");
function isLegacy(r){
  if(r.uk_warehouse!==0) return false;
  const ls=(r.listing_sku||"").toUpperCase(), ms=(r.master_sku||"").toUpperCase();
  return ls.includes("WW") && !ms.includes("WW");
}
let filter="all", query="", sortK=null, sortDir=1;

function view(){
  let rows=DATA.filter(r=>{
    if(filter==="zero"){ if(r.uk_warehouse!==0) return false; }
    else if(filter==="legacy"){ if(!isLegacy(r)) return false; }
    else if(filter!=="all" && r.status!==filter) return false;
    if(query){
      const s=(r.asin+" "+r.account+" "+r.listing_sku+" "+r.master_sku+" "+r.suppliers+" "+r.containers).toLowerCase();
      if(!s.includes(query)) return false;
    }
    return true;
  });
  if(sortK){
    const c=COLS.find(x=>x.k===sortK);
    rows.sort((a,b)=>{
      let x=a[sortK],y=b[sortK];
      if(c.num){x=Number(x)||0;y=Number(y)||0;return (x-y)*sortDir;}
      return String(x).localeCompare(String(y))*sortDir;
    });
  }
  return rows;
}
function renderKpis(){
  const t=DATA.length;
  const crit=DATA.filter(r=>r.status==="No Stock / Critical").length;
  const going=DATA.filter(r=>r.status==="Going Out of Stock").length;
  const heal=DATA.filter(r=>r.status==="Healthy Stock").length;
  const zero=DATA.filter(r=>r.uk_warehouse===0).length;
  const units=DATA.reduce((s,r)=>s+(Number(r.uk_warehouse)||0),0);
  const cards=[
    {n:t,l:"Total ASIN rows",c:"",ic:"&#128202;",f:"all"},
    {n:heal,l:"Healthy",c:"k-heal",ic:"&#9989;",f:"Healthy Stock"},
    {n:going,l:"Going Out",c:"k-going",ic:"&#8987;",f:"Going Out of Stock"},
    {n:crit,l:"Critical",c:"k-crit",ic:"&#128308;",f:"No Stock / Critical"},
    {n:zero,l:"Zero UK stock",c:"k-zero",ic:"&#128721;",f:"zero"},
    {n:nf(units),l:"UK units on hand",c:"",ic:"&#128230;"},
  ];
  document.getElementById("kpis").innerHTML=cards.map(c=>
    `<div class="kpi ${c.c}" ${c.f?`data-f="${c.f}"`:""} title="${c.f?"Click to filter":""}">
       <div class="top"><div class="ic">${c.ic}</div></div>
       <div class="n">${c.n}</div><div class="l">${c.l}</div><div class="bar"></div></div>`).join("");
  document.querySelectorAll(".kpi[data-f]").forEach(k=>k.onclick=()=>setFilter(k.dataset.f));
  document.getElementById("c-all").textContent=t;
  document.getElementById("c-crit").textContent=crit;
  document.getElementById("c-going").textContent=going;
  document.getElementById("c-heal").textContent=heal;
}
function renderActions(){
  const crit=DATA.filter(r=>r.status==="No Stock / Critical").length;
  const zero=DATA.filter(r=>r.uk_warehouse===0).length;
  const legacy=DATA.filter(isLegacy).length;
  const incoming=DATA.filter(r=>r.status==="No Stock / Critical"&&r.po_qty>0).length;
  document.getElementById("legcount").textContent=legacy;
  let html;
  if(crit===0){
    html=`<span class="lead">&#9889; Priority actions</span><span class="ok">&#10004; All ASINs healthy — no action needed.</span>`;
  }else{
    const p=[];
    p.push(`<span class="pill p-crit" data-f="No Stock / Critical"><span class="d"></span>${crit} need action</span>`);
    if(zero)     p.push(`<span class="pill p-zero" data-f="zero"><span class="d"></span>${zero} at zero stock</span>`);
    if(legacy)   p.push(`<span class="pill p-leg" data-f="legacy"><span class="d"></span>${legacy} possible legacy alias</span>`);
    if(incoming) p.push(`<span class="pill p-po"><span class="d"></span>${incoming} with incoming PO</span>`);
    html=`<span class="lead">&#9889; Priority actions</span>`+p.join("");
  }
  const el=document.getElementById("actions");
  el.innerHTML=html;
  el.querySelectorAll(".pill[data-f]").forEach(x=>x.onclick=()=>setFilter(x.dataset.f));
}
function setFilter(f){
  filter=f;
  document.querySelectorAll(".chip").forEach(c=>c.classList.toggle("active",c.dataset.f===f));
  document.querySelectorAll(".kpi").forEach(k=>k.classList.toggle("active",k.dataset.f===f));
  renderBody();
}
function renderHead(){
  document.getElementById("hrow").innerHTML=COLS.map(c=>{
    const sorted=sortK===c.k?"sorted":"";
    const ar=sortK===c.k?(sortDir===1?"&#9650;":"&#9660;"):"&#8645;";
    const align=c.num?'style="text-align:right"':'';
    return `<th data-k="${c.k}" class="${sorted}" ${align}>${c.t}<span class="ar">${ar}</span></th>`;
  }).join("");
  document.querySelectorAll("thead th").forEach(th=>th.onclick=()=>{
    const k=th.dataset.k;
    if(sortK===k) sortDir*=-1; else {sortK=k; sortDir=1;}
    renderHead(); renderBody();
  });
}
function cell(r,c){
  let v=r[c.k];
  if(c.num) v=(v===""||v==null)?"":nf(v);
  if(c.k==="days"){
    if(r.uk_warehouse===0){ v='<span class="days-warn">0</span>'; }
    else{
      const warn=r.days<15?"days-warn":"";
      if(r.days>365) v=`<span class="days-cap" title="${nf(r.days)} days of cover">365+</span>`;
      else           v=`<span class="${warn}">${nf(r.days)}</span>`;
    }
  }
  if(c.k==="po_qty") v = r.po_qty>0 ? `<span class="po">+${nf(r.po_qty)}</span>` : '<span class="dim">0</span>';
  if(c.k==="master_sku") v=`${r.master_sku}${isLegacy(r)?'<span class="flag">LEGACY?</span>':''}`;
  if(c.k==="status") v=`<span class="badge ${BADGE[r.status]}"><span class="bd"></span>${r.status}</span>`;
  if((c.k==="suppliers"||c.k==="containers")&&(v===""||v==null)) v='<span class="dim">–</span>';
  return `<td class="${c.cls}">${v}</td>`;
}
function renderBody(){
  const rows=view();
  const tb=document.getElementById("tbody");
  if(!rows.length) tb.innerHTML=`<tr><td colspan="${COLS.length}" class="empty">No rows match your filter.</td></tr>`;
  else tb.innerHTML=rows.map(r=>`<tr class="${ROWC[r.status]}">${COLS.map(c=>cell(r,c)).join("")}</tr>`).join("");
  document.getElementById("count").textContent=`${rows.length} of ${DATA.length} rows`;
}
// CSV export of current view
function exportCSV(){
  const rows=view();
  const head=COLS.map(c=>c.t);
  const esc=s=>{s=String(s??"");return /[",\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;};
  const lines=[head.join(",")];
  rows.forEach(r=>lines.push(COLS.map(c=>esc(c.k==="master_sku"&&isLegacy(r)?r[c.k]+" (LEGACY?)":r[c.k])).join(",")));
  const blob=new Blob(["﻿"+lines.join("\r\n")],{type:"text/csv;charset=utf-8"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download=`Table5_Weekly_Stock_Check_Thuwaraga_${TODAY}.csv`;
  a.click();URL.revokeObjectURL(a.href);
}
document.getElementById("q").addEventListener("input",e=>{query=e.target.value.trim().toLowerCase();renderBody();});
document.querySelectorAll(".chip").forEach(ch=>ch.onclick=()=>setFilter(ch.dataset.f));
document.getElementById("csvBtn").onclick=exportCSV;
document.getElementById("printBtn").onclick=()=>window.print();
renderKpis();renderActions();renderHead();renderBody();
</script>
</body>
</html>
"""

HTML = (HTML.replace("__TODAY__", TODAY)
            .replace("__FILEPATH__", FILE_PATH)
            .replace("__DATA__", DATA_JSON))
out = OUT
with open(out, "w", encoding="utf-8") as f:
    f.write(HTML)

from collections import Counter
print("saved", out, "| rows", len(rows), "|", dict(Counter(r["status"] for r in rows)))
