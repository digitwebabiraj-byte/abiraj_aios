"""
build_chop_d01.py — REQ-24-D01 Channel Opportunity report (chop / PRJ-2026-021).

One generator module (the one-fetch-path rule). Reads a governed JSON snapshot of per-base-SKU
units-by-channel (Germany, rolling 90 days, Completed) pulled READ-ONLY from the curated warehouse
`public.order_transaction` via the AIOS knowledge-base MCP (docs.ledsone.co.uk), classifies each SKU's
cross-channel Opportunity + Action on the DOCUMENTED DEFAULT rules below (owner-pending: Mahima), and
renders the Excel deliverable.

Metric = UNITS (cross-channel comparable; avoids the DST currency trap). Grain = one row per internal
base SKU (order_transaction.sku is platform-independent; summing by sku already consolidates eBay
item_id sprawl). Money is deliberately NOT used for the comparison.

DEFAULT classification rules (Notes tab documents these; Mahima confirms before sign-off):
  Let sh/am/eb = 90-day units per channel, total = sh+am+eb, leader = max(sh,am,eb).
  Only SKUs with leader >= FLOOR(10) are considered (a real seller, not 1-off noise).
  * Missing channel   — at least one channel == 0 units. Action: "Create <missing channel(s)> listing".
  * Shopify winner    — all 3 > 0, Shopify is the top channel AND Shopify >= 50% of total.
                        Action: "Improve Amazon/eBay listing".
  * Marketplace winner— all 3 > 0, (Amazon+eBay) >= 60% of total AND Shopify <= 20% of total.
                        Action: "Add Shopify promotion".
  * Balanced          — everything else; NOT an opportunity, excluded from the table.
"""
import ast, json, os, re, sys
from datetime import date
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "chop_payload_2026-08-05.json")
RAW  = sys.argv[1] if len(sys.argv) > 1 else None
OUT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "evidence", "final_outputs",
                                       "REQ-24_channel-opportunity"))
OUT_XLSX = os.path.join(OUT_DIR, "REQ-24-D01_channel_opportunity.xlsx")
OUT_HTML = os.path.join(OUT_DIR, "REQ-24-D01_channel_opportunity.html")

FLOOR = 10
WINDOW_DAYS = 90
DATA_THROUGH = "2026-08-04"
MARKET = "Germany"


def load_snapshot():
    """Build the governed JSON snapshot from the raw mcp.ledsone result file (once), else read snapshot.

    Accepts the raw Postgres-MCP export {"data": {"rows": [...]}} — the per-base-SKU units-by-channel
    pivot pulled from order_management (Germany, Completed, 90d, clean-SKU = strip -IDE)."""
    if RAW and os.path.exists(RAW):
        outer = json.loads(open(RAW, "r", encoding="utf-8").read())
        rows = outer["data"]["rows"] if "data" in outer else ast.literal_eval(
            re.sub(r"Decimal\('(-?\d+(?:\.\d+)?)'\)", r"\1", outer["result"][0]["text"]))
        clean = [{"sku": r["sku"],
                  "shopify_u": int(r["shopify_u"]),
                  "amazon_u": int(r["amazon_u"]),
                  "ebay_u": int(r["ebay_u"]),
                  "total_u": int(r["total_u"])} for r in rows]
        json.dump({"generated": DATA_THROUGH, "market": MARKET, "window_days": WINDOW_DAYS,
                   "metric": "units", "source": "raw mcp.ledsone order_management (clean-SKU: strip -IDE)",
                   "rows": clean}, open(SNAP, "w", encoding="utf-8"), indent=1)
        return clean
    return json.load(open(SNAP, "r", encoding="utf-8"))["rows"]


def classify(sh, am, eb):
    total = sh + am + eb
    leader = max(sh, am, eb)
    if leader < FLOOR:
        return None, None
    missing = [name for name, v in (("Shopify", sh), ("Amazon", am), ("eBay", eb)) if v == 0]
    if missing:
        return "Missing channel", "Create " + " + ".join(missing) + " listing"
    # all three > 0
    if sh == leader and sh >= 0.50 * total:
        weak = [name for name, v in (("Amazon", am), ("eBay", eb)) if v < 0.30 * leader]
        tgt = "/".join(weak) if weak else "Amazon/eBay"
        return "Shopify winner", f"Improve {tgt} listing"
    if (am + eb) >= 0.60 * total and sh <= 0.20 * total:
        return "Marketplace winner", "Add Shopify promotion"
    return None, None  # Balanced — not an opportunity


def build():
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    rows = load_snapshot()
    opps = []
    for r in rows:
        sh, am, eb = r["shopify_u"], r["amazon_u"], r["ebay_u"]
        cls, act = classify(sh, am, eb)
        if cls is None:
            continue
        opps.append({**r, "opportunity": cls, "action": act})
    opps.sort(key=lambda x: (x["opportunity"], -x["total_u"]))

    os.makedirs(OUT_DIR, exist_ok=True)
    wb = openpyxl.Workbook()

    # ---- Notes & Method tab ----
    nt = wb.active
    nt.title = "Notes & Method"
    FONT = "Arial"
    notes = [
        ("REQ-24-D01 — Channel Opportunity (chop / PRJ-2026-021)", True, 14),
        ("", False, 11),
        ("What: for each product (internal base SKU), units sold laid side by side across Shopify, "
         "Amazon and eBay — to surface products that sell well in one channel but are weak or MISSING "
         "in others, so the listing gap can be closed.", False, 11),
        (f"Scope: market = {MARKET}; channels = Shopify / Amazon / eBay; order_status = Completed.", False, 11),
        (f"Window: rolling {WINDOW_DAYS} days, data through {DATA_THROUGH} (last complete day).", False, 11),
        ("Metric: UNITS (SUM(quantity)). Units are used — not revenue — because the three channels are "
         "compared side by side and marketplace revenue is in each marketplace's own currency (no FX "
         "table; the DST currency rule). Revenue can be added if Mahima prefers.", False, 11),
        ("Grain: one row per internal base SKU (order_transaction.sku is platform-independent; summing "
         "by SKU already consolidates eBay item_id sprawl).", False, 11),
        ("Source: RAW ledsone Postgres DB via the mcp.ledsone.co.uk MCP, READ-ONLY — order_management "
         "(orders + order_item_info + sub_source + source). Germany = market_place '10'; channels via "
         "source.source_name; units = order_item_info.item_quantity. Query patterns per the AIOS "
         "knowledge-base (docs.ledsone.co.uk) text-to-sql-multi skill.", False, 11),
        ("Clean-SKU step (mandatory): base SKU = resolved inventory SKU (order_item_info.real_sku, else "
         "item_sku) with the listing suffix '-IDE' stripped, so a product's Shopify/Amazon/eBay listings "
         "roll up to one row (proven: LDMST64E274 = LDMST64E274-IDE + LDMST64E274). Multi-packs (2PK…) and "
         "combos (SKUs containing '+') are distinct products and kept separate.", False, 11),
        ("", False, 11),
        ("Opportunity classes + Action (DEFAULT rules — pending Mahima's confirmation):", True, 12),
        (f"  Only SKUs whose top channel sold >= {FLOOR} units in the window are flagged (real sellers).", False, 11),
        ("  Missing channel  — at least one channel sold 0 units. Action: Create the missing listing(s). "
         "The clearest opportunity: proven demand, zero coverage somewhere.", False, 11),
        ("  Shopify winner   — all three channels > 0, Shopify is the top channel AND >= 50% of total "
         "units. Action: Improve Amazon/eBay listing (the weak marketplace).", False, 11),
        ("  Marketplace winner — all three > 0, Amazon+eBay >= 60% of total AND Shopify <= 20% of total. "
         "Action: Add Shopify promotion.", False, 11),
        ("  (SKUs selling evenly across all channels are 'balanced' — not an opportunity — and excluded.)", False, 11),
        ("", False, 11),
        ("These thresholds are documented DEFAULTS, not final. Trend/threshold sign-off is owner-pending "
         "(Mahima). No number below is a sample from the source mock-up — every figure is live warehouse data.", False, 11),
    ]
    r = 1
    for txt, bold, size in notes:
        c = nt.cell(row=r, column=1, value=txt)
        c.font = Font(name=FONT, bold=bold, size=size)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        r += 1
    nt.column_dimensions["A"].width = 118

    # ---- Channel Opportunity tab ----
    ws = wb.create_sheet("Channel Opportunity")
    headers = ["SKU", "Shopify Sales", "Amazon Sales", "eBay Sales",
               "Total Units", "Opportunity", "Action"]
    hdr_fill = PatternFill("solid", fgColor="1F4E5F")
    hdr_font = Font(name=FONT, bold=True, color="FFFFFF", size=11)
    thin = Side(style="thin", color="D9D9D9")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    cls_fill = {"Missing channel": "FCE4D6", "Shopify winner": "E2EFDA", "Marketplace winner": "DDEBF7"}

    ws.append(headers)
    for ci, _ in enumerate(headers, 1):
        c = ws.cell(row=1, column=ci)
        c.fill = hdr_fill; c.font = hdr_font; c.border = border
        c.alignment = Alignment(horizontal="center", vertical="center")

    for o in opps:
        ws.append([o["sku"], o["shopify_u"], o["amazon_u"], o["ebay_u"],
                   o["total_u"], o["opportunity"], o["action"]])
        rr = ws.max_row
        fill = cls_fill.get(o["opportunity"])
        for ci in range(1, len(headers) + 1):
            cell = ws.cell(row=rr, column=ci)
            cell.font = Font(name=FONT, size=10)
            cell.border = border
            if ci in (2, 3, 4, 5):
                cell.alignment = Alignment(horizontal="center")
            if fill:
                cell.fill = PatternFill("solid", fgColor=fill)

    widths = [30, 13, 13, 11, 12, 18, 32]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:G{ws.max_row}"

    wb.save(OUT_XLSX)
    total_base = len(rows)
    write_dashboard(opps, total_base)

    # ---- console summary ----
    from collections import Counter
    cnt = Counter(o["opportunity"] for o in opps)
    print("saved:", OUT_XLSX)
    print("saved:", OUT_HTML)
    print("total opportunity rows:", len(opps), "/ base SKUs:", total_base)
    for k in ("Missing channel", "Shopify winner", "Marketplace winner"):
        print(f"  {k}: {cnt.get(k,0)}")


def write_dashboard(opps, total_base):
    """Self-contained interactive HTML dashboard (full-screen, light theme)."""
    data = json.dumps([{"s": o["sku"], "sh": o["shopify_u"], "am": o["amazon_u"],
                        "eb": o["ebay_u"], "t": o["total_u"], "o": o["opportunity"],
                        "a": o["action"]} for o in sorted(opps, key=lambda x: -x["total_u"])])
    from collections import Counter
    c = Counter(o["opportunity"] for o in opps)
    html = _HTML.replace("__DATA__", data) \
               .replace("__TOTAL__", str(len(opps))).replace("__BASE__", f"{total_base:,}") \
               .replace("__MISS__", str(c.get("Missing channel", 0))) \
               .replace("__MKT__", str(c.get("Marketplace winner", 0))) \
               .replace("__SHOP__", str(c.get("Shopify winner", 0))) \
               .replace("__THROUGH__", DATA_THROUGH).replace("__WINDOW__", str(WINDOW_DAYS)) \
               .replace("__MARKET__", MARKET)
    open(OUT_HTML, "w", encoding="utf-8").write(html)


_HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Channel Opportunity — REQ-24-D01</title>
<style>
:root{
  --bg:#eef3f8; --panel:#ffffff; --ink:#0f2233; --muted:#5b7085; --line:#e2e9f0;
  --accent:#0ea5a4; --accent2:#0891b2;
  --miss:#f59e0b; --miss-bg:#fef3e2; --mkt:#2563eb; --mkt-bg:#e8eefe; --shop:#16a34a; --shop-bg:#e7f6ec;
  --sh:#16a34a; --am:#f59e0b; --eb:#2563eb;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--ink);font:14px/1.45 -apple-system,Segoe UI,Roboto,Arial,sans-serif}
.wrap{max-width:1500px;margin:0 auto;padding:22px 26px 60px}
header{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:18px}
h1{margin:0;font-size:24px;letter-spacing:-.3px}
h1 .tag{background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--muted);font-size:13px;margin-top:4px}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:18px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px 18px;box-shadow:0 1px 2px rgba(15,34,51,.04)}
.kpi .n{font-size:30px;font-weight:700;letter-spacing:-.5px}
.kpi .l{color:var(--muted);font-size:12px;margin-top:2px;text-transform:uppercase;letter-spacing:.4px}
.kpi.b-miss{border-top:3px solid var(--miss)} .kpi.b-mkt{border-top:3px solid var(--mkt)}
.kpi.b-shop{border-top:3px solid var(--shop)} .kpi.b-acc{border-top:3px solid var(--accent)}
.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:14px}
.chip{border:1px solid var(--line);background:var(--panel);color:var(--muted);border-radius:999px;
  padding:7px 14px;font-size:13px;cursor:pointer;font-weight:600;transition:.15s}
.chip:hover{border-color:var(--accent)}
.chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.chip.on.miss{background:var(--miss);border-color:var(--miss)}
.chip.on.mkt{background:var(--mkt);border-color:var(--mkt)}
.chip.on.shop{background:var(--shop);border-color:var(--shop)}
.search{margin-left:auto;flex:1;min-width:200px;max-width:340px}
.search input{width:100%;padding:9px 13px;border:1px solid var(--line);border-radius:10px;font-size:14px;background:var(--panel)}
.search input:focus{outline:2px solid var(--accent);border-color:transparent}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden;box-shadow:0 1px 3px rgba(15,34,51,.05)}
.scroll{overflow:auto;max-height:calc(100vh - 320px)}
table{width:100%;border-collapse:collapse;font-size:13.5px}
thead th{position:sticky;top:0;background:#f3f7fb;border-bottom:2px solid var(--line);
  text-align:left;padding:11px 14px;font-size:12px;letter-spacing:.4px;color:var(--muted);text-transform:uppercase;cursor:pointer;white-space:nowrap}
thead th.num{text-align:right} thead th:hover{color:var(--accent)}
tbody td{padding:10px 14px;border-bottom:1px solid #eef2f6}
tbody tr:hover{background:#f7fbfc}
td.sku{font-family:ui-monospace,Menlo,Consolas,monospace;font-weight:600}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.bar{display:inline-block;height:8px;border-radius:4px;vertical-align:middle;margin-right:7px}
.z{color:#c2cede} .sh-c{color:var(--sh);font-weight:600} .am-c{color:var(--am);font-weight:600} .eb-c{color:var(--eb);font-weight:600}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap}
.badge.miss{background:var(--miss-bg);color:#b45309} .badge.mkt{background:var(--mkt-bg);color:#1d4ed8} .badge.shop{background:var(--shop-bg);color:#15803d}
td.action{color:var(--muted)}
.count{color:var(--muted);font-size:12.5px;margin:10px 2px 0}
footer{color:var(--muted);font-size:12px;margin-top:16px;line-height:1.6}
@media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}}
</style></head><body>
<div class="wrap">
  <header>
    <div>
      <h1>Channel <span class="tag">Opportunity</span></h1>
      <div class="sub">Products selling well in one channel but weak or missing in others · __MARKET__ · units · rolling __WINDOW__ days · data through __THROUGH__ · source: raw ledsone (order_management)</div>
    </div>
  </header>
  <div class="kpis">
    <div class="kpi b-acc"><div class="n">__TOTAL__</div><div class="l">Opportunities</div></div>
    <div class="kpi b-miss"><div class="n">__MISS__</div><div class="l">Missing channel</div></div>
    <div class="kpi b-mkt"><div class="n">__MKT__</div><div class="l">Marketplace winner</div></div>
    <div class="kpi b-shop"><div class="n">__SHOP__</div><div class="l">Shopify winner</div></div>
    <div class="kpi"><div class="n">__BASE__</div><div class="l">Base SKUs scanned</div></div>
  </div>
  <div class="toolbar">
    <span class="chip on" data-f="all" onclick="setF(this,'all')">All</span>
    <span class="chip miss" data-f="Missing channel" onclick="setF(this,'Missing channel')">Missing channel</span>
    <span class="chip mkt" data-f="Marketplace winner" onclick="setF(this,'Marketplace winner')">Marketplace winner</span>
    <span class="chip shop" data-f="Shopify winner" onclick="setF(this,'Shopify winner')">Shopify winner</span>
    <div class="search"><input id="q" placeholder="Search SKU or action…" oninput="render()"></div>
  </div>
  <div class="count" id="count"></div>
  <div class="panel"><div class="scroll"><table>
    <thead><tr>
      <th onclick="sortBy('s')">SKU</th>
      <th class="num" onclick="sortBy('sh')">Shopify</th>
      <th class="num" onclick="sortBy('am')">Amazon</th>
      <th class="num" onclick="sortBy('eb')">eBay</th>
      <th class="num" onclick="sortBy('t')">Total</th>
      <th onclick="sortBy('o')">Opportunity</th>
      <th onclick="sortBy('a')">Action</th>
    </tr></thead>
    <tbody id="tb"></tbody>
  </table></div></div>
  <footer>
    <b>Method (documented defaults — owner-locked, pending Mahima review):</b>
    one row per clean base SKU (strip <code>-IDE</code> suffix); a SKU is flagged only if its top channel sold ≥10 units.
    <b>Missing channel</b> = 0 units in ≥1 channel · <b>Shopify winner</b> = Shopify ≥50% of units ·
    <b>Marketplace winner</b> = Amazon+eBay ≥60% and Shopify ≤20%. Read-only; every figure traces to the live database. REQ-24-D01.
  </footer>
</div>
<script>
const DATA=__DATA__;
let filt='all', sortK='t', sortDir=-1;
const cls={'Missing channel':'miss','Marketplace winner':'mkt','Shopify winner':'shop'};
const MAX=Math.max(...DATA.map(d=>Math.max(d.sh,d.am,d.eb)),1);
function setF(el,f){filt=f;document.querySelectorAll('.chip').forEach(c=>c.classList.remove('on'));el.classList.add('on');render();}
function sortBy(k){if(sortK===k)sortDir*=-1;else{sortK=k;sortDir=(k==='s'||k==='o'||k==='a')?1:-1;}render();}
function cell(v,klass){if(!v)return '<td class="num z">0</td>';
  const w=Math.max(4,Math.round(v/MAX*46));
  return `<td class="num"><span class="bar" style="width:${w}px;background:var(--${klass})"></span><span class="${klass}-c">${v}</span></td>`;}
function render(){
  const q=document.getElementById('q').value.trim().toLowerCase();
  let rows=DATA.filter(d=>(filt==='all'||d.o===filt)&&(!q||d.s.toLowerCase().includes(q)||d.a.toLowerCase().includes(q)));
  rows.sort((a,b)=>{let x=a[sortK],y=b[sortK];if(typeof x==='string')return x.localeCompare(y)*sortDir;return (x-y)*sortDir;});
  document.getElementById('count').textContent=`${rows.length} of ${DATA.length} opportunities`;
  document.getElementById('tb').innerHTML=rows.map(d=>{const k=cls[d.o];
    return `<tr><td class="sku">${d.s}</td>${cell(d.sh,'sh')}${cell(d.am,'am')}${cell(d.eb,'eb')}`
      +`<td class="num"><b>${d.t}</b></td>`
      +`<td><span class="badge ${k}">${d.o}</span></td><td class="action">${d.a}</td></tr>`;}).join('');
}
render();
</script>
</body></html>"""


if __name__ == "__main__":
    build()
