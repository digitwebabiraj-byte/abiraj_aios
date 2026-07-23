# Generator — REQ-17 Daily Sales Track

**Status: EMPTY. Nothing built.** Blocked on decisions **A, B, C, D, E, F** (see `PROJECT_HOME.md`).

## What lands here

`build_dst_d01.py` — **one module** that pulls both databases, computes the 22 columns and the
9-KPI panel, and renders all three D01 artefacts (governed JSON → HTML dashboard + xlsx workbook).

**One module, not several.** REQ-16 shipped a defect where the workbook and the dashboard were built
from separate fetches and drifted apart. A single module makes that impossible.

## Non-negotiables for whoever writes it

- **Inherit REQ-13's measurement definitions verbatim** — `SUM(order_total)`,
  `COUNT(DISTINCT order_id)`, `SUM(quantity)`, filtered `source_name='EBAY'` and
  `order_status='Completed'`. Do not re-derive them. See `CLAUDE.md` §2.
- **Anchor on the last COMPLETE day** —
  `CASE WHEN MAX(date) < CURRENT_DATE THEN MAX(date) ELSE MAX(date) - 1 END`. See `CLAUDE.md` §3.
- **Blank, never zero**, for any absent figure. See `CLAUDE.md` §4.
- **Trend bands as editable config**, never inlined in SQL.
- **Product titles from `ledsone`**, not the warehouse (only 8.3% populated there).
- **Deterministic ordering** — add a final unique sort key (REQ-16 found 9,222 of 11,176 rows tied on
  its sort columns, so consecutive runs emitted different orderings until `item_id` was appended).
- Read-only throughout. Direct `psycopg2` (no MCP) so the same module can be scheduled later.
