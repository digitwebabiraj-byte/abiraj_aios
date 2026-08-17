# -*- coding: utf-8 -*-
"""
EBPD -> standard merge file (read-only). Reproduces EBPD's OWN account×marketplace table
exactly — the same derived cells its build_html_v3.render_view() computes (AOV, Conv,
TACOS, Return, PPC Rank, Sales Rank) — from the fresh ROWS captured by the runner.

Input (EBPD_SRC): a json {"rows": [ 12-field EBPD ROWS lists ], "label": "<Month Year>"}
  ROW = [name, store, mkt, mkc, rev[3], ord[3], units[3], conv[3], ad[4]|None, active, newl, stock]

EBPD is £-only (order_total summed as GBP even for DE rows) -> a hidden "__ccy" column forces £.
Grain: one row per account × marketplace. Native columns use a two-level grouped header; the
merged flat grid qualifies the repeated period columns (Revenue LM/LY, Orders LM/LY, …) so each
stays meaningful. Does NOT touch the EBPD task.
"""
import os, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("EBPD_SRC")
if not SRC:
    raise SystemExit("EBPD_SRC not set (path to the captured ROWS json)")
OUT = os.path.join(HERE, "ebpd_merge.json")

# (key, display-name, role, type) — EXACT native columns, flat-qualified for the merged grid
SPEC = [
    ("acct",       "Account & Marketplace", "id",     "text"),
    ("revenue",    "Revenue",               "metric", "money"),
    ("revenue_lm", "Revenue LM",            "metric", "money"),
    ("revenue_ly", "Revenue LY",            "metric", "money"),
    ("orders",     "Orders",                "metric", "num"),
    ("orders_lm",  "Orders LM",             "metric", "num"),
    ("orders_ly",  "Orders LY",             "metric", "num"),
    ("units",      "Units",                 "metric", "num"),
    ("units_lm",   "Units LM",              "metric", "num"),
    ("units_ly",   "Units LY",              "metric", "num"),
    ("aov",        "AOV",                   "metric", "money"),
    ("aov_lm",     "AOV LM",                "metric", "money"),
    ("aov_ly",     "AOV LY",                "metric", "money"),
    ("conv",       "Conv.",                 "metric", "pct"),
    ("conv_lm",    "Conv. LM",              "metric", "pct"),
    ("conv_ly",    "Conv. LY",              "metric", "pct"),
    ("ad_spend",   "Ad Spend",              "metric", "money"),
    ("ad_sales",   "Ad Sales",              "metric", "money"),
    ("tacos",      "TACOS",                 "metric", "pct"),
    ("ret",        "Return",                "metric", "num"),
    ("ppc_rk",     "PPC Rk",                "metric", "num"),
    ("active",     "Active",                "metric", "num"),
    ("newl",       "New",                   "metric", "num"),
    ("sales_rk",   "Sales Rk",              "metric", "num"),
    ("stock",      "Stock",                 "metric", "num"),
    ("__ccy",      "__ccy",                 "id",     "text"),   # hidden — forces £
]
COLUMNS = [{"key": k, "name": n, "role": r, "type": t} for (k, n, r, t) in SPEC]

MLAB = {"UK": "UK", "Germany": "DE", "France": "FR", "Italy": "IT", "Ireland": "IE",
        "US": "US", "Canada": "CA"}

def aov(r, o):
    return (r / o) if (r is not None and o) else None

payload = json.load(open(SRC, encoding="utf-8"))
raw = payload.get("rows", [])
asof = datetime.date.today().isoformat()

# EBPD keys: name, store, mkt, mkc, rev, ord, units, conv, ad, active, newl, stock
D = [dict(zip(["name", "store", "mkt", "mkc", "rev", "ord", "units", "conv",
               "ad", "active", "newl", "stock"], r)) for r in raw]
n = len(D)

# ranks — identical to render_view: sales rank by reporting-month revenue desc; PPC rank by ad spend desc
order = sorted(range(n), key=lambda i: -((D[i]["rev"] or [0])[0] or 0))
sales_rank = {i: k + 1 for k, i in enumerate(order)}
ppc = sorted([i for i in range(n) if D[i]["ad"]], key=lambda i: -(D[i]["ad"][0] or 0))
ppc_rank = {i: k + 1 for k, i in enumerate(ppc)}

def p3(v):  # a [reporting, LM, LY] triple with Nones tolerated
    return (v or [None, None, None]) + [None, None, None]

rows = []
for i in order:                          # emit in native (revenue-desc) order
    d = D[i]
    rev, od, un = p3(d["rev"]), p3(d["ord"]), p3(d["units"])
    cv = p3(d["conv"])
    ad = d["ad"]
    tacos = (ad[0] / rev[0] * 100.0) if (ad and rev[0]) else None
    ret = (rev[0] / ad[0]) if (ad and ad[0]) else None
    rows.append({
        "acct": f"{d['name']} · {MLAB.get(d['mkt'], d['mkt'])}",
        "revenue": rev[0], "revenue_lm": rev[1], "revenue_ly": rev[2],
        "orders": od[0], "orders_lm": od[1], "orders_ly": od[2],
        "units": un[0], "units_lm": un[1], "units_ly": un[2],
        "aov": aov(rev[0], od[0]), "aov_lm": aov(rev[1], od[1]), "aov_ly": aov(rev[2], od[2]),
        "conv": (cv[0] * 100.0 if cv[0] is not None else None),
        "conv_lm": (cv[1] * 100.0 if cv[1] is not None else None),
        "conv_ly": (cv[2] * 100.0 if cv[2] is not None else None),
        "ad_spend": (ad[0] if ad else None), "ad_sales": (ad[1] if ad else None),
        "tacos": tacos, "ret": (round(ret, 2) if ret is not None else None),
        "ppc_rk": ppc_rank.get(i), "active": d["active"], "newl": d["newl"],
        "sales_rk": sales_rank.get(i), "stock": d["stock"],
        "__ccy": "GBP",
    })

out = {"task": "EBPD", "label": "Account Performance", "owner": "eBay Team",
       "join_key": "acct", "as_of": asof, "columns": COLUMNS, "rows": rows}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", OUT)
print("task EBPD |", len(rows), "rows |", len([c for c in COLUMNS if c['key'] != '__ccy']),
      "columns | as_of", asof)
