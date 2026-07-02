# PROJECT_HOME — PH Segmentation

## Project ID

PRJ-2026-001_ph-segmentation

## Project Name

PH Segmentation

## Purpose

Provide one canonical project home for the PH Segmentation work so its completed input
documents, final HTML output, work summaries and Claude Chat evidence can be preserved,
registered and validated inside the GPT-controlled Mini-AIOS workflow.

## Business Question

PH Segmentation produced a segmentation deliverable (final HTML output). The exact original
business question is **to be confirmed from the incoming source documents** during this
onboarding task and recorded here once verified — it has not been invented.

## Owner and Reviewers

- Owner: Abiraj
- Coordinator: Varmen
- Technical Reviewer: Sajeesan
- Queryability Reviewer: Tamil Selvan
- Business Validator: Task-dependent (assigned per task type)

## Approved Scope

- Create and maintain this project folder and its subfolders only.
- Receive and store the completed PH Segmentation inputs, final HTML, work summaries and
  Claude Chat evidence into the designated subfolders.
- Register and validate the existing work without changing it.

## Prohibited Scope

- Do not repeat, re-run or modify the original PH Segmentation implementation.
- Do not rewrite or edit the original final HTML during onboarding.
- Do not modify anything outside this project folder without written approval.
- Do not create business, financial or PPC logic.
- Do not commit or push without explicit approval after GPT review.

## Systems and Sources

- Original implementation environment: **Claude Chat** (completed before the GPT-controlled
  workflow was adopted).
- Source documents and final HTML: to be imported into `evidence/source_documents/` and
  `evidence/final_outputs/` under the active Task ID.
- No live database, n8n or OpenFlow system is in scope for this onboarding task.

## Existing Assets

At creation time, no PH Segmentation files exist inside this Mini-AIOS workbench (discovery
returned zero matches). The completed inputs, final HTML and chat evidence are external and
will be imported under Task REQ-05_ph-asin-segmentation.

## Source-of-Truth Locations

- Source documents: `evidence/source_documents/REQ-05_ph-asin-segmentation/`
- Final output (HTML): `evidence/final_outputs/REQ-05_ph-asin-segmentation/`
- Process logs / screenshots / chat evidence: `evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/`
- Validation: `validation/REQ-05_ph-asin-segmentation/`
- Closure: `closure/REQ-05_ph-asin-segmentation/`

## Active Tasks

- REQ-05_ph-asin-segmentation — Status: DISCOVERY (see TASK_REGISTER.md)

## Evidence Locations

- Structure-creation evidence: `evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/2026-06-25_structure_creation_evidence.md`
- Duplicate-risk reports: `duplicate_risk_reports/REQ-05_ph-asin-segmentation/`

## Duplicate-Risk Status

GREEN — PH Segmentation has exactly one canonical project folder; Project ID and Task ID are
unique; no parallel source of truth exists.

## Known Risks

- The original implementation was performed in Claude Chat before GPT supervision; provenance
  of the original work depends on the imported evidence being complete and accurate.
- The original business question and source-document set must be confirmed on import.
- The Mini-AIOS root is not yet a Git repository, so no commit history backs this work yet.

## Current Status

DISCOVERY — canonical structure created and registered; awaiting import of the completed
PH Segmentation inputs, final HTML and Claude Chat evidence.

## One Next Action

Import the completed PH Segmentation source documents and final HTML into the Task ID
subfolders under `evidence/source_documents/` and `evidence/final_outputs/`.

## Pass / Fail Rule

PASS if PH Segmentation has one canonical project folder, the Project and Task IDs are unique,
no original PH Segmentation file is changed, all imported assets land in the correct Task ID
subfolders with evidence, and no commit/push occurs without approval. FAIL if a duplicate
project is created, the original work is modified, an asset is stored without evidence, or
truth is duplicated.

## Provenance Note

The original PH Segmentation implementation was completed in **Claude Chat before the
GPT-controlled workflow was adopted**. This onboarding task **preserves and validates existing
work**. It does **not** claim that GPT supervised the original implementation.

## Portfolio Registration

* Root Project Register:
  ../../PROJECT_REGISTER.md
* Registration Status:
  REGISTERED
* Business Question:
  REQUIRES BUSINESS VALIDATOR (reconstructed from source; not yet confirmed)

## Imported Assets

Imported 2026-06-25 under Task REQ-05_ph-asin-segmentation (COPY-only; originals
preserved; checksums matched). See the manifest for full SHA-256 verification:

* Source manifest: `evidence/source_documents/REQ-05_ph-asin-segmentation/SOURCE_MANIFEST.md`
* Canonical final HTML: `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-06-24_ph-asin_segmentation_report_2026-07.html`
* SQL engine (stored, NOT executed): `sql/REQ-05_ph-asin-segmentation/2026-06-25_ph_segment_engine.sql`
* Monthly run prompt (historical): `prompts/implementation/REQ-05_ph-asin-segmentation/2026-06-25_monthly_run_prompt_historical.md`
* Day-1 summary: `handover/REQ-05_ph-asin-segmentation/2026-06-23__abiraj__ph-asin__REQ-05-D01.md`
* Day-2 summary: `handover/REQ-05_ph-asin-segmentation/2026-06-24__abiraj__ph-asin__REQ-05-D02.md`
* Claude provenance link: `evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/2026-06-25_claude_chat_share_link.txt`

## Candidate Business Question

Which of each PH's UK-Amazon FBM ASINs are underperforming each month based on impressions,
clicks and CVR against category benchmarks, how are they moving month over month, and what
action is due?

Status: CONFIRMED (Business Validator: Bietrick — confirmed by Abiraj on 2026-06-25).

## Reviewer Validations

* Technical Validation: PASS — Sajeesan
* Queryability Validation: PASS — Tamil Selvan
* Business Validation: PASS — Bietrick
* Coordinator Validation: PASS — Varmen
* Onboarding Status: COMPLETED

(All confirmed by Abiraj on 2026-06-25; no separate signed reviewer artifact was supplied.)

## Systems and Sources

* analytics.ph_segment_30days_window
* analytics.ph_segment_report
* public.order_transaction
* PH ASIN Segmentation Protocol document v1.0

## Known Risks

* segmentation mapping requires business ratification;
* SQL is write/DDL and must not run without approval;
* Claude provenance is live-link-only;
* no independent row-count execution evidence;
* HTML visual review remains pending.

## Project Status

ACTIVE. Single task **REQ-05_ph-asin-segmentation**: onboarding/preservation scope CLOSED-PASS,
now in a **delivery phase**. Three delivery increments recorded: the 26 June 2026 dashboard UI fix &
live release, the 30 June 2026 final-June refresh + report validation + data-quality review, and the
**1 July 2026 (REQ-05-D06)** Option-A movement fix + Orphan-ASIN routing + engine v2 + protocol
clarifications + dropdown UI redesign.

## Latest Increment (updated 2026-07-01)

| Field | Value |
|---|---|
| Latest Work Date | 2026-07-01 |
| Latest Deliverable | REQ-05-D06 |
| Project Status | ACTIVE |
| Current live UI | PH dropdown + one-view flat table (`ph_task` id 5); saved HTML imported 2 Jul (`evidence/final_outputs/…/2026-07-01_ph_asin_dashboard_id5_live_2026-07.html`) — VERIFIED_FROM_FILE (live DB row not re-queried) |
| Current live cycle | 2026-07 on the approved Option-A movement state (segments unchanged 8,149) |
| Future engine | v2 four-week engine (`2026-07-01_ph_segment_engine_v2.sql`) — first live run 3 Aug |
| Orphan monitor | `analytics.v_orphan_asins` (permanent view) + live dashboard flag |
| Main open gap | monthly routine HTML BLOCK 1 still builds the **old** UI (swap before 3 Aug) |
| Automation | PENDING (Cloud Routine — Windows VM Platform feature) |
| Import result | PASS (updated 2 Jul) — D06 + **all 6** supporting artifacts imported & checksummed (4 on 1 Jul, 3 on 2 Jul); nothing missing. Was AMBER on 1 Jul. Delivery still ACTIVE (routine BLOCK-1 swap + engine-v2 first run open) |

Records: `handover/REQ-05_ph-asin-segmentation/2026-07-01__abiraj__ph-asin__REQ-05-D06.md`,
`.../TASK_HOME.md`, `.../HANDOVER.md`,
`evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/2026-07-01_req-05-d06_source_manifest.md`
(+ update-evidence), `duplicate_risk_reports/REQ-05_ph-asin-segmentation/2026-07-01_req-05-d06_duplicate_risk.md`,
`validation/REQ-05_ph-asin-segmentation/2026-07-01_req-05-d06_aios_validation.md`,
`evidence/final_outputs/REQ-05_ph-asin-segmentation/` (2 Jul: `2026-07-01_ph_asin_dashboard_id5_live_2026-07.html`,
`2026-07-01_ph_asin_dashboard_ph_view_template.html`, `2026-07-01_unowned_asins_for_assignment_2026-07.csv`).

## Active Tasks (updated 2026-06-30)

- REQ-05_ph-asin-segmentation — Status: **DELIVERY** (onboarding CLOSED-PASS; delivery increments
  AMBER). Two increments of the same REQ-05 requirement, not separate tasks:
  - 26 Jun — dashboard UI fix + live release + routine build:
    `handover/REQ-05_ph-asin-segmentation/2026-06-26_delivery_dashboard-ui-live-report-release.md`.
  - **30 Jun — final-June refresh + validation + data-quality review:**
    `handover/REQ-05_ph-asin-segmentation/2026-06-30_delivery_final-june-refresh-and-data-quality-validation.md`.
  - *Re-homing note:* the 26 Jun increment was briefly filed under a non-compliant dated ID
    `REQ-20260626-002_…`; it was folded back into REQ-05 (the real requirement) per the
    ID-naming convention. The dated ID is retired. Ratified by Abiraj on 2026-06-26.

## Current Operational State

As of **2026-07-01** (DOCUMENTED_IN_D06 unless marked otherwise; the 30 Jun rows below carry
forward except where superseded by the 1 Jul increment — dashboard UI, movement window, orphan
monitor, engine v2):

| Aspect | State |
|---|---|
| Dashboard UI (`ph_task` row id 5) | **PH-dropdown + one-view flat table** (Rank/Avg Conv/Δ Conv/Status), classification logic unchanged; pushed live 1 Jul (~879,907 bytes) — supersedes the tabs/sidebar layout |
| Movement window | **Option A live** — last 4 complete weeks vs previous 4 complete weeks; current segments unchanged; declines 628→574; escalation 24/22 |
| Orphan ASIN monitor | `analytics.v_orphan_asins` created (permanent) + live dashboard warning (492 converting orphans) |
| Engine (going forward) | **v2** self-contained on weekly `traffic_data`, returning-aware — validated scratch-only, first live run 3 Aug |
| Dashboard release (`ph_task` row id 5) | LIVE with **complete-June** numbers (8,149) as of 30 Jun (reported — DB state; DB not queried) |
| `ph_segment_report` | Rebuilt to complete-June window + fully validated vs source + protocol (reported — 30 Jun session) |
| Distribution | **8,149** (51/426/139/5/440/7,088), escalation 24/21 (reported). **Supersedes** the 26 Jun **7,855** build (VERIFIED in repo) |
| 30 Jun backups | `ph_task_id5_backup_20260630`, `ph_segment_report_backup_20260630` in place (droppable when ready) |
| Downloadable HTML (26 Jun build) | **VERIFIED** (imported + checksummed `6F126A4E…`; 7,855). The 30 Jun rebuilt HTML is **not yet imported** |
| Monthly PostgreSQL routine | BUILT (reported; not created/enabled; routine file not imported) |
| Automation creation | PAUSED — Windows VM Platform feature now enabled (PC restarted 30 Jun); routine creation not finished; "Run now" deliberately not clicked |
| Final post-June refresh | **DONE 30 Jun** (reported) — was PENDING on 26 Jun |
| Mark done database persistence | PENDING — **CONFIRMED not implemented** (file persists ticks to browser `localStorage` only) |

> **Source-of-truth note:** `SYSTEM_REFERENCE.md` §1/§7 still show the superseded 7,855 distribution.
> They were **not** overwritten because the 8,149 build is REPORTED_BY_ABIRAJ with no imported
> artifact. Update §1/§7 only after the 30 Jun rebuilt HTML is imported and checksummed.

Records: `handover/REQ-05_ph-asin-segmentation/2026-06-30_delivery_final-june-refresh-and-data-quality-validation.md`,
`validation/REQ-05_ph-asin-segmentation/2026-06-30_final-june-refresh_validation.md`,
`capability/2026-06-30_weekly-snapshot-window-and-data-quality-findings.md`,
`handover/REQ-05_ph-asin-segmentation/2026-06-26_delivery_dashboard-ui-live-report-release.md`,
`validation/REQ-05_ph-asin-segmentation/2026-06-26_release_validation.md`,
`evidence/final_outputs/REQ-05_ph-asin-segmentation/` (2026-06-26 release HTML + `2026-06-26_release_evidence_manifest.md`),
`capability/2026-06-26_server-side-monthly-build-method.md`.

## Future Governed Tasks

Candidates only — **no Task IDs assigned** (no approved written requirement exists yet):

1. Enable and validate monthly PH report automation (Cloud Routine / `pg_cron` / manual on the 3rd).
2. Implement database persistence for the "Mark done" action.
3. Import the 30 Jun work products (rebuilt HTML + checksum, forced-window SQL line, chat link) and
   then update `SYSTEM_REFERENCE.md` §1/§7 to the 8,149 build in a governed step.
4. Adopt the **"last 4 complete weeks"** window (trial, then run past Bietrick) and fix the report
   **header label**; document the **66 "lateral SAME" moves** treatment in `SYSTEM_REFERENCE.md`.
   See `capability/2026-06-30_weekly-snapshot-window-and-data-quality-findings.md`.

> Note: candidate #2 of the prior list — "Refresh the July report after June data closes" — was
> **completed on 30 Jun** as a delivery increment of REQ-05 and is removed from the candidate list.

> **Update 2026-07-01 (REQ-05-D06):** candidate #4 above is now largely delivered — the
> **"last 4 complete weeks" window is approved (Option A, live)**, folded into **engine v2**, and the
> **66 "lateral SAME" / edge-case rules are documented** in the imported protocol clarifications. Two
> leading next action remains **(a) swap the monthly routine's HTML shell (BLOCK 1) to the new dropdown
> UI before the 3 Aug run**. Item **(b) import the 3 missing D06 artifacts** (orphan/unowned CSV + both
> dashboard HTML) is **DONE — imported 2 Jul with matching checksums**. Candidate #1 (automation) is
> unchanged — still PENDING.
