# PH Segmentation — Handover (Dashboard UI Fix & Live Report Release)

## Project ID

PRJ-2026-001_ph-segmentation

## Task ID

REQ-20260626-002_dashboard-ui-live-report-release

## What This Records

The 26 June 2026 end-state: the PH report was rebuilt/fixed and released to the live dashboard,
delivered as a downloadable HTML file, and the monthly PostgreSQL routine was built (engine as
Step 0 + insert + data-fill + skip guards, cron `0 9 3 * *`, PostgreSQL-only). Automation
creation was deliberately **paused**.

## Evidence Status (updated 2026-06-26 — delivered HTML imported)

The delivered report is now imported + checksummed:
`evidence/final_outputs/REQ-20260626-002_dashboard-ui-live-report-release/2026-06-26_release_ph-asin_segmentation_report_2026-07.html`
(SHA-256 `6F126A4E…76FEEE87`; manifest in same folder).

**VERIFIED from the file:** 24 PHs, 1,765 priority cards, 7,855 segmentation rows (`segTotal`
sum), 686 LLL (`lllShown`), July-2026 period on a 1–30 Jun FBM window generated 26 June, and
that "Mark done" persists to browser `localStorage` only (no DB write-back).

**Still REPORTED_BY_ABIRAJ:**

* dashboard release (`ph_task` row id 5, status `released`) — DB state, DB not queried;
* byte-for-byte identity with the DB HTML — DB copy not pulled (checksum recorded for a future approved comparison);
* 57 category benchmarks — the file shows 51 distinct categories among the embedded priority cards;
* monthly routine file — not imported (only the REQ-05 engine SQL is present);
* the UI-fix *visuals* (no overlap / full-height sidebar) — not headlessly confirmable.

See `handover/REQ-20260626-002_dashboard-ui-live-report-release/TASK_HOME.md` for the
item-by-item evidence table and `validation/REQ-20260626-002_dashboard-ui-live-report-release/2026-06-26_release_validation.md`
for the read-only validation.

## What Must Not Be Done (carried forward)

* do not execute SQL;
* do not modify the live database;
* do not initialise, create or enable the automation;
* do not refresh the July report until June closes (then refresh for final values);
* do not mark any claim VERIFIED without saving the corresponding evidence;
* do not commit or push without explicit approval after GPT review.

## Operational State

See `## Current Operational State` in `PROJECT_HOME.md`.

## Future Governed Tasks

See `## Future Governed Tasks` in `PROJECT_HOME.md` — candidates only; no Task IDs assigned.

## One Next Step

GPT/Abiraj to ratify the Task ID and decide whether to import the 26 June work products as
evidence so the REPORTED_BY_ABIRAJ claims can be upgraded to VERIFIED.
