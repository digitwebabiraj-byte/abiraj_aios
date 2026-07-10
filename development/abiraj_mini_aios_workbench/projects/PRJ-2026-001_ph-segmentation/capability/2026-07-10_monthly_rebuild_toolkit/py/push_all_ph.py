import psycopg2, hashlib, os
# Set PGPASSWORD env var before running. temp_user creds are in Downloads/temp_user 1.py — DO NOT commit them.
# EACH CYCLE, refresh: EXISTING (query ph_task for current id->assigned_user map), ROSTER (sql/00),
# the task_id prefix + description window text (period-specific), and BKDIR (dated folder).
DB=dict(host="149.28.134.54",port="5435",dbname="order_management_copy",user="temp_user",password=os.getenv("PGPASSWORD"))
HTMLDIR="per_ph_html"
BKDIR=r"C:\Users\digit\OneDrive\Desktop\Abiraj_AIOS\.claude\worktrees\phase-asin-segmentation-progress-4a77f8\development\abiraj_mini_aios_workbench\projects\PRJ-2026-001_ph-segmentation\evidence\final_outputs\REQ-05_ph-asin-segmentation\2026-07-10_per_ph_PRE-UPDATE_backups"
os.makedirs(BKDIR,exist_ok=True)

ROSTER=["Abinayaa","Akalika","Akanila","Arudchelvi","Dilakshiga","Dilani","Illakkiya","Jasmini","Jathisha","Jubista","mothajini","Nithushana","paulr","prasath","preethi","Ramsika","Renuha","Saranya","Sarbavi","Shanthini","shimee","thanusha","Tharshana","Tharsiga(nelli)","Tharsika(jaffna)","Theepana","Thojika","thuwaraga","utharsika","Vaishnavi"]
EXISTING={'Abinayaa':58,'Arudchelvi':59,'Dilani':60,'Illakkiya':61,'Jasmini':62,'Jubista':63,'Nithushana':64,'Poovitha':65,'Renuha':66,'Saranya':67,'Shanthini':68,'Tharshana':69,'Tharsiga(nelli)':70,'Tharsika(jaffna)':71,'Theepana':72,'Thojika':73,'mothajini':74,'paulr':75,'prasath':76,'preethi':77,'shimee':78,'thanucha':79,'thuwaraga':80,'utharsika':81}

def load(n):
    h=open(os.path.join(HTMLDIR,n+".html"),encoding="utf-8").read()
    return h, hashlib.md5(h.encode("utf-8")).hexdigest()

updates=[n for n in ROSTER if n in EXISTING]
inserts=[n for n in ROSTER if n not in EXISTING]
print("UPDATE:",len(updates),"| INSERT:",len(inserts),"->",inserts)

conn=psycopg2.connect(connect_timeout=20,**DB)
try:
    with conn:
        with conn.cursor() as cur:
            filemd5={}
            # ---- UPDATE existing (with backup) ----
            for n in updates:
                tid=EXISTING[n]
                cur.execute("SELECT html_content FROM tech_team_outputs.ph_task WHERE id=%s",(tid,))
                old=cur.fetchone()[0]
                with open(os.path.join(BKDIR,f"{tid}_{n}.html"),"w",encoding="utf-8",newline="") as f: f.write(old or "")
                html,md5=load(n); filemd5[n]=md5
                cur.execute("UPDATE tech_team_outputs.ph_task SET html_content=%s, updated_at=now() WHERE id=%s",(html,tid))
                assert cur.rowcount==1
            print("updated",len(updates),"rows (backed up to project evidence)")
            # ---- INSERT new ----
            for n in inserts:
                html,md5=load(n); filemd5[n]=md5
                tid_txt="ph-asin-2026-07-"+n.lower()
                disp=n[:1].upper()+n[1:]
                desc=(f"Monthly PH ASIN segmentation report (UK Amazon FBM). {disp}, 6 segments, "
                      "category-wise benchmarks, movement vs previous 4-week window, escalation flags. "
                      "Window: last 4 complete weeks (31 May-27 Jun 2026). Corrected 30-PH roster; rebuilt 10 Jul 2026.")
                cur.execute("""INSERT INTO tech_team_outputs.ph_task
                  (project_name,project_code,task_name,task_id,team,developer,assigned_user,assigned_user_team,html_content,description,phase_level,version_level,version_status)
                  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                  ('PH ASIN Segmentation — GPE','ph-asin','PH ASIN Segmentation — July 2026',tid_txt,'Development','Abiraj',n,'ph_priors',html,desc,4,1,'released'))
                # NOTE: assigned_user_team='ph_priors' is REQUIRED (not in the sample DDL). Missing it = NULL = the card-team gap fixed on 2026-07-10.
                newid=cur.fetchone()[0]
                print(f"  inserted {n:<12} -> id {newid}  task_id {tid_txt}")
            # ---- verify all 30 within txn ----
            bad=0
            for n in ROSTER:
                cur.execute("SELECT md5(html_content) FROM tech_team_outputs.ph_task WHERE assigned_user=%s AND project_code='ph-asin' AND task_id LIKE 'ph-asin-2026-07-%%'",(n,))
                rows=cur.fetchall()
                got=[r[0] for r in rows]
                ok = (filemd5[n] in got) and len(rows)==1
                if not ok:
                    bad+=1; print("  VERIFY FAIL",n,"rows",len(rows),"md5",got,"exp",filemd5[n])
            assert bad==0, f"{bad} verify failures -> rolling back"
            print("VERIFY: all 30 roster rows match their file md5 (exactly 1 row each)")
    print("TRANSACTION COMMITTED OK")
finally:
    conn.close()
