# Data Availability Audit — REQ-16 eBay Slow Moving & No Moving Products

**Date:** 2026-07-22 · **Developer:** abiraj · **Method:** read-only, live, both databases
**Verdict:** 🟢 **GREEN with three disclosed gaps** — 19 of 20 columns and 11 of 12 rules are
obtainable. One column (`Watchers`) has no source anywhere and one rule (Rule 10) is structurally
unreachable.

---

## 1. Headline finding — this report needs TWO databases

**Neither database can build this report alone.** This was tested, not assumed.

| Source | Supplies | Fatal missing piece |
|---|---|---|
| **`ledsone`** (Ledsone DB MCP / psycopg2) | Title, category breadcrumb, image, price, stock, sales, PPC incl. SMART | **Views + Conversion Rate** — `traffic_data` does not exist in this DB |
| **`order_management_copy`** (warehouse / Postgres MCP) | Views, Conversion, sales, stock, image, category_id, PPC (90d) | **Product Title — only 8.3% populated** (890 of 10,739 in-scope items) |

### 1.1 Warehouse-only test (measured)

| Column | Warehouse `public.listing_data` | Verdict |
|---|---|---|
| Product Title | **890 / 10,739 items = 8.3%** | ❌ **fatal** — 91.7% would ship blank |
| Category | 10,739 / 10,739 — but a bare numeric `category_id` (`117503`, `20708`) | ⚠ degraded vs `ledsone`'s readable breadcrumb |
| Image | 10,615 / 10,739 | ✅ |
| Price · Stock · `is_ended` · `created_at` | 0% missing, refreshed 2026-07-22 | ✅ |
| Sales | `order_transaction` from **2017-09-13**; 15,871 rows in the 90d window, 19,114 in the year-ago window | ✅ |

A merchandiser cannot action "End Listing" on a row with no product name. **The warehouse cannot be
the sole source.**

### 1.2 Why this matters beyond this project

A first-pass audit that searched **only** the `ledsone` DB concluded eBay Views, Conversion Rate and
Watchers were all unavailable. **Two of those three were wrong** — Views and Conversion exist in the
warehouse. Any future eBay project needing traffic metrics must read the warehouse; any project
needing listing text must read `ledsone`.

---

## 2. Evidence Map — all 20 output columns

| # | Column | Source | Grade |
|---|---|---|---|
| 1 | Image | `ledsone` `listings.ebay_listings.main_image_url` | VERIFIED |
| 2 | Account | derived — `order_management.sub_source.map_name` + `ebay_listings.site` | VERIFIED |
| 3 | Brand | derived from the seller account — no brand field exists | PARTIAL |
| 4 | SKU | `ebay_listings.sku` | **PARTIAL** — see §4 (`wrong_sku`) |
| 5 | Item ID | `ebay_listings.item_id` | VERIFIED |
| 6 | Product Title | `ebay_listings.title` — 0% blank in `ledsone` | VERIFIED |
| 7 | Category | `ebay_listings.product_type` (breadcrumb) | VERIFIED |
| 8 | Current Price | `ebay_listings.price` + `.currency` | VERIFIED |
| 9 | Stock | `ebay_listings.quantity` | VERIFIED ⚠ platform-displayed qty, capped by `listing_max_platform_stock` |
| 10–13 | 7 / 30 / 90-day sales + Same Period Last Year | `order_management.orders.order_date` + `order_item_info.real_qty` | VERIFIED |
| 14 | Sales Trend | derived `(col12 − col13)/col13`, live formula | VERIFIED |
| 15 | Days Since Last Sale | anchor − `MAX(order_date)` | VERIFIED ⚠ never-sold → listing age substituted |
| 16 | Views (30 Days) | **warehouse** `public.traffic_data.click` (`which_channel = 2`) | **PARTIAL** — §3 |
| 17 | **Watchers** | **none** | **UNAVAILABLE** — §3 |
| 18 | Conversion Rate | **warehouse** `SUM(conversion)/NULLIF(SUM(click),0)` | **PARTIAL** — §3 |
| 19 | Listing Status | derived from `is_ended` / `end_date` | VERIFIED ⚠ `status` col ~99% NULL, never read directly |
| 20 | Action Required | 12-rule engine, live in-sheet formula | VERIFIED |

**Result: 16 VERIFIED · 3 PARTIAL · 1 UNAVAILABLE.**

---

## 3. The three disclosed gaps

### 3.1 🔴 `Watchers` — no source in either database

Every column in **both** databases was scanned for `watch` / `favorite` / `wishlist` / `saved`. The
only matches are unrelated `watched_status` fields in `staging_ai` internal tables. eBay exposes
Watchers only through its **Trading API**, which is not ingested anywhere.

**Consequence: Rule 6 (Watchers >10 but no 30-day sales) can never fire.** Column 17 ships blank.
It is **not** rendered as `0` — a zero would be a fabricated measurement that could trigger action.

### 3.2 🔴 eBay traffic ingestion lost 11 days

Within 2026-04-23 → 2026-07-22 (91 days) only **78 days** are present.

| Dates | Days | Nature |
|---|---|---|
| 7–11 May 2026 | 5 | outage |
| 26 Jun · 29 Jun – 1 Jul 2026 | 4 | outage |
| 26 Apr · 18 Jul 2026 | 2 | isolated |
| 21–22 Jul 2026 | 2 | normal ~2-day reporting lag, **not** a failure |

**Proven eBay-specific, not a pipeline outage** — Shopify traffic loaded normally on every one of
those dates (e.g. 7 May: eBay 0 rows, Shopify 4,587).

**Root cause is not recorded in either database.** `public.etl_status` covers only the dblink table
copy and only from 2026-07-19; `development.etl_run_log` covers only the `amazon_fbm` weekly
channel. It must be obtained from the ingestion job's own logs.

**Impact:** Views understated ~12% over 90 days and **~23% over the 30-day window** — degrading
Rules 5 and 9, both of which use absolute view thresholds. **Mitigation applied:** Rules 5 and 9 are
evaluated **only** for listings that have traffic rows; absent traffic renders **blank, never zero**.
Collapsing "no data" to `0` would make Rule 9 ("views < 50") fire on every listing the ingestion
missed. **Likely recoverable** by re-running the eBay Analytics pull for those dates.

### 3.3 🟠 eBay PPC — a genuine trade-off, not a simple limit

| Source | Window | Ad-grain spend | Completeness |
|---|---|---|---|
| `ledsone` `ebay_campaigns.performance_data` | **65 days** (from 2026-05-18) | — | **complete, includes SMART** |
| warehouse `public.ppc_performance` | **90 days** (2026-04-24 → 2026-07-21) | £31,481.20 ad grain vs **£39,454.11** campaign grain | **incomplete — £7,973 gap, consistent with SMART omitted at ad grain** |

📌 **Correction to an earlier statement in this project:** a 90-day eBay PPC figure **does** exist —
in the warehouse. The earlier "no 90-day PPC" claim was based only on `ledsone`.

**Build decision: `ledsone` was used** — complete but shorter (Rule 8 runs on a 30-day window, fully
covered by both). This matches the EPPA precedent, which found the warehouse silently omits SMART
campaigns at ad grain.

---

## 4. 🔴 Material finding — 51.7% of in-scope listings carry `wrong_sku = 1`

| `wrong_sku` | Listings | SKU blank | Qty null | Title blank | Avg stock |
|---|---|---|---|---|---|
| 0 | 5,389 | 0 | 0 | 0 | 241.8 |
| **1** | **5,767 (51.7%)** | 0 | 0 | 0 | 178.2 |

**These are real, live, sellable listings.** Sampled rows carry proper titles, prices and stock —
e.g. item `265660320119` "Industrial Wall Light Metal Shade E27 Vintage", 248 units, £18.59. The
flag means the **SKU string is not a clean inventory code** (`ENC979-Wall Light`,
`Small Curvy Wall Sconces` — descriptive text rather than a SKU), so the row will not bridge to
inventory.

**Build decision: `wrong_sku` is NOT filtered.** Excluding it would delete **51.7% of the portfolio**
from a dead-stock report — including listings holding hundreds of units. The warehouse's standing
"always filter `wrong_sku = 0`" rule exists for **SKU→inventory bridging**, a join path this report
does not use (stock comes straight from `ebay_listings.quantity`).

**Disclosure required:** column 4 (SKU) is unreliable for those 5,767 rows, and none of them can be
bridged to warehouse inventory if a future deliverable needs true stock.

---

## 5. Scope reconciliation — the 417-listing difference is EXPLAINED

| Source | Filter | Count |
|---|---|---|
| `ledsone` `listings.ebay_listings` | `is_ended=0 AND is_child=0`, site UK/DE | **11,156** |
| warehouse `public.listing_data` | `is_ended=0 AND wrong_sku=0`, market UK/DE, distinct `ref_id` | 10,739 |

**Not stale data — a grain convention difference.** In warehouse `listing_data`, `is_child = 0`
returns only **890** rows, exactly equal to `is_parent = 1`: sellable rows there are `is_child = 1`.
In `ledsone.ebay_listings`, `is_child = 0` means **parents + singles** (the sellable grain). The two
tables encode the parent/child flags differently, and the warehouse additionally applies
`wrong_sku = 0` — which alone accounts for 5,767 rows (§4). **The counts are not comparable and
neither is wrong.** `ledsone`'s 11,156 is the correct universe for this report.

---

## 6. Scope as built — 12 accounts · 16 account × marketplace · 11,156 listings

| Account | UK | Germany |
|---|---|---|
| LEDSone (`led_sone`) | 2,838 | 1,350 |
| ElectricalSone | 1,505 | 486 |
| SunSone (`so_926407`) | 1,148 | 295 |
| LEDSone DE (`ledsonede`) | 2 | 634 |
| Huettenlampen | — | 542 |
| Coventry Lights | 536 | — |
| Vintage Interior | 474 | — |
| DC Transformer | 467 | — |
| RetroLED (`re6865`) | 403 | — |
| LightingSone | 247 | — |
| Homin GmbH | — | 164 |
| BestBringer | 65 | — |
| **Total** | **7,685** | **3,471** |

**`neighbourmarket` falls out of scope** — a live eBay account with 345 active listings, but
US-only, therefore no UK/DE rows.

---

## 7. Data freshness

| Source | Latest | Coverage in the 90-day window |
|---|---|---|
| Sales (`orders` + `order_item_info`) | **2026-07-22** | **91 / 91 days — complete, zero missing** |
| Listings (`ebay_listings`) | 2026-07-22 | live, refreshed daily |
| Traffic (`traffic_data`) | 2026-07-20 | **78 / 91 days** — see §3.2 |
| PPC (`ebay_campaigns.performance_data`) | 2026-07-22 | 65 days available — see §3.3 |

**Anchor = 2026-07-22**, the latest day for which sales are complete. Traffic lags ~2 days; this is
disclosed on the report and must never be read as zero views.

---

## 8. 🔴 Structural finding — Rule 10 is unreachable

Any listing satisfying **Rule 10** (age > 180 days AND last sale > 90 days ago) necessarily has
**zero 90-day sales**, so **Rule 1 (Critical) always claims it first** under the assumed precedence.

**Rule 10 matched 0 of 11,156 listings.** This is a property of the rule set, not a data fault.
Either the condition needs revising, or Rule 10 should apply only to listings that *did* sell within
90 days. Raised as decision **C**.

---

## 9. Undefined in the source — recorded as assumptions, not decisions

| Item | Source says | Build assumed |
|---|---|---|
| **Rule precedence** | assigns priorities, never states multi-match resolution | Critical → High → Medium → Low, first match wins; lower rule number wins within a band |
| **Rule 8 "PPC Spend High"** | "high" defined nowhere | **> £5.00 over 30 days** with zero 30-day sales |

Both are exposed as editable configuration on the workbook's **Rules** sheet and flagged for
Business Validator confirmation (decisions **C** and **G**). Neither is presented as fact.

---

## 10. Verification performed

| Check | Result |
|---|---|
| Engine implemented **twice independently** (live Excel formulas + Python) and diffed row-by-row | **11,156 / 11,156 identical · 0 mismatches** |
| Formula errors across the entire workbook | **0** |
| Field-by-field live reconciliation, item `164889807930` | 7d **0** · 30d **0** · 90d **1** · SPLY **14** · trend **−92.86%** · idle **77d** · views **18** · CVR **0%** — **exact on every field against both databases** |
| Summary totals vs detail sheet | 11,156 and 8,067 agree; account breakdown sums to the same totals |
| Source sample used as a baseline | **No** — the sample is fabricated and its actions contradict its own rule table |

---

## 11. Verdict

🟢 **GREEN to build** — and built. **REQ-16-D01** produced 11,156 rows: 8,067 Critical (End
Listing), 1,210 Clearance, 851 Price Cut, 476 SEO, 149 Bundle, 42 Competitor Review, 26 Listing
Quality, 2 Pause PPC, 109 Maintain, 53 Grow, 171 Monitor.

**Carried forward as open items:** the `Watchers` decision · the traffic backfill · rule precedence
and the unreachable Rule 10 · the £5.00 Rule 8 threshold · the actionability of a report where
72.3% of rows share one Critical action.
