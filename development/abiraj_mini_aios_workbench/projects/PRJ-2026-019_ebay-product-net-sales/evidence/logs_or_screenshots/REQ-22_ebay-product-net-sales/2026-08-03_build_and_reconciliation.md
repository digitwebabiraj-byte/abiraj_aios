# Build & Reconciliation record — REQ-22-D01 eBay Product Net Sales

Run live 2026-08-03 against the **raw ledsone** DB (`mcp.ledsone.co.uk`, read-only). Read the AIOS
knowledge base first (source_id=2, VARCHAR casts). All figures below are from the live DB.

## Universe
- eBay orders (`sub_source.source_id = 2`), `order_date` in the last 30 days ending the last complete
  day (`>= CURRENT_DATE-30 AND < CURRENT_DATE`), `status IN ('Completed','New','Inprogress')`.
- **4,432 orders** (grain = one row per order; multi-line orders are 5.5% — SKUs concatenated with ` | `).

## The decoded deduction stack (from order 02-14934-76138)
| Component | Source | Value on anchor |
|---|---|---|
| Gross Sales | `orders.total` (post-promotion) | 26.38 |
| Final Value Fee | `accounting.ebay_order_expenses.fee` WHERE `transaction_type='SALE'` (FINAL_VALUE_FEE + FINAL_VALUE_FEE_FIXED_PER_ORDER + REGULATORY_OPERATING_FEE + INTERNATIONAL_FEE) | 3.40+0.48+0.11 = 3.99 |
| PPC Cost | `ebay_order_expenses.fee` WHERE `fee_type IN ('AD_FEE','PREMIUM_AD_FEES')` | 0.00 (not promoted) |
| General | `ebay_order_expenses.fee` WHERE `fee_type IN ('INSERTION_FEE','OTHER_FEES','SUBTITLE_FEE','INTERNATIONAL_LISTING_FEE','GALLERY_PLUS_FEE','PAYMENT_DISPUTE_FEE')` | 0.00 |
| **Net Sales (NNV)** | Gross − FVF − PPC − General | **22.39** |

✅ **Ties to the penny** to the source worked example (22.39) **and** to `ebay_order_expenses` SALE
`transaction_amount` (22.39) for the same order. `order_marketplace_fee` (3.99) independently confirms the FVF bucket.

## Reconciliation totals (per currency — NEVER blended)
| Currency | Orders | Gross | Final Value Fee | PPC | Net Sales (NNV) |
|---|---|---|---|---|---|
| GBP (UK) | 3,231 | 58,411.31 | 8,461.32 | 3,646.53 | 46,303.46 |
| EUR (DE+FR+IE+IT) | 1,180 | 29,213.85 | 5,249.13 | 2,417.14 | 21,547.58 |
| USD (US) | 21 | 975.03 | 96.88 | 28.54 | 849.61 |

Workbook re-read with pandas reproduces these exactly.

## Column verdicts
- **Sourced & reconciled:** Order ID, SKU, Account, Marketplace, Currency, Order Date, Gross Sales,
  Promotion, Final Value Fee, Postage, PPC Cost, General, Net Sales (NNV).
- **VAT (20%)** — DERIVED estimate (`total − total/1.2`), shown for context, **not deducted from NNV**
  (output VAT is remitted to HMRC separately).
- **Product Cost** — 🔴 **NO DATA.** Swept every ledsone schema 2026-08-03: no per-SKU COGS anywhere
  (`inventory` has no cost column; only `business_reports.amz_search_query_performance` median *market*
  price exists, which is not our cost). Column ships literally `NO DATA`.

## Ad-fee attribution notes
- `AD_FEE` (CPC) carries `order_id` + `item_id` → per-order attributable.
- `PREMIUM_AD_FEES` (CPS) has no `order_id` but has `item_id` (= `order_item_info.item_transaction_id`);
  bucketed into PPC via the eBay `order_id` present on the row set used, then summed per order.

## Open decision for Kobiga (does not block delivery)
The delivered **Net Sales (NNV)** = eBay net payout (Gross − eBay fees). If Kobiga wants a **true net
profit** that also subtracts VAT and Product Cost, a real COGS source is required (Product Cost is NO DATA).
The source's small "VAT 0.67 / Promotion 0.40" panel does not reconcile to 22.39 and was illustrative.
