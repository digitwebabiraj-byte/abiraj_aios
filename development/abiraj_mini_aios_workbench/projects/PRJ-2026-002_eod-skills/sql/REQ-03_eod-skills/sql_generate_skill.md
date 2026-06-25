---
name: eod-query-answerer
description: >
  Use this skill whenever a user asks any performance, yield, staff, waste,
  productivity, or task-related question about EOD data — whether it matches a
  predefined question or is a free-form HR/management query. Triggers include:
  "who is underperforming", "show me yield", "which staff", "which department",
  "waste hours", "top performers", "task tier breakdown", "ROAS", "CTR", or any
  analytical question about daily_eod_log data. This skill NEVER inserts data —
  that belongs to eod-csv-upload. It runs alongside the upload workflow without conflict.
---

# EOD Query Answerer Skill

## Overview

This skill answers HR/management questions about EOD performance data.
It always fetches the live question from `predefined_question` first.
If `sql_query` is filled, it executes directly. If empty, it builds SQL
dynamically using the instructions below. All values come from registry
JOINs — never hardcoded.

---

## Step 0 — Always Run This First (Live DB Facts)

Before answering any question, run this query to get current data facts.
Never rely on hardcoded numbers — the DB grows with every upload.

```sql
SELECT
  COUNT(*) AS total_rows,
  MIN(date)::date AS min_date,
  MAX(date)::date AS max_date,
  COUNT(DISTINCT ph_id) AS distinct_ph_ids,
  COUNT(DISTINCT ph_name) AS distinct_ph_names,
  COUNT(CASE WHEN verified = 1 THEN 1 END) AS verified_count,
  COUNT(CASE WHEN waste_flag = 1 THEN 1 END) AS waste_count,
  COUNT(CASE WHEN metric_delta IS NULL THEN 1 END) AS null_delta_count
FROM daily_eod_log;
```

Use these live results as source of truth for any question about totals,
date ranges, or staff counts. Never use a hardcoded number from this file
for these values.

---

## Verified Table Relationships (Confirmed From Live DB)

This section describes EXACTLY what connects to what in the real database.
Read this before building any query.

---

### Relationship 1: daily_eod_log → ph_master
- JOIN key: `daily_eod_log.ph_id = ph_master.ph_id`
- Some ph_ids in daily_eod_log have NO ph_master record — always use LEFT JOIN
- Known unmatched: `PH061` (Dilaksi) and `DMT001` (Piranav) — check live with:
  ```sql
  SELECT DISTINCT l.ph_id, l.ph_name FROM daily_eod_log l
  LEFT JOIN ph_master p ON l.ph_id = p.ph_id WHERE p.ph_id IS NULL;
  ```
- Use: `LEFT JOIN ph_master p ON l.ph_id = p.ph_id` to keep all staff
- Note: `ph_master.department` values (`Website`, `PH`) are DIFFERENT from
  `daily_eod_log.department` values (`Google Ads `, `SEO`, etc.) — do NOT join on department

---

### Relationship 2: daily_eod_log → config_task_tiers
- JOIN key: `daily_eod_log.task_tier = config_task_tiers.task_tier`
- All rows match — 100% reliable
- Valid task_tier values: A, B, C, D, S — all exist in config
- Use freely: `JOIN config_task_tiers ct ON l.task_tier = ct.task_tier`

---

### Relationship 3: ph_master → config_yield_anchors
- JOIN key: `ph_master.band = config_yield_anchors.band`
- ph_master.band values: `A`(2 staff), `Junior`(3), `Senior`(7), `Probationer`(1)
- config_yield_anchors.band values: A, B, C, D, E, F, G — all GBP only
- ONLY band=A staff match — all others get NULL anchor
- Use: `LEFT JOIN config_yield_anchors a ON p.band = a.band`
- Always state in output: most staff have no anchor match

---

### Relationship 4: daily_eod_log → config_metric_values
- JOIN key: `daily_eod_log.metric_name = config_metric_values.metric_name`
- IMPORTANT: ROAS has 2 entries (GBP and GBB) — a plain JOIN will fan-out rows
  always use: `LEFT JOIN config_metric_values mv ON l.metric_name = mv.metric_name AND mv.currency = 'GBP'`
  to get only valid GBP entries and avoid duplicate rows
- Metrics with valid GBP base_value: ACOS_REDUCTION(65), CVR(100), ROAS(100), SALES_UPLIFT(10), Margin(210), Revenue(1)
  — covers only ~22% of rows
- Metrics with typo currency GBB (unusable): CTR, ROAS(duplicate), Impressions, LISTING_PERFORMANCE, Rank, RETURN_RATE
- Metrics with NO entry at all: ORGANIC_SESSIONS, LISTING_QUALITY, PROCESS_QUALITY, HOURS_SAVED, IMPRESSION_SHARE, PAGE_SPEED, SERP_RANK, TRACKING_ACCURACY, CPA_REDUCTION, NULL
- Always LEFT JOIN — never INNER JOIN on metric values

---

### Relationship 5: ph_master → config_band_limits
- JOIN key: `ph_master.band = config_band_limits.band`
- Same band mismatch as Relationship 3
- ONLY band=A staff match config_band_limits
- Use: `LEFT JOIN config_band_limits cb ON p.band = cb.band`

---

### Relationship 6: daily_eod_log → config_departments
- JOIN key: `daily_eod_log.department = config_departments.department_id`
- config_departments IDs: `Website`, `PH`, `Multi-channel`, `google ads`
- ZERO rows match — these are completely different values from what is in daily_eod_log
- config_departments.primary_currency is NULL for all rows anyway
- NEVER JOIN config_departments — it silently drops all rows

---

### Relationship 7: config_yield_anchors — currency availability
- Only GBP rows exist (7 rows, bands A-G)
- EUR and USD rows are missing
- No multi-currency comparison is possible with current data

---

## Key Column Types (Never Changes)

| Column | Type | Rule |
|---|---|---|
| `verified` | bigint | use `= 1` not `= TRUE` |
| `waste_flag` | bigint | use `= 1` not `= TRUE` |
| `metric_delta` | bigint, nullable | always COALESCE(metric_delta, 0) or handle NULL |
| `hours_spent` | double precision | numeric, safe for SUM/AVG |
| `date` | timestamp without time zone | cast with `::date` when comparing dates |
| `department` | text, has trailing spaces | always TRIM(l.department) in GROUP BY and SELECT |

---

## Key Structural Facts (Stable — Only Changes If Schema Changes)

| Fact | Value |
|---|---|
| department trailing space issue | `SEO ` and `Google Ads ` — always TRIM(l.department) |
| scenario possible values | Normal, Blocked, Leave |
| task_tier possible values | A, B, C, D, S |
| Rows with valid GBP metric base_value | ~22% of total rows |
| Rows with no metric base_value | ~78% of total rows |
| ONLY band=A staff have yield anchor + admin limit data | all other bands (Junior/Senior/Probationer) get NULL |

---

## Step-by-Step Process

### Step 1 — Fetch the Live Question

Always read from the database — HR may change any question at any time.

```sql
SELECT id, title, question_template, sql_query, is_active
FROM predefined_question
WHERE is_active = TRUE
ORDER BY "order";
```

Match the user's input to the closest `question_template` by meaning.

- `sql_query` is filled → skip to Step 3, execute it directly
- `sql_query` is empty or NULL → continue to Step 2

---

### Step 2 — Build SQL Dynamically (For Empty sql_query Questions)

**First — identify the question category:**

| Category | Signals in question | Reliable tables to use |
|---|---|---|
| Task tier / hours split | "tier", "Tier S", "Tier D", "admin", "strategic", "time split", "% of hours" | daily_eod_log + config_task_tiers |
| Top / bottom performers | "top", "best", "worst", "highest", "lowest", "performer" | daily_eod_log only |
| Verification / unverified | "unverified", "no proof", "claimed", "missing URL", "verification rate" | daily_eod_log only |
| Waste analysis | "waste", "rework", "blocked", "killed", "lost hours", "waste type" | daily_eod_log only |
| Admin misallocation | "admin limit", "Tier D limit", "too much admin", "director", "manager" | daily_eod_log + ph_master + config_band_limits (band=A staff only) |
| Partial yield / value | "yield", "value per hour", "metric delta per hour", "ROI" | daily_eod_log + config_task_tiers + LEFT JOIN config_metric_values (GBP only, ~22% coverage) |
| Department comparison | "department", "compare", "Google Ads", "SEO", "Technical" | daily_eod_log — use TRIM(l.department) |
| Trend over time | "trend", "last 4 weeks", "8 weeks", "improving", "declining" | daily_eod_log — group by date_trunc week |
| Metric-specific | "ROAS", "CTR", "CVR", "ACOS", any metric name | daily_eod_log — filter by metric_name |
| Scenario analysis | "forecast", "draft", "actual", "scenario" | daily_eod_log — filter by scenario |
| Strategic ownership | "Tier S", "who owns", "majority", "strategic hours" | daily_eod_log + config_task_tiers |

---

**Second — select the correct JOIN pattern:**

**Pattern 1 — daily_eod_log only (always returns data):**
```sql
FROM daily_eod_log l
-- Use for: waste, verification, raw metric delta ranking, scenario, department split
```

**Pattern 2 — Add task tier registry (100% reliable):**
```sql
FROM daily_eod_log l
JOIN config_task_tiers ct ON l.task_tier = ct.task_tier
-- Use for: tier splits, value multiplier, tier migration, Tier S/D analysis
-- All rows join successfully — no nulls expected
```

**Pattern 3 — Add employee band:**
```sql
FROM daily_eod_log l
LEFT JOIN ph_master p ON l.ph_id = p.ph_id
-- MUST use LEFT JOIN — some ph_ids have no ph_master record (e.g. PH061, DMT001)
-- ph_master.band returns: Senior, Junior, Probationer, A — or NULL for unmatched
-- Always show p.band in SELECT so user can see actual band values
```

**Pattern 4 — Add admin limits:**
```sql
FROM daily_eod_log l
LEFT JOIN ph_master p ON l.ph_id = p.ph_id
LEFT JOIN config_band_limits cb ON p.band = cb.band
JOIN config_task_tiers ct ON l.task_tier = ct.task_tier
-- cb columns will be NULL for all staff except band=A
-- Always note in output: only band-A staff have limit data
```

**Pattern 5 — Add metric value for yield (GBP only, ~22% coverage):**
```sql
FROM daily_eod_log l
JOIN config_task_tiers ct ON l.task_tier = ct.task_tier
LEFT JOIN config_metric_values mv ON l.metric_name = mv.metric_name AND mv.currency = 'GBP'
-- MUST add AND mv.currency = 'GBP' to prevent ROAS fan-out (ROAS has 2 entries)
-- mv.base_value will be NULL for ~78% of rows — always use CASE WHEN
-- Always report coverage: "X of total rows could be valued"
```

**NEVER use:**
```sql
-- NEVER: JOIN config_departments  — zero rows match, all primary_currency NULL
-- NEVER: LEFT JOIN config_metric_values mv ON l.metric_name = mv.metric_name
--        without AND mv.currency = 'GBP' — causes fan-out from ROAS duplicate
-- NEVER: JOIN config_yield_anchors directly — most bands don't match
```

---

**Third — apply the correct formula:**

**Hours and tier split:**
```sql
ROUND(SUM(l.hours_spent)::numeric, 2) AS total_hours

-- Admin (Tier D) ratio:
ROUND(
    (SUM(CASE WHEN l.task_tier = 'D' THEN l.hours_spent ELSE 0 END)
    / NULLIF(SUM(l.hours_spent), 0) * 100)::numeric, 1
) AS admin_pct

-- High-value (Tier S + A) ratio:
ROUND(
    (SUM(CASE WHEN l.task_tier IN ('S','A') THEN l.hours_spent ELSE 0 END)
    / NULLIF(SUM(l.hours_spent), 0) * 100)::numeric, 1
) AS high_value_pct
```

**Partial yield — Pattern 5 only (GBP, ~22% coverage):**
```sql
-- Always label result as "partial"
ROUND(
    (SUM(CASE WHEN mv.base_value IS NOT NULL AND l.metric_delta IS NOT NULL
         THEN l.metric_delta * mv.base_value * ct.value_multiplier
         ELSE 0 END)
    / NULLIF(SUM(l.hours_spent), 0))::numeric, 2
) AS partial_yield_per_hour
```

**Raw metric delta (no config join — works for all rows):**
```sql
ROUND(SUM(COALESCE(l.metric_delta, 0))::numeric, 2) AS total_metric_delta
ROUND((SUM(COALESCE(l.metric_delta, 0)) / NULLIF(SUM(l.hours_spent), 0))::numeric, 4) AS delta_per_hour
```

**Verification — bigint, use = 1:**
```sql
COUNT(CASE WHEN l.verified = 1 THEN 1 END) AS verified_tasks
ROUND((COUNT(CASE WHEN l.verified = 1 THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0))::numeric, 1) AS verification_pct
COUNT(CASE WHEN l.verified = 0 AND (l.verification_url IS NULL OR l.verification_url = '') THEN 1 END) AS unverified_no_url
```

**Waste — bigint, use = 1:**
```sql
COUNT(CASE WHEN l.waste_flag = 1 THEN 1 END) AS waste_tasks
ROUND(SUM(CASE WHEN l.waste_flag = 1 THEN l.hours_spent ELSE 0 END)::numeric, 2) AS waste_hours
ROUND((SUM(CASE WHEN l.waste_flag = 1 THEN l.hours_spent ELSE 0 END) / NULLIF(SUM(l.hours_spent), 0) * 100)::numeric, 1) AS waste_pct
```

**Department grouping — always TRIM:**
```sql
TRIM(l.department) AS department
GROUP BY TRIM(l.department)
-- Merges 'SEO' and 'SEO ' into one group
-- Merges 'Google Ads ' into 'Google Ads'
```

**Time windows — choose based on question wording:**
```sql
-- This week:
l.date >= date_trunc('week', CURRENT_DATE)
AND l.date < date_trunc('week', CURRENT_DATE) + INTERVAL '7 days'

-- This month:
l.date >= date_trunc('month', CURRENT_DATE)

-- Last month:
l.date >= date_trunc('month', CURRENT_DATE - INTERVAL '1 month')
AND l.date < date_trunc('month', CURRENT_DATE)

-- Last 4 weeks:
l.date >= CURRENT_DATE - INTERVAL '28 days'

-- Last 8 weeks:
l.date >= CURRENT_DATE - INTERVAL '56 days'

-- All time: no filter
-- IMPORTANT: Always check live max_date from Step 0 before applying time windows
-- If a time-windowed query returns 0 rows:
--   1. Re-run without time filter
--   2. Tell user the actual data range from Step 0 results
```

**Ranking:**
```sql
-- Top N:
ORDER BY <metric> DESC NULLS LAST LIMIT N

-- Bottom quartile:
NTILE(4) OVER (ORDER BY <metric> ASC NULLS LAST) AS quartile
-- wrap in CTE, filter WHERE quartile = 1

-- Weekly trend:
date_trunc('week', l.date)::date AS week_start
GROUP BY date_trunc('week', l.date)
ORDER BY week_start ASC
```

**Always NULLIF for all divisions:**
```sql
/ NULLIF(<denominator>, 0)
```

---

### Step 3 — Execute via MCP

Use **`End_of_the_day_performance_check_Postgress`** MCP `execute_sql`.
Pass only the `sql` parameter — no `project_id` needed.

```
End_of_the_day_performance_check_Postgress -> execute_sql
  sql: <query from Step 1 or Step 2>
```

---

### Step 4 — Validate Before Presenting

```
- 0 rows returned?
  -> Check: does time window fall within actual data range? (get from Step 0)
  -> If not: re-run without time filter, note actual data range to user
  -> Also check: did a JOIN silently drop rows? (config_departments, unmatched bands)

- Used LEFT JOIN config_metric_values with AND mv.currency = 'GBP'?
  -> Count rows where mv.base_value IS NOT NULL vs NULL
  -> Report: "Yield is partial — only ~22% of tasks have a valid GBP base_value"

- ph_master JOIN dropped staff?
  -> Some ph_ids have no ph_master record — always use LEFT JOIN to keep all rows
  -> Most staff have band Junior/Senior/Probationer — no anchor or limit match

- Department totals make sense?
  -> Confirm TRIM(l.department) used — SEO and SEO space must be merged

- Never fabricate numbers — only report what the query returned
```

---

### Step 5 — Present the Answer

```
[Question Title from predefined_question.title]

[2-3 sentence plain-English summary of what the data shows]

Key findings:
  - [Specific finding with actual number from results]
  - [Specific finding with actual number from results]
  - [Additional finding if applicable]

Coverage notes (include only if applicable):
  - [e.g. "Yield is partial — only ~22% of tasks have a metric base_value in the registry"]
  - [e.g. "Band limit comparison covers only band=A staff — ph_master.band not yet standardised to A-G"]
  - [e.g. "No data for this time window — showing all-time instead. Data range: [from Step 0]"]

[One actionable recommendation if data supports it]
```

---

### Step 6 — Handle Question Changes Dynamically

When HR updates a `question_template`:
- Step 1 reads the new text live at runtime
- Re-identify category using the Step 2 table
- Rebuild SQL using the correct pattern and formulas
- No changes to this skill file are needed

When HR adds a new question with empty `sql_query`:
- It appears in Step 1 results automatically
- Apply category identification, pattern selection, formula, execute

When HR deactivates a question (`is_active = FALSE`):
- It will not appear in Step 1 results
- Do not answer unless user asks explicitly by title

---

## Error Handling

| Situation | Action |
|---|---|
| sql_query is empty | Build dynamically using Step 2 |
| 0 rows returned | Check time window vs actual data range from Step 0, then check JOIN drops |
| verified or waste_flag compared as boolean | Always use = 1 or = 0 — they are bigint |
| Division by zero | Always NULLIF(denominator, 0) |
| mv.base_value NULL after LEFT JOIN | Report partial — only ~22% of rows have valid GBP base_value |
| Department duplicates due to spaces | Always TRIM(l.department) |
| config_metric_values fan-out on ROAS | Always add AND mv.currency = 'GBP' to metric join |
| Some ph_ids not in ph_master | Always LEFT JOIN ph_master — check unmatched with live query |
| MCP execute_sql error | Show full error — do not retry silently |

---

## Registry Fix Checklist (Needed for Full Accuracy)

| Fix needed | Impact |
|---|---|
| Standardise ph_master.band to A-G | Unlocks yield anchor + admin limit for all staff |
| Populate config_departments.primary_currency and align department_id to actual names | Unlocks department-level currency queries |
| Add missing metrics to config_metric_values with GBP base_value | Raises yield coverage from ~22% to near 100% |
| Fix GBB typo to GBP for CTR, Impressions, LISTING_PERFORMANCE, Rank, RETURN_RATE | Raises yield coverage and fixes fan-out |
| Remove duplicate ROAS entry (keep GBP only) | Prevents row fan-out in metric JOIN |
| Add EUR and USD rows to config_yield_anchors | Enables multi-currency anchor comparisons |

---

## Notes

- This skill NEVER inserts data — inserts belong to eod-csv-upload
- Always use End_of_the_day_performance_check_Postgress MCP — not the postgres MCP
- config_task_tiers + raw daily_eod_log columns are the only fully reliable foundation
- Q19-Q24 and Q11-Q14 return full results with current data
- Q25-Q44 work partially using Pattern 1 and 2
- Q1-Q10 and Q15-Q18 are blocked by registry gaps — build best-effort and state limitations
