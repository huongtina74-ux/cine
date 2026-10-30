#!/usr/bin/env python3
"""Single CINE A2 Master Skill runtime: dispatch 21 existing specialists by verified artifacts.

Deterministic coordination ONLY: never claims to execute an LLM, inspect media,
approve human A2 performance, authenticate a reviewer, or render a video.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
from types import SimpleNamespace

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import cf_script_factory as factory
from cf_a2_story_contract import read as read_graph,validate_graph,_relative

MODE="A2_ANIMATED_SCREENPLAY"
NICHE="magical_witch_family_stories"
STAGES=("research","insights","concepts","story","outline","script","review","final")
RECEIPTS="master_skill_receipts"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def _safe(base,rel):
    p=pathlib.PurePosixPath(rel)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError("Invalid artifact path")
    dest=base.joinpath(*p.parts).resolve()
    if not dest.is_relative_to(base.resolve()):
        raise ValueError("Artifact escapes project root")
    return dest

def _write(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".new")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    os.replace(tmp,path)

def context(repo,episode_id,store=None):
    repo=pathlib.Path(repo).resolve()
    base=factory.project_dir(episode_id,pathlib.Path(store).resolve() if store else repo/"data/script_factory/projects").resolve()
    if not base.is_dir():
        raise ValueError("Episode not initialized; use the existing cf_script_factory.py init")
    manifest=_json(base/"manifest.json")
    if manifest.get("project_id")!=episode_id or manifest.get("mode")!=MODE or manifest.get("niche_id")!=NICHE:
        raise ValueError("Not the Bell & Leaf A2 screenplay project")
    validate_graph(repo,factory.config())
    return repo,base,manifest,read_graph(repo)

def _node_map(graph):
    return {node["id"]:node for node in graph["nodes"]}

def _receipt_file(base,node_id):
    if not node_id.replace("-","").isalnum():
        raise ValueError("Bad skill ID")
    return base/RECEIPTS/(node_id+".json")

def _inspect_output(base,rel):
    path=_safe(base,rel)
    if not path.is_file() or path.stat().st_size<10:
        raise ValueError("Missing/empty skill output "+rel)
    if path.suffix==".json":
        obj=_json(path)
        if not isinstance(obj,(dict,list)) or not obj: raise ValueError("Empty JSON skill output "+rel)
    if path.suffix==".md" and len(path.read_text(encoding="utf-8").strip())<150:
        raise ValueError("Incomplete Markdown skill output "+rel)
    if path.suffix==".fountain" and len(path.read_text(encoding="utf-8").strip())<1200:
        raise ValueError("Incomplete Fountain screenplay "+rel)
    if path.suffix==".csv" and len(path.read_text(encoding="utf-8-sig").splitlines())<2:
        raise ValueError("CSV output has no entries "+rel)
    return digest(path)

def receipt_status(base,node,graph):
    path=_receipt_file(base,node["id"])
    if not path.is_file():
        return {"status":"NOT_RECORDED","reason":"Skill output handoff not recorded"}
    try:
        rec=_json(path)
        if rec.get("skill_id")!=node["id"] or rec.get("status")!="HANDOFF_RECORDED_NOT_ARTISTIC_APPROVAL":
            raise ValueError("Wrong skill receipt identity/status")
        if rec.get("outputs_sha256")!={p:_inspect_output(base,p) for p in node["outputs"]}:
            raise ValueError("Output changed since skill handoff")
        for dep in node["requires"]:
            dependency=_receipt_file(base,dep)
            if not dependency.is_file() or rec.get("upstream_receipts_sha256",{}).get(dep)!=digest(dependency):
                raise ValueError("Upstream skill changed/missing: "+dep)
        return {"status":"HANDOFF_RECORDED","sha256":digest(path)}
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        return {"status":"STALE_OR_INVALID","reason":str(exc)}

def _prior_stages_pass(factory_status,stage):
    ix=STAGES.index(stage)
    return all(factory_status["stages"].get(s)=="PASS" for s in STAGES[:ix])

def scan(repo,episode_id,store=None):
    repo,base,manifest,graph=context(repo,episode_id,store)
    fs=factory.status(SimpleNamespace(id=episode_id,root=base.parent))
    nodes=_node_map(graph)
    seen={}
    next_item=None
    for node in graph["nodes"]:
        if not node["enabled_by_default"]:
            seen[node["id"]]={"status":"OPTIONAL_DISABLED"}
            continue
        state=receipt_status(base,node,graph)
        seen[node["id"]]=state
    for stage in STAGES:
        current=[n for n in graph["nodes"] if n["stage"]==stage and n["enabled_by_default"]]
        if not _prior_stages_pass(fs,stage):
            continue
        if fs["stages"].get(stage)=="PASS":
            continue
        for node in current:
            if seen[node["id"]]["status"]=="HANDOFF_RECORDED":
                continue
            pending=[dep for dep in node["requires"] if seen.get(dep,{}).get("status")!="HANDOFF_RECORDED"]
            if pending:
                continue
            next_item={"type":"RUN_SKILL","skill_id":node["id"],"stage":stage,
                       "read_skill":node["skill_file"],"requires":node["requires"],
                       "output_paths":node["outputs"],
                       "record_command":"python tools/cf_a2_master_skill.py record --id "+episode_id+
                         " --skill "+node["id"]+" --actor <actual-author-id>",
                       "note":"Agent must actually read source and author every output; recording is not quality approval."}
            break
        if not next_item:
            all_recorded=all(seen[n["id"]]["status"]=="HANDOFF_RECORDED" for n in current)
            next_item=({"type":"STAGE_QC_GATE","stage":stage,
                        "command":"python tools/cf_script_factory.py advance --id "+episode_id+
                          " --stage "+stage+" --actor <actual-reviewer-id>",
                        "note":"Requires actual review, stage artifact inspection and current SHA."}
                       if all_recorded else
                       {"type":"BLOCKED_DEPENDENCIES","stage":stage,
                        "note":"Resolve stale/missing upstream handoffs before advancing."})
        break
    if not next_item:
        next_item={"type":"ALL_STAGES_STRUCTURALLY_PASSED" if all(x=="PASS" for x in fs["stages"].values()) else "BLOCKED_STAGE",
                   "note":"Structural checks are not human/production approval."}
    completed=sum(s["status"]=="HANDOFF_RECORDED" for s in seen.values())
    return {"project_id":"slow_english_a2_bell_leaf","episode_id":episode_id,
            "subniche_id":NICHE,"master_skill":".claude/skills/cine-script-factory/SKILL.md",
            "total_specialist_skills":len(graph["nodes"]),"mandatory_specialist_skills":sum(n["enabled_by_default"] for n in graph["nodes"]),
            "recorded_handoffs":completed,"stage_gates":fs["stages"],"next":next_item,
            "skill_states":seen,"production_authorized":False,"model_executed_by_this_command":False}

def record(repo,episode_id,skill,actor,store=None):
    repo,base,manifest,graph=context(repo,episode_id,store)
    byid=_node_map(graph)
    if skill not in byid or not byid[skill]["enabled_by_default"]:
        raise ValueError("Skill not an enabled Bell & Leaf specialist")
    node=byid[skill]
    if not actor or not actor.strip() or len(actor)>150:
        raise ValueError("Actual author id is required")
    fs=factory.status(SimpleNamespace(id=episode_id,root=base.parent))
    if not _prior_stages_pass(fs,node["stage"]):
        raise ValueError("Previous Script Factory stage not approved")
    deps={}
    for dep in node["requires"]:
        if receipt_status(base,byid[dep],graph)["status"]!="HANDOFF_RECORDED":
            raise ValueError("Upstream skill not current: "+dep)
        deps[dep]=digest(_receipt_file(base,dep))
    outputs={p:_inspect_output(base,p) for p in node["outputs"]}
    target=_receipt_file(base,skill)
    receipt={"skill_id":skill,"stage":node["stage"],
             "status":"HANDOFF_RECORDED_NOT_ARTISTIC_APPROVAL",
             "author_id":actor.strip(),"recorded_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
             "outputs_sha256":outputs,"upstream_receipts_sha256":deps,
             "warning":"Files/hash/dependencies only. Does not certify human, independent artistic QC, YouTube evidence or actual LLM execution."}
    _write(target,receipt)
    return {"skill_id":skill,"status":receipt["status"],"receipt_sha256":digest(target),
            "output_files":list(outputs),"production_authorized":False}

def require_stage_ready(base,stage,manifest):
    """Called from the SAME existing Script Factory advance() and status(), not a second runner."""
    if manifest.get("mode")!=MODE:
        return
    if stage not in STAGES: raise ValueError("Unknown stage")
    root=ROOT
    graph=read_graph(root)
    byid=_node_map(graph)
    for node in graph["nodes"]:
        if node["stage"]!=stage or not node["enabled_by_default"]:
            continue
        status=receipt_status(pathlib.Path(base),node,graph)
        if status["status"]!="HANDOFF_RECORDED":
            raise ValueError("Missing/stale master skill handoff "+node["id"]+": "+status.get("reason",status["status"]))
    # The existing Script Factory still checks all specialized stage artifacts,
    # input provenance, actual independent reviewer evidence and SHA-bound Script Lock.

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("command",choices=["status","next","record"])
    p.add_argument("--repo",type=pathlib.Path,default=ROOT)
    p.add_argument("--storage-root",type=pathlib.Path)
    p.add_argument("--id",required=True,help="Existing CINE Script Factory episode id")
    p.add_argument("--skill")
    p.add_argument("--actor")
    a=p.parse_args(argv)
    try:
        if a.command=="record":
            result=record(a.repo,a.id,a.skill or "",a.actor or "",a.storage_root)
        else:
            result=scan(a.repo,a.id,a.storage_root)
            if a.command=="next":
                result={"episode_id":a.id,"next":result["next"],"recorded_handoffs":result["recorded_handoffs"],
                        "stage_gates":result["stage_gates"],"production_authorized":False}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (OSError,KeyError,ValueError,TypeError,json.JSONDecodeError) as exc:
        print(json.dumps({"status":"BLOCKED","error":str(exc),"production_authorized":False},ensure_ascii=False))
        return 2
if __name__=="__main__":
    raise SystemExit(main())
