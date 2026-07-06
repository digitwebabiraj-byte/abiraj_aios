# REQ-05-D08 Source Manifest

## Project ID

PRJ-2026-001_ph-segmentation

## Requirement ID

REQ-05

## Deliverable ID

REQ-05-D08

## Date

2026-07-03

## Recording Posture

The 3 July 2026 work (Phase-08) was executed by **Abiraj in a live Claude Chat session, READ-ONLY
against the live PostgreSQL database** — no INSERT/UPDATE/DELETE/DDL, no push, nothing dropped. This
workbench record documents and imports the knowledge file and cross-references the deliverables.
Evidence rule: **VERIFIED_FROM_FILE** = saved checksummed file here; **DOCUMENTED_IN_D08** = stated in
the D08 knowledge file (live read-only, not re-derived here); **LIVE_STATE_NOT_RECHECKED** = live state.

## What D08 delivered (from the knowledge file)

1. **Assigned Listings confirmation** — read-only re-derivation per PH reconciled to `public.traffic_data`,
   **diff 0 for all 24 PHs** (paulr = 466 listings / 464 distinct ASINs). The count each PH's card shows.
2. **Preview-only clarity pass** — jargon removed ("Method-A", "returning-aware" → 0 remaining), category-click
   filtering, explicit window date ranges (31 May–27 Jun vs 3 May–30 May), a per-PH allocated card, plainer
   Segment-mix / Movement labels. **Preview only — not pushed live** (live `ph_task` id 5 unchanged from D07).
3. **24 single-PH-locked standalone dashboards** — one per PH, other PHs' data physically removed, dropdown
   hidden, filenames per Bietrick's authoritative spelling list.

## Attribution note (D07 ⇄ D08 overlap — read this)

Deliverables **2** and **3** above were **physically imported under REQ-05-D07** (the D07 chat transcript
showed them dated 2 Jul), and are already in the repo. This D08 knowledge file dates them 3 Jul (Phase-08).
Rather than duplicate or move already-pushed files, they are **cross-referenced here by path**. The work
plausibly spanned 2–3 Jul; both source documents are preserved so the record is honest either way.

- Clarity preview → `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_asin_dashboard_catfilter_preview.html`
- 24 per-PH locked views → `evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_per_holder_views/` (+ `.sha256` index)

## Sources

| Source File | Original Path | Canonical Destination | Size | SHA-256 | Classification | Status |
| ----------- | ------------- | --------------------- | ---: | ------- | -------------- | ------ |
| 2026-07-03__abiraj__ph-asin__REQ-05-D08.md | DigitWeb_Works_Abiraj\03_07_2026\ | handover/REQ-05_ph-asin-segmentation/2026-07-03__abiraj__ph-asin__REQ-05-D08.md | 19983 | 5813bb2c7295e3915dfc9e88e9b615136d45b74565ee6597731674111e47123d | DAILY_KNOWLEDGE | IMPORTED (checksum recorded) |
| 24 per-PH locked views | (cross-ref — imported under D07) | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_per_holder_views/ | — | see `2026-07-02_per_holder_views.sha256` | PER_HOLDER_VIEWS | ALREADY IN REPO (D07) — referenced, not duplicated |
| clarity-pass preview (catfilter) | (cross-ref — imported under D07) | evidence/final_outputs/REQ-05_ph-asin-segmentation/2026-07-02_ph_asin_dashboard_catfilter_preview.html | 891397 | a72dc10e… | DASHBOARD_PREVIEW | ALREADY IN REPO (D07) — referenced, not duplicated |
| Assigned-Listings reconciliation (diff 0, all 24 PHs) | live read-only SELECTs | — (no query output exported) | — | — | READ_ONLY_VERIFICATION | DOCUMENTED_IN_D08 (not exported) |
| 2026-07-03__abiraj__ph-asin__REQ-05-D08(old).md | DigitWeb_Works_Abiraj\03_07_2026\ | — | — | — | SUPERSEDED_DRAFT | NOT IMPORTED (vague `(old)` name; superseded by the current D08 file) |

## Claims Evidence Classification

| Claim | Evidence Status | Limitation |
| ----- | --------------- | ---------- |
| Assigned Listings correct for all 24 PHs, diff 0 (paulr 466/464) | DOCUMENTED_IN_D08 | Live read-only; no saved query output imported |
| Jargon removed (0 "Method-A" / "returning-aware") + clarity features | VERIFIED_FROM_FILE (catfilter preview) | Preview only — NOT live on `ph_task` id 5 |
| 24 single-PH-locked views (own data only, dropdown hidden, correct filenames) | VERIFIED_FROM_FILE (24 files + index in repo) | Snapshot for 2026-07; do not auto-update |
| Live DB untouched (read-only all day) | DOCUMENTED_IN_D08 | DB not queried here to confirm |
| Live dashboard `ph_task` id 5 unchanged from D07 | LIVE_STATE_NOT_RECHECKED | DB not queried |

## Missing Artifacts

**NONE new.** All D08 deliverables are either imported (knowledge file) or already in the repo from D07
(24 views + clarity preview). The Assigned-Listings reconciliation is a live read-only result, honestly
labelled DOCUMENTED_IN_D08 (no query output was exported — not a missing file, a not-created one).
(Carried from earlier: `live_v4_movrule.html` and engine v3 remain MISSING from the D07 record.)

## Duplicate Check

- D08 knowledge file imported once. GREEN.
- 24 per-PH views + clarity preview **referenced, not re-copied** — exactly one canonical copy each (under D07). GREEN.
- `(old)` draft deliberately not imported — avoids a second D08 knowledge file. GREEN.

## Result

**GREEN / PASS** — D08 is a read-only increment; its knowledge file is imported and checksummed, and every
deliverable is present in the repo (imported here or cross-referenced from D07). No live write, no push, no
duplication, no new missing artifact. The clarity pass remains a **preview pending Bietrick approval** — a
project state, not an import gap.
