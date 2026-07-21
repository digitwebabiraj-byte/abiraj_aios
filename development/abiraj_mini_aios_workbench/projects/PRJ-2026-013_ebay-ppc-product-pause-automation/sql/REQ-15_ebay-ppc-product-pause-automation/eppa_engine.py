"""
REQ-15 — the pause rule engine. Single source of truth for the weekly run and any manual rebuild.

This is the source HTML mockup's evaluate() implemented exactly: ordered gates, first match wins.
Do not fork this logic into a renderer or a scheduled script — import it.
"""

# Thresholds come from the source workbook's "Pause Rules" sheet.
# They are CONFIGURATION. Change them here and every output recomputes; never inline them in SQL.
THRESHOLDS = dict(
    stock_floor=5,        # a listing below this counts as low stock
    acos_ceiling=40.0,    # Rule 1 — pause at or above this 30D ACOS
    acos_rescue=20.0,     # Rule 1 — skip the pause below this 7D ACOS (improving trend)
    clicks_min=20,        # Rule 2 — only applies at or above this many 14D clicks
    spend_floor=2.50,     # Rule 2 — skip the pause below this 14D spend (cheap organic clicks)
    prio_high=40.0,       # priority bands, by 30D spend at risk
    prio_med=15.0,
)


def money(v):
    return "£%.2f" % v


def priority_for(row, th=THRESHOLDS):
    if row["spend30"] >= th["prio_high"]:
        return "High"
    if row["spend30"] >= th["prio_med"]:
        return "Medium"
    return "Low"


def evaluate(r, th=THRESHOLDS):
    """Return the pause decision for one campaign row. Gates run in order; first match wins.

    ⚠ The decision is returned under the key `outcome`, NOT `status`. `status` is the campaign's
    own live state (RUNNING / PAUSED / ENDED) and must survive untouched — if the decision
    overwrote it, a second pass over the same rows would read every PAUSED recommendation as an
    already-off campaign and silently return zero pauses. That bug is why these keys differ.
    """
    trace = []
    T = lambda label, ok, detail: trace.append((label, ok, detail))

    # ---- Gate 0 — state. Rules are not evaluated against a campaign that is not running.
    if r["status"] != "RUNNING":
        T("State check — campaign is live", False,
          "campaign is %s — rules not evaluated" % r["status"])
        return dict(outcome="ALREADY OFF", rule="—", priority=None, trace=trace,
                    reason="Campaign is already %s. No pause action taken — the rules are not "
                           "evaluated against a campaign that is not running." % r["status"])
    T("State check — campaign is live", True, "eligible for pause rules")

    # ---- Gate 1 — Stock. Availability beats performance, so it runs before any ACOS rule.
    # The source sheet held one hand-typed stock figure per row. Live data cannot supply that:
    # a campaign advertises many listings and each listing carries many variant SKUs. The faithful
    # equivalent is "this campaign is paying to advertise items that cannot be bought".
    oos = r["out_of_stock"]
    T("Stock rule — advertised listings that are out of stock", oos > 0,
      "%d of %d listings at 0 units" % (oos, r["listings"]))
    if oos > 0:
        return dict(outcome="PAUSED", rule="Stock", priority="High", trace=trace,
                    reason="%d of the %d listings this campaign advertises %s out of stock (0 units). "
                           "Ads are paused so spend does not keep running on items that cannot be "
                           "bought." % (oos, r["listings"], "is" if oos == 1 else "are"))

    # ---- Gate 2 — Rule 1, high 30D ACOS, rescued by an improving 7D trend.
    in_scope = r["ord30"] > 0
    T("Rule 1 scope — 30D orders > 0", in_scope, "%g orders in 30D" % r["ord30"])
    if in_scope:
        a30 = r["acos30"]
        hi = a30 is not None and a30 >= th["acos_ceiling"]
        T("Condition — 30D ACOS ≥ %g%%" % th["acos_ceiling"], hi,
          ("30D ACOS %.1f%%" % a30) if a30 is not None else "no attributed sales")
        if hi:
            a7 = r["acos7"]
            rescue = a7 is not None and a7 < th["acos_rescue"]
            T("Do-not-pause — 7D ACOS < %g%% (improving trend)" % th["acos_rescue"], rescue,
              ("7D ACOS %.1f%%" % a7) if a7 is not None else "no 7D sales")
            if not rescue:
                return dict(outcome="PAUSED", rule="Rule 1", priority=priority_for(r, th), trace=trace,
                            reason="30-day ACOS is %.1f%%, over the %g%% ceiling. The last 7 days are "
                                   "%s — not below the %g%% needed to count as an improving trend, "
                                   "so the campaign is paused."
                                   % (a30, th["acos_ceiling"],
                                      ("still at %.1f%% ACOS" % a7) if a7 is not None
                                      else "showing no attributed sales at all",
                                      th["acos_rescue"]))

    # ---- Gate 3 — Rule 2, clicks with no sales, rescued by cheap spend.
    in_scope = r["ord14"] == 0
    T("Rule 2 scope — 14D orders = 0", in_scope, "%g orders in 14D" % r["ord14"])
    if in_scope:
        enough = r["clicks14"] >= th["clicks_min"]
        T("Condition — 14D clicks ≥ %d" % th["clicks_min"], enough, "%g clicks" % r["clicks14"])
        if enough:
            cheap = r["spend14"] < th["spend_floor"]
            T("Do-not-pause — 14D spend < %s (organic ranking boost, low cost)"
              % money(th["spend_floor"]), cheap, money(r["spend14"]))
            if not cheap:
                return dict(outcome="PAUSED", rule="Rule 2", priority=priority_for(r, th), trace=trace,
                            reason="%g clicks over 14 days produced zero orders, and spend of %s is "
                                   "at or above the %s floor — no longer cheap enough to justify "
                                   "keeping it live for the organic-ranking signal."
                                   % (r["clicks14"], money(r["spend14"]), money(th["spend_floor"])))

    return dict(outcome="RUNNING", rule="—", priority=None, trace=trace,
                reason="No rule matched — the campaign keeps running.")


PRIO_ORDER = {"High": 0, "Medium": 1, "Low": 2}


def decide_all(rows, th=THRESHOLDS):
    """Evaluate every row, sort by priority then spend, and return (rows, kpis)."""
    for r in rows:
        r["acos30"] = (r["spend30"] / r["sales30"] * 100) if r["sales30"] else None
        r["acos7"] = (r["spend7"] / r["sales7"] * 100) if r["sales7"] else None
        r.update(evaluate(r, th))
    rows.sort(key=lambda r: (PRIO_ORDER.get(r["priority"], 3), -r["spend30"]))

    paused = [r for r in rows if r["outcome"] == "PAUSED"]
    kpis = dict(
        scope=len(rows), paused=len(paused),
        high=sum(1 for r in paused if r["priority"] == "High"),
        med=sum(1 for r in paused if r["priority"] == "Medium"),
        low=sum(1 for r in paused if r["priority"] == "Low"),
        stock=sum(1 for r in paused if r["rule"] == "Stock"),
        r1=sum(1 for r in paused if r["rule"] == "Rule 1"),
        r2=sum(1 for r in paused if r["rule"] == "Rule 2"),
        running=sum(1 for r in rows if r["outcome"] == "RUNNING"),
        off=sum(1 for r in rows if r["outcome"] == "ALREADY OFF"),
        spend_at_risk=sum(r["spend30"] for r in paused),
        spend_all=sum(r["spend30"] for r in rows),
        listings=sum(r["listings"] for r in rows),
        oos_listings=sum(r["out_of_stock"] for r in rows),
        nodata_listings=sum(r["no_stock_data"] for r in rows),
    )
    return rows, kpis
