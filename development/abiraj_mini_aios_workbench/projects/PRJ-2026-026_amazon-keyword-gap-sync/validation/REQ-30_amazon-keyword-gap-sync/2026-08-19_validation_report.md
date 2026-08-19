# VALIDATION REPORT — REQ-30-D01 / D02 (bgct)

**Date:** 2026-08-19 · **Verdict:** 🟢 **10 / 10 checks PASS** · **Method:** every headline figure
recomputed independently against the live DB and compared with the delivered payload — not re-read from
the builder's own working.

## Result

| # | Check | Report | Independent | |
|---|---|---|---|---|
| 1 | Scope is the requester's own `staff.ph_categories` 65 "Bulbs" | 776 ASINs | 776 | ✅ |
| 2 | Top-Moving ASINs (>5 units in ≥2 of 3 months), recomputed in pure SQL | 30 | 30 | ✅ |
| 3 | Every `zero_sales_6mo` listing truly sold 0 units Feb–Jul | 0 exceptions | 0 | ✅ |
| 4 | All **124** distinct keywords trace to a real `amz_search_query_performance` row | 0 missing | 0 | ✅ |
| 5 | Every Part A listing genuinely lacks bullets **or** backend keywords | 0 exceptions | 0 | ✅ |
| 6 | No listing appears in more than one Part | 0 overlaps | 0 | ✅ |
| 7 | `add_target` matches the source's §2.7 truth table on **every** row | 0 violations | 0 | ✅ |
| 8 | The two accounts are never merged | 0 violations | 0 | ✅ |
| 9 | Rejected (Part C) pairs never appear in Part A or B | 0 leaks | 0 | ✅ |
| 10 | Every reported listing exists in the live catalogue | 51 | 51 | ✅ |

Plus the builder's own 7 in-run QA assertions (source §2.10) — **7/7 PASS** — and 6 import-time
assertions on the SKU and fitting rules that abort the build if either regresses.

## Three defects the validation found and fixed

**1. Part A over-reported — content read from one listing row.** An ASIN commonly has several listing
rows (per market / SKU variant) and its bullets or backend keywords may sit on a different row from the
one sampled. Three listings were labelled "no content" while holding content on a sibling row.
First fix (aggregate within the base-SKU family) still missed **2**, because an ASIN's rows can
normalise to *different* base SKUs once `mapped_sku` is applied. Now indexed by `(account, ASIN)`
directly. **Part A 25 → 22; those listings moved to Part B where they are actionable.**

**2. The cap-fitting check was silently disabled.** `\b` in the regex had been written to the file as a
literal **backspace character (0x08)**, so `title_fittings()` returned `None` for every title and the
check never fired — it looked like "0 mismatches found" rather than an error. Two genuinely wrong pairs
(screw vs bayonet) were passing straight into the report. Now fixed, with **4 import-time assertions**
so a broken regex fails the build loudly instead of quietly doing nothing.

**3. Screw/bayonet pairs were being matched at all.** `B0D7MDP9XP` and `B0DTHWWCZS` are **B22 bayonet**
bulbs sharing a base SKU with **E27 screw** twins. They do not fit the same socket. Recommending a screw
bulb's keywords onto a bayonet listing would be wrong. Both now rejected into Part C.

## Also checked, no defect found
- **Shape consistency** (G125 / G95 / G80 / ST64 / T45 / T185 / A60 / A95) across all 52 pairs — **0 mismatches**.
- **`wrong_sku = 1` rows** — 55 exist in scope; none causes a bad pair after `mapped_sku` is applied.

## Final figures
| | |
|---|---|
| Top-Moving ASINs | **30** (24 with converting SQP terms) |
| Phase 1 search terms | **359** |
| Underperforming listings | **48** |
| **Part A** — no content, needs a rewrite | **22** |
| **Part B** — real keyword gaps | **204** across 26 listings (275 rows) |
| **Part C** — wrong SKU, pair rejected | **3** |

## What validation cannot prove
**Keyword relevance.** The report finds terms that demonstrably work on a selling listing; it cannot
judge whether a term suits the product. That remains the requester's call and is question 3 on her sheet.

## Standing
Read-only throughout. No Amazon API call of any kind. **Validated — not yet published, not automated,
and awaiting Thuwaraga's business sign-off.**
