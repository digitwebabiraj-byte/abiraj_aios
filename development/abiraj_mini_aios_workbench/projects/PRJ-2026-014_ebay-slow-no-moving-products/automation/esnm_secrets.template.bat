@echo off
REM ==== ESNM credentials - copy to esnm_secrets.bat and fill in; that copy is git-ignored ====
REM Normally you do NOT need this file: the global credential store already provides both
REM connections (05_documentation/capability/shared_db_credentials/). Use it only as an override.
REM
REM ledsone = listings, sales, PPC (read-only).
set "LED_PGHOST=207.148.78.148"
set "LED_PGPORT=5432"
set "LED_PGDATABASE=ledsone"
set "LED_PGUSER=dbhub_readonly"
set "LED_PGPASSWORD="
REM warehouse = eBay organic traffic (views/conversion) AND the ph_task publish target.
set "PGPASSWORD="
