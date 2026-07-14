# TASK_REGISTER — PRJ-2026-008_frrc-fba-returns-root-cause

Canonical index of tasks in this project. One requirement = one Task ID.

## Tasks

| Task ID | Deliverable | Source ref | Status | Evidence | Validation |
|---|---|---|---|---|---|
| REQ-10_fba-returns-root-cause | **D01** — FRRC returns root-cause report (multi-table CTE query + 3-tab xlsx + full-screen HTML console + 19 per-PH dashboards + control-total validation), run 2026-07-14, fixed window 2026-06-14→2026-07-13: **91 returning ASINs / 105 return units**. **PUBLISHED per-PH to `ph_task` ids 216–234** (`project_code=frrc`, `ph_priors`, released). | `_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` `REQ-10-D01` (project_code `frrc`) + `HANDOFF_FRRC_REQ-10-D01.md` | **COMPLETE (technical) — PUBLISHED per-PH (216–234); VALIDATION GREEN; REVIEWER + BUSINESS SIGN-OFF PENDING** | `evidence/final_outputs/REQ-10_fba-returns-root-cause/` + `evidence/source_documents/REQ-10_fba-returns-root-cause/` | `validation/REQ-10_.../2026-07-14_validation.md` (+ `sql/REQ-10_.../validation_checks.sql`, `evidence/logs_or_screenshots/REQ-10_.../2026-07-14_import_checksum_evidence.md`, `…/2026-07-14_per_ph_publish_record.md`) · closed-out record `closure/REQ-10_.../2026-07-14_closure.md` |

## D01 — Deliverable detail
- **Query:** `sql/REQ-10_.../generate_report.sql` — `returns_agg` (by asin, reason-bucket split) LEFT
  JOIN `sales_agg` (Units Sold, responsible PH) LEFT JOIN `bridge` (`listing_data` ASIN→SKU);
  aggregate-first; `json_agg` form for the pull. Thresholds applied in the render layer, not the SQL.
- **Reason check:** `sql/REQ-10_.../reason_domain_check.sql` — run first; flag any live `reason` not in the map.
- **Validation queries:** `sql/REQ-10_.../validation_checks.sql` — completeness (91/105), bucket
  arithmetic (0 failures), one-ASIN-one-owner, return-status split (feeds open item F).
- **Data:** `evidence/final_outputs/REQ-10_.../frrc30.json` — 91 rows — **system of record**.
- **Outputs (build scripts):** `build_frrc30.py` → 3-tab threshold-driven `.xlsx`;
  `build_console.py` → full-screen HTML console with the Portfolio-holder dropdown.
- **Rendered output (imported 2026-07-14):** `FRRC_FBA_Returns_Console_REQ-10-D01_30day.html`
  (md5 `fb00ff20`, 35,625 bytes) — the canonical all-owners console; data parity with `frrc30.json`
  verified exact (91 rows / 105 returns / all tuples). The `.xlsx` + simpler grouped `.html` are still
  to import (regenerable from `frrc30.json`).
- **Per-PH dashboards (published 2026-07-14):** `evidence/final_outputs/REQ-10_.../per_ph/<PH>.html`
  (19 files + `_manifest.json`) built by `build_per_ph.py` — each locked to one holder. Published to
  `ph_task` ids 216–234; see `evidence/logs_or_screenshots/REQ-10_.../2026-07-14_per_ph_publish_record.md`.
- **Reconciliation:** 91 ASINs · 105 returns · 0 bucket failures · Flag CRITICAL 44 / HIGH 20 / OK 9 /
  N/A 18 · 19 named owners + 18 unassigned. Cross-check vs source tracker: Returns 95/101, Units 65/101
  exact (misses 1–3 higher in live). Excel recalc 0 errors.

## Onboarding (this session, 2026-07-14)
- Imported the 6-file handoff bundle (COPY-only, SHA-256 verified) → `evidence/source_documents/` +
  `evidence/final_outputs/`; wrote `SOURCE_MANIFEST.md` + import/integrity evidence note.
- Extracted the canonical SQL (HANDOFF §5) + reason-domain check + validation checks → `sql/`.
- Authored the five standing docs (README, PROJECT_HOME, SYSTEM_REFERENCE, CLAUDE, TASK_REGISTER).
- Re-verified dataset integrity independently (91/105, 0 bucket failures). **No DB SQL executed** in
  this documentation session; **no publish, no commit/push.**

## Open / next (route to Satheesvaran — do NOT decide)
- **A. Order-status set** for Units Sold — FBA-UK Completed (current) vs also Deleted/Hold/Refunded. **OPEN.**
- **B. Marketplace scope** — UK-only (current) vs all Amazon. **OPEN.**
- **C. Window length / cadence** — 30 days (current) vs the workbook's ~62-day example. **OPEN.**
- **D. Returns↔sales alignment** — `request_date`-based (current) vs align to order `order_date`. **OPEN.**
- **E. Rare reason codes** — MISSING_PARTS / SWITCHEROO / MISSED_ESTIMATED_DELIVERY / POOR_FIT /
  MISORDERED / UNAUTHORIZED_PURCHASE (currently → Unknown). **OPEN.**
- **F. Return-status filter** — count all returns (current) vs only physically-returned units.
  **The only item that changes the numbers** — pull the status split first. **OPEN.**
- **G. Unassigned owners** — attribute the 18 N/A ASINs via `listing_data`. **OPEN (engineering).**
- **REQ-10-D02 (separable, not opened):** schedule a recurring run (query already `CURRENT_DATE`-ready).
  Needs owner confirmation.
- **Reviewer gates:** Queryability (Tamil Selvan) · Technical (Sajeesan) — sign-off pending.

## Rule
A new day or Claude session does **not** create a new Task ID. Keep using
`REQ-10_fba-returns-root-cause` until D01 is formally closed; only a genuinely new requirement (with
owner confirmation) gets a new deliverable/task id.
