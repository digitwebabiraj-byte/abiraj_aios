# SYSTEM_REFERENCE — eBay Feedback AI Triage (PRJ-2026-009)

Complete functional detail of what this system is specified to do, derived **only** from the two
canonical sources (`ebay_feedback_task_prompt.md`, `Thinesh task.xlsx`). Written for a leader or a new
engineer.

> **Status caveat — read first.** Nothing in this document is built. Several rules below are marked
> **UNDEFINED** or **CONFLICT**: they are recorded exactly as the sources leave them, and are **not**
> resolved here. Resolving them is Thinesh's Step-1 decision, not the executor's.

---

## 1. What the system does

Every eBay feedback comment of type **Negative** or **Neutral** is:

1. **classified** into a fixed category by an LLM,
2. **routed** to the responsible department with a priority and a suggested action,
3. **tracked** to closure with an owner and status,
4. **aggregated** into SKU-level repeat and trend analytics.

**Positive feedback never enters the pipeline** (Step 5).

## 2. Population & scope

- Channel: **eBay only** (the platform is multi-channel Amazon / eBay / Shopify; this is the eBay leg).
- Accounts seen in the sample sheet: `Huttenlampen`, `ELECTRICALSONE`, `SUNSONE`, `Coventry` —
  per-account (`sub_source`) iteration is required by the sync (Step 3).
- Feedback types: `Positive` | `Neutral` | `Negative`. Only the latter two are processed.

## 3. Target output — the 20 fields

| Group | Fields |
|---|---|
| **Raw** (8) | Date · Account · Item ID · Listing SKU · Parent SKU · Order ID · Feedback Type · Feedback Message |
| **AI** (3) | AI Category · AI Root Cause · AI Confidence % |
| **Routing** (5) | Department · Priority · Business Impact · Suggested Action · Owner |
| **Analytics** (3) | Repeat SKU Count · Repeat Item Count · Product Health Score |
| **Workflow** (1) | Status |

## 4. Data model — four layers, never mixed

The prompt's central architectural rule: **raw / AI / config / derived data stay in separate objects.**

| Object | Layer | Holds | Rule |
|---|---|---|---|
| `message.ebay_feedback` | Raw landing | feedback_id (UNIQUE, upsert key) · sub_source · ss_name · item_id · transaction_id · order_id · buyer_id · feedback_type · feedback_text · feedback_date · sync_status | **Raw only.** No AI, derived or routing fields. Modelled on `message.ebay_msg` conventions. |
| `message.ebay_feedback_ai` | AI | FK → `message.ebay_feedback.id` · category · root_cause · confidence · model name/version · classified_at | Separate table so classification can be **re-run without touching raw data**. Model version stored so results are reproducible and re-classification auditable. |
| `message.feedback_routing` | Config | category (PK) · department · priority · business_impact · suggested_action | A **config table, not hardcoded CASE statements** — mappings change and must be editable without a deploy. |
| `message.ebay_feedback_enriched` | Derived | VIEW joining raw + AI + routing | Derived metrics are **views, never columns** — they go stale the moment new feedback arrives. |

**Bridge — RESOLVED by the Step-2 audit, 2026-07-15 (executed).** The eBay API returns **no SKU** — SKU is
always resolved, never supplied.

- ⚠ **`item_id` is NOT a safe attribution key.** The prompt's Step 4 (*"Join item_id →
  order_transaction to get order_id and listing SKU"*) was measured against live data and **fails**: an
  eBay listing is a multi-variant container, so `item_id` alone resolves to a single SKU only **52.05%**
  of the time on real orders (**2.46%** via `listing_data`; worst listing = **245 SKUs**).
- ✅ **Attribute by ORDER LINE.** `item_id` + `order_id` → single SKU **96.07%** (3.93% residual).
  eBay `GetFeedback` returns **`TransactionID`** and **`OrderLineItemID`**, so this is available at
  source; Step 3's raw table already stores `transaction_id` / `order_id` — **only Step 4's join key
  changes.** (Open item K — Thinesh to confirm.)
- **Parent SKU = `public.listing_data.parent_sku`**, bridged `ref_id` = eBay `item_id`, filtered
  `which_channel = 2 AND wrong_sku = 0 AND is_parent = 0`. Coverage **85.32%** (118,739 / 139,171 eBay
  child rows; 5,464 distinct parents). The **14.68%** without a parent must degrade gracefully (item M).
- ⚠ **`listing_data_1` DOES NOT EXIST** (item L) — the real table is `public.listing_data`.
  **`inv_final_stock` has no parent column** and is not the Parent-SKU source.
- `mapped_sku` is effectively dead on eBay (**31 rows**) — the platform rule
  `COALESCE(NULLIF(mapped_sku,''), sku)` still applies but will almost always resolve to `sku`.
- **Unattributable feedback (the 3.93%)** keeps its category + department routing (which need no SKU) and
  is **excluded from all SKU-level analytics** — never defaulted to a wrong SKU.

**Data availability — ✅ CORRECTED 2026-07-15. The feedback table EXISTS.**
Source of truth: **`customer_service.ebay_orders_customer_feedbacks`** on the **`ledsone`** database
(**Ledsone-db-mcp** connector) — **311,042 rows, 2015-06-13 → 2026-07-15**, Positive/Neutral/Negative,
synced from `message_app.feedbacks` (MySQL). Columns: `id`, `buyer`, `rating_star`, `buyer_score`,
`comment`, `date`, `type`, `item_id`, `role`, `feedback_id`, `transaction_id`, `order_line_item_id`,
`price`, `sub_source`. Join → `order_management.order_item_info` on `item_id` **+** `transaction_id`
(the order-line key — item **K**'s PASS route), then `orders` / `sub_source`. Match rate is ~0% pre-2023,
82.2% in 2023 and **100% from 2024** — see `database/postgresql/schemas/customer_service/relationships.md`;
it does not bite a recent-window pull.

> **⚠ SUPERSEDED (audit trail).** This paragraph read: *"Data availability — the hard constraint. There is
> **no eBay feedback table anywhere** in the database (all 26 user schemas swept by name and by column).
> eBay feedback has **never been synced**… Every field in §3 therefore depends on data that must first
> arrive via the `GetFeedback` sync (Step 3, gated) or a Seller Hub **export**."*
> **False.** The sweep covered `order_management_copy`, not `ledsone`. **REQ-11-D01 (2026-07-15) built a
> populated report straight from this table** — no sync, no export, no DDL. Note `order_line_item_id` and
> `transaction_id` are **already columns on this table**, so item K's correct attribution key is available
> today. `message.ebay_msg` is still support traffic, still not a substitute.
> See `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_d01_delivery_and_data_correction.md`.

Fields in §3 that are **not** in this table (Parent SKU, Product Health Score, Owner, Status, the AI
columns) still depend on decisions **A/D/E** and the gated build — the data existing does not define them.

## 5. AI classification rules

- **Closed enum — the LLM may not invent values:**
  `Quality Issue` | `Shipping Issue` | `Wrong Item` | `Broken` | `Missing Parts` | `Other`
- `Other` is the **mandatory fallback bucket** (platform convention).
- Prompt returns **strict JSON only** — no prose, no markdown fences:
  `{"category": "...", "root_cause": "...", "confidence": 0-100}`
- **Validate the category against the enum on receipt.** Anything unrecognised → `Other`, confidence `0`.
  *Never trust the model's output shape.*
- **Unconfirmed root causes are never presented as fact.** An LLM root cause displays as
  *"LLM suggestion (not confirmed)"* until a matching row exists in `message.message_app_logs` with
  `action = 'root_cause_confirmed'`.

## 6. Routing rules (from the xlsx *Developer Business Rules* block)

| Category | Department | Priority | Business Impact | Suggested Action |
|---|---|---|---|---|
| Wrong Item | Warehouse | High | Critical | Audit picker & SKU |
| Quality Issue | Supplier/QC | High | High | Investigate supplier batch |
| Shipping Issue | Logistics | High | High | Review shipping settings |
| Broken | Packaging | Medium | Medium | Improve packaging |
| Missing Parts | Packing | Medium | Medium | Packing checklist |
| `Other` | — | — | — | **UNDEFINED** — enum requires it; the rules block omits it (open item J) |

**Overrides (apply regardless of category):**
- **Negative feedback** → create an urgent case **immediately**.
- **Neutral feedback** → review within **48 hours** (SLA due at +48h).

**Confidence gate:** auto-assign the department only when **AI Confidence > 90**. Below that the row goes
to a **human review queue with department NULL**.
> ⚠ **CONFLICT (open item F):** this gate contradicts §5's confirmation convention. Auto-assigning work on
> an unconfirmed LLM classification is what that convention forbids. **Unresolved — Thinesh decides.**

## 7. Escalation & analytics

Derived in the `message.ebay_feedback_enriched` view — **never materialised**:

| Field | Definition |
|---|---|
| `repeat_sku_count` | `COUNT(*) OVER (PARTITION BY listing_sku)` |
| `repeat_item_count` | `COUNT(*) OVER (PARTITION BY item_id)` |
| `product_health_score` | **UNDEFINED — no formula in either source** (open item A) |
| `escalation_level` | `>=10` → *Recommend stop listing* · `>=5` → *Escalate to manager* · `>=3` → *Investigate listing* · else NULL |
| `risk_flag` | TRUE when `product_health_score < 70` — depends on the undefined formula |

**Window:** "the interval agreed in Step 1" — **UNSPECIFIED** (open item B). Every escalation threshold
above is meaningless without it: all-time vs rolling 30/90d changes who gets escalated.

## 8. SKU attribution

- Join `item_id` → `order_transaction` for order_id + Listing SKU; resolve Parent SKU via the Step-2 table.
- **Unattributable feedback is EXPECTED, not an error.** It must not fail the job, and must be
  **excluded from SKU-level analytics rather than silently defaulting to a wrong SKU**.
- Report resolved / unresolved counts + the reason breakdown for unresolved.
- **Step-2 stop-gate:** if **>10%** of feedback can't be attributed to a single SKU, the SKU analytics
  need rethinking *before* they are built.

## 9. Workflow tracking

- **Status lifecycle:** `Open → In Progress → Resolved → Closed` — proposed by Step 8, **not agreed**
  (open item D). Sample rows only ever show `Open`.
- **Owner assignment:** **UNDEFINED** (open item E) — empty in all 6 sample rows; rules route to a
  *department*, never a person.
- **Logging:** every status transition and owner change logs into the **existing**
  `message.message_app_logs`. **Do not create a new log table.**
- **SLA timers:** Negative = due at creation · Neutral = due at +48h. Surface an `is_overdue` flag.

## 10. The four reports (Step 9)

1. Complaint count by **Listing SKU**, descending.
2. Complaint count by **Parent SKU** — family-level product issues.
3. **Monthly trend** — count by `date_trunc('month', feedback_date)`, with month-over-month delta and % change.
4. **Top 10 worst SKUs** by complaint count, with category breakdown, health score and escalation level.

Each report returns **real executed results** plus what action the data suggests — never SQL alone.

## 11. Platform conventions (do not re-invent)

- Message tables live in the **`message` schema**.
- Store/account filters **always use `=`, never `LIKE`**.
- LLM root causes are **UNCONFIRMED** until `message.message_app_logs.action = 'root_cause_confirmed'`.
- LLM classifications **always include an `Other` fallback**.
- eBay listing bridge: `item_id` → `order_transaction.item_id`.
- **Execute every query — never hand over SQL as the final answer.**

## 12. Delivery order

Sprint 1 (Steps 1–4) → Sprint 2 (Step 5) → Sprint 3 (Steps 6–7) → Sprint 4 (Steps 8–9).
**Ship Sprint 1 before starting Sprint 2** — it answers most of the business question on its own
(feedback synced + SKU resolved makes the worst-SKU reports possible without any AI).

## 13. Data-quality notes on the source sheet

- The 6 sample rows are **mock** — `SKU-1001…1005`, `PARENT-100…104` are placeholders. **Illustrative
  only; never reproduce them as an answer or validate against them.**
- The `Date` column **mixes formats**: text `29/05/2026` (dd/mm) alongside Excel datetimes `2026-03-06`
  and `2026-08-06`. `2026-08-06` post-dates the 2026-07-15 handoff by three weeks — at least one value
  was parsed dd/mm as mm/dd. **Take dates from the eBay API (`CommentTime`), never from this sheet.**
- Rows 6 and 7 share `SKU-1005` with `Repeat SKU Count = 2` — consistent, and the only place the repeat
  logic is demonstrated at all.
