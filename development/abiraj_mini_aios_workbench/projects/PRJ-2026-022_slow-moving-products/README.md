# Slow Moving Products (smp) — PRJ-2026-022

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`; task index in `TASK_REGISTER.md`.

## What
A **Slow Moving Product Analysis** for **Mahima**, covering **Germany (DE)** across all three sales
channels (Shopify DE, Amazon DE, eBay DE). It is the **inverse of Fast Moving Products (PRJ-2026-020)**:
instead of the top sellers, it lists SKUs that are **holding German stock but NOT selling**, so buying /
clearance / promotion decisions can be made on dead and slowing inventory. For each SKU it shows the stock
level, when it last sold, its 30-day and 90-day sales, how long it has gone without a sale, and a
recommended **Reason** + **Action**.

## Status
🟢 **BUILT & DELIVERED 2026-08-11 — pending Mahima sign-off.** DE-only, live raw `mcp.ledsone` data.
**13,344 slow-moving SKUs** (0 units sold in the last 30 days, holding German stock). Excel
(`SlowMovingProducts_DE.xlsx`, Notes + Slow Moving table) + interactive HTML dashboard. Every **factual**
column is sourced live; **Reason / Action use documented default rules (Notes tab) awaiting Mahima's
confirmation.** Committed to `main` (f79400f). Not published to `ph_task`, not automated.

> ⚠ The source workbook (`mahima task (2).xlsx`) is a **layout mock-up with sample rows** (ABC123,
> "High stock" → "Create bundle"). It defines the desired **columns and Action vocabulary only** — never
> copy a sample value. Every delivered figure traces to live `ledsone` data.

## Identity (provisional)
`PRJ-2026-022` / `REQ-25` / code `smp`. Provisional — the source has no requirement number; REQ-24 is
taken by `channel-opportunity` (chop). Confirm with Abiraj (cosmetic).

## Deliverable
- **REQ-25-D01** — Slow Moving Products report, one data layer rendered as:
  - **Excel** — `evidence/final_outputs/REQ-25_slow-moving-products/SlowMovingProducts_DE.xlsx`
    (Notes tab + "Slow Moving" tab, 9 columns, filterable, frozen header).
  - **HTML dashboard** — `.../slow_moving_dashboard.html` (KPI tiles, searchable, sortable).
  - Builder: single read-only module `sql/REQ-25_slow-moving-products/build_smp_d01.py`.

## The report shape (9 columns, from the source workbook)
`SKU · Product Name · Stock Qty · Last Sale Date · Last 30 Days Sales · Last 90 Days Sales ·
Days Without Sale · Reason · Action`

## Authoritative documents
- `PROJECT_HOME.md` — canonical project truth
- `SYSTEM_REFERENCE.md` — the column → `schema.table.column` map
- `CLAUDE.md` — execution rules
- `TASK_REGISTER.md` — task/deliverable index

## Next step
Discovery decision sheet to **Mahima**: slow-moving definition & row count, Days-Without-Sale convention
for never-sold SKUs, and the Reason/Action rule vocabulary. Then confirm identity, publish audience, and
(optionally) weekly automation on the FMP pattern.
