# Evidence Note — REQ-04-D07 Deep Continuation Package

Date: 2026-07-07
Supports: the nine documents in
`../../final_outputs/REQ-04_ledsone-centralizer-user-skill/` (the D06 skill file, updated in
place to Rev 2, plus eight D07 documents).
Method: exhaustive **read-only** analysis of the `ledsone-centralizer` repository
(`C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer`) on 2026-07-07, including git
history (read-only: `log`, `show`, `blame`, pickaxe `-S`/`-G`). No application file, config, or
database was modified. No git commit or push. No source code was copied into AIOS (map by
reference only).

## How the package was produced

Six parallel analysis passes, each writing one document, then a synthesis pass:

| Document | Coverage | Key result |
|---|---|---|
| API_REFERENCE | 80 routes (57 BLOS deep, 23 shared/brief) | Public admin-creation route; public user dump; 22 dead routes |
| DATA_DICTIONARY | 12 BLOS/file/user tables deep, 41 shared brief | `ThresholdChangeRequest`/`ThresholdDependency` models deleted; schema doc stale; fresh-DB hazard |
| UI_REFERENCE | 20 `resources/js/Account/` files | Admin controls hidden not disabled; change_reason check off; Replace-diff only for text ≤900 KB |
| SECURITY_AND_DEPLOY | Auth chain + deploy runbook | 12 findings incl. committed prod credential, CORS `*`+creds, sign-out not revoking token |
| VERIFICATION_FINDINGS | 4 open questions + tracker cross-check | All 4 settled; 13 tracker mismatches; 6 nonexistent POS controllers |
| SHARED_MODULES_INVENTORY | ~50 non-BLOS files | Owners: sajeesans2 (POS/order/base), gajan (PPC/ETL); no SPA page for any |
| CODE_MAP | 209 files walked (~105 deep, ~104 one-line) | BLOS backend = 1 controller; rule engine = 3 frontend files; BLOS tables via hand-run SQL |
| CONTINUATION_GUIDE | synthesis | 9-stage status re-baselined; prioritised next steps; first-week checklist |
| user_skill_file (Rev 2) | updated in place | 4 open questions resolved; §12 rewritten; body claims corrected |

## Anti-fabrication control (important)

One analysis agent (code map) initially returned sub-agent content that did **not** match the
repository (it invented an approval-workflow method set, wrong `Threshold` columns, a
`managed_files` table, and a modern `users` schema). This was caught by direct spot-checks
against the repo and the agent was **re-run under strict "read every file yourself, no
sub-agents" instructions**; the final CODE_MAP was rebuilt from first-hand reads. In addition,
the coordinator independently spot-verified, against the live repo, the load-bearing claims of
every other document:

| Claim spot-checked | Result | Evidence |
|---|---|---|
| `Threshold` real 24-column fillable | Confirmed | `app/Models/Threshold.php` |
| No approve/reject/requestChange anywhere | Confirmed absent | grep of `app/` = 0 hits |
| Commit `f8804b8` removed change-request/impact-approval | Confirmed | `git show f8804b8` message |
| `add-new-users` public since `24169cf` (sajeesans2) | Confirmed | `git log` |
| CORS `*` + credentials | Confirmed | `config/cors.php:22,32` |
| Sign-out doesn't call `/api/logout` | Confirmed (live path `Header.vue`) | `Header.vue:232-240` |
| `.vscode/sftp.json` plaintext prod password + uploadOnSave | Confirmed | `.vscode/sftp.json` |
| Token mutator truncates to 32 chars | Confirmed | `app/Models/User.php:105-111` |
| Fresh-DB hazard: `proposed_value AFTER previous_value` | Confirmed | migration `2026_04_28_000002:16` |
| Rule engine files exist at `components/` | Confirmed | `RuleNode.vue`, `ruleLogic.js` |

## Secret handling

The committed production password found in `.vscode/sftp.json` is recorded as a **finding**
(location + nature) but its value is **not reproduced** in any AIOS document — verified by
grep across the whole project folder (0 hits). This complies with the workbench "no secrets in
files" rule.

## Closure gates

A fresh, no-context reviewer agent ran two tests before sign-off: a **queryability test**
(answer 5 continuation questions from the package alone) and a **completeness critic**
(cross-check package claims against the repo, hunt for gaps/contradictions). Result recorded in
`../../validation/REQ-04_ledsone-centralizer-user-skill/2026-07-07_REQ-04-D07_closure_gates.md`.

## Integrity statement

No file in `ledsone-centralizer` or the Desktop archive was created, modified, or deleted.
All writes occurred inside `projects/PRJ-2026-003_blos-project-sentinel/`. No commit or push.
