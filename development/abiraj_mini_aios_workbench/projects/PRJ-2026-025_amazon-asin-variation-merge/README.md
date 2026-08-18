# Amazon ASIN Rating Analysis & Variation Merging (avm) — PRJ-2026-025

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`; task index in `TASK_REGISTER.md`.

## What
An **Amazon ASIN rating analysis and variation-merge recommendation** report. It finds Amazon ASINs that
have **no reviews or a low rating**, identifies a **stronger parent ASIN** in the same product family to
merge them under, checks that the merge is safe (**variation attribute not already used**, **stock
available**), and presents each candidate for **operator approval**. Nothing merges automatically — the
report recommends, a human approves, and the approved merges are executed through the Amazon Seller Central
flat-file process.

## Who it's for
**User / Business Validator: Prasath** (`staff.users` id 163, Jaffna, Active). **Assigned by HR**, 2026-08-18.
Owner Abiraj · Tech Sajeesan · Queryability Tamil Selvan · Coordinator Varmen.

## Status
🟡 **SETUP / SCAFFOLD ONLY — 2026-08-18.** Folder structure, source import, governance docs and a live
data-foundation probe are done. **No build, no deliverable, nothing committed, nothing published.** Next
step is a discovery decision sheet to Prasath + a GPT-approved implementation prompt (this workbench:
Claude executes approved prompts, it does not invent business logic).

## Expected benefit (the requester's own ROI panel)
Cut manual ASIN rating and variation analysis time · **consolidate customer reviews** across eligible
variations · **improve listing credibility** where a stronger review history is shared · **reduce manual
errors** through systematic parent selection and duplicate checks · produce **measurable outputs and
execution logs** for follow-up.

## 🔴 The blocking finding (measured live 2026-08-18)
**Amazon product star rating and review count do not exist anywhere in the database.** A full column and
table sweep of the live raw DB found rating/review data for **eBay only** (`customer_service.ebay_account_ratings`,
`ebay_orders_customer_feedbacks`, `ebay_feedback_analytics`). There is **no Amazon equivalent**.

Rating is the report's **primary selection criterion** — columns E (`Parent Rating / Reviews`) and G
(`Child Colour / Rating`) and the entire "no-review / low-rated" universe depend on it. Without a source,
those cells can only render **NO DATA**, and the report cannot rank or select. **This gap must be closed
before the build starts.** Options are on the discovery sheet in `PROJECT_HOME.md`; the closest precedent
is **ECKR #017**, where missing competitor data was solved by a live browser scrape rather than SQL.

Everything else is sourceable — see below.

## ✅ What IS sourceable today (measured, Amazon UK, `amazon Ledsone` sub_source 8)
`listings.amazon_listings` is live to **2026-08-18** and holds **18,721 UK rows / 16,963 ASINs / 1,489
parents / 17,232 children**, with **14,665 rows carrying `selected_variations`** (a jsonb list of
`{name: color|size, value: …}`). That single table supplies Base SKU, Parent ASIN, Child ASIN/SKU, Child
Colour, Stock Status and — crucially — the **Duplicate Warning** check.

> **Duplicate variations are real, not theoretical.** Parent `KI-QF1W-MGJP` carries **227 child ASINs but
> only 51 distinct colour values**. The duplicate check the requirement asks for is genuinely needed.

## The report shape (12 columns, from the source workbook)
`Platform · Account · Base SKU · Parent ASIN · Parent Rating / Reviews · Child ASIN / SKU ·
Child Colour / Rating · Merge Reason · Stock Status · Duplicate Warning · Approved (Y/N) · Operator Notes`

## Identity (provisional)
`PRJ-2026-025` / `REQ-29` / code `avm`. **Provisional** — the source workbook carries no requirement number
(REQ-26 = esdt, REQ-27 = merge, REQ-28 = akyp). The `996` in the source filename is not a requirement
number. Confirm with Abiraj (cosmetic).

## Deliverable (planned, not built)
- **REQ-29-D01** — ASIN Rating Analysis & Variation Merge report, one data layer rendered as **Excel**
  (Notes + merge-candidate table + field reference) + **interactive HTML dashboard** (the 4 KPI tiles,
  merge-status overview and approval view the source Dashboard sheet specifies).

## Authoritative documents
- `PROJECT_HOME.md` — canonical project truth
- `SYSTEM_REFERENCE.md` — column → `schema.table.column` map and every derived-field rule
- `CLAUDE.md` — execution rules
- `TASK_REGISTER.md` — task/deliverable index
- `evidence/logs_or_screenshots/REQ-29_amazon-asin-variation-merge/2026-08-18_data_foundation_probe.md` — the
  live probe behind every claim above

## Next step
Send the discovery decision sheet in `PROJECT_HOME.md` to **Prasath** — **starting with the rating-source
question**, which blocks the build. Then a GPT-approved implementation prompt before any build.
