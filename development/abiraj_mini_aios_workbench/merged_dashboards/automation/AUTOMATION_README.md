# Merge Dashboard Automation

Self-contained, fleet-pattern refresh for the eBay unified dashboard. **Does NOT touch the 3
source tasks** — it reuses their build functions read-only and writes only into `merged_dashboards/`.

## What it does
`merge_monthly_run.py`:
1. **EPPR** — imports `render_eppr_dashboard`, redirects its output paths into a temp dir, calls
   `build_records()` (live DB pull, **no publish**) → fresh EPPR data.
2. **ESNM** — imports `build_esnm_d01` + `render_esnm_dashboard`, redirects outputs, runs
   `fetch()`/`assemble()` + `build()` + `render.main()` (live pull, **no publish**) → fresh ESNM data.
3. **ERA** — v1 carries the last-good `era_merge.json` (see caveat).
4. Runs the emitters (`EPPR_SRC`/`ESNM_SRC` env → fresh files) then `build_merged.py`.
5. Fail-closed gates (row floors, HTML size); writes `merge_status.txt`; `MERGE_ALERT.txt` on failure.

Run: `python merge_monthly_run.py` · dry-run: `python merge_monthly_run.py --dry-run`
PC wrapper: `run_merge_monthly.bat` (reads global env DB creds, like the fleet).

## ⚠️ STATUS — built, NOT yet proven
- **Not scheduled yet.** Per fleet discipline, it must be **dry-run proven in an environment with
  DB credentials** before registering a task. That could not be done from the authoring session
  (no DB access there). First step on the run machine:
  ```
  run_merge_monthly.bat --dry-run
  ```
  Expect ~11k EPPR + ~11k ESNM rows and `OK(dry-run)` in `merge_status.txt`.
- **ERA is not live in v1.** Its build feeds HTML only (structured data is a frozen mockup xlsx),
  so ERA carries its last snapshot. Making ERA live = reuse `build_returns_live_html.pull()` +
  map its columns → `era_merge.json` (a flagged follow-up).

## Open decisions
- **Schedule:** monthly after the 5th (all 3 sources refreshed). Register as a PC task
  (`MERGE_Monthly_Dashboard`) once dry-run passes — same RandomDelay/RestartOnFailure as the fleet.
- **Cloud (`aios-live`):** the merge builds a LOCAL HTML file. On PC that's the viewable output.
  In the cloud the file is ephemeral → the cloud job needs a **publish target** (upload as an
  Actions artifact, or publish to `ph_task`). Decide before adding `merge.yml`.
- **PC is the natural home** for now: it produces the openable HTML on disk each month.
