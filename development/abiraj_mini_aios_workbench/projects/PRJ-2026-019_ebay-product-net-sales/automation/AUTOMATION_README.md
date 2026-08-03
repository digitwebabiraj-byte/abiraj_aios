# EPNS automation — REQ-22-D02

Weekly refresh of the eBay Product Net Sales report, published to `ph_task` for the **ebay_priors**
audience (6 users). Mirrors the fleet's fail-closed pattern (EPPR/DST).

| Field | Value |
|---|---|
| Windows task | **`EPNS_Weekly_Net_Sales`** |
| Schedule | **Every Wednesday 11:30** (free slot — fleet occupies 09:00–11:00) |
| Runner | `run_epns_weekly.bat` → `epns_weekly_run.py` |
| Data source | LIVE ledsone `169.58.91.229` (`dev_user`), read-only, direct psycopg2 |
| Publish target | warehouse `order_management_copy` @ `149.28.134.54:5435` (`temp_user`), `tech_team_outputs.ph_task` |
| Secrets | `epns_secrets.bat` (git-ignored; copy from `epns_secrets.template.bat`) |
| Status / log | `epns_status.txt`, `epns_run.log`, `epns_last_good.json` |

## Fail-closed gates (no bad publish)
- **Row floor:** refuse if < 1,500 settled orders (healthy ≈ 4,000).
- **Collapse guard:** refuse if < 60% of the last good run's row count.
- Any error → status file `FAIL` + Desktop alert; nothing is published.
- Publish is a guarded per-user upsert and **always sets `assigned_user_team='ebay_priors'`**
  (the column the portal filters on — omitting it makes rows invisible).

## Install
```
copy epns_secrets.template.bat epns_secrets.bat   :: then fill in the two passwords
powershell -ExecutionPolicy Bypass -File register_epns_task.ps1
```

## Method (locked)
- **NNV = Gross − Final Value Fee − General(AD_FEE)** — ties to eBay's per-order payout.
- General = Promoted Listings "General" fee (`AD_FEE`, per order). PPC = `PREMIUM_AD_FEES` (CPC, listing-allocated).
- Settled-only (order has SALE fees booked). Money per marketplace currency, never blended.
- VAT (20%) and Product Cost (20% proxy) are estimates; Net Profit = NNV − VAT − Product Cost − PPC.
