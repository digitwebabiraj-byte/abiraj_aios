#!/usr/bin/env python3
"""
render_epns_portal.py — STATIC-FIRST portal build of the eBay Product Net Sales dashboard.

Unlike render_epns_dashboard.py (which builds the KPIs/table with JavaScript), this renders every
KPI tile and every table row directly into the HTML, so the report is fully visible even when the
portal viewer runs NO JavaScript. JS (search + click-to-sort) is optional enhancement over the DOM.
Layout uses normal document flow (no 100vh lock) so it renders inside the portal iframe.

Usage:
  python -c "import json,render_epns_portal as p; p.render_portal(json.load(open('rows.json'))['data']['rows'],'out.html')"
"""
import os, datetime as dt

CUR_SYM = {"GBP": "£", "EUR": "€", "USD": "$"}
_FONT = os.path.join(os.path.dirname(__file__), "epns_fonts.css")

def _font_css():
    return open(_FONT, encoding="utf-8").read() if os.path.exists(_FONT) else ""

def _f(v):
    try: return float(v)
    except (TypeError, ValueError): return 0.0

def _money(v, c):
    try: return CUR_SYM.get(c, "") + "{:,.2f}".format(float(v))
    except (TypeError, ValueError): return ""

def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))

def summarise(rows):
    by = {}
    for r in rows:
        c = r.get("currency") or "?"
        s = by.setdefault(c, {"orders":0,"gross":0.0,"fvf":0.0,"ppc":0.0,"gen":0.0,"net":0.0})
        s["orders"] += 1
        s["gross"] += _f(r.get("gross_sales")); s["fvf"] += _f(r.get("final_value_fee"))
        s["ppc"]   += _f(r.get("ppc_cost"));    s["gen"] += _f(r.get("general"))
        s["net"]   += _f(r.get("net_sales_nnv"))
    return by

COLS = [
    ("Date","order_date","l"),("Order ID","order_id","l"),("SKU","sku","sku"),
    ("Account","account","l"),("Market","marketplace","pill"),
    ("Gross Sales","gross_sales","m"),("VAT (20%)·est","vat_20","est"),
    ("Promotion","promotion","m"),("Final Value Fee","final_value_fee","fee"),
    ("Product Cost·est","product_cost","est"),("Postage","postage","m"),
    ("PPC Cost","ppc_cost","fee"),("General","general","fee"),
    ("Net Sales (NNV)","net_sales_nnv","net"),("Net Profit·est","net_profit_est","est"),
]

def render_portal(rows, out_path):
    anchor = dt.date.today().isoformat()
    summ = summarise(rows)
    order = sorted(summ.keys(), key=lambda c: -summ[c]["gross"])
    CLS = {"GBP":"gbp","EUR":"eur","USD":"usd"}

    kpis = []
    for c in order:
        s = summ[c]
        feeRate = 100*(s["fvf"]+s["ppc"]+s["gen"])/s["gross"] if s["gross"] else 0
        netRate = 100*s["net"]/s["gross"] if s["gross"] else 0
        kpis.append(
            '<div class="kpi %s"><span class="strip"></span><span class="cchip">%s</span>'
            '<div class="lab">Net Sales &middot; %d orders</div><div class="val">%s</div>'
            '<div class="subx">Gross %s &middot; fees %s (%.1f%%)</div>'
            '<div class="bar"><i style="width:%.1f%%"></i></div></div>'
            % (CLS.get(c,"other"), c, s["orders"], _money(s["net"],c),
               _money(s["gross"],c), _money(s["fvf"]+s["ppc"]+s["gen"],c), feeRate, netRate))

    head = "".join('<th class="%s">%s</th>' % ("l" if k in ("l","sku","pill") else "", _esc(t))
                   for (t,_key,k) in COLS)

    body = []
    for d in rows:
        cur = d.get("currency","")
        cells = []
        for (t,key,k) in COLS:
            v = d.get(key,"")
            if k == "pill":
                m = (d.get("marketplace") or "").lower()
                cls = "uk" if m=="uk" else "de" if m=="germany" else "us" if m=="us" else "other"
                cells.append('<td class="l"><span class="pill %s">%s</span></td>' % (cls, _esc(d.get("marketplace",""))))
            elif k == "sku":
                cells.append('<td class="l"><span class="sku" title="%s">%s</span></td>' % (_esc(v), _esc(v)))
            elif k == "l":
                cells.append('<td class="l">%s</td>' % _esc(v))
            else:
                cls = {"fee":"mono fee","est":"mono est","net":"mono net","m":"mono"}[k]
                cells.append('<td class="%s">%s</td>' % (cls, _money(v,cur)))
        body.append("<tr>" + "".join(cells) + "</tr>")

    html = (TEMPLATE
            .replace("/*__FONTS__*/", _font_css())
            .replace("__ANCHOR__", anchor).replace("__NROWS__", str(len(rows)))
            .replace("<!--KPIS-->", "".join(kpis))
            .replace("<!--HEAD-->", head).replace("<!--BODY-->", "".join(body)))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out_path


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>eBay Product Net Sales - Kobiga - REQ-22-D01</title>
<style>
/*__FONTS__*/
:root{--font:'Manrope',-apple-system,"Segoe UI",Arial,sans-serif;--display:'Sora','Manrope',"Segoe UI",Arial,sans-serif;
--ink:#0f2540;--muted:#6a7a92;--line:#e6ecf5;--accent:#3b6ef6;--warn:#e0532f}
*{box-sizing:border-box}
body{margin:0;font-family:var(--font);color:var(--ink);-webkit-font-smoothing:antialiased;
 background:radial-gradient(1100px 460px at 12% -8%,#e9f0ff 0,transparent 60%),radial-gradient(900px 460px at 100% 0,#f2ecff 0,transparent 55%),#eef2fb}
.wrap{max-width:1760px;margin:0 auto;padding:16px 20px 40px}
h1{font-family:var(--display);font-size:21px;font-weight:800;letter-spacing:-.5px;margin:0 0 4px;
 background:linear-gradient(90deg,#3b6ef6,#7c5cff,#12b26b);-webkit-background-clip:text;background-clip:text;color:transparent}
.lead{color:var(--muted);font-size:11.5px;line-height:1.5;margin:0 0 12px;max-width:980px}
.badge{display:inline-block;background:linear-gradient(135deg,#e7f8f0,#d4f3e4);color:#0e9257;font-weight:800;font-size:11px;padding:3px 10px;border-radius:999px;margin-right:6px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-bottom:14px}
.kpi{position:relative;overflow:hidden;background:rgba(255,255,255,.72);border:1px solid rgba(255,255,255,.8);border-radius:16px;
 padding:12px 15px 13px;box-shadow:0 1px 2px rgba(16,26,44,.05),0 16px 40px -18px rgba(16,26,44,.3)}
.kpi .strip{position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--g1),var(--g2))}
.kpi .lab{font-size:10px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted);font-weight:800}
.kpi .val{font-family:var(--display);font-size:23px;font-weight:800;letter-spacing:-.7px;margin-top:2px;
 background:linear-gradient(120deg,var(--g1),var(--g2));-webkit-background-clip:text;background-clip:text;color:transparent}
.kpi .subx{font-size:10.5px;margin:2px 0 0;color:var(--muted)}
.kpi .cchip{position:absolute;top:10px;right:11px;font-size:10px;font-weight:900;color:#fff;background:linear-gradient(135deg,var(--g1),var(--g2));padding:2px 8px;border-radius:7px}
.kpi .bar{height:6px;border-radius:6px;background:rgba(16,26,44,.07);margin-top:8px;overflow:hidden}.kpi .bar>i{display:block;height:100%;border-radius:6px;background:linear-gradient(90deg,var(--g1),var(--g2))}
.kpi.gbp{--g1:#3b6ef6;--g2:#63b3ff}.kpi.eur{--g1:#7c5cff;--g2:#b07bff}.kpi.usd{--g1:#12b26b;--g2:#4fd68f}.kpi.other{--g1:#5b6b82;--g2:#93a2b8}
.card{background:rgba(255,255,255,.78);border:1px solid rgba(255,255,255,.8);border-radius:16px;overflow:hidden;box-shadow:0 1px 2px rgba(16,26,44,.05),0 22px 56px -26px rgba(16,26,44,.32)}
.ctrls{padding:10px 14px;border-bottom:1px solid var(--line);background:linear-gradient(180deg,#fbfdff,#f6faff);display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.ctrls input{flex:1;min-width:200px;border:1px solid var(--line);border-radius:10px;padding:8px 12px;font-size:13.5px;outline:none}
.ctrls input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(59,110,246,.14)}
.cnt{font-size:12px;color:var(--muted);font-weight:700}
.tw{max-height:74vh;overflow-y:auto;overflow-x:hidden}
table{border-collapse:separate;border-spacing:0;width:100%;table-layout:fixed;font-size:11.5px}
thead th{position:sticky;top:0;z-index:2;background:linear-gradient(180deg,#eef4ff,#e7eeff);text-align:right;padding:8px 7px;font-size:9.5px;
 text-transform:uppercase;letter-spacing:.3px;color:#41527a;font-weight:800;white-space:normal;line-height:1.2;cursor:pointer;box-shadow:inset 0 -1px 0 rgba(59,110,246,.18)}
thead th.l{text-align:left}
/* fixed-layout widths so all 15 columns fit the container (no horizontal scroll) */
th:nth-child(1){width:6%}   /* Date */
th:nth-child(2){width:8%}   /* Order ID */
th:nth-child(3){width:12%}  /* SKU */
th:nth-child(4){width:8%}   /* Account */
th:nth-child(5){width:5%}   /* Market */
tbody td{padding:6px 7px;text-align:right;border-bottom:1px solid #eef3fa;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
tbody td.l{text-align:left}
tbody tr:nth-child(even) td{background:rgba(244,248,255,.5)}
tbody tr:hover td{background:linear-gradient(90deg,rgba(59,110,246,.09),rgba(124,92,255,.05))}
.mono{font-variant-numeric:tabular-nums}.fee{color:var(--warn)}.est{color:#8a79d6}
.net{font-weight:800;color:#0e9257}
.pill{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11px;font-weight:800}
.pill.uk{background:linear-gradient(135deg,#e7efff,#dbe8ff);color:#2b5bd7}.pill.de{background:linear-gradient(135deg,#fff0e4,#ffe6d3);color:#c9631d}.pill.us{background:linear-gradient(135deg,#e6faf0,#d6f6e5);color:#0e9257}.pill.other{background:#eef1f6;color:#5b6b82}
.sku{color:var(--muted);max-width:100%;overflow:hidden;text-overflow:ellipsis;display:inline-block;vertical-align:bottom}
.foot{color:var(--muted);font-size:10.5px;line-height:1.5;margin-top:12px}.foot b{color:var(--ink)}
</style></head>
<body><div class="wrap">
<h1>eBay Product Net Sales</h1>
<p class="lead"><span class="badge">SETTLED ONLY</span>Kobiga - REQ-22-D01 - last 30 days ending __ANCHOR__ - <b>__NROWS__</b> settled orders - ties to eBay (VAT-inclusive fees) - per marketplace currency, never blended.</p>
<div class="kpis"><!--KPIS--></div>
<div class="card">
 <div class="ctrls"><input id="q" type="search" placeholder="Search order ID, SKU or account..."><span class="cnt" id="cnt"></span></div>
 <div class="tw"><table><thead><tr><!--HEAD--></tr></thead><tbody id="tb"><!--BODY--></tbody></table></div>
</div>
<div class="foot"><b>Net Sales (NNV)</b> = Gross - Final Value Fee - PPC - General (eBay net payout; ties to eBay "Total fees incl VAT").
<b>VAT (20%)</b> and <b>Product Cost</b> (20% proxy) are estimates; <b>Net Profit-est</b> = NNV - VAT - Product Cost. Unsettled recent orders are excluded until eBay books their fees.</div>
</div>
<script>
(function(){var tb=document.getElementById('tb'),q=document.getElementById('q'),cnt=document.getElementById('cnt');
var rows=[].slice.call(tb.rows);function upd(){cnt.textContent=rows.filter(function(r){return r.style.display!=='none';}).length.toLocaleString()+' orders';}
upd();
q.addEventListener('input',function(){var s=q.value.toLowerCase();rows.forEach(function(r){r.style.display=r.textContent.toLowerCase().indexOf(s)>-1?'':'none';});upd();});
var ths=document.querySelectorAll('thead th');ths.forEach(function(th,i){var dir=1;th.addEventListener('click',function(){dir*=-1;
 var num=!th.classList.contains('l');rows.slice().sort(function(a,b){var x=a.cells[i].textContent.replace(/[^0-9.\-]/g,''),y=b.cells[i].textContent.replace(/[^0-9.\-]/g,'');
 if(num){return ((parseFloat(x)||0)-(parseFloat(y)||0))*dir;}return a.cells[i].textContent<b.cells[i].textContent?-dir:dir;}).forEach(function(r){tb.appendChild(r);});});});
})();
</script>
</body></html>
"""
