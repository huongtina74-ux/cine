import copy
import json
import pytest
from cinefactory.production.studio_director import build_studio_production_plan

def brief():
    return {
        "schema":"cine.studio.creative_brief.v1",
        "project_id":"minecraft_premium_pilot",
        "niche":"Minecraft animation","audience":"English longform adults and teens",
        "creative_intent":"Original comedy mystery with an emotionally satisfying resolution",
        "originality_statement":"New world, characters and new story beats, not copied from another channel",
        "episode_premise":"One friend hides an impossible secret, forcing the other to choose between trust and proof",
        "quality_profile":"cinema_flagship",
        "competitor_research_revision":"source_hash_reviewable_20261009",
        "episode_beat_plan":[
            "A suspicious light appears during a peaceful village festival",
            "The hero follows conflicting clues and makes a consequential mistake",
            "The hero repairs trust with a new original solution that pays off the opening"],
        "script_editor_approved":True,
        "studio_budget_approved":False,"original_asset_rights_cleared":False,
        "character_bible":{"actor01":{
            "identity_asset_id":"hero_rig_v1","silhouette":"voxel shape with unique face",
            "rig_version":"1.0","expression_set":["fear","shock","joy"],
            "wardrobe_state":"blue jacket"}},
        "shots":[{
            "shot_id":"S001","scene_kind":"character_dialogue","duration_seconds":8,
            "characters":["actor01"],"scene_goal":"Show fear while maintaining character empathy",
            "script_beat":"Hero notices a strange signal and responds with nervous resolve",
            "location_id":"mystery_cabin_day","blocking":"Hero enters from left, rotates to camera",
            "camera_plan":"Medium push-in 35mm equivalent, eye level, cut to close reaction",
            "lighting_plan":"Warm backlight, cool motivated door fill",
            "sound_plan":"Quiet footsteps, room tone, short tension sting",
            "transition_in":"J cut from previous question",
            "transition_out":"L cut into witness reaction",
            "storyboard_reference":"S001_board_rev1.png",
            "storyboard_approved":True,
            "emotion_beats":[{"second":0,"emotion":"uncertain"},
                             {"second":4,"emotion":"startled"}],
            "expression_animation":"eye widening, shoulders lift, jaw reaction",
            "performance_direction":"held eye contact then reactive recoil",
            "continuity_state":"blue jacket, same rig and cabin door positions",
        }],
    }


def test_flagship_routes_actor_to_deterministic_3d_and_does_not_claim_capability(tmp_path):
    report=build_studio_production_plan(brief(),{"schema":"cine.studio.capability_registry.v1","lanes":{}},tmp_path/"plan.json")
    assert report["state"]=="PLANNED_BLOCKED_TOOL_BENCHMARK"
    shot=report["shots"][0]
    assert shot["primary_lane"]=="blender_character_animation"
    assert "ExpressionEngine" in shot["candidate_tools"]
    assert shot["technical_route_state"]=="NOT_EXECUTABLE_UNTIL_CAPABILITY_VERIFIED"
    assert shot["creative_work_order_state"]=="DIRECTOR_PACK_COMPLETE_REVIEW_STILL_REQUIRED"
    assert report["quality_accepted"] is False
    assert report["production_permission"] is False


def test_never_hardcode_3060_and_allows_multi_gpu_pool(tmp_path):
    cap={"schema":"cine.studio.capability_registry.v1",
         "resource_pool":[
            {"worker_id":"gpu_a","gpu_model":"RTX 5090","vram_gb":32},
            {"worker_id":"gpu_b","gpu_model":"H100","vram_gb":80}],
         "lanes":{"blender_character_animation":{
            "state":"BENCHMARKED_READY","evidence_ref":"sha256:bench_result_real",
            "tested_tool_version":"Blender 5.0","measured_seconds_per_output_second":0.4}}}
    b=brief()
    b["studio_budget_approved"]=True
    b["original_asset_rights_cleared"]=True
    result=build_studio_production_plan(b,cap,tmp_path/"plan.json")
    assert result["state"]=="READY_FOR_DEPARTMENT_REVIEW_NOT_PRODUCTION"
    assert result["shots"][0]["technical_route_state"]=="CAPABILITY_BENCHMARKED"
    assert "MULTI_GPU" in result["gpu_policy"]
    assert result["production_permission"] is False


def test_fails_closed_when_script_and_expression_missing(tmp_path):
    b=brief()
    b["shots"][0]["script_beat"]=""
    b["shots"][0]["emotion_beats"]=[]
    b["shots"][0]["storyboard_approved"]=False
    result=build_studio_production_plan(b,{"schema":"cine.studio.capability_registry.v1","lanes":{}},tmp_path/"bad.json")
    assert result["state"]=="PLANNED_BLOCKED_CREATIVE_REQUIREMENTS"
    assert "script_beat" in result["shots"][0]["missing"]
    assert "emotion_beats" in result["shots"][0]["missing"]
    assert "STORYBOARD_NOT_APPROVED" in result["shots"][0]["missing"]


def test_same_character_requires_complete_bible(tmp_path):
    b=brief()
    b["character_bible"]["actor01"].pop("rig_version")
    result=build_studio_production_plan(b,{"schema":"cine.studio.capability_registry.v1","lanes":{}},tmp_path/"bad.json")
    assert "INCOMPLETE_CHARACTER_BIBLE:actor01" in result["shots"][0]["missing"]


def test_two_character_cinematic_action_prefers_rigged_scene(tmp_path):
    b=brief()
    b["character_bible"]["actor02"]=dict(b["character_bible"]["actor01"])
    b["shots"][0]["characters"]=["actor01","actor02"]
    b["shots"][0]["scene_kind"]="cinematic_action"
    out=build_studio_production_plan(b,{"schema":"cine.studio.capability_registry.v1","lanes":{}},tmp_path/"plan.json")
    assert out["shots"][0]["primary_lane"]=="blender_character_animation"


@pytest.mark.parametrize("niche,kind,lane",[
    ("Long Slide Game","physics_simulation","game_engine_capture"),
    ("ASMR sleep","tactile_asmr","physical_camera_capture"),
    ("Rain sleep","rain_ambience","audio_environment"),
    ("English learning","educational_explainer","remotion_graphics"),
    ("Film montage","stylized_montage","comfyui_controlled_ai_video"),
])
def test_niche_specific_lane_not_forced_to_one_model(tmp_path,niche,kind,lane):
    b=brief()
    b["niche"]=niche
    b["shots"][0]["scene_kind"]=kind
    b["shots"][0]["characters"]=[]
    report=build_studio_production_plan(b,{"schema":"cine.studio.capability_registry.v1","lanes":{}},tmp_path/"out.json")
    assert report["shots"][0]["primary_lane"]==lane
    assert report["production_permission"] is False


def test_unrecognized_niche_explicitly_requires_blueprint(tmp_path):
    b=brief(); b["niche"]="New undiscovered niche"
    report=build_studio_production_plan(b,{"schema":"cine.studio.capability_registry.v1","lanes":{}},tmp_path/"plan.json")
    assert "NEW_NICHE_NEEDS_A_DIRECTOR_REVIEWED_PRODUCTION_BLUEPRINT" in report["project_findings"]


def test_duplicate_or_bad_shots_cannot_pass(tmp_path):
    b=brief()
    b["shots"].append(copy.deepcopy(b["shots"][0]))
    with pytest.raises(ValueError,match="Duplicate"):
        build_studio_production_plan(b,{"schema":"cine.studio.capability_registry.v1","lanes":{}},tmp_path/"out.json")
    assert not (tmp_path/"out.json").exists()


def test_does_not_overwrite_original_plan(tmp_path):
    b=brief()
    cap={"schema":"cine.studio.capability_registry.v1","lanes":{}}
    build_studio_production_plan(b,cap,tmp_path/"plan.json")
    with pytest.raises(FileExistsError):
        build_studio_production_plan(b,cap,tmp_path/"plan.json")


def test_rejects_incomplete_episode_arc_even_when_shots_are_filled(tmp_path):
    b=brief()
    b["episode_beat_plan"]=[]
    b["studio_budget_approved"]=True
    b["original_asset_rights_cleared"]=True
    cap={"schema":"cine.studio.capability_registry.v1","lanes":{"blender_character_animation":{
        "state":"BENCHMARKED_READY","evidence_ref":"sha256:real_independent_execution",
        "tested_tool_version":"Blender 5.0"}}}
    report=build_studio_production_plan(b,cap,tmp_path/"bad.json")
    assert report["state"]=="PLANNED_BLOCKED_PROJECT_APPROVALS"
    assert "EPISODE_NEEDS_AT_LEAST_THREE_SUBSTANTIVE_DIRECTED_BEATS" in report["project_findings"]


def test_rights_and_budget_not_silently_approved(tmp_path):
    b=brief()
    cap={"schema":"cine.studio.capability_registry.v1","lanes":{"blender_character_animation":{
        "state":"BENCHMARKED_READY","evidence_ref":"sha256:real_independent_execution",
        "tested_tool_version":"Blender 5.0"}}}
    report=build_studio_production_plan(b,cap,tmp_path/"plan.json")
    assert report["state"]=="PLANNED_BLOCKED_PROJECT_APPROVALS"
    assert "ASSET_AND_CHARACTER_RIGHTS_NOT_CLEARED" in report["project_findings"]
