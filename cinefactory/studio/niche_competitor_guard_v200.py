"""CineFactory v1.6.40 — fail-closed format-specific competitor evidence gate.

Each niche needs its own *format*, not merely matching YouTube search terms.
A video is not called a rival of a niche because it happened to appear in
its keyword search. Conservative title-only classification is a FIRST PASS
for R&D admission, NOT visual/audio/video understanding; uncertainty goes to
an explicitly separated quarantine, never to the niche playbook.

Some channels publish several formats; evaluate every VIDEO, not a permanent
one-channel-one-format assignment. Author's content cannot be re-used as
scripts, skins, voice, music or training data.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Literal
from .production_tool_catalog_v191 import NICHE_BLUEPRINTS

@dataclass(frozen=True)
class NicheVideoRouting:
    lane: str
    niche_id: str | None
    format_id: str | None
    status: Literal["MATCHED_METADATA_FORMAT_CANDIDATE",
                    "QUARANTINE_CROSS_NICHE_OR_AMBIGUOUS",
                    "QUARANTINE_NO_SUFFICIENT_FORMAT_EVIDENCE"]
    reason: str
    search_lane_is_not_format_proof: bool = True
    video_watched_in_full: bool = False
    audio_examined: bool = False
    can_be_registered_as_verified_competitor: bool = False
    can_be_auto_promoted_to_production: bool = False

# Minecraft split by actual on-screen format, not by generic keyword "Minecraft".
LANE_TO_NICHE={
    "minecraft_gameplay":"minecraft",
    "minecraft_animation":"minecraft",
    "preschool_musical":"preschool_3d_musical",
    "long_slide_game":"long_slices_game",
    "ai_storytelling":"ai_family_drama",
    "asmr_sleep":"asmr_sleep_hands_objects",
    "roblox_animation":"roblox_animation",
    "animal_animation":"animal_animation",
    "gta_gameplay":"gta_gameplay",
    "cartoon_2d":"2d_cartoon",
    "audio_storytelling_seniors":"audio_storytelling_seniors",
    "rain_sleep_white_noise":"rain_sleep_white_noise",
    "fishing_silent":"fishing_silent",
    "daily_english":"daily_english",
}
assert set(LANE_TO_NICHE.values())==set(NICHE_BLUEPRINTS)

EXPLICIT_TECH_TUTORIAL=re.compile(
    r"\b(how to|tutorial|guide to|course|review|blender tutorial|"
    r"how i made|making of|tips and tricks|software comparison)\b",re.I)

def _has(s:str,pattern:str)->bool:
    return re.search(pattern,s,re.I) is not None

def format_signals(title:str)->set[str]:
    s=" ".join(title.lower().replace("_"," ").split())
    if EXPLICIT_TECH_TUTORIAL.search(s):
        return set()
    hit=set()
    minecraft=_has(s,r"\bminecraft\b|\bsteve and sadako\b")
    if minecraft:
        if _has(s,r"\b(100 days|hardcore|surviv(ed|al)|gameplay|"
                     r"speedrun|minecraft challenge|let'?s play|manhunt|"
                     r"i spent [0-9]+ days|minecraft adventure|"
                     r"build battle|build challenge|noob vs pro|"
                     r"minecraft,?\s*but|security house|base battle)\b"):
            hit.add("minecraft_gameplay")
        if _has(s,r"\b(animation|animated|short film|movie|cinematic|"
                     r"love story|sadako|cartoon|film)\b"):
            hit.add("minecraft_animation")
    if _has(s,r"\broblox\b") and _has(s,r"\b(animation|animated|r6|r15|cartoon|film)\b"):
        hit.add("roblox_animation")
    if _has(s,r"\b(long slide|long slides|slide race|slide game|"
                  r"animal slide|mega slide|obstacle slide)\b") and _has(
                      s,r"\b(3d|animal|slide|race|game|obstacle)\b"):
        hit.add("long_slide_game")
    if _has(s,r"\b(nursery rhyme|nursery rhymes|kids songs|"
                  r"preschool song|baby songs|abc song|"
                  r"learning songs for kids)\b") and _has(
                      s,r"\b(3d|animated|animation|cartoon|kids|baby|nursery)\b"):
        hit.add("preschool_musical")
    if _has(s,r"\b(3d animal animation|animal animation movie|"
                  r"animated animal adventure|3d animal cartoon)\b") and "long_slide_game" not in hit:
        hit.add("animal_animation")
    if _has(s,r"\b(gta|grand theft auto)\b") and _has(
                      s,r"\b(gameplay|stunts|missions|racing|mod|"
                        r"challenge|police chase)\b"):
        hit.add("gta_gameplay")
    if _has(s,r"\b(ai (film|movie|drama|story)|ai-generated (film|movie)|"
                  r"animated family drama|cinematic family drama)\b"):
        hit.add("ai_storytelling")
    if _has(s,r"\b(2d animation|2d animated|2d cartoon)\b"):
        hit.add("cartoon_2d")
    if _has(s,r"\basmr\b") and _has(
        s,r"\b(sleep|relaxation|tapping|hand sounds|"
          r"hand triggers|no talking|triggers)\b"):
        hit.add("asmr_sleep")
    if _has(s,r"\b(stories for seniors|senior storytelling|"
                  r"bedtime stories for adults|audio story for elderly|"
                  r"senior life stories)\b"):
        hit.add("audio_storytelling_seniors")
    if _has(s,r"\b(rain sounds|rain ambience|white noise|"
                  r"thunderstorm sounds|rain for sleep)\b"):
        hit.add("rain_sleep_white_noise")
    if _has(s,r"\b(fishing|angling|catching fish)\b") and _has(
                      s,r"\b(silent|no talking|no commentary|"
                        r"fishing session|fishing adventure)\b"):
        hit.add("fishing_silent")
    if _has(s,r"\b(learn english|daily english|english listening|"
                  r"english conversation|english speaking practice)\b"):
        hit.add("daily_english")
    return hit

def validate_video_niche(title:str,lane:str)->NicheVideoRouting:
    if lane not in LANE_TO_NICHE:
        raise ValueError("NO_SIGNED_NICHE_FORMAT_BLUEPRINT")
    signals=format_signals(title)
    # A generic unspecified word in the query is not evidence.
    if not signals:
        return NicheVideoRouting(lane,None,None,
            "QUARANTINE_NO_SUFFICIENT_FORMAT_EVIDENCE",
            "TITLE_DOES_NOT_ESTABLISH_FORMAT_OR_IS_A_TUTORIAL")
    if signals!={lane}:
        return NicheVideoRouting(lane,None,None,
            "QUARANTINE_CROSS_NICHE_OR_AMBIGUOUS",
            "OBSERVED_TITLE_FORMATS:"+",".join(sorted(signals))+
            ";SEARCH_LANE:"+lane)
    return NicheVideoRouting(
        lane,LANE_TO_NICHE[lane],lane,
        "MATCHED_METADATA_FORMAT_CANDIDATE",
        "EXACT_SEARCH_LANE_AND_TITLE_FORMAT_SIGNAL_WITHOUT_MEDIA_REVIEW")

def channel_competitor_profile(lane:str)->dict:
    if lane not in LANE_TO_NICHE:
        raise ValueError("NO_SIGNED_NICHE_FORMAT_BLUEPRINT")
    return {
        "format_id":lane,"niche_id":LANE_TO_NICHE[lane],
        "is_per_video_not_permanent_channel_identity":True,
        "full_video_review_completed":False,
        "source_evidence_status":"PUBLIC_METADATA_AND_TITLE_CLASSIFICATION_ONLY",
        "producer_tools_verified":False,
    }
