# SYSTEM_REFERENCE — Amazon ASIN Rating Analysis & Variation Merging (avm) · PRJ-2026-025 / REQ-29

Complete functional detail: what the report is, the exact column → source map, and the logic behind every
derived field. **Status: DESIGN reference (2026-08-18) — no builder exists yet.** Source mappings marked
✅ were measured live on 2026-08-18 via `Ledsone-db-mcp`; those marked 🔴 have **no source at all** and are
the reason the build is blocked. Where no truthful source exists a cell must render **NO DATA**, never a guess.

## 1. What the system will produce
For each Amazon ASIN that has **no reviews or a low rating**, one row proposing a **merge into a stronger
parent ASIN** in the same product family, with the safety checks and the operator's approval decision.
Rendered as one data layer / two files:
- **Excel** `REQ-29-D01_asin_variation_merge.xlsx`: `Notes & Method` + `ASIN Merge Task` (12 cols) +
  `Field Reference` tabs — mirroring the source workbook's own three sheets.
- **HTML dashboard** `REQ-29-D01_asin_variation_merge.html`: the 4 KPI tiles, the Merge Status Overview,
  a searchable/sortable candidate table and the approval view.

Nothing in this system performs a merge. It ends at a reviewed recommendation.

## 2. Universe & candidate logic (from the source workbook — RULES NOT YET CONFIRMED)
The workbook states the shape but not the thresholds. The intended flow is:
1. Take the Amazon catalogue for the agreed account(s) and market(s).
2. Group ASINs into **variation families** (Base SKU / parent).
3. Within each family, find children with **no reviews** or a **low rating** → merge candidates.
4. Find the family's **strongest parent** (best rating / review history) → the merge target.
5. Reject or warn where the child's **variation attribute already exists** under that parent
   (Duplicate Warning) or where the child is **Out of Stock**.
6. Emit one row per candidate for **operator approval**.

Steps 3, 4 and 5 all need business rules the source does not state — see `PROJECT_HOME.md` open items #4–#8.
Do not choose them unilaterally.

## 3. Column → source map (12 columns)

Measured live 2026-08-18. Scope of the measurement: `listings.amazon_listings`, `site = 'UK'`,
`sub_source = 8` (`amazon Ledsone`) — 18,721 rows / 16,963 ASINs / 1,489 parents / 17,232 children, table
live to **2026-08-18 00:31**.

| # | Column | Source / derivation | Status |
|---|---|---|---|
| 1 | **Platform** | Constant `AMAZON` (the report's scope) | ✅ derived |
| 2 | **Account** | `order_management.sub_source.name` via `amazon_listings.sub_source` — 8 `amazon Ledsone`, 6 `amazon Dcvoltage`, 9 `amazon SRM Amazon` | ✅ verified |
| 3 | **Base SKU** | `listings.amazon_listings.parent_sku` (the listing-tool family key). Alternative: the family's shared SKU stem. ⚠ `parent_sku` is often an opaque code (`KI-QF1W-MGJP`), not a readable stem like the spec's `CRSF120` — Prasath may mean the SKU stem instead | ✅ present, ⚠ definition open (#5) |
| 4 | **Parent ASIN** | `amazon_listings.asin` where `is_parent = 1` (1,489 UK/Ledsone parents). Alternative: `business_reports.amz_sales_and_traffic_by_asin.parent_asin` — Amazon's own family map | ✅ both exist, ⚠ which is authoritative is open (#5) |
| 5 | **Parent Rating / Reviews** | 🔴 **NO SOURCE.** No Amazon rating or review-count column or table exists anywhere in the database | 🔴 **BLOCKER** |
| 6 | **Child ASIN / SKU** | `amazon_listings.asin` + `amazon_listings.sku` where `is_child = 1` (17,232 UK/Ledsone children) | ✅ verified |
| 7 | **Child Colour / Rating** | **Colour** ✅ `amazon_listings.selected_variations` jsonb → the entry with `name='color'`, e.g. `[{"name":"color","value":"40cm Hemp-1m"}]`; 14,665 UK/Ledsone rows carry it. **Rating** 🔴 no source | ⚠ half sourceable |
| 8 | **Merge Reason** | DERIVED from the rating test ("No reviews — merge into stronger parent" / "Low rating — merge into higher-rated parent"). Vocabulary is the spec's; the **thresholds are not stated** | 🔴 depends on #5, ⚠ rule open (#4) |
| 9 | **Stock Status** | `amazon_listings.quantity > 0` → `In Stock`, else `Out of Stock`; `status` ('Active'/'Inactive') available as a second signal. ⚠ this is **platform** stock — warehouse stock is a different source (`inventory.*`) and a different number | ✅ verified, ⚠ which stock is meant is open |
| 10 | **Duplicate Warning** | DERIVED — does the child's variation attribute already exist among the parent's other children? Computed from `selected_variations` within the `parent_sku` group. **Measured real:** parent `KI-QF1W-MGJP` has 227 children across only 51 distinct colour values | ✅ computable, ⚠ matching rule open (#7) |
| 11 | **Approved (Y/N)** | **Operator input** — not derivable. Blank in a generated report; filled by the PH/operator | ✅ by design |
| 12 | **Operator Notes** | **Operator input** — free text, blank in a generated report | ✅ by design |

### The blocker in one line
**10 of 12 columns are sourceable today. The 2 that are not — Parent Rating/Reviews and the rating half of
Child Colour/Rating — are the ones that decide which rows exist at all.**

## 4. 🔴 The rating gap, in full
> **Owner-confirmed 2026-08-18 (Abiraj):** there is no review data in the database. The sweeps below are the
> evidence; the conclusion is now an accepted project constraint, not a pending question.

A whole-database sweep on 2026-08-18:

```sql
SELECT table_schema, table_name, column_name
FROM information_schema.columns
WHERE column_name ILIKE '%rating%' OR column_name ILIKE '%review%';
-- 10 rows: all eBay (customer_service.ebay_account_ratings,
--          ebay_orders_customer_feedbacks.rating_star) or false matches
--          (*_messages.body_preview, matched on "preview")
```

```sql
SELECT table_schema, table_name FROM information_schema.tables
WHERE table_name ILIKE ANY (ARRAY['%review%','%rating%','%feedback%']);
-- 3 rows: customer_service.ebay_account_ratings,
--         customer_service.ebay_feedback_analytics,
--         customer_service.ebay_orders_customer_feedbacks
```

**No Amazon rating exists.** The eBay rows that do exist are account-level seller ratings and per-order
buyer feedback — neither is an Amazon product star rating, and neither can substitute for one.

Both sweeps were then **repeated on the second database** — `dev` @ 10.8.0.3 (the warehouse, via the
`3320445b-…` "Postgresql" connector): **0 rating/review/feedback tables**, and its only 2 `%rating%|%review%`
column hits are `message.amz_msg.body_preview` and `message.shopify_msg.body_preview` — the same false match
on the word "preview". The `83171520-…` connector resolves to the same `ledsone` database as the primary one.
**The gap holds across every database reachable from this machine.**

The Amazon warehouse tables were checked for a proxy and none is legitimate:
`business_reports.amz_sales_and_traffic_by_asin` carries units, sales, sessions, page views, buy-box % and
refund rate; `amz_best_seller_rank` carries BSR. **None of these is a review signal** and using one as a
stand-in would fabricate a business conclusion. See `CLAUDE.md` §2.

### Precedents for closing it
| Precedent | What happened | Applies here as |
|---|---|---|
| **ECKR #017** (eBay Competitor & Keyword Research) | The needed data existed only on the live marketplace, not in any table → the project became a governed **browser scrape** instead of a SQL build | option (a): scrape/SP-API pull the rating per ASIN |
| **AKYP #024** (Amazon Keyword YoY) | The keyword tables were missing → **Sajeesan ingested them** and the build was unblocked the same day | option (c): request Amazon rating/review ingestion |

## 5. Data sources — the raw DB `ledsone` (via `Ledsone-db-mcp`, live host 169.58.91.229)
A second database, `dev` @ 10.8.0.3 (warehouse, `3320445b-…` connector), was swept for the rating gap only;
it holds no Amazon catalogue or rating data relevant to this report.
| Domain | Schema.table | Key |
|---|---|---|
| Amazon catalogue: ASIN, SKU, parent/child, variations, price, title, stock, status | `listings.amazon_listings` | `asin`, `parent_sku`, `sub_source`, `site` |
| Account names | `order_management.sub_source` | `id` (8 / 6 / 9 = the Amazon accounts) |
| Amazon variation family (Amazon's own view) + sales/traffic per ASIN | `business_reports.amz_sales_and_traffic_by_asin` | `parent_asin` → `child_asin`, `date`, `sub_source`, `market_place` |
| Amazon orders (if unit history is wanted) | `order_management.order_item_info.item_asin` | `item_asin` |
| Warehouse stock (if warehouse rather than platform stock is meant) | `inventory.*` | `sku` |
| **Rating / reviews** | 🔴 **none** | — |

- The AIOS knowledge base MCP is `docs.ledsone.co.uk/mcp` (an MCP endpoint, not an HTTP page — 404 on plain
  fetch). The raw-data MCP is `mcp.ledsone.co.uk/mcp` (the `Ledsone-db-mcp` `execute_sql` used above).

## 6. Dashboard specification (source Dashboard sheet)
The HTML deliverable reproduces what the requester drew, driven by live counts:

| Element | Content |
|---|---|
| KPI tiles (4) | Total ASINs · No-Review / Low-Rated · Approved · Rejected / Review |
| Merge Status Overview | Approved · Rejected / Review · Duplicate Warnings · Out of Stock (count per status) |
| Business / Technical Summary | Automation Objective · Approval Control · Key Validation · Execution · Open Dependency |
| ROI panel | The five business-value statements (see `PROJECT_HOME.md`) |

The sample counts on the sheet (5 / 5 / 3 / 2) are illustrative and must never be shipped.

## 7. Open items (do not resolve by guessing — workbench stop-condition)
All of these are **Prasath's** decisions (Business Validator / end user, `staff.users` id 163, Jaffna,
Active; task assigned by HR 2026-08-18).

0. ✅ RESOLVED — requester / Business Validator = **Prasath**.
1. 🔴 Rating & review-count source (blocks the build).
2. Account(s): Ledsone / Dcvoltage / SRM / all.
3. Market(s): UK only or wider.
4. "Low rating" threshold and "no reviews" definition.
5. Authoritative parent definition (`parent_sku`/`is_parent` vs `parent_asin`) and what "Base SKU" means.
6. Stronger-parent selection rule, and the fallback when no parent qualifies.
7. Duplicate-attribute matching rule (exact vs normalised; colour only or colour + size).
8. Out-of-stock policy (hard reject vs overridable warning).
9. Approval mechanism (editable Excel returned by the PH vs a write-back UI).
10. Seller Central flat-file template, sample file and variation field list (requester's own dependency).
11. Publish audience + automation cadence.

## 8. Reproduce (once built — placeholder)
```
set LED_PGHOST/LED_PGUSER/LED_PGPASSWORD/LED_PGDATABASE/LED_PGPORT   # git-ignored shared store
python sql/REQ-29_amazon-asin-variation-merge/build_avm_d01.py
```
Will write a payload snapshot + both outputs into `evidence/final_outputs/REQ-29_amazon-asin-variation-merge/`.
