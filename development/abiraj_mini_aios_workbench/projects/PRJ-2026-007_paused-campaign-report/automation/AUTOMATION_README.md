# PC — Paused Campaign Report (Utharsika) — automation (REQ-09)

Weekly refresh of Utharsika's paused-Amazon-PPC dashboard. Recomputes READ-ONLY and refreshes the
`ph_task` row — keeping the **exact hand-finished dashboard**, only the data changes.

## What runs, and when

| | |
|---|---|
| Task | `PC_Weekly_PausedCampaigns` |
| When | **Wednesdays, 09:00** |
| What | Utharsika ad targets PPC automation paused that are STILL paused today |
| Reads | `public.ppc`, `public.ppc_etl_automation_log`, `public.ppc_performance` — READ-ONLY |
| Writes | 1 row in `ph_task` (`PC`, `PC_utharsika_paused_campaigns_dashboard-V1`, `assigned_user=utharsika`, `ph_priors`) |
| Entry | `run_pc_weekly.bat` → `pc_weekly_run.py` |

## How the exact look is preserved

The canonical `Utharsika_Paused_Campaigns_Report.html` is **data-driven**: its rows come from an
embedded `<script id="payload">` JSON block and every KPI is computed in the browser from those
rows. The runner reads that file as a **read-only template** and re-injects, each run:

- the payload rows (11 fields: campaign, adgroup, asin, sku, reason, pause_date, days, rule, summary,
  chips, rulenum)
- `const RUN` (run date), `TOTAL_PAUSES` (all automation pauses), `WINDOW` (perf window)

No look change — same dashboard, fresh counts.

## The method (unchanged from signed-off REQ-09-D01)

Still-paused = a successful automation pause (`ppc_etl_automation_log`, `action_type='ad_pause_logs'`,
`status='success'`, `applied_by='0'`) whose ad's **current** `ppc.record_status='paused'`. The SQL
already uses `CURRENT_DATE` (Days Paused, still-paused), so it is run-date safe with no
parameterization. `TOTAL_PAUSES` reuses the canonical CTEs + a count. The 3 rules' label / summary /
metric-chips are derived deterministically from each verbatim reason string (a WARN logs if a reason
format ever fails to parse).

## Publish grain — WEEKLY REPLACE

`task_id = PC_utharsika_paused_campaigns_dashboard-V1`, updated in place each week (backup-first,
md5-verified). One row, always current.

## Gates (fail-closed)

Row floor · collapse-vs-last-good (50%, pauses are volatile) · md5 before commit. Exit `2` = a gate
failed, nothing published, last week's dashboard stays live.

## Everyday use

```bat
run_pc_weekly.bat --dry-run   :: recompute + build, write NOTHING (safe)
run_pc_weekly.bat             :: a real weekly refresh, now
```

On failure `PC_ALERT_FAILED.txt` appears on the Desktop and clears after the next success.

## Proven (2026-07-24)

Dry-run: 69 still-paused of 88 total (was 33/41 at D01 — more pauses since); rendered payload has all
11 keys, each rule's chips parse cleanly (0 unparsed), RUN/TOTAL_PAUSES/WINDOW updated. Nothing
published.

## Related

Same pattern + credential store as the rest of the fleet.
