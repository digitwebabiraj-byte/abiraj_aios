# PH ASIN Segmentation — automation (REQ-05)

Monthly refresh of the leader + 30 per-PH segmentation dashboards. Recomputes the whole portfolio
READ-ONLY from the live warehouse and publishes to `tech_team_outputs.ph_task`.

## What runs, and when

| | |
|---|---|
| Task | `SEG_Monthly_Segmentation` |
| When | **3rd of each month, 09:00** |
| Window | the last 4 complete Saturday-weeks vs the previous 4 (rolling; not a fixed date) |
| Reads | `public.traffic_data` + `public.order_transaction` — READ-ONLY (`set_session(readonly)`) |
| Writes | 31 rows in `ph_task` (leader + 30 per-PH), `project_code='ph-asin'`, `assigned_user_team='ph_priors'` |
| Entry | `run_seg_monthly.bat` → `seg_monthly_run.py` |

One database: the warehouse `temp_user` connection is both the data source and the publish target.
No second DB, no MCP (a scheduled task has no MCP session).

## The method (unchanged from the signed-off toolkit)

- **Conversion rule = COUNT-based** (`a.conv >= b.bcv`) — matches what is already live. A refresh,
  not a rule change.
- **Roster is dynamic** each run from `sql/00` + `sql/04` — never a hardcoded name/alloc list.
- **Big PHs auto-split by category** (`sql/02`) when over `SEG_SPLIT_THRESHOLD` (900) ASINs —
  utharsika (~1,550) and Jasmini (~1,211) run in ~5s each where the whole query times out. The
  split was proven byte-identical to the whole query on a smaller PH (0 segment/movement diffs).

## Publish grain — NEW ROW PER MONTH

`task_id = ph-asin-YYYY-MM-<PH>` (leader `ph-asin-YYYY-MM-LEADER`). Each month writes its own rows and
leaves prior months intact, so the movement history is kept (same pattern as EBPD/ERA). A **re-run of
the same month** backs up that month's rows, DELETEs them by `task_id` prefix, and re-INSERTs — it
refreshes the month, it cannot pile up duplicates. Departed holders are **reported, never
auto-deleted**.

## The gates (all fail-closed, before any write)

| Gate | Catches |
|---|---|
| PGPASSWORD / roster floor | a partial or broken run |
| Total-ASIN floor (`SEG_MIN_TOTAL`) | a broken pull dressed up as a quiet month |
| Collapse vs last good run (`SEG_MAX_DROP`, 40%) | a feed that half-empties |
| Segment tally reconciles to total | broken aggregation |
| Every roster PH produced rows | a silently dropped PH |
| md5 of every stored row before commit | a truncated/corrupted payload (rolls back) |

Exit `2` = a gate failed, **nothing published**, previous month's dashboards stay live.

## Everyday use

```bat
run_seg_monthly.bat --dry-run     :: recompute + validate + assemble, write NOTHING (safe)
run_seg_monthly.bat               :: a real monthly refresh, now
check the tail of seg_status.txt  :: one plain-English line per run
```

On failure `SEG_ALERT_FAILED.txt` appears on the Desktop and clears after the next success.

## Proven (2026-07-24)

Full 30-PH dry-run: 10,031 ASINs across 30 PHs in 192s, both big PHs auto-split, all gates passed,
distribution `HHH 205 · HHL 382 · HLH 136 · LHH 24 · LLH 159 · LLL 9,125`. That total matched an
independent whole-portfolio query to the digit. Nothing published.

## Related

Same five-stage pattern + credential store as the rest of the fleet;
method doc `05_documentation/capability/2026-07-15_monthly-report-automation-pattern.md`.
