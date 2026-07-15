# FRRC — Monthly Run Toolkit (REQ-10-D02)

Unattended **monthly** run of the FBA Returns Root-Cause report via **Windows Task Scheduler**.
Pull → validate → rebuild every Portfolio Holder's dashboard → publish to `tech_team_outputs.ph_task`.

## Cadence (as instructed)
| Setting | Value | Why |
|---|---|---|
| **Runs** | **Day 8 of every month, 09:00** | Monthly, before the 15th |
| **Window** | **Last 30 days** | D01 locked rule |
| **Settle buffer** | **7 days** (`SETTLE_DAYS`) | Amazon's FBA returns feed **back-fills**. A T+1 window is **~12% short** — measured 2026-07-15: the identical window read **105 units on the 14th and 118 on the 15th**. Ending the window 7 days before the run lets the tail land. |

So an **8 Aug** run reports **2026-07-02 → 2026-07-31** — effectively the previous month, fully settled.

## One-time setup (3 steps)

```powershell
# 1. Install the DB driver (once)
pip install psycopg2-binary

# 2. Store the DB password (once). YOU run this — the secret is never written by Claude
#    and never stored in any file in this repo.
.\set_credential.ps1

# 3. Register the scheduled task (day 8, 09:00, every month)
.\register_scheduled_task.ps1
```

Test it any time — **safe, publishes nothing**:
```powershell
.\run_frrc_monthly.bat --dry-run
```
Run the real thing on demand:
```powershell
Start-ScheduledTask -TaskName "FRRC_Monthly_FBA_Returns_Report"
```

## Files
| File | Purpose |
|---|---|
| `run_frrc_monthly.py` | The runner: pull → validate → render → guarded publish → log |
| `frrc_per_ph_template.html` | **Single source of truth for the dashboard UI** (V7: colour = severity only, reasons in words) |
| `run_frrc_monthly.bat` | Task Scheduler entry point (checks the credential, forwards args) |
| `register_scheduled_task.ps1` | Creates/updates the monthly task |
| `set_credential.ps1` | Stores `FRRC_PGPASSWORD` as a user env var (run once, by you) |
| `logs/` | One dated log per run |
| `output/` | The rendered dashboards + a dataset snapshot per run |

## Safety contract
- **Source tables are READ-ONLY** (`amazon_returns`, `order_transaction`, `listing_data`). The only write is the guarded per-PH UPSERT into the **output store** `ph_task`.
- **Fails closed.** Every check runs *before* any write; a failure aborts with a non-zero exit code and **publishes nothing** (single transaction, auto-rollback). It aborts on:
  - a **new unmapped return reason code** (would be mis-bucketed → needs Satheesvaran, item E)
  - **bucket arithmetic** mismatch
  - an ASIN **spanning both accounts** (would break the per-ASIN grain)
  - an **unrecognised account tag**
  - **control totals** disagreeing with the DB
  - **0 rows** (refuses to publish an empty report)
  - **md5 mismatch** on any row before commit
- **No credential in any file.** Read from `FRRC_PGPASSWORD`.
- **New Portfolio Holder?** Handled — the run UPDATEs existing `task_id`s and INSERTs a new row (with `assigned_user_team='ph_priors'`) if a holder appears. `version_level` auto-increments each run.

## Exit codes
`0` success · `1` config/credential · `2` integrity check failed (nothing published) · `3` DB error · `4` publish verification failed (rolled back)

## Verified
Dry-run on 2026-07-15 against the D01 window reproduced the published figures **exactly**: reason-domain 15/15 mapped · **101 ASINs / 118 units** · 0 integrity failures · control totals reconciled · **19 dashboards, 83 owned + 18 unassigned**.

## ⚠ Known limits — read before relying on this
1. **`SETTLE_DAYS=7` is an evidence-based default, not a confirmed rule.** D01's literal rule was 1 day. The change is **open item C for Satheesvaran**. The exact settle time was **not measurable** — `amazon_returns` has no ingestion timestamp and its `id` timeline is contaminated by a bulk load. To prove it: snapshot a fixed window's counts daily for ~10 days and see when they stop moving.
2. **A 30-day window starves the root-cause engine.** Root Cause needs ≥2 returns/ASIN; at 30 days only **15 of 101** ASINs qualify → **~85% read "Too few returns to evaluate"**. Coverage by window: 30 d → 15/99 · 60 d → 45/180 · 90 d → 76/234. The source workbook's own example used ~62 days. **Recommend 60–90 days** — item C, Satheesvaran. Change `WINDOW_DAYS` when he rules.
3. **Windows Task Scheduler is an interim host.** The PC must be on (the task uses `-WakeToRun` + `-StartWhenAvailable`, but a powered-off machine still misses the slot and there is **no alerting** on failure). The company's **n8n / OpenFlow** is the correct long-term home for a production schedule.
4. **Credential at rest.** The password lives in a user env var so an unattended task can read it. **Sajeesan should approve** this; a secret store would be better.
5. **Account scope.** The report still **combines LEDSone + DCVoltage** (shown and filterable, not filtered). Open item for Satheesvaran.

## Changing the rules later (one line each)
Edit the CONFIG block at the top of `run_frrc_monthly.py`:
```python
RUN_DAY     = 8    # also update register_scheduled_task.ps1 (-DaysOfMonth)
WINDOW_DAYS = 30   # -> 60 or 90 when Satheesvaran rules on item C
SETTLE_DAYS = 7    # -> whatever the 10-day measurement proves
```
