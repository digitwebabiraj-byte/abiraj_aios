# CLAUDE.md — PRJ-2026-020 Fast Moving Products

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional.

## Identity
- Project `PRJ-2026-020_fast-moving-products` · code `fmp` · Task `REQ-23`.
  Owner Abiraj; Business Validator **Mahima**. **IDs provisional** (source is a spec mock-up, no
  requirement number; REQ-22 is taken by `epns`). A new day/session does not mint a new Task ID.

## 1. The source workbook is a layout spec, not data
Every value in `mahima task.xlsx` (LDMST64E27, ASIN123, the quantities) is an **illustrative sample**.
It defines the desired **columns, tables and Action vocabulary** only. Never copy a sample number into a
deliverable. Every delivered figure must trace to live `ledsone` / warehouse data.

## 2. Confirm the business rules before building — do NOT invent thresholds
"Fast moving", **Trend** (Growing/Stable/Slow), **Action** and **Final Decision** are business rules, not
raw columns. The window (fixed month vs rolling 30/90-day), the ranking metric & N, the **Average Daily
Sales** denominator behind Stock Cover Days, and the Action thresholds must all be confirmed with Mahima.
A single mock-up row is not a spec.

## 3. This is DE / EUR — never blend currencies (the DST defect)
The report is Germany across 3 channels → **€**. `orders.total` and money fields are in the marketplace's
own currency; format every money cell as €, never sum across marketplaces of different currency, and never
label a EUR value with £.

## 4. Per-channel isolation + eBay grain
- Amazon = `which_channel=1`, eBay = `which_channel=2`, Shopify = `which_channel=3`. Keep them separate;
  only the Combined table rolls up.
- **eBay: never join sales by SKU alone** — one SKU → many item_ids (~13× overstatement). Attribute by
  order_id / item_id; isolate eBay with `source_id=2`.

## 5. Stock resolution is a bridge, not a column
Current Stock / Stock Cover comes from `location_wise_inv_stock` via the `listing_data` SKU bridge
(`ppc-stock-lookup` skill): wrong_sku check → mapped_sku fallback → **mandatory clean-SKU step** →
location filter (DE). A resolved listing SKU can still fail to match inventory — do the clean-SKU step.

## 6. Combined table keys on the base SKU
The same product has different Product IDs per channel (ASIN / Listing ID / Shopify id) but a shared base
SKU. Roll up Amazon/eBay/Shopify units per **clean base SKU**, never per channel Product ID.

## 7. Source of record + read the KB first
- This is **multi-domain** (Orders + Stock, 3 channels) → use `text-to-sql-multi` + `ppc-stock-lookup`.
- Prefer **raw `ledsone`** for eBay (warehouse hides SMART campaigns / is thinner).
- **Read the AIOS knowledge base (`docs.ledsone.co.uk/mcp`) before writing any SQL** — skipping it caused
  wrong builds twice. Apply `all_list=1`, VARCHAR casts, the parent-row title trap.

## 8. Read-only; never fabricate
- READ-ONLY on all source tables. No INSERT/UPDATE/DELETE/DDL. The only future write is a guarded
  `ph_task` publish on explicit owner instruction after the audience is named and each recipient verified.
- Every filled column traces to a real `schema.table.column`. Unsourceable columns render `NO DATA` —
  never a guess. A `0` is written only where the true value is zero. Watchers-style "no source" columns
  (if any surface) are flagged, not faked.
- Credentials come from the git-ignored shared store, never committed.

## 9. One generator module
The report (and any future scheduled run) comes from a single module `sql/REQ-23_.../fmp_build_d01.py`.
Do not fork a second fetch path.

## 10. Stop conditions (in addition to the workbench's)
- A build is requested before the window, ranking metric, Trend rule and Action thresholds are confirmed
  with Mahima.
- A build would populate Trend / Action / Stock Cover by guessing a rule or denominator.
- A publish is requested before the audience is named and each recipient verified.
- Any request to blend currencies or report a single total across channels of different currency.

## Vocabulary
Fast moving = top sellers by units · Stock Cover Days = Current Stock ÷ Avg Daily Sales · Trend = velocity
classification (Growing/Stable/Slow) · Action / Final Decision = inventory rule engine output ·
which_channel 1/2/3 = Amazon/eBay/Shopify · NO DATA = no truthful source.
