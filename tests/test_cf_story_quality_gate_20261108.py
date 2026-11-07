"""Deterministic CINE story logic + episode memory + Script Factory stage tests.

All episode plans and editorial signoffs are synthetic testing fixtures, never
real user-approved story episodes or proofs of video ownership/production.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/cf_story_quality_gate.py"
spec = importlib.util.spec_from_file_location("storygate", P)
gate = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(gate)

KINDS = ["HOOK", "GOAL", "DISCOVERY", "REVERSAL", "DISCOVERY", "CRISIS",
         "DISCOVERY", "REVERSAL", "CRISIS", "CLIMAX", "RESOLUTION", "AFTERMATH"]


def plan(niche="magical_witch_family_stories", series="bell_leaf", episode="BL-0622"):
    beats = []
    for i in range(12):
        beats.append({
            "beat_id": f"B{i+1:02d}", "kind": KINDS[i],
            "start_s": i * 225, "end_s": (i+1) * 225,
            "caused_by": [f"B{i:02d}"] if i else [],
            "because": "A prior choice creates a measurable new challenge the family must face",
            "visible_action": f"The family uses evidence from the previous scene to inspect the water clock {i+1} carefully",
            "obstacle": "An old safety protocol restricts access until the community verifies the environmental readings",
            "character_choice": "Mara chooses to ask permission and test a safer alternative instead of using stronger magic",
            "immediate_consequence": "The witnesses change the rescue schedule and the family must reconsider their route",
        })
    return {
        "schema": "cine.story_quality.episode.v1",
        "episode_id": episode, "niche_id": niche, "series_id": series,
        "target_minutes": 45,
        "setting_class": "NEW",
        "approved_character_tags": ["MARA", "LIA", "BUBU"],
        "canon": {"owner_source_lock": "FOUR_OWNER_TEXTS_20261107",
                  "visual_canon_reference": "CHARACTER_VISUAL_CANON_LOCK_CURRENT.json",
                  "canon_mutations": []},
        "story": {
            "title": "A Clock That Measures the River's Forgotten Promise",
            "hook": "The river bell rings for a boat that never arrived, while a water clock records a changing tide",
            "goal": "Mara wants to restore safe passage without forcing the local boat keepers to surrender control",
            "central_conflict": "Two well-meaning groups interpret a faulty tide chart differently and block the rescue",
            "stakes": "A family on the far bank misses treatment unless the crossing can be verified before night",
            "theme": "Shared evidence and consent can protect a community more effectively than unchecked power",
            "twist": "The clock does not predict the future; a damaged water tube records a delayed older current",
            "resolution": "Lia observes local fish patterns while Mara and the river keepers validate three new readings together",
            "emotional_change": "Juno learns the difference between being clever and allowing people to review the solution",
            "lasting_consequence": "The community keeps its own verified tide ledger and grants temporary repair access",
            "why_this_episode": "It lets a frightened witness become a trusted expert instead of a passive person rescued",
            "originality_difference": "A water-measurement and community-consent conflict replaces a magical battle or arbitrary portal",
        },
        "beats": beats,
        "setup_payoffs": [
            {"setup_beat":"B01","payoff_beat":"B05",
             "specific_clue":"The river bell makes an echo only after the clock's glass tube trembles",
             "earned_resolution":"The keeper checks the tube and proves the signal is delayed by trapped air"},
            {"setup_beat":"B03","payoff_beat":"B08",
             "specific_clue":"Three fish move against the tide at the same moment every afternoon",
             "earned_resolution":"Lia cross-checks the observations rather than treating them as magic"},
            {"setup_beat":"B06","payoff_beat":"B11",
             "specific_clue":"A faded flood mark shows how far the river reached in another season",
             "earned_resolution":"Mara compares three measurements and proposes safe passage with consent"},
        ],
        "continuity_deltas": [
            {"entity_id":"river_council_tide_ledger",
             "before":"no shared record of verified readings",
             "after":"a public ledger of verified readings maintained by elected river keepers",
             "caused_by":"B11"},
            {"entity_id":"mara_trust_community",
             "before":"river keepers hesitate to cooperate",
             "after":"river keepers grant conditional access for repairs after seeing transparent evidence",
             "caused_by":"B12"},
        ],
        "creative_axes": [
            "A river environmental measurement mystery rather than a missing-person rift",
            "A resolution through witness consent rather than forced magical power",
            "A visible limitation from a delayed clock tube that changes rescue timing",
        ],
        "editorial_questions":[
            "Would the river community reasonably withhold consent until measurements were verified?",
            "Is the delayed glass tube seeded clearly enough for the final discovery to be fair?",
            "How does Lia's observed animal behavior matter without making her omniscient?",
        ],
    }


def temp_root():
    p = ROOT / "data" / "story_quality" / "_pytest_sandbox"
    p.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(prefix="cine-story-", dir=p)


def test_profiles_match_canonical_niches_and_idea_seeds_are_niche_specific():
    p = gate.load_profiles()
    assert len(p["niches"]) == 10
    assert p["niches"]["magical_witch_family_stories"]["duration_minutes"] == [40, 50]
    with temp_root() as d:
        out = gate.offer_ideas("magical_witch_family_stories", "bell_leaf", 12, Path(d))
        assert len(out["directions"]) == len({x["seed_signature"] for x in out["directions"]}) == 12
        assert out["not_a_script"] is True
        assert all(x["status"] == "IDEA_SEED_ONLY_NOT_SCREENPLAY" for x in out["directions"])
        senior = gate.offer_ideas("mom_grandma_family_original", "grandma_saga", 6, Path(d))
        assert senior["status"] == "IDEA_SEEDS_NEED_WRITER_DEVELOPMENT"
        assert "BUBU" not in json.dumps(senior)
        assert gate.offer_ideas("magical_witch_family_stories", "wrong_series", 3, Path(d))["status"] == "BLOCKED"


def test_valid_structural_plan_is_only_a_candidate_for_editorial_review():
    with temp_root() as d:
        r = gate.evaluate(plan(), ledger_root=Path(d))
        assert r["status"] == "INDEPENDENT_STORY_EDITOR_REVIEW_REQUIRED", r
        assert r["automated_story_approval"] is False
        assert r["youtube_release_authorized"] is False
        assert r["approved_ledger_count"] == 0


def test_malformed_plot_fails_for_causality_setup_payoff_and_duration():
    broken = plan()
    broken["beats"][3]["caused_by"] = ["B11"]
    broken["beats"][4]["start_s"] += 10
    broken["beats"][7]["character_choice"] = ""
    broken["setup_payoffs"][0]["setup_beat"] = "B12"
    broken["target_minutes"] = 60
    with temp_root() as d:
        out = gate.evaluate(broken, ledger_root=Path(d))
        assert out["status"] == "BLOCKED"
        flags = "|".join(out["blocking"])
        assert "LACKS_PREVIOUS_CAUSAL_TRIGGER" in flags
        assert "BAD_TIMING_OR_GAP" in flags
        assert "UNSEEDED_OR_BACKWARDS" in flags
        assert "DURATION_OR_BEAT_TOTAL_OUTSIDE_NICHE_FORMAT" in flags


def test_bell_leaf_owner_canon_cannot_mutate_or_invent_gate():
    b = plan()
    b["canon"]["canon_mutations"] = [{"rule":"Earth was already mapped"}]
    b["beats"][2]["travel"] = {"route":"NEW","mechanism":"FREE_TELEPORT"}
    b["approved_character_tags"].append("INVENTED_GRANDMA")
    with temp_root() as d:
        o = gate.evaluate(b, ledger_root=Path(d))
        assert o["status"] == "BLOCKED"
        assert "BELL_LEAF_UNAPPROVED_CANON_MUTATION" in o["blocking"]
        assert "BELL_LEAF_CAST_NOT_OWNER_VERIFIED" in o["blocking"]
        assert "BEAT_2_UNKNOWN_WORLD_REQUIRES_ECHO" in o["blocking"]
        assert "BEAT_2_NO_SAFE_EXIT_PLAN" in o["blocking"]


def test_no_leakage_into_other_niches():
    b = plan(niche="slow_english_a2_story",series="bell_leaf",episode="A2_034")
    with temp_root() as d:
        r = gate.evaluate(b, ledger_root=Path(d), check_bell_leaf_proposals=False)
        assert "BELL_LEAF_MUST_USE_MAGICAL_WITCH_FAMILY_NICHE" in r["blocking"]


def test_duplicate_against_approved_memory_blocks_even_changed_title():
    b = plan()
    with temp_root() as d:
        store = Path(d)
        file = gate.ledger_file(b["niche_id"], b["series_id"], store)
        file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "niche_id":b["niche_id"], "series_id":b["series_id"],
            "episode_id":"BL-0100", "status":"EDITORIAL_SIGNOFF_RECORDED",
            "story_fingerprint": {k:b["story"][k] for k in
                ("hook","goal","central_conflict","twist","resolution","emotional_change","lasting_consequence")},
        }
        file.write_text(json.dumps(data,ensure_ascii=False)+"\n",encoding="utf-8")
        b["story"]["title"] = "A Completely Different Name for the Same Story"
        r=gate.evaluate(b,ledger_root=store,check_bell_leaf_proposals=False)
        assert "DUPLICATES_PRIOR_APPROVED_EPISODE" in r["blocking"]
        assert r["similar_approved_episodes"][0]["episode_id"] == "BL-0100"
        assert r["similar_approved_episodes"][0]["level"] == "BLOCK_DUPLICATE"


def test_corrupted_or_cross_niche_memory_fails_closed():
    b=plan()
    with temp_root() as d:
        file=gate.ledger_file(b["niche_id"],b["series_id"],Path(d))
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text('{"niche_id":"original_horror_audio","series_id":"bell_leaf","episode_id":"BL-0100","status":"EDITORIAL_SIGNOFF_RECORDED"}\n',encoding="utf-8")
        r=gate.evaluate(b,ledger_root=Path(d),check_bell_leaf_proposals=False)
        assert any(x.startswith("APPROVED_EPISODE_LEDGER_CORRUPT") for x in r["blocking"])


def test_reviewed_ledger_append_is_explicit_and_no_overwrite():
    b=plan()
    with temp_root() as d:
        root=Path(d); pp=root/"plan.json"; rr=root/"review.json"; ev=root/"review_evidence.txt"
        pp.write_text(json.dumps(b,ensure_ascii=False),encoding="utf-8")
        ev.write_text("Synthetic detailed review evidence in an isolated unit test only",encoding="utf-8")
        receipt={
            "verdict":"PASS", "reviewer_id":"synthetic_editor_test", "author_id":"synthetic_writer_test",
            "plan_sha256":gate.digest(pp), "owner_approval_reference":"SYNTHETIC_FIXTURE_ONLY",
            "evidence_file":str(ev), "evidence_sha256":gate.digest(ev),
            "evidence_notes":["Causal chain visibly advances the river rescue",
                              "The tide tube twist has a prior clue in the plan",
                              "The council's consent changes the later gate record"],
        }
        rr.write_text(json.dumps(receipt,ensure_ascii=False),encoding="utf-8")
        result=gate.append_reviewed_episode(pp,rr,ledger_root=root,project_root=ROOT)
        assert result["status"] == "EDITORIAL_RECORD_APPENDED"
        assert len(gate.load_ledger(b["niche_id"],b["series_id"],root)) == 1
        with pytest.raises(ValueError,match="CANNOT_REGISTER|EXISTING_EPISODE"):
            gate.append_reviewed_episode(pp,rr,ledger_root=root,project_root=ROOT)
        assert len(gate.load_ledger(b["niche_id"],b["series_id"],root)) == 1


def test_new_script_factory_project_hard_requires_quality_files():
    sys.path.insert(0, str(ROOT / 'tools'))
    spec2=importlib.util.spec_from_file_location("cf_factory_under_test", ROOT / "tools/cf_script_factory.py")
    factory=importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(factory)
    with temp_root() as d:
        store=Path(d)
        arg=SimpleNamespace(id="test_story_quality_001",mode="ORIGINAL_FICTION",
            niche="mom_grandma_family_original",minutes=45,writer="synthetic_writer",
            language="en-US",root=store)
        factory.initialize(arg)
        p=store/arg.id
        manifest=factory.read_json(p/"manifest.json")
        assert manifest["story_quality_contract_version"] == "1"
        assert (p/"05_outline").is_dir() and (p/"07_review").is_dir()
        out=next(x for x in factory.config()["stages"] if x["id"]=="outline")
        review=next(x for x in factory.config()["stages"] if x["id"]=="review")
        assert "05_outline/episode_quality_plan.json" in factory.stage_files(p,factory.config(),out)
        assert "07_review/story_quality_review.json" in factory.stage_files(p,factory.config(),review)
        with pytest.raises(ValueError,match="MISSING_EPISODE_QUALITY_PLAN"):
            gate.require_factory_stage(p,manifest,"outline")
        stat=factory.status(SimpleNamespace(id=arg.id,root=store))
        assert stat["story_quality_contract"] == "V1_REQUIRED_FOR_OUTLINE_ONWARD"
        assert not stat["editorial_originality_human_verified"]


def test_script_trace_and_editorial_review_require_actual_artifact_sha():
    b=plan()
    with temp_root() as d:
        p=Path(d);(p/"05_outline").mkdir();(p/"06_script").mkdir();(p/"07_review").mkdir()
        (p/"05_outline/episode_quality_plan.json").write_text(json.dumps(b,ensure_ascii=False),encoding="utf-8")
        manifest={"mode":"A2_ANIMATED_SCREENPLAY","niche_id":"magical_witch_family_stories",
                  "target_minutes":45,"writer_id":"writer_not_editor","story_quality_contract_version":"1"}
        gate.require_factory_stage(p,manifest,"outline",ROOT)
        script=p/"06_script/script.md"
        script.write_text("A very long script with no beat provenance " * 200, encoding="utf-8")
        with pytest.raises(ValueError,match="TRACE_IDS"):
            gate.require_factory_stage(p,manifest,"script",ROOT)
        script.write_text((" ".join(f"B{i:02d}" for i in range(1,13))+"\n"+
                          "MARA: I need everyone to see why this choice matters.\n")*130,encoding="utf-8")
        gate.require_factory_stage(p,manifest,"script",ROOT)
        review={
            "reviewer_id":"writer_not_editor","reviewed_script_sha256":gate.digest(script),
            "verdict":"PASS", "evidence_notes":["x","y","z"],
            "checklist":{k:"PASS" for k in ("causality","character_agency","setup_payoff",
                   "originality","continuity","distinct_emotional_resolution","niche_fit")}
        }
        rp=p/"07_review/story_quality_review.json"
        rp.write_text(json.dumps(review),encoding="utf-8")
        with pytest.raises(ValueError,match="NOT_INDEPENDENT"):
            gate.require_factory_stage(p,manifest,"review",ROOT)
        review["reviewer_id"]="separate_editor"
        rp.write_text(json.dumps(review),encoding="utf-8")
        gate.require_factory_stage(p,manifest,"review",ROOT)
        script.write_text(script.read_text(encoding="utf-8")+"Minor changed dialogue",encoding="utf-8")
        with pytest.raises(ValueError,match="STALE"):
            gate.require_factory_stage(p,manifest,"review",ROOT)
