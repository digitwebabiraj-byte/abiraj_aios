# REQ-19-D02 — eBay Product Performance monthly automation

Unattended monthly refresh of the eBay Product Performance report. Rebuilds the static NO-JS portal
HTML from live data and refreshes the `ph_task` rows **472–475** (`ebay_priors`) in place. Read-only
on all source data; the only write is the guarded `ph_task` refresh.

## Schedule
**2nd Wednesday of each month at 10:00** (Windows Task `EPPR_Monthly_Product_Performance`).
Chosen to satisfy "every ~30 days, on a weekday, at a clean time": the 2nd Wednesday is always a
weekday and ~monthly, and **10:00 is clear of all 9 existing fleet jobs** (which cluster at
09:00–09:45 and the Mon/Thu 10:30–11:00 slots) so it never contends for the shared `temp_user`
connection pool. The report is a rolling **30-day** window to the last complete day, so each run is a
fresh monthly snapshot.

## Files
| File | Role |
|---|---|
| `eppr_monthly_run.py` | The runner — rebuild → fail-closed gates → publish → status. |
| `render_eppr_static.py` | Regenerates the static portal HTML (imported by the runner). |
| `publish_eppr_ph_task.py` | Guarded publisher — refreshes ph_task 472–475 (imported with `commit=True`). |
| `run_eppr_monthly.bat` | Wrapper the task runs — loads secrets, runs the runner, alerts on failure. |
| `register_eppr_task.ps1` | Registers the scheduled task (run once). |
| `eppr_alert.ps1` | Desktop failure alert. |
| `check_status.bat` | Shows last status + last-good + the scheduled-task state. |
| `eppr_secrets.template.bat` | Copy to `eppr_secrets.bat` (git-ignored) and fill the two passwords. |
| `eppr_status.txt` · `eppr_last_good.json` · `eppr_run.log` | Machine-local, git-ignored, regenerated. |

## Fail-closed gates (a stale-but-correct report beats a fresh wrong one)
The runner refuses to publish (leaving the last good rows untouched) and raises a Desktop alert if:
- 0 rows returned, or
- rows < **8,000** (baseline ~11,100 — a collapsed universe), or
- rows < **60%** of the last good run, or
- the static HTML is missing / < 1 MB.

## Set up (once)
1. Credentials: either copy `eppr_secrets.template.bat` → `eppr_secrets.bat` and fill `LED_PGPASSWORD`
   (ledsone read-only) and `PGPASSWORD` (warehouse `temp_user`), **or** rely on the machine's shared
   global env store. `eppr_secrets.bat` is git-ignored — never commit a real password.
2. Register the task (PowerShell, from this folder):
   ```powershell
   .\register_eppr_task.ps1
   ```
3. Verify anytime:
   ```
   check_status.bat
   ```

## Notes
- Registered against **this main-tree path** — never a temporary git worktree (the OneDrive
  `0xC000013A` silent-no-run trap). If the repo ever moves off OneDrive, re-register.
- Credentials are read from the environment; no passwords are hardcoded in tracked code.
- Manual run for testing: `run_eppr_monthly.bat` (or `python eppr_monthly_run.py` with env set).
