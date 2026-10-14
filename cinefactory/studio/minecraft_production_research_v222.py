"""v222 research conference: actual Minecraft art receipts + external tool evidence.

This module never downloads competitor footage, marks a public case as fully
reviewed, renders shots, approves paid usage or modifies production recipes.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any
import json

import yaml

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT/"config/niches/minecraft/research_backlog_v222.yaml"
EXPECTED_SCHEMA = "cine.minecraft.production_research.v222"


def load_minecraft_research_board() -> dict[str, Any]:
    board = yaml.safe_load(BOARD.read_text(encoding="utf-8"))
    if not isinstance(board, dict) or board.get("schema")!=EXPECTED_SCHEMA:
        raise ValueError("UNSUPPORTED_MINECRAFT_BOARD")
    safety=board["policy"]
    if any(safety[x] is not False for x in (
        "report_actual_full_competitor_viewing",
        "paid_generation_credits_authorized",
        "import_competitor_skins_or_scripts",
        "change_active_blender_worker",
        "publish_approval",
    )):
        raise ValueError("MINECRAFT_UNVERIFIED_RESEARCH_MUST_NOT_PROMOTE")
    if board["pilot_plan"]["allow_production_promotion"] is not False:
        raise ValueError("UNVERIFIED_MINECRAFT_PILOT_CANNOT_DEPLOY")
    cases=board["competitor_cases"]
    if len(cases)!=3 or len({x["id"] for x in cases})!=3:
        raise ValueError("MINECRAFT_RESEARCH_CASES_MISSING")
    if any(x["full_video_and_audio_inspected"] or
           x["exact_production_tool_verified"] for x in cases):
        raise ValueError("CANNOT_ASSERT_UNWATCHED_COMPETITOR_VIDEOS")
    tech=board["technology_study"]
    if len(tech)<7 or len({x["id"] for x in tech})!=len(tech):
        raise ValueError("INCOMPLETE_MINECRAFT_TECH_STUDY")
    if any(x.get("production_quality_qualified") for x in tech):
        raise ValueError("MINECRAFT_UNQUALIFIED_TOOL_CANNOT_BE_ACTIVE")
    shots=board["pilot_plan"]["shot_beats"]
    if not 8<=len(shots)<=18 or len({x["id"] for x in shots})!=len(shots):
        raise ValueError("MINECRAFT_PILOT_SHOTS_INVALID")
    if sum(x["seconds"] for x in shots)!=board["pilot_plan"]["duration_seconds"]:
        raise ValueError("MINECRAFT_SHOT_TIMING_NOT_LOCKED")
    if board["pilot_plan"]["target_resolution"] != [1920,1080] or board["pilot_plan"]["fps"]<24:
        raise ValueError("MINECRAFT_PILOT_MUST_BE_TRUE_1080P24")
    return board


def _file_status(path: str, expected_hash: str|None=None) -> dict:
    base = (ROOT/path).resolve()
    if not base.is_relative_to(ROOT.resolve()):
        raise ValueError("MINECRAFT_EVIDENCE_PATH_OUTSIDE_ROOT")
    exists=base.is_file()
    actual_hash=sha256(base.read_bytes()).hexdigest() if exists and expected_hash else None
    return {
        "relative_path":path,"exists":exists,
        "verified_sha256":actual_hash,
        "sha256_matches_receipt":bool(exists and expected_hash and actual_hash==expected_hash),
    }


def minecraft_research_conference() -> dict:
    board=load_minecraft_research_board()
    baseline=board["local_baseline"]
    pilot=_file_status(baseline["relative_video"],baseline["video_sha256"])
    receipt=_file_status(baseline["relative_receipt"])
    audit=_file_status(baseline["relative_art_qc"])
    screenshot=_file_status(baseline["relative_storyboard"])
    blockers=[]
    if audit["exists"]:
        data=json.loads((ROOT/baseline["relative_art_qc"]).read_text(encoding="utf-8"))
        gate=data.get("v197_art_gate",{})
        blockers=gate.get("hard_blockers",[])
        old_gate_status=gate.get("decision","UNKNOWN")
    else:
        old_gate_status="MISSING_ART_QC_SOURCE"
    tech=board["technology_study"]
    cases=board["competitor_cases"]
    return {
        "schema":"cine.minecraft.production_research_summary.v222",
        "date":board["date"],
        "status":"RESEARCH_IN_PROGRESS_NOT_PRODUCTION_READY",
        "scope":"FIRST_PARTY_ORIGINAL_ANIMATION_RESEARCH",
        "existing_render_video":{
            **pilot,
            "has_original_receipt":receipt["exists"],
            "has_art_qc_report":audit["exists"],
            "has_three_shot_contact_sheet":screenshot["exists"],
            "duration_seconds":baseline["duration_seconds"],
            "fps":baseline["fps"],
            "resolution":baseline["resolution"],
            "art_review":old_gate_status,
            "recorded_blocker_count":len(blockers),
            "recorded_blockers":blockers,
        },
        "competitor_research":[{
            "id":r["id"],"channel":r["channel"],"url":r["url"],
            "public_metadata_seen":r["public_metadata_seen"],
            "full_video_and_audio_inspected":False,
            "exact_production_tool_verified":False,
            "research_questions":r["research_questions"],
        } for r in cases],
        "reviewed_technology_candidates":[{
            "id":t["id"],"role":t["role"],"priority":t["priority"],
            "source":t["source"],"installed_checked":t["installed_and_version_checked"],
            "production_qualified":False,"next_gate":t["gate"],
        } for t in tech],
        "tool_priorities":dict(Counter(t["priority"] for t in tech)),
        "pilot_story":board["pilot_plan"]["title"],
        "pilot_intents":board["pilot_plan"]["shot_beats"],
        "pilot_seconds":board["pilot_plan"]["duration_seconds"],
        "pilot_target":"1920x1080@24fps",
        "pipeline_approval":False,
        "paid_ai_authorized":False,
        "actual_competitor_full_video_evidence":False,
        "future_minecraft_8min_breakout_validated":False,
    }


def original_minecraft_pilot_storyboard() -> dict:
    board=load_minecraft_research_board()
    plan=board["pilot_plan"]
    when=0
    beats=[]
    for shot in plan["shot_beats"]:
        beats.append({
            "shot_id":shot["id"],
            "start_seconds":when,"end_seconds":when+shot["seconds"],
            "action":shot["beat"],"camera":shot["camera"],
            "required_capabilities":shot["needs"],
            "rendered_and_reviewed":False,
        })
        when+=shot["seconds"]
    return {
        "schema":"cine.minecraft.storyboard_plan.v222",
        "title":plan["title"],"format":"ORIGINAL_MINECRAFT_STYLE_3D",
        "duration_seconds":when,"shot_count":len(beats),
        "shots":beats,"gates":plan["gated_stages"],
        "publishable":False,"has_real_45_second_media":False,
        "cost_approved":False,
    }
