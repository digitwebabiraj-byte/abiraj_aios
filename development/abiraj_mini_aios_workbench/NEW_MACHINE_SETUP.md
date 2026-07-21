# Restoring this workbench on a new machine

**Read this first if the old PC is gone, or you are moving to a new one.**

This repo is the single source of truth for the work — but a `git clone` alone does **not** give
you a running system. Four things live outside git on purpose or by omission, and this page is the
sequence that closes all four. Follow it in order; step 4 depends on 1–3.

Everything here was verified on 2026-07-21 against the live fleet.

---

## Step 1 — Python and two packages

The runners import exactly two third-party packages. Without them every job dies with
`ModuleNotFoundError` **after** the schedule fires — a failure that looks like broken automation
rather than a missing install.

```powershell
python --version            # proven on 3.14.5
pip install -r requirements.txt
```

## Step 2 — Clone the repo

```powershell
git clone https://github.com/digitwebabiraj-byte/abiraj_aios.git
```

⚠ **Think before putting it back under `OneDrive\`.** On the original machine OneDrive held locks on
`.git\worktrees\*`, so git could not clean up after itself, and it is the prime suspect for Task
Scheduler failures that leave an **empty log** and look like the job never ran (it didn't). GitHub
is already the off-machine copy, so OneDrive adds risk here without adding safety. `C:\dev\` is a
safer home.

## Step 3 — The two database passwords

**They are not in this repo, and never will be.** They come from Abiraj's password manager:

| Login | Role |
|---|---|
| `dbhub_readonly` on `ledsone` | the data — READ-ONLY |
| `temp_user` on `order_management_copy` | the publish target (`ph_task`) only |

```powershell
cd 05_documentation\capability\shared_db_credentials
.\set_global_db_credentials.ps1     # passwords are masked as you type
# then OPEN A NEW TERMINAL - env vars only reach processes started afterwards
python verify_global_credentials.py # prints OK/FAIL per connection, never a password
```

If both passwords are ever lost, **Sajeesan or the DB owner can reissue** — neither is an admin
credential.

Also confirm this machine can actually *reach* both servers (`207.148.78.148:5432` and
`149.28.134.54:5435`). If they are IP-restricted or need VPN, sort that out before step 4 —
otherwise the jobs will fail for a reason that has nothing to do with the code.

## Step 4 — Re-register the six scheduled jobs

```powershell
cd 05_documentation\capability\scheduled_tasks
```

Follow that folder's README. **Before registering, edit the `<Command>` path in each XML** if the
repo is no longer at `C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS` — the paths are absolute.
Never point a task at a `.claude\worktrees\…` path; worktrees get deleted and the schedule then
breaks silently.

---

## Prove it before trusting it

Do **not** wait for Monday to find out. Every job supports `--dry-run`: it runs every validation
gate and rebuilds the files, but writes nothing to `ph_task`.

```powershell
.\run_ebpd_weekly.bat --dry-run
.\run_t7_weekly.bat   --dry-run
.\run_eppa_weekly.bat --dry-run
```

A good run ends with `validation: all gates PASSED`. Then register **one temporary task** with
`--dry-run`, confirm `LastTaskResult = 0`, and delete it — that is the only thing that proves Task
Scheduler can resolve the environment variables at launch, which is a different question from
whether the code works.

## What will NOT come back, and does not need to

Run logs, `*_status.txt`, and the `*_last_good.json` collapse baselines are git-ignored, so the new
machine starts with no history. That is fine: the collapse guard simply skips its check until the
first successful publish writes a new baseline. No job fails because of it.

## Known trap

`LastTaskResult = 3221225786` (`0xC000013A`) **with an empty log means the job never started** —
it is not a code failure. Suspected OneDrive file hydration; see Step 2.

## Related

`05_documentation/capability/scheduled_tasks/` (the six task definitions) ·
`05_documentation/capability/shared_db_credentials/` (credential store) ·
`05_documentation/capability/2026-07-15_monthly-report-automation-pattern.md` (how the jobs are built)
