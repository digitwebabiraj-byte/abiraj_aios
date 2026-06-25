# EOD-Skills — Complete System Reference

> **What this file is:** a plain-language, complete description of what the EOD (End-of-Day)
> performance-analytics system does — the data model, the query skill, the metrics, the question
> bank, the deliverables and the data-integrity work. It is a **derived reference** synthesised
> from the canonical sources; it does not replace them. Sources:
> - Query skill (authoritative logic): `sql/REQ-03_eod-skills/sql_generate_skill.md`
> - Skill manual: `evidence/final_outputs/REQ-03_eod-skills/2026-06-05_EOD_QueryAnswerer_Skill_Abiraj.docx`
> - HR/IT deliverables: `evidence/final_outputs/REQ-03_eod-skills/` (accountability, problems register, issues-fix, upload guide)
> - Build/decisions: `handover/REQ-03_eod-skills/2026-06-0*__abiraj__eod__REQ-03-D0*.md` (D01–D04)
> - QA reviews: `validation/REQ-03_eod-skills/*_validation.md`
> Where the documents disagree on numbers, the disagreement is preserved and flagged in §11 (not "corrected").

---

## 1. What the system does (in one paragraph)

The EOD system turns each staff member's **end-of-day task log** into answerable performance
intelligence for HR and management. Its core is a Claude skill — **`eod-query-answerer`** — that
takes a free-form or predefined HR question ("who is underperforming", "show me yield", "waste
hours", "top performers", "task-tier breakdown") and returns a correct, **live** SQL-backed answer
from the Postgres `daily_eod_log` table — **never hardcoded** (it re-reads the live DB on every
question). Around that skill sit a set of **HR/IT reports** (staff accountability, a problems
register, an issues-fix report) and a **team-leader upload guide**, plus a **data-integrity
clean-up** that made the answers trustworthy.

- **Owner / developer:** Abiraj. **Requirement:** REQ-03 (deliverables D01–D04, 3–9 June 2026).
- **Audience:** HR and management (leaders). **Database:** the Postgres "ROI database".
- **MCP connection:** `End_of_the_day_performance_check_Postgress` (`execute_sql`).
- **Two complementary skills:** `eod-query-answerer` (reads/answers — this project) and `eod-csv-upload` (inserts the daily data — separate). The query skill **never inserts**.

## 2. The data model — `daily_eod_log` (the central table)

One row = one task a staff member logged at end of day. Key columns:

| Column | Type | Meaning / rule |
|---|---|---|
| `ph_id`, `ph_name` | text | Staff identifier and name |
| `department` | text (**has trailing spaces**) | e.g. `SEO `, `Google Ads ` — always `TRIM()` |
| `task_tier` | text | One of **S, A, B, C, D** (S/A = high-value/strategic, D = admin) |
| `metric_name` | text | The KPI worked on (ROAS, CVR, CTR, Margin, Revenue, …) |
| `metric_delta` | bigint, nullable | The measured change in that metric — `COALESCE(...,0)` |
| `hours_spent` | double precision | Time on the task — safe for SUM/AVG |
| `verified` | bigint (0/1) | Was the work verified — compare `= 1`, not `TRUE` |
| `waste_flag` | bigint (0/1) | Was it waste/rework — compare `= 1` |
| `verification_url` | text | Proof link (blank/NULL = unverifiable) |
| `date` | timestamp | Cast `::date` for comparisons |
| `scenario` | text | `Normal`, `Blocked`, `Leave` |

## 3. The registry / config tables and how they connect

The skill JOINs `daily_eod_log` to config tables — but only some are reliable. This map is the heart of the system:

| # | Relationship | Join key | Reliability |
|---|---|---|---|
| 1 | `daily_eod_log` → `ph_master` | `ph_id` | **LEFT JOIN** — some staff (e.g. `PH061`, `DMT001`) have no master record |
| 2 | `daily_eod_log` → `config_task_tiers` | `task_tier` | **100% reliable** — the only fully-trusted JOIN |
| 3 | `ph_master` → `config_yield_anchors` | `band` | Only `band=A` matches (others NULL) |
| 4 | `daily_eod_log` → `config_metric_values` | `metric_name` **+ `currency='GBP'`** | **LEFT JOIN**; ROAS has a duplicate → must filter GBP to avoid row fan-out |
| 5 | `ph_master` → `config_band_limits` | `band` | Only `band=A` matches |
| 6 | `daily_eod_log` → `config_departments` | `department` | **NEVER JOIN** — zero rows match; silently drops everything |
| 7 | `config_yield_anchors` currency | — | GBP only (no EUR/USD) → no multi-currency |

**Golden foundation:** `daily_eod_log` raw columns + `config_task_tiers` are the only always-reliable base. Everything else is LEFT-JOINed and may be NULL.

## 4. How the skill answers a question (the process)

1. **Step 0 — live facts first.** Always run a live count (total rows, date range, distinct staff, verified/waste counts) so no number is ever hardcoded — the DB grows with each upload.
2. **Step 1 — fetch the live question** from `predefined_question` (`is_active = TRUE`). If its `sql_query` is filled, run it directly; if empty, build SQL dynamically.
3. **Step 2 — categorize + pick a JOIN pattern + formula** (see §5/§6). Match the user's wording to the closest question by meaning.
4. **Step 3 — execute** via the `End_of_the_day_performance_check_Postgress` MCP `execute_sql`.
5. **Step 4 — validate** (0 rows? check time window vs real data range and silent JOIN drops; report partial coverage).
6. **Step 5 — present**: title, 2–3 sentence summary, key findings with **actual numbers**, coverage caveats, one recommendation.
7. **Step 6 — adapt**: if HR edits/adds/deactivates a question, the skill picks it up live — no skill-file change needed.

The skill **never fabricates numbers** — it reports only what the query returned.

## 5. Question categories → reliable tables (the routing table)

| Category | Trigger words | Tables to use |
|---|---|---|
| Task-tier / hours split | "tier", "admin", "% of hours" | `daily_eod_log` + `config_task_tiers` |
| Top / bottom performers | "top", "worst", "performer" | `daily_eod_log` only |
| Verification / unverified | "unverified", "no proof", "verification rate" | `daily_eod_log` only |
| Waste analysis | "waste", "rework", "blocked", "lost hours" | `daily_eod_log` only |
| Admin misallocation | "admin limit", "Tier D limit", "director" | + `ph_master` + `config_band_limits` (band=A only) |
| Partial yield / value | "yield", "value per hour", "ROI" | + `config_task_tiers` + `config_metric_values` (GBP, ~22%) |
| Department comparison | "department", "Google Ads", "SEO" | `daily_eod_log` — `TRIM(department)` |
| Trend over time | "trend", "last 4 weeks", "improving" | `daily_eod_log` — group by week |
| Metric-specific | "ROAS", "CTR", "CVR", "ACOS" | `daily_eod_log` — filter `metric_name` |
| Scenario / Strategic | "forecast", "Tier S", "who owns" | `daily_eod_log` (+ `config_task_tiers`) |

## 6. The core formulas

- **Hours / tier split:** total hours = `SUM(hours_spent)`; admin % = Tier-D hours ÷ total × 100; high-value % = Tier (S+A) hours ÷ total × 100.
- **Verification rate:** `COUNT(verified=1) × 100 / COUNT(*)`; unverified-no-URL = `verified=0 AND verification_url IS NULL/''`.
- **Waste:** waste tasks = `COUNT(waste_flag=1)`; waste hours/% from those rows.
- **Partial yield/hour (GBP, ~22% coverage):** `SUM(metric_delta × base_value × value_multiplier) ÷ SUM(hours_spent)` — always labelled "partial".
- **Raw metric delta (all rows):** `SUM(COALESCE(metric_delta,0))` and `… ÷ NULLIF(SUM(hours_spent),0)`.
- **Always:** `TRIM(department)` in grouping; `NULLIF(denominator,0)` on every division; `verified/waste_flag = 1` (they're bigint, not boolean).

**Coverage reality:** only ~**22%** of rows have a valid GBP `base_value` (metrics `ACOS_REDUCTION, CVR, ROAS, SALES_UPLIFT, Margin, Revenue`); ~78% cannot be valued in money — so yield is always reported as *partial*.

## 7. The predefined question bank (~50 HR/management questions)

Questions live in `predefined_question` (HR can edit them live). Current answerability against the data:

| Questions | Status |
|---|---|
| Q11–Q14, Q19–Q24 | **Full** results with current data |
| Q25–Q44 | **Partial** (using `daily_eod_log` + `config_task_tiers`) |
| Q1–Q10, Q15–Q18 | **Blocked** by registry gaps — answered best-effort with stated limitations |

## 8. The deliverables (5 documents)

| File | What it is | Audience |
|---|---|---|
| `2026-06-05_EOD_QueryAnswerer_Skill_Abiraj.docx` | Full technical reference for the skill (relationships, patterns, formulas, golden rules) | developers / owner |
| `2026-06-08__HR_Staff_Accountability_Report.docx` | Accountability review (e.g. 16 staff / 1,782 tasks; 0%-verification escalation; 12-item action table) — HR-CONFIDENTIAL | HR + managers |
| `2026-06-09_EOD_Complete_Problems_Register.docx` | Master register of all data/structure problems (57) with severity/owner/fix | System Owner / IT / HR |
| `2026-06-09_EOD_Issues_Fix_Report_J_Abiraj.docx` | What was fixed vs pending (57 found / 34 fixed / 23 pending) + per-staff verification table — HR-CONFIDENTIAL | HR |
| `2026-06-09_EOD_Upload_Guide_Team_Leaders.docx` | CSV upload SOP: every column, tier guide, 10-point checklist, 9 canonical department names | team leaders |

## 9. Data-integrity remediation (what made the answers trustworthy)

The June work loaded May data and fixed the registry so queries return correct results:
- Row growth tracked across uploads; resolved a **DMK004 ID collision** and an **ADS vs "Google Ads" synonym**.
- **34 database corrections** applied via MCP; `ph_master` expanded so **all active `ph_ids` matched (0 unmatched)**; all departments registered.
- **Verification rate trend** improved across the period (~53% → ~74% → ~82%).

*(These DB writes were performed during the original June work — they are not re-executed or re-verified inside this onboarding.)*

## 10. Known registry gaps (limit full accuracy) — the fix checklist

| Fix needed | Impact |
|---|---|
| Standardise `ph_master.band` to A–G | Unlocks yield anchor + admin limits for **all** staff (today only band=A) |
| Align `config_departments` IDs to real names + populate currency | Enables department-currency queries (today zero match) |
| Add missing metrics to `config_metric_values` (GBP base_value) | Raises yield coverage from ~22% toward ~100% |
| Fix the `GBB` typo → `GBP` (CTR, Impressions, Rank, RETURN_RATE, LISTING_PERFORMANCE) | More valuable rows; fixes fan-out |
| Remove the duplicate `ROAS` entry (keep GBP) | Prevents row fan-out |
| Add EUR/USD rows to `config_yield_anchors` | Enables multi-currency comparison |

## 11. Accuracy / reconciliation notes (preserved, not "fixed")

- **Numeric drift across the deliverables** (preserved as-is, flagged for business review): row counts appear as 1,782 / 2,560 / 2,582 in different documents; staff counts as 16 / 35 / 40; "fixed" counts as 4 (Problems Register, 8 Jun) vs 34 (Issues-Fix Report, 8–9 Jun, reflecting the D03→D04 transition). The Problems Register's own header (50 found / 4 fixed / 46) also disagrees with its body (57). These are **content discrepancies inside the original deliverables** — not changed here.
- **Self-checks were historically unreliable** — early daily files marked "metadata complete: YES" when it wasn't; the external QA validation reports (scores 60 → 58 → 78 → 91 across D01→D04) are the more reliable signal.
- **DB corrections are claimed but unverifiable from this folder** (no DB access, no commit hashes).

## 12. What the system does NOT do

- The query skill **never inserts data** (that's `eod-csv-upload`).
- It does **not** value ~78% of rows in money (no registry base_value) — yield is partial.
- It does **not** join `config_departments` (zero match) or assume non-band-A staff have anchors/limits.
- It does **not** invent numbers — only reports live query results.

## 13. Status & provenance

Built by Abiraj under requirement **REQ-03**; preserved in this project
(`PRJ-2026-002_eod-skills`, task `REQ-03_eod-skills`); imported with all 14 source files
checksum-verified. Owner-required reviews complete: **Business (HR) PASS** and **Queryability
(Tamil Selvan) PASS**; technical review (Sajeesan) not required for onboarding but **would be
required before any live execution** of the skill/SQL. Task **CLOSED**, project **ACTIVE**.
The skill/SQL is **stored, not executed** in the workbench.
