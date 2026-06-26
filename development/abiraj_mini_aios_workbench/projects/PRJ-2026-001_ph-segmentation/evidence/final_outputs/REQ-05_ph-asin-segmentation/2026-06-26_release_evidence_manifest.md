# Final Output Manifest — REQ-05 Delivery Increment (Released July 2026 Report)

## Project / Task

* Project: PRJ-2026-001_ph-segmentation
* Task: REQ-05_ph-asin-segmentation (delivery/release increment, 2026-06-26)
* Re-homed 2026-06-26 from the non-compliant dated ID `REQ-20260626-002_…`; see the delivery
  record `handover/REQ-05_ph-asin-segmentation/2026-06-26_delivery_dashboard-ui-live-report-release.md`.

## Imported Asset

| Field | Value |
|---|---|
| Canonical path | `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-06-26_release_ph-asin_segmentation_report_2026-07.html` |
| Imported from | `c:\Users\digit\Downloads\PH_ASIN_Segmentation_Report_2026-07 (1).html` (original preserved; COPY-only) |
| Import date | 2026-06-26 |
| Size (bytes) | 457,618 (446.9 KB) |
| SHA-256 | `6F126A4E365934ACD4A0D9AEA539B3FE6620C4EE54C4F9191350B4DE76FEEE87` |
| Copy integrity | VERIFIED (source and destination SHA-256 identical) |

This is a **new build** — its SHA-256 differs from the previous 2026-06-24 D02 file
(`25dd9103…29f7f74c`), confirming it is not the onboarding-era HTML.

## Facts Read Directly From the File (VERIFIED)

Extracted read-only from the embedded data object `D` (line 98) and document head:

| Fact | Value in file | Matches reported claim? |
|---|---|---|
| Title / period | "PH ASIN Segmentation Report — July 2026" | yes |
| `meta.period` | "JULY 2026" | yes |
| `meta.window` | "1 Jun → 30 Jun 2026 (FBM only)" | yes — June window |
| `meta.prev` | "1 May → 30 May 2026" | yes — prior window |
| `meta.generated` | "26 Ju…" (26 June 2026) | yes — confirms partial-June generation |
| Distinct PHs | 24 | yes — 24 PHs |
| Priority card records (`"asin"`) | 1,765 | yes — 1,765 priority cards |
| `segTotal` | HHH 77 · HHL 479 · HLH 157 · LHH 17 · LLH 349 · LLL 6776 | — |
| `segTotal` sum | **7,855** | yes — 7,855 segmentation rows |
| `lllShown` | 686 | yes — 686 LLL priority items |
| "Mark done" persistence | browser `localStorage` (`exportTicks`/`importTicks` JSON) | confirms **NOT** database-backed (open item #6) |

## Facts NOT Provable From the File (remain REPORTED_BY_ABIRAJ)

| Claim | Why not provable from file | What file shows instead |
|---|---|---|
| 57 category benchmarks | File embeds only the 1,765 priority cards | 51 distinct categories (`"cat"`) appear among embedded cards; full 7,855-row set is not embedded (LLL banner states the complete list lives in `analytics.ph_segment_report`) |
| Dashboard release: `tech_team_outputs.ph_task` row id 5, status `released` | Database state, not in the file | n/a — DB was not queried (prohibited) |
| Delivered HTML byte-for-byte identical to the DB HTML | The DB copy was not pulled (DB query prohibited) | Delivered-file SHA-256 recorded above as the reference for a future, approved DB comparison |
| Monthly PostgreSQL routine built | No routine file supplied/imported | n/a |

## UI-Fix Claims (PARTIAL)

The file contains a dedicated "Mark done" tick mechanism separate from segment data, sidebar
rendering code, and the LLL escalation banner — consistent with the reported card/sidebar/
indicator work. The **visual** correctness (no badge/button overlap, full-height sidebar) cannot
be confirmed headlessly and remains REPORTED_BY_ABIRAJ pending a rendered visual review.

## Method

All values read with read-only file inspection (`Get-FileHash`, regex extraction over the
embedded data line). No live database or dashboard was contacted. No SQL executed.
