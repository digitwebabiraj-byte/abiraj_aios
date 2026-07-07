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
