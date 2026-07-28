@echo off
REM Copy to eppr_secrets.bat (git-ignored) and fill in the two passwords — OR rely on the
REM machine's shared global env store (05_documentation/capability/shared_db_credentials/).
set "LED_PGHOST=207.148.78.148"
set "LED_PGPORT=5432"
set "LED_PGDATABASE=ledsone"
set "LED_PGUSER=dbhub_readonly"
set "LED_PGPASSWORD=__fill_me__"
set "PGHOST=149.28.134.54"
set "PGPORT=5435"
set "PGDATABASE=order_management_copy"
set "PGUSER=temp_user"
set "PGPASSWORD=__fill_me__"
