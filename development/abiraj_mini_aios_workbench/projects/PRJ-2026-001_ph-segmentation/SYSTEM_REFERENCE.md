# PH ASIN Segmentation — Complete System Reference

> **What this file is:** a plain-language, complete description of what the PH ASIN Segmentation
> system does — the protocol, the six segments, the benchmark rules, the classification logic,
> the report, and the escalations. It is a **derived reference** synthesised from the canonical
> sources; it does not replace them. Sources:
> - Protocol (authoritative spec): `evidence/source_documents/REQ-05_ph-asin-segmentation/2026-06_ph-asin_segmentation_protocol_v1.0.docx`
> - Build/decisions: `handover/REQ-05_ph-asin-segmentation/2026-06-24__abiraj__ph-asin__REQ-05-D02.md` (and D01)
> - Engine (authoritative logic): `sql/REQ-05_ph-asin-segmentation/2026-06-25_ph_segment_engine.sql`
> - Deliverable: `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-06-24_ph-asin_segmentation_report_2026-07.html`
> Where the protocol document and the as-built engine differ, the **engine is authoritative** and the difference is flagged in §11.

---

## 1. What the system does (in one paragraph)

Every month, the system classifies **every UK-Amazon FBM ASIN owned by each Portfolio Holder (PH)**
into one of **six performance segments**, based on three live signals — **Impressions, Clicks,
Conversion Rate (CVR)** — each rated HIGH or LOW against a **benchmark specific to that PH's
product category**. Each segment carries a fixed **action plan**. The system tracks each ASIN's
**movement** between segments month-over-month, and delivers everything as an **interactive HTML
report** with per-PH tabs, action checklists and progress bars. It **flags** problems and assigns
actions; it never takes commercial action automatically.

- **Owner:** Bietrick (TL). **Scope:** UK Amazon **FBM** (Fulfilled by Merchant), all PHs under Bietrick.
- **Cadence:** Monthly, on the 1st. **Tool:** Claude + Postgres. **Source of truth (output):** `analytics.ph_segment_report`.
- **June 2026 build:** 7,855 ASINs across 24 PHs and 57 categories (2 accounts: LEDSone UK, DCVoltage UK).

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
2. For each category, take the **top 30 ASINs by units sold** in the last 30 days (from `order_transaction`).
   - If fewer than 30 sold, use the **top 10**.
   - If fewer than 10 sold → **flag "manual benchmark"** (do not invent a threshold).
3. The benchmark = the **average Impression, average Click, and average CVR** across those top-N ASINs.
4. An ASIN scores **HIGH** on a signal if it is **at or above** its category benchmark, else **LOW**.
5. Benchmarks are **recalculated fresh every month** — they are not fixed.

Each PH sees their own category thresholds in their tab of the report.

## 4. The six segments

| Code | Impression · Click · Conversion | Priority (protocol) | Name (as-built) | Colour |
|---|---|---|---|---|
| **HHH** | HIGH · HIGH · HIGH | Scale | Champions | Green `#1A8A4A` |
| **HHL** | HIGH · HIGH · LOW | Fix Now | Leaky Buckets | Amber `#B87800` |
| **HLH** | HIGH · LOW · HIGH | Quick Win | Wallflowers | Blue `#1A6E99` |
| **LHH** | LOW · HIGH · HIGH | Growth Play | Hidden Gems | Purple `#6B3FA0` |
| **LLH** | LOW · LOW · HIGH | Maintain Selectively | Niche Winners | Teal `#0D7377` |
| **LLL** | LOW · LOW · LOW | Kill / Review | Dead Horses | Red `#C0392B` |

**Undefined combos (as-built "Option B" mapping):** the two leftover combinations are routed to
the segment whose action plan fixes their real problem — **`HLL → HLH`** and **`LHL → HHL`**.
Result: every ASIN lands in exactly one of the six segments; none is left unclassified.

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

## 6. Movement tracking (month-over-month)

Each ASIN's current-month segment is compared to last month's:

| Movement | Symbol | Meaning | Action |
|---|---|---|---|
| Improved | ↑ green | Moved to a higher segment | Acknowledge; continue |
| Same | → grey | No change | Check the action plan is being executed |
| Declined | ↓ red | Moved to a lower segment | Escalate; investigate root cause |
| New | ★ blue | First appearance this month | Assign segment action plan |

"Higher/lower" is measured by an **h-count** (number of HIGH signals): HHH = 3; HHL/HLH/LHH = 2;
LLH = 1; LLL = 0. Current > previous = Improved; < = Declined; = Same; no previous = New. Movement
is always vs the immediately preceding 30-day window — no fixed baseline.

## 7. The as-built engine (authoritative logic)

The monthly engine (`ph_segment_engine.sql`) is **parameter-free** — it auto-detects the latest two
data windows and rebuilds the report table. Key locked rules:

- **Scope filters:** `which_channel = 1`, `market_place = 'UK'`, **FBM only** (`order_transaction.fba_sales = false`).
  *(FBM-only was a build correction: ~23% of in-scope units were FBA and were inflating the benchmark; removing them re-segmented 100+ ASINs.)*
- **Benchmark population:** top 30 sold (top 10 if <30; flag `needs_manual` if <10).
- **CVR method (Method A):** average of **per-ASIN** CVR across the top-N (each ASIN's conv/click first, zero-click = 0, then average) — plus mean impression and mean click.
- **Classification edges:** Impression HIGH if `imp ≥ bm_imp`; Click HIGH if `clk ≥ bm_clk`; Conversion: `clicks = 0 → LOW`; `conversions > clicks → HIGH`; else `cvr ≥ bm_cvr → HIGH` else LOW.
- **Undefined-combo map (Option B):** `HLL → HLH`, `LHL → HHL`.
- **Account:** from `sub_source_name` (`amazon Ledsone → LEDSone UK`, `amazon Dcvoltage → DCVoltage UK`). **SKU:** most-sold FBM SKU per ASIN.
- **Output:** `analytics.ph_segment_report` (one row per ASIN: PH, account, category, metrics, benchmark, current segment, previous segment, movement, SKU, manual flag, `report_period`).

**June 2026 distribution (FBM-only, Option B):**

| Segment | ASINs |
|---|---:|
| HHH Champions | 77 |
| HHL Leaky Buckets | 479 |
| HLH Wallflowers | 157 |
| LHH Hidden Gems | 17 |
| LLH Niche Winners | 349 |
| LLL Dead Horses | 6,776 |
| **Total** | **7,855** |

~86% land in LLL (expected — the bar is the top sellers' average). 1,118 ASINs sit in <10-seller categories (manual-benchmark flag).

## 8. The monthly HTML report (what it looks like)

A self-contained interactive HTML file (white theme, Poppins), built to a fixed spec:

- **Header bar:** title, month, data window, generated date.
- **Six segment tabs** (HHH/HHL/HLH/LHH/LLH/LLL) each with an ASIN **count badge**, colour-coded.
- **Left PH sidebar:** click a PH to filter to their ASINs; "All PHs" shows everyone.
- **Configurator panel per PH:** category benchmarks (category, #ASINs used, Impression/Click/CVR thresholds).
- **ASIN cards:** ASIN, account tag, SKU, category, live metrics, benchmark, segment badge, **movement arrow + previous segment**.
- **Tick box per ASIN** (mark actioned) and a **live progress bar per PH** (X of Y actioned).
- **Action-plan summary** at the top of each segment tab.
- **§8 escalation banner** (e.g. PHs >30% LLL, PHs with >5 declines).
- Persists ticks in browser `localStorage` with Export/Import.

## 9. Escalation rules

| Trigger | Escalate to | Deadline |
|---|---|---|
| ASIN in LLL for 2 consecutive months despite action | Bietrick + sub-leader review | Within 3 days of report |
| ASIN drops HHH → LLL in one month | Bietrick immediately | Same day |
| A PH has >30% of ASINs in LLL | Sathees (Operations) | Within 1 week — portfolio review |
| <10 sold ASINs in a category (no benchmark) | Sub-leader flags | Note in report — manual threshold |
| >5 ASINs declined for one PH in a month | Bietrick + sub-leader | Within 48 hours |
| PH fails to action flagged ASINs by the 7th, 2 months running | Arun (ROI Officer) | Accountability review in 48h |

## 10. Data sources & field reference

| Data point | Table | Field | Filter |
|---|---|---|---|
| Impressions | `traffic_data` | `impression` | `which_channel=1, market_place='UK'` |
| Clicks | `traffic_data` | `click` | same |
| CVR | `traffic_data` | `conversion / click × 100` | same; `NULLIF(click,0)` |
| ASIN | `traffic_data` | `ref_id` | (not called `asin` in this table) |
| PH ownership | `analytics.ph_segment` (build: `ph_segment_30days_window`) | `user_name` | latest `period_end` |
| Units sold | `order_transaction` | `quantity` | `source_name='AMAZON', market_place='UK', fba_sales=false` |
| Account | `order_transaction` | `ss_name` / `sub_source_name` | LEDSone UK / DCVoltage UK |
| SKU | `order_transaction` | `sku` | join via ASIN |
| PPC spend | `ppc_performance` | `spend` | `marketplace='UK'` — kill-criteria checks only |

## 11. Protocol-document vs as-built differences (honest reconciliation)

The engine is authoritative; these are the deliberate build decisions that differ from / refine the v1.0 document:

- **FBM-only filter** (`fba_sales=false`) — added in the build; not explicit in the doc. Corrected a ~23% FBA contamination of the benchmark.
- **Undefined combos** — the doc lists only six codes; the build added the explicit **Option B** map (`HLL→HLH`, `LHL→HHL`). *(Note: this differs from a different live-DB taxonomy that used `LHL→LLH`; Option B is canonical for this report.)*
- **CVR = Method A** (per-ASIN average), making the high-CVR bar intentional.
- **Segment names** — the doc uses priorities (Scale/Fix Now/…); the build also applies friendly names (Champions/Leaky Buckets/…). Same six codes.
- **PH count** — the doc mock shows 28 PHs; the build found **24** PHs actually own UK-Amazon FBM ASINs this window (not a data error).
- **Single-cycle table** — the output table is overwritten each run (history lives in the source window table); accepted by design.

## 12. What this protocol does NOT do

- It does **not** replace the weekly leakage protocol.
- It does **not** auto-pause PPC or change listings (actions are manual).
- It does **not** provide exact profit/margin/COGS/fees/VAT.
- It does **not** detect within-a-single-week issues (that's the leakage report).
- It does **not** replace BLOS threshold governance.

## 13. Status & provenance

This system was built by Abiraj under requirement **REQ-05** and is preserved in this project
(`PRJ-2026-001_ph-segmentation`, task `REQ-05_ph-asin-segmentation`), validated (Technical,
Queryability, Business, Coordinator — all PASS) and ACTIVE. The SQL engine is **stored, not
executed** in the workbench; any live monthly run requires a new task, technical approval and
database write authorisation.
