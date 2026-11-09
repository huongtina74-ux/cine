"""Bell & Leaf owner-directed first-15-second hook, independent of media rendering."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("a2first15",ROOT/"tools/bell_leaf/opening_hook_gate.py")
hook_module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_module)


def get_plan():
    return json.loads((ROOT/"docs/story/bell_leaf/ep001_screenplay/EP001_STORY_QUALITY_PLAN_v2.json").read_text(encoding="utf-8"))


def test_ep001_actual_hook_0_to_15_structurally_valid():
    result=hook_module.inspect_hook(get_plan())
    assert result["blocking"] == []
    assert result["status"] == "STRUCTURAL_HOOK_PASS_EDITORIAL_PENDING"
    assert result["production_authorized"] is False


def test_every_episode_missing_opening_is_blocked():
    p=get_plan()
    p.pop("opening_hook")
    assert "FIRST_15S_HOOK_MISSING" in hook_module.inspect_hook(p)["blocking"]


def test_past_veylora_never_contains_unborn_children_or_evan():
    p=get_plan()
    p["opening_hook"]["shots"][0]["visible_tags"] += ["JUNO","EVAN","BUBU"]
    assert "FIRST_15S_PAST_CONTAINS_UNBORN_OR_EARTH_FAMILY" in hook_module.inspect_hook(p)["blocking"]


def test_hook_must_reinforce_by_second_15():
    p=get_plan()
    p["opening_hook"]["shots"][1]["reinforce_at_s"] = 16
    assert "FIRST_15S_REINFORCEMENT_AFTER_15_SECONDS" in hook_module.inspect_hook(p)["blocking"]


def test_one_exact_ten_second_shot_cannot_be_fifteen_seconds():
    p=get_plan()
    p["opening_hook"]["shots"][0]["end_s"] = 15
    assert "FIRST_15S_SHOT_0_NOT_FIXED_10S" in hook_module.inspect_hook(p)["blocking"]


def test_bell_leaf_hook_type_can_be_not_a_disaster():
    p=get_plan()
    h=p["opening_hook"]
    h["hook_type"]="EMOTIONAL_CHOICE"
    h["shots"][0]["timeline"]="EARTH_PRESENT"
    h["shots"][0]["location_tag"]="@BELL_KITCHEN_DAY"
    h["shots"][0]["visible_tags"]=["MARA","LIA"]
    assert hook_module.inspect_hook(p)["blocking"] == []


def test_no_fake_editor_signoff_or_unsupported_payout():
    p=get_plan()
    p["opening_hook"]["editorial_status"]="APPROVED"
    p["opening_hook"]["payoff_scene_id"]="SC-999"
    errs=hook_module.inspect_hook(p)["blocking"]
    assert "FIRST_15S_CANNOT_FAKE_EDITORIAL_APPROVAL" in errs
    assert "FIRST_15S_PAYOFF_SCENE_NOT_IN_EPISODE" in errs


def test_hook_not_repeated_and_shot_asset_cast_now_consistent():
    p=get_plan()
    assert p["target_minutes"]==45
    shots=p["opening_hook"]["shots"]
    assert [s["shot_id"] for s in shots] == ["S001","S002"]
    assert shots[0]["visible_tags"]==["MARA","ORIN"]
    assert shots[1]["visible_tags"]==["MARA","BIX"]
    bindings=json.loads((ROOT/"docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json").read_text(encoding="utf-8"))
    assert len(bindings["shots"])==270
    s1,s2=bindings["shots"][:2]
    assert s1["active_character_tags_candidate"]==shots[0]["visible_tags"]
    assert s2["active_character_tags_candidate"]==shots[1]["visible_tags"]
    assert s1["owner_location_plate_path"] is None
    assert s1["location_evidence_status"]=="MISSING_VEYLORA_HISTORICAL_STATION_OWNER_PLATE"
    assert s2["location_anchor_id"]=="BELL_KITCHEN_DAY"


def test_bell_leaf_only_profile_not_other_niches():
    cfg=json.loads((ROOT/"config/story_factory/story_quality_profiles_v1.json").read_text(encoding="utf-8"))
    assert cfg["niches"]["magical_witch_family_stories"]["opening_hook_policy"]["mandatory_for_every_episode"]
    assert "opening_hook_policy" not in cfg["niches"]["slow_english_a2_story"]
