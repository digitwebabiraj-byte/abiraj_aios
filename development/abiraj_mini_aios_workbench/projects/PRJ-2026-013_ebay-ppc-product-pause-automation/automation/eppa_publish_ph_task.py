"""
REQ-15-D01 — publish the pause dashboard to tech_team_outputs.ph_task.

DRY RUN BY DEFAULT. Prints the exact row it would write and changes nothing.
Pass --commit to actually write.

    python eppa_publish_ph_task.py            # show the row, write nothing
    python eppa_publish_ph_task.py --commit   # write it

Two live-schema facts the sample DDL gets wrong — both verified against production 2026-07-21:

  1. `assigned_user_team` EXISTS in live (18th column) but is ABSENT from the sample DDL.
     It must be set or the row will not group into the portal for the user.
  2. There is NO unique constraint on `task_id` — production has only PRIMARY KEY (id).
     The sample DDL's `ph_task_task_id_unique` does not exist, so `ON CONFLICT (task_id)`
     raises. Refreshing a row therefore means DELETE-by-task_id + INSERT inside ONE
     transaction; a plain INSERT would silently accumulate duplicates on every run.

Credentials come from the environment (PGPASSWORD), never from this file.
"""
import os, sys, json, time, argparse, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, ".."))
FINAL = os.path.join(PROJ, "evidence", "final_outputs",
                     "REQ-15_ebay-ppc-product-pause-automation")
HTML = os.path.join(FINAL, "REQ-15-D01_eppa_dashboard.html")
DATA = os.path.join(FINAL, "eppa_d01_data.json")

DB = {
    "host":     os.getenv("PGHOST", "149.28.134.54"),
    "port":     os.getenv("PGPORT", "5435"),
    "dbname":   os.getenv("PGDATABASE", "order_management_copy"),
    "user":     os.getenv("PGUSER", "temp_user"),
    "password": os.getenv("PGPASSWORD"),
}

# ---- the row -----------------------------------------------------------------
# Identity is fixed; the window and the headline figures are DERIVED from the governed dataset,
# so a weekly refresh never republishes last week's date or counts in the row metadata.
IDENTITY = dict(
    project_name="eBay PPC Product Pause Automation",
    project_code="eppa",
    task_id="eppa_meshika_ebay_ppc_pause_dashboard",
    # House convention, verified against live 2026-07-21: all of this developer's rows
    # (ebpd, epc, ERA, frrc, PC, SMAW, ZSFO, ebft, ph-asin, WSPC) use developer='Abiraj'
    # with team='Development'. "Tech Team" appears nowhere in the table.
    team="Development",
    developer="Abiraj",
    assigned_user="meshika",
    assigned_user_team="cppc_priors",
    phase_level=1,
    version_status="released",
)


def build_row():
    """Identity + a task_name and description generated from the current governed dataset."""
    d = json.load(open(DATA, encoding="utf-8"))
    k, th, anchor = d["kpis"], d["thresholds"], d["anchor"]
    row = dict(IDENTITY)
    row["task_name"] = ("eBay PPC Product Pause Automation — LEDSone eBay UK "
                        "(30 days to %s)" % anchor)
    row["description"] = (
        "Read-only pause RECOMMENDATION report for LEDSone eBay UK Promoted Listings "
        "(Advanced / ON_SITE). One row per campaign, 30-day window to %s (the latest complete "
        "day). Rules run in order, first match wins: campaign not RUNNING -> not evaluated; "
        "Stock -> a campaign advertising a listing whose every version is at 0 units; "
        "Rule 1 -> 30D ACOS >= %g%% unless 7D ACOS < %g%%; Rule 2 -> 14D clicks >= %d with 0 "
        "orders unless 14D spend < GBP %.2f. Result: %d campaigns, %d recommended pauses "
        "(%d Stock / %d Rule 1 / %d Rule 2), GBP %s of GBP %s 30-day spend at risk. "
        "Standard (COST_PER_SALE) campaigns are excluded — they record no per-click spend, so "
        "ACOS cannot be computed. NOTHING IS PAUSED AUTOMATICALLY: this report recommends, a "
        "human applies approved pauses in Seller Hub. Requirement REQ-15, deliverable "
        "REQ-15-D01. Refreshed automatically every Monday."
        % (anchor, th["acos_ceiling"], th["acos_rescue"], th["clicks_min"], th["spend_floor"],
           k["scope"], k["paused"], k["stock"], k["r1"], k["r2"],
           format(k["spend_at_risk"], ",.2f"), format(k["spend_all"], ",.2f")))
    row["version_level"] = 1
    return row


def connect(attempts=6, first_wait=10):
    """Connect, retrying on a transient full connection pool.

    The warehouse runs max_connections=100 and a single pgAdmin desktop client has been observed
    holding 97 idle slots, leaving nothing for temp_user. That is a capacity condition, not a
    permission one — waiting is the right response, not escalating to a superuser account (whose
    reserved slots exist so an admin can rescue exactly this situation).

    Waits 10s, 20s, 40s, 80s, 160s between attempts — about 5 minutes total, which comfortably
    outlasts a transient spike while still failing closed if the pool is genuinely saturated.
    """
    import psycopg2
    wait = first_wait
    for i in range(1, attempts + 1):
        try:
            return psycopg2.connect(connect_timeout=20, **DB)
        except psycopg2.OperationalError as exc:
            transient = any(t in str(exc) for t in (
                "remaining connection slots", "too many clients",
                "server closed the connection unexpectedly", "could not connect"))
            if not transient or i == attempts:
                raise
            print("  connect attempt %d/%d failed (%s) — retrying in %ds"
                  % (i, attempts, str(exc).strip().splitlines()[0][:70], wait), flush=True)
            time.sleep(wait)
            wait *= 2


def preflight(cur, task_id, user, team):
    print("=" * 78)
    print("PRE-FLIGHT (read-only)")
    print("=" * 78)
    cur.execute("SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='tech_team_outputs' AND table_name='ph_task' "
                "AND column_name='assigned_user_team'")
    print("  assigned_user_team column present : %s" % ("YES" if cur.fetchone() else "*** NO ***"))

    cur.execute("SELECT COUNT(*) FROM pg_constraint "
                "WHERE conrelid='tech_team_outputs.ph_task'::regclass AND contype='u'")
    print("  UNIQUE constraints on the table   : %d  (0 = must pre-DELETE, never ON CONFLICT)"
          % cur.fetchone()[0])

    cur.execute("SELECT id, version_level, version_status, updated_at "
                "FROM tech_team_outputs.ph_task WHERE task_id=%s ORDER BY id", (task_id,))
    existing = cur.fetchall()
    print("  rows already on this task_id      : %d %s"
          % (len(existing), existing if existing else ""))

    cur.execute("SELECT COUNT(*) FROM tech_team_outputs.ph_task WHERE assigned_user_team=%s",
                (team,))
    n_team = cur.fetchone()[0]
    print("  existing rows for team %-11s: %d %s"
          % (team, n_team, "" if n_team else "  <-- NEW TEAM VALUE, never used before"))

    cur.execute("SELECT COUNT(*) FROM tech_team_outputs.ph_task WHERE assigned_user=%s", (user,))
    n_user = cur.fetchone()[0]
    print("  existing rows for user %-11s: %d %s"
          % (user, n_user, "" if n_user else "  <-- NEW USER, never received a ph_task row"))
    return existing


def publish(html_path=None, bump_version=True, quiet=False):
    """Refresh this report's ph_task row. Returns (id, version_level, md5).

    Called by the weekly job as well as the CLI, so the published row and the rebuilt files can
    never drift. DELETE-by-task_id + INSERT in one transaction — production has no unique
    constraint on task_id, so ON CONFLICT is unavailable and a plain INSERT would duplicate.
    """
    if not DB["password"]:
        raise RuntimeError("PGPASSWORD is not set")
    path = html_path or HTML
    html = open(path, encoding="utf-8").read()
    md5 = hashlib.md5(html.encode("utf-8")).hexdigest()

    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(MAX(version_level),0) FROM tech_team_outputs.ph_task "
                        "WHERE task_id=%s", (IDENTITY["task_id"],))
            cur_ver = cur.fetchone()[0]
        row = build_row()
        row["version_level"] = (cur_ver + 1) if (bump_version and cur_ver) else max(cur_ver, 1)

        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM tech_team_outputs.ph_task WHERE task_id=%s",
                            (row["task_id"],))
                deleted = cur.rowcount
                cols = list(row) + ["html_content"]
                cur.execute(
                    "INSERT INTO tech_team_outputs.ph_task (%s) VALUES (%s) RETURNING id"
                    % (", ".join(cols), ", ".join(["%s"] * len(cols))),
                    [row[k] for k in row] + [html])
                new_id = cur.fetchone()[0]

        with conn.cursor() as cur:                      # independent re-read
            cur.execute("SELECT MD5(html_content) FROM tech_team_outputs.ph_task WHERE id=%s",
                        (new_id,))
            got = cur.fetchone()[0]
        if got != md5:
            raise RuntimeError("published md5 %s != file md5 %s" % (got, md5))
        if not quiet:
            print("published id=%d version=%d (replaced %d) md5=%s"
                  % (new_id, row["version_level"], deleted, md5))
        return new_id, row["version_level"], md5
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="actually write (default: dry run)")
    args = ap.parse_args()

    if not DB["password"]:
        sys.exit("PGPASSWORD is not set. Export it for this shell; never hardcode it here.")
    if not os.path.exists(HTML):
        sys.exit("dashboard not found: %s" % HTML)

    html = open(HTML, encoding="utf-8").read()
    md5 = hashlib.md5(html.encode("utf-8")).hexdigest()

    conn = connect()
    try:
        with conn.cursor() as cur:
            row = build_row()
            existing = preflight(cur, row["task_id"], row["assigned_user"],
                                 row["assigned_user_team"])

            print()
            print("=" * 78)
            print("ROW TO BE WRITTEN")
            print("=" * 78)
            for k, v in row.items():
                v = str(v)
                print("  %-19s %s" % (k, v if len(v) <= 92 else v[:89] + "..."))
            print("  %-19s %d bytes (%.1f KB), md5 %s" % ("html_content", len(html),
                                                          len(html) / 1024, md5))
            print()

            if not args.commit:
                print("DRY RUN — nothing written. Re-run with --commit to publish.")
                if existing:
                    print("NOTE: %d existing row(s) on this task_id would be DELETED and replaced."
                          % len(existing))
                return

            # one transaction: delete-by-task_id then insert. No ON CONFLICT — no unique exists.
            with conn:
                with conn.cursor() as c2:
                    c2.execute("DELETE FROM tech_team_outputs.ph_task WHERE task_id=%s",
                               (row["task_id"],))
                    deleted = c2.rowcount
                    cols = list(row) + ["html_content"]
                    c2.execute(
                        "INSERT INTO tech_team_outputs.ph_task (%s) VALUES (%s) RETURNING id"
                        % (", ".join(cols), ", ".join(["%s"] * len(cols))),
                        [row[k] for k in row] + [html])
                    new_id = c2.fetchone()[0]
            print("COMMITTED — deleted %d, inserted id %d" % (deleted, new_id))

        # independent re-read on a fresh cursor
        with conn.cursor() as cur:
            cur.execute("SELECT id, project_code, task_id, assigned_user, assigned_user_team, "
                        "version_status, LENGTH(html_content), MD5(html_content) "
                        "FROM tech_team_outputs.ph_task WHERE task_id=%s", (IDENTITY["task_id"],))
            for r in cur.fetchall():
                print("VERIFIED id=%s code=%s user=%s team=%s status=%s bytes=%s md5=%s"
                      % (r[0], r[1], r[3], r[4], r[5], r[6], r[7]))
                print("  md5 matches the file: %s" % ("YES" if r[7] == md5 else "*** NO ***"))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
