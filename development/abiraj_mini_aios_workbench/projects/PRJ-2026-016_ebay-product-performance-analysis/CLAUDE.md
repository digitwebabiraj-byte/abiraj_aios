# CLAUDE.md — PRJ-2026-016 eBay Product Performance Analysis

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional.

## Identity
- Project `PRJ-2026-016_ebay-product-performance-analysis` · code `eppr` · Task `REQ-19`.
  Owner Abiraj; Business Validator Thinesh. **IDs provisional** (source has no requirement number;
  REQ-18 is taken by `fauto`). A new day/session does not mint a new Task ID.

## 1. Do NOT invent the profit logic — the source has none
Every apparent formula in `Thinesh task (5).xlsx` is a typed constant. Only **Revenue = Price × Units**
and **Margin = Net ÷ Revenue** tie. Gross/Net Profit and the cost-column semantics are undefined and
must be **decided with Thinesh**, never inferred from the fabricated sample.

## 2. Cost Price is absent — profit columns stay NO DATA
`development.sku_cogs` is empty; no per-SKU product cost exists in the warehouse. Until a real cost
source arrives (`ledsone` `inventory`, or a figure from Thinesh), **Cost Price, Gross Profit, Net
Profit and Profit Margin render `NO DATA`.** Do not substitute the `interim_product_cost_20_percent`
estimate or `sku_selling_cost_rates_v1` percentages as if they were product cost.

## 3. Grain = one row per eBay listing (item_id)
Attribute sales/fees/ad/traffic by item_id (or item_id+market). **Never join sales by SKU alone** —
one SKU is listed under many item_ids and the sales duplicate across every listing (~13× overstatement).

## 4. Money is per marketplace currency, never blended
UK = GBP £, DE = EUR €. Format each money cell with its own symbol; never sum across currencies and
never label a EUR value with £ (the DST defect). There is no FX table.

## 5. Read-only; never fabricate
- READ-ONLY on all warehouse source tables. No INSERT/UPDATE/DELETE/DDL. The only future write would be
  a guarded `ph_task` publish on explicit owner instruction after the audience is named (not yet decided).
- Every filled column traces to a real `schema.table.column`. Unsourceable columns render `NO DATA` —
  never a guess. A `0` is only written where the true value is zero (e.g. a listing with no sales).

## 6. Source of record for the build
- Warehouse `order_management_copy` (host `149.28.134.54:5435`, user `temp_user`) — this build's source
  because `ledsone` was down 2026-07-27. Credentials from the git-ignored shared store, never committed.
- ⚠ `temp_user` **cannot read `staging_ai`** (brand map was retrieved via the postgres MCP and pinned as
  `BRAND_MAP` in the builder). Re-verify brand values if the account roster changes.
- Prefer `ledsone` for Title/Category-name/Cost/PPC-campaign once it is reachable — the warehouse is a
  mirror and is thinner on those fields (Title 86% here vs complete in ledsone).

## 7. One generator module
The report (and any future scheduled run) comes from the single module `sql/REQ-19_.../eppr_build_d01.py`.
Do not fork a second fetch path — that is how REQ-16 drifted.

## 8. Stop conditions (in addition to the workbench's)
- A build is requested that would populate Cost/Gross/Net/Margin by guessing a cost.
- A publish is requested before the audience is named and each recipient verified.
- Any request to add a marketplace write-back or action column (new requirement).

## Vocabulary
item_id = one eBay listing · all_list=1 = the eBay listing filter (KB) · COGS = product cost (absent) ·
Views=Clicks = eBay's single organic click/view metric · NO DATA = no truthful warehouse source.
