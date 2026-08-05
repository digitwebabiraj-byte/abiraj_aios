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

    # ---- console summary ----
    from collections import Counter
    cnt = Counter(o["opportunity"] for o in opps)
    print("saved:", OUT_XLSX)
    print("total opportunity rows:", len(opps))
    for k in ("Missing channel", "Shopify winner", "Marketplace winner"):
        print(f"  {k}: {cnt.get(k,0)}")
    print("top 8 by total units:")
    for o in sorted(opps, key=lambda x: -x["total_u"])[:8]:
        print(f"  {o['sku']:<16} sh={o['shopify_u']:<4} am={o['amazon_u']:<4} eb={o['ebay_u']:<4} "
              f"tot={o['total_u']:<4} {o['opportunity']:<18} {o['action']}")


if __name__ == "__main__":
    build()
