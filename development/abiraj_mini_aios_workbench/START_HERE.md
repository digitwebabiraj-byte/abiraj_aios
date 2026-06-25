# START HERE — Abiraj Mini-AIOS Workbench

> This Mini-AIOS subfolder is **not** parent-AIOS truth.
> Assets created here remain **local subfolder assets** until reviewed and approved
> through the correct parent-AIOS validation process.

## 1. Subfolder Name

`abiraj_mini_aios_workbench`

## 2. Staff / Team Name

Abiraj

## 3. Parent Domain

Development

## 4. Purpose

A safe, evidence-backed and LLM-queryable Mini-AIOS folder structure for Abiraj's daily
development work. It gives every task a fixed place to live so the work is structured,
evidence-backed, reviewable, queryable by an LLM, and safe for another person to continue.

## 5. Business Question

How can Abiraj organise daily development tasks and workflows so every task is structured,
evidence-backed, reviewable, LLM-queryable and safe for another person to continue?

## 6. Local Repository Root

`C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS`

## 7. GitHub Repository Reference

`https://github.com/digitwebabiraj-byte/abiraj_aios.git`

## 8. Approved Scope

- Inspect (read-only): `C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS`
- Create / modify (write): **only** inside
  `C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\development\abiraj_mini_aios_workbench`

## 9. Prohibited Scope

Do not: modify anything outside this subfolder; delete, rename, move or overwrite existing
content; change source code or application configuration; modify PostgreSQL or execute SQL;
run n8n / OpenFlow workflows; change environment variables; create business, financial or
PPC logic; promote anything into parent AIOS; clone another repository; commit or push;
access unrelated folders; or invent missing information.

## 10. Folder Map

| Folder | What goes here |
|---|---|
| `README.md` | Concise project landing page (points to this file and CLAUDE.md) |
| `START_HERE.md` | This orientation file — detailed operating and folder guide |
| `CLAUDE.md` | Claude Code execution rules for this workbench |
| `ASSET_REGISTER.md` | Master list of every asset created here |
| `01_requirements` | Approved written requirements, IDs, scope, PASS/FAIL rules |
| `02_discovery` | Existing-asset searches, inspection reports, duplicate-risk reports |
| `03_source_mapping` | File / source / system / API maps, evidence-source links |
| `04_prompts` | Approved GPT-generated Claude Code prompts that were executed |
| `05_documentation` | Reusable operating documentation and guidance |
| `06_evidence` | Proof: command output, git status, logs, query results, screenshots |
| `07_validation` | Validation reports, queryability tests, PASS/FAIL decisions |
| `08_handover` | Documents that let an unknown person continue without verbal help |
| `09_closure` | Task closure records, final status, paths, one next action |
| `10_daily_work` | Daily requirements, work logs, priorities, end-of-day closure |
| `11_parent_aios_candidates` | Draft candidates for wider reuse (NOT parent-AIOS truth) |

### Authoritative Operating Documents

- `README.md` — concise project landing page.
- `START_HERE.md` — this detailed operating and folder guide.
- `CLAUDE.md` — Claude Code execution rules for this workbench.
- `ASSET_REGISTER.md` — reusable asset register.

### Technical Setup Guide Mapping (reconciliation, ABIRAJ-AIOS-STRUCTURE-002)

The numbered **01–11 structure is the implemented and authoritative architecture** for this
workbench. The `Abiraj_Technical_Setup_Guide.docx` output types are **mapped into** that
numbered structure — **no duplicate named root folders** (evidence, prompts, sql, validation,
workflows, handover, capability, closure) are created at the workbench root.

| Technical Guide Output Type | Approved Destination |
|---|---|
| Proof of work | `06_evidence` |
| GPT prompts executed by Claude | `04_prompts` |
| SQL inspection and draft validation queries | `03_source_mapping/sql` |
| Validation reports | `07_validation` |
| Workflow exports and workflow documentation | `05_documentation/workflows` |
| Closure and handover notes | `08_handover` |
| Reusable extracted methods and capabilities | `05_documentation/capability` |
| Daily closure entries | `09_closure` |

**Launch rule:** Claude Code must be launched from the Mini-AIOS workbench root
(`development\abiraj_mini_aios_workbench`) so it auto-reads `CLAUDE.md` and this guide.

## Multi-Project Storage Rule

1. **Workbench folders `01–11` are for workbench governance only** — Mini-AIOS setup,
   reusable standards, governance reports and workbench-level evidence. They do not hold any
   specific project's working files.
2. **Real business or development projects belong under `projects/<PROJECT_ID>/`** (e.g.
   `projects/PRJ-2026-001_ph-segmentation/`). A project's requirements, prompts, evidence,
   validation, handover and closure all live inside that project folder — never in `01–11`.
3. **Tasks belong only to their assigned project**, stored under their own `<TASK_ID>` inside
   that project. A task never spans two projects.
4. **A new day or a new Claude session does not create a new Task ID.** Keep the existing Task
   ID until the requirement is closed; only a new requirement gets a new Task ID.
5. **Do not mix files from different projects.** One project = one `projects/<PROJECT_ID>/` tree.
6. **Do not duplicate canonical assets.** Each SQL, HTML, evidence or validation asset has one
   canonical location; reference it by path instead of copying it. Identifiers stay unique —
   one Project ID per project, one Task ID per task.
7. **PH Segmentation (`PRJ-2026-001_ph-segmentation`) remains in its current approved
   structure** as the completed legacy project and must not be restructured or moved.

## 11. GPT-to-Claude Operating Loop

1. GPT (planning layer) asks the mandatory questions and writes a structured prompt.
2. Claude Code (execution layer) runs **discovery first** — searching for existing assets.
3. Claude Code reports findings + a GREEN / AMBER / RED decision back to GPT.
4. GPT reviews and, if safe, issues the implementation prompt.
5. Claude Code executes, saves evidence, and reports back.
6. GPT validates (PASS / FAIL) and issues a closure prompt.
7. The task is recorded in `ASSET_REGISTER.md` and closed in `09_closure`.

Claude Code is the **executor, not the planner**. If scope, evidence or a PASS/FAIL rule is
missing from a prompt, it stops and reports the gap instead of inventing it.

## 12. Existing-Asset-First Rule

Before creating anything, search for an existing asset. Decision order:
**1. REUSE** if it fully meets the requirement → **2. EXTEND** if partial →
**3. MERGE** only when clearly safe and no truth is lost → **4. CREATE** only when
uniqueness is proven → **5. STOP** when duplicate or parallel-truth risk exists.

## 13. Duplicate-Truth Prevention Rule

There must be exactly one source of truth for any fact. If creating an asset would produce a
second, competing version of something that already exists, STOP and return the finding for
GPT review rather than creating parallel truth.

## 14. Evidence Requirement

No evidence = not done. Every important asset must point to proof stored in `06_evidence`
(command output, git status, logs, query results or screenshots), linked by path.

## 15. Queryability Requirement

The structure and its assets must be answerable by a clean LLM using only the saved files.
A new LLM should be able to read `START_HERE.md` and the folder READMEs and correctly explain
what this subfolder is, what goes where, and what the rules are — with no verbal explanation.

## 16. Reviewer Responsibilities

- **Coordinator — Varmen:** owns the operating loop and overall task flow.
- **Queryability Reviewer — Tamil Selvan:** confirms the work is answerable by an LLM from saved files.
- **Technical Reviewer — Sajeesan:** reviews technical correctness when technical review is required.

## 17. Business Validator Assignment Rule

A Business Validator is assigned **separately, per task, according to the task type**. Folder
architecture (this task) does not require a Business Validator.

## 18. Daily Task Workflow

1. Record the day's requirement and priorities in `10_daily_work`.
2. Run a reusable-asset scan (existing-asset-first) and log it in `02_discovery`.
3. Execute the approved GPT prompt; save proof to `06_evidence`.
4. Validate the result (PASS / FAIL) in `07_validation`.
5. Register the asset in `ASSET_REGISTER.md`.

## 19. Daily Closure Rule

At end of day, write a closure entry referencing the day's asset paths, evidence paths,
reviewers, any genuine blockers, and exactly one next action — stored in `09_closure`
(with a daily reference in `10_daily_work`).

## 20. Parent-AIOS Candidate Rule

Anything that may be reusable beyond this subfolder goes in `11_parent_aios_candidates` and
must state: `DRAFT CANDIDATE - NOT PARENT-AIOS TRUTH.` Promotion into parent AIOS happens
only through the correct parent-AIOS validation process — never from inside this subfolder.

## 21. Known Limitations

- The local root `Abiraj_AIOS` is **not yet a Git repository** (no `.git` present); GitHub
  status cannot be captured until it is initialised and connected.
- No validated assets exist yet — this is structure only.
- The GitHub repository reference has not been connected or verified from this machine.

## 22. Current Status

ACTIVE STRUCTURE — NO VALIDATED ASSETS YET.

## 23. One Next Action

Hand this structure to GPT for review, then receive the first approved daily-task prompt to
populate `01_requirements` with a real requirement.

## 24. PASS / FAIL Rule

PASS if: the local repository was inspected first; duplicate risk is GREEN; the structure
lives only inside the approved subfolder; no existing file was overwritten; every folder
purpose is documented; discovery, evidence, validation and closure records exist;
`START_HERE.md` is queryable; `ASSET_REGISTER.md` exists; another person can continue using
saved files only; and no commit or push was performed.

FAIL if any of the above is not met.
