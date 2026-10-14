"""v228 regression: every competitor niche/video needs complete A/V evidence to conclude."""
import json

import pytest
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio.claude_mcp_gateway_v218 import build_server
from cinefactory.studio.universal_competitor_review_v228 import (
    competitor_full_review_gate, competitor_study_department_gate,
    load_studio_full_video_policy,
)
from cinefactory.studio.niche_technology_strategy_v213 import prepare_niche_technology_strategy


def test_policy_is_global_and_never_replaces_complete_av_with_metadata():
    p=load_studio_full_video_policy()
    assert "ALL_NICHES" in p["scope"]
    assert not p["discovery_requires_full_media"]
    assert p["deep_content_analysis_requires_complete_video_and_audio"]
    assert p["one_short_excerpt_is_never_full_video"]
    assert p["every_selected_reference_must_pass"]
    assert p["max_visual_audio_segment_seconds"]==30
    assert not p["authoritative_technology_attribution_from_pixels_alone"]
    assert not p["allow_auto_publish_after_research"]


@pytest.mark.parametrize("niche",[
    "minecraft_story_adventure", "minecraft_maizen", "roblox_animation",
    "long_slices_game","gta_gameplay","asmr_sleep_hands_objects",
    "rain_sleep_white_noise","daily_english","animal_animation",
    "ai_family_drama","fishing_silent",
])
def test_no_full_watch_means_no_competitor_method_conclusions(niche):
    g=competitor_full_review_gate(niche)
    assert g["discovery_metadata_and_growth_scanning_allowed"]
    assert not g["deep_full_episode_analysis_allowed"]
    assert not g["competitor_content_method_conclusions_allowed"]
    assert not g["competitor_production_backend_attribution_proven"]
    assert not g["metadata_thumbnails_short_clips_transcript_can_replace_full_av"]
    assert not g["seven_company_department_content_and_method_promotions_allowed"]


def test_all_selected_video_ids_must_be_fully_reviewed_not_one_viral_sample():
    ids=["zhPBXzHsLuo","oX6Azwe5QLg"]
    data=competitor_full_review_gate("long_slices_game",ids)
    assert data["references_required"]==2
    assert data["references_passed"]==0
    assert set(x["video_id"] for x in data["video_statuses"])==set(ids)
    assert all("DIRECT_OFFICIAL_SOURCE_METADATA_MISSING" in x["blockers"]
               for x in data["video_statuses"])
    assert not data["all_selected_reference_videos_checked"]


def test_maizen_special_compulsory_cohort_kept_even_with_no_video_ids():
    data=competitor_full_review_gate("minecraft_maizen")
    assert data["references_required"]==3
    assert data["references_passed"]==0
    assert not data["deep_full_episode_analysis_allowed"]
    one_extra=competitor_full_review_gate("maizen_style",["abcDEF12_-Z"])
    assert one_extra["references_required"]==4
    assert one_extra["references_passed"]==0


def test_departments_can_screen_but_cannot_infer_methods():
    for dep in ("INTELLIGENCE","EVIDENCE","WRITERS_ROOM","DIRECTION",
                "PRODUCTION_DESIGN","PERFORMANCE","TECHNICAL_DIRECTION",
                "AUDIO","EDITORIAL","QC","PRODUCTION","STUDIO_MANAGEMENT"):
        report=competitor_study_department_gate(
            "roblox_animation",dep,["zhPBXzHsLuo"],
        )
        assert report["may_screen_channel_age_views_metadata"] == (
            dep in ("INTELLIGENCE","EVIDENCE")
        )
        assert not report["may_conclude_competitor_story_acting_camera_audio_production_methods"]
        assert not report["may_promote_competitor_based_production_recipe"]


def test_wrong_ids_and_invalid_department_fail_closed():
    with pytest.raises(ValueError,match="INVALID_COMPETITOR_SOURCE_VIDEO_ID"):
        competitor_full_review_gate("minecraft_story_adventure",["bad"])
    with pytest.raises(ValueError,match="DUPLICATE_COMPETITOR_REFERENCE"):
        competitor_full_review_gate("minecraft_story_adventure",["zhPBXzHsLuo"]*2)
    with pytest.raises(ValueError,match="NICHE_SLUG_REQUIRED"):
        competitor_full_review_gate("../../root")
    with pytest.raises(ValueError,match="UNKNOWN_COMPETITOR_STUDY_DEPARTMENT"):
        competitor_study_department_gate("roblox_animation","SUPER_ADMIN",[])


def test_each_niche_tech_strategy_report_contains_global_blocker():
    for niche in ("minecraft_story_adventure","long_slices_game","roblox_animation"):
        x=prepare_niche_technology_strategy(niche)
        g=x["universal_full_video_audio_first_gate"]
        assert g["niche_id"]==niche
        assert not g["deep_full_episode_analysis_allowed"]
        assert not x["deep_competitor_evidence_gate_passed"]
        assert not x["competitor_method_and_backend_auto_approval"]
        assert not x["production_permission"]


def test_real_mcp_registry_and_cli_global_review_read_only():
    server=build_server()
    assert "competitor_full_review_gate" in server._tool_manager._tools
    assert "competitor_study_department_gate" in server._tool_manager._tools
    cli=CliRunner()
    result=cli.invoke(app,["competitor-full-review","--niche","long_slices_game",
                           "--video-id","zhPBXzHsLuo","--video-id","oX6Azwe5QLg"])
    assert result.exit_code==0,str(result.exception)
    x=json.loads(result.stdout)
    assert x["references_required"]==2
    assert not x["deep_full_episode_analysis_allowed"]
    department=cli.invoke(app,["competitor-full-review","--niche","roblox_animation",
                               "--department","TECHNICAL_DIRECTION"])
    assert department.exit_code==0,str(department.exception)
    assert not json.loads(department.stdout)["may_conclude_competitor_story_acting_camera_audio_production_methods"]
