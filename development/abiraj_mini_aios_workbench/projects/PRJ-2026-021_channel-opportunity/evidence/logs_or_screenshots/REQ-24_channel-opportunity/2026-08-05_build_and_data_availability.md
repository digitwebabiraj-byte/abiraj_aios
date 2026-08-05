# REQ-24-D01 — Build & Data-Availability note (2026-08-05, RAW-sourced)

Read-only build of the Channel Opportunity report from the **RAW `ledsone` Postgres DB** via the
`mcp.ledsone.co.uk` MCP (host 169.58.91.229, `order_management` schema). Knowledge/query patterns from the
AIOS knowledge base (`docs.ledsone.co.uk`, `text-to-sql-multi`). No writes, no DDL, no publish.

> ⚠ First build (earlier same day) sourced the curated warehouse `public.order_transaction` via the
> AIOS-KB connector. On the owner's instruction the data source was moved to the **raw `mcp.ledsone` DB**;
> the raw figures below are now the source of record. They reconcile to the warehouse within ±2 units on
> edge SKUs (merged-shipment / combo attribution) — see the reconciliation table.

## Raw source mapping (order_management)
- `orders o` — `status='Completed'`, `market_place='10'` (= Germany, confirmed via `order_management.market_place`),
  `order_date` window; `sub_source_id → sub_source.id`.
- `sub_source ss.source_id → source.id`; `source.source_name IN ('AMAZON','EBAY','SHOPIFY')`.
- `order_item_info oii.order_id → orders.id`; units = `oii.item_quantity` (VARCHAR → numeric).
- **Clean-SKU step (mandatory):** base SKU = `COALESCE(NULLIF(real_sku,''), item_sku)` with the listing
  suffix **`-IDE`** stripped. `-IDE` is the only systematic suffix (3,758 rows; every other trailing tag ≤13,
  i.e. genuine SKU parts). Multi-packs (`2PK`…) and combos (SKUs containing `+`) are distinct products, kept separate.

## Scope as built (documented defaults — Mahima to confirm)
Market = Germany (id 10) · channels Shopify/Amazon/eBay · `status='Completed'` · metric = **UNITS** ·
window = rolling **90 days**, data through **2026-08-04** · grain = one row per clean base SKU.

## Data availability (Germany, 90-day, Completed, raw)
Distinct clean base SKUs selling in DE: **2,436**. Deliverable = **283 opportunity rows**:
- **Missing channel — 270** (sells ≥10 somewhere, 0 units in ≥1 channel → create the missing listing).
- **Marketplace winner — 10** (Amazon+eBay ≥60% of units, Shopify ≤20% → add Shopify promotion).
- **Shopify winner — 3** (Shopify ≥50% of units and top channel → improve the weak marketplace listing).
Balanced SKUs (selling evenly) are excluded — not an opportunity.

## Reconciliation — raw clean-SKU vs the curated warehouse mirror (5 SKUs)
| SKU | RAW sh/am/eb | Warehouse sh/am/eb | Note |
|---|---|---|---|
| LDMST64E274 | 96/0/43 | 96/0/43 | exact (folds `LDMST64E274` + `LDMST64E274-IDE`) |
| PHUH0.5HETBM | 91/0/0 | 91/0/0 | exact |
| LHSHE27CO | 64/3/39 | 66/3/39 | Shopify ±2 (merged-shipment edge) |
| 12IP6710 | 5/0/107 | 5/1/105 | eBay ±2; Amazon 0 (raw) vs 1 (warehouse folded a stray combo unit) |
| 12IP6715 | 15/0/93 | 15/0/95 | eBay ±2 |

The ±2 residuals never change an Opportunity class. Where raw and warehouse disagree, the **raw operational
DB is taken as the source of record** per the owner's instruction (12IP6710 therefore classes as
*Missing channel*, Amazon=0, not *Marketplace winner*).

## Notes / open
- Opportunity/Action **thresholds are documented DEFAULTS** (Notes tab), owner-pending (Mahima):
  FLOOR=10, Shopify-winner ≥50% share, Marketplace-winner ≥60% marketplace & ≤20% Shopify.
- Product Name/Category not required by the source mock-up; omitted (raw order lines carry no clean category).
- Builder: `sql/REQ-24_.../build_chop_d01.py` reads the governed raw snapshot
  `chop_payload_2026-08-05.json` (2,436 SKUs) → classifies → Excel. Not published, not committed.
