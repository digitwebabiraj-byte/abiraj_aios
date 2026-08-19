@echo off
REM Copy to bgct_secrets.bat (git-ignored) and fill in the password - OR rely on the machine's
REM shared global env store (05_documentation/capability/shared_db_credentials/).
REM BGCT reads the WAREHOUSE only; there is no ledsone-raw connection in this project.
set "PGHOST=149.28.134.54"
set "PGPORT=5435"
set "PGDATABASE=order_management_copy"
set "PGUSER=temp_user"
set "PGPASSWORD=__fill_me__"
