# EOD-Skills — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques extracted from this project's skill file and work summaries.
> **Source:** `sql/REQ-03_eod-skills/sql_generate_skill.md` and
> `handover/REQ-03_eod-skills/2026-06-0*__abiraj__eod__REQ-03-D0*.md`.

## 1. Map registry relationships before querying
Before building queries against a registry of config tables, document **exactly which JOINs are
reliable**: which are 100% (`config_task_tiers`), which must be LEFT JOIN (some keys unmatched),
and which **silently drop all rows** and must never be joined (`config_departments` = zero match).
A relationship map prevents queries that quietly return wrong/empty results.

## 2. Always report coverage when a JOIN is partial
If a config join only values part of the data (here only ~22% of rows have a valid GBP
`base_value`), **label the result "partial" and report the coverage %**. Never present a partial
aggregate as if it covered everything.

## 3. Step-0 "live facts" before answering
Never hardcode totals, date ranges or counts. Run a live facts query first (total rows, min/max
date, distinct entities, flag counts) and use that as the source of truth — the dataset grows
with every upload.

## 4. Type-aware, hygiene-safe predicates
- Bigint flags (`verified`, `waste_flag`) compare with `= 1`, **not** boolean `TRUE`.
- Text with trailing spaces (`'SEO '`, `'Google Ads '`) — always `TRIM()` before grouping.
- Every division wrapped in `NULLIF(denominator, 0)`.
- Nullable numerics `COALESCE(x, 0)` before SUM.

## 5. Avoid silent row fan-out
When a registry key has duplicate entries (here `ROAS` exists in two currencies), **filter to the
valid one in the JOIN** (`AND currency = 'GBP'`) or the result double-counts.

## 6. Fetch the question/definition live
Hold the question set in a table (`predefined_question`) and read it at runtime, so business
users (HR) can edit/add/deactivate questions with **no code change** to the skill.

## 7. Separate read from write
The query skill **never inserts** — data entry is a separate skill (`eod-csv-upload`). Keeping
read and write as distinct, single-responsibility skills prevents accidental writes during analysis.

## 8. Fix the source, not just the symptom (upload SOP)
Data-quality problems were also addressed at the source with a team-leader upload guide
(canonical department names, tier guide, 10-point checklist) — stopping bad data at entry rather
than only cleaning it downstream.
