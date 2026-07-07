# LEDsONE Centralizer (BLOS / Project Sentinel) — COMPLETE Skill File

**The single all-in-one document.** This file consolidates the entire skill-file deliverable
for the LEDsONE Centralizer / BLOS system into one place: the user skill file (how to use the
system) plus the full deep-reference package (how the system is built and how to continue it).
Every part below is the verified content of an individual deliverable, merged here unchanged.

| Field | Value |
|---|---|
| date | 2026-07-07 |
| project | LEDsONE Centralizer — Business Logic Operating System (Project Sentinel) |
| project_code | blos |
| task | REQ-04_ledsone-centralizer-user-skill (deliverables D06 + D07) |
| author | J. Abiraj (compiled by Claude Code, evidence-backed) |
| status | DRAFT — awaiting Queryability (Tamil Selvan) + Technical (Sajeesan) review |
| source of truth | repository `ledsone-centralizer` @ HEAD `bc1204a`, scanned read-only 2026-07-07 + git history |
| note | Consolidated master. The same content also exists as 9 separate files in this folder; this file is the merged single copy for readers who want everything in one place. |

---

## MASTER TABLE OF CONTENTS

- **PART A — USER SKILL FILE** (what the system is, roles, workflows, business rules, evidence map, known limits) — the 15 mandated sections
- **PART B — CONTINUATION GUIDE** (current stage, what to do next, how to continue without the developer)
- **PART C — CODE MAP** (every file, by reference)
- **PART D — DATA DICTIONARY** (every table and column)
- **PART E — API REFERENCE** (every endpoint)
- **PART F — UI REFERENCE** (every screen and control)
- **PART G — SECURITY & DEPLOY** (auth model + deployment runbook)
- **PART H — VERIFICATION FINDINGS** (the four open questions, settled with git evidence)
- **PART I — SHARED-REPO MODULES INVENTORY** (code in the repo that is NOT part of this project)

---



---

# PART A — USER SKILL FILE

---

# LEDsONE Centralizer (BLOS / Project Sentinel) — User Skill File

| Field | Value |
|---|---|
| **date** | 2026-07-07 |
| **developer / author** | abiraj (compiled by Claude Code under approved GPT prompt) |
| **project** | LEDsONE Centralizer (Centralized Admin / Operations Platform) |
| **project_code** | blos |
| **requirement_id** | REQ-04 |
| **deliverable_id** | REQ-04-D06 (this user skill file) — its deep companion documents are **REQ-04-D07**, same task folder |
| **revision** | **Rev 2 (2026-07-07)** — this D06 skill file was updated in place after the D07 deep code analysis: the four previously-open questions are now resolved (see §11–§12), missing UI behaviours added, evidence expanded. Deliverable ID intentionally stays D06 (updated in place, not forked); the D07 ID belongs to the eight companion analysis documents. |
| **status** | DRAFT — awaiting Queryability review |
| **audience** | New Centralizer users, dept leaders, developers or MD (and LLMs) |
| **repository** | `ledsone-centralizer` (GitLab `sajeesans2/ledsone-centralizer`, branch `Abiraj`) · live: https://centralizer.vintageinterior.co.uk |
| **evidence basis** | Repository scan of 2026-07-07 + git history + imported delivery archive (see §11 Evidence Map) |
| **companion (deep) docs** | For developers: the D07 package in this same folder — CODE_MAP, DATA_DICTIONARY, API_REFERENCE, UI_REFERENCE, SECURITY_AND_DEPLOY, VERIFICATION_FINDINGS, SHARED_MODULES_INVENTORY, and the CONTINUATION_GUIDE (start there to continue the project) |
| **llm_queryable** | YES |

> Repo paths below are relative to the `ledsone-centralizer` repository root.
> Archive paths (`archive/…`) refer to this project's
> `evidence/source_documents/REQ-04_ledsone-centralizer-user-skill/`.

---

## 1. Purpose

LEDsONE Centralizer is a **central admin / operations hub** web application. It sits on top of
multiple company MySQL databases (Order Management, PPC, Accounts) and provides one place to:

- **Manage business-rule thresholds** — the numeric values (e.g. `TH-001`…) that gate company
  business rules (`BL-001`…), with full change history, versioning, and per-domain ownership.
  This is the **BLOS — Business Logic Operating System** core.
- **Author rule logic** in a drag-and-drop **Rule Builder** (admin only).
- **Manage a Central File Library** (SkillVault) — hierarchical folders, upload/replace,
  text preview, single-file and ZIP-folder downloads.
- **Manage users and their domain access** so non-admin staff see only the thresholds of the
  business domains they own.
- Serve additional catalog/POS-style endpoints (products, categories, inventory, sales).

Evidence: `DATABASE_SCHEMA.md:1-26` (hub-of-databases description), route/module inventory in
§5, archive tracker `archive/gaps_and_logics/skill_requirement_tracker.md` (Project Identity).

## 2. Business / Operational Question Supported

**"What are our official business-rule threshold values right now, who is allowed to change
each one, what changed, when, by whom and why — and how do staff and systems consume the
current values safely?"**

The system makes every threshold value a governed record: domain-scoped editing, an
append-only version history (`threshold_versions`), and machine-readable exports
(YAML `rules_registry.yaml`, CSV per table) so people and downstream systems read one source
of truth instead of hardcoded numbers. Secondary question: "where do our internal skill/
knowledge files live?" — answered by the Central File Library.
Evidence: `app/Http/Controllers/Api/ThresholdConfigurationController.php:486-553` (versioned
update), `:819-873` (exports); `archive/requirement_documents/BLOS_Build_Guide_Vithushali_v1.0 (2).docx`.

## 3. User Roles

| Role | How it is determined | What they can do |
|---|---|---|
| **admin** | `user.config_role` normalised to lowercase = `admin` (`app/Models/User.php:77-84`); enforced by `EnsureUserIsAdmin` middleware → 403 otherwise | Everything: all threshold-config CRUD tabs (business rules, condition logics, mappings, glossary, versions), domain management + domain-access matrix, YAML/CSV export, CSV bulk import, Rule Builder page, File Library writes (upload/replace/rename/move/delete), user management |
| **Non-admin (default role `cashier`)** | Default on registration (`app/Http/Controllers/Api/AuthController.php:123`) | Log in, view the SPA, **view and edit threshold values only within their allowed domains**, browse/preview/download the File Library (read-only) |
| **domain_owner** | Role value accepted at registration (`AuthController.php:104`); `domain_owner` middleware alias registered (`app/Http/Kernel.php:69`) | Treated as non-admin with domain scoping; the domains they own come from `user.domain` + `user_domain_access` rows |

**Domain scoping rule:** a non-admin's allowed domains = their home `user.domain` column plus
every row for them in `user_domain_access`
(`ThresholdConfigurationController@allowedDomainsFor()`, lines 45–77; filter applied at
lines 96–114). Admin bypasses the filter entirely (returns `null` = no filter).

## 4. Main Workflows

### 4.1 Log in
1. Open the app → SPA route `/login` (`resources/js/Account/Router.js:13-26`).
2. Submit email + password → `POST /api/login` (`routes/api.php:17`).
3. Server checks the account is active and the password hash matches, then issues a 32-char
   bearer token stored on the user row (`AuthController.php:30-80`).
4. The SPA stores the token (localStorage/sessionStorage) and sends
   `Authorization: Bearer <token>` on every request; `CheckAuthMiddleware` validates it per
   request (`app/Http/Middleware/CheckAuthMiddleware.php:13-30`).

### 4.2 Change a threshold value (admin or domain owner)
1. Open **Threshold Configurator** (`/threshold-configurator`) or **Business OS**
   (`/oil-configurator`).
2. Non-admins see only thresholds in their allowed domains (§3).
3. Edit the value; enter a change reason (currently optional — see §7 and §12).
4. Save → `PUT /api/threshold-config/thresholds/{thresholdId}` (`routes/api.php:35-78` group).
5. If the value actually changed (difference > 0.0000001), the system in one transaction:
   updates the threshold, stamps `last_changed_by`/`last_changed_at` (UTC), increments
   `version` by exactly 1, and writes an audit row (old value, new value, reason) to
   `threshold_versions` (`ThresholdConfigurationController.php:486-553`).

### 4.3 Author rule logic (admin only)
1. Open **Rule Builder** (`/rule-builder`) — route is admin-gated (`Router.js:19`).
2. Pick a business rule from the sidebar and compose its condition logic; referenced codes
   must exist: `GL-##` in `glossary`, `TH-##` in `thresholds`
   (`unknownConditionCodes()`, `ThresholdConfigurationController.php:233-262`).
3. Leaving with unsaved edits triggers a themed discard-guard modal on every exit path
   (delivery record: `archive/skills/2026-06-19__abiraj__blos__REQ-04-D05.md`).

### 4.4 Maintain BLOS reference data (admin only)
CRUD on the 8 admin tabs — business rules, condition logics, rule-threshold mappings,
glossary, thresholds, versions, domains, domain access — via
`/api/threshold-config/...` endpoints (`routes/api.php:41-78`). Codes are normalised
(uppercased, whitespace stripped: "gl- 005" → "GL-005") before validation
(`normalizeCodeFields()`, `ThresholdConfigurationController.php:116-129`).

### 4.5 Bulk import from CSV (admin only)
1. Prepare a CSV whose header row matches the target tab's columns.
2. `POST /api/threshold-config/bulk-import/{tab}` (`routes/api.php:76`) for tab =
   `business_rules` | `glossary` | `rule_threshold_mapping` | `condition_logics` |
   `thresholds` | `versions`.
3. Parser strips the BOM, trims cells, treats blanks as null, skips empty rows, validates
   each row against tab-specific rules, then inserts/updates
   (`parseCsvFile()` :971-1007, `bulkImport()` :1015+, rules :904-920).

### 4.6 Export the registry (admin only)
- **YAML:** `GET /api/threshold-config/export-yaml` → `rules_registry.yaml` mapping
  `threshold_key: value` (`exportYaml()`, :819-835).
- **CSV:** `GET /api/threshold-config/export-csv?tab={tab}` → full table dump (`exportCsv()`, :837-873).

### 4.7 Use the Central File Library
- Everyone (authenticated): browse the folder tree (`GET /api/folders/tree`), open a folder
  (`GET /api/folders/{folder}`), preview text files (`GET /api/files/{id}/content` — md, txt,
  json, xml, csv), download a file (`GET /api/files/{id}/download`) or a whole folder as ZIP
  (`GET /api/folders/{folder}/download-zip`) (`routes/api.php:81-95`).
- Admin only: create/rename/move/delete folders and files, upload, and **replace** a file —
  replacement shows a diff review modal and only commits after explicit Confirm
  (`app/Services/FolderFileService.php`; delivery record
  `archive/skills/2026-05-19__Abiraj__blos__REQ-01-D02.md`).

### 4.8 Manage users and domain access (admin only)
- Create users: `POST /api/add-new-users` (see caution in §8/§12 — endpoint is public);
  list/update: `GET/POST/PUT /api/users`.
- Grant/revoke a user's domain access:
  `GET/PUT/POST/DELETE /api/threshold-config/domain-access` (`routes/api.php:41-78`).

## 5. Key Pages / Modules / Routes

### SPA pages (`resources/js/Account/Router.js:13-26`)

| Route | Path | Component | Access |
|---|---|---|---|
| Dashboard | `/` | `Pages/Dashboard.vue` | Authenticated |
| Threshold Configurator | `/threshold-configurator` | `Pages/ThresholdConfigurator.vue` | Authenticated (domain-scoped) |
| Business OS | `/oil-configurator` | `Pages/OilConfigurator.vue` | Authenticated (domain-scoped) |
| Rule Builder | `/rule-builder` | `Pages/RuleBuilder.vue` | **Admin only** (`Router.js:19`) |
| File Manager | `/file-manager` | `Pages/FileManager.vue` | Authenticated (writes admin-only) |
| Login | `/login` | `Pages/auth/Login.vue` | Guest |
| `/register` | redirects to `/login` — no Register page exists (`Router.js:23`) | — | — |
| `/markdown-manager` | redirects to `/file-manager` | — | — |

### API groups (`routes/api.php`)

| Group | Prefix | Gate |
|---|---|---|
| Auth: login / register / configurations | `/api/login`, `/api/add-new-users`, `/api/configurations` | Public (`routes/api.php:16-19`) |
| Session: me / logout | `/api/me`, `/api/logout` | Bearer token (`:24`) |
| Threshold read + value update | `/api/threshold-config/thresholds`, `PUT /api/threshold-config/thresholds/{id}` | Token + domain scope |
| BLOS admin tabs, domains, domain-access, exports, bulk import, stats | `/api/threshold-config/...` | Token + **admin** (`:41`) |
| File Library reads | `/api/folders/...`, `/api/files/...` | Token (`:81-95`) |
| File Library writes | same prefixes | Token + **admin** |
| Catalog/POS: products, categories, inventory, sales, users | `/api/products`, `/api/sales`, `/api/users`, … | Token (users/products CRUD admin) |
| Stock sync | `GET /api/warehouse-location-wise-stock-update` | Public (`:22`) |

### Database (own schema — `DATABASE_SCHEMA.md`; migrations in `database/migrations/`)

- **BLOS:** `business_rules`, `condition_logics`, `glossary`, `rule_threshold_mapping`,
  `thresholds`, `threshold_versions` (append-only audit), `threshold_change_requests`
  (approval queue table — see §12), `user_domain_access`.
- **File Library:** `folders` (self-referential tree), `files` (managed files with
  mime/extension/size).
- **Users:** legacy `user` table (`user_email`, `user_password`, `config_role`,
  `user_status`, `token`, `domain`) accessed through accessors in `app/Models/User.php`.

## 6. Inputs and Outputs

| User input | System output |
|---|---|
| Login credentials | Bearer token; user profile (`/api/me`) |
| New threshold value + change reason | Updated threshold with `version` +1, `last_changed_by/at`; permanent `threshold_versions` audit row |
| Business rule / logic / glossary / mapping records (forms) | Validated, code-normalised records (422 with field errors if invalid) |
| CSV file per tab (bulk import) | Inserted/updated rows; per-row validation errors reported |
| Uploaded file (File Library, admin) | Stored file with slug-timestamp name, recorded mime type, extension, size (`app/Services/FolderFileService.php:160-191`) |
| Replacement file (admin) | Diff review modal (line diff / rendered) → committed only on Confirm |
| Export requests | `rules_registry.yaml` (key → value map); `{tab}.csv` full-table download; folder ZIP archives |
| Text file selection | In-browser preview (md/txt/json/xml/csv); 415 for non-text types |

## 7. Business Rules Found

All statements below are visible in code, config, docs, or SQL — nothing inferred.

1. **A threshold edit only counts as a change if it differs by more than 0.0000001** from the
   stored value (`ThresholdConfigurationController.php:531`).
2. **Every real change writes a `threshold_versions` audit row and bumps `version` by exactly
   1** — next version = max(current `version`, highest `version_number` in history) + 1,
   inside a DB transaction (`:539-551`).
3. **`change_reason` is currently OPTIONAL** (`nullable|string|max:1000`, `:516`) — an
   explicit TEMP deferral of the original `required|min:10` rule (commented at `:515`;
   deferral recorded in `archive/skills/2026-06-19__abiraj__blos__REQ-04-D05.md`). The
   reason, when given, is stored **only in history**, not on `thresholds` (`:513`).
4. **New thresholds must have a unique `threshold_id` matching `^TH-\d+$` and a unique
   `threshold_key`** (`:450-484`).
5. **Deleting a threshold cascades** — its `threshold_versions` and `rule_threshold_mapping`
   rows are deleted too (`:555-568`).
6. **Non-admins may only touch thresholds in their allowed domains** (home `domain` +
   `user_domain_access` rows); violations get 403 "You do not have access to this domain."
   (`:45-77`, `:96-114`, `:491`).
7. **Rule/glossary/threshold codes are normalised** (uppercase, whitespace stripped) before
   validation and save (`:116-129`).
8. **Condition logic may only reference codes that exist** — `GL-\d+` must be in `glossary`,
   `TH-\d+` in `thresholds`, otherwise the save is rejected (`:233-262`, rejection at `:273`).
9. **Login requires an active account** (`user_status` interpreted as active) and a matching
   password hash (`AuthController.php:30-80`; `User.php` `is_active` accessor).
10. **Admin-only middleware returns 403 "Admin access required"** for the BLOS admin tabs,
    exports, bulk import, File Library writes, and user CRUD (`EnsureUserIsAdmin`;
    `routes/api.php:41`).
11. **File replacement cannot commit without explicit admin confirmation** in the diff review
    modal (delivery record `archive/skills/2026-05-19__Abiraj__blos__REQ-01-D02.md`).
12. **No seed data:** the seeder is intentionally empty because production threshold data
    already exists (`database/seeders/DatabaseSeeder.php:15-19`).

## 8. What Users Must Not Do

- **Do not edit thresholds outside your domain** — the API refuses (403), and attempting it
  signals a domain-access misconfiguration that should be reported instead.
- **Do not delete a threshold without approval** — deletion permanently removes its entire
  version history and rule mappings (§7.5). Treat as an approval-required action.
- **Do not skip the change reason just because it is currently optional** — the governing
  rule (BLOS Build Guide) requires a ≥10-character reason; the validation is temporarily
  relaxed, the obligation is not (§7.3, §12).
- **Do not bulk-import a CSV you have not reviewed** — imports insert/update live reference
  data (admin action, no undo beyond version history on thresholds).
- **Do not run scripts from `docs/sql/` against the database casually** — e.g.
  `drop_threshold_snapshot_columns.sql` requires a privileged DB account and coordinated
  deployment (`archive/skills/2026-06-19__abiraj__blos__REQ-04-D05.md`).
- **Do not hardcode threshold values in consuming systems** — read them from the API/exports;
  that is the system's entire purpose (§2).
- **Do not share bearer tokens.** Note the current "Sign out" button only clears your browser
  storage — it does **not** call `POST /api/logout`, so the token stays valid on the server
  until a new login overwrites it (`Header.vue:232-240`; flagged for review in §12.4). A
  server-side logout endpoint exists but the UI does not call it.
- **Non-admins must not expect File Library write access** — upload/replace/delete are
  admin-gated by design.

## 9. Common User Tasks

**Log in:** open the site → enter email + password → you land on the Dashboard. If login
fails, check with an admin that your account is active.

**See your thresholds:** open *Threshold Configurator* (or *Business OS* for the
domain-grouped view). You will only see domains assigned to you — if a domain is missing, ask
an admin to add it in the Domain Access matrix.

**Change a threshold value:** find the row → edit the value → type WHY you are changing it in
the change-reason box → Save. Your name, the time, the old and new value are recorded
automatically; the version number goes up by 1. (Note: the change-reason box is currently
*not enforced* — Save works even if it's empty — and editing the same value through *Business
OS* records a generic reason instead of yours. Always type a real reason so the history stays
meaningful; see §12.8.)

**Check who changed a value and why:** open the threshold's version history (Versions tab /
history view) — every change is listed with old value, new value, who, when, and the reason.

**Export all current values:** (admin) *export YAML* for the machine-readable
`rules_registry.yaml`, or *export CSV* per tab for spreadsheets.

**Load many records at once:** (admin) prepare the CSV with the exact column headers of the
target tab → bulk import → fix any per-row validation errors it reports.

**Find and read a knowledge file:** open *File Manager* → navigate the folder tree → click a
file to preview (markdown/text/csv/json/xml render in-browser) → Download for a copy, or
Download-ZIP on a folder for everything inside.

**Replace a file with a new version:** (admin) choose Replace on the file → review the diff
the modal shows (removed lines red, added lines green) → Confirm to commit; Cancel leaves the
original untouched.

**Give a colleague access to a domain:** (admin) Domain Access matrix →
add the user–domain pair. Their Threshold Configurator view updates on next load.

## 10. Error / Exception Handling

| Status | Meaning in this app | Typical cause / message |
|---|---|---|
| 401 | Invalid or missing bearer token | "Invalid authentication" (`CheckAuthMiddleware.php:28`) — log in again |
| 403 | Allowed user, forbidden action | "Admin access required" (admin gate) or "You do not have access to this domain." (`ThresholdConfigurationController.php:491`) |
| 404 | Resource or file missing | e.g. file recorded in DB but missing on disk (`FolderFileController.php:48-51`) |
| 415 | File type cannot be previewed | Non-text file requested via `/files/{id}/content` (`FolderFileController.php:161-162`) |
| 422 | Validation failed | Response body: `{"success": false, "message": "Validation failed", "errors": {field: [...]}}` — fix the listed fields |
| 500 | Unhandled server error | Controllers wrap work in try/catch and return a JSON error (`AuthController.php:73-78`) — report to the developer/admin |

Bulk import reports row-level validation problems instead of silently skipping data
(`ThresholdConfigurationController.php:904-920`). A value edit that does not actually change
the number (≤ 0.0000001 difference) writes **no** version row — this is by design, not a bug.

## 11. Evidence Map

Status legend: **VERIFIED** = confirmed in the repository scan of 2026-07-07 ·
**PARTIAL** = supported by delivery/tracker documents but not fully confirmed in current code ·
**CONFIRMED-ABSENT** = the D07 analysis + git history proved the feature is not in the code
(removed by design or never built) · **DB-DATA** = a live-database question, not a code
question, and out of scope for this static analysis.

> **Rev 2 note:** the four items the first revision marked UNPROVEN/CONTRADICTED are now
> settled by the D07 verification pass (git-history pickaxe + full-tree grep). See
> `2026-07-07_REQ-04-D07_verification_findings.md` for the complete search trail.

| Claim | Evidence File/Path | Status |
|---|---|---|
| App is a central admin/operations hub over multiple company DBs | `DATABASE_SCHEMA.md:1-26` | VERIFIED |
| SPA routes: Dashboard, ThresholdConfigurator, OilConfigurator, RuleBuilder (admin), FileManager, Login | `resources/js/Account/Router.js:13-26` | VERIFIED |
| Rule Builder route is admin-only | `resources/js/Account/Router.js:19` | VERIFIED |
| No Register page; `/register` redirects to `/login` | `resources/js/Account/Router.js:23` | VERIFIED |
| Bearer-token auth on protected API routes | `app/Http/Middleware/CheckAuthMiddleware.php:13-30` | VERIFIED |
| Login flow: active check, hash check, 32-char token | `app/Http/Controllers/Api/AuthController.php:30-80` | VERIFIED |
| Roles: admin / cashier (default) / domain_owner | `app/Models/User.php:77-84`; `AuthController.php:104,123`; `app/Http/Kernel.php:69` | VERIFIED |
| Domain scoping = `user.domain` + `user_domain_access` | `ThresholdConfigurationController.php:45-77,96-114`; migration `2026_04_28_000002_create_user_domain_access_table.php` | VERIFIED |
| Threshold update: epsilon 0.0000001, version +1, audit row, transaction | `ThresholdConfigurationController.php:486-553` | VERIFIED |
| `change_reason` currently optional (TEMP), history-only | `ThresholdConfigurationController.php:513-516`; `archive/skills/2026-06-19__abiraj__blos__REQ-04-D05.md` | VERIFIED |
| Threshold ID format `^TH-\d+$`, unique key | `ThresholdConfigurationController.php:450-484` | VERIFIED |
| Delete cascades versions + mappings; domain check first | `ThresholdConfigurationController.php:555-568` | VERIFIED |
| Code normalisation (uppercase, strip spaces) | `ThresholdConfigurationController.php:116-129` | VERIFIED |
| Condition codes must exist in glossary/thresholds | `ThresholdConfigurationController.php:233-262` | VERIFIED |
| Admin tabs, domains, domain-access, stats endpoints | `routes/api.php:35-78` | VERIFIED |
| YAML export `rules_registry.yaml` | `ThresholdConfigurationController.php:819-835`; `routes/api.php:74` | VERIFIED |
| CSV export per tab | `ThresholdConfigurationController.php:837-873`; `routes/api.php:75` | VERIFIED |
| CSV bulk import per tab with row validation | `ThresholdConfigurationController.php:971-1007,1015+,904-920`; `routes/api.php:76` | VERIFIED |
| File Library: tree, folder view, preview, download, ZIP | `routes/api.php:81-95`; `app/Http/Controllers/Api/FolderFileController.php` | VERIFIED |
| Upload stores mime/extension/size with slug-timestamp name | `app/Services/FolderFileService.php:160-191` | VERIFIED |
| File Library writes admin-only | `routes/api.php:81-95` (admin group) | VERIFIED |
| Replace-file diff modal with Confirm — **only for previewable text files ≤900 KB**; binaries/large files replace with no review | `FileManager.vue:952-959` (`fmShouldOfferReplaceDiff`); D07 UI_REFERENCE | VERIFIED |
| Error codes 401/403/404/415/422/500 and messages | `CheckAuthMiddleware.php:28`; `ThresholdConfigurationController.php:491`; `FolderFileController.php:48-51,161-162`; `AuthController.php:38-42,73-78` | VERIFIED |
| Seeder intentionally empty (production data live) | `database/seeders/DatabaseSeeder.php:15-19` | VERIFIED |
| `threshold_change_requests` table is an **orphaned** migration — its model was deleted, no code uses it | migration `2026_04_28_000001`; model removal in commit `f8804b8`; grep of `app/` finds zero references | VERIFIED |
| HIGH-impact change **approval workflow** — **removed by design**, not merely missing | existed at `09c85d7` (`changeRequestsApprove/Reject`), removed by commit `f8804b8` (2026-06-17 "remove … change-request/impact-approval"); D07 VERIFICATION_FINDINGS Q1 | CONFIRMED-ABSENT |
| Impact preview (`thresholdsImpactPreview`) — **removed by design** | route + method deleted by `f8804b8`; only dead `.tc-impact*` CSS remains; D07 VERIFICATION_FINDINGS Q2 | CONFIRMED-ABSENT |
| Consumer GET API (`/thresholds/{key}`, snapshot, `BLOS_API_KEY`) — **never built** | pickaxe across all branches returns nothing; tracker's "Stage 2 DONE" is incorrect; D07 VERIFICATION_FINDINGS Q3 | CONFIRMED-ABSENT |
| Registration: `POST /api/add-new-users` is **public and has been since creation** (base code, `24169cf` sajeesans2 2026-04-16); accepts `role=admin` unauthenticated | `routes/api.php:16`; `AuthController.php:104,123`; D07 VERIFICATION_FINDINGS Q4 | VERIFIED (P0 security — §12) |
| Business OS renders thresholds across domains | `OilConfigurator.vue`; D05 records 35 rows in `thresholds` | DB-DATA (exact counts are a live-DB question) |
| Live deployment at centralizer.vintageinterior.co.uk | `archive/skills/2026-06-19__abiraj__blos__REQ-04-D05.md`; `.vscode/sftp.json` (host + remotePath) | VERIFIED (from committed config) |
| Sign-out clears only browser storage — does **not** call `POST /api/logout`; server token stays valid | `Header.vue:232-240`; D07 SECURITY_AND_DEPLOY F-7 | VERIFIED |
| Threshold tables created by hand-run `docs/sql/*.sql` (string PKs), not Laravel migrations | `docs/sql/*.sql`; D07 CODE_MAP, DATA_DICTIONARY | VERIFIED |

## 12. Known Limits

**Security findings — for Sajeesan's technical review (facts only; not fixed by this task).**
Full detail in `2026-07-07_REQ-04-D07_security_and_deploy.md` and `..._verification_findings.md`.

1. **Privilege escalation (P0):** `POST /api/add-new-users` is public and accepts `role=admin`
   in the body (`routes/api.php:16`; `AuthController.php:104,123`) — anyone can mint an admin
   account. Confirmed base code, public since 2026-04-16, **not** a regression.
2. **Committed production credential (P0):** `.vscode/sftp.json` holds the live server host and
   a **plaintext password** with `uploadOnSave: true` → production. Rotate and purge from git.
3. **Unauthenticated user dump:** `GET /api/test` returns `User::all()` (`AuthController.php:82-91`).
4. **Sign-out doesn't revoke the token:** the UI clears browser storage only and never calls
   `POST /api/logout` (`Header.vue:232-240`), so a leaked token stays valid server-side.
5. **Dead routes:** `routes/api.php` binds six controllers that don't exist
   (Product/Category/Sale/Inventory/Report/Image) → 500 on dispatch.

**Design decisions (resolved — recorded so they are not mistaken for gaps):**

6. **Approval workflow & impact preview were removed on purpose** in commit `f8804b8`
   (2026-06-17) during the BLOS schema migration — they are not missing features to "finish".
   `threshold_change_requests` remains only as an orphaned table to drop.
7. **The consumer GET API was never built** (verified across all branches) — the May tracker's
   "Stage 2 DONE" is wrong. Building one would be net-new work, not a resume.
8. **`change_reason` enforcement is switched off** in both API (`nullable`, TEMP) and UI
   (`canSave` always true, `ThresholdConfigurator.vue:832-838`); `OilConfigurator.vue:461-462`
   hard-codes a generic reason. Audit-trail quality depends on which screen an edit came from.
   Whether to restore the ≥10-char rule is a held decision (MD / Sajeesan).

**Scope limits of this document:**

9. **The imported tracker is dated 2026-05-20 and pre-dates the June migration** — where it
   disagrees with the code, the code wins. Data-population claims (BL-## count,
   `user_domain_access` rows) are **DB-DATA** questions not re-verified against the live
   database by this static analysis.
10. **Runtime behaviour was not exercised** — no requests were made to the live system and no
    DB queries were run; all claims are from source files + git history.
11. The repo docs `BLOS-Rule-Builder-*` describe a **planned** redesign (not implemented);
    `database sample.txt` and `DATABASE_SCHEMA.md` are **stale** (pre-June schema) — do not read
    them as current truth. Use the D07 DATA_DICTIONARY instead.

## 13. Owner / Reviewer

- Coordinator: Varmen
- Queryability Reviewer: Tamil Selvan
- Technical Reviewer: Sajeesan
- Business Validator: *(to be assigned per task type)*

## 14. Pass / Fail Rule

**PASS** if: all 15 sections are present; every claim in §1–§10 appears in the §11 Evidence
Map with a real file path; every PARTIAL / CONFIRMED-ABSENT / DB-DATA / security item is listed
in §12; no application file was modified; and a new user, support person, or LLM can correctly
answer "what is this app, who can do what, and how do I do X" using only this file and the
cited paths — with no verbal explanation.

**FAIL** if any claim rests on guesses, chat memory, or undocumented assumptions, or if a
duplicate user guide is later found that this file should have extended instead.

## 15. Next Step

Submit this Rev 2 draft (with the full D07 companion package) to **Tamil Selvan (Queryability
Reviewer)** and **Sajeesan (Technical Reviewer — priority: the §12.1 privilege-escalation and
§12.2 committed-credential P0 findings)**; record the verdict in
`validation/REQ-04_ledsone-centralizer-user-skill/`. Developers continuing the project should
start from `2026-07-07_REQ-04-D07_continuation_guide.md`.


---

# PART B — CONTINUATION GUIDE

---

# LEDsONE Centralizer / BLOS — Continuation Guide

> **The "continue without Abiraj" document.** If you are a new developer or leader picking up
> this project, start here. It tells you the exact current state of the system (re-verified
> against today's code, not the older tracker), what is done, what is deliberately removed,
> what is genuinely open, and precisely how to keep going.

| Field | Value |
|---|---|
| date | 2026-07-07 |
| deliverable | REQ-04-D07 |
| project | PRJ-2026-003_blos-project-sentinel |
| status | DRAFT — awaiting Queryability (Tamil Selvan) + Technical (Sajeesan) review |
| evidence basis | Direct read-only scan of `ledsone-centralizer` on 2026-07-07 + git history; six companion documents in this folder |
| companion documents | CODE_MAP · DATA_DICTIONARY · API_REFERENCE · UI_REFERENCE · SECURITY_AND_DEPLOY · VERIFICATION_FINDINGS · SHARED_MODULES_INVENTORY (all dated 2026-07-07, REQ-04-D07) |

---

## 0. Read-order for a new person

1. **This guide** — where the project stands and how to continue.
2. **The user skill file** (`2026-07-07_ledsone-centralizer_user_skill.md`) — how to *use* the system.
3. **CODE_MAP** — where every file lives.
4. **API_REFERENCE / DATA_DICTIONARY / UI_REFERENCE** — the reference layer when you touch a specific endpoint, table, or screen.
5. **SECURITY_AND_DEPLOY** — before you deploy anything.
6. **VERIFICATION_FINDINGS + SHARED_MODULES_INVENTORY** — why the older tracker disagrees with the code, and which code is *not* yours.

---

## 1. What this system is (one paragraph)

LEDsONE Centralizer is a Laravel 9 + Vue 2 admin/operations hub. **The BLOS (Business Logic
Operating System) part — the only part this project owns — is a governed registry of business
rules (`BL-###`), the numeric thresholds those rules use (`TH-###`), a glossary of metrics
(`GL-###`), and the mappings between them (`MAP-###`), all with an append-only change history.**
Admins author rule logic in a drag-and-drop Rule Builder and manage threshold values through a
7-tab configurator; domain owners can edit values inside their assigned domains. A separate
Central File Library (SkillVault) stores folders and files. The same repository also hosts
**other teams'** POS, PPC/ETL and inventory code — see §7 and the Shared-Modules Inventory;
that code is not BLOS and not this project's responsibility.

## 2. Architecture at a glance (all verified 2026-07-07)

| Concern | Reality | Evidence |
|---|---|---|
| Backend | Laravel 9, PHP 8.0 | `composer.json` |
| Frontend | Vue 2 + BootstrapVue SPA, single Laravel Mix entry `Account.js` → `public/js/Account.js` (git-ignored) | `webpack.mix.js`, `resources/js/Account.js` |
| **All BLOS backend logic** | **ONE controller** — `app/Http/Controllers/Api/ThresholdConfigurationController.php` (~1,100 lines, 35 endpoints under `/api/threshold-config/*`) | CODE_MAP §controllers |
| BLOS models (6) | `BusinessRule`, `ConditionLogic`, `Threshold`, `ThresholdVersion`, `RuleThresholdMapping`, `Glossary` | DATA_DICTIONARY |
| **BLOS rule engine (frontend)** | 3 files — `Pages/RuleBuilder.vue`, `components/RuleNode.vue` (recursive node editor), `components/ruleLogic.js` (pure parse/serialise of `IF GL-001 < TH-001 AND …` strings) | UI_REFERENCE |
| Threshold admin UI | `Pages/ThresholdConfigurator.vue` (CRUD over 7 tabs) + `Pages/OilConfigurator.vue` (Business OS value view) | UI_REFERENCE |
| File Library | `FolderFileController` + `FolderFileService`; `Pages/FileManager.vue` (4,749 lines — the largest file); tables `folders` + `files` | CODE_MAP, DATA_DICTIONARY |
| Auth | Custom 32-char bearer token on the legacy **`user`** table + `CheckAuthMiddleware`; Sanctum installed but unused; roles `admin` / `cashier` / `domain_owner`; non-admins domain-scoped via `user_domain_access` | SECURITY_AND_DEPLOY |
| Databases | default `mysql` (BLOS + users + files), `orders` (inventory), `ppc` (ad ETL), `accounts_management` (unused) | CODE_MAP, config/database.php |

## 3. The one thing you must understand: the June schema migration

The imported requirements tracker (`skill_requirement_tracker.md`) is dated **2026-05-20** and
describes an **older BLOS design**. On **2026-06-17, commit `f8804b8`** ("Migrate threshold
config to new BLOS schema") you (digitwebabiraj) **deliberately re-architected BLOS** and
removed several things the tracker still lists as built. Then **2026-06-19, commit `bc1204a`**
dropped two now-redundant threshold columns. **Today's code reflects the post-migration
design; the tracker does not.** This single fact explains almost every discrepancy below.

What the migration changed (verified in the commit message and current code):
- **Added** the current core: `condition_logics`, `rule_threshold_mapping`, `glossary`;
  `business_rules` repointed to a string PK (`BL-###`) with new columns.
- **Removed** (by design, not lost): the change-request / impact-approval workflow, the impact
  preview, `threshold_dependencies`, and `BusinessRuleCategoricalMapping`.
- **Changed** threshold saves to **immediate**, each writing a `threshold_versions` audit row.
- `bc1204a` then dropped `thresholds.previous_value` and `thresholds.change_reason` (now
  history-only).

## 4. The four questions D06 left open — now settled

| Question | Verdict (2026-07-07) | Proof |
|---|---|---|
| HIGH-impact **approval workflow** exists? | **CONFIRMED-ABSENT** — existed pre-migration (`09c85d7` had `changeRequestsApprove/Reject`), removed by `f8804b8`. Zero code touches `threshold_change_requests` today; only an orphaned migration + stale schema doc remain | VERIFICATION_FINDINGS Q1 |
| **Impact preview** exists? | **CONFIRMED-ABSENT** — `thresholdsImpactPreview()` + `impact-preview` route deleted by `f8804b8`; only dead `.tc-impact*` CSS remains | VERIFICATION_FINDINGS Q2 |
| **Consumer GET API** (`/thresholds/{key}`, snapshot, `BLOS_API_KEY`) exists? | **CONFIRMED-ABSENT** — pickaxe across *all* branches finds nothing; it was **never committed**. The tracker's Stage-2 "DONE" is wrong | VERIFICATION_FINDINGS Q3 |
| **Registration** admin-controlled? | **CONFIRMED public since creation** (`24169cf`, sajeesans2, 2026-04-16) — not a regression; base code. `0956069` removed only the SPA signup screen. **`register()` accepts `role=admin` unauthenticated** | VERIFICATION_FINDINGS Q4 |

## 5. Current status of the BLOS Build Guide's 9 stages (re-baselined against today's code)

| Stage | Tracker said (May) | **Actual today** | Note |
|---|---|---|---|
| 1 Schema & DB | DONE | **DONE — but built by hand-run `docs/sql/*.sql`, not Laravel migrations**; string PKs BL-/TH-/GL-/MAP- | Fresh-DB rebuild needs the SQL scripts, not `artisan migrate` |
| 2 API Layer | DONE | **PARTIAL** — admin CRUD API (35 endpoints) exists and works; the **consumer GET API was never built** | Tracker overstated |
| 3 Domain & Key Setup | GAP-CRITICAL | **Data-dependent, not re-verified live** — the code path (`allowedDomainsFor`, `user_domain_access`) exists; whether rows/rules are loaded is a DB-data question | Verify against live DB before trusting |
| 4 Impact Simulation | PARTIAL | **REMOVED BY DESIGN** (`f8804b8`) — no longer a gap; it's a closed decision | Do not "finish" it without a new requirement |
| 5 Domain Owner UI | DONE | **DONE** — `ThresholdConfigurator.vue` + `RuleBuilder.vue` (+ recursive `RuleNode.vue`, `ruleLogic.js`) | Solid |
| 6 Skill Pack | NOT STARTED | **IN PROGRESS** — the D06 user skill file + this D07 package are the first entries | Continue here |
| 7 Consumer Governance | NOT STARTED | **NOT STARTED** | Blocked on Stage 2 consumer API decision |
| 8 3AM Documentation | PARTIAL | **ADVANCED by D07** — code map, data dictionary, API ref, security & deploy runbook now exist | Monitoring guide + failure runbook still to write |
| 9 Sign-Off & Go-Live | NOT STARTED | **NOT STARTED** | Depends on 2/3/6/7 |

## 6. What to do next (concrete, prioritised)

**P0 — take to Sajeesan immediately (security; findings only, not fixed here):**
1. **Committed production credentials:** `.vscode/sftp.json` contains a live server host + a
   plaintext password with `uploadOnSave: true` → production. Rotate the password, purge the
   file from git history, and add it to `.gitignore`. (SECURITY_AND_DEPLOY, CODE_MAP §root.)
2. **Privilege escalation:** `POST /api/add-new-users` is public and accepts `role=admin`.
   Gate it behind admin auth or strip role from the payload. (API_REFERENCE, VERIFICATION Q4.)
3. **Unauthenticated user dump:** `GET /api/test` returns `User::all()`. Remove it.
4. **Dead routes:** `routes/api.php` binds six controllers that don't exist
   (Product/Category/Sale/Inventory/Report/Image) → these 500 on dispatch. Remove or implement.

**P1 — data-model hygiene:**
5. Drop the orphaned `threshold_change_requests` table + its migration (workflow is gone).
6. Fix the fresh-DB hazard: migration `2026_04_28_000002` adds `proposed_value AFTER
   previous_value`, but `previous_value` was dropped — a clean rebuild will fail. Reconcile the
   migrations with the hand-run `docs/sql` DDL so a new environment can be built repeatably.
7. Decide the **`change_reason` policy**: the ≥10-char rule is switched off in both the API
   (`nullable`, TEMP comment) and the UI (`canSave` always true); OilConfigurator hard-codes a
   generic reason. Either restore the rule or document the relaxation as permanent.

**P2 — continue the documented roadmap:**
8. Finish Stage 8: write the monitoring guide and failure runbook (the two 3AM-standard docs
   still missing).
9. Decide Stage 2/7: is a governed consumer API (for other systems to read thresholds) still
   wanted? If yes it is net-new build, not a "resume". If no, close Stages 2/7 as descoped.
10. Update the repo's own `docs/skill.md` engineering log and reconcile `DATABASE_SCHEMA.md`
    (it still documents the pre-June schema).

## 7. What is NOT yours (do not touch, do not document as BLOS)

Roughly 50 files in this repo belong to other work streams (full list in
SHARED_MODULES_INVENTORY):
- **POS/catalog & order management** (models `Product`, `Category`, `Sale`, `SaleItem`,
  `Image`, `ImageType`, `Inventory`; `StockController`) — owner **sajeesans2**.
- **PPC/ETL** (26 `CentralizedEtlData` models, `TestingController`, `ppc:etl-data` command) —
  owner **gajan**.
- **Inventory DB models**, websockets, jobs/events, base auth scaffolding — sajeesans2.

None of these has an Account-SPA page (the SPA router has only the five BLOS screens). If you
open the repo and see this code, it is shared infrastructure — leave it to its owners.

## 8. First week for a new developer (checklist)

1. Read this guide + the user skill file end to end.
2. Get the repo; `composer install`, `npm install`; build the SPA with `npm run development`.
   Confirm you understand: **save = live** on the server, and the frontend must be rebuilt for
   JS changes to appear. (SECURITY_AND_DEPLOY Part 2.)
3. **Before any DB change:** remember the web DB user lacks `ALTER` — DDL runs under a
   privileged account, and BLOS tables are created by `docs/sql/*.sql`, not migrations.
4. Trace one full BLOS flow yourself: open Threshold Configurator → change a value → confirm a
   `threshold_versions` row appears and `version` increments. (API_REFERENCE `thresholdsUpdate`.)
5. Trace one rule in the Rule Builder → read `ruleLogic.js` to see how `IF GL-### < TH-###`
   strings parse into the recursive `RuleNode` tree.
6. Read VERIFICATION_FINDINGS so you don't chase features (approval workflow, impact preview,
   consumer API) that were removed or never built.
7. Action the P0 security items with Sajeesan before shipping anything.

## 9. Held decisions (need a named human, not a developer choice)

| Decision | Who decides | Status |
|---|---|---|
| `change_reason` mandatory or permanently optional | MD / Sajeesan (data-quality owner) | Open — currently off |
| Rebuild a governed consumer API (Stage 2/7) or descope it | MD / Coordinator (Varmen) | Open |
| SkillVault Phase-1 classification (version ledger, download tracking — per tracker Part 2) | MD | Open — inherited from tracker |
| Whether the removed approval workflow should ever return | Business owner | Closed by `f8804b8` unless reopened |

---

*Continuation Guide — REQ-04-D07 — evidence-backed, by-reference; the `ledsone-centralizer`
repository remains the single source of code truth.*


---

# PART C — CODE MAP

---

# CODE MAP — ledsone-centralizer

| Field | Value |
|---|---|
| **Date** | 2026-07-07 |
| **Deliverable** | REQ-04-D07 |
| **Project** | PRJ-2026-003_blos-project-sentinel |
| **Status** | DRAFT — code mapped **by reference only**; the repository remains the canonical source of truth (no-duplicate-truth rule). No code bodies are copied here; only paths, purposes, and symbol signatures. |
| **Repository** | `C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer` (Laravel 9 / PHP ^8.0.2 backend + Vue 2 SPA) |
| **Method** | Every entry below was produced from a direct read of the named file (or a symbol-level grep of it) on 2026-07-07. |

---

## How to read this map

- **FULL entries** list every public method/symbol with a one-line description.
- **One-line entries** are either framework boilerplate (marked *boilerplate*) or shared-repo modules outside BLOS scope (marked **Shared-repo module — NOT BLOS scope**).
- "BLOS" = the Business Logic Operating System feature set: business rules, condition logics, thresholds, threshold versions, rule↔threshold mappings, glossary, Rule Builder UI, Threshold Configurator UI.

### Orientation in 60 seconds

- **All BLOS backend logic is in ONE controller**: `app/Http/Controllers/Api/ThresholdConfigurationController.php` (≈1,100 lines), operating on six small root models (`BusinessRule`, `ConditionLogic`, `Threshold`, `ThresholdVersion`, `RuleThresholdMapping`, `Glossary`).
- **All BLOS frontend logic is in three files**: `resources/js/Account/Pages/RuleBuilder.vue`, `resources/js/Account/components/RuleNode.vue`, and the pure-JS engine `resources/js/Account/components/ruleLogic.js` (plus the CRUD UI `ThresholdConfigurator.vue`).
- **BLOS tables have NO Laravel migrations** — they are created by hand-run SQL in `docs/sql/*.sql` (string business-code PKs: `BL-001`, `TH-001`, `GL-001`, `MAP-001`). `DATABASE_SCHEMA.md` documents this split.
- **Auth is custom token auth, not Sanctum/session**: `AuthController@login` writes a 32-char token to the legacy `user` table; `CheckAuthMiddleware` matches the Bearer token. The `User` model maps legacy columns (`user_email`, `user_password`, `config_role`, `user_status`) through accessors.
- **Dead references exist**: `routes/api.php` imports six controllers that do not exist in this repo (Category/Product/Inventory/Sale/Report/Image), and `app/Jobs/CreateBulkRuleRun.php` references models (`Order`, `Flag`, …) not present here — vestiges of the shared repo; those routes/jobs would fatal if invoked.

---

## Top-level directory overview

| Path | Files | Role |
|---|---|---|
| `app/` | 86 | Backend PHP: controllers, middleware, models, jobs, events, service, console command |
| `bootstrap/` | 6 | Laravel bootstrap + framework cache (boilerplate/generated) |
| `config/` | 16 | Laravel configuration (multi-DB, CORS, websockets are the customized ones) |
| `database/` | 9 | 7 migrations + empty seeder + user factory (BLOS tables are NOT migrated here) |
| `docs/` | 15 | BLOS design docs (4 md + 1 html mockup) + 10 hand-run SQL scripts for BLOS tables |
| `lang/` | 4 | Stock English translation files (boilerplate) |
| `public/` | 12* | Web root: entry point, static images/fonts, mix manifest (*excludes 14 built js/css artifacts) |
| `resources/` | 31 | Vue 2 SPA (`js/Account/**`), shared JS plumbing, 3 Blade views, css/scss |
| `routes/` | 4 | `api.php` (all real endpoints), `web.php` (SPA catch-all), channels, console |
| `scripts/` | 0 | Empty directory |
| `tests/` | 4 | Stock example tests only (boilerplate) |
| *(root)* | 22 | composer/package manifests, webpack.mix, phpunit, schema handbook, AI-agent memory files, editor/deploy configs |

Total: **209 files** walked (see Coverage statement at the end).

---

## Root files

### `composer.json` — FULL
PHP dependency manifest. Name `laravel/laravel` (never renamed), PHP `^8.0.2`, `laravel/framework ^9.19`.
- Key non-stock requires: `beyondcode/laravel-websockets ^1.13` (self-hosted websocket server), `cboden/ratchet ^0.4.4` (websocket transport), `laravel/sanctum ^3.0` (installed but unused — auth is custom token), `pusher/pusher-php-server ^7.2` (broadcast driver), `elibyy/tcpdf-laravel ^10.0` + `webklex/laravel-pdfmerger ^1.3` (PDF generation/merge), `league/flysystem-aws-s3-v3 ^3.29` (S3/Contabo disks), `guzzlehttp/guzzle ^7.2`.
- Dev: faker, pint, sail, mockery, phpunit, collision, spatie/laravel-ignition. Stock Laravel scripts (post-autoload-dump, post-update-cmd, etc.).

### `composer.lock` — one line
Locked dependency graph for composer.json (generated; not documented further).

### `package.json` — FULL
NPM manifest for the Vue 2 / Laravel Mix frontend.
- Scripts: `dev`/`development` (mix), `watch`, `watch-poll`, `hot`, `prod`/`production`.
- devDependencies: `laravel-mix ^6`, `vue ^2.6.14` + `vue-loader ^15` + `vue-template-compiler`, `bootstrap ^5.1.3`, `sass`/`sass-loader`, `axios ^0.25`, `laravel-echo ^1.16`, `pusher-js ^7.6`, `lodash`, `postcss`, `@popperjs/core`, `resolve-url-loader`.
- dependencies: `bootstrap-vue ^2.22`, `vue-router ^3.5`, `vuex ^3.6`, `chart.js ^4.2`, `marked ^18` + `marked-highlight` + `highlight.js` (markdown preview in File Manager), `socket.io-client ^4.8`, `ws ^8.18`, `vue-shortkey ^3.1`.

### `package-lock.json` — one line
NPM lockfile (generated).

### `phpunit.xml` — FULL
PHPUnit config: bootstrap `vendor/autoload.php`; two suites — `Unit` (`tests/Unit`) and `Feature` (`tests/Feature`); coverage includes `./app`; test env vars: `APP_ENV=testing`, `BCRYPT_ROUNDS=4`, `CACHE_DRIVER=array`, `MAIL_MAILER=array`, `QUEUE_CONNECTION=sync`, `SESSION_DRIVER=array`, `TELESCOPE_ENABLED=false` (sqlite in-memory DB lines are commented out). Stock boilerplate otherwise.

### `webpack.mix.js` — FULL
Laravel Mix build config — the whole frontend build.
- `mix.js('resources/js/Account/Account.js', 'public/js')` — single SPA entry → `public/js/Account.js`.
- `.sass('resources/scss/app.scss', 'public/css')` — compiles the (currently empty) SCSS entry.
- `.vue()` — Vue 2 single-file-component support.
- `.webpackConfig({resolve.alias})` — aliases `marked$`, `highlight.js$`, `marked-highlight$` to concrete dist files in node_modules.
- `.disableNotifications()`.

### `DATABASE_SCHEMA.md` — FULL (reference)
51-section hand-off handbook describing every DB connection, table, column and CRUD flow. Key content verified: distinguishes **app-owned tables** (created by this repo's migrations: `folders`, `files`, `threshold_change_requests`, `user_domain_access`, `websockets_statistics_entries`) from **external/pre-existing tables** (`user`, `thresholds`, `business_rules`, `inv_products`, all PPC tables — no migrations here; source of truth is the live DBs). Documents the connection map: `mysql` (default/main), `orders` (order-management DB), `order_management` (duplicate alias), `ppc` (advertising ETL DB), `accounts_management` (configured, unused by models).

### `README.md` — one line
*Boilerplate* — stock Laravel framework README, no project-specific content.

### `MEMORY.md` — one line
AI-assistant project memory / changelog protocol file ("Project Sentinel", append-only changelog rules); note its header claims Laravel 10/Tailwind, which does **not** match the actual stack (Laravel 9 + BootstrapVue).

### `readme.json` — one line
Sample eBay "GetOrders" API response payload (test fixture data from 2022; not code).

### `readme.txt` — one line
Orphaned Vue template snippet (old chat/message UI markup); scratch file, not used.

### `database sample.txt` — one line
99-line scratch SQL sketch of a generic `users`/POS schema (`CREATE TABLE users …`); NOT the real schema (real `user` table is legacy; see DATABASE_SCHEMA.md).

### `artisan` — one line
*Boilerplate* — stock Laravel CLI entry script.

### `.env` — one line
Live environment secrets (DB credentials, Pusher keys). Present in repo working tree; intentionally not documented further.

### `.env.example` — FULL (key groups)
Template env. Groups verified: `APP_*` (name "Ledsone centralizer"), `LOG_*`, `DB_*` (default DB `message_app`; note the extra per-connection prefixes `DB_*_ORDER_MANAGEMENT`, `DB_*_PPC`, `DB_*_ACCOUNTS_MANAGEMENT` used by config/database.php are NOT listed in the example), `BROADCAST_DRIVER=pusher`, `CACHE/FILESYSTEM/QUEUE/SESSION`, `MEMCACHED/REDIS`, `PUSHER_*` (hardcoded app id/key/secret pointing at self-hosted `message.vintageinterior.co.uk:6001`), `VITE_PUSHER_*` mirrors, `EBAY_API_TOKEN`.

### `.gitignore` — one line
Stock Laravel ignores plus custom: `public/js/Account.js` (built bundle), `.scannerwork`, `.claude/`, and unusually `composer.json/lock` + `package.json/lock` are ignored (manifest changes are untracked — beware).

### `.editorconfig` — one line
*Boilerplate* — UTF-8, LF, 4-space indent (2 for YAML).

### `.cursorrules` — one line
Cursor AI agent rules: memory protocol requiring MEMORY.md read/update per session ("Project Sentinel"; stack description outdated as in MEMORY.md).

### `.cursor/rules/project-memory.mdc` — one line
Same Cursor memory protocol in `.mdc` rule form (`alwaysApply: true`).

### `.cursorignore` — one line
Cursor indexing ignores (node_modules, vendor, .env, .vscode).

### `.hintrc` — one line
webhint config extending `development` with several accessibility hints disabled (axe/forms, image-alt, button-type, no-inline-styles).

### `.vscode/sftp.json` — one line
VS Code SFTP deploy config: `uploadOnSave: true` to host `207.148.78.148:22`, remote path `/opt/lampp/htdocs/ledsone-centralizer` — **live-server deploy-on-save is enabled**; treat edits as production-affecting.

---

## app/

### app/Casts

#### `app/Casts/CompactDecimal.php` — FULL
Custom Eloquent cast used by `Threshold.value` and `ThresholdVersion.old_value/new_value` to strip DECIMAL padding (e.g. `1000.0000` → `"1000"`).
- `get($model, string $key, $value, array $attributes)` — returns the numeric string with trailing zeros/decimal point trimmed; passes through null/non-numeric.
- `set($model, string $key, $value, array $attributes)` — stores the value unchanged (empty string → null).

### app/Console

#### `app/Console/Kernel.php` — one line + flag
*Near-boilerplate with disabled custom schedule*: `$commands` and `schedule()` contain only a commented-out daily `command:PpcEtlData` at 05:45 Asia/Colombo — **no cron is active**; `commands()` auto-loads `app/Console/Commands`.

#### `app/Console/Commands/Ppc/PpcEtlData.php` — FULL (Shared-repo module — NOT BLOS scope)
Custom artisan command `command:PpcEtlData` (~1,700 lines): syncs Amazon/eBay/Google Ads dimension + performance data into the unified `ppc_etl` / `ppc_etl_performance_data` tables. Public methods (each an ETL step, verified by grep):
- `handle()` — orchestrates all steps below with logging.
- `saveAmazonCampaignsMetadataToPpcEtl()` / `saveAmazonAdGroupsMetadataToPpcEtl()` / `saveAmazonPerformanceDataToPpcEtlPerformanceData()`.
- `saveEbayCampaignsMetadataToPpcEtl()` / `saveEbayAdGroupsMetadataToPpcEtl()` / `saveEbayPriorityStrategyCampaignPerformanceDataToPpcEtlPerformanceData()` / `saveEbayGeneralStrategyCampaignPerformanceDataToPpcEtlPerformanceData()` / `saveEbayAdPerformanceDataToPpcEtlPerformanceData()`.
- `saveGoogleAdsCampaignsMetadataToPpcEtl()` / `saveGoogleAdsAdGroupsMetadataToPpcEtl()` / `saveGoogleAdsCampaignPerformanceDataToPpcEtlPerformanceData()` / `saveGoogleAdsProductPerformanceDataToPpcEtlPerformanceData()` / `saveGoogleAdsAssetGroupsMetadataToPpcEtl()` / `saveGoogleAdsAssetsMetadataToPpcEtl()` / `saveGoogleAdsAssetsPerformanceDataToPpcEtlPerformanceData()`.

### app/Events

#### `app/Events/MessageSent.php` — FULL
Broadcast event (`ShouldBroadcast`) carrying an arbitrary `$message` payload.
- `__construct($message)` — stores payload. `broadcastWith()` — returns payload. `broadcastOn()` — `PrivateChannel('chat')`.

#### `app/Events/OrderUpdateEvents.php` — FULL (Shared-repo module — NOT BLOS scope)
Broadcast event used by the bulk jobs to push order progress over laravel-websockets.
- `__construct($data)` — stores payload. `broadcastWith()` — returns payload. `broadcastOn()` — `PrivateChannel('orders-updates.orders')`.

### app/Exceptions

#### `app/Exceptions/Handler.php` — one line
*Boilerplate* — stock Laravel 9 handler (dontFlash password fields, empty `register()` reportable).

### app/Http/Controllers

#### `app/Http/Controllers/Controller.php` — FULL
Abstract base controller; uses `AuthorizesRequests`, `DispatchesJobs`, `ValidatesRequests` traits. No methods of its own (*boilerplate*).

#### `app/Http/Controllers/auth/AuthController.php` — FULL
Custom token auth (NO Sanctum, NO session guard). Login writes a `Str::random(32)` token to the legacy `user` table; every later request is matched by `CheckAuthMiddleware`.
- `__construct()` — empty.
- `login(Request $request)` — validates email/password; loads `User` by `user_email`; checks `is_active` + `Hash::check` against `password_hash` accessor; rotates 32-char token; returns `{token, user{id,name,email,role,domain}}`.
- `TEst()` — debug endpoint: returns ALL users as JSON (mounted at `GET /api/test`; a data-exposure risk to note).
- `register(Request $request)` — validates (unique `user.user_email`, role in admin/cashier/domain_owner, password+confirmPassword) and creates a user with hashed password + fresh token.
- `me(Request $request)` — returns the authenticated user's profile (id, name, email, role, domain); used by the SPA on every route change.
- `logout(Request $request)` — nulls the `token` column for the Bearer token's user.
- `configurations(Request $request)` — returns basic app config (`app_name`, `app_env`, `version`) and echoes back the token if valid; used by the SPA boot screen.

#### `app/Http/Controllers/Api/ThresholdConfigurationController.php` — FULL — **the BLOS backend**
Single controller (~1,100 lines) implementing every BLOS endpoint under `/api/threshold-config/*`: CRUD for the six BLOS tables, domain-based access control, stats, domain admin, CSV/YAML export, CSV bulk import. Uses `Symfony\Component\Yaml`.
- Protected helpers: `isAdmin($user)` — role check; `userIdFrom($user)` — int PK; `allowedDomainsFor($user)` — merges the user's home `domain` column with `user_domain_access` pivot rows (null = admin sees all); `ensureDomainAllowed($user, $domain)` — per-row domain guard; `applyThresholdDomainFilterForNonAdmin($q, $user)` — SQL domain filter; `normalizeCodeFields(Request, array $fields)` — uppercases/strips whitespace on business codes ("gl- 005" → "GL-005").
- Business rules: `businessRulesIndex()`, `businessRulesStore(Request)`, `businessRulesUpdate(Request, $ruleId)`, `businessRulesDestroy($ruleId)` — CRUD on `business_rules` (string PK `BL-\d+`).
- Condition logics: `conditionLogicsIndex(Request)` (filterable by `rule_id`/`stage`), `conditionLogicsStore(Request)`, `conditionLogicsUpdate(Request, $conditionId)`, `conditionLogicsDestroy($conditionId)`.
- Rule↔threshold mappings: `ruleThresholdMappingsIndex(Request)`, `ruleThresholdMappingsStore(Request)`, `ruleThresholdMappingsUpdate(Request, $mappingId)`, `ruleThresholdMappingsDestroy($mappingId)`.
- Glossary: `glossaryIndex(Request)` (search + type filter), `glossaryStore(Request)`, `glossaryUpdate(Request, $glossaryId)`, `glossaryDestroy($glossaryId)`.
- Thresholds: `thresholdsIndex(Request)` — domain-scoped for non-admins, filters status/type/search; `thresholdsStore(Request)` — full 24-field validation (`TH-\d+` PK, unique `threshold_key`); `thresholdsUpdate(Request, $thresholdId)` — domain-guarded; **on value change** bumps `version`, stamps `last_changed_by/at`, and writes a `ThresholdVersion` audit row in one transaction (`change_reason` is input-only, logged to versions); `thresholdsDestroy($thresholdId)` — transactionally deletes versions + mappings + row.
- Versions: `versionsIndex(Request)` (filter by threshold_id), `versionsStore(Request)`, `versionsUpdate(Request, $versionId)`, `versionsDestroy($versionId)` — raw CRUD on the audit table.
- `stats()` — row counts for all seven tabs (domain_access count = users count).
- Domains/admin: `domainsIndex(Request)` — distinct threshold domains; `domainsRename(Request)` — renames a domain across thresholds and user access; `domainAccessIndex(Request)`, `domainAccessMatrix(Request)` — user×domain matrix; `domainAccessReplace(Request, $userId)`, `domainAccessAdd(Request, $userId)`, `domainAccessRemove(Request, $userId, $domain)`.
- Import/export: `exportYaml()` — thresholds keyed by `threshold_key`; `exportCsv(Request)` — any tab as CSV; `bulkImport(Request, $tab)` — CSV bulk import with check/commit modes and upsert.

#### `app/Http/Controllers/Api/UserController.php` — FULL
Admin user management (3 endpoints; delete intentionally absent).
- `index()` — all users ordered by first/last name, mapped through the User accessors to `{id,name,email,role,domain,is_active,created_at}`.
- `store(Request $request)` — validates (unique `user.user_email`, role in admin/cashier/domain_owner), hashes password into `password_hash`, defaults role `cashier`, `is_active` true.
- `update(Request $request, $id)` — partial update; optional password re-hash; unique-email rule excludes own row.

#### `app/Http/Controllers/Api/FolderFileController.php` — FULL
Central File Library HTTP layer; thin wrappers around `FolderFileService` with a shared JSON error format. Route-model-binds `Folder` and `ManagedFile`.
- `__construct()` — resolves `FolderFileService` from the container.
- `jsonError(\Throwable $e, $action)` *(protected)* — logs `folder_file_manager_failed` and returns a 500 JSON envelope.
- `tree(Request)` — full folder tree.
- `downloadFolderZip(Request, Folder $folder)` — builds a temp zip via the service, streams as download, deletes after send; 404-maps "missing/Invalid" errors.
- `downloadFile(Request, ManagedFile $managed_file)` — streams the file with its display name.
- `showFolder(Request, Folder $folder)` — folder contents + breadcrumb.
- `storeFolder(Request)` — validates `name` (+ optional `parent_id` exists) then creates.
- `renameFolder(Request, Folder $folder)` — validates and renames (disk + DB + descendants).
- `destroyFolder(Request, Folder $folder)` — recursive delete.
- `uploadFile(Request, Folder $folder)` — validates one uploaded `file` and stores it.
- `reuploadFile(Request, ManagedFile $managed_file)` — replaces file content in place.
- `fileContent(Request, ManagedFile $managed_file)` — text preview (415 for non-text, 404 for missing).
- `renameFile(Request, ManagedFile)` / `moveFile(Request, ManagedFile)` / `destroyFile(Request, ManagedFile)` — rename on disk, move between folders (validates target `folder_id`), delete.

#### `app/Http/Controllers/Inventory/StockController.php` — one line (Shared-repo module — NOT BLOS scope)
Inventory stock sync: `WarehouseLocationWiseStockUpdate()` chunks `inv_products` (orders DB) and rewrites `location_wise_inv_stock` for UK/Germany/US; helper `GetInvStock($skuMapping = [])` computes stock with pack/combo/alternative-product logic.

#### `app/Http/Controllers/Ppc/TestingController.php` — one line (Shared-repo module — NOT BLOS scope)
WIP/testing harness for the PPC ETL: `testData()` (mounted at `GET /testData` in web.php) delegates to `saveAmazonPerformanceDataToPpcEtlPerformanceData()`, a batch upsert of Amazon ad performance into `ppc_etl_performance_data`; large commented-out prior version retained in-file.

### app/Http/Kernel + Middleware

#### `app/Http/Kernel.php` — FULL
HTTP kernel. Global stack: stock (TrustProxies, HandleCors, PreventRequestsDuringMaintenance, ValidatePostSize, TrimStrings, ConvertEmptyStringsToNull; TrustHosts commented out).
- `web` group: stock session/cookie stack incl. `VerifyCsrfToken`.
- `api` group: **custom** — `throttle:200,1` (200 req/min) + `SubstituteBindings`; Sanctum stateful middleware commented out.
- Route middleware aliases: stock set **plus custom** `admin` → `EnsureUserIsAdmin` and `domain_owner` → `EnsureDomainOwner`. (Note: `CheckAuthMiddleware` is applied by class name in routes, not via an alias; `WebSocketMiddleware` is not registered here.)

#### `app/Http/Middleware/CheckAuthMiddleware.php` — FULL — **custom, core of auth**
- `handle(Request $request, Closure $next)` — reads Bearer token; finds `User` where `token` matches AND `is_active`; `Auth::onceUsingId()` + sets the request user resolver; otherwise 401 JSON `{"error":"Invalid authentication"}`.

#### `app/Http/Middleware/EnsureUserIsAdmin.php` — FULL — custom
- `handle(Request, Closure $next)` — 403 JSON unless `$request->user()->role === 'admin'`. Registered as alias `admin`.

#### `app/Http/Middleware/EnsureDomainOwner.php` — FULL — custom
- `handle(Request, Closure $next)` — 403 JSON unless role === `'domain_owner'`. Registered as alias `domain_owner` (alias currently unused by any route in routes/*).

#### `app/Http/Middleware/WebSocketMiddleware.php` — FULL — custom (stub/debug)
- `handle(Request, Closure $next)` — passes only if `$request->some == 123`, else redirects `/`. Placeholder/debug code; not registered in the kernel.

#### `app/Http/Middleware/VerifyCsrfToken.php` — FULL
Stock base with custom `$except = ['packlist', 'zip']` (legacy shared-repo endpoints excluded from CSRF).

#### `app/Http/Middleware/Authenticate.php` — one line
*Boilerplate* — redirects non-JSON guests to the `login` route.

#### `app/Http/Middleware/EncryptCookies.php` — one line
*Boilerplate* — empty `$except`.

#### `app/Http/Middleware/PreventRequestsDuringMaintenance.php` — one line
*Boilerplate* — empty `$except`.

#### `app/Http/Middleware/RedirectIfAuthenticated.php` — one line
*Boilerplate* — redirects authenticated users to `RouteServiceProvider::HOME` (`/home`, a route that doesn't exist — harmless because guests use the SPA).

#### `app/Http/Middleware/TrimStrings.php` — one line
*Boilerplate* — excepts password fields.

#### `app/Http/Middleware/TrustHosts.php` — one line
*Boilerplate* — `hosts()` returns all subdomains of app URL; not enabled in kernel.

#### `app/Http/Middleware/TrustProxies.php` — one line
*Boilerplate* — stock forwarded-header config.

#### `app/Http/Middleware/ValidateSignature.php` — one line
*Boilerplate* — empty `$except`.

### app/Jobs

#### `app/Jobs/CreateBulkRuleRun.php` — FULL (Shared-repo module — NOT BLOS scope; **broken in this repo**)
Queued job (`ShouldQueue`, `ShouldBeUniqueUntilProcessing`) that applies order-processing rules in bulk: flags (e.g. "Lampshade"), packing-box sizes, and carrier services per order line, then broadcasts `OrderUpdateEvents`. **Imports many classes that do not exist in this repo** (`App\Models\Order`, `Flag`, `OrderFlag`, `Shipment`, `App\Http\Controllers\Apis\Orders\RuleController`, `App\Models\Hostinger\*` …) — it would fatal if dispatched; vestigial code from the shared/parent repo. Note: despite the name, this is order-fulfilment rules, NOT the BLOS rule builder.
- `__construct($orderIds)` — stores order ids. `handle()` — sleeps 150s then iterates orders applying flag/box/carrier rules via `RuleController` helpers.

#### `app/Jobs/CreateBulkShipments.php` — FULL (Shared-repo module — NOT BLOS scope)
Minimal queued job: `__construct($orderIds)`; `handle()` sleeps 20s then broadcasts a stub `OrderUpdateEvents` payload. Demo/placeholder.

### app/Models (root level) — FULL

> All six BLOS models live on the **default `mysql` connection** with hand-created tables (see `docs/sql/`), string business-code PKs (except auto-int `condition_id`/`version_id`), and `$timestamps = false`.

#### `app/Models/BusinessRule.php`
BLOS: a saved business rule. Table `business_rules`, PK `rule_id` (string, e.g. `BL-001`, non-incrementing), no timestamps.
- Fillable: `rule_id, rule_name, description, domain, status, owner, created_by, created_at`; casts `created_at` date.
- `conditionLogics()` — hasMany `ConditionLogic` on `rule_id`.
- `ruleThresholdMappings()` — hasMany `RuleThresholdMapping` on `rule_id`.

#### `app/Models/ConditionLogic.php`
BLOS: one per-stage condition row of a rule (stores both the coded string `condition_logic_by_ids`, e.g. `IF GL-001 < TH-001 AND …`, and the readable `condition_logic_rule`). Table `condition_logics`, PK `condition_id` (auto int), no timestamps.
- Fillable: `rule_id, condition_logic_by_ids, condition_logic_rule, decision_output, stage, stage_description, level, type, fulfillment, channel, account, site, status, owner, created_by, created_at`.
- `businessRule()` — belongsTo `BusinessRule` on `rule_id`.

#### `app/Models/Threshold.php`
BLOS: named limit/threshold referenced by rules (`TH-…` codes in condition strings). Table `thresholds`, PK `threshold_id` (string, e.g. `TH-001`, non-incrementing), no timestamps.
- Fillable (24 cols): `threshold_id, threshold_key, label, description, alternative_names, value, value_type, unit, type, fulfillment, channel, account, site, domain, owner, created_by, created_at, last_changed_by, last_changed_at, version, status, effective_from, approver, management_approval`.
- Casts: `value` → `CompactDecimal`; `created_at` date, `last_changed_at` datetime, `effective_from` date, `version` int.
- `versions()` — hasMany `ThresholdVersion` on `threshold_id`.
- `ruleThresholdMappings()` — hasMany `RuleThresholdMapping` on `threshold_id`.

#### `app/Models/ThresholdVersion.php`
BLOS: audit row per threshold value change (written automatically by `thresholdsUpdate`). Table `threshold_versions`, PK `version_id` (auto int), no timestamps.
- Fillable: `threshold_id, old_value, new_value, changed_by, approved_by, change_reason, timestamp, version_number`; casts old/new value → `CompactDecimal`, `timestamp` datetime.
- `threshold()` — belongsTo `Threshold` on `threshold_id`.

#### `app/Models/RuleThresholdMapping.php`
BLOS: junction rule↔threshold. Table `rule_threshold_mapping`, PK `mapping_id` (string, e.g. `MAP-001`, non-incrementing), no timestamps.
- Fillable: `mapping_id, rule_id, threshold_id, created_by, created_at`.
- `businessRule()` — belongsTo `BusinessRule`; `threshold()` — belongsTo `Threshold`.

#### `app/Models/Glossary.php`
BLOS: metric/term dictionary (`GL-…` codes used as clause left-operands). Table `glossary`, PK `glossary_id` (string, e.g. `GL-001`), no timestamps.
- Fillable: `glossary_id, term, type, definition, alternative_names`. No relationships.

#### `app/Models/User.php`
Authenticatable user mapping the **legacy `user` table** (PK column literally named `user`) via accessors — the only place legacy column names are translated.
- Fillable (virtual names): `name, email, password_hash, role, is_active, token, domain`; hidden `user_password`, `token`.
- `getAuthIdentifierName()` — returns `'user'`. `getAuthPassword()` — reads `user_password`.
- `getIdAttribute()` — int of `user` column. `getNameAttribute()` / `setNameAttribute($value)` — composes `user_firstname + user_lastname` (writes firstname only).
- `getEmailAttribute()` / `setEmailAttribute($value)` — maps `user_email`.
- `getPasswordHashAttribute()` / `setPasswordHashAttribute($value)` — maps `user_password`.
- `getRoleAttribute()` / `setRoleAttribute($value)` — maps `config_role`, normalized lowercase, default `cashier`.
- `getIsActiveAttribute()` / `setIsActiveAttribute($value)` — maps `user_status` ('active'/'1'/'yes'/'true'/'enabled' → true; writes 'active'/'inactive').
- `setTokenAttribute($value)` — truncates token to **32 chars**.
- `booted()` *(protected static)* — on create defaults `user_accounts = 'list'`.
- `sales()` — hasMany `Sale` (`user_id` → `user`). `userDomainAccess()` — hasMany `UserDomainAccess` using the schema-detected FK column.

#### `app/Models/UserDomainAccess.php`
BLOS multi-domain access grant. Table `user_domain_access`; fillable `user, user_id, domain`.
- `userFkColumn()` *(static)* — schema-sniffs whether the FK column is `user` or `user_id` (cached).
- `assignedUserId()` — int user id via the detected column.

#### `app/Models/Folder.php`
File Library folder (hierarchical, slug + materialized `path`). Table `folders` (migrated); fillable `name, slug, path, parent_id`.
- `parent()` — belongsTo self. `children()` — hasMany self ordered by name. `allChildren()` — recursive eager tree (children + files). `files()` — hasMany `ManagedFile` ordered by name.

#### `app/Models/ManagedFile.php`
File Library file metadata. **Table `files`** (migrated); fillable `folder_id, name, filename, file_path, mime_type, extension, size`.
- `folder()` — belongsTo `Folder`.

#### `app/Models/Product.php` — (POS/catalog; Shared-repo scope)
Default-connection catalog product; fillable `category_id, name, sku, description, price, cost_price, unit, is_active`; appends `image_path`.
- `category()` belongsTo; `inventory()` hasOne `Inventory`; `saleItems()` hasMany; `images()` morphMany `Image` via `entity_type/entity_id`; `getImagePathAttribute()` — first loaded image of type slug `product_main`.

#### `app/Models/Category.php` — (POS/catalog; Shared-repo scope)
Product category; fillable `name, slug, description, is_active`; appends `image_path`.
- `products()` hasMany; `images()` morphMany; `getImagePathAttribute()` — first `category_main` image.

#### `app/Models/Image.php` — (POS/catalog; Shared-repo scope)
Polymorphic image row; fillable `image_type_id, path, entity_type, entity_id, name, title, alt, sort_order`.
- `imageType()` belongsTo; `scopeOfType($query, $slug)` — filter by type slug; `imageable()` morphTo; `getUrlAttribute()` — `/storage/`-prefixed URL.

#### `app/Models/ImageType.php` — (POS/catalog; Shared-repo scope)
Image type lookup (`name, slug`). `images()` — hasMany `Image`.

#### `app/Models/Inventory.php` — (POS/catalog; Shared-repo scope)
Simple stock row, table `inventory` (`product_id, quantity, low_stock_threshold`; only `updated_at` timestamp). `product()` — belongsTo `Product`.

#### `app/Models/Sale.php` — (POS; Shared-repo scope)
Sale header; fillable `user_id, invoice_number, total_amount, discount, paid_amount, payment_method, status`.
- `user()` — belongsTo `User` (`user_id` → `user`); `saleItems()` — hasMany.

#### `app/Models/SaleItem.php` — (POS; Shared-repo scope)
Sale line (`sale_id, product_id, quantity, unit_price, subtotal`; no timestamps). `sale()` belongsTo; `product()` belongsTo.

### app/Models — Shared-repo modules — NOT BLOS scope (one line each)

#### `app/Models/auth/`
- `app/Models/auth/User.php` — legacy duplicate Authenticatable on the same `user` table (raw column fillables `user_firstname…`, `getAuthIdentifierName()`, `getAuthPassword()`); superseded by root `App\Models\User` — avoid.

#### `app/Models/CentralizedEtlData/Ppc/Amazon/` (connection `ppc`)
- `AmazonCampaigns.php` — table `campaigns`; Amazon PPC campaign dimensions.
- `AmazonAdGroups.php` — table `ad_groups`; Amazon ad-group dimensions.
- `AmazonAds.php` — table `ads`; Amazon ad rows.
- `AmazonPerformanceData.php` — table `performance_data`; daily Amazon ad performance metrics.
- `AmazonProducts.php` — table `products`; Amazon listing/ASIN rows.
- `AmazonSellerStores.php` — table `seller_stores`; Amazon seller account registry.
- `AmazonStoreMarketPlacesDev.php` — table `store_market_places_dev`; store↔marketplace mapping (dev).

#### `app/Models/CentralizedEtlData/Ppc/Common/`
- `MarketPlaces.php` — table `market_places` (conn `ppc`); marketplace lookup.
- `Region.php` — table `tbl_region` (conn `ppc`); region lookup.
- `States.php` — table `states` (conn `ppc`); state lookup.
- `PpcEtl.php` — table `ppc_etl` (**default connection** — no `$connection` set); unified cross-platform dimension target of the ETL.
- `PpcEtlPerformanceData.php` — table `ppc_etl_performance_data` (**default connection**); unified daily performance target of the ETL.

#### `app/Models/CentralizedEtlData/Ppc/Ebay/` (connection `ppc`)
- `EbayCampaigns.php` — table `ebay_campaigns`; eBay campaign dimensions.
- `EbayAdGroups.php` — table `ebay_ad_groups`; eBay ad-group dimensions.
- `EbayAds.php` — table `ebay_ads`; eBay promoted-listing ads.
- `EbayPerformanceData.php` — table `ebay_performance_data`; daily eBay ad performance.
- `EbayCampaignReportData.php` — table `ebay_campaign_report_data`; campaign report metrics.
- `EbaySellerStores.php` — table `ebay_seller_stores_dev`; eBay seller accounts.

#### `app/Models/CentralizedEtlData/Ppc/GoogleAds/` (connection `ppc`)
- `GoogleAccounts.php` — table `google_accounts`; Google Ads accounts.
- `GoogleCampaigns.php` — table `google_campaigns`; campaign dimensions.
- `GoogleAdGroups.php` — table `google_ad_groups`; ad-group dimensions.
- `GoogleAssetGroups.php` — table `google_asset_groups`; PMax asset groups.
- `GoogleAssetGroupsAssets.php` — table `google_ad_asset_group_assets`; asset-group↔asset links.
- `GoogleAssetsPerformance.php` — table `google_ad_asset_group_performance`; asset performance.
- `GoogleCampaignPerformance.php` — table `google_campaign_performance`; daily campaign metrics.
- `GoogleProductPerformance.php` — table `google_product_performance`; shopping product metrics.

#### `app/Models/Inventory/` (connection `orders`, except noted)
- `InvProducts.php` — table `inv_products`; inventory product master (`getInvStocks()`, `getStocks()`, `getCombos()`).
- `InvStock.php` — table `inv_stock`; stock rows (`getAlternativeStock()`, `getCombos()`, `warehouses()`).
- `InvProductCombo.php` — table `inv_product_combo`; bundle composition (`getComboProductInfo()`, `getPackInfo()`).
- `InvProductMapping.php` — table `inv_product_mapping`; alternative-product mapping (`getAlternativeProduct()`, `getAlternativeProductStock()`, `Products()`, `Warehouses()`).
- `ProductPK.php` — table `product_pk`; product pack-key lookup.
- `Warehouse.php` — table `warehouse`; warehouse registry.
- `LocationWiseStock.php` — table `location_wise_inv_stock` on **`mysql` connection**; denormalized per-location stock written by `StockController`.

### app/Providers

- `app/Providers/AppServiceProvider.php` — near-boilerplate **with one custom behavior**: `boot()` calls `JsonResource::withoutWrapping()` (API resources return unwrapped JSON).
- `app/Providers/AuthServiceProvider.php` — *boilerplate*; empty policies, no gates.
- `app/Providers/BroadcastServiceProvider.php` — **custom**: `Broadcast::routes(['middleware' => [CheckAuthMiddleware::class]])` — websocket channel auth uses the token middleware; loads `routes/channels.php`.
- `app/Providers/EventServiceProvider.php` — *boilerplate*; only Registered→SendEmailVerificationNotification; `shouldDiscoverEvents()` false.
- `app/Providers/RouteServiceProvider.php` — *boilerplate*: HOME `/home`; maps `routes/api.php` under `/api` with `api` group and `routes/web.php` with `web`; `api` rate limiter 60/min (note the kernel's `throttle:200,1` on the api group is what actually applies to API routes).

### app/Services

#### `app/Services/FolderFileService.php` — FULL
All File Library business logic: disk layout mirrors the folder tree under the `local` disk (`storage/app`), slug-based folder paths, self-healing `file_path` resolution, zip export.
- Protected helpers: `disk()` — Storage `local`; `normalizeStorageKey($path)`; `replacePathPrefix($fullPath, $oldPrefix, $newPrefix)`; `resolvedStorageRelativePath(ManagedFile)` — finds the real disk key and repairs the DB if moved; `uniqueSlugForParent($name, $parentId, $exceptFolderId=null)` + `slugTaken(...)` — sibling-unique slugs; `updateDescendantPaths(...)`; `folderAndDescendantIds(Folder)`; `safeZipPathLabel(...)`; `folderChainFromArchiveRoot(...)`; `reserveUniqueZipEntry(...)`.
- `createFolder($name, $parentId = null)` — creates disk directory + `folders` row.
- `renameFolder(Folder $folder, $newName)` — re-slugs, moves the directory, rewrites descendant folder/file paths.
- `deleteFolder(Folder $folder)` — recursive disk + DB delete.
- `uploadFile(Folder $folder, UploadedFile $uploadedFile)` — stores the upload (reuses row when display name collides).
- `reuploadManagedFile(ManagedFile $file, UploadedFile $uploadedFile)` — replaces content in place.
- `renameFile(ManagedFile $file, $newName)` — renames on disk preserving extension.
- `moveFile(ManagedFile $file, Folder $targetFolder)` — moves disk object + updates row.
- `deleteFile(ManagedFile $file)` — disk + DB delete.
- `getTree()` — root folders with recursive children + files.
- `getFolderContents(Folder $folder)` — folder, children, files, breadcrumb.
- `createFolderZipArchive(Folder $folder)` — builds a temp `.zip` of the whole subtree with sanitized, deduplicated entry names.
- `absolutePathForManagedFile(ManagedFile $file)` — absolute filesystem path (throws on missing).
- `readTextPreview(ManagedFile $file)` — file contents for text-like MIME types only.

---

## bootstrap/

- `bootstrap/app.php` — *boilerplate*: creates the Application container and binds Http/Console kernels + exception handler singletons.
- `bootstrap/cache/.gitignore` — *boilerplate* cache ignore.
- `bootstrap/cache/packages.php`, `bootstrap/cache/services.php` — framework-generated package/service manifests (do not edit).
- `bootstrap/cache/serDDD.tmp`, `bootstrap/cache/serDEC.tmp` — stray generated temp files (safe to ignore).

---

## config/

- `config/app.php` — app name default **"Ledsone centralizer"**, timezone UTC, locale en; otherwise stock provider/alias lists.
- `config/auth.php` — **FULL**: default guard `web` (session) with provider `users` = eloquent `App\Models\User`; passwords broker `users` (expire 60, throttle 60); `password_timeout` 10800. Note: the API does not use these guards — `CheckAuthMiddleware` authenticates directly; this config matters mainly for `Auth::onceUsingId` and the provider model binding.
- `config/broadcasting.php` — default `BROADCAST_DRIVER` (env, default null; .env.example sets `pusher`); `pusher` connection reads `PUSHER_*` env and targets the **self-hosted** laravel-websockets server; ably/redis/log/null stock.
- `config/cache.php` — stock; default `CACHE_DRIVER` (file).
- `config/cors.php` — **FULL**: paths `['api/*', 'sanctum/csrf-cookie']`; allowed methods/origins/headers all `*`; `supports_credentials: true`; max_age 0. Fully permissive CORS on the API.
- `config/database.php` — **FULL**: default `DB_CONNECTION` (mysql). Connections: `sqlite` (stock); `mysql` — main app DB, utf8mb4, strict **with custom relaxed modes** (ONLY_FULL_GROUP_BY, STRICT_TRANS_TABLES, NO_ENGINE_SUBSTITUTION — zero-date/division modes removed); `orders` — order-management DB via `DB_*_ORDER_MANAGEMENT` env; `ppc` — advertising ETL DB via `DB_*_PPC`; `accounts_management` — via `DB_*_ACCOUNTS_MANAGEMENT` (configured, no model uses it); `order_management` — exact duplicate of `orders` (legacy alias); `pgsql`/`sqlsrv` stock fallbacks. Redis stock (phpredis, default + cache DBs).
- `config/filesystems.php` — **FULL**: default `FILESYSTEM_DISK` (local). Disks: `local` → `storage/app` (used by FolderFileService); `public` → `storage/app/public` with `/storage` URL; `s3` → AWS env vars; **custom `contabo`** → S3-compatible disk via `CONTABO_*` env vars. Symlink `public/storage` → `storage/app/public`.
- `config/hashing.php` — stock bcrypt (10 rounds).
- `config/logging.php` — stock stack/single channels.
- `config/mail.php` — stock; default `MAIL_MAILER` (smtp).
- `config/queue.php` — stock; default `QUEUE_CONNECTION` (sync — jobs run inline unless env changes it).
- `config/sanctum.php` — stock stateful-domain config; Sanctum installed but not used for API auth.
- `config/services.php` — stock third-party stubs (mailgun/postmark/ses).
- `config/session.php` — stock; `SESSION_DRIVER` default file, lifetime 120.
- `config/view.php` — stock view paths/compiled.
- `config/websockets.php` — laravel-websockets server: port 6001; single app from `PUSHER_APP_*` env; statistics enabled (60s interval, 60-day retention); **custom SSL defaults** pointing at Let's Encrypt certs for `message.vintageinterior.co.uk`; `verify_peer` false; dashboard behind `web` + package Authorize middleware.

---

## database/

### database/migrations — FULL (one entry each)

- `0000_00_00_000000_create_websockets_statistics_entries_table.php` — creates `websockets_statistics_entries` (`id`, `app_id`, `peak_connection_count`, `websocket_message_count`, `api_message_count`, nullable timestamps) for the websockets dashboard.
- `2023_01_17_081228_create_product_table.php` — creates a bare `product` table (`id`, timestamps only) — legacy stub, unrelated to the `Product` model's `products` table.
- `2025_03_15_000001_add_token_to_users_table.php` — adds `token` VARCHAR(60) nullable to the legacy `user` table (the auth token column; model truncates to 32 chars).
- `2026_04_28_000001_create_threshold_change_requests_table.php` — creates `threshold_change_requests` (`threshold_id` unsignedBigInteger, old/new value DECIMAL(18,6), effective_from, requested/approved by+at, status default 'pending', change_reason, high/medium/low_count, `impact_snapshot` JSON, timestamps; index (threshold_id, status)). **No model/controller currently uses it** — built for a planned approval workflow; note its integer `threshold_id` predates the string `TH-…` PK (see `docs/sql/align_threshold_fk_columns.sql`).
- `2026_04_28_000002_add_domain_to_user_table.php` — adds `domain` VARCHAR(100) to `user` AND `proposed_value` DECIMAL(10,4) to `thresholds` (the latter column belongs to the old thresholds schema; superseded by docs/sql rebuild).
- `2026_04_28_000002_create_user_domain_access_table.php` — creates `user_domain_access` (`id`, `user` unsignedInteger, `domain` VARCHAR(100), timestamps; unique (user, domain)).
- `2026_05_01_000001_create_folders_and_managed_files_tables.php` — creates `folders` (`name`, `slug`, `path`, self-FK `parent_id` cascade) and `files` (FK `folder_id` cascade, `name`, `filename`, `file_path`, `mime_type`, `extension`, `size`) for the File Library.

### database/seeders + factories — FULL

- `database/seeders/DatabaseSeeder.php` — **empty on purpose**; comment states OilThresholdsSeeder was removed because real threshold data lives in the DB with production key names.
- `database/factories/UserFactory.php` — *boilerplate* stock user factory (`name/email/email_verified_at/password/remember_token`, `unverified()` state); note it targets stock column names, not the legacy `user` table mapping, so it is effectively unusable as-is.

---

## docs/ — FULL

- `docs/BLOS-Rule-Builder-Summary.md` — plain-language BLOS plan (2026-06-16 draft): problem = hand-typed rule sentences; solution = drag-and-drop builder from Metric/Operator/Threshold blocks joined by AND/OR; outlines the proposed OPERATORS + CONDITION_CLAUSE tables and 8 implementation steps.
- `docs/blos-rule-builder-model.md` — technical data-model spec (draft): decision "Way 2" = store both the readable sentence AND structured clause rows; documents real inconsistencies found in the Excel source (mixed `≥`/`>=`, typo `=<`); proposes `OPERATORS` lookup + `CONDITION_CLAUSE` table; leaves nesting (`group_no`) and per-category thresholds as open team questions. *(Note: the shipped implementation instead stores the coded string in `condition_logics.condition_logic_by_ids` parsed by `ruleLogic.js` — CONDITION_CLAUSE was not built.)*
- `docs/blos-rule-builder-ui.md` — UI plan (draft): compares free-form canvas vs guided clause rows vs hybrid; recommends Hybrid (C); maps to `Pages/RuleBuilder.vue` + child components + `vuedraggable@2`; proposes phased rollout (flat rows → drag → nesting).
- `docs/blos-rule-builder-mockup.html` — 262-line standalone interactive HTML/CSS mockup of the rule-builder screen (no build deps; open in a browser).
- `docs/skill.md` — "ledsone-engineering-log" agent skill: living engineering activity log with maintenance protocol (read at session start, append activity entries after changes); includes conventions and chronological change record (last updated 2026-05-20).

### docs/sql/ — FULL (one line each; hand-run DDL/DML for BLOS tables — the real "migrations")

- `docs/sql/business_rules.sql` — CREATE TABLE `business_rules` (VARCHAR(20) PK `rule_id`) + seed row `BL-001` "CTR Collapse"; notes live-server rename history.
- `docs/sql/condition_logics.sql` — CREATE TABLE `condition_logics` (17 cols, auto-int PK) + 3 seed rows (BL-001 stages initial/restore/kill), sourced from CONDITION_LOGICS.xlsx.
- `docs/sql/glossary.sql` — CREATE TABLE `glossary` (VARCHAR(20) PK `GL-…`) + 3 seed rows (organic_ctr, organic_impressions, organic_ctr_days).
- `docs/sql/rule_threshold_mapping.sql` — CREATE TABLE `rule_threshold_mapping` (VARCHAR(20) PK `MAP-…`, unique (rule_id, threshold_id)) + 5 seed links BL-001↔TH-001..TH-005.
- `docs/sql/thresholds.sql` — DROP+CREATE the new 26-column `thresholds` table (string PK `TH-…`, unique `threshold_key`) + 7 seed rows; notes that `previous_value`/`change_reason` were later dropped.
- `docs/sql/threshold_versions.sql` — CREATE TABLE IF NOT EXISTS `threshold_versions` schema spec (already live and written by the app).
- `docs/sql/align_threshold_fk_columns.sql` — ALTERs widening `threshold_id` from INT to VARCHAR(20) in `threshold_versions`, `threshold_dependencies`, `threshold_change_requests` to match the new string PK.
- `docs/sql/drop_threshold_snapshot_columns.sql` — ALTER dropping redundant `previous_value` + `change_reason` from `thresholds` (history lives in `threshold_versions`).
- `docs/sql/rename_business_rule_table.sql` — RENAME `business_rule_table` → `business_rules` on the live server.
- `docs/sql/thresholds_data_load.sql` — DELETE + INSERT full 35-row threshold data load from the latest Excel (warns it wipes UI edits/version bumps; no FK enforcement on old links).

---

## lang/

- `lang/en/auth.php`, `lang/en/pagination.php`, `lang/en/passwords.php`, `lang/en/validation.php` — *boilerplate* stock Laravel English strings (verified unmodified in intent; validation.php is the stock rule-message catalogue).

---

## public/ (excluding built js/css — see Coverage)

- `public/index.php` — *boilerplate* Laravel front controller.
- `public/.htaccess` — *boilerplate* Laravel rewrite rules.
- `public/mix-manifest.json` — generated Mix asset manifest (`/js/Account.js`, `/css/app.css`).
- `public/robots.txt` — *boilerplate* allow-all.
- `public/favicon.ico` — site icon binary.
- `public/hello_world.pdf` — stray test PDF (likely from the TCPDF dependency trial).
- `public/fonts/glyphicons-halflings-regular.woff2` — legacy Bootstrap glyphicon font.
- `public/Img/` (5 binaries) — `chat.png`, `ebay.png`, `ebay_PNG20.png`, `user.png`, `Logo/Company_logo/com.jpg` — static UI/logo images.

---

## resources/

### resources/js (shared plumbing) — FULL

#### `resources/js/app.js`
Global Vue 2 bootstrap imported by the SPA entry: registers BootstrapVue plugins (Modal, Spinner, Tooltip, Toast, Dropdown) and components (`b-button`, `b-pagination`, `b-tabs`, `b-tab`, `b-spinner`, `b-skeleton`, `b-tooltip`, `b-dropdown`, `b-dropdown-item-button`, `b-collapse`, `v-b-toggle` directive); applies `Mixins` globally and the `Directive` plugin; wires `window.Pusher` and `Vue.prototype.Echo` (laravel-echo). Exports the configured `Vue`.

#### `resources/js/Api.js`
Axios wrapper (default export `ajax(d)`).
- Response interceptor — on 401/403/419 clears all auth (via `clearAllAuth`) and hard-redirects to `/login` (once).
- `uploadFile(data)` — multipart POST with `FormData` (extracts `data.data.file`, appends other fields, progress callback).
- `apiRequests(data)` — generic JSON request (method/url/headers/body merge).
- `ajax(d)` — injects `Authorization: Bearer` from localStorage/sessionStorage `auth` and routes to upload vs plain request.

#### `resources/js/Directive.js`
Vue plugin exporting `install(app, options)` — registers global `v-focus` directive (focus element on insert).

#### `resources/js/Mixins.js`
Global mixin: data `Errors`, `Domain` (hostname), `mailRegex`; computed `Store` (mapState).
- `filterData(data, string)` — dead placeholder.
- `api(data)` — dispatches the Vuex `Store/requests` action (main legacy API path).
- `apiKey()` — token from local/session storage.
- `getCsrf()` — reads `#csrf` meta.
- `echo(data)` — constructs a laravel-echo Pusher client against `wsHost:6001` with CSRF + Bearer auth headers (hardcoded key `3141…`).
- `getObj(data)` — Proxy pass-through helper.

#### `resources/js/Store.js`
Namespaced Vuex module used as module `Store` in the SPA store.
- state: `errors`.
- mutation `error(state, e)` — 401/419/403 → clear auth + redirect `/login`; else invokes optional `e.error` callback.
- mutation `ajax(state, i)` — `Vue.set(state, i.state, i.data)` + optional `i.success` callback (references an undefined global `Stores.callback` — latent bug if reached).
- action `requests(commit, data)` — maps shorthand actions (get/create/update/delete → verbs), prefixes `'/api' + url`, calls `Api()` and commits `ajax`/`error`.

#### `resources/js/StoreLimits.js`
Variant of Store.js with lazy-load semantics: `requests` only hits the API when `state[data.state]` is undefined and no `force` flag; errors 403 → redirect `/signin`. **Not registered** in the Account store (unused in this SPA).

### resources/js/Account (the SPA) — FULL

#### `resources/js/Account/Account.js`
Webpack entry: imports the configured Vue from `../app`, mounts `App.vue` with `router` + `store` at `#app`.

#### `resources/js/Account/App.vue`
Root layout: shows `Loading` overlay until `loaded`, conditional `Header`, transition-wrapped `<router-view>`; defines the app-wide CSS design tokens.
- data: `isLoading`.
- computed: `showLayout()` — hide chrome on Login; `isFullBleedMain()` — full-bleed for Dashboard/ThresholdConfigurator/FileManager/OilConfigurator; `routeViewKey()`.
- methods: `handleLoaded()` — clears the boot loader.

#### `resources/js/Account/Components.js`
Stub Vue plugin — `install(app, options)` with everything commented out (*dead boilerplate*).

#### `resources/js/Account/Pages.vue`
Two-line passthrough component rendering `<router-view/>` (unused legacy).

#### `resources/js/Account/Router.js`
Vue Router (history mode). Routes (verified):
- `/` → `Dashboard` (requiresAuth)
- `/threshold-configurator` → `ThresholdConfigurator` (requiresAuth)
- `/oil-configurator` → `OilConfigurator` (requiresAuth)
- `/rule-builder` → `RuleBuilder` (requiresAuth + **requiresAdmin**)
- `/file-manager` → `FileManager` (requiresAuth); `/markdown-manager` → redirect `/file-manager`
- `/login` → `Login` (requiresGuest); `/register` → redirect `/login`; `*` → redirect `/`.
- `beforeEach` — token presence check; awaits `refreshSessionUser()` (`'expired'` → back to login); `requiresAdmin` gate parses the stored user's role.
- `afterEach` — smooth scroll-to-top (reduced-motion aware); `onError` — console logging.

#### `resources/js/Account/Store.js`
Builds the Vuex store: registers `Components` plugin and single module `Store` (from `../Store`).

#### `resources/js/Account/userSession.js`
Session/token bookkeeping shared by router, pages, and Api.js. Exports:
- `sessionProfileTick` — `Vue.observable({n})` bumped after profile refresh so computeds re-run.
- `setAuthBucket(which)` / `clearAuthBucket()` — records whether auth lives in localStorage ("remember me") or sessionStorage.
- `userAuthStorage()` — resolves which Storage currently holds the token (with stale-bucket cleanup and completeness heuristics).
- `getStoredUserJson()` — user JSON from the active storage only (avoids mixing users).
- `authHeaders()` — `{Accept, Authorization: Bearer …}`.
- `clearAllAuth()` — wipes auth + user from both storages.
- `refreshSessionUser()` *(async)* — GET `/api/me`; rewrites stored user, bumps the tick; returns `true` / `false` / `'expired'` (401/403/419 → clears auth).

#### `resources/js/Account/Pages/Dashboard.vue`
Static welcome dashboard (no API calls): hero, metric cards, tool cards linking to the other pages; heavy scoped CSS with animated background.
- computed: `userName`, `isAdmin`, `roleLabel`, `todayIso`, `todayShort`, `metrics` (4 informational cards).

#### `resources/js/Account/Pages/Loading.vue`
Boot splash. props: `duration` (default ~1200ms). data: `particleStyles`.
- `created()` — builds particle animations and calls `loadConfigurations()`.
- `loadConfigurations()` — GET `/configurations` via the Vuex `api` mixin (→ `/api/configurations`), refreshing the echoed token.
- `mounted()` — emits **`loaded`** after `duration`.

#### `resources/js/Account/Pages/auth/Login.vue`
Login screen (1,141 lines, mostly scoped CSS). data: `form {email, password, rememberMe}`, `loading`, `passwordVisible`.
- `handleLogin()` — posts `url:'/login'` through the Vuex `requests` action (→ POST `/api/login`); on success stores `auth` token + `user` JSON in localStorage (remember me) or sessionStorage, calls `setAuthBucket`, redirects to `/` (or `?redirect`).

#### `resources/js/Account/Pages/ThresholdConfigurator.vue`
The BLOS **data-administration UI** (4,099 lines): seven tabs mirroring the BLOS tables — `business_rules`, `condition_logics`, `glossary`, `rule_threshold_mapping`, `thresholds` (default), `user_domain_access`, `threshold_versions` — with search/filters, add/edit modals, delete confirm, CSV bulk import, CSV/YAML export, domain-access admin, and deep-links into the Rule Builder.
- data highlights: `tabs[7]`, `activeTab`, `rows`, `filters {domain,status,type,stage,role,noDomains}`, `counts`, `refRules`/`refThresholds` (reference lists), `bulk`, `modal`/`form`/`editPk`, `admin {users, domains, …}`, `domainAccessModal`, `picker`, `toast`, `confirm`.
- computed (verified): `isAdmin`, `visibleTabs`, `currentTab`, `filtered`, `tabFilterActive`, `domainOptions`, `typeSuggestions`, `comboOptions`, `adminDomainsFiltered`, `domainAccessDomainsFiltered`, `domainAccessRoles`, `pickerFiltered`, `nextCodeForActiveTab`, `canSave`, `pkIsDuplicate`, `pkHint`, `deleteIdForRow`, `colspan`, …
- methods (verified; selection): `apiGet`/`apiSend` — axios with `authHeaders()`; `loadTab`/`loadStats`/`loadRefLists` — per-tab data; `switchTab(key)`; `openAdd`/`openEdit`/`saveForm`/`cleanPayload`/`normalizeFormDates`/`stripPrimaryKeysOnCreate` — modal CRUD; `askDelete`/`doDelete`; `openBulk`/`onBulkFile`/`bulkCheck`/`bulkCommit`/`bulkSend`/`closeBulk` — CSV import (`POST /api/threshold-config/bulk-import/{tab}`); `exportCsv`/`exportYaml`/`verifyExportBlob`/`triggerBlobDownload`; `loadAdminUsers`/`loadAdminDomains`/`loadAdminAccess`/`saveAdminAccess`/`renameDomain`/`addCustomDomain`/`toggleAdminDomain`/`removeAdminDomain` — domain admin; `loadDomainAccessTab`/`openDomainAccessEdit`/`saveDomainAccessEdit`/`toggleDomainAccessDomain`/`addDomainAccessCustomDomain` — per-user domain matrix editing; `goToRuleBuilder` — deep-link `/rule-builder?rule=…&stage=…`; `openPicker`/`choosePicker`/`closePicker` + mobile menu helpers; `ruleNameFor`, `comboDisplay`, `rowKey`, `getByPath`/`setByPath`, `formatNavLabel`, `toastMsg`.
- Endpoints: everything under `/api/threshold-config/*` (all routes listed in routes/api.php below).

#### `resources/js/Account/Pages/RuleBuilder.vue`
The BLOS **Rule Builder** (837 lines; admin-only route). Sidebar of business rules; per-rule stage tabs (one `condition_logics` row per stage); visual clause/group editor (via recursive `RuleNode`) with live coded + readable previews; raw-text fallback when a stored string cannot be parsed; unsaved-changes guard; context metadata panel.
- data: `rules`, `glossary`, `thresholds`, `activeRuleId`, `conditions`, `activeConditionId` (null = new), `form` (condition fields), `tree` (ruleLogic tree), `rawMode`/`rawText`, `previewCoded`/`previewReadable`, `dirty`, `showNewRule`/`newRule`, `discard`, `toast`.
- computed: `glossaryMap` (GL→term), `thresholdMap` (TH→label), `stageSuggestions` (initial/restore/kill + existing), `canSave`, `saveBlockReason`.
- methods: `apiGet(path, params)` / `apiSend(method, path, body)` — axios + `authHeaders()`; `loadAll()` — parallel GET business-rules/glossary/thresholds + deep-link handling (`?rule=&stage=`); `selectRule(ruleId)` / `applyRule(ruleId)`; `loadConditions(ruleId)` — GET condition-logics?rule_id=; `selectCondition(row)` / `applyCondition(row)` — parses `condition_logic_by_ids` via `parseSafe` (falls to raw mode on failure); `selectStageByName(stage)`; `newCondition()` / `applyNewCondition()` — blank form with sibling defaults; `onTreeChange()` / `regenerate()` — recompute previews via `serializePreview` + `toReadable`; `tryParseRaw()`; `buildPayload()` — serializes tree → `condition_logic_by_ids` + readable → `condition_logic_rule`; `saveCondition()` — POST/PUT condition-logics; `removeCondition()` — DELETE; `openNewRule()` / `nextRuleId()` (next `BL-nnn`) / `createRule()` — POST business-rules; `currentUserName()`; discard-guard suite `guard/askDiscard/discardConfirm/discardCancel/discardEdits/revertEdits/onKeydown`; `goBack()`; `beforeRouteLeave` hook routes exits through the discard modal.

#### `resources/js/Account/Pages/OilConfigurator.vue`
"Business OS (OIL)" threshold editor (2,041 lines): domain-grouped read/edit of ALL thresholds with per-key change tracking, YAML preview/copy/download, and bulk save.
- data: `allRows`, `localValues` (threshold_key → edited value), `activeDomain`, `search`, `loading`/`saving`, `toast`; `DOMAIN_ICONS` emoji map.
- computed/methods (verified): `domains`, `rowsByDomain`, `changedKeys`, `activeChannelSections`, `channelSectionsForDomain`, `buildTypeSections`, `rowChannel`, `isRowChanged`, `matchesSearch`, `searchMatchCount`, `yamlString`, `domainAccent`/`domainIcon`; `loadThresholds()` — GET `/api/threshold-config/thresholds`; `saveAll()` — PUT per changed threshold; `discardChanges()`, `onInput()`, `copyYaml()`, `downloadYaml()`, `showToast()`.

#### `resources/js/Account/Pages/FileManager.vue`
Central File Library UI (4,749 lines — the largest file): folder tree sidebar + table main pane; admin CRUD (create/rename/delete folders, upload/reupload/rename/move/delete files); zip download; rich in-browser viewer (markdown via `marked`+`highlight.js`, CSV/JSON/XML rendering); "what changed" highlighting via localStorage snapshots and re-upload diff (side-by-side line diff).
- ~120 methods verified by extraction; key ones: `loadTree()`, `openFolder(id)`, `refreshMain()`, `goRoot()`, `toggleTreeFolder`, `onTreeRowClick`, `openCreateFolder`/`submitCreateFolder`, `startRenameFolder`/`submitRenameFolder`, `openDeleteFolderModal`/`submitDeleteFolderConfirmed`, `onPickUpload` (multi-upload), `pickReupload`/`onReuploadPicked`/`executeManagedFileReupload`, `startRenameFile`/`submitRenameFile`, `startMoveFile`/`submitMoveFile`, `deleteFileById`/`submitDeleteFileConfirmed`, `downloadManagedFile`, `downloadFolderZipById`/`downloadCurrentFolderZip`, `openFullViewer`/`closeFullViewer`/`setViewerMode`, `fmFetchManagedTextContent`, `mdToHtml`/`renderCsvHtml`/`renderJsonHtml`/`prettyXml`, snapshot/diff suite (`fmCollectSnapshotFromTree`, `fmComputeSnapshotDiff`, `fmApplyHighlightMaps`, `fmOpenReplaceDiffModal`, `fmBuildSideBySideDiffHtml`, `fmLineDiffOps`, …), `fmtBytes`, `logAxiosError`.
- Endpoints: `/api/folders/tree`, `/api/folders`, `/api/folders/{id}…`, `/api/files/{id}…`.

#### `resources/js/Account/Pages/includes/Header.vue`
Fixed top nav: logo, links (Dashboard, Threshold config, Business OS, Rule Builder [admin-only], Files), mobile hamburger, user dropdown.
- data: `mobileNavOpen`, `userOpen`; computed: `isAdmin`, `userName`, `userInitial`, `roleLabel`, `pageTitle`.
- methods: `toggleMobileNav()`, `closeMobileNav()`, `toggleUserMenu()` (outside-click aware), `handleLogout()` — clears auth and routes to `/login`.

#### `resources/js/Account/Pages/includes/Sidebar.vue`
Legacy sidebar (not mounted in current layout): computed `userName`; method `handleLogout()`.

#### `resources/js/Account/Pages/includes/TopBar.vue`
Legacy page-title bar (not mounted): computed `pageTitle` from route name.

#### `resources/js/Account/components/AccountRouteLoader.vue`
Reusable loading skeleton, props `variant` ('shell'|'card'), `title`, `subtitle`; pure presentation (no methods).

#### `resources/js/Account/components/RuleNode.vue`
Recursive BLOS group/clause editor used by RuleBuilder. Props: `node` (tree node), `glossary`, `thresholds`, `isRoot`, `depth`. Renders an AND/OR segmented toggle per group, clause rows with three selects (metric GL-code, operator, threshold TH-code), join pills, and per-row tools.
- methods: `setOp(op)` — switch group AND/OR; `onClause(child, key, ev)` — update a clause field; `addClause()` / `addGroup()`; `removeChild(i)`; `moveChild(i, dir)` — reorder; `wrapChild(i)` — wrap a clause into a nested group; `ungroupChild(i)` — flatten a nested group; `bubble()` — emit `change` upward.

#### `resources/js/Account/components/ruleLogic.js`
Pure framework-free engine converting between `condition_logic_by_ids` strings and an editable tree (`{kind:'clause',metric,op,value}` / `{kind:'group',op,children}`). Exports:
- `OPERATORS` — `['>=','<=','!=','<','>','=']` (aliases `==`,`=<`,`=>`,`<>` normalized on parse).
- `opLabel(op)` — friendly operator word.
- `emptyTree()` / `emptyClause()` / `emptyGroup(op)` — constructors.
- `isComplete(node)` / `clauseCount(node)` — validation helpers.
- `parse(str)` — tree or empty fallback; `parseSafe(str)` — `{ok, tree | error, raw}` (drives the raw-mode fallback).
- `serialize(tree)` — clean `IF …` string (prunes incomplete clauses; parens only for nested multi-child groups); `serializePreview(tree)` — keeps `[metric]`/`[value]` placeholders.
- `toReadable(tree, glossaryMap, thresholdMap)` — human sentence for `condition_logic_rule`.
- Internal: `tokenize`, recursive-descent `parseOr/parseAnd/parsePrimary` (OR lower precedence), `flattenSameOp`, `serializeNode`, `pruneIncomplete`, `readableNode`.

### resources/css + scss + views

- `resources/css/puvii.css` — large minified legacy CSS bundle (5 physical lines); not referenced by the current build.
- `resources/scss/app.scss` — **empty file** (0 bytes); still the Mix CSS entry, producing an empty `public/css/app.css`.
- `resources/views/accounts.blade.php` — **the SPA shell** (custom): loads Google Fonts (Inter/JetBrains Mono), local bootstrap/site/glyphicon CSS, CDN jQuery + Select2 + Font Awesome + Bootstrap Icons, sets `#csrf` meta, mounts `#app`, loads `/js/Account.js` (cache-busted). Served by the web.php catch-all.
- `resources/views/welcome.blade.php` — *boilerplate* stock Laravel welcome page (unused).
- `resources/views/emails/trackingInvoiceMail.blade.php` — custom email template rendering `$emailMessage` + `$fileUrl` download link (legacy shared-repo tracking/invoice mail; no mailer invokes it in this repo).

---

## routes/ — FULL

### `routes/api.php`
All API endpoints (mounted under `/api` with the `api` middleware group → `throttle:200,1`).
**Public (no auth):**
- `POST /add-new-users` → `AuthController@register`
- `POST /login` → `AuthController@login`
- `GET /configurations` → `AuthController@configurations`
- `GET /test` → `AuthController@TEst` *(debug — dumps all users)*
- `GET /warehouse-location-wise-stock-update` → `StockController@WarehouseLocationWiseStockUpdate` *(unauthenticated stock sync trigger)*

**Authenticated group (`CheckAuthMiddleware` by class):**
- `GET /me` → `AuthController@me`; `POST /logout` → `AuthController@logout`
- `GET /products`, `GET /products/{id}` → **ProductController (does not exist — dead route)**
- `GET|POST /sales`, `GET /sales/{id}` → **SaleController (does not exist — dead route)**
- **`prefix('threshold-config')` — the BLOS API:**
  - `GET thresholds` → `thresholdsIndex`; `PUT thresholds/{thresholdId}` → `thresholdsUpdate` *(any authenticated user, domain-scoped)*
  - **admin-only subgroup (`middleware ['admin']`):** `GET stats`; `GET|POST business-rules`, `PUT|DELETE business-rules/{ruleId}`; `GET|POST condition-logics`, `PUT|DELETE condition-logics/{conditionId}`; `GET|POST rule-threshold-mappings`, `PUT|DELETE rule-threshold-mappings/{mappingId}`; `GET|POST glossary`, `PUT|DELETE glossary/{glossaryId}`; `POST thresholds`, `DELETE thresholds/{thresholdId}`; `GET|POST versions`, `PUT|DELETE versions/{versionId}`; `GET domains`, `PUT domains/rename`; `GET domain-access`, `GET domain-access/matrix`, `PUT|POST domain-access/{userId}`, `DELETE domain-access/{userId}/{domain}`; `GET export-yaml`, `GET export-csv`; `POST bulk-import/{tab}` — all → `ThresholdConfigurationController`.
- **File Library (any authenticated user):** `GET /folders/tree`, `GET /folders/{folder}/download-zip`, `GET /folders/{folder}`, `GET /files/{managed_file}/download`, `GET /files/{managed_file}/content` → `FolderFileController`.
- **admin-only subgroup:** `POST /folders`, `PUT /folders/{folder}/rename`, `DELETE /folders/{folder}`, `POST /folders/{folder}/files`, `POST /files/{managed_file}/reupload`, `PUT /files/{managed_file}/rename`, `PUT /files/{managed_file}/move`, `DELETE /files/{managed_file}` → `FolderFileController`; `Route::apiResource('categories', …)` + `POST /categories/{id}/image` → **CategoryController (missing — dead)**; `POST|PUT|DELETE /products…` + image → **ProductController (missing — dead)**; `DELETE /images/{id}` → **ImageController (missing — dead)**; `GET|PUT /inventory…` → **InventoryController (missing — dead)**; `PUT /sales/{id}` → **SaleController (missing — dead)**; `GET /reports/daily|monthly|top-products` → **ReportController (missing — dead)**; `GET|POST /users`, `PUT /users/{id}` → `UserController@index/store/update` (real).

### `routes/web.php`
- `GET /testData` → `Ppc\TestingController@testData` (ETL test trigger).
- `GET {any?}` (regex excluding `api/…`) → returns `view('accounts')` — the SPA catch-all.

### `routes/channels.php`
- `Broadcast::channel('orders-updates.{ids}', fn($user, $role) => $role)` — permissive order-update channel auth.
- `Broadcast::channel('chat', fn() => true)` — open chat channel.

### `routes/console.php`
*Boilerplate* — only the stock `inspire` artisan closure command.

---

## tests/

- `tests/CreatesApplication.php` — *boilerplate* trait bootstrapping the app for tests.
- `tests/TestCase.php` — *boilerplate* abstract base TestCase.
- `tests/Feature/ExampleTest.php` — *boilerplate* stock "GET / returns 200" example.
- `tests/Unit/ExampleTest.php` — *boilerplate* stock "true is true" example.
- **There are no real tests in this repository.**

---

## Coverage statement

- **Total files walked: 209** (every tracked file excluding the skip list below), matching a pruned `find` count executed 2026-07-07.
- **Full-detail entries (every public symbol listed): ≈105 files** — 5 controllers + HTTP kernel + 13 middleware + 17 root models + 1 service + 2 jobs + 2 events + 1 cast + 1 console command + 4 route files + 7 migrations + seeder + factory + 4 deep config files + 5 root manifests (composer.json, package.json, phpunit.xml, webpack.mix.js, DATABASE_SCHEMA.md) + 26 frontend JS/Vue files + 15 docs/sql files.
- **One-line entries: ≈104 files** — 34 shared-repo models (CentralizedEtlData 26, Inventory 7, auth 1), 2 shared-scope controllers (Stock, Testing — with brief method notes), 12 shallow config files, 5 providers, boilerplate (bootstrap 6, lang 4, tests 4, views 3, public 12, exceptions 1, console kernel 1, misc root files ~22 incl. lockfiles).
- **Skipped entirely and why:**
  - `vendor/` — Composer packages (third-party).
  - `node_modules/` — NPM packages (third-party).
  - `storage/` — runtime logs/cache/uploads (generated data).
  - `.git/`, `.claude/worktrees/` — VCS/tooling internals.
  - `public/js/*` (10 files) and `public/css/*` (4 files) — Laravel Mix **build artifacts** of `resources/js/**` and `resources/scss/app.scss` (source is mapped instead).
  - Binary asset **contents** (`public/Img/*`, favicon, woff2, hello_world.pdf) — listed above as one-liners; binaries not inspected.
  - `composer.lock` / `package-lock.json` contents — generated lockfiles, listed as one-liners.
  - `.env` values — secrets; existence noted, contents deliberately not documented.
  - `bootstrap/cache/*` contents — framework-generated manifests/temp files, listed as one-liners.
  - `scripts/` — exists but is empty (0 files).

*End of CODE_MAP — REQ-04-D07. Repository remains canonical; verify against source before acting on any entry.*


---

# PART D — DATA DICTIONARY

---

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


---

# PART E — API REFERENCE

---

# API Reference — ledsone-centralizer

| Field | Value |
|---|---|
| Date | 2026-07-07 |
| Deliverable | REQ-04-D07 |
| Project | PRJ-2026-003_blos-project-sentinel |
| Status | DRAFT — awaiting review |
| Source | Repo scan of 2026-07-07, `C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer` (branch `claude/dazzling-lehmann-32c5a5`, HEAD `f4eb6df`) |
| Scope | DEEP: auth, users, threshold-config, folder/file library. BRIEF: shared-repo modules (products, categories, inventory, sales, reports, images, stock-sync, PPC/ETL) |

All file:line references are relative to the repo root. All API routes carry the `api` prefix (i.e. `routes/api.php` entry `/login` is served at `/api/login`).

---

## 1. Authentication model and middleware gates

There are three gate levels, all defined in the codebase (no Sanctum/Passport — this is a hand-rolled token scheme):

| Gate | Mechanism | Evidence |
|---|---|---|
| **Public** | No middleware at all. | `routes/api.php:16-22` |
| **Bearer token** | `App\Http\Middleware\CheckAuthMiddleware` — reads `Authorization: Bearer <token>`, looks up `User where token = <token>` and requires `is_active`; on success binds the user via `Auth::onceUsingId()` + request user resolver; otherwise returns `401 {"error":"Invalid authentication"}`. | `app/Http/Middleware/CheckAuthMiddleware.php:13-29`; applied at `routes/api.php:24` |
| **Admin** | Alias `admin` → `App\Http\Middleware\EnsureUserIsAdmin` — requires `$request->user()->role === 'admin'`, else `403 {"error":"Admin access required"}`. Always nested inside the bearer-token group. | `app/Http/Kernel.php:68`; `app/Http/Middleware/EnsureUserIsAdmin.php:10-17`; applied at `routes/api.php:41,87` |
| **Domain-scoped** (application-level, not middleware) | Inside `ThresholdConfigurationController`: non-admin users only see/modify thresholds whose `domain` is in their allowed set (union of `user.domain` column + `user_domain_access` pivot rows, case-insensitive). Admins bypass. | `app/Http/Controllers/Api/ThresholdConfigurationController.php:45-114` |

Token facts (relevant to every gated endpoint):
- Tokens are `Str::random(32)`, stored **in plain text** in `user.token` (`app/Http/Controllers/auth/AuthController.php:55-57`), truncated to 32 chars by the model mutator (`app/Models/User.php:105-112`).
- One token per user: each login overwrites the previous token, so a second login invalidates the first session. Tokens never expire.
- The `User` model maps friendly attributes onto legacy columns: table `user`, PK column `user`, `name` ⇄ `user_firstname`/`user_lastname`, `email` ⇄ `user_email`, `role` ⇄ `config_role`, `password_hash` ⇄ `user_password`, `is_active` ⇄ `user_status` (`app/Models/User.php:12-103`).
- `App\Http\Middleware\EnsureDomainOwner` exists (`app/Http/Middleware/EnsureDomainOwner.php`) but is **not referenced by any route** — dead middleware.

Generic error behaviour used throughout:
- `Model::firstOrFail()` / `findOrFail()` / implicit route-model binding miss → Laravel renders `404` (JSON for API requests).
- `$request->validate()` failure → Laravel renders `422` with `{"message": ..., "errors": {...}}`; controllers using `Validator::make` return their own `422 {"success":false,"message":"Validation failed","errors":{...}}` shape.

---

## 2. Endpoint summary table (every route in routes/api.php)

Gate legend: **P** = public, **T** = bearer token, **T+A** = bearer token + admin, **T(+D)** = bearer token with domain scoping for non-admins, **T+A(+D)** = admin with domain check.

| # | Method | URL | Gate | Scope | Route line |
|---|---|---|---|---|---|
| 1 | POST | /api/add-new-users | P | BLOS — deep | routes/api.php:16 |
| 2 | POST | /api/login | P | BLOS — deep | routes/api.php:17 |
| 3 | GET | /api/configurations | P | BLOS — deep | routes/api.php:18 |
| 4 | GET | /api/test | P | BLOS — deep | routes/api.php:19 |
| 5 | GET | /api/warehouse-location-wise-stock-update | P | Shared — brief | routes/api.php:22 |
| 6 | GET | /api/me | T | BLOS — deep | routes/api.php:25 |
| 7 | POST | /api/logout | T | BLOS — deep | routes/api.php:26 |
| 8 | GET | /api/products | T | Shared — brief (dead) | routes/api.php:28 |
| 9 | GET | /api/products/{id} | T | Shared — brief (dead) | routes/api.php:29 |
| 10 | GET | /api/sales | T | Shared — brief (dead) | routes/api.php:31 |
| 11 | POST | /api/sales | T | Shared — brief (dead) | routes/api.php:32 |
| 12 | GET | /api/sales/{id} | T | Shared — brief (dead) | routes/api.php:33 |
| 13 | GET | /api/threshold-config/thresholds | T(+D) | BLOS — deep | routes/api.php:37 |
| 14 | PUT | /api/threshold-config/thresholds/{thresholdId} | T(+D) | BLOS — deep | routes/api.php:38 |
| 15 | GET | /api/threshold-config/stats | T+A | BLOS — deep | routes/api.php:42 |
| 16 | GET | /api/threshold-config/business-rules | T+A | BLOS — deep | routes/api.php:43 |
| 17 | POST | /api/threshold-config/business-rules | T+A | BLOS — deep | routes/api.php:44 |
| 18 | PUT | /api/threshold-config/business-rules/{ruleId} | T+A | BLOS — deep | routes/api.php:45 |
| 19 | DELETE | /api/threshold-config/business-rules/{ruleId} | T+A | BLOS — deep | routes/api.php:46 |
| 20 | GET | /api/threshold-config/condition-logics | T+A | BLOS — deep | routes/api.php:47 |
| 21 | POST | /api/threshold-config/condition-logics | T+A | BLOS — deep | routes/api.php:48 |
| 22 | PUT | /api/threshold-config/condition-logics/{conditionId} | T+A | BLOS — deep | routes/api.php:49 |
| 23 | DELETE | /api/threshold-config/condition-logics/{conditionId} | T+A | BLOS — deep | routes/api.php:50 |
| 24 | GET | /api/threshold-config/rule-threshold-mappings | T+A | BLOS — deep | routes/api.php:51 |
| 25 | POST | /api/threshold-config/rule-threshold-mappings | T+A | BLOS — deep | routes/api.php:52 |
| 26 | PUT | /api/threshold-config/rule-threshold-mappings/{mappingId} | T+A | BLOS — deep | routes/api.php:53 |
| 27 | DELETE | /api/threshold-config/rule-threshold-mappings/{mappingId} | T+A | BLOS — deep | routes/api.php:54 |
| 28 | GET | /api/threshold-config/glossary | T+A | BLOS — deep | routes/api.php:55 |
| 29 | POST | /api/threshold-config/glossary | T+A | BLOS — deep | routes/api.php:56 |
| 30 | PUT | /api/threshold-config/glossary/{glossaryId} | T+A | BLOS — deep | routes/api.php:57 |
| 31 | DELETE | /api/threshold-config/glossary/{glossaryId} | T+A | BLOS — deep | routes/api.php:58 |
| 32 | POST | /api/threshold-config/thresholds | T+A | BLOS — deep | routes/api.php:59 |
| 33 | DELETE | /api/threshold-config/thresholds/{thresholdId} | T+A(+D) | BLOS — deep | routes/api.php:60 |
| 34 | GET | /api/threshold-config/versions | T+A | BLOS — deep | routes/api.php:61 |
| 35 | POST | /api/threshold-config/versions | T+A | BLOS — deep | routes/api.php:62 |
| 36 | PUT | /api/threshold-config/versions/{versionId} | T+A | BLOS — deep | routes/api.php:63 |
| 37 | DELETE | /api/threshold-config/versions/{versionId} | T+A | BLOS — deep | routes/api.php:64 |
| 38 | GET | /api/threshold-config/domains | T+A | BLOS — deep | routes/api.php:67 |
| 39 | PUT | /api/threshold-config/domains/rename | T+A | BLOS — deep | routes/api.php:68 |
| 40 | GET | /api/threshold-config/domain-access | T+A | BLOS — deep | routes/api.php:69 |
| 41 | GET | /api/threshold-config/domain-access/matrix | T+A | BLOS — deep | routes/api.php:70 |
| 42 | PUT | /api/threshold-config/domain-access/{userId} | T+A | BLOS — deep | routes/api.php:71 |
| 43 | POST | /api/threshold-config/domain-access/{userId} | T+A | BLOS — deep | routes/api.php:72 |
| 44 | DELETE | /api/threshold-config/domain-access/{userId}/{domain} | T+A | BLOS — deep | routes/api.php:73 |
| 45 | GET | /api/threshold-config/export-yaml | T+A | BLOS — deep | routes/api.php:74 |
| 46 | GET | /api/threshold-config/export-csv | T+A | BLOS — deep | routes/api.php:75 |
| 47 | POST | /api/threshold-config/bulk-import/{tab} | T+A | BLOS — deep | routes/api.php:76 |
| 48 | GET | /api/folders/tree | T | BLOS — deep | routes/api.php:81 |
| 49 | GET | /api/folders/{folder}/download-zip | T | BLOS — deep | routes/api.php:82 |
| 50 | GET | /api/folders/{folder} | T | BLOS — deep | routes/api.php:83 |
| 51 | GET | /api/files/{managed_file}/download | T | BLOS — deep | routes/api.php:84 |
| 52 | GET | /api/files/{managed_file}/content | T | BLOS — deep | routes/api.php:85 |
| 53 | POST | /api/folders | T+A | BLOS — deep | routes/api.php:88 |
| 54 | PUT | /api/folders/{folder}/rename | T+A | BLOS — deep | routes/api.php:89 |
| 55 | DELETE | /api/folders/{folder} | T+A | BLOS — deep | routes/api.php:90 |
| 56 | POST | /api/folders/{folder}/files | T+A | BLOS — deep | routes/api.php:91 |
| 57 | POST | /api/files/{managed_file}/reupload | T+A | BLOS — deep | routes/api.php:92 |
| 58 | PUT | /api/files/{managed_file}/rename | T+A | BLOS — deep | routes/api.php:93 |
| 59 | PUT | /api/files/{managed_file}/move | T+A | BLOS — deep | routes/api.php:94 |
| 60 | DELETE | /api/files/{managed_file} | T+A | BLOS — deep | routes/api.php:95 |
| 61 | GET | /api/categories | T+A | Shared — brief (dead) | routes/api.php:97 |
| 62 | POST | /api/categories | T+A | Shared — brief (dead) | routes/api.php:97 |
| 63 | GET | /api/categories/{category} | T+A | Shared — brief (dead) | routes/api.php:97 |
| 64 | PUT/PATCH | /api/categories/{category} | T+A | Shared — brief (dead) | routes/api.php:97 |
| 65 | DELETE | /api/categories/{category} | T+A | Shared — brief (dead) | routes/api.php:97 |
| 66 | POST | /api/categories/{id}/image | T+A | Shared — brief (dead) | routes/api.php:98 |
| 67 | POST | /api/products | T+A | Shared — brief (dead) | routes/api.php:99 |
| 68 | PUT | /api/products/{id} | T+A | Shared — brief (dead) | routes/api.php:100 |
| 69 | DELETE | /api/products/{id} | T+A | Shared — brief (dead) | routes/api.php:101 |
| 70 | POST | /api/products/{id}/image | T+A | Shared — brief (dead) | routes/api.php:102 |
| 71 | DELETE | /api/images/{id} | T+A | Shared — brief (dead) | routes/api.php:103 |
| 72 | GET | /api/inventory | T+A | Shared — brief (dead) | routes/api.php:105 |
| 73 | PUT | /api/inventory/{id} | T+A | Shared — brief (dead) | routes/api.php:106 |
| 74 | PUT | /api/sales/{id} | T+A | Shared — brief (dead) | routes/api.php:108 |
| 75 | GET | /api/reports/daily | T+A | Shared — brief (dead) | routes/api.php:110 |
| 76 | GET | /api/reports/monthly | T+A | Shared — brief (dead) | routes/api.php:111 |
| 77 | GET | /api/reports/top-products | T+A | Shared — brief (dead) | routes/api.php:112 |
| 78 | GET | /api/users | T+A | BLOS — deep | routes/api.php:114 |
| 79 | POST | /api/users | T+A | BLOS — deep | routes/api.php:115 |
| 80 | PUT | /api/users/{id} | T+A | BLOS — deep | routes/api.php:116 |

Web routes (`routes/web.php`, not counted in the API total): `GET /testData` → `Ppc\TestingController@testData` (public, triggers a PPC/ETL data sync — shared-repo module, `routes/web.php:5`), and a catch-all `GET {any?}` returning the `accounts` SPA view for every non-`api/` path (`routes/web.php:7-9`).

> **"(dead)" rows:** the controllers `App\Http\Controllers\Api\CategoryController`, `ProductController`, `InventoryController`, `SaleController`, `ReportController`, and `ImageController` are imported at `routes/api.php:5-11` but **do not exist anywhere in the repository** (`app/Http/Controllers/Api/` contains only `FolderFileController.php`, `ThresholdConfigurationController.php`, `UserController.php`). Every route pointing at them returns **500 "Target class does not exist"** at dispatch. 22 of the 23 shared routes are dead; only the stock-sync route has a real controller.

---

## 3. Auth endpoints (DEEP)

Controller: `app/Http/Controllers/auth/AuthController.php` (note lowercase `auth` namespace).

### 3.1 POST /api/add-new-users — register

- **Gate:** PUBLIC (`routes/api.php:16`). No auth of any kind.
- **Handler:** `AuthController@register` — `app/Http/Controllers/auth/AuthController.php:99`.
- **Validation (verbatim, lines 101-108):**
  - `name` → `required|string|max:100`
  - `email` → `required|string|email|max:150|unique:user,user_email`
  - `role` → `nullable|in:admin,cashier,domain_owner`
  - `domain` → `nullable|string|max:100`
  - `password` → `required|string|min:6`
  - `confirmPassword` → `required|string|same:password`
- **Success:** `201` — `{"success":true,"message":"User registered successfully","data":{"id","name","email","role"}}` (lines 129-138).
- **Errors:** `422 {"success":false,"message":"Validation failed","errors":{...}}` (lines 110-116); `500 {"success":false,"message":"Registration failed","error":<exception message>}` on DB failure (lines 139-145).
- **Side effects:** inserts a `user` row with `password_hash = Hash::make(password)`, `role = request role or 'cashier'`, `is_active = true`, a fresh 32-char `token`, and `domain` (lines 119-127). The model's `creating` hook also defaults `user_accounts = 'list'` (`app/Models/User.php:114-121`).
- **⚠ Finding:** because the route is public and `role` accepts `admin`, **an unauthenticated caller can create an admin account** (`role => 'nullable|in:admin,cashier,domain_owner'`, line 104).

### 3.2 POST /api/login

- **Gate:** PUBLIC (`routes/api.php:17`).
- **Handler:** `AuthController@login` — `AuthController.php:30`.
- **Validation (verbatim, lines 32-35):** `email` → `required|string|email`; `password` → `required|string`.
- **Logic:** finds `User where user_email = email`; rejects if missing, `!is_active`, or `Hash::check` fails (line 48). On success generates `Str::random(32)`, saves it to `user.token` (lines 55-57).
- **Success:** `200` — `{"success":true,"message":"Login successful","data":{"token","user":{"id","name","email","role","domain"}}}` (lines 59-72).
- **Errors:** `422` validation shape as above (lines 37-43); `401 {"success":false,"message":"Invalid email or password"}` (lines 48-53); `500 {"success":false,"message":"Login failed","error":...}` (lines 73-79).
- **Side effects:** overwrites `user.token` — any previously issued token for that user stops working.

### 3.3 GET /api/configurations

- **Gate:** PUBLIC (`routes/api.php:18`). Optionally reads a bearer token.
- **Handler:** `AuthController@configurations` — `AuthController.php:208`.
- **Validation:** none.
- **Logic:** if a bearer token matches a user, the same token is echoed back in the response; config data is hard-coded, not DB-driven despite the docblock (lines 226-231).
- **Success:** `200` — `{"success":true,"data":{"app_name","app_env","version":"1.0.0"},"token"?:<echoed bearer token>}` (lines 233-243).
- **Errors:** `500 {"success":false,"message":"Failed to load configurations","error":...}` (lines 244-249).
- **Side effects:** none.

### 3.4 GET /api/test

- **Gate:** PUBLIC (`routes/api.php:19`).
- **Handler:** `AuthController@TEst` — `AuthController.php:82`.
- **Validation:** none.
- **Success:** `200` — `{"success":true,"message":"Test successful","data":[<every row of the user table>]}` (lines 85-90). The model hides `user_password` and `token` (`app/Models/User.php:22`), but all other user columns (emails, names, roles, status, domain) are exposed.
- **⚠ Finding:** unauthenticated full user-table dump. Debug leftover; should be removed or gated.

### 3.5 GET /api/me

- **Gate:** Bearer token (`routes/api.php:25`).
- **Handler:** `AuthController@me` — `AuthController.php:154`.
- **Validation:** none.
- **Success:** `200` — `{"success":true,"data":{"user":{"id","name","email","role","domain"}}}` (lines 160-171).
- **Errors:** `401 {"success":false,"message":"Unauthenticated"}` if the resolver returns no user (lines 157-159) — in practice unreachable because the middleware already 401s; middleware failure returns `401 {"error":"Invalid authentication"}`.
- **Side effects:** none.

### 3.6 POST /api/logout

- **Gate:** Bearer token (`routes/api.php:26`).
- **Handler:** `AuthController@logout` — `AuthController.php:174`.
- **Validation:** none.
- **Logic:** re-reads the bearer token, finds the matching user, sets `token = null` (lines 177-187). Succeeds even if the token matches nobody.
- **Success:** `200` — `{"success":true,"message":"Logout successful"}` (lines 189-192).
- **Errors:** `500 {"success":false,"message":"Logout failed","error":...}` (lines 193-198).
- **Side effects:** clears `user.token` (revokes the session).

---

## 4. Users endpoints (DEEP)

Controller: `app/Http/Controllers/Api/UserController.php`. All three routes are bearer + admin (`routes/api.php:87,114-116`).

### 4.1 GET /api/users

- **Handler:** `UserController@index` — `UserController.php:12`.
- **Validation:** none.
- **Success:** `200` — `{"success":true,"data":[{"id","name","email","role","domain","is_active","created_at"}]}` ordered by `user_firstname`, `user_lastname` (lines 14-26).
- **Errors:** `401` (middleware), `403` (non-admin).

### 4.2 POST /api/users

- **Handler:** `UserController@store` — `UserController.php:29`.
- **Validation (verbatim, lines 31-37, via `$request->validate` → framework `422` on failure):**
  - `name` → `required|string|max:100`
  - `email` → `required|string|email|max:150|unique:user,user_email`
  - `password` → `required|string|min:6`
  - `role` → `nullable|in:admin,cashier,domain_owner`
  - `domain` → `nullable|string|max:100`
- **Success:** `201` — `{"success":true,"data":{"id","name","email","role","domain","is_active"}}` (lines 43-53).
- **Side effects:** creates a `user` row; `password_hash = Hash::make(password)`, default `role = 'cashier'`, `is_active = true` (lines 38-42). No token is issued (unlike the public register endpoint).

### 4.3 PUT /api/users/{id}

- **Handler:** `UserController@update` — `UserController.php:56`.
- **Validation (verbatim, lines 59-66):**
  - `name` → `sometimes|string|max:100`
  - `email` → `sometimes|string|email|max:150|unique:user,user_email,{id},user`
  - `password` → `nullable|string|min:6`
  - `role` → `nullable|in:admin,cashier,domain_owner`
  - `domain` → `nullable|string|max:100`
  - `is_active` → `boolean`
- **Success:** `200` — same `{"success":true,"data":{...}}` shape as store (lines 72-82).
- **Errors:** `404` via `findOrFail` (line 58); `422` on validation.
- **Side effects:** updates the user row; re-hashes `password` only when non-empty (lines 67-70). Setting `is_active=false` disables login and immediately invalidates the user's bearer token (middleware requires `is_active`, `CheckAuthMiddleware.php:19`). No delete endpoint exists.

---

## 5. Threshold-config endpoints (DEEP)

Controller: `app/Http/Controllers/Api/ThresholdConfigurationController.php` (1121 lines, read in full). Route prefix `threshold-config` (`routes/api.php:35`). Everything is bearer-gated; everything except `GET/PUT thresholds` is additionally admin-gated (`routes/api.php:41`).

Shared behaviours:
- **Code normalization:** `normalizeCodeFields()` uppercases and strips all whitespace from business-code fields before validation ("gl- 005" → "GL-005") (lines 118-129).
- **`Validator::make` error shape:** `422 {"success":false,"message":"Validation failed","errors":{...}}` (used in every store/update).
- **`firstOrFail` misses:** `404` JSON.
- **Domain scoping helpers:** `isAdmin` (line 24), `allowedDomainsFor` = union of `user.domain` column + `user_domain_access` pivot, deduped case-insensitively (lines 45-77), `ensureDomainAllowed` (line 79), `applyThresholdDomainFilterForNonAdmin` — SQL filter `LOWER(TRIM(COALESCE(domain,""))) = ?` per allowed domain, or `1 = 0` when the user has none (lines 96-114).

### 5.1 Thresholds

**GET /api/threshold-config/thresholds** — `thresholdsIndex`, line 416. Gate: bearer, domain-scoped.
- Query params: `domain` (admin only, line 422-424), `status`, `type`, `search` (LIKE against `label`, `threshold_key`, `alternative_names`, lines 433-444).
- Non-admin: if allowed-domain set is empty → `200 {"success":true,"data":[]}` short-circuit (lines 426-429); otherwise rows filtered to allowed domains.
- Success: `200 {"success":true,"data":[<threshold rows>]}` ordered by `threshold_id` (line 447).

**POST /api/threshold-config/thresholds** — `thresholdsStore`, line 450. Gate: bearer + admin.
- Validation (verbatim, lines 453-478): `threshold_id` → `['required','string','max:20','regex:/^TH-\d+$/','unique:thresholds,threshold_id']`; `threshold_key` → `required|string|max:150|unique:thresholds,threshold_key`; `label` → `required|string|max:150`; `description` → `nullable|string`; `alternative_names` → `nullable|string|max:255`; `value` → `nullable|numeric`; `value_type` → `nullable|string|max:20`; `unit` → `nullable|string|max:30`; `type` → `nullable|string|max:30`; `fulfillment` → `nullable|string|max:30`; `channel` → `nullable|string|max:30`; `account` → `nullable|string|max:50`; `site` → `nullable|string|max:20`; `domain` → `nullable|string|max:100`; `owner` → `nullable|string|max:100`; `created_by` → `nullable|string|max:100`; `created_at` → `nullable|date`; `last_changed_by` → `nullable|string|max:100`; `last_changed_at` → `nullable|date`; `version` → `nullable|integer`; `status` → `nullable|string|max:20`; `effective_from` → `nullable|date`; `approver` → `nullable|string|max:100`; `management_approval` → `nullable|string|max:20`.
- Success: `201 {"success":true,"message":"Threshold created","data":<row>}` (line 483). Side effect: insert into `thresholds`. No version row is created on create.

**PUT /api/threshold-config/thresholds/{thresholdId}** — `thresholdsUpdate`, line 486. Gate: bearer, **domain-checked** (`ensureDomainAllowed`, lines 489-492 → `403 {"success":false,"message":"You do not have access to this domain."}`). Not admin-gated — any user with domain access can update.
- Validation (verbatim, lines 493-521): same field set as store minus the unique rules, all `nullable` (`threshold_key` → `nullable|string|max:150`, `label` → `nullable|string|max:150`, ... `effective_from` → `nullable|date`), plus `change_reason` → `nullable|string|max:1000` — code comment: *"TEMP: change_reason made optional on request. Restore to 'required|string|min:10|max:1000' when re-enabling the reason rule."* (lines 513-516), `status` → `nullable|string|max:20`, `version` → `nullable|integer`, `approver` → `nullable|string|max:100`, `management_approval` → `nullable|string|max:20`.
- Logic: `change_reason` is stripped from the update payload (input-only; logged to the version table, lines 526-529). Value change detected by `abs(new - old) > 0.0000001` (line 531).
  - **No value change:** plain `$row->update()` → `200 {"success":true,"message":"Threshold updated","data":<fresh row>}` (lines 533-536).
  - **Value change:** computes `nextVersion = max(row.version, max(threshold_versions.version_number)) + 1`; stamps `last_changed_by` (user name or "Unknown") and `last_changed_at` (UTC now); then inside a `DB::transaction` updates the threshold **and inserts a `threshold_versions` row** `{threshold_id, old_value, new_value, changed_by, approved_by:null, change_reason (or null), timestamp: now UTC, version_number}` (lines 539-551). Response same `200` shape (line 552).
- Errors: `404` (unknown threshold_id, line 488), `403` (domain), `422` (validation).

**DELETE /api/threshold-config/thresholds/{thresholdId}** — `thresholdsDestroy`, line 555. Gate: bearer + admin, plus a domain check via `Auth::user()` (lines 558-561; admins always pass, so effectively admin-only).
- Success: `200 {"success":true,"message":"Threshold deleted"}` (line 567).
- Side effects — **cascade inside `DB::transaction`** (lines 562-566): deletes all `threshold_versions` rows for the threshold, deletes all `rule_threshold_mapping` rows for it, then deletes the threshold itself.
- Errors: `404` unknown id; `403` domain (unreachable for admins).

### 5.2 Business rules

**GET /api/threshold-config/business-rules** — `businessRulesIndex`, line 131. Returns `200 {"success":true,"data":[<rows ordered by rule_id>]}`. No filters.

Shared rule set `businessRulesRules($ruleId = null)` (verbatim, lines 138-154): `rule_id` → `['required','string','max:20','regex:/^BL-\d+$/', 'unique:business_rules,rule_id[,{ruleId},rule_id]']`; `rule_name` → `required|string|max:150`; `description` → `nullable|string`; `domain` → `nullable|string|max:100`; `status` → `nullable|string|max:20`; `owner` → `nullable|string|max:100`; `created_by` → `nullable|string|max:100`; `created_at` → `nullable|date`.

**POST business-rules** — `businessRulesStore`, line 156. Normalizes `rule_id`; `422` on validation; success `201 {"success":true,"message":"Business rule created","data":<fresh row>}` (line 165). Side effect: insert into `business_rules`.

**PUT business-rules/{ruleId}** — `businessRulesUpdate`, line 168. `404` if `rule_id` not found (line 170); unique rule ignores the current `rule_id`; success `200 {"success":true,"message":"Business rule updated","data":<fresh row>}` (line 177).

**DELETE business-rules/{ruleId}** — `businessRulesDestroy`, line 180. **Referential guards** (not DB constraints): returns `422 {"success":false,"message":"Cannot delete: rule-threshold mappings still reference this rule_id."}` (lines 184-186) or `422 "Cannot delete: condition logics still reference this rule_id."` (lines 187-189). Success `200 {"success":true,"message":"Business rule deleted"}` (line 191). `404` if unknown.

### 5.3 Condition logics

**GET /api/threshold-config/condition-logics** — `conditionLogicsIndex`, line 194. Query filters: `rule_id`, `stage` (lines 197-202). `200 {"success":true,"data":[...]}` ordered by `condition_id`.

Shared rule set `conditionLogicsRules()` (verbatim, lines 206-226): `rule_id` → `required|string|max:20|regex:/^BL-\d+$/`; `condition_logic_by_ids` → `nullable|string`; `condition_logic_rule` → `nullable|string`; `decision_output` → `nullable|string`; `stage` → `nullable|string|max:30`; `stage_description` → `nullable|string`; `level` → `nullable|string|max:50`; `type` → `nullable|string|max:30`; `fulfillment` → `nullable|string|max:30`; `channel` → `nullable|string|max:30`; `account` → `nullable|string|max:50`; `site` → `nullable|string|max:20`; `status` → `nullable|string|max:20`; `owner` → `nullable|string|max:100`; `created_by` → `nullable|string|max:100`; `created_at` → `nullable|date`.

Cross-reference guard `unknownConditionCodes()` (lines 233-262): extracts every `GL-\d+` / `TH-\d+` code from `condition_logic_by_ids` and checks existence in `glossary` / `thresholds`. On any unknown code, store/update return `422 {"success":false,"message":"Unknown code(s) in the condition logic: <codes>. Every GL- code must exist in the glossary and every TH- code in thresholds."}` (lines 271-274, 287-290).

**POST condition-logics** — `conditionLogicsStore`, line 264. Success `201 {"success":true,"message":"Condition logic created","data":<fresh row>}` (line 276). `condition_id` is DB auto-increment (client never supplies it).

**PUT condition-logics/{conditionId}** — `conditionLogicsUpdate`, line 279. `404` on unknown `condition_id`; same code guard; success `200 ... "Condition logic updated"` (line 292).

**DELETE condition-logics/{conditionId}** — `conditionLogicsDestroy`, line 295. `404` or `200 {"success":true,"message":"Condition logic deleted"}` (line 298). No referential guard.

### 5.4 Rule-threshold mappings

**GET /api/threshold-config/rule-threshold-mappings** — `ruleThresholdMappingsIndex`, line 301. Filters: `rule_id`, `threshold_id` (lines 304-309). `200 {"success":true,"data":[...]}` ordered by `mapping_id`.

Shared rule set `ruleThresholdMappingsRules($mappingId = null)` (verbatim, lines 313-326): `mapping_id` → `['required','string','max:20','regex:/^MAP-\d+$/', 'unique:rule_threshold_mapping,mapping_id[,{mappingId},mapping_id]']`; `rule_id` → `required|string|max:20|regex:/^BL-\d+$/`; `threshold_id` → `required|string|max:20|regex:/^TH-\d+$/`; `created_by` → `nullable|string|max:100`; `created_at` → `nullable|date`.
- Note: `rule_id`/`threshold_id` are only pattern-checked here — no `exists:` rule, so a mapping can reference a nonexistent rule/threshold.

**POST rule-threshold-mappings** — `ruleThresholdMappingsStore`, line 328. Normalizes `mapping_id`, `rule_id`, `threshold_id`. Success `201 ... "Rule-threshold mapping created"` (line 336).

**PUT rule-threshold-mappings/{mappingId}** — `ruleThresholdMappingsUpdate`, line 339. `404`/`422`; success `200 ... "Rule-threshold mapping updated"` (line 348).

**DELETE rule-threshold-mappings/{mappingId}** — `ruleThresholdMappingsDestroy`, line 351. `404` or `200 {"success":true,"message":"Rule-threshold mapping deleted"}` (line 354).

### 5.5 Glossary

**GET /api/threshold-config/glossary** — `glossaryIndex`, line 357. Filters: `type`; `search` (LIKE against `term`, `definition`, `alternative_names`, lines 360-369). `200 {"success":true,"data":[...]}` ordered by `glossary_id`.

Shared rule set `glossaryRules($glossaryId = null)` (verbatim, lines 372-385): `glossary_id` → `['required','string','max:20','regex:/^GL-\d+$/', 'unique:glossary,glossary_id[,{glossaryId},glossary_id]']`; `term` → `required|string|max:150`; `type` → `nullable|string|max:30`; `definition` → `nullable|string`; `alternative_names` → `nullable|string|max:255`.

**POST glossary** — `glossaryStore`, line 387 → `201 ... "Glossary term created"` (line 395). **PUT glossary/{glossaryId}** — `glossaryUpdate`, line 398 → `200 ... "Glossary term updated"` (line 407). **DELETE glossary/{glossaryId}** — `glossaryDestroy`, line 410 → `200 {"success":true,"message":"Glossary term deleted"}` (line 413). `404` on unknown id, `422` on validation. Note: deleting a glossary term is not blocked even if `GL-` codes reference it from existing condition logics (guard only runs at condition-logic write time).

### 5.6 Versions

**GET /api/threshold-config/versions** — `versionsIndex`, line 570. Filter: `threshold_id` (lines 573-575). `200 {"success":true,"data":[...]}` ordered by `version_id`.

**POST versions** — `versionsStore`, line 579. Validation (verbatim, lines 582-591): `threshold_id` → `required|string|max:20|regex:/^TH-\d+$/`; `old_value` → `nullable|numeric`; `new_value` → `nullable|numeric`; `changed_by` → `nullable|string|max:100`; `approved_by` → `nullable|string|max:100`; `change_reason` → `nullable|string`; `timestamp` → `nullable|date`; `version_number` → `nullable|integer`. `timestamp` defaults to `now()` when empty (lines 596-598). Success `201 {"success":true,"message":"Version record created","data":<row>}` (line 600). Allows manual insertion of audit rows (admin can fabricate history).

**PUT versions/{versionId}** — `versionsUpdate`, line 603. Same validation set (lines 607-616, `threshold_id` still `required`). `404`/`422`; success `200 ... "Version record updated"` (line 621). Audit rows are mutable.

**DELETE versions/{versionId}** — `versionsDestroy`, line 624. `404` or `200 {"success":true,"message":"Version record deleted"}` (line 627). Audit rows are deletable.

### 5.7 Stats

**GET /api/threshold-config/stats** — `stats`, line 630. No params. `200`:
```json
{"success":true,"data":{"business_rules":N,"condition_logics":N,"rule_threshold_mapping":N,"glossary":N,"thresholds":N,"versions":N,"domain_access":N}}
```
`domain_access` is `User::count()` — one matrix row per user, matching `domainAccessMatrix()` (comment at lines 641-643).

### 5.8 Domains & domain access

**GET /api/threshold-config/domains** — `domainsIndex`, line 648. Returns the distinct non-empty `thresholds.domain` values: `200 {"success":true,"data":["Domain A","Domain B",...]}` (lines 650-660).

**PUT /api/threshold-config/domains/rename** — `domainsRename`, line 663.
- Validation (verbatim, lines 665-668): `old_domain` → `required|string|max:100`; `new_domain` → `required|string|max:100`.
- Extra guards: `422 {"success":false,"message":"Domain values cannot be empty."}` after trim (lines 675-677); case-insensitive no-op → `200 {"success":true,"message":"No changes applied."}` (lines 678-680).
- Side effects (in `DB::transaction`, lines 682-686): bulk-updates `thresholds.domain` and `user_domain_access.domain` from old → new.
- Success: `200 {"success":true,"message":"Domain renamed","data":{"thresholds_updated":N,"user_domain_access_updated":N}}` (line 688).

**GET /api/threshold-config/domain-access** — `domainAccessIndex`, line 691. Query params: `format=matrix` delegates to the matrix handler (lines 693-695); `user_id` filters rows (lines 698-700). Returns raw `user_domain_access` rows ordered by user FK then domain: `200 {"success":true,"data":[...]}`. The user FK column is runtime-detected as `user` or `user_id` (`app/Models/UserDomainAccess.php:16-30`).

**GET /api/threshold-config/domain-access/matrix** — `domainAccessMatrix`, line 704. One row per user (all users, even with zero domains): `200 {"success":true,"data":[{"user_id","name","email","role","domains":[...sorted],"domainsText":"a, b" or "—"}]}` (lines 726-740).

**PUT /api/threshold-config/domain-access/{userId}** — `domainAccessReplace`, line 743.
- Validation (verbatim, lines 745-748): `domains` → `nullable|array`; `domains.*` → `string|max:100`.
- Side effects (in `DB::transaction`, lines 761-766): **deletes all** of the user's `user_domain_access` rows, then recreates one per trimmed/deduped domain. Sending `{"domains":[]}` revokes everything.
- Success: `200 {"success":true,"message":"Domain access updated","data":[<user's access rows ordered by domain>]}` (lines 768-772). `404` if user not found (line 760).

**POST /api/threshold-config/domain-access/{userId}** — `domainAccessAdd`, line 775.
- Validation (verbatim, lines 777-779): `domain` → `required|string|max:100`; plus `422 {"success":false,"message":"Domain cannot be empty."}` after trim (lines 785-787).
- Side effect: inserts the pivot row only if not already present (idempotent, lines 790-793).
- Success: `200 {"success":true,"message":"Domain added","data":[<rows>]}` (lines 795-799). `404` unknown user.

**DELETE /api/threshold-config/domain-access/{userId}/{domain}** — `domainAccessRemove`, line 802. `422 "Domain cannot be empty."` for a blank path segment (lines 804-807); deletes matching pivot rows; success `200 {"success":true,"message":"Domain removed","data":[<remaining rows>]}` (lines 812-816). `404` unknown user.

### 5.9 Export & bulk import

**GET /api/threshold-config/export-yaml** — `exportYaml`, line 819. Builds `{threshold_key: value}` for every threshold with a non-empty key and returns raw YAML: `200`, headers `Content-Type: text/yaml; charset=UTF-8`, `Content-Disposition: attachment; filename="rules_registry.yaml"` (lines 829-834). No side effects.

**GET /api/threshold-config/export-csv?tab=<tab>** — `exportCsv`, line 837.
- `tab` must be one of `business_rules`, `condition_logics`, `rule_threshold_mapping`, `glossary`, `thresholds`, `versions` (`bulkModelMap()`, lines 877-887); otherwise `422 {"success":false,"message":"Invalid tab."}` (lines 841-843).
- Dumps **every column** of the table (schema-derived via `Schema::getColumnListing`, line 848) for **every row**, ordered by PK, as CSV: `200`, `Content-Type: text/csv; charset=UTF-8`, `Content-Disposition: attachment; filename="<tab>.csv"` (lines 869-872). No side effects.

**POST /api/threshold-config/bulk-import/{tab}?mode=validate|commit&upsert=0|1** — `bulkImport`, line 1015.
- `{tab}` — same six values via `bulkSpec()` (lines 891-902); unknown → `422 "Invalid tab."` (lines 1017-1020).
- Validation (verbatim, line 1021): `file` → `required|file|max:5120`; failure message is customized: `422 {"success":false,"message":"Please upload a CSV file (max 5MB)."}` (lines 1022-1024).
- `mode` query param: anything other than `commit` means `validate` (dry-run, line 1026). `upsert` read via `$request->boolean('upsert')` (line 1027).
- CSV parsing (`parseCsvFile`, lines 971-1013): first row = header, UTF-8 BOM stripped, cells trimmed, blank cells → null, fully blank rows skipped.
- Guards: `422 "No data rows found in the file."` (lines 1033-1035); `422 "Too many rows (N). Limit is 1000 per upload."` (lines 1036-1038).
- Per-row processing (lines 1044-1103): code fields normalized per tab (`business_rules`: rule_id; `glossary`: glossary_id; `rule_threshold_mapping`: mapping_id/rule_id/threshold_id; `thresholds`: threshold_id; `condition_logics`: rule_id; `versions`: threshold_id — lines 893-900). For auto-PK tabs (`condition_logics`, `versions`) the PK column is stripped, so those tabs are **insert-only regardless of `upsert`**. Each row validated against the same rule sets as the single-row endpoints (`bulkRules`, lines 904-921; thresholds use `thresholdsBulkRules` lines 923-953 where `threshold_key` is `required` and unique-ignore keys off `threshold_id`; versions use `versionsBulkRules` lines 955-967). `condition_logics` rows also run the `unknownConditionCodes` guard (row error: `"Unknown code(s) in condition logic: <codes>"`, lines 1078-1087). Existing PK without `upsert` → row skipped with error `'<pk> "<val>" already exists — skipped (enable "update existing" to overwrite)'` (line 1096). Row errors are capped at 200 entries.
- Side effects: only in `mode=commit` — a single `DB::transaction` performing `create` for inserts and `where(pk)->update` for upserts (lines 1105-1116). **No version rows are written by bulk threshold updates** (unlike `thresholdsUpdate`).
- Success (both modes): `200 {"success":true,"data":{"total","valid","invalid","skipped","inserted","updated","errors":[{"row","message"}],"mode"}}` (lines 1040, 1118-1119).

---

## 6. Folder / file library endpoints (DEEP)

Controller: `app/Http/Controllers/Api/FolderFileController.php`; all storage logic in `app/Services/FolderFileService.php` (disk = Laravel `local` disk, i.e. `storage/app`, `FolderFileService.php:13-16`). Read endpoints are bearer-gated for any authenticated user (`routes/api.php:80-85`); write endpoints are bearer + admin (`routes/api.php:87-95`).

`{folder}` and `{managed_file}` are implicit route-model bindings on `App\Models\Folder` / `App\Models\ManagedFile` — unknown IDs yield a framework `404` before the controller runs. Every handler wraps work in try/catch; unexpected exceptions are logged (`folder_file_manager_failed`) and returned as `500 {"success":false,"message":<exception message>,"action":<handler name>}` (`FolderFileController.php:22-26`).

### 6.1 GET /api/folders/tree
- **Handler:** `FolderFileController@tree` — `FolderFileController.php:28`; service `getTree()` — `FolderFileService.php:272-275`.
- **Success:** `200 {"success":true,"data":[<root folders with nested allChildren + files>]}`.
- **Errors:** `500` shape above. No side effects.

### 6.2 GET /api/folders/{folder}
- **Handler:** `showFolder` — `FolderFileController.php:74`; service `getFolderContents()` — `FolderFileService.php:277-290`.
- **Success:** `200 {"success":true,"data":{"folder":<folder with children+files>,"breadcrumb":[{"id","name"},... root→leaf]}}`.
- **Errors:** `404` (binding), `500`.

### 6.3 GET /api/folders/{folder}/download-zip
- **Handler:** `downloadFolderZip` — `FolderFileController.php:37`; service `createFolderZipArchive()` — `FolderFileService.php:370-415`.
- **Success:** `200` binary ZIP download, name `<slug-of-folder-name>.zip` (fallback `folder-<id>.zip`), `Content-Type: application/zip`; temp file deleted after send (`FolderFileController.php:41-46`).
- **Logic:** walks the folder + all descendants (BFS, `folderAndDescendantIds`, service lines 292-308), adds every DB-registered file that exists on disk, sanitizes zip entry labels and dedupes case-insensitively as `name (2).ext` (service lines 310-368). Files missing on disk are silently skipped (service lines 393-399).
- **Errors:** `404 {"success":false,"message":"Folder missing on disk."}` or `"Invalid folder path."` (message matched on "missing"/"Invalid", controller lines 48-51); `500` for zip create/finalize failures (`"Could not create zip file."` / `"Could not finalize zip file."`, service lines 385-387, 410-413).
- **Side effects:** creates then deletes a temp zip in the system temp dir.

### 6.4 GET /api/files/{managed_file}/download
- **Handler:** `downloadFile` — `FolderFileController.php:56`; service `absolutePathForManagedFile()` — `FolderFileService.php:417-425`.
- **Success:** `200` binary download named from `managed_file.name` (fallback `filename`).
- **Errors:** `404 {"success":false,"message":"File missing on disk."}` (controller lines 66-69); `500` otherwise.
- **Side effects:** self-healing path resolution — if `file_path` is stale, the service tries `folder.path + filename` and persists the corrected `file_path` back to the row (`resolvedStorageRelativePath`, service lines 42-61).

### 6.5 GET /api/files/{managed_file}/content
- **Handler:** `fileContent` — `FolderFileController.php:154`; service `readTextPreview()` — `FolderFileService.php:427-444`.
- **Preview allowlist:** mime starting `text/`, or `application/json|xml|javascript|ecmascript|markdown`, `text/markdown`; otherwise extension in `md, markdown, txt, csv, json, xml, log` (service lines 429-437).
- **Success:** `200 {"success":true,"data":{"content":<full file text>,"mime_type","name"}}`.
- **Errors:** **`415`** `{"success":false,"message":"Preview is only available for plain-text-like files."}` (matched on "preview", controller lines 161-163); `404 "File missing on disk."` (lines 164-166); `500` otherwise.

### 6.6 POST /api/folders (admin)
- **Handler:** `storeFolder` — `FolderFileController.php:83`; service `createFolder()` — `FolderFileService.php:92-104`.
- **Validation (verbatim, line 86):** `name` → `required|string|max:255`; `parent_id` → `nullable|exists:folders,id`. `ValidationException` is re-thrown → framework `422` (lines 90-91).
- **Success:** `201 {"success":true,"data":<folder row>}`.
- **Side effects:** generates a slug unique within the parent (suffix `-2`, `-3`, ... on collision, service lines 63-90), creates the physical directory on the `local` disk, inserts a `folders` row `{name (trimmed), slug, path, parent_id}`.

### 6.7 PUT /api/folders/{folder}/rename (admin)
- **Handler:** `renameFolder` — `FolderFileController.php:97`; service `renameFolder()` — `FolderFileService.php:120-149`.
- **Validation (verbatim, line 100):** `name` → `required|string|max:255`.
- **Success:** `200 {"success":true,"data":<fresh folder row>}`.
- **Side effects:** computes a new unique slug/path; if the path changed, **moves the directory on disk**, rewrites `file_path` for every direct file, then recursively rewrites `path`/`file_path` for all descendant folders and files (`updateDescendantPaths`, service lines 106-118); finally updates the folder row.
- **Errors:** `422` validation; `500 {"success":false,"message":"Target path already exists on disk.","action":"renameFolder"}` when the destination exists (service lines 135-137).

### 6.8 DELETE /api/folders/{folder} (admin)
- **Handler:** `destroyFolder` — `FolderFileController.php:110`; service `deleteFolder()` — `FolderFileService.php:151-158`.
- **Success:** `200 {"success":true,"message":"Folder deleted"}`.
- **Side effects:** deletes the physical directory tree (`deleteDirectory`) then deletes the `folders` row. **Child-folder and `managed_files` DB rows are not explicitly cascaded in code** — cleanup depends on DB FK constraints; on-disk contents are removed regardless.

### 6.9 POST /api/folders/{folder}/files (admin)
- **Handler:** `uploadFile` — `FolderFileController.php:120`; service `uploadFile()` — `FolderFileService.php:160-191`.
- **Validation (verbatim, line 123):** `file` → `required|file`; plus `422 {"success":false,"message":"Invalid upload"}` if the upload object is invalid (lines 125-127). **No max-size or mime restriction in code** (server limits apply).
- **Success:** `201 {"success":true,"data":<managed_file row>}`.
- **Side effects:** if a file with the same display name already exists in the folder, this becomes a **reupload of that row** (old blob deleted, row updated — service lines 164-172). Otherwise stores the blob as `<slug-base>-<unix time>.<ext>` under the folder's path and inserts a `managed_files` row `{folder_id, name (original client name), filename, file_path, mime_type, extension, size}`.

### 6.10 POST /api/files/{managed_file}/reupload (admin)
- **Handler:** `reuploadFile` — `FolderFileController.php:137`; service `reuploadManagedFile()` — `FolderFileService.php:193-219`.
- **Validation:** `file` → `required|file` (line 140); `422 "Invalid upload"` as above.
- **Success:** `200 {"success":true,"data":<fresh row>}`.
- **Side effects:** deletes the old blob from disk (if found), writes the new blob with a fresh timestamped filename, updates the row in place (name, filename, file_path, mime_type, extension, size) — same DB id, so links keep working.

### 6.11 PUT /api/files/{managed_file}/rename (admin)
- **Handler:** `renameFile` — `FolderFileController.php:171`; service `renameFile()` — `FolderFileService.php:221-246`.
- **Validation (verbatim, line 174):** `name` → `required|string|max:255`.
- **Success:** `200 {"success":true,"data":<fresh row>}`.
- **Side effects:** keeps the original extension (appends it to the display name if missing), moves the blob to a new timestamped filename, updates `name`/`filename`/`file_path`.
- **Errors:** `422`; `500 {"success":false,"message":"File missing on disk.","action":"renameFile"}` if the source blob is gone (service lines 236-238).

### 6.12 PUT /api/files/{managed_file}/move (admin)
- **Handler:** `moveFile` — `FolderFileController.php:184`; service `moveFile()` — `FolderFileService.php:248-261`.
- **Validation (verbatim, line 187):** `folder_id` → `required|exists:folders,id`.
- **Success:** `200 {"success":true,"data":<fresh row>}`. Moving to the same folder is a no-op (service lines 250-252).
- **Side effects:** moves the blob to `<target folder path>/<filename>`, updates `folder_id` and `file_path`.
- **Errors:** `422`; `500 "File missing on disk."` if the source blob is gone.

### 6.13 DELETE /api/files/{managed_file} (admin)
- **Handler:** `destroyFile` — `FolderFileController.php:198`; service `deleteFile()` — `FolderFileService.php:263-270`.
- **Success:** `200 {"success":true,"message":"File deleted"}`.
- **Side effects:** deletes the blob from disk (if present) then deletes the `managed_files` row.

---

## 7. Shared-repo modules (BRIEF — NOT BLOS scope)

| Method + URL | Handler | Note |
|---|---|---|
| GET /api/warehouse-location-wise-stock-update | `Inventory\StockController@WarehouseLocationWiseStockUpdate` (`app/Http/Controllers/Inventory/StockController.php:23`) | Shared-repo module — NOT BLOS scope. **Public GET that performs stock-sync writes** across UK/Germany/US locations, chunking `InvProducts`. |
| GET/POST /api/products*, POST /api/products/{id}/image | `Api\ProductController` | Shared-repo module — NOT BLOS scope. **Controller class does not exist → 500 at dispatch** (6 routes, `routes/api.php:28-29,99-102`). |
| GET/POST/PUT /api/sales* | `Api\SaleController` | Shared-repo module — NOT BLOS scope. Controller missing → 500 (4 routes, `routes/api.php:31-33,108`). |
| apiResource /api/categories + POST /api/categories/{id}/image | `Api\CategoryController` | Shared-repo module — NOT BLOS scope. Controller missing → 500 (6 routes, `routes/api.php:97-98`). |
| GET/PUT /api/inventory* | `Api\InventoryController` | Shared-repo module — NOT BLOS scope. Controller missing → 500 (2 routes, `routes/api.php:105-106`). |
| GET /api/reports/daily, /monthly, /top-products | `Api\ReportController` | Shared-repo module — NOT BLOS scope. Controller missing → 500 (3 routes, `routes/api.php:110-112`). |
| DELETE /api/images/{id} | `Api\ImageController` | Shared-repo module — NOT BLOS scope. Controller missing → 500 (1 route, `routes/api.php:103`). |
| GET /testData (web route) | `Ppc\TestingController@testData` (`app/Http/Controllers/Ppc/TestingController.php:33`) | Shared-repo module — NOT BLOS scope. Public web route triggering the Amazon PPC → ETL performance-data sync. |

---

## 8. Notable findings for reviewers

1. **Public admin creation:** `POST /api/add-new-users` is unauthenticated and accepts `role=admin` (`routes/api.php:16`; `AuthController.php:104`). Anyone who can reach the API can mint an admin account and unlock every admin endpoint.
2. **Public user-table dump:** `GET /api/test` returns `User::all()` with no auth (`routes/api.php:19`; `AuthController.php:82-91`). Password hash and token are hidden by the model, everything else leaks.
3. **22 dead routes:** six controllers imported in `routes/api.php:5-11` (`ProductController`, `CategoryController`, `InventoryController`, `SaleController`, `ReportController`, `ImageController`) do not exist in the repo; all their routes 500 at dispatch. Only `UserController`, `ThresholdConfigurationController`, `FolderFileController` exist under `app/Http/Controllers/Api/`.
4. **Public write via GET:** `/api/warehouse-location-wise-stock-update` (stock sync) and web `/testData` (PPC ETL) are unauthenticated GETs with heavy side effects.
5. **Threshold update is not admin-only:** any bearer user with matching domain access can `PUT thresholds/{id}` — by design (domain-scoped), but reviewers should confirm intent; `change_reason` is temporarily optional (`ThresholdConfigurationController.php:513-516`).
6. **Audit history is mutable:** admin can create/update/delete `threshold_versions` rows directly (sections 5.6), and threshold deletes cascade-delete their whole version history (`ThresholdConfigurationController.php:562-566`). Bulk threshold imports bypass version logging entirely.
7. **Plain-text, non-expiring tokens:** 32-char tokens stored unhashed in `user.token`; one active session per user; no expiry (`AuthController.php:55-57`; `CheckAuthMiddleware.php:15-26`).

---

## 9. Coverage statement

- **Total routes registered in `routes/api.php`: 80** (counting the `apiResource('categories', ...)` at `routes/api.php:97` as its 5 registered routes, with `PUT|PATCH` update counted once).
- **Documented DEEP: 57** — auth 6 (rows 1-4, 6-7) + threshold-config 35 (rows 13-47) + folder/file library 13 (rows 48-60) + users 3 (rows 78-80).
- **Marked shared/brief: 23** — stock-sync 1 (row 5) + products 6 (rows 8-9, 67-70) + sales 4 (rows 10-12, 74) + categories 6 (rows 61-66) + images 1 (row 71) + inventory 2 (rows 72-73) + reports 3 (rows 75-77).
- **57 + 23 = 80 — nothing skipped.** Additionally, both `routes/web.php` routes (2) are noted in sections 2 and 7 (the PPC `/testData` route and the SPA catch-all); they are outside the api.php count.


---

# PART F — UI REFERENCE

---

# UI Reference — Ledsone Centralizer Account SPA (Vue 2)

| Field | Value |
|---|---|
| **Date** | 2026-07-07 |
| **Deliverable** | REQ-04-D07 |
| **Project** | PRJ-2026-003_blos-project-sentinel |
| **Status** | DRAFT |
| **Source root** | `resources/js/Account/` (repo: ledsone-centralizer, read-only) |
| **Evidence convention** | Every claim cites `file:line` of the component file under `resources/js/Account/` unless another path is given |

This document describes the complete user-facing behaviour of the Account single-page application: routes, guards, layout, session handling, and each of the five pages (Dashboard, Threshold Configurator, Business OS / Oil Configurator, Rule Builder, File Manager) plus the Login page and shared shell components.

---

## 1. Route / component summary

| Route (history mode) | Route name | Component | Guard(s) | Full-bleed main? | Notes |
|---|---|---|---|---|---|
| `/` | `Dashboard` | `Pages/Dashboard.vue` | `requiresAuth` (Router.js:16) | Yes (App.vue:43) | Landing hub, role-aware copy |
| `/threshold-configurator` | `ThresholdConfigurator` | `Pages/ThresholdConfigurator.vue` | `requiresAuth` (Router.js:17) | Yes (App.vue:43) | 7-tab data grid; non-admins see thresholds tab only |
| `/oil-configurator` | `OilConfigurator` | `Pages/OilConfigurator.vue` | `requiresAuth` (Router.js:18) | Yes (App.vue:43) | "Business OS" inline threshold-value editor + YAML export |
| `/rule-builder` | `RuleBuilder` | `Pages/RuleBuilder.vue` | `requiresAuth` **+ `requiresAdmin`** (Router.js:19) | No | Visual condition-logic builder (admin only) |
| `/file-manager` | `FileManager` | `Pages/FileManager.vue` | `requiresAuth` (Router.js:20) | Yes (App.vue:43) | Central file library; admin full CRUD, others read/download |
| `/markdown-manager` | — | redirect → `/file-manager` | — | — | Legacy alias (Router.js:21) |
| `/login` | `Login` | `Pages/auth/Login.vue` | `requiresGuest` (Router.js:22) | Layout hidden entirely (App.vue:38-41) | Email/password + remember-me |
| `/register` | — | redirect → `/login` | — | — | Router.js:23 |
| `*` | — | redirect → `/` | — | — | Catch-all (Router.js:24) |

Shared shell: `App.vue` (layout + boot loader), `Pages/Loading.vue` (boot splash), `Pages/includes/Header.vue` (top nav), `components/AccountRouteLoader.vue` (per-page skeleton loader). Rule Builder engine: `components/ruleLogic.js` + `components/RuleNode.vue`. Session plumbing: `userSession.js`.

---

## 2. Bootstrap & shell

### 2.1 Account.js — entry point
- Imports the shared Vue instance from `../app`, mounts `App.vue` on `#app` with the router and Vuex store (Account.js:1-14). Template is `<App class="h-100"/>` (Account.js:13).

### 2.2 Store.js / Components.js (Account-local)
- `Account/Store.js` creates a Vuex store with a single module `Store` (the app-level `resources/js/Store.js`) and installs `Account/Components.js` (Store.js:6-16). `Components.js` is an empty plugin — its whole body is commented out (Components.js:6-42). Not applicable to users.
- The app-level Vuex module (outside Account/, `resources/js/Store.js`) provides the global `this.api({url, action, body, success, error})` helper used by Login and Loading: it prefixes `'/api'` onto the URL (resources/js/Store.js:60), maps `action: 'create'`→POST / `'update'`→PUT / `'delete'`→DELETE (resources/js/Store.js:50-55), and on HTTP 401/419/403 it calls `clearAllAuth()` and hard-redirects to `/login` (resources/js/Store.js:14-24). This is the global "session expired" behaviour for all `this.api` calls.

### 2.3 Pages.vue
- A two-line pass-through: `<template><router-view/></template>` (Pages.vue:1-3). Not referenced by the live app (App.vue renders `<router-view>` itself).

### 2.4 App.vue — layout & isFullBleedMain
- On first mount a boot splash is shown: `isLoading: true` renders `<Loading @loaded="handleLoaded"/>`; when Loading emits `loaded`, the app shell appears (App.vue:3, 32-35, 50-52).
- `showLayout` hides the entire chrome (Header + `<main>`) on the Login route: `return name !== 'Login'` (App.vue:38-41). Login renders bare inside a route transition (App.vue:13-17).
- `isFullBleedMain` — `true` for Dashboard, ThresholdConfigurator, FileManager, OilConfigurator (App.vue:42-44). When true, `<main class="app-main">` gets `app-main--fullbleed` (App.vue:7), which strips the default padding/max-width so those pages own the full viewport (App.vue:131-136). RuleBuilder is **not** in the list, so it renders inside the padded `app-main` container (padding defined at App.vue:123-129).
- Route transitions use a fade/translate pair (`app-route`) keyed by `$route.path` (App.vue:8-16, 45-47, 144-160), with reduced-motion fallbacks (App.vue:162-177).
- App-wide CSS design tokens (colors, radii, nav height 72px, easing curves) are declared on `:root` (App.vue:64-107).

### 2.5 userSession.js — token storage & header injection
- **Reactive tick**: `sessionProfileTick = Vue.observable({ n: 0 })` is bumped whenever the stored user changes so components' computed `isAdmin`/`userName` re-run (localStorage is not reactive) (userSession.js:5; consumed via `void sessionProfileTick.n` in Header.vue:159, Dashboard.vue:171, ThresholdConfigurator.vue:750, FileManager.vue:705).
- **Auth bucket**: `lc_auth_bucket` records whether login wrote to `localStorage` ("remember me") or `sessionStorage`, so the token and cached user always resolve from the *same* storage (userSession.js:7-25). `userAuthStorage()` resolves the active storage with fallbacks — prefers the bucket if it still holds a token, clears stale bucket markers, prefers whichever storage has *both* `auth` and `user`, then any storage with `auth` (userSession.js:31-64).
- **`getStoredUserJson()`** reads the `user` JSON strictly from the same storage as the active token — deliberately never merged across storages to avoid mixing one user's token with another's cached role (userSession.js:66-74).
- **`authHeaders()`** returns `{ Accept: 'application/json', Authorization: 'Bearer <token>' }` (userSession.js:76-82). Every Account-app axios call spreads this into its headers (e.g. ThresholdConfigurator.vue:1188, RuleBuilder.vue:284, OilConfigurator.vue:431, FileManager.vue:763-765).
- **`refreshSessionUser()`** — GET `/api/me`; on success re-writes `user` into the active storage, wipes the `user` copy in the other storage, backfills the bucket marker, and bumps the tick (userSession.js:95-122). On HTTP 401/403/419 it calls `clearAllAuth()` and returns the string `'expired'` (userSession.js:129-132), which the router treats as logout (see 2.6). Other failures log to console and return `false`.
- **`clearAllAuth()`** removes `auth` + `user` from both storages and the bucket key (userSession.js:86-92).

### 2.6 Router.js — guards (full detail)
- **`beforeEach`** (Router.js:55-103):
  1. Token check: `localStorage.getItem('auth') || sessionStorage.getItem('auth')` (Router.js:56).
  2. For `requiresAuth` routes: unauthenticated users are redirected to `/login?redirect=<fullPath>` (Router.js:58-62).
  3. Authenticated users then get a **profile refresh on every navigation**: `await refreshSessionUser()`; if it returns `'expired'` the user is sent to `/login?redirect=…` (Router.js:63-68). A non-fatal failure only logs a warning that the UI may show an old role (Router.js:69-71).
  4. For `requiresAdmin` routes (Rule Builder only): the stored user JSON is parsed and `role` compared case-insensitively to `'admin'`; anything else (including parse errors) redirects to `/` with a console warning (Router.js:75-90). So a non-admin typing `/rule-builder` lands on the Dashboard.
  5. `requiresGuest` (Login): an authenticated user visiting `/login` is bounced to `/` (Router.js:94-99).
- **`afterEach`** (Router.js:28-49): logs FileManager navigations (Router.js:29-31); smooth-scrolls to top on every route change except same-path or Login, honouring `prefers-reduced-motion` (Router.js:34-48).
- **`onError`** logs navigation/runtime errors (Router.js:51-53).

### 2.7 Pages/Loading.vue — boot splash
- Full-screen dark teal loader with rings, particles, "Ledsone centralizer / Loading" text (Loading.vue:2-37; styles 96-378).
- On `created` it builds 18 particle styles and calls `loadConfigurations()` (Loading.vue:56-67): `this.api({ url: '/configurations', state: 'Configss', … })` → GET `/api/configurations`. If the response carries `data.token`, it is written into the active auth storage and `refreshSessionUser()` re-fetches the profile (Loading.vue:74-91) — i.e. the backend can rotate/refresh the bearer token at boot.
- On `mounted` it emits `loaded` after `duration` (default **1200 ms**), which is what dismisses the splash (Loading.vue:45-50, 68-72). The splash is time-based, not data-based.

### 2.8 Pages/includes/Header.vue — top navigation
- **Structure**: sticky header (Header.vue:272-280) with logo (LC mark + "Ledsone centralizer / Operations hub", Header.vue:5-15), a desktop pill nav, a mobile hamburger, a live page chip and the user menu.
- **Nav links** (desktop Header.vue:17-23; mobile duplicate Header.vue:89-132):
  - Dashboard `/`
  - "Threshold config" `/threshold-configurator` — tooltip for non-admins: "Thresholds for your assigned domains" (Header.vue:19, 96)
  - "Business OS" `/oil-configurator` — tooltip "Business OS — threshold values by domain and YAML export" (Header.vue:20)
  - **"Rule Builder" `/rule-builder` rendered only `v-if="isAdmin"`** (Header.vue:21, 111-121) — non-admins never see the link (and the route guard blocks direct URL entry, Router.js:75-90)
  - "Files" `/file-manager` — tooltip "Central file library — browse and download; admins manage uploads" (Header.vue:22)
- **Role display**: `isAdmin` / `userName` / `roleLabel` are computed from `getStoredUserJson()` with the reactivity tick (Header.vue:158-201). `roleLabel` maps `admin`→"Admin", `domain_owner`→"Domain owner", `cashier`→"Cashier", otherwise Title-Cases the snake_case role (Header.vue:185-201).
- **Page chip**: `pageTitle` maps route name → friendly label (Dashboard, Threshold configurator, Business OS configurator, Rule Builder, Central file library) shown with a green dot and transition (Header.vue:39-44, 148-157). Hidden below 1024px (Header.vue:932-935).
- **User menu**: avatar initial + name + role pill; clicking toggles a dropdown with a header block and one action, **Sign out** (Header.vue:46-66). `handleLogout()` clears the bucket and both storages' `auth`/`user`, then routes to `/login` (Header.vue:232-240). Outside-click and Escape both close the menus (Header.vue:243-253); on tab re-focus (`visibilitychange` → visible) the profile is silently re-fetched via `refreshSessionUser()` (Header.vue:254-259).
- **Mobile hamburger** (`≤768px`): three-line toggle button with `aria-expanded`/`aria-controls` (Header.vue:24-37; shown at Header.vue:956-963). Opens a full-screen `role="dialog"` sheet with backdrop button, "Menu" head, ✕ close, current-page context line, and the same nav links (each `@click.native="closeMobileNav"`) (Header.vue:71-135). While open, `<html>`/`<body>` scrolling is locked (watcher Header.vue:204-214). Any route change closes both menus (Header.vue:215-218). Opening the user menu closes the mobile nav and vice versa (Header.vue:221-231).

### 2.9 components/AccountRouteLoader.vue — page skeleton
- Presentational loader with two variants selected by prop `variant`: `'shell'` — full-page skeleton with fake topbar, sidebar (7 nav bars), hero/save/cards shimmer plus caption title/subtitle (AccountRouteLoader.vue:3-26); `'card'` — centered orbit spinner card (AccountRouteLoader.vue:27-41). Props: `variant`, `title`, `subtitle` (AccountRouteLoader.vue:48-52). Used by RuleBuilder (`shell`, RuleBuilder.vue:3), OilConfigurator (`shell`, OilConfigurator.vue:3-8), ThresholdConfigurator (`card`, ThresholdConfigurator.vue:297-302). Honors reduced motion (AccountRouteLoader.vue:389-406).

### 2.10 Pages/includes/Sidebar.vue and TopBar.vue — orphaned
- `Sidebar.vue` is a dark left sidebar with only a Dashboard link, user name and Sign out (Sidebar.vue:2-19, logout at 40-47). `TopBar.vue` is a slim page-title bar (TopBar.vue:3-15, 29-41). **Neither is imported by any live component** (grep of `resources/js` finds no consumer) — they are legacy leftovers; the live shell is `Header.vue`. Documented brief for completeness.

---

## 3. Pages/auth/Login.vue

**Purpose**: authenticate and choose token persistence. Route `/login`, guest-only (Router.js:22, 94-99). Rendered without Header (App.vue:38-41).

**UI regions**: animated gradient/orb background (Login.vue:3-7), glass card with LC logo cluster, "Welcome back" title, "Secure session · Encrypted credentials" kicker (Login.vue:9-24), and the form (Login.vue:28-93).

**Fields & client-side validation**
- Email: `type="email" required autocomplete="email"` (Login.vue:35-43).
- Password: `required autocomplete="current-password"`, with a show/hide eye toggle (`passwordVisible`, aria-pressed) (Login.vue:56-74).
- "Remember me" checkbox bound to `form.rememberMe` (Login.vue:78-84).
- "Forgot password?" is a dead link (`href="#"`, Login.vue:50) — no reset flow exists in this SPA.
- Submit button disabled while `loading`, showing spinner + "Signing in…" (Login.vue:86-92).

**Submit flow — `handleLogin()`** (Login.vue:116-171)
- Calls `this.api({ url: '/login', action: 'create', body: { email, password } })` → **POST `/api/login`** (Login.vue:119-125; `/api` prefix + POST mapping in resources/js/Store.js:53, 60).
- On success it tolerates both `{token,user}` and `{data:{token,user}}` shapes (Login.vue:130-133). Storage choice: `rememberMe ? localStorage : sessionStorage` (Login.vue:139); writes `auth` (+ `user` if present), wipes the other storage, and calls `setAuthBucket('local'|'session')` (Login.vue:140-152). Bumps `sessionProfileTick` and runs `refreshSessionUser()` before redirecting to `$route.query.redirect || '/'` (Login.vue:134, 153-157).
- If the response has no token it still navigates to the redirect target (Login.vue:135-138) — relying on the guard to bounce back if truly unauthenticated.
- On error: flattens Laravel `errors` bag into a browser `alert()`, else alerts `message` or a generic failure (Login.vue:159-169).

---

## 4. Pages/Dashboard.vue

**Purpose**: role-aware landing hub with links into the three main modules. Route `/`, auth-only (Router.js:16). No API calls of its own — everything is computed from the stored user.

**Regions**
- **Hero**: "Welcome back, {{ userName }}" with gradient accent (Dashboard.vue:18-21); lead text differs by role — admin: "Manage thresholds, Business OS configuration, and the central file library…"; non-admin: "Access thresholds and Business OS for your assigned domains, and browse the shared file library." (Dashboard.vue:22-27). Chips: role label (admin-styled when admin) + "Live workspace" (Dashboard.vue:28-34).
- **Session panel** (right aside): animated bars, "Signed in" name, today's date (`todayIso`/`todayShort`, Dashboard.vue:208-217), "All systems operational" status (Dashboard.vue:37-62) — decorative, not live telemetry.
- **Metrics strip** (4 cards, computed `metrics` Dashboard.vue:218-225): "3 Workspace tools"; "Access level" = roleLabel; "File library" = **Full** (admin) vs **Read-only** (non-admin, amber tone); "Threshold scope" = **Unrestricted** (admin) vs **Domain-scoped**.
- **Non-admin notice** (`v-if="!isAdmin"`, Dashboard.vue:76-87): amber banner "Your access as {{ roleLabel }}" explaining the file library is read-only (browse/preview/download only; uploads need an admin) and thresholds/Business OS stay scoped to their domains.
- **Workspace tools** section with an "Administrator" / "Member access" badge (Dashboard.vue:97-99) and three router-link cards:
  - *Threshold configurator* → `/threshold-configurator`; description differs by role (admin: "…business rules, mappings, and versions", non-admin: "…domains assigned to your account") (Dashboard.vue:103-118).
  - *Business OS configurator* → `/oil-configurator`; tag "OIL v5"; "Edit OIL margin bands, channel policies, KPI levels… Exports rules_registry.yaml." (Dashboard.vue:120-134).
  - *Central file library* → `/file-manager`; tag **"Library"** (admin) vs **"Read-only"** (non-admin), card tinted emerald vs amber, and role-specific descriptions (Dashboard.vue:136-152).
- There is **no Rule Builder card** on the dashboard — admin reaches it via the Header link or deep links from the Threshold Configurator.

**Role logic**: `userName` / `isAdmin` / `roleLabel` parse `getStoredUserJson()` with the tick (Dashboard.vue:169-207); role `admin` compared case-insensitively (Dashboard.vue:185-186).

---

## 5. Pages/ThresholdConfigurator.vue

**Purpose**: the master data grid for the whole BLOS threshold configuration schema — 7 tabs mapped 1:1 to DB tables, with admin CRUD, CSV/YAML export, CSV bulk import, and a user↔domain access console. Route `/threshold-configurator`, auth-only (Router.js:17), full-bleed (App.vue:43).

### 5.1 Tabs & role gating
- Tabs defined at ThresholdConfigurator.vue:700-708: `business_rules` (◇), `condition_logics` (◎, "view here; Add/Edit open the Rule Builder"), `glossary` (📖), `rule_threshold_mapping` (⛓), `thresholds` (◆, default `activeTab` line 709), `domain_access` (⊕, label `user_domain_access`), `versions` (◷, label `threshold_versions`, "Audit trail of value changes").
- **`visibleTabs`: non-admins see only the `thresholds` tab** (ThresholdConfigurator.vue:761-764); `switchTab` also force-resets non-admins to `thresholds` (ThresholdConfigurator.vue:1244-1251). So the entire multi-tab surface (rules, logic, glossary, mappings, access, versions) is admin-only UI.
- Tab endpoints (`pathForTab`, ThresholdConfigurator.vue:1214-1217): GET `/api/threshold-config/thresholds`, `/business-rules`, `/condition-logics`, `/glossary`, `/rule-threshold-mappings`, `/domain-access`, `/versions`.
- Tab counts strip: clickable stat pills per tab (ThresholdConfigurator.vue:106-119); counts come from GET `/api/threshold-config/stats` — **admin only**, non-admins skip the call (ThresholdConfigurator.vue:1202-1213).
- **Domain scoping (non-admin)**: the server returns only thresholds whose `domain` matches the user's `domain` field / `user_domain_access` rows. When a non-admin gets zero rows the page shows an explanatory hint block naming `thresholds.domain` and `user_domain_access` and telling them to ask an admin (ThresholdConfigurator.vue:184-188), plus a console warning (ThresholdConfigurator.vue:1232-1234). A softer hint appears when rows exist but filters exclude them all (ThresholdConfigurator.vue:188).

### 5.2 Layout & navigation
- Left sidebar "Sections" with icon, label (snake_case prettified by `formatNavLabel`, ThresholdConfigurator.vue:846-850) and per-tab count (ThresholdConfigurator.vue:19-39). On mobile a ☰ button opens a slide-in drawer with the same items (ThresholdConfigurator.vue:13-18, 41-68).
- Topbar hero: breadcrumb "Threshold suite / <tab>", title, "In view" chip = `filtered.length`, plus a "Loaded" chip when a filter/search is active and hides rows (ThresholdConfigurator.vue:70-93; `tabFilterActive` 775-782).

### 5.3 Toolbar: search, filters, mobile pickers
- Free-text search box filters across *all* fields of a row, case-insensitive (ThresholdConfigurator.vue:121, 783-788).
- Per-tab filters (`filtered` computed, ThresholdConfigurator.vue:783-802):
  - thresholds: domain (options from admin catalog or distinct row values, `domainOptions` 820-827), status (active/inactive), type (common/specific) (ThresholdConfigurator.vue:122-151).
  - domain_access: role dropdown (distinct roles, 815-819), "No domains assigned" checkbox, Reload button (ThresholdConfigurator.vue:152-168).
  - condition_logics: stage (initial/restore/kill) (ThresholdConfigurator.vue:169-182).
- On narrow screens each `<select>` is replaced by a button that opens a searchable picker panel (`openPicker`/`choosePicker`, template 128-201, methods 1151-1186).

### 5.4 Table rendering
- One `<thead>` variant per tab with literal DB column names (thresholds 25 cols incl. approver/management_approval, ThresholdConfigurator.vue:306-326) and matching row templates (ThresholdConfigurator.vue:333-428). Status rendered as ok/off badge (355, 366, 386); versions tab colors `old_value` red / `new_value` green (419-420). Colspan map for the "No records" row at 828-831.
- Row actions: **Edit** + **Delete** on most tabs (e.g. 359, 370, 406, 426); `rule_threshold_mapping` rows have Delete only (398); `domain_access` rows have a single primary **Edit** (414). On `condition_logics`, Edit does *not* open the modal — it deep-links to the Rule Builder (see 5.7).

### 5.5 Header actions (all admin-only)
- **Export YAML** — only on the thresholds tab (ThresholdConfigurator.vue:95): GET `/api/threshold-config/export-yaml` with `Bearer` headers, `responseType: 'blob'`, saved as `rules_registry.yaml` (ThresholdConfigurator.vue:1061-1074).
- **Export CSV** — every tab except domain_access (line 96): GET `/api/threshold-config/export-csv?tab=<tab>` → `<tab>.csv` (1075-1089). Both exports run `verifyExportBlob` which detects HTML/JSON masquerading as a file and toasts a precise diagnostic (e.g. "Download is a web page… use Export here so the Bearer token is sent") (1038-1060).
- **⤓ Bulk upload** — every tab except domain_access (line 97); see 5.8.
- **Add new** — becomes **"New in Rule Builder"** on condition_logics (ThresholdConfigurator.vue:98-101).

### 5.6 Add/Edit modal (per tab)
- Opened by `openAdd()` (1342-1353) / `openEdit(r)` (1401-1410). Edit deep-copies the row, records `editPk` via `deleteIdForRow`, and normalizes date/datetime strings for the native inputs (`normalizeFormDates`, 1411-1429).
- **Auto-generated primary keys with a lock**: for thresholds/business_rules/mappings/glossary the ID field (`TH-`, `BL-`, `MAP-`, `GL-` prefixes; `codeConfigForTab` 870-878) is prefilled with the next code (`nextCodeForActiveTab` scans existing rows for the max numeric suffix, 879-894) and rendered **disabled** with a "🔒 Auto · Edit" unlock button; clicking it sets `pkUnlocked` and shows "✎ editing manually" (template e.g. 492, 519, 562, 597). A live hint validates format (`^PREFIX\d+$`) and duplicates: muted "Auto-generated next ID…", warning "Wrong format…", "⚠ TH-00X already exists…", or "✓ … is available." (`pkHint`, 1354-1367). In edit mode the PK is always disabled (same lines, `:disabled="modal.mode === 'edit' …"`).
- **Searchable combo pickers** for foreign keys `rule_id` and `threshold_id` (condition_logics, mapping, versions forms): button opens a panel with search + options `ID — label` fed from `refRules`/`refThresholds`, loaded once for admins from business-rules and thresholds endpoints (`loadRefLists` 855-869; combo methods 895-920; templates 530-544, 563-592, 605-619). A click-away scrim closes it (490).
- **`change_reason` field** on the thresholds form, labelled "why — saved to history … Logged to threshold_versions when the value changes" (ThresholdConfigurator.vue:512). **Note**: the `canSave` computed currently returns `true` whenever the modal is open and not saving — a comment marks that the former "change_reason ≥ 10 chars required for threshold edits" rule is temporarily disabled ("TEMP: change_reason is not required for threshold edits right now. To restore: re-add the < 10 char check", ThresholdConfigurator.vue:832-838). So Save is only disabled while a save is in flight.
- **Save** (`saveForm`, 1515-1571): in add mode the PK is uppercased/despaced, regex- and duplicate-validated with toasts on failure (1519-1532); empty/null fields are stripped (`cleanPayload` 1492-1499) and legacy camelCase PK aliases removed on create (`stripPrimaryKeysOnCreate` 1500-1514). POST `/api/threshold-config/<table>` (add) or PUT `/api/threshold-config/<table>/<pk>` (edit) (1534-1552). Versions `timestamp` converts `T`→space (1548-1550). Success closes the modal, toasts, reloads the tab and refreshes ref lists (1553-1557); Laravel `errors` bags are flattened into the toast (1562-1566).

### 5.7 Condition-logics hand-off to Rule Builder
- `openAdd()` on condition_logics calls `goToRuleBuilder()` (1344-1345); `openEdit(r)` calls `goToRuleBuilder(r.rule_id, r.stage)` (1401-1403), pushing `{ name: 'RuleBuilder', query: { rule, stage } }` (1395-1400). Comments state condition logic is "built visually in the Rule Builder, never typed here" (1344, 1402). (A raw condition_logics form still exists in the modal template at 528-560 for completeness, but neither button reaches it.)

### 5.8 Bulk upload modal (admin)
- Opened by `openBulk()` (fresh state, 1090-1092). Modal (447-482) walks three steps: 1) "Download the template" (the current tab's CSV export doubles as template, link at 455); 2) edit in Excel, keep header row, IDs blank only where auto-generated (condition_logics, versions) (456); 3) choose file and **Check file** before anything is saved (457).
- File input accepts `.csv` (460); "Update existing rows (otherwise duplicates are skipped)" checkbox sets `upsert` (461).
- **Check file** → `bulkSend('validate')`, **Import N rows** → `bulkSend('commit')`: POST `/api/threshold-config/bulk-import/<tab>` as multipart with `?mode=validate|commit&upsert=0|1` (1101-1130). The result panel shows pills — "N ready", "N errors", "N skipped", "N added · N updated" (commit), "N total rows" — and a per-row error list "Row X: message" (463-474). The **Import** button stays disabled until a validation result exists with `valid > 0` (479); Cancel closes without side effects (477). Commit success toasts "N added · N updated" and reloads the tab (1116-1121).

### 5.9 Delete confirmation
- Delete buttons call `askDelete(r)` → small confirm modal "Delete record? / This cannot be undone." with Cancel / Delete (437-446, 1459-1461). Confirm runs DELETE `/api/threshold-config/<table>/<id>` and reloads on success (`doDelete`, 1471-1491). domain_access rows are explicitly excluded from delete (1472).

### 5.10 Domain access console (admin-only tab)
- Only rendered `v-if="isAdmin && activeTab === 'domain_access'"` (202). Two admin cards above the user matrix table:
  - **Domain access** — step 1 pick a user (`admin.users` select, 216-225; changing it loads current assignments via GET `/api/threshold-config/domain-access?user_id=<id>`, `loadAdminAccess` 942-955); step 2 assign domains: "Choose from list" opens a multi-select picker over the domain catalog (GET `/api/threshold-config/domains`, `loadAdminDomains` 931-941; picker 243-258), "Reload catalog", a **custom domain** free-text add (236-242, `addCustomDomain` 976-982), chips with ✕ remove (259-268), and **Save access** → PUT `/api/threshold-config/domain-access/<userId>` with `{domains: [...]}` (`saveAdminAccess` 983-999). Callout: "Account `domain` is always included; this adds *extra* domains only." (210-213).
  - **Rename domain** — old-domain select + new-name input + button ("Updates thresholds and user assignments."); PUT `/api/threshold-config/domains/rename` `{old_domain, new_domain}`, then reloads catalog, tab and current user's access (`renameDomain` 273-294, 1000-1021). Button disabled until both fields are set (291).
- The tab's table is a user matrix (user_id, name, email, role, domains) loaded by `loadDomainAccessTab`: GET `/api/threshold-config/domain-access?format=matrix` with a fallback to `/domain-access/matrix`, with specific deployment-hint error strings surfaced in a red alert (`domainAccessLoadError`, 296, 1252-1299). Per-row **Edit** opens a modal with domain search, custom add, checklist picker and chips, saved via the same PUT (635-686, 1300-1341).

### 5.11 State that matters to users
- Switching tabs resets search and filters (`loadTab` clears them, 1218-1221).
- Loading state shows AccountRouteLoader card "Syncing data from the server…" (297-302).
- Toasts auto-hide after 3.2 s (`toastMsg`, 1572-1576).

---

## 6. Pages/OilConfigurator.vue — "Business OS configurator"

**Purpose**: a friendlier, values-only editor over the same `thresholds` table, grouped Domain → Channel → Type, with a YAML export of the whole registry. Route `/oil-configurator`, auth-only (Router.js:18), full-bleed (App.vue:43). No admin gate in the component — scope comes entirely from the API (non-admins only receive their domains' rows).

**Data load**: GET `/api/threshold-config/thresholds` with bearer headers on mount (`loadThresholds`, OilConfigurator.vue:428-445, 524-526); failure toasts "Could not load thresholds — check your domain access" (441). While loading, AccountRouteLoader shell "Business OS / Loading thresholds…" (3-8).

**Regions**
- **Sidebar "Domains"**: one button per distinct `domain` (sorted; `domains` computed 301-308), each with a keyword-matched emoji icon (`domainIcon` over DOMAIN_ICONS map, 270-278, 342-348), accent color by index (338-341) and row count (42). Below a divider, a **System → "Export YAML"** pseudo-domain (`activeDomain = '__export'`) showing a badge with the number of unsaved edits (44-60).
- **Topbar**: "OIL v5 / Rules registry" crumb, title, chips for Domains / Thresholds / **Unsaved n** (66-97); actions "📤 Export YAML" (jumps to export page) and "💾 Save All" (disabled unless `changedKeys.length` and not saving) (88-95).
- **Empty state** when the API returns no rows: "No thresholds found … Check your domain access or ask an admin to assign domains to your account." (102-106).

**Export page** (`activeDomain === '__export'`, 108-135)
- Header: "Export — rules_registry.yaml … the single source of truth read by AI agents and N8N workflows." (110-113).
- **📋 Copy YAML** (button flips to "✓ Copied!" for 2 s, `copyYaml` via `navigator.clipboard` 503-508) and **⬇ Download .yaml** (client-side Blob download named `rules_registry.yaml`, `downloadYaml` 510-516). The YAML is built client-side: one `threshold_key: value  # [domain] label (unit)` line per row, using any unsaved local edits (`yamlString`, 492-501) — note this export includes *unsaved* values, unlike the Threshold Configurator's server-side YAML export.
- Per-domain preview cards listing `key: value # unit — label` (120-134).

**Domain page** (138-233)
- Header with stat chips (thresholds count, channel count, unsaved count) and a scoped search box with live match count and ✕ clear (140-162; `matchesSearch` checks label/key/unit/type/channel, 383-388; `searchMatchCount` 329-334).
- **Save bar**: shows "n unsaved change(s)" with a dot, or "✓ All values saved" / transient "n values saved" message; buttons **Discard** (clears all local edits, `discardChanges` 488-490 — no confirm dialog) and **💾 Save Changes** (165-183).
- **Grouping**: rows are bucketed by `channel` (blank → "No Channel", sorted last) then by `type` (blank → "General"), one card per type with accent color, capitalized title, optional fulfillment tag and value count (`channelSectionsForDomain` 390-413, `buildTypeSections` 357-380; template 185-226).
- **Inline editing**: each threshold renders label, mono `threshold_key`, and a `type="number" step="any"` input whose value is `localValues[key] ?? row.value`; edits parse with `parseFloat` and non-numeric input is ignored (`onInput`, 421-426). Changed fields get amber "changed" styling (`isRowChanged`, 211-221, 415-419). `changedKeys` counts only keys whose string value differs from the original (318-323).
- **Save All / Save Changes** (`saveAll`, 447-486): loops the changed keys and issues one **PUT `/api/threshold-config/thresholds/<threshold_id>`** per key with body `{ value, change_reason: 'Updated via Business OS Configurator' }` (457-464) — i.e. this page always writes an audit reason. Successful rows update in place and leave the dirty set; failures are counted and reported "X saved · Y failed — check permissions" (479-485). Non-admins can therefore *attempt* saves; the server enforces permissions.
- No-search-match and no-domain-selected empty states (228-239).

---

## 7. Rule Builder (admin only)

Three files: page `Pages/RuleBuilder.vue`, recursive editor `components/RuleNode.vue`, pure engine `components/ruleLogic.js`. Route `/rule-builder`, `requiresAuth + requiresAdmin` (Router.js:19); nav link hidden for non-admins (Header.vue:21).

### 7.1 RuleBuilder.vue — page

**Purpose**: visually author `condition_logics` rows (the WHEN/THEN per-stage logic of business rules) without typing the coded string.

**Data load** (`loadAll`, RuleBuilder.vue:295-320): on mount, parallel GETs to `/api/threshold-config/business-rules`, `/glossary`, `/thresholds` (298-302). Failure toasts "Could not load rule data — admin access required" (316). **Deep-link support**: `?rule=BL-001&stage=initial` selects that rule and stage (or pre-fills a new condition with the stage if it doesn't exist yet) — this is the target of the Threshold Configurator's condition-logics Add/Edit hand-off (306-314; `selectStageByName` 367-373). Otherwise the first rule is auto-selected (312-313). Loading shows the AccountRouteLoader shell (3).

**Regions**
- **Sidebar "Business rules"** (dark): count pill, one button per rule showing `rule_id` + name, active highlight, and a **＋ New rule** button (8-27).
- **Topbar**: ← Back button (`goBack`: history back, else `/threshold-configurator`, 584-587), "BLOS / Rule Builder" crumb, chips Rules / Metrics / Thresholds counts (30-44).
- **New-rule panel** (`showNewRule`): Rule ID (pre-filled with next `BL-nnn` via `nextRuleId`, 494-501), Rule name* (required — Create disabled until non-empty, 62), Domain, Owner (defaults to current user, `openNewRule` 488-492). **Create rule** POSTs `/api/threshold-config/business-rules` with `status: 'Active'` and `created_by`; success reloads the rule list and selects the new rule (`createRule`, 503-528). Cancel hides the panel (61).
- **Empty state** "Pick a business rule" when nothing selected (69-72).
- **Stage tabs**: one pill per existing condition (`c.stage` or "stage?"), plus a dashed **＋ New** tab (`activeConditionId === null` means unsaved new condition) (77-93). Selecting a condition loads its row into the form; selecting while dirty triggers the discard guard (`selectCondition`, 344-350).
- **Builder card**:
  - Stage* input with datalist suggestions `initial / restore / kill` + any stages already used (98-101; `stageSuggestions` 256-261) and Stage description (102-103).
  - **WHEN** section: hosts the recursive `<RuleNode>` tree (118) — or, if the stored coded string cannot be parsed, a **raw mode** amber panel: "⚠ This rule couldn't be read into the visual builder, so you're editing the raw text. Fix it and click 'Parse', or save as-is." with a mono textarea and a **Parse into builder** button (`tryParseRaw` re-attempts `parseSafe`; success switches to visual mode and marks dirty, failure toasts the parse error) (111-117, 409-420). Raw mode is entered per-condition in `applyCondition` when `parseSafe` fails (352-365) — this guarantees malformed legacy data is never lost.
  - **Preview**: side-by-side "Plain text" (human sentence via `toReadable` with glossary/threshold label maps) and "Logic (saved to condition_logic_by_ids)" (`serializePreview`, keeps `[metric]`/`[value]` placeholders) — regenerated on every tree change (121-130; `regenerate` 399-407; maps 246-255).
  - **THEN** textarea → `decision_output` (133-134).
  - **"Where this rule applies"** collapsible context panel (📍, Show/Hide) with level/type/fulfillment/channel/account/site/status/owner inputs (137-158). New conditions copy these context defaults from an existing sibling condition and set owner to the current user (`applyNewCondition`, 379-392).
  - **Save bar**: status text — block reason, "Unsaved changes", or "✓ Up to date" (161-166); buttons **Delete stage** (only for saved conditions; native `window.confirm('Delete this condition (<stage>)? This cannot be undone.')` then DELETE `/api/threshold-config/condition-logics/<id>` — `removeCondition` 471-486), **Discard changes** (disabled unless dirty; routes through the discard modal then reverts to last-saved row or a blank new condition — `discardEdits`/`revertEdits` 567-582), and **Create condition / Save changes** (167-173).

**Client-side validation — `canSave` / `saveBlockReason`** (262-274): requires `rule_id` and non-empty `stage`; in visual mode requires ≥1 clause and every clause complete (metric+op+value via `isComplete`/`clauseCount`); in raw mode requires non-empty text. Messages: "Stage is required", "Add at least one condition", "Finish every condition (metric, operator, threshold)", "Condition text is empty". The primary button is disabled while `!canSave || saving` (170).

**Save** (`saveCondition`, 441-469): builds payload with both representations — `condition_logic_by_ids` (coded, `serialize`) and `condition_logic_rule` (readable) — plus stage/context fields and `created_by` defaulting to the current user (`buildPayload` 422-439). POST `/api/threshold-config/condition-logics` for new, PUT `/api/threshold-config/condition-logics/<id>` for existing (447-451). On success: toast, `dirty` cleared **before** reloading conditions so the post-save re-select can't trip the discard guard (comment at 458-459), then re-selects the saved row (460-462).

**Unsaved-changes discard guard** (the page's signature behaviour)
- Any destructive navigation funnels through `guard(proceed)`: if `dirty`, it opens the modal instead of proceeding (538-544). Triggers: switching rules (322-324), switching stage tabs (344-350), starting a new condition (375-377), and the explicit Discard button (567-571).
- Modal (183-193): ⚠️ "Discard unsaved changes?" — "You've edited this stage but haven't saved it. If you continue, those changes will be lost and can't be recovered." Buttons: **Keep editing** (cancel — runs optional onCancel, 557-561) and **Discard changes** (solid red — clears dirty and runs the queued action, 550-555). Escape key cancels (563-565).
- **Route-leave guard**: `beforeRouteLeave` intercepts Back button, header nav and browser back — if dirty it opens the same modal, calling `next()` on confirm and `next(false)` on cancel (592-595). There is no `beforeunload` hook, so a hard refresh/close still loses edits silently.

### 7.2 components/RuleNode.vue — recursive group/clause editor

- Renders one **group** node; the root group is passed `is-root` from RuleBuilder.vue:118. Group header: "Match" segmented control **ALL of these** (AND) / **ANY of these** (OR) (`setOp`, RuleNode.vue:8-11, 121-123), item count (12), and — for non-root groups — an "Either/or group" tag plus tools **⤴ Ungroup** and **✕ remove** emitted to the parent (14-17).
- **Clause rows** (33-61): three selects — metric (glossary terms shown as `term (GL-xxx)`, with an "(unknown)" fallback option when the stored code isn't in the glossary, 35-39), operator (word labels from `opLabel`: "is less than", "is at least", etc., 42-44), threshold (labels as `label (TH-xxx)` with unknown fallback, 47-51). Row tools (revealed on hover/focus; always visible on touch, 293-295): ↑/↓ move (disabled at ends, `moveChild` 145-151), **⊟** "Put this on its own either/or branch" (`wrapChild` wraps the clause in a new group, 155-160), ✕ remove (140-143).
- Nested groups recurse with `depth + 1`; accent colour cycles by depth from a 6-colour palette so nesting levels are visually distinct (63-74, 95-96, 110-112). AND/OR joiner pills appear between children (28-31).
- A single-child non-root group shows the hint "A group needs 2+ conditions to do anything — add another, or Ungroup." (79-82). `ungroupChild` splices a group's children up one level (163-169).
- Footer buttons: **＋ Condition** (append blank clause) and **＋ Either/or group** (append AND group with one blank clause) (85-88, 130-138). Every mutation emits `change`, which bubbles to RuleBuilder's `onTreeChange` → regenerate preview + `dirty = true` (119, RuleBuilder.vue:394-397).
- Note: despite the task brief's phrase "drag-and-drop", the builder is **drag-free** — ordering is via ↑/↓ buttons; the Header tooltip itself says "drag-free clause builder" (Header.vue:21).

### 7.3 components/ruleLogic.js — pure engine

- Purpose comment: converts between the stored `condition_logics.condition_logic_by_ids` string (e.g. `IF GL-001 < TH-001 AND GL-002 >= TH-002`) and an editable tree, and renders the readable sentence for `condition_logic_rule`; framework-free by design for unit testing (ruleLogic.js:1-17).
- Tree shape: `clause {metric, op, value}` / `group {op: AND|OR, children[]}`; root is always a group (ruleLogic.js:9-14). Operators `>=, <=, !=, <, >, =` with aliases `==, =<, =>, <>` normalized on input (20, 33).
- **Tokenizer** tolerates leading `IF`/`WHEN`, newlines, irregular spacing; throws descriptive errors ("Could not read a condition near …") on garbage (83-121). **Parser** is recursive-descent with OR lower precedence than AND, parentheses supported, same-operator groups flattened (`parseOr`/`parseAnd`/`parsePrimary`/`flattenSameOp`, 177-227). `parseSafe` returns `{ok:false, error, raw}` instead of throwing — that is what flips the UI to raw mode so data is never lost (139-171).
- **Serializers**: `serialize` prunes incomplete clauses and emits parentheses only where a nested multi-child group needs them, prefixing `IF ` (238-268); `serializePreview` keeps `[metric]`/`?`/`[value]` placeholders for the live preview (244-249). `toReadable` maps GL codes→glossary terms and TH codes→threshold labels with word operators and lowercase and/or (289-310). Validation helpers `isComplete` / `clauseCount` back the page's `canSave` (53-70).

---

## 8. Pages/FileManager.vue — Central file library

**Purpose**: hierarchical shared file library — folders/files tree, table browser, text-file viewer, uploads, replace-with-diff review, rename/move/delete, ZIP export, and "New/Updated" change highlighting across sessions. Route `/file-manager`, auth-only (Router.js:20), full-bleed (App.vue:43). `/markdown-manager` redirects here (Router.js:21).

### 8.1 Role model
- `isAdmin` computed from stored user (FileManager.vue:704-714). Admin-only UI: New folder, Upload, per-row Delete buttons, the "More" menus (Replace/Rename/Move), and the hidden re-upload input (44, 91-96, 134-139, 192-197, 211-214). Every admin method also re-checks `if (!this.isAdmin) return` server-guard style (e.g. 1624, 1629, 1653, 1659, 1708, 1718, 1784, 2212, 2218, 2242, 2254, 2278, 2288). Non-admins keep Open/Download everywhere and get a "Download ZIP" button in the root table where admins get Delete/More (140).
- Hero copy is role-aware: admin "Organize folders, upload files, and export ZIP archives…", non-admin "Browse, preview, and download files. Press **Reload** after the library changes.", with a "Full access" / "Read-only" chip (31-38).

### 8.2 Layout & regions
- **Global busy strip**: a thin animated bar at the very top whenever anything is in flight — `fmGlobalBusy` ORs loading/treeLoading/uploading/creating/renaming/moving/deleting/replacing/zipping (3-7, 643-658) with an aria-label naming the operation (659-672).
- **Sidebar "Library hierarchy"**: Refresh button (48-51), hint "Use ▸ to expand or collapse. Click a folder name to open it…" (53), a "Library root" item (55-60), then a flattened tree (`treeFlatVisible` walks roots respecting `treeExpandedIds`, emitting folder rows and — when expanded — file rows, 560-581). Chevron click toggles expansion without opening (66-68, 1571-1579); clicking a folder row opens it in the main panel; clicking a file row opens its folder and then the viewer (if previewable) or just marks it seen (`onTreeRowClick`/`onSidebarFileClick`, 1580-1596). Changed folders/files get tinted classes (`treeRowBtnClass`, 1530-1547).
- **Toolbar**: breadcrumb (Root + `folderPayload.breadcrumb` segments, each clickable, 81-89); actions — **New folder** (admin), **Upload file(s)** (admin; multi-file label-input, disabled at root: `:disabled="fmToolbarLocked || currentFolderId == null"`, 92-96), **Reload** (`refreshMain` = tree + current folder, 97-100, 1617-1622). All disabled while `fmToolbarLocked` (loading/uploading/creating/diff open, 701-703).
- **Root panel** (`currentFolderId === null`): intro card ("Uploads must go inside a folder (nothing is stored loose at root)." for admins, 104-109) and a "Top-level folders" table — Name, Path, Contents summary ("n subfolders · m files total", `rootFolderSummaryLine` 1695-1702), Modified, Actions (110-152). Header shows total file count across all folders (113, 552-559).
- **Folder panel**: "Contents (n files, m folders)" card with a header **Download** button that ZIPs the current folder (166-171), an overlay spinner "Updating folder…" during reloads (157-164), and a combined table of subfolder rows then file rows (185-216). File rows show a "New"/"Updated" badge when highlighted (202-205), a Details column with text-file line counts (206; lazily fetched per file via GET `/api/files/<id>/content` and cached in `fileLineCounts`, 1875-1891), and a Modified tooltip including created/updated timestamps (1866-1874).
- **"More" menus**: a viewport-fixed portal menu (so table overflow can't clip it) positioned against the trigger with flip-above logic and window scroll/resize tracking (236-258, 1932-2019). Items by target: root folder → Download ZIP, Rename; subfolder → Rename; file → **Replace file**, Rename, Move (246-257). Any outside click, resize, or folder change closes it (741-751, 726-728).

### 8.3 API calls (all with `authHeaders()`, FileManager.vue:763-765)
| Action | Endpoint | Where |
|---|---|---|
| Load tree | GET `/api/folders/tree` | loadTree 1500-1521 |
| Open folder | GET `/api/folders/<id>` | openFolder 1597-1616 |
| Create folder | POST `/api/folders` `{name, parent_id}` | submitCreateFolder 1628-1651 |
| Rename folder | PUT `/api/folders/<id>/rename` `{name}` | submitRenameFolder 1658-1681 |
| Delete folder | DELETE `/api/folders/<id>` | deleteFolder 1730-1747 |
| Folder ZIP | GET `/api/folders/<id>/download-zip` (blob) | downloadFolderZipById 810-835 |
| Upload file(s) | POST `/api/folders/<id>/files` (multipart, one per file) | onPickUpload 1783-1851 |
| File content (viewer, line counts, diff-left) | GET `/api/files/<id>/content` | 1881, 2198, 922-928 |
| File download | GET `/api/files/<id>/download` (blob; name from Content-Disposition) | downloadManagedFile 1247-1265 |
| Replace file | POST `/api/files/<id>/reupload` (multipart) | executeManagedFileReupload 1210-1231 |
| Rename file | PUT `/api/files/<id>/rename` `{name}` | submitRenameFile 2217-2240 |
| Move file | PUT `/api/files/<id>/move` `{folder_id}` | submitMoveFile 2253-2276 |
| Delete file | DELETE `/api/files/<id>` | deleteFileById 2300-2321 |

### 8.4 Modals & dialogs
- **New folder** (260-275): hint states whether it will be created at library root or inside the open folder (263-264); Create disabled until name non-blank; Enter submits.
- **Rename folder / Rename file** (277-305): single input, Save disabled while saving or blank, Enter submits.
- **Move file** (307-322): target-folder `<select>` built from the whole tree with `— ` indents (`moveOptions`, 582-595); default target prefers a folder other than the file's current one (2241-2252); Move disabled without a target. If no folders exist an inline error asks to create one first (2243-2246).
- **Delete folder** (324-345): danger modal — "You are about to remove **{name}** and **everything inside it**", bullet list (all nested subfolders; every file on disk and in the database), live stats line "Contains n files and m subfolders (including all nested levels)." (`deleteFolderStatsLine`, 1703-1706), "This cannot be undone.", Cancel / **Delete folder** (buttons disabled while deleting; Cancel blocked mid-delete, 1712-1716). Deleting the currently-open folder returns you to root (1735-1737).
- **Delete file** (347-364): danger modal — "Remove **{name}** from the library? The file will be deleted from storage and the catalog. If it is open in the viewer, that window will close." + "This cannot be undone." Confirm deletes, clears highlight, closes the viewer if it shows that file, and refreshes (2287-2321).
- **Replace-file diff review modal** — see 8.5.
- **Full-screen viewer** — see 8.6.

### 8.5 Replace-file diff review (admin)
Two entry paths, both promise-based via `fmOpenReplaceDiffModal({kind, managed, uploadFile})` which resolves `'confirm' | 'cancel'` (870-890):
1. **Replace file** (More menu) → hidden input → `onReuploadPicked`: if the pair qualifies, the modal opens *before* any upload; only `'confirm'` proceeds to POST `/api/files/<id>/reupload` (1232-1246).
2. **Upload collision**: during multi-upload, if a picked file's name matches an existing file in the folder and qualifies, the modal opens with kind `'upload'`; Cancel skips just that file and the batch continues (1800-1807).

- **Qualification** (`fmShouldOfferReplaceDiff`, 952-959): existing file must be previewable text (`canPreview` + `isTextFile`), upload ≤ 900,000 bytes, and the browser file must look texty by MIME or extension (whitelist csv/txt/json/xml/log/md/yml/html/js/ts/php/py/sql/vue…, 941-951). Non-qualifying replacements happen immediately with **no** diff review.
- **Content**: left = library version via GET `/api/files/<id>/content`, right = the picked file read with `FileReader` (891-940). While loading: "Loading both versions and building the diff…" (373); errors shown inline (374).
- **Line diff mode** (default): side-by-side LCS line diff with legend chips "Removed — left column only" / "Added — right column only", column headers "Library (current)" / "New file (selected)", per-line −/+ marks and line numbers (`fmBuildSideBySideDiffHtml`, 1143-1209). The LCS is capped at 2200×2200 lines / 950k cells; beyond that a note says the diff is too large but you can still confirm (960-1002, 1147-1153).
- **Rendered mode** — only offered when the file type supports it (md/markdown, json, csv, xml by ext or MIME; `replaceDiffSupportsRender`, 685-695; tab buttons 376-379): same row alignment as the text diff, but each line is individually rendered — Markdown through `marked`+highlight.js, JSON syntax-highlighted, CSV/XML escaped in styled line boxes (`fmBuildRenderedLineDiffHtml` + `fmRenderDiffLineHtml`, 1044-1142). Hint text explains the semantics (369-372, 382).
- **Buttons**: Cancel (also via backdrop click, 366) and the primary confirm labelled **"Upload and replace"** (upload-collision kind) or **"Replace library file"** (replace kind) — disabled while the diff is still loading (386-391, 682-684). A sequence counter invalidates stale async loads if the modal is reopened quickly (857-868, 884-921).

### 8.6 Full-screen viewer ("Open")
- Only for previewable files: ext md/markdown/txt/csv/json/xml/log or `text/*`, `application/json`, `application/xml` MIME (`canPreview`, 2048-2055). The Open button shows "Opening…" while loading (209).
- Full-viewport dialog with file name/meta, a **Text / Render** segmented control, and ✕ close (Esc key and click on the empty body area also close; body scroll locked while open) (395-431, 716-724, 2161-2182).
- Content fetched from GET `/api/files/<id>/content` (2197-2207). Default mode is **Render** for md/json/csv, else Text (2193-2196). Text mode = escaped `<pre>` "Source" (614-621). Render mode: Markdown via `marked` with highlight.js code blocks (623-624, 442-456, 2065-2078); JSON as a key-value list, an array-of-objects table, or pretty-printed block (2079-2108); CSV as a real table with quote-aware splitting and header handling (2109-2154); XML pretty-printed (632-634, 2155-2157); anything else as an escaped "Reading view" (635-641).

### 8.7 New/Updated highlighting (cross-session)
- Two localStorage keys: `ledsoneFmLibSnapshot_v1` (last-seen mtimes of every file/folder) and `ledsoneFmPendingHighlight_v1` (unacknowledged highlights) (459-462).
- On every tree load, current mtimes are diffed against the stored snapshot: unseen file ids → "New", increased mtimes → "Updated"; folder-meta changes flag folders; results merge with persisted pending highlights, prune entries for rows that no longer exist, then persist (`fmProcessLibrarySnapshotAfterTree` and helpers, 1278-1480). Ancestor folders of changed files are tinted in tree and tables (`fmRebuildFolderHighlightState`, 1407-1429).
- Files uploaded this session are marked "New" immediately (`markFileNew`, 1766-1772) with a 750 ms "shield" so the dialog-close click can't instantly clear the badge (1846-1850, comment 524).
- Highlights clear when the user acknowledges the file: clicking its table row (outside the Actions cell), opening the viewer, downloading, or deleting (`markFileSeen`, 1754-1765; call sites 1773-1777, 2185, 1259, 2305).

---

## 9. Cross-cutting behaviours a reviewer should know

1. **Role is re-verified on every navigation** — the router refreshes `/api/me` before entering any auth route and hard-logs-out on 401/403/419 (Router.js:63-68; userSession.js:129-132), so demoting a user takes effect on their next click, not next login.
2. **Admin surface is hidden, not just disabled**: Rule Builder link (Header.vue:21), Threshold Configurator's six extra tabs (ThresholdConfigurator.vue:761-764), all export/bulk/add buttons (ThresholdConfigurator.vue:95-101), and FileManager's mutation controls (FileManager.vue:91-96 etc.) simply don't render for non-admins; server scoping (domains) does the rest.
3. **The change_reason requirement for threshold edits is currently switched off** in the UI (`canSave` always true, ThresholdConfigurator.vue:832-838) while the Business OS page hard-codes `change_reason: 'Updated via Business OS Configurator'` on every save (OilConfigurator.vue:461-462).
4. **Two different YAML exports exist**: Threshold Configurator downloads the server-generated file (GET `/api/threshold-config/export-yaml`, ThresholdConfigurator.vue:1061-1074) while Business OS builds YAML client-side *including unsaved edits* (OilConfigurator.vue:492-516).
5. **Data-loss guards are asymmetric**: Rule Builder guards every in-app exit with its discard modal including `beforeRouteLeave` (RuleBuilder.vue:538-595) but not browser refresh/close; Business OS has a Discard button but **no** guard on navigation — unsaved threshold edits are silently lost on route change (OilConfigurator.vue:488-490; no `beforeRouteLeave`).

---

## 10. Coverage statement

Every file under `resources/js/Account/` (recursive), with coverage level:

| File | Coverage |
|---|---|
| `Account.js` | documented-deep (§2.1) |
| `App.vue` | documented-deep (§2.4) |
| `Router.js` | documented-deep (§1, §2.6) |
| `Store.js` | documented-brief (§2.2 — 15-line store shim; app-level module documented for the `api` helper) |
| `Components.js` | documented-brief (§2.2 — empty/commented-out plugin, no runtime behaviour) |
| `Pages.vue` | documented-brief (§2.3 — 2-line unused pass-through) |
| `userSession.js` | documented-deep (§2.5) |
| `components/AccountRouteLoader.vue` | documented-deep (§2.9 — presentational; both variants and props covered) |
| `components/ruleLogic.js` | documented-deep (§7.3) |
| `components/RuleNode.vue` | documented-deep (§7.2) |
| `Pages/Loading.vue` | documented-deep (§2.7) |
| `Pages/auth/Login.vue` | documented-deep (§3) |
| `Pages/Dashboard.vue` | documented-deep (§4) |
| `Pages/ThresholdConfigurator.vue` | documented-deep (§5) |
| `Pages/OilConfigurator.vue` | documented-deep (§6) |
| `Pages/RuleBuilder.vue` | documented-deep (§7.1) |
| `Pages/FileManager.vue` | documented-deep (§8) |
| `Pages/includes/Header.vue` | documented-deep (§2.8) |
| `Pages/includes/Sidebar.vue` | documented-brief (§2.10 — orphaned, not imported anywhere) |
| `Pages/includes/TopBar.vue` | documented-brief (§2.10 — orphaned, not imported anywhere) |

No files under `resources/js/Account/` were skipped. There are no binary/asset files in the directory (all 20 entries are `.js` / `.vue`), so the `not-applicable(asset)` category is empty.

*Styling-only line ranges (scoped `<style>` blocks) were read but summarised rather than itemised, since they carry no user-facing behaviour beyond what is noted (full-bleed layout, sticky headers, responsive breakpoints, reduced-motion fallbacks).*


---

# PART G — SECURITY & DEPLOY

---

# REQ-04-D07 · Security & Access Model + Environment, Build & Deploy Runbook

## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-07-07 |
| **deliverable_id** | REQ-04-D07 |
| **requirement_id** | REQ-04 |
| **project** | PRJ-2026-003_blos-project-sentinel |
| **project_name** | LEDsONE Centralizer (Centralized Admin / Operations Platform) |
| **status** | DRAFT |
| **app_under_review** | `C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer` (READ-ONLY) |
| **stack** | Laravel 9 (PHP ^8.0.2) + Vue 2 SPA (vue-router history mode), Laravel Mix / Webpack |
| **scope** | Part 1 — Security & Access Model (traced to file:line). Part 2 — Environment, Build & Deploy runbook. |
| **note** | All security defects are recorded in the final section as **FINDINGS ONLY — for Sajeesan review, not fixed.** Nothing in the app was modified. |

> **Terminology note:** this app implements a **custom token scheme** (a random string stored in the `user.token` column and matched per-request), **not** Laravel Sanctum tokens and **not** Laravel session auth — even though both Sanctum and the session guard are installed/configured. See §1.9 (config actually in use vs unused).

---

# PART 1 — SECURITY & ACCESS MODEL

## 1.1 Authentication lifecycle (end to end)

### Step 1 — Login request
- Route: `POST /api/login` → `AuthController@login`, registered **outside** any auth middleware. `routes/api.php:17`.
- Controller: `app/Http/Controllers/auth/AuthController.php:30-80`.
- Validation: `email => required|string|email`, `password => required|string` (`AuthController.php:32-35`). Note there is **no throttle-specific validation**; global throttle only (see §1.8).
- User lookup by email column `user_email`: `User::where('user_email', $request->email)->first()` (`AuthController.php:46`).
- Gate on login: rejects if user missing, **not active**, or password mismatch — `if (!$user || !$user->is_active || !Hash::check($request->password, $user->password_hash))` → 401 (`AuthController.php:48-53`).
  - `is_active` is a computed accessor over the `user_status` column (see §1.5).
  - `password_hash` is a computed accessor over the `user_password` column (see §1.7).

### Step 2 — Token generation
- Token = `Str::random(32)` → a 32-character random string (`AuthController.php:55`).
- Stored on the user row: `$user->token = $token; $user->save();` (`AuthController.php:56-57`).
- Storage column: `token` on the `user` table (`User::$fillable` includes `'token'`, `app/Models/User.php:20`).
- The `setTokenAttribute` mutator **truncates the stored token to 32 chars** and normalises empty/null to `null`: `substr((string) $value, 0, 32)` (`User.php:105-112`). (Token length 32 == truncation length 32, so no data is lost, but this coupling is fragile.)
- Login response returns `token` plus a small user object (`id, name, email, role, domain`) (`AuthController.php:59-72`).

### Step 3 — Client-side token storage (localStorage vs sessionStorage)
- Decided by the **"Remember me"** checkbox in the login form: `const storage = this.form.rememberMe ? localStorage : sessionStorage` (`resources/js/Account/Pages/auth/Login.vue:139`).
- Token stored under key `auth`, user JSON under key `user` (`Login.vue:140-143`).
- The **other** storage is cleared and a "bucket" marker (`lc_auth_bucket` = `local` | `session`) is written so token and user always resolve from the same place (`Login.vue:144-152`; `setAuthBucket` in `resources/js/Account/userSession.js:12-20`).
- Rationale for the bucket abstraction (from code comments): fixes "wrong thresholds / role" caused by token in one storage and cached user in the other (`userSession.js:11, 66-74`).

### Step 4 — Authorization Bearer header injection
- `userSession.authHeaders()` builds `Authorization: 'Bearer ' + token` from whichever storage the bucket resolves to (`userSession.js:76-82`). Used by `refreshSessionUser()`'s call to `/api/me` (`userSession.js:102`).
- The general API helper `resources/js/Api.js` **independently** reads the token: `let auth = localStorage.getItem('auth') || sessionStorage.getItem('auth')` and sets `headers.headers.Authorization = 'Bearer ' + auth` (`Api.js:105-109`). (Two separate token-resolution code paths exist — `authHeaders()` and `Api.js`; see finding F-9.)

### Step 5 — Per-request server validation
- Middleware: `App\Http\Middleware\CheckAuthMiddleware` (`app/Http/Middleware/CheckAuthMiddleware.php:11-30`).
- Logic: read `$request->bearerToken()`; if non-empty, look up `User::where('token', $token)->first()`; if the user exists **and** `$user->is_active`, call `Auth::onceUsingId($user->getKey())` and set a user resolver, then continue; otherwise return `401 {"error":"Invalid authentication"}` (`CheckAuthMiddleware.php:15-28`).
- `Auth::onceUsingId` logs the user in **for the current request only** (no session persistence) — consistent with the stateless token model.
- `$user->getKey()` returns the primary key, which is the `user` column (`User::$primaryKey = 'user'`, `User.php:14`; `getAuthIdentifierName()` returns `'user'`, `User.php:24-27`).
- Applied as a route group in `routes/api.php:24` wrapping all protected routes.

### Step 6 — is_active / user_status gating (per request)
- Both login (`AuthController.php:48`) and every authenticated request (`CheckAuthMiddleware.php:19`) require `is_active` to be truthy.
- `is_active` is derived from the `user_status` column: null/empty ⇒ **treated as active (`true`)**; otherwise active only if the value is one of `active|1|yes|true|enabled` (case-insensitive) (`User.php:91-98`). See finding F-8 (null status defaults to active).

### Step 7 — Logout / token clearing
- Route: `POST /api/logout` → `AuthController@logout`, **inside** the auth group (`routes/api.php:26`).
- Server: reads bearer token, finds the user, sets `$user->token = null; $user->save();` (`AuthController.php:174-200`). This invalidates the token server-side.
- Client sign-out button (live path: `Header.vue:60` → `handleLogout`, `Header.vue:232-240`; identical logic duplicated in dead-code `Sidebar.vue:40-47`, which is imported nowhere) **only clears local/session storage and the bucket** and routes to `/login`. It does **not** call `POST /api/logout` — so the server-side token is not cleared on a normal sign-out (see finding F-7).
- Axios response interceptor: on 401/403/419 it calls `clearAllAuth()` and hard-redirects to `/login` (`Api.js:6-17`; `clearAllAuth` in `userSession.js:86-92`).

**Auth chain (one line):** `POST /api/login` validates + checks `is_active` + `Hash::check` → issues `Str::random(32)` saved to `user.token` → client stores under `auth` in local/sessionStorage (per "Remember me") → sends `Authorization: Bearer <token>` → `CheckAuthMiddleware` matches the token to a row, re-checks `is_active`, and `Auth::onceUsingId()` for that request → `POST /api/logout` nulls `user.token`.

---

## 1.2 Role model

- Roles are stored in the DB column `config_role` and normalised through the `role` accessor: `getRoleAttribute()` lowercases/trims `config_role`; returns `admin` or `cashier` verbatim; otherwise returns the raw value if non-empty, else defaults to `'cashier'` (`app/Models/User.php:77-84`). `setRoleAttribute()` writes back to `config_role` (`User.php:86-89`).
- The **three role values** referenced across the app: `admin`, `cashier`, `domain_owner`:
  - Registration `role` validation allows `in:admin,cashier,domain_owner` (`AuthController.php:104`).
  - `admin` gate: `EnsureUserIsAdmin` requires `$user->role === 'admin'`, else `403 {"error":"Admin access required"}` (`app/Http/Middleware/EnsureUserIsAdmin.php:10-17`).
  - `domain_owner` gate: `EnsureDomainOwner` requires `$user->role === 'domain_owner'`, else 403 (`app/Http/Middleware/EnsureDomainOwner.php:10-17`).
  - **Accessor edge case:** `getRoleAttribute()` only special-cases `admin`/`cashier`; `domain_owner` falls through the "else return raw" branch (`User.php:82-83`). It still returns `'domain_owner'` correctly because the raw value is passed through — but there is no explicit normalisation for it (worth noting; not a defect per se).
- Middleware aliases: `'admin' => EnsureUserIsAdmin::class`, `'domain_owner' => EnsureDomainOwner::class` (`app/Http/Kernel.php:68-69`).
- The `admin` alias is applied to the admin-only route groups in `routes/api.php:41` (threshold-config management) and `routes/api.php:87` (folder/file writes, categories, products, inventory, sales-update, reports, users CRUD). **`domain_owner` is aliased but never applied to any route** (`grep` of `routes/api.php` shows no `'domain_owner'` middleware usage) — see finding F-6.
- **Client-side role gate for `/rule-builder`:** the route is defined with `meta: { requiresAuth: true, requiresAdmin: true }` (`resources/js/Account/Router.js:19`). The `router.beforeEach` guard, for a `requiresAdmin` route, parses the stored user JSON and blocks (redirect to `/`) unless `role === 'admin'` (`Router.js:75-90`). **This is a client-side gate only** — there is no server route named `/rule-builder`; Rule Builder reads/writes go through the admin-guarded `threshold-config/business-rules`, `condition-logics`, `rule-threshold-mappings` endpoints, which ARE server-side admin-gated (`routes/api.php:43-54`). So the UI gate is convenience; the data endpoints are properly protected.

---

## 1.3 Domain scoping (non-admin data isolation)

Traced in `app/Http/Controllers/Api/ThresholdConfigurationController.php`.

- `isAdmin($user)`: true iff lowercased `role === 'admin'` (`:24-31`).
- `allowedDomainsFor($user)` (`:45-77`):
  - If admin → returns `null` (meaning "no restriction / all domains") (`:47-49`).
  - If no user id → returns `[]` (empty) (`:50-53`).
  - Collects domains from **two** sources and merges (de-duplicated, case-insensitive):
    1. The pivot: `$user->userDomainAccess()->pluck('domain')` (`:54-58`). Relation `userDomainAccess()` is `hasMany(UserDomainAccess, <fk>, 'user')` (`User.php:128-131`); pivot table is `user_domain_access` (`app/Models/UserDomainAccess.php:10`). The FK column is resolved dynamically as `user` or `user_id` depending on which exists (`UserDomainAccess::userFkColumn()`, `:16-30`).
    2. The user's own `domain` column (falls back to `user_domain`): `$user->getAttribute('domain') ?? $user->getAttribute('user_domain')` (`:59-65`).
  - Merge order: user-column domain first, then pivot domains; de-dup by lowercase (`:66-76`).
- `ensureDomainAllowed($user, $domain)` (`:79-94`): admin always true; else case-insensitive membership check against `allowedDomainsFor()`. Used to gate `thresholdsUpdate` (`:490-492` returns 403 "You do not have access to this domain.").
- `applyThresholdDomainFilterForNonAdmin($q, $user)` (`:96-114`):
  - Admin → no filter (`:98-100`).
  - **If `allowedDomains` is empty → `$q->whereRaw('1 = 0')`** (returns nothing) (`:101-105`).
  - Else adds `OR LOWER(TRIM(COALESCE(domain,''))) = ?` for each allowed domain (`:106-113`).
- Applied in `thresholdsIndex()` (`:416-448`): admin may optionally filter by `?domain=`; a non-admin with **zero** allowed domains gets an early `return ... data: []` (`:427-429`), otherwise the domain filter is applied (`:430`).

**What a non-admin with zero access rows actually sees:** an **empty** threshold list (`data: []`) — both via the early return in `thresholdsIndex` (`:427-429`) and via the `1 = 0` filter fallback (`:103`). They cannot see or edit any threshold. Any threshold update to a domain they lack is rejected 403 (`:490-492`).

> **Scope caveat:** domain scoping is implemented **only on the threshold endpoints** in this controller. Other admin-gated resources (products, inventory, files, users, etc. in `routes/api.php:87-118`) are gated by `admin` only, not domain-scoped — which is consistent since only admins reach them.

---

## 1.4 Registration endpoint

- Route: `POST /api/add-new-users` → `AuthController@register` (`routes/api.php:16`).
- **Position relative to auth middleware:** it sits at `routes/api.php:16`, i.e. **above and outside** the `CheckAuthMiddleware` group (which begins at `routes/api.php:24`). It is therefore a **fully public, unauthenticated endpoint** — anyone can call it. **[FINDING F-1 — see final section.]**
- Validation (`AuthController.php:101-108`):
  - `name => required|string|max:100`
  - `email => required|string|email|max:150|unique:user,user_email`
  - `role => nullable|in:admin,cashier,domain_owner`  ← a caller MAY set `role=admin`. **[FINDING F-2.]**
  - `domain => nullable|string|max:100`
  - `password => required|string|min:6`  ← 6-char minimum, no complexity. **[FINDING F-3.]**
  - `confirmPassword => required|string|same:password`
- On success creates the user with `is_active => true`, `token => Str::random(32)`, `role` defaulting to `'cashier'` when not supplied (`AuthController.php:119-127`). Password stored via `password_hash` accessor → `Hash::make` (`AuthController.php:122`).

*(Reported as fact; risks flagged in the final section; not fixed.)*

---

## 1.5 Password hashing
- Login uses `Hash::check($request->password, $user->password_hash)` (`AuthController.php:48`).
- Registration uses `Hash::make($request->password)` written to the `password_hash` accessor (`AuthController.php:122`).
- `password_hash` is an accessor/mutator over the DB column `user_password` (`User.php:67-75`).
- Hash driver: **bcrypt** (`config/hashing.php:18`); `phpunit.xml:22` sets `BCRYPT_ROUNDS=4` for tests only (production uses the framework default of 10 unless overridden by env).
- `getAuthPassword()` returns `user_password` for the framework's own auth flows (`User.php:29-32`), though the session guard is not the active auth path here.

## 1.6 Rate limiting
- Global API throttle is applied in the `api` middleware group: `'throttle:200,1'` = **200 requests/minute** (`app/Http/Kernel.php:45`). The commented-out `'throttle:api'` line above it is disabled (`Kernel.php:42-44`).
- A named `api` limiter also exists (`60/min` keyed by user id or IP) in `RouteServiceProvider::configureRateLimiting()` (`app/Providers/RouteServiceProvider.php:46-51`) but is **not referenced** by the active middleware group (the group uses the literal `throttle:200,1`, not `throttle:api`). So effective limit = 200/min per IP for all API routes, including `/login` and `/add-new-users`. **[FINDING F-4 — login/registration not separately throttled.]**

## 1.7 CORS
- `config/cors.php`: `paths => ['api/*', 'sanctum/csrf-cookie']`, `allowed_methods => ['*']`, `allowed_origins => ['*']`, `allowed_headers => ['*']`, **and `supports_credentials => true`** (`config/cors.php:18-32`).
- `HandleCors` is in the global middleware stack (`app/Http/Kernel.php:19`).
- **[FINDING F-5]** `allowed_origins => ['*']` together with `supports_credentials => true` is an invalid/permissive combination. (Bearer-token auth here does not rely on cookies, so the practical exposure is lower, but the config is wrong and browsers reject wildcard+credentials for cookie flows.)

## 1.8 Sanctum / session config: in use vs unused
- **Custom token scheme is the real auth** (see §1.1): a random string in `user.token`, matched by `CheckAuthMiddleware`. This is **not** Sanctum personal-access-tokens and **not** the session guard.
- `laravel/sanctum` **is installed** (`composer.json:14`) and `config/sanctum.php` exists, but the Sanctum stateful middleware is **commented out** in the `api` group (`app/Http/Kernel.php:42`). Sanctum is effectively **unused** by the auth path.
- `config/auth.php`: default guard `web` (session driver), provider `users` → `App\Models\User` (`config/auth.php:16-19, 38-43, 62-66`). The `web`/session guard is **not** exercised by the API token flow; `Auth::onceUsingId()` sets the user for a single request without a session.
- `config/session.php` exists (framework default); sessions are used by `web` middleware only, which serves the SPA shell (`routes/web.php:7-9`).

## 1.9 API keys / env-based auth
- **No `BLOS_API_KEY` or similar API-key auth exists.** `grep` for `BLOS_API_KEY|API_KEY|api_key` across the repo (excluding `node_modules`) returned **no matches**.
- The only tokens/secrets present in `.env.example` are **Pusher** app id/key/secret and an **eBay API token** (`.env.example:37-50`). These are third-party integration credentials committed to `.env.example` — see finding F-10 (secrets in example env).
- `config/auth.php` guards: only the `web` session guard is defined (`config/auth.php:38-43`). No custom API guard is registered — the token check is done entirely in `CheckAuthMiddleware`, not through a Laravel guard.

---

# PART 2 — ENVIRONMENT, BUILD & DEPLOY RUNBOOK (for a new developer)

## 2.1 Stack & versions

**Backend (`composer.json`):**
- PHP constraint: `^8.0.2` (`composer.json:8`).
- Laravel framework `^9.19` (`composer.json:13`).
- Key packages: `laravel/sanctum ^3.0` (installed, effectively unused for auth — see §1.8), `laravel/tinker ^2.7`, `beyondcode/laravel-websockets ^1.13`, `cboden/ratchet ^0.4.4`, `pusher/pusher-php-server ^7.2` (realtime), `guzzlehttp/guzzle ^7.2`, `league/flysystem ^3.29` + `league/flysystem-aws-s3-v3 ^3.29` (S3 disks), `elibyy/tcpdf-laravel ^10.0` + `webklex/laravel-pdfmerger ^1.3` (PDF) (`composer.json:9-19`).
- Dev: `phpunit/phpunit ^9.5.10`, `laravel/pint`, `laravel/sail`, `mockery`, `nunomaduro/collision`, `spatie/laravel-ignition` (`composer.json:21-29`).
- `minimum-stability: dev`, `prefer-stable: true` (`composer.json:70-71`).

**Frontend (`package.json`):**
- Build tool: `laravel-mix ^6.0.6` (Webpack) (`package.json:16`).
- Framework: `vue ^2.6.14`, `vue-loader ^15.9.8`, `vue-template-compiler ^2.6.12`, `vue-router ^3.5.1`, `vuex ^3.6.2` (`package.json:24-26, 35, 37`).
- Notable deps: `bootstrap ^5.1.3` + `bootstrap-vue ^2.22.0`, `chart.js ^4.2.1`, `marked ^18.0.2` + `marked-highlight` + `highlight.js ^11.11.1` (markdown/file preview), `axios ^0.25.0`, `laravel-echo` + `pusher-js` + `socket.io-client` + `ws` (realtime) (`package.json:12-39`).
- Scripts (`package.json:3-11`): `dev`/`development` = `mix`; `watch` = `mix watch`; `watch-poll`; `hot` = `mix watch --hot`; `prod`/`production` = `mix --production`.

## 2.2 Build configuration (`webpack.mix.js`)
- Entry JS: `resources/js/Account/Account.js` → output `public/js` (produces `public/js/Account.js`) (`webpack.mix.js:15`).
- SCSS: `resources/scss/app.scss` → `public/css` (`webpack.mix.js:16`).
- `.vue()` enabled; webpack aliases for `marked`, `highlight.js`, `marked-highlight` (`webpack.mix.js:17-26`).
- Notifications disabled (`webpack.mix.js:27`).

## 2.3 Local setup (new developer)
1. `composer install` (PHP 8.0.2+; ensure `pdo_mysql` extension).
2. `cp .env.example .env` then `php artisan key:generate` (composer's `post-root-package-install`/`post-create-project-cmd` do this on fresh installs — `composer.json:50-55`). **Edit `.env`**: set `DB_DATABASE` and credentials (the example points at `message_app` / `root` / no password — `.env.example:14-16`, which is a leftover; the live DB is `centralizer`, see §2.6).
3. `npm install`.
4. Build the frontend:
   - Dev: `npm run development` (or `npm run watch` while iterating).
   - Prod: `npm run production`.
   - Output lands at **`public/js/Account.js`** (and `public/css/app.css`).
5. Serve: `php artisan serve` locally, **or** run under XAMPP (Apache + MySQL) — the live server uses XAMPP/LAMPP (§2.6).
6. SPA routing: all non-`api` GET routes return the `accounts` view (`routes/web.php:7-9`); Vue Router (history mode) handles client routes (`Router.js:14`).

## 2.4 Built bundle is git-ignored
- `.gitignore` ignores **`/public/js/Account.js`** (listed twice — `.gitignore:7` and `.gitignore:20`), plus `/public/build`, `/public/hot`, `/public/storage`, `/node_modules`, `/vendor`, `.env*`.
- Notably `.gitignore` also ignores **`composer.json`, `composer.lock`, `package.json`, `package-lock.json`** (`.gitignore:22-25`) and `.claude/` (`.gitignore:27`). (These files nevertheless exist in the working tree / repo history; the ignore entries mean local edits to them are not tracked by default — worth being aware of when onboarding.)
- **Consequence:** because `Account.js` is git-ignored, the built bundle is **not** delivered via git. It must be rebuilt on/after deploy — on this project it is pushed to the live server directly by the developer's save (§2.6).

## 2.5 Database connections expected (`config/database.php`)
- Default connection: `mysql` (`config/database.php:18`).
- Defined MySQL connections (all `driver => mysql`):
  - `mysql` — primary app DB (`:46-70`). Live value = `centralizer` (§2.6); example default in code = `forge`, `.env.example` = `message_app`.
  - `orders` — env `DB_*_ORDER_MANAGEMENT` (`:72-90`).
  - `ppc` — env `DB_*_PPC` (`:93-111`). Used by PPC data-sync / `Ppc\TestingController` (`routes/web.php:5`).
  - `accounts_management` — env `DB_*_ACCOUNTS_MANAGEMENT` (`:114-132`).
  - `order_management` — env `DB_*_ORDER_MANAGEMENT` (duplicate of `orders`, same env keys) (`:134-152`).
  - Also `pgsql` and `sqlsrv` scaffolding (unused) (`:156-184`).
- **`.env.example` only defines the primary `DB_*` keys** (`.env.example:11-16`); the `orders`/`ppc`/`accounts_management`/`order_management` env keys are **not** present in `.env.example`, so a new developer must add them (they fall back to `127.0.0.1`/`forge` defaults otherwise). These are cross-database integrations (order management, PPC, accounts) beyond the centralizer's own schema.

## 2.6 Deployment reality (from REQ-04-D05 archive)

> Source: `...\source_documents\REQ-04_ledsone-centralizer-user-skill\skills\2026-06-19__abiraj__blos__REQ-04-D05.md` — Metadata + Environment (§0/§1) and §3 "Deploy ordering".

- **Live server:** XAMPP/Linux (LAMPP) at **`/opt/lampp/htdocs/ledsone-centralizer`**; live URL `https://centralizer.vintageinterior.co.uk` (D05 metadata + §1 Environment).
- **Live MySQL database:** **`centralizer`** (D05 §1 Environment, §0).
- **Local `.env` is empty**; the frontend is built locally with `npm run development` → `public/js/Account.js` (git-ignored) (D05 §1).
- **"save = live":** the developer's saves land **directly on the live server**, including the built bundle. So after a frontend build, "save = live." **PHP controller changes are live once saved.** (D05 §1 Environment.)
- **`php artisan optimize:clear`** only needed when a cached route/opcode is **stale** (D05 §1, §3).
- **The one exception — DB DDL:** the **web/app DB user lacks `ALTER`** (MySQL error `#1142`), so any `ALTER`/DDL (e.g. the D05 `drop_threshold_snapshot_columns.sql` column drop) must be run **as a privileged DB account**, and DDL must ship **together with** the code that depends on it, then `optimize:clear` (D05 §3 "Deploy ordering", §4 Gap).

### Deploy runbook (condensed)
1. Build frontend locally: `npm run production` (or `development`) → regenerates `public/js/Account.js`.
2. Save/sync changed PHP + the rebuilt bundle to `/opt/lampp/htdocs/ledsone-centralizer` (direct-to-server; "save = live").
3. If a route/config/opcode cache is stale: `php artisan optimize:clear`.
4. **If the change includes DB DDL (ALTER/CREATE/DROP):** run the SQL as a **privileged** MySQL account (not the web user) on DB `centralizer`, deployed **with** the matching code, then `php artisan optimize:clear`.
5. No migrations pipeline is relied upon for DDL in practice — hand-run SQL under a privileged account is the documented path (D05 §3–§4).

## 2.7 Testing
- `phpunit.xml` defines `Unit` (`./tests/Unit`) and `Feature` (`./tests/Feature`) suites (`phpunit.xml:7-14`).
- Test env overrides: `APP_ENV=testing`, `BCRYPT_ROUNDS=4`, `CACHE_DRIVER=array`, `SESSION_DRIVER=array`, `QUEUE_CONNECTION=sync`, mail `array` (`phpunit.xml:20-30`). The sqlite in-memory DB lines are **commented out** (`phpunit.xml:24-25`) — tests run against the configured MySQL unless overridden.

---

# Security findings for technical review
**(FINDINGS ONLY — for Sajeesan review. Nothing was fixed. Facts + file:line + risk.)**

| ID | Severity | Finding | Evidence | Risk |
| :- | :------- | :------ | :------- | :--- |
| **F-1** | **HIGH** | `POST /api/add-new-users` is a **public, unauthenticated** registration endpoint (sits above the auth group). | `routes/api.php:16` (vs group start `:24`) | Anyone on the internet can create accounts. |
| **F-2** | **HIGH** | Registration accepts `role` incl. `admin` from the request body (`nullable|in:admin,cashier,domain_owner`); combined with F-1, an anonymous caller can **self-register as admin**. | `AuthController.php:104`, `:123` | Privilege escalation to full admin. |
| **F-3** | **MEDIUM** | Password policy is `min:6` only; no complexity/breach check. | `AuthController.php:106` | Weak passwords accepted. |
| **F-4** | **MEDIUM** | No dedicated throttle on `/login` or `/add-new-users`; only a blanket `throttle:200,1` (200/min per IP). The finer `throttle:api` (60/min) limiter defined in `RouteServiceProvider` is **not wired** to the active group. | `app/Http/Kernel.php:45`; `RouteServiceProvider.php:46-51` | Credential brute-force / mass account creation feasible within 200/min. |
| **F-5** | **MEDIUM** | CORS allows all origins **with credentials**: `allowed_origins => ['*']` + `supports_credentials => true`. | `config/cors.php:22, 32` | Invalid/over-permissive CORS; unsafe if any cookie-based flow is added. |
| **F-6** | **LOW** | `domain_owner` middleware alias exists but is **applied to no route**; the role is effectively inert server-side. | `app/Http/Kernel.php:69`; no usage in `routes/api.php` | Dead access control; `domain_owner` users are treated like any non-admin. |
| **F-7** | **LOW/MEDIUM** | Client "Sign out" clears only local/session storage and does **not** call `POST /api/logout`, so `user.token` remains valid server-side until overwritten by a new login. | `Header.vue:232-240` (live; `Sidebar.vue:40-47` is unimported dead code with identical logic) vs server logout `AuthController.php:174-200` | Token not revoked on normal logout; a leaked token stays usable. |
| **F-8** | **LOW** | `is_active` defaults to **true** when `user_status` is null/empty. | `User.php:91-98` | Users with unset status are implicitly active; a blanked status re-activates a user. |
| **F-9** | **LOW** | Two independent client token-resolution paths (`userSession.authHeaders()` and `Api.js`) read auth from storage differently (bucket-aware vs `localStorage||sessionStorage`). | `userSession.js:76-82`; `Api.js:105-109` | Divergence risk (the "wrong role/thresholds" class of bug the bucket abstraction was added to fix). |
| **F-10** | **MEDIUM** | Third-party secrets committed in `.env.example`: Pusher `PUSHER_APP_SECRET`/key/id and an `EBAY_API_TOKEN`. | `.env.example:37-50` | Real-looking credentials in a tracked example file; should be redacted/rotated. |
| **F-11** | **LOW** | Debug/utility public routes left in production routing: `GET /api/test` (dumps **all users** via `AuthController@TEst`) and `GET /api/warehouse-location-wise-stock-update`, both unauthenticated; `GET /api/configurations` is also public. | `routes/api.php:18-22`; `AuthController.php:82-91` (`TEst` returns `User::all()`) | `/api/test` leaks the entire user table (incl. hashes are hidden by `$hidden`, but emails/roles/domains exposed). |
| **F-12** | **INFO** | Token = `Str::random(32)` stored plaintext in `user.token`; mutator truncates to exactly 32 chars (`substr(...,0,32)`), coupling generation length to storage length. | `AuthController.php:55`; `User.php:105-112` | Plaintext bearer tokens in DB (not hashed); brittle length coupling. |

> Note on `$hidden`: `User::$hidden = ['user_password', 'token']` (`User.php:22`) hides the password hash and token from JSON serialization, which mitigates F-11's exposure to *credentials* — but `/api/test` still returns names/emails/roles/domains/status of all users to anyone.

---

*End of REQ-04-D07 (DRAFT). Prepared read-only against the ledsone-centralizer working tree on branch `claude/dazzling-lehmann-32c5a5`. Deployment facts cited from REQ-04-D05 archive. No source files were modified.*


---

# PART H — VERIFICATION FINDINGS

---

# REQ-04-D07 — Verification Findings: Four Open Questions + Tracker Cross-Check

| Field | Value |
|---|---|
| **Date** | 2026-07-07 |
| **Deliverable** | REQ-04-D07 |
| **Project** | PRJ-2026-003_blos-project-sentinel |
| **Status** | DRAFT |
| **Repository verified** | `C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer` |
| **HEAD at verification** | `bc1204a` ("Drop redundant previous_value/change_reason from thresholds table"), branch `Abiraj` |
| **Method** | Read-only: `Grep` over working tree, `git log --all` pickaxe (`-S` / `-G`), `git show` of historical revisions. No files modified. |

Every verdict below is CONFIRMED-EXISTS or CONFIRMED-ABSENT — no "unknown"s remain.

---

## Q1 — HIGH-impact threshold approval workflow (`threshold_change_requests`)

### Verdict: **CONFIRMED-ABSENT** (in current code) — it *did* exist and was **deliberately removed on 2026-06-17** (commit `f8804b8`). The DB table and migration survive as orphans.

### Search trail
1. `grep -ri "ThresholdChangeRequest|threshold_change_request"` across the whole repo → hits only in `DATABASE_SCHEMA.md` (doc), `docs/sql/align_threshold_fk_columns.sql` (SQL script), and `database/migrations/2026_04_28_000001_create_threshold_change_requests_table.php` (migration). **Zero hits in `app/`, `routes/`, `resources/js/`.**
2. `grep -ri "approve|approval|impact|changeRequest|change_request|requires_approval"` across `app/` → only passive column names: `approver`/`management_approval`/`approved_by` validation strings in `ThresholdConfigurationController.php` (lines 476–477, 519–520, 550, 587, 612, 950–951, 962) and model `$fillable` arrays (`app/Models/Threshold.php:21`, `app/Models/ThresholdVersion.php:20`). These are plain text columns saved on rows — **no workflow logic, no status transitions, no create/approve/reject of `threshold_change_requests` rows.**
3. Same grep across `resources/js/` (all Vue components) → matches only in `ThresholdConfigurator.vue`: table column headers/inputs for `approver`, `management_approval`, `approved_by` (lines 325, 357–358, 422, 515–516, 623) and **dead CSS** (`.tc-impact*` classes, lines 3631–3722, with no template markup using them). No `change-requests` API call anywhere in the frontend.
4. `app/Models/` directory listing → `ThresholdChangeRequest.php` **does not exist** today.
5. Route file `routes/api.php` (all 119 lines read) → no `change-requests`, no `approve`, no `reject` route.
6. Git pickaxe: `git log --all --oneline -S "ThresholdChangeRequest"` → 4 commits: `f9492de`, `09c85d7`, `5938fcf`, `f8804b8`.

### Timeline evidence
| Date | Commit | Event |
|---|---|---|
| 2026-04-28/29 | migration `2026_04_28_000001`, `f9492de` (digitwebabiraj) | Table + `App\Models\ThresholdChangeRequest` model created |
| 2026-04-29 | `09c85d7` | Full workflow live. Proof — `git show 09c85d7:routes/api.php` lines 34, 49–50: `GET change-requests`, `POST change-requests/{id}/approve`, `POST change-requests/{id}/reject`. `git show 09c85d7:app/.../ThresholdConfigurationController.php`: `changeRequestsIndex()` (line 162), `changeRequestsApprove()` (line 188, sets `status='approved'`), `changeRequestsReject()` (line 206), and `thresholdsUpdate` creating `ThresholdChangeRequest::create([...])` with `impact_snapshot` (lines 476–497) |
| 2026-06-17 | `f8804b8` (digitwebabiraj, "Migrate threshold config to new BLOS schema...") | Commit message explicitly: "**remove mappings/dependencies/change-request/impact-approval; thresholds save immediately + log version row**". Diffstat deletes `app/Models/ThresholdChangeRequest.php` (−15) and `app/Models/ThresholdDependency.php` (−27) |
| 2026-07-07 (today) | HEAD `bc1204a` | No code path reads or writes `threshold_change_requests` |

### Defect-shaped findings — for Sajeesan review
- **Orphaned table/migration:** `database/migrations/2026_04_28_000001_create_threshold_change_requests_table.php` still creates the table, but no application code will ever insert into it. Fresh installs get dead schema.
- **Stale in-repo doc:** `DATABASE_SCHEMA.md` (committed `5938fcf`, 2026-06-11 — *six days before* the removal commit and never updated since) still documents the approval workflow as live ("Branch A — requires approval: insert a `threshold_change_requests` row (`status=pending`, ...)", line 467; section 4.8, lines 210–211).
- **Dead CSS:** `ThresholdConfigurator.vue` lines 3631–3722 keep the `.tc-impact*` style block from the removed impact-preview UI.

---

## Q2 — Impact preview (`thresholdsImpactPreview`)

### Verdict: current code **CONFIRMED-ABSENT**; git history **CONFIRMED-EXISTS** (added ~2026-04-29, removed 2026-06-17 by `f8804b8`).

### Search trail
1. `grep -ri "thresholdsImpactPreview|impactPreview|impact-preview"` across the whole repo (all file types) → **no matches**.
2. `grep -ri "impact"` in `app/` → only `impact_level`/`impact_description` nullable-validation leftovers? No — actually zero `impact_*` fields remain in the current controller (the only "impact" hits in `app/` are none; see Q1 trail item 2 — hits were `approver`/`approved_by` only). In `resources/js/` → only dead `.tc-impact*` CSS (Q1).
3. Git pickaxe: `git log --all --oneline -S "thresholdsImpactPreview"` → 2 commits: `09c85d7` (present), `f8804b8` (removed).

### Evidence
- Existed: `git show 09c85d7:routes/api.php` line 33: `Route::get('thresholds/{thresholdId}/impact-preview', [ThresholdConfigurationController::class, 'thresholdsImpactPreview']);` and `git show 09c85d7:app/.../ThresholdConfigurationController.php` line 113: `public function thresholdsImpactPreview(Request $request, $thresholdId)` — computed HIGH/MEDIUM/LOW from `threshold_dependencies` (lines 127–152).
- Removed: `f8804b8` commit message ("remove ... impact-approval") and diffstat (controller rewritten, −812/+~800 lines net replacement; `ThresholdDependency.php` deleted). Today's `routes/api.php` and controller contain no impact-preview method or route (full route file read; controller grepped).

**For Sajeesan review:** any consumer or document still referring to an impact-preview endpoint is referencing removed functionality.

---

## Q3 — Consumer GET API (`/thresholds/{key}`, `/thresholds/snapshot`, `/thresholds/{key}/history`, `/thresholds/since/{timestamp}`, `/rules/{rule_id}`, `BLOS_API_KEY`)

### Verdict: **CONFIRMED-ABSENT** — in current code **and in the entire git history (all branches)**. These endpoints have never existed in this repository.

### Search trail
1. `grep -ri "BLOS_API_KEY"` whole repo → **no matches**. `grep -ri "api_key|apikey|bearer"` in `.env.example` + `config/*.php` → only the stock Laravel Sanctum comment (`config/sanctum.php:31`). No custom API-key auth anywhere.
2. `grep -ri "snapshot"` whole repo → only FileManager.vue localStorage snapshot-diff helpers, `impact_snapshot` migration column, and SQL/doc files. `grep -r "/since/"` → no matches.
3. Full read of `routes/api.php` (119 lines) — the only threshold routes are the admin/session-token `threshold-config/*` group (lines 35–78). `routes/web.php` — only `/testData` (PPC) and the SPA catch-all. `routes/channels.php`, `routes/console.php` — nothing relevant.
4. Git pickaxe, all branches: `git log --all --oneline -S "BLOS_API_KEY"` → empty. `-S "/since/"` → empty. `-S "thresholds/snapshot"` → empty. `-S "thresholds/domain"` → empty. `-S "rules/domain"` → empty. `-S "history" -- routes` → empty. `git log --all -G "Route::get\('/?rules" -- routes` → empty.
5. Auth model check: the only bearer mechanism is `app/Http/Middleware/CheckAuthMiddleware.php` (line 18: `User::where('token', $token)->first()`) — a per-user session token issued at login (`AuthController::login` line 55, `Str::random(32)`), not a service API key.

### Defect-shaped finding — for Sajeesan review
The imported tracker (`skill_requirement_tracker.md`, Stage 2, lines 111–126) marks all nine consumer endpoints **and** "Bearer token (BLOS_API_KEY) authentication" as `DONE`. Git history across all branches shows **none of these routes were ever committed**. The Stage 2 `DONE` verdict is not supported by any commit; at best it conflated the internal admin UI API (`/api/threshold-config/*`, session-token gated) with the specified consumer GET API. **Stage 2 should be re-classified (proposed: `GAP`).**

---

## Q4 — Registration control (public `POST /api/add-new-users` vs "SPA registration removed — admin-controlled only", commit `0956069`)

### Verdict: **CONFIRMED-EXISTS** — the public, unauthenticated registration endpoint exists today (`routes/api.php:16`) and is **not a regression: it has been public since the day it was created and was never gated or removed**. Commit `0956069` exists but only removed the *frontend* Register page. The tracker claim "admin-controlled only" was never true at the API layer.

### Search trail
- `git show 0956069 --stat` — commit exists: `2026-04-29, digitwebabiraj, "fix(account-ui): align session storage with token and remove SPA signup"`. Touches **only** `resources/js/Account/*` (deletes `Pages/auth/Register.vue`, −912 lines; edits `Router.js` to redirect `/register` → `/login`). **`routes/api.php` and `AuthController.php` are not in the diffstat.**
- `git log --all --follow --oneline -- routes/api.php` → 10 commits; `git log --all -G "add-new-users" -- routes/api.php` → exactly **one** commit ever touched that string: `24169cf 2026-04-16 sajeesans2 "updates"` (`-G` catches moves/edits as well as add/remove, so the line was never relocated into a middleware group).
- `git show 24169cf:routes/api.php` line 13: `Route::post('/add-new-users', [AuthController::class, 'register']);` — already **above** the `CheckAuthMiddleware` group (line 17). Same shape at `09c85d7` (line 14) and at HEAD today (line 16, group opens at line 24).
- `git log --follow -- app/Http/Controllers/auth/AuthController.php` → first `sajeesans2 2026-04-16`, last `sajeesans2 2026-04-29`. Full read of `AuthController::register()` (lines 99–146): **no auth check, no invite token, no feature flag, no admin gate of any kind.**

### Timeline
| Date | Commit | State of registration |
|---|---|---|
| 2026-04-16 | `24169cf` (sajeesans2) | `POST /api/add-new-users` created **public** (outside all middleware) + SPA `Register.vue` page exists |
| 2026-04-29 | `0956069` (digitwebabiraj) | SPA `Register.vue` and `/register` route removed (frontend only). API route untouched — still public |
| 2026-05 → today | — | Route never modified again. HEAD `routes/api.php:16` still public. Admin-gated alternative exists in parallel: `POST /api/users` → `UserController::store` inside `admin` middleware (`routes/api.php:115`, alias `admin` → `EnsureUserIsAdmin`, `app/Http/Kernel.php:68`) |

### Defect-shaped finding — HIGH severity, for Sajeesan review
`AuthController::register()` line 104 validates `'role' => 'nullable|in:admin,cashier,domain_owner'` and line 123 persists it (`$request->get('role', 'cashier')`). Combined with the unauthenticated route, **anyone who can reach the API can create an active `admin` account with a valid token** (line 124 `is_active => true`, line 125 token issued immediately). The tracker's Stage 5 claim "SPA registration removed — admin-controlled only `DONE` — commit 0956069" (line 201) describes only the UI; the backend contradicts "admin-controlled only". Recommend closing or admin-gating `/add-new-users` (an admin-gated `POST /api/users` already exists).

---

## Section 5 — Cross-check of tracker Stage claims (Stages 1, 2, 4, 5) against today's code

Tracker: `evidence/source_documents/REQ-04_ledsone-centralizer-user-skill/gaps_and_logics/skill_requirement_tracker.md` (last updated 2026-05-20). The schema migration of 2026-06-17 (`f8804b8`) and the column drop of `bc1204a` invalidated many `DONE` markings. Findings only — nothing fixed.

| # | Tracker claim (line) | Tracker status | Today's code | Mismatch verdict |
|---|---|---|---|---|
| 5.1 | Stage 2 — all 9 consumer GET endpoints + BLOS_API_KEY (111–126) | `DONE` | Never existed in any commit (Q3) | **NO LONGER / NEVER MATCHED — critical** |
| 5.2 | Stage 4 — `thresholdsImpactPreview()` API method (172) | `DONE` | Removed in `f8804b8` (Q2) | **NO LONGER MATCHES** |
| 5.3 | Stage 4 — ThresholdChangeRequest model / HIGH-impact approval workflow (173, 176) | `DONE` | Model + workflow deleted in `f8804b8` (Q1) | **NO LONGER MATCHES** |
| 5.4 | Stage 4 — impact preview fires in UI (174, 177) | `DONE` | No impact UI; only dead `.tc-impact*` CSS remains | **NO LONGER MATCHES** |
| 5.5 | Stage 5 — "HIGH-impact save replaced with Submit for Approval" (196) | `DONE` | `f8804b8`: "thresholds save immediately + log version row" | **NO LONGER MATCHES** |
| 5.6 | Stage 5 — "Change reason mandatory — save disabled until 10+ characters" (195); Stage 1 — "`change_reason` NOT NULL, min 10-char validation" (96) | `DONE` | Controller line 514–516: "TEMP: change_reason made optional", `'change_reason' => 'nullable|string|max:1000'`; column dropped from `thresholds` entirely in `bc1204a` | **NO LONGER MATCHES** |
| 5.7 | Stage 1 — "`previous_value` auto-captured before every UPDATE" (95) | `DONE` | `previous_value` column dropped from `thresholds` in `bc1204a` (history lives only in `threshold_versions`) | **NO LONGER MATCHES** (intent preserved via versions table, but the stated mechanism is gone) |
| 5.8 | Stage 1 — FK `thresholds.rule_id` → `business_rules.rule_id` NOT NULL (93); thresholds table has `rule_id` FK (89) | `DONE` | `app/Models/Threshold.php:21` fillable has **no `rule_id`**; linkage moved to junction table `rule_threshold_mapping` (`f8804b8`, `docs/sql/align_threshold_fk_columns.sql`) | **NO LONGER MATCHES** |
| 5.9 | Stage 1 — `threshold_dependencies` table + model (91) | `DONE` | `ThresholdDependency.php` deleted in `f8804b8`; no migration for the table exists in `database/migrations/` | **NO LONGER MATCHES** |
| 5.10 | Part 4 — `business_rule_categorical_mapping` 69 records (423) | `PARTIAL` | Model `BusinessRuleCategoricalMapping.php` deleted in `f8804b8`; concept replaced by `condition_logics` / `rule_threshold_mapping` | **NO LONGER MATCHES** |
| 5.11 | Stage 5 — "SPA registration removed — admin-controlled only" (201) | `DONE` | UI removed, but public API registration with self-selectable `admin` role remains (Q4) | **PARTIALLY FALSE — HIGH severity** |
| 5.12 | Modules table (62–68) lists 4 SPA modules | — | `Router.js:19` now also has `/rule-builder` (`RuleBuilder.vue`, admin-only), added after tracker date | Stale by omission (informational) |
| 5.13 | Stack table (51–56): "Database MySQL / PostgreSQL" | — | `config/database.php` default `mysql`; no pgsql connection configured with env values in active use; Stage 1 header says "five-table PostgreSQL database" (84) but app-owned migrations run on MySQL (`DATABASE_SCHEMA.md:19` "mysql — app-owned") | Discrepancy (informational) |

**Additional finding (not in tracker) — for Sajeesan review:** `routes/api.php` imports and binds `CategoryController`, `ProductController`, `InventoryController`, `SaleController`, `ReportController`, `ImageController` (lines 5–11, 28–33, 97–112), but **none of these classes exist anywhere in `app/` and never have** (`git log --all` on each path → empty). Every one of those POS routes will fatal-error (`Class not found` / 500) when hit, and `php artisan route:cache` would fail. See the companion shared-modules inventory (REQ-04-D07) for the fence-off of that POS code area.

**Stages 1, 4, 5 proposed re-marking (for Sajeesan review):** Stage 1 `DONE` → `PARTIAL` (schema materially changed since claim), Stage 2 `DONE` → `GAP` (never built), Stage 4 `PARTIAL` → `REMOVED/GAP` (engine deleted), Stage 5 `DONE` → `PARTIAL` (approval-flow and change-reason items no longer hold; registration claim false at API layer).

---

*Prepared as REQ-04-D07 (DRAFT) — all claims carry file:line or commit evidence; verification was strictly read-only.*

---

## Addendum (2026-07-07, closure review)

Minor code-comment defect noted for completeness (not a documentation gap, for Sajeesan awareness): `app/Http/Controllers/auth/AuthController.php` — the `me()` method (approx. lines 148-153) carries a mislabeled docstring reading "Handle logout request". The method actually returns the authenticated user profile; the logout handler is a separate method. A 3AM reader grepping for the logout handler by comment could be misled. Report only — not fixed by this task.


---

# PART I — SHARED-REPO MODULES INVENTORY

---

# REQ-04-D07 — Shared Modules Inventory (Non-BLOS Code in `ledsone-centralizer`)

> **Shared-repo modules — NOT part of the BLOS / Project Sentinel scope. Inventoried so a new person does not mistake them for BLOS work. Owner: see git authorship per row.**

| Field | Value |
|---|---|
| **Date** | 2026-07-07 |
| **Deliverable** | REQ-04-D07 |
| **Project** | PRJ-2026-003_blos-project-sentinel |
| **Status** | DRAFT |
| **Repository** | `C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer` @ `bc1204a` (branch `Abiraj`) |

## How "no Account-SPA UI page" was established (applies to every row)

The Account SPA route table is `resources/js/Account/Router.js` lines 16–24. Its complete page list is: `Dashboard`, `ThresholdConfigurator`, `OilConfigurator`, `RuleBuilder`, `FileManager`, `Login` (plus redirects). **No POS, PPC/ETL, order-management, inventory, or stock page exists in the SPA** — that single fact is the shared per-row evidence, cited as "Router.js 16–24" below. Additionally, a repo-wide grep of `resources/js/` for the module endpoints (`/products`, `/sales`, `/inventory`, `/reports`, `testData`, `warehouse-location-wise-stock-update`) returns no frontend callers.

Authorship format: `first-commit author, date → last-commit author, date` (from `git log --reverse --format="%an %ad" -- <path> | head -1` and `git log -1`).

---

## 1. POS / Catalog (products, categories, sales, images)

| Path | Purpose (one line) | Account-SPA UI? | Git authorship |
|---|---|---|---|
| `app/Models/Product.php` | POS product catalog model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/Category.php` | POS product category model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/Sale.php` | POS sale header model | None — Router.js 16–24 | sajeesans2 2026-04-16 → digitwebabiraj 2026-04-21 (touch only) |
| `app/Models/SaleItem.php` | POS sale line-item model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/Inventory.php` (root) | POS per-product stock quantity model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/Image.php` | Product/category image attachment model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/ImageType.php` | Image type lookup model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `routes/api.php` lines 5–11, 28–33, 97–112 (POS route group) | REST routes for products/categories/sales/inventory/reports/images | None — Router.js 16–24; **no callers in `resources/js/`** | routes introduced by sajeesans2 2026-04-16 (`24169cf`) |
| `database/migrations/2023_01_17_081228_create_product_table.php` | Creates the POS `product` table | n/a (migration) | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |

**Caution (for Sajeesan review, reported only):** the controllers those POS routes point at — `Api\CategoryController`, `Api\ProductController`, `Api\InventoryController`, `Api\SaleController`, `Api\ReportController`, `Api\ImageController` — **do not exist in `app/` and never existed in git history** (`git log --all -- <each path>` is empty). The routes are dangling; hitting them 500s. Documented in the companion verification-findings file, Section 5.

## 2. PPC / ETL (Amazon, eBay, Google Ads centralized ETL)

| Path | Purpose (one line) | Account-SPA UI? | Git authorship |
|---|---|---|---|
| `app/Http/Controllers/Ppc/TestingController.php` | Dev/testing endpoint that copies Amazon performance data into PPC ETL tables (`/testData`) | None — Router.js 16–24 | gajan 2026-05-05 → gajan 2026-05-11 |
| `app/Console/Commands/Ppc/PpcEtlData.php` | Artisan `command:PpcEtlData` — saves campaigns, ad groups, asset groups, assets, performance to ETL tables | None (CLI) | gajan 2026-05-05 → GAJAN 2026-05-08 |
| `app/Models/CentralizedEtlData/Ppc/Amazon/` (7 models: AmazonAdGroups, AmazonAds, AmazonCampaigns, AmazonPerformanceData, AmazonProducts, AmazonSellerStores, AmazonStoreMarketPlacesDev) | Amazon ads source-data models, all on `ppc` DB connection (`protected $connection = 'ppc'`) | None — Router.js 16–24 | gajan 2026-05-05 → GAJAN 2026-05-08 (directory-level) |
| `app/Models/CentralizedEtlData/Ppc/Ebay/` (6 models: EbayAdGroups, EbayAds, EbayCampaignReportData, EbayCampaigns, EbayPerformanceData, EbaySellerStores) | eBay ads source-data models (`ppc` connection) | None — Router.js 16–24 | gajan 2026-05-05 → GAJAN 2026-05-08 |
| `app/Models/CentralizedEtlData/Ppc/GoogleAds/` (8 models: GoogleAccounts, GoogleAdGroups, GoogleAssetGroups, GoogleAssetGroupsAssets, GoogleAssetsPerformance, GoogleCampaignPerformance, GoogleCampaigns, GoogleProductPerformance) | Google Ads source-data models (`ppc` connection) | None — Router.js 16–24 | gajan 2026-05-05 → GAJAN 2026-05-08 |
| `app/Models/CentralizedEtlData/Ppc/Common/` (5 models: MarketPlaces, PpcEtl, PpcEtlPerformanceData, Region, States) | Cross-channel ETL target tables + reference data (`ppc` connection) | None — Router.js 16–24 | gajan 2026-05-05 → GAJAN 2026-05-08 |
| `routes/web.php` line 5 (`GET /testData`) | Web route to `TestingController::testData` (PPC ETL trigger) | None — Router.js 16–24 | route added by gajan 2026-05-05 (file last: gajan 2026-05-05) |
| `config/database.php` connection `'ppc'` (line 93) | Dedicated MySQL connection for PPC ETL schema | n/a (config) | config/database.php: sajeesans2 2026-04-16 → gajan 2026-05-05 |

## 3. Order-management / Inventory / Stock-sync

| Path | Purpose (one line) | Account-SPA UI? | Git authorship |
|---|---|---|---|
| `app/Http/Controllers/Inventory/StockController.php` | Warehouse/location-wise stock recalculation and sync (`WarehouseLocationWiseStockUpdate`, `GetInvStock`) | None — Router.js 16–24 | sajeesans2 2026-05-05 → sajeesans2 2026-05-05 |
| `app/Models/Inventory/InvProducts.php` | Order-management product model (`orders` DB connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 (directory-level) |
| `app/Models/Inventory/InvStock.php` | Stock rows on `orders` connection | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/InvProductCombo.php` | Combo/bundle product mapping (`orders` connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/InvProductMapping.php` | SKU mapping model (`orders` connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/ProductPK.php` | Product primary-key/lookup helper (`orders` connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/Warehouse.php` | Warehouse master (`orders` connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/LocationWiseStock.php` | Location-wise stock result table (**writes to local `mysql` connection**) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `routes/api.php` line 22 (`GET /warehouse-location-wise-stock-update`) | Stock-sync trigger route — **outside auth middleware (public)** | None — Router.js 16–24 | sajeesans2 (route group first authored 2026-04-16; stock line added ~2026-05-05) |
| `app/Jobs/CreateBulkShipments.php` | Queued job broadcasting order-update events (stub: `sleep(20)` + broadcast) | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Jobs/CreateBulkRuleRun.php` | Queued bulk-rule-run job (order pipeline stub) | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Events/OrderUpdateEvents.php` | Broadcast event for order updates (websockets) | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Events/MessageSent.php` | Generic broadcast message event (websockets) | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Http/Middleware/WebSocketMiddleware.php` | Websocket auth middleware for the broadcast stack | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `config/websockets.php` + `config/broadcasting.php` | Laravel-websockets / broadcast config supporting the order-event stack | n/a (config) | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `database/migrations/0000_00_00_000000_create_websockets_statistics_entries_table.php` | Websockets statistics table (broadcast infra) | n/a (migration) | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `config/database.php` connections `'orders'` (line 72), `'accounts_management'` (line 114), `'order_management'` (line 134) | External MySQL connections for order/stock/accounts systems | n/a (config) | sajeesans2 2026-04-16 → gajan 2026-05-05 |

## 4. Shared auth plumbing (dual-use — used by BLOS *and* the shared modules; do not refactor unilaterally)

| Path | Purpose (one line) | Account-SPA UI? | Git authorship |
|---|---|---|---|
| `app/Models/auth/User.php` | Legacy/secondary user model under `auth` namespace (not the one used by `CheckAuthMiddleware`, which uses root `App\Models\User`) | Login page only | sajeesans2 2026-04-16 → digitwebabiraj 2026-04-21 |
| `app/Models/User.php` (root) | Active user model (token auth) — **shared**: created for the POS/base app, later reused by BLOS | Login/Dashboard | sajeesans2 2026-04-16 → digitwebabiraj 2026-05-13 |
| `app/Http/Controllers/auth/AuthController.php` | Login/register/logout/configurations — created with the base app; BLOS SPA consumes login only | Login page | sajeesans2 2026-04-16 → sajeesans2 2026-04-29 |
| `database/migrations/2025_03_15_000001_add_token_to_users_table.php` | Adds `token` column for bearer auth | n/a | sajeesans2 2026-04-16 → digitwebabiraj 2026-04-21 |

---

## Authorship summary

- **POS/catalog, order-management/stock-sync, websockets, base auth:** created and owned by **sajeesans2** (bulk import commit `24169cf`, 2026-04-16; Inventory stock module 2026-05-05).
- **PPC/ETL (CentralizedEtlData, TestingController, PpcEtlData command):** created and owned by **gajan / GAJAN** (2026-05-05 → 2026-05-11).
- **BLOS work (thresholds, rules, file library, Account SPA)** is authored by **digitwebabiraj** — the only overlap with the rows above is incidental touches to shared auth files and `app/Models/Sale.php` (2026-04-21 formatting-era commit).

Nothing in this inventory has an Account-SPA page, and none of it is referenced by the BLOS threshold/rule/file-library controllers. Internals deliberately not documented further — out of BLOS scope.

*Prepared as REQ-04-D07 (DRAFT) — for Sajeesan review where flagged; verification was strictly read-only.*
