# TASK_HOME — REQ-04_ledsone-centralizer-user-skill

Project: PRJ-2026-003_blos-project-sentinel
Task ID: REQ-04_ledsone-centralizer-user-skill
Deliverable ID: **REQ-04-D06** (continues BLOS REQ-04, whose D01–D05 are registered in
`../../evidence/source_documents/REQ-04_ledsone-centralizer-user-skill/skills/`)
Owner: Abiraj · Coordinator: Varmen · Technical: Sajeesan · Queryability: Tamil Selvan
Opened: 2026-07-07
Status: IN PROGRESS

## Requirement

Daily requirement document (morning plan, canonical copy in the daily-work archive):
`C:\Users\digit\OneDrive\Desktop\DigitWeb_Works_Abiraj\07_07_2026\2026-07-07_abiraj_REQ-blos_REQ-04-D06.md`

Per the approved GPT prompt (see `../../prompts/implementation/2026-07-07_user_skill_gpt_prompt.md`):

1. Import and register the BLOS/Sentinel delivery archive (COPY-only, checksummed). **DONE 2026-07-07.**
2. Discovery-first scan of the `ledsone-centralizer` application; report existing docs and a
   GREEN/AMBER/RED duplicate-risk verdict **before** creating anything.
3. If duplicate risk clears: create the evidence-backed **user skill file** (15 mandated
   sections incl. Evidence Map with VERIFIED/PARTIAL/UNPROVEN statuses) and an evidence note.
4. Report back in the GPT prompt's 9-point output format.

## Constraints

- Do NOT modify ledsone-centralizer code/config/DB. Do NOT invent features.
- No claim without a file path. No duplicate truth (repo `docs/skill.md` stays the
  engineering log; this deliverable is user-facing).
- No git commit/push without explicit instruction.

## Deliverable Paths

| Artifact | Path |
|---|---|
| Source manifest | `../../evidence/source_documents/REQ-04_ledsone-centralizer-user-skill/SOURCE_MANIFEST.md` |
| Import checksum evidence | `../../evidence/logs_or_screenshots/REQ-04_ledsone-centralizer-user-skill/2026-07-07_import_checksum_evidence.md` |
| Duplicate-risk report | `../../duplicate_risk_reports/REQ-04_ledsone-centralizer-user-skill/2026-07-07_user_skill_duplicate_risk.md` |
| **User skill file (main deliverable)** | `../../evidence/final_outputs/REQ-04_ledsone-centralizer-user-skill/2026-07-07_ledsone-centralizer_user_skill.md` |
| Evidence note | `../../evidence/logs_or_screenshots/REQ-04_ledsone-centralizer-user-skill/2026-07-07_user_skill_evidence_note.md` |

## PASS/FAIL Rule

PASS if the user skill file exists with all 15 sections, all major claims carry file-path
evidence, duplicate risk is documented GREEN/AMBER/RED, no application file was modified, and
a new person can understand the application from the saved files alone.
FAIL if any claim rests on guesses, chat memory, or unsupported assumptions.
