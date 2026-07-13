# Validation — REQ-09_paused-campaign-report (D01)

**Date:** 2026-07-13 · **DB:** `order_management_copy` (read-only, Postgres MCP) · **By:** Abiraj (Claude Code executor)
**Decision:** **GREEN (technical)** — business sign-off (Satheesvaran, items A–E) **PENDING**.

## What was validated
The Paused Campaign report for Utharsika: 33 still-paused Amazon ad targets (32 distinct ASINs),
seven columns, built from the validated handoff SQL and reconciled to the live DB.

## Live checks (queries in `sql/REQ-09_.../validation_checks.sql`)
| # | Check | Expected | DB result | Verdict |
|---|---|---|---|---|
| 1 | Report count (targets / ASINs) | 33 / 32 | `targets 33, asins 32` | ✅ PASS |
| 2 | Still-paused vs all-pauses | 41 / 33 / 8 | `total 41, still_paused 33, reactivated 8` | ✅ PASS |
| 3 | Pause-date waves | 18 @ 33d + 15 @ 26d = 33 | 2026-06-10 ×18, 2026-06-17 ×15 | ✅ PASS |
| 4 | Pause-reason integrity (verbatim, R1/R2/R3) | all verbatim; 3 rule families | R1 9 · R2 22 · R3 3 (1 combined) | ✅ PASS |

## Output reconciliation
- `data.json`: 33 rows, 32 distinct ASINs, metadata block matches the reconciliation figures.
- `Paused_Campaign_Report_Utharsika.xlsx`: `Report` sheet = 33 data rows / 7 columns / 32 distinct
  ASIN cells; `Summary` + `Notes` sheets present and consistent.
- **Published dashboard** `Utharsika_Paused_Campaigns_Report.html` (owner-supplied, hand-finished,
  md5 `6b971cf330e04404417db70ee6d70336`): embedded payload diffed against `data.json` →
  **33/33 row tuples match exactly, 0 differences**; 32 ASINs; rule split R1 9 / R2 22 / R3 2
  (the combined B0DPMQZ1WP classed as Rule 1); waves 18 / 15; still-paused rate 33/41 = 80%. Reason
  shown as a cleaned presentation (verbatim retained in `data.json`/xlsx) — approved, see
  SYSTEM_REFERENCE §7. My earlier auto-built `…_Dashboard.html` was removed to avoid parallel truth;
  `build_html.py` retained as a secondary audit renderer (`…_dataview.html`).
- **V2 redesign (2026-07-13 14:04, published row 215):** dashboard rebuilt as a table-hero, full-width
  layout (rule-coded bands/badges, heat Days Paused, no CDN). **Same 33-row payload reused verbatim**
  from V1 → parity unchanged. Live `tech_team_outputs.ph_task` id 215 verified: `version_level=2`,
  `md5=fbd4b6007110a6b440f0757111de1158`, 34,213 chars — matches the canonical file; identity fields
  (project_code/task_id/assigned_user) unchanged.

## Duplicate-risk
- **GREEN.** New project ID `PRJ-2026-007` (next sequential) and new task `REQ-09_paused-campaign-report`
  (source's real `REQ-09-D01`). No existing PPC/paused-campaign asset in the workbench — this is the
  first. No canonical asset overwritten; source docs imported COPY-only (originals preserved).

## Evidence
- SQL: `sql/REQ-09_.../generate_report.sql`, `validation_checks.sql`.
- Data + outputs + pack: `evidence/final_outputs/REQ-09_.../` (`data.json`, `.xlsx`, dashboard,
  `PAUSED_CAMPAIGN_VERIFICATION_PACK.md`).
- Source provenance: `evidence/source_documents/REQ-09_.../SOURCE_MANIFEST.md`.

## Open items (Satheesvaran — do NOT decide)
A. scope key · B. grain (per-ASIN vs per-campaign) · C. included set (33 vs 41) · D. platform ·
E. manual pauses. B and C change the row count.

## Result
**GREEN (technical).** Query correct, counts reconciled 4/4, outputs consistent, no DB writes, nothing
committed/pushed. **Business validation by Satheesvaran on A–E is the remaining gate.**
