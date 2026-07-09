# SMAW Table 5 Weekly Stock Check — Task Register

Project: PRJ-2026-004_smaw-table5-stock-check

One task (`REQ-06_table5-weekly-stock-check`) carries the REQ-06 stream; deliverables tracked per
row below (same pattern as REQ-05 D01–D09 in PRJ-2026-001, REQ-04 in PRJ-2026-003).

| Task ID / Deliverable | Requirement | Status | Task Home / Requirement Doc | Evidence Path | Validation Path | Closure Path | PASS/FAIL | Next Step |
|---|---|---|---|---|---|---|---|---|
| REQ-06_table5-weekly-stock-check · **D01** | REQ-06-D01 — Phase-01 Reporting & Data Model: discovery-first duplicate-risk scan of existing stock objects, map every Table 5 column to a real source (VERIFIED/PARTIAL/UNPROVEN), and — if duplicate-risk clears — build the read-only reporting view `v_table5_weekly_stock_check` + evidence note | **DELIVERED — pending review** | requirement doc: DigitWeb_Works_Abiraj/08_07_2026/2026-07-08_abiraj_REQ-smaw_REQ-06-D01.md | sql/REQ-06_table5-weekly-stock-check/generate_dataset.sql · evidence/source_documents/REQ-06_table5-weekly-stock-check/HANDOFF.md | validation/REQ-06_table5-weekly-stock-check/ (pending) | closure/REQ-06_table5-weekly-stock-check/ (pending) | **PENDING** | Reviewer sign-off (Tamil Selvan · Sajeesan) |
| REQ-06_table5-weekly-stock-check · **D02** | REQ-06-D02 — Phase-02 Reporting & Presentation: render the governed Table 5 output as a Portfolio-Holder-facing interactive HTML dashboard (colour-banded, filterable, CSV/PDF export), reconcile to live inventory truth, surface the legacy→canonical SKU risk, and scope the full-portfolio (all-ASIN) coverage expansion | **DELIVERED — pending review** | requirement doc: DigitWeb_Works_Abiraj/09_07_2026/2026-07-09_abiraj_REQ-smaw_REQ-06-D02.md | evidence/final_outputs/REQ-06_table5-weekly-stock-check/Table5_Weekly_Stock_Check_Thuwaraga.html · build_html.py · dataset.py · build_report.py | validation/REQ-06_table5-weekly-stock-check/ (pending) | closure/REQ-06_table5-weekly-stock-check/ (pending) | **PENDING** | (1) Thuwaraga's full-portfolio coverage decision · (2) reviewer sign-off |

## Open items (carried in PROJECT_HOME → Known Risks)

1. **Full-portfolio coverage decision** — which source defines "all her ASINs" (ph-asin
   segmentation / `ph_action_board` vs all-time sales vs listings) + whether no-sales-zero-stock
   items are included. Question raised 2026-07-09, dismissed (awaiting).
2. **Legacy→canonical SKU mapping source** — not in `order_management_copy`; candidates unverified.
3. **4 UNPROVEN D01 fields** — FBA on-hand · container ETA · W1/W2/W3 · stock-checked date.
4. **Postgresql MCP reconnect** required before any live re-pull.
