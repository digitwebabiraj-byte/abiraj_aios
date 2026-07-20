# AUTOMATION PLAYBOOK — turn a recurring AIOS task into a headless, no-MCP, scheduled job

Use this to convert any project's recurring deliverable into an automatic run that needs **no human and no
MCP** — it queries the live Postgres database(s) directly with `psycopg2`, builds the output, writes it to
the right place, and runs on a schedule. Working reference to copy:
**`projects/PRJ-2026-011_ebay-account-performance-dashboard/automation/`** (the EBPD dashboard).

---

## 0) Pre-flight — answer these BEFORE building
1. **Is this project's data in one of the two Postgres DBs below?** If yes → automatable exactly like EBPD.
   If any of its data comes from a **non-Postgres source** (an external API, an Amazon/eBay API, or a
   file-store MCP like `*-aios-mcp`), that part CANNOT be replaced by psycopg2 — flag it to the user; it
   needs that source's own credentials/API.
2. **What does it produce and where does it go?** (e.g. HTML/xlsx published to `tech_team_outputs.ph_task`,
   or a file, or another table.) Confirm the write target and that you have credentials to write there.
3. **How often?** (weekly Monday 09:30, daily, monthly…) and **what reporting window** (last complete month,
   rolling 7 days, etc.).

## 1) The two Postgres databases (same for every project)
| Role | Host / port / db | User | Access |
|---|---|---|---|
| Warehouse | `149.28.134.54:5435` / `order_management_copy` | `temp_user` | reads all warehouse tables **+ write to `ph_task`** |
| Ledsone ("ukvm" in pgAdmin) | `207.148.78.148:5432` / `ledsone` | `dbhub_readonly` | **read-only** |

> The MCPs your tasks use (Postgres MCP, Ledsone-db MCP) are just wrappers over these two DBs. The **same
> SQL** runs directly through psycopg2. A single script can open **both** connections (EBPD does).

**Passwords are NOT in git.** They live only in a git-ignored `automation/ebpd_secrets.bat` (env vars
`PGPASSWORD`, `LED_PGPASSWORD`). Never hard-code a password in a tracked `.py`/`.bat`; read from `os.getenv`.
If you don't have the secrets file, ask the user for the passwords and write them ONLY into that git-ignored file.

## 2) Build steps
1. Take the project's existing MCP queries and **re-run the same SQL via psycopg2** (`warehouse()` /
   `ledsone()` connections). Keep the exact business logic/definitions the project already agreed.
2. Build the output in **Python** (report / HTML / xlsx). If it publishes HTML to the **ph_task viewer**,
   the data MUST be **pre-rendered as static HTML** — the viewer runs **no JavaScript**, so anything drawn
   by JS shows blank. (See EBPD `build_html_v3.py`.)
3. Write the result to its target. For `ph_task`: pre-DELETE by `task_id` + INSERT (there is **no UNIQUE** on
   `task_id`), set the hidden required column **`assigned_user_team`**, use a **period-keyed `task_id`**
   (`<code>_<user>_<name>_<YYYY-MM>`) so a re-run refreshes the period and a new period adds a row.
4. Add the ops wrappers (copy from EBPD): `run_*.bat` (sets non-secret env, calls the git-ignored secrets
   for passwords, runs the script, logs), a plain-text **status file** line per run, and a **Desktop failure
   alert** (`*_alert.ps1`). Keep all `.bat` files **plain ASCII** (a non-ASCII char like `—` breaks cmd.exe).
5. **Schedule** it with Windows Task Scheduler pointing at the `.bat`
   (`schtasks /Create /TN "<name>" /SC WEEKLY /D MON /ST 09:30 /F /TR "\"<path>\run_*.bat\""`).

## 3) Verify before declaring done
- Run **build-only** first (no publish) and reconcile a few numbers against an independent live query.
- If it publishes HTML to ph_task: confirm it renders with **no JS** (inject the HTML via `innerHTML` in a
  browser and check the data still shows).
- Run once for real, confirm the status line says `OK` and the target updated.

## 4) Security rules (must hold before any git commit/push)
- No plaintext DB password in any tracked file (`git grep` must return nothing).
- `secrets.bat`, run logs, and generated output files are **git-ignored**.
- Read-only on all source tables; the only writes are the agreed output target.

---
**Copy the EBPD `automation/` folder as your starting template and adapt steps 1–3 to this project.**
