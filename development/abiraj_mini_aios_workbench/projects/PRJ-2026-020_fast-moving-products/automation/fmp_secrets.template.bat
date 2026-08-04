@echo off
REM ==== FMP credentials — copy this file to fmp_secrets.bat and fill in; it is git-ignored ====
REM RAW ledsone (DATA source, read-only) = mcp.ledsone.co.uk. Live host after the 2026-07-29 migration.
set "LED_PGHOST=169.58.91.229"
set "LED_PGPORT=5432"
set "LED_PGDATABASE=ledsone"
set "LED_PGUSER=dev_user"
set "LED_PGPASSWORD="
REM No warehouse/ph_task publish for this task yet — refresh only (held pending Mahima's audience).
