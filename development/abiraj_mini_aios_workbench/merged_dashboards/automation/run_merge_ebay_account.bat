@echo off
REM Merged — eBay Account Performance monthly run — refresh live (EBPD + DST) -> build -> publish to ebay_priors.
REM Credentials from the GLOBAL user environment (PGPASSWORD warehouse + LED_* ledsone); non-secret defaults below.
setlocal
cd /d "%~dp0"
if not defined PGHOST     set "PGHOST=149.28.134.54"
if not defined PGPORT     set "PGPORT=5435"
if not defined PGDATABASE set "PGDATABASE=order_management_copy"
if not defined PGUSER     set "PGUSER=temp_user"
if not defined LED_PGPORT set "LED_PGPORT=5432"
python "%~dp0merge_ebay_account_run.py" %* >> "%~dp0merge_ebay_account_run.log" 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [MERGE-EACC] run FAILED with exit code %RC% - see merge_ebay_account_run.log >&2
exit /b %RC%
