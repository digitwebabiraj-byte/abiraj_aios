# REQ-16-D02 — ESNM monthly automation

Refreshes all three REQ-16-D01 artefacts from live data and republishes them to `ph_task`,
unattended, once a month.

| | |
|---|---|
| Task name | `ESNM_Monthly_Slow_No_Moving` |
| Schedule | **2nd of every month, 09:45** |
| Anchor | **last day of the previous calendar month** |
| Audience | `ebay_priors` — Thinesh · Jarsini · kobiga · powsteena (ph_task 411-414) |
| Connection | direct psycopg2, **no MCP** (a Scheduled Task has no MCP session) |
| Behaviour on failure | **fails closed** — previous report survives untouched, Desktop alert raised |

---

## Why day 2 at 09:45

**Day 2, not day 1** — the anchor is the last day of the previous month, so running on the 2nd
gives that final day a full extra day for late order syncs and eBay attribution to settle.
Because the window is a *closed calendar month*, running on the 2nd, 3rd or a week later
produces the **identical** dataset. The run date does not change the numbers.

**09:45, not 09:30** — the fleet already holds:

| Job | Slot |
|---|---|
| FRRC_Monthly_FBA_Returns_Report | day 8, 09:00 |
| **EBPD_Weekly_Dashboard** | **Mon 09:30** |
| ERA_Monthly_Dashboard | day 5, 09:30 |
| EPC_Weekly_Price_Checker | Mon 10:30 |
| T7_Weekly_SKU_Performance | Thu 11:00 |
| EPPA_Weekly_Pause_Report | Mon 11:00 |

Whenever the 2nd falls on a Monday, a 09:30 slot here would collide with EBPD on the same
shared `temp_user` warehouse login. 09:45 is clear of everything.

---

## The anchor is the point of this job

Anchoring on `today` was recorded as **defect H**. Today is still accumulating orders — at 09:00
it holds roughly **11 units against ~230 for a full day** — so a "30-day" window is 29 days plus
a stub, and the same report run twice returns different counts. Measured within one morning:

| | |
|---|---|
| listings | 11,156 → 11,176 |
| Rule 1 (Critical) | 8,067 → 8,065 |

A closed calendar month is complete and cannot move. **Two consecutive runs now produce a
byte-identical payload** (verified: `cdcc3d58…` twice).

Getting there needed a second fix: **9,222 of 11,176 rows tie** on (priority, 90-day sales,
stock), and the listings `SELECT` has no `ORDER BY`, so tied rows came back in whatever order
Postgres chose. `item_id` is now the final sort key.

EPPA hit the same class of defect and fixed it the same way.

---

## Fail-closed gates — all run BEFORE anything is written

| Gate | Threshold | Catches |
|---|---|---|
| Fetch retry | 3 attempts, 20s backoff | transient VPN / connection drops |
| Listing floor | `< 8,000` aborts | a broken pull (reference: 11,176) |
| Account floor | `< 10` account × marketplace | an account roster that failed to load |
| **Collapse guard** | `>40%` drop vs the **last good run** | a feed that silently *half*-empties — an absolute floor alone would let this through |
| Rule 1 = 0 | aborts | sales join returned nothing |
| Rule 1 = every row | aborts | sales join returned nothing, the other way |

On any abort: nothing is written, `esnm_status.json` records the reason, `esnm_run.log` keeps the
detail, and `ESNM_ALERT_FAILED.txt` appears on the Desktop (it auto-clears on the next good run).

**A stale-but-correct report beats a fresh wrong one that tells someone to end 8,000 listings.**

---

## Commands

```bat
:: safe test - rebuilds everything, never touches ph_task
run_esnm_monthly.bat --dry-run

:: rebuild for a specific anchor
python esnm_monthly_run.py --anchor 2026-06-30 --dry-run

:: health check - next/last run, last result, recent log, failure flag
check_status.bat

:: register / remove  (RUN FROM THE MAIN TREE, NOT A WORKTREE)
powershell -File register_esnm_task.ps1
powershell -File register_esnm_task.ps1 -Time 09:30 -Day 1
powershell -File register_esnm_task.ps1 -Remove
```

⚠ **Register against the main tree path, never `.claude\worktrees\…`.** A worktree can be deleted
between runs and the task then fails silently. `register_esnm_task.ps1` refuses to register from
a worktree path.

---

## Credentials

Resolution order, same chain as ERA / EPC / EPPA:

1. `esnm_secrets.bat` beside this file — git-ignored, an override only
2. **global user environment variables** — the normal path, set once via
   `05_documentation/capability/shared_db_credentials/`
3. non-secret defaults for host/port/db/user — **never a password**

**This report needs TWO databases.** `PGPASSWORD` is the warehouse (traffic + the ph_task publish
target); `LED_PGPASSWORD` is `ledsone` (listings, sales, PPC). If either is missing the run aborts
before writing anything.

---

## Data traps this job inherits

Documented in the project `CLAUDE.md`; repeated here because they cost real debugging:

- **Two databases are mandatory.** eBay organic traffic is only in the warehouse
  (`public.traffic_data`, `which_channel = 2`); the `ledsone` DB has no traffic at all. A
  warehouse-only build fails the other way — Product Title is populated on just 8.3% of items.
- **`click` is the page view**, not `impression` (which is ~250× larger).
- **Missing traffic is blank, never 0.** A zero would make Rule 9 ("views < 50") fire on every
  listing the ingestion missed.
- **`wrong_sku = 1` is NOT filtered** — 51.7% of in-scope listings carry it and they are real,
  sellable listings. Excluding them would delete half the portfolio from a dead-stock report.
- **Never read `ebay_listings.status`** — ~99% NULL and self-contradictory.
- **`ph_task` has NO unique constraint on `task_id`** despite the sample DDL claiming one, so the
  publisher SELECTs then UPDATEs. A blind INSERT would silently duplicate the report.
- **`assigned_user_team` is absent from the sample DDL but is required** — without it the row
  never reaches the audience.
- **Never assert `version_status` after publishing** — staff change it themselves.

---

## Known limitation the schedule does NOT fix

`Watchers` still has no source in either database, so **Rule 6 can never fire** regardless of how
often this runs. Closing that needs a new eBay Trading-API ingestion — outside this job.

Likewise the **11 lost eBay traffic days** understate Views; a monthly rerun does not backfill
them.
