# PRJ-2026-011 — eBay Account Performance Dashboard (Thinesh)

One-screen landing page. Canonical context is `PROJECT_HOME.md`; full functional detail is
`SYSTEM_REFERENCE.md`.

**What:** for every active eBay store account across every marketplace it sells in, a monthly
**account × marketplace** performance dashboard — Sales (revenue/orders/units/AOV/conversion, with
Month-over-Month + Year-over-Year), Advertising (real ad spend + TACOS + Return), and Listings & Stock
(active, new, sales rank) — so a manager reads each account's real position per marketplace, June 2026.
**Task:** REQ-13_ebay-account-performance-dashboard. **Dev:** Abiraj. **Business Validator:** Thinesh.

## ✅ Status — **REQ-13-D01 DELIVERED · PUBLISHED (4 users) · ACCEPTED — CLOSED 2026-07-20**

A live read-only dashboard over **12 active eBay accounts × their marketplaces = 22 rows**, June 2026,
published per-user to `tech_team_outputs.ph_task` — **ids 333 (Thinesh), 334 (Jarsini), 335 (kobiga),
336 (powsteena)**, all `project_code=ebpd`, `assigned_user_team=ebay_priors`, `released`, each the same
final dashboard (per-marketplace, order_total sales, ON_SITE ad + Ad Sales + TACOS, filters, sticky
headers, CSV export). Both formats — the interactive HTML and a 3-sheet Excel — in
`evidence/final_outputs/REQ-13_ebay-account-performance-dashboard/`. **Accepted 2026-07-20 by Thinesh
("all ok")**; the two remaining definition items resolved-as-accepted with current defaults.

**Result (June 2026):** Revenue **£95,455.18** (order_total, Completed) · 4,625 orders · 7,330 units ·
ON_SITE ad spend **£7,788.75** · Overall **TACOS 8.16%** · Active listings 14,288 (12,799 per-site) ·
New listings 248.

## The build was corrected **five times** against the owner's own live-DB checks (the defining story)
The first build was straightforward; the value was in reconciliation. Each round exposed a real
definition trap and moved real numbers:

| # | Owner flag | Root cause | Fix |
|---|---|---|---|
| 1 | Revenue mismatch vs owner's MCP check | `item_price*qty` (+ my template-postage) ≠ eBay's paid total | **Revenue = `SUM(order_total)`** (settled paid value, incl. real postage) |
| 2 | "LEDSONE UK" too high | a store sells cross-border; whole-store inflated the "UK" row | **rows = account × marketplace** (led_sone-UK £28,975.37 now ties to the owner's check) |
| 3 | Conversion should be whole-account | was ad-only (ad orders ÷ ad clicks) | **`traffic_data.which_channel=2`** (eBay) whole-account conversion |
| 4 | New Listings shown as N/A | warehouse `listing_data` has no creation date | sourced from the **ledsone DB** `listings.ebay_listings.created_at` |
| 5 | Ad Sales > revenue | eBay attributes one order to every overlapping campaign | dropped attributed ACOS/ROAS → **TACOS**; then filtered to **ON_SITE** (Priority) campaigns only — so_926407 UK £884.07 now ties to the owner's check |

**Lesson: reconcile every headline against the owner's own live-DB figure, and take the platform's
settled total (order_total) over a reconstructed one.**

## ⚠ This is a READ-ONLY REPORT (like PRJ-2026-004→008, 010)
No DDL, no sync, no production writes to source tables. The only write is the **guarded publish** of the
finished dashboard to `tech_team_outputs.ph_task` (the team output registry on `order_management_copy`),
on explicit owner instruction.

## The 12 accounts (active in June 2026)
led_sone (**LEDSONE UK**) · so_926407 (**SUNSONE UK**) · electricalsone (**Electricalsone UK**) ·
ledsonede (**LEDSONE DE**) · huettenlampen · coventrylights · vintageinterior · dctransformer · re6865 ·
neighbourmarket · lighting_sone · homin_gmbh. The mockup named only 4; the other 8 were discovered from
live June activity. 5 of the 12 run eBay Promoted Listings (ON_SITE). 7 marketplaces: UK, DE, FR, IT, IE
(dormant), US, CA — UK + DE ≈ 99% of activity.

## Decisions — RESOLVED & ACCEPTED 2026-07-20 (audit trail)
- **Revenue field** — `SUM(order_total)` (Thinesh: "product + postage both"; order_total is the settled paid value).
- **Row grain** — account × marketplace (Thinesh chose per-marketplace over whole-store).
- **Conversion** — whole-account (`traffic_data which_channel=2`), not ad-only.
- **Advertising** — eBay Promoted Listings **ON_SITE (Priority) only**; shown as **TACOS** (Standard COST_PER_SALE excluded).
- **New Listings** — from ledsone `listings.ebay_listings.created_at`.
- **Sales Rank** — by revenue. **Duplicate mockup AOV column** — removed.
- **Orders count** — `COUNT(DISTINCT order_id)` kept (accepted "all ok"; the owner's other analysis showed the line-count 1,619 = `COUNT(*)` — noted).
- **Conversion RAG threshold** — kept as the mockup's (green >4.5%); flagged in the Excel Definitions sheet as suited to recalibration for whole-account conversion (~2–3%).

## Key files
| File | What |
|---|---|
| `PROJECT_HOME.md` | Governance: purpose, scope, reviewers, status, decisions |
| `SYSTEM_REFERENCE.md` | Full functional detail: the metric definitions, the 22-row grain, sources, joins, the ad-attribution + ON_SITE story |
| `CLAUDE.md` | Project execution rules |
| `TASK_REGISTER.md` | Tasks + deliverable detail |
| `evidence/source_documents/REQ-13_.../Thinesh task (1).xlsx` | Requester's mockup (target layout, dummy June figures) |
| `evidence/source_documents/REQ-13_.../2026-07-17_abiraj_REQ-ebpd_REQ-13-D01.md` | Daily requirement / planning doc |
| `evidence/source_documents/REQ-13_.../2026-07-17_ebpd_questions-for-Thinesh.md` | Clarification log (answers + resolutions) |
| `evidence/final_outputs/REQ-13_.../*FINAL.html / *FINAL.xlsx` | The published dashboard (HTML) + the matching 3-sheet Excel |
| `evidence/final_outputs/REQ-13_.../build_html_v3.py / build_excel_v3.py / push_ebpd_dashboard.py` | Generators (Excel imports the HTML's data → no drift) + the guarded publisher |
| `evidence/logs_or_screenshots/REQ-13_.../2026-07-17__abiraj__ebpd__REQ-13-D01.md` | End-of-day Skill File (the six reusable findings) |
| `sql/REQ-13_.../*.sql` | Canonical extraction queries (read-only) |
| `validation/REQ-13_.../2026-07-20_validation.md` | Reconciliation + validation record |

## Rules
Read-only against all source data. **Two databases:** the **warehouse `order_management_copy`** (sales,
ads, traffic, listings, stock) and the **`ledsone` DB** (listing creation dates + account-name map); the
`ph_task` table on `order_management_copy` is the publish target only. Sales = `SUM(order_total)`,
Completed. Ads = eBay Promoted Listings **ON_SITE** only, shown as TACOS. Mockup dummy rows are never the
answer. REQ-13-D01 is **CLOSED / accepted 2026-07-20**. See root `CLAUDE.md` + this project's `CLAUDE.md`.
