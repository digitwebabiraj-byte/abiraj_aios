## ── METADATA BLOCK ──────────────────────────────────────────────────────────

| Field | Value |
| :---- | :---- |
| **date** | 2026-06-18 |
| **developer** | abiraj |
| **project** | LEDsONE Centralizer (Centralized Admin / Operations Platform) |
| **project\_code** | blos |
| **phase** | IMPLEMENTATION (BUILD + DEPLOY) |
| **requirement\_id** | REQ-04 |
| **deliverable\_id** | REQ-04-D04 |
| **status** | COMPLETE — BLOS Rule Builder (the headline feature) built, wired, validated, polished; logic editing unified through it; committed + pushed to `Abiraj` (commits `989a682` … `aee9be7`); live on server. Deferred (by decision): FK constraints, restore `change_reason`. |
| **evidence\_location** | Git commits **`989a682`, `b25266a`, `4b05bd8`, `a1bd395`, `6a16b25`, `16dbadd`, `eed4fb0`, `80f5c5f`, `aee9be7`** on branch `Abiraj` (GitLab: `sajeesans2/ledsone-centralizer`) · new code: `resources/js/Account/components/{ruleLogic.js,RuleNode.vue}`, `resources/js/Account/Pages/RuleBuilder.vue` · changed: `resources/js/Account/{Router.js,Pages/includes/Header.vue,Pages/ThresholdConfigurator.vue,Pages/OilConfigurator.vue}`, `app/Http/Controllers/Api/ThresholdConfigurationController.php` · live: https://centralizer.vintageinterior.co.uk |
| **blos\_keys\_used** | Rule `BL-001` (CTR Collapse), stages initial/restore/kill; condition_logics rows 1–3; glossary metrics `GL-001…GL-003` (organic_ctr / organic_impressions / organic_ctr_days); thresholds `TH-001…TH-035`. Logic shape read+written: `IF GL-001 < TH-001 AND GL-002 >= TH-002 AND GL-003 <= TH-003`. |
| **hardcoded\_thresholds** | Operator list (UI dropdown + parser): `>= <= != < > =` (aliases tolerated on read: `== => =< <>`). Server code regex (unchanged): `^TH-\d+$ ^BL-\d+$ ^MAP-\d+$ ^GL-\d+$`. Parser keywords: leading `IF`/`WHEN` stripped, `AND`/`OR` joiners, `( )` grouping. Nesting UI: depth-accent palette `#0f766e #0369a1 #7c3aed #b45309 #be123c #0d9488`; single-item group collapses (no parens). Opaque sticky-cell fix colours: hover `#f1f7f6`, even-row `#f8fafc`. Bulk caps unchanged (1000 rows / 5 MB / 200 errors). **CHANGED today:** `condition_logic_rule` is now auto-generated + stored (was always NULL). **STILL TEMP:** `change_reason` optional (deferred again, by request). |
| **three\_am\_standard** | PASS |
| **llm\_queryable** | YES |
| **company\_knowledge\_candidate** | YES |
| **domain** | DATABASE \| BLOS-THRESHOLDS \| LARAVEL \| VUE-SPA \| RULE-ENGINE \| AMAZON-LISTINGS |

## File path:
# 2026-06-18__abiraj__blos__REQ-04-D04.md
# DigitWeb_Works_Abiraj/18_06_2026/

---

## SECTION 1 · SYSTEM STATE

- **Current system state at start of today:** After D03 the schema migration was finished and committed (`f8804b8`): all BLOS tables (`business_rules`, `condition_logics`, `glossary`, `rule_threshold_mapping`, `thresholds` with 35 rows) existed, were fully wired through models → controller → routes → Vue, and were live. The one thing the whole programme was built **for** — a visual way to author rule logic instead of hand-typing `condition_logic_by_ids` strings — **did not exist yet.**
- **What was working:** All admin tabs (CRUD), bulk CSV upload, OilConfigurator ("Business OS") value editing + YAML export, auth.
- **What was broken / missing:** (1) No Rule Builder. (2) The only way to edit rule logic was a **free textarea** on the Threshold Configurator's `condition_logics` tab — the exact typo-prone hand-typing the programme set out to eliminate. (3) Rules could reference deleted `GL-`/`TH-` codes — nothing validated them. (4) The "User Domain Access" sidebar count loaded only after clicking the tab. (5) A sticky-column rendering bug let scrolling text bleed through the Edit/Delete buttons. (6) Domain-access admin panels sat on the wrong tab (Thresholds).
- **Your starting point:** Build the **BLOS Rule Builder** (the headline feature), make it the single editing path for logic, then harden + polish.
- **Environment:** Laravel 9 + Vue 2 SPA. Server XAMPP/Linux at `/opt/lampp/htdocs/ledsone-centralizer`, MySQL `centralizer`. Local `.env` empty — frontend built with `npm run development` → `public/js/Account.js` (git-ignored). **Deploy clarified today:** the developer's saves go **directly onto the live server** (incl. the built bundle), so "save = live" after the frontend build; PHP controller changes are live once saved (`php artisan optimize:clear` only if a cached route/opcode is stale).

> **In plain terms:** Everything up to now was groundwork. Today we built the actual tool the whole project was for: a screen where a non-technical person clicks dropdowns to build a rule ("when organic CTR is below the floor AND impressions are above the minimum…") instead of typing cryptic code like `IF GL-001 < TH-001`. It shows the rule in plain English and in code, supports "either/or" branches with grouping, and saves both versions to the database. We then made it the **only** place logic is edited (so nobody can hand-type it wrong again), stopped rules from pointing at deleted metrics/thresholds, and did a round of UI fixes the user asked for.

---

## SECTION 2 · WHAT CHANGED TODAY

- **Change 1 — Rule-logic engine (`ruleLogic.js`, NEW, pure JS, no Vue → unit-testable):** `parse`/`parseSafe` (string → tree; tolerant of `IF`, newlines, double spaces, parentheses, AND-over-OR precedence; `parseSafe` returns `{ok:false}` so the UI can fall back to a raw-text editor and **never lose data**); `serialize` (tree → clean coded string, parentheses **only** where a nested group has >1 child, so existing flat rules re-save byte-identically); `serializePreview` (keeps `[metric]`/`[value]` placeholders for live preview); `toReadable` (tree + glossary/threshold maps → plain-English sentence for `condition_logic_rule`); helpers `emptyTree/isComplete/clauseCount/OPERATORS`. **Verified during the build** by round-tripping the 3 real BL-001 rules + hand-built nested examples through parse → serialize → parse: flat rules re-save byte-identically, nested rules survive — confirmed in the live app (the 3 BL-001 rows open in the builder and re-save unchanged).
- **Change 2 — Recursive builder component (`RuleNode.vue`, NEW):** renders a GROUP — clause rows inline (3 native `<select>`: metric = glossary term → saves `glossary_id`; operator; value = threshold label → saves `threshold_id`) and nested groups via **itself**. Controls: "Match ALL / ANY" (AND/OR) toggle, + Condition, + Either/or group, per-row move ↑↓ / wrap / remove, per-group ungroup / remove. Mutates the node + `$emit('change')` bubbling to the page.
- **Change 3 — Rule Builder page (`RuleBuilder.vue`, NEW):** business-rule sidebar + inline "New rule" (auto next `BL-###`); stage tabs (one `condition_logics` row per stage + "New"); the WHEN builder; **live preview (plain text + coded side by side)**; THEN `decision_output`; collapsible "Where this rule applies" context panel; save/load/delete via the existing admin `condition-logics` CRUD; `← Back`; accepts `?rule=BL-001&stage=initial` deep-link. **No schema/backend change** — fills `condition_logic_by_ids` (coded) **and** `condition_logic_rule` (readable, finally populated — was always NULL).
- **Change 4 — Wiring:** `Router.js` route `/rule-builder` (`requiresAuth + requiresAdmin`); `Header.vue` desktop + mobile nav entry (`v-if="isAdmin"`) + page-title map.
- **Change 5 — Unified logic editing:** on the Threshold Configurator `condition_logics` tab, **Add/Edit now launch the Rule Builder** (no typeable logic form); primary button reads "New in Rule Builder"; tab description updated; rows show **rule_name under rule_id**. Did **not** embed the builder in the cramped modal (would duplicate the editor).
- **Change 6 — Code validation (backend, `ThresholdConfigurationController`):** new `unknownConditionCodes()` extracts `GL-`/`TH-` codes from `condition_logic_by_ids` and **rejects** store/update (422, codes listed) if any don't exist in `glossary`/`thresholds`; same check wired into `bulkImport()` for the `condition_logics` tab.
- **Change 7 — Sidebar count fix:** `stats()` now returns `'domain_access' => User::count()` (matches the user↔domain matrix's one-row-per-user shape) so the User Domain Access count loads on page open, not only after clicking the tab.
- **Change 8 — UX polish (committed in small, reviewable units):** removed dead CSS + added a "single-item group does nothing" hint with inline Ungroup (`a1bd395`); **role + "no domains assigned" filters** on the User Domain Access tab (`6a16b25`); **restyled the sign-out dropdown** — glass panel, pop-in, avatar circle, role pill, logout icon, chevron rotates (`16dbadd`); **search box** for the Business OS domain view (display-only filter; hidden-by-search edits still save) (`eed4fb0`); **fixed sticky-Actions scroll-through** — translucent hover/even backgrounds made opaque (`80f5c5f`); **moved Domain access + Rename domain panels** off the Thresholds tab onto the User Domain Access tab (`aee9be7`); hid Edit on `rule_threshold_mapping` (links are add/remove only).

### Deliverables
- **Deliverable A —** BLOS Rule Builder: engine + recursive component + page, wired (route + nav), live. (`989a682`)
- **Deliverable B —** Logic editing unified through the builder; rule_name in table; mapping Edit hidden; domain_access count fix. (`b25266a`)
- **Deliverable C —** Server-side validation that rules only reference existing GL/TH codes (form + bulk). (`4b05bd8`)
- **Deliverable D —** UI polish/bug-fix set (6 commits) — dropdown, filters, search, sticky-column fix, panel relocation.
- **Deliverable E —** All committed + pushed to `Abiraj`; this EOD file.

Evidence: 9 commits `989a682`…`aee9be7`; new files `ruleLogic.js` (310), `RuleNode.vue` (~360), `RuleBuilder.vue` (~760). Rebuilt `public/js/Account.js` (git-ignored, deployed via direct-to-server save). No credentials included.

---

## SECTION 3 · POSTGRESQL / MCP / DATABASE FINDING

> Stack is **MySQL** (XAMPP). **No schema change today** — the Rule Builder reuses the existing `condition_logics` table; both `condition_logic_by_ids` and `condition_logic_rule` are `nullable TEXT`.

### The two columns that store a rule's logic (the "Way 2" decision, now implemented)

| Column | Role | Example | Written by |
| :---- | :---- | :---- | :---- |
| `condition_logic_by_ids` | structured/coded — **source of truth** | `IF GL-001 < TH-001 AND GL-002 >= TH-002` | builder `serialize()` |
| `condition_logic_rule` | human-readable sentence (was always NULL) | `IF organic_ctr is less than Organic CTR Floor and …` | builder `toReadable()` |

### The three identifiers a threshold carries (clarified today)

| Column | Example | Used for |
| :---- | :---- | :---- |
| `threshold_id` (PK) | `TH-001` | **goes into the rule logic** + `rule_threshold_mapping` |
| `threshold_key` (UNIQUE) | `amz_led_uk_organic_ctr_floor` | the **YAML registry** slug for AI agents / N8N |
| `label` | `Organic CTR Floor (Warning)` | human display in the UI |

> The rule references `TH-001` (the ID), **not** the key. The builder shows the `label`, saves the `threshold_id`. Same on the metric side: shows glossary `term` (`organic_ctr`), saves `glossary_id` (`GL-001`).

### Actual logic patterns in the live data (audited today)
All 3 existing rows are **flat AND-only** — zero OR, zero nesting:
```
1 initial : IF GL-001 < TH-001 AND GL-002 >= TH-002 AND GL-003 <= TH-003
2 restore : IF GL-001 >= TH-004 AND GL-003 <= TH-005
3 kill    : IF GL-001 < TH-007 AND GL-003 >= TH-008
```
Source stores them with embedded `\n` and irregular spacing; the parser normalises on read, the serializer writes clean single-line output.

### Validation now enforced server-side
`unknownConditionCodes($byIds)`: regex-extracts `GL-\d+` / `TH-\d+`, looks each up in `glossary` / `thresholds`, returns the missing ones; called in `condition-logics` store/update and per-row in `bulkImport`. Prevents a rule pointing at a deleted/renamed metric or threshold.

---

## SECTION 4 · GAP FOUND

- **Gap — nested-logic path is unverified against real data (LOW, OPEN):** the engine supports flat **and** nested (`((A OR B) AND C) OR D`) at any depth, but **no real rule uses nesting yet** (all 3 are flat AND), so the deep path is verified against hand-built examples while the flat path round-trips the 3 real rules byte-identically. First real nested rule should be sanity-checked. Owner: abiraj.
- **Gap — cross-table FK constraints still not added (LOW, OPEN — deferred):** with app-level validation now in place the urgency dropped. The one real remaining gap: `rule_threshold_mapping.threshold_id` has **no existence check anywhere** (a mapping can still point to a non-existent threshold). `condition_logics.rule_id` / `rule_threshold_mapping.rule_id` are already guarded by `businessRulesDestroy()` + the new validation. SQL drafted/commented in `docs/sql`; must run as a privileged DB user with an orphan pre-check first. Owner: abiraj (user opted to defer).
- **Gap — bulk CSV import still accepts logic as text (LOW, MITIGATED):** it is now run through the same GL/TH code validator, but it remains a power-admin path that bypasses the visual builder. Acceptable for migration; flagged for awareness. Owner: abiraj.
- **Gap — drag-to-reorder (P2) deferred (LOW, OPEN):** reordering inside a group is via ↑/↓ buttons; drag (`vuedraggable@2`) is the only deferred builder polish. Owner: abiraj.
- **Gap — `change_reason` still optional (LOW, OPEN — deferred by request):** the `// TEMP:` relaxation stays; user explicitly said restore it "some days after." Owner: abiraj / team lead.

---

## SECTION 5 · VALIDATION RULE ADDED OR CHANGED

### RULE ADDED — condition-logic codes must reference real glossary/threshold rows
- **Condition checked:** every `GL-###` and `TH-###` referenced inside `condition_logic_by_ids` must exist in `glossary` / `thresholds`.
- **Prevents:** a rule pointing at a metric or threshold that was deleted or renamed (silent broken rule; dangling reference downstream).
- **Where:** `ThresholdConfigurationController::unknownConditionCodes()`, called in `conditionLogicsStore`, `conditionLogicsUpdate`, and per-row in `bulkImport($tab)` for `condition_logics`. Returns 422 with the offending codes; the Rule Builder surfaces the message automatically.

### RULE ADDED — Rule Builder save gate (client)
- A rule is saveable only when a stage is set **and** every clause is complete (`metric` + `op` + `value`); otherwise Save is disabled with the reason shown. Half-built rules still **preview** (placeholders) but cannot persist.

### RULE CONFIRMED UNCHANGED — `change_reason` stays optional (deferred)
- Remains `nullable|string|max:1000` (`// TEMP:`). Restore to `required|min:10` only when the team re-enables the audit-reason requirement.

---

## SECTION 6 · FAILURE MODE OR EDGE CASE

- **Failure mode (RESOLVED) — scrolling text bleeding through the sticky Actions column (LOW, visual):** Trigger — the pinned Edit/Delete cell used **translucent** backgrounds (`rgba(15,118,110,0.06)` on hover, `0.95` on even rows), so horizontally-scrolling row text showed **through** the buttons. Fix — made the cell **and** its `::before` background layer fully opaque (`#f1f7f6` hover, `#f8fafc` even) with the same visual colour. (`80f5c5f`)
- **Edge case (HANDLED) — messy stored logic strings:** parser collapses whitespace + newlines, strips leading `IF`/`WHEN`, tolerates glued operators (`GL-001<TH-001`) and operator aliases (`=<`, `==`, `<>`). Unparseable input → `parseSafe` returns `{ok:false}` → UI shows a raw-text editor with a "Parse" button, so the original string is **never destroyed**.
- **Edge case (HANDLED) — single-item group:** a group with one condition collapses on serialize (no parentheses) because AND/OR needs ≥2 operands. The builder now shows a hint + inline Ungroup so users aren't confused that "the group did nothing".
- **Edge case (HANDLED) — editing a row hidden by Business OS search:** the search is **display-only**; editing, change-tracking, and Save All operate on the full row set, so a hidden-by-search edit is still saved (no data loss).
- **Edge case (HANDLED) — AND/OR precedence without parentheses:** `A AND B OR C` parses as `(A AND B) OR C` (AND binds tighter than OR) and serialises with the implied parentheses, so meaning is never ambiguous.

---

## SECTION 7 · DECISIONS MADE TODAY

- **Decision: build the recursive, nesting-capable engine ("option C"), not flat-only ("B").** Alternatives: flat AND/OR rows only; one level of grouping. Reason: the user expects nested logic ("it has chance to come"), and the expensive part (recursive parser/serializer + tree model) **cannot be cheaply retrofitted** — building flat first would mean a later rewrite. One engine now handles flat + nested in the same builder; a flat rule is just a tree with no groups (re-saves identically). Trade-off: a bit more build time + the deep path is unverified against real data. Approved: user.
- **Decision: one editor for logic = the Rule Builder; the raw tab is read-only/launcher.** Alternatives: embed the builder inside the Threshold Configurator modal; keep the free textarea. Reason: the modal is too cramped for a nested builder, and embedding would **duplicate** the editor. So `condition_logics` Add/Edit launch the dedicated page; the table just displays the logic. Trade-off: a page navigation instead of in-place. Approved: user.
- **Decision: group-level AND/OR (Match ALL / ANY), not a per-row joiner.** Reason: a per-line AND/OR mix (`A AND B OR C`) is **ambiguous** for non-technical users; the box model makes precedence explicit and visible — you mix by adding a nested "either/or" group. Trade-off: mixing needs an extra group, but it is unambiguous. Approved: user (after worked examples).
- **Decision: keep BOTH domain-access editing paths, move the panels to the right tab.** Reason: the "Domain access" + "Rename domain" panels are access-administration, not threshold data, so they belong on the User Domain Access tab; the per-row Edit on the matrix is kept too. Implemented as a one-line render-condition flip (block is self-contained). Approved: user.
- **Decision: hide Edit on `rule_threshold_mapping`, keep Add + Delete.** Reason: a mapping is a pure link — nothing meaningful to *edit*; you create or remove links. Keep Delete so mistakes are fixable. Approved: user.
- **Decision: defer FK constraints + `change_reason` restore.** Reason: app-level validation now covers the main flows; user chose to defer. Trade-off: `rule_threshold_mapping.threshold_id` stays unprotected at the DB level for now.

---

## SECTION 8 · COMPANY KNOWLEDGE EXTRACT

### The rule-logic model (how a condition is structured)
A condition is a **tree**: a *clause* is `{metric, operator, value}` (e.g. `organic_ctr  is less than  Organic CTR Floor`); a *group* joins its children with **one** operator — **Match ALL** (AND) or **Match ANY** (OR). The root is always a group. **Mixing AND and OR is done by nesting a group** inside another, which serialises to parentheses. A flat rule is a tree with no sub-groups → no parentheses.

### Reusable Logic / Formula
- **Serialize:** `IF ` + recurse; wrap a child group in `( … )` **only** if it has >1 child; join a group's children with its operator. → flat rules stay flat, nested rules get exactly the parentheses they need.
- **Parse (recursive descent):** tokenize (strip `IF`/`WHEN`, space-out parens + operators, split) → `parseOr → parseAnd → parsePrimary` (OR is lower precedence than AND) → flatten same-operator nested groups. Tolerant input, opaque output. Falls back to raw-text mode if it can't parse — data is never lost.
- **Readable sentence:** map `GL-id → glossary.term`, `TH-id → thresholds.label`, operator → words (`<`→"is less than", `>=`→"is at least", …); same parenthesis rule as serialize.
- **Code-existence guard:** regex-extract `GL-\d+`/`TH-\d+` from the expression, `whereIn` against `glossary`/`thresholds`, reject the difference.

### Canonical Vocabulary

| Term | Meaning |
| :---- | :---- |
| Rule Builder | the visual screen that authors `condition_logics` rows (no typing) |
| clause | one condition: metric `op` threshold (`organic_ctr < CTR Floor`) |
| group / either-or group | a box that joins its rows by ALL (AND) or ANY (OR); nest to mix |
| coded vs readable | `condition_logic_by_ids` (GL/TH codes) vs `condition_logic_rule` (plain English) |
| threshold_id vs threshold_key | `TH-001` (used in logic) vs `amz_…_floor` (used in YAML export) |
| raw-text fallback | editor shown when an existing string can't be parsed, so it is never lost |

### Cross-Project Applicability
- The **pure parse/serialize/readable engine** (framework-free and self-contained, so it stays easy to verify in isolation) is a reusable pattern for any "store a structured expression as a string + edit it visually" requirement (CFIS filters, PPC rules, KMS query builders).
- The **recursive self-rendering group component** (group renders clauses inline + nests itself for sub-groups; events bubble up) is a drop-in for any nested AND/OR builder.
- The **"opaque background required on sticky cells"** lesson: any `position:sticky` table column needs a **fully opaque** background on every row state (normal/even/hover) or scrolling content bleeds through.

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
- **WHAT** was done — built the BLOS Rule Builder (engine `ruleLogic.js` + recursive `RuleNode.vue` + page `RuleBuilder.vue`), wired it (route + admin nav), made it the single logic-editing path, added server-side GL/TH code validation, fixed the domain-access sidebar count, and shipped a 6-commit UI polish/bug-fix set; committed + pushed `989a682`…`aee9be7`.
- **WHAT** the structure is — rule logic is a tree of clauses + AND/OR groups, serialised to `condition_logic_by_ids` (parens only where a nested group needs them) and auto-described into `condition_logic_rule`; reuses the existing `condition_logics` table (no schema change).
- **WHAT** is pending — verify the nested path on the first real nested rule; FK constraint on `rule_threshold_mapping.threshold_id`; restore `change_reason` required; optional drag-to-reorder.
- **WHO** needs action — abiraj (FK, nested verification, drag P2); team lead (when to restore `change_reason`).
- **WHY** decisions were made — recursive engine over flat (avoid a rewrite when nesting arrives); one visual editor over a typeable form (no more hand-typed logic); group-level AND/OR over per-row (unambiguous); panels moved to the access tab (correct home).
- **WHERE** everything lives — repo `ledsone-centralizer` branch `Abiraj` (commits above); new files under `resources/js/Account/components` + `…/Pages/RuleBuilder.vue`; server `/opt/lampp/htdocs/ledsone-centralizer`; live https://centralizer.vintageinterior.co.uk.
- **WHAT** to do next — verify a real nested rule end-to-end; add the one missing FK; optionally drag-reorder; then revisit `change_reason`.

---

## ── SUBMISSION CHECKLIST ─────────────────────────────────────────────────────

- [x] File named correctly: `2026-06-18__abiraj__blos__REQ-04-D04.md`
- [x] Metadata complete — includes `blos_keys_used` and `hardcoded_thresholds`
- [x] Data-model (two logic columns, three threshold identifiers, live logic patterns) in Section 3
- [x] Section names 1–9 match standard template
- [x] No credentials, passwords, or API keys included
- [x] LLM Standard Check table completed
- [x] Three-AM Standard self-assessment written (WHAT/WHO/WHY/WHERE)
- [x] Evidence referenced by commit hashes (`989a682`…`aee9be7`) + files + live URL
- [x] ✅ **DELIVERED:** BLOS Rule Builder (engine + recursive component + page) — built, wired, live
- [x] ✅ **DELIVERED:** logic editing unified through the builder (no typeable logic form); rule_name in table
- [x] ✅ **DELIVERED:** server-side GL/TH code validation (form + bulk import)
- [x] ✅ **DELIVERED:** domain_access sidebar count fix
- [x] ✅ **DELIVERED:** UI polish/bug set — dropdown, filters, Business OS search, sticky-column fix, panel relocation, mapping Edit hidden
- [x] ✅ **DELIVERED:** all committed + pushed to `Abiraj`
- [ ] ⚠️ **OPEN:** verify the nested-logic path on the first real nested rule (abiraj)
- [ ] ⚠️ **OPEN:** FK constraint on `rule_threshold_mapping.threshold_id` (abiraj — deferred)
- [ ] ⚠️ **OPEN:** restore the `change_reason` requirement when approved (deferred by request)
- [ ] ⚠️ **OPEN:** optional drag-to-reorder in the builder (P2, abiraj)

---
*DIGITWEB LK LTD — Daily Skill Increment System — v3.0 — June 2026*
