# Prompt Record — Discovery (REQ-05_ph-asin-segmentation)

> This is a **record** of the instruction that drove this stage, captured from the execution
> session. The **verbatim, canonical prompt belongs to the GPT project chat** (the planning
> layer). To store the exact GPT prompt text, paste it into this folder alongside this record.

- **Stage:** Discovery (read-only)
- **Date:** 2026-06-25
- **Driven by:** GPT-issued controlled discovery prompt(s).

## What the prompt instructed
- Inspect the temporary intake folder read-only; do not import.
- Inventory every file: type, size, timestamps, full SHA-256, classification, confidence.
- Sensitive-information check; identify the canonical final HTML; static HTML checks.
- Reconstruct the requirement and business question (evidence-backed, no invention).
- Duplicate/parallel-truth check; decide GREEN / AMBER / RED.
- A follow-up prompt re-inspected the intake after the SQL engine + monthly prompt were added.

## Outcome
AMBER (final-HTML canonical ambiguity + missing referenced artifacts) → after Abiraj confirmed
the canonical HTML, decision moved to **GREEN**. Evidence in
`evidence/logs_or_screenshots/REQ-05_ph-asin-segmentation/`.
