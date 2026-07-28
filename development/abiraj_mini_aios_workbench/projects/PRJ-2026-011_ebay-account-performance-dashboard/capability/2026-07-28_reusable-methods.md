# eBay Account Performance Dashboard — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques extracted from this project's locked method.
> **What this project does:** a read-only monthly dashboard of per-account × per-marketplace
> eBay KPIs (Sales, Conversion, Advertising/TACOS, Listings, Stock) across every active eBay
> store account and every marketplace it sells to.
> **Source:** `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md`, `closure/…/2026-07-20_closure.md`,
> `validation/…/2026-07-20_validation.md`.

## Reusable rules / methods

### 1. Use the settled order value (`order_total`) as the sales basis
Revenue = `SUM(order_total)` — eBay's settled paid order value, which already includes the postage
actually charged. Do **not** rebuild revenue as `SUM(item_price*quantity)` (product-only) nor
product + `shipping_template_price` (template postage over-states real postage). `order_total` is
stored at line level; the ≈£100/account gap vs product-only is the real postage.
*Reusable for any eBay sales-value report.*

### 2. Row grain = account × marketplace (never whole-store)
A single eBay store sells cross-border (led_sone billed UK/DE/FR/US/IT buyers in June). A
"whole-store" row wrongly attributes cross-border sales to the store's home marketplace. Grain each
row as one store (`ss_name`) to one marketplace (`market_place`). Here 12 accounts → 22 rows.
*Reusable for any multi-marketplace channel report.*

### 3. Advertising = ON_SITE campaigns only, presented as TACOS
eBay Promoted Listings has two products distinguished by `ppc.record_subtype`: `ON_SITE`
(Priority/Advanced, CPC) and `COST_PER_SALE` (Standard, %-of-sale). Ad Spend/Ad Sales use ON_SITE
only. Filter via `record_id IN (SELECT DISTINCT parent_id FROM ppc WHERE record_main_type='campaign'
AND record_subtype='ON_SITE')` (subquery avoids join fan-out; join key
`ppc_performance.record_id = ppc.parent_id`). Report **TACOS = Ad Spend ÷ total revenue** and
**Return = revenue ÷ Ad Spend** — never attributed ACOS/ROAS (see traps).
*Reusable for any eBay PPC efficiency report.*

### 4. Whole-account conversion, not ad-click conversion
Conversion = `SUM(conversion)/SUM(click)` from `traffic_data which_channel=2` per
`sub_source_name × market_place` — all traffic, not ad-only. Whole-account eBay conversion is low
(~1–3%), so RAG thresholds written for ad-click conversion (green >4.5%) read amber/red and need
recalibration; state the basis explicitly.

### 5. Per-marketplace breakdown from the source, not a mock
Discover the universe from live `order_transaction` (accounts with the month's Completed activity)
rather than trusting the mockup's named set — the mockup named 4, the live data had 12. Marketplaces
present: UK, Germany, France, Italy, Ireland (dormant), US, Canada; UK+DE ≈ 99%.

## Gotchas / traps

- **Attributed eBay ad sales over-count.** eBay attributes one order to *every* overlapping campaign
  (led_sone runs 116), so summed attributed Ad Sales/Orders can exceed real revenue at the
  all-types/campaign level. Spend is clean; only at ON_SITE scope does attributed Ad Sales stay under
  real revenue. Present TACOS, and filter ON_SITE via the `ppc` subquery.
- **`order_total` ≠ `item_price*quantity`**, and `shipping_template_price` over-states postage — use
  `order_total`.
- **eBay traffic = `which_channel=2`** (numeric code: 1=Amazon, 3=Shopify/other) — verify, don't assume.
- **Listing creation dates live in the ledsone DB, not the warehouse** — warehouse `listing_data` has
  only `row_update`/`end_date`, no creation date.
- **`ph_task` publish traps:** the live table has **no real `UNIQUE(task_id)`** despite the DDL comment
  (so `ON CONFLICT` fails) → publish by **pre-DELETE-by-task_id + plain INSERT**; and it has a hidden
  **required `assigned_user_team`** column missing from the sample DDL (set `='ebay_priors'`).
- **Account row is not one marketplace** — always attribute per `market_place` (restates trap #2).
- **Stock overlaps across a store's rows** — physical stock is shared across a store's marketplace rows
  (gross backing stock, not exclusive); label it as such.

## Key sources (schema.table.column)

- Sales — `order_management_copy` warehouse `order_transaction`: `order_total`, `order_id`, `quantity`,
  `item_price`, filters `source_name='EBAY'`, `order_status='Completed'`, `order_date` window.
- Conversion — `order_transaction`/`traffic_data.which_channel=2`: `conversion`, `click`,
  `sub_source_name`, `market_place`.
- Advertising — `ppc_performance` (`source_name='EBAY'`, `record_type='campaign'`, `record_id`) +
  `ppc` (`parent_id`, `record_main_type`, `record_subtype`).
- Active Listings — `listing_data`: `COUNT(DISTINCT ref_id)`, `which_channel_name='ebay'`, per
  `market_place`.
- New Listings — **ledsone DB** `listings.ebay_listings.created_at` + `order_management.sub_source`
  (account name) + `site` (marketplace).
- Stock — `inv_final_stock.stock`, bridged through `listing_data` SKU (`wrong_sku=0`, `mapped_sku`
  fallback).
- Publish target — `tech_team_outputs.ph_task` on `order_management_copy` (via `temp_user`).

## Automation pattern

- **Cadence:** REQ-13-D02 — weekly autonomous refresh, Windows Task `EBPD_Weekly_Dashboard`, Mon 09:30.
- **Window:** dynamic last-complete-month (no hard-coded dates).
- **Rebuild:** direct psycopg2 (no MCP), static-HTML render (fixes the no-JS viewer); Excel imports the
  exact data array from the HTML builder so the two formats cannot drift.
- **Publish:** month-keyed publish to `ph_task` per user (`project_code=ebpd`,
  `assigned_user_team=ebay_priors`, `released`) via `push_ebpd_dashboard.py` — pre-DELETE by task_id +
  plain INSERT.
- **Ops:** status file + `check_status.bat` + Desktop failure alert; credentials moved to the
  git-ignored `ebpd_secrets.bat`. See `automation/AUTOMATION_README.md`.
