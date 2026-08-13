# Mergeable Task Data Spec (v1)

A tiny, shared shape that any task writes so it can be dropped into a merged dashboard
**without custom decoding**. One file per task. Read-only add-on — it does **not** change
what the task already does or publishes.

---

## The file

Each task writes `<code>_merge.json` (e.g. `eppr_merge.json`) shaped like this:

```json
{
  "task":     "EPPR",
  "label":    "Product Performance",
  "owner":    "Thinesh",
  "join_key": "item_id",
  "as_of":    "2026-07-27",
  "columns": [
    { "key": "item_id", "name": "eBay Item ID", "role": "id",     "type": "text"  },
    { "key": "sku",     "name": "SKU",           "role": "id",     "type": "text"  },
    { "key": "title",   "name": "Product Title", "role": "id",     "type": "text"  },
    { "key": "revenue", "name": "Revenue",       "role": "metric", "type": "money" },
    { "key": "units",   "name": "Units Sold",    "role": "metric", "type": "num"   },
    { "key": "margin",  "name": "Margin %",      "role": "metric", "type": "pct"   }
  ],
  "rows": [
    { "item_id": "394444713965", "sku": "12IP20100", "title": "DC ...", "revenue": 2316.66, "units": 124, "margin": -14.13 }
  ]
}
```

That's the whole contract. Nothing else is required.

---

## Field meanings

| Field | Meaning |
|---|---|
| `task` | Short code, uppercase (EPPR, ESNM, ERA...). Becomes the tab code. |
| `label` | Human tab name shown to users ("Product Performance"). |
| `owner` | Who the task belongs to (PH / person). Shown on the tab. |
| `join_key` | The column every task joins on. **Use `item_id`** for eBay listing tasks. |
| `as_of` | The data date (the run's window end / anchor). Shown on the tab as "as of ...". |
| `columns` | List of columns. Each has `key`, `name`, `role`, `type`. |
| `rows` | List of objects keyed by the column `key`s. One object per listing. |

### `role`
- `id` — shared identity (SKU, Item ID, Title, Brand, Marketplace, Account, Price, Stock).
  These are the **left, pinned** columns. Every task repeats them; the merger keeps one copy.
- `metric` — the task's own numbers. These become that task's columns/KPIs on its tab.

### `type` (controls formatting + aggregation)
- `text` — shown as-is.
- `num` — integer count; card = **sum**.
- `money` — 2-decimals; card = **sum**.
- `pct` — percentage; card = **average**.
- (special: per-listing states like "days since sale" → card = **average**, mark with `"agg": "avg"`.)

---

## Rules

1. **Grain = one row per `join_key` value.** If a task is finer (per-order), it must
   pre-aggregate to one row per listing before writing this file.
2. **`id` columns must agree across tasks** (same Item ID = same listing). The merger uses
   the first task's identity and fills gaps from the others.
3. **Missing values are allowed** — a listing in one task but not another just leaves that
   task's metrics blank. Don't invent zeros.
4. **Numbers are raw numbers**, not pre-formatted strings (no "£", no commas). Formatting is
   the dashboard's job.
5. **`as_of` is required** so the merge can show freshness and never silently mix periods.

---

## How a task adopts this

Add a small **read-only emitter** to the task's automation that, right after its normal run,
writes `<code>_merge.json` from data it already has. It does not change the task's existing
outputs or publish step. ~20–30 lines per task.

Once a task emits this file, adding it to the merged dashboard is a **one-line registry entry**
(file path + colour) — no custom decoding like ESNM needed.

---

## Registry (the merged dashboard's config)

The merged dashboard reads one small list:

```json
[
  { "task": "EPPR", "file": ".../eppr_merge.json", "color": "#3a2f6b" },
  { "task": "ESNM", "file": ".../esnm_merge.json", "color": "#0f5c57" }
]
```

Add a task = add a line here. That is the whole "merge process" once the spec is adopted.

---

**Status:** spec only (v1). No task emits this file yet. Next step = pick the first task and
add its emitter (suggest ESNM, since it was the hardest to decode by hand).
