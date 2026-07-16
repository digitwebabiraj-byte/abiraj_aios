# TASK_REGISTER — PRJ-2026-010_ebay-price-checker

Canonical index of tasks in this project. One requirement = one Task ID.

## Tasks

| Task ID | Deliverable | Source ref | Status | Evidence | Validation |
|---|---|---|---|---|---|
| REQ-12_ebay-price-checker | eBay Price Checker — cross-channel price-drift report over live eBay UK & DE listings across Thinesh's 13 accounts. Target = Amazon ×0.90 (lowest), else website ×1.10, else DATA MISSING; tolerance ±£0.50/£1.00 at the £20 band; priority by money-at-risk. **D01 report DELIVERED & PUBLISHED 2026-07-16 (`ph_task` id 264, released) — NOT signed off.** | `Ebay System Task -Thinesh.xlsx` (13-col shape, legend, 7 **mock** rows) + the owner's **CONFIRMED BUSINESS RULE** + **Thinesh Q1–Q8** (both chat-captured). Task ID **minted with owner confirmation 2026-07-16** — the source carries no requirement id. | **D01 DELIVERED (read-only) 2026-07-16** — `ph_task` **id 264**. Technically GREEN (8/8 reconciled); **shipping-blind, unsigned**. | `evidence/final_outputs/REQ-12_.../` (UI xlsx · dashboard · decision sheet · scripts) + `sql/REQ-12_.../d01_price_checker_pull.sql` + `validation/REQ-12_.../2026-07-16_validation.md` | 8/8 DB reconciliation PASS; 0 formula errors; 0 blanks; dashboard KPIs = xlsx. Reviewer + business sign-off **pending**. |

## REQ-12-D01 — deliverable detail (2026-07-16)
- **Scope:** a populated read-only price-drift report over **126,070 live eBay UK & DE listings**, in three
  artifacts (13-column UI xlsx, full-screen dashboard HTML, decision sheet) + build/publish scripts.
- **Rule applied:** owner CONFIRMED BUSINESS RULE + Thinesh Q1–Q8. Amazon-first (lowest), website
  fallback, else DATA MISSING; ROUND(raw,2); £20 tolerance band; priority by money-at-risk; bundles = sum
  components.
- **project_code `epc`** — minted with owner confirmation 2026-07-16; verified unused in `ph_task` before
  publish.
- **Requirement doc:** `DigitWeb_Works_Abiraj/16_07_2026/2026-07-16_abiraj_REQ-epc_REQ-12-D01.md`.
- **Published:** `tech_team_outputs.ph_task` **id 264** — `task_id=epc_Thinesh_ebay_price_checker-V1`,
  `assigned_user=Thinesh`, `assigned_user_team=ebay_priors`, phase 1 / version 1 / **released**, 17 MB
  dashboard. Guarded `temp_user` INSERT (dry-run + manual duplicate guard, no UNIQUE on `task_id` in live).
  Independently re-verified via the Postgres MCP. Detail:
  `evidence/logs_or_screenshots/REQ-12_.../2026-07-16_d01_delivery_and_publish_record.md`.

## ⚠ What D01 does NOT settle — read before treating it as "the system"
- **Shipping-blind.** Status compares item price only; the AIOS KB warns this misreports correctly-priced
  listings, and the shipping source is not yet identified (`amazon_listings.shipping_id`). **Rank, do not
  reprice.** The defining open item.
- **Sunsone (`so_926407`) / Retro LED (`re6865`)** — inferred account identities, not confirmed by Thinesh.
- **Amazon ×0.90 (base ×1.08) vs the documented eBay target base ×1.10** — a ~2% gap to reconcile.
- **Priority £5/£2 cutoffs** — developer defaults; Q6 gave a direction, not numbers.
- **Q8 two new status values** — not yet in `staging_ai.pricing_safe_status_reason_catalog_v1` (Sajeesan).
- **FX** for the German EUR accounts is undefined.
- **Bundles** — the sum-of-components rule recovers only ~11%.

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
- **No source table written.** The only DB write is the publish of the dashboard to `ph_task` id 264
  (already done, on owner instruction).

## One next action
Route the open items in order: **(1) shipping basis** to Sajeesan / the DB owner (it gates repricing);
**(2) Sunsone / Retro LED identity** + **Priority cutoffs** + **FX** + **the base-×1.08-vs-×1.10 gap** to
Thinesh; **(3) the Q8 two new status values** to Sajeesan before the production catalog is touched. Then
engage Sajeesan (technical) and Tamil Selvan (queryability) for sign-off.

## Rule
A new day or Claude session does **not** create a new Task ID. Keep using `REQ-12_ebay-price-checker` until
it is formally closed; only a genuinely new requirement (with owner confirmation) gets a new
deliverable/task id.
