# CLAUDE CODE HANDOFF — eBay Return Analysis Dashboard

You are picking up a data task. Reproduce a per-SKU eBay returns dashboard (Excel)
from the **live Ledsone PostgreSQL** database. This brief is self-contained: SQL,
build script, acceptance checks, and pitfalls are all here.

## Package (files in this handoff)
- `ebay_return_analysis.sql` — the two queries (main 19-column dataset + reason breakdown). **Source of truth.**
- `build_dashboard.py` — formats the query outputs into the workbook. Formatting only; no data logic.
- `eBay_Return_Analysis_June2026.xlsx` — reference output to diff against.
- `eBay_Return_Analysis_HANDOFF.md` — long-form column/derivation reference (read if a number looks wrong).

## Environment / data access
- DB is reached through the **Ledsone Database MCP** (`execute_sql`, `search_objects`) — Postgres at `mcp.ledsone.co.uk`. No raw creds; go through the MCP tool.
- Use the **normalised domain schemas** (`customer_service`, `order_management`, `listings`, `inventory`, `ebay_campaigns`, `accounting`). Do **not** use the `public.*` denormalised layer — it belongs to a different DB and returns nothing here.
- Docs knowledge base: **Ledsone AIOS MCP** (`docs.ledsone.co.uk`) — read-only unless you have an API key.

## Task parameters (agreed with Thinesh)
- Channel: **eBay only**, all accounts/marketplaces (UK, DE).
- Period built: **June 2026** (`2026-06-01` → `2026-07-01`). Return Rate = period returns ÷ period units ordered.
- Return Cost = **eBay refund fees + selling fees** (REFUND + FINAL_VALUE_FEE on returned orders).
- Ad columns = **single** Ad Spend / Ad Sales / ACOS / ROAS set (exact task-sheet layout), combining CPC + CPS.
- Comparison windows: Last Month = May 2026, Last Year = June 2025.

## Output columns (exactly 19, in order)
`SKU · Product Title · Account · Orders · Returns · Return Rate · Last Month Returns ·
Last Year Returns · Refund (£) · Return Cost (£) · Main Return Reason · Return Rank ·
Negative Feedback · Open Cases · Stock · Ad Spend (£) · Ad Sales (£) · ACOS · ROAS`
Plus, on the same sheet: Return-Reason Breakdown table, Filter Options block, Before/After efficiency table.

## RUNBOOK
1. **Run statement 1** of `ebay_return_analysis.sql`. Export rows as **tab-separated,
   no header, NULLs as empty string** → `main.tsv`. (Friendly Account, mapped reason
   labels, and `#n` rank are produced by the SQL — do not post-process.)
2. **Run statement 2** (bottom of the .sql) → `reason_breakdown.tsv`
   (`Return Reason<TAB>Returns<TAB>Pct`).
3. `pip install openpyxl` then `python build_dashboard.py main.tsv reason_breakdown.tsv eBay_Return_Analysis_June2026.xlsx`
4. **Recalculate** so cached formula values populate (openpyxl writes formulas with no
   values). Use LibreOffice headless, e.g. the xlsx skill's `scripts/recalc.py`, or
   `soffice --headless --convert-to xlsx`. Confirm `total_errors == 0`.

## ACCEPTANCE CRITERIA (June 2026 — must match the reference file)
- **144** SKU rows; **19** columns in the exact order above.
- Totals row: **153** returns · blended return rate **17.7%** · Refund **£2,937.37** ·
  Ad Spend **£1,387.96** · Ad Sales **£9,343.63** · ACOS **14.9%** · ROAS **6.73x**.
- Reason breakdown sums to **153** (Wrong Size 47 / Ordered Wrong Item 28 / Not as Described 21 / …).
- Zero recalc errors.

## INTENTIONAL BLANKS (do not "fix" by filling with 0)
- **Return Rate** blank on 17 SKUs = zero period orders (returns of earlier-period purchases). Verified.
- **ACOS** blank on 20 / **ROAS** blank on 12 = no ad-attributed sales / no ad spend that SKU. Verified against all listings.
- Count/£ columns DO show real `0` / `£0.00` (do not format zeros as dashes — that made columns look empty).
- Return Cost = £0 on 4 SKUs = no matching fee row upstream (~65% fee coverage) — data limitation, not a bug.

## PITFALLS (each one bit us; the SQL already handles them)
1. **SKU resolution:** join returns→SKU via `transaction_id` → `order_item_info.item_transaction_id`. Joining on `item_id` is WRONG (1,331 item_ids map to multiple variants).
2. **`ebay_campaigns.performance_data` is CPC-only** (all value columns are `cpc_*`). Standard/CPS ad cost is a per-sale fee in `accounting.ebay_order_expenses` (`AD_FEE` / `PREMIUM_AD_FEES`). Ad Spend/Sales = CPC + CPS.
3. **Text-typed numerics:** `item_quantity`, `real_qty`, `item_price`, `real_price` are VARCHAR — cast with `NULLIF(x,'')::numeric`.
4. **Order id mismatch:** `accounting.ebay_order_expenses.order_id` = the eBay order reference (`orders.order_id`, varchar), NOT internal `orders.id`.
5. **Return case fields:** `reason` + `seller_refund_amount` live only on the EARLIEST row per `return_id`; latest STATE is the NEWEST row. Hence the two `DISTINCT ON` CTEs.

## RE-RUN FOR ANOTHER MONTH
Edit the six dates at the top of `ebay_return_analysis.sql` (reporting period, last month,
last year), rerun the runbook, update `PERIOD_LABEL` in `build_dashboard.py`. Stock is
always a live snapshot, never period-bound.
