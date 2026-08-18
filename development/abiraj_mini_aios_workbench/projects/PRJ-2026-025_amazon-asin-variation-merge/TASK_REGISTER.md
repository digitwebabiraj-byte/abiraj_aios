# TASK REGISTER — PRJ-2026-025 Amazon ASIN Rating Analysis & Variation Merging

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

## Assignment
| Field | Value |
|---|---|
| **Today's Task (2026-08-18)** | Onboard the Amazon ASIN Rating Analysis & Variation Merging requirement into AIOS as `PRJ-2026-025` / `REQ-29` (`avm`): understand the source workbook, create the standard project structure, import and checksum-verify the source, and map the data foundation before any build. |
| **Task Assigned By** | **HR** |
| **User / Business Validator** | **Prasath** — `staff.users` id **163**, username `prasath`, branch **Jaffna**, role User, status Active |
| **Expected Benefit** | Cut manual ASIN rating and variation analysis time · consolidate customer reviews across eligible variations · improve listing credibility where a stronger review history is shared · reduce manual errors via systematic parent selection and an automated duplicate-attribute check · produce measurable outputs and execution logs for follow-up *(the requester's own ROI panel)*. |

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-29 | **REQ-29-D01** | **Amazon ASIN Rating Analysis & Variation Merge** recommendation report. Finds Amazon ASINs with no reviews or a low rating, proposes a stronger parent ASIN in the same variation family to merge each under, flags duplicate variation attributes and out-of-stock children, and presents every candidate for operator approval. 12 columns: Platform · Account · Base SKU · Parent ASIN · Parent Rating / Reviews · Child ASIN / SKU · Child Colour / Rating · Merge Reason · Stock Status · Duplicate Warning · Approved (Y/N) · Operator Notes. Excel (Notes + table + field reference) + interactive HTML dashboard (4 KPI tiles + merge-status overview + approval view), from one read-only builder. **No merge is ever executed by this system.** | 🟡 **PILOT DELIVERED — RULES CONFIRMED (2026-08-18).** REQ-29-D01 rebuilt on **Prasath's confirmed rules (Q2-Q7)**: **253 rows — 245 merge candidates + 8 needing review — across 165 families**, from 1,302 scraped ASINs (0 errors). Includes **75 'No Suitable Parent' families** surfaced for manual review per Q5b. ⚠ **Scope gap: covers amazon Ledsone only; Prasath confirmed Ledsone AND Dcvoltage** — Dcvoltage (15,035 UK ASINs) is not yet scraped. Not validated, not published, not automated, not committed. |

## Source
- `evidence/source_documents/REQ-29_amazon-asin-variation-merge/2026-08-18_source_asin-variation-merge-spec.xlsx`
  (from `996_ASIN_Variation_Merge_Dashboard.xlsx`) — 3 sheets: Dashboard (KPI tiles + status overview +
  business summary + ROI), ASIN Merge Task (12-column table with 5 **sample** rows), Field Reference
  (Prasath's own definition of each field).

The workbook is **spec, not data** — it says so itself ("EXAMPLE DATA ONLY"). It defines columns, KPI tiles,
merge-reason vocabulary and the approval control model, never a delivered figure.

## 🔴 Blocker — Amazon rating & review count have no source
**✅ CONFIRMED BY ABIRAJ 2026-08-18.** Owner agrees: the DB holds no review data for Amazon. The blocker is
accepted, not disputed — what remains is choosing the external source (open item #1).
Measured 2026-08-18 against the live raw DB: a full column sweep (`%rating%` / `%review%`) and table sweep
(`%rating%` / `%review%` / `%feedback%`) found rating data for **eBay only** —
`customer_service.ebay_account_ratings`, `ebay_orders_customer_feedbacks`, `ebay_feedback_analytics`. There
is **no Amazon product rating or review-count column or table anywhere**.

Rating is this report's primary selection criterion (columns 5 and 7, and the whole "no-review / low-rated"
universe). Without a source those cells can only render **NO DATA** and no candidate can be selected or
ranked. The build does not start until the requester chooses a source — scrape/SP-API (the **ECKR #017**
precedent), a Seller Central export, warehouse ingestion by Sajeesan (the **AKYP #024** precedent), or a
descope. **That choice is Prasath's.**

**10 of the 12 columns are sourceable today** from `listings.amazon_listings` (18,721 UK rows / 16,963 ASINs
/ 1,489 parents / 17,232 children / 14,665 with `selected_variations`, live to 2026-08-18) — including the
Duplicate Warning check, which is measurably needed: parent `KI-QF1W-MGJP` carries **227 child ASINs across
only 51 distinct colour values**.

## Deliverables (planned)
- Excel: `evidence/final_outputs/REQ-29_amazon-asin-variation-merge/REQ-29-D01_asin_variation_merge.xlsx`
- HTML dashboard: `.../REQ-29-D01_asin_variation_merge.html`
- Builder: `sql/REQ-29_amazon-asin-variation-merge/build_avm_d01.py`

## Open items (block the build)
- **#0 ✅ RESOLVED 2026-08-18 — Business Validator / user = Prasath** (`staff.users` id 163, Jaffna, Active);
  assigned by HR. The source workbook had said only "PH / Product Team".
- **#1 🔴 Rating & review-count source** — no SQL source exists. **Prasath's decision.**
- **#2 ✅ ANSWERED** — Ledsone (8) **and** Dcvoltage (6). SRM excluded.
- **#3 ✅ ANSWERED** — UK only.
- **#4 ✅ ANSWERED** — low rating = below 3.5; no reviews = exactly 0.
- **#5** Authoritative parent definition (`amazon_listings.parent_sku`/`is_parent` vs
  `amz_sales_and_traffic_by_asin.parent_asin`) and what "Base SKU" means.
- **#6 ✅ ANSWERED** — rating ≥3.5, then highest review count, tie → fewer variations; no parent → show as 'No Suitable Parent'.
- **#7 ✅ ANSWERED** — smart match (case/space-insensitive), colour AND size.
- **#8 ✅ ANSWERED** — show with a warning; operator decides.
- **#9** Approval mechanism (editable Excel returned by the PH vs a write-back UI).
- **#10** Seller Central flat-file template, sample file and variation field list — *the requester's own
  stated dependency*.
- **#11** Publish audience + automation cadence (deferred until a first report is seen).
- Confirm provisional identity `PRJ-2026-025` / `REQ-29` / `avm` with Abiraj (cosmetic).
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability), **Prasath** (business).

## Business decisions — CONFIRMED by Prasath 2026-08-18 ✅
| # | Decision | Confirmed rule |
|---|---|---|
| Q2 | **Accounts** | **amazon Ledsone (8) AND amazon Dcvoltage (6)** — both. SRM excluded. |
| Q3 | **Market** | **UK only.** |
| Q4 | **"Low rating"** | **below 3.5 stars**. **"No reviews" = exactly 0 reviews.** |
| Q5 | **Parent selection** | A parent must have **rating ≥ 3.5**. Among eligible, pick the **highest review count**; tie → **fewer child variations**. Worked example given: A 4.8/100, B 4.5/500, C 4.2/300 → **B wins** on review count. |
| Q5b | **No eligible parent** | **Show the family as "No Suitable Parent" for manual review** — never hide it. |
| Q6 | **Duplicate check** | **Smart match** (ignore capitals and spacing), comparing **colour AND size**. |
| Q7 | **Out of stock** | **Show with a warning; the operator decides.** Not an automatic rejection. |

### Implementation note on the Q5 tie-break
"Fewer child variations" is not a stored column. It is derived: ASINs within a family sharing an
**identical (rating, reviews) pair** are already one Amazon variation, so that count is how many
children a candidate parent already carries. Documented proxy, not a guess — see
`sql/REQ-29_.../build_avm_d01.py`.

### Still open (not answered)
**Q1** long-term rating source (scraping is the interim answer) · **Q8** approval mechanism ·
**Q9** flat-file template / sample / variation fields · **Q10** platform vs warehouse stock ·
**Q11** publish audience + automation cadence.

## Automation
None. Not automated, not scheduled, not on the fleet.

## Publish record — ph_task
None. Nothing published.

## Sign-off
None. Project scaffolded 2026-08-18 and assigned by HR to **Prasath**; blocked on the rating source (#1),
which is Prasath's decision.
