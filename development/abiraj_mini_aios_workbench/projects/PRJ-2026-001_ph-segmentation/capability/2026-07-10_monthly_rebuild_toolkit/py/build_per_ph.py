"""
build_per_ph.py  —  build one single-PH dashboard HTML per holder.

INPUT  (edit BASE):
  BASE/raw/<PH>.json     one file per PH from the recompute (01/02); each is
                         {"nrows":N,"rows":[15-field arrays],"cats":[9-field arrays]}
                         row = [user_name,cat,seg,mov,asin,sku,acc,imp,clk,conv,cvr,bi,bk,bcvr,rank]
                         cat = [user_name,cat,listings,topn,bi,bk,bcvr,status,bconv]
  BASE/alloc.json        {"<PH>": <allocated_count>, ...}  from sql/04_alloc_counts.sql
  BASE/tmpl_prefix.txt , BASE/tmpl_suffix_single.txt   (template shell; single-PH suffix
                         adds the auto-select line so the file opens straight on that PH)

OUTPUT:
  BASE/per_ph_html/<PH>.html   one locked single-PH dashboard each

Same UI as the leader; each file embeds ONLY that PH's data (phIdx forced to 0).
"""
import json, os

BASE = r"<SET THIS to the working dir that holds raw/ , alloc.json , tmpl_*>"
PERIOD    = "2026-07"          # report_period label
GENERATED = "10 Jul 2026"      # shown in the meta strip

RAW = os.path.join(BASE,"raw"); OUT = os.path.join(BASE,"per_ph_html"); os.makedirs(OUT,exist_ok=True)
ALLOC  = json.load(open(os.path.join(BASE,"alloc.json"),encoding="utf-8"))
prefix = open(os.path.join(BASE,"tmpl_prefix.txt"),encoding="utf-8").read()
suffix = open(os.path.join(BASE,"tmpl_suffix_single.txt"),encoding="utf-8").read()

names = sorted([f[:-5] for f in os.listdir(RAW) if f.endswith(".json")], key=str.lower)
total = 0
for n in names:
    d = json.load(open(os.path.join(RAW,n+".json"),encoding="utf-8"))
    rows = d["rows"] if isinstance(d.get("rows"),list) else json.loads(d["rows"])
    cats = d["cats"] if isinstance(d.get("cats"),list) else json.loads(d["cats"])
    assert all(x[0]==n for x in rows), f"{n}: a row is labelled for another PH"
    rows2 = [[0]+x[1:] for x in rows]     # phIdx -> 0
    cats2 = [[0]+x[1:] for x in cats]
    D = {"period":PERIOD,"generated":GENERATED,"alloc":{n:ALLOC.get(n,0)},"phs":[n],"rows":rows2,"cats":cats2}
    html = prefix + json.dumps(D,ensure_ascii=False,separators=(",",":")) + suffix
    open(os.path.join(OUT,n+".html"),"w",encoding="utf-8",newline="").write(html)
    total += len(rows); print(f"  {n:<18} rows={len(rows):<5} cats={len(cats):<3} {len(html.encode('utf-8'))} bytes")
print(f"built {len(names)} per-PH HTMLs, total rows {total}")
