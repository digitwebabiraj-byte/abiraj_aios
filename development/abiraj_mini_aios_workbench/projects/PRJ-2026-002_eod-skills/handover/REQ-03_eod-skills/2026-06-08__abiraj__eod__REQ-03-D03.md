
## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-08 |
| **developer** | abiraj |
| **project** | EOD Performance Tracker |
| **project\_code** | eod |
| **phase** | OPERATIONS |
| **requirement\_id** | REQ-03 |
| **deliverable\_id** | D03 |
| **status** | COMPLETE |
| **evidence\_location** | `daily_eod_log` — PostgreSQL · ROI database · vintageinterior.co.uk |
| **blos\_keys\_used** | NONE — query/testing session only, no storage keys written |
| **hardcoded\_thresholds** | NONE — all figures pulled live via Step 0 / MCP `execute_sql` at runtime |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | EOD \| QUERY-TESTING \| DATA-INTEGRITY \| SKILL-FILE \| HR-REPORT |

## File path (fill after saving):
# 2026-06-08__abiraj__eod__REQ-03-D03.md

---

## SECTION 1 · SYSTEM STATE

- **Current system state:** EOD performance system operational. New data loaded since the D02 report — table grew from 1,006 to 1,782 rows; data range now 2026-02-03 to 2026-05-29 (May logs present). The `eod-query-answerer` skill (`sql_generate_skill.md`) was tested live against the larger dataset today. MCP connected to PostgreSQL ROI database at vintageinterior.co.uk. 50 predefined questions active, all now carry a `sql_query`.
- **What was working at start of today:** Corrected skill file (D01/D02) with live Step 0 query. Dashboard artifact and FastAPI zip built. Question registry populated.
- **What was built / explored today:** Re-ran Step 0 live facts; tested tier/department/staff/waste/time-window query patterns end-to-end; discovered a ph_id collision and a duplicate department code; confirmed verification improved sharply; compiled findings for HR (this file, D03).
- **Your starting point:** D02 complete, skill file accurate. Today was a verification/testing pass against the newly-uploaded May data, surfacing data-integrity issues.
- **Environment:** Production — claude.ai · EOD MCP · PostgreSQL ROI database · vintageinterior.co.uk

> **In plain terms:** Today's job was to test the query system against the freshly-loaded May data, check the answers come back correctly, and find anything broken. Verification rates jumped and SEO improved, but the new data introduced a duplicate staff ID and a duplicate department name. Every number below was pulled live from the database — none are guessed.

---

## SECTION 2 · WHAT CHANGED TODAY

- **Change 1 — Dataset grew; May data loaded:** Step 0 shows 1,006 → 1,782 rows. Max date 2026-04-24 → 2026-05-29. Total hours 1,576.44h → 3,083.77h. Distinct staff 13 → 16. The 41-day gap from D02 is now a 10-day gap.

  > **In plain terms:** Someone uploaded the missing May data. Coverage is now February–end of May instead of stopping in April.

- **Change 2 — Verification rate jumped:** Overall 53.2% → 73.6%. SEO (the D02 crisis at 4.3%) is now 48.5%. Hetheesha 0% → 44.2%, Kamsi 0% → 80.0%. Sukirtha still 0%, Dilaksi 17.1%.

  > **In plain terms:** Most staff started attaching proof links. SEO went from almost nothing to about half. Two people still submit no proof.

- **Change 3 — NEW: ph_id collision (DMK004):** Testing surfaced that ph_id `DMK004` is shared by two people — Thasitha and Thisoban.

  > **In plain terms:** Two staff were given the same ID, so the system can't reliably separate their work.

- **Change 4 — NEW: "ADS" department duplicates "Google Ads":** A new `ADS` code (205 tasks, 398.5h) holds mostly existing Google Ads staff plus three new starters.

  > **In plain terms:** The same ad team is logged under two department names; reports treat them as two teams unless merged.

- **Change 5 — More staff unmatched in ph_master:** Unmatched ph_ids rose 2 → 5, adding new starters Theekshy (DMK005), Thanishtika (DMK006), Jakshan (DMKS05).

  > **In plain terms:** Three new employees were logged before being added to the staff master list.

- **Change 6 — Skill patterns re-tested on larger data — all passed:** Step 0, tier split, TRIM department grouping, staff ranking, waste log and time-window fallback all behaved correctly.

  > **In plain terms:** The query reference guide still works on the bigger dataset without edits.

---

## SECTION 3 · POSTGRESQL / MCP FINDING

All results below returned live from `End_of_the_day_performance_check_Postgress` MCP `execute_sql`. Nothing hardcoded.

### Live data snapshot (moved out of metadata)

| Field | Value |
| :---- | :---- |
| data range | 2026-02-03 to 2026-05-29 |
| total tasks logged | 1,782 |
| total hours logged | 3,083.77h |
| verification rate | 73.6% (1,311 of 1,782) |
| high-value % (Tier S+A hours) | 84.9% (2,617.7h) |
| waste hours | 13.5h across 9 tasks (0.4%) |

### Tier distribution

| Tier | Tasks | Hours | % of total hours |
| :---- | :---- | :---- | :---- |
| S (Strategic) | 37 | 124.5h | 4.0% |
| A (Revenue-Direct) | 1,366 | 2,493.2h | 80.8% |
| B (Revenue-Support) | 218 | 285.1h | 9.2% |
| C (Operational) | 158 | 179.2h | 5.8% |
| D (Admin) | 3 | 1.8h | 0.1% |

### Department summary (TRIM applied)

| Department | Staff | Tasks | Hours | High-val % | Verified % |
| :---- | :---- | :---- | :---- | :---- | :---- |
| SEO | 5 | 600 | 979.5h | 89.6% | 48.5% ⚠ |
| Google Ads | 6 | 581 | 909.8h | 85.9% | 78.0% |
| TECH | 2 | 321 | 660.0h | 81.3% | 100.0% ✓ |
| ADS ⚠ | 9 | 205 | 398.5h | 88.0% | 100.0% ✓ |
| Technical / GTM | 1 | 47 | 85.0h | 51.2% | 55.3% |
| Technical / UI-UX | 1 | 28 | 51.0h | 54.9% | 53.6% |

### Staff performance

| Staff | Primary Dept | Tasks | Hours | Ver % | Δ/hr | Waste |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Kuberan | TECH | 248 | 508.0h | 86.3% | 3.01 | 6 |
| Sajeepan | Google Ads | 173 | 293.5h | 79.8% | 4.82 | 0 |
| Hetheesha | SEO | 165 | 292.5h | 44.2% | 16.62 | 0 |
| Piranav | TECH | 148 | 288.0h | 100.0% ✓ | 1.93 | 0 |
| Kamsi | SEO | 165 | 260.0h | 80.0% | 20.03 | 0 |
| Thisoban | Google Ads | 99 | 213.5h | 93.9% | 21.34 | 0 |
| Jefri | Google Ads | 138 | 189.7h | 72.5% | 2.95 | 2 |
| Thivagini | Google Ads | 126 | 183.8h | 85.7% | 2.74 | 0 |
| Sukirtha | SEO | 116 | 169.5h | 0.0% ⚠ | 9.33 | 0 |
| Sonya | Google Ads | 94 | 166.8h | 95.7% | 4.26 | 0 |
| Mahima | Google Ads | 96 | 146.5h | 71.9% | 3.41 | 1 |
| Dilaksi | SEO | 82 | 134.0h | 17.1% ⚠ | 15.64 | 0 |
| Jakshan | SEO | 72 | 123.5h | 100.0% ✓ | 17.41 | 0 |
| Theekshy | ADS | 24 | 46.5h | 100.0% ✓ | 0.95 | 0 |
| Thasitha | ADS ⚠ | 20 | 38.0h | 100.0% ✓ | 1.24 | 0 |
| Thanishtika | ADS | 16 | 30.0h | 100.0% ✓ | 1.27 | 0 |

### Integrity findings from the MCP queries

- **ph_id `DMK004` → two names** (Thasitha, Thisoban). Confirmed via `GROUP BY ph_id HAVING COUNT(DISTINCT ph_name) > 1`.
- **`ADS` department** members are mostly existing Google Ads staff (Jefri, Mahima, Sajeepan, Sonya, Thisoban, Thivagini) plus three new starters.
- **Waste log unchanged** from D02 — 9 tasks / 13.5h; share fell to 0.4% only because total hours doubled. Kuberan 6 tasks (11.5h, external blockers), Jefri 2 (2h), Mahima 1 (0h).

---

## SECTION 4 · GAP FOUND

- **Master-data gap — 5 ph_ids unmatched in ph_master** (was 2): Theekshy (DMK005), Thanishtika (DMK006), Jakshan (DMKS05), Piranav (DMT001), Dilaksi (PH061). Band / yield / limit data is NULL for all five. An INNER JOIN would now silently drop 5 staff instead of 2 — LEFT JOIN remains mandatory.
- **Verification gap — Sukirtha 0%, Dilaksi 17.1%.** SEO overall improved to 48.5% but Sukirtha (116 tasks, 169.5h, zero proof) is the main drag.
- **Department-coverage gap — `ADS` vs `Google Ads`.** Hours for one team are split across two labels, so department totals understate the true Google Ads footprint.
- **Data gap — 10 days.** Last log 2026-05-29; today 2026-06-08. All "this week / this month / last 28 days" windows return 0 rows and fall back to all-time.
- **Registry gaps (carried from D02):** `ph_master.band` not standardised to A–G (only band=A staff match anchors/limits); `config_metric_values` covers only ~22% of tasks (9 metrics missing, GBB typo on 5 entries, duplicate ROAS row) — yield remains partial.

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

Two new pre-insert validations proposed for the `eod-csv-upload` skill (`tally.md`), driven by today's findings:

- **RULE ADDED — ph_id uniqueness check:** before insert, verify each `ph_id` maps to exactly one `ph_name` across the existing table; block/flag collisions such as `DMK004`. (No such check exists today — that is how the collision entered.)
- **RULE ADDED — department canonicalisation warning:** warn when a CSV introduces a `department` string that is a near-synonym of an existing one (`ADS` vs `Google Ads`), rather than silently creating a parallel code. `TRIM()` merges whitespace only, not synonyms.

Existing validation rules confirmed still correct (no change needed):

- `TRIM(l.department)` in GROUP BY/SELECT — still merges `SEO `/`SEO`.
- `LEFT JOIN ph_master` — still required (5 unmatched ph_ids).
- `AND mv.currency = 'GBP'` on the metric join — still prevents ROAS fan-out.

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Edge case (handled):** time-window query for "this week" returned 0 rows because data ends 2026-05-29. Skill correctly fell back to all-time and reported the actual data range. Verified live.
- **Failure mode (open):** ph_id collision `DMK004` — any per-staff query keyed on ph_id will merge or misattribute Thasitha's and Thisoban's work until one is re-coded.
- **Failure mode (open):** synonym department codes — `ADS`/`Google Ads` split a single team across two groups in every department-level rollup.
- **Failure mode (avoided):** INNER JOIN on ph_master would now drop 5 staff (was 2). Avoided by mandatory LEFT JOIN.
- **Edge case (guarded):** `config_metric_values` ROAS has two rows (GBP + GBB typo); without the `currency = 'GBP'` filter the metric join fans out and double-counts. Guard is in place.

---

## SECTION 7 · DECISIONS MADE TODAY

- **Read-only session — no production writes.** Re-coding `DMK004` and merging `ADS` are write operations on live data; decided to flag them for HR rather than execute them unilaterally.
- **Recommended canonical department = `Google Ads`** — merge `ADS` rows into it (decision pending HR sign-off).
- **Re-code decision deferred** — which of Thasitha / Thisoban keeps `DMK004` needs HR/owner input; flagged, not chosen.
- **Keep report as corrected D03** — applied template fixes to yesterday's file rather than deferring to D04.
- **No skill-file edits made today** — proposed validation rules logged in Section 5 for review before changing `tally.md`.
- **Dashboard rebuild deferred** — artifact still reflects the old 1,006-row dataset; rebuild to be done after DMK004/ADS fixes so it isn't built on dirty data.

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### What today's test pass proved about the skill file

The `eod-query-answerer` skill ran against a dataset that nearly doubled (1,006 → 1,782 rows) with no edits:

- **Step 0 live-facts query** reported the new totals — the "never hardcode" rule held; every figure in this file came from the live DB.
- **TRIM(l.department)** merges whitespace but surfaced a problem it cannot fix automatically — a genuinely different code (`ADS` vs `Google Ads`). Synonym merging needs a registry decision, not TRIM.
- **Time-window fallback** behaved correctly on the larger data.
- **LEFT JOIN ph_master** stayed essential — unmatched ph_ids grew 2 → 5.

### Data-integrity rules to add to the upload skill

1. ph_id uniqueness check before insert (catch collisions like `DMK004`).
2. Department synonym warning (catch `ADS` vs `Google Ads`).

### Verification trend (auditable)

| Date | Rows | Overall Ver % | SEO Ver % | Data gap |
| :---- | :---- | :---- | :---- | :---- |
| 2026-06-04 (D02) | 1,006 | 53.2% | 4.3% | 41 days |
| 2026-06-08 (D03) | 1,782 | 73.6% | 48.5% | 10 days |

### File Naming Standard

```
YYYY-MM-DD__[developer]__[project-code]__[deliverable-id].md
Example: 2026-06-08__abiraj__eod__REQ-03-D03.md
```

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (3–7)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment

A developer with no context could understand from this file alone:

- **WHAT** was done today — tested the query skill against newly-loaded May data and audited it for integrity problems
- **WHAT** changed in the data — 1,006 → 1,782 rows, May loaded, verification 53.2% → 73.6%, SEO 4.3% → 48.5%
- **WHAT** is newly broken — ph_id `DMK004` collision (Thasitha/Thisoban) and `ADS` duplicating Google Ads
- **WHO** still needs action — Sukirtha (0% verification); 3 new starters missing from ph_master
- **WHY** the skill held up — Step 0 live query, TRIM, LEFT JOIN and time-window fallback behaved correctly
- **WHERE** everything lives — PostgreSQL ROI at vintageinterior.co.uk, MCP at eod-mcp.vintageinterior.co.uk/sse
- **WHAT** to do next — fix DMK004, merge ADS, chase June upload, add new starters to ph_master

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-06-08__abiraj__eod__REQ-03-D03.md`
- [x] Metadata complete — includes `blos_keys_used` and `hardcoded_thresholds`
- [x] Six performance fields moved out of metadata into Section 3
- [x] Section names 3–7 match standard template (POSTGRESQL/MCP FINDING, GAP FOUND, VALIDATION RULE ADDED OR CHANGED, FAILURE MODE OR EDGE CASE, DECISIONS MADE TODAY)
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written
- [x] All numbers pulled live
- [ ] ⚠️ **OPEN:** Resolve ph_id collision DMK004
- [ ] ⚠️ **OPEN:** Merge ADS into Google Ads
- [ ] ⚠️ **OPEN:** Sukirtha 0% verification action
- [ ] ⚠️ **OPEN:** Upload June 2026 EOD CSV (10-day gap)
- [ ] ⚠️ **OPEN:** Add 3 new starters to ph_master

---
*DIGITWEB LK LTD — Daily Skill Increment System — v3.0 — June 2026*
