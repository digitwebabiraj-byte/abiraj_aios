# -*- coding: utf-8 -*-
"""
ERA -> standard merge file (read-only).
Reads ERA's existing Excel output and writes era_merge.json per MERGE_DATA_SPEC.md.
ERA is per-SKU (no Item ID) — in the independent-tab model that is fine: its tab shows
its OWN rows with its OWN identity (SKU / Title / Account). Sources are never touched.
"""
import json, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", "..", "projects"))
XLSX = glob.glob(os.path.join(BASE, "PRJ-2026-012*", "evidence", "final_outputs", "**", "*.xlsx"), recursive=True)[0]
OUT = os.path.join(HERE, "era_merge.json")

import openpyxl
wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
ws = wb["eBay Return Analysis"]

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def clean(s):
    return "" if s is None else str(s).replace("�", "").replace("�", "").strip()

# find the header row ("SKU","Product Title","Account",...)
grid = list(ws.iter_rows(values_only=True))
hdr_i = next(i for i, r in enumerate(grid) if r and str(r[0]).strip() == "SKU")
data = grid[hdr_i + 1:]

# as_of from the "Last updated: YYYY-MM-DD" preamble, else reporting month
asof = ""
for r in grid[:hdr_i]:
    for c in r:
        m = re.search(r"(20\d\d-\d\d-\d\d)", str(c) if c else "")
        if m: asof = m.group(1)
if not asof: asof = "2026-06-30"

COLUMNS = [
    {"key": "sku",       "name": "SKU",            "role": "id",     "type": "text"},
    {"key": "title",     "name": "Product Title",  "role": "id",     "type": "text"},
    {"key": "account",   "name": "Account",        "role": "id",     "type": "text"},
    {"key": "r_orders",  "name": "Orders",         "role": "metric", "type": "num"},
    {"key": "r_returns", "name": "Returns",        "role": "metric", "type": "num"},
    {"key": "r_rate",    "name": "Return Rate",    "role": "metric", "type": "pct"},
    {"key": "r_lastm",   "name": "Last Month Returns", "role": "metric", "type": "num"},
    {"key": "r_lasty",   "name": "Last Year Returns",  "role": "metric", "type": "num"},
    {"key": "r_refund",  "name": "Refund",         "role": "metric", "type": "money"},
    {"key": "r_cost",    "name": "Return Cost",    "role": "metric", "type": "money"},
    {"key": "r_reason",  "name": "Main Return Reason", "role": "metric", "type": "text"},
    {"key": "r_rank",    "name": "Return Rank",    "role": "metric", "type": "text"},
    {"key": "r_negfb",   "name": "Negative Feedback",  "role": "metric", "type": "num"},
    {"key": "r_open",    "name": "Open Cases",     "role": "metric", "type": "num"},
    {"key": "r_stock",   "name": "Stock",          "role": "metric", "type": "num"},
    {"key": "r_adspend", "name": "Ad Spend",       "role": "metric", "type": "money"},
    {"key": "r_adsales", "name": "Ad Sales",       "role": "metric", "type": "money"},
    {"key": "r_acos",    "name": "ACOS",           "role": "metric", "type": "pct"},
    {"key": "r_roas",    "name": "ROAS",           "role": "metric", "type": "num"},
]

def pct(x):                       # ERA stores rates as fractions (0.2308) -> 23.08%
    v = num(x)
    return None if v is None else round(v * 100, 2)

rows = []
for r in data:
    sku = clean(r[0])
    acct = clean(r[2])
    if not sku or sku.upper().startswith("TOTAL") or "AVG" in sku.upper() or "SKUS" in acct.upper():
        continue   # skip the Excel's TOTAL / AVG summary row
    rows.append({
        "sku": sku, "title": clean(r[1]), "account": clean(r[2]),
        "r_orders": num(r[3]), "r_returns": num(r[4]), "r_rate": pct(r[5]),
        "r_lastm": num(r[6]), "r_lasty": num(r[7]), "r_refund": num(r[8]),
        "r_cost": num(r[9]), "r_reason": clean(r[10]), "r_rank": clean(r[11]),
        "r_negfb": num(r[12]), "r_open": num(r[13]), "r_stock": num(r[14]),
        "r_adspend": num(r[15]), "r_adsales": num(r[16]),
        "r_acos": pct(r[17]), "r_roas": num(r[18]),
    })

out = {
    "task": "ERA", "label": "Return Analysis", "owner": "Thinesh",
    "join_key": "sku", "as_of": asof, "columns": COLUMNS, "rows": rows,
}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", OUT)
print("task ERA |", len(rows), "rows |", len(COLUMNS), "columns | as_of", asof)
