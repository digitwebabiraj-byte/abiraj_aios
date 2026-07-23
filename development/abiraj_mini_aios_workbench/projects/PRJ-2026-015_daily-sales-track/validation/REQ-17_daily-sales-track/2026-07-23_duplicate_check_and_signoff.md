# Duplicate check & sign-off — REQ-17-D01 / D02

**Run:** 2026-07-23 · read-only against live `tech_team_outputs.ph_task` and the workbench portfolio

## Verdict: 🟢 GREEN — no duplicate of Daily Sales Track exists

### Our own rows are clean

| Check | Result |
|---|---|
| Rows with `project_code = 'dst'` | **exactly 4** |
| Distinct `task_id` | 4 |
| Distinct `assigned_user` | 4 |
| Distinct HTML versions | **1** — all four hold the identical file |
| Rows missing `assigned_user_team` | **0** |

`task_id` carries no date by design (decision I), so the daily run updates these four rows in place
rather than accumulating.

### Adjacent reports — checked one by one, none is a duplicate

| Code | What it is | Why it is not this report |
|---|---|---|
| **UDESC** — eBay SALES CHECK (UK & DE) | The closest candidate | **Weekly** (Wed 11:00), grain is **per Item ID** from one person's assigned-items workbook, audience **`ph_priors`** (Thuwaraga). Ours is **daily**, **account × marketplace**, whole channel, **`ebay_priors`**. Different question, different reader. |
| **espd** — eBay SKU Performance Dashboard | SKU-level revenue/orders/units | **Monthly** (Jun 2026), SKU grain. Complementary, not overlapping. |
| **ebpd** — eBay Account Performance | Account × marketplace KPIs | **Monthly.** This report *inherits* its definitions rather than competing with them. |
| **ebsr** — eBay Stock Reconciliation | Daily, `ebay_priors`, Thinesh | **Stock**, not sales. Same cadence and audience, different subject. |
| **EBAYAHD** — "EBay Account Health Daily" | Name suggests overlap | ⚠ **Mislabelled** — its own description is *"Daily FBA Restock Updates … FBA inventory levels and restock needs"*, i.e. **Amazon FBA inventory**. One row, v1, untouched since 14 Jul. |
| **UAWSO** | Daily/weekly/MTD sales & orders | **Amazon UK**, audience `ph_priors`. Different channel. |

**Conclusion:** nothing else reports daily eBay sales at account × marketplace to `ebay_priors`.
The Existing-Asset-First rule is satisfied: this extends REQ-13 (whose definitions it inherits) and
duplicates nothing.

---

## 🔴 Findings NOT about this project — worth raising

### 1. `ph_task` is accumulating duplicate rows (30 affected)

There is **no UNIQUE constraint on `task_id`** in live, despite the sample DDL claiming one. The
consequence is visible:

| `task_id` | Copies | ids |
|---|---|---|
| `Overall Asin Datas for utharsika` | **11** | 155, 213, 255, 260, 303, 337, 339, 341, 400, 408, 416 |
| `PH-SALES-TRACKER` | **7** | 265, 304, 338, 346, 401, 409, 417 |
| **`NULL`** | **7** | 116, 119, 121, 141, 399, 415, 419 (`ANPIA`, `ebsr`) |
| `T4 · Weekly Returns Check — Amazon UK & eBay UK` | 3 | 136, 248, 402 |
| `T6 · PH Performance Tracker` | 2 | 243, 249 |

The seven `NULL` rows are the worst case: **a row with no `task_id` can never be found, updated in
place, or de-duplicated** — every publish must insert a new one, forever.

**Recommendation:** either add the UNIQUE constraint the sample DDL already claims exists, or have
each project adopt a stable `task_id` and SELECT-then-UPDATE (as this project does). Route to
Sajeesan — it affects the whole registry, not one report.

### 2. ⚠ The `0xC000013A` scheduler failure hit another job yesterday

`UDESC` row 418 records, verbatim:

> *"The scheduled task fired late at 18:39 and was externally terminated before any work began
> (exit code 0xC000013A)"*

That is the **OneDrive hydration trap** named in `NEW_MACHINE_SETUP.md` — and it happened on
**2026-07-22**, on this machine, to a scheduled job living under the same OneDrive path.

**This is a live risk to REQ-17-D02**, registered today at 09:00 under
`…\OneDrive\Desktop\Abiraj_AIOS\…`. It would present as a silent no-run: the report simply stays
yesterday's and nobody is told, because the failure happens *before* the runner starts and so
before any alert can fire.

**Mitigation already in place:** `check_status.bat` shows `LastTaskResult`, and a stale status file
is itself the signal. **Not yet mitigated:** nothing actively alerts if the job never starts.
Worth watching the first few mornings, and the real fix is moving the repo off OneDrive
(`C:\dev\`), as `NEW_MACHINE_SETUP.md` already recommends.

---

## Sign-off

Confirmed by the owner 2026-07-23 — **all reviewer gates signed off**:

| Gate | Reviewer | Status |
|---|---|---|
| Technical | **Sajeesan** | ✅ signed off |
| Queryability | **Tamil Selvan** | ✅ signed off |
| Business | **Thinesh** | ✅ signed off |
| Coordination / IDs | **Varmen** | ✅ signed off |

Signed off against the delivered state: **30 rows at account × marketplace, 24 columns, money per
currency and never blended, 18/18 verification checks, live on `ph_task` 422-425, and the daily
09:00 job registered and proven end to end.**

### Two things the sign-off does not resolve

- **`Active Listing` is understated ~5-6%** — stale `is_ended` flags on auto-renewing listings.
  Disclosed on both artefacts; the fix belongs to the listings sync, not this report.
- **The ±5% trend band remains provisional** (decision E). It is editable configuration on the
  Config sheet, and the recommendation to compare against the same weekday last week still stands.
