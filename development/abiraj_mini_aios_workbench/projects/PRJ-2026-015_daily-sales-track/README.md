# PRJ-2026-015 — Daily Sales Track (DST)

**For each trading account and marketplace, what happened yesterday — and is it better or worse than
the day before and the same day last year?**

| | |
|---|---|
| Status | ✅ **CLOSED 2026-07-23** — REQ-17-D01 DELIVERED · VERIFIED (18/18) · PUBLISHED (ph_task 422-425, `ebay_priors`, **v9**, md5 `642a5a27`) · REQ-17-D02 **AUTOMATED** (daily 09:05) · **all four sign-offs received** |
| Code | `dst` · Task `REQ-17_daily-sales-track` |
| Scope | eBay, **all accounts**, every marketplace with live listings — **30 account × marketplace rows** |
| Output | Read-only daily tracker — **24 columns**, money **per currency**, + 9 KPI cards. Changes nothing on any marketplace. |
| Opened / closed | 2026-07-23 — same day |

## The 24 columns

| # | Column | # | Column |
|---|---|---|---|
| 1 | Account | 13 | Same Day LY Orders |
| 2 | **Market** | 14 | Units Sold |
| 3 | **Currency** | 15 | Avg Order Value |
| 4 | Date | 16 | Active Listing |
| 5 | Today's Sales | 17 | AH Listing |
| 6 | Yesterday Sales | 18 | AH Listing Sales |
| 7 | Sales Diff | 19 | AH Sales Trend |
| 8 | Sales Growth % | 20 | PH Listing |
| 9 | Same Day LY Sales | 21 | PH Listing Sales |
| 10 | Today's Orders | 22 | PH Sales Trend |
| 11 | Yesterday Orders | 23 | Account Sales Trend |
| 12 | Order Growth % | 24 | **AH Holder** |

Plus a **9-KPI summary panel**: Total Accounts · Total Sales Today · Total Sales Yesterday ·
Overall Growth · Total Orders · Yesterday Orders · Order Growth · Total Units Sold · Average Order
Value. Every KPI card is clickable and re-sorts the table on that column.

**Column history:** the source specified 22. `Best Seller` was **removed** on Thinesh's instruction
(→ 21); `AH Holder` was **added** on his request (→ 22); `Market` and `Currency` were added by the
grain and currency corrections (→ **24**).

## ⚠ Read this before touching the build

**1. 🔴 `orders.total` is in the MARKETPLACE'S OWN currency, not GBP.** `order_management.orders` has
no currency column at all — the code lives in `order_management.order_info.currency`, and the
site→currency map is authoritative in `listings.market_place_id_mapping`. The first build rendered
every figure with a `£` and summed them; **20 of 30 rows were mislabelled and the blended headline
read "+3.19% up" while GBP had fallen 5.16% and EUR risen 26.23%.** **There is no exchange-rate table
anywhere in `ledsone`** — money is reported per currency and **never converted, never summed across
currencies.**

**2. The source contains no business logic at all.** Every cell that looks like a formula is a
constant typed with a leading `=+` (cell `E2` holds the literal `=+435.3`, not `=C2-D2`). There is
no rule table — the equivalent of REQ-16's canonical rows 20–32 **does not exist in this file**.
Every definition was **inherited** or **decided**; none could be read out of the spreadsheet.

**3. Sales count orders PLACED, not completed** — `status <> 'Cancelled'` only. This **deliberately
diverges from REQ-13 (EBPD)**, which counts `Completed` for a *monthly* view. Orders reach
`Completed` about **two days** after purchase; at R−1 only **25.4%** had matured, so a
`Completed`-only filter understates the reported day by **69%** and reads as a crash. The right
status filter depends on the reporting **period**, not on house style.

**4. Everything else is inherited from REQ-13 — do not re-derive it.** EBPD's revenue definition was
corrected **five times** against the owner's own live-DB checks before it settled.

| Measure | Definition |
|---|---|
| Sales | `SUM(orders.total)` — the order grand total, in the marketplace's currency |
| Orders | `COUNT(DISTINCT orders.id)` — `COUNT(*)` returns order **lines**, ~7% higher |
| Units | `SUM(CAST(order_item_info.item_quantity AS INT))` |
| AOV | Sales ÷ Orders, within one currency |
| Filter | eBay via `sub_source.source_id = 2`; `status <> 'Cancelled'` |

**5. "Today" is a partial day.** A run on date **R** reports **R−1** as "Today" and **R−2** as
"Yesterday". Taken literally, a morning run would report a collapse on every account every day —
a defect already found twice in this workbench (REQ-15 fixed, REQ-16 decision H).

**6. Pin the anchor dates as SQL literals — never `CURRENT_DATE`.** The warehouse runs
`Asia/Colombo` and rolls over **4.5 hours before** London. The day *buckets* are safe (`order_date`
is stored in UK time in both databases, verified by hour-of-day distribution); only the anchor
arithmetic was at risk.

**7. `Active Listing` is understated ~5–6%** — eBay shows 3,033 active on LEDSone UK's UK site
against 2,843 here. Cause: the listings mirror leaves **stale `is_ended` flags on auto-renewing
(GTC) listings**. Disclosed on both artefacts; the fix belongs to the listings sync. **Do not quote
listing counts against Seller Hub.**

**8. AH + PH = Active, on every row.** AH is the **PH remainder** — a live listing with no
portfolio-holder assignment belongs to the account holder. This is also a control total, and it is
gated in both the harness and the daily runner.

## The anchor that proves the report

**LEDSone UK / UK = £837.93 for 22 July 2026** — Thinesh's own eBay Seller Hub screen. It is a
permanent verification gate (V14); **the build fails if it stops matching.** That check is also what
exposed the original grain error: the account row read £1,144.51 because it combined UK (£837.93)
with Germany (€306.58).

> A verification harness proves a report is *self-consistent*. It cannot prove it is *right*. Both
> serious defects here were found by comparing against an external source — the requester's own screen.

## Sample-data ruling

The 6-row sample is **fabricated** — 2 distinct account names against a stated `Total Accounts = 6`,
placeholder listing counts (`1212 / 12 / 2222 / 22 / 111`), generic product names. It can never be a
reconciliation baseline.

✅ **But its arithmetic is sound and was independently re-derived: 32 of 32 relationships reconcile
exactly** (9 KPIs + 24 per-row derived fields). So the **formula layer of the spec is confirmed** and
needed no decision. Only the inputs to those formulas were open. See the SOURCE_MANIFEST.

## Where things are

| | |
|---|---|
| Governance, decisions | [PROJECT_HOME.md](PROJECT_HOME.md) |
| **Full functional detail** | [SYSTEM_REFERENCE.md](SYSTEM_REFERENCE.md) |
| Execution rules | [CLAUDE.md](CLAUDE.md) |
| Task index | [TASK_REGISTER.md](TASK_REGISTER.md) |
| Source (COPY, SHA-256 verified byte-identical) | `evidence/source_documents/REQ-17_daily-sales-track/` |
| Data audit | `evidence/logs_or_screenshots/REQ-17_.../2026-07-23_data_availability_audit.md` |
| Generator | `sql/REQ-17_.../` — `dst_d01_rows.py` · `build_dst_d01.py` · `render_dst_dashboard.py` |
| Deliverables | `evidence/final_outputs/REQ-17_.../` — dashboard `.html` · workbook `.xlsx` · governed `.json` |
| Verification | `validation/REQ-17_.../` — `verify_dst_d01.py` (18/18) + records |
| Automation | `automation/` — see [AUTOMATION_README.md](automation/AUTOMATION_README.md) |
| Daily requirement document | `DigitWeb_Works_Abiraj/23_07_2026/2026-07-23_abiraj_REQ-dst_REQ-17-D01.md` |
| Closure record | `closure/REQ-17_daily-sales-track/2026-07-23_closure.md` |

## Who

Requester / end user / Business Validator: **Thinesh** (`public."user"` id 63, Active).
Coordinator Varmen · Technical Sajeesan · Queryability Tamil Selvan. **All four signed off 2026-07-23.**

Audience `ebay_priors` = Thinesh · **Jarsini** · kobiga · powsteena.
⚠ **Name trap:** the requester supplied "Jarshini", which matches nobody. `staff.users` holds
**`Jarsini` (id 91)** *and* **`Jasmini` (id 84)** — two different Active people. He confirmed
**Jarsini**. Also `powsteena`, not "Powesteena".

## Decisions — 13 of 15 closed by Thinesh on 2026-07-23

| Decision | Answer |
|---|---|
| **M** status filter | Count orders **placed** (exclude `Cancelled` only) |
| **B** anchor | Run on **R** reports **R−1** as "Today", **R−2** as "Yesterday" |
| **A** AH/PH | **AH = the PH remainder** — unassigned listings; AH + PH = Active |
| **C** last year | **Same calendar date** (weekday therefore differs) |
| **D** Best Seller | **Removed** |
| **F** grain | **Account × marketplace** — reversed from account-only after the Seller Hub check |
| **G** scope | **All eBay accounts** |
| **H** units | **Yesterday only** |
| **I** track vs snapshot | **Snapshot — replaces each morning**, no history kept |
| **K** active listings | **`all_list = 1`** (settled by the AIOS knowledge base) |
| **N** publish target | Source lock is **data retrieval only** — `ph_task` publishing unaffected |
| **P** AH names | Displayed as the **AH Holder** column; informational, changes no figure |
| **J** recipients | `ebay_priors`, published 09:05 daily |

**Still open — neither blocks anything:**

- **E — trend bands.** Ships as editable config, default ±5% (matching the source sample), flagged
  for confirmation. Measured: a *normal* day swings **15–60%** by account, so at ±5% only **6.5%** of
  account-days read "Stable". Recommendation: compare against the **same weekday last week** rather
  than yesterday.
- **O — `ph_dashboard` duplicate check.** Needs the `ph_pgsql` role to read.

## Next action

**After 09:05 tomorrow (2026-07-24), run `automation\check_status.bat`** and look for a fresh line
beginning `STATUS OK`. A *manually triggered* run is proven; an *unattended scheduled fire* is not,
and that is precisely the distinction the `0xC000013A` trap exploits — it hit `UDESC` on 2026-07-22.
