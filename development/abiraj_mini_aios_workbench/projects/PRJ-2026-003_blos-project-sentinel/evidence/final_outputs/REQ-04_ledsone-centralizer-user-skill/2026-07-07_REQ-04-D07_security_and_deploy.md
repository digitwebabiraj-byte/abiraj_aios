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
