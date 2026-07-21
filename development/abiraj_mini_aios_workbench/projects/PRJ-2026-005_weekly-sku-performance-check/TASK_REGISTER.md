# Weekly SKU Performance Check (Table 7) — Task Register

Project: PRJ-2026-005_weekly-sku-performance-check

One task (`T7_weekly-sku-performance-check`) carries the Table 7 stream; deliverables tracked per
row (same pattern as REQ-06 D01–D03 in PRJ-2026-004). `T7` is the source's real task id
(Task 7 / Table 7 / project code `PH-2026-07-THUW07`).

| Task ID / Deliverable | Requirement | Status | Source / Handoff | Evidence Path | Validation | PASS/FAIL | Next Step |
|---|---|---|---|---|---|---|---|
| T7_weekly-sku-performance-check · **D01** | Phase-01 Reporting & Presentation: governed rolling-7-day SKU performance report for Thuwaraga across Amazon/eBay/B&Q UK — dataset rebuild query + Portfolio-Holder HTML dashboard + template-matching xlsx, for the first live window 02-Jul→08-Jul-2026; zero-order listings flagged, data-quality risks surfaced; published live to the team output store | Table 7 spec (sheet `PH-2026-07-THUW07 - Abiraj`) + `HANDOFF_weekly_sku_performance_check.md` | **COMPLETE — VALIDATED & CLOSED (2026-07-09)** | source: `evidence/source_documents/T7_weekly-sku-performance-check/HANDOFF.md` · query: `sql/T7_weekly-sku-performance-check/generate_dataset.sql` | outputs: `evidence/final_outputs/T7_weekly-sku-performance-check/Table7_Weekly_SKU_Performance_Thuwaraga.html` · `.xlsx` · `data.json` · `build_html.py` · `build_report.py` — reconciled to live DB @ snapshot 2026-07-09 14:17 (2,140 listings · 110 performing · 170 orders · 122/27/21 · **218 product families**, pack-variants merged; matches an independent direct query) — **published live:** `tech_team_outputs.ph_task` row **135** (`WSPC` / `WSPC_thuwaraga_SKU_Performance_Dashboard-V1`) — evidence in `validation/T7_weekly-sku-performance-check/2026-07-09_validation.md` · closure in `closure/T7_weekly-sku-performance-check/2026-07-09_final_closure.md` | **PASS — validated & signed off by Thuwaraga (end user) + Satheewaran (2026-07-09)** | **NONE — delivered, live and closed.** (Optional future REQ-07-D02: schedule the weekly refresh + multi-PH parameterisation.) |
| T7_weekly-sku-performance-check · **D02** | Phase-02 Automation: make the signed-off D01 report self-running — dynamic rolling-7-day window computed from the DB's `CURRENT_DATE` + Windows Task Scheduler trigger every **Thursday 11:00**, refreshing the same `ph_task` row rather than creating new ones | D01's canonical SQL comment ("set it dynamically at run time") + TASK_REGISTER item 5 ("Scheduling / automation — FUTURE") | **COMPLETE — REGISTERED & LIVE (2026-07-21)** | runner: `automation/t7_weekly_run.py` (reads the canonical `sql/…/generate_dataset.sql`, one copy only) · scheduler entry: `automation/run_t7_weekly.bat` · registration: `automation/register_t7_task.ps1` · runbook: `automation/AUTOMATION_README.md` | Five-stage fail-closed runner (pull → validate → render → guarded publish → log). Renders through the signed-off `build_html.py`; method unchanged. Gates: zero-row/floor, unexpected platform, negative orders, missing SKU, duplicate listing key, **control total vs a direct `COUNT(DISTINCT order_item_info)`**, family count, dashboard size, **md5 of the stored HTML verified before commit**, post-write routing check. Dry-run proven on live data (window 2026-07-14→20: 2,166 listings / 179 orders / 237 families; control total 179 == 179). **D01 regression** (`--window 2026-07-02`): all 2,140 signed-off listings still produced, **0 lost**. Task Scheduler proof: temporary `--dry-run` task `LastTaskResult=0`, then deleted. Nothing published during validation. | **PASS — built, proven, registered. Reviewer sign-off for D02 not yet sought.** | **Open: the settle buffer.** Re-running D01's own window 12 days later yields **+13 orders (7.1%)**, every one an increment on a row D01 already had — orders still settling when D01 ran at T+1. D02 keeps D01's window exactly as signed off; whether Thursday's window should end earlier changes the numbers and belongs to **Satheewaran / Thuwaraga**. Also open: multi-PH parameterisation (still Thuwaraga-only). |


## Items — status at closure (2026-07-09)

REQ-07-D01 is **VALIDATED & CLOSED**; the items below are resolved or moved to a future requirement.

1. **SKU-family grouping — RESOLVED & shipped.** Owner chose **merge by product** (anchored,
   reversible pack-suffix strip; `mapped_sku` not used). 218 families (138 merge >1 SKU, tagged
   `+N SKUs`). Validated & signed off (Thuwaraga + Satheewaran).
2. **Delivery channel — RESOLVED.** Delivered as the interactive HTML dashboard + xlsx and
   **published live** to `tech_team_outputs.ph_task` (row 135), matching the sibling T1–T6 dashboards.
3. **Zero-order framing — ACCEPTED.** Dashboard defaults to Active families; confirmed at sign-off.
4. **Live-DB snapshot drift — HANDLED.** Each run carries an `as of` timestamp; reconciliation is at
   the same instant.
5. **Scheduling / automation — DELIVERED as REQ-07-D02 (2026-07-21).** Thursday trigger + dynamic
   window are live (see the D02 row above). **Multi-PH parameterisation was NOT delivered** — the
   runner is still Thuwaraga-only (`PH_USER`); that remains open for a future deliverable.
6. **Postgres MCP reconnect** required before any future live re-pull (connector GUID rotates per session).

---

## 2026-07-21 — post-delivery hardening (no scope change)

Two corrections to REQ-07-D02, both proven before commit. Neither alters the signed-off method.

1. **One canonical query.** The runner carried its own paste of `generate_dataset.sql`. Both copies
   were identical, so nothing was wrong — but the `.sql` could be corrected later and this job would
   keep running the old logic unnoticed, against the workbench rule that each SQL asset has exactly
   one canonical location. `generate_dataset.sql` now binds the window (`%(ws)s` / `%(we)s`) — the
   substitution its own header always prescribed — and the runner reads that file at startup.
   A guard aborts (exit 1) if the file goes missing, stops binding the window, or regains a
   hard-coded `DATE` literal: that failure is invisible to every other gate, because the report
   would look perfectly healthy while describing **the wrong seven days**.
2. **Collapse guard** (borrowed from PRJ-2026-013 / EPPA). `MIN_ROWS` only catches a total wipe-out;
   a drop from 2,166 to 600 listings would have cleared the floor of 500 and published. The runner
   now also rejects a >40% fall against the last good run (`t7_last_good.json`, git-ignored, written
   only after a successful publish so a dry-run cannot poison it).

Re-proven after both changes, byte-identical: regression `--window 2026-07-02` reproduces all 2,140
signed-off listings (0 lost); live window 179 orders, control total 179 == 179. Negative tests:
re-hardcoded query, missing file, and a forced 10,000→2,166 collapse each abort with nothing
published. Git `6680498`, `04b6ed0`.
