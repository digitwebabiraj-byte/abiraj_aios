# Execution Prompt — eBay Feedback AI Triage System

> Copy each STEP block into your AI assistant / dev tool one at a time.
> Do **not** paste the whole document at once — each step has a stop-gate
> that must be cleared before the next one starts.

---

## CONTEXT BLOCK (paste this once, at the start of the session)

```
You are building an AI-powered eBay feedback triage system for our
e-commerce operation (Amazon / eBay / Shopify multi-channel, Postgres backend).

GOAL
Every Negative or Neutral eBay feedback comment is automatically:
  1. classified into a fixed category by an LLM
  2. routed to the responsible department with a priority
  3. tracked to closure with an owner and status
  4. aggregated into SKU-level repeat/trend analytics

EXISTING SYSTEM CONVENTIONS — follow these, do not invent new patterns:
- Message tables live in the `message` schema (message.ebay_msg,
  message.amz_msg, message.shopify_msg, message.msg_tag_etl)
- Store/account filters ALWAYS use `=`, never `LIKE`
- LLM-derived root causes are UNCONFIRMED until a matching row exists in
  message.message_app_logs with action = 'root_cause_confirmed'.
  Never surface an unconfirmed root cause as fact.
- LLM classifications always include an `Other` fallback bucket
- eBay listing bridge: item_id -> order_transaction.item_id

TARGET OUTPUT (20 fields)
Raw:       Date, Account, Item ID, Listing SKU, Parent SKU, Order ID,
           Feedback Type, Feedback Message
AI:        AI Category, AI Root Cause, AI Confidence %
Routing:   Department, Priority, Business Impact, Suggested Action, Owner
Analytics: Repeat SKU Count, Repeat Item Count, Product Health Score
Workflow:  Status

BUSINESS RULES
- Negative feedback  -> create urgent case immediately
- Neutral feedback   -> review within 48 hours
- Wrong Item         -> Warehouse    | High   | Critical | Audit picker & SKU
- Quality Issue      -> Supplier/QC  | High   | High     | Investigate supplier batch
- Shipping Issue     -> Logistics    | High   | High     | Review shipping settings
- Broken             -> Packaging    | Medium | Medium   | Improve packaging
- Missing Parts      -> Packing      | Medium | Medium   | Packing checklist
- Repeat SKU >= 3    -> investigate listing
- Repeat SKU >= 5    -> escalate to manager
- Repeat SKU >= 10   -> recommend stop listing
- Health Score < 70  -> high risk product
- AI Confidence > 90 -> auto-assign department

Acknowledge this context. Do not write any code yet.
```

---

## STEP 1 — Resolve the open spec questions

```
Before any implementation, list every ambiguity in the spec above that
would block or bias the build. For each one give:
  - the question
  - why it blocks
  - your recommended default
  - the cost of getting it wrong

Focus especially on: the Product Health Score formula (undefined), the
time window for Repeat SKU/Item counts (unspecified), the difference
between Priority and Business Impact, the Status lifecycle, how Owner is
assigned, and the conflict between "auto-assign at >90% confidence" and
our existing root-cause-confirmation rule.

Output a one-page decision sheet. Write no code.
```

**STOP-GATE:** get the decision sheet signed off by the task owner before Step 2. Every phase below depends on it.

---

## STEP 2 — Audit what already exists

```
Inspect the database. Do not assume; query it.

1. Does any feedback table already exist?
   SELECT table_schema, table_name FROM information_schema.tables
   WHERE table_name ILIKE '%feedback%';

2. Show me the actual columns of order_transaction, listing_data_1 and
   inv_final_stock. I need to know which table holds the Listing SKU ->
   Parent SKU relationship, and whether item_id -> order_id -> SKU
   resolution is reliable for eBay.

3. On a sample of recent eBay orders, what percentage of item_id values
   resolve to exactly one SKU? Report the multi-SKU and no-match rates.

Execute the queries and report real results. Then tell me whether we are
building a sync from scratch or extending something existing.
```

**STOP-GATE:** the multi-SKU / no-match rate determines the Phase-2 fallback rule. If >10% of feedback can't be attributed to a single SKU, the SKU analytics need rethinking before you build them.

---

## STEP 3 — Raw feedback table + eBay sync

```
Create the raw landing table `message.ebay_feedback`, modelled on the
conventions of message.ebay_msg.

Requirements:
- feedback_id (text, UNIQUE) is the sync upsert key — idempotent re-runs
- store: feedback_id, sub_source, ss_name, item_id, transaction_id,
  order_id, buyer_id, feedback_type, feedback_text, feedback_date,
  sync_status
- feedback_type is one of: Positive, Neutral, Negative
- No AI fields, no derived fields, no routing fields in this table.
  Raw data only.

Then write the sync job against eBay's GetFeedback API. Note the API
returns FeedbackID, CommentType, CommentText, CommentTime, ItemID,
TransactionID, OrderLineItemID and CommentingUser — it does NOT return
SKU or Parent SKU. Those are resolved in the next step.

Handle: pagination, per-account (sub_source) iteration, incremental sync
by date, and upsert-on-conflict.

Show me the DDL and the sync code. Run the DDL.
```

---

## STEP 4 — SKU enrichment

```
Write the enrichment step that resolves Listing SKU, Parent SKU and
Order ID for each feedback row.

- Join item_id -> order_transaction to get order_id and listing SKU
- Resolve Parent SKU using the table you identified in Step 2
- Apply the no-match / multi-SKU fallback rule decided in Step 1

Unattributable feedback is EXPECTED, not an error. It must not fail the
job, and it must be excluded from SKU-level analytics rather than
silently defaulting to a wrong SKU.

Report: total feedback rows, resolved, unresolved, and the reason
breakdown for unresolved.
```

---

## STEP 5 — AI classification

```
Build the classification layer in a SEPARATE table
`message.ebay_feedback_ai` with a FK to message.ebay_feedback.id, so
classification can be re-run without touching raw data.

Rules:
- Only classify rows where feedback_type IN ('Negative','Neutral').
  Positives never enter the pipeline.
- Category is a CLOSED enum. The LLM may not invent values:
  Quality Issue | Shipping Issue | Wrong Item | Broken | Missing Parts | Other
- Prompt must return strict JSON only, no prose, no markdown fences:
  {"category": "...", "root_cause": "...", "confidence": 0-100}
- Validate category against the enum on receipt. Anything unrecognised
  becomes Other with confidence 0. Never trust the model's output shape.
- Store the model name/version and classified_at on every row so results
  are reproducible and re-classification is auditable.

Then apply our existing confirmation convention: the AI root cause is
displayed as "LLM suggestion (not confirmed)" until a matching
root_cause_confirmed row exists in message.message_app_logs.

Show me the prompt, the validation code, and the DDL.
```

---

## STEP 6 — Routing rules

```
Build routing as a CONFIG TABLE, not hardcoded CASE statements — these
mappings will change and must be editable without a deploy.

CREATE TABLE message.feedback_routing (
  category         text PRIMARY KEY,
  department       text,
  priority         text,
  business_impact  text,
  suggested_action text
);

Seed it with the five mappings from the business rules in the context
block. Then implement the two overrides:
- Negative feedback -> urgent case created immediately regardless of category
- Neutral feedback  -> 48-hour review SLA

Auto-assign department only when AI Confidence > 90. Below that, the row
goes to a human review queue with department NULL.
```

---

## STEP 7 — Analytics view

```
Build `message.ebay_feedback_enriched` as a VIEW joining raw + AI +
routing, with these DERIVED (never stored) fields:

- repeat_sku_count  — COUNT(*) OVER (PARTITION BY listing_sku)
- repeat_item_count — COUNT(*) OVER (PARTITION BY item_id)
- product_health_score — using the formula agreed in Step 1
- escalation_level — from repeat_sku_count:
    >=10 'Recommend stop listing' / >=5 'Escalate to manager'
    />=3 'Investigate listing' / else NULL
- risk_flag — TRUE when product_health_score < 70

Scope the window to the interval agreed in Step 1.

Do NOT materialise repeat counts or health score as columns on the base
table — they go stale the moment new feedback arrives.
```

---

## STEP 8 — Workflow tracking

```
Add status and owner handling.

- status: Open -> In Progress -> Resolved -> Closed (use the lifecycle
  agreed in Step 1)
- owner: assignment method per Step 1
- Log EVERY status transition and owner change into the existing
  message.message_app_logs table. Do not create a new log table.
- SLA timers: Negative = due at creation, Neutral = due at +48h.
  Surface an is_overdue flag.
```

---

## STEP 9 — The four reports

```
Write and execute these four queries against the enriched view:

1. Complaint count by Listing SKU (descending)
2. Complaint count by Parent SKU — family-level product issues
3. Monthly trend — count by date_trunc('month', feedback_date), with
   month-over-month delta and % change
4. Top 10 worst SKUs by complaint count, with their category breakdown,
   health score and escalation level

Return real results, not just SQL. For each report, tell me what action
the data suggests.
```

---

## Delivery order

| Sprint | Steps | Value delivered |
|---|---|---|
| 1 | 1–4 | Feedback synced + SKU resolved — worst-SKU reports already possible |
| 2 | 5 | AI categories appear |
| 3 | 6–7 | Auto-routing + analytics live |
| 4 | 8–9 | Workflow closed + reports shipped |

Ship Sprint 1 before starting Sprint 2. It answers most of the business question on its own.

---

## Guardrails to repeat if the assistant drifts

```
- Execute every query. Never hand me SQL as a final answer.
- Store filters use = , never LIKE.
- Raw / AI / derived data stay in separate tables. No mixing.
- The LLM category enum is closed. Other is mandatory.
- Unconfirmed LLM root causes are never presented as fact.
- Derived metrics are views, not columns.
```
