# PH ASIN Segmentation — Monthly Run Prompt (paste into Claude Code on the 1st)

> This is the FIXED prompt. It does not change month to month. The SQL auto-detects
> the newest data window, so there are no dates to edit. Run it as-is every cycle.

---

**TASK: Regenerate the PH ASIN Segmentation monthly report (UK Amazon FBM).**

Follow `PH ASIN Segmentation Protocol v1.0` and the locked decisions below. Do NOT
re-invent the methodology or trust the pre-baked `performance_segment` column — the
engine SQL re-derives segments per the protocol.

**Locked decisions (do not change):**
- Benchmark = average of the per-ASIN CVR (conversions ÷ clicks) of the top-30 sold
  ASINs per PH per category (top-10 if fewer than 30 sellers). Method A.
- Conversion signal: zero clicks → LOW; conversions > clicks → HIGH; else CVR vs benchmark.
- Undefined 3-signal combos map: HLL → HLH, LHL → HHL.
- Scope: `which_channel = 1`, `market_place = 'UK'`, **FBM only** (`order_transaction.fba_sales = false`). Account from `sub_source_name`
  (amazon Ledsone → LEDSone UK, amazon Dcvoltage → DCVoltage UK).

**Steps:**
1. Run the engine script `ph_segment_engine.sql` via the Postgres MCP. It auto-selects
   the latest two windows from `analytics.ph_segment_30days_window`, rebuilds
   `analytics.ph_segment_report` (one row per UK-Amazon ASIN: PH, account, category,
   metrics, benchmark, current segment, previous segment, movement, SKU, manual flag,
   and a `report_period` label). Confirm row count and the detected windows.
2. Pull the per-PH configurator (benchmarks) and per-PH summary (segment counts,
   LLL %, declines) from `analytics.ph_segment_report`.
3. Pull the ASIN cards: all non-LLL rows, plus LLL rows where movement IN ('DECLINED','NEW').
4. Build the interactive HTML report identical in structure to the established report
   (`PH_ASIN_Segmentation_Report_*.html`): dark header (title, month, data window,
   generated date); six colour-coded tabs HHH/HHL/HLH/LHH/LLL/LLH with count badges
   (§5.2 hex colours); left PH sidebar filter; per-PH configurator panel; ASIN cards
   (ASIN, account tag, SKU, category, metrics, benchmark, segment badge, movement arrow
   + previous segment); tick boxes; live progress bars; §8 escalation banner
   (PH > 30% LLL, PH > 5 declines); Export/Import progress buttons; white theme, Poppins.
5. Name the file `PH_ASIN_Segmentation_Report_<report_period>.html` and present it.
6. Report: detected windows, total ASINs, segment counts, and any PH breaching §8.

**Evidence to return:** detected current/previous window dates, total row count,
segment distribution, and the download link.
