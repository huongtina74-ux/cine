"""Verified Branch 2 searches only user approved formats."""
import datetime as dt
import pytest
from cinefactory.studio.approved_niche_keyword_scan_v201 import (
    KEYWORD_PACKS,search_approved_formats,
)
from cinefactory.studio.two_track_research_v201 import DualResearchStore,LANE_TO_NICHE
from cinefactory.studio.daily_youtube_breakout_v199 import PublicVideo
AT=dt.datetime(2026,10,9,10,tzinfo=dt.timezone.utc)
A="t5wy_OsuMvM"
B="L3mZVFZRJ8E"
CH="UC"+"g"*22
class Stub:
    def __init__(self,title="JJ Survived 100 Days Hardcore in Minecraft"):
        self.title=title
        self.search_calls=0
        self.video_calls=0
    def search(self,key,*,limit):
        self.search_calls+=1
        return [{"id":A,"title":self.title}]
    def video(self,vid,*,lane):
        self.video_calls+=1
        return PublicVideo.parse({
            "id":vid,"title":self.title,"upload_date":"20261008",
            "duration":1200,"view_count":1_250_000,
            "channel_id":CH,"channel":"Stub creator","was_live":False,
        },lane)

def approve(tmp_path,niche="minecraft",fmt="minecraft_gameplay"):
    store=DualResearchStore(tmp_path/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
    store.approve(niche,fmt,actor="USER_EXPLICIT_APPROVAL",
                  note="User authorizes format-specific research",at=AT.isoformat())
    return store

def test_all_14_formats_have_multiple_search_queries():
    assert set(KEYWORD_PACKS)==set(LANE_TO_NICHE)
    assert all(len(queries)>=3 for queries in KEYWORD_PACKS.values())

def test_no_approval_means_strict_no_network_calls(tmp_path):
    spy=Stub()
    r=search_approved_formats(root=tmp_path,client=spy,as_of=AT)
    assert r["status"]=="NO_APPROVED_NICHES_NO_NETWORK_CONTACT"
    assert spy.search_calls==0 and spy.video_calls==0

def test_explicit_approval_runs_only_its_own_queries(tmp_path):
    approve(tmp_path)
    spy=Stub()
    r=search_approved_formats(root=tmp_path,client=spy,as_of=AT,
                              per_niche_keywords=3,max_total_metadata=4)
    assert r["approved_format_count"]==1
    assert spy.search_calls==3
    assert spy.video_calls==1  # ID dedup across keyword variants
    assert len(r["admitted"])==1
    assert r["admitted"][0]["format_id"]=="minecraft_gameplay"
    assert r["quarantined"]==[]
    assert r["never_cross_into_unapproved_niches"]

def test_wrong_niche_in_search_does_not_get_ingested(tmp_path):
    approve(tmp_path)
    spy=Stub(title="The Love Story of Steve and Sadako Minecraft Animation")
    r=search_approved_formats(root=tmp_path,client=spy,as_of=AT,
                              per_niche_keywords=1,max_total_metadata=1)
    assert r["admitted"]==[]
    assert len(r["quarantined"])==1

def test_paused_format_stops_future_extra_search(tmp_path):
    store=approve(tmp_path)
    store.pause("minecraft","minecraft_gameplay",actor="USER_EXPLICIT_APPROVAL")
    spy=Stub()
    r=search_approved_formats(root=tmp_path,client=spy,as_of=AT)
    assert r["status"]=="NO_APPROVED_NICHES_NO_NETWORK_CONTACT"
    assert spy.search_calls==0

def test_max_total_metadata_budget_enforced(tmp_path):
    with pytest.raises(ValueError,match="BUDGET"):
        search_approved_formats(root=tmp_path,max_total_metadata=500)

def test_reviewed_proposed_format_requires_actual_media_review_provenance(tmp_path):
    from cinefactory.studio.two_track_research_v201 import VideoEvidence
    store=DualResearchStore(tmp_path/"research.sqlite3")
    key=store.propose_format("Original kinetic story", "nonexisting unique kinetic method",
                             "NEW_CATEGORY","not the same as minecraft animation",
                             AT.isoformat())
    v=VideoEvidence(A,CH,key,"Original film", "2026-10-08",1_500_000,1800,AT.isoformat())
    with pytest.raises(PermissionError,match="TRACEABLE"):
        store.store_reviewed_format_video(v,format_review_provenance="METADATA_ONLY")
    store.store_reviewed_format_video(v,format_review_provenance="VISUAL_REVIEW:original public timeline frame backed observation")
    assert store.reviewed_videos()[0].format_id==key

def test_multiple_minecraft_formats_can_each_be_separately_approved(tmp_path):
    store=approve(tmp_path)
    store.approve("minecraft","minecraft_animation",actor="USER_EXPLICIT_APPROVAL",
                  note="Separately approved story animation",at=AT.isoformat())
    assert {x["format_id"] for x in store.approvals()}=={
        "minecraft_gameplay","minecraft_animation"}

def test_two_approved_formats_share_budget_without_starving_one(tmp_path):
    store=approve(tmp_path)
    store.approve("minecraft","minecraft_animation",actor="USER_EXPLICIT_APPROVAL",
                  note="Enable second Minecraft format",at=AT.isoformat())
    class Distinct:
        def search(self,key,*,limit):
            base=("anim" if ("animation" in key or "movie" in key) else "game")
            return [{"id":(base+str(i)).ljust(11,"A")} for i in range(6)]
        def video(self,vid,*,lane):
            title=("Minecraft Animation JJ Mikey original movie"
                  if lane=="minecraft_animation"
                  else "Minecraft 100 Days Survival Challenge")
            return PublicVideo.parse({"id":vid,"title":title,
                "upload_date":"20261008","duration":1200,"view_count":1_200_000,
                "channel_id":CH,"channel":"Sample studio"},lane)
    r=search_approved_formats(root=tmp_path,client=Distinct(),as_of=AT,
                              per_niche_keywords=4,per_query=6,max_total_metadata=6)
    assert r["full_metadata_checks"]==6
    observed={a["format_id"] for a in r["admitted"]}
    assert observed=={"minecraft_gameplay","minecraft_animation"}
    assert sum(a["format_id"]=="minecraft_animation" for a in r["admitted"])==3
    assert sum(a["format_id"]=="minecraft_gameplay" for a in r["admitted"])==3
