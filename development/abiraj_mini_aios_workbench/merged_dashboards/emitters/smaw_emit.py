# -*- coding: utf-8 -*-
"""
SMAW -> standard merge file (read-only). Reads SMAW's smaw_data_all.json (list of per-SKU dicts).
Env override: SMAW_SRC. Does not touch the SMAW task.
"""
import os, glob, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", "..", "projects"))
SRC = os.environ.get("SMAW_SRC") or glob.glob(os.path.join(BASE, "PRJ-2026-004*", "automation", "smaw_data_all.json"), recursive=True)[0]
OUT = os.path.join(HERE, "smaw_merge.json")

# (source-key, display-name, role, type)
SPEC = [
    ("asin",          "ASIN",                "id",     "text"),
    ("account",       "Account",             "id",     "text"),
    ("listing_sku",   "Listing SKU",         "id",     "text"),
    ("master_sku",    "Correct SKU (Master)","id",     "text"),
    ("amazon_fbm",    "Amazon Qty (FBM)",    "metric", "num"),
    ("uk_warehouse",  "UK Warehouse (Real)", "metric", "num"),
    ("order_count_90","90d Order Count",     "metric", "num"),
    ("velocity",      "Velocity /day",       "metric", "num"),
    ("days_remaining","Days Remaining",      "metric", "num"),
    ("suppliers",     "Upcoming Supplier",   "metric", "text"),
    ("po_qty",        "PO Qty (Incoming)",   "metric", "num"),
    ("containers",    "Container #",         "metric", "text"),
    ("stock_status",  "Stock Status",        "metric", "text"),
]
COLUMNS = [{"key": k, "name": n, "role": r, "type": t} for (k, n, r, t) in SPEC]

def clean(s):
    return "" if s is None else str(s).strip()
def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

data = json.load(open(SRC, encoding="utf-8"))
data = data if isinstance(data, list) else data.get("rows", [])
asof = datetime.date.fromtimestamp(os.path.getmtime(SRC)).isoformat()

rows = []
for r in data:
    sku = clean(r.get("listing_sku"))
    if not sku:
        continue
    row = {}
    for (k, _n, _r, t) in SPEC:
        v = r.get(k)
        row[k] = num(v) if t == "num" else clean(v)
    rows.append(row)

out = {"task": "SMAW", "label": "Stock Check", "owner": "Thuwaraga",
       "join_key": "listing_sku", "as_of": asof, "columns": COLUMNS, "rows": rows}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", OUT)
print("task SMAW |", len(rows), "rows |", len(COLUMNS), "columns | as_of", asof)
