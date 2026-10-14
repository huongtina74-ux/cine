"""v201 contracts: no false viral conclusions, no cross-approval or media claims."""
import datetime as dt
import json
import sqlite3
from pathlib import Path
import pytest
from cinefactory.studio.two_track_research_v201 import (
    ChannelEvidence,VideoEvidence,DualResearchStore,verified_opportunity,
    approved_niche_research,revenue_scenarios,generate_two_track_daily,
    load_v199_snapshot,
)
from cinefactory.studio.channel_provenance_v201 import (
    official_channel_refresh,parse_official_channel,
)
from cinefactory.studio.research_frontier_v201 import find_frontier
from cinefactory.studio.niche_competitor_guard_v200 import LANE_TO_NICHE
ASOF=dt.date(2026,10,9)
WHEN="2026-10-09T10:00:00+00:00"
NEWCID="UC"+"n"*22
OLDCID="UC"+"o"*22
LEAD="UC"+"l"*22
def ch(cid=NEWCID,created="2026-09-25",provenance="YOUTUBE_DATA_API_CHANNELS_SNIPPET_PUBLISHED_AT",subs=None):
    return ChannelEvidence(cid,cid,created,provenance,subs,WHEN if subs else None)
def video(id,channel=NEWCID,format="minecraft_gameplay",views=1000000,
          day="2026-10-01",duration=750):
    return VideoEvidence(id,channel,format,"Original Minecraft 100 Days Survival",day,views,duration,WHEN)
A="t5wy_OsuMvM"
B="L3mZVFZRJ8E"
C="tOKS0VExE_Q"

def test_revenue_is_explicitly_hypothetical():
    s=revenue_scenarios([1_000_000,10_000_000])
    assert all(not row["is_observed_revenue"] and not row["is_earnings_prediction"] for row in s)
    assert any(row["hypothetical_monthly_views"]==1_000_000 for row in s)

def test_two_distinct_million_videos_with_official_age_mature_peer_and_novel_format():
    channels={NEWCID:ch(),OLDCID:ch(OLDCID,"2019-01-01")}
    proof=verified_opportunity(
        fingerprint="proposal-specific completely different mechanic",
        format_id="minecraft_gameplay",
        channels=channels,
        videos=[video(A),video(B,views=2_100_000),
                video(C,channel=OLDCID,views=250_000)],
        mature_peer_channel_ids={OLDCID},
        niche_existing_fingerprints={"minecraft_animation"},as_of=ASOF,
        format_novelty_independently_reviewed=True)
    assert proof["status"]=="EMPIRICAL_BREAKOUT_PATTERN_CONFIRMED_FINANCE_REVIEW_REQUIRED"
    assert proof["winner_channels"][0]["million_video_count"]==2
    assert len(proof["mature_current_demand_evidence"])==1
    assert not proof["can_earn_thousands_monthly_proven"]
    assert not proof["long_term_100k_to_1m_monthly_proven"]
    assert proof["human_greenlight_required"]

def test_same_video_twice_never_meets_two_million():
    result=verified_opportunity(
        fingerprint="new idea",format_id="minecraft_gameplay",
        channels={NEWCID:ch(),OLDCID:ch(OLDCID,"2019-01-01")},
        videos=[video(A),video(A),video(C,channel=OLDCID,views=250000)],
        mature_peer_channel_ids={OLDCID},niche_existing_fingerprints=set(),as_of=ASOF,
        format_novelty_independently_reviewed=True)
    assert result["winner_channels"]==[]
    assert not result["gate_results"]["TWO_DIFFERENT_MILLION_VIDEOS_PER_NEW_CHANNEL"]

def test_channel_creation_from_video_age_must_not_be_inferred():
    for source in (None,"UNVERIFIED", "VIDEO_UPLOAD_DATE_ASSUMED"):
        uncertain=ch(created="2026-09-25",provenance=source)
        assert not uncertain.new_channel_eligible(ASOF)
    without=ChannelEvidence(NEWCID,"New channel",None,None)
    assert not without.new_channel_eligible(ASOF)

@pytest.mark.parametrize("created",["2026-09-08","2026-10-10","2025-01-01"])
def test_age_beyond_0_30_day_window_disallowed(created):
    assert not ch(created=created).new_channel_eligible(ASOF)

def test_exact_0_or_30_days_allowed():
    assert ch(created="2026-10-09").new_channel_eligible(ASOF)
    assert ch(created="2026-09-09").new_channel_eligible(ASOF)

def test_sustainable_demand_requires_mature_same_format_recent_100k():
    proof=verified_opportunity(
        fingerprint="original style change",format_id="minecraft_gameplay",
        channels={NEWCID:ch(),OLDCID:ch(OLDCID,"2010-01-01")},
        videos=[video(A),video(B),video(C,channel=OLDCID,views=99_999)],
        mature_peer_channel_ids={OLDCID},niche_existing_fingerprints=set(),as_of=ASOF,
        format_novelty_independently_reviewed=True)
    assert not proof["gate_results"]["MATURE_SAME_FORMAT_STILL_GETS_100K_VIEWS"]

def test_known_same_format_not_a_new_niche():
    proof=verified_opportunity(
        fingerprint="Minecraft Gameplay",format_id="minecraft_gameplay",
        channels={NEWCID:ch()},
        videos=[video(A),video(B)],
        mature_peer_channel_ids=set(),niche_existing_fingerprints={"minecraft gameplay"},
        as_of=ASOF,format_novelty_independently_reviewed=True)
    assert not proof["gate_results"]["NEW_FORMAT_OR_PROVEN_DIFFERENT_IMPLEMENTATION"]

def test_no_novelty_review_means_not_confirmed():
    proof=verified_opportunity(
        fingerprint="new idea",format_id="minecraft_gameplay",
        channels={NEWCID:ch(),OLDCID:ch(OLDCID,"2019-01-01")},
        videos=[video(A),video(B),video(C,channel=OLDCID,views=200_000)],
        mature_peer_channel_ids={OLDCID},niche_existing_fingerprints=set(),as_of=ASOF)
    assert proof["status"]=="WATCHLIST_INSUFFICIENT_EVIDENCE"
    assert proof["novelty_requires_independent_review"]

def test_only_same_format_counts_million_hits():
    proof=verified_opportunity(
        fingerprint="new original game",format_id="minecraft_gameplay",
        channels={NEWCID:ch()},
        videos=[video(A),video(B,format="minecraft_animation")],
        mature_peer_channel_ids=set(),niche_existing_fingerprints=set(),as_of=ASOF)
    assert not proof["winner_channels"]

def test_short_or_old_videos_do_not_count():
    proof=verified_opportunity(
        fingerprint="new",format_id="minecraft_gameplay",
        channels={NEWCID:ch()},
        videos=[video(A,duration=479),video(B,day="2026-08-01")],
        mature_peer_channel_ids=set(),niche_existing_fingerprints=set(),as_of=ASOF)
    assert not proof["winner_channels"]

def test_approval_cannot_be_inferred_or_written_by_scheduler(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    assert store.approvals()==[]
    with pytest.raises(PermissionError):
        store.approve("minecraft","minecraft_gameplay",actor="AUTOMATION",note="just because",at=WHEN)
    assert not store.approved("minecraft","minecraft_gameplay")

def test_approve_only_one_format_leaves_second_minecraft_route_inactive(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    store.approve("minecraft","minecraft_gameplay",actor="USER_EXPLICIT_APPROVAL",note="personal decision",at=WHEN)
    assert store.approved("minecraft","minecraft_gameplay")
    assert not store.approved("minecraft","minecraft_animation")
    store.approve("minecraft","minecraft_animation",actor="USER_EXPLICIT_APPROVAL",note="separate decision",at=WHEN)
    assert len(store.approvals())==2
    store.pause("minecraft","minecraft_gameplay",actor="USER_EXPLICIT_APPROVAL")
    assert not store.approved("minecraft","minecraft_gameplay")
    assert store.approved("minecraft","minecraft_animation")

def test_wrong_format_approval_blocked(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    with pytest.raises(ValueError,match="NOT_REGISTERED"):
        store.approve("minecraft","asmr_sleep",actor="USER_EXPLICIT_APPROVAL",note="wrong",at=WHEN)

def test_branch_2_hard_block_before_approval(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    report=approved_niche_research(
        store=store,niche_id="minecraft",format_id="minecraft_gameplay",
        channels={NEWCID:ch()},videos=[video(A)],as_of=ASOF)
    assert report["status"]=="NOT_APPROVED_NO_NICHE_RESEARCH"
    assert not report["rivals_leaders"]

def test_branch_2_has_3_distinct_groups_after_approval(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    store.approve("minecraft","minecraft_gameplay",actor="USER_EXPLICIT_APPROVAL",note="genuine",at=WHEN)
    store.link_peer("minecraft","minecraft_gameplay",LEAD,"LEADER","Source-backed large channel",WHEN)
    channels={NEWCID:ch(),LEAD:ch(LEAD,"2014-01-01",subs=2_500_000)}
    items=[
        video(A,channel=LEAD,views=120_000,day="2026-10-01"),
        video(B,channel=LEAD,views=140_000,day="2026-10-02"),
        video(C,channel=LEAD,views=990_000,day="2026-10-03"),
        video("MPNPIaHFoPo",channel=NEWCID,views=1_100_000),
    ]
    result=approved_niche_research(store=store,niche_id="minecraft",format_id="minecraft_gameplay",
                                   channels=channels,videos=items,as_of=ASOF)
    assert result["status"].startswith("APPROVED")
    assert result["cohort_A_leaders"][0]["million_subscribers_verified"]
    assert len(result["cohort_A_leaders"][0]["recent_outperformance_vs_same_channel_median"])==1
    assert len(result["cohort_B_new_channels"])==1
    assert len(result["cohort_C_trends_0_15d_million"])==1
    assert result["cohort_C_trends_0_15d_million"][0]["video_id"]=="MPNPIaHFoPo"
    assert not result["approved_for_publication"]
    assert not result["shot_by_shot_audio_analysis_completed"]

def test_trend_0_15_days_only_and_million_views(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    store.approve("minecraft","minecraft_animation",actor="USER_EXPLICIT_APPROVAL",note="ok",at=WHEN)
    items=[video(A,format="minecraft_animation",day="2026-09-24"),
           video(B,format="minecraft_animation",day="2026-09-23",views=3_000_000),
           video(C,format="minecraft_animation",day="2026-10-05",views=999_999)]
    r=approved_niche_research(store=store,niche_id="minecraft",format_id="minecraft_animation",
                              channels={NEWCID:ch()},videos=items,as_of=ASOF)
    assert [v["video_id"] for v in r["cohort_C_trends_0_15d_million"]]==[A]

def test_format_proposals_are_hypotheses_and_deduplicated(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    key=store.propose_format("New visual physics loop",
             "new visual physics loop no dialogue","NEW_CATEGORY",
             "Distinct from existing Long Slide",WHEN)
    assert key.startswith("proposal_")
    assert store.proposals()[0]["state"]=="HYPOTHESIS_UNVERIFIED"
    with pytest.raises(ValueError,match="DUPLICATE"):
        store.propose_format("Duplicate"," NEW   visual physics loop no dialogue ",
                             "NEW_CATEGORY","Another",WHEN)

def test_official_channel_published_at_verified_but_not_video_upload():
    official=parse_official_channel({
        "id":NEWCID,"snippet":{"title":"Channel","publishedAt":"2026-09-25T12:00:00Z"},
        "statistics":{"subscriberCount":"15000"}}, {NEWCID})
    assert official.has_verified_creation
    assert official.new_channel_eligible(ASOF)
    assert official.subscriber_count==15_000
    with pytest.raises(ValueError,match="MISMATCH"):
        parse_official_channel({"id":OLDCID,"snippet":{"publishedAt":"2026-01-01T00:00:00Z"}},{NEWCID})

def test_api_without_key_fails_closed_and_never_contacts_network(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    got=official_channel_refresh(store,[NEWCID],api_key="")
    assert got["status"]=="NO_API_KEY_AGES_REMAIN_UNKNOWN"
    assert not got["official_age_verified"]
    assert store.channel(NEWCID) is None

def test_mock_official_api_writes_dates_without_revealing_key(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    def source(url):
        assert url.startswith("https://www.googleapis.com/youtube/v3/channels?")
        assert "not-a-real-test-key" in url
        return {"items":[{
            "id":NEWCID,"snippet":{"title":"Channel","publishedAt":"2026-09-25T00:00:00Z"},
            "statistics":{"hiddenSubscriberCount":True,"subscriberCount":"123456"},
        }]}
    got=official_channel_refresh(store,[NEWCID],api_key="not-a-real-test-key",fetch_json=source)
    assert got["channels_updated"]==1
    assert got["api_key_redacted"]
    assert "not-a-real-test-key" not in json.dumps(got)
    assert store.channel(NEWCID).new_channel_eligible(ASOF)
    assert store.channel(NEWCID).subscriber_count is None

def test_global_report_from_actual_local_ledger_does_not_falsely_claim_success(tmp_path):
    r=generate_two_track_daily(tmp_path,as_of=ASOF)
    assert r["branch_1_global_new_niche_scan"]["status"]=="NO_EMPIRICAL_WINNING_NICHE_CONFIRMED"
    assert r["branch_2_approved_niche_studies"]["approved_format_count"]==0
    assert not r["full_competitor_videos_watched"]
    assert Path(r["report_path"]).exists()

def test_frontier_classification_is_a_backlog_not_new_niche(tmp_path):
    class Stub:
        def search(self,_term,*,limit):
            return [{"id":A,"title":"Interesting original creator video"}]
        def read(self,_argv,*,timeout):
            return json.dumps({"id":A,"title":"Unusual seamless long form colorful kinetic videos",
                               "upload_date":"20261008","duration":800,"view_count":1_800_000,
                               "channel_id":NEWCID,"was_live":False})
    r=find_frontier(root=tmp_path,client=Stub(),now=dt.datetime(2026,10,9,tzinfo=dt.timezone.utc),
                    queries=1,limit_per_query=1,max_watch=1)
    assert r["unclassified_count"]==1
    assert r["candidate_videos"][0]["new_niche_verified"] is False
    assert r["candidate_videos"][0]["two_million_videos_confirmed"] is False
    assert r["status"]=="FRONTIER_RESEARCH_BACKLOG_NOT_WINNING_NICHES"

def test_v201_format_novelty_needs_independent_review_sources(tmp_path):
    store=DualResearchStore(tmp_path/"research.sqlite3")
    key=store.propose_format("New editorial format","unique audience game interaction",
                             "NEW_CATEGORY","not present in known blueprints",WHEN)
    with pytest.raises(PermissionError,match="INDEPENDENT"):
        store.review_format_novelty(key,source_ids=["s1","s2"],actor="AUTOMATION",at=WHEN)
    with pytest.raises(ValueError,match="TWO_INDEPENDENT"):
        store.review_format_novelty(key,source_ids=["s1","s1"],
                                    actor="INDEPENDENT_HUMAN_RESEARCH_REVIEW",at=WHEN)
    store.review_format_novelty(key,source_ids=["source_1","source_2"],
                                actor="INDEPENDENT_HUMAN_RESEARCH_REVIEW",at=WHEN)
    assert store.proposals()[0]["state"]=="DISTINCT_FORMAT_REVIEWED"

def test_studio_company_exposes_two_branch_read_only_research(tmp_path):
    from cinefactory.studio.daily_youtube_breakout_v199 import DailyYouTubeBreakoutResearchService
    svc=DailyYouTubeBreakoutResearchService(tmp_path)
    assert svc.niche_research_approvals()==[]
    r=svc.two_branch_owner_report()
    assert r["branch_2_approved_niche_studies"]["status"]=="NO_USER_APPROVED_NICHES"

def test_official_source_mature_channel_and_newborn_channel_different_cohorts():
    assert ch().new_channel_eligible(ASOF)
    assert not ch().mature_channel_eligible(ASOF)
    assert ch(OLDCID,"2019-01-01").mature_channel_eligible(ASOF)
    assert not ch(OLDCID,"2019-01-01").new_channel_eligible(ASOF)

def test_report_renderer_generates_two_distinct_human_readable_markdowns(tmp_path,monkeypatch):
    from scripts import run_two_track_research_v201 as runner
    monkeypatch.setattr(runner,"ROOT",tmp_path)
    result=generate_two_track_daily(tmp_path,as_of=ASOF)
    out=runner.write_owner_briefs(result,frontier=None,deep=None)
    a=Path(out["branch_1_markdown"]).read_text(encoding="utf-8")
    b=Path(out["branch_2_markdown"]).read_text(encoding="utf-8")
    assert "2+ DISTINCT" in a and "1,000,000+" in a
    assert "BRANCH 2" in b and "APPROVED" in b
    assert Path(out["branch_1_markdown"]).exists()
    assert out["approved_niche_agent_packets"]==[]

def test_windows_scheduled_job_integrates_both_paths_without_auto_approval():
    source=(Path(__file__).resolve().parents[1]/
        "scripts/daily_cinefactory_research_v199.ps1").read_text(encoding="utf-8")
    assert "run_daily_cinefactory_youtube_v199.py" in source
    assert "run_two_track_research_v201.py" in source
    assert "--with-frontier --scan-approved" in source
    assert "--approve-niche" not in source

def test_parent_niche_market_valid_only_with_independent_relationship_review():
    channels={NEWCID:ch(),OLDCID:ch(OLDCID,"2015-03-02")}
    evidence=[video(A),video(B),
              video(C,channel=OLDCID,format="minecraft_animation",views=200_000)]
    args=dict(fingerprint="new original mechanic",format_id="minecraft_gameplay",
              channels=channels,videos=evidence,
              mature_peer_channel_ids={OLDCID},niche_existing_fingerprints=set(),
              as_of=ASOF,format_novelty_independently_reviewed=True,
              broader_parent_format_ids={"minecraft_animation"})
    without=verified_opportunity(**args,parent_demand_relationship_reviewed=False)
    assert not without["gate_results"]["MATURE_SAME_FORMAT_STILL_GETS_100K_VIEWS"]
    reviewed=verified_opportunity(**args,parent_demand_relationship_reviewed=True)
    assert reviewed["broader_parent_market_used"]
    assert reviewed["gate_results"]["MATURE_SAME_FORMAT_STILL_GETS_100K_VIEWS"]

def test_earnings_require_views_assumptions_not_automatic_monetization_proof():
    result=verified_opportunity(
        fingerprint="novel",format_id="minecraft_gameplay",
        channels={},videos=[],mature_peer_channel_ids=set(),
        niche_existing_fingerprints=set(),as_of=ASOF)
    needed=result["hypothetical_monthly_views_needed_before_costs"]
    assert {x["monthly_views_required"] for x in needed["3000"]}=={6_000_000,1_500_000,600_000,300_000}
    assert "1000000" in needed
    assert not result["can_earn_thousands_monthly_proven"]
