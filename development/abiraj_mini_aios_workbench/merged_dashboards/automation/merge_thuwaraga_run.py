# -*- coding: utf-8 -*-
"""
Thuwaraga Products merge — live monthly run (T7 + SMAW, Thuwaraga), UNIFIED-TABLE model.
Each tab shows that task's own rows/columns in ONE consistent merged UI (shared search/sort/
filter). Reuses each task's OWN build (live WAREHOUSE pull, NO publish) to produce fresh data,
reads it via the emitters (T7 reproduces its signed-off 13-col xlsx report; SMAW its 13-col
table), builds the dashboard, republishes the thuwaraga rows. Both use the warehouse (5435) —
no PGPORT stripping. Task folders restored via git checkout.

  python merge_thuwaraga_run.py            # real run
  python merge_thuwaraga_run.py --dry-run  # build fresh data + dashboard, skip publish
"""
import os, sys, json, subprocess, tempfile, hashlib, logging, datetime
import psycopg2

HERE = os.path.dirname(os.path.abspath(__file__))
MERGE_DIR = os.path.abspath(os.path.join(HERE, ".."))
EMIT_DIR = os.path.join(MERGE_DIR, "emitters")
PROJECTS = os.path.abspath(os.path.join(MERGE_DIR, "..", "projects"))
STATUS = os.path.join(HERE, "merge_thuwaraga_status.txt")
DRY = "--dry-run" in sys.argv
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-7s %(message)s")
log = logging.getLogger("merge-thu").info

T7_PROJ = os.path.join(PROJECTS, "PRJ-2026-005_weekly-sku-performance-check")
T7_SQL = os.path.join(T7_PROJ, "sql", "T7_weekly-sku-performance-check", "generate_dataset.sql")
SMAW_PROJ = os.path.join(PROJECTS, "PRJ-2026-004_smaw-table5-stock-check")
SMAW_RUN_DIR = os.path.join(SMAW_PROJ, "automation")
SMAW_JSON = os.path.join(SMAW_RUN_DIR, "smaw_data_all.json")
MIN_T7, MIN_SMAW = 300, 100


def die(msg):
    logging.getLogger("merge-thu").error("ABORT: %s", msg)
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("FAIL %s\n%s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), msg))
    sys.exit(1)


def run_build(name, script_dir, script, args=None):
    import time
    for attempt in (1, 2, 3):
        log("%s: running its live build (%s), attempt %d…" % (name, script, attempt))
        r = subprocess.run([sys.executable, os.path.join(script_dir, script)] + (args or []),
                           cwd=script_dir, capture_output=True, text=True)
        if r.returncode == 0:
            return
        log("  %s attempt %d failed: %s" % (name, attempt, (r.stderr or r.stdout).strip()[-200:]))
        if attempt < 3:
            time.sleep(20 * attempt)
    die("%s build failed after 3 attempts" % name)


def run_emitter(script, src_env, src_path):
    env = dict(os.environ); env[src_env] = src_path
    r = subprocess.run([sys.executable, os.path.join(EMIT_DIR, script)],
                       cwd=EMIT_DIR, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        die("emitter %s failed: %s" % (script, (r.stderr or r.stdout)[-400:]))
    log("emitter %s ok: %s" % (script, (r.stdout or "").strip().splitlines()[-1] if r.stdout else ""))
    return json.load(open(os.path.join(EMIT_DIR, script.replace("_emit.py", "_merge.json")), encoding="utf-8"))


def restore(proj_dirs):
    for d in proj_dirs:
        try:
            subprocess.run(["git", "checkout", "--", d], cwd=PROJECTS, capture_output=True, text=True)
        except Exception:
            pass


def fetch_t7(workdir):
    # Reuse T7's OWN canonical query (its runner never persists data.json) against the warehouse
    # read-only, write a fresh data.json into the workdir. Does NOT touch the T7 task.
    log("T7: live pull via its canonical generate_dataset.sql…")
    sql = open(T7_SQL, encoding="utf-8").read()
    conn = psycopg2.connect(host=os.getenv("PGHOST", "149.28.134.54"), port=os.getenv("PGPORT", "5435"),
                            dbname=os.getenv("PGDATABASE", "order_management_copy"),
                            user=os.getenv("PGUSER", "temp_user"), password=os.getenv("PGPASSWORD"),
                            connect_timeout=20)
    conn.set_session(readonly=True)
    cur = conn.cursor()
    cur.execute("SELECT (CURRENT_DATE - 7)::date, (CURRENT_DATE - 1)::date")
    ws, we = cur.fetchone()
    cur.execute(sql, {"ws": ws, "we": we})
    cols = [d[0] for d in cur.description]
    raw = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    rows = [{"s": r.get("sku"), "r": r.get("ref_id"), "p": r.get("platform"), "a": r.get("account"),
             "b": r.get("base_sku"), "m": int(r.get("mapped_flag") or 0), "o": int(r.get("orders") or 0)}
            for r in raw]
    names = {r["sku"]: r.get("product_name") for r in raw if r.get("sku")}
    data = {"meta": {"run_date": str(we), "week_start": str(ws), "week_end": str(we)},
            "names": names, "rows": rows}
    path = os.path.join(workdir, "t7_data.json")
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    return path


def main():
    log("=== thuwaraga merge run start (dry_run=%s) ===" % DRY)
    work = tempfile.mkdtemp(prefix="thu_")
    try:
        t7_json = fetch_t7(work)
        run_build("SMAW", SMAW_RUN_DIR, "smaw_weekly_run.py", ["--dry-run"])

        t7 = run_emitter("t7_emit.py", "T7_SRC", t7_json)
        smaw = run_emitter("smaw_emit.py", "SMAW_SRC", SMAW_JSON)
        if len(t7["rows"]) < MIN_T7:
            die("T7 only %d rows (< %d)" % (len(t7["rows"]), MIN_T7))
        if len(smaw["rows"]) < MIN_SMAW:
            die("SMAW only %d rows (< %d)" % (len(smaw["rows"]), MIN_SMAW))
        log("fresh data: T7 %d · SMAW %d" % (len(t7["rows"]), len(smaw["rows"])))
    finally:
        restore([SMAW_PROJ])
        import shutil; shutil.rmtree(work, ignore_errors=True)

    r = subprocess.run([sys.executable, os.path.join(MERGE_DIR, "build_merged.py"),
                        os.path.join(MERGE_DIR, "registry_thuwaraga.json")],
                       cwd=MERGE_DIR, capture_output=True, text=True)
    if r.returncode != 0:
        die("build_merged failed: %s" % (r.stderr or r.stdout)[-400:])
    html = os.path.join(MERGE_DIR, "thuwaraga_t7_smaw", "merged_thuwaraga_dashboard.html")
    if not os.path.exists(html) or os.path.getsize(html) < 200_000:
        die("built HTML missing or too small")
    md5 = hashlib.md5(open(html, "rb").read()).hexdigest()[:10]

    if DRY:
        log("DRY-RUN: dashboard built (md5 %s), skipped publish." % md5)
    elif os.environ.get("PGPASSWORD"):
        pub = subprocess.run([sys.executable, os.path.join(HERE, "publish_thuwaraga_ph_task.py"), "--refresh"],
                             cwd=HERE, capture_output=True, text=True)
        if pub.returncode != 0:
            die("portal refresh failed (build OK): %s" % (pub.stderr or pub.stdout)[-300:])
        log("portal rows refreshed: " + (pub.stdout or "").strip().splitlines()[-1])
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write("OK%s %s | md5 %s\n" % ("(dry-run)" if DRY else "",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), md5))
    log("=== thuwaraga merge run done | md5 %s ===" % md5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
