"""BL-0001 v2 continuity memory and anti-repeat regression tests."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"tools/bell_leaf/ep001_story_memory_gate.py"
spec=importlib.util.spec_from_file_location("ep001_story_memory_gate",SRC)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def memory():
    return mod.load_json(mod.DATA)


def test_30_scene_canon_and_reference_integrity():
    assert not mod.validate_memory(memory(),mod.load_json(mod.INDEX),
       mod.SCRIPT.read_text(encoding="utf-8-sig"))
    scenes=memory()["scene_cards"]
    assert len(scenes)==30
    assert scenes[0]["scene_id"]=="SC-001" and "Bix" in scenes[0]["story_detail_vi"]
    assert "flashback" in memory()["story_first_rule"].lower()
    assert scenes[10]["scene_id"]=="SC-011"
    assert scenes[-1]["end_s"]==2700
    assert scenes[-1]["production_status"]=="STORY_OUTLINE_ONLY_NOT_V2_SHOT_APPROVED"


def test_protected_states_and_two_separate_signal_mechanisms():
    d=memory()
    assert d["state_at_end"]["evan_aware_of_magic"] is False
    assert d["state_at_end"]["elara_status"]=="MISSING_UNCONFIRMED"
    assert d["state_at_end"]["aila_sister_status"]=="MISSING_NOT_LOCATED"
    assert "NO_GATE_OPENED" in d["state_at_end"]["bubu_unmapped_world_target"]
    assert "COPPER_RESONANCE" in d["state_at_end"]["suitcase"]
    assert d["assets"]["aila_visual_approved"] is False


def future(**patch):
    d={
        "series_id":"bell_leaf","niche_id":"magical_witch_family_stories",
        "episode_id":"BL-0002","title":"The Lantern and the Storm-Broken Orchard Bridge",
        "hook":"A lost little lantern shines only when the orchard is silent.",
        "goal":"Mara and Lia must help a gardener safely harvest her seeds.",
        "central_conflict":"A storm destroys the bridge and separates two community orchards.",
        "resolution":"Residents rebuild the footbridge using logs and rope by themselves.",
        "unique_difference":"Independent earth gardener story, no suitcase or pulse mechanism.",
        "claimed_new_event_ids":["orchard_storm_bridge_rebuild"],
        "callbacks_to_prior_episode":[],
        "inherits_state":{k:memory()["state_at_end"][k] for k in
             ("evan_aware_of_magic","elara_status","aila_sister_status","bubu_unmapped_world_target")},
        "central_mechanism_id":"storm_breaks_small_footbridge",
        "solution_mechanism_id":"resident_log_rope_bridge"
    }
    d.update(patch)
    return d


def test_repeated_ep001_event_is_blocked():
    r=mod.check_future_episode(memory(),future(
        claimed_new_event_ids=["juno_copper_brace_amplifies_suitcase_afterpulse"]
    ))
    assert r["status"]=="BLOCKED"
    assert "REPEATED_EP001_EVENT_AS_NEW" in "\n".join(r["blocked"])


def test_same_copper_suitcase_plot_is_blocked_even_with_new_event_name():
    r=mod.check_future_episode(memory(),future(
        central_mechanism_id="copper_suitcase_station_afterpulse",
        solution_mechanism_id="wood_linen_two_pulse_suitcase"
    ))
    assert r["status"]=="BLOCKED"


def test_new_story_remains_human_review_not_automatically_approved():
    r=mod.check_future_episode(memory(),future())
    assert r["status"]=="MANUAL_NOVELTY_REVIEW_REQUIRED"
    assert not r["production_authorized"] and not r["editorial_approval"]


def test_cannot_reset_magic_secrecy_and_missing_family():
    v=future()
    v["inherits_state"]["evan_aware_of_magic"]=True
    assert "CONFLICTS_WITH_EP001_END_STATE:evan_aware_of_magic" in mod.check_future_episode(memory(),v)["blocked"]


def test_recap_callback_distinct_from_claiming_new_incident():
    v=future(callbacks_to_prior_episode=[
       {"event_id":"juno_copper_brace_amplifies_suitcase_afterpulse",
        "new_consequence":"Juno rechecks a distinct non-metal bridge prototype due to his past failure."}
    ])
    assert mod.check_future_episode(memory(),v)["status"]=="MANUAL_NOVELTY_REVIEW_REQUIRED"


def test_corrupt_30_scene_timing_is_detected():
    d=memory()
    d["scene_cards"][1]["start_s"]=99
    problems=mod.validate_memory(d,mod.load_json(mod.INDEX),
        mod.SCRIPT.read_text(encoding="utf-8-sig"))
    assert any("TIME_GAP_OR_OVERLAP" in issue for issue in problems)
