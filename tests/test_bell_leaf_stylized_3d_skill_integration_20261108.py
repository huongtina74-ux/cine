import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_production_routes_exact_bell_leaf_to_stylized_3d_prompt_skill():
    p=json.loads((ROOT/"config/niches/slow_english_a2/production.json").read_text(encoding="utf-8"))
    assert p["series_id"]=="bell_leaf"
    assert p["subniche_id"]=="magical_witch_family_stories"
    g=p["bell_leaf_3d_i2v_provider_gate"]
    assert g["stylized_3d_prompt_skill"]==".claude/skills/cine-bell-leaf-stylized-3d-prompt-director/SKILL.md"
    assert g["stylized_3d_prompt_compiler"]=="tools/bell_leaf/compile_3d_animation_prompts.py"
    assert g["prompt_pair_requires_matching_active_tags"] is True
    assert g["prompt_output_status"]=="DRAFT_QC_PENDING_NO_MODEL_OR_HUMAN_APPROVAL"
    assert g["live_action_recast_permitted"] is False
    assert g["production_authorized"] is False

def test_three_existing_skills_delegate_to_single_prompt_skill_not_new_canon():
    for f in [
        ".claude/skills/cine-a2-muse-reference-anchoring/SKILL.md",
        ".claude/skills/cine-script-factory/SKILL.md",
        ".claude/skills/cine-bellfern-location-multiview-lock/SKILL.md"
    ]:
        data=(ROOT/f).read_text(encoding="utf-8")
        assert data.count("Mandatory Bell & Leaf 3D Prompt Director (2026-11-08)")==1
        assert "compile_3d_animation_prompts.py" in data
        assert "Mia/Walter/Biscuit" in data

def test_canon_artwork_remains_unmodified_by_new_prompt_skill():
    a=json.loads((ROOT/"config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json").read_text(encoding="utf-8"))
    assert len(a["characters"])==11 and len(a["locations"])==9
    assert a["storage_policy"]["original_artwork_public_release_authorized"] is False
    refs=json.loads((ROOT/"docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json").read_text(encoding="utf-8"))
    assert len(refs["shots"])==270
    assert refs["shots"][0]["active_character_tags_candidate"]==["MARA","ORIN"]
    assert all(x["image_video_final_canon_gate"]!="PASS" for x in refs["shots"])
