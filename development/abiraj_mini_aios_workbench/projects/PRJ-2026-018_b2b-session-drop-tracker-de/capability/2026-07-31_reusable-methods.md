# Reusable Methods — B2B Session Drop Tracker (bsdt)

Locked rules, gotchas and sources worth carrying to other Amazon B2B / traffic reports.

## Locked rules
- **Tier by MAX(prev, current) B2B Sessions** vs editable thresholds (Tier 2 ≥ 5, Tier 3 ≥ 10).
  Session Change / Units / Buy Box % are context — never gate on them.
- **B2B-only columns** (Sessions·Total·B2B, Page Views·Total·B2B, Units ordered·B2B) — never the
  blended B2B+B2C totals. B2B Conversion % is unreliable at .de's low per-ASIN volume — omit it.
- **Include an ASIN only if it has B2B traffic in ≥ 1 window** (sessions or page views).
- **Thresholds are configuration** — editable Thresholds sheet cells `B4`/`B5`; Tier is a live
  formula, never a hardcoded value.

## The headline gotcha — mapping ≠ coverage
A single ASIN reconciling to the unit proves the **column mapping**, not the **coverage**. Here
`B0DLWRP73C` matched exactly (DB 19 = sheet 15+4) yet the DB reproduces only ~half the sheet. **Always
run a full-population completeness test** before declaring a source usable: for every source row, the
windowed total must be ≤ the DB all-time total for that key; count the "impossible" rows.

## Data-source facts (raw `ledsone`, `mcp.ledsone.co.uk`)
- Amazon B2B session/page-view/order data lives **only** in `business_reports.amz_traffic_by_asin`
  (43 cols: `sessions_b2b`, `page_views_b2b`, `units_ordered_b2b`, `buy_box_percentage_b2b`).
- Germany = `market_place = 10` (`order_management.market_place`); .de account = `sub_source = 8`
  (`order_management.sub_source` → "amazon Ledsone").
- 🔴 This mirror is **incomplete for .de B2B**: May 2026 entirely missing, ~half the ASINs absent,
  recent months sparse. **It cannot reproduce a Seller Central B2B report** — the export is the
  system of record. (Sync gap = a data-engineering issue for Sajeesan, not this report's source.)
- The other `business_reports` Amazon table, `amz_catalog_performance_data`, is the Search-Catalog
  funnel (impressions/clicks/cart-adds/purchases) — **no sessions, no B2B**.

## Connector discipline
- Data: **`mcp.ledsone.co.uk`** (`Ledsone-db-mcp`) only. Knowledge: **`docs.ledsone.co.uk`**.
- Do **not** use the generic `postgres`/warehouse connector for this task.

## Build pattern (FRRC-style enrich-the-export)
`build_bsdt.py` reads the owner-supplied export, re-derives Session Change + Tier + Status + Action
from the thresholds, verifies they match the source (fails on any mismatch), and emits a governed
`bsdt_data.json`. `build_xlsx.py` and `gen_dashboard.py` render from that JSON so the two artefacts
never drift. Each cycle needs a fresh 2-window export (the DB can't feed it).
