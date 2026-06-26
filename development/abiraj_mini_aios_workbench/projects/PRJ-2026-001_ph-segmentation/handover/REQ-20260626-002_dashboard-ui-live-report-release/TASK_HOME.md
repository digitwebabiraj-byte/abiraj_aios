# PH Segmentation — Dashboard UI Fix & Live Report Release

## Task ID

REQ-20260626-002_dashboard-ui-live-report-release

> **ID governance note:** this is a freshly-invented dated ID supplied by Abiraj for this
> documentation update. It deviates from the project naming convention (workbench `CLAUDE.md`
> ID rule: "NOT a freshly-invented dated ID"), and no separate written-requirement file backs
> it yet. Recorded as instructed; flagged AMBER for GPT/Abiraj to ratify or rename to a
> `REQ-<n>_<deliverable>` form. See `## Open Items`.

## Project ID

PRJ-2026-001_ph-segmentation

## Relationship to REQ-05

REQ-05_ph-asin-segmentation (onboarding/preservation) is **CLOSED — PASS**. That task only
preserved and validated the pre-existing Claude-Chat work. The work recorded here — the card-UI
fix, the sidebar fix, the indicator strengthening, the full-report dashboard release, the
server-side build method, and the monthly routine build — is **new execution beyond REQ-05's
preservation scope** and therefore belongs to a new task, not a reopening of the CLOSED task.

## Purpose

Record the complete end-state of the 26 June 2026 PH Segmentation session: the report was
rebuilt and fixed, released to the live dashboard, delivered as a downloadable file, and the
monthly PostgreSQL routine was built (but not created/enabled as automation).

## Evidence Rule Applied

A claim is marked **VERIFIED** only when supported by a saved file, checksum, database result,
SQL/routine file, or existing validation evidence inside this project. Otherwise it is
**REPORTED_BY_ABIRAJ**. No execution logs, screenshots or reviewer approvals were invented.

**Update 2026-06-26:** the delivered HTML has now been imported as canonical evidence —
`evidence/final_outputs/REQ-20260626-002_dashboard-ui-live-report-release/2026-06-26_release_ph-asin_segmentation_report_2026-07.html`
(SHA-256 `6F126A4E…76FEEE87`, 457,618 bytes; copy integrity verified). Several counts are now
**VERIFIED directly from the file**; database-side and visual claims remain REPORTED_BY_ABIRAJ.
See `evidence/final_outputs/REQ-20260626-002_dashboard-ui-live-report-release/SOURCE_MANIFEST.md`.

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
3. **No automation action** was taken during this documentation update — not enabled, created or executed.
4. **The current July report was generated on partial June data.**
5. **The report must be refreshed after June closes** to produce the final July values.
6. **Per-card "Mark done" database persistence remains incomplete.** CONFIRMED by the imported file: ticks persist to browser `localStorage` with manual JSON export/import only — there is no database write-back.
7. **Task ID convention conflict (AMBER):** see the governance note at the top — GPT/Abiraj to ratify or rename.

## Current Status

RECORDED — documentation update only. No SQL executed, no live database modified, no automation
created/enabled, no commit/push performed.

## Final Task Result

AMBER (materially strengthened 2026-06-26). The delivered report is now imported and checksummed,
and its core counts are **VERIFIED from the file** (7,855 rows, 1,765 cards, 24 PHs, 686 LLL;
July-2026 period on a 1–30 Jun FBM window, generated 26 June). Still AMBER because: the dashboard
DB release and the byte-for-byte DB identity are unverified (DB not queried — prohibited), the
57-benchmark count is unproven (file shows 51), the monthly routine file is not imported, the
UI-fix *visuals* are not headlessly confirmable, and the Task ID still awaits ratification.

## One Next Step

GPT/Abiraj to (a) ratify or rename this Task ID, and (b) decide whether to save the 26 June work
products (new HTML + checksum, routine file, DB release proof) into the project so the claims can
move from REPORTED_BY_ABIRAJ to VERIFIED.

## Pass / Fail Rule

PASS if the recorded end-state matches what was reported, no claim is marked VERIFIED without
in-repo evidence, and no prohibited action (SQL execution, DB change, automation enablement,
commit/push) is taken. FAIL otherwise.
