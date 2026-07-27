# Generator — REQ-19 eBay Product Performance Analysis

## What lands here

`eppr_build_d01.py` — **one module** that connects to the warehouse (read-only, direct psycopg2),
computes all 35 columns at eBay-listing (item_id) grain, and writes the Excel deliverable.

**One module, not several** (the REQ-16 drift lesson): the single builder is the only fetch path.

## Non-negotiables for whoever edits it

- **Grain = one row per eBay listing (item_id).** Never join sales by SKU alone — one SKU is listed
  under many item_ids and sales duplicate ~13×. See `CLAUDE.md` §3.
- **Do NOT invent the profit logic.** Cost Price / Gross / Net / Margin stay `NO DATA` until a real
  COGS source exists (`development.sku_cogs` is empty). No 20%-estimate substitution. `CLAUDE.md` §1–2.
- **Money per marketplace currency** — UK £, DE €, formatted per cell, never blended. `CLAUDE.md` §4.
- **`NO DATA` for any unsourceable column; `0` only where the true value is zero** (e.g. a listing
  with no sales in the window). Never fabricate.
- **Read-only throughout.** Direct psycopg2 as `temp_user`; credentials from the git-ignored shared
  store, never committed. `temp_user` cannot read `staging_ai` (brand values are pinned from the MCP).
- **Anchor on the last COMPLETE day** for all flow metrics (30-day window ending `CURRENT_DATE-1`).

## Prefer ledsone when it returns
This build ran warehouse-only because `ledsone` was down. Title (86% here), Category name, Cost Price
and PPC Campaign are all thinner in the warehouse — re-source them from `ledsone` once reachable.
