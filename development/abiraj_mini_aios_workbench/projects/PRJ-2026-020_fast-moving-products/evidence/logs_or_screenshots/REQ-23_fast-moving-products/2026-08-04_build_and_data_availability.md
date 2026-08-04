# REQ-23-D01 — Build & Data-Availability Note (2026-08-04)

## Verdict: data is COMPLETE for this task, Germany (DE) only, EUR.
Confirmed against the live curated warehouse (`public.order_transaction` etc.) via the Postgres MCP.

## Scope confirmed
- **Germany (DE) only** — as the requester expected. Currency **EUR (€)** (DST currency rule: DE money is in €, never blended with £).
- All three channels have healthy DE volume (last 120 days, Completed): **eBay 8,239 units / Shopify 6,542 / Amazon 4,360**. Data current to **2026-08-03**.
- Windows used: **30-day 2026-07-05 → 2026-08-03**, **90-day 2026-05-06 → 2026-08-03** (rolling, ending last complete day).

## Column → source map (as built)
| Sheet column | Source | Coverage |
|---|---|---|
| SKU | `order_transaction.sku` | 100% |
| Product ID (ASIN / eBay Listing ID / Shopify id) | `asin` / `item_id` / `product_id` | 100% |
| Product Name | `listing_data.title` (by ref_id, then by sku) → `inv_products.title` (skip `Combo Default Title.`) | ~98.6% |
| Category | latest non-null `order_transaction.category_name` per SKU | ~74% (rest `Uncategorised`) |
| Sold Qty 30d / 90d, Orders | `order_transaction` Completed, DE, per channel | 100% |
| Sales Revenue € | `SUM(item_price*quantity)` (EUR) | 100% |
| Current Stock | `location_wise_inv_stock` `location='Germany'` by SKU | 100% (43,940 DE SKUs) |
| Avg Order Qty / Stock Cover Days / Trend / Action / Final Decision | derived (rules on Notes tab) | — |

## Derived-rule DEFAULTS (documented on the workbook's Notes tab; pending Mahima's confirmation)
- **Avg Order Qty** = 30-day units ÷ 30-day orders.
- **Stock Cover Days** = Current Stock ÷ (30-day units ÷ 30).  ← the source's stated formula.
- **Trend** = (30d÷30) vs (90d÷90): ≥1.30 Growing / 0.80–1.30 Stable / <0.80 Slowing.
- **Action** = f(stock, cover, trend): 0→Restock immediately; <30d→Reorder soon; ≤90d→Promote (if Growing) else Maintain; >365d→Overstocked; Slowing & >180d→Slow-reduce; else Monitor.
- **Final Decision** (combined) = f(stock, combined cover): 0→Restock immediately; <30d→Restock soon; ≤90d→Maintain; >365d→Overstocked; else Sufficient.

## Data caveats (also on Notes tab)
1. Trend/Action/Final-Decision thresholds are **defaults**, not yet agreed with Mahima.
2. Some eBay/Shopify **variant SKUs** carry only a variant label as title (e.g. `50W`, `2`, `No`) — best available title used.
3. **Category** coverage ~74%.
4. **Stock is live "as of today"**, not as-of the sales window.
5. Combo SKUs (contain `+`) ranked as sold; `inv_products` may return `Combo Default Title.` (fell back to listing title where possible).
6. **Revenue** = item_price×qty (per-product), which by design differs from `order_total`.

## Repointed to the RAW mcp.ledsone DB (2026-08-04, owner request)
The pipeline now sources **every number + stock + Product ID from the raw `mcp.ledsone` DB** (the
`order_management` + `inventory` schemas), not the curated warehouse. Cross-checked: the raw DB reproduces
the warehouse figures **to the cent** (e.g. Shopify `LSMS320BI+RPR44WH` 51 / €635.69 / 2 orders; stock 492/491/0;
Amazon top rows identical bar ≤€0.01 rounding). Mapping used:
- **Channel:** `order_management.orders.sub_source_id` → `sub_source.source_id` (Amazon=1 / eBay=2 / Shopify=3).
- **Germany:** `orders.market_place = '10'` (`order_management.market_place.id` 10 = Germany). **Status** `'Completed'`.
- **Grain:** per (Product ID, SKU) per channel (`item_asin` / `item_id` / `product_id`); combined per shared `item_sku`.
- **Units/Revenue:** `order_item_info.item_quantity` / `item_price` (VARCHAR → numeric); revenue = Σ price×qty (EUR).
- **Stock:** `inventory.products` → `inventory.local_inventory_current_stock_location_wise` (`warehouse_location='Germany'`).
- **Product Name & Category:** curated catalog labels carried by SKU (raw `inventory.products.title` is a
  `Combo Default Title.` placeholder for combos, and Category has **no per-SKU home** in the raw transactional
  tables — `listings.*.category_id` is the marketplace's own code, not the PH category). Numbers are 100% raw.
- **Connector discipline:** data via `mcp.ledsone.co.uk` (raw), knowledge via `docs.ledsone.co.uk`.
- **Automation-ready:** the shared LED credentials reach this raw host (169.58.91.229), so `fmp_fetch_raw.py`
  can run on a schedule (unlike the warehouse, which had no reachable credentials).

## Reproducibility
- Canonical query: `sql/REQ-23_.../fmp_query_warehouse.sql` (run on the warehouse → one JSON payload).
- Payload snapshot 2026-08-04: `sql/REQ-23_.../fmp_payload_2026-08-04.json` (+ `fmp_payload_snapshot.py`).
- Workbook builder: `sql/REQ-23_.../build_fmp_d01.py` → `evidence/final_outputs/REQ-23_.../REQ-23-D01_fast_moving_products.xlsx`.
- ⚠ **Automation note:** the LED shared credentials reach the RAW `ledsone` (order_management schema), NOT the curated warehouse the report is validated against. Scheduling a refresh needs either warehouse credentials or a re-expression of `fmp_query_warehouse.sql` against `order_management`. Out of scope for D01.
