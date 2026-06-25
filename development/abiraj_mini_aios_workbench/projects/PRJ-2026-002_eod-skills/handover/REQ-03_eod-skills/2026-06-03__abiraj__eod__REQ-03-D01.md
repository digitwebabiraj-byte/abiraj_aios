
## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-03 |
| **developer** | abiraj |
| **project** | EOD Performance Tracker |
| **project\_code** | eod |
| **phase** | OPERATIONS |
| **requirement\_id** | REQ-03 |
| **deliverable\_id** | D01 |
| **status** | COMPLETE |
| **evidence\_location** | `daily_eod_log` — PostgreSQL · ROI database · vintageinterior.co.uk |
| **data\_range** | 2026-02-03 to 2026-04-24 |
| **total\_tasks\_logged** | 1,006 |
| **total\_hours\_logged** | 1,576.44h |
| **verification\_rate** | 53.2% (535 of 1,006 tasks) |
| **high\_value\_pct** | 80.6% (Tier S + A hours) |
| **waste\_hours** | 13.5h across 9 tasks (0.9%) |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | EOD \| PERFORMANCE \| YIELD \| VERIFICATION \| WASTE \| STAFF |

---

## SECTION 1 · SYSTEM STATE

- **Current system state:** EOD performance log active with 1,006 tasks across 13 ph\_ids (12 staff names), 5 departments, Feb 3 to Apr 24 2026. Skill file at v2 with live MCP connection to PostgreSQL ROI database. 50 predefined questions active in predefined\_question table. Dashboard artifact built and verified.
- **What was working:** EOD log with 865 rows, skill file with hardcoded data facts, date range Feb 3 to Apr 3 2026.
- **What was broken / missing at start:** (1) Skill file had 10 hardcoded data facts that became stale after each CSV upload. (2) DMT001 (Piranav) unmatched in ph\_master — not documented in skill file. (3) TECH department (141 rows) entirely absent from skill file department list. (4) Leave scenario value not documented. (5) Time-windowed questions Q1, Q9, Q15 returning 0 rows due to 40-day data gap. (6) Blocked scenario count wrong (3 → 10).
- **Your starting point:** 1,006 rows in daily\_eod\_log. Last entry date: Apr 24 2026. Skill file corrected — hardcoded counts replaced with live Step 0 query.
- **Environment:** Production — EOD query skill, dashboard, and data audit session.

> **In plain terms:** The daily task log has 1,006 entries from 12 staff across 5 departments. The reference guide used by Claude to answer HR questions had become out of date — it had wrong row counts, a missing department, and an undocumented staff member. Everything has been corrected. The guide now runs a live database check before answering any question, so it will always use the correct numbers regardless of when new data is uploaded.

---

## SECTION 2 · WHAT CHANGED TODAY

- **Change 1 — sql\_generate\_skill.md corrected — hardcoded values removed:**
  All 10 stale hardcoded data facts removed from the Key Data Facts table. Replaced with a new Step 0 — a live SQL query that runs at the start of every session to fetch current row count, date range, staff count, verified count, waste count, and null delta count directly from the database. This means the skill file will always be accurate regardless of when new CSV data is uploaded. No manual update needed after each upload.

  > **In plain terms:** The reference guide for answering HR questions used to have fixed numbers baked in — like "865 tasks" and "data ends Apr 3". These numbers went wrong every time new data was added. Now the guide checks the live database for those numbers every time it runs, so it always gives the correct answer.

- **Change 2 — Piranav (DMT001) added to unmatched ph\_id documentation:**
  DMT001 (Piranav) identified as a second unmatched ph\_id in ph\_master. Previously only PH061 (Dilaksi) was documented as unmatched. Piranav has 60 rows in daily\_eod\_log with no corresponding ph\_master record. Pattern 3 LEFT JOIN rule now covers both unmatched ph\_ids. A live query added to check for unmatched ph\_ids dynamically at runtime.

  > **In plain terms:** One staff member (Piranav) was missing from the staff master table, meaning some queries were silently dropping their 60 task records. This is now documented and the query patterns are written to keep all staff in results regardless.

- **Change 3 — TECH department added to skill file:**
  TECH department with 141 rows entirely absent from Relationship 6 department list. Added with note that it does not merge with Technical / GTM or Technical / UI-UX via TRIM. TECH is a separate raw value. Department count corrected from 4 to 5 in all relevant sections.

  > **In plain terms:** A whole department (TECH, 141 tasks) was missing from the documentation. Any department comparison query would have produced incomplete results. This is now corrected.

- **Change 4 — Leave scenario value documented:**
  scenario column now has 3 distinct values: Normal (994), Blocked (10), Leave (2). Previously only Normal and Blocked were documented, and Blocked count was wrong (3 → 10). All scenario values now listed correctly in the stable structural facts section.

  > **In plain terms:** The Leave scenario was never written down. Staff on leave have 2 task entries logged under this value. It is now documented so queries filtering by scenario produce complete results.

- **Change 5 — EOD dashboard artifact built and verified:**
  Full live dashboard artifact built inside claude.ai with 4 tabs: Overview (KPIs, tier bars, weekly chart, department cards, top performers, scenarios), Staff (sortable table), Departments (hour bars, verification bars, detail cards), Metrics & Waste (top 10 metrics, waste log). All numbers verified against live DB. Artifact can be published for HR access.

  > **In plain terms:** A live visual dashboard was built that shows all EOD performance data in one place. It has charts, staff tables, and department breakdowns. It runs inside Claude and can be shared with HR as a published link.

---

## SECTION 3 · LAST DATE DATA (2026-04-24)

### Tasks logged on Apr 24 2026

| Staff | Dept | Tier | Task | Metric | Δ | Hours | Verified |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Kuberan | TECH | A | Pre-Order App Installation & Testing | CVR | 2 | 2.0h | ✅ |
| Kuberan | TECH | A | Bulk Buy Badge UX Enhancement | CTR | 2 | 1.0h | ✅ |
| Kuberan | TECH | B | Google Search Console Weekly Check | ORGANIC\_SESSIONS | — | 1.0h | ✅ |
| Kuberan | TECH | A | Ledsone.de Language Corrections – Final Pass | CVR | 1 | 1.0h | ✅ |
| Piranav | TECH | A | Configurator UI – Final Corrections & QA | CVR | 3 | 2.0h | ✅ |
| Piranav | TECH | A | FAQ Schema Deployment – Additional Products | CTR | 3 | 1.5h | ✅ |
| Piranav | TECH | A | Speed Testing + Website UI Review | PAGE\_SPEED | 1 | 1.5h | ✅ |
| Piranav | TECH | B | Learning / Skill Development | PROCESS\_QUALITY | 1 | 0.5h | ✅ |

**Day summary:** 8 tasks · 10.5h · 100% verified · 0 waste · 75% high-value (Tier A)

---

## SECTION 4 · CUMULATIVE PERFORMANCE SUMMARY

### Overall KPIs (Feb 3 – Apr 24 2026)

| Metric | Value |
| :---- | :---- |
| Total tasks | 1,006 |
| Total hours | 1,576.44h |
| Verified tasks | 535 (53.2%) |
| High-value hours (Tier S+A) | 1,270.87h (80.6%) |
| Wasted hours | 13.5h (0.9%) |
| Waste tasks | 9 |
| Active staff | 12 names / 13 ph\_ids |
| Departments | 5 |

### Tier distribution

| Tier | Tasks | Hours | % of total hours |
| :---- | :---- | :---- | :---- |
| S (Strategic) | 27 | 87.0h | 5.5% |
| A (Revenue-Direct) | 703 | 1,183.9h | 75.1% |
| B (Revenue-Support) | 166 | 201.1h | 12.8% |
| C (Operational) | 107 | 102.7h | 6.5% |
| D (Admin) | 3 | 1.8h | 0.1% |

### Department summary

| Department | Staff | Tasks | Hours | High-val % | Verified % | Δ total |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Google Ads | 6 | 467 | 699.4h | 84.0% | 72.6% | 4,268 |
| SEO | 4 names/5 ids | 323 | 506.0h | 81.8% | 4.3% ⚠ | 6,577 |
| TECH | 2 | 141 | 235.0h | 84.0% | 100.0% ✓ | 628 |
| Technical / GTM | 1 | 47 | 85.0h | 51.2% | 55.3% | 445 |
| Technical / UI-UX | 1 | 28 | 51.0h | 54.9% | 53.6% | 308 |

### Staff performance

| Staff | Dept | Tasks | Hours | Ver % | Δ/hr | Waste |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Kuberan | TECH/GTM/UI | 156 | 273.5h | 78.2% | 4.12 | 6 |
| Sajeepan | Google Ads | 131 | 199.0h | 73.3% | 3.72 | 0 |
| Sukirtha | SEO | 116 | 169.5h | 0.0% ⚠ | 9.33 | 0 |
| Hetheesha | SEO | 92 | 152.0h | 0.0% ⚠ | 14.78 | 0 |
| Thisoban | Google Ads | 64 | 134.5h | 90.6% | 16.70 | 0 |
| Dilaksi | SEO | 82 | 134.0h | 17.1% ⚠ | 15.64 | 0 |
| Jefri | Google Ads | 98 | 118.2h | 61.2% | 3.65 | 2 |
| Piranav | TECH | 60 | 97.5h | 100.0% ✓ | 2.61 | 0 |
| Thivagini | Google Ads | 66 | 91.5h | 72.7% | 3.84 | 0 |
| Mahima | Google Ads | 65 | 80.5h | 58.5% | 4.76 | 1 |
| Sonya | Google Ads | 43 | 75.8h | 90.7% | 1.54 | 0 |
| Kamsi | SEO | 33 | 50.5h | 0.0% ⚠ | 12.95 | 0 |

---

## SECTION 5 · ISSUES & ALERTS

### Critical — Verification

- **SEO department: 4.3% verification rate** — 309 of 323 tasks unverified. Hetheesha (0%), Kamsi (0%), Sukirtha (0%) have never submitted a verification URL. Dilaksi at 17.1%. High delta values remain unconfirmed.
- **Unverified high-delta tasks** — SEO staff claim the highest delta/hr values (9–15 range) but have the lowest verification. Cannot confirm accuracy without URLs.

### Warning — Data Gap

- **No data since Apr 24 2026** — 40-day gap as of Jun 3 2026. All time-windowed questions (this week, this month, last 28 days) return 0 rows. May and June EOD logs not yet uploaded.

### Warning — Registry Gaps

- **ph\_master.band not standardised** — Senior, Junior, Probationer do not match config\_yield\_anchors bands (A–G). Only 2 staff (band=A) have yield anchor data. 11 staff cannot be yield-benchmarked.
- **config\_metric\_values covers only ~22% of tasks** — 9 metrics missing from registry. GBB typo on 5 entries. Yield calculations are partial.
- **DMT001 (Piranav) missing from ph\_master** — 60 rows in daily\_eod\_log with no master record.

### Info — New Items Found

- **TECH department** — 141 rows, 2 staff (Kuberan, Piranav), 100% verification. New department not previously documented.
- **Leave scenario** — 2 rows with scenario = 'Leave'. Not previously documented.
- **Blocked scenario** increased from 3 to 10 rows since last skill file update.

---

## SECTION 6 · WASTE LOG

| Waste type | Staff | Tasks | Hours |
| :---- | :---- | :---- | :---- |
| Blocked – mobile alignment | Kuberan | 1 | 4.0h |
| Blocked – YouTube Error 153 | Kuberan | 2 | 3.0h |
| Unplanned | Jefri | 2 | 2.0h |
| Blocked – form submission failed | Kuberan | 1 | 2.0h |
| API rate limit | Kuberan | 1 | 1.5h |
| Blocked – root cause unknown | Kuberan | 1 | 1.0h |
| Wrong approach | Mahima | 1 | 0.0h |

**Total: 9 tasks · 13.5h · 0.9% of all hours**
Kuberan accounts for 6 of 9 waste tasks (11.5h) — all blocked by external issues.

---

## SECTION 7 · OPEN ITEMS

- [ ] ⚠️ **CRITICAL:** Upload May 2026 and June 2026 EOD CSV files to fill 40-day data gap
- [ ] ⚠️ **CRITICAL:** SEO department verification — Hetheesha, Kamsi, Sukirtha at 0% — action required
- [ ] **OPEN:** Standardise ph\_master.band to A–G format — unlocks yield anchors for all 12 staff
- [ ] **OPEN:** Add DMT001 (Piranav) to ph\_master — 60 rows currently unlinked
- [ ] **OPEN:** Fix config\_metric\_values — add 9 missing metrics with GBP base\_value
- [ ] **OPEN:** Fix GBB typo to GBP for CTR, Impressions, LISTING\_PERFORMANCE, Rank, RETURN\_RATE
- [ ] **OPEN:** Remove duplicate ROAS entry from config\_metric\_values (keep GBP only)
- [ ] **OPEN:** Align config\_departments.department\_id to actual daily\_eod\_log department values
- [ ] **OPEN:** Decide on TECH department mapping — is it separate from Technical / GTM and UI-UX?

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### EOD System Architecture

The EOD performance system consists of:
- `daily_eod_log` — main task log table (1,006 rows, grows with each CSV upload)
- `ph_master` — staff master table (13 records, band classification not yet A–G standardised)
- `config_task_tiers` — tier definitions A/B/C/D/S with value multipliers (100% reliable JOIN)
- `config_metric_values` — metric base values for yield calculation (GBP only, ~22% coverage)
- `config_yield_anchors` — minimum yield per hour by band (band=A staff only currently)
- `config_band_limits` — admin hour limits by band (band=A staff only currently)
- `predefined_question` — 50 active HR/management questions with pre-written SQL
- `config_departments` — department registry (zero rows match daily\_eod\_log — do not JOIN)

### Key Structural Rules (Never Changes)

- `verified` and `waste\_flag` are bigint — always compare with `= 1` not `= TRUE`
- `date` column is timestamp — cast with `::date` for date comparisons
- `department` has trailing spaces — always `TRIM(l.department)` in GROUP BY
- Never JOIN `config\_departments` — zero rows match
- Always `LEFT JOIN config\_metric\_values ... AND mv.currency = 'GBP'` — ROAS has 2 entries
- Always `LEFT JOIN ph\_master` — some ph\_ids have no master record

### Yield Coverage Limitation

Only ~22% of tasks have a valid GBP base\_value in config\_metric\_values. Delta/hr calculations using raw metric\_delta are available for all rows but are not monetised. True yield calculation requires registry expansion.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES |
| Is the GAP section completed or marked NONE? | ✅ YES |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES |
| Is metadata complete? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment

A developer with no context could understand from this file alone:

- **WHAT** the EOD system tracks — daily task logs per staff, with tier, metric, hours, verification, and waste
- **HOW** to query it — LEFT JOIN ph\_master, TRIM department, verified=1 not TRUE, always AND mv.currency='GBP'
- **WHY** some queries return wrong numbers — hardcoded facts in skill file became stale; now replaced with live Step 0 query
- **WHO** has the worst verification problem — SEO dept at 4.3%, four staff at 0–17%
- **WHAT** the top performers look like — Thisoban (16.70 Δ/hr), Dilaksi (15.64), Hetheesha (14.78)
- **WHAT** is blocking full yield calculation — ph\_master bands not standardised, 9 metrics missing from config\_metric\_values
- **WHAT** needs uploading urgently — May and June 2026 EOD data (40-day gap)
- **WHERE** the live data is — PostgreSQL ROI database, daily\_eod\_log table, vintageinterior.co.uk

---
