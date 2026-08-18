# VM rating collector — REQ-29 (avm)

Runs the Amazon rating collection on an always-on machine so it continues after the laptop
is shut down. **Contains no credentials and touches no database** — it reads a list of
ASINs and writes a JSON file. Safe to copy anywhere.

## Setup on the VM (one time)

1. Copy this whole `vm_scraper` folder to the VM.
2. Install Python 3 if it is not there, then:

       pip install requests beautifulsoup4 lxml

## Run it

    python vm_scrape.py

Leave it running. It prints progress every 20 ASINs with an hours-remaining estimate.

- **Resumable** — Ctrl+C or a reboot loses nothing. Re-run the same command and it skips
  everything already collected.
- **Patient** — if Amazon rate-limits, it waits (2 min, then 5, 10, 15, 30, 45, 60) and
  retries the SAME ASIN rather than skipping it.
- **Honest** — it never solves CAPTCHAs, never disguises itself. If Amazon refuses for
  24 straight cooldowns it stops and says so.

### Keep it running after you disconnect

AnyDesk/RDP disconnect will not stop it, but closing the console will. Use one of:

**Windows**

    start /b python vm_scrape.py > scrape.log 2>&1

**Linux**

    nohup python3 vm_scrape.py > scrape.log 2>&1 &

Then watch with `type scrape.log` (Windows) or `tail -f scrape.log` (Linux).

## When it finishes

Copy **`avm_ratings_cache.json`** back to:

    Abiraj_AIOS/development/abiraj_mini_aios_workbench/projects/
      PRJ-2026-025_amazon-asin-variation-merge/sql/REQ-29_amazon-asin-variation-merge/

If a cache file is already there, the two need merging rather than overwriting — say so and
it will be merged key by key (both are plain JSON objects keyed by ASIN).

Then rebuild the report on the laptop:

    python build_avm_d01.py
    python render_avm_dashboard.py

## Files

| File | What it is |
|---|---|
| `vm_scrape.py` | the collector — no DB, no secrets |
| `asins_todo.txt` | the worklist: 18,644 ASINs still needing a rating |
| `avm_ratings_cache.json` | created by the run; the thing you copy back |

## Scope of the worklist

Amazon **UK**, accounts **amazon Ledsone (8)** and **amazon Dcvoltage (6)** — Prasath's
confirmed scope (Q2/Q3). Only **active listings inside multi-child variation families** are
included, because nothing else can be merged. That is why the list is 18,644 and not the
full 31,286 ASINs in the export.

## ⚠ Expect this to be slower on a VM than on the laptop

Amazon treats datacenter IP addresses far more harshly than home broadband. The laptop ran
112 minutes without a single block. A VM may be throttled much sooner, or refused outright.

**Test it before committing to the long run:** let it fetch 20–30 ASINs and check the log.
If you see `ok=` climbing with `blocks=0`, it is working. If it blocks immediately and keeps
blocking, the VM's IP is the problem — tell Abiraj, because then the real answer is to have
Sajeesan ingest Amazon ratings into the warehouse instead of scraping at all.
