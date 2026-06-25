# EOD Query Skill — Import Note (REQ-03_eod-skills)

File: `sql_generate_skill.md` (SHA-256 `6af21f652810efa2a6cb83da1e02e92ff5e578b5cb6ca689590797b03209a31f`)

## Status

STORED FOR PRESERVATION AND TECHNICAL REVIEW — NOT EXECUTED.

## What it is

The `eod-query-answerer` Claude skill: read-oriented query patterns (table relationships, JOIN
patterns, formulas, golden rules) for answering HR/management questions from the `daily_eod_log`
registry. Values come from live joins, never hardcoded.

## Execution / safety

- Do **not** run this skill or any EOD SQL against a database during onboarding.
- The original EOD work (June 2026) executed **34 database corrections** via MCP — those writes
  happened **outside this onboarding** and are **not** re-executed or re-verified here.
- Any future EOD database execution requires: a new Task ID, Sajeesan's technical approval, and
  explicit database write authorization.

Do not modify this file. Changes require a new GPT-reviewed task.
