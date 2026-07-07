## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-11 |
| **developer** | abiraj |
| **project** | LEDsONE Centralizer (Centralized Admin / Operations Platform) |
| **project\_code** | blos |
| **phase** | DISCOVERY |
| **requirement\_id** | REQ-04 |
| **deliverable\_id** | D01 |
| **status** | COMPLETE |
| **evidence\_location** | `DATABASE_SCHEMA.md` (repo root, branch Abiraj) · derived from `config/database.php`, `database/migrations/*`, `app/Models/**`, `app/Http/Controllers/**`, `app/Console/Commands/Ppc/PpcEtlData.php`, `routes/api.php` — Laravel 9 repo, local |
| **blos\_keys\_used** | NONE — schema discovery & documentation session; no business logic constants written |
| **hardcoded\_thresholds** | Threshold approval gate: high_count ≥ 2 → approval required; MEDIUM impact → reviewed_impact confirmation; change_reason ≥ 10 chars. PPC ETL: 32-day rolling window, 5-day batches, 3000-row buffer, chunkById 1000. Stock job: chunkById 200, fixed locations [UK, Germany, US], pack sizes 5 (5PK) / 10 (APK). PPC source codes: 1=Amazon, 2=eBay, 3=Google |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| SCHEMA-DISCOVERY \| LARAVEL \| MULTI-DB \| PPC-ETL |

## File path (fill after saving):
# 2026-06-11__abiraj__blos__REQ-04-D01.md

---

## SECTION 1 · SYSTEM STATE

- **Current system state:** Laravel 9 + Vue 2 SPA ("LEDsONE Centralizer") fully operational. A complete database-layer audit was completed today and a single hand-off reference, `DATABASE_SCHEMA.md`, was authored covering ~40 tables across 3 live databases, all relationships, every CRUD flow, the PPC ETL pipeline, the auth/permission model, and all non-working code. No application code was modified — this was a read-only discovery and documentation pass.
- **What was working at start of today:** The app runs; Threshold Configuration, File Library, and the PPC ETL command are all in place and functional.
- **What was broken / missing at start of today:** No database documentation of any kind existed. Only the stock Laravel `README.md` was present. The multi-database architecture was undocumented; a new developer had no map of which table lived in which database, how tables relate, or how data is created/read/updated. Several routes and jobs silently reference classes that do not exist.
- **Your starting point:** A request to produce a complete database schema + relationships + CRUD reference for hand-off to another developer (REQ-04-D01).
- **Environment:** Local Laravel 9 repository (PHP 8), branch `Abiraj`. Databases: `mysql` (app-owned, default), `orders` (external Order-Management DB), `ppc` (external Ads DB). No live DB / MCP access used — all findings derived from source code.

> **In plain terms:** The system worked but nobody had written down how its database actually fits together. Today mapped the entire data layer into one document so a new developer can understand it without reading the source — including the fact that the app reads from three different databases, two of which it does not own.

---

## SECTION 2 · WHAT CHANGED TODAY

- **Change 1 — Authored `DATABASE_SCHEMA.md` (repo root):** Single hand-off document with 9 sections — multi-DB overview, where PPC data comes from, auth/permissions, table-by-table schema, relationship map, CRUD flows, conventions, dead code, open questions.

- **Change 2 — Mapped the multi-database architecture:** Documented all connections in `config/database.php` (`mysql`, `orders`, `ppc`, plus unused `accounts_management` / `order_management` aliases) and labelled every table as **app-owned** (created by migrations) vs **external** (provisioned by other systems, no migrations here).

- **Change 3 — Documented the Threshold Configuration chain:** `business_rules → business_rule_categorical_mapping → thresholds → (threshold_dependencies, threshold_versions, threshold_change_requests)`, including the impact-based change/approval workflow and domain-scoped access control.

- **Change 4 — Traced the PPC ETL pipeline (`command:PpcEtlData`):** Reads the external `ppc` source tables (Amazon/eBay/Google) → normalizes status/marketplace/source codes → `upsert`s unified rows into `ppc_etl` and `ppc_etl_performance_data` on the local `mysql` DB. Clarified that the PPC source tables and data are NOT in this repo.

- **Change 5 — Documented the Inventory stock calculation:** `StockController@WarehouseLocationWiseStockUpdate` reads the `orders` DB (simple vs combo products, alternative stock) and writes computed per-location availability into `location_wise_inv_stock`.

- **Change 6 — Documented the File Library:** `folders` (self-referencing tree) + `files`, served via `FolderFileService` (Flysystem / S3).

- **Change 7 — Flagged all non-working code:** 6 controllers referenced by `routes/api.php` that do not exist; 2 jobs importing ~20 classes absent from the repo; empty seeder.

- **Deliverable A — `DATABASE_SCHEMA.md`** produced (full reference).
- **Deliverable B — this EOD skill file** produced for the Daily Skill Increment System.

Evidence reference: `DATABASE_SCHEMA.md` on branch `Abiraj` (not yet committed). All findings traceable to named source files. No credentials included.

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> Source of findings: **static source-code analysis** (models, migrations, controllers, config), not a live MCP/SQL session. The app uses **MySQL**, and most business tables have **no migration** in the repo — their structure is inferred from each model's `$table`, `$fillable`, `$casts`, `$primaryKey`, `$connection` and the queries that use them.

### Connection inventory

| Connection | Target DB | Ownership | Used by |
| :---- | :---- | :---- | :---- |
| `mysql` *(default)* | This app's DB | **App-owned** | Users, Thresholds, Business Rules, Folders/Files, POS models, PPC ETL **output** tables |
| `orders` | Order-Management DB | External | `App\Models\Inventory\*` |
| `ppc` | PPC / Ads DB | External | `App\Models\CentralizedEtlData\Ppc\*` (source tables) |
| `accounts_management` | Accounts DB | External | Configured, **not used** |
| `order_management` | Same as `orders` | — | Duplicate alias, config only |

### Table inventory by module

| Module | Connection | Origin | Tables (count) |
| :---- | :---- | :---- | :---- |
| Users & access | mysql | mixed | `user` (external), `user_domain_access` (migration) — 2 |
| Threshold Config | mysql | mostly external | `business_rules`, `business_rule_categorical_mapping`, `thresholds`, `threshold_dependencies`, `threshold_versions` (external) + `threshold_change_requests` (migration) — 6 |
| File Library | mysql | migration | `folders`, `files` — 2 |
| POS / Catalog | mysql | external (stub migration for `product`) | `categories`, `products`, `inventory`, `sales`, `sale_items`, `images`, `image_types` — 7 |
| Inventory / Stock | orders (+1 on mysql) | external | `inv_products`, `inv_stock`, `inv_product_combo`, `inv_product_mapping`, `product_pk`, `warehouse`, `location_wise_inv_stock` — 7 |
| PPC source | ppc | external | Amazon (7), eBay (6), Google (8), Common (3) — 24 |
| PPC output | mysql | external (filled by ETL) | `ppc_etl`, `ppc_etl_performance_data` — 2 |
| Infrastructure | mysql | migration | `websockets_statistics_entries` — 1 |

### Key structural findings

| # | Finding | Why it matters |
| :---- | :---- | :---- |
| 1 | App spans **3 live databases**; `$connection` decides which | Cannot SQL-JOIN across DBs — joins happen in PHP via Eloquent |
| 2 | **No migrations** for most business tables (thresholds, inventory, PPC) | `php artisan migrate` will NOT recreate a working DB; external dumps required |
| 3 | `user` is a **legacy table**; `User` model is an adapter (accessors map `name`→`user_firstname`, etc.) | Never write friendly column names directly in SQL |
| 4 | `ppc_etl` / `ppc_etl_performance_data` are the **centralized ETL output** on `mysql`, not `ppc` | This is the literal purpose of the "Centralizer" |
| 5 | Relationships join on **business keys** (`rule_id`, `threshold_id`, `campaign_id`, `amzAdGroupID`), not surrogate `id` | Each relation's foreign/owner keys must be read explicitly |
| 6 | `business_rule_categorical_mapping` has **column drift** (casing/renames) across environments | Controller resolves real column names at runtime via `Schema::getColumnListing` |

### SQL / pattern discovered

```php
// PPC ETL writes unified rows with composite natural keys (cross-DB: read ppc, write mysql)
PpcEtl::upsert($rows,
  ['source','sub_source_id','marketplace_id','parent_id','child_id','record_type'],  // unique key
  ['name','status','start_date','end_date','budget_type','type','targeting_type','updated_at']);

PpcEtlPerformanceData::upsert($rows,
  ['source','sub_source_id','marketplace_id','date','record_type','ref_id','sku','record_id','child_id','parent_id'],
  ['impressions','clicks','spend','sales','orders','updated_at']);
```

Operational meaning: this app is a **hub/centralizer**. It owns only a small set of config/file/approval tables; it reads other teams' databases (orders, ads) and consolidates them.

---

## SECTION 4 · GAP FOUND

- **Gap — 6 missing controllers (HIGH):** `routes/api.php` references `ProductController`, `CategoryController`, `SaleController`, `InventoryController`, `ReportController`, `ImageController` — none exist. Their models exist; the endpoints will 500. Impact: POS/catalog API appears available but fails. Action: implement or remove the routes. Owner: Dev team.

- **Gap — change-request approval does not apply the value (HIGH):** Approving a `threshold_change_requests` row only flips `status` + stamps approver; it does **not** write `new_value` into `thresholds` or create a `threshold_versions` row. Impact: approved changes silently never take effect. Action: add the "apply value" step. Owner: Dev team / product owner.

- **Gap — unauthenticated heavy endpoint (MEDIUM):** `GET /api/warehouse-location-wise-stock-update` runs full cross-DB stock recomputation but is outside auth middleware. Impact: publicly triggerable load. Action: move behind auth / CRON-only. Owner: Dev team.

- **Gap — broken jobs (LOW):** `CreateBulkRuleRun` / `CreateBulkShipments` import ~20 classes absent from the repo (`Order`, `Flag`, `Shipment`, `Hostinger\*`, `RuleController`, …). Impact: dead code, misleading. Action: delete or restore from the order-management system. Owner: Dev team.

- **Gap — no environment provisioning docs (MEDIUM):** External (`orders`, `ppc`) tables have no migrations or DDL here. Impact: a fresh environment cannot be stood up from this repo alone. Action: document/obtain external DB credentials and dumps. Owner: Team lead.

- **Gap — eBay/Google performance ETL not invoked (MEDIUM):** `PpcEtlData::handle()` calls Amazon performance but the eBay/Google performance methods exist and are not called. Impact: those platforms' performance rows may be stale. Action: confirm intended; wire up if needed. Owner: Dev team.

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

> No new rules coded today — existing rules were extracted from source so they are visible outside the code.

- **RULE EXTRACTED — Threshold change impact gate:** On a value change, count `threshold_dependencies.impact_level`. If `high_count ≥ 2` → create a pending change request (do not apply). If overall impact = MEDIUM → require `reviewed_impact = true`. `change_reason` must be ≥ 10 chars. Non-admins must pass domain check. Implemented in `ThresholdConfigurationController@thresholdsUpdate`. Prevents unreviewed high-risk threshold changes.

- **RULE EXTRACTED — Business-rule delete guard:** A `business_rules` row cannot be deleted while any mapping or threshold references its `rule_id`. Implemented in `businessRulesDestroy`. Prevents orphaned mappings/thresholds.

- **RULE EXTRACTED — Mapping delete reassignment:** Deleting a mapping first nulls `thresholds.mapping_id` inside a transaction. Implemented in `mappingsDestroy`. Prevents FK/orphan errors.

- **RULE EXTRACTED — User email uniqueness:** `email` unique against `user.user_email` on create/update. Implemented in `AuthController@register`, `UserController@store/update`.

- **RULE PROPOSED — Approval must apply value:** When a change request is approved, write `new_value` to `thresholds` and append a `threshold_versions` row in one transaction. Closes the gap in Section 4.

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Failure mode (OPEN) — POS/catalog endpoints 500:** Routes wired to non-existent controllers throw "class not found" at runtime. Detected via logs / 500 responses. Recovery: implement or remove. Risk: MEDIUM.

- **Failure mode (OPEN) — ETL / stock job without external DB access:** Missing or wrong `DB_*_PPC` / `DB_*_ORDER_MANAGEMENT` env values, or unpopulated source tables, cause connection errors or empty reads; the ETL has nothing to upsert. Detected via connection errors. Recovery: configure external credentials; confirm upstream sync populated the source tables. Risk: HIGH (core centralizer function depends on external DBs).

- **Failure mode (OPEN) — approved threshold change never applies:** Approval flips status only; the value stays unchanged. Detected only by comparing `threshold_change_requests.new_value` against `thresholds.value`. Recovery: add apply-step. Risk: HIGH (silent).

- **Failure mode (OPEN) — broken jobs on dispatch:** Queuing `CreateBulkRuleRun` / `CreateBulkShipments` fails on missing classes. Recovery: remove/restore. Risk: LOW.

- **Edge case (HANDLED in doc) — cross-database joins:** Because `orders` and `ppc` are separate databases, no SQL JOIN across them is possible. The codebase joins in PHP via Eloquent relations. Documented so a developer doesn't attempt a cross-DB SQL query.

- **Edge case (HANDLED in doc) — column drift on mapping table:** `business_rule_categorical_mapping` columns vary by environment; the controller probes real names at runtime. Documented so future edits keep the pattern.

---

## SECTION 7 · DECISIONS MADE TODAY

- **Decision: Document external tables by reverse-engineering models, not migrations.**
  Alternatives: wait for external DB dumps/DDL; document only app-owned tables. Reason: the deliverable is a hand-off doc and migrations for external tables will never exist in this repo. Trade-off accepted: external column lists are model-derived (may omit columns not in `$fillable`) — explicitly noted in the document.

- **Decision: Explicitly flag dead/non-working code in the document.**
  Alternatives: omit it. Reason: prevents a new developer from trusting endpoints/models that fail at runtime. Trade-off: none.

- **Decision: Make "where PPC data comes from" a top-level section.**
  Reason: this was the single most-confusing point (source tables are external, not in the repo). Promoting it prevents the most likely misunderstanding.

- **Decision: Do not modify any application code.**
  Reason: scope is discovery/documentation (REQ-04-D01). Fixes (missing controllers, approval apply-step) are flagged as gaps for a future deliverable, not silently changed.

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule — Threshold changes are governed by impact, not by edit rights

A threshold value change is risk-assessed from its registered dependencies. Any change touching **2 or more HIGH-impact dependent systems** cannot be applied directly — it becomes a **pending change request** for admin approval. MEDIUM-impact changes require the editor to confirm they reviewed the impact. Every applied change is versioned in `threshold_versions` (who/when/why). This exists so critical operational thresholds cannot be altered silently.

### Business Rule — The app is a centralizer, not a system of record

Most data is owned by other systems. `orders` (Order-Management) and `ppc` (Ads) are external databases this app only reads. The app owns just its config, file-library, approval, and PPC-ETL-output tables. Any environment setup must provide valid credentials for all three databases.

### Operational Assumption — PPC source data is produced elsewhere

The Amazon/eBay/Google tables on the `ppc` connection are filled by a separate sync application. This repo's `command:PpcEtlData` only reads them and writes the unified `ppc_etl` / `ppc_etl_performance_data` tables. Without the external DB populated, the ETL has nothing to consolidate.

### Reusable Logic / Formula

- **Impact level:** `HIGH` if any HIGH dependency, else `MEDIUM` if any MEDIUM, else `LOW`. `requires_approval = (count(HIGH) ≥ 2)`.
- **PPC source codes:** `source` = 1 Amazon · 2 eBay · 3 Google. Upsert identity keys listed in Section 3.
- **Stock pack logic:** for cable SKUs (`CL…5PK` / `APK`), when primary stock ≤ 5, derive units from base cable stock ÷ pack size (5 for 5PK, 10 for APK); combo availability = MIN across components.
- **Domain access:** allowed domains = `user.domain` + `user_domain_access` rows; admins bypass all domain checks.

### Canonical Vocabulary

| Term | Meaning |
| :---- | :---- |
| Centralizer | This app's role — consolidates external DBs into unified output |
| `ppc_etl` / `ppc_etl_performance_data` | Unified ETL output tables (on `mysql`) |
| connection | Which physical DB a model uses (`$connection`) — `mysql` / `orders` / `ppc` |
| app-owned vs external | Table created by a repo migration vs provisioned by another system |
| domain | A threshold ownership scope for non-admin access control (not a web domain) |
| `inventory_bool` | true = simple product, false = combo product |
| `record_type` | `campaign` / `ad_group` / `ad` in the ETL tables |
| business key | A natural key used for joins (`rule_id`, `threshold_id`, `campaign_id`) instead of `id` |

### Cross-project applicability

The **multi-connection + cross-database ETL upsert** pattern and the **impact-weighted approval workflow** are reusable for any project that consolidates other teams' databases or needs governed configuration changes (PPC, finance threshold systems). The **legacy-table adapter model** (accessors mapping new names to old columns) is reusable wherever a modern app sits on a legacy schema.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced? | ✅ YES |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (3–7)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment

A developer with no context could understand from this file alone:

- **WHAT** was done today — full database-layer audit; authored `DATABASE_SCHEMA.md` covering ~40 tables, all relationships, CRUD flows, the PPC ETL pipeline, auth/permissions, and all non-working code.
- **WHAT** the structure is — 3 live databases (`mysql` app-owned, `orders` + `ppc` external); most business tables have no migration; `ppc_etl` tables are the centralized output.
- **WHAT** is still broken — 6 missing controllers; approval doesn't apply values; unauthenticated stock route; broken jobs; no external-DB provisioning docs.
- **WHO** needs action — Dev team (controllers, approval apply-step, stock route, jobs); Team lead (external DB dumps/credentials).
- **WHY** the decisions were made — documented external tables from models (no migrations exist); flagged dead code instead of hiding it; no app code changed (scope = discovery).
- **WHERE** everything lives — repo `ledsone-centralizer`, branch `Abiraj`; reference doc `DATABASE_SCHEMA.md`; connections in `config/database.php`.
- **WHAT** to do next — commit `DATABASE_SCHEMA.md`; raise the 6 gaps; obtain external DB credentials/dumps to validate external table columns.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-06-11__abiraj__blos__REQ-04-D01.md`
- [x] Metadata complete — includes `blos_keys_used` and `hardcoded_thresholds`
- [x] Table inventory + connection inventory included in Section 3
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written
- [x] Evidence locations referenced (repo source files + `DATABASE_SCHEMA.md`)
- [x] ✅ **DELIVERED:** `DATABASE_SCHEMA.md` — full multi-DB schema, relationships, CRUD flows
- [x] ✅ **DOCUMENTED:** 3-database architecture and app-owned vs external tables
- [x] ✅ **DOCUMENTED:** PPC ETL pipeline and centralized output tables
- [x] ✅ **DOCUMENTED:** Threshold change/approval workflow + domain access model
- [x] ✅ **FLAGGED:** 6 missing controllers, 2 broken jobs, empty seeder
- [ ] ⚠️ **OPEN:** Implement or remove the 6 missing controllers (Dev team)
- [ ] ⚠️ **OPEN:** Add value-apply step to change-request approval (Dev team)
- [ ] ⚠️ **OPEN:** Move `warehouse-location-wise-stock-update` behind auth / CRON-only (Dev team)
- [ ] ⚠️ **OPEN:** Delete or restore the broken bulk jobs (Dev team)
- [ ] ⚠️ **OPEN:** Obtain external DB (`orders`, `ppc`) credentials + dumps for environment setup (Team lead)
- [ ] ⚠️ **OPEN:** Confirm whether eBay/Google performance ETL methods should be invoked (Dev team)
- [ ] ⚠️ **OPEN:** Commit `DATABASE_SCHEMA.md` and replace evidence path with commit hash

---
*DIGITWEB LK LTD — Daily Skill Increment System — v3.0 — June 2026*
