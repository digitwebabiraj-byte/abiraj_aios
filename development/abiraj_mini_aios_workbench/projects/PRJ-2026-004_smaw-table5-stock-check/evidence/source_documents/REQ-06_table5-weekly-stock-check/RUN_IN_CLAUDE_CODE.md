# Generate the complete Table 5 HTML (all ~733 ASINs) — Claude Code steps

Files needed (in this folder): `generate_dataset_all_asins.sql`, `build_all.py`

## 1) Connect the database (once)
    claude mcp add --transport http postgres https://mcp.vintageinterior.co.uk/mcp
    # inside Claude Code:
    /mcp        # confirm "postgres" is connected

## 2) One prompt to Claude Code (paste this):
Use the postgres MCP (database order_management_copy, read-only). Run the query in
generate_dataset_all_asins.sql exactly as written. It returns one row per (ASIN, account).
Collect ALL rows (page through if the connector limits rows) into a single JSON array and
save it as data_all.json in this folder. Then run:
    pip install openpyxl --break-system-packages
    python build_all.py
This reads data_all.json and writes:
    Table5_Weekly_Stock_Check_Thuwaraga_ALL.html   <- the HTML you want
    Table5_Weekly_Stock_Check_Thuwaraga_ALL.xlsx
Then tell me the row count and the status breakdown, and confirm LDSSTRE274 = 990 and
LDMA60E274 = 0.

## Expected result (verified against live data today)
- ~733 rows total (a strict superset of the 240 sellers — nothing dropped)
- 240 with sales (velocity + days filled)
- ~493 idle stock (stock shown, velocity/days blank, grey "No Recent Sales" flag)
- 8 real critical stockouts (top of the list, red)

## To reproduce a specific date (e.g. 2026-07-08)
In generate_dataset_all_asins.sql change:  SELECT CURRENT_DATE AS d   ->   SELECT DATE '2026-07-08' AS d
