# SKILL FILE — DAILY KNOWLEDGE EXTRACTION
# DIGITWEB LK LTD · Daily Skill Increment System · v3.0

---

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-24 |
| **developer** | abiraj |
| **project** | PH ASIN Segmentation — Growth Protection Engine (GPE) |
| **project\_code** | ph-asin |
| **phase** | BUILD |
| **requirement\_id** | REQ-05 |
| **deliverable\_id** | REQ-05-D02 |
| **status** | **COMPLETE** — End-to-end build delivered and verified. The segmentation was **re-derived strictly per the protocol document** (not read from the table's pre-baked column) into the materialised table `analytics.ph_segment_report` (7,855 rows), then surfaced as a self-contained interactive HTML report. A parameter-free monthly engine (`ph_segment_engine.sql`) + the ChatGPT-brain handover files make the monthly run repeatable. All decision/scope items from the first pass are now **closed** (Section 7) — including the **FBM-only correction** (the benchmark was unintentionally counting ~23% FBA units; now filtered to `fba_sales=false`, which moved 100+ ASINs between segments). |
| **evidence\_location** | **Live MCP calls this session (read + write, write authorised — see S7 D-0):** `information_schema.columns` (new-table schema + `fba_sales` discovery), window/segment-distribution aggregates, benchmark validation (utharsika), FBM split verification, and the engine DDL (`CREATE TABLE … AS` for `_ph_cur`/`_ph_prev`/`ph_segment_report`, helpers then `DROP`ped). Outputs captured in Section 3. **Artifacts (handed to Abiraj → file under `evidence/monthly-reports/2026-07/`):** `PH_ASIN_Segmentation_Report_2026-07.html`, `ph_segment_engine.sql` (FBM-corrected), `MONTHLY_RUN_PROMPT.md`, `ChatGPT_Brain_Setup.md`. **No Git SHA** — built in the Claude execution environment; handed over as files. |
| **blos\_keys\_used** | NONE — project does not consume BLOS rule/threshold keys. (Protocol carries its own kill-criteria + escalation thresholds; captured in `hardcoded_thresholds`.) |
| **hardcoded\_thresholds** | **Benchmark population:** top **30** sold ASINs per PH-per-category; top **10** if <30 sellers; **flag "manual"** if <10 sellers. **Benchmark value (Method A, locked):** mean of *per-ASIN* CVR across the top-N (each ASIN's conv/click first, zero-click=0, then average) + mean impression + mean click. **Classification:** Impression HIGH if `imp ≥ bm_imp`; Click HIGH if `clk ≥ bm_clk`; **Conversion:** `clicks=0 → LOW`; `conversion>clicks → HIGH`; else `cvr ≥ bm_cvr → HIGH` else LOW. **Undefined-combo map (Option B, locked):** `HLL → HLH`, `LHL → HHL`; other 6 identity. **Movement h-count:** HHH=3, HHL/HLH/LHH=2, LLH=1, LLL=0 → cur>prev IMPROVED, <prev DECLINED, = SAME, no prev NEW. **Scope filters (locked):** `ph_segment_30days_window` `which_channel=1, market_place='UK'`, latest `period_end`=current, 2nd-latest=previous; `order_transaction` `source_name='AMAZON', market_place='UK', order_status='Completed', fba_sales=false (FBM only)`, dates = window `period_start..period_end`. **Account map:** `sub_source_name` `amazon Ledsone→LEDSone UK`, `amazon Dcvoltage→DCVoltage UK`. **SKU:** most-sold per ASIN, FBM only (`ROW_NUMBER() ORDER BY SUM(quantity) DESC`). **report_period label:** `TO_CHAR(cur period_end + 1 day,'YYYY-MM')`. **Escalation (§8, FLAG only):** PH >30% LLL; PH >5 declines (both in report banner); + carried kill-criteria (margin<15%/30d; CVR not +20%/60d; CTR<1% after 2 fixes; impressions not +50%/60d; units<20/mo after overhaul; ACoS>40%/30d). |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| SEGMENTATION \| REPORTING \| AMAZON-LISTINGS \| FRONTEND-HTML \| LLM-ORCHESTRATION |

## File path:
# 2026-06-24__abiraj__ph-asin__REQ-05-D02.md
# DigitWeb_Works_Abiraj/24_06_2026/

---

## SECTION 1 · SYSTEM STATE

- **At start of today:** D01 ended BLOCKED on a read-only/four-table scope check; the working assumption was "read-and-show from the bi-weekly `analytics.ph_segment`."
- **What changed the brief today (input from Abiraj, with authorisation — see S7 D-0):** (1) a **new dedicated source table** was provisioned for this requirement — `analytics.ph_segment_30days_window` (monthly/30-day window); (2) writes to `analytics.*` to materialise the result are **authorised** for this project; (3) instruction to **follow the protocol document exactly using existing data** — i.e. *re-derive* segments, do not trust any pre-computed column; (4) deliver as standalone HTML now, website tab later; (5) ChatGPT = brain (emits the prompt), Claude Code = executor.
- **What was working:** the new source table holds 15 monthly windows (Apr 2025 → Jun 2026), latest `period_end = 2026-06-30`, with impression/click/conversion/total_sales, `user_name` (PH), `category_name`, `sub_source_name` (account).
- **Settled today:** do not trust the pre-baked `performance_segment` (different method); handle the 2 undefined combos (Option B); CVR averaging (Method A); zero-click & conv>click edges; SKU rollup; **and the FBM scope** (the field `order_transaction.fba_sales` exists and ~23% of in-scope units were FBA — now filtered out).
- **Starting point:** inspect the new table, prove the document's method is buildable, lock decisions, materialise the result, generate the report, wire the monthly loop.

> **In plain terms:** Yesterday we found a segmentation already existed and planned to just display it. Today the brief changed — a new monthly table was created and writes were authorised — so we rebuilt the segments *exactly the way the document defines them* and put them in a report. Mid-build we caught that the "best sellers" used to set each benchmark were mixing FBA in with FBM; the scope is FBM, so we filtered to FBM and rebuilt. That correction moved 100+ products between segments.

---

## SECTION 2 · WHAT CHANGED TODAY

A **build day**, finished and verified.

- **Change 1 — Inspected the new source `analytics.ph_segment_30days_window`** (schema, 15 monthly windows, latest Jun 2026). UK-Amazon scope (`which_channel=1, market_place='UK'`) = **7,855 ASINs / 24 PHs / 57 categories**, accounts `amazon Ledsone` + `amazon Dcvoltage`.
- **Change 2 — Proved the document benchmark builds on existing data** (validated on `utharsika`).
- **Change 3 — Built the engine `analytics.ph_segment_report`** (7,855 rows) via `_ph_cur` + `_ph_prev` → joined report (+SKU +movement +`report_period`); helpers dropped.
- **Change 4 — Locked the methodology decisions** (S7): re-derive; Method A CVR; zero-click→LOW & conv>click→HIGH; Option B (HLL→HLH, LHL→HHL).
- **Change 5 — Caught and fixed the FBM scope error.** `order_transaction.fba_sales` exists; the June in-scope set was **FBM 4,499 units / FBA 1,338 units (~23%)**. Benchmark unit ranking + SKU rollup now filtered to `fba_sales=false`. Rebuilt the table and engine. **Effect:** HHH 54→**77**, HHL 437→**479**, HLH 128→**157**, LHH 24→**17**, LLH 364→**349**, LLL 6,848→**6,776**.
- **Change 6 — Generated the self-contained HTML report** to the §5 spec (six colour-coded tabs + per-PH count badges, PH sidebar filter, per-PH configurator, ASIN cards with movement arrows, tick boxes, progress bars, §8 banner, Export/Import). Rendered + screenshot-verified.
- **Change 7 — Made the engine parameter-free (`ph_segment_engine.sql`):** auto-detects the latest two windows (no dates to edit); verified it reproduces 7,855 rows; now carries the FBM filter.
- **Change 8 — ChatGPT-brain handover** (`MONTHLY_RUN_PROMPT.md` + `ChatGPT_Brain_Setup.md`): one fixed monthly prompt, same every cycle.
- **Change 9 — Per-PH badge fix:** report tab counts recompute to the selected PH and revert to totals on "All PHs".

### Deliverables
- **A — `analytics.ph_segment_report`** (7,855 rows, FBM-correct).
- **B — `PH_ASIN_Segmentation_Report_2026-07.html`** (working report).
- **C — `ph_segment_engine.sql`** (auto-window, FBM-correct engine).
- **D — `MONTHLY_RUN_PROMPT.md` + `ChatGPT_Brain_Setup.md`** (repeatable orchestration).

Evidence: live MCP query/DDL outputs (S3) + the four files. No credentials. No Git SHA (handed over as files).

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> **PostgreSQL via MCP — READ and WRITE used this session, under the authorisation in S7 D-0.**

**Tables:** `analytics.ph_segment_30days_window` (source, read), `public.order_transaction` (units + SKU + `fba_sales`, read), `analytics.ph_segment_report` (created), `_ph_cur`/`_ph_prev`/`_ph_windows` (temp, created+dropped).

### Finding A — new source table pre-segments by a *different* method
`ph_segment_30days_window` carries a pre-baked `performance_segment` (6-code) from a raw `overall_segment` (8-code) using category-median + raw conversion counts, folding `HLL→HLH`, `LHL→LLH`. This does **not** match the document (top-30-sold average + CVR), so it was **re-derived**, not reused.

### Finding B — FBM vs FBA in the benchmark (the key correction today)
`order_transaction.fba_sales` is a boolean. June, UK-Amazon, Completed: **FBM 3,557 orders / 4,499 units; FBA 1,229 orders / 1,338 units (~23%).** Protocol scope is FBM, so the benchmark must rank on FBM units only → added `fba_sales=false` to both window unit CTEs and the SKU rollup.

### Finding C — final distribution (FBM-only, Option B), June window
| Segment | ASINs | Improved | Same | Declined | New | Manual-bm |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| HHH Champions | 77 | 73 | 4 | 0 | 0 | 55 |
| HHL Leaky Buckets | 479 | 218 | 250 | 6 | 5 | 145 |
| HLH Wallflowers | 157 | 75 | 79 | 2 | 1 | 36 |
| LHH Hidden Gems | 17 | 15 | 0 | 1 | 1 | 11 |
| LLH Niche Winners | 349 | 229 | 98 | 18 | 4 | 7 |
| LLL Dead Horses | 6,776 | 0 | 6,090 | 572 | 114 | 864 |
| **Total** | **7,855** | | | | | **1,118** |
~86% land in LLL (expected — bar = top sellers' average). **1,118** ASINs sit in <10-seller categories (manual-benchmark flag). Escalation (§8): **24** PHs >30% LLL; **20** PHs >5 declines.

### Finding D — SKU rollup (FBM)
Most-sold FBM SKU per ASIN. **6,937 of 7,855 have a SKU; 918 do not** (no completed FBM order carrying a SKU → `—`). Bundles kept verbatim with `+`.

### Finding E — date storage (by design)
`ph_segment_report` stores `report_period` text (e.g. `2026-07`). Data-window dates (`2026-06-01 → 2026-06-30` current; `2026-05-01 → 2026-05-30` previous) live in the source table's `period_start`/`period_end`. History is **single-cycle by design** (engine overwrites) — accepted, see S7 D-6.

### Finding F — conversion field semantics
368 ASINs convert with 0 clicks; 436 have conv>clicks; pooled CVR 14.6% vs Method-A per-ASIN average ~45–60%. Handled by the locked edge rules.

### Benchmark example (FBM, utharsika)
Lampshade Imp≥3,911 · Clk≥22.7 · CVR≥60.67% (228 sellers, top-30); Wall plug Imp≥727 · Clk≥10.6 · CVR≥54.37% (55 sellers, top-30).

---

## SECTION 4 · GAP FOUND

> All prior-pass gaps are now resolved (S7). Remaining items are forward-looking only.

- **Gap A — Website integration not yet built (LOW, PLANNED — P3).** Standalone HTML ships now; the Vue/Laravel tab (reads `ph_segment_report`, same SQL) is the next phase. Not blocking. Owner: abiraj (schedule).
- **Gap B — Tick state is per-browser until the website tab exists (LOW, KNOWN).** Standalone report persists ticks in `localStorage` + Export/Import. Shared server-side state arrives with the Vue/Laravel tab. Owner: abiraj.
- **Gap C — Source June window completeness (LOW, MONITOR).** `period_end=2026-06-30` is a future-dated label relative to the run date; the engine always uses the latest *closed* window on the 1st-of-month cadence, so this self-resolves at production time. Monitor on first live run. Owner: abiraj.

> `GAP: no blocking gaps. Three forward-looking items above.`

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

> Rules **implemented in `ph_segment_engine.sql`** (enforced in SQL, FBM-corrected).

- **RULE — FBM-only inputs.** `order_transaction.fba_sales=false` on both window unit CTEs and the SKU rollup (matches protocol scope; prevents FBA inflating the benchmark).
- **RULE — benchmark top 30 / else top 10 / else flag.** ≥30 sellers→top30; 10–29→top10; <10→`needs_manual` (never invent).
- **RULE — Method A CVR.** Per-ASIN CVR (zero-click→0) averaged across top-N.
- **RULE — conversion edge cases.** clicks=0→LOW; conv>clicks→HIGH; else CVR vs benchmark.
- **RULE — every ASIN exactly one of six segments.** Option B (HLL→HLH, LHL→HHL); verified 77+479+157+17+349+6,776 = 7,855, zero unclassified.
- **RULE — account from `sub_source_name`; SKU = most-sold FBM per ASIN.**
- **RULE — flag-don't-act on §8** (banner only; no commercial action taken).
- **RULE — auto-detect windows** (current = latest `period_end`, previous = 2nd-latest); reproduces 7,855 rows.

> `VALIDATION RULE: FBM filter added; all others as above.`

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Failure mode (FIXED) — FBA units inflating the FBM benchmark.** Trigger: unit ranking counted all fulfilment types. Detection: `fba_sales` split showed ~23% FBA. Recovery: `fba_sales=false` filter; table+engine rebuilt; 100+ ASINs re-segmented. Risk: was MEDIUM → **resolved**.
- **Edge case (HANDLED) — zero-click / conv>click** → zero-click LOW, conv>click HIGH (avoids div-by-zero / >100%). Risk LOW.
- **Edge case (HANDLED) — many SKUs per ASIN** → most-sold FBM pick; caveat: displayed SKU can change month-to-month if a different variant outsells. Risk LOW.
- **Method note (ACCEPTED) — Method A CVR runs high** (~45–60%) because low-click top sellers are noisy; accepted by decision (S7 D-2); the bar is high by design.
- **Edge case (AWARENESS) — engine overwrites** (single-cycle, no history) — accepted (S7 D-6). Risk LOW.
- **Edge case (AWARENESS) — `localStorage` ticks** persist only in the reviewer's own browser after download; Export/Import is the portable fallback. Risk LOW.

> `FAILURE MODE: one fixed (FBM); remainder handled or accepted.`

---

## SECTION 7 · DECISIONS MADE TODAY

- **D-0 — Scope change ratified (governance, CLOSED).** Writes to `analytics.*` and use of the new `analytics.ph_segment_30days_window` (in) / `analytics.ph_segment_report` (out) are the **authorised** approach for this requirement — a dedicated table was provisioned by the business for exactly this purpose. Recorded as the sanctioned scope for REQ-05 (supersedes D01's read-only/four-table assumption). Approved: abiraj (business).
- **D-1 — Re-derive per the document; do NOT trust the pre-baked column.** The pre-baked segment uses category-median + raw counts + a different fold; the brief is "follow the document exactly." Trade-off: more compute, spec-faithful. Approved: abiraj.
- **D-2 — Method A CVR benchmark** (per-ASIN CVR then average). Reason: matches the document's "average CVR of the top ASINs." Trade-off: a high, sometimes noisy bar. Approved: abiraj.
- **D-3 — Conversion edges: zero-click→LOW, conv>clicks→HIGH.** Approved: abiraj.
- **D-4 — Undefined combos Option B (HLL→HLH, LHL→HHL).** Routes each leftover to the segment whose action plan fixes its real problem. Note: LHL diverges from the live DB's `LHL→LLH`; Option B is the canonical for this report. Approved: abiraj (action-correct).
- **D-5 — FBM-only inputs.** The protocol scope is FBM; the data mixed ~23% FBA into the benchmark. Filtered to `fba_sales=false`; table + engine + prompt updated. Approved: abiraj.
- **D-6 — Single-cycle table (no history columns) accepted.** Data-window dates live in the source table; the dashboard phase can add history later if needed. Not required now. Approved: abiraj.
- **D-7 — PH universe = 24 (not 28) accepted.** Only 24 PHs own UK-Amazon FBM ASINs this window; the others have no in-scope stock. Not a data error. Approved: abiraj.
- **D-8 — LLL view = declined/new cards + full list in the table, accepted.** 6,776 cards is unusable UX; every LLL ASIN is still classified and stored. Approved: abiraj.
- **D-9 — Standalone HTML now, website tab later; ChatGPT brain / Claude Code hands; one fixed monthly prompt.** Approved: abiraj.

> Constants live in both `MONTHLY_RUN_PROMPT.md` and `ph_segment_engine.sql`; **the SQL is authoritative** — if a constant changes, change the SQL first, then mirror the prompt.

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule
Every UK-Amazon **FBM** ASIN owned by a PH is classified **monthly** into one of six segments from three live signals — **Impressions, Clicks, CVR** — each rated HIGH/LOW against a **per-PH, per-category** benchmark = the **average of that category's top-30 best-selling FBM ASINs** (top-10 if <30; flagged if <10), recomputed each cycle. So a product is judged only against the top sellers in its own category. Each segment has a fixed action plan; movement vs the prior month is tracked; the system **flags** and never takes commercial action. Source `analytics.ph_segment_30days_window` → output `analytics.ph_segment_report`.

### Operational Assumption
`ref_id`=ASIN; `conversion_count`=order count (not revenue) and **not** strictly "clicks that converted" (zero-click & conv>click rows exist); account=`sub_source_name`; **benchmark units are FBM only** (`fba_sales=false`); PH ownership + category from the segmentation table. 30-day windows are calendar-month-ish (29-day spans). The execution connection is **write-authorised** for `analytics.*` (D-0).

### Reusable Logic / Formula
- **Benchmark (per PH-category):** rank FBM-sold ASINs by `SUM(quantity)` desc; top 30 (10 if <30; flag if <10); `bm_imp/bm_clk=mean`; **`bm_cvr=mean of per-ASIN conv/click` (zero-click=0, Method A).**
- **Classify:** `imp≥bm_imp→H`; `clk≥bm_clk→H`; conversion `clicks=0→L`, `conv>clicks→H`, else `cvr≥bm_cvr→H`. Concatenate `[I][C][V]`.
- **8→6 map (Option B canonical):** identity for the 6; **HLL→HLH, LHL→HHL.**
- **Movement:** h-count (HHH=3, HHL/HLH/LHH=2, LLH=1, LLL=0); cur>prev IMPROVED, <prev DECLINED, = SAME, none NEW.
- **Window auto-detect (reusable):** current=`MAX(period_end)`, previous=next-lower — parameter-free monthly job.
- **Fulfilment filter (reusable):** `order_transaction.fba_sales=false` = FBM; `=true` = FBA. Always confirm fulfilment scope before any sales-ranked metric.

### Canonical Vocabulary
| Term | Meaning |
| :---- | :---- |
| PH | Portfolio Holder (`user_name`) |
| GPE | Growth Protection Engine |
| Method A | per-ASIN CVR averaged across top-N (vs pooled CVR) |
| Option B | undefined-combo map HLL→HLH, LHL→HHL |
| `fba_sales` | bool in `order_transaction`: false=FBM, true=FBA |
| `sub_source_name` | account → LEDSone UK / DCVoltage UK |
| `report_period` | text cycle label e.g. `2026-07` (≠ data dates) |
| brain / hands | ChatGPT (orchestrator) / Claude Code (executor) |

### Cross-Project Applicability
- **Confirm fulfilment scope before sales-ranked metrics** — FBA/FBM mixing silently skews any "top sellers" calculation; cost ~23% of units here. Reusable across PPC, CFIS, any Amazon analytics.
- **Pre-compute-then-serve:** materialise heavy per-row analytics into one table; UIs read it, never recompute.
- **Parameter-free engine via window auto-detect** for scheduled jobs.
- **Decision-before-build register (D-0…D-9):** lock spec-vs-data choices with the owner and record them, rather than picking silently.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES — benchmark, Method A, edges, Option B, FBM filter, scope, escalation in metadata + S5/S8 |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES — no blockers; 3 forward-looking items |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES — live query/DDL outputs (S3) + four artifact files; no Git SHA (files), stated plainly |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (1–9)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment
A developer with no context could, from this file alone:
- **WHAT** was done — re-derived the 6-segment classification per the protocol (Method A CVR, Option B, edge rules, **FBM-only**) into `analytics.ph_segment_report` (7,855 rows); built a working interactive HTML report; made a parameter-free, FBM-correct monthly engine; produced the ChatGPT-brain handover; caught and fixed an FBA-in-benchmark error that moved 100+ ASINs.
- **WHAT** the rules are — top-30/10 FBM-sold average per PH-category (Method A); ≥benchmark→HIGH; zero-click→LOW, conv>click→HIGH; Option B map; movement by h-count; account from `sub_source_name`; SKU most-sold FBM; flag-don't-act.
- **WHAT** is closed — scope ratified (D-0), methodology locked (D-1…D-5), history/PH-count/LLL-view accepted (D-6…D-8); no blockers remain.
- **WHO** owns the future items — abiraj (website tab + shared tick state; monitor first live run).
- **WHY** — follow the document over the pre-baked column; Method A matches the doc; Option B is action-correct; FBM matches scope; precompute-then-serve.
- **WHERE** — source `ph_segment_30days_window`; output `ph_segment_report`; units/SKU/`fba_sales` in `public.order_transaction`; artifacts under `evidence/monthly-reports/2026-07/`.
- **WHAT** next — run the fixed monthly prompt on 1 July; build the Vue/Laravel tab off `ph_segment_report` when scheduled.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-06-24__abiraj__ph-asin__REQ-05-D02.md`
- [x] Saved under dated folder `DigitWeb_Works_Abiraj/24_06_2026/`
- [x] Metadata complete — incl. `blos_keys_used` (NONE) and `hardcoded_thresholds` (full FBM-correct constants)
- [x] Live query + DDL evidence in Section 3 (schema, FBM split, distributions, benchmark, table builds)
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written (WHAT/WHO/WHY/WHERE)
- [x] Evidence referenced (live MCP outputs + four artifact files); no Git SHA (files), stated plainly
- [x] ✅ **BUILT:** `analytics.ph_segment_report` (7,855 rows, FBM-correct) + working HTML report + parameter-free engine + ChatGPT-brain files
- [x] ✅ **DECISIONS CLOSED (D-0…D-9):** scope ratified · re-derive · Method A · edges · Option B · **FBM-only** · history/PH-count/LLL-view accepted
- [x] ✅ **CORRECTION:** FBA (~23% of units) removed from the benchmark → 100+ ASINs re-segmented; engine + prompt + report updated
- [x] ✅ **VERIFIED:** auto-window engine reproduces 7,855 rows; counts reconcile (77/479/157/17/349/6,776); report rendered across tabs/PH filter
- [x] ✅ **STATUS:** COMPLETE — no blockers; 3 forward-looking (website tab, shared ticks, first-run window check)

---
*DIGITWEB LK LTD — Daily Skill Increment System — v3.0 — June 2026*
