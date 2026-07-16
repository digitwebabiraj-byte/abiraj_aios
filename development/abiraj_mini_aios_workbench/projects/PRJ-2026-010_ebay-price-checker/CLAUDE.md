# CLAUDE.md — PRJ-2026-010_ebay-price-checker

Inherits all rules from the workbench root `CLAUDE.md` and `START_HERE.md`
(`development/abiraj_mini_aios_workbench/`). Project-specific rules below.

## Scope
- Write only inside `projects/PRJ-2026-010_ebay-price-checker/`.
- The Postgres estate is **READ-ONLY for source data**. The **only** approved write is the guarded
  single-row publish of the finished dashboard to `tech_team_outputs.ph_task`, on explicit owner
  instruction (done 2026-07-16, id 264).
- Downloads artifact (`Ebay System Task -Thinesh.xlsx`) is the user's original — read-only; the registered
  copy lives in `evidence/source_documents/REQ-12_ebay-price-checker/`.

## Task ID Rule
- Active task: `REQ-12_ebay-price-checker`. **Minted with owner confirmation 2026-07-16** — the source
  file carries no requirement id (as with REQ-11). Named after the deliverable. `project_code = epc`.
- **Minting without owner confirmation is the exact error corrected on 2026-07-15** (the `REQ-11-D02` fold,
  git `79eb59b`). Do not repeat it. A new day/session does NOT mint a new Task ID.

## ⚠ Two-Database Rule (the REQ-11 lesson — load-bearing here)
| Database | Connector | Role in this project |
|---|---|---|
| **`ledsone`** | **Ledsone-db-mcp** (`mcp.ledsone.co.uk`, `dbhub_readonly`, host 10.8.0.5) | **The price data** — `listings.*`, `inventory.*` |
| **`order_management_copy`** | Postgres MCP (host 10.8.0.3) / `temp_user` psycopg2 (149.28.134.54:5435) | **The `ph_task` publish target only** — NOT a data source |
| **AIOS knowledge base** | **Ledsone-aios-mcp** (`docs.ledsone.co.uk`) | Business rules + schema docs — **read this BEFORE building** |
- A negative sweep is only valid for the database you name. **Sweep both, say which.**
- The owner questioned using `order_management_copy` as a data *source*; do not. Its only role is publish
  + the existing-asset check.

## ⚠ Read the AIOS Knowledge Base BEFORE building (Existing-Asset-First covers rules, not just data)
The first builds ignored `Ledsone-aios-mcp` and the SKU matching was wrong. **Always apply:**
- **`all_list = 1`** on every listing query (`business/rules/ebay-listing-sku-filter.md`) — NOT
  `wrong_sku=0/is_child/is_ended`. Missing it silently drops rows (6,392 UK).
- **Amazon `_` marketplace suffix** — the base inventory SKU is everything before the first `_`
  (`sku-format-rules.md`). eBay/Shopify/B&Q do not use `_`.
- **ENC codes** — a SKU starting `ENC` is a shortened combo; resolve via `inventory.products.sku_original`.
- **`<char>PK` pack quantity** — decode via `inventory.product_pk`; multiply component prices in bundle sums.
- **Markup policy** (`cross-platform-pricing-markup.md`): website base · eBay = base ×1.10 · Amazon = base
  ×1.20. Thinesh's Amazon ×0.90 = base ×1.08 — a ~2% difference from the documented eBay target; flag it.

## 🔴 Shipping-Blind Rule (the standing safety caveat)
The AIOS KB states a price check without shipping *"will misreport correctly-priced listings as
violations"*, and the shipping source is **not yet identified** (`amazon_listings.shipping_id`, undocumented
FK). This report is **item-price only**. ⇒ **Status / Priority / Action are for ranking, not repricing.**
Never present them as sign-off-ready, and never automate this into a repricer. The VAT/postage hypothesis
was refuted (median drift +0.98%); shipping is the real open item. Route to **Sajeesan / the DB owner**.

## Confirmed Rule (do not re-derive — it is captured verbatim)
The target-price rule and Thinesh's Q1–Q8 are in `evidence/source_documents/REQ-12_.../`. Amazon-first
(lowest price), website fallback, else DATA MISSING; `ROUND(raw,2)`; £20 tolerance band; priority by
money-at-risk; bundles = sum components. **Do not blend, average, or let website override a valid Amazon
match. Exact SKU only — never approximate/parent/ASIN** (owner FAIL conditions).

## Open items (route — do NOT decide)
- **Shipping basis** → Sajeesan / DB owner. The blocker for repricing.
- **Sunsone (`so_926407`) / Retro LED (`re6865`) identity** → Thinesh (inferred, not confirmed).
- **Priority £5/£2 cutoffs** → Thinesh (Q6 gave a direction, not numbers — the bands are the developer's).
- **Q8 two new status values** (`PRICE_TOO_HIGH`, `PRICE_SOURCE_MISSING`) → Sajeesan before they enter
  `staging_ai.pricing_safe_status_reason_catalog_v1` (duplicate-vocabulary risk).
- **FX** for the German (EUR) accounts → Thinesh (Q7 said "same rules"; no rate given).

## Locked Conventions (from the sources — reproduce, do not re-invent)
- Grain: **one row per eBay listing SKU** (`item_id` + `sku`). eBay price is per-variant (this resolves the
  REQ-11 item-K multi-variant worry favourably).
- Currency: UK £, Germany €. **No FX applied** — do not sum money across currencies.
- Store/account filters use `=`, never `LIKE`.
- The xlsx's 7 sample rows are **mock** AND known-wrong under the confirmed rule — never reproduce, never
  validate against them.
- `project_code = 'epc'` verified unused before publish; live has **no UNIQUE on `task_id`** — guard
  duplicates manually inside the committing transaction.

## Stop Conditions (in addition to workbench rules)
- Stop before repricing anything or automating a repricer — Status is shipping-blind and unsigned.
- Stop before adding the two new Q8 status values to the production catalog without Sajeesan.
- Stop before drawing a "not found anywhere" conclusion from one database.
- Stop and route the open items above rather than deciding them.
- Do not commit/push or re-publish without explicit instruction.
