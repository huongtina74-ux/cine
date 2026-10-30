#!/usr/bin/env python3
"""CINE Bell & Leaf: Script Factory reviewed script -> existing 10s Shot Director.

Read-only intake until the exact current script SHA, specialist stage gates
and attached director shot map agree. Even a successful run DOES NOT authorize
rendering, paid API calls, voice cloning, publishing, or artistic sign-off.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import sys
from types import SimpleNamespace

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"tools"))
import cf_script_factory as factory
from cf_a2_story_contract import _relative
from scripts.slow_english_a2_preflight import run as compile_shots

def _json(p):
    return json.loads(p.read_text(encoding="utf-8"))
def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def prepare(repo_root,project_id,output_dir,project_storage_root=None):
    repo_root=pathlib.Path(repo_root).resolve()
    storage=pathlib.Path(project_storage_root).resolve() if project_storage_root else repo_root/"data/script_factory/projects"
    project=factory.project_dir(project_id,storage).resolve()
    if not project.is_dir():
        raise ValueError("Canonical CINE Script Factory episode not found")
    manifest=_json(project/"manifest.json")
    if manifest.get("project_id")!=project_id or manifest.get("niche_id")!="magical_witch_family_stories" or manifest.get("mode")!="A2_ANIMATED_SCREENPLAY":
        raise ValueError("Not an original Bell & Leaf A2 animated screenplay")
    # We do not rely on script_ready_for_production (intentionally always false).
    # All eight structural stage events must pass, including SHA-bound source evidence.
    state=factory.status(SimpleNamespace(root=storage,id=project_id))
    if not state.get("structural_stage_gates_passed") or any(v!="PASS" for v in state["stages"].values()):
        raise ValueError("Full research→story→A2 script→independent review→script lock stage gates not passed")
    current=_sha(project/"06_script/script.md")
    handoff=_json(project/"08_final/shot_handoff.json")
    if handoff.get("project_id")!="slow_english_a2_bell_leaf" or handoff.get("subniche_id")!="magical_witch_family_stories":
        raise ValueError("Cross-subniche director handoff not permitted")
    if handoff.get("script_sha256")!=current:
        raise ValueError("Director source screenplay has changed since script review")
    if handoff.get("narrator_allowed") is not False or handoff.get("shot_duration_seconds")!=10:
        raise ValueError("Bell & Leaf must be 10.0s per shot and without narrator")
    rel=handoff.get("shots_file")
    if not rel:
        raise ValueError("Approved episode shot-map relative path is missing")
    shots_path=(project.joinpath(*_relative(rel).parts)).resolve()
    if not shots_path.is_relative_to(project) or not shots_path.is_file():
        raise ValueError("Shot map is missing or escapes the canonical script project")
    if _sha(shots_path)!=handoff.get("shots_sha256"):
        raise ValueError("Shot map changed after approval")
    shots=_json(shots_path)
    if shots.get("project_id")!="slow_english_a2_bell_leaf":
        raise ValueError("Shot map belongs to a different production")
    if not isinstance(shots.get("shots"),list) or not shots["shots"] or handoff.get("shot_count")!=len(shots["shots"]):
        raise ValueError("Shot count missing or inconsistent")
    if any(s.get("duration_seconds")!=10 for s in shots["shots"]):
        raise ValueError("Every shot must be exactly 10.0s")
    # Existing CineFactory resolver checks real character identities, room/prop
    # geometry and voice, and blocks if any source has not been approved.
    result=compile_shots(repo_root,shots_path,pathlib.Path(output_dir).resolve())
    return {
        "project_id":"slow_english_a2_bell_leaf",
        "script_project_id":project_id,
        "script_sha256":current,
        "shot_map_sha256":_sha(shots_path),
        "stage_gates_passed":True,
        "director_reference_status":result["reference_preflight_status"],
        "shot_count":result["shot_count"],
        "source_hashes_verified":True,
        "production_authorized":False,
        "media_generated":0,
        "note":"Only read-only director reference prompts and QC report created; original audio/film assets still need independent approval"
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo",type=pathlib.Path,default=ROOT)
    p.add_argument("--id",required=True,help="Existing Script Factory episode ID")
    p.add_argument("--out",type=pathlib.Path,required=True)
    p.add_argument("--storage-root",type=pathlib.Path)
    args=p.parse_args()
    try:
        result=prepare(args.repo,args.id,args.out,args.storage_root)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,FileNotFoundError,KeyError,OSError) as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc),"production_authorized":False},ensure_ascii=False))
        raise SystemExit(2)
if __name__=="__main__":
    main()
