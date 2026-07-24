# ZSFO — Zero Sales Full Optimization (Utharsika) — automation (REQ-08)

Weekly refresh of Utharsika's Amazon-UK zero-sale dashboard. Recomputes READ-ONLY from the live
warehouse and refreshes the `ph_task` row.

## What runs, and when

| | |
|---|---|
| Task | `ZSFO_Weekly_ZeroSales` |
| When | **Mondays, 08:00** (clear of EBPD/EPC/EPPA at 09:30/10:30/11:00) |
| Window | `[run_date-30, run_date-1]`, current day excluded — rolling, computed from the run date |
| Reads | `public.traffic_data`, `public.order_transaction`, `public.vendor_sales`, listing/stock — READ-ONLY |
| Writes | 1 row in `ph_task` (`ZSFO`, `ZSFO_utharsika_zero_sales_dashboard-V1`, `assigned_user=utharsika`, `ph_priors`) |
| Entry | `run_zsfo_weekly.bat` → `zsfo_weekly_run.py` → drives the signed-off `build_html.py` |

## The method (unchanged from the signed-off REQ-08-D01)

Zero-sale = 0 units in the window across `order_transaction` (FBA+FBM, Completed) **AND**
`vendor_sales` (1P, OVERLAP match). The runner computes `run_date` + the five weekly traffic
buckets from `CURRENT_DATE` and substitutes the canonical SQL's hardcoded literals — the one
"scheduling not wired" gap from SYSTEM_REFERENCE. A guard aborts if any reference literal survives
substitution (that would silently report the wrong week).

Reuses the signed-off assets with no duplication: reads `generate_dataset.sql`, maps its 21 output
columns to the `data.json` short keys, and runs the existing `build_html.py` via env-var path
overrides (`ZSFO_DATA` / `ZSFO_OUT`).

## Publish grain — WEEKLY REPLACE

`task_id = ZSFO_utharsika_zero_sales_dashboard-V1`, updated in place each week (backup-first,
md5-verified), matching the other weekly jobs and how ZSFO was first published (id 167). One row,
always current.

## The gates (fail-closed, before any write)

| Gate | Catches |
|---|---|
| PGPASSWORD set | a run with no publish credential |
| Universe floor (`ZSFO_MIN_UNIVERSE`) | a broken universe pull |
| Zero-row floor | publishing an empty report over a good one |
| Collapse vs last good (`ZSFO_MAX_DROP`, 40%) | a feed that half-empties |
| Reference (only with `--date 2026-07-10`) | logic drift — must reproduce 1,250 zero-sale rows exactly |
| Mapped-key check + md5 before commit | broken column mapping / truncated payload (rolls back) |

Exit `2` = a gate failed, nothing published, last week's dashboard stays live.

## Everyday use

```bat
run_zsfo_weekly.bat --dry-run                :: recompute + build, write NOTHING (safe)
run_zsfo_weekly.bat --dry-run --date 2026-07-10 :: reproduce the signed-off reference (1,250 rows)
run_zsfo_weekly.bat                          :: a real weekly refresh, now
```

On failure `ZSFO_ALERT_FAILED.txt` appears on the Desktop and clears after the next success.

## Proven (2026-07-24)

`--date 2026-07-10` reproduced the deliverable exactly (1,250 zero-sale rows); universe 1,720 vs
1,719 is a +1 live-drift (drift check, not equality). Fresh window (24 Jun–23 Jul) gave 1,289
zero-sale, dashboard built via the reused builder, nothing published.

## Related

Same pattern + credential store as the rest of the fleet;
method doc `05_documentation/capability/2026-07-15_monthly-report-automation-pattern.md`.
