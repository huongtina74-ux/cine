"""Bell & Leaf Muse I2V production-safety regressions: NO fake media approval."""
import importlib.util
import json
from pathlib import Path

import pytest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


i2v=load("tools/bell_leaf/muse_i2v_preflight.py","i2v")
review=load("tools/bell_leaf/muse_i2v_frame_qc.py","review")
MOTION="The original small robot turns its head toward the mother, tilts the tray slowly, then stops."
PROVIDERS=["unknown_muse","meta_muse_video","fawna_muse","google_flow_omni_1_2","google_flow_veo_3_1"]


@pytest.mark.parametrize("provider",PROVIDERS)
def test_no_provider_is_automatically_claimed_live_and_account_authorized(provider):
    x=i2v.compile_shot("S001",provider,MOTION)
    assert x["status"]=="BLOCKED"
    assert x["production_authorized"] is False
    assert x["provider_account_tested"] is False
    assert x["model_version_tested"] is False
    assert x["real_generation_attempted"] is False
    assert x["generation_status"]=="NOT_STARTED"
    assert "PROVIDER_ACCOUNT_AND_MODEL_NOT_VERIFIED" in x["blockers"]


def test_unknown_muse_not_falsely_assumed_meta():
    x=i2v.compile_shot("S001","muse",MOTION)
    assert x["provider_id"]=="unknown_muse"
    assert "MUSE_PROVIDER_NOT_IDENTIFIED" in x["blockers"]
    assert "MODEL_10S_16_9_I2V_CAPABILITY_NOT_CONFIRMED" in x["blockers"]


def test_fawna_muse_grid_policy_does_not_break_one_scene_first_frame():
    x=i2v.compile_shot("S001","fawna_muse",MOTION)
    assert "PROVIDER_FIRST_FRAME_GRID_COLLIDES_WITH_SINGLE_SCENE_FRAME_POLICY" in x["blockers"]


def test_no_face_image_or_approved_location_means_no_production():
    x=i2v.compile_shot("S001","google_flow_omni_1_2",MOTION)
    assert "APPROVED_16_9_CGI_FIRST_FRAME_MISSING" in x["blockers"]
    assert "SHOT_CAST_VISIBLE_VOICE_ONLY_UNVERIFIED" in x["blockers"]
    assert "SHOT_CAMERA_ANGLE_NOT_APPROVED" in x["blockers"]
    assert "LOCATION_ANGLE_OR_VIEW_NOT_APPROVED" in x["blockers"]
    assert all(r["tag"] in i2v.ONLY_TAGS for r in x["reference_characters"])


def test_bell_leaf_legacy_character_templates_are_rejected():
    for person in ("Mia","Grandpa Walter","Biscuit"):
        text=f"The original robot turns and speaks to {person} at the breakfast table."
        x=i2v.compile_shot("S001","google_flow_omni_1_2",text)
        assert "LEGACY_NON_BELL_LEAF_CHARACTER_TEMPLATE" in x["blockers"]


@pytest.mark.parametrize("motion",[
 "Mara morphs into a real actor and changes her face completely.",
 "Juno becomes a photorealistic human on camera and walks forward.",
 "The film will cut to a new street and then change scene.",
])
def test_recasting_or_multiple_scenes_cannot_pass(motion):
    x=i2v.compile_shot("S001","google_flow_veo_3_1",motion)
    assert any(b.startswith("ACTION_") or b=="MULTI_SCENE_IN_ONE_10S_TAKE" for b in x["blockers"])


def test_motion_prompt_one_line_no_unnecessary_cast_or_photographic_remake():
    x=i2v.compile_shot("S001","google_flow_omni_1_2",MOTION)
    prompt=x["single_shot_motion_prompt"]
    assert "\n" not in prompt
    assert "ACTIVE TAGS FOR THIS SHOT: [" in prompt
    assert "STYLIZED" not in prompt  # style expressed once in readable sentence
    assert "stylized 3D CGI" in prompt
    assert "Mia" not in prompt and "Walter" not in prompt and "Biscuit" not in prompt
    assert "No on-screen text" in prompt
    assert "zoom-only substitute" in prompt


def test_first_frame_is_actual_single_landscape_16_9_image(tmp_path):
    good=tmp_path/"frame.png"
    Image.new("RGB",(1280,720),(45,78,93)).save(good)
    data=i2v.valid_first_frame(good)
    assert data["dimensions"]==[1280,720]
    assert data["sha256"]==i2v.digest(good)
    portrait=tmp_path/"portrait.png"
    Image.new("RGB",(720,1280),(45,78,93)).save(portrait)
    with pytest.raises(ValueError,match="16_9"):
        i2v.valid_first_frame(portrait)


def test_specific_unapproved_cast_is_blocked():
    x=i2v.compile_shot("S145","google_flow_omni_1_2",MOTION)
    # This is a single real production shot; it may or may not feature Aila
    # depending on the latest script, but the safe result is never approval.
    assert x["production_authorized"] is False
    assert x["status"]=="BLOCKED"


def test_real_mp4_review_is_not_simulated(tmp_path):
    with pytest.raises(ValueError,match="NO_REAL_VIDEO_PRESENT"):
        review.inspect(tmp_path/"not-generated.mp4",tmp_path/"reviews")
    assert "no_live_action_or_real_person_recast" in review.REVIEW_FLAGS
    assert "real_visible_character_motion_not_zoom_only" in review.REVIEW_FLAGS
    assert "approved_wav_voice_and_mouth_sync_if_dialogue" in review.REVIEW_FLAGS


def test_every_registered_model_has_explicit_capability_and_source():
    data=i2v.read_obj(i2v.CONTRACTS)
    assert set(data["providers"])==set(PROVIDERS)
    for key,p in data["providers"].items():
        assert "provider_verified_for_account" in p
        assert p["provider_verified_for_account"] is False
        if key!="unknown_muse":assert p["documentation_url"].startswith("https://")


def test_bell_leaf_270_shot_bindings_preserve_original_canon():
    d=i2v.read_obj(i2v.BIND)
    assert d["niche_id"]=="magical_witch_family_stories"
    assert len(d["shots"])==270
    assert all(s["referenceImageMediaIds"]==[] for s in d["shots"])
    assert all(s["image_video_final_canon_gate"]!="PASS" for s in d["shots"])

def test_cine_bell_leaf_specific_gate_does_not_certify_external_provider():
    root=Path(__file__).resolve().parents[1]
    config=json.loads((root/"config/niches/slow_english_a2/production.json").read_text(encoding="utf-8"))
    assert config["subniche_id"]=="magical_witch_family_stories"
    gate=config["bell_leaf_3d_i2v_provider_gate"]
    assert gate["provider_id"]=="unknown_muse"
    assert gate["production_authorized"] is False
    assert gate["provider_account_verified"] is False
    assert gate["live_action_recast_permitted"] is False
    assert gate["require_one_frame_not_9_grid"] is True
    assert set(gate["disallowed_legacy_characters"])=={"Mia","Grandpa Walter","Biscuit"}


def test_preflight_and_sample_qc_have_dedicated_locked_owner_skills():
    for rel in (
        ".claude/skills/cine-a2-muse-reference-anchoring/SKILL.md",
        ".claude/skills/cine-script-factory/SKILL.md",
        ".claude/skills/cine-bellfern-location-multiview-lock/SKILL.md"
    ):
        t=(ROOT/rel).read_text(encoding="utf-8")
        assert "Bell & Leaf Muse 3D animation drift prevention" in t
        assert "muse_i2v_preflight.py" in t
    doc=(ROOT/"docs/story/bell_leaf/MUSE_I2V_PROVIDER_STYLE_CONTINUITY_20261108.md").read_text(encoding="utf-8")
    assert "Fawna" in doc and "Meta Muse" in doc and "Omni 1.2" in doc
