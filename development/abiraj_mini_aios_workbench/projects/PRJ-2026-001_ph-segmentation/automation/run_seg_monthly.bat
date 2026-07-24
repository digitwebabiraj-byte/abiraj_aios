@echo off
setlocal
REM ==== PH ASIN Segmentation - monthly auto refresh (3rd, 09:00) - headless, no MCP, no human ====
REM Credentials resolve in this order (same as PRJ-2026-010/011/012/013/014):
REM   1. seg_secrets.bat next to this file (optional, git-ignored)  - per-project override
REM   2. GLOBAL user environment variables                          - the normal case
REM      set up once via 05_documentation/capability/shared_db_credentials/
REM   3. the non-secret defaults below (host/port/db/user only - never a password)
cd /d "%~dp0"
if exist "seg_secrets.bat" call "seg_secrets.bat"
if not defined PGHOST     set "PGHOST=149.28.134.54"
if not defined PGPORT     set "PGPORT=5435"
if not defined PGDATABASE set "PGDATABASE=order_management_copy"
if not defined PGUSER     set "PGUSER=temp_user"
REM No password default anywhere: if PGPASSWORD is unset the run ABORTS before writing.

python "%~dp0seg_monthly_run.py" %* >> "%~dp0seg_run.log" 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see seg_run.log >> "%~dp0seg_status.txt"
REM ---- Desktop alert on failure / auto-clear on success ----
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0seg_alert.ps1" -Rc %RC%
endlocal & exit /b %RC%
