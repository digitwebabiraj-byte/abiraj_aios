#!/usr/bin/env python3
"""
render_epns_dashboard.py — REQ-22-D01 eBay Product Net Sales dashboard.
Reads the settled rows (list of dicts, same shape as epns_build_d01.SQL output) and writes a
single self-contained, modern light-theme HTML file (no external CDNs — portal-safe).

Usage (from JSON):
  python -c "import json,render_epns_dashboard as r; r.render(json.load(open('rows.json'))['data']['rows'],'out.html')"
"""
import json, os, datetime as dt

CUR_SYM = {"GBP": "£", "EUR": "€", "USD": "$"}
_FONT_CSS_PATHS = [
    os.path.join(os.path.dirname(__file__), "epns_fonts.css"),
]

def _font_css():
    for p in _FONT_CSS_PATHS:
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                return fh.read()
    return ""  # graceful: falls back to the system stack

def _f(v):
    try: return float(v)
    except (TypeError, ValueError): return 0.0

def summarise(rows):
    by = {}
    for r in rows:
        c = r.get("currency") or "?"
        s = by.setdefault(c, {"orders":0,"gross":0.0,"fvf":0.0,"ppc":0.0,"gen":0.0,"net":0.0,"profit":0.0})
        s["orders"] += 1
        s["gross"]  += _f(r.get("gross_sales"))
        s["fvf"]    += _f(r.get("final_value_fee"))
        s["ppc"]    += _f(r.get("ppc_cost"))
        s["gen"]    += _f(r.get("general"))
        s["net"]    += _f(r.get("net_sales_nnv"))
        s["profit"] += _f(r.get("net_profit_est"))
    return by

def render(rows, out_path):
    anchor = dt.date.today().isoformat()
    summ = summarise(rows)
    # order currencies by gross desc
    order = sorted(summ.keys(), key=lambda c: -summ[c]["gross"])
    data_json = json.dumps(rows, separators=(",", ":"))
    summ_json = json.dumps({c: summ[c] for c in order}, separators=(",", ":"))
    accounts = sorted({(r.get("account") or "") for r in rows})
    markets  = sorted({(r.get("marketplace") or "") for r in rows})
    acct_opts = "".join(f"<option value='{a}'>{a}</option>" for a in accounts if a)
    mkt_opts  = "".join(f"<option value='{m}'>{m}</option>" for m in markets if m)

    html = HTML_TEMPLATE
    html = html.replace("/*__FONTS__*/", _font_css())
    html = html.replace("__ANCHOR__", anchor)
    html = html.replace("__NROWS__", str(len(rows)))
    html = html.replace("__ACCT_OPTS__", acct_opts)
    html = html.replace("__MKT_OPTS__", mkt_opts)
    html = html.replace("__DATA__", data_json)
    html = html.replace("__SUMM__", summ_json)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out_path


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>eBay Product Net Sales — Kobiga · REQ-22-D01</title>
<style>
/*__FONTS__*/
:root{
  --font:'Manrope',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
  --display:'Sora','Manrope',-apple-system,"Segoe UI",Arial,sans-serif;
  --bg:#f4f7fb; --bg2:#eaf0f9; --card:#ffffff; --ink:#0f2540; --muted:#6a7a92;
  --line:#e6ecf5; --accent:#3b6ef6; --accent2:#7c5cff; --good:#12b26b; --good-bg:#e7f8f0;
  --warn:#e0532f; --warn-bg:#fdeee9; --chip:#eef3fc; --shadow:0 2px 6px rgba(16,26,44,.06),0 16px 40px rgba(16,26,44,.07);
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;height:100%}
body{font-family:var(--font);color:var(--ink);height:100vh;overflow:hidden;position:relative;
  background:#eef2fb;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
/* animated gradient mesh background */
body::before{content:"";position:fixed;inset:-20%;z-index:-2;
  background:
    radial-gradient(42% 42% at 18% 20%,rgba(59,110,246,.30),transparent 60%),
    radial-gradient(40% 40% at 82% 12%,rgba(124,92,255,.28),transparent 60%),
    radial-gradient(44% 44% at 75% 85%,rgba(18,178,107,.20),transparent 62%),
    radial-gradient(40% 40% at 12% 88%,rgba(80,170,255,.20),transparent 60%);
  filter:saturate(1.05);animation:mesh 22s ease-in-out infinite alternate}
body::after{content:"";position:fixed;inset:0;z-index:-1;background:linear-gradient(180deg,rgba(255,255,255,.55),rgba(255,255,255,.72))}
/* full-viewport flex column: header + kpis fixed, table fills the rest */
.wrap{height:100vh;max-width:1760px;margin:0 auto;padding:14px 22px;display:flex;flex-direction:column;gap:12px}
header.top{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;
  animation:drop .55s cubic-bezier(.2,.8,.2,1) both}
.title h1{margin:0;font-family:var(--display);font-size:21px;letter-spacing:-.5px;font-weight:800;display:flex;align-items:center;gap:9px;
  background:linear-gradient(90deg,#3b6ef6,#7c5cff,#12b26b,#3b6ef6);background-size:300% auto;
  -webkit-background-clip:text;background-clip:text;color:transparent;animation:hue 9s linear infinite}
.title p{margin:4px 0 0;color:var(--muted);font-size:11.5px;max-width:950px;line-height:1.45}
.badge{display:inline-flex;align-items:center;gap:6px;background:linear-gradient(135deg,#e7f8f0,#d4f3e4);color:#0e9257;
  font-weight:800;font-size:11px;padding:4px 11px;border-radius:999px;margin-right:6px;box-shadow:0 2px 8px rgba(18,178,107,.18)}
.badge .dot{width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 0 0 rgba(18,178,107,.6);animation:ring 1.8s ease-out infinite}
.tools{display:flex;gap:9px;align-items:center}
.btn{border:1px solid rgba(255,255,255,.7);background:rgba(255,255,255,.6);backdrop-filter:blur(10px);color:var(--ink);
  font-weight:700;font-size:12.5px;padding:9px 14px;border-radius:12px;cursor:pointer;box-shadow:var(--shadow);
  transition:.2s cubic-bezier(.2,.8,.2,1);display:inline-flex;gap:6px;align-items:center}
.btn:hover{transform:translateY(-2px);color:var(--accent);box-shadow:0 12px 26px rgba(59,110,246,.2)}
.btn:active{transform:translateY(0)}
.btn.primary{background:linear-gradient(135deg,#3b6ef6,#7c5cff);color:#fff;border:none;background-size:180% auto;
  box-shadow:0 8px 22px rgba(92,92,255,.34)}
.btn.primary:hover{filter:brightness(1.07);color:#fff;background-position:right center;box-shadow:0 14px 30px rgba(92,92,255,.42)}

.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
.kpi{position:relative;overflow:hidden;background:rgba(255,255,255,.62);backdrop-filter:blur(16px) saturate(1.2);
  border:1px solid rgba(255,255,255,.75);border-radius:18px;padding:12px 15px 13px;
  box-shadow:0 1px 2px rgba(16,26,44,.05),0 16px 40px -16px rgba(16,26,44,.28);
  animation:rise .55s cubic-bezier(.2,.8,.2,1) both;transition:.25s cubic-bezier(.2,.8,.2,1)}
.kpi:hover{transform:translateY(-4px);box-shadow:0 1px 2px rgba(16,26,44,.05),0 26px 50px -18px rgba(16,26,44,.34)}
.kpi:nth-child(2){animation-delay:.07s}.kpi:nth-child(3){animation-delay:.14s}
.kpi:nth-child(4){animation-delay:.21s}.kpi:nth-child(5){animation-delay:.28s}.kpi:nth-child(6){animation-delay:.35s}
.kpi .strip{position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--g1),var(--g2))}
.kpi::after{content:"";position:absolute;top:0;left:-120%;width:55%;height:100%;
  background:linear-gradient(100deg,transparent,rgba(255,255,255,.65),transparent);transform:skewX(-18deg);animation:sheen 5s ease-in-out infinite}
.kpi .lab{font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);font-weight:800}
.kpi .val{font-family:var(--display);font-size:24px;font-weight:800;margin-top:3px;letter-spacing:-.8px;line-height:1.12;font-variant-numeric:tabular-nums;
  background:linear-gradient(120deg,var(--g1),var(--g2));-webkit-background-clip:text;background-clip:text;color:transparent}
.kpi .sub{font-size:10.5px;color:var(--muted);margin-top:2px}
.kpi .cchip{position:absolute;top:11px;right:12px;font-size:10px;font-weight:900;color:#fff;
  background:linear-gradient(135deg,var(--g1),var(--g2));padding:3px 9px;border-radius:8px;box-shadow:0 4px 10px -2px var(--g2)}
.kpi .bar{height:6px;border-radius:6px;background:rgba(16,26,44,.07);margin-top:9px;overflow:hidden}
.kpi .bar>i{display:block;height:100%;width:0;border-radius:6px;background:linear-gradient(90deg,var(--g1),var(--g2));
  box-shadow:0 0 12px -2px var(--g2);animation:grow 1.15s .25s cubic-bezier(.2,.8,.2,1) forwards}
.kpi.gbp{--g1:#3b6ef6;--g2:#63b3ff}.kpi.eur{--g1:#7c5cff;--g2:#b07bff}
.kpi.usd{--g1:#12b26b;--g2:#4fd68f}.kpi.other{--g1:#5b6b82;--g2:#93a2b8}

.panel{flex:1;min-height:0;display:flex;flex-direction:column;background:rgba(255,255,255,.72);backdrop-filter:blur(18px) saturate(1.2);
  border:1px solid rgba(255,255,255,.8);border-radius:20px;box-shadow:0 1px 2px rgba(16,26,44,.05),0 24px 60px -24px rgba(16,26,44,.34);
  overflow:hidden;animation:fade .65s .1s ease both}
.controls{display:flex;gap:9px;flex-wrap:wrap;align-items:center;padding:11px 15px;border-bottom:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.7),rgba(247,250,255,.6))}
.search{flex:1;min-width:220px;display:flex;align-items:center;gap:9px;background:#fff;border:1px solid var(--line);
  border-radius:12px;padding:9px 13px;transition:.2s}
.search input{border:none;outline:none;font-size:13.5px;width:100%;background:transparent;color:var(--ink)}
select{border:1px solid var(--line);background:#fff;border-radius:12px;padding:9px 12px;font-size:13px;color:var(--ink);
  cursor:pointer;outline:none;transition:.2s}
select:focus,.search:focus-within{border-color:var(--accent);box-shadow:0 0 0 3.5px rgba(59,110,246,.16)}
.count{font-size:12px;color:var(--muted);font-weight:700;white-space:nowrap}

.tablewrap{flex:1;min-height:0;overflow:auto}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:13px}
thead th{position:sticky;top:0;z-index:2;background:linear-gradient(180deg,#eef4ff,#e7eeff);text-align:right;padding:11px 12px;font-size:11px;
  text-transform:uppercase;letter-spacing:.5px;color:#41527a;font-weight:800;
  box-shadow:inset 0 -1px 0 rgba(59,110,246,.18),0 8px 14px -10px rgba(16,26,44,.2);
  cursor:pointer;white-space:nowrap;user-select:none;transition:.15s}
thead th.l{text-align:left}
thead th:hover{color:var(--accent);background:linear-gradient(180deg,#e6efff,#dce8ff)}
thead th .ar{opacity:.5;font-size:10px}
tbody td{padding:9px 12px;text-align:right;border-bottom:1px solid #eef3fa;white-space:nowrap;transition:background .15s}
tbody td.l{text-align:left}
tbody tr{animation:slidein .34s cubic-bezier(.2,.8,.2,1) both}
tbody tr:nth-child(even) td{background:rgba(244,248,255,.5)}
tbody tr:hover td{background:linear-gradient(90deg,rgba(59,110,246,.09),rgba(124,92,255,.05))}
tbody tr:hover{box-shadow:inset 3px 0 0 var(--accent)}
.mono{font-variant-numeric:tabular-nums}
.pill{display:inline-block;padding:2px 10px;border-radius:999px;font-size:11px;font-weight:800}
.pill.uk{background:linear-gradient(135deg,#e7efff,#dbe8ff);color:#2b5bd7}
.pill.de{background:linear-gradient(135deg,#fff0e4,#ffe6d3);color:#c9631d}
.pill.us{background:linear-gradient(135deg,#e6faf0,#d6f6e5);color:#0e9257}
.pill.other{background:#eef1f6;color:#5b6b82}
.sku{color:var(--muted);max-width:250px;overflow:hidden;text-overflow:ellipsis;display:inline-block;vertical-align:bottom}
.net{font-weight:900;background:linear-gradient(120deg,#0e9257,#20c47d);-webkit-background-clip:text;background-clip:text;color:transparent}
.fee{color:var(--warn)}
.netcell{position:relative}
.netcell .mag{position:absolute;left:0;bottom:1px;height:3px;border-radius:3px;width:0;
  background:linear-gradient(90deg,#4fd68f,#0e9257);box-shadow:0 0 8px -1px rgba(18,178,107,.5);opacity:.7;animation:barin .6s cubic-bezier(.2,.8,.2,1) forwards}
.est{color:#8a79d6}
.pager{display:flex;justify-content:space-between;align-items:center;padding:10px 15px;border-top:1px solid var(--line);
  background:linear-gradient(180deg,rgba(255,255,255,.7),rgba(246,250,255,.6))}
.pg{display:flex;gap:6px;align-items:center}
.pg button{border:1px solid var(--line);background:#fff;border-radius:10px;padding:7px 12px;cursor:pointer;font-weight:700;font-size:12.5px;transition:.15s}
.pg button:hover:not(:disabled){border-color:var(--accent);color:var(--accent);transform:translateY(-1px)}
.pg button:disabled{opacity:.4;cursor:default}
.foot{color:var(--muted);font-size:10.5px;line-height:1.45}
.foot b{color:var(--ink)}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes drop{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
@keyframes rise{from{opacity:0;transform:translateY(14px) scale(.98)}to{opacity:1;transform:none}}
@keyframes slidein{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes grow{from{width:0}}
@keyframes barin{from{width:0}}
@keyframes hue{to{background-position:300% center}}
@keyframes sheen{0%,58%{left:-120%}82%,100%{left:135%}}
@keyframes ring{0%{box-shadow:0 0 0 0 rgba(18,178,107,.55)}70%,100%{box-shadow:0 0 0 7px rgba(18,178,107,0)}}
@keyframes mesh{0%{transform:translate(0,0) scale(1)}50%{transform:translate(2%,-1.5%) scale(1.05)}100%{transform:translate(-2%,1.5%) scale(1.02)}}
</style>
</head>
<body>
<div class="wrap" id="app">
  <header class="top">
    <div class="title">
      <h1>◆ eBay Product Net Sales</h1>
      <p><span class="badge"><span class="dot"></span>SETTLED ONLY</span> Kobiga · REQ-22-D01 · last 30 days ending __ANCHOR__ ·
         <b>__NROWS__</b> settled orders · ties to eBay (VAT-inclusive fees) · per-currency, never blended.</p>
    </div>
    <div class="tools">
      <button class="btn" id="csv">⇩ CSV</button>
      <button class="btn primary" id="fs">⛶ Full screen</button>
    </div>
  </header>

  <section class="kpis" id="kpis"></section>

  <section class="panel">
    <div class="controls">
      <label class="search">🔍<input id="q" type="search" placeholder="Search order ID, SKU or account…"></label>
      <select id="fCur"><option value="">All currencies</option></select>
      <select id="fMkt"><option value="">All marketplaces</option>__MKT_OPTS__</select>
      <select id="fAcct"><option value="">All accounts</option>__ACCT_OPTS__</select>
      <span class="count" id="count"></span>
    </div>
    <div class="tablewrap">
      <table>
        <thead><tr id="head"></tr></thead>
        <tbody id="body"></tbody>
      </table>
    </div>
    <div class="pager">
      <span class="count" id="pinfo"></span>
      <div class="pg">
        <button id="prev">‹ Prev</button>
        <span class="count" id="pnum"></span>
        <button id="next">Next ›</button>
      </div>
    </div>
  </section>

  <div class="foot">
    <b>Net Sales (NNV)</b> = Gross − Final Value Fee − PPC − General (eBay net payout; ties to eBay's SALE transaction & "Total fees incl VAT").
    <b>Output VAT (20%)</b> is a derived estimate on the sale price (info only, not deducted, ≠ eBay's fee-VAT).
    <b>Product Cost</b> = 20% of price (owner-agreed proxy, no real COGS) → <b>Net Profit [est]</b> = NNV − Output VAT − Product Cost.
    Unsettled/very recent orders are excluded until eBay books their fees.
  </div>
</div>

<script>
const DATA = __DATA__;
const SUMM = __SUMM__;
const SYM = {GBP:"£",EUR:"€",USD:"$"};
// Ordered to match the source sheet's 12 columns (Order ID … Net Sales), plus Date/Market/Net Profit extras.
const COLS = [
  {k:"order_date",t:"Date",l:true},
  {k:"order_id",t:"Order ID",l:true},          // src 1
  {k:"sku",t:"SKU",l:true,sku:true},           // src 2
  {k:"account",t:"Account",l:true},            // src 3
  {k:"marketplace",t:"Market",l:true,pill:true},
  {k:"gross_sales",t:"Gross Sales",m:1},       // src 4
  {k:"vat_20",t:"VAT (20%)·est",m:1,est:1},    // src 5
  {k:"promotion",t:"Promotion",m:1},           // src 6
  {k:"final_value_fee",t:"Final Value Fee",m:1,fee:1}, // src 7
  {k:"product_cost",t:"Product Cost·est",m:1,est:1},   // src 8
  {k:"postage",t:"Postage",m:1},               // src 9
  {k:"ppc_cost",t:"PPC Cost",m:1,fee:1},       // src 10
  {k:"general",t:"General",m:1,fee:1},         // src 11
  {k:"net_sales_nnv",t:"Net Sales (NNV)",m:1,net:1},   // src 12
  {k:"net_profit_est",t:"Net Profit·est",m:1,est:1},
];
const PAGE=100;
let state={q:"",cur:"",mkt:"",acct:"",sort:"order_date",dir:-1,page:0,rows:DATA};
const $=s=>document.querySelector(s);
const fmt=(v,c)=> (SYM[c]||"")+ (Number(v)||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});

// ---- KPI tiles per currency ----
function kpis(){
  const box=$("#kpis");box.innerHTML="";
  const curs=Object.keys(SUMM);
  // currency filter options
  const fc=$("#fCur");curs.forEach(c=>{const o=document.createElement("option");o.value=c;o.textContent=c;fc.appendChild(o);});
  const CLS={GBP:"gbp",EUR:"eur",USD:"usd"};
  curs.forEach(c=>{
    const s=SUMM[c], feeRate=s.gross?(100*(s.fvf+s.ppc+s.gen)/s.gross):0, netRate=s.gross?(100*s.net/s.gross):0;
    const el=document.createElement("div");el.className="kpi "+(CLS[c]||"other");
    el.innerHTML=`<span class="strip"></span><span class="cchip">${c}</span>
      <div class="lab">Net Sales · ${s.orders} orders</div>
      <div class="val" data-count="${s.net}" data-cur="${c}">${SYM[c]}0.00</div>
      <div class="sub">Gross ${fmt(s.gross,c)} · fees ${fmt(s.fvf+s.ppc+s.gen,c)} (${feeRate.toFixed(1)}%)</div>
      <div class="bar"><i style="--w:${netRate.toFixed(1)}%"></i></div>`;
    box.appendChild(el);
  });
  // bars + count-up
  document.querySelectorAll(".bar>i").forEach(i=>{i.style.width=i.style.getPropertyValue("--w");});
  animateCounts();
}
function animateCounts(){
  document.querySelectorAll("[data-count]").forEach(el=>{
    const end=+el.dataset.count, c=el.dataset.cur, dur=900, t0=performance.now();
    (function step(t){const p=Math.min(1,(t-t0)/dur), e=1-Math.pow(1-p,3);
      el.textContent=fmt(end*e,c); if(p<1)requestAnimationFrame(step);})(t0);
  });
}

// ---- table ----
function head(){
  const tr=$("#head");tr.innerHTML="";
  COLS.forEach(c=>{
    const th=document.createElement("th");th.className=c.l?"l":"";
    th.innerHTML=c.t+' <span class="ar">'+(state.sort===c.k?(state.dir>0?"▲":"▼"):"")+'</span>';
    th.onclick=()=>{if(state.sort===c.k)state.dir*=-1;else{state.sort=c.k;state.dir=c.m?-1:1;}state.page=0;draw();};
    tr.appendChild(th);
  });
}
function filtered(){
  const q=state.q.toLowerCase();
  let r=DATA.filter(d=>
    (!state.cur||d.currency===state.cur)&&(!state.mkt||d.marketplace===state.mkt)&&(!state.acct||d.account===state.acct)&&
    (!q||(d.order_id+" "+d.sku+" "+d.account).toLowerCase().includes(q)));
  const k=state.sort,dir=state.dir,isNum=COLS.find(c=>c.k===k)?.m;
  r.sort((a,b)=>{let x=a[k],y=b[k]; if(isNum){x=+x;y=+y;} else {x=(x||"")+"";y=(y||"")+"";}
    return x<y?-1*dir:x>y?1*dir:0;});
  return r;
}
function draw(){
  head();
  const rows=filtered(); state.rows=rows;
  const maxNet=Math.max(1,...rows.slice(0,400).map(r=>+r.net_sales_nnv||0));
  const pages=Math.max(1,Math.ceil(rows.length/PAGE));
  if(state.page>=pages)state.page=pages-1;
  const slice=rows.slice(state.page*PAGE,state.page*PAGE+PAGE);
  const b=$("#body");b.innerHTML="";
  slice.forEach((d,i)=>{
    const tr=document.createElement("tr");tr.style.animationDelay=(i*8)+"ms";
    COLS.forEach(c=>{
      const td=document.createElement("td");td.className=c.l?"l":"mono";
      let v=d[c.k];
      if(c.pill){const m=(d.marketplace||"").toLowerCase();const cls=m==="uk"?"uk":m==="germany"?"de":m==="us"?"us":"other";
        td.innerHTML=`<span class="pill ${cls}">${d.marketplace||"?"}</span>`;}
      else if(c.sku){td.innerHTML=`<span class="sku" title="${(v||'').replace(/"/g,'&quot;')}">${v||""}</span>`;}
      else if(c.m){const cur=d.currency;td.textContent=fmt(v,cur);
        if(c.fee&&+v>0)td.classList.add("fee");
        if(c.est)td.classList.add("est");
        if(c.net){td.classList.add("net","netcell");
          const w=Math.max(3,100*(+v||0)/maxNet);
          const mag=document.createElement("span");mag.className="mag";mag.style.width=w+"%";td.appendChild(mag);}
      } else td.textContent=v||"";
      tr.appendChild(td);
    });
    b.appendChild(tr);
  });
  $("#count").textContent=rows.length.toLocaleString()+" orders";
  $("#pinfo").textContent=rows.length?`Showing ${state.page*PAGE+1}–${Math.min(rows.length,state.page*PAGE+PAGE)} of ${rows.length.toLocaleString()}`:"No orders match";
  $("#pnum").textContent=`Page ${state.page+1} / ${pages}`;
  $("#prev").disabled=state.page<=0;$("#next").disabled=state.page>=pages-1;
}

// ---- events ----
$("#q").oninput=e=>{state.q=e.target.value;state.page=0;draw();};
$("#fCur").onchange=e=>{state.cur=e.target.value;state.page=0;draw();};
$("#fMkt").onchange=e=>{state.mkt=e.target.value;state.page=0;draw();};
$("#fAcct").onchange=e=>{state.acct=e.target.value;state.page=0;draw();};
$("#prev").onclick=()=>{if(state.page>0){state.page--;draw();}};
$("#next").onclick=()=>{state.page++;draw();};
$("#fs").onclick=()=>{const a=$("#app");if(!document.fullscreenElement)a.requestFullscreen?.();else document.exitFullscreen?.();};
$("#csv").onclick=()=>{
  const rows=state.rows;const head=COLS.map(c=>c.t).join(",");
  const body=rows.map(d=>COLS.map(c=>{let v=d[c.k]??"";v=(""+v).replace(/"/g,'""');return /[",]/.test(v)?`"${v}"`:v;}).join(",")).join("\n");
  const blob=new Blob([head+"\n"+body],{type:"text/csv"});const u=URL.createObjectURL(blob);
  const a=document.createElement("a");a.href=u;a.download="epns_net_sales.csv";a.click();URL.revokeObjectURL(u);
};

kpis();draw();
</script>
</body>
</html>
"""
