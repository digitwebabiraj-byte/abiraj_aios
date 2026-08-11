# -*- coding: utf-8 -*-
"""PRJ-2026-022 (REQ-25) Slow Moving Products - Mahima / Germany.
Inverse of FMP #020: German-stocked SKUs that are NOT selling.
Numbers 100% RAW mcp.ledsone (order_management + inventory) via LED_* env creds.
Reason/Action = PROVISIONAL default rules (FMP-style) pending Mahima sign-off.
Emits: smp_payload.json, SlowMovingProducts_DE.xlsx, slow_moving_dashboard.html
"""
import os, json, datetime, psycopg2, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.abspath(os.path.join(HERE, "..", "..", "evidence", "final_outputs", "REQ-25_slow-moving-products"))

SQL = r"""
WITH stk AS (
  SELECT p.sku, MAX(p.title) title, SUM(COALESCE(s.stock,0)) stock
  FROM inventory.products p
  JOIN inventory.local_inventory_current_stock_location_wise s ON s.inventory_id=p.id
  WHERE s.warehouse_location='Germany' GROUP BY p.sku HAVING SUM(COALESCE(s.stock,0))>0
),
sales AS (
  SELECT oi.item_sku sku,
    MAX(o.order_date::date) last_sale,
    SUM(CASE WHEN o.order_date::date>=CURRENT_DATE-30 THEN COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END) q30,
    SUM(CASE WHEN o.order_date::date>=CURRENT_DATE-90 THEN COALESCE(NULLIF(oi.item_quantity,'')::numeric,0) ELSE 0 END) q90
  FROM order_management.orders o
  JOIN order_management.sub_source ss ON ss.id=o.sub_source_id
  JOIN order_management.order_item_info oi ON oi.order_id=o.id
  WHERE o.market_place='10' AND o.status='Completed' AND ss.source_id IN (1,2,3)
    AND oi.item_sku IS NOT NULL AND oi.item_sku<>''
  GROUP BY oi.item_sku
)
SELECT stk.sku, stk.title, stk.stock::int,
  s.last_sale, COALESCE(s.q30,0)::int q30, COALESCE(s.q90,0)::int q90,
  CASE WHEN s.last_sale IS NULL THEN NULL ELSE (CURRENT_DATE - s.last_sale) END dws
FROM stk LEFT JOIN sales s ON s.sku=stk.sku
WHERE COALESCE(s.q30,0)=0            -- SLOW = nothing sold in the last 30 days (provisional)
ORDER BY stk.stock DESC, dws DESC NULLS LAST;
"""

def clean_name(sku, title):
    if not title or title.strip().lower().startswith("combo default"):
        return sku  # combo placeholder trap -> fall back to SKU (real name carried later if catalog available)
    return title.strip()

def rule_engine(stock, q90, dws):
    """PROVISIONAL default Reason/Action rules (pending Mahima)."""
    never = dws is None
    if never:
        reason = "No sales history (dead stock)"
        action = "Clearance / liquidate" if stock >= 100 else "Review / delist"
    elif q90 == 0 and stock >= 100:
        reason = "High stock, no demand in 90 days"
        action = "Clearance / bundle"
    elif q90 == 0:
        reason = "No demand in 90 days"
        action = "Create bundle / promote"
    else:  # q90>0 but q30==0
        reason = "Slowing down (no sale in 30 days)"
        action = "Improve listing / promote"
    return reason, action

def fetch():
    conn = psycopg2.connect(host=os.environ["LED_PGHOST"], user=os.environ["LED_PGUSER"],
        password=os.environ["LED_PGPASSWORD"], dbname=os.environ.get("LED_PGDATABASE","ledsone"),
        port=os.environ.get("LED_PGPORT","5432"), connect_timeout=30)
    try:
        cur = conn.cursor(); cur.execute(SQL); rows = cur.fetchall()
    finally:
        conn.close()
    out = []
    for sku, title, stock, last_sale, q30, q90, dws in rows:
        reason, action = rule_engine(stock, q90, dws)
        out.append({
            "sku": sku, "product_name": clean_name(sku, title), "stock": stock,
            "last_sale": last_sale.isoformat() if last_sale else None,
            "q30": q30, "q90": q90,
            "days_without_sale": int(dws) if dws is not None else None,
            "reason": reason, "action": action,
        })
    return out

# ---------- Excel ----------
HDRS = ["SKU","Product Name","Stock Qty","Last Sale Date","Last 30 Days Sales",
        "Last 90 Days Sales","Days Without Sale","Reason","Action"]

def build_xlsx(rows, meta):
    wb = openpyxl.Workbook()
    nz = wb.active; nz.title = "Notes"
    notes = [
        ("Slow Moving Product Analysis - Germany (PRJ-2026-022 / REQ-25)", True),
        (f"Generated: {meta['generated']}  |  Owner: Abiraj  |  Business Validator: Mahima", False),
        ("", False),
        ("SCOPE (mirrors Fast Moving #020):", True),
        ("  * Germany only (market_place=10), status='Completed', channels Amazon/eBay/Shopify.", False),
        ("  * Universe = SKUs holding German stock > 0.", False),
        ("  * SLOW MOVING = 0 units sold in the last 30 days (provisional definition).", False),
        ("  * Sorted by Stock Qty desc (biggest tied-up stock first).", False),
        ("", False),
        ("DATA SOURCE: RAW mcp.ledsone (order_management + inventory). Numbers 100% live.", False),
        ("Days Without Sale = today - last sale date (all-time). 'Never' = no sale on record.", False),
        ("", False),
        (">>> REASON & ACTION ARE PROVISIONAL DEFAULT RULES - PENDING MAHIMA SIGN-OFF <<<", True),
        ("  Never sold + stock>=100 -> 'No sales history' / 'Clearance / liquidate'", False),
        ("  q90=0 & stock>=100      -> 'High stock, no demand in 90 days' / 'Clearance / bundle'", False),
        ("  q90=0 & stock<100       -> 'No demand in 90 days' / 'Create bundle / promote'", False),
        ("  q90>0 & q30=0           -> 'Slowing down' / 'Improve listing / promote'", False),
    ]
    for i,(t,b) in enumerate(notes,1):
        c = nz.cell(row=i, column=1, value=t)
        if b: c.font = Font(bold=True)
    nz.column_dimensions['A'].width = 95

    ws = wb.create_sheet("Slow Moving")
    hf = Font(bold=True, color="FFFFFF"); hfill = PatternFill("solid", fgColor="6D28D9")
    thin = Side(style="thin", color="DDDDDD"); bd = Border(thin,thin,thin,thin)
    for j,h in enumerate(HDRS,1):
        c = ws.cell(row=1, column=j, value=h); c.font=hf; c.fill=hfill
        c.alignment=Alignment(horizontal="center", vertical="center"); c.border=bd
    for i,r in enumerate(rows,2):
        vals = [r["sku"], r["product_name"], r["stock"], r["last_sale"] or "",
                r["q30"], r["q90"],
                ("Never" if r["days_without_sale"] is None else r["days_without_sale"]),
                r["reason"], r["action"]]
        for j,v in enumerate(vals,1):
            c = ws.cell(row=i, column=j, value=v); c.border=bd
            if j in (3,5,6,7): c.alignment=Alignment(horizontal="center")
    widths=[16,42,10,14,12,12,14,32,26]
    for j,w in enumerate(widths,1): ws.column_dimensions[openpyxl.utils.get_column_letter(j)].width=w
    ws.freeze_panes="A2"; ws.auto_filter.ref=f"A1:{openpyxl.utils.get_column_letter(len(HDRS))}{len(rows)+1}"
    path = os.path.join(OUT, "SlowMovingProducts_DE.xlsx"); wb.save(path); return path

# ---------- Dashboard ----------
def build_html(rows, meta):
    never = sum(1 for r in rows if r["days_without_sale"] is None)
    z90   = sum(1 for r in rows if r["q90"]==0)
    units = sum(r["stock"] for r in rows)
    tr = "\n".join(
        "<tr><td>{sku}</td><td class=nm>{nm}</td><td class=n>{st}</td><td>{ls}</td>"
        "<td class=n>{q30}</td><td class=n>{q90}</td><td class=n>{dws}</td>"
        "<td>{rs}</td><td>{ac}</td></tr>".format(
            sku=r["sku"], nm=(r["product_name"] or "").replace("<","&lt;"),
            st=f'{r["stock"]:,}', ls=r["last_sale"] or "&mdash;",
            q30=r["q30"], q90=r["q90"],
            dws=("Never" if r["days_without_sale"] is None else r["days_without_sale"]),
            rs=r["reason"], ac=r["action"])
        for r in rows)
    html = """<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Slow Moving Products - Germany</title><style>
:root{--v:#6d28d9;--c:#0891b2;--bg:#f6f7fb;--ink:#1e293b;--mut:#64748b;--line:#e5e7eb}
*{box-sizing:border-box}body{margin:0;font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--ink)}
header{background:linear-gradient(100deg,var(--v),var(--c));color:#fff;padding:22px 28px}
h1{margin:0;font-size:22px}.sub{opacity:.9;font-size:13px;margin-top:4px}
.kpis{display:flex;gap:14px;flex-wrap:wrap;padding:18px 28px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 18px;min-width:150px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.kpi .v{font-size:26px;font-weight:700}.kpi .l{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.4px}
.warn{margin:0 28px 14px;background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;padding:10px 14px;border-radius:10px;font-size:13px}
.wrap{padding:0 28px 40px}.tools{display:flex;gap:10px;margin:8px 0 12px}
input{flex:1;padding:10px 14px;border:1px solid var(--line);border-radius:10px;font-size:14px}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.05)}
th,td{padding:9px 12px;border-bottom:1px solid var(--line);font-size:13px;text-align:left}
th{position:sticky;top:0;background:var(--v);color:#fff;cursor:pointer;white-space:nowrap}
td.n{text-align:center}td.nm{max-width:320px;color:var(--mut)}tr:hover td{background:#faf5ff}
.foot{color:var(--mut);font-size:12px;padding:16px 28px}
</style></head><body>
<header><h1>Slow Moving Products &mdash; Germany</h1>
<div class=sub>PRJ-2026-022 / REQ-25 &middot; Business Validator: Mahima &middot; Generated __GEN__ &middot; Source: RAW mcp.ledsone</div></header>
<div class=kpis>
<div class=kpi><div class=v>__ROWS__</div><div class=l>Slow-moving SKUs</div></div>
<div class=kpi><div class=v>__UNITS__</div><div class=l>Units tied up</div></div>
<div class=kpi><div class=v>__Z90__</div><div class=l>Zero sales in 90d</div></div>
<div class=kpi><div class=v>__NEVER__</div><div class=l>Never sold on record</div></div>
</div>
<div class=warn><b>Provisional:</b> "Reason" and "Action" use default rules pending Mahima's sign-off. Slow-moving = 0 units sold in last 30 days.</div>
<div class=wrap><div class=tools><input id=q placeholder="Search SKU, name, reason, action..."></div>
<table id=t><thead><tr>
<th>SKU</th><th>Product Name</th><th>Stock</th><th>Last Sale</th><th>30d</th><th>90d</th><th>Days No Sale</th><th>Reason</th><th>Action</th>
</tr></thead><tbody>
__ROWS_HTML__
</tbody></table></div>
<div class=foot>Numbers 100% live from raw ledsone (order_management + inventory, Germany). Days Without Sale = all-time.</div>
<script>
const q=document.getElementById('q'),rows=[...document.querySelectorAll('#t tbody tr')];
q.addEventListener('input',()=>{const v=q.value.toLowerCase();rows.forEach(r=>r.style.display=r.innerText.toLowerCase().includes(v)?'':'none')});
document.querySelectorAll('#t th').forEach((h,i)=>h.addEventListener('click',()=>{
 const tb=h.closest('table').querySelector('tbody');const rs=[...tb.rows];const asc=h.dataset.a=h.dataset.a==='1'?'':'1';
 rs.sort((a,b)=>{let x=a.cells[i].innerText,y=b.cells[i].innerText;const nx=parseFloat(x.replace(/,/g,'')),ny=parseFloat(y.replace(/,/g,''));
 if(!isNaN(nx)&&!isNaN(ny)){x=nx;y=ny}return (x>y?1:x<y?-1:0)*(asc?1:-1)});rs.forEach(r=>tb.appendChild(r))}));
</script></body></html>"""
    html = (html.replace("__GEN__", meta["generated"]).replace("__ROWS__", f"{len(rows):,}")
            .replace("__UNITS__", f"{units:,}").replace("__Z90__", f"{z90:,}")
            .replace("__NEVER__", f"{never:,}").replace("__ROWS_HTML__", tr))
    path = os.path.join(OUT, "slow_moving_dashboard.html"); open(path,"w",encoding="utf-8").write(html); return path

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rows = fetch()
    meta = {"generated": datetime.date.today().isoformat(), "rows": len(rows)}
    json.dump({"meta": meta, "rows": rows}, open(os.path.join(HERE,"smp_payload.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    xp = build_xlsx(rows, meta); hp = build_html(rows, meta)
    print("rows:", len(rows)); print("xlsx:", xp); print("html:", hp)
