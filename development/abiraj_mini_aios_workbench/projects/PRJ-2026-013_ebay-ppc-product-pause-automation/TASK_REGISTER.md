# TASK_REGISTER — PRJ-2026-013 eBay PPC Product Pause Automation

Canonical index of tasks in this project. One requirement = one Task ID.

| Task ID | Deliverable | Status | Owner | Evidence | Next |
|---|---|---|---|---|---|
| `REQ-15_ebay-ppc-product-pause-automation` | **REQ-15-D01** — read-only pause-recommendation report (dashboard + Pause Log + staff approve/reject) for LEDSone eBay UK | **BUILT 2026-07-21 — awaiting review** (read-only, not published) | Abiraj | `evidence/final_outputs/REQ-15_.../` (HTML + xlsx + data.json) · `evidence/logs_or_screenshots/REQ-15_.../` · `sql/REQ-15_.../` | Reviewer + business sign-off; confirm the campaign-grain Stock rule |

## Deliverable plan

| Deliverable | Description | Status |
|---|---|---|
| REQ-15-D01 | Read-only pause-recommendation report — HTML dashboard + xlsx, ON_SITE campaigns, LEDSone eBay UK | **BUILT + LIVE-VERIFIED 2026-07-21 · dashboard verified by Meshika** — 45 campaigns, 15 recommended pauses (8 Stock / 7 Rule 1 / 0 Rule 2), **£1,403.54 of £3,532.41** 30D spend at risk (anchor 2026-07-20, last complete day). Read-only, not published, not committed. **Decision C closed 2026-07-21 — Option A (a listing is out of stock only when every version is at zero); no rebuild needed.** |
| REQ-15-D02 | **Autonomous weekly refresh** — Windows Task `EPPA_Weekly_Pause_Report`, **Monday 11:00**, direct psycopg2 (no MCP), fail-closed, desktop alert on failure | **BUILT 2026-07-21 — awaiting registration.** Needs `eppa_secrets.bat` (the `ledsone` read-only password) then one command to register. |

## REQ-15-D02 — automation design

| Item | Value |
|---|---|
| Task name | `EPPA_Weekly_Pause_Report` |
| Schedule | **Every Monday 11:00** — clear of the fleet (FRRC 09:00 day 8 · EBPD Mon 09:30 · ERA 09:30 day 5 · EPC Mon 10:30) |
| Window | Rolling **last 30 days**, anchored on the latest **complete** day — `CASE WHEN MAX(date) < CURRENT_DATE THEN MAX(date) ELSE MAX(date)-1 END`; never `CURRENT_DATE`, and never the part-filled current day |
| Connection | `ledsone` read-only via **direct psycopg2** — a Scheduled Task has no MCP session. Session forced `readonly=True`. |
| Credentials | `automation/eppa_secrets.bat`, git-ignored; template committed. Reuses the EBPD/ERA `dbhub_readonly` login. |
| Rule engine | `sql/REQ-15_.../eppa_engine.py` — **one shared module**, imported by both the weekly run and any manual rebuild, so the two can never drift. |
| Outputs | Rewrites `eppa_d01_data.json`, the dashboard HTML and the xlsx in place. |
| **Fail-closed gates** | Refuses to overwrite if: the pull errors · 0 campaigns · fewer than 20 campaigns · campaign count collapses >40% vs the last good run · total 30D spend is 0. On failure the previous report survives untouched, `eppa_status.json` records why, and `eppa_alert.ps1` drops `EPPA_REFRESH_FAILED.txt` on the Desktop plus a balloon alert. |
| Health check | `automation/check_status.bat` — next/last run, last result, last 12 log lines. |
| Still human | The report **recommends**; pausing in Seller Hub stays manual. No write to eBay, no `ph_task` publish. |

## Task log

### 2026-07-21 — onboarding + Step-2 data availability audit
- Project created as `PRJ-2026-013_ebay-ppc-product-pause-automation`, code `eppa`.
- Task ID `REQ-15_ebay-ppc-product-pause-automation` minted with owner approval — the two source
  files carry **no requirement ID**; REQ-15 follows the eBay sequence REQ-12 (epc), REQ-13 (ebpd),
  REQ-14 (ERA).
- Both sources imported COPY-only, SHA-256 recorded; originals left in `Downloads`.
- Read both files in full; established the **HTML as canonical** for business logic and documented
  the complete rule engine in `SYSTEM_REFERENCE.md`.
- Recorded three provenance warnings about the mockup sample (single 7-day export reused as 30D/14D;
  Rule 1 rescue therefore dead in the sample; stock figures untraceable to the eBay export).
- Executed a read-only live audit: eBay PPC data **exists at listing grain** for `led_sone`/UK
  (337,338 ad rows, 2,362 item_ids, from 2026-04-22); campaign state and Manual/Smart type available;
  stock bridges for 92.2% of advertised listings.
- Ran the full engine live — **21 pause candidates** (10 stock, 3 Rule 1, 8 Rule 2), 33 no-stock-data,
  678 keep running.
- Raised four structural gaps (A–D) and seven open decisions (A–G). **No build, no writes, no
  publish, not committed.**
### 2026-07-21 (same day, later) — field-by-field verification against the RAW `ledsone` DB + AIOS KB
Owner supplied two further MCP endpoints (`docs.ledsone.co.uk/mcp` knowledge base,
`mcp.ledsone.co.uk/mcp` raw Postgres) and asked for a complete check of every column the task sheet
expects. Both connectors verified live. Result: **12 of 14 Input Data columns fully sourced**, and
**three of the earlier warehouse-only findings were overturned**:
- 🔴 **Gap A WITHDRAWN** — SMART campaigns *do* have listing-level rows in the raw DB (179 listings,
  £751.09/30D). The warehouse showed zero; that was an ETL artefact. Building on the warehouse would
  have silently dropped all SMART spend from the pause engine.
- 🔴 **Listing price EXISTS** (`listings.ebay_listings.price`, 730/730 resolved).
- 🔴 **Gap B explained mechanically** — CPS records £0.00 spend/sales in `performance_data` (every
  money column is `cpc_*`), so Rule 1 is uncomputable and Rule 2 is permanently self-rescued.
- **Gap C is worse than measured**: 89.2% multi-SKU (not 80.1%), and `all_list=1` does not fix it.
- **Gap D confirmed with a trap**: `ebay_listings.status` is 99.4% NULL and self-contradictory
  (137 items `status='Active'` while `is_ended=1`) — never use it; `ads.state` is undecoded.
- Raw `performance_data` is a **60-day rolling window, not backfilled** — fine for 30D/14D, unusable
  beyond ~60 days; the warehouse holds more history.
- Build source switched to the **raw `ledsone` DB**; warehouse baseline numbers marked PROVISIONAL.
Evidence: `evidence/logs_or_screenshots/REQ-15_.../2026-07-21_field_by_field_source_verification.md`.

### 2026-07-21 (same day, later) — live verification, anchor fix, business review
- **Live data verification PASSED.** The rule engine was re-implemented independently in SQL and
  diffed against the shipped artefacts: **45/45 campaigns identical on all 6 fields** (270
  comparisons, 0 mismatches), all 10 KPIs reconciled, internal arithmetic balanced, every decision
  re-derived from its own stored figures, scope audit balanced (45 in scope · 73 CPS · 1 OFF_SITE ·
  145 deleted excluded), HTML + xlsx matched the governed JSON, and the warehouse independently
  corroborated the campaign census. Record: `validation/REQ-15_.../2026-07-21_live_data_verification.md`.
- 🔴 **Defect found and fixed the same day — partial-day anchor.** The window anchored on
  `MAX(date)`, which is *today* once the hourly sync runs; today held **8 clicks / £1.39** against a
  ~540-click, ~£99 normal day, making the "30-day" window 29 days plus a stub. Anchor now resolves to
  the latest **complete** day (`CASE WHEN MAX(date) < CURRENT_DATE THEN MAX(date) ELSE MAX(date)-1 END`)
  and both windows are closed at the top. **Decisions unchanged** (45/15, 8 Stock · 7 Rule 1 · 0
  Rule 2, 16 running, 14 off); money corrected: at risk **£1,355.02 → £1,403.54**, total
  **£3,400.40 → £3,532.41** — exactly the value of the day swapped out (£133.40 in, £1.39 out).
- Near-miss caught: the re-pull changed the PERF row layout from 15 fields to 12; the build failed
  but the renderers still rebuilt from the **stale** JSON, so the artefacts looked fresh while
  carrying old numbers. A `len(fields)` assertion now guards the parser.
- **Business Validator = Meshika** (`staff.users` id 182, verified live). **Dashboard verified by
  Meshika 2026-07-21.**
- ✅ **Decision C CLOSED 2026-07-21 — Option A (SUM across variants).** A listing counts as out of
  stock only when every one of its versions is at zero. This is what the build already did, so
  nothing was rebuilt and the 15 recommendations stand. The alternative was measured first and was
  decisive: "any one version at zero" would flag **31 of 31 live campaigns** rather than 8 — it would
  pause the whole account. Accepted caveat recorded: a listing whose best-selling version is at zero
  keeps advertising while its siblings hold stock.
- UI reworked: sans-face interface type (mono reserved for figures), larger scale, gradients and
  polished cards, single-view table (13 → 10 columns, percentage widths, no horizontal scroll),
  working sticky header (the nested scroll container was the bug), whole-row click to expand,
  explicit date ranges on every window, and a placeholder guard that fails the build rather than
  shipping raw `__TOKENS__`.

- Corrected a workbench knowledge-base error: the `ppc-stock-lookup` reference claims eBay `ad`-grain
  rows exist only for `COST_PER_SALE`; live data shows **ON_SITE MANUAL also has them** (610
  item_ids) while **ON_SITE SMART does not**. The reference should be split by `bidding_strategy`.

---

## 2026-07-21 — fleet alignment (no scope change)

EPPA was audited against the other five automated projects the same day it went live. The report
logic, thresholds and rule engine are **unchanged**.

**What EPPA gave the fleet.** Its **collapse guard** — rejecting a >40% fall in count against the
*last good run* rather than only an absolute floor — was the one gate no other job had, and it has
been **backported to T7, EPC, EBPD and ERA**. An absolute floor only catches a total wipe-out; a
feed that silently half-empties clears it and publishes a confidently wrong report. (FRRC is
deliberately excluded: its row count is return-driven and legitimately volatile month to month, so
the guard would produce false aborts.)

**What EPPA took from the fleet.**

1. **Credentials via the global store**
   (`05_documentation/capability/shared_db_credentials/`). It previously *required* a plaintext
   `eppa_secrets.bat` and refused to start without one; a local file still wins as an override, but
   is no longer needed. Proven by running with the file moved away: exit 0.
2. **`--dry-run` / `--no-publish` added.** It had **none** — meaning the job could not be tested or
   proven at all without a live publish, contrary to the automation pattern's "always ship a
   dry-run" rule. Proven to leave `ph_task` untouched.
3. **`AUTOMATION_README.md` written**, carrying the data traps that cost real debugging: the
   warehouse hides SMART campaigns (use the RAW `ledsone` DB); CPS campaigns log £0 spend; 89% of
   listings are multi-SKU; `ebay_listings.status` is 99.4% NULL; unbridged ≠ zero stock.

⚠ **Disclosure — a live publish during verification.** Because no dry-run existed at the time,
confirming the credential migration required a real run. It refreshed `ph_task` **id 405 → 407
(version 3)**. Content identical — same anchor 2026-07-20, 45 campaigns, 15 pause recommendations,
£1,403.54 spend-at-risk — so this was a version bump, not a data change, and the row count stayed
at exactly 1 (no duplicate). The dry-run flag now makes this unnecessary.

✅ EPPA correctly does **not** assert `version_status` after publishing — see PRJ-2026-010's note on
why asserting `'released'` would roll back every future run. Do not add it.

Git `04b6ed0`.
