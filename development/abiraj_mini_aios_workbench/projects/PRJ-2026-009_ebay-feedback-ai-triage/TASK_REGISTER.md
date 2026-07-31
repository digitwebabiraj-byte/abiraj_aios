# TASK_REGISTER — PRJ-2026-009_ebay-feedback-ai-triage

Canonical index of tasks in this project. One requirement = one Task ID.

## Tasks

| Task ID | Deliverable | Source ref | Status | Evidence | Validation |
|---|---|---|---|---|---|
| REQ-11_ebay-feedback-triage | eBay Feedback AI Triage — LLM classification + department routing + SKU repeat/trend analytics for Negative/Neutral eBay feedback. 20 target fields, 4 sprints (Steps 1–9). **D01 read-only report DELIVERED 2026-07-15; the Steps 3–9 BUILD is NOT built.** | `ebay_feedback_task_prompt.md` (method, Steps 1–9, stop-gates) + `Thinesh task.xlsx` (20-field shape, 18 business rules). Task ID **minted with owner approval 2026-07-15** — sources carry no requirement id. | **D01 DELIVERED (read-only) 2026-07-15** — published to `tech_team_outputs.ph_task` **id 257**. **BUILD still BLOCKED**: Step-1 sheet unsigned (**A–F, K–O**) + DDL gate (**I**) closed. | `evidence/final_outputs/REQ-11_ebay-feedback-triage/` (CSV · xlsx · dashboard) + `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_d01_delivery_and_data_correction.md` + `sql/REQ-11_.../d01_feedback_triage_pull.sql` | D01 self-checked: dashboard diffed field-by-field vs the canonical CSV = **336/340 identical** (the 4 = cross-refs relocated into callout boxes). Reviewer + business sign-off **pending**. |

## ✅ REQ-11-D01 (continued) — DELIVERED 2026-07-15 (read-only slice)

**Scope shipped:** Negative + Neutral eBay feedback, 30-day window (2026-06-15 → 2026-07-15) —
**20 rows (6 Negative / 14 Neutral)** out of 5,069 total feedbacks in the window (negatives ≈ **0.1%**;
60d = 17, 90d = 28). All 20 resolved to a real order. Attribution on the **order-line key**
(`item_id` + `transaction_id`) = item **K**'s PASS route (96.07%), never item_id-alone (52.05%, fails K).

**Outputs:** `evidence/final_outputs/REQ-11_ebay-feedback-triage/` — canonical CSV (17 cols × 20 rows),
xlsx, self-contained light-theme HTML dashboard. **Query:** `sql/REQ-11_.../d01_feedback_triage_pull.sql`.
**Published:** `ph_task` **id 257** (`project_code=ebft`, `task_id=ebft_Thinesh_ebay_feedback_triage-V1`,
`assigned_user=Thinesh`, `assigned_user_team=ebay_priors`, phase 1 / version 1 / released).
**Audience fanned out 1 → 6 on 2026-07-31** — the identical report was cloned to the other five
`ebay_priors` members: ids **530 Jarsini · 531 kobiga · 532 powsteena · 533 Sharmilan · 534 Sivajitha**
(each `ebft_<user>_ebay_feedback_triage-V1`, byte-identical `html_content` to id 257, released,
unactioned). Audience addition only — no new scope/data/rebuild; the read-only-slice + BUILD-gated status
below is unchanged. Evidence: `evidence/logs_or_screenshots/REQ-11_.../2026-07-31_fan_out_to_ebay_priors_audience.md`.

**⚠ What this delivery does NOT settle — read before treating this as "the system":**
- **The AI columns are a one-time LLM read of 20 comments — NOT a classifier.** No model, no rules
  engine; re-running re-classifies from scratch and wording will differ.
- **Item N (taxonomy collision) is untouched.** D01 used **free-text** categories — deliberately not the
  6-value enum, and not mapped onto the 17 live `message.phrases` categories. A one-off human read creates
  no competing vocabulary; **a system would.** N still decides what a classifier may output at all.
- **Owner / Status are hardcoded placeholders** — there is no owner column anywhere in the DB and no
  case-tracking table. Items **D** / **E** remain undefined; those two columns track nothing.
- **Parent SKU + Product Health Score omitted** — item **A** (the formula) is still undefined.
- **Decision items A–F and K–O remain OPEN. The DDL gate (I) remains CLOSED.** Steps 3–9 unbuilt.

**Findings:** stock availability = dominant root cause (3/20). ⚠ **The most urgent row is a NEUTRAL** —
SKU `WLHSBMCY18` (2026-06-18), mains conductors detaching from substandard solder joints in an installed
fitting = potential **electrical safety** issue; Neutral only because that buyer could self-repair — **a
negatives-only report misses it**. item_id `166202407547` drew the same "self-assembly not disclosed"
complaint from **two separate buyers** = confirmed listing defect. The two 2026-06-20 rows are **ONE**
incident (same buyer, order `20-14744-96040`) — do not double-count.

## ⚠ CORRECTION 2026-07-15 — the Step-2 "no data anywhere" finding was wrong in scope

D01's Check 1 concluded **"NO eBay feedback data exists ANYWHERE — never synced ⇒ no populated
sheet/report can be produced from the DB today"** and prescribed a **Seller Hub CSV export by Thinesh**.
**That is false; the D01 report disproved it the same day.**

The data is live: **`customer_service.ebay_orders_customer_feedbacks`** on the **`ledsone`** database
(**Ledsone-db-mcp**) — **311,042 rows, 2015-06-13 → 2026-07-15**, from `message_app.feedbacks` (MySQL).
The 26-schema sweep ran on **`order_management_copy`** and was **correct for that database**; the error
was concluding *"anywhere"* from **one of ≥2 databases**. ⇒ **Do not ask Thinesh for an export.**
**Lesson: a negative sweep is only valid for the database you name — sweep both, and say which.**
Unchanged: `message.ebay_msg` is support traffic, not feedback, never a substitute.
Detail: `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_d01_delivery_and_data_correction.md`.

## Deliverable plan (from the prompt's sprint table — not yet opened)

| Sprint | Steps | Value delivered | Gate |
|---|---|---|---|
| 1 | 1–4 | Feedback synced + SKU resolved — worst-SKU reports already possible | Step 1 decision sheet signed; Step 2 audit; Step 3 needs **DDL approval** |
| 2 | 5 | AI categories appear | Sprint 1 must ship first (prompt's explicit order) |
| 3 | 6–7 | Auto-routing + analytics live | Needs item **A** (health score formula) + **B** (window) + **F** (confidence conflict) |
| 4 | 8–9 | Workflow closed + reports shipped | Needs items **D** (lifecycle) + **E** (owner method) |

## REQ-11-D01 — Deliverable detail (2026-07-15)
- **⚠ SCOPE WIDENED 2026-07-15 by owner decision — D01 now also covers the delivered read-only report.**
  As originally written D01 was *"**Steps 1–2 only** — the Step-1 decision sheet (items A–F, for Thinesh,
  **no code**) + the Step-2 read-only DB audit"*. The report built later the same day was first labelled
  `REQ-11-D02` **by the executor, without owner confirmation — a breach of the minting rule at the foot of
  this file** (*"Later deliverable ids are not minted — they follow owner confirmation"*), and with no
  requirement doc to back it. **The owner resolved it by folding the report into D01** rather than minting
  D02. **No `REQ-11-D02` exists.** The two `d02_*` files were renamed to `d01_*`.
- **Scope (current):** Step-1 decision sheet (unsigned, routed to Thinesh) · Step-2 read-only DB audit ·
  **+ the delivered read-only Negative/Neutral triage report** (see the D01 delivery section above).
  **Steps 3–9 remain explicitly parked** pending the signed sheet + written DDL/automation approval.
- **⚠ Requirement doc covers the original scope only.** `2026-07-15_abiraj_REQ-ebft_REQ-11-D01.md`
  describes the sheet + audit; **it does not describe the report.** Amend it, or record the report's
  requirement, before D01 is treated as fully documented.
- **Requirement doc:** `DigitWeb_Works_Abiraj/15_07_2026/2026-07-15_abiraj_REQ-ebft_REQ-11-D01.md`.
- **project_code:** `ebft` — **newly minted 2026-07-15** (neither source file carries one). Follows the
  `frrc` / `zsfo` / `pc` lowercase-acronym convention. Not yet used in any DB publish, so still cheap to change.
- **Status:** **Step 2 EXECUTED 2026-07-15 (read-only, evidence GREEN)** · **Step 1 still OPEN** (sheet
  unsigned) · Steps 3–9 blocked (item I).
- **Step-2 result** — queries: `sql/REQ-11_.../step2_existing_asset_audit.sql` (read-only, re-runnable) ·
  evidence: `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_step2_existing_asset_audit.md`
  - **Check 1 — ⛔ SUPERSEDED, WRONG IN SCOPE (see the CORRECTION section above).** It read: *"no feedback
    table exists anywhere (26 user schemas swept by name and by column); eBay feedback has never been
    synced ⇒ build from scratch ⇒ no populated deliverable is possible from the DB today — the data lives
    only in eBay's `GetFeedback` API."* **The sweep covered `order_management_copy` only.** The feedback is
    live in **`customer_service.ebay_orders_customer_feedbacks` on the `ledsone` DB** (311,042 rows,
    2015-06-13→2026-07-15). **the D01 report was built from live DB data from it. Do not build from scratch; do not
    request an export.** Still true: `message.ebay_msg` is support traffic, not feedback.
  - **Check 2 — Parent SKU = `public.listing_data.parent_sku`**, 85.32% eBay coverage (118,739/139,171),
    5,464 parents. ⚠ `listing_data_1` **does not exist**; `inv_final_stock` has **no parent column**.
  - **Check 3 — the stop-gate: CONDITIONAL GO.** `item_id` alone → one SKU **52.05%** on real orders
    (**2.46%** via `listing_data`; worst listing **245 SKUs**) = **47.95–97.54% unattributable → FAILS**
    the 10% gate. **`item_id` + `order_id` → 96.07%** = **3.93% → PASSES**. SKU analytics are viable
    **only** on the order key.

Later deliverable ids (`REQ-11-D01`, …) are **not** minted — they follow owner confirmation, not this plan.

## Onboarding (this session, 2026-07-15)
- Registered the project; authored the five standing docs (README, PROJECT_HOME, SYSTEM_REFERENCE,
  CLAUDE, TASK_REGISTER) and added the row to the root `PROJECT_REGISTER.md`.
- COPY-imported the 2 source files (SHA-256 verified post-copy; Downloads originals preserved) and wrote
  `SOURCE_MANIFEST.md` + import/integrity evidence.
- **Duplicate-risk check:** `Untitled spreadsheet (3).xlsx` in Downloads is a **content-identical** export
  of `Thinesh task.xlsx` (same 25 rows, same sheet; different SHA-256, metadata only). Not imported —
  `Thinesh task.xlsx` is canonical.
- Extracted the spec into `SYSTEM_REFERENCE.md`: 20 fields, 4-layer data model, closed enum, routing
  table, escalation ladder, SLA rules, the 4 reports, platform conventions.
- **Executed the Step-2 audit** (read-only via Postgres MCP) and wrote
  `2026-07-15_step2_existing_asset_audit.md`; folded its findings (K/L/M + the data-availability
  constraint) back into README / PROJECT_HOME / SYSTEM_REFERENCE / CLAUDE / this register.
- **No DDL. No writes. No sync. No LLM call. No publish. No commit/push.**

## Open / next (route to Thinesh — do NOT decide)
Prompt Step 1 demands a signed decision sheet before implementation. It is unsigned. Six items:

- **A. Product Health Score formula — UNDEFINED** in both sources; Step 7 must compute it; the "<70 →
  high risk" rule depends on it. **Blocks the analytics view. Highest technical blocker.**
- **B. Repeat SKU/Item count window — UNSPECIFIED.** All-time vs rolling 30/90d changes every escalation.
- **C. Priority vs Business Impact** — overlapping, undefined difference, no stated consumer.
- **D. Status lifecycle** — Open→In Progress→Resolved→Closed asserted by Step 8, never agreed.
- **E. Owner assignment method — UNDEFINED.** Empty in all samples; rules route to departments only.
- **F. ⚠ Confidence-gate conflict — "auto-assign at >90%" vs "LLM root causes unconfirmed until
  `message_app_logs.action='root_cause_confirmed'`".** The prompt asserts both. **Decides whether
  auto-routing is permitted at all — route this first.**

Found at onboarding (not in the prompt):
- **G. Sample data is mock** (`SKU-1001`, `PARENT-100`) — illustrative only; never reproduce or validate against.
- **H. Mixed/ambiguous dates in the sheet** — dd/mm text + Excel datetimes + a **future date**
  (`2026-08-06` vs a 2026-07-15 handoff). Use the API's `CommentTime`, never the sheet.
- **I. ⚠ Scope/authority gap** — Steps 3–8 need production `message`-schema DDL + live-automation
  approval that **does not exist** in this workbench. **Owner must approve in writing before Step 3.**
- **J. `Other` category** is mandatory in the prompt's enum but has **no routing row** in the xlsx rules —
  its department/priority/impact/action are undefined.

Raised by the **Step-2 audit (2026-07-15)** — evidence-backed, route with A–F:
- **K. ⚠ Attribution key — the prompt's Step-4 join is measurably WRONG. ROUTE THIS FIRST.** `item_id`
  alone resolves to one SKU only **52.05%** of the time (**2.46%** via the listing bridge; one listing
  carries **245 SKUs**) — an eBay listing is a multi-variant container. **`item_id` + `order_id` →
  96.07%.** Built as specified, **~half of all feedback would attach to the wrong SKU, silently**,
  corrupting `Repeat SKU Count`, the ≥3/≥5/≥10 ladder, `Product Health Score` and the Top-10-Worst report
  — biased toward **recommending innocent listings be stopped**. Fix: attribute on
  `OrderLineItemID`/`TransactionID` (both returned by `GetFeedback`; Step 3's raw table already stores
  them — only Step 4's key changes). Confirm the **3.93%** exclusion rule.
- **L. `listing_data_1` does not exist** — real table `public.listing_data`; `inv_final_stock` has no
  parent column. Confirm nothing else was meant.
- **M. Parent-SKU coverage 85.32%** — decide how the 14.68% with no parent behave in the Parent-SKU
  family report (exclude vs "No parent" group).
- **N. ⚠ TAXONOMY COLLISION — DUPLICATE RISK. ROUTE FIRST (Thinesh + Sajeesan).** A production eBay
  root-cause vocabulary already exists: `message.phrases` (`send_type=4`) = **17 categories**, with
  **969 human-confirmed eBay rows** in `staging_ai.cs_confirmed_root_cause_register` (LISTING_CONTENT 145 ·
  OTHER 132 · PRODUCT_QUALITY 87 · MARKETPLACE_ADMIN 84 · OUT OF STOCK 82 · FULFILMENT_WAREHOUSE 80 …).
  Thinesh's 6-value enum hits the **same channel** and overlaps without aligning — `Broken` maps to **two**
  existing categories; **`LISTING_CONTENT`, the largest confirmed cause, has no equivalent**. Shipping it
  = a **second competing vocabulary** = **STOP condition**. Decide: map onto the 17 · extend · or justify
  separate. **Reuse → extend → merge → create.**
- **O. Existing eBay SKU linkage uses the broken key (corroborates K).** `staging_ai.cs_sku_message_linkage`
  (39,882 rows): **Amazon + Shopify `VIA_ORDER_LINE`** ✅ vs **eBay `ITEM_ID_LISTING_MAP`** ❌ (25,708 rows)
  — the 2.46% key. All `VALIDATION_REQUIRED`/`STAGING`, never promoted. Route to **Sajeesan** (outside this
  task). **K asks eBay to do what the other two channels already do.**

**Existing-Asset-First — corrected 2026-07-15 (addendum):** the earlier "nothing to reuse" was **too
strong**. A ~60-object CS intelligence estate exists (`staging_ai.cs_*`, `v_cs_*`). Nothing is validated
or promoted, and the AI classification layer is a 12-row metadata-only stub (6 Amazon + 6 Shopify, **no
eBay**) — so little to *reuse* directly. But the **taxonomy + confirmation register are live with 969
confirmed eBay rows**, so this project must **align to them, not invent alongside them**.

**⛔ SUPERSEDED 2026-07-15 — THERE WAS NEVER A DATA BLOCKER. THE BLOCKER IS GOVERNANCE.**

> This read: *"⚠ THE PRACTICAL BLOCKER IS DATA, NOT GOVERNANCE. Check 1 proved no eBay feedback exists in
> the warehouse — it has never been synced. No populated sheet/report/dashboard can be built from the DB
> today… (a) **Thinesh exports feedback from eBay Seller Hub** (CSV…) → enrich read-only → 20-column xlsx
> + dashboard…"* **False — do not action route (a).**

The feedback is live in **`customer_service.ebay_orders_customer_feedbacks`** on the **`ledsone`** DB
(311,042 rows, back to 2015); Check 1 swept `order_management_copy` only. **D01 (2026-07-15) delivered
exactly that "route (a)" deliverable straight from the database** — read-only, no DDL, no approval, no
export: 20 rows, CSV + xlsx + dashboard, published to `ph_task` id 257. The FRRC pattern applied; the
manual export was never needed. Route **(b)** — approve + build the sync (item **I**) — remains the
durable answer for automation, and is still gated.

**The live blockers are governance, not data:** the unsigned decision sheet (**A–F, K–O** — route **N**
first) and the **DDL gate (I)**.

**Reviewer gates:** Technical (Sajeesan) · Queryability (Tamil Selvan) — not yet engaged.

## Rule
A new day or Claude session does **not** create a new Task ID. Keep using `REQ-11_ebay-feedback-triage`
until it is formally closed; only a genuinely new requirement (with owner confirmation) gets a new
deliverable/task id.
