"""Contract tests: no niche can convert tool discovery into verified production."""
import hashlib
import json

import pytest
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio.niche_technology_strategy_v213 import (
    prepare_niche_technology_strategy,
)


def _conference(tmp_path, niche="minecraft_story_adventure"):
    doc = {
        "schema": "cine.studio.production_conference.v1",
        "approved_niche": niche,
        "video_cases": [
            {"video_id": "ABCDEFGHIJK", "full_video_inspection": "NOT_DONE"}
        ],
        "video_case_count": 1,
        "source_rights_status": "NOT_CLEARED",
    }
    p = tmp_path / "conference.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def test_full_inventory_and_every_company_department_are_included():
    report = prepare_niche_technology_strategy("long_slices_game")
    assert report["registry_items"] == 96
    assert len({x for ids in report["registry_by_category"].values()
                for x in ids}) == 96
    assert report["all_departments_count"] == 26
    assert report["decision"] == "RESEARCH_AND_PILOT_PLAN_ONLY"
    assert not report["production_permission"]
    assert report["competitor_video_research"]["full_videos_verified"] == 0
    assert report["update_policy"]["review_new_claude_code_claude_agent_sdk_mcp_plugins"]


def test_gameplay_never_gets_film_animation_as_primary_pilot():
    capture = prepare_niche_technology_strategy("minecraft_recorded_survival")
    film = prepare_niche_technology_strategy("minecraft_story_adventure")
    capture_ids = capture["per_scene_pilot_candidates"]["camera"]["PRODUCTION"]
    assert "blender" not in capture_ids
    assert "blender" in film["per_scene_pilot_candidates"]["camera"]["PRODUCTION"]


def test_competitor_metadata_is_not_full_video_proof(tmp_path):
    conf = _conference(tmp_path)
    report = prepare_niche_technology_strategy(
        "minecraft_story_adventure", conference_file=conf,
    )
    assert report["competitor_video_research"]["catalogued_cases"] == 1
    assert report["competitor_video_research"]["full_videos_verified"] == 0
    assert "FULL_COMPETITOR_VIDEO_AUDIO_STUDY_NOT_AUTHENTICATED" in report["blockers"]
    assert not report["automatic_backend_switch"]


def test_bakeoff_revision_must_match_competitor_conference(tmp_path):
    conf = _conference(tmp_path)
    fake = tmp_path / "bakeoff.json"
    fake.write_text(json.dumps({
        "schema": "cine.studio.pilot_bakeoff.v1",
        "conference_sha256": "0" * 64,
        "advisory_rankings": {"s1": {"advisory_fastest_meeting_quality": "blender"}},
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="REVISION_MISMATCH"):
        prepare_niche_technology_strategy(
            "minecraft_story_adventure", conference_file=conf, bakeoff_file=fake,
        )


def test_cli_report_is_read_only_and_complete():
    result = CliRunner().invoke(
        app, ["niche-technology-plan", "--minor-niche", "asmr_sleep_hands_objects"]
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["registry_items"] == 96
    assert data["format_family"] == "REAL_ASMR"
    assert data["production_permission"] is False
    assert data["measured_pilot_evidence"]["advisory_only"]
