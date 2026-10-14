from __future__ import annotations
"""v1.6.29 real Blender dataset mask provenance, split isolation and release gates."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import cv2
import pytest

from cinefactory.studio.blender_mask_dataset_qc import (
    BlenderVisibleMaskDatasetAssembler,BlenderMaskDatasetQC,
)
from cinefactory.studio.multiscene_detector_qc import MultiSceneDetectorEvaluator
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"verification"/"v189_scene_diversity"
SMOKE=ROOT/"data"/"verification"/"v189_scene_diversity_smoke"


@pytest.fixture(scope="module")
def mask_qc():
    x=BlenderMaskDatasetQC.model_validate_json(
        (DATA/"mask_dataset_qc.json").read_text(encoding="utf-8")
    )
    assert x.passed
    return x


@pytest.fixture(scope="module")
def release_evidence():
    p=DATA/"v189_qualification_evidence.json"
    if not p.is_file():
        pytest.skip("V189 held-out model evaluation not completed yet")
    return json.loads(p.read_text(encoding="utf-8"))


def test_actual_blender_152_distinct_scenes_and_three_splits(mask_qc):
    assert mask_qc.status=="MASK_DERIVED_YOLO_SCENE_SPLITS_PASS"
    assert mask_qc.raw_scenes==152
    assert mask_qc.split_counts=={"train":96,"val":24,"test":32}
    assert len(mask_qc.samples)==152
    assert len({s.seed for s in mask_qc.samples})==152
    assert len({s.scene_id for s in mask_qc.samples})==152
    assert mask_qc.production_qualified is False


def test_all_real_actor_masks_are_nonoverlapping_visible(mask_qc):
    assert all(x.mask_overlap_pixels==0 for x in mask_qc.samples)
    assert all(2<=len(x.boxes)<=3 for x in mask_qc.samples)
    assert all(
        box.visible_pixel_count>=150
        for s in mask_qc.samples for box in s.boxes
    )
    assert sum(len(s.boxes) for s in mask_qc.samples)==382


def test_all_heldout_scenes_and_actor_instances_grounded_to_masks(mask_qc):
    subset=[s for s in mask_qc.samples if s.split=="test"]
    assert len(subset)==32
    assert len({s.image_sha256 for s in subset})==32
    assert all(
        all(len(b.mask_sha256)==64 for b in s.boxes)
        for s in subset
    )
    assert all(s.scene_id.startswith("test_") for s in subset)


def test_mask_derived_image_label_coordinates_not_rig_approximations(mask_qc):
    sample=next(x for x in mask_qc.samples if x.split=="test")
    raw=json.loads((DATA/"raw"/"render_index.json").read_text(encoding="utf-8"))
    source=next(x for x in raw if x["scene_id"]==sample.scene_id)
    assert source["label_source"]=="INDEPENDENT_BLENDER_PIXEL_MASK_NOT_PROJECTED_BOX"
    for actor in sample.boxes:
        # Independent Pillow decode: OpenCV IMREAD_GRAYSCALE is not
        # guaranteed to return 2D if test process has patched imread.
        import numpy as np
        from PIL import Image
        mask=np.asarray(Image.open(source["actor_masks"][actor.actor]).convert("L"))
        assert mask.ndim==2
        yy,xx=(mask>127).nonzero()
        assert actor.image_box==[int(xx.min()),int(yy.min()),
                                 int(xx.max())+1,int(yy.max())+1]


def test_train_validation_test_seed_and_palette_disjoint(mask_qc):
    idx=json.loads((DATA/"raw"/"render_index.json").read_text(encoding="utf-8"))
    palette={"train":"primary","val":"complementary","test":"unseen_palette"}
    for row in idx:
        assert row["palette_family"]==palette[row["split"]]
        assert row["seed"] in {s.seed for s in mask_qc.samples}
        assert row["rig_description"].startswith("PROCEDURAL_VOXEL")
    assert set(mask_qc.per_split_identities)=={"train","val","test"}


def test_unmodified_dataset_integrity_unchanged_since_labeling(mask_qc):
    findings=BlenderVisibleMaskDatasetAssembler.verify_preinference_integrity(
        dataset_dir=DATA/"dataset",report=mask_qc,
    )
    assert findings==[]


def test_negative_tamper_a_label_cannot_be_accepted(mask_qc,tmp_path):
    # Audit a single copied sample and leave source dataset fully untouched.
    row=next(s for s in mask_qc.samples if s.split=="test")
    base=tmp_path/"poison_dataset"
    im=base/"images"/"test"/(row.scene_id+".png")
    label=base/"labels"/"test"/(row.scene_id+".txt")
    im.parent.mkdir(parents=True)
    label.parent.mkdir(parents=True)
    import shutil
    shutil.copy2(DATA/"dataset"/"images"/"test"/im.name,im)
    label.write_text("0 0.50000000 0.50000000 0.90000000 0.90000000\n",
                     encoding="utf-8")
    partial=mask_qc.model_copy(update={"samples":[row]})
    findings=BlenderVisibleMaskDatasetAssembler.verify_preinference_integrity(
        dataset_dir=base,report=partial,
    )
    assert "BLENDER_PIXEL_MASK_LABEL_CHANGED:"+row.scene_id in findings


def test_negative_tamper_a_validation_image_hash_cannot_be_accepted(mask_qc,tmp_path):
    row=next(s for s in mask_qc.samples if s.split=="val")
    base=tmp_path/"bad_pixel_dataset"
    im=base/"images"/"val"/(row.scene_id+".png")
    label=base/"labels"/"val"/(row.scene_id+".txt")
    im.parent.mkdir(parents=True)
    label.parent.mkdir(parents=True)
    im.write_bytes(b"not-a-real-image")
    label.write_text("0 .5 .5 .2 .2\n",encoding="utf-8")
    partial=mask_qc.model_copy(update={"samples":[row]})
    errors=BlenderVisibleMaskDatasetAssembler.verify_preinference_integrity(
        dataset_dir=base,report=partial,
    )
    assert "DATASET_EVALUATION_IMAGE_HASH_MISMATCH:"+row.scene_id in errors


def test_duplicate_split_seeds_and_rgb_frames_fail_closed(tmp_path):
    rows=json.loads((SMOKE/"raw"/"render_index.json").read_text(encoding="utf-8"))
    # Introduce collision in a separate temporary manifest, do not edit real dataset.
    rows[1]["seed"]=rows[0]["seed"]
    m=tmp_path/"poison_raw.json"
    m.write_text(json.dumps(rows),encoding="utf-8")
    decision=BlenderVisibleMaskDatasetAssembler().assemble(
        render_index=m,dataset_dir=tmp_path/"derived",
    )
    assert not decision.passed
    assert "TRAIN_VAL_TEST_SCENE_SEED_COLLISION" in decision.blockers


def test_shared_pixel_mask_for_two_actors_is_rejected(tmp_path):
    rows=json.loads((SMOKE/"raw"/"render_index.json").read_text(encoding="utf-8"))
    # Reuse one actor's mask for the other actor in a different manifest only.
    row=rows[0]
    shared=next(iter(row["actor_masks"].values()))
    row["actor_masks"][list(row["actor_masks"])[1]]=shared
    manifest=tmp_path/"bad_masks.json"
    manifest.write_text(json.dumps(rows),encoding="utf-8")
    result=BlenderVisibleMaskDatasetAssembler().assemble(
        render_index=manifest,dataset_dir=tmp_path/"derived",
    )
    assert not result.passed
    assert any("ACTOR_MASKS_OVERLAP" in e for e in result.blockers)


def test_cannot_evaluate_model_selection_on_train_images():
    with pytest.raises(ValueError,match="NON_HELDOUT_SPLIT_EVALUATION_FORBIDDEN"):
        MultiSceneDetectorEvaluator().evaluate_split(
            model=None,dataset_dir=DATA/"dataset",
            split="train",thresholds=(.20,),
        )


def test_v189_production_gate_remains_blocked_without_human_review(mask_qc):
    diag=SimpleNamespace(passed=True,production_qualified=False,
                         generalized_real_video_detection_qualified=False)
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v189_required=True,blender_mask_dataset=mask_qc,
        diverse_scene_detector=diag,independent_human_detector_review=None,
    )
    assert not gate.passed
    assert "REAL_UNSEEN_STYLE_DETECTOR_GENERALIZATION_UNQUALIFIED" in gate.blockers
    assert "INDEPENDENT_HUMAN_ACTOR_LABEL_REVIEW_MISSING" in gate.blockers
    assert "BLENDER_PIXEL_MASK_DATASET_QC_FAILED" not in gate.blockers


def test_v189_missing_input_mandatory_fail_closed():
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v189_required=True,
    )
    assert not gate.passed
    assert "BLENDER_PIXEL_MASK_DATASET_QC_FAILED" in gate.blockers
    assert "DIVERSE_SCENE_HELDOUT_DETECTOR_QC_FAILED" in gate.blockers


def test_v189_company_services_are_attached():
    from cinefactory.appctx import build_context
    context=build_context(ROOT)
    company=context.studio.professional_company
    assert context.blender_mask_dataset_qc is company.blender_mask_dataset_qc
    assert context.multiscene_detector_qc is company.multiscene_detector_qc


def test_v189_actual_training_uses_no_test_images():
    p=DATA/"training_manifest_v189.json"
    if not p.is_file():
        pytest.skip("Training not yet complete")
    manifest=json.loads(p.read_text(encoding="utf-8"))
    assert manifest["train_images"]==96
    assert manifest["val_images"]==24
    assert manifest["test_images_not_seen"]==32
    assert manifest["training_uses_test"] is False
    assert manifest["generalized_actor_detection"] is False
    assert hashlib.sha256(Path(manifest["trained_model"]).read_bytes()).hexdigest()==manifest["trained_sha256"]


def test_v189_heldout_test_threshold_chosen_using_validation_only(release_evidence):
    measured=release_evidence["synthetic_unseen_scene_detector"]
    assert measured["measured"]
    assert measured["selection_rule"]=="VALIDATION_ONLY_MAX_F1_WITH_PRECISION_FLOOR_0_80"
    assert measured["chosen_confidence"] in [.10,.20,.30,.40,.50]
    assert measured["heldout_test"]["split"]=="test"
    assert measured["heldout_test"]["images"]==32
    assert measured["inference_used_target_boxes"] is False
    assert measured["target_ground_truth_source"]=="HELDOUT_PIXEL_RENDERED_ACTOR_MASKS"
    assert not measured["production_qualified"]


def test_v189_synthetic_test_not_equal_general_cinefactory_approval(release_evidence):
    gate=release_evidence["production_gate"]
    assert gate["status"]=="BLOCKED"
    assert not gate["passed"]
    assert "INDEPENDENT_HUMAN_ACTOR_LABEL_REVIEW_MISSING" in gate["blockers"]
    assert not release_evidence["production_qualified"]


def test_heldout_original_cinefactory_video_is_not_train(release_evidence):
    trained=release_evidence["real_existing_cinefactory_blender_video"]
    baseline=release_evidence["previous_v188_detector_same_real_video"]
    assert trained["model_kind"]=="V189_DIVERSE_PROCEDURAL_VOXEL_ON_V186_ACTUAL_BLENDER"
    assert baseline["model_kind"]=="V188_SINGLE_SCENE_MODEL_BASELINE"
    assert trained["measured"] and baseline["measured"]
    assert not trained["general_out_of_domain_actor_detection_verified"]
    assert not trained["production_qualified"]


def test_v189_rejects_fake_human_signoff_without_production_status(mask_qc):
    diag=SimpleNamespace(passed=True,production_qualified=False,
                         generalized_real_video_detection_qualified=False)
    review=SimpleNamespace(approved=True,production_qualified=False)
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v189_required=True,blender_mask_dataset=mask_qc,
        diverse_scene_detector=diag,independent_human_detector_review=review,
    )
    assert not gate.passed
    assert "INDEPENDENT_HUMAN_ACTOR_LABEL_REVIEW_MISSING" in gate.blockers



def test_blender_render_replay_is_pixel_deterministic_even_if_png_bytes_differ():
    import numpy as np
    first=ROOT/"data"/"verification"/"v189_scene_diversity_smoke"/"raw"/"render_index.json"
    second=ROOT/"data"/"verification"/"v189_scene_diversity_replay"/"raw"/"render_index.json"
    if not second.is_file():
        pytest.skip("Controlled Blender replay fixture unavailable")
    a={x["scene_id"]:x for x in json.loads(first.read_text(encoding="utf-8"))}
    b=json.loads(second.read_text(encoding="utf-8"))
    assert len(b)==3
    for row in b:
        source=a[row["scene_id"]]
        pairs=[(source["image"],row["image"])]
        assert set(source["actor_masks"])==set(row["actor_masks"])
        pairs.extend(
            (source["actor_masks"][k],row["actor_masks"][k])
            for k in source["actor_masks"]
        )
        for left,right in pairs:
            pixels_a=cv2.imread(left,cv2.IMREAD_COLOR)
            pixels_b=cv2.imread(right,cv2.IMREAD_COLOR)
            assert pixels_a is not None and pixels_b is not None
            assert np.array_equal(pixels_a,pixels_b)
    # SHA256 is a *file provenance* check, not proof of decoded-pixel equality.


def test_mask_ingestion_normalizes_three_channel_opencv_decode(monkeypatch):
    # Regression: full repository suite can introduce CV adapters which
    # cause imread(IMREAD_GRAYSCALE) to return an HxWx3 frame.
    original=cv2.imread
    def color_backend(path,flags=cv2.IMREAD_COLOR):
        return original(path,cv2.IMREAD_COLOR)
    monkeypatch.setattr(cv2,"imread",color_backend)
    rows=json.loads((SMOKE/"raw"/"render_index.json").read_text(encoding="utf-8"))
    sample,labels,failures=BlenderVisibleMaskDatasetAssembler()._sample(rows[0])
    assert not failures
    assert len(labels)==len(rows[0]["actor_masks"])
    assert all(b.visible_pixel_count>150 for b in sample.boxes)
