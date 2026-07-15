# PRJ-2026-009 — eBay Feedback AI Triage (Thinesh)

One-screen landing page. Canonical context is `PROJECT_HOME.md`; full functional detail is
`SYSTEM_REFERENCE.md`.

**What:** turn every **Negative or Neutral eBay feedback** comment into a tracked, owned case — LLM
**classified** into a closed category, **routed** to the responsible department with a priority and
suggested action, **tracked** to closure with an owner and status, and **aggregated** into SKU-level
repeat/trend analytics (worst SKUs, parent-family issues, monthly trend, escalation ladder).
**Task:** REQ-11_ebay-feedback-triage. **Dev:** Abiraj. **Business Validator:** Thinesh.

## ✅ Status — **REQ-11-D01 DELIVERED 2026-07-15** (read-only report, `ph_task` id 257) · Steps 3–9 BUILD still blocked

**What is done:** a populated read-only triage report — Negative + Neutral, 30-day window
(2026-06-15 → 07-15), **20 rows (6 Negative / 14 Neutral)** from live DB data, published to
`tech_team_outputs.ph_task` **id 257** (`project_code=ebft`, `assigned_user=Thinesh`, released).
CSV + xlsx + dashboard in `evidence/final_outputs/REQ-11_ebay-feedback-triage/`.

**What is NOT done:** the Steps 3–9 **BUILD** (production DDL, live `GetFeedback` sync, the LLM
classifier layer, case tracking). The report's AI columns are a **one-time LLM read of 20 comments —
not a classifier**. Decision items **A–F, K–O remain open**; the **DDL gate (I) remains closed**.
**Item N (taxonomy collision) is untouched** — the report used free-text categories, so it does not
create a competing vocabulary, but a *system* would. N must be decided before any classifier is built.

| Gate | What it blocks | Who clears it |
|---|---|---|
| **Step-1 decision sheet** (unsigned) — now **A–F + K, L, M** (nine items) | Steps 3–9. The prompt's own rule: signed sheet *before* any implementation | **Thinesh** |
| **The DDL gate** — item **I** | Steps 3–8: production `message`-schema DDL + the live eBay sync job. No written approval exists | **Owner** (Abiraj → Varmen) |

**This project is unlike REQ-05 → REQ-10.** Those were read-only reporting. This is a **build** —
new production tables, a live API sync, an LLM layer. The root `CLAUDE.md` puts all three under
*Never Touch Without Written Approval*. The prompt is the **method**, not the **authority**.

## ✅ CORRECTED 2026-07-15 — the feedback data EXISTS, in the `ledsone` database

> **⚠ SUPERSEDED (kept for the audit trail).** This section read: *"🔴 THE BIGGEST FACT: there is no eBay
> feedback data. Anywhere… eBay feedback has never been synced into the warehouse… No populated sheet,
> report or dashboard can be built from the database today… The data exists only inside eBay's
> `GetFeedback` API. Route 1: Thinesh exports feedback from eBay Seller Hub (CSV)."*
> **That was false.** REQ-11-D01 disproved it the same day by building a populated report from live DB
> data. **Do not act on it. Do not ask Thinesh for a Seller Hub export — it is not needed.**

| | |
|---|---|
| Table | **`customer_service.ebay_orders_customer_feedbacks`** |
| Database | **`ledsone`** — via the **Ledsone-db-mcp** connector |
| Rows | **311,042** · **2015-06-13 → 2026-07-15** · Positive / Neutral / Negative |
| Origin | `message_app.feedbacks` (MySQL) — i.e. it **has** been synced |
| Join docs | `database/postgresql/schemas/customer_service/relationships.md` (verified year-by-year match rates) |

**Why the audit concluded otherwise — the estate spans two databases and it swept one.**
The 26-schema sweep was **correct for `order_management_copy`** (the warehouse, `149.28.134.54:5435`,
which also holds `tech_team_outputs.ph_task`) — there genuinely is no feedback table there. The error was
concluding **"anywhere"** from **one database**.
⇒ **On this estate "swept everything" means nothing unless you name the database. Sweep both, and say
which connector produced a negative result.**

**Still true:** `message.ebay_msg` **is** support-message traffic (`AskSellerQuestion`,
`ResponseToASQQuestion`, `ContactTransactionPartner`) — a **different eBay API**, not feedback, never a
substitute.

⇒ **A populated read-only report needs no DDL, no sync, no approval — D01 shipped one on 2026-07-15.**
The Step-3 sync (item **I**) remains unbuilt and gated, but it was never a prerequisite for reporting.
Detail: `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_d01_delivery_and_data_correction.md`.

## 🔴 SECOND FACT: the spec's SKU attribution is measurably wrong (item K)

The prompt's Step 4 joins on `item_id`. An eBay listing is a **multi-variant container** — one listing
carries **245 SKUs**. Measured live:

| Attribution key | → exactly one SKU | vs the spec's own 10% gate |
|---|---|---|
| `item_id` via `listing_data` | **2.46%** | ❌ 97.54% unattributable |
| `item_id` via real orders (90d) | **52.05%** | ❌ 47.95% unattributable |
| **`item_id` + `order_id`** | **96.07%** | ✅ **3.93% — PASSES** |

**Built as written, ~half of all feedback attaches to the wrong SKU — silently** — corrupting repeat
counts, the escalation ladder, Health Score and the Top-10-Worst report, biased toward **stopping
listings that did nothing wrong** (the ≥10 rule). Fix: attribute by **order line**
(`OrderLineItemID`/`TransactionID`, both returned by `GetFeedback`). **Stop-gate verdict: CONDITIONAL GO
— SKU analytics are viable only on the order key.** Evidence:
`evidence/logs_or_screenshots/REQ-11_.../2026-07-15_step2_existing_asset_audit.md`.

Also: **`listing_data_1` does not exist** (it's `public.listing_data`, item L); Parent SKU =
`listing_data.parent_sku` at **85.32%** coverage (item M).

## 🔴 THIRD FACT: the category enum duplicates a live taxonomy (item N — duplicate risk)

**A production root-cause vocabulary for eBay already exists.** `message.phrases` (`send_type=4`) holds
**17 categories**, and `staging_ai.cs_confirmed_root_cause_register` carries **969 human-confirmed eBay
rows** against them — top causes **LISTING_CONTENT 145 · OTHER 132 · PRODUCT_QUALITY 87**.

Thinesh's proposed 6-value enum targets the **same channel** and overlaps without aligning: `Broken` maps
to **two** existing categories at once, and **`LISTING_CONTENT` — the single largest confirmed eBay cause —
has no equivalent in his enum at all.** Shipping it as written creates a **second competing vocabulary** —
a **duplicate-risk STOP condition** under the root `CLAUDE.md`. Decide: map onto the existing 17, extend
them, or justify a separate one. **Reuse → extend → merge → create.**

Related (item O): the company's own `cs_sku_message_linkage` resolves **Amazon + Shopify by order line**
(correct) but **eBay by listing** (`ITEM_ID_LISTING_MAP`, 25,708 rows) — independently reproducing the
fault in K. It's all `VALIDATION_REQUIRED`/`STAGING`, never promoted. **K asks eBay to do what Amazon and
Shopify already do.**

## The unresolved rules (route to Thinesh — do NOT decide)
- **A. Product Health Score formula — UNDEFINED.** Column exists, "<70 → high risk" rule exists, **no formula anywhere.** Blocks the analytics view.
- **B. Repeat SKU/Item window — UNSPECIFIED.** ">=3 / >=5 / >=10" with no time bound.
- **C. Priority vs Business Impact** — overlapping, never distinguished.
- **D. Status lifecycle** — asserted by Step 8, not agreed.
- **E. Owner assignment method — UNDEFINED.** Empty in every sample; rules route to departments, not people.
- **F. ⚠ Auto-assign at >90% confidence vs "LLM root causes are unconfirmed until `message_app_logs.action='root_cause_confirmed'`".** The prompt asserts both. **Decides whether auto-routing is allowed at all.**
- **K. ⚠ Attribution key must be the order line, not `item_id`** — evidence above. **Route first.**
- **L.** `listing_data_1` doesn't exist · **M.** Parent-SKU coverage is 85.32%, decide the 14.68%.

## Key files
| File | What |
|---|---|
| `PROJECT_HOME.md` | Governance: purpose, scope, prohibited scope, reviewers, status, open items A–J |
| `SYSTEM_REFERENCE.md` | Full functional detail: 20 fields, 4-layer data model, enum, routing, escalation, SLA, the 4 reports |
| `CLAUDE.md` | Project execution rules — **the DDL gate**, the Step-1 stop-gate, locked conventions |
| `TASK_REGISTER.md` | Tasks + the 4-sprint deliverable plan |
| `evidence/source_documents/REQ-11_.../ebay_feedback_task_prompt.md` | **Single source of truth** — context block, Steps 1–9, stop-gates, guardrails |
| `evidence/source_documents/REQ-11_.../Thinesh task.xlsx` | Requester's spec — 20-column shape, 18 business rules, 6 **mock** sample rows |
| `evidence/source_documents/REQ-11_.../SOURCE_MANIFEST.md` | Provenance + SHA-256 |
| `sql/REQ-11_.../step2_existing_asset_audit.sql` | **The Step-2 audit queries** — read-only, re-runnable, each with its 2026-07-15 result inline |
| `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_step2_existing_asset_audit.md` | **Step-2 audit (executed live)** — no feedback table exists · Parent-SKU source · the attribution measurements + stop-gate verdict |
| `evidence/logs_or_screenshots/REQ-11_.../2026-07-15_import_checksum_evidence.md` | Import + duplicate-risk evidence (2/2 SHA-256) |
| `DigitWeb_Works_Abiraj/15_07_2026/2026-07-15_abiraj_REQ-ebft_REQ-11-D01.md` | Daily requirement / planning doc (`project_code=ebft`) |

## Delivery order (prompt's own sprints)
**1** Steps 1–4 → feedback synced + SKU resolved (worst-SKU reports already possible, no AI needed) ·
**2** Step 5 → AI categories · **3** Steps 6–7 → routing + analytics · **4** Steps 8–9 → workflow + reports.
**Ship Sprint 1 before starting Sprint 2** — it answers most of the business question on its own.

## Rules
Read-only DB until the DDL gate clears. Raw / AI / config / derived stay in **separate objects**. The
category enum is **closed**; `Other` is mandatory; validate on receipt — never trust the model's output
shape. Unconfirmed LLM root causes are **never surfaced as fact**. Derived metrics are **views, not
columns**. Store filters use `=`, never `LIKE`. Positives never enter the pipeline. Unattributable
feedback is **expected** — exclude it from SKU analytics, never default it to a wrong SKU. The xlsx's
sample rows are **mock** — never reproduce them. Execute SQL; never hand over SQL as the answer. Items
A–F go to **Thinesh** — do not decide silently. Not published, not committed. See root `CLAUDE.md` + this
project's `CLAUDE.md`.
