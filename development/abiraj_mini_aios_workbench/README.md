# Abiraj Mini-AIOS Workbench

## Setup

| Field | Value |
|---|---|
| Staff / Team Name | Abiraj |
| Assigned AIOS Subfolder | development/abiraj_mini_aios_workbench |
| Parent Domain | Development |
| Coordinator | Varmen |
| Technical Reviewer | Sajeesan |
| Queryability Reviewer | Tamil Selvan |
| Business Validator | Assigned according to task type |
| Repository Root | C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS |

## What Is This?

This is Abiraj's controlled Mini-AIOS workbench for organising daily development work into
evidence-backed, reusable and LLM-queryable assets. Every task has a fixed place to live so
the work is structured, reviewable, queryable by an LLM, and safe for another person to
continue.

## Why Does It Exist?

It exists so daily development tasks are never ad-hoc: each task starts from an approved
requirement, is executed by Claude Code under GPT direction, leaves proof in `06_evidence`,
is validated, and is closed with one clear next action — leaving a trail anyone can follow.

## Business Question Supported

How can Abiraj organise daily development tasks and workflows so every task is structured,
evidence-backed, reviewable, LLM-queryable and safe for another person to continue?

## Authoritative Operating Documents

- README.md — concise project landing page (this file)
- START_HERE.md — detailed operating and folder guide
- CLAUDE.md — Claude Code execution rules
- ASSET_REGISTER.md — reusable asset register

> README.md must not redefine detailed rules already maintained in START_HERE.md or CLAUDE.md.
> For full rules, scope and workflow, read START_HERE.md and CLAUDE.md.

## Folder Map

The **numbered 01–11 structure is the implemented and authoritative architecture.** No
duplicate named root folders are created; the Technical Setup Guide output types map into it.

| Folder | Purpose | Guide Output Type Mapped Here |
|---|---|---|
| `01_requirements` | Approved requirements, IDs, scope, PASS/FAIL | — |
| `02_discovery` | Existing-asset searches, duplicate-risk reports | — |
| `03_source_mapping` | Source / system / API maps | — |
| `03_source_mapping/sql` | SQL inspection & draft validation queries | SQL inspection and draft validation queries |
| `04_prompts` | Approved GPT prompts executed by Claude | GPT prompts executed by Claude |
| `05_documentation` | Reusable operating documentation | — |
| `05_documentation/workflows` | Workflow exports & documentation | Workflow exports and workflow documentation |
| `05_documentation/capability` | Reusable extracted methods | Reusable extracted methods and capabilities |
| `06_evidence` | Proof of work | Proof of work |
| `07_validation` | Validation reports | Validation reports |
| `08_handover` | Closure and handover notes | Closure and handover notes |
| `09_closure` | Final task closure records | Daily closure entries |
| `10_daily_work` | Daily requirements and work logs | — |
| `11_parent_aios_candidates` | Draft parent-AIOS candidates (not truth) | — |

## Evidence

See 06_evidence.

## Status

DRAFT — AWAITING REVIEW

## Known Limits

- The local repository root is not yet a Git repository; no commit/push has occurred or is possible until it is initialised and connected.
- The `Abiraj_Technical_Setup_Guide.docx` is located in the user's Downloads folder, not inside the repository root.
- No validated work assets exist yet — this is structure and reconciliation only.

## Pass / Fail Rule

PASS if this landing page correctly identifies the authoritative documents and numbered
structure, maps the guide output types without creating duplicate root folders, and lets a
new reader reach START_HERE.md and CLAUDE.md for full rules. FAIL if it redefines detailed
rules, contradicts START_HERE.md/CLAUDE.md, or introduces a parallel structure.

## One Next Step

Hand README.md and CLAUDE.md to the Coordinator (Varmen), Technical Reviewer (Sajeesan) and
Queryability Reviewer (Tamil Selvan) for review.
