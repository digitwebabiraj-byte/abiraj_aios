# CLAUDE.md — PRJ-2026-004_smaw-table5-stock-check

Inherits all rules from the workbench root `CLAUDE.md` and `START_HERE.md`
(`development/abiraj_mini_aios_workbench/`). Project-specific rules below.

## Scope

- Write only inside `projects/PRJ-2026-004_smaw-table5-stock-check/`.
- The production DB `order_management_copy` (via the "Postgresql" MCP) is a **read-only evidence
  source** — never `INSERT`/`UPDATE`/`DELETE`, never DDL against `public`/`supplier`/`staging_ai`
  live tables. The only approved DB write is the single reporting view `v_table5_weekly_stock_check`
  in an approved reporting schema (`sandbox`/`staging_ai`).
- The Downloads artifacts (`C:\Users\digit\Downloads\HANDOFF.md`, `generate_dataset.sql`,
  `dataset.py`, `build_report.py`, `build_html.py`, the HTML) are the user's originals — read-only;
  the registered copies live in this project's `evidence/` and `sql/`.

## Task ID Rule

- Active task: `REQ-06_table5-weekly-stock-check` (deliverables **REQ-06-D01**, **REQ-06-D02**).
- Name Task IDs after the deliverable, not process words (see workbench feedback on Task-ID naming).
- Do not mint new REQ numbers; a new requirement needs the owner's confirmation first.

## Evidence Rule

- Every column / figure must map to a real `schema.table.column` or an explicit "derived from X"
  formula, graded **VERIFIED / PARTIAL / UNPROVEN**.
- No confirmed source = the field goes to Known Limits, never stated as fact.
- Locked data rules (verified against live DB) are in `SYSTEM_REFERENCE.md` and `HANDOFF.md` —
  do not silently change them (UK stock = `location_wise_inv_stock`, NOT `inv_final_stock`; PH
  filter = `order_transaction.user_name='thuwaraga'`; etc.).

## Duplicate-Truth Rule

- `tech_team_outputs.ph_task` already holds `PSLD_thuwaraga_stock_Dashboard-V1` (project PSLD —
  "Portfolio Stock Level Dashboard"). This Table 5 render serves a **distinct weekly-stock-check
  purpose** — complement / align, never silently duplicate or replace it.
- Scan existing stock objects before creating any new DB view (per D01 duplicate-risk scan).

## Stop Conditions (in addition to workbench rules)

- Stop if asked to correct a `LEGACY?` row by inventing a SKU→SKU mapping not present in the DB.
- Stop if asked to expand to full-portfolio coverage without an authoritative PH→ASIN ownership
  source and a live re-pull.
- Stop if a rendered figure diverges from the governed data or the live-UI spot-checks without
  explanation.
- Stop if any write would land outside this project folder or the one approved reporting view.
