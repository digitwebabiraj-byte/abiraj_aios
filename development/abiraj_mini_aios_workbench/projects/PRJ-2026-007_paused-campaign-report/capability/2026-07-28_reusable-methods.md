# Paused Campaign Report — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques from PRJ-2026-007 (REQ-09) — a **read-only** report of
> Utharsika's Amazon PPC ad targets that the **automation engine paused** and that remain
> **paused today** (7 columns: Campaign · Ad Group · ASIN · SKU · Pause Reason · Pause Date ·
> Days Paused). Methods a future eBay/Amazon PPC pause/optimisation project could reuse — not
> project-specific facts.
> **Source:** `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md`, `automation/AUTOMATION_README.md`.

## Reusable rules / methods

### 1. "Latest event per entity" then "still-true today" — two-stage filter
For any "was X-ed by automation and is still X today" report: (a) take the **latest** pause per
target with `DISTINCT ON (record_id, source) … ORDER BY action_datetime DESC` from the event log,
then (b) keep it only if the **current** status confirms it (`ppc.record_status='paused'` at ad
grain). Re-activated targets fall out naturally. Separates *event history* from *current state*.

### 2. Automation-only isolation on the event log
Scope pauses to what the engine did with three log filters:
`action_type='ad_pause_logs'`, `status='success'`, `applied_by='0'` (`'0'` = automation, not a
human). Reuse the same triple to isolate any automated action from manual ones.

### 3. Verbatim reason, presented separately
The pause `reason` string is preserved **verbatim** in the system-of-record (`data.json`, `.xlsx`)
— never paraphrased or invented. A **cleaned presentation** (drop the perf-window clause, normalise
`≥`→`>=`, derive summary + metric chips) is derived deterministically for the dashboard only, with
no figure altered. Keep the raw and the pretty as two layers, not one.

### 4. Run-date-safe SQL (no parameterization)
`Days Paused = CURRENT_DATE − pause_date` and the still-paused test both key off `CURRENT_DATE`, so
the same query is correct on any run day with zero date edits — the enabler for scheduling.

### 5. Name-token scope key when no owner column exists
With no owner field in `ppc`, ownership is resolved by `record_name ILIKE '%utharsika%'`. Works, but
log it as an open risk (item A) rather than treating it as authoritative.

### 6. Data-driven dashboard as a read-only template
The canonical HTML computes every KPI in-browser from an embedded `<script id="payload">` JSON
block. Re-runs re-inject only the payload rows + a few constants (`RUN`, `TOTAL_PAUSES`, `WINDOW`) —
same hand-finished look, fresh numbers. Never re-paste the whole HTML.

### 7. Flag business edge-cases, never decide them
Grain (per-ASIN vs per-campaign), included set (still-paused vs all-pauses), platform, manual pauses
were all logged for the Business Validator (items A–E), not silently chosen.

## Gotchas / traps

- **`ppc.record_status` is CURRENT, not historical** — no pause history table; "still paused" and
  Days Paused are always as-of-today.
- **SB campaigns corrupt ASIN-grain rows** — Amazon maps one unrepresentative ASIN to an SB
  campaign; exclude SB. (In practice the pause log holds only Amazon ad-level events.)
- **One target → multiple performance rows** — `string_agg(DISTINCT …)` ASIN/SKU to avoid row
  duplication; one ASIN under two ad groups still yields 2 rows (32 ASINs → 33 rows).
- **Combined reasons exist** — a target can carry `Rule 1 … | Rule 3 …`; keep verbatim, parse both.
- **Amazon pauses individual ads, not whole campaigns** — "Campaign Name" is the parent, not the
  paused unit.
- **Reason-parse can fail** — the deterministic rule/summary/chip derivation logs a WARN if a reason
  string ever fails to parse; don't assume the format is stable.
- **The Amazon Ads console is the external cross-check** — a mismatch there is an upstream ETL issue,
  not a report bug.

## Key sources (schema.table.column)

- `public.ppc_etl_automation_log` — pause events: `action_type`, `status`, `applied_by`, `reason`,
  `action_datetime`, `record_id`, `parent_id`, `child_id`, `source`.
- `public.ppc` — campaign/ad-group/ad metadata + **current** status: `record_main_type`,
  `record_name`, `record_status`, `parent_id`, `child_id`, `source`.
- `public.ppc_performance` — ASIN + SKU at ad grain: `record_type='ad'`, `record_id`, `ref_id`
  (ASIN), `sku`, `source`.
- Join keys: log `parent_id/source` → campaign; log `record_id` → ad `child_id` (still-paused test)
  and → `ppc_performance.record_id` (ASIN/SKU); log `parent_id+child_id` → ad_group.
- DB: PostgreSQL `order_management_copy` (production), via the Postgres MCP, READ-ONLY.

## Automation pattern

- **Cadence:** Windows task `PC_Weekly_PausedCampaigns`, **Wednesdays 09:00**. Entry
  `run_pc_weekly.bat` → `pc_weekly_run.py`.
- **Rebuild:** recompute READ-ONLY, re-inject payload + `RUN`/`TOTAL_PAUSES`/`WINDOW` into the
  canonical HTML template. No parameterization (CURRENT_DATE-based). `--dry-run` builds but writes
  nothing.
- **Publish grain — WEEKLY REPLACE:** one `ph_task` row updated in place (backup-first, md5-verified)
  — `task_id=PC_utharsika_paused_campaigns_dashboard-V1`, `project_code=PC`,
  `assigned_user=utharsika`, `assigned_user_team=ph_priors`, in `tech_team_outputs.ph_task`
  (published row id 215).
- **Gates (fail-closed):** row floor · collapse-vs-last-good (50%, pauses are volatile) · md5 before
  commit. Exit 2 = gate failed → nothing published, last week's dashboard stays live; a Desktop
  `PC_ALERT_FAILED.txt` appears and clears on next success.
