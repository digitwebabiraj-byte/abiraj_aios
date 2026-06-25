# SQL Engine — Import Warning (REQ-20260625-001_retroactive-onboarding)

> **DO NOT EXECUTE WITHOUT WRITTEN APPROVAL.**

File: `2026-06-25_ph_segment_engine.sql` (SHA-256 `0ca4818c07ae70c03226d4b8f771ed4a32ff957412f6b6594bb910fc1966239e`)

## Status

STORED ONLY — NOT EXECUTED. Imported for **preservation and technical review only**.

## Why this warning exists

- The SQL contains **write / DDL operations**.
- It **drops and recreates** `analytics.ph_segment_report` and temporary helper tables
  (`analytics._ph_windows`, `analytics._ph_cur`, `analytics._ph_prev`).
- It writes to the `analytics.*` schema.

## Execution conditions (all required before any run)

- **Sajeesan's technical approval** (technical review).
- **Explicit database write authorisation** for `analytics.*`.
- Run only via an approved, scoped connection — never on a mis-scoped/over-privileged role.

## Evidence position

- **No execution evidence was produced during onboarding.**
- The **7,855-row** reproduction claim remains **PARTIAL** until independently validated.

Do not modify the SQL file. Any change requires a new GPT-reviewed task.
