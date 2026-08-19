# TASK REGISTER — PRJ-2026-026 BGCT Keyword Collection & Cross-ASIN Gap Sync

Canonical index of tasks/deliverables within this project. Detail lives in `PROJECT_HOME.md` /
`SYSTEM_REFERENCE.md`.

## Assignment
| Field | Value |
|---|---|
| **Today's Task (2026-08-19)** | Onboard the BGCT Manual Keyword Collection & Automated Backend Sync Workflow v2.1 into AIOS as `PRJ-2026-026` / `REQ-30` (`bgct`): understand the source specification, create the standard project structure, import and checksum-verify the source, and map the data foundation before any build. |
| **Task Assigned By** | **HR** |
| **User / Business Validator** | **Thuwaraga** — `staff.users` id **122**, username `thuwaraga`, branch **Jaffna**, role User, status Active |
| **Expected Benefit** | Replace manual keyword lookup with a monthly automated cycle, per the source's own "MD instruction" that the pipeline run **end-to-end with zero manual keyword lookup**. Take the search terms **already proven** on a Top-Moving ASIN — first-party Amazon SQP data, *"not estimated"* — and close the gap on sibling listings of the **same base SKU** that are declining or making no sales, so a keyword that demonstrably works on one listing stops being absent from its dying twin. **Route each missing term to the right place** (backend keyword field, bullets, or both) rather than a blanket backend push, so listing content is corrected where the gap actually is. Reduce two accounts' worth of per-ASIN Seller Central navigation to a reviewed report whose only human actions are *Mark Reviewed* or *Add Missing Keywords*. |

| Task | Deliverable | Description | Status |
|---|---|---|---|
| REQ-30 | **REQ-30-D01** | **Phase 1 — SQP top search terms per Top-Moving ASIN.** Per account, rank ASINs by units/sessions, then pull their highest-volume, highest-converting real customer search terms from Amazon Search Query Performance. Export contract: `search_term · search_query_score · search_query_volume · total_count · asin_count · asin_share · click_rate`. | 🟢 **BUILT 2026-08-19 (PH-scoped, ≥2-of-3 rule).** Source data verified present (137,048 SQP rows / 3,368 ASINs, Ledsone UK). Gated on open items #2, #4, #5, #10. |
| REQ-30 | **REQ-30-D02** | **Phase 2 — cross-ASIN keyword gap detection.** For each underperforming listing (3-month sales drop or 6-month zero sales) sharing a Top-Moving ASIN's base SKU, check every confirmed term against the title/bullets/description (Method 1) and the backend generic keyword field (Method 2), independently, and emit the directional add target. 12 columns: `brand · top_asin · base_sku · duplicate_asin · duplicate_status · keyword · in_frontend · in_backend · status · add_target · action_state · date_checked`. Excel + interactive review dashboard. **No marketplace write is performed by this system.** | 🟢 **BUILT 2026-08-19 (PH-scoped, ≥2-of-3 rule).** All four content surfaces verified present. Gated on open items #1, #3, #6, #7, #8, #9. |

## Source
- `evidence/source_documents/REQ-30_amazon-keyword-gap-sync/2026-08-19_source_bgct-keyword-workflow-spec.pdf`
  (from `BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf`, 153,412 bytes, md5
  `637da6187137bde151010b0d8a983c85`) — 5 pages: Phase 1 (8 steps + interpretation guide), Phase 2 (7 steps),
  §2.7 button/directional-add logic, §2.8 pseudocode, §2.9 the 12-column output contract, §2.10 QA checklist.

The PDF is **specification, not data**. Its example identifiers (`B0CNPZ2FZZ`, the `LDMG95E278` family) are
illustrations of a rule, never delivered figures — even where they coincide with real catalogue rows.

## 🟢 Data-foundation verdict — GREEN, no blocker
Measured live 2026-08-19 against the raw `ledsone` DB. Unlike #025, **every read this workflow needs already
exists**:

| Need | Table | Measured |
|---|---|---|
| SQP search terms | `business_reports.amz_search_query_performance` (48 cols) | UK: **137,048** rows / 3,368 ASINs / 71,679 queries (ss 8) · 39,173 / 2,216 / 24,615 (ss 6) |
| Top-Moving + drop/zero sales | `business_reports.amz_sales_and_traffic_by_asin` | UK: 417,030 rows (ss 8) · 355,610 (ss 6) · to **2026-08-17** |
| Title + description | `listings.amazon_listings` | UK: 18,721 rows / 16,963 ASINs (ss 8) · 16,396 / 15,035 (ss 6) · to **2026-08-19** |
| Bullets | `listings.amazon_listing_bullet_points` | **429,224** rows · join `product_id` → `amazon_listings.id` ✅ |
| Backend keywords | `listings.amazon_listing_search_engine_keywords` | **189,192** rows · same join ✅ |

## ✅ Feasibility — the full chain was RUN, not inferred (2026-08-19)
Top-Mover `B0B9Y5MRSK` → zero-sale twin `B07FNP5GYB` → 15 live SQP terms → Method 1 + Method 2 →
`status`/`add_target`. Top gap: **"3 core electrical cable", 4,008 searches/month, missing from both
surfaces**. The workflow does what the spec claims. Top-5 Ledsone ASINs return **34–363** SQP terms each.

🔴 **One correction to the spec's method:** `amz_sales_and_traffic_by_asin` is traffic-driven — **4,650 of
16,963 UK ASINs (27%) have no row at all** in 180 days, so zero-sales must anchor on the catalogue with a
LEFT JOIN, not on the sales table. Full zero-sale universe = **13,845 ASINs (82%)**.

⚠ **Two unstated rules control the output size:** SKU normalisation swings candidates **~125×** (58 → 7,396
pairs) and the keyword match rule swings frontend hits **~5×** (2/50 exact-phrase vs 10/50 all-tokens).

Full assessment: `evidence/logs_or_screenshots/REQ-30_.../2026-08-19_feasibility_assessment.md`.

Full evidence:
`evidence/logs_or_screenshots/REQ-30_amazon-keyword-gap-sync/2026-08-19_data_foundation_probe.md`.

## 🔴 Scope boundary — the SP-API write is out of workbench scope
Source §2.7 ends in automatic SP-API writes to live Amazon listings. That is destructive, public and
irreversible, and no write credential exists here. **The AIOS deliverable ends at a reviewed gap report with
a per-keyword add-target recommendation.** Enabling any listing write requires written owner approval and is
a separate system. See `CLAUDE.md` §2 and open item #1.

## Deliverables (planned)
- Phase 1 export: `evidence/final_outputs/REQ-30_amazon-keyword-gap-sync/REQ-30-D01_sqp_top_terms.xlsx`
- Phase 2 Excel: `.../REQ-30-D02_keyword_gap_report.xlsx`
- Phase 2 dashboard: `.../REQ-30_bgct_keyword_dashboard.html`
- Builder: `sql/REQ-30_amazon-keyword-gap-sync/build_bgct_d01.py`

## Open items (block the build)
All of these are **Thuwaraga's** decisions (Business Validator / end user, `staff.users` id 122, Jaffna,
Active; task assigned by HR 2026-08-19).
- **#0 ✅ RESOLVED 2026-08-19 — Business Validator / user = Thuwaraga** (`staff.users` id 122, Jaffna,
  Active); assigned by **HR**. The source PDF had named no one — it is addressed to the "Automation Team"
  and cites an "MD instruction".
- **#1** SP-API write in or out of AIOS scope (recommended: out).
- **#2** Phase 1 from the database vs the manual Seller Central export.
- **#3** Account scope stated at row level — the same ASIN exists under both accounts.
- **#4** How weekly SQP rows become the spec's monthly windows; the reference-month anchor, given DCVOLTAGE
  lags LEDSone by two weeks.
- **#5** "Top-Moving" definition and cut-off.
- **#6** SKU normalisation rule (far messier than the spec's `2PK`/`5PK`).
- **#7** Which "SKU mapping table" — `amazon_listings.mapped_sku` / `wrong_sku`?
- **#8** Exact "Sales Drop (3mo)" and "Zero Sales (6mo)" tests.
- **#9** Keyword match semantics — case, punctuation, plurals, word order, contiguity.
- **#10** Number of top terms per ASIN; Step 6 / Step 7 filter thresholds; which column is `click_rate`.
- **#11** Publish audience + automation cadence slot.
- **#12 🆕** How to report listings with **no content at all** (20% have an empty backend field, 11% are
  title-only) — one "no content" finding vs hundreds of keyword gaps.
- Confirm provisional identity `PRJ-2026-026` / `REQ-30` / `bgct` with Abiraj (cosmetic).
- Reviewer gates: Sajeesan (technical), Tamil Selvan (queryability), **Thuwaraga** (business).

## Business decisions — CONFIRMED by Abiraj (owner) 2026-08-19 ✅
> **Attribution:** these three answers came from **Abiraj (owner)**, not from Thuwaraga. Thuwaraga's
> business sign-off is still outstanding, as are the remaining open items.

| # | Decision | Confirmed rule |
|---|---|---|
| **Q1** | **Automatic Amazon write** | **NO — not needed.** The system produces a **report only**; a person applies the keywords. No SP-API push, no listing write. This matches the workbench boundary in `CLAUDE.md` §2. |
| **Q6** | **SKU normalisation** | **Strip pack size (`2PK`/`5PK`…), trailing letters (` M`, ` R`, ` A`, `-a`) and account suffixes (`_DCVV`, `_AMD`, `_AMN`, `_KP`, `_AML`, `_UK`, `-DC`).** All such variants = the same product. |
| **Q6b** | **Bundle / kit SKUs** | **Kept WHOLE** — `CRSF100BM+PHHT1PBRBM+LSFT320DG` is its own product, not a variant of `CRSF100BM`. *(Implementation decision, flagged for confirmation — see the note below.)* |
| **Q9** | **Keyword match** | **Words anywhere** — all words of the search term must appear somewhere in the text, in any order. Case and punctuation ignored. Not exact-phrase. |

### ⚠ Why Q6b had to be decided separately
A first measurement split bundle SKUs on `+` and grouped by the first component. That produced **10,801
candidate pairs** because base `CRSF100BM` matched **1,151 distinct ASINs** — every kit containing that one
ceiling rose was treated as the same product. That is over-matching, not generosity, so bundles are kept
whole. **If Thuwaraga wants bundles decomposed, say so — it changes the report by roughly 100×.**

### Resulting report size (measured 2026-08-19, under the confirmed rules)
| Top-Moving cut-off | DCVOLTAGE UK pairs | LEDSone UK pairs | Total |
|---|---|---|---|
| Top 20 | 3 | 7 | **10** |
| **Top 50** | 27 | 31 | **58** |
| Top 100 | 38 | 73 | **111** |

Largest SKU family under the rule: 32 (DCVOLTAGE) / 65 (LEDSone) — sane, no runaway groups. At ~30 keywords
per pair, **Top-50 ≈ 1,700 keyword rows** — a workable review dashboard.

### Still open
**Q5** the Top-Moving cut-off (20 / 50 / 100 — drives the table above) · **Q2** database vs manual Seller
Central for Phase 1 · **Q3** account scope at row level · **Q4** monthly window from weekly SQP · **Q7** SKU
mapping table · **Q8** exact drop/zero tests · **Q10** term count and filters · **Q11** publish audience and
cadence · **Q12** how to report listings with no content.

## Rules stated by the requester (implement exactly — these are NOT open)
| Area | Rule (source §2.7 / §2.10) |
|---|---|
| Account separation | DCVOLTAGE UK and LEDSone UK processed and reported independently, never merged |
| One-place-is-enough | Method 1 ticks if the term is in **any one** of title, bullets or description |
| Dual-method coverage | Methods 1 and 2 are independent — a term can pass one and fail the other |
| Directional add | frontend-only gap → **backend**; backend-only gap → **bullets only**; neither → **both** |
| Human actions | exactly two — *Mark Reviewed* and *Add Missing Keywords* |
| Cadence | monthly, once per brand account |

## Automation
None. Not automated, not scheduled, not on the fleet.

## Publish record — ph_task
✅ **PUBLISHED 2026-08-19 — `tech_team_outputs.ph_task` id 980**, md5-verified byte-identical
(141,402 chars, `22a8f2bb10ca9c73c913ff2d22d7571e`).

| field | value |
|---|---|
| id | **980** |
| project_code | **`bgct-kwgap`** |
| task_id | `bgct-kwgap-2026-08-19-thuwaraga` |
| assigned_user | **thuwaraga** · assigned_user_team **ph_priors** |
| team / developer | Development / Abiraj |
| version_status | released · version_level 1 |

🔴 **Why the code is `bgct-kwgap`, not `bgct`.** `ph_task` already holds project_code **`BGCT` at id 9
= "BGCT Listing Generator"** — developer tharsika, assigned to **utharsika**, last updated 2026-08-17.
A different team's live project that merely shares the prefix. Publishing under `bgct` would have
collided with it in the portal, and updating id 9 would have destroyed their work. Verified after the
insert: **id 9 is unchanged** (9,176 chars, still updated 2026-08-17).

Publisher: `automation/publish_bgct_ph_task.py` — guarded INSERT, refuses to touch any row whose
`project_code`/`task_id` are not ours, md5-verifies the read-back, and takes the password from
`PGPASSWORD` only. Refresh with `--update 980`.

## Sign-off
None. Project scaffolded 2026-08-19 and assigned by HR to **Thuwaraga** (`staff.users` id 122); sign-off is
pending the decision sheet (open items #1–#11) and a first delivered report.
