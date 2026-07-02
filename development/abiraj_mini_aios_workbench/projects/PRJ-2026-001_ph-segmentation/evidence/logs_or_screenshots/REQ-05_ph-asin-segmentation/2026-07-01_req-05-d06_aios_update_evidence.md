# REQ-05-D06 AIOS Update Evidence — 2026-07-01

## Project ID / Requirement / Deliverable

PRJ-2026-001_ph-segmentation · REQ-05 · REQ-05-D06

## What This Records

The controlled documentation + evidence-import run that folded the 1 July 2026 PH Segmentation
work into the existing REQ-05 task. Import (COPY-only) and register updates only — no database,
no automation, no live-dashboard change, no commit/push.

## Files Copied (byte-exact, checksum-verified after copy)

| # | Destination (project-relative) | Size | SHA-256 |
|---|---|---:|---|
| 1 | handover/REQ-05_ph-asin-segmentation/2026-07-01__abiraj__ph-asin__REQ-05-D06.md | 43951 | 5ebdcb0c238389c37d2b96cfe005b2da770fcaff64563887fc0e41951bb1739c |
| 2 | sql/REQ-05_ph-asin-segmentation/2026-07-01_ph_segment_engine_v2.sql | 12534 | 14a63bc4d24e114a6333b51367b360b7b65f48e2a8a6ce1b2bb2912040e529b0 |
| 3 | prompts/implementation/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_monthly_routine.txt | 38322 | 947879174d87d7f4632e1150a62b05784882e909e8224e85e8706d568c95d1ed |
| 4 | validation/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_protocol_v1_clarifications.md | 4963 | 1de131c25557462929f351dc37b4d4a94eb24fcd519e7772dfe5e4b0cc99f359 |

Each destination was confirmed non-existent before copy (no overwrite). `cp -n` used; post-copy
`sha256sum` matched the source checksums exactly.

## Files Copied — Second Pass (2026-07-02, checksum-verified after copy)

The three artifacts absent on 1 Jul were supplied by Abiraj from `C:\Users\digit\Downloads\` and imported:

| # | Destination (project-relative) | Size | SHA-256 |
|---|---|---:|---|
| 5 | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_unowned_asins_for_assignment_2026-07.csv | 27447 | d4f288d0a47c729275a73f84ea1c4130ad0e4c1a5ca9a41a20e56214267af02c |
| 6 | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_dashboard_id5_live_2026-07.html | 884658 | 951354efd8969d7d97762f9fc6a8d6e5172687524a418fe98f75179f321711b6 |
| 7 | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_dashboard_ph_view_template.html | 752008 | 1bb90b8cca63a2457a27c76bdbf5879e3f0aa61fd62c2cf402c23ff4025319c0 |

Sources: `unowned_asins_for_assignment_2026-07.csv` (Orphan-ASIN assignment output; keeps older
"unowned" name), `preview_v2.html` (confirmed by Abiraj as the latest/live id-5 v2 dashboard — 884,658 B
vs D06-cited ~879,907 B, minor; live DB not queried), `PH_ASIN_Dashboard_PH_view_TEMPLATE.html`.
Each destination confirmed non-existent before copy; `cp -n`; post-copy checksums matched.

_1 Jul discovery search scope (for the record): full `DigitWeb_Works_Abiraj` tree; `Desktop/Postgress_backup/`
incl. `files.zip`; depth-4 `Desktop` sweep. The three files were not present then; no replacements were invented._

## Existing Files Referenced but NOT Copied

- v1 engine `sql/REQ-05_ph-asin-segmentation/2026-06-25_ph_segment_engine.sql` — retained as historical; v2 added alongside, not over it.
- Undated `DigitWeb_Works_Abiraj/PH_Segmentation_Intake/ph_segment_engine.sql` (v1 variant, SHA `0ca4818c…`) — not imported (v1 lineage duplicate).

## Control Files Updated

- handover/REQ-05_ph-asin-segmentation/TASK_HOME.md — added "Daily Increment — REQ-05-D06" section.
- handover/REQ-05_ph-asin-segmentation/HANDOVER.md — added 1 July section + "Do Not Repeat".
- PROJECT_HOME.md — latest work date/deliverable/state fields updated.
- TASK_REGISTER.md — existing REQ-05 row updated (no new row).
- ../../PROJECT_REGISTER.md — REQ-05 row Status/Next-Step updated.

## Records Created (this run)

- evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/2026-07-01_req-05-d06_source_manifest.md
- evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/2026-07-01_req-05-d06_aios_update_evidence.md (this file)
- duplicate_risk_reports/REQ-05_ph-asin-segmentation/2026-07-01_req-05-d06_duplicate_risk.md
- validation/REQ-05_ph-asin-segmentation/2026-07-01_req-05-d06_aios_validation.md

## Actions Deliberately NOT Taken

| Action | Status |
|---|---|
| Database execution | NONE |
| SQL run | NONE |
| Live dashboard modification | NONE |
| Automation execution / creation | NONE |
| Backup tables dropped | NONE |
| Git commit | NOT CREATED |
| Git push | NOT PERFORMED |
| Existing canonical file overwritten | NONE |

## Result

**PASS (updated 2026-07-02)** — all 7 work-products imported and checksum-verified (4 on 1 Jul,
3 on 2 Jul); no artifact missing. No DB/automation/dashboard action; no backup dropped; no commit/push.
_(Was AMBER on 1 Jul when 3 artifacts were absent.)_
