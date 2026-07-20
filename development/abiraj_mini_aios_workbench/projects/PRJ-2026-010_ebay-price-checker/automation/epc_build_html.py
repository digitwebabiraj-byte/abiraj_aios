# -*- coding: utf-8 -*-
"""EPC dashboard UI - SINGLE SOURCE OF TRUTH for the rendered dashboard.
Extracted verbatim from the D01 builder (V3: Export-CSV button + taller bounded table).
Used by epc_weekly_run.py. Edit the template HERE only - never fork it.
    build(payload) -> html   (payload keys: accounts accOrder accStack kpi imgPrefix rows)
"""
import json

HTML = u"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>eBay Price Checker &mdash; Live Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#eef2f8; --surface:#fff; --surface2:#f6f9fc; --ink:#0f1b2d; --ink2:#51607a; --muted:#8a97ad;
  --line:#e6ebf3; --accent:#3b5bdb; --accent2:#6f8bff; --accent-soft:#eaefff;
  --good:#0f9d58; --good-bg:#e6f6ec; --warn:#e8a13a; --warn-bg:#fdf3e3; --bad:#e5484d; --bad-bg:#fdeaea;
  --neutral:#8a97ad; --neutral-bg:#eef1f6; --shadow:0 1px 2px rgba(20,40,80,.05),0 6px 20px rgba(20,40,80,.06);
  --num:ui-monospace,'Cascadia Mono','Consolas','Roboto Mono','Courier New',monospace;
  --head:'Segoe UI Semibold','Segoe UI',system-ui,sans-serif;
  --cols:120px 158px 58px 152px 100px 100px 112px 116px 98px 84px 156px 90px minmax(180px,1fr);
}
html,body{min-height:100%}
body{font-family:'Segoe UI',system-ui,-apple-system,Roboto,Arial,sans-serif;background:var(--bg);color:var(--ink);font-size:13px;-webkit-font-smoothing:antialiased}
.app{display:flex;flex-direction:column;min-height:100vh;padding:14px 18px 12px;gap:11px}

/* ---- splash */
#splash{position:fixed;inset:0;background:linear-gradient(135deg,#f2f6ff,#eaf0fb);display:grid;place-items:center;z-index:99;
  transition:opacity .5s ease,visibility .5s}
#splash.hidden{opacity:0;visibility:hidden}
.sp{display:flex;flex-direction:column;align-items:center;gap:16px}
.spin{width:44px;height:44px;border:4px solid var(--accent-soft);border-top-color:var(--accent);border-radius:50%;animation:spin .8s linear infinite}
.sp p{color:var(--ink2);font-weight:600;font-size:13px}
@keyframes spin{to{transform:rotate(360deg)}}

/* ---- appbar */
.appbar{display:flex;align-items:center;gap:16px;flex:none;animation:slideDown .5s ease both}
.brand{display:flex;align-items:center;gap:12px;flex:none}
.logo{width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:grid;place-items:center;
  color:#fff;font-size:20px;box-shadow:0 6px 16px rgba(59,91,219,.35);animation:pop .6s cubic-bezier(.2,1.4,.4,1) both}
.brand h1{font-family:var(--head);font-size:18px;font-weight:800;letter-spacing:-.02em;line-height:1;
  background:linear-gradient(92deg,#2440c4,#7a4de0);-webkit-background-clip:text;background-clip:text;color:transparent}
.brand p{color:var(--ink2);font-size:11px;margin-top:3px;font-weight:500}
.pills{display:flex;gap:9px;flex:1;overflow:hidden}
.pill{flex:1;min-width:0;background:var(--surface);border:1px solid var(--line);border-radius:13px;padding:8px 12px;box-shadow:var(--shadow);
  cursor:pointer;position:relative;overflow:hidden;transition:transform .16s,box-shadow .16s,border-color .16s;animation:fadeUp .5s ease both}
.pill:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(20,40,80,.12)}
.pill.active{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-soft)}
.pill:nth-child(1){animation-delay:.04s}.pill:nth-child(2){animation-delay:.08s}.pill:nth-child(3){animation-delay:.12s}
.pill:nth-child(4){animation-delay:.16s}.pill:nth-child(5){animation-delay:.20s}
.pill .rail{position:absolute;left:0;top:0;bottom:0;width:4px}
.pill.p-tot .rail{background:var(--accent)}.pill.p-norm .rail{background:var(--good)}.pill.p-high .rail{background:var(--bad)}
.pill.p-low .rail{background:var(--warn)}.pill.p-miss .rail{background:var(--neutral)}
.pill .l{display:flex;align-items:center;gap:6px;color:var(--ink2);font-size:10.5px;font-weight:700;white-space:nowrap;text-transform:uppercase;letter-spacing:.03em}
.pill .n{font-family:var(--num);font-size:22px;font-weight:800;letter-spacing:-.02em;font-variant-numeric:tabular-nums;margin-top:2px}
.pill.p-norm .n{color:var(--good)}.pill.p-high .n{color:var(--bad)}.pill.p-low .n{color:#b9791a}.pill.p-miss .n{color:var(--ink2)}.pill.p-tot .n{color:var(--accent)}
.pill .p{font-size:10px;color:var(--muted);font-weight:600}
.actions{display:flex;gap:8px;flex:none}
.btn{display:flex;align-items:center;gap:7px;padding:9px 14px;border:1px solid var(--line);border-radius:11px;background:var(--surface);
  font-size:12.5px;font-weight:600;color:var(--ink2);cursor:pointer;box-shadow:var(--shadow);transition:all .15s;white-space:nowrap}
.btn:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-1px)}
.btn.primary{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-color:transparent}
.btn.primary:hover{color:#fff;box-shadow:0 8px 20px rgba(59,91,219,.4)}
.btn.ins{background:var(--accent-soft);color:var(--accent);border-color:#c3d1ff;font-weight:700;animation:insHint 1.6s ease-in-out 3}
.btn.ins:hover{background:#dde5ff;color:var(--accent);border-color:var(--accent)}
.btn.ins .bico{font-size:14px}
.btn.ins .chev{font-size:9px;transition:transform .3s;opacity:.7}
.btn.ins.open .chev{transform:rotate(180deg)}
.btn.export{background:var(--good-bg);color:var(--good);border-color:#bfe6cd;font-weight:700}
.btn.export:hover{background:#d5f0df;color:var(--good);border-color:var(--good)}
.btn.export .bico{font-size:13px}
@keyframes insHint{0%,100%{box-shadow:0 0 0 0 rgba(59,91,219,0)}50%{box-shadow:0 0 0 6px rgba(59,91,219,.16)}}

/* ---- insights drawer */
.insights{flex:none;max-height:0;overflow:hidden;transition:max-height .45s cubic-bezier(.2,.8,.2,1),margin .3s;margin-top:-3px}
.insights.open{max-height:320px}
.insGrid{display:grid;grid-template-columns:290px 1fr;gap:12px;padding-top:3px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px 16px;box-shadow:var(--shadow)}
.card h3{font-family:var(--head);font-size:12px;color:#2a3852;font-weight:800;text-transform:uppercase;letter-spacing:.04em;margin-bottom:12px;display:flex;justify-content:space-between}
.card h3 span{color:var(--muted);font-weight:500}
.donutWrap{display:flex;align-items:center;gap:14px}
.donut{width:118px;height:118px;border-radius:50%;position:relative;flex:none;transition:background 1s cubic-bezier(.2,.8,.2,1)}
.donut::after{content:"";position:absolute;inset:14px;background:var(--surface);border-radius:50%}
.donut .c{position:absolute;inset:0;display:grid;place-items:center;z-index:2;text-align:center}
.donut .c b{font-size:20px;font-weight:800}.donut .c span{font-size:9px;color:var(--muted);display:block}
.leg{display:flex;flex-direction:column;gap:6px;flex:1}
.li{display:flex;align-items:center;gap:8px;font-size:11.5px;cursor:pointer;padding:3px 5px;border-radius:7px;transition:background .15s}
.li:hover{background:var(--surface2)}.li .sw{width:10px;height:10px;border-radius:3px;flex:none}.li .v{margin-left:auto;font-weight:700;font-variant-numeric:tabular-nums}
.bars{display:flex;flex-direction:column;gap:6px;max-height:238px;overflow-y:auto;padding-right:6px}
.bars::-webkit-scrollbar{width:8px}.bars::-webkit-scrollbar-thumb{background:#cdd6e6;border-radius:6px}.bars::-webkit-scrollbar-thumb:hover{background:var(--accent)}
.brow{display:grid;grid-template-columns:128px 1fr 50px;align-items:center;gap:10px;font-size:11px;cursor:pointer}
.brow:hover .nm{color:var(--accent)}
.brow .nm{color:var(--ink2);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:color .15s}
.bar{height:15px;border-radius:5px;background:var(--surface2);display:flex;overflow:hidden}
.bar span{height:100%;display:block;transition:width 1s cubic-bezier(.2,.8,.2,1)}
.bar .s0{background:var(--good)}.bar .s1{background:var(--bad)}.bar .s2{background:var(--warn)}.bar .s3{background:#cbd3e0}
.brow .tot{text-align:right;font-weight:700;color:var(--ink2);font-variant-numeric:tabular-nums}

/* ---- toolbar */
.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:9px;flex:none;animation:fadeUp .5s .12s ease both}
.search{flex:1;min-width:220px;position:relative}
.search input{width:100%;padding:9px 12px 9px 34px;border:1px solid var(--line);border-radius:10px;background:var(--surface);font-size:13px;color:var(--ink);outline:none;transition:border .15s,box-shadow .15s}
.search input:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
.search .ic{position:absolute;left:11px;top:50%;transform:translateY(-50%);color:var(--muted)}
select{padding:9px 11px;border:1px solid var(--line);border-radius:10px;background:var(--surface);font-size:12.5px;color:var(--ink);outline:none;cursor:pointer;transition:border .15s}
select:focus{border-color:var(--accent)}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{padding:8px 12px;border:1px solid var(--line);border-radius:99px;background:var(--surface);font-size:11.5px;font-weight:600;cursor:pointer;color:var(--ink2);transition:all .15s;user-select:none;white-space:nowrap}
.chip:hover{border-color:var(--accent);transform:translateY(-1px)}
.chip.on{color:#fff;border-color:transparent}
.chip.on.c-all{background:var(--accent)}.chip.on.c0{background:var(--good)}.chip.on.c1{background:var(--bad)}.chip.on.c2{background:var(--warn)}.chip.on.c3{background:var(--neutral)}

/* ---- table fills viewport */
.tableCard{height:calc(100vh - 210px);min-height:600px;display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--line);border-radius:14px;
  box-shadow:var(--shadow);overflow:hidden;position:relative;animation:fadeUp .5s .16s ease both}
.tableCard::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;z-index:8;
  background:linear-gradient(90deg,var(--good) 0%,var(--good) 17%,var(--bad) 17%,var(--bad) 49%,var(--warn) 49%,var(--warn) 66%,#cbd3e0 66%)}
.tscroll{flex:1;min-height:0;overflow:auto;position:relative}
.tscroll::-webkit-scrollbar{width:12px;height:12px}
.tscroll::-webkit-scrollbar-track{background:var(--surface2)}
.tscroll::-webkit-scrollbar-thumb{background:#c4cfe2;border-radius:8px;border:3px solid var(--surface2)}
.tscroll::-webkit-scrollbar-thumb:hover{background:var(--accent)}
.tinner{min-width:1544px;position:relative}
.thead{display:grid;grid-template-columns:var(--cols);position:sticky;top:0;z-index:6;
  background:linear-gradient(180deg,#fbfcfe,#f4f7fb);border-bottom:2px solid var(--line)}
.th{font-family:var(--head);padding:12px 12px;font-size:10.5px;font-weight:800;color:#3a4a63;text-transform:uppercase;letter-spacing:.05em;cursor:pointer;user-select:none;
  white-space:nowrap;display:flex;align-items:center;gap:5px;transition:color .15s}
.th:hover{color:var(--accent);background:rgba(59,91,219,.06)}.th.r{justify-content:flex-end}.th.c{justify-content:center}
.th .ar{opacity:.3;font-size:8px;transition:opacity .15s,transform .2s}
.th.sorted{color:var(--accent);box-shadow:inset 0 -3px 0 var(--accent)}.th.sorted .ar{opacity:1}
.th.desc .ar{transform:rotate(0)}.th.asc .ar{transform:rotate(180deg)}
#spacer{position:relative;width:100%}
.trow{position:absolute;left:0;right:0;display:grid;grid-template-columns:var(--cols);align-items:center;height:46px;
  border-bottom:1px solid var(--line);transition:background .12s,box-shadow .12s}
.trow::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;opacity:.9}
.trow.rs0::before{background:var(--good)}.trow.rs1::before{background:var(--bad)}
.trow.rs2::before{background:var(--warn)}.trow.rs3::before{background:#cbd3e0}
.trow:nth-child(even){background:#fbfcfe}
.trow:hover{background:var(--accent-soft);box-shadow:0 4px 16px rgba(59,91,219,.14);z-index:3}
.td{padding:0 12px;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-variant-numeric:tabular-nums}
.td.r{text-align:right;font-family:var(--num);letter-spacing:-.01em}
.td.c{text-align:center}
.id{color:var(--muted);font-size:11px;font-family:var(--num)}
.thumb{width:34px;height:34px;border-radius:8px;object-fit:cover;background:var(--surface2);border:1px solid var(--line);transition:transform .2s}
.thumb:hover{transform:scale(2.4);z-index:9;position:relative;box-shadow:0 8px 24px rgba(0,0,0,.25)}
.sku{font-family:var(--num);font-weight:700;color:#1b2a44;letter-spacing:-.01em}
.acct{color:var(--ink2);font-size:11.5px;font-weight:500}
.dchip{display:inline-block;padding:2px 8px;border-radius:7px;font-weight:800;font-family:var(--num)}
.dchip.dpos{background:var(--bad-bg);color:var(--bad)}.dchip.dneg{background:var(--warn-bg);color:#b9791a}
.badge{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:99px;font-size:10.5px;font-weight:700;white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis}
.b0{background:var(--good-bg);color:var(--good)}.b1{background:var(--bad-bg);color:var(--bad)}.b2{background:var(--warn-bg);color:#b9791a}.b3{background:var(--neutral-bg);color:var(--ink2)}
.pri{display:inline-block;padding:2px 8px;border-radius:6px;font-weight:700;font-size:10.5px}
.pp3{background:var(--bad-bg);color:var(--bad)}.pp2{background:var(--warn-bg);color:#b9791a}.pp1{background:var(--good-bg);color:var(--good)}.pp0{background:var(--neutral-bg);color:var(--muted)}
.diffpos{color:var(--bad);font-weight:700}.diffneg{color:var(--warn);font-weight:700}
.act{color:var(--ink2);font-size:11.5px}
.empty{padding:70px;text-align:center;color:var(--muted);font-size:14px}
.foot{display:flex;justify-content:space-between;align-items:center;padding:9px 16px;border-top:1px solid var(--line);background:var(--surface2);font-size:12px;color:var(--ink2);flex:none}
.foot b{color:var(--ink)}
.warnpin{display:inline-flex;align-items:center;gap:6px;color:#8a5a12;background:var(--warn-bg);border:1px solid #f3dcae;padding:3px 10px;border-radius:99px;font-size:11px;font-weight:600}

@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes slideDown{from{opacity:0;transform:translateY(-10px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:scale(1)}}
@media(max-width:900px){.pills{display:none}.insGrid{grid-template-columns:1fr}}
</style></head>
<body>
<div id="splash"><div class="sp"><div class="spin"></div><p>Loading 126,070 listings&hellip;</p></div></div>

<div class="app">
  <div class="appbar">
    <div class="brand"><div class="logo">&#163;</div>
      <div><h1>eBay Price Checker</h1><p>Cross-channel price drift &middot; UK &amp; Germany &middot; REQ-12-D01</p></div></div>
    <div class="pills" id="pills"></div>
    <div class="actions">
      <button class="btn ins" id="insBtn"><span class="bico">&#128202;</span> Charts &amp; insights <span class="chev">&#9660;</span></button>
      <button class="btn export" id="exportBtn" title="Download the current filtered view as CSV (opens in Excel)"><span class="bico">&#11015;</span> Export CSV</button>
      <button class="btn primary" id="fsBtn">&#9974; Full screen</button>
    </div>
  </div>

  <div class="insights" id="insights"><div class="insGrid">
    <div class="card"><h3>Status mix <span>click to filter</span></h3>
      <div class="donutWrap"><div class="donut" id="donut"><div class="c"><b id="dCenter">0%</b><span>priced OK</span></div></div>
      <div class="leg" id="legend"></div></div></div>
    <div class="card"><h3>By account <span>stacked by status &middot; click a bar to filter</span></h3>
      <div class="bars" id="accBars"></div></div>
  </div></div>

  <div class="toolbar">
    <div class="search"><span class="ic">&#128269;</span><input id="q" placeholder="Search by SKU or eBay item ID&hellip;"></div>
    <select id="accSel"><option value="">All accounts (13)</option></select>
    <select id="regSel"><option value="">UK &amp; Germany</option><option value="0">UK only</option><option value="1">Germany only</option></select>
    <div class="chips" id="statusChips">
      <div class="chip on c-all" data-s="">All</div>
      <div class="chip c0" data-s="0">&#9989; Normal</div>
      <div class="chip c1" data-s="1">&#128308; Too high</div>
      <div class="chip c2" data-s="2">&#128308; Too low</div>
      <div class="chip c3" data-s="3">No comparator</div>
      <div class="chip c3" data-s="4">Bundle</div>
    </div>
    <span class="warnpin">&#9888; shipping-blind &mdash; rank, don't reprice</span>
  </div>

  <div class="tableCard">
    <div class="tscroll" id="tscroll"><div class="tinner">
      <div class="thead" id="thead"></div>
      <div id="spacer"></div>
    </div><div class="empty" id="empty" style="display:none">No listings match your filters.</div></div>
    <div class="foot"><span>Showing <b id="fcount">0</b> of <b id="tcount">0</b> listings</span>
      <span>&#163; UK &middot; &#8364; Germany &middot; source <b>ledsone</b> &middot; refreshed <b>2026-07-15</b></span></div>
  </div>
</div>

<script>
const P=__PAYLOAD__, ROWS=P.rows, ACC=P.accounts, IMGP=P.imgPrefix, K=P.kpi;
const SNAME=["Normal","Too high","Too low","No data"], SCOL=["var(--good)","var(--bad)","var(--warn)","#cbd3e0"];
const BADGE=["\\u2705 Normal","\\ud83d\\udd34 Too high","\\ud83d\\udd34 Too low","No comparator","Bundle"];
const ACTION=["No action required","Reduce eBay price","Increase eBay price","eBay-only \\u2013 no match","Bundle \\u2013 price the kit"];
const PNAME=["\\u2014","Low","Med","High"];
const CUR=r=>r[12]===0?"\\u00a3":"\\u20ac";
const money=(v,r)=>v==null?"\\u2014":CUR(r)+v.toFixed(2);
const pctf=v=>v==null?"\\u2014":(v*100).toFixed(1)+"%";
const nf=n=>n.toLocaleString("en-GB");

/* ---- KPI pills */
const pillDefs=[["p-tot","total","All listings","","\\ud83d\\udce6"],["p-norm","normal","Priced OK","0","\\u2705"],
  ["p-high","high","Too high","1","\\ud83d\\udd34"],["p-low","low","Too low","2","\\ud83d\\udcc9"],["p-miss","miss","Missing target","m","\\u2753"]];
const pills=document.getElementById("pills");
pillDefs.forEach(d=>{
  const v=K[d[1]], pct=((v/K.total)*100).toFixed(1);
  const el=document.createElement("div"); el.className="pill "+d[0]; el.dataset.s=d[3];
  el.innerHTML=`<div class="rail"></div><div class="l">${d[4]} ${d[2]}</div><div class="n" data-to="${v}">0</div>
    <div class="p">${d[1]==="total"?"13 accounts \\u00b7 2 markets":pct+"% of total"}</div>`;
  if(d[3]!=="")el.onclick=()=>setStatus(d[3]===curStatus?"":d[3]);
  pills.appendChild(el);
});

/* ---- donut + legend */
const seg=[K.normal,K.high,K.low,K.miss];
let a=0,stops=[]; seg.forEach((v,i)=>{const p=v/K.total*100;stops.push(`${SCOL[i]} ${a}% ${a+p}%`);a+=p;});
document.getElementById("dCenter").textContent=((K.normal/K.total)*100).toFixed(0)+"%";
const legend=document.getElementById("legend");
["Normal","Too high","Too low","Missing"].forEach((nm,i)=>{
  const code=i===3?"m":String(i);
  const li=document.createElement("div"); li.className="li";
  li.innerHTML=`<span class="sw" style="background:${SCOL[i]}"></span>${nm}<span class="v">${nf(seg[i])}</span>`;
  li.onclick=()=>setStatus(code===curStatus?"":code); legend.appendChild(li);
});

/* ---- account bars */
const accBars=document.getElementById("accBars"), accSel=document.getElementById("accSel");
P.accStack.forEach(a=>{
  const tot=a[1]+a[2]+a[3]+a[4], w=i=>((a[i+1]/tot)*100).toFixed(2);
  const row=document.createElement("div"); row.className="brow";
  row.innerHTML=`<div class="nm" title="${a[0]}">${a[0]}</div><div class="bar">${[0,1,2,3].map(i=>`<span class="s${i}" style="width:0" data-w="${w(i)}"></span>`).join("")}</div><div class="tot">${nf(tot)}</div>`;
  row.onclick=()=>{accSel.value=a[0];applyFilters();};
  accBars.appendChild(row);
});
P.accOrder.forEach(a=>{const o=document.createElement("option");o.value=a;o.textContent=a;accSel.appendChild(o);});

/* ---- table columns (task order) */
const COLS=[
  {h:"ID",k:"id",cls:"",r:d=>`<div class="td id">${d[0]}</div>`},
  {h:"SKU",k:"sku",cls:"",r:d=>`<div class="td"><span class="sku">${d[1]}</span></div>`},
  {h:"Image",k:null,cls:"c",r:d=>{const im=d[2]?(d[2][0]==="!"?d[2].slice(1):IMGP+d[2]):"";return `<div class="td c">${im?`<img class="thumb" loading="lazy" src="${im}" onerror="this.style.visibility='hidden'">`:""}</div>`;}},
  {h:"Account",k:"acct",cls:"",r:d=>`<div class="td acct">${ACC[d[3]]}</div>`},
  {h:"Website Price",k:"wp",cls:"r",r:d=>`<div class="td r">${money(d[4],d)}</div>`},
  {h:"Amazon Price",k:"ap",cls:"r",r:d=>`<div class="td r">${money(d[5],d)}</div>`},
  {h:"Target eBay",k:"tgt",cls:"r",r:d=>`<div class="td r">${money(d[6],d)}</div>`},
  {h:"Current eBay",k:"ebay",cls:"r",r:d=>`<div class="td r" style="font-weight:700">${money(d[7],d)}</div>`},
  {h:"Difference",k:"diff",cls:"r",r:d=>{
     if(d[8]==null)return `<div class="td r" style="color:var(--muted)">\\u2014</div>`;
     const pos=d[8]>0, t=(pos?"+":"")+CUR(d)+d[8].toFixed(2);
     const inner=d[11]===3?`<span class="dchip ${pos?'dpos':'dneg'}">${t}</span>`:`<span class="${pos?'diffpos':'diffneg'}">${t}</span>`;
     return `<div class="td r">${inner}</div>`;}},
  {h:"Diff %",k:"pct",cls:"r",r:d=>`<div class="td r" style="color:var(--ink2)">${pctf(d[9])}</div>`},
  {h:"Status",k:"st",cls:"",r:d=>`<div class="td"><span class="badge b${Math.min(d[10],3)}" title="${BADGE[d[10]]}">${BADGE[d[10]]}</span></div>`},
  {h:"Priority",k:"pri",cls:"c",r:d=>`<div class="td c"><span class="pri pp${d[11]}">${PNAME[d[11]]}</span></div>`},
  {h:"Action",k:"act",cls:"",r:d=>`<div class="td act" title="${ACTION[d[10]]}">${ACTION[d[10]]}</div>`},
];
const KEYIDX={id:0,sku:1,acct:3,wp:4,ap:5,tgt:6,ebay:7,diff:8,pct:9,st:10,pri:11};
const thead=document.getElementById("thead");
COLS.forEach(c=>{
  const th=document.createElement("div"); th.className="th "+c.cls; th.dataset.k=c.k||"";
  th.innerHTML=c.h+(c.k?` <span class="ar">\\u25bc</span>`:"");
  if(c.k)th.onclick=()=>sortBy(c.k,th);
  thead.appendChild(th);
});

/* ---- virtualized body */
const tscroll=document.getElementById("tscroll"), spacer=document.getElementById("spacer"), emptyEl=document.getElementById("empty");
const RH=46; let view=ROWS, curStatus="", curSort={k:"pri",dir:-1};
function passStatus(r){return curStatus===""?true:curStatus==="m"?r[10]>=3:r[10]===+curStatus;}
function applyFilters(){
  const q=document.getElementById("q").value.trim().toLowerCase();
  const acc=accSel.value, reg=document.getElementById("regSel").value;
  view=ROWS.filter(r=>{
    if(!passStatus(r))return false;
    if(acc&&ACC[r[3]]!==acc)return false;
    if(reg!==""&&r[12]!==+reg)return false;
    if(q&&!(r[1].toLowerCase().includes(q)||r[0].includes(q)))return false;
    return true;
  });
  sortView();
  document.getElementById("fcount").textContent=nf(view.length);
  document.getElementById("tcount").textContent=nf(ROWS.length);
  spacer.style.height=(view.length*RH)+"px"; emptyEl.style.display=view.length?"none":"block";
  tscroll.scrollTop=0; render();
}
function sortView(){const k=curSort.k,dir=curSort.dir,idx=KEYIDX[k];
  view.sort((A,B)=>{let x=A[idx],y=B[idx];
    if(k==="diff"){x=x==null?-1e9:Math.abs(x);y=y==null?-1e9:Math.abs(y);}
    if(x==null)x=-1e12;if(y==null)y=-1e12;
    if(typeof x==="string")return dir*x.localeCompare(y);return dir*(x-y);});}
function sortBy(k,th){curSort.dir=curSort.k===k?-curSort.dir:-1;curSort.k=k;
  document.querySelectorAll(".th").forEach(t=>t.classList.remove("sorted","asc","desc"));
  th.classList.add("sorted",curSort.dir<0?"desc":"asc"); sortView(); render();}
function render(){
  const top=tscroll.scrollTop, h=tscroll.clientHeight;
  const start=Math.max(0,Math.floor(top/RH)-6), end=Math.min(view.length,Math.ceil((top+h)/RH)+6);
  let html="";
  for(let i=start;i<end;i++){const d=view[i];
    html+=`<div class="trow rs${Math.min(d[10],3)}" style="top:${i*RH}px">`+COLS.map(c=>c.r(d)).join("")+`</div>`;}
  document.querySelectorAll(".trow").forEach(n=>n.remove());
  spacer.insertAdjacentHTML("beforeend",html);
}
function setStatus(s){curStatus=s;
  document.querySelectorAll("#statusChips .chip").forEach(c=>c.classList.toggle("on",c.dataset.s===s));
  document.querySelectorAll(".pill").forEach(p=>p.classList.toggle("active",p.dataset.s!==""&&p.dataset.s===s));
  applyFilters();}
let raf; tscroll.addEventListener("scroll",()=>{if(raf)cancelAnimationFrame(raf);raf=requestAnimationFrame(render);});
document.getElementById("q").addEventListener("input",()=>{clearTimeout(window._t);window._t=setTimeout(applyFilters,140);});
accSel.onchange=applyFilters; document.getElementById("regSel").onchange=applyFilters;
document.querySelectorAll("#statusChips .chip").forEach(c=>c.onclick=()=>setStatus(c.dataset.s));
window.addEventListener("resize",render);

/* ---- insights toggle + fullscreen */
document.getElementById("insBtn").onclick=function(){
  const o=document.getElementById("insights").classList.toggle("open");
  this.classList.toggle("open",o);
  setTimeout(()=>{ // animate charts when opened
    document.querySelectorAll(".bar span").forEach(s=>s.style.width=s.dataset.w+"%");
    document.getElementById("donut").style.background=`conic-gradient(${stops.join(",")})`;
    setTimeout(render,460);
  },20);
};
document.getElementById("fsBtn").onclick=()=>{
  if(!document.fullscreenElement)document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen();
  else document.exitFullscreen&&document.exitFullscreen();
};
document.addEventListener("fullscreenchange",()=>setTimeout(render,120));

/* ---- Export current view to CSV (13 task columns + Region + Currency; UTF-8 for £/€) */
const STATX=["Normal","High Price","Low Price","DATA MISSING - NO COMPARATOR","DATA MISSING - BUNDLE"];
const PRIX=["Unknown","Low","Medium","High"];
function csvCell(v){v=(v==null?"":String(v));return /[",\\n\\r]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}
function exportCSV(){
  const cols=["ID","SKU","Product Image","Account","Website Price","Amazon Price","Target eBay Price","Current eBay Price","Difference","Difference (%)","Status","Priority","Action","Region","Currency"];
  const out=[cols.join(",")];
  for(let i=0;i<view.length;i++){const d=view[i];
    const img=d[2]?(d[2][0]==="!"?d[2].slice(1):IMGP+d[2]):"";
    const cur=d[12]===0?"GBP":"EUR", region=d[12]===0?"UK":"Germany";
    out.push([
      d[0], d[1], img, ACC[d[3]],
      d[4]==null?"":d[4].toFixed(2), d[5]==null?"":d[5].toFixed(2),
      d[6]==null?"":d[6].toFixed(2), d[7].toFixed(2),
      d[8]==null?"":d[8].toFixed(2), d[9]==null?"":(d[9]*100).toFixed(2),
      STATX[d[10]], PRIX[d[11]], ACTION[d[10]], region, cur
    ].map(csvCell).join(","));
  }
  const blob=new Blob(["\\uFEFF"+out.join("\\r\\n")],{type:"text/csv;charset=utf-8"});
  const url=URL.createObjectURL(blob), a=document.createElement("a");
  const dt=new Date(), ymd=dt.getFullYear()+"-"+String(dt.getMonth()+1).padStart(2,"0")+"-"+String(dt.getDate()).padStart(2,"0");
  a.href=url; a.download="ebay_price_checker_"+ymd+"_"+view.length+"rows.csv";
  document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),1000);
  const b=document.getElementById("exportBtn"), t=b.innerHTML;
  b.innerHTML="&#10003; "+view.length.toLocaleString("en-GB")+" rows exported"; setTimeout(()=>{b.innerHTML=t;},2200);
}
document.getElementById("exportBtn").onclick=exportCSV;

/* ---- boot */
document.querySelector('.th[data-k="pri"]').classList.add("sorted","desc");
applyFilters();
document.querySelectorAll(".pill .n").forEach(n=>{const to=+n.dataset.to,dur=900,t0=performance.now();
  (function s(t){const p=Math.min(1,(t-t0)/dur);n.textContent=nf(Math.round(to*(1-Math.pow(1-p,3))));if(p<1)requestAnimationFrame(s);})(t0);});
setTimeout(()=>document.getElementById("splash").classList.add("hidden"),350);
</script>
</body></html>"""

def build(payload):
    """Render the dashboard HTML from the payload dict."""
    return HTML.replace("__PAYLOAD__", json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
