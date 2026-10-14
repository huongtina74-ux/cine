import json
from datetime import datetime,timezone,timedelta
from pathlib import Path
import pytest

from cinefactory.research_intelligence.pod_dispatch import dispatch_pods_once

NOW=datetime(2026,10,10,12,tzinfo=timezone.utc)
def utc(hours=0):
    return (NOW-timedelta(hours=hours)).isoformat()
def record(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj),encoding="utf-8")

def pod():
    return {"schema":"cine.niche.pod.v1","state":"CONFIGURED_NOT_SCHEDULED",
            "niche":"Minecraft animation","format_key":"custom-stage",
            "niche_id":"minecraft-animation--custom-stage","source_company":"C:/Company Youtube"}

def bridge(hours=0):
    vid={"video_id":"ABCdef12345","views":1500000,
         "published_at":utc(18),"observed_at":utc(hours),
         "source_url":"https://www.youtube.com/watch?v=ABCdef12345",
         "title":"Evidence test","evidence_status":"VERIFIED"}
    return {"schema":"cine.bridge.company_snapshot.v1",
            "niche":"Minecraft animation","format_key":"custom-stage",
            "source_project":"C:/Company Youtube","as_of":utc(hours),
            "candidates":[{"channels":[{"channel_id":"UCtest","age_days":8,
                            "subscriber_count":30000,"videos":[vid]}]}]}

def test_no_approved_pod_no_false_success(tmp_path):
    (tmp_path/"pods").mkdir()
    (tmp_path/"bridges").mkdir()
    result=dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",
                              tmp_path/"result",as_of=utc())
    assert result["state"]=="NO_PODS"
    assert not result["full_video_research_complete"]
    assert not result["automated_production_or_upload"]

def test_missing_bridge_is_blocked_not_empty_success(tmp_path):
    record(tmp_path/"pods"/"niche"/"pod.json",pod())
    (tmp_path/"bridges").mkdir()
    result=dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",
                              tmp_path/"result",as_of=utc())
    assert result["state"]=="BLOCKED"
    assert result["tasks"][0]["state"]=="BLOCKED_NO_VERIFIED_CURRENT_INPUT"

def test_durable_readonly_watch_fresh_actual_snapshot(tmp_path,monkeypatch):
    monkeypatch.setattr("cinefactory.research_intelligence.pod_dispatch.verify_imported_company_sources",lambda b:True)
    monkeypatch.setattr("cinefactory.research_intelligence.pod_watch.verify_imported_company_sources",lambda b:True)
    record(tmp_path/"pods"/"niche"/"pod.json",pod())
    record(tmp_path/"bridges"/"old.json",bridge(24))
    record(tmp_path/"bridges"/"new.json",bridge(0))
    result=dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",
                              tmp_path/"result",as_of=utc())
    assert result["state"]=="WATCHES_COMPLETE"
    assert result["watch_reports_created"]==1
    watch=json.loads(Path(result["tasks"][0]["watch_report"]).read_text(encoding="utf-8"))
    assert watch["fresh_15d_million_videos"]==1
    assert result["youtube_api_calls"]==0
    work=json.loads(Path(result["tasks"][0]["research_work_orders"]).read_text(encoding="utf-8"))
    assert work["lane_counts"]["newcomer_breakout"]==1
    assert work["full_video_content_extracted"] is False
    assert not result["owner_event_authenticated_by_this_runner"]
    with pytest.raises(FileExistsError):
        dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",tmp_path/"result",as_of=utc())

def test_stale_verified_snapshot_is_blocked(tmp_path,monkeypatch):
    monkeypatch.setattr("cinefactory.research_intelligence.pod_dispatch.verify_imported_company_sources",lambda b:True)
    record(tmp_path/"pods"/"niche"/"pod.json",pod())
    record(tmp_path/"bridges"/"old.json",bridge(70))
    result=dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",tmp_path/"result",as_of=utc())
    assert result["state"]=="BLOCKED"
    assert result["watch_reports_created"]==0

def test_bad_fake_source_is_never_used(tmp_path):
    record(tmp_path/"pods"/"niche"/"pod.json",pod())
    record(tmp_path/"bridges"/"bad.json",bridge())
    result=dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",tmp_path/"result",as_of=utc())
    assert result["state"]=="BLOCKED"


def test_real_directory_can_contain_unrelated_json_arrays(tmp_path):
    (tmp_path/"pods").mkdir()
    (tmp_path/"bridges").mkdir()
    record(tmp_path/"bridges"/"catalog.json",[{"sku":"image"},{"sku":"voice"}])
    record(tmp_path/"bridges"/"other.json",["this","is","not","a","bridge"])
    result=dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",
                              tmp_path/"result",as_of=utc())
    assert result["state"]=="NO_PODS"
    assert result["watch_reports_created"]==0


def test_malformed_pod_list_blocks_its_own_task_not_crash(tmp_path):
    record(tmp_path/"pods"/"bad"/"pod.json",["bad","data"])
    (tmp_path/"bridges").mkdir()
    result=dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",
                              tmp_path/"result",as_of=utc())
    assert result["state"]=="BLOCKED"
    assert result["tasks"][0]["state"]=="BLOCKED_NO_VERIFIED_CURRENT_INPUT"


def test_equal_timestamps_identical_snapshots_are_deduped(tmp_path,monkeypatch):
    monkeypatch.setattr("cinefactory.research_intelligence.pod_dispatch.verify_imported_company_sources",
                        lambda b:True)
    monkeypatch.setattr("cinefactory.research_intelligence.pod_watch.verify_imported_company_sources",
                        lambda b:True)
    record(tmp_path/"pods"/"niche"/"pod.json",pod())
    record(tmp_path/"bridges"/"old.json",bridge(24))
    record(tmp_path/"bridges"/"new1.json",bridge(0))
    record(tmp_path/"bridges"/"new2.json",bridge(0))
    r=dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",
                         tmp_path/"complete",as_of=utc())
    assert r["state"]=="WATCHES_COMPLETE"
    assert r["watch_reports_created"]==1


def test_equal_time_conflicting_snapshot_values_block_one_pod(tmp_path,monkeypatch):
    monkeypatch.setattr("cinefactory.research_intelligence.pod_dispatch.verify_imported_company_sources",
                        lambda b:True)
    record(tmp_path/"pods"/"niche"/"pod.json",pod())
    record(tmp_path/"bridges"/"new1.json",bridge(0))
    changed=bridge(0)
    changed["candidates"][0]["channels"][0]["videos"][0]["views"]=9500000
    record(tmp_path/"bridges"/"new2.json",changed)
    r=dispatch_pods_once(tmp_path/"pods",tmp_path/"bridges",
                         tmp_path/"blocked",as_of=utc())
    assert r["state"]=="BLOCKED"
    assert r["tasks"][0]["state"]=="BLOCKED_NO_VERIFIED_CURRENT_INPUT"
    assert "Conflicting same-time" in r["tasks"][0]["reason"]
