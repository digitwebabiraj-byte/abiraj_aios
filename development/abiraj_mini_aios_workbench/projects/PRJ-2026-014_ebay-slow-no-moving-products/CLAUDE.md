# CLAUDE.md — PRJ-2026-014 eBay Slow Moving & No Moving Products

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional and
specific to this project.

## 1. Never write to eBay

This project recommends actions. It **does not execute them.** Ending, discounting, bundling or
re-pricing a listing is a write to a live marketplace and is covered by *Never Touch Without Written
Approval* ("live automation"). No approval exists.

Do not write eBay API calls, do not build a write-back path, do not add an "apply actions" button.
If asked to, stop and report the gate.

## 2. This report needs BOTH databases — never build from one

The single most important fact about this build.

| Need | Database |
|---|---|
| Listings, title, category, image, price, stock, sales, PPC | **`ledsone`** |
| **Views, Conversion Rate** | **warehouse `order_management_copy`** — `public.traffic_data WHERE which_channel = 2` |

`traffic_data` **does not exist** in `ledsone`. Conversely the warehouse's `listing_data` has
**Product Title populated on only 8.3%** of in-scope eBay items — a warehouse-only build ships
91.7% of rows with no product name. Both were measured 2026-07-22.

An audit that searches only `ledsone` will wrongly conclude eBay views and conversion do not exist.
That mistake was made and corrected in this project; do not repeat it.

## 3. Views: `click`, never `impression`

In `traffic_data`, **`click` is the listing page view** — that is the report's "Views". `impression`
is a search impression and is roughly 250× larger; using it would make Rules 5 and 9 meaningless.
`Conversion Rate = SUM(conversion) / NULLIF(SUM(click),0)`.

## 4. Missing traffic is "unknown", never zero

The eBay traffic feed lost **11 days** inside the 90-day window and lags ~2 days. A listing with no
traffic row means **NO DATA**, and must render blank.

Collapsing it to `0` would make **Rule 9** ("views < 50") fire on every listing the ingestion missed
and recommend SEO work on listings that may be performing fine. Rules 5 and 9 are therefore
evaluated **only** where a traffic row exists. Never `COALESCE(views, 0)` for a rule test — display
only.

## 5. Do NOT filter `wrong_sku = 1` out of this report

The warehouse's standing "always filter `wrong_sku = 0`" rule exists for **SKU→inventory bridging**,
a join path this report does not use — stock comes straight from `ebay_listings.quantity`.

**51.7% of in-scope listings (5,767 of 11,156) carry `wrong_sku = 1`**, and they are **real, live,
sellable listings** with proper titles, stock and prices; the flag only means the SKU string is not
a clean inventory code. Excluding them would delete half the portfolio from a dead-stock report.

**But:** column 4 (SKU) is unreliable for those rows, and none of them can be bridged to inventory.
State this on any deliverable that shows SKU.

## 6. Never read `ebay_listings.status`

It is **~99% NULL** (populated only on parent/single rows) and is known to contradict `is_ended`.
Derive Listing Status from `is_ended` / `end_date` instead. EPPA precedent.

## 7. Thresholds stay configuration

All eleven thresholds live on the workbook's **Rules** sheet as editable cells, and `Action Required`
is a live formula referencing them. Never inline a threshold into SQL or the script.

Two of them are **assumptions, not source facts**, and must be labelled as such wherever they
appear: **rule precedence** (the source never states multi-match resolution) and **Rule 8's £5.00 /
30-day** spend floor (the source says "high" and defines it nowhere).

## 8. Window anchor

Anchor on the latest day for which **sales** are complete (verified 91/91 days → the anchor is
today). Never anchor on the traffic feed, which lags ~2 days — doing so would silently shorten every
sales window.

## 9. Grain: account × marketplace × listing

One row per account × marketplace × listing. The source has no Marketplace column, so the
marketplace is carried inside `Account`.

Use the **account** name, not the brand: `led_sone` and `ledsonede` both carry the LEDSone brand and
both sell on Germany, so brand alone silently merges two accounts. EBPD precedent on
account×marketplace double-counting.

## 10. Rule 6 can never fire — say so, don't hide it

`Watchers` has no source in either database. Column 17 ships blank with the reason stated on the
report itself. Never populate it with `0` or an estimate.

## 11. Rule 8 does not override EPPA

`PRJ-2026-013` (EPPA) is **canonical** for eBay PPC pause decisions. This report's Rule 8 is a coarse
listing-level flag (spend with no sales), not a pause recommendation, and it fired on 2 listings.
Do not second-guess EPPA from this report, and do not let the two diverge into competing truths.

## 12. Never reconcile against the source sample

Rows 1–11 of the source file are **fabricated** (placeholder item IDs, synthetic SKUs) and their
`Action Required` values **contradict the file's own rule table**. They fix column order and header
text only. Reconcile against the live database.

## 13. Read-only until gated

Read-only queries only. No DDL, no `ph_task` publish, no scheduled task registration, no git commit
until the open decisions in `PROJECT_HOME.md` are closed and the reviewer gates pass.
