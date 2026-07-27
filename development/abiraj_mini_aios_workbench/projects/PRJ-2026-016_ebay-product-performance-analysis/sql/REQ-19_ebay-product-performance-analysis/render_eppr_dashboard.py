# -*- coding: utf-8 -*-
"""
REQ-19-D01 dashboard renderer — self-contained, full-screen, LIGHT-THEME HTML console.
Virtual-scrolled table (only visible rows in the DOM) for smooth interaction at 9,781 rows.
Reuses the SAME query/config as the xlsx builder so the two never drift. Read-only.
"""
import os, json
from datetime import date, timedelta
import psycopg2
from eppr_build_d01 import SQL, WH, BRAND_MAP, VAT_RATE, HEADERS

HERE = os.path.dirname(__file__)
OUTDIR = os.path.abspath(os.path.join(HERE, "..","..","evidence","final_outputs",
                                       "REQ-19_ebay-product-performance-analysis"))
JSON_OUT = os.path.join(OUTDIR, "eppr_d01_data.json")
HTML_OUT = os.path.join(OUTDIR, "REQ-19-D01_dashboard.html")
ND = "NO DATA"

def build_records():
    anchor = date.today() - timedelta(days=1); d0 = anchor - timedelta(days=29)
    conn = psycopg2.connect(**WH); cur = conn.cursor()
    cur.execute(SQL, {"d0": d0, "d1": anchor}); rows = cur.fetchall(); conn.close()
    recs = []
    for r in rows:
        (mkt, acct, item_id, parent_sku, rep_sku, vc, title, category, ldate, price, stock, img,
         units, orders, revenue, last_sold, ebay_fees, ad_cost, is_promoted,
         shipping_cost, impr, clicks, conv) = r
        revenue = float(revenue) if revenue is not None else 0.0
        vat = round(revenue - revenue/(1+VAT_RATE[mkt]), 2) if revenue else 0
        ctr = round(float(clicks)/float(impr)*100, 2) if impr and clicks is not None and float(impr) > 0 else None
        cvr = round(float(conv)/float(clicks)*100, 2) if clicks and conv is not None and float(clicks) > 0 else None
        rec = [
            img or "", (rep_sku or ND) + ("" if vc == 1 else " (+%d)" % (vc-1)), parent_sku or ND,
            str(item_id), title or ND, BRAND_MAP.get(acct, acct.title() if acct else ND), category or ND,
            mkt, acct, ldate.isoformat() if ldate else ND, "Active",
            round(float(price), 2) if price is not None else None,
            None, float(shipping_cost) if shipping_cost is not None else 0,
            float(ebay_fees) if ebay_fees is not None else 0, float(ad_cost) if ad_cost is not None else 0,
            vat, int(stock) if stock is not None else None,
            int(units) if units is not None else 0, int(orders) if orders is not None else 0,
            revenue, None, None, None,
            int(impr) if impr is not None else None,
            int(clicks) if clicks is not None else None, int(clicks) if clicks is not None else None,
            ctr, cvr, None,
            last_sold.isoformat() if last_sold else ND,
            (anchor - ldate).days if ldate else None,
            "Promoted" if is_promoted else "Not Promoted", None, None,
        ]
        recs.append({"c": "£" if mkt == "UK" else "€", "v": rec})
    return recs, d0, anchor

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>eBay Product Performance — REQ-19-D01</title>
<style>
:root{
  --bg1:#eef3fb; --bg2:#f7f9fd; --panel:#ffffff; --ink:#101a2c; --ink2:#3d4a60; --muted:#8592a6;
  --line:#e9eef6; --line2:#f0f4fa; --accent:#3b6ef6; --accent2:#8b5cf6; --good:#16a34a; --muted2:#b8c2d2;
  --warn:#d97706; --bad:#dc2626;
  --shadow-sm:0 1px 2px rgba(16,26,44,.05); --shadow:0 2px 6px rgba(16,26,44,.06),0 14px 34px rgba(16,26,44,.07);
  --r:16px; --rowh:42px;
}
*{box-sizing:border-box}
html,body{height:100%;margin:0}
body{font:13px/1.45 "Inter",-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);
  background:radial-gradient(1200px 600px at 15% -10%,#e7eefc 0%,transparent 60%),linear-gradient(180deg,var(--bg1),var(--bg2));
  height:100vh;overflow:hidden;-webkit-font-smoothing:antialiased}
.app{display:flex;flex-direction:column;height:100vh;padding:9px 14px 10px;gap:8px}
.reveal{opacity:0;transform:translateY(12px);animation:rise .6s cubic-bezier(.22,.7,.2,1) forwards}
.d1{animation-delay:.03s}.d2{animation-delay:.09s}.d3{animation-delay:.15s}.d4{animation-delay:.21s}
header.top{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:13px}
.logo{position:relative;width:38px;height:38px;border-radius:12px;background:linear-gradient(135deg,var(--accent),var(--accent2));
  display:grid;place-items:center;color:#fff;font-weight:850;font-size:14px;letter-spacing:-.5px;overflow:hidden;
  box-shadow:0 10px 26px rgba(59,110,246,.42);animation:pop .6s cubic-bezier(.2,.8,.2,1),float 5s ease-in-out infinite .6s}
.logo::after{content:"";position:absolute;top:0;left:-70%;width:45%;height:100%;transform:skewX(-20deg);
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.55),transparent);animation:shine 3.8s ease-in-out infinite 1s}
h1{font-size:16px;margin:0;font-weight:800;letter-spacing:-.2px;
  background:linear-gradient(115deg,#101a2c,#3b6ef6 55%,#8b5cf6);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--muted);font-size:11.5px;margin-top:3px}
.btn{font:inherit;font-weight:650;padding:10px 16px;border:none;border-radius:11px;cursor:pointer;color:#fff;
  background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 8px 20px rgba(59,110,246,.28);
  transition:transform .18s cubic-bezier(.2,.8,.2,1),box-shadow .18s,filter .18s}
.btn:hover{transform:translateY(-2px);box-shadow:0 12px 26px rgba(59,110,246,.36);filter:brightness(1.04)}
.btn:active{transform:translateY(0)}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:10px}
.kpi{--c:#3b6ef6;--bg:#eaf1ff;--glow:rgba(59,110,246,.22);position:relative;overflow:hidden;padding:10px 14px 11px;
  border-radius:18px;background:linear-gradient(165deg,#fff,#fbfcff);border:1px solid var(--line);
  box-shadow:0 1px 2px rgba(16,26,44,.05),0 10px 26px rgba(16,26,44,.06);
  transition:transform .28s cubic-bezier(.2,.8,.2,1),box-shadow .28s}
.kpi::before{content:"";position:absolute;right:-34px;top:-34px;width:120px;height:120px;border-radius:50%;
  background:radial-gradient(circle,var(--glow),transparent 68%);opacity:.75;transition:opacity .28s,transform .5s cubic-bezier(.2,.8,.2,1)}
.kpi:hover{transform:translateY(-6px);box-shadow:0 22px 48px var(--glow)}
.kpi:hover::before{opacity:1;transform:scale(1.22)}
.kpi .khead{display:flex;align-items:center;gap:9px;position:relative}
.kpi .kicon{width:27px;height:27px;border-radius:9px;display:grid;place-items:center;flex:none;background:var(--bg);color:var(--c);
  box-shadow:inset 0 0 0 1px rgba(0,0,0,.03);transition:transform .28s cubic-bezier(.2,.8,.2,1)}
.kpi:hover .kicon{transform:scale(1.12) rotate(-5deg)}
.kpi .kicon svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.kpi .lbl{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.6px;font-weight:750}
.kpi .val{font-size:21px;font-weight:820;margin-top:5px;letter-spacing:-.5px;font-variant-numeric:tabular-nums;color:var(--ink);position:relative}
.kpi .bar{height:5px;border-radius:999px;background:var(--bg);margin-top:6px;overflow:hidden}
.kpi .bar>i{display:block;height:100%;width:0;border-radius:999px;background:var(--c);transition:width .9s cubic-bezier(.2,.8,.2,1)}
.controls{display:flex;gap:9px;flex-wrap:wrap;align-items:center;background:var(--panel);border:1px solid var(--line);
  border-radius:13px;padding:8px 11px;box-shadow:var(--shadow)}
.controls input,.controls select{font:inherit;padding:8px 12px;border:1px solid var(--line);border-radius:10px;
  background:#fbfcfe;color:var(--ink);outline:none;transition:border .16s,box-shadow .16s,background .16s,transform .16s}
.controls input:focus,.controls select:focus{border-color:var(--accent);background:#fff;box-shadow:0 0 0 3.5px rgba(59,110,246,.15)}
.searchbox{position:relative}
.searchbox .sicon{position:absolute;left:12px;top:50%;transform:translateY(-50%);width:15px;height:15px;stroke:var(--muted);
  fill:none;stroke-width:2;stroke-linecap:round;pointer-events:none;transition:stroke .16s}
.searchbox input[type=search]{min-width:262px;padding-left:34px}
.searchbox:focus-within .sicon{stroke:var(--accent)}
.controls select{cursor:pointer;appearance:none;-webkit-appearance:none;padding-right:32px;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%238592a6' stroke-width='2.6' stroke-linecap='round' stroke-linejoin='round'><path d='M6 9l6 6 6-6'/></svg>");
  background-repeat:no-repeat;background-position:right 11px center}
.controls select:hover{border-color:#cdd8ea;background-color:#fff}
.spacer{flex:1}
.pill{font-size:11.5px;color:var(--ink2);background:#f1f5fc;border:1px solid var(--line);padding:7px 12px;border-radius:999px;font-weight:600}
.pill b{color:var(--accent)}
.tablewrap{flex:1;min-height:0;background:var(--panel);border:1px solid var(--line);border-radius:var(--r);
  box-shadow:var(--shadow);overflow:auto;position:relative}
.tablewrap::-webkit-scrollbar{width:12px;height:12px}
.tablewrap::-webkit-scrollbar-thumb{background:#d3dcea;border-radius:999px;border:3px solid var(--panel)}
.tablewrap::-webkit-scrollbar-thumb:hover{background:#bcc8db}
table{border-collapse:separate;border-spacing:0;width:100%;table-layout:fixed;font-variant-numeric:tabular-nums}
thead th{position:sticky;top:0;z-index:3;background:#f6f9fe;color:var(--ink2);font-size:10px;text-transform:uppercase;
  letter-spacing:.3px;font-weight:750;text-align:right;padding:7px 9px;height:48px;border-bottom:1.5px solid var(--line);
  white-space:normal;line-height:1.16;vertical-align:middle;overflow:hidden;overflow-wrap:break-word;cursor:pointer;user-select:none;transition:color .15s}
thead th.l{text-align:left}
thead th:hover{color:var(--accent)}
thead.scrolled th{box-shadow:0 6px 14px rgba(16,26,44,.07)}
thead th .ar{opacity:.85;font-size:9px;margin-left:4px;color:var(--accent)}
tbody td{padding:0 11px;height:var(--rowh);border-bottom:1px solid var(--line2);text-align:right;white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis}
tbody td.l{text-align:left}
tr.row{background:#fff}
tr.row.even{background:#fbfcff}
tr.row:hover{background:#eaf1ff}
th.s0,td.s0{position:sticky;left:0;z-index:2;background:inherit}
th.s1,td.s1{position:sticky;left:72px;z-index:2;background:inherit}
thead th.s0,thead th.s1{z-index:4;background:#f6f9fe}
tr.row td.s0,tr.row td.s1{background:inherit}
img.thumb{width:34px;height:34px;object-fit:cover;border-radius:9px;border:1px solid var(--line);background:#eef2f8;
  box-shadow:0 1px 3px rgba(16,26,44,.14);transition:transform .22s cubic-bezier(.2,.8,.2,1),box-shadow .22s;cursor:zoom-in;vertical-align:middle}
.db{position:relative;width:100%;height:100%;display:flex;align-items:center;justify-content:flex-end}
.dbf{position:absolute;right:0;top:50%;transform:translateY(-50%);height:20px;border-radius:5px;z-index:0}
.dbf.rev{background:linear-gradient(90deg,rgba(59,110,246,.04),rgba(59,110,246,.28))}
.dbf.un{background:linear-gradient(90deg,rgba(14,165,164,.04),rgba(14,165,164,.26))}
.dbn{position:relative;z-index:1}
.stock{font-weight:650}
.stock.s-out{color:var(--bad)}.stock.s-low{color:var(--warn)}
.stock.s-out::before,.stock.s-low::before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:5px;vertical-align:middle}
.stock.s-out::before{background:var(--bad)}.stock.s-low::before{background:var(--warn)}
td.s1,th.s1{box-shadow:9px 0 12px -9px rgba(16,26,44,.14)}
tr.row:hover td.s0{box-shadow:inset 3px 0 0 var(--accent)}
.flag{margin-right:4px;font-size:11px}
.zero{color:#c9d2e0;font-weight:500}
.tag{display:inline-block;max-width:100%;padding:2px 8px;border-radius:7px;background:#eef2f9;color:var(--ink2);font-size:11px;font-weight:600;overflow:hidden;text-overflow:ellipsis;vertical-align:middle}
.tag.alt{background:#f0edfb;color:#5f4fb0}
.pctv.g{color:var(--good);font-weight:650}
.pctv.m{color:var(--muted2)}
td.gdiv,th.gdiv{border-left:2px solid #e4eaf4}
thead th.gdiv{border-left:2px solid #dbe4f1}
.btn.ghost{background:#fff;color:var(--ink2);border:1px solid var(--line);box-shadow:var(--shadow-sm)}
.btn.ghost:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-1px);filter:none;box-shadow:0 6px 16px rgba(59,110,246,.16)}
img.thumb:hover{transform:scale(1.1);box-shadow:0 5px 14px rgba(16,26,44,.28);border-color:var(--accent)}
#imgprev{position:fixed;left:0;top:0;z-index:200;pointer-events:none;opacity:0;transform:scale(.9);transform-origin:center;
  transition:opacity .13s ease,transform .13s cubic-bezier(.2,.8,.2,1);background:#fff;border:1px solid var(--line);
  border-radius:16px;box-shadow:0 24px 60px rgba(16,26,44,.32);padding:9px}
#imgprev.on{opacity:1;transform:scale(1)}
#imgprev img{display:block;width:220px;height:220px;object-fit:contain;border-radius:10px;background:#f4f6fb}
.nd{color:var(--muted2);font-style:italic;font-size:11px}
.chip{display:inline-block;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:650;line-height:1.2}
.chip.pro{background:rgba(22,163,74,.12);color:var(--good)}
.chip.no{background:rgba(133,146,166,.14);color:var(--muted)}
.mkt{display:inline-block;padding:3px 9px;border-radius:7px;font-size:10.5px;font-weight:750;letter-spacing:.2px}
.mkt.UK{background:rgba(59,110,246,.12);color:var(--accent)}
.mkt.Germany{background:rgba(139,92,246,.14);color:var(--accent2)}
.money{font-weight:600}
.foot{color:var(--muted);font-size:11px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.foot b{color:var(--ink2)}
@keyframes rise{to{opacity:1;transform:none}}
@keyframes pop{from{transform:scale(.5);opacity:0}to{transform:scale(1);opacity:1}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
@keyframes shine{0%,55%{left:-70%}100%{left:140%}}
@media(max-width:1100px){.kpis{grid-template-columns:repeat(3,1fr)}}
</style></head><body>
<div class="app">
  <header class="top reveal d1">
    <div class="brand">
      <div class="logo">eP</div>
      <div><h1>eBay Product Performance Analysis</h1>
        <div class="sub">REQ-19-D01 · <b id="nlist">__N__</b> live listings · UK + Germany · window __D0__ → __D1__ · warehouse (read-only) · money per marketplace currency</div></div>
    </div>
    <button class="btn" onclick="exportCSV()">⬇ Export CSV</button>
  </header>
  <section class="kpis" id="kpis"></section>
  <div class="controls reveal d3">
    <div class="searchbox"><svg class="sicon" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg><input type="search" id="q" placeholder="Search title / SKU / item id / brand…" oninput="refresh()"></div>
    <select id="fAcct" onchange="refresh()"></select>
    <select id="fMkt" onchange="refresh()"><option value="">All marketplaces</option><option>UK</option><option>Germany</option></select>
    <select id="fPromo" onchange="refresh()"><option value="">All promotion</option><option>Promoted</option><option>Not Promoted</option></select>
    <button class="btn ghost" id="dbtn" onclick="toggleDensity()">Compact</button>
    <div class="spacer"></div>
    <div class="pill">Showing <b id="shown">0</b> of __N__</div>
  </div>
  <div class="tablewrap reveal d4" id="wrap"><table><colgroup id="cg"></colgroup><thead id="thead"></thead><tbody id="tbody"></tbody></table></div>
  <div class="foot reveal d4">
    <span>Grain: one row per eBay listing (item_id). Money in each row's own currency — <b>UK £ / DE €</b> — never blended.</span>
    <span><b>NO DATA</b> = no warehouse source: Cost Price · Gross/Net/Margin (sku_cogs empty) · Watch Count · PPC Campaign · Sales Trend.</span>
  </div>
</div>
<script>
const H=__HEADERS__, DATA=__DATA__;
const MONEY=new Set([11,12,13,14,15,16,20,21,22]), PCT=new Set([23,27,28]), NUM=new Set([17,18,19,24,25,26,31]);
const LEFT=new Set([0,1,2,3,4,5,6,8,9,32,33,34]);
const GDIV=new Set([7,11,17,21,24,30]), ZMUTE=new Set([13,14,15,16,18,19,20,24,25,26]);
const W=[72,150,150,120,300,120,150,96,120,102,88,102,96,108,96,94,94,90,72,72,112,104,104,98,104,80,84,74,106,92,116,92,122,112,92];
let ROWH=42; const BUF=10;
let sortCol=20, sortDir=-1, view=[], maxRev=1, maxUnits=1;
const wrap=document.getElementById('wrap'), tbody=document.getElementById('tbody'), thead=document.getElementById('thead');
const fmtN=x=>x==null?null:x.toLocaleString('en-GB');
const fmtM=(x,c)=>x==null?null:c+x.toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});
function buildStatic(){
  document.getElementById('cg').innerHTML=W.map(w=>`<col style="width:${w}px">`).join('');
  drawHead();
}
function drawHead(){
  thead.innerHTML='<tr>'+H.map((h,i)=>{const cls=(LEFT.has(i)?'l ':'')+(i===0?'s0':i===1?'s1':'')+(GDIV.has(i)?' gdiv':'');
    const ar=sortCol===i?(sortDir>0?'▲':'▼'):''; return `<th class="${cls}" onclick="sortBy(${i})">${h}<span class="ar">${ar}</span></th>`;}).join('')+'</tr>';
}
function acctOpts(){const s=[...new Set(DATA.map(r=>r.v[8]))].sort();
  document.getElementById('fAcct').innerHTML='<option value="">All accounts</option>'+s.map(a=>`<option>${a}</option>`).join('');}
function computeView(){
  const q=document.getElementById('q').value.trim().toLowerCase();
  const fa=document.getElementById('fAcct').value, fm=document.getElementById('fMkt').value, fp=document.getElementById('fPromo').value;
  view=DATA.filter(r=>{const v=r.v; if(fa&&v[8]!==fa)return false; if(fm&&v[7]!==fm)return false; if(fp&&v[32]!==fp)return false;
    if(q){if(!((v[4]+' '+v[1]+' '+v[3]+' '+v[5]).toLowerCase().includes(q)))return false;} return true;});
  view.sort((a,b)=>{let x=a.v[sortCol],y=b.v[sortCol]; if(x==null)return 1; if(y==null)return -1;
    if(typeof x==='number'&&typeof y==='number')return (x-y)*sortDir; return String(x).localeCompare(String(y))*sortDir;});
  maxRev=1;maxUnits=1;
  for(const r of view){const rv=r.v[20]||0,u=r.v[18]||0; if(rv>maxRev)maxRev=rv; if(u>maxUnits)maxUnits=u;}
}
function cell(v,i,cur){
  if(v==null||v===''||v==='NO DATA')return '<span class="nd">NO DATA</span>';
  if(i===0)return `<img class="thumb" loading="lazy" src="${v}" onerror="this.style.visibility='hidden'">`;
  if(ZMUTE.has(i)&&v===0)return '<span class="zero">–</span>';
  if(i===7)return `<span class="mkt ${v}"><span class="flag">${v==='UK'?'🇬🇧':'🇩🇪'}</span>${v}</span>`;
  if(i===5)return `<span class="tag" title="${String(v).replace(/"/g,'&quot;')}">${v}</span>`;
  if(i===6)return `<span class="tag alt" title="${String(v).replace(/"/g,'&quot;')}">${v}</span>`;
  if(i===32)return `<span class="chip ${v==='Promoted'?'pro':'no'}">${v}</span>`;
  if(i===17){const c=v===0?'s-out':v<5?'s-low':'';return `<span class="stock ${c}">${fmtN(v)}</span>`;}
  if(i===27){const cls=v>=2?'g':v>=0.8?'':'m';return `<span class="pctv ${cls}">${v.toFixed(2)}%</span>`;}
  if(i===28){const cls=v>=3?'g':v>=1?'':'m';return `<span class="pctv ${cls}">${v.toFixed(2)}%</span>`;}
  if(i===20){const p=Math.min(100,v/maxRev*100);return `<div class="db"><i class="dbf rev" style="width:${p}%"></i><span class="dbn money">${fmtM(v,cur)}</span></div>`;}
  if(i===18){const p=Math.min(100,v/maxUnits*100);return `<div class="db"><i class="dbf un" style="width:${p}%"></i><span class="dbn">${fmtN(v)}</span></div>`;}
  if(MONEY.has(i))return `<span class="money">${fmtM(v,cur)}</span>`;
  if(PCT.has(i))return v.toFixed(2)+'%';
  if(NUM.has(i))return fmtN(v);
  if(i===4)return `<span title="${String(v).replace(/"/g,'&quot;')}">${v}</span>`;
  return v;
}
function renderWindow(){
  const st=wrap.scrollTop, h=wrap.clientHeight;
  thead.classList.toggle('scrolled',st>2);
  let start=Math.max(0,Math.floor(st/ROWH)-BUF);
  let end=Math.min(view.length,Math.ceil((st+h)/ROWH)+BUF);
  const top=start*ROWH, bot=Math.max(0,(view.length-end)*ROWH);
  let html=top?`<tr style="height:${top}px"><td colspan="35" style="padding:0;border:0"></td></tr>`:'';
  for(let i=start;i<end;i++){const r=view[i],v=r.v; let tds='';
    for(let c=0;c<H.length;c++){const cls=(LEFT.has(c)?'l ':'')+(c===0?'s0':c===1?'s1':'')+(GDIV.has(c)?' gdiv':'');
      tds+=`<td class="${cls}">${cell(v[c],c,r.c)}</td>`;}
    html+=`<tr class="row ${i%2?'even':''}">${tds}</tr>`;}
  if(bot)html+=`<tr style="height:${bot}px"><td colspan="35" style="padding:0;border:0"></td></tr>`;
  tbody.innerHTML=html;
}
function animateNum(el,to,fmt){
  el.textContent=fmt(to);                 // guarantee final value even if rAF never fires (bg tab)
  const from=el._cur||0; el._cur=to;
  if(from===to)return;
  const dur=520, t0=performance.now();
  function step(now){let p=Math.min(1,(now-t0)/dur); p=1-Math.pow(1-p,3);
    el.textContent=fmt(from+(to-from)*p); if(p<1)requestAnimationFrame(step);}
  requestAnimationFrame(step);
}
const IC={
 layers:'<svg viewBox="0 0 24 24"><path d="M12 2 2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
 card:'<svg viewBox="0 0 24 24"><rect x="1.5" y="4.5" width="21" height="15" rx="2.5"/><path d="M1.5 9.5h21"/></svg>',
 cart:'<svg viewBox="0 0 24 24"><circle cx="9" cy="21" r="1.4"/><circle cx="19" cy="21" r="1.4"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23.5 6H6"/></svg>',
 bag:'<svg viewBox="0 0 24 24"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
 trend:'<svg viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
};
const KPI=[
 {lbl:'Listings',c:'#3b6ef6',bg:'#eaf1ff',glow:'rgba(59,110,246,.22)',icon:IC.layers,sub:'active · UK + DE',calc:v=>v.length,fmt:x=>Math.round(x).toLocaleString('en-GB')},
 {lbl:'UK Revenue',c:'#4f46e5',bg:'#edecfe',glow:'rgba(79,70,229,.22)',icon:IC.card,sub:'30-day · GBP',calc:v=>v.reduce((s,r)=>s+(r.v[7]==='UK'?r.v[20]:0),0),fmt:x=>'£'+Math.round(x).toLocaleString('en-GB')},
 {lbl:'DE Revenue',c:'#8b5cf6',bg:'#f2eafe',glow:'rgba(139,92,246,.22)',icon:IC.card,sub:'30-day · EUR',calc:v=>v.reduce((s,r)=>s+(r.v[7]==='Germany'?r.v[20]:0),0),fmt:x=>'€'+Math.round(x).toLocaleString('en-GB')},
 {lbl:'Units Sold',c:'#0ea5a4',bg:'#e0f6f5',glow:'rgba(14,165,164,.22)',icon:IC.cart,sub:'last 30 days',calc:v=>v.reduce((s,r)=>s+(r.v[18]||0),0),fmt:x=>Math.round(x).toLocaleString('en-GB')},
 {lbl:'Orders',c:'#f59e0b',bg:'#fdf0d9',glow:'rgba(245,158,11,.22)',icon:IC.bag,sub:'last 30 days',calc:v=>v.reduce((s,r)=>s+(r.v[19]||0),0),fmt:x=>Math.round(x).toLocaleString('en-GB')},
 {lbl:'Promoted',c:'#16a34a',bg:'#e3f6e9',glow:'rgba(22,163,74,.22)',icon:IC.trend,bar:true,sub:'of listings',calc:v=>v.length?v.filter(r=>r.v[32]==='Promoted').length/v.length*100:0,fmt:x=>Math.round(x)+'%'},
];
function drawKPIs(){document.getElementById('kpis').innerHTML=KPI.map((k,i)=>
 `<div class="kpi reveal d2" style="--c:${k.c};--bg:${k.bg};--glow:${k.glow};animation-delay:${(.04+i*.05).toFixed(2)}s">
   <div class="khead"><span class="kicon">${k.icon}</span><span class="lbl">${k.lbl}</span></div>
   <div class="val" id="kpi${i}">0</div>
   ${k.bar?`<div class="bar"><i id="bar${i}"></i></div>`:''}</div>`).join('');}
function updateKPIs(){KPI.forEach((k,i)=>{const val=k.calc(view);animateNum(document.getElementById('kpi'+i),val,k.fmt);
  if(k.bar){const b=document.getElementById('bar'+i);if(b)b.style.width=Math.max(3,Math.min(100,val))+'%';}});}
function refresh(){computeView();updateKPIs();document.getElementById('shown').textContent=view.length.toLocaleString('en-GB');
  wrap.scrollTop=0;renderWindow();}
function sortBy(i){if(sortCol===i)sortDir*=-1;else{sortCol=i;sortDir=(LEFT.has(i)?1:-1);}drawHead();refresh();}
let dense=false;
function toggleDensity(){dense=!dense;ROWH=dense?36:42;document.documentElement.style.setProperty('--rowh',ROWH+'px');
  document.getElementById('dbtn').textContent=dense?'Comfortable':'Compact';renderWindow();}
function exportCSV(){const esc=s=>'"'+String(s==null?'NO DATA':s).replace(/"/g,'""')+'"';
  let out=H.map(esc).join(',')+'\n';
  for(const r of view)out+=r.v.map((x,i)=>esc(x==null?'NO DATA':(MONEY.has(i)?r.c+x:x))).join(',')+'\n';
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([out],{type:'text/csv'}));
  a.download='REQ-19-D01_ebay_product_performance.csv';a.click();}
// floating image preview (escapes table overflow clipping)
const prev=document.createElement('div');prev.id='imgprev';prev.innerHTML='<img alt="">';document.body.appendChild(prev);
const prevImg=prev.firstChild;
tbody.addEventListener('mouseover',e=>{const t=e.target;if(t.classList&&t.classList.contains('thumb')&&t.complete&&t.naturalWidth>0){prevImg.src=t.src;prev.classList.add('on');}});
tbody.addEventListener('mouseout',e=>{if(e.target.classList&&e.target.classList.contains('thumb'))prev.classList.remove('on');});
tbody.addEventListener('mousemove',e=>{if(!prev.classList.contains('on'))return;const w=238,h=238,pad=22;
  let x=e.clientX+pad,y=e.clientY-h/2;if(x+w>innerWidth-6)x=e.clientX-w-pad;if(x<6)x=6;
  if(y<6)y=6;if(y+h>innerHeight-6)y=innerHeight-h-6;prev.style.left=x+'px';prev.style.top=y+'px';},{passive:true});
wrap.addEventListener('scroll',()=>{prev.classList.remove('on');renderWindow();},{passive:true});
window.addEventListener('resize',renderWindow);
buildStatic();acctOpts();drawKPIs();refresh();
</script></body></html>"""

def main():
    recs, d0, anchor = build_records()
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump({"headers": HEADERS, "records": recs, "window": [d0.isoformat(), anchor.isoformat()]}, f)
    html = (HTML.replace("__HEADERS__", json.dumps(HEADERS))
                .replace("__DATA__", json.dumps(recs, ensure_ascii=False))
                .replace("__N__", "{:,}".format(len(recs)))
                .replace("__D0__", d0.isoformat()).replace("__D1__", anchor.isoformat()))
    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("rows:", len(recs))
    print("HTML:", round(os.path.getsize(HTML_OUT)/1e6, 2), "MB ->", HTML_OUT)

if __name__ == "__main__":
    main()
