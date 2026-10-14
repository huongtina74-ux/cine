"""v200: strict per-format competitor intelligence and false-assignment regression."""
from pathlib import Path
import datetime as dt
import pytest
from cinefactory.studio.niche_competitor_guard_v200 import (
    LANE_TO_NICHE,format_signals,validate_video_niche,
)
from cinefactory.studio.production_tool_catalog_v191 import NICHE_BLUEPRINTS
from cinefactory.studio.daily_youtube_breakout_v199 import (
    SEARCH_LANES,scan_daily,PublicVideo,UTC,
)

def test_all_13_production_blueprints_have_separate_format_lanes():
    assert set(LANE_TO_NICHE.values())==set(NICHE_BLUEPRINTS)
    assert set(LANE_TO_NICHE)==set(SEARCH_LANES)
    assert LANE_TO_NICHE["minecraft_gameplay"]==LANE_TO_NICHE["minecraft_animation"]=="minecraft"
    assert len(SEARCH_LANES)==14

@pytest.mark.parametrize("title,lane",[
    ("JJ and Mikey Survived 100 Days in an EXPANDING WORLD in Minecraft","minecraft_gameplay"),
    ("The love story of poor Steve and Sadako - Minecraft Animation","minecraft_animation"),
    ("Long Slide Game with Cow Elephant Gorilla Hippopotamus Tiger 3d Animal Game","long_slide_game"),
    ("Original 3D Nursery Rhymes for Kids Songs Animation","preschool_musical"),
    ("Roblox R6 Animation Adventure Story","roblox_animation"),
    ("3D Animated Animal Adventure Full Movie","animal_animation"),
    ("GTA V Gameplay Police Chase Challenge","gta_gameplay"),
    ("AI Cinematic Family Drama Original Story","ai_storytelling"),
    ("2D Cartoon Full Episode Family Adventures","cartoon_2d"),
    ("ASMR Sleep No Talking Hand Sounds 3 Hours","asmr_sleep"),
    ("Stories for Seniors: A Life Worth Living","audio_storytelling_seniors"),
    ("Rain Sounds for Sleep Thunderstorm 10 Hours","rain_sleep_white_noise"),
    ("Silent Fishing Session No Talking in the Rain","fishing_silent"),
    ("Daily English Listening and Conversation Practice","daily_english"),
])
def test_title_signals_only_match_correct_niche(title,lane):
    result=validate_video_niche(title,lane)
    assert result.status=="MATCHED_METADATA_FORMAT_CANDIDATE"
    assert result.niche_id==LANE_TO_NICHE[lane]
    assert not result.can_be_registered_as_verified_competitor
    assert not result.can_be_auto_promoted_to_production

@pytest.mark.parametrize("title,lane",[
    ("JJ and Mikey Survived 100 Days in Minecraft","minecraft_animation"),
    ("The love story of Steve and Sadako Minecraft Animation","minecraft_gameplay"),
    ("Long Slide Game with Cow Elephant 3d Animal Game","animal_animation"),
    ("Roblox Animation Story","minecraft_animation"),
    ("Minecraft Animation Tutorial for Beginners","minecraft_animation"),
    ("How to Make Minecraft Animation with Blender","minecraft_animation"),
    ("3D animal slide video gameplay","preschool_musical"),
    ("Funny animals video 2026","animal_animation"),
    ("New viral cartoon baby dance","preschool_musical"),
    ("Minecraft 100 Days Survival Minecraft Animation","minecraft_gameplay"),
    ("Rain Sleep ASMR with Tapping and Thunderstorm Sounds","asmr_sleep"),
])
def test_cross_format_or_unproven_video_is_quarantined(title,lane):
    result=validate_video_niche(title,lane)
    assert result.status!="MATCHED_METADATA_FORMAT_CANDIDATE"
    assert result.niche_id is None
    assert not result.can_be_registered_as_verified_competitor

def test_unknown_lanes_cannot_relabel_candidates():
    with pytest.raises(ValueError,match="NO_SIGNED_NICHE"):
        validate_video_niche("Minecraft 100 Days","emerging_animation")

def test_search_can_return_wrong_niche_but_ingestion_must_quarantine(tmp_path):
    class Fake:
        def search(self,_query,*,limit):
            return [{"id":"t5wy_OsuMvM","title":"Minecraft gameplay result"}]
        def video(self,vid,*,lane):
            return PublicVideo.parse({
                "id":vid,"title":"Minecraft Animation The Sadako Story",
                "upload_date":"20261008","duration":630,"view_count":800000,
                "channel_id":"UC"+"z"*22,"channel":"Foreign Format",
                "was_live":False,
            },lane)
    r=scan_daily(root=tmp_path,client=Fake(),
                 lanes=["minecraft_gameplay"],now=dt.datetime(
                     2026,10,9,10,tzinfo=UTC),max_metadata=1,search_per_lane=1)
    assert r["results_count"]==0
    assert r["cross_niche_quarantined_count"]==1
    assert r["cross_niche_quarantine"][0]["NOT_A_VERIFIED_SAME_NICHE_COMPETITOR"]
    assert r["ledger_stats"]["unique_videos"]==0
    assert r["ledger_stats"]["followed_competitor_channels"]==0

def test_verified_candidate_niche_label_and_doubt_boundary(tmp_path):
    class Fake:
        def search(self,_query,*,limit):
            return [{"id":"t5wy_OsuMvM"}]
        def video(self,vid,*,lane):
            return PublicVideo.parse({
                "id":vid,"title":"Minecraft 100 Days Hardcore Survival Challenge",
                "upload_date":"20261008","duration":630,"view_count":800000,
                "channel_id":"UC"+"z"*22,"channel":"Original Gameplay",
                "was_live":False,
            },lane)
    r=scan_daily(root=tmp_path,client=Fake(),
                 lanes=["minecraft_gameplay"],
                 now=dt.datetime(2026,10,9,10,tzinfo=UTC),
                 max_metadata=1,search_per_lane=1)
    assert r["results_count"]==1
    row=r["verified_candidates"][0]
    assert row["niche_id"]=="minecraft"
    assert row["format_id"]=="minecraft_gameplay"
    assert not row["competitor_same_niche_confirmed"]
    assert row["format_admission"]=="TITLE_ONLY_CANDIDATE_NOT_VISUAL_VERIFIED"
    assert r["cross_niche_quarantined_count"]==0
