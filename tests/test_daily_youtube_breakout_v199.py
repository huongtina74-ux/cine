"""v199 persistent discovery and evidence-grade QA, all fixture tests offline."""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import sqlite3
from pathlib import Path
import pytest
from cinefactory.studio.daily_youtube_breakout_v199 import (
    WINDOW_DAYS,PublicVideo,PublicYoutubeClient,BreakoutLedger,
    classify,scan_daily,command_reader,SEARCH_LANES,UTC,
)
from cinefactory.studio.youtube_storyboard_research_v199 import (
    inspect_sparse_storyboards,_pull_jpg,
)
from scripts.run_daily_cinefactory_youtube_v199 import create_claude_packet,report_to_markdown

AT=dt.datetime(2026,10,9,10,0,tzinfo=UTC)
DAY="20261008"
VID="t5wy_OsuMvM"
CHID="UC"+"a"*22

def video(vid=VID,*,published=DAY,views=400000,duration=620,live=False,lane="minecraft_gameplay"):
    return PublicVideo.parse({
        "id":vid,"title":"Original dynamic Minecraft 100 days",
        "upload_date":published,"duration":duration,"view_count":views,
        "channel_id":CHID,"channel":"Test Channel",
        "was_live":live,"live_status":"not_live"
    },lane)

class Stub:
    def __init__(self,records=None):
        self.records=records or {VID:video()}
        self.search_count=0
        self.video_count=0
    def search(self,keyword,*,limit):
        self.search_count+=1
        return [{"id":vid,"title":"Fixture title","channel":"Fixture channel"}
                for vid in self.records][:limit]
    def video(self,vid,*,lane):
        self.video_count+=1
        record=self.records[vid]
        return PublicVideo.parse({
            "id":record.video_id,"title":record.title,
            "upload_date":record.published_date,
            "duration":record.duration_sec,"view_count":record.views,
            "channel_id":record.channel_id,"channel":record.channel_name,
            "was_live":record.is_live,
        },lane)

def test_dates_are_all_windows():
    assert WINDOW_DAYS==(2,3,4,5,6,7,14,30)

def test_true_real_public_metadata_is_valid():
    v=video()
    assert v.video_id==VID and v.views==400000
    assert len(v.metadata_sha256)==64
    assert v.channel_id==CHID

@pytest.mark.parametrize("bad",["invalid","../../.env","http://x/", "???????????"])
def test_bad_video_ids_rejected(bad):
    with pytest.raises(ValueError):
        video(vid=bad)

def test_missing_real_upload_date_never_guessed():
    with pytest.raises(ValueError,match="UPLOAD_DAY_NOT_PROVEN"):
        PublicVideo.parse({"id":VID,"duration":601,"view_count":500,
                           "upload_date":None},"minecraft_gameplay")

def test_missing_view_count_never_zero_filled():
    with pytest.raises(ValueError,match="VIEWS_UNAVAILABLE"):
        PublicVideo.parse({"id":VID,"duration":601,"view_count":None,
                           "upload_date":DAY},"minecraft_gameplay")

def test_live_and_short_videos_not_eligible():
    assert classify(video(live=True),AT,None) is None
    assert classify(video(duration=479),AT,None) is None

def test_future_and_old_videos_rejected():
    assert classify(video(published="20261010"),AT,None) is None
    assert classify(video(published="20260701"),AT,None) is None

def test_windows_membership_one_day_recent_video():
    r=classify(video(),AT,None)
    assert r["window_membership_days"]==[2,3,4,5,6,7,14,30]
    assert r["channel_created_at"] is None
    assert r["new_channel_under_30_days"]=="UNKNOWN"

def test_window_4days_excludes_shorter_buckets():
    r=classify(video(published="20261005"),AT,None)
    assert r["window_membership_days"]==[5,6,7,14,30]

def test_age_bucket_14_and_30days():
    r=classify(video(published="20260921"),AT,None)
    assert r["window_membership_days"]==[30]

def test_views_per_day_not_automatically_true_growth():
    r=classify(video(),AT,None)
    assert r["average_views_per_day_since_posting_APPROX"]>0
    assert r["observed_views_per_hour_from_snapshots"] is None
    assert not r["real_growth_curve_verified"]
    assert not r["actual_video_watched"]

def test_true_growth_requires_two_observations():
    r=classify(video(views=700000),AT,(400000,"2026-10-08T10:00:00+00:00"))
    assert r["observed_views_delta"]==300000
    assert r["observed_views_per_hour_from_snapshots"]==12500
    assert r["breakout_verified"]

def test_true_growth_does_not_accept_negative_views():
    r=classify(video(views=2),AT,(400000,"2026-10-08T10:00:00+00:00"))
    assert r["observed_views_delta"] is None

def test_real_delta_time_under_one_hour_unavailable():
    r=classify(video(views=500000),AT,(400000,"2026-10-09T09:45:00+00:00"))
    assert r["observed_views_delta"] is None

def test_persistent_ledger_first_seen_preserved(tmp_path):
    ledger=BreakoutLedger(tmp_path/"persistent.sqlite3")
    id1=ledger.begin(AT.isoformat(),["minecraft_gameplay"])
    ledger.ingest(id1,video(),AT.isoformat(),1)
    later=(AT+dt.timedelta(days=1)).isoformat()
    id2=ledger.begin(later,["minecraft_gameplay"])
    assert ledger.older_sighting(VID,later)==(400000,AT.isoformat())
    ledger.ingest(id2,video(views=900000),later,1)
    ledger.queue(VID,"minecraft_gameplay",later,"PUBLIC_METADATA_ONLY")
    with ledger._db() as db:
        row=db.execute("SELECT first_seen FROM videos WHERE video_id=?",(VID,)).fetchone()
    assert row[0]==AT.isoformat()
    assert ledger.stats()["runs"]==2
    assert ledger.stats()["observations"]==2

def test_two_runs_in_days_do_not_overwrite_each_other(tmp_path):
    stub=Stub()
    a=scan_daily(root=tmp_path,client=stub,lanes=["minecraft_gameplay"],
                 now=AT,max_metadata=1,search_per_lane=1)
    b=scan_daily(root=tmp_path,client=stub,lanes=["minecraft_gameplay"],
                 now=AT+dt.timedelta(days=1),max_metadata=1,search_per_lane=1)
    assert a["run_id"]!=b["run_id"]
    assert Path(a["run_report_path"]).exists()
    assert Path(b["run_report_path"]).exists()
    assert b["ledger_stats"]["runs"]==2

def test_two_observations_growth_calculated_after_snapshot(tmp_path):
    stub=Stub()
    scan_daily(root=tmp_path,client=stub,lanes=["minecraft_gameplay"],
               now=AT,max_metadata=1,search_per_lane=1)
    stub.records[VID]=video(views=850000)
    report=scan_daily(root=tmp_path,client=stub,lanes=["minecraft_gameplay"],
                      now=AT+dt.timedelta(days=1),max_metadata=1,search_per_lane=1)
    assert report["verified_candidates"][0]["observed_views_delta"]==450000
    assert report["verified_candidates"][0]["real_growth_curve_verified"]

def test_bad_or_duplicate_lanes_are_rejected_before_network(tmp_path):
    for lanes in (["evil"],["minecraft_gameplay"]*2,[]):
        with pytest.raises(ValueError,match="INVALID_LANES"):
            scan_daily(root=tmp_path,client=Stub(),now=AT,lanes=lanes)

def test_network_limits_enforced_before_calls(tmp_path):
    with pytest.raises(ValueError,match="NETWORK_RESEARCH_BUDGET_EXCEEDED"):
        scan_daily(root=tmp_path,client=Stub(),now=AT,
                   lanes=["minecraft_gameplay"],max_metadata=500)

def test_one_limited_query_cannot_claim_all_youtube(tmp_path):
    record=scan_daily(root=tmp_path,client=Stub(),now=AT,
                      lanes=["minecraft_gameplay"],max_metadata=1,search_per_lane=1)
    assert record["search_result_candidates"]==1
    assert record["results_count"]==1
    assert not record["complete_all_youtube_coverage"]
    assert not record["source_scope_limits"]["actual_video_frame_decode_done"]
    assert not record["source_scope_limits"]["production_method_reliably_inferred"]

def test_claude_research_packet_does_not_execute_model(tmp_path):
    report=scan_daily(root=tmp_path,client=Stub(),now=AT,
                      lanes=["minecraft_gameplay"],max_metadata=1,search_per_lane=1)
    source=create_claude_packet(tmp_path,report,[])
    p=json.loads(source.read_text(encoding="utf-8"))
    assert p["claude_code_called_automatically"] is False
    assert not p["video_scripts_or_assets_generated"]
    assert p["requested_departments"]
    assert "DO_NOT_CLAIM_WATCHED_VIDEO_IF_ONLY_STORYBOARD_OR_METADATA" in p["decision_rules"]

def test_markdown_report_observation_boundary(tmp_path):
    report=scan_daily(root=tmp_path,client=Stub(),now=AT,
                      lanes=["minecraft_gameplay"],max_metadata=1,search_per_lane=1)
    md=report_to_markdown(report,[])
    assert "NOT real growth" in md
    assert "UNKNOWN (first snapshot)" in md
    assert "no video/audio" in md.lower() or "audio" in md.lower()

def test_untrusted_subprocess_cannot_execute_other_programs():
    with pytest.raises(ValueError,match="ONLY_YT_DLP"):
        command_reader(["powershell.exe","-Command","Remove-Item C:\\"])

def test_untrusted_video_source_host_denied():
    with pytest.raises(ValueError,match="UNTRUSTED_STORYBOARD_URL"):
        _pull_jpg("http://127.0.0.1/secret")
    with pytest.raises(ValueError,match="UNTRUSTED_STORYBOARD_URL"):
        _pull_jpg("https://evil.example/sb/X/abcd")

def test_empty_storyboard_format_honestly_unavailable(tmp_path):
    r=inspect_sparse_storyboards(VID,tmp_path,
        extractor=lambda _id: {"id":VID,"formats":[]})
    assert r["status"]=="NO_ACCESSIBLE_PUBLIC_STORYBOARD"
    assert r["shots"]==[]
    assert not r["fully_played_or_decoded_video"]

def test_storyboard_id_mismatch_cannot_claim_access(tmp_path):
    r=inspect_sparse_storyboards(VID,tmp_path,
        extractor=lambda _id: {"id":"L3mZVFZRJ8E","formats":[]})
    assert not r["public_storyboard_actually_fetched"]
    assert any("VIDEO_ID_MISMATCH" in e for e in r["errors"])

def test_channel_follow_and_rescan_is_durable(tmp_path):
    ledger=BreakoutLedger(tmp_path/"watch.sqlite3")
    ledger.follow_channel(video(),AT.isoformat(),"VERIFIED_USER_SEED")
    assert ledger.stats()["followed_competitor_channels"]==1
    watch=ledger.followed()
    assert watch[0]["channel_id"]==CHID
    assert watch[0]["created_at"] is None
    assert not watch[0]["age_confirmed"]
    again=BreakoutLedger(tmp_path/"watch.sqlite3")
    assert again.followed()[0]["reason"]=="VERIFIED_USER_SEED"

def test_competitor_channel_scan_finds_new_video_when_enabled(tmp_path):
    from cinefactory.studio.daily_youtube_breakout_v199 import PublicYoutubeClient
    class WithWatch(Stub):
        def channel_new_videos(self,channel_id,*,limit):
            assert channel_id==CHID
            return [{"id":"L3mZVFZRJ8E","title":"NEW WATCH VIDEO"}]
    stub=WithWatch({
        VID:video(),
        "L3mZVFZRJ8E":video(vid="L3mZVFZRJ8E",views=250000),
    })
    db=BreakoutLedger(tmp_path/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
    db.follow_channel(video(),(AT-dt.timedelta(days=1)).isoformat(),"SAVED_WATCHLIST")
    report=scan_daily(root=tmp_path,client=stub,lanes=["minecraft_gameplay"],
                      now=AT,max_metadata=2,search_per_lane=1)
    assert report["followed_channels_checked"]
    assert len(report["verified_candidates"])==2
    assert "L3mZVFZRJ8E" in {r["video_id"] for r in report["verified_candidates"]}

def test_company_context_instantiates_no_network_scan():
    from cinefactory.appctx import build_context
    from cinefactory.studio.daily_youtube_breakout_v199 import DailyYouTubeBreakoutResearchService
    ctx=build_context(Path(__file__).resolve().parents[1])
    svc=ctx.daily_youtube_breakout_research
    assert isinstance(svc,DailyYouTubeBreakoutResearchService)
    assert svc is ctx.studio.professional_company.daily_youtube_breakout_research
    with pytest.raises(PermissionError,match="MUST_BE_AUTHORIZED"):
        svc.run_explicit()

def test_genuine_live_scan_evidence_and_channels_saved_in_real_repository():
    root=Path(__file__).resolve().parents[1]
    folder=root/"data/research/youtube_breakout"
    runs=sorted((folder/"runs").glob("*_run*.json"))
    assert len(runs)>=2
    good=[json.loads(f.read_text(encoding="utf-8")) for f in runs]
    assert any(r["results_count"]>=1 for r in good)
    assert all(not r["complete_all_youtube_coverage"] for r in good)
    assert all(not r["source_scope_limits"]["actual_video_frame_decode_done"]
               for r in good)
    ledger=BreakoutLedger(folder/"cinefactory_breakout.sqlite3")
    assert ledger.stats()["followed_competitor_channels"]>=2
    assert ledger.stats()["unique_videos"]>=1
    seed=json.loads((folder/"seed_competitors_v199.json").read_text(encoding="utf-8"))
    assert {x["name"] for x in seed if x.get("status")=="VERIFIED_CHANNEL_FOLLOWED"} >= {"Maizen","BigSchool"}
    assert all(x.get("channel_new_channel_status")=="UNKNOWN"
               for x in seed if x.get("status")=="VERIFIED_CHANNEL_FOLLOWED")
