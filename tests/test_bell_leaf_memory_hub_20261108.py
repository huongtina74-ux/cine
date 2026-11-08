"""Read-only Bell & Leaf memory loader integration and anti-regression gates."""
import copy
import importlib.util
import json
import shutil
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("bell_memory_hub",ROOT/"tools/bell_leaf/story_memory_resolver.py")
H=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(H)

def test_story_bundle_loads_full_v2_not_legacy():
    c=H.load(root=ROOT,episode_id="BL-0001",stage="story")
    assert c["series_id"]=="bell_leaf" and c["niche_id"]=="magical_witch_family_stories"
    assert c["source_episode_id"]=="BL-0001"
    assert c["episode_story_revision"]=="v2.0_family_first_dramatic_development"
    assert len(c["all_30_scene_cards"])==30
    assert len(c["protected_events"])==30
    assert c["complete_30_scene_treatment"]==(ROOT/"docs/story/bell_leaf/ep001_screenplay/EP001_STORY_V2_MASTER_30_SCENES.md").read_text(encoding="utf-8")
    assert "S001" in c["episode_source_receipts"]["shot_bindings"]["source_path"] or "EP001_" in c["episode_source_receipts"]["shot_bindings"]["source_path"]
    assert c["production_authorized"] is False
    assert c["human_story_approval"] is False
    assert "private_owner_full_text" not in c and "secret_villain_identity" not in c

def test_scene_timing_events_and_end_state():
    c=H.load(root=ROOT,episode_id="BL-0001",stage="script",include_story_text=False)
    scenes=c["all_30_scene_cards"]
    assert [x["scene_id"] for x in scenes]==[f"SC-{i:03d}" for i in range(1,31)]
    assert scenes[0]["start_s"]==0 and scenes[-1]["end_s"]==2700
    assert c["state_at_end"]["evan_aware_of_magic"] is False
    assert c["state_at_end"]["aila_sister_status"]=="MISSING_NOT_LOCATED"
    assert c["state_at_end"]["elara_status"]=="MISSING_UNCONFIRMED"
    assert c["state_at_end"]["earth_fixed_station"]=="OFFLINE_AT_END"
    assert c["state_at_end"]["bubu_unmapped_world_target"]=="ECHO_HEARD_SOURCE_UNCONFIRMED_NO_GATE_OPENED"

def test_early_shot_binds_only_actual_cast_not_entire_scene():
    c=H.load(root=ROOT,episode_id="BL-0001",stage="image",shot_id="S001")
    s=c["shot_binding"]
    assert s["active_character_tags"]==["BIX","MARA"]
    assert s["scene_id"]=="SC-001"
    assert len(c["scene_card"]["character_tags"])==6
    assert [x["tag"] for x in c["character_media"]]==["BIX","MARA"]
    assert c["location_media"]["anchor_id"]=="BELL_KITCHEN_DAY"
    assert c["location_media"]["multiview_approved"] is False
    assert c["production_authorized"] is False
    assert "MULTIVIEW_NOT_APPROVED" in c["warnings"]
    assert "human" not in c["shot_status"].lower()

def test_next_episode_inherits_exact_final_state_and_anti_repeat():
    nxt=H.load(root=ROOT,episode_id="BL-0002",stage="next")
    old=H.load(root=ROOT,episode_id="BL-0001",stage="story",include_story_text=False)
    assert nxt["prior_episode_id"]=="BL-0001"
    assert nxt["continuity_start_from_previous_episode"]==old["state_at_end"]
    assert nxt["protected_events"]==old["protected_events"]
    assert nxt["proposed_episode_state"]=="NEW_PITCH_ONLY_NOT_WRITTEN_OR_APPROVED"
    assert "Flying Suitcase" in nxt["collision_warning"]
    assert not nxt["human_story_approval"]

@pytest.mark.parametrize("ep,stage,shot,err",[
("BL-0002","script",None,"EPISODE_NOT_REGISTERED"),
("BL-0001","next",None,"NEXT_EPISODE_ID_ALREADY_REGISTERED"),
("BL-0001","video",None,"SHOT_ID_REQUIRED"),
("BL-0001","story","S001","SHOT_ID_NOT_VALID_FOR_STAGE"),
("BL-0001","image","S271","SHOT_NOT_FOUND"),
("BL-0001","video","S000","SHOT_NOT_FOUND"),
("BROKEN","next",None,"BAD_EPISODE_ID"),
])
def test_wrong_episode_stage_and_shot_fail_closed(ep,stage,shot,err):
    with pytest.raises(ValueError,match=err):
        H.load(root=ROOT,episode_id=ep,stage=stage,shot_id=shot,include_story_text=False)

def test_rejects_missing_canon_on_cloned_root(tmp_path):
    # Only copy the exact required source links; no private originals/media.
    m=json.loads((ROOT/"config/series/bell_leaf/memory_manifest_v1.json").read_text(encoding="utf-8"))
    rels={"config/series/bell_leaf/memory_manifest_v1.json"}
    rels.update(m["source_files"].values())
    for ep in m["episode_registry"].values():
        rels.update(v for k,v in ep.items() if k in ("story_treatment","continuity","quality_plan","shot_bindings","legacy_shooting_script"))
    for rel in rels:
        dst=tmp_path/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/rel,dst)
    f=tmp_path/m["source_files"]["series_story"]
    f.unlink()
    with pytest.raises(ValueError,match="MISSING_REQUIRED_CANON_SOURCE"):
        H.load(root=tmp_path,stage="story",include_story_text=False)

def test_refuses_public_villain_source_export_and_no_invented_approvals():
    data=(ROOT/".claude/skills/cine-bell-leaf-memory-hub/SKILL.md").read_text(encoding="utf-8")
    assert "NEVER copies owner's four private full texts" in data
    assert "no" in data.lower() and "approval" in data.lower()
    a=H.load(root=ROOT,stage="story",include_story_text=False)
    assert a["private_source_policy"].startswith("LOCAL_ONLY")
    assert "production_authorized" in a and a["production_authorized"] is False

def test_both_agent_skills_identical():
    a=(ROOT/".claude/skills/cine-bell-leaf-memory-hub/SKILL.md").read_text(encoding="utf-8")
    b=(ROOT/".agents/skills/cine-bell-leaf-memory-hub/SKILL.md").read_text(encoding="utf-8")
    assert a==b and "story_memory_resolver.py" in a
