# SPEC COMPLIANCE CHECK — deliverables vs `BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf`

**Date:** 2026-08-19 · **Question asked by the owner:** *"is this the correct file according to the
requirement?"* · **Answer:** the Excel was correct; **the dashboard was not, and has been fixed.**

## What the check found

🔴 **The dashboard rebuild had dropped the source's §2.7 review buttons.** Grep for
`Mark reviewed` / `Add missing keywords` in the shipped HTML returned **0**. The rebuild traded the
per-pair panels (which carried the buttons) for a flat filterable table — better to work from, but it
silently removed a stated requirement, and with it any way to set `action_state`, column 11 of the §2.9
contract. §2.6 also requires the keyword status to be shown **per ASIN pair**.

✅ **Fixed by adding a second view rather than reverting.** The toolbar now has **View**:
- **All keywords — one list** (default): the flat, sortable, filterable table.
- **By listing — with review buttons**: per ASIN pair, keyword-by-keyword status, and the two §2.7
  buttons. This is the §2.6 view the document describes.

Both views obey every filter, so nothing is lost either way.

## Compliance matrix

### Phase 1 (REQ-30-D01)
| Source step | Required | Delivered | |
|---|---|---|---|
| 1 | Top-Moving ASINs per account, ranked by units/sessions | `amz_sales_and_traffic_by_asin`, per `sub_source`, units threshold | ✅ |
| 2 | SQP **ASIN View** | `amz_search_query_performance` is ASIN-grain | ✅ |
| 3 | One ASIN at a time | set-based query, same result | ✅ *(deviation 1)* |
| 4 | Monthly, last 3 months separately | months assembled from weekly rows; rates recomputed, never averaged | ✅ |
| 5 | Sort by volume, top 30–50 | top 50 by `search_query_volume` | ✅ |
| 6 | Cross-filter click rate / ASIN share; drop zero-conversion | zero-conversion dropped; both metrics kept as columns | ✅ |
| 7 | Long-tail: 3–6 words, 50–500/mo, high click/conversion | `is_long_tail` flag, all three conditions | ✅ |
| 8 | CSV, 7 named columns | all 7 present in `REQ-30-D01_sqp_top_terms.xlsx` | ✅ |

### Phase 2 (REQ-30-D02)
| Source step | Required | Delivered | |
|---|---|---|---|
| 1 | Sales-drop 3mo **or** zero-sales 6mo | both, catalogue-anchored | ✅ *(deviation 2)* |
| 2 | Strip pack suffixes; correct wrong SKUs against the **SKU mapping table** | pack/marker/account normalisation **+ `mapped_sku`** | ✅ |
| 3 | Compare the top terms against the twin | one row per pair × keyword | ✅ |
| 4 | Method 1 — title/bullets/description as one group, any one place is enough | `in_frontend` = OR of the three surfaces | ✅ |
| 5 | Method 2 — backend field, **independently** | `in_backend` computed separately | ✅ |
| 6 | Pre-computed dashboard, keyword-by-keyword tick/missing **per ASIN pair** | **"By listing" view** | ✅ *(was ❌ before this fix)* |
| 7 | Monthly, per account, reported independently | `date_checked`; accounts never merged | ✅ |

### §2.7 — buttons and directional add logic
| Required | Delivered | |
|---|---|---|
| Button 1 *"All Keywords Present · Mark Reviewed"*, shown **only** when every term ticks both methods | shown only when the pair has 0 gaps; verified — 3 such pairs exist | ✅ |
| Button 2 *"Add Missing Keywords"* whenever any gap exists | shown with the gap count | ✅ |
| frontend-only gap → **backend** | truth table asserted on 100% of rows | ✅ |
| backend-only gap → **bullets only** | asserted | ✅ |
| missing from both → **backend AND bullets** | asserted | ✅ |
| *"All writes happen automatically via the SP-API Listings endpoint"* | 🔴 **DELIBERATELY NOT DONE** — out of workbench scope, owner-confirmed. Buttons record state in-page and say so on screen. | ⛔ by decision |

### §2.9 — output contract, all 12 columns
`brand · top_asin · base_sku · duplicate_asin · duplicate_status · keyword · in_frontend · in_backend ·
status · add_target · action_state · date_checked` — **all 12 present and in order** in
`REQ-30-D02_keyword_gap_report.xlsx` → sheet `Part B - Keyword Gaps`, plus one addition
(`search_query_volume`) so the work can be prioritised. ✅

### §2.10 — QA checklist
| Check | |
|---|---|
| Account separation, never merged | ✅ asserted |
| SKU normalisation applied | ✅ asserted + 6 import-time assertions |
| One-place-is-enough | ✅ asserted |
| Dual-method coverage, independent | ✅ asserted |
| Directional add logic, never a blanket push | ✅ asserted on every row |
| Zero manual lookup | ✅ every keyword traced to a live SQP row |
| Monthly cadence | ✅ |

## Additions beyond the source (both documented)
**Part A** — listings with no content at all, reported once instead of once per keyword (owner decision
Q12). **Part C** — pairs rejected because the two listings' wattage or cap fitting disagree, so a wrong
SKU cannot cause a wrong recommendation. Neither is in the document; both prevent misleading output.

## Two deliberate deviations
1. **Phase 1 read from the warehouse** rather than performed as 8 manual Seller Central steps — same
   data, and it is what makes the document's own "zero manual lookup" instruction achievable.
   *Requester approval still outstanding (open item #2).*
2. **Zero-sales anchored on the product catalogue**, not the sales report — that report only lists an
   ASIN on days it had traffic, so 27% of ASINs, the deadest ones, never appear in it.

## Verdict
🟢 **Both files now match the requirement**, with the single stated exclusion of the SP-API write.
Verified interactively: 23 pair panels, 23 buttons, Button 1 correctly restricted to the 3 fully-present
pairs, and the on-screen note *"recorded in this page only — nothing was sent to Amazon"*.
