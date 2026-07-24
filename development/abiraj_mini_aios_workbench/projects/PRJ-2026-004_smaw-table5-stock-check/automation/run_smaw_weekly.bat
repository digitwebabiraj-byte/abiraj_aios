@echo off
setlocal
REM ==== SMAW weekly auto-refresh (Thuwaraga Table 5 stock) - Mondays, headless, no MCP ====
cd /d "%~dp0"
if exist "smaw_secrets.bat" call "smaw_secrets.bat"
if not defined PGHOST     set "PGHOST=149.28.134.54"
if not defined PGPORT     set "PGPORT=5435"
if not defined PGDATABASE set "PGDATABASE=order_management_copy"
if not defined PGUSER     set "PGUSER=temp_user"
REM No password default: if PGPASSWORD is unset the run ABORTS before writing.

python "%~dp0smaw_weekly_run.py" %* >> "%~dp0smaw_run.log" 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see smaw_run.log >> "%~dp0smaw_status.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0smaw_alert.ps1" -Rc %RC%
endlocal & exit /b %RC%
