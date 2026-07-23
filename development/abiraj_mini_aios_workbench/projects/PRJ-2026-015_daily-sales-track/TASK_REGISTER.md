# TASK_REGISTER — PRJ-2026-015 Daily Sales Track

Canonical index of tasks in this project. One requirement = one Task ID.

| Task ID | Deliverable | Status | Owner | Evidence | Next |
|---|---|---|---|---|---|
| `REQ-17_daily-sales-track` | **REQ-17-D01** — read-only daily sales tracker (22 columns per account per day + a 9-KPI panel): governed dataset + dashboard + workbook | **DELIVERED · VERIFIED · PUBLISHED 2026-07-23.** 30 account × marketplace rows, 24 columns, money per currency (never blended), 18/18 checks, ph_task 422-425 v4. Not automated. Superseded note follows:  Specification received, read cell-by-cell and analysed; source imported COPY-only with SHA-256 verified byte-identical. **No live query has been run.** Blocked on decision **A** for 6 of 22 columns | Abiraj | `evidence/source_documents/REQ-17_.../` (source + SOURCE_MANIFEST) · `DigitWeb_Works_Abiraj/23_07_2026/2026-07-23_abiraj_REQ-dst_REQ-17-D01.md` (requirement document) | Run the Step-2 data-availability audit; then route decisions **A, B, C, D, E, F** to Thinesh |

## Deliverable plan

**REQ-17-D01 is the report, and it is three artefacts** — the governed JSON dataset, the HTML
dashboard and the xlsx workbook. They are one deliverable because they are one dataset rendered three
ways. (Same shape as REQ-16-D01.) All three must come from **one generator module** — REQ-16 shipped
a defect where the workbook and dashboard were built from separate fetches and drifted.

| Deliverable | Description | Status |
|---|---|---|
| **REQ-17-D01** | Read-only daily tracker. **(a)** governed JSON dataset · **(b)** static-rendered HTML dashboard — 22 columns, the 9 KPIs as cards that recompute on the filtered view, account/marketplace/trend filters, date selector, frozen Account column, trend colour bars, CSV export · **(c)** xlsx workbook — *Daily Sales Track* (22 columns) · *KPI Summary* (the 9 KPIs) · *Config* (editable trend thresholds) · *Data Notes* (every source, inheritance, assumption and gap) | ⬜ **NOT STARTED** |
| REQ-17-D02 | Autonomous scheduled refresh — fail-closed, the fleet's **7th** job and its **first daily** one | ⬜ **NOT STARTED** — blocked on decisions **I** (track vs snapshot) and **J** (cadence + slot) |

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
| I8 | Columns with no definition or source | 🔴 **6 of 22** — cols 16–21 (AH/PH) |
| I9 | Duplicate-risk assessed against the portfolio | ⚠ **AMBER vs REQ-13 (EBPD)** — 13 of 22 columns are its daily equivalent; resolved as **EXTEND**, definitions inherited verbatim |
| I10 | Live data availability | ⬜ **NOT TESTED** — no query has been run for this requirement |

## PASS / FAIL rules for REQ-17-D01

To be evaluated when D01 is built. Stated now so the build cannot move the goalposts later.

| # | Measurable rule | Status |
|---|---|---|
| P1 | Reproduces the 22 source columns — exact text, exact order | ⬜ |
| P2 | Reproduces the 9-KPI panel, with AOV computed portfolio-wide (Σ sales ÷ Σ orders), not as a mean of per-account AOVs | ⬜ |
| P3 | Sales, Orders, Units and AOV match **REQ-13's inherited definitions exactly** — verified by running REQ-13's own query for an overlapping period and reconciling | ⬜ |
| P4 | The anchor is a **complete** day; two consecutive runs on the same anchor produce an identical payload | ⬜ |
| P5 | Every one of the 22 columns carries a stated `schema.table.column` or is visibly blank with a stated reason — **no column ships silently empty** | ⬜ |
| P6 | Trend bands are editable configuration, never inlined in SQL | ⬜ |
| P7 | The formula layer reproduces the 32 verified sample relationships | ⬜ |
| P8 | Absent data renders **blank, never zero**, in every sales, orders, growth and LY column | ⬜ |
| P9 | Independently re-implemented and diffed row-by-row, 0 mismatches | ⬜ |
| P10 | At least one account-day reconciled by hand to a figure the requester can verify independently | ⬜ |
| P11 | Every gap disclosed **inside** the deliverable (Data Notes), not only in the governance files | ⬜ |
| P12 | The REQ-16 divergence (`Completed`-only vs Refunded/Inprogress-included) stated on the deliverable | ⬜ |

## Blocking items

| # | Item | Blocks |
|---|---|---|
| 🔴 **A** | AH / PH definition and assignment source | **Columns 16–21 — 27% of the report.** Unanswerable by any database work |
| 🔴 **B** | Anchor — last complete day or live intraday | Column 2 and every measure hanging off it |
| 🔴 **C** | Same Day LY — calendar date or weekday | Columns 7 and 11 |
| 🔴 **D** | Best Seller ranking basis | Column 14 |
| 🔴 **E** | Trend bands | Columns 18, 21, 22 |
| 🔴 **F** | Row grain — account or account × marketplace | Every row in the report |
| **K** | `Active Listing` — REQ-13's definition or REQ-16's | Column 15 |
| **I**, **J** | Track vs snapshot; cadence and slot | REQ-17-D02 |
| **G**, **H**, **L** | Scope; Units period; ID confirmation | Scoping and naming |

Full decision table with owners: `PROJECT_HOME.md`.

## Next

1. Step-2 data-availability audit (read-only, both databases) →
   `evidence/logs_or_screenshots/REQ-17_daily-sales-track/`.
2. Route the decision sheet to Thinesh with that evidence attached — **A first**.
3. Build REQ-17-D01 only after A, B, C, D, E and F are closed.
