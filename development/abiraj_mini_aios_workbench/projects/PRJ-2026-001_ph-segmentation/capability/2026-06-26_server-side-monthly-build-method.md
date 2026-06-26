# PH Segmentation — Server-Side Monthly Build Method (Documentation)

> Reusable method record for how the monthly PH report is built and released **server-side**,
> plus the monthly routine composition. **Status of all specifics below: REPORTED_BY_ABIRAJ** —
> no routine file, build script, or database output is saved in this project as evidence yet.
> Related reusable techniques: `capability/2026-06-25_reusable-methods.md` (esp. §5 Pre-compute-
> then-serve, §6 Parameter-free scheduled engine).

## Method (as reported 2026-06-26)

1. **Build the report server-side from `ph_segment_report`** rather than pasting a large HTML
   blob. The report is generated from the pre-computed segmentation table and written directly
   into the dashboard record — proving the production build path works without a manual paste.
2. **Release target:** `tech_team_outputs.ph_task` (reported live record: row id 5, task_id
   `ph-asin-2026-07`, status `released`).
3. **Round-trip delivery:** the downloadable HTML is pulled back out of the database so the file
   and the dashboard record are intended to be byte-for-byte identical. *(No new checksum is
   saved; this identity is REPORTED_BY_ABIRAJ.)*

## Monthly Routine Composition (as reported, BUILT — not created/enabled)

| Step | Element | Note |
|---|---|---|
| 0 | Segmentation engine | Fills `ph_segment_report`; identified as a real gap and added as Step 0 so the engine is itself automated |
| 1 | Report insert | Writes the built report into `ph_task` |
| 2 | Data-fill process | Populates supporting data |
| — | Skip guards | Completeness guard prevents segmenting an in-progress month |
| — | Schedule | cron `0 9 3 * *` (3rd of month, 09:00) to match data-loading timing |
| — | Implementation | PostgreSQL-only |

## Status & Blockers

* **BUILT** as a routine file (reported); **NOT created, NOT enabled, NOT executed.**
* **Blocker to creation:** Windows Virtual Machine Platform must be enabled (restart required).
* Completeness guard reported to correctly prevent segmenting an in-progress month.

## Evidence Gap

To upgrade this from REPORTED_BY_ABIRAJ to VERIFIED, save into the project:

* the routine file (under `sql/<Task ID>/` or `workflows/<Task ID>/`);
* the built monthly HTML + its SHA-256;
* a database release proof for the `ph_task` row.

## Do-Not

* Do not execute this routine or its SQL from this documentation record.
* Do not enable the automation.
* Do not treat the cron schedule as live until creation is approved and enabled.
