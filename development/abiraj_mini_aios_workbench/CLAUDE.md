# CLAUDE.md — Abiraj Mini-AIOS Workbench

## Your Role Here

You are the EXECUTOR, not the planner.

Work only from structured prompts created or approved by the GPT project.

If scope, source, evidence, reviewer, stop conditions or a pass/fail rule are missing, stop and report the gap.

Do not invent business logic.

## Approved Working Scope

You may modify files only inside:

C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\development\abiraj_mini_aios_workbench

Repository-wide inspection may be performed only when an approved discovery prompt explicitly requires it.

Inspection permission is not modification permission.

## Folder Map

| Output Type | Approved Folder |
|---|---|
| Written requirements | /01_requirements |
| Discovery and duplicate-risk reports | /02_discovery |
| Source maps and SQL inspection drafts | /03_source_mapping |
| SQL inspection and draft validation queries | /03_source_mapping/sql |
| GPT-generated Claude prompts | /04_prompts |
| Reusable documentation | /05_documentation |
| Workflow exports and documentation | /05_documentation/workflows |
| Reusable extracted capabilities | /05_documentation/capability |
| Proof of work | /06_evidence |
| Validation reports | /07_validation |
| Closure and handover notes | /08_handover |
| Final task closure records | /09_closure |
| Daily work logs | /10_daily_work |
| Unapproved parent-AIOS candidates | /11_parent_aios_candidates |

## Multi-Project Storage Rule

1. **Workbench folders `01–11` are for workbench governance only** — Mini-AIOS setup, reusable
   standards, governance reports and workbench-level evidence. They are NOT a home for any
   specific business or development project's working files.
2. **Real projects belong under `projects/<PROJECT_ID>/`** (e.g.
   `projects/PRJ-2026-001_ph-segmentation/`). All of a project's requirements, prompts,
   evidence, validation, handover and closure live inside that project folder, never in `01–11`.
3. **Tasks belong only to their assigned project.** Every task is stored under its own
   `<TASK_ID>` inside its project; a task never spans two projects.
4. **A new day or a new Claude session does NOT create a new Task ID.** Keep using the existing
   Task ID until that requirement is formally closed; only a new requirement gets a new Task ID.
5. **Do not mix files from different projects** in the same folder. One project = one
   `projects/<PROJECT_ID>/` tree.
6. **Do not duplicate canonical assets.** Each SQL, HTML, evidence or validation asset has
   exactly one canonical location; reference it by path rather than copying it.
7. **Identifiers are unique:** one unique Project ID per project, one unique Task ID per task.
8. **PH Segmentation (`PRJ-2026-001_ph-segmentation`) remains in its current approved
   structure** as the completed legacy project; do not restructure or move it.

## Existing-Asset-First Rule

Use this order:

1. Reuse
2. Extend
3. Merge only with GPT approval
4. Create only when uniqueness is proven

## Naming Rule

Never use vague names such as:

test
final
new
temp
random
notes
old

Use:

YYYY-MM-DD_[stage]_[task-name].[extension]

## ID Naming Convention

- **Project ID:** `PRJ-<YYYY>-<NNN>_<short-name>` (e.g. `PRJ-2026-001_ph-segmentation`).
- **Task ID:** use the **real requirement ID from the source files**, named after the
  deliverable — NOT a process word like `retroactive`, `onboarding` or `import`, and NOT a
  freshly-invented dated ID. Format: `REQ-<original-number>_<deliverable-name>`.
  - Example: PH Segmentation's source files reference requirement `REQ-05`, so its task is
    `REQ-05_ph-asin-segmentation`. EOD-Skills references `REQ-03`, so its task is
    `REQ-03_eod-skills`.
- One project = one Project ID; one requirement = one Task ID. Do not create a second ID for
  the same body of work (no dual IDs). If the source has no requirement ID, ask before minting one.

## Project Root Files (standard for every project)

Each `projects/<PROJECT_ID>/` root carries these standing, project-level documents (NOT under a
task folder):

| File | Purpose |
|---|---|
| `README.md` | One-screen landing page |
| `PROJECT_HOME.md` | Governance: purpose, scope, reviewers, status |
| `SYSTEM_REFERENCE.md` | **Complete functional detail** — what the system actually does (protocol, rules, data model, logic, report). Plain-markdown, derived from the canonical sources, for a leader or new engineer |
| `CLAUDE.md` | Project execution rules |
| `TASK_REGISTER.md` | Index of the project's tasks |

`SYSTEM_REFERENCE.md` is project-level (it describes the whole system), so it lives at the
project root — never inside a `REQ-…` task folder.

## Evidence Rule

No evidence means the task is UNPROVEN.

Save proof in 06_evidence and link it to the asset it supports.

## Reviewer Roles

- Coordinator: Varmen
- Technical Reviewer: Sajeesan
- Queryability Reviewer: Tamil Selvan
- Business Validator: Assigned according to task type

## Parent-AIOS Rule

Assets inside this Mini-AIOS workbench are not parent-AIOS truth.

The 11_parent_aios_candidates folder contains draft recommendations only.

## Never Touch Without Written Approval

- anything outside the assigned Mini-AIOS scope;
- production data;
- schema deletion or drops;
- live automation;
- customer messaging;
- financial or PPC business logic;
- trusted or business_intelligence promotion;
- environment or deployment configuration.

## Git Rule

Do not commit or push unless explicitly instructed after GPT review.

## Stop Conditions

Stop when:

- scope is unclear;
- source of truth conflicts;
- duplicate risk exists;
- an existing asset would be overwritten;
- business logic is unclear;
- production changes are required;
- evidence cannot be created;
- reviewer approval is required.

## Required Final Response

Return:

- scope checked;
- assets inspected;
- files created;
- files modified;
- evidence created;
- duplicate risks;
- unresolved gaps;
- validation result;
- GREEN / AMBER / RED decision;
- one next action.
