# Channel Opportunity (chop) — PRJ-2026-021

Concise landing page. Full context in `PROJECT_HOME.md`; execution rules in `CLAUDE.md`; field-by-field
source map in `SYSTEM_REFERENCE.md`.

## What
A **Channel Opportunity Table** for **Mahima**: find products that sell **well in one marketplace but are
weak or missing in others**, so the listing gap can be closed. For each SKU it lays sales side by side
across the three channels — **Shopify · Amazon · eBay** — classifies the **Opportunity** (Shopify winner /
Marketplace winner / Missing channel) and recommends an **Action** (Improve Amazon/eBay listing / Add
Shopify promotion / Create eBay listing …).

## Status
🟢 **SIGNED OFF & CLOSED 2026-08-05 (Mahima).** Published to `ph_task` id 699 (v7). Built & delivered same day — Germany, UNITS metric, rolling 90 days,
sourced from the **RAW `mcp.ledsone` DB** (`order_management`, clean-SKU = strip `-IDE`, data through
2026-08-04); knowledge/query patterns from the AIOS KB (`docs.ledsone.co.uk`). Excel
`REQ-24-D01_channel_opportunity.xlsx` holds **283 opportunity rows** (270 Missing channel · 10 Marketplace
winner · 3 Shopify winner), reconciled against the raw DB on 5 SKUs incl. zero/absent channels (raw = source
of record; agrees with the warehouse mirror within ±2 units). Opportunity/Action use documented DEFAULT
rules (Notes tab) awaiting Mahima. Identity (`PRJ-2026-021` / `REQ-24` / code `chop`) is provisional. Not
published to `ph_task`, not committed.

> ⚠ Every number in the source workbook is an **illustrative sample** (`xyz`, `dgh`, `kytd`, 100 / 5 / 2),
> not real data. It defines the desired columns, Opportunity classes and Action vocabulary only. Nothing
> here is reconciled against `ledsone` yet.

## Deliverable (planned)
- **REQ-24-D01** — Channel Opportunity report, one data layer rendered as:
  - **Excel** — a single cross-channel table (one row per base SKU) + a Notes tab.
  - **HTML dashboard** (optional, per the house pattern) — searchable/sortable, filter by Opportunity class.
  - Builder: single read-only module in `sql/REQ-24_channel-opportunity/`.

## The report shape (from the source workbook)
One table — *"Table: Channel Opportunity — find products selling well in one marketplace but missing in others"*:

`SKU · Shopify Sales · Amazon Sales · eBay Sales · Opportunity · Action`

Sample Opportunity classes: **Shopify winner** · **Marketplace winner** · **Missing channel**.
Sample Actions: **Improve Amazon/eBay listing** · **Add Shopify promotion** · **Create eBay listing**.

## Authoritative documents
- `PROJECT_HOME.md` — canonical project truth
- `SYSTEM_REFERENCE.md` — the column → `schema.table.column` map (DRAFT — to verify live)
- `CLAUDE.md` — execution rules
- `TASK_REGISTER.md` — task/deliverable index

## Next step
Discovery decision sheet to Mahima (scope, market, window, sales metric — units or revenue, the numeric
definition of "selling well" and "missing", the Opportunity classes and Action vocabulary, publish
audience), then read the AIOS knowledge base (`docs.ledsone.co.uk/mcp`) and map every column live against
`ledsone` / the warehouse before building anything.
