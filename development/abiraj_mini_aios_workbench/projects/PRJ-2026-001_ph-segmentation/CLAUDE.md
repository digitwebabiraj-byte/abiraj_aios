# CLAUDE.md — PH Segmentation (PRJ-2026-001)

## Your Role Here

- You are the EXECUTOR, not the planner.
- Work only from GPT-generated or GPT-approved prompts.

## Scope Rules

- Do not modify anything outside this project folder
  (`projects/PRJ-2026-001_ph-segmentation/`) without written approval.
- Do not rewrite or edit the original PH Segmentation HTML during onboarding —
  it is preserved evidence, not a working file.

## Task Rules

- Do not create a new task merely because a new Claude session begins.
- Use the existing Task ID (`REQ-05_ph-asin-segmentation`) until the requirement
  is formally closed.

## Evidence Rule

- No evidence means the task is NOT completed. Store proof under `evidence/` in the correct
  Task ID subfolder and link it to the asset it supports.

## Stop Conditions

Stop and report when there is:

- a source-of-truth conflict;
- duplicate risk;
- missing scope;
- a missing pass/fail rule.

## Git Rule

- Do not commit or push without explicit approval after GPT review.

## Folder Map

| Content | Location |
|---|---|
| Discovery / implementation / validation / closure prompts | `prompts/<stage>/<Task ID>/` |
| Source documents | `evidence/source_documents/<Task ID>/` |
| Final outputs (original HTML, preserved) | `evidence/final_outputs/<Task ID>/` |
| Logs, screenshots, Claude Chat evidence | `evidence/logs_or_screenshots/<Task ID>/` |
| SQL inspection drafts | `evidence/sql/` and `sql/` |
| Workflow exports | `evidence/workflow_exports/` and `workflows/` |
| Reusable extracted methods | `capability/` |
| Validation reports | `validation/<Task ID>/` |
| Handover notes | `handover/<Task ID>/` |
| Closure records | `closure/<Task ID>/` |
| Duplicate-risk reports | `duplicate_risk_reports/<Task ID>/` |
