# EPC — Weekly Auto-Refresh (REQ-12)

Unattended **weekly** run of the eBay Price Checker via **Windows Task Scheduler**.
Pull live prices → validate → rebuild the dashboard → publish to all 4 users' `ph_task` rows.
**No human, no MCP, no manual step.**

## Cadence
| Setting | Value | Why |
|---|---|---|
| **Runs** | **Every Monday, 07:00** | Prices move daily (competitor repricing + manual changes); a week-old "Too high" flag is often wrong. Monday morning = fresh list for the week. |
| **Window** | **Live / current state** | This is a "what is mispriced right now" report — no reporting period, no settle buffer needed (unlike FRRC/ERA). |
| **Publishes to** | `ph_task` ids **264 (Thinesh), 299 (Jarsini), 300 (kobiga), 301 (powsteena)** | Updated **in place** — same ids, same links; `version_level` bumps each run. |

## One-time setup (3 steps)

```powershell
# 1. Install the DB driver (once)
pip install psycopg2-binary

# 2. Store the credentials (once). YOU do this — no password is ever written by Claude
#    or committed. Copy the template, fill it in, save as epc_secrets.bat:
copy epc_secrets.template.bat epc_secrets.bat
notepad epc_secrets.bat      # fill LED_* (ledsone) + PGPASSWORD (warehouse)

# 3. Register the weekly task (Monday 07:00)
.\register_scheduled_task.ps1
```

> The `ledsone` login is the same one **project 11 (EBPD)** already uses — see its `ebpd_secrets.bat`.

**Test it any time — safe, publishes nothing:**
```powershell
.\run_epc_weekly.bat --dry-run
```
**Run the real thing on demand:**
```powershell
Start-ScheduledTask -TaskName "EPC_Weekly_Price_Checker"
```
**Is it healthy?**
```powershell
.\check_status.bat
```

## Files
| File | Purpose |
|---|---|
| `epc_weekly_run.py` | The runner: pull → validate → build → guarded publish → log |
| `epc_build_html.py` | **Single source of truth for the dashboard UI** (V3: Export-CSV + taller table). Edit the template here only — never fork it |
| `run_epc_weekly.bat` | Task Scheduler entry point (loads secrets, runs, logs, fires the alert) |
| `register_scheduled_task.ps1` | Creates/updates the weekly task (safe to re-run) |
| `epc_secrets.template.bat` | Credential template → save as `epc_secrets.bat` (git-ignored) |
| `epc_alert.ps1` | Desktop alert on failure, auto-clears on success |
| `check_status.bat` | Last 15 runs + open-alert state + next scheduled run |
| `epc_status.txt` | One plain-English line per run (git-ignored) |
| `epc_run.log` | Full run log, newest at the bottom (git-ignored) |
| `epc_auto_dashboard.html` | The dashboard the last run published (git-ignored) |

## Safety contract
- **Source data is READ-ONLY.** `listings.*` / `inventory.*` on `ledsone` are only ever read. The single
  write is the guarded UPSERT into the **output store** `tech_team_outputs.ph_task`.
- **Fails closed.** Every gate runs *before* any write; a failure exits non-zero and **publishes nothing**,
  so the last good dashboard stays live. It aborts on:
  - **0 rows** (refuses to publish an empty report)
  - fewer than **`EPC_MIN_ROWS`** rows (default 50,000 — catches a broken pull; expect ~126k)
  - **status counts not reconciling** to the row count
  - the **DATA MISSING split** (no-comparator + bundle) not reconciling
  - any row with a **missing/non-positive eBay price** or no account
  - the dashboard **failing to render** (placeholder left, or < 1 MB)
  - **missing credentials**
- **One transaction.** All 4 users are updated together; any error rolls the whole thing back.
- **No credential in any tracked file.** Everything comes from `epc_secrets.bat`, which is git-ignored.
- **Connection retries.** The `temp_user` pool intermittently returns *"too many clients"* — the runner
  retries 5× with backoff before giving up (and even then, publishes nothing).
- **New user added?** Handled — the run UPDATEs the 4 known `task_id`s and INSERTs a row (with
  `assigned_user_team='ebay_priors'`) if a new user appears in the list.
- **Never reprices.** The report recommends only; it writes nothing to any listing.

## Business rules (owner-confirmed — change them in `epc_weekly_run.py` only)
`target = Amazon (amazon Ledsone, sub_source 8, LOWEST) × 0.90` → else `website (Shopify 104/108) × 1.10`
→ else `bundle = Σ(component × pack qty)` → else **DATA MISSING**. Tolerance **±£0.50** below the **£20**
band, **±£1.00** at/above. Priority by money-at-risk (**≥£5** High, **≥£2** Medium). SKU-normalised per the
AIOS KB: `all_list=1`, Amazon `_` suffix, `ENC`→`sku_original`, `<char>PK` pack qty.

⚠ **Status is item-price only** (shipping accepted at sign-off) — the dashboard keeps its
*"rank, don't reprice"* banner. A shipping-aware Status would be a separate change.

## What a healthy run looks like
```
[EPC] start  publish=True
[EPC] pulled 130,850 live eBay UK+DE listing rows from ledsone
[EPC] kept 126,xxx rows across the 13 named accounts (dropped 4,xxx from unnamed accounts)
[EPC]   Normal 21,xxx | Too high 40,xxx | Too low 22,xxx | No target 42,xxx (...)
[EPC] validation: all gates PASSED
[EPC] dashboard built: epc_auto_dashboard.html (18,xxx,xxx bytes)
[EPC]   updated Thinesh    -> id 264 (version 5)
[EPC]   updated Jarsini    -> id 299 (version 2)
[EPC]   updated kobiga     -> id 300 (version 2)
[EPC]   updated powsteena  -> id 301 (version 2)
[EPC] published to ph_task for 4 users
```
Row counts drift week to week — that is the point (the catalogue moved 130,336 → 130,850 within one day
on 2026-07-16).

## Status
Scripts written, syntax-checked, fail-closed path tested, the SQL validated live against `ledsone`
(130,850 rows / 16 account×site pairs) and the dashboard renderer verified. **The DB-connected end-to-end
run is untested until `epc_secrets.bat` exists** — the first `--dry-run` after filling it in is the real
proof. It cannot publish anything until then (it aborts on missing credentials).
