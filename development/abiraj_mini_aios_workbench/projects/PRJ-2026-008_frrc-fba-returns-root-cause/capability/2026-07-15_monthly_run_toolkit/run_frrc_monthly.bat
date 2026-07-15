@echo off
REM ==========================================================================
REM  FRRC - FBA Returns Root-Cause : monthly run wrapper (Windows Task Scheduler)
REM  Fires on day 8 of each month. See README.md.
REM  Requires the user env var FRRC_PGPASSWORD (set once - see README).
REM ==========================================================================
setlocal
cd /d "%~dp0"
if "%FRRC_PGPASSWORD%"=="" (
  echo [FRRC] ERROR: FRRC_PGPASSWORD is not set. Run set_credential.ps1 once. >&2
  exit /b 1
)
python "%~dp0run_frrc_monthly.py" %*
set RC=%ERRORLEVEL%
if not "%RC%"=="0" echo [FRRC] run FAILED with exit code %RC% - see logs\ >&2
exit /b %RC%
