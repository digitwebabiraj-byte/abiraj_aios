@echo off
REM Thuwaraga Products merge monthly run — refresh live (T7 + SMAW) -> build -> publish to Thuwaraga.
REM Credentials from the GLOBAL user environment (PGPASSWORD); non-secret warehouse defaults below.
setlocal
cd /d "%~dp0"
if not defined PGHOST     set "PGHOST=149.28.134.54"
if not defined PGPORT     set "PGPORT=5435"
if not defined PGDATABASE set "PGDATABASE=order_management_copy"
if not defined PGUSER     set "PGUSER=temp_user"
python "%~dp0merge_thuwaraga_run.py" %* >> "%~dp0merge_thuwaraga_run.log" 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [MERGE-THU] run FAILED with exit code %RC% - see merge_thuwaraga_run.log >&2
exit /b %RC%
