# SYSTEM_REFERENCE — eBay Account Performance Dashboard (REQ-13)

Full functional detail. Governance is `PROJECT_HOME.md`; landing is `README.md`.

## 1 · Grain & scope
- **Row grain = account (`ss_name`) × marketplace (`market_place`).** A single eBay store sells cross-border
  (led_sone sold to UK, DE, FR, US, IT buyers in June), so a "whole-store" row would attribute cross-border
  sales to the store's home marketplace. Each row is one store's sales to one marketplace's buyers.
- **Universe = the 12 eBay accounts with June-2026 Completed activity**, across their marketplaces = **22
  rows**. Channel = `source_name='EBAY'`. Marketplaces present: UK, Germany, France, Italy, Ireland
  (dormant — 0 orders), US, Canada. UK + DE ≈ 99% of activity.
- **Account mapping (Thinesh-confirmed):** LEDSONE UK=`led_sone` · SUNSONE UK=`so_926407` · Electricalsone
  UK=`electricalsone` · LEDSONE DE=`ledsonede`. The other 8 (huettenlampen, coventrylights, vintageinterior,
  dctransformer, re6865, neighbourmarket, lighting_sone, homin_gmbh) shown by store name.

## 2 · Reporting window
- **Reporting month = June 2026:** `order_date >= '2026-06-01' AND order_date < '2026-07-01'`.
- **Last Month (LM) = May 2026**; **Last Year (LY) = June 2025** — same `< next-month` pattern.
- Traffic (`traffic_data which_channel=2`) history starts 2025-04, so LY conversion exists only for
  accounts live since June 2025.

## 3 · SALES (order_transaction)
- Filter: `source_name='EBAY'`, `order_status='Completed'` (Refunded / Cancelled excluded).
- **Revenue = `SUM(order_total)`** — eBay's settled paid order value, which includes the postage actually
  charged. **NOT** `SUM(item_price*quantity)` (product-only), and **NOT** product + `shipping_template_price`
  (the template postage over-states real postage). `order_total` is stored at line level;
  `SUM(order_total) ≠ SUM(item_price*quantity)` (≈ £100/account difference is the real postage).
- **Orders = `COUNT(DISTINCT order_id)`** (a multi-item order counts once). The owner's other analysis showed
  **`COUNT(*)` = order-line count (1,619 vs 1,517 for led_sone UK)** — noted, not adopted.
- **Units = `SUM(quantity)`**. **AOV = Revenue / Orders.** All three periods (June / LM / LY).

## 4 · CONVERSION (traffic_data)
- **eBay organic traffic lives in `traffic_data.which_channel = 2`** (1 = Amazon, 3 = Shopify/other).
- **Conversion = `SUM(conversion) / SUM(click)`** — whole-account (all traffic, not just ads), per
  `sub_source_name × market_place`. Page-view based, typically ~1–3% for eBay. Blank where no traffic
  (e.g. Neighbour Market).
- ⚠ The mockup's RAG threshold (green >4.5%) was written for ad-click conversion; whole-account is lower,
  so most cells read amber/red under it — flagged for recalibration.

## 5 · ADVERTISING (ppc_performance + ppc) — the ON_SITE story
- eBay Promoted Listings has **two products**, distinguished by campaign metadata `ppc.record_subtype`:
  **`ON_SITE`** (Priority / Advanced, CPC) · **`COST_PER_SALE`** (Standard, pay-%-of-sale) · `OFF_SITE`.
- **Ad Spend / Ad Sales = ON_SITE campaigns ONLY** (Standard excluded per Thinesh). Query:
  `ppc_performance` (`source_name='EBAY'`, `record_type='campaign'`) filtered to
  `record_id IN (SELECT DISTINCT parent_id FROM ppc WHERE record_main_type='campaign' AND
  record_subtype='ON_SITE')`. **Join key: `ppc_performance.record_id = ppc.parent_id`** (the campaign id;
  `child_id='0'` on both). Filter via the `IN (…parent_id…)` subquery to avoid join fan-out.
- **Do NOT present attributed ACOS/ROAS.** eBay attributes one order to **every** overlapping campaign
  (led_sone runs 116), so summed attributed Ad Sales/Orders over-count and can exceed real revenue at the
  all-types/campaign level. Spend is clean (one row per campaign per day, incremental). At the ON_SITE
  scope, attributed Ad Sales stays under real revenue, so **Ad Sales is shown** (labelled ON_SITE-attributed).
- **Efficiency = TACOS = Ad Spend ÷ total revenue** (RAG green <12% / amber 12–18% / red >18%);
  **Return = revenue ÷ Ad Spend** (green >8 / amber 5–8 / red <5). **PPC Rank = ad rows by ON_SITE spend.**
- Only **5 of 12** accounts run eBay ads (led_sone, so_926407, electricalsone, ledsonede, huettenlampen);
  the rest show no ad data. Some marketplaces have no ON_SITE campaign (led_sone-IT, electricalsone-US →
  blank). led_sone Canada has £10.29 ON_SITE spend but **no Canada Completed sales**, so no row to attach it to.

## 6 · LISTINGS & STOCK
- **Active Listings = `COUNT(DISTINCT ref_id)`** from `listing_data` (`which_channel_name='ebay'`), per
  `market_place`. (`offer_id`/`is_ended`/`status` are unpopulated → `ref_id` is the listing key.)
- **New Listings = `COUNT(DISTINCT item_id)` created in the month** from the **ledsone DB**
  `listings.ebay_listings.created_at` (a genuine creation timestamp, 2015→2026), joined to
  `order_management.sub_source` for the account name, `site` for the marketplace. The **warehouse
  `listing_data` has no creation date** (only `row_update`/`end_date`) — this is why it must come from the
  ledsone DB.
- **Stock = `SUM(inv_final_stock.stock)`** for the SKUs the account lists in that marketplace (via the
  `listing_data` SKU bridge, `wrong_sku=0`, `mapped_sku` fallback). Physical stock is **shared** across a
  store's marketplace rows → the figure overlaps between a store's rows (gross backing stock, not exclusive).
- **Sales Rank = rows ranked by June revenue** (highest = #1), Thinesh-confirmed.

## 7 · Columns (final, 24 in HTML incl. Account+Market; Excel mirrors)
`Account · Market · | Revenue LM LY · Orders LM LY · Units LM LY · AOV LM LY · Conversion LM LY · | Ad Spend ·
Ad Sales · TACOS · Return · PPC Rank · | Active · New · Sales Rank · Stock`. The mockup's duplicate second
"AOV" block (values ~11–12, undefined) was **removed**.

## 8 · Deliverables & build
- **HTML** (`…FINAL.html`) — self-contained, slate+teal theme, sticky grouped+column headers, pinned
  Account+Market column, live search + Account/Marketplace/Sort filters, CSV export, print CSS. Built by
  `build_html_v3.py` (data embedded as a JS `ROWS` array).
- **Excel** (`…FINAL.xlsx`) — 3 sheets (Dashboard 22 rows + total, By Marketplace, Definitions). Built by
  `build_excel_v3.py`, which **imports the exact `R` data from `build_html_v3.py`** so the two formats
  cannot drift. Derived cells (AOV, TACOS, Return, totals) are live formulas; recalc'd 0 errors.
- **Publisher** (`push_ebpd_dashboard.py`) — pre-DELETE by task_id + plain INSERT into `ph_task`, sets
  `assigned_user_team='ebay_priors'`. (Housekeeping: DB password currently in plaintext — move to a secret.)

## 9 · Reconciliation (June 2026, final method)
| Metric | Value |
|---|---|
| Rows | 22 (12 accounts × their marketplaces) |
| Revenue (order_total, Completed) | £95,455.18 |
| Orders / Units | 4,625 / 7,330 |
| ON_SITE Ad Spend / Ad Sales | £7,788.75 / £42,100.97 |
| Overall TACOS | 8.16% |
| Active (per-site) / New / Stock | 12,799 / 248 / 13,579,887 |
| led_sone UK revenue (owner check) | **£28,975.37** ✅ |
| so_926407 UK ON_SITE ad spend (owner check) | **£884.07** ✅ (434 orders / 5,612 clicks / 3,032,285 impr) |

## 10 · Data traps (recorded)
- `order_total` ≠ `item_price*quantity`; `shipping_template_price` over-states postage. Use `order_total`.
- A store's account row is not one marketplace — attribute per `market_place`.
- eBay traffic = `which_channel=2` (numeric code, verify not assume).
- Listing creation dates are in the ledsone DB, not the warehouse.
- Attributed eBay ad sales over-count (multi-campaign attribution) — use TACOS; filter ON_SITE via `ppc`.
- `ph_task` has no real `UNIQUE(task_id)` (ON CONFLICT fails) + a hidden required `assigned_user_team`.
