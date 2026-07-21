# ERA eBay Return Analysis — automation (REQ-14-D02)

Refreshes the signed-off REQ-14-D01 dashboard every month without a human. The report's method is
unchanged — the runner pulls through `build_returns_live_html.py`, the same module that produced
the signed-off June 2026 build.

## What runs, and when

| | |
|---|---|
| Task | `ERA_Monthly_Dashboard` |
| When | **Day 5 of each month, 09:30** |
| Reporting month | the **last complete calendar month** (5 Aug → July) |
| Reads | `ledsone` (the returns data) — READ-ONLY, `set_session(readonly=True)` |
| Writes | 4 rows in `tech_team_outputs.ph_task` (`ERA`, `ebay_priors`), one per assigned user |
| Renders | `evidence/final_outputs/REQ-14_ebay-return-analysis/build_returns_live_html.py` |

Day 5 gives a settle buffer after month end. 09:30 is staggered against the other jobs, which share
the one restricted `temp_user` warehouse account.

## Two databases, two roles

| DB | Role |
|---|---|
| `ledsone` (`LED_PG*`) | **the data** — returns, orders, ads, stock. Read-only. |
| warehouse (`PG*`) | **the publish target only** — `ph_task`. Never a data source. |

Both come from the global credential store
(`05_documentation/capability/shared_db_credentials/`). No secrets file is needed; if either
password is missing the run **aborts before writing anything**.

## The five stages

```
pull  ->  validate (FAIL CLOSED)  ->  render  ->  guarded publish  ->  log
```

| Gate | Catches |
|---|---|
| Credentials absent | publishing a partial or empty report |
| Zero SKUs / floor (`ERA_MIN_SKUS`, default 20) | an empty pull replacing a good dashboard |
| `returns < SKUs` | impossible arithmetic — every listed SKU must have ≥ 1 return |
| Negative refund / spend | broken money arithmetic |
| **June 2026 anchor** (144 SKUs / 153 returns) | drift from the signed-off reference build |
| Placeholder left / dashboard < 100 KB | a render that silently produced nothing |
| **md5 of each stored row, before commit** | a truncated or corrupted payload (rolls back) |
| Row count ≠ 4 assigned users | a partial publish |

Exit code `2` = a gate failed and **nothing was published** — the previous month's dashboard stays
live rather than being replaced by something broken.

## Everyday use

```bat
run_era_monthly.bat --dry-run              :: safe: validate + build, write nothing
run_era_monthly.bat --dry-run 2026-06      :: rebuild a specific month, still no publish
run_era_monthly.bat                        :: a real refresh, now
```

`--window`-style month override is the bare `YYYY-MM` argument. On failure,
`ERA_ALERT_FAILED.txt` appears on the Desktop and clears itself after the next success;
`era_status.txt` keeps one plain-English line per run.

## Publish behaviour — read this before changing it

The publish is **pre-DELETE by `task_id` + plain INSERT**, not an UPSERT: live has **no real
`UNIQUE(task_id)`**, so `ON CONFLICT (task_id)` fails. The task ids carry the reporting month
(`ERA_<user>_ebay_return_analysis_<YYYY-MM>`), so a re-run **within** a month refreshes that month's
rows while each new month adds its own. Legacy `ebra_*` ids are cleaned up in the same statement.

`assigned_user_team` is **missing from the sample DDL but must be set** (`ebay_priors`) or the
report won't group for the team.

## ⚠ Governance conflict — unresolved

The project `CLAUDE.md` still says `REQ-14`/`ERA` are *"working defaults, minted with owner
confirmation PENDING"* and *"do not publish to `ph_task` without explicit owner instruction"* —
while this task publishes monthly, unattended, as `version_status='released'`. The delivery record
says all three reviewers signed off on 2026-07-20, so the automation is very likely the correct
state and the `CLAUDE.md` wording is stale. **That is a source-of-truth conflict between two
governing documents, and the automation pattern calls it a STOP condition.** Reconcile the
`CLAUDE.md` with the sign-off before relying on this job.

## Related

Same pattern as `PRJ-2026-010` (EPC) and `PRJ-2026-008` (FRRC); method doc:
`05_documentation/capability/2026-07-15_monthly-report-automation-pattern.md`.
