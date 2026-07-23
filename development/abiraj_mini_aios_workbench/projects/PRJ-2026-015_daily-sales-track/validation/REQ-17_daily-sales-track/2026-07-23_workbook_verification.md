# Verification record — REQ-17-D01 workbook (Daily Sales Track)

**Verified:** 2026-07-23 · **Artefact:** `evidence/final_outputs/REQ-17_daily-sales-track/REQ-17-D01_daily_sales_track.xlsx`
**Harness:** `verify_dst_d01.py` (re-runnable) · **Result: 12 / 12 PASS**

## Method

The harness **does not import the builder**. It holds its own reference figures obtained from a
**separate re-derivation query** against live `ledsone` — a single-scan `FILTER` aggregation over all
accounts, rather than the builder's per-date `GROUP BY` — plus a third whole-channel aggregate with
no `GROUP BY` at all for the KPI totals.

Formulas are **recalculated through LibreOffice** before reading, so every derived cell is verified as
an **evaluated value**, not merely as a formula string. This matters: three of the twelve checks
(V6–V9) would be vacuous against unevaluated formulas.

## Results

| # | Check | Result |
|---|---|---|
| V1 | 21 headers exact and in order | ✅ |
| V2 | Row count = 13 accounts | ✅ |
| V3 | All 13 reference accounts present | ✅ |
| V4 | **78 measured cells** match the independent re-derivation (13 accounts × sales/orders × 3 periods) | ✅ 0 mismatches |
| V5 | Listings match, and **AH + PH = Active on every row** | ✅ 13/13 |
| V6 | `Sales Diff` evaluates correctly | ✅ |
| V7 | `Sales Growth %` evaluates correctly, **blank when prior = 0** | ✅ |
| V8 | `Avg Order Value` evaluates correctly, **blank when 0 orders** | ✅ |
| V9 | `Account Sales Trend` evaluates to the expected band | ✅ 13/13 |
| V10 | Engine Inputs rows align 1:1 with the report | ✅ |
| V11 | KPI panel reconciles to the whole-channel aggregate | ✅ |
| V12 | Zero formula errors anywhere in the workbook | ✅ |

## Reconciliation anchors

| Figure | Builder | Independent re-derivation |
|---|---|---|
| Total Sales Today (R−1, 2026-07-22) | £2,983.35 | **£2,983.35** ✅ |
| Total Sales Yesterday (R−2, 2026-07-21) | £2,891.03 | **£2,891.03** ✅ |
| Total Orders / Yesterday Orders | 142 / 158 | **142 / 158** ✅ |
| Total Units Sold | 223 | — |
| Average Order Value | £21.01 | £2,983.35 ÷ 142 = **£21.01** ✅ |
| Active listings across 13 accounts | 14,607 | 2,750 PH + 11,857 AH = **14,607** ✅ |

## Defects found and fixed

**Two, both caught by the harness rather than by inspection.**

| # | Defect | Effect | Fix |
|---|---|---|---|
| **1** | 🔴 **A Config note beginning `=>` was parsed as a formula**, producing a live `#VALUE!` error in the shipped workbook (`Config!A9`). | A reviewer opening the Config sheet — the sheet they are meant to edit — would have seen a broken cell and reasonably doubted the whole engine. | Reworded to `CONSEQUENCE: …`. Caught by **V12**. |
| **2** | 🟠 **`Engine Inputs` header sat on row 2 and was overwritten by the first account.** The trend formulas reference that sheet **positionally**, so row 2 must be the first account. | The sheet shipped with no visible header, and the positional contract was undocumented — a later editor sorting or inserting a row would have silently mis-paired every AH/PH trend against the wrong account. | Header moved to row 1; an explicit red warning added at `E1`. Caught by **V10** after the fix was designed. |

## Known limitations, disclosed

- **Formula evaluation is LibreOffice's**, not Excel's. The formulas used (`IF`, `AND`, `SUM`,
  `COUNTA`, arithmetic) are core and portable, but the numbers a reviewer sees in Excel are
  recalculated by Excel.
- **AH + PH sales do not sum to `Today's Sales`.** `Today's Sales` is the order grand total
  (`orders.total`, includes postage and discount); AH/PH sales are line-level
  `qty × item_price` attributed per listing. The residual is postage/discount, not an error. Stated
  on the **Data Notes** sheet. Not a defect — a definitional consequence of the source columns, and
  it should be confirmed as acceptable by the Business Validator.
- **The dataset is embedded** in `build_dst_d01.py` rather than pulled at runtime, because the MCP is
  the only credentialled path in this session. Every statement used is recorded verbatim in
  `SQL_USED`, so a scheduled run (REQ-17-D02) executes the same SQL over psycopg2 and feeds the same
  `render_workbook()`. **Re-running the builder today reproduces this file byte-for-byte; it does not
  re-query.**
- **Trend band is provisional** at ±5% (decision **E** open). It is editable on the Config sheet and
  every trend column re-evaluates from it.

## Dashboard verification (REQ-17-D01, HTML) — added 2026-07-23

`REQ-17-D01_dst_dashboard.html` is rendered by `render_dst_dashboard.py` **from the same
`dst_d01_data.json` the workbook is built from**, so the two cannot drift. (REQ-16 shipped a defect
where the workbook and dashboard came from separate fetches; this is the structural fix.)

### Structural checks

| Check | Result |
|---|---|
| Rows rendered | ✅ 13 |
| Cells per row (uniform) | ✅ 20 / 20 on every row |
| Header cells | ✅ 20 |
| Unfilled template placeholders | ✅ none |
| Figures present and matching the workbook | ✅ `£2,983.35` · `142` · `223` · `£21.01` · `14,607` |
| KPI: Same Day Last Year | ✅ £3,929.06 — re-derived by hand from the 13 LY values |
| KPI: Accounts Trading | ✅ 9 / 13 (accounts with ≥1 order on R−1) |
| Every row pre-rendered as static HTML | ✅ readable with JavaScript disabled |

### Layout, measured live in a browser at 1680 × 1000

| Metric | Before tightening | After |
|---|---|---|
| Table width vs pane | 1914 px in 1611 px → **horizontal scroll** | **1619 px in 1619 px → fits, no scroll** |
| Table height vs pane | 723 px in 583 px | 671 px in 668 px (**3 px**) |
| Page-level scrollbar | none | none |
| Row height | 54 px | 46 px |

At a true full-screen viewport (~1030 px) the table fits vertically with room to spare. The header,
column headers and totals row are all sticky, so the view stays readable while scrolling regardless.

### Interaction checks (executed in-browser, not assumed)

| Control | Result |
|---|---|
| Filter → Down | ✅ 13 → **7** rows |
| Filter → All | ✅ back to **13** |
| Search "sharm" | ✅ **1** row (matches the AH holder column, not just account name) |
| Sort by Today £ ascending | ✅ Retro LED (£0.00) moves to the top |
| Export CSV / Compact / Full screen | ✅ wired and present |

### Deliberate presentation differences from the workbook

Not data differences — the dashboard shows **the same 22 data columns in 20 display columns**:

- **`Date`** is in the masthead rather than repeated identically on all 13 rows.
- **`AH Listing` and `PH Listing`** are merged into one **PH / AH split** cell showing both counts
  plus a proportion bar.

Nothing is omitted, and the totals row reconciles to the workbook.

## What this does NOT verify

- That the **business definitions** are the right ones — those are decisions A, B, C, D, F, G, H, I,
  M, closed by Thinesh on 2026-07-23 and recorded in `PROJECT_HOME.md`.
- **Business plausibility.** No figure has yet been checked against eBay Seller Hub by a human. That
  remains the outstanding acceptance step — REQ-13 was corrected five times precisely because early
  passes skipped it.

---

# ADDENDUM 2026-07-23 - grain change, currency defect, two sticky-layout defects

The record above describes the **first** build (13 rows, one per account, 22 columns). It was
superseded the same day. Kept for history; this addendum is authoritative.

## Final shape

**30 rows, one per account x marketplace. 24 columns. Money per currency, never blended.
18/18 verification checks. Published to `ph_task` 422-425 (`ebay_priors`), v4.**

## Defect 1 - grain (found by an external check, not by the harness)

A Seller Hub screenshot showed **LEDSone UK = GBP 837.93** for 22 Jul; the account row read
**GBP 1,144.51**. Both were correct - the account row combined UK (GBP 837.93) and Germany
(EUR 306.58). Seller Hub reports per marketplace, so the report was rebuilt at account x
marketplace. Totals were unchanged by the split (2,983.35 / 142 orders / 223 units), which proves
nothing was lost or duplicated. **V14 now fails the build if LEDSone UK / UK ever stops equalling
GBP 837.93.**

## Defect 2 - currency (the serious one)

`order_management.orders.total` is stored in the **marketplace's own currency**, not GBP. Confirmed
by joining `order_management.order_info.currency`, which matches `amount_paid` exactly:

| Currency | 22 Jul | 21 Jul | Same day LY | Orders 22 Jul |
|---|---|---|---|---|
| GBP | 1,899.40 | 2,002.72 | 2,529.00 | 97 |
| EUR | 1,083.95 | 858.69 | 1,400.06 | 45 |
| USD | 0.00 | 29.62 | 0.00 | 0 |

The first build rendered **every** figure with a pound sign and summed them. **20 of 30 rows were
mislabelled**, and every cross-currency total was meaningless - `Total Sales Today GBP 2,983.35` was
GBP 1,899.40 + EUR 1,083.95 added together.

**The blend also inverted the story.** Split properly, **GBP fell 5.16%** while **EUR rose 26.23%**;
the blended headline read **"+3.19% up"**, hiding a decline in the largest market. That is the real
damage - not a cosmetic symbol.

**Fix:** per-row symbol from `listings.market_place_id_mapping`; totals reported one row per
currency; nothing converted, because `ledsone` holds **no exchange-rate table** (searched
`exchange` / `fx` / `currency` / `conversion_rate` - zero objects).

**Three new gates prevent recurrence:** V15 (row currency matches the marketplace mapping),
V16 (money cells carry their own symbol), **V17 (fails if any blended cross-currency total appears
on the KPI sheet)**. Two publish-time gates also refuse to ship if the EUR total is missing or the
old blended figure reappears.

## Defects 3 and 4 - sticky layout, both found by measuring in a real browser

| # | Defect | Effect |
|---|---|---|
| 3 | **Both header rows pinned at `top:0`** | Scrolling made the column-name row rise and **cover the group headers** - undoing the column grouping precisely when a reader needs it |
| 4 | **All three currency footer rows pinned at `bottom:0`** | They stacked on each other; only the last (all-zero **USD**) row stayed visible while scrolling |

Same root cause both times: multiple sticky rows sharing one offset. Fixed by staggering
(`--grp-h`, `--foot-h`), with offsets set to **measured** heights - the first attempt at each was
2-4px out and left a visible overlap.

## Layout in the ph_task portal

The portal embeds the page in a **~700px** container; the viewport-locked layout compressed the
table to ~6 rows. A `@media (max-height:820px)` rule now reclaims the chrome automatically
(11 rows, 14 maximised).

> **An alternative was tried and rejected:** letting the page grow instead of compress rendered all
> 30 rows, but **broke `position:sticky` entirely** (headers scrolled off at -352px). For a
> 24-column financial table, losing the headers is worse than a shorter table.

## Still not verified

- **Active Listing is understated ~5-6%** - eBay shows 3,033 active on LEDSone UK's UK site against
  2,843 here; 6,883 vs 6,510 account-wide. Cause: the listings mirror leaves stale `is_ended` flags
  on auto-renewing listings. A sync defect **outside this report**; disclosed on both artefacts.
- **Trend band +/-5% is provisional** (decision E).
- **No reviewer sign-off** - Sajeesan, Tamil Selvan, Thinesh all pending.
