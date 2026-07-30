# -*- coding: utf-8 -*-
# ph_task publish page = the FULL interactive dashboard (hero + filter bar + JS)
# with the table/stats/chips ALSO pre-rendered server-side, so it displays
# completely even if the ph_task viewer does not run JavaScript.
import json, re, os, sys, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_req20 as b
IMG=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"images.json"),encoding="utf-8"))
DASH=r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\.claude\worktrees\gifted-keller-42ebdd\development\abiraj_mini_aios_workbench\projects\PRJ-2026-017_ebay-competitor-keyword-research\evidence\final_outputs\REQ-20_ebay-competitor-keyword-research\REQ-20-D01_dashboard.html"
doc=open(DASH,encoding="utf-8").read()

def soldnum(s):
    s=(s or "").replace(",","").replace("+","").strip(); return int(s) if s.isdigit() else 0
def fbpct(s):
    m=re.match(r"([\d.]+)%", s or ""); return float(m.group(1)) if m else 0.0
esc=H.escape
COLS=["Image","Product Name","Competitor ID","Brand","Title","Sold Quantity","Price",
      "Feedback Rate","Shipping type","Promotion Type & %","Primary Keywords",
      "Secondary Keywords","Long-Tail Keywords","Notes"]
WRAP={"Product Name","Title","Primary Keywords","Secondary Keywords","Long-Tail Keywords","Notes"}
NUMH={"Sold Quantity","Price"}

rows=[]
for cat in b.order:
    pk,sk,lt=b.KW[cat]
    data=sorted(b.DATA[cat], key=lambda r:-soldnum(r[4]))
    for i,(cid,seller,brand,title,sold,price,fb,ship,promo) in enumerate(data):
        rows.append(dict(cat=cat,first=(i==0),img=IMG.get(cid,""),product=cat if i==0 else "",
            cid=cid,brand=brand,title=title,sold=sold,soldn=soldnum(sold),price=price.replace("GBP","£"),
            fb=fb,fbn=fbpct(fb),ship=ship,promo=("" if promo=="-" else promo),
            pk=pk if i==0 else "",sk=sk if i==0 else "",lt=lt if i==0 else "",notes="Competitor seller: "+seller))
maxsold=max(r["soldn"] for r in rows)
comp=len(rows); sold_tot=sum(r["soldn"] for r in rows)
brands=len({r["brand"] for r in rows if r["brand"] not in ("(not listed)","Unbranded","Does not apply")})
fbs=[r["fbn"] for r in rows if r["fbn"]>0]; avgfb=round(sum(fbs)/len(fbs),1)
def kf(n): return (str(round(n/1000,1))+"k") if n>=1000 else str(n)
def fbcolor(p): return "var(--green)" if p>=99 else "var(--amber)" if p>=97 else "var(--pink)"
def chips(s,c): return "".join(f'<span class="kw {c}">{esc(k.strip())}</span>' for k in s.split(",")) if s else ""

thead="".join(f'<th class="{"wrap" if c in WRAP else "num" if c in NUMH else ""}"><span class="thl">{esc(c)}</span></th>' for c in COLS)
stats="".join(f'<div class="stat"><div class="v">{v}</div><div class="k">{k}</div></div>'
              for k,v in [("Categories",len(b.order)),("Competitors",comp),("Units sold",kf(sold_tot)),("Avg feedback",f"{avgfb}%"),("Brands",brands)])
cats=list(dict.fromkeys(r["cat"] for r in rows))
fchips="".join(f'<span class="fchip{" on" if i==0 else ""}" data-c="{esc(c)}">{esc(c)}</span>' for i,c in enumerate(["All"]+cats))

body=[]
for r in rows:
    if r["first"]:
        body.append(f'<tr class="grp"><td colspan="{len(COLS)}"><div class="grpband"><span class="gdot"></span><span class="gname">{esc(r["product"])}</span></div></td></tr>')
        alt=0
    pct=max(3,round(r["soldn"]/maxsold*100)); fbw=max(6,min(100,(r["fbn"]-90)/10*100))
    ship='<span class="tag free">Free postage</span>' if "free" in r["ship"].lower() else '<span class="tag paid">With postage</span>'
    promo=f'<span class="tag promo">{esc(r["promo"])}</span>' if r["promo"] else '<span class="tag none">—</span>'
    imgc=f'<a href="https://www.ebay.co.uk/itm/{r["cid"]}" target="_blank" rel="noopener"><img loading="lazy" src="{r["img"]}" alt=""></a>' if r["img"] else ""
    cnt=(re.search(r"\(([^)]+)\)", r["fb"]) or [None,""])[1]
    altcls=" alt" if alt%2==1 else ""; alt+=1
    sh="free" if "free" in r["ship"].lower() else "paid"
    body.append(f'''<tr class="comp{altcls}" data-cat="{esc(r["cat"])}" data-ship="{sh}" data-promo="{1 if r["promo"] else 0}" data-sold="{r["soldn"]}" data-price="{(re.search(r"[\\d.]+",r["price"]) or [0])[0]}" data-fb="{r["fbn"]}" data-s="{esc((r["product"]+" "+r["cid"]+" "+r["brand"]+" "+r["title"]+" "+r["notes"]).lower())}">
<td class="imgcell">{imgc}</td>
<td class="product wrap">{esc(r["product"])}</td>
<td class="cid"><a href="https://www.ebay.co.uk/itm/{r["cid"]}" target="_blank" rel="noopener">{esc(r["cid"])}</a></td>
<td class="brand">{esc(r["brand"])}</td>
<td class="ttl">{esc(r["title"])}</td>
<td class="soldc num"><span class="soldn">{esc(r["sold"])}</span><div class="bar"><i style="width:{pct}%"></i></div></td>
<td class="price num">{esc(r["price"])}</td>
<td class="fbcell"><div class="fbtop"><span class="fbpct" style="color:{fbcolor(r["fbn"])}">{r["fbn"]}%</span><span class="fbcnt">{esc(cnt)}</span></div><div class="fbbar"><i style="width:{fbw}%;background:{fbcolor(r["fbn"])}"></i></div></td>
<td>{ship}</td><td>{promo}</td>
<td class="kwcell">{chips(r["pk"],"p")}</td><td class="kwcell">{chips(r["sk"],"s")}</td><td class="kwcell">{chips(r["lt"],"l")}</td>
<td class="notes">{esc(r["notes"])}</td></tr>''')
tbody="".join(body)

# inject pre-rendered fallback into the full dashboard doc (JS will rebuild identically if it runs)
doc=doc.replace('<div class="stats" id="stats"></div>', f'<div class="stats" id="stats">{stats}</div>')
doc=doc.replace('<div class="chips" id="chips"></div>', f'<div class="chips" id="chips">{fchips}</div>')
doc=doc.replace('<tr id="hd"></tr>', f'<tr id="hd">{thead}</tr>')
doc=doc.replace('<tbody id="tb"></tbody>', f'<tbody id="tb">{tbody}</tbody>')

OUT=r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\.claude\worktrees\gifted-keller-42ebdd\development\abiraj_mini_aios_workbench\projects\PRJ-2026-017_ebay-competitor-keyword-research\evidence\final_outputs\REQ-20_ebay-competitor-keyword-research\REQ-20-D01_ph_task.html"
open(OUT,"w",encoding="utf-8").write(doc)
print("ph_task publish html (full UI + pre-rendered fallback):",len(doc),"bytes ·",comp,"rows")
