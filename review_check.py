#!/usr/bin/env python3
"""Verification script for review.md. Recomputes the numbers review.md cites that meta.py does not emit.
Run: python3 review_check.py   (reads the three source corpora read-only; ~20 s)."""
import json, re, collections, statistics as st, os, math
HOME=os.path.expanduser("~")
AF=json.load(open(f"{HOME}/alignment-forum-scrape/projects.json"))
LW=json.load(open(f"{HOME}/scrape-lesswrong/lesswrong_empirical_ai_safety_projects.json"))
POST_ID=re.compile(r"/posts/([A-Za-z0-9]+)/"); GH=re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
def repo(u):
    if not u: return None
    m=GH.search(u); return f"{m.group(1)}/{m.group(2)}".lower().removesuffix(".git") if m else None
for r in AF: r["_pid"]=POST_ID.search(r["url"]).group(1)
for r in LW: r["_pid"]=r["_id"]
AFP={r["_pid"]:r for r in AF}; LWP={r["_pid"]:r for r in LW}
U={}
for r in LW: U[r["_pid"]]=dict(r,_src="LW")
for r in AF: U.setdefault(r["_pid"],dict(r,_src="AF"))
V=list(U.values()); BOTH=set(AFP)&set(LWP)
print("schema AF:",sorted(AF[0].keys())); print("schema LW:",sorted(LW[0].keys()))
# (a) repos claimed by >1 union post, correctly
c=collections.Counter(filter(None,(repo(r["github-link"]) for r in V)))
print("distinct own repos in union:",len(c)," >1 posts:",sum(1 for v in c.values() if v>1)," >2 posts:",sum(1 for v in c.values() if v>2))
print(" list >1:",[(k,v) for k,v in c.most_common() if v>1])
# (b) date range and partial periods
ds=sorted(r["date"] for r in V); print("date range union:",ds[0],ds[-1])
print("AF range:",min(r["date"] for r in AF),max(r["date"] for r in AF)); print("LW range:",min(r["date"] for r in LW),max(r["date"] for r in LW))
def half(d): return f"{d[:4]}H{1 if int(d[5:7])<=6 else 2}"
days={"2024H2":(153),"2025H1":181,"2025H2":184,"2026H1":181,"2026H2":56}  # Aug1-Dec31=153; Jul1-Aug25=56
for lbl,rs in [("AF",AF),("LW",LW),("UNION",V)]:
    g=collections.Counter(half(r["date"]) for r in rs)
    print(lbl,"per-half:",dict(g)," per-30-days:",{p:round(30*g[p]/days[p],1) for p in days})
# monthly AF counts 2026
m=collections.Counter(r["date"][:7] for r in AF); print("AF monthly:",sorted(m.items())[-14:])
m=collections.Counter(r["date"][:7] for r in LW); print("LW monthly:",sorted(m.items())[-14:])
# (c) in_af vs not
ina=[int(r["karma"]) for r in V if r["_pid"] in AFP]; notin=[int(r["karma"]) for r in V if r["_pid"] not in AFP]
print("in_af n",len(ina),"med karma",st.median(ina)," repo%",round(100*sum(1 for r in V if r['_pid'] in AFP and r['github-link'])/len(ina),1))
print("not in_af n",len(notin),"med karma",st.median(notin))
# (d) Wilson CI for coverage
def wilson(k,n,z=1.96):
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return round(100*(c-h)),round(100*(c+h))
for p,(k,n) in {"2024H2":(28,37),"2025H1":(49,78),"2025H2":(44,80),"2026H1":(21,44),"2026H2":(7,14)}.items(): print(p,f"{100*k/n:.0f}%",wilson(k,n))
# (e) regex false positives sample
for name,pat in [("bootstrap",r"\bbootstrap"),("seeds_loose",r"\b(random seed|seeds?\b|across \d+ seeds|seed variance)\b"),("±",r"±"),("agentic",r"\bagentic\b")]:
    rx=re.compile(pat,re.I); hits=[]
    for r in V:
        for mm in rx.finditer(r["article-content"] or ""):
            s=r["article-content"][max(0,mm.start()-50):mm.end()+50].replace("\n"," "); hits.append(s)
    import random; random.seed(1)
    print(f"\n== {name}: {len(hits)} hits; sample:")
    for s in random.sample(hits,min(8,len(hits))): print("   …"+s+"…")
# strict seeds w/ only "random seed"
rx=re.compile(r"\brandom seeds?\b",re.I); print("\nrandom seed(s) only:",round(100*sum(1 for r in V if rx.search(r['article-content'] or ''))/len(V),1),"%")
# multi-model alt: count distinct model family names
fam=re.compile(r"\b(gpt-?[45o]|claude|gemma|llama|qwen|mistral|deepseek|pythia|gemini|o[13]-?(?:mini)?|kimi|phi-?\d)\b",re.I)
mm=[len({x.lower()[:4] for x in fam.findall(r["article-content"] or "")}) for r in V]
print("posts naming >=2 model families (crude):",round(100*sum(1 for x in mm if x>=2)/len(V),1),"%  >=3:",round(100*sum(1 for x in mm if x>=3)/len(V),1),"%")
# AF karma field vs LW: check a shared record's fields
p=next(iter(BOTH)); print("\nAF rec keys sample:",{k:(str(v)[:40]) for k,v in AFP[p].items() if k not in("article-content","github-readme")})
print("LW rec keys sample:",{k:(str(v)[:40]) for k,v in LWP[p].items() if k not in("article-content","github-readme")})
