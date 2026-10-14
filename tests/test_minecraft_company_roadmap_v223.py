"""v223 MineFactory two-lane reference film study and 26-department plan."""
import json
from typer.testing import CliRunner
import pytest
from cinefactory.cli import app
from cinefactory.studio.contracts import DepartmentId
from cinefactory.studio.minecraft_company_roadmap_v223 import (
    load_minecraft_master_company_plan,minecraft_company_roadmap,
    minecraft_next_approved_step,PHASES
)
from cinefactory.studio.claude_mcp_gateway_v218 import build_server

def test_exact_26_existing_departments_28_complete_gates_and_rights():
    data=load_minecraft_master_company_plan()
    assert len(data["departments"])==26
    assert {d["id"] for d in data["departments"]}=={x.value for x in DepartmentId}
    assert len(data["master_steps"])==28
    assert {s["phase"] for s in data["master_steps"]}==set(PHASES)
    assert all(s["blocking_acceptance"] and s["receipt"] for s in data["master_steps"])
    assert data["policy"]["owner_credit_budget_usd"]==0
    assert not data["policy"]["allow_autopublish"]
    assert not data["policy"]["allow_competitor_asset_reproduction"]

def test_two_truthful_lanes_no_fabricated_gameplay_or_renderer_claims():
    d=load_minecraft_master_company_plan()
    lanes={r["id"]:r for r in d["lanes"]}
    assert lanes["SCRIPTED_MINECRAFT_GAMEPLAY"]["requires_real_minecraft_runtime"]
    assert not lanes["AUTHORED_VOXEL_3D_ANIMATION"]["requires_real_minecraft_runtime"]
    assert not any(x["media_ready"] for x in lanes.values())
    assert all(x["minimum_pilot_seconds"]==45 for x in lanes.values())

def test_three_exact_official_video_cases_no_fake_viewing():
    d=load_minecraft_master_company_plan()
    lookup={x["id"]:x for x in d["reference_videos"]}
    assert lookup["maizen_choose_right_hole_2026"]["url"].endswith("ZmT0ITUGUII")
    assert lookup["maizen_house_inside_bed_2025"]["url"].endswith("zhPBXzHsLuo")
    assert lookup["bigschool_season3_compilation_2020"]["url"].endswith("X09yxFuKLAs")
    assert len(lookup["bigschool_season3_compilation_2020"]["public_description_chapters"])==7
    assert all(not x["viewed_full_video"] and not x["heard_full_audio"] for x in lookup.values())
    assert "SNAPSHOT" in lookup["maizen_choose_right_hole_2026"]["views_provenance"]

def test_6_original_video_ideas_and_timed_v222_art_study_not_reused_characters():
    d=load_minecraft_master_company_plan()
    assert len(d["original_video_queue"])==6
    assert len({x["id"] for x in d["original_video_queue"]})==6
    assert all(x["status"] in ("ORIGINAL_PITCH_NOT_PRODUCED","STORYBOARD_ONLY_45S")
               for x in d["original_video_queue"])
    assert d["verified_historical_baseline"]["hard_blockers"]==12
    assert d["verified_historical_baseline"]["duration_seconds"]==2

def test_lane_dept_and_phase_scoped_company_report():
    report=minecraft_company_roadmap(lane="AUTHORED_VOXEL_3D_ANIMATION",
                                     phase="PREPRO")
    assert report["all_steps"]==28
    assert report["all_departments"]==26
    assert len(report["ordered_steps"])>=5
    assert all(s["phase"]=="PREPRO" for s in report["ordered_steps"])
    assert len(report["referenced_video_metadata"])==1
    assert all("full_video_watched" in x and x["full_video_watched"] is False
               for x in report["referenced_video_metadata"])
    assert all(x["lane"]=="AUTHORED_VOXEL_3D_ANIMATION"
               for x in report["original_video_ideas"])
    assert not report["publication_authorized"]

def test_first_step_cannot_skip_incomplete_metadata_and_media_review():
    for lane in ("SCRIPTED_MINECRAFT_GAMEPLAY","AUTHORED_VOXEL_3D_ANIMATION"):
        step=minecraft_next_approved_step(lane)
        assert step["current_step"]=="G01"
        assert step["requires_real_footage"]
        assert not step["may_claim_competitor_video_watched"]
        assert not step["may_publish_full_episode"]

def test_cli_and_mcp_expose_readonly_roadmap():
    cli=CliRunner()
    out=cli.invoke(app,["minecraft-company-roadmap","--lane",
                       "SCRIPTED_MINECRAFT_GAMEPLAY","--phase","RESEARCH"])
    assert out.exit_code==0,str(out.exception)
    j=json.loads(out.output)
    assert j["all_steps"]==28
    assert len(j["ordered_steps"])==4
    block=cli.invoke(app,["minecraft-company-roadmap","--lane",
                       "AUTHORED_VOXEL_3D_ANIMATION","--blockers-only"])
    assert block.exit_code==0,str(block.exception)
    assert json.loads(block.output)["current_step"]=="G01"
    assert "minecraft_company_roadmap" in build_server()._tool_manager._tools
    assert "minecraft_next_approved_step" in build_server()._tool_manager._tools

def test_unexpected_lane_phase_fail_closed():
    with pytest.raises(ValueError,match="UNKNOWN_MINECRAFT_LANE"):
        minecraft_company_roadmap(lane="UNKNOWN")
    with pytest.raises(ValueError,match="UNKNOWN_MINECRAFT_PHASE"):
        minecraft_company_roadmap(phase="PUBLISH_WITHOUT_QC")


def test_niche_technology_report_contains_exact_lane_without_gameplay_relabel():
    from cinefactory.studio.niche_technology_strategy_v213 import prepare_niche_technology_strategy
    animated=prepare_niche_technology_strategy("minecraft_school_comedy")
    assert animated["minecraft_two_lane_company_roadmap"]["lane"]=="AUTHORED_VOXEL_3D_ANIMATION"
    assert animated["minecraft_two_lane_company_roadmap"]["all_steps"]==28
    gameplay=prepare_niche_technology_strategy("minecraft_scripted_machinima")
    assert gameplay["minecraft_two_lane_company_roadmap"]["lane"]=="SCRIPTED_MINECRAFT_GAMEPLAY"
    assert gameplay["minecraft_original_animation_research"] is None
    control=prepare_niche_technology_strategy("long_slices_game")
    assert control["minecraft_two_lane_company_roadmap"] is None
