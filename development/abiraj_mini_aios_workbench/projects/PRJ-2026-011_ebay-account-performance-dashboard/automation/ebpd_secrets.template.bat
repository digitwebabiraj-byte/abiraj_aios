@echo off
REM ==== EBPD ledsone (New Listings) credentials ====
REM Fill these with the ledsone Postgres connection you have, then SAVE THIS FILE AS: ebpd_secrets.bat
REM (ebpd_secrets.bat is git-ignored — the real passwords never get committed.)
set "LED_PGHOST="
set "LED_PGPORT=5432"
set "LED_PGDATABASE="
set "LED_PGUSER="
set "LED_PGPASSWORD="
REM Optional: override the warehouse creds here too if you prefer not to keep them in run_ebpd_weekly.bat.
REM set "PGPASSWORD="
