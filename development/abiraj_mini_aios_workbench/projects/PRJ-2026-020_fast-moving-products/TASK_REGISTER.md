# TASK REGISTER — PRJ-2026-020 Fast Moving Products

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-23 | **REQ-23-D01** | **Fast Moving Products** report for Mahima — channel-wise top-selling SKUs across **Shopify DE, Amazon DE, eBay DE** + a **Final Combined (All Channels)** roll-up. Per channel: Rank · SKU · Product ID · Product Name · Category · Sold Qty 30d/90d · Sales Revenue € · Orders · Avg Order Qty · Current Stock · Stock Cover Days · Trend · Action. Combined: Overall Rank · SKU · Product Name · Category · Amazon/eBay/Shopify sold Qty · Total Units · Total Revenue € · Current Stock · Stock Cover · Final Decision. Excel workbook (5 tabs: Notes + tab per channel + Combined), built from one read-only warehouse query. | 🟢 **BUILT & DELIVERED (2026-08-04) — pending Mahima sign-off.** DE-only, EUR; live warehouse data to 2026-08-03; top-25 per channel + combined. Every column sourced (Product Name ~98.6%, Category ~74%). Trend/Action/Final-Decision use documented default rules (Notes tab) awaiting Mahima's confirmation. Not published to ph_task, not committed (git gated on GPT review). |

## Source
`evidence/source_documents/REQ-23_fast-moving-products/mahima task.xlsx`
(SHA-256 `f72b3667748a9e63f188d0a1f3a7259f76f2a9f3edff362e0924bb00cf78b41d`, imported 2026-08-04).
The workbook is a **layout mock-up with sample rows** — it defines columns/tables/Action vocabulary, not data.

## Open items (all blocking build)
- Discovery decision sheet to **Mahima**: market scope, window (fixed month vs rolling 30/90-day + anchor),
  ranking metric & top-N, Average Daily Sales denominator (Stock Cover Days), Trend classification rule,
  Action / Final Decision thresholds, Category source, publish audience.
- Confirm provisional identity `PRJ-2026-020` / `REQ-23` / code `fmp` with Abiraj (cosmetic).
- Read the AIOS KB and map every column live against `ledsone` / warehouse (fill `SYSTEM_REFERENCE.md` + coverage %).
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability), Mahima (business).

## Publish record — ph_task
None yet. No publish, no git commit of outputs, until built and signed off.

## Sign-off
None yet.
