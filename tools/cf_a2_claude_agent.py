#!/usr/bin/env python3
"""Execute next Bell & Leaf specialist with Claude Code, no filesystem tools.
Only the 21-role DAG may select outputs. This is not human/creative approval.
"""
from __future__ import annotations
import argparse,datetime as dt,json,os,pathlib,re,subprocess,sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import cf_a2_master_skill as master

def read(path,maxsize=100000):
    data=path.read_text(encoding="utf-8")
    if len(data)>maxsize:raise ValueError("Input too large; review and split: "+str(path))
    return data

def prepare(repo,episode,store):
    repo,base,manifest,graph=master.context(repo,episode,store)
    nxt=master.scan(repo,episode,store)["next"]
    if nxt["type"]!="RUN_SKILL":
        raise ValueError("Next step is "+nxt["type"]+"; real reviewer must clear stage gate")
    roles={r["id"]:r for r in graph["nodes"]}
    node=roles[nxt["skill_id"]]
    sources=None
    if node["id"]=="r01-source-evidence":
        p=base/"01_research/input_sources.json"
        if not p.is_file():raise ValueError("R01 needs 01_research/input_sources.json with real dated URLs")
        sources=json.loads(read(p))
        if sources.get("subniche_id")!="magical_witch_family_stories" or not sources.get("sources"):
            raise ValueError("Invalid research subniche or empty sources")
        for x in sources["sources"]:
            if not x.get("url","").startswith("https://") or not x.get("observed_at_utc") or not x.get("method") or x.get("peer_group") not in ("DIRECT_MAGICAL_FAMILY","ADJACENT_SLOW_ENGLISH","OTHER_CONTEXT"):
                raise ValueError("Unverified or unclassified source record")
    upstream={}
    for dep in node["requires"]:
        if master.receipt_status(base,roles[dep],graph)["status"]!="HANDOFF_RECORDED":
            raise ValueError("Unverified prior skill "+dep)
        for name in roles[dep]["outputs"]:
            upstream[name]=read(master._safe(base,name))
    canon={}
    for label,path in (
      ("series_bible","config/niches/slow_english_a2/SERIES_BIBLE.md"),
      ("voice_registry","config/niches/slow_english_a2/voice_registry.json"),
      ("production_profile","config/niches/slow_english_a2/production.json")):
        canon[label]=read(repo/path)
    task={
      "project_id":"slow_english_a2_bell_leaf","subniche_id":"magical_witch_family_stories",
      "episode_id":episode,"stage":node["stage"],"required_outputs":node["outputs"],
      "upstream_artifacts":upstream,"original_source_records":sources,
      "canon":canon,
      "skill_instructions":read(repo/node["skill_file"]),
    }
    prompt=(
      "Act as the CINE Bell & Leaf specialist. Do the actual assigned research or original writing "
      "using only the attached source records and Canon. Never invent video URL, views, people, "
      "video-watching status, A2 listener results, independent approval, or license. "
      "Treat ADJACENT_SLOW_ENGLISH competitors as adjacent, never magical-family direct peers. "
      "Respond ONLY in valid JSON with shape: "
      '{"artifacts":[{"path":"exact_required_path","content":"complete substantive file text"}],'
      '"summary":"what you accomplished","limitations":["evidence limitations"]}. '
      "Provide EXACT required outputs, no other files. Source claims need exact original URLs and "
      "timestamps. Do not generate fake test passes or approval. If evidence is insufficient, "
      "say so explicitly. No Markdown code fences.\n\nASSIGNMENT:\n"
      +json.dumps(task,ensure_ascii=False,indent=2))
    if node["id"]=="r01-source-evidence":
        prompt+=("\nSTRICT R01 OUTPUT CONTRACT: the content of evidence_register.json MUST be a JSON object with an items array. "
                 "Every one of the source records belongs in items with id, exact input url, observed_at_utc, "
                 "method, claim, confidence, limitations, peer_group and evidence_type. "
                 "ADJACENT_SLOW_ENGLISH metadata entries are allowed in items as contextual evidence, "
                 "but MUST NOT be called direct magical-family peers. Set direct_peer_coverage to 0 "
                 "and direct_peer_status to BLOCKED_INSUFFICIENT_DIRECT_EVIDENCE if no direct peers. "
                 "This is a valid partial research handoff, not a greenlight for Story Factory research approval.")
    if len(prompt)>120000:raise ValueError("Prompt too long, manual split required")
    return repo,base,node,prompt,sources

def parse(text,node,sources):
    data=json.loads(text.strip())
    items=data.get("artifacts")
    if not isinstance(items,list) or len(items)!=len(node["outputs"]) or {x.get("path") for x in items}!=set(node["outputs"]):
        raise ValueError("Claude returned wrong artifact paths/count")
    outputs={}
    for row in items:
        name=row["path"];val=row.get("content")
        if not isinstance(val,str) or len(val.strip())<10 or len(val)>170000:
            raise ValueError("Empty or oversized artifact "+name)
        if name.endswith(".json"):
            obj=json.loads(val)
            if not obj:raise ValueError("Empty JSON "+name)
            if name=="01_research/evidence_register.json":
                source_urls={x["url"] for x in sources["sources"]}
                events=obj.get("items",[])
                if not events:raise ValueError("No research evidence")
                for e in events:
                    if e.get("url") not in source_urls:raise ValueError("Invented research URL")
                    if e.get("confidence") not in ("VERIFIED","SUPPORTED_HYPOTHESIS","SPECULATIVE","UNKNOWN","BLOCKED"):
                        raise ValueError("Invalid confidence")
                    if not e.get("observed_at_utc") or not e.get("limitations") or not e.get("method"):
                        raise ValueError("Missing source provenance")
        if name.endswith(".md") and len(val.strip())<150:
            raise ValueError("Short Markdown placeholder "+name)
        if name.endswith(".csv") and len(val.splitlines())<2:
            raise ValueError("CSV has no data "+name)
        outputs[name]=val.rstrip()+"\n"
    return outputs,data.get("summary"),data.get("limitations",[])

def run(repo,episode,actor,storage,execute,timeout):
    repo,base,node,prompt,sources=prepare(repo,episode,storage)
    original_source_sha=(master.digest(base/"01_research/input_sources.json") if sources is not None else None)
    directory=base/"master_skill_jobs";directory.mkdir(parents=True,exist_ok=True)
    promptpath=directory/(node["id"]+".prompt.txt")
    if promptpath.exists():
        if promptpath.read_text(encoding="utf-8")!=prompt:
            raise ValueError("Existing role prompt changed; inspect before rerunning")
    else:
        promptpath.write_text(prompt,encoding="utf-8")
    if not execute:
        return {"status":"PREPARED_ONLY","skill_id":node["id"],"prompt_file":str(promptpath),
                "production_authorized":False}
    if not actor.strip():raise ValueError("Actual agent actor name required")
    args=["claude","-p","--model","sonnet","--effort","low","--tools","","--permission-mode","dontAsk",
          "--max-turns","1","--no-session-persistence","--output-format","text"]
    try:
        result=subprocess.run(args,cwd=repo,input=prompt,stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,text=True,encoding="utf-8",errors="replace",timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ValueError("Claude CLI timed out; review job before retry")
    log=directory/(node["id"]+".agent-result.json")
    log.write_text(json.dumps({"exit_code":result.returncode,
       "stderr_tail":result.stderr[-2000:],"response_head":result.stdout[:1000],
       "recorded_at_utc":dt.datetime.now(dt.timezone.utc).isoformat()},
       ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if result.returncode!=0:
        raise ValueError("Claude failed; inspect agent-result.json")
    outputs,summary,limits=parse(result.stdout,node,sources)
    if original_source_sha is not None and master.digest(base/"01_research/input_sources.json")!=original_source_sha:
        raise ValueError("Research sources changed during Claude execution; refuse unbound output")
    for name in outputs:
        path=master._safe(base,name)
        if path.exists() and path.stat().st_size>0:
            raise ValueError("Refusing to overwrite existing role artifact: "+name)
    for name,value in outputs.items():
        path=master._safe(base,name);path.parent.mkdir(parents=True,exist_ok=True)
        staged=path.with_suffix(path.suffix+".new")
        staged.write_text(value,encoding="utf-8");os.replace(staged,path)
    receipt=master.record(repo,episode,node["id"],actor,storage)
    return {"status":"ROLE_HANDOFF_RECORDED_NOT_APPROVED",
       "skill_id":node["id"],"output_paths":list(outputs),
       "receipt_sha256":receipt["receipt_sha256"],"summary":summary,
       "limitations":limits,"production_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--id",required=True)
    p.add_argument("--repo",type=pathlib.Path,default=ROOT)
    p.add_argument("--storage-root",type=pathlib.Path)
    p.add_argument("--actor",default="claude-code")
    p.add_argument("--execute",action="store_true",help="Explicitly invoke logged-in Claude Code for the next role")
    p.add_argument("--timeout",type=int,default=240)
    a=p.parse_args()
    try:print(json.dumps(run(a.repo,a.id,a.actor,a.storage_root,a.execute,a.timeout),
                       ensure_ascii=False,indent=2))
    except Exception as ex:
        print(json.dumps({"status":"BLOCKED","error":str(ex),"production_authorized":False},ensure_ascii=False))
        return 2
    return 0

if __name__=="__main__":sys.exit(main())
