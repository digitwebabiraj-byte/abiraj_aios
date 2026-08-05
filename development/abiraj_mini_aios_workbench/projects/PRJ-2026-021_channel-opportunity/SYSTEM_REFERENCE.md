# SYSTEM_REFERENCE — REQ-24 Channel Opportunity

Field-by-field map: each report column → its intended source. **DRAFT — not yet verified live against
`ledsone` / warehouse.** Sources below are the *expected* homes carried in from prior projects
(FMP / EPPR / DST / text-to-sql-multi); each must be confirmed in discovery before the builder trusts it,
and each row updated with a real `schema.table.column` + coverage %.

## Grain, window & scope (to confirm with Mahima)
- Grain: **one row per base SKU**, with the three channels pivoted onto that row.
- Window: not stated in the source — confirm (rolling 30/90-day, or a fixed month, + anchor).
- Scope: market TBC (fmp sibling is DE). Sales metric TBC — **units preferred** over revenue (avoids the
  currency trap); if revenue, money is per-marketplace currency, never blended.

## Column map (draft)
| # | Column | Expected source | Note / risk |
|---|---|---|---|
| 1 | SKU | clean **base SKU** (`listing_data`, `all_list=1`, clean-SKU step) | cross-channel roll-up key; never a per-channel Product ID |
| 2 | Shopify Sales | orders units (or revenue), `which_channel=3`, window, per base SKU | Shopify item_id trap (see KB) |
| 3 | Amazon Sales | orders units (or revenue), `which_channel=1`, window, per base SKU | parent/child; title on `all_list=0` |
| 4 | eBay Sales | orders units (or revenue), `which_channel=2`, `source_id=2`, window, per base SKU | **attribute by order_id/item_id, not SKU** (~13× sprawl) |
| 5 | Opportunity | derived classifier (Shopify winner / Marketplace winner / Missing channel) | **business rule — thresholds define with Mahima** |
| 6 | Action | derived rule engine (Improve …/Add …/Create …) | **vocabulary + mapping define with Mahima** |

## Optional supporting source (to strengthen "Missing channel")
| Column | Source | Note |
|---|---|---|
| has-live-listing per channel | `listing_data` (`all_list=1`) LEFT JOIN per channel | proves a real gap (no listing), not merely no sales |

## Key rules to apply (AIOS KB — read before SQL)
- **Multi-domain** (Orders × 3 channels, optionally Listings) → `text-to-sql-multi`.
- Channels: Amazon `which_channel=1`, eBay `which_channel=2`, Shopify `which_channel=3`.
- eBay: `source_id=2`; attribute by order_id/item_id, never SKU alone.
- `all_list=1` for real SKUs; title/image on the parent row (`all_list=0`).
- `order_item_info.item_price` / `item_quantity` are VARCHAR → CAST (only if revenue metric).
- "Missing channel" via LEFT JOIN / absence — never assumed.
- Money per marketplace currency; no FX table (the DST currency trap) → prefer units.

## Open source questions (blockers for the builder)
1. **Sales metric** — units or revenue?
2. **Opportunity thresholds** — what separates winner / weak / missing numerically?
3. **Action** vocabulary and its mapping from the Opportunity class.
4. **Window** (rolling 30/90-day vs fixed month) + anchor.
5. **Market scope** — DE-only (like fmp) or all marketplaces?

> Everything above is a **starting hypothesis**. Replace each row with a confirmed `schema.table.column`
> + coverage % after the live discovery sweep, exactly as EPPR's / FMP's did.
