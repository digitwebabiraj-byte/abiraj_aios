# -*- coding: utf-8 -*-
"""
RICH static (NO-JS) HTML render of REQ-19-D01 for the ph_task portal (which runs no JavaScript).
Matches the interactive dashboard's LOOK — gradient KPI cards, in-cell data bars, chips, flags,
stock dots, group dividers, sticky header, frozen columns, CSS animations — all pure CSS, no <script>.
Interactive behaviours (search/sort/filter/hover-zoom) can't run in the portal and are omitted.
All 11k rows pre-rendered. Same data layer (fetch_records) as the dashboard + xlsx.
"""
import os, sys, html
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sql", "REQ-19_ebay-product-performance-analysis"))
from eppr_build_d01 import fetch_records, HEADERS

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","evidence","final_outputs",
      "REQ-19_ebay-product-performance-analysis","REQ-19-D01_ph_task.html"))
MONEY={11,12,13,14,15,16,20,21,22}; PCT={23,27,28}; NUM={17,18,19,24,25,26,31}
LEFT={0,1,2,3,4,5,6,8,9,32,33,34}; GDIV={7,11,17,21,24,30}; ZMUTE={13,14,15,16,18,19,20,24,25,26}
W=[62,150,150,120,300,120,150,96,120,102,88,102,96,108,96,94,94,90,72,72,112,104,104,98,104,80,84,72,106,92,116,92,122,150,92]
IC={"layers":'<svg viewBox="0 0 24 24"><path d="M12 2 2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
    "card":'<svg viewBox="0 0 24 24"><rect x="1.5" y="4.5" width="21" height="15" rx="2.5"/><path d="M1.5 9.5h21"/></svg>',
    "cart":'<svg viewBox="0 0 24 24"><circle cx="9" cy="21" r="1.4"/><circle cx="19" cy="21" r="1.4"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23.5 6H6"/></svg>',
    "bag":'<svg viewBox="0 0 24 24"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>',
    "trend":'<svg viewBox="0 0 24 24"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'}

def render():
    recs, d0, anchor = fetch_records()
    ukR=deR=units=orders=promo=0; maxRev=1.0; maxUnits=1
    for r in recs:
        v=r["v"]
        if v[7]=="UK": ukR+=v[20] or 0
        else: deR+=v[20] or 0
        units+=v[18] or 0; orders+=v[19] or 0
        if v[32]=="Promoted": promo+=1
        if (v[20] or 0)>maxRev: maxRev=v[20]
        if (v[18] or 0)>maxUnits: maxUnits=v[18]
    n=len(recs); ppct=round(promo/n*100) if n else 0
    KP=[("Listings","#3b6ef6","#eaf1ff","rgba(59,110,246,.22)",IC["layers"],f"{n:,}","active · UK + DE",None),
        ("UK Revenue","#4f46e5","#edecfe","rgba(79,70,229,.22)",IC["card"],f"£{ukR:,.0f}","30-day · GBP",None),
        ("DE Revenue","#8b5cf6","#f2eafe","rgba(139,92,246,.22)",IC["card"],f"€{deR:,.0f}","30-day · EUR",None),
        ("Units Sold","#0ea5a4","#e0f6f5","rgba(14,165,164,.22)",IC["cart"],f"{units:,}","last 30 days",None),
        ("Orders","#f59e0b","#fdf0d9","rgba(245,158,11,.22)",IC["bag"],f"{orders:,}","last 30 days",None),
        ("Promoted","#16a34a","#e3f6e9","rgba(22,163,74,.22)",IC["trend"],f"{ppct}%","of listings",ppct)]
    kpi_html=""
    for i,(lbl,c,bg,glow,icon,val,sub,bar) in enumerate(KP):
        barhtml=f'<div class=bar><i style="width:{max(3,min(100,bar))}%"></i></div>' if bar is not None else ''
        kpi_html+=(f'<div class=k style="--c:{c};--bg:{bg};--glow:{glow};animation-delay:{.04+i*.05:.2f}s">'
                   f'<div class=kh><span class=ki>{icon}</span><span class=kl>{lbl}</span></div>'
                   f'<div class=kv>{val}</div>{barhtml}<div class=ks>{sub}</div></div>')

    def cell(v,i,cur):
        if v is None or v=="NO DATA": return '<span class=nd>NO DATA</span>'
        if i==0: return f'<img loading=lazy class=t src="{html.escape(str(v))}">'
        if ZMUTE and i in ZMUTE and v==0: return '<span class=z>–</span>'
        if i==7: return f'<span class="m {v}"><span class=fl>{"🇬🇧" if v=="UK" else "🇩🇪"}</span>{v}</span>'
        if i==5: return f'<span class=tag>{html.escape(str(v))}</span>'
        if i==6: return f'<span class="tag a">{html.escape(str(v))}</span>'
        if i==32: return f'<span class="c {"p" if v=="Promoted" else "np"}">{v}</span>'
        if i==17:
            cl='so' if v==0 else ('sl' if v<5 else ''); return f'<span class="st {cl}">{v:,}</span>'
        if i==27: cl='g' if v>=2 else ('m' if v<0.8 else ''); return f'<span class="pc {cl}">{v:.2f}%</span>'
        if i==28: cl='g' if v>=3 else ('m' if v<1 else ''); return f'<span class="pc {cl}">{v:.2f}%</span>'
        if i==20:
            p=min(100,v/maxRev*100); return f'<span class=db><i class="bf r" style="width:{p:.1f}%"></i><b>{cur}{v:,.2f}</b></span>'
        if i==18:
            p=min(100,v/maxUnits*100); return f'<span class=db><i class="bf u" style="width:{p:.1f}%"></i><b>{v:,}</b></span>'
        if i in MONEY: return f'{cur}{v:,.2f}'
        if i in PCT: return f'{v:.2f}%'
        if i in NUM: return f'{v:,}'
        return html.escape(str(v))

    cols="".join(f'<col style="width:{w}px">' for w in W)
    th="".join(f'<th class="{"l" if i in LEFT else "r"}{" g" if i in GDIV else ""}{" s0" if i==0 else " s1" if i==1 else ""}">{html.escape(h)}</th>' for i,h in enumerate(HEADERS))
    body=[]
    for r in recs:
        v=r["v"]; cur=r["c"]
        tds="".join(f'<td>{cell(v[i],i,cur)}</td>' for i in range(len(HEADERS)))
        body.append("<tr>"+tds+"</tr>")
    # column alignment / dividers / frozen columns driven by CSS nth-child (no per-cell classes -> smaller file)
    left_css=",".join(f'td:nth-child({i+1})' for i in sorted(LEFT))
    gdiv_css=",".join(f'td:nth-child({i+1})' for i in sorted(GDIV))

    doc=f"""<!doctype html><html><head><meta charset=utf-8><title>eBay Product Performance — REQ-19-D01</title>
<style>
:root{{--ink:#101a2c;--ink2:#3d4a60;--muted:#8592a6;--line:#e9eef6;--accent:#3b6ef6;--accent2:#8b5cf6;
--good:#16a34a;--warn:#d97706;--bad:#dc2626;--muted2:#b8c2d2;--rowh:40px}}
*{{box-sizing:border-box}}body{{margin:0;font:12px/1.4 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:var(--ink);
background:radial-gradient(1000px 500px at 12% -8%,#e7eefc,transparent 60%),linear-gradient(180deg,#eef3fb,#f7f9fd)}}
.wrap{{padding:14px}}
.top{{display:flex;align-items:center;gap:13px;margin-bottom:12px}}
.logo{{position:relative;width:38px;height:38px;border-radius:12px;overflow:hidden;display:grid;place-items:center;color:#fff;
font-weight:850;font-size:14px;background:linear-gradient(135deg,var(--accent),var(--accent2));box-shadow:0 10px 26px rgba(59,110,246,.42);animation:pop .6s cubic-bezier(.2,.8,.2,1)}}
.logo::after{{content:"";position:absolute;top:0;left:-70%;width:45%;height:100%;transform:skewX(-20deg);background:linear-gradient(90deg,transparent,rgba(255,255,255,.55),transparent);animation:shine 3.8s ease-in-out infinite 1s}}
h1{{font-size:16px;margin:0;font-weight:800;letter-spacing:-.2px;background:linear-gradient(115deg,#101a2c,#3b6ef6 55%,#8b5cf6);-webkit-background-clip:text;background-clip:text;color:transparent}}
.sub{{color:var(--muted);font-size:11px;margin-top:2px}}
.kpis{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:12px}}
.k{{--c:#3b6ef6;--bg:#eaf1ff;--glow:rgba(59,110,246,.22);position:relative;overflow:hidden;padding:10px 14px 11px;border-radius:18px;
background:linear-gradient(165deg,#fff,#fbfcff);border:1px solid var(--line);box-shadow:0 1px 2px rgba(16,26,44,.05),0 10px 26px rgba(16,26,44,.06);
opacity:0;transform:translateY(12px);animation:rise .6s cubic-bezier(.22,.7,.2,1) forwards}}
.k::before{{content:"";position:absolute;right:-34px;top:-34px;width:120px;height:120px;border-radius:50%;background:radial-gradient(circle,var(--glow),transparent 68%);opacity:.75}}
.kh{{display:flex;align-items:center;gap:9px}}
.ki{{width:27px;height:27px;border-radius:9px;display:grid;place-items:center;background:var(--bg);color:var(--c)}}
.ki svg{{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}
.kl{{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.6px;font-weight:750}}
.kv{{font-size:21px;font-weight:820;margin-top:5px;letter-spacing:-.5px;color:var(--ink)}}
.ks{{color:var(--muted);font-size:10px;margin-top:5px;font-weight:600}}
.k .bar{{height:5px;border-radius:999px;background:var(--bg);margin-top:6px;overflow:hidden}}
.k .bar>i{{display:block;height:100%;border-radius:999px;background:var(--c)}}
.tbl{{background:#fff;border:1px solid var(--line);border-radius:16px;overflow:auto;box-shadow:0 2px 6px rgba(16,26,44,.06),0 14px 34px rgba(16,26,44,.07)}}
table{{border-collapse:separate;border-spacing:0;width:100%;table-layout:fixed;font-variant-numeric:tabular-nums}}
thead th{{position:sticky;top:0;z-index:3;background:#f6f9fe;color:var(--ink2);font-size:10px;text-transform:uppercase;letter-spacing:.3px;
font-weight:750;padding:7px 9px;height:48px;border-bottom:1.5px solid var(--line);line-height:1.16;vertical-align:middle;overflow:hidden}}
th.l{{text-align:left}}th.r{{text-align:right}}
td{{padding:0 9px;height:var(--rowh);border-bottom:1px solid #f0f4fa;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:right;background:#fff}}
{left_css}{{text-align:left}}
tr:nth-child(even) td{{background:#fbfcff}}
{gdiv_css}{{border-left:2px solid #e4eaf4}}th.g{{border-left:2px solid #dbe4f1}}
th.s0,td:nth-child(1){{position:sticky;left:0;z-index:2;box-shadow:9px 0 12px -9px rgba(16,26,44,.14)}}
th.s1,td:nth-child(2){{position:sticky;left:62px;z-index:2}}
thead th.s0,thead th.s1{{z-index:4;background:#f6f9fe}}
img.t{{width:32px;height:32px;object-fit:cover;border-radius:8px;border:1px solid var(--line);vertical-align:middle}}
.nd{{color:var(--muted2);font-style:italic;font-size:11px}}.z{{color:#c9d2e0}}
.m{{padding:2px 8px;border-radius:7px;font-size:10.5px;font-weight:750}}.m.UK{{background:rgba(59,110,246,.12);color:var(--accent)}}.m.Germany{{background:rgba(139,92,246,.14);color:var(--accent2)}}.fl{{margin-right:4px}}
.tag{{display:inline-block;max-width:100%;padding:2px 8px;border-radius:7px;background:#eef2f9;color:var(--ink2);font-size:11px;font-weight:600;overflow:hidden;text-overflow:ellipsis;vertical-align:middle}}.tag.a{{background:#f0edfb;color:#5f4fb0}}
.c{{padding:3px 10px;border-radius:999px;font-size:11px;font-weight:650}}.c.p{{background:rgba(22,163,74,.12);color:var(--good)}}.c.np{{background:rgba(133,146,166,.14);color:var(--muted)}}
.st{{font-weight:650}}.st.so{{color:var(--bad)}}.st.sl{{color:var(--warn)}}.st.so::before,.st.sl::before{{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;margin-right:5px;vertical-align:middle}}.st.so::before{{background:var(--bad)}}.st.sl::before{{background:var(--warn)}}
.pc.g{{color:var(--good);font-weight:650}}.pc.m{{color:var(--muted2)}}
.db{{position:relative;display:flex;align-items:center;justify-content:flex-end;height:100%}}
.bf{{position:absolute;right:0;top:50%;transform:translateY(-50%);height:20px;border-radius:5px;z-index:0}}
.bf.r{{background:linear-gradient(90deg,rgba(59,110,246,.04),rgba(59,110,246,.28))}}.bf.u{{background:linear-gradient(90deg,rgba(14,165,164,.04),rgba(14,165,164,.26))}}
.db b{{position:relative;z-index:1;font-weight:600}}
.foot{{color:var(--muted);font-size:10.5px;margin-top:8px}}
@keyframes rise{{to{{opacity:1;transform:none}}}}@keyframes pop{{from{{transform:scale(.5);opacity:0}}to{{transform:scale(1);opacity:1}}}}@keyframes shine{{0%,55%{{left:-70%}}100%{{left:140%}}}}
</style></head><body><div class=wrap>
<div class=top><div class=logo>eP</div><div><h1>eBay Product Performance Analysis</h1>
<div class=sub>REQ-19-D01 · {n:,} live eBay listings · UK + Germany · window {d0} → {anchor} · money per marketplace currency (UK £ / DE €)</div></div></div>
<div class=kpis>{kpi_html}</div>
<div class=tbl><table><colgroup>{cols}</colgroup><thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody></table></div>
<div class=foot>Source: raw ledsone (all columns) + warehouse (organic traffic only). <b>⚠ ESTIMATE:</b> Cost Price = 20% of selling price (no real COGS exists); Gross/Net Profit &amp; Margin are derived from it and are estimates. <b>NO DATA</b> only: Watch Count (eBay API), Sales Trend (undefined). "–" = zero. Money never blended across currencies.</div>
</div></body></html>"""
    with open(OUT,"w",encoding="utf-8") as f: f.write(doc)
    print("rows:",n,"| rich static HTML:",round(os.path.getsize(OUT)/1e6,2),"MB ->",OUT)

if __name__=="__main__":
    render()
