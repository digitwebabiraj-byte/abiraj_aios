# PROJECT_HOME — Fast Moving Products (fmp)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-020_fast-moving-products` |
| **Project code** | `fmp` *(provisional)* |
| **Task ID** | `REQ-23_fast-moving-products` *(provisional — REQ-22 = `epns`)* |
| **Status** | 🟢 **BUILT & DELIVERED 2026-08-04 — pending Mahima sign-off.** DE-only, EUR, live warehouse data to 2026-08-03. Excel `REQ-23-D01_fast_moving_products.xlsx` (Notes + Shopify/Amazon/eBay DE + Combined). All columns sourced; Trend/Action/Final-Decision on documented default rules awaiting Mahima. Not published/committed. See `evidence/logs_or_screenshots/REQ-23_.../2026-08-04_build_and_data_availability.md`. |
| **Opened** | 2026-08-04 |
| **Owner** | Abiraj · **Tech** Sajeesan · **Queryability** Tamil Selvan |
| **Business Validator** | **Mahima** (requester / PH — new). Publish audience TBC (which `ph_task` team Mahima belongs to). |

> ⚠ IDs provisional (source is a spec mock-up with no requirement number). Do not mint a new Task ID on a
> new day/session. Confirm `PRJ-2026-020` / `REQ-23` / `fmp` with Abiraj (cosmetic).

## Business question
Which products are **fast moving** (top sellers by units) on each DE sales channel — **Shopify DE, Amazon
DE, eBay DE** — over the reporting window, and combined across all channels? For each, show the velocity
and stock picture and recommend an inventory **Action** so buying/promotion decisions can be made.

## Scope (from the source workbook — CONFIRM with Mahima in discovery)
- **Market:** Germany (DE) across all 3 channels. Confirm whether DE-only or all marketplaces.
- **Window:** the source header reads *"Report Filter: 01 July 2026 – 31 July 2026 (custom date range +
  live data)"* — a **calendar-month** window, with **30-day AND 90-day** sold-qty columns side by side.
  Confirm: fixed month vs rolling 30/90-day, and the anchor.
- **Ranking metric:** "fast moving" = top N by **Sold Qty**. Confirm N (source shows top 3 per channel,
  top 5 combined) and whether ranked by 30-day qty, revenue, or velocity.

## The four tables (exact columns from the source)
**1. Fast Moving Products – Shopify DE**
`Rank · SKU · Product ID · Category · Sold Qty (30 Days) · Sold Qty (90 Days) · Sales Revenue € · Orders ·
Avg Order Qty · Current Stock · Stock Cover Days · Trend · Action`

**2. Fast Moving Products – Amazon DE**
`Rank · SKU · Product ID (ASIN) · Product Name · Category · Sold Qty (30 Days) · Sold Qty (90 Days) ·
Sales Revenue € · Orders · Avg Order Qty · Current Stock · Stock Cover Days · Trend · Action`

**3. Fast Moving Products – eBay DE**
`Rank · SKU · Listing ID · Product Name · Category · Sold Qty (30 Days) · Sold Qty (90 Days) ·
Sales Revenue € · Orders · Avg Order Qty · Current Stock · Stock Cover Days · Trend · Action`

**4. Final Combined Top Products (All Channels)**
`Overall Rank · SKU · Category · Amazon sold Qty · eBay sold Qty · Shopify sold Qty · Total Units Sold ·
Total Revenue (€) · Current Stock · Stock Cover · Final Decision`

## Derived fields (formulae stated / implied by the source)
- **Stock Cover Days = Current Stock ÷ Average Daily Sales** (explicit in the source note).
  Average Daily Sales must be defined (30-day qty ÷ 30? ÷ days-in-window?) — confirm.
- **Avg Order Qty = Sold Qty ÷ Orders**.
- **Trend** = Growing ↑ / Stable / Slow — the classification rule (e.g. 30-day-rate vs 90-day-rate) must
  be defined with Mahima; it is a business rule, not a raw column.
- **Action / Final Decision** = a rule engine (Maintain / Promote / Reorder / Restock / Monitor / Bundle …)
  driven by trend + stock cover. The exact thresholds must be agreed — do not invent them.

## 🔒 Source (to confirm in discovery — follow the house rules)
- **Orders / units / revenue** — per channel:
  - **Amazon DE** (`which_channel=1`), **eBay DE** (`which_channel=2`), **Shopify DE** (`which_channel=3`).
  - eBay raw source of record = **raw `ledsone`** (the EPPR/EPPA/DST pattern); the warehouse hides SMART campaigns.
- **Stock / current stock** — `location_wise_inv_stock` via the `listing_data` SKU bridge (the
  `ppc-stock-lookup` skill: wrong_sku check → mapped_sku fallback → clean-SKU step). Filter by the DE location(s).
- **AIOS knowledge base** (`docs.ledsone.co.uk/mcp`) — **read before writing any SQL.** This is a
  **multi-domain** question (Orders + Stock, 3 channels) → use `text-to-sql-multi` + `ppc-stock-lookup`.

## 🟠 Known traps carried in from prior projects
- **eBay SKU sprawl:** never join sales by SKU alone (one SKU → many item_ids, ~13× overstatement).
  Attribute by order_id / item_id, isolate eBay with `source_id=2`.
- **Currency trap (DST):** `orders.total` is in the **marketplace's own currency**. This report is DE →
  **€**; do not blend with £ marketplaces and never label a value with the wrong symbol.
- **Amazon parent/child + title on the parent row** (`all_list=0`) — the EPPR gotcha.
- **Stock SKU resolution is non-trivial** — listing SKU ≠ inventory SKU; the clean-SKU step is mandatory.
- **Combined table SKU key:** the same physical product has different Product IDs per channel (ASIN /
  Listing ID / Shopify id) but a shared SKU — the roll-up key must be the base SKU, confirmed clean.

## Deliverables (planned)
- Excel: `evidence/final_outputs/REQ-23_.../REQ-23-D01_fast_moving_products.xlsx`
  (Shopify DE · Amazon DE · eBay DE · Combined tabs).
- Optional HTML dashboard (house pattern).
- Builder: single read-only module `sql/REQ-23_.../fmp_build_d01.py`.

## Reviewer gates (none passed yet)
Sajeesan (technical) · Tamil Selvan (queryability) · Mahima (business).

## Next actions
1. **Discovery decision sheet to Mahima:** market scope, window (fixed month vs rolling 30/90), ranking
   metric & N, Average Daily Sales definition, Trend classification rule, Action/Final-Decision thresholds,
   Category source, and publish audience.
2. Confirm the provisional `PRJ-2026-020` / `REQ-23` / `fmp` identity with Abiraj (cosmetic).
3. Read the AIOS knowledge base, then map every column live against `ledsone` / warehouse into
   `SYSTEM_REFERENCE.md` with a coverage %.
4. Build the single generator module; reconcile a real top-seller per channel before locking layout.
5. Decide publish audience (`ph_task`) — no publish, no git commit of outputs until signed off.
