"""Approved-niche market catalogue must not conflate metadata with true A/V QC."""
import datetime as dt
import json
from pathlib import Path
from cinefactory.studio.two_track_research_v201 import DualResearchStore
from cinefactory.studio.approved_minecraft_rival_catalog_v256 import compile_approved_minecraft_catalog
from cinefactory.studio.daily_youtube_breakout_v199 import BreakoutLedger,PublicVideo

NOW="2026-10-11T07:00:00+00:00"
def approve(tmp_path):
    root=Path(tmp_path)
    store=DualResearchStore(root/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
    for fmt in ("minecraft_animation","minecraft_gameplay"):
        store.approve("minecraft",fmt,actor="USER_EXPLICIT_APPROVAL",note="User selected both",at=NOW)
    return store

def test_original_sources_ranked_separately_and_no_av_certification(tmp_path):
    approve(tmp_path)
    folder=tmp_path/"docs"
    folder.mkdir()
    data={"all":[
        {"id":"W7R8k10Kjk","title":"JJ vs Mikey - Minecraft Animation movie",
         "channel":"Example Animator","channel_id":"UC"+"a"*22,
         "views":2200000,"duration_sec":1800,"date":"2026-10-03","age_days":8},
        {"id":"t5wy_OsuMvM","title":"JJ and Mikey Survived 100 Days in Minecraft",
         "channel":"Example Gamer","channel_id":"UC"+"b"*22,
         "views":1500000,"duration_sec":2400,"date":"2026-10-05","age_days":6},
        {"id":"NvoKphWCXXk","title":"Minecraft obby in Roblox 100 days",
         "channel":"Off niche","channel_id":"UC"+"c"*22,
         "views":9000000,"duration_sec":900,"date":"2026-10-09","age_days":2},
    ]}
    (folder/"MINECRAFT_WIDE_RANK_V253.json").write_text(json.dumps(data))
    r=compile_approved_minecraft_catalog(tmp_path,as_of=dt.date(2026,10,11))
    fmt={f["format_id"]:f for f in r["format_reports"]}
    assert fmt["minecraft_animation"]["breakouts_1m_within_14d_snapshot_count"]==1
    assert fmt["minecraft_gameplay"]["breakouts_1m_within_14d_snapshot_count"]==1
    assert fmt["minecraft_animation"]["rival_channel_candidates"][0]["confirmed_competitor_by_full_audio_video"] is False
    assert fmt["minecraft_gameplay"]["full_video_review_queue"][0]["video_fully_watched"] is False
    assert fmt["minecraft_animation"]["new_channel_two_1m_proven"] is False
    assert all(v["views_observed"]!=9000000 for f in fmt.values() for v in f["top_90d"])

def test_new_daily_ledger_video_is_merged_into_historical_catalog(tmp_path):
    store=approve(tmp_path)
    led=BreakoutLedger(store.path)
    r=led.begin(NOW,["minecraft_gameplay"])
    vid=PublicVideo.parse({
        "id":"12345678901","title":"I Survived 100 Days in Minecraft Hardcore",
        "upload_date":"20261009","duration":1080,"view_count":1250000,
        "channel_id":"UC"+"d"*22,"channel":"Upcoming creator"
    },"minecraft_gameplay")
    led.ingest(r,vid,NOW,1)
    report=compile_approved_minecraft_catalog(tmp_path,as_of=dt.date(2026,10,11))
    assert report["fresh_or_updated_ledger_video_count"]==1
    gameplay=next(f for f in report["format_reports"] if f["format_id"]=="minecraft_gameplay")
    assert gameplay["breakouts_1m_within_14d_snapshot_count"]==1
    assert gameplay["top_30d"][0]["video_id"]=="12345678901"
    assert gameplay["rival_channel_candidates"][0]["channel_creation_research_pending"]
    assert gameplay["rival_channel_candidates"][0]["channel_born_0_30_days_verified"] is False
