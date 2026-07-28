# eBay Product Performance Analysis (eppr) — PRJ-2026-016

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`.

## What
A per-listing eBay dashboard for Thinesh: for every active eBay listing (UK + Germany, all accounts),
its identity, pricing, cost stack, sales, traffic and lifecycle — 34 columns, one row per eBay listing.

## Status
✅ **CLOSED — DELIVERED · PUBLISHED · SIGNED OFF (Thinesh) 2026-07-28 · AUTOMATED.** 11,123 live listings,
**34 columns, 33/34 populated**. Built from **raw `ledsone`** (+ warehouse for organic traffic only).
Published to `ph_task` 472–475 (`ebay_priors`). Monthly auto-refresh (`EPPR_Monthly_Product_Performance`,
2nd Wednesday 10:00).

Only **Sales Trend** is `NO DATA` (undefined bands — a decision). Cost Price / Gross / Net / Margin are
filled from an **owner-agreed 20%-of-selling-price estimate** (no real COGS exists in any DB), flagged as
estimates. Watch Count was **removed** (eBay Trading API only, in no DB).

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
