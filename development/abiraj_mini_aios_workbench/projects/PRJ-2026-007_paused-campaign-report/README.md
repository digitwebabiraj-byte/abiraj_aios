# PRJ-2026-007 — Paused Campaign Report (Utharsika)

One-screen landing page. Canonical context is `PROJECT_HOME.md`; full functional detail is
`SYSTEM_REFERENCE.md`.

**What:** a **read-only PPC report** listing Utharsika's Amazon ad targets that **automation paused
and that are still paused today** — seven columns: Campaign Name · Ad Group Name · ASIN · SKU ·
Pause Reason · Campaign Pause Date · Days Paused.
**Task:** REQ-09_paused-campaign-report (`PH-2026-07-UTHAR10`, req `REQ-09-D01`). **Dev:** Abiraj.

## Run 2026-07-13
- **33** paused ad targets · **32** distinct ASINs (B0DXQ84YT7 appears under two ad groups).
- **41** total automation pauses → **33** still paused · **8** re-activated (excluded).
- Two pause waves: **2026-06-10** (18 targets, 33 days paused) · **2026-06-17** (15 targets, 26 days).
- Validation: **4/4 checks PASS** — GREEN (technical). Business sign-off (Satheesvaran) pending on items A–E.

## Key files
| File | What |
|---|---|
| `PROJECT_HOME.md` | Governance: purpose, scope, reviewers, status |
| `SYSTEM_REFERENCE.md` | Locked rules, data model, logic, columns |
| `TASK_REGISTER.md` | Tasks in this project |
| `sql/REQ-09_.../generate_report.sql` | Canonical read-only report query |
| `sql/REQ-09_.../validation_checks.sql` | The count / still-paused validation queries |
| `evidence/final_outputs/REQ-09_.../Utharsika_Paused_Campaigns_Report.html` | **Published dashboard (key deliverable)** — hand-finished |
| `evidence/final_outputs/REQ-09_.../Paused_Campaign_Report_Utharsika.xlsx` | Template-matching spreadsheet |
| `evidence/final_outputs/REQ-09_.../data.json` | Governed 33-row pull + metadata (system of record) |
| `evidence/final_outputs/REQ-09_.../build_html.py` | Secondary/audit re-render of data.json (NOT the published artifact) |
| `evidence/final_outputs/REQ-09_.../PAUSED_CAMPAIGN_VERIFICATION_PACK.md` | Independent 4-check pack |
| `validation/REQ-09_.../2026-07-13_validation.md` | Live reconciliation evidence |
| `closure/REQ-09_.../2026-07-13_closure.md` | Closure record |

## Regenerate
`generate_report.sql` → run via Postgres MCP (`json_agg` form) → `data.json` →
`python build_report.py` (xlsx) → re-run the 4 validation checks (require 4/4). The **published**
dashboard `Utharsika_Paused_Campaigns_Report.html` is hand-finished; refresh its embedded
`<script id="payload">` block from the new `data.json`. `build_html.py` re-renders a plain audit
data view only (not the published file).

## Rules
Read-only DB. No writes/DDL. No invented data. Pause reason is stored **verbatim** in `data.json` +
the xlsx (system of record); the published dashboard shows a **cleaned presentation** of the same
reason (drops the `Date Range …` prefix, `≥`→`>=`, adds structured chips). Do not commit/push without
instruction. Unclear business rules (A–E) go to Satheesvaran — do not decide silently. See root
`CLAUDE.md` + this project's `CLAUDE.md`.
