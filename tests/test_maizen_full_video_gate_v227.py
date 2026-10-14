"""v227: entire competitor video & original audio mandatory before any method conclusion."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio import maizen_full_video_gate_v227 as gate
from cinefactory.studio.maizen_media_decode_v227 import verify_reference_media
from cinefactory.studio.maizen_method_review_v226 import maizen_production_method_audit,maizen_shot_method_options
from cinefactory.studio.maizen_studio_kickoff_v225 import maizen_studio_status,maizen_department_work
from cinefactory.studio.minecraft_company_roadmap_v223 import minecraft_company_roadmap
from cinefactory.studio.technology_council_v212 import counsel_for_all_departments
from cinefactory.studio.claude_mcp_gateway_v218 import build_server

def test_policy_requires_entire_original_moving_film_and_audio_for_each_reference():
    p=gate.load_full_video_policy()
    r=p["rules"]
    assert r["must_watch_every_selected_reference_from_start_to_end"]
    assert r["must_hear_every_selected_original_audio_track"]
    assert not r["allow_10_second_excerpt_to_replace_full_video"]
    assert not r["allow_thumbnail_transcript_metadata_to_replace_av"]
    assert not r["allow_early_method_conclusion"]
    assert not r["allow_script_room_production_design_character_technical_audio_editorial_qc_promotions_before_gate"]
    assert r["max_segment_seconds"]==30

def test_three_required_source_films_are_100_percent_covered_not_10_seconds():
    vids={x["video_id"]:x for x in gate.load_full_video_policy()["required_references"]}
    assert set(vids)=={"ZmT0ITUGUII","zhPBXzHsLuo","oX6Azwe5QLg"}
    assert sum(x["duration_seconds"] for x in vids.values())==3832
    required=gate.maizen_full_video_review_gate()
    assert required["required_total_seconds"]==3832
    assert required["required_total_segments"]==130
    assert required["required_video_count"]==3
    assert not required["cohort_gate_passed"]
    assert not required["g03_competitor_method_analysis_authorized"]
    assert not required["g04_g28_department_production_workflow_promotions_authorized"]
    assert not required["may_run_independent_internal_quality_experiments"]
    assert not required["may_claim_video_reference_review_completed"]
    assert all(not s["gate_passed"] for s in required["videos"])

def test_each_blank_workbook_covers_all_source_seconds_but_does_not_assert_watch():
    for video in gate.load_full_video_policy()["required_references"]:
        record=gate.draft_full_review_template(video["video_id"])
        windows=record["intervals"]
        assert windows[0]["start_seconds"]==0
        assert windows[-1]["end_seconds"]==video["duration_seconds"]
        assert len(windows)==(video["duration_seconds"]+29)//30
        assert all(x["end_seconds"]-x["start_seconds"]<=30 for x in windows)
        assert all(x["visual_observation"]=="" and x["audio_observation"]==""
                   and not x["viewed_moving_video"] and not x["heard_original_audio"]
                   for x in windows)
        assert record["observed_duration_seconds"] is None
        assert record["watch_provenance"]=="NOT_WATCHED"

def test_missing_original_media_rejects_fake_full_watch_report(tmp_path,monkeypatch):
    monkeypatch.setattr(gate,"REVIEW_DIR",tmp_path)
    r=gate.draft_full_review_template("zhPBXzHsLuo")
    r["visual_full_watch"]=r["audio_full_watch"]=True
    r["decode_full_video"]=r["decode_full_audio"]=True
    r["viewer_attestation"]={"reviewer":"Alice","visual_entire_film":True,
                              "audio_entire_film":True,"reviewed_at":"2026-10-11"}
    r["independent_reviewer_attestation"]={"reviewer":"Bob",
                                          "audited_all_intervals":True,
                                          "signed_at":"2026-10-11"}
    r["watch_provenance"]="AUTHORIZED_COMPLETE_MOVING_MEDIA_AND_ORIGINAL_AUDIO"
    (tmp_path/"zhPBXzHsLuo.json").write_text(json.dumps(r),encoding="utf8")
    video=next(x for x in gate.load_full_video_policy()["required_references"]
               if x["video_id"]=="zhPBXzHsLuo")
    actual=gate._review_file_status(video)
    assert not actual["gate_passed"]
    assert "ORIGINAL_FULL_AUDIO_VIDEO_MEDIA_MISSING" in actual["blockers"] or            any("INVALID" in b for b in actual["blockers"])

def test_source_validation_blocks_unknown_ids_and_unsafe_paths():
    with pytest.raises(ValueError,match="UNKNOWN_MAIZEN_REFERENCE_ID"):
        gate.draft_full_review_template("BADID")
    with pytest.raises(ValueError,match="OUT_OF_RESEARCH_REPOSITORY"):
        gate._confined(gate.ROOT,"../../../../WINDOWS/secret.bin")
    with pytest.raises(ValueError,match="UNKNOWN_MAIZEN_REFERENCE_ID"):
        verify_reference_media("../../../../../etc/passwd")
    with pytest.raises(ValueError,match="PROVIDE_EXACTLY_ONE_LOCAL_AUTHORIZED"):
        verify_reference_media("zhPBXzHsLuo")

def test_stages_g01_and_g02_only_allowed_for_data_collection():
    assert gate.maizen_research_stage_gate("G01")["may_begin_stage"]
    assert gate.maizen_research_stage_gate("G02")["may_begin_stage"]
    for stage in ("G03","G04","G05","G06","G08","G09","G10","G13","G17","G20","G21","G23","G26","G28"):
        state=gate.maizen_research_stage_gate(stage)
        assert not state["may_begin_stage"]
        assert set(state["blocking_video_ids"])==set(gate.ALLOWED_IDS)
        with pytest.raises(PermissionError,match="FULL_VIDEO_AUDIO_REVIEW_REQUIRED"):
            gate.require_maizen_full_video_review_for_stage(stage)
    with pytest.raises(ValueError,match="UNKNOWN_MAIZEN_COMPANY_STAGE"):
        gate.maizen_research_stage_gate("G99")

def test_all_26_department_handoffs_are_only_historical_draft_work():
    s=maizen_studio_status()
    assert not s["seven_stage_production_method_conclusions_allowed"]
    assert s["all_department_v225_handoffs_are_only_preliminary_drafts"]
    assert s["full_competitor_video_first_research_gate"]["full_verified_videos"]==0
    for dept in ("WRITERS_ROOM","PRODUCTION_DESIGN","PERFORMANCE","TECHNICAL_DIRECTION","AUDIO","EDITORIAL","QC"):
        d=maizen_department_work(dept)
        assert not d["full_reference_review_passed"]
        assert not d["may_promote_department_production_method_or_recipe"]

def test_company_roadmap_blocks_all_maizen_stages_beyond_full_research():
    d=minecraft_company_roadmap(lane="SCRIPTED_MINECRAFT_GAMEPLAY")
    assert not d["maizen_mandatory_full_video_review_gate"]["cohort_gate_passed"]
    by_id={x["step_id"]:x for x in d["ordered_steps"]}
    assert not by_id["G01"]["maizen_full_source_analysis_gate_blocks_stage"]
    assert not by_id["G02"]["maizen_full_source_analysis_gate_blocks_stage"]
    assert all(x["maizen_full_source_analysis_gate_blocks_stage"] for x in d["ordered_steps"]
               if x["step_id"] not in ("G01","G02"))
    assert d["maizen_production_method_correction"]["competitor_method_conclusion_blocked"]

def test_company_wide_technology_council_requires_entire_video_not_excerpt():
    council=counsel_for_all_departments("minecraft_story_adventure")
    assert len(council["all_departments"])==26
    for dept in council["all_departments"].values():
        assert dept["entire_reference_film_and_original_audio_required_before_method_conclusion"]
        assert dept["ten_second_sample_or_thumbnails_never_sufficient"]
        assert not dept["competitor_specific_method_conclusions_automatically_authorized"]

def test_mcp_and_cli_expose_gate_readonly():
    tools=build_server()._tool_manager._tools
    assert "maizen_full_video_review_gate" in tools
    assert "maizen_full_video_review_template" in tools
    runner=CliRunner()
    response=runner.invoke(app,["maizen-full-video-review"])
    assert response.exit_code==0,str(response.exception)
    data=json.loads(response.output)
    assert data["required_total_seconds"]==3832 and not data["cohort_gate_passed"]
    template=runner.invoke(app,["maizen-full-video-review","--video-id","ZmT0ITUGUII"])
    assert template.exit_code==0,str(template.exception)
    t=json.loads(template.output)
    assert t["expected_duration_seconds"]==1684
    assert not t["audio_full_watch"]


def test_any_future_selected_reference_is_also_mandatory(monkeypatch,tmp_path):
    doc=gate.load_full_video_policy()
    doc["required_references"].append({
        "video_id":"ABC123xy_Z1",
        "channel":"Maizen",
        "title":"Additional authenticated long-form competitor reference",
        "duration_seconds":605,
        "source_metadata_independently_verified":True,
    })
    path=tmp_path/"policy.json"
    path.write_text(json.dumps(doc),encoding="utf8")
    monkeypatch.setattr(gate,"POLICY_PATH",path)
    result=gate.maizen_full_video_review_gate()
    assert result["required_video_count"]==4
    assert result["required_total_seconds"]==3832+605
    assert any(x["video_id"]=="ABC123xy_Z1" and not x["gate_passed"]
               for x in result["videos"])
    assert not result["cohort_gate_passed"]
    assert gate.draft_full_review_template("ABC123xy_Z1")["expected_duration_seconds"]==605


def test_maizen_stage_cli_enforcement_hard_fails_unreviewed_G03():
    runner=CliRunner()
    g=runner.invoke(app,["maizen-research-stage","--stage-id","G03"])
    assert g.exit_code==0,str(g.exception)
    assert json.loads(g.output)["may_begin_stage"] is False
    enforced=runner.invoke(app,["maizen-research-stage","--stage-id","G03","--enforce"])
    assert enforced.exit_code!=0
    assert "FULL_VIDEO_AUDIO_REVIEW_REQUIRED" in str(enforced.exception)
    allowed=runner.invoke(app,["maizen-research-stage","--stage-id","G02","--enforce"])
    assert allowed.exit_code==0,str(allowed.exception)
    assert json.loads(allowed.output)["may_begin_stage"]
    assert "maizen_research_stage_gate" in build_server()._tool_manager._tools
