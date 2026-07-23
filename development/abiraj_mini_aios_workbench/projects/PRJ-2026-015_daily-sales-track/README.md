# PRJ-2026-015 — Daily Sales Track (DST)

**For each trading account, what happened yesterday — and is it better or worse than the day before
and the same day last year?**

| | |
|---|---|
| Status | **ONBOARDING — specification received, nothing built.** No live query has been run for this requirement. |
| Code | `dst` · Task `REQ-17_daily-sales-track` |
| Scope | ⚠ **UNDECIDED** — channel, accounts and marketplaces are all open (decisions **F**, **G**) |
| Output | Read-only daily tracker — 22 columns per account per day + a 9-KPI panel. Changes nothing on any marketplace. |
| Opened | 2026-07-23 |

⚠ **IDs pending owner confirmation** — the source file carries no requirement number. `REQ-17`
continues the sequence REQ-12 (`epc`) → REQ-13 (`ebpd`) → REQ-14 (`ERA`) → REQ-15 (`eppa`) →
REQ-16 (`esnm`).

⚠ **The project name is deliberately channel-neutral.** The source never names a channel. eBay is
the working assumption (all five of this requester's prior requirements are eBay, and the sample's
account names resolve to eBay stores in REQ-13's confirmed map) — but it is an inference, and a
project ID cannot be renamed later, so the name does not claim one.

## The 22 columns

| # | Column | # | Column |
|---|---|---|---|
| 1 | Account | 12 | Units Sold |
| 2 | Date | 13 | Avg Order Value (£) |
| 3 | Today's Sales (£) | 14 | Best Seller |
| 4 | Yesterday Sales (£) | 15 | Active Listing |
| 5 | Sales Diff (£) | 16 | **AH Listing** 🔴 |
| 6 | Sales Growth % | 17 | **AH Listing Sales** 🔴 |
| 7 | Same Day LY Sales (£) | 18 | **AH Sales Trend** 🔴 |
| 8 | Today's Orders | 19 | **PH Listing** 🔴 |
| 9 | Yesterday Orders | 20 | **PH Listing Sales** 🔴 |
| 10 | Order Growth % | 21 | **PH Sales Trend** 🔴 |
| 11 | Same Day LY Orders | 22 | Account Sales Trend |

Plus a **9-KPI summary panel**: Total Accounts · Total Sales Today · Total Sales Yesterday ·
Overall Growth · Total Orders · Yesterday Orders · Order Growth · Total Units Sold · Average Order
Value.

🔴 = **no definition and no located source.** See decision **A**.

## ⚠ Read this before touching the build

**1. The source contains no business logic at all.** Every cell that looks like a formula is a
constant typed with a leading `=+` (cell `E2` holds the literal `=+435.3`, not `=C2-D2`). There is
no rule table — the equivalent of REQ-16's canonical rows 20–32 **does not exist in this file**.
Every definition must be **inherited** or **decided**; none can be read out of the spreadsheet.

**2. Do not re-derive the sales definitions — inherit them from REQ-13.** EBPD's revenue definition
was corrected **five times** against the owner's own live-DB checks before it settled. Deriving them
again here produces a daily number that disagrees with the published monthly one.

| Measure | Definition (from REQ-13) |
|---|---|
| Sales | `SUM(order_total)` — settled paid value, **not** `item_price × quantity`, **not** plus template postage |
| Orders | `COUNT(DISTINCT order_id)` — `COUNT(*)` returns order **lines**, ~7% higher |
| Units | `SUM(quantity)` |
| AOV | Sales ÷ Orders |
| Filter | `source_name='EBAY'`, `order_status='Completed'` |

**3. "Today" is a partial day.** Taken literally, a morning run reports a collapse on every account
every day. This defect has already been found twice in this workbench — REQ-15 (fixed) and REQ-16
(decision H). Anchor on the **last complete day**.

**4. The daily grain itself is untested here.** Every existing project uses a monthly or rolling
multi-day window. Whether `order_transaction.order_date` is a date or a timestamp, and **what
timezone its day boundary falls on**, has never needed to be established. It does now.

## Sample-data ruling

The 6-row sample is **fabricated** — 2 distinct account names against a stated `Total Accounts = 6`,
placeholder listing counts (`1212 / 12 / 2222 / 22 / 111`), generic product names.

✅ **But its arithmetic is sound and was independently re-derived: 32 of 32 relationships reconcile
exactly** (9 KPIs + 24 per-row derived fields). So the **formula layer of the spec is confirmed** and
needs no decision. Only the inputs to those formulas are open. See the SOURCE_MANIFEST.

## Where things are

| | |
|---|---|
| Governance, open decisions | [PROJECT_HOME.md](PROJECT_HOME.md) |
| **Full functional detail** | [SYSTEM_REFERENCE.md](SYSTEM_REFERENCE.md) |
| Execution rules | [CLAUDE.md](CLAUDE.md) |
| Task index | [TASK_REGISTER.md](TASK_REGISTER.md) |
| Source (COPY, SHA-256 verified) | `evidence/source_documents/REQ-17_daily-sales-track/` |
| Data audit | `evidence/logs_or_screenshots/REQ-17_daily-sales-track/` — ⬜ **not yet run** |
| Generator | `sql/REQ-17_daily-sales-track/` — ⬜ empty |
| Deliverables | `evidence/final_outputs/REQ-17_daily-sales-track/` — ⬜ empty |
| Verification harness | `validation/REQ-17_daily-sales-track/` — ⬜ empty |
| Daily requirement document | `DigitWeb_Works_Abiraj/23_07_2026/2026-07-23_abiraj_REQ-dst_REQ-17-D01.md` |

## Who

Requester / end user / Business Validator: **Thinesh** (`public."user"` id 63, Active, verified
2026-07-22 for REQ-16). Coordinator Varmen · Technical Sajeesan · Queryability Tamil Selvan.

## Status 2026-07-23 — DECISIONS CLOSED, READY TO BUILD

**13 of 15 decisions closed by Thinesh on 2026-07-23.** Every one of the **21 columns** (was 22 —
`Best Seller` removed) now has a confirmed source and definition.

| Decision | Answer |
|---|---|
| **M** status filter | Count orders **placed** (exclude `Cancelled` only) — yesterday = £2,983.35 / 142 orders |
| **B** anchor | Run on **R** reports **R−1** as "Today", **R−2** as "Yesterday" |
| **A** AH/PH | **AH = the PH remainder** — unassigned listings. 14,607 = 2,750 PH + 11,857 AH |
| **C** last year | **Same calendar date** |
| **D** Best Seller | **Removed** → 21 columns |
| **F** grain | **One row per account** |
| **G** scope | **All eBay accounts** — 13 with live listings |
| **H** units | **Yesterday only** |
| **I** track vs snapshot | **Snapshot — replaces each morning**, no history kept |
| **K** active listings | **`all_list = 1`** (settled by the AIOS knowledge base) |
| **N** publish target | Source lock is **data retrieval only** — `ph_task` publishing unaffected |
| **P** AH names | **Informational only** — no AH-name column exists, so names change no figure |

**Still open — neither blocks the build:**

- **E — trend bands.** Thinesh asked this back. Measured: a *normal* day swings **15–60%** by account
  size, so at ±10% about **85% of rows would read Up or Down daily**. Recommendation: compare against
  the **same weekday last week** rather than yesterday. Ships as editable config, default ±5%
  (matching the source sample), flagged for confirmation.
- **J — recipients and delivery time.** Blocks publishing only.
- **O — `ph_dashboard` duplicate check.** Needs the `ph_pgsql` role to read.

## Superseded — the pre-decision open list

Full table in [PROJECT_HOME.md](PROJECT_HOME.md); evidence in
`evidence/logs_or_screenshots/REQ-17_.../2026-07-23_data_availability_audit.md`.

1. 🔴 **M — the status filter. NEW, and now the biggest one.** Orders reach `Completed` ~2 days after
   they are placed: at **R−1 only 26.2%** have matured (£1,102.43 of a true £3,010.04), vs 99.3% at
   R−2. REQ-13's inherited `Completed`-only filter **cannot be used with the confirmed R−1 anchor** —
   every report would show a **63% collapse that did not happen.**
2. 🟠 **A — AH only.** The **PH half is closed** (sourced from ledsone `staff.ph_categories`, 28%
   coverage). **AH has no source in either database.** Down from 6 blocked columns to 3.
3. 🔴 **C — Same Day LY: same calendar date, or same weekday?** 2026-07-23 is a Thursday;
   2025-07-23 is a **Wednesday**.
4. 🔴 **D — Best Seller ranked by units or revenue?** (Source confirmed — ledsone `ebay_listings.title`.)
5. 🔴 **E — confirm the ±5% trend bands** (inferred from six sample rows, never stated).
6. 🔴 **F — row grain: account, or account × marketplace?**
7. **K — `Active Listing`:** warehouse (REQ-13) or ledsone (REQ-16) definition?

✅ **B is CLOSED** — confirmed by the owner 2026-07-23: a run on date **R** reports **R−1** as
"Today", **R−2** as "Yesterday", and LY relative to R−1.

✅ **Feasibility is GREEN** — the daily grain works (`order_date` carries real clock times, no gaps
in the observed series), and both databases store `order_date` in **UK time**, so the daily buckets
agree. Only `CURRENT_DATE` differs (warehouse is `Asia/Colombo`, ledsone `Europe/London`) — pin the
anchor explicitly.

## Next action

Route decisions to Thinesh with the audit attached — **M first** (it sets every money figure), then
A (AH), C, D, E, F.
