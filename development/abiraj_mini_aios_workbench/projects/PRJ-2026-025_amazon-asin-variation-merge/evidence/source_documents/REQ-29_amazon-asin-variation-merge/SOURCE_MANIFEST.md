# SOURCE MANIFEST — REQ-29 Amazon ASIN Rating Analysis & Variation Merging

Imported 2026-08-18. This is the **original requester input**, verbatim. It is a **specification**
(desired columns, KPI tiles, merge-reason vocabulary, approval control model) — **not data**. The workbook
states this itself. Never copy a sample value into a deliverable.

| File (in this folder) | Original name | Type | What it defines |
|---|---|---|---|
| `2026-08-18_source_asin-variation-merge-spec.xlsx` | `996_ASIN_Variation_Merge_Dashboard.xlsx` | Excel, 3 sheets | Dashboard layout (4 KPI tiles, merge-status overview, business/technical summary, ROI list) · the 12-column "ASIN Merge Task" table with 5 **sample** rows · a Field Reference defining each of the 10 data fields. |

## Sheet-by-sheet

### 1. `Dashboard`
Title **"ASIN RATING ANALYSIS & VARIATION MERGING"**, subtitle *"Amazon UK Automation Dashboard | Example
data — replace with actual automation output"*.
- **KPI tiles (4):** Total ASINs · No-Review / Low-Rated · Approved · Rejected / Review. Sample values 5 / 5 / 3 / 2.
- **Merge Status Overview:** Approved 3 · Rejected / Review 2 · Duplicate Warnings 1 · Out of Stock 1.
- **Business / Technical Summary** — the control model, quoted verbatim:
  - *Automation Objective:* "Identify low/no-rating ASINs and recommend stronger variation parents."
  - *Approval Control:* **"No merge executes without PH/operator approval."**
  - *Key Validation:* "Duplicate variation attributes must be checked before merging."
  - *Execution:* "Approved merges use the required Amazon Seller Central flat-file process."
  - *Open Dependency:* "PH team input is required for template, sample file and variation fields."
- **Expected Business Value / ROI (5 statements):** reduce manual analysis time · consolidate customer
  reviews across eligible variations · improve listing credibility via shared review history · reduce manual
  errors through systematic parent selection and duplicate checks · create measurable automation outputs and
  execution logs.

### 2. `ASIN Merge Task`
The working table — **12 columns**:
`PLATFORM · ACCOUNT · BASE SKU · PARENT ASIN · PARENT RATING / REVIEWS · CHILD ASIN / SKU ·
CHILD COLOUR / RATING · MERGE REASON · STOCK STATUS · DUPLICATE WARNING · APPROVED (Y/N) · OPERATOR NOTES`

5 sample rows across 2 sample families (`CRSF120` → `B0PARENT01` 4.6/128; `CRSF150` → `B0PARENT02` 4.4/96),
demonstrating each outcome the report must be able to express:

| Sample outcome | Demonstrated by |
|---|---|
| Approved — no reviews | `B0CHILD01` Black / 0.0, In Stock, no duplicate → **Y** |
| Approved — low rating | `B0CHILD02` White / 2.9 → **Y** |
| Rejected — out of stock | `B0CHILD03` Yellow Brass / 0.0, **Out of Stock** → **N** |
| Rejected — duplicate colour | `B0CHILD04` Black / 1.8, **Duplicate Warning = Yes** → **N** |
| Approved — unique variation | `B0CHILD05` Chrome / 0.0 → **Y** |

Merge-reason vocabulary used: *"No reviews — merge into stronger parent"* and *"Low rating — merge into
higher-rated parent"*. **Note the workbook gives no numeric threshold for "low rating"** — 2.9 and 1.8 both
qualify in the samples, 4.4 and 4.6 are treated as strong parents, but no cut-off is stated.

Row 8 carries the requester's own disclaimer: *"EXAMPLE DATA ONLY — ASINs, ratings and SKUs above are
illustrative and should be replaced with actual automation output."*

### 3. `Field Reference`
The requester's one-line definition of each field — the authority on intent:

| Field | Purpose (verbatim) |
|---|---|
| Base SKU | Product family identifier. |
| Parent ASIN | Selected parent variation ASIN. |
| Parent Rating / Reviews | Parent star rating and review count. |
| Child ASIN / SKU | ASIN to merge as child and its SKU. |
| Child Colour / Rating | Child variation colour and current rating. |
| Merge Reason | Reason for merging, such as no reviews or low rating. |
| Stock Status | In Stock / Out of Stock. |
| Duplicate Warning | Yes/No — whether the colour/variation is duplicated. |
| Approved (Y/N) | Operator approval decision. |
| Operator Notes | Space for operator comments. |

## Key facts extracted
- **Requester / PH:** **Prasath** (`staff.users` id 163, Jaffna, Active), confirmed 2026-08-18; task
  assigned by **HR**. The workbook itself names no one — its Account column says only "PH / Product Team".
- **Platform:** Amazon. **Market:** Amazon **UK** (from the Dashboard subtitle). **Account:** not named.
- **Objective:** find no-review / low-rated ASINs, recommend a stronger variation parent, verify the merge is
  safe, and route it for human approval.
- **Hard control:** no merge executes without PH/operator approval; execution is via the Seller Central
  flat-file process, outside this workbench.
- **Requester's own open dependency:** flat-file template, sample file and variation field list.
- **Not specified anywhere in the source:** the low-rating threshold, the stronger-parent selection rule, the
  duplicate-matching rule, the out-of-stock policy, the account, and the approval mechanism.

## Integrity
Copied byte-for-byte from `C:\Users\digit\Downloads\996_ASIN_Variation_Merge_Dashboard.xlsx` (12,887 bytes).
No edits. Renamed to the workbench `YYYY-MM-DD_[stage]_[task-name].[ext]` convention. The `996` in the
original filename is **not** a requirement number and was not carried into any ID.
