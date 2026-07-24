@echo off
setlocal
REM ==== ZSFO weekly auto-refresh (Utharsika zero-sales) - Mondays, headless, no MCP, no human ====
REM Credentials resolve: seg_secrets-style local file (optional) -> GLOBAL user env vars -> non-secret defaults.
cd /d "%~dp0"
if exist "zsfo_secrets.bat" call "zsfo_secrets.bat"
if not defined PGHOST     set "PGHOST=149.28.134.54"
if not defined PGPORT     set "PGPORT=5435"
if not defined PGDATABASE set "PGDATABASE=order_management_copy"
if not defined PGUSER     set "PGUSER=temp_user"
REM No password default: if PGPASSWORD is unset the run ABORTS before writing.

python "%~dp0zsfo_weekly_run.py" %* >> "%~dp0zsfo_run.log" 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see zsfo_run.log >> "%~dp0zsfo_status.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0zsfo_alert.ps1" -Rc %RC%
endlocal & exit /b %RC%
