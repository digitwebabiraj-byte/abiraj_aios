# SYSTEM_REFERENCE — eBay UK Top 50 Sales Drop (esdt) · PRJ-2026-023 / REQ-26

Complete functional detail: what the report is, the exact column → source map, and the logic behind every
derived field. **Status: DESIGN reference (2026-08-12) — no builder exists yet.** All source mappings below
are *planned* from proven prior-project patterns and are marked `TO VERIFY` until reconciled live. Where no
truthful source exists a cell must render a documented sentinel, never a guess.

## 1. What the system will produce
The Top-50 eBay UK SKUs by sales loss, current vs previous equal period, rendered as one data layer / two files:
- **Excel** `REQ-26-D01_ebay_top50_sales_drop.xlsx`: `Notes & Method` tab + `Top 50 Sales Drop` table (14 cols).
- **HTML dashboard** `REQ-26-D01_ebay_top50_sales_drop.html`: KPI tiles + Priority filter + sortable table + CSV export.

Row order: **absolute £ loss descending** (largest loss = Rank 1), tie-break Drop % descending.

## 2. Universe & filter logic (workflow PDF §4–5)
1. Compute current and previous sales per SKU over two equal, adjacent date ranges.
2. Sales Drop % = (Current − Previous) ÷ Previous × 100.
3. **Exclude** SKUs with **no previous-period sales** (division undefined / not a "drop").
4. **Exclude** SKUs where sales **increased or held** (keep only Loss £ < 0, i.e. Current < Previous).
5. **Rank** remaining by Loss £ (largest first); tie-break Drop %; take **Top 50**.

## 3. Column → source map (14 columns) — ✅ VERIFIED LIVE 2026-08-12

All sources confirmed against the live raw DB via `Ledsone-db-mcp`. **Everything is in ONE database** —
the earlier "two-DB join" risk is void: `business_reports.ebay_traffic_data` (organic) and
`ebay_campaigns.listing_performance` (PPC) sit alongside orders/listings/inventory.

**Account & scope keys (verified):** ELECTRICALSONE eBay sales = `order_management.orders.sub_source_id = 22`
(`sub_source.name='electricalsone'`, `source_id=2`); **eBay UK = `orders.market_place = '23'`** (proven: those
orders join to `ebay_listings.site='UK'`). Germany = '10'. Data is **live to 2026-08-11** (orders) / **-08-10**
(traffic) / **-08-12** (PPC).

| # | Column | Verified source / derivation | Coverage (last 60d, UK) |
|---|---|---|---|
| 1 | **Rank** | Row number after sort (Loss £ desc, then Drop % desc) | derived |
| 2 | **SKU** | `order_management.order_item_info.item_sku` | 700 SKUs |
| 3 | **Item ID** | `order_item_info.item_id` = `listings.ebay_listings.item_id` | **100%** (57,963/57,963 lines) |
| 4 | **Product** | `ebay_listings.title` (join on `item_id`); ⚠ parent/child rows share `item_id` — take the parent (`is_parent=1`/`all_list`) title | via item_id |
| 5 | **Previous Sales £** | SUM `orders.total` (or line `item_price`×`item_quantity`), UK completed, **previous** window | live |
| 6 | **Current Sales £** | SUM `orders.total`, UK completed, **current** window | live |
| 7 | **Loss £** | Current − Previous (negative = loss) | derived |
| 8 | **Drop %** | (Current − Previous) ÷ Previous × 100 | derived |
| 9 | **CTR** | `business_reports.ebay_traffic_data` (`site_code='EBAY-GB'`): `ctr` (or `clicks?`/`impressions`); join `ebay_traffic_data.item_id = order_item_info.item_id` | **100%** of item_ids have traffic |
| 10 | **CVR** | `ebay_traffic_data`: `quantity_sold ÷ ebay_views` (STR/conversion); per item_id/day | via item_id |
| 11 | **ROAS** | `ebay_campaigns.listing_performance.return_on_ad_spend` (pre-computed) or `sale_amount_listing_currency ÷ ad_fees_listing_currency`; **join `listing_performance.ebay_listing_id::text = order_item_info.item_id`** (this column holds the eBay item number, NOT `ebay_listings.id`) | **91%** (292/321 item_ids); £2,415.52 spend / £19,509.98 sales |
| 12 | **Stock** | `inventory.products.sku` → `local_inventory_current_stock_location_wise.stock` (also `ebay_listings.quantity` for platform stock) | **99.1%** (694/700 SKUs) |
| 13 | **Priority** | DERIVED — alert band from Drop % (§4) | derived |
| 14 | **Action** | DERIVED — reason/diagnosis rule engine (§5) | derived |

Diagnostic inputs the PDF §2/§7 lists (Units, Impressions, Clicks, PPC Sales, PPC Spend, ACOS) all exist in
the same tables (`ebay_traffic_data.impressions/ebay_views`, `listing_performance.impressions/clicks/
ad_fees_listing_currency/sale_amount_listing_currency`) — carry them on an audit sheet feeding the 14 headline cols.

### Verified traps (measured, not assumed)
- **Multi-SKU listings (confirmed):** 700 SKUs across only **321 Item IDs** — each listing carries several
  variation SKUs. The **ranking grain (SKU vs Item ID) is a real business choice** (open item #3), not cosmetic.
- **PPC £0-spend rows (confirmed, eppa trap):** only 4,033 of 21,973 PPC rows have non-zero spend (ON_SITE/CPS
  impressions logged at £0). Aggregate spend is real, so item-level ROAS is meaningful; guard per-row ÷0.
- **9% unadvertised / 0.9% no-stock:** render **`n/a` / NO DATA**, never a guess.
- **PPC join key gotcha:** `listing_performance.ebay_listing_id` = the eBay item number (join on `item_id`),
  NOT `ebay_listings.id`. Joining on `ebay_listings.id` returns 0 rows.

## 4. Priority band (workflow PDF §6 — PROVISIONAL, pending Kobiga)
| Drop % | Priority |
|---|---|
| ≥ 50% | 🔴 Critical |
| 30–49.99% | 🟠 High |
| 15–29.99% | 🟡 Medium |
| < 15% | 🟢 Stable |

## 5. Reason / Action rule engine (workflow PDF §8 — PROVISIONAL, pending Kobiga)
| Condition | Reason | Action (example) |
|---|---|---|
| Sales ↓ & Impressions ↓ | Visibility / SEO issue | SEO + PPC review |
| Impressions ~flat & CTR ↓ | Title / main-image issue | Listing (title/image) review |
| Clicks ~flat & Conversion ↓ | Price / listing / offer issue | Price + offer review |
| PPC Spend ↓ & PPC Sales ↓ | Advertising visibility issue | PPC review |
| Stock = 0 | Stock issue | Restock |
| Sales ↓ & competitor price lower | Pricing review required | Price review |

The Excel/PDF sample Actions ("SEO + PPC Review", "Listing Review") are the target vocabulary — confirm the
final wording and precedence with Kobiga.

## 6. Data sources — ✅ ONE raw DB (`mcp.ledsone.co.uk/mcp`, via `Ledsone-db-mcp`)
Verified 2026-08-12: every column resolves from a single raw Postgres. No warehouse cross-DB join needed.
| Domain | Schema.table | Key |
|---|---|---|
| Sales / units | `order_management.orders` + `order_item_info` + `sub_source` | `sub_source_id=22`, `market_place='23'` (UK) |
| Listing (Item ID, title, price, image, category, status) | `listings.ebay_listings` (+ `ebay_listings_parent_child_mapping`) | `item_id` |
| Organic traffic (impressions, views, CTR, STR) | `business_reports.ebay_traffic_data` | `item_id` / `site_code='EBAY-GB'` |
| PPC (spend, sales, ROAS, ACOS, CPC, CVR) | `ebay_campaigns.listing_performance` (+ `campaigns` for account/marketplace) | `ebay_listing_id`(=item number) |
| Stock | `inventory.products` → `local_inventory_current_stock_location_wise` | `sku` → `inventory_id` |

- The AIOS knowledge base MCP is `docs.ledsone.co.uk/mcp` (an MCP endpoint, not an HTTP page — 404 on plain
  fetch). The raw-data MCP is `mcp.ledsone.co.uk/mcp` (the `Ledsone-db-mcp` `execute_sql` used above).

## 7. Open items (do not resolve by guessing — workbench stop-condition)
1. Scope (ELECTRICALSONE only vs all eBay UK accounts).
2. Period length / cadence / anchor date.
3. Ranking grain (SKU vs Item ID) given the 89% multi-SKU listings.
4. Alert thresholds (confirm 50/30/15%).
5. Reason/Action vocabulary (Kobiga's own list).
6. CPS £0-spend handling for ROAS/ACOS.
7. Publish audience + automation cadence.

## 8. Reproduce (once built — placeholder)
```
set LED_PGHOST/LED_PGUSER/LED_PGPASSWORD/LED_PGDATABASE/LED_PGPORT   # git-ignored shared store
set WH_PG* (warehouse traffic_data)                                  # git-ignored shared store
python sql/REQ-26_ebay-top50-sales-drop/build_esdt_d01.py
```
Will write a payload snapshot + both outputs into `evidence/final_outputs/REQ-26_ebay-top50-sales-drop/`.
