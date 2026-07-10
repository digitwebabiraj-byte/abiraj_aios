# CLAUDE.md — PRJ-2026-006_zero-sales-full-optimization

Inherits all rules from the workbench root `CLAUDE.md` and `START_HERE.md`
(`development/abiraj_mini_aios_workbench/`). Project-specific rules below.

## Scope
- Write only inside `projects/PRJ-2026-006_zero-sales-full-optimization/`.
- Production DB `order_management_copy` (via Postgres MCP) is a **read-only evidence source** —
  never `INSERT`/`UPDATE`/`DELETE`, never DDL. This report needs **no DB object** (per-run extract,
  not a view); do not create one without the owner's written approval.
- Downloads artifacts (`PROJECT_CONTEXT.md`, `utharsika task.xlsx`, prior xlsx/verification pack)
  are the user's originals — read-only; the registered copies live in this project's `evidence/`.

## Task ID Rule
- Active task: `REQ-08_zero-sales-full-optimization` (deliverable **D01**). `REQ-08` is the source's
  real requirement id (`utharsika task.xlsx` → `REQ-08-D01`, project_code `PH-2026-07-UTHAR04`).
- A new day or session does NOT mint a new Task ID — keep using `REQ-08_…` until D01 is closed.
- A genuinely new requirement (e.g. scheduling) gets a new deliverable id (REQ-08-D02) after owner
  confirmation — do not invent one silently.

## Locked-rule Rule (do not change without owner sign-off — see SYSTEM_REFERENCE.md)
- PH filter = `user_name='utharsika'`; universe from `traffic_data` (which_channel=1, UK).
- Zero-sale = 0 units across `order_transaction` (Completed, AMAZON, UK) **AND** `vendor_sales`.
- Window = `[run_date-30, run_date-1]`, current day excluded.
- Vendor match = **OVERLAP** (not `start_time` alone).
- `listing_data` for Utharsika = **which_channel is NULL** — never filter `which_channel=1` on it.
- UK stock exact-SKU match on `location_wise_inv_stock` (`location='UK'`); FBM = merchant & not-FBA.

## Data-Quality / Flag Rule
- `amzn.gr.*` sku values are Amazon internal group IDs — excluded; keep visible in SQL for audit.
- Do not silently drop zero-impression / out-of-stock rows — they are the point of the report.
- Never present a lifetime vendor figure as an in-window sale — the "Last Vendor Sale" column exists
  precisely to keep that distinction visible.

## Stop Conditions (in addition to workbench rules)
- Stop if asked to filter `which_channel=1` on `listing_data` for Utharsika (zeroes her stock).
- Stop if asked to use previous-calendar-month instead of the 30-day window for "Last Month Sales".
- Stop if asked to hard-code the window once scheduling is wired (must compute from run date).
- Stop if a rendered figure diverges from the governed pull / DB without explanation.
- Stop if any write would land outside this project folder, or if any DB write (view/DDL/DML) is
  requested.
