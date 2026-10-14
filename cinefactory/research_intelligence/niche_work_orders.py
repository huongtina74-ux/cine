"""Generate source-linked research work orders from a niche's daily watch report.

A work order is an assignment, not evidence that a movie was watched or that
competitor success has been causally explained. Source snapshots remain locked.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def create_niche_work_orders(watch_file:str|Path, out_file:str|Path,
                             *, max_per_lane:int=6)->dict:
    if not 1<=max_per_lane<=30:
        raise ValueError("Per-lane budget must be 1 to 30")
    path=Path(watch_file).resolve(strict=True)
    report=json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema")!="cine.niche.watch_report.v1":
        raise ValueError("Research work orders require canonical pod watch evidence")
    items=report.get("videos",[])
    if not isinstance(items,list):
        raise ValueError("Watch video list must be present")
    unique=set()
    for item in items:
        if not isinstance(item,dict) or not item.get("video_id"):
            raise ValueError("Malformed source video")
        if item["video_id"] in unique:
            raise ValueError("Duplicate video ID in research watch source")
        unique.add(item["video_id"])
    lanes={
        "leader_historic_and_new":[v for v in items if v.get("million_sub_leader") is True],
        "newcomer_breakout":[v for v in items if v.get("newcomer") is True and v.get("views",0)>=100000],
        "fresh_trends_0_15d":[v for v in items if v.get("age_days",-1)>=0
                              and v.get("age_days")<=15 and v.get("views",0)>=100000],
    }
    tasks=[]
    for lane, rows in lanes.items():
        sorted_rows=sorted(rows,key=lambda v:(
            -int(v.get("alert") is not None),
            -(v.get("view_velocity_per_hour") or 0),
            -v.get("views",0),v["video_id"]))
        for v in sorted_rows[:max_per_lane]:
            task={
                "work_id":lane+"--"+v["video_id"],
                "lane":lane,"video_id":v["video_id"],
                "video_url":v.get("video_url"),
                "channel_id":v["channel_id"],
                "metadata_as_of":report["as_of"],
                "source_watch_sha256":_sha(path),
                "views_observed":v.get("views"),"age_days_at_source":v.get("age_days"),
                "outlier_ratio":v.get("outlier_ratio"),
                "outlier_sample_size":v.get("age_matched_sample_count"),
                "trend_signal":v.get("alert"),
                "evidence_status":v.get("evidence_status","UNKNOWN"),
                "full_video_semantics_status":"NOT_OBSERVED",
                "source_media_rights_status":"NOT_CLEARED",
                "tasks":[
                    "Establish actual authorized video/audio access and exact timecodes",
                    "Script room: hook, motivations, stakes, setup-payoff, unique plot structure",
                    "Director: blocking, character eye-lines, camera coverage and emotional framing",
                    "Animation: rig/identity, expression/acting, motion timing, prop/physics interaction",
                    "Art and sound: world/lighting/color/VFX/foley/voice/music and continuity",
                    "Editor: actual cut pacing, J/L transitions, reaction holds and audio bridges",
                    "Packaging: title/thumbnail promise and video payoff",
                    "Challenge hypothesis with weak in-niche controls; originality and rights review",
                    "Tool scout: choose original scene pilot options, measure quality + accepted sec/h",
                ],
                "production_permission":False,
            }
            tasks.append(task)
    count={k:sum(item["lane"]==k for item in tasks) for k in lanes}
    result={
        "schema":"cine.niche.work_orders.v1","state":"PENDING_AUTHORIZED_MULTIMODAL_RESEARCH",
        "watch_source":str(path),"watch_source_sha256":_sha(path),
        "niche_id":report["niche_id"],"watch_time":report["as_of"],
        "lane_tasks":tasks,"lane_counts":count,
        "empty_lanes":[k for k,v in count.items() if v==0],
        "full_video_content_extracted":False,
        "actual_footage_access_granted":False,
        "channel_approved_by_this_generator":False,
        "tool_bakeoff_completed":False,
        "production_permission":False,
        "notes":[
            "One video may be in multiple research lanes; one semantic dossier can serve linked work orders",
            "Sub-million newcomer videos are scouting leads, NOT proof of new channel breakout",
            "Do not invent age, view velocity, script, camera, CTR, RPM or private retention",
            "A missing leader/newcomer/trend lane remains EMPTY rather than fabricated",
        ],
    }
    target=Path(out_file)
    if target.exists():raise FileExistsError("Immutable research work order already exists")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
