# PROJECT_HOME — Slow Moving Products (smp)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-022_slow-moving-products` |
| **Project code** | `smp` *(provisional)* |
| **Task ID** | `REQ-25_slow-moving-products` *(provisional — REQ-24 = `channel-opportunity`)* |
| **Status** | 🟢 **BUILT & DELIVERED 2026-08-11 — pending Mahima sign-off.** DE-only; live raw `mcp.ledsone`. 13,344 slow-moving SKUs. Excel `SlowMovingProducts_DE.xlsx` (Notes + Slow Moving) + HTML dashboard. All factual columns sourced; Reason/Action on documented default rules awaiting Mahima. Committed to `main` (f79400f). Not published to `ph_task`, not automated. |
| **Opened** | 2026-08-11 |
| **Owner** | Abiraj · **Tech** Sajeesan · **Queryability** Tamil Selvan |
| **Business Validator** | **Mahima** (requester / PH). Publish audience TBC (which `ph_task` team — likely `german_priors`, as FMP #020). |

> ⚠ IDs provisional (source is a spec mock-up with no requirement number). Do not mint a new Task ID on a
> new day/session. Confirm `PRJ-2026-022` / `REQ-25` / `smp` with Abiraj (cosmetic).

## Business question
Which products are **slow moving** — holding stock in Germany but **not selling** — so we can decide what
to bundle, promote, clear, or delist? This is the **inverse of Fast Moving Products (PRJ-2026-020)** and
shares the same PH (Mahima), market (DE) and data foundation.

## Scope (built defaults — CONFIRM with Mahima in discovery)
- **Market:** Germany (DE) across all 3 channels (Amazon / eBay / Shopify), one consolidated per-SKU list.
- **Universe:** SKUs holding **German stock > 0** (14,404 SKUs, 1,275,897 units).
- **Slow-moving definition (default):** **0 units sold in the last 30 days** → **13,344 SKUs**. Sorted by
  Stock Qty descending (biggest tied-up stock first). *Confirm the cutoff & row count with Mahima.*
- **Grain:** one row per SKU, sales summed across all its listings (same SKU-wise grain Mahima confirmed
  for FMP #020 on 2026-08-05 — avoids eBay SKU sprawl).

## The report (9 columns, exact from the source workbook)
`SKU · Product Name · Stock Qty · Last Sale Date · Last 30 Days Sales · Last 90 Days Sales ·
Days Without Sale · Reason · Action`

## Derived fields (business rules — PROVISIONAL, do not treat as agreed)
- **Days Without Sale** = today − last sale date (**all-time** lookback). Never sold on record → **"Never"**.
- **Reason / Action** = a default rule engine (documented on the Excel Notes tab + dashboard banner),
  awaiting Mahima's own vocabulary:
  - Never sold + stock ≥ 100 → *No sales history (dead stock)* / *Clearance · liquidate*
  - Never sold + stock < 100 → *No sales history (dead stock)* / *Review · delist*
  - 90-day sales = 0 & stock ≥ 100 → *High stock, no demand in 90 days* / *Clearance · bundle*
  - 90-day sales = 0 & stock < 100 → *No demand in 90 days* / *Create bundle · promote*
  - Sold in 90d but not last 30d → *Slowing down (no sale in 30 days)* / *Improve listing · promote*

## Data foundation (gathered live 2026-08-11)
| Metric | Value |
|---|---|
| SKUs holding German stock > 0 (universe) | 14,404 (1,275,897 units) |
| Slow-moving rows delivered (0 sold in last 30d) | **13,344** |
| Never sold on record | 9,650 |
| No demand in 90 days | 2,239 (+758 high-stock) |
| Slowing (sold in 90d, not last 30d) | 697 |
| Highest dead-stock SKU | `CBFA200BM` — 4,255 units, never sold |

## 🔒 Source (raw `mcp.ledsone` — reachable via `Ledsone-db-mcp` execute_sql)
- Host `169.58.91.229`, db `ledsone`, schemas `order_management` + `inventory` (numbers 100% raw).
- **Sales:** `order_management.orders` + `order_item_info` + `sub_source`; DE = `orders.market_place='10'`,
  `status='Completed'`, `sub_source.source_id IN (1,2,3)`. Units = `order_item_info.item_quantity`.
- **Stock:** `inventory.products` → `local_inventory_current_stock_location_wise`
  (`warehouse_location='Germany'`), summed per `products.sku`.
- Cross-checked against FMP #020: the raw figures reproduce the warehouse to the cent.

## 🟠 Known traps carried in from prior projects
- **Combo title trap:** `inventory.products.title` is `"Combo Default Title."` for combo SKUs — those fall
  back to the SKU as the name; real catalog names can be carried by SKU later (the FMP pattern).
- **eBay SKU sprawl:** never join eBay sales by SKU alone (one SKU → many item_ids). Handled by the
  SKU-wise grain + `source_id`.
- **Currency trap (DST):** DE = €; never blend with £ marketplaces. (This report is unit-count only, so
  no money column — but keep the rule if revenue is added.)

## Deliverables
- Excel: `evidence/final_outputs/REQ-25_slow-moving-products/SlowMovingProducts_DE.xlsx`
- HTML dashboard: `.../slow_moving_dashboard.html`
- Builder: `sql/REQ-25_slow-moving-products/build_smp_d01.py` (+ `smp_payload.json` snapshot)

## Reviewer gates (none passed yet)
Sajeesan (technical) · Tamil Selvan (queryability) · Mahima (business).

## Next actions
1. **Discovery decision sheet to Mahima:** slow-moving cutoff & row count, Days-Without-Sale convention
   for never-sold SKUs, Reason/Action vocabulary, and publish audience.
2. Confirm provisional `PRJ-2026-022` / `REQ-25` / `smp` identity with Abiraj (cosmetic).
3. On sign-off: publish to `ph_task` (likely `german_priors`) and optionally automate weekly on the FMP
   pattern (`SMP_Weekly_Slow_Moving_Products`).
