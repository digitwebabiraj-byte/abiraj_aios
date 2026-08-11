@echo off
REM ==== SMP credentials — copy to smp_secrets.bat and fill in; it is git-ignored ====
REM RAW ledsone (DATA source, read-only) — live host after the 2026-07-29 migration.
set "LED_PGHOST=169.58.91.229"
set "LED_PGPORT=5432"
set "LED_PGDATABASE=ledsone"
set "LED_PGUSER=dev_user"
set "LED_PGPASSWORD="
REM Portal publish (temp_user @ order_management_copy) — refreshes ph_task id 735 each run.
REM Leave PGPASSWORD blank to REFRESH OUTPUTS ONLY (no portal update).
set "PGHOST=149.28.134.54"
set "PGPORT=5435"
set "PGDATABASE=order_management_copy"
set "PGUSER=temp_user"
set "PGPASSWORD="
