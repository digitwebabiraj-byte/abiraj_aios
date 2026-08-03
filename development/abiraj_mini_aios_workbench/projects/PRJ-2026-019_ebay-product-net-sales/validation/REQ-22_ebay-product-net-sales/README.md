# Validation — REQ-22 eBay Product Net Sales

**Status: not built, so nothing to validate yet.** Once REQ-22-D01 is built, a re-runnable harness
`verify_epns_d01.py` must re-derive every figure *without importing the builder* and diff it against the
workbook.

## What it must check (planned)
| Check | Why |
|---|---|
| Row count = live distinct eBay order lines (30d, source_id=2) | Universe complete, not duplicated by SKU sprawl |
| Gross / Net Sales re-derived per order match the workbook | The core facts |
| The worked example `02-14934-76138` reconciles to 22.39 | The stated business anchor |
| Money never blended across currencies; UK cells £, DE cells € | The DST currency defect must not recur |
| Every `NO DATA` cell (Product Cost etc.) is genuinely unsourceable, not a dropped join | No silent guessing |
| Net Sales Lookup returns the same value as the main table for a given Order ID | Tab consistency |
| Two consecutive runs on the same anchor produce an identical payload | Determinism / partial-day guard |

## Blocking note
Full Net Sales validation is impossible until the **Product Cost** handling is decided — if Product Cost
is `NO DATA`, Net Sales is computed excluding it (flagged), and that must be stated, not reconciled away.
