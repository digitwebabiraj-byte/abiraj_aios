# SYSTEM_REFERENCE — REQ-19 eBay Product Performance Analysis

The authoritative field-by-field map: each of the 35 report columns → real `schema.table.column`,
with the population measured live on 2026-07-27 (warehouse `order_management_copy`).

## Grain & window
- **Grain:** one row per eBay listing = `listing_data` where `which_channel=2 AND all_list=1 AND
  wrong_sku=0 AND is_child=1`, grouped by `(market_place, sub_source_name, ref_id)`. **9,781 rows** (UK+DE).
- **Window:** rolling 30 days ending on the last COMPLETE day (anchor = `CURRENT_DATE-1`), for all flow
  metrics (sales, fees, ad, traffic, shipping). Stock/price/identity are current snapshot.

## Column map

| # | Report column | Source | Grade / note |
|---|---|---|---|
| 1 | Product Image | `listing_data.main_image_url` | 98% |
| 2 | SKU | `listing_data.sku` (rep + variant count) | 100% |
| 3 | Parent SKU | `listing_data.parent_sku` | 83% |
| 4 | eBay Item ID | `listing_data.ref_id` | 100% |
| 5 | Product Title | `inv_products.title` via resolved SKU | 86% |
| 6 | Brand | `salesprot_account_brand_map_v1` by account (pinned; temp_user can't read staging_ai) | 100% |
| 7 | Category | `order_transaction.category_name` else `listing_data.category_id` | 100% (name ~38%, id rest) |
| 8 | Marketplace | `listing_data.market_place` | 100% |
| 9 | Account | `listing_data.sub_source_name` | 100% |
| 10 | Listing Date | `listing_data.created_at` | 100% ⚠ may be ETL date |
| 11 | Listing Status | `all_list=1` ⇒ "Active" | 100% |
| 12 | Selling Price | `listing_data.price` (MAX across variants) | 100% |
| 13 | **Cost Price** | — `sku_cogs` EMPTY | 🔴 NO DATA |
| 14 | Shipping Cost | `order_shipping_billing_detail.carrier_charge` via order_id (per-sale) | populated where sold |
| 15 | eBay Fees | `ebay_order_expenses.fee` where `fee_type NOT IN (AD_FEE,PREMIUM_AD_FEES)` | per-sale; item-level attribution partial |
| 16 | Ad Cost | `ppc_performance.spend` (CPC) + `ebay_order_expenses` AD_FEE/PREMIUM_AD_FEES (CPS) | 100% (0 if not promoted) |
| 17 | VAT | derived: revenue − revenue/(1+rate), rate 20% UK / 19% DE | derived, flagged |
| 18 | Available Stock | `listing_data.quantity` (SUM across variants) | 100% |
| 19 | Units Sold | `order_transaction.quantity` (30d) | 0 if none |
| 20 | Orders | `COUNT(DISTINCT order_transaction.order_id)` (30d) | 0 if none |
| 21 | Revenue | `SUM(order_transaction.order_total)` (30d) | 0 if none |
| 22 | **Gross Profit** | — needs Cost | 🔴 NO DATA |
| 23 | **Net Profit** | — needs Cost | 🔴 NO DATA |
| 24 | **Profit Margin %** | — needs Net Profit | 🔴 NO DATA |
| 25 | Impressions | `traffic_data.impression` (which_channel=2, 30d) | organic |
| 26 | Views | `traffic_data.click` | = Clicks (eBay one metric) |
| 27 | Clicks | `traffic_data.click` | = Views |
| 28 | CTR % | derived: click / impression × 100 | derived |
| 29 | Conversion Rate % | derived: conversion / click × 100 | derived |
| 30 | **Watch Count** | — no table in either DB (eBay Trading API only) | 🔴 NO DATA |
| 31 | Last Sold Date | `MAX(order_transaction.order_date)` | where sold |
| 32 | Days Active | derived: anchor − listing_date | 100% |
| 33 | Promotion Status | Promoted if ad spend > 0 in window, else Not Promoted | 100% |
| 34 | **PPC Campaign** | `ppc.record_name` exists but item→campaign link only 29% in warehouse | 🔴 NO DATA |
| 35 | **Sales Trend** | — undefined business rule (no bands) | 🔴 NO DATA |

## Tables verified present (2026-07-27)
`public.listing_data` · `public.order_transaction` · `public.ebay_order_expenses` ·
`public.order_shipping_billing_detail` · `public.ppc` · `public.ppc_performance` ·
`public.traffic_data` · `public.inv_products` · `public.location_wise_inv_stock` /
`public.inv_final_stock` · `development.sku_cogs` (EMPTY) · `development.channel_vat_log` (EMPTY) ·
`staging_ai.sku_selling_cost_rates_v1` (11,074 rows, selling-cost %, not COGS) ·
`staging_ai.salesprot_account_brand_map_v1` (39 rows).

## Reconciliation (30-day window)
Revenue attached to active listings: **UK £54,286.40 · DE €25,340.97** ≈ 93–94% of the full eBay
UK+DE window total (UK £58,402 · DE €26,876); the remainder is sales from now-inactive listings.

## To reach a full profit report
Need a **product Cost Price** (COGS) source — `ledsone.inventory` once reachable, or a figure from
Thinesh. That single input unlocks columns 13, 22, 23 and 24.
