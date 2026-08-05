# PROJECT_HOME — Channel Opportunity (chop)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-021_channel-opportunity` |
| **Project code** | `chop` *(provisional)* |
| **Task ID** | `REQ-24_channel-opportunity` *(provisional — REQ-23 = `fmp`)* |
| **Status** | 🟢 **BUILT & DELIVERED 2026-08-05 — pending Mahima sign-off.** Germany, UNITS, rolling 90 days (data through 2026-08-04), **RAW `mcp.ledsone` `order_management`** (clean-SKU = strip `-IDE`); knowledge from AIOS-KB `text-to-sql-multi`. Excel `REQ-24-D01_channel_opportunity.xlsx` (Notes & Method + Channel Opportunity, **283 opportunity rows**: 270 Missing channel · 10 Marketplace winner · 3 Shopify winner). Reconciled vs raw DB on 5 SKUs incl. zero/absent channels (raw = source of record; agrees with warehouse mirror within ±2 units). Opportunity/Action on documented DEFAULT rules awaiting Mahima. **PUBLISHED 2026-08-05 to `ph_task` id 699 (Mahi / german_priors), md5 read-back MATCH.** Committed + pushed to `main`. See `evidence/logs_or_screenshots/REQ-24_.../2026-08-05_build_and_data_availability.md`. |
| **Opened** | 2026-08-05 |
| **Owner** | Abiraj · **Tech** Sajeesan · **Queryability** Tamil Selvan |
| **Business Validator** | **Mahima** (requester / PH). Publish audience TBC (which `ph_task` team — the fmp sibling published to `german_priors`). |

> ⚠ IDs provisional (source is a spec mock-up with no requirement number). Do not mint a new Task ID on a
> new day/session. Confirm `PRJ-2026-021` / `REQ-24` / `chop` with Abiraj (cosmetic).

## Business question
Which products **sell well in one marketplace but are weak or missing in others**? Lay each product's
sales side by side across **Shopify · Amazon · eBay**, classify the **Opportunity**, and recommend the
**Action** that closes the gap — so listings can be created / promoted where demand exists but coverage
doesn't.

## Scope (from the source workbook — CONFIRM with Mahima in discovery)
- **Market:** the sibling fmp report is DE-only; confirm whether chop is DE-only or all marketplaces.
- **Window:** not stated in the source — confirm (rolling 30/90-day, or a fixed month, + anchor).
- **Sales metric:** the source column is just "Sales" (integers) → most likely **units sold**. Confirm
  units vs revenue. Prefer units (avoids the currency trap); use revenue only if Mahima asks.

## The table (exact columns from the source)
*"Channel Opportunity Table — find products selling well in one marketplace but missing in others."*

`SKU · Shopify Sales · Amazon Sales · eBay Sales · Opportunity · Action`

Sample rows (illustrative only):
| SKU | Shopify | Amazon | eBay | Opportunity | Action |
|---|---|---|---|---|---|
| xyz | 100 | 5 | 2 | Shopify winner | Improve Amazon/eBay listing |
| dgh | 10 | 120 | 50 | Marketplace winner | Add Shopify promotion |
| kytd | 0 | 80 | 0 | Missing channel | Create eBay listing |

## Derived fields (rules implied by the source — define with Mahima)
- **Opportunity** — classification of the per-SKU sales spread:
  - *Shopify winner* — strong on Shopify, weak on the marketplaces.
  - *Marketplace winner* — strong on Amazon/eBay, weak/absent on Shopify.
  - *Missing channel* — sells in ≥1 channel, **zero** in another (a listing gap).
  The numeric thresholds (what counts as "strong" / "weak" / "missing") are a **business rule** — do not
  invent them.
- **Action** — a rule engine keyed off the Opportunity class (Improve Amazon/eBay listing / Add Shopify
  promotion / Create eBay listing / …). Vocabulary to confirm with Mahima.

## 🔒 Source (to confirm in discovery — follow the house rules)
- **Sales per channel** — Amazon (`which_channel=1`), eBay (`which_channel=2`), Shopify (`which_channel=3`);
  eBay source of record = **raw `ledsone`**. Aggregate units (or revenue) per **base SKU** per channel over
  the window, then pivot the three channels onto one row.
- **"Missing" / "no listing"** (optional, to strengthen the Missing-channel class) — `listing_data`
  (`all_list=1`) to prove a SKU has no live listing in a channel, not merely no sales.
- **AIOS knowledge base** (`docs.ledsone.co.uk/mcp`) — **read before writing any SQL.** Multi-domain
  (Orders × 3 channels, optionally Listings) → `text-to-sql-multi`.

## 🟠 Known traps carried in from prior projects
- **Base-SKU roll-up key:** the same product has different Product IDs per channel — pivot on the **clean
  base SKU**, confirmed clean (the FMP combined-table rule).
- **eBay SKU sprawl:** never join eBay sales by SKU alone (~13× overstatement); attribute by
  order_id / item_id, isolate with `source_id=2`.
- **Currency trap (DST):** if the metric is revenue, `orders.total` is in the marketplace's own currency
  and there is no FX table — do not blend. Prefer units.
- **Amazon parent/child + title on the parent row** (`all_list=0`) — the EPPR gotcha.
- **"Missing" must be proven by absence** (LEFT JOIN), never assumed.

## Deliverables (planned)
- Excel: `evidence/final_outputs/REQ-24_.../REQ-24-D01_channel_opportunity.xlsx` (Notes + cross-channel table).
- Optional HTML dashboard (house pattern), filterable by Opportunity class.
- Builder: single read-only module `sql/REQ-24_.../chop_build_d01.py`.

## Reviewer gates (none passed yet)
Sajeesan (technical) · Tamil Selvan (queryability) · Mahima (business).

## Next actions
1. **Discovery decision sheet to Mahima:** market scope, window, sales metric (units vs revenue), the
   numeric winner/weak/missing thresholds, the Opportunity classes, the Action vocabulary, and publish audience.
2. Confirm the provisional `PRJ-2026-021` / `REQ-24` / `chop` identity with Abiraj (cosmetic).
3. Read the AIOS knowledge base, then map every column live against `ledsone` / warehouse into
   `SYSTEM_REFERENCE.md` with a coverage %.
4. Build the single generator module; reconcile a real cross-channel SKU before locking the classifier.
5. Decide publish audience (`ph_task`) — no publish, no git commit of outputs until signed off.
