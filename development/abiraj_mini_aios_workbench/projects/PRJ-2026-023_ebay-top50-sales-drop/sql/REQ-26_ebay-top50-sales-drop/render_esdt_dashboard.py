#!/usr/bin/env python3
"""
REQ-26-D01 — eBay UK Top 50 Sales Drop · interactive HTML dashboard renderer (v2).
Reads esdt_payload.json (same verified snapshot as the Excel) and writes a self-contained,
full-screen, light-theme dashboard: product thumbnails, in-row prev->current bars, severity
colour-scale, and a click-to-open row-detail drawer. Product images load from the eBay CDN
(i.ebayimg.com); everything else is offline/self-contained.
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "esdt_payload.json")
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "evidence", "final_outputs", "REQ-26_ebay-top50-sales-drop"))
OUT = os.path.join(OUT_DIR, "REQ-26-D01_ebay_top50_sales_drop.html")

def priority_key(mag):
    if mag >= 50: return "critical"
    if mag >= 30: return "high"
    if mag >= 15: return "medium"
    return "stable"

def diagnose(r):
    imp_c, imp_p = r["cur_impr"], r["prev_impr"]
    v_c, v_p = r["cur_views"], r["prev_views"]
    ctr_c = (v_c/imp_c) if imp_c else 0.0
    ctr_p = (v_p/imp_p) if imp_p else 0.0
    cvr_c = (r["cur_units"]/v_c) if v_c else 0.0
    cvr_p = (r["prev_units"]/v_p) if v_p else 0.0
    sp_c, sp_p = r["cur_ppc_spend"], r["prev_ppc_spend"]
    if r["stock_uk"] == 0: return "Out of stock", "Stock — restock urgently"
    if imp_p > 0 and imp_c < imp_p*0.85: return "Visibility / SEO drop (impressions ↓)", "SEO Review — title, keywords, item specifics"
    if ctr_p > 0 and ctr_c < ctr_p*0.85: return "CTR drop — listing appeal", "Main Image + Title Review"
    if cvr_p > 0 and cvr_c < cvr_p*0.85: return "Conversion drop — price / offer", "Price & Offer Review"
    if sp_p > 0 and sp_c < sp_p*0.85: return "PPC pull-back (ad spend ↓)", "PPC Review — budget & bids"
    return "Broad sales decline", "Review listing, price & PPC"

def build_rows(rows):
    out = []
    for r in rows:
        imp, v = r["cur_impr"], r["cur_views"]
        ctr = round(100.0*v/imp, 2) if imp else None
        cvr = round(100.0*r["cur_units"]/v, 2) if v else None
        roas = round(r["cur_ppc_sales"]/r["cur_ppc_spend"], 2) if r["cur_ppc_spend"] > 0 else None
        reason, action = diagnose(r)
        out.append(dict(
            rank=r["rank"], sku=r["sku"], item_id=str(r["item_id"] or ""), product=r["product"] or r["sku"],
            image=r.get("image") or "",
            prev=round(r["prev_sales"],2), cur=round(r["cur_sales"],2), loss=round(r["loss_gbp"],2),
            drop=r["drop_pct"], ctr=ctr, cvr=cvr, roas=roas, stock=r["stock_uk"],
            prio=priority_key(abs(r["drop_pct"])), reason=reason, action=action,
            cur_units=r["cur_units"], prev_units=r["prev_units"],
            cur_impr=r["cur_impr"], prev_impr=r["prev_impr"],
            cur_views=r["cur_views"], prev_views=r["prev_views"],
            cur_ppc_sales=round(r["cur_ppc_sales"],2), cur_ppc_spend=round(r["cur_ppc_spend"],2),
            prev_ppc_sales=round(r["prev_ppc_sales"],2), prev_ppc_spend=round(r["prev_ppc_spend"],2)))
    return out

def main():
    data = json.load(open(PAYLOAD, encoding="utf-8"))
    meta = data["meta"]
    payload = dict(rows=build_rows(data["rows"]), generated=meta.get("generated"),
                   cur=[meta.get("cur_from"), meta.get("cur_to")],
                   prev=[meta.get("prev_from"), meta.get("prev_to")])
    tpl = TEMPLATE.replace("/*__DATA__*/null", json.dumps(payload))
    os.makedirs(OUT_DIR, exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(tpl)
    print("OK dashboard:", OUT, "bytes:", os.path.getsize(OUT))

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>eBay UK — Top 50 Sales Drop · ELECTRICALSONE</title>
<style>
:root{
  --bg:#eef2f7; --panel:#ffffff; --ink:#0f2033; --muted:#64748b; --line:#e7ecf3;
  --accent:#2563eb; --accent-soft:#eaf1ff;
  --crit:#e5484d; --crit-bg:#fdecec; --high:#f5820b; --high-bg:#fdf0e1;
  --med:#d9a400; --med-bg:#fbf6e0; --stable:#2fa96b; --stable-bg:#e7f6ee;
  --shadow:0 1px 2px rgba(16,32,51,.04),0 8px 24px rgba(16,32,51,.06);
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:linear-gradient(180deg,#f6f9fd,var(--bg));color:var(--ink);
  font:14px/1.45 "Segoe UI",system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif;padding:14px;
  min-height:100%}
.wrap{max-width:1620px;width:100%;margin:0 auto;display:flex;flex-direction:column;gap:11px}
/* ---------- HERO (top section) ---------- */
.hero{position:relative;border-radius:16px;padding:11px 18px;overflow:hidden;
  background:
    radial-gradient(1200px 220px at 12% -60%,rgba(37,99,235,.13),transparent 60%),
    radial-gradient(900px 260px at 105% -20%,rgba(229,72,77,.09),transparent 55%),
    linear-gradient(180deg,#ffffff, #fbfdff);
  border:1px solid #e3ebf6;box-shadow:0 1px 2px rgba(16,32,51,.04),0 12px 34px rgba(21,52,96,.07)}
.hero::before{content:"";position:absolute;inset:0 0 auto 0;height:3px;
  background:linear-gradient(90deg,#2563eb,#4f7bf0 40%,#e5484d)}
.herobar{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:nowrap}
.brand{display:flex;gap:13px;align-items:center;min-width:0;flex:1 1 auto}
.title{min-width:0;flex:1 1 auto}
.tools{flex:0 0 auto}
@media(max-width:620px){.herobar{flex-wrap:wrap}}
.logo{width:44px;height:44px;border-radius:12px;flex:none;display:flex;align-items:center;justify-content:center;
  font-size:22px;background:linear-gradient(145deg,#2563eb,#1e40af);
  box-shadow:0 5px 13px rgba(37,99,235,.30),inset 0 1px 0 rgba(255,255,255,.35)}
.title h1{margin:0;font-size:20px;font-weight:800;letter-spacing:-.02em;color:#12233b;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.title p{margin:3px 0 0;color:var(--muted);font-size:12.5px;display:flex;align-items:center;flex-wrap:nowrap;gap:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.title p .perpill{flex:none}
.title p b{color:#2b3b50}
.perpill{display:inline-block;background:#eef3fb;border:1px solid #e0e8f4;color:#4a6076;
  font-size:11px;font-weight:600;padding:1px 9px;border-radius:999px;font-variant-numeric:tabular-nums}
.badge{display:inline-flex;align-items:center;gap:7px;background:#eafaf0;color:#1c7a4c;font-weight:700;
  font-size:12px;padding:6px 12px;border-radius:999px;border:1px solid #cdeeda}
.badge .ld{width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 0 0 rgba(34,197,94,.55);
  animation:pulse 2s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(34,197,94,.5)}70%{box-shadow:0 0 0 7px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}
.tools{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
button,select,input{font:inherit;color:var(--ink)}
.btn{border:1px solid #dbe3ee;background:rgba(255,255,255,.9);border-radius:11px;padding:9px 14px;cursor:pointer;
  box-shadow:0 1px 2px rgba(16,32,51,.05);transition:.15s;display:inline-flex;gap:2px;align-items:center;font-weight:650}
.btn:hover{border-color:#bcc9db;transform:translateY(-1px);box-shadow:0 6px 16px rgba(16,32,51,.10)}
.btn.primary{background:linear-gradient(145deg,#2b6ef0,#2158d8);color:#fff;border-color:#2158d8;box-shadow:0 6px 16px rgba(37,99,235,.28)}
.btn.primary:hover{filter:brightness(1.05)}
.kpis{display:flex;flex-wrap:wrap;align-items:stretch;margin-top:10px;padding-top:9px;border-top:1px solid #e6ecf5}
.kpi{flex:1 1 0;min-width:0;padding:0 18px;border-left:1px solid #e9eef6}
.kpi:first-child{padding-left:2px;border-left:0}
@media(max-width:760px){.kpi{flex:1 1 42%;padding:6px 14px;border-left:0}}
.kpi .k{display:flex;align-items:center;gap:6px;color:var(--muted);font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi .k::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--kc,#c7d3e4);flex:none}
.kpi .v{font-size:19px;font-weight:800;margin-top:3px;letter-spacing:-.02em;line-height:1.1;color:#14243b}
.kpi .s{font-size:11px;color:var(--muted);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi.danger .v{color:var(--crit)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);
  overflow:hidden;display:flex;flex-direction:column}
.controls{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:10px 14px;border-bottom:1px solid var(--line)}
.search{flex:1;min-width:150px;display:flex;align-items:center;gap:8px;background:#f7f9fc;border:1px solid var(--line);border-radius:10px;padding:8px 12px}
.search input{border:0;background:transparent;outline:0;width:100%}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 12px;cursor:pointer;font-weight:600;font-size:12.5px;color:var(--muted)}
.chip[data-active="1"]{color:#fff;border-color:transparent}
.chip.all[data-active="1"]{background:var(--accent)}
.chip.critical[data-active="1"]{background:var(--crit)}
.chip.high[data-active="1"]{background:var(--high)}
.chip.medium[data-active="1"]{background:var(--med)}
.chip.stable[data-active="1"]{background:var(--stable)}
/* bounded, robust table height (works standalone AND in a short portal iframe);
   inner scroll keeps the sticky header fixed while rows scroll */
.tablewrap{height:clamp(500px,90vh,1500px);overflow:auto}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:13px}
thead th{position:sticky;top:0;z-index:2;background:#f4f7fb;text-align:left;padding:11px 12px;font-weight:700;color:#334155;white-space:nowrap;border-bottom:1px solid var(--line);cursor:pointer;user-select:none}
thead th.num{text-align:right}
thead th .ar{opacity:.35;font-size:11px;margin-left:3px}
thead th[data-dir] .ar{opacity:1;color:var(--accent)}
tbody td{padding:9px 12px;border-bottom:1px solid #f1f4f8;white-space:nowrap;vertical-align:middle}
tbody tr{cursor:pointer;transition:background .12s}
tbody tr:hover{background:#f4f9ff}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.prodcell{display:flex;align-items:center;gap:10px;min-width:300px;max-width:440px;white-space:normal}
.thumb{width:44px;height:44px;border-radius:9px;object-fit:cover;background:#eef2f7;border:1px solid var(--line);flex:none}
.thumb.ph{display:flex;align-items:center;justify-content:center;color:#9aa7b6;font-size:16px}
.ptxt{line-height:1.25}
.ptxt .pt{color:#1f2d3d}
.ptxt .pi{color:var(--muted);font-size:11.5px;font-variant-numeric:tabular-nums}
.sku{font-weight:700;letter-spacing:-.01em}
.loss{color:var(--crit);font-weight:700}
.losscell{min-width:118px}
.mbar{height:6px;border-radius:4px;background:#eceff4;position:relative;margin-top:5px;overflow:hidden}
.mbar>.rem{position:absolute;left:0;top:0;bottom:0;background:#8fb4f6}
.mbar>.now{position:absolute;left:0;top:0;bottom:0;background:#2fa96b}
.dropcell{font-weight:700;border-radius:8px;text-align:center}
.pill{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-weight:700;font-size:12px}
.pill.critical{background:var(--crit-bg);color:var(--crit)}
.pill.high{background:var(--high-bg);color:#b4610a}
.pill.medium{background:var(--med-bg);color:#9a7500}
.pill.stable{background:var(--stable-bg);color:#1c7a4c}
.dot{width:7px;height:7px;border-radius:50%}
.dot.critical{background:var(--crit)}.dot.high{background:var(--high)}.dot.medium{background:var(--med)}.dot.stable{background:var(--stable)}
.rankcell{font-weight:800;color:#334155}
.na{color:#9aa7b6}
.action{color:#334155}
.reason{color:var(--muted);font-size:12px}
footer.foot{display:flex;justify-content:space-between;color:var(--muted);font-size:12px;padding:4px 6px;flex-wrap:wrap;gap:8px}
.count{color:var(--muted);font-weight:600;font-size:12.5px;margin-left:auto}
.fsel{border:1px solid var(--line);background:#fff;border-radius:10px;padding:8px 10px;font-weight:600;font-size:12.5px;color:#334155;cursor:pointer;max-width:190px}
.fsel:hover{border-color:#cfd9e6}
.ftog{border:1px solid var(--line);background:#fff;border-radius:999px;padding:7px 13px;font-weight:600;font-size:12.5px;color:var(--muted);cursor:pointer}
.ftog:hover{border-color:#cfd9e6}
.ftog[data-on="1"]{background:var(--ink);color:#fff;border-color:transparent}
.ftog.clear{color:#94a3b8}
.fslider{display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:600;color:var(--muted);
  border:1px solid var(--line);border-radius:10px;padding:6px 12px;background:#fff}
.fslider input[type=range]{width:104px;accent-color:var(--accent);cursor:pointer}
.fslider .lv{color:var(--ink);font-variant-numeric:tabular-nums;min-width:44px;text-align:right}
/* drawer */
.scrim{position:fixed;inset:0;background:rgba:15,32,51,.28;background:rgba(15,32,51,.34);opacity:0;pointer-events:none;transition:.2s;z-index:40}
.scrim.open{opacity:1;pointer-events:auto}
.drawer{position:fixed;top:0;right:0;height:100%;width:min(460px,94vw);background:var(--panel);box-shadow:-10px 0 40px rgba(16,32,51,.18);
  transform:translateX(100%);transition:transform .24s cubic-bezier(.4,0,.2,1);z-index:50;display:flex;flex-direction:column}
.drawer.open{transform:none}
.dhead{padding:12px 16px;border-bottom:1px solid var(--line);display:flex;gap:11px;align-items:flex-start}
.dhead img{width:52px;height:52px;border-radius:11px;object-fit:cover;border:1px solid var(--line);background:#eef2f7;flex:none}
.dhead .dt{font-weight:700;font-size:13.5px;line-height:1.28}
.dhead .ds{color:var(--muted);font-size:12px;margin-top:3px}
.dclose{margin-left:auto;border:0;background:#f1f4f8;border-radius:9px;width:30px;height:30px;cursor:pointer;font-size:15px;color:#5a6b7b;flex:none}
.dbody{padding:11px 16px;overflow:auto;display:flex;flex-direction:column;gap:10px}
.dhero{display:flex;gap:10px}
.dhero .box{flex:1;background:#f8fafd;border:1px solid var(--line);border-radius:11px;padding:9px 11px}
.dhero .lab{color:var(--muted);font-size:10.5px;font-weight:600;text-transform:uppercase;letter-spacing:.03em}
.dhero .big{font-size:19px;font-weight:750;margin-top:2px}
.cmp{display:flex;flex-direction:column;gap:7px}
.cmp .row{display:grid;grid-template-columns:80px 1fr;gap:9px;align-items:center}
.cmp .rl{color:var(--muted);font-size:11.5px;font-weight:600}
.pair{display:flex;flex-direction:column;gap:5px}
.pair{gap:4px!important}
.pb{height:13px;border-radius:5px;background:#eef2f7;position:relative;overflow:hidden}
.pb>span{position:absolute;left:0;top:0;bottom:0;border-radius:5px}
.pb .pv{position:absolute;right:7px;top:0;bottom:0;display:flex;align-items:center;font-size:11px;font-weight:700;color:#274257}
.pb.prev>span{background:#c9d6ea}
.pb.now>span{background:#7fb1f4}
.mini{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}
.mini .m{background:#f8fafd;border:1px solid var(--line);border-radius:10px;padding:7px 8px;text-align:center}
.mini .m .l{color:var(--muted);font-size:10.5px;font-weight:600}
.mini .m .n{font-size:15px;font-weight:750;margin-top:1px}
.callout{background:var(--accent-soft);border:1px solid #d7e4ff;border-radius:11px;padding:9px 12px}
.callout .r{color:var(--accent);font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
.callout .a{font-weight:700;margin-top:4px}
.callout .rr{color:var(--muted);font-size:12.5px;margin-top:2px}
.dlink{color:var(--accent);text-decoration:none;font-weight:600}.dlink:hover{text-decoration:underline}
@media(max-width:1100px){.kpis{grid-template-columns:repeat(3,1fr)}}
@media(max-width:640px){.kpis{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="wrap">
  <section class="hero">
    <div class="herobar">
      <div class="brand">
        <div class="logo">📉</div>
        <div class="title">
          <h1>eBay UK — Top&nbsp;50 Sales Drop</h1>
          <p>Account <b>ELECTRICALSONE</b> · last 30 days vs previous 30 days <span class="perpill" id="periods"></span></p>
        </div>
      </div>
      <div class="tools">
        <span class="badge"><span class="ld"></span>Live ledsone data</span>
        <button class="btn" id="csvBtn">⬇&nbsp; Export CSV</button>
        <button class="btn primary" id="fsBtn">⛶&nbsp; Full screen</button>
      </div>
    </div>
    <div class="kpis" id="kpis"></div>
  </section>
  <div class="panel">
    <div class="controls">
      <div class="search">🔎<input id="q" placeholder="Search SKU, product, item ID, action…"/></div>
      <div class="chips" id="chips">
        <div class="chip all" data-p="all" data-active="1">All</div>
        <div class="chip critical" data-p="critical">🔴 Critical</div>
        <div class="chip high" data-p="high">🟠 High</div>
        <div class="chip medium" data-p="medium">🟡 Medium</div>
        <div class="chip stable" data-p="stable">🟢 Stable</div>
      </div>
      <select class="fsel" id="actionF" title="Filter by recommended action"><option value="all">All actions</option></select>
      <select class="fsel" id="adF" title="Advertising status">
        <option value="all">All PPC</option><option value="ad">Advertised</option><option value="noad">Not advertised</option></select>
      <button class="ftog" id="stockF" title="Show only out-of-stock SKUs">📦 Out of stock</button>
      <button class="ftog clear" id="clearF" title="Clear all filters">✕ Clear</button>
      <span class="count" id="count"></span>
    </div>
    <div class="tablewrap">
      <table id="tbl"><thead><tr id="head"></tr></thead><tbody id="body"></tbody></table>
    </div>
  </div>
</div>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer"></aside>

<script>
const DATA = /*__DATA__*/null;
const COLS = [
  {k:'rank',  t:'#',        num:true,  cls:'rankcell'},
  {k:'product',t:'Product', cls:'prodcell'},
  {k:'prev',  t:'Prev £',   num:true},
  {k:'cur',   t:'Curr £',   num:true},
  {k:'loss',  t:'Loss £ (prev→now)', num:true, cls:'losscell'},
  {k:'drop',  t:'Drop %',   num:true},
  {k:'ctr',   t:'CTR %',    num:true},
  {k:'cvr',   t:'CVR %',    num:true},
  {k:'roas',  t:'ROAS',     num:true},
  {k:'stock', t:'Stock',    num:true},
  {k:'prio',  t:'Priority'},
  {k:'action',t:'Action'},
];
const PLABEL={critical:'Critical',high:'High',medium:'Medium',stable:'Stable'};
const gbp=v=>'£'+Number(v).toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});
const gbp0=v=>'£'+Number(v).toLocaleString('en-GB',{maximumFractionDigits:0});
const num=v=>Number(v).toLocaleString('en-GB');
const pct=v=>(v==null?'<span class="na">n/a</span>':Number(v).toFixed(1)+'%');
const pct2=v=>(v==null?'<span class="na">n/a</span>':Number(v).toFixed(2)+'%');
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const maxPrev=Math.max(...DATA.rows.map(x=>x.prev));
// If embedded in the portal (iframe), render the table at full height and let the portal scroll.
try{ if(window.self!==window.top) document.documentElement.classList.add('embedded'); }catch(e){ document.documentElement.classList.add('embedded'); }
let state={q:'',prio:'all',sort:'rank',dir:1,action:'all',ad:'all',stock0:false,minloss:0};

function view(){
  let r=DATA.rows.filter(x=>state.prio==='all'||x.prio===state.prio);
  if(state.q){const q=state.q.toLowerCase();
    r=r.filter(x=>(x.sku+' '+x.product+' '+x.item_id+' '+x.action+' '+x.reason).toLowerCase().includes(q));}
  if(state.action!=='all') r=r.filter(x=>x.action===state.action);
  if(state.ad==='ad')   r=r.filter(x=>x.cur_ppc_spend>0||x.prev_ppc_spend>0);
  if(state.ad==='noad') r=r.filter(x=>!(x.cur_ppc_spend>0||x.prev_ppc_spend>0));
  if(state.stock0)      r=r.filter(x=>x.stock===0);
  if(state.minloss>0)   r=r.filter(x=>Math.abs(x.loss)>=state.minloss);
  const s=state.sort,d=state.dir;
  r=r.slice().sort((a,b)=>{let x=a[s],y=b[s];
    if(x==null)x=(d>0?Infinity:-Infinity);if(y==null)y=(d>0?Infinity:-Infinity);
    if(typeof x==='string')return d*x.localeCompare(y);return d*(x-y);});
  return r;
}
function kpis(r){
  const lost=r.reduce((s,x)=>s+x.loss,0),prev=r.reduce((s,x)=>s+x.prev,0),cur=r.reduce((s,x)=>s+x.cur,0);
  const crit=r.filter(x=>x.prio==='critical').length;
  const avg=r.length?r.reduce((s,x)=>s+x.drop,0)/r.length:0;
  const mx=r.reduce((m,x)=>x.loss<m.loss?x:m,{loss:0,sku:'—'});
  const K=[
    {k:'SKUs shown',v:r.length,s:'of '+DATA.rows.length+' in report',c:'#2563eb'},
    {k:'Total lost',v:gbp(Math.abs(lost)),s:gbp(prev)+' → '+gbp(cur),d:1,c:'#e5484d'},
    {k:'Critical',v:crit,s:'drop ≥ 50%',d:1,c:'#e5484d'},
    {k:'Avg drop',v:avg.toFixed(1)+'%',s:'across shown rows',c:'#f5820b'},
    {k:'Biggest loss',v:gbp(Math.abs(mx.loss)),s:esc(mx.sku),c:'#d9a400'},
    {k:'Current sales',v:gbp(cur),s:'was '+gbp(prev),c:'#2fa96b'},
  ];
  document.getElementById('kpis').innerHTML=K.map(x=>
    `<div class="kpi ${x.d?'danger':''}" style="--kc:${x.c}">
       <div class="k">${x.k}</div>
       <div class="v">${x.v}</div><div class="s" title="${x.s}">${x.s}</div></div>`).join('');
}
function head(){
  document.getElementById('head').innerHTML=COLS.map(c=>{
    const dir=state.sort===c.k?(state.dir>0?'asc':'desc'):'';
    const ar=state.sort===c.k?(state.dir>0?'▲':'▼'):'⇅';
    return `<th class="${c.num?'num':''}" data-k="${c.k}" ${dir?`data-dir="${dir}"`:''}>${esc(c.t)}<span class="ar">${ar}</span></th>`;
  }).join('');
  document.querySelectorAll('#head th').forEach(th=>th.onclick=()=>{
    const k=th.dataset.k;if(state.sort===k)state.dir*=-1;else{state.sort=k;state.dir=1;}render();});
}
function dropStyle(v){ // light red scale by magnitude (0..100)
  const m=Math.min(Math.abs(v),100)/100, a=(0.08+m*0.42).toFixed(2);
  return `background:rgba(229,72,77,${a});color:${m>0.6?'#fff':'#8a1f22'}`;
}
function thumb(x,cls){
  if(x.image) return `<img class="${cls}" loading="lazy" referrerpolicy="no-referrer" src="${esc(x.image)}" onerror="this.classList.add('ph');this.removeAttribute('src');this.textContent='▦'">`;
  return `<div class="${cls} ph">▦</div>`;
}
function cell(c,x){
  const v=x[c.k];
  switch(c.k){
    case 'rank': return v;
    case 'product': return `${thumb(x,'thumb')}<div class="ptxt"><div class="pt sku">${esc(x.sku)}</div><div class="pi">${esc(x.product)}</div></div>`;
    case 'prev': case 'cur': return gbp(v);
    case 'loss': {
      const remPct=Math.max(0,Math.min(100,x.prev? x.prev/maxPrev*100:0));
      const nowPct=Math.max(0,Math.min(100,x.prev? x.cur/maxPrev*100:0));
      return `<span class="loss">-${gbp(Math.abs(v))}</span>
        <div class="mbar" title="prev ${gbp(x.prev)} → now ${gbp(x.cur)}">
          <span class="rem" style="width:${remPct}%"></span><span class="now" style="width:${nowPct}%"></span></div>`;
    }
    case 'drop': return `<span class="dropcell" style="${dropStyle(v)};padding:3px 8px;display:inline-block">${Number(v).toFixed(1)}%</span>`;
    case 'ctr': case 'cvr': return pct2(v);
    case 'roas': return v==null?'<span class="na">n/a</span>':Number(v).toFixed(2);
    case 'stock': return v===0?'<span class="loss">0</span>':num(v);
    case 'prio': return `<span class="pill ${x.prio}"><span class="dot ${x.prio}"></span>${PLABEL[x.prio]}</span>`;
    case 'action': return `<div class="action">${esc(x.action)}</div><div class="reason">${esc(x.reason)}</div>`;
    default: return esc(v);
  }
}
function render(){
  const r=view();kpis(r);head();
  document.getElementById('count').textContent=r.length+' shown';
  const b=document.getElementById('body');
  b.innerHTML=r.map((x,i)=>`<tr data-i="${DATA.rows.indexOf(x)}">`+COLS.map(c=>
    `<td class="${c.num?'num':''} ${c.cls||''}">${cell(c,x)}</td>`).join('')+'</tr>').join('');
  b.querySelectorAll('tr').forEach(tr=>tr.onclick=()=>openDrawer(DATA.rows[+tr.dataset.i]));
}
// ---- detail drawer ----
function pair(label,prev,cur,fmt){
  const mx=Math.max(prev,cur,1);
  const wp=(prev/mx*100).toFixed(1),wc=(cur/mx*100).toFixed(1);
  return `<div class="row"><div class="rl">${label}</div><div class="pair">
     <div class="pb prev"><span style="width:${wp}%"></span><div class="pv">prev ${fmt(prev)}</div></div>
     <div class="pb now"><span style="width:${wc}%"></span><div class="pv">now ${fmt(cur)}</div></div>
   </div></div>`;
}
function openDrawer(x){
  const d=document.getElementById('drawer');
  const ctr=x.ctr==null?'n/a':x.ctr.toFixed(2)+'%', cvr=x.cvr==null?'n/a':x.cvr.toFixed(2)+'%', roas=x.roas==null?'n/a':x.roas.toFixed(2);
  d.innerHTML=`
   <div class="dhead">
     ${x.image?`<img referrerpolicy="no-referrer" loading="lazy" src="${esc(x.image)}" onerror="this.style.visibility='hidden'">`:`<div style="width:72px;height:72px;border-radius:12px;background:#eef2f7;border:1px solid var(--line);display:flex;align-items:center;justify-content:center;color:#9aa7b6;font-size:22px">▦</div>`}
     <div><div class="dt">${esc(x.product)}</div>
       <div class="ds"><span class="sku">${esc(x.sku)}</span> · Item <a class="dlink" target="_blank" rel="noopener" href="https://www.ebay.co.uk/itm/${esc(x.item_id)}">${esc(x.item_id)}</a></div>
       <div style="margin-top:6px"><span class="pill ${x.prio}"><span class="dot ${x.prio}"></span>${PLABEL[x.prio]}</span></div>
     </div>
     <button class="dclose" onclick="closeDrawer()">✕</button>
   </div>
   <div class="dbody">
     <div class="dhero">
       <div class="box"><div class="lab">Sales lost</div><div class="big loss">-${gbp(Math.abs(x.loss))}</div><div class="ds">${gbp(x.prev)} → ${gbp(x.cur)}</div></div>
       <div class="box"><div class="lab">Drop</div><div class="big" style="color:var(--crit)">${x.drop.toFixed(1)}%</div><div class="ds">vs previous 30 days</div></div>
     </div>
     <div class="cmp">
       ${pair('Sales £',x.prev,x.cur,gbp0)}
       ${pair('Units sold',x.prev_units,x.cur_units,num)}
       ${pair('Impressions',x.prev_impr,x.cur_impr,num)}
       ${pair('Views / clicks',x.prev_views,x.cur_views,num)}
       ${pair('PPC spend',x.prev_ppc_spend,x.cur_ppc_spend,gbp0)}
       ${pair('PPC sales',x.prev_ppc_sales,x.cur_ppc_sales,gbp0)}
     </div>
     <div class="mini">
       <div class="m"><div class="l">CTR</div><div class="n">${ctr}</div></div>
       <div class="m"><div class="l">CVR</div><div class="n">${cvr}</div></div>
       <div class="m"><div class="l">ROAS</div><div class="n">${roas}</div></div>
       <div class="m"><div class="l">Stock (UK)</div><div class="n" style="color:${x.stock===0?'var(--crit)':'inherit'}">${num(x.stock)}</div></div>
       <div class="m"><div class="l">Prev units</div><div class="n">${num(x.prev_units)}</div></div>
       <div class="m"><div class="l">Now units</div><div class="n">${num(x.cur_units)}</div></div>
     </div>
     <div class="callout"><div class="r">Why · ${esc(x.reason)}</div><div class="a">${esc(x.action)}</div>
       <div class="rr">Recommended next step for this SKU.</div></div>
   </div>`;
  d.classList.add('open');document.getElementById('scrim').classList.add('open');
}
function closeDrawer(){document.getElementById('drawer').classList.remove('open');document.getElementById('scrim').classList.remove('open');}
document.getElementById('scrim').onclick=closeDrawer;
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeDrawer();});
function csv(){
  const r=view();const H=['Rank','SKU','Item ID','Product','Prev £','Curr £','Loss £','Drop %','CTR %','CVR %','ROAS','Stock','Priority','Reason','Action'];
  const F=x=>[x.rank,x.sku,x.item_id,x.product,x.prev,x.cur,x.loss,x.drop,x.ctr??'n/a',x.cvr??'n/a',x.roas??'n/a',x.stock,PLABEL[x.prio],x.reason,x.action];
  const lines=[H.join(',')].concat(r.map(x=>F(x).map(v=>{v=String(v).replace(/"/g,'""');return /[",\n]/.test(v)?`"${v}"`:v;}).join(',')));
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([lines.join('\n')],{type:'text/csv'}));
  a.download='ebay_uk_top50_sales_drop.csv';a.click();
}
document.getElementById('q').oninput=e=>{state.q=e.target.value;render();};
document.getElementById('chips').onclick=e=>{const c=e.target.closest('.chip');if(!c)return;
  state.prio=c.dataset.p;document.querySelectorAll('.chip').forEach(k=>k.dataset.active=(k===c?'1':''));render();};
// --- extra filters ---
const actions=[...new Set(DATA.rows.map(x=>x.action))].sort();
const aF=document.getElementById('actionF');
actions.forEach(a=>{const o=document.createElement('option');o.value=a;o.textContent=a;aF.appendChild(o);});
aF.onchange=e=>{state.action=e.target.value;render();};
document.getElementById('adF').onchange=e=>{state.ad=e.target.value;render();};
const stockBtn=document.getElementById('stockF');
stockBtn.onclick=()=>{state.stock0=!state.stock0;stockBtn.dataset.on=state.stock0?'1':'';render();};
document.getElementById('clearF').onclick=()=>{
  state={q:'',prio:'all',sort:state.sort,dir:state.dir,action:'all',ad:'all',stock0:false,minloss:0};
  document.getElementById('q').value='';aF.value='all';document.getElementById('adF').value='all';
  stockBtn.dataset.on='';
  document.querySelectorAll('.chip').forEach(k=>k.dataset.active=(k.dataset.p==='all'?'1':''));render();};
document.getElementById('csvBtn').onclick=csv;
document.getElementById('fsBtn').onclick=()=>{if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen();};
(()=>{const MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const fmt=s=>{const p=s.split('-');return (+p[2])+' '+MON[+p[1]-1];};
  const el=document.getElementById('periods');
  el.textContent=fmt(DATA.cur[0])+' – '+fmt(DATA.cur[1])+' '+DATA.cur[1].slice(0,4);
  el.title='Current '+DATA.cur[0]+' → '+DATA.cur[1]+'   ·   Previous '+DATA.prev[0]+' → '+DATA.prev[1];})();
render();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
