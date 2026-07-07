# skill.md — Ledsone Centralizer · Project Sentinel
## LLM-Queryable Requirements & Track Status File
### Last Updated: 2026-05-20 · Maintained by J. Abiraj

> **Read this file at the start of every session.**
> Do not contradict recent decisions. Do not re-engineer solved problems.
> Append to the Activity Log after every session (newest-first).

---

## HOW TO USE THIS FILE (LLM Query Guide)

This file is structured so an LLM can answer:
- "Is requirement X complete?" → Check the Requirements Registry sections
- "Is the project on track?" → Check the Track Status Summary
- "What work was done on date Y?" → Check the Activity Log
- "What gaps exist?" → Check the Gap Analysis section
- "What is the current DB state?" → Check the Database State section

**Status labels used throughout:**
- `DONE` — requirement fully met, evidence confirmed
- `PARTIAL` — requirement in progress or partially met
- `GAP` — requirement not yet met, blocking or at-risk
- `NOT STARTED` — requirement not yet begun
- `IN PROGRESS` — actively being worked on
- `DEFERRED` — deliberately pushed to a later phase

---

## Project Identity

| Attribute | Detail |
|---|---|
| **Project Name** | BLOS — Business Logic Operating System (Project Sentinel) |
| **Repository** | `ledsone-centralizer` |
| **Platform** | Ledsone Centralizer — Operations Hub |
| **Developer** | J. Abiraj |
| **Application Type** | Laravel + Vue 2 Account SPA |
| **Last Engineering Activity** | 2026-05-20 |
| **Requirement Source (BLOS)** | BLOS Build Guide v1.0 (MD Requirement Document) |
| **Requirement Source (SkillVault)** | SkillVault System Design v1.0 (May 14, 2026) |
| **Requirement Source (OIL v5)** | oil_configurator_v5.html (reference design) |
| **Classification** | Confidential — Internal Distribution Only |

---

## Stack

| Layer | Technology | Path |
|---|---|---|
| Backend API | Laravel (PHP) | `app/Http/Controllers/Api/` |
| Account SPA | Vue 2 | `resources/js/Account/` |
| Build Pipeline | Laravel Mix | `npm run development / production` |
| SPA Entry Point | Account.js → Account Router | `resources/js/Account.js` |
| Layout Controller | App.vue — `isFullBleedMain()` | `resources/js/Account/App.vue` |
| Database | MySQL / PostgreSQL | Relational — FK-enforced schema |

---

## Modules

| Module | Route | Component | Function |
|---|---|---|---|
| Dashboard | `/` | `Dashboard.vue` | Role-aware workspace portal with live metrics and tool navigation |
| Threshold Configurator | `/threshold-configurator` | `ThresholdConfigurator.vue` | Admin surface for business rule thresholds, mappings, and versioning |
| Business OS Configurator | `/oil-configurator` | `OilConfigurator.vue` | OIL v5 rules registry: 8 domains, 80 thresholds, YAML export |
| Central File Library | `/file-manager` | `FileManager.vue` | Hierarchical file management with folder navigation, upload, and ZIP export |

---

---

# PART 1 — BLOS REQUIREMENTS & TRACK STATUS

## BLOS Build Guide — 9 Stage Progress Tracker

Source: `BLOS_Build_Guide_Abiraj_v1.0.docx`
Rule: Every stage must be signed off by Sajeesan (DTL) before the next begins.

---

### STAGE 1 — Schema & Database `DONE`

Build the five-table PostgreSQL database.

| Checklist Item | Status |
|---|---|
| `business_rules` table — rule_id (BL-##), rule_name, description, condition_logic, decision_output, domain, business_owner, rationale, created_by, created_at, status | `DONE` |
| `thresholds` table — threshold_id (UUID), rule_id (FK NOT NULL), threshold_key, label, value, value_type, unit, direction, domain, domain_owner, last_changed_by, last_changed_at, effective_from, previous_value, change_reason, status, version | `DONE` |
| `threshold_versions` table (append-only ledger) — version_id, threshold_id, old_value, new_value, changed_by, approved_by, change_reason, timestamp, version_number | `DONE` |
| `threshold_dependencies` table — dependency_id, threshold_id, dependent_system, system_type, impact_level (HIGH/MEDIUM/LOW), impact_description, registered_by, registered_at, last_verified | `DONE` (table exists, 0 records — see Gap Analysis) |
| `threshold_change_requests` table — impact_snapshot (JSON), old_value, new_value, status, high_count, medium_count, low_count | `DONE` |
| FK constraint: `thresholds.rule_id` → `business_rules.rule_id` (NOT NULL — enforced at DB level) | `DONE` |
| `version` auto-increments by exactly 1 on every UPDATE (never skip, never reset) | `DONE` — commit `752d248` |
| `previous_value` auto-captured before every UPDATE | `DONE` — ThresholdVersion model |
| `change_reason` NOT NULL, minimum 10-character validation (DB + API + frontend) | `DONE` |
| DB indexes on `threshold_key`, `domain`, `status`, `effective_from` | `DONE` |
| Migration scripts version-controlled in repository | `DONE` |
| Sajeesan (DTL) sign-off on schema | *Not verifiable from daily summaries* |

**Stage 1 Verdict: `DONE` — all five tables created, constraints enforced, versioning logic confirmed.**

---

### STAGE 2 — API Layer `DONE`

Build the REST consumer API — GET-only for all consumers.

| Checklist Item | Status |
|---|---|
| `GET /thresholds` — list by domain, admin sees all, non-admin sees only their domains | `DONE` |
| `GET /thresholds/{key}` — single threshold with full `business_rule` block embedded | `DONE` |
| `GET /thresholds/domain/{domain}` — all active thresholds for a domain | `DONE` |
| `GET /thresholds/snapshot` — full export of all active thresholds | `DONE` |
| `GET /thresholds/{key}/history` — full version history | `DONE` |
| `GET /thresholds/{key}/dependencies` — impact level per dependent system | `DONE` |
| `GET /thresholds/since/{timestamp}` — thresholds changed after datetime | `DONE` |
| `GET /rules/{rule_id}` — full BL-## record | `DONE` |
| `GET /rules/domain/{domain}` — all rules for a domain | `DONE` |
| Bearer token (BLOS_API_KEY) authentication on ALL endpoints | `DONE` — CheckAuthMiddleware |
| Consumer API is GET-only — no POST/PUT/PATCH/DELETE | `DONE` — admin middleware group |
| Unknown key returns 404 (not null, not 0) | `DONE` |
| Response includes `business_rule` block (rule_id, condition_logic, decision_output) — not just value | `DONE` |
| `direction` field always present (max / min / target / exact) | `DONE` |
| `last_changed_date` always a UTC ISO timestamp | `DONE` |
| `version` always an integer (never string, never null) | `DONE` |
| API response time < 2 seconds | *Not confirmed from summaries* |
| 1-hour TTL cache — invalidates on threshold change | *Not confirmed from summaries* |
| OpenAPI/Swagger documentation | *Not confirmed from summaries* |
| API integration tests for all 8 endpoints | *Not confirmed from summaries* |
| Sajeesan (DTL) sign-off on API architecture | *Not verifiable from daily summaries* |

**Stage 2 Verdict: `DONE` (core). Cache, Swagger, and automated tests not confirmed — manual verification performed 2026-05-20.**

---

### STAGE 3 — Domain & Key Setup `GAP — CRITICAL`

Register every BL-## business rule and threshold key from BLOS Register spreadsheet v1.6.

| Checklist Item | Required | Current | Status |
|---|---|---|---|
| BL-## business rules registered in `business_rules` table | 300+ rules (BL-01 to BL-323+) | **16 rules** | `GAP` |
| FBM rules (BL-01 to BL-73) | 73 rules | Unknown subset of 16 | `GAP` |
| FBA rules (BL-74 to BL-92) | 19 rules | Unknown subset of 16 | `GAP` |
| PPC rules (BL-93 to BL-108) | 16 rules | Unknown subset of 16 | `GAP` |
| PH Action SLA rules (BL-149 to BL-173) | 25 rules | Not registered | `GAP` |
| Amazon PPC Anomaly rules (BL-174 to BL-207) | 34 rules | Not registered | `GAP` |
| eBay rules (BL-208 to BL-237) | 30 rules | Not registered | `GAP` |
| Google Ads rules (BL-238 to BL-263) | 26 rules | Not registered | `GAP` |
| Facebook Meta rules (BL-264 to BL-297) | 34 rules | Not registered | `GAP` |
| Channel Economics rules (BL-298 to BL-323) | 26 rules | Not registered | `GAP` |
| No rule_id is NULL in `thresholds` table | Required | Not confirmed | `GAP` |
| No duplicate rule_id in `business_rules` | Required | Not confirmed at full scale | `GAP` |
| Threshold keys registered with correct `domain_owner` per role titles in BLOS register | Required | 80 thresholds present, domain_owner correctness unconfirmed at full scale | `PARTIAL` |
| `user_domain_access` records populated for all domain owners | Required | **0 records** | `GAP` |
| Domain isolation tested: non-admin cannot see/edit another domain's thresholds | Required | Logic exists (allowedDomainsFor()) but no access records to enforce | `GAP` |
| All `pending_review` thresholds confirmed by domain owners (BL-19, BL-25–27, BL-42, BL-50–51, BL-54–55, BL-59–60) | Required | Unknown | `GAP` |
| Sajeesan (DTL) confirmed all threshold keys correctly registered | Required — BLOCKER | Not confirmed | `GAP` |

**Stage 3 Verdict: `GAP — CRITICAL`. Only 16 of 300+ required BL-## rules are in the system. `user_domain_access` has 0 records. This is the largest single gap in the entire project. The Impact Simulation Engine (Stage 4) and Domain Owner UI (Stage 5) are functionally hollow without real data.**

---

### STAGE 4 — Impact Simulation Engine `PARTIAL`

Build the Impact Simulation Engine using `threshold_dependencies`.

| Checklist Item | Status |
|---|---|
| `threshold_dependencies` table schema created | `DONE` |
| `thresholdsImpactPreview()` API method — calculates HIGH/MEDIUM/LOW impact before save | `DONE` |
| ThresholdChangeRequest model — HIGH-impact triggers approval workflow | `DONE` |
| Impact preview fires automatically on value entry in Domain Owner UI | `DONE` |
| `threshold_dependencies` records populated with real dependent systems | `GAP` — **0 records** |
| HIGH-impact save blocked — Submit for Approval workflow activated instead | `DONE` |
| Impact preview in frontend shows HIGH/MEDIUM/LOW affected systems | `DONE` (UI built; shows empty when no dependencies registered) |

**Stage 4 Verdict: `PARTIAL`. Engine is built and wired up. However, with 0 records in `threshold_dependencies`, every threshold change shows zero impact — the engine is functionally silent. Real dependency data must be populated for this stage to be complete.**

---

### STAGE 5 — Domain Owner UI `DONE`

The web interface for Team Leaders to change threshold values.

| Checklist Item | Status |
|---|---|
| Login screen — credential validation | `DONE` |
| Token-based auth (Bearer), stored in session storage | `DONE` — commit `0956069` |
| Role-based routing — admin and domain owner views separate | `DONE` |
| Threshold list view — key, label, value, unit, direction, last changed date/by | `DONE` |
| Domain scoping — non-admin sees only their assigned domains | `DONE` — `allowedDomainsFor()` |
| Edit screen — current value, BL-## rule (read-only), impact preview | `DONE` |
| Change reason mandatory — save button disabled until 10+ characters entered | `DONE` |
| HIGH-impact save replaced with Submit for Approval — old value stays active | `DONE` |
| Threshold export — YAML and CSV | `DONE` — commit `3b5f2cc` |
| Version history view | `DONE` |
| Responsive design (tablet and desktop) | `DONE` — commit `7000df9` |
| Mobile layout — hamburger overlay, safe-area, fixed dropdown | `DONE` — 2026-05-20 |
| SPA registration removed — admin-controlled only | `DONE` — commit `0956069` |
| Header navigation — active state, branding | `DONE` — commit `3b5f2cc` |

**Stage 5 Verdict: `DONE`. Full Domain Owner UI delivered with all required features. Mobile layout completed 2026-05-20.**

---

### STAGE 6 — Skill Pack `NOT STARTED`

Seven skill files for AI systems and developers to consume BLOS correctly.

| Checklist Item | Status |
|---|---|
| 7 skill files written covering threshold consumption, BL-## rules, API usage | `NOT STARTED` |
| Skill files published to SkillVault / accessible to consuming systems | `NOT STARTED` |

**Stage 6 Verdict: `NOT STARTED`. No evidence of any skill file creation for BLOS consumption.**

---

### STAGE 7 — Consumer Governance `NOT STARTED`

Space 2 Check 8 integration, developer code review, LLM space audit.

| Checklist Item | Status |
|---|---|
| Space 2 Check 8 integration | `NOT STARTED` |
| Developer code review process using BLOS | `NOT STARTED` |
| LLM space audit | `NOT STARTED` |

**Stage 7 Verdict: `NOT STARTED`.**

---

### STAGE 8 — 3AM Documentation `PARTIAL`

Architecture map, monitoring guide, failure runbook — must meet 3AM Standard.

| Checklist Item | Status |
|---|---|
| Architecture map | `PARTIAL` — engineering docs written (BLOS_ProjectSentinel_Documentation) but not a dedicated 3AM architecture map |
| Monitoring guide | `NOT STARTED` |
| Failure runbook | `NOT STARTED` |
| Living engineering log (`docs/skill.md`) maintained | `DONE` |

**Stage 8 Verdict: `PARTIAL`. Engineering documentation exists but dedicated monitoring guide and failure runbook have not been produced.**

---

### STAGE 9 — Sign-Off & Go-Live `NOT STARTED`

Sign-off, go-live, handover to all domain owners and consuming systems.

| Checklist Item | Status |
|---|---|
| DTL final sign-off | `NOT STARTED` |
| Handover to domain owners | `NOT STARTED` |
| Consuming systems notified and connected | `NOT STARTED` |

**Stage 9 Verdict: `NOT STARTED`. Blocked by Stages 3, 6, 7, and 8.**

---

## BLOS Build Guide — Overall Stage Summary

| Stage | Name | Status | Blocking? |
|---|---|---|---|
| 1 | Schema & Database | `DONE` | — |
| 2 | API Layer | `DONE` | — |
| 3 | Domain & Key Setup | `GAP — CRITICAL` | Yes — empty DB, no domain access |
| 4 | Impact Simulation | `PARTIAL` | Yes — 0 dependency records |
| 5 | Domain Owner UI | `DONE` | — |
| 6 | Skill Pack | `NOT STARTED` | Yes — required for Stage 9 |
| 7 | Consumer Governance | `NOT STARTED` | Yes — required for Stage 9 |
| 8 | 3AM Documentation | `PARTIAL` | Yes — monitoring + runbook missing |
| 9 | Sign-Off & Go-Live | `NOT STARTED` | Blocked by 3, 6, 7, 8 |

---

---

# PART 2 — SKILLVAULT REQUIREMENTS & TRACK STATUS

## SkillVault Phase 1 — Core System Requirements

Source: `SkillVault_System_Design_v1.0.docx` (May 14, 2026)
Developer doc: `SkillVault_Developer_Documentation_Abiraj_1.docx`

**MD Project Rule:** *"A phase is closed only when the beneficiary uses the benefit in their daily work. Not a feature. Not a sprint. Not a milestone."*

### Phase 1 — Backend API & File Operations

| Requirement | Spec Priority | Status | Evidence |
|---|---|---|---|
| Hierarchical folder structure matching `/mnt/skills/` directory | P0 | `DONE` | Folder model + self-referential `parent_id` |
| File upload into a specified folder (admin only) | P0 | `DONE` | `uploadFile()` + `POST /folders/{id}/files` |
| Replace / overwrite existing file (admin only) | P0 | `DONE` | `reuploadManagedFile()` + `POST /files/{id}/reupload` |
| Browse folder tree — full hierarchy | P0 | `DONE` | `getTree()` + `GET /folders/tree` |
| View folder contents (immediate children) | P0 | `DONE` | `getFolderContents()` + `GET /folders/{id}` |
| Open & read file content (md, txt, json, xml, csv) | P1 | `DONE` | `readTextPreview()` + `GET /files/{id}/content` |
| Download individual file (admin only) | P0 | `DONE` | `GET /files/{id}/download` |
| Download entire folder as ZIP (structure preserved) | P0 | `DONE` | `createFolderZipArchive()` + `GET /folders/{id}/download-zip` |
| Rename folder (all descendant paths updated) | P1 | `DONE` | `renameFolder()` + `PUT /folders/{id}/rename` |
| Delete folder (cascade removes all children and files) | P1 | `DONE` | `deleteFolder()` + `DELETE /folders/{id}` |
| Rename file | P1 | `DONE` | `renameFile()` + `PUT /files/{id}/rename` |
| Move file between folders | P1 | `DONE` | `moveFile()` + `PUT /files/{id}/move` |
| Delete individual file | P1 | `DONE` | `deleteFile()` + `DELETE /files/{id}` |
| Admin-only write gates on all write/delete/download routes | P0 | `DONE` | Admin middleware group in `routes/api.php` |
| MIME-type detection on upload | P1 | `DONE` | `files.mime_type` + `files.extension` stored |
| File size recorded on upload | P1 | `DONE` | `files.size` column |
| Self-healing file path after folder rename | P1 | `DONE` | `resolvedStorageRelativePath()` auto-repair |
| Storage driver swap (local → S3) with zero code change | P1 | `DONE` | `FolderFileService disk()` abstraction |
| Frontend file library UI in Account SPA | P0 | `DONE` | `FileManager.vue` — `Account.js` SPA |
| Markdown file content preview in browser | P1 | `DONE` | `GET /files/{id}/content` → rendered by frontend |
| Replace File review modal (diff before confirm) | P1 | `DONE` | Added 2026-05-19 — Line diff + Rendered mode |

### Phase 1 — SkillVault-Specific Features (Version & Download Tracking)

These requirements appear in the System Design as **Phase 1 (P0/P1)** but were reclassified as Phase 2 in the developer's delivery. This is a **classification mismatch** that needs MD review.

| Requirement | Spec Priority | Developer Status | Risk |
|---|---|---|---|
| `skill_versions` table — full version history per skill file | P1 | `DEFERRED to Phase 2` | MD may consider Phase 1 incomplete |
| Rollback to previous version (creates new version record) | P1 | `DEFERRED to Phase 2` | MD may consider Phase 1 incomplete |
| Per-user download tracking (`user_skill_downloads` pivot) | P0 | `DEFERRED to Phase 2` | **P0 item deferred — high risk** |
| Amber pulse indicator — undownloaded updates shown per user | P1 | `DEFERRED to Phase 2` | MD may consider Phase 1 incomplete |
| Row count (line count) displayed per skill file | P1 | `DEFERRED to Phase 2` | MD may consider Phase 1 incomplete |
| Summary bar: Total Skills / Recently Updated / Pending Download | P1 | `DEFERRED to Phase 2` | MD may consider Phase 1 incomplete |

**Action Required:** Clarify with MD whether the six items above must be built before Phase 1 is officially closed. Per the MD Project Rule, a phase closes only when the beneficiary uses the benefit daily — not when features are built.

### Phase 2 — Automation & MCP (Not Started)

Status: `NOT STARTED` — awaiting beneficiary confirmation of Phase 1 daily use.

| Requirement | Status |
|---|---|
| REST manifest endpoint: `GET /api/skills/manifest` (returns current version IDs JSON) | `NOT STARTED` |
| MCP Server: auto-fetch changed skill files on version change | `NOT STARTED` |
| Webhook: POST to registered endpoint on skill update | `NOT STARTED` |
| Claude Code CLI: `claude skills sync` command | `NOT STARTED` |
| API token authentication for programmatic access | `NOT STARTED` |
| Audit log (who changed what, when) | `NOT STARTED` |

---

## SkillVault — Delivered File Reference

| File | Type | Purpose |
|---|---|---|
| `app/Http/Controllers/Api/FolderFileController.php` | Controller | 13 REST endpoints — thin, delegates to service |
| `app/Services/FolderFileService.php` | Service | All file system operations; storage-driver agnostic |
| `app/Models/Folder.php` | Model | Self-referential; eager-loads children + files |
| `app/Models/ManagedFile.php` | Model | Belongs to Folder; table name: `files` |
| `database/migrations/2026_05_01_000001_*` | Migration | Creates `folders` + `files` tables with FK constraints |
| `routes/api.php` | Routes | 13 routes under admin middleware group |

---

---

# PART 3 — OIL CONFIGURATOR v5 — THRESHOLD REGISTRY

Source: `oil_configurator_v5.html` (reference design)
Implementation: `OilConfigurator.vue` (80 thresholds, 8 domains)

## Business Logic Domains & Threshold Status

| Domain | UI Thresholds | Status |
|---|---|---|
| Amazon Organic Listing Performance | 7 | `DONE` |
| Fulfilment SLA | 8 | `DONE` |
| Organic Listing Performance | 16 | `DONE` |
| Portfolio Health | 8 | `DONE` |
| Pricing Strategy | 8 | `DONE` |
| Product Economics | 14 | `DONE` |
| Product Quality | 12 | `DONE` |
| SKU Lifecycle | 7 | `DONE` |
| **Total** | **80** | **`DONE` — all 80 rendered in UI** |

## Key Confirmed Threshold Values (from OIL v5 reference, confirmed Apr 2026)

| Key | Value | Unit | Domain |
|---|---|---|---|
| `band_red_max` | 0 | % | Margin Bands |
| `band_amber_max` | 3 | % | Margin Bands |
| `band_yellow_max` | 8 | % | Margin Bands |
| `band_dkgreen_max` | 15 | % | Margin Bands |
| `band_purple_min` | 16 | % | Margin Bands |
| `hips_min_revenue` | 2000 | £/mo | SKU Economics |
| `hips_min_margin_pct` | 22 | % | SKU Economics |
| `hips_kill_margin_pct` | 12 | % | SKU Economics |
| `hips_kill_consecutive_months` | 2 | months | SKU Economics |
| `oaf_kpi_floor_score` | 70 | /100 | Staff Accountability |
| `oaf_escalation_reviews` | 2 | reviews | Staff Accountability |
| `oaf_kill_reviews` | 4 | reviews | Staff Accountability |
| `ppc_acos_target` | 20 | % | PPC (updated Apr 2026 from 22%) |
| `ch_amazon_referral_pct` | 18 | % | Channel Fees (updated Apr 2026 from 15%) |
| `ch_ebay_fvf_pct` | 12.35 | % | Channel Fees |
| `fbm_postage_cost_gbp` | 2.50 | £ | Amazon FBM |
| `fbm_min_aov_gbp` | 24 | £ | Amazon FBM |
| `fbm_cancellation_rate_pct` | 2 | % | Amazon FBM |
| `fbm_return_rate_amazon_pct` | 4 | % | Amazon FBM |
| `cogs_pct_of_listing` | 20 | % | Economics |
| `vat_pct` | 20 | % | Economics |
| `kpi_l2_amber_weeks` | 3 | weeks | KPI Escalation |
| `kpi_l5_resolution_days` | 7 | days | KPI Escalation |
| `cop_refund_self_approval_gbp` | 75 | £ | Customer Ops |
| `whs_pick_accuracy_floor` | 98 | % | Warehouse |
| `seo_content_sla_standard_days` | 5 | days | SEO |

---

---

# PART 4 — DATABASE STATE

## Current Record Counts vs Requirements

| Table | Required (Spec) | Current | Status |
|---|---|---|---|
| `business_rules` | 300+ (BL-01 to BL-323+) | **16** | `GAP — CRITICAL` |
| `business_rule_categorical_mapping` | Proportional to BL-## count | 69 | `PARTIAL` |
| `thresholds` | Proportional to BL-## count | 80 | `PARTIAL` |
| `user_domain_access` | One record per user-domain pair | **0** | `GAP — CRITICAL` |
| `threshold_versions` | Grows with edits | 3 | `DONE` (correct — grows over time) |
| `threshold_dependencies` | One per dependent system per threshold | **0** | `GAP` |
| `threshold_change_requests` | Grows with HIGH-impact edits | Unknown | `DONE` (table exists) |
| `folders` (SkillVault) | Mirrors `/mnt/skills/` structure | Unknown | `DONE` |
| `files` (SkillVault) | All skill files | Unknown | `DONE` |

**Note:** Database was reloaded from Excel master sheet on 2026-05-20. Row counts above reflect post-reload state for non-threshold tables. BL-## registration from BLOS Register v1.6 is the outstanding data gap.

---

---

# PART 5 — TRACK STATUS SUMMARY

## Overall Project Track Assessment (as of 2026-05-20)

| Project | Component | On Track? | Notes |
|---|---|---|---|
| BLOS | Infrastructure & schema | `YES` | Stages 1, 2, 5 complete |
| BLOS | Data population (BL-## rules) | `NO` | Only 16 of 300+ rules registered |
| BLOS | Domain access records | `NO` | 0 records — permissions non-functional |
| BLOS | Impact Simulation | `PARTIAL` | Engine built, 0 dependency records |
| BLOS | Stages 6, 7, 9 | `NO` | Not started |
| BLOS | Stage 8 (3AM Docs) | `PARTIAL` | Engineering docs done, runbook/monitor missing |
| SkillVault | Core file library (backend + frontend) | `YES` | All 13 endpoints + FileManager.vue |
| SkillVault | Phase 1 SkillVault-specific features | `AT RISK` | Version ledger, download tracking, pulse indicator deferred |
| SkillVault | Phase 2 (MCP, webhooks) | `BLOCKED` | Awaiting Phase 1 beneficiary confirmation |
| OIL Configurator | 80 thresholds across 8 domains | `YES` | All rendered in UI with YAML export |
| Mobile UI | Header, hamburger, safe-area | `YES` | Completed 2026-05-20 |
| API verification | All endpoint groups | `YES` | Manual pass completed 2026-05-20 |

## What Is Blocking Go-Live

1. **Stage 3 data gap** — Register all BL-## rules (BL-01 to BL-323+) from BLOS Register v1.6
2. **user_domain_access** — Populate domain access records for all domain owners
3. **threshold_dependencies** — Register dependent systems per threshold for Impact Simulation to function
4. **Stage 6** — Write 7 skill files for AI/developer consumption
5. **Stage 7** — Consumer Governance setup
6. **Stage 8** — Monitoring guide + failure runbook
7. **6 uncommitted files from 2026-05-18** — Must be committed after team review
8. **SkillVault Phase 1 classification** — Clarify with MD whether deferred items (version ledger, download tracking) must ship before Phase 1 closes

---

---

# PART 6 — GAP ANALYSIS

## Critical Gaps (project cannot go live without these)

### GAP-1: BL-## Rules Registration (Stage 3)
- **What's missing:** ~290+ business rules not yet registered in the `business_rules` table
- **Source:** BLOS Register spreadsheet v1.6 is the authoritative source
- **Impact:** Without rules, thresholds have no BL-## context; API response business_rule blocks return empty/incorrect data; consuming systems get numbers without meaning
- **Fix:** Data entry from BLOS Register v1.6 into `business_rules` and `thresholds` tables using SQL scripts with conflict handling
- **Owner:** Abiraj / Vithushali (per Build Guide)

### GAP-2: user_domain_access Records (Stage 3)
- **What's missing:** 0 records — no user has been assigned to any domain
- **Impact:** `allowedDomainsFor()` logic exists but returns empty — all non-admin users see no thresholds; domain-scoped permission enforcement is completely non-functional in practice
- **Fix:** Insert user-domain pairs per domain owner role as confirmed by Sajeesan (DTL)
- **Owner:** Abiraj

### GAP-3: threshold_dependencies Records (Stage 4)
- **What's missing:** 0 records — no dependent systems registered against any threshold
- **Impact:** Impact Simulation Engine shows zero impact for every threshold change — HIGH-impact approval workflow never triggers because every change appears low-risk
- **Fix:** Register all dependent systems per threshold key from BLOS Register or domain owner input
- **Owner:** Abiraj / domain owners

### GAP-4: Stages 6, 7, 9 Not Started
- **What's missing:** Skill pack (7 files), Consumer Governance, Sign-Off
- **Impact:** Consuming systems (AI agents, developers) have no governed way to read BLOS; go-live cannot happen
- **Fix:** Stage 6 → write 7 BLOS skill files; Stage 7 → Space 2 Check 8 integration; Stage 9 → DTL sign-off + handover
- **Owner:** Abiraj

### GAP-5: SkillVault Phase 1 Classification Mismatch
- **What's missing:** `skill_versions` table, `user_skill_downloads` pivot, amber pulse indicator, row count, summary bar
- **Impact:** These are listed as Phase 1 P0/P1 requirements in the System Design but marked as Phase 2 by developer — if MD considers Phase 1 incomplete, Phase 2 cannot start
- **Fix:** Confirm with MD whether Phase 1 is closed or whether these features must be built
- **Owner:** Abiraj + MD sign-off

---

---

# PART 7 — ACTIVITY LOG

*Append new sessions at the TOP. Format: date · type · area · summary · status.*

---

### 2026-05-20 — Data Migration · API Verification · Mobile UI Overhaul

| Type | Area | Summary | Status |
|---|---|---|---|
| `data` | database | Reviewed Excel master sheet and wrote SQL queries to reload all records with duplicate key conflict handling | done |
| `data` | database | Executed SQL queries — verified row counts match Excel source, no orphan records, no duplicates | done |
| `api` | all-endpoints | Full manual API verification across File Management (13 endpoints), Threshold Configuration, auth, and role-gated routes | done |
| `api` | auth | Confirmed admin-only endpoints correctly reject non-admin tokens (401/403) | done |
| `ui` | thresholds | Rebuilt Threshold Configurator sticky Actions column — flex layout, consistent gap, hairline left border separator, drop-shadow removed, redundant `.tc-actions` class removed | done |
| `ui` | header | Replaced `Header.vue` flex + `order` layout with CSS Grid (`left \| menu \| right`) for correct consistent alignment | done |
| `ui` | header | Fixed active nav link — removed `translateY` so pills stay vertically aligned | done |
| `ui` | header | Added `safe-area-inset` top/bottom to header inner | done |
| `ui` | header | Built ≤768px two-row mobile pattern: Row 1 brand + avatar, Row 2 scrollable nav | done |
| `ui` | header | Hamburger overlay full-screen sheet — safe-area, fixed z-index, locked body scroll, scrollable sheet | done |
| `ui` | header | Account dropdown fixed to `position: fixed` + `z-index: 270` — no longer clipped by header overflow on mobile | done |
| `fix` | app-vue | Corrected `safe-area-inset-left` / `right` swap in `App.vue` — content aligns on all notch devices | done |

**Compliance:** Fully compliant. All four task areas completed and verified.
**DB changes:** Data reload only — no schema changes.
**Phase 2 status:** Pending beneficiary confirmation of Phase 1 daily use.

---

### 2026-05-19 — UI Polish & File Manager Enhancement

| Type | Area | Summary | Status |
|---|---|---|---|
| `ui` | business-os | Redesigned `OilConfigurator.vue` sidebar — dark gradient background, compact single-line brand header, accent icon chips per domain with count pills, brighter nav labels and icons, compact topbar | done |
| `ui` | thresholds | Redesigned `ThresholdConfigurator.vue` sidebar — matched dark sidebar visual system, flex column + space-between nav layout, compact topbar hero, improved contrast | done |
| `fix` | file-manager | Fixed `FileManager.vue` More actions dropdown — rebuilt from per-row inline menus to single portal menu (`fmMoreMenuPortal`) anchored at viewport level via `getBoundingClientRect()` | done |
| `feature` | file-manager | Delivered Replace File review modal — Line diff mode (removed lines red, added lines green) + Rendered mode (syntax-aware per extension: md, json, csv, xml). Confirm required before reupload commits. | done |
| `docs` | repo | Initialised `.cursorrules` (Cursor AI project rules) and `MEMORY.md` (project knowledge base) at repository root | done |

**New functions added:**
- `fmMoreMenuPortal` — single portal dropdown for all File Manager row More actions
- `replaceDiffOpen` — state flag for Replace File review modal visibility
- `replaceDiffViewMode` — tracks active view (Line diff / Rendered)
- `replaceDiffRenderedLineDiffHtml` — computed rendered + diff HTML for modal
- `fm-modal--diff` — CSS class for Replace File review modal layout

**Business logic added:**
- Replace File Safety Rule: file replacement cannot commit until admin explicitly clicks Confirm inside review modal
- Diff computed client-side before any API call is made
- Rendered mode formats lines by file type before display

**Compliance:** Fully compliant. All five tasks match SkillVault System Design v1.0 and Account SPA visual consistency standard. Backend/API unchanged.

---

### 2026-05-18 — Account UI Polish · Engineering Log Initialised

| Type | Area | Summary | Status |
|---|---|---|---|
| `docs` | docs | Initialised engineering activity log and Cursor IDE agent maintenance rule (`.cursor/rules/engineering-activity-log.mdc`) | done |
| `ui` | business-os | Business OS (`OilConfigurator.vue`): animated `oil-bg`, staggered `oil-in` entrances, hero topbar with live dot, glass sidebar and topbar | in-progress — **6 files uncommitted — action required** |
| `ui` | thresholds | Threshold Configurator (`ThresholdConfigurator.vue`): `tc-bg` background layer, `tc-in` stagger on shell regions, glass toolbar and table, reduced-motion support | in-progress |
| `ui` | file-library | File Manager (`FileManager.vue`): `fm-bg` mesh/orbs/grid, `fm-in` hero/layout/sidebar/main, glass metrics and toolbar | in-progress |
| `ui` | account-ui | Dashboard (`Dashboard.vue`): full-screen light theme, animated mesh, glass cards, `dash-in` stagger, role-based content preserved | in-progress |
| `ui` | account-ui | Header (`Header.vue`): removed logo outer border and accent stripe; restored soft mint gradient and sheen on `.nav-logo-sheen` | in-progress |
| `config` | account-ui | Full-bleed main layout extended to Dashboard route in `App.vue` | in-progress |

**Action required:** Commit the 6 in-progress files after team review.

---

### Prior Activity (Pre-May 18)

| Date | Type | Area | Summary | Author | Commit |
|---|---|---|---|---|---|
| 2026-05-12 | `fix` | thresholds | Threshold decimal precision, file replace diff preview, compact admin UI | team | `54bb479` |
| 2026-05-12 | `ui` | file-library | Library counts, line rows, download button, hierarchy styling, animated logo | team | `aee9695` |
| 2026-05-12 | `ui` | account-ui | Full-width layout, centred nav, role-based file library access | team | `246432f` |
| 2026-05-05 | `docs` | hr | Developer Project Documentation submitted (BLOS HR submission) | Abiraj | — |
| — | `feature` | business-os | Business OS Configurator UI added | team | `f79ee0d` |
| — | `feature` | file-library | Central File Library and Account UI refresh | team | `dca4116` |
| — | `feature` | auth | Authentication, token middleware, domain access, registration control | Abiraj | multiple |
| — | `db` | schema | All five BLOS tables, UserDomainAccess, ThresholdChangeRequest models | Abiraj | `f9492de` |
| — | `db` | versioning | Record threshold value changes in threshold_versions, sync audit fields | Abiraj | `752d248` |

---

---

# PART 8 — ARCHITECTURE REFERENCE

## CSS Namespace Convention Map

**Strict per-module CSS namespacing enforced. Never share classes across page components.**

| Module | Background Layer | Entrance Class | Delay Variable | Rise Keyframe |
|---|---|---|---|---|
| Dashboard | `dashboard-bg`, `dashboard-bg-mesh`, `dashboard-bg-orb--*`, `dashboard-bg-grid` | `dash-in` | `--dash-delay` | Inline `@keyframes` |
| File Manager | `fm-bg`, `fm-bg-mesh`, `fm-bg-orb--*`, `fm-bg-grid` | `fm-in` | `--fm-delay` | `fm-rise` |
| Threshold Config | `tc-bg`, `tc-bg-mesh`, `tc-bg-orb--*`, `tc-bg-grid` | `tc-in` | `--tc-delay` | `tc-rise` |
| Business OS | `oil-bg`, `oil-bg-mesh`, `oil-bg-orb--*`, `oil-bg-grid` | `oil-in` | `--oil-delay` | `oil-rise` |

## Animation System Standards

| Property | Specification |
|---|---|
| Entrance Class | `*-in` applied to all entering elements |
| Delay Variable | `--*-delay` CSS custom property, staggered `0.05s–0.3s` per element |
| Rise Keyframe | `translateY(18px)` → `translateY(0)`, duration `0.75s`, easing `ease-out` |
| Reduced Motion | `@media (prefers-reduced-motion: reduce)` disables all keyframe animations |
| Background Orbs | 3 animated gradient orbs per page at varying viewport positions |

## Glass-Morphism System

```css
/* Content panels */
background: rgba(255, 255, 255, 0.88);
backdrop-filter: blur();

/* Topbars and toolbars */
background: rgba(255, 255, 255, 0.94);
backdrop-filter: blur();
```

## Full-Bleed Layout

`isFullBleedMain()` in `App.vue` removes default main-content padding for: `dashboard`, `threshold-configurator`, `oil-configurator`, `file-manager`.
**Do not add padding overrides inside page components — control from `isFullBleedMain()` only.**

## Key File Reference

| Topic | File | Symbols / Classes |
|---|---|---|
| Full-bleed layout | `resources/js/Account/App.vue` | `isFullBleedMain()` |
| Routes | `resources/js/Account/Router.js` | `routes` array |
| Session / auth | `resources/js/Account/userSession` | auth token + header injection |
| Dashboard UI | `resources/js/Account/Pages/Dashboard.vue` | `dashboard-bg*`, `dash-in`, `--dash-delay` |
| File Library UI | `resources/js/Account/Pages/FileManager.vue` | `fm-bg*`, `fm-in`, `--fm-delay`, `fmMoreMenuPortal` |
| Threshold UI | `resources/js/Account/Pages/ThresholdConfigurator.vue` | `tc-bg*`, `tc-in`, `--tc-delay` |
| Business OS UI | `resources/js/Account/Pages/OilConfigurator.vue` | `oil-bg*`, `oil-in`, `oil-shell`, `--oil-delay`, `__export` |
| Header | `resources/js/Account/Pages/includes/Header.vue` | `.nav-logo`, `.nav-logo-sheen`, hamburger overlay |
| Threshold API | `app/Http/Controllers/Api/ThresholdConfigurationController.php` | all threshold endpoints |
| File API | `app/Http/Controllers/Api/FolderFileController.php` | 13 file endpoints |
| File Service | `app/Services/FolderFileService.php` | all file operations |
| Auth Middleware | `app/Http/Middleware/CheckAuthMiddleware.php` | Bearer token validation |

## Engineering Conventions

- Only standard HTML elements in Vue templates — no unregistered custom elements
- CSS custom properties are the mandatory mechanism for stagger delay parameterisation
- Animation timing curves standardised at `ease-out`
- All interactive elements maintain WCAG-compatible contrast ratios
- `backdrop-filter: blur()` applied only to interactive panel surfaces — not background layers
- `transform: translateY()` and `opacity` used exclusively in animations — no layout-triggering properties
- All component styles use Vue 2 `<style scoped>` — no global style pollution
- No dist artifacts committed — build output is gitignored
- Any dropdown inside a container with `overflow: hidden` must use `position: fixed` to escape clipping
- CSS Grid (`left | menu | right`) is the header layout standard — not flex + `order`

---

## Session Protocol

1. Read this file before starting any work
2. Complete engineering work
3. Append Activity Log entry (newest-first) after every session
4. Update Track Status Summary if any status changes
5. Update Gap Analysis if any gap is resolved or discovered
6. Verify UI build: `npm run development`

**Do not store secrets, credentials, or PII in this file. Use path citations and ticket references only.**

---

*skill.md — LLM-Queryable Requirements & Track Status*
*Maintained by J. Abiraj · Project Sentinel · Ledsone Centralizer Operations Hub*
*Sources: BLOS Build Guide v1.0 · SkillVault System Design v1.0 · OIL Configurator v5 · Daily Updates May 18–20, 2026*
*Last updated: 2026-05-20*
