# TASK_REGISTER — PRJ-2026-015 Daily Sales Track

Canonical index of tasks in this project. One requirement = one Task ID.

| Task ID | Deliverable | Status | Owner | Evidence | Next |
|---|---|---|---|---|---|
| `REQ-17_daily-sales-track` | **REQ-17-D01** — read-only daily sales tracker (24 columns per account × marketplace + a 9-KPI panel): governed dataset + dashboard + workbook. **REQ-17-D02** — autonomous daily refresh | ✅ **CLOSED 2026-07-23 — DELIVERED · VERIFIED · PUBLISHED · AUTOMATED · SIGNED OFF.** 30 account × marketplace rows, 24 columns, money per currency (never blended, no FX table exists), 18/18 independent checks incl. the external Seller Hub anchor £837.93. Live on ph_task 422-425 (`ebay_priors`, **v9**, md5 `642a5a27`). Automated as `DST_Daily_Sales_Track`, **daily 09:05**, fail-closed on eleven gates, proven end to end (`LastTaskResult 0`). All four sign-offs received; duplicate check GREEN | Abiraj | `evidence/source_documents/REQ-17_.../` (source + SOURCE_MANIFEST, SHA-256 byte-identical) · `evidence/final_outputs/REQ-17_.../` (dashboard, workbook, governed JSON) · `validation/REQ-17_.../` (harness + records) · `automation/` · `09_closure/2026-07-23_REQ-17_daily-sales-track_closure.md` · `DigitWeb_Works_Abiraj/23_07_2026/` (requirement + skill file) | After 09:05 on 2026-07-24 run `automation\check_status.bat` — confirms the **unattended** fire, which a manual run does not prove. Then close decisions **E** (trend band) and **O** (`ph_dashboard` overlap) |

## Deliverable plan

**REQ-17-D01 is the report, and it is three artefacts** — the governed JSON dataset, the HTML
dashboard and the xlsx workbook. They are one deliverable because they are one dataset rendered three
ways. (Same shape as REQ-16-D01.) All three must come from **one generator module** — REQ-16 shipped
a defect where the workbook and dashboard were built from separate fetches and drifted.

| Deliverable | Description | Status |
|---|---|---|
| **REQ-17-D01** | Read-only daily tracker. **(a)** governed JSON dataset · **(b)** static-rendered HTML dashboard — **24 columns**, the 9 KPIs as **clickable** cards that recompute and re-sort on the filtered view, account/marketplace/trend filters, frozen Account column, grouped sticky headers, per-currency sticky footers, trend colour bars, CSV export · **(c)** xlsx workbook — *Daily Sales Track* (24 columns) · *KPI Summary* (the 9 KPIs, `SUMIF` per currency) · *Config* (editable trend thresholds) · *Engine Inputs* · *Data Notes* (every source, inheritance, assumption and gap) | ✅ **DELIVERED · VERIFIED 18/18 · PUBLISHED** — ph_task 422-425, v9, md5 `642a5a27` |
| REQ-17-D02 | Autonomous scheduled refresh — fail-closed on **eleven** gates, the fleet's **7th** job and its **first daily** one | ✅ **DELIVERED** — `DST_Daily_Sales_Track`, **daily 09:05**, `LastTaskResult 0`; next run 2026-07-24 |

⚠ **`ph_task` publication is not a separate deliverable** — it is a publish step on D01. **No publish
may occur**: the audience is undecided (decision J) and no recipient has been verified.

## Intake verification — what was actually proven on 2026-07-23

| # | Check | Result |
|---|---|---|
| I1 | Source imported COPY-only, original untouched | ✅ Original left in `C:\Users\digit\Downloads\` |
| I2 | Copy is byte-identical to the original | ✅ SHA-256 `C14CEB45…42B1`, 65,067 bytes, both sides |
| I3 | Every cell in the workbook read and inventoried | ✅ 22-column header · 6 sample rows · 9-KPI panel · rows 8–12 and 23–1000 empty · one sheet only |
| I4 | Structural features checked | ✅ No defined names, tables, merged cells, conditional formatting, freeze panes or autofilter |
| I5 | **Sample arithmetic independently re-derived** | ✅ **32 of 32 exact** — 9 KPIs + 24 per-row derived fields |
| I6 | Real formulas present? | 🔴 **None.** Apparent formulas are constants typed with a leading `=+` (`E2` = the literal `=+435.3`) |
| I7 | Sample usable as a value baseline? | 🔴 **No** — fabricated. 2 distinct accounts against a stated `Total Accounts = 6`; placeholder listing counts `1212 / 12 / 2222 / 22 / 111` |
| I8 | Columns with no definition or source | 🔴 **6 of 22 at intake** — cols 16–21 (AH/PH) → ✅ **all 6 closed** by decision A (AH = the PH remainder) |
| I9 | Duplicate-risk assessed against the portfolio | ⚠ **AMBER vs REQ-13 (EBPD)** at intake — 13 of 22 columns are its daily equivalent; resolved as **EXTEND**, definitions inherited verbatim → ✅ **GREEN at closure**, full record in `validation/REQ-17_.../2026-07-23_duplicate_check_and_signoff.md` |
| I10 | Live data availability | ✅ **TESTED** — `evidence/logs_or_screenshots/REQ-17_.../2026-07-23_data_availability_audit.md`; feasibility GREEN |

## PASS / FAIL rules for REQ-17-D01

Stated before the build so it could not move the goalposts later. **Evaluated 2026-07-23 by
`validation/REQ-17_.../verify_dst_d01.py` — a harness that does not import the builder, re-derives
every figure from a separate live query, and recalculates formulas through LibreOffice: 18/18, 0
failures.**

| # | Measurable rule | Status |
|---|---|---|
| P1 | Reproduces the 22 source columns — exact text, exact order | ✅ **PASS, superseded by owner decision** — `Best Seller` removed, `AH Holder` + `Market` + `Currency` added, so **24** columns ship. All surviving source headers keep their exact text and relative order |
| P2 | Reproduces the 9-KPI panel, with AOV computed portfolio-wide (Σ sales ÷ Σ orders), not as a mean of per-account AOVs | ✅ **PASS** — KPI sheet uses `SUMIF` **per currency**, so no cross-currency mean exists |
| P3 | Sales, Orders, Units and AOV match **REQ-13's inherited definitions exactly** | ✅ **PASS with one owner-approved divergence** — the **status filter**: this report counts orders **placed**, REQ-13 counts `Completed`. Deliberate (decision M): `Completed` matures ~2 days late and understates a daily view by 69%. Disclosed on the deliverable |
| P4 | The anchor is a **complete** day; two consecutive runs on the same anchor produce an identical payload | ✅ **PASS** — anchor pinned as a SQL literal, never `CURRENT_DATE`; the runner gates on **"the reported day must be in the past"** |
| P5 | Every column carries a stated `schema.table.column` or is visibly blank with a stated reason — **no column ships silently empty** | ✅ **PASS** — Data Notes sheet |
| P6 | Trend bands are editable configuration, never inlined in SQL | ✅ **PASS** — Config sheet (decision E still open on the *value*, not the mechanism) |
| P7 | The formula layer reproduces the 32 verified sample relationships | ✅ **PASS** |
| P8 | Absent data renders **blank, never zero**, in every sales, orders, growth and LY column | ✅ **PASS** — blanks are intentional and documented |
| P9 | Independently re-implemented and diffed row-by-row, 0 mismatches | ✅ **PASS** — 18/18, harness does not import the builder |
| P10 | At least one account-day reconciled by hand to a figure the requester can verify independently | ✅ **PASS — the one that matters.** `LEDSone UK / UK = £837.93` for 22 Jul 2026 reconciles to **Thinesh's own eBay Seller Hub screen**, and is now permanent gate **V14**. This check is what exposed both serious defects |
| P11 | Every gap disclosed **inside** the deliverable (Data Notes), not only in the governance files | ✅ **PASS** |
| P12 | The REQ-16 divergence (`Completed`-only vs Refunded/Inprogress-included) stated on the deliverable | ✅ **PASS** — Data Notes states both the REQ-13 divergence ("DOES NOT TIE TO EBPD") and the REQ-16 scope difference (~99.97% scope, not definition) |

**Three gates were added after the fact, specifically to stop the currency defect returning:** V15
(each row's currency matches `market_place_id_mapping`), V16 (each row renders its **own** symbol),
V17 (**no blended total anywhere**).

## Blocking items — 13 of 15 CLOSED 2026-07-23

| # | Item | Blocked | Resolution |
|---|---|---|---|
| ~~A~~ | AH / PH definition and assignment source | Columns 16–21 — 27% of the report | ✅ **AH = the PH remainder** (Thinesh). AH + PH = Active on every row — also a control total |
| ~~B~~ | Anchor — last complete day or live intraday | Column 2 and every measure hanging off it | ✅ Run on **R** reports **R−1**; anchor pinned as a literal |
| ~~C~~ | Same Day LY — calendar date or weekday | Columns 7 and 11 | ✅ **Same calendar date**; weekday difference disclosed |
| ~~D~~ | Best Seller ranking basis | Column 14 | ✅ **Column removed** |
| 🔴 **E** | Trend bands | The three trend columns | ⚠ **STILL OPEN.** Ships as editable config, default ±5%. Measured: a normal day swings 15–60% by account, so only **6.5%** of account-days read "Stable". Recommendation: compare against the **same weekday last week** |
| ~~F~~ | Row grain — account or account × marketplace | Every row in the report | ✅ **Account × marketplace** — reversed from account-only after the Seller Hub check; 13 rows → **30** |
| ~~K~~ | `Active Listing` — REQ-13's definition or REQ-16's | Column 15 | ✅ **`all_list = 1`** — settled by the AIOS knowledge base; **both** previously-used definitions were wrong |
| ~~I~~, ~~J~~ | Track vs snapshot; cadence and slot | REQ-17-D02 | ✅ **Snapshot that replaces**; `ebay_priors`, **daily 09:05** |
| ~~G~~, ~~H~~, ~~L~~ | Scope; Units period; ID confirmation | Scoping and naming | ✅ All eBay accounts; yesterday only; `REQ-17` confirmed by Varmen |
| ~~M~~ | Status filter — placed or completed | Every money figure | ✅ **Placed**, excluding `Cancelled` only |
| ~~N~~ | Does the source lock cover publishing? | REQ-17-D02 | ✅ Lock is **data retrieval only** — `ph_task` publishing unaffected |
| ~~P~~ | AH holder names | Display only | ✅ Shipped as the **AH Holder** column. ⚠ "Jarshini" matches nobody; confirmed **Jarsini** (id 91), not `Jasmini` (id 84) |
| 🔴 **O** | `ph_dashboard` duplicate check | Nothing — non-blocking | ⚠ **STILL OPEN.** `dbhub_readonly` has no grants; needs the `ph_pgsql` role |

Full decision table with owners: `PROJECT_HOME.md`.

## Next

1. Step-2 data-availability audit (read-only, both databases) →
   `evidence/logs_or_screenshots/REQ-17_daily-sales-track/`.
2. Route the decision sheet to Thinesh with that evidence attached — **A first**.
3. Build REQ-17-D01 only after A, B, C, D, E and F are closed.
