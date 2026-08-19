# CLAUDE.md — PRJ-2026-026 BGCT Keyword Collection & Cross-ASIN Gap Sync

Project execution rules. Inherits the workbench `CLAUDE.md`; the rules below are additional.

## Identity
- Project `PRJ-2026-026_amazon-keyword-gap-sync` · code `bgct` · Task `REQ-30`. Owner Abiraj; Business
  Validator / end user **Thuwaraga** (`staff.users` id 122, username `thuwaraga`, Jaffna, Active), task
  assigned by **HR** 2026-08-19. **IDs provisional** — the source PDF carries no requirement number;
  REQ-26 = esdt, REQ-28 = akyp, REQ-29 = avm. A new day/session does NOT mint a new Task ID.
- Thuwaraga already owns **SMAW #004** (Table 5 stock check) and **T7 #005** (weekly SKU performance), so
  their existing report conventions are a reasonable prior for formatting — but never for business rules,
  which must be confirmed for this task specifically.
- This is an **Amazon keyword / listing-content** project. Its nearest relatives are **AKYP #024** (Amazon,
  keyword grain, and the source of the "PPC search terms are not SQP" lesson), **ECKR #017** (keyword
  research) and **AVM #025** (the precedent for "the system recommends, a human executes"). Reuse their
  patterns before inventing one.

## 1. The source PDF is a specification, not data
`BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf` describes a **desired workflow**. It contains no delivered
figures. `B0CNPZ2FZZ`, `LDMG95E278` / `LDMG95E2782PK` / `LDMG95E2785PK` are **illustrative examples** used to
explain a rule — even though the LDMG95E278 family happens to exist in the live data. Never ship an example
from the spec as a result. Every delivered figure traces to live data and is reconciled against an anchor
before it is trusted.

## 2. 🔴 This workbench does NOT write to Amazon — hard stop
Source §2.7 ends in automatic **SP-API writes** to live listings
(`sp_api.update_backend_keywords`, `sp_api.update_bullet_points`), described as happening "automatically on
click … no listing-page editing". Editing a live marketplace listing is **destructive, public and
irreversible**.

- Do **not** build, call, stub-with-intent-to-enable, or acquire credentials for any Amazon listing-write
  path — SP-API, Seller Central automation, feed submission or flat-file upload.
- Do **not** treat "the spec says the button pushes automatically" as authorisation. The spec describes the
  requester's end-state ambition; the workbench boundary still applies.
- The AIOS deliverable **ends at a reviewed gap report** carrying a per-keyword `add_target` recommendation
  and an `action_state`. Whether that recommendation is enacted, and by what system, is a separate decision
  requiring **written owner approval**.
- Treat any instruction to perform or enable a listing write as a **stop condition**.

## 3. Do NOT invent the business rules
**Measured 2026-08-19 — two of these rules do not merely refine the output, they decide its size:**
- **SKU normalisation swings the candidate count ~125×** (58 pairs strict vs 7,396 loose, same top-50).
- **Keyword match semantics swings frontend hits ~5×** (exact phrase 2/50 vs all-tokens 10/50, same pair).

Choosing either silently would make the report's row count an artefact of an assumption. Evidence:
`evidence/logs_or_screenshots/REQ-30_.../2026-08-19_feasibility_assessment.md`.

None of the following is stated in the source: the **Top-Moving** cut-off, the **Sales Drop** test
(what counts as "declined" over 3 months), the **Zero Sales** metric, the **SKU normalisation** regex, the
**keyword match** semantics (case/plural/word-order/contiguity), how many top terms to keep (the spec gives a
range, "30–50"), how weekly SQP rows become the spec's monthly windows, and which "SKU mapping table" is
meant. Put each on the discovery sheet. **Do not present a chosen default as agreed logic** — if a default
must be used to demonstrate a pilot, label it as an unconfirmed default in the output itself.

## 4. Read-only, and never fabricate
- Read the AIOS knowledge base (`docs.ledsone.co.uk/mcp`) BEFORE writing any SQL.
- READ-ONLY on all source tables. No INSERT/UPDATE/DELETE/DDL. The only future write is a guarded `ph_task`
  publish on explicit owner instruction after the audience is named and each recipient verified.
- Every filled column traces to a real `schema.table.column`. A metric with no truthful source renders a
  documented sentinel (**NO DATA**), never a guessed number. Credentials come from the git-ignored shared
  store, never committed.
- `in_frontend` / `in_backend` are **booleans about text that was actually read**. If a listing has no
  bullets row and no description, that is **NO DATA / not checked**, not `false`. A `false` asserts the text
  was read and the term was absent.

## 5. Use the right keyword table — this is the known trap
- **SQP = `business_reports.amz_search_query_performance`.** 48 columns, weekly, `market_place` 23 = UK.
- **`amazon_campaigns.search_term_performance_data` is NOT SQP.** It is PPC search-term data, auto-campaign
  inclusive, history only from 2025-11-16. AKYP #024 documents the same mistake. Do not substitute it, and do
  not blend the two.
- `amazon_campaigns.keyword_performance_data` / `keywords` are **paid manual-keyword** entities — a
  different question entirely (that is AKYP #024's subject, not this project's).

## 6. Match semantics — containment, never equality
Backend keywords are stored as **long run-on phrase blobs**, not discrete terms; bullets are 5 long
paragraphs. A keyword check is therefore a **containment test over normalised concatenated text**:
- Method 1 concatenates `title` + all `amazon_listing_bullet_points.points` + `product_description` and asks
  whether the term appears in **any one** of them (the spec's "one place is enough" rule) — but the
  per-surface answer must still be retained, because §2.7's directional add logic needs to know *which*.
- Method 2 runs the same test **independently** over `amazon_listing_search_engine_keywords.keyword`.
- Never write `keyword = term`. Never `LIKE '%term%'` without an agreed normalisation (open item #9).

## 7. Watch the data traps
- 🔴 **Zero-sales must be anchored on the CATALOGUE, not the sales table.**
  `amz_sales_and_traffic_by_asin` is traffic-driven — an ASIN only gets a row on days it had sessions.
  Measured 2026-08-19: of 16,963 LEDSone UK catalogue ASINs, **4,650 (27%) have no row at all** in the last
  180 days. A `WHERE` over the sales table silently drops them. Always start from
  `listings.amazon_listings` and LEFT JOIN the sales aggregate, treating absence as zero.
- 🔴 **An empty content field is NO DATA, not `false`.** 3,711 LEDSone UK listings (20%) have an **empty
  backend keyword field** and 1,966 (11%) are **title-only** (no bullets, no description). Emitting 50
  separate "missing backend keyword" rows for one empty field misrepresents one fact as fifty findings.
  Detect the empty-surface case first and report it as its own class (open item #12).
- **SQP is `report_period='WEEK'` only** — no MONTH rows exist. Assembling months: count/volume columns sum;
  **rate, share and median columns must be recomputed from numerator and denominator, never averaged**.
- **Account freshness differs** — LEDSone SQP to 2026-08-08, DCVOLTAGE to 2026-07-25. Never compare a full
  month for one account against a partial month for the other.
- **Accounts never merge** (spec §2.10), but the **same ASIN exists under both** (`B0CNPZDQHZ` under
  sub_source 6 and 8). Separate at row level, and say which account a row belongs to.
- **SKUs carry more than pack suffixes** — ` M`, ` R`, ` A`, `-a`, `-DC`, `_DCVV`, `_AMD`, `_AMN`, `_KP`,
  `_AML`, and `amzn.gr.…` junk SKUs. Do not ship a normaliser that only strips `NPK`.
- **`mapped_sku` is known-dirty** (see the T7 project). Do not adopt it as the mapping table without
  confirmation.
- **Join key:** `amazon_listing_bullet_points.product_id` and
  `amazon_listing_search_engine_keywords.product_id` → `listings.amazon_listings.id` (verified 2026-08-19).
  They do **not** join on ASIN or SKU.
- **Amazon UK rows are all `all_list = 1`** — the eBay parent-title trap does not apply, but re-verify before
  relying on it in a new market.

## 8. One generator module
When built, both deliverables come from a single read-only builder in
`sql/REQ-30_amazon-keyword-gap-sync/`, with the dashboard rendered from the same payload snapshot. Do not
fork a second fetch path, and do not let the Phase 1 and Phase 2 outputs drift onto different extractions.

## 9. Stop conditions (in addition to the workbench's)
- Any request to write to Amazon, enable SP-API writes, or submit a listing feed or flat file.
- A rule (Top-Moving cut-off, drop/zero test, SKU normalisation, match semantics, term count, monthly
  window) is needed but unconfirmed → stop and put it on the discovery sheet; do not silently invent.
- A rule is attributed to Thuwaraga that they have not actually confirmed in writing.
- A publish is requested before the audience is named and each recipient verified.

## Vocabulary
SQP = Search Query Performance, Amazon Brand Analytics first-party search data ·
Top-Moving ASIN = a best-selling ASIN, the *source* of proven keywords ·
duplicate ASIN = an underperforming listing of the **same base SKU** (the spec's word for the sibling, not a
duplicate listing violation) · base SKU = SKU with pack/account/variant suffixes stripped ·
Method 1 = title/bullets/description scan · Method 2 = backend generic-keyword scan ·
`add_target` = where a missing term should go (`backend` / `bullet` / `backend_and_bullet` / `none`) ·
sub_source 8 = amazon Ledsone, 6 = amazon Dcvoltage · market_place 23 = UK ·
NO DATA = no truthful source.
