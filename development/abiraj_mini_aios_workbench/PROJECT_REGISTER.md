# Abiraj Mini-AIOS Project Register

## Purpose

This register is the root index of projects managed inside Abiraj's Mini-AIOS workbench.

It helps users and LLMs locate each project's canonical PROJECT_HOME.md, current status, reviewers and next action.

This register is not the detailed source of project truth.

Detailed project context must remain in each project's PROJECT_HOME.md.

## Canonical Truth Rule

* PROJECT_REGISTER.md is the portfolio index.
* Each PROJECT_HOME.md is the canonical project context.
* Each project-level TASK_REGISTER.md is the canonical index of tasks within that project.
* Evidence, validation and closure remain in their approved project paths.
* Do not copy complete project descriptions into this register.
* Link to canonical files instead.

## Project Status Values

* PROPOSED
* DISCOVERY
* ONBOARDING
* ACTIVE
* BLOCKED
* VALIDATION
* CLOSED
* SUPERSEDED

## Business Question Status Values

* CONFIRMED
* TO BE CONFIRMED FROM SOURCE DOCUMENTS
* REQUIRES BUSINESS VALIDATOR
* NOT APPLICABLE

## Project Register

| Project ID | Project Name | Business Question | Business Question Status | Owner | Coordinator | Technical Reviewer | Queryability Reviewer | Business Validator | Status | Project Home | Task Register | Evidence | Next Step |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRJ-2026-001_ph-segmentation | PH Segmentation | Reconstructed (see PROJECT_HOME.md) | CONFIRMED | Abiraj | Varmen | Sajeesan | Tamil Selvan | Bietrick | ACTIVE | projects/PRJ-2026-001_ph-segmentation/PROJECT_HOME.md | projects/PRJ-2026-001_ph-segmentation/TASK_REGISTER.md | projects/PRJ-2026-001_ph-segmentation/evidence/source_documents/REQ-05_ph-asin-segmentation/SOURCE_MANIFEST.md | REQ-05-D06 fully imported (Option-A movement fix, Orphan-ASIN monitor, engine v2, protocol clarifications, dropdown UI) — import **PASS** as of 2 Jul: D06 + all 6 supporting artifacts checksummed (live dashboard HTML, UI template & unowned/orphan CSV added 2 Jul). Delivery still ACTIVE. Next: swap the monthly routine's HTML BLOCK 1 to the new dropdown UI before the 3 Aug run; then update SYSTEM_REFERENCE §1/§7 to 8,149. |
| PRJ-2026-002_eod-skills | EOD-Skills | Reconstructed (see PROJECT_HOME.md) | CONFIRMED | Abiraj | Varmen | Sajeesan | Tamil Selvan | HR | ACTIVE | projects/PRJ-2026-002_eod-skills/PROJECT_HOME.md | projects/PRJ-2026-002_eod-skills/TASK_REGISTER.md | projects/PRJ-2026-002_eod-skills/evidence/source_documents/REQ-03_eod-skills/SOURCE_MANIFEST.md | NONE — onboarding closed (Business + Queryability PASS); a new task + Sajeesan approval needed before any EOD execution. |
