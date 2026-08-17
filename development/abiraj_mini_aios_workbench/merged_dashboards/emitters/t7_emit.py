# -*- coding: utf-8 -*-
"""
T7 -> standard merge file (read-only). Reproduces T7's OWN signed-off REPORT (build_report.py,
the Table-7 xlsx Thuwaraga receives) EXACTLY: the 13-column layout with the product-family tree
(purple SKU SUMMARY rows + blue listing rows), the [+N SKUs] / [variant] tags, Row Type = SKU
SUMMARY / ref-id, Week Start/End, per-platform Amazon/eBay/B&Q order columns, TOTAL Orders, and
the Performing?/Action-Required verdict — via the same build_groups() logic. Flattened into one
table for the merged grid. Env override: T7_SRC. Does not touch the T7 task.
"""
import os, glob, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", "..", "projects"))
SRC = os.environ.get("T7_SRC") or glob.glob(os.path.join(BASE, "PRJ-2026-005*", "evidence", "final_outputs", "**", "data.json"), recursive=True)[0]
OUT = os.path.join(HERE, "t7_merge.json")

d = json.load(open(SRC, encoding="utf-8"))
names = d.get("names", {})
meta = d.get("meta", {})
ws2 = meta.get("week_start", "")
we2 = meta.get("week_end", "")
asof = meta.get("run_date") or we2 or ""

# EXACT columns of T7's signed-off xlsx report (build_report.py COLS)
COLUMNS = [
    {"key": "sku",       "name": "SKU / ASIN",      "role": "id",     "type": "text"},
    {"key": "row_type",  "name": "Row Type",        "role": "id",     "type": "text"},
    {"key": "title",     "name": "Product Name",    "role": "id",     "type": "text"},
    {"key": "platform",  "name": "Platform",        "role": "id",     "type": "text"},
    {"key": "account",   "name": "Account Name",    "role": "id",     "type": "text"},
    {"key": "week_start","name": "Week Start",      "role": "id",     "type": "text"},
    {"key": "week_end",  "name": "Week End",        "role": "id",     "type": "text"},
    {"key": "amazon",    "name": "Amazon Orders",   "role": "metric", "type": "num"},
    {"key": "ebay",      "name": "eBay Orders",     "role": "metric", "type": "num"},
    {"key": "bq",        "name": "B&Q Orders",      "role": "metric", "type": "num"},
    {"key": "total",     "name": "TOTAL Orders",    "role": "metric", "type": "num"},
    {"key": "perf",      "name": "Performing?",     "role": "id",     "type": "text"},
    {"key": "action",    "name": "Action Required", "role": "id",     "type": "text"},
    {"key": "__name_tip","name": "__name_tip",      "role": "id",     "type": "text"},  # hidden: real name (T7 shows "Bulb", real name on hover)
]

PLATFORM_KEY = {"AMAZON": "amazon", "EBAY": "ebay", "B&Q": "bq"}
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


# ---- reproduce build_groups() exactly (base SKU family + its variants) ------
uni_upper = {r["s"].upper() for r in d.get("rows", []) if r.get("s")}
grp = collections.OrderedDict()
for r in d.get("rows", []):
    if not r.get("s"):
        continue
    grp.setdefault(product_family(r["s"], uni_upper), []).append(r)

groups = []
for base, listings in grp.items():
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
    distinct = {r["s"] for r in listings}
    merged = len(distinct) > 1
    # perf verdict string — EXACTLY as T7's build_html.build_groups produces it
    if y > 0 and x == y:
        perf = "All performing ✅"
    elif x == 0:
        perf = f"0/{y} performing \U0001f534"
    else:
        perf = f"{x}/{y} performing ⚠️"
    action = "See ASIN rows below ↓" if x < y else "—"
    blue = []
    for r in sorted(listings, key=lambda z: (-z["o"], z["p"])):
        pk = PLATFORM_KEY[r["p"]]
        ro = {"amazon": 0, "ebay": 0, "bq": 0}
        ro[pk] = r["o"]
        blue.append({
            "sku": r["s"], "ref": r["r"] or ("B&Q SKU" if r["p"] == "B&Q" else "—"),
            "name": names.get(r["s"], "") or pname or "—", "platform": r["p"],
            "account": r["a"] or "—", "amazon": ro["amazon"], "ebay": ro["ebay"],
            "bq": ro["bq"], "total": r["o"], "performing": r["o"] > 0,
            "action": "—" if r["o"] > 0 else "Investigate & fix listing",
            "variant": r["s"] != base,
        })
    groups.append({"base": base, "name": pname or "—", "skus": len(distinct),
                   "amazon": plat["amazon"], "ebay": plat["ebay"], "bq": plat["bq"],
                   "total": total, "perf": perf, "action": action, "merged": merged,
                   "active": total > 0, "rows": blue})
groups.sort(key=lambda g: (not g["active"], -g["total"], g["base"]))

# ---- flatten to the xlsx's 13-column rows (purple SUMMARY then blue listings)
rows = []
for g in groups:
    base_lbl = g["base"] + (f"  [+{g['skus']-1} SKUs]" if g["merged"] else "")
    rows.append({
        "sku": base_lbl, "row_type": "SKU SUMMARY", "title": "Bulb", "__name_tip": g["name"],
        "platform": "All Platforms", "account": "-", "week_start": ws2, "week_end": we2,
        "amazon": g["amazon"], "ebay": g["ebay"], "bq": g["bq"], "total": g["total"],
        "perf": g["perf"], "action": g["action"],
    })
    for r in g["rows"]:
        sku_lbl = r["sku"] + ("  [variant]" if r["variant"] else "")
        rows.append({
            "sku": sku_lbl, "row_type": clean(r["ref"]), "title": "Bulb", "__name_tip": clean(r["name"]),
            "platform": clean(r["platform"]), "account": clean(r["account"]),
            "week_start": ws2, "week_end": we2,
            "amazon": r["amazon"], "ebay": r["ebay"], "bq": r["bq"], "total": r["total"],
            "perf": "YES" if r["performing"] else "NO", "action": r["action"],
        })

out = {"task": "T7", "label": "SKU Performance", "owner": "Thuwaraga",
       "join_key": "sku", "as_of": asof, "columns": COLUMNS, "rows": rows}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", OUT)
print("task T7 |", len(rows), "rows (", len(groups), "families ) |",
      len([c for c in COLUMNS if not c["key"].startswith("__")]), "columns | as_of", asof)
