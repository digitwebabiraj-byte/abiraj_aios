# REQ-17-D02 — Daily Sales Track, automatic daily run

Rebuilds all three REQ-17-D01 artefacts from live data every morning and refreshes the four
`ph_task` rows in place. No human, no MCP — direct `psycopg2` against both databases.

| | |
|---|---|
| Task name | `DST_Daily_Sales_Track` |
| Runs | **every day at 09:05** |
| Reports | **yesterday** (R−1), compared with R−2 and the same calendar date last year |
| Publishes to | `tech_team_outputs.ph_task` **ids 422–425**, audience `ebay_priors` |
| Fails | **closed** — a bad pull publishes nothing and yesterday's report stays live |

## Set up (once)

```powershell
copy dst_secrets.template.bat dst_secrets.bat
notepad dst_secrets.bat          # fill in the two passwords
.\run_dst_daily.bat --dry-run    # proves everything without publishing
.\register_dst_task.ps1          # elevated PowerShell
```

Then prove the schedule itself, which is a different question from whether the code works:

```powershell
Start-ScheduledTask -TaskName DST_Daily_Sales_Track
Get-ScheduledTaskInfo -TaskName DST_Daily_Sales_Track | Select LastRunTime,LastTaskResult
```

`LastTaskResult 0` = success. **`3221225786` (`0xC000013A`) with an empty log means the job never
started** — the OneDrive hydration trap, not a code failure.

## Daily check

```
check_status.bat
```

Shows the last 25 status lines and the task's next/last run.

## The gates — all must pass before anything is published

| Gate | Why |
|---|---|
| ≥ 20 rows | the universe is ~30 account × marketplace rows |
| ≥ 20 orders on the day | a normal day is 110–175 across the channel |
| money non-zero | |
| every row has a currency | money is per currency and must never blend |
| AH + PH = Active on every row | the arithmetic that defines AH |
| **reported day is in the past** | stops the partial-day defect that hit REQ-15 and REQ-16 |
| rows not collapsed > 40% vs last good run | catches a half-finished pull |
| orders not collapsed > 70% vs last good run | orders swing hard; only near-total loss is a fault |
| dashboard ≥ 20 KB | catches a truncated render |

The collapse guard uses `dst_last_good.json`, written only after a successful publish. On a fresh
machine it has no baseline and skips itself — by design; it is not a failure.

## What it does NOT do

- **No exchange rates.** `orders.total` is in each marketplace's own currency and neither database
  holds a rate. Totals are reported per currency and never summed across them.
- **No history.** Decision I — this is a snapshot that replaces. `task_id` deliberately carries no
  date, so each run updates the same four rows rather than accumulating one set per day.
- **No writes to eBay.** Read-only on every source table; the only write is the `ph_task` refresh.

## Timing note

**09:05, not 09:00.** FRRC fires at **09:00 on the 8th of each month** against the same shared
`temp_user` login; five minutes removes that overlap outright rather than leaning on the connection
retry. The run itself takes **~10 seconds**, so nothing else in the fleet comes near it.

Data-wise any morning slot would do: the reported day (R−1) is settled at midnight and `ledsone` is
live to within ~20 minutes. The time is about fleet contention, not data readiness.

⚠ **A far bigger reliability risk than the schedule is the `0xC000013A` trap** — it killed the
`UDESC` job on 2026-07-22 ("fired late at 18:39 and was externally terminated before any work
began"). It presents as a **silent no-run**. The durable fix is moving the repo off OneDrive to
`C:\dev\`, as `NEW_MACHINE_SETUP.md` recommends.

Existing fleet slots: EBPD Mon 09:30 · ERA day 5 09:30 · FRRC day 8 09:00 · EPC Mon 10:30 ·
EPPA Mon 11:00 · T7 Thu 11:00.

## Re-running a specific day

```
run_dst_daily.bat --dry-run
python dst_daily_run.py --date 2026-07-22
```

## Files

| File | |
|---|---|
| `dst_daily_run.py` | the runner — live pull, gates, rebuild, publish |
| `run_dst_daily.bat` | wrapper: loads secrets, logs, fires the alert on failure |
| `dst_secrets.template.bat` | copy to `dst_secrets.bat` (**git-ignored**) |
| `dst_alert.ps1` | drops a failure notice on the Desktop |
| `register_dst_task.ps1` | one-time Task Scheduler registration |
| `check_status.bat` | last runs + task state |
| `publish_dst_ph_task.py` | manual publisher, dry-run by default |

`dst_secrets.bat`, `*.log`, `dst_status.txt` and `dst_last_good.json` are git-ignored and will not
come back on a new machine. That is fine — the collapse guard simply skips until the first
successful publish writes a new baseline.
