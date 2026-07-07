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
