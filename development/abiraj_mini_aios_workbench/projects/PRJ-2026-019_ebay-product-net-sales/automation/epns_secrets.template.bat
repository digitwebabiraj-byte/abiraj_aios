@echo off
REM ==== EPNS credentials — copy this file to epns_secrets.bat and fill in; it is git-ignored ====
REM Live ledsone (DATA source, read-only). New host after the 2026-07-29 migration.
set "LED_PGHOST=169.58.91.229"
set "LED_PGPORT=5432"
set "LED_PGDATABASE=ledsone"
set "LED_PGUSER=dev_user"
set "LED_PGPASSWORD="
REM Warehouse temp_user (ph_task publish target, order_management_copy @ 149.28.134.54:5435).
set "WH_PGHOST=149.28.134.54"
set "WH_PGPORT=5435"
set "WH_PGDATABASE=order_management_copy"
set "WH_PGUSER=temp_user"
set "PGPASSWORD="
