# CLAUDE.md — PRJ-2026-007_paused-campaign-report

Inherits all rules from the workbench root `CLAUDE.md` and `START_HERE.md`
(`development/abiraj_mini_aios_workbench/`). Project-specific rules below.

## Scope
- Write only inside `projects/PRJ-2026-007_paused-campaign-report/`.
- Production DB `order_management_copy` (via Postgres MCP) is a **read-only evidence source** —
  never `INSERT`/`UPDATE`/`DELETE`, never DDL. This report needs **no DB object** (per-run extract,
  not a view); do not create one without the owner's written approval.
- Downloads artifacts (`CLAUDE_CODE_HANDOFF_Paused_Campaign.md`, `Utharsika task (2).xlsx`, the prior
  xlsx/dashboard) are the user's originals — read-only; the registered copies live in this project's
  `evidence/source_documents/`.

## Task ID Rule
- Active task: `REQ-09_paused-campaign-report` (deliverable **D01**). `REQ-09` is the source's real
  requirement id (`Utharsika_task.xlsx` → `REQ-09-D01`, project_code `PH-2026-07-UTHAR10`).
- A new day or session does NOT mint a new Task ID — keep using `REQ-09_…` until D01 is closed.
- A genuinely new requirement (e.g. scheduling) gets a new deliverable id (`REQ-09-D02`) after owner
  confirmation — do not invent one silently.

## Locked-rule Rule (do not change without owner sign-off — see SYSTEM_REFERENCE.md)
- Scope key = campaign `record_name ILIKE '%utharsika%'` (there is **no owner column**).
- Platform = Amazon (`source=1`); **SB excluded** (single-ASIN mapping is unrepresentative).
- Pause source = `ppc_etl_automation_log`, `action_type='ad_pause_logs'`, `status='success'`,
  `applied_by='0'` (automation only); **latest pause per ad target** via `DISTINCT ON (record_id, source)`.
- **Still-paused only** = current `ppc.record_status='paused'` at ad grain (`child_id=record_id`).
- **Pause Reason is verbatim in the data layer** (`data.json` + the `.xlsx`, system of record) —
  never paraphrase, drop figures, or map it to only the workbook's "Rule 2" there. The **published
  dashboard** may show a cleaned presentation of the same reason (drop the `Date Range …` prefix,
  `≥`→`>=`, structured chips) — an approved presentation decision (SYSTEM_REFERENCE.md §7); it must
  not alter any number and the verbatim string must remain recoverable from `data.json`.
- **Days Paused** = `CURRENT_DATE − pause_date` (`pause_date = action_datetime::date`).

## Data-Quality / Flag Rule
- The workbook's two sample rows (B0DH182H6J / B0CVKSQN9K, 2026-07-06, Days Paused 0) are
  **illustrative only** — never reproduce them as the answer.
- Report the reconciliation counts every run (targets / distinct ASINs / total pauses / re-activated);
  a divergence from the rendered outputs is a stop condition.
- Keep re-activated pauses **out** of the report but **visible** in the still-paused-vs-all-pauses
  check — that difference (33 vs 41) is the audit trail, not noise.

## Stop Conditions (in addition to workbench rules)
- Stop if asked to paraphrase / bucket the `reason` text **in the data layer** (`data.json`/xlsx) —
  it stays verbatim there. (The published dashboard's cleaned presentation is already approved.)
- Stop if asked to include re-activated ads, manual pauses, or SB campaigns without owner sign-off
  (these are open items C / E / D).
- Stop if asked to hard-code Days Paused or the run date instead of computing from `CURRENT_DATE`.
- Stop if a rendered figure diverges from the governed pull / DB without explanation.
- Stop if any write would land outside this project folder, or if any DB write (view/DDL/DML) is
  requested.
- Stop and route items A–E to **Satheesvaran** rather than deciding any of them.
