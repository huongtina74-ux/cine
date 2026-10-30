"""CINE existing Script Factory A2 specialized skill DAG + evidence gate.

The tool verifies actual files and declared contracts, not that LLMs were run or
that a human truly provided consent/signature. Do NOT grant production permission.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
from typing import Any

GRAPH="config/story_factory/a2_bell_leaf_skill_graph.json"
EXPECTED_TAG="magical_witch_family_stories"
STAGES=("research","insights","concepts","story","outline","script","review","final")
def read(root: pathlib.Path):
    return json.loads((root/GRAPH).read_text(encoding="utf-8"))
def _relative(path):
    p=pathlib.PurePosixPath(path)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError("Illegal project-relative artifact path: "+str(path))
    return p
def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))
def _has_proof(rec, base, digest, writer):
    if rec.get("verdict")!="PASS" or rec.get("reviewed_script_sha256")!=digest:
        raise ValueError("A2 reviewer verdict does not match current script SHA")
    if not rec.get("reviewer_id") or rec.get("reviewer_id")==writer:
        raise ValueError("A2 reviewer must be independently identified")
    if not isinstance(rec.get("evidence_notes"),list) or not rec["evidence_notes"]:
        raise ValueError("A2 reviewer evidence notes missing")
    rel=rec.get("evidence_file")
    if not rel or not rec.get("evidence_sha256"):
        raise ValueError("External evidence attachment and hash required")
    path=(base.joinpath(*_relative(rel).parts)).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file() or _digest(path)!=rec["evidence_sha256"]:
        raise ValueError("Evidence file missing or changed")
def validate_graph(root, factory=None):
    root=pathlib.Path(root)
    g=read(root)
    if (g.get("mode"),g.get("project_id"),g.get("niche_id")) != (
       "A2_ANIMATED_SCREENPLAY","slow_english_a2_bell_leaf",EXPECTED_TAG):
        raise ValueError("Wrong Bell & Leaf project/taxonomy in skill graph")
    if g.get("stage_order")!=list(STAGES):
        raise ValueError("Incorrect CINE eight-stage ordering")
    if factory and factory.get("specializations",{}).get("A2_ANIMATED_SCREENPLAY",{}).get("niche_id")!=EXPECTED_TAG:
        raise ValueError("Script Factory A2 mode does not match research subniche")
    nodes=g.get("nodes",[])
    names=[n["id"] for n in nodes]
    if len(names)!=21 or len(set(names))!=21:
        raise ValueError("Exactly 21 original specialist skill roles required")
    roles={n["id"]:n for n in nodes}
    found=set();outputs=set()
    for n in nodes:
        if n["stage"] not in STAGES: raise ValueError("Unknown stage "+n["id"])
        if n["id"] in found: raise ValueError("Skill duplicated")
        skill=_relative(n["skill_file"])
        path=root.joinpath(*skill.parts)
        if not path.is_file() or n["id"] not in path.read_text(encoding="utf-8"):
            raise ValueError("Declared skill file missing or wrong: "+n["id"])
        for dep in n["requires"]:
            if dep not in roles or dep not in found:
                raise ValueError("Dependency unavailable before skill: "+n["id"]+" -> "+dep)
            if STAGES.index(roles[dep]["stage"])>STAGES.index(n["stage"]):
                raise ValueError("Backward cross-stage dependency "+n["id"])
        for rel in n["outputs"]:
            _relative(rel)
            if rel in outputs: raise ValueError("Output artifact has multiple owners: "+rel)
            outputs.add(rel)
        found.add(n["id"])
    if {n["id"] for n in nodes if not n["enabled_by_default"]}!={"s09-anthology-architect"}:
        raise ValueError("Only anthology architect is opt-in for Bell & Leaf")
    return {"status":"SKILL_GRAPH_CONNECTED_SOURCE_ONLY","node_count":len(nodes),
            "edge_count":sum(len(n["requires"]) for n in nodes),
            "output_file_count":len(outputs),"model_execution_verified":False,
            "independent_story_quality_qualified":False}
def required_artifacts(root,stage):
    g=read(pathlib.Path(root))
    if stage not in STAGES: raise ValueError("Unknown stage")
    files=[f for n in g["nodes"] if n["stage"]==stage and n["enabled_by_default"] for f in n["outputs"]]
    if stage=="review": files.extend(g["required_independent_reviews"])
    if stage=="final": files.extend(g["final_handoff"])
    return files
def validate_a2_stage(base,stage,manifest):
    base=pathlib.Path(base).resolve()
    if manifest.get("mode")!="A2_ANIMATED_SCREENPLAY": return
    if manifest.get("niche_id")!=EXPECTED_TAG:
        raise ValueError("A2 evidence from a different research subniche")
    if not 30<=manifest.get("target_minutes",0)<=50:
        raise ValueError("Bell & Leaf is a 30–50 minute episode, not audio-story 60 minute mode")
    if stage=="research":
        evidence=_json(base/"01_research/evidence.json")
        if evidence.get("niche_id")!=EXPECTED_TAG:
            raise ValueError("Research evidence cohort is not magical family stories")
        sources=evidence.get("sources",[])
        if not sources or not all(
            isinstance(s,dict) and s.get("url") and s.get("observed_at_utc")
            and s.get("evidence_type") in ("METADATA_ONLY","TRANSCRIPT_REVIEWED","AUDIO_REVIEWED","VIDEO_REVIEWED","FULL_AV_REVIEWED")
            for s in sources):
            raise ValueError("Source evidence URL/date/modality must be recorded; no invented full-video review")
    elif stage=="story":
        story=_json(base/"04_story/story_dna.json")
        if story.get("series_id")!="bell_leaf" or story.get("project_id")!="slow_english_a2_bell_leaf":
            raise ValueError("Story DNA must belong to Bell & Leaf, not another A2 show")
        for k in ("veylora_progression","a2_communication_objectives","episode_id","series_canon_sha256"):
            if not story.get(k):raise ValueError("A2 series story DNA missing "+k)
    elif stage=="script":
        screenplay=(base/"06_script/screenplay.fountain").read_text(encoding="utf-8")
        if len(screenplay.strip())<1200:
            raise ValueError("Screenplay is just an outline, not a complete production script")
        if "NARRATOR" in screenplay.upper():
            raise ValueError("Bell & Leaf has no narrator")
    elif stage=="review":
        script_sha=_digest(base/"06_script/script.md")
        writer=manifest.get("writer_id")
        for rel in ("07_review/a2_review.json","07_review/canon_review.json"):
            _has_proof(_json(base/rel),base,script_sha,writer)
        clock=_json(base/"07_review/timed_read.json")
        _has_proof(clock,base,script_sha,writer)
        if clock.get("measurement_method") not in ("REAL_TABLE_READ","REAL_VOICE_WAV_MEASURED") or not 1800<=clock.get("measured_seconds",0)<=3000:
            raise ValueError("Actual 30-50 minute timing not measured")
        if _json(base/"07_review/a2_review.json").get("human_a2_comprehension_result")!="PASS":
            raise ValueError("A2 learner/human comprehension evidence not approved")
        if _json(base/"07_review/canon_review.json").get("series_canon_result")!="PASS":
            raise ValueError("Veylora/characters/location canon not independently approved")
    elif stage=="final":
        shot=_json(base/"08_final/shot_handoff.json")
        if shot.get("project_id")!="slow_english_a2_bell_leaf" or shot.get("subniche_id")!=EXPECTED_TAG:
            raise ValueError("Shot handoff routing wrong series/subniche")
        if shot.get("shot_duration_seconds")!=10 or shot.get("narrator_allowed") is not False:
            raise ValueError("Director shot handoff must be 10s/no narrator")
        if shot.get("script_sha256")!=_digest(base/"06_script/script.md"):
            raise ValueError("Director handoff script SHA does not match script lock")
def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo",type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1])
    p.add_argument("--project",type=pathlib.Path)
    a=p.parse_args()
    from cf_script_factory import config
    result=validate_graph(a.repo,config())
    if a.project:
        manifest=_json(a.project/"manifest.json")
        result["project_niche"]=manifest.get("niche_id")
        result["specialized_artifact_status"]={}
        for stage in STAGES:
            result["specialized_artifact_status"][stage]={
                p:(a.project.joinpath(*pathlib.PurePosixPath(p).parts)).is_file()
                for p in required_artifacts(a.repo,stage)}
        result["all_specialized_artifacts_present"]=all(all(x.values()) for x in result["specialized_artifact_status"].values())
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
