---
name: postgres-warehouse-sql
description: "Use whenever a question needs data from the company PostgreSQL warehouse via the connected Postgres MCP — sales/orders, organic traffic, PPC/advertising, warehouse stock/inventory, expenses, shipments, returns (Amazon/eBay/Shopify), buyer messages, listings, PH/ASIN segments, keyword phrases, or gate evaluations. Read this before writing any SQL against that database: it routes to the right query-pattern (single-domain, multi-domain, or PPC→stock lookup) and the exact per-table schema references, and enforces the rule that SQL must be EXECUTED via the Postgres MCP and the real results returned — never a SQL block alone. Applies to every project on this machine."
---

# PostgreSQL Warehouse — Text-to-SQL Skill (all projects)

Reusable knowledge base for querying the company PostgreSQL warehouse (`order_management_copy`
and its development twin) through the **connected Postgres MCP** `execute_sql` tool. Use it on any
project that touches this database.

> **Note on the tool name:** older copies of these notes say `postgres:execute_sql`. In practice
> the tool is the connected Postgres MCP's **`execute_sql`** (the connector's GUID rotates per
> session — rely on the tool, not the id). Run all queries through it and return the real rows.

## ⚠️ The one non-negotiable rule

Generating SQL is the **midpoint**, never the answer. Every data question must:

```
1. Detect intent  → choose the right table(s)
2. Generate the SQL
3. EXECUTE it via the Postgres MCP execute_sql tool
4. Return the actual data rows to the user
```

A SQL block shown without executing it is an incomplete response.

## Which pattern to read (progressive disclosure)

Read the matching pattern file in `references/` **before** writing SQL:

| Question shape | Read |
|---|---|
| One data domain (sales/orders **or** traffic **or** PPC **or** stock, etc.) | `references/pattern_single_table.md` |
| Two+ domains joined (e.g. spend **and** stock, orders **and** traffic) | `references/pattern_multi_table.md` |
| Stock/inventory for ASINs / eBay item_ids / Shopify products coming from PPC data (bridge via `listing_data` → inventory, clean-SKU step, top-N spend, zero-stock detection) | `references/pattern_ppc_stock_lookup.md` |

Then open only the specific `references/TABLE_*.md` files for the tables you touch — they carry the
authoritative columns, join keys and gotchas. Do not guess a column; if it isn't in the reference,
say so.

## Table references available (`references/TABLE_*.md`)

- **Orders / sales:** `TABLE_order_transaction.md` (central bridge — ASIN/item_id/product_id/SKU)
- **Listings / SKU resolution:** `TABLE_listing_data.md` (`wrong_sku`, `mapped_sku`, `ref_id`, `which_channel`)
- **Stock / inventory:** `TABLE_inv_final_stock.md`
- **PPC / advertising:** `TABLE_ppc.md`
- **Organic traffic:** `TABLE_traffic_data.md`
- **Expenses:** `TABLE_expense_amz_ebay_shopify.md`
- **Returns:** `TABLE_amazon_returns.md` · `TABLE_ebay_returns.md` · `TABLE_shopify_returns.md`
- **Buyer messages:** `TABLE_amz_msg.md` · `TABLE_ebay_msg.md` · `TABLE_shopify_msg.md` · `TABLE_message_app_logs.md` · `TABLE_msg_tag.md`
- **Segmentation / keywords / gates:** `TABLE_ph_segment.md` · `TABLE_phrases.md` · `TABLE_gate_Evalution.md`

## Standing safety defaults

- **Read-only by default.** Do not `INSERT`/`UPDATE`/`DELETE` or run DDL against live schemas unless
  the project explicitly authorises a specific write; then keep it single-row and guarded.
- **Never invent numbers or mappings.** Every figure traces to a real `table.column`; unclear fields
  are flagged, not decided.
- **SKU resolution** goes through `listing_data` (`wrong_sku=0`, then `mapped_sku` else `sku`) — see
  the pattern files for the full bridge and clean-SKU rules.
