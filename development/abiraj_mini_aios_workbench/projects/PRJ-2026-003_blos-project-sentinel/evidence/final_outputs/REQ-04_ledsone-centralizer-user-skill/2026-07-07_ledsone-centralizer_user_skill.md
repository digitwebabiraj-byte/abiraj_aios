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
| **status** | **VALIDATED — CLOSED** (validated by Satheewaran, user, 2026-07-07; adversarial fact-check CORRECT; closure gates PASS). No pending next steps. |
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
