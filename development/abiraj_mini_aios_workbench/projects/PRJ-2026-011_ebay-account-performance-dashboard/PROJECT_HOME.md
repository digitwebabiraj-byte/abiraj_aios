# PROJECT_HOME — eBay Account Performance Dashboard (Thinesh)

## Project ID
PRJ-2026-011_ebay-account-performance-dashboard

## Project Name
eBay Account Performance Dashboard | monthly account × marketplace KPIs (Sales · Advertising · Listings ·
Stock) across every eBay store account and every marketplace it sells in (LEDsONE analytics platform)

## Purpose
For every active eBay store account, for each marketplace it sells to, present the month's real
performance — revenue, orders, units, AOV, whole-account conversion (with MoM + YoY), advertising
efficiency (real ON_SITE ad spend + TACOS + Return), and listings/stock (active, new, sales rank) — so
Thinesh and the account managers read each account's true position per marketplace, not a mocked or
aggregated proxy.

**This project is a READ-ONLY REPORT** (like PRJ-2026-004 → 008, 010), **unlike PRJ-2026-009** which is a
gated build. No DDL, no sync, no writes to source tables. The only write is the guarded publish of the
finished dashboard to `tech_team_outputs.ph_task`.

## Business Question
For each of our active eBay accounts, per marketplace, what were the month's sales, advertising
efficiency and listing/stock position — so the account owner reads each account's real per-marketplace
performance for June 2026?

Status: **CONFIRMED** in shape and rule. The mockup (`Thinesh task (1).xlsx`) fixed the column shape;
Thinesh confirmed the account mapping, the revenue field (`order_total`), the row grain (account ×
marketplace), the conversion basis (whole-account), the advertising scope (ON_SITE only) and the
listing/rank rules through five reconciliation rounds against his own live-DB checks.

## Owner and Reviewers
- Owner / Developer: **Abiraj**
- Requester / report owner: **Thinesh** (+ the eBay account managers; report viewers Jarsini, kobiga, powsteena)
- Coordinator: Varmen
- Technical Reviewer: **Sajeesan** — gate pending (technical)
- Queryability Reviewer: **Tamil Selvan** — gate pending
- Business Validator: **Thinesh** — **accepted 2026-07-20 ("all ok")**

## Original Requirement
- **REQ-13 (2026-07-17)** — Build the eBay account-performance dashboard per `Thinesh task (1).xlsx`
  (target layout, dummy June figures) as clarified by Thinesh across the day. Task ID
  `REQ-13_ebay-account-performance-dashboard` and `project_code=ebpd` **minted with owner confirmation** —
  the source carries no requirement id (as with REQ-11 / REQ-12).
- **REQ-13-D01** — first deliverable: a populated read-only dashboard, June 2026, over the 12 active eBay
  accounts × their marketplaces (22 rows); interactive HTML + 3-sheet Excel; **published to `ph_task`
  ids 333–336 (released)**. Requirement doc:
  `evidence/source_documents/REQ-13_.../2026-07-17_abiraj_REQ-ebpd_REQ-13-D01.md`.

## Approved Scope
- Maintain this project folder (`projects/PRJ-2026-011_ebay-account-performance-dashboard/`).
- Read-only against the warehouse `order_management_copy` (Postgres MCP) and the `ledsone` DB (Ledsone-db-mcp) for source data.
- The **single approved write**: the guarded publish of the finished dashboard to
  `tech_team_outputs.ph_task` on `order_management_copy`, on explicit owner instruction (done — ids 333–336).

## Prohibited Scope
- No write to any **source** table; no DDL; no schema change; no automation.
- The report reports; it never changes a listing, price or campaign.
- Do not use `order_management_copy` as a data source for anything except the `ph_task` publish (its
  warehouse tables ARE the source; the `ph_task` table is the output registry).
- Do not decide the two remaining definition items unilaterally — they belong to Thinesh. Do not
  re-publish without explicit instruction.

## Systems and Sources
- **Warehouse `order_management_copy`** (Postgres MCP, read-only) — the data: `order_transaction`
  (sales), `order_shipping_billing_detail` (postage; not used — order_total supersedes),
  `ppc_performance` + `ppc` (advertising + campaign metadata), `traffic_data` (organic traffic),
  `listing_data` (active listings), `inv_final_stock` (stock).
- **`ledsone` DB** (Ledsone-db-mcp, read-only) — `listings.ebay_listings` (listing `created_at` → New
  Listings) + `order_management.sub_source` (account-name map).
- **`tech_team_outputs.ph_task`** on `order_management_copy` (Postgres MCP / `temp_user`) — the publish target only.

## Run Snapshot — REQ-13-D01 delivered 2026-07-17, accepted 2026-07-20 (read-only)
| # | Question | Executed answer |
|---|---|---|
| 1 | Which accounts / scope? | Mockup named 4; **12 accounts active in June** across **7 marketplaces** — discovered from live `order_transaction`. Rows = account × marketplace = **22**. |
| 2 | Revenue field? | **`SUM(order_total)`** (Completed) — the settled paid value incl. real postage. Reconciles to the owner's check (led_sone UK £28,975.37). |
| 3 | Conversion? | **Whole-account** = `SUM(conversion)/SUM(click)` from `traffic_data which_channel=2` (eBay), per marketplace. |
| 4 | Advertising? | eBay Promoted Listings **ON_SITE (Priority) only** (join `ppc_performance.record_id = ppc.parent_id`, `record_subtype='ON_SITE'`). Real spend + **TACOS** (attributed ACOS/ROAS over-count → omitted). so_926407 UK £884.07 reconciles to the owner's check. |
| 5 | New Listings? | `listings.ebay_listings.created_at` on the **ledsone DB** (warehouse `listing_data` has no creation date) — 248 in June. |
| 6 | Result | 22 rows; Revenue £95,455.18 / 4,625 orders / 7,330 units; ON_SITE ad £7,788.75 / TACOS 8.16%; active 12,799 (per-site) / new 248 / stock 13.58M (shared). Reconciled to the owner's independent MCP figures to the penny. |

## Decisions — RESOLVED & ACCEPTED 2026-07-20 (audit trail)
- **A. Revenue field** — `SUM(order_total)` (settled paid value). Product-only and product+template-postage were both wrong.
- **B. Row grain** — account × marketplace (a store sells cross-border; the owner chose per-marketplace).
- **C. Conversion basis** — whole-account eBay traffic (`which_channel=2`), not ad-only.
- **D. Advertising scope** — ON_SITE (Priority) campaigns only; Standard COST_PER_SALE excluded; shown as TACOS.
- **E. New Listings source** — ledsone `listings.ebay_listings.created_at`.
- **F. Sales Rank** = by revenue; **duplicate mockup AOV column** removed.
- **G. Orders count** — `COUNT(DISTINCT order_id)` kept ("all ok"); the owner's other analysis showed 1,619 = `COUNT(*)` line-count — noted, not adopted.
- **H. Conversion RAG threshold** — kept as the mockup's; flagged for recalibration (whole-account conversion is ~2–3%, so green >4.5% mostly reads amber/red). Documented in the Excel Definitions sheet.

## Live Publish — 4 users
**`tech_team_outputs.ph_task`** — published per-user, all `project_code=ebpd`,
`assigned_user_team=ebay_priors`, `released`, each the same final dashboard:

| id | assigned_user | task_id |
|---|---|---|
| 333 | Thinesh | `ebpd_Thinesh_ebay_account_performance-V1` |
| 334 | Jarsini | `ebpd_Jarsini_ebay_account_performance-V1` |
| 335 | kobiga | `ebpd_kobiga_ebay_account_performance-V1` |
| 336 | powsteena | `ebpd_powsteena_ebay_account_performance-V1` |

Guarded `temp_user` publish via `push_ebpd_dashboard.py` (**pre-DELETE by task_id + plain INSERT** — the
live table has **no real `UNIQUE(task_id)`** despite the DDL comment, so `ON CONFLICT` fails; the
**`assigned_user_team` column is missing from the sample DDL but must be set** = `ebay_priors`). Re-pushed
on each correction; the ids increment by 4 per publish (309→313→317→321→325→329→333).

## Status
**REQ-13-D01 — DELIVERED · PUBLISHED (4 users) · ACCEPTED — CLOSED 2026-07-20.** Both formats (HTML live +
Excel) on the final method (per-marketplace, order_total, ON_SITE ad + TACOS), each headline reconciled to
the owner's independent live-DB check. Business acceptance received ("all ok"); the two definition items
resolved-as-accepted with current defaults. Reviewer gates (Sajeesan technical, Tamil Selvan queryability)
not formally recorded.

**REQ-13-D02 — DELIVERED 2026-07-20.** Weekly autonomous refresh (Windows Task `EBPD_Weekly_Dashboard`,
Mon 09:30) → dynamic last-complete-month, direct psycopg2 (no MCP), static-HTML render (fixes the no-JS
viewer), month-keyed publish, ledsone New Listings wired, status file + `check_status.bat` + Desktop failure
alert, and **in-month date-range presets** (pure-CSS, Full/halves/weeks — work in the viewer). All passwords
moved to the git-ignored `ebpd_secrets.bat`. See `automation/AUTOMATION_README.md`.

## One Next Action
**None outstanding.** D01 CLOSED/ACCEPTED; D02 automation live, scheduled, monitored, credentials secured.
Optional future (only if requested): browser-only free from/to date picker; formal reviewer sign-off record.
