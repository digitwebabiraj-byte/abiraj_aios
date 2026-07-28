# eBay Return Analysis — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques extracted from this project (PRJ-2026-012, `ERA` / REQ-14).
> These are methods worth reusing on other eBay/analytics projects — not project-specific facts.
> **What this project does:** a per-SKU eBay Return Analysis dashboard — one row per variant SKU
> with ≥ 1 eBay return in the period (returns, rate, refund/return-cost, main reason, negative
> feedback, open cases, stock, Ad Spend/Sales/ACOS/ROAS), across all eBay stores/marketplaces (UK, DE).
> **Sources:** `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md`, `automation/AUTOMATION_README.md`,
> `validation/REQ-14_.../2026-07-20_live_count_verification.md`, `closure/REQ-14_.../2026-07-20_closure.md`.

## Reusable rules / methods

### 1. transaction_id → SKU bridge for multi-variant eBay listings
Map an eBay return (or feedback row) to its exact variant SKU via
`ebay_returns.transaction_id` → `order_management.order_item_info.item_transaction_id` → `real_sku`
(fallback `item_sku`). **Never join on `item_id`** — 1,331 `item_id`s map to multiple variant SKUs,
so `item_id` mis-attributes returns to the wrong variant. The `transaction_id` bridge is a 100% match
to the exact variant. Reuse for any per-variant eBay metric (returns, feedback, units).

### 2. CPC + CPS ad blend (two ad models in two tables)
eBay has two ad models in different tables; using only one silently drops half the ad cost.
- **CPC / Advanced (`ON_SITE`)** lives in `ebay_campaigns.performance_data` (every value column is
  `cpc_*` — CPC-only). Per-listing, so **spread across the listing's variant SKUs** (÷ variants).
- **CPS / Standard (`COST_PER_SALE`)** is **not** in `performance_data` (its rows there are zero); the
  cost is a per-sale fee in `accounting.ebay_order_expenses` (`fee_type IN (AD_FEE, PREMIUM_AD_FEES)`),
  attributed to SKU by splitting each order's fee across its lines by line value.
- **Ad Spend = CPC spend + CPS ad fee; Ad Sales = CPC attributed sales + CPS line revenue.** Reading
  only `performance_data` was the cause of earlier empty ad columns.

### 3. Intentional blanks for genuinely-missing metrics (not zeros)
Distinguish "no data" from "real zero". Leave **blank**: Return Rate where period orders = 0; ACOS
where Ad Sales = 0; ROAS where Ad Spend = 0. But **show real `0` / `£0.00`** for count/£ columns —
formatting real zeros as dashes made columns look empty and was a defect. Document each blank cause so
reviewers read it as data, not a bug.

### 4. Blended (pooled) return rate for the TOTAL row
The TOTAL/AVG row uses a **blended** return rate (total returns ÷ total units), not an average of the
per-SKU rates — e.g. June 2026 = 17.7% across 153 returns. Per-SKU Return Rate can exceed 100% when a
SKU has period returns but few/zero period orders (bought in an earlier window). State which rate you use.

### 5. Anchor a re-runnable build against a known reference month
The build is re-runnable for any month by changing six dates; a live rebuild must reproduce the
June-2026 reference to the penny (144 SKUs · 153 returns · 17.7% · Refund £2,937.37 · Return Cost
£869.39 · Ad Spend £1,387.96 · Ad Sales £9,343.63 · ACOS 14.9% · ROAS 6.73x) before acceptance.

## Gotchas / traps
- **Direct psycopg2 read-only to `ledsone`, no MCP.** The live build and automation query `ledsone`
  directly via read-only psycopg2 (`set_session(readonly=True)`) — not the Ledsone DB MCP path.
- **`item_id` is a multi-variant container** — see method 1; join on `transaction_id`, never `item_id`.
- **Wrong DB layer.** Use the normalised domain schemas (`customer_service`, `order_management`,
  `accounting`, `ebay_campaigns`, `listings`, `inventory`); the `public.*` denormalised layer is a
  different DB and returns nothing here.
- **Fees keyed on the eBay order reference** (`orders.order_id`, varchar) — **not** internal `orders.id`.
- **Fee coverage ~65%** — Return Cost = £0 on some SKUs means no matching fee row upstream, a data
  limitation not a bug. Currency is mixed GBP/EUR, **not FX-normalised**.
- `item_quantity` is stored as TEXT → cast to numeric before arithmetic.

## Key sources (schema.table.column)
- Returns: `customer_service.ebay_returns` (`transaction_id`, `reason`, `seller_refund_amount`,
  `to_state`, `sub_source`) — two `DISTINCT ON (return_id)` CTEs (id ASC = reason/refund, id DESC = state).
- Negative feedback: `customer_service.ebay_orders_customer_feedbacks` (`type='Negative'`).
- SKU bridge / title: `order_management.order_item_info` (`item_transaction_id`, `real_sku`, `item_title`).
- Account name: `order_management.sub_source.map_name`.
- Orders: `order_management.orders` ⋈ `sub_source` ⋈ `source` (`source_name='EBAY'`), period on `order_date`.
- Fees / CPS ads: `accounting.ebay_order_expenses` (`transaction_type='REFUND'`,
  `fee_type IN (FINAL_VALUE_FEE, FINAL_VALUE_FEE_FIXED_PER_ORDER, AD_FEE, PREMIUM_AD_FEES)`).
- CPC ads: `ebay_campaigns.performance_data` ⋈ `campaigns` (`campaign_type='ON_SITE'`);
  listing→variant spread via `listings.ebay_listings` (`item_id`, `wrong_sku=0`, `sku`).
- Stock: `inventory.products` ⋈ `inventory.local_inventory_current_stock_location_wise` (live snapshot).
- Publish target: `tech_team_outputs.ph_task` (publish only, never a data source).

## Automation pattern
- Windows Task **`ERA_Monthly_Dashboard`**, **day 5 of each month, 09:30**; reports the last complete
  calendar month. Day 5 = settle buffer after month end; 09:30 staggered against jobs sharing the one
  restricted `temp_user` warehouse account.
- Reads `ledsone` read-only via direct psycopg2; renders through the same
  `build_returns_live_html.py` that produced the signed-off June build.
- **Refresh-in-place:** publishes the 4 `ph_task` rows (ids **387 Thinesh · 388 Jarsini · 389 kobiga ·
  390 powsteena**; `project_code=ERA`, `assigned_user_team=ebay_priors`, `released`) via **pre-DELETE by
  `task_id` + plain INSERT** (no real `UNIQUE(task_id)`, so `ON CONFLICT` fails). Task ids carry the
  reporting month, so a within-month re-run refreshes that month while each new month adds its own.
- **Fail-closed gates:** credentials-absent, zero-SKU floor (`ERA_MIN_SKUS`), `returns < SKUs`,
  negative money, June-2026 anchor drift, placeholder/undersized render, per-row md5 before commit,
  row-count ≠ 4. Exit code 2 = a gate failed and nothing was published (last good dashboard stays live).
- **Credentials** come from the global shared store
  (`05_documentation/capability/shared_db_credentials/`); missing password aborts before any write.
- Same monthly-report pattern as PRJ-2026-010 (EPC) and PRJ-2026-008 (FRRC).
