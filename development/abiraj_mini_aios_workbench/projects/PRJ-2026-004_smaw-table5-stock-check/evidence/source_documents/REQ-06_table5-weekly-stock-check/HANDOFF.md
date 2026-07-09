# Weekly Stock Check (Table 5) — Handoff to Claude Code

Resume brief for the **Thuwaraga weekly stock report**. Drop this whole folder into
your Claude Code project directory and tell Claude Code: *"Read HANDOFF.md and continue."*

## Files in this package
- `HANDOFF.md` — this brief
- `generate_dataset.sql` — the query that builds the dataset from the live DB
- `dataset.py` — the current 240-row dataset (Python list `DATA`), already correct on `location_wise`
- `build_report.py` — openpyxl builder; imports `dataset.py`, writes the styled Excel
- `Table5_Weekly_Stock_Check_Thuwaraga.xlsx` — current output

## How to run (once MCP is connected — see below)
    pip install openpyxl --break-system-packages
    python build_report.py     # writes Table5_Weekly_Stock_Check_Thuwaraga.xlsx
To refresh data: run generate_dataset.sql via the Postgresql MCP, then paste the rows into
dataset.py as `DATA = [...]`, and rerun build_report.py.

---

## Connect the SAME data sources in Claude Code (MCP)
The chat used remote/hosted MCP servers. Add them to Claude Code once; they then load every session.
Verify current syntax against the docs, but as of now:

    # hosted (HTTP) MCP servers — same endpoints the web app used:
    claude mcp add --transport http postgres      https://mcp.vintageinterior.co.uk/mcp
    claude mcp add --transport http dev-postgres   https://question-mcp.vintageinterior.co.uk/mcp
    claude mcp add --transport http ledsone-docs   https://docs.ledsone.co.uk/mcp
    # then, inside Claude Code:
    /mcp        # confirm each shows "connected"; complete any OAuth prompt

- Project-scoped alternative: put an `.mcp.json` in the repo root (travels with the project).
- Global: `~/.claude/mcp.json`.
- The production DB is **order_management_copy**, reached through the **postgres** server above.
- Docs: https://docs.claude.com/en/docs/claude-code/mcp  (and `/mcp` inside Claude Code)

---

## What the report is
One row per **(ASIN, account)** for PH **Thuwaraga**, **Amazon UK, FBM only, Completed orders, last 90 days**.
Columns A-O: Last Stock Checked Date | ASIN | Account | Listing SKU | Correct SKU (Master) |
Amazon Listing Qty (FBM) | UK Warehouse Stock (Real) | Last 3-Month Order Count | Sales Velocity |
Days of Stock Remaining | Upcoming Supplier | PO Qty (Incoming) | Container Number | Container Reaching Date | Stock Status.
Colors: header grey E8EAED, healthy peacock 13B4CF, going-out yellow FFEB84, critical red F4A6A6. Font Poppins.

## Locked-in decisions (all verified against the live DB)
1. **PH filter** = order_transaction.user_name='thuwaraga' (NOT ss_name — that's the store/account).
2. **Scope** = Amazon UK, fba_sales=false (FBM), order_status='Completed', last 90 days.
3. **UK stock source = location_wise_inv_stock (location='UK')** — this MATCHES the live inventory UI.
   Do NOT use inv_final_stock; it is stale (only 26% of SKUs agree between the two feeds).
4. **Master SKU resolution** (priority): listing_data.mapped_sku -> order_transaction.sku ->
   suffix-stripped listing SKU (strips trailing _1, " A", -DC, -LV, etc.). Keep the real channel SKU
   in the "Listing SKU" column; show the resolved base in "Correct SKU (Master)".
5. **Velocity** = units sold in 90d / 90. (The "Last 3-Month Order Count" column actually holds UNITS SOLD.)
6. **Days** = UK warehouse / velocity. **Status**: warehouse 0 -> Critical; <15 days -> Critical; <=60 -> Going Out; else Healthy.
7. **Incoming PO** = SUM(ctns*ctn_pcs) from supplier.order_items where supplier.orders.status_arrived=0;
   supplier via supplier.suppliers, container via supplier.final_containers.
8. **Container reaching date** is not stored in the DB -> shown as "-".

## OPEN TASK (blocked — pick up here)
**Legacy->canonical "Mapping SKU" is not in this database.** Example: LDMA60E274 (report shows 0 / Critical)
is a drained legacy alias that the inventory UI maps to LDMA60E274WW (real stock 3,233 -> Healthy).
Affected rows so far: ASINs B0DG25H3RQ, B0DGL8XMR7. Other current criticals may be the same pattern.

Searched the whole DB: the only SKU->SKU column is listing_data.mapped_sku (NULL for these); no SKU-master/
mapping table exists in order_management_copy. **Need the mapping source**, then:
- likely candidates: the **dev-postgres** DB (vintageinterior) may hold the inventory product master, OR
  a Google Sheet / export the user maintains.
- Once found: build a legacy_sku -> canonical_sku dict, apply it BEFORE the stock lookup (resolve alias ->
  canonical), re-pull location_wise UK stock, rebuild dataset.py, rerun build_report.py, then
  **re-run the recalc + a full 240-row reconciliation** against location_wise (0 mismatches expected).

## Validation to run after every rebuild
- Recalc / zero formula errors (xlsx skill): python .../xlsx/scripts/recalc.py <file>  ->  total_errors: 0.
- Reconcile every row's UK stock == location_wise_inv_stock for its master SKU (0 mismatches).
- Spot-check vs the live UI: LDSSTRE274=990, LDMG95E274=8131, LDMST64E274=30120, LDMA60E274=0 (legacy).

## Freshness caveat
location_wise_inv_stock.updated_at = 2026-05-04 (matched the user's screen). If a fresher inventory feed
exists, repoint the `inv` CTE in generate_dataset.sql and re-reconcile.

## "Remaining task also"
This is one of several Table-N reports. Other tables in the project knowledge include traffic, PPC,
returns (amazon/ebay/shopify), messages, expenses, order transactions, etc. Ask which report is next;
reuse the same MCP setup and the same validation discipline (match the live system, reconcile before delivering).
