# SYSTEM_REFERENCE — Slow Moving Products (smp) · PRJ-2026-022 / REQ-25

Complete functional detail: what the report is, the exact column → source map, and the logic behind every
derived field. Derived from the canonical builder `sql/REQ-25_slow-moving-products/build_smp_d01.py`.
All numbers are 100% live from **raw `mcp.ledsone`**; nothing is fabricated. Where no truthful source
exists a cell renders a documented sentinel, never a guess.

## 1. What the system produces
Slow-moving German inventory rendered in the **same 4-tab shape as Fast Moving #020** — one data layer, two files:
- **Excel** `REQ-25-D01_slow_moving_products.xlsx`: `Notes & Method` + **`Shopify DE` · `Amazon DE` · `eBay DE` · `Combined`** tabs (the 9-column table each).
- **HTML dashboard** `REQ-25-D01_slow_moving_products.html`: tab bar + KPI tiles + search / Reason / Recency filters + sortable sticky table + CSV export.

Row order in every tab: **Stock Qty descending** (largest tied-up stock first).

## 2. Universe, tabs & the "slow" definition
- Universe = SKUs with `SUM(stock) > 0` where `warehouse_location = 'Germany'` → **14,404 SKUs**.
- **Channel tabs** (Shopify/Amazon/eBay DE): SKU sold on that channel at some point but **0 units on that
  channel in the last 30 days**; sales figures shown are that channel's only. Rows: Shopify **1,495** ·
  Amazon **1,168** · eBay **3,295**.
- **Combined tab**: **0 units sold on ANY channel in the last 30 days**, including never-sold dead stock;
  sales figures are all-channel. Rows: **13,344**.
- Sales scope: `orders.market_place = '10'` (Germany), `orders.status = 'Completed'`,
  `sub_source.source_id IN (1,2,3)` (Amazon=1 / eBay=2 / Shopify=3).

## 3. Column → source map

| # | Column | Source / derivation | Notes |
|---|---|---|---|
| 1 | **SKU** | `inventory.products.sku` (= `order_item_info.item_sku` for the sales join) | Grain key. One row per SKU. |
| 2 | **Product Name** | `inventory.products.title` (MAX per SKU) | Combo SKUs = `"Combo Default Title."` placeholder → **fall back to the SKU**. Real catalog names can be carried by SKU later. |
| 3 | **Stock Qty** | `inventory.local_inventory_current_stock_location_wise.stock`, `SUM` per SKU, `warehouse_location='Germany'` | Joined `products.id = stock.inventory_id`. |
| 4 | **Last Sale Date** | `MAX(orders.order_date::date)` over DE completed orders (all channels), **all-time** | `NULL` → rendered as empty / "Never sold on record". |
| 5 | **Last 30 Days Sales** | `SUM(order_item_info.item_quantity)` where `order_date >= CURRENT_DATE-30` | Units. `item_quantity` is TEXT → `NULLIF(...,'')::numeric`. Always 0 in this report by definition of the filter. |
| 6 | **Last 90 Days Sales** | `SUM(order_item_info.item_quantity)` where `order_date >= CURRENT_DATE-90` | Units. |
| 7 | **Days Without Sale** | `CURRENT_DATE - Last Sale Date` (all-time) | Never sold → **"Never"**. |
| 8 | **Reason** | **DERIVED — provisional rule engine** (§4) | Not a raw column. Awaiting Mahima. |
| 9 | **Action** | **DERIVED — provisional rule engine** (§4) | Not a raw column. Awaiting Mahima. |

## 4. Reason / Action rule engine (PROVISIONAL — pending Mahima)
Documented on the Excel Notes tab and the dashboard banner. Applied in `build_smp_d01.py::rule_engine`.

| Condition | Reason | Action |
|---|---|---|
| Never sold & stock ≥ 100 | No sales history (dead stock) | Clearance / liquidate |
| Never sold & stock < 100 | No sales history (dead stock) | Review / delist |
| 90-day sales = 0 & stock ≥ 100 | High stock, no demand in 90 days | Clearance / bundle |
| 90-day sales = 0 & stock < 100 | No demand in 90 days | Create bundle / promote |
| Sold in 90d but not last 30d | Slowing down (no sale in 30 days) | Improve listing / promote |

Delivered mix (2026-08-11): No sales history 9,650 · No demand in 90 days 2,239 · High stock no demand 758 ·
Slowing down 697.

## 5. Canonical SQL (embedded in the builder)
```sql
WITH stk AS (
  SELECT p.sku, MAX(p.title) title, SUM(COALESCE(s.stock,0)) stock
  FROM inventory.products p
  JOIN inventory.local_inventory_current_stock_location_wise s ON s.inventory_id=p.id
  WHERE s.warehouse_location='Germany' GROUP BY p.sku HAVING SUM(COALESCE(s.stock,0))>0
),
sales AS (
  SELECT oi.item_sku sku, MAX(o.order_date::date) last_sale,
    SUM(CASE WHEN o.order_date::date>=CURRENT_DATE-30 THEN COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END) q30,
    SUM(CASE WHEN o.order_date::date>=CURRENT_DATE-90 THEN COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END) q90
  FROM order_management.orders o
  JOIN order_management.sub_source ss ON ss.id=o.sub_source_id
  JOIN order_management.order_item_info oi ON oi.order_id=o.id
  WHERE o.market_place='10' AND o.status='Completed' AND ss.source_id IN (1,2,3)
    AND oi.item_sku IS NOT NULL AND oi.item_sku<>'' GROUP BY oi.item_sku
)
SELECT stk.sku, stk.title, stk.stock::int, s.last_sale,
  COALESCE(s.q30,0)::int q30, COALESCE(s.q90,0)::int q90,
  CASE WHEN s.last_sale IS NULL THEN NULL ELSE (CURRENT_DATE - s.last_sale) END dws
FROM stk LEFT JOIN sales s ON s.sku=stk.sku
WHERE COALESCE(s.q30,0)=0
ORDER BY stk.stock DESC, dws DESC NULLS LAST;
```

## 6. Reproduce
```
set LED_PGHOST/LED_PGUSER/LED_PGPASSWORD/LED_PGDATABASE/LED_PGPORT   # git-ignored shared store
python sql/REQ-25_slow-moving-products/build_smp_d01.py
```
Writes `smp_payload.json` (snapshot) and rebuilds both outputs into
`evidence/final_outputs/REQ-25_slow-moving-products/`.

## 7. Open items (do not resolve by guessing — workbench stop-condition)
1. Slow-moving definition / row count (30-day cutoff vs 60/90-day vs top-N by stock).
2. Days-Without-Sale convention for never-sold SKUs ("Never" vs a numeric floor).
3. Reason / Action vocabulary (Mahima's own list).
4. Publish audience (`ph_task` team) and whether to automate weekly.
