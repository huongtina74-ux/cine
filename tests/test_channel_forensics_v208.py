"""v208 channel URL -> source-truthed video taxonomy -> same-format peers."""
from datetime import datetime,timezone
import json

import pytest
from typer.testing import CliRunner
from cinefactory.cli import app
from cinefactory.studio.channel_forensics_v208 import (
    ChannelSample,Sample,classify_video,analyze_channel,plan_queries,
    compare_peer,rank_peer_channels,
)
from cinefactory.research_intelligence.channel_forensics_runner_v208 import (
    normalize_reference,run_forensics,collect_channel,store_dossier,
)

A="UC"+"a"*22
B="UC"+"b"*22
C="UC"+"c"*22
URL="https://www.youtube.com/@OriginalSource/videos"


def vid(i):
    return "v"+str(i).zfill(10)


def sample(i,title,channel=A,*,duration=600,live="NOT_LIVE",views=1000):
    return Sample(
        video_id=vid(i),channel_id=channel,title=title,
        duration_seconds=duration,live_state=live,views=views,
        published_at="20261008",source="PUBLIC_METADATA_ONLY",
    )


def snapshot(titles,channel=A,url=URL):
    return ChannelSample(
        channel_id=channel,submitted_url=url,
        videos=[sample(i+1,t,channel=channel) for i,t in enumerate(titles)],
        collected_at="2026-10-10T07:00:00+00:00",
    )


@pytest.mark.parametrize("title,wanted",[
    ("Minecraft school animation funny class full episode","minecraft_school_comedy"),
    ("Minecraft animated adventure movie full episode","minecraft_story_adventure"),
    ("Minecraft monster animation fantasy movie","minecraft_monster_fantasy"),
    ("Minecraft animated challenge episode","minecraft_animated_challenge"),
    ("Minecraft survival gameplay 100 days","minecraft_recorded_survival"),
    ("Minecraft real gameplay build tutorial","minecraft_gameplay_tutorial"),
    ("Minecraft livestream real player survival","minecraft_live_gameplay"),
    ("Minecraft machinima cinematic in-game short film","minecraft_scripted_machinima"),
    ("3D animal long slide obstacle race game full video","long_slide_game"),
    ("ASMR sleep hand sounds tapping no talking","asmr_sleep"),
    ("rain sounds sleep white noise thunderstorm","rain_sleep_white_noise"),
    ("silent fishing no talking full session","fishing_silent"),
    ("3D nursery rhymes original kids songs animation","preschool_musical"),
    ("Roblox R6 animated story full film","roblox_animation"),
    ("GTA V gameplay racing challenge","gta_gameplay"),
])
def test_per_video_taxonomy_is_not_keyword_only(title,wanted):
    got=classify_video(sample(1,title))
    assert got.minor_niche==wanted,got
    assert got.status=="METADATA_MATCH_CANDIDATE"
    assert got.actual_visual_reviewed is False
    assert got.safe_as_competitor_evidence is False


@pytest.mark.parametrize("title",[
    "Minecraft new update cool video",
    "Minecraft challenge movie",  # no proof animation or recorded game
    "Minecraft 100 days animated gameplay",
    "Minecraft real gameplay animation full movie",
    "Minecraft cinematic episode",
])
def test_ambiguous_minecraft_does_not_become_false_competitor(title):
    assert classify_video(sample(1,title)).status=="AMBIGUOUS"


@pytest.mark.parametrize("state",["LIVE","PAST_LIVE","UPCOMING"])
def test_livestream_never_counts_as_longform_story(state):
    item=sample(1,"Minecraft animation school story long film",live=state)
    result=classify_video(item)
    assert result.status=="EXCLUDED_LIVE"
    assert result.minor_niche=="minecraft_live_gameplay"
    assert not compare_peer("minecraft_school_comedy",item)[
        "same_subniche_and_media_lane_metadata"]


def test_dominant_channel_is_built_from_episodes_not_from_handle_keywords():
    data=snapshot([
        "Minecraft school animation episode funny classroom",
        "Minecraft animated school class cartoon",
        "Minecraft school comedy animation full movie",
        "Minecraft school animation series new episode",
        "Minecraft real gameplay survival 100 days",
    ])
    report=analyze_channel(data)
    assert report["market_major_niche"]=="minecraft"
    assert report["dominant_minor_niche"]=="minecraft_school_comedy"
    assert report["dominant_share_of_sample"]==0.8
    assert len(report["longform_nonlive_ids_matching_dominant_metadata"])==4
    q=report["search_plan"]["queries"]
    assert q and all("Minecraft" in x["query"] for x in q)
    assert all("school" in x["query"].lower() or "class" in x["query"].lower()
               for x in q)
    assert report["format_characteristics"]["likely_production_lane"]=="FILM_ANIMATION"
    assert report["high_confidence_semantic_fit"] is False


def test_mixed_channel_reports_multiple_subniches_without_false_dominant_query():
    data=snapshot([
        "Minecraft school animation full movie",
        "Minecraft school animation funny cartoon",
        "Minecraft survival gameplay 100 days",
        "Minecraft real survival gameplay 100 days",
        "Minecraft livestream real player survival",
    ])
    report=analyze_channel(data)
    assert report["status"]=="MIXED_OR_INSUFFICIENT_SAMPLE"
    assert report["dominant_minor_niche"] is None
    assert report["search_plan"]["queries"]==[]
    assert "minecraft_school_comedy" in report["per_subniche_search_plans"]
    assert "minecraft_recorded_survival" in report["per_subniche_search_plans"]


def test_unknown_channels_cannot_be_assigned_from_name_alone():
    report=analyze_channel(snapshot([
        "Amazing fun times", "The best day in the world", "Everybody check this",
    ]))
    assert report["dominant_minor_niche"] is None
    assert report["status"]=="UNKNOWN_NOT_ENOUGH_FORMAT_EVIDENCE"


def test_one_viral_video_is_not_enough_for_channel_competitor_membership():
    original=[
        sample(31,"Minecraft school animation full movie",channel=B),
        sample(32,"Minecraft real gameplay survival 100 days",channel=B),
        sample(33,"Minecraft animated school comedy episode",channel=C),
    ]
    peers=rank_peer_channels("minecraft_school_comedy",original)
    assert peers["metadata_peer_channel_candidates"]==[]
    assert len(peers["single_video_matches_unconfirmed"])==2


def test_two_same_subniche_8min_peers_admitted_only_as_metadata_candidates():
    items=[
        sample(31,"Minecraft school animation full movie",channel=B),
        sample(32,"Minecraft animated school classroom episode",channel=B),
        sample(33,"Minecraft real survival gameplay 100 days",channel=C),
        sample(34,"Minecraft school animated comedy film",channel=C,duration=180),
        sample(35,"Minecraft school animated comedy movie",channel=C,live="PAST_LIVE"),
        sample(36,"Minecraft school animated story",channel=C,live="UNKNOWN"),
    ]
    rank=rank_peer_channels("minecraft_school_comedy",items)
    assert len(rank["metadata_peer_channel_candidates"])==1
    assert rank["metadata_peer_channel_candidates"][0]["channel_id"]==B
    assert rank["verified_competitors"]==[]
    assert rank["independent_video_review_required"] is True
    assert len(rank["rejected_video_matches"])==4


@pytest.mark.parametrize("url",[
    "http://youtube.com/@channel",
    "https://evil.example/@channel",
    "https://youtube.com.evil.example/@channel",
    "file:///etc/passwd",
    "https://user:pass@youtube.com/@channel",
    "https://youtube.com:8080/@channel",
    "https://youtube.com/redirect?url=https://evil.test",
])
def test_external_reference_links_are_strictly_allowlisted(url):
    with pytest.raises(ValueError):
        normalize_reference(url)


def test_handles_channel_ids_and_watch_urls_without_guessing():
    assert normalize_reference("https://youtube.com/@TestChannel/videos")[
        "channel_url"]=="https://www.youtube.com/@TestChannel/videos"
    assert normalize_reference("https://www.youtube.com/channel/"+A+"/videos")[
        "channel_id"]==A
    assert normalize_reference("https://www.youtube.com/watch?v="+vid(1))[
        "video_id"]==vid(1)
    assert normalize_reference("https://youtu.be/"+vid(1))["kind"]=="VIDEO"


def test_channel_source_rejects_foreign_videos_duplicates_and_time_naivety():
    with pytest.raises(ValueError,match="OTHER_CHANNEL_VIDEO"):
        ChannelSample(channel_id=A,submitted_url=URL,videos=[
            sample(1,"Minecraft animation story",A),
            sample(2,"Minecraft animation story",B),
        ],collected_at="2026-10-10T07:00:00+00:00")
    with pytest.raises(ValueError,match="DUPLICATE_VIDEO"):
        ChannelSample(channel_id=A,submitted_url=URL,videos=[
            sample(1,"Minecraft animation story",A),
            sample(1,"Minecraft animation story",A),
        ],collected_at="2026-10-10T07:00:00+00:00")
    with pytest.raises(ValueError,match="COLLECTION_TIME"):
        ChannelSample(channel_id=A,submitted_url=URL,videos=[
            sample(1,"Minecraft animation story",A),
        ],collected_at="2026-10-10T07:00:00")


def test_keyword_plan_is_subniche_specific_and_budgeted():
    school=plan_queries("minecraft_school_comedy",budget=4)
    game=plan_queries("minecraft_recorded_survival",budget=4)
    assert school["queries"]!=game["queries"]
    assert all("school" in x["query"].lower() or "class" in x["query"].lower()
               for x in school["queries"])
    assert all("gameplay" in x["query"].lower() or "real player" in x["query"].lower()
               for x in game["queries"])
    assert school["paid_api_calls_required"] is False
    with pytest.raises(ValueError,match="QUERY_BUDGET"):
        plan_queries("minecraft_school_comedy",budget=99)


class StubFreeYoutubeClient:
    def __init__(self):
        self.calls=[]
        self.records={
            vid(1):{"channel_id":A,"title":"Minecraft school animation episode one"},
            vid(2):{"channel_id":A,"title":"Minecraft animated school comedy episode two"},
            vid(3):{"channel_id":A,"title":"Minecraft animated school classroom episode three"},
            vid(4):{"channel_id":A,"title":"Minecraft school animation full movie four"},
            vid(11):{"channel_id":B,"title":"Minecraft school animation long episode"},
            vid(12):{"channel_id":B,"title":"Minecraft animated school comedy full movie"},
            vid(13):{"channel_id":C,"title":"Minecraft recorded survival gameplay 100 days"},
            vid(14):{"channel_id":C,"title":"Minecraft animated school movie", "live_status":"was_live"},
        }
    def read(self,argv,*,timeout):
        self.calls.append(argv)
        if "--flat-playlist" in argv:
            if "/channel/"+A+"/videos" not in argv[-1]:
                raise RuntimeError("unexpected channel")
            return "\n".join(json.dumps({"id":vid(i)}) for i in range(1,5))
        if "--dump-single-json" in argv:
            v=argv[-1].split("v=",1)[-1]
            row=self.records[v]
            return json.dumps({
                "id":v,"channel_id":row["channel_id"],"title":row["title"],
                "upload_date":"20261009","duration":680,"view_count":300000,
                "live_status":row.get("live_status","not_live"),
            })
        raise AssertionError("Unsupported public read invocation")
    def search(self,keyword,*,limit):
        self.calls.append(("search",keyword,limit))
        assert "Minecraft" in keyword
        return [{"id":vid(i)} for i in (11,12,13,14)]


def test_public_discovery_uses_existing_free_transport_and_filters_wrong_competitors():
    client=StubFreeYoutubeClient()
    url="https://youtube.com/channel/"+A+"/videos"
    report=run_forensics(url,client=client,search=True,max_videos=4)
    assert report["classification"]["dominant_minor_niche"]=="minecraft_school_comedy"
    assert report["competitor_discovery"]["no_paid_credits_used"] is True
    p=report["competitor_discovery"]["peer_matches"]
    assert len(p["metadata_peer_channel_candidates"])==1
    assert p["metadata_peer_channel_candidates"][0]["channel_id"]==B
    assert p["verified_competitors"]==[]
    assert any(x["reason"]=="DIFFERENT_MINOR_NICHE_OR_UNCLASSIFIED"
               for x in p["rejected_video_matches"])
    assert report["industry_market_winner_verified"] is False
    assert report["studio_production_approved"] is False
    assert all(x[0] not in ("pip","curl") for x in client.calls)


def test_search_peers_refuses_empty_channel_niche_evidence():
    unknown=analyze_channel(snapshot(["Odd project","Stuff happened"]))
    client=StubFreeYoutubeClient()
    from cinefactory.research_intelligence.channel_forensics_runner_v208 import search_peers
    data=search_peers(unknown,client=client)
    assert data["status"]=="NEEDS_BETTER_CHANNEL_FORMAT_EVIDENCE"
    assert client.calls==[]


def test_cli_snapshot_is_offline_and_saves_append_only_evidence(tmp_path):
    url="https://www.youtube.com/@OriginalSource/videos"
    data=snapshot([
        "Minecraft school animation full episode one",
        "Minecraft animated school classroom comedy episode two",
        "Minecraft school animation story three",
    ])
    snap=tmp_path/"public_catalogue.json"
    snap.write_text(data.model_dump_json(indent=2),encoding="utf8")
    output=tmp_path/"evidence"/"research_report.json"
    args=["channel-forensics","--channel-url",url,
          "--snapshot-json",str(snap),"--output-file",str(output)]
    res=CliRunner().invoke(app,args)
    assert res.exit_code==0,res.output[-1000:]
    info=json.loads(res.output)
    assert info["dominant_minor_niche"]=="minecraft_school_comedy"
    assert info["competitors_verified"] is False
    record=json.loads(output.read_text(encoding="utf8"))
    assert record["ingestion"]=="USER_SUPPLIED_UNTRUSTED_PUBLIC_METADATA_SNAPSHOT"
    assert record["need_independent_visual_video_review"] is True
    assert record["classification"]["search_plan"]["queries"]
    again=CliRunner().invoke(app,args)
    assert again.exit_code!=0


def test_repeated_generic_video_themes_refine_search_without_stealing_title():
    data=snapshot([
        "Minecraft school animation teacher solves a puzzle full movie",
        "Minecraft animated school comedy teacher helps the class",
        "Minecraft school animation teacher mystery new episode",
        "Minecraft animated classroom teacher drama cartoon",
    ])
    report=analyze_channel(data)
    assert "teacher" in report["recurring_generic_topic_signals"]
    searches=report["search_plan"]["queries"]
    assert len(searches)>=3
    assert searches[-1]["axis"]=="recurring_generic_theme"
    assert "teacher" in searches[-1]["query"]
    assert "solves a puzzle" not in searches[-1]["query"]
    assert "teacher helps the class" not in searches[-1]["query"]
    assert searches[0]["axis"]=="exact_format"


def test_mixed_channel_keeps_separate_format_search_plans_not_blended_keywords():
    data=snapshot([
        "Minecraft animated school teacher comedy film",
        "Minecraft school animation teacher funny story",
        "Minecraft survival gameplay 100 days",
        "Minecraft hardcore real player gameplay",
    ])
    profile=analyze_channel(data)
    assert profile["dominant_minor_niche"] is None
    school=profile["per_subniche_search_plans"]["minecraft_school_comedy"]
    survival=profile["per_subniche_search_plans"]["minecraft_recorded_survival"]
    assert school["queries"][0]["query"]!=survival["queries"][0]["query"]
    assert profile["search_plan"]["queries"]==[]


def test_real_youtube_watch_unavailable_falls_back_to_catalogue_without_fabricating_views():
    class PlaylistOnlyClient(StubFreeYoutubeClient):
        def read(self,argv,*,timeout):
            self.calls.append(argv)
            if "--flat-playlist" in argv:
                return "\n".join(json.dumps({
                    "id":vid(i),"playlist_channel_id":A,
                    "title":("Minecraft school animation teacher episode"
                             if i==1 else
                             "Minecraft animated school comedy episode"),
                    "duration":800,
                }) for i in (1,2))
            if "--dump-single-json" in argv:
                raise RuntimeError("This video is not available")
            raise AssertionError("unexpected operation")
    client=PlaylistOnlyClient()
    url="https://youtube.com/channel/"+A+"/videos"
    out=run_forensics(url,client=client,max_videos=2,search=False)
    assert out["watch_metadata_readback_complete"] is False
    assert out["playlist_only_video_count"]==2
    assert out["source_errors"]==[
        "WATCH_METADATA_UNAVAILABLE:"+vid(1)+":RuntimeError",
        "WATCH_METADATA_UNAVAILABLE:"+vid(2)+":RuntimeError",
    ]
    assert out["classification"]["dominant_minor_niche"]=="minecraft_school_comedy"
    assert out["classification"]["longform_nonlive_ids_matching_dominant_metadata"]==[]
    assert all(v["views"] is None and v["live_state"]=="UNKNOWN"
               and v["published_at"] is None for v in out["snapshot"]["videos"])
    assert out["need_independent_visual_video_review"] is True


def test_unknown_playlist_channel_identity_is_not_silently_accepted():
    class NoIdentityClient(StubFreeYoutubeClient):
        def read(self,argv,*,timeout):
            if "--flat-playlist" in argv:
                return "\n".join(json.dumps({
                    "id":vid(i),"title":"Minecraft school animation long episode"
                }) for i in (1,2))
            raise RuntimeError("Cannot fetch watch metadata")
    with pytest.raises(ValueError,match="INSUFFICIENT_CHANNEL_WATCH_METADATA"):
        collect_channel(URL,client=NoIdentityClient(),max_videos=2)


def test_live_video_is_excluded_from_longform_peers_even_if_archive_claims_not_live():
    livestream=sample(68,"Minecraft livestream real player gameplay",
                      channel=B,duration=7200,live="NOT_LIVE",views=2_000_000)
    x=compare_peer("minecraft_live_gameplay",livestream)
    assert x["same_subniche_and_media_lane_metadata"] is False
    assert x["rejected_reason"]=="LIVESTREAM_EXCLUDED_FROM_LONGFORM_PEER_RANKING"
    assert rank_peer_channels("minecraft_live_gameplay",[
        livestream,
        sample(69,"Minecraft live stream real gameplay",channel=B,
               duration=8000,live="NOT_LIVE"),
    ])["metadata_peer_channel_candidates"]==[]


def test_live_channel_uses_separate_peer_research_not_video_longform():
    from cinefactory.research_intelligence.channel_forensics_runner_v208 import search_peers
    live=snapshot([
        "Minecraft livestream survival real player",
        "Minecraft live stream real player gameplay",
        "Minecraft livestream interactive fans gameplay",
        "Minecraft live gameplay 100 days",
    ])
    report=analyze_channel(live)
    assert report["dominant_minor_niche"]=="minecraft_live_gameplay"
    client=StubFreeYoutubeClient()
    got=search_peers(report,client=client)
    assert got["status"]=="LIVESTREAM_NEEDS_SEPARATE_PEER_RESEARCH_NOT_LONGFORM"
    assert got["live_longform_breakout_excluded"] is True
    assert not client.calls


def test_two_video_catalogue_is_marked_small_sample_not_channel_certification():
    report=analyze_channel(snapshot([
        "3D nursery rhymes baby songs animation",
        "3D animated nursery rhyme kids songs",
    ]))
    assert report["sample_coverage_class"]=="SMALL_SAMPLE_2_TO_3_WEAK_EVIDENCE"
    assert report["dominant_minor_niche"]=="preschool_musical"
    assert report["high_confidence_semantic_fit"] is False
