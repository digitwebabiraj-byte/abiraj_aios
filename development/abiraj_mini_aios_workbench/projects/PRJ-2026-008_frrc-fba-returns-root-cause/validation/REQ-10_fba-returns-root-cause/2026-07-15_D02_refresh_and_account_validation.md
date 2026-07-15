# Validation — REQ-10_fba-returns-root-cause (D02: data refresh + account split)

**Date:** 2026-07-15 · **DB:** `order_management_copy` (read-only reads; guarded output-store write) · **By:** Abiraj (Claude Code executor)
**Decision:** **GREEN (technical)** — reviewer gates (Tamil Selvan / Sajeesan) + business sign-off (Satheesvaran, items A–G + the three D02 findings) **PENDING**. Republished per-PH V6 (rows 216–234).

## What was validated
The **refreshed** FRRC pull for the **same D01 window (2026-06-14 → 2026-07-13)**, re-run live on 2026-07-15
under the **unchanged D01 rules**, enriched with the **Amazon account** (LEDSone / DCVoltage), rendered
into the 19 per-PH dashboards and republished. **No business rule was changed** — only the data was
refreshed and a display dimension added.

## Why the refresh (the drift finding)
The identical fixed window returned different numbers a day apart — **105 units / 91 ASINs** at the D01
build (2026-07-14) vs **118 units / 101 ASINs** on 2026-07-15. Confirmed as **late-arriving inserts**,
not a recount:
- The 13 extra rows carry the window's **highest ids** (LEDSone 92907–92914; DCVoltage 93635–93639) — the window's id range is 30447–93639.
- All 13 have `request_date` in the window **tail (2026-07-09 → 07-13)**.
- `id` rises **monotonically with `request_date`** for recent rows (06-14 ≈ 30k → 07-13 ≈ 92.9k) ⇒ **append-only ingestion**, so the newest ids genuinely arrived last.
- They landed in **two per-account batches**, consistent with a per-account ETL sync of Amazon's FBA Customer Returns report.
- 11 of the 13 rows were on **10 ASINs new to the window** (→ 91→101); the other 2 landed on ASINs already reported (→ their counts/rates rose). 105 + 13 = **118**. ✔ arithmetic ties.
- **Caveat recorded:** the exact settle lag could **not** be measured — `amazon_returns` has **no ingestion timestamp** (all 35 columns checked) and the `id` timeline is contaminated by an **initial bulk load** (May request_dates hold ids 1–16664; January 5465–55312), so any id-based lag estimate over history is invalid. An id-proxy attempt returned an implausible 71-day median and was **discarded, not reported**.

## Live checks (read-only)
| # | Check | Expected | Result | Verdict |
|---|---|---|---|---|
| 1 | Refreshed control totals (same window) | — | **101 ASINs / 118 return units** | ✅ PASS |
| 2 | Per-row bucket arithmetic (5 buckets = total_returns) | 0 failures | 0 failures | ✅ PASS |
| 3 | ASINs spanning **both** accounts (grain guard) | 0 | 0 | ✅ PASS |
| 4 | Unmapped account tag | 0 | 0 | ✅ PASS |
| 5 | PH roster vs D01 | no new PHs | **19 named, identical roster** (⇒ 19-row UPDATE, no INSERTs) | ✅ PASS |
| 6 | Owner coverage | — | **83 owned + 18 unassigned = 101** | ✅ PASS |
| 7 | DB identity (two independent connections) | same | MCP `postgres@10.8.0.3:5435` **and** psycopg2 `temp_user@149.28.134.54:5435` → both `order_management_copy`, both **118/101/118**, max id **93639** | ✅ PASS |
| 8 | Publish integrity (MCP re-verify) | 19 rows V6 | 19 rows, `version_level=6`, all `ph_priors`, all `released`, `description` NULL; stored md5 == local (utharsika `b3ae5b89…`, Abinayaa `e0e86bc1…`) | ✅ PASS |

## Refreshed vs D01 snapshot
| | D01 (published 2026-07-14) | D02 refresh (2026-07-15) |
|---|---|---|
| ASINs / return units | 91 / 105 | **101 / 118** |
| Flag split | CRIT 44 · HIGH 20 · OK 9 · N/A 18 | **CRIT 50 · HIGH 24 · OK 9 · N/A 18** |
| Owned / unassigned | 73 / 18 | **83 / 18** |
| Account split | (not shown) | **DCVoltage 49 ASINs / 61 units · LEDSone 52 ASINs / 57 units** |
| ASINs with ≥2 returns | 12 | **15** |

## Account enrichment (display only — no number changes)
- Resolved read-only from `amazon_returns.sub_source_name` (`amazon Ledsone` → **LEDSone** (sub_source 8); `amazon Dcvoltage` → **DCVoltage** (sub_source 6)) via `mode()` per ASIN, with a `COUNT(DISTINCT sub_source_name)` guard — **0 ASINs span both accounts**, so the one-row-per-ASIN grain is unaffected.
- The report remains **account-agnostic**: no account filter is applied to returns or sales. The account is only **shown and filterable**. Whether to filter/split by account is a **new open item for Satheesvaran**.
- **D01's `frrc30.json` was NOT mutated** — its SHA-256 remains `2cbfe13d0a5e…` per `SOURCE_MANIFEST.md`. The refresh is a **new asset** (`frrc_refresh_2026-07-15.json`); the query is `sql/REQ-10_.../generate_report_with_account.sql`.

## UI verification (in-browser, measured)
At the portal width **1360px**: page horizontal scroll **0**, table fills full width (**1095 = main 1095**), sticky column header pinned at `top:0`. Account filter proven functional: **LEDSone 7 + DCVoltage 16 = 23 = All** for utharsika, each filtered set **pure** (100% of rendered account cells match the selection). Per-PH isolation re-checked on all 19 files: each contains **only** its own holder's rows; 83 rows total across the 19 = the 83 owned ASINs.

## Duplicate-risk
- **GREEN.** No new project/task ID; D02 is a deliverable of the existing `REQ-10_fba-returns-root-cause`. The D01 dataset and its manifest checksum are preserved intact (no parallel-truth overwrite); the refresh is added as a distinct, dated asset alongside it.

## Open items (Satheesvaran — do NOT decide)
A. order-status set · B. marketplace scope · **C. window length / cadence** · D. returns↔sales alignment ·
E. rare reason codes · **F. return-status filter** · G. unassigned-owner attribution — **plus D02's findings:**
(i) **run date / settle lag** (T+1 undercuts ~12%; recommend a ~7-day buffer, i.e. run on the 8th — measurement still required);
(ii) **window starvation** (30 d → only 15/99 ASINs reach the ≥2-returns gate ⇒ **85% undiagnosable**; 60 d → 45/180, 90 d → 76/234; the workbook's own example used ~62 d);
(iii) **account scope** (combined today) **and** the per-account `status` vocabulary split (LEDSone `Unit returned to inventory` vs DCVoltage `DEFECTIVE`/`SELLABLE`/`CUSTOMER_DAMAGED`) — which directly affects item **F**.

## Result
**GREEN (technical).** Refresh executed under unchanged D01 rules, all control totals and grain guards
pass, account enrichment verified non-mutating and functional, publish md5-verified live and
independently re-confirmed on a second connection, D01's system-of-record preserved. **Reviewer sign-off
and Satheesvaran's decisions remain the outstanding gates.** Reversible: `DELETE … WHERE project_code='frrc'`
(rows 216–234 only); the D01 snapshot can be re-rendered from the untouched `frrc30.json`.
