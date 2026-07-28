# eBay Price Checker — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques extracted from PRJ-2026-010 (REQ-12). These are methods
> worth reusing on other cross-channel pricing / listing-report projects — not one-off facts.
> **What this project does:** a read-only exception report of eBay price-drift vs the company's
> own Amazon (or website) target price, across live UK + DE listings on 13 accounts.
> **Sources:** `PROJECT_HOME.md`, `SYSTEM_REFERENCE.md`, the CONFIRMED BUSINESS RULE
> (`evidence/source_documents/…/2026-07-16_CONFIRMED_BUSINESS_RULE_target_ebay_price.md`),
> and the source-audit log (`evidence/logs_or_screenshots/…/2026-07-16_source_audit_and_aios_rules_correction.md`).

## Reusable rules / methods

### 1. Amazon-first target-price rule (single source, never blended)
Derive one target from a strict source priority: look up the (normalised) eBay SKU in the
approved Amazon source → if a valid price exists, `target = amazon_price × 0.90`
(`target_source = AMAZON`). Only if Amazon is missing/invalid, fall back to the website source →
`target = website_price × 1.10` (`WEBSITE_FALLBACK`). Else `Status = DATA MISSING`.
**Never** average, compute-both-and-choose, or let website override a valid Amazon match. Exact
SKU only — no parent/similar/approximate SKU. On a duplicate Amazon match take the **LOWEST**
price. Round to 2dp.

### 2. SKU normalisation before matching (four documented transforms)
Apply to every listing before comparing prices:
- `all_list = 1` on all four listing tables — returns only real listable SKUs (parent containers
  excluded). Mandatory.
- Amazon `_` marketplace suffix — base SKU is everything before the first `_` (Amazon only).
- `ENC…` shortened combo codes — resolve to the real SKU via `inventory.products.sku_original`.
- `<char>PK` pack suffix — decode the pack quantity via `inventory.product_pk`; multiply
  component prices by it in bundle sums.

### 3. Tolerance bands scaled by price
Classify drift inside a band, not on exact equality: `±£0.50` when eBay price < £20, `±£1.00` at
£20 and above. Within → `Normal`; above → `High Price`; below → `Low Price`.

### 4. Bundle = sum of priced components
Combo (`+`) SKUs: split on `+`, price each component, sum, then apply the normal rule. Only valid
when every component is priced (recovers ~11% of bundles); otherwise flag as `BUNDLE` under DATA
MISSING (distinct from `NO COMPARATOR` = eBay-only).

### 5. Priority by money-at-risk
Rank exceptions by absolute money exposure, not percentage: High if `|Difference| ≥ £5`, Medium
if `≥ £2`, else Low; `Unknown` when no target. (Owner gave the direction; the £5/£2 cutoffs are
the developer's.)

## Gotchas / traps
- **Read the AIOS KB BEFORE building.** The first builds (v1–v2) skipped `Ledsone-aios-mcp` and
  got SKU matching wrong (`all_list` filter, Amazon `_` suffix, ENC, PK) — dropping 6,392 rows and
  mis-handling tens of thousands of SKUs. Fixing against the documented rules lifted direct Amazon
  matches +22%. Existing-Asset-First applies to documented **rules**, not just data.
- **Two-database rule.** `ledsone` (Ledsone-db-mcp) is the read-only source of all price data;
  `order_management_copy` is the **publish target only** — never a data source. It was earlier
  wrongly used as a source, which the owner questioned.
- **No UNIQUE on `ph_task.task_id`.** The publish table has no uniqueness constraint, so a
  re-publish can silently duplicate rows — guard manually (verify names live against `staff.users`,
  re-verify inserted rows).
- **`assigned_user_team` missing from sample DDL.** The published rows still need it set
  (`ebay_priors` here); the sample DDL omits the column.
- **Shipping-blind.** Status/Priority/Action compare **item price only**; the KB warns a correct
  check must add per-channel shipping. Use for ranking, not repricing (a shipping-aware rebuild =
  future REQ-12-D02).
- **Derived currency.** `shopify_listings.currency` is empty — derive from `sub_source` (GBP=104,
  EUR=108); no FX applied across UK/DE, so never sum money across currencies.

## Key sources (schema.table.column)
- Current eBay price: `listings.ebay_listings` — `all_list=1`, `site IN ('UK','Germany')`, `price>0`.
- Approved Amazon price: `listings.amazon_listings` — `all_list=1`, `sub_source=8`; lowest on duplicate.
- Approved website price: `listings.shopify_listings` — `all_list=1`, `sub_source=104` (UK) / `108` (DE).
- SKU normalisation: `inventory.products.sku_original` (ENC), `inventory.product_pk` (pack qty).
- Account labels: `order_management.sub_source`.
- Publish target: `tech_team_outputs.ph_task` on `order_management_copy`.

## Automation pattern
`EPC_Weekly_Price_Checker` runs unattended every **Monday 10:30** via Windows Task Scheduler
(EBPD pattern): pull live prices from `ledsone` → validate → rebuild dashboard → guarded UPSERT of
all four `ph_task` rows in place (`version_level` bumps each run). **Fails closed** — 0 rows, a
row-count floor, non-reconciling counts, a bad render, or missing credentials abort *before* any
write, so the last good dashboard stays live. Desktop alert on failure (auto-clears on success);
`--dry-run` validates without publishing. Logins come from the **shared global credential store**
(`05_documentation/capability/shared_db_credentials/`) — no per-project secret. 10:30 was chosen to
clear other jobs sharing the `temp_user` account. Published per-user to 4 `ph_task` rows (Thinesh,
Jarsini, kobiga, powsteena), all `project_code=epc`, `assigned_user_team=ebay_priors`.
