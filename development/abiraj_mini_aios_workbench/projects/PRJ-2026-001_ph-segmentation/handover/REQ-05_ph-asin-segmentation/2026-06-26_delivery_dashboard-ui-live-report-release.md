# REQ-05 Delivery Increment — Dashboard UI Fix & Live Report Release (26 June 2026)

## Task ID

REQ-05_ph-asin-segmentation

> **Re-homing note (2026-06-26):** this record was originally filed under a separate, non-compliant
> Task ID `REQ-20260626-002_dashboard-ui-live-report-release` (a freshly-invented dated ID). Per the
> project ID-naming convention (workbench `CLAUDE.md`: "use the real requirement ID … NOT a freshly-
> invented dated ID"), it has been folded back into **REQ-05** — the real requirement this report
> delivers. The dashboard UI fix and live release are the **delivery phase** of REQ-05's segmentation
> report, not a separate requirement. Ratified by Abiraj on 2026-06-26.

## Project ID

PRJ-2026-001_ph-segmentation

## Phase

DELIVERY / RELEASE increment of REQ-05. The earlier REQ-05 closure
(`closure/REQ-05_ph-asin-segmentation/2026-06-25_final_onboarding_closure.md`) covered the
**onboarding/preservation** scope only; this increment records the subsequent delivery of the
same REQ-05 report. REQ-05 is therefore **reopened to a delivery phase**.

## What This Records

The 26 June 2026 end-state: the PH segmentation report was rebuilt and fixed, released to the
live dashboard, delivered as a downloadable HTML file, and the monthly PostgreSQL routine was
built (engine as Step 0 + insert + data-fill + skip guards, cron `0 9 3 * *`, PostgreSQL-only).
Automation creation was deliberately **paused**.

## Evidence Rule Applied

A claim is marked **VERIFIED** only when supported by a saved file, checksum, database result,
SQL/routine file, or existing validation evidence inside this project. Otherwise it is
**REPORTED_BY_ABIRAJ**. No execution logs, screenshots or reviewer approvals were invented.

The delivered HTML is imported as canonical evidence:
`evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-06-26_release_ph-asin_segmentation_report_2026-07.html`
(SHA-256 `6F126A4E…76FEEE87`, 457,618 bytes; copy integrity verified). Manifest:
`evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-06-26_release_evidence_manifest.md`.
Read-only validation:
`validation/REQ-05_ph-asin-segmentation/2026-06-26_release_validation.md`.

## Completed Items (status as of 2026-06-26, post-import)

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | PH report requirement rechecked against the canonical protocol | REPORTED_BY_ABIRAJ | Protocol docx present; no saved comparison artifact for the recheck |
| 2 | Card segment-badge vs "Mark done" button overlap fixed | PARTIAL — mechanism VERIFIED, visual REPORTED_BY_ABIRAJ | File has a dedicated "Mark done" tick mechanism separate from the segment badge; no-overlap visual not confirmable headlessly |
| 3 | Sidebar fixed so all 24 PHs are visible | PARTIAL — 24 PHs VERIFIED, full-height visual REPORTED_BY_ABIRAJ | File embeds exactly 24 distinct PHs; full-height rendering not confirmable headlessly |
| 4 | Priority, Kill, movement and escalation indicators strengthened | PARTIAL — present in code, visual REPORTED_BY_ABIRAJ | LLL escalation banner + segment/priority structures present; visual strengthening not confirmable headlessly |
| 5 | Complete report replaced the 36-card test report | VERIFIED (file is the complete report) / dashboard-replacement REPORTED_BY_ABIRAJ | File embeds 1,765 cards and full `segTotal` (7,855) — not a 36-card test; that it *replaced* the test in the DB is DB state |
| 6 | Live dashboard record published (`ph_task` row id 5, `ph-asin-2026-07`, `released`) | REPORTED_BY_ABIRAJ | DB state; DB not queried (prohibited) |
| 7 | Released report contents | MIXED | **VERIFIED:** 7,855 rows (`segTotal` sum), 1,765 cards, 24 PHs, 686 LLL (`lllShown`). **REPORTED_BY_ABIRAJ:** 57 category benchmarks (file shows 51 distinct categories among the embedded priority cards) |
| 8 | Delivered HTML byte-for-byte identical to the database HTML | REPORTED_BY_ABIRAJ | Delivered file imported + checksummed (`6F126A4E…`); the DB copy was not pulled (DB query prohibited), so identity is not yet proven. Recorded checksum is the reference for a future approved comparison |
| 9 | Monthly PostgreSQL routine built | REPORTED_BY_ABIRAJ | No routine file saved in `sql/` or `workflows/`; only the REQ-05 engine SQL is present |

### Live dashboard record (item 6, as reported)

* table: `tech_team_outputs.ph_task`
* row id: 5
* task_id: `ph-asin-2026-07`
* status: `released`

### Released report contents (item 7)

* 7,855 segmentation rows — **VERIFIED** (`segTotal` sums to 7,855: 77+479+157+17+349+6776)
* 1,765 priority cards — **VERIFIED** (1,765 card records embedded)
* 24 PHs — **VERIFIED** (24 distinct PH values embedded)
* 57 category benchmarks — **REPORTED_BY_ABIRAJ** (file shows 51 distinct categories among the embedded priority cards; full set not embedded)
* 686 LLL priority items — **VERIFIED** (`lllShown: 686`)

### Monthly routine composition (item 9, as reported)

* segmentation engine as **Step 0**
* report insert
* data-fill process
* skip guards
* cron expression: `0 9 3 * *`
* PostgreSQL-only implementation

## Open Items

1. **Automation creation is PAUSED.** Not created, not enabled, not executed.
2. **Blocker:** Windows Virtual Machine Platform must be enabled (requires restart/enablement).
3. **No automation action** was taken — not enabled, created or executed.
4. **The current July report was generated on partial June data.**
5. **The report must be refreshed after June closes** to produce the final July values.
6. **Per-card "Mark done" database persistence remains incomplete.** CONFIRMED by the imported file:
   ticks persist to browser `localStorage` with manual JSON export/import only — no database write-back.

## What Must Not Be Done (carried forward)

* do not execute SQL;
* do not modify the live database;
* do not initialise, create or enable the automation;
* do not refresh the July report until June closes (then refresh for final values);
* do not mark any claim VERIFIED without saving the corresponding evidence.

## Operational State

See `## Current Operational State` in `PROJECT_HOME.md`.

## Future Governed Tasks

See `## Future Governed Tasks` in `PROJECT_HOME.md` — candidates only; no Task IDs assigned.

## Current Status

RECORDED — delivery increment of REQ-05. No SQL executed, no live database modified, no
automation created/enabled.

## Final Result

AMBER (materially strengthened 2026-06-26). The delivered report is imported and checksummed, and
its core counts are **VERIFIED from the file** (7,855 rows, 1,765 cards, 24 PHs, 686 LLL; July-2026
period on a 1–30 Jun FBM window, generated 26 June). Still AMBER because: the dashboard DB release
and the byte-for-byte DB identity are unverified (DB not queried — prohibited), the 57-benchmark
count is unproven (file shows 51), the monthly routine file is not imported, and the UI-fix
*visuals* are not headlessly confirmable.

## One Next Step

Decide whether to import the remaining 26 June work products (monthly routine file; a DB release
proof; a pulled DB copy for the byte-for-byte comparison) so the REPORTED_BY_ABIRAJ claims can
move to VERIFIED.
