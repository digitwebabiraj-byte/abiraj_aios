# PH ASIN Segmentation — Complete System Reference

> **What this file is:** a plain-language, complete description of what the PH ASIN Segmentation
> system does — the protocol, the six segments, the benchmark rules, the classification logic,
> the movement rule, the Orphan-ASIN monitor, the two per-PH counts, the report, and the escalations.
> It is a **derived reference** synthesised from the canonical sources; it does not replace them.
>
> **Currency:** updated **2026-07-06** to reflect the work through **REQ-05-D08** (increments D05–D08).
> Where an older statement was superseded, the current rule is given and the change is flagged in §11.
>
> **Canonical sources:**
> - Protocol (authoritative spec): `evidence/source_documents/REQ-05_ph-asin-segmentation/2026-06_ph-asin_segmentation_protocol_v1.0.docx`
> - Protocol clarifications: `validation/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_protocol_v1_clarifications.md`
> - Daily build/decisions: `handover/REQ-05_ph-asin-segmentation/2026-07-0{1,2,3}__abiraj__ph-asin__REQ-05-D0{6,7,8}.md` (and D01/D02, and the 30 Jun delivery record)
> - Engines: `sql/REQ-05_ph-asin-segmentation/2026-07-02_ph_segment_engine_strict_rank.sql` (current, strict-rank) · `2026-07-01_ph_segment_engine_v2.sql` (returning-aware) · `2026-06-25_ph_segment_engine.sql` (v1, historical)
> - Live dashboards (id-5 builds): `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-01_ph_asin_dashboard_id5_navy_live_2026-07.html` (1 Jul navy) · `..._catfilter_preview.html` (3 Jul clarity build, md5 `1f657a1b`)
>
> Where the protocol document and the as-built engine differ, the **engine is authoritative** and the difference is flagged in §11.

---

## 1. What the system does (in one paragraph)

Every month, the system classifies **every UK-Amazon FBM ASIN owned by each Portfolio Holder (PH)**
into one of **six performance segments**, based on three live signals — **Impressions, Clicks,
Conversion Rate (CVR)** — each rated HIGH or LOW against a **benchmark specific to that PH's
product category**. Each segment carries a fixed **action plan**. The system tracks each ASIN's
**movement** between segments versus the previous window, surfaces ASINs that sell with **no PH
owner** ("Orphan ASINs"), and delivers everything as an **interactive HTML dashboard** with a
per-PH view, action checklists and progress bars. It **flags** problems and assigns actions; it
never takes commercial action automatically.

- **Owner:** Bietrick (TL). **Scope:** UK Amazon **FBM** (Fulfilled by Merchant), all PHs under Bietrick.
- **Cadence:** Monthly. **Comparison window:** the **last 4 complete weeks** vs the **previous 4 complete weeks** (Saturday-ending weeks) — *not* a calendar month (see §6). **Tool:** Claude + Postgres (MCP). **Source of truth (output):** `analytics.ph_segment_report`.
- **Current build (report_period 2026-07, window 31 May–27 Jun 2026):** **8,149 ASINs** across **24 PHs** and 57 categories (2 accounts: LEDSone UK, DCVoltage UK).

## 2. The three signals

| Signal | Source field | Meaning |
|---|---|---|
| **Impressions** | `traffic_data.impression` | How often the ASIN was shown in search/browse |
| **Clicks** | `traffic_data.click` | How many shoppers clicked through to the product page |
| **Conversion (CVR)** | `conversion / click × 100` | % of clicks that resulted in a sale |

Each signal is marked **HIGH** or **LOW** versus the PH's category benchmark → three letters → one segment code (e.g. `HHL`).

## 3. The benchmark ("Configurator") — per PH, per category

A benchmark is **not** a global average — a Pendant Holder and a Cable Tie cannot share an
impression bar. So it is computed **per PH, per category**:

1. Find every category the PH owns.
2. For each category, take the **top 30 ASINs by units sold** in the window (from `order_transaction`).
   - If fewer than 30 sold, use the **top 10**.
   - If fewer than 10 sold → **flag "manual benchmark"** (do not invent a threshold).
3. The benchmark = the **average Impression, average Click, and average CVR** across those top-N ASINs.
4. An ASIN scores **HIGH** on a signal if it is **at or above** its category benchmark, else **LOW**.
5. Benchmarks are **recalculated fresh every cycle** — they are not fixed.

Each PH sees their own category thresholds in their view of the report.

## 4. The six segments

| Code | Impression · Click · Conversion | Rank (strict) | Priority (protocol) | Name (as-built) | Colour |
|---|---|:--:|---|---|---|
| **HHH** | HIGH · HIGH · HIGH | 1 (best) | Scale | Champions | Green `#1A8A4A` |
| **HHL** | HIGH · HIGH · LOW | 2 | Fix Now | Leaky Buckets | Amber `#B87800` |
| **HLH** | HIGH · LOW · HIGH | 3 | Quick Win | Wallflowers | Blue `#1A6E99` |
| **LHH** | LOW · HIGH · HIGH | 4 | Growth Play | Hidden Gems | Purple `#6B3FA0` |
| **LLH** | LOW · LOW · HIGH | 5 | Maintain Selectively | Niche Winners | Teal `#0D7377` |
| **LLL** | LOW · LOW · LOW | 6 (worst) | Kill / Review | Dead Horses | Red `#C0392B` |

**Undefined combos (as-built "Option B" mapping):** the two leftover combinations are routed to
the segment whose action plan fixes their real problem — **`HLL → HLH`** and **`LHL → HHL`**.
Result: every ASIN lands in exactly one of the six segments; none is left unclassified.

The **Rank** column is the strict 1–6 order used by the movement rule (§6).

## 5. The six segment action plans (what each means + what to do)

**HHH — Champions (Scale).** Strong on all three: visible, clicked, converting.
→ Expand keywords, add rich media, scale ad spend (proven ROI), push B2B/global, Subscribe & Save/bundles, monthly pricing review.
**Kill criterion:** margin < 15% for 30 days → mandatory pricing review.

**HHL — Leaky Buckets (Fix Now).** Lots of traffic, customers drop off at the page.
→ Revamp detail page/A+ content, upgrade images, A/B test, competitive pricing, build reviews (Vine), answer negative reviews in 48h, cut PPC until conversion is fixed.
**Kill criterion:** CVR not +20% within 60 days → cut PPC 50% and escalate to Bietrick.

**HLH — Wallflowers (Quick Win).** Seen but not clicked; those who click convert.
→ Replace main image, rewrite title (lead keyword + benefit), A/B test, get reviews, add negative keywords to remove irrelevant impressions, visible coupons/pricing.
**Kill criterion:** CTR < 1% after 2 image/title fixes → treat as an LHH (impression-volume) problem.

**LHH — Hidden Gems (Growth Play).** Great listing, just not visible enough.
→ Expand keywords/backend terms, raise Sponsored Products budget, verify category/browse node, add Sponsored Brand/Display, external traffic, voice-search phrasing.
**Kill criterion:** impressions not +50% within 60 days despite spend → pause scaling, investigate targeting.

**LLH — Niche Winners (Maintain Selectively).** Low reach but excellent conversion — a niche product with strong fit.
→ Broaden keywords carefully, selective PPC, product-targeting ads on competitor pages, niche external marketing; **don't scale aggressively** until ACoS < 40%.
**Kill criterion:** PPC ACoS > 40% for 30 days → stop scaling, leave as organic niche.

**LLL — Dead Horses (Kill / Review).** Weak on all three signals.
→ Full listing audit, rebuild keywords from scratch, professional photography, competitor reverse-engineering, pricing review, PPC only after fixes; if no improvement after full relist → discontinuation review.
**Kill criterion:** units < 20/month after a full overhaul + 30 days PPC → delist/liquidation review.

## 6. Movement tracking (vs the previous window)

Each ASIN's current segment is compared to its segment in the **previous 4-week window**:

| Movement | Symbol | Meaning | Action |
|---|---|---|---|
| Improved | ↑ green | Moved **up** the rank ladder | Acknowledge; continue |
| Same | → grey | No change | Check the action plan is being executed |
| Declined | ↓ red | Moved **down** the rank ladder | Escalate; investigate root cause |
| New | ★ blue | Not in the previous window | Assign segment action plan |

**The rule (strict segment rank — current since D07, 2026-07-02).** Every segment has a distinct
rank: `HHH=1, HHL=2, HLH=3, LHH=4, LLH=5, LLL=6` (lower = better). Movement = the ASIN's **current
rank vs its previous rank**: current `<` previous → **Improved**; `>` → **Declined**; `=` → **Same**;
no previous → **New**.

- This **replaced** the earlier equal-weight *h-count* (which counted HIGH signals: HHH=3, HHL/HLH/LHH=2,
  LLH=1, LLL=0, so HHL/HLH/LHH were tied and lateral moves between them wrongly read as "Same").
  The strict rank makes them distinct, so those real up/down moves are now surfaced (this corrected 65 rows).
- **Two consequences at the ends of the ladder:** the top segment **HHH can never be "Declined"**
  (nothing above it to fall from) and the bottom **LLL can never be "Improved"** (nothing below to climb
  from). LLL *can* be Declined (a product fell into it) and HHH *can* be Improved (a product climbed into it).
- **"New" is about history, not traffic.** New means the ASIN was **not in the previous window** — so there
  is no earlier segment to compare. A New ASIN can still have thousands of impressions.
- **Returning-aware NEW (engine rule).** An ASIN absent from the narrow 4-week previous window but present
  in the 4 weeks before that (an 8-week lookback) is treated as **returning, not New**. *(Status: the live
  report currently uses the simple rule — 191 NEW; the engine's returning-aware rule gives 121. Which is
  official is a pending Bietrick sign-off — see §11.)*
- **Governance note:** the strict-rank change was **user-directed (2026-07-02), not yet a Bietrick protocol
  sign-off**; it is live in the report, dashboard and engine.

## 7. The as-built engine (authoritative logic)

The monthly engine is **parameter-free** — it auto-detects the latest two 4-week windows and rebuilds
the report table. The current engine (`2026-07-02_ph_segment_engine_strict_rank.sql`) is self-contained
on weekly `traffic_data`. Key locked rules:

- **Window:** current = last 4 complete weeks; previous = the 4 weeks before that (Saturday-ending). For 2026-07: current **31 May–27 Jun**, previous **3 May–30 May**. *(Approved live as "Option A" — previous-window recompute only, current segments untouched — by Bietrick, D06.)*
- **Scope filters:** `which_channel = 1`, `market_place = 'UK'`, **FBM only** (`order_transaction.fba_sales = false`).
  *(FBM-only was a build correction: ~23% of in-scope units were FBA and were inflating the benchmark; removing them re-segmented 100+ ASINs.)*
- **Benchmark population:** top 30 sold (top 10 if <30; flag `needs_manual` if <10).
- **CVR method (Method A):** average of **per-ASIN** CVR across the top-N (each ASIN's conv/click first, zero-click = 0, then average) — plus mean impression and mean click.
- **Classification edges:** Impression HIGH if `imp ≥ bm_imp`; Click HIGH if `clk ≥ bm_clk`; Conversion: `clicks = 0 → LOW`; `conversions > clicks → HIGH`; else `cvr ≥ bm_cvr → HIGH` else LOW. *(A **lateral change** in the same rank is SAME; these edges are formalised in the Protocol v1.0 Clarifications.)*
- **Movement:** strict segment rank (§6); returning-aware NEW.
- **Undefined-combo map (Option B):** `HLL → HLH`, `LHL → HHL`.
- **Account:** from `sub_source_name` (`amazon Ledsone → LEDSone UK`, `amazon Dcvoltage → DCVoltage UK`). **SKU:** most-sold FBM SKU per ASIN.
- **Output:** `analytics.ph_segment_report` (one row per ASIN: PH, account, category, metrics, benchmark, current segment, previous segment, movement, SKU, manual flag, `report_period`).

**Current distribution (report_period 2026-07, window 31 May–27 Jun, Option-A movement):**

| Segment | ASINs |
|---|---:|
| HHH Champions | 51 |
| HHL Leaky Buckets | 426 |
| HLH Wallflowers | 139 |
| LHH Hidden Gems | 5 |
| LLH Niche Winners | 440 |
| LLL Dead Horses | 7,088 |
| **Total** | **8,149** |

~87% land in LLL (expected — the bar is the top sellers' average). Movement this cycle: declines 574,
escalation flags 24 PHs >30% LLL / 22 PHs with >5 declines. Source reconciliation vs `traffic_data`:
8,146 of 8,149 rows match exactly (3 differ by ±1 conversion — benign late-attribution restatement).

*(Prior build for reference: the June partial-month build was 7,855; the complete-June refresh (30 Jun)
moved it to 8,149. The 7,855 figure is historical.)*

## 7A. Orphan ASINs (unowned selling products) — added D06

An **Orphan ASIN** is a product with **traffic/sales but no PH owner** — `user_name` is NULL (or the row
is absent) across **all four** ownership sources checked: `traffic_data`, `order_transaction`,
`development.vw_surfaceable_data`, `public.amz_fbm_performance_data`. It is a genuine ownership gap, not a
pipeline bug, so ownership must be **assigned by a person** — the engine **never auto-assigns**.

- **Monitor:** `analytics.v_orphan_asins` — a permanent, evergreen view (recomputes the latest 4 complete weeks, no parameters). Flag-only.
- **Live flag:** the dashboard's escalation banner shows a line like *"⚠ 492 Orphan ASIN(s) selling with no PH owner"*.
- **Current (2026-07):** ~15,914 orphan ASINs total, **492 actively converting**; assignment hand-off `2026-07-01_unowned_asins_for_assignment_2026-07.csv` (492 rows) — held for Bietrick assignment/sign-off.

## 7B. The two per-PH "listing count" numbers — clarified D08

Two different, both-correct counts exist for the same PH and must not be confused:

| Count | What it answers | Source | Example (paulr) |
|---|---|---|---|
| **Assigned / Active** (dashboard) | "how many owned listings are in scope **this window**" | `analytics.ph_segment_report` (current 4-week, owned, UK-Amazon-FBM) | 466 listings / 464 distinct ASINs |
| **Allocated / roster** | "how many IDs is this PH allocated **in total**" | `user → ph_categories → ph_cate_products`, `which_channel=1`, distinct `ref_id` | 503 |

The gap (503 − 464 = 39 for paulr) = allocated ASINs **not active** in this window (4 never had UK traffic).
The dashboard's **Assigned Listings** count is verified against `traffic_data` with **diff 0 for all 24 PHs**.

## 8. The dashboard / HTML report (what it looks like)

A self-contained interactive HTML file baked into `tech_team_outputs.ph_task` **id 5** (the dashboard
reads the baked HTML, **not** the DB live — any data change requires a re-push). Current UI (restyled D07,
clarity pass D08):

- **Header:** gold gradient header + greeting bar over a slate/teal body; title, report period, generated date.
- **Per-PH dropdown** (replaced the old six-tab / sidebar layout): pick a PH to see only their ASINs in one flat table.
- **Meta strip:** the exact **window date ranges** (current 31 May–27 Jun vs previous 3 May–30 May), benchmark basis, report period.
- **Summary cards:** Assigned listings, distinct ASINs, distinct SKUs, categories, **Champions (green)**, **Dead Horses (red)** with icons, and an **Allocated** card (roster count, with "not active" note).
- **Segment-mix & Movement chips:** click to filter the ASIN table; segment × movement combine as an **intersection (AND)**; chip counts are full-portfolio totals (the live count is the hint line above the table).
- **Category benchmark table:** click a category to filter the ASIN table to it.
- **ASIN table (19 cols):** Rank, Category, Segment badge, Movement, ASIN, SKU, Account, metrics, benchmark, Δ columns, and a **Status** (ABOVE/NEAR/BELOW vs the category top-N average) shown **alongside** Movement — not replacing it.
- **Escalation banner:** §9 triggers + the Orphan-ASIN flag.
- **NEEDS REVIEW** rows (conversions>clicks, CVR>100%, or conversions with zero clicks) tinted amber as a data-quality flag.

**Per-PH standalone files:** 24 single-PH **locked** HTML files (one per PH) are generated each cycle —
each contains **only that PH's data** (others physically removed), dropdown hidden, filenames using the
authoritative spellings (e.g. `Tharsiga(nelli).html`). A 2026-07 snapshot; regenerated each cycle.

*Logic note:* the restyle, cards and per-PH files are **presentation only** — the six-segment / movement /
Method-A-CVR classification is unchanged. A reference board from another team using a **weighted CVR** and an
ABOVE/NEAR/BELOW status was **not** adopted as the classification (its status label was added alongside only).

## 9. Escalation rules

| Trigger | Escalate to | Deadline |
|---|---|---|
| ASIN in LLL for 2 consecutive months despite action | Bietrick + sub-leader review | Within 3 days of report |
| ASIN drops HHH → LLL in one month | Bietrick immediately | Same day |
| A PH has >30% of ASINs in LLL | Sathees (Operations) | Within 1 week — portfolio review |
| <10 sold ASINs in a category (no benchmark) | Sub-leader flags | Note in report — manual threshold |
| >5 ASINs declined for one PH in a month | Bietrick + sub-leader | Within 48 hours |
| PH fails to action flagged ASINs by the 7th, 2 months running | Arun (ROI Officer) | Accountability review in 48h |
| Orphan ASINs selling with no PH owner | Bietrick (assignment) | Assign owners so they enter segmentation |

The dashboard's live banner surfaces the >30% LLL and >5-declined counts and the Orphan-ASIN count.

## 10. Data sources & field reference

| Data point | Table | Field | Filter |
|---|---|---|---|
| Impressions | `traffic_data` | `impression` | `which_channel=1, market_place='UK'` |
| Clicks | `traffic_data` | `click` | same |
| CVR | `traffic_data` | `conversion / click × 100` | same; `NULLIF(click,0)` |
| ASIN | `traffic_data` | `ref_id` | (not called `asin` in this table) |
| PH ownership | `traffic_data.user_name` (current engine reads it directly) | `user_name` | latest 4 complete weeks; NOT NULL = owned |
| Units sold | `order_transaction` | `quantity` | `source_name='AMAZON', market_place='UK', fba_sales=false` |
| Account | `order_transaction` | `ss_name` / `sub_source_name` | LEDSone UK / DCVoltage UK |
| SKU | `order_transaction` | `sku` | join via ASIN |
| Allocated roster | `ph_categories` → `ph_cate_products` | `ref_id` (distinct) | `which_channel=1` (per-PH "Allocated" count) |
| Orphan monitor | `analytics.v_orphan_asins` | (view) | `user_name` NULL across the 4 ownership sources |
| PPC spend | `ppc_performance` | `spend` | `marketplace='UK'` — kill-criteria checks only |
| Segmentation output | `analytics.ph_segment_report` | (all) | current `report_period` (single-cycle) |

Ownership sources checked for Orphan ASINs: `traffic_data`, `order_transaction`, `development.vw_surfaceable_data`, `public.amz_fbm_performance_data`.

## 11. Protocol-document vs as-built differences (honest reconciliation)

The engine is authoritative; these are the deliberate build decisions that differ from / refine the v1.0 document:

- **FBM-only filter** (`fba_sales=false`) — added in the build; corrected a ~23% FBA contamination of the benchmark.
- **Undefined combos** — the doc lists only six codes; the build added the explicit **Option B** map (`HLL→HLH`, `LHL→HHL`). *(Differs from a different live-DB taxonomy that used `LHL→LLH`; Option B is canonical for this report.)*
- **CVR = Method A** (per-ASIN average), making the high-CVR bar intentional.
- **Window = last 4 complete weeks** (not a calendar month) — the "last 30 days" is implemented as 4 Saturday-ending weeks; applied symmetrically to current and previous windows (**Option A** approved live by Bietrick, D06).
- **Movement = strict segment rank** (HHH=1…LLL=6) — replaced the equal-weight h-count (D07). **User-directed, not yet a Bietrick protocol sign-off.**
- **Returning-aware NEW** — 8-week lookback in the engine (D06). **Open sign-off:** live report uses the simple rule (NEW=191) vs the engine's returning-aware rule (NEW=121); which is official awaits Bietrick.
- **Orphan ASIN** — formal definition + `v_orphan_asins` monitor + live flag + assignment list (D06); flag-only, never auto-assigned.
- **Two per-PH counts** — Assigned/Active (dashboard) vs Allocated/roster clarified (D08); both correct, different questions.
- **Edge-case clarifications** — lateral-change = SAME, zero-click → LOW conversion, conversions>clicks → HIGH, HLL→HLH / LHL→HHL — written up in `PH_ASIN_Protocol_v1.0_Clarifications.md` (awaiting Bietrick sign-off).
- **UI redesign** — dropdown + one-view table + restyle + cards (D07) and clarity pass (D08) — presentation only; classification unchanged.
- **Segment names** — the doc uses priorities (Scale/Fix Now/…); the build also applies friendly names (Champions/Leaky Buckets/…). Same six codes.
- **PH count** — the doc mock shows 28 PHs; the build found **24** PHs actually own UK-Amazon FBM ASINs this window (not a data error).
- **Single-cycle table** — the output table is overwritten each run (history lives in the source data); accepted by design.

## 12. What this protocol does NOT do

- It does **not** replace the weekly leakage protocol.
- It does **not** auto-pause PPC or change listings (actions are manual).
- It does **not** auto-assign Orphan-ASIN owners (human decision only).
- It does **not** provide exact profit/margin/COGS/fees/VAT.
- It does **not** detect within-a-single-week issues (that's the leakage report).
- It does **not** replace BLOS threshold governance.

## 13. Status & provenance

Built by Abiraj under requirement **REQ-05**, preserved in `PRJ-2026-001_ph-segmentation`
(task `REQ-05_ph-asin-segmentation`), validated (Technical, Queryability, Business, Coordinator — all
PASS) and **ACTIVE**.

**Delivery increments recorded (all imported PASS/GREEN as of 2026-07-06):** D06 (1 Jul) Option-A movement
fix + Orphan-ASIN + engine v2 + protocol clarifications + dropdown UI · D07 (2 Jul) restyle + card redesign
+ strict-rank movement + strict-rank engine · D08 (3 Jul) Assigned-Listings confirmation + clarity pass
(**pushed LIVE 3 Jul 14:19, md5 `1f657a1b`**) + 24 per-PH locked views · D09 (6 Jul) backup housekeeping —
9 `ph_task_id5_backup_*` archived + dropped (≈1.8 MB), live id-5 md5 unchanged, 3 report backups kept.
Live output: `tech_team_outputs.ph_task` id 5 (current build = the 3 Jul clarity/catfilter, md5 `1f657a1b`).

**Open items (delivery, not this document):**
- Monthly routine (`PH_ASIN_Monthly_Routine.txt`) still builds the **old** UI shell — must be swapped to the
  new dropdown UI before the next auto-run (3 Aug) or that run would revert the live dashboard.
- `analytics.v_orphan_asins` view not backed up as a file — export `v_orphan_asins.sql`.
- Bietrick sign-offs pending: the **NEW definition** (live 191 vs engine 121), the **edge-case protocol**,
  and the **492 Orphan-ASIN assignments**; the 3 report backups stay until acceptance.
- The strict-rank movement rule is live but **not yet formally ratified** as protocol.

The workbench holds the engines **stored, not executed**; any live monthly run requires a new task,
technical approval and database write authorisation. (The live pushes to date were performed by Abiraj in
a separate Claude Chat session against the live DB; this workbench documents them read-only.)
