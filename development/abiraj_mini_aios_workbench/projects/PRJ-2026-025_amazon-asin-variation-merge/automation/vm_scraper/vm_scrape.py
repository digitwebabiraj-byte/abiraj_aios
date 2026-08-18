"""
REQ-29 · standalone VM rating collector.

Runs on any always-on machine. Reads a plain list of ASINs, fetches each one's Amazon UK
rating + review count, writes a resumable JSON cache. Copy the cache back when done.

NO DATABASE. NO CREDENTIALS. NO SECRETS. It reads asins_todo.txt and writes
avm_ratings_cache.json — nothing else. Safe to hand to any machine.

    pip install requests beautifulsoup4 lxml
    python vm_scrape.py

Stop it any time with Ctrl+C; re-running resumes and never re-fetches a collected ASIN.

Rate limiting: we ask slowly and back off when Amazon says no. We do NOT rotate user
agents, spoof fingerprints, use proxies, or attempt CAPTCHAs. If Amazon refuses after the
escalating cooldowns, the run stops and reports honestly.
"""
import json, random, re, sys, time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
TODO = HERE / "asins_todo.txt"
CACHE = HERE / "avm_ratings_cache.json"

DELAY = (3.0, 6.5)
COOLDOWNS = [120, 300, 600, 900, 1800, 1800, 2700, 2700, 3600, 3600]
MAX_BLOCKS = 24
CHECKPOINT_EVERY = 20

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"),
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
NUM_RE = re.compile(r"([\d,]+(?:\.\d+)?)")


def scrape_one(session, asin):
    """(rating|None, reviews|None, status) — status: ok | no_reviews | error:*

    The rating is read ONLY from inside #averageCustomerReviews. A page-wide regex for
    "X out of 5 stars" is WRONG — Amazon pages carry other products' ratings in
    recommendation carousels, so on a child page with no reviews the first match belongs
    to a DIFFERENT product. That bug was found and fixed on 2026-08-18; do not reintroduce it.
    """
    try:
        r = session.get(f"https://www.amazon.co.uk/dp/{asin}", timeout=25)
    except Exception as exc:
        return None, None, f"error:{type(exc).__name__}"
    if r.status_code != 200:
        return None, None, f"error:http{r.status_code}"
    html = r.text
    if "captcha" in html.lower() or "Enter the characters you see below" in html:
        return None, None, "error:blocked"

    soup = BeautifulSoup(html, "lxml")
    if soup.select_one("#productTitle") is None:
        return None, None, "error:unrecognised_page"

    block = soup.select_one("#averageCustomerReviews")
    if block is None:
        return None, 0, "no_reviews"          # confirmed product page, no review block = true zero

    alt = block.select_one("i.a-icon-star span.a-icon-alt") or block.select_one("span.a-icon-alt")
    rating = None
    if alt:
        m = NUM_RE.search(alt.get_text())
        rating = float(m.group(1).replace(",", "")) if m else None
    count_el = soup.select_one("#acrCustomerReviewText")
    count = None
    if count_el:
        m = NUM_RE.search(count_el.get_text())
        count = int(m.group(1).replace(",", "")) if m else None
    if rating is None or count is None:
        return rating, count, "error:block_unparsed"   # a parse failure is NEVER "no reviews"
    return rating, count, "ok"


def main():
    if not TODO.exists():
        sys.exit(f"missing {TODO.name} — copy it next to this script")
    asins = [a.strip() for a in TODO.read_text().splitlines() if a.strip()]
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = [a for a in asins if a not in cache or cache[a]["status"].startswith("error")]
    print(f"worklist {len(asins)} | already collected {len(asins)-len(todo)} | to fetch {len(todo)}",
          flush=True)

    session = requests.Session(); session.headers.update(HEADERS)
    ok = nore = err = blocks = 0
    started = time.time()
    i = 0
    while i < len(todo):
        asin = todo[i]
        rating, count, status = scrape_one(session, asin)

        if status == "error:blocked":
            if blocks >= MAX_BLOCKS:
                print(f"  blocked {blocks} times — Amazon is refusing sustained access from this "
                      f"machine. Stopping with {len(cache)} collected.", flush=True)
                break
            wait = COOLDOWNS[min(blocks, len(COOLDOWNS) - 1)]
            blocks += 1
            CACHE.write_text(json.dumps(cache, indent=1))
            print(f"  BLOCKED at {i}/{len(todo)} (#{blocks}) — waiting {wait//60} min, "
                  f"then retrying {asin}", flush=True)
            time.sleep(wait)
            session = requests.Session(); session.headers.update(HEADERS)
            continue                                   # retry the same ASIN, never skip it

        cache[asin] = {"rating": rating, "reviews": count, "status": status,
                       "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        ok += status == "ok"; nore += status == "no_reviews"; err += status.startswith("error")
        i += 1
        if i % CHECKPOINT_EVERY == 0 or i == len(todo):
            CACHE.write_text(json.dumps(cache, indent=1))
            rate = i / max(1e-9, time.time() - started)
            print(f"  {i}/{len(todo)}  ok={ok} no_reviews={nore} err={err} blocks={blocks} "
                  f"~{int((len(todo)-i)/rate/3600)}h left", flush=True)
        time.sleep(random.uniform(*DELAY))

    CACHE.write_text(json.dumps(cache, indent=1))
    print(f"DONE | {len(cache)} in cache | {blocks} block(s) | "
          f"{int((time.time()-started)/60)} min", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nstopped — progress is saved, re-run to resume")
