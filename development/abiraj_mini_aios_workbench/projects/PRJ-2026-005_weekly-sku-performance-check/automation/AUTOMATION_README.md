# T7 Weekly SKU Performance Check — automation (REQ-07-D02)

Turns the **closed and signed-off** REQ-07-D01 report into a self-running weekly refresh.
Nothing about the report's method changes here. The only things added are the **dynamic window**
and the **schedule** — the two items `generate_dataset.sql` and `TASK_REGISTER.md` both named as
the open item ("Scheduling / automation — FUTURE… Thursday trigger + dynamic `CURRENT_DATE` window").

## What runs, and when

| | |
|---|---|
| Task | `T7_Weekly_SKU_Performance` |
| When | **Every Thursday 11:00** |
| Window | rolling 7 days ending **yesterday** (Thu run → last Thu … last Wed) |
| Reads | `order_management_copy` — `order_transaction`, `listing_data` (READ-ONLY) |
| Writes | exactly one row: `tech_team_outputs.ph_task` `WSPC` / `WSPC_thuwaraga_SKU_Performance_Dashboard-V1` (id 135) |
| Renders | `evidence/final_outputs/T7_weekly-sku-performance-check/build_html.py` — the signed-off UI, never re-implemented |

11:00 keeps it clear of the other jobs, which share the same restricted `temp_user` account
(FRRC day-8 09:00 and ERA day-5 09:30 can both land on a Thursday).

## The five stages

```
pull  ->  validate (FAIL CLOSED)  ->  render  ->  guarded publish  ->  log
```

Every check runs **before** any write. Any failure ⇒ non-zero exit and **nothing is published** —
Thuwaraga keeps seeing the last good dashboard rather than a broken one.

| Gate | Catches |
|---|---|
| Zero rows / floor (`T7_MIN_ROWS`, default 500) | an empty or collapsed pull replacing a good report |
| Unexpected platform | a source change leaking non-UK/non-target rows in |
| Negative orders · missing SKU | broken arithmetic / unsafe grain |
| Duplicate listing key | double-counted listings |
| **Control total** vs a direct `COUNT(DISTINCT order_item_info)` | query drift |
| Family count · dashboard size | a render that produced an empty or broken page |
| **md5 of the stored HTML, before commit** | a truncated or corrupted payload (rolls back) |
| Routing (`ph_priors` + `released`) still intact after write | a report nobody can see |

Exit codes: `0` ok · `1` config/credential · `2` a data gate failed (nothing published) ·
`3` database · `4` publish verify failed (rolled back).

## Credentials

Needs **one** database. No `ledsone` connection, no secrets file — `PGPASSWORD` comes from the
global store (`05_documentation/capability/shared_db_credentials/`). Host/port/db/user come from
non-secret defaults in `run_t7_weekly.bat`. **There is no password default anywhere**: if
`PGPASSWORD` is unset the run aborts before writing.

## Everyday use

```bat
check_status.bat                             :: last 15 runs + next scheduled run
run_t7_weekly.bat --dry-run                  :: safe: validate + build, write nothing
run_t7_weekly.bat --dry-run --window 2026-07-02   :: the D01 regression test
run_t7_weekly.bat                            :: a real refresh, now
```

If a run fails, `T7_ALERT_FAILED.txt` appears on the Desktop and clears itself after the next
success. `t7_status.txt` keeps one plain-English line per run.

## The D01 regression test — and why it isn't an equality check

`--window 2026-07-02` re-runs the signed-off D01 window. It asserts **containment**: every one of
D01's 2,140 listings must still be produced. A lost row means the query drifted.

It deliberately does **not** assert D01's headline totals, because those legitimately move.
Measured 2026-07-21 against that same window:

| | D01 (2026-07-09) | Same window, 12 days later |
|---|---|---|
| Listings | 2,140 | 2,166 (+26 new, **0 lost**) |
| Orders | 170 | 183 (+13) |
| Families | 218 | 237 |

The +26 listings are real new listings (the `universe` CTE is not window-bounded). The +13 orders
are **every one an increment on a row D01 already had** (`3→4`, `0→1`) — orders that were still
settling when D01 ran at T+1.

## ⚠ Open item for the owner — the settle buffer

That +13 is **7.1% of the window's orders arriving after the report was produced**. D01 ran one day
after the window closed and undercounted by that much. FRRC hit the same class of problem (~12%)
and answered it by ending its window a settle-buffer before the run date.

**This runner keeps D01's T+1 window exactly as signed off — it does not change the business rule.**
Whether Thursday's window should end earlier (e.g. T+2/T+3) changes the numbers, so it belongs to
the Business Validator, not here. Route to **Satheewaran / Thuwaraga** with the figures above.

## Related

Same pattern as `PRJ-2026-010` (EPC) and `PRJ-2026-008` (FRRC); method doc:
`05_documentation/capability/2026-07-15_monthly-report-automation-pattern.md`.
