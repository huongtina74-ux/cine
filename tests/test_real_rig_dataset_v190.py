from __future__ import annotations
"""v1.6.30 actual worker rig + real video generalization qualification."""
import hashlib,json
from pathlib import Path
from collections import Counter
from types import SimpleNamespace

import pytest

from cinefactory.studio.blender_mask_dataset_qc import (
    BlenderMaskDatasetQC,BlenderVisibleMaskDatasetAssembler,
)
from cinefactory.studio.real_rig_domain_qc import RealRigDomainAdmissionQC
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate
from cinefactory.studio.trained_actor_detector_qc import TrainedDetectorEvaluation
from cinefactory.studio.multiscene_detector_qc import (
    MultiSceneDetectorReport,SplitDetectionResult,
)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"verification"/"v190_real_rig_dataset"

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

@pytest.fixture(scope="module")
def qc():
    obj=BlenderMaskDatasetQC.model_validate_json(
        (OUT/"mask_dataset_qc.json").read_text(encoding="utf-8"))
    assert obj.passed
    return obj

@pytest.fixture(scope="module")
def index():
    return json.loads((OUT/"raw"/"render_index.json").read_text(encoding="utf-8"))

@pytest.fixture(scope="module")
def report():
    path=OUT/"v190_qualification_evidence.json"
    assert path.is_file()
    data=json.loads(path.read_text(encoding="utf-8"))
    assert data["milestone"]=="v1.6.30"
    return data

def test_actual_cinefactory_minecraft_roblox_rigs_not_v189_proxies(index):
    assert len(index)==114
    assert all(x["rig_description"]=="ACTUAL_CINEFACTORY_WORKER_MINECRAFT_OR_ROBLOX_R6" for x in index)
    assert all(x["worker_sha256"]==digest(ROOT/"scripts"/"blender_animation_worker.py") for x in index)
    assert {"MINECRAFT","ROBLOX_R6"}=={x["rig_family"] for x in index}
    rigs={r["rig_id"] for r in json.loads((OUT/"rig_snapshot_v190.json").read_text(encoding="utf-8"))["rigs"]}
    assert all(set(x["rig_ids"].values())<=rigs for x in index)

def test_real_worker_camera_lighting_poses_split_manifest(index):
    assert Counter(x["split"] for x in index)=={"train":72,"val":18,"test":24}
    assert len({x["seed"] for x in index})==114
    assert len({x["scene_id"] for x in index})==114
    assert len({x["image"] for x in index})==114
    assert set(x["lighting_family"] for x in index)=={"low_key","medium","high_key"}
    assert {"seated","standing"}=={v for x in index for v in x["postures"].values()}
    assert all(x["camera_family"]=="HELDOUT_WIDE_HIGH_LOW" for x in index if x["split"]=="test")
    assert all(x["camera_family"]=="TRAIN_FRONT_MEDIUM" for x in index if x["split"]!="test")

def test_source_character_scene_registry_fingerprint_matches(index):
    snap=json.loads((OUT/"rig_snapshot_v190.json").read_text(encoding="utf-8"))
    assert snap["source_sha256"]["characters.yaml"]==digest(ROOT/"config"/"block_animation"/"characters.yaml")
    assert snap["source_sha256"]["scenes.yaml"]==digest(ROOT/"config"/"block_animation"/"scenes.yaml")
    assert {"mc_a","mc_b","r6_a","r6_b"}<={r["rig_id"] for r in snap["rigs"]}
    assert {"minecraft_classroom","roblox_classroom"}<={r["scene_id"] for r in snap["scenes"]}

def test_visible_actor_masks_derived_and_disjoint(qc):
    assert qc.raw_scenes==114
    assert qc.status=="MASK_DERIVED_YOLO_SCENE_SPLITS_PASS"
    assert qc.split_counts=={"train":72,"val":18,"test":24}
    assert sum(len(q.boxes) for q in qc.samples)==286
    assert all(s.mask_overlap_pixels==0 for s in qc.samples)
    assert all(len(x.boxes)>=2 for x in qc.samples)
    assert all(x.visible_pixel_count>=150 for r in qc.samples for x in r.boxes)
    assert not qc.production_qualified

def test_immutable_mask_label_hashes_verified(qc):
    changes=BlenderVisibleMaskDatasetAssembler.verify_preinference_integrity(
        dataset_dir=OUT/"dataset",report=qc,
    )
    assert changes==[]

def test_test_mask_label_pixel_coordinates_independently(qc,index):
    import cv2
    import numpy as np
    from PIL import Image
    row=next(x for x in index if x["split"]=="test" and x["rig_family"]=="ROBLOX_R6")
    sample=next(s for s in qc.samples if s.scene_id==row["scene_id"])
    for box in sample.boxes:
        img=np.asarray(Image.open(row["actor_masks"][box.actor]).convert("L"))
        y,x=np.where(img>127)
        assert len(x)>150
        assert box.image_box==[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1]

def test_real_rig_occlusion_actors_are_not_all_standing(index):
    assert sum(v=="seated" for x in index for v in x["postures"].values())>145
    assert sum(v=="standing" for x in index for v in x["postures"].values())>25
    assert sum(1 for x in index if len(x["postures"])==3)>10

def test_attack_fake_duplicate_split_seed_is_blocked(index,tmp_path):
    rows=json.loads(json.dumps(index[:]))
    rows[1]["seed"]=rows[0]["seed"]
    # Includes all three splits so only intended collision blocks.
    f=tmp_path/"duplicate_real_rigs.json"
    f.write_text(json.dumps(rows),encoding="utf-8")
    result=BlenderVisibleMaskDatasetAssembler().assemble(
        render_index=f,dataset_dir=tmp_path/"derived")
    assert not result.passed
    assert "TRAIN_VAL_TEST_SCENE_SEED_COLLISION" in result.blockers

def test_attack_modified_heldout_pixel_label_fails_closed(qc,tmp_path):
    import shutil
    selected=next(x for x in qc.samples if x.split=="test")
    img=tmp_path/"dataset"/"images"/"test"/(selected.scene_id+".png")
    label=tmp_path/"dataset"/"labels"/"test"/(selected.scene_id+".txt")
    img.parent.mkdir(parents=True)
    label.parent.mkdir(parents=True)
    shutil.copyfile(OUT/"dataset"/"images"/"test"/img.name,img)
    label.write_text("0 0.50000000 0.50000000 0.90000000 0.90000000\n",encoding="utf-8")
    restricted=qc.model_copy(update={"samples":[selected]})
    findings=BlenderVisibleMaskDatasetAssembler.verify_preinference_integrity(
        dataset_dir=tmp_path/"dataset",report=restricted)
    assert "BLENDER_PIXEL_MASK_LABEL_CHANGED:"+selected.scene_id in findings

def test_v190_local_company_wiring():
    from cinefactory.appctx import build_context
    ctx=build_context(ROOT)
    assert ctx.real_rig_domain_qc is ctx.studio.professional_company.real_rig_domain_qc

def test_v190_release_gate_blocks_missing_real_domain_evidence(qc):
    decision=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v190_required=True,actual_rig_dataset=qc,
    )
    assert not decision.passed
    assert "REAL_RIG_EXTERNAL_VIDEO_GENERALIZATION_FAILED" in decision.blockers
    assert "MULTIPROJECT_REAL_RIG_GENERALIZATION_UNQUALIFIED" in decision.blockers
    assert "HUMAN_APPROVED_ACTOR_MASKS_MISSING" in decision.blockers
    assert "DETECTOR_COMMERCIAL_LICENSE_NOT_APPROVED" in decision.blockers
    assert "ACTUAL_CINEFACTORY_WORKER_RIG_DATASET_FAILED" not in decision.blockers

def test_human_approval_cannot_be_faked_as_production_review(qc):
    dummy=SimpleNamespace(
        passed=True,production_qualified=False,
        generalization_to_multiple_independent_projects_verified=False,
        license_approved_for_commercial_distribution=False)
    fake=SimpleNamespace(approved=True,production_qualified=False)
    decision=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v190_required=True,actual_rig_dataset=qc,real_rig_domain=dummy,
        human_approved_dataset=fake,
    )
    assert not decision.passed
    assert "HUMAN_APPROVED_ACTOR_MASKS_MISSING" in decision.blockers

def test_trained_candidate_from_actual_factory_rigs_not_leaked_external_test(report):
    trained=report["trained_model"]
    assert trained["train_images"]==72 and trained["val_images"]==18
    assert trained["heldout_images_unseen"]==24
    assert trained["training_uses_test"] is False
    assert trained["training_uses_v186_external_video"] is False
    assert digest(trained["model_path"])==trained["model_sha256"]
    assert trained["real_worker_sha256"]==digest(ROOT/"scripts"/"blender_animation_worker.py")
    assert not trained["production_qualified"]

def test_heldout_test_threshold_selected_only_on_val(report):
    row=report["sealed_holdout_render"]
    assert row["measured"]
    assert row["target_ground_truth_source"]=="HELDOUT_PIXEL_RENDERED_ACTOR_MASKS"
    assert row["selection_rule"]=="VALIDATION_ONLY_MAX_F1_WITH_PRECISION_FLOOR_0_80"
    assert len(row["validation_sweep"])==5
    assert row["chosen_confidence"] in (.1,.2,.3,.4,.5)
    assert row["heldout_test"]["split"]=="test"
    assert row["heldout_test"]["images"]==24
    assert not row["production_qualified"]

def test_external_v186_video_is_heldout_from_both_models(report):
    real=report["unseen_existing_cinefactory_video"]
    baseline=report["previous_v189_model_same_video"]
    assert real["measured"] and baseline["measured"]
    assert real["video_sha256"]==baseline["video_sha256"]
    assert real["frames"]==12
    assert real["model_sha256"]==report["trained_model"]["model_sha256"]
    assert real["model_kind"]=="V190_REAL_RIG_WORKER_HELDOUT_V186_VIDEO"
    assert not real["production_qualified"]

def test_real_domain_admission_checks_external_recall_and_baseline(report):
    gate=report["real_domain_admission"]
    assert gate["measured"]
    assert gate["actual_cinefactory_rig_source_verified"]
    assert gate["external_recall_delta"]==pytest.approx(
        gate["external_video_recall"]-gate["baseline_external_recall"])
    assert gate["synthetic_test_precision"]==pytest.approx(
        report["sealed_holdout_render"]["heldout_test"]["precision"])
    assert not gate["production_qualified"]

def test_production_remains_blocked_even_if_heldout_synthetic_passes(report):
    gate=report["production_gate"]
    assert gate["status"]=="BLOCKED"
    assert not gate["passed"]
    assert "HUMAN_APPROVED_ACTOR_MASKS_MISSING" in gate["blockers"]
    assert "DETECTOR_COMMERCIAL_LICENSE_NOT_APPROVED" in gate["blockers"]
    assert "MULTIPROJECT_REAL_RIG_GENERALIZATION_UNQUALIFIED" in gate["blockers"]
    assert not report["production_qualified"]
