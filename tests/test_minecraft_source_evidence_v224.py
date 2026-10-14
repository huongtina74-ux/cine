"""v224 metadata and public image samples cannot be promoted to full competitor movie."""
import json
from typer.testing import CliRunner
import pytest

from cinefactory.cli import app
from cinefactory.studio.minecraft_source_evidence_v224 import (
    load_public_minecraft_evidence,minecraft_g01_g02_evidence
)
from cinefactory.studio.minecraft_company_roadmap_v223 import (
    minecraft_company_roadmap,minecraft_next_approved_step
)
from cinefactory.studio.claude_mcp_gateway_v218 import build_server

def test_authoritative_page_metadata_seven_8min_videos_and_controls():
    d=load_public_minecraft_evidence()
    rows={r["video_id"]:r for r in d["source_video_records"]}
    assert len(rows)==7
    assert all(r["verified_8min_plus"] and r["duration_seconds"]>=480 for r in rows.values())
    assert rows["ZmT0ITUGUII"]["duration_seconds"]==1684
    assert rows["zhPBXzHsLuo"]["duration_seconds"]==1117
    assert rows["X09yxFuKLAs"]["duration_seconds"]==4173
    assert rows["oX6Azwe5QLg"]["duration_seconds"]==1031
    assert rows["w2U4rcZlKnQ"]["duration_seconds"]==525
    assert rows["le0yTRqFRro"]["duration_seconds"]==497

def test_sample_views_do_not_establish_14day_breakout_or_new_channel():
    d=minecraft_g01_g02_evidence()
    assert d["new_channel_2x_1m_in_14days_verified"]==0
    assert d["channels_created_within_30days_verified"]==0
    assert d["full_competitor_video_audio_watches"]==0
    assert not d["production_permission"]
    assert not d["promote_competitor_breakdown_to_verified"]
    assert all(not row["full_video_watched"] and not row["full_audio_heard"]
               and not row["has_two_1m_14day_breakouts"] for row in d["case_metadata"])
    assert d["case_metadata"][0]["views_at_snapshot"]==4677671

def test_chapter_timings_genuine_source_claim_not_visual_playback():
    rows={r["video_id"]:r for r in load_public_minecraft_evidence()["source_video_records"]}
    bed=rows["zhPBXzHsLuo"]["chapters"]
    drops=rows["oX6Azwe5QLg"]["chapters"]
    assert len(bed)==7 and len(drops)==8
    assert bed[-1]["end_seconds"]==1117
    assert drops[-1]["end_seconds"]==1031
    assert sum(r["duration_seconds"] for r in bed)==1117
    assert sum(r["duration_seconds"] for r in drops)==1031
    assert "INCOMPLETE" in rows["X09yxFuKLAs"]["chapter_status"]
    assert all(x["verified_from"]=="YOUTUBE_PAGE_METADATA_CHAPTERS_NOT_PLAYED"
               for x in bed)

def test_three_visual_previews_are_sparse_thumbnail_evidence_not_audio():
    d=minecraft_g01_g02_evidence()
    previews=d["visual_preview_reports"]
    assert len(previews)==3
    assert {p["video_id"] for p in previews}=={
        "zhPBXzHsLuo","X09yxFuKLAs","oX6Azwe5QLg"
    }
    assert all(p["preview_thumbnails_not_playback"]
               and not p["has_sound"] and len(p["thumbnail_tile_hashes"])==3
               for p in previews)

def test_roadmap_reads_fresh_snapshot_not_old_cached_view_counts():
    r=minecraft_company_roadmap(lane="SCRIPTED_MINECRAFT_GAMEPLAY")
    s=r["g01_g02_source_evidence"]
    assert s["public_video_metadata_count"]==7
    assert s["sampled_thumbnail_video_count"]==3
    assert s["full_video_audio_watches"]==0
    meta={x["id"]:x for x in r["referenced_video_metadata"]}
    assert meta["maizen_choose_right_hole_2026"]["verified_direct_2026_10_10_view_count"]==4677671
    assert meta["maizen_house_inside_bed_2025"]["verified_direct_2026_10_10_duration_seconds"]==1117
    gate=minecraft_next_approved_step("SCRIPTED_MINECRAFT_GAMEPLAY")
    assert gate["current_step"]=="G01"
    assert "AGE_14DAY" in gate["status"]
    assert not gate["may_claim_competitor_video_watched"]

def test_cli_video_id_scope_and_mcp_tool_present():
    cli=CliRunner()
    res=cli.invoke(app,["minecraft-source-evidence","--video-id","zhPBXzHsLuo"])
    assert res.exit_code==0,str(res.exception)
    data=json.loads(res.output)
    assert data["verified_public_video_count"]==1
    assert len(data["visual_preview_reports"])==1
    assert data["case_metadata"][0]["chapters"][0]["title"]=="Breaking in as tiny people"
    assert "minecraft_g01_g02_evidence" in build_server()._tool_manager._tools

def test_invalid_id_and_source_overclaim_rejected():
    with pytest.raises(ValueError,match="UNKNOWN_RESEARCH_VIDEO_ID"):
        minecraft_g01_g02_evidence("../../etc/passwd")
    d=load_public_minecraft_evidence()
    assert all(r["verified_1m_within_14d"]=="UNKNOWN_NO_DAILY_VIDEO_HISTORY"
               for r in d["source_video_records"])
