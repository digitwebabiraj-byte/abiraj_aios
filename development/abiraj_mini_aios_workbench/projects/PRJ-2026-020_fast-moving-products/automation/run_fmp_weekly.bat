@echo off
REM FMP weekly runner — sources git-ignored secrets, then runs the fail-closed pipeline.
setlocal
cd /d "%~dp0"
if not exist "fmp_secrets.bat" (
  echo [FMP] fmp_secrets.bat missing - copy fmp_secrets.template.bat and fill it in. >> fmp_status.txt
  exit /b 1
)
call "fmp_secrets.bat"
python "fmp_weekly_run.py" >> "fmp_run.log" 2>&1
exit /b %errorlevel%
