# SYSTEM_REFERENCE — Daily Sales Track (DST)

Complete functional detail of what this system is specified to do, for a leader or a new engineer.

> ✅ **BUILT AND PUBLISHED 2026-07-23.** 30 account × marketplace rows, 24 columns, money per
> currency, 18/18 verification checks, live on `ph_task` 422-425.
>
> *(The note below described the pre-build state and is kept for history.)*
> ⚠ **SPECIFICATION STAGE.** Unlike the REQ-13/REQ-14/REQ-16 system references, this describes a
> system that **has not been built**. It is derived from the canonical source (`Thinesh task (4).xlsx`,
> row 1 and the sample's verified arithmetic) and from **definitions inherited from REQ-13**. Every
> statement below is marked **CONFIRMED**, **INHERITED**, **INFERRED** or **UNDEFINED**. No live query
> has been run for this requirement.

| | |
|---|---|
| Project | `PRJ-2026-015_daily-sales-track` · code `dst` |
| Task | `REQ-17_daily-sales-track` |
| Deliverables | **D01** the report = dashboard + workbook + governed JSON (not started) · **D02** scheduled daily refresh (not started) |

---


## 🔴 Money is per currency — never blended

`order_management.orders.total` is stored in the **marketplace's own currency**, not GBP —
confirmed by joining `order_management.order_info.currency`, which matches `amount_paid` exactly.
Site → currency comes from `listings.market_place_id_mapping`: UK = GBP; Germany, France, Ireland,
Austria, Italy, Spain, Netherlands = EUR; US = USD; Canada = CAD.

**There is no exchange-rate table anywhere in `ledsone`**, so nothing is converted. Every row shows
its own symbol and totals are reported **one row per currency**.

⚠ The first build rendered every figure with a pound sign and summed them. 20 of 30 rows were
mislabelled and the headline read **"+3.19% up"** when GBP had actually fallen **5.16%** and EUR
risen **26.23%** — the blend hid a decline in the biggest market. Three verification gates now exist
specifically to stop that returning (V15 row currency, V16 own symbol, V17 no blended total).

## Grain: one row per account × marketplace

**30 rows.** Changed from one-row-per-account on 2026-07-23 after a Seller Hub check: LEDSone UK
showed **£837.93** for 22 Jul while the account row read £1,144.51. Both were right — the account
row combined UK (£837.93) and Germany (€306.58). Seller Hub reports per marketplace, so this report
does too, and **every row ties to one Seller Hub screen**. That anchor is now a permanent
verification check.

## 1. Purpose

For each trading account, on each day, state the day's sales, orders and units; compare them against
the previous day and against the same day one year earlier; name the day's best-selling product;
count the account's active listings; and classify the account as trending up, stable or down.

The system **reports only**. It has no action column, no recommendation, and no write path to any
marketplace.

**What makes it different from everything already built:** nothing in the business currently retains
a daily series. Today the question "when did this account start declining?" cannot be answered from
any existing record — the check is done by eye in Seller Hub and the result is discarded. This
system's output is intended to accumulate (⚠ decision **I**).

---

## 2. Output shape — 22 columns

**CONFIRMED** from row 1 of the source. Order and header text are canonical.

| # | Column | Meaning | Basis |
|---|---|---|---|
| 1 | Account | The trading account | **INHERITED** — REQ-13's confirmed name map |
| 2 | Date | The day being reported | **UNDEFINED** — decision B |
| 3 | Today's Sales (£) | Sales on the anchor day | **INHERITED** |
| 4 | Yesterday Sales (£) | Sales on D−1 | **INHERITED** |
| 5 | Sales Diff (£) | col 3 − col 4 | **CONFIRMED** — re-derived 6/6 |
| 6 | Sales Growth % | col 5 ÷ col 4 | **CONFIRMED** — re-derived 6/6 |
| 7 | Same Day LY Sales (£) | Sales on the last-year anchor | **UNDEFINED** — decision C |
| 8 | Today's Orders | Orders on the anchor day | **INHERITED** |
| 9 | Yesterday Orders | Orders on D−1 | **INHERITED** |
| 10 | Order Growth % | (col 8 − col 9) ÷ col 9 | **CONFIRMED** — re-derived 6/6 |
| 11 | Same Day LY Orders | Orders on the last-year anchor | **UNDEFINED** — decision C |
| 12 | Units Sold | Units on the anchor day | **INHERITED** · period ambiguous — decision H |
| 13 | Avg Order Value (£) | col 3 ÷ col 8 | **CONFIRMED** — re-derived 6/6 |
| 14 | Best Seller | The day's best-selling product | **UNDEFINED** ranking — decision D |
| 15 | Active Listing | Count of live listings | 🔴 **CONFLICT** — decision K |
| 16 | AH Listing | — | 🔴 **UNDEFINED** — decision A |
| 17 | AH Listing Sales | — | 🔴 **UNDEFINED** — decision A |
| 18 | AH Sales Trend | — | 🔴 **UNDEFINED** — decision A |
| 19 | PH Listing | — | 🔴 **UNDEFINED** — decision A |
| 20 | PH Listing Sales | — | 🔴 **UNDEFINED** — decision A |
| 21 | PH Sales Trend | — | 🔴 **UNDEFINED** — decision A |
| 22 | Account Sales Trend | Up / Stable / Down from col 6 | **INFERRED** bands — decision E |

## 3. Output shape — the 9-KPI panel

**CONFIRMED** from rows 13–22, and every one independently re-derived from the sample rows.

| KPI | Formula | Verified |
|---|---|---|
| Total Accounts | count of rows | ✅ |
| Total Sales Today | Σ col 3 | ✅ £22,493.05 exact |
| Total Sales Yesterday | Σ col 4 | ✅ £21,971.65 exact |
| Overall Growth | (today − yesterday) ÷ yesterday | ✅ 2.3730% → 2.37% |
| Total Orders | Σ col 8 | ✅ 629 exact |
| Yesterday Orders | Σ col 9 | ✅ 613 exact |
| Order Growth | (today − yesterday) ÷ yesterday | ✅ 2.6101% → 2.61% |
| Total Units Sold | Σ col 12 | ✅ 1,543 exact |
| Average Order Value | Total Sales Today ÷ Total Orders | ✅ 35.7600 → £35.76 |

⚠ Note the KPI panel computes **AOV of the whole portfolio** (Σ sales ÷ Σ orders), **not** the mean
of the per-account AOVs. Those differ whenever accounts have different order sizes. The sample
confirms the portfolio method.

---

## 4. Measurement definitions — INHERITED FROM REQ-13, NOT RE-DERIVED

This is the single most important engineering fact about this build. **REQ-13's revenue definition
was corrected five times against the owner's own live-DB checks before it settled.** Re-deriving it
here would produce a daily number that disagrees with the published monthly one.

| Measure | Definition | Trap it avoids |
|---|---|---|
| **Sales** | `SUM(order_transaction.order_total)` | **Not** `SUM(item_price × quantity)` (product-only, excludes real postage). **Not** product + `shipping_template_price` (template postage over-states). `order_total` is eBay's settled paid value and is stored at line level. |
| **Orders** | `COUNT(DISTINCT order_id)` | `COUNT(*)` returns the order **line** count — 1,619 vs 1,517 for led_sone in June, ~7% higher. |
| **Units** | `SUM(quantity)` | — |
| **AOV** | Sales ÷ Orders | — |
| **Filter** | `source_name='EBAY'` AND `order_status='Completed'` | Refunded and Cancelled excluded. |

⚠ **Deliberate divergence from REQ-16.** ESNM *included* Refunded and Inprogress because it was
measuring **demand** for a dead-stock assessment. This report measures **trading revenue**, so
REQ-13's stricter `Completed`-only filter is the correct inheritance. **This divergence must be
stated on the deliverable** — otherwise a reader comparing the two reports will find sales figures
that do not tie and assume one is wrong.

**Account name map (Thinesh-confirmed in REQ-13):** LEDSONE UK = `led_sone` · SUNSONE UK =
`so_926407` · Electricalsone UK = `electricalsone` · LEDSONE DE = `ledsonede`. The other eight
accounts are shown by store name.

---

## 5. The anchor — the highest-risk design decision

**UNDEFINED — decision B.**

The source column is literally `Today's Sales`. Taken at face value, a scheduled morning run
measures a **partial day** and every account reports a catastrophic decline, every single day.

This is not hypothetical. It has occurred twice in this workbench:

- **REQ-15 (EPPA)** anchored on `MAX(date)` = today and read **8 clicks / £1.39** against a normal
  ~540-click, ~£99 day. Found and fixed the same day; the fix was
  `CASE WHEN MAX(date) < CURRENT_DATE THEN MAX(date) ELSE MAX(date) - 1 END`.
- **REQ-16 (ESNM)** hit the same defect; logged as decision H, closed by anchoring the scheduled job
  on the last day of the previous month and ad-hoc runs on the last **complete** day.

**Recommended: anchor on the last complete day.** "Today's Sales" then means the most recent full
trading day, and "Yesterday" the day before it. If the requester genuinely wants live intraday
figures, the column must be re-labelled and the partial-day meaning stated on the face of the report.

---

## 6. The last-year comparator

**UNDEFINED — decision C.**

`Same Day LY` can mean either:

| Option | For anchor 2026-07-23 (a **Thursday**) | Consequence |
|---|---|---|
| Same calendar date | 2025-07-23 — a **Wednesday** | Compares a Thursday against a Wednesday |
| Same weekday, `D − 364` | 2025-07-24 — a **Thursday** | Weekday-aligned |

For daily retail sales, **weekday dominates** — a Saturday and a Tuesday are different businesses.
A calendar-date comparison silently reports the weekday difference as a year-on-year trend.

---

## 7. Trend classification

**INFERRED — decision E.** The source states no thresholds anywhere. The sample brackets them:

| Sample row | Sales Growth % | Trend shown |
|---|---|---|
| R5 | +13.84% | 📈 Up |
| R2 | +8.73% | 📈 Up |
| **R4** | **+6.91%** | **📈 Up** |
| **R7** | **+3.89%** | **➡ Stable** |
| R6 | −8.20% | 📉 Down |
| R3 | −12.72% | 📉 Down |

The cut therefore lies **between 3.89% and 6.91%**, making **±5%** the obvious candidate. This is an
inference from six rows and must be exposed as **editable configuration**, echoed on the deliverable,
and confirmed — never inlined into the query.

⚠ The sample gives no negative value between 0% and −8.20%, so the **lower** band is unbracketed.
Symmetry is assumed, not evidenced.

---

## 8. The AH / PH block — 6 columns, undefined

**🔴 UNDEFINED — decision A. This is the project blocker.**

The source provides no definition, no example value and no source for columns 16–21. In the sample:

- Columns **16, 17, 19, 20** are **blank on all six rows**.
- Columns **18 and 21** *are* populated — and carry **exactly the same value as column 22
  (`Account Sales Trend`) on all six rows**.

The trend values were therefore **copied across** and reveal nothing about how an AH or PH trend
would be computed.

**Working interpretation, unconfirmed:** **AH = Account Holder**, **PH = Product Holder** — the
staff-ownership concepts already used throughout this workbench (`ph_task`, `ph_segment`,
`ph_priors`). A product-holder assignment demonstrably exists: **REQ-10 (FRRC) routed returns to 19
named PH holders**, one `ph_task` row each. Its **eBay listing-level equivalent has not been
located**.

**27% of the requested report cannot be built until this is answered, and no amount of database work
will answer it** — it is a business definition only the requester holds. The Step-2 audit should
nonetheless sweep both databases for a candidate assignment object, **by column name as well as table
name** (searching only table names is the mistake that made REQ-11's first audit wrong).

---

## 9. Data sources — expected, TO BE VERIFIED

Two databases, on the pattern REQ-16 established.

| Need | Database | Status |
|---|---|---|
| Sales, orders, units, per account per day | warehouse `order_management_copy` → `public.order_transaction` | Expected primary — **daily grain UNTESTED** |
| Active listings (REQ-13 definition) | warehouse → `public.listing_data` | **CONFLICT** with the below |
| Active listings (REQ-16 definition) | `ledsone` → `listings.ebay_listings` | **CONFLICT** with the above |
| **Best Seller product titles** | **`ledsone` → `listings.ebay_listings.title`** | ⚠ **Mandatory** — REQ-16 measured the warehouse title as populated on only **8.3%** of in-scope eBay items (890 of 10,739). A warehouse-only build ships ~92% of Best Seller cells blank. |
| Seller-account resolution | `ledsone` → `order_management.sub_source` (`source_id = 2` = eBay) | Expected |
| **AH / PH assignment** | **UNLOCATED** | 🔴 decision A |

---

## 10. What the Step-2 audit must establish

Not yet run. It must answer, read-only:

1. **Does `order_transaction` support a daily grain at all?** Is `order_date` a date or a timestamp,
   and **what timezone does its day boundary fall on?** Every prior project used monthly or rolling
   windows, so this has never needed establishing.
2. **Is the daily series complete?** REQ-16 found the eBay traffic feed had lost **11 of 91 days**. A
   daily report is far more sensitive than a 90-day rolling one — a single lost day reads as a total
   trading halt, not a 1% understatement.
3. **How far back is the last-year comparator populated**, per account? An account live for under a
   year has no LY figure and must render **blank, never zero**.
4. **Does an AH/PH assignment object exist in either database?** Sweep by **column** name as well as
   table name.
5. **Which `Active Listing` definition to adopt**, and what the gap between the two is today.
6. **One hand-reconciled account-day** against a figure the requester can verify independently.

---

## 11. Deliverables (planned)

| Deliverable | Description | Status |
|---|---|---|
| **REQ-17-D01** | The report — three artefacts from one dataset: governed JSON, static-rendered HTML dashboard (22 columns + the 9 KPIs as cards that recompute on the filtered view), and a multi-sheet xlsx (Daily Sales Track · KPI Summary · Config · Data Notes) | ⬜ **NOT STARTED** |
| REQ-17-D02 | Autonomous scheduled refresh — fail-closed, the fleet's 7th job and its first daily one | ⬜ **NOT STARTED** — blocked on decisions I and J |

**Build rule inherited from REQ-16:** one generator module produces all three artefacts. REQ-16 had
a defect where the workbook and the dashboard were built from separate fetches and drifted; a single
module makes that impossible.

**Publish rule:** if D01 is published to `tech_team_outputs.ph_task`, the HTML must be
**pre-rendered static** (the viewer runs no JavaScript), the write must be SELECT-then-UPDATE
(**there is no UNIQUE constraint on `task_id`**, despite the sample DDL claiming one), and
**`assigned_user_team` must be set** (absent from the sample DDL; without it the row never reaches
the audience).

---

## 12. Data traps recorded

- **The source has no business logic** — its formulas are constants typed with a leading `=+`.
- **`order_total` ≠ `item_price × quantity`**; `shipping_template_price` over-states postage.
- **`COUNT(*)` counts order lines, not orders** — ~7% high.
- **"Today" is a partial day.** Anchor on the last complete day.
- **Same-calendar-date last year is a different weekday.**
- **Product titles are only 8.3% populated in the warehouse** — take them from `ledsone`.
- **`Active Listing` has two disagreeing live definitions** in this workbench.
- **A store sells cross-border** — account alone mis-attributes marketplace sales (REQ-13's correction).
- **Missing data renders blank, never zero.** A `0` in a sales or growth column is indistinguishable
  from a real trading collapse — and detecting collapses is this report's entire purpose.
