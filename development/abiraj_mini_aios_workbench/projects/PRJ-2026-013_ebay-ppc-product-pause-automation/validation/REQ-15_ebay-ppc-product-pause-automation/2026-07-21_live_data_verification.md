# Live Data Verification — REQ-15-D01

**Executed:** 2026-07-21 · read-only against the live `ledsone` DB (Ledsone Postgres MCP)
**Method:** the rule engine was **re-implemented independently in SQL** and diffed against the
shipped artefacts. A report agreeing with itself proves nothing; this compares two separate
implementations of the same rules over the same live data.

## Verdict

**PASS on correctness — zero discrepancies across 45 campaigns.**
**One methodological defect found and FIXED the same day:** the window anchored on a *partial*
day (see §5). It changed no decision, but understated the money figures by ~3.5%. The anchor now
resolves to the latest **complete** day and every artefact has been rebuilt and re-verified.

---

## 1. Coverage

| | |
|---|---|
| Campaigns in the SQL recompute | 45 |
| Campaigns in the shipped report | 45 |
| In SQL but missing from the report | none |
| In the report but not in SQL | none |

## 2. Per-campaign diff — all 45 rows, 6 fields each

Fields compared: **verdict · 30D spend · advertised listings · out-of-stock · low stock · no-stock-data**

**0 field mismatches across 270 comparisons.** Every campaign carries an identical verdict and
identical figures in both implementations.

## 3. KPI reconciliation

| Metric | SQL recompute | Shipped report | |
|---|---|---|---|
| Campaigns in scope | 45 | 45 | ✅ |
| Recommend pause | 15 | 15 | ✅ |
| · Stock | 8 | 8 | ✅ |
| · Rule 1 | 7 | 7 | ✅ |
| · Rule 2 | 0 | 0 | ✅ |
| Still running | 16 | 16 | ✅ |
| Already off | 14 | 14 | ✅ |
| 30D spend at risk | £1,355.02 | £1,355.02 | ✅ |
| 30D spend total | £3,400.40 | £3,400.40 | ✅ |
| Advertised listings | 1,578 | 1,578 | ✅ |
| Out-of-stock listings | 16 | 16 | ✅ |
| No-stock-record listings | 229 | 229 | ✅ |

**Internal arithmetic:** paused+running+off = 45 = scope ✅ · stock+r1+r2 = 15 = paused ✅ ·
high+med+low = 15 = paused ✅ · Σ(row spend) = £3,400.40 = KPI ✅

**Rule logic re-derived** from each row's own stored figures — 0 mismatches, so every decision
follows from the numbers printed beside it.

## 4. Scope audit — nothing silently dropped

Every LEDSone eBay-UK campaign accounted for:

| Disposition | Campaigns |
|---|---|
| **IN THE REPORT** — ON_SITE, not deleted (RUNNING 23+8 · ENDED 7+2 · PAUSED 4+1) | **45** |
| Excluded: COST_PER_SALE (logs no per-click spend — documented on the report) | 73 |
| Excluded: OFF_SITE (1 ended campaign) | 1 |
| Excluded: `deleted = true` | 145 |

23+8+7+4+2+1 = **45** — balances exactly.

## 5. 🔴 DEFECT — the window anchors on a partial day

The anchor is `MAX(performance_data.date)` = **2026-07-21**, which is *today*, and the hourly sync
last wrote at **03:17**. That day is nearly empty:

| Date | Rows | Clicks | Spend |
|---|---|---|---|
| **2026-07-21 (anchor)** | 530 | **8** | **£1.39** |
| 2026-07-20 | 1,005 | 539 | £98.73 |
| 2026-07-19 | 998 | 558 | £103.97 |
| 2026-07-18 | 995 | 508 | £94.29 |

So the "30-day" window is really **29 full days + a 1%-populated stub**, and it has dropped a full
day off the start of the range to make room for it.

**Impact on decisions: none today.** Re-running the whole engine anchored on the last *complete*
day (2026-07-20) returns the identical split — **Stock 8 · Rule 1 7 · Running 16 · Already off 14**.
The 15 recommendations are the same campaigns either way.

**Impact on money: ~3.5% understated.**

| | Partial anchor (shipped) | Complete-day anchor |
|---|---|---|
| Spend at risk | £1,355.02 | £1,403.54 |
| Stock rule | £743.68 | £768.92 |
| Rule 1 | £611.34 | £634.62 |

**Why it must be fixed before unattended running:** the weekly job fires Monday 11:00, so its anchor
day will hold roughly half a day of data. Today the margins were wide enough that nothing moved, but
a campaign sitting near the 40% ACOS ceiling or the 20% rescue line could tip on a half-counted day —
and nobody would see it happen.

**FIXED 2026-07-21.** The anchor CTE is now:

```sql
SELECT CASE WHEN MAX(date) < CURRENT_DATE THEN MAX(date) ELSE MAX(date) - 1 END AS d
```

If `MAX(date)` is in the past it is a finished day, so use it; if it is today it is still filling,
so step back one. Both windows are now also closed at the top (`AND date <= a.d`). Applied to
`eppa_weekly_run.py` and `eppa_rule_engine_dryrun.sql`; the engine module is unaffected.

**Rebuilt on the corrected anchor (2026-07-20) and re-verified — decisions unchanged, money now
complete:**

| | Partial anchor (withdrawn) | **Complete-day anchor (shipped)** |
|---|---|---|
| Campaigns / paused | 45 / 15 | **45 / 15** |
| Stock · Rule 1 · Rule 2 | 8 · 7 · 0 | **8 · 7 · 0** |
| Running / already off | 16 / 14 | **16 / 14** |
| Spend at risk | £1,355.02 | **£1,403.54** |
| 30D spend total | £3,400.40 | **£3,532.41** |

All ten KPIs re-reconciled against the independent SQL recompute, and the HTML + xlsx re-verified
against the governed JSON: **0 mismatches**.

## 6. Artefact consistency

The HTML and the workbook must show what the governed `eppa_d01_data.json` holds:

- **Dashboard** — all 8 KPI cards, the spend-at-risk sub-label and the 45 data rows: **match**
- **Workbook** — all 9 Dashboard KPIs and 45 Pause Log rows: **match**
- **0 artefact mismatches**

## 7. Cross-database corroboration

The warehouse (`order_management_copy`) independently reports the same campaign census for
`ss_name='led_sone'` / UK: **23 running ON_SITE MANUAL · 8 running ON_SITE SMART · 73 running
COST_PER_SALE**. Two separate databases, same answer.

---

## What this does and does not prove

**Proven:** the shipped numbers are a faithful computation of the stated rules over the live data;
two independent implementations agree exactly; the artefacts agree with the governed dataset; no
campaign is silently missing.

**Not proven — still open, unchanged by this pass:**
1. That the **campaign-grain Stock rule** is the rule the business wants (decision C). It fires on
   "≥1 advertised listing at 0 units" — a construction, since the source sheet's single hand-typed
   stock figure cannot be reproduced. 8 of the 15 recommendations depend on it.
2. That excluding **CPS campaigns** is acceptable (73 running campaigns unserved).
3. **Rule 2 returning 0** is arithmetically correct, but worth a second opinion — at campaign grain
   a whole campaign taking zero orders across 14 days is rare, where a single listing doing so is
   common. Correct for this grain; a question about whether the grain is right.

Read-only throughout. No writes, no DDL, no publish.
