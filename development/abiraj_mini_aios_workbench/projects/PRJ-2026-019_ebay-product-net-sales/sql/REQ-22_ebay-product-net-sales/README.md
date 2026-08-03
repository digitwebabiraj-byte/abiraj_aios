# Generator — REQ-22 eBay Product Net Sales

## What will land here
`epns_build_d01.py` — **one module** that connects to `ledsone` (read-only, direct psycopg2), computes
the 12 Net Sales columns at eBay order-line grain over the last 30 days, and writes the Excel deliverable
(Net Sales tab + Net Sales Lookup tab).

**One module, not several** (the REQ-16 drift lesson): the single builder is the only fetch path.

## Non-negotiables for whoever builds it
- **Confirm the deduction set with Kobiga first** — do not infer it from the single sample row. `CLAUDE.md` §1.
- **Product Cost stays `NO DATA`** until a real COGS source is supplied — no 20%-estimate substitution
  without a recorded owner decision. `CLAUDE.md` §2.
- **Money per marketplace currency** — UK £ / DE €, formatted per cell, never blended (DST defect). §3.
- **eBay grain = order_id / item_id; never join sales by SKU alone** (~13× overstatement); `source_id=2`. §4.
- **Read the AIOS knowledge base before writing SQL.** `all_list=1`, VARCHAR casts, parent-row title. §5.
- **Read-only throughout;** credentials from the git-ignored shared store, never committed. §6.
- **Anchor on the last COMPLETE day** for the 30-day window.
- **Reproduce the worked example** (`02-14934-76138` → 22.39) from live data as the first sanity check.
