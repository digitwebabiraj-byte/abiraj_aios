# -*- coding: utf-8 -*-
"""
EPPR -> standard merge file (read-only). FULL column set (all 34), matching the
original EPPR table exactly, in the original order. Reads EPPR's finished output only.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", "..", "projects"))
SRC = os.environ.get("EPPR_SRC") or os.path.join(BASE, r"PRJ-2026-016_ebay-product-performance-analysis\evidence\final_outputs\REQ-19_ebay-product-performance-analysis\eppr_d01_data.json")
OUT = os.path.join(HERE, "eppr_merge.json")

d = json.load(open(SRC, encoding="utf-8"))
win = d.get("window", ["", ""])

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None
def clean(s):
    return "" if s is None else str(s).replace("�", "").strip()

# (v-index, key, name, role, type) — full 34, original order
SPEC = [
    (0,  "image",     "Product Image",  "id",     "img"),
    (1,  "sku",       "SKU",            "id",     "text"),
    (2,  "parent_sku","Parent SKU",     "id",     "text"),
    (3,  "item_id",   "eBay Item ID",   "id",     "text"),
    (4,  "title",     "Product Title",  "id",     "text"),
    (5,  "brand",     "Brand",          "id",     "text"),
    (6,  "category",  "Category",       "id",     "text"),
    (7,  "market",    "Marketplace",    "id",     "text"),
    (8,  "account",   "Account",        "id",     "text"),
    (9,  "list_date", "Listing Date",   "metric", "text"),
    (10, "status",    "Listing Status", "metric", "text"),
    (11, "price",     "Selling Price",  "metric", "money"),
    (12, "cost",      "Cost Price",     "metric", "money"),
    (13, "ship",      "Shipping Cost",  "metric", "money"),
    (14, "fees",      "eBay Fees",      "metric", "money"),
    (15, "adcost",    "Ad Cost",        "metric", "money"),
    (16, "vat",       "VAT",            "metric", "money"),
    (17, "stock",     "Available Stock","metric", "num"),
    (18, "units",     "Units Sold",     "metric", "num"),
    (19, "orders",    "Orders",         "metric", "num"),
    (20, "revenue",   "Revenue",        "metric", "money"),
    (21, "gross",     "Gross Profit",   "metric", "money"),
    (22, "net",       "Net Profit",     "metric", "money"),
    (23, "margin",    "Profit Margin %","metric", "pct"),
    (24, "impr",      "Impressions",    "metric", "num"),
    (25, "views",     "Views",          "metric", "num"),
    (26, "clicks",    "Clicks",         "metric", "num"),
    (27, "ctr",       "CTR %",          "metric", "pct"),
    (28, "cvr",       "Conversion Rate %","metric","pct"),
    (29, "last_sold", "Last Sold Date", "metric", "text"),
    (30, "days_active","Days Active",   "metric", "num"),
    (31, "promo",     "Promotion Status","metric","text"),
    (32, "ppc_camp",  "PPC Campaign",   "metric", "text"),
    (33, "trend",     "Sales Trend",    "metric", "text"),
]
TYPES = {k: t for (_i, k, _n, _r, t) in SPEC}
COLUMNS = [{"key": k, "name": n, "role": r, "type": t} for (_i, k, n, r, t) in SPEC]

rows = []
for rec in d["records"]:
    v = rec["v"]
    item = clean(v[3])
    if not item:
        continue
    row = {}
    for (i, k, _n, _r, t) in SPEC:
        val = v[i] if i < len(v) else None
        if t in ("num", "money", "pct"):
            row[k] = num(val)
        elif t == "img":
            row[k] = val
        else:
            row[k] = clean(val)
    rows.append(row)

out = {"task": "EPPR", "label": "Product Performance", "owner": "Thinesh",
       "join_key": "item_id", "as_of": win[1] if len(win) > 1 else "",
       "columns": COLUMNS, "rows": rows}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", OUT)
print("task EPPR |", len(rows), "rows |", len(COLUMNS), "columns (full) | as_of", out["as_of"])
