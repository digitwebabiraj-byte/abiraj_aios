# TASK_REGISTER — PRJ-2026-014 eBay Slow Moving & No Moving Products

Canonical index of tasks in this project. One requirement = one Task ID.

| Task ID | Deliverable | Status | Owner | Evidence | Next |
|---|---|---|---|---|---|
| `REQ-16_ebay-slow-no-moving-products` | **REQ-16-D01** — read-only slow/no-mover report (12-rule action engine) across all active eBay accounts, UK + Germany: **reviewer dashboard (HTML) + workbook (xlsx) + governed dataset (JSON)** | **BUILT · VERIFIED · PUBLISHED 2026-07-22** (ph_task 411-414, `ebay_priors`, v4) — awaiting reviewer sign-off | Abiraj | `evidence/final_outputs/REQ-16_.../` (HTML + xlsx + data.json) · `evidence/logs_or_screenshots/REQ-16_.../` (data audit) · `evidence/source_documents/REQ-16_.../` (source + SHA-256) · `sql/REQ-16_.../` (generator + renderer) · `validation/REQ-16_.../` (2 verification records + re-runnable harness) | Confirm IDs; close decisions A, C, F, **H** (partial-day anchor) |

## Deliverable plan

**REQ-16-D01 is the report, and it is three artefacts** — the HTML dashboard, the xlsx workbook and
the `esnm_d01_data.json` behind both. They are one deliverable because they are one dataset rendered
three ways; the dashboard is not a separate deliverable. (Same shape as REQ-15-D01, which was an HTML
console plus a workbook.)

| Deliverable | Description | Status |
|---|---|---|
| **REQ-16-D01** | Read-only slow/no-mover report, **11,156 listings**, 12-rule action engine with editable thresholds. Three artefacts: **(a)** `REQ-16-D01_esnm_dashboard.html` — full-screen reviewer console, **20 columns**, product thumbnails with hover zoom + click-through to eBay, date + dimension filters, KPI cards that recompute on the filtered view, frozen Image/Account columns, priority edge bars, inline stock bars, collapse toggles, full-screen control; **(b)** `REQ-16-D01_slow_no_moving_products.xlsx` — 5 sheets, **21 columns** (the 20 source columns plus the split last-year comparator), live-formula engine; **(c)** `esnm_d01_data.json` — the governed dataset both renderers read | **BUILT 2026-07-22.** Anchor 2026-07-22: **8,067 Critical (End Listing) · 1,210 Clearance · 851 Price Cut · 476 SEO · 149 Bundle · 42 Competitor Review · 26 Listing Quality · 2 Pause PPC · 109 Maintain · 53 Grow · 171 Monitor.** **PUBLISHED to ph_task 411-414 (`ebay_priors`, v4).** Read-only, **not automated**. Counts drift between rebuilds - see decision **H**. |
| REQ-16-D02 | Autonomous scheduled refresh — fail-closed weekly/monthly job rebuilding all three artefacts | **NOT STARTED** — blocked on decision **D** (cadence); would be the fleet's 7th job |

⚠ **Column-count divergence inside D01:** the dashboard shows **20** columns, the workbook **21**.
`Watchers` was removed from the dashboard on the owner's instruction 2026-07-22 because it can never
be populated; the workbook retains it blank so the artefact still matches the requirement sheet
literally. Record against decision **A**.

`ph_task` publication is **not** a separate deliverable — it is a publish step on D01. ✅ **Done
2026-07-22**: ids 411-414, audience `ebay_priors`, decision **E** closed.

## PASS / FAIL rules for REQ-16-D01

| # | Measurable rule | Result 2026-07-22 |
|---|---|---|
| P1 | Reproduces the 20 source columns — exact text, exact order | ✅ 20/20 |
| P2 | Row count equals the live in-scope universe | ✅ 11,156 = 11,156 |
| P3 | **Zero** formula errors anywhere in the workbook | ✅ 0 |
| P4 | In-sheet engine agrees with an **independent** implementation on **every** row | ✅ 0 mismatches / 11,156 |
| P5 | Sampled rows reconcile field-by-field to the live database | ✅ item `164889807930` exact on 7 fields |
| P6 | Summary totals reconcile to the detail sheet | ✅ 11,156 / 8,067 |
| P7 | Every threshold is editable configuration, not hardcoded | ✅ Rules sheet |
| P8 | Every gap disclosed **inside** the deliverable | ✅ Data Notes sheet |
| P9 | No figure originates from the fabricated source sample | ✅ |
| P10 | Read-only throughout — **no write to eBay** or any live business schema | ✅ (⚠ `ph_task` was written on 2026-07-22 as an authorised publish — the only write this project makes) |

**All ten green.** ⚠ Green on P1–P10 proves the artefact is internally sound and matches live data;
it does **not** close the three business assumptions (decisions A, C, G).

## Task log

### 2026-07-22 — onboarding, data availability audit, and D01 build

- Project created as `PRJ-2026-014_ebay-slow-no-moving-products`, code `esnm`. Task ID
  `REQ-16_ebay-slow-no-moving-products` **minted pending owner confirmation** — the source file
  carries **no requirement ID**; REQ-16 follows the eBay sequence REQ-12 (`epc`), REQ-13 (`ebpd`),
  REQ-14 (`ERA`), REQ-15 (`eppa`).
- Source imported COPY-only, SHA-256 recorded; original left in `Downloads`.
- Read the source in full. Established **rows 20–32 (the rule table) as canonical**, and recorded
  four provenance warnings — most importantly that **rows 1–11 are fabricated** and that the
  sample's own `Action Required` values **contradict the file's own rule table** (e.g. `LED-004`'s
  figures satisfy Rule 4 but the sample says "Bundle Product"), so the sample cannot be used to
  infer precedence or as a reconciliation baseline.
- **Scope confirmed by the owner:** all active eBay accounts (not the three in the sample),
  **UK + Germany only**. Resulting universe **12 accounts · 16 account × marketplace · 11,156
  listings** (UK 7,685 / Germany 3,471). **`neighbourmarket` falls out** — US-only.
- 🔴 **Key finding — this report needs TWO databases and cannot be built from either alone.**
  A first-pass audit of only the `ledsone` DB concluded eBay Views, Conversion Rate and Watchers
  were all unavailable. **Two of the three were wrong.** eBay organic traffic lives in the
  **warehouse**, `public.traffic_data WHERE which_channel = 2` (`click` = page views,
  `conversion/click` = CVR). Conversely a **warehouse-only** build was tested and fails: Product
  Title is populated on only **8.3%** of in-scope eBay items (890 of 10,739).
- **Evidence Map produced for all 20 columns — 16 VERIFIED · 3 PARTIAL · 1 UNAVAILABLE.**
- 🔴 **`Watchers` (col 17) is UNAVAILABLE.** Every column in both databases scanned for
  `watch`/`favorite`/`wishlist`/`saved`; only unrelated `staging_ai.watched_status` hits. eBay
  exposes it only via the Trading API, which is not ingested. **Rule 6 can never fire.** Column
  ships blank, never `0`.
- 🔴 **eBay traffic ingestion lost 11 days** in the 90-day window — 7–11 May (5), 26 Jun +
  29 Jun–1 Jul (4), 26 Apr, 18 Jul; only **78 of 91 days** present (21–22 Jul is the normal ~2-day
  lag, not a failure). Proven **eBay-specific, not a pipeline outage** — Shopify loaded normally on
  every one of those dates. **Root cause is in neither database**: `public.etl_status` covers only
  the dblink copy from 19 Jul, `development.etl_run_log` only the `amazon_fbm` channel. Views
  understated ~12% over 90 days and **~23% over 30 days**, degrading Rules 5 and 9. Mitigated by
  evaluating those rules **only** where traffic rows exist and rendering absent traffic **blank,
  never zero**. Likely recoverable by re-running the eBay Analytics pull.
- 📌 **Correction made same day — a 90-day PPC figure DOES exist.** An earlier claim that it did not
  was based only on `ledsone` (65 days, from 2026-05-18). The **warehouse** `ppc_performance` covers
  the full 90 days at ad grain — **but omits SMART at ad grain** (£31,481.20 ad vs £39,454.11
  campaign, a £7,973 gap consistent with the EPPA finding). Build stayed on `ledsone`
  (complete but shorter); Rule 8 runs on 30 days, fully covered by both.
- 🔴 **Material finding — 51.7% of in-scope listings carry `wrong_sku = 1`** (5,767 of 11,156).
  These are **real, live, sellable listings** with proper titles, stock and prices (e.g.
  `265660320119`, 248 units, £18.59); the flag only means the SKU string is not a clean inventory
  code. **`wrong_sku` is deliberately NOT filtered** — excluding it would delete half the portfolio
  from a dead-stock report. The warehouse's standing "always filter `wrong_sku = 0`" rule applies to
  SKU→inventory bridging, a path this report does not use. Disclosed: column 4 is unreliable for
  those rows and none of them bridge to inventory.
- ✅ **Scope discrepancy RESOLVED (not stale data).** `ledsone` returns 11,156 at
  `is_ended=0 AND is_child=0`; the warehouse returns 10,739 distinct `ref_id`. The two encode
  parent/child differently — in warehouse `listing_data`, `is_child = 0` yields only **890** rows,
  exactly equal to `is_parent = 1`, so its sellable grain is `is_child = 1`. The warehouse also
  applies `wrong_sku = 0`. **The counts are not comparable and neither is wrong**; `ledsone`'s
  11,156 is the correct universe.
- 🔴 **Structural finding — Rule 10 is unreachable.** Any listing meeting "age > 180d AND last sale
  > 90d" necessarily has zero 90-day sales, so Rule 1 (Critical) always claims it first. Matched
  **0 of 11,156**. A property of the rule set, not a data fault.
- ⚠ **Two things the source never defines** were implemented as **explicit assumptions**, exposed as
  editable configuration and flagged for the Business Validator: **rule precedence** (Critical →
  High → Medium → Low, first match wins, lower rule number within a band) and **Rule 8's "PPC Spend
  High"** (**> £5.00 / 30 days** with zero sales).
- **REQ-16-D01 built and self-verified.** 5-sheet workbook; `Action Required` and `Sales Trend` are
  **live formulas** driven by an editable Rules sheet. The engine was implemented **twice
  independently** (Excel formulas + Python) and diffed row-by-row — **11,156/11,156 identical,
  0 mismatches**, **0 formula errors** workbook-wide. Item `164889807930` reconciled exactly on all
  seven measured fields against both databases. All ten PASS/FAIL rules green.
- ⚠ **Actionability flagged, not silently accepted:** **72.3% of rows carry the same Critical
  action**. An 8,067-row undifferentiated list is not operationally usable as delivered; ranking or
  capping is raised as decision **F** rather than applied unilaterally.
- Daily Requirement Document written to
  `DigitWeb_Works_Abiraj/22_07_2026/2026-07-22_abiraj_REQ-esnm_REQ-16-D01.md`.
- **Read-only throughout. No `ph_task` publish, no scheduled task, no git commit, no write to eBay.**

**Open at end of day:** IDs unconfirmed · independent validation record not yet written · decisions
A (Watchers), B (traffic backfill), C (precedence + Rule 10), D (cadence), E (publish audience),
F (actionability), G (Rule 8 threshold) all open · D02 and D03 not started.

### 2026-07-22 (same day, later) — dashboard, second last-year comparator, publish

- **Reviewer dashboard added to D01** (`REQ-16-D01_esnm_dashboard.html`, self-contained, ~3.2 MB):
  20 columns, product thumbnails with hover zoom and click-through to the live eBay listing, date
  + quick-range + priority + account + marketplace + action + search filters, frozen Image/Account
  columns, priority edge bars, inline stock magnitude bars, density toggle, light theme, row
  virtualisation for 11,156 rows. The dashboard is **part of D01**, not a separate deliverable —
  same shape as REQ-15-D01.
- 🔴 **Defect found and fixed — KPI cards never updated on filter.** They were computed once at
  load, so filtering the table to one account left whole-portfolio totals sitting beside it.
  Anyone screenshotting a filtered view would have reported the wrong number. Cards now recompute
  from the filtered view and are cross-checked to the DB (SunSone-UK 1,148 · LEDSone-UK 2,838 ·
  Coventry Lights-UK 536 · Germany 3,471 / 2,668 critical — all match).
- 🔴 **Pre-existing sort bug fixed.** The sort dictionary map pointed at column indices 19/20,
  which never existed, so "Action Required" sorted against the *status* lookup and produced
  nonsense ordering.
- **Owner requested `Watchers` removed from the dashboard** (it can never be populated). Dashboard
  is now 20 columns; **the workbook keeps all 21 including the blank Watchers column** for literal
  spec compliance. Divergence recorded against decision **A**.
- **Owner requested the last-year comparator split.** `Same Period Last Year` is now **two**
  columns — `LY 30d` (2025-06-23 → 2025-07-22) and `LY 90d` (2025-04-24 → 2025-07-22). Every Excel
  column letter from M shifted right; trend formula re-pointed to `=IF(N2=0,IF(L2>0,"NEW",0),(L2-N2)/N2)`,
  action formula moved to column U, autofilter to `A1:U`. **Sales Trend and Rule 4 stay on the
  90-day pair** — that is what the source's own sample rows reconcile to.
- **Owner requested no dashes under Sales Trend.** Filled with `0%` **only where both windows are
  zero** (6,768 rows — genuinely no change). The other **1,504** rows had zero last year but sales
  *this* year, one of them 111 units; writing 0% there would report a growing listing as flat, so
  they show **▲ NEW**. Zero dashes remain.
- **Embedded-layout defects fixed** after the report was seen inside the ph_task panel: a
  `min(860px,100vh)` floor was a no-op in an iframe (100vh resolves to the iframe's own short
  height); the short-viewport CSS block was inserted *before* the table rules and was losing the
  cascade; the footer caveat banner was wrapping to **133px**; and `width:max-content` defeated
  `table-layout:fixed`, leaving the table 3,104px wide against ~1,650px of pane. Now: table
  **1,880px**, 8 rows visible by default and 13 with the new **⌃ Filters / ⌃ Cards** collapse
  toggles, plus a **⛶ Full screen** control.
- ✅ **PUBLISHED to `tech_team_outputs.ph_task` — ids 411-414, audience `ebay_priors`**
  (Thinesh · Jarsini · kobiga · powsteena), one row each, currently v4. Publisher
  `automation/publish_esnm_ph_task.py` is dry-run by default and SELECT-then-UPDATEs because
  **there is no unique constraint on `task_id`**; it also sets `assigned_user_team`, which the
  sample DDL omits entirely and without which the rows never reach the audience.
- **Independent verification harness written** (`validation/REQ-16_.../verify_esnm_d01.py`) — it
  re-derives every figure from both live databases and the workbook **without importing the
  builder**, so a bug cannot mask itself. Result **17/17 data checks + 9/9 UI checks, 0 failures**,
  including a seeded 25-listing × ~15-field sample with 0 mismatches in ~375 comparisons.
- 🔴 **OPEN — decision H: the anchor sits on a partial day.** Rebuilds drift (Rule 1 8,067→8,066,
  row count 11,156→11,176). Not yet fixed because it changes figures already published.

### 2026-07-23 — business verification

- ✅ **Dashboard verified by Thinesh ("all ok")** — Business Validator gate closed. The report as
  published (ph_task 411-414, `ebay_priors`, v7, anchor 2026-07-22) is accepted by the requester.
- ⚠ **Recorded per the REQ-15 precedent:** an artefact verification does **not** by itself close a
  business assumption that must be confirmed explicitly. Two remain load-bearing:
  - **Decision C — rule precedence.** The source assigns priorities but never states multi-match
    resolution. The chosen order (Critical → High → Medium → Low, first match wins, lower rule
    number inside a band) is what makes **8,065 of 11,176 rows** read "End Listing" and what
    shadows **7,021 listings** out of Rule 10 entirely. If this is ruled differently the headline
    number and roughly a third of the recommendations change.
  - **Decision F — actionability.** 72.2% of rows carry one Critical action. The sharper cut is
    already measurable in the data: **1,299 listings sold 5,001 units in the same window last year
    and zero this year** (Declined) vs 3,761 Dormant and 3,007 Never-sold.
- Also still open: **A** (Watchers / Rule 6 permanently dark), **G** (£5.00 Rule 8 threshold),
  **B** (11 lost traffic days), ID confirmation, and Sajeesan / Tamil Selvan / Varmen sign-off.
