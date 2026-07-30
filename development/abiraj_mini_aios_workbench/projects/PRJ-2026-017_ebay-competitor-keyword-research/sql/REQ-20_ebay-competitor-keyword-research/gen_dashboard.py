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
.logo{display:flex;align-items:center;gap:13px}
.ebay{font-weight:800;font-style:italic;font-size:30px;letter-spacing:-1px;line-height:1;
 text-shadow:0 2px 6px rgba(0,0,0,.18);animation:pop .7s cubic-bezier(.2,1.2,.3,1) both}
.ebay .r{color:var(--eR)}.ebay .b{color:var(--eB)}.ebay .a{color:var(--eY)}.ebay .g{color:var(--eG)}
.logo .divider{width:1px;height:34px;background:rgba(255,255,255,.35)}
.htxt h1{margin:0;font-size:18px;font-weight:800;letter-spacing:-.3px}
.htxt p{margin:2px 0 0;font-size:11.5px;opacity:.9}
.stats{display:flex;gap:12px;margin-left:auto;flex-wrap:wrap}
.stat{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);border-radius:13px;
 padding:9px 15px;text-align:center;min-width:78px;backdrop-filter:blur(6px);animation:rise .6s ease both}
.stat .v{font-size:20px;font-weight:800;line-height:1}
.stat .k{font-size:9.5px;text-transform:uppercase;letter-spacing:.5px;opacity:.85;margin-top:3px;font-weight:700}
.search{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.95);border-radius:11px;
 padding:9px 13px;min-width:230px;box-shadow:var(--shadow2)}
.search input{border:0;background:transparent;outline:0;color:var(--ink);font-size:13.5px;width:100%}
.search svg{flex:none}

/* ---------- table ---------- */
.tablewrap{flex:1;overflow:auto;padding:14px 16px 26px}
table{border-collapse:separate;border-spacing:0;font-size:12.5px;white-space:nowrap;width:100%;
 background:var(--panel);border-radius:16px;overflow:hidden;box-shadow:var(--shadow)}
thead th{position:sticky;top:0;z-index:6;background:linear-gradient(180deg,#f4f8ff,#e7f0fb);
 text-align:left;padding:14px 13px;border-bottom:2px solid var(--band-line)}
thead th .thl{display:inline-block;font-family:"Trebuchet MS","Segoe UI",system-ui,sans-serif;
 font-size:11px;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;
 background:linear-gradient(92deg,#24468a,#2f5fb0 45%,#5b8de0);-webkit-background-clip:text;background-clip:text;
 color:transparent;position:relative;padding-bottom:6px}
thead th .thl::after{content:"";position:absolute;left:0;bottom:0;width:18px;height:2.5px;border-radius:2px;
 background:linear-gradient(90deg,var(--eR),var(--eY));transition:width .3s}
thead th:hover .thl::after{width:100%}
tbody td{padding:9px 13px;border-bottom:1px solid var(--line);vertical-align:top;background:transparent}
tbody tr.comp{animation:rowin .5s ease both}
@keyframes rowin{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
tr.comp{transition:box-shadow .2s,transform .2s}
tr.comp:hover{box-shadow:inset 3px 0 0 var(--brand)}
tr.comp:hover td{background:#f5f9ff}
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
.soldc{min-width:118px}.soldn{font-weight:800}
.bar{height:7px;border-radius:6px;background:#e8eef7;overflow:hidden;margin-top:5px;width:96px}
.bar>i{display:block;height:100%;border-radius:6px;width:0;
 background:linear-gradient(90deg,var(--brand),var(--brand2));transition:width 1.1s cubic-bezier(.2,.8,.2,1)}
.price{font-weight:800}
.fb{display:flex;align-items:center;gap:7px;font-weight:600}
.fbdot{width:9px;height:9px;border-radius:50%;box-shadow:0 0 0 3px rgba(0,0,0,.04)}
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
    <span class="ebay"><span class="r">e</span><span class="b">b</span><span class="a">a</span><span class="g">y</span></span>
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

document.getElementById('hd').innerHTML=COLS.map(c=>`<th class="${['Product Name','Title','Primary Keywords','Secondary Keywords','Long-Tail Keywords','Notes'].includes(c)?'wrap':''}"><span class="thl">${esc(c)}</span></th>`).join('');
let html='',idx=0;
ROWS.forEach(r=>{
 if(r.first){html+=`<tr class="grp"><td colspan="${COLS.length}"><div class="grpband"><span class="gdot"></span><span class="gname">${esc(r.product)}</span></div></td></tr>`;}
 const pct=Math.max(3,Math.round(r.soldn/S.maxsold*100));
 const ship=r.ship.toLowerCase().includes('free')?'<span class="tag free">Free postage</span>':'<span class="tag paid">With postage</span>';
 const promo=r.promo?`<span class="tag promo">${esc(r.promo)}</span>`:'<span class="tag none">—</span>';
 const search=(r.product+' '+r.cid+' '+r.brand+' '+r.title+' '+r.notes).toLowerCase();
 const imgcell=r.img?`<a href="https://www.ebay.co.uk/itm/${r.cid}" target="_blank" rel="noopener"><img loading="lazy" src="${r.img}" alt=""></a>`:'';
 const delay=Math.min(idx*28,700); idx++;
 html+=`<tr class="comp" style="animation-delay:${delay}ms" data-s="${esc(search)}">
  <td class="imgcell">${imgcell}</td>
  <td class="product wrap">${esc(r.product)}</td>
  <td class="cid"><a href="https://www.ebay.co.uk/itm/${r.cid}" target="_blank" rel="noopener">${esc(r.cid)}</a></td>
  <td class="brand">${esc(r.brand)}</td>
  <td class="ttl">${esc(r.title)}</td>
  <td class="soldc"><span class="soldn">${esc(r.sold)}</span><div class="bar"><i data-w="${pct}"></i></div></td>
  <td class="price">${esc(r.price)}</td>
  <td><div class="fb"><span class="fbdot" style="background:${fbColor(r.fbn)}"></span>${esc(r.fb)}</div></td>
  <td>${ship}</td><td>${promo}</td>
  <td class="kwcell">${kw(r.pk,'p')}</td><td class="kwcell">${kw(r.sk,'s')}</td><td class="kwcell">${kw(r.lt,'l')}</td>
  <td class="notes">${esc(r.notes)}</td></tr>`;
});
document.getElementById('tb').innerHTML=html;
setTimeout(()=>{document.querySelectorAll('.bar>i').forEach(b=>b.style.width=b.dataset.w+'%');countUp();},180);
document.getElementById('q').addEventListener('input',e=>{
 const q=e.target.value.trim().toLowerCase();let shown=0;
 document.querySelectorAll('tbody tr.comp').forEach(tr=>{const ok=!q||tr.dataset.s.includes(q);tr.classList.toggle('hide',!ok);if(ok)shown++;});
 document.querySelectorAll('tbody tr.grp').forEach(g=>{let n=g.nextElementSibling,any=false;
   while(n&&n.classList.contains('comp')){if(!n.classList.contains('hide'))any=true;n=n.nextElementSibling;}
   g.classList.toggle('hide',!any);});
 document.getElementById('empty').style.display=shown?'none':'block';
});
</script>
</body></html>"""
html=html.replace("__DATA__",DATA_JSON).replace("__STAT__",STAT).replace("__COLS__",json.dumps(COLS))
OUT=r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\.claude\worktrees\gifted-keller-42ebdd\development\abiraj_mini_aios_workbench\projects\PRJ-2026-017_ebay-competitor-keyword-research\evidence\final_outputs\REQ-20_ebay-competitor-keyword-research\REQ-20-D01_dashboard.html"
open(OUT,"w",encoding="utf-8").write(html)
print("enhanced dashboard written:",len(html),"bytes ·",total_comp,"rows")
