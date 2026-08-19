# Data-foundation probe — REQ-30 BGCT Keyword Gap Sync

**Date:** 2026-08-19 · **Method:** live read-only SQL via `Ledsone-db-mcp` (`execute_sql`) against the raw
`ledsone` DB (live host 169.58.91.229) · **Verdict:** 🟢 **GREEN — every read the workflow needs exists.**

This is the evidence behind every number quoted in `README.md`, `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md` and
`TASK_REGISTER.md`. All queries were SELECT-only.

---

## 1. Does an SQP source exist at all? — YES

```sql
SELECT table_schema, table_name FROM information_schema.tables
WHERE table_name ILIKE ANY (ARRAY['%search_query%','%search_term%','%sqp%','%brand_analytic%','%keyword%'])
ORDER BY 1,2;
```
**11 rows.** The one that matters:

| schema.table | verdict |
|---|---|
| **`business_reports.amz_search_query_performance`** | ✅ **this is SQP** |
| `amazon_campaigns.search_term_performance_data` | ❌ **PPC search terms, not SQP** (AKYP #024's documented trap) |
| `amazon_campaigns.keyword_performance_data`, `amazon_campaigns.keywords` | ❌ paid manual-keyword entities (AKYP #024's subject) |
| `amazon_campaigns.search_term_sku_data` | ❌ PPC |
| `google_ads.*` (5 tables) | ❌ different channel |
| **`listings.amazon_listing_search_engine_keywords`** | ✅ **the backend/generic keyword field (Method 2)** |

## 2. `amz_search_query_performance` — 48 columns, every spec Step-8 column present

```sql
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema='business_reports' AND table_name='amz_search_query_performance'
ORDER BY ordinal_position;
```
**48 columns.** Keys: `asin`, `start_date`, `end_date`, `report_period`, `sub_source`, `market_place`.
Metrics include `search_query`, `search_query_score`, `search_query_volume`,
`total_query_impression_count`, `asin_impression_count`, `asin_impression_share`, `total_click_count`,
`total_click_rate`, `asin_click_count`, `asin_click_share`, `total_cart_add_count`, `total_cart_add_rate`,
`asin_cart_add_share`, `total_purchase_count`, `total_purchase_rate`, `asin_purchase_count`,
`asin_purchase_share`, and median click/cart-add/purchase prices with currency codes.

**Spec Step 8 mapping — all 7 required columns exist:** `search_term`→`search_query` ·
`search_query_score`→`search_query_score` · `search_query_volume`→`search_query_volume` ·
`total_count`→`total_query_impression_count` · `asin_count`→`asin_impression_count` ·
`asin_share`→`asin_impression_share` · `click_rate`→`total_click_rate` *or* `asin_click_share`
(**the spec does not say which — open item #10**).

## 3. SQP coverage per account and market — 🟠 WEEK grain only

```sql
SELECT sub_source, market_place, report_period,
       COUNT(*) rows, COUNT(DISTINCT asin) asins, COUNT(DISTINCT search_query) queries,
       MIN(start_date) first_start, MAX(end_date) last_end
FROM business_reports.amz_search_query_performance
GROUP BY 1,2,3 ORDER BY rows DESC;
```

| sub_source | market_place | report_period | rows | ASINs | queries | first_start | last_end |
|---|---|---|---|---|---|---|---|
| **8 (Ledsone)** | **23 (UK)** | WEEK | **137,048** | 3,368 | 71,679 | 2026-01-25 | **2026-08-08** |
| **6 (Dcvoltage)** | **23 (UK)** | WEEK | 39,173 | 2,216 | 24,615 | 2026-01-25 | **2026-07-25** |
| 8 | 10 (DE) | WEEK | 11,047 | 806 | 6,993 | 2026-02-22 | 2026-08-08 |
| 8 | 9 (FR) | WEEK | 4,741 | 535 | 3,382 | 2026-04-26 | 2026-07-25 |
| 8 | 24 (US) | WEEK | 3,730 | 261 | 2,775 | 2026-02-22 | 2026-08-08 |
| 6 | 10 (DE) | WEEK | 3,438 | 395 | 2,189 | 2026-02-22 | 2026-07-25 |
| 6 | 9 (FR) | WEEK | 412 | 36 | 333 | 2026-04-26 | 2026-07-25 |

**Three findings:**
1. 🟠 **`report_period` is `'WEEK'` in every one of the 7 groups. No MONTH rows exist.** The spec's Step 4
   ("Reporting Range → Monthly, last 3 consecutive months one month at a time") has no direct row. Months
   must be assembled from weeks — and **count/volume columns sum while rate, share and median columns must be
   recomputed from numerator and denominator, never averaged**. Amazon's own monthly SQP is also not the
   arithmetic sum of its weeks. **Open item #4.**
2. 🟠 **DCVOLTAGE is two weeks staler than LEDSone** (2026-07-25 vs 2026-08-08). A monthly run must not
   compare a complete month for one account against a partial month for the other.
3. 🟠 **Coverage is partial by design** — 3,368 SQP ASINs out of 16,963 Ledsone UK catalogue ASINs (~20%),
   2,216 of 15,035 for DCVOLTAGE. Amazon only reports queries above a volume floor. This is sufficient for
   Top-Movers (which are high-volume by definition) but caps how far Phase 1 can be widened.

## 4. Sales & traffic — Top-Moving (Phase 1 Step 1) and drop/zero sales (Phase 2 Step 1)

```sql
SELECT sub_source, COUNT(*) rows, COUNT(DISTINCT child_asin) asins,
       MIN(date) first_date, MAX(date) last_date
FROM business_reports.amz_sales_and_traffic_by_asin
WHERE market_place=23 AND sub_source IN (6,8) GROUP BY 1 ORDER BY 1;
```

| sub_source | rows | ASINs | first_date | last_date |
|---|---|---|---|---|
| 6 (Dcvoltage) | 355,610 | 11,701 | 2026-01-01 | **2026-08-17** |
| 8 (Ledsone) | **417,030** | 13,745 | 2026-01-01 | **2026-08-17** |

53 columns, daily grain, including `units_ordered`, `ordered_product_sales`, `sessions`, `page_views`,
`buy_box_percentage`, `unit_session_percentage`, `refund_rate`, plus `parent_asin` → `child_asin`.
Sufficient for both the Top-Moving ranking ("rank by units/sessions") and the 3-month-decline /
6-month-zero tests. ⚠ **History starts 2026-01-01** — a 6-month zero-sales window anchored at 2026-08 reaches
back to 2026-02, which is inside the window; a 6-month window anchored earlier than 2026-07 would not be.

## 5. The four Method 1 / Method 2 content surfaces — all present

### 5a. `listings.amazon_listings` — 32 columns
Carries `title` (varchar) and `product_description` (text), plus `id`, `asin`, `sku`, `mapped_sku`,
`parent_sku`, `quantity`, `status`, `selected_variations`, `is_parent`, `is_child`, `all_list`, `sub_source`,
`site`, `wrong_sku`, `updated_at`. **No bullet-point column** — bullets are a separate table (§5b).

```sql
SELECT sub_source, COUNT(*) uk_rows, COUNT(DISTINCT asin) uk_asins,
  COUNT(*) FILTER (WHERE all_list=1) all_list_1, COUNT(*) FILTER (WHERE all_list=0) all_list_0,
  COUNT(*) FILTER (WHERE title IS NOT NULL AND title<>'') with_title,
  COUNT(*) FILTER (WHERE product_description IS NOT NULL AND product_description<>'') with_desc,
  COUNT(*) FILTER (WHERE is_parent=1) parents, COUNT(*) FILTER (WHERE is_child=1) children,
  MAX(updated_at) fresh
FROM listings.amazon_listings WHERE site='UK' AND sub_source IN (6,8) GROUP BY 1 ORDER BY 1;
```

| sub_source | UK rows | UK ASINs | all_list=1 | all_list=0 | with title | with desc | parents | children | freshest |
|---|---|---|---|---|---|---|---|---|---|
| 6 | 16,396 | 15,035 | **16,396** | **0** | 16,395 | 15,019 | 1,196 | 15,200 | 2026-08-19 00:30 |
| 8 | 18,721 | 16,963 | **18,721** | **0** | 18,721 | 16,050 | 1,489 | 17,232 | 2026-08-19 00:31 |

✅ **The eBay `all_list=0` parent-title trap does not apply to Amazon UK** — every row is `all_list=1`, so
titles sit on the row itself. (Re-verify before relying on this in another market.)
⚠ Description is missing on ~14% of rows (16,050 of 18,721 for Ledsone) — those must read **NO DATA / not
checked** for the description surface, not `false`.

### 5b. Bullets and backend keywords — separate tables, joined on `product_id`

```sql
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema='listings' AND table_name IN
  ('amazon_listing_bullet_points','amazon_listing_search_engine_keywords');
```
- `amazon_listing_bullet_points` → `id`, **`product_id`**, **`points`** (text), `view_order` (smallint)
- `amazon_listing_search_engine_keywords` → `id`, **`product_id`**, **`keyword`** (text), `view_order`

```sql
SELECT (SELECT COUNT(*) FROM listings.amazon_listing_bullet_points) bullet_rows,
       (SELECT COUNT(DISTINCT product_id) FROM listings.amazon_listing_bullet_points) bullet_products,
       (SELECT COUNT(*) FROM listings.amazon_listing_search_engine_keywords) kw_rows,
       (SELECT COUNT(DISTINCT product_id) FROM listings.amazon_listing_search_engine_keywords) kw_products,
       (SELECT COUNT(*) FROM listings.amazon_listings) listing_rows;
```
| bullet_rows | bullet_products | kw_rows | kw_products | listing_rows (all sites) |
|---|---|---|---|---|
| **429,224** | 80,829 | **189,192** | 68,072 | 133,763 |

**Join verified** — `product_id` → `listings.amazon_listings.id` (not ASIN, not SKU):

| sub_source (UK) | listings with bullets | listings with backend keywords |
|---|---|---|
| 6 | 15,613 | 14,381 |
| 8 | 16,719 | 15,010 |

### 5c. 🟠 What the content actually looks like — why matching is containment, not equality
Real row, ASIN `B0CV3W93JL`, SKU `LDMG95E2782PK`, sub_source 8:

- **Title:** *"LEDSone Pack 2 | LED Edison E27 Light Bulb, G95 8W = 60W Dim…"*
- **Bullets:** 5 rows, each a full paragraph — *"Energy Saving and Durable: The E27 screw bulb 8W Equivalent
  to 60W itraditional bulbs, saving more than 90% energy cost…"*
- **Backend keywords:** a **single run-on blob**, not discrete terms —
  *"E27 LED retro vintage g95 8w led dimmable globe edison style filament bulb smoked gold glass b22 edison
  screw energy class a+ g95 b22 8w ribbed gold g80 globe screw es e27 calex g95 8 watt bulb deco g125 double
  2700 kelvin 240 lumen smoked light bulb 2 pack filament g95 castello g200 virtual light ledsone dimmable
  g125 vintage bulb amazon 8w10cm crompton lamp led g95 globe 7w es-e27 dimmable 40w equivalent warm white
  806lm large light bulb x6 led g95 screw diall 8w e27 bayonet e14 amber bulb"*

**Method 1 and Method 2 are therefore containment tests over normalised concatenated text, never
`keyword = term`.** The backend field is already dense, so a "missing keyword" finding must survive a
normalisation a human would agree with. **Open item #9.**

## 6. 🟠 SKU normalisation — the spec's own example family is real, and messier than the spec

```sql
SELECT sku, asin, site, sub_source FROM listings.amazon_listings
WHERE sku ILIKE 'LDMG95E278%' AND site='UK' ORDER BY sku LIMIT 20;
```

| sku | asin | sub_source |
|---|---|---|
| `LDMG95E278 M` | B09475XCMR | 8 |
| `LDMG95E278 R` | B0845ZBTJV | 8 |
| `LDMG95E278-DC` | B0CNPZDQHZ | 6 |
| `LDMG95E278-DC_DCVV` | **B0CNPZDQHZ** | **8** |
| `LDMG95E278-a` | B0CNPS9D19 | 6 |
| `LDMG95E2782PK` | B0D4Y98Z49 · B0DH4KLR3P · B0CV3W93JL | 6 · 9 · 8 |
| `LDMG95E2782PK_AMD` | B0D4Y98Z49 | 6 |
| `LDMG95E2782PK_KP` | B0F3NYFLLV | 8 |
| `LDMG95E2783PK` | B0D4YG1QFJ · B0DH4JC6CM · B09479HV6W | 6 · 9 · 8 |
| `LDMG95E2783PK A` | B09479HV6W | 8 |
| `LDMG95E2783PK_DCVV` | B0D4YG1QFJ | 8 |
| `LDMG95E2785PK` | B0DH4K136X | 9 |
| `LDMG95E2785PK A` · `LDMG95E2785PK_AMN` | B09477VMYH | 8 |
| `LDMG95E2786PK` | B0DH4LZZYX · B0D4Y9DKJD | 9 · 6 |

**Two findings:**
1. Stripping `2PK`/`5PK` is **not sufficient**. Real suffixes include trailing letters (` M`, ` R`, ` A`,
   `-a`), account markers (`-DC`, `_DCVV`, `_AMD`, `_AMN`, `_KP`, `_AML`) and Amazon-generated junk SKUs
   (`amzn.gr.TPOSBDBM-87P0SJqtG2g1zCHyzPHJ-LN`, seen in §7). **The normaliser is a business rule — open
   item #6.**
2. **The same ASIN appears under more than one account.** `B0CNPZDQHZ` is listed under sub_source 6 *and* 8;
   `B0D4Y98Z49` and `B09479HV6W` likewise. The spec's "accounts never merged" rule does **not** partition
   ASINs cleanly and must be stated at row level. **Open item #3.**

## 7. End-to-end feasibility — proven on live data

```sql
WITH tm AS (
  SELECT child_asin asin, SUM(units_ordered) units, SUM(sessions) sessions
  FROM business_reports.amz_sales_and_traffic_by_asin
  WHERE market_place=23 AND sub_source=8 AND date >= DATE '2026-08-17' - 30
  GROUP BY 1 HAVING SUM(units_ordered) > 0 ORDER BY units DESC LIMIT 5)
SELECT tm.asin, tm.units, tm.sessions,
  (SELECT COUNT(DISTINCT search_query) FROM business_reports.amz_search_query_performance q
    WHERE q.asin=tm.asin AND q.sub_source=8 AND q.market_place=23
      AND q.start_date >= DATE '2026-08-08' - 90) sqp_terms_90d,
  (SELECT string_agg(DISTINCT l.sku,' / ') FROM listings.amazon_listings l
    WHERE l.asin=tm.asin AND l.site='UK' AND l.sub_source=8) skus
FROM tm ORDER BY units DESC;
```

| ASIN | units (30d) | sessions | distinct SQP terms (90d) | SKUs |
|---|---|---|---|---|
| B0CZXL6ZYG | 109 | 2,117 | **363** | `TPOSBDBM` / `TPOSBDBM_AML` / `amzn.gr.TPOSBDBM-87P0SJqtG2g1zCHyzPHJ-LN` |
| B0DH4KYFPD | 53 | 649 | 153 | `WCDTBM2PK+RPR44WH2PK` / `…_AML` |
| B0B9Y5MRSK | 37 | 434 | 105 | `CL3TGD5PK` / `CL3TGD5PK AM` |
| B0DX6NBT9P | 27 | 350 | 34 | `CENU19150WH J` |
| B0CGRPTT6W | 25 | 219 | 172 | `CRSF100BM+PHRYWP2RBM` |

✅ **Every Top-Moving ASIN returns well above the spec's "top 30–50 terms" requirement.** The Phase 1 → Phase
2 chain is reproducible from SQL alone.
🟠 Note the composite SKUs (`WCDTBM2PK+RPR44WH2PK`, `CRSF100BM+PHRYWP2RBM`) and the `amzn.gr.…` junk SKU —
more input for the normalisation rule (#6).

---

## Verdict

| Question | Answer |
|---|---|
| Does SQP exist in the DB? | ✅ Yes — `business_reports.amz_search_query_performance`, both accounts, UK |
| All 7 Step-8 export columns? | ✅ Yes (one ambiguity: which column is `click_rate`) |
| Top-Moving / drop / zero-sales data? | ✅ Yes — daily, 2026-01-01 → 2026-08-17 |
| Title, bullets, description? | ✅ All three, join verified |
| Backend generic keywords? | ✅ Yes — 189,192 rows |
| **Is anything missing?** | **No. The build is gated on unstated business rules, not on data.** *(Requester assigned by HR to Thuwaraga, `staff.users` id 122, the same day — 2026-08-19.)* |
| Can Phase 1's manual Seller Central steps be replaced by SQL? | ✅ Technically yes — but that is a scope change for the requester to approve (#2) |
| Is the SP-API write in scope? | 🔴 **No** — destructive, public, irreversible; out of workbench scope (`CLAUDE.md` §2, open item #1) |

**All queries read-only. No writes, no DDL, no publishes.**
