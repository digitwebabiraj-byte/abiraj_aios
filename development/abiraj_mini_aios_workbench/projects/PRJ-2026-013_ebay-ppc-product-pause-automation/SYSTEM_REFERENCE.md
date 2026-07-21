# SYSTEM_REFERENCE — eBay PPC Product Pause Automation (EPPA)

**Project:** PRJ-2026-013_ebay-ppc-product-pause-automation · **code** `eppa`
**Derived from:** the two canonical sources in
`evidence/source_documents/REQ-15_ebay-ppc-product-pause-automation/` (HTML is canonical for logic)
**Written:** 2026-07-21

This is the complete functional description of what the system does, for a leader or a new engineer.
It separates **what the mockup specifies** from **what the live warehouse can actually supply**
(established by the Step-2 audit, 2026-07-21).

---

## 1. Purpose

For LEDSone's eBay Promoted Listings on the **UK** marketplace, decide — on a repeating schedule —
which advertised listings should stop being advertised, because they are either **unsellable**
(no stock) or **losing money** (ACOS above ceiling, or clicks with no sales). Every decision is
explained in plain English and routed to a human for approval.

The governing idea, taken from the mockup's own comments: **availability beats performance.** A
listing that cannot be bought is paused before any efficiency rule is even considered.

---

## 2. Rule engine — the ordered gates

Evaluated top to bottom per listing. **First match wins**; later rules are not consulted.

### Gate 0 — State check
If the campaign is OFF (or the listing is OFF), the listing is **not evaluated at all**. Its status
is `ALREADY OFF` and every rule column reads "—". Rationale: rules are not run against an entity
that is not running.

### Gate 1 — Stock rule
```
units in stock < stock_floor (5)          -> PAUSE
```
Sub-classified for the reason text and priority:
- `units = 0` → "Out of stock — ads paused so spend does not run on an unbuyable item." → always **High** priority.
- `0 < units < floor` → "Low stock (N units, below the 5-unit floor) — ads paused to protect the remaining units."

### Gate 2 — Rule 1, high ACOS
```
scope:      30D orders > 0                       (ACOS is only meaningful with sales)
condition:  30D ACOS >= acos_ceiling (40%)
rescue:     7D ACOS < acos_rescue (20%)  -> DO NOT PAUSE (improving trend)
```
Pauses only when the 30-day figure breaches the ceiling **and** the last 7 days have not recovered.

### Gate 3 — Rule 2, clicks without sales
```
scope:      14D orders = 0
condition:  14D clicks >= clicks_min (20)
rescue:     14D spend < spend_floor (GBP 2.50) -> DO NOT PAUSE (cheap organic-ranking clicks)
```
The rescue exists deliberately: cheap traffic is kept alive for its organic-ranking value.

### Gate 4 — Custom rules
User-defined rules (`metric operator value`, AND-ed) evaluated after the two base rules.
Metrics offered: 30D/7D ACOS, 30D/14D orders, 14D clicks, 14D/30D spend, listing price, units in
stock. Operators: `> >= < <= = !=`.
In the xlsx these are **a planning worksheet only** — not wired to the Pause Log formulas.

### Priority (applies to paused rows only)
```
Stock rule AND units = 0        -> High
30D spend >= 40                 -> High
30D spend >= 15                 -> Medium
otherwise                       -> Low
```
Priority ranks the review queue by money at risk, so staff work the expensive pauses first.

---

## 3. Thresholds — configuration, never code

All five come from the `Pause Rules` sheet and must remain editable inputs:

| Setting | Value | Effect |
|---|---|---|
| Stock floor (units) | 5 | Pause below this |
| Rule 1 — 30D ACOS ceiling (%) | 40 | Pause at or above this |
| Rule 1 — 7D ACOS rescue (%) | 20 | Skip the pause below this |
| Rule 2 — 14D clicks minimum | 20 | Rule 2 only applies at or above this |
| Rule 2 — 14D spend floor (£) | 2.50 | Skip the pause below this |
| *(HTML only)* priority High / Medium | 40 / 15 | 30D spend bands |

---

## 4. Data model — live sources

Warehouse `order_management_copy`, read-only. Account = `ss_name='led_sone'`, `source=2`,
`marketplace='UK'`.

**Build source = the raw `ledsone` DB** (`mcp.ledsone.co.uk/mcp`), NOT the warehouse. It is fresher
(hourly sync), it carries listing price, and it is the only one exposing SMART campaigns at listing
grain. Scope key: `campaigns.marketplace_id='EBAY_GB'` + `sub_source=1` + `deleted=false`.

| Field the engine needs | Live source (verified 2026-07-21) |
|---|---|
| Listing (item_id) | `ebay_campaigns.performance_data.ebay_listing_id` |
| Campaign id / name | `ebay_campaigns.campaigns.campaign_id` / `.campaign_name` |
| Campaign state | `campaigns.campaign_status` (`RUNNING`/`PAUSED`/`ENDED`) — **never `campaigns.state`, which is an undecoded numeric code** |
| Type Manual / Smart | `campaigns.campaign_target_type` (`MANUAL`/`SMART`; NULL for CPS) |
| Advanced vs Standard | `campaigns.campaign_type` (`ON_SITE` / `COST_PER_SALE` / `OFF_SITE`) |
| Spend (per window) | `SUM(performance_data.ad_fees_payout_currency)` |
| Sales revenue (per window) | `SUM(performance_data.sale_amount_payout_currency)` |
| Orders (per window) | `SUM(performance_data.attributed_sales)` |
| Clicks (per window) | `SUM(performance_data.clicks)` |
| ACOS | `ad_fees / sale_amount * 100` per window (derived, never stored) |
| Listing price | `listings.ebay_listings.price` (+ `currency`), `all_list=1` |
| Units in stock | `ebay_listings.sku` (`all_list=1`, `wrong_sku=0`) → `inventory.products.id` → `inventory.local_inventory_current_stock_location_wise` (`warehouse_location='UK'`) |

Stock values are produced by `GetInvStock` logic — combo `min()` across components, pack-size
division, CL cable-pack exception — see `business/rules/stock-calculation-logic.md` in the AIOS
knowledge base. Standing exclusions: `warehouse_location != 'Canada'`; exclude warehouses
`Netherlands1` and `Duisburg warehouse` on any warehouse-level join.

**`all_list = 1` is mandatory** on every listing-table query (`business/rules/ebay-listing-sku-filter.md`)
— without it, parent variation containers with no real SKU inflate and corrupt every SKU-level result.

Window anchor = `MAX(date)` of the loaded PPC data, not `CURRENT_DATE` — otherwise a late ETL run
produces a short, ragged final day.

---

## 5. Known structural limits (audited 2026-07-21)

These are properties of the data, not bugs. Full detail in
`evidence/logs_or_screenshots/REQ-15_.../2026-07-21_step2_data_availability_audit.md`.

| # | Limit | Consequence |
|---|---|---|
| ~~A~~ | ~~SMART campaigns emit no listing-level rows~~ | **WITHDRAWN 2026-07-21** — true of the *warehouse* only. The raw `ledsone` DB has **179 SMART listings / £751.09 per 30D** at listing grain. Building on the warehouse would have silently dropped them. |
| **B** | CPS campaigns record **£0.00 spend and £0.00 sales** in `performance_data` — every money column there is a `cpc_*` (cost-per-click) field | Rule 1 is uncomputable for CPS (zero denominator); Rule 2 is permanently rescued by its own `spend < £2.50` clause, so it can never fire. **CPS out of scope** until its money is sourced from `campaign_report_data` / `accounting.ebay_order_expenses`. |
| **C** | **89.2%** of listings map to >1 SKU (max **245**) — 9,323 item×SKU pairs from 730 listings — **even after the mandatory `all_list=1` filter** | "Units in stock" per listing needs a defined rule (SUM / MIN / any-variant-zero). **Biggest open decision.** |
| **C2** | 17.8% (158/888) of advertised listings are absent from `ebay_listings`, which mirrors active listings only while ad history covers ended ones | No stock **and** no price for those. Must render **NO DATA**, never 0 — a 0 would auto-pause a possibly well-stocked listing. |
| **D** | No trustworthy listing-level ad state. `ads.state` is an **undecoded** numeric code (no eBay lookup table exists); `ebay_listings.status` is **99.4% NULL** and self-contradictory (137 items `status='Active'` with `is_ended=1`) | The mockup's separate "Listing ON/OFF" line cannot be reproduced. Use `is_ended` for *ended*, campaign state for on/off. **Never use `status`.** ✅ Listing **price** *is* available (`ebay_listings.price`). |
| **E** | Stock tables hold live stock only, no history | Windowed spend is always paired with today's stock; the report must say so. |
| **F** | PPC history starts 2026-04-22 | 30D windows fine; no long-run trend. |

---

## 6. Output

A read-only **recommendation** report, per the mockup's own shape:

- **Dashboard counters** — listings in scope, paused, by priority, by rule, still running, already
  off, 30D spend at risk vs 30D spend total.
- **Pause Log table** — Campaign/Listing · Item ID · Stock · State · Rule · Priority · plain-English
  Reason · Status (`PAUSED` / `RUNNING` / `ALREADY OFF`) · staff **Decision**
  (Pending/Approved/Rejected/On hold) · Note.
- Filters by rule, priority and state; free-text search; per-row decision trace showing every gate
  that was evaluated and why it passed or failed.

**The system recommends; it does not act.** Executing a pause is a write to live eBay PPC, which the
workbench's *Never Touch Without Written Approval* rule covers twice over ("live automation",
"financial or PPC business logic"). No such approval exists. A human applies approved pauses in
Seller Hub.

---

## 7. Baseline numbers — ⚠ PROVISIONAL, WAREHOUSE-DERIVED, DO NOT ACT ON

> These came from the **warehouse**, before the raw-DB verification. They are known to be
> incomplete: they exclude SMART listings entirely (£751.09/30D of real spend the warehouse could
> not see), and their stock figure used an unapproved `SUM`-across-variants assumption. **Re-derive
> from the raw `ledsone` DB once decision C is closed.**

(live dry run, 2026-07-21, ON_SITE running, 30D to 2026-07-20)

| Decision | Listings | 30D spend at stake |
|---|---|---|
| Keep running | 678 | £1,658.64 |
| PAUSE — Rule 2 | 8 | £57.25 |
| PAUSE — Rule 1 | 3 | £48.49 |
| NO STOCK DATA | 33 | £30.82 |
| PAUSE — Stock | 10 | £11.38 |

21 pause candidates. Grain is item × campaign (732 rows from 610 distinct listings — a listing can
run in several campaigns; whether the report de-duplicates to one row per listing is an open
decision).
