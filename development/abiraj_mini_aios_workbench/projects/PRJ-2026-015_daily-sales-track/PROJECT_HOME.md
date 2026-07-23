# PROJECT_HOME — Daily Sales Track (DST)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-015_daily-sales-track` |
| **Project code** | `dst` |
| **Task ID** | `REQ-17_daily-sales-track` |
| **Status** | **REQ-17-D01 DELIVERED · VERIFIED · PUBLISHED 2026-07-23** — 30 account × marketplace rows, 24 columns, money per currency. 18/18 verification checks. Live on `ph_task` 422-425 (`ebay_priors`, v4). **Not automated (D02 not started); reviewer sign-off pending.** |
| **Opened** | 2026-07-23 |
| **Owner** | Abiraj |
| **Coordinator** | Varmen |
| **Technical Reviewer** | Sajeesan |
| **Queryability Reviewer** | Tamil Selvan |
| **Business Validator** | **Thinesh** (requester) — identity verified live for REQ-16 in `public."user"` (id **63**, `user_name` `Thinesh`, status **Active**, single exact match). ⚠ The user table in `order_management_copy` is `public."user"`, **not** `staff.users` — the `staff` schema is empty in that database. **Publish audience NOT decided** (decision **J**); candidate `ebay_priors`. |

> ⚠ **ID approval pending.** The source file carries **no requirement number**. `REQ-17` continues the
> sequence REQ-12 (`epc`) → REQ-13 (`ebpd`) → REQ-14 (`ERA`) → REQ-15 (`eppa`) → REQ-16 (`esnm`), and
> `PRJ-2026-015` follows `PRJ-2026-014`. Both need owner confirmation (decision **L**).

> ⚠ **The project name is deliberately channel-neutral** — `daily-sales-track`, not
> `ebay-daily-sales-track`. The source never names a channel. A project ID must not be renamed later,
> so it does not claim one now. See decision **G**.


## Grain: one row per account × marketplace

**30 rows.** Changed from one-row-per-account on 2026-07-23 after a Seller Hub check: LEDSone UK
showed **£837.93** for 22 Jul while the account row read £1,144.51. Both were right — the account
row combined UK (£837.93) and Germany (€306.58). Seller Hub reports per marketplace, so this report
does too, and **every row ties to one Seller Hub screen**. That anchor is now a permanent
verification check.

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

## Business question

> For each trading account, on each day: what were the sales, orders and units — how do they compare
> with the previous day and with the same day one year earlier — what was the day's best seller, how
> many listings are active, and is the account trending up, down or flat?

## Scope

**Confirmed:**
- The output shape — **22 columns, one row per account per day**, plus a **9-KPI summary panel**.
- The **formula layer** — verified against the source sample, 32 of 32 relationships exact.
- The **measurement definitions** — inherited verbatim from REQ-13 (EBPD), not re-derived.

**⚠ NOT confirmed — every one of these is an open decision:**
- **Channel** (decision G). Working assumption eBay; the source never says so.
- **Accounts** (decision G). The sample names 2 while its own KPI panel states 6.
- **Marketplaces** (decision G). The source has **no Marketplace column at all**.
- **Row grain** (decision F) — account, or account × marketplace.
- **Anchor day** (decision B) — last complete day, or live intraday.
- **Last-year comparator** (decision C) — same calendar date, or same weekday.

**Out of scope / blocked:**
- **Any write to a marketplace.** This is a read-only reporting requirement; it recommends nothing
  and changes nothing. There is no action column and no write-back path.
- **Changing REQ-13's sales definitions.** They are inherited. A change to them is a REQ-13 matter
  and must be routed there, not decided inside this project.
- **Amazon and Shopify** — unless decision G opens the channel scope, in which case the inherited
  definitions (which are eBay-filtered) no longer transfer and must be re-established.

## 🔒 Source lock (owner instruction, 2026-07-23)

**Only these two MCPs may be used. They carry the live data.**

| MCP | URL | Role |
|---|---|---|
| `Ledsone-aios-mcp` | `https://docs.ledsone.co.uk/mcp` | **AIOS knowledge base** — read BEFORE writing SQL |
| `Ledsone-db-mcp` | `https://mcp.ledsone.co.uk/mcp` | **Raw `ledsone` Postgres** — the only data source |

🔴 **The warehouse `order_management_copy` is OUT OF SCOPE.** It is a mirror and it diverges —
measured on identical days: 21 Jul £2,884.11/152 orders (warehouse) vs **£2,891.03/157** (ledsone);
19 Jul £3,783.17 vs **£3,770.73**. It also connects as `postgres` (full write) rather than a
read-only role.

⚠ Two consequences, both recorded as decisions: REQ-13's warehouse-based definitions can no longer be
inherited (the ledsone equivalents are in `CLAUDE.md` §2 — and are *cleaner*, being at order grain
rather than line grain), and the **publish target is unreachable** (decision **N**).

## Spec source

Single source, imported COPY-only with SHA-256 verified byte-identical against the original —
`evidence/source_documents/REQ-17_daily-sales-track/SOURCE_MANIFEST.md`.

**Row 1 (the header) is canonical** for column shape and order. **The sample's arithmetic
relationships are canonical** for the formula layer (32/32 verified). **The sample's values are
fabricated** and can never be a reconciliation baseline.

## Current position

**Specification received, read cell-by-cell, and analysed. No build has started and no live query
has been run for this requirement.**

What the intake established:

| Finding | Status |
|---|---|
| The 22-column shape and the 9-KPI panel | ✅ Confirmed from row 1 and rows 13–22 |
| The formula layer (Diff, Growth %, AOV, all 9 KPIs) | ✅ **Independently re-derived — 32/32 exact** |
| Sales / Orders / Units / AOV definitions | ✅ **Inherited from REQ-13** — not re-derived |
| Best Seller product title source | ⚠ Located (ledsone `ebay_listings.title`) — ranking basis undefined |
| Active Listing | 🔴 **Two competing live definitions** — REQ-13's and REQ-16's disagree |
| AH / PH — 6 columns | 🔴 **No definition, no located source** |
| Anchor day | 🔴 Partial-day hazard, unresolved |
| Daily grain feasibility | ⬜ **UNTESTED** — no prior project in this workbench uses a daily grain |

## Known gaps — measured at intake, not assumed

| # | Gap | Effect |
|---|---|---|
| 🔴 1 | **The source contains no computational logic.** Every apparent formula is a constant typed with a leading `=+` (`E2` = the literal `=+435.3`, not `=C2-D2`). There is no rule table; the equivalent of REQ-16's canonical rows 20–32 does not exist. | **100% of the report's logic must be inherited or decided.** Nothing can be read out of the file. Inferring it from six sample rows would have produced a plausible, fully-populated, silently-wrong report. |
| 🔴 2 | **Six columns (16–21, the AH/PH block) have no definition and no located source.** In the sample, cols 16, 17, 19 and 20 are **blank on every row**, while cols 18 and 21 *are* populated — carrying **exactly the same value as col 22 (`Account Sales Trend`) on all six rows**. The trend values were copied across and reveal nothing. | **27% of the requested report is unbuildable.** No database work can resolve it — it is a business definition only the requester holds. See decision **A**. |
| 🔴 3 | **`Active Listing` already has two disagreeing definitions live in this workbench.** REQ-13 counts `COUNT(DISTINCT ref_id)` from warehouse `listing_data` (12,799 per-site, June). REQ-16 counts `is_ended=0 AND is_child=0` from ledsone `ebay_listings` (11,156, UK+DE). | One must be chosen and the difference from the other report expected and explained. See decision **K**. |
| 🔴 4 | **"Today's Sales" is a partial day.** A morning run reports a collapse on every account, every day. Found and fixed in REQ-15 (EPPA read 8 clicks / £1.39 against a normal ~540-click, ~£99 day); logged as open decision H in REQ-16. | The build must anchor on the **last complete day** unless the requester explicitly requires live intraday figures and accepts what they mean. See decision **B**. |
| 🔴 5 | **`Same Day LY` misaligns weekdays.** The anchor 2026-07-23 is a **Thursday**; the same calendar date in 2025 is a **Wednesday**. `D − 364` gives 2025-07-24, a Thursday. | For daily retail sales, weekday dominates. A calendar-date comparison compares a Thursday against a Wednesday and reports the difference as a trend. See decision **C**. |
| ⬜ 6 | **The daily grain is untested in this workbench.** Every existing project uses a monthly window or a rolling multi-day window. Whether `order_transaction.order_date` is a date or a timestamp, and what timezone its day boundary falls on, has never needed establishing. | Must be established by the Step-2 audit **before any figure is published**. |
| ⬜ 7 | **Daily-series completeness is unverified.** REQ-16 found the eBay *traffic* feed had silently lost **11 of 91 days**. Order data may be cleaner — but a **daily** report is far more sensitive than a 90-day rolling one: a single lost day reads as a total trading halt, not a 1% understatement. | The Step-2 audit must hunt for gaps in the daily series explicitly. Absent data must render **blank, never zero**. |

## Duplicate-risk assessment — **AMBER** (provisional, pre-audit)

**13 of the 22 columns are the daily equivalent of metrics `PRJ-2026-011` (EBPD, REQ-13) already
delivers monthly** — revenue, orders, units, AOV and active listings, per account × marketplace.

**Resolved as EXTEND, not CREATE.** Under the Existing-Asset-First rule (reuse → extend → merge →
create) this project **inherits REQ-13's definitions verbatim**. If it derives sales its own way, the
business holds a daily number and a monthly number that do not reconcile — the duplicate-truth
condition the workbench exists to prevent.

**Not a STOP**, because the business question is genuinely different: EBPD answers *"how did each
account perform last month?"*; this answers *"what happened yesterday, and is it better or worse
than the day before and the same day last year?"*. Different period, different cadence, different
decision. Nothing that exists today retains a daily series at all.

Purpose-adjacent projects remain canonical for **their** purpose: `PRJ-2026-011` (EBPD) monthly
account performance · `PRJ-2026-012` (ERA) returns · `PRJ-2026-013` (EPPA) PPC pause decisions ·
`PRJ-2026-014` (ESNM) slow/no-moving listings.

**The final verdict is to be confirmed after the Step-2 audit, not asserted from this document.**

## Open decisions — required before any build

| # | Decision | Who | Why it matters |
|---|---|---|---|
| ~~M~~ | ✅ **CLOSED 2026-07-23 — THINESH CHOSE (a): count all orders PLACED.** Sales/orders/units = every order placed on the day, **excluding `Cancelled` only**. Yesterday therefore reads **£2,983.35 / 142 orders**, not £928.58 / 36. ⚠ Two consequences to disclose on the deliverable: (1) figures **will not tie to EBPD's monthly numbers**, which count `Completed` only; (2) because refunds land later, a day's figure **restates downward over time** — settle this against decision **I** (freeze the published row, or restate it). | — | *(original wording below)* |
| ~~M-orig~~ | **the status filter.** Orders reach `Completed` ~2 days after they are placed: at **R−1 only 26.2%** have matured (37 of 141 orders; **£1,102.43** of a true **£3,010.04**), against **99.3%** at R−2. REQ-13's inherited `order_status='Completed'` filter therefore **cannot be used with the owner's confirmed R−1 anchor** — every report would show a **63% one-day collapse that did not happen**. Options: **(a)** count orders **placed**, excluding `Cancelled` only *(recommended — that is what "yesterday's sales" means to a trader)*; **(b)** keep `Completed` and move the headline day to R−2. | **Thinesh + Sajeesan** | **BLOCKER — sets every sales, orders, units and AOV figure in the report.** Option (a) diverges from REQ-13, so the daily report will not tie to EBPD's monthly figure on the most recent ~2 days. Measured in `evidence/logs_or_screenshots/REQ-17_.../2026-07-23_data_availability_audit.md` §4. |
| ~~A~~ | ✅ **CLOSED 2026-07-23 — THINESH DEFINED IT.** **AH = Account Holder, and the AH set is the PH remainder:** a listing with **no** PH category assignment belongs to the account's AH. So per account, `AH Listing + PH Listing = total live listings` — they partition, which is why the sheet carries both. **Measured live** (`all_list = 1`, `is_ended = 0`): 13 accounts · **14,607 listings = 2,750 PH + 11,857 AH**. Seven accounts (`coventrylights`, `vintageinterior`, `dctransformer`, `re6865`, `lighting_sone`, `homin_gmbh`, `bestbringer`) have **zero** PH assignments, so AH = 100% of their listings. **The AH *person* is a manual account→staff map supplied by Thinesh — it exists in no database and must ship as editable config.** ⚠ Three follow-ups open — see **P**. | — | Columns 16–21 are now **all buildable**. |
| ~~B~~ | ~~Anchor — last complete day, or live intraday?~~ | — | ✅ **CLOSED 2026-07-23 — CONFIRMED BY THE OWNER.** This is a **daily automated** report: a run on date **R** reports **R−1** as `Today's Sales`/`Today's Orders`, **R−2** as `Yesterday Sales`/`Yesterday Orders`, and the matching day one year before **R−1** as `Same Day LY`. `Date` (col 2) = **R−1**. A report generated in the morning cannot show that morning's own trading. ⚠ The anchor must be **pinned explicitly** — the warehouse runs on `Asia/Colombo (+05:30)`, so its `CURRENT_DATE` rolls over 4.5 hours before London's. ⚠ Because the headers still read "Today's"/"Yesterday", the reported date must be shown on the face of the report, or every reader will misread it. |
| ~~C~~ | ✅ **CLOSED 2026-07-23 — SAME CALENDAR DATE.** `Same Day LY` = the same date one year earlier (e.g. R−1 = 22 Jul 2026 → 22 Jul 2025). ⚠ Disclose that the weekday differs, so the comparison carries a day-of-week effect. Accounts younger than a year render **blank, never zero**. | — | |
| ~~D~~ | ✅ **CLOSED 2026-07-23 — `Best Seller` REMOVED** on Thinesh's instruction ("no need, remove that"). **The report is now 21 columns, not 22.** ⚠ Side effect: this was the only column requiring `listings.ebay_listings.title`. | — | |
| 🔴 **E** | **Confirm the trend bands.** The sample brackets them — `Up` at **+6.91%**, `Stable` at **+3.89%**, `Down` at **−8.20%** — so the cut lies between 3.89% and 6.91%, making **±5%** the candidate. Also: does the same band apply to all three trend columns? | Thinesh | An inference from six rows. Sets every trend value in the report. |
| ~~F~~ | ✅ **CLOSED 2026-07-23 — ONE ROW PER ACCOUNT.** No marketplace split. ⚠ Disclose that an account row therefore **combines its marketplaces** (`led_sone` sells to UK, DE, FR, US and IT buyers), so DST rows are **not comparable to EBPD's account × marketplace rows**. | — | |
| ~~G~~ | ✅ **CLOSED 2026-07-23 — ALL eBay ACCOUNTS.** Channel = eBay only. Universe measured live: **13 accounts with live listings** — `led_sone` 6,510 · `electricalsone` 2,700 · `so_926407` 1,515 · `ledsonede` 636 · `huettenlampen` 543 · `coventrylights` 537 · `vintageinterior` 474 · `dctransformer` 468 · `re6865` 403 · `neighbourmarket` 344 · `lighting_sone` 247 · `homin_gmbh` 165 · `bestbringer` 65. (9 further eBay `sub_source` rows exist with zero live listings.) All marketplaces included, per decision F. | — | |
| ~~P~~ | ✅ **CLOSED 2026-07-23 — the AH name map is INFORMATIONAL ONLY and blocks nothing.** **The report has no AH-name column.** The six AH/PH columns are counts, sales and trends — none carries a person's name — so who the account holder *is* changes no figure. Thinesh's clarifications, recorded for reference: **LEDSone UK = `led_sone`** and **Ledsone DE = `ledsonede`** are two **separate accounts** (confirmed live). **Sunsone = `so_926407` is ONE account** selling to both UK (475 orders/30d) and DE (77) — "Sunsone UK — powsteena" and "Sunsone DE — sivajitha" are two people on **one** account, which under decision **F** (one row per account) produces a single row. ⚠ **If an AH-name column is ever added**, three things must be resolved first: (1) "Jarshini" matches nobody — `staff.users` holds **`Jarsini`** (91) and **`Jasmini`** (84), two different Active people; (2) Sunsone's single row would carry two holders; (3) seven accounts have no holder named. ✅ Verified Active: `Sharmilan` (232) · `kobiga` (157) · `powsteena` (162 — not "Powesteena") · `genga` (143) · `Sivajitha` (231). | — | Build unblocked. |
| ~~P-orig~~ | **the AH name map does not reconcile to the live roster.** Three problems in the eight rows Thinesh supplied: **(1) 🔴 "Jarshini" does not exist.** `staff.users` holds **`Jarsini`** (id 91) *and* **`Jasmini`** (id 84) — two different Active people, neither spelled Jarshini. Which one owns `huettenlampen` and `ledsonede`? (This is the same trap that forced a rebuild in REQ-12.) **(2) Duplicate/unknown account labels** — "LEDSone UK" (Sharmilan) *and* "LEDSone UK Reg" (Genga) both map to the single `led_sone` account; "Sunsone UK" (Powesteena) *and* "Sunsone" (Sivajitha) both map to `so_926407`. What is "Reg", and which person owns which? **(3) Seven of the 13 accounts have no AH named** — `vintageinterior`, `dctransformer`, `re6865`, `neighbourmarket`, `lighting_sone`, `homin_gmbh`, `bestbringer`. Their AH name renders **blank**; their AH *listings and sales* still compute. ✅ Verified Active in `staff.users`: `Sharmilan` (232) · `kobiga` (157) · `powsteena` (162 — note spelling, not "Powesteena") · `genga` (143) · `Sivajitha` (231). | **Thinesh** | AH **names** are wrong or missing for 9 of 13 accounts until resolved. AH figures are unaffected. |
| ~~H~~ | ✅ **CLOSED 2026-07-23 — YESTERDAY ONLY.** `Units Sold` is a single figure for the anchor day (R−1). No prior-day or last-year units. | — | |
| ~~I~~ | ✅ **CLOSED 2026-07-23 — SNAPSHOT, REPLACES.** Each morning's run **replaces** the previous output; no history accumulates. No history table, no append. The `ph_task` row is refreshed in place (the EBPD pattern). ⚠ Note the sheet is *named* "Track" but is a snapshot — the accumulating daily series the business currently lacks is **not** created by this deliverable. ✅ Side benefit: this **retires the restatement worry** raised under decision **M** — with no stored history, a later refund cannot leave a stale published figure behind. | — | |
| **J** | **Cadence, delivery time and publish audience.** Candidate audience `ebay_priors` (Thinesh · Jarsini · kobiga · powsteena). | Thinesh + Varmen | See the scheduling constraint below. |
| ~~K~~ | ~~`Active Listing` — REQ-13's definition or REQ-16's?~~ | — | ✅ **CLOSED 2026-07-23 BY THE AIOS KNOWLEDGE BASE — neither.** `business/queries/ph-sales-by-channel.md` states the eBay listing filter is **`all_list = 1`**, and explicitly: *"Do not use `is_child`/`is_parent` combinations."* Both prior definitions were wrong. |
| ~~N~~ | ~~The publish target is unreachable under the source lock~~ | — | ✅ **CLOSED 2026-07-23 — the owner clarified the lock governs DATA RETRIEVAL only.** Every figure is retrieved via the two named MCPs; the output step is unaffected, so publishing to `tech_team_outputs.ph_task` (warehouse) remains the normal route. Still gated on decision **J** (audience named + each recipient verified) and explicit owner instruction — as for every prior report. |
| 🟠 **O** | **A Portfolio Holder dashboard already exists.** AIOS KB `infrastructure/postgres-access.md` documents a third database on the same instance — **`ph_dashboard`** (Django app), with `analytics_phmonthchannel`, `analytics_phtotalids`, `analytics_metricpoint`. `analytics_phmonthchannel` (PH × month × channel) is adjacent to this report's PH columns. ⚠ **Not readable** — `dbhub_readonly` has no grants on it; the `ph_pgsql` role would be needed. | Sajeesan + Varmen | **Duplicate risk.** Must be checked before REQ-17 builds its own PH view. |
| **L** | **Confirm `PRJ-2026-015` / `REQ-17` / code `dst`**, and the channel-neutral project name. | Varmen | The source carries no requirement number. |

⚠ **Scheduling constraint for decision J.** REQ-17-D02 would be the automation fleet's **7th**
scheduled job and its **first daily** one — every existing job is weekly or monthly. All seven share
the same restricted `temp_user` account, and **Monday 11:00 is already taken twice** (EPPA and T7).
A daily slot must be chosen clear of the existing six.

## Reviewer gates

- **Thinesh (business)** — ⬜ pending. **Owns decisions A–E, G–J.** A is the blocker.
- **Sajeesan (technical)** — ⬜ pending. Owns K, co-owns F.
- **Tamil Selvan (queryability)** — ⬜ pending.
- **Varmen (coordination / ID approval)** — ⬜ pending. Owns L.

## Register links

- Task index: `TASK_REGISTER.md`
- Full functional detail: `SYSTEM_REFERENCE.md`
- Execution rules: `CLAUDE.md`
- Portfolio row: `../../PROJECT_REGISTER.md` — ✅ added 2026-07-23
- Source manifest: `evidence/source_documents/REQ-17_daily-sales-track/SOURCE_MANIFEST.md`
- Daily requirement document:
  `DigitWeb_Works_Abiraj/23_07_2026/2026-07-23_abiraj_REQ-dst_REQ-17-D01.md`
- Inherited definitions: `../PRJ-2026-011_ebay-account-performance-dashboard/SYSTEM_REFERENCE.md`

## Next action

1. **Run the Step-2 data-availability audit** (read-only, both databases) into
   `evidence/logs_or_screenshots/REQ-17_daily-sales-track/`. It must establish: the daily grain and
   its timezone boundary · daily-series completeness · how far back the last-year comparator is
   populated · **whether any AH/PH assignment object exists in either database** (sweep by **column**
   name, not only table name — the mistake that made REQ-11's first audit wrong) · which
   `Active Listing` definition to adopt · one hand-reconciled account-day.
2. **Route the decision sheet to Thinesh with that evidence attached — A first**, then B, C, D, E, F.
3. Only then build REQ-17-D01.
