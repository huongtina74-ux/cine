"""Tests for Bell & Leaf stylized 3D CGI prompt skill/CLI.
These assert prompt *constraints*, not generated video/face identity.
"""
from __future__ import annotations
import copy,importlib.util,json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("cgi_compiler",ROOT/"tools/bell_leaf/compile_3d_animation_prompts.py")
P=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(P)
BRIEF=ROOT/"docs/story/bell_leaf/ep001_screenplay/EP001_3D_PROMPT_BRIEF_EXAMPLE.json"


def fixture():
    return json.loads(BRIEF.read_text(encoding="utf-8"))


def test_two_canon_locked_reference_shots_generate_paired_draft_prompts():
    result=P.compile_batch(fixture(),ROOT)
    assert result["count"]==2 and result["status"]=="DRAFT_QC_PENDING"
    assert result["none_production_authorized"]
    for rec in result["receipts"]:
        assert rec["status"]=="DRAFT_BLOCKED_PENDING_CANON_AND_PRODUCTION_QC"
        assert rec["production_authorized"] is False
        assert rec["provider_account_verified"] is False
        assert rec["image_status"]==rec["video_status"]=="DRAFT_NOT_GENERATED"
        assert "DIRECTOR_VISIBLE_CAST_UNREVIEWED" in rec["blockers"]
        assert "DIRECTOR_CAMERA_AND_GEOMETRY_UNREVIEWED" in rec["blockers"]
        assert "FIRST_FRAME_NOT_CREATED_OR_HUMAN_APPROVED" in rec["blockers"]
        assert "REAL_10S_CGI_VIDEO_NOT_REVIEWED" in rec["blockers"]
        assert rec["image_prompt"].endswith("ACTIVE TAGS FOR THIS SHOT: ["+", ".join(rec["active_tags"])+"]")
        assert rec["video_prompt"].endswith("ACTIVE TAGS FOR THIS SHOT: ["+", ".join(rec["active_tags"])+"]")
        assert "stylized 3D CGI" in rec["image_prompt"]
        assert "stylized 3D" in rec["video_prompt"]
        assert "0–2s" in rec["video_prompt"] and "2–7s" in rec["video_prompt"] and "7–10s" in rec["video_prompt"]
        assert "one 10.0-second" not in rec["video_prompt"].lower() or "10.0" in rec["video_prompt"]
        assert "\n" not in rec["image_prompt"] and "\n" not in rec["video_prompt"]
        assert rec["location_reference_sha256"] and len(rec["location_reference_sha256"])==64
        assert len(rec["character_references"])==len(rec["active_tags"])
    assert result["receipts"][0]["active_tags"]==["BIX","MARA"]
    assert result["receipts"][1]["active_tags"]==["LIA"]
    assert result["images_txt"].count("\n\n")==1
    assert result["videos_txt"].count("\n\n")==1
    assert result["images_txt"].endswith("\n") and not result["images_txt"].endswith("\n\n")


def test_never_fabricates_approval_or_uploaded_images():
    d=P.compile_batch(fixture(),ROOT)
    for item in d["receipts"]:
        assert "provider_upload_ids" not in item
        assert "referenceImageMediaIds" not in item
        assert item["human_canon_visual_approval"] is False
        assert "no new face" not in item["image_prompt"].lower()
        assert "Biscuit" not in item["image_prompt"]


@pytest.mark.parametrize("bad",[
 "The photorealistic actress smiles at the camera",
 "The real human turns toward the robot",
 "A cinematic live-action woman in the family kitchen",
 "Hyperrealistic skin pores and a smiling woman",
 "Mia gently speaks to Mara while walking",
 "Grandpa Walter reaches across the table",
 "Biscuit watches the spoon on a sunny afternoon",
 "Cut to a new scene in the village",
 "A 3x3 collage of Mara's face angles",
 "The camera orbit 360 degrees around the boy",
])
def test_rejects_recast_noncanon_multiscene_and_grid_directions(bad):
    data=fixture()
    data["shots"][0]["image"]["pose"]=bad
    with pytest.raises(ValueError):
        P.compile_batch(data,ROOT)


@pytest.mark.parametrize("bad",[
 "The camera zooms in on the face, then cuts to the garden for a new scene",
 "The real actor morphs into a human woman",
 "A montage of Juno as a real actress in a new place",
])
def test_rejects_invalid_i2v_motion(bad):
    data=fixture()
    data["shots"][0]["video"]["action_2_7"]=bad
    with pytest.raises(ValueError):
        P.compile_batch(data,ROOT)


def test_rejects_wrong_niche_unknown_face_or_wrong_cast():
    data=fixture()
    data["niche_id"]="cozy_bedtime_fiction"
    with pytest.raises(ValueError,match="WRONG_NICHE"):
        P.compile_batch(data,ROOT)
    data=fixture()
    data["shots"][0]["visible_cast"]=["MARA","BIX"]
    with pytest.raises(ValueError,match="CAST_NOT_EQUAL"):
        P.compile_batch(data,ROOT)
    data=fixture()
    data["shots"][0]["visible_cast"]=["AILA"]
    with pytest.raises(ValueError,match="UNAPPROVED_OR_FOREIGN_VISIBLE_CAST"):
        P.compile_batch(data,ROOT)
    data=fixture()
    data["shots"][0]["visible_cast"]=["BIX","BIX"]
    with pytest.raises(ValueError,match="VISIBLE_CAST"):
        P.compile_batch(data,ROOT)


def test_rejects_duplicate_unordered_or_unsupported_shot_numbers():
    data=fixture()
    data["shots"].reverse()
    with pytest.raises(ValueError,match="SHOTS_NOT_ORDERED"):
        P.compile_batch(data,ROOT)
    data=fixture()
    data["shots"].append(copy.deepcopy(data["shots"][0]))
    with pytest.raises(ValueError,match="BAD_OR_DUPLICATE"):
        P.compile_batch(data,ROOT)
    data=fixture()
    data["shots"][1]["shot_id"]="S999"
    with pytest.raises(ValueError,match="UNKNOWN_OR_DUPLICATE"):
        P.compile_batch(data,ROOT)


def test_rejects_empty_motion_and_overdirected_shot():
    data=fixture()
    data["shots"][0]["video"]["setup_0_2"]="A lovely image with no movements to animate"
    data["shots"][0]["video"]["action_2_7"]="A wonderful static beautiful scene of family comfort"
    data["shots"][0]["video"]["reaction_7_10"]="The very image continues to look very wonderful"
    with pytest.raises(ValueError,match="NO_VISIBLE_PHYSICAL_MOTION"):
        P.compile_batch(data,ROOT)
    data=fixture()
    data["shots"][0]["video"]["action_2_7"]="Mara nods "+("very slowly "*100)
    with pytest.raises(ValueError):
        P.compile_batch(data,ROOT)


def test_cli_writes_exact_one_blank_line_between_prompt_lines(tmp_path):
    from subprocess import run
    out=tmp_path/"drafts"
    proc=run([__import__("sys").executable,str(ROOT/"tools/bell_leaf/compile_3d_animation_prompts.py"),
              "--brief",str(BRIEF),"--out-dir",str(out)],capture_output=True,text=True)
    assert proc.returncode==0,proc.stderr+" "+proc.stdout
    for name in ("FLOW_IMAGE_DRAFTS.txt","MUSE_VIDEO_DRAFTS.txt"):
        p=out/name
        assert p.is_file()
        assert len(p.read_text(encoding="utf-8").splitlines())==3
        assert not p.read_text(encoding="utf-8").splitlines()[1]
    receipts=json.loads((out/"DRAFT_QC_RECEIPTS.json").read_text(encoding="utf-8"))
    assert receipts["count"]==2 and receipts["none_production_authorized"]
    assert "images_txt" not in receipts and "videos_txt" not in receipts


def test_no_silent_github_artwork_backup_claims():
    p=P.json_obj(ROOT/P.CONTRACT)
    assert p["series_id"]=="bell_leaf"
    assert p["approval_status"]=="ENGINE_AND_HUMAN_VIDEO_QC_NOT_VERIFIED"
    assert p["production_authorized"] is False
    assert any("Google" in x["title"] for x in p["source_basis"])
    assert p["locked_media_format"]["real_human_recast_allowed"] is False


def test_same_prompt_skill_for_claude_and_codex():
    a=(ROOT/".claude/skills/cine-bell-leaf-stylized-3d-prompt-director/SKILL.md").read_text(encoding="utf-8")
    b=(ROOT/".agents/skills/cine-bell-leaf-stylized-3d-prompt-director/SKILL.md").read_text(encoding="utf-8")
    assert a==b
    assert "FIRST FRAME" not in a.upper() or "first frame" in a.lower()
    assert "Mia" in a and "BUBU" in a
    assert "production_authorized" in a
