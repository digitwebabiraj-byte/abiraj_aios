# SYSTEM_REFERENCE — REQ-22 eBay Product Net Sales

Field-by-field map: each of the 12 columns → its intended source. **DRAFT — not yet verified live
against `ledsone`.** Sources below are the *expected* homes carried in from prior eBay projects
(EPPR / EPPA / DST / ERA); each must be confirmed in discovery before the builder trusts it.

## Grain & window (to confirm with Kobiga)
- Proposed grain: one row per eBay **order line** (Order ID × SKU), eBay only (`sub_source.source_id=2`).
- Window: rolling **last 30 days** of order data, anchored on the last complete day.
- Marketplace scope: confirm UK only vs UK+DE. Money **per marketplace currency**, never blended.

## Column map (draft)
| # | Column | Expected source | Note / risk |
|---|---|---|---|
| 1 | Order ID | `order_management.orders.order_id` (eBay, source_id=2) | e.g. `02-14934-76138` |
| 2 | SKU | eBay listing / order line SKU (`all_list=1`, real SKU) | SKU-sprawl trap — attribute by item_id |
| 3 | Account | `order_management.sub_source.name` (source_id=2) | store/account name |
| 4 | Gross Sales | order line `item_price × item_quantity` (CAST VARCHAR) | **per marketplace currency** |
| 5 | VAT (20%) | derived: `revenue − revenue/(1+rate)`, 20% UK | derived estimate, not booked |
| 6 | Promotion % | eBay promotion/markdown discount on the order | confirm %-vs-amount with Kobiga |
| 7 | Final Value Fee | `accounting.ebay_order_expenses.fee` (FVF fee types) | per order/item_id, not per SKU |
| 8 | **Product Cost** | 🔴 **NO SOURCE** — no per-SKU COGS in any DB | blocker — see below |
| 9 | Postage | `orders.shipping_cost` / `order_shipping_billing_detail.carrier_charge` | per sale |
| 10 | PPC Cost | `ebay_campaigns.performance_data` (CPC) + `ebay_order_expenses` AD_FEE (CPS) | EPPA lesson; CPS may log £0 |
| 11 | General | catch-all "additional fees" bucket | **define with Kobiga** — undefined in source |
| 12 | **Net Sales (NNV)** | derived: Gross − VAT − Promotion − FVF − Product Cost − Postage − PPC − General | inherits #8's `NO DATA` risk |

## 🔴 Product Cost is unsourceable (the EPPR sweep)
No real per-SKU COGS exists anywhere: `development.sku_cogs` is EMPTY, `inventory.products` has no cost
column, and `suppliers.invoices.unit_price` is not SKU-keyed. Until Kobiga supplies a cost basis, column
8 stays `NO DATA` and Net Sales (col 12) is computed **excluding** Product Cost with a visible flag, or
held, per the owner decision. **No 20%-estimate substitution without a recorded owner decision.**

## Worked-example reconciliation target
Order `02-14934-76138`: source shows Gross `26.38`, VAT `0.67`, Promotion `0.40`, Net Sales `22.39`.
Gross − VAT − Promotion = `25.31`, so ≈`2.92` of FVF + Postage + PPC + General (+ Product Cost?) is
implied. **This single row is the first thing the builder must reproduce from live data** — but it is a
reconciliation *check*, not a source of the deduction logic (which comes from Kobiga).

## Key ledsone rules to apply (AIOS KB — read before SQL)
- `source_id=2` isolates eBay (else Shopify/Amazon leak in).
- `all_list=1` for real SKUs; title/image on the parent row (`all_list=0`).
- `order_item_info.item_price` / `item_quantity` are VARCHAR → CAST.
- `ebay_campaigns.*.ebay_listing_id` = the eBay item_id — the ad/campaign join key.
- Money per marketplace currency; no FX table (the DST currency trap).

> Everything above is a **starting hypothesis**. Replace each row with a confirmed
> `schema.table.column` + coverage % after the live discovery sweep, exactly as EPPR's did.
