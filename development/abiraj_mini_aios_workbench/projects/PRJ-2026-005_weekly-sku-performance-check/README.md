# PRJ-2026-005 — Weekly SKU Performance Check (Table 7)

Governed weekly report for Portfolio Holder **Thuwaraga**: every listing on **Amazon · eBay ·
B&Q (UK)**, grouped by base SKU, with a rolling-7-day Completed-order count per platform and a
flag on every zero-order listing. Runs **every Thursday** (window = last 7 days ending yesterday).

| | |
|---|---|
| **Project ID** | `PRJ-2026-005_weekly-sku-performance-check` |
| **Task** | `T7_weekly-sku-performance-check` (Task 7 / Table 7 / `PH-2026-07-THUW07`) |
| **Owner / Dev** | Abiraj · **PH:** Thuwaraga · **Reviewers:** Sajeesan (tech), Tamil Selvan (queryability) |
| **Source** | PostgreSQL `order_management_copy` (read-only) — `order_transaction`, `listing_data` |
| **Status** | **COMPLETE — VALIDATED & CLOSED** (2026-07-09, Thuwaraga + Satheewaran) · published live: `tech_team_outputs.ph_task` row 135 |

## Deliverables

- **Dashboard** → [`Table7_Weekly_SKU_Performance_Thuwaraga.html`](evidence/final_outputs/T7_weekly-sku-performance-check/Table7_Weekly_SKU_Performance_Thuwaraga.html)
- **Spreadsheet** → [`Table7_Weekly_SKU_Performance_Thuwaraga.xlsx`](evidence/final_outputs/T7_weekly-sku-performance-check/Table7_Weekly_SKU_Performance_Thuwaraga.xlsx)
- **Rebuild query** → [`generate_dataset.sql`](sql/T7_weekly-sku-performance-check/generate_dataset.sql)
- **Data spine** → `evidence/final_outputs/T7_weekly-sku-performance-check/data.json`
- **Builders** → `build_html.py`, `build_report.py`

## This week (run 2026-07-09 · window 02-Jul → 08-Jul-2026 · as of 14:17 Asia/Colombo)

**218 product families · 2,140 listings · 110 performing · 170 orders** (Amazon 122 · eBay 27 · B&Q 21).
Grouping = base SKU + pack-size variants merged (owner-confirmed). Live DB — counts are a
point-in-time snapshot and settle for ~1–2 days after a window closes.

## Read next

- `PROJECT_HOME.md` — governance, scope, reviewers, risks.
- `SYSTEM_REFERENCE.md` — locked data rules, pipeline, columns, regeneration.
- `TASK_REGISTER.md` — task/deliverable tracking & open items.
- `CLAUDE.md` — project execution rules.
