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
