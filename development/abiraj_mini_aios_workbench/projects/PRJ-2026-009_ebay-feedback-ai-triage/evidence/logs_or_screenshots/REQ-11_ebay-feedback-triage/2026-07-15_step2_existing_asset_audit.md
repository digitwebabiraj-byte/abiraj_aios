# Step-2 Existing-Asset Audit — REQ-11-D01 (EBFT)

> # ⛔ CHECK 1 OF THIS DOCUMENT IS WRONG — CORRECTED 2026-07-15 (same day)
>
> **Do not act on Check 1.** It concludes *"no feedback table exists anywhere… never been synced…
> build from scratch"*. **The feedback data exists:** `customer_service.ebay_orders_customer_feedbacks`
> on the **`ledsone`** database (Ledsone-db-mcp) — **311,042 rows, 2015-06-13 → 2026-07-15**, synced from
> `message_app.feedbacks` (MySQL). **REQ-11-D02 built a populated report from it the same day**
> (`ph_task` id 257).
>
> **Why:** the sweep below ran against **`order_management_copy`** and is **correct for that database** —
> there is no feedback table there. **This estate has ≥2 databases.** Concluding *"anywhere"* from one of
> them was the error. **A negative result is only ever valid for the database you actually queried.**
>
> **Checks 2 and 3 (Parent SKU source · `item_id` attribution) are UNAFFECTED and still stand** — and
> Check 3's finding is *reinforced*: the real feedback table already carries `transaction_id` and
> `order_line_item_id`, so item K's correct order-line key is available today.
>
> Full correction: `2026-07-15_d02_delivery_and_data_correction.md`.

**Date:** 2026-07-15 · **Task:** REQ-11_ebay-feedback-triage · **Deliverable:** REQ-11-D01 (Step 2 of 9)
**Method:** read-only queries executed live via the Postgres MCP `execute_sql`. **No DDL, no writes, no LLM call.**
**Database swept:** `order_management_copy` — **NOT** `ledsone` (this is the gap; see the banner above).
**Prompt rule honoured:** *"Inspect the database. Do not assume; query it."* — every statement below is an executed result.

---

## CHECK 1 — Does any feedback table already exist? **NO.** ⛔ **SUPERSEDED — see the banner. Answer is YES, in `ledsone`.**

```sql
SELECT table_schema, table_name, table_type FROM information_schema.tables
WHERE table_name ILIKE '%feedback%' ORDER BY table_schema, table_name;
```

**Result — 5 rows, none of them eBay feedback:**

| schema | table | type |
|---|---|---|
| staging_ai | cppc_pmax_action_learning_feedback_v1 | VIEW |
| staging_ai | cppc_pmax_staff_problem_feedback_v1 | BASE TABLE |
| staging_ai | pmax_capability_feedback_loop_20260707 | BASE TABLE |
| staging_ai | v_aios_governance_submission_feedback_v1 | VIEW |
| staging_ai | v_daily_task_supervisor_feedback | VIEW |

All five are PPC/PMax/AIOS-governance artifacts — **unrelated to eBay customer feedback.**

**`message` schema contents (executed):** `amz_msg` · `ebay_messages` · `ebay_msg` · `message_app_logs` ·
`messages_headers` · `msg_tag_etl` · `phrases` · `shopify_msg`. **No `ebay_feedback`.**
(The prompt's claim that message tables live in the `message` schema is **confirmed**.)

**Widened search** (`%ebay%`, `%review%`, `%rating%`, `%comment%`, `%fdbk%`) returned expense, returns,
message and governance tables only — **no feedback store anywhere in the database.**

**Is feedback hiding inside `message.ebay_msg`? NO.** Its `message_type` domain is entirely
message/Q&A traffic:

| message_type | rows |
|---|---|
| ResponseToASQQuestion | 40,215 |
| *(empty)* | 28,436 |
| ContactTransactionPartner | 17,391 |
| AskSellerQuestion | 10,103 |
| ContacteBayMemberViaAnonymousEmail | 914 |
| ContactEbayMember | 429 |
| ResponseToContacteBayMember | 413 |
| CustomCode | 74 |

eBay **messages** (buyer↔seller support threads, `GetMyMessages`) and eBay **feedback**
(Positive/Neutral/Negative transaction ratings, `GetFeedback`) are **different APIs and different data**.
`ebay_msg` is not a substitute and must never be used as one.

### ➡ CHECK 1 VERDICT
**Building a sync from scratch — not extending anything** (the prompt's own Step-2 question, answered).
**There is zero eBay feedback data in the warehouse.** No report, dashboard or Excel deliverable can be
populated from the DB until the Step-3 sync exists — and Step 3 is **blocked on written DDL/automation
approval** (open item I). Existing-Asset-First rule: nothing to reuse; creation would be justified —
**but authority is still missing, so nothing is created today.**

---

## CHECK 2 — Which table holds Listing SKU → Parent SKU? **`public.listing_data.parent_sku`.**

⚠ **The prompt named two wrong candidates:**
- **`listing_data_1` DOES NOT EXIST.** The real table is **`public.listing_data`**. (Executed
  `information_schema.tables` returned only `listing_data`, `inv_final_stock`, `order_transaction`.)
- **`inv_final_stock` is NOT the parent source** — its only SKU-ish column is `sku`. No parent column.

**`public.listing_data` — relevant columns (executed):** `ref_id` · `sku` · `mapped_sku` ·
**`parent_sku`** · `sys_mapped_sku` · `is_parent` · `which_channel` · `which_channel_name` ·
`which_channel_new` · `wrong_sku` · `channel`.

**eBay parent coverage (executed, `which_channel=2`, `wrong_sku=0`, `is_parent=0`):**

| metric | value |
|---|---|
| eBay child listing rows | 139,171 |
| rows with `parent_sku` populated | 118,739 |
| **% `parent_sku` populated** | **85.32%** |
| distinct parent SKUs | 5,464 |
| rows with `mapped_sku` populated | **31** (≈0.02% — matches the reference: "almost never populated" on eBay) |

### ➡ CHECK 2 VERDICT
**Parent SKU source = `public.listing_data.parent_sku`**, bridged by `ref_id` = eBay `item_id`,
filtered `which_channel = 2 AND wrong_sku = 0 AND is_parent = 0`. **Coverage 85.32%** — the remaining
**14.68%** have no parent and must degrade gracefully (the Parent-SKU analysis in Step 9 report #2 will
not cover them). `mapped_sku` is effectively dead on eBay (31 rows) — `COALESCE(NULLIF(mapped_sku,''), sku)`
still applies per the platform rule, but it will almost always resolve to `sku`.

---

## CHECK 3 — `item_id` → SKU resolution rate. **THE HEADLINE FINDING.**

The prompt's Step 4 instructs: *"Join item_id -> order_transaction to get order_id and listing SKU."*
**Measured against live data, keying on `item_id` fails.**

### 3a — via the listing bridge (`listing_data`, eBay, valid non-parent rows)

| metric | value |
|---|---|
| total eBay `item_id`s | 12,699 |
| resolve to **exactly one** SKU | 312 |
| **% single-SKU** | **2.46%** |
| **% multi-SKU** | **97.54%** |
| worst case | **245 SKUs on ONE listing** |

### 3b — via **real eBay orders** (`order_transaction`, `source_name='EBAY'`, last 90 days)

| metric | value |
|---|---|
| eBay order lines (90d) | 16,533 |
| distinct `item_id`s | 3,347 |
| `item_id` → exactly one SKU | 1,742 |
| **% single-SKU keyed on `item_id` alone** | **52.05%** ❌ |
| max SKUs on one `item_id` | 42 |
| distinct (`item_id`,`order_id`) pairs | 15,748 |
| **% single-SKU keyed on `item_id` + `order_id`** | **96.07%** ✅ |

### ➡ CHECK 3 VERDICT — the Step-2 stop-gate, applied

The prompt's gate: **">10% of feedback unattributable to a single SKU → the SKU analytics need
rethinking before you build them."**

| Attribution key | Unattributable | vs 10% gate |
|---|---|---|
| `item_id` via `listing_data` | **97.54%** | ❌ **FAILS catastrophically** |
| `item_id` via recent orders | **47.95%** | ❌ **FAILS** |
| **`item_id` + `order_id`** | **3.93%** | ✅ **PASSES** |

**The SKU analytics are viable — but ONLY if feedback is attributed via the ORDER, never via the listing.**
This is a **design-changing finding**, not a tuning detail:

- An eBay listing is a **multi-variant container** (up to 245 SKUs). "Which SKU did this buyer complain
  about?" is **unanswerable from `item_id`**; it is answered by **which order line they bought**.
- **This is feasible:** eBay's `GetFeedback` returns **`TransactionID`** and **`OrderLineItemID`**
  alongside `ItemID` — the exact order line. The prompt's Step 3 already stores `transaction_id` and
  `order_id`, so the raw table needs no change; **Step 4's join key does.**
- **Consequence if built as written:** keying on `item_id` would mis-attribute roughly **half** of all
  feedback (and up to 97% by listing) to the wrong SKU — silently. Every downstream number —
  `Repeat SKU Count`, the ≥3/≥5/≥10 escalation ladder, `Product Health Score`, the Top-10-Worst-SKU
  report — would be **wrong**, and wrong in the direction of **recommending that innocent listings be
  stopped** (rule: "Repeat SKU >= 10 → recommend stop listing").
- The prompt's own guardrail already anticipates the failure mode: *"Unattributable feedback ... must be
  excluded from SKU-level analytics rather than silently defaulting to a wrong SKU."* The **3.93%**
  residual under the order key is exactly that exclusion set.

**Recommended fallback rule (for Thinesh's Step-1 sheet — proposed, NOT decided):** attribute on
`OrderLineItemID`/`TransactionID` → `order_transaction` order line. Where the order line is absent or
still resolves to >1 SKU (**3.93%**), mark the row `SKU unattributable`, keep it in the raw feed and in
category/department routing (which need **no** SKU), and **exclude it from all SKU-level analytics**.

---

---

# ADDENDUM — Customer-Service estate sweep (2026-07-15, prompted by the owner)

**Why:** the owner asked "check customer service schema". The first pass searched for `%feedback%` by
table name and missed a **~60-object customer-service intelligence estate** in `staging_ai` (`cs_*`,
`v_cs_*`). This addendum is the correction. **It does not change Check 1's verdict (no feedback data
exists) — but it substantially changes the Existing-Asset-First picture and raises two new open items.**

There is **no schema literally named customer-service**; the estate lives in `staging_ai` under the
`cs_` prefix (+ `message_claude_reply.amz_customer_case`, `public.customer_info`,
`validation.cs_prevention_action_validation_runs`).

## N. ⚠ TAXONOMY COLLISION — a production root-cause vocabulary for eBay already exists (DUPLICATE RISK)

**`message.phrases` where `send_type = 4` is the canonical root-cause taxonomy — 17 categories:**

`Charge Back` · `CUSTOMER_MISUSE` · `Delivery Issue` · `DISCOUNT` · `EBAY_RECALL` ·
`FULFILMENT_CARRIER` · `FULFILMENT_WAREHOUSE` · `INVOICE` · `LISTING_CONTENT` · `MARKETPLACE_ADMIN` ·
**`OTHER`** · `OUT OF STOCK` · `PRE_SALES_QUERY` · `PRODUCT_QUALITY` · `RETURN` · `TRANSFORMER_ISSUE` ·
`Wrong Address`

**It is not theoretical — `staging_ai.cs_confirmed_root_cause_register` holds 1,266 rows, of which
969 are eBay, human-confirmed** (executed):

| root_cause | confirmed eBay rows |
|---|---|
| LISTING_CONTENT | 145 |
| OTHER | 132 |
| PRODUCT_QUALITY | 87 |
| MARKETPLACE_ADMIN | 84 |
| OUT OF STOCK | 82 |
| FULFILMENT_WAREHOUSE | 80 |
| CUSTOMER_MISUSE | 71 |
| FULFILMENT_CARRIER | 71 |
| RETURN | 63 |
| INVOICE | 47 |
| PRE_SALES_QUERY | 41 |
| Delivery Issue | 24 · Charge Back 20 · Wrong Address 10 · EBAY_RECALL 5 · DISCOUNT 2 |

**The collision.** Thinesh's spec proposes a **new 6-value enum** — `Quality Issue` / `Shipping Issue` /
`Wrong Item` / `Broken` / `Missing Parts` / `Other` — for the **same eBay channel** that already has a
17-value confirmed vocabulary. They overlap but do not align:

| Thinesh's proposed value | Plausibly already exists as |
|---|---|
| Quality Issue | `PRODUCT_QUALITY` |
| Shipping Issue | `FULFILMENT_CARRIER` / `Delivery Issue` |
| Wrong Item | `FULFILMENT_WAREHOUSE` (picking error) |
| Broken | `PRODUCT_QUALITY` **or** `FULFILMENT_CARRIER` (damaged in transit) — **ambiguous** |
| Missing Parts | `FULFILMENT_WAREHOUSE` (packing error) |
| Other | `OTHER` ✅ exact |
| *(no equivalent)* | `CUSTOMER_MISUSE`, `LISTING_CONTENT`, `MARKETPLACE_ADMIN`, `OUT OF STOCK`, `RETURN`, `INVOICE`, `PRE_SALES_QUERY`, `EBAY_RECALL`, `TRANSFORMER_ISSUE`, `Charge Back`, `Wrong Address`, `DISCOUNT` |

Building the spec as written creates a **second, competing root-cause vocabulary on the same channel** —
a **duplicate-risk STOP condition** under the workbench root `CLAUDE.md`. Note `LISTING_CONTENT` (the
single largest confirmed eBay cause, 145) has **no equivalent** in Thinesh's enum, and `Broken` maps to
two existing categories at once.

**Decide (Thinesh + Sajeesan — do NOT decide here):** (a) map feedback categories onto the existing
17-value taxonomy; (b) extend that taxonomy with any genuinely new feedback-only values; or (c) justify a
separate feedback-only vocabulary and accept two vocabularies. **Existing-Asset-First order applies:
reuse → extend → merge (with approval) → create only when uniqueness is proven.**

**Data-quality note (informational):** the confirmed register is not perfectly clean — casing variants
(`OUT OF STOCK` vs `Out of stock`) and free-text leakage into `root_cause` (e.g. *"send the replacement
with the new order"*, a Royal Mail tracking number). Any mapping must handle these.

## O. ⚠ The existing eBay SKU linkage uses the method this audit just disproved — CORROBORATES K

`staging_ai.cs_sku_message_linkage` (39,882 rows) already solves "which SKU is this customer contact
about?" — **and it resolves eBay the wrong way** (executed):

| platform | link_type | resolution_method | rows | with resolved_sku |
|---|---|---|---|---|
| **EBAY** | EBAY_ITEM_ID | **`ITEM_ID_LISTING_MAP`** | **25,708** | 25,708 |
| AMAZON | ORDER_ID | **`VIA_ORDER_LINE`** | 5,549 | 5,549 |
| AMAZON | ASIN | `VIA_ORDER_LINE` | 5,335 | 5,335 |
| EBAY | EBAY_ITEM_ID | `UNRESOLVED` | 1,588 | 0 |
| SHOPIFY | ORDER_ID | `VIA_ORDER_LINE` | 1,539 | 1,539 |
| SHOPIFY | ORDER_ID | `UNRESOLVED` | 73 | 0 |
| AMAZON | ASIN | `DIRECT_ASIN_MAP` | 72 | 72 |
| AMAZON | ORDER_ID | `UNRESOLVED` | 16 | 0 |

**Amazon and Shopify resolve `VIA_ORDER_LINE` — the correct key. eBay alone resolves via
`ITEM_ID_LISTING_MAP` — the listing key this audit measured at 2.46% single-SKU** (Check 3a). All 25,708
eBay rows carry a `resolved_sku` that, on a multi-variant listing (up to 245 SKUs), cannot be
distinguished from an arbitrary pick.

**Mitigating context — this is staging, not truth:** every row is `resolution_status =
'VALIDATION_REQUIRED'` and `promotion_status = 'STAGING'`. The estate has **not** been validated or
promoted, and `cs_issue_classification_staging` is a 12-row category-level summary (6 Amazon + 6 Shopify,
**no eBay**, `confidence_score = 'METADATA_ONLY'`, `recommended_action` NULL) — i.e. **the AI
classification layer Thinesh wants does NOT exist in working form.** So there is little to *reuse*
directly, but a great deal to *align with*.

**Route to Sajeesan (outside this task's scope, but he should know):** the eBay `ITEM_ID_LISTING_MAP`
resolution is unvalidated and, per this audit's measurements, unsound for multi-variant listings.
It is flagged `VALIDATION_REQUIRED`, so the estate's own controls already say so — this audit supplies
the evidence for why it should not be promoted as-is.

## What the addendum changes

- **Check 1 verdict — UNCHANGED.** Still **no eBay feedback data anywhere**; no `%feedback%` column in
  any `cs_*` object. The CS estate is built on **messages**, not feedback. The sheet still cannot be
  populated from the DB.
- **Check 3 / item K — STRENGTHENED.** The company's own linkage table independently reproduces the
  fault: eBay by listing, Amazon/Shopify by order line. The fix (order-line keying) is already the
  house pattern on the other two channels — **item K asks eBay to do what Amazon and Shopify already do.**
- **NEW: item N (taxonomy collision / duplicate risk)** and **item O (unvalidated eBay linkage)**.
- **Existing-Asset-First — corrected finding:** "nothing to reuse" was **too strong**. Nothing is
  *promoted* or *validated*, and the AI layer isn't working — but the **root-cause taxonomy
  (`message.phrases` send_type 4) and the confirmation register are live and carry 969 confirmed eBay
  rows.** The project must **align to them**, not invent alongside them.

---

## Summary — what today's audit establishes

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Feedback table exists? | **No — none, anywhere** | Sync-from-scratch (Step 3) — **blocked on approval**. **No data exists to populate any report today.** |
| 2 | Parent SKU source? | **`listing_data.parent_sku`** (85.32% eBay coverage) | Prompt's `listing_data_1` **doesn't exist**; `inv_final_stock` **has no parent column** |
| 3 | `item_id` → 1 SKU? | **52.05%** (2.46% by listing) | ❌ **Gate FAILED** on the prompt's key |
| 3 | `item_id`+`order_id` → 1 SKU? | **96.07%** | ✅ **Gate PASSED** — attribute by **order**, not listing |

**Step-2 stop-gate outcome: CONDITIONAL GO.** The SKU analytics are buildable **only** on the order key.
On the prompt's stated `item_id` key they are **not** buildable and must not be attempted.

**New open items raised by this audit (route to Thinesh with A–F):**
- **K. Attribution key — the prompt's Step-4 join is wrong.** Must key on `OrderLineItemID`/`TransactionID`,
  not `item_id`. Confirm, and confirm the 3.93% exclusion rule.
- **L. `listing_data_1` does not exist** — the spec names a non-existent table. Substitute
  `public.listing_data`; confirm no other table was meant.
- **M. Parent-SKU coverage is 85.32%** — decide how the 14.68% with no parent behave in the Parent-SKU
  family report (exclude vs group as "No parent").

**Unchanged:** Steps 3–9 remain blocked (item I — no DDL/automation approval; Step-1 sheet unsigned).
Nothing was created, written or published. No commit, no push.
