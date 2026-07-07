## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-19 |
| **developer** | abiraj |
| **project** | LEDsONE Centralizer (Centralized Admin / Operations Platform) |
| **project\_code** | blos |
| **phase** | IMPLEMENTATION (HARDENING + DATA-MODEL CLEANUP) |
| **requirement\_id** | REQ-04 |
| **deliverable\_id** | REQ-04-D05 |
| **status** | COMPLETE (code) — Rule Builder discard-guard hardened; redundant `previous_value`/`change_reason` snapshot columns dropped from `thresholds` across model/controller/UI; committed + pushed to `Abiraj` (`b20c211`, `bc1204a`); builds clean. ⚠ **ONE pending server step:** run `drop_threshold_snapshot_columns.sql` as a privileged DB account, deployed together with the code. |
| **evidence\_location** | Git commits **`b20c211`, `bc1204a`** on branch `Abiraj` (GitLab: `sajeesans2/ledsone-centralizer`) · changed: `resources/js/Account/Pages/RuleBuilder.vue`, `app/Http/Controllers/Api/ThresholdConfigurationController.php`, `app/Models/Threshold.php`, `resources/js/Account/Pages/ThresholdConfigurator.vue`, `resources/js/Account/Pages/OilConfigurator.vue` · new SQL: `docs/sql/drop_threshold_snapshot_columns.sql` · live: https://centralizer.vintageinterior.co.uk |
| **blos\_keys\_used** | Rule `BL-001` (CTR Collapse), stages initial/restore/kill; condition_logics rows 1–3; thresholds `TH-001…TH-035`. Threshold-value edit path: writes `threshold_versions` row (old_value/new_value/change_reason) + bumps `version`; `thresholds` row now keeps only `last_changed_by/at` + `version` as current-state metadata. |
| **hardcoded\_thresholds** | Threshold value-change float epsilon `0.0000001` (unchanged). Threshold grid colspan **27 → 25** after dropping 2 columns. Discard-modal palette: overlay `rgba(15,23,42,0.45)` + 2px blur, solid-danger gradient `#e11d48→#be123c` (hover `#f43f5e→#be123c`), pop `0.14s`/fade `0.12s`, max-width `24rem`, z-index `60`. **STILL TEMP:** `change_reason` validation stays `nullable` (deferred again, by request) — now also **input-only** (logged to history, never stored on `thresholds`). |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| BLOS-THRESHOLDS \| LARAVEL \| VUE-SPA \| RULE-ENGINE \| AUDIT-HISTORY |

## File path:
# 2026-06-19__abiraj__blos__REQ-04-D05.md
# DigitWeb_Works_Abiraj/19_06_2026/

---

## SECTION 1 · SYSTEM STATE

- **Current system state at start of today:** After D04 the BLOS Rule Builder (engine `ruleLogic.js` + recursive `RuleNode.vue` + page `RuleBuilder.vue`) was built, wired, validated, and live; logic editing was unified through it; the schema (`business_rules`, `condition_logics`, `glossary`, `rule_threshold_mapping`, `thresholds` 35 rows) was complete and deployed.
- **What was working:** All admin CRUD tabs, bulk CSV upload, OilConfigurator ("Business OS") value editing + export, auth, and the new Rule Builder authoring rules end-to-end.
- **What was broken / rough:** (1) The Rule Builder's unsaved-changes protection still used a **native `window.confirm`**, and some exit paths (header nav, browser back) lost edits silently or inconsistently; there was no in-place way to abandon edits without navigating away. (2) The `thresholds` table carried two columns — `previous_value` and `change_reason` — that only ever mirrored the **latest** `threshold_versions` row, i.e. pure duplication of the audit history (the real source of truth).
- **Your starting point:** Harden the Rule Builder's discard flow into a single themed guard, then remove the redundant snapshot columns from `thresholds` cleanly across code + UI without losing any change history.
- **Environment:** Laravel 9 + Vue 2 SPA. Server XAMPP/Linux at `/opt/lampp/htdocs/ledsone-centralizer`, MySQL `centralizer`. Local `.env` empty — frontend built with `npm run development` → `public/js/Account.js` (git-ignored). Deploy = developer's saves land directly on the live server (incl. the built bundle), so "save = live" after the frontend build; PHP controller changes are live once saved (`php artisan optimize:clear` only if a cached route/opcode is stale). **DB ALTER is the one exception** — the web user lacks `ALTER`, so column drops run as a privileged account.

> **In plain terms:** Two cleanups on top of yesterday's big feature. First, the rule-editing screen now warns you with a proper on-brand pop-up — not the browser's grey box — whenever you try to leave with unsaved edits, and it does this consistently on every way out (Back, switching rule/stage, top-menu nav, browser back). It also gained a plain "Discard changes" button so you can throw away edits without leaving the page. Second, we deleted two columns from the thresholds table that were just copies of the most recent entry in the change-history table — duplicated data that could drift out of sync. The reason someone types when they change a threshold is still saved (into the history table where it belongs), so nothing is lost.

---

## SECTION 2 · WHAT CHANGED TODAY

- **Change 1 — Rule Builder: themed discard-changes modal replaces `window.confirm` (`b20c211`, `RuleBuilder.vue`):** every exit path now funnels through one guard. New `guard(proceed)` runs `proceed` immediately when nothing is dirty, otherwise pops the modal and only runs it on confirm. `selectRule`/`selectCondition`/`newCondition` were split into a guard wrapper + an `applyRule`/`applyCondition`/`applyNewCondition` body, so the modal sits in front of every state switch. `beforeRouteLeave` now routes **header nav + browser back** through the same modal (previously these bypassed the confirm and lost edits). Modal state is `discard:{show,onConfirm,onCancel}`; `discardConfirm`/`discardCancel` resolve it; **Esc** closes it (`onKeydown` listener added in `mounted`, removed in `beforeDestroy`).
- **Change 2 — Rule Builder: in-place "Discard changes" button + "Delete stage" rename (`b20c211`):** added a ghost "Discard changes" button next to Save (`:disabled="!dirty || saving"`) → `discardEdits()` confirms via the modal, then `revertEdits()` reloads the last-saved DB row (`applyCondition`) for an existing stage, or resets to blank (`applyNewCondition`) for an unsaved new stage. Renamed the existing **Delete → "Delete stage"** (with a tooltip) so abandoning edits is no longer confused with deleting the whole condition row.
- **Change 3 — Post-save guard fix (`b20c211`):** moved `this.dirty = false` to **before** the post-save `loadConditions` + re-select, so the automatic re-select after a save can't trip the discard guard (previously `dirty` was cleared after the reload).
- **Change 4 — Drop redundant `previous_value` + `change_reason` from `thresholds` (`bc1204a`, model + controller + 2 Vue grids):**
  - **Model `Threshold.php`:** removed `previous_value` and `change_reason` from `$fillable` and dropped the `previous_value` numeric cast.
  - **Controller `ThresholdConfigurationController`:** removed both columns from the store, update, and bulk validation rule sets; removed the `$validated['previous_value'] = $oldValue` write on a value change. `change_reason` is now **input-only** — extracted early (`$reason = trim(...)`) and **`unset($validated['change_reason'])` before any `thresholds` update**, then logged to `threshold_versions.change_reason`. The version-history write (old_value/new_value/changed_by/version_number) is unchanged, so the full audit trail is intact.
  - **`ThresholdConfigurator.vue`:** removed the 2 grid columns + the `previous_value` form field; **colspan 27 → 25**.
  - **`OilConfigurator.vue`:** removed `previous_value` from the value-save payload.
- **Change 5 — Migration SQL + historical-snapshot notes (`bc1204a`, `docs/sql/`):** added `drop_threshold_snapshot_columns.sql` (`ALTER TABLE thresholds DROP previous_value, DROP change_reason`, with a rationale header + "run as privileged account / no data lost" notes). Added header notes to `thresholds.sql` and `thresholds_data_load.sql` marking them as historical snapshots (not row-edited).

### Deliverables
- **Deliverable A —** Rule Builder discard hardening: themed modal on every exit path (incl. header nav / browser back via `beforeRouteLeave`), in-place Discard button, Delete→"Delete stage", post-save `dirty` fix. (`b20c211`)
- **Deliverable B —** `thresholds` table slimmed: `previous_value` + `change_reason` removed from model/controller/both grids; `change_reason` re-routed to input-only history logging; audit trail preserved. (`bc1204a`)
- **Deliverable C —** `drop_threshold_snapshot_columns.sql` migration drafted (run privileged, deploy with code) + historical-snapshot header notes on the two seed SQL files. (`bc1204a`)
- **Deliverable D —** Both committed + pushed to `Abiraj`; frontend builds clean (`npm run development`); this EOD file.

Evidence: 2 commits `b20c211`, `bc1204a`; `RuleBuilder.vue` +118/−10; controller/model/2 grids + new SQL = +42/−16. Rebuilt `public/js/Account.js` (git-ignored, deployed via direct-to-server save). No credentials included.

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> Stack is **MySQL** (XAMPP). **Schema change today:** drop 2 columns from `thresholds` (via `drop_threshold_snapshot_columns.sql`, privileged account) — the only structural DB change in this deliverable.

### What was removed and why (duplication of the audit history)

| Column (removed from `thresholds`) | What it held | Where the truth actually lives |
| :---- | :---- | :---- |
| `previous_value` | a copy of the **latest** prior value | `threshold_versions.old_value` (every change, not just the last) |
| `change_reason` | a copy of the **latest** edit reason | `threshold_versions.change_reason` (per-change) |

> Both columns only ever mirrored the most-recent `threshold_versions` row, so they were redundant **and** at risk of drifting out of sync with the real history. `threshold_versions` remains the single source of truth.

### What stays on `thresholds` (current-state metadata, intentionally kept)

| Column | Role |
| :---- | :---- |
| `last_changed_by` | who made the most recent change (cheap grid display) |
| `last_changed_at` | when (cheap grid display) |
| `version` | current version number (bumped on each value change) |

### The value-edit flow after this change
On a threshold value edit the controller: (1) validates input, (2) extracts `change_reason` and **unsets it before the `thresholds` update**, (3) detects a real value change via `abs(new − old) > 0.0000001`, (4) inside a transaction `update`s the `thresholds` row (value + version + last_changed_by/at, **no `previous_value`**) and inserts a `threshold_versions` row carrying `old_value`, `new_value`, `changed_by`, `version_number`, and the typed `change_reason`. History is complete; the thresholds row no longer duplicates it.

### Deploy ordering (important)
Code and the `ALTER` must ship **together**: old code writes `previous_value`, so dropping the columns *without* the new code errors; the new code *without* the `ALTER` simply leaves two unused NULL columns. Run `drop_threshold_snapshot_columns.sql` as a privileged account (web user lacks `ALTER`, #1142), then `php artisan optimize:clear`.

---

## SECTION 4 · GAP FOUND

- **Gap — `drop_threshold_snapshot_columns.sql` not yet run on the server (MEDIUM, OPEN — action item):** the code is committed but the live `thresholds` table still has the 2 columns. Until the privileged `ALTER` runs, the new code simply ignores them (harmless), but the cleanup is incomplete. Deploy code + ALTER together, then `optimize:clear`. Owner: abiraj.
- **Gap — `change_reason` still optional (LOW, OPEN — deferred by request):** the `// TEMP:` `nullable` relaxation stays; user said restore it "some days after." Now additionally input-only (logged to history, not stored on `thresholds`). Owner: abiraj / team lead.

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

### RULE REMOVED — `previous_value` / `change_reason` no longer validated on `thresholds`
- Both were dropped from the store, update, and bulk validation rule sets (they are no longer columns on `thresholds`). `previous_value` is no longer written; `change_reason` is now extracted as **input-only** and logged to `threshold_versions`, never persisted on the thresholds row.

### RULE CHANGED — `change_reason` is input-only (and still optional)
- Still `nullable|string|max:1000` (`// TEMP:` — restore to `required|string|min:10|max:1000` when the team re-enables the reason requirement). Behaviour change: it is now pulled out of `$validated` **before** the thresholds update and written only to the history row.

### RULE CONFIRMED UNCHANGED — Rule Builder save gate (client)
- A condition is saveable only when a stage is set **and** every clause is complete; the new Discard button is the complementary path (abandon edits without saving). Discard is enabled only when `dirty && !saving`.

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Failure mode (RESOLVED) — silent loss of edits on header nav / browser back (LOW→fixed):** Trigger — the old `window.confirm` guard only sat on in-page actions (`selectRule`, `goBack`), so leaving via the top-menu nav or the browser Back button bypassed it and discarded unsaved edits with no prompt. Fix — `beforeRouteLeave` now routes **every** real route exit through the same discard modal (`next()` on confirm, `next(false)` on cancel). (`b20c211`)
- **Failure mode (RESOLVED) — post-save re-select tripping the guard (LOW→fixed):** after saving, the code reloaded conditions and re-selected the saved row while `dirty` was still `true`, which could pop the discard modal on a successful save. Fix — clear `dirty = false` **before** the reload + re-select. (`b20c211`)
- **Edge case (HANDLED) — Discard on an unsaved *new* stage:** `revertEdits()` checks `activeConditionId`; for an existing stage it reloads the saved DB row (`applyCondition`), for an unsaved new stage there is no DB row to restore so it resets to a blank condition (`applyNewCondition`) — no stale half-built form left behind.
- **Edge case (HANDLED) — Esc / overlay click while the modal is open:** Esc (`onKeydown`) and clicking the overlay (`@click.self="discardCancel"`) both run the cancel path = "Keep editing"; the listener is added in `mounted` and removed in `beforeDestroy` (no leak).
- **Edge case (HANDLED) — deploying the column drop out of order:** documented in the SQL header — old code + dropped columns errors (writes a missing column); new code + un-dropped columns just leaves 2 unused NULLs. Ship code and `ALTER` together. No data loss either way (history is in `threshold_versions`).

---

## SECTION 7 · DECISIONS MADE TODAY

- **Decision: one discard guard for the whole page, not per-action confirms.** Alternatives: keep the native `window.confirm`; add ad-hoc confirms on each exit. Reason: the native box is off-brand and, more importantly, was only wired to *some* exits — header nav and browser back slipped past it. A single `guard()` + `beforeRouteLeave` funnel makes the protection uniform and on-theme. Trade-off: a little more wiring (split select/new into guard + apply). Approved: user.
- **Decision: add an explicit in-place "Discard changes" button.** Reason: previously the only way to abandon edits was to navigate away and confirm; users wanted to revert and stay on the page. `revertEdits()` reloads the last-saved state in place. Trade-off: one more button on the save bar — disambiguated by renaming Delete → "Delete stage". Approved: user.
- **Decision: drop `previous_value` + `change_reason` from `thresholds` rather than keep them in sync.** Alternatives: leave them and keep mirroring the latest history row. Reason: they duplicated `threshold_versions` (the source of truth) and could drift; the grid's current-state needs are met by `last_changed_by/at` + `version`. Trade-off: a privileged `ALTER` is required and must deploy with the code. Approved: user.
- **Decision: keep capturing `change_reason` on a value edit, but log it only to history.** Reason: the audit reason is still valuable, but it belongs in `threshold_versions`, not as a snapshot on the live row. Implemented as extract-then-`unset` before the update. Trade-off: none meaningful — history is unchanged. Approved: user.
- **Decision: keep `change_reason` optional for now (deferred again).** Reason: user reiterated "some days after." The `// TEMP:` marker stays so it is easy to restore to `required|min:10`. Approved: user.

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### Current-state vs history (a reusable data-model rule)
A live row should hold **current state**; a separate versions table should hold **history**. Copying "the latest history value" back onto the live row (`previous_value`, `change_reason`) is duplication that can silently drift — delete it and read history from the history table. Keep only cheap current-state metadata (`last_changed_by`, `last_changed_at`, `version`) on the live row. Capture audit input (the typed reason) but write it to the **history** row, not the live row.

### Reusable pattern — one navigation/discard guard for a dirty form
- **Shape:** `guard(proceed)` → if `!dirty` run `proceed()` immediately, else open a modal whose confirm runs `proceed()` and whose cancel aborts. Split each state-switch action into a thin `select*` wrapper (`guard(() => apply*())`) + an `apply*()` body.
- **Cover every exit:** in-page switches go through `guard`; **real route exits** (header nav, browser Back) go through Vue Router's `beforeRouteLeave` → same modal (`next()` / `next(false)`). A native `window.confirm` on individual handlers *misses* router-level exits — this is the bug class to avoid.
- **In-place revert:** a "Discard changes" button = confirm via the same modal, then reload the last-saved record (existing row) or reset to blank (unsaved new) — lets users abandon edits without leaving.
- **Hygiene:** clear `dirty` **before** any post-save reload/re-select so a programmatic re-select can't trip the guard; add the Esc keydown listener in `mounted`, remove it in `beforeDestroy`.

### Reusable pattern — extract-then-unset input-only fields
When a request field must be captured but **not** written to the target table, pull it out of the validated array (`$x = trim($validated['x']); unset($validated['x'])`) **before** the model update, then use `$x` for the side-effect write (here: the history row). Guarantees the column can be safely dropped from the main table.

### Canonical Vocabulary

| Term | Meaning |
| :---- | :---- |
| current-state metadata | `last_changed_by/at`, `version` — kept on `thresholds` |
| audit history | `threshold_versions` rows — the single source of truth for changes |
| snapshot column (anti-pattern) | a live-row copy of the latest history value (`previous_value`) — removed |
| input-only field | captured from the request but logged elsewhere, never stored on the target row (`change_reason`) |
| discard guard | the single modal every dirty-form exit path funnels through |
| Discard changes vs Delete stage | revert unsaved edits in place vs delete the whole condition row |

### Cross-Project Applicability
- The **current-state-vs-history** rule applies to any audited entity (PPC bid changes, listing-price history, config edits): never mirror the latest history value onto the live row.
- The **single discard guard + `beforeRouteLeave`** pattern is a drop-in for any Vue SPA dirty-form page where edits must survive accidental navigation — and a reminder that a native `confirm` on click handlers does **not** cover router-level exits.
- The **extract-then-unset** trick is the safe migration step before dropping any "input-only" column from a table.

---

## SECTION 9 · LLM STANDARD CHECK

| Check | YES / NO |
| :---- | :---- |
| Could an unknown developer continue from this file without reading source code? | ✅ YES |
| Is every business threshold visible (not buried in code)? | ✅ YES |
| Is the GAP FOUND section completed or marked NONE? | ✅ YES |
| Is the COMPANY KNOWLEDGE EXTRACT section substantive? | ✅ YES |
| Are evidence locations referenced (commits + files + URL)? | ✅ YES |
| Is metadata complete (incl. blos_keys_used + hardcoded_thresholds)? | ✅ YES |
| Are section names per standard template (1–9)? | ✅ YES |
| Is this extracting knowledge — not just logging activity? | ✅ YES |

### Three-AM Standard Self-Assessment
A developer with no context could, from this file alone:
- **WHAT** was done — hardened the Rule Builder's unsaved-changes flow (one themed modal on every exit path incl. header nav / browser back via `beforeRouteLeave`, an in-place "Discard changes" button, Delete→"Delete stage", and a pre-reload `dirty` fix), and dropped the redundant `previous_value`/`change_reason` snapshot columns from `thresholds` across model/controller/both grids while re-routing `change_reason` to input-only history logging; committed + pushed `b20c211`, `bc1204a`.
- **WHAT** the structure is — `threshold_versions` is the single source of truth for change history; `thresholds` now keeps only current-state metadata (`last_changed_by/at`, `version`); the value-edit controller extracts `change_reason`, unsets it before the update, and logs it to a version row.
- **WHAT** is pending — **run `drop_threshold_snapshot_columns.sql` on the server (privileged, with the code)**; restore `change_reason` required when approved.
- **WHO** needs action — abiraj (run the ALTER); team lead (when to restore `change_reason`).
- **WHY** decisions were made — one guard over per-action confirms (native confirm missed router exits); drop snapshot columns over keeping them synced (duplication that can drift); keep capturing the reason but log it to history (right home for audit input).
- **WHERE** everything lives — repo `ledsone-centralizer` branch `Abiraj` (commits above); `RuleBuilder.vue`, `ThresholdConfigurationController.php`, `Threshold.php`, `ThresholdConfigurator.vue`, `OilConfigurator.vue`, `docs/sql/drop_threshold_snapshot_columns.sql`; server `/opt/lampp/htdocs/ledsone-centralizer`; live https://centralizer.vintageinterior.co.uk.
- **WHAT** to do next — deploy the code + ALTER together and `optimize:clear`; restore `change_reason` required when the team approves.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-06-19__abiraj__blos__REQ-04-D05.md`
- [x] Metadata complete — includes `blos_keys_used` and `hardcoded_thresholds`
- [x] Data-model (removed snapshot columns vs retained metadata, value-edit flow) in Section 3
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written (WHAT/WHO/WHY/WHERE)
- [x] Evidence referenced by commit hashes (`b20c211`, `bc1204a`) + files + live URL
- [x] ✅ **DELIVERED:** Rule Builder discard hardening — themed modal on every exit path, in-place Discard button, Delete→"Delete stage", post-save dirty fix
- [x] ✅ **DELIVERED:** `previous_value`/`change_reason` removed from `thresholds` (model/controller/both grids); `change_reason` re-routed to input-only history logging
- [x] ✅ **DELIVERED:** `drop_threshold_snapshot_columns.sql` migration drafted + historical-snapshot notes on seed SQL
- [x] ✅ **DELIVERED:** both committed + pushed to `Abiraj`; frontend builds clean
- [ ] ⚠️ **OPEN:** run `drop_threshold_snapshot_columns.sql` on the server as a privileged account (deploy with code, then `optimize:clear`) (abiraj)
- [ ] ⚠️ **OPEN:** restore the `change_reason` requirement when approved (deferred by request)

---
*DIGITWEB LK LTD — Daily Skill Increment System — v3.0 — June 2026*
