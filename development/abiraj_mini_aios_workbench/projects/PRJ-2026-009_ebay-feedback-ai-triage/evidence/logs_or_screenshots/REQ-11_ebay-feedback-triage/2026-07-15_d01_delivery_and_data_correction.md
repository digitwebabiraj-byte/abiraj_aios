# REQ-11-D01 (continued) — delivery evidence + CORRECTION to the Step-2 data finding

**Date:** 2026-07-15 · **Developer:** Abiraj · **Mode:** read-only query + one guarded publish
**Status:** DELIVERED (read-only scope). No DDL, no sync, no writes to `message_app_logs`.

---

## 1. ⚠ CORRECTION — the Step-2 "no feedback data anywhere" finding was wrong in scope

`2026-07-15_step2_existing_asset_audit.md` (earlier the same day) concluded, and README /
PROJECT_HOME / SYSTEM_REFERENCE / CLAUDE / TASK_REGISTER / PROJECT_REGISTER all repeated:

> **NO eBay feedback data exists ANYWHERE** — 26 user schemas swept by table name *and* by
> column; it has **never been synced** ⇒ **no populated sheet/report can be produced from the
> DB today**; the data lives only in eBay's `GetFeedback` API.

**That is false.** The data exists and today's deliverable was built from it.

| | |
|---|---|
| **Table** | `customer_service.ebay_orders_customer_feedbacks` |
| **Database** | **`ledsone`** (Ledsone-db-mcp connector) |
| **Rows** | **311,042** |
| **Range** | **2015-06-13 → 2026-07-15** |
| **Types** | Positive / Neutral / Negative (3) |
| **Documented origin** | `message_app.feedbacks` (MySQL) — i.e. it **has** been synced |
| **Documented join** | `database/postgresql/schemas/customer_service/relationships.md` — includes a verified year-by-year match-rate table |

### Why the audit reached the wrong conclusion — and why it was not sloppy

**The estate spans at least two databases, and the audit swept one of them.**

| Database | Reached via | Holds |
|---|---|---|
| `order_management_copy` @ `149.28.134.54:5435` | Postgres MCP / `temp_user` | the warehouse; `tech_team_outputs.ph_task` |
| **`ledsone`** | **Ledsone-db-mcp** | **`customer_service`**, `staff`, `listings`, `order_management` |

The 26-schema sweep was **correct for `order_management_copy`** — there genuinely is no feedback
table there. The error was concluding *"anywhere"* from *one database*. The related claims stay
true: `message.ebay_msg` **is** support traffic, not feedback, and is not a substitute.

### What this changes

- **The project was never data-blocked.** The documented "fastest route" — *Thinesh exports
  feedback from eBay Seller Hub as CSV* — is **unnecessary**. Do not ask him to do it.
- The **DDL gate (item I) is unaffected**: a *sync* is still not built and Steps 3–9 still want
  production DDL. But a **populated read-only report needed neither**, which D01 proves.
- **Lesson for this workbench:** "swept everything" is meaningless without naming the database.
  Sweep **both**, and state which connector produced a negative result.

---

## 2. What D01 delivered

**Scope:** a narrow **read-only slice** — Negative + Neutral eBay feedback for the last 30 days.
Explicitly **not** the Steps 3–9 BUILD, and **not** the full 20-field spec.

- **Window:** 2026-06-15 → 2026-07-15 (relative, `CURRENT_DATE - INTERVAL '30 days'`)
- **Volume:** **20 feedbacks — 6 Negative, 14 Neutral** — out of **5,069** total in the window
  (5,049 Positive). Negatives run **~0.1%** of feedback. 60d = 17 negatives, 90d = 28.
- **Join integrity:** **all 20 rows resolved to a real order** — the pre-2023 caveat does not
  bite a 2026 window. Latest negative in the whole table is 2026-07-07 (no negatives in the
  final 8 days — the window is not clipping recent data).
- **Attribution:** keyed on `item_id` + `transaction_id` (the **order-line** key) — audit item
  **K**'s PASS route (96.07%), **not** the item_id-alone key that fails K's gate at 52.05%.

**Query:** `sql/REQ-11_ebay-feedback-triage/d01_feedback_triage_pull.sql` (read-only, re-runnable).

**Outputs** — `evidence/final_outputs/REQ-11_ebay-feedback-triage/`:

| File | What |
|---|---|
| `ebay_negative_feedback_triage_2026-07-15.csv` | first cut, Negative only (6 rows) — superseded |
| `ebay_negative_neutral_feedback_triage_2026-07-15.csv` | **canonical** — 17 columns × 20 rows |
| `ebay_negative_neutral_feedback_triage_2026-07-15.xlsx` | same data, formatted workbook |
| `ebay_feedback_triage_dashboard_2026-07-15.html` | self-contained light-theme dashboard |

**Published:** `tech_team_outputs.ph_task` **id 257** — `project_code=ebft`,
`task_id=ebft_Thinesh_ebay_feedback_triage-V1`, `assigned_user=Thinesh`,
`assigned_user_team=ebay_priors`, `team=Development`, `developer=Abiraj`,
phase 1 / version 1 / `released`. Guarded INSERT via `temp_user` (dry-run first, manual
duplicate-`task_id` guard, html length round-trip verified).

**Verification:** the dashboard was diffed field-by-field against the canonical CSV —
**336/340 values character-identical**; the 4 differences are cross-reference notes relocated
from `Suggested Action` prose into dedicated callout boxes (content preserved, nothing lost).

---

## 3. ⚠ What D01 did NOT settle — read before reusing this

- **Item N (taxonomy collision) is UNTOUCHED and still a STOP condition for the build.** The report's
  categories are **free-text**, deliberately *not* Thinesh's 6-value enum and *not* mapped onto
  the 17 live `message.phrases` (`send_type=4`) categories backed by 969 confirmed eBay rows.
  A one-off human-read report does not create a competing vocabulary; **a system would.** N must
  still be decided (Thinesh + Sajeesan) before any classifier is built.
- **The AI columns are not a classifier.** Feedback Message, AI Category, AI Root Cause, AI
  Confidence %, Department, Priority, Business Impact and Suggested Action are a **one-time LLM
  read** of 20 comments. Re-running re-classifies from scratch; wording will differ. There is no
  saved model, no rules engine, no repeatability guarantee.
- **Owner / Status are hardcoded placeholders** (`Unassigned` / `Open`). There is no owner column
  anywhere in the database and no case-tracking table. Decision items **D** (status lifecycle)
  and **E** (owner assignment) remain undefined — these two columns track nothing.
- **Parent SKU and Product Health Score are deliberately absent.** Item **A** (the Health Score
  formula) is still undefined; inventing one would fabricate an authoritative-looking number.
- **Decision items A–F and K–O remain open**; the **DDL gate (I)** remains closed.

---

## 4. Findings worth acting on (from the 20 comments)

1. **Stock availability is the dominant root cause — 3 of 20**, including the two worst negatives
   (2026-07-07 buyer told on the delivery due date; 2026-06-23 never handed to the carrier, three
   conflicting explanations). A third (2026-07-07 `CO1230ACL`) landed *Neutral* only because the
   refund was fast.
2. **⚠ The most urgent row is a NEUTRAL.** SKU **`WLHSBMCY18`**, 2026-06-18: mains conductors
   detaching from substandard solder joints **inside an installed fitting** — a potential
   **electrical safety** issue. It is Neutral only because that buyer could self-repair.
   **A negatives-only report misses it entirely** — which is the case for pulling Neutrals.
3. **Confirmed listing defect:** item_id **166202407547** drew the *same* "self-assembly not
   disclosed" complaint from **two separate buyers** (2026-06-23 and 2026-06-27).
4. **Hard data error:** `24IP20120` length listed 13cm, actually 20cm (2026-07-10).
5. **⚠ Do not double-count:** the two 2026-06-20 rows are **ONE incident** — same buyer, same
   order `20-14744-96040`, feedback left against two items on that order.
6. **Confidence spread is real:** 95% on the explicit dimension error, **20%** on a comment whose
   entire text is "Sorry". The low-confidence rows are labelled, not guessed at.
