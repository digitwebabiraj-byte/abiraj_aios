# Evidence Note — Ledsone Centralizer User Skill File (REQ-04-D06)

Date: 2026-07-07
Supports: `../../final_outputs/REQ-04_ledsone-centralizer-user-skill/2026-07-07_ledsone-centralizer_user_skill.md`
Method: read-only repository scan (no code executed, no DB queried, no live requests) +
imported delivery archive. Scan performed 2026-07-07 against the local clone at
`C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer`.

## What was scanned

| Area | Files |
|---|---|
| Docs | `README.md`, `DATABASE_SCHEMA.md`, `MEMORY.md`, `docs/skill.md`, `docs/BLOS-Rule-Builder-*.{md,html}`, `docs/sql/*.sql`, `readme.txt`, `readme.json`, `database sample.txt` |
| Routes | `routes/api.php`, `routes/web.php`, `resources/js/Account/Router.js` |
| Controllers | `app/Http/Controllers/Api/ThresholdConfigurationController.php`, `AuthController.php`, `FolderFileController.php`, others enumerated |
| Middleware | `app/Http/Middleware/CheckAuthMiddleware.php`, `EnsureUserIsAdmin`, `app/Http/Kernel.php` |
| Models | all of `app/Models/` (18 root models + `CentralizedEtlData/`, `Inventory/`, `Ppc/`, `auth/` subdirs) |
| Services | `app/Services/FolderFileService.php` |
| Database | `database/migrations/` (7 files), `database/seeders/DatabaseSeeder.php` |
| SPA pages | `resources/js/Account/Pages/` (Dashboard, ThresholdConfigurator, OilConfigurator, RuleBuilder, FileManager, auth/Login, includes/Header, Loading) |
| Archive | all 19 imported files — see `2026-07-07_import_checksum_evidence.md` |

## Key verifications (claim → evidence)

The full claim-by-claim table lives in §11 of the skill file. Highlights:

- Versioned threshold update (epsilon `0.0000001`, version max()+1, transactional audit row):
  `ThresholdConfigurationController.php:486-553`.
- `change_reason` TEMP-optional with original `required|min:10` preserved as comment:
  `:513-516` — matches the deferral recorded in REQ-04-D05.
- Domain scoping: `allowedDomainsFor()` `:45-77`, filter `:96-114`, 403 message `:491`.
- Admin gating: `routes/api.php:41` group + `EnsureUserIsAdmin`; Rule Builder SPA gate
  `Router.js:19`.
- Exports: YAML `:819-835`, CSV `:837-873`; bulk import `:904-920, :971-1007, :1015+`.
- File Library reads vs admin writes: `routes/api.php:81-95`; upload metadata capture
  `FolderFileService.php:160-191`.
- Empty-by-design seeder: `database/seeders/DatabaseSeeder.php:15-19`.

## Findings that shaped VERIFIED / PARTIAL / UNPROVEN statuses

1. **CONTRADICTION — registration:** `POST /api/add-new-users` is registered OUTSIDE the auth
   middleware (`routes/api.php:16`), yet the imported tracker (Stage 5) records "SPA
   registration removed — admin-controlled only" (commit `0956069`). SPA-side there is indeed
   no Register.vue and `/register` redirects to `/login` (`Router.js:23`) — the API side is
   the open question. Escalated to Technical Reviewer.
2. **Approval workflow:** `threshold_change_requests` migration exists
   (`2026_04_28_000001_...`), but no controller methods creating/approving/rejecting requests
   were found; `thresholdsImpactPreview()` was not located. Tracker Stage 4 claims these DONE
   as of 2026-05-20 — code may have moved or been removed by later commits (D05 dropped
   snapshot columns on 2026-06-19). Marked UNPROVEN for current code.
3. **Consumer GET API** (`GET /thresholds/{key}`, `snapshot`, `history`, `since/{ts}` with
   `BLOS_API_KEY`) from tracker Stage 2: not present in current `routes/api.php`. Marked
   UNPROVEN.
4. **Stale artifact:** `database sample.txt` shows tables (`items`, `tasks`, `vault`, …) that
   do not exist in the current schema — recorded as outdated, excluded as evidence.
5. **No user-facing documentation existed anywhere** before this deliverable — basis of the
   GREEN duplicate-risk verdict (see
   `../../../duplicate_risk_reports/REQ-04_ledsone-centralizer-user-skill/2026-07-07_user_skill_duplicate_risk.md`).

## Integrity statement

No file in the `ledsone-centralizer` repository or the Desktop archive was created, modified,
or deleted by this task. All writes occurred inside
`projects/PRJ-2026-003_blos-project-sentinel/`. No git commit or push was performed.
