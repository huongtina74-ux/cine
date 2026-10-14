"""v248: three real-source browser timeline/ASR research with strict native QC blocker."""
import json
from pathlib import Path
import pytest
from typer.testing import CliRunner
from cinefactory.cli import app
from cinefactory.studio import maizen_three_source_study_v248 as study
from cinefactory.studio.claude_mcp_gateway_v218 import build_server

def test_three_distinct_real_source_story_formats():
 p=study.load_three_source_study()
 assert p["first_source"]["video_id"]=="ZmT0ITUGUII"
 assert [x["video_id"] for x in p["remaining_references"]]==[
  "zhPBXzHsLuo","oX6Azwe5QLg"]
 assert {x["format_hypothesis"] for x in p["remaining_references"]}=={
  "TINY_SECRET_HOME_REVENGE","SINGLE_CHEAT_RULE_TO_END_BOSS_PROGRESSION"}
 assert len(p["comparison"])>=6
 assert len(p["generalizable_lessons"])>=7
 assert not p["safety"]["strict_v227_cohort_gate_passed"]

def test_actual_two_original_source_browser_av_and_first_5s_patches():
 d=study.maizen_three_source_video_study()
 assert d["three_selected_original_browser_timeline_audio_data_acquired"]
 assert d["first_source_original_audio_and_asr_local_receipt_verified"]
 assert d["total_original_browser_segmentation_windows"]==103
 assert d["first_party_video_frame_samples"]>=420
 assert len(d["additional_reference_videos"])==2
 for r in d["additional_reference_videos"]:
  assert r["whole_original_browser_av_position_trace_verified"]
  assert r["automatic_local_asr_all_segments_verified"]
  assert r["original_first_5s_audio_patch_verified"]
  assert r["asr_words_uncorrected"]>1000
 assert {r["segments_verified"] for r in d["additional_reference_videos"]}=={30,28}

def test_original_3film_av_capture_not_a_comprehensive_native_audio_independent_qc():
 r=study.maizen_three_source_video_study()
 assert not r["native_audio_music_sfx_comprehensively_human_approved"]
 assert not r["every_visual_frame_independently_reviewed"]
 assert not r["secondary_independent_auditor_signed_off"]
 assert not r["exact_software_mods_game_versions_proven"]
 assert not r["strict_v227_independent_3video_av_gate_passed"]
 assert not r["g03_to_g28_competitor_method_production_promotion_allowed"]
 assert r["credits_spent_by_this_study"]==0

def test_report_fails_closed_if_unmounted_machine_receipts_missing(monkeypatch,tmp_path):
 monkeypatch.setattr(study,"LOCAL",tmp_path/"no-browser-source")
 monkeypatch.setattr(study,"FIRST_AUDIO_AUDIT",tmp_path/"missing-audio1.json")
 d=study.maizen_three_source_video_study()
 assert not d["three_selected_original_browser_timeline_audio_data_acquired"]
 assert not d["first_source_original_audio_and_asr_local_receipt_verified"]
 assert not d["g03_to_g28_competitor_method_production_promotion_allowed"]
 assert all(not v["whole_original_browser_av_position_trace_verified"] for v in d["additional_reference_videos"])

def test_mcp_and_cli_are_read_only():
 assert "maizen_three_source_video_study" in build_server()._tool_manager._tools
 cmd=CliRunner().invoke(app,["maizen-three-source-study"])
 assert cmd.exit_code==0,str(cmd.exception)
 p=json.loads(cmd.output)
 assert p["total_original_browser_segmentation_windows"]==103
 assert not p["strict_v227_independent_3video_av_gate_passed"]
