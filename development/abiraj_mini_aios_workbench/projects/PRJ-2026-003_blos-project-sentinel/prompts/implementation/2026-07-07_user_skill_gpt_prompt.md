# GPT Prompt — Ledsone Centralizer User Skill File (REQ-04-D06)

Received: 2026-07-07 · Executor: Claude Code · Recorded verbatim below.

---

You are working inside the currently opened application folder.

Role:
Act as Project Tech Lead, Code Reviewer, Application Documentation Analyst, and AIOS skill-file creator.

Objective:
Create a complete, evidence-backed USER SKILL FILE for this already-built application so a new user, support staff member, developer, or LLM can understand how to use the system without asking the original developer.

Important:
Do NOT modify application code.
Do NOT create new business logic.
Do NOT invent features.
Do NOT claim anything unless it is supported by files in this project.
Do NOT create duplicate truth if an existing user guide, README, skill file, SOP, or documentation already covers the same purpose.

Before creating anything:
First scan the project and report what already exists.

Search these areas first:
- README files
- docs folders
- skills folders
- handover folders
- route files
- page/component files
- controller files
- API route files
- database/migration/model files
- config files
- authentication/role/permission files
- existing prompt/skill/capability files
- any test files or seed/sample data
- package/config files that explain framework or structure

Discovery Tasks:
1. Identify the application purpose from existing files only.
2. Identify main user roles.
3. Identify main user workflows.
4. Identify pages, routes, APIs, modules, or features.
5. Identify input/output data used by the application.
6. Identify business rules already present in code/config/docs.
7. Identify existing documentation or skill files.
8. Identify duplicate-risk if a similar user guide already exists.
9. Identify missing evidence or unclear areas.
10. Recommend the best file path for the user skill file.

If duplicate risk exists:
Do not create a new file immediately. Recommend whether to update, merge, or extend the existing file.

If no duplicate risk exists:
Create a new Markdown draft skill file in the most suitable existing documentation/skills folder.

The skill file must include these sections:

# [Application Name] — User Skill File

## 1. Purpose
## 2. Business / Operational Question Supported
## 3. User Roles
## 4. Main Workflows
## 5. Key Pages / Modules / Routes
## 6. Inputs and Outputs
## 7. Business Rules Found
## 8. What Users Must Not Do
## 9. Common User Tasks
## 10. Error / Exception Handling
## 11. Evidence Map (| Claim | Evidence File/Path | Status |)
## 12. Known Limits
## 13. Owner / Reviewer (Coordinator / Queryability Reviewer / Technical Reviewer / Business Validator)
## 14. Pass / Fail Rule
## 15. Next Step

Also create or update an evidence note if appropriate:
- docs/evidence/[application-name]-user-skill-evidence.md
or another suitable existing evidence folder.

Output format back to GPT:
1. Summary of what was scanned
2. Existing documentation found
3. Duplicate-risk result: GREEN / AMBER / RED
4. Skill file path created or recommended
5. Evidence file path created or recommended
6. Claims that are VERIFIED / PARTIAL / UNPROVEN
7. Known gaps
8. Pass/fail result
9. One next step

Stop conditions:
Stop and report without creating a file if:
- existing documentation already fully covers the same purpose
- source of truth is unclear
- app purpose cannot be identified from files
- creating a new file would duplicate an existing skill/user guide
- task requires production data changes
- task requires business rule decisions

Pass/fail:
PASS if a user skill file is created or an existing one is safely improved, all major claims have file-path evidence, duplicate risk is documented, and a new person can understand the application without verbal explanation.
FAIL if the skill file depends on guesses, chat memory, undocumented assumptions, or unsupported claims.

---

## Execution Notes (AIOS adaptation, approved by owner 2026-07-07)

- Target application: `ledsone-centralizer` (confirmed by owner).
- Skill file and evidence note are stored **inside this AIOS project** (not in the app repo),
  per the owner's instruction — paths in `../../handover/REQ-04_ledsone-centralizer-user-skill/TASK_HOME.md`.
- Task ID: REQ-04-D06 (owner chose to continue the REQ-04 stream).
- Source archive imported COPY-only from
  `C:\Users\digit\OneDrive\Desktop\Project 1 BLOS-ProjectSentinel`.
