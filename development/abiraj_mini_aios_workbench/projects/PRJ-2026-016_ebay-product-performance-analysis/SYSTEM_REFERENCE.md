# SYSTEM_REFERENCE — REQ-19 eBay Product Performance Analysis

Field-by-field map: each of the 35 columns → real source. Built from **raw `ledsone`** (source of record)
+ the **warehouse** for the organic-traffic feed only. Measured live 2026-07-27.

## Grain & window
- One row per eBay listing (item_id): `listings.ebay_listings` `all_list=1 AND is_ended=0 AND wrong_sku=0
  AND site IN ('UK','Germany')`, grouped by item_id → **11,123 rows**.
- ⚠ **Title/image/type/parent live on the PARENT row (`all_list=0`)** — a separate `meta` CTE takes them
  over ALL rows per item_id, else Title is only ~8%.
- Window: rolling 30 days ending the last complete day, for all flow metrics.

## Column map
| # | Column | Source | Note |
|---|---|---|---|
| 1 | Product Image | `ebay_listings.main_image_url` (meta) | 100% |
| 2 | SKU | `ebay_listings.sku` (`all_list=1`) + variant count | 100% |
| 3 | Parent SKU | `ebay_listings.parent_sku` (meta) | 74% |
| 4 | eBay Item ID | `ebay_listings.item_id` | 100% |
| 5 | Product Title | `ebay_listings.title` (meta, parent row) | ~99% |
| 6 | Brand | account store-brand map (`BRAND_MAP`) | 100% |
| 7 | Category | `ebay_listings.product_type` else `category_id` | 100% (real names) |
| 8 | Marketplace | `ebay_listings.site` (UK/Germany) | 100% |
| 9 | Account | `order_management.sub_source.name` (source_id=2) | 100% |
| 10 | Listing Date | `ebay_listings.created_at` (all_list=1) | 100% |
| 11 | Listing Status | `all_list=1 & is_ended=0` ⇒ Active | 100% |
| 12 | Selling Price | `ebay_listings.price` (MAX per item) | 100% |
| 13 | **Cost Price** | **ESTIMATE = 20% × Selling Price** (owner decision) | 🟠 estimate |
| 14 | Shipping Cost | `order_management.orders.shipping_cost` via order lines | per-sale |
| 15 | eBay Fees | `accounting.ebay_order_expenses.fee` (non-ad fee_types) | per item_id |
| 16 | Ad Cost | `ebay_campaigns.performance_data.ad_fees_payout_currency` (CPC) + `ebay_order_expenses` AD_FEE/PREMIUM (CPS) | ebay_listing_id = item_id |
| 17 | VAT | derived: revenue − revenue/(1+rate), 20% UK / 19% DE | derived |
| 18 | Available Stock | `ebay_listings.quantity` (SUM per item) | 100% |
| 19 | Units Sold | `order_item_info.item_quantity` (30d, source_id=2, not Cancelled/Deleted) | 0 if none |
| 20 | Orders | `COUNT(DISTINCT order_id)` (30d) | 0 if none |
| 21 | Revenue | `SUM(item_price×item_quantity)` (30d, CAST VARCHAR) | 0 if none |
| 22 | **Gross Profit** | derived: Revenue − Cost×Units | 🟠 estimate (via #13) |
| 23 | **Net Profit** | derived: Gross − Fees − Ad − Shipping − VAT | 🟠 estimate |
| 24 | **Profit Margin %** | derived: Net ÷ Revenue (where Revenue>0) | 🟠 estimate |
| 25 | Impressions | **warehouse** `traffic_data.impression` (which_channel=2) | organic |
| 26 | Views | warehouse `traffic_data.click` | = Clicks |
| 27 | Clicks | warehouse `traffic_data.click` | eBay one metric |
| 28 | CTR % | derived: click/impression×100 | |
| 29 | Conversion Rate % | derived: conversion/click×100 | |
| 30 | **Watch Count** | — no source in either DB (eBay Trading API only) | 🔴 NO DATA |
| 31 | Last Sold Date | `MAX(order_date)` (30d) | where sold |
| 32 | Days Active | derived: anchor − listing_date | 100% |
| 33 | Promotion Status | Promoted if ad spend / running campaign, else Not Promoted | 100% |
| 34 | PPC Campaign | `ebay_campaigns.ads`→`campaigns.campaign_name` (ebay_listing_id=item_id) | ~65% |
| 35 | **Sales Trend** | — undefined business rule (no bands) | 🔴 NO DATA |

## Key ledsone rules applied (AIOS KB)
- `all_list=1` mandatory for real SKUs; title/image on the parent row (`all_list=0`).
- eBay orders isolated with `sub_source.source_id=2` (else Shopify item_ids leak in).
- `order_item_info.item_price` / `item_quantity` are VARCHAR → CAST.
- `ebay_campaigns.*.ebay_listing_id` = the eBay item_id (numeric) — the join key for ad/campaign.

## Cost / profit = estimate
No real per-SKU COGS exists (`inventory.products` has no cost; `sku_cogs` empty; `suppliers.invoices.unit_price`
not SKU-keyed). Owner decision 2026-07-27: **Cost Price = 20% of Selling Price**; Gross/Net/Margin derived
and flagged as estimates on every artefact.

## Reconciliation
Revenue on active listings (30d): UK £59,526 · DE €26,634. Per currency, never blended.
