# CLAUDE.md — EOD-Skills (PRJ-2026-002)

## Your Role Here

- You are the EXECUTOR, not the planner. Work only from GPT-generated or GPT-approved prompts.

## Scope Rules

- Do not modify anything outside this project folder (`projects/PRJ-2026-002_eod-skills/`) without written approval.
- Do not modify the original EOD deliverables, work summaries or QA reports — they are preserved evidence.
- Do not "correct" the numeric discrepancies inside the deliverables; preserve them and flag for business review.

## Task Rules

- Use the existing Task ID (`REQ-03_eod-skills`) until the requirement is formally closed.
- A new day or a new Claude session does not create a new Task ID.

## Data / Execution Rules

- Do NOT execute the EOD SQL or the `eod-query-answerer` skill against any database during onboarding.
- Any future EOD database execution requires a new Task ID, Sajeesan's technical approval, and explicit DB authorization.

## Sensitivity Rule

- The HR deliverables contain named staff performance data and salary-field references (HR-CONFIDENTIAL).
  Treat as confidential; do not copy PII outside this project; do not push without explicit approval.

## Evidence Rule

- No evidence means the task is NOT completed. Store proof under `evidence/` in the correct Task ID subfolder.

## Folder Map

| Content | Location |
|---|---|
| Final deliverables (docx) | `evidence/final_outputs/<TASK>/` |
| Work summaries (D01–D04) | `handover/<TASK>/` |
| QA validation reports | `validation/<TASK>/` |
| Query skill / SQL assets | `sql/<TASK>/` |
| Source manifest + source docs | `evidence/source_documents/<TASK>/` |
| Logs / screenshots / import evidence | `evidence/logs_or_screenshots/<TASK>/` |
| Duplicate-risk reports | `duplicate_risk_reports/<TASK>/` |
| Closure records | `closure/<TASK>/` |

## Git Rule

- Do not commit or push without explicit approval (HR/PII content is involved).

## Stop Conditions

Stop on: unclear scope, source-of-truth conflict, duplicate risk, an existing asset would be overwritten,
DB execution requested, or reviewer approval required.
