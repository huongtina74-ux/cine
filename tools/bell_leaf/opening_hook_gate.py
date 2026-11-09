#!/usr/bin/env python3
"""Bell & Leaf opening-hook policy: first 15s must earn attention, never break Canon.

A2 family animation uses fixed 10.0-second shots. The first 15 seconds span
all of shot S001 and the first five seconds of S002. Structural gates cannot
measure human engagement, which requires audience data and editorial viewing.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HOOK_TYPES = {
    "DISASTER_TEASER", "MYSTERY", "EMOTIONAL_CHOICE", "VISUAL_SURPRISE",
    "COMEDIC_PROBLEM", "URGENT_PROMISE", "UNEXPECTED_WORLD_RULE",
}
PAST_EXCLUDED = {
    "EVAN", "JUNO", "LIA", "BIX", "BUBU",
    "GRANDPA_EARTH", "GRANDMA_EARTH",
}
ALLOWED_TIMELINES = {"VEYLORA_PAST", "EARTH_PRESENT", "OTHER_WORLD", "UNKNOWN"}
SHOT_RE = re.compile(r"^S\d{3,4}$")
SCENE_RE = re.compile(r"^SC-\d{3,4}$")


def inspect_hook(plan: dict) -> dict:
    """Deterministic preflight. Never returns artistic PASS or publication approval."""
    errors = []
    hook = plan.get("opening_hook")
    if not isinstance(hook, dict):
        return {"status": "BLOCKED", "blocking": ["FIRST_15S_HOOK_MISSING"],
                "editorial_review_required": True, "production_authorized": False}
    if hook.get("schema") != "cine.bell_leaf.opening_hook.v1":
        errors.append("FIRST_15S_HOOK_SCHEMA_INVALID")
    if hook.get("hook_type") not in HOOK_TYPES:
        errors.append("FIRST_15S_HOOK_TYPE_INVALID")
    if hook.get("target_window_seconds") != 15 or hook.get("fixed_shot_seconds") != 10:
        errors.append("FIRST_15S_SHOT_TIMING_POLICY_VIOLATED")
    if hook.get("editorial_status") != "PENDING_INDEPENDENT_REVIEW":
        errors.append("FIRST_15S_CANNOT_FAKE_EDITORIAL_APPROVAL")
    for key in ("viewer_question", "episode_relevance", "truthful_payoff"):
        value = hook.get(key)
        if not isinstance(value, str) or len(value.strip()) < 30:
            errors.append("FIRST_15S_MISSING_" + key.upper())
    scenes = {s.get("scene_id") for s in plan.get("scenes", []) if isinstance(s, dict)}
    if hook.get("payoff_scene_id") not in scenes:
        errors.append("FIRST_15S_PAYOFF_SCENE_NOT_IN_EPISODE")
    slots = hook.get("shots")
    if not isinstance(slots, list) or len(slots) != 2:
        errors.append("FIRST_15S_REQUIRES_TWO_10S_SHOT_PLANS")
        slots = []
    required_shots = (("S001", 0, 10), ("S002", 10, 20))
    for index, shot in enumerate(slots):
        if not isinstance(shot, dict):
            errors.append(f"FIRST_15S_SHOT_{index}_INVALID")
            continue
        if index >= len(required_shots):
            break
        id_, start, end = required_shots[index]
        if (shot.get("shot_id"), shot.get("start_s"), shot.get("end_s")) != (id_, start, end):
            errors.append(f"FIRST_15S_SHOT_{index}_NOT_FIXED_10S")
        tags = shot.get("visible_tags")
        if (not isinstance(tags, list) or len(tags) != len(set(tags)) or
                not all(isinstance(t, str) and t.strip() for t in tags)):
            errors.append(f"FIRST_15S_SHOT_{index}_INVALID_ACTIVE_TAGS")
            tags = []
        timeline = shot.get("timeline")
        if timeline not in ALLOWED_TIMELINES:
            errors.append(f"FIRST_15S_SHOT_{index}_BAD_TIMELINE")
        if timeline == "VEYLORA_PAST" and (set(tags) & PAST_EXCLUDED):
            errors.append("FIRST_15S_PAST_CONTAINS_UNBORN_OR_EARTH_FAMILY")
        if not isinstance(shot.get("physical_action"), str) or len(shot["physical_action"].strip()) < 40:
            errors.append(f"FIRST_15S_SHOT_{index}_NOT_VISUALLY_ACTIONABLE")
        spoken = shot.get("dialogue_en_a2", "")
        if not isinstance(spoken, str) or len(spoken.split()) > 18:
            errors.append(f"FIRST_15S_SHOT_{index}_TOO_MUCH_A2_DIALOGUE")
        if not isinstance(shot.get("location_tag"), str) or not shot["location_tag"].startswith("@"):
            errors.append(f"FIRST_15S_SHOT_{index}_LOCATION_TAG_MISSING")
    if len(slots) == 2:
        one = slots[0].get("trigger_at_s")
        two = slots[1].get("reinforce_at_s")
        if not isinstance(one, (int, float)) or isinstance(one, bool) or not 0 <= one < 10:
            errors.append("FIRST_15S_NO_REAL_EVENT_IN_FIRST_SHOT")
        if not isinstance(two, (int, float)) or isinstance(two, bool) or not 10 <= two <= 15:
            errors.append("FIRST_15S_REINFORCEMENT_AFTER_15_SECONDS")
    if hook.get("only_reuses_existing_slots") is not True:
        errors.append("FIRST_15S_MUST_PRESERVE_EXISTING_EPISODE_DURATION")
    return {"status": "BLOCKED" if errors else "STRUCTURAL_HOOK_PASS_EDITORIAL_PENDING",
            "blocking": sorted(set(errors)),
            "production_authorized": False,
            "editorial_review_required": True,
            "note": "No hook can guarantee retention; judge the real first 30s after publication."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = inspect_hook(json.loads(args.plan.read_text(encoding="utf-8-sig")))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result["blocking"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
