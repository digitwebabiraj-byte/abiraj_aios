# SYSTEM_REFERENCE — LEDsONE Centralizer (BLOS / Project Sentinel)

Project: PRJ-2026-003_blos-project-sentinel · Last updated: 2026-07-07
Audience: a leader or new engineer who needs to know what the system actually does.

> Canonical deep detail lives in two places — this file summarises and points, it does not
> duplicate:
> **(1)** the user skill file
> `evidence/final_outputs/REQ-04_ledsone-centralizer-user-skill/2026-07-07_ledsone-centralizer_user_skill.md`
> (roles, workflows, business rules, evidence map), and
> **(2)** the imported requirements tracker
> `evidence/source_documents/REQ-04_ledsone-centralizer-user-skill/gaps_and_logics/skill_requirement_tracker.md`
> (build-stage status, gap analysis, activity log as of 2026-05-20).

## 1. What the system is

LEDsONE Centralizer is the company's central admin/operations hub (Laravel 9 API + Vue 2
Account SPA) hosting the **BLOS — Business Logic Operating System**: a governed registry of
business rules (`BL-##`), their numeric thresholds (`TH-##`), glossary metrics (`GL-##`),
rule↔threshold mappings, and an append-only version history — plus a **Central File Library**
(SkillVault) and catalog/POS endpoints. It reads/writes several company MySQL databases
(source: repo `DATABASE_SCHEMA.md`).

## 2. Stack and deployment

| Layer | Detail |
|---|---|
| Backend | Laravel 9, controllers in `app/Http/Controllers/Api/` |
| Frontend | Vue 2 SPA, `resources/js/Account/` (entry `Account.js`, routes `Router.js`) |
| Build | Laravel Mix — `npm run development` / `production` → `public/js/Account.js` (git-ignored) |
| DB | MySQL `centralizer` (+ external orders/ppc connections) |
| Auth | Custom bearer token (`user.token`), `CheckAuthMiddleware`; roles admin / cashier / domain_owner |
| Live | https://centralizer.vintageinterior.co.uk · server `/opt/lampp/htdocs/ledsone-centralizer` (per REQ-04-D05 delivery record) |
| Repo | GitLab `sajeesans2/ledsone-centralizer`, branch `Abiraj` |

## 3. Functional modules

| Module | SPA route | What it does |
|---|---|---|
| Dashboard | `/` | Role-aware landing workspace |
| Threshold Configurator | `/threshold-configurator` | Domain-scoped threshold viewing/editing; admin CRUD tabs for all BLOS reference tables; version history; YAML/CSV export; CSV bulk import |
| Business OS (OIL) | `/oil-configurator` | Domain-grouped threshold registry view/edit |
| Rule Builder | `/rule-builder` (admin) | Drag-drop authoring of rule condition logic; codes validated against glossary/thresholds; discard-guard on unsaved edits |
| File Manager | `/file-manager` | Folder-tree file library; text preview; file/ZIP download; admin upload/replace (diff-review confirm)/rename/move/delete |

## 4. Data model (own schema)

BLOS: `business_rules`, `condition_logics`, `glossary`, `rule_threshold_mapping`,
`thresholds`, `threshold_versions` (append-only audit), `threshold_change_requests`
(approval queue — table only, workflow code unproven), `user_domain_access`.
File Library: `folders`, `files`. Users: legacy `user` table via accessor-mapped
`app/Models/User.php`. Full column detail: repo `DATABASE_SCHEMA.md` and `docs/sql/*.sql`.

## 5. Core protocol (threshold change)

Value edit → domain permission check → change detected only if |Δ| > 0.0000001 →
transaction: update row, stamp `last_changed_by/at` (UTC), `version` +1 (never skipped,
never reset), insert `threshold_versions` row (old/new value, reason). `change_reason` is
temporarily optional (recorded deferral). Deletion cascades history + mappings.

## 6. Open items — RE-VERIFIED against today's code (D07, 2026-07-07)

The four items D06 could not confirm are now settled by direct code + git-history checks
(see `evidence/final_outputs/.../2026-07-07_REQ-04-D07_verification_findings.md`):

- **Approval workflow — REMOVED BY DESIGN**, not missing. Commit `f8804b8` (2026-06-17)
  dropped the change-request/impact-approval code during the BLOS schema migration.
  `threshold_change_requests` is now an orphaned table.
- **Impact preview — REMOVED BY DESIGN** by the same commit.
- **Consumer GET API (`BLOS_API_KEY`, snapshot, since/…) — NEVER BUILT** on any branch; the
  May tracker's "Stage 2 DONE" is incorrect.
- **Registration — public since creation** (`24169cf`, sajeesans2, base code), accepts
  `role=admin` unauthenticated → **P0 security item for Sajeesan** (not a regression).

The imported tracker is dated 2026-05-20 and pre-dates the June migration; where it disagrees
with the code, **the code wins**. Data-population gaps it lists (BL-## count,
`user_domain_access` rows) are DB-data questions, not code questions, and were not re-verified
against the live database by this documentation task.

## 7. The full D07 continuation package

For a new person taking this over without Abiraj, the keystone is
`evidence/final_outputs/REQ-04_ledsone-centralizer-user-skill/2026-07-07_REQ-04-D07_continuation_guide.md`,
backed by CODE_MAP, DATA_DICTIONARY, API_REFERENCE, UI_REFERENCE, SECURITY_AND_DEPLOY,
VERIFICATION_FINDINGS and SHARED_MODULES_INVENTORY (all REQ-04-D07). The user-facing
how-to-use document is the D06 skill file (updated in place, same ID).

Current-code evidence supersedes the tracker; tracker retained only for historical context.
