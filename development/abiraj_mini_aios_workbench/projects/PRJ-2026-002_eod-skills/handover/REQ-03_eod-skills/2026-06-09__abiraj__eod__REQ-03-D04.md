## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-09 |
| **developer** | abiraj |
| **project** | EOD Performance Tracker |
| **project\_code** | eod |
| **phase** | OPERATIONS |
| **requirement\_id** | REQ-03 |
| **deliverable\_id** | D04 |
| **status** | COMPLETE |
| **evidence\_location** | `daily_eod_log`, `ph_master`, `config_metric_values`, `config_departments` — PostgreSQL · ROI database · vintageinterior.co.uk |
| **blos\_keys\_used** | NONE — data integrity correction session; no business logic constants written |
| **hardcoded\_thresholds** | NONE — all figures pulled live via Step 0 / MCP `execute_sql` at runtime |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | EOD \| DATA-INTEGRITY \| DB-FIXES \| PH-MASTER \| HR-REPORT \| UPLOAD-GUIDE |

## File path (fill after saving):
# 2026-06-09__abiraj__eod__REQ-03-D04.md

---

## SECTION 1 · SYSTEM STATE

- **Current system state:** EOD performance system operational. Full data integrity audit completed and 34 database fixes applied directly via MCP `execute_sql`. Dataset grew from D03 state (1,782 rows) to 2,560 rows as new team data was discovered already present in the database. ph_master expanded from ~11 records to 40. All 9 departments now registered in `config_departments`. All 36 active ph_ids now matched in ph_master — zero unmatched staff remaining.
- **What was working at start of today:** D03 identified the DMK004 ph_id collision, the ADS/Google Ads synonym problem, 5 unmatched staff, and a GBB currency typo. All were deferred as write operations in D03.
- **What was broken / missing at start of today:** DMK004 shared by Thasitha and Thisoban; PH061 wrong ID for Dilaksi; GBB typo on 6 config rows; duplicate ROAS entry; trailing spaces in department column (532 rows); Kamsi's April CSV uploaded twice (22 duplicate task rows); ph_master had only 6 records for 35 active staff; 9 departments used in the log had no config_departments entry; tab/space/double-space corruption in ph_master.department; 2 duplicate ph_master rows (Saranya, Jubista); band values with trailing spaces, wrong casing and a typo ("Senoir"); DMT001 name field contained the ph_id string instead of the person's name.
- **Your starting point:** D03 complete — integrity issues documented but no writes applied. Today was the correction execution pass plus HR and team-leader documentation.
- **Environment:** Production — claude.ai · EOD MCP (`eod-mcp.vintageinterior.co.uk/sse`) · PostgreSQL ROI database · vintageinterior.co.uk

> **In plain terms:** D03 found everything that was wrong. D04 fixed it. 34 specific database corrections were applied, two HR documents were produced, and a team-leader upload guide was written to prevent these problems recurring.

---

## SECTION 2 · WHAT CHANGED TODAY

- **Change 1 — PH061 wrong ID corrected (6 rows):** Dilaksi had 6 tasks filed under phantom ID PH061 due to a CSV upload typo on 26–27 March 2026. Corrected to DMKS02.
  > `UPDATE daily_eod_log SET ph_id = 'DMKS02' WHERE ph_id = 'PH061'`

- **Change 2 — Trailing spaces removed from department column (532 rows):** "Google Ads " and "SEO " had invisible trailing spaces causing department totals to be split across two labels in every GROUP BY query.
  > `UPDATE daily_eod_log SET department = TRIM(department) WHERE department != TRIM(department)`

- **Change 3 — Thasitha ph_id corrected (20 rows):** Thasitha's 20 task rows were filed under DMK004 (Thisoban's ID). Her ph_master record uses DMG004. All task rows corrected.
  > `UPDATE daily_eod_log SET ph_id = 'DMG004' WHERE ph_name = 'Thasitha' AND ph_id = 'DMK004'`

- **Change 4 — Kamsi duplicate task rows deleted (22 rows):** Kamsi's April 2026 CSV was uploaded twice, creating 22 exact duplicate task rows (S0411–S0432). Duplicates removed using ctid; one copy of each kept.

- **Change 5 — TECH renamed to Technical / GTM (321 rows):** "TECH" was a shorthand synonym for "Technical / GTM". Confirmed by HR and merged.
  > `UPDATE daily_eod_log SET department = 'Technical / GTM' WHERE department = 'TECH'`

- **Change 6 — ADS renamed to Google Ads (205 rows):** "ADS" was a shorthand synonym for "Google Ads". Confirmed by HR and merged. D03 open item resolved.
  > `UPDATE daily_eod_log SET department = 'Google Ads' WHERE department = 'ADS'`

- **Change 7 — GBB currency typo corrected (6 rows):** config_metric_values had currency = "GBB" on 6 rows (CTR, Impressions, LISTING_PERFORMANCE, Rank, RETURN_RATE, ROAS duplicate). Corrected to GBP.
  > `UPDATE config_metric_values SET currency = 'GBP' WHERE currency = 'GBB'`

- **Change 8 — Duplicate ROAS entry deleted (1 row):** ROAS had two entries (id=2 GBP correct; id=9 GBB typo). id=9 deleted. Prevents row fan-out in metric JOINs.
  > `DELETE FROM config_metric_values WHERE id = 9`

- **Change 9 — Revenue unit corrected (1 row):** `unit_description` said "per €1" (Euro) in a GBP table — corrected to "per £1".

- **Change 10 — config_departments primary_currency and is_active populated (7 rows):** Both columns were NULL for all 7 existing rows. Set primary_currency = 'GBP', is_active = 'true'.

- **Change 11 — 5 new team departments added to config_departments:** Jasmini's Team, Renuha's Team, Thuwaraga's Team, Jubista's Team, Utharsika's Team were all missing from the registry. All added with primary_currency = 'GBP', is_active = 'true'.

- **Change 12 — ph_master duplicate rows deleted (2 rows):** Saranya (JAS-004) and Jubista (JUB-STL) each had two identical rows. Duplicates deleted (ids 58 and 36).

- **Change 13 — Band trailing spaces removed from ph_master (9 staff):** Jasmini, Tharsika Nelliyadi, Thuwaraga, Paul Roshan, Tharsika Jaffna, Shimee, Poovitha, Utharsika, Arudchelvi all had "Senior " with a trailing space. Trimmed.
  > `UPDATE ph_master SET band = TRIM(band) WHERE band != TRIM(band)`

- **Change 14 — Band casing corrections (3 staff):** Theekshy: "probationer" → "Probationer". Thanucha (THU-005): "INTERN" → "Intern". Piranav (DMT001): "Senoir" → "Senior" (typo).

- **Change 15 — DMT001 name field corrected:** Piranav's name field contained the string "DMT001" (the ph_id was entered in the name column by mistake). Corrected to "Piranav".
  > `UPDATE ph_master SET name = 'Piranav' WHERE ph_id = 'DMT001' AND name = 'DMT001'`

- **Change 16 — Tab characters, leading spaces and double spaces removed from ph_master.department (10 staff):** Sajeepan, Theekshy, Thasitha had a tab character prefix. Jefri had a leading space. Mahima had a trailing space. Kamsi, Dilaksi, Sukirtha, Hetheesha, Jakshan had "SEO  -Website" with a double space. All cleaned.
  > `UPDATE ph_master SET department = TRIM(REPLACE(REPLACE(department, chr(9), ''), '  ', ' ')) WHERE ...`

- **Change 17 — 5 missing staff added to ph_master:** Renuha (REN-STL), Thojika (REN-001), Nithushana (REN-003), Tharshana (REN-004) added as Senior. Thanishtika (DMK006) added as Probationer. All had been logging tasks with no master record.

- **Change 18 — ph_master department standardised to sub-team names (Option B):** JAS/JUB/THU/UTH staff had department = "PH" in ph_master but logged tasks under sub-team names (e.g. "Jasmini's Team"). This caused zero JOIN matches. Option B chosen: update ph_master to use sub-team department name. All 20 affected staff updated.

- **Change 19 — Original staff ph_master departments aligned to log values:** DMK/DMKS/DMT staff had "Google Ads -Website", "SEO -Website", "TECH-Website" style in ph_master — not matching daily_eod_log values. Corrected to exact match: "Google Ads", "SEO", "Technical / GTM".

- **Change 20 — ph_master TECH-Website → Technical / GTM-Website:** DMT001 and DMT002 profiles updated to align with the TECH → Technical / GTM rename.

- **Deliverable A — HR Issues Report produced:** Word document `EOD_Issues_Report_J_Abiraj.docx` — covers 57 problems found, 34 fixed by J. Abiraj, 23 remaining. Includes verification rate table for all 36 staff, plain-English explanations, and sign-off table.

- **Deliverable B — Team Leader Upload Guide produced:** Word document `EOD_Upload_Guide_Team_Leaders.docx` — 9 sections: why it matters, every CSV column explained with common mistakes, tier guide, 10-point pre-upload checklist, approved department name list, 8 most common mistakes with prevention advice, weekly process schedule, quick-reference card, acknowledgement sign-off.

Evidence reference: All SQL corrections applied via `End_of_the_day_performance_check_Postgress` MCP `execute_sql`. No credentials included. Both documents saved to output.

---

## SECTION 3 · POSTGRESQL / MCP FINDING

All results below returned live from `End_of_the_day_performance_check_Postgress` MCP `execute_sql`. Nothing hardcoded.

### Live data snapshot — post-correction state (D04)

| Field | D03 value | D04 value (now) | Change |
| :---- | :---- | :---- | :---- |
| Total rows | 1,782 | 2,560 | +778 (new teams discovered) |
| Data range | 2026-02-03 → 2026-05-29 | 2026-02-03 → 2026-06-08 | Max date advanced |
| Total hours | 3,083.77h | 4,753.97h | +1,670.2h |
| Distinct staff (ph_id) | 16 | 36 | +20 (new teams) |
| Verified count | 1,311 (73.6%) | 2,089 (81.6%) | +778 verified |
| Unverified count | 471 (26.4%) | 471 (18.3%) | Unchanged — same staff issues |
| Null metric_delta | 454 | 1,245 | Higher — new team data has zero delta |
| Waste tasks | 9 | 9 | Unchanged |
| Unmatched ph_ids | 5 | 0 | ✓ All resolved |
| Duplicate ph_ids | 1 (DMK004) | 0 | ✓ Resolved |
| Duplicate task rows | 22 (Kamsi) | 0 | ✓ Resolved |
| Dept config gaps | 7 departments | 0 | ✓ All 9 depts registered |

### Tier distribution (post-fix)

| Tier | Tasks | Hours | % of tasks | % of hours |
| :---- | :---- | :---- | :---- | :---- |
| S (Strategic) | 37 | 124.5h | 1.4% | 2.6% |
| A (Revenue-Direct) | 1,407 | 2,610.1h | 55.0% | 54.9% |
| B (Revenue-Support) | 954 | 1,836.4h | 37.3% | 38.6% |
| C (Operational) | 159 | 181.2h | 6.2% | 3.8% |
| D (Admin) | 3 | 1.8h | 0.1% | 0.0% |

> **Note:** Tier B share has risen significantly (9.2% in D03 → 38.6% in D04) due to new team data — Jasmini's, Jubista's, Renuha's, Thuwaraga's, Utharsika's Teams log predominantly Tier B tasks.

### Department summary (post-fix — all 9 matched in config)

| Department | Staff | Tasks | Hours | High-val % | Verified % |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Google Ads | 9 | 786 | 1,308.3h | 86.5% | 83.7% |
| Jasmini's Team | 5 | 584 | 1,189.9h | 2.5% ⚠ | 100.0% ✓ |
| SEO | 5 | 578 | 944.0h | 89.2% | 46.5% ⚠ |
| Technical / GTM | 2 | 368 | 745.0h | 77.9% | 94.3% ✓ |
| Renuha's Team | 4 | 68 | 160.9h | 30.5% ⚠ | 100.0% ✓ |
| Thuwaraga's Team | 4 | 57 | 140.8h | 40.7% ⚠ | 100.0% ✓ |
| Jubista's Team | 5 | 55 | 130.1h | 12.3% ⚠ | 100.0% ✓ |
| Utharsika's Team | 2 | 36 | 84.0h | 0.0% ⚠ | 100.0% ✓ |
| Technical / UI-UX | 1 | 28 | 51.0h | 54.9% | 53.6% |

> **New team observation:** Jasmini's, Jubista's, Renuha's, Thuwaraga's and Utharsika's Teams show very low high-value task % (0–40%) and zero metric_delta across all tasks. This is likely a data-completeness issue — metric_name and task_tier may need review for these teams rather than an actual performance problem.

### Staff performance (post-fix, top 16 by hours)

| Staff | ph_id | Dept | Tasks | Hours | Ver % | Δ/hr | Waste |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Kuberan | DMT002 | Technical / GTM | 220 | 457.0h | 90.5% | 2.67 | 6 |
| Dilani | JAS-001 | Jasmini's Team | 182 | 368.0h | 100.0% ✓ | 0.00 ⚠ | 0 |
| Sajeepan | DMK001 | Google Ads | 173 | 293.5h | 79.8% | 4.82 | 0 |
| Hetheesha | DMKS04 | SEO | 165 | 292.5h | 44.2% ⚠ | 16.62 | 0 |
| Piranav | DMT001 | Technical / GTM | 148 | 288.0h | 100.0% ✓ | 1.93 | 0 |
| Prasath | JAS-003 | Jasmini's Team | 135 | 280.5h | 100.0% ✓ | 0.00 ⚠ | 0 |
| Jasmini | JAS-STL | Jasmini's Team | 124 | 252.0h | 100.0% ✓ | 0.00 ⚠ | 0 |
| Theepana | JAS-002 | Jasmini's Team | 118 | 234.0h | 100.0% ✓ | 0.00 ⚠ | 0 |
| Kamsi | DMKS01 | SEO | 143 | 224.5h | 76.9% | 19.65 | 0 |
| Thisoban | DMK004 | Google Ads | 99 | 213.5h | 93.9% | 21.34 | 0 |
| Jefri | DMG001 | Google Ads | 138 | 189.7h | 72.5% | 2.95 | 2 |
| Thivagini | DMK003 | Google Ads | 126 | 183.8h | 85.7% | 2.74 | 0 |
| Sukirtha | DMKS03 | SEO | 116 | 169.5h | 0.0% ⚠ | 9.33 | 0 |
| Sonya | DMK002 | Google Ads | 94 | 166.8h | 95.7% | 4.26 | 0 |
| Mahima | DMG002 | Google Ads | 96 | 146.5h | 71.9% | 3.41 | 1 |
| Dilaksi | DMKS02 | SEO | 82 | 134.0h | 17.1% ⚠ | 15.64 | 0 |

---

## SECTION 4 · GAP FOUND

- **Verification gap — Sukirtha 0%, Dilaksi 17.1% — UNCHANGED:** These two staff were flagged in D02 and D03. No improvement. Sukirtha has 116 tasks and 169.5h with zero proof. Escalated formally in the HR Issues Report (Deliverable A). Requires HR 1:1 — cannot be resolved by a database fix.

- **New team metric_delta gap — 5 teams, 0.00 Δ/hr across all tasks:** Jasmini's, Jubista's, Renuha's, Thuwaraga's, and Utharsika's Teams all have null metric_delta on every task. Their metric_name values ("Operational", "Sales") are also missing from config_metric_values. Root cause: new teams were onboarded without agreeing on KPIs or adding their metrics to the config registry. Impact: ROI is completely invisible for ~800 tasks (1,705 hours).

- **Metric registry gap — 10 metrics missing GBP base_value:** Operational (525 tasks, 1,053h), Sales (262 tasks, 629h), ORGANIC_SESSIONS (293 tasks, 534h), LISTING_QUALITY (154 tasks, 189h) and 6 more. ROI coverage remains ~30% of all task hours. Requires director decision on monetary value per metric.

- **Band standardisation gap — all 40 ph_master records use non-standard labels:** Senior, Junior, Probationer, Intern, Team Leader — none map to the A–G scale used by config_yield_anchors and config_band_limits. Zero staff can be benchmarked against yield targets or admin hour limits. Requires director approval of the mapping.

- **Salary and status gap — monthly_salary_lkr, expected_status, scenario NULL for all 40 staff:** Cost-per-hour and status tracking impossible. Requires HR to populate.

- **Data gap — 1 day:** Last log date 2026-06-08; today 2026-06-09. Acceptable — within normal range.

- **Open: unit_description and direction NULL for 5 config_metric_values rows:** CTR, Impressions, LISTING_PERFORMANCE, Rank, RETURN_RATE had currency fixed from GBB → GBP today but metadata fields remain blank. Requires director to confirm unit and direction per metric.

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

Four validation rules confirmed, corrected, or newly proposed today:

- **RULE CONFIRMED — department TRIM before GROUP BY:** `TRIM(l.department)` in all SELECT and GROUP BY statements. Validated — zero trailing-space rows remain post-fix. Still mandatory for future uploads that may reintroduce spaces.

- **RULE CONFIRMED — LEFT JOIN ph_master (not INNER JOIN):** Mandatory. Was 5 unmatched staff at D03 start; now 0 after ph_master additions. Rule remains in force because new staff will always be added before ph_master records are created.

- **RULE CONFIRMED — `AND mv.currency = 'GBP'` on metric JOIN:** Prevents ROAS fan-out. Duplicate ROAS row (id=9, GBB) deleted today — but the guard clause must remain because other metrics could have duplicate entries added in future.

- **RULE PROPOSED — Pre-upload ph_id collision check:** Before any CSV insert, verify that each ph_id in the incoming file maps to exactly one ph_name in daily_eod_log. If a new ph_name is found using an existing ph_id, block the insert and alert. This would have caught the DMK004 collision at source. Proposed for addition to `tally.md` (eod-csv-upload skill).

- **RULE PROPOSED — Department synonym warning on upload:** Before insert, check if incoming department string is a close synonym of an existing registered department (e.g. "ADS" vs "Google Ads", "TECH" vs "Technical / GTM"). TRIM() handles whitespace but not synonyms. Warn the uploader and require explicit confirmation before creating a new department code. Proposed for addition to `tally.md`.

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Failure mode (RESOLVED) — ph_id collision DMK004:** Thasitha's 20 task rows were merged with Thisoban's records. Resolved by correcting Thasitha's rows to DMG004 (her ph_master ID). Root cause: no uniqueness check on ph_id at upload time. Prevention: add pre-upload ph_id collision check (Section 5).

- **Failure mode (RESOLVED) — PH061 phantom ID:** Dilaksi's 6 tasks were filed under a non-existent ID due to a two-day upload error in March. Resolved by correcting to DMKS02. Root cause: same as above — no ph_id validation at upload.

- **Failure mode (RESOLVED) — Duplicate CSV upload (Kamsi):** Kamsi's April CSV was uploaded twice, creating 22 duplicate task rows and inflating her task count and hours by exactly 100%. Resolved by deleting duplicates. Prevention: team leaders instructed to log upload dates in the Team Leader Upload Guide (Deliverable B).

- **Failure mode (RESOLVED) — Department synonym split:** "TECH", "ADS" created parallel department codes that split totals for what were actually single teams. Resolved by renaming to canonical values. Prevention: approved department name list added to Deliverable B; synonym warning rule proposed for upload skill.

- **Failure mode (OPEN) — New team metric_delta all null:** 5 new teams have 0.00 Δ/hr across all tasks because "Operational" and "Sales" are not in config_metric_values. Any yield query against these teams returns 0 — indistinguishable from genuine zero performance. Risk level: HIGH. Resolution requires director to assign GBP base_values.

- **Failure mode (OPEN) — Band mismatch blocks all benchmarking:** No staff can be compared against yield anchors or admin hour limits because ph_master.band uses free-text labels not matching the A–G config scale. Risk level: MEDIUM. Resolution requires director band mapping decision.

- **Edge case (HANDLED) — ph_master department vs daily_eod_log department mismatch:** JAS/JUB/THU/UTH staff had department = "PH" in ph_master but sub-team names in the log. A JOIN on department would return zero matches. Resolved by Option B — updating ph_master to use sub-team names. Trade-off: PH as a parent group no longer exists in ph_master; queries wanting all PH teams must use a pattern match (e.g. `department LIKE '%Team%'`). Documented in HR report.

---

## SECTION 7 · DECISIONS MADE TODAY

- **Decision: Apply all 34 database corrections directly (not deferred).**
  Alternatives: defer to HR as write-only recommendations (D03 approach). Reason for change: D03 deferred because writes were unilateral on live data with no explicit authorisation. In D04 session, the business owner (HR) confirmed each correction category explicitly before execution. All changes are non-destructive (correct typos, remove duplicates, standardise values) with no business logic alteration. Trade-off accepted: live production data modified — risk accepted because all changes were reversible and verified by row count before and after.

- **Decision: Option B for ph_master department (sub-team names, not PH parent).**
  Alternatives: Option A (add sub-team names to config_departments, keep "PH" in ph_master); Option C (add parent_team column to ph_master). Option B chosen for simplicity — no schema change required, JOINs between ph_master and daily_eod_log now work correctly. Trade-off: PH-level roll-up queries require a LIKE pattern rather than a direct equality match. Documented for future developers.

- **Decision: Confirm TECH = Technical / GTM and ADS = Google Ads before renaming.**
  D03 flagged these as suspected synonyms but could not confirm. In D04, HR confirmed both matches explicitly before any UPDATE was run. No assumption made without sign-off.

- **Decision: Produce two HR deliverables (Issues Report and Upload Guide) from this session.**
  HR requested a clear summary of what was found, what was fixed, and what remains. A separate upload guide was produced because the root cause of most data problems was team leaders not knowing the correct upload procedure — this needed a standalone reference document, not just a paragraph in the issues report.

- **Decision: Do not attempt to populate monthly_salary_lkr, expected_status, band A–G, or metric base_values.**
  These require business decisions (monetary value per metric, salary data, band-to-role mapping) that only HR and the director can make. Flagged as open items. Writing placeholder values would create misleading data.

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule — ph_id must be unique per person, globally

A ph_id collision (two names sharing one ID) cannot be detected by the database because no UNIQUE constraint exists on ph_id in ph_master or daily_eod_log. The collision was caught only by querying `GROUP BY ph_id HAVING COUNT(DISTINCT ph_name) > 1`. This query must be run after every new data upload as a standard health check. A UNIQUE constraint on ph_master.ph_id should be added to enforce this at the database level.

### Business Rule — department values in daily_eod_log must be copy-pasted, never typed

Every department-related data problem found in this audit (trailing spaces, tab characters, synonym codes, double spaces) was caused by manual typing in CSV files. The canonical department names are:

```
Google Ads
SEO
Technical / GTM
Technical / UI-UX
Jasmini's Team
Jubista's Team
Thuwaraga's Team
Utharsika's Team
Renuha's Team
```

These names must be distributed to all team leaders as a copy-paste reference. Any new department must be added to config_departments before it is used in a CSV upload — not after.

### Business Rule — ph_master.department must match daily_eod_log.department exactly

ph_master and daily_eod_log are joined on ph_id, not department — so a department mismatch does not break staff-level queries. However, any query that joins on department (e.g. department performance reports) will silently drop staff whose ph_master.department does not match their log department. After Option B was applied, all 36 active staff now have matching department values in both tables. This must be maintained on every new hire addition.

### Operational Assumption — new teams log tasks before being added to ph_master

Pattern observed across three data loads (D01–D04): staff consistently appear in daily_eod_log before their ph_master record is created. The LEFT JOIN on ph_master is therefore not optional — an INNER JOIN will always drop recently-added staff. The eod-query-answerer skill correctly enforces LEFT JOIN for all ph_master lookups. This pattern will recur with every future hire.

### Operational Assumption — new teams use different ph_id formats

Original staff (2026-02 onwards): `DMAANN` format (e.g. DMK001, DMKS04).
New teams (2026-05 onwards): `XXX-NNN` format (e.g. JAS-001, THU-STL).
Both formats are accepted by the database. No standardisation was applied in D04. If a single format is preferred, a migration should be planned — but this is a cosmetic issue, not a data integrity one.

### Reusable Logic — five-query health check for every upload

Run these five queries after every CSV upload to confirm data integrity:

```sql
-- 1. ph_id collision check
SELECT ph_id, COUNT(DISTINCT ph_name) AS names
FROM daily_eod_log GROUP BY ph_id HAVING COUNT(DISTINCT ph_name) > 1;

-- 2. Unmatched ph_ids
SELECT DISTINCT l.ph_id, l.ph_name FROM daily_eod_log l
LEFT JOIN ph_master p ON l.ph_id = p.ph_id WHERE p.ph_id IS NULL;

-- 3. Trailing space in department
SELECT DISTINCT department FROM daily_eod_log WHERE department != TRIM(department);

-- 4. Duplicate task rows
SELECT task_id, ph_name, COUNT(*) AS cnt FROM daily_eod_log
WHERE task_id IS NOT NULL AND task_id != ''
GROUP BY task_id, ph_name, date, task_description, hours_spent HAVING COUNT(*) > 1;

-- 5. Department config coverage
SELECT TRIM(l.department) AS dept, COUNT(*) AS tasks
FROM daily_eod_log l
LEFT JOIN config_departments cd ON TRIM(l.department) = cd.department_id
WHERE cd.department_id IS NULL GROUP BY TRIM(l.department);
```

All five should return zero rows after a clean upload. If any return rows, correct before running reports.

### Verification trend (auditable)

| Date | File | Rows | Overall Ver % | SEO Ver % | Unmatched staff | Data gap |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| 2026-06-04 | D02 | 1,006 | 53.2% | 4.3% | 2 | 41 days |
| 2026-06-08 | D03 | 1,782 | 73.6% | 48.5% | 5 | 10 days |
| 2026-06-09 | D04 | 2,560 | 81.6% | 46.5% | 0 ✓ | 1 day ✓ |

### Canonical Vocabulary

| Term | Meaning |
| :---- | :---- |
| ph_id | Unique staff identifier — maps daily_eod_log tasks to ph_master profile |
| ph_master | Staff profile register — holds band, department, salary, expected_status |
| task_tier | S/A/B/C/D — value classification of a task (S = Strategic, A = Revenue-Direct) |
| verified | bigint 0/1 — whether the staff member confirmed the task as completed |
| verification_url | Proof link — screenshot or report URL supporting the verified flag |
| metric_delta | Numeric outcome value — the measurable result the task achieved |
| config_metric_values | Registry of KPIs with GBP monetary base_value for ROI calculation |
| config_departments | Registry of valid department names and their primary_currency |
| config_yield_anchors | Target yield per hour per band (A–G) — blocked until band standardised |
| high-value % | % of hours spent on Tier S + A tasks |
| STL | Sub-Team Lead — the XXX-STL ph_id pattern denotes a team leader |

### Cross-project applicability

The five-query health check (above) is reusable for any project using a CSV-upload-to-PostgreSQL pattern. The ph_id uniqueness and department canonicalisation rules apply to any system where staff records and task logs are in separate tables. The LEFT JOIN pattern for master data lookups is universally applicable when master data lags behind operational data.

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

- **WHAT** was done today — 34 database corrections applied across daily_eod_log, ph_master, config_metric_values and config_departments; two HR documents produced; one team-leader upload guide produced
- **WHAT** changed in the data — 1,782 → 2,560 rows; 16 → 36 staff; 0 unmatched ph_ids; 0 duplicate ph_ids; 0 duplicate task rows; all 9 departments registered in config
- **WHAT** is still broken — Sukirtha 0% verification (HR action); new team metric_delta all null (director metric values needed); all bands non-standard (director band mapping needed); salary/status fields empty
- **WHO** still needs action — HR (Sukirtha 1:1, salary data, status); Director/System Owner (metric GBP values, band A–G mapping); Staff (fill metric_delta, hours, proof URLs)
- **WHY** the decisions were made — Option B for department matching; confirmed TECH=GTM and ADS=Google Ads before renaming; all corrections verified by row count; no salary/metric values written without business input
- **WHERE** everything lives — PostgreSQL ROI at vintageinterior.co.uk, MCP at eod-mcp.vintageinterior.co.uk/sse
- **WHAT** to do next — run five-query health check after next upload; chase HR for Sukirtha action; chase Director for metric base_values and band mapping; distribute upload guide to team leaders

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-06-09__abiraj__eod__REQ-03-D04.md`
- [x] Metadata complete — includes `blos_keys_used` and `hardcoded_thresholds`
- [x] Live data snapshot included in Section 3 with D03 vs D04 comparison
- [x] Section names 3–7 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written
- [x] All numbers pulled live from MCP at time of writing
- [x] Evidence locations referenced (PostgreSQL ROI · vintageinterior.co.uk)
- [x] ✅ **RESOLVED (from D03):** ph_id collision DMK004 — Thasitha corrected to DMG004
- [x] ✅ **RESOLVED (from D03):** ADS merged into Google Ads
- [x] ✅ **RESOLVED (from D03):** PH061 phantom ID — Dilaksi corrected to DMKS02
- [x] ✅ **RESOLVED (from D03):** GBB currency typo — corrected to GBP (6 rows)
- [x] ✅ **RESOLVED (from D03):** 3 new starters missing from ph_master — 5 staff added total
- [x] ✅ **NEW RESOLVED:** Kamsi duplicate CSV upload (22 rows deleted)
- [x] ✅ **NEW RESOLVED:** TECH/ADS department synonyms corrected
- [x] ✅ **NEW RESOLVED:** ph_master data quality (duplicates, spaces, tabs, typos, name errors)
- [x] ✅ **NEW RESOLVED:** All 9 departments registered in config_departments
- [ ] ⚠️ **OPEN:** Sukirtha 0% verification — HR 1:1 required
- [ ] ⚠️ **OPEN:** Dilaksi 17.1% verification — HR coaching required
- [ ] ⚠️ **OPEN:** Add GBP base_values for Operational, Sales, ORGANIC_SESSIONS and 7 other missing metrics (Director decision)
- [ ] ⚠️ **OPEN:** Standardise ph_master.band to A–G (Director + HR decision)
- [ ] ⚠️ **OPEN:** Populate monthly_salary_lkr and expected_status for all 40 staff (HR)
- [ ] ⚠️ **OPEN:** Fill unit_description and direction for CTR, Impressions, LISTING_PERFORMANCE, Rank, RETURN_RATE (Director)
- [ ] ⚠️ **OPEN:** Distribute team leader upload guide and collect acknowledgement signatures
- [ ] ⚠️ **OPEN:** Add UNIQUE constraint on ph_master.ph_id at database level (IT Admin / Dev)
- [ ] ⚠️ **OPEN:** Add pre-upload ph_id collision check and department synonym warning to tally.md

---
*DIGITWEB LK LTD — Daily Skill Increment System — v3.0 — June 2026*
