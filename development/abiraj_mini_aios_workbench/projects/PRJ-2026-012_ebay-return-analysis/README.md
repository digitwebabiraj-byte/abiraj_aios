# PRJ-2026-012 — eBay Return Analysis Dashboard (Thinesh)

One-screen landing page. Canonical context is `PROJECT_HOME.md`; full functional detail is
`SYSTEM_REFERENCE.md`.

**What:** a per-SKU **eBay Return Analysis** dashboard (Excel) — one row per variant SKU with at least
one eBay return in the period — showing Orders, Returns, Return Rate, Last Month / Last Year Returns,
Refund (£), Return Cost (£), Main Return Reason, Return Rank, Negative Feedback, Open Cases, Stock, and
Ad Spend / Ad Sales / ACOS / ROAS, plus a Return-Reason Breakdown, a Filter Options block and a
Before/After efficiency table. Built from the live Ledsone PostgreSQL.
**Task:** REQ-14_ebay-return-analysis (`project_code=ERA`). **Dev:** Abiraj. **Business Validator:** Thinesh.

## ✅ Status — **DELIVERED · PUBLISHED · AUTOMATED · SIGNED OFF — 2026-07-20**

**Governed identity:** project = eBay Return Analysis · `project_code=ERA` · phase = Reporting &
Presentation (first governed report) · requirement `REQ-14` · deliverable `REQ-14-D01`. Reviewer
(Sajeesan, Tamil Selvan) + business (Thinesh) **sign-offs received 2026-07-20**. Live rows **ids
387–390**.

A light-theme HTML dashboard (EBPD house style) with a **date-range dropdown** — Full month / 1st–2nd
half / Week 1–4, each re-scoping the whole dashboard from live per-window pulls (pure-CSS, works in the
no-JS ph_task viewer), rendered **full-width / full-screen**. **Published per-user to
`tech_team_outputs.ph_task` — ids 387 (Thinesh), 388 (Jarsini), 389 (kobiga), 390 (powsteena)**,
`project_code=ERA`, `assigned_user_team=ebay_priors`, `released`. **Automated monthly:** Windows Task
`ERA_Monthly_Dashboard`, **day 5 @ 09:30** (next run 2026-08-05), reports the last complete month, direct
psycopg2 (no MCP). The canonical SQL is live-verified against `ledsone` — see
`validation/REQ-14_.../2026-07-20_live_count_verification.md`.

**Figures — LIVE (June 2026):** 144 SKU rows · 153 returns · blended return rate **17.7%** · Refund
**£2,937.37** · Return Cost **£869.39** · Ad Spend **£1,387.96** · Ad Sales **£9,343.63** · ACOS **14.9%**
· ROAS **6.73x**; reason breakdown sums to 153 (live Orders total 863). Sign-offs received; identity
confirmed. Only open item: optional cross-month ranges (Last 90 Days / Last Year) + git commit.

## ⚠ Identifiers minted with owner confirmation PENDING
The source files carry no requirement id (as with REQ-11 / REQ-12 / REQ-13). `REQ-14` and `ERA` are the
next value in the documented sequence, used as the working default so onboarding is not blocked —
**confirm both with the owner** before a live build or publish.

## ⚠ This is a READ-ONLY REPORT (like PRJ-2026-004→008, 010, 011)
No DDL, no sync, no production writes to source tables. The only write — **only** when a live build is
explicitly authorised — is the guarded publish of the finished dashboard to `tech_team_outputs.ph_task`.

## The build recipe (from the handoff — for whoever runs the live build)
1. Run **statement 1** of `sql/REQ-14_.../ebay_return_analysis.sql` via the **Ledsone Database MCP** →
   export as tab-separated, no header, NULLs as empty string → `main.tsv`.
2. Run **statement 2** (bottom of the .sql) → `reason_breakdown.tsv`.
3. `python build_dashboard.py main.tsv reason_breakdown.tsv eBay_Return_Analysis_June2026.xlsx` (needs `openpyxl`).
4. **Recalculate** with LibreOffice (openpyxl writes formulas with no cached values); confirm 0 errors.
5. **Diff against the reference** figures above before acceptance.
- To re-run for another month: edit the **six dates** at the top of the SQL + `PERIOD_LABEL` in the
  build script (handoff §6 / RUNBOOK). Stock is always a live snapshot, never period-bound.

## The pitfalls the SQL already handles (do not "fix")
- **SKU resolution:** join returns→SKU via `transaction_id` → `order_item_info.item_transaction_id`.
  Joining on `item_id` is WRONG (1,331 item_ids map to multiple variants).
- **`performance_data` is CPC-only** — Standard/CPS ad cost is a per-sale fee in
  `accounting.ebay_order_expenses` (`AD_FEE` / `PREMIUM_AD_FEES`). Ad Spend/Sales = **CPC + CPS**.
- **Text-typed numerics** (`item_quantity`, `real_qty`, prices) are VARCHAR — cast `NULLIF(x,'')::numeric`.
- **`ebay_order_expenses.order_id` = the eBay order reference** (`orders.order_id`, varchar), not `orders.id`.
- **Return case fields** (reason, `seller_refund_amount`) live only on the **earliest** row per
  `return_id`; latest STATE = the **newest** row (the two `DISTINCT ON` CTEs).

## Intentional blanks (real, not errors — do not fill with 0)
- Blank **Return Rate** = zero period orders (returns of earlier-period purchases).
- Blank **ACOS / ROAS** = no ad-attributed sales / no ad spend that SKU.
- Count / £ columns DO show real `0` / `£0.00`. Return Cost = £0 on some SKUs = no matching fee row
  upstream (~65% fee coverage) — a data limitation, not a bug.

## Key files
| File | What |
|---|---|
| `PROJECT_HOME.md` | Governance: purpose, scope, reviewers, status |
| `SYSTEM_REFERENCE.md` | Full functional detail: the 19 columns + their derivations, sources/joins, the CPC+CPS ad story, blanks & caveats |
| `CLAUDE.md` | Project execution rules |
| `TASK_REGISTER.md` | Tasks + deliverable detail |
| `evidence/source_documents/REQ-14_.../CLAUDE_CODE_HANDOFF.md` | Execution brief / RUNBOOK / acceptance criteria |
| `evidence/source_documents/REQ-14_.../eBay_Return_Analysis_HANDOFF.md` | Long-form column/derivation reference |
| `evidence/source_documents/REQ-14_.../Thinesh task (2).xlsx` | Requester's mockup (target layout, dummy figures) |
| `evidence/source_documents/REQ-14_.../SOURCE_MANIFEST.md` | Import provenance + SHA-256 |
| `sql/REQ-14_.../ebay_return_analysis.sql` | The two canonical queries (source of truth for the data) |
| `evidence/final_outputs/REQ-14_.../build_dashboard.py` | Formats the query outputs into the workbook (formatting only) |
| `evidence/final_outputs/REQ-14_.../eBay_Return_Analysis_June2026.xlsx` | Reference build (diff target) — NOT a workbench-produced deliverable yet |

## Rules
Read-only against all source data (live Ledsone PostgreSQL, normalised domain schemas — **not** the
`public.*` layer). The `ph_task` table is the publish target only, and only when a live build is
authorised. Mockup dummy rows are never the answer. See root `CLAUDE.md` + this project's `CLAUDE.md`.
