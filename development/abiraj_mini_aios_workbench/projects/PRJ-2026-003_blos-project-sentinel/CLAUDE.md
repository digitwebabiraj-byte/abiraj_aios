# CLAUDE.md — PRJ-2026-003_blos-project-sentinel

Inherits all rules from the workbench root `CLAUDE.md` and `START_HERE.md`
(`development/abiraj_mini_aios_workbench/`). Project-specific rules below.

## Scope

- Write only inside `projects/PRJ-2026-003_blos-project-sentinel/`.
- The `ledsone-centralizer` repository
  (`C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer`) is **read-only evidence
  source** — never modify its code, config, or database from this project.
- The Desktop archive `C:\Users\digit\OneDrive\Desktop\Project 1 BLOS-ProjectSentinel` holds
  the user's original delivery files — read-only; the registered copies live in
  `evidence/source_documents/REQ-04_ledsone-centralizer-user-skill/`.

## Task ID Rule

- Active task: `REQ-04_ledsone-centralizer-user-skill` (deliverable **REQ-04-D06**, continuing
  the BLOS REQ-04 stream whose D01–D05 are imported in `evidence/source_documents/.../skills/`).
- Do not mint new REQ numbers; a new requirement needs the owner's confirmation first.

## Evidence Rule

- Every claim in the user skill file must map to a file path in the repository, the imported
  source documents, or this project — with status VERIFIED / PARTIAL / UNPROVEN.
- No evidence = UNPROVEN = flagged in Known Limits, never stated as fact.

## Duplicate-Truth Rule

- The repository file `docs/skill.md` is the repo-side **engineering log** (developer-facing).
  The user skill file here is **user-facing** — different purpose, no merge. Do not create a
  second engineering log; do not copy the user skill file back into the repository without an
  approved prompt.

## Stop Conditions (in addition to workbench rules)

- Stop if asked to state a business rule that has no file evidence.
- Stop if asked to modify the ledsone-centralizer application.
- Stop if a change would contradict the imported requirement tracker without new evidence.
