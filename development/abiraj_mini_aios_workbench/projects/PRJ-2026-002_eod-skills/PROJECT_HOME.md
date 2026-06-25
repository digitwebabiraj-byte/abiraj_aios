# PROJECT_HOME — EOD-Skills

## Project ID

PRJ-2026-002_eod-skills

## Project Name

EOD-Skills (End-of-Day Staff-Performance Analytics)

## Purpose

Provide one canonical project home for the End-of-Day (EOD) performance-analytics work: the
`eod-query-answerer` Claude skill over the Postgres `daily_eod_log` table, the supporting HR/IT
reports, and the data-integrity remediation — so its deliverables, work summaries and QA
validations are preserved, registered and validated inside the Mini-AIOS structure.

## Business Question

Reconstructed from the source files: "For our staff, across departments and time, who is
delivering high-value verified work, who is wasting hours or logging unverifiable work, and what
is each person's and department's measurable EOD performance?" The skill answers a bank of ~50
predefined HR/management questions from live `daily_eod_log` joins.

Status: **CONFIRMED** (validated by HR; confirmed by Abiraj on 2026-06-25).

## Owner and Reviewers

- Owner: Abiraj
- Coordinator: Varmen
- Technical Reviewer: Sajeesan
- Queryability Reviewer: Tamil Selvan
- Business Validator: HR (validated 2026-06-25)

## Original Requirement

REQ-03, deliverables D01 (2026-06-03), D02 (2026-06-04), D03 (2026-06-08), D04 (2026-06-09).

## Approved Scope

- Maintain this project folder and its subfolders only.
- Preserve, register and validate the existing EOD deliverables, work summaries and QA reports.

## Prohibited Scope

- Do not execute the EOD SQL / skill against any database during onboarding.
- Do not modify the original deliverables or their reported numbers.
- Do not modify anything outside this project folder without written approval.
- Do not commit or push HR/PII content without explicit approval.

## Systems and Sources

- PostgreSQL "ROI database", central table `daily_eod_log`; supporting tables `ph_master`,
  `predefined_question`, department/config tables.
- MCP connection `End_of_the_day_performance_check_Postgress` (historical, used during the original work).

## Imported Assets

Imported 2026-06-25 under Task REQ-03_eod-skills (COPY-only; originals preserved; all 14 checksums
matched). See `evidence/source_documents/REQ-03_eod-skills/SOURCE_MANIFEST.md`.

- 5 final deliverables → `evidence/final_outputs/REQ-03_eod-skills/` (2 are HR-CONFIDENTIAL)
- 4 work summaries (D01–D04) → `handover/REQ-03_eod-skills/`
- 4 QA validation reports (D01–D04) → `validation/REQ-03_eod-skills/`
- 1 query skill (`sql_generate_skill.md`) → `sql/REQ-03_eod-skills/`

## Source-of-Truth Locations

- Final deliverables: `evidence/final_outputs/REQ-03_eod-skills/`
- Work summaries: `handover/REQ-03_eod-skills/`
- QA validations: `validation/REQ-03_eod-skills/`
- Skill: `sql/REQ-03_eod-skills/`
- Manifest: `evidence/source_documents/REQ-03_eod-skills/SOURCE_MANIFEST.md`

## Known Risks

- HR/PII-sensitive deliverables stored in a private repo (consent given).
- The original requirement document (REQ-03 brief) is missing.
- Numeric drift across the deliverables requires business reconciliation (preserved as-is).
- DB corrections claimed in the summaries are unverifiable from this folder.
- Some referenced artifacts (dashboard zip, FastAPI package, Claude artifact) were not provided.

## Reviews

* Business Validation: PASS — HR
* Queryability Validation: PASS — Tamil Selvan
* Technical (Sajeesan) and Coordinator (Varmen): not required by the owner for this onboarding.

(Both required reviews confirmed by Abiraj on 2026-06-25; no separate signed reviewer artifact was supplied.)

## Current Status

ACTIVE — onboarding COMPLETED; task REQ-03_eod-skills CLOSED on the owner-required reviews
(Business + Queryability). Technical review applies only if the EOD skill/SQL is later executed.

## One Next Action

Request technical (Sajeesan), queryability (Tamil Selvan) and business (HR) review of the imported EOD assets.

## Pass / Fail Rule

PASS if EOD-Skills has one canonical project folder, unique Project and Task IDs, all 14 assets
preserved with matching checksums and evidence, no original deliverable modified, and no
unsupported claim marked verified. FAIL otherwise.
