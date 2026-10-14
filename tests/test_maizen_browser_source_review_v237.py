"""v237 direct YouTube Chrome playback receipts are real, but QC remains blocked."""
import json
from pathlib import Path
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio.claude_mcp_gateway_v218 import build_server
from cinefactory.studio import maizen_browser_source_review_v237 as b

def test_real_original_youtube_browser_timecode_receipt_exists():
    d=b.load_maizen_browser_study()
    assert d["source_duration_seconds"]==1684.461
    assert d["capture"]["chrome_playback_timeline_covered"]
    assert d["capture"]["playback_segments"]==45
    assert d["capture"]["gaps_greater_than_0_7s"]==0
    assert len(d["scene_timeline"])==10
    assert d["round_count"]==7

def test_first_party_playback_does_not_claim_entire_audio_semantics_or_G02_qc():
    s=b.maizen_browser_source_study()
    assert s["source_browser_full_timeline_verified_by_local_trace"]
    assert s["successful_38s_consecutive_playback_segments"]==45
    assert s["audio_energy_samples"]>300
    assert s["audible_energy_samples"]>300
    assert s["captured_video_sample_frames"]>100
    assert not s["full_native_audio_semantic_listening_verified"]
    assert not s["independent_media_qc_completed"]
    assert not s["exact_rival_tools_mods_known"]
    assert not s["can_conclude_Maizen_uses_only_gameplay_or_only_Blender"]
    assert not s["maizen_v227_first_video_final_qc_approved"]
    assert not s["company_G03_competitor_technique_greenlight"]
    assert s["additional_two_source_videos_pending"]

def test_unavailable_local_machine_research_receipts_not_counterfeited(monkeypatch,tmp_path):
    monkeypatch.setattr(b,"AUDIT",tmp_path/"nonexistent.json")
    s=b.maizen_browser_source_study()
    assert not s["source_browser_full_timeline_verified_by_local_trace"]
    assert s["successful_38s_consecutive_playback_segments"]==0
    assert not s["company_G03_competitor_technique_greenlight"]

def test_mcp_and_cli_readonly_video_original_study_exposed():
    assert "maizen_browser_source_study" in build_server()._tool_manager._tools
    output=CliRunner().invoke(app,["maizen-browser-source"])
    assert output.exit_code==0,str(output.exception)
    result=json.loads(output.stdout)
    assert result["source_browser_full_timeline_verified_by_local_trace"]
    assert result["video_id"]=="ZmT0ITUGUII"
