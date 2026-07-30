# -*- coding: utf-8 -*-
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_req20 as b
IMG=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"images.json"),encoding="utf-8"))

def soldnum(s):
    s=(s or "").replace(",","").replace("+","").strip()
    return int(s) if s.isdigit() else 0
def fbpct(s):
    m=re.match(r"([\d.]+)%", s or ""); return float(m.group(1)) if m else 0.0

COLS=["Image","Product Name","Competitor ID","Brand","Title","Sold Quantity","Price",
      "Feedback Rate","Shipping type","Promotion Type & %","Primary Keywords",
      "Secondary Keywords","Long-Tail Keywords","Notes"]
rows=[]
for cat in b.order:
    pk,sk,lt=b.KW[cat]
    data=sorted(b.DATA[cat], key=lambda r:-soldnum(r[4]))
    for i,(cid,seller,brand,title,sold,price,fb,ship,promo) in enumerate(data):
        rows.append(dict(cat=cat, first=(i==0), img=IMG.get(cid,""),
            product=cat if i==0 else "", cid=cid, brand=brand, title=title, sold=sold, soldn=soldnum(sold),
            price=price.replace("GBP","£"), fb=fb, fbn=fbpct(fb), ship=ship,
            promo=("" if promo=="-" else promo),
            pk=pk if i==0 else "", sk=sk if i==0 else "", lt=lt if i==0 else "",
            notes="Competitor seller: "+seller ))

total_comp=len(rows); total_sold=sum(r["soldn"] for r in rows); maxsold=max(r["soldn"] for r in rows)
brands=sorted({r["brand"] for r in rows if r["brand"] not in ("(not listed)","Unbranded","Does not apply")})
allfb=[r["fbn"] for r in rows if r["fbn"]>0]; avgfb=round(sum(allfb)/len(allfb),1) if allfb else 0
DATA_JSON=json.dumps(rows, ensure_ascii=False)
STAT=json.dumps(dict(cats=len(b.order),comp=total_comp,sold=total_sold,brands=len(brands),avgfb=avgfb,maxsold=maxsold))

html=r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>eBay Competitor & Keyword Dashboard — Jarsini</title>
<style>
:root{
 --bg:#eaf0f8;--panel:#ffffff;--ink:#16202e;--muted:#66788f;--line:#e6ecf4;
 --brand:#2f5fb0;--brand2:#5b8de0;--band1:#eef4fd;--band2:#f6f9ff;--band-line:#d6e3f6;
 --green:#12a150;--amber:#d9832b;--pink:#d24d72;
 --chipP:#e9f0fc;--chipS:#e6f6ec;--chipL:#fdeef4;
 --eR:#e53238;--eB:#0064d2;--eY:#f5af02;--eG:#86b817;
 --shadow:0 10px 30px rgba(26,52,96,.10);--shadow2:0 4px 14px rgba(26,52,96,.08);
}
*{box-sizing:border-box}html,body{height:100%}
body{margin:0;color:var(--ink);height:100vh;overflow:hidden;display:flex;flex-direction:column;
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased;
 background:radial-gradient(1200px 500px at 10% -5%,#e7f0ff 0%,transparent 60%),radial-gradient(1000px 500px at 100% 0%,#fdeef3 0%,transparent 55%),var(--bg)}

/* ---------- hero ---------- */
.hero{flex:none;position:relative;overflow:hidden;color:#fff;
 background:linear-gradient(120deg,#24468a 0%,#2f5fb0 45%,#4f8ae0 100%);
 padding:16px 26px;box-shadow:var(--shadow);z-index:8}
.hero::after{content:"";position:absolute;inset:0;background:
 radial-gradient(600px 200px at 85% -40%,rgba(255,255,255,.25),transparent 60%);pointer-events:none}
.hero::before{content:"";position:absolute;top:-60%;left:-10%;width:60%;height:220%;
 background:linear-gradient(90deg,transparent,rgba(255,255,255,.14),transparent);transform:skewX(-20deg);
 animation:sheen 7s ease-in-out infinite}
@keyframes sheen{0%{left:-30%}55%{left:120%}100%{left:120%}}
.herorow{position:relative;display:flex;flex-wrap:wrap;gap:16px 26px;align-items:center;z-index:2}
.logo{display:flex;align-items:center;gap:14px}
.logobox{display:inline-flex;align-items:center;background:#fff;border-radius:13px;
 padding:8px 15px 9px;box-shadow:0 6px 18px rgba(0,0,0,.22);animation:pop .7s cubic-bezier(.2,1.2,.3,1) both}
.ebay{font-weight:800;font-style:italic;font-size:29px;letter-spacing:-1px;line-height:1}
.ebay .r{color:var(--eR)}.ebay .b{color:var(--eB)}.ebay .a{color:var(--eY)}.ebay .g{color:var(--eG)}
.logo .divider{width:1px;height:36px;background:rgba(255,255,255,.4)}
.htxt h1{margin:0;font-size:18px;font-weight:800;letter-spacing:-.3px}
.htxt p{margin:2px 0 0;font-size:11.5px;opacity:.9}
.stats{display:flex;gap:12px;margin-left:auto;flex-wrap:wrap}
.stat{background:#fff;border:1px solid rgba(255,255,255,.6);border-radius:13px;
 padding:9px 16px;text-align:center;min-width:82px;box-shadow:0 6px 16px rgba(15,32,66,.18);animation:rise .6s ease both}
.stat .v{font-size:21px;font-weight:800;line-height:1;
 background:linear-gradient(92deg,#24468a,#2f5fb0 55%,#5b8de0);-webkit-background-clip:text;background-clip:text;color:transparent}
.stat .k{font-size:9.5px;text-transform:uppercase;letter-spacing:.5px;color:#7183a0;margin-top:4px;font-weight:800}
.search{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.95);border-radius:11px;
 padding:9px 13px;min-width:230px;box-shadow:var(--shadow2)}
.search input{border:0;background:transparent;outline:0;color:var(--ink);font-size:13.5px;width:100%}
.search svg{flex:none}

/* ---------- filter bar ---------- */
.filterbar{flex:none;display:flex;flex-wrap:nowrap;gap:12px;align-items:center;
 padding:9px 18px;background:rgba(255,255,255,.72);backdrop-filter:blur(8px);
 border-bottom:1px solid var(--line);box-shadow:0 4px 14px rgba(26,52,96,.05);z-index:7}
.chips{display:flex;gap:7px;flex-wrap:nowrap;flex:1;min-width:0;overflow-x:auto;padding:6px 2px}
.chips::-webkit-scrollbar{height:6px}
.chips::-webkit-scrollbar-thumb{background:#cdd9ec;border-radius:6px}
.fspacer{display:none}
.fgroup,.ftoggle,.fsel,.count,.fclear{flex:none;white-space:nowrap}
.fchip{cursor:pointer;border:1px solid var(--line);background:#fff;color:var(--muted);
 padding:7px 13px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;transition:all .18s}
.fchip:hover{transform:translateY(-2px);color:var(--ink);border-color:var(--brand2)}
.fchip.on{background:linear-gradient(92deg,#2f5fb0,#5b8de0);color:#fff;border-color:transparent;
 box-shadow:0 6px 15px rgba(47,95,176,.32)}
.fspacer{flex:1}
.fgroup{display:flex;align-items:center;gap:7px}
.fgroup label{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.4px}
.fsel{border:1px solid var(--line);background:#fff;border-radius:10px;padding:7px 11px;font-size:12.5px;
 font-weight:600;color:var(--ink);cursor:pointer;outline:0}
.fsel:focus{border-color:var(--brand2)}
.ftoggle{display:flex;align-items:center;gap:6px;cursor:pointer;font-size:12.5px;font-weight:700;color:var(--muted);
 border:1px solid var(--line);background:#fff;border-radius:10px;padding:7px 11px;transition:all .18s;user-select:none}
.ftoggle.on{background:#fdf1e3;color:var(--amber);border-color:#f4d8b3}
.ftoggle input{display:none}
.count{font-size:12px;font-weight:700;color:var(--muted)}
.count b{color:var(--brand)}
.fclear{cursor:pointer;font-size:12px;font-weight:700;color:var(--pink);background:none;border:0;padding:6px 4px}
.fclear:hover{text-decoration:underline}

/* ---------- table ---------- */
.tablewrap{flex:1;min-height:0;overflow:auto;padding:0}
table{border-collapse:separate;border-spacing:0;font-size:12.5px;white-space:nowrap;width:100%;
 background:var(--panel)}
thead th{position:sticky;top:0;z-index:6;background:linear-gradient(180deg,#f4f8ff,#e7f0fb);
 text-align:left;padding:14px 13px;border-bottom:2px solid var(--band-line)}
thead th:first-child{left:0;z-index:9}
thead th:nth-child(2){left:78px;z-index:9}
thead th.num{text-align:right}
thead th .thl{display:inline-block;font-family:"Trebuchet MS","Segoe UI",system-ui,sans-serif;
 font-size:11.5px;font-weight:900;letter-spacing:1.3px;text-transform:uppercase;
 background:linear-gradient(92deg,#24468a,#2f5fb0 45%,#5b8de0);-webkit-background-clip:text;background-clip:text;
 color:transparent;position:relative;padding-bottom:6px}
thead th .thl::after{content:"";position:absolute;left:0;bottom:0;width:18px;height:2.5px;border-radius:2px;
 background:linear-gradient(90deg,var(--eR),var(--eY));transition:width .3s}
thead th:hover .thl::after{width:100%}
tbody td{padding:9px 13px;border-bottom:1px solid var(--line);vertical-align:middle;background:#fff}
tbody tr.comp{animation:rowin .5s ease both}
@keyframes rowin{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
tbody tr.alt>td{background:#f6f9fe}                         /* zebra */
tr.comp:hover>td{background:#e9f2ff}                        /* hover wins */
td.num{text-align:right;font-variant-numeric:tabular-nums}
th.num{font-variant-numeric:tabular-nums}
/* sticky first two columns */
tbody td.imgcell{position:sticky;left:0;z-index:5;background:#fff}
tbody td.product{position:sticky;left:78px;z-index:5;background:#fff;box-shadow:6px 0 10px -8px rgba(20,40,80,.18)}
tbody tr.alt>td.imgcell,tbody tr.alt>td.product{background:#f6f9fe}
tr.comp:hover>td.imgcell,tr.comp:hover>td.product{background:#e9f2ff}
thead th:nth-child(2){box-shadow:6px 0 10px -8px rgba(20,40,80,.18)}
td.wrap,th.wrap{white-space:normal}
.imgcell{width:78px;min-width:78px;padding:7px 6px}
.imgcell a{display:block;width:66px;height:66px;border-radius:12px;overflow:hidden;border:1px solid var(--line);
 background:#eef3fb;box-shadow:var(--shadow2)}
.imgcell img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .35s cubic-bezier(.2,.8,.2,1)}
.imgcell a:hover img{transform:scale(1.18)}
.product{font-weight:800;color:var(--ink);min-width:150px;max-width:170px}
.cid a{color:var(--brand);font-weight:700;font-family:ui-monospace,Menlo,Consolas,monospace;text-decoration:none;font-size:12px}
.cid a:hover{text-decoration:underline}
.brand{font-weight:600}
.ttl{white-space:normal;min-width:230px;max-width:300px;color:#33455c}
.soldc{min-width:118px;text-align:right}.soldn{font-weight:800;font-variant-numeric:tabular-nums}
.bar{height:7px;border-radius:6px;background:#e8eef7;overflow:hidden;margin-top:5px;width:96px;margin-left:auto}
.bar>i{display:block;height:100%;border-radius:6px;width:0;
 background:linear-gradient(90deg,var(--brand),var(--brand2));transition:width 1.1s cubic-bezier(.2,.8,.2,1)}
.price{font-weight:800}
/* feedback mini bar */
.fbcell{min-width:118px}
.fbtop{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.fbpct{font-weight:800;font-variant-numeric:tabular-nums}
.fbcnt{font-size:10.5px;color:var(--muted);font-weight:700}
.fbbar{height:6px;border-radius:5px;background:#e8eef7;overflow:hidden;margin-top:5px;width:100px}
.fbbar>i{display:block;height:100%;border-radius:5px;width:0;transition:width 1s cubic-bezier(.2,.8,.2,1)}
.tag{display:inline-block;padding:3px 10px;border-radius:999px;font-size:10.5px;font-weight:700}
.tag.free{background:#e5f6ec;color:var(--green)}.tag.paid{background:#eef2f8;color:var(--muted)}
.tag.promo{background:#fdf1e3;color:var(--amber);white-space:normal}.tag.none{color:#bcc7d4}
.kwcell{white-space:normal;min-width:178px;max-width:230px}
.kw{display:inline-block;margin:0 4px 4px 0;padding:3px 8px;border-radius:7px;font-size:10.5px;font-weight:600;
 border:1px solid transparent;transition:transform .15s}
.kw:hover{transform:translateY(-1px)}
.kw.p{background:var(--chipP);color:var(--brand);border-color:#d5e2f7}
.kw.s{background:var(--chipS);color:var(--green);border-color:#cdebd9}
.kw.l{background:var(--chipL);color:var(--pink);border-color:#f6d8e2}
.notes{white-space:normal;min-width:150px;max-width:180px;color:var(--muted);font-size:11.5px}
/* category band */
tr.grp td{padding:0;border:0}
.grpband{display:flex;align-items:center;gap:12px;padding:13px 16px;margin-top:2px;
 background:linear-gradient(90deg,var(--band1),var(--band2));border-top:1px solid var(--band-line);border-bottom:1px solid var(--band-line)}
.grpband .gdot{width:10px;height:10px;border-radius:50%;background:var(--brand);position:relative;flex:none}
.grpband .gdot::after{content:"";position:absolute;inset:-5px;border-radius:50%;border:2px solid var(--brand);opacity:.4;animation:pulse 2s ease-out infinite}
@keyframes pulse{0%{transform:scale(.7);opacity:.6}100%{transform:scale(1.6);opacity:0}}
.grpband .gname{font-size:15px;font-weight:800;letter-spacing:-.2px}
.grpband .gcount{background:#fff;border:1px solid var(--band-line);border-radius:999px;padding:3px 11px;font-size:11px;font-weight:700;color:var(--brand)}
tr.hide{display:none}
.empty{padding:50px;text-align:center;color:var(--muted)}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.8) rotate(-4deg)}to{opacity:1;transform:none}}
/* scrollbar */
.tablewrap::-webkit-scrollbar{height:11px;width:11px}
.tablewrap::-webkit-scrollbar-thumb{background:#c3d3ea;border-radius:8px;border:3px solid var(--bg)}
.tablewrap::-webkit-scrollbar-thumb:hover{background:#a9bfe0}
@media(max-width:820px){.stats{gap:8px}.ttl{max-width:180px}.htxt{display:none}}
</style></head>
<body>
<div class="hero">
 <div class="herorow">
  <div class="logo">
    <span class="logobox"><span class="ebay"><span class="r">e</span><span class="b">b</span><span class="a">a</span><span class="g">y</span></span></span>
    <span class="divider"></span>
    <div class="htxt"><h1>Competitor &amp; Keyword Dashboard</h1>
     <p>Jarsini · eBay UK · 2026-07-30 · our 13 accounts excluded · all competitors sold-proven</p></div>
  </div>
  <div class="stats" id="stats"></div>
  <div class="search">
   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#66788f" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>
   <input id="q" placeholder="Search seller / brand / title…">
  </div>
 </div>
</div>
<div class="filterbar">
 <div class="chips" id="chips"></div>
 <div class="fspacer"></div>
 <div class="fgroup"><label>Shipping</label>
   <select class="fsel" id="fship"><option value="">All</option><option value="free">Free postage</option><option value="paid">With postage</option></select></div>
 <label class="ftoggle" id="fpromo"><input type="checkbox">🏷️ Promotions only</label>
 <div class="fgroup"><label>Sort</label>
   <select class="fsel" id="fsort">
     <option value="sold">Most sold</option>
     <option value="price_lo">Price: low → high</option>
     <option value="price_hi">Price: high → low</option>
     <option value="fb">Best feedback</option>
   </select></div>
 <span class="count" id="count"></span>
 <button class="fclear" id="fclear">Reset</button>
</div>
<div class="tablewrap">
 <table>
  <thead><tr id="hd"></tr></thead>
  <tbody id="tb"></tbody>
 </table>
 <div class="empty" id="empty" style="display:none">No matches.</div>
</div>
<script>
const ROWS=__DATA__, S=__STAT__, COLS=__COLS__;
const kf=n=>n>=1000?(n/1000).toFixed(n>=10000?0:1)+'k':''+n;
const esc=s=>(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fbColor=p=>p>=99?'var(--green)':p>=97?'var(--amber)':'var(--pink)';
const kw=(str,cls)=>!str?'':str.split(',').map(k=>`<span class="kw ${cls}">${esc(k.trim())}</span>`).join('');

// KPI tiles with count-up
const KP=[['Categories',S.cats,false],['Competitors',S.comp,false],['Units sold',S.sold,true],['Avg feedback',S.avgfb,'pct'],['Brands',S.brands,false]];
document.getElementById('stats').innerHTML=KP.map((k,i)=>`<div class="stat" style="animation-delay:${i*80}ms"><div class="v" data-n="${k[1]}" data-fmt="${k[2]}">0</div><div class="k">${k[0]}</div></div>`).join('');
function countUp(){document.querySelectorAll('.stat .v').forEach(el=>{
  const target=+el.dataset.n, fmt=el.dataset.fmt; const t0=performance.now(), dur=900;
  function tick(t){let p=Math.min(1,(t-t0)/dur);p=1-Math.pow(1-p,3);let v=target*p;
    el.textContent = fmt==='true'?kf(Math.round(v)) : fmt==='pct'?v.toFixed(1)+'%' : Math.round(v);
    if(p<1)requestAnimationFrame(tick);}
  requestAnimationFrame(tick);});}

const WRAP=['Product Name','Title','Primary Keywords','Secondary Keywords','Long-Tail Keywords','Notes'];
const NUMH=['Sold Quantity','Price'];
document.getElementById('hd').innerHTML=COLS.map(c=>`<th class="${WRAP.includes(c)?'wrap':NUMH.includes(c)?'num':''}"><span class="thl">${esc(c)}</span></th>`).join('');
let html='',idx=0;
ROWS.forEach(r=>{
 if(r.first){html+=`<tr class="grp"><td colspan="${COLS.length}"><div class="grpband"><span class="gdot"></span><span class="gname">${esc(r.product)}</span></div></td></tr>`;}
 const pct=Math.max(3,Math.round(r.soldn/S.maxsold*100));
 const ship=r.ship.toLowerCase().includes('free')?'<span class="tag free">Free postage</span>':'<span class="tag paid">With postage</span>';
 const promo=r.promo?`<span class="tag promo">${esc(r.promo)}</span>`:'<span class="tag none">—</span>';
 const search=(r.product+' '+r.cid+' '+r.brand+' '+r.title+' '+r.notes).toLowerCase();
 const imgcell=r.img?`<a href="https://www.ebay.co.uk/itm/${r.cid}"><img loading="lazy" src="${r.img}" alt=""></a>`:'';
 const delay=Math.min(idx*28,700); idx++;
 const priceNum=parseFloat((r.price.match(/[\d.]+/)||[0])[0])||0;
 const shipKey=r.ship.toLowerCase().includes('free')?'free':'paid';
 html+=`<tr class="comp" style="animation-delay:${delay}ms" data-s="${esc(search)}" data-cat="${esc(r.cat)}" data-ship="${shipKey}" data-promo="${r.promo?1:0}" data-sold="${r.soldn}" data-price="${priceNum}" data-fb="${r.fbn}">
  <td class="imgcell">${imgcell}</td>
  <td class="product wrap">${esc(r.product)}</td>
  <td class="cid"><a href="https://www.ebay.co.uk/itm/${r.cid}">${esc(r.cid)}</a></td>
  <td class="brand">${esc(r.brand)}</td>
  <td class="ttl">${esc(r.title)}</td>
  <td class="soldc num"><span class="soldn">${esc(r.sold)}</span><div class="bar"><i data-w="${pct}"></i></div></td>
  <td class="price num">${esc(r.price)}</td>
  <td class="fbcell"><div class="fbtop"><span class="fbpct" style="color:${fbColor(r.fbn)}">${r.fbn}%</span><span class="fbcnt">${esc((r.fb.match(/\(([^)]+)\)/)||[])[1]||'')}</span></div><div class="fbbar"><i data-fw="${Math.max(6,Math.min(100,(r.fbn-90)/10*100))}" style="background:${fbColor(r.fbn)}"></i></div></td>
  <td>${ship}</td><td>${promo}</td>
  <td class="kwcell">${kw(r.pk,'p')}</td><td class="kwcell">${kw(r.sk,'s')}</td><td class="kwcell">${kw(r.lt,'l')}</td>
  <td class="notes">${esc(r.notes)}</td></tr>`;
});
const tb=document.getElementById('tb');
tb.innerHTML=html;
function animBars(){document.querySelectorAll('.bar>i').forEach(b=>b.style.width=b.dataset.w+'%');
  document.querySelectorAll('.fbbar>i').forEach(b=>b.style.width=b.dataset.fw+'%');}
setTimeout(()=>{animBars();countUp();},180);

// ---- filters ----
const CH=['All',...[...new Set(ROWS.map(r=>r.cat))]];
document.getElementById('chips').innerHTML=CH.map((c,i)=>`<span class="fchip${i===0?' on':''}" data-c="${esc(c)}">${esc(c)}</span>`).join('');
const st={cat:'All',ship:'',promo:false,sort:'sold',q:''};

function groups(){const out=[];let cur=null;[...tb.children].forEach(tr=>{
  if(tr.classList.contains('grp')){cur={band:tr,rows:[]};out.push(cur);}else if(cur)cur.rows.push(tr);});return out;}
function sortKey(a,b){
  if(st.sort==='sold')return b.dataset.sold-a.dataset.sold;
  if(st.sort==='price_lo')return a.dataset.price-b.dataset.price;
  if(st.sort==='price_hi')return b.dataset.price-a.dataset.price;
  if(st.sort==='fb')return b.dataset.fb-a.dataset.fb;return 0;}
function applyAll(){
  let shown=0;
  groups().forEach(g=>{
    // reorder rows within this category per sort
    const sorted=g.rows.slice().sort(sortKey);
    let ref=g.band; sorted.forEach(tr=>{ref.after(tr);ref=tr;});
    let any=false, vi=0;
    sorted.forEach(tr=>{
      const ok=(st.cat==='All'||tr.dataset.cat===st.cat)
        && (!st.ship||tr.dataset.ship===st.ship)
        && (!st.promo||tr.dataset.promo==='1')
        && (!st.q||tr.dataset.s.includes(st.q));
      tr.classList.toggle('hide',!ok);
      if(ok){any=true;shown++;tr.classList.toggle('alt',vi%2===1);vi++;}
      else tr.classList.remove('alt');
    });
    g.band.classList.toggle('hide',!any);
  });
  document.getElementById('count').innerHTML=`<b>${shown}</b> of ${ROWS.length} competitors`;
  document.getElementById('empty').style.display=shown?'none':'block';
}
document.getElementById('chips').addEventListener('click',e=>{const c=e.target.closest('.fchip');if(!c)return;
  document.querySelectorAll('.fchip').forEach(x=>x.classList.remove('on'));c.classList.add('on');st.cat=c.dataset.c;applyAll();});
document.getElementById('fship').addEventListener('change',e=>{st.ship=e.target.value;applyAll();});
document.getElementById('fpromo').addEventListener('change',e=>{st.promo=e.target.checked;e.target.closest('.ftoggle').classList.toggle('on',e.target.checked);applyAll();});
document.getElementById('fsort').addEventListener('change',e=>{st.sort=e.target.value;applyAll();setTimeout(animBars,20);});
document.getElementById('q').addEventListener('input',e=>{st.q=e.target.value.trim().toLowerCase();applyAll();});
document.getElementById('fclear').addEventListener('click',()=>{st.cat='All';st.ship='';st.promo=false;st.sort='sold';st.q='';
  document.getElementById('q').value='';document.getElementById('fship').value='';document.getElementById('fsort').value='sold';
  document.querySelector('#fpromo input').checked=false;document.getElementById('fpromo').classList.remove('on');
  document.querySelectorAll('.fchip').forEach((x,i)=>x.classList.toggle('on',i===0));applyAll();});
applyAll();
</script>
</body></html>"""
html=html.replace("__DATA__",DATA_JSON).replace("__STAT__",STAT).replace("__COLS__",json.dumps(COLS))
OUT=r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\.claude\worktrees\gifted-keller-42ebdd\development\abiraj_mini_aios_workbench\projects\PRJ-2026-017_ebay-competitor-keyword-research\evidence\final_outputs\REQ-20_ebay-competitor-keyword-research\REQ-20-D01_dashboard.html"
open(OUT,"w",encoding="utf-8").write(html)
print("enhanced dashboard written:",len(html),"bytes ·",total_comp,"rows")
