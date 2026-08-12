# PROJECT_HOME — eBay UK Top 50 Sales Drop (esdt)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-023_ebay-top50-sales-drop` |
| **Project code** | `esdt` *(provisional)* |
| **Task ID** | `REQ-26_ebay-top50-sales-drop` *(provisional — source has no requirement number; REQ-25 = `slow-moving-products`)* |
| **Status** | 🟡 **SETUP / SCAFFOLD ONLY (2026-08-12).** Folder structure + source import + governance docs done; task understood and data foundation mapped from prior eBay projects. **No SQL run, no deliverable, nothing committed.** Awaiting discovery answers from Kobiga + a GPT-approved implementation prompt. |
| **Opened** | 2026-08-12 |
| **Owner** | Abiraj · **Tech** Sajeesan · **Queryability** Tamil Selvan |
| **Business Validator** | **Kobiga** (requester / PH — same PH as eBay Product Net Sales #019). Account **ELECTRICALSONE**, market **eBay UK**. Publish audience TBC (likely `ebay_priors`). |

> ⚠ IDs provisional (source is a spec mock-up + workflow PDF, no requirement number). A new day/session does
> NOT mint a new Task ID. Confirm `PRJ-2026-023` / `REQ-26` / `esdt` with Abiraj (cosmetic).

## Business question
Which **50 eBay UK products lost the most sales** this period versus the previous equal period, **how much**
did each lose, and **what should the team investigate or fix**? The report must be actionable — pairing the
loss with traffic, conversion, PPC and stock diagnostics and a Priority + Action, not just a sales delta.

## Source of truth (two documents, imported verbatim)
1. `kobiga task (2).xlsx` — 1-sheet **layout spec** (Task ID/Name/Objective/Scope/Action + a 14-column
   final-output mock with **sample** rows). Defines columns + Action vocabulary only.
2. `eBay UK Top 50 Sales Drop Automation Workflow.pdf` — the full method: data list, period comparison
   maths, filter/rank logic, alert thresholds, diagnosis matrix, output shape and schedule.

## Scope (from the two sources — CONFIRM with Kobiga in discovery)
- **Channel / account:** eBay **UK**, account **ELECTRICALSONE** (PDF title + Excel row 3). Confirm whether
  UK-only ELECTRICALSONE or all UK eBay accounts.
- **Universe:** SKUs with sales in the **previous** period (SKUs with no previous-period sales are excluded
  — PDF §4.3; you cannot compute a drop % against zero).
- **Filter:** keep only SKUs where **sales decreased** (exclude increases — §4.4).
- **Rank:** by **absolute £ sales loss, highest first** (primary). Tie-break by **Drop %** highest first
  (§5). Take the **Top 50**.
- **Currency:** eBay UK = **£**. (Carries the **DST currency trap** — `orders.total` is in the marketplace's
  own currency; UK is already GBP, but never blend with DE/other-marketplace rows.)

## The report (14 columns, exact from the source workbook §9)
`Rank · SKU · Item ID · Product · Previous Sales · Current Sales · Loss £ · Drop % · CTR · CVR · ROAS ·
Stock · Priority · Action`

## Period comparison (PDF §3)
Two equal-length, adjacent date ranges. Worked example in the PDF: Current **1–7 Aug 2026** vs Previous
**25–31 Jul 2026** (7 vs 7 days). Per SKU:
- **Sales Change £** = Current Sales − Previous Sales
- **Sales Drop %** = (Current − Previous) ÷ Previous × 100
*Confirm the canonical period length (7-day weekly? calendar month?) and the anchor date with Kobiga.*

## Alert / Priority levels (PDF §6 — PROVISIONAL, confirm with Kobiga)
| Priority | Sales Drop | Default action |
|---|---|---|
| 🔴 Critical | ≥ 50% | Immediate listing + PPC investigation |
| 🟠 High | 30–49.99% | Review title, images, pricing, stock, PPC, conversion |
| 🟡 Medium | 15–29.99% | Monitor and review performance |
| 🟢 Stable | < 15% | No immediate action |

## Automatic Reason / diagnosis matrix (PDF §8 — PROVISIONAL rule engine, confirm with Kobiga)
| Signal | Suspected reason |
|---|---|
| Sales ↓ + Impressions ↓ | Visibility / SEO issue |
| Impressions stable + CTR ↓ | Title / main-image issue |
| Clicks stable + Conversion ↓ | Price / listing / offer issue |
| PPC Spend ↓ + PPC Sales ↓ | Advertising visibility issue |
| Stock = 0 | Stock issue |
| Sales ↓ + competitor price lower | Pricing review required |

## Data foundation — where each field lives (mapped from prior eBay projects, NOT yet verified for this build)
This report is a **synthesis of four proven eBay builds**; reuse their data paths, do not fork new ones.

| Field group | Source (proven pattern) | Prior project |
|---|---|---|
| Sales £, Units, SKU, Item ID | RAW `mcp.ledsone` `order_management` (eBay = `sub_source.source_id = 2`); order value in marketplace currency | epns #019, eppr #016, dst #015 |
| Impressions, Clicks, CTR, CVR | **Warehouse** `public.traffic_data`, `which_channel = 2` (eBay); `click` = Views, CVR = conversion ÷ click | traffic-source ref, eppr #016 |
| PPC Sales, PPC Spend, ROAS, ACOS | RAW `mcp.ledsone` eBay PPC (CPC + CPS ad types); ⚠ **CPS logs £0 spend** | eppa #013, eppr #016 |
| Stock Quantity | `inventory` current-stock tables | smp #022, fmp #020 |
| SKU ↔ Item ID bridge | `transaction_id` SKU bridge; ⚠ **~89% eBay listings are multi-SKU** | era #012, eppa #013 |

> ✅ **VERIFIED LIVE 2026-08-12** against the raw DB (`Ledsone-db-mcp`). See the corrected map below and the
> full column table in `SYSTEM_REFERENCE.md` §3. All 14 columns are sourceable from **one** database.

## ✅ Data-coverage verdict (measured 2026-08-12 — last 60 days, ELECTRICALSONE eBay UK)
Every column is sourceable from the **single raw DB** `mcp.ledsone.co.uk/mcp`. The feared warehouse↔ledsone
two-DB join **does not exist** — eBay organic traffic and PPC are in the same DB as orders/listings/stock.

| Check | Result |
|---|---|
| Account / scope keys | eBay sales = `orders.sub_source_id=22` (electricalsone, source_id 2); **eBay UK = `market_place='23'`** (proven via `ebay_listings.site='UK'`); Germany='10' |
| Data recency (live?) | ✅ orders → 2026-08-11 · traffic → 2026-08-10 · PPC → 2026-08-12. **Not a frozen host.** |
| Sales → listing (Item ID) join | ✅ **100%** — 57,963/57,963 order lines matched `ebay_listings.item_id` |
| Grain reality | 700 SKUs across **321 Item IDs** → multi-SKU listings confirmed (ranking-grain decision is real) |
| Organic traffic (CTR/CVR) | ✅ **100%** of the 321 Item IDs have `ebay_traffic_data` rows (site `EBAY-GB`) |
| PPC (ROAS/spend) | ✅ **91%** (292/321 Item IDs); real £2,415.52 spend / £19,509.98 sales; join on `listing_performance.ebay_listing_id::text = item_id` |
| Stock | ✅ **99.1%** (694/700 SKUs) resolve in `inventory` with a stock row |

**Corrections to earlier assumptions (now verified):** (1) eBay **UK = market_place '23'**, not a source_id
change; sales sit under `sub_source_id 22`. (2) Organic traffic = `business_reports.ebay_traffic_data`
(same DB), **not** a separate warehouse `public.traffic_data`. (3) PPC join key = the eBay **item number** in
`listing_performance.ebay_listing_id`, **not** `ebay_listings.id` (that returns 0 rows). Full detail in
`SYSTEM_REFERENCE.md` §3/§6.

> ⚠ Residual honest gaps (not blockers): ~9% of Item IDs are unadvertised → ROAS renders `n/a`; PPC has many
> £0-spend ON_SITE/CPS rows (eppa trap) — guard ÷0; parent/child listing rows share `item_id` → take the
> parent title.

## 🟠 Known traps carried in from prior projects
- **Currency trap (DST):** `orders.total` is in the marketplace's own currency; no FX table exists. UK rows
  are GBP — safe to sum within UK; never blend with other marketplaces.
- **CPS £0-spend trap (eppa):** eBay CPS campaigns log £0 spend → ROAS/ACOS can look infinite; handle
  explicitly.
- **Multi-SKU listing trap (era/eppa):** ~89% of eBay listings carry multiple SKUs; SKU↔Item ID is not 1:1.
  Decide the ranking grain (SKU vs Item ID) before building.
- **Watchers = NO DATA** (organic-traffic ref): not in either database. Not requested here, but do not invent.
- **Warehouse ↔ ledsone split:** sales/PPC/stock live in raw `ledsone`; organic traffic lives in the
  warehouse. This report must join across both — the single hardest part of the build.

## Deliverable (planned, not built)
- **REQ-26-D01** — Excel (`Notes & Method` + `Top 50 Sales Drop` table) + interactive HTML dashboard, from
  one read-only builder module `sql/REQ-26_ebay-top50-sales-drop/build_esdt_d01.py`.

## Reviewer gates (none passed)
Sajeesan (technical) · Tamil Selvan (queryability) · Kobiga (business).

## Decisions — CONFIRMED by Kobiga 2026-08-12 ✅
1. **Ranking grain → SKU** (one row per individual product code; not Item ID). *(700 SKUs → 321 Item IDs; a
   representative Item ID/title is still shown per SKU for reference.)*
2. **Period → monthly comparison: last 30 days vs previous 30 days.** Current = `[CURRENT_DATE−30, CURRENT_DATE)`,
   Previous = `[CURRENT_DATE−60, CURRENT_DATE−30)`. (Not the 7-day weekly example.)
3. **Scope → ELECTRICALSONE only, eBay UK** = `orders.sub_source_id=22` AND `market_place='23'`.
4. **Alert thresholds → PDF §6 as-is:** 🔴 ≥50 · 🟠 30–49.99 · 🟡 15–29.99 · 🟢 <15%.
5. **Reason/Action → PDF §8 diagnosis matrix as-is** (defaults accepted).
6. **Rank metric → PDF §4–5:** exclude no-prior-sales & increases; rank by absolute £ loss desc, tie-break Drop % desc; Top 50.

### Residual (technical, not owner-blocking)
- **CPS £0-spend / unadvertised** → ROAS renders `n/a` (guard ÷0). ~9% of Item IDs unadvertised.
- **Publish audience / automation** → deferred until after Kobiga sees the first report (PDF §10 suggests
  monthly recurring; candidate `ph_task` team `ebay_priors`).

## Next actions
1. Send the discovery decision sheet above to **Kobiga**.
2. On answers: request a **GPT-approved implementation prompt**, then build REQ-26-D01 from one read-only
   fetch, reconcile each field against a live anchor, and produce Excel + HTML.
3. Confirm provisional `PRJ-2026-023` / `REQ-26` / `esdt` identity with Abiraj (cosmetic).
