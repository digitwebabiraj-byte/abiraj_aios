# PH ASIN Segmentation — Reusable Methods (Capability Extract)

> Reusable, generalisable techniques extracted from this project's work summaries. These are
> methods worth reusing on other projects — not project-specific facts.
> **Source:** `handover/REQ-05_ph-asin-segmentation/2026-06-23__abiraj__ph-asin__REQ-05-D01.md`
> and `…D02.md` ("Cross-Project Applicability" / "Reusable Logic" sections), and the engine
> `sql/REQ-05_ph-asin-segmentation/2026-06-25_ph_segment_engine.sql`.

## 1. Scope-check an MCP/DB connection before using it
Before running real work on a database/MCP connection, verify it is correctly scoped with a
2-call check: `list_schemas` + an `information_schema.tables` count. It must expose only the
allow-listed tables and be `SELECT`-only. **Never run a write to "test" write capability** — the
tool surface is sufficient evidence. Any deviation = hard stop + escalate.
*Reusable for every MCP/DB integration.*

## 2. Confirm fulfilment scope before any sales-ranked metric
FBA vs FBM (or any fulfilment/channel split) silently skews "top sellers". In this project ~23%
of in-scope units were FBA and were inflating the benchmark; filtering to FBM re-segmented 100+
ASINs. **Always confirm the fulfilment/channel scope before ranking by sales.**
*Reusable across PPC, CFIS, any Amazon analytics.*

## 3. Inspect before you build
Check whether an existing table already answers the requirement before constructing new
analytics. Here it shrank a "build" into a "read-and-show".

## 4. Document-vs-live conflict register
When a written spec and a live system disagree (grouping, cadence, naming), **log the conflicts
and route them to the owner** — never silently pick one. Prevents two competing sources of truth.

## 5. Pre-compute-then-serve
Materialise heavy per-row analytics into one output table; UIs/reports read that table and never
recompute. (Here: `analytics.ph_segment_report`.)

## 6. Parameter-free scheduled engine via window auto-detect
For a monthly/periodic job, auto-detect the window instead of hard-coding dates:
current = `MAX(period_end)`, previous = the next-lower window. No dates to edit each cycle.

## 7. Per-entity, per-category dynamic benchmark
Benchmark each item only against its peers (top-30 sold, min-10, flag if <10) within the same
owner+category — never a single global average across unlike things.

## 8. Method A vs pooled averages
"Average of the per-item rates" (Method A) ≠ "pooled rate". Choose deliberately and state which;
Method A produces an intentionally high, peer-relative bar.
