# Final Closure — Table 7 Weekly SKU Performance Check (REQ-07-D01)

- **Project:** PRJ-2026-005_weekly-sku-performance-check
- **Task / Deliverable:** T7_weekly-sku-performance-check · REQ-07-D01
- **Date closed:** 2026-07-09
- **Owner / Developer:** Abiraj · **End user:** Thuwaraga
- **Verdict:** **GREEN — COMPLETE, VALIDATED & CLOSED.**

## What was delivered
Governed, database-derived **Table 7 Weekly SKU Performance report** for Thuwaraga across Amazon ·
eBay · B&Q UK, for the rolling window **02-Jul → 08-Jul-2026** (run 2026-07-09):

- Read-only dataset query `sql/T7_weekly-sku-performance-check/generate_dataset.sql`.
- Data spine `data.json`; generators `build_html.py` / `build_report.py`.
- Interactive HTML dashboard `Table7_Weekly_SKU_Performance_Thuwaraga.html` (product-family grouping,
  KPIs, Active/All/Zero-order/Merged filters, fixed header, full-width, light theme, "Bulb" labels).
- Template-matching spreadsheet `Table7_Weekly_SKU_Performance_Thuwaraga.xlsx`.
- **Published live** to `tech_team_outputs.ph_task` (DB `order_management_copy`) — **row id 135**:
  `WSPC` / `WSPC_thuwaraga_SKU_Performance_Dashboard-V1` / `assigned_user=thuwaraga` /
  `assigned_user_team=ph_priors` / `team=Development` / `version_status=released`.

## Reconciliation (proof)
Report totals == an independent direct DB `COUNT(DISTINCT order_item_info)` per `source_name` at the
same snapshot (2026-07-09 14:17 Asia/Colombo): **170 orders = Amazon 122 / eBay 27 / B&Q 21**,
**110 listings performing**, **218 product families**, **2,140 listings** (18 `amzn.gr.*` pseudo-SKUs
excluded). Evidence: `validation/T7_weekly-sku-performance-check/2026-07-09_validation.md`.

## Decisions locked
- SKU-family grouping = **merge by product** (anchored, reversible pack-suffix strip; `mapped_sku`
  not used — dirty). 138/218 families merge >1 SKU, tagged `+N SKUs`.
- Data-quality flagged, not silently fixed (dirty `mapped_sku`; `amzn.gr.*` excluded; snapshot drift
  stamped with an `as of` time).
- Delivery = HTML dashboard + xlsx, published as one governed `ph_task` row.

## Sign-off
**Read, validated and signed off by Thuwaraga (end user) and Satheewaran on 2026-07-09.**
No carried-open items for REQ-07-D01.

## Safety
Read-only on live application/`public` data; the only writes were guarded single-row
`INSERT`/`UPDATE` to `tech_team_outputs.ph_task` row 135 (owner-authorised). **No credentials written
to any AIOS file** (the DB write-user's password lives only in a temporary scratchpad script outside
the repo, never in the project or repo).

## Next (optional, future — not part of this closed deliverable)
REQ-07-D02: schedule the weekly Thursday refresh with a dynamic `CURRENT_DATE` window and
parameterise for multi-PH coverage.
