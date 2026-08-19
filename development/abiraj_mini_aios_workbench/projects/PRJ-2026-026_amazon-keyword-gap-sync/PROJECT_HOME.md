# PROJECT_HOME — BGCT Keyword Collection & Cross-ASIN Gap Sync (bgct)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-026_amazon-keyword-gap-sync` |
| **Project code** | `bgct` *(provisional)* |
| **Task ID** | `REQ-30_amazon-keyword-gap-sync` *(provisional — source PDF has no requirement number; REQ-26 = esdt, REQ-28 = akyp, REQ-29 = avm)* |
| **Status** | 🟡 **SETUP / SCAFFOLD ONLY — 2026-08-19.** Structure, source import (md5-verified), governance docs, a live data-foundation probe and an end-to-end feasibility run are done. **Data foundation GREEN; feasibility PROVEN.** Requester assigned (**Thuwaraga**, by HR). **The three build-blocking rules (Q1 report-only, Q6 SKU normalisation, Q9 word-anywhere matching) are now CONFIRMED by Abiraj** — build can start on a GPT-approved implementation prompt. Nothing built, validated, published, automated or committed. |
| **Opened** | 2026-08-19 |
| **Owner** | Abiraj · **Coordinator** Varmen · **Tech** Sajeesan · **Queryability** Tamil Selvan |
| **Business Validator / User** | ✅ **Thuwaraga** — assigned 2026-08-19. `staff.users` **id 122**, username `thuwaraga`, branch **Jaffna**, role User, status Active. *(Resolves open item #0.)* |
| **Assigned by** | **HR** |
| **Channel / scope** | **Amazon UK**, LED bulb listings, **two seller accounts**: **DCVOLTAGE UK** (`sub_source` 6, `amazon Dcvoltage`) and **LEDSone UK** (`sub_source` 8, `amazon Ledsone`). UK = `market_place` 23. |

## Task assignment (2026-08-19)
| Field | Value |
|---|---|
| **Today's Task** | Onboard the **BGCT Manual Keyword Collection & Automated Backend Sync Workflow v2.1** into AIOS as `PRJ-2026-026` / `REQ-30` (`bgct`): understand the source specification, create the standard project structure, import and checksum-verify the source, and map the data foundation before any build. |
| **Task Assigned By** | **HR** |
| **User** | **Thuwaraga** (`staff.users` id 122, username `thuwaraga`, Jaffna, Active) — the end user and Business Validator for this report. |
| **Expected Benefit** | Replace manual keyword lookup with a monthly automated cycle, per the source's own "MD instruction" that the pipeline run **end-to-end with zero manual keyword lookup**. Take the search terms **already proven** on a Top-Moving ASIN — first-party Amazon SQP data, *"not estimated"* — and close the gap on sibling listings of the **same base SKU** that are declining or making no sales, so a keyword that demonstrably works on one listing stops being absent from its dying twin. **Route each missing term to the right place** (backend keyword field, bullets, or both) rather than a blanket backend push, so listing content is corrected where the gap actually is. Reduce two accounts' worth of per-ASIN Seller Central navigation to a reviewed report whose only human actions are *Mark Reviewed* or *Add Missing Keywords*. |
| **Outcome today** | Structure, source import, governance docs, a requester decision sheet and a live data-foundation probe complete. **Data foundation verified green** — every read the workflow needs exists in the raw DB. Requester assigned by HR to **Thuwaraga**, resolving open item #0. Build gated on 11 unstated business rules, not on missing data. |

> ⚠ IDs provisional. The source PDF `BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf` carries **no requirement
> number**. A new day/session does NOT mint a new Task ID. Confirm `PRJ-2026-026` / `REQ-30` / `bgct` with
> Abiraj (cosmetic).

## Business question
For each **Top-Moving Amazon UK ASIN**, what are its **highest-volume, highest-converting real customer
search terms** (Phase 1) — and do the **other listings of the same base SKU that are declining or making no
sales** already carry those terms in their **title/bullets/description** and in their **backend keyword
field** (Phase 2)? Where a term is missing, **which of the two places** should it be added to?

## Why the business wants it (stated in the source)
- Phase 1 uses **first-party SQP data** — real customer search behaviour, "not estimated", the most reliable
  keyword source available.
- Phase 2 closes the gap where a **proven keyword already works on one listing** but is absent from a
  sibling listing of the same product that is dying.
- Per the source's own "MD instruction": the pipeline runs **end-to-end with zero manual keyword lookup**,
  and the only human actions are *Mark Reviewed* or *Add Missing Keywords*.

## Source of truth (one document, imported verbatim)
`BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf` — 5 pages, "For Automation Team Use · Internal Reference
Only · Aug 2026". It defines:
1. **Phase 1 (Method A)** — 8 numbered steps to collect SQP top terms per Top-Moving ASIN, plus a
   "What to Look For in SQP Data" interpretation guide (5 patterns).
2. **Phase 2** — 7 numbered steps of cross-ASIN gap detection, §2.7 review-button and directional-add logic,
   §2.8 pseudocode, §2.9 the 12-column output contract, §2.10 a 7-point QA checklist.

Full breakdown: `evidence/source_documents/REQ-30_amazon-keyword-gap-sync/SOURCE_MANIFEST.md`.

## The Phase 2 report (12 columns, exact from source §2.9)
`brand · top_asin · base_sku · duplicate_asin · duplicate_status · keyword · in_frontend · in_backend ·
status · add_target · action_state · date_checked`

## Control model — stated by the requester, non-negotiable
| Area | Rule (source §2.7 / §2.10) |
|---|---|
| Account separation | **DCVOLTAGE UK and LEDSone UK processed and reported independently, never merged.** |
| One-place-is-enough | Method 1 ticks a keyword if it appears in **any one** of title, bullets or description. |
| Dual-method coverage | Method 1 and Method 2 are **independent** — a term can pass one and fail the other. |
| Directional add | `in_frontend & !in_backend` → backend only · `in_backend & !in_frontend` → **bullets only** (explicitly *not* title, *not* description) · neither → **both**. |
| Human actions | Exactly two: *Mark Reviewed* (only when every term ticks both methods) and *Add Missing Keywords*. |
| Cadence | Full pipeline re-runs **monthly**, once per brand account. |

## 🟢 Data-foundation verdict (probed live 2026-08-19 via `Ledsone-db-mcp`)
**GREEN. Every read this workflow needs already exists.** This is the opposite of #025, which was blocked on
absent data. Full evidence:
`evidence/logs_or_screenshots/REQ-30_amazon-keyword-gap-sync/2026-08-19_data_foundation_probe.md`.

### Phase 1 — SQP data is in the warehouse, not just Seller Central
`business_reports.amz_search_query_performance` carries **48 columns**, including every column the spec's
Step 8 export requires: `search_query`, `search_query_score`, `search_query_volume`,
`total_query_impression_count`, `asin_impression_count`, `asin_impression_share`, `total_click_rate`,
`asin_click_share`, `total_purchase_count`, `asin_purchase_share`.

| sub_source | market | rows | ASINs | distinct queries | coverage |
|---|---|---|---|---|---|
| **8 LEDSone** | 23 UK | **137,048** | 3,368 | 71,679 | 2026-01-25 → **2026-08-08** |
| **6 DCVOLTAGE** | 23 UK | 39,173 | 2,216 | 24,615 | 2026-01-25 → **2026-07-25** |
| 8 LEDSone | 10 DE | 11,047 | 806 | 6,993 | 2026-02-22 → 2026-08-08 |
| 8 LEDSone | 9 FR | 4,741 | 535 | 3,382 | 2026-04-26 → 2026-07-25 |
| 8 LEDSone | 24 US | 3,730 | 261 | 2,775 | 2026-02-22 → 2026-08-08 |
| 6 DCVOLTAGE | 10 DE | 3,438 | 395 | 2,189 | 2026-02-22 → 2026-07-25 |
| 6 DCVOLTAGE | 9 FR | 412 | 36 | 333 | 2026-04-26 → 2026-07-25 |

**Implication:** Phase 1's 8 manual Seller Central steps (login → Brand Analytics → ASIN View → set range →
sort → filter → export CSV) reduce to **one query**. The interpretation guide ("High Volume + Low ASIN
Share", "3–6 word phrases", seasonal comparison) becomes derived columns. This is a scope simplification the
requester must approve — see open item #2.

### Phase 1 Step 1 / Phase 2 Step 1 — Top-Moving and drop/zero-sales ASINs
`business_reports.amz_sales_and_traffic_by_asin`, `market_place = 23`, daily grain:

| sub_source | rows | ASINs | coverage |
|---|---|---|---|
| 8 LEDSone | **417,030** | 13,745 | 2026-01-01 → **2026-08-17** |
| 6 DCVOLTAGE | 355,610 | 11,701 | 2026-01-01 → **2026-08-17** |

Carries `units_ordered`, `sessions`, `page_views`, `ordered_product_sales`, `buy_box_percentage`,
`unit_session_percentage` — enough for both the Top-Moving ranking (units/sessions, as the spec asks) and
the 3-month-decline / 6-month-zero tests.

### Phase 2 Methods 1 & 2 — all four content surfaces exist
`listings.amazon_listings` is live to **2026-08-19 00:31**:

| sub_source | UK rows | UK ASINs | with title | with description | parents | children |
|---|---|---|---|---|---|---|
| 8 LEDSone | 18,721 | 16,963 | **18,721** | 16,050 | 1,489 | 17,232 |
| 6 DCVOLTAGE | 16,396 | 15,035 | 16,395 | 15,019 | 1,196 | 15,200 |

| Surface | Table | Join | Rows | UK listings covered |
|---|---|---|---|---|
| **Bullets** | `listings.amazon_listing_bullet_points` (`points`, `view_order`) | `product_id` → `amazon_listings.id` ✅ verified | 429,224 | 16,719 (Ledsone) · 15,613 (DCV) |
| **Backend keywords** | `listings.amazon_listing_search_engine_keywords` (`keyword`, `view_order`) | same ✅ verified | 189,192 | 15,010 (Ledsone) · 14,381 (DCV) |

✅ **The eBay `all_list=0` parent-title trap does not apply here** — every Amazon UK row for both accounts is
`all_list = 1` (18,721 / 18,721 and 16,396 / 16,396), so titles are on the row itself.

### End-to-end feasibility, proven on live data
Top 5 Ledsone UK ASINs by units in the 30 days to 2026-08-17, each with its 90-day SQP term count:

| ASIN | units | sessions | distinct SQP terms (90d) | SKUs |
|---|---|---|---|---|
| B0CZXL6ZYG | 109 | 2,117 | **363** | `TPOSBDBM` / `TPOSBDBM_AML` / `amzn.gr.TPOSBDBM-…` |
| B0DH4KYFPD | 53 | 649 | 153 | `WCDTBM2PK+RPR44WH2PK` (+`_AML`) |
| B0B9Y5MRSK | 37 | 434 | 105 | `CL3TGD5PK` / `CL3TGD5PK AM` |
| B0DX6NBT9P | 27 | 350 | 34 | `CENU19150WH J` |
| B0CGRPTT6W | 25 | 219 | 172 | `CRSF100BM+PHRYWP2RBM` |

Every Top-Moving ASIN returns well above the spec's "top 30–50 terms" requirement.

## 🔴 Hard boundary — the SP-API write is NOT in scope for this workbench
Source §2.7 specifies that clicking *Add Missing Keywords* calls
`sp_api.update_backend_keywords()` / `sp_api.update_bullet_points()` and edits the **live Amazon listing**
automatically. That is a **destructive, public, irreversible** action on production marketplace data, in the
same category as the #025 variation merge.

- No SP-API write credential exists in this workbench, and none may be created here.
- The AIOS deliverable **ends at a reviewed gap report** with a per-keyword `add_target` recommendation.
- Building or invoking a listing-write path requires **written owner approval** and is a separate system.

This is a **stop condition**, not a task to route around. See `CLAUDE.md` §2.

## 🟠 Known traps (all measured 2026-08-19 — none of them is in the spec)
1. **SQP is `report_period = 'WEEK'` only.** Every row in the table is weekly; there is no MONTH row. The
   spec's "Set Reporting Range → Monthly … check the last 3 consecutive months one month at a time" has no
   direct equivalent. Weeks can be aggregated into months, but **volume/count columns sum while rate and
   median columns do not** — `total_click_rate`, `asin_impression_share`, `asin_click_share`,
   `*_median_*_price` must be recomputed from their numerators and denominators, never averaged. Amazon's own
   monthly SQP is also not the arithmetic sum of its weeks. **Rule needed (open item #4).**
2. **Backend keywords are phrase blobs, not discrete keywords.** A single
   `amazon_listing_search_engine_keywords.keyword` row holds a long run-on string
   (e.g. *"E27 LED retro vintage g95 8w led dimmable globe edison style filament bulb smoked gold glass b22…"*).
   Method 2 is therefore a **containment / token test on concatenated text**, never `keyword = term`. Same for
   Method 1 against title + bullets + description. *(Same class as the T7 containment-not-equality rule.)*
3. **SQP covers a fraction of the catalogue** — 3,368 of 16,963 Ledsone UK ASINs (~20%) and 2,216 of 15,035
   DCVOLTAGE UK ASINs. Amazon only reports queries above a volume floor. Fine for Top-Movers by definition,
   but it caps how far Phase 1 can be widened.
4. **The two accounts are not equally fresh.** LEDSone SQP runs to 2026-08-08; DCVOLTAGE stops **2026-07-25**
   — two weeks behind. A monthly run must not silently compare a full month against a partial one.
5. **SKU normalisation is much messier than the spec's `2PK` / `5PK`.** The spec's own example family is
   real, and looks like this in the live data:

   | SKU | ASIN | account |
   |---|---|---|
   | `LDMG95E278 M` / `LDMG95E278 R` | B09475XCMR / B0845ZBTJV | 8 |
   | `LDMG95E278-DC` | B0CNPZDQHZ | 6 |
   | `LDMG95E278-DC_DCVV` | **B0CNPZDQHZ** | **8** |
   | `LDMG95E278-a` | B0CNPS9D19 | 6 |
   | `LDMG95E2782PK` | B0D4Y98Z49 / B0DH4KLR3P / B0CV3W93JL | 6 / 9 / 8 |
   | `LDMG95E2782PK_AMD` · `LDMG95E2782PK_KP` | B0D4Y98Z49 / B0F3NYFLLV | 6 / 8 |
   | `LDMG95E2783PK` · `LDMG95E2783PK A` · `LDMG95E2783PK_DCVV` | … | 6 / 9 / 8 |
   | `LDMG95E2785PK A` · `LDMG95E2785PK_AMN` | B09477VMYH | 8 |

   Stripping `2PK`/`5PK` is not enough: trailing letters (` M`, ` R`, ` A`, `-a`), account suffixes
   (`_DCVV`, `_AMD`, `_AMN`, `_KP`, `_AML`) and Amazon-generated junk SKUs (`amzn.gr.TPOSBDBM-…`) all occur.
   **The normalisation regex is a business rule, not a guess (open item #6).**
6. **The same ASIN appears under both accounts.** `B0CNPZDQHZ` is listed under sub_source 6 *and* 8. The
   spec's "accounts never merged" rule therefore does not produce a clean partition of ASINs — the rule needs
   to be stated at row level, not ASIN level (open item #3).
7. **`amazon_campaigns.search_term_performance_data` is NOT SQP.** It is *PPC* search-term data —
   auto-campaign-inclusive and only starting 2025-11-16. Confusing the two is the exact mistake AKYP #024
   documented. **SQP = `business_reports.amz_search_query_performance`.** Nothing else.
8. **The spec references a "SKU mapping table"** ("where a listing's stored SKU doesn't match its real
   product, correct it against the SKU mapping table"). `amazon_listings` carries `mapped_sku` and a
   `wrong_sku` flag — whether those are the intended mapping table is unconfirmed (open item #7). *(The T7
   project already carries a known "dirty mapped_sku" caution.)*

## Deliverables (planned, not built)
- **REQ-30-D01** — Phase 1 output: Top-Moving ASINs per account + their confirmed SQP top search terms
  (the spec's Step 8 export contract: `search_term`, `search_query_score`, `search_query_volume`,
  `total_count`, `asin_count`, `asin_share`, `click_rate`).
- **REQ-30-D02** — Phase 2 output: the 12-column gap contract as Excel + an interactive review dashboard
  (per-ASIN-pair keyword table with tick/missing for both methods, the directional `add_target`, and the
  two action states) — from one read-only builder module in `sql/REQ-30_amazon-keyword-gap-sync/`.

## Reviewer gates (none passed)
Sajeesan (technical) · Tamil Selvan (queryability) · **Thuwaraga** (business).

## Open items — discovery decision sheet (do not resolve by guessing)
Full sheet with context and options:
`prompts/discovery/REQ-30_amazon-keyword-gap-sync/2026-08-19_DECISION_SHEET_for_requester.md`
All of these are **Thuwaraga's** decisions (Business Validator / end user, `staff.users` id 122, Jaffna,
Active; task assigned by HR 2026-08-19).

**#0 — ✅ RESOLVED 2026-08-19. Requester / Business Validator = Thuwaraga** (`staff.users` id 122, Jaffna,
Active); task assigned by **HR**. The source PDF had named no one — it is addressed to the "Automation Team"
and cites an "MD instruction". The decision sheet below now has an owner and can be sent.

**#1 — Is the SP-API write in or out?** Confirming the AIOS deliverable ends at the report (recommended), or
escalating the write to a separately-approved system with owner sign-off.

**#2 — Phase 1 from the database instead of manual Seller Central?** The SQP export already exists in the
warehouse. Approve replacing the 8 manual steps with a query, or keep the manual export as the source of
record.

**#3 — Account scope at row level.** ASINs appear under both accounts; state the separation rule precisely.

**#4 — Monthly window from weekly SQP rows.** How months are assembled, and which reference month anchors a
run, given DCVOLTAGE lags LEDSone by two weeks.

**#5 — "Top-Moving" definition.** Rank by units, sessions, or both? Top N per account, or a threshold? The
spec says "rank by units/sessions" but sets no cut-off.

**#6 — SKU normalisation rule.** The exact strip/normalise rule, given the mess in trap #5.

**#7 — Which SKU mapping table?** Is `amazon_listings.mapped_sku` (+ `wrong_sku`) the "SKU mapping table" the
spec refers to?

**#8 — "Sales Drop" and "Zero Sales" exact tests.** "Declined or stopped over the last 3 consecutive months"
— strictly monotonic decline, or any net drop? By what percentage? Does "zero sales in the last 6 months"
mean zero `units_ordered` or zero `ordered_product_sales`?

**#9 — Keyword match rule.** Case folding, punctuation, plurals, word-order, and whether a multi-word term
must appear contiguously or as scattered tokens.

**#10 — How many top terms per ASIN?** The spec says "record the top 30–50" — pick a number, and say whether
the zero-conversion filter (Step 6) and the long-tail band (Step 7, 50–500/mo) are applied before or after.

**#11 — Publish audience + automation cadence.** Monthly is stated; the `ph_task` audience and the schedule
slot are not.

**#12 — 🆕 How should listings with NO content be reported?** Measured 2026-08-19: **3,711 LEDSone UK
listings (20%) have an empty backend keyword field** and **1,966 (11%) are title-only** — no bullets, no
description. For these every keyword is "missing" because there is nothing to search, not because of 50
individual oversights. Should such a listing be reported as a single **"listing has no content"** finding
rather than hundreds of keyword-gap rows?

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

## ✅ Feasibility — proven end-to-end 2026-08-19
The whole Phase 1 → Phase 2 chain was run on live data, not merely inferred. Real result: Top-Mover
`B0B9Y5MRSK` → zero-sale twin `B07FNP5GYB`, top gap **"3 core electrical cable" (4,008 searches/month)**,
missing from both surfaces → `add_target = backend_and_bullet`. **The workflow does what the spec claims.**
Full assessment:
`evidence/logs_or_screenshots/REQ-30_amazon-keyword-gap-sync/2026-08-19_feasibility_assessment.md`.

### 🔴 Correction to the spec's own method — zero-sales must anchor on the catalogue
`amz_sales_and_traffic_by_asin` is **traffic-driven**: an ASIN only gets a row on days it had sessions. Of
16,963 LEDSone UK catalogue ASINs, **4,650 (27%) have no row at all** in 180 days. A query written over the
sales table — as the spec's §2.8 pseudocode implies — **silently misses them**. Start from the catalogue and
LEFT JOIN. Full 6-month zero-sale universe = **13,845 ASINs (82% of the catalogue)**; scoping it, not
finding it, is the constraint.

### ⚠ Two unstated rules control the output size
| Rule | Variants tested (same top-50) | Result |
|---|---|---|
| **SKU normalisation (#6)** | strict → split-composite → loose stem | **58 → 7,136 → 7,396 pairs (~125×)** |
| **Keyword match (#9)** | exact phrase vs all-tokens | **2/50 vs 10/50 frontend hits (~5×)** |

Building before these are answered would make the row count an artefact of an assumption rather than a
business decision.

## Next actions
1. Send the decision sheet (#1–#12) to **Thuwaraga**, leading with the SP-API scope question (#1) since it
   decides what is being built.
2. On answers: request a GPT-approved implementation prompt, then build REQ-30-D01/D02 from one read-only
   fetch, reconcile each field against a live anchor, and produce Excel + dashboard.
3. Confirm provisional `PRJ-2026-026` / `REQ-30` / `bgct` with Abiraj (cosmetic).
