# TASK_REGISTER — PRJ-2026-010_ebay-price-checker

Canonical index of tasks in this project. One requirement = one Task ID.

## Tasks

| Task ID | Deliverable | Source ref | Status | Evidence | Validation |
|---|---|---|---|---|---|
| REQ-12_ebay-price-checker | eBay Price Checker — cross-channel price-drift report over live eBay UK & DE listings across Thinesh's 13 accounts. Target = Amazon ×0.90 (lowest), else website ×1.10, else DATA MISSING; tolerance ±£0.50/£1.00 at the £20 band; priority by money-at-risk. **D01 report DELIVERED · PUBLISHED (4 users: ids 264, 299–301, released) · SIGNED OFF — CLOSED 2026-07-16.** | `Ebay System Task -Thinesh.xlsx` (13-col shape, legend, 7 **mock** rows) + the owner's **CONFIRMED BUSINESS RULE** + **Thinesh Q1–Q8** (both chat-captured). Task ID **minted with owner confirmation 2026-07-16** — the source carries no requirement id. | **D01 DELIVERED (read-only) 2026-07-16 — CLOSED.** `ph_task` ids **264, 299–301**. Technically GREEN (8/8 reconciled); all decisions + reviewer gates signed off 2026-07-16. | `evidence/final_outputs/REQ-12_.../` (UI xlsx · dashboard · decision sheet · scripts) + `sql/REQ-12_.../d01_price_checker_pull.sql` + `validation/REQ-12_.../2026-07-16_validation.md` | 8/8 DB reconciliation PASS; 0 formula errors; 0 blanks; dashboard KPIs = xlsx. Business + reviewer sign-off **complete 2026-07-16**. |

## REQ-12-D01 — deliverable detail (2026-07-16)
- **Scope:** a populated read-only price-drift report over **126,070 live eBay UK & DE listings**, in three
  artifacts (13-column UI xlsx, full-screen dashboard HTML, decision sheet) + build/publish scripts.
- **Rule applied:** owner CONFIRMED BUSINESS RULE + Thinesh Q1–Q8. Amazon-first (lowest), website
  fallback, else DATA MISSING; ROUND(raw,2); £20 tolerance band; priority by money-at-risk; bundles = sum
  components.
- **project_code `epc`** — minted with owner confirmation 2026-07-16; verified unused in `ph_task` before
  publish.
- **Requirement doc:** `DigitWeb_Works_Abiraj/16_07_2026/2026-07-16_abiraj_REQ-epc_REQ-12-D01.md`.
- **Published — 4 users** to `tech_team_outputs.ph_task`, all `project_code=epc`,
  `assigned_user_team=ebay_priors`, `released`, each the same 17 MB version-3 dashboard (Export-CSV +
  taller table): **id 264 (Thinesh), 299 (Jarsini), 300 (kobiga), 301 (powsteena)**. Guarded `temp_user`
  INSERTs (dry-run + manual duplicate guard — no UNIQUE on `task_id` in live; names verified live against
  `staff.users`, `Jarsini` ≠ `Jasmini`). Independently re-verified via the Postgres MCP (four `epc` rows).
  Detail: `evidence/logs_or_screenshots/REQ-12_.../2026-07-16_d01_delivery_and_publish_record.md`.

## Decisions — RESOLVED & SIGNED OFF 2026-07-16 (audit trail)
- **Shipping basis** — signed off (Sajeesan / DB owner) on an item-price basis. ⚠ **Data note (true
  regardless of sign-off):** Status compares item price only; a shipping-aware refresh, if scoped, = future
  REQ-12-D02. The live `ph_task` descriptions keep the "item-price" note for end users.
- **Sunsone (`so_926407`) / Retro LED (`re6865`)** — identities confirmed (Thinesh).
- **Amazon ×0.90 (base ×1.08) vs the documented eBay target base ×1.10** — confirmed (Thinesh).
- **Priority £5/£2 cutoffs** — confirmed (Thinesh).
- **Q8 two new status values** — decided (Sajeesan).
- **FX** for the German EUR accounts — confirmed (Thinesh).
- **Bundles** — bundle-pricing policy confirmed (Thinesh); sum-of-components stands (~11%).

## Corrections during the build (honest record)
1. **Matching rebuilt against the AIOS KB** — `all_list=1` (+6,392 rows), Amazon `_`-suffix, ENC→sku_original,
   PK pack qty. Direct Amazon matches +22%. The earlier builds were wrong for having skipped the KB.
2. **`concat_ws` NULL-drop bug** — 570 rows lost their image field and shifted columns; caught by a
   field-count assertion, repaired, asserted.
3. **VAT/postage hypothesis refuted; ENC-recovery prediction wrong** — both recorded so the confident-but-
   wrong cause claims are not repeated.

## Onboarding (this session, 2026-07-16)
- Registered the project; authored the five standing docs (README, PROJECT_HOME, SYSTEM_REFERENCE, CLAUDE,
  TASK_REGISTER) and added the row to the root `PROJECT_REGISTER.md`.
- COPY-imported the source xlsx (SHA-256 verified, Downloads original preserved); captured the chat-only
  CONFIRMED BUSINESS RULE + Thinesh Q1–Q8 verbatim; wrote `SOURCE_MANIFEST.md` + import evidence.
- Registered the delivered outputs + build/publish scripts, the canonical + audit SQL, the source-audit /
  AIOS-rules correction log, the delivery + publish record, and the validation report.
- **No source table written.** The only DB writes are the guarded publishes of the dashboard to `ph_task`
  (ids 264, 299–301) + the V2/V3 in-place refreshes, all on owner instruction.
- **Committed + pushed to git `main`.**

## Automation — WEEKLY AUTO-REFRESH BUILT 2026-07-16 (part of REQ-12, not a separate task)
`automation/` — unattended weekly run via Windows Task Scheduler (**Monday 10:30**), following the
**PRJ-2026-011 (EBPD)** pattern: pull live prices from `ledsone` → validate → rebuild the dashboard →
guarded UPSERT of all 4 `ph_task` rows (264, 299–301) in place, `version_level` bumping each run.
Files: `epc_weekly_run.py` (runner) · `epc_build_html.py` (**single source of truth for the UI**) ·
`run_epc_weekly.bat` · `register_scheduled_task.ps1` · `epc_secrets.template.bat` · `epc_alert.ps1`
(desktop alert on failure, auto-clears on success) · `check_status.bat`. **Fails closed** — 0 rows, a
row-count floor, non-reconciling counts, a bad render or missing credentials all abort *before* any write,
so the last good dashboard stays live. No credential in any tracked file (`epc_secrets.bat` is git-ignored).
`--dry-run` builds and validates without publishing. See `automation/AUTOMATION_README.md`.

**✅ SWITCHED ON 2026-07-20.** `EPC_Weekly_Price_Checker` is registered in Windows Task Scheduler; the
DB-connected `--dry-run` passed (published nothing, as designed). Credentials come from the **shared
global store** (`05_documentation/capability/shared_db_credentials/`) — no `epc_secrets.bat` on this
machine. **Next run: Monday 2026-07-27 10:30.** The time was moved from 07:00 to **10:30** so it never
overlaps the other jobs on the same restricted `temp_user` account, whose pool intermittently returns
*"too many clients"*: FRRC 09:00 (day 8) · ERA 09:30 (5th) · **EBPD 09:30 Monday** (same weekday as EPC).

## One next action
**None required — it runs itself weekly.** Optional: `Start-ScheduledTask -TaskName
"EPC_Weekly_Price_Checker"` to refresh the four dashboards now instead of waiting for 27 July (they
currently show 16-July prices). Optional later: a shipping-aware Status rebuild (REQ-12-D02).

## Rule
A new day or Claude session does **not** create a new Task ID. Keep using `REQ-12_ebay-price-checker` until
it is formally closed; only a genuinely new requirement (with owner confirmation) gets a new
deliverable/task id.
