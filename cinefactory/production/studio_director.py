"""Studio-grade creative production planning, independent of current GPU hardware.

Planning ONLY. Tool names are candidates, never proof of installation/execution.
This is an extension of the existing ShotRouter/StoryboardGate/VideoFactory
and does not silently route paid services or approve publication.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


LANES={
    "blender_character_animation":{
        "candidate_tools":["Blender","CharacterRigRegistry","AnimationClipLibrary","ExpressionEngine"],
        "fit":["character_dialogue","character_acting","complex_interaction"],
        "evidence_needed":["rig_continuity","facial_performance","lip_sync","camera_coverage","lighting","character_identity"],
        "production_kind":"deterministic_3d"},
    "unreal_realtime_cinematic":{
        "candidate_tools":["Unreal Engine","Control Rig","Sequencer"],
        "fit":["cinematic_action","large_environment","realtime_scene"],
        "evidence_needed":["rig_continuity","simulation","performance","camera_coverage","lighting"],
        "production_kind":"realtime_3d"},
    "comfyui_controlled_ai_video":{
        "candidate_tools":["ComfyUI","LTX-2.5","Wan2.2","reference keyframes","LoRA or control adapters"],
        "fit":["stylized_montage","cinematic_transition","environment_insert","ai_visual_experiment"],
        "evidence_needed":["frame_identity","temporal_consistency","anatomy","camera_coverage","rights"],
        "production_kind":"generative_video"},
    "game_engine_capture":{
        "candidate_tools":["Unity or Unreal runtime","deterministic camera controller","asset/obstacle library"],
        "fit":["gameplay","long_slide","physics_simulation"],
        "evidence_needed":["physics_correctness","camera_tracking","asset_identity","collision_safety"],
        "production_kind":"deterministic_runtime"},
    "physical_camera_capture":{
        "candidate_tools":["camera/microphone capture","DaVinci Resolve","Fairlight"],
        "fit":["tactile_asmr","fishing_live_action","physical_demonstration"],
        "evidence_needed":["microphone_noise_floor","focus","continuity","visual_clarity"],
        "production_kind":"physical_capture"},
    "audio_environment":{
        "candidate_tools":["licensed/recorded sound","FFmpeg","DaVinci Fairlight","audio QA"],
        "fit":["rain_ambience","sleep_soundscape","narrated_audio_story"],
        "evidence_needed":["audio_source_rights","loop_seams","integrated_loudness","distortion"],
        "production_kind":"audio_first"},
    "remotion_graphics":{
        "candidate_tools":["Remotion","FFmpeg","After Effects candidate"],
        "fit":["motion_graphics","educational_explainer","title_sequence"],
        "evidence_needed":["readability","motion_safe_area","timing","caption_sync"],
        "production_kind":"procedural_graphics"},
}

NICHE_BLUEPRINTS={
    "minecraft_animation":{"default_lane":"blender_character_animation","style":"voxel_identity_locked",
        "focus":["character silhouette","facial expression and acting","camera readability","comedic causality","beat timing"]},
    "roblox_animation":{"default_lane":"blender_character_animation","style":"r6_anatomy_identity_locked",
        "focus":["R6 body/clothing consistency","clear action","expressive poses","shot continuity"]},
    "long_slide_game":{"default_lane":"game_engine_capture","style":"deterministic_physics_action",
        "focus":["animal/obstacle identity","collision readability","camera tracking","spectacle pacing"]},
    "asmr_sleep":{"default_lane":"physical_camera_capture","style":"close_macro_sensory",
        "focus":["clean close microphone capture","gentle rhythm","macro texture","no sudden loudness"]},
    "fishing_silent":{"default_lane":"physical_camera_capture","style":"observational_documentary",
        "focus":["authentic outdoor action","wildlife/environmental care","camera coverage","natural sound"]},
    "audio_story":{"default_lane":"audio_environment","style":"narration_first",
        "focus":["narrative arcs","voice authenticity","licensed source content","audible scene changes"]},
    "rain_sleep":{"default_lane":"audio_environment","style":"seamless_audio_ambience",
        "focus":["seamless loop","quiet dynamics","rights clearance","consistent atmosphere"]},
    "gta_animation":{"default_lane":"unreal_realtime_cinematic","style":"controlled_game_cinema",
        "focus":["original assets and rights","action beats","character identity","physical staging"]},
    "english_learning":{"default_lane":"remotion_graphics","style":"clear_educational_story",
        "focus":["pedagogical correctness","human voice delivery","captions","clarity of scene examples"]},
}


def _need_string(value: Any, label: str, *, minimum: int=3):
    if not isinstance(value,str) or len(value.strip())<minimum:
        raise ValueError(label+" is required")


def _positive(v: Any, label: str):
    if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or v<=0:
        raise ValueError(label+" must be a finite positive number")


def _canon(niche: str):
    n=niche.strip().casefold().replace("-"," ").replace("_"," ")
    # Long-form market research may name subdivisions of established production families.
    mapping=(
        ("minecraft","minecraft_animation"),("roblox","roblox_animation"),
        ("long slide","long_slide_game"),("asmr","asmr_sleep"),
        ("rain","rain_sleep"),("fishing","fishing_silent"),
        ("audio story","audio_story"),("storytelling","audio_story"),
        ("gta","gta_animation"),("english","english_learning"),
    )
    return next((v for token,v in mapping if token in n),None)


def _shot_lane(shot:dict,blueprint:dict|None)->str:
    kind=shot["scene_kind"]
    explicit={
        "character_dialogue":"blender_character_animation",
        "character_acting":"blender_character_animation",
        "complex_interaction":"blender_character_animation",
        "cinematic_action":"unreal_realtime_cinematic",
        "large_environment":"unreal_realtime_cinematic",
        "realtime_scene":"unreal_realtime_cinematic",
        "stylized_montage":"comfyui_controlled_ai_video",
        "cinematic_transition":"comfyui_controlled_ai_video",
        "environment_insert":"comfyui_controlled_ai_video",
        "ai_visual_experiment":"comfyui_controlled_ai_video",
        "gameplay":"game_engine_capture",
        "long_slide":"game_engine_capture",
        "physics_simulation":"game_engine_capture",
        "tactile_asmr":"physical_camera_capture",
        "fishing_live_action":"physical_camera_capture",
        "physical_demonstration":"physical_camera_capture",
        "rain_ambience":"audio_environment",
        "sleep_soundscape":"audio_environment",
        "narrated_audio_story":"audio_environment",
        "motion_graphics":"remotion_graphics",
        "educational_explainer":"remotion_graphics",
        "title_sequence":"remotion_graphics",
    }
    if kind not in explicit:
        raise ValueError("Unknown scene kind "+str(kind))
    lane=explicit[kind]
    # For asset-heavy, repeat characters, prefer deterministic rigs rather than
    # rediscovering identity via a series of unrelated stochastic AI generations.
    if shot.get("characters") and len(shot["characters"])>=2 and kind=="cinematic_action":
        lane="blender_character_animation"
    return lane


def build_studio_production_plan(brief:dict, capability_registry:dict, output:str|Path)->dict:
    """Generate audit-ready director's work order. No media generated/approved."""
    if brief.get("schema")!="cine.studio.creative_brief.v1":
        raise ValueError("Expected cine.studio.creative_brief.v1")
    for key in ("project_id","niche","audience","creative_intent","originality_statement","episode_premise"):
        _need_string(brief.get(key),key,minimum=8 if key in ("creative_intent","originality_statement","episode_premise") else 3)
    profile=brief.get("quality_profile")
    if profile not in ("broadcast_premium","cinema_flagship"):
        raise ValueError("Premium quality profile required")
    if not isinstance(brief.get("shots"),list) or not brief["shots"] or len(brief["shots"])>500:
        raise ValueError("1 to 500 directed shots required")
    if capability_registry.get("schema")!="cine.studio.capability_registry.v1":
        raise ValueError("Capability evidence registry required")
    capabilities=capability_registry.get("lanes",{})
    if not isinstance(capabilities,dict):
        raise ValueError("Capability registry lanes must be object")
    char_bible=brief.get("character_bible",{})
    if not isinstance(char_bible,dict):
        raise ValueError("Character bible must be a dictionary")
    bp_key=_canon(brief["niche"])
    blueprint=NICHE_BLUEPRINTS.get(bp_key)
    findings=[]
    if not blueprint:
        findings.append("NEW_NICHE_NEEDS_A_DIRECTOR_REVIEWED_PRODUCTION_BLUEPRINT")
    if not brief.get("competitor_research_revision"):
        findings.append("COMPETITOR_STUDY_NOT_LINKED_TO_EVIDENCE_REVISION")
    beats=brief.get("episode_beat_plan")
    if (not isinstance(beats,list) or len(beats)<3 or
        any(not isinstance(x,str) or len(x.strip())<12 for x in beats)):
        findings.append("EPISODE_NEEDS_AT_LEAST_THREE_SUBSTANTIVE_DIRECTED_BEATS")
    if not brief.get("script_editor_approved",False):
        findings.append("SCRIPT_EDITOR_SIGNOFF_PENDING")
    shots=[]
    seen_ids=set()
    for s in brief["shots"]:
        if not isinstance(s,dict):
            raise ValueError("Malformed shot work order")
        sid=s.get("shot_id")
        _need_string(sid,"shot_id")
        if sid in seen_ids:raise ValueError("Duplicate shot ID")
        seen_ids.add(sid)
        _positive(s.get("duration_seconds"),"shot duration")
        lane=_shot_lane(s,blueprint)
        missing=[]
        for field in ("scene_goal","script_beat","location_id","blocking","camera_plan","lighting_plan",
                      "sound_plan","transition_in","transition_out","storyboard_reference"):
            if not isinstance(s.get(field),str) or len(s[field].strip())<3:
                missing.append(field)
        if not isinstance(s.get("characters"),list):
            missing.append("characters")
            characters=[]
        else:characters=s["characters"]
        for char in characters:
            if char not in char_bible:
                missing.append("CHARACTER_BIBLE:"+str(char))
        if characters:
            for field in ("emotion_beats","expression_animation","performance_direction","continuity_state"):
                if not s.get(field):
                    missing.append(field)
            for char in characters:
                if char in char_bible:
                    b=char_bible[char]
                    if not isinstance(b,dict) or not all(b.get(t) for t in (
                            "identity_asset_id","silhouette","rig_version","expression_set","wardrobe_state")):
                        missing.append("INCOMPLETE_CHARACTER_BIBLE:"+char)
        if not s.get("storyboard_approved",False):
            missing.append("STORYBOARD_NOT_APPROVED")
        used=capabilities.get(lane,{})
        if not isinstance(used,dict):used={}
        proved=(used.get("state")=="BENCHMARKED_READY" and
                isinstance(used.get("evidence_ref"),str) and len(used["evidence_ref"])>=12
                and isinstance(used.get("tested_tool_version"),str)
                and len(used["tested_tool_version"])>=2)
        alternate=[key for key,lane_meta in LANES.items()
                   if key!=lane and s["scene_kind"] in lane_meta["fit"]]
        shots.append({
            "shot_id":sid,"scene_kind":s["scene_kind"],"scene_goal":s.get("scene_goal"),
            "duration_seconds":s["duration_seconds"],"primary_lane":lane,
            "candidate_tools":LANES[lane]["candidate_tools"],
            "possible_alternative_lanes":alternate,
            "source_character_ids":characters,
            "technical_route_state":"CAPABILITY_BENCHMARKED" if proved else "NOT_EXECUTABLE_UNTIL_CAPABILITY_VERIFIED",
            "creative_work_order_state":"DIRECTOR_REVIEW_PENDING" if missing else "DIRECTOR_PACK_COMPLETE_REVIEW_STILL_REQUIRED",
            "missing":missing,
            "required_visual_audio_gates":LANES[lane]["evidence_needed"],
            "human_dailies_required":True,
            "single_final_character_identity":True if characters else None,
            "gpu_requirement":"SCHEDULE_FROM_CAPABILITY_BENCHMARK_NOT_CURRENT_GPU",
            "benchmarked_seconds_per_output_second":
                used.get("measured_seconds_per_output_second") if proved
                and isinstance(used.get("measured_seconds_per_output_second"),(float,int))
                and not isinstance(used.get("measured_seconds_per_output_second"),bool)
                and math.isfinite(used["measured_seconds_per_output_second"])
                and used["measured_seconds_per_output_second"]>0 else None,
            "external_paid_api_permitted":False,
        })
    if not brief.get("studio_budget_approved",False):
        findings.append("STUDIO_BUDGET_APPROVAL_PENDING")
    if not brief.get("original_asset_rights_cleared",False):
        findings.append("ASSET_AND_CHARACTER_RIGHTS_NOT_CLEARED")
    unmet=sum(len(x["missing"]) for x in shots)
    unbench=sum(x["technical_route_state"]!="CAPABILITY_BENCHMARKED" for x in shots)
    critical_project_reasons={
        "NEW_NICHE_NEEDS_A_DIRECTOR_REVIEWED_PRODUCTION_BLUEPRINT",
        "COMPETITOR_STUDY_NOT_LINKED_TO_EVIDENCE_REVISION",
        "EPISODE_NEEDS_AT_LEAST_THREE_SUBSTANTIVE_DIRECTED_BEATS",
        "SCRIPT_EDITOR_SIGNOFF_PENDING",
        "STUDIO_BUDGET_APPROVAL_PENDING",
        "ASSET_AND_CHARACTER_RIGHTS_NOT_CLEARED",
    }
    status=("PLANNED_BLOCKED_CREATIVE_REQUIREMENTS" if unmet else
            "PLANNED_BLOCKED_TOOL_BENCHMARK" if unbench else
            "PLANNED_BLOCKED_PROJECT_APPROVALS" if critical_project_reasons.intersection(findings) else
            "READY_FOR_DEPARTMENT_REVIEW_NOT_PRODUCTION")
    plan={
        "schema":"cine.studio.director_plan.v1",
        "project_id":brief["project_id"],"niche":brief["niche"],
        "quality_profile":profile,"state":status,
        "brief_sha256":hashlib.sha256(json.dumps(brief,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
        "capability_sha256":hashlib.sha256(json.dumps(capability_registry,sort_keys=True).encode()).hexdigest(),
        "niche_blueprint":bp_key or "CUSTOM_NEEDS_RESEARCH",
        "studio_focus":blueprint["focus"] if blueprint else [],
        "shots":shots,"shot_count":len(shots),
        "creative_missing_count":unmet,"unbenchmarked_shot_count":unbench,
        "project_findings":findings,
        "postproduction_plan":{
            "offline_assembly":"FFmpeg/Remotion automated rough edit and frame-accurate conform",
            "hero_edit":"DaVinci Resolve Edit, manual film editing or verified scripted integration",
            "compositing_vfx":"DaVinci Fusion or After Effects if executable and benchmarked",
            "color":"DaVinci Resolve managed color and shot-match QC",
            "audio":"DaVinci Fairlight; dialogue/music/foley/ambience separate stems",
            "final_delivery":"FFmpeg encode/QC + final audio peak/loudness and continuity review",
            "editorial_tests":["narrative clarity","emotion arc","reaction timing","continuity",
                               "pacing by beat","dialogue intelligibility","sound design",
                               "color consistency","rights","4K actual footage"],
        },
        "company_pipeline":["research_provenance","creative_conference","niche_visual_dna",
                            "premise_outlines","script_room","script_table_read","character_bible",
                            "world_bible","shot_list","storyboard_animatic","asset_rig_lock",
                            "pilot_render","daily_footage_QC","animation_or_ai_retake",
                            "offline_edit","vfx_sound_color","independent_QC","rights_clearance",
                            "owner_approval","publish","owned_analytics_learning"],
        "gpu_policy":"HARDWARE_AGNOSTIC_LOCAL_MULTI_GPU_REMOTE_CLOUD_ALLOWED_IF_COST_AND_RIGHTS_APPROVED",
        "not_disney_certified":True,
        "human_creative_review_completed":False,
        "quality_accepted":False,"production_permission":False,
        "no_auto_publish":True,
    }
    dst=Path(output)
    if dst.exists():raise FileExistsError("Director plan is immutable, use a new revision file")
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return plan


def main() -> int:
    """Produce an auditable plan, not a video/render/approval."""
    import argparse
    parser=argparse.ArgumentParser(description="CineFactory studio director production work order")
    parser.add_argument("--brief",required=True,help="Project director's creative brief JSON")
    parser.add_argument("--capabilities",required=True,help="Actually benchmarked lane registry JSON")
    parser.add_argument("--output",required=True,help="New immutable production plan JSON")
    args=parser.parse_args()
    brief=json.loads(Path(args.brief).read_text(encoding="utf-8"))
    caps=json.loads(Path(args.capabilities).read_text(encoding="utf-8"))
    report=build_studio_production_plan(brief,caps,args.output)
    print(json.dumps({
        "schema":report["schema"],"state":report["state"],
        "shot_count":report["shot_count"],
        "creative_missing_count":report["creative_missing_count"],
        "unbenchmarked_shot_count":report["unbenchmarked_shot_count"],
        "production_permission":report["production_permission"],
        "output":str(Path(args.output).resolve()),
    },ensure_ascii=False))
    return 0 if report["state"]=="READY_FOR_DEPARTMENT_REVIEW_NOT_PRODUCTION" else 2


if __name__=="__main__":
    raise SystemExit(main())
