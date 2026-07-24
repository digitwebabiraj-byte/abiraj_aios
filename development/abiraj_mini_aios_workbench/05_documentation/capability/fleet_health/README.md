# Fleet Health — one-glance status of all 12 automated jobs

Double-click **`run_fleet_health.bat`** (or run `fleet_health.ps1`). It reads Windows Task
Scheduler + each job's status file, writes `fleet_health.html`, and opens it.

## What it shows

A table of all 12 jobs — **last result** (OK / never run / FAILED), **last run**, **next run**,
**state**, and each job's **last status line** (e.g. "776 rows / 121 critical"). KPI tiles up top:
how many are OK / pending / failed.

- **OK** (green) — last scheduled run returned 0
- **never run** (amber) — scheduled but not yet fired (first runs land 27 Jul → 8 Aug)
- **FAILED** (red) — non-zero exit; open that job's `*_run.log`. A `0xC000013A` with an empty
  status line means it never started (suspected OneDrive), not a code failure.

Run it any morning to confirm the fleet is healthy. The `.html` is regenerated each run
(git-ignored); the generator + this README are the tracked assets.
