# PROJECT_HOME — eBay Price Checker (Thinesh)

## Project ID
PRJ-2026-010_ebay-price-checker

## Project Name
eBay Price Checker | Amazon-first cross-channel price-drift report (Amazon ⇄ Website ⇄ eBay) over live eBay
UK & Germany listings across 13 accounts (LEDsONE analytics platform)

## Purpose
For every live eBay listing SKU, derive a **target price** from the company's own Amazon price (fallback:
the website price), compare it to the current eBay price, and classify the drift into a Status / Priority /
Action — so a manager reads only the mispriced rows. A listing priced too low bleeds margin; too high it
stops converting.

**This project is a READ-ONLY REPORT** (like PRJ-2026-004 → PRJ-2026-008), **unlike PRJ-2026-009** which is
a gated build. No DDL, no sync, no writes to source tables. The only write is the guarded publish of the
finished dashboard to `tech_team_outputs.ph_task`.

## Business Question
Across our 13 eBay accounts (UK + Germany), which listings are mispriced against our own Amazon/website
prices, and in which direction — so the pricing owner can act only on the exceptions?

Status: **CONFIRMED** in shape and rule. The target rule is the owner's CONFIRMED BUSINESS RULE
(2026-07-16) and Thinesh answered the eight open decisions (Q1–Q8). A handful of items remain open (see
*Known Risks / Open Items*), the largest being **shipping**.

## Owner and Reviewers
- Owner / Developer: **Abiraj**
- Requester / report owner: **Thinesh** (+ the 13 eBay account managers and whoever owns pricing/margin)
- Coordinator: Varmen
- Technical Reviewer: **Sajeesan** — **signed off 2026-07-16** (shipping source + Q8 vocabulary + technical)
- Queryability Reviewer: **Tamil Selvan** — **signed off 2026-07-16**
- Business Validator: **Thinesh** — Q1–Q8 answered; **signed off 2026-07-16**

## Original Requirement
- **REQ-12 (2026-07-16)** — Build the eBay price checker per `Ebay System Task -Thinesh.xlsx` (13-column
  target shape) as clarified by the owner's **CONFIRMED BUSINESS RULE — TARGET EBAY PRICE** and Thinesh's
  **Q1–Q8**. Task ID `REQ-12_ebay-price-checker` and `project_code=epc` **minted with owner confirmation**
  — the source carries no requirement id (as with REQ-11).
- **REQ-12-D01 (2026-07-16)** — first deliverable: a populated read-only price-drift report over 126,070
  live eBay UK & DE listings; 13-column UI xlsx + full-screen dashboard + decision sheet; **published to
  `ph_task` id 264 (released)**. Requirement doc:
  `DigitWeb_Works_Abiraj/16_07_2026/2026-07-16_abiraj_REQ-epc_REQ-12-D01.md`.

## Approved Scope
- Maintain this project folder (`projects/PRJ-2026-010_ebay-price-checker/`).
- Read-only against the `ledsone` DB for source data (via Ledsone-db-mcp) and the AIOS KB (Ledsone-aios-mcp).
- The **single approved write**: the guarded publish of the finished dashboard to
  `tech_team_outputs.ph_task` on `order_management_copy`, on explicit owner instruction (done — id 264).

## Prohibited Scope
- No write to any **source** table; no DDL; no schema change; no repricer/automation.
- **The report recommends; it never changes a live price.** Status is computed on an item-price basis
  (signed off 2026-07-16); pricing is commercial logic under the root `CLAUDE.md` — no repricer/automation.
- The two Q8 status values were decided by **Sajeesan** (2026-07-16); do not alter the production catalog further without him.
- Do not use `order_management_copy` as a data source (it is the publish target only).
- Do not decide the open items — they belong to Thinesh / Sajeesan. Do not commit/push or re-publish
  without explicit instruction.

## Systems and Sources
- **`ledsone` DB** (Ledsone-db-mcp, read-only) — the price data: `listings.ebay_listings` /
  `amazon_listings` / `shopify_listings`, `inventory.products` (ENC), `inventory.product_pk`,
  `order_management.sub_source`. Refreshed 2026-07-15.
- **AIOS knowledge base** (Ledsone-aios-mcp, `docs.ledsone.co.uk`) — `business/rules/*`
  (cross-platform-pricing-markup, sku-format-rules, ebay-listing-sku-filter) + schema docs. **Read before
  building.**
- **`order_management_copy`** (Postgres MCP / `temp_user`) — the `ph_task` publish target only.

## Run Snapshot — REQ-12-D01 delivered 2026-07-16 (read-only)
| # | Question | Executed answer |
|---|---|---|
| 1 | Where are the three prices? | **`listings.amazon_listings` / `shopify_listings` / `ebay_listings` on `ledsone`** — identified live (the confirmed rule named them only as "approved sources"). |
| 2 | Existing price-checker asset? | **None.** `staging_ai.pricing_safe_*` on `order_management_copy` is a 21-SKU/63-row pilot with `target_price` all NULL — not a duplicate. Swept both DBs. |
| 3 | Grain / multi-variant (REQ-11 item K)? | **Resolved favourably.** eBay price is per-variant row; one row per SKU has its own price. Start-from-SKU is the right key. |
| 4 | SKU matching correct? | **Corrected against the AIOS KB** — `all_list=1` (+6,392 rows), Amazon `_`-suffix, ENC→sku_original, PK pack qty. Direct Amazon matches +22%. |
| 5 | Result | 126,070 rows — Priced OK 21,138 / Too high 40,261 / Too low 22,008 / DATA MISSING 42,663 (21,048 eBay-only + 21,615 bundles). 8/8 DB reconciliation PASS. |
| 6 | Shipping? | **Signed off 2026-07-16** on an item-price basis. Status is computed on item price only; a shipping-aware refresh, if scoped, = future REQ-12-D02. |

## Decisions — RESOLVED & SIGNED OFF 2026-07-16 (audit trail; formerly the open items)
- **A. Shipping basis** — signed off (Sajeesan / DB owner). ⚠ **Data note (true regardless of sign-off):**
  Status is computed on **item price only**; a shipping-aware refresh, if scoped, is a future REQ-12-D02.
  The live `ph_task` row descriptions keep the "item-price" note for end users.
- **B. Sunsone (`so_926407`) / Retro LED (`re6865`) identities** — confirmed (Thinesh).
- **C. Amazon ×0.90 = base ×1.08 vs the documented eBay target base ×1.10** — confirmed (Thinesh).
- **D. Priority £5/£2 cutoffs** — confirmed (Thinesh).
- **E. Q8 two new status values** (`PRICE_TOO_HIGH`, `PRICE_SOURCE_MISSING`) — decided (Sajeesan).
- **F. FX** for the German (EUR) accounts — confirmed (Thinesh).
- **G. Bundles** — bundle-pricing policy confirmed (Thinesh); the sum-of-components rule stands (~11%).

## Live Publish — 6 users
**`tech_team_outputs.ph_task`** — published per-user, all `project_code=epc`,
`assigned_user_team=ebay_priors`, `released`, each carrying the identical ~18 MB dashboard (Export-CSV +
taller table):

| id | assigned_user | task_id | added |
|---|---|---|---|
| 264 | Thinesh | `epc_Thinesh_ebay_price_checker-V1` | 2026-07-16 |
| 299 | Jarsini | `epc_Jarsini_ebay_price_checker-V1` | 2026-07-16 |
| 300 | kobiga | `epc_kobiga_ebay_price_checker-V1` | 2026-07-16 |
| 301 | powsteena | `epc_powsteena_ebay_price_checker-V1` | 2026-07-16 |
| 528 | Sharmilan | `epc_Sharmilan_ebay_price_checker-V1` | 2026-07-31 |
| 529 | Sivajitha | `epc_Sivajitha_ebay_price_checker-V1` | 2026-07-31 |

Guarded `temp_user` INSERTs. The first four were name-verified live and re-verified via the Postgres MCP.
The last two (**Sharmilan, Sivajitha**, 2026-07-31) were verified against the exact spellings already in
`ph_task.assigned_user` (each already receives other reports through this registry) and given a byte-identical
copy of the live dashboard (18,393,533 B, md5-matched to id 264). All six now sit in the weekly runner's
`ASSIGNED` list. Committed + pushed to git `main`.

## Status
**REQ-12-D01 — DELIVERED · PUBLISHED (4 users) · SIGNED OFF — CLOSED 2026-07-16.** Technically GREEN (8/8
reconciled); all business/technical decisions and reviewer gates completed on 2026-07-16. Project
registered, source imported + checksum-verified, the chat-only confirmed rule + Q1–Q8 captured, governance
docs authored, the report built (matching corrected against the AIOS KB), published per-user, and committed
to `main`. **No open items.**

## Automation — weekly auto-refresh (built 2026-07-16, part of REQ-12)
`automation/` runs unattended every **Monday 10:30** via Windows Task Scheduler (PRJ-2026-011 / EBPD
pattern): pull live prices from `ledsone` → validate → rebuild the dashboard → guarded UPSERT of all four
`ph_task` rows in place (`version_level` bumps each run). **Fails closed** — 0 rows, a row-count floor,
non-reconciling counts, a bad render or missing credentials abort *before* any write, so the last good
dashboard stays live. Desktop alert on failure (auto-clears on success); `--dry-run` validates without
publishing; no credential in any tracked file. Detail: `automation/AUTOMATION_README.md`.

**✅ LIVE since 2026-07-20.** `EPC_Weekly_Price_Checker` is registered in Windows Task Scheduler and draws
its logins from the **shared global credential store**
(`05_documentation/capability/shared_db_credentials/`) — no per-project secrets file. **Next run: Monday
2026-07-27 10:30.** 10:30 was chosen so it clears the other jobs sharing the `temp_user` account
(FRRC 09:00 day 8 · ERA 09:30 on the 5th · **EBPD 09:30 Monday**, the same day as EPC).

## One Next Action
**None required — the schedule runs itself.** Optional: `Start-ScheduledTask -TaskName
"EPC_Weekly_Price_Checker"` to refresh the four dashboards now rather than waiting for 27 July
(they currently show 16-July prices). Optional later: a shipping-aware Status rebuild (REQ-12-D02).
