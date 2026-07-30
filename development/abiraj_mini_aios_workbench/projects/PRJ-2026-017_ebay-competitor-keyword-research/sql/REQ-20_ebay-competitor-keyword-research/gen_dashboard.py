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

# Build rows exactly like the Excel: 14 columns, Product Name/SKU/keywords only on first row of each category
COLS=["Image","Product Name","Competitor ID","Brand","Title","Sold Quantity","Price",
      "Feedback Rate","Shipping type","Promotion Type & %","Primary Keywords",
      "Secondary Keywords","Long-Tail Keywords","Notes"]
rows=[]
for cat in b.order:
    pk,sk,lt=b.KW[cat]
    data=sorted(b.DATA[cat], key=lambda r:-soldnum(r[4]))
    for i,(cid,seller,brand,title,sold,price,fb,ship,promo) in enumerate(data):
        rows.append(dict(
            cat=cat, first=(i==0), img=IMG.get(cid,""),
            product=cat if i==0 else "",
            sku=b.SKU.get(cat,"") if i==0 else "",
            cid=cid, brand=brand, title=title, sold=sold, soldn=soldnum(sold),
            price=price.replace("GBP","£"), fb=fb, fbn=fbpct(fb), ship=ship,
            promo=("" if promo=="-" else promo),
            pk=pk if i==0 else "", sk=sk if i==0 else "", lt=lt if i==0 else "",
            notes="Competitor seller: "+seller ))

total_comp=len(rows)
total_sold=sum(r["soldn"] for r in rows)
maxsold=max(r["soldn"] for r in rows)
brands=sorted({r["brand"] for r in rows if r["brand"] not in ("(not listed)","Unbranded","Does not apply")})
allfb=[r["fbn"] for r in rows if r["fbn"]>0]; avgfb=round(sum(allfb)/len(allfb),1) if allfb else 0
DATA_JSON=json.dumps(rows, ensure_ascii=False)
STAT=json.dumps(dict(cats=len(b.order),comp=total_comp,sold=total_sold,brands=len(brands),avgfb=avgfb,maxsold=maxsold))

html=r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>eBay Competitor & Keyword Dashboard — Jarsini</title>
<style>
:root{
 --bg:#eef2f8;--panel:#fff;--ink:#1c2836;--muted:#6a7a90;--line:#e4eaf2;
 --brand:#2f5fb0;--brand2:#5b8de0;--band:#eaf1fc;--band-line:#d3e0f4;
 --green:#16a34a;--amber:#d9832b;--pink:#d24d72;
 --chipP:#e8effb;--chipS:#e7f6ee;--chipL:#fdeef3;--shadow:0 6px 22px rgba(28,52,94,.09);
}
*{box-sizing:border-box}html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
 -webkit-font-smoothing:antialiased;display:flex;flex-direction:column;height:100vh;overflow:hidden}
.top{flex:none;background:var(--panel);border-bottom:1px solid var(--line);box-shadow:var(--shadow);
 padding:11px 20px;display:flex;flex-wrap:wrap;gap:14px 22px;align-items:center;z-index:6}
.brandmark{display:flex;align-items:center;gap:11px}
.logo{width:37px;height:37px;border-radius:11px;background:linear-gradient(135deg,var(--brand),var(--brand2));
 display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;box-shadow:0 4px 12px rgba(47,95,176,.35)}
.brandmark h1{margin:0;font-size:16.5px;letter-spacing:-.3px}
.brandmark p{margin:1px 0 0;font-size:11px;color:var(--muted)}
.stats{display:flex;gap:20px;margin-left:auto;flex-wrap:wrap}
.stat .v{font-size:18px;font-weight:800;color:var(--brand);line-height:1}
.stat .k{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-top:3px;font-weight:700}
.search{display:flex;align-items:center;gap:7px;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:7px 11px;min-width:220px}
.search input{border:0;background:transparent;outline:0;color:var(--ink);font-size:13px;width:100%}
.tablewrap{flex:1;overflow:auto}
table{border-collapse:separate;border-spacing:0;font-size:12.5px;white-space:nowrap}
thead th{position:sticky;top:0;z-index:5;background:#eef4fc;color:#3a4a60;text-align:left;
 font-size:10.5px;text-transform:uppercase;letter-spacing:.4px;font-weight:800;
 padding:10px 12px;border-bottom:2px solid var(--band-line);border-right:1px solid var(--line)}
tbody td{padding:9px 12px;border-bottom:1px solid var(--line);border-right:1px solid var(--line);
 vertical-align:top;background:#fff}
tr.newcat td{border-top:2px solid var(--band-line)}
tr:hover td{background:#f7faff}
/* first two cols + keyword cols wrap; rest nowrap */
td.wrap,th.wrap{white-space:normal}
.imgcell{width:76px;min-width:76px;padding:6px}
.imgcell a{display:block;width:64px;height:64px;border-radius:9px;overflow:hidden;border:1px solid var(--line);background:#f4f7fc}
.imgcell img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .25s}
.imgcell a:hover img{transform:scale(1.12)}
.product{font-weight:800;color:var(--ink);min-width:150px;max-width:170px}
.sku{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:10.5px;color:var(--muted);min-width:150px;max-width:180px;white-space:normal;word-break:break-all}
.cid a{color:var(--brand);font-weight:700;font-family:ui-monospace,Menlo,Consolas,monospace;text-decoration:none;font-size:12px}
.cid a:hover{text-decoration:underline}
.brand{font-weight:600}
.ttl{white-space:normal;min-width:240px;max-width:300px;color:#33455c}
.soldc{min-width:110px}.soldn{font-weight:800}
.bar{height:6px;border-radius:5px;background:#e9eef6;overflow:hidden;margin-top:5px;width:92px}
.bar>i{display:block;height:100%;border-radius:5px;background:linear-gradient(90deg,var(--brand),var(--brand2));width:0;transition:width 1s cubic-bezier(.2,.8,.2,1)}
.price{font-weight:800}
.fb{display:flex;align-items:center;gap:6px;font-weight:600}
.fbdot{width:8px;height:8px;border-radius:50%}
.tag{display:inline-block;padding:3px 9px;border-radius:999px;font-size:10.5px;font-weight:700}
.tag.free{background:#e7f6ee;color:var(--green)}.tag.paid{background:#eef2f7;color:var(--muted)}
.tag.promo{background:#fdf1e3;color:var(--amber);white-space:normal}.tag.none{color:#b7c2d0}
.kwcell{white-space:normal;min-width:180px;max-width:230px;vertical-align:top}
.kw{display:inline-block;margin:0 4px 4px 0;padding:2px 7px;border-radius:6px;font-size:10.5px;font-weight:600;border:1px solid transparent}
.kw.p{background:var(--chipP);color:var(--brand);border-color:#d5e2f7}
.kw.s{background:var(--chipS);color:var(--green);border-color:#cdebd9}
.kw.l{background:var(--chipL);color:var(--pink);border-color:#f6d8e2}
.notes{white-space:normal;min-width:150px;max-width:180px;color:var(--muted);font-size:11.5px}
tr.hide{display:none}
.empty{padding:50px;text-align:center;color:var(--muted)}
</style></head>
<body>
<div class="top">
 <div class="brandmark"><div class="logo">eB</div>
  <div><h1>eBay Competitor &amp; Keyword Dashboard</h1>
   <p>Jarsini · eBay UK · 2026-07-30 · exact 14-column view · our 13 accounts excluded · all sold-proven</p></div></div>
 <div class="stats" id="stats"></div>
 <div class="search">🔎<input id="q" placeholder="Search…"></div>
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
document.getElementById('stats').innerHTML=[
 ['Categories',S.cats],['Competitors',S.comp],['Units sold',kf(S.sold)],
 ['Avg feedback',S.avgfb+'%'],['Brands',S.brands]
].map(x=>`<div class="stat"><div class="v">${x[1]}</div><div class="k">${x[0]}</div></div>`).join('');
const esc=s=>(s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fbColor=p=>p>=99?'var(--green)':p>=97?'var(--amber)':'var(--pink)';
const kw=(str,cls)=>!str?'':str.split(',').map(k=>`<span class="kw ${cls}">${esc(k.trim())}</span>`).join('');
document.getElementById('hd').innerHTML=COLS.map(c=>`<th class="${['Product Name','Title','Primary Keywords','Secondary Keywords','Long-Tail Keywords','Notes'].includes(c)?'wrap':''}">${esc(c)}</th>`).join('');
let html='';
ROWS.forEach(r=>{
 const pct=Math.max(3,Math.round(r.soldn/S.maxsold*100));
 const ship=r.ship.toLowerCase().includes('free')?'<span class="tag free">Free postage</span>':'<span class="tag paid">With postage</span>';
 const promo=r.promo?`<span class="tag promo">${esc(r.promo)}</span>`:'<span class="tag none">—</span>';
 const search=(r.product+' '+r.cid+' '+r.brand+' '+r.title+' '+r.notes).toLowerCase();
 const imgcell = r.img ? `<a href="https://www.ebay.co.uk/itm/${r.cid}" target="_blank" rel="noopener"><img loading="lazy" src="${r.img}" alt=""></a>` : '';
 html+=`<tr class="${r.first?'newcat':''}" data-s="${esc(search)}">
  <td class="imgcell">${imgcell}</td>
  <td class="product wrap">${esc(r.product)}</td>
  <td class="cid"><a href="https://www.ebay.co.uk/itm/${r.cid}" target="_blank" rel="noopener">${esc(r.cid)}</a></td>
  <td class="brand">${esc(r.brand)}</td>
  <td class="ttl">${esc(r.title)}</td>
  <td class="soldc"><span class="soldn">${esc(r.sold)}</span><div class="bar"><i data-w="${pct}"></i></div></td>
  <td class="price">${esc(r.price)}</td>
  <td><div class="fb"><span class="fbdot" style="background:${fbColor(r.fbn)}"></span>${esc(r.fb)}</div></td>
  <td>${ship}</td><td>${promo}</td>
  <td class="kwcell">${kw(r.pk,'p')}</td>
  <td class="kwcell">${kw(r.sk,'s')}</td>
  <td class="kwcell">${kw(r.lt,'l')}</td>
  <td class="notes">${esc(r.notes)}</td></tr>`;
});
document.getElementById('tb').innerHTML=html;
requestAnimationFrame(()=>document.querySelectorAll('.bar>i').forEach(b=>b.style.width=b.dataset.w+'%'));
document.getElementById('q').addEventListener('input',e=>{
 const q=e.target.value.trim().toLowerCase();let shown=0;
 document.querySelectorAll('tbody tr').forEach(tr=>{const ok=!q||tr.dataset.s.includes(q);tr.classList.toggle('hide',!ok);if(ok)shown++;});
 document.getElementById('empty').style.display=shown?'none':'block';
});
</script>
</body></html>"""
html=html.replace("__DATA__",DATA_JSON).replace("__STAT__",STAT).replace("__COLS__",json.dumps(COLS))
OUT=r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\.claude\worktrees\gifted-keller-42ebdd\development\abiraj_mini_aios_workbench\projects\PRJ-2026-017_ebay-competitor-keyword-research\evidence\final_outputs\REQ-20_ebay-competitor-keyword-research\REQ-20-D01_dashboard.html"
open(OUT,"w",encoding="utf-8").write(html)
print("14-column dashboard written:",len(html),"bytes ·",total_comp,"rows ·",len(COLS),"columns")
