import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest
from cinefactory.research_intelligence.breakout_proof import audit_official_artifact

NOW = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
CID = "UC" + "a" * 22
CID_OLD = "UC" + "b" * 22
VID1, VID2, VID3 = "ABCdef12345", "GHIjkl67890", "QWErty12345"

def when(days=0):
    return (NOW-timedelta(days=days)).isoformat()

def film(ident, channel=CID, views=1300000, secs=600, fmt="LONG_FORM", published=2):
    return {"video_id":ident, "channel_id":channel, "video_url":f"https://www.youtube.com/watch?v={ident}",
            "published_at":when(published), "views":views, "duration_seconds":secs,
            "format_proxy":fmt, "privacy_status":"public", "evidence_status":"VERIFIED"}

def source():
    return {"generated_at":when(), "channels":{
        CID:{"channel_id":CID, "created_at":when(9), "evidence_status":"VERIFIED", "channel_url":"https://youtube.com/channel/"+CID},
        CID_OLD:{"channel_id":CID_OLD, "created_at":when(700), "evidence_status":"VERIFIED"}},
        "catalogs":{CID:[film(VID1), film(VID2)], CID_OLD:[film(VID3,CID_OLD)]}}

def audit(tmp_path, payload):
    path = tmp_path / "official.json"
    path.write_text(json.dumps(payload),encoding="utf-8")
    return audit_official_artifact(path,tmp_path/"evidence.json")

def test_exact_two_distinct_videos_in_30day_channel(tmp_path):
    result=audit(tmp_path,source())
    assert result["state"]=="CHANNEL_BREAKOUT_EVIDENCE_PRESENT"
    assert len(result["witness_channels"])==1
    assert result["witness_channels"][0]["channel_id"]==CID
    assert result["witness_channels"][0]["witness_count"]==2
    assert result["opportunity_niches_verified"]==0
    assert json.loads((tmp_path/"evidence.json").read_text(encoding="utf-8"))["sha256"]==result["sha256"]

def test_short_livestream_private_and_wrong_format_cannot_pass(tmp_path):
    for field,value in [("duration_seconds",55),("format_proxy","SHORT_PROXY"),
                        ("is_live",True),("is_short",True),("privacy_status","private"),
                        ("views",900000),("evidence_status","HYPOTHESIS")]:
        packet=source()
        packet["catalogs"][CID][1][field]=value
        result=audit(tmp_path,packet)
        assert not result["witness_channels"],(field,value)

def test_age_and_video_creation_causality(tmp_path):
    packet=source()
    packet["channels"][CID]["created_at"]=when(31)
    assert not audit(tmp_path,packet)["witness_channels"]
    packet=source()
    packet["catalogs"][CID][1]["published_at"]=when(20)
    assert not audit(tmp_path,packet)["witness_channels"]

def test_duplicate_same_video_not_double_counted(tmp_path):
    packet=source()
    packet["catalogs"][CID]=[film(VID1),film(VID1)]
    assert not audit(tmp_path,packet)["witness_channels"]

def test_channel_video_link_mismatch_blocks(tmp_path):
    packet=source()
    packet["catalogs"][CID][1]["video_url"]="https://evil.example/watch?v="+VID2
    assert not audit(tmp_path,packet)["witness_channels"]

def test_no_historical_relabeling_as_today(tmp_path):
    packet=source()
    packet["generated_at"]="2026-07-01T12:00:00Z"
    with pytest.raises(ValueError,match="Cannot evaluate old scan"):
        audit_official_artifact(_create(tmp_path, packet),tmp_path/"bad.json",observed_at=when())

def _create(tmp_path,payload):
    p=tmp_path/"official.json"
    p.write_text(json.dumps(payload),encoding="utf-8")
    return p

def test_no_minority_foreign_channel_masquerading_as_new(tmp_path):
    packet=source()
    packet["catalogs"][CID][1]["channel_id"]=CID_OLD
    assert not audit(tmp_path,packet)["witness_channels"]

def test_invalid_channel_metadata_cannot_qualify(tmp_path):
    packet=source()
    packet["channels"][CID]["evidence_status"]="UNKNOWN"
    assert not audit(tmp_path,packet)["witness_channels"]


def test_proof_of_million_views_within_14_days_from_early_snapshot(tmp_path):
    packet=source()
    result=audit(tmp_path,packet)
    row=result["witness_channels"][0]
    assert row["two_million_within_14d_proved"] is True
    assert result["counts"]["channels_two_million_within_14_days_proved"]==1
    packet["catalogs"][CID][1]["published_at"]=when(15)
    packet["channels"][CID]["created_at"]=when(30)
    result=audit(tmp_path,packet)
    assert result["witness_channels"][0]["two_million_within_14d_proved"] is False


def test_full_movie_risk_is_flagged_not_recommended(tmp_path):
    packet=source()
    packet["catalogs"][CID][0]["title"]="Full Action Blockbuster Movie Hindi Dubbed"
    row=audit(tmp_path,packet)["witness_channels"][0]
    assert "hindi dubbed" in row["rights_risk_markers"]
    assert row["originality_and_rights"]=="NEEDS_MANUAL_CLEARANCE"
    assert row["production_recommendation"].startswith("DO_NOT_PRODUCE")


def test_cross_channel_catalog_duplication_blocks_young_witness(tmp_path):
    packet=source()
    packet["catalogs"][CID_OLD].append(film(VID1,CID_OLD))
    result=audit(tmp_path,packet)
    assert not result["witness_channels"]
    assert any(x["reason"]=="DUPLICATE_OR_CROSS_CHANNEL_VIDEO" for x in result["anomalies"])


def test_followup_tasks_require_all_remaining_gates(tmp_path):
    result=audit(tmp_path,source())
    assert result["research_followup_tasks"]
    task=result["research_followup_tasks"][0]
    assert task["automatically_approved"] is False
    assert "MATURE_CHANNEL_RECENT_DEMAND_PROOF" in task["requirements"]
    assert "CINECOUNCIL_CROSS_EXAMINATION" in task["requirements"]
