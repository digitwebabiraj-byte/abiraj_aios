# CLAUDE.md — PRJ-2026-008_frrc-fba-returns-root-cause

Inherits all rules from the workbench root `CLAUDE.md` and `START_HERE.md`
(`development/abiraj_mini_aios_workbench/`). Project-specific rules below.

## Scope
- Write only inside `projects/PRJ-2026-008_frrc-fba-returns-root-cause/`.
- The production Postgres analytics DB (via the Postgres MCP) is a **read-only evidence source** —
  never `INSERT`/`UPDATE`/`DELETE`, never DDL, never seed. This report needs **no DB object** (per-run
  extract, not a view); do not create one without the owner's written approval.
- Downloads artifacts (`files (5).zip` contents) are the user's originals — read-only; the registered
  copies live in this project's `evidence/source_documents/` and `evidence/final_outputs/`.

## Task ID Rule
- Active task: `REQ-10_fba-returns-root-cause` (deliverable **D01**). `REQ-10` is the source's real
  requirement id (`_Amazon_FBA_Returns_Tracker_-_Rebecca.xlsx` → `REQ-10-D01`, project_code `frrc`).
- A new day or session does NOT mint a new Task ID — keep using `REQ-10_…` until D01 is closed.
- A genuinely new requirement (e.g. scheduling) gets a new deliverable id (`REQ-10-D02`) after owner
  confirmation — do not invent one silently.

## Locked-rule Rule (do not change without owner sign-off — see SYSTEM_REFERENCE.md)
- **Population:** Amazon FBA only. Returns `amazon_returns.fulfilment='fba'`; sales
  `source_name='AMAZON'` AND `fba_sales=TRUE`. **Units Sold = FBA-UK Completed**
  (`market_place='UK'`, `order_status='Completed'`). Return-driven; zero-return ASINs excluded.
- **Window:** last 30 days ending the day **before** the run; current-day excluded
  (`CURRENT_DATE − 30d` … `CURRENT_DATE − 1d`). The 30-day **length is HELD** (open item C) — the
  spec doesn't fix it.
- **Grain / join:** one row per returning **ASIN**; anchor on ASIN (returns SKUs are listing-variants,
  sales SKUs are base — they do not join on `sku`); resolve the display SKU via the `listing_data`
  bridge (`which_channel=1`, `wrong_sku=0`, non-parent, UK; `COALESCE(NULLIF(mapped_sku,''),sku)`).
- **Return Rate** = Total Returns / Units Sold; Units Sold = 0 → "N/A" (Flag "N/A - No Sales Data").
  N/A rows are **correct**, not a bug.
- **Thresholds** (Critical > 0.20 · High > 0.10 · min 2 returns · Listing/Quality share ≥ 0.40 · Buyer
  ≥ 0.50) come from the **editable Thresholds tab** — applied in the render layer, **never hardcoded**
  into the SQL row logic.
- **Reproduce the independence quirk faithfully:** Flag (rate-based) and Root Cause (count-based, min 2)
  are independent gates — a 1-return ASIN can read CRITICAL yet resolve to "Too few returns to
  evaluate". Do **not** "fix" this.
- **Responsible Person** = `order_transaction.user_name`; one ASIN = one owner (verified); no
  in-window sale → "Unassigned".

## Data-Quality / Flag Rule
- The tracker's existing sample rows are **illustrative only** — never reproduce them as the answer.
- **Run `reason_domain_check.sql` first every run.** Any live `reason` not in the §4 map is **flagged**
  for Satheesvaran, never silently pushed into Unknown.
- Report the reconciliation counts every run (returning ASINs / return units / per-row bucket sum);
  a divergence from the rendered outputs is a stop condition.
- SQL is **never** the deliverable — it must be executed via the Postgres MCP and real rows returned.

## Stop Conditions (in addition to workbench rules)
- Stop and route the open items to **Satheesvaran** rather than deciding any of them:
  A order-status set · B marketplace scope · C window length/cadence · D returns↔sales alignment ·
  E rare reason-code buckets · F return-status filter (the only one that changes the numbers) ·
  G attributing unassigned owners via `listing_data`.
- Stop if asked to hardcode the thresholds into the SQL, or to hardcode the run date instead of
  `CURRENT_DATE`.
- Stop if a live `reason` code cannot be safely bucketed.
- Stop if a rendered figure diverges from the governed pull / DB without explanation.
- Stop if any write would land on any source table (DML/DDL/seed), or outside this project folder.
- **Do not publish** to `tech_team_outputs.ph_task` or commit/push without explicit owner instruction.
