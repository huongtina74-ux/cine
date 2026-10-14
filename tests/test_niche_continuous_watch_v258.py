"""Persistent niche watch: repeat competitors, newcomer evidence and true snapshot velocity."""
import datetime as dt
from cinefactory.studio.two_track_research_v201 import DualResearchStore, ChannelEvidence
from cinefactory.studio.niche_continuous_watch_v258 import NicheCompetitorWatch

CID="UC"+"x"*22
NOW="2026-10-11T08:00:00+00:00"

def make(tmp_path):
    store=DualResearchStore(tmp_path/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
    store.approve("minecraft","minecraft_animation",actor="USER_EXPLICIT_APPROVAL",
                  note="Owner approval",at=NOW)
    return store,NicheCompetitorWatch(tmp_path)

def add(w,vid,views=1200000,at=NOW,precision="INSTANT"):
    return w.add(niche_id="minecraft",format_id="minecraft_animation",
                 video_id=vid,channel_id=CID,channel_name="Candidate animation studio",
                 title="Minecraft Animation story",published_day="2026-10-08",
                 duration_sec=1100,views=views,observed_at=at,
                 origin="SOURCE_METADATA",observation_precision=precision)

def test_new_channel_continues_watch_as_existing_and_two_distinct_million(tmp_path):
    store,w=make(tmp_path)
    store.save_channel(ChannelEvidence(CID,"Candidate animation studio","2026-10-01",
        "YOUTUBE_DATA_API_CHANNELS_SNIPPET_PUBLISHED_AT",120000,NOW),NOW)
    assert add(w,"A"*11)
    assert add(w,"B"*11)
    report=w.report(as_of=dt.datetime.fromisoformat(NOW))
    c=report["candidate_channels"][0]
    assert c["strict_newcomer_winner"]
    assert c["qualifying_distinct_early_million_videos"]==2
    assert c["tracking_state"]=="NEWLY_ADDED"
    assert c["was_new_at_discovery"]
    assert {v["views_per_subscriber"] for v in report["ranked_video_signals"]}=={10}
    future=w.report(as_of=dt.datetime(2026,11,18,tzinfo=dt.timezone.utc))
    old=future["candidate_channels"][0]
    assert old["tracking_state"]=="ONGOING_TRACKING"
    assert old["was_new_at_discovery"] and old["strict_newcomer_winner"]
    assert future["tracked_channels"]==1
    assert NicheCompetitorWatch(tmp_path).report(as_of=dt.datetime.fromisoformat(NOW))["tracked_channels"]==1

def test_metadata_cannot_prove_creation_or_ratio_when_missing(tmp_path):
    _,w=make(tmp_path)
    assert add(w,"C"*11)
    r=w.report(as_of=dt.datetime.fromisoformat(NOW))
    assert not r["candidate_channels"][0]["strict_newcomer_winner"]
    assert r["candidate_channels"][0]["verified_created_day"] is None
    assert r["ranked_video_signals"][0]["views_per_subscriber"] is None
    assert r["ranked_video_signals"][0]["measured_views_per_hour"] is None

def test_true_two_snapshots_required_for_five_day_vph_and_day_only_ignored(tmp_path):
    _,w=make(tmp_path)
    assert add(w,"D"*11,views=200000,at="2026-10-11T00:00:00+00:00",precision="DATE_ONLY")
    assert add(w,"D"*11,views=250000,at="2026-10-11T08:00:00+00:00")
    r=w.report(as_of=dt.datetime.fromisoformat(NOW))
    assert r["ranked_video_signals"][0]["measured_views_per_hour"] is None
    assert add(w,"D"*11,views=275000,at="2026-10-11T10:00:00+00:00")
    q=w.report(as_of=dt.datetime.fromisoformat("2026-10-11T10:00:00+00:00"))
    assert q["ranked_video_signals"][0]["measured_views_per_hour"]==12500
    assert "EARLY_5D_MEASURED_MOMENTUM" in q["ranked_video_signals"][0]["signals"]

def test_wrong_format_never_enter_watch_without_approval(tmp_path):
    _,w=make(tmp_path)
    assert not w.add(niche_id="minecraft",format_id="minecraft_gameplay",
            video_id="E"*11,channel_id=CID,channel_name="Wrong",
            title="Minecraft 100 days",published_day="2026-10-08",
            duration_sec=1200,views=1000000,observed_at=NOW,origin="PUBLIC")
    assert not w.add(niche_id="minecraft",format_id="minecraft_animation",
            video_id="F"*11,channel_id=CID,channel_name="Short",
            title="Minecraft animation",published_day="2026-10-08",
            duration_sec=60,views=1000000,observed_at=NOW,origin="PUBLIC")
    assert w.report(as_of=dt.datetime.fromisoformat(NOW))["tracked_channels"]==0
