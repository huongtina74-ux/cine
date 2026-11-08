#!/usr/bin/env python3
"""Bell & Leaf EP001 v2 story memory: structural continuity and repeated-incident guard.

This checks explicit writer-room episode memory. It does NOT prove semantic
originality, certify artistic quality, authenticate an owner's signoff, or
authorize image/video production.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "docs/story/bell_leaf/ep001_screenplay/EP001_STORY_V2_CONTINUITY_LOCK.json"
INDEX = ROOT / "docs/story/bell_leaf/EPISODE_STORY_MEMORY_INDEX_V1.json"
SCRIPT = ROOT / "docs/story/bell_leaf/ep001_screenplay/EP001_FULL_45MIN_SHOOTING_SCREENPLAY_DRAFT.md"
SCENE = re.compile(r"SC-\d{3}$")
EVENT = re.compile(r"^[a-z0-9][a-z0-9_]{10,100}$")
SHOOTING_SLOT = re.compile(r"^\*\*S(\d{3}) \[(\d\d:\d\d)–(\d\d:\d\d)\]\*\*")


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("Expected JSON object: " + str(path))
    return value


def validate_memory(memory: dict, index: dict, shooting_text: str) -> list[str]:
    problems = []
    if (memory.get("series_id"), memory.get("niche_id"), memory.get("episode_id")) != (
        "bell_leaf", "magical_witch_family_stories", "BL-0001"
    ):
        problems.append("WRONG_CANON_IDENTITY")
    if memory.get("source_basis", [None])[0] != "OWNER_FOUR_LOCKED_SOURCES_20261107":
        problems.append("OWNER_ORIGINAL_SOURCES_NOT_FIRST")
    if "PRODUCTION_APPROVAL" not in memory.get("authority", ""):
        problems.append("PRODUCTION_STATUS_MISSING_DISTINCTION")
    scenes = memory.get("scene_cards", [])
    if len(scenes) != 30:
        problems.append("NOT_30_SCENES")
    found_events = set()
    for ix, s in enumerate(scenes):
        if s.get("scene_id") != f"SC-{ix + 1:03d}" or not SCENE.fullmatch(s.get("scene_id", "")):
            problems.append("SCENE_ID_ORDER_" + str(ix))
        if (s.get("start_s"), s.get("end_s")) != (ix * 90, (ix + 1) * 90):
            problems.append("TIME_GAP_OR_OVERLAP_" + str(ix))
        if s.get("act") != (ix // 6) + 1:
            problems.append("WRONG_ACT_" + str(ix))
        if s.get("shot_slot_range") != [f"S{ix * 9 + 1:03d}", f"S{(ix + 1) * 9:03d}"]:
            problems.append("SHOT_RANGE_MISMATCH_" + str(ix))
        if not all(isinstance(s.get(k), str) and len(s[k]) >= (12 if k == "audience_question" else 35) for k in
                   ("story_detail_vi", "decision", "causal_outcome", "audience_question")):
            problems.append("UNDERDEVELOPED_SCENE_" + str(ix))
        if not isinstance(s.get("dialogue_draft_a2"), list) or not s["dialogue_draft_a2"]:
            problems.append("MISSING_A2_DIALOGUE_" + str(ix))
        ident = s.get("original_event_id", "")
        if ident in found_events or not EVENT.fullmatch(ident):
            problems.append("DUPLICATE_OR_INVALID_EVENT_" + str(ix))
        found_events.add(ident)
        if s.get("production_status") != "STORY_OUTLINE_ONLY_NOT_V2_SHOT_APPROVED":
            problems.append("INVALID_PRODUCTION_APPROVAL_" + str(ix))
    if memory.get("timing", {}).get("target_seconds") != 2700:
        problems.append("BAD_45_MIN_TARGET")
    if "same" not in memory.get("story_first_rule", "").lower():
        problems.append("MISSING_SAME_MORNING_LOCK")
    if "S001" not in shooting_text or "clink" not in shooting_text.casefold():
        problems.append("ORIGINAL_SHOT_SOURCE_DRIFT")
    index_items = index.get("plot_registry", [])
    if len(index_items) < 1 or index_items[0].get("episode_id") != "BL-0001":
        problems.append("EP001_MISSING_MEMORY_INDEX")
    elif set(index_items[0].get("locked_event_ids", [])) != found_events:
        problems.append("EP001_INDEX_EVENT_DRIFT")
    end = memory.get("state_at_end", {})
    for k,v in (("evan_aware_of_magic", False),
                ("paternal_grandparents_aware_of_magic", False),
                ("aila_sister_status", "MISSING_NOT_LOCATED"),
                ("elara_status", "MISSING_UNCONFIRMED"),
                ("bubu_unmapped_world_target", "ECHO_HEARD_SOURCE_UNCONFIRMED_NO_GATE_OPENED")):
        if end.get(k) != v:
            problems.append("POST_EP001_STATE_DRIFT_" + k.upper())
    if len(memory.get("motifs", [])) < 8 or len(memory.get("anti_repeat", {}).get("blacklist_reuse", [])) < 5:
        problems.append("INCOMPLETE_SEED_PAYOFF_OR_ANTI_REPEAT")
    if memory.get("assets", {}).get("aila_visual_approved") is not False:
        problems.append("INVENTED_AILA_ART_APPROVAL")
    if memory.get("assets", {}).get("aila_voice_approved") is not False:
        problems.append("INVENTED_AILA_VOICE_APPROVAL")
    return problems


def check_future_episode(memory: dict, candidate: dict) -> dict:
    """Fail closed on known repeats; always ask for independent semantic review."""
    blocked, review = [], []
    if candidate.get("series_id") != "bell_leaf" or candidate.get("niche_id") != "magical_witch_family_stories":
        blocked.append("WRONG_SERIES_OR_NICHE")
    episode_id = candidate.get("episode_id", "")
    if not re.fullmatch(r"BL-\d{4}", episode_id) or episode_id == "BL-0001":
        blocked.append("INVALID_FUTURE_EPISODE_ID")
    for key in ("title", "hook", "goal", "central_conflict", "resolution", "unique_difference"):
        if not isinstance(candidate.get(key), str) or len(candidate[key].strip()) < 25:
            blocked.append("MISSING_DEVELOPED_" + key.upper())
    events = candidate.get("claimed_new_event_ids")
    if not isinstance(events, list) or not all(isinstance(x,str) for x in events):
        blocked.append("MISSING_EXPLICIT_NEW_EVENT_IDS")
        events = []
    reserved = {s["original_event_id"] for s in memory["scene_cards"]}
    overlap = sorted(set(events) & reserved)
    if overlap:
        blocked.append("REPEATED_EP001_EVENT_AS_NEW:" + ",".join(overlap))
    if len(events) != len(set(events)):
        blocked.append("DUPLICATE_EVENTS_WITHIN_CANDIDATE")
    # A retrospective callback can cite an old event, but only with an
    # explicit category and a new consequence. Never mislabel old events as NEW.
    callbacks = candidate.get("callbacks_to_prior_episode", [])
    if not isinstance(callbacks, list):
        blocked.append("INVALID_CALLBACK_LIST")
        callbacks = []
    for cb in callbacks:
        if not isinstance(cb, dict) or cb.get("event_id") not in reserved or not cb.get("new_consequence"):
            blocked.append("INVALID_CALLBACK")
    existing_states = memory["state_at_end"]
    inherited = candidate.get("inherits_state", {})
    if not isinstance(inherited, dict):
        blocked.append("MISSING_INHERITED_STATE")
        inherited = {}
    for state_key in ("evan_aware_of_magic","elara_status","aila_sister_status","bubu_unmapped_world_target"):
        if state_key not in inherited:
            blocked.append("UNDECLARED_INHERITED_STATE:" + state_key)
        elif inherited[state_key] != existing_states[state_key]:
            blocked.append("CONFLICTS_WITH_EP001_END_STATE:" + state_key)
    # An old screenplay plot can progress but cannot be presented as the new premise.
    mechanism = str(candidate.get("central_mechanism_id", "")).casefold()
    solution = str(candidate.get("solution_mechanism_id", "")).casefold()
    if mechanism in ("copper_suitcase_station_afterpulse","aila_flying_copper_suitcase") and solution in (
        "wood_linen_two_pulse_suitcase","remove_copper_and_cover_with_linen"
    ):
        blocked.append("REUSED_EP001_COPPER_SUITCASE_CAUSE_AND_RESOLUTION")
    if episode_id == "BL-0003" and ("suitcase" in candidate.get("title","").lower() or "vali" in candidate.get("title","").lower()):
        review.append("BL-0003_ORIGINAL_SLATE_COLLISION_REQUIRES_NEW_CONFLICT")
    review.extend(["CROSSCHECK_1000_DRAFT_SLATE_SAME_NICHE",
                   "CROSSCHECK_FULL_PRIOR_SCREENPLAYS_AND_SCENE_CAUSALITY",
                   "INDEPENDENT_HUMAN_SEMANTIC_NOVELTY_AND_CANON_EDITOR"])
    return {"episode_id":episode_id,"status":"BLOCKED" if blocked else "MANUAL_NOVELTY_REVIEW_REQUIRED",
            "blocked":blocked,"review_required":review,
            "matching_existing_event_ids":overlap,
            "story_reference":"BL-0001/EP001_STORY_V2_CONTINUITY_LOCK.json",
            "editorial_approval":False,"production_authorized":False}


def cli(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["verify","check-candidate"])
    parser.add_argument("--candidate",type=Path)
    parser.add_argument("--out",type=Path)
    args = parser.parse_args(argv)
    memory=load_json(DATA)
    index=load_json(INDEX)
    issues=validate_memory(memory,index,SCRIPT.read_text(encoding="utf-8-sig"))
    if issues:
        report={"status":"BLOCKED_STORY_MEMORY_CORRUPT","issues":issues,"production_authorized":False}
    elif args.command=="verify":
        report={"status":"STORY_MEMORY_STRUCTURE_VERIFIED_EDITOR_REVIEW_REQUIRED","episode_id":"BL-0001",
                "scene_count":30,"shot_slots":270,"event_ids":len(index["plot_registry"][0]["locked_event_ids"]),
                "motif_chains":len(memory["motifs"]),"owner_approved_media":False,
                "editorial_approval":False,"production_authorized":False}
    elif not args.candidate:
        report={"status":"BLOCKED","issues":["CANDIDATE_ARGUMENT_REQUIRED"],"production_authorized":False}
    else:
        report=check_future_episode(memory,load_json(args.candidate))
    payload=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(payload,encoding="utf-8")
    print(payload)
    return 2 if report["status"].startswith("BLOCKED") else 0


if __name__ == "__main__":
    raise SystemExit(cli())
