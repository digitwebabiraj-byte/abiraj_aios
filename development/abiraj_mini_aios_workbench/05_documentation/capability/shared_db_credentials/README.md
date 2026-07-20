# Shared DB Credentials — one global store for every project's automation

**Problem this solves.** Each automated project (EBPD, ERA, EPC, FRRC…) was carrying its own
`*_secrets.bat`. The same two logins get copied into every new project — more places to leak from, and a
password change means hunting down every copy.

**The fix.** Store the credentials **once** as Windows **user environment variables**. Every project's
runner already reads them from the environment, so they all inherit the same values and **no project needs
its own secrets file**.

## The two logins every project uses
| Purpose | Variables |
|---|---|
| **`ledsone`** — READ (live listing/price data) | `LED_PGHOST` `LED_PGPORT` `LED_PGDATABASE` `LED_PGUSER` `LED_PGPASSWORD` |
| **Warehouse** — WRITE (`tech_team_outputs.ph_task` only) | `PGHOST` `PGPORT` `PGDATABASE` `PGUSER` `PGPASSWORD` |

## Set it up (once per machine)

**If a project already has working credentials** (project 11 / EBPD does) — promote them:
```powershell
.\promote_project_secrets_to_global.ps1
```
Reads `PRJ-2026-011…\automation\ebpd_secrets.bat` and copies the values into user environment variables.
**The values are never printed, logged, or written to any tracked file** — the copy happens entirely on
your machine. Point it at a different source with `-Source "C:\path\to\other_secrets.bat"`.

**If no secrets file exists** — type them in (passwords are masked):
```powershell
.\set_global_db_credentials.ps1
```

**Then verify** (open a **new** terminal first, so it picks up the new variables):
```powershell
python verify_global_credentials.py
```
Prints `OK` / `FAIL` per connection and the server it reached — never a password.

## After setting them
- **Open a new terminal.** Environment variables are only inherited by processes started afterwards.
- **Re-register any scheduled task** so the task picks up the new environment.
- Projects keep working with **no per-project secrets file**. A project's own `*_secrets.bat`, if present,
  still wins — useful when one project needs a different login.

## Precedence (how a runner resolves a value)
```
project *_secrets.bat  (if present)   →  overrides
global user env var                   →  the normal case
built-in default in the .bat          →  non-secret host/port/db/user only
```
Passwords have **no** built-in default — if none is set, the run **aborts before writing anything**.

## Rules
- **Never commit a real credential.** Every `*_secrets.bat` is git-ignored; only `*.template.bat` is
  tracked. These scripts never write a secret into the repo.
- **Never print a password** — not to a console, a log, or a status file. The verify script prints only
  the user, host and database.
- **Rotate in one place.** Re-run `set_global_db_credentials.ps1`, open a new terminal, re-register tasks.
- The warehouse login is a **restricted** account (`temp_user`) whose only write target is `ph_task`.
  Source data stays read-only everywhere.

## Used by
`PRJ-2026-010` (EPC, weekly) · `PRJ-2026-011` (EBPD, weekly) · `PRJ-2026-012` (ERA, monthly) ·
`PRJ-2026-008` (FRRC, monthly). Any new automated project should read the environment and ship only a
`*.template.bat`.
