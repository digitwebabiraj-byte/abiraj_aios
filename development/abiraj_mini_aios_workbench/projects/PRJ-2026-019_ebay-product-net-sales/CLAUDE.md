# CLAUDE.md — PRJ-2026-019 eBay Product Net Sales

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional.

## Identity
- Project `PRJ-2026-019_ebay-product-net-sales` · code `epns` · Task `REQ-22`.
  Owner Abiraj; Business Validator **Kobiga**. **IDs provisional** (source has no requirement number;
  REQ-21 is taken by `bsdt`). A new day/session does not mint a new Task ID.

## 1. Confirm the deduction set — do NOT infer it from one sample row
The source shows a single worked example (`02-14934-76138`: Gross 26.38 − VAT 0.67 − Promotion 0.40 →
22.39) with ≈£2.92 of further, un-itemised deductions. The header formula and the 12-column stack phrase
Net Sales differently. **The exact set of deductions and their sign must be confirmed with Kobiga**
before the builder is written. One reconciled sample row is not a spec.

## 2. Product Cost has no source — it stays NO DATA until one is supplied
No per-SKU COGS exists in any database (`development.sku_cogs` empty; `inventory.products` has no cost;
supplier invoices not SKU-keyed — the EPPR sweep). Until Kobiga supplies a real cost basis, **Product
Cost renders `NO DATA`, and any column derived from it (Net Sales, if it includes Product Cost) is
flagged accordingly.** Do **not** substitute a 20%-of-price or any other estimate as if it were cost
without an explicit, recorded owner decision.

## 3. Money is per marketplace currency, never blended (the DST defect)
`orders.total` and every money field are in the marketplace's own currency (UK £ / DE €), never GBP, and
there is no FX table. Format each money cell with its own symbol; never sum across currencies and never
label a EUR value with £.

## 4. eBay grain — never join sales by SKU alone
Attribute sales/fees/promotion/ad by order_id / item_id. One SKU is listed under many item_ids and sales
duplicate across every listing (~13× overstatement). Isolate eBay with `sub_source.source_id=2` (else
Shopify/Amazon rows leak in).

## 5. Source of record = raw `ledsone`; read the KB first
- Prefer **raw `ledsone`** for eBay orders/SKU/account/fees/promotion/PPC (the EPPR/EPPA/DST pattern).
  The warehouse is a thinner mirror and hides SMART campaigns.
- **Read the AIOS knowledge base (`docs.ledsone.co.uk/mcp`) before writing any SQL** — skipping it caused
  wrong builds twice. Apply `source_id=2`, `all_list=1`, VARCHAR casts, parent-row title trap.

## 6. Read-only; never fabricate
- READ-ONLY on all source tables. No INSERT/UPDATE/DELETE/DDL. The only future write is a guarded
  `ph_task` publish on explicit owner instruction after the audience is named and each recipient verified.
- Every filled column traces to a real `schema.table.column`. Unsourceable columns render `NO DATA` —
  never a guess. A `0` is written only where the true value is zero.
- Credentials come from the git-ignored shared store, never committed.

## 7. One generator module
The report (and any future scheduled run) comes from a single module
`sql/REQ-22_.../epns_build_d01.py`. Do not fork a second fetch path — that is how REQ-16 drifted.

## 8. Stop conditions (in addition to the workbench's)
- A build is requested before the deduction set and Product Cost handling are confirmed with Kobiga.
- A build would populate Product Cost / Net Sales by guessing a cost.
- A publish is requested before the audience is named and each recipient verified.
- Any request to blend currencies or report a single GBP total across marketplaces.

## Vocabulary
NNV = Net Nominal/Net Sales value · FVF = Final Value Fee (eBay's per-sale commission) ·
source_id=2 = the eBay channel filter · Promotion = eBay markdown/promoted-listing discount ·
General = catch-all "additional fees" bucket (define with Kobiga) · NO DATA = no truthful source.
