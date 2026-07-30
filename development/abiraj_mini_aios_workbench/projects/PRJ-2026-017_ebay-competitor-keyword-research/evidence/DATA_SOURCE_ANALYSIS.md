# REQ-20 — Data-Source Feasibility Analysis

**Project:** PRJ-2026-017 eBay Competitor & Keyword Research
**PH / owner:** Jarsini (eBay `ebay_priors` user)
**Source brief:** `evidence/source_documents/REQ-20_.../Jarsini_task_source.xlsx`
**Analysed:** 2026-07-30 against **live** warehouse (`public.listing_data` etc.) + raw ledsone DB.

## The brief (14 columns)

Product Name · SKU · Competitor ID · Brand · Title · Sold Quantity · Price ·
Feedback Rate · Shipping type · Promotion Type & % · Primary Keywords ·
Secondary Keywords · Long-Tail Keywords · Notes

Legend from the brief: Primary = main product name (1–5 words); Secondary = related
terms/synonyms; Long-Tail = detailed buyer phrases; Brand = official manufacturer name.

## Verdict: this is a competitor-intelligence + keyword-research task, NOT an internal-SQL report

Every prior AIOS project read our OWN data from the DB. This one is fundamentally different:
the bulk of the columns describe **competitor eBay listings** and **keyword research**, neither
of which lives in our databases.

### Live-DB probe results (verified, not assumed)

| Search | Result |
|--------|--------|
| `%competitor%` tables | **0 found** |
| `%promotion% / %markdown% / %discount%` tables | **0 found** |
| `%keyword%` tables | only `google_ads.keywords`, `google_ads.keyword_performance`, `listings.amazon_listing_search_engine_keywords` — Google/Amazon only, **no eBay** |
| `%feedback%` tables | `customer_service.ebay_orders_customer_feedbacks` = feedback on **OUR** orders; `customer_service.ebay_account_ratings` = **OUR** account rating (account-level) |
| `%brand%` columns | only `google_ads.merchant_products.brand` + amazon; **no brand on `ebay_listings` / `listing_data`** |
| `%shipping%` on listings | none — only customer address & supplier invoice & per-order `shipping_method` |

### Column-by-column source map

| # | Column | In live DB? | Source / method |
|---|--------|-------------|-----------------|
| 1 | Product Name | ✅ own | `listings.ebay_listings.title` |
| 2 | SKU | ✅ own | `ebay_listings.sku` / `parent_sku` |
| 3 | Competitor ID | ❌ DB → ✅ **eBay live scrape** | item id from eBay search/listing URL |
| 4 | Brand | ⚠️ | not in DB for eBay; **from competitor eBay item specifics** when scraping |
| 5 | Title | ✅ own / ✅ scrape | own `ebay_listings.title`; competitor from listing |
| 6 | Sold Quantity | ⚠️ | own `ebay_listings.quantity_sold`; competitor **only when eBay displays "X sold"** (often blank) |
| 7 | Price | ✅ own / ✅ scrape | own `ebay_listings.price`; competitor from listing |
| 8 | Feedback Rate | ⚠️ | own = `ebay_account_ratings` (account-level); competitor = seller "% positive" from listing |
| 9 | Shipping type | ❌ DB → ✅ scrape | from eBay listing postage line (**must force delivery country = UK**) |
| 10 | Promotion Type & % | ❌ DB → ✅ scrape | eBay listing promo line ("Save up to 10% with Multi-buy", "coupon") |
| 11 | Primary Keywords | ❌ DB → ✅ **generated** | keyword research from product name/type |
| 12 | Secondary Keywords | ❌ DB → ✅ generated | synonyms / related terms |
| 13 | Long-Tail Keywords | ❌ DB → ✅ generated | buyer search phrases |
| 14 | Notes | — | manual |

## Capability decision

Filling this report needs a **new capability** vs the SQL-only stack: **live eBay scraping**
(browser) for competitor columns, plus **AI keyword generation**. Proven working in POC
(see `evidence/logs_or_screenshots/`).

### Confirmed gotchas from the POC (2026-07-30)

1. **Own-listing contamination** — an eBay keyword search for our products returns OUR OWN
   listings first (`led_sone`, `electricalsone`, etc.). Must exclude our 14 eBay seller accounts
   or "competitors" = ourselves. (See store list in `listing_data` reference.)
2. **Delivery-country trap** — browser geolocated to Sri Lanka → eBay quoted GSP international
   postage (£82.15). Shipping figures are WRONG unless delivery country is forced to **UK**.
3. **Sold Quantity often absent** — eBay only shows "X sold" with recent sales; exact competitor
   sold qty is frequently not exposed anywhere. Capture when shown, blank otherwise.
4. **Brand** lives in eBay **item specifics** ("Brand: CAN"), parsed from the listing body, not a
   card field.

## Scope (locked with Abiraj 2026-07-30)

9 product categories: Cone metal pendant light · Wall Light · Metal shade Ceiling Light ·
Glass shade ceiling light · Spider Light · Cage pendant light · Pipe Light · Bulbs · Lamp Holder.
