import json, os, sys
from collections import Counter

BASE = r"C:\Users\digit\AppData\Local\Temp\claude\C--Users-digit-OneDrive-Desktop-Abiraj-AIOS--claude-worktrees-phase-asin-segmentation-progress-4a77f8\08d1586b-488c-492c-9e43-46a5488e7f49\scratchpad"
RAW = os.path.join(BASE, "raw")

NAMES = ["Abinayaa","Akalika","Akanila","Arudchelvi","Dilakshiga","Dilani","Illakkiya","Jasmini","Jathisha","Jubista","mothajini","Nithushana","paulr","prasath","preethi","Ramsika","Renuha","Saranya","Sarbavi","Shanthini","shimee","thanusha","Tharshana","Tharsiga(nelli)","Tharsika(jaffna)","Theepana","Thojika","thuwaraga","utharsika","Vaishnavi"]

ALLOC = {'Abinayaa':253,'Akalika':303,'Akanila':265,'Arudchelvi':245,'Dilakshiga':57,'Dilani':425,'Illakkiya':236,'Jasmini':1264,'Jathisha':220,'Jubista':217,'mothajini':181,'Nithushana':255,'paulr':634,'prasath':530,'preethi':330,'Ramsika':98,'Renuha':227,'Saranya':219,'Sarbavi':90,'Shanthini':105,'shimee':726,'thanusha':146,'Tharshana':230,'Tharsiga(nelli)':355,'Tharsika(jaffna)':432,'Theepana':345,'Thojika':438,'thuwaraga':776,'utharsika':1723,'Vaishnavi':74}

# NOTE: EXPECT_SEG updated to the COUNT-BASED conversion rule (Bietrick-approved 2026-07-10),
# verified read-only against the live DB on the D10 window (weeks ending 6/13/20/27 Jun, rn 2..5).
# The RATE-based D10 gate was {'HHH':42,'HHL':580,'HLH':173,'LHH':10,'LLH':626,'LLL':8516}.
# EXPECT_TOTAL and EXPECT_PH are UNCHANGED (same 9,947 ASINs / same ownership — only the segment mix moved).
EXPECT_TOTAL = 9947
EXPECT_SEG = {'HHH':180,'HHL':433,'HLH':173,'LHH':19,'LLH':144,'LLL':8998}
EXPECT_PH = {'Abinayaa':224,'Akalika':162,'Akanila':224,'Arudchelvi':237,'Dilakshiga':47,'Dilani':368,'Illakkiya':217,'Jasmini':1220,'Jathisha':206,'Jubista':188,'mothajini':162,'Nithushana':242,'paulr':609,'prasath':478,'preethi':162,'Ramsika':91,'Renuha':218,'Saranya':161,'Sarbavi':72,'Shanthini':103,'shimee':639,'thanusha':129,'Tharshana':199,'Tharsiga(nelli)':331,'Tharsika(jaffna)':381,'Theepana':316,'Thojika':292,'thuwaraga':622,'utharsika':1578,'Vaishnavi':69}

missing = [n for n in NAMES if not os.path.exists(os.path.join(RAW, n+".json"))]
if missing:
    print("MISSING raw files:", missing); sys.exit(1)

rows=[]; cats=[]
for n in NAMES:
    d=json.load(open(os.path.join(RAW,n+".json"),encoding="utf-8"))
    r=d["rows"] if isinstance(d["rows"],list) else json.loads(d["rows"])
    c=d["cats"] if isinstance(d["cats"],list) else json.loads(d["cats"])
    # guard: every row/cat must belong to this PH
    assert all(x[0]==n for x in r), f"row user mismatch in {n}"
    assert all(x[0]==n for x in c), f"cat user mismatch in {n}"
    rows+=r; cats+=c

# ---- validate ----
assert len(rows)==EXPECT_TOTAL, f"total {len(rows)} != {EXPECT_TOTAL}"
seg=Counter(x[2] for x in rows)
for k,v in EXPECT_SEG.items():
    assert seg[k]==v, f"seg {k} {seg[k]} != {v}"
perph=Counter(x[0] for x in rows)
for k,v in EXPECT_PH.items():
    assert perph[k]==v, f"ph {k} {perph[k]} != {v}"
mov=Counter(x[3] for x in rows)
print("VALIDATED: total",len(rows),"| seg",dict(seg),"| mov",dict(mov),"| cats",len(cats))

# ---- build phs order (case-insensitive alpha) + index map ----
phs=sorted(NAMES, key=str.lower)
idx={n:i for i,n in enumerate(phs)}
rows2=[[idx[x[0]]]+x[1:] for x in rows]
cats2=[[idx[x[0]]]+x[1:] for x in cats]

D={"period":"2026-07","generated":"10 Jul 2026","alloc":{n:ALLOC[n] for n in phs},"phs":phs,"rows":rows2,"cats":cats2}

prefix=open(os.path.join(BASE,"tmpl_prefix.txt"),encoding="utf-8").read()
suffix=open(os.path.join(BASE,"tmpl_suffix.txt"),encoding="utf-8").read()
html=prefix+json.dumps(D,ensure_ascii=False,separators=(",",":"))+suffix

out=os.path.join(BASE,"ph_asin_dashboard_all_ph_leader_corrected_2026-07.html")
open(out,"w",encoding="utf-8",newline="").write(html)
print("WROTE",out,"bytes",len(html.encode("utf-8")))
print("phs(",len(phs),"):",phs)
