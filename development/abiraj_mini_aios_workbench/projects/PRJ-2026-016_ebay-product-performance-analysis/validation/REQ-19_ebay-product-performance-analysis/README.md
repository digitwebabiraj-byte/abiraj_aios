# Validation — REQ-19 eBay Product Performance Analysis

**Status: independent verification note not yet written.** The build has been self-checked (row count
9,781 = live distinct item_ids; revenue reconciled UK £54,286 / DE €25,341 ≈ 93–94% of the window
total), but a re-runnable harness that re-derives every figure *without importing the builder* is TODO.

## What must land here

`verify_eppr_d01.py` — re-derives each populated column straight from the warehouse and diffs it
against the workbook, plus a dated verification record.

## What it must check
| Check | Why |
|---|---|
| Row count = live distinct active eBay item_ids (UK+DE) | Proves the universe is complete and not duplicated by the SKU-sprawl trap |
| Revenue/Units/Orders re-derived per item_id match the workbook | The core sales facts |
| Money never blended across currencies; UK cells £, DE cells € | The DST currency defect must not recur |
| Every `NO DATA` column is genuinely unsourceable, not a dropped join | Cost/profit, Watch Count, PPC Campaign, Sales Trend |
| One listing reconciled by hand to a figure Thinesh can verify | The REQ-13 lesson (five corrections came from skipping this) |
| Two consecutive runs on the same anchor produce an identical payload | Determinism / partial-day guard |

## Blocking note
A full profit validation is impossible until a **Cost Price** source exists — the profit columns are
`NO DATA` by design, so there is nothing to reconcile there yet.
