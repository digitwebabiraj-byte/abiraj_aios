# PROJECT_HOME — eBay Product Net Sales (epns)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-019_ebay-product-net-sales` |
| **Project code** | `epns` *(provisional)* |
| **Task ID** | `REQ-22_ebay-product-net-sales` *(provisional — REQ-21 = `bsdt`)* |
| **Status** | ✅ **CLOSED — DELIVERED · PUBLISHED · AUTOMATED · SIGNED OFF (Kobiga) 2026-08-03.** Settled-only 4,072 orders from live ledsone; NNV = Gross − FVF − General(AD_FEE) ties to eBay payout (anchor 22.39). Published `ph_task` ids 594–599 (ebay_priors). Weekly auto-refresh `EPNS_Weekly_Net_Sales` (Wed 11:30, proven). Git `main` `e38dc7a`. See `closure/REQ-22_.../2026-08-03_closure_signoff.md`. |
| **Opened** | 2026-08-03 |
| **Owner** | Abiraj · **Tech** Sajeesan · **Queryability** Tamil Selvan |
| **Business Validator** | **Kobiga** (requester / PH). Likely publish audience = `ebay_priors` (kobiga is a member) — to confirm. |

> ⚠ IDs provisional (source has no requirement number). Do not mint a new Task ID on a new day/session.

## Business question
For each eBay order in the last 30 days: what did it gross, what came off it (VAT, promotion, eBay Final
Value Fee, product cost, postage, PPC, general), and what is the resulting **Net Sales (NNV)**? Plus:
look up the Net Sales of any single Order ID on demand.

## The Net Sales formula (canonical, from the source workbook)
```
Net Sales (NNV) = Gross Sales
                − VAT (20%)
                − Promotion
                − Final Value Fee
                − Product Cost
                − Postage
                − PPC Cost
                − General
```
The source phrases it two ways that must be reconciled during discovery:
- Header formula: `Net Sales = NNV − Promotion Cost − Final Value Fee − Additional Fees`.
- Column stack (the 12 columns) implies the fuller deduction list above.
The worked example (Order `02-14934-76138`) shows Gross `26.38`, VAT `0.67`, Promotion `0.40` →
Net `22.39`. Those three alone give `25.31`, so **≈£2.92 of further deductions** (FVF / cost / postage /
PPC / general) are implied but not itemised in the sample. **The exact deduction set must be confirmed
with Kobiga before building — do not infer it from the single sample row.**

## Grain & window
- One row per eBay **order line** (Order ID × SKU). Confirm with Kobiga whether the grain is per order,
  per order-line (SKU), or per SKU aggregated.
- Rolling **last 30 days** of order data, anchored on the last complete day.

## Columns (12, canonical order from the source)
Order ID · SKU · Account · Gross Sales · VAT (20%) · Promotion % · Final Value Fee · Product Cost ·
Postage · PPC Cost · General · **Net Sales (NNV)**

## 🔒 Source (to confirm in discovery — follow the eBay-project house rule)
- **Raw `ledsone` Postgres** is the source of record for eBay orders/SKU/account/fees/promotion
  (the EPPR / EPPA / DST pattern) — the warehouse hides SMART campaigns and is thinner.
- **AIOS knowledge base** (`docs.ledsone.co.uk/mcp`) — **read before writing any SQL** (`source_id=2`
  for eBay, `all_list=1`, VARCHAR casts, the parent-row title trap).
- **Warehouse** only if a feed has no `ledsone` source.

## 🟠 Known blockers / traps carried in from prior eBay projects
- **Product Cost has NO source.** No per-SKU COGS anywhere (`development.sku_cogs` empty;
  `inventory.products` has no cost; supplier invoices not SKU-keyed). Either Kobiga supplies a cost
  basis, or the column is `NO DATA` / an explicitly-flagged owner-agreed estimate. **Never silently guess.**
- **Currency trap (DST):** `orders.total` is in the **marketplace's own currency**, never GBP, and there
  is no FX table. Net Sales must be reported per marketplace currency, never blended.
- **Final Value Fee / eBay Fees:** live in `accounting.ebay_order_expenses` (fee types) — attribute per
  order/item_id, not per SKU.
- **PPC / Ad Cost:** eBay CPC (`ebay_campaigns.performance_data`) + CPS (`ebay_order_expenses` AD_FEE) —
  the EPPA lesson; the SMART/CPS spend often logs £0 in the warehouse.
- **VAT** is a derived standard-rate estimate (20% UK), not a booked figure.
- **eBay grain / SKU sprawl:** never join sales by SKU alone (one SKU → many item_ids, ~13× overstatement).

## Deliverables (planned)
- Excel: `evidence/final_outputs/REQ-22_.../REQ-22-D01_ebay_product_net_sales.xlsx`
  - **Tab 1 — Net Sales:** the 12-column per-order table.
  - **Tab 2 — Net Sales Lookup:** enter an Order ID, return its Net Sales and the full deduction breakdown.
- Builder: `sql/REQ-22_.../epns_build_d01.py` (single read-only module — the one-fetch-path rule).

## Reviewer gates (none passed yet)
Sajeesan (technical) · Tamil Selvan (queryability) · Kobiga (business).

## Next actions
1. **Discovery decision sheet to Kobiga:** confirm grain (order vs order-line vs SKU), the exact
   deduction set, the Product Cost source, promotion %-vs-amount, and the marketplace scope (UK only? +DE?).
2. Confirm the provisional `PRJ-2026-019` / `REQ-22` / `epns` identity (cosmetic).
3. Read the AIOS knowledge base, then map every column live against `ledsone` into `SYSTEM_REFERENCE.md`.
4. Build the single generator module; reconcile the worked example against real data.
5. Decide publish audience (`ph_task`, likely `ebay_priors`) — no publish, no git commit until signed off.
