# REQ-05 Delivery Increment — Final-June Refresh, Report Validation & Data-Quality Review (30 June 2026)

## Task ID

REQ-05_ph-asin-segmentation

> This is the **second delivery increment** of REQ-05, recording the 30 June 2026 Claude Chat
> session. It is **not** a new Task ID: per the workbench `CLAUDE.md` ID-naming rule ("a new day or
> a new Claude session does NOT create a new Task ID"), the post-June refresh is the delivery phase
> of the same REQ-05 segmentation report. It directly completes the item the 26 June increment left
> open: *"The report must be refreshed after June closes to produce the final July values."*

## Project ID

PRJ-2026-001_ph-segmentation

## Phase

DELIVERY / RELEASE increment of REQ-05 (refresh + validation). Follows
`handover/REQ-05_ph-asin-segmentation/2026-06-26_delivery_dashboard-ui-live-report-release.md`.

## Execution Environment & Recording Posture

This work was executed by **Abiraj in a separate Claude Chat session against the live PostgreSQL
database and dashboard** on 30 June 2026. This workbench record **documents** that session; the
workbench executor did **not** query or modify the live database, run SQL, or touch automation.

## Evidence Rule Applied

A claim is **VERIFIED** only when supported by a saved file, checksum, database result or existing
validation evidence inside this project. Otherwise it is **REPORTED_BY_ABIRAJ**. No execution logs,
DB pulls, screenshots or reviewer approvals were invented.

> **Evidence status for this increment:** no artifact from the 30 June session has yet been imported
> into the repo (the rebuilt HTML lives only in the live DB row, which must not be queried here).
> Therefore **all 30 June outputs below are REPORTED_BY_ABIRAJ.** The pre-refresh ("before") figures
> are **VERIFIED** because they already exist in the repo (`SYSTEM_REFERENCE.md` §7 and the
> 2026-06-24 / 2026-06-26 HTML, `segTotal` = 7,855).

## What This Records — the 30 June session, in order

### 1. Upstream window investigated (`analytics.ph_segment_30days_window`)

| Finding | Detail | Status |
|---|---|---|
| Scheduler | **No `pg_cron` inside Postgres** — the table is loaded by an ETL outside the DB; the schedule is not recorded anywhere observable | REPORTED_BY_ABIRAJ |
| Load pattern | **Full wipe-and-reload** (not incremental) — which is why it was briefly caught empty mid-reload | REPORTED_BY_ABIRAJ |
| State after reload | **239,353 rows / 15 monthly windows**, April 2025 → June 2026; latest window **1–30 June** | REPORTED_BY_ABIRAJ |
| Lineage | raw `public.traffic_data` → aggregated `ph_segment_30days_window` (engine input) **and** sibling `analytics.ph_segment` | REPORTED_BY_ABIRAJ |

### 2. Automation options reviewed (no automation created)

- **Claude Cloud Routine** — already built; blocked only by a Windows feature (Virtual Machine
  Platform). Abiraj **restarted the PC to enable the feature**; step-by-step to finish creating the
  routine was given, with explicit advice **not to click "Run now" today**.
- **`pg_cron`** — not installed; would require the DBA.
- **Manual run on the 3rd** — the fallback.
- Clarified **pgAdmin is not a scheduler**, and that a *view* could solve the empty-table problem
  cleanly but is the wrong tool for the heavy engine.
- **Outcome: automation still PAUSED / not created / not enabled / not executed.** REPORTED_BY_ABIRAJ.

### 3. Dashboard count source confirmed

- The dashboard renders **only** the HTML stored in `tech_team_outputs.ph_task.html_content`
  (**row id 5**) — it does **not** query the tables live.
- Tab counts are baked into the HTML as a `segTotal` object, rendered by the report's own JavaScript.
- All three layers (database row → embedded HTML → rendered tabs) matched exactly, including the
  escalation banner (**24 / 20**). REPORTED_BY_ABIRAJ.

### 4. Report refreshed to final-June numbers (reversible method)

The June window had filled out more completely (**15,608 → 16,378 rows**), so the dashboard was
refreshed to correct final numbers:

1. **Backed up first** — both the live HTML row and the report table:
   `ph_task_id5_backup_20260630` and `ph_segment_report_backup_20260630`.
2. **Re-ran the engine with a one-time forced window selector** (only that one line changed) to use
   the complete June window.
3. **Rebuilt the HTML server-side into row id 5** and updated the description/timestamp.
4. **Verified end-to-end:** no leftover placeholder, embedded counts identical to the database, live
   render check passed.

**Distribution shift (totals VERIFIED before / REPORTED_BY_ABIRAJ after):**

| Segment | Before (26 Jun, partial June) | After (30 Jun, complete June) |
|---|---:|---:|
| HHH Champions | 77 | 51 |
| HHL Leaky Buckets | 479 | 426 |
| HLH Wallflowers | 157 | 139 |
| LHH Hidden Gems | 17 | 5 |
| LLH Niche Winners | 349 | 440 |
| LLL Dead Horses | 6,776 | 7,088 |
| **Total** | **7,855** | **8,149** |
| Escalation banner | 24 / 20 | 24 / 21 |

The shift is expected: complete June data raises the benchmarks. **Totals (7,855 → 8,149) are as
reported; the per-segment assignment above is REPORTED_BY_ABIRAJ** and should be reconciled against
the rebuilt HTML when it is imported (the dominant ~7,000 bucket is LLL).

### 5. `ph_segment_report` validated vs source and protocol

See the companion validation record:
`validation/REQ-05_ph-asin-segmentation/2026-06-30_final-june-refresh_validation.md`. Summary
(all REPORTED_BY_ABIRAJ — recomputed in the live session, not re-run in the workbench):

- **Internal consistency:** 0 mismatches across all **8,149** rows (segment, movement, CVR,
  manual-flag, account, benchmark uniformity, duplicates).
- **Signal vs source:** report signals matched the June window **8/8** and a direct `traffic_data`
  sum **10/10**.
- **Benchmark recomputed from scratch** (thuwaraga / Bulbs): **135 sellers, Imp 2,097, Clk 24.9,
  CVR 91.46%** — matched the stored benchmark exactly.
- **Four protocol-undefined points** where the engine makes a documented choice were flagged — **none
  are errors**: the 66 "lateral SAME" moves; zero-click → LOW; conversions > clicks → HIGH; and the
  `HLL → HLH` / `LHL → HHL` mappings.

### 6. Data-quality questions investigated

Captured as reusable knowledge in
`capability/2026-06-30_weekly-snapshot-window-and-data-quality-findings.md`. Headlines:

- **CVR can exceed 100%** — clicks and conversions are counted independently and across different
  weeks; 8 sales on 1 click is a genuinely strong converter, not an error.
- **Why conversions ÷ clicks** — it isolates the product page's selling power, separate from
  visibility and search appeal.
- **Key discovery:** `traffic_data` is **weekly snapshots dated on the week-ending Saturday**, not
  daily (confirmed by the screenshot's weeks 22–26). A calendar-month window therefore catches a
  variable number of weeks (May = 5, June = 4), making month-over-month movement slightly unfair. The
  clean fix is a **"last 4 complete weeks"** window. It does **not** change the ASIN universe
  (8,134 = 8,134), and the **current report already uses 4 complete weeks for June** — so the existing
  report is correct; only the **header label** and the **previous-window (May) consistency** are
  refinements.
- **Zero-clicks proven safe** — across all four June weeks there are **zero NULLs**; the ~16,000
  zero-click rows per week are genuine zeros (seen, not clicked) — the normal long-tail, not missing
  data.
- **Conversions without clicks** — real examples (`B0CCD4KL94`, `B0B9Y59487` twice) — caused by
  Amazon attributing the click and the sale to different weeks, or buyers reaching products via
  cart / Buy-Again. Normal attribution; the engine correctly reads these as strong converters
  (LLH / HLH).

## Evidence Table

| # | Claim | Status | Basis |
|---|---|---|---|
| 1 | Pre-refresh distribution = 77/479/157/17/349/6,776 (7,855) | **VERIFIED** | `SYSTEM_REFERENCE.md` §7; 2026-06-24 + 2026-06-26 HTML `segTotal` |
| 2 | Upstream window: 239,353 rows / 15 windows, no pg_cron, wipe-and-reload | REPORTED_BY_ABIRAJ | Live DB inspection in chat; DB not queried here |
| 3 | Dashboard reads only `ph_task` row 5 HTML; counts in `segTotal` | REPORTED_BY_ABIRAJ | Live session; consistent with `SYSTEM_REFERENCE.md` §8 |
| 4 | Backups taken: `ph_task_id5_backup_20260630`, `ph_segment_report_backup_20260630` | REPORTED_BY_ABIRAJ | DB state; not pulled |
| 5 | Engine re-run with one-line forced window; HTML rebuilt into row 5 | REPORTED_BY_ABIRAJ | Live session; no SQL diff or HTML imported here |
| 6 | Post-refresh distribution totals = 8,149; June window 16,378 rows | REPORTED_BY_ABIRAJ | Live session; rebuilt HTML not imported |
| 7 | Validation: 0 internal mismatches; 8/8 + 10/10 signal vs source; benchmark recompute matched | REPORTED_BY_ABIRAJ | Recomputed live; not re-run in workbench |
| 8 | Data-quality findings (weekly snapshots, zero-click safety, attribution) | REPORTED_BY_ABIRAJ | Live session + screenshot (weeks 22–26) not imported |

## Source-of-Truth Note (action required)

`SYSTEM_REFERENCE.md` §1 and §7 still state the **superseded** partial-June distribution
(**7,855** / 77-479-157-17-349-6,776), which is now the *previous* build. The canonical numbers were
**not edited** in this increment because the 30 June figures are REPORTED_BY_ABIRAJ with no imported
artifact. **Do not overwrite the reference until the rebuilt HTML is imported and checksummed**, then
update §1/§7 to the 8,149 build in a governed step. Recorded here so the divergence is not lost.

## Open Decisions (none urgent — for GPT / Abiraj / Bietrick)

1. Whether to **formally document the four edge-case interpretations**. Note: three are already in
   `SYSTEM_REFERENCE.md` (zero-click → LOW and conversions > clicks → HIGH in §7; `HLL→HLH`/`LHL→HHL`
   in §4/§11). The **66 "lateral SAME" moves** treatment is the one not yet written down explicitly.
2. Whether to **fix the report header label** to read "last 4 complete weeks".
3. Whether to **adopt the 4-complete-weeks window** going forward (trial it, then run past Bietrick).
4. Whether to **finish the automation** (Cloud Routine / `pg_cron` / manual on the 3rd).

## Current State (end of 30 June 2026)

| Aspect | State |
|---|---|
| Dashboard (`ph_task` row id 5) | LIVE with verified, complete-June numbers (REPORTED_BY_ABIRAJ; DB not queried here) |
| `ph_segment_report` | Rebuilt and fully validated vs source + protocol (REPORTED_BY_ABIRAJ) |
| Backups | `ph_task_id5_backup_20260630`, `ph_segment_report_backup_20260630` still in place (can be dropped when ready) |
| Automation | PAUSED — not created/enabled/executed; Windows feature enabled via restart, routine creation not finished |

## What Must Not Be Done (carried forward)

- Do not execute SQL or modify the live database from the workbench;
- Do not initialise, create or enable the automation;
- Do not drop the 30 June backups until Abiraj confirms;
- Do not overwrite `SYSTEM_REFERENCE.md` numbers until the rebuilt HTML is imported and checksummed;
- Do not mark any 30 June claim VERIFIED without saving the corresponding evidence.

## Current Status

RECORDED — second delivery increment of REQ-05. No SQL executed, no live database modified, no
automation created/enabled, no canonical reference overwritten.

## Final Result

AMBER. The 30 June refresh, validation and data-quality review are **recorded faithfully and
read-only**. The "before" baseline is VERIFIED from the repo; **all 30 June outputs are
REPORTED_BY_ABIRAJ** because no artifact (rebuilt HTML, backups DDL, forced-window SQL diff, chat
share link) has been imported yet.

## One Next Step

Import the 30 June work products — the rebuilt HTML (+ checksum), the forced-window SQL line, and a
chat share link — so the 8,149 build can be upgraded from REPORTED_BY_ABIRAJ to VERIFIED and
`SYSTEM_REFERENCE.md` §1/§7 can be updated in a governed step.
