@echo off
REM ==== EPC credentials ====
REM Fill these in, then SAVE THIS FILE AS:  epc_secrets.bat   (that name is git-ignored)
REM The real passwords never get committed.

REM --- ledsone (READ: the live eBay / Amazon / Shopify prices) ---
set "LED_PGHOST="
set "LED_PGPORT=5432"
set "LED_PGDATABASE=ledsone"
set "LED_PGUSER="
set "LED_PGPASSWORD="

REM --- warehouse (WRITE: ph_task only). Host/user come from run_epc_weekly.bat. ---
set "PGPASSWORD="
