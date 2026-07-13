# SOURCE_MANIFEST — REQ-09_paused-campaign-report

Provenance of the source documents for the Paused Campaign report. COPY-only import from the
user's `C:\Users\digit\Downloads\`; the Downloads originals are preserved unchanged.

| Registered file | md5 | Origin (Downloads) | Role |
|---|---|---|---|
| `CLAUDE_CODE_HANDOFF_Paused_Campaign.md` | `e74b33bbf418a4caaff0a775322e8599` | `CLAUDE_CODE_HANDOFF_Paused_Campaign.md` | Task brief + validated SQL + business rules + open items A–E |
| `Utharsika_task.xlsx` | `00aa8ef57d2639ad9e7644e7c85e9131` | `Utharsika task (2).xlsx` | Original requirement — column shape, "Days paused" rule, "consult Satheesvaran" instruction |

## Requirement identity
- **Project code:** PH-2026-07-UTHAR10 (workbook sheet `PH-2026-07-UTHAR10 - Abiraj - 1`).
- **Requirement / deliverable:** REQ-09-D01.
- **Columns (7):** Campaign Name · Ad Group Name · ASIN · SKU · Pause Reason · Campaign Pause Date · Days Paused.
- **Sample rows (illustrative only, NOT the answer):** B0DH182H6J / B0CVKSQN9K, pause date 2026-07-06,
  Days Paused 0.
- **Stated rule:** "Days paused = how many days past after pausing"; unclear logic → consult Satheesvaran.

## Referenced-but-not-imported
The handoff (section 2) also lists reference files not needed to run the report and not part of the
requirement, so they were **not** imported:
- `TABLE_ppc.md`, `SKILL_single_table.md`, `SKILL_multi_table.md`, `SKILL_ppc_stock_lookup.md` — these
  live in this machine's `postgres-warehouse-sql` Claude skill
  (`C:\Users\digit\.claude\skills\postgres-warehouse-sql\references\`), the canonical location; the
  build read `TABLE_ppc.md` from there rather than duplicating it here.
- `2026-07-13_abiraj_REQ-pc_REQ-09-D01.md` and `Paused_Campaign_Report_Utharsika_2026-07-13.xlsx` —
  the planner's own prior planning record + output, not present in this Downloads set. Our regenerated,
  live-verified deliverables are the canonical outputs under `evidence/final_outputs/REQ-09_.../`.

## Rule
These are read-only source artefacts. The canonical, verified outputs are the ones this project
generated and validated against the live DB — see `evidence/final_outputs/REQ-09_paused-campaign-report/`.
