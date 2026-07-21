# Scheduled task definitions — the automation fleet, backed up

**Why this folder exists.** The AIOS repo is the single source of truth for all of this work, but
until 2026-07-21 the six scheduled jobs existed **only in this machine's Windows Task Store**.
Cloning the repo elsewhere restored the code and got you nothing that runs. These exports close
that gap: rebuilding the fleet on a new machine is now a restore, not a rebuild from memory.

**No secret is in here.** Every task runs as `digit` with `LogonType=InteractiveToken`, which stores
no Windows password, and the DB passwords live in user environment variables — never in a task
definition. Verified at export: zero password matches across all six files.

## The fleet

| Task | Schedule | Project |
|---|---|---|
| `EBPD_Weekly_Dashboard` | Mondays 09:30 | PRJ-2026-011 eBay Account Performance |
| `EPC_Weekly_Price_Checker` | Mondays 10:30 | PRJ-2026-010 eBay Price Checker |
| `EPPA_Weekly_Pause_Report` | Mondays 11:00 | PRJ-2026-013 eBay PPC Pause |
| `T7_Weekly_SKU_Performance` | Thursdays 11:00 | PRJ-2026-005 Weekly SKU Performance |
| `ERA_Monthly_Dashboard` | Day 5, 09:30 | PRJ-2026-012 eBay Return Analysis |
| `FRRC_Monthly_FBA_Returns_Report` | Day 8, 09:00 | PRJ-2026-008 FBA Returns Root-Cause |

Times are staggered deliberately — they share one restricted `temp_user` warehouse account.

## Restore one task

```powershell
Register-ScheduledTask -Xml (Get-Content ".\EBPD_Weekly_Dashboard.xml" | Out-String) `
                       -TaskName "EBPD_Weekly_Dashboard" -User $env:USERNAME
```

## Restore the whole fleet on a new machine

```powershell
Get-ChildItem *.xml | ForEach-Object {
  Register-ScheduledTask -Xml (Get-Content $_.FullName | Out-String) `
                         -TaskName $_.BaseName -User $env:USERNAME
}
```

**Then, before trusting any of them:**

1. **Set the credentials first** — `05_documentation/capability/shared_db_credentials/`. Without
   them every job aborts before writing (by design), so nothing corrupts, but nothing runs either.
   **The two passwords come from Abiraj's password manager, never from this repo** — no credential
   is committed anywhere in the AIOS folder, and that is deliberate. There are two: the `ledsone`
   read-only login (`dbhub_readonly`) and the warehouse publish login (`temp_user`). If both are
   ever lost, **Sajeesan or the DB owner can reissue them** — neither is an admin credential.
2. **Check the paths.** Each XML hard-codes an absolute path to its `run_*.bat`. If the repo lives
   anywhere other than `C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS`, edit the `<Command>` element
   before registering. **Never point a task at a `.claude/worktrees/…` path** — worktrees are
   deleted and the schedule then breaks silently.
3. **Prove it with a dry-run** before letting it publish: every job supports `--dry-run`
   (EPPA gained one on 2026-07-21). Register a temporary task, confirm `LastTaskResult = 0`,
   delete the temporary task.

## Keep these in step

These are a **snapshot**, not a live mirror. Re-export after changing any schedule:

```powershell
Export-ScheduledTask -TaskName "<name>" | Set-Content ".\<name>.xml" -Encoding utf8
```

## Known trap

A job that reports `LastTaskResult = 3221225786` (`0xC000013A`) **with an empty log never ran at
all** — do not read it as a code failure. Suspected OneDrive on-demand file hydration when Task
Scheduler launches a `.bat` stored under `OneDrive\…`. Intermittent, not root-caused. See
`project-epc-weekly-automation-live` in memory.
