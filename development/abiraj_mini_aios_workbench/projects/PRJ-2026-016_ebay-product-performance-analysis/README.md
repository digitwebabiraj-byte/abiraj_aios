# eBay Product Performance Analysis (eppr) — PRJ-2026-016

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`.

## What
A per-listing eBay dashboard for Thinesh: for every active eBay listing (UK + Germany, all accounts),
its identity, pricing, cost stack, sales, traffic and lifecycle — 35 columns, one row per eBay listing.

## Status (2026-07-27)
**REQ-19-D01 BUILT — warehouse-only interim.** 9,781 live listings, **28 of 35 columns populated**,
7 `NO DATA`. Not published, not signed off, not automated.

The 7 `NO DATA` columns are honest gaps, not omissions: Cost Price + Gross/Net/Margin (no product cost
in the warehouse — `sku_cogs` is empty), Watch Count (eBay API only), PPC Campaign (link unreliable in
warehouse), Sales Trend (undefined rule). **Cost Price is the one blocker** — it alone gates the 4
profit columns and needs `ledsone` (down 2026-07-27) or a figure from Thinesh.

## Deliverable
`evidence/final_outputs/REQ-19_.../REQ-19-D01_ebay_product_performance_v4_final.xlsx`

## Build
`sql/REQ-19_.../eppr_build_d01.py` — single read-only module, direct psycopg2 to the warehouse.

## Authoritative documents
- `PROJECT_HOME.md` — canonical project truth
- `SYSTEM_REFERENCE.md` — the 35-column → `schema.table.column` map with grades
- `CLAUDE.md` — execution rules
- `TASK_REGISTER.md` — task/deliverable index

## Next step
Get a Cost Price source, then route the decision sheet to Thinesh and take D01 through reviewer sign-off.
