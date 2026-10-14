"""Channel-first YouTube format forensics and peer-search design, v208.

Per-video signals precede channel-level positioning. Public titles and metadata
are NOT video playback or production provenance. Strictly match subniche and
media lane before competitor evidence is admitted. No copyright content copied.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .minecraft_subniche_v207 import CATALOG as MC_FORMATS, Lane
from .niche_competitor_guard_v200 import LANE_TO_NICHE, format_signals

CID = re.compile(r"^UC[A-Za-z0-9_-]{22}$")
VID = re.compile(r"^[A-Za-z0-9_-]{11}$")
MAX_VIDEOS = 24

class Sample(BaseModel):
    video_id: str
    channel_id: str | None = None
    title: str = Field(min_length=1,max_length=450)
    description: str = Field(default="",max_length=2000)
    published_at: str | None = None
    duration_seconds: int | None = Field(default=None,ge=0)
    views: int | None = Field(default=None,ge=0)
    live_state: Literal["LIVE","PAST_LIVE","UPCOMING","NOT_LIVE","UNKNOWN"] = "UNKNOWN"
    source: str = "PUBLIC_METADATA_ONLY"

    @model_validator(mode="after")
    def valid_ids(self):
        if not VID.fullmatch(self.video_id):
            raise ValueError("INVALID_YOUTUBE_VIDEO_ID")
        if self.channel_id is not None and not CID.fullmatch(self.channel_id):
            raise ValueError("INVALID_YOUTUBE_CHANNEL_ID")
        return self


class ChannelSample(BaseModel):
    channel_id: str | None = None
    submitted_url: str
    display_name: str | None = None
    videos: list[Sample] = Field(min_length=1,max_length=MAX_VIDEOS)
    collected_at: str
    source: str = "PUBLIC_YOUTUBE_METADATA_SNAPSHOT"

    @model_validator(mode="after")
    def valid_channel(self):
        if self.channel_id is not None and not CID.fullmatch(self.channel_id):
            raise ValueError("INVALID_CHANNEL_ID")
        identities=[x.video_id for x in self.videos]
        if len(identities)!=len(set(identities)):
            raise ValueError("DUPLICATE_VIDEO_IN_CATALOG")
        if self.channel_id and any(
            v.channel_id and v.channel_id!=self.channel_id for v in self.videos
        ):
            raise ValueError("OTHER_CHANNEL_VIDEO_IN_SOURCE_CATALOG")
        dt=datetime.fromisoformat(self.collected_at.replace("Z","+00:00"))
        if dt.tzinfo is None:
            raise ValueError("COLLECTION_TIME_MUST_INCLUDE_TIMEZONE")
        return self


class VideoFinding(BaseModel):
    video_id: str
    major_niche: str | None = None
    minor_niche: str | None = None
    media_lane: str | None = None
    status: Literal["METADATA_MATCH_CANDIDATE","AMBIGUOUS","UNKNOWN","EXCLUDED_LIVE"]
    reason: str
    actual_visual_reviewed: bool = False
    production_tools_verified: bool = False
    safe_as_competitor_evidence: bool = False


def _has(text: str, *terms: str) -> bool:
    return any(phrase in text for phrase in terms)


def classify_video(v: Sample) -> VideoFinding:
    """Title-first conservative evidence: never call a title a watched video."""
    s=" ".join(v.title.casefold().replace("_"," ").split())
    if not s:
        return VideoFinding(video_id=v.video_id,status="UNKNOWN",reason="MISSING_TITLE")
    minecraft=bool(re.search(r"\bminecraft\b",s))
    if minecraft:
        animated=_has(s,"animation","animated","blender","cartoon")
        live=_has(s,"livestream","live stream","streaming live","live gameplay")
        recorded=_has(s,"gameplay","playthrough","let's play","100 days",
                      "hardcore survival","speedrun","real player")
        machinima=_has(s,"machinima","staged inside minecraft","in-game short film")
        # Audience proof is false if a scheduled/past/live broadcast is treated
        # as ordinary produced 8+ minute YouTube long-form.
        if v.live_state in {"LIVE","PAST_LIVE","UPCOMING"}:
            return VideoFinding(video_id=v.video_id,major_niche="minecraft",
                minor_niche="minecraft_live_gameplay",
                media_lane=Lane.LIVE_RUNTIME,
                status="EXCLUDED_LIVE",reason="LIVE_SOURCE_NOT_LONGFORM_FILM")
        if sum((animated,live or recorded,machinima))>1:
            return VideoFinding(video_id=v.video_id,major_niche="minecraft",
                status="AMBIGUOUS",reason="MIXED_ANIMATION_GAMEPLAY_SOURCE_SIGNALS")
        if live:
            minor="minecraft_live_gameplay"
        elif machinima:
            minor="minecraft_scripted_machinima"
        elif recorded:
            minor=("minecraft_gameplay_tutorial"
                   if _has(s,"tutorial","how to","guide","explained") else
                   "minecraft_recorded_survival")
        elif animated:
            minor=("minecraft_school_comedy"
                   if _has(s,"school","classroom","school life","class teacher") else
                   "minecraft_monster_fantasy"
                   if _has(s,"monster","creature","zombie monster") else
                   "minecraft_animated_challenge"
                   if _has(s,"challenge","100 days animated","survival animation") else
                   "minecraft_story_adventure")
        else:
            return VideoFinding(video_id=v.video_id,major_niche="minecraft",
                status="AMBIGUOUS",
                reason="TITLE_MENTIONS_MINECRAFT_WITHOUT_SOURCE_FORMAT_PROOF")
        route=MC_FORMATS[minor]
        return VideoFinding(
            video_id=v.video_id,major_niche="minecraft",minor_niche=minor,
            media_lane=route.production_lane,status="METADATA_MATCH_CANDIDATE",
            reason="TITLE_SOURCE_FORMAT_SIGNAL_NOT_FULL_MEDIA_REVIEW")
    other=format_signals(v.title)
    if len(other)!=1:
        return VideoFinding(
            video_id=v.video_id,status="AMBIGUOUS" if other else "UNKNOWN",
            reason="NON_MINECRAFT_TITLE_HAS_MULTIPLE_OR_NO_FORMAT_SIGNALS",
        )
    minor=next(iter(other))
    major=LANE_TO_NICHE[minor]
    if v.live_state in {"LIVE","PAST_LIVE","UPCOMING"}:
        return VideoFinding(video_id=v.video_id,major_niche=major,
            minor_niche=minor,status="EXCLUDED_LIVE",
            reason="RECORDED_LIVE_NOT_ELIGIBLE_FOR_LONGFORM_PEER_COMPARISON")
    return VideoFinding(
        video_id=v.video_id,major_niche=major,minor_niche=minor,
        media_lane=(
            "ANIMATED_MEDIA" if minor in {"roblox_animation","preschool_musical",
            "cartoon_2d","animal_animation","long_slide_game"} else
            "OWNED_SOURCE_MEDIA_REQUIRED"
        ),
        status="METADATA_MATCH_CANDIDATE",
        reason="TITLE_FORMAT_SIGNAL_NOT_FULL_VIDEO_VERIFICATION",
    )


# Every search axis includes actual production grammar; never generic "Minecraft".
# Terms are SEARCH HYPOTHESES only; relevance is independently rechecked.
SEARCH_GRAMMAR={
    "minecraft_story_adventure":(
        "Minecraft animated story full episode",
        "Minecraft animation adventure movie long",
        "original Minecraft character animated story",
        "Minecraft animation narrative episodes",
    ),
    "minecraft_school_comedy":(
        "Minecraft school animation full episode",
        "Minecraft classroom animated comedy story",
        "Minecraft animated high school story long",
        "Minecraft school cartoon series episodes",
    ),
    "minecraft_monster_fantasy":(
        "Minecraft monster animation long movie",
        "Minecraft fantasy cartoon story full episode",
        "Minecraft monster animated adventure story",
    ),
    "minecraft_animated_challenge":(
        "Minecraft animated challenge full episode",
        "Minecraft animation survival story challenge",
        "Minecraft cartoon funny challenge movie",
    ),
    "minecraft_recorded_survival":(
        "Minecraft survival gameplay full episode",
        "Minecraft 100 days hardcore gameplay video",
        "Minecraft real player survival challenge",
    ),
    "minecraft_gameplay_tutorial":(
        "Minecraft survival tutorial gameplay long",
        "Minecraft building guide recorded gameplay",
        "Minecraft technical farm guide walkthrough",
    ),
    "minecraft_live_gameplay":(
        "Minecraft live gameplay interactive stream",
        "Minecraft real player livestream survival",
    ),
    "minecraft_scripted_machinima":(
        "Minecraft machinima movie in game",
        "Minecraft scripted cinematic in game recording",
    ),
    "long_slide_game":(
        "3D animal long slide obstacle race full episode",
        "animal mega slide game 3d long videos",
        "long slide animal 3d obstacle animation",
    ),
    "asmr_sleep":(
        "ASMR hand sounds sleep long video",
        "ASMR hand triggers no talking full session",
        "ASMR tapping fingers sleep sounds long form",
    ),
    "rain_sleep_white_noise":(
        "rain sounds sleep 3 hours white noise",
        "original rain ambience long video no talking",
        "heavy rain sounds black screen sleep",
    ),
    "fishing_silent":(
        "silent fishing no talking full trip",
        "natural fishing ambience full session no talking",
        "peaceful fishing no commentary long video",
    ),
    "audio_storytelling_seniors":(
        "life stories for seniors narrated full story",
        "senior bedtime audio storytelling long",
        "elderly life story audio narrative English",
    ),
    "preschool_musical":(
        "3D animated nursery rhyme full songs",
        "kids preschool original animation songs compilation",
        "3D cartoon nursery rhymes long video",
    ),
    "roblox_animation":(
        "Roblox R6 animation full movie",
        "Roblox animated story full episode",
        "Roblox cinematic cartoon adventure long",
    ),
    "gta_gameplay":(
        "GTA V real gameplay challenge full",
        "GTA 5 modded gameplay long video",
        "GTA V stunt race gameplay episode",
    ),
    "daily_english":(
        "daily English listening long conversation",
        "English speaking practice long dialogue",
        "learn English listening comprehension 30 minutes",
    ),
}
SEARCH_KEYWORD_SOURCE="CURATED_FORMAT_ONTOLOGY_NOT_VERIFIED_VIDEO_TRAFFIC"
# These are general storytelling/topic labels, not channel names or copied
# titles. A motif must recur across >=2 sampled same-format videos.
ALLOWED_RECURRING_THEMES={
    "teacher","classroom","school","rescue","escape","mystery","monster",
    "zombie","village","family","friends","challenge","survival","building",
    "race","competition","adventure","animals","sleep","tapping",
    "rain","thunderstorm","fishing","story","lesson","puzzle",
}

def recurring_themes(videos: list[Sample],findings: list[VideoFinding],
                     minor_niche: str | None) -> list[str]:
    if not minor_niche:
        return []
    counts=Counter()
    for video,found in zip(videos,findings):
        if found.minor_niche!=minor_niche or found.status!="METADATA_MATCH_CANDIDATE":
            continue
        words=set(re.findall(r"[a-z]+",video.title.casefold()))
        for token in words & ALLOWED_RECURRING_THEMES:
            counts[token]+=1
    return [word for word,count in sorted(counts.items(),
            key=lambda row:(-row[1],row[0])) if count>=2][:3]


def plan_queries(minor_niche: str, budget: int = 4,
                 recurring_topic_terms: list[str] | None = None) -> dict:
    if not 1<=budget<=6:
        raise ValueError("QUERY_BUDGET_OUT_OF_RANGE")
    if minor_niche not in SEARCH_GRAMMAR:
        return {"state":"UNCLASSIFIED_NO_FORMAT_SAFE_QUERIES",
                "queries":[],"minor_niche":minor_niche}
    questions=[
        {"axis":axis,"query":q,"provenance":SEARCH_KEYWORD_SOURCE}
        for axis,q in zip(
            ("exact_format","adjacent_synonym","audience_job","format_variation"),
            SEARCH_GRAMMAR[minor_niche][:budget])
    ]
    generic_topics=[
        x for x in (recurring_topic_terms or [])
        if x in ALLOWED_RECURRING_THEMES
    ]
    if questions and generic_topics:
        # Preserve at least 2 highly precise format queries before thematic
        # expansion. Only add safe recurring generic motifs, never copied
        # reference titles or channel/actor names.
        theme=generic_topics[0]
        base=SEARCH_GRAMMAR[minor_niche][0]
        candidate=(base+" "+theme)[:140]
        if len(questions)>=3:
            questions[-1]={
                "axis":"recurring_generic_theme","query":candidate,
                "provenance":"GENERIC_RECURRING_MOTIF_IN_SAME_FORMAT_VIDEO_TITLES",
            }
    return {
        "state":"READY_FOR_BOUNDED_PUBLIC_DISCOVERY",
        "minor_niche":minor_niche,
        "queries":questions,
        "discovery_not_exhaustive":True,
        "paid_api_calls_required":False,
        "video_fit_requires_recheck":True,
    }


def analyze_channel(sample: ChannelSample) -> dict:
    findings=[classify_video(video) for video in sample.videos]
    matched=[x for x in findings if x.status=="METADATA_MATCH_CANDIDATE"]
    by_minor=Counter(x.minor_niche for x in matched)
    by_market=Counter(x.major_niche for x in matched)
    total=len(sample.videos)
    first=by_minor.most_common(1)[0] if by_minor else None
    dominant=(first[0] if first and first[1]>=2 and
              first[1]/total>=0.60 else None)
    major=by_market.most_common(1)[0][0] if by_market else None
    # Mixed content must not be collapsed into a single channel-wide label.
    if not matched:
        status="UNKNOWN_NOT_ENOUGH_FORMAT_EVIDENCE"
    elif dominant:
        status="DOMINANT_METADATA_FORMAT_CANDIDATE"
    else:
        status="MIXED_OR_INSUFFICIENT_SAMPLE"
    good_long=[v.video_id for v,x in zip(sample.videos,findings)
               if x.minor_niche==dominant and
               x.status=="METADATA_MATCH_CANDIDATE"
               and v.live_state=="NOT_LIVE" and
               v.duration_seconds is not None and
               v.duration_seconds>=480]
    topics=recurring_themes(sample.videos,findings,dominant)
    characteristics=(
        {
            "audience_intent":MC_FORMATS[dominant].audience_intent,
            "candidate_source_truth":MC_FORMATS[dominant].source_truth,
            "likely_production_lane":MC_FORMATS[dominant].production_lane.value,
            "production_hypothesis_not_tool_verification":MC_FORMATS[dominant].required_executable,
            "evergreen_demand_hypothesis":MC_FORMATS[dominant].evergreen_hypothesis,
        }
        if dominant in MC_FORMATS else
        {"audience_intent":"TO_BE_REVIEWED_FROM_ACTUAL_VIDEO",
         "candidate_source_truth":"METADATA_ONLY_NOT_VALIDATED",
         "likely_production_lane":"NOT_INDEPENDENTLY_VERIFIED"}
    )
    return {
        "schema":"cine.research.channel_forensics.v208",
        "source_channel_id":sample.channel_id,
        "submitted_url":sample.submitted_url,
        "source_snapshot_timestamp":sample.collected_at,
        "sample_size":total,
        "market_major_niche":major,
        "dominant_minor_niche":dominant,
        "status":status,
        "dominant_share_of_sample":round(first[1]/total,3) if first else 0,
        "sample_coverage_class":(
            "SMALL_SAMPLE_2_TO_3_WEAK_EVIDENCE" if total<4 else
            "BOUNDED_RECENT_UPLOAD_SAMPLE_NOT_COMPLETE_CATALOG"
        ),
        "longform_duration_known_count":sum(
            v.duration_seconds is not None and v.duration_seconds>=480
            for v in sample.videos
        ),
        "views_observed_count":sum(v.views is not None for v in sample.videos),
        "nonlive_proven_count":sum(v.live_state=="NOT_LIVE" for v in sample.videos),
        "minor_niche_counts":dict(by_minor),
        "format_characteristics":characteristics,
        "recurring_generic_topic_signals":topics,
        "per_subniche_search_plans":{
            name:plan_queries(
                name,recurring_topic_terms=recurring_themes(sample.videos,findings,name)
            )
            for name,count in by_minor.most_common()
        },
        "per_video":[x.model_dump() for x in findings],
        "longform_nonlive_ids_matching_dominant_metadata":good_long,
        "search_plan":plan_queries(
            dominant,recurring_topic_terms=topics
        ) if dominant else {
            "state":"BLOCKED_UNTIL_HUMAN_FORMAT_TRIAGE","queries":[],
        },
        "video_playback_performed":False,
        "production_stack_verified":False,
        "channel_age_or_monetization_verified":False,
        "high_confidence_semantic_fit":False,
        "business_viability_proven":False,
    }


def compare_peer(reference_minor: str, video: Sample,
                 finding: VideoFinding | None = None) -> dict:
    """Strict matching for peers; possible format cousins stay outside matches."""
    finding=finding or classify_video(video)
    if reference_minor not in SEARCH_GRAMMAR:
        raise ValueError("UNKNOWN_PEER_SEARCH_TARGET")
    source_lane=(MC_FORMATS[reference_minor].production_lane
                 if reference_minor in MC_FORMATS else None)
    reason=None
    if reference_minor=="minecraft_live_gameplay":
        reason="LIVESTREAM_EXCLUDED_FROM_LONGFORM_PEER_RANKING"
    elif finding.minor_niche!=reference_minor:
        reason="DIFFERENT_MINOR_NICHE_OR_UNCLASSIFIED"
    elif finding.status!="METADATA_MATCH_CANDIDATE":
        reason="AMBIGUOUS_OR_LIVE_VIDEO"
    elif source_lane is not None and finding.media_lane!=source_lane:
        reason="PRODUCTION_LANE_MISMATCH"
    elif video.live_state!="NOT_LIVE":
        reason="SOURCE_IS_LIVE_OR_LIVE_STATUS_UNKNOWN"
    elif video.duration_seconds is None or video.duration_seconds<480:
        reason="NOT_VERIFIED_EIGHT_MINUTE_LONGFORM"
    return {
        "video_id":video.video_id,
        "channel_id":video.channel_id,
        "candidate_minor_niche":finding.minor_niche,
        "same_subniche_and_media_lane_metadata":reason is None,
        "rejected_reason":reason,
        "actual_video_content_verified":False,
        "source_is_metadata_only":True,
    }


def rank_peer_channels(target_minor: str, videos: list[Sample]) -> dict:
    """Two distinct matching long videos, not a keyword hit, for a peer candidate."""
    matched=defaultdict(set)
    errors=[]
    seen=set()
    for video in videos:
        if video.video_id in seen:
            continue
        seen.add(video.video_id)
        result=compare_peer(target_minor,video)
        if result["same_subniche_and_media_lane_metadata"] and video.channel_id:
            matched[video.channel_id].add(video.video_id)
        else:
            errors.append({"video_id":video.video_id,"reason":
                           result["rejected_reason"] or "CHANNEL_ID_UNVERIFIED"})
    qualified=[{
        "channel_id":channel,"matching_sampled_longform_ids":sorted(ids),
        "matching_count":len(ids),
        "status":"TWO_METADATA_MATCHES_NEED_INDEPENDENT_VIDEO_REVIEW",
        "video_watched":False,
    } for channel,ids in matched.items() if len(ids)>=2]
    qualified.sort(key=lambda x:(-x["matching_count"],x["channel_id"]))
    return {
        "target_minor_niche":target_minor,
        "metadata_peer_channel_candidates":qualified,
        "single_video_matches_unconfirmed":sorted(
            [{"channel_id":cid,"video_id":next(iter(ids))}
             for cid,ids in matched.items() if len(ids)==1],
            key=lambda x:x["channel_id"]),
        "rejected_video_matches":errors,
        "verified_competitors":[],
        "peer_discovery_is_exhaustive":False,
        "independent_video_review_required":True,
    }
