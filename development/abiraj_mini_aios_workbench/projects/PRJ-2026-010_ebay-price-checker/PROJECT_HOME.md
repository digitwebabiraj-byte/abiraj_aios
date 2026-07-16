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
- Technical Reviewer: **Sajeesan** — not yet engaged (owns the shipping source + the Q8 vocabulary)
- Queryability Reviewer: **Tamil Selvan** — not yet engaged
- Business Validator: **Thinesh** — Q1–Q8 answered; **final sign-off pending**

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
- **Do not reprice from this report** — Status is shipping-blind (see *Known Risks*). It recommends; it
  never changes a live price. Pricing is commercial logic under the root `CLAUDE.md`.
- Do not add the two Q8 status values to the production catalog without **Sajeesan**.
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
| 6 | Shipping? | ⚠ **NOT included.** AIOS KB warns this misreports; source not identified. **Status is shipping-blind — rank, don't reprice.** |

## Known Risks / Open Items (route — do NOT decide)
- **A. ⚠ Shipping basis — the defining open item.** The AIOS KB states a price check without shipping
  *"will misreport correctly-priced listings as violations"*; the source is not identified
  (`amazon_listings.shipping_id`, undocumented FK). **Status/Priority/Action are for ranking, not
  repricing.** → Sajeesan / DB owner.
- **B. Sunsone (`so_926407`) / Retro LED (`re6865`) identities** are inferred (fit the UK/DE split, counts
  reconcile, but no literal name in the DB). → Thinesh.
- **C. Amazon ×0.90 = base ×1.08** vs the documented eBay target base ×1.10 (~2% gap). → Thinesh.
- **D. Priority £5/£2 cutoffs** are developer defaults — Q6 gave a direction, not numbers. → Thinesh.
- **E. Q8 two new status values** (`PRICE_TOO_HIGH`, `PRICE_SOURCE_MISSING`) are not in
  `staging_ai.pricing_safe_status_reason_catalog_v1` — a duplicate-vocabulary risk. → Sajeesan.
- **F. FX** for the German (EUR) accounts is undefined (Q7 said "same rules"; no rate). → Thinesh.
- **G. Bundles** — the sum-of-components rule recovers only ~11% (components often unpriced too). A
  bundle-pricing policy is needed for the rest. → Thinesh.

## Live Publish
**`tech_team_outputs.ph_task` id 264** — `project_code=epc`, `task_id=epc_Thinesh_ebay_price_checker-V1`,
`assigned_user=Thinesh`, `assigned_user_team=ebay_priors`, released, 17 MB dashboard. Guarded `temp_user`
INSERT; independently re-verified. Repo not committed/pushed.

## Status
**REQ-12-D01 — DELIVERED & PUBLISHED (read-only), technically GREEN (8/8 reconciled), NOT SIGNED OFF.**
Project registered, source imported + checksum-verified, the chat-only confirmed rule + Q1–Q8 captured,
governance docs authored, the report built (matching corrected against the AIOS KB) and published on owner
instruction. Blocked from "done" by the shipping question (A) + reviewer/business sign-off; several smaller
items (B–G) open.

## One Next Action
Route **A (shipping basis)** to Sajeesan / the DB owner — it gates repricing and is the difference between
"a ranking aid" and "a system." In parallel, put **B–D, F, G** to Thinesh and **E** to Sajeesan, and
engage Sajeesan + Tamil Selvan for sign-off.
