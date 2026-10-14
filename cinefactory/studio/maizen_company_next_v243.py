"""v243 original MAI01 production conference, evidence-aware and fail-closed.

Provides an actual detailed original 14-minute script/beat matrix, a source-
agnostic 9-shot animatic plan, 26-department immutable desk-work receipts and
department-by-department next tasks. Does NOT run a blocked reference-derived
G03-G28 stage, render footage, fake Maizen techniques, consume credits or upload.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any
import json

from .contracts import DepartmentId
from .maizen_studio_kickoff_v225 import load_maizen_studio_a
from .maizen_full_video_gate_v227 import maizen_full_video_review_gate

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/"config/niches/minecraft/maizen_original_production_packet_v243.json"
AV_EVIDENCE=ROOT/"config/niches/minecraft/maizen_original_browser_audio_evidence_v242.json"
OUTPUT=ROOT/"data/verification/v243_maizen_original_preproduction"
SCHEMA="cine.minecraft.maizen_original_preproduction.v243"

ACTIONS={
"STUDIO_MANAGEMENT":("DIRECTOR_BRIEF","Assign responsible owners, approve the screenplay for internal revision only; do not greenlight filming before full reference/source gates","Director signs original-IP and cost policy; source study progress must be visible"),
"INTELLIGENCE":("REFERENCE_COHORT","Complete source video 2+3 original whole-picture/sound analysis and compare multiple long-form story formats","Full-film timecode coverage of all references without invented footage claims"),
"EVIDENCE":("SOURCE_VERIFICATION","Independently audit audio/visual source reports, every <=30s interval and uncertain original-video observations","Source ID, visual+audio reviewer, SHA/trace and outstanding unknowns attached"),
"CREATIVE_STRATEGY":("FORMAT_HYPOTHESIS","Contrast short choices against the single long waterfall mystery without claiming competitor format certainty","Original format DNA, retention assumptions explicitly hypotheses"),
"PLANNING":("840_SECOND_STRUCTURE","Lock draft seven-chapter duration grid and generate 21 timed beat/production handoffs","No duration gaps, timing labels and dependencies present"),
"WRITERS_ROOM":("ORIGINAL_BEAT_SCRIPT","Rewrite original 21 scene beats into full natural English dialogue, humor and motivations; retain 14m timing","Two original voices and causal surprises; exact competitor lines never copied"),
"SCRIPT_LOGIC":("CAUSAL_CONTINUITY","Verify map, valve, river bridge, waterfall access, clue, fallback exit and flood states","Every prop ownership and threat response resolves in subsequent scenes"),
"DIRECTION":("CAMERA_SHOT_PLAN","Review all 21 original beats and nine pilot shots; block shots without stage cause/effect","All scene coverage and reveal timing make sense before a backend selection"),
"PERFORMANCE":("ACTOR_BLOCKING","Define original Nova/Pip silhouettes, rig gestures, emotions, hand/foot and eye lines per shot","Reactions align with actor voices and objects; separate unique character identity"),
"CINEMATOGRAPHY":("SHOT_CAMERA_MATRIX","Storyboard wide/POV/two-shot/cutaway decisions, scene geography, look direction and continuity","No camera teleports, all 9 pilot shots technically feasible in chosen tool later"),
"PRODUCTION_DESIGN":("SCENE_BLUEPRINT","Build original connected waterfall/river/river fork/workshop layouts as versioned set sketches","River, waterfall, cave route and emergency exit spatially connected"),
"ASSETS":("RIGHTS_CLEAN_ASSET_REGISTRY","Create original unique map, pressure plate, valve, crystal, latch, bridges and accessories, with asset IDs","All assets have owner/rights and inspectable model/texture versions"),
"TECHNICAL_DIRECTION":("METHOD_BENCHMARK_SPEC","Write per-shot acceptance benchmarks for Blender/Game Staged/Hybrid; do not assert Maizen backend or start blocked benchmark","Runtime needs, controllable camera, physical actor movement, performance, audio sync and rights gates"),
"PRODUCTION":("RENDER_EXECUTION_QUEUE","Prepare deterministic 9-shot shot manifests and worker/safety dependencies; do not render before source and quality gates","Queue is hold-only with no fake rendered frames"),
"GENERATIVE_MEDIA":("MODEL_AND_WORKFLOW_QUALIFICATION","Record optional ComfyUI workflows with license, VRAM and continuity testing before any use","No paid credit calls, no untrusted external workflow execution"),
"VFX":("FX_CAUSAL_PLAN","Specify physically consistent amber clue light, river waterfall, flood, blue crystal, safety latch, sparse particle FX","Effects originate at scene objects and respect continuity"),
"EDITORIAL":("ANIMATIC_EDIT_PLAN","Prepare editable timeline from the 21 timecoded beats and 9-shot pilot; define cold-open, discoveries, construction montage, crisis and resolution","All final timeline seconds accounted for; no stock competitor footage"),
"AUDIO":("DIALOGUE_FOLEY_CUE_LIST","Plan two original English voices, waterfall ambience, map paper, footsteps, block place, clue, urgent flood and musical mood","Original voice/music/SFX licenses, source sync and speech/noise mix QC pending"),
"COLOR":("ART_DIRECTION_LOOK_BIBLE","Plan pixel-nearest voxel materials, consistent sky/cave/crystal luminance and final output color transform","No washed-out/double gamma; actual rendered samples required for approval"),
"QC":("STORY_AND_RENDER_TEST_MATRIX","Audit all scene states, scene-to-scene transitions, lip/audio sync, image quality, camera cuts, rights and full playback","Research G02 blocked; no auto-approved production"),
"RIGHTS":("IP_AND_LICENSE_MATRIX","Prohibit JJ/Mikey/Maizen skins, official videos/music and unlicensed voice cloning; verify every new media asset before production","Right holder/license and permitted usage for all source materials"),
"PACKAGING":("ORIGINAL_THUMBNAIL_BRIEF","Create title, 3 thumbnail concepts and branded visual style from Nova/Pip without copying Maizen packaging","Original silhouettes, no reused Maizen logo/colors/official skin"),
"ANALYTICS":("EXPERIMENT_HYPOTHESES","Specify pre-release tests for hook clarity, 15s retention risks, midpoint twist and final reveal","Do not fabricate 1M views or expected RPM; analytics require actual published data"),
"RND":("LOCAL_PIPELINE_RESEARCH","Research stage-camera controller, OpenUSD/Blender interchange and testability only, with reproducible GPU benchmarks when approved","RTX3060 12GB feasibility and no hidden paid providers"),
"RD_KNOWLEDGE":("EVIDENCE_TO_SKILLS_RULES","Version confirmed source observations separate from one-film hypotheses, propagate skill after human QC","No training on guessed Maizen tools or false benchmark data"),
"OPERATIONS":("WORKSTATION_PREFLIGHT","Check Blender 4.5/FFmpeg, RTX3060 driver, disk, project isolation and rights, plus game license only if game route selected","No installation, game purchase, OBS session or cloud spend without separate authorization"),
}

def load_original_preproduction() -> dict[str,Any]:
    obj=json.loads(INPUT.read_text(encoding="utf8"))
    if obj.get("schema")!=SCHEMA or obj.get("project_id")!="MAI01_WATERFALL" or obj.get("status")!="SAFE_ORIGINAL_PREPRO_DRAFT_ONLY":
        raise ValueError("ORIGINAL_PREPRO_SCHEMA_OR_APPROVAL_INVALID")
    if obj.get("reference_video_id")!="ZmT0ITUGUII" or not AV_EVIDENCE.is_file():
        raise ValueError("PROVENANCE_OR_AV_EVIDENCE_MISSING")
    refs=json.loads(AV_EVIDENCE.read_text(encoding="utf8"))
    c=refs["source_trace"]
    if refs.get("video_id")!="ZmT0ITUGUII" or not c["automatic_whisper_en_speech_segments_complete"]==45 or not c["original_visual_browser_playback_segments_complete"]==45:
        raise ValueError("ONE_EPISODE_EVIDENCE_NOT_MATCHED")
    historic=load_maizen_studio_a()
    if obj["duration_seconds"]!=historic["episode"]["duration_seconds"] or obj["pilot_shot_ids"]!=[s["id"] for s in historic["pilot"]["shots"]]:
        raise ValueError("ORIGINAL_PILOT_ID_OR_EPISODE_LENGTH_CHANGED")
    if [x["id"] for x in obj["chapters"]]!=[x["id"] for x in historic["episode"]["chapters"]]:
        raise ValueError("CHAPTER_ORDER_CHANGED")
    beats=obj["beats"]
    if len(beats)!=21 or len({b["id"] for b in beats})!=len(beats):
        raise ValueError("EPISODE_BEATS_INCOMPLETE")
    cursor=0
    for beat in beats:
        if (beat["start"]!=cursor or beat["end"]<=cursor
            or not beat.get("dialogue") or not beat.get("action")
            or not beat.get("audio") or not beat.get("continuity")
            or beat["creative_status"]!="ORIGINAL_WORKING_DRAFT_NOT_SOURCE_CONCLUSION"):
            raise ValueError("ORIGINAL_BEAT_TIMELINE_OR_DESK_STATUS")
        cursor=beat["end"]
    if cursor!=840:
        raise ValueError("ORIGINAL_BEAT_END_MISMATCH")
    for chapter in obj["chapters"]:
        selected=[b for b in beats if b["chapter"]==chapter["id"]]
        if len(selected)!=3 or selected[0]["start"]!=chapter["start"] or selected[-1]["end"]!=chapter["end"]:
            raise ValueError("ORIGINAL_CHAPTER_NOT_THREE_COMPLETE_BEATS")
    if {x["id"] for x in obj["characters"]}!={"NOVA","PIP"}:
        raise ValueError("ORIGINAL_ACTORS_NOT_DISTINCT")
    if any(obj["original_rights"][x] for x in ("copy_Maizen_characters","copy_Maizen_dialogue","copy_Maizen_music","copy_reference_assets")):
        raise ValueError("RIVAL_COPYING_NOT_ALLOWED")
    if any(x not in ("BLENDER_AUTHORED","GAME_ENGINE_STAGED","SCENE_HYBRID") for x in obj["technical_candidates"]):
        raise ValueError("UNREVIEWED_TECHNOLOGY_INCLUDED")
    if not obj["research_gate_policy"]["requires_all_3_full_av_independent_approvals"] or not obj["research_gate_policy"]["no_publish_before_art_audio_continuity_rights_qc"]:
        raise ValueError("SOURCE_RESEARCH_OR_RELEASE_GATES_MISSING")
    ids={a["id"] for a in obj["asset_requirements"]}
    if len(ids)!=len(obj["asset_requirements"]) or "NOVA_RIG" not in ids or "PIP_RIG" not in ids:
        raise ValueError("ASSET_IDS_NOT_UNIQUE")
    if set(ACTIONS)!={x.value for x in DepartmentId}:
        raise ValueError("NOT_ALL_26_DEPARTMENTS_WIRED")
    return obj

def director_pilot_shots()->list[dict]:
    original=load_maizen_studio_a()
    result=[]
    seen=0
    for item in original["pilot"]["shots"]:
        if item["start"]!=seen:
            raise ValueError("PILOT_TIMECODE_CONTINUITY_FAILURE")
        seen=item["end"]
        lens=("28mm_wide" if item["camera"] in ("EXTERIOR_WIDE","TWO_SHOT_PULLBACK","THIRD_PERSON_TWO_SHOT")
              else "35mm_medium")
        result.append({
            "shot_id":item["id"],"start":item["start"],"end":item["end"],
            "original_action":item["action"],"dialogue_scratch_only":item["dialogue"],
            "scene":item["location"],"coverage":item["camera"],
            "lens_candidate":lens,"art_source":"ORIGINAL_VOXEL_NO_MAIZEN_ASSETS",
            "voice_state":"SCRATCH_VOICE_NOT_RECORDED",
            "media_source":"NO_REAL_FRAMES_EXIST",
            "game_vs_blender_selection":"CANDIDATES_ONLY_NO_METHOD_CHOSEN",
            "execution_gate":"HOLD_G02_INDEPENDENT_FULL_REFERENCE_STUDY",
            "delivery_criteria":[
                "character and prop continuity versus previous shot",
                "camera framing and line-of-action QC",
                "original English dialogue audible and synced",
                "action visible on rendered frames, not screenshot inference",
                "no competitor voices/rigs/branding copied",
            ],
        })
    if seen!=45:
        raise ValueError("PILOT_NOT_45_SECONDS")
    return result

def maizen_next_company_stage()->dict:
    p=load_original_preproduction()
    g=maizen_full_video_review_gate()
    pending=[v["video_id"] for v in g["videos"] if not v["gate_passed"]]
    return {
        "schema":"cine.minecraft.maizen_company_next_step.v243",
        "project_id":p["project_id"],"name":p["original_working_title"],
        "company_department_count":len(ACTIONS),
        "script_draft_beats":len(p["beats"]),"full_script_vo_recorded":False,
        "draft_14min_story_arc_exists":True,
        "draft_45sec_pilot_shots":len(p["pilot_shot_ids"]),
        "original_assets_listed":len(p["asset_requirements"]),
        "stage":"DESK_PREPRO_WORK_PRODUCTS_ONLY",
        "next_required_research_stage":"G02_EVIDENCE_QC_OTHER_TWO_FILMS_AND_FIRST_FULL_AUDIO_FX_QC",
        "can_execute_render_or_stage_G03_to_G28":g["cohort_gate_passed"],
        "source_full_video_qc_pass":g["cohort_gate_passed"],
        "source_videos_still_missing_approval":pending,
        "source_1_browser_timeline_and_asr_completed_unverified_strict_qc":True,
        "exact_rival_technical_stack_confirmed":False,
        "chosen_render_method":None,
        "full_pilot_media_created":False,"publish_approved":False,
        "owner_cost_guard":"ZERO_EXTERNAL_CREDITS_WITHOUT_EXPLICIT_APPROVAL",
        "next_actions":[
            {"order":1,"owner":"EVIDENCE","action":"Validate source 1 native audio/SFX against every <=30s interval and get independent QC; complete original image/audio study for remaining source films.","gate":"G02"},
            {"order":2,"owner":"STUDIO_MANAGEMENT","action":"Review only the original 14-minute draft and 45-second pilot, separate from unverified Maizen method; assign detailed shot owners.","gate":"DESK_PREPRO_DRAFT_NOT_G03_APPROVAL"},
            {"order":3,"owner":"SCRIPT_LOGIC","action":"Test river/map/valve/flood continuity in 21 original beat ledger; fix contradictions before script lock.","gate":"ORIGINAL_CONTENT_QC"},
            {"order":4,"owner":"TECHNICAL_DIRECTION","action":"After full source QC choose Blender authored vs licensed game staged vs hybrid using a first-party quality test.","gate":"G02_THEN_G13_AND_RIGHTS"},
            {"order":5,"owner":"PRODUCTION","action":"Only after source/method/rights greenlight create original game stage or voxel CGI and render the full 45s pilot with sound.","gate":"G02_G13_RIGHTS_QC"},
            {"order":6,"owner":"QC","action":"Review entire actual pilot audio/video, remake failed scenes, then consider 14-minute production.","gate":"ACTUAL_RENDER_QC_NOT_TESTS_ONLY"}
        ],
        "per_department_status":[{
            "department":key,"deliverable":a[0],"work_to_do":a[1],
            "acceptance":a[2],
            "desk_packet_generated":True,"autonomous_agent_completed_task":False,
            "source_based_conclusion_approved":g["cohort_gate_passed"],
            "actual_media_completed":False,"release_approved":False,
        } for key,a in ACTIONS.items()]
    }

def _bytes(data:dict)->bytes:
    return (json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode("utf-8")

def materialize_original_preproduction(output_dir:Path|None=None)->dict:
    """Create first-party original desk-ready files, immutable and SHA audited."""
    pkt=load_original_preproduction()
    report=maizen_next_company_stage()
    target=(output_dir if output_dir is not None else OUTPUT).resolve()
    if output_dir is None and not target.is_relative_to(ROOT.resolve()):
        raise ValueError("UNSAFE_DEFAULT_OUTPUT_PATH")
    if target.exists() and target.is_symlink():
        raise ValueError("UNSAFE_PREPRO_OUTPUT_SYMLINK")
    target.mkdir(parents=True,exist_ok=True)
    items=[]
    def write(path:str,data:dict):
        destination=target/path
        if destination.is_symlink():
            raise ValueError("OUTPUT_SYMLINK_BLOCKED")
        blob=_bytes(data);digest=sha256(blob).hexdigest()
        if destination.exists():
            if destination.read_bytes()!=blob:
                raise ValueError("EXISTING_PREPRO_ASSET_MODIFIED_"+path)
        else:
            destination.write_bytes(blob)
        items.append({"file":path,"sha256":digest,"bytes":len(blob)})
    write("original_story_and_21_beats.json",{
        "project_id":pkt["project_id"],"chapters":pkt["chapters"],
        "beats":pkt["beats"],"status":"UNRECORDED_ORIGINAL_SCREENPLAY_DRAFT",
        "source_provenance":"ONE_MAIZEN_FILM_ORIGINAL_AV_PROVISIONALLY_ANALYZED"
    })
    write("nine_pilot_shots.json",{
        "project_id":pkt["project_id"],"pilot_seconds":45,
        "shots":director_pilot_shots(),"status":"ANIMATIC_SHOT_MANIFEST_NOT_RENDERED",
    })
    write("asset_registry_needs.json",{
        "project_id":pkt["project_id"],"assets":pkt["asset_requirements"],
        "characters":pkt["characters"],"no_approved_model_licenses_or_generated_meshes":True,
        "stage":"PLANNED_ASSETS_NO_3D_ASSET_BUILT",
    })
    write("edit_audio_cue_timeline.json",{
        "project_id":pkt["project_id"],"duration_seconds":840,
        "cues":[{
            "beat":b["id"],"in":b["start"],"out":b["end"],
            "scratch_line":b["dialogue"],"sfx_music_notes":b["audio"],
            "picture_scene":b["location"],"state":"SPEECH_AND_SOUND_DESIGN_NOT_RECORDED",
        } for b in pkt["beats"]],"actual_audio_files_exist":False,
    })
    for dep in report["per_department_status"]:
        name="department_"+dep["department"].lower()+".json"
        write(name,{
            "project_id":pkt["project_id"],"department":dep["department"],
            "deliverable":dep["deliverable"],"input_artifacts":[
                "original_story_and_21_beats.json",
                "nine_pilot_shots.json",
                "asset_registry_needs.json",
                "edit_audio_cue_timeline.json",
            ],
            "task":dep["work_to_do"],"acceptance":dep["acceptance"],
            "source_gate_status":"NOT_APPROVED",
            "status":"DRAFT_HANDOFF_NOT_EXECUTED",
            "never_fake_26_agents_or_real_render":True,
        })
    write("company_stage_board.json",report)
    manifest={
        "schema":"cine.minecraft.maizen_original_prepro_receipts.v243",
        "project_id":pkt["project_id"],"artifact_count":len(items),
        "artifacts":items,"rendered_film_created":False,
        "source_gate_g02_approved":False,"any_actual_script_voice_recording":False,
        "no_paid_service_or_new_install":True,
        "note":"29 original work receipts (4 cross-department + 26 unique departments + board = 31); all desk only, no backend approved"
    }
    # Canonical count: 4 cross-department + 26 department + one board = 31.
    if len(items)!=31:
        raise ValueError("WRONG_NUMBER_OF_PRODUCTION_RECEIPTS")
    manifest["note"]="31 original SHA-bound desk receipts: four shared source-agnostic contracts, 26 department packets and one company board."
    dest=target/"manifest.json"
    blob=_bytes(manifest)
    if dest.exists():
        if dest.read_bytes()!=blob:
            raise ValueError("PREPRO_MANIFEST_CONFLICT")
    else:
        dest.write_bytes(blob)
    return {"schema":manifest["schema"],"destination":str(target),
            "department_receipts":26,"work_products_created_or_verified":31,
            "manifest_sha256":sha256(blob).hexdigest(),
            "any_render_started":False,
            "source_research_cohort_gate_approved":maizen_full_video_review_gate()["cohort_gate_passed"]}
