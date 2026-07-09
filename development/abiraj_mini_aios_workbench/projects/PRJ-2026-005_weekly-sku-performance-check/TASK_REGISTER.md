# Weekly SKU Performance Check (Table 7) — Task Register

Project: PRJ-2026-005_weekly-sku-performance-check

One task (`T7_weekly-sku-performance-check`) carries the Table 7 stream; deliverables tracked per
row (same pattern as REQ-06 D01–D03 in PRJ-2026-004). `T7` is the source's real task id
(Task 7 / Table 7 / project code `PH-2026-07-THUW07`).

| Task ID / Deliverable | Requirement | Status | Source / Handoff | Evidence Path | Validation | PASS/FAIL | Next Step |
|---|---|---|---|---|---|---|---|
| T7_weekly-sku-performance-check · **D01** | Phase-01 Reporting & Presentation: governed rolling-7-day SKU performance report for Thuwaraga across Amazon/eBay/B&Q UK — dataset rebuild query + Portfolio-Holder HTML dashboard + template-matching xlsx, for the first live window 02-Jul→08-Jul-2026; zero-order listings flagged, data-quality risks surfaced; published live to the team output store | Table 7 spec (sheet `PH-2026-07-THUW07 - Abiraj`) + `HANDOFF_weekly_sku_performance_check.md` | **COMPLETE — VALIDATED & CLOSED (2026-07-09)** | source: `evidence/source_documents/T7_weekly-sku-performance-check/HANDOFF.md` · query: `sql/T7_weekly-sku-performance-check/generate_dataset.sql` | outputs: `evidence/final_outputs/T7_weekly-sku-performance-check/Table7_Weekly_SKU_Performance_Thuwaraga.html` · `.xlsx` · `data.json` · `build_html.py` · `build_report.py` — reconciled to live DB @ snapshot 2026-07-09 14:17 (2,140 listings · 110 performing · 170 orders · 122/27/21 · **218 product families**, pack-variants merged; matches an independent direct query) — **published live:** `tech_team_outputs.ph_task` row **135** (`WSPC` / `WSPC_thuwaraga_SKU_Performance_Dashboard-V1`) — evidence in `validation/T7_weekly-sku-performance-check/2026-07-09_validation.md` · closure in `closure/T7_weekly-sku-performance-check/2026-07-09_final_closure.md` | **PASS — validated & signed off by Thuwaraga (end user) + Satheewaran (2026-07-09)** | **NONE — delivered, live and closed.** (Optional future REQ-07-D02: schedule the weekly refresh + multi-PH parameterisation.) |

## Items — status at closure (2026-07-09)

REQ-07-D01 is **VALIDATED & CLOSED**; the items below are resolved or moved to a future requirement.

1. **SKU-family grouping — RESOLVED & shipped.** Owner chose **merge by product** (anchored,
   reversible pack-suffix strip; `mapped_sku` not used). 218 families (138 merge >1 SKU, tagged
   `+N SKUs`). Validated & signed off (Thuwaraga + Satheewaran).
2. **Delivery channel — RESOLVED.** Delivered as the interactive HTML dashboard + xlsx and
   **published live** to `tech_team_outputs.ph_task` (row 135), matching the sibling T1–T6 dashboards.
3. **Zero-order framing — ACCEPTED.** Dashboard defaults to Active families; confirmed at sign-off.
4. **Live-DB snapshot drift — HANDLED.** Each run carries an `as of` timestamp; reconciliation is at
   the same instant.
5. **Scheduling / automation — FUTURE (not in D01 scope).** Thursday trigger + dynamic
   `CURRENT_DATE` window + multi-PH parameterisation → optional REQ-07-D02.
6. **Postgres MCP reconnect** required before any future live re-pull (connector GUID rotates per session).
