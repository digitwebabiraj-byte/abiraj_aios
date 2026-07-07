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
