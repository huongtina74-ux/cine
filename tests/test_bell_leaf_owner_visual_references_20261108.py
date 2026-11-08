"""Prevent regression of actual user-supplied Bell & Leaf character/location identity."""
import importlib.util,json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/"config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json"
B=ROOT/"docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json"
M=ROOT/".claude/skills/cine-a2-muse-reference-anchoring/integration/config/LOCATION_CURRENT.json"
spec=importlib.util.spec_from_file_location("owner_visual",ROOT/"tools/bell_leaf/inspect_visual_reference_20261108.py")
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

def test_owner_character_sources_and_spatial_conflicts_are_explicit():
    d=json.loads(A.read_text(encoding="utf-8"))
    tags={x for x in d["characters"] if x!="GROUP"}
    assert tags=={"EVAN","MARA","JUNO","LIA","BIX","BUBU","ORIN","GRANDPA_EARTH","GRANDMA_EARTH","ELARA"}
    assert all(r["canon_pixel_exact_to_owner"] for r in d["characters"].values())
    assert len(d["locations"])==9 and len(d["multi_location_concept_boards"])==3
    assert not any(v["geometry_lock"] for v in d["multi_location_concept_boards"].values())
    assert all(not v["multiangle_production_approved"] for v in d["locations"].values())
    assert {"EXT_A","BELLCHAMBER_A","MULTIANGLE_A","ROOM_ASSIGN_A"}=={x["id"] for x in d["conflict_register"]}
    assert d["global_rules"]["BIX"].endswith("NO BELL")
    assert "SPARKLING SPIRAL" in d["global_rules"]["BUBU"]

def test_270_shots_are_referenced_by_exact_source_asset_not_invented_upload_id():
    p=json.loads(B.read_text(encoding="utf-8"))
    assert len(p["shots"])==270
    assert p["shots"][0]["shot_id"]=="S001"
    assert p["shots"][-1]["shot_id"]=="S270"
    assert p["shots"][0]["space_id"]=="BH-KITCHEN"
    assert p["shots"][0]["owner_location_plate_path"].endswith("BELL_KITCHEN_DAY.png")
    assert p["shots"][17]["space_id"]=="BH-KITCHEN"
    assert p["shots"][18]["site_id"]=="VEYLORA"
    assert p["shots"][18]["owner_location_plate_path"] is None
    assert all(s["image_video_final_canon_gate"]!="PASS" for s in p["shots"])
    assert all(s["referenceImageMediaIds"]==[] for s in p["shots"])
    assert any("AILA" in x["characters_without_approved_visuals"] for x in p["shots"])
    assert all("AILA" not in x["character_reference_paths"] for x in p["shots"])
    assert all(s["active_tags_line"].startswith("ACTIVE TAGS FOR THIS SHOT: [") for s in p["shots"])

def test_existing_location_gate_keeps_all_proposed_multiview_views_pending():
    info=json.loads(M.read_text(encoding="utf-8"))
    for key in ("BH-KITCHEN","BH-EXT","BH-ATELIER","BH-PARENTS","BH-FOYER","BH-JUNO","BH-LIA","BH-BELLCHAMBER","BH-REAR-GARDEN"):
        v=info["locations"]["BELL"]["spaces"][key]
        assert v["approval_state"]=="PENDING_NOT_GENERATED"
        assert v["owner_source_anchors_20261108"]
        assert all(x["approval_state"]=="SOURCE_VIEW_ONLY_PENDING_MULTIVIEW" for x in v["owner_source_anchors_20261108"])

def test_all_committed_binary_assets_pass_sha_when_present():
    result=gate.inspect(require_assets=True)
    if result["assets_missing"]:
        pytest.skip("OWNER_BINARY_ASSETS_NOT_YET_MIRRORED_IN_THIS_GIT_CHECKOUT")
    assert result["status"]=="OWNER_ASSET_SOURCE_INTEGRITY_PASS_NOT_PRODUCTION_APPROVED",result
    assert result["violations"]==[]
    assert result["files_verified"]>=44

def test_missing_reference_is_hard_block_when_require_assets():
    result=gate.inspect(require_assets=True)
    if result["assets_missing"]:
        assert "REQUIRED_OWNER_BINARY_ASSETS_MISSING" in result["violations"]
        assert result["status"]=="FAIL"
    else:
        assert result["status"]=="OWNER_ASSET_SOURCE_INTEGRITY_PASS_NOT_PRODUCTION_APPROVED"

def test_original_owner_artwork_is_not_silently_published_to_public_github():
    data=json.loads(A.read_text(encoding="utf-8"))
    policy=data["storage_policy"]
    assert policy["github_repository_visibility"].startswith("PUBLIC")
    assert policy["original_artwork_public_release_authorized"] is False
    assert policy["public_github_binary_images_state"]=="NOT_UPLOADED"
    assert policy["private_asset_storage_required_for_remote_sync"] is True
    assert policy["github_main_text_manifest_is_not_binary_backup"] is True
