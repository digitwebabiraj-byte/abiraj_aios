# SOURCE MANIFEST — REQ-30 BGCT Keyword Collection & Cross-ASIN Gap Sync

Imported 2026-08-19. This is the **original requester input**, verbatim. It is a **specification** (a desired
two-phase workflow, its step sequence, decision logic and output contract) — **not data**. Never copy an
example identifier from it into a deliverable.

| File (in this folder) | Original name | Type | What it defines |
|---|---|---|---|
| `2026-08-19_source_bgct-keyword-workflow-spec.pdf` | `BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf` | PDF, 5 pages | Phase 1 (8-step SQP keyword collection + a 5-pattern interpretation guide) · Phase 2 (7-step cross-ASIN gap detection) · §2.7 review-button and directional-add logic · §2.8 pseudocode · §2.9 the 12-column output contract · §2.10 a 7-point QA checklist. |

Header: *"BGCT · Manual Keyword Collection & Automated Backend Sync Workflow — Amazon UK LED Bulb Listings ·
Automation Team Reference · v2.1"*.
Sources cited by the document itself: *BGCT Best Practice (T2) · Product Page Data Sheet · Seller Central SQP
· SP-API Orders & Listings · Aug 2026*.
Footer: *"For Automation Team Use · Internal Reference Only · Aug 2026"*.

## Page-by-page

### Page 1 — Document purpose + Phase 1 steps 1–5
- **Purpose:** two-phase keyword process for Amazon UK LED bulb listings. Phase 1 (Method A) is *"unchanged
  from the original BGCT reference"*. **Phase 2 is new.**
- **Phase 1 definition:** SQP shows *"which actual search terms customers used to find and click your
  specific ASINs. This is first-party, highest-accuracy data — not estimated."*
- **Step 1 — Identify Top-Moving ASINs.** Business Report, separately for **DCVOLTAGE UK** and **LEDSone
  UK**. *"Rank ASINs by units/sessions and record each Top-Moving ASIN together with its SKU."* This list is
  the input for every later step in both phases. **No cut-off or Top-N is stated.**
- **Step 2 —** Seller Central → Brand Analytics → Search Analytics → Search Query Performance → **ASIN View**
  (Brand View is explicitly rejected as too aggregate).
- **Step 3 —** one ASIN per run (example `B0CNPZ2FZZ`); loop per ASIN in automation.
- **Step 4 — Reporting period.** Monthly range, **last 3 consecutive months one month at a time, not as a
  combined range**; extend to 6 months if 3 is thin. *"Consistent date ranges are essential."*
- **Step 5 —** sort Search Query Volume descending; **record the top 30–50 terms per ASIN** (a range, not a
  number).

### Page 2 — Phase 1 steps 6–8, interpretation guide, Phase 2 steps 1–2
- **Step 6 — secondary filters:** cross-filter by **Click Rate** and **ASIN Share %** (*"low share on
  high-volume = opportunity gap"*); **filter out terms with zero conversion**. No numeric thresholds given.
- **Step 7 — long-tail:** 3–6 word phrases, **moderate volume (50–500/mo)**, high click or conversion.
  *"long-tail gold — specific, buyer-intent terms that competitors often miss."*
- **Step 8 — export CSV.** Required columns: `search_term`, `search_query_score`, `search_query_volume`,
  `total_count` (impressions), `asin_count`, `asin_share`, `click_rate`. Naming `SQP_[ASIN]_[YYYY-MM].csv`.
  **This export is the input to Phase 2.**
- **"What to Look For in SQP Data" (5 patterns):** High Volume + High Conversion → *"must be in title Zone
  A"* · High Volume + Low ASIN Share → optimise title Zone A · Low Volume + High Click Rate → long-tail for
  bullets and backend · 3–6 word phrases → natural long-tail · Seasonal Patterns → Oct/Nov spikes = gifting
  keywords. *(Note: "title Zone A" is used without definition.)*
- **Phase 2 definition:** takes Phase 1's confirmed terms and checks whether *"other listings of the same
  product — declining or generating no sales — already carry those terms."* *"Per MD instruction, this runs
  end-to-end with zero manual keyword lookup, and is processed separately for each seller account."*
- **Step 1 — find underperformers:** (a) **Sales Drop** — *"orders declined or stopped over the last 3
  consecutive months"*; (b) **Zero Sales** — *"no orders at all in the last 6 months"*. Record ASIN + SKU.
  **Neither test is quantified.**
- **Step 2 — normalise SKUs:** *"Strip pack-size suffixes before matching — e.g. `LDMG95E278` (single) vs
  `LDMG95E2782PK` / `LDMG95E2785PK` (2-pack / 5-pack) all resolve to the same base SKU."* Match the base SKU
  against the Top-Moving list, *"whichever variant (single or pack) is actually the Top-Moving one"*. *"Where
  a listing's stored SKU doesn't match its real product, correct it against the **SKU mapping table**."*
  **The mapping table is referenced but not identified.**

### Page 3 — Phase 2 steps 3–7, §2.7 button logic, §2.8 pseudocode (start)
- **Step 3 —** take the Top-Moving ASIN's confirmed terms, run the two checks against its underperforming
  twin.
- **Step 4 — Method 1:** scan **Title, Bullets and Description together as one group**. *"If a keyword
  appears in any one of these three places, that's enough — mark it placed."*
- **Step 5 — Method 2:** separately scan the **backend (generic) keyword field**. *"This check is independent
  of Method 1 — a term can pass one and fail the other."*
- **Step 6 —** the system pre-computes every check; the dashboard shows keyword-by-keyword tick/missing for
  both methods, with exactly two possible actions.
- **Step 7 —** the full pipeline re-runs **monthly**, once per brand account, each reported independently.
- **§2.7 Review Buttons & Directional Add Logic** — quoted:
  - *Button 1 "All Keywords Present · Mark Reviewed"* — shown **only** when a keyword ticks in **both**
    methods for **every** top term.
  - *Button 2 "Add Missing Keywords"* — *"Where the keyword sends it depends on where it's missing, not a
    blanket backend push"*:
    - present frontend, missing backend → **backend keyword field only**
    - present backend, missing frontend → **bullets only (not title, not description)**
    - missing from both → **backend AND bullets**
  - *"All writes happen automatically on click via the SP-API Listings endpoint — no copy-paste, no
    listing-page editing."*

### Page 4 — §2.8 pseudocode (end) + §2.9 output schema
- Pseudocode `run_phase2(account)`: `find_sales_drop(window_months=3)` + `find_zero_sales(window_months=6)`
  → `normalise_sku(resolve_mapped_sku(...))` → match to `top_base_sku` → `load_sqp_top_terms(top_asin)` →
  per term `scan_title_bullets_desc()` and `scan_backend_keywords()` → status/add_target → dashboard.
  Button handlers call `sp_api.update_backend_keywords()` / `sp_api.update_bullet_points()`.
- **§2.9 output contract, 12 columns:** `brand` (enum `dcvoltage_uk`/`ledsone_uk`, *"accounts never
  merged"*) · `top_asin` · `base_sku` · `duplicate_asin` · `duplicate_status` (enum `sales_drop_3mo` /
  `zero_sales_6mo`) · `keyword` · `in_frontend` (bool) · `in_backend` (bool) · `status` (enum
  `present`/`gap`) · `add_target` (enum `backend`/`bullet`/`backend_and_bullet`/`none`) · `action_state`
  (enum `reviewed`/`pending_add`/`added`) · `date_checked` (date).

### Page 5 — §2.10 QA & Automation checklist (7 points)
Account Separation (*"never merged"*) · SKU Normalisation Applied · One-Place-Is-Enough Rule · Dual-Method
Coverage · Directional Add Logic (*"never a blanket backend-only push"*) · Zero Manual Lookup (*"the only
human actions are clicking Mark Reviewed or Add Missing Keywords"*) · Monthly Cadence.

## Key facts extracted
- **Requester / PH:** 🔴 **none named.** The document is addressed to the "Automation Team" and attributes
  the zero-manual-lookup requirement to an *"MD instruction"*, but names no individual. **Open item #0.**
- **Platform:** Amazon. **Market:** **UK**. **Product scope:** LED bulb listings.
- **Accounts:** **DCVOLTAGE UK** and **LEDSone UK** — processed and reported **independently, never merged**.
- **Cadence:** monthly, per account.
- **Hard control:** the only human actions are *Mark Reviewed* and *Add Missing Keywords*.
- **Requester's stated end-state:** SP-API writes the listing automatically on click. *(Out of workbench
  scope — see `CLAUDE.md` §2 and open item #1.)*

## Not specified anywhere in the source
The Top-Moving cut-off · the quantitative "declined" test · the zero-sales metric (units vs revenue) · the
full SKU normalisation rule beyond pack suffixes · the identity of the "SKU mapping table" · keyword match
semantics (case, plurals, word order, contiguity) · the exact number of top terms (a 30–50 range is given) ·
Step 6 filter thresholds · which column `click_rate` means · what "title Zone A" is · the `ph_task` audience
· the schedule slot.

## Integrity
Copied byte-for-byte from `C:\Users\digit\Downloads\BGCT_Keyword_Workflow_Phase1_Phase2_v2.1.pdf`
(**153,412 bytes**, md5 **`637da6187137bde151010b0d8a983c85`** — source and copy verified identical). No
edits. Renamed to the workbench `YYYY-MM-DD_[stage]_[task-name].[ext]` convention. Text extracted for
analysis with `pypdf`; the PDF itself is the canonical artefact.
