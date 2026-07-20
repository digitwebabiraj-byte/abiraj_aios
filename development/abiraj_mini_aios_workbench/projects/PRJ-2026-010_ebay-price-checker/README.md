# PRJ-2026-010 — eBay Price Checker (Thinesh)

One-screen landing page. Canonical context is `PROJECT_HOME.md`; full functional detail is
`SYSTEM_REFERENCE.md`.

**What:** for every live eBay listing across Thinesh's 13 accounts (UK + Germany), compute a **target
price** from the Amazon price (fallback: the website price), measure the drift against the current eBay
price, and return a **Status / Priority / Action** — an exception report of what's mispriced and which way.
**Task:** REQ-12_ebay-price-checker. **Dev:** Abiraj. **Business Validator:** Thinesh.

## ✅ Status — **REQ-12-D01 DELIVERED · PUBLISHED (4 users) · SIGNED OFF — CLOSED 2026-07-16**

A populated read-only report over **126,070 live eBay UK & DE listings**, published per-user to
`tech_team_outputs.ph_task` — **id 264 (Thinesh), 299 (Jarsini), 300 (kobiga), 301 (powsteena)**, all
`project_code=epc`, `assigned_user_team=ebay_priors`, `released`, each the same 17 MB dashboard (with the
Export-CSV button + taller table, version 3). Deliverables — the 13-column UI xlsx, the full-screen
dashboard, the decision sheet and the build scripts — in `evidence/final_outputs/REQ-12_ebay-price-checker/`.
**Signed off 2026-07-16** by Thinesh (business), Sajeesan (technical / shipping / Q8 vocabulary) and
Tamil Selvan (queryability). Data note: Status is computed on **item price only** (shipping basis accepted
at sign-off); a shipping-aware refresh, if scoped, is a future REQ-12-D02.

**Result:** Priced OK 21,138 · Too high 40,261 · Too low 22,008 · No target 42,663
(21,048 eBay-only + 21,615 bundles).

## 🔁 Weekly automation (built 2026-07-16) — `automation/`
Runs unattended every **Monday 10:30** (Windows Task Scheduler), following the **PRJ-2026-011 (EBPD)**
pattern: pull live prices from `ledsone` → validate → rebuild the dashboard → refresh all 4 `ph_task` rows
in place. **Fails closed** (a bad pull publishes nothing — the last good dashboard stays live), alerts on
your Desktop if a run fails, and keeps no credential in any tracked file.
Test safely: `run_epc_weekly.bat --dry-run` · Health: `check_status.bat` · Setup: `automation/AUTOMATION_README.md`.
**✅ LIVE since 2026-07-20** — `EPC_Weekly_Price_Checker` is registered and uses the shared global
credential store (no per-project secrets file). **Next run: Monday 2026-07-27 10:30.** 10:30 was chosen to
clear the other jobs on the same `temp_user` account (FRRC 09:00 · ERA 09:30 · **EBPD 09:30 Monday**).

## The rule (owner CONFIRMED BUSINESS RULE, 2026-07-16 + Thinesh Q1–Q8)
`Target = Amazon (amazon Ledsone, sub_source 8, LOWEST price) × 0.90`; else `website (Shopify ledsone /
ledsone-de) × 1.10`; else **DATA MISSING**. `ROUND(raw, 2)`. Tolerance ±£0.50 / ±£1.00 at the **£20** band.
Priority by money-at-risk. Bundles: sum component prices (works ~11% of the time). Verbatim rule:
`evidence/source_documents/REQ-12_.../2026-07-16_CONFIRMED_BUSINESS_RULE_target_ebay_price.md`.

## ⚠ This is a READ-ONLY REPORT, unlike REQ-11 (which was a gated build)
No DDL, no sync, no production writes to source tables. The only write is the **guarded publish** of the
finished dashboard to `ph_task` (the team output registry on `order_management_copy`), on explicit owner
instruction.

## 🔴 The defining caveat — Status is SHIPPING-BLIND (do not reprice from it)
The AIOS knowledge base (`business/rules/cross-platform-pricing-markup.md`) states a price check without
shipping *"will misreport correctly-priced listings as violations"*, and the shipping source is **not yet
identified** (`amazon_listings.shipping_id`, an undocumented FK). This report compares **item price only**.
⇒ **Use it for ranking and investigation, not for changing live prices.** (An earlier VAT/postage-artifact
hypothesis was refuted — the rule is well-centred; the shipping caveat is the real limitation.)

## 🔴 The build was corrected against the AIOS knowledge base (read the KB BEFORE building)
The first builds ignored the AIOS `business/rules/`, and the SKU matching was wrong. Fixing it moved real
numbers:

| AIOS rule | Fix | Impact |
|---|---|---|
| `ebay-listing-sku-filter.md` — `all_list=1` always | replaced the naive child/ended filter | **+6,392 UK rows** recovered |
| `sku-format-rules.md` — Amazon `_` suffix | strip from first `_` | 12,461 Amazon SKUs matched |
| `sku-format-rules.md` — ENC codes | resolve via `inventory.products.sku_original` | 32,474 eBay SKUs |
| `sku-format-rules.md` — `<char>PK` pack qty | decode via `inventory.product_pk` | bundle sums fixed |

Direct Amazon matches rose **+22%**. **Lesson: Existing-Asset-First covers documented rules, not just data.**

## The 13 accounts (Thinesh, 2026-07-16)
7 UK: LEDSone UK · Electricalsone UK · Sunsone UK · Vintageinterior UK · Coventrylight UK · Lightingsone
UK · Retro LED UK. 6 DE: HUETTEN LAMP DE · Ledsone DE Reg DE · Homin DE · LEDSone UK Reg DE · ElectricalSone
DE · Sunsone DE. ⚠ **`Sunsone = so_926407` and `Retro LED = re6865` are inferred** — they fit the UK/DE
split and reconcile the counts exactly, but Thinesh hasn't literally confirmed them.

## Decisions — RESOLVED & SIGNED OFF 2026-07-16 (audit trail)
All previously-open items were closed at sign-off:
- **Shipping basis** — signed off (Sajeesan / DB owner). Status is item-price-only by accepted decision; a
  shipping-aware refresh is a future REQ-12-D02.
- **Sunsone (`so_926407`) / Retro LED (`re6865`) identity** — confirmed (Thinesh).
- **Q8 two new status values** — decided (Sajeesan).
- **Priority £5/£2 cutoffs** — confirmed (Thinesh).
- **FX** for the EUR accounts + **Amazon ×0.90 = base ×1.08 vs documented base ×1.10** — confirmed (Thinesh).

## Key files
| File | What |
|---|---|
| `PROJECT_HOME.md` | Governance: purpose, scope, reviewers, status, open items |
| `SYSTEM_REFERENCE.md` | Full functional detail: the rule, the 13-account mapping, the columns, SKU normalisation, grain, currency |
| `CLAUDE.md` | Project execution rules |
| `TASK_REGISTER.md` | Tasks + deliverable detail |
| `evidence/source_documents/REQ-12_.../Ebay System Task -Thinesh.xlsx` | Requester's spec (13-col shape, legend, 7 **mock** rows) |
| `evidence/source_documents/REQ-12_.../2026-07-16_CONFIRMED_BUSINESS_RULE_target_ebay_price.md` | **The authoritative rule** (chat-captured) |
| `evidence/source_documents/REQ-12_.../2026-07-16_thinesh_decisions_Q1-Q8.md` | Thinesh's answers + account labels |
| `evidence/final_outputs/REQ-12_.../` | UI xlsx · dashboard html · decision sheet · build + publish scripts |
| `sql/REQ-12_.../d01_price_checker_pull.sql` | Canonical extraction query (read-only) |
| `evidence/logs_or_screenshots/REQ-12_.../2026-07-16_source_audit_and_aios_rules_correction.md` | Source identification + the AIOS-rules correction + the shipping-blind caveat |
| `evidence/logs_or_screenshots/REQ-12_.../2026-07-16_d01_delivery_and_publish_record.md` | Delivery + the 4-user `ph_task` publish (ids 264, 299–301) |
| `DigitWeb_Works_Abiraj/16_07_2026/2026-07-16_abiraj_REQ-epc_REQ-12-D01.md` | Daily requirement / planning doc |

## Rules
Read-only against source data. Two databases: **`ledsone`** = the price data (Ledsone-db-mcp); **`order_management_copy`** = the `ph_task` publish target only. Exact SKU only — never approximate/parent/ASIN. Mock sample rows are never the answer. Status is computed on **item price only** (shipping accepted at sign-off; a shipping-aware refresh = future REQ-12-D02). REQ-12-D01 is **CLOSED / signed off 2026-07-16**. See root `CLAUDE.md` + this project's `CLAUDE.md`.
