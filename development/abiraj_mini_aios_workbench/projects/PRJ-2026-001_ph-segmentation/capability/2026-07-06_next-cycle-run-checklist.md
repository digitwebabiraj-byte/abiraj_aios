# PH ASIN Segmentation — Next-Cycle Run Checklist (4-week refresh)

> **Purpose:** a plain-language runbook for refreshing the PH ASIN Segmentation report + dashboard each
> cycle (next run **3 Aug 2026**, building report_period **2026-08**). Written 2026-07-06.
>
> **Who runs it:** Abiraj (or whoever owns the run), in a **Claude Chat session against the live DB via
> the Postgres MCP connector** — this is where SQL/DDL executes. The AIOS workbench only *documents* the
> run; it does not execute it. Every live write is **backup-first and byte/md5-verified**.
>
> **Reference files in this project (inputs to copy from):**
> - Engine: `sql/REQ-05_ph-asin-segmentation/2026-07-02_ph_segment_engine_strict_rank.sql`
> - Target dashboard UI: `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_asin_dashboard_catfilter_preview.html`
> - Per-PH template + spellings: `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_per_holder_views/`
> - Current routine (OLD UI — must be fixed, see gate): `prompts/implementation/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_monthly_routine.txt`

---

## ⛔ PRE-RUN GATE — do these BEFORE running, or the cycle will regress

1. **Fix the monthly routine (highest risk).** The current `PH_ASIN_Monthly_Routine.txt` still builds the
   **OLD tabs dashboard**. If the run uses it as-is, it **overwrites the live dropdown/restyled dashboard
   back to the old layout** and drops the enrichments. Before running, update the routine so it:
   - embeds the **strict-rank** engine (`…_strict_rank.sql`);
   - builds the **new dropdown UI** (BLOCK 1 HTML shell = the catfilter build), including the allocated card,
     window-date meta strip, category-click filter, Rank/Status columns, and the Orphan-ASIN banner line;
   - pulls the Orphan count live from `analytics.v_orphan_asins`.
2. **Settle the NEW definition (Bietrick).** Live simple rule = **191 NEW**; engine returning-aware = **121**.
   Whichever is official must be the one baked into the engine before the run.
3. **Confirm the data is in.** The new window's `public.traffic_data` (4 complete Saturday-ending weeks) must
   be **fully loaded** before running, or the window will be short.
4. **Decide how it runs.** pg_cron (`SELECT * FROM pg_extension WHERE extname='pg_cron';` to check),
   Windows VM / Cloud Routine, or a manual run on the 3rd. Steps 1–2 below can be scheduled; step 3 (24 files)
   can't self-run in-DB — it needs a manual/standalone regen.

---

## THE RUN — 4 steps

### Step 1 — Rebuild the report table
- Run the strict-rank engine → it auto-detects the latest two 4-week windows and rebuilds
  `analytics.ph_segment_report` (~8k rows / 24 PHs). No dates to edit.
- **Verify:** row count sane; segment/movement counts reconcile; spot-reconcile a few PHs' listing counts
  vs `traffic_data` (target: diff 0). Note the new distribution + escalation counts.

### Step 2 — Rebuild the live dashboard (`tech_team_outputs.ph_task` id 5)
Use the **safe push method** (never touch the other 49 rows):
1. **Back up** id 5 first (e.g. `ph_task_id5_backup_<date>`); record its length + md5.
2. Build the new HTML from the routine's updated shell + the fresh report data.
3. Transfer big content **base64 → temp table → reassemble server-side → md5-verify == expected BEFORE any write.**
4. **Guarded** `UPDATE … WHERE id = 5` only (for small CSS/JS-only changes, a targeted `replace()` of just the
   changed block is safer — the ~840 KB data never moves).
5. **Verify:** live length/md5 == the approved build; 0 leftover placeholders; exactly one `<style>` pair;
   spot-check a known ASIN/SKU/PH; **render-check** in a browser (dropdown, cards, banner). Drop the temp table.

### Step 3 — Regenerate the 24 per-PH locked files
- From the finished dashboard, generate one **single-PH-locked** file per PH: filter the data object to that
  PH's index, re-index to a single-PH array, **physically remove** all other PHs' rows, hide the dropdown, auto-render.
- **Filenames = the authoritative spelling list**, parentheses kept (e.g. `Tharsiga(nelli).html`, `Tharsika(jaffna).html`).
- **Verify per file:** correct PH auto-opens, dropdown hidden, only 1 PH in the data.

### Step 4 — Distribute
- Hand each PH their own file. These are a **snapshot** for the period (they don't auto-update — regenerate each cycle).

---

## SAFETY — do NOT

- Do **not** run the OLD-UI routine unmodified (it reverts the dashboard — see the gate).
- Do **not** touch any `ph_task` row other than **id 5**.
- Do **not** auto-assign Orphan-ASIN owners (human decision only).
- Do **not** drop the retained backups (`ph_segment_report_backup_*`, id-5 backups) until Bietrick formally accepts.
- Do **not** treat the strict-rank movement rule as ratified protocol until Bietrick signs off.
- Do **not** push any live write without backup-first + byte/md5-verify.

---

## AFTER THE RUN — record it in the AIOS
Import the cycle's outputs (rebuilt dashboard HTML + checksum, the run's SQL/log, the 24 files) into this
project as the next daily increment (same Task ID `REQ-05_ph-asin-segmentation`, next `REQ-05-D…`), with a
source manifest, evidence, duplicate-risk and validation — read-only, checksum-verified, as for D06–D08.

## Readiness summary (as of 2026-07-06)
- ✅ Strict-rank engine — ready.
- ✅ Target dashboard UI + 24-file template — ready.
- ❌ Monthly routine — **NOT ready** (still old UI); must be fixed before 3 Aug.
- ⏳ NEW-definition decision, scheduling choice, and data-loaded confirmation — pending.
