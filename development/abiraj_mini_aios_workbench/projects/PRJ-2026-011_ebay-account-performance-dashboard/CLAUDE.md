# CLAUDE.md — PRJ-2026-011 eBay Account Performance Dashboard (execution rules)

Project-level rules. The root workbench `CLAUDE.md` and `PROJECT_HOME.md` still govern.

## Identity
- Project: `PRJ-2026-011_ebay-account-performance-dashboard`. Task: `REQ-13_ebay-account-performance-dashboard`.
  `project_code=ebpd`. Owner/dev Abiraj; business validator Thinesh.
- A new day/session does **not** mint a new Task ID. Keep `REQ-13` until a genuinely new requirement (with
  owner confirmation) earns a new deliverable/task id. REQ-13-D01 is **CLOSED / accepted 2026-07-20**.

## Read-only discipline
- **READ-ONLY on all source data** — warehouse `order_management_copy` tables + the `ledsone` DB. No
  INSERT/UPDATE/DELETE, no DDL, no schema change, no automation on any source/application table.
- The **only** approved write is the guarded publish of the finished dashboard to
  `tech_team_outputs.ph_task` (the output registry), on explicit owner instruction. Done — ids 333–336.
- Never re-publish or overwrite `ph_task` rows without explicit instruction.

## The confirmed method (do not silently change)
- Sales = `SUM(order_total)` on `source_name='EBAY'`, `order_status='Completed'`. Rows = account × marketplace.
- Conversion = `traffic_data which_channel=2` `SUM(conversion)/SUM(click)` (whole-account).
- Advertising = eBay Promoted Listings **ON_SITE only** (`ppc.record_subtype='ON_SITE'`, join
  `ppc_performance.record_id = ppc.parent_id`); show Ad Spend, Ad Sales (ON_SITE-attributed), **TACOS**,
  Return. Never present ACOS/ROAS on attributed sales.
- New Listings from ledsone `listings.ebay_listings.created_at`; Active from `listing_data` distinct `ref_id`;
  Stock from `inv_final_stock` (shared); Sales Rank by revenue.

## Reconciliation is mandatory
- Every headline must reconcile to the owner's own live-DB figure before it ships (this project was
  corrected five times exactly because early passes didn't). led_sone UK revenue £28,975.37 and so_926407 UK
  ON_SITE ad £884.07 are the anchor checks.
- SQL is never the final answer — execute it via the MCP and return the real rows.

## Publish gotchas (ph_task)
- No real `UNIQUE(task_id)` in live → `ON CONFLICT (task_id)` fails; use **pre-DELETE by task_id + plain INSERT**.
- **`assigned_user_team` is missing from the sample DDL but MUST be set** = `ebay_priors`, or the report
  won't group. `action_took_by`/`action_took_date_time` stay NULL until a user actions it.

## Open items (owner's, not to be decided here)
- Orders count definition (distinct 1,517 vs line 1,619) — kept distinct, accepted "all ok".
- Conversion RAG threshold recalibration for whole-account conversion (~2–3%).
- Housekeeping: move the `temp_user` DB password out of `push_ebpd_dashboard.py` plaintext.

## Vocabulary
`order_total` = settled paid revenue · account × marketplace = row grain · ON_SITE = Priority/Advanced ad ·
COST_PER_SALE = Standard ad (excluded) · TACOS = spend ÷ total revenue · which_channel=2 = eBay traffic ·
ebay_priors = the ph_task team group.
