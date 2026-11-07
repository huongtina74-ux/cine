"""Historical CINE screenplay inventory: same-niche archive without fake owner approval."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_FILE = ROOT / "tools/cf_story_archive_scan.py"
SPEC = importlib.util.spec_from_file_location("cine_archive", MODULE_FILE)
archive = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(archive)


def sandbox():
    root = ROOT / "data/story_quality/_pytest_sandbox"
    root.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=root, prefix="cine-archive-")


def make_project(root: Path, pid: str, niche="mom_grandma_family_original",
                 full_script=True, legacy=True):
    base = root / pid
    (base / "04_story").mkdir(parents=True)
    (base / "05_outline").mkdir(parents=True)
    (base / "06_script").mkdir(parents=True)
    (base / "08_final").mkdir(parents=True)
    story = {
        "niche_id": niche, "working_title": "The Seven Family Envelopes",
        "goal": "An elderly neighbor has to secure a safe supply route without losing dignity",
        "central_conflict": "The volunteer network cannot honor promises because two members disagree over consent",
        "resolution": "The family builds a transparent opt-in roster and the community revises its safe transit plan",
        "hook": "A sealed letter arrives for the person who vanished from the county twenty years before",
        "twist": "The missing signature belongs to a trusted volunteer who has been protecting someone else's privacy",
        "emotional_change": "The older protagonist abandons a need for total control and accepts genuine help",
        "lasting_consequence": "A permanent independent route ledger is maintained by the community rather than one hero",
        "theme": "Trust requires honest consent rather than forced dependence",
    }
    (base / "04_story/story_dna.json").write_text(json.dumps(story), encoding="utf-8")
    outline = {"niche_id":niche,"beats":[
        {"title":"A letter","goal":story["hook"]},
        {"title":"A mistaken route","goal":story["central_conflict"]},
        {"title":"A safe change","goal":story["resolution"]}
    ]}
    (base / "05_outline/beat_sheet.json").write_text(json.dumps(outline),encoding="utf-8")
    doc = "\n".join(
        f"SC-{i:03d}: A volunteer checks a unique bus departure for the Mercer family at exact time {i}."
        f" A letter that had remained sealed since {i+1950} now becomes evidence in the case."
        f" The protagonist asks for consent from witness {i} and changes the route accordingly."
        for i in range(280))
    output = base / "08_final/final_script.md"
    if full_script:
        output.write_text(doc,encoding="utf-8")
    manifest = {
        "project_id":pid,"niche_id":niche,
        "mode":"ORIGINAL_FICTION",
        "approved_stages":{"final":{"artifact_hashes":{
            "08_final/final_script.md":archive.sha(output) if full_script else "missing"
        }}} if legacy else {}
    }
    (base/"manifest.json").write_text(json.dumps(manifest),encoding="utf-8")
    return base, doc, story


def test_scans_earlier_scripts_from_same_niche_only():
    with sandbox() as d:
        root=Path(d)
        make_project(root,"old_grandma_project")
        make_project(root,"science_other_project","science_space_nature_sleep")
        (root/"empty_project").mkdir()
        (root/"empty_project/manifest.json").write_text(
            json.dumps({"project_id":"empty_project","niche_id":"mom_grandma_family_original","approved_stages":{}}),encoding="utf-8")
        result=archive.scan("mom_grandma_family_original",archive_root=root)
        assert result["projects_seen"]==3
        assert result["matching_niche"]==2
        assert len(result["historical_records"])==1
        item=result["historical_records"][0]
        assert item["status"]=="HISTORICAL_STAGE_ATTESTATION_NOT_HUMAN_VERIFIED"
        assert item["human_editor_signoff_authenticated"] is False
        assert item["artifact_kind"]=="FULL_SCRIPT_PRESENT"


def test_story_rephrase_different_title_but_same_conflict_resolution_is_blocked():
    with sandbox() as d:
        root=Path(d)
        _,_,story=make_project(root,"old_grandma_project")
        plan={"story":{"title":"A Fresh New Family Story With Another Name",
                       "central_conflict":story["central_conflict"],
                       "resolution":story["resolution"],
                       "goal":"A related character wants to protect her neighborhood"}}
        r=archive.compare_plan(plan,archive.scan("mom_grandma_family_original",archive_root=root))
        assert r and r[0]["level"]=="BLOCK_HISTORICAL_STORY_COPY"
        assert "central_conflict" in r[0]["matched_axes"]


def test_full_script_copy_detected_after_title_and_metadata_changes():
    with sandbox() as d:
        root=Path(d)
        _,body,_=make_project(root,"old_grandma_project")
        report=archive.scan("mom_grandma_family_original",archive_root=root)
        copied="A DIFFERENT TITLE\\n"+body.replace("Mercer family","a different family")
        found=archive.compare_script(copied,report)
        assert found
        assert found[0]["level"]=="BLOCK_HISTORICAL_SCRIPT_COPY"
        assert found[0]["shared_seven_word_spans"]>=100


def test_unrelated_short_script_does_not_false_block():
    with sandbox() as d:
        root=Path(d)
        make_project(root,"old_grandma_project")
        new="The postman helps a family find a small silver bell while clouds gather in Bellfern. "*80
        assert archive.compare_script(new,archive.scan("mom_grandma_family_original",archive_root=root))==[]


def test_stale_old_script_receipt_flagged_not_silently_approved():
    with sandbox() as d:
        root=Path(d)
        base,_,_=make_project(root,"old_grandma_project")
        (base/"08_final/final_script.md").write_text("Changed after historic attestation",encoding="utf-8")
        result=archive.scan("mom_grandma_family_original",archive_root=root)
        assert result["historical_records"][0]["status"]=="STALE_SCRIPT_SHA_STAGE_ATTESTATION"
        assert result["historical_records"][0]["human_editor_signoff_authenticated"] is False


def test_malformed_manifest_or_cross_niche_story_is_fail_closed():
    with sandbox() as d:
        root=Path(d)
        base,_,_=make_project(root,"old_grandma_project")
        (base/"04_story/story_dna.json").write_text(
            json.dumps({"niche_id":"science_space_nature_sleep"}),encoding="utf-8")
        with pytest.raises(ValueError,match="Cross-niche"):
            archive.scan("mom_grandma_family_original",archive_root=root)
        (base/"manifest.json").write_text("{malformed",encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            archive.scan("mom_grandma_family_original",archive_root=root)


def test_history_isolated_from_other_niches_and_validates_missing_archive():
    with sandbox() as d:
        root=Path(d)
        make_project(root,"old_grandma_project")
        assert archive.scan("magical_witch_family_stories",archive_root=root)["historical_records"]==[]
        missing=root/"not_mounted"
        assert archive.scan("mom_grandma_family_original",archive_root=missing)["status"]=="ARCHIVE_NOT_MOUNTED"


def test_new_story_quality_gate_uses_legacy_archive_before_approval():
    from importlib.util import spec_from_file_location,module_from_spec
    p=ROOT/"tools/cf_story_quality_gate.py"
    s=spec_from_file_location("storygate_legacy",p)
    obj=module_from_spec(s);s.loader.exec_module(obj)
    with sandbox() as d:
        root=Path(d)
        _,_,story=make_project(root,"old_grandma_project")
        fixture={
            "niche_id":"mom_grandma_family_original","series_id":"old_family_series",
            "episode_id":"AUDIO-002","story":{
                "title":"A completely different headline",
                "central_conflict":story["central_conflict"],
                "resolution":story["resolution"]
            }
        }
        result=obj.evaluate(fixture,ledger_root=root/"ledger",historical_root=root,
                            check_bell_leaf_proposals=False)
        assert result["status"]=="BLOCKED"
        assert "DUPLICATES_HISTORICAL_PROJECT_OUTLINE" in result["blocking"]
        assert result["historical_script_archive_count"]==1
