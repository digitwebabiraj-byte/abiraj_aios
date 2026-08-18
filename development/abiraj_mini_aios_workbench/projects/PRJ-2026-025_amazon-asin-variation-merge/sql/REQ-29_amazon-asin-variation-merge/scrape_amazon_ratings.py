"""
REQ-29-D01 · step 1 of 2 — Amazon rating / review-count collector.

WHY THIS EXISTS
    Amazon product star rating and review count exist in NEITHER company database
    (owner-confirmed 2026-08-18; see evidence/logs_or_screenshots/REQ-29_.../
    2026-08-18_data_foundation_probe.md).  They are the primary selection criterion
    for this report, so they are collected from the public Amazon UK product page.
    Everything else in the report comes from SQL.

WHAT IT DOES
    1. Picks the pilot universe from listings.amazon_listings (read-only).
    2. Fetches each ASIN's public product page and extracts rating + review count.
    3. Writes a resumable JSON cache.  Re-running skips ASINs already collected.

HONESTY RULES
    - The rating is read ONLY from inside the #averageCustomerReviews block.  A page-wide
      regex for "X out of 5 stars" is WRONG: Amazon pages carry OTHER products' ratings in
      recommendation carousels, so on a child page with no reviews of its own the first
      match belongs to a DIFFERENT PRODUCT.  Verified 2026-08-18 — that bug produced
      "4.5 stars / 0 reviews" rows in the first build (and even mis-read the parent
      B084VPLPS5 as 4.5 when its true rating is 4.4).  It was found and corrected.
    - No review block on a CONFIRMED product page == a true zero (Amazon omits the block
      entirely when a product has never been reviewed).
    - A block that exists but does not parse is status='error:block_unparsed', NEVER 0 —
      recording it as 0 would invent a merge candidate out of a parse failure.
    - A page that FAILS (network error, block, non-200, not a product page) is
      status='error' and is NEVER treated as "no reviews" — the two are different and
      must not be conflated.
    - Nothing is guessed.  No value is carried over from another ASIN.

READ-ONLY: SELECT only against the database; GET only against Amazon.
"""
import json, os, random, re, sys, time
from pathlib import Path

import psycopg2
import psycopg2.extras
import requests
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
CACHE = HERE / "avm_ratings_cache.json"

# ── Scope — CONFIRMED BY PRASATH 2026-08-18 (Q2, Q3) ─────────────────────────────
#   Q2 accounts: amazon Ledsone (8) AND amazon Dcvoltage (6).  SRM (9) excluded.
#   Q3 market  : UK only.
# Configurable per run so the estate can be covered account by account rather than in
# one impossible sitting.  AVM_SUB_SOURCES="6" scrapes Dcvoltage, "8" Ledsone, "8,6" both.
SITE = "UK"
SUB_SOURCES = [int(x) for x in os.environ.get("AVM_SUB_SOURCES", "8,6").split(",") if x.strip()]
PILOT_FAMILIES = int(os.environ.get("AVM_PILOT_FAMILIES", "150"))
MIN_CHILDREN = int(os.environ.get("AVM_MIN_CHILDREN", "2"))
MAX_CHILDREN = int(os.environ.get("AVM_MAX_CHILDREN", "12"))

# ── Rate limiting ────────────────────────────────────────────────────────────────
# Amazon rate-limited the first run after ~274 requests at ~2.5s spacing.  The answer is
# to ASK MORE SLOWLY and to BACK OFF when told to — not to disguise the traffic.  We do
# not rotate user agents, spoof fingerprints, use proxies, or attempt to solve CAPTCHAs;
# if Amazon keeps refusing after the escalating cooldowns below, the run stops and says so.
DELAY = (3.0, 6.5)                          # base spacing between requests
# Escalating pause after each block, then a plateau. The run is meant to grind through the
# whole universe unattended over hours, so it stays patient rather than giving up early.
COOLDOWNS = [120, 300, 600, 900, 1800, 1800, 2700, 2700, 3600, 3600]
MAX_BLOCKS = int(os.environ.get("AVM_MAX_BLOCKS", "24"))   # ~ up to 12h of waiting
CHECKPOINT_EVERY = 20                       # write the cache this often

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"),
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

NUM_RE = re.compile(r"([\d,]+(?:\.\d+)?)")

# ⚠ DO NOT parse the rating with a page-wide regex for "X out of 5 stars".
#   An Amazon product page carries other products' ratings (recommendation carousels,
#   "customers also viewed", the variation twister).  A page-wide match returns the FIRST
#   one found, which on a child page with no reviews of its own is ANOTHER PRODUCT's rating.
#   Verified 2026-08-18: B084VPHL47 has no reviews, but a page-wide regex returned "4.5";
#   B084VPLPS5's true rating is 4.4 while the page-wide regex returned 4.5.
#   The rating MUST be read from inside the #averageCustomerReviews block only.


def db():
    return psycopg2.connect(
        host=os.environ["LED_PGHOST"], port=os.environ.get("LED_PGPORT", "5432"),
        dbname=os.environ["LED_PGDATABASE"], user=os.environ["LED_PGUSER"],
        password=os.environ["LED_PGPASSWORD"], connect_timeout=30,
    )


def pilot_universe(conn):
    """The pilot slice: active UK/Ledsone listings in multi-child variation families."""
    sql = """
    WITH fam AS (
      SELECT parent_sku, COUNT(*) AS children
      FROM listings.amazon_listings
      WHERE site=%s AND sub_source = ANY(%s) AND is_child=1
        AND parent_sku IS NOT NULL AND status='Active'
      GROUP BY parent_sku
      HAVING COUNT(*) BETWEEN %s AND %s
      ORDER BY COUNT(*) DESC
      LIMIT %s
    )
    SELECT a.asin, a.sku, a.parent_sku, a.is_parent, a.is_child, a.status,
           a.quantity, a.title, a.price, a.selected_variations, f.children
    FROM listings.amazon_listings a
    JOIN fam f ON f.parent_sku = a.parent_sku
    WHERE a.site=%s AND a.sub_source = ANY(%s) AND a.asin IS NOT NULL
      AND a.status = 'Active'          -- EFFICIENCY: an inactive listing cannot be merged
    ORDER BY a.parent_sku, a.is_parent DESC, a.asin;
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, (SITE, SUB_SOURCES, MIN_CHILDREN, MAX_CHILDREN,
                          PILOT_FAMILIES, SITE, SUB_SOURCES))
        return [dict(r) for r in cur.fetchall()]


def scrape_one(session, asin):
    """Return (rating|None, review_count|None, status). status: ok | no_reviews | error."""
    try:
        r = session.get(f"https://www.amazon.co.uk/dp/{asin}", timeout=25)
    except Exception as exc:                                  # network / timeout
        return None, None, f"error:{type(exc).__name__}"
    if r.status_code != 200:
        return None, None, f"error:http{r.status_code}"
    html = r.text
    if "captcha" in html.lower() or "Enter the characters you see below" in html:
        return None, None, "error:blocked"                    # never solved, only reported

    soup = BeautifulSoup(html, "lxml")
    if soup.select_one("#productTitle") is None:
        return None, None, "error:unrecognised_page"          # not a product page — never assume

    block = soup.select_one("#averageCustomerReviews")
    if block is None:
        # Amazon omits the review block entirely when a product has never been reviewed.
        # The page IS a product page (checked above), so this is a true zero.
        return None, 0, "no_reviews"

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
        # The block exists but did not parse. That is a PARSE FAILURE, not "no reviews".
        # Recording it as 0 would invent a merge candidate — see the module docstring.
        return rating, count, "error:block_unparsed"
    return rating, count, "ok"


def main():
    conn = db()
    rows = pilot_universe(conn)
    conn.close()
    # ── EFFICIENCY: order the work family-round-robin, and learn as we go ──────────
    # Two measured facts drive this (2026-08-18):
    #  (a) 244 of 1,847 pilot ASINs are Inactive -> excluded in SQL above.
    #  (b) ~60% of families already share ONE rating across every member, i.e. Amazon has
    #      already merged them. Those families have nothing to recommend, so once a family
    #      is PROVEN merged we stop fetching its remaining members.
    # Round-robin (member 1 of every family, then member 2, ...) means a run that is cut
    # short still covers ALL families shallowly rather than a few families deeply.
    by_family = {}
    for r in rows:
        by_family.setdefault(r["parent_sku"], []).append(r["asin"])
    for k in by_family:
        by_family[k] = sorted(set(by_family[k]))
    asins = []
    depth = 0
    while True:
        layer = [v[depth] for v in by_family.values() if len(v) > depth]
        if not layer:
            break
        asins.extend(layer)
        depth += 1
    family_of = {a: k for k, v in by_family.items() for a in v}
    print(f"scope: site={SITE} sub_sources={SUB_SOURCES} families<={PILOT_FAMILIES} "
          f"children {MIN_CHILDREN}-{MAX_CHILDREN}", flush=True)
    print(f"universe: {len(rows)} listing rows | "
          f"{len({r['parent_sku'] for r in rows})} families | {len(asins)} distinct ASINs",
          flush=True)

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = [a for a in asins
            if a not in cache or cache[a]["status"].startswith("error")]
    print(f"already cached: {len(cache)} | to fetch: {len(todo)}", flush=True)

    session = requests.Session()
    session.headers.update(HEADERS)
    ok = nore = err = 0
    blocks = 0
    started = time.time()

    # A family is PROVEN merged when >= MERGED_PROOF members are cached with an identical
    # (rating, reviews) pair and reviews > 0. Skipped members are RECORDED, never silently
    # dropped, so coverage stays auditable and a later run can fill them in.
    MERGED_PROOF = int(os.environ.get("AVM_MERGED_PROOF", "3"))

    def family_is_proven_merged(fam_key):
        seen = [(cache[a]["rating"], cache[a]["reviews"]) for a in by_family.get(fam_key, [])
                if a in cache and cache[a]["status"] == "ok"]
        return len(seen) >= MERGED_PROOF and len(set(seen)) == 1 and seen[0][1] > 0

    i = 0
    skipped = 0
    while i < len(todo):
        asin = todo[i]

        fam_key = family_of.get(asin)
        if fam_key is not None and family_is_proven_merged(fam_key):
            cache[asin] = {"rating": None, "reviews": None,
                           "status": "skipped:family_already_merged",
                           "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
            skipped += 1
            i += 1
            continue

        rating, count, status = scrape_one(session, asin)

        if status == "error:blocked":
            # Amazon is telling us to slow down. Wait it out, then RETRY THE SAME ASIN.
            # We never try to defeat the block - we only wait longer each time.
            if blocks >= MAX_BLOCKS:
                print(f"  blocked {blocks} times - Amazon is refusing sustained access. "
                      f"Stopping honestly with {len(cache)} ASINs collected.", flush=True)
                break
            wait = COOLDOWNS[min(blocks, len(COOLDOWNS) - 1)]
            blocks += 1
            CACHE.write_text(json.dumps(cache, indent=1))
            print(f"  BLOCKED at {i}/{len(todo)} (block #{blocks}) - cooling down "
                  f"{wait//60} min, then retrying {asin}", flush=True)
            time.sleep(wait)
            session = requests.Session()          # fresh connection, same identity
            session.headers.update(HEADERS)
            continue                              # retry the same ASIN, never skip it

        cache[asin] = {"rating": rating, "reviews": count, "status": status,
                       "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        if status == "ok":
            ok += 1
        elif status == "no_reviews":
            nore += 1
        else:
            err += 1
        i += 1

        if i % CHECKPOINT_EVERY == 0 or i == len(todo):
            CACHE.write_text(json.dumps(cache, indent=1))
            rate = i / max(1e-9, time.time() - started)
            eta = int((len(todo) - i) / rate / 60) if rate else 0
            print(f"  {i}/{len(todo)}  ok={ok} no_reviews={nore} err={err} "
                  f"skipped_merged={skipped} blocks={blocks}  ~{eta} min left", flush=True)

        time.sleep(random.uniform(*DELAY))

    CACHE.write_text(json.dumps(cache, indent=1))
    usable = sum(1 for v in cache.values() if v["status"] in ("ok", "no_reviews"))
    print(f"DONE | {usable} usable | {skipped} skipped (family already merged) | "
          f"{blocks} block(s) survived | {int((time.time()-started)/60)} min -> {CACHE.name}",
          flush=True)


if __name__ == "__main__":
    sys.exit(main())
