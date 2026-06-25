# Prompt Record — Validation (REQ-05_ph-asin-segmentation)

> Record of the instruction that drove this stage, captured from the execution session. The
> verbatim, canonical prompt belongs to the GPT project chat. Paste the exact GPT prompt here to
> store it.

- **Stage:** Validation / pre-commit audit (read-only)
- **Date:** 2026-06-25
- **Driven by:** GPT-issued final pre-commit audit prompt.

## What the prompt instructed
- Verify the complete folder structure, filenames, identifiers, links and canonical asset
  locations before any Git commit.
- Confirm registers agree (PROJECT_REGISTER / TASK_REGISTER / PROJECT_HOME / TASK_HOME).
- Confirm reviewer-name consistency, checksums match the manifest, no duplicate/parallel truth,
  no unwanted/secret files, and that an unknown developer could continue from saved files.

## Outcome
Audit informed closure. The four reviewer validations (Technical/Queryability/Business/
Coordinator) and the final closure are stored in `validation/` and `closure/` for this task.
