import json, re
src = r"C:\Users\digit\Downloads\preview_catfilter (1).html"
html = open(src, encoding="utf-8").read()
i = html.find("const D=")
assert i != -1
j = i + len("const D=")
# brace-match from first '{'
start = html.index("{", j)
depth=0; k=start; instr=False; esc=False
while k < len(html):
    c = html[k]
    if instr:
        if esc: esc=False
        elif c=="\\": esc=True
        elif c=='"': instr=False
    else:
        if c=='"': instr=True
        elif c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0:
                break
    k+=1
end = k  # index of matching closing brace
payload = html[start:end+1]
D = json.loads(payload)
prefix = html[:start]      # includes 'const D='
suffix = html[end+1:]      # starts right after '}' (the ';...')
open("tmpl_prefix.txt","w",encoding="utf-8").write(prefix)
open("tmpl_suffix.txt","w",encoding="utf-8").write(suffix)
open("old_D.json","w",encoding="utf-8").write(json.dumps(D, indent=1))
print("prefix bytes:", len(prefix), "suffix bytes:", len(suffix))
print("D top keys:", list(D.keys()))
print("period:", D.get("period"), "| generated:", D.get("generated"))
print("phs count:", len(D["phs"]))
print("alloc keys:", len(D["alloc"]))
print("rows count:", len(D["rows"]))
print("sample row:", D["rows"][0])
print("row length:", len(D["rows"][0]))
# any other keys?
for kk,v in D.items():
    if kk not in ("period","generated","alloc","phs","rows"):
        print("OTHER KEY", kk, "->", str(v)[:200])
