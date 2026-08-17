# -*- coding: utf-8 -*-
"""
T7 -> standard merge file (read-only). Reads T7's data.json (compressed keys + names map).
Env override: T7_SRC. Does not touch the T7 task.
"""
import os, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", "..", "projects"))
SRC = os.environ.get("T7_SRC") or glob.glob(os.path.join(BASE, "PRJ-2026-005*", "evidence", "final_outputs", "**", "data.json"), recursive=True)[0]
OUT = os.path.join(HERE, "t7_merge.json")

d = json.load(open(SRC, encoding="utf-8"))
names = d.get("names", {})
meta = d.get("meta", {})
asof = meta.get("run_date") or meta.get("week_end") or ""

COLUMNS = [
    {"key": "sku",      "name": "SKU",           "role": "id",     "type": "text"},
    {"key": "title",    "name": "Product Name",  "role": "id",     "type": "text"},
    {"key": "ref_id",   "name": "Listing Ref",   "role": "id",     "type": "text"},
    {"key": "platform", "name": "Platform",      "role": "id",     "type": "text"},
    {"key": "account",  "name": "Account",       "role": "id",     "type": "text"},
    {"key": "base_sku", "name": "Base SKU",      "role": "id",     "type": "text"},
    {"key": "mapped",   "name": "Mapped",        "role": "metric", "type": "num"},
    {"key": "orders",   "name": "Orders (week)", "role": "metric", "type": "num"},
]

def clean(s):
    return "" if s is None else str(s).strip()

rows = []
for r in d.get("rows", []):
    sku = clean(r.get("s"))
    if not sku:
        continue
    rows.append({
        "sku": sku, "title": clean(names.get(r.get("s"), "")), "ref_id": clean(r.get("r")),
        "platform": clean(r.get("p")), "account": clean(r.get("a")), "base_sku": clean(r.get("b")),
        "mapped": r.get("m"), "orders": r.get("o"),
    })

out = {"task": "T7", "label": "SKU Performance", "owner": "Thuwaraga",
       "join_key": "sku", "as_of": asof, "columns": COLUMNS, "rows": rows}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", OUT)
print("task T7 |", len(rows), "rows |", len(COLUMNS), "columns | as_of", asof)
