# Monthly Run Prompt — Historical (REQ-20260625-001_ph-asin-segmentation)

File: `2026-06-25_monthly_run_prompt_historical.md` (SHA-256 `236f7a3e1041a80ad7919fc84ec05a6b006c965e4cf83bee6b57c53f5021f89f`)

## Status

PRESERVED AS HISTORICAL — NOT GOVERNED FOR REUSE.

## Why this warning exists

This prompt predates the governed GPT → Claude → GPT workflow. As written it:

- must **not** be executed as-is;
- **lacks complete stop conditions**;
- **lacks governed reviewer requirements**;
- **lacks a measurable pass/fail rule**;
- **lacks approved AIOS evidence paths**;
- **instructs execution of write/DDL SQL** (`ph_segment_engine.sql`).

## Required before future use

It must be **extended through a separate GPT-reviewed task** into a governed prompt (with
stop conditions, reviewers, pass/fail rule, evidence paths, and a pre-run scope check)
before it is used for any live monthly run.

Do not modify the historical prompt itself.
