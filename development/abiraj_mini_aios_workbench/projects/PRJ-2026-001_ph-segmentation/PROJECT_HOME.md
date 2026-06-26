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

ACTIVE (onboarding COMPLETED; task REQ-05_ph-asin-segmentation CLOSED). A second task,
REQ-20260626-002_dashboard-ui-live-report-release, records the 26 June 2026 dashboard UI fix
and live report release (RECORDED — documentation only; substantive claims REPORTED_BY_ABIRAJ).

## Active Tasks (updated 2026-06-26)

- REQ-05_ph-asin-segmentation — Status: CLOSED (PASS). Onboarding/preservation.
- REQ-20260626-002_dashboard-ui-live-report-release — Status: RECORDED (AMBER). New execution
  beyond REQ-05's preservation scope (UI fix + live release + routine build). All claims
  REPORTED_BY_ABIRAJ; Task ID pending GPT/Abiraj ratification (dated invented ID, no backing
  written requirement). See `handover/REQ-20260626-002_dashboard-ui-live-report-release/TASK_HOME.md`.

## Current Operational State

As of 2026-06-26 (REPORTED_BY_ABIRAJ unless marked otherwise):

| Aspect | State |
|---|---|
| Dashboard release | COMPLETE (reported — DB state; not independently verified, DB not queried) |
| Downloadable HTML | COMPLETE — **VERIFIED** (imported + checksummed `6F126A4E…`; 24 PHs, 1,765 cards, 7,855 `segTotal`, 686 LLL, July-2026/Jun-FBM window all read from the file) |
| Monthly PostgreSQL routine | BUILT (reported; not created/enabled; routine file not imported) |
| Automation creation | PAUSED (blocker: Windows Virtual Machine Platform enablement/restart) |
| Final post-June refresh | PENDING (July built on partial June data — file `meta.generated` = 26 June, window 1–30 Jun) |
| Mark done database persistence | PENDING — **CONFIRMED not implemented** (file persists ticks to browser `localStorage` only) |

Records: `handover/REQ-20260626-002_dashboard-ui-live-report-release/TASK_HOME.md`,
`validation/REQ-20260626-002_dashboard-ui-live-report-release/2026-06-26_release_validation.md`,
`evidence/final_outputs/REQ-20260626-002_dashboard-ui-live-report-release/` (HTML + `SOURCE_MANIFEST.md`),
`capability/2026-06-26_server-side-monthly-build-method.md`.

## Future Governed Tasks

Candidates only — **no Task IDs assigned** (no approved written requirement exists yet):

1. Enable and validate monthly PH report automation.
2. Refresh the July report after June data closes.
3. Implement database persistence for the "Mark done" action.
