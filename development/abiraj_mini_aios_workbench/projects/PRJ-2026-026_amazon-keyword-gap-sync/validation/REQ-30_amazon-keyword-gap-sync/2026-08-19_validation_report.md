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

---

# ADDENDUM — D01 given the same treatment as D02, and three D01 defects found (2026-08-19)

Owner: *"not D02 same all same D01"* — D01 had only an Excel file while D02 had Excel **and** a
dashboard. Building D01 its matching dashboard surfaced three real defects in the Phase 1 data.

## 🔴 Defect 1 — `click_rate` used the wrong denominator
The source's Step 8 requires a `click_rate` column. The builder computed
`total_click_count / total_query_impression_count`. **Amazon's own definition is
`total_click_count / search_query_volume`**, proved against its stored column on live rows:

| search term | impressions | clicks | Amazon `total_click_rate` | clicks/impressions | clicks/**volume** |
|---|---|---|---|---|---|
| ceiling fans with lights | 4,298,113 | 58,873 | **31.55%** | 1.37% ✗ | **31.5524%** ✅ |
| ceiling fan | 4,251,180 | 54,055 | **30.09%** | 1.27% ✗ | **30.0919%** ✅ |
| kitchen | 2,011,567 | 3,125 | **3.33%** | 0.16% ✗ | **3.3305%** ✅ |
| garden lights | 1,771,067 | 13,633 | **18.81%** | 0.77% ✗ | **18.8067%** ✅ |

Every delivered click rate was therefore **~23× too low**. Fixed.
`asin_impression_share` was already correct (ASIN impressions / total query impressions — confirmed
against Amazon's column on the same rows).

## 🔴 Defect 2 — the three months were combined, which the source forbids
Step 4 is explicit: *"Check the last 3 consecutive months **one month at a time, not as a combined
range**"*, and Step 8's filename `SQP_[ASIN]_[YYYY-MM].csv` confirms a per-month export. The builder
summed the whole window into one row per ASIN × term.

Fixed: Phase 1 is now **one row per ASIN × month × term** (443 rows), the top-N cut applies **within
each month**, and the Excel writes **one sheet per account per month** (`SQP LED 2026-05`,
`SQP DCV 2026-06`, …). Each weekly row is assigned to the month containing its `start_date` — Amazon
weeks are Sun–Sat and can straddle a boundary, so the choice is stated rather than left implicit.

Phase 2 still audits *"the confirmed top search terms"* — now the **de-duplicated union** across the
three months (411 distinct terms), keeping each term's highest monthly volume.

## 🔴 Defect 3 — the volume column was mislabelled
`search_query_volume` is the **market-wide** volume for that term in that week, identical for every ASIN
in the same week (6,610 for all ASINs in w/c 2026-07-19). Summing it per ASIN across the window made an
ASIN present in 2 weeks look twice as in-demand as one present in 1 week — that is **week coverage, not
customer demand**. With months now separate the figure is a genuine monthly volume and the label
"Searches / mo" is accurate.

## Re-verification
**372 single-week rows compared directly against Amazon's own stored `total_click_rate` and
`asin_impression_share` columns — 0 mismatches beyond rounding.** (Single-week months are the only ones
directly comparable; multi-week months are aggregates by construction.)

## D01 dashboard
Same design, filters and interaction model as D02: full-screen, sticky toolbar, sortable tables,
clickable KPI tiles. Filters: search · account · **month** · Top-Moving ASIN · min searches ·
**Opportunity only** · **Long-tail only**. 443 terms · 141 opportunity · 73 long-tail.

*Opportunity* implements the source's "High Volume + Low ASIN Share" pattern. The document names the
pattern but gives no cut-off (open item #10), so it is a **median split of this run**, labelled as such
on screen — no business threshold has been invented.

## Standing after this addendum
| | |
|---|---|
| D01 | Excel (7 month/account sheets) **+ dashboard** — rate columns now match Amazon exactly |
| D02 | Excel (Parts A/B/C + field reference) **+ dashboard** with the §2.7 review buttons |
| Independent checks | 10/10 · in-run QA 7/7 · 372 rate rows reconciled |

---

# ADDENDUM 2 — consolidated to ONE dashboard file (2026-08-19)

Owner: *"keep only correct html not keep many html"*. The folder had grown two HTML dashboards, one per
phase. A person receiving this should open **one** thing.

## Now
| File | |
|---|---|
| **`REQ-30_bgct_keyword_dashboard.html`** | **the only dashboard** — both phases as two tabs |
| `REQ-30-D01_sqp_top_terms.xlsx` | Phase 1 workbook (7 month/account sheets) |
| `REQ-30-D02_keyword_gap_report.xlsx` | Phase 2 workbook (Parts A/B/C + field reference) |

`REQ-30-D01_sqp_top_terms_dashboard.html` and `REQ-30-D02_keyword_gap_dashboard.html` are **deleted**,
and `render_bgct_d01_dashboard.py` with them — one renderer now emits one file. The renderer deletes the
two superseded names on every run, so they cannot reappear.

The two **Excel workbooks stay separate** because they are the two named deliverables (D01 and D02).
Only the review surface is consolidated.

## Verified interactively
| Action | Result |
|---|---|
| Opens on Phase 1 | 443 keyword rows · 24 ASINs · 30 Top-Movers listed |
| Phase 1 + month 2026-06 | 210 rows · 21 ASINs |
| Phase 1 + Opportunity only | 44 rows · 14 ASINs |
| Switch to Phase 2 | Part A 22 · Part B 204 · Part C 3 |
| Phase 2 + LEDSone | 177 rows |
| Phase 2 "By listing" view | 15 pair panels, 15 §2.7 buttons |
| Phase 2 KPI "Need a rewrite" | 22 rows, Part B hidden |
| Back to Phase 1 | state intact |

Each tab keeps its own filter bar, KPI tiles and Reset, so the two phases never interfere. Still one
self-contained file — no network, no external assets, 153 KB.

---

# ADDENDUM 3 — instructions built into the dashboard (2026-08-19)

Owner: *"the UI must look easy to the user … I need to explain how to use it"*. Rather than ship a
separate guide that gets separated from the file, the instructions are now **inside the dashboard** —
still one file, nothing to lose.

## What was added
A **"How to use this tab"** panel at the top of each tab, open by default, with a
**Hide / Show instructions** button in the header. Written in plain language for a reader whose first
language is not English: short sentences, no jargon, and the **coloured labels shown inline** so the
reader can match the instruction to what they see in the table.

**Phase 1** — what the words are, what *Opportunity* and *Long-tail* mean in business terms
("many people search this but your bulb hardly shows up"), how to use Month / ASIN, and when to use this
tab at all.

**Phase 2** — framed as a monthly to-do list: the three Parts are **three different jobs** (write /
add words / fix the SKU), what each *What to do* label means, **work in batches** using the filter,
start with the biggest numbers, and mark done in the "By listing" view. It closes with the two things
that matter most: nothing touches Amazon, and **a word that does not suit the bulb must not be added** —
that judgement is hers, not the report's.

## 🔴 A real bug this exposed
Remembering the Hide/Show preference used `localStorage`, which **throws** in sandboxed viewers and
`data:` URLs. Because `help()` runs during start-up, that exception would have aborted the script
**before the tables drew** — the whole dashboard would have opened blank, with working filters and no
data, in any viewer that blocks storage. Now wrapped in try/catch: the preference is a nicety, and
failing to save it can never stop the page.

## Verified in a storage-blocked context
| Check | Result |
|---|---|
| Page still draws with storage blocked | ✅ 443 Phase 1 rows |
| Instructions shown by default | ✅ |
| Hide / Show toggle + button label | ✅ both directions |
| Phase 2 after toggling | ✅ A 22 · B 204 · C 3 |
| Filter still works | ✅ "Add to backend" → 51 rows |
| Reset | ✅ 229 rows |

One self-contained file, 157 KB.
