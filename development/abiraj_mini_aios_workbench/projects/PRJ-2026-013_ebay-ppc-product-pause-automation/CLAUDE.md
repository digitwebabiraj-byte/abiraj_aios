# CLAUDE.md — PRJ-2026-013 eBay PPC Product Pause Automation

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional and
specific to this project.

## 1. Never write to live PPC

This project recommends pauses. It **does not execute them.** Pausing an eBay campaign or listing is
a write to live advertising and is covered twice by *Never Touch Without Written Approval*
("live automation", "financial or PPC business logic"). No approval exists.

Do not write eBay API calls, do not build a write-back path, do not add a "apply pauses" button.
If asked to, stop and report the gate.

## 2. Never combine ON_SITE and COST_PER_SALE

Standing warehouse rule with no exceptions. eBay Advanced (`ON_SITE`, charged per click) and
Standard (`COST_PER_SALE`, charged as a % of sale) have incompatible pricing models. Never sum their
spend/sales, never report one blended ACOS, never let one rule span both. Split by
`ppc.record_subtype` and label each.

## 3. SMART campaigns have no listing-level data

`ON_SITE` + `bidding_strategy='SMART'` emits campaign-grain rows only — zero `ad`-grain item_ids.
Never present a SMART campaign as if it were a per-listing decision. Until decision A is closed,
SMART is out of scope; if it enters scope it is a **whole-campaign** decision and must be labelled
as such.

## 4. Stock: never turn "unknown" into "zero"

7.8% of advertised listings do not bridge to any SKU. A missing bridge means **NO STOCK DATA**, and
must render as such. Collapsing it to `0` would trip the stock rule and auto-recommend pausing a
listing that may be fully in stock. Always `LEFT JOIN`; always `COALESCE` for display only, never
for the rule test.

80% of listings map to multiple SKUs. Do not silently pick an aggregation — the rule is decision C
and must be stated on the report once chosen.

## 5. Thresholds stay configuration

The five thresholds (stock floor 5 · ACOS ceiling 40 · ACOS rescue 20 · clicks min 20 · spend floor
2.50) come from the `Pause Rules` sheet. They must live in an editable config surface and be echoed
on the report. Never hardcode them in a query or a script — FRRC precedent.

## 6. Window anchor

Anchor all windows on `MAX(date)` of loaded PPC data, never `CURRENT_DATE`. A late ETL run otherwise
produces a ragged, under-counted final day and silently changes decisions.

## 7. Stock is live, spend is windowed

`location_wise_inv_stock` has no history. Every report pairing a 30D spend figure with a stock number
must state that stock is as of today.

## 8. Canonical source

Where the xlsx and the HTML differ, **the HTML wins** — it holds the executable engine. The xlsx
`Custom Rules` sheet is explicitly a planning worksheet and is wired to nothing.

## 9. Read-only until gated

Read-only queries only. No DDL, no `ph_task` publish, no scheduled task registration, no git commit
until the open decisions in `PROJECT_HOME.md` are closed and the reviewer gates pass.
