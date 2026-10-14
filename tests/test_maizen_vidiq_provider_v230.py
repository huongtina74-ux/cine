"""v230: external long-form provider result is preserved but NOT certified source A/V."""
import json
from typer.testing import CliRunner
from cinefactory.cli import app
from cinefactory.studio.maizen_vidiq_provider_v230 import (
    load_vidiq_watch_case,maizen_vidiq_provider_evidence,
)
from cinefactory.studio.claude_mcp_gateway_v218 import build_server

def test_external_vidiq_watch_job_provenance_and_duration():
    d=load_vidiq_watch_case()
    assert d["video_id"]=="ZmT0ITUGUII"
    assert d["job_status"]=="completed"
    assert d["video_duration_seconds"]==1684
    assert len(d["rounds"])==7
    assert len(d["chronological_scenes"])==23
    assert d["chronological_scenes"][0]["begin_seconds"]==0
    assert d["chronological_scenes"][-1]["end_seconds"]==1684

def test_source_original_picture_and_audio_not_proven():
    r=maizen_vidiq_provider_evidence()
    assert r["provider_watch_job_completed"]
    assert r["provider_summary_scene_sections"]==23
    assert r["provider_summary_longest_scene_seconds"]>30
    assert r["provider_explicit_audio_detail_segments"]<23
    assert not r["source_film_audio_stream_independently_verified"]
    assert not r["independent_av_auditor_approved"]
    assert not r["official_mods_software_tools_identified"]
    assert not r["v227_all_three_full_video_gate_passed"]
    assert not r["v227_first_video_gate_passed"]
    assert not r["may_promote_competitor_workflow_to_production"]

def test_actual_spend_balance_not_assumed_equal_advertised_price():
    r=maizen_vidiq_provider_evidence()
    assert r["provider_advertised_credits"]==25
    assert r["observed_balance_before"]==201
    assert r["observed_balance_after"]==200
    assert r["actual_charge_cannot_be_inferred_from_advertised_pricing"]

def test_readonly_cli_and_mcp_display_provider_report():
    cli=CliRunner()
    out=cli.invoke(app,["maizen-vidiq-evidence"])
    assert out.exit_code==0,str(out.exception)
    d=json.loads(out.stdout)
    assert d["video_id"]=="ZmT0ITUGUII"
    assert d["provider_summary_scene_sections"]==23
    assert "maizen_vidiq_provider_evidence" in build_server()._tool_manager._tools
