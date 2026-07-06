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
| PRJ-2026-001_ph-segmentation | PH Segmentation | Reconstructed (see PROJECT_HOME.md) | CONFIRMED | Abiraj | Varmen | Sajeesan | Tamil Selvan | Bietrick | ACTIVE | projects/PRJ-2026-001_ph-segmentation/PROJECT_HOME.md | projects/PRJ-2026-001_ph-segmentation/TASK_REGISTER.md | projects/PRJ-2026-001_ph-segmentation/evidence/source_documents/REQ-05_ph-asin-segmentation/SOURCE_MANIFEST.md | D06–D08 all imported and PASS/GREEN as of 6 Jul. On 6 Jul the gap-fillers were found in `Downloads\files (2)\` and imported: the **1 Jul navy live dashboard** (md5 9b65e429 → D06 PASS) and the **strict-rank engine** (sha 3164f427 → D07 PASS); D08 GREEN (read-only). Only the superseded 2 Jul intermediate live build is absent (not needed). Delivery ACTIVE. Next: swap the monthly routine's HTML BLOCK 1 before the 3 Aug run; get Bietrick's NEW-definition decision; then update SYSTEM_REFERENCE §1/§7 to 8,149. |
| PRJ-2026-002_eod-skills | EOD-Skills | Reconstructed (see PROJECT_HOME.md) | CONFIRMED | Abiraj | Varmen | Sajeesan | Tamil Selvan | HR | ACTIVE | projects/PRJ-2026-002_eod-skills/PROJECT_HOME.md | projects/PRJ-2026-002_eod-skills/TASK_REGISTER.md | projects/PRJ-2026-002_eod-skills/evidence/source_documents/REQ-03_eod-skills/SOURCE_MANIFEST.md | NONE — onboarding closed (Business + Queryability PASS); a new task + Sajeesan approval needed before any EOD execution. |
