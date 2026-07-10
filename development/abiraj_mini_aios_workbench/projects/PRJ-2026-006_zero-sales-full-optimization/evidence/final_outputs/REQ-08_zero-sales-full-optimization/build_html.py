"""Build the ZSFO interactive HTML dashboard from the governed data.json.
Read-only: consumes data.json (produced by generate_dataset.sql via the Postgres MCP).
Self-contained single file (data embedded) — opens offline. Run: python build_html.py
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")
OUT  = os.path.join(HERE, "ZSFO_Utharsika_dashboard.html")

with open(DATA, encoding="utf-8") as f:
    d = json.load(f)
meta, rows = d["meta"], d["rows"]

# compact payload for the browser (short keys already)
payload = json.dumps({"meta": meta, "rows": rows}, ensure_ascii=False, separators=(",", ":"))

oos      = sum(1 for r in rows if r["uk_stock"] == 0 and r["fbm_stock"] == 0)
zero_imp = sum(1 for r in rows if r["impr"] == 0)
has_uk   = sum(1 for r in rows if r["uk_stock"] > 0)
tot_imp  = sum(r["impr"] for r in rows)
tot_clk  = sum(r["clk"] for r in rows)

html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZSFO — Zero Sales Full Optimization — Utharsika</title>
<style>
:root{--navy:#1f2a44;--head:#2e3b55;--line:#e3e7f0;--ink:#1b2233;--mut:#6b7488;
--red:#c8393c;--redbg:#fdecec;--amb:#b8791b;--ambbg:#fff6e6;--grn:#2f855a;--accent:#3956a8;}
*{box-sizing:border-box}
body{margin:0;font:13px/1.45 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:#eef1f6}
header{background:linear-gradient(135deg,#1f2a44,#33436b);color:#fff;padding:18px 22px}
header h1{margin:0;font-size:19px;letter-spacing:.2px}
header .sub{margin-top:5px;font-size:12px;color:#c7d0e6;max-width:1100px}
.kpis{display:flex;flex-wrap:wrap;gap:12px;padding:16px 22px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 16px;min-width:150px;flex:1}
.kpi .n{font-size:22px;font-weight:700}
.kpi .l{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px;margin-top:2px}
.kpi.red .n{color:var(--red)} .kpi.amb .n{color:var(--amb)} .kpi.grn .n{color:var(--grn)}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:0 22px 12px}
.controls input,.controls select{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px;background:#fff}
.controls input[type=search]{min-width:240px}
.chip{padding:6px 12px;border:1px solid var(--line);border-radius:20px;background:#fff;cursor:pointer;font-size:12px}
.chip.on{background:var(--navy);color:#fff;border-color:var(--navy)}
.wrap{padding:0 22px 40px}
.tblbox{background:#fff;border:1px solid var(--line);border-radius:10px;overflow:auto;max-height:74vh}
table{border-collapse:collapse;width:100%;font-size:12px}
thead th{position:sticky;top:0;background:var(--head);color:#fff;padding:8px 9px;text-align:left;white-space:nowrap;cursor:pointer;z-index:2}
thead th.num{text-align:right}
tbody td{padding:6px 9px;border-top:1px solid var(--line);white-space:nowrap}
tbody td.num{text-align:right;font-variant-numeric:tabular-nums}
tbody tr:hover{background:#f2f5fb}
tr.oos{background:var(--redbg)} tr.oos:hover{background:#fbe3e3}
tr.zeroimp{background:var(--ambbg)} tr.zeroimp:hover{background:#fdeecf}
.asin a{color:var(--accent);text-decoration:none;font-weight:600}
.spark{display:inline-block}
.hint{max-width:320px;white-space:normal;color:var(--mut)}
.tag{display:inline-block;padding:1px 7px;border-radius:10px;font-size:10.5px;font-weight:600}
.t-oos{background:var(--redbg);color:var(--red)} .t-imp{background:var(--ambbg);color:var(--amb)}
.t-clk{background:#eaf1ff;color:var(--accent)} .t-sale{background:#e9f6ef;color:var(--grn)}
.foot{padding:14px 22px;color:var(--mut);font-size:11px}
.old{color:var(--red);font-weight:600}
.count{font-size:12px;color:var(--mut);padding:8px 2px}
</style></head><body>
<header>
  <h1>ZSFO — Zero Sales Full Optimization</h1>
  <div class="sub" id="sub"></div>
</header>
<div class="kpis" id="kpis"></div>
<div class="controls">
  <input type="search" id="q" placeholder="Search ASIN or SKU…">
  <span class="chip on" data-f="all">All</span>
  <span class="chip" data-f="oos">Out of stock</span>
  <span class="chip" data-f="zeroimp">Zero impressions</span>
  <span class="chip" data-f="hasuk">Has UK stock</span>
  <span class="chip" data-f="clk">Had clicks</span>
  <span class="count" id="count"></span>
</div>
<div class="wrap"><div class="tblbox"><table id="t"><thead></thead><tbody></tbody></table></div></div>
<div class="foot" id="foot"></div>
<script>
const D = __PAYLOAD__;
const meta = D.meta, ROWS = D.rows;
const wk = meta.week_buckets;
document.getElementById('sub').textContent =
  `${meta.portfolio_holder[0].toUpperCase()+meta.portfolio_holder.slice(1)} · ${meta.marketplace} · run ${meta.run_date} · window ${meta.window_start} → ${meta.window_end} (last completed 30 days, current day excluded) · zero-sale = 0 units across FBA+FBM AND Vendor`;
const fmt = n => (n==null?'':Number(n).toLocaleString());
const pct = n => (n==null?'—':(n*100).toFixed(2)+'%');
const runY = new Date(meta.run_date).getFullYear();
function isOld(dt){ if(!dt) return true; return (new Date(meta.run_date)-new Date(dt))/86400000 > 120; }

function kpi(n,l,cls){return `<div class="kpi ${cls||''}"><div class="n">${n}</div><div class="l">${l}</div></div>`;}
document.getElementById('kpis').innerHTML =
  kpi(fmt(meta.universe_asins),'UK ASINs (universe)') +
  kpi(fmt(ROWS.length),'Zero-sale (report)','') +
  kpi(fmt(ROWS.filter(r=>r.uk_stock==0&&r.fbm_stock==0).length),'Out of stock','red') +
  kpi(fmt(ROWS.filter(r=>r.impr==0).length),'Zero impressions','amb') +
  kpi(fmt(ROWS.filter(r=>r.uk_stock>0).length),'Has UK stock','grn') +
  kpi(fmt(ROWS.reduce((a,r)=>a+r.impr,0)),'Total impressions');

function spark(vals){
  const max = Math.max(1,...vals);
  const w=8,g=2,h=22;
  let bars = vals.map((v,i)=>{const bh=Math.max(1,Math.round(v/max*h));
    return `<rect x="${i*(w+g)}" y="${h-bh}" width="${w}" height="${bh}" rx="1" fill="#3956a8" opacity="${v?0.85:0.2}"/>`;}).join('');
  return `<svg class="spark" width="${vals.length*(w+g)}" height="${h}" title="${vals.join(' / ')}">${bars}</svg>`;
}
function tag(rc){
  if(rc.startsWith('Out of stock')) return '<span class="tag t-oos">OOS</span>';
  if(rc.startsWith('Zero impressions')) return '<span class="tag t-imp">0 impr</span>';
  if(rc.startsWith('Impressions but 0 clicks')) return '<span class="tag t-imp">0 clk</span>';
  return '<span class="tag t-clk">0 sale</span>';
}
const COLS = [
  ['asin','ASIN',false],['sku','SKU',false],['uk_stock','UK Whse',true],['fbm_stock','FBM',true],
  ['impr','Impr',true],['clk','Clicks',true],['cr','Conv%',true],
  ['trend','Weekly impr ('+wk.join(' · ')+')',false],
  ['last_order','Last Amz sale',false],['last_vendor','Last vendor sale',false],
  ['vlife','Vendor units (life)',true],['root_cause','Root-cause hint',false]
];
let th='<tr>';COLS.forEach((c,i)=>{th+=`<th data-i="${i}" class="${c[2]?'num':''}">${c[1]}</th>`;});th+='</tr>';
document.querySelector('#t thead').innerHTML=th;

let filter='all', q='', sortI=4, sortDir=-1;
function pass(r){
  if(filter=='oos' && !(r.uk_stock==0&&r.fbm_stock==0)) return false;
  if(filter=='zeroimp' && r.impr!=0) return false;
  if(filter=='hasuk' && !(r.uk_stock>0)) return false;
  if(filter=='clk' && !(r.clk>0)) return false;
  if(q){const s=(r.asin+' '+r.sku).toLowerCase();if(!s.includes(q))return false;}
  return true;
}
function render(){
  let data=ROWS.filter(pass);
  const key=COLS[sortI][0];
  if(key!=='trend'){data.sort((a,b)=>{let x=a[key],y=b[key];
    if(typeof x==='string'||typeof y==='string'){x=(x||'');y=(y||'');return x<y?-sortDir:x>y?sortDir:0;}
    return ((x||0)-(y||0))*sortDir;});}
  const tb=data.map(r=>{
    const cls=(r.uk_stock==0&&r.fbm_stock==0)?'oos':(r.impr==0?'zeroimp':'');
    const wkimp=[r.w1i,r.w2i,r.w3i,r.w4i,r.w5i];
    return `<tr class="${cls}">
      <td class="asin"><a href="https://www.amazon.co.uk/dp/${r.asin}" target="_blank" rel="noopener">${r.asin}</a></td>
      <td>${r.sku||''}</td>
      <td class="num">${fmt(r.uk_stock)}</td>
      <td class="num">${fmt(r.fbm_stock)}</td>
      <td class="num">${fmt(r.impr)}</td>
      <td class="num">${fmt(r.clk)}</td>
      <td class="num">${pct(r.cr)}</td>
      <td>${spark(wkimp)}</td>
      <td class="${isOld(r.last_order)?'old':''}">${r.last_order||'—'}</td>
      <td class="${isOld(r.last_vendor)?'old':''}">${r.last_vendor||'—'}</td>
      <td class="num">${fmt(r.vlife)}</td>
      <td class="hint">${tag(r.root_cause)} ${r.root_cause}</td>
    </tr>`;}).join('');
  document.querySelector('#t tbody').innerHTML=tb;
  document.getElementById('count').textContent=`${data.length.toLocaleString()} of ${ROWS.length.toLocaleString()} shown`;
}
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));
  c.classList.add('on');filter=c.dataset.f;render();});
document.getElementById('q').oninput=e=>{q=e.target.value.trim().toLowerCase();render();};
document.querySelector('#t thead').onclick=e=>{const th=e.target.closest('th');if(!th)return;
  const i=+th.dataset.i;if(i===sortI)sortDir*=-1;else{sortI=i;sortDir=(COLS[i][2]?-1:1);}render();};
document.getElementById('foot').innerHTML =
  `Zero-sale = 0 units in window across order_transaction (FBA+FBM, Completed) AND vendor_sales (1P, OVERLAP match). ` +
  `Stock is live-as-of-today (location_wise_inv_stock has no history); the 30-day window is historical. ` +
  `Red = out of stock (UK warehouse + FBM both 0). Amber = zero impressions. ` +
  `"Last vendor sale (lifetime)" clarifies that a large lifetime vendor figure with an old date is NOT an in-window sale. ` +
  `Source: generate_dataset.sql · data.json (${meta.run_date}).`;
render();
</script></body></html>"""

html = html.replace("__PAYLOAD__", payload)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"wrote {OUT}  ({os.path.getsize(OUT)} bytes, {len(rows)} rows)")
print(f"KPIs: universe={meta['universe_asins']} zero-sale={len(rows)} oos={oos} zeroimp={zero_imp} has_uk={has_uk} imp={tot_imp} clk={tot_clk}")
