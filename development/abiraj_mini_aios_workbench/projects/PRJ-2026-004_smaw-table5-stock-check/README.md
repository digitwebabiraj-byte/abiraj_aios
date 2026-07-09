# PRJ-2026-004 — SMAW Table 5 Weekly Stock Check

One-screen landing page. Canonical context lives in [PROJECT_HOME.md](PROJECT_HOME.md).

- **What:** AIOS project home for the **Table 5 Weekly Stock Check** — a governed single-source
  stock truth for PH Thuwaraga (Amazon FBM + UK warehouse + incoming supplier POs), delivered as
  a read-only SQL view (D01) and a Portfolio-Holder-facing HTML dashboard (D02).
- **Owner:** Abiraj · **End user:** Thuwaraga · **Technical:** Sajeesan · **Queryability:** Tamil Selvan
- **Active task:** `REQ-06_table5-weekly-stock-check` — see [TASK_REGISTER.md](TASK_REGISTER.md)
- **Rules for agents:** [CLAUDE.md](CLAUDE.md)
- **System functional detail:** [SYSTEM_REFERENCE.md](SYSTEM_REFERENCE.md)
- **Key deliverable:**
  `evidence/final_outputs/REQ-06_table5-weekly-stock-check/Table5_Weekly_Stock_Check_Thuwaraga.html`
- **Rebuild:** run `build_html.py` (dashboard) / `build_report.py` (Excel) over `dataset.py`;
  refresh data via `sql/REQ-06_table5-weekly-stock-check/generate_dataset.sql`.
