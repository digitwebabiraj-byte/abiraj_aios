# PROJECT_HOME — BLOS Project Sentinel

## Project ID

PRJ-2026-003_blos-project-sentinel

## Project Name

BLOS — Business Logic Operating System (Project Sentinel) on Ledsone Centralizer

## Purpose

Provide one canonical AIOS project home for Abiraj's BLOS / Project Sentinel work on the
`ledsone-centralizer` application (Laravel + Vue 2 Operations Hub): preserve and register the
completed delivery record (REQ-01 D01–D03, REQ-04 D01–D05), and produce the evidence-backed
**user skill file** (REQ-04-D06) that lets a new user, support staff member, developer or LLM
understand and operate the system without the original developer.

## Business Question

How can the Ledsone Centralizer / BLOS platform (thresholds, business rules, rule builder,
file library) be understood and operated by a new person or LLM using only saved,
evidence-backed documentation — without verbal explanation from the developer?

Status: **CONFIRMED** (derived from the BLOS Build Guide Stage 6 "Skill Pack" and Stage 8
"3AM Documentation" requirements, both tracked as open gaps in the imported
`skill_requirement_tracker.md`).

## Owner and Reviewers

- Owner: Abiraj
- Coordinator: Varmen
- Technical Reviewer: Sajeesan
- Queryability Reviewer: Tamil Selvan
- Business Validator: To be assigned per task type (documentation task — assignment pending)

## Original Requirement

- REQ-01 — deliverables D01 (2026-05-18), D02 (2026-05-19), D03 (2026-05-20): schema,
  UI/File-Manager delivery, data reload + API verification.
- REQ-04 — deliverables D01 (2026-06-11) through D05 (2026-06-19): Rule Builder,
  hardening, data-model cleanup.
- **REQ-04-D06 (this project's active task):** create the ledsone-centralizer user skill file
  per the approved GPT prompt (discovery-first, duplicate-risk-gated, evidence-mapped).

## Approved Scope

- Maintain this project folder and its subfolders only.
- Read-only inspection of the `ledsone-centralizer` repository
  (`C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer`) for discovery and evidence.
- COPY-only import of the Desktop delivery archive
  (`C:\Users\digit\OneDrive\Desktop\Project 1 BLOS-ProjectSentinel`).
- Create the user skill file and its evidence note inside this project.

## Prohibited Scope

- Do not modify `ledsone-centralizer` application code, config, or database.
- Do not invent features, business rules, or claims not supported by files.
- Do not modify the imported source documents or the Desktop originals.
- Do not modify anything outside this project folder without written approval.
- Do not commit or push without explicit instruction after GPT review.

## Systems and Sources

- Application: `ledsone-centralizer` — Laravel 9 backend + Vue 2 Account SPA
  (live: https://centralizer.vintageinterior.co.uk; GitLab `sajeesans2/ledsone-centralizer`,
  branch `Abiraj`).
- Database: MySQL `centralizer` — BLOS tables (`business_rules`, `thresholds`,
  `threshold_versions`, `threshold_dependencies`, `threshold_change_requests`,
  `condition_logics`, `glossary`, `rule_threshold_mapping`, `user_domain_access`) and
  SkillVault tables (`folders`, `files`).
- Requirement sources: BLOS Build Guide v1.0, SkillVault System Design v1.0,
  OIL Configurator v5 reference (all imported — see manifest).

## Imported Assets

Imported 2026-07-07 under Task REQ-04_ledsone-centralizer-user-skill (COPY-only; originals
preserved; all 19 SHA-256 checksums matched). See
`evidence/source_documents/REQ-04_ledsone-centralizer-user-skill/SOURCE_MANIFEST.md`.

- 5 gap/logic notes incl. the master requirements tracker → `evidence/source_documents/.../gaps_and_logics/`
- 8 delivery summaries (REQ-01 D01–D03, REQ-04 D01–D05) → `evidence/source_documents/.../skills/`
- 3 formal developer documentation .docx → `evidence/source_documents/.../output_documents/`
- 3 requirement source documents → `evidence/source_documents/.../requirement_documents/`

## Source-of-Truth Locations

**D06 — user skill file, delivered in four presentation formats (same verified content, different audiences):**
- **Technical / evidence version** (file:line citations, evidence map):
  `evidence/final_outputs/REQ-04_ledsone-centralizer-user-skill/2026-07-07_ledsone-centralizer_user_skill.md` (Rev 2)
- **End-user manual version** (Listing-Tool format: module-by-module How-to; independently fact-checked against the repo 2026-07-07 — CORRECT):
  `evidence/final_outputs/REQ-04_ledsone-centralizer-user-skill/LEDsONE_Centralizer_Skill_File.md`
- **MD / executive version** (clean prose, no code citations, security items excluded):
  `evidence/final_outputs/REQ-04_ledsone-centralizer-user-skill/2026-07-07_ledsone-centralizer_user_guide_MD.md`
- **COMPLETE all-in-one** (skill file + all D07 deep docs merged into one file):
  `evidence/final_outputs/REQ-04_ledsone-centralizer-user-skill/2026-07-07_ledsone-centralizer_COMPLETE_skill_file.md`
- Evidence note: `evidence/logs_or_screenshots/REQ-04_ledsone-centralizer-user-skill/2026-07-07_user_skill_evidence_note.md`
- Duplicate-risk report: `duplicate_risk_reports/REQ-04_ledsone-centralizer-user-skill/2026-07-07_user_skill_duplicate_risk.md`

**D07 — deep continuation package (all under `evidence/final_outputs/REQ-04_ledsone-centralizer-user-skill/`):**
- `2026-07-07_REQ-04-D07_continuation_guide.md` — **start here to continue the project**
- `2026-07-07_REQ-04-D07_code_map.md`
- `2026-07-07_REQ-04-D07_data_dictionary.md`
- `2026-07-07_REQ-04-D07_api_reference.md`
- `2026-07-07_REQ-04-D07_ui_reference.md`
- `2026-07-07_REQ-04-D07_security_and_deploy.md`
- `2026-07-07_REQ-04-D07_verification_findings.md`
- `2026-07-07_REQ-04-D07_shared_modules_inventory.md`
- D07 evidence note: `evidence/logs_or_screenshots/REQ-04_ledsone-centralizer-user-skill/2026-07-07_REQ-04-D07_evidence_note.md`
- D07 closure gates: `validation/REQ-04_ledsone-centralizer-user-skill/2026-07-07_REQ-04-D07_closure_gates.md`

**Project-level:** `SYSTEM_REFERENCE.md` (upgraded to v2, 2026-07-07).

**Shared:**
- Source manifest: `evidence/source_documents/REQ-04_ledsone-centralizer-user-skill/SOURCE_MANIFEST.md`
- Repository-side living engineering log (NOT owned by this project, referenced only):
  `ledsone-centralizer/docs/skill.md`

## Known Risks

- The BLOS system has documented data gaps (only 16 of 300+ BL-## rules registered;
  `user_domain_access` and `threshold_dependencies` at 0 records per the tracker) — the user
  skill file documents behaviour as built, and flags data-dependent features accordingly.
- The Desktop archive and the repository may drift; the copies here are frozen as of 2026-07-07.
- Requirement docx files are company-confidential — internal distribution only.

## Status

ACTIVE

## One Next Action

Submit the D06 skill file (Rev 2) + the D07 continuation package for Queryability review
(Tamil Selvan) and Technical review (Sajeesan — priority: the P0 security findings: public
`role=admin` registration, and the plaintext production credential committed in
`.vscode/sftp.json`). Developers continuing the project start from the D07 continuation guide.
