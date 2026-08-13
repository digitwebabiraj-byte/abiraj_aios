# -*- coding: utf-8 -*-
"""
ESNM -> standard merge file (read-only). FULL column set (all 20), matching the
original ESNM table exactly. Decodes ESNM's raw row slots + dict lookups.
Reads ESNM's finished output only; does not touch the ESNM task.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", "..", "projects"))
SRC = os.path.join(BASE, r"PRJ-2026-014_ebay-slow-no-moving-products\evidence\final_outputs\REQ-16_ebay-slow-no-moving-products\esnm_d01_data.json")
OUT = os.path.join(HERE, "esnm_merge.json")

d = json.load(open(SRC, encoding="utf-8"))
dic = d["dicts"]

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None
def clean(s):
    return "" if s is None else str(s).replace("�", "").strip()
def dref(tbl, i):
    try: return clean(dic[tbl][int(i)])
    except (KeyError, ValueError, IndexError, TypeError): return ""

# (raw slot, lookup-dict or None, key, name, role, type) — full 20, original order
SPEC = [
    (0,  None,      "image",    "Product Image",   "id",     "img"),
    (1,  "account", "account",  "Account",         "id",     "text"),
    (2,  "brand",   "brand",    "Brand",           "id",     "text"),
    (3,  None,      "sku",      "SKU",             "id",     "text"),
    (4,  None,      "item_id",  "eBay Item ID",    "id",     "text"),
    (5,  None,      "title",    "Product Title",   "id",     "text"),
    (6,  "category","category", "Category",        "id",     "text"),
    (7,  None,      "price",    "Current Price",   "metric", "money"),
    (9,  None,      "stock",    "Stock",           "metric", "num"),
    (10, None,      "s_7d",     "7d Sales",        "metric", "num"),
    (11, None,      "s_30",     "30d Sales",       "metric", "num"),
    (12, None,      "s_90",     "90d Sales",       "metric", "num"),
    (26, None,      "s_ly30",   "LY 30d",          "metric", "num"),
    (13, None,      "s_ly90",   "LY 90d",          "metric", "num"),
    (14, None,      "s_trend",  "Sales Trend",     "metric", "text"),
    (15, None,      "s_days",   "Days Since Sale", "metric", "num"),
    (16, None,      "s_views",  "Views 30d",       "metric", "num"),
    (18, None,      "s_conv",   "Conv Rate",       "metric", "pct"),
    (19, "status",  "s_status", "Listing Status",  "metric", "text"),
    (20, "action",  "s_action", "Action Required", "metric", "text"),
]
COLUMNS = [{"key": k, "name": n, "role": r, "type": t} for (_s, _d, k, n, r, t) in SPEC]

rows = []
for raw in d["rows"]:
    item = clean(raw[4])
    if not item:
        continue
    row = {}
    for (slot, lut, k, _n, _r, t) in SPEC:
        val = raw[slot] if slot < len(raw) else None
        if lut:
            row[k] = dref(lut, val)
        elif t in ("num", "money", "pct"):
            row[k] = num(val)
        elif t == "img":
            row[k] = val
        else:
            row[k] = clean(val) if val not in (None, "") else ""
    rows.append(row)

out = {"task": "ESNM", "label": "Slow / No-Moving", "owner": "Thinesh",
       "join_key": "item_id", "as_of": d.get("anchor", ""),
       "columns": COLUMNS, "rows": rows}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", OUT)
print("task ESNM |", len(rows), "rows |", len(COLUMNS), "columns (full) | as_of", out["as_of"])
