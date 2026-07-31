# REQ-12-D01 — added 2 more users to the eBay Price Checker (2026-07-31)

Owner asked to publish the same dashboard to **two more users**, bringing the total to six:
**Sharmilan** and **Sivajitha**.

## What was done
Copied the **live** dashboard from the canonical epc row (id 264, Thinesh) into two new
`tech_team_outputs.ph_task` rows — byte-identical, not a rebuild — so the two new users see exactly what
the existing four see.

| id | assigned_user | task_id | html bytes | status | team |
|---|---|---|---|---|---|
| 528 | Sharmilan | `epc_Sharmilan_ebay_price_checker-V1` | 18,393,533 | released | ebay_priors |
| 529 | Sivajitha | `epc_Sivajitha_ebay_price_checker-V1` | 18,393,533 | released | ebay_priors |

All six epc rows after the insert: 264 (Thinesh), 299 (Jarsini), 300 (kobiga), 301 (powsteena),
**528 (Sharmilan), 529 (Sivajitha)** — every one `project_code=epc`, `assigned_user_team=ebay_priors`.

## How the names were verified (spelling is load-bearing)
There is **no `staff.users` table on `order_management_copy`** (the 2026-07-16 record's name check ran via
the Postgres MCP against a different catalog). The authoritative check here is the registry itself:
**both `Sharmilan` (5 existing tasks) and `Sivajitha` (5 existing tasks)** already appear in
`ph_task.assigned_user` with exactly that spelling — they already receive other reports through this
registry. A fuzzy scan returned that single spelling for each (no `Jarsini`/`Jasmini`-style collision), so
the exact registry spelling was used for `assigned_user` and the `task_id`.

## Method / safety (same guarded pattern as the 4-user fan-out)
- **Credentials** from the shared global store (`PGPASSWORD` env var); never hardcoded.
- **Source of the payload:** `SELECT html_content …` from id 264 — copied verbatim; the new rows'
  stored bytes equal the template's (18,393,533 B) and md5-match it.
- **Manual duplicate guard** (live has no UNIQUE on `task_id`): pre-checked both `task_id`s free, then
  **dry-run INSERT + rollback**, then the real INSERT + commit in one transaction.
- **Idempotent going forward:** both new `task_id`s follow the runner's `epc_<user>_ebay_price_checker-V1`
  convention, so the weekly job UPDATEs them in place (no duplicate rows).

## Automation kept in step
`automation/epc_weekly_run.py` — `ASSIGNED` extended from 4 to **6**
(`["Thinesh","Jarsini","kobiga","powsteena","Sharmilan","Sivajitha"]`). The Monday 10:30 run now refreshes
all six rows in the same single transaction (fails closed; the collapse/row-count/md5/routing gates are
unchanged).

## Not changed
The 2026-07-16 delivery / validation / closure records are left as the accurate history of the original
4-user delivery. REQ-12-D01 stays **CLOSED** — this is an audience addition, not new scope or a new Task ID.
