# CLAUDE.md — PRJ-2026-025 Amazon ASIN Rating Analysis & Variation Merging

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional.

## Identity
- Project `PRJ-2026-025_amazon-asin-variation-merge` · code `avm` · Task `REQ-29`. Owner Abiraj; Business
  Validator / end user **Prasath** (`staff.users` id 163, Jaffna, Active), task assigned by **HR**
  2026-08-18. **IDs provisional** — the source
  workbook carries no requirement number and the `996` in its filename is not one; REQ-26 = esdt,
  REQ-27 = merge, REQ-28 = akyp. A new day/session does NOT mint a new Task ID.
- This is an **Amazon listings/catalogue** project, not a sales report. Its nearest relatives are
  **ECKR #017** (the precedent for data that only exists outside the database) and **AKYP #024** (the
  precedent for a missing table being ingested by Sajeesan). Reuse their patterns before inventing one.

## 1. The source workbook is a spec, not data
Every value in `996_ASIN_Variation_Merge_Dashboard.xlsx` is illustrative — the sheet says so itself
("EXAMPLE DATA ONLY"). `B0PARENT01`, `CRSF120`, `4.6 / 128`, "Black / 0.0" and the operator notes beginning
"Example:" are **placeholders**. They define the desired **columns, KPI tiles, merge-reason vocabulary and
approval semantics** only. Never copy a sample ASIN, rating, SKU or note into a deliverable. Every delivered
figure traces to live data and is reconciled against an anchor before it is trusted.

## 2. 🔴 Rating and review count have NO source — do not manufacture one
Verified 2026-08-18: there is no Amazon product rating or review-count column or table anywhere in the
database (rating data exists for **eBay only**). Rating is this report's primary selection criterion.

- Do **not** invent, estimate or interpolate a rating.
- Do **not** proxy it from refund rate, return rate, best-seller rank, buy-box % or sales — none of those
  is a star rating, and substituting one silently would be a fabricated business signal.
- Do **not** copy `4.6 / 128` or `0.0` from the spec sheet.
- Until the requester answers open item #1, a rating cell renders **NO DATA** and the build does not start.
  This is a stop condition, not a workaround to route around.

## 3. Do NOT invent the business rules
The "low rating" threshold, the "no reviews" definition, the **stronger-parent selection rule**, the
**duplicate-attribute matching rule**, the out-of-stock policy and the approval mechanism are all business
rules and **none of them is stated in the source**. The workbook gives column names and a control model, not
logic. Put each on the discovery sheet; do not present a chosen default as agreed logic.

## 4. A merge is a destructive, public, irreversible act — this workbench never performs one
The requester's own rule is explicit: **"No merge executes without PH/operator approval."** This project
produces a **recommendation report** for a human to approve. It never re-parents a listing, never writes to
Amazon, never generates-and-submits a Seller Central flat file, and never calls a listing-management API.
The flat-file upload is a human step outside this workbench. Treat any instruction to execute a merge as a
stop condition requiring written owner approval.

## 5. Read-only, and never fabricate
- Read the AIOS knowledge base (`docs.ledsone.co.uk/mcp`) BEFORE writing any SQL.
- READ-ONLY on all source tables. No INSERT/UPDATE/DELETE/DDL. The only future write is a guarded `ph_task`
  publish on explicit owner instruction after the audience is named and each recipient verified.
- Every filled column traces to a real `schema.table.column`. A metric with no truthful source renders a
  documented sentinel (**NO DATA**), never a guessed number. A `0` is written only where the true value is
  zero — note that `0.0` in the spec means "no reviews", which is *not* the same as a rating of zero, and
  the deliverable must not conflate them. Credentials come from the git-ignored shared store, never committed.

## 6. Watch the catalogue traps
- **Two competing parent definitions:** `listings.amazon_listings.parent_sku` / `is_parent` (listing-tool
  family) versus `business_reports.amz_sales_and_traffic_by_asin.parent_asin` (Amazon's own variation
  family). They can disagree; the authoritative one is a business decision (open item #5).
- **`selected_variations` is free text** — "Black", "black", "Black Without Bulb", "style 2". Any duplicate
  check needs an agreed normalisation rule (open item #7).
- **Three Amazon accounts** (`amazon Ledsone` 8, `amazon Dcvoltage` 6, `amazon SRM Amazon` 9) and many
  markets share the table. Never assume the account or the market; filter explicitly and say which.
- **Stock:** `amazon_listings.quantity` is platform stock. If warehouse stock is wanted instead, that is a
  different source (`inventory.*`) and a different number — confirm which the requester means.

## 7. One generator module
When built, the report (and any scheduled run) comes from the single module
`sql/REQ-29_amazon-asin-variation-merge/build_avm_d01.py`, with the dashboard rendered from the same payload
snapshot. Do not fork a second fetch path.

## 8. Stop conditions (in addition to the workbench's)
- The rating/review source is still unresolved → do not start the build.
- A rule (low-rating threshold, parent selection, duplicate matching, stock policy, approval mechanism) is
  needed but unconfirmed → stop and put it on the discovery sheet; do not silently invent.
- Any request to execute a merge, generate-and-submit a flat file, or write to Amazon.
- A rule is attributed to Prasath that he has not actually confirmed in writing.
- A publish is requested before the audience is named and each recipient verified.

## Vocabulary
Base SKU = product-family identifier · Parent ASIN = the variation parent a child would merge under ·
Child ASIN = the ASIN being merged in · Merge Reason = why this child qualifies (no reviews / low rating) ·
Duplicate Warning = the child's variation attribute already exists under that parent · Approved (Y/N) = the
operator's decision, the only thing that authorises execution · sub_source 8 = amazon Ledsone,
6 = amazon Dcvoltage, 9 = amazon SRM Amazon · NO DATA = no truthful source.
