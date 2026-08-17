# -*- coding: utf-8 -*-
"""
T7 -> standard merge file (read-only). Reproduces T7's OWN displayed table exactly:
the product-family tree (purple SKU summary rows + blue listing/ASIN rows) with the
Amz/eBay/B&Q order pivot and the Performing?/Action verdict — same columns, same names,
same grouping/verdict logic as its build_html.build_groups(). Flattened to one table
with a "Type" column (Family / Listing) so it fits the merged dashboard's uniform grid.
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

# ---- exact columns of T7's native table -------------------------------------
COLUMNS = [
    {"key": "sku",      "name": "SKU / ASIN",   "role": "id",     "type": "text"},
    {"key": "type",     "name": "Type",         "role": "id",     "type": "text"},
    {"key": "title",    "name": "Product Name", "role": "id",     "type": "text"},
    {"key": "platform", "name": "Platform",     "role": "id",     "type": "text"},
    {"key": "account",  "name": "Account",      "role": "id",     "type": "text"},
    {"key": "amazon",   "name": "Amz",          "role": "metric", "type": "num"},
    {"key": "ebay",     "name": "eBay",         "role": "metric", "type": "num"},
    {"key": "bq",       "name": "B&Q",          "role": "metric", "type": "num"},
    {"key": "total",    "name": "Total",        "role": "metric", "type": "num"},
    {"key": "perf",     "name": "Performing?",  "role": "id",     "type": "text"},
    {"key": "action",   "name": "Action",       "role": "id",     "type": "text"},
]

PLATFORM_KEY = {"AMAZON": "amazon", "EBAY": "ebay", "B&Q": "bq"}

# pack-size / multipack suffixes — identical to T7's build_html
_PACK_SUFFIXES = (
    ["APK"]
    + [f"{n}PK" for n in range(1, 25)]
    + [f"{n}PCK" for n in range(1, 25)]
    + [f"PCK{n}" for n in range(1, 25)]
    + [f"PACK{n}" for n in range(1, 25)] + [f"{n}PACK" for n in range(1, 25)]
)
_PACK_SUFFIXES.sort(key=len)


def product_family(sku, uni_upper):
    su = sku.upper()
    for suf in _PACK_SUFFIXES:
        if su.endswith(suf) and len(su) > len(suf):
            base = sku[: len(sku) - len(suf)]
            if base and base.upper() in uni_upper:
                return base
    return sku


def clean(s):
    return "" if s is None else str(s).strip()


# ---- reproduce build_groups, then flatten to Family + Listing rows ----------
import collections
uni_upper = {r["s"].upper() for r in d.get("rows", []) if r.get("s")}
groups = collections.OrderedDict()
for r in d.get("rows", []):
    if not r.get("s"):
        continue
    groups.setdefault(product_family(r["s"], uni_upper), []).append(r)

fams = []
for base, listings in groups.items():
    pname = names.get(base, "")
    if not pname:
        for r in listings:
            pname = names.get(r["s"], "") or pname
            if pname:
                break
    y = len(listings)
    x = sum(1 for r in listings if r["o"] > 0)
    plat = {"amazon": 0, "ebay": 0, "bq": 0}
    for r in listings:
        plat[PLATFORM_KEY[r["p"]]] += r["o"]
    total = sum(plat.values())
    if y > 0 and x == y:
        perf = "All performing ✅"
    elif x == 0:
        perf = f"0/{y} performing \U0001f534"
    else:
        perf = f"{x}/{y} performing ⚠️"
    action = "See ASIN rows below ↓" if x < y else "—"
    fams.append({
        "base": base, "name": pname or "—", "x": x, "y": y,
        "amazon": plat["amazon"], "ebay": plat["ebay"], "bq": plat["bq"],
        "total": total, "perf": perf, "action": action, "active": total > 0,
        "listings": listings, "pname": pname,
    })
fams.sort(key=lambda g: (not g["active"], -g["total"], g["base"]))

rows = []
for g in fams:
    # purple family (summary) row
    rows.append({
        "sku": g["base"], "type": "Family", "title": g["name"],
        "platform": "—", "account": "—",
        "amazon": g["amazon"], "ebay": g["ebay"], "bq": g["bq"], "total": g["total"],
        "perf": g["perf"], "action": g["action"],
    })
    # blue listing (detail) rows — same sort as T7 (orders desc, then platform)
    for r in sorted(g["listings"], key=lambda z: (-z["o"], z["p"])):
        pk = PLATFORM_KEY[r["p"]]
        row_orders = {"amazon": 0, "ebay": 0, "bq": 0}
        row_orders[pk] = r["o"]
        performing = r["o"] > 0
        rows.append({
            "sku": clean(r["s"]),
            "type": "Listing",
            "title": clean(names.get(r["s"], "") or g["pname"] or "—"),
            "platform": clean(r["p"]),
            "account": clean(r["a"]) or "—",
            "amazon": row_orders["amazon"], "ebay": row_orders["ebay"],
            "bq": row_orders["bq"], "total": r["o"],
            "perf": "Yes" if performing else "No",
            "action": "—" if performing else "Investigate & fix listing",
        })

out = {"task": "T7", "label": "SKU Performance", "owner": "Thuwaraga",
       "join_key": "sku", "as_of": asof, "columns": COLUMNS, "rows": rows}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", OUT)
print("task T7 |", len(rows), "rows (", len(fams), "families ) |", len(COLUMNS), "columns | as_of", asof)
