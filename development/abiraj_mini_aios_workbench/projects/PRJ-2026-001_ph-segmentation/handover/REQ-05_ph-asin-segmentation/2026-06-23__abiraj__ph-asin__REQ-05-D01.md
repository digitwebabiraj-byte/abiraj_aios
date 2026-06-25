# SKILL FILE — DAILY KNOWLEDGE EXTRACTION
# DIGITWEB LK LTD · Daily Skill Increment System · v3.0

---

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-23 |
| **developer** | abiraj |
| **project** | PH ASIN Segmentation — Growth Protection Engine (GPE) |
| **project\_code** | ph-asin |
| **phase** | DISCOVERY |
| **requirement\_id** | REQ-05 |
| **deliverable\_id** | REQ-05-D01 |
| **status** | **BLOCKED** — Mandatory pre-run scope check executed **live** on the connected Postgres MCP and **FAILED**: the connection is mis-scoped on both counts (sees far beyond the four allowed tables; exposes write-capable SQL). Per the project's own rule, work stops here and returns to Abiraj → Sajeesan to re-scope before any prompt is run. Requirement document also analysed: the segmentation already exists in `analytics.ph_segment`, with three document-vs-database conflicts pending an MD decision. **No prompt was run, no report produced, nothing written.** |
| **evidence\_location** | **Live MCP calls run this session (read-only):** `postgres:list_schemas` and one `information_schema.tables` count query — outputs captured in Section 3. Requirement doc: `Traffic_-_06_Segmentations_-_GPE__Growth_Protection_Engine_.docx` (PH ASIN Segmentation Protocol v1.0, owner Bietrick). Scope rules: project instruction doc ("Read-Only, Four Tables Only"). This file is the deliverable artifact. **No Git commit** (discovery + scope-verification day, no build). |
| **blos\_keys\_used** | NONE — this project does not consume BLOS rule/threshold keys. (The protocol carries its own kill-criteria + escalation thresholds; captured under `hardcoded_thresholds`, not as BLOS-* codes.) |
| **hardcoded\_thresholds** | **Benchmark:** top **30** sold ASINs per category in last 30 days; fall back to top **10** if <30 have sales; HIGH/LOW line = the **average (mean)** across that set. **Data window:** 30 days current + days **31–60** for movement. **DB filters:** `which_channel=1`, `market_place='UK'` (traffic_data / ph_segment); `source_name='AMAZON'`, `market_place='UK'` (order_transaction); `marketplace='UK'` (ppc_performance — note lowercase/no-underscore variant). **CVR:** `SUM(conversion)/NULLIF(SUM(click),0)*100`. **Kill criteria (FLAG only, never act):** margin <15% for 30d; CVR not +20% in 60d; CTR <1% after 2 fixes; impressions not +50% in 60d; units <20/month after overhaul; PPC ACoS >40% for 30d. **Escalation:** ASIN in LLL 2 months; HHH→LLL in one month; PH >30% ASINs in LLL; <10 sold ASINs in a category; >5 ASINs declined for one PH; action missed by 7th two months running. **Scope constants (this project):** allow-list = exactly `traffic_data, order_transaction, ppc_performance, analytics.ph_segment`; connection must be **read-only**. |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| MCP \| AMAZON-LISTINGS \| SEGMENTATION \| REPORTING \| SECURITY-SCOPE |

## File path:
# 2026-06-23__abiraj__ph-asin__REQ-05-D01.md
# DigitWeb_Works_Abiraj/23_06_2026/

---

## SECTION 1 · SYSTEM STATE

- **Current system state at start of today:** The PH ASIN Segmentation Protocol v1.0 (owner Bietrick) defines a monthly process that classifies every PH's UK Amazon FBM ASINs into performance segments from three live signals (Impressions, Clicks, Conversion/CVR), each rated HIGH/LOW against a per-PH, per-category benchmark. The intended tooling is a Claude Project + Postgres MCP that runs four prompts in order (benchmark → classify → movement → HTML report). This project's only job is to **run those four prompts read-only and produce the HTML report** — it plans nothing (GPT plans), builds no files, edits no repo.
- **What was working:** The Postgres MCP connector **is reachable from this chat** (clarified today — it is *not* on a separate account as the earlier handoff had assumed).
- **What was broken / missing / unknown at start:** (1) Whether the live MCP connection is correctly scoped (the project rule requires read-only access to exactly four tables). (2) Whether this project must *build* the segmentation or merely *read* it. (3) The category source, the meaning of `conversion`, the SKU→ASIN rollup, and the document's 6-vs-8 segment gap.
- **Your starting point today:** Before running any prompt, perform the **mandatory scope check** the project rules demand, and reconcile the requirement document against the live schema.
- **Operating rules (this project, authoritative):** read-only; four tables only; run the supplied prompt exactly as given (don't improve/shorten/reinterpret; if ambiguous, say so); never write/update/delete; never act on a kill-criteria threshold (flag, don't act); never invent an unretrievable number; never build/edit a repo (that's Claude Code's job); the documented report layout/colour spec is the source of truth; output a downloadable file for Abiraj to save under `evidence/monthly-reports/[YYYY-MM]/`.

> **In plain terms:** The rules say "before you do anything, check the database door is locked to read-only and opens onto only your four tables." I checked the door today. It is **not** locked and it opens onto the whole building. So I stopped — exactly as the rules require — instead of running the monthly prompts on a connection that could change live data or read things it shouldn't.

---

## SECTION 2 · WHAT CHANGED TODAY

This was a **discovery + scope-verification day**. No prompt was run, no report produced, nothing written. What changed: the mis-scope is now **confirmed on the live connection** (previously only suspected from the other account), and the project's real shape is pinned down.

- **Change 1 — Ran the mandatory pre-run scope check, live, read-only.** Loaded the Postgres MCP tools and called `list_schemas` + one `information_schema.tables` count. Result: the connection sees **16 user schemas / 542 base tables**, not the four allowed tables. **Scope check FAILED.**
- **Change 2 — Confirmed write capability is exposed.** The connection's SQL tool is described as "execute **any** SQL query" — i.e. write/update/delete is on the surface, not a read-only role. I did **not** test a write (testing one would itself break the never-write rule); the capability surface alone fails the rule.
- **Change 3 — Stopped and escalated, per the project rule.** The rule is explicit: *"If you can write… or if you can see tables outside this list, stop and tell Abiraj — that connection is mis-scoped and needs fixing by Sajeesan before any further use."* Did exactly that. No prompt run.
- **Change 4 — Read the requirement document and extracted its real instruction set:** six named segments, the per-PH per-category dynamic benchmark (top 30 / min 10, averaged), movement (current 30d vs days 31–60), and the four Section-4 prompts ending in the Section-5 HTML report spec.
- **Change 5 — Confirmed the key discovery: the segmentation already exists in `analytics.ph_segment`** (PH = `user_name`, `category_name`, per-signal segments, `overall_segment` code, `performance_segment_name`). So this is "read & show", not "build".
- **Change 6 — Logged three document-vs-database conflicts** (grouping of the 8 combos, bi-monthly vs 30-day cadence, segment names) for the MD decision (Section 4).
- **Change 7 — Settled the data unknowns:** category is a real column (not a SKU prefix); `conversion` is an order **count** (so the doc's CVR formula is valid); `order_transaction` needs SKU cleaning + rollup; the doc's 6-segment gap (HLL/LHL) is **already handled** in the DB (folded into Wallflowers / Niche Winners).

### Deliverables
- **Deliverable A — Live scope verdict:** connection mis-scoped on both counts → BLOCKED → routed to Sajeesan. (Primary outcome of the day.)
- **Deliverable B — Document analysis:** protocol instruction set + four-prompt pipeline extracted.
- **Deliverable C — Discovery finding:** segmentation already lives in `analytics.ph_segment`; project is read-and-show.
- **Deliverable D — Conflict register:** three document-vs-database conflicts logged for the MD.

Evidence: live `list_schemas` + `information_schema.tables` count (Section 3); requirement `.docx`; project scope-rules doc. No credentials included. No Git commit (no build).

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> **PostgreSQL via MCP. Read-only metadata listing only** — `list_schemas` and one `information_schema.tables` count. The four target tables' data was **not** queried; **nothing** was written; **no** prompt was run.

### Scope check — what the connection can actually see (FAIL)
The project allow-list is four tables. The live connection exposes **16 user schemas** and **542 base tables**:

| Schema | Base tables | Note |
| :---- | ----: | :---- |
| staging_ai | 368 | AI attribute/enrichment staging — out of scope |
| public | 69 | contains 3 of the 4 target tables, buried among 69 |
| development | 35 | out of scope |
| daily_task | 19 | out of scope |
| growth_protection_engine | 10 | **possibly project-relevant** (this protocol's home?) — still out of the four-table scope |
| message | 8 | out of scope |
| raw_data | 8 | out of scope |
| cppc_staff_ui | 5 | out of scope |
| cppc_intelligence | 5 | out of scope |
| validation | 4 | out of scope |
| analytics | 4 | contains the 4th target table `analytics.ph_segment` |
| business_intelligence | 2 | out of scope |
| audit | 2 | out of scope |
| governance | 1 | out of scope |
| tech_team_outputs | 1 | out of scope |
| ph_action_board | 1 | **possibly relevant** (tick/action state?) — still out of scope |

The four allowed tables exist (3 in `public`, `ph_segment` in `analytics`) but are surrounded by ~538 tables that should not be reachable. **Verdict: visibility scope = FAIL.**

### Scope check — write capability (FAIL)
The connection's SQL tool is described as *"Execute any SQL query."* That means `INSERT/UPDATE/DELETE/DDL` are reachable through this role. A correctly scoped connection for this project would be a `SELECT`-only role. **Not tested** (testing a write violates the never-write rule). **Verdict: write scope = FAIL.**

### Field reference for the four allowed tables (from doc Section 7 — for use *after* re-scope)
| Data point | Table | Field | Filter |
| :---- | :---- | :---- | :---- |
| Impressions | `traffic_data` | `impression` | `which_channel=1, market_place='UK'` |
| Clicks | `traffic_data` | `click` | same |
| CVR | `traffic_data` | `conversion / click × 100` | same; `NULLIF(click,0)` |
| ASIN | `traffic_data` | `ref_id` | not called `asin` |
| PH ownership | `analytics.ph_segment` | `user_name` | latest `period_end` |
| Units sold | `order_transaction` | `quantity` | `source_name='AMAZON', market_place='UK'` |
| Account | `order_transaction` | `ss_name` | `amazon Ledsone`/`amazon Dcvoltage` → LEDSone UK / DCVoltage UK |
| SKU | `order_transaction` | `sku` | join to traffic_data via ASIN |
| PPC spend | `ppc_performance` | `spend` | `source_name='AMAZON', marketplace='UK'` (lowercase) — kill-criteria only |

### `analytics.ph_segment` — the table that already does the job
Carried finding (from prior inspection, not re-queried today, since scope failed before any data read): 19 columns incl. `ref_id` (ASIN), `user_name` (PH), `category_name`, `overall_segment` (3-letter code), `performance_segment_name` (friendly name), the three per-signal segments, counts, `total_sales`. Live taxonomy folds all 8 combos into 6 names: **HLH+HLL → Wallflowers**, **LHL+LLH → Niche Winners** (this is how the DB covers the two combos the document omits).

### Data hygiene to apply once a run is authorised
`conversion` is an order **count** (not revenue). In `order_transaction`: drop junk SKUs `''`/`'---'`; `UPPER()`-normalise (case variants double-count); collapse suffix variants to base SKU before SKU→ASIN rollup. `ppc_performance` uses `marketplace` (no underscore) while others use `market_place`.

---

## SECTION 4 · GAP FOUND

- **Gap 1 — MCP connection mis-scoped, CONFIRMED LIVE (HIGH, OPEN — infra).** Sees 16 schemas / 542 tables (allow-list is 4) and exposes write-capable SQL. Impact: rule breach; risk of reading out-of-scope data or accidentally changing live data; cannot safely run any prompt. Recommended action: **Sajeesan** creates/points to a `SELECT`-only DB role granted on exactly the four tables and nothing else, then re-run this scope check to confirm. Owner: Sajeesan (fix), Abiraj (raise). **This blocks the whole project until fixed.**
- **Gap 2 — Document omits two of eight segments (MEDIUM, OPEN — MD decision).** Doc lists 6 segments; never accounts for **HLL** or **LHL**. The live DB handles all 8 (folded into Wallflowers / Niche Winners). Building strictly to the doc would leave HLL/LHL ASINs unclassified and contradict live data. Recommended: adopt the DB's 8→6 grouping or have Bietrick amend the doc. Owner: Bietrick / MD.
- **Gap 3 — Cadence conflict (MEDIUM, OPEN — MD decision).** Doc wants 30-day monthly windows; DB runs bi-monthly (1st–14th, 15th–28th), and the current period is incomplete. Movement means different things in each. Owner: Bietrick / MD.
- **Gap 4 — Naming conflict (LOW, OPEN).** Doc: Scale/Fix Now/Quick Win/Growth Play/Kill-Review/Maintain. DB: Champions/Leaky Buckets/Wallflowers/Hidden Gems/Niche Winners/Dead Horses. Owner: Bietrick / MD (pick canonical).
- **Gap 5 — The four prompt skill files are not yet in hand (LOW, OPEN).** `benchmark-calculator.md`, `segment-classifier.md`, `movement-tracker.md`, `report-generator.md` were not provided, so no prompt could be run verbatim even if scope passed. Recommended: paste the exact prompt file when a run is wanted. Owner: abiraj.
- **Gap 6 — Two on-server schemas may belong to this protocol (LOW, OPEN — clarify).** `growth_protection_engine` (10 tables) and `ph_action_board` (1 table) exist on the same DB and may hold protocol outputs / tick-box state — but they're outside the four-table scope, so left untouched. Clarify their relationship with Bietrick/Sajeesan. Owner: Bietrick / Sajeesan.

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

> No code written today. These are the **guardrails enforced in this session** and the rules to apply when a run is later authorised — recorded so they aren't trapped in anyone's head.

- **RULE ENFORCED TODAY — scope check before any execution.** Before running any of the four prompts, verify the connection is read-only and limited to the four tables. If either fails, stop and escalate to Abiraj/Sajeesan. (Applied today → blocked.)
- **RULE ENFORCED TODAY — no write, not even a test.** Did not attempt any `INSERT/UPDATE/DELETE` to "probe" write capability; capability was inferred from the tool surface only. Prevents the never-write rule being broken in the name of verification.
- **RULE (for authorised runs) — every ASIN gets exactly one segment.** Acceptance check: unclassified-ASIN count must be 0; use the DB's 8→6 mapping so HLL/LHL are covered.
- **RULE (for authorised runs) — benchmark top 30, else top 10, else flag.** ≥30 sellers → top 30; <30 → top 10; <10 → flag "benchmark cannot be calculated" (escalation), never invent a threshold.
- **RULE (for authorised runs) — clean SKUs before rollup.** Exclude `''`/`'---'`; `UPPER()`; collapse suffix variants to base SKU.
- **RULE (for authorised runs) — flag kill-criteria, never act.** Mark a kill threshold as hit; never cut PPC, change price, delist, or stop-scale.
- **RULE (for authorised runs) — run the prompt exactly as given.** No improving/shortening/reinterpreting; if ambiguous, say so rather than guess. Report layout follows the documented spec; conflicts with a verbal description are surfaced, not silently resolved.

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Failure mode (LIVE, HIGH, OPEN) — over-scoped / write-capable connection.** Trigger: the MCP role can see all schemas and run any SQL. Detection: `list_schemas`/`information_schema.tables` returns more than the four tables; the SQL tool is "execute any SQL". Recovery: stop; Sajeesan re-scopes to a `SELECT`-only role on the four tables; re-run the check. Risk: HIGH (rule breach + possible accidental data change). **Detected and contained today; not yet recovered.**
- **Failure mode (HANDLED in rules) — building to the document would mis-segment ASINs.** HLL/LHL have no bucket in the doc. Recovery: use the DB's 8→6 grouping. Risk: MEDIUM.
- **Edge case (HANDLED in rules) — `conversion` mistaken for revenue.** It's an order count. Recovery: use `conversion/NULLIF(click,0)*100` for CVR only. Risk: MEDIUM.
- **Edge case (HANDLED in rules) — dirty SKUs inflate the benchmark.** Blank/`---`/case/suffix variants double-count. Recovery: filter + `UPPER()` + base-SKU rollup before ranking top-30. Risk: MEDIUM.
- **Edge case (AWARENESS) — bi-monthly live data read as a finished month.** Current period (15–28 Jun) is incomplete; reading it as a 30-day month gives misleading movement. Resolve cadence (Gap 3) first. Risk: MEDIUM.
- **Edge case (AWARENESS) — `ppc_performance.marketplace` (no underscore, lowercase)** vs `market_place` elsewhere; a copy-paste filter silently returns nothing. Risk: LOW.

---

## SECTION 7 · DECISIONS MADE TODAY

- **Decision: run the scope check first and stop on failure.** Alternatives: skip straight to a prompt because the MCP is "right there". Reason: the project rule makes the scope check mandatory and makes mis-scope a hard stop. Trade-off: zero report output today, but no rule breach and no risk to live data. Approved: project rules / abiraj.
- **Decision: infer write capability, do not test it.** Alternatives: run a harmless write to "prove" it. Reason: any write breaks the never-write rule; the tool description ("execute any SQL") is sufficient evidence. Trade-off: capability is shown by surface, not by demonstration — which is the correct trade-off here. Approved: abiraj.
- **Decision: treat the project as "read & show", not "build".** Reason: `analytics.ph_segment` already holds the finished segmentation; rebuilding would duplicate/conflict with the live source of truth. Trade-off: depends on the MD's canonical-segmentation decision before a report is trustworthy. Approved: pending MD.
- **Decision: surface the three document-vs-DB conflicts to the MD rather than silently pick one.** Reason: doc and live system genuinely disagree on grouping, cadence, names; silent choice risks two conflicting sources of truth. Trade-off: blocked on a human decision. Approved: abiraj.
- **Decision: do not run any of the four prompts today.** Reason: scope failed; prompt files not supplied; canonical-segmentation decision unresolved. Trade-off: analysis + scope verdict only. Approved: abiraj.

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule
Every UK Amazon FBM ASIN owned by a PH is classified monthly into a performance segment from three live signals — **Impressions, Clicks, Conversion (CVR)** — each rated HIGH/LOW against a **per-PH, per-category** benchmark (not a global average, because a Pendant Holder and a Cable Tie can't share an impression bar). Benchmark = **average of the top 30 sold ASINs** in that category over 30 days (top 10 if <30 sold), recalculated each cycle. Each segment has a fixed action plan; movement is tracked vs the immediately preceding period. The protocol **flags** problems and **never** takes commercial action.

### Operational Assumption
The segmentation engine already runs and lands in `analytics.ph_segment`. `traffic_data.ref_id` *is* the ASIN; `conversion` is an order **count**, not revenue; account comes from `order_transaction.ss_name`; PH ownership from `ph_segment.user_name` at latest `period_end`. The execution tool is assumed to be a **scoped, read-only** connection — an assumption that **failed verification today**.

### Reusable Logic / Formula
- **CVR:** `SUM(conversion)/NULLIF(SUM(click),0)*100`.
- **Benchmark per category:** rank ASINs by `SUM(quantity)` desc in window; top 30 (or 10 if <30); HIGH/LOW = mean of impression/click/CVR across that set.
- **8→6 segment map (live canonical):** HHH→Champions, HHL→Leaky Buckets, **HLH+HLL→Wallflowers**, LHH→Hidden Gems, **LHL+LLH→Niche Winners**, LLL→Dead Horses.
- **Pre-run scope check (reusable):** `list_schemas` + `information_schema.tables` count → must return only the allow-listed tables; the SQL tool must be `SELECT`-only. Any deviation = hard stop + escalate.

### Canonical Vocabulary
| Term | Meaning |
| :---- | :---- |
| PH | Portfolio Holder (`ph_segment.user_name`) |
| GPE | Growth Protection Engine — the protocol umbrella |
| configurator | a PH's per-category benchmark thresholds |
| segment code | 3-letter Hi/Lo on Impression·Click·Conversion (e.g. HHL) |
| Wallflowers / Niche Winners | the two DB names each covering two combos (HLH+HLL / LHL+LLH) |
| movement | this-period segment vs previous-period segment (Improved/Same/Declined/New) |
| `ref_id` | the ASIN, in both `traffic_data` and `ph_segment` (never `asin`) |
| `ss_name` | account marker in `order_transaction` → LEDSone UK / DCVoltage UK |
| mis-scoped connection | an MCP/DB role that exceeds its allow-list or read-only mandate |

### Cross-Project Applicability
- **Scope-check-before-use guardrail:** any read-only analytics MCP should be verified with a 2-call check (`list_schemas` + table count) before running real work, and a write should never be used to "test" write capability. Reusable for every MCP/DB integration in the company (CFIS, PPC, KMS, BLOS).
- **"Inspect before you build":** check whether a table already answers the requirement before constructing analytics — here it shrank a build into a read.
- **Document-vs-live conflict register:** when a spec and a live system disagree, log the conflicts and route to the owner instead of choosing silently.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES — benchmark, CVR, filters, kill-criteria, escalation, scope constants all in metadata + S3/S5/S8 |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES — 6 gaps, with owners and the one hard blocker marked |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES — **live MCP call outputs** (list_schemas + table count), requirement `.docx`, scope-rules doc; no commit (no build), stated plainly |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (1–9)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment
A developer with no context could, from this file alone:
- **WHAT** was done — ran the mandatory live scope check on the connected Postgres MCP; it FAILED (16 schemas / 542 tables vs an allow-list of 4; write-capable SQL exposed); stopped and escalated per the rule; also confirmed the segmentation already exists in `analytics.ph_segment` and logged three document-vs-DB conflicts.
- **WHAT** the rules are — read-only, four tables, run prompts exactly as given, flag-don't-act on kill-criteria, never write, never edit a repo, output a downloadable file for Abiraj to file under `evidence/monthly-reports/[YYYY-MM]/`.
- **WHAT** blocks progress — (HARD) the mis-scoped connection; (DECISION) the canonical-segmentation choice (grouping/cadence/names); (INPUT) the missing prompt skill files.
- **WHO** needs action — **Sajeesan** (re-scope the MCP to a SELECT-only role on the four tables, then re-check); **MD/Bietrick** (canonical segmentation; clarify the `growth_protection_engine` / `ph_action_board` schemas); **abiraj** (supply the exact prompt file; carry decisions back).
- **WHY** decisions were made — scope check is mandatory and mis-scope is a hard stop; write capability inferred not tested (never-write rule); read-and-show over rebuild; conflicts surfaced not guessed.
- **WHERE** things live — connected Postgres MCP (this chat); target data in `analytics.ph_segment` (+ `traffic_data`, `order_transaction`, `ppc_performance` in `public`); requirement `.docx`; report outputs eventually under `evidence/monthly-reports/[YYYY-MM]/`.
- **WHAT** to do next — Sajeesan re-scopes → re-run the 2-call scope check → on PASS, with the correct prompt file and the MD's segmentation decision, run read-only and produce the HTML report.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-06-23__abiraj__ph-asin__REQ-05-D01.md`
- [x] Metadata complete — includes `blos_keys_used` (NONE, justified) and `hardcoded_thresholds` (incl. scope constants)
- [x] Live scope-check evidence (schema list + table count) captured in Section 3
- [x] Field reference + data hygiene for the four allowed tables in Section 3
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written (WHAT/WHO/WHY/WHERE)
- [x] Evidence referenced (live MCP outputs + requirement `.docx` + scope-rules doc); no Git commit (no build), stated plainly
- [x] ✅ **VERDICT:** live scope check FAILED — mis-scoped on both counts (visibility + write); work stopped per rule
- [x] ✅ **FINDING:** segmentation already exists in `analytics.ph_segment` → read-and-show, not build
- [x] ✅ **FINDING:** three document-vs-database conflicts (grouping / cadence / names) logged for MD
- [x] ✅ **RULE FOLLOWED:** no prompt run, no report produced, nothing written, no repo touched
- [ ] ⚠️ **BLOCKER (HIGH):** Sajeesan to re-scope MCP to SELECT-only on the four tables, then re-run the scope check
- [ ] ⚠️ **OPEN (MD):** decide canonical segmentation — existing table vs document (grouping + cadence + names)
- [ ] ⚠️ **OPEN:** obtain the exact prompt skill file before any execution run
- [ ] ⚠️ **OPEN:** clarify `growth_protection_engine` (10 tables) + `ph_action_board` (1) relationship to this project

---
*DIGITWEB LK LTD — Daily Skill Increment System — v3.0 — June 2026*
