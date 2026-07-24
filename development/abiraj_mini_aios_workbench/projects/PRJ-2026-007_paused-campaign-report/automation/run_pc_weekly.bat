@echo off
setlocal
REM ==== PC weekly auto-refresh (Utharsika paused campaigns) - Wednesdays, headless, no MCP ====
cd /d "%~dp0"
if exist "pc_secrets.bat" call "pc_secrets.bat"
if not defined PGHOST     set "PGHOST=149.28.134.54"
if not defined PGPORT     set "PGPORT=5435"
if not defined PGDATABASE set "PGDATABASE=order_management_copy"
if not defined PGUSER     set "PGUSER=temp_user"
REM No password default: if PGPASSWORD is unset the run ABORTS before writing.

python "%~dp0pc_weekly_run.py" %* >> "%~dp0pc_run.log" 2>&1
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [%DATE% %TIME%]  FAILED (exit %RC%)  ^|  see pc_run.log >> "%~dp0pc_status.txt"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0pc_alert.ps1" -Rc %RC%
endlocal & exit /b %RC%
