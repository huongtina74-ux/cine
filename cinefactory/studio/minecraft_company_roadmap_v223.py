"""v223 — one step-by-step Minecraft company production research contract.

Public YouTube descriptions and reported snapshots are not decoded video
observations. All 26 departments and 28 gates are mapped with clear owners.
No internet, OS command, render, upload, creator impersonation, paid call or
external MCP execution is exposed by this planning API.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
import json
from typing import Any

from cinefactory.studio.contracts import DepartmentId

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"config/niches/minecraft/master_company_plan_v223.json"
ALLOWED_LANES=frozenset(("SCRIPTED_MINECRAFT_GAMEPLAY","AUTHORED_VOXEL_3D_ANIMATION"))
PHASES=("RESEARCH","GREENLIGHT","STORY","PREPRO","PRODUCTION","POST","QC","RELEASE","LEARN")
REQUIRED_REFERENCES={
    "maizen_choose_right_hole_2026",
    "maizen_house_inside_bed_2025",
    "bigschool_season3_compilation_2020",
}

def load_minecraft_master_company_plan() -> dict[str,Any]:
    content=json.loads(SOURCE.read_text(encoding="utf-8"))
    if content.get("schema")!="cine.minecraft.two_lane_master_production.v223":
        raise ValueError("MINECRAFT_MASTER_SCHEMA_MISMATCH")
    policy=content.get("policy",{})
    if (policy.get("owner_credit_budget_usd")!=0 or
        policy.get("benchmark_quality_before_speed") is not True or
        any(policy.get(x) is not False for x in (
            "allow_third_party_mcp_auto_install","allow_competitor_asset_reproduction",
            "allow_autopublish","allow_backends_promotion_without_pilot"
        ))):
        raise ValueError("UNSAFE_MINECRAFT_COMPANY_RESEARCH")
    lanes=content["lanes"]
    if len(lanes)!=2 or {x["id"] for x in lanes}!=ALLOWED_LANES:
        raise ValueError("MINECRAFT_PRODUCTION_LANES_MISSING")
    for lane in lanes:
        if lane["media_ready"] or lane["minimum_pilot_seconds"]<30:
            raise ValueError("MINECRAFT_LANE_UNVERIFIED_READY")
    depts=content["departments"]
    expected={x.value for x in DepartmentId}
    if len(depts)!=26 or {x["id"] for x in depts}!=expected:
        raise ValueError("MINECRAFT_DEPARTMENTS_NOT_COVERED")
    if [r["sequence"] for r in depts]!=list(range(1,27)):
        raise ValueError("MINECRAFT_DEPARTMENT_SEQUENCE_INVALID")
    steps=content["master_steps"]
    if len(steps)!=28 or [s["step_id"] for s in steps]!=[
        "G"+str(i).zfill(2) for i in range(1,29)
    ]:
        raise ValueError("MINECRAFT_MASTER_STEP_COUNT_ORDER")
    if {s["phase"] for s in steps}!=set(PHASES):
        raise ValueError("MINECRAFT_MASTER_PHASES_INCOMPLETE")
    if any(s["owner"] not in expected or
           not set(s["support"]).issubset(expected) or
           not s["receipt"] or not s["blocking_acceptance"] or
           s["execution_status"]!="NOT_EXECUTED_IN_THIS_RESEARCH_PASS"
           for s in steps):
        raise ValueError("MINECRAFT_STEP_EVIDENCE_MISSING")
    references=content["reference_videos"]
    if len(references)!=3 or {r["id"] for r in references}!=REQUIRED_REFERENCES:
        raise ValueError("MINECRAFT_SOURCE_CASES_MISSING")
    for r in references:
        u=urlparse(r["url"])
        if (u.scheme!="https" or u.hostname!="www.youtube.com"
            or not u.path.startswith("/watch")
            or r["lane"] not in ALLOWED_LANES
            or r["viewed_full_video"] or r["heard_full_audio"]
            or not r["source_urls"]):
            raise ValueError("MINECRAFT_PUBLIC_METADATA_MUST_NOT_FAKE_WATCH")
    queue=content["original_video_queue"]
    if len(queue)!=6 or len({r["id"] for r in queue})!=6:
        raise ValueError("MINECRAFT_ORIGINAL_VIDEO_QUEUE_MISSING")
    if any(x["lane"] not in ALLOWED_LANES or
           x["status"] not in ("ORIGINAL_PITCH_NOT_PRODUCED","STORYBOARD_ONLY_45S")
           for x in queue):
        raise ValueError("MINECRAFT_ORIGINAL_CONTENT_NOT_READY")
    program=content["stage_program"]
    if len(program)!=6 or any(p["state"] in ("READY","APPROVED","RELEASED") for p in program):
        raise ValueError("MINECRAFT_UNQUALIFIED_STAGE")
    return content


def minecraft_company_roadmap(lane:str|None=None,phase:str|None=None) -> dict:
    if lane is not None and lane not in ALLOWED_LANES:
        raise ValueError("UNKNOWN_MINECRAFT_LANE")
    if phase is not None and phase not in PHASES:
        raise ValueError("UNKNOWN_MINECRAFT_PHASE")
    d=load_minecraft_master_company_plan()
    from .minecraft_source_evidence_v224 import minecraft_g01_g02_evidence
    newer=minecraft_g01_g02_evidence()
    latest={x["video_id"]:x for x in newer["case_metadata"]}
    steps=[r for r in d["master_steps"] if phase is None or r["phase"]==phase]
    videos=[r for r in d["original_video_queue"] if lane is None or r["lane"]==lane]
    refs=[r for r in d["reference_videos"] if lane is None or r["lane"]==lane]
    maizen_kickoff = None
    if lane in (None, "SCRIPTED_MINECRAFT_GAMEPLAY"):
        from .maizen_studio_kickoff_v225 import maizen_studio_status
        maizen_kickoff = maizen_studio_status()
    maizen_full_review = None
    if lane in (None, "SCRIPTED_MINECRAFT_GAMEPLAY"):
        from .maizen_full_video_gate_v227 import maizen_full_video_review_gate
        maizen_full_review = maizen_full_video_review_gate()
    maizen_method_correction = None
    if lane in (None, "SCRIPTED_MINECRAFT_GAMEPLAY"):
        from .maizen_method_review_v226 import maizen_production_method_audit
        maizen_method_correction = maizen_production_method_audit()
    return {
        "schema":"cine.minecraft.company_roadmap.v223",
        "lane":lane,"phase":phase,
        "all_departments":len(d["departments"]),
        "all_steps":len(d["master_steps"]),
        "stage_program":d["stage_program"],
        "maizen_selected_studio_a_kickoff":maizen_kickoff,
        "maizen_production_method_correction":maizen_method_correction,
        "maizen_mandatory_full_video_review_gate":maizen_full_review,
        "g01_g02_source_evidence":{
            "snapshot_date":newer["snapshot_date"],
            "public_video_metadata_count":newer["verified_public_video_count"],
            "sampled_thumbnail_video_count":len(newer["visual_preview_reports"]),
            "g01":newer["phase_g01_status"],
            "g02":newer["phase_g02_status"],
            "full_video_audio_watches":0,
            "breakout_0_30d_2x_1m_14d_verified":0,
        },
        "lane_specs":[x for x in d["lanes"] if lane is None or x["id"]==lane],
        "referenced_video_metadata":[
            {"id":r["id"],"title":r["title"],"channel":r["channel"],
             "url":r["url"],"upload_date":r["published_date"],
             "reported_views_historical_v223":r["reported_views"],
             "reported_duration_seconds_historical_v223":r["reported_duration_seconds"],
             "verified_direct_2026_10_10_view_count":latest.get(r["url"].split("v=")[-1],{}).get("views_at_snapshot"),
             "verified_direct_2026_10_10_duration_seconds":latest.get(r["url"].split("v=")[-1],{}).get("duration_seconds"),
             "duration_provenance":r["duration_provenance"],
             "public_description_summary":r["description_summary"],
             "public_chapters":r.get("public_description_chapters",[]),
             "hypotheses_not_observations":r["creative_mechanic_hypotheses"],
             "questions_before_adopting":r["study_questions"],
             "full_video_watched":False,"full_audio_heard":False,
             "visual_timestamps_verified":False}
            for r in refs
        ],
        "original_video_ideas":videos,
        "ordered_steps":[{
            **s,
            "maizen_full_source_analysis_gate_blocks_stage":bool(
                maizen_full_review is not None
                and not maizen_full_review["cohort_gate_passed"]
                and s["step_id"] not in ("G01","G02")
            ),
        } for s in steps],
        "paid_credits_authorized":False,
        "production_execution_qualified":False,
        "publication_authorized":False,
        "competitor_exact_software_verified":False,
    }


def minecraft_next_approved_step(lane:str) -> dict:
    if lane not in ALLOWED_LANES:
        raise ValueError("UNKNOWN_MINECRAFT_LANE")
    d=load_minecraft_master_company_plan()
    from .minecraft_source_evidence_v224 import minecraft_g01_g02_evidence
    progress=minecraft_g01_g02_evidence()
    full_watch=None
    if lane=="SCRIPTED_MINECRAFT_GAMEPLAY":
        from .maizen_full_video_gate_v227 import maizen_full_video_review_gate
        full_watch=maizen_full_video_review_gate()
    relevant=[x for x in d["reference_videos"] if x["lane"]==lane]
    # G01 is not passed until official video durations, metadata and negative
    # controls have been independently corroborated. G02 needs actual media.
    return {
        "schema":"cine.minecraft.first_blocking_step.v223",
        "lane":lane,"current_step":"G01",
        "status":"BLOCKED_PENDING_AGE_14DAY_VELOCITY_AND_CONTROL_COHORT",
        "requires_real_footage":True,
        "maizen_full_watch_blocks_G03_onward":bool(full_watch is not None and not full_watch["cohort_gate_passed"]),
        "maizen_full_watch_gate":full_watch,
        "current_public_metadata_status":progress["phase_g01_status"],
        "current_thumbnail_sample_status":progress["phase_g02_status"],
        "known_video_count":len(relevant),
        "needed_video_urls":[x["url"] for x in relevant],
        "studio_technical_pilot_status": (
            "EXISTING_TWO_SECOND_LOW_QUALITY_BLENDER_BASELINE"
            if lane=="AUTHORED_VOXEL_3D_ANIMATION"
            else "NO_AUTHENTIC_MINECRAFT_RUNTIME_CAPTURE_ACCEPTED"
        ),
        "may_proceed_with_original_story_and_asset_experiments":bool(
            full_watch is None or full_watch["cohort_gate_passed"]
        ),
        "may_claim_competitor_video_watched":False,
        "may_publish_full_episode":False,
        "next_approval":"SOURCE_VIDEO_ACCESS_THEN_ARTIST_QUALITY_PILOT",
    }
