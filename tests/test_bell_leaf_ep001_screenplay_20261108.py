"""Regressions for Bell & Leaf EP001 screenplay draft, not owner acceptance."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/"docs/story/bell_leaf/ep001_screenplay"
VFILE=ROOT/"tools/bell_leaf/verify_ep001_screenplay_20261108.py"
S=importlib.util.spec_from_file_location("ep001_validator",VFILE)
validator=importlib.util.module_from_spec(S);S.loader.exec_module(validator)

QFILE=ROOT/"tools/cf_story_quality_gate.py"
QS=importlib.util.spec_from_file_location("cine_story_quality",QFILE)
quality=importlib.util.module_from_spec(QS);QS.loader.exec_module(quality)


def test_ep001_exact_45min_slot_timing_and_substantive_a2_dialogue():
    q=validator.analyze()
    assert q["status"]=="INDEPENDENT_STORY_EDITOR_REVIEW_REQUIRED",q
    assert q["problems"]==[]
    assert q["scenes"]==30 and q["shots"]==270
    assert q["timed_script_seconds"]==2700
    # A2 deliberately allows natural reaction/silence within fixed 10s shots; wordcount is NOT duration.
    assert 2200 <= q["speech_words_quoted_approx"] <= 3300
    assert q["dialogue_quiet_shots"]<=16
    assert q["max_words_one_shot"]<=24
    assert q["voice_lipsync_qc"]=="NOT_PRODUCED"
    assert q["story_editor_approval"]=="PENDING"


def test_ep001_all_five_original_acts_in_complete_combined_reading_copy():
    full=(EP/"EP001_FULL_45MIN_SHOOTING_SCREENPLAY_DRAFT.md").read_text(encoding="utf-8-sig")
    paths=sorted(EP.glob("EP001_ACT_*.md"))
    assert len(paths)==5
    for act in paths:
        segment=act.read_text(encoding="utf-8-sig")
        assert segment in full, f"Combined script is stale relative to {act.name}"
    assert len(full)>55_000
    assert "STORY_REVIEW_REQUIRED" in full
    assert "not an approved final" in full.lower()
    assert "Aila" in full
    assert "Bubu" in full
    assert "Veylora" in full


def test_ep001_story_logic_plan_is_structurally_valid_but_unapproved():
    # V1 is an archived plan that predates the mandatory first-15s policy.
    plan=json.loads((EP/"EP001_STORY_QUALITY_PLAN_v2.json").read_text(encoding="utf-8-sig"))
    assert plan["niche_id"]=="magical_witch_family_stories" and plan["series_id"]=="bell_leaf"
    assert plan["canon"]["owner_source_lock"]=="FOUR_OWNER_TEXTS_20261107"
    assert plan["canon"]["canon_mutations"]==[]
    assert plan["target_minutes"]==45
    assert len(plan["beats"])==15 and len(plan["scenes"])==30
    assert len(plan["setup_payoffs"])>=4
    assert len(plan["character_arcs"])>=3
    assert len(plan["continuity_deltas"])>=5
    assert not plan.get("depends_on_approved_episodes",[])
    result=quality.evaluate(plan,project_root=ROOT)
    assert result["status"]=="INDEPENDENT_STORY_EDITOR_REVIEW_REQUIRED",result
    assert result["blocking"]==[]
    assert not result["automated_story_approval"]
    assert not result["youtube_release_authorized"]


def test_ep001_keeps_public_secret_and_visual_source_holds():
    file=(EP/"EP001_FULL_45MIN_SHOOTING_SCREENPLAY_DRAFT.md").read_text(encoding="utf-8-sig")
    lower=file.casefold()
    assert "isel varr" not in lower and "ash bellkeeper" not in lower
    assert "no ancient earth gate" in lower
    assert "ASSET_PENDING" in file
    assert "ONE GOLD" in file or "one gold" in file.lower()
    assert "SPARKLING SPIRAL" in file
    assert "NO bell" in file or "NO BELL" in file
    assert "fixed" in lower and "unknown" in lower
    memo=(EP/"EP001_STORY_EDITOR_REVIEW_NOTES_v1.md").read_text(encoding="utf-8-sig")
    assert "EP003" in memo and "DO NOT reuse" in memo
    assert "No automatic acceptance" in memo


def test_ep001_opens_on_warm_family_life_then_explains_vey_lora():
    acts=(EP/"EP001_ACT_I_00_09.md").read_text(encoding="utf-8")
    assert "SC-001 — A Very Strange, Very Normal Morning" in acts
    assert "SC-002 — One Breakfast, One Little Robot" in acts
    assert "SC-003 — The Flower Before the Fall" in acts
    assert "JUNO" in acts and "LIA" in acts and "EVAN" in acts
    assert "SPARKLING SPIRAL PURPLE" in acts
    assert "ordinary household noise, not a magical signal" in acts
    assert "COLD-OPEN / VEYLORA YEARS AGO" in acts
    assert "ORIN" in acts and "MARA" in acts
    plan=json.loads((EP/"EP001_STORY_QUALITY_PLAN_v2.json").read_text(encoding="utf-8"))
    assert plan["opening_hook"]["hook_type"]=="DISASTER_TEASER"
    assert plan["opening_hook"]["shots"][0]["visible_tags"]==["MARA","ORIN"]
    assert "Veylora" in plan["scenes"][0]["location"] and "Bell & Leaf" in plan["scenes"][0]["location"]
    assert "Veylora" in plan["scenes"][2]["location"]
    assert plan["scenes"][0]["start_s"]==0 and plan["scenes"][1]["end_s"]==180
    assert plan["scenes"][10]["start_s"]==900
    assert "same" in plan["scenes"][10]["location"].lower() and "morning" in plan["scenes"][10]["location"].lower()
    full=(EP/"EP001_FULL_45MIN_SHOOTING_SCREENPLAY_DRAFT.md").read_text(encoding="utf-8")
    assert "FIRST-15S HOOK" in full or "FAMILY-FIRST" in full
    assert "no ancient Earth gate" in full
