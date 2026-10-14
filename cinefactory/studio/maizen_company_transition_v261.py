"""Maizen v261 research-to-preproduction handoff: fail-closed real evidence, original-IP only.
Only writes internal desk plans. Never renders, installs packages, spends credits or uploads.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"data/verification/v261_maizen_company_transition"
SOURCE=ROOT/"docs/MAIZEN_RESEARCH_CONTINUOUS_A_TO_D_V260_20261011.md"
PILOT=ROOT/"data/verification/v243_maizen_original_preproduction/nine_pilot_shots.json"
BOARD=ROOT/"data/verification/v243_maizen_original_preproduction/company_stage_board.json"
RESEARCH=ROOT/"data/research/youtube_breakout/approved_deep_research/maizen_canonical_about_join_v259.json"
AUDITS=ROOT/".tools/maizen_peer_av_v260"
CASES={
    "RjyeHZ5hSaE":("MINE_BLOCK","ANIMATION",1561),
    "7jgzaEmqVQU":("JJ_CARTOONS","GAMEPLAY",1354),
    "qtWfSIqNfdU":("MSTOONS","ANIMATION",613),
}
def _load(path:Path)->dict:
    if not path.is_file():raise FileNotFoundError(str(path))
    obj=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj,dict):raise ValueError("EXPECTED_JSON_OBJECT:"+str(path))
    return obj
def _hash(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def _scene_requests(shots:list[dict])->list[dict]:
    cursor=0
    stage=[]
    for shot in shots:
        if shot["start"]!=cursor or shot["end"]!=cursor+5 or shot["media_source"]!="NO_REAL_FRAMES_EXIST":
            raise ValueError("PILOT_SHOT_TIMING_OR_PROVENANCE_INCORRECT")
        stage.append({
            "shot_id":shot["shot_id"],"time_start":shot["start"],"time_end":shot["end"],
            "original_action":shot["original_action"],"coverage":shot["coverage"],
            "actor_audio":shot["dialogue_scratch_only"],
            "candidate_paths":["BLENDER_AUTHORED","LICENSED_GAME_RUNTIME_CAPTURE"],
            "state":"DESK_BLOCKING_PENDING_MEDIA",
            "quality_tests":["legible_mobile_hook","consistent_original_character_identity",
                             "spatial_continuity","lipsync_if_dialogue","audio_clear",
                             "visual_motion_and_camera_intent","commercial_asset_rights"],
        })
        cursor=shot["end"]
    if cursor!=45 or len(stage)!=9:raise ValueError("UNEXPECTED_PILOT_DURATION")
    return stage

def make_transition(*,root:Path=ROOT,write:bool=False)->dict[str,Any]:
    # root override aids regression tests; no writes without explicit write=True
    source=root/"docs/MAIZEN_RESEARCH_CONTINUOUS_A_TO_D_V260_20261011.md"
    research=root/"data/research/youtube_breakout/approved_deep_research/maizen_canonical_about_join_v259.json"
    pilot=root/"data/verification/v243_maizen_original_preproduction/nine_pilot_shots.json"
    board=root/"data/verification/v243_maizen_original_preproduction/company_stage_board.json"
    audits_root=root/".tools/maizen_peer_av_v260"
    if not source.is_file() or not research.is_file():raise FileNotFoundError("RESEARCH_HANDOFF_EVIDENCE_MISSING")
    source_sha=_hash(source)
    owner_source=_load(research)
    if not owner_source.get("canonical_public_about_source"):raise ValueError("NO_CANONICAL_COMPANY_RESEARCH_SOURCE")
    shots=_load(pilot)
    if shots.get("project_id")!="MAI01_WATERFALL" or shots.get("pilot_seconds")!=45:
        raise ValueError("NOT_APPROVED_ORIGINAL_PILOT")
    scene_plan=_scene_requests(shots["shots"])
    board_data=_load(board)
    if (board_data.get("company_department_count")!=26 or
        board_data.get("can_execute_render_or_stage_G03_to_G28") is not False or
        board_data.get("chosen_render_method") is not None or
        board_data.get("full_pilot_media_created") is not False):
        raise ValueError("UNSAFE_OR_INCOMPLETE_26_DEPARTMENT_BOARD")
    refs=[]
    for video_id,(channel,fmt,duration) in CASES.items():
        audit=_load(audits_root/video_id/"audit.json")
        if audit.get("source_id")!=video_id or audit.get("expected_duration")!=duration:
            raise ValueError("VIDEO_AUDIT_PROVENANCE_MISMATCH:"+video_id)
        receipt_complete=(audit.get("segments")==audit.get("complete") and
                         isinstance(audit.get("segments"),int) and audit["segments"]>0 and
                         audit.get("seam_gaps")==[] and audit.get("frames",0)>0 and
                         audit.get("audio_bytes",0)>1000)
        if not receipt_complete:raise ValueError("INCOMPLETE_SOURCE_BROWSER_PLAYBACK:"+video_id)
        # Machine readout and sparse frames do not elevate a film to independent AV QC.
        semantic=bool(audit.get("independent_semantic_audio_qc") and audit.get("separate_reviewer_approved"))
        refs.append({
            "video_id":video_id,"channel":channel,"format":fmt,
            "public_source_url":"https://www.youtube.com/watch?v="+video_id,
            "browser_playback_segments":audit["segments"],
            "complete_browser_segments":audit["complete"],
            "visual_frame_samples":audit["frames"],
            "source_audio_bytes":audit["audio_bytes"],
            "browser_source_acquisition":"COMPLETE_SOURCE_TIMELINE_WITH_SPARSE_SAMPLED_FRAMES",
            "native_audio_human_independent_semantic_qc":"PASSED" if semantic else "PENDING",
            "full_original_moving_frame_semantic_qc":"PENDING",
            "backend_or_exact_competitor_software":"UNKNOWN",
            "source_scope":"SOURCE_FRAMES_PLUS_AUTO_CAPTIONS_NOT_FULL_CERTIFIED_AV",
            "production_method_proven":False,
        })
    g02=all(r["native_audio_human_independent_semantic_qc"]=="PASSED" and
            r["full_original_moving_frame_semantic_qc"]=="PASSED" for r in refs)
    if g02:raise RuntimeError("G02_NEEDS_SEPARATE_SIGNED_MULTIMODAL_VERIFICATION")
    concepts=[
        {"concept_id":"ORIGINAL_CHALLENGE_HOLES","subformat":"MINECRAFT_GAMEPLAY_CHOICE_PUZZLE",
         "premise":"Nova and Pip each choose one of two underground escape routes, discovering that the shortest path is not the safest.",
         "hook_seconds":10,"format":"REAL_GAMEPLAY_CAPTURE","original_characters":["NOVA","PIP"],
         "repeatable_elements":["randomized choice room","parkour chamber","logic gate","visible reward","final goal"],
         "rights":"NO_MAIZEN_CHARACTER_SKINS_OR_BRAND_COPY","status":"ORIGINAL_DESK_CONCEPT"},
        {"concept_id":"MAI01_WATERFALL","subformat":"MINECRAFT_GAMEPLAY_MYSTERY_OR_ANIMATION",
         "premise":"Nova and Pip discover a secret below a waterfall and must repair a flood valve by using clues introduced early.",
         "hook_seconds":10,"format":"SIDE_BY_SIDE_METHOD_BAKEOFF",
         "original_characters":["NOVA","PIP"],
         "repeatable_elements":["waterfall scene","map clue","valve mechanism","timed flood","earned resolution"],
         "rights":"ORIGINAL_IP_DRAFT","status":"21_BEATS_9_SHOTS_EXIST_NO_REAL_PILOT"},
        {"concept_id":"ORIGINAL_CANDY_ESCAPE","subformat":"AUTHORED_VOXEL_CHARACTER_ANIMATION",
         "premise":"Two original friends must rescue a teammate from a magical confectionery machine before the timer runs out.",
         "hook_seconds":7,"format":"BLENDER_AUTHORED_ANIMATION",
         "original_characters":["NOVA","PIP"],
         "repeatable_elements":["transform rig","face reactions","moving obstacles","comic body acting","final rescue"],
         "rights":"NO_MSTOONS_ASSETS_STORY_SHOTS_OR_VOICES","status":"ORIGINAL_DESK_CONCEPT"}
    ]
    next_steps=[
        {"phase":"G02","owner":"EVIDENCE_QC","task":"Independently review native motion+sound of at least three original source films; sample timecodes and auto captions are insufficient","status":"BLOCKED"},
        {"phase":"G03","owner":"INTELLIGENCE+SCRIPT+DIRECTOR","task":"Compare winner videos with same-format lower performers, time-coded hooks and full scripts, explicitly avoid source-based method overclaim","status":"DESK_RESEARCH_ONLY"},
        {"phase":"G04","owner":"STRATEGY","task":"Score Maizen gameplay puzzle versus independent voxel animation using true small-channel cohorts, rights and cost uncertainty","status":"PROVISIONAL"},
        {"phase":"G05-G07","owner":"STUDIO_MANAGEMENT+WRITERS_ROOM+SCRIPT_LOGIC","task":"Review three ORIGINAL concepts; finish professional VO script and run causal continuity checks on 21-waterfall-beat draft","status":"DRAFT_ALLOWED"},
        {"phase":"G08-G15","owner":"DIRECTOR+DESIGN+RND+OPERATIONS","task":"Prepare original 45-second common-scene comparability benchmark; verify licensed game runtime, first-party assets, Blender and RTX3060 capacity","status":"PLANNED_NOT_EXECUTED"},
        {"phase":"G16-G24","owner":"PRODUCTION+POST+QC","task":"Only after source/right/owner approval render and record real 45-second visual+audio pilot, measure accepted seconds/hour, quality, memory, sound and rework","status":"HOLD"},
        {"phase":"G25-G28","owner":"PACKAGING+ANALYTICS+RELEASE","task":"Only after actual pilot QC and owner approval prepare original packaging and evaluate launch results (never fake retention/RPM)","status":"HOLD"}
    ]
    rights=[
        {"asset":"ORIGINAL_NOVA_RIG","license":"UNVERIFIED_UNBUILT","approved":False},
        {"asset":"ORIGINAL_PIP_RIG","license":"UNVERIFIED_UNBUILT","approved":False},
        {"asset":"MINECRAFT_RUNTIME_IF_USED","license":"VERIFY_PURCHASE_AND_COMMERCIAL_USE","approved":False},
        {"asset":"ORIGINAL_SFX_VOICES_MUSIC","license":"UNSOURCED_RIGHTS_CHECK","approved":False},
    ]
    progress={
        "schema":"cine.company.maizen_research_transition.v261",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "study_scope":["minecraft_gameplay","minecraft_animation"],
        "source_report_sha256":source_sha,"source_report":str(source),
        "independent_source_cases":refs,
        "gates":{"G01":"PARTIAL_BOUNDED_DISCOVERY",
                 "G02":"PASS" if g02 else "BLOCKED_INDEPENDENT_NATIVE_AV",
                 "G03":"PENDING_AUTHENTICATED_SOURCE_SCENE_CONFERENCE",
                 "G04":"PROVISIONAL_NO_VERIFIED_NEWBORN_TWO_MILLION",
                 "G05_G15":"ORIGINAL_DESK_PREPRO_ONLY",
                 "G16_G28":"HOLD_NO_PRODUCTION_OR_RELEASE_APPROVAL"},
        "original_pilot":{"project_id":"MAI01_WATERFALL","duration_seconds":45,
                          "shot_count":len(scene_plan),"shots":scene_plan,
                          "rendered":False,"vo_recorded":False},
        "business_rule":"No competitor-derived production method approved; no paid credits or auto publish",
        "valid_commercial_rights_ready":False,
        "hardware_qualification_evidence":"PENDING_REAL_BENCHMARK",
        "new_channel_0_30d_two_distinct_million_verified":False,
        "research_to_production_approved":False,
        "original_concept_candidates":concepts,
        "bakeoff_spec":{
            "same_original_story_and_9_shots":True,
            "methods":["BLENDER_AUTHORED","LICENSED_GAME_RUNTIME_CAPTURE"],
            "preserve_original_characters":True,"cost_and_elapsed":None,
            "minimum_qc":["all_45_seconds_1080p24_real_media","native_audio_continuous_listen",
                         "0_character_continuity_failures","0_unlicensed_assets",
                         "verified_owner_approval_before_production",
                         "measure_quality_against_reference_brief",
                         "track_wall_time_and_rework_per_accepted_second"],
            "status":"PLAN_ONLY_NO_MEASURED_SPEED_OR_GPU",
        },
        "department_packets_reference":str(board),
        "work_stages":next_steps,
        "rights_matrix":rights,
    }
    if write:
        out=root/"data/verification/v261_maizen_company_transition"
        out.mkdir(parents=True,exist_ok=True)
        target=out/"company_transition_gate.json"
        target.write_text(json.dumps(progress,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        manifest={"schema":"cine.company.maizen_manifest.v261","created_utc":progress["created_utc"],
                  "files":[{"name":target.name,"sha256":_hash(target),"bytes":target.stat().st_size}],
                  "source_sha256":source_sha,"gate_G02":progress["gates"]["G02"],
                  "production_approved":False}
        (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        progress["output_path"]=str(target)
    return progress

if __name__=="__main__":
    obj=make_transition(write=True)
    print(json.dumps({"schema":obj["schema"],"source_films":len(obj["independent_source_cases"]),
                       "source_segments":sum(c["browser_playback_segments"] for c in obj["independent_source_cases"]),
                       "frame_samples":sum(c["visual_frame_samples"] for c in obj["independent_source_cases"]),
                       "gates":obj["gates"],"pilot_shots":obj["original_pilot"]["shot_count"],
                       "concepts":[c["concept_id"] for c in obj["original_concept_candidates"]],
                       "output":obj["output_path"]},ensure_ascii=False,indent=2))
