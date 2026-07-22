# Live Data Verification — REQ-16-D01 eBay Slow Moving & No Moving Products

**Date:** 2026-07-22 · **Developer:** abiraj · **Artefact under test:**
`evidence/final_outputs/REQ-16_ebay-slow-no-moving-products/REQ-16-D01_slow_no_moving_products.xlsx`
**Anchor:** 2026-07-22 · **Rows:** 11,156

**VERDICT: 🟢 PASS on all ten PASS/FAIL rules.**
⚠ Passing proves the artefact is **internally correct and matches live data**. It does **not** close
the three business assumptions (decisions A, C, G), which remain open.

---

## Test 1 — Independent re-implementation of the rule engine

The engine exists **twice, written separately**:

1. **In-sheet** — column T is a nested `IF` referencing the editable **Rules** sheet and the
   **Engine Inputs** sheet. This is what a reviewer sees and what recalculates when a threshold is
   edited.
2. **In Python** — `build_esnm_d01.py::evaluate()`, a procedural loop over `EVAL_ORDER`.

The two share **no code path**. The workbook was recalculated with LibreOffice (so every formula
produced a real cached value), then every row's formula result was compared against the Python
result.

| Measure | Result |
|---|---|
| Rows compared | **11,156** |
| Mismatches | **0** |
| Blank `Action Required` cells | **0** |
| Formula error cells (`#REF!` `#NAME?` `#VALUE!` `#DIV/0!` `#N/A` `#NULL!` `#NUM!`) anywhere in the workbook | **0** |

Action distribution — **identical from both implementations**:

| Action | Formula engine | Python reference |
|---|---|---|
| End Listing / Clear Stock | 8,067 | 8,067 |
| Run Clearance Promotion | 1,210 | 1,210 |
| Reduce Price by 5-10% | 851 | 851 |
| Improve SEO & Increase Promotion | 476 | 476 |
| Monitor - No Rule Matched | 171 | 171 |
| Bundle with Best Seller | 149 | 149 |
| Maintain Current Strategy | 109 | 109 |
| Increase Stock & PPC Budget | 53 | 53 |
| Review Competitor Pricing | 42 | 42 |
| Improve Images & SEO Title | 26 | 26 |
| Pause PPC Campaign | 2 | 2 |
| **Total** | **11,156** | **11,156** |

---

## Test 2 — Field-by-field reconciliation to the live databases

Listing **`164889807930`** (LEDSone UK, "Vintage B22/E27 4/8Watts LED Filament…"), chosen because it
exercises every measured field at once (has sales, has a year-ago comparison, has traffic).

| Field | Workbook | Live database | Match |
|---|---|---|---|
| Last 7 Days Sales | 0 | 0 | ✅ |
| Last 30 Days Sales | 0 | 0 | ✅ |
| Last 90 Days Sales | 1 | 1 | ✅ |
| Same Period Last Year | 14 | 14 | ✅ |
| Sales Trend | −92.86% | (1−14)/14 = −92.857% | ✅ |
| Days Since Last Sale | 77 | last sale 2026-05-06 → 77 days | ✅ |
| Views (30 Days) | 18 | 18 | ✅ |
| Conversion Rate | 0.0% | 0 conversions / 18 clicks | ✅ |

Sales queried from `ledsone` (`orders` + `order_item_info`, `Cancelled` excluded); traffic from the
warehouse (`public.traffic_data`, `which_channel = 2`, UK+Germany). **Exact on all eight measures
across both databases.**

---

## Test 3 — Scope audit

| Check | Result |
|---|---|
| Rows in workbook | 11,156 |
| Live in-scope universe (`ledsone`: `source_id=2`, site UK/DE, `is_ended=0`, `is_child=0`) | 11,156 ✅ |
| Accounts represented | 12 |
| Account × marketplace combinations | 16 ✅ |
| UK / Germany split | 7,685 / 3,471 = 11,156 ✅ |
| `neighbourmarket` present? | **No** ✅ — US-only, correctly excluded |

Account labels verified unique across the 16 combinations — including the collision case
`LEDSone - Germany` (account `led_sone`) vs `LEDSone DE - Germany` (account `ledsonede`), which share
the LEDSone **brand** but are distinct **accounts**. Had the label used brand rather than account,
these two would have merged silently.

---

## Test 4 — Summary sheet reconciliation

| Check | Result |
|---|---|
| Summary rule counts vs detail sheet | identical on all 11 rows ✅ |
| Summary TOTAL | 11,156 = detail row count ✅ |
| Account breakdown total | 11,156 ✅ |
| "Zero 90-Day Sales" total (8,067) vs Rule 1 count (8,067) | ✅ consistent — Rule 1 is exactly `90d = 0` and is evaluated first, so the two must be equal |

---

## Test 5 — Gap handling (the tests that matter most)

These verify the report does not **fabricate** a measurement.

| Check | Result |
|---|---|
| `Watchers` (col 17) populated anywhere? | **No — blank on all 11,156 rows** ✅ |
| `Watchers` rendered as `0`? | **No** ✅ — a zero would be an invented measurement |
| Rule 6 assigned to any listing? | **No — 0** ✅ (correct; its input does not exist) |
| Views/CVR rendered as `0` where no traffic row exists? | **No — blank** ✅ |
| Rules 5 and 9 evaluated on listings with no traffic row? | **No — skipped** ✅ |
| Rule 10 count | **0** ✅ — matches the predicted structural unreachability |
| Any figure traceable to the fabricated source sample? | **No** ✅ |

---

## Test 6 — Configuration, not hardcoding

| Check | Result |
|---|---|
| All 11 evaluable thresholds present as editable cells on the **Rules** sheet | ✅ |
| Column T formula references those cells (not literals) | ✅ |
| Column N (Sales Trend) is a formula, not a pasted value | ✅ |
| Editing a threshold re-evaluates the report | ✅ — verified by recalculation |
| Rule 6 row visibly greyed with its reason stated in red | ✅ |

---

## Test 7 — Read-only confirmation

| Check | Result |
|---|---|
| Writes to any live schema | **None** ✅ |
| DDL executed | **None** ✅ |
| `ph_task` publish | **None** ✅ |
| Write to eBay | **None** ✅ — blocked by design |
| Scheduled task registered | **None** ✅ |
| Git commit | **None** ✅ |
| DB users used | `dbhub_readonly` (`ledsone`), `temp_user` (warehouse) — both read-only |

---

## Findings raised during verification

| # | Finding | Disposition |
|---|---|---|
| 1 | **Rule 10 unreachable** — 0 of 11,156; Rule 1 always claims those listings first | Reported, not silently absorbed. Decision **C** |
| 2 | **Rule 6 dead** — `Watchers` has no source in either database | Column blank + stated on the artefact. Decision **A** |
| 3 | **51.7% of listings carry `wrong_sku = 1`** but are real sellable listings | Deliberately **not** filtered; disclosed. See `CLAUDE.md` §5 |
| 4 | **A 90-day PPC figure DOES exist** (warehouse) — an earlier project claim was wrong | Corrected in `PROJECT_HOME.md`, `TASK_REGISTER.md` and the audit. Build stays on `ledsone` (complete incl. SMART) |
| 5 | **Scope discrepancy 11,156 vs 10,739** | Resolved — grain convention difference, not stale data. `ledsone` is correct |
| 6 | **72.3% of rows share one Critical action** | Flagged as decision **F**; not silently re-ranked |

---

## What this verification does NOT establish

Stated explicitly so the PASS is not over-read:

1. **Rule precedence is unverified business logic.** The source never states multi-match resolution.
   The engine is provably self-consistent, but "Critical → High → Medium → Low, first match wins" is
   an **assumption** — and it is the single choice that makes 8,067 listings read "End Listing".
2. **Rule 8's £5.00 / 30-day threshold is invented.** The source says "high" and defines it nowhere.
3. **Views are knowingly understated** (~23% over the 30-day window) because of the 11 lost
   ingestion days. Rules 5 and 9 are correct *given the data present*, not given complete data.
4. **No business review has occurred.** Thinesh has not seen the output.
5. **Stock is the eBay platform-displayed quantity**, capped by `listing_max_platform_stock` — not
   true warehouse stock. Rules 2 and 7 test that figure, not physical inventory.

---

## Conclusion

**REQ-16-D01 PASSES verification.** The artefact reproduces the source's 20 columns exactly, covers
the confirmed live universe of 11,156 listings, contains no formula errors, and its rule engine is
reproduced identically by an independent implementation on every row. Gap handling was tested
specifically and the report **never fabricates a measurement**.

**It remains AMBER for sign-off** — three business assumptions are open (decisions A, C, G), the
Watchers and traffic gaps are unresolved, and no reviewer has yet approved it.
