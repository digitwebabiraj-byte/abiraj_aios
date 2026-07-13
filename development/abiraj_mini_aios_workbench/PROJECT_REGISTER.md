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
| PRJ-2026-003_blos-project-sentinel | BLOS Project Sentinel (Ledsone Centralizer) | Reconstructed (see PROJECT_HOME.md) | CONFIRMED | Abiraj | Varmen | Sajeesan | Tamil Selvan | Satheewaran (validated) | **CLOSED — VALIDATED** | projects/PRJ-2026-003_blos-project-sentinel/PROJECT_HOME.md | projects/PRJ-2026-003_blos-project-sentinel/TASK_REGISTER.md | projects/PRJ-2026-003_blos-project-sentinel/evidence/source_documents/REQ-04_ledsone-centralizer-user-skill/SOURCE_MANIFEST.md | **CLOSED 2026-07-07 — VALIDATED by Satheewaran (user read + validated the skill file).** Delivered: D06 user skill file (4 formats) + D07 deep continuation package (9 docs); 19/19 checksums, duplicate-risk GREEN, closure gates PASS, adversarial fact-check CORRECT; pushed to git (453ad32). **No pending next steps.** (Informational, outside task: app-side security findings handed to Sajeesan, tracked separately.) |
| PRJ-2026-004_smaw-table5-stock-check | SMAW Table 5 — Weekly Stock Check | Reconstructed (see PROJECT_HOME.md) | CONFIRMED | Abiraj | Varmen | Sajeesan | Tamil Selvan | Thuwaraga (sign-off pending) | VALIDATION | projects/PRJ-2026-004_smaw-table5-stock-check/PROJECT_HOME.md | projects/PRJ-2026-004_smaw-table5-stock-check/TASK_REGISTER.md | projects/PRJ-2026-004_smaw-table5-stock-check/evidence/ | **DELIVERED & LIVE (2026-07-09).** REQ-06 D01 (governed view) + D02 (sellers-only dashboard) + D03 (full-portfolio all-ASIN, **756 ASINs**, FBM fix) complete, reconciled 0-mismatch, published to ops registry (`ph_task` id 137). Next: route V2 dashboard for reviewer sign-off (Tamil Selvan · Sajeesan) + Thuwaraga confirmation; standing item: obtain legacy→canonical SKU mapping. |
| PRJ-2026-005_weekly-sku-performance-check | Table 7 — Weekly SKU Performance Check | Reconstructed (see PROJECT_HOME.md) | CONFIRMED | Abiraj | Varmen | Sajeesan | Tamil Selvan | Thuwaraga + Satheewaran (validated) | **CLOSED — VALIDATED** | projects/PRJ-2026-005_weekly-sku-performance-check/PROJECT_HOME.md | projects/PRJ-2026-005_weekly-sku-performance-check/TASK_REGISTER.md | projects/PRJ-2026-005_weekly-sku-performance-check/evidence/ | **CLOSED 2026-07-09 — VALIDATED by Thuwaraga + Satheewaran.** T7-D01 dataset query + HTML dashboard + xlsx for window 02-Jul→08-Jul-2026 (218 families, 110 performing / 170 orders), reconciled to live DB, published live to `tech_team_outputs.ph_task` (row 135). Optional future: Thursday scheduled run (dynamic window). |
| PRJ-2026-006_zero-sales-full-optimization | ZSFO — Zero Sales Full Optimization (Utharsika, Amazon UK) | Confirmed from utharsika task.xlsx + PROJECT_CONTEXT.md | CONFIRMED (business edge cases pending) | Abiraj | Varmen | Sajeesan | Tamil Selvan | Satheesvaran (sign-off pending) | VALIDATION | projects/PRJ-2026-006_zero-sales-full-optimization/PROJECT_HOME.md | projects/PRJ-2026-006_zero-sales-full-optimization/TASK_REGISTER.md | projects/PRJ-2026-006_zero-sales-full-optimization/evidence/final_outputs/REQ-08_zero-sales-full-optimization/ | **D01 GREEN (technical) + D02 AMBER — BUSINESS SIGN-OFF PENDING (2026-07-10).** D01 weekly zero-sale report (2026-06-10→2026-07-09): **1,719 UK ASINs → 1,250 zero-sale**; corrected query (vendor OVERLAP + NULL-channel bridge), governed data.json, xlsx + dashboard, 6/6 verification pack. **D02** = Amazon `AMZ_2026` cross-check "corrected" report (**1,065**; verified 1,059). ⚠ Revised handoff's *vendor-gap* diagnosis **refuted** on verification — 0/191 vendor, **87% seller sibling-ASIN sales already in DB** (per-ASIN vs per-product / listing sprawl); `vendor_sales` NOT missing; no DB re-sync done (read-only + unwarranted). Not committed/pushed. Next: Satheesvaran to decide per-ASIN vs per-product definition (with correct mechanism) + exclusion rule; then D03 scheduled run. |
| PRJ-2026-007_paused-campaign-report | Paused Campaign Report (Utharsika, Amazon PPC) | Confirmed from Utharsika_task.xlsx + CLAUDE_CODE_HANDOFF_Paused_Campaign.md | CONFIRMED (business edge cases A–E pending) | Abiraj | Varmen | Sajeesan | Tamil Selvan | Satheesvaran (sign-off pending) | VALIDATION | projects/PRJ-2026-007_paused-campaign-report/PROJECT_HOME.md | projects/PRJ-2026-007_paused-campaign-report/TASK_REGISTER.md | projects/PRJ-2026-007_paused-campaign-report/evidence/final_outputs/REQ-09_paused-campaign-report/ | **D01 GREEN (technical) — BUSINESS SIGN-OFF PENDING (2026-07-13).** Read-only PPC report of Utharsika's automation-paused Amazon ad targets that are **still paused today**: **41 total automation pauses → 33 still paused (32 ASINs)**, 8 re-activated excluded. Seven columns (Campaign · Ad Group · ASIN · SKU · Pause Reason (verbatim) · Pause Date · Days Paused); pause waves 2026-06-10 (18) + 2026-06-17 (15). Validated query + governed data.json + xlsx + interactive dashboard + 4/4 verification pack; reconciled live. **Published to `tech_team_outputs.ph_task` row id 215** (`project_code=PC`, `task_id=PC_utharsika_paused_campaigns_dashboard-V1`, `assigned_user=utharsika`, released; guarded single-row INSERT via temp_user, ZSFO precedent; **V2 table-hero dashboard redesign**, version_level 2, md5 fbd4b600). Repo not committed/pushed. Next: Satheesvaran to decide items A–E — primarily grain (per-ASIN vs per-campaign) + included set (33 vs 41); then optional REQ-09-D02 scheduled run. |
