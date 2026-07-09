# CLAUDE.md — PRJ-2026-005_weekly-sku-performance-check

Inherits all rules from the workbench root `CLAUDE.md` and `START_HERE.md`
(`development/abiraj_mini_aios_workbench/`). Project-specific rules below.

## Scope

- Write only inside `projects/PRJ-2026-005_weekly-sku-performance-check/`.
- The production DB `order_management_copy` (via the Postgres MCP) is a **read-only evidence
  source** — never `INSERT`/`UPDATE`/`DELETE`, never DDL. This report needs **no DB object**
  (it is a per-run extract, not a view); do not create one without the owner's written approval.
- The Downloads artifacts (`HANDOFF_weekly_sku_performance_check.md`, `PHs Daily works -
  Dev_Automation.xlsx`) are the user's originals — read-only; the registered copies live in this
  project's `evidence/` and `sql/`.

## Task ID Rule

- Active task: `T7_weekly-sku-performance-check` (deliverable **D01**). `T7` is the source's real
  task number (Task 7 / Table 7 / project code `PH-2026-07-THUW07`) — no `REQ-NN` exists in the
  source, so the real task id is used, named after the deliverable.
- A new day or session does NOT mint a new Task ID — keep using `T7_…` until D01 is closed.
- Do not invent a `REQ` number; a genuinely new requirement needs the owner's confirmation first.

## Evidence Rule

- Every column / figure must map to a real `schema.table.column` or an explicit "derived from X"
  formula. No confirmed source = the field goes to Known Limits, never stated as fact.
- Locked data rules (verified against the live DB) are in `SYSTEM_REFERENCE.md` and the imported
  `HANDOFF.md` — do not silently change them (PH filter = `user_name='thuwaraga'`; orders =
  `COUNT(DISTINCT order_item_info)` where `order_status='Completed'`; platforms = AMAZON/EBAY/B&Q
  UK; base SKU = `mapped_sku` else `sku`).

## Data-Quality / Flag Rule

- `mapped_sku` is dirty for this PH — flag differing rows `MAPPED?`, **never auto-correct** the
  grouping by inventing a SKU→SKU mapping (mirrors the Table 5 legacy-SKU decision).
- `amzn.gr.*` sku values are Amazon internal group IDs, not products — exclude from the report,
  keep visible in SQL for audit.
- Do not silently drop zero-order listings — the spec requires them to appear as 0.

## Stop Conditions (in addition to workbench rules)

- Stop if asked to trust `mapped_sku` groupings that reassign a listing to an unrelated family
  without owner confirmation.
- Stop if asked to hard-code the report window instead of computing it from the run date, once
  scheduling is wired.
- Stop if a rendered figure diverges from the governed pull / DB without explanation.
- Stop if any write would land outside this project folder, or if any DB write (view/DDL/DML) is
  requested.
