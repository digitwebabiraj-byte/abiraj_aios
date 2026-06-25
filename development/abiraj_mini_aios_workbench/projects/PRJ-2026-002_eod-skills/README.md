# EOD-Skills — PRJ-2026-002

## What Is EOD-Skills?

An End-of-Day (EOD) staff-performance analytics system: a Claude skill (`eod-query-answerer`)
that answers HR/management questions from the live Postgres `daily_eod_log` table, plus HR/IT
reports and a data-integrity clean-up. Built by Abiraj under requirement REQ-03 (3–9 June 2026).

## Why This Project Folder Exists

To give EOD-Skills one canonical home in the Mini-AIOS workbench so its deliverables, work
summaries and QA validations are preserved, registered and validated — without changing the
original work.

## Business Question Supported

Who is delivering high-value verified work, who is wasting hours or logging unverifiable work,
and what is each person's/department's measurable EOD performance? (Status: REQUIRES BUSINESS VALIDATOR.)

## Where Things Are Stored

- Final deliverables (5 docx): `evidence/final_outputs/REQ-03_eod-skills/`
- Work summaries (D01–D04): `handover/REQ-03_eod-skills/`
- QA validation reports (D01–D04): `validation/REQ-03_eod-skills/`
- Query skill: `sql/REQ-03_eod-skills/`
- Manifest + evidence: `evidence/source_documents/…/SOURCE_MANIFEST.md`, `evidence/logs_or_screenshots/…`

## Who Owns and Reviews It

Owner: Abiraj · Coordinator: Varmen · Technical: Sajeesan · Queryability: Tamil Selvan · Business: HR (to be assigned).

## Current Status

ONBOARDING — imported and registered; pending technical, queryability and business validation.

## Known Limitations

- HR/PII-sensitive deliverables (private repo).
- Original REQ-03 requirement document missing.
- Numeric drift across deliverables (preserved as-is, flagged for business review).
- DB corrections claimed but unverifiable from this folder.

## One Next Step

Request technical, queryability and business review of the imported EOD assets.

## Pass / Fail Rule

PASS if all 14 assets are preserved with matching checksums and evidence, IDs are unique, no
original deliverable is modified, and no unsupported claim is marked verified. FAIL otherwise.

For full detail see `PROJECT_HOME.md`; for execution rules see `CLAUDE.md`.
