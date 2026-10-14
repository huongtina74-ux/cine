"""Minecraft is a MARKET, not a single reusable production pipeline.

Hard boundaries: authored Blender stories != genuine game-runtime footage !=
unscripted live gameplay. Transfers require semantic/media compatibility.
No supplied video statistics are treated as verified merely because a flag
or title asserts that they are.
"""
from __future__ import annotations
from enum import StrEnum
from typing import Literal
from pydantic import BaseModel, Field

class Lane(StrEnum):
    FILM_ANIMATION = "FILM_ANIMATION"
    CAPTURED_GAMEPLAY = "CAPTURED_GAMEPLAY"
    LIVE_RUNTIME = "LIVE_RUNTIME"
    STAGED_GAME_MACHINIMA = "STAGED_GAME_MACHINIMA"

class Format(BaseModel):
    subniche_id: str
    production_lane: Lane
    audience_intent: str
    source_truth: str
    target_output: str = "LONG_FORM_8MIN_PLUS"
    evergreen_hypothesis: str
    required_executable: str
    research_status: Literal["HYPOTHESIS_NOT_CURRENTLY_VERIFIED"] = "HYPOTHESIS_NOT_CURRENTLY_VERIFIED"

CATALOG: dict[str,Format] = {
    "minecraft_story_adventure":Format(
        subniche_id="minecraft_story_adventure",production_lane=Lane.FILM_ANIMATION,
        audience_intent="original_character_driven_scripted_animation",
        source_truth="authored_original_3d_animation",
        evergreen_hypothesis="recurring original stories and emotional payoff",
        required_executable="BLENDER_3D_ANIMATION_WORKER"),
    "minecraft_school_comedy":Format(
        subniche_id="minecraft_school_comedy",production_lane=Lane.FILM_ANIMATION,
        audience_intent="original_character_driven_scripted_animation",
        source_truth="authored_original_3d_animation",
        evergreen_hypothesis="episodic ensemble comedy with character-driven arcs",
        required_executable="BLENDER_3D_ANIMATION_WORKER"),
    "minecraft_monster_fantasy":Format(
        subniche_id="minecraft_monster_fantasy",production_lane=Lane.FILM_ANIMATION,
        audience_intent="original_character_driven_scripted_animation",
        source_truth="authored_original_3d_animation",
        evergreen_hypothesis="original creature lore with serialized stories",
        required_executable="BLENDER_3D_ANIMATION_WORKER"),
    "minecraft_animated_challenge":Format(
        subniche_id="minecraft_animated_challenge",production_lane=Lane.FILM_ANIMATION,
        audience_intent="original_character_driven_scripted_animation",
        source_truth="authored_original_3d_animation",
        evergreen_hypothesis="comedy challenges executed as animation, not fake livestream",
        required_executable="BLENDER_3D_ANIMATION_WORKER"),
    "minecraft_recorded_survival":Format(
        subniche_id="minecraft_recorded_survival",production_lane=Lane.CAPTURED_GAMEPLAY,
        audience_intent="authentic_gameplay_progression",
        source_truth="owned_recording_of_real_game_session",
        evergreen_hypothesis="progression, constraints and player skill",
        required_executable="REAL_MINECRAFT_GAME_SESSION_CAPTURE"),
    "minecraft_gameplay_tutorial":Format(
        subniche_id="minecraft_gameplay_tutorial",production_lane=Lane.CAPTURED_GAMEPLAY,
        audience_intent="authentic_gameplay_guidance",
        source_truth="owned_recording_of_real_game_session",
        evergreen_hypothesis="searchable utility and updated gameplay mechanics",
        required_executable="REAL_MINECRAFT_GAME_SESSION_CAPTURE"),
    "minecraft_live_gameplay":Format(
        subniche_id="minecraft_live_gameplay",production_lane=Lane.LIVE_RUNTIME,
        audience_intent="live_interactive_player_session",
        source_truth="real_live_authenticated_game_runtime",
        target_output="LIVESTREAM_EXCLUDED_FROM_LONGFORM_BREAKOUT_RANKING",
        evergreen_hypothesis="realtime viewer interaction, separate from scripted story films",
        required_executable="REALTIME_GAME_AND_STREAM_CAPTURE"),
    "minecraft_scripted_machinima":Format(
        subniche_id="minecraft_scripted_machinima",production_lane=Lane.STAGED_GAME_MACHINIMA,
        audience_intent="scripted_story_shot_inside_game_runtime",
        source_truth="staged_capture_inside_actual_game_runtime",
        evergreen_hypothesis="cinematic story with actual game camera and staging",
        required_executable="QUALIFIED_GAME_RUNTIME_STAGE_AND_CAPTURE"),
}
# Maintains compatibility with the older v206 short name without inventing a
# second niche. It means *animated*, not captured survival gameplay.
ALIASES={"minecraft_challenge_survival":"minecraft_animated_challenge"}

class Route(BaseModel):
    market: Literal["minecraft"] = "minecraft"
    subniche_id: str | None = None
    production_lane: Lane | None = None
    confidence: Literal["EXPLICIT", "RULE_MATCH", "AMBIGUOUS", "UNKNOWN"]
    blocker: str | None = None
    acceptable_as_minecraft_story: bool = False
    live_views_excluded_from_rankings: bool = True

def canonical_subniche(text: str | None) -> str | None:
    if text is None:
        return None
    return ALIASES.get(text.strip().lower(),text.strip().lower())

def classify_minecraft(prompt: str, explicit_subniche: str | None = None) -> Route:
    if explicit_subniche:
        name=canonical_subniche(explicit_subniche)
        if name not in CATALOG:
            return Route(confidence="UNKNOWN",blocker="UNKNOWN_MINECRAFT_SUBNICHE")
        profile=CATALOG[name]
        text=prompt.lower()
        contradictory=(
            (profile.production_lane is Lane.FILM_ANIMATION and any(
                x in text for x in ("livestream","live stream","realtime livestream",
                                    "phát trực tiếp","người chơi thật đang live",
                                    "real gameplay","recorded gameplay",
                                    "quay màn hình game thật","người chơi đang chơi thật")))
            or (profile.production_lane in {Lane.LIVE_RUNTIME,Lane.CAPTURED_GAMEPLAY}
                and any(x in text for x in (
                    "blender animation","hoạt hình dựng","animated movie",
                    "fully animated story")))
        )
        if contradictory:
            return Route(subniche_id=name,production_lane=profile.production_lane,
                         confidence="AMBIGUOUS",blocker="EXPLICIT_FORMAT_CONTRADICTS_SOURCE_TRUTH")
        return Route(subniche_id=name,production_lane=profile.production_lane,
                     confidence="EXPLICIT",
                     acceptable_as_minecraft_story=profile.production_lane is Lane.FILM_ANIMATION)
    text=prompt.lower()
    live_terms=("livestream","live stream","streaming live","phát trực tiếp",
                "người chơi realtime","thời gian thực")
    capture_terms=("gameplay","playthrough","survival gameplay","real player",
                   "quay màn hình","chơi game thật","người chơi thật")
    animated_terms=("animation","animated","hoạt hình","blender",
                    "3d cinematic","animated story","phim 3d","phim hoạt hình")
    machinima_terms=("machinima","in-game scripted","inside minecraft runtime",
                     "quay trong game theo kịch bản")
    live=any(x in text for x in live_terms)
    capture=any(x in text for x in capture_terms)
    animated=any(x in text for x in animated_terms)
    machinima=any(x in text for x in machinima_terms)
    if (live and (animated or machinima)) or (capture and animated and not machinima):
        return Route(confidence="AMBIGUOUS",blocker="MIXED_MEDIA_PROVENANCE_REQUIRES_EXPLICIT_FORMAT")
    if live:
        chosen="minecraft_live_gameplay"
    elif machinima:
        chosen="minecraft_scripted_machinima"
    elif capture:
        chosen=("minecraft_gameplay_tutorial"
                if any(x in text for x in ("tutorial","guide","hướng dẫn","how to"))
                else "minecraft_recorded_survival")
    elif animated:
        chosen=("minecraft_school_comedy"
                if any(x in text for x in ("school","classroom","học đường","trường học"))
                else "minecraft_animated_challenge"
                if any(x in text for x in ("animated challenge","thử thách hoạt hình"))
                else "minecraft_monster_fantasy"
                if any(x in text for x in ("monster","creature","quái vật"))
                else "minecraft_story_adventure")
    else:
        return Route(confidence="UNKNOWN",blocker="MINECRAFT_VIDEO_PRODUCTION_FORMAT_NOT_SPECIFIED")
    return Route(subniche_id=chosen,production_lane=CATALOG[chosen].production_lane,
                 confidence="RULE_MATCH",
                 acceptable_as_minecraft_story=CATALOG[chosen].production_lane is Lane.FILM_ANIMATION)

def assess_transfer(source: str,target: str,pattern: str) -> dict:
    a,b=CATALOG[canonical_subniche(source)],CATALOG[canonical_subniche(target)]
    universal={"hook_structure","title_clarity","audience_question",
               "thumbnail_hypothesis","retention_measurement"}
    narrative={"story_structure","character_development","emotional_payoff"}
    technical={"rig","shot_camera","live_scene_capture","player_runtime","production_assets"}
    if pattern in technical:
        permitted=(a.production_lane==b.production_lane and
                   a.source_truth==b.source_truth)
    elif pattern in narrative:
        permitted=(a.production_lane==b.production_lane==Lane.FILM_ANIMATION
                   or {a.production_lane,b.production_lane} <=
                   {Lane.FILM_ANIMATION,Lane.STAGED_GAME_MACHINIMA})
    else:
        permitted=pattern in universal
    return {
        "source_subniche":a.subniche_id,"target_subniche":b.subniche_id,
        "pattern":pattern,"transferable_as_test_hypothesis":permitted,
        "copy_source_expression_allowed":False,
        "cross_format_metrics_do_not_prove_own_audience_fit":True,
        "requires_independent_validation":True,
    }

def compare_for_one_channel(a: str,b: str) -> dict:
    x,y=CATALOG[canonical_subniche(a)],CATALOG[canonical_subniche(b)]
    matching=(x.audience_intent==y.audience_intent and x.source_truth==y.source_truth
              and x.production_lane==y.production_lane)
    return {
        "can_share_channel_editorial_strategy": matching,
        "may_share_company_backoffice": True,
        "requires_distinct_production_lane":x.production_lane!=y.production_lane,
        "reason":("SAME_VIEWER_PROMISE_AND_MEDIA_SOURCE_FAMILY" if matching
                  else "DIFFERENT_VIEWER_PROMISE_OR_MEDIA_PROVENANCE"),
        "growth_claim_verified":False,
    }

def rank_subniche_research(records: list[dict]) -> dict:
    """Rank only source-attested independently reviewed evidence, never fabricate
    breakout/evergreen stats. Live formats excluded from long-form RPM research.
    """
    eligible=[]
    rejected=[]
    for row in records:
        name=canonical_subniche(row.get("subniche_id"))
        if name not in CATALOG:
            rejected.append({"subniche_id":name,"reason":"UNKNOWN_SUBNICHE"})
            continue
        profile=CATALOG[name]
        if profile.production_lane is Lane.LIVE_RUNTIME:
            rejected.append({"subniche_id":name,"reason":"LIVE_VIEWS_EXCLUDED"})
            continue
        if row.get("source_provenance")!="INDEPENDENTLY_REVIEWED_YOUTUBE_API_ARCHIVE":
            rejected.append({"subniche_id":name,"reason":"NO_INDEPENDENTLY_REVIEWED_PROVIDER_ARCHIVE"})
            continue
        if row.get("distinct_new_channel_1m_longform_14d",0)<2:
            rejected.append({"subniche_id":name,"reason":"TWO_LONGFORM_BREAKOUTS_NOT_ATTESTED"})
            continue
        if row.get("established_recent_100k_longform_evidence") is not True:
            rejected.append({"subniche_id":name,"reason":"EVERGREEN_DEMAND_NOT_ATTESTED"})
            continue
        if row.get("rights_risk_review")!="PASSED" or row.get("toolchain_reproducibility")!="PASSED":
            rejected.append({"subniche_id":name,"reason":"RIGHTS_OR_REPRODUCIBILITY_NOT_ATTESTED"})
            continue
        # Named, explainable editorial score; not predicted earnings/RPM.
        score=(40+min(20,int(row.get("verified_repeatable_examples",0))*4)
               +min(20,int(row.get("independent_recent_channels",0))*4)
               +min(20,int(row.get("verified_demand_stability_months",0))*2))
        eligible.append({"subniche_id":name,"score_for_editorial_research":score,
                         "decision":"HUMAN_REVIEW_REQUIRED_NOT_AUTOPRODUCTION",
                         "evidence_id":row.get("evidence_archive_id"),
                         "rpm_or_revenue_prediction":None})
    eligible.sort(key=lambda t:(-t["score_for_editorial_research"],t["subniche_id"]))
    # A caller-provided string saying "reviewed" cannot cryptographically
    # attest YouTube figures. Keep these only as tentative human research
    # candidates until the actual API archive is authenticated externally.
    return {"verified_research_shortlist":[],
            "provisional_research_shortlist":eligible,
            "rejected_or_unknown":rejected,
            "ranked_as_global_best":False,"must_crosscheck_actual_archive":True}
