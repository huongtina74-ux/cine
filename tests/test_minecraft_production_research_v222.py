"""v222 factual Minecraft research: original video evidence, provenance and pilot storyboard."""
import json
from pathlib import Path
import pytest
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio import minecraft_production_research_v222 as module
from cinefactory.studio.claude_mcp_gateway_v218 import build_server


def test_existing_real_mp4_and_sha_must_match_original_receipt():
    d=module.minecraft_research_conference()
    video=d["existing_render_video"]
    assert video["exists"]
    assert video["sha256_matches_receipt"]
    assert video["has_original_receipt"] and video["has_art_qc_report"]
    assert video["has_three_shot_contact_sheet"]
    assert video["duration_seconds"]==2.0
    assert video["resolution"]==[960,540] and video["fps"]==24
    assert video["art_review"]=="BLOCKED_MINECRAFT_ART_PRODUCTION"
    assert video["recorded_blocker_count"]==12
    assert not d["pipeline_approval"]


def test_no_competitor_workflow_can_be_attributed_without_watching():
    d=module.minecraft_research_conference()
    assert len(d["competitor_research"])==3
    assert all(not r["full_video_and_audio_inspected"] and
               not r["exact_production_tool_verified"]
               for r in d["competitor_research"])
    assert d["actual_competitor_full_video_evidence"] is False
    assert d["future_minecraft_8min_breakout_validated"] is False


def test_technical_workflow_source_provenance_and_missing_qualifications():
    d=module.minecraft_research_conference()
    assert len(d["reviewed_technology_candidates"])==9
    tech={r["id"]:r for r in d["reviewed_technology_candidates"]}
    assert tech["existing_blender_4_5"]["installed_checked"]
    assert tech["blockbench_original_assets"]["priority"]=="P0"
    assert tech["mcprep"]["priority"]=="HOLD"
    assert tech["blender_lab_mcp"]["priority"]=="HOLD"
    assert all(not x["production_qualified"] for x in tech.values())


def test_proposed_45s_10shot_story_timing_is_locked_not_fabricated_media():
    scene=module.original_minecraft_pilot_storyboard()
    assert scene["shot_count"]==10
    assert scene["duration_seconds"]==45
    assert [r["start_seconds"] for r in scene["shots"]]==[0,4,8,12,17,22,27,32,37,41]
    assert scene["shots"][-1]["end_seconds"]==45
    assert not scene["publishable"] and not scene["has_real_45_second_media"]


def test_mcp_and_cli_include_readonly_study_only():
    server=build_server()
    assert "minecraft_research_conference" in server._tool_manager._tools
    assert "original_minecraft_pilot_storyboard" in server._tool_manager._tools
    cli=CliRunner()
    res=cli.invoke(app,["minecraft-production-research"])
    assert res.exit_code==0,str(res.exception)
    payload=json.loads(res.output)
    assert payload["existing_render_video"]["sha256_matches_receipt"]
    assert not payload["paid_ai_authorized"]
    preview=cli.invoke(app,["minecraft-production-research","--storyboard"])
    assert preview.exit_code==0,str(preview.exception)
    assert json.loads(preview.output)["shot_count"]==10


def test_reject_misleading_full_watch_or_production_override(monkeypatch):
    board=module.load_minecraft_research_board()
    assert board["policy"]["publish_approval"] is False
    assert board["policy"]["report_actual_full_competitor_viewing"] is False
    assert board["pilot_plan"]["allow_production_promotion"] is False


def test_all_paths_restricted_within_repo_and_missing_files_not_verified():
    with pytest.raises(ValueError,match="OUTSIDE_ROOT"):
        module._file_status("../../Windows/System32/drivers/etc/hosts")
    f=module._file_status("data/verification/no_file_v222.mp4","a"*64)
    assert f["exists"] is False
    assert f["sha256_matches_receipt"] is False


def test_existing_niche_strategy_displays_minecraft_actual_art_receipts():
    from cinefactory.studio.niche_technology_strategy_v213 import prepare_niche_technology_strategy
    plan=prepare_niche_technology_strategy("minecraft_story_adventure")
    s=plan["minecraft_original_animation_research"]
    assert s["existing_render_video"]["sha256_matches_receipt"]
    assert s["existing_render_video"]["recorded_blocker_count"]==12
    assert not s["pipeline_approval"] and not plan["production_permission"]
    school=prepare_niche_technology_strategy("minecraft_school_comedy")
    assert school["minecraft_original_animation_research"]["pilot_seconds"]==45
    other=prepare_niche_technology_strategy("minecraft_recorded_survival")
    assert other["minecraft_original_animation_research"] is None
