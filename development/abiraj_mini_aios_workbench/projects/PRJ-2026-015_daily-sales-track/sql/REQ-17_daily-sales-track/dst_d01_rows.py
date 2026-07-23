# -*- coding: utf-8 -*-
"""
REQ-17-D01 governed dataset — one row per eBay ACCOUNT x MARKETPLACE.

Retrieved read-only on 2026-07-23 from the raw `ledsone` Postgres via the Ledsone DB MCP
(https://mcp.ledsone.co.uk/mcp). The exact SQL is recorded in build_dst_d01.py SQL_USED.

GRAIN CHANGED 2026-07-23 (decision F reversed on the owner's instruction): the report was one row
per account; a Seller Hub check showed LEDSone UK at GBP 837.93 for 22 Jul while the account row
read GBP 1,144.51. Both were right - the account row combined UK (837.93) and Germany (306.58).
Seller Hub reports per marketplace, so the report now does too and every row ties to one Seller Hub
screen.

Universe: every account x site with live listings (all_list=1, is_ended=0) = 30 rows.
Reconciles to the account-grain build: sales 2,983.35 / orders 142 / units 223 identical.
Active listings 14,606 here vs 14,607 at account grain - exactly one live listing carries a NULL
site and cannot be placed in a marketplace; it is excluded and disclosed.

UNASSIGNED marks an account x marketplace with no named account holder.
"""

UNASSIGNED = "— not assigned"

ROWS = [
    {"key": "led_sone", "site": "UK", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 837.93, "s_r2": 863.36, "s_ly": 1233.51, "o_r1": 42, "o_r2": 49, "o_ly": 78,
     "units_r1": 70, "ph_r1": 394.11, "ah_r1": 436.24, "ph_r2": 534.77, "ah_r2": 336.33,
     "active": 2843, "ph_l": 1245, "ah_l": 1598},
    {"key": "electricalsone", "site": "UK", "display": "ElectricalSone UK", "holder": "Kobiga",
     "s_r1": 397.95, "s_r2": 444.60, "s_ly": 497.19, "o_r1": 21, "o_r2": 28, "o_ly": 34,
     "units_r1": 35, "ph_r1": 223.86, "ah_r1": 197.77, "ph_r2": 292.81, "ah_r2": 166.19,
     "active": 1513, "ph_l": 548, "ah_l": 965},
    {"key": "led_sone", "site": "Germany", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 306.58, "s_r2": 61.33, "s_ly": 534.56, "o_r1": 6, "o_r2": 4, "o_ly": 22,
     "units_r1": 11, "ph_r1": 0.00, "ah_r1": 298.23, "ph_r2": 7.41, "ah_r2": 33.65,
     "active": 1353, "ph_l": 214, "ah_l": 1139},
    {"key": "so_926407", "site": "UK", "display": "Sunsone", "holder": "Powsteena",
     "s_r1": 261.26, "s_r2": 198.00, "s_ly": 259.76, "o_r1": 14, "o_r2": 10, "o_ly": 13,
     "units_r1": 21, "ph_r1": 70.21, "ah_r1": 201.28, "ph_r2": 53.83, "ah_r2": 146.10,
     "active": 1150, "ph_l": 457, "ah_l": 693},
    {"key": "ledsonede", "site": "Germany", "display": "LEDSone DE", "holder": "Jarsini",
     "s_r1": 149.50, "s_r2": 241.79, "s_ly": 212.66, "o_r1": 11, "o_r2": 10, "o_ly": 11,
     "units_r1": 11, "ph_r1": 7.19, "ah_r1": 133.07, "ph_r2": 30.07, "ah_r2": 208.41,
     "active": 634, "ph_l": 82, "ah_l": 552},
    {"key": "led_sone", "site": "Ireland", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 0.00, "s_r2": 5.81, "s_ly": 0.00, "o_r1": 0, "o_r2": 1, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 5.81,
     "active": 622, "ph_l": 0, "ah_l": 622},
    {"key": "led_sone", "site": "Austria", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 592, "ph_l": 0, "ah_l": 592},
    {"key": "huettenlampen", "site": "Germany", "display": "Huetten Lampen DE", "holder": "Jarsini",
     "s_r1": 397.19, "s_r2": 256.76, "s_ly": 394.90, "o_r1": 19, "o_r2": 11, "o_ly": 23,
     "units_r1": 22, "ph_r1": 33.38, "ah_r1": 379.38, "ph_r2": 60.27, "ah_r2": 201.27,
     "active": 541, "ph_l": 92, "ah_l": 449},
    {"key": "coventrylights", "site": "UK", "display": "Coventry Lights", "holder": "Genga",
     "s_r1": 202.68, "s_r2": 280.92, "s_ly": 113.61, "o_r1": 8, "o_r2": 15, "o_ly": 5,
     "units_r1": 10, "ph_r1": 0.00, "ah_r1": 202.68, "ph_r2": 0.00, "ah_r2": 271.95,
     "active": 537, "ph_l": 0, "ah_l": 537},
    {"key": "electricalsone", "site": "Germany", "display": "ElectricalSone UK", "holder": "Kobiga",
     "s_r1": 45.48, "s_r2": 159.54, "s_ly": 105.46, "o_r1": 4, "o_r2": 9, "o_ly": 6,
     "units_r1": 5, "ph_r1": 6.70, "ah_r1": 26.57, "ph_r2": 0.00, "ah_r2": 138.84,
     "active": 486, "ph_l": 36, "ah_l": 450},
    {"key": "vintageinterior", "site": "UK", "display": "Vintage Interior", "holder": UNASSIGNED,
     "s_r1": 157.59, "s_r2": 75.78, "s_ly": 82.87, "o_r1": 8, "o_r2": 8, "o_ly": 10,
     "units_r1": 14, "ph_r1": 0.00, "ah_r1": 166.07, "ph_r2": 0.00, "ah_r2": 77.10,
     "active": 474, "ph_l": 0, "ah_l": 474},
    {"key": "dctransformer", "site": "UK", "display": "DC Transformer", "holder": UNASSIGNED,
     "s_r1": 41.99, "s_r2": 57.70, "s_ly": 27.34, "o_r1": 4, "o_r2": 2, "o_ly": 3,
     "units_r1": 13, "ph_r1": 0.00, "ah_r1": 45.43, "ph_r2": 0.00, "ah_r2": 60.76,
     "active": 468, "ph_l": 0, "ah_l": 468},
    {"key": "re6865", "site": "UK", "display": "Retro LED", "holder": UNASSIGNED,
     "s_r1": 0.00, "s_r2": 65.78, "s_ly": 314.72, "o_r1": 0, "o_r2": 2, "o_ly": 6,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 68.78,
     "active": 403, "ph_l": 0, "ah_l": 403},
    {"key": "led_sone", "site": "US", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 391, "ph_l": 38, "ah_l": 353},
    {"key": "electricalsone", "site": "US", "display": "ElectricalSone UK", "holder": "Kobiga",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 380, "ph_l": 3, "ah_l": 377},
    {"key": "led_sone", "site": "France", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 0.00, "s_r2": 26.33, "s_ly": 0.00, "o_r1": 0, "o_r2": 1, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 9.08,
     "active": 368, "ph_l": 0, "ah_l": 368},
    {"key": "neighbourmarket", "site": "US", "display": "Neighbour Market", "holder": UNASSIGNED,
     "s_r1": 0.00, "s_r2": 29.62, "s_ly": 0.00, "o_r1": 0, "o_r2": 1, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 26.99,
     "active": 344, "ph_l": 16, "ah_l": 328},
    {"key": "so_926407", "site": "Germany", "display": "Sunsone", "holder": "Sivajitha",
     "s_r1": 32.29, "s_r2": 78.15, "s_ly": 152.48, "o_r1": 2, "o_r2": 4, "o_ly": 12,
     "units_r1": 2, "ph_r1": 0.00, "ah_r1": 28.84, "ph_r2": 0.00, "ah_r2": 68.09,
     "active": 295, "ph_l": 0, "ah_l": 295},
    {"key": "lighting_sone", "site": "UK", "display": "Lighting Sone", "holder": UNASSIGNED,
     "s_r1": 0.00, "s_r2": 16.58, "s_ly": 0.00, "o_r1": 0, "o_r2": 1, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 16.58,
     "active": 247, "ph_l": 0, "ah_l": 247},
    {"key": "led_sone", "site": "Canada", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 184, "ph_l": 0, "ah_l": 184},
    {"key": "electricalsone", "site": "France", "display": "ElectricalSone UK", "holder": "Kobiga",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 167, "ph_l": 19, "ah_l": 148},
    {"key": "homin_gmbh", "site": "Germany", "display": "Homin GmbH", "holder": UNASSIGNED,
     "s_r1": 152.91, "s_r2": 28.98, "s_ly": 0.00, "o_r1": 3, "o_r2": 2, "o_ly": 0,
     "units_r1": 9, "ph_r1": 0.00, "ah_r1": 157.69, "ph_r2": 0.00, "ah_r2": 28.98,
     "active": 164, "ph_l": 0, "ah_l": 164},
    {"key": "electricalsone", "site": "Canada", "display": "ElectricalSone UK", "holder": "Kobiga",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 154, "ph_l": 0, "ah_l": 154},
    {"key": "led_sone", "site": "Italy", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 137, "ph_l": 0, "ah_l": 137},
    {"key": "so_926407", "site": "France", "display": "Sunsone", "holder": UNASSIGNED,
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 70, "ph_l": 0, "ah_l": 70},
    {"key": "bestbringer", "site": "UK", "display": "Bestbringer", "holder": UNASSIGNED,
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 65, "ph_l": 0, "ah_l": 65},
    {"key": "led_sone", "site": "Spain", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 14, "ph_l": 0, "ah_l": 14},
    {"key": "led_sone", "site": "Netherlands", "display": "LEDSone UK", "holder": "Sharmilan",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 6, "ph_l": 0, "ah_l": 6},
    {"key": "huettenlampen", "site": "Italy", "display": "Huetten Lampen DE", "holder": "Jarsini",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 2, "ph_l": 0, "ah_l": 2},
    {"key": "ledsonede", "site": "UK", "display": "LEDSone DE", "holder": "Jarsini",
     "s_r1": 0.00, "s_r2": 0.00, "s_ly": 0.00, "o_r1": 0, "o_r2": 0, "o_ly": 0,
     "units_r1": 0, "ph_r1": 0.00, "ah_r1": 0.00, "ph_r2": 0.00, "ah_r2": 0.00,
     "active": 2, "ph_l": 0, "ah_l": 2},
]

# ---------------------------------------------------------------------------
# CURRENCY. Added 2026-07-23 after a defect: `order_management.orders.total` is
# stored in the MARKETPLACE'S OWN currency, not GBP. Confirmed by joining
# order_management.order_info.currency, which matches amount_paid exactly:
# on 22 Jul the UK rows are GBP 1,899.40 and the German rows EUR 1,083.95.
# The first build rendered every figure with a GBP sign and summed them, which
# made all cross-row totals meaningless.
#
# Source of truth: listings.market_place_id_mapping (verified 2026-07-23).
# Currency is 1:1 with marketplace - no order mixes currencies within a site.
# There is NO exchange-rate table anywhere in ledsone, so nothing is converted;
# totals are reported per currency instead.
# ---------------------------------------------------------------------------
SITE_CURRENCY = {
    "UK": "GBP",
    "Germany": "EUR", "France": "EUR", "Ireland": "EUR", "Austria": "EUR",
    "Italy": "EUR", "Spain": "EUR", "Netherlands": "EUR", "Belgium": "EUR",
    "US": "USD", "Canada": "CAD",
}
CURRENCY_SYMBOL = {"GBP": "£", "EUR": "€", "USD": "$", "CAD": "CA$"}

for _r in ROWS:
    _r["currency"] = SITE_CURRENCY[_r["site"]]

# ---------------------------------------------------------------------------
# Maps the daily run (REQ-17-D02) needs to rebuild ROWS from live SQL, kept here
# so the scheduled job and the one-off build share exactly one definition.
# ---------------------------------------------------------------------------
DISPLAY = {
    "led_sone": "LEDSone UK", "electricalsone": "ElectricalSone UK",
    "so_926407": "Sunsone", "ledsonede": "LEDSone DE",
    "huettenlampen": "Huetten Lampen DE", "coventrylights": "Coventry Lights",
    "vintageinterior": "Vintage Interior", "dctransformer": "DC Transformer",
    "re6865": "Retro LED", "neighbourmarket": "Neighbour Market",
    "lighting_sone": "Lighting Sone", "homin_gmbh": "Homin GmbH",
    "bestbringer": "Bestbringer",
}

# AH holder is a MANUAL map - no database records who owns an account. Supplied by
# Thinesh 2026-07-23. Sunsone is ONE eBay account selling into both UK and Germany,
# so it is the only one split by marketplace. "Jarshini" matched nobody in
# staff.users (which holds Jarsini id 91 AND Jasmini id 84); Thinesh confirmed Jarsini.
HOLDER_SITE = {("so_926407", "UK"): "Powsteena", ("so_926407", "Germany"): "Sivajitha"}
HOLDER_ACCT = {
    "led_sone": "Sharmilan", "electricalsone": "Kobiga", "coventrylights": "Genga",
    "huettenlampen": "Jarsini", "ledsonede": "Jarsini",
}
