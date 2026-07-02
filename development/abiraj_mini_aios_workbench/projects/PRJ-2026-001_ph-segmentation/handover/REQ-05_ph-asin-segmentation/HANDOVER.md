# PH Segmentation Handover

## Project ID

PRJ-2026-001_ph-segmentation

## Task ID

REQ-05_ph-asin-segmentation

## What Was Imported

The approved seven-asset PH Segmentation set: the protocol document, the canonical final HTML,
the Day-1 and Day-2 work summaries, the Claude Chat provenance link, the SQL engine, and the
historical monthly run prompt. All copied with matching SHA-256 checksums.

## Why It Was Imported

To preserve, classify and validate previously completed work (done in Claude Chat before the
GPT-controlled workflow) inside the approved Mini-AIOS project structure, so it is reviewable,
queryable and safe for another person to continue.

## Canonical Asset Paths

* Protocol: `evidence/source_documents/REQ-…001/2026-06_ph-asin_segmentation_protocol_v1.0.docx`
* Final HTML: `evidence/final_outputs/REQ-…001/2026-06-24_ph-asin_segmentation_report_2026-07.html`
* SQL engine: `sql/REQ-…001/2026-06-25_ph_segment_engine.sql`
* Monthly prompt (historical): `prompts/implementation/REQ-…001/2026-06-25_monthly_run_prompt_historical.md`
* Day-1 / Day-2 summaries: `handover/REQ-…001/2026-06-2{3,4}__abiraj__ph-asin__REQ-05-D0{1,2}.md`
* Provenance link: `evidence/logs_or_screenshots/REQ-…001/2026-06-25_claude_chat_share_link.txt`

## Source Manifest

`evidence/source_documents/REQ-05_ph-asin-segmentation/SOURCE_MANIFEST.md`

## Final HTML

CANONICAL_CONFIRMED by Abiraj (SHA-256 `25dd9103…29f7f74c`). Visual correctness review still pending.

## SQL Warning

STORED ONLY — NOT EXECUTED. Write/DDL (drops & recreates `analytics.ph_segment_report` + temp helpers). See `sql/REQ-…001/README.md`.

## Monthly Prompt Status

PRESERVED AS HISTORICAL — NOT GOVERNED FOR REUSE. See `prompts/implementation/REQ-…001/README.md`.

## Claude Provenance Limitation

LIVE_LINK_ONLY — ACCEPTED WITH LIMITATION. May expire; not archived locally; partial provenance; not a blocker.

## Validation Status

Import PASS (checksums matched, originals preserved). All four reviews now PASS:

* Technical Validation: PASS — Sajeesan
* Queryability Validation: PASS — Tamil Selvan
* Business Validation: PASS — Bietrick
* Coordinator Validation: PASS — Varmen

(Confirmed by Abiraj on 2026-06-25; no separate signed reviewer artifact was supplied.)
**Task status: onboarding scope CLOSED; REOPENED to a DELIVERY phase on 2026-06-26** — the
dashboard UI fix and live report release are a delivery increment of this requirement, recorded
at `handover/REQ-05_ph-asin-segmentation/2026-06-26_delivery_dashboard-ui-live-report-release.md`
(re-homed from the non-compliant dated ID `REQ-20260626-002_…`). Future SQL execution still
requires written write authorisation.

## Business Question Status

CONFIRMED.

## Technical Review

PASS — Sajeesan. (Future DB execution still requires a new task + written write authorisation.)

## Business Review

PASS — Bietrick.

## Known Gaps

No saved SQL execution output; no independent 7,855-row validation; no immutable chat export; no business sign-off; no production-readiness approval.

## What Must Not Be Done

* do not execute SQL without approval;
* do not treat the monthly prompt as governed;
* do not claim business approval;
* do not replace canonical files without a new task;
* do not duplicate evidence.

## 1 July 2026 Increment (REQ-05-D06)

Recorded read-only from the D06 knowledge file; live session run by Abiraj. Import result **AMBER**.

- **What is now live** (DOCUMENTED_IN_D06, DB not queried here): dashboard row `tech_team_outputs.ph_task`
  id 5 rebuilt to a **PH-dropdown + one-view flat-table UI** with the Option-A movement fix and a
  live Orphan-ASIN warning banner; `analytics.ph_segment_report` on the approved Option-A state
  (current segments unchanged 51/426/139/5/440/7,088; declines 628→574); `analytics.v_orphan_asins`
  monitor view created.
- **Files delivered & imported** (all checksum-matched): engine v2 (`2026-07-01_ph_segment_engine_v2.sql`),
  updated monthly routine (`2026-07-01_ph_asin_monthly_routine.txt`), protocol clarifications
  (`2026-07-01_ph_asin_protocol_v1_clarifications.md`), the D06 knowledge file, and — imported 2 Jul —
  the live dashboard HTML (`evidence/final_outputs/…/2026-07-01_ph_asin_dashboard_id5_live_2026-07.html`),
  the UI review template (`…_ph_view_template.html`), and the orphan/unowned assignment CSV
  (`…/2026-07-01_unowned_asins_for_assignment_2026-07.csv`, 492 rows).
- **Logic changed**: movement window = last 4 complete weeks vs the previous 4 complete weeks
  (Option A live; Option B baked into engine v2 for future cycles); returning-aware NEW rule (8-week
  lookback); Orphan ASIN formally defined (user_name NULL across 4 sources).
- **Logic NOT changed**: 6-segment classification, Method-A CVR benchmark, movement h-count,
  FBM/UK/Amazon scope, conversion edges, Option-B letter map. The reference board's weighted-CVR
  method was **rejected** — only its layout was adopted.
- **Database objects involved**: read `traffic_data`, `order_transaction`, `vw_surfaceable_data`,
  `amz_fbm_performance_data`; wrote `ph_segment_report` (+ backups) and `ph_task` id 5 (+ backups);
  created `v_orphan_asins`; scratch tables created and dropped.
- **Scratch-only**: engine v2 was validated in scratch tables and **not** run against the live
  2026-07 report (first live run 3 Aug).
- **Backups remaining**: `ph_segment_report_backup_optA`, `ph_segment_report_backup_20260630`,
  `ph_task_id5_backup_orphan`, `ph_task_id5_backup_20260630`, `ph_task_id5_backup_newui`, plus a
  pre-push backup before the column-add UI update — all KEPT.
- **Routine UI-shell risk**: the monthly routine's HTML shell (BLOCK 1) still builds the **old** tabs
  layout; a 3 Aug run before it is swapped would regenerate the old UI (data/logic still correct).
- **Automation blocker**: Cloud Routine still not created (Windows Virtual Machine Platform feature).
- **Missing artifacts**: NONE remaining. The three files absent on 1 Jul (orphan/unowned CSV + both
  dashboard HTML) were supplied by Abiraj and imported 2 Jul with matching checksums — the import is
  now PASS. (The live DB row itself was not re-queried; the imported HTML is the confirmed latest v2 build.)
- **Next safe action**: swap the routine's BLOCK 1 to the new UI before 3 Aug.

### Do Not Repeat

- Do not rerun the Option-A patch without a new approved requirement.
- Do not run engine v2 against the frozen 2026-07 report.
- Do not auto-assign Orphan ASIN owners.
- Do not adopt the reference dashboard's weighted-CVR method.
- Do not drop backup tables without a separately approved housekeeping task.
- Do not execute the monthly routine merely to validate its documentation.

## One Next Step

Swap the monthly routine's HTML shell (BLOCK 1) to the new dropdown UI before the 3 Aug run. All D06
artifacts (incl. the live dashboard HTML, UI template and orphan/unowned CSV) are now imported and
checksummed, so the D06 artifact-import step is closed. Any future SQL execution still requires
written write authorisation.
