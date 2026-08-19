# BGCT monthly automation — REQ-30-D03

The keyword-gap report rebuilds and re-publishes itself **on the 20th of each month at 12:00**,
unattended and fail-closed. This file is everything you need to operate, diagnose or change it.

| | |
|---|---|
| **Windows task** | `BGCT_Monthly_Keyword_Gap` |
| **Schedule** | 20th of each month, **12:00** |
| **Registered path** | `…\projects\PRJ-2026-026_amazon-keyword-gap-sync\automation\run_bgct_monthly.bat` (**main tree**) |
| **Publishes to** | `tech_team_outputs.ph_task` **id 980** — Thuwaraga, team `ph_priors` |
| **Proven** | 2026-08-19 — `LastTaskResult 0`, 776 bulbs, 136 gaps, `last_good` md5 == the DB's md5 |
| **Writes to Amazon** | **Never.** Read-only on all source data; the single write is the guarded `ph_task` refresh. |

## Check it

```bash
check_status.bat
```

Shows the last run's status line, the last-good record, and the task's `Last Result` / `Next Run Time`.
On failure the run also drops **`BGCT_AUTOMATION_ALERT.txt` on the Desktop** — if that file is not
there, the last run did not fail.

## What one run does

1. `build_bgct_d01.py` — rebuilds `bgct_payload.json` from live data (window = the **3 most recent
   complete calendar months**, re-derived each run; never a hard-coded date).
2. **Gates** — see below. Nothing is rendered or published until every gate passes.
3. `render_bgct_dashboard.py` — rebuilds the single dashboard HTML.
4. `publish_bgct_ph_task.py --update 980` — guarded refresh, bumps `version_level`, reads the row
   back and md5-verifies it against the file on disk.
5. Writes `bgct_status.txt` + `bgct_last_good.json`; full output appended to `bgct_run.log`.

## The gates

| Gate | Threshold | Why |
|---|---|---|
| Credentials present | `PGPASSWORD` set | secrets come from the environment, never tracked code |
| Catalogue not empty | `> 0` | an empty portfolio means the PH scoping broke |
| Catalogue floor | `≥ 500` | her Bulbs category is ~776 |
| **Accounting ties** | `sum(buckets) == total` | every one of her bulbs must be accounted for; a mismatch means some vanished |
| Collapse guard | `≥ 60%` of last good | catches a partial pull from a dropped connection |
| Top-Movers | `≥ 1` | with no best sellers nothing can supply keywords |
| SQP not wholly absent | at least one account has weeks | an empty search-data window makes the report meaningless |
| **No silent account loss** | an account with weeks last run must not have 0 now | catches DCVOLTAGE quietly dropping out |
| Render size | `≥ 150 KB` | baseline ~411 KB; a truncated render must never reach the portal |

Any gate trips → **refuse to publish**, leave id 980 untouched, write `FAILED`, exit 1, raise the
Desktop alert. A stale-but-correct report beats a fresh wrong one.

### 🔴 There is deliberately NO minimum on the gap count

The other fleet jobs gate on their row count (EPPR refuses below 8,000 listings). Copying that here
would be **wrong**. This report's row count is a **backlog, not a universe** — every keyword
Thuwaraga adds *removes* a row. 136 gaps today; if she does the work it trends toward zero, which is
the project **succeeding**. A `MIN_GAPS` floor would start failing the automation at exactly the
moment it worked, and would train whoever reads the alerts to ignore them. The gates are on the
**stable universe** (her 776-bulb catalogue) and on the **integrity of the accounting** — never on
how much work is left.

## Why the 20th at 12:00

- **12:00 is the only clock slot with no other fleet job on it.** The 14 existing jobs sit at
  09:00–09:45, 10:00, 10:30, 11:00 and 11:30, and the shared `temp_user` pool intermittently throws
  *"connection slots reserved for SUPERUSER"* when jobs overlap.
- **Day 20 is clear of every other monthly job** (2, 3, 4, 5, 6, 8, and EPPR's 2nd Wednesday).
- **Amazon delivers each account's SQP on its own schedule.** DCVOLTAGE measured **25 days behind**
  on 2026-08-19. The 20th gives the newest month in the window ~3 weeks to arrive.

## Known data limitation — DCVOLTAGE search data is thin, not just late

Measured 2026-08-19 for the same window: **DCVOLTAGE 0 / 3 / 3 weeks** for May / Jun / Jul against
**LEDSone 4 / 4 / 3**. A month assembled from fewer weeks carries lower keyword volumes than a full
one, and nothing in a row admits that. So:

- the builder records `sqp_coverage` (weeks per account per month) in the payload,
- the dashboard shows a **Search-data coverage** banner naming the thin account and its week counts,
- the runner **tolerates** thin (it is normal here) but **refuses** two things: *all* accounts empty,
  and an account that had data last run arriving with none.

Do not compare keyword volumes *across* the two accounts. Compare within an account.

## Files

| File | Purpose |
|---|---|
| `bgct_monthly_run.py` | the fail-closed runner |
| `run_bgct_monthly.bat` | wrapper — loads secrets, runs, raises the alert on failure |
| `register_bgct_task.ps1` | registers the Windows task (**refuses to run from a git worktree**) |
| `bgct_alert.ps1` | Desktop failure alert |
| `check_status.bat` | one-command health check |
| `bgct_secrets.template.bat` | copy to `bgct_secrets.bat` (**git-ignored**) and fill in, or use the shared global env store |
| `publish_bgct_ph_task.py` | the guarded publisher (also usable by hand: `--dry-run`, `--update 980`) |
| `bgct_status.txt` · `bgct_last_good.json` · `bgct_run.log` | run state (generated) |

## Changing it

- **Different day/time** — edit `register_bgct_task.ps1` and re-run it (`/F` overwrites). Pick a slot
  clear of the other jobs.
- **Different rules** (Top-Moving cut-off, windows, volume floor, term count) — these all live in the
  single `RULES` dict at the top of `build_bgct_d01.py`. **They are currently unconfirmed defaults;
  Thuwaraga's answers on the decision sheet replace them.**
- **Stop it** — `schtasks /Delete /TN "BGCT_Monthly_Keyword_Gap" /F`.

## Traps this setup already avoids

- **Registering on a git worktree path** → the OneDrive `0xC000013A` "task never ran" trap. The
  registrar hard-refuses if its own folder is under `.claude\worktrees\`.
- **Publishing over another team's row** — `project_code 'BGCT'` already belongs to *"BGCT Listing
  Generator"* at **id 9** (tharsika → utharsika). This project publishes as `bgct-kwgap`, and the
  publisher refuses any row whose `project_code` + `task_id` do not match.
- **Filtering the log** — `run()` logs the **full** stdout/stderr of every step. A previous session
  grepped a build's output and missed a crash the unfiltered output showed plainly.
- **An md5 that can never match** — the runner reads the HTML in **text** mode exactly as the
  publisher does. A binary read differs by the file's 723 CRLF pairs, giving a last-good digest that
  could never equal the one stored in `ph_task`.
