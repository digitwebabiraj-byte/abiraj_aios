@echo off
REM ==== ERA credentials — copy this file to era_secrets.bat and fill in, then it is git-ignored ====
REM era_secrets.bat is git-ignored (see automation/.gitignore) so passwords never get committed.
REM
REM Ledsone DB = the DATA source (read-only). Server "ukvm" in pgAdmin. Same connection PRJ-2026-011 uses.
set "LED_PGHOST=207.148.78.148"
set "LED_PGPORT=5432"
set "LED_PGDATABASE=ledsone"
set "LED_PGUSER=dbhub_readonly"
set "LED_PGPASSWORD="
REM Warehouse temp_user password = the ph_task publish target (order_management_copy @ 149.28.134.54:5435).
set "PGPASSWORD="
