# CLAUDE.md — PRJ-2026-012_ebay-return-analysis (execution rules)

Inherits all rules from the workbench root `CLAUDE.md` and `START_HERE.md`
(`development/abiraj_mini_aios_workbench/`). The project `PROJECT_HOME.md` and `SYSTEM_REFERENCE.md`
still govern. Project-specific rules below.

## Identity
- Project: `PRJ-2026-012_ebay-return-analysis`. Task: `REQ-14_ebay-return-analysis`. `project_code=ERA`.
  Owner/dev Abiraj; business validator Thinesh.
- ⚠ **`REQ-14` and `ERA` are working defaults, minted with owner confirmation PENDING** — the source
  files carry no requirement id (as with REQ-11 / REQ-12 / REQ-13). Confirm both with the owner before a
  live build or any publish.
- A new day/session does **not** mint a new Task ID. Keep `REQ-14` until D01 is closed; a genuinely new
  requirement (e.g. scheduling) earns a new deliverable id (`REQ-14-D02`) only after owner confirmation.

## Scope
- Write only inside `projects/PRJ-2026-012_ebay-return-analysis/`.
- The user's Downloads originals (`files (6).zip`, `Thinesh task (2).xlsx`) are read-only; the registered
  copies in `evidence/` + `sql/` are this project's canonical copies.

## Read-only discipline
- **READ-ONLY on all source data.** The live Ledsone PostgreSQL (via the **Ledsone Database MCP**) is a
  read-only evidence source — never `INSERT`/`UPDATE`/`DELETE`, never DDL, never seed. This report needs
  **no DB object** (per-run extract, not a view); do not create one.
- Use the **normalised domain schemas** (`customer_service`, `order_management`, `listings`, `inventory`,
  `ebay_campaigns`, `accounting`). **Do NOT use the `public.*` denormalised layer** — it belongs to a
  different DB and returns nothing here.
- The **only** approved write is the guarded publish of the finished dashboard to
  `tech_team_outputs.ph_task`, and **only** when a live build is explicitly authorised. **Not yet done.**
  Never re-publish or overwrite `ph_task` rows without explicit instruction.

## The locked method (do not silently change — see SYSTEM_REFERENCE.md)
- **Grain:** one row per variant SKU with ≥ 1 eBay return in the period. **SKU resolution via
  `transaction_id` → `order_item_info.item_transaction_id`** — never `item_id` (1,331 map to multiple
  variants).
- **Return Cost** = REFUND + FINAL_VALUE_FEE(_FIXED_PER_ORDER) on returned orders, from
  `accounting.ebay_order_expenses` keyed on the **eBay order reference** (`orders.order_id`, varchar).
- **Advertising = CPC + CPS.** `ebay_campaigns.performance_data` is **CPC-only**; CPS/Standard cost is
  the `AD_FEE`/`PREMIUM_AD_FEES` per-sale fee in `accounting.ebay_order_expenses`. Never present ad
  columns from `performance_data` alone.
- **Text-typed numerics** (`item_quantity`, `real_qty`, `item_price`, `real_price`) are VARCHAR — cast
  `NULLIF(x,'')::numeric`.
- **Case fields** (reason, `seller_refund_amount`) live on the **earliest** row per `return_id`; latest
  **state** on the **newest** row (the two `DISTINCT ON` CTEs). Do not collapse them.
- **Intentional blanks are correct, not bugs:** blank Return Rate = no period orders; blank ACOS/ROAS =
  no ad sales / no ad spend; Return Cost £0 = no upstream fee row. Do not fill with 0 or dashes.
- The `build_dashboard.py` layer is **formatting only** — the SQL emits friendly Account, mapped reason
  labels and `#n` rank; do not remap in Python.

## Reconciliation is mandatory
- SQL is **never** the deliverable — it must be executed via the Ledsone DB MCP and the real rows returned.
- A live build must match the **June 2026 reference**: 144 SKU rows · 153 returns · 17.7% blended · Refund
  £2,937.37 · Return Cost £869.39 · Ad Spend £1,387.96 · Ad Sales £9,343.63 · ACOS 14.9% · ROAS 6.73x;
  reason breakdown sums to 153. A divergence without explanation is a stop condition.
- The mockup's dummy rows (LS1001 etc.) are **illustrative only** — never reproduce them as the answer.

## Publish gotchas (ph_task) — apply the PRJ-2026-010/011 precedent when authorised
- No real `UNIQUE(task_id)` in live → `ON CONFLICT (task_id)` fails; use **pre-DELETE by task_id + plain
  INSERT** under a guarded `temp_user` transaction (dry-run + duplicate guard first).
- **`assigned_user_team` is missing from the sample DDL but MUST be set** (eBay team group, e.g.
  `ebay_priors`), or the report won't group. Verify user names live vs `staff.users` before publish.

## Stop Conditions (in addition to workbench rules)
- Stop and confirm with the owner before minting/committing to the `REQ-14` / `ERA` identifiers for a
  live build.
- Stop if asked to run the SQL against the `public.*` layer or any DB other than the Ledsone normalised
  schemas.
- Stop if a rendered figure diverges from the governed live pull without explanation.
- Stop if any write would land on any source table (DML/DDL/seed), or outside this project folder.
- **Do not publish** to `tech_team_outputs.ph_task` or commit/push without explicit owner instruction.

## Vocabulary
transaction_id bridge = the correct returns→SKU join · CPC = ON_SITE/Advanced ads (performance_data) ·
CPS = Standard/COST_PER_SALE ads (AD_FEE per-sale fee) · Return Cost = REFUND + FINAL_VALUE_FEE · Open
Case = latest to_state ≠ CLOSED · Stock = live snapshot (not period-bound) · ebay_priors = the ph_task
team group.
