# FOLDER_STANDARD.md — the per-project folder structure

> **Status: PROPOSAL (awaiting Abiraj's confirmation).** This documents the standard every
> `projects/<PROJECT_ID>/` folder should follow, so the structure stops drifting between projects.
> It is derived from what the 15 existing projects actually converged on — it does not invent new rules.

## Why this exists

An audit on 2026-07-27 found the per-project scaffold had drifted with no single template:
early projects (001–004) carried 10 sub-folders; the newest (012–015) carried 4. There was no
document saying which folders a project *must* have, so "weak structure" was undefinable. This file
sets the baseline.

## Root files — required for every project (already consistent across all 15)

| File | Purpose |
|---|---|
| `README.md` | One-screen landing page |
| `PROJECT_HOME.md` | Governance: purpose, scope, reviewers, status |
| `SYSTEM_REFERENCE.md` | Complete functional detail — what the system actually does |
| `CLAUDE.md` | Project execution rules |
| `TASK_REGISTER.md` | Index of the project's tasks |

## Sub-folders

### Required — every project

| Folder | Holds | Rule |
|---|---|---|
| `evidence/` | Proof of work — `source_documents/`, `final_outputs/`, `logs_or_screenshots/` per `REQ-…` | No evidence = the task is UNPROVEN |
| `sql/` | Canonical SQL per `REQ-…` | One canonical copy; reference by path |
| `validation/` | Validation / verification records per `REQ-…` | Every headline reconciled before it ships |
| `closure/` | Task closure records per `REQ-…` (`closure/REQ-XX_.../<date>_closure.md`) | One record per task; states final status, evidence paths, reviewers, open items, one next action |

### Required *when applicable*

| Folder | Required when | Rule |
|---|---|---|
| `automation/` | The project has (or will have) a scheduled job | Holds the runner, registrar, secrets template, status/alert scripts. If automation lives elsewhere (e.g. under `capability/`), that is a naming inconsistency to fix, not a second home |

### Optional — governance-heavy onboarding only

These were used mainly by the first four projects (001–004) during heavy onboarding and are **not
required**. Create one only when it will actually hold content — never as an empty placeholder
(empty dirs do not survive a git commit anyway).

`capability/` · `handover/` · `prompts/` · `workflows/` · `duplicate_risk_reports/`

## The baseline, in one line

**Required: `evidence` + `sql` + `validation` + `closure`** (plus `automation` if scheduled), on top of
the five root files. Everything else is optional and content-driven.

## Closure-record location (settles the DST anomaly)

A project's closure record lives in its **own** `projects/<ID>/closure/` folder — this is the dominant
convention (11 of 15 projects) and matches the CLAUDE.md multi-project rule ("all of a project's …
closure live inside that project folder, never in 01–11"). The workbench-level `09_closure/` is for
**workbench-governance** closures (e.g. the folder-architecture closure), not per-business-project ones.
PRJ-2026-015 (DST) was the historical exception; its record was relocated from `09_closure/` into
`projects/PRJ-2026-015_daily-sales-track/closure/REQ-17_daily-sales-track/2026-07-23_closure.md` on
2026-07-27, so all business-project closures now live in their own project folders.

## Known-good reference

`PRJ-2026-010_ebay-price-checker` is a clean example of the required baseline done well
(root files + `automation/closure/evidence/sql/validation`, with a full closure record).
`PRJ-2026-001_ph-segmentation` is the completed legacy project and is **not** to be restructured.

## Conformance as of 2026-07-27

All 15 projects now hold the four required folders (`closure/` was added to 012–015 on 2026-07-27, and
DST's closure record was consolidated into its project folder the same day).
Deviations that remain are intentional and recorded:
- **003** blos-project-sentinel — no `sql/` (non-SQL project); left as-is by owner instruction.
- **002** eod-skills — no `automation/` (onboarding-only, nothing scheduled); left as-is.
- **008** frrc — automation scripts live under `capability/2026-07-15_monthly_run_toolkit/` rather than
  `automation/`; a naming inconsistency, content is present and working.
