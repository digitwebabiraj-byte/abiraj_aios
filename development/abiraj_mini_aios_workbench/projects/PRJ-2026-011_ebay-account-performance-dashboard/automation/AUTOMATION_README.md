# EBPD — Weekly Auto-Refresh (REQ-13-D02)

Runs the eBay Account Performance Dashboard **automatically every week, headless — no MCP, no human**.

## What it does (each run)
1. Computes the reporting window dynamically — the **last complete calendar month** relative to run day
   (so a run any week in July reports June; the first run in August reports July). LM + LY follow.
2. Discovers the **active eBay accounts** for that month from `order_transaction` (no hardcoded list).
3. Pulls, via direct psycopg2 (no MCP): Sales (`SUM(order_total)`, Completed), ON_SITE advertising (+TACOS),
   whole-account conversion (`traffic_data which_channel=2`), active listings + stock, and — from the
   **ledsone DB** — New Listings (`listings.ebay_listings.created_at`).
4. Builds the HTML dashboard (reuses `build_html_v3.py`'s template — same look as the live one).
5. Publishes per-user to `tech_team_outputs.ph_task` (Thinesh, Jarsini, kobiga, powsteena; `ebpd`,
   `ebay_priors`, `released`) via pre-DELETE + INSERT.

## Files
- `ebpd_weekly_run.py` — the pipeline. `build_html_v3.py` — the HTML template it reuses.
- `run_ebpd_weekly.bat` — wrapper the scheduler calls (sets env, runs the script, logs to `ebpd_run.log`).
- `ebpd_secrets.template.bat` — copy to **`ebpd_secrets.bat`** and fill the ledsone connection (git-ignored).

## Credentials
- **Warehouse** (reads + `ph_task` write): the `temp_user` connection (set in `run_ebpd_weekly.bat`).
- **Ledsone** (New Listings only): set `LED_PGHOST / LED_PGPORT / LED_PGDATABASE / LED_PGUSER /
  LED_PGPASSWORD` in `ebpd_secrets.bat`. **If unset, the run still works but New Listings show 0.**

## Manual test
```
cd automation
python ebpd_weekly_run.py --no-publish     # build only, writes ebpd_auto_dashboard.html, no ph_task write
python ebpd_weekly_run.py                  # full run: build + publish to ph_task
```

## Schedule (Windows Task Scheduler)
Registered as a weekly task calling `run_ebpd_weekly.bat`. To (re)create it:
```
schtasks /Create /TN "EBPD_Weekly_Dashboard" /SC WEEKLY /D MON /ST 08:00 /F ^
  /TR "\"<full path>\run_ebpd_weekly.bat\""
```
Runs when the machine is on. (No always-on server needed, per owner instruction — this desktop hosts it.)

## How to know it ran (or didn't) each week
Three ways, easiest first:
1. **Double-click `check_status.bat`** — shows the last several runs in plain English plus the
   Windows Scheduler's own Last-Run / Result / Next-Run. This is the one-stop check.
2. **Open `ebpd_status.txt`** — one line per run, e.g.
   `[2026-07-27 09:30]  OK  |  July 2026  |  22 rows  |  GBP 95,347.92  |  New Listings 249  |  PUBLISHED to 4 users`
   A crash instead writes `FAILED (exit N)  |  see ebpd_run.log`. **No line at all for a Monday = it never ran**
   (PC was off at 09:30 and hadn't caught up yet).
3. **Task Scheduler** → task `EBPD_Weekly_Dashboard` → *Last Run Result* `0` = success.

**On failure you also get an automatic alert:** a file `EBPD_ALERT_FAILED.txt` appears on the **Desktop**
(plus a popup) with the exit code and what to do. It **clears itself** after the next successful run.
The logic lives in `ebpd_alert.ps1` (called by the runner). For the actual error text, open `ebpd_run.log`
(full run output, newest at the bottom).

Note: keep the `.bat`/secrets files **plain ASCII** — non-ASCII (e.g. an em-dash in a comment) breaks
cmd.exe parsing and pollutes the run with spurious errors.

## Notes
- Numbers reflect **live data at run time**, so they can differ slightly from an earlier manual snapshot as
  orders settle — this is the point of an auto-refresh.
- Housekeeping: the warehouse password currently sits in `run_ebpd_weekly.bat`; move it into
  `ebpd_secrets.bat` (also git-ignored) if you want zero plaintext creds in tracked-adjacent files.
