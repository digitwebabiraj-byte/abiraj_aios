# -*- coding: utf-8 -*-
"""Verify the GLOBAL database credentials work. Prints OK/FAIL only - never a password."""
import os, sys
try:
    import psycopg2
except ImportError:
    sys.exit("psycopg2 not installed.  pip install psycopg2-binary")

def check(label, cfg, need):
    missing = [k for k in need if not cfg.get(k)]
    if missing:
        print("  FAIL  %-10s missing env var(s): %s" % (label, ", ".join(missing))); return False
    try:
        c = psycopg2.connect(connect_timeout=15, **cfg)
        with c.cursor() as cur:
            cur.execute("SELECT current_database(), current_user, inet_server_addr()::text, inet_server_port()")
            db, usr, addr, port = cur.fetchone()
        c.close()
        print("  OK    %-10s %s@%s:%s  db=%s" % (label, usr, addr, port, db)); return True
    except Exception as e:
        print("  FAIL  %-10s %s" % (label, str(e).strip().splitlines()[0])); return False

led = dict(host=os.getenv("LED_PGHOST"), port=os.getenv("LED_PGPORT","5432"),
           dbname=os.getenv("LED_PGDATABASE"), user=os.getenv("LED_PGUSER"),
           password=os.getenv("LED_PGPASSWORD"))
wh  = dict(host=os.getenv("PGHOST","149.28.134.54"), port=os.getenv("PGPORT","5435"),
           dbname=os.getenv("PGDATABASE","order_management_copy"),
           user=os.getenv("PGUSER","temp_user"), password=os.getenv("PGPASSWORD"))

print("Global credential check (values are never printed):")
a = check("ledsone",  led, ["host","dbname","user","password"])
b = check("warehouse", wh, ["host","dbname","user","password"])
print("\nRESULT:", "both connections OK - every project can now run unattended."
      if (a and b) else "at least one FAILED - fix before scheduling any automation.")
sys.exit(0 if (a and b) else 1)
