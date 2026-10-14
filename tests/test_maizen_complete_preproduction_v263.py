"""Acceptance tests: original 14m screenplay, unique storyboard images, importable assets,
and unsigned G02 source-review evidence. No fake release gate."""
from __future__ import annotations
import hashlib,json,shutil,zipfile
from pathlib import Path
from PIL import Image
import pytest
from cinefactory.studio.maizen_full_screenplay_v263 import make_story, ROOT, SCENES
from cinefactory.studio.maizen_original_assets_v263 import make_assets,ASSETS
from cinefactory.studio.maizen_g02_recheck_v263 import verify

ART=ROOT/"data/verification/v263_maizen_full_story_assets"

def test_82_shot_screenplay_has_exact_840s_continuity_and_original_character_bible():
    obj=make_story(root=ROOT,write=False)
    shots=obj["shots"]
    assert obj["runtime_seconds"]==840
    assert obj["story_beats"]==21
    assert obj["shooting_script_shots"]==82
    assert len(shots)==82
    assert shots[0]["start"]==0
    assert shots[-1]["end"]==840
    assert all(s["end"]>s["start"] for s in shots)
    assert all(shots[i]["end"]==shots[i+1]["start"] for i in range(81))
    assert {b for b in SCENES}=={f"B{i:02d}" for i in range(4,22)}
    assert obj["source_script_status"]!="FINAL_APPROVED_SCRIPT"
    assert not obj["rendered_media_exists"]
    assert not obj["approved_for_commercial_release"]
    assert all("Mikey" not in s["action"] for s in shots)

def test_story_uses_real_v262_pilot_props_without_teleportation():
    obj=make_story(root=ROOT)
    early=obj["shots"][:9]
    assert [(x["start"],x["end"]) for x in early]==[(i*5,(i+1)*5) for i in range(9)]
    assert early[2]["state_after"]=="SKETCH_VISIBLE_UNOWNED"
    assert early[3]["state_after"]=="SKETCH_WITH_PIP"
    assert obj["shots"][9]["start"]==45
    assert obj["shots"][9]["end"]==50
    text=" ".join(s["action"] for s in obj["shots"])
    for term in ("BLUE–AMBER–BLUE","HOOK_TOOL","WORKSHOP_FLOOR_DRAIN","DOOR_CAVE_CODED","DOOR_WORKSHOP_FALSEWALL"):
        assert term in text

def test_generated_assets_are_original_importable_static_meshes_and_unique_storyboards():
    meta=json.loads((ART/"original_voxel_asset_registry.json").read_text(encoding="utf8"))
    assert meta["asset_count"]==len(ASSETS)==27
    assert meta["original_only"] is True
    assert meta["real_rendered_video"] is False
    assert all(not a["rigged"] and not a["animated"] for a in meta["meshes"])
    asset_ids={a["asset_id"] for a in meta["meshes"]}
    screenplay=json.loads((ART/"nova_pip_14min_shooting_script.json").read_text(encoding="utf8"))
    assert all(set(shot["asset_refs"]).issubset(asset_ids) for shot in screenplay["shots"]), "Missing asset for storyboard or 14min shot"
    for a in meta["meshes"]:
        mesh=ART/a["file_obj"];mtl=ART/a["material_file"]
        assert mesh.is_file() and mtl.is_file()
        txt=mesh.read_text(encoding="utf8")
        assert txt.count("\nv ")==a["vertex_count"]
        assert txt.count("\nf ")==a["face_count"]
        assert txt.count("\ng ")>=a["component_count"]
        assert hashlib.sha256(mesh.read_bytes()).hexdigest()==a["file_sha256"]
        assert "mtllib " in txt
        assert "newmtl" in mtl.read_text(encoding="utf8")
        for line in txt.splitlines():
            if line.startswith("f "):
                indices=[int(x) for x in line.split()[1:]]
                assert len(indices)==4
                assert all(1<=n<=a["vertex_count"] for n in indices)
    storyboard=json.loads((ART/"storyboard_9shots_editable.json").read_text(encoding="utf8"))
    assert len(storyboard["frames"])==9
    hashes=set()
    for frame in storyboard["frames"]:
        path=ART/frame["storyboard_png"]
        with Image.open(path) as image:
            assert image.size==(1280,720)
            image.verify()
        hashes.add(hashlib.sha256(path.read_bytes()).hexdigest())
    assert len(hashes)==9, "Storyboards must show distinct setups, not the same frame renamed."
    with zipfile.ZipFile(ART/"nova_pip_preproduction_blockouts_v263.zip") as package:
        assert package.testzip() is None
        paths=set(package.namelist())
        assert "nova_pip_14min_screenplay.md" in paths
        assert "nova_pip_shot_edl.csv" in paths
        assert "storyboard/P09.png" in paths
        assert "meshes/NOVA.obj" in paths and "meshes/PIP.obj" in paths

def test_rechecked_source_files_do_not_grant_signed_semantic_qc():
    result=verify(root=ROOT,write=False,decode=False)
    assert result["reopened_source_windows"]==11
    assert result["original_review_windows"]==120
    assert result["new_dense_source_frame_samples"]>=100
    assert result["G02"].startswith("BLOCKED")
    assert result["reviewer_signoff"]=="NOT_SIGNED"
    assert result["independent_native_soundtrack_listening_completed"] is False
    assert not result["original_video_all_frames_reobserved_1x"]
    assert all(x["native_audio_recording_speed"]==1 for x in result["technical_source_evidence"])
    assert all(x["sound_hash_verified"] for x in result["technical_source_evidence"])
    assert all(x["reviewer_signature"] is None for x in result["pending_reviewer_windows"])

def test_tampered_legacy_story_is_rejected_before_screenplay_accepted(tmp_path):
    old=ROOT/"data/verification/v243_maizen_original_preproduction/original_story_and_21_beats.json"
    corrected=ROOT/"data/verification/v262_maizen_story_alignment/corrected_pilot_and_continuity.json"
    out=tmp_path/"data/verification/v243_maizen_original_preproduction"
    out.mkdir(parents=True)
    obj=json.loads(old.read_text(encoding="utf8"))
    obj["beats"][3]["end"]=999
    (out/old.name).write_text(json.dumps(obj),encoding="utf8")
    tgt=tmp_path/"data/verification/v262_maizen_story_alignment"
    tgt.mkdir(parents=True)
    shutil.copy2(corrected,tgt/corrected.name)
    with pytest.raises(ValueError,match="SOURCE_BEAT_TIMELINE_DRIFT"):
        make_story(root=tmp_path,write=False)

def test_entire_14minute_storyboard_has_82_real_png_and_editable_vector_panels():
    import xml.etree.ElementTree as ET
    index=json.loads((ART/"storyboard_full_82_editable.json").read_text(encoding="utf8"))
    assert index["runtime_sec"]==840 and index["shot_count"]==82
    shots=index["frames"]
    assert len(shots)==82
    assert shots[0]["source_seconds"][0]==0
    assert shots[-1]["source_seconds"][-1]==840
    ids={a["asset_id"] for a in json.loads((ART/"original_voxel_asset_registry.json").read_text(encoding="utf8"))["meshes"]}
    hashes=[]
    for a in shots:
        assert set(a["referenced_asset_ids"]).issubset(ids)
        png=ART/a["png"];svg=ART/a["editable_svg"]
        assert png.is_file() and svg.is_file()
        with Image.open(png) as im:
            assert im.size==(1280,720)
            im.verify()
        tree=ET.parse(svg)
        assert tree.getroot().tag.endswith("svg")
        hashes.append(hashlib.sha256(png.read_bytes()).hexdigest())
    assert len(set(hashes))==82
    assert all(shots[i]["source_seconds"][1]==shots[i+1]["source_seconds"][0] for i in range(81))
    with zipfile.ZipFile(ART/"nova_pip_full_14min_preproduction_v263.zip") as z:
        assert z.testzip() is None
        names=set(z.namelist())
        assert len([n for n in names if n.startswith("storyboard_full/") and n.endswith(".svg")])==82
        assert len([n for n in names if n.startswith("storyboard_full/") and n.endswith(".png")])==82
        assert "g02_unsigned_independent_review_queue.json" in names
        assert "meshes/RIVER_RIDGE.obj" in names
