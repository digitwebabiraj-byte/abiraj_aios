# PROJECT_HOME — Amazon ASIN Rating Analysis & Variation Merging (avm)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-025_amazon-asin-variation-merge` |
| **Project code** | `avm` *(provisional)* |
| **Task ID** | `REQ-29_amazon-asin-variation-merge` *(provisional — source has no requirement number; REQ-26 = esdt, REQ-27 = merge, REQ-28 = akyp)* |
| **Status** | 🟡 **PILOT DELIVERED — RULES CONFIRMED (2026-08-18).** REQ-29-D01 rebuilt on **Prasath's confirmed rules (Q2-Q7)**: **253 rows — 245 merge candidates + 8 needing review — across 165 families**, from 1,302 scraped ASINs (0 errors). Includes **75 'No Suitable Parent' families** surfaced for manual review per Q5b. ⚠ **Scope gap: covers amazon Ledsone only; Prasath confirmed Ledsone AND Dcvoltage** — Dcvoltage (15,035 UK ASINs) is not yet scraped. Not validated, not published, not automated, not committed. |
| **Opened** | 2026-08-18 |
| **Owner** | Abiraj · **Coordinator** Varmen · **Tech** Sajeesan · **Queryability** Tamil Selvan |
| **Business Validator / User** | ✅ **Prasath** — confirmed 2026-08-18. `staff.users` **id 163**, username `prasath`, branch **Jaffna**, role User, status Active. *(Resolves former open item #0.)* |
| **Assigned by** | **HR** |
| **Channel / scope** | **Amazon**, source workbook says **Amazon UK**. Account not named (the DB holds three Amazon accounts: `amazon Ledsone` 8, `amazon Dcvoltage` 6, `amazon SRM Amazon` 9). |

## Task assignment (2026-08-18)
| Field | Value |
|---|---|
| **Today's Task** | Onboard the **Amazon ASIN Rating Analysis & Variation Merging** requirement into AIOS as `PRJ-2026-025` / `REQ-29` (`avm`): understand the source workbook, create the standard project structure, import and checksum-verify the source, and map the data foundation before any build. |
| **Task Assigned By** | **HR** |
| **User** | **Prasath** (`staff.users` id 163, Jaffna, Active) — the end user and Business Validator for this report. |
| **Expected Benefit** | Cut the manual time spent analysing ASIN ratings and variation structures; **consolidate customer reviews** across eligible variations so a strong review history is shared rather than fragmented; **improve listing credibility** on ASINs that currently show no or poor reviews; **reduce manual errors** through systematic parent selection and an automated duplicate-attribute check; and produce **measurable outputs and execution logs** for follow-up. *(Source: the requester's own "Expected Business Value / ROI" panel.)* |
| **Outcome today** | Structure, source import and governance complete. **Build blocked** — Amazon rating/review data has no source in the database (see below); Prasath's decision is needed on open item #1. |

> ⚠ IDs provisional. The `996` in the source filename `996_ASIN_Variation_Merge_Dashboard.xlsx` is **not** a
> requirement number. A new day/session does NOT mint a new Task ID. Confirm `PRJ-2026-025` / `REQ-29` /
> `avm` with Abiraj (cosmetic).

## Business question
Which Amazon ASINs are **hurt by having no reviews or a low rating**, which **stronger parent ASIN** in the
same product family should each be merged under so it inherits that parent's review history, and is that
merge **safe to perform** (variation attribute not already taken, stock available) — presented for
**operator approval** before anything is executed in Seller Central?

## Why the business wants it (source Dashboard sheet, "Expected Business Value / ROI")
- Reduce manual ASIN rating and variation analysis time.
- Consolidate customer reviews across eligible variations.
- Improve listing credibility where a stronger review history is shared.
- Reduce manual errors through systematic parent selection and duplicate checks.
- Create measurable automation outputs and execution logs for follow-up.

## Source of truth (one document, imported verbatim)
`996_ASIN_Variation_Merge_Dashboard.xlsx` — 3 sheets:
1. **Dashboard** — 4 KPI tiles (Total ASINs · No-Review/Low-Rated · Approved · Rejected/Review), a Merge
   Status Overview (Approved / Rejected-Review / Duplicate Warnings / Out of Stock), a Business-Technical
   summary and the ROI list.
2. **ASIN Merge Task** — the **12-column** working table with 5 **sample** rows.
3. **Field Reference** — the requester's own one-line definition of each of the 10 data fields.

The sheet itself states: *"EXAMPLE DATA ONLY — ASINs, ratings and SKUs above are illustrative and should be
replaced with actual automation output."* Treat every value in it as **specification, never data**.

## The report (12 columns, exact from the source workbook)
`Platform · Account · Base SKU · Parent ASIN · Parent Rating / Reviews · Child ASIN / SKU ·
Child Colour / Rating · Merge Reason · Stock Status · Duplicate Warning · Approved (Y/N) · Operator Notes`

## Control model — stated by the requester, non-negotiable
| Area | Rule (source Dashboard sheet) |
|---|---|
| Objective | Identify low/no-rating ASINs and recommend stronger variation parents. |
| **Approval control** | **No merge executes without PH/operator approval.** |
| Key validation | Duplicate variation attributes must be checked before merging. |
| Execution | Approved merges use the required Amazon Seller Central **flat-file** process. |
| Open dependency | *The requester already flags it:* "PH team input is required for template, sample file and variation fields." |

> This is a **recommendation-and-approval** system, not an auto-merge system. The AIOS deliverable ends at a
> reviewed report; the flat-file upload is a human step outside this workbench.

## 🔴 Data-foundation verdict (probed live 2026-08-18 via `Ledsone-db-mcp`)
**One hard gap, everything else green.**

### The gap — Amazon rating & review count have NO SOURCE
**✅ CONFIRMED BY ABIRAJ 2026-08-18** — the owner confirms there is no review data in the DB. This is no
longer a probe finding awaiting challenge; it is an accepted fact of the project. The rating must therefore
come from **outside** the database, or the report must be re-scoped (open item #1 — Prasath's call).
A sweep of `information_schema.columns` for `%rating%` / `%review%` across the whole database returned
**10 columns, all eBay or unrelated**:

| Where rating/review data DOES exist | Platform |
|---|---|
| `customer_service.ebay_account_ratings` (`thirty_day_rating`, `week_rating`, counts) | eBay — **account level**, not product |
| `customer_service.ebay_orders_customer_feedbacks.rating_star` | eBay — order feedback |
| `customer_service.ebay_feedback_analytics` | eBay |
| `*_messages.body_preview` | matched on the word "preview" only — irrelevant |

A table-name sweep for `%review%` / `%rating%` / `%feedback%` returned **only those three eBay tables**.
**There is no Amazon product rating or review-count table or column anywhere.**

✅ **Checked across BOTH databases.** The same sweep was run separately on the second, separate database
(`dev` @ 10.8.0.3 — the warehouse, reached via the `3320445b-…` "Postgresql" connector): **0** rating/review/
feedback tables and only 2 `body_preview` false matches. The third connector (`83171520-…`) resolves to the
same `ledsone` database as the first. So the gap is not an artefact of looking in one place.

This is consistent with the known reference: eBay **Watchers** is likewise absent from both databases. The
warehouse Amazon tables (`business_reports.amz_*`) carry sales, traffic, sessions, buy-box and best-seller
rank — but **not** star rating or review count.

**Impact:** columns **E (Parent Rating / Reviews)** and **G (Child Colour / Rating — the rating half)** have
no truthful source, and the report's *entire selection universe* ("no reviews / low rating") cannot be
derived. Per the workbench evidence rule those cells would render **NO DATA** — which makes the deliverable
useless as specified. **This blocks the build.**

### Everything else — measured and green (Amazon UK, `amazon Ledsone` sub_source 8)
`listings.amazon_listings`, live to **2026-08-18 00:31**:

| Measure | Value |
|---|---|
| UK rows / distinct ASINs | **18,721 / 16,963** |
| Parent rows (`is_parent=1`) | **1,489** |
| Child rows (`is_child=1`) | **17,232** |
| Rows carrying `selected_variations` | **14,665** |
| Other Amazon accounts also present | `amazon Dcvoltage` (6): 16,395 UK rows · `amazon SRM Amazon` (9): 5,526 UK rows |

`selected_variations` is **jsonb**, e.g. `[{"name":"color","value":"40cm Hemp-1m"}]` — sometimes with a
second `size` entry. It supplies the **Child Colour** column directly and powers the **Duplicate Warning**
check. `parent_sku` groups the variation family (Base SKU candidate); `quantity` + `status` give **Stock
Status**; `business_reports.amz_sales_and_traffic_by_asin` independently carries a real
`parent_asin` → `child_asin` family map.

### ✅ Duplicate variations are real, not hypothetical
Measured on UK / sub_source 8 child rows grouped by `parent_sku`:

| parent_sku | child ASINs | distinct colour values | in stock |
|---|---|---|---|
| `KI-QF1W-MGJP` | 227 | **51** | 226 |
| `3H-7K6O-NIQZ` | 52 | **26** | 50 |
| `GM-OLH8-QRN0` | 50 | **10** | 21 |
| `LDQ-Neon` | 48 | 10 | 30 |
| `PJ-BDAM-2HWY` | 48 | 12 | 33 |

227 children across 51 colours means the same colour value repeats many times under one parent — exactly the
collision the requester's Duplicate Warning column is meant to catch.

Full evidence: `evidence/logs_or_screenshots/REQ-29_amazon-asin-variation-merge/2026-08-18_data_foundation_probe.md`.

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

## 🟠 Known traps
- **Rating/reviews = NO DATA in SQL** (above). Do not invent, estimate, proxy from returns/refund rate, or
  copy the sample values (4.6 / 128) from the spec sheet.
- **Parent identity is ambiguous.** Two different "parent" notions exist: `amazon_listings.parent_sku` /
  `is_parent` (the listing-tool family) and `amz_sales_and_traffic_by_asin.parent_asin` (Amazon's own
  variation family). They may disagree. Decide which is authoritative before building.
- **A "merge" is destructive and public.** It re-parents a live Amazon listing. This workbench never
  executes it — the deliverable stops at an approved recommendation.
- **`selected_variations` is free text.** "Black", "black", "Black Without Bulb", "style 2" all appear; the
  duplicate check needs a normalisation rule, and that rule is a business decision.
- **Multi-account.** Three Amazon accounts exist; the source names none. Do not silently assume Ledsone.
- **Multi-market.** `amazon_listings` covers UK, Germany, France, Spain, Ireland, Italy, US, Canada and more.
  The source says Amazon UK; confirm before widening.

## Deliverable (planned, not built)
- **REQ-29-D01** — Excel (`Notes & Method` + `ASIN Merge Task` table + `Field Reference`) + interactive HTML
  dashboard (KPI tiles + merge-status overview + approval view), from one read-only builder module
  `sql/REQ-29_amazon-asin-variation-merge/build_avm_d01.py`.

## Reviewer gates (none passed)
Sajeesan (technical) · Tamil Selvan (queryability) · **Prasath** (business).

## Open items — discovery decision sheet (do not resolve by guessing)
**#0 — ✅ RESOLVED 2026-08-18. Requester / Business Validator = Prasath** (`staff.users` id 163, Jaffna,
Active); task assigned by **HR**. The discovery sheet below now has an owner and can be sent.

**#1 — 🔴 Where do Amazon rating and review count come from?** No SQL source exists. Candidate answers, for
the requester to choose:
  - (a) a **live Amazon scrape / SP-API pull** per ASIN — the ECKR #017 precedent, where missing competitor
    data was solved by browser scraping rather than SQL; needs volume + rate-limit scoping against ~17k ASINs;
  - (b) a **Seller Central report export** the PH team already downloads, imported as a file;
  - (c) **Sajeesan ingests rating/reviews into the warehouse** — the AKYP #024 precedent, where he added the
    missing keyword tables and unblocked that build the same day;
  - (d) descope: drop rating and select candidates on a different signal — but that is a different report.

**#2 — Which account(s)?** Ledsone (8) / Dcvoltage (6) / SRM (9) / all three.

**#3 — Which market(s)?** UK only (as written), or the wider Amazon estate.

**#4 — What is "low rated"?** The threshold (< 3.0? < 3.5?) and what counts as "no reviews" (0 reviews, or
below a minimum review count).

**#5 — Which parent definition is authoritative?** `amazon_listings.parent_sku`/`is_parent` vs
`amz_sales_and_traffic_by_asin.parent_asin`.

**#6 — How is the "stronger parent" chosen?** Highest rating? Most reviews? Both, and in what order? What
happens when the family has no qualifying parent?

**#7 — Duplicate-warning rule.** Exact-match or normalised (case/whitespace/synonyms) comparison of the
variation attribute, and which attributes count (colour only, or colour + size).

**#8 — Out-of-stock handling.** The sample row rejects an out-of-stock child. Is out-of-stock an automatic
rejection, or a warning the operator may override?

**#9 — Approval mechanism.** How does the operator record Approved (Y/N) and Operator Notes — an editable
Excel returned by the PH, or a write-back UI? This decides whether the deliverable is read-only.

**#10 — The requester's own open dependency:** the Seller Central **flat-file template**, a **sample file**
and the **variation field list** ("PH team input is required").

**#11 — Publish audience + automation cadence** — deferred until the requester sees a first report.

## Next actions
1. Send the discovery decision sheet (#1–#11) to **Prasath**, leading with the **rating-source question
   (#1)** — it blocks everything else.
2. On answers: request a GPT-approved implementation prompt, then build REQ-29-D01 from one read-only fetch,
   reconcile each field against a live anchor, and produce Excel + HTML.
3. Confirm provisional `PRJ-2026-025` / `REQ-29` / `avm` with Abiraj (cosmetic).
