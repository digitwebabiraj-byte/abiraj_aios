# Feasibility assessment — REQ-30 BGCT Keyword Gap Sync

**Date:** 2026-08-19 · **Method:** live read-only SQL via `Ledsone-db-mcp`, `sub_source` 8 (LEDSone UK),
`market_place` 23 · **Question asked:** *is this task completely doable?*

The earlier probe (`2026-08-19_data_foundation_probe.md`) established that **the sources exist**. This
document goes further and answers whether **the workflow actually produces rows** — by running the whole
Phase 1 → Phase 2 chain end-to-end on live data.

---

## Verdict in one table

| Part of the spec | Doable? | Evidence |
|---|---|---|
| **Phase 1** — Top-Moving ASINs + SQP top terms | ✅ **Yes, proven** | All 7 export columns map; top ASINs return 34–363 terms each |
| **Phase 2 Step 1** — sales-drop / zero-sales detection | ✅ **Yes, with one correction** | See §2 — must anchor on the catalogue, not the sales table |
| **Phase 2 Step 2** — SKU normalise + base-SKU match | ⚠ **Yes, but the rule decides everything** | See §3 — output swings **~125×** on the rule chosen |
| **Phase 2 Steps 3–5** — Method 1 + Method 2 keyword checks | ✅ **Yes, proven end-to-end** | See §4 — a real pair with real gaps |
| **Phase 2 Step 6** — pre-computed review dashboard | ✅ Yes | Standard build; all inputs derived above |
| **Phase 2 Step 7** — monthly cadence, per account | ✅ Yes | Both accounts present; see the freshness caveat |
| **§2.7 — SP-API automatic write to live listings** | 🔴 **No — out of workbench scope** | Destructive, public, irreversible; no write credential exists here |

**Bottom line: the report is fully buildable today. The write-back is not, and should not be, built here.
Nothing is blocked on missing data — but three unstated rules control the output so strongly that building
before they are answered would produce a number nobody can defend.**

---

## 1. The full chain runs — proven, not asserted

A single query took a Top-Moving ASIN → its live SQP terms → normalised base SKU → a zero-sale sibling →
Method 1 and Method 2 → `status` / `add_target`. Real output:

**Top-Mover `B0B9Y5MRSK`** (37 units/30d, base SKU `CL3TGD`) → **zero-sale twin `B07FNP5GYB`** (0 units in
180 days):

| keyword | monthly volume | in_frontend | in_backend | → add_target |
|---|---|---|---|---|
| **3 core electrical cable** | **4,008** | ❌ | ❌ | `backend_and_bullet` |
| electric cable | 765 | ❌ | ❌ | `backend_and_bullet` |
| light cable | 622 | ❌ | ❌ | `backend_and_bullet` |
| electric cooker cable | 486 | ❌ | ❌ | `backend_and_bullet` |
| bell wire | 349 | ❌ | ❌ | `backend_and_bullet` |
| braided cable | 339 | ❌ | ❌ | `backend_and_bullet` |
| lamp wire | 62 | ✅ | ❌ | `backend` |
| *(8 more)* | … | ❌ | ❌ | `backend_and_bullet` |

This is a genuine, actionable finding: a dead listing missing a 4,008-search/month term that its selling
sibling ranks for. **The workflow does what the spec claims it does.**

---

## 2. 🔴 Correction: "zero sales" cannot be read from the sales table alone

`business_reports.amz_sales_and_traffic_by_asin` is **traffic-driven** — an ASIN gets a row on days it had
sessions, and 51,865 of 55,084 rows in the last 30 days carry `units_ordered = 0` (51,255 of those with
`sessions > 0`). So zero-sale ASINs *are* represented — **but only if they got traffic**.

Measured over 180 days, LEDSone UK:

| Population | Count |
|---|---|
| Catalogue ASINs | 16,963 |
| Present in the sales table | 12,829 |
| — present, but **0 units** in 180 days | **9,195** |
| — present with sales | 3,634 |
| **Absent from the sales table entirely** | **4,650** |

**A query written over the sales table would silently miss 4,650 zero-sale ASINs (27% of the catalogue).**
The zero-sales test must **anchor on `listings.amazon_listings` and LEFT JOIN the sales data**, treating
absence as zero.

Full 6-month zero-sale universe = 9,195 + 4,650 = **13,845 ASINs, 82% of the LEDSone UK catalogue.** The
candidate pool is not the constraint — scoping it is.

---

## 3. ⚠ The SKU normalisation rule swings the output ~125×

Same top-50 Top-Movers, same zero-sales test, three plausible normalisers:

| Normaliser variant | Top-Movers that gained ≥1 sibling | Zero-sale candidate pairs |
|---|---|---|
| **A** strip pack + account suffix + trailing letter | 10 / 50 | **58** |
| **B** A, plus split composite `A+B` SKUs on `+` | 20 / 50 | **7,136** |
| **C** loose alphabetic stem | 21 / 50 | **7,396** |

**58 rows or 7,396 rows — a ~125× difference, from a rule the source document does not state.** The spec
only says "strip pack-size suffixes … e.g. `LDMG95E278` vs `LDMG95E2782PK`". That is variant A, which under
strict matching pairs only **14 of 50** Top-Movers and produces a very small report.

This is the single strongest argument for not guessing open item **#6**.

---

## 4. ⚠ The keyword match rule swings frontend hits ~5×

Same pair, top 50 SQP terms, two plausible match semantics:

| Match rule | Terms found in frontend | Terms found in backend |
|---|---|---|
| **Exact phrase** (`LIKE '%term%'`) | **2 / 50** | 0 / 50 |
| **All tokens present, any order** | **10 / 50** | 0 / 50 |

A 5× swing on the frontend result from open item **#9** alone. Exact-phrase matching will report almost
everything as a gap; token matching is far more forgiving. Neither is "right" without the requester's call.

---

## 5. 🔴 New finding: much of the catalogue has nothing to check

The pilot's twin `B07FNP5GYB` had **156 characters** of frontend content (title only — no bullets, no
description) and **zero characters** of backend keywords. Its 50 "missing" keywords were not 50 individual
oversights; **the listing is simply empty**.

At scale, UK:

| | LEDSone (8) | DCVOLTAGE (6) |
|---|---|---|
| UK listing rows | 18,721 | 16,396 |
| Has bullets | 16,719 | 15,613 |
| Has backend keywords | 15,010 | 14,381 |
| **Backend keyword field EMPTY** | **3,711 (20%)** | **2,015 (12%)** |
| **Title-only (no bullets, no description)** | **1,966 (11%)** | **758 (5%)** |

**Two consequences:**
1. For a listing with an empty backend field, `in_backend = false` is **NO DATA — nothing was read**, not a
   checked miss. Reporting 50 separate "missing backend keyword" rows for one empty field is misleading.
   This is `CLAUDE.md` §4, now proven on the very first pilot pair rather than a theoretical caution.
2. For the ~11% of listings that are title-only, the honest finding is **"this listing has no content"** —
   which is more useful and more actionable than a keyword-by-keyword diff. This is a **new open item (#12)**:
   should such listings be surfaced as their own class rather than as hundreds of keyword gaps?

---

## 6. What this means for effort

| Component | Assessment |
|---|---|
| Phase 1 builder | Straightforward — one query, all columns present |
| Weekly→monthly SQP aggregation | Moderate — rate/share/median must be recomputed, not averaged (#4) |
| SKU normaliser | **The hard part** — needs the requester's rule, then careful testing (#6) |
| Drop/zero-sales detection | Straightforward once anchored on the catalogue (§2) |
| Method 1 / Method 2 matcher | Straightforward — but needs the match rule (#9) |
| Dashboard | Standard, mirrors existing AIOS dashboards |
| Monthly automation | Standard, mirrors the existing fleet |
| **SP-API write-back** | **Not in scope — do not build here** |

No component requires data that does not exist, a new ingestion by Sajeesan, or a scrape. That is the
material difference from **AVM #025** (blocked on absent rating data) and **ECKR #017** (needed a browser
scrape).

---

## 7. Answer to "is this completely doable?"

**Yes — with one exclusion and three decisions.**

- ✅ **Everything the report needs to READ exists and works.** Proven end-to-end, not inferred.
- 🔴 **The one part that is not doable here is the automatic SP-API push** to live Amazon listings. That is a
  deliberate scope boundary, not a technical limitation.
- ⚠ **Three unstated rules control the output**: SKU normalisation (**~125×**), keyword match semantics
  (**~5×**), and the Top-Moving cut-off. Building before these are answered produces a report whose row count
  is an accident of my assumptions rather than a business decision.
- 🟠 **One correction to the spec's own method**: zero-sales must be anchored on the catalogue, or 27% of the
  ASINs are silently missed.
- 🟠 **One new question for the requester (#12)**: how to report listings that have no content at all.

**All queries in this assessment were SELECT-only. No writes, no DDL, no publishes.**

---

## 8. Addendum — "sales above 5 units per month" threshold (measured 2026-08-19)

Asked separately, as a candidate rule for the Top-Moving cut-off (**open item #5**). Not part of the
original assessment. Period **2026-03-01 → 2026-08-17**, Amazon UK, `market_place` 23, both accounts.
"Above 5" read as **`units_ordered > 5` in a calendar month**.

### ASINs selling >5 units, by month
| Month | DCVOLTAGE (6) | LEDSone (8) | DCV any sale | LEDSone any sale |
|---|---|---|---|---|
| 2026-03 | 184 | 194 | 1,393 | 1,510 |
| 2026-04 | 143 | 167 | 1,315 | 1,390 |
| 2026-05 | 154 | 178 | 1,257 | 1,425 |
| 2026-06 | 143 | 178 | 1,211 | 1,332 |
| 2026-07 | 149 | 164 | 1,221 | 1,355 |
| **2026-08 ⚠ partial (1–17 only)** | **30** | **72** | 697 | 1,073 |

**All 6 months** contained ASINs above the threshold. The August collapse is a **period artefact**, not a
sales collapse — the month is 17 days long in this data.

### How consistently each ASIN clears the threshold
| Months above 5 | DCVOLTAGE ASINs | LEDSone ASINs | DCV cumulative (≥) | LEDSone cumulative (≥) |
|---|---|---|---|---|
| 6 of 6 | 9 | 16 | 9 | 16 |
| 5 | 15 | 29 | 24 | 45 |
| 4 | 31 | 32 | 55 | 77 |
| 3 | 48 | 38 | 103 | 115 |
| 2 | 85 | 93 | 188 | 208 |
| 1 | 236 | 284 | **424** | **492** |

### Totals
| Period | Distinct ASINs with ≥1 month above 5 |
|---|---|
| 6 months Mar–Aug (Aug partial) | **913** *(916 account-ASIN rows — only 3 ASINs appear under both accounts)* |
| 5 complete months Mar–Jul | **891** |

### Why this matters for open item #5
Using **">5 units in any one month"** as the Top-Moving rule selects **913 ASINs** — versus 100 under a
Top-100 cut-off. That is roughly a **9× larger** Top-Moving set, and the candidate-pair count scales with it.
Tightening to **">5 units in all 6 months"** gives **25 ASINs** (9 + 16); **≥3 of 6 months** gives **218**.

The threshold rule and the Top-N rule are alternative answers to the same question. Both are available;
which one the requester wants is still #5.

⚠ Read as `> 5` (strictly more than five) **units ordered**. `>= 5`, or a revenue-based threshold, gives
different numbers.

**All queries SELECT-only.**

---

## 9. Top-Moving rule (open item #5) — measured on the document's own period, 2026-08-19

The requester's rule is **"months with sales above 5 units"**. The document's Step 4 defines the period as
the **last 3 consecutive months, checked one month at a time** (extend to 6 if thin). The last 3 **complete**
months are therefore **May, June, July 2026** — August is excluded because the data only runs to the 17th.

Read as `units_ordered > 5` in a calendar month. `market_place = 23`, accounts kept separate.

### How many months had sales above 5 — all 3 did
| Month | DCVOLTAGE (6) | LEDSone (8) | DCV any sale | LEDSone any sale |
|---|---|---|---|---|
| 2026-05 | 154 | 178 | 1,257 | 1,425 |
| 2026-06 | 143 | 178 | 1,211 | 1,332 |
| 2026-07 | 149 | 164 | 1,221 | 1,355 |

### Total ASINs meeting the condition
| Qualifying rule | DCVOLTAGE | LEDSone | **Distinct ASINs** |
|---|---|---|---|
| above 5 in **≥1 of 3** months | 290 | 331 | **621** |
| above 5 in **≥2 of 3** months | 109 | 133 | **242** |
| above 5 in **all 3** months | 47 | 56 | **103** |

Breakdown by exact count of qualifying months:

| Months above 5 | DCVOLTAGE | LEDSone |
|---|---|---|
| 3 of 3 | 47 | 56 |
| 2 of 3 | 62 | 77 |
| 1 of 3 | 181 | 198 |

**No ASIN appears under both accounts in this window** — 621 account-rows = 621 distinct ASINs.

### 6-month fallback (the document's "extend to 6 months if thin")
Mar–Aug 2026: **913** distinct ASINs above 5 in ≥1 month; **218** in ≥3 months; **25** in all 6.
*(August is partial — see §8.)*

### Recommendation for the Step 1 rule
**"Above 5 units in all 3 months" → 103 Top-Moving ASINs.** A Top-Moving ASIN should be a *consistent*
seller; a single good month is a spike, not a trend, and the document itself stresses checking months
separately and keeping ranges consistent. 103 ASINs is also a workable report size.

⚠ Read as **strictly more than 5** units ordered. `>= 5`, or a revenue-based threshold, gives different
numbers. Still to confirm: which of the three thresholds above.

**All queries SELECT-only.**

---

## 10. PILOT RUN — full pipeline on all confirmed rules (2026-08-19)

First complete run of Phase 1 → Phase 2 with every confirmed rule applied. Read-only; no files produced.

**Rules used**
| Rule | Setting |
|---|---|
| Top-Moving (Q5) ✅ | `units_ordered > 5` in **all 3** months — May, June, July 2026 |
| Underperformer | `zero_sales_6mo` only — Feb–Jul 2026, **catalogue-anchored**, absence = zero |
| SKU base (Q6) ✅ | pack size + trailing letters + account suffixes stripped; **bundles whole** |
| Keyword match (Q9) ✅ | all words present anywhere, any order, case/punctuation ignored |
| Terms per ASIN | top 50 by volume *(open #10 — 30 or 50 not yet confirmed)* |
| Write-back (Q1) ✅ | none — report only |

### Funnel
| Stage | Result |
|---|---|
| Top-Moving ASINs (>5 units in all 3 months) | **103** *(201 ASIN × base-SKU combinations — some ASINs carry several SKU forms)* |
| Top-Movers that have a dead twin | **41** |
| **Candidate pairs** | **71** — 27 DCVOLTAGE, 44 LEDSone |
| Distinct dead listings | 71 |
| **Report rows (pair × keyword)** | **2,212** |

### Output breakdown — the §2.7 truth table, on real data
| status / add_target | rows | share | of which: backend field is EMPTY |
|---|---|---|---|
| `gap` / **`backend_and_bullet`** | 1,383 | 62.5% | 761 |
| `gap` / **`backend`** | 569 | 25.7% | 401 |
| `present` / `none` | 182 | 8.2% | — |
| `gap` / **`bullet`** | 78 | 3.5% | — |
| **Total** | **2,212** | | **1,162** |

### 🔴 The headline finding — half the dead listings are simply empty
Of the **71** dead listings in this run:

| Condition | Count | Share |
|---|---|---|
| **Backend keyword field completely empty** | **37** | **52%** |
| No bullet points at all | 29 | 41% |
| No description | 33 | 46% |

**Those 37 empty-backend listings generate 1,162 of the 2,030 gap rows — 57% of all gaps.** They are not
1,162 individual keyword oversights; they are 37 listings that were never filled in. Reporting them
keyword-by-keyword would bury the real finding.

**This makes open item #12 the most valuable remaining question.** Recommended output shape:
- a **"listing has no content"** class listing those 37 (and the 29 with no bullets), fixed by a rewrite;
- the genuine keyword-gap rows — roughly **850 rows across the remaining 34 listings** — where the listing
  *does* have content and specific proven terms are missing.

### ⚠ Scope note on this run
Only **`zero_sales_6mo`** was included. **`sales_drop_3mo` is NOT in these numbers** because its test is
still open (#8) — "declined over 3 consecutive months" is not quantified in the source. Adding it will
increase the pair count.

**All queries SELECT-only.**

---

## 11. FINAL PILOT — all rules confirmed (2026-08-19)

Second full run, now with **every business rule confirmed**. Read-only; no files produced.

### Confirmed rule set
| # | Rule | Setting |
|---|---|---|
| Q1 ✅ | Amazon write | **None.** Report only; a person applies the keywords |
| Q5 ✅ | Top-Moving | `units_ordered > 5` in **all 3** months (May, Jun, Jul 2026) → **103 ASINs** |
| Q6 ✅ | Base SKU | strip pack size + trailing letters + account suffixes; **bundles kept whole** |
| Q8 ✅ | Sales drop | **strictly falling** — May > Jun > Jul, with May > 0 |
| Q8 ✅ | Zero sales | 0 units Feb–Jul 2026, **catalogue-anchored** (absence = zero) |
| Q9 ✅ | Keyword match | all words present anywhere, any order, case/punctuation ignored |
| Q12 ✅ | Empty listings | **separated into Part A** — one row each, not one row per keyword |
| #10 🟠 | Terms per ASIN | 50 (still unconfirmed — 30 or 50) |

### Candidate pairs — 79 total
| duplicate_status | DCVOLTAGE | LEDSone | Total |
|---|---|---|---|
| `zero_sales_6mo` | 27 | 44 | **71** |
| `sales_drop_3mo` | 6 | 2 | **8** |
| **Total** | **33** | **46** | **79** |

The strictly-falling drop test (Q8 option A) is deliberately tight — it adds only 8 pairs. A looser test
("July lower than May") would add more; the requester chose the strict reading.

### The Q12 split
| Part | Listings | What it says |
|---|---|---|
| **A — listing is empty** | **39** | No backend keywords and/or no bullets at all. **Needs a rewrite, not keyword edits.** One row per listing. |
| **B — real keyword gaps** | **40** | Listing has content; specific proven terms are missing. One row per keyword. |

Part A by account: DCVOLTAGE 9, LEDSone 30.

### Part B output — 1,130 keyword rows
| status / add_target | rows | share |
|---|---|---|
| `gap` / **`backend_and_bullet`** | 660 | 58.4% |
| `present` / `none` | 208 | 18.4% |
| `gap` / **`backend`** | 181 | 16.0% |
| `gap` / **`bullet`** | 81 | 7.2% |
| **Total** | **1,130** | |

**922 real, actionable keyword gaps** across 40 listings — plus 39 listings flagged for rewrite. Compare
with the un-split run (§10): 2,212 rows of which 1,162 were an artefact of empty fields. The Q12 split
removes that noise entirely.

### Verdict
**Every rule is now confirmed and the pipeline runs end to end on live data.** The remaining open items
(#2 Phase-1 source, #3 row-level account scope, #4 monthly window, #7 SKU mapping table, #10 term count,
#11 publish audience and cadence) refine the output but do not block the build.

**All queries SELECT-only.**

---

## 12. BUILD — REQ-30-D01 / D02 produced (2026-08-19)

Built on owner instruction. ⚠ **Governance note:** the workbench rule requires a GPT-approved
implementation prompt before code is written; the owner instructed the build directly. Recorded, not
hidden.

**Modules** (read-only, single fetch path):
`sql/REQ-30_amazon-keyword-gap-sync/build_bgct_d01.py` → `bgct_payload.json` + both Excel workbooks ·
`render_bgct_dashboard.py` → the HTML dashboard from the same payload snapshot.

Run: `BGCT_REFERENCE_DATE=2026-08-19 python build_bgct_d01.py` → period **2026-05-01 … 2026-07-31**,
zero-sales window from **2026-02-01**.

### Output
| Deliverable | Contents |
|---|---|
| `REQ-30-D01_sqp_top_terms.xlsx` | Notes & Method · SQP dcvoltage_uk (688 rows) · SQP ledsone_uk (1,001) · Top-Moving ASINs (103) |
| `REQ-30-D02_keyword_gap_report.xlsx` | Notes & Method · **Part A — No Content (38)** · **Part B — Keyword Gaps (542)** · Field Reference |
| `REQ-30-D02_keyword_gap_dashboard.html` | 150 KB self-contained · KPI tiles · per-account sections · Part A table · 28 Part B pair panels with the two §2.7 buttons |

### Result
| Measure | Value |
|---|---|
| Top-Moving ASINs | **103** |
| …with ≥1 converting SQP term | **81** |
| Phase 1 terms | **1,689** (avg 20.9/ASIN; 368 flagged long-tail) |
| Underperforming listings | **66** — Part A 38 + Part B 28 |
| Part B keyword rows | **542**, of which **381 gaps** |
| `add_target` split | backend_and_bullet 227 · none 161 · backend 94 · bullet 60 |
| `duplicate_status` | zero_sales_6mo 546 · sales_drop_3mo 34 |
| QA (§2.10) | **6/6 PASS** — account separation · one-place-is-enough · dual-method independence · directional-add truth table (100% of rows) · zero manual lookup · monthly cadence |

### ⚠ Why these numbers differ from the §11 pilot (79 pairs / 1,130 rows)
The builder applies the source's **Step 6 zero-conversion filter** (*"Filter out terms with zero
conversion to avoid wasted optimisation effort"*), which the pilot did not. Effect: terms per ASIN fall
from the 50 cap to an average of **20.9**, and **22 of 103 Top-Moving ASINs return no converting terms at
all**, so their pairs produce no rows. The filter is stated in the source, so it is applied; the pilot
figures were pre-filter. Neither set is wrong — they answer different questions.

### Verified in-browser
Dashboard opened and inspected. Worked example rendering correctly — Top-Mover `B0F1D3FS5C` →
zero-sale twin `B0DZWY1Y2J` (base SKU `RWWPSY0660YE`), showing all four §2.7 outcomes on one screen:

| keyword | volume | frontend | backend | → |
|---|---|---|---|---|
| rawl plugs | 4,391 | ✓ | ✗ | **Add to backend** |
| wall plugs | 3,179 | ✓ | ✓ | present |
| rawplugs for brickwork | 91 | ✗ | ✓ | **Add to bullets** |
| rawlplugs | 98 | ✗ | ✗ | **Add to backend + bullets** |

### Still not done
Not validated (no reconciliation report), **not published**, **not automated**, **not committed**.
Open items #2, #3, #4, #7, #10, #11 remain; Thuwaraga's business confirmation is outstanding.

**Build was read-only throughout. No writes, no DDL, no publish, and no Amazon API call of any kind.**

---

## 13. 🔴 SCOPE ERROR FOUND AND CORRECTED — the PH filter was missing (2026-08-19)

Found by the owner asking *"did you find Thuwaraga's ASINs only, or what?"* The answer was **no**.

### What was wrong
The first build (§12) ran across **the entire Amazon UK catalogue for both accounts — 35,117 listing
rows / ~32,000 ASINs**. No per-requester filter was applied, because the source document names the
scope only as *"Amazon UK LED Bulb Listings"* and I read that as a description rather than a filter.

**Thuwaraga is a Portfolio Holder with exactly one category:**

```sql
SELECT c.id, c.category_name, c.user_id, COUNT(p.ref_id)
FROM staff.ph_categories c
LEFT JOIN staff.ph_category_products p ON p.ph_category_id = c.id
WHERE c.user_id = 122 GROUP BY 1,2,3;
-- 65 | Bulbs | 122 | 1,217 products across 3 sources
```

Her category is **"Bulbs"**. The source says **"LED Bulb Listings"**. They are the same scope, and it was
sitting in the database the whole time.

`staff.ph_category_products.ref_id` is polymorphic by `source_id`: **1 = Amazon** (776 refs, **all 776
match `listings.amazon_listings` UK sub_source 6/8**), 2 = eBay item ids (287), 16 = barcodes (154).
So her Amazon UK scope is **776 ASINs**, not 32,000.

### The damage
**Only 5 of the 66 listings in the first build were hers — 92% of the report was out of scope.** The
symptom was visible in the output and I did not read it: the top recommendations were **"rawl plugs"**
(wall fixings), **"ceiling fan"** and **"wall lights"**. None of those is a bulb.

### The fix
`RULES["ph_category_id"] = 65` / `ph_source_id = 1` now filters the catalogue, and the filter applies to
**Top-Moving ASINs as well as underperformers** — a keyword proven on a product outside her category is
not evidence for a product inside it. Set `ph_category_id = None` to run the whole estate, and the run
log says which mode it used.

### Before and after
| | Whole catalogue (wrong) | PH "Bulbs" scope (correct) |
|---|---|---|
| ASINs in scope | ~32,000 | **776** |
| Top-Moving ASINs | 103 | **11** |
| …with converting SQP terms | 81 | **9** |
| Phase 1 terms | 1,689 | **184** |
| Part A (rewrites) | 38 | **3** |
| Part B listings / rows / gaps | 28 / 542 / 381 | **2 / 4 / 4** |
| QA (§2.10) | 6/6 PASS | **6/6 PASS** |

### 🟠 Consequence — the Top-Moving rule now needs revisiting
"Above 5 units in all 3 months" was chosen while looking at whole-catalogue numbers, where it selected
103 ASINs. Inside her actual 776-ASIN category it selects **11**, and the finished report is **5 listings
and 4 keyword gaps** — a very thin month's work.

Measured within her scope:

| Top-Moving rule | Her ASINs selected |
|---|---|
| above 5 units in **all 3** months | **11** |
| above 5 units in **≥2 of 3** months | 30 |
| above 5 units in **≥1 of 3** months | 56 |
| any sales at all in the period | 258 |
| (her Amazon UK category total) | 776 |

The rule is not wrong — but it was calibrated against the wrong population, so it should be re-chosen now
that the scope is right. **Requester's decision.**

### Lesson
**A named requester is a scope filter, not just a sign-off name.** `staff.ph_categories` /
`ph_category_products` map every PH to the products they own; check it during onboarding, not after the
build. A report that silently spans another PH's products is wrong even when every figure in it is
correct — and here the wrongness was visible in the output ("rawl plugs") a step before anyone asked.

---

## 14. FINAL BUILD — PH-scoped, Top-Moving rule re-chosen (2026-08-19)

After the §13 scope correction the Top-Moving threshold was re-chosen, because "all 3 months" had been
selected against whole-catalogue numbers and yielded only 11 of the requester's 776 bulbs.

**Rule now: `units_ordered > 5` in AT LEAST 2 of the 3 months.** Still a repeat seller, not a one-month
spike.

🔴 **Latent bug fixed in the same change.** The Top-Moving test read
`count == months_required`. At 3-of-3 that was accidentally correct; at 2 it would have selected ASINs
that sold in *exactly* two months and **excluded every three-month seller**. Changed to `>=`.
Also fixed: the dashboard's rule caption was a hardcoded string reading "in all 3 months" — it now
derives from the payload, so the deliverable can never misstate the rule it was built on.

### Final output
| Measure | all-3 (previous) | **≥2-of-3 (final)** |
|---|---|---|
| Top-Moving ASINs | 11 | **30** |
| …with converting SQP terms | 9 | **24** |
| Phase 1 terms | 184 | **359** |
| Part A — rewrites | 3 | **6** |
| Part B — listings / rows / gaps | 2 / 4 / 4 | **22 / 225 / 216** |
| QA (§2.10) | 6/6 PASS | **6/6 PASS** |

`add_target`: backend_and_bullet 184 · bullet 18 · backend 14 · none 9.
`duplicate_status`: zero_sales_6mo 221 · sales_drop_3mo 10.
Accounts: Part A all LEDSone (6); Part B LEDSone 209 rows, DCVOLTAGE 16.

Verified in-browser: tiles, Part A table, Part B pair panels and the two §2.7 buttons all render, and
the rule caption now reads "at least 2 of 3 months".

**Read-only throughout. No Amazon API call of any kind. Still DRAFT — not validated, not published,
not automated.**

---

## 15. 🔴 SKU NORMALISER BUG — found by the owner in the Listing Management tool (2026-08-19)

The owner opened the two ASINs from the §14 worked example in the listing tool and their SKUs did not
belong together. **He was right — the pairing was wrong.**

### The bug
`_TAIL_RE = r"\s*([0-9]+PK)?(\s*-?[A-Za-z]{1,2})?$"` — `[0-9]+PK` is **greedy**. It consumed the product
code as well as the pack quantity:

| SKU | product | old base | correct base |
|---|---|---|---|
| `LDMST64E2786PK` | 8W ST64, 6-pack | `LDMST64E` | **`LDMST64E278`** |
| `LDMST64E2746PK` | 6W ST84, 6-pack | `LDMST64E` | **`LDMST64E274`** |

Two genuinely different bulbs collapsed to the same base SKU and were paired as one product — a
Top-Moving 8W ST64 was used as the keyword source for a dead 6W ST84.

**The source document's own example was the test I failed to run.** It states
`LDMG95E278` = `LDMG95E2782PK` = `LDMG95E2785PK`. My rule returned `LDMG95E` for the pack variants and
`LDMG95E278` for the single — so under my own rule the spec's example **did not even match itself**.
Every §12–§14 pairing is suspect as a result.

### The fix
Pack quantity is a **single digit** glued to `PK`. Verified across the catalogue: every multi-digit
capture before `PK` is product code + a 1-digit pack (`…2786PK` = product `…278` + `6PK`; last digits
observed are 2–6, none ending 0 or 1, so no 10PK/12PK forms exist).

The normaliser now strips **repeatedly until stable**, in the right order:
1. separator-introduced markers — `[\s\-_][A-Za-z]{1,4}[0-9]{0,2}$` (` D`, ` AM`, `-B1`, `-AFR`, `-DC`, `_DCVV`)
2. pack quantity — `([0-9])PK$`

Verified:

| SKU | base |
|---|---|
| `LDMG95E278` / `LDMG95E2782PK` / `LDMG95E2785PK` / `LDMG95E278 M` / `LDMG95E278-DC_DCVV` | **`LDMG95E278`** ✅ all match |
| `LDMST64E2786PK` / `-B1` / `-AFR` / ` AM` / `amzn.gr.LDMST64E2786PK-B1-60H9yWgQhY6-LN` | **`LDMST64E278`** ✅ |
| `LDMST64E2746PK` / `LDMST64E2746PK D` | **`LDMST64E274`** ✅ correctly separate |
| `CRSF100BM+PHHT1PBRBM+LSFT320DG` | unchanged ✅ bundle kept whole |

**Two assertions now run at import time** so this can never silently regress: the source's worked
example must match itself, and `LDMST64E2786PK` must not equal `LDMST64E2746PK`.

### Effect on the report
| | §14 (broken rule) | **corrected** |
|---|---|---|
| Top-Moving ASINs | 30 | 30 |
| Part A — rewrites | 6 | **18** |
| Part B — listings / rows / gaps | 22 / 225 / 216 | **13 / 144 / 115** |
| `add_target` | b+b 184 · bullet 18 · backend 14 · none 9 | b+b 89 · none 29 · backend 18 · bullet 8 |
| QA (§2.10) | 6/6 | **6/6** |

The wrong pair `B0BLP1JSRK → B0CNTH491L` is gone. Base SKUs are now real product codes —
`LDMG95E278`, `LDMG125E278`, `LDMST64E274`, `LDMST64E278`, `LDMG80E274`.

Part A rose from 6 to 18 because tighter matching re-paired listings against their *actual* twins, and
more of those twins turn out to be empty listings.

### Lesson
**When the source document contains a worked example, make it an automated assertion before building
anything on the rule.** The example was quoted verbatim in `SOURCE_MANIFEST.md`, `SYSTEM_REFERENCE.md`
and the implementation plan — and never executed. It would have failed on the first run.
Second lesson: a greedy quantifier next to a product code is a silent data-merge, and the QA checklist
did not catch it because every §2.10 check passed on wrongly-paired rows.

---

## 16. Owner spot-check in the Listing Management tool — §15 fix CONFIRMED, one more marker found

The owner checked the corrected pairs in `listings.vintageinterior.co.uk` and sent four screenshots.

### ✅ The §15 fix is right — both pairs verified as the same product
| ASIN | SKU | pack | base SKU |
|---|---|---|---|
| `B0BLP1JSRK` (Top-Moving) | `LDMST64E2786PK` | 6-pack | `LDMST64E278` |
| `B0BLNZS78D` (dead) | `LDMST64E2782PK` | 2-pack | `LDMST64E278` |
| `B0BLP1LN2C` (dead) | `LDMST64E278` | single | `LDMST64E278` |

Exactly the shape the source document describes (single / 2-pack / 5-pack of one product), on a real
family. Both pairings are correct. Titles disagree with each other on ST64 vs ST84 across markets — a
listing-content inconsistency, not a matching error; the SKU family is unambiguous. **Both assertions
added to the builder so this family stays verified.**

### 🔴 New finding from the same screenshots — 'A' is the 10-pack marker
The listings page showed one product's German family:

| SKU | title says |
|---|---|
| `LDSG125MUE274APK _DE` | **(10er-Packung)** |
| `LDSG125MUE2746PK_DE` | (6er-Packung) |
| `LDSG125MUE2745PK _DE` | (5er-Packung) |
| `LDSG125MUE2743PK_DE` | (3er-Packung) |

**`APK` = 10-pack, not a numeric suffix.** Measured: **4,208 rows carry an `APK` suffix across 1,635
ASINs**; **487** of their titles say "pack of 10" and **414** say "10er-Packung". The §15 rule
`([0-9])PK$` did not strip it, so `LDMG95E274APK` survived as its own base SKU and 10-packs were
separated from the rest of their family.

Fixed to `([0-9A])PK$`, with an assertion: `LDSG125MUE274APK` and `LDSG125MUE2746PK` must both give
`LDSG125MUE274`.

### Effect
| | §15 | **§16 (APK fixed)** |
|---|---|---|
| Part A — rewrites | 18 | **21** |
| Part B — listings / rows / gaps | 13 / 144 / 115 | **16 / 191 / 149** |
| Base SKUs still containing "PK" | 1 (`LDMG95E274APK`) | **0** |
| QA (§2.10) | 6/6 | **6/6** |

### Lesson
**A pack marker is not necessarily a digit.** Two rounds of this bug came from assuming the SKU grammar
instead of reading it off the catalogue. The owner's spot-check in the operational tool found in minutes
what the QA checklist structurally cannot see — the checklist verifies that rules were applied, never
that the rule matches reality.

---

## 17. 🔴 WRONG SKUs IN THE CATALOGUE — Part C added (owner spot-check, 2026-08-19)

The owner searched SKU family `LDMG125E278` in the Listing Management tool. Nine listings came back —
eight are **8W dimmable G125**, one is not:

| ASIN | SKU | title says |
|---|---|---|
| B09M42FP91 · B09M42QJCS · B0CNQ1Q3BJ · B0B8SRVWSP · B0DQ8TM75J · B0B8SP4JD1 | `LDMG125E278…` | **8W** dimmable |
| **`B0B8P75R4Y`** | **`LDMG125E2782PK`** | **4W, non-dimmable** |

The SKU grammar encodes wattage — `LDMG125` + `E27` + **`8`** = G125, E27 fitting, 8W. So
`B0B8P75R4Y` carries an **8W SKU on a 4W bulb**. The normaliser grouped it correctly *by SKU*; the SKU
itself is wrong.

**The existing flag does not catch it:** `wrong_sku = 0`, `mapped_sku = null`. This is precisely the
case the source's Phase 2 Step 2 anticipates — *"Where a listing's stored SKU doesn't match its real
product, correct it against the SKU mapping table"* — and it resolves **open item #7**: `wrong_sku`
cannot serve as that mapping table.

### Scale, measured inside the requester's category
| | |
|---|---|
| Listings where both SKU wattage and title wattage are readable | **518** |
| They agree | 394 |
| **They DISAGREE** | **124 (24%)** |
| …of those, flagged `wrong_sku = 1` | **4 (3%)** |

### The fix — Part C, reject rather than guess
A pair is now **rejected** when both listings state a wattage and the two disagree. The report never
decides which listing is wrong; it surfaces the conflict:

> *"same base SKU but the listings state different wattage (8W vs 4W) — the stored SKU looks wrong"*

Wattage is read from the title, taking the **minimum** of the numbers found, because Amazon titles
state it twice (`8W (Equivalent 60W)`) and the equivalent figure is always the larger incandescent
comparison. A new QA assertion `2_sku_mismatch_never_paired` guards it.

### What Part C caught
| base SKU | Top-Moving | dead listing | verdict |
|---|---|---|---|
| `LDMG125E278` | B0B8P9BKXB **8W** | **B0B8P75R4Y 4W** | rejected — the owner's find |
| `LDCWB223` | B09Z6P8H29 **7W** | B0D5CMBXK6 **3W** | rejected |
| `LDMST64E278` | B0BLP1JSRK **8W** | **B0D7HPWK2P 4W** | rejected |

The third is notable: `B0D7HPWK2P` was one of the three pairs put to the owner for checking in §16.
The automated check found it independently — **the two verification routes agree**.

### Effect
| | §16 | **§17 (Part C)** |
|---|---|---|
| Part A — rewrites | 21 | **20** |
| Part B — listings / rows / gaps | 16 / 191 / 149 | **14 / 150 / 115** |
| **Part C — rejected, SKU wrong** | — | **3** |
| QA | 6/6 | **7/7** (new mismatch check) |

### Lesson
**Matching on an identifier assumes the identifier is right.** 24% of comparable listings here contradict
their own SKU, and the system's `wrong_sku` flag catches 3% of those. Any report that joins products by
SKU needs an independent cross-check on an attribute the SKU claims — here, wattage from the title.
Three rounds of SKU bugs (§15 greedy pack, §16 APK marker, §17 wrong SKUs) were all found by the owner
opening the operational tool, never by the QA checklist.
