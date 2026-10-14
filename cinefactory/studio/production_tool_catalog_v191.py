from __future__ import annotations
"""Conservative tool discovery and niche blueprints; no invented benchmarks.

Host probes are read-only and do not install packages, call paid APIs, create
cloud accounts or start a renderer. Tool *presence* is not executable proof.
"""
import json
import shutil
import subprocess
from pathlib import Path
from pydantic import BaseModel, Field
from .production_selection_council import (
    ProductionSelectionCouncil, ShotToolRequest, Stage, ToolEvidence, ToolState,
)

LIC={
    "blender":"https://www.blender.org/about/license/",
    "godot":"https://godotengine.org/license/",
    "opentoonz":"https://github.com/opentoonz/opentoonz/blob/master/LICENSE.txt",
    "comfyui":"https://github.com/Comfy-Org/ComfyUI/blob/master/LICENSE",
    "ultralytics":"https://www.ultralytics.com/license",
    "remotion":"https://www.remotion.dev/docs/license/pricing",
    "ffmpeg":"https://ffmpeg.org/legal.html",
    "lmms":"https://github.com/LMMS/lmms/blob/master/LICENSE.txt",
    "obs":"https://github.com/obsproject/obs-studio/blob/master/COPYING",
    "sapi":"https://learn.microsoft.com/en-us/dotnet/api/system.speech.synthesis.speechsynthesizer",
}

class StageBlueprint(BaseModel):
    stage: Stage
    must_have: set[str]
    review_departments: list[str]=Field(default_factory=list)

class NicheBlueprint(BaseModel):
    niche_id: str
    display_name: str
    stage_sequence: list[StageBlueprint]
    key_qc: list[str]=Field(min_length=1)
    specialist_departments: list[str]=Field(min_length=1)
    rights_risks: list[str]=Field(min_length=1)
    children_audience: bool=False
    production_qualified: bool=False

def blueprint(niche,name,rows,qc,depts,risks,children=False)->NicheBlueprint:
    return NicheBlueprint(niche_id=niche,display_name=name,
        stage_sequence=[StageBlueprint(stage=Stage[s],must_have=set(tags),
           review_departments=list(depts)) for s,tags in rows],
        key_qc=list(qc),specialist_departments=list(depts),
        rights_risks=list(risks),children_audience=children)

NICHE_BLUEPRINTS={
    x.niche_id:x for x in [
        blueprint("preschool_3d_musical","Preschool 3D Original Musical",
            [("SCRIPT",["learning_objective","original_preschool_story"]),
             ("MUSIC",["original_song","beat_timeline"]),
             ("VOICE",["authorized_child_safe_vocal"]),
             ("CHARACTER_RIG",["organic_face_rig","original_character_ip"]),
             ("ANIMATION",["beat_choreography","lip_viseme_singing","identity_stable"]),
             ("EDITORIAL",["timeline_compositing","audio_mux"]),
             ("FINAL_QC",["child_safety_review","education_accuracy","music_rights"])],
            ["beat_and_syllable_alignment","age_appropriate_learning","dance_quality","character_continuity"],
            ["Early Childhood Curriculum","Original IP","Music","3D Animation","Child Safety"],
            ["original_music_ownership","made_for_kids","never_clone_cocomelon_characters"],True),
        blueprint("minecraft","Minecraft Original Animation",
            [("SCRIPT",["original_story"]),("CHARACTER_RIG",["voxel_rig"]),
             ("ANIMATION",["voxel_rig","identity_stable"]),("EDITORIAL",["timeline_compositing"])],
            ["character_identity","rig_intersection","camera_grammar","narrative_continuity"],
            ["Writing","Art","3D Animation","Technical QC"],["game_asset_rights","original_scripting"]),
        blueprint("roblox_animation","Roblox Original R6/R15 Animation",
            [("CHARACTER_RIG",["r6_rig"]),("ANIMATION",["identity_stable","r6_rig"]),
             ("EDITORIAL",["timeline_compositing"])],
            ["r6_skin_integrity","shot_continuity","prop_intersections"],
            ["Writing","Rigging","3D Animation"],["roblox_ip_and_asset_rights"]),
        blueprint("animal_animation","3D Original Animal Animation",
            [("CHARACTER_RIG",["animal_skeleton"]),("ANIMATION",["animal_behavior","physics"]),
             ("EDITORIAL",["timeline_compositing"])],
            ["animal_anatomy","body_poses","occlusions","motion_smoothness"],
            ["Creature Design","Animation","Simulation"],["licensed_models","unique_story"]),
        blueprint("long_slices_game","Long Slide / Physics Game",
            [("GAME_RUNTIME",["physics_sim","obstacle_course","camera_tracking"]),
             ("EDITORIAL",["timeline_compositing"])],
            ["contact_collision","course_finish","tracking_camera","rerun_same_seed"],
            ["Game Design","Physics","Gameplay Capture"],["asset_license","original_gameplay"]),
        blueprint("gta_gameplay","GTA Authentic Gameplay",
            [("GAME_RUNTIME",["authentic_gameplay"]),("CAPTURE",["real_game_recording"]),
             ("EDITORIAL",["timeline_compositing"])],
            ["authentic_runtime","capture_stability","legal_gameplay_access"],
            ["Gameplay","Capture","Editing"],["publisher_content_rules","no_stolen_footage"]),
        blueprint("ai_family_drama","AI Cinematic Fiction",
            [("SCRIPT",["original_story"]),("AI_VIDEO",["identity_conditioning","continuity"]),
             ("EDITORIAL",["timeline_compositing"])],
            ["character_consistency","face_hands_morph","style_continuity","fictional_identity"],
            ["Writing","AI Film","Continuity","Editorial"],["model_and_training_rights","no_reference_copy"]),
        blueprint("2d_cartoon","2D Original Cartoon",
            [("GRAPHICS_2D",["2d_character_animation"]),("VOICE",["speech_narration"]),
             ("EDITORIAL",["timeline_compositing"])],
            ["readable_composition","timing","visual_identity"],
            ["Storyboarding","2D Animation","Audio"],["original_illustrations"]),
        blueprint("asmr_sleep_hands_objects","Hand/Object ASMR Sleep",
            [("CAPTURE",["real_hand_capture","microphone_recording"]),
             ("AUDIO_POST",["low_noise","click_removal"]),("EDITORIAL",["timeline_compositing"])],
            ["noise_floor","no_harsh_transients","realistic_audio","consent"],
            ["Capture","Microphone Engineering","Sound Mastering"],["performer_consent","recording_rights"]),
        blueprint("audio_storytelling_seniors","Senior-friendly Longform Storytelling",
            [("SCRIPT",["original_story","rights_check"]),("VOICE",["speech_narration"]),
             ("AUDIO_POST",["loudness_measure"]),("EDITORIAL",["timeline_compositing"])],
            ["pronunciation","intelligibility","chapter_consistency","copyright"],
            ["Writing","Voice","Sound","Accessibility"],["text_rights","voice_consent"]),
        blueprint("rain_sleep_white_noise","Rain Sleep and White Noise",
            [("AUDIO_POST",["loop_clean","loudness_measure"]),
             ("EDITORIAL",["timeline_compositing"])],
            ["transient_free_loop","no_flicker","longform_ambience","source_authenticity"],
            ["Soundscape","Mastering","Editor"],["audio_source_license"]),
        blueprint("fishing_silent","Authentic Silent Fishing",
            [("CAPTURE",["camera_recording"]),
             ("AUDIO_POST",["low_noise"]),("EDITORIAL",["timeline_compositing"])],
            ["genuine_footage","on_location_safety","natural_audio"],
            ["Location Capture","Editing","Sound"],["footage_rights","location_consent"]),
        blueprint("daily_english","Daily English Learning",
            [("SCRIPT",["education_accuracy"]),("VOICE",["speech_narration"]),
             ("GRAPHICS_2D",["typography_animation"]),("EDITORIAL",["timeline_compositing"])],
            ["spoken_language_accuracy","subtitle_alignment","curriculum_fit"],
            ["Education","Language Expert","Motion Graphics"],["example_content_originality"]),
    ]
}


def host_inventory(root: str|Path)->dict:
    root=Path(root).resolve()
    found={name:shutil.which(name) for name in
           ("python","ffmpeg","ffprobe","node","npm","godot","godot4",
            "opentoonz","obs64","blender","reaper","audacity","lmms")}
    blender=root/".tools"/"blender-4.5.14-windows-x64"/"blender.exe"
    comfy=root/".tools"/"ComfyUI"
    def version(binary,args):
        if not binary:return None
        try:
            completed=subprocess.run([str(binary),*args],
                capture_output=True,text=True,timeout=9,check=False)
            return completed.stdout.splitlines()[0][:160] if completed.returncode==0 and completed.stdout else None
        except (OSError,subprocess.TimeoutExpired):
            return None
    blender_version=version(blender,["-b","--version"]) if blender.is_file() else None
    ffmpeg_version=version(found["ffmpeg"],["-version"])
    return {
        "root":str(root),"path_executables":found,
        "blender_binary":str(blender) if blender.is_file() else None,
        "blender_version_probe":blender_version,
        "ffmpeg_version_probe":ffmpeg_version,
        "comfyui_folder_exists":comfy.is_dir(),
        "comfyui_video_workflow_executable_verified":False,
        "godot_runtime_verified":False,
        "remotion_executable_verified":False,
        "no_paid_api_automatically_enabled":True,
        "inventory_not_proof_of_niche_quality":True,
    }


def candidate_catalog(root: str|Path,inventory:dict|None=None)->list[ToolEvidence]:
    root=Path(root).resolve()
    h=inventory if inventory is not None else host_inventory(root)
    blender_ok=bool(h.get("blender_version_probe"))
    ffmpeg_ok=bool(h.get("ffmpeg_version_probe"))
    present_comfy=bool(h.get("comfyui_folder_exists"))
    def tool(method,tool_id,stage,tags,*,niches=("*",),state=ToolState.DISCOVERED,
             exe=None,approved=False,license_key=None,note="",costly=False):
        return ToolEvidence(
            method_id=method,tool_id=tool_id,stage=stage,
            supported_niches=set(niches),capability_tags=set(tags),
            state=state,license_approved=approved,
            license_source_url=LIC.get(license_key or tool_id),
            license_note=note or "LICENSE_REVIEW_REQUIRED",
            executable_evidence=exe,
            paid_api_required=costly,
            notes=["CANDIDATE_NOT_SCOPED_BENCHMARKED"],
        )
    bstate=ToolState.EXECUTABLE if blender_ok else ToolState.DISCOVERED
    fstate=ToolState.EXECUTABLE if ffmpeg_ok else ToolState.DISCOVERED
    return [
        tool("blender.voxel.render","blender",Stage.ANIMATION,
             ("voxel_rig","r6_rig","identity_stable"),niches=("minecraft","roblox_animation"),
             state=bstate,exe=str(root/".tools"/"blender-4.5.14-windows-x64"/"blender.exe") if blender_ok else None,
             approved=True,note="GPL_ENGINE_OUTPUT_USE_PERMITTED_BUT_ASSETS_REVIEW_SEPARATE"),
        tool("blender.organic.musical","blender",Stage.ANIMATION,
             ("organic_face_rig","beat_choreography","lip_viseme_singing","identity_stable"),
             niches=("preschool_3d_musical",),state=ToolState.PRESENT if blender_ok else ToolState.DISCOVERED,
             approved=True,note="BLENDER_ENGINE_OK_ORGANIC_SINGING_PIPELINE_NOT_BUILT"),
        tool("blender.voxel.rig","blender",Stage.CHARACTER_RIG,
             ("voxel_rig","r6_rig"),niches=("minecraft","roblox_animation"),
             state=bstate,exe=str(root/".tools"/"blender-4.5.14-windows-x64"/"blender.exe") if blender_ok else None,
             approved=True,note="BLENDER_ENGINE_OUTPUT_OK_RIG_AND_ASSET_RIGHTS_SEPARATE"),
        tool("blender.preschool.rig","blender",Stage.CHARACTER_RIG,
             ("organic_face_rig","original_character_ip"),niches=("preschool_3d_musical",),
             state=ToolState.PRESENT if blender_ok else ToolState.DISCOVERED,
             approved=True,note="REQUIRES_NEW_ORIGINAL_ORGANIC_RIG_PRODUCTION"),
        tool("ffmpeg.editorial","ffmpeg",Stage.EDITORIAL,("timeline_compositing","audio_mux","encode"),
             state=fstate,exe=h["path_executables"].get("ffmpeg") if ffmpeg_ok else None,
             note="EXACT_LOCAL_FFMPEG_BUILD_LICENSE_AND_CODEC_OPTIONS_UNREVIEWED"),
        tool("ffmpeg.audio.post","ffmpeg",Stage.AUDIO_POST,("loop_clean","loudness_measure","low_noise"),
             state=fstate,exe=h["path_executables"].get("ffmpeg") if ffmpeg_ok else None,
             note="SOURCE_AUDIO_RIGHTS_AND_QUALITY_QC_NOT_VERIFIED"),
        tool("godot.physics.runtime","godot",Stage.GAME_RUNTIME,
             ("physics_sim","obstacle_course","camera_tracking"),
             niches=("long_slices_game",),
             state=ToolState.PRESENT if h["path_executables"].get("godot") else ToolState.DISCOVERED,
             approved=True,note="MIT_LICENSE_TOOL_BUT_NO_RUNTIME_SHOT_BENCHMARK"),
        tool("game.authentic.capture","game_runtime",Stage.GAME_RUNTIME,("authentic_gameplay",),
             niches=("gta_gameplay",),note="REQUIRES_LICENSED_REAL_GAME_RUNTIME"),
        tool("obs.real.capture","obs",Stage.CAPTURE,
             ("real_game_recording","camera_recording","microphone_recording","real_hand_capture"),
             state=ToolState.PRESENT if h["path_executables"].get("obs64") else ToolState.DISCOVERED,
             note="CAPTURE_HARDWARE_AND_PERSON_CONSENT_NEEDED"),
        tool("comfy.video.workflow","comfyui",Stage.AI_VIDEO,
             ("identity_conditioning","continuity"),niches=("ai_family_drama",),
             state=ToolState.PRESENT if present_comfy else ToolState.DISCOVERED,
             note="COMFYUI_FOLDER_ONLY_NO_VIDEO_WORKFLOW_GPU_BENCHMARK_MODEL_LICENSE_SEPARATE"),
        tool("opentoonz.2d","opentoonz",Stage.GRAPHICS_2D,
             ("2d_character_animation","typography_animation"),
             state=ToolState.PRESENT if h["path_executables"].get("opentoonz") else ToolState.DISCOVERED,
             approved=True,note="BSD_3_CLAUSE_CORE_THIRD_PARTY_ASSETS_REVIEW"),
        tool("remotion.motion","remotion",Stage.GRAPHICS_2D,("typography_animation","2d_character_animation"),
             note="COMPANY_SIZE_AND_AUTOMATION_LICENSE_CONDITIONAL"),
        tool("original.composer","composer",Stage.MUSIC,("original_song","beat_timeline"),
             niches=("preschool_3d_musical",),
             note="NO_PROVEN_LYRICS_MELODY_VOCAL_MUSIC_PRODUCTION_CHAIN"),
        tool("licensed.singer","human_voice",Stage.VOICE,("authorized_child_safe_vocal",),
             niches=("preschool_3d_musical",),note="CONSENT_PERFORMANCE_VOCAL_MUSIC_RIGHTS_REQUIRED"),
        tool("local.sapi.speech","sapi",Stage.VOICE,("speech_narration",),
             state=ToolState.PRESENT,note="SAPI_CAN_SPEAK_NOT_CERTIFIED_AS_SINGING_OR_ANY_LANGUAGE"),
        tool("qualified.writing.room","writers_room",Stage.SCRIPT,
             ("original_story","education_accuracy","learning_objective","original_preschool_story","rights_check"),
             note="HUMAN_VALIDATED_CREATIVE_SCRIPT_OUTPUT_REQUIRED"),
        tool("pocketsphinx.audio.qc","pocketsphinx",Stage.FINAL_QC,
             ("speech_timing","word_proxy"),state=ToolState.PRESENT,
             note="LEXICON_CONDITIONED_NOT_INDEPENDENT_WORD_CERTIFICATION"),
        tool("preschool.review","human_review",Stage.FINAL_QC,
             ("child_safety_review","education_accuracy","music_rights"),niches=("preschool_3d_musical",),
             note="EARLY_CHILDHOOD_EXPERT_AND_LICENSE_CHECK_REQUIRED"),
    ]


def niche_recommendations(root: str|Path,niche_id:str,*,intent="RESEARCH")->dict:
    if niche_id not in NICHE_BLUEPRINTS:
        return {"status":"BLOCKED_UNKNOWN_NICHE","niche_id":niche_id,
                "required_action":"Niche research conference must define a signed blueprint",
                "production_authorized":False}
    inv=host_inventory(root)
    council=ProductionSelectionCouncil(candidate_catalog(root,inv))
    niche=NICHE_BLUEPRINTS[niche_id]
    steps=[]
    for idx,item in enumerate(niche.stage_sequence):
        decision=council.advise(ShotToolRequest(
            project_id="NICHE_EXPLORATION",niche_id=niche_id,
            shot_id=f"stage_{idx+1:02d}_{item.stage}",
            stage=item.stage,required_capabilities=item.must_have,
            is_made_for_kids=niche.children_audience,
            intent=intent,
        ))
        steps.append({"stage":item.stage.value,"capabilities":sorted(item.must_have),
                      "department_review":item.review_departments,
                      "selection":decision.model_dump(mode="json")})
    return {
        "status":"NICHE_STUDY_NOT_PRODUCTION_CERTIFIED",
        "niche":niche.model_dump(mode="json"),"inventory":inv,
        "stage_decisions":steps,"production_authorized":False,
        "unverified_stage_count":sum(
            x["selection"]["status"]!="PRODUCTION_METHOD_SELECTED"
            for x in steps),
    }


class ProductionPortfolioAdvisor:
    """Lazy read-only front door from the existing ProfessionalCompanyLayer.

    Research never executes a method. Existing SceneConference/MethodSwitch
    remains responsible for any separately authorised executable selection.
    """
    def __init__(self,root: str|Path):
        self.root=Path(root).resolve()

    def niche_report(self,niche_id:str,*,intent:str="RESEARCH")->dict:
        return niche_recommendations(self.root,niche_id,intent=intent)

    def stage_report(self,request:ShotToolRequest):
        inventory=host_inventory(self.root)
        return ProductionSelectionCouncil(
            candidate_catalog(self.root,inventory)
        ).advise(request)
