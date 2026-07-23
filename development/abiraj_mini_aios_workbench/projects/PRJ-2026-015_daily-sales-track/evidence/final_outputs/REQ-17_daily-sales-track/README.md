# Deliverables — REQ-17-D01 Daily Sales Track

**Status: EMPTY. Nothing built.**

## What lands here

REQ-17-D01 is **one deliverable rendered three ways**, all produced by the single generator in
`sql/REQ-17_daily-sales-track/build_dst_d01.py`:

| Artefact | File | Contents |
|---|---|---|
| Governed dataset | `dst_d01_data.json` | The single dataset both renderers read |
| Reviewer dashboard | `REQ-17-D01_dst_dashboard.html` | 22 columns · the 9 KPIs as cards that recompute on the filtered view · account / marketplace / trend filters · date selector · frozen Account column · trend colour bars · CSV export. **Static-rendered** — the `ph_task` viewer runs no JavaScript |
| Reviewer workbook | `REQ-17-D01_daily_sales_track.xlsx` | *Daily Sales Track* (22 columns) · *KPI Summary* (the 9 KPIs) · *Config* (editable trend thresholds) · *Data Notes* (every source, inheritance, assumption and gap) |

## Disclosure requirements — these ship *inside* the artefacts, not only in the governance files

- The six **AH/PH columns**, if still undefined, appear **present and visibly blank** with the reason
  stated. Never silently omitted, never guessed.
- The **anchor day** and whether it is complete.
- The **REQ-16 divergence** — this report filters `Completed` only (trading revenue), while ESNM
  included Refunded and Inprogress (demand). Without this note, a reader comparing the two will find
  sales figures that do not tie and assume one is wrong.
- Which **`Active Listing`** definition was adopted, and that the other governed report uses the
  other one.
- Any **gaps in the daily series**.
