# -*- coding: utf-8 -*-
"""
DST -> standard merge file (read-only). Reproduces DST's OWN daily-sales table exactly —
same columns and the same _trend()/growth logic as its render_dst_dashboard.py — from the
fresh governed dst_d01_data.json its runner writes.

Env override: DST_SRC (path to dst_d01_data.json). Multi-currency (£/€/$/CA$) per row via a
hidden "__ccy" column (money is NEVER blended across currencies — matches the source's rule).
Grain: one row per account × marketplace. Native uses a grouped header; the merged flat grid
qualifies the repeated period columns (Sales/Orders Today/Yesterday/Growth/LY). Does NOT touch DST.
"""
import os, glob, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", "..", "projects"))
SRC = os.environ.get("DST_SRC") or glob.glob(
    os.path.join(BASE, "PRJ-2026-015*", "**", "dst_d01_data.json"), recursive=True)[0]
OUT = os.path.join(HERE, "dst_merge.json")

SPEC = [
    ("acct",     "Account",            "id",     "text"),
    ("market",   "Market",             "id",     "text"),
    ("s_today",  "Sales Today",        "metric", "money"),
    ("s_yest",   "Sales Yesterday",    "metric", "money"),
    ("s_diff",   "Sales Diff",         "metric", "money"),
    ("s_growth", "Sales Growth %",     "metric", "pct"),
    ("s_ly",     "Same Day LY Sales",  "metric", "money"),
    ("o_today",  "Orders Today",       "metric", "num"),
    ("o_yest",   "Orders Yesterday",   "metric", "num"),
    ("o_growth", "Orders Growth %",    "metric", "pct"),
    ("o_ly",     "Same Day LY Orders", "metric", "num"),
    ("units",    "Units",              "metric", "num"),
    ("aov",      "AOV",                "metric", "money"),
    ("active",   "Active",             "metric", "num"),
    ("split",    "PH / AH split",      "id",     "text"),
    ("ah_sales", "AH Sales",           "metric", "money"),
    ("ah_trend", "AH Trend",           "id",     "text"),
    ("ph_sales", "PH Sales",           "metric", "money"),
    ("ph_trend", "PH Trend",           "id",     "text"),
    ("trend",    "Trend",              "id",     "text"),
    ("holder",   "AH Holder",          "id",     "text"),
    ("__ccy",    "__ccy",              "id",     "text"),   # hidden — per-row currency
]
COLUMNS = [{"key": k, "name": n, "role": r, "type": t} for (k, n, r, t) in SPEC]

def clean(s):
    return "" if s is None else str(s).strip()

def growth(cur, prev):
    return ((cur - prev) / prev * 100.0) if prev else None

def trend(cur, prev, band):
    # identical to render_dst_dashboard._trend
    if prev == 0 and cur == 0:
        return ""
    if prev == 0:
        return "Up"
    g = (cur - prev) / prev
    return "Up" if g > band else ("Down" if g < -band else "Stable")

data = json.load(open(SRC, encoding="utf-8"))
band = data.get("trend_band", 0.10)
asof = clean(data.get("generated")) or datetime.date.today().isoformat()

rows = []
for a in data.get("rows", []):
    s1, s2, sly = a["s_r1"], a["s_r2"], a["s_ly"]
    o1, o2, oly = a["o_r1"], a["o_r2"], a["o_ly"]
    ph1, ah1, ph2, ah2 = a["ph_r1"], a["ah_r1"], a["ph_r2"], a["ah_r2"]
    rows.append({
        "acct": clean(a.get("display")), "market": clean(a.get("site")),
        "s_today": s1, "s_yest": s2, "s_diff": (s1 - s2), "s_growth": growth(s1, s2), "s_ly": sly,
        "o_today": o1, "o_yest": o2, "o_growth": growth(o1, o2), "o_ly": oly,
        "units": a.get("units_r1"), "aov": ((s1 / o1) if o1 else None), "active": a.get("active"),
        "split": f"{a.get('ph_l')} / {a.get('ah_l')}",
        "ah_sales": ah1, "ah_trend": trend(ah1, ah2, band),
        "ph_sales": ph1, "ph_trend": trend(ph1, ph2, band),
        "trend": trend(s1, s2, band), "holder": clean(a.get("holder")),
        "__ccy": clean(a.get("currency")) or "GBP",
    })

out = {"task": "DST", "label": "Daily Sales", "owner": "eBay Team",
       "join_key": "acct", "as_of": asof, "columns": COLUMNS, "rows": rows}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", OUT)
print("task DST |", len(rows), "rows |", len([c for c in COLUMNS if c['key'] != '__ccy']),
      "columns | as_of", asof)
