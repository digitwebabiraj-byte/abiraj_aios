# Evidence — logs & audits · REQ-17 Daily Sales Track

**Status: EMPTY. The Step-2 data-availability audit has not been run.**

Nothing in this project has been proven against live data. Until the audit lands here, every source
claim in `SYSTEM_REFERENCE.md` is either **inherited** from REQ-13 or **expected**, and must be read
that way.

## What must land here first

`YYYY-MM-DD_data_availability_audit.md` — read-only, both databases, answering:

1. **Does `order_transaction` support a daily grain at all?** Is `order_date` a date or a timestamp,
   and **what timezone does its day boundary fall on?** Every prior project in this workbench used a
   monthly or rolling multi-day window, so this has never needed establishing. Getting it wrong
   shifts every figure by a partial day.
2. **Is the daily series complete?** REQ-16 found the eBay traffic feed had silently lost **11 of 91
   days**. A daily report is far more sensitive than a 90-day rolling one — one lost day reads as a
   total trading halt, not a 1% understatement.
3. **How far back is the last-year comparator populated, per account?** An account live for under a
   year has no LY figure and must render **blank, never zero**.
4. 🔴 **Does an AH/PH assignment object exist in either database?** Sweep **both**, **by column name
   as well as table name** — searching only table names is the mistake that made REQ-11's first audit
   wrong ("no eBay feedback data exists anywhere" — it was live in the other database).
5. **Which `Active Listing` definition to adopt** (REQ-13's vs REQ-16's), and what the gap between
   them is today.
6. **One hand-reconciled account-day** against a figure Thinesh can verify independently in Seller
   Hub.

Output a **GREEN / AMBER / RED** verdict and a column→source Evidence Map before any build code is
written.
