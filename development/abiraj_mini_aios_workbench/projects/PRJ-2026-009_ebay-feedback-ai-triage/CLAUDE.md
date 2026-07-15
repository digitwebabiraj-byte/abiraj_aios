# CLAUDE.md — PRJ-2026-009_ebay-feedback-ai-triage

Inherits all rules from the workbench root `CLAUDE.md` and `START_HERE.md`
(`development/abiraj_mini_aios_workbench/`). Project-specific rules below.

## Scope
- Write only inside `projects/PRJ-2026-009_ebay-feedback-ai-triage/`.
- The production Postgres analytics DB (via the Postgres MCP) is **READ-ONLY** in this project **until
  written owner approval exists** for the build (see *The DDL Gate*).
- Downloads artifacts (`Thinesh task.xlsx`, `ebay_feedback_task_prompt.md`) are the user's originals —
  read-only; the registered copies live in `evidence/source_documents/REQ-11_ebay-feedback-triage/`.

## Task ID Rule
- Active task: `REQ-11_ebay-feedback-triage`. **Minted with owner approval on 2026-07-15** because
  neither source file carries a requirement id of its own (unlike REQ-10, which came from Rebecca's
  tracker). Named after the deliverable, per the root naming rule.
- A new day or session does NOT mint a new Task ID — keep using `REQ-11_…` until it is formally closed.
- Deliverables get suffixes after owner confirmation (`REQ-11-D01`, `-D02`, …) — do not invent silently.
  The prompt's four sprints are the natural deliverable boundaries.

## ⚠ The DDL Gate — the defining rule of this project
Every prior project in this workbench (REQ-05 → REQ-10) was **read-only reporting**. This one is a
**build**, and Steps 3–8 of `ebay_feedback_task_prompt.md` instruct actions the root `CLAUDE.md` lists
under *Never Touch Without Written Approval*:

- **STOP** — do not create, alter or drop **any** object in the production `message` schema
  (`ebay_feedback`, `ebay_feedback_ai`, `feedback_routing`, `ebay_feedback_enriched`). Step 3 says "Run
  the DDL"; **that instruction does not carry approval**. The prompt is the *method*, not the authority.
- **STOP** — do not build, deploy or schedule the eBay `GetFeedback` API sync job. That is **live
  automation**.
- **STOP** — do not write to `message.message_app_logs` (Step 8). It is an existing production table.
- **STOP** — do not call an LLM over real customer feedback text until the classification design is
  approved.

A prompt authored for a generic dev tool does not override this workbench's approval rules. **Read-only
inspection (Step 2) is permitted** — inspection permission is not modification permission.

## Step-1 Stop-Gate Rule (do not decide — route to Thinesh)
The prompt's own Step 1 requires a **signed decision sheet before any implementation**. It is unsigned.
Six items are undefined or contradictory; **Thinesh is the Business Validator** and owns all six:

- **A. Product Health Score formula** — undefined in both sources, yet Step 7 must compute it and the
  rule "Health Score < 70 → high risk" depends on it. **Blocks the analytics view.**
- **B. Repeat SKU/Item window** — unspecified; all-time vs rolling 30/90d changes every escalation.
- **C. Priority vs Business Impact** — overlapping, never distinguished.
- **D. Status lifecycle** — asserted by Step 8, not agreed.
- **E. Owner assignment method** — undefined; empty in all samples; rules route to departments only.
- **F. Confidence-gate conflict** — "auto-assign at >90% confidence" vs the platform convention that LLM
  root causes are unconfirmed until `message_app_logs.action='root_cause_confirmed'`. **The most
  important item: it decides whether auto-routing is permitted at all.**

Do not invent business logic. Do not pick a "sensible default" and proceed.

## ⚠ Taxonomy Rule — DUPLICATE RISK (Step-2 addendum, 2026-07-15)
- **A production root-cause taxonomy for eBay already exists — do NOT invent a second one.**
  `message.phrases` (`send_type = 4`) = **17 canonical categories**; `staging_ai.cs_confirmed_root_cause_register`
  holds **969 human-confirmed eBay rows** against them (LISTING_CONTENT 145 · OTHER 132 · PRODUCT_QUALITY 87).
- Thinesh's 6-value enum targets the **same channel** and overlaps without aligning: `Broken` maps to
  **two** existing categories; **`LISTING_CONTENT` — the largest confirmed eBay cause — has no
  equivalent** in his enum. **Shipping the spec's enum as-is = a competing vocabulary = a STOP condition.**
- **Do not decide this.** Route to **Thinesh + Sajeesan** (item N). Existing-Asset-First order:
  **reuse → extend → merge (with approval) → create only when uniqueness is proven.**
- The CS estate (`staging_ai.cs_*`, ~60 objects) is **STAGING / VALIDATION_REQUIRED — not truth.** Do not
  treat it as production, and do not build on it without Sajeesan. But **do align to it.**

## Locked Convention Rule (from the sources — do not change without owner sign-off)
- **Layer separation:** raw / AI / config / derived live in separate objects. Never mix.
- **Closed enum (as specified — ⚠ but see the Taxonomy Rule above; item N may replace it):**
  `Quality Issue | Shipping Issue | Wrong Item | Broken | Missing Parts | Other`.
  `Other` is mandatory. Validate on receipt; unrecognised → `Other`, confidence 0.
- **Never trust the model's output shape** — strict JSON, validated, no fences.
- **Unconfirmed LLM root causes are never surfaced as fact.**
- **Derived metrics are views, never columns** — repeat counts and health score go stale instantly.
- **Store/account filters use `=`, never `LIKE`.**
- **Positives never enter the pipeline.**
- `feedback_id` is the UNIQUE upsert key — re-runs must be idempotent.
- Store model name/version + `classified_at` on every classified row.
- Log to the **existing** `message.message_app_logs` — never create a new log table.

## ⚠ Attribution Rule (evidence-backed — Step-2 audit, 2026-07-15)
- **NEVER attribute feedback to a SKU using `item_id` alone.** Measured live: `item_id` → one SKU only
  **52.05%** of the time on real eBay orders (**2.46%** via `listing_data`; worst listing = **245 SKUs**).
  An eBay listing is a multi-variant container. Building the prompt's Step-4 join as written would
  **silently mis-attribute ~half of all feedback**, corrupting every downstream number and biasing the
  ≥10 rule toward **stopping innocent listings**.
- **Attribute by ORDER LINE** — `OrderLineItemID` / `TransactionID` → `order_transaction`.
  `item_id` + `order_id` resolves to one SKU **96.07%** of the time. Feasible: `GetFeedback` returns both.
- The **3.93%** that still don't resolve are the exclusion set: keep them in raw + category/department
  routing, **exclude from all SKU-level analytics**, never default to a wrong SKU.
- **Parent SKU = `public.listing_data.parent_sku`** (`which_channel=2`, `wrong_sku=0`, `is_parent=0`) —
  **85.32%** coverage. ⚠ **`listing_data_1` does not exist**; **`inv_final_stock` has no parent column**.
- Stop and route to Thinesh (item K) before building on any other key.

## Data Availability Rule — ✅ CORRECTED 2026-07-15
- **The feedback data EXISTS. Use `customer_service.ebay_orders_customer_feedbacks` on the `ledsone`
  database (Ledsone-db-mcp connector).** 311,042 rows, 2015-06-13 → 2026-07-15, synced from
  `message_app.feedbacks` (MySQL). Join docs:
  `database/postgresql/schemas/customer_service/relationships.md`.
- > **⚠ SUPERSEDED RULE (audit trail).** This read: *"There is no eBay feedback data in the warehouse —
  > none, in any of the 26 user schemas… It has never been synced. No populated report/xlsx/dashboard can
  > be produced from the DB until either the Step-3 sync is approved and built, or Thinesh supplies a
  > Seller Hub export."* **False — REQ-11-D02 built one from live DB data on 2026-07-15.
  > Do NOT ask Thinesh for a Seller Hub export.**
- **⚠ THE TRAP THAT CAUSED IT — this estate has ≥2 databases. Always name the one you swept.**
  | Database | Connector | Holds |
  |---|---|---|
  | `ledsone` | **Ledsone-db-mcp** | **`customer_service` (the feedback)**, `staff`, `listings`, `order_management` |
  | `order_management_copy` @ `149.28.134.54:5435` | Postgres MCP / `temp_user` (psycopg2) | the warehouse; `tech_team_outputs.ph_task` |
  The 26-schema sweep was **right about `order_management_copy`** and wrong to say *"anywhere"*.
  **A negative result is only valid for the database you actually queried — sweep both, and say which.**
- **A populated read-only report needs no DDL, no sync and no approval.** The Step-3 sync (item **I**) is
  still unbuilt and still gated — but it is not a prerequisite for reporting.
- **`message.ebay_msg` is NOT feedback** — its `message_type` domain is support traffic
  (`AskSellerQuestion`, `ResponseToASQQuestion`, `ContactTransactionPartner`). Messages and feedback are
  different eBay APIs. **Never substitute it**, and never present it as feedback. *(unchanged, still true)*
- Any export used as a data source **must carry the order / transaction id per row** — an item-id-only
  export inherits the 48% mis-attribution above regardless of where it came from.

## Data-Quality / Flag Rule
- The xlsx's 6 sample rows are **mock** (`SKU-1001`, `PARENT-100`) — **illustrative only**. Never
  reproduce them as an answer; never validate the build against them.
- The sheet's `Date` column mixes dd/mm text with Excel datetimes and contains a **future date**
  (`2026-08-06` vs a 2026-07-15 handoff). Take dates from the API's `CommentTime`, never from the sheet.
- **Unattributable feedback is expected, not an error** — exclude it from SKU analytics; never default it
  to a wrong SKU; never let it fail the job.
- SQL is **never** the deliverable — execute it via the Postgres MCP and return real rows.

## Stop Conditions (in addition to workbench rules)
- Stop and route items **A–F** to **Thinesh** rather than deciding any of them.
- Stop before **any** DDL, sync, LLM call over real feedback, or write to production — see *The DDL Gate*.
- Stop if the Step-2 audit shows **>10% of feedback cannot be attributed to a single SKU** — the SKU
  analytics need rethinking before they are built (the prompt's own gate).
- Stop if a feedback table already exists — Existing-Asset-First: reuse / extend before creating.
- Stop if asked to hardcode the routing mappings instead of using the config table.
- Stop if asked to materialise repeat counts or health score as base-table columns.
- Stop if asked to start Sprint 2 before Sprint 1 has shipped.
- **Do not publish** to `tech_team_outputs.ph_task` and do not commit/push without explicit instruction.
