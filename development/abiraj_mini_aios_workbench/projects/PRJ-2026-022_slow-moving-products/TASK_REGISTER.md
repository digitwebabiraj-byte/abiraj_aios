# TASK REGISTER — PRJ-2026-022 Slow Moving Products

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-25 | **REQ-25-D01** | **Slow Moving Products** report for Mahima — German-stocked inventory that is **not selling** (inverse of Fast Moving #020). Same 4-tab shape as FMP: **Shopify DE · Amazon DE · eBay DE · Combined**. Columns: SKU · Product Name · Stock Qty · Last Sale Date · Last 30 Days Sales · Last 90 Days Sales · Days Without Sale · Reason · Action. Excel (Notes + 4 tabs) + interactive HTML dashboard (tabbed), built from one read-only raw-`ledsone` fetch. | 🟢 **BUILT & DELIVERED (2026-08-11) — pending Mahima sign-off.** DE-only; live raw `mcp.ledsone`. Rows per tab: **Shopify 1,495 · Amazon 1,168 · eBay 3,295 · Combined 13,344**. Channel tabs = sold on that channel before but 0 units there in last 30d (channel-only figures); Combined = 0 sold on any channel in last 30d incl. never-sold dead stock. Sorted by stock desc. Every factual column sourced live; Reason/Action use documented default rules awaiting Mahima. Committed to `main`. Not published to `ph_task`, not automated. |

## Source
`evidence/source_documents/REQ-25_slow-moving-products/2026-08-11_source_slow-moving-spec.xlsx`
(imported 2026-08-11, from `mahima task (2).xlsx`, sheet "slow moving").
The workbook is a **layout mock-up with sample rows** — it defines columns/Reason-Action vocabulary, not data.

## Deliverables (built)
- Excel: `evidence/final_outputs/REQ-25_slow-moving-products/SlowMovingProducts_DE.xlsx`
- HTML dashboard: `evidence/final_outputs/REQ-25_slow-moving-products/slow_moving_dashboard.html`
- Builder: `sql/REQ-25_slow-moving-products/build_smp_d01.py` (+ `smp_payload.json` snapshot)

## Open items (all pending Mahima — not blocking the delivered draft)
- **Slow-moving definition / row count** — 30-day-zero cutoff (current) vs 60/90-day vs top-N by stock.
- **Days Without Sale** convention for the 9,650 never-sold SKUs — "Never" (current) vs a numeric floor.
- **Reason / Action** vocabulary — Mahima's own list vs the documented default rule engine.
- Confirm provisional identity `PRJ-2026-022` / `REQ-25` / `smp` with Abiraj (cosmetic).
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability), Mahima (business).

## Automation
❌ **Not automated.** On sign-off, mirror the FMP pattern → Windows task `SMP_Weekly_Slow_Moving_Products`
(fail-closed runner, row-floor + collapse gates, git-ignored secrets, Desktop alert on failure).

## Publish record — ph_task
❌ **Not published.** On sign-off, likely audience = `german_priors` (same as FMP #020, Mahi / staff.users
id 40). No publish, and no publish-related git write, until the audience is named and each recipient verified.

## Business decisions (Mahima)
- Pending — none confirmed yet. (Grain SKU-wise is carried over from FMP #020, confirmed by Mahima 2026-08-05.)

## Sign-off
None yet. Draft delivered 2026-08-11 for Mahima's review of the three open rules above.
