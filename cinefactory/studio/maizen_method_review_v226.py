"""v226: evidence-backed correction of the Maizen-style production hypothesis.

Maizen's official hiring site demonstrates Minecraft recording/command skills,
NOT spontaneous unscripted gameplay and NOT proof every video uses that method.
The official marketplace adventure demonstrates designed playable game worlds.
Official OBJ downloads demonstrate only available models, not Blender render
usage. Keep v225 hash-bound historical desk receipts unchanged for audit.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
import json

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"config/niches/minecraft/maizen_production_reassessment_v226.json"
MODES=frozenset(("GAME_ENGINE_STAGED","BLENDER_AUTHORED","SCENE_HYBRID"))
SHOTS=tuple("P"+str(i).zfill(2) for i in range(1,10))

def load_maizen_method_review()->dict[str,Any]:
    d=json.loads(SOURCE.read_text(encoding="utf8"))
    if d.get("schema")!="cine.minecraft.maizen_directed_storytelling.v226":
        raise ValueError("MAIZEN_METHOD_REVIEW_SCHEMA")
    if d["project_id"]!="MAI01_WATERFALL" or d["production_default"]!="METHOD_UNDECIDED_COMPARE_STAGED_GAME_VS_OFFLINE_AUTHORED_CGI":
        raise ValueError("MAIZEN_SOURCE_METHOD_CANNOT_BE_PRESUMED")
    methods=d["methods"]
    if len(methods)!=3 or {m["id"] for m in methods}!=MODES:
        raise ValueError("MAIZEN_REQUIRED_PRODUCTION_CHOICES_MISSING")
    if any(m["status"]=="QUALIFIED" or
           not m["pilot_gate"] or not m["source_truth"] for m in methods):
        raise ValueError("MAIZEN_TOOLS_CANNOT_FAKE_QUALIFICATION")
    source=d["official_primary_sources"]
    if len(source)<4 or any(not x["uri"].startswith("https://maizen.com/")
                            for x in source if x["source_type"]=="MAIZEN_OFFICIAL"):
        raise ValueError("MAIZEN_OFFICIAL_EVIDENCE_MISSING")
    if not any(x["source_type"]=="COMMUNITY_ACCOUNT_NOT_VERIFIED_OFFICIAL" for x in source):
        raise ValueError("MAIZEN_COMMUNITY_EVIDENCE_LABEL_MISSING")
    shots=d["shot_candidates"]
    if len(shots)!=9 or tuple(x["id"] for x in shots)!=SHOTS:
        raise ValueError("MAIZEN_SHOT_PLANNING_MISSING")
    if any(x["first_pilot_method"] not in MODES or
           x["alternative_method"] not in MODES or
           x["method_qualified"] or x["real_media_exists"]
           for x in shots):
        raise ValueError("MAIZEN_SHOT_METHOD_PREMATURE")
    gate=d["stage_gates"]
    if (gate["game_install_required_for_all_methods"] or not gate["publish_blocked"]
        or not gate["study_source_is_partial"] or not gate["do_not_delete_old_v225_receipts"]
        or not gate["cinematic_quality_pilot_needed"]
        or gate["blender_v197_qc_blockers"]!=12
        or d["existing_video_samples"]["full_video_and_audio_watched"]
        or not d["no_auto_execute"]):
        raise ValueError("MAIZEN_FALSE_SOURCE_OR_RELEASE_CLAIM")
    return d

def maizen_production_method_audit() -> dict:
    d=load_maizen_method_review()
    from .maizen_full_video_gate_v227 import maizen_full_video_review_gate
    full_review=maizen_full_video_review_gate()
    return {
        "full_video_first_requirement":full_review,
        "competitor_method_conclusion_blocked":not full_review["cohort_gate_passed"],
        "any_method_promoted_to_production":False,
        "schema":"cine.minecraft.maizen_production_method_audit.v226",
        "project_id":d["project_id"],
        "selected_format":d["selected_program"],
        "corrected_misconception":d["supersedes_wrong_assumption"],
        "production_default":d["production_default"],
        "method_comparison":[{
            "id":m["id"],"label":m["label"],"truth":m["source_truth"],
            "game_license_required":m["game_license_required"],
            "qualification_status":m["status"],
            "advantage":m["strengths"],"limits":m["risks"],
            "next_actual_pilot":m["pilot_gate"],
        } for m in d["methods"]],
        "official_evidence":[{
            "url":x["uri"],"provenance":x["source_type"],
            "statement":x["fact"],"supports":x["establishes"],
            "does_not_prove":x["does_not_establish"],
        } for x in d["official_primary_sources"]],
        "shot_method_candidates":d["shot_candidates"],
        "corrected_department_briefs":d["departments_updated"],
        "reference_full_video_audio_watched":full_review["cohort_gate_passed"],
        "source_video_stream_probe":d["existing_video_samples"]["attempted_10s_mp4_segment"],
        "transcript_access":d["existing_video_samples"]["transcript_connector"],
        "studio_3d_worker_requires_game_install":False,
        "minecraft_capture_remains_optional_method":True,
        "source_label_per_shot_mandatory":True,
        "old_v225_handoff_receipts_preserved":True,
        "production_approved":False,
        "credits_spent":0,
    }

def maizen_shot_method_options(shot_id:str)->dict:
    if shot_id not in SHOTS:
        raise ValueError("UNKNOWN_MAIZEN_SHOT")
    d=load_maizen_method_review()
    s=next(x for x in d["shot_candidates"] if x["id"]==shot_id)
    from .maizen_full_video_gate_v227 import maizen_full_video_review_gate
    full_review=maizen_full_video_review_gate()
    return {
        "full_video_first_reference_review_passed":full_review["cohort_gate_passed"],
        "competitor_based_shot_method_choice_blocked":not full_review["cohort_gate_passed"],
        "schema":"cine.minecraft.maizen_shot_method_decision.v226",
        "shot":s,
        "first_candidate":next(x for x in d["methods"] if x["id"]==s["first_pilot_method"]),
        "alternative":next(x for x in d["methods"] if x["id"]==s["alternative_method"]),
        "decision":"PENDING_TWO_METHOD_STAGING_AND_VISUAL_AUDIO_QC",
        "game_runtime_always_required":False,
        "real_shot_media_exists":False,
        "approved_for_episode":False,
    }
