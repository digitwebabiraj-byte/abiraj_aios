@echo off
REM REQ-15-D02 — weekly Monday refresh of the eBay PPC Pause Automation report.
REM Loads credentials from the git-ignored eppa_secrets.bat, then runs the Python job.
setlocal
cd /d "%~dp0"

if not exist "eppa_secrets.bat" (
  echo [EPPA] eppa_secrets.bat not found. Copy eppa_secrets.template.bat to eppa_secrets.bat and fill it in.
  exit /b 2
)
call "eppa_secrets.bat"

python "eppa_weekly_run.py" %*
set RC=%ERRORLEVEL%

if not "%RC%"=="0" (
  echo [EPPA] run FAILED with code %RC% - raising desktop alert
  powershell -NoProfile -ExecutionPolicy Bypass -File "eppa_alert.ps1"
)

REM Clear the credentials from this shell's environment.
set "LED_PGPASSWORD="
exit /b %RC%
