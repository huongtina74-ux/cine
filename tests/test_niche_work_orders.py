import json
from pathlib import Path
import pytest
from cinefactory.research_intelligence.niche_work_orders import create_niche_work_orders

def _source(tmp_path):
    examples=[
        {"video_id":"ABCdef12345","channel_id":"UC_leader","video_url":"https://youtube.com/watch?v=ABCdef12345",
         "age_days":2,"million_sub_leader":True,"newcomer":False,"views":2500000,
         "alert":"FRESH_15D_MILLION","evidence_status":"VERIFIED"},
        {"video_id":"EFGhij67890","channel_id":"UC_new","video_url":"https://youtube.com/watch?v=EFGhij67890",
         "age_days":5,"million_sub_leader":False,"newcomer":True,"views":1400000,
         "alert":"FRESH_15D_MILLION","evidence_status":"VERIFIED"},
        {"video_id":"KLMnop13579","channel_id":"UC_leader","video_url":"https://youtube.com/watch?v=KLMnop13579",
         "age_days":55,"million_sub_leader":True,"newcomer":False,"views":80000,
         "alert":None,"evidence_status":"VERIFIED"}]
    path=tmp_path/"watch.json"
    path.write_text(json.dumps({"schema":"cine.niche.watch_report.v1",
        "niche_id":"minecraft--original","as_of":"2026-10-10T03:00:00Z","videos":examples}),
        encoding="utf-8")
    return path

def test_three_research_lanes_preserve_sources_and_no_fabricated_content(tmp_path):
    report=create_niche_work_orders(_source(tmp_path),tmp_path/"orders.json")
    assert report["lane_counts"]["leader_historic_and_new"]==2
    assert report["lane_counts"]["newcomer_breakout"]==1
    assert report["lane_counts"]["fresh_trends_0_15d"]==2
    assert not report["full_video_content_extracted"]
    assert not report["production_permission"]
    assert all(x["source_watch_sha256"]==report["watch_source_sha256"] for x in report["lane_tasks"])
    assert all(x["full_video_semantics_status"]=="NOT_OBSERVED" for x in report["lane_tasks"])
    assert all(len(x["tasks"])>=7 for x in report["lane_tasks"])

def test_empty_newcomer_lane_is_explicit(tmp_path):
    path=_source(tmp_path)
    payload=json.loads(path.read_text(encoding="utf-8"))
    payload["videos"]=[x for x in payload["videos"] if not x["newcomer"]]
    path.write_text(json.dumps(payload),encoding="utf-8")
    report=create_niche_work_orders(path,tmp_path/"orders.json")
    assert "newcomer_breakout" in report["empty_lanes"]

def test_duplicate_evidence_cannot_be_assigned_twice(tmp_path):
    path=_source(tmp_path)
    data=json.loads(path.read_text(encoding="utf-8"))
    data["videos"].append(dict(data["videos"][0]))
    path.write_text(json.dumps(data),encoding="utf-8")
    with pytest.raises(ValueError,match="Duplicate"):
        create_niche_work_orders(path,tmp_path/"orders.json")

def test_immutable_report(tmp_path):
    path=_source(tmp_path)
    create_niche_work_orders(path,tmp_path/"orders.json")
    with pytest.raises(FileExistsError):
        create_niche_work_orders(path,tmp_path/"orders.json")
