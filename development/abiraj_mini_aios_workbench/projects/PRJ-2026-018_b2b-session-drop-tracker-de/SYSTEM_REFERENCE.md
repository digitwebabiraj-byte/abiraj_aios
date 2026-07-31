# SYSTEM_REFERENCE — B2B Session Drop Tracker · Amazon.de (bsdt)

Complete functional detail of what this system does, for a leader or a new engineer. Derived from
the canonical source (`B2B_Session_Drop_Tracker_DE.xlsx`, 3 tabs) and the data-source investigation
of 2026-07-31.

| | |
|---|---|
| Project | `PRJ-2026-018_b2b-session-drop-tracker-de` · code `bsdt` (provisional) |
| Task | `REQ-21_b2b-session-drop-tracker-de` (provisional) |
| End user | **Jensika** (`staff.users` id 99, Active, Nelliady) |
| Deliverables | **D01** the report = interactive HTML dashboard + xlsx workbook + governed JSON (built, verified 2026-07-31) · **D02** scheduled refresh (not started) |

---

## 1. Purpose

For every Amazon.de child ASIN with business-customer (B2B) traffic in either of two matching 30-day
windows, show how its **B2B Sessions, Page Views and Orders** changed between the previous and
current window, tier it by B2B session volume, and assign one fixed action per tier — so a real
decline in visibility to **business buyers** gets caught and investigated.

It deliberately does **not** use B2B Conversion %: per-ASIN B2B session volume on .de is too low for
a percentage to mean anything. The system **recommends only** — applying an action is a human step in
Seller Central.

---

## 2. Source of record

A direct **Amazon.de Seller Central Business Report** export — *Detail Page Sales and Traffic by
Child Item* — using the **B2B-only** columns (Sessions·Total·B2B, Page Views·Total·B2B, Units
ordered·B2B), exported for two matching 30-day windows.

🔴 The internal database is **not** the source. `business_reports.amz_traffic_by_asin` carries the
right columns but only ~half the coverage (May 2026 absent for .de; ~half the ASINs missing), proven
by a full 527-ASIN completeness test. See `evidence/DATA_SOURCE_ANALYSIS.md`.

---

## 3. Windows

| Cycle | Range |
|---|---|
| **Current** | 2026-06-16 → 2026-07-15 |
| **Previous** | 2026-05-17 → 2026-06-15 |

Each is a 30-day window; the two are contiguous. Future refreshes carry whatever two matching
windows the new export covers.

---

## 4. The tier / action engine

Tier is set purely by **MAX(Prev, Current) B2B Sessions** against two editable boundaries on the
Thresholds tab. Status and Action follow directly from Tier. Session Change, Units Orders and Buy
Box % are context only.

| Tier | Rule `MAX(prev,current)` | Status | Action (summary) |
|---|---|---|---|
| **Tier 1 – Low** | `< 5` | Low Volume - Setup Needed | Set a Business Price (5–10% below retail) + Quantity Discount tiers (5+ units 5% off, 10+ units 10% off); add bulk/case-pack info to title & bullets |
| **Tier 2 – Moderate** | `≥ 5` and `< 10` | Moderate - Review | Light check — Buy Box %, confirm Business Price/Quantity Discount still active, quick scan of title & main image |
| **Tier 3 – High** | `≥ 10` | High - Priority Review | Priority review — Buy Box % & stock, Business Price & Quantity Discount tiers, spec table + bulk/case-pack info, A+ business use-case content, Business-only offers, VAT invoicing, backend B2B search terms, certifications visible |

**Result over the source export (526 ASINs):** Tier 1 – Low **506** · Tier 2 – Moderate **16** ·
Tier 3 – High **4**.

---

## 5. Thresholds — configuration, never code

Tier 2 lower bound (**5**) and Tier 3 lower bound (**10**) live on the workbook's **Thresholds**
sheet as editable cells (`B4`, `B5`). The Tracker's Tier column is a live formula reading them, so
changing either boundary re-tiers all rows. Never inline a threshold.

---

## 6. Output — the Tracker (12 columns)

`ASIN · Prev B2B Sessions · Prev B2B Page Views · Prev B2B Orders · Current B2B Sessions · Current
B2B Page Views · Current B2B Orders · Buy Box % (Current) · Session Change · Tier · Status · Action`.
Grain = one row per child ASIN. Session Change = Current − Prev B2B Sessions (derived).

Inclusion rule: an ASIN appears only if it had some B2B Sessions or Page Views in ≥ 1 window.

---

## 7. Deliverables (REQ-21-D01)

- `evidence/final_outputs/REQ-21_.../REQ-21-D01_b2b_session_drop_tracker_DE.html` — interactive
  dashboard (KPI cards, tier filter chips, ASIN search, only-drops toggle, sortable columns,
  colour-coded Session Change, CSV export).
- `..._REQ-21-D01_b2b_session_drop_tracker_DE.xlsx` — workbook: Tracker (live Thresholds-driven Tier
  formulas) · editable Thresholds · Summary · Data Notes.
- `sql/REQ-21_.../` — reproducible build: `build_bsdt.py` (→ governed `bsdt_data.json`),
  `build_xlsx.py`, `gen_dashboard.py`.

---

## 8. Verification

Engine independently re-derived and reconciled across all four artefacts (source Excel ↔ governed
JSON ↔ built xlsx ↔ dashboard) — **0 mismatches** on Session Change, Tier, Status and Action; tier
distribution 506 / 16 / 4 reproduced exactly. See `validation/REQ-21_.../2026-07-31_verification.md`.

---

## 9. Open items (gate BUILD → PUBLISH)

- `ph_task` audience/team for Jensika (just her, or a group?).
- IDs `REQ-21` / `bsdt` confirmation.
- D02 scheduled refresh — needs a repeatable export each cycle (owner-supplied) since the DB can't
  be the source.
