# Duplicate-Risk Report — REQ-19 eBay Product Performance Analysis

**Date:** 2026-07-27 · **Verdict: 🟠 AMBER** (heavy overlap, but a genuinely new element justifies a
distinct project that *inherits* rather than re-derives).

## Rule applied
Existing-Asset-First: **reuse → extend → merge → create**. Scanned the workbench for an existing
per-listing eBay performance/profit object before building.

## Overlap found (per-listing eBay, UK+DE)
| Existing project | Overlaps this report on | Stays canonical for |
|---|---|---|
| **PRJ-2026-014 ESNM** | traffic (Views/Conversion), stock, listing status, Sales Trend, per-listing grain | slow/no-moving actions — near-superset overlap |
| **PRJ-2026-010 EPC** | per-listing pricing | price-drift vs Amazon/website |
| **PRJ-2026-012 ERA** | eBay fees (FVF), ad cost (CPC+CPS) | returns analysis |
| **PRJ-2026-011 EBPD / PRJ-2026-015 DST** | sales/revenue definitions | account × marketplace performance (monthly / daily) |

## Why not STOP (why this is not a pure duplicate)
The **per-listing profit-and-loss line** — Cost Price → eBay Fees → Ad Cost → VAT → **Gross / Net
Profit / Profit Margin %** — is produced by **no** existing project. Consolidating identity + pricing +
cost + sales + traffic into one product-level P&L view is the new value.

## Consequence (governs the build)
Most of the 35 columns must be **inherited** from the projects above, not re-derived, or the business
gets a second set of numbers that don't reconcile with published reports (the duplicate-truth failure
DST guards against). This is enforced in `CLAUDE.md` (inherit definitions; one generator module).

## Caveat
This verdict is provisional — it was formed during a **warehouse-only** audit (`ledsone` down) and
before the P&L logic is confirmed with Thinesh. Re-confirm once the profit definitions and publish
audience are settled. No `ph_task` publish has occurred, so no live duplicate exists yet.
