# PROJECT_HOME — eBay PPC Product Pause Automation (EPPA)

| Field | Value |
|---|---|
| **Project ID** | `PRJ-2026-013_ebay-ppc-product-pause-automation` |
| **Project code** | `eppa` |
| **Task ID** | `REQ-15_ebay-ppc-product-pause-automation` |
| **Status** | **D01 + D02 BUILT · live-verified · dashboard verified + stock rule (decision C) confirmed 2026-07-21 — awaiting reviewer sign-off and schedule registration** |
| **Opened** | 2026-07-21 |
| **Owner** | Abiraj |
| **Coordinator** | Varmen |
| **Technical Reviewer** | Sajeesan |
| **Queryability Reviewer** | Tamil Selvan |
| **Business Validator** | **Meshika** — confirmed 2026-07-21, verified live in `staff.users` (id 182, username `meshika`, Active, Nelliady; single exact match). ⚠ Not in the `ebay_priors` group that receives REQ-12/13/14 — the publish audience for this report must be confirmed before any `ph_task` write. |

## Business question

> For LEDSone's eBay UK Promoted Listings, which advertised listings should be paused right now
> because they are out of stock, low on stock, running above the ACOS ceiling, or burning clicks
> without producing sales — and how much monthly spend does that recover?

## Scope

**In scope (confirmed by the owner, 2026-07-21):**
- Account **LEDSone** (`ss_name='led_sone'`), marketplace **UK**, eBay Promoted Listings.
- **Stock data** + **eBay campaign performance data** as the two inputs.
- The rule engine exactly as specified in the canonical HTML mockup (see `SYSTEM_REFERENCE.md` §2).
- A **read-only recommendation** output with a staff approve/reject column.

**Out of scope / blocked:**
- **Any write to live eBay PPC.** Executing a pause falls under *Never Touch Without Written
  Approval* ("live automation" + "financial or PPC business logic"). No approval exists. The
  system recommends; a human executes in Seller Hub.
- Marketplaces US and DE (present in the mockup's switcher; owner scoped this build to UK).
- Custom Rules engine — planning worksheet only in the source, not wired to anything.

## Sources

Both imported COPY-only with SHA-256 recorded —
`evidence/source_documents/REQ-15_ebay-ppc-product-pause-automation/SOURCE_MANIFEST.md`.
The **HTML is canonical** for business logic (it holds the executable `evaluate()` engine); the xlsx
is the same system rendered as a workbook.

## Current position

**REQ-15-D01 built and live-verified; REQ-15-D02 built, not yet registered.** Anchored on the last
complete day (2026-07-20): **45 campaigns · 15 recommended pauses (8 Stock · 7 Rule 1 · 0 Rule 2) ·
16 still running · 14 already off · £1,403.54 of £3,532.41 30-day spend at risk.**

The engine was **re-implemented independently in SQL** and diffed against the shipped artefacts —
45/45 campaigns identical on all six fields, all ten KPIs reconciled, scope audit balanced, HTML and
xlsx matching the governed JSON, warehouse corroborating the campaign census. Record:
`validation/REQ-15_.../2026-07-21_live_data_verification.md`.

**Dashboard verified by Meshika 2026-07-21.**

The live build has **better inputs than the mockup**: the mockup's sample was one 7-day export with
30D/14D fields faked from it (which silently disabled Rule 1's rescue clause), whereas the raw DB
carries true daily grain.

## Open decisions — required before build

| # | Decision | Who | Why it matters |
|---|---|---|---|
| ~~A~~ | ~~SMART campaigns: whole-campaign or exclude?~~ | — | **CLOSED / WITHDRAWN 2026-07-21.** The "no listing-level data" finding was a *warehouse* artefact. The raw `ledsone` DB has 179 SMART listings / £751.09 per 30D at listing grain, so SMART is evaluated per listing like everything else. No decision needed. |
| **B** | Are Standard (COST_PER_SALE) campaigns in scope, and under what rule? | Business Validator + Sajeesan | Verified mechanically: CPS records **£0.00 spend and £0.00 sales** in `performance_data` (all money columns are `cpc_*`). Rule 1 is uncomputable; Rule 2 is permanently rescued by its own spend floor. CPS money must first be sourced from `campaign_report_data` / `accounting.ebay_order_expenses`. 1,841 listings / 5,492 clicks / 1,069 orders currently unserved. |
| ~~C~~ | ~~"Units in stock" for a multi-variant listing~~ | — | **CLOSED 2026-07-21 — OPTION A (SUM across variants).** A listing is out of stock only when every version is at zero. Already what the report does, so no rebuild. Measured alternative: "any one version at zero" would flag **31 of 31** live campaigns instead of 8. Accepted caveat: a listing whose best version is at zero keeps advertising while siblings hold stock — stated on the report. |
| **D** | Report grain: one row per listing, or per listing×campaign? | Business Validator | 610 listings produce 732 rows because a listing can run in several campaigns. |
| ~~E~~ | ~~Business Validator identity~~ | — | **CLOSED 2026-07-21 — Meshika** (verified live in `staff.users`, id 182). |
| **E2** | Who receives the published report? | Meshika | Meshika is not in `ebay_priors` (the REQ-12/13/14 audience). Recipients must be named before any `ph_task` publish, and each verified against `staff.users`. |
| **F** | Run cadence (mockup implies weekly, Monday) and whether it becomes a scheduled job | Coordinator | Slot must avoid the four existing jobs on the shared `temp_user` account. |
| **G** | Confirm the five thresholds are the real operating values, not mockup placeholders | Business Validator | They drive every decision; they stay configuration, never hardcoded. |

## Reviewer gates

- **Sajeesan (technical)** — pending
- **Tamil Selvan (queryability)** — pending
- **Business Validator (Meshika)** — ✅ **dashboard verified 2026-07-21.** ⚠ Records review of the
  artefact; does **not** by itself close decision C (the stock rule), which must be confirmed
  explicitly because 8 of the 15 recommendations rest on it.

## Register links

- Task index: `TASK_REGISTER.md`
- Full functional detail: `SYSTEM_REFERENCE.md`
- Execution rules: `CLAUDE.md`
- Portfolio row: `../../PROJECT_REGISTER.md`

## Next action

Dashboard reviewed ✅ · Decision C answered ✅ (Option A) — **the report is no longer provisional.**
Remaining, in order:
1. **Register the weekly task** — fill `eppa_secrets.bat`, then `register_eppa_task.ps1`.
2. **Sajeesan (technical) + Tamil Selvan (queryability) sign-off.**
3. **Decisions B** (are CPS campaigns in scope) and **E2** (who receives the published report).
4. `ph_task` publish and git commit — both await explicit owner instruction.
