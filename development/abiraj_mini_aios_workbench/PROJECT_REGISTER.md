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
| PRJ-2026-001_ph-segmentation | PH Segmentation | Reconstructed (see PROJECT_HOME.md) | CONFIRMED | Abiraj | Varmen | Sajeesan | Tamil Selvan | Bietrick | ACTIVE | projects/PRJ-2026-001_ph-segmentation/PROJECT_HOME.md | projects/PRJ-2026-001_ph-segmentation/TASK_REGISTER.md | projects/PRJ-2026-001_ph-segmentation/evidence/source_documents/REQ-05_ph-asin-segmentation/SOURCE_MANIFEST.md | D06–D09 all imported and PASS/GREEN as of 6 Jul. Gap-fillers imported 6 Jul (1 Jul navy dashboard md5 9b65e429 → D06 PASS; strict-rank engine sha 3164f427 → D07 PASS). D08 GREEN — clarity pass confirmed **pushed LIVE 3 Jul** (md5 1f657a1b, corrected from "preview"). D09 GREEN — first project DROP: 9 id-5 backups archived + dropped (≈1.8 MB), live id-5 md5 unchanged, 3 report backups kept. Delivery ACTIVE. Next: export v_orphan_asins.sql; swap the monthly routine's HTML BLOCK 1 before the 3 Aug run; get Bietrick's NEW-definition decision; then update SYSTEM_REFERENCE §1/§7 to 8,149. |
| PRJ-2026-002_eod-skills | EOD-Skills | Reconstructed (see PROJECT_HOME.md) | CONFIRMED | Abiraj | Varmen | Sajeesan | Tamil Selvan | HR | ACTIVE | projects/PRJ-2026-002_eod-skills/PROJECT_HOME.md | projects/PRJ-2026-002_eod-skills/TASK_REGISTER.md | projects/PRJ-2026-002_eod-skills/evidence/source_documents/REQ-03_eod-skills/SOURCE_MANIFEST.md | NONE — onboarding closed (Business + Queryability PASS); a new task + Sajeesan approval needed before any EOD execution. |
