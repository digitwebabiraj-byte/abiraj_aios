# Capability — Monthly Report Automation Pattern (reusable)

**Extracted from:** `PRJ-2026-008_frrc-fba-returns-root-cause` → `capability/2026-07-15_monthly_run_toolkit`
(built + proven live 2026-07-15: Windows Task Scheduler, day 8, 09:00, publishes 19 per-PH dashboards).
**Status:** reusable method for any recurring governed report in this workbench.

---

## 1. When this pattern applies
Use it when a report is **already delivered and validated** and you now want it to run itself. Do **not**
use it to build a report from scratch — automation is the *last* step, never the first.

**Pre-requisites (all must be true before automating):**
| # | Must exist | Why |
|---|---|---|
| 1 | A **validated, executed** query (canonical SQL) | You automate a proven thing, not a guess |
| 2 | A **governed dataset** + control totals that reconcile to the DB | The runner asserts these every run |
| 3 | A known **publish target** + its routing key (e.g. `ph_task` + `assigned_user_team='ph_priors'`) | Wrong key = rows nobody sees |
| 4 | **Confirmed** run date + window (or an explicit owner decision to proceed provisionally) | Automating a wrong window repeats the error forever, silently |

---

## 2. The five-stage runner (copy this shape)
```
pull  ->  validate (FAIL CLOSED)  ->  render  ->  guarded publish  ->  log
```
- **Source tables READ-ONLY.** The only write is the guarded UPSERT into the *output store*.
- **Fail closed** — every check runs **before** any write. Any failure ⇒ non-zero exit, **publish nothing**.
- **One transaction**, md5-verified **before** commit, auto-rollback.

**The check list that caught real problems (reuse it):**
| Check | Catches |
|---|---|
| Unknown enum/lookup value (e.g. a new `reason` code) | Silent mis-bucketing of live data |
| Per-row arithmetic (parts sum to total) | Broken aggregation |
| Grain guard (e.g. ASIN spanning 2 accounts) | Duplicate/again-wrong rows |
| Control totals vs a direct DB count | Query drift |
| Zero rows | Publishing an empty report over a good one |
| Per-row md5 after write, before commit | Truncated / corrupted payload |

---

## 3. Hard-won rules (each of these cost real debugging)
1. **Register the task against the PERMANENT folder, never a git-worktree path.** Worktrees
   (`.claude/worktrees/...`) are deleted — the task silently breaks. Commit + sync first, then register
   from the real path.
2. **`New-ScheduledTaskTrigger` has no `-Monthly`** in Windows PowerShell 5.1. Use
   `schtasks.exe /SC MONTHLY /D <n> /ST <HH:MM>`, then harden with `Set-ScheduledTask`
   (`-StartWhenAvailable -WakeToRun`).
3. **`schtasks /Create` prompts for the Windows password** and hangs a non-interactive shell. Add
   `/RU "$env:USERNAME" /IT` (run only when logged on) to avoid storing a Windows password.
4. **Never write the DB password to a file.** Read it from an env var; ship a `set_credential.ps1`
   the **owner** runs once. Claude never persists the secret.
5. **A freshly-set user env var is invisible to already-running processes** — but Task Scheduler loads
   it from the registry at launch. Don't conclude it failed; **prove it** with a temporary
   `--dry-run` task and check `LastTaskResult = 0`.
6. **Always ship a `--dry-run` mode**, and test with a **temporary** task so the production task and
   live outputs are never touched. Delete the temp task afterwards.
7. **Check whether the source feed back-fills.** A T+1 window can be materially short (FRRC: **~12%**).
   End the window a settle-buffer before the run date.
8. **Handle roster growth** — UPSERT: UPDATE existing key, INSERT if new (and set the routing column).

---

## 4. Copy-paste prompt for Claude Code
> **AUTOMATE A RECURRING REPORT — reuse the FRRC pattern**
>
> **Reference implementation (read it first and reuse its structure):**
> `development/abiraj_mini_aios_workbench/projects/PRJ-2026-008_frrc-fba-returns-root-cause/capability/2026-07-15_monthly_run_toolkit`
> and the method doc `05_documentation/capability/2026-07-15_monthly-report-automation-pattern.md`.
>
> **Automate:** `<report / PRJ-ID>`
> **Cadence:** day `<N>` of every month at `<HH:MM>`, via **Windows Task Scheduler**
> **Window:** `<last N days | previous calendar month>`
> **Publish target:** `<schema.table>`, `<project_code=...>`, routing key `<column=value>`
>
> **Hard requirements:**
> - Source tables **READ-ONLY**; the only write is the guarded UPSERT into the output store.
> - **Fail closed**: validate before any write; abort and publish nothing on any failure. Checks must
>   include control totals vs a direct DB count, per-row arithmetic, grain guards, unknown enum values,
>   zero rows, and per-row md5 before commit. One transaction, auto-rollback.
> - **No credential in any file** — read from an env var and give me a `set_credential.ps1` to run myself.
> - **Verify the LIVE schema** of the output store before writing (columns drift from sample DDL).
> - **Check if the source feed back-fills** before fixing the run date; if it does, add a settle buffer
>   and tell me the evidence.
> - Register the task against the **permanent folder**, never a git-worktree path.
> - **Prove it**: `--dry-run`, then a **temporary** scheduled task with `--dry-run`; show
>   `LastTaskResult = 0`; delete the temp task. Do not touch the production task or live outputs.
> - **Do not lock any business rule I have not confirmed** — flag and park it for the Business Validator.
> - Commit + push + fast-forward my AIOS folder. No secret in the repo.
>
> **At the end tell me:** what runs, when, what *I* must do, and what is still open.

---

## 5. Known limits to state every time (don't hide these)
- **Windows Task Scheduler is an interim host.** Needs the PC on and logged on; **no alerting** on
  failure. **n8n / OpenFlow** is the correct long-term home for production schedules.
- **Credential at rest** in a user env var needs **Sajeesan's** approval.
- **Provisional parameters** (e.g. a settle buffer) must be labelled as such and routed to the Business
  Validator — never presented as locked.
- **And the converse — never re-open a CONFIRMED rule on the strength of a metric.** If two source
  documents disagree on whether a rule is LOCKED or HELD, that is a **source-of-truth conflict = STOP**:
  flag it and ask. (FRRC: the handoff said the 30-day window was user-confirmed/LOCKED while the morning
  doc called it a held item; it was wrongly re-opened for most of a day.)

## 6. Reference: what FRRC's automation looks like
`run_frrc_monthly.py` (runner) · `frrc_per_ph_template.html` (single UI source of truth) ·
`run_frrc_monthly.bat` (scheduler entry) · `register_scheduled_task.ps1` · `set_credential.ps1` ·
`README.md` · `logs/` + `output/` (git-ignored).
Exit codes: `0` ok · `1` config/credential · `2` integrity fail (nothing published) · `3` DB error ·
`4` publish verify failed (rolled back).
