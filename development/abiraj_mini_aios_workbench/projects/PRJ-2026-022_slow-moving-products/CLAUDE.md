# CLAUDE.md — PRJ-2026-022 Slow Moving Products

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional.

## Identity
- Project `PRJ-2026-022_slow-moving-products` · code `smp` · Task `REQ-25`. Owner Abiraj; Business
  Validator **Mahima**. **IDs provisional** (source is a spec mock-up, no requirement number; REQ-24 is
  taken by `channel-opportunity`). A new day/session does not mint a new Task ID.
- This is the **inverse of PRJ-2026-020 Fast Moving Products** — same PH, market and data foundation.
  Reuse FMP's proven query/build pattern; do not fork a second data path.

## 1. The source workbook is a layout spec, not data
Every value in `mahima task (2).xlsx` (ABC123, "High stock" → "Create bundle", the quantities) is an
**illustrative sample**. It defines the desired **columns and Reason/Action vocabulary** only. Never copy
a sample number or label into a deliverable. Every delivered figure traces to live `ledsone` data.

## 2. Do NOT invent the slow-moving rules
"Slow moving", the **Reason** and the **Action** are business rules, not raw columns. The current build
uses **documented default rules** (Notes tab / dashboard banner / `SYSTEM_REFERENCE.md` §4) explicitly
flagged **provisional — pending Mahima**. Do not present them as agreed logic and do not silently change
thresholds. The slow-moving cutoff (30d vs 60/90d vs top-N), the Days-Without-Sale convention and the
Reason/Action vocabulary must be confirmed with Mahima.

## 3. This is DE — never blend currencies (the DST defect)
The report is Germany. It is currently **unit-count only** (no money column). If revenue is ever added it
is **€** — never sum across marketplaces of different currency, never label a EUR value with £.

## 4. Grain = SKU-wise, one consolidated list
One row per SKU, sales summed across all its listings (the grain Mahima confirmed for FMP #020 on
2026-08-05). Never join eBay sales by SKU alone at the listing grain (SKU sprawl, ~13× overstatement);
the SKU-wise `GROUP BY item_sku` + `source_id` filter handles it.

## 5. Stock resolution
Current Stock = `inventory.local_inventory_current_stock_location_wise.stock` summed per `products.sku`,
filtered to `warehouse_location='Germany'`. Combo titles are `"Combo Default Title."` placeholders → fall
back to the SKU for the name; do not display the placeholder.

## 6. Source of record + read the KB first
- Multi-domain (Orders + Stock, 3 channels) → raw `mcp.ledsone` (`order_management` + `inventory`),
  reachable via `Ledsone-db-mcp` execute_sql (host 169.58.91.229) or LED_* env creds for the local build.
- Read the AIOS knowledge base (`docs.ledsone.co.uk/mcp`) before writing any new SQL.

## 7. Read-only; never fabricate
- READ-ONLY on all source tables. No INSERT/UPDATE/DELETE/DDL. The only future write is a guarded
  `ph_task` publish on explicit owner instruction after the audience is named and each recipient verified.
- Every filled column traces to a real `schema.table.column`. Days Without Sale renders **"Never"** when
  there is no sale on record — never a guessed number. A `0` is written only where the true value is zero.
- Credentials come from the git-ignored shared store, never committed.

## 8. One generator module
The report (and any future scheduled run) comes from the single module
`sql/REQ-25_slow-moving-products/build_smp_d01.py`. Do not fork a second fetch path.

## 9. Stop conditions (in addition to the workbench's)
- A rule change (slow cutoff, Reason/Action vocabulary, Days-Without-Sale convention) is requested without
  Mahima's confirmation → keep the documented default and flag it, do not silently invent.
- A publish is requested before the audience is named and each recipient verified.
- Any request to blend currencies or add a money column across channels of different currency.

## Vocabulary
Slow moving = holds German stock but 0 units sold in last 30 days (provisional) · Days Without Sale =
today − last sale date (all-time), "Never" = no sale on record · Reason / Action = inventory rule-engine
output (provisional) · source_id 1/2/3 = Amazon/eBay/Shopify · NO DATA / "Never" = no truthful source.
