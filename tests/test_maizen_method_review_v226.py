"""v226: Correct Maizen-style stage assumptions with official evidence and honest uncertainty."""
import json
import pytest
from typer.testing import CliRunner
from cinefactory.cli import app
from cinefactory.studio.maizen_method_review_v226 import (
    load_maizen_method_review, maizen_production_method_audit,
    maizen_shot_method_options,
)
from cinefactory.studio.minecraft_company_roadmap_v223 import minecraft_company_roadmap
from cinefactory.studio.claude_mcp_gateway_v218 import build_server
from cinefactory.studio.maizen_studio_kickoff_v225 import (
    load_maizen_studio_a, maizen_studio_status,
)

def test_official_sources_do_not_conflate_ingame_filming_with_raw_unplanned_play():
    plan=load_maizen_method_review()
    assert plan["production_default"]=="METHOD_UNDECIDED_COMPARE_STAGED_GAME_VS_OFFLINE_AUTHORED_CGI"
    sources={v["uri"]:v for v in plan["official_primary_sources"]}
    career=sources["https://maizen.com/video-recording-team/"]
    assert career["source_type"]=="MAIZEN_OFFICIAL"
    assert "unscripted" not in career["establishes"].lower()
    assert "no script" in career["does_not_establish"]
    assert "Blender as renderer" in career["does_not_establish"]
    obj=sources["https://maizen.com/downloads/"]
    assert "published videos rendered with Blender" in obj["does_not_establish"]

def test_no_global_minecraft_runtime_gate_for_offline_voxel_cinematic():
    report=maizen_production_method_audit()
    options={x["id"]:x for x in report["method_comparison"]}
    assert len(options)==3
    assert options["BLENDER_AUTHORED"]["game_license_required"] is False
    assert options["GAME_ENGINE_STAGED"]["game_license_required"] is True
    assert report["studio_3d_worker_requires_game_install"] is False
    assert report["minecraft_capture_remains_optional_method"]
    assert not report["production_approved"]

def test_per_shot_method_selection_still_requires_real_pilot_video():
    plan=maizen_production_method_audit()
    assert len(plan["shot_method_candidates"])==9
    assert all(not v["method_qualified"] and not v["real_media_exists"]
               for v in plan["shot_method_candidates"])
    for shot in ("P01","P03","P05","P09"):
        route=maizen_shot_method_options(shot)
        assert not route["game_runtime_always_required"]
        assert not route["real_shot_media_exists"]
        assert not route["approved_for_episode"]
    with pytest.raises(ValueError,match="UNKNOWN_MAIZEN_SHOT"):
        maizen_shot_method_options("../../../../system")

def test_very_old_v225_real_receipts_preserved_no_falsified_movie_review():
    old=load_maizen_studio_a()
    assert old["pilot"]["real_game_captured"] is False
    status=maizen_studio_status()
    assert not status["production_release_authorized"]
    fresh=maizen_production_method_audit()
    assert fresh["reference_full_video_audio_watched"] is False
    assert fresh["source_video_stream_probe"]["result"]=="REMOTE_VIDEO_STREAM_HTTP_403"
    assert fresh["transcript_access"]["credits_spent"]==0
    assert fresh["old_v225_handoff_receipts_preserved"]

def test_claude_tools_and_company_plan_reference_correction():
    server=build_server()
    assert "maizen_production_method_audit" in server._tool_manager._tools
    assert "maizen_shot_method_options" in server._tool_manager._tools
    c=minecraft_company_roadmap(lane="SCRIPTED_MINECRAFT_GAMEPLAY")
    assert c["maizen_production_method_correction"]["production_default"].startswith("METHOD_UNDECIDED")
    assert c["maizen_selected_studio_a_kickoff"]["project"]=="MAI01_WATERFALL"
    a=minecraft_company_roadmap(lane="AUTHORED_VOXEL_3D_ANIMATION")
    assert a["maizen_production_method_correction"] is None

def test_cli_source_audit_and_shot_action_return_readonly_recommendations():
    runner=CliRunner()
    full=runner.invoke(app,["maizen-method-audit"])
    assert full.exit_code==0,str(full.exception)
    val=json.loads(full.output)
    assert len(val["official_evidence"])==5
    assert val["credits_spent"]==0
    one=runner.invoke(app,["maizen-method-audit","--shot-id","P05"])
    assert one.exit_code==0,str(one.exception)
    s=json.loads(one.output)
    assert s["shot"]["id"]=="P05"
    assert s["decision"]=="PENDING_TWO_METHOD_STAGING_AND_VISUAL_AUDIO_QC"
