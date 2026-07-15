# PROJECT_HOME — eBay Feedback AI Triage (Thinesh)

## Project ID
PRJ-2026-009_ebay-feedback-ai-triage

## Project Name
eBay Feedback AI Triage | LLM classification + department routing + SKU repeat/trend analytics for
Negative and Neutral eBay feedback (LEDsONE analytics platform)

## Purpose
Turn every **Negative or Neutral eBay feedback comment** into a tracked, owned, actionable case:
classified into a fixed category by an LLM, routed to the responsible department with a priority and a
suggested action, tracked to closure with an owner and status, and aggregated into SKU-level repeat and
trend analytics so recurring product problems surface before they damage account health.

**This project is NOT like PRJ-2026-004 → PRJ-2026-008.** Those were read-only reporting tasks. This one
is specified as a **build**: new tables in the production `message` schema, a live eBay `GetFeedback` API
sync job, an LLM classification layer, and workflow/SLA tracking. That scope is **BLOCKED pending written
approval** — see *Approved Scope* and *Known Risks / Open Items*.

## Business Question
For every Negative and Neutral eBay feedback comment — what is the complaint category, the likely root
cause, which department owns it, how urgent is it, is this SKU (or its parent family) generating repeat
complaints, and is the product now high-risk enough to investigate, escalate or stop listing?

Status: **TO BE CONFIRMED FROM SOURCE DOCUMENTS.** The spec's *shape* is confirmed from
`Thinesh task.xlsx` (20 target fields + 18 developer business rules) and `ebay_feedback_task_prompt.md`
(9-step build, sprint order, guardrails). But **six business rules are undefined by the prompt's own
admission** (Step 1) and no decision sheet has been signed. See *Known Risks / Open Items*.

## Owner and Reviewers
- Owner / Developer: **Abiraj**
- Requester / report owner persona: **Thinesh** + the Warehouse / Supplier-QC / Logistics / Packaging /
  Packing departments
- Coordinator: Varmen
- Technical Reviewer: **Sajeesan** — not yet engaged
- Queryability Reviewer: **Tamil Selvan** — not yet engaged
- Business Validator: **Thinesh** (owns the six undefined rules + the confidence/confirmation conflict)
  — **sign-off pending; this is the Step-1 stop-gate**

## Original Requirement
- **REQ-11 (2026-07-15)** — Build the eBay feedback AI triage system per `ebay_feedback_task_prompt.md`,
  delivering the 20-field target output over four sprints:

  | Sprint | Steps | Value delivered |
  |---|---|---|
  | 1 | 1–4 | Feedback synced + SKU resolved — worst-SKU reports already possible |
  | 2 | 5 | AI categories appear |
  | 3 | 6–7 | Auto-routing + analytics live |
  | 4 | 8–9 | Workflow closed + reports shipped |

  Task ID `REQ-11_ebay-feedback-triage` was **minted with owner approval (2026-07-15)** — the source
  files carry no requirement id of their own. Sprint 1 is specified to ship before Sprint 2 starts.
- **project_code: `ebft`** — **newly minted 2026-07-15**, following the `frrc` / `zsfo` / `pc`
  lowercase-acronym convention. Neither source file carries a project code. Not yet used in any DB
  publish or commit, so still cheap to change if Thinesh or Varmen prefers another.
- **REQ-11-D01 (2026-07-15)** — first deliverable, scoped to **Steps 1–2 only**: the Step-1 decision
  sheet (items A–F, for Thinesh, no code) + the Step-2 read-only DB audit. **Steps 3–9 parked** behind
  the two gates. Planning doc:
  `DigitWeb_Works_Abiraj/15_07_2026/2026-07-15_abiraj_REQ-ebft_REQ-11-D01.md`. **Neither step executed yet.**

## Approved Scope (this onboarding session only)
- Maintain this project folder (`projects/PRJ-2026-009_ebay-feedback-ai-triage/`) only.
- COPY-only import of the two source files from `C:\Users\digit\Downloads\` (originals preserved).
- Author the five standing project docs + the source manifest + import evidence.
- **Nothing else is approved.** No DB touched, no DDL, no sync, no classifier, no code.

## Prohibited Scope — READ THIS BEFORE STEP 3
The prompt instructs "Run the DDL" (Step 3) and builds live automation (Steps 3–8). Under the workbench
root `CLAUDE.md` → *Never Touch Without Written Approval*, the following need **explicit written owner
approval that does not yet exist**:
- **Creating any object in the production `message` schema** — `message.ebay_feedback`,
  `message.ebay_feedback_ai`, `message.feedback_routing`, `message.ebay_feedback_enriched`. DDL against
  production is not covered by any existing approval in this workbench.
- **Live automation** — the eBay `GetFeedback` API sync job (scheduled, incremental, writing rows).
- **Writing to `message.message_app_logs`** (Step 8) — an existing production table.
- Deciding any of the six undefined business rules. They belong to **Thinesh**.
- Committing or pushing without explicit instruction.

**Read-only inspection (Step 2) is permitted** and is the correct next action.

## Systems and Sources
- **Production Postgres analytics DB** via the Postgres MCP — **read-only for now**. Store/account
  filters always use `=`, never `LIKE` (platform convention, restated by the prompt).
- Existing convention tables named by the prompt — **now verified live (Step 2, 2026-07-15)**:
  `message.ebay_msg`, `message.amz_msg`, `message.shopify_msg`, `message.msg_tag_etl`,
  `message.message_app_logs` — **all confirmed present**; `public.order_transaction`,
  `public.inv_final_stock` — confirmed. ⚠ **`listing_data_1` DOES NOT EXIST** — the real table is
  **`public.listing_data`** (open item L). ⚠ **`inv_final_stock` holds no parent column** — it is **not**
  the Parent-SKU source. **Parent SKU = `public.listing_data.parent_sku`** (85.32% eBay coverage).
- eBay listing bridge asserted by the prompt: `item_id` → `order_transaction.item_id`. ⚠ **Measured and
  found unsafe as an attribution key** — see open item K and the Run Snapshot below.
- External: eBay `GetFeedback` API — returns FeedbackID, CommentType, CommentText, CommentTime, ItemID,
  TransactionID, OrderLineItemID, CommentingUser. It does **not** return SKU or Parent SKU.
- Spec / acceptance source: `Thinesh task.xlsx` + `ebay_feedback_task_prompt.md`.

## Imported Assets
Under Task `REQ-11_ebay-feedback-triage` (COPY-only; Downloads originals preserved):
- `evidence/source_documents/REQ-11_.../ebay_feedback_task_prompt.md` — **single source of truth**:
  context block, Steps 1–9, stop-gates, sprint order, guardrails.
- `evidence/source_documents/REQ-11_.../Thinesh task.xlsx` — the requester's spec sheet: 20-column
  target shape, 6 illustrative sample rows, and the 18-row *Developer Business Rules* block.
- `evidence/source_documents/REQ-11_.../SOURCE_MANIFEST.md` — provenance + SHA-256.
- `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_import_checksum_evidence.md` — import evidence.
- `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_step2_existing_asset_audit.md` — **Step-2 audit
  (executed live, read-only)** — the three checks, the executed results, and the stop-gate verdict.

## Run Snapshot — Step 2 audit EXECUTED 2026-07-15 (read-only, no DDL, no writes)

| # | Question | Executed answer |
|---|---|---|
| 1 | Feedback table exists? | ✅ **YES — CORRECTED 2026-07-15. `customer_service.ebay_orders_customer_feedbacks` on the `ledsone` DB (Ledsone-db-mcp): 311,042 rows, 2015-06-13 → 2026-07-15, synced from `message_app.feedbacks` (MySQL).** ⚠ **SUPERSEDED ANSWER (audit trail):** *"NO — none, in any of the 26 user schemas… eBay customer feedback has never been synced… ⇒ Build from scratch."* That sweep covered **`order_management_copy`** (the warehouse) and was **correct for it** — but the estate has **≥2 databases** and the feedback lives in **`ledsone`**. Concluding *"anywhere"* from one DB was the error. **REQ-11-D01 built a populated report from this table the same day** (`ph_task` id 257) ⇒ **do NOT build from scratch, and do NOT request a Seller Hub export.** Still true: `message.ebay_msg` is support traffic (`ResponseToASQQuestion` 40,215 · `ContactTransactionPartner` 17,391 · `AskSellerQuestion` 10,103), messages ≠ feedback, never a substitute. |
| 2 | Parent SKU source? | **`public.listing_data.parent_sku`** — 139,171 eBay child rows, **118,739 (85.32%) populated**, 5,464 distinct parents. `mapped_sku` is dead on eBay (**31 rows**). |
| 3 | `item_id` → 1 SKU? | **FAILS.** Via `listing_data`: **2.46%** single-SKU / **97.54% multi** (worst listing = **245 SKUs**). Via real eBay orders (90d, 16,533 lines, 3,347 item_ids): **52.05%** single-SKU (max 42). |
| 3 | `item_id` + `order_id` → 1 SKU? | **96.07%** — only **3.93%** unattributable. |

**Stop-gate verdict: CONDITIONAL GO.** The prompt's gate is *">10% unattributable → rethink the SKU
analytics before building them."* On the prompt's stated `item_id` key: **47.95–97.54% unattributable —
FAILS.** On the order key: **3.93% — PASSES.** The SKU analytics are viable **only** when feedback is
attributed by **order line**, never by listing. Feasible today: eBay `GetFeedback` returns
`TransactionID` + `OrderLineItemID`, and Step 3's raw table already stores `transaction_id` / `order_id`
— **only Step 4's join key changes.** Full evidence:
`evidence/logs_or_screenshots/REQ-11_.../2026-07-15_step2_existing_asset_audit.md`.

## Source-of-Truth Locations
- **Build method / steps / guardrails:** `evidence/source_documents/REQ-11_.../ebay_feedback_task_prompt.md`.
- **Target field shape + business rules:** `evidence/source_documents/REQ-11_.../Thinesh task.xlsx`.
- **Locked rules / functional detail:** `SYSTEM_REFERENCE.md` (this project).
- **Data (system of record):** none yet — nothing has been built or pulled.

## Known Risks / Open Items (route to Thinesh — do NOT decide)
The prompt's own Step 1 requires a signed decision sheet before any implementation. **Six rules are
undefined**, and one is a direct contradiction:

- **A. Product Health Score formula — UNDEFINED.** The sheet shows a `Product Health Score` column
  (samples: 90/95) and rule "Health Score < 70 → high risk product", but **no formula exists anywhere in
  either source**. Step 7 must compute it and cannot. **This blocks the analytics view.**
- **B. Repeat SKU / Item count window — UNSPECIFIED.** "Repeat SKU >= 3 / >= 5 / >= 10" has no time
  bound. All-time vs rolling 30/90d changes every escalation. Step 7's window depends on it.
- **C. Priority vs Business Impact — overlapping, not distinguished.** The rules give both (e.g. Wrong
  Item → High / Critical) with no definition of how they differ or who acts on which.
- **D. Status lifecycle — asserted, not agreed.** Step 8 proposes Open → In Progress → Resolved → Closed
  "use the lifecycle agreed in Step 1". Nothing agreed. Samples only ever show `Open`.
- **E. Owner assignment method — UNDEFINED.** The `Owner` column is **empty in all 6 sample rows**. The
  rules route to a *department*, never to a person. Step 8 needs the method.
- **F. ⚠ Direct rule conflict — "AI Confidence > 90 → auto-assign department" vs the platform's existing
  root-cause-confirmation convention** ("LLM-derived root causes are UNCONFIRMED until a matching
  `message.message_app_logs` row has `action = 'root_cause_confirmed'`; never surface an unconfirmed root
  cause as fact"). The prompt asserts both, then asks Step 1 to resolve it. **Auto-routing work to a
  department on an unconfirmed LLM guess is exactly what the convention forbids.** Thinesh must decide.

Additional risks found at onboarding (not in the prompt):
- **G. The sample data is mock, not real.** SKUs are `SKU-1001…SKU-1005`, parents `PARENT-100…104` —
  placeholders. The 6 rows are **illustrative only** and must never be reproduced as an answer or used to
  validate the build (FRRC precedent).
- **H. ⚠ Mixed/ambiguous date formats in the source sheet.** Column `Date` mixes `29/05/2026` (text,
  dd/mm) with Excel datetimes `2026-03-06` and `2026-08-06`. `2026-08-06` is **three weeks in the
  future** relative to the 2026-07-15 handoff, which means at least one value was parsed dd/mm as mm/dd.
  Any date logic built off this sheet inherits the ambiguity — take dates from the API, not the sheet.
- **I. Scope/authority gap.** Steps 3–8 require production DDL + live automation approval that does not
  exist. See *Prohibited Scope*.
- **J. `Other` category is mandatory but absent from the sheet.** The prompt's enum includes `Other`
  (fallback); the xlsx business rules list only the five real categories. Build to the prompt's enum.

Raised by the **Step-2 audit (2026-07-15)** — evidence-backed, route with A–F:
- **K. ⚠ Attribution key — the prompt's Step-4 join is measurably WRONG.** Step 4 says *"Join item_id →
  order_transaction to get order_id and listing SKU."* Live measurement: `item_id` alone resolves to a
  single SKU only **52.05%** of the time on real orders (**2.46%** via the listing bridge; one listing
  carries **245 SKUs**). An eBay listing is a **multi-variant container** — "which SKU did this buyer
  complain about?" is unanswerable from `item_id`. Keyed on `item_id` + `order_id`: **96.07%**.
  **Built as specified, ~half of all feedback would attach to the WRONG SKU, silently** — corrupting
  `Repeat SKU Count`, the ≥3/≥5/≥10 ladder, `Product Health Score` and the Top-10-Worst report, biased
  toward **recommending innocent listings be stopped** (the ≥10 rule). Confirm: attribute on
  `OrderLineItemID`/`TransactionID`, and confirm the **3.93%** residual exclusion rule.
- **L. `listing_data_1` does not exist.** The spec names a non-existent table. Real table:
  **`public.listing_data`**. `inv_final_stock` has **no parent column** and is not the Parent-SKU source.
  Confirm no other table was meant.
- **M. Parent-SKU coverage is 85.32%.** The remaining **14.68%** of eBay listings have no `parent_sku`.
  Decide how they behave in the Parent-SKU family report (exclude vs group as "No parent").
- **N. ⚠ TAXONOMY COLLISION — DUPLICATE RISK. A production root-cause vocabulary for eBay already
  exists.** `message.phrases` (`send_type = 4`) holds **17 canonical categories** (`LISTING_CONTENT`,
  `PRODUCT_QUALITY`, `FULFILMENT_WAREHOUSE`, `FULFILMENT_CARRIER`, `CUSTOMER_MISUSE`,
  `MARKETPLACE_ADMIN`, `OUT OF STOCK`, `RETURN`, `INVOICE`, `PRE_SALES_QUERY`, `EBAY_RECALL`,
  `TRANSFORMER_ISSUE`, `Charge Back`, `Delivery Issue`, `Wrong Address`, `DISCOUNT`, **`OTHER`**), and
  `staging_ai.cs_confirmed_root_cause_register` carries **969 human-confirmed eBay rows** against them
  (top: LISTING_CONTENT 145 · OTHER 132 · PRODUCT_QUALITY 87). Thinesh's proposed **6-value enum**
  (`Quality Issue`/`Shipping Issue`/`Wrong Item`/`Broken`/`Missing Parts`/`Other`) targets the **same
  channel** and overlaps without aligning — `Broken` maps to **two** existing categories at once, and
  `LISTING_CONTENT`, the **largest confirmed eBay cause**, has **no equivalent** in his enum. Building it
  as written creates a **second competing vocabulary** — a **duplicate-risk STOP condition** under the
  root `CLAUDE.md`. Decide (Thinesh + **Sajeesan**): map onto the existing 17 · extend them · or justify
  a separate feedback-only vocabulary. **Existing-Asset-First: reuse → extend → merge → create.**
- **O. The existing eBay SKU linkage already uses the broken key — corroborates K.**
  `staging_ai.cs_sku_message_linkage` (39,882 rows) resolves **Amazon + Shopify `VIA_ORDER_LINE`**
  (the correct key) but **eBay via `ITEM_ID_LISTING_MAP`** (25,708 rows) — the listing key measured here
  at **2.46%** single-SKU. Every row is `VALIDATION_REQUIRED` / `STAGING` (never validated or promoted),
  so the estate's own controls already flag it. **Item K therefore asks eBay to do what Amazon and
  Shopify already do.** Route the linkage concern to **Sajeesan** — it is outside this task, but this
  audit supplies the evidence for why it should not be promoted as-is.

**⚠ Consequence of K for the whole task (the headline):** because **no feedback data exists anywhere**
(item 1 above), *no* report, dashboard or populated Excel sheet can be produced from the warehouse today
— the data lives only inside eBay's `GetFeedback` API. Either the sync is approved and built (item I), or
Thinesh supplies a Seller Hub feedback **export**. **Any export must include the order / transaction id
per row** — an item-id-only export inherits the 48% mis-attribution in item K regardless of the source.

## Live Publish
**NONE.** Nothing built, nothing pulled, nothing published.

## Status
**REQ-11-D01 — Step 2 COMPLETE (executed, evidence GREEN) · Step 1 OPEN · Steps 3–9 BLOCKED.**
Project registered, sources imported and checksum-verified, governance docs authored, and the **Step-2
existing-asset audit executed live read-only** (3/3 checks, no DDL, no writes, no LLM call). What the
audit changes: the build is **from scratch** (no feedback data exists anywhere), the spec names a
**non-existent table** (L), and the specified **attribution key is wrong** (K) — a defect that would have
silently mis-attributed ~half of all feedback.

Still blocked. **Step 1** needs Thinesh's signed decision sheet (now **A–F + K, L, M** — nine items).
**Steps 3–9** additionally need written owner approval for production DDL + live automation (item I).
Not yet reviewed by Sajeesan (technical) or Tamil Selvan (queryability).

## One Next Action
Route the decision sheet — now **eleven items** — in this order:
1. **N (taxonomy collision)** — **Thinesh + Sajeesan.** A duplicate-risk stop condition, and it decides
   what the AI layer is even allowed to output. Everything downstream (routing, reports) keys off the
   category, so this outranks the rest.
2. **K (attribution key)** — evidence-backed; Amazon/Shopify already do it right, eBay doesn't.
3. **F** (confidence ⇄ confirmation conflict — decides whether auto-routing is permitted at all).
4. **A** (Health Score formula — without it Step 7 cannot be built).
**L**, **M** are cheap confirmations. **O** routes to **Sajeesan** as an estate concern outside this task.
In parallel, get **written approval for production `message`-schema DDL and the live sync job** (item I),
and engage Sajeesan + Tamil Selvan.

**✅ CORRECTED 2026-07-15 — there was never a data blocker.**

> **⚠ SUPERSEDED (audit trail).** This read: *"The practical blocker is data, not governance. No populated
> deliverable is possible from the warehouse — eBay feedback has never been synced and exists only in the
> `GetFeedback` API. Fastest route to a real sheet without any approval: **Thinesh exports feedback from
> eBay Seller Hub (CSV…)**."* **False — do not action it.**

The feedback is live in **`customer_service.ebay_orders_customer_feedbacks`** on the **`ledsone`** database
(311,042 rows, back to 2015). The earlier sweep covered `order_management_copy` only. **REQ-11-D01
(2026-07-15) delivered exactly the "fastest route" deliverable — read-only, no DDL, no approval, no export
— straight from the DB**: 20 rows (6 Negative / 14 Neutral), 30-day window, CSV + xlsx + dashboard,
published to `ph_task` **id 257**. The FRRC pattern applied; Thinesh's manual export was never needed.

**The remaining blocker is governance, not data.** The Step-3 sync + Steps 3–9 BUILD still need written
DDL/automation approval (item **I**), and the decision sheet (**A–F, K–O**) is still unsigned — item **N**
(taxonomy collision) first, since it decides what a classifier may output at all.
