# Import + integrity evidence — REQ-12_ebay-price-checker (2026-07-16)

COPY-only import. Origins in `C:\Users\digit\Downloads\` preserved untouched.

## Source file
| File | SHA-256 | Bytes |
|---|---|---|
| origin `Downloads\Ebay System Task -Thinesh.xlsx` | `0cbfd8f32ee7a3a7ff1f9f6d8b3bf20fbccab3ad1bebbd3423cadc56818ce353` | 54,301 |
| copy `evidence/source_documents/REQ-12_.../Ebay System Task -Thinesh.xlsx` | `0cbfd8f32ee7a3a7ff1f9f6d8b3bf20fbccab3ad1bebbd3423cadc56818ce353` | 54,301 |

**✅ Byte-for-byte identical.** Origin re-hashed after copy, unchanged.

## Duplicate-risk (Existing-Asset-First)
- `Downloads\Ebay System Task -Thinesh (1).xlsx` — content-identical (54,301 bytes), different SHA-256
  `e4370e8b1cbff072ff999993d8001e986e30225dc0f1a854347ea8d046c21b9b` (metadata-only re-export).
  **NOT imported** — the canonical file is the one without `(1)`.
- No prior workbench project covers eBay price checking (PRJ-2026-001 → PRJ-2026-009 checked).
- No existing price-checker DB asset (both databases swept — see the source-audit log).

## Deliverables registered (built during D01, 2026-07-16)
| File | SHA-256 | Bytes |
|---|---|---|
| `..._price-checker_UI.xlsx` | `625293bb01f3f08b3b95dd2948c9be33d86b5deaa93955b469fc13a7bdf3c3c5` | 9,281,112 |
| `..._price-checker_dashboard.html` | `4b52b45351ef2a45145165e70fb8ea2b015eea73acc06893e463db757f83d600` | 18,235,565 |
| `..._decision-sheet-thinesh.md` | `54957c22bcc92e0dc7f0882e5d193def4b8e2a0a659fcb113f43287ba3f3e27c` | 8,332 |
| `build_price_checker_xlsx.py` | `57485e44273bee16cfc33756311a73de3c2f9ba126fd82be452552eed2263b1a` | 5,045 |
| `build_dashboard_html.py` | `ff2cc6a409396980dd0526505e7902047157e3b874684ba95b16185f284031f1` | 28,608 |
| `publish_to_ph_task.py` | `af56932a2a66310ff14168bf5c01f477ac68c083657ca32e3e428c5a15cb2edb` | 4,776 |

*(The dashboard HTML size differs by a few hundred bytes from the copy published to `ph_task` id 264,
18,235,217 bytes — later UI polish edits post-date the publish. The published row can be refreshed in
place via an `UPDATE` if the exact byte match is required.)*

## Note
The **CONFIRMED BUSINESS RULE** and **Thinesh's Q1–Q8** had no source file — they arrived as chat text and
were captured verbatim into `evidence/source_documents/REQ-12_.../` at onboarding. They are the canonical
record of the authoritative spec.
