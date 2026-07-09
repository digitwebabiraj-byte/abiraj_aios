# SYSTEM_REFERENCE — SMAW Table 5 Weekly Stock Check

Functional reference for the Table 5 weekly stock-check report. Locked rules below are verified
against the live DB (`order_management_copy`, read-only). Source of these rules: the imported
`evidence/source_documents/REQ-06_table5-weekly-stock-check/HANDOFF.md`.

## 1. What the report is

One row per **(ASIN, account)** for PH **Thuwaraga** — **Amazon UK, FBM only, Completed orders,
last 90 days**. 15 columns:

Last Stock Checked Date · ASIN · Account · Listing SKU · Correct SKU (Master) · Amazon Listing
Qty (FBM) · UK Warehouse Stock (Real) · Last 3-Month Order Count (holds **units sold**) · Sales
Velocity · Days of Stock Remaining · Upcoming Supplier · PO Qty (Incoming) · Container Number ·
Container Reaching Date · Stock Status.

Current build: **240 rows** — 231 Healthy · 9 Critical · 8 zero-stock.

## 2. Locked data rules (verified)

| # | Rule |
|---|---|
| 1 | **PH filter** = `order_transaction.user_name='thuwaraga'` (NOT `ss_name`, which is the store/account). |
| 2 | **Scope** = Amazon UK · `fba_sales=false` (FBM) · `order_status='Completed'` · last 90 days. |
| 3 | **UK stock source = `public.location_wise_inv_stock` WHERE location='UK'** — matches the live inventory UI. **Do NOT use `inv_final_stock`** (stale; ~26% agreement). |
| 4 | **Master SKU resolution priority:** `listing_data.mapped_sku` → `order_transaction.sku` → suffix-stripped listing SKU. Keep the real channel SKU in "Listing SKU"; show the resolved base in "Correct SKU (Master)". |
| 5 | **Velocity** = units sold in 90d ÷ 90. ("Last 3-Month Order Count" column holds UNITS SOLD.) |
| 6 | **Days** = UK warehouse ÷ velocity. **Status:** warehouse 0 → Critical; <15 days → Critical; ≤60 → Going Out; else Healthy. |
| 7 | **Incoming PO** = `SUM(ctns × ctn_pcs)` from `supplier.order_items` where `supplier.orders.status_arrived=0`; supplier via `supplier.suppliers`, container via `supplier.final_containers`. |
| 8 | **Container reaching date** is not stored in the DB → shown as "–". |

## 3. Presentation spec (D02)

- Colours: header grey `E8EAED` · Peacock `13B4CF` (Healthy) · Yellow `FFEB84` (Going Out) ·
  Red `F4A6A6` (No Stock / Critical). Font: Poppins.
- The HTML dashboard (`build_html.py` → `Table5_Weekly_Stock_Check_Thuwaraga.html`) adds: KPI
  tiles, a dynamic Priority-Actions line, search, clickable status filters, sortable columns,
  Export-CSV (current view) and Print/PDF (colour-faithful). `LEGACY?` tag auto-flags legacy-alias
  rows. Days-of-cover over 365 displayed as `365+` (true value on hover).
- Row colouring is a **presentation-layer** concern (out of SQL scope in D01).

## 4. Rebuild / refresh procedure

1. **Refresh data:** run `sql/REQ-06_table5-weekly-stock-check/generate_dataset.sql` via the
   Postgresql MCP; paste rows into `dataset.py` as `DATA = [...]`.
2. **Rebuild dashboard:** `python build_html.py` → `Table5_Weekly_Stock_Check_Thuwaraga.html`.
3. **Rebuild Excel (optional):** `python build_report.py`.
4. **Validate:** reconcile every row's UK stock == `location_wise_inv_stock` for its master SKU
   (0 mismatches); spot-check vs live UI (LDSSTRE274=990 · LDMG95E274=8,131 · LDMST64E274=30,120 ·
   LDMA60E274=0 legacy · LDMA60E274WW=3,233); xlsx recalc → total_errors: 0.

## 5. Known limits / open items

- **Legacy→canonical SKU aliases** (e.g. `LDMA60E274` 0 → `LDMA60E274WW` 3,233): no SKU→SKU master
  map in the DB beyond `listing_data.mapped_sku` (NULL for these). Unverified candidates:
  `staging_ai.cppc_sku_identity_resolver_v1` (card_sku→resolved_sku),
  `staging_ai.amazon_asin_internal_sku_bridge_v1`. Rows flagged, not corrected.
- **Sales-only universe:** no-sales-but-in-stock ASINs are excluded; full-portfolio expansion needs
  a PH→ASIN ownership source + live re-pull (decision pending).
- **UNPROVEN fields:** Amazon FBA on-hand · container ETA · W1/W2/W3 mapping · authoritative stock-
  checked date.
- Inventory feed frozen at `2026-05-04`.
