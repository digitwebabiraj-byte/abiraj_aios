# SYSTEM_REFERENCE — REQ-23 Fast Moving Products

Field-by-field map: each report column → its intended source. **DRAFT — not yet verified live against
`ledsone` / warehouse.** Sources below are the *expected* homes carried in from prior projects
(EPPR / DST / ppc-stock-lookup); each must be confirmed in discovery before the builder trusts it, and
each row updated with a real `schema.table.column` + coverage %.

## Grain, window & scope (to confirm with Mahima)
- Grain: one row per **channel × ranked SKU** (top N). Combined table: one row per **base SKU**.
- Window: source shows a **calendar month** (01–31 Jul 2026) with **30-day AND 90-day** sold-qty columns.
  Confirm fixed-month vs rolling 30/90-day and the anchor day.
- Scope: **DE** market, 3 channels. Money in **€**, never blended with other currencies.

## Per-channel column map (draft — Shopify DE / Amazon DE / eBay DE share this shape)
| # | Column | Expected source | Note / risk |
|---|---|---|---|
| 1 | Rank | derived (rank by Sold Qty desc) | ranking metric to confirm (30d qty? revenue?) |
| 2 | SKU | listing / order-line SKU (`listing_data`, `all_list=1`, clean SKU) | clean-SKU step; eBay SKU sprawl |
| 3 | Product ID | Shopify=product/item id · Amazon=**ASIN** · eBay=**Listing ID** | per-channel identifier |
| 4 | Product Name | listing title (parent row `all_list=0` — the EPPR trap) | Shopify table omits it in the source |
| 5 | Category | listing / product category | confirm the category source & taxonomy |
| 6 | Sold Qty (30 Days) | orders units, `which_channel` = 1/2/3, last 30d | eBay: attribute by item_id, not SKU |
| 7 | Sold Qty (90 Days) | orders units, same, last 90d | side-by-side velocity comparison |
| 8 | Sales Revenue € | order line `item_price × qty` (CAST VARCHAR), DE=€ | **per marketplace currency** |
| 9 | Orders | distinct order count for the SKU/window | |
| 10 | Avg Order Qty | derived = Sold Qty ÷ Orders | |
| 11 | Current Stock | `location_wise_inv_stock` via `listing_data` bridge, DE location | ppc-stock-lookup clean-SKU step |
| 12 | Stock Cover Days | derived = Current Stock ÷ **Avg Daily Sales** | define the daily-sales denominator |
| 13 | Trend | derived classification (Growing/Stable/Slow) | **business rule — define with Mahima** |
| 14 | Action | derived rule engine (Maintain/Promote/Reorder/…) | **thresholds — define with Mahima** |

## Combined table — "Final Combined Top Products (All Channels)"
| # | Column | Expected source | Note |
|---|---|---|---|
| 1 | Overall Rank | derived (rank by Total Units) | |
| 2 | SKU | **clean base SKU** (roll-up key across channels) | never a per-channel Product ID |
| 3 | Category | as above | |
| 4 | Amazon sold Qty | channel 1 units for the SKU | |
| 5 | eBay sold Qty | channel 2 units (item_id-attributed) | SKU-sprawl trap |
| 6 | Shopify sold Qty | channel 3 units | |
| 7 | Total Units Sold | derived = sum of the three | |
| 8 | Total Revenue (€) | derived = sum of per-channel € revenue | **€ only — do not blend other currencies** |
| 9 | Current Stock | `location_wise_inv_stock` for the base SKU | |
| 10 | Stock Cover | derived = Current Stock ÷ Avg Daily Sales (combined) | define denominator |
| 11 | Final Decision | derived rule engine (Restock immediately / Increase production / Maintain / …) | thresholds to define |

## Key rules to apply (AIOS KB — read before SQL)
- **Multi-domain** (Orders + Stock) → `text-to-sql-multi`; stock via `ppc-stock-lookup` (which_channel 1/2/3).
- Channels: Amazon `which_channel=1`, eBay `which_channel=2`, Shopify `which_channel=3`.
- eBay: `source_id=2`; attribute by order_id/item_id, never SKU alone.
- `all_list=1` for real SKUs; title/image on the parent row (`all_list=0`).
- `order_item_info.item_price` / `item_quantity` are VARCHAR → CAST.
- Stock: `listing_data` bridge (wrong_sku → mapped_sku → clean-SKU) → `location_wise_inv_stock`, DE location.
- Money per marketplace currency; no FX table (the DST currency trap).

## Open source questions (blockers for the builder)
1. **Average Daily Sales** denominator behind Stock Cover Days.
2. **Trend** classification rule and **Action / Final Decision** thresholds.
3. **Category** authoritative source and taxonomy.
4. Fixed-month vs rolling 30/90-day window + anchor.
5. Which DE **location(s)** define "Current Stock".

> Everything above is a **starting hypothesis**. Replace each row with a confirmed `schema.table.column`
> + coverage % after the live discovery sweep, exactly as EPPR's did.
