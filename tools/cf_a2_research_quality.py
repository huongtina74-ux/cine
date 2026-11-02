"""CINE Bell & Leaf research handoff quality gate.

This is a *structural and evidence-modality* gate, never a claim that an
agent actually watched video. Missing direct competitors can only be handled
by a separately approved alternative-cohort research policy (not enabled).
"""
from __future__ import annotations
import csv
import json
from pathlib import Path
from urllib.parse import urlparse

DIRECT = "DIRECT_MAGICAL_FAMILY"
CONTENT = {"TRANSCRIPT_REVIEWED","VIDEO_REVIEWED","FULL_AV_REVIEWED","AUDIO_REVIEWED"}
VIDEO = {"VIDEO_REVIEWED","FULL_AV_REVIEWED"}

def _load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError,ValueError):
        return {}

def inspect(base):
    base = Path(base)
    folder = base/"01_research"
    raw = _load(folder/"input_sources.json")
    register = _load(folder/"evidence_register.json")
    factory = _load(folder/"evidence.json")
    autopsy_path = folder/"story_autopsy.md"
    board = folder/"outlier_board.csv"
    reasons = []
    source_rows = raw.get("sources",[])
    items = register.get("items",[])
    if not isinstance(source_rows,list): source_rows=[]
    if not isinstance(items,list): items=[]
    if raw.get("subniche_id")!="magical_witch_family_stories" or not source_rows:
        reasons.append("R01_INPUT_SOURCES_MISSING_OR_WRONG_SUBNICHE")
    sources_by_url={}
    for s in source_rows:
        if not isinstance(s,dict):continue
        url=s.get("url","")
        p=urlparse(url)
        if p.scheme!="https" or not p.netloc or not s.get("observed_at_utc") or not s.get("method"):
            reasons.append("SOURCE_MISSING_URL_DATE_OR_METHOD")
            continue
        if s.get("peer_group") not in (DIRECT,"ADJACENT_SLOW_ENGLISH","OTHER_CONTEXT"):
            reasons.append("SOURCE_PEER_GROUP_INVALID")
        sources_by_url[url]=s
    accepted=[]
    for item in items:
        if not isinstance(item,dict):continue
        src=sources_by_url.get(item.get("url"))
        if src is None:
            reasons.append("R01_REGISTER_HAS_UNGROUNDED_SOURCE")
            continue
        if item.get("observed_at_utc")!=src.get("observed_at_utc"):
            reasons.append("R01_REGISTER_OBSERVATION_MISMATCH")
        if item.get("peer_group")!=src.get("peer_group"):
            reasons.append("R01_REGISTER_COHORT_MISMATCH")
        if item.get("evidence_type")!=src.get("evidence_type"):
            reasons.append("R01_REGISTER_MODALITY_MISMATCH")
        accepted.append(item)
    if not accepted:
        reasons.append("R01_REGISTER_EMPTY_OR_UNGROUNDED")
    direct={x.get("url") for x in accepted if x.get("peer_group")==DIRECT}
    if len(direct)<2:
        reasons.append("INSUFFICIENT_DIRECT_MAGICAL_FAMILY_PEERS:"+str(len(direct))+"/2")
    av={x.get("url") for x in accepted if x.get("evidence_type") in VIDEO}
    if not av:
        reasons.append("NO_ORIGINAL_VIDEO_CONTENT_REVIEW_EVIDENCE")
    # Transcripts may improve writing but cannot justify claims about edits,
    # visual beats, staging or viewer retention.
    if not any(x.get("evidence_type") in CONTENT for x in accepted):
        reasons.append("NO_CONTENT_REVIEW_BEYOND_METADATA")
    if register.get("direct_peer_status","").startswith("BLOCKED") or register.get("handoff_status","").startswith("PARTIAL"):
        reasons.append("R01_SELF_DECLARED_INCOMPLETE")
    if factory:
        if factory.get("niche_id")!="magical_witch_family_stories":
            reasons.append("FACTORY_RESEARCH_COHORT_WRONG")
        refs={x.get("url") for x in factory.get("sources",[]) if isinstance(x,dict)}
        if refs!=set(sources_by_url):
            reasons.append("FACTORY_EVIDENCE_NOT_SAME_SOURCES_AS_R01")
    else:
        reasons.append("FACTORY_EVIDENCE_JSON_NOT_DERIVED_FROM_R01")
    if board.is_file():
        with board.open(encoding="utf-8-sig",newline="") as f:
            try: outliers=list(csv.DictReader(f))
            except csv.Error:outliers=[]
        referenced={x.get("url") for x in outliers if x.get("url")}
        if referenced and not referenced.issubset(set(sources_by_url)):
            reasons.append("OUTLIER_BOARD_URL_NOT_IN_R01_SOURCES")
        if not outliers: reasons.append("R04_OUTLIER_TABLE_EMPTY")
    else:
        reasons.append("R04_OUTLIER_TABLE_MISSING")
    if not autopsy_path.is_file():
        reasons.append("R05_STORY_AUTOPSY_MISSING")
    else:
        content=autopsy_path.read_text(encoding="utf-8")
        if "status: BLOCKED" in content or "cannot be completed" in content.lower():
            reasons.append("R05_STORY_AUTOPSY_ADMITTED_BLOCKED")
        if len(content.strip())<500:reasons.append("R05_STORY_AUTOPSY_TOO_SHORT")
    return {
        "status":"BLOCKED" if reasons else "EVIDENCE_STRUCTURALLY_REVIEWABLE",
        "reasons":list(dict.fromkeys(reasons)),
        "source_count":len(sources_by_url),
        "direct_peer_count":len(direct),
        "video_review_claim_count":len(av),
        "manual_verification_still_required":True,
        "actual_av_watch_proven":False,
        "human_review_authenticated":False,
        "production_authorized":False,
    }

def require_research_ready(base):
    report=inspect(base)
    if report["status"]!="EVIDENCE_STRUCTURALLY_REVIEWABLE":
        raise ValueError("A2_RESEARCH_QUALITY_BLOCKED: "+", ".join(report["reasons"]))
    return report

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--project-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(inspect(a.project_dir),indent=2,ensure_ascii=False))
