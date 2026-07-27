# Task closure — REQ-17 Daily Sales Track

| | |
|---|---|
| **Project** | `PRJ-2026-015_daily-sales-track` · code `dst` |
| **Task** | `REQ-17_daily-sales-track` |
| **Deliverables** | **REQ-17-D01** (report) · **REQ-17-D02** (daily automation) |
| **Opened / closed** | 2026-07-23 — same day |
| **Status** | ✅ **CLOSED — DELIVERED, AUTOMATED, SIGNED OFF** |
| **Requester / Business Validator** | Thinesh |

## What was delivered

A daily eBay sales tracker: **30 rows at account × marketplace, 24 columns**, reporting yesterday
against the day before and the same calendar date last year, with sales, orders, units, AOV, active
listings and the AH/PH split. **Money is reported per currency and never blended.**

Three artefacts from **one governed dataset**, so the workbook and dashboard cannot drift — the
structural fix for the defect REQ-16 shipped.

**Live:** `tech_team_outputs.ph_task` ids **422–425**, audience `ebay_priors`
(Thinesh · Jarsini · kobiga · powsteena).

**Automated:** Windows task `DST_Daily_Sales_Track`, **every day 09:05**, fail-closed on **eleven**
gates: row count · orders · money non-zero · every row carries a currency · AH+PH=Active per row ·
**the reported day must be in the past** · per-currency sums reconcile · listing split reconciles ·
row collapse vs last good · order collapse vs last good · dashboard ≥ 20 KB. The stored payload's
md5 and `assigned_user_team` are then re-read **inside the transaction**, and the write is rolled
back on any mismatch. The fleet's **7th job and its first daily one**.

## Evidence

| | |
|---|---|
| Source (COPY, SHA-256 verified byte-identical) | `evidence/source_documents/REQ-17_daily-sales-track/` |
| Data-availability audit | `evidence/logs_or_screenshots/REQ-17_.../2026-07-23_data_availability_audit.md` |
| Verification record + addendum | `validation/REQ-17_.../2026-07-23_workbook_verification.md` |
| Duplicate check + sign-off | `validation/REQ-17_.../2026-07-23_duplicate_check_and_signoff.md` |
| Deliverables | `evidence/final_outputs/REQ-17_daily-sales-track/` |
| Requirement document | `DigitWeb_Works_Abiraj/23_07_2026/2026-07-23_abiraj_REQ-dst_REQ-17-D01.md` |

## PASS / FAIL

**PASS.** 18/18 verification checks, on a harness that does not import the builder, re-derives every
figure from a separate live query, and recalculates formulas through LibreOffice rather than reading
formula strings.

**The anchor that matters:** the report reconciles to Thinesh's own eBay Seller Hub screen —
**LEDSone UK / UK = £837.93 for 22 July**. That is now a permanent verification gate; the build
fails if it ever stops matching.

## Reviewers — all signed off 2026-07-23

Sajeesan (technical) · Tamil Selvan (queryability) · Thinesh (business) · Varmen (coordination).

## Duplicate risk: GREEN

Nothing else reports daily eBay sales at account × marketplace to `ebay_priors`. Checked
individually: `UDESC` is weekly at item-ID grain for `ph_priors`; `espd` is monthly SKU-level;
`ebpd` is monthly and is the source this project **inherits** from; `ebsr` is daily but reports
stock; `EBAYAHD` is mislabelled and actually covers Amazon FBA restock.

## What this task got wrong, and how it was caught

Nine defects. Two were serious, and **neither was found by the harness checking the report against
itself — both came from checking it against reality.**

1. **Currency.** `orders.total` is stored in the marketplace's own currency, not GBP. Every figure
   rendered with a `£` and was summed. 20 of 30 rows were mislabelled, and the blended headline read
   **"+3.19% up"** while GBP had fallen **5.16%** and EUR risen **26.23%** — it hid a decline in the
   largest market. Money is now never summed across currencies; three verification gates block
   recurrence.
2. **Grain.** A Seller Hub screenshot showed £837.93 against an account row of £1,144.51. Both were
   right — the account row combined UK and Germany. Rebuilt per marketplace.

The rest: a Config note beginning `=>` that Excel parsed as a live formula error; an Engine Inputs
header overwriting its own first data row; a header/body cell-count mismatch; **two separate
sticky-row overlaps** (header rows and footer rows each sharing a single offset); portal layout
compression; and a `$—` rendering glitch.

**Lesson worth carrying:** a verification harness proves a report is *self-consistent*. It cannot
prove the report is *right*. Both serious defects were exposed by comparing against an external
source — the requester's own screen.

## Raised for others — outside this task

1. **`ph_task` holds 30 duplicate rows** across five task_ids, including **7 with a NULL `task_id`**
   that can never be found or updated in place. Live has **no UNIQUE constraint on `task_id`**
   despite the sample DDL claiming one. → **Sajeesan**, registry-wide.
2. 🔴 **The `0xC000013A` scheduler trap fired on 2026-07-22** against `UDESC` — *"fired late at 18:39
   and was externally terminated before any work began"*. It presents as a **silent no-run** and
   threatens all seven jobs on this OneDrive path. The durable fix is moving the repo to `C:\dev\`.
   → machine owner.
3. **`Active Listing` is understated ~5–6%** — eBay shows 3,033 active on LEDSone UK's UK site
   against 2,843 here. Stale `is_ended` flags on auto-renewing listings. Affects **any** report
   counting eBay listings, not only this one. Disclosed on both artefacts. → **Sajeesan**.

## Open, non-blocking

- **Decision E** — the ±5% trend band is provisional. Measured: a normal day swings 15–60% by
  account, so "Stable" almost never appears. Recommendation: compare against the **same weekday last
  week**. It ships as editable configuration on the Config sheet.
- **Decision O** — the existing `ph_dashboard` Django app (`analytics_phmonthchannel`) has never been
  checked for overlap; `dbhub_readonly` has no grants on it, so it needs the `ph_pgsql` role.

## One next action

**After 09:05 tomorrow (2026-07-24), run `automation\check_status.bat`.** A fresh line ending
`published 4 rows - OK` confirms the job is genuinely self-running. A *manually* triggered run has
been proven; an *unattended scheduled fire* has not, and that is precisely the distinction the
`0xC000013A` trap exploits.
