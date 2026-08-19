# SYSTEM_REFERENCE — BGCT Keyword Collection & Cross-ASIN Gap Sync (bgct) · PRJ-2026-026 / REQ-30

Complete functional detail: what the two-phase workflow is, the exact column → source map, and the logic
behind every derived field. **Status: DESIGN reference (2026-08-19) — no builder exists yet.** Every source
mapping marked ✅ was measured live on 2026-08-19 via `Ledsone-db-mcp`. Where no truthful source exists a cell
must render **NO DATA**, never a guess.

## 1. What the system will produce

**Phase 1 (REQ-30-D01)** — for each Top-Moving ASIN per account, its confirmed top search terms, in the
spec's Step 8 export contract:
`search_term · search_query_score · search_query_volume · total_count (impressions) · asin_count ·
asin_share · click_rate`

**Phase 2 (REQ-30-D02)** — one row per (underperforming ASIN × keyword), in the spec's §2.9 contract:

| # | Column | Type | Description (verbatim from source §2.9) |
|---|---|---|---|
| 1 | `brand` | enum | `dcvoltage_uk` / `ledsone_uk` — accounts never merged |
| 2 | `top_asin` | string | Top-Moving ASIN (source of top search terms) |
| 3 | `base_sku` | string | Normalised SKU — pack suffixes stripped, mapping applied |
| 4 | `duplicate_asin` | string | Underperforming ASIN sharing the same base SKU |
| 5 | `duplicate_status` | enum | `sales_drop_3mo` / `zero_sales_6mo` |
| 6 | `keyword` | string | Top search term being audited (from Phase 1 export) |
| 7 | `in_frontend` | bool | True if found in title, bullets or description |
| 8 | `in_backend` | bool | True if found in backend/generic keyword field |
| 9 | `status` | enum | `present` / `gap` |
| 10 | `add_target` | enum | `backend` / `bullet` / `backend_and_bullet` / `none` |
| 11 | `action_state` | enum | `reviewed` / `pending_add` / `added` |
| 12 | `date_checked` | date | ISO date of this monthly run |

Rendered as Excel + an interactive review dashboard. **Nothing in this system writes to Amazon.**

## 2. Phase 1 — the eight spec steps, and where each one actually lives

| Spec step | What it says to do manually | DB equivalent | Status |
|---|---|---|---|
| 1 | Pull Business Report per account, rank ASINs by units/sessions, record Top-Moving ASIN + SKU | `business_reports.amz_sales_and_traffic_by_asin` (`units_ordered`, `sessions`) + `listings.amazon_listings.sku` | ✅ available — **cut-off unstated (#5)** |
| 2 | Seller Central → Brand Analytics → SQP → **ASIN View** | `business_reports.amz_search_query_performance` is already ASIN-grain (`asin` column) | ✅ available |
| 3 | Enter one Top-Moving ASIN, loop per ASIN | `WHERE asin = …` — no loop needed, set-based | ✅ available |
| 4 | Reporting Range → Monthly, last 3 months one at a time; extend to 6 if thin | 🟠 **table is `report_period='WEEK'` only** — months must be assembled from weeks | ⚠ **rule needed (#4)** |
| 5 | Sort by Search Query Volume desc, record top 30–50 | `ORDER BY search_query_volume DESC LIMIT n` | ✅ available — **n unstated (#10)** |
| 6 | Cross-filter by click rate and ASIN share; drop zero-conversion terms | `total_click_rate`, `asin_impression_share`, `asin_purchase_count` | ✅ available — **thresholds unstated (#10)** |
| 7 | Find 3–6 word long-tail phrases, 50–500/mo volume, high click/conversion | derived: word count of `search_query` + `search_query_volume` band | ✅ derivable |
| 8 | Export CSV `SQP_[ASIN]_[YYYY-MM].csv` with 7 named columns | all 7 map to real columns — see §4 | ✅ available |

**Consequence:** Phase 1 as specified is a manual Seller Central procedure, but the warehouse already holds
the export. The whole phase can be a query. **That is a scope change the requester must approve (open item
#2)** — it changes Phase 1 from a human task into a derived dataset.

## 3. Phase 2 — the seven spec steps

| Spec step | Logic | Source | Status |
|---|---|---|---|
| 1 | Find (a) **Sales Drop** — declined/stopped over 3 consecutive months; (b) **Zero Sales** — no orders in 6 months | `amz_sales_and_traffic_by_asin` (`units_ordered`, `ordered_product_sales`), daily from 2026-01-01 | ✅ data present — **exact test unstated (#8)** |
| 2 | Normalise SKUs, strip pack suffixes, apply SKU mapping, match to Top-Moving base SKU | `amazon_listings.sku` / `mapped_sku` / `wrong_sku` | ⚠ **normaliser is a business rule (#6, #7)** |
| 3 | Take the Top-Moving ASIN's confirmed terms, prepare for both checks | Phase 1 output | ✅ |
| 4 | **Method 1** — scan title + bullets + description as one group; any one place = placed | `amazon_listings.title` · `amazon_listing_bullet_points.points` · `amazon_listings.product_description` | ✅ all three exist — **match rule unstated (#9)** |
| 5 | **Method 2** — scan backend/generic keyword field independently | `amazon_listing_search_engine_keywords.keyword` | ✅ exists — **match rule unstated (#9)** |
| 6 | Pre-compute everything; dashboard shows keyword-by-keyword tick/missing for both methods | derived | ✅ |
| 7 | Re-run monthly, once per brand account, reported independently | scheduling | ⚠ **cadence slot unstated (#11)** |

### §2.7 directional add logic (stated by the requester — implement exactly)
| `in_frontend` | `in_backend` | `status` | `add_target` |
|---|---|---|---|
| ✅ | ✅ | `present` | `none` |
| ✅ | ❌ | `gap` | `backend` |
| ❌ | ✅ | `gap` | `bullet` — **bullets only, explicitly not title, not description** |
| ❌ | ❌ | `gap` | `backend_and_bullet` |

*Button 1 "All Keywords Present · Mark Reviewed"* is shown **only** when every top term ticks both methods.
*Button 2 "Add Missing Keywords"* is shown whenever any gap exists. In this workbench both buttons record
state; **neither performs a marketplace write** (see `CLAUDE.md` §2).

## 4. Column → source map

### Phase 1 export (spec Step 8) — `business_reports.amz_search_query_performance`
| Spec column | Source column | Status |
|---|---|---|
| `search_term` | `search_query` | ✅ |
| `search_query_score` | `search_query_score` | ✅ |
| `search_query_volume` | `search_query_volume` | ✅ |
| `total_count` (impressions) | `total_query_impression_count` | ✅ |
| `asin_count` | `asin_impression_count` | ✅ |
| `asin_share` | `asin_impression_share` | ✅ |
| `click_rate` | `total_click_rate` (total) / `asin_click_share` (ASIN's share) — **the spec does not say which** | ⚠ ambiguous (#10) |

Filter keys: `sub_source` (6 / 8), `market_place = 23` (UK), `start_date` / `end_date`, `report_period`
(always `'WEEK'`). Also available and useful for Step 6/7: `total_purchase_count`, `total_purchase_rate`,
`asin_purchase_count`, `asin_purchase_share`, `total_cart_add_rate`, `asin_median_click_price`.

### Phase 2 contract (spec §2.9)
| # | Column | Source / derivation | Status |
|---|---|---|---|
| 1 | `brand` | `sub_source` 8 → `ledsone_uk`, 6 → `dcvoltage_uk` (`order_management.sub_source.name`) | ✅ |
| 2 | `top_asin` | Top-Moving ASIN from Phase 1 Step 1 | ✅ derived |
| 3 | `base_sku` | `amazon_listings.sku` normalised — **rule not stated** | ⚠ rule open (#6) |
| 4 | `duplicate_asin` | underperforming ASIN sharing `base_sku` | ✅ derived |
| 5 | `duplicate_status` | `sales_drop_3mo` / `zero_sales_6mo` — **anchor on `amazon_listings`, LEFT JOIN `amz_sales_and_traffic_by_asin`**; absence = zero (27% of ASINs have no sales row) | ⚠ test open (#8) |
| 6 | `keyword` | Phase 1 `search_query` | ✅ |
| 7 | `in_frontend` | containment of `keyword` in `title` ∪ `bullet_points.points` ∪ `product_description` | ✅ sources exist, ⚠ semantics open (#9) |
| 8 | `in_backend` | containment of `keyword` in `search_engine_keywords.keyword` | ✅ source exists, ⚠ semantics open (#9) |
| 9 | `status` | `present` iff `in_frontend AND in_backend`, else `gap` | ✅ stated by spec |
| 10 | `add_target` | the §2.7 truth table above | ✅ stated by spec |
| 11 | `action_state` | operator state — `pending_add` on generation; `reviewed` / `added` set by the operator | ✅ by design |
| 12 | `date_checked` | run date | ✅ derived |

## 5. Data sources — the raw DB `ledsone` (via `Ledsone-db-mcp`, live host 169.58.91.229)
| Domain | Schema.table | Key | Measured 2026-08-19 |
|---|---|---|---|
| **SQP search terms** | `business_reports.amz_search_query_performance` | `asin`, `sub_source`, `market_place`, `start_date`/`end_date`, `report_period` | 48 cols · UK: **137,048** rows / 3,368 ASINs (ss 8), 39,173 / 2,216 (ss 6) |
| Sales & traffic per ASIN (Top-Moving, drop, zero) | `business_reports.amz_sales_and_traffic_by_asin` | `child_asin`, `parent_asin`, `date`, `sub_source`, `market_place` | UK: 417,030 rows (ss 8), 355,610 (ss 6) · 2026-01-01 → **2026-08-17** |
| Listing title, description, SKU, ASIN, stock, parent/child | `listings.amazon_listings` | `id`, `asin`, `sku`, `mapped_sku`, `sub_source`, `site` | UK: 18,721 rows / 16,963 ASINs (ss 8) · 16,396 / 15,035 (ss 6) · live to **2026-08-19 00:31** |
| **Bullets** | `listings.amazon_listing_bullet_points` | `product_id` → `amazon_listings.id`, `points`, `view_order` | **429,224** rows / 80,829 products |
| **Backend generic keywords** | `listings.amazon_listing_search_engine_keywords` | `product_id` → `amazon_listings.id`, `keyword`, `view_order` | **189,192** rows / 68,072 products |
| Account names | `order_management.sub_source` | `id` — 6 `amazon Dcvoltage`, 8 `amazon Ledsone`, 9 `amazon SRM Amazon` | ✅ |
| ❌ **Not this project's source** | `amazon_campaigns.search_term_performance_data` | — | PPC search terms, **not SQP** — see `CLAUDE.md` §5 |

- The AIOS knowledge base MCP is `docs.ledsone.co.uk/mcp` (an MCP endpoint, not an HTTP page — 404 on plain
  fetch). The raw-data MCP is `mcp.ledsone.co.uk/mcp` (the `Ledsone-db-mcp` `execute_sql` used above).

## 6. Worked example of the content surfaces (real row, 2026-08-19)
ASIN `B0CV3W93JL`, SKU `LDMG95E2782PK`, account 8:

- **Title** — *"LEDSone Pack 2 | LED Edison E27 Light Bulb, G95 8W = 60W Dim…"*
- **Bullets** — 5 rows in `amazon_listing_bullet_points`, each a full paragraph
  (*"Energy Saving and Durable: The E27 screw bulb 8W Equivalent to 60W…"*).
- **Backend keywords** — a single run-on blob:
  *"E27 LED retro vintage g95 8w led dimmable globe edison style filament bulb smoked gold glass b22 edison
  screw energy class a+ g95 b22 8w ribbed gold g80 globe screw es e27 calex g95 8 watt bulb deco g125…"*

**This is why matching is containment, not equality** (`CLAUDE.md` §6). It also shows the backend field is
already dense — a "missing keyword" finding must survive a normalisation that a human would agree with.

## 7. Dashboard specification (source §2.6 / §2.7)
| Element | Content |
|---|---|
| Per ASIN-pair panel | Top-Moving ASIN → underperforming ASIN, base SKU, `duplicate_status` |
| Keyword table | one row per top term: Method 1 tick/missing · Method 2 tick/missing · `add_target` |
| Actions | Button 1 *Mark Reviewed* (only when all terms tick both) · Button 2 *Add Missing Keywords* |
| Account separation | DCVOLTAGE UK and LEDSone UK rendered and reported independently, never merged |

In this workbench both buttons record state only — see `CLAUDE.md` §2.

## 8. Open items (do not resolve by guessing — workbench stop-condition)
Full sheet: `prompts/discovery/REQ-30_amazon-keyword-gap-sync/2026-08-19_DECISION_SHEET_for_requester.md`
All of these are **Thuwaraga's** decisions (Business Validator / end user, `staff.users` id 122, Jaffna,
Active; task assigned by HR 2026-08-19).

0. ✅ RESOLVED 2026-08-19 — requester / Business Validator = **Thuwaraga** (`staff.users` id 122, Jaffna, Active); assigned by **HR**.
1. SP-API write in or out of AIOS scope (recommended: out — `CLAUDE.md` §2).
2. Phase 1 from the database vs the manual Seller Central export.
3. Account scope stated at row level (the same ASIN exists under both accounts).
4. How weekly SQP rows become the spec's monthly windows, and the reference-month anchor.
5. "Top-Moving" definition and cut-off.
6. SKU normalisation rule.
7. Which "SKU mapping table" — is it `amazon_listings.mapped_sku` / `wrong_sku`?
8. Exact "Sales Drop (3mo)" and "Zero Sales (6mo)" tests.
9. Keyword match semantics — case, punctuation, plurals, word order, contiguity.
10. Number of top terms per ASIN, and the Step 6 / Step 7 filter thresholds; which column is `click_rate`.
11. Publish audience + automation cadence slot.
12. 🆕 How to report listings with no content at all (20% empty backend field, 11% title-only).

**Feasibility measured 2026-08-19** — the chain was run end-to-end and works; zero-sales must anchor on the
catalogue (27% of ASINs are absent from the sales table); the SKU rule swings output ~125× and the match rule
~5×. See `evidence/logs_or_screenshots/REQ-30_.../2026-08-19_feasibility_assessment.md`.

## 9. Reproduce (once built — placeholder)
```
set LED_PGHOST/LED_PGUSER/LED_PGPASSWORD/LED_PGDATABASE/LED_PGPORT   # git-ignored shared store
python sql/REQ-30_amazon-keyword-gap-sync/build_bgct_d01.py
```
Will write a payload snapshot + the outputs into
`evidence/final_outputs/REQ-30_amazon-keyword-gap-sync/`.
