## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-16 |
| **developer** | abiraj |
| **project** | LEDsONE Centralizer (Centralized Admin / Operations Platform) |
| **project\_code** | blos |
| **phase** | IMPLEMENTATION |
| **requirement\_id** | REQ-04 |
| **deliverable\_id** | D02 |
| **status** | IN-PROGRESS (threshold + mapping tables delivered; remaining BLOS tables pending) |
| **evidence\_location** | `docs/sql/thresholds.sql`, `docs/sql/align_threshold_fk_columns.sql`, `docs/sql/rule_threshold_mapping.sql`, `docs/blos-rule-builder-model.md`, `docs/BLOS-Rule-Builder-Summary.md`, `docs/blos-rule-builder-ui.md`, `docs/blos-rule-builder-mockup.html` · code: `app/Models/Threshold.php`, `app/Models/BusinessRuleCategoricalMapping.php`, `app/Http/Controllers/Api/ThresholdConfigurationController.php`, `resources/js/Account/Pages/ThresholdConfigurator.vue` — local working branch, not yet committed |
| **blos\_keys\_used** | Threshold business codes created: TH-001…TH-007. Rule code referenced: BL-001. Mapping codes: MAP-001…MAP-005. Source sheets: `THRESHOLDS_TABLE`, `RULE_THRESHOLD_MAPPING` (from `BLOS TABLE MODEL.xlsx`) |
| **hardcoded\_thresholds** | PRESERVED approval gate (unchanged): high_count ≥ 2 → approval required; MEDIUM impact → reviewed_impact confirmation; change_reason ≥ 10 chars. LOADED threshold values: CTR Floor 0.93%, Min Impressions 1000, CTR Review Period 14 days, Recovery Target 1.05%, CTR Recovery Window 21 days, CTR Kill Window 0.77%, CTR Kill Days 30 |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| SCHEMA-MIGRATION \| LARAVEL \| BLOS \| THRESHOLDS |

## File path (fill after saving):
# 2026-06-16__abiraj__blos__REQ-04-D02.md

---

## SECTION 1 · SYSTEM STATE

- **Current system state:** The BLOS threshold subsystem has been migrated off the old hand-built `thresholds` table onto the new colleague-authored Excel data model. A new `thresholds` table (26 columns, **string primary key** `TH-xxx`) is created and live on the server with 7 seeded rows; the Laravel model, API controller, and Vue configurator UI have all been updated to match. A new `rule_threshold_mapping` junction table (5 rows) is also created. All other existing tables are untouched.
- **What was working at start of today:** The old Threshold Configurator running on the old `thresholds` table (integer PK, columns `mapping_id` / `rule_id` linking each threshold to a business rule and categorical mapping). The BLOS Rule Builder existed only as a plan in earlier session notes.
- **What was broken / missing at start of today:** None of the new BLOS data model (from the colleague's `BLOS TABLE MODEL.xlsx`) existed in the database — it was design only. No SQL, no tables, no UI for the new structure.
- **Your starting point:** Continue the BLOS Rule Builder work — finalise the design, then build the new tables from the (now mostly finalised) Excel model, starting with the threshold table, and update the code to use it.
- **Environment:** Laravel 9 + Vue 2 SPA, local working branch. Server MySQL database `centralizer`, accessed via phpMyAdmin. The app's runtime DB user is `centralizer-limited-web` (restricted: no CREATE/DROP/ALTER). Local `.env` is empty — code edited and built locally (`npm run development`); all SQL run on the server by hand.

> **In plain terms:** A colleague redesigned how business rules and thresholds are stored (in an Excel model). Today we started turning that design into real database tables, beginning with the thresholds table — built it from the spreadsheet, loaded its data, and rewired the app's code and screens to the new column layout. We also built the small "mapping" table that links rules to thresholds. The old tables were left in place so nothing breaks; they'll be retired once everything is migrated.

---

## SECTION 2 · WHAT CHANGED TODAY

- **Change 1 — Authored the BLOS Rule Builder design set:** `docs/blos-rule-builder-model.md` (technical table model), `docs/BLOS-Rule-Builder-Summary.md` (plain-language), `docs/blos-rule-builder-ui.md` (UI plan), and `docs/blos-rule-builder-mockup.html` (clickable mockup demonstrating the drag-and-drop builder and that rules are stored as **IDs, not values**).

- **Change 2 — Built the new `thresholds` table from Excel:** Read `THRESHOLDS_TABLE` (sheet) with openpyxl → generated `docs/sql/thresholds.sql` faithfully — 26 columns, 7 rows (TH-001…TH-007). The literal text `"null"` in the sheet was converted to real SQL `NULL`. `value` typed as `DECIMAL(15,4)`.

- **Change 3 — Migrated the threshold schema (column changes):** REMOVED `mapping_id`, `rule_id`, `also_known_as`, `direction`, `domain_owner`. ADDED `alternative_names`, `type`, `fulfillment`, `channel`, `account`, `site`, `owner`, `created_by`, `created_at`, `approver`. PK changed from integer auto-increment to **string code** (`TH-001`).

- **Change 4 — Updated the Laravel code to match:** `Threshold` model (`$incrementing=false`, `$keyType='string'`, new `$fillable`/`$casts`, dropped the `categoricalMapping()` and `businessRule()` relations); `BusinessRuleCategoricalMapping` (dropped `thresholds()` relation); `ThresholdConfigurationController` (rewrote `thresholdsStore`/`thresholdsUpdate` validation, fixed `thresholdsIndex` filters/search, removed `mapping_id`-based hydration and dead helpers, changed dependency/version `threshold_id` validation int→string); `ThresholdConfigurator.vue` (table headers, row cells, add/edit form, filters, colspan — `threshold_id` now an editable code on Add, disabled on Edit). PHP lints clean; frontend compiles clean.

- **Change 5 — Aligned child tables:** Produced `docs/sql/align_threshold_fk_columns.sql` widening `threshold_versions`, `threshold_dependencies`, `threshold_change_requests`.`threshold_id` from integer to `VARCHAR(20)` so they accept `TH-xxx`.

- **Change 6 — Built the `rule_threshold_mapping` junction table:** From `RULE_THRESHOLD_MAPPING` (sheet) → `docs/sql/rule_threshold_mapping.sql`, 5 rows (MAP-001…MAP-005, all linking rule `BL-001` to thresholds TH-001…TH-005). PK `mapping_id` (string), unique `(rule_id, threshold_id)`, indexes on both FKs. No FK constraints yet (parent `business_rule_table` not built).

- **Change 7 — Established the migration strategy:** New tables are built **alongside** the existing ones using the Excel sheet names (lowercased) — existing tables are not touched; old tables retired only after full migration. SQL scripts switched to `CREATE TABLE IF NOT EXISTS` (no `DROP`) because the web DB user is restricted.

- **Deliverable A — `thresholds` table + data** live on server.
- **Deliverable B — `rule_threshold_mapping` table + data** live on server.
- **Deliverable C — Threshold code/UI migration** (model, controller, Vue) complete.
- **Deliverable D — this EOD skill file.**

Evidence reference: all `docs/sql/*.sql` and the four changed source files on branch `gajan` (not yet committed). No credentials included.

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> Source: the colleague's `BLOS TABLE MODEL.xlsx` (10 sheets) read with openpyxl, plus static analysis of the Laravel models/controller. The app uses **MySQL**; the new BLOS tables are being created by hand-run SQL (no migrations).

### New BLOS data model — sheet inventory

| Sheet | Cols | Rows | Built today? | Target table name |
| :---- | :---- | :---- | :---- | :---- |
| THRESHOLDS_TABLE | 26 | 7 | ✅ | `thresholds` (replaced old) |
| RULE_THRESHOLD_MAPPING | 5 | 5 | ✅ | `rule_threshold_mapping` (new) |
| BUSINESS_RULE_TABLE | 9 | 19 | pending | `business_rule_table` (new) |
| CONDITION_LOGICS | 18 | 3 | pending | `condition_logics` (new) |
| BLOS_GLOSSARY | 5 | 3 | not finished | — |
| DATA_SOURCE | 5 | 3 | not finished | — |
| BLOS_DATA_SOURCE | 6 | 0 | empty | — |
| THRESHOLD_VERSION | 9 | 0 | empty | — |
| CONDITION_LOGIC_VERSION / RULE_VERSION | 6 | 0 | empty | — |
| RULE_DEPENDENCIES | 9 | 0 | empty | — |

### KEY STRUCTURAL CHANGE — the rule↔threshold link moved

| | OLD model | NEW model |
| :---- | :---- | :---- |
| How a threshold links to its rule | Columns **on** the threshold row: `thresholds.mapping_id`, `thresholds.rule_id` | A **separate junction table** `rule_threshold_mapping (mapping_id, rule_id, threshold_id)` |
| Threshold PK | integer auto-increment | **string business code** `TH-001` |
| Consequence | UI grouped thresholds via those columns | Grouping now requires a JOIN through the junction table |

This is *why* the old "Business OS" (`OilConfigurator.vue`) page breaks — it read the now-removed `thresholds.mapping_id` / `rule_id`.

### Threshold table — before / after columns

```
REMOVED : mapping_id, rule_id, also_known_as, direction, domain_owner
ADDED   : alternative_names, type, fulfillment, channel, account, site,
          owner, created_by, created_at, approver
PK      : int auto-increment  ->  VARCHAR(20) string code (TH-001)
```

### Permission finding

The runtime DB user `centralizer-limited-web` has **no DDL rights** (CREATE/DROP/ALTER denied, error #1142). MySQL checks the CREATE privilege **before** evaluating `IF NOT EXISTS`, so even a safe `CREATE TABLE IF NOT EXISTS` fails for this user if it lacks CREATE. All table-creation SQL must be run from a **privileged** DB account (the database owner / admin login).

---

## SECTION 4 · GAP FOUND

- **Gap — child FK columns were integer (HIGH, RESOLVED):** `threshold_versions`, `threshold_dependencies`, `threshold_change_requests` carried integer `threshold_id`; the new PK is a string. Without widening, saving a version/dependency/change-request fails. Action: `align_threshold_fk_columns.sql` (run on server). Owner: abiraj — done.

- **Gap — `OilConfigurator.vue` ("Business OS") broken (MEDIUM, OPEN):** Page groups thresholds by the removed `mapping_id` / `rule_id`; it now collapses into one ungrouped blob with blank fields. Options agreed: (a) rework to group by `domain` + `channel` (threshold-only, decoupled from rule/mapping tables → won't break again), or (b) hide it and rebuild later using the new `rule_threshold_mapping` junction once the rule tables exist. Decision deferred. Owner: Dev team / product owner.

- **Gap — restricted DB user cannot create tables (MEDIUM, WORKAROUND):** `centralizer-limited-web` lacks CREATE/DROP. Action: run all DDL from the privileged DB account. Owner: abiraj / hosting admin.

- **Gap — remaining BLOS tables not yet built (PLANNED):** `business_rule_table`, `condition_logics` (finished sheets) still pending; `blos_glossary`, `data_source`, version/dependency sheets not finished in the Excel. Action: build as each sheet is finalised. Owner: abiraj + colleague (Excel).

- **Gap — cross-table FK constraints not yet added (LOW):** `rule_threshold_mapping` has indexes but no FK constraints, because the parent `business_rule_table` does not exist yet. Action: add `ALTER … ADD FOREIGN KEY` once the rule + threshold tables coexist. Owner: abiraj.

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

- **RULE CHANGED — Threshold create validation:** `threshold_id` is now `required|string|max:20|unique:thresholds` (user-supplied business code on create, previously auto-increment). `threshold_key` `required|unique`. New nullable columns validated (`alternative_names`, `type`, `fulfillment`, `channel`, `account`, `site`, `owner`, `created_by`, `created_at`, `approver`). Removed validation for `mapping_id`, `rule_id`, `also_known_as`, `direction`, `domain_owner`. Implemented in `ThresholdConfigurationController@thresholdsStore`.

- **RULE CHANGED — Threshold update validation:** Same column set; `threshold_id` is the URL key (not editable). Implemented in `@thresholdsUpdate`.

- **RULE PRESERVED — Threshold change impact gate (unchanged):** `high_count ≥ 2` → pending change request; MEDIUM impact → `reviewed_impact = true`; `change_reason ≥ 10` chars; non-admin domain check. Logic untouched and still works against the new schema.

- **RULE CHANGED — Dependency / Version `threshold_id`:** validation changed `integer` → `string|max:20` in `dependenciesStore/Update` and `versionsStore/Update`, to accept `TH-xxx`.

- **RULE CHANGED — Business-rule delete guard:** now checks only that no `business_rule_categorical_mapping` references the `rule_id` (the old threshold `rule_id` check was removed — that column is gone). Implemented in `@businessRulesDestroy`.

- **RULE ADDED — Junction uniqueness:** `rule_threshold_mapping` enforces `UNIQUE(rule_id, threshold_id)` so a rule cannot link the same threshold twice.

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Edge case (HANDLED) — `"null"` text in the sheet:** Several cells (`last changed by/at`, `previous value`, `change reason`) contained the literal string `"null"`. Converted to real SQL `NULL` during SQL generation so they aren't stored as the text "null".

- **Failure mode (RESOLVED) — string PK vs integer child columns:** New `TH-001` PK could not be stored in the integer `threshold_id` of the version/dependency/change-request tables. Resolved by `align_threshold_fk_columns.sql`.

- **Failure mode (OPEN) — Business OS page degraded:** `OilConfigurator.vue` shows ungrouped thresholds with blank `direction`/rule fields. Recovery: rework or hide (Section 4). Risk: MEDIUM (user-visible page).

- **Failure mode (HANDLED) — CREATE denied under restricted user:** `#1142 CREATE denied` even with `IF NOT EXISTS`. Recovery: run DDL as a privileged DB account. Note the import can report "successfully finished" on first run while a second run errors — confirm with `SELECT * FROM <table>`.

- **Edge case (NOTED) — old version/dependency rows use integer ids:** Any pre-existing `threshold_versions` / `threshold_dependencies` rows keyed to old integer ids won't line up with the new `TH-xxx` codes. New rows are fine; legacy rows (if any) need remapping.

---

## SECTION 7 · DECISIONS MADE TODAY

- **Decision: Reuse the name `thresholds` for the new threshold table (replace), but use new names for all other BLOS tables (build alongside).**
  Reason: the threshold table was deleted and rebuilt to keep the existing Threshold Configurator working with minimal disruption; the rest are built as new tables so nothing else breaks until the full migration is verified. Trade-off: temporary mix of old + new tables until cutover.

- **Decision: `threshold_id` (and `rule_id`, `mapping_id`) are string business codes as the real primary keys.**
  Reason: matches the Excel model exactly and keeps the codes human-meaningful and stable across systems. Trade-off: child tables must widen their FK columns to VARCHAR.

- **Decision: Do not add cross-table FK constraints yet.**
  Reason: parent tables (`business_rule_table`) are not built; adding FKs now would fail. Add them after all tables coexist.

- **Decision: Defer the Business OS (`OilConfigurator`) fix.**
  Reason: the correct rework depends on whether it should group by `domain` (threshold-only) or by rule via the new junction table — and the rule tables aren't built yet. Decided to avoid double-work by waiting.

- **Decision: Switch SQL scripts to `CREATE TABLE IF NOT EXISTS`, no `DROP`.**
  Reason: the web DB user lacks DROP/CREATE privileges; re-runs must be handled by a privileged account.

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule — Business logic is built from blocks, never hand-typed

The BLOS redesign exists to stop people hand-typing rule logic (which caused inconsistent operators like `≥` vs `>=` and typos like `=<`). In the new model a rule is assembled from **draggable building blocks** — a metric (from the glossary), an operator (from a fixed list), and a threshold — and the system both stores the structured pieces **and** generates the readable sentence. Rules reference **IDs** (`TH-001`, `GL-001`), never the display values, so renaming a threshold never breaks a rule.

### Business Rule — Threshold changes are governed by impact (unchanged)

A threshold value change is risk-assessed from its registered dependencies: any change touching **2+ HIGH-impact systems** becomes a pending approval request; MEDIUM requires a reviewed-impact confirmation; every change needs a reason ≥ 10 chars and is versioned. This rule survived the schema migration unchanged.

### Architectural Fact — the rule↔threshold link is a junction table now

`rule_threshold_mapping (mapping_id, rule_id, threshold_id)` is the single source of truth for which thresholds belong to which rule. The threshold row itself no longer carries any rule reference. One rule (e.g. `BL-001`) maps to many thresholds.

### Reusable Logic / Reference

- **Threshold business values (live):** CTR Floor 0.93% · Min Impressions 1000 · CTR Review Period 14d · Recovery Target 1.05% · CTR Recovery Window 21d · CTR Kill Window 0.77% · CTR Kill Days 30 (all `domain = Organic Listing Performance`, `channel = Amazon`, `account = ledsone`, `site = UK`).
- **Build playbook (per table):** read sheet → generate `CREATE TABLE IF NOT EXISTS` + INSERT SQL → run on server as a privileged user → update Model + Controller + Vue → align child FK columns if PK type changed → rebuild frontend → deploy code + `public/js/Account.js`.

### Canonical Vocabulary

| Term | Meaning |
| :---- | :---- |
| BLOS | The business-logic / rules redesign programme (project code) |
| business code PK | A human-readable string primary key (`TH-001`, `BL-001`, `MAP-001`) |
| `rule_threshold_mapping` | Junction table linking rules to thresholds (replaces threshold columns) |
| Rule Builder | The planned drag-and-drop UI that assembles rule logic from blocks |
| build alongside | Create new tables next to old ones; retire old ones only after cutover |

### Cross-project applicability

The **string-business-code PK** convention and the **junction-table link** pattern are reusable across any config-governance system. The **"build new tables alongside, retire later"** migration strategy is a safe template for replacing a live schema without downtime.

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
| Are section names per standard template (1–9)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment

A developer with no context could understand from this file alone:

- **WHAT** was done today — built the new `thresholds` table (26 cols, string PK, 7 rows) and the `rule_threshold_mapping` junction table (5 rows) from the BLOS Excel model; rewired the Threshold model, API controller, and Vue configurator to the new columns; aligned child FK tables; authored the Rule Builder design docs + mockup.
- **WHAT** the structure is — new BLOS model uses string business codes as PKs and a junction table for rule↔threshold links; the threshold row no longer holds `mapping_id`/`rule_id`.
- **WHAT** is still broken / pending — `OilConfigurator.vue` ("Business OS") uses removed columns; remaining BLOS tables (`business_rule_table`, `condition_logics`) not yet built; cross-table FKs not added; some Excel sheets unfinished.
- **WHO** needs action — abiraj (build remaining tables, decide Business OS fix); colleague (finish glossary/data-source sheets); hosting admin (privileged DB account for DDL).
- **WHY** the decisions were made — replace `thresholds` in place but build others alongside; string-code PKs to match the Excel; defer Business OS to avoid double-work.
- **WHERE** everything lives — repo `ledsone-centralizer`, local working branch; SQL in `docs/sql/`; design in `docs/blos-rule-builder-*`; server DB `centralizer`.
- **WHAT** to do next — build `business_rule_table` + `condition_logics`; add FK constraints; decide and implement the Business OS rework; commit the branch.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-06-16__abiraj__blos__REQ-04-D02.md`
- [x] Metadata complete — includes `blos_keys_used` and `hardcoded_thresholds`
- [x] Sheet inventory + before/after schema included in Section 3
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written
- [x] Evidence locations referenced (SQL scripts + source files)
- [x] ✅ **DELIVERED:** new `thresholds` table (26 cols, string PK, 7 rows) live on server
- [x] ✅ **DELIVERED:** `rule_threshold_mapping` junction table (5 rows) live on server
- [x] ✅ **DELIVERED:** threshold code/UI migration (model, controller, Vue) — lints + builds clean
- [x] ✅ **DELIVERED:** BLOS Rule Builder design docs + interactive mockup
- [x] ✅ **RESOLVED:** child FK columns widened to VARCHAR (align SQL run)
- [ ] ⚠️ **OPEN:** Build `business_rule_table` + `condition_logics` (abiraj)
- [ ] ⚠️ **OPEN:** Decide + implement Business OS (`OilConfigurator`) rework or hide (Dev team)
- [ ] ⚠️ **OPEN:** Add FK constraints once all BLOS tables coexist (abiraj)
- [ ] ⚠️ **OPEN:** Obtain a privileged DB account for table-creation DDL (hosting admin)
- [ ] ⚠️ **OPEN:** Commit the working branch and replace evidence path with commit hash
- [ ] ⚠️ **OPEN:** Finish glossary / data-source Excel sheets before building those tables (colleague)

---
*DIGITWEB LK LTD — Daily Skill Increment System — v3.0 — June 2026*
