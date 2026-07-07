## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-17 |
| **developer** | abiraj |
| **project** | LEDsONE Centralizer (Centralized Admin / Operations Platform) |
| **project\_code** | blos |
| **phase** | IMPLEMENTATION (BUILD + DEPLOY) |
| **requirement\_id** | REQ-04 |
| **deliverable\_id** | REQ-04-D03 |
| **status** | COMPLETE — committed + pushed to `Abiraj` (commit `f8804b8`); 2 planned TODOs remain (FK constraints, Rule Builder UI) |
| **evidence\_location** | Git commit **`f8804b8`** on branch `Abiraj` (GitLab: `sajeesans2/ledsone-centralizer`) · SQL: `docs/sql/business_rules.sql`, `condition_logics.sql`, `glossary.sql`, `threshold_versions.sql`, `thresholds_data_load.sql`, `rename_business_rule_table.sql` · code: `app/Models/{ConditionLogic,RuleThresholdMapping,Glossary,BusinessRule,Threshold}.php`, `app/Http/Controllers/Api/ThresholdConfigurationController.php`, `routes/api.php`, `resources/js/Account/Pages/{ThresholdConfigurator,OilConfigurator}.vue` · live: https://centralizer.vintageinterior.co.uk |
| **blos\_keys\_used** | Rule `BL-001` (CTR Collapse); thresholds `TH-001…TH-035`; glossary metrics `GL-001…GL-003`; mappings `MAP-001…MAP-005`; condition_logics rows 1–3 (stages initial/restore/kill). Source sheets: `BUSINESS_RULE_TABLE`, `CONDITION_LOGICS`, `GLOSSARY`, `THRESHOLDS_TABLE (3)`, `THRESHOLD_VERSION` |
| **hardcoded\_thresholds** | PK code regex (server-enforced): `^TH-\d+$`, `^BL-\d+$`, `^MAP-\d+$`, `^GL-\d+$`. Bulk upload caps: 1000 rows / 5 MB / first 200 errors returned. Auth token length 32 (`Str::random(32)`). FK dropdown list height 220px. **CHANGED today:** `change_reason` downgraded from `required\|min:10` to **optional** (TEMP). Live threshold values now TH-001…TH-035 (35 rows) |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| BLOS-THRESHOLDS \| LARAVEL \| VUE-SPA \| AMAZON-LISTINGS |

## File path:
# 2026-06-17__abiraj__blos__REQ-04-D03.md
# DigitWeb_Works_Abiraj/17_06_2026/

---

## SECTION 1 · SYSTEM STATE

- **Current system state at start of today:** After D02 the migration was half-done. The DB had **10 tables**; the three legacy tables the code still depended on — `business_rule_categorical_mapping`, `threshold_dependencies`, `threshold_change_requests` — had been **deleted**. The new tables `business_rule_table`, `condition_logics`, `rule_threshold_mapping` existed in the DB but had **no Eloquent models, controller methods, routes, or UI** (SQL only). `thresholds` held 7 rows.
- **What was working:** Viewing the thresholds list, domains, domain-access, version history, and YAML export. File Manager / Inventory / Users were unaffected.
- **What was broken / missing:** Editing a threshold value returned **HTTP 500** (controller queried the deleted `threshold_dependencies`). The admin grid's `mappings` and `dependencies` tabs + the impact/approval workflow all 500'd. `OilConfigurator` ("Business OS") grouping was dead (read removed `mapping_id`/`rule_id`). `business_rule_table` carried a redundant `_table` suffix.
- **Your starting point:** Build SQL for the remaining sheets, then make the **entire codebase consistent** with the new schema so editing works again, and harden the data-entry UX for non-technical users.
- **Environment:** Laravel 9 + Vue 2 SPA. Server is **XAMPP/Linux** at `/opt/lampp/htdocs/ledsone-centralizer`, MySQL DB `centralizer`. Runtime DB user `centralizer-limited-web` has no CREATE/DROP/ALTER. Local `.env` empty — code built locally (`npm run development`), SQL run on the server by hand, files deployed by manual copy.

> **In plain terms:** Yesterday we replaced the thresholds table; today we finished the job. We turned the rest of the colleague's spreadsheet into real database tables (rules, conditions, glossary), reconnected every screen and API to the new layout so saving works again, and made the forms much harder to get wrong — IDs fill in automatically, links are picked from dropdowns, and you can now upload many rows at once from a CSV. We also fixed the "Business OS" page and traced a confusing "keeps logging me out" problem to a shared login.

---

## SECTION 2 · WHAT CHANGED TODAY

- **Change 1 — Authored SQL for the remaining BLOS tables** (read each per-sheet `.xlsx` with python+openpyxl): `docs/sql/condition_logics.sql` (17 cols, 3 rows), `docs/sql/business_rules.sql` (8 cols, 1 row BL-001), `docs/sql/glossary.sql` (5 cols, GL-001…GL-003), `docs/sql/threshold_versions.sql` (schema doc for the existing table), `docs/sql/thresholds_data_load.sql` (DELETE + re-INSERT **35** rows TH-001…TH-035), `docs/sql/rename_business_rule_table.sql`.
- **Change 2 — Naming fix:** `RENAME TABLE business_rule_table TO business_rules` — dropped the redundant `_table` suffix (the old `business_rules` was already deleted, so the name was free; reuse-the-name pattern, same as `thresholds`).
- **Change 3 — New Eloquent models:** `ConditionLogic`, `RuleThresholdMapping`, `Glossary`; `BusinessRule` repointed to `business_rules` (string PK `rule_id` + `domain/owner/created_by/created_at`); **deleted** `BusinessRuleCategoricalMapping`, `ThresholdDependency`, `ThresholdChangeRequest`.
- **Change 4 — `ThresholdConfigurationController` rewritten:** removed mappings/dependencies/change-request/impact-approval code; added full CRUD for `condition_logics`, `rule_threshold_mapping`, `glossary`; threshold value-edit now saves immediately + logs a `threshold_versions` row (no approval gate); `stats()` + `exportCsv()` updated; added `bulkImport($tab)`.
- **Change 5 — `routes/api.php`:** removed dead routes; added CRUD routes for condition-logics, rule-threshold-mappings, glossary, and `POST bulk-import/{tab}`.
- **Change 6 — `ThresholdConfigurator.vue` retabbed:** tabs = business_rules / condition_logics / glossary / rule_threshold_mapping / thresholds / domain_access / versions, with matching headers, cells, add/edit forms, filters, counts, rowKey, save/delete paths.
- **Change 7 — Data-entry UX hardening:** auto-generated primary-key codes (prefix + next number, zero-padded), shown **locked** with a "🔒 Auto · Edit" toggle and live availability hint (✓ available / ⚠ duplicate / ⚠ wrong format); foreign-key fields became custom **searchable scrollable dropdowns**; `type` fields became **datalist** (dropdown + free typing); fixed a CSS grid overflow (`.tc-input width:100%`+`box-sizing`, `.tc-field min-width:0`).
- **Change 8 — Bulk CSV upload per tab:** validate-then-commit preview, skip-duplicates (with "update existing" upsert checkbox), partial import, admin-only; reuses the single-add validators + code normalisation.
- **Change 9 — `OilConfigurator.vue` ("Business OS") decoupled:** now groups by `thresholds.domain → channel → type` (real columns); removed all mapping/rule/condition/approval code and dead `requires_approval`/`needReload`.
- **Change 10 — TEMP:** `change_reason` made optional on threshold edits (frontend `canSave` + backend `thresholdsUpdate`), both marked `// TEMP:` for later restore.

### Deliverables
- **Deliverable A —** `business_rules`, `condition_logics`, `glossary` tables built + seeded on server; `thresholds` reloaded to 35 rows.
- **Deliverable B —** Full code integration (models + controller + routes + Vue) for all new tables — lints + builds clean.
- **Deliverable C —** UX hardening (auto-IDs + lock, searchable dropdowns, datalist) + Bulk CSV upload.
- **Deliverable D —** OilConfigurator decoupled/fixed.
- **Deliverable E —** Committed + pushed (`f8804b8`, Abiraj) + this EOD skill file.

Evidence reference: commit **`f8804b8`** (18 files, +1441/−776); `docs/sql/*.sql`; rebuilt `public/js/Account.js` (git-ignored, deployed manually). No credentials included.

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> Stack is **MySQL** (XAMPP/MariaDB), not PostgreSQL. New tables created by hand-run SQL (no Eloquent migrations). Sheets read with openpyxl from per-table `.xlsx` files.

### BLOS sheet inventory — status after today

| Sheet | Cols | Rows | Built today? | Target table |
| :---- | :---- | :---- | :---- | :---- |
| THRESHOLDS_TABLE (3) | 26 | 35 | ✅ reloaded | `thresholds` |
| BUSINESS_RULE_TABLE | 8 | 1 | ✅ built + renamed | `business_rules` |
| CONDITION_LOGICS | 17 | 3 | ✅ built | `condition_logics` |
| GLOSSARY | 5 | 3 | ✅ built | `glossary` |
| THRESHOLD_VERSION | 9 | 0 | ✅ documented | `threshold_versions` (already existed) |
| RULE_THRESHOLD_MAPPING | 5 | 5 | (D02) | `rule_threshold_mapping` |

### The BLOS data model (now complete enough to build the Rule Builder)

| Layer | Table | Holds |
| :---- | :---- | :---- |
| What the rule is | `business_rules` (BL-001) | rule name, description, domain, owner |
| How it decides per stage | `condition_logics` (1–3) | `condition_logic_by_ids`, decision_output, stage (initial/restore/kill) |
| What numbers it uses | `thresholds` (TH-001…035) + `rule_threshold_mapping` (MAP-) | values + rule↔threshold links |
| What the metric codes mean | `glossary` (GL-001…003) | metric term + definition (referenced inside condition expressions) |

### Primary-key convention discovered

```
String business codes : rule_id BL-### , threshold_id TH-### , mapping_id MAP-### , glossary_id GL-###
Integer auto-increment : condition_logics.condition_id , threshold_versions.version_id
                         (because those sheets used plain 1,2,3 — source honoured)
```

### Other findings

- **`user` table:** `created_at` and `updated_at` are `NOT NULL` with **no default** → a manual `INSERT` must supply `NOW()` for both (MySQL error **#1364** otherwise).
- **Auth:** custom bearer-token, NOT Sanctum. `user.token` is a **single** `varchar(60)` column; `CheckAuthMiddleware` finds the user by it and requires `is_active`. Role is read from **`config_role`**; active status from `user_status`.
- **Import hygiene:** literal text `"null"` in sheet cells must be converted to SQL `NULL` (else `'null'` is inserted into DATETIME → error). Web user lacks DDL (#1142) → run DDL as a privileged account; all scripts use `CREATE TABLE IF NOT EXISTS`.

---

## SECTION 4 · GAP FOUND

- **Gap — no "Add User" UI + single-session auth (MEDIUM, OPEN):** New accounts must be made via raw SQL (bcrypt-hashed password) or `POST /api/add-new-users`. Auth allows only **one active token per account**, so a second login silently invalidates the first. Impact: sharing one login causes random "auto logout"; onboarding a tester needs DB/dev work. Action: (a) build an Add-User admin screen; (b) optionally multi-session auth (`user_tokens` table — designed today, deliberately **not** built, see §7). Owner: abiraj / team lead.
- **Gap — `condition_logics.condition_logic_by_ids` is unvalidated free text (MEDIUM, OPEN):** expressions like `IF GL-001 < TH-001 …` are not checked against existing GL/TH codes. Proper structured editing belongs in the future Rule Builder. Owner: abiraj.
- **Gap — cross-table FK constraints still not added (LOW, OPEN):** all parent tables now exist, so `condition_logics.rule_id` & `rule_threshold_mapping.rule_id` → `business_rules`, and `rule_threshold_mapping.threshold_id` → `thresholds` can be added. Currently commented in the SQL files. Owner: abiraj.
- **Gap — manual-deploy fragility (MEDIUM, MITIGATED):** copying the controller without the new model files (or skipping `composer dump-autoload` / `route:clear`) causes 500/404. Action: documented deploy checklist (§6). Owner: abiraj.

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

### RULE ADDED — BLOS business-code format & normalisation guard
- **Condition checked:** every ID/code field is uppercased + whitespace-stripped, then matched on the server — `threshold_id ^TH-\d+$`, `rule_id ^BL-\d+$`, `mapping_id ^MAP-\d+$`, `glossary_id ^GL-\d+$`; PKs must be unique.
- **Prevents:** malformed codes from non-technical users (`gl- 005`, `GL005`, lowercase, trailing spaces) and duplicate PKs — the data that all GL/TH/BL/MAP cross-references depend on.
- **Where:** `ThresholdConfigurationController` (`normalizeCodeFields()` + `regex:` rules in every store/update); frontend mirror in `ThresholdConfigurator.vue` (`pkHint()`, `saveForm` normalise/block, `nextCodeForActiveTab()` auto-fill).

### RULE ADDED — Bulk-import per-row validation (reuses single-add rules)
- Each CSV row is normalised + validated with the same per-tab rules; duplicates are skipped (or upserted); only valid rows commit, inside a transaction; invalid rows reported with row numbers. Caps: 1000 rows / 5 MB.

### RULE CHANGED (TEMPORARY) — threshold change_reason
- `thresholdsUpdate`: `change_reason` `required|string|min:10|max:1000` → **`nullable|string|max:1000`**; frontend `canSave` reason-gate removed; label shows "(optional for now)". Marked `// TEMP:` in both files — restore to required when the audit-reason requirement is re-enabled.

### RULE CHANGED — business-rule delete guard
- `businessRulesDestroy` now blocks deletion if `rule_threshold_mapping` **or** `condition_logics` reference the `rule_id` (the old categorical-mapping check was removed).

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Failure mode (RESOLVED) — "auto logout after a while / on every click" (MEDIUM):** Trigger — the login was **shared with a tester**; each login overwrites the single `user.token`, so the older session's token stops matching. Detection — `Router.js beforeEach` (and tab `visibilitychange`) call `GET /api/me`; `CheckAuthMiddleware` returns **401**; `refreshSessionUser()` returns `'expired'` → clears auth → `/login`. Recovery — give each person their **own** account; immediate workaround = full logout → login in one tab.
- **Failure mode (MITIGATED) — partial deploy "Class App\Models\X not found" / route 404 (MEDIUM):** Trigger — copying controller/routes without new model files or without autoload/route cache refresh. Recovery — copy model files, then `composer dump-autoload` + `php artisan route:clear` + `optimize:clear`.
- **Edge case (HANDLED) — literal `"null"` text in sheets:** converted to SQL `NULL` in `thresholds_data_load.sql` (else `'null'` breaks DATETIME columns).
- **Edge case (HANDLED) — `user.updated_at` NOT NULL (#1364):** manual user INSERT must include `created_at`/`updated_at` = `NOW()`.
- **Edge case (HANDLED) — long `<select>` blew out the form grid:** native dropdown of 35 thresholds overflowed; replaced with a sized, scrollable, searchable custom dropdown (`flex:0 0 auto` so items don't squash).

---

## SECTION 7 · DECISIONS MADE TODAY

- **Decision: rename `business_rule_table` → `business_rules`.** Alternatives: keep the suffix; use singular `business_rule`. Reason: `_table` is redundant, `business_rules` is the correct plural and was free (old one deleted); same precedent as `thresholds`. Trade-off: one `RENAME TABLE` step. Approved: abiraj.
- **Decision: remove the impact/approval workflow; threshold edits save immediately.** Alternative: recreate `threshold_dependencies` + `threshold_change_requests`. Reason: those tables were intentionally deleted; the new model expresses decisions in `condition_logics`. Trade-off: no approval gate (a version row is still logged).
- **Decision: fix shared-login logouts with separate accounts, NOT multi-session.** Alternatives: `user_tokens` multi-token table (designed + half-built); widen `user.token` to a JSON list. Reason: user declined the extra table; separate accounts are zero-code and improve change attribution. Trade-off: one login per account; the `user_tokens` change was fully reverted.
- **Decision: auto-generate PK codes but keep them editable (locked with toggle).** Reason: removes typos for non-technical users while allowing the rare manual override. Trade-off: a little extra UI state.
- **Decision: bulk import = CSV with preview-then-commit, skip-duplicates default + upsert option, partial import.** Reason: safest for non-technical users; round-trips with the existing Export CSV. Trade-off: `.xlsx` not directly accepted (Save-As-CSV needed).

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Business Rule — a rule runs in three stages
A BLOS rule (e.g. **BL-001 "CTR Collapse"**) is evaluated **initial → restore → kill**: `initial` flags an underperforming SKU, `restore` reinstates it if it recovers above the restore threshold, `kill` suppresses it if it stays below the kill threshold for the required days. Stage logic + decision live in `condition_logics`; the numbers live in `thresholds` (linked via `rule_threshold_mapping`); metric codes are defined in `glossary`.

### Operational Assumption
Every business code (BL-/TH-/MAP-/GL-) is globally unique and upper-case; condition expressions reference **existing** GL (metric) and TH (threshold) codes; one human owner per rule/threshold; thresholds are scoped `domain → channel → type → fulfillment → account → site`.

### Reusable Logic / Formula
- **Condition expression format:** `IF <GL-metric> <op> <TH-threshold> [AND …]` — e.g. `IF GL-001 < TH-001 AND GL-002 >= TH-002 AND GL-003 <= TH-003`.
- **Next-code generator:** `prefix + zeroPad(max(existing numeric suffix)+1, 3)` → max `GL-003` ⇒ next `GL-004`.
- **Threshold registry export** = `threshold_key: value` YAML map = single source of truth for downstream AI agents / N8N.
- **Per-table build playbook:** read sheet → generate `CREATE TABLE IF NOT EXISTS` + INSERT → run as privileged DB user → add Model + Controller CRUD + routes + Vue tab → reuse validators → `composer dump-autoload` + `route:clear` + `optimize:clear` → deploy `public/js/Account.js`.

### Canonical Vocabulary

| Term | Meaning |
| :---- | :---- |
| BLOS | Business-logic / rules redesign programme |
| OIL / Business OS | `OilConfigurator` screen for editing threshold values |
| business-code PK | human-readable string PK (`TH-001`, `BL-001`, `MAP-001`, `GL-001`) |
| condition expression | `IF GL-x <op> TH-y AND …` stored in `condition_logics.condition_logic_by_ids` |
| stages | initial · restore · kill |
| datalist field | input with dropdown suggestions that still allows free typing |
| validate-then-commit | bulk import dry-run preview before any write |

### Cross-Project Applicability
- The **auto-generate + lock + live availability hint + server normalise/regex** pattern for prefixed business codes is reusable in any CFIS/KMS/PPC form.
- The **validate-then-commit bulk-CSV importer** (preview counts + per-row errors, skip/upsert, reuse single-record validators) is a drop-in component for any admin grid.
- The **"build new tables alongside, retire later" + string-code PK + junction-table link** patterns are a safe template for replacing a live schema without downtime.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced (commit + SQL + URL)? | ✅ YES |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (1–9)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment
A developer with no context could, from this file alone:
- **WHAT** was done — built `business_rules` / `condition_logics` / `glossary`, reloaded `thresholds` to 35 rows; fully wired every new table through models → controller → routes → Vue; added auto-IDs + searchable dropdowns + datalist + bulk CSV upload; decoupled OilConfigurator; committed `f8804b8`.
- **WHAT** the structure is — rule (`business_rules`) → stage logic (`condition_logics`) → numbers (`thresholds` via `rule_threshold_mapping`) → metric meanings (`glossary`); string-code PKs except auto-int `condition_id`/`version_id`.
- **WHAT** is pending — DB FK constraints; the drag-and-drop Rule Builder UI; (temp) restore the `change_reason` requirement.
- **WHO** needs action — abiraj (FKs, Rule Builder, Add-User screen); team lead (multi-session decision if sharing continues).
- **WHY** decisions were made — rename to drop `_table`; remove approval workflow (tables deleted); separate accounts over multi-session (no new table); auto-but-editable IDs for safety.
- **WHERE** everything lives — repo `ledsone-centralizer` branch `Abiraj` (commit `f8804b8`); SQL in `docs/sql/`; server `/opt/lampp/htdocs/ledsone-centralizer`, DB `centralizer`; live https://centralizer.vintageinterior.co.uk.
- **WHAT** to do next — add FK constraints, then start the BLOS Rule Builder (all supporting tables now exist).

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-06-17__abiraj__blos__REQ-04-D03.md`
- [x] Metadata complete — includes `blos_keys_used` and `hardcoded_thresholds`
- [x] Sheet inventory + data-model + PK convention included in Section 3
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written (WHAT/WHO/WHY/WHERE)
- [x] Evidence referenced by commit hash (`f8804b8`) + SQL + live URL
- [x] ✅ **DELIVERED:** `business_rules`, `condition_logics`, `glossary` tables built; `thresholds` reloaded to 35 rows
- [x] ✅ **DELIVERED:** full code integration (models, controller, routes, Vue) — lints + builds clean
- [x] ✅ **DELIVERED:** UX hardening (auto-IDs + lock, searchable FK dropdowns, datalist) + Bulk CSV upload
- [x] ✅ **DELIVERED:** OilConfigurator ("Business OS") decoupled to domain → channel → type
- [x] ✅ **DELIVERED:** committed + pushed (`f8804b8`, branch `Abiraj`)
- [ ] ⚠️ **OPEN:** add cross-table FK constraints (abiraj)
- [ ] ⚠️ **OPEN:** build the BLOS Rule Builder drag-and-drop UI (abiraj)
- [ ] ⚠️ **OPEN:** restore the `change_reason` requirement when approved (temporary relaxation)
- [ ] ⚠️ **OPEN:** Add-User admin screen / decide multi-session if login sharing continues (team lead)

---
*DIGITWEB LK LTD — Daily Skill Increment System — v3.0 — June 2026*
