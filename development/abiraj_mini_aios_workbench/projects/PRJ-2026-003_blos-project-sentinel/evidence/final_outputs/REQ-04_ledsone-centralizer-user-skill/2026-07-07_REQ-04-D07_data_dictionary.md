# DATA DICTIONARY — ledsone-centralizer (BLOS scope deep, shared-repo brief)

| Field | Value |
|---|---|
| **Date** | 2026-07-07 |
| **Deliverable** | REQ-04-D07 |
| **Project** | PRJ-2026-003_blos-project-sentinel |
| **Status** | DRAFT |
| **Source repo** | `C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer` (read-only) |
| **Code state audited** | git HEAD `bc1204a` — "Drop redundant previous_value/change_reason from thresholds table" |
| **Primary sources** | `DATABASE_SCHEMA.md` (repo root, cross-checked — **partially stale**, see §4), `database/migrations/*` (7 files), `docs/sql/*.sql` (10 files), `app/Models/**` (52 models), `app/Http/Controllers/Api/ThresholdConfigurationController.php`, `UserController.php`, `app/Http/Controllers/auth/AuthController.php`, `app/Services/FolderFileService.php` |

> **How to read evidence tags:** `file:line` refers to the repo above. SQL evidence cites `docs/sql/<file>.sql`. Where the live DB column set comes from a SQL script rather than a Laravel migration, the script is the source of truth (most BLOS tables were created by privileged manual SQL, not `php artisan migrate` — see notes in each `docs/sql` header, e.g. `business_rules.sql` lines 32–33: web DB user lacks DROP/CREATE/ALTER, error #1142).

---

## 1. Summary of all tables

Legend: **DEEP** = every column documented below. **BRIEF** = shared-repo module, one-row summary only.

| # | Table | Module | Connection | Coverage | Defined by |
|---|---|---|---|---|---|
| 1 | `thresholds` | BLOS / Threshold Configuration | mysql | DEEP | `docs/sql/thresholds.sql` + `drop_threshold_snapshot_columns.sql` |
| 2 | `threshold_versions` | BLOS | mysql | DEEP | pre-existing; spec `docs/sql/threshold_versions.sql`; widened by `align_threshold_fk_columns.sql` |
| 3 | `business_rules` | BLOS | mysql | DEEP | `docs/sql/business_rules.sql` (+ `rename_business_rule_table.sql`) |
| 4 | `condition_logics` | BLOS | mysql | DEEP | `docs/sql/condition_logics.sql` |
| 5 | `glossary` | BLOS | mysql | DEEP | `docs/sql/glossary.sql` |
| 6 | `rule_threshold_mapping` | BLOS | mysql | DEEP | `docs/sql/rule_threshold_mapping.sql` |
| 7 | `threshold_change_requests` | BLOS (**orphaned** — model deleted) | mysql | DEEP | migration `2026_04_28_000001` |
| 8 | `business_rule_categorical_mapping` | BLOS (**legacy/retired** — model deleted) | mysql | DEEP (as-was) | DATABASE_SCHEMA.md §4.4 only — no model, no migration, no SQL script |
| 9 | `user_domain_access` | BLOS / domain scoping | mysql | DEEP | migration `2026_04_28_000002_create_user_domain_access_table` |
| 10 | `user` (legacy) | Auth / Users (shared, but BLOS depends on it) | mysql | DEEP | external table; `token` + `domain` columns added by repo migrations |
| 11 | `folders` | Central File Library | mysql | DEEP | migration `2026_05_01_000001` |
| 12 | `files` | Central File Library | mysql | DEEP | migration `2026_05_01_000001` |
| 13 | `products` | POS/Catalog | mysql | BRIEF | external (see `product` stub note, §3) |
| 14 | `categories` | POS/Catalog | mysql | BRIEF | external |
| 15 | `inventory` | POS/Catalog | mysql | BRIEF | external |
| 16 | `sales` | POS/Catalog | mysql | BRIEF | external |
| 17 | `sale_items` | POS/Catalog | mysql | BRIEF | external |
| 18 | `images` | POS/Catalog | mysql | BRIEF | external |
| 19 | `image_types` | POS/Catalog | mysql | BRIEF | external |
| 20 | `product` (stub) | POS/Catalog | mysql | BRIEF | migration `2023_01_17_081228` (id + timestamps only) |
| 21 | `websockets_statistics_entries` | Infrastructure | mysql | BRIEF | migration `0000_00_00_000000` |
| 22–28 | `inv_products`, `inv_stock`, `inv_product_combo`, `inv_product_mapping`, `product_pk`, `warehouse` (orders DB); `location_wise_inv_stock` (mysql) | Order-Management / Stock | orders / mysql | BRIEF | external |
| 29–31 | `tbl_region`, `states`, `market_places` | PPC reference | ppc | BRIEF | external |
| 32–33 | `ppc_etl`, `ppc_etl_performance_data` | PPC ETL output (core centralizer tables) | mysql | BRIEF | external |
| 34–40 | `seller_stores`, `store_market_places_dev`, `campaigns`, `ad_groups`, `ads`, `products` (Amazon), `performance_data` | PPC Amazon | ppc | BRIEF | external |
| 41–46 | `ebay_seller_stores_dev`, `ebay_campaigns`, `ebay_ad_groups`, `ebay_ads`, `ebay_performance_data`, `ebay_campaign_report_data` | PPC eBay | ppc | BRIEF | external |
| 47–54 | `google_accounts`, `google_campaigns`, `google_ad_groups`, `google_asset_groups`, `google_ad_asset_group_assets`, `google_ad_asset_group_performance`, `google_campaign_performance`, `google_product_performance` | PPC Google Ads | ppc | BRIEF | external |
| 55 | `threshold_dependencies` | BLOS (**ghost** — in docs/SQL only) | mysql | flagged §5 | DATABASE_SCHEMA.md §4.6 + `align_threshold_fk_columns.sql:13-14`; NO model, NO migration |

**ID format conventions (BLOS):** `TH-###` thresholds, `BL-###` business rules, `GL-###` glossary terms, `MAP-###` rule↔threshold mappings. All are `VARCHAR(20)` string business-code primary keys, supplied by the client and validated by regex (`ThresholdConfigurationController.php:145, 320, 379, 454`). Codes are normalized before validation — uppercased, all whitespace stripped — by `normalizeCodeFields()` (`ThresholdConfigurationController.php:118-129`). `condition_logics.condition_id` and `threshold_versions.version_id` are the two BLOS PKs that remain integer AUTO_INCREMENT (see their sections).

---

## 2. DEEP coverage — BLOS, File Library, legacy user

### 2.1 `thresholds`

- **Purpose:** master registry of every configurable business threshold value (the "T" in BLOS rules). Referenced by `TH-###` codes inside `condition_logics.condition_logic_by_ids` and joined by `rule_threshold_mapping`.
- **Model:** `app/Models/Threshold.php` — `$primaryKey='threshold_id'`, `$incrementing=false`, `$keyType='string'`, `$timestamps=false` (lines 12-19).
- **PK / convention:** `threshold_id VARCHAR(20)`, business code `TH-###` (`docs/sql/thresholds.sql:254`; regex `^TH-\d+$` at `ThresholdConfigurationController.php:454`).
- **Created by:** manual privileged SQL (`docs/sql/thresholds.sql` — `DROP TABLE IF EXISTS` + `CREATE`, replacing the old integer-PK thresholds table). Data loads: 7 rows (`thresholds.sql:284-293`), then 35-row replacement (`thresholds_data_load.sql:311-350`).
- **NO Laravel migration** creates this table. (Migration `2026_04_28_000002_add_domain_to_user_table.php` *alters* it — see lifecycle notes.)

| Column | Type (SQL) | Null | Meaning | Written by |
|---|---|---|---|---|
| `threshold_id` 🔑 | VARCHAR(20) | NO | Business code `TH-###` | client-supplied on create — `thresholdsStore` (`ThresholdConfigurationController.php:450-484`), bulk CSV import (`:1015-1120`) |
| `threshold_key` | VARCHAR(150), UNIQUE `uq_thresholds_key` | NO | Machine key (e.g. `amz_merch_led_uk_organic_ctr_floor_warning`); used as YAML export key (`exportYaml`, `:819-835`) | store/update/bulk |
| `label` | VARCHAR(150) | NO | Human display name | store/update/bulk |
| `description` | TEXT | YES | Long description | store/update/bulk |
| `alternative_names` | VARCHAR(255) | YES | Comma-separated synonyms; searched by `thresholdsIndex` LIKE filter (`:442`) | store/update/bulk |
| `value` | DECIMAL(15,2) | YES | **The live threshold value.** Cast `CompactDecimal` (model line 23; `app/Casts/CompactDecimal.php` strips trailing zeros on read) | store; `thresholdsUpdate` (`:486-553`) with version bump when changed |
| `value_type` | VARCHAR(20) | YES | e.g. `percentage`, `number`, `currency`, `ratio`, `Integer` (inconsistent casing present in seed data, `thresholds_data_load.sql`) | store/update/bulk |
| `unit` | VARCHAR(30) | YES | e.g. `%`, `days`, `£/order`, `grams` | store/update/bulk |
| `type` | VARCHAR(30) | YES | rule dimension, seed data all `common` | store/update/bulk |
| `fulfillment` | VARCHAR(30) | YES | e.g. `merchant` | store/update/bulk |
| `channel` | VARCHAR(30) | YES | e.g. `amazon`, `shopify` | store/update/bulk |
| `account` | VARCHAR(50) | YES | e.g. `ledsone` | store/update/bulk |
| `site` | VARCHAR(20) | YES | e.g. `uk` | store/update/bulk |
| `domain` | VARCHAR(100) | YES | **Access-scoping key** — non-admin users only see thresholds whose domain is in their allowed set (`applyThresholdDomainFilterForNonAdmin`, `:96-114`); distinct list served by `domainsIndex` (`:648-661`) | store/update; renamed in bulk by `domainsRename` (`:682-686`) |
| `owner` | VARCHAR(100) | YES | business owner name | store/update/bulk |
| `created_by` | VARCHAR(100) | YES | creator name (free text) | store/bulk |
| `created_at` | DATE | YES | creation date — cast `date` (model line 23). **Not** a Laravel timestamp (`$timestamps=false`) | store/bulk |
| `last_changed_by` | VARCHAR(100) | YES | stamped with authenticated user's name on value change (`:542-546`) | `thresholdsUpdate` |
| `last_changed_at` | DATETIME | YES | UTC stamp on value change (`:547`) — cast `datetime` | `thresholdsUpdate` |
| `version` | INT NOT NULL DEFAULT 1 | NO | current version counter — see increment logic below | `thresholdsUpdate` (`:541`) |
| `status` | VARCHAR(20) NOT NULL DEFAULT 'active' | NO | `active` etc.; filterable (`:433-435`) | store/update/bulk |
| `effective_from` | DATE | YES | date the value takes effect — cast `date` | store/update/bulk |
| `approver` | VARCHAR(100) | YES | e.g. `TL` | store/update/bulk |
| `management_approval` | VARCHAR(20) | YES | e.g. `Pending` / `approved` | store/update/bulk |

**Dropped columns (2026-06-19, `docs/sql/drop_threshold_snapshot_columns.sql`, commit `bc1204a`):** `previous_value DECIMAL(15,4)` and `change_reason VARCHAR(255)` were removed because they only mirrored the latest `threshold_versions` row; `threshold_versions` is now the single source of change history (script header lines 109-126). The user-typed reason is still captured, but written **only** to `threshold_versions.change_reason` (`ThresholdConfigurationController.php:513, 526-529, 550`).

**`version` increment logic (verify-critical):** on a value change, `thresholdsUpdate` computes `nextVn = max((int)$row->version, max(version_number in threshold_versions for this threshold)) + 1` (`:539-541`), writes it to `thresholds.version` (`:541`) and to the new `threshold_versions.version_number` (`:550`) — this self-heals if the two counters ever diverge. "Value changed" means `abs(new - old) > 0.0000001` (`:531`). If the value did **not** change, a plain update runs with **no** version bump and no version row (`:533-536`).

- **Relationships:** `hasMany ThresholdVersion` (`threshold_id`→`threshold_id`, model :25-28); `hasMany RuleThresholdMapping` (:30-33). No DB-enforced FKs.
- **Lifecycle:** rows deleted via `thresholdsDestroy` (`:555-568`) — inside one transaction it **deletes all `threshold_versions` and `rule_threshold_mapping` rows for that threshold, then the threshold** (application-level cascade; no DB FK). Domain-guarded: non-admins can only update/delete thresholds in their allowed domains (`:490-492, 558-561`).
- **Residual drift:** migration `2026_04_28_000002_add_domain_to_user_table.php` also added `thresholds.proposed_value DECIMAL(10,4) ... AFTER previous_value`. The rebuilt `thresholds.sql` table has **neither** `proposed_value` nor `previous_value`, and the model `$fillable` (Threshold.php:21) lists neither. Re-running that migration on a fresh DB will fail (positions after a dropped column) — flagged in §5.

### 2.2 `threshold_versions`

- **Purpose:** audit log of threshold value changes — one row per applied change; the **single source of truth for change history** after the 2026-06-19 snapshot-column drop (`drop_threshold_snapshot_columns.sql:112-117`).
- **Model:** `app/Models/ThresholdVersion.php` — PK `version_id`, `$incrementing=true`, int, `$timestamps=false` (lines 12-18).
- **Created by:** pre-existing on the server (`docs/sql/threshold_versions.sql` header lines 209-215: "ALREADY EXISTS ... IF NOT EXISTS makes it a safe no-op"); `threshold_id` widened INT→VARCHAR(20) by `align_threshold_fk_columns.sql:10-11`.

| Column | Type (SQL) | Null | Meaning | Written by |
|---|---|---|---|---|
| `version_id` 🔑 | INT UNSIGNED AUTO_INCREMENT | NO | surrogate PK (integer, **not** a business code) | DB |
| `threshold_id` | VARCHAR(20), KEY `idx_tv_threshold` | NO | → `thresholds.threshold_id` (`TH-###`); FK commented out in DDL (`threshold_versions.sql:234-235`) | all writers |
| `old_value` | DECIMAL(15,4) | YES | value before change — cast `CompactDecimal` (model :22) | `thresholdsUpdate` auto-log (`ThresholdConfigurationController.php:550`); manual `versionsStore` (`:579-601`) |
| `new_value` | DECIMAL(15,4) | YES | value after change — cast `CompactDecimal` | same |
| `changed_by` | VARCHAR(100) | YES | authenticated user's name, fallback `'Unknown'` (`:542-545`) | same |
| `approved_by` | VARCHAR(100) | YES | always `NULL` from the auto-log path (`:550`); only fillable via manual endpoints / CSV | `versionsStore/Update`, bulk import |
| `change_reason` | TEXT | YES | user-typed reason, captured from the threshold edit form (input-only field, `:513-516, 528`) | `thresholdsUpdate` (`:550`), manual endpoints |
| `timestamp` | DATETIME | YES | UTC change time; `versionsStore` defaults it to `now()` when omitted (`:596-598`) — cast `datetime` | same |
| `version_number` | INT | YES | monotonically increasing per threshold (see §2.1 increment logic) | same |

- **Append-only? Verified nuance:** the *design intent* is an immutable, append-only log (SQL header; drop-columns rationale). The auto-log insert happens inside the **same DB transaction** as the threshold update (`:548-551`), so a version row is written iff the value change lands. **However** the code also exposes admin CRUD that violates strict append-only: `versionsUpdate` (`:603-622`) and `versionsDestroy` (`:624-628`) can rewrite/delete history, and `thresholdsDestroy` wipes a threshold's whole history (`:563`). The bulk CSV `versions` tab is insert-only (`'auto' => true` strips the PK — `:899, 1053-1055`).
- **Relationships:** `belongsTo Threshold` (model :24-27).

### 2.3 `business_rules`

- **Purpose:** master list of BLOS business rules (e.g. BL-001 "CTR Collapse"); parent of `condition_logics` and `rule_threshold_mapping`.
- **Model:** `app/Models/BusinessRule.php` — PK `rule_id`, string, non-incrementing, `$timestamps=false` (lines 11-18).
- **Created by:** manual SQL `docs/sql/business_rules.sql:34-46`. History: the *old* `business_rules` table (documented in DATABASE_SCHEMA.md §4.3 with int `id` + business key `rule_id` like `R001`) was **deleted**; on the live server the new table was created as `business_rule_table` and then renamed via `docs/sql/rename_business_rule_table.sql:169` (`RENAME TABLE business_rule_table TO business_rules`). The SQL script creates it directly under the final name for fresh DBs (header lines 24-27).

| Column | Type (SQL) | Null | Meaning | Written by |
|---|---|---|---|---|
| `rule_id` 🔑 | VARCHAR(20) | NO | Business code `BL-###` (regex `^BL-\d+$`, `ThresholdConfigurationController.php:145`) | `businessRulesStore` (`:156-166`), bulk import |
| `rule_name` | VARCHAR(150) | NO | rule title | store/update (`:168-178`)/bulk |
| `description` | TEXT | YES | what the rule detects | same |
| `domain` | VARCHAR(100), KEY `idx_br_domain` | YES | owning domain (e.g. "Organic Listing Performance") | same |
| `status` | VARCHAR(20), KEY `idx_br_status` | YES | e.g. `Active` | same |
| `owner` | VARCHAR(100) | YES | business owner | same |
| `created_by` | VARCHAR(100) | YES | creator | same |
| `created_at` | DATE | YES | cast `date` (model :22); not a Laravel timestamp | same |

- **Relationships:** `hasMany ConditionLogic` and `hasMany RuleThresholdMapping`, both on `rule_id`→`rule_id` (model :24-32).
- **Lifecycle:** **guarded delete** — `businessRulesDestroy` refuses (HTTP 422) while any `rule_threshold_mapping` or `condition_logics` row still references the `rule_id` (`ThresholdConfigurationController.php:180-192`). No DB FK enforcement.

### 2.4 `condition_logics`

- **Purpose:** per-stage IF/THEN logic of each business rule (stages `initial` / `restore` / `kill`), expressed in glossary + threshold codes; the data behind the drag-and-drop Rule Builder (`resources/js/Account/Pages/RuleBuilder.vue`).
- **Model:** `app/Models/ConditionLogic.php` — PK `condition_id`, **int AUTO_INCREMENT** (the only BLOS master table without a string code PK; kept integer to match the source Excel — `docs/sql/condition_logics.sql:61-62`), `$timestamps=false`.
- **Created by:** manual SQL `docs/sql/condition_logics.sql:67-90` (17 columns; seeded with 3 rows for BL-001).

| Column | Type (SQL) | Null | Meaning | Written by |
|---|---|---|---|---|
| `condition_id` 🔑 | INT UNSIGNED AUTO_INCREMENT | NO | surrogate PK (sheet values 1..3) | DB |
| `rule_id` | VARCHAR(20), KEY `idx_cl_rule` | NO | → `business_rules.rule_id` (`BL-###`); FK commented out in DDL (:88-89) | `conditionLogicsStore` (`ThresholdConfigurationController.php:264-277`), update (`:279-293`), bulk |
| `condition_logic_by_ids` | TEXT | YES | machine-readable logic, e.g. `IF GL-001 < TH-001 AND GL-002 >= TH-002` — **every `GL-`/`TH-` code is validated to exist** in `glossary`/`thresholds` before save (`unknownConditionCodes`, `:233-262`, enforced at `:271-274, 287-290, 1078-1087`) | same |
| `condition_logic_rule` | TEXT | YES | human-readable version (empty in source sheet) | same |
| `decision_output` | TEXT | YES | action taken when condition matches | same |
| `stage` | VARCHAR(30), KEY `idx_cl_stage` | YES | `initial` / `restore` / `kill` | same |
| `stage_description` | TEXT | YES | prose description of the stage trigger | same |
| `level` | VARCHAR(50) | YES | e.g. `sku` | same |
| `type` | VARCHAR(30) | YES | e.g. `organic` | same |
| `fulfillment` | VARCHAR(30) | YES | e.g. `merchant` | same |
| `channel` | VARCHAR(30) | YES | e.g. `amazon` | same |
| `account` | VARCHAR(50) | YES | e.g. `ledsone` | same |
| `site` | VARCHAR(20) | YES | e.g. `uk` | same |
| `status` | VARCHAR(20) | YES | e.g. `Active` | same |
| `owner` | VARCHAR(100) | YES | business owner | same |
| `created_by` | VARCHAR(100) | YES | creator | same |
| `created_at` | DATE | YES | cast `date` (model :21) | same |

- **Relationships:** `belongsTo BusinessRule` (model :23-26).
- **Lifecycle:** free delete per row (`conditionLogicsDestroy`, `:295-299`); rows block deletion of their parent business rule (§2.3). Bulk CSV import is insert-only for this tab (auto PK stripped, `:898, 1053-1055`). **Note:** glossary/threshold codes are validated only at write time — deleting a glossary term or threshold later does *not* touch existing logic strings (dangling-code risk; threshold deletion at least clears `rule_threshold_mapping` but not `condition_logic_by_ids`).

### 2.5 `glossary`

- **Purpose:** dictionary of metric/term codes (`GL-###`) referenced inside condition logic expressions (e.g. GL-001 = `organic_ctr`).
- **Model:** `app/Models/Glossary.php` — PK `glossary_id`, string, non-incrementing, `$timestamps=false` (lines 11-18). No relationships defined.
- **Created by:** manual SQL `docs/sql/glossary.sql:141-149` (5 columns, seeded GL-001..GL-003).

| Column | Type (SQL) | Null | Meaning | Written by |
|---|---|---|---|---|
| `glossary_id` 🔑 | VARCHAR(20) | NO | Business code `GL-###` (regex `^GL-\d+$`, `ThresholdConfigurationController.php:379`) | `glossaryStore` (`:387-396`), bulk import |
| `term` | VARCHAR(150), KEY `idx_glossary_term` | NO | canonical metric name, e.g. `organic_ctr` | store/update (`:398-408`)/bulk |
| `type` | VARCHAR(30) | YES | data type of the metric, e.g. `decimal`, `integer` | same |
| `definition` | TEXT | YES | prose definition | same |
| `alternative_names` | VARCHAR(255) | YES | comma-separated synonyms; searched by `glossaryIndex` LIKE filter (`:363-368`) | same |

- **Lifecycle:** unguarded delete (`glossaryDestroy`, `:410-414`) — existing `condition_logics` rows that reference the deleted `GL-` code are **not** checked (validation is write-time only, §2.4).

### 2.6 `rule_threshold_mapping`

- **Purpose:** junction table linking business rules to the thresholds they consume (`BL-###` ↔ `TH-###`). Replaces the retired `business_rule_categorical_mapping` linkage (§2.8).
- **Model:** `app/Models/RuleThresholdMapping.php` — PK `mapping_id`, string, non-incrementing, `$timestamps=false` (lines 11-18).
- **Created by:** manual SQL `docs/sql/rule_threshold_mapping.sql:182-192` (seeded MAP-001..MAP-005, all BL-001).

| Column | Type (SQL) | Null | Meaning | Written by |
|---|---|---|---|---|
| `mapping_id` 🔑 | VARCHAR(20) | NO | Business code `MAP-###` (regex `^MAP-\d+$`, `ThresholdConfigurationController.php:320`) | `ruleThresholdMappingsStore` (`:328-337`), bulk import |
| `rule_id` | VARCHAR(20), KEY `idx_rtm_rule` | NO | → `business_rules.rule_id` (`BL-###`) | store/update (`:339-349`)/bulk |
| `threshold_id` | VARCHAR(20), KEY `idx_rtm_threshold` | NO | → `thresholds.threshold_id` (`TH-###`) | same |
| `created_by` | VARCHAR(100) | YES | creator | same |
| `created_at` | DATETIME | YES | cast `datetime` (model :22) | same |

- **Constraints:** `UNIQUE uq_rule_threshold (rule_id, threshold_id)` (`rule_threshold_mapping.sql:189`) — a rule can map a given threshold once.
- **Lifecycle:** direct delete (`:351-355`); rows are also **cascade-deleted in code** when their threshold is deleted (`thresholdsDestroy`, `:564`); their existence **blocks** deletion of the parent business rule (`:184-186`). No DB FKs.

### 2.7 `threshold_change_requests` — **ORPHANED TABLE**

- **Purpose (as designed):** approval queue for high-impact threshold changes (created when a change required approval; approve/reject flipped `status`). Described in DATABASE_SCHEMA.md §4.8 and §5.3.
- **Current status at HEAD `bc1204a`: the model (`App\Models\ThresholdChangeRequest`) and its companion `ThresholdDependency` have been DELETED from `app/Models/`, and zero references remain anywhere in `app/`** (verified by repo-wide grep for `ThresholdChangeRequest|threshold_change_requests`). The approval workflow was removed along with the dependency-impact logic. The table still exists (migration is live) but nothing reads or writes it.
- **Defined by:** migration `database/migrations/2026_04_28_000001_create_threshold_change_requests_table.php`; `threshold_id` later widened INT→`VARCHAR(20)` by `docs/sql/align_threshold_fk_columns.sql:16-17` to match the new string threshold PK.

| Column | Type (migration) | Null | Meaning |
|---|---|---|---|
| `id` 🔑 | BIGINT UNSIGNED AUTO_INCREMENT (`$table->id()`) | NO | surrogate PK |
| `threshold_id` | declared `unsignedBigInteger`; **live DB: VARCHAR(20)** after `align_threshold_fk_columns.sql` | NO | → `thresholds.threshold_id` |
| `old_value` | DECIMAL(18,6) | YES | value at request time |
| `new_value` | DECIMAL(18,6) | YES | proposed value |
| `effective_from` | DATE | YES | requested effective date |
| `requested_by` | VARCHAR(100) | YES | requester name |
| `requested_at` | TIMESTAMP | YES | request time |
| `approved_by` | VARCHAR(100) | YES | approver name |
| `approved_at` | TIMESTAMP | YES | decision time |
| `status` | VARCHAR(40) **DEFAULT 'pending'** | NO | `pending` / `approved` / `rejected` |
| `change_reason` | TEXT | YES | requester's reason |
| `high_count` / `medium_count` / `low_count` | UNSIGNED INT, DEFAULT 0 each | NO | snapshot of dependency impact counts at request time |
| `impact_snapshot` | JSON (was cast `array` in the deleted model) | YES | `{overall_impact, systems[]}` snapshot |
| `created_at` / `updated_at` | TIMESTAMP | YES | Laravel timestamps |
| — | INDEX (`threshold_id`, `status`) | | |

- **Lifecycle:** effectively frozen — any rows are historical. DATABASE_SCHEMA.md's known gap ("approval does not write the value back", §5.3/§8) is now moot: the entire flow is gone; `thresholdsUpdate` always applies changes directly with a `threshold_versions` log.

### 2.8 `business_rule_categorical_mapping` — **LEGACY / RETIRED**

- **Purpose (as-was):** category-dimensioned mapping between the *old* business_rules and thresholds, with decision outputs (`decision_output`/`decision_restore`, `decision_kill`, `rationale`, `business_owner`) and dual-cased dimension columns (`Level`/`level`, `Type`/`type`, `Fulfillment`/`fulfillment`, `Channel`/`channel`) that the old controller probed at runtime via `Schema::getColumnListing` (DATABASE_SCHEMA.md §4.4).
- **Current status:** the model (`App\Models\BusinessRuleCategoricalMapping`) is **deleted**; no references in `app/`; no migration and no `docs/sql` script ever covered it. Its role is superseded by `condition_logics` (stage logic + dimensions + decisions) plus `rule_threshold_mapping` (rule↔threshold links). Documented per-column detail exists **only** in DATABASE_SCHEMA.md §4.4 (columns: `id` PK, `rule_id`, `condition_logic`, `decision_output`/`decision_restore`, `decision_kill`, `rationale`, `business_owner`, dual-case `Level/Type/Fulfillment/Channel`, `created_by`). If the physical table still exists in the DB it is dead weight; treat DATABASE_SCHEMA.md §4.4 as historical.

### 2.9 `user_domain_access`

- **Purpose:** grants a non-admin user access to threshold domains beyond their home `user.domain`. Allowed set = home domain + these rows, deduplicated case-insensitively (`allowedDomainsFor`, `ThresholdConfigurationController.php:45-77`). Admins bypass all domain filters (`:47-49, 81-83`).
- **Model:** `app/Models/UserDomainAccess.php`. Default PK `id`, Laravel timestamps on.
- **Defined by:** migration `database/migrations/2026_04_28_000002_create_user_domain_access_table.php`.

| Column | Type (migration) | Null | Meaning | Written by |
|---|---|---|---|---|
| `id` 🔑 | BIGINT UNSIGNED AUTO_INCREMENT | NO | surrogate PK | DB |
| `user` | UNSIGNED INT | NO | → `user.user` (logical FK, not DB-enforced) | `domainAccessReplace` (`ThresholdConfigurationController.php:743-773`), `domainAccessAdd` (`:775-800`) — both write via `$user->userDomainAccess()->create(...)` |
| `domain` | VARCHAR(100) | NO | granted domain name | same; bulk-renamed by `domainsRename` (`:684`) |
| `created_at` / `updated_at` | TIMESTAMP | YES | Laravel timestamps | Eloquent |
| — | UNIQUE(`user`,`domain`); INDEX(`user`); INDEX(`domain`) | | | |

- **`userFkColumn()` dual-name handling (verify-critical):** the model tolerates two environments — the FK column may be named `user` **or** `user_id`. `UserDomainAccess::userFkColumn()` (model lines 16-30) probes `Schema::hasColumn($table,'user')`, then `'user_id'`, defaults to `'user'`, and **caches the answer in a static** for the process. Both names are in `$fillable` (line 12). Every consumer goes through it: the `User::userDomainAccess()` relationship FK (`app/Models/User.php:130`), listing/ordering (`ThresholdConfigurationController.php:696-699, 707-708`), and `assignedUserId()` (model :32-35).
- **Lifecycle:** `domainAccessReplace` is destructive replace — deletes **all** of the user's rows then recreates from the payload, in a transaction (`:761-766`). `domainAccessRemove` deletes one (user, domain) pair (`:802-817`). No cascade from `user` deletion (no code path deletes users).

### 2.10 `user` (legacy table)

- **Purpose:** authentication + authorization principal. Pre-existing company table with **legacy column names**; the app adapts it via accessor/mutator mappings.
- **Models:** primary adapter `app/Models/User.php` (table `user`, PK `user`, int auto-inc, lines 12-18); legacy raw model `app/Models/auth/User.php` (same table, `$fillable` uses physical names — note it lists `user_role` at line 20 although the adapter maps role to `config_role`, a fillable-list drift; the auth model appears vestigial).
- **Defined by:** external (no create migration). Two repo migrations alter it: `2025_03_15_000001_add_token_to_users_table.php` (adds `token`) and `2026_04_28_000002_add_domain_to_user_table.php` (adds `domain`).

| Physical column | Type | Null | Virtual accessor (app/Models/User.php) | Meaning / write path |
|---|---|---|---|---|
| `user` 🔑 | INT AUTO_INCREMENT | NO | `id` (getter :34-37); auth identifier name (`getAuthIdentifierName`, :24-27) | PK |
| `user_firstname` | string | ? | `name` getter joins first+last, falls back to `user_name` (:39-48); `name` setter writes the whole value into `user_firstname` and blanks `user_lastname` (:50-55) | `UserController@store/update` (`Api/UserController.php:42, 71`), `AuthController@register` (`auth/AuthController.php:119-127`) |
| `user_lastname` | string | ? | part of `name` | blanked by the `name` mutator |
| `user_name` | string | ? | fallback for `name` (:47) | read-only fallback |
| `user_email` | string | NO | `email` (:57-65) — login lookup key (`AuthController.php:46`); uniqueness validated against `user,user_email` (`UserController.php:33, 61`) | UserController, AuthController register |
| `user_password` | string (bcrypt hash) | NO | `password_hash` (:67-75); `getAuthPassword()` (:29-32); hidden from JSON (:22) | `Hash::make()` in `UserController.php:38, 68` and `AuthController.php:122` |
| `config_role` | string | ? | `role` (:77-89) — normalized lowercase; returns `admin`/`cashier` as-is, any other non-empty value passthrough, empty → `'cashier'`. Validated set on write: `admin,cashier,domain_owner` (`UserController.php:35, 63`) | UserController, AuthController register (default `cashier`, `AuthController.php:123`) |
| `user_status` | string | ? | `is_active` (:91-103) — NULL/'' treated **active**; truthy set `active/1/yes/true/enabled`; setter writes literal `'active'`/`'inactive'` | UserController (`is_active=true` on create, :41), AuthController |
| `user_accounts` | string | ? | none — defaulted to `'list'` on create by `booted()` hook (:114-121) | model hook |
| `token` | VARCHAR(60) | YES | mutator truncates to **32 chars** (:105-112); hidden from JSON. Bearer auth: `CheckAuthMiddleware` matches `Authorization: Bearer <token>` to this column | login writes `Str::random(32)` (`AuthController.php:55-57`); register (`:125`); logout nulls it (`:183-184`). Added by migration `2025_03_15_000001` |
| `domain` | VARCHAR(100) | YES | none (read raw; also probes `user_domain` as alternate name in `allowedDomainsFor`, `ThresholdConfigurationController.php:61`) | home threshold domain; UserController store/update. Added by migration `2026_04_28_000002_add_domain_to_user_table` |
| `created_at`/`updated_at` | TIMESTAMP | YES | Laravel timestamps active (adapter model does not disable them) | Eloquent |

- **Relationships:** `hasMany Sale` (`sales.user_id`→`user.user`, User.php:123-126); `hasMany UserDomainAccess` (FK via `userFkColumn()`, :128-131).
- **Lifecycle:** no delete endpoint in the API; users are deactivated via `is_active`.

### 2.11 `folders` (Central File Library)

- **Purpose:** self-referential folder tree for the file library; `path` is a materialized path kept in sync on rename/move.
- **Model:** `app/Models/Folder.php` (default `id` PK, timestamps on). Relationships: `parent` belongsTo self, `children`/`allChildren` hasMany self (recursive eager-load with files), `files` hasMany ManagedFile (lines 11-29).
- **Defined by:** migration `database/migrations/2026_05_01_000001_create_folders_and_managed_files_tables.php`.

| Column | Type (migration) | Null | Meaning | Written by (`app/Services/FolderFileService.php`) |
|---|---|---|---|---|
| `id` 🔑 | BIGINT UNSIGNED AUTO_INCREMENT | NO | PK | DB |
| `name` | VARCHAR(255) | NO | display name | create `:103`; rename `:147` |
| `slug` | VARCHAR(255) | NO | slugified name | `:103, :147` |
| `path` | VARCHAR(255) | NO | materialized path; descendants re-pathed on rename (`:113-115`) | `:103, :115, :147` |
| `parent_id` | BIGINT UNSIGNED, **FK → folders.id, `cascadeOnDelete`** | YES | parent folder (NULL = root) | `:103` |
| `created_at`/`updated_at` | TIMESTAMP | YES | Laravel timestamps | Eloquent |

- **Lifecycle:** deleting a folder (`FolderFileService.php:157` via `FolderFileController@destroyFolder`, admin-only route) relies on the **DB-level cascade** to remove child folders and files rows; physical files on disk are removed by the service. This is one of only two BLOS-adjacent tables with real DB foreign keys.

### 2.12 `files` (model `ManagedFile`)

- **Purpose:** metadata for each stored file (physical bytes live on the Flysystem disk; S3 driver installed).
- **Model:** `app/Models/ManagedFile.php` — `$table='files'` (line 17), default `id` PK, timestamps on; `belongsTo Folder` (:25-31).
- **Defined by:** same migration as folders.

| Column | Type (migration) | Null | Meaning | Written by (`app/Services/FolderFileService.php`) |
|---|---|---|---|---|
| `id` 🔑 | BIGINT UNSIGNED AUTO_INCREMENT | NO | PK | DB |
| `folder_id` | BIGINT UNSIGNED, **FK → folders.id, `cascadeOnDelete`** | NO | owning folder | upload `:182`; move `:259` |
| `name` | VARCHAR(255) | NO | display name | upload `:182`; rename `:244` |
| `filename` | VARCHAR(255) | NO | stored filename | upload; rename `:244` |
| `file_path` | VARCHAR(255) | NO | path on disk/S3 | upload `:182`; reupload `:210`; rename `:244`; move `:259`; self-heal fixups `:48, :56, :142` |
| `mime_type` | VARCHAR(255) | YES | MIME type | upload/reupload |
| `extension` | VARCHAR(255) | YES | file extension | upload/reupload |
| `size` | BIGINT UNSIGNED | YES | bytes | upload/reupload |
| `created_at`/`updated_at` | TIMESTAMP | YES | Laravel timestamps | Eloquent |

- **Lifecycle:** row + physical file deleted together (`:267-269`); rows also die via the folder FK cascade. Reupload deletes the old physical file first (`:198`).

---

## 3. BRIEF coverage — shared-repo modules (NOT BLOS scope)

| Table | Purpose | Owning module | Scope note |
|---|---|---|---|
| `products` | product catalog (name, sku, price, cost_price, category_id, is_active) — `app/Models/Product.php` | POS/Catalog | Shared-repo module — NOT BLOS scope |
| `product` | stub created by migration `2023_01_17_081228` — **id + timestamps only**; the `Product` model's implicit table is `products`, so this singular stub is unused/dead | POS/Catalog | Shared-repo module — NOT BLOS scope |
| `categories` | product categories (name, slug, is_active) — `app/Models/Category.php` | POS/Catalog | Shared-repo module — NOT BLOS scope |
| `inventory` | per-product stock qty + low_stock_threshold — `app/Models/Inventory.php` (only `updated_at`) | POS/Catalog | Shared-repo module — NOT BLOS scope |
| `sales` | sale headers (user_id → user.user, invoice_number, totals, payment_method, status) — `app/Models/Sale.php` | POS/Catalog | Shared-repo module — NOT BLOS scope |
| `sale_items` | sale line items (sale_id, product_id, qty, unit_price, subtotal) — `app/Models/SaleItem.php` | POS/Catalog | Shared-repo module — NOT BLOS scope |
| `images` | polymorphic images via custom morph columns `entity_type`/`entity_id` — `app/Models/Image.php` | POS/Catalog | Shared-repo module — NOT BLOS scope |
| `image_types` | image slot types (`product_main`, `category_main`) — `app/Models/ImageType.php` | POS/Catalog | Shared-repo module — NOT BLOS scope |
| `websockets_statistics_entries` | beyondcode/laravel-websockets dashboard stats — migration `0000_00_00_000000` | Infrastructure | Shared-repo module — NOT BLOS scope |
| `inv_products` | order-management product master (sku, inventory_bool simple/combo) — `app/Models/Inventory/InvProducts.php`, connection **orders** | Order-Management / Stock | Shared-repo module — NOT BLOS scope |
| `inv_stock` | per-warehouse stock rows (quantity, reserved_quantity, location) — `InvStock.php`, **orders** | Order-Management / Stock | Shared-repo module — NOT BLOS scope |
| `inv_product_combo` | combo-product components (pack_count → product_pk) — `InvProductCombo.php`, **orders** | Order-Management / Stock | Shared-repo module — NOT BLOS scope |
| `inv_product_mapping` | alternative product/stock substitution map — `InvProductMapping.php`, **orders** | Order-Management / Stock | Shared-repo module — NOT BLOS scope |
| `product_pk` | pack-size lookup (ppk_char/ppk_val) — `ProductPK.php`, **orders** | Order-Management / Stock | Shared-repo module — NOT BLOS scope |
| `warehouse` | warehouse master (PK `warehouse`) — `Warehouse.php`, **orders** | Order-Management / Stock | Shared-repo module — NOT BLOS scope |
| `location_wise_inv_stock` | computed location-aware available stock per SKU; write target of `StockController@WarehouseLocationWiseStockUpdate` — `LocationWiseStock.php`, connection **mysql** | Order-Management / Stock | Shared-repo module — NOT BLOS scope |
| `tbl_region` | PPC region/API reference — `CentralizedEtlData/Ppc/Common/Region.php`, connection **ppc** | PPC / Advertising ETL | Shared-repo module — NOT BLOS scope |
| `states` | campaign/ad state lookup — `Common/States.php`, **ppc** | PPC ETL | Shared-repo module — NOT BLOS scope |
| `market_places` | marketplace reference (regionId, countryCode, currency) — `Common/MarketPlaces.php`, **ppc** | PPC ETL | Shared-repo module — NOT BLOS scope |
| `ppc_etl` | **centralized ETL output**: unified campaign/ad-group metadata, upserted by console command `PpcEtlData` — `Common/PpcEtl.php`, connection **mysql** (default) | PPC ETL | Shared-repo module — NOT BLOS scope |
| `ppc_etl_performance_data` | centralized daily ad metrics (impressions/clicks/spend/sales/orders), upsert target — `Common/PpcEtlPerformanceData.php`, **mysql** | PPC ETL | Shared-repo module — NOT BLOS scope |
| `seller_stores` | Amazon seller stores — `Amazon/AmazonSellerStores.php`, **ppc** | PPC Amazon | Shared-repo module — NOT BLOS scope |
| `store_market_places_dev` | Amazon store↔marketplace link — `Amazon/AmazonStoreMarketPlacesDev.php`, **ppc** | PPC Amazon | Shared-repo module — NOT BLOS scope |
| `campaigns` | Amazon campaigns — `Amazon/AmazonCampaigns.php`, **ppc** | PPC Amazon | Shared-repo module — NOT BLOS scope |
| `ad_groups` | Amazon ad groups — `Amazon/AmazonAdGroups.php`, **ppc** | PPC Amazon | Shared-repo module — NOT BLOS scope |
| `ads` | Amazon ads — `Amazon/AmazonAds.php`, **ppc** | PPC Amazon | Shared-repo module — NOT BLOS scope |
| `products` (Amazon, ppc DB) | Amazon advertised products (amzSKU/amzASIN) — `Amazon/AmazonProducts.php`, **ppc** (same name as the mysql catalog table but a different DB) | PPC Amazon | Shared-repo module — NOT BLOS scope |
| `performance_data` | Amazon ad-level daily metrics — `Amazon/AmazonPerformanceData.php`, **ppc** | PPC Amazon | Shared-repo module — NOT BLOS scope |
| `ebay_seller_stores_dev` | eBay stores — `Ebay/EbaySellerStores.php`, **ppc** | PPC eBay | Shared-repo module — NOT BLOS scope |
| `ebay_campaigns` | eBay campaigns — `Ebay/EbayCampaigns.php`, **ppc** | PPC eBay | Shared-repo module — NOT BLOS scope |
| `ebay_ad_groups` | eBay ad groups — `Ebay/EbayAdGroups.php`, **ppc** | PPC eBay | Shared-repo module — NOT BLOS scope |
| `ebay_ads` | eBay ads — `Ebay/EbayAds.php`, **ppc** | PPC eBay | Shared-repo module — NOT BLOS scope |
| `ebay_performance_data` | eBay ad performance — `Ebay/EbayPerformanceData.php`, **ppc** | PPC eBay | Shared-repo module — NOT BLOS scope |
| `ebay_campaign_report_data` | eBay campaign daily report — `Ebay/EbayCampaignReportData.php`, **ppc** | PPC eBay | Shared-repo module — NOT BLOS scope |
| `google_accounts` | Google Ads accounts — `GoogleAds/GoogleAccounts.php`, **ppc** | PPC Google | Shared-repo module — NOT BLOS scope |
| `google_campaigns` | Google campaigns — `GoogleAds/GoogleCampaigns.php`, **ppc** | PPC Google | Shared-repo module — NOT BLOS scope |
| `google_ad_groups` | Google ad groups — `GoogleAds/GoogleAdGroups.php`, **ppc** | PPC Google | Shared-repo module — NOT BLOS scope |
| `google_asset_groups` | Google asset groups — `GoogleAds/GoogleAssetGroups.php`, **ppc** | PPC Google | Shared-repo module — NOT BLOS scope |
| `google_ad_asset_group_assets` | asset-group assets — `GoogleAds/GoogleAssetGroupsAssets.php`, **ppc** | PPC Google | Shared-repo module — NOT BLOS scope |
| `google_ad_asset_group_performance` | asset performance — `GoogleAds/GoogleAssetsPerformance.php`, **ppc** | PPC Google | Shared-repo module — NOT BLOS scope |
| `google_campaign_performance` | campaign daily metrics — `GoogleAds/GoogleCampaignPerformance.php`, **ppc** | PPC Google | Shared-repo module — NOT BLOS scope |
| `google_product_performance` | product-level metrics — `GoogleAds/GoogleProductPerformance.php`, **ppc** | PPC Google | Shared-repo module — NOT BLOS scope |

> Housekeeping note: `app/Models/Ppc/` exists but contains only **empty** `Amazon/` and `Common/` directories (no PHP files) — leftover scaffolding; all live PPC models are under `app/Models/CentralizedEtlData/Ppc/`.

---

## 4. Verified special cases (code + SQL cross-check)

1. **`thresholds.version` increment** — `nextVn = max(thresholds.version, MAX(threshold_versions.version_number)) + 1`, written to both tables atomically (`ThresholdConfigurationController.php:539-551`). Only fires when the numeric value changes by more than 1e-7 (`:531`).
2. **`threshold_versions` append-only** — append-only *by design and by the primary write path* (transactional insert alongside the threshold update), but **not enforced**: admin `versionsUpdate`/`versionsDestroy` endpoints exist (`:603-628`) and `thresholdsDestroy` deletes a threshold's entire version history (`:563`).
3. **2026-06-19 snapshot-column drop** — `docs/sql/drop_threshold_snapshot_columns.sql` removed `thresholds.previous_value` and `thresholds.change_reason` (commit `bc1204a`). `change_reason` is now an input-only request field logged to `threshold_versions.change_reason` (`:513-516, 526-529, 550`). Its validation was **temporarily relaxed** from `required|min:10` to `nullable` (comment at `:514-516`).
4. **Legacy `user` columns + accessors** — physical `user_email`, `user_password`, `config_role`, `user_status`, `token`, `domain` ↔ virtual `email`, `password_hash`, `role`, `is_active` (`app/Models/User.php:57-112`); `token` truncated to 32 chars by the mutator despite the VARCHAR(60) column.
5. **`user_domain_access.userFkColumn()`** — runtime probe of `user` vs `user_id` column name with static caching (`app/Models/UserDomainAccess.php:16-30`); used by the `User` relationship and all controller queries.
6. **`threshold_change_requests` columns** — `impact_snapshot` JSON, `high/medium/low_count` unsigned ints default 0, `status` VARCHAR(40) default `'pending'` (migration `2026_04_28_000001`); table now orphaned (§2.7).

---

## 5. Coverage statement

- **Total distinct tables found across models + migrations + DATABASE_SCHEMA.md + docs/sql:** **55**
  (52 model-backed tables — 52 model files map to 51 distinct tables since two `User` models share `user`, plus `location_wise_inv_stock` etc.; plus migration-only tables `product` (stub), `websockets_statistics_entries`, `threshold_change_requests`; plus doc/SQL-only ghosts `threshold_dependencies` and `business_rule_categorical_mapping`.)
- **DEEP coverage:** 12 tables (§2.1–§2.12).
- **BRIEF / shared-repo coverage:** 41 tables (§3), of which 26 are PPC, 7 order-management/stock, 7 POS/catalog (+ `product` stub), 1 infrastructure.
- **Tables mentioned in DATABASE_SCHEMA.md with NO model and NO migration in the current code (explicit flags):**
  - **`threshold_dependencies`** — DATABASE_SCHEMA.md §4.6 documents it fully and `docs/sql/align_threshold_fk_columns.sql:13-14` still ALTERs it, but the `ThresholdDependency` model is deleted and nothing in `app/` references it. Ghost table; the dependency-impact/approval feature it powered is gone.
  - **`business_rule_categorical_mapping`** — DATABASE_SCHEMA.md §4.4/§4.5; model deleted; no migration/SQL script; superseded by `condition_logics` + `rule_threshold_mapping`.
  - Related partial case: **`threshold_change_requests`** has a live migration but **no model and no code references** (orphaned, §2.7).
- **Stale-doc warning:** DATABASE_SCHEMA.md predates the BLOS rebuild — it still shows integer `thresholds.threshold_id`, `mapping_id`/`rule_id` FKs into `business_rule_categorical_mapping`, `previous_value`/`proposed_value`/`change_reason` columns, and it does **not** mention `glossary`, `condition_logics`, or `rule_threshold_mapping` at all. This dictionary reflects the code + `docs/sql` state at commit `bc1204a` and supersedes DATABASE_SCHEMA.md for the BLOS module.
- **Fresh-DB hazard:** migration `2026_04_28_000002_add_domain_to_user_table.php` adds `thresholds.proposed_value ... AFTER previous_value`; against a DB built from the current `thresholds.sql` (+ snapshot-column drop) this migration will fail (`previous_value` no longer exists), and `proposed_value` is absent from both the model `$fillable` and the rebuilt DDL.

*End of document.*
