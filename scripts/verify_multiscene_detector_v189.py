from __future__ import annotations
"""CineFactory v1.6.29 model test: validation-only confidence selection;
sealed 32-scene TEST; unrelated CineFactory final video comparison;
negative domain examples; mandatory fail-closed production decision.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.blender_mask_dataset_qc import (
    BlenderMaskDatasetQC,BlenderVisibleMaskDatasetAssembler,
)
from cinefactory.studio.multiscene_detector_qc import MultiSceneDetectorEvaluator
from cinefactory.studio.trained_actor_detector_qc import HeldoutActorDetectorEvaluator
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate

OUT=ROOT/"data"/"verification"/"v189_scene_diversity"

def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    reportfile=OUT/"v189_qualification_evidence.json"
    details={"milestone":"v1.6.29","status":"STARTED","production_qualified":False}
    try:
        qc=BlenderMaskDatasetQC.model_validate_json(
            (OUT/"mask_dataset_qc.json").read_text(encoding="utf-8")
        )
        assert qc.passed and qc.raw_scenes==152,qc.blockers
        integrity=BlenderVisibleMaskDatasetAssembler.verify_preinference_integrity(
            dataset_dir=OUT/"dataset",report=qc,
        )
        assert not integrity,integrity
        training=json.loads((OUT/"training_manifest_v189.json").read_text(encoding="utf-8"))
        checkpoint=Path(training["trained_model"])
        assert sha(checkpoint)==training["trained_sha256"]
        assert training["train_data_manifest_sha256"]==qc.manifest_sha256
        assert not training["training_uses_test"]
        model_qc=MultiSceneDetectorEvaluator().evaluate(
            checkpoint=checkpoint,
            dataset_dir=OUT/"dataset",
            dataset_manifest_sha256=qc.manifest_sha256,
        )
        details["dataset_qc"]={
            "passed":qc.passed,"count":qc.raw_scenes,
            "split_counts":qc.split_counts,
            "visible_actor_instances":sum(len(x.boxes) for x in qc.samples),
            "mask_overlap_total":sum(x.mask_overlap_pixels for x in qc.samples),
            "scene_seed_separated":len(set(x.seed for x in qc.samples))==152,
            "integrity_blockers":integrity,
            "raw_render_manifest_sha256":qc.manifest_sha256,
            "synthetic_rig_only":True,
            "human_annotated_ground_truth":False,
        }
        details["training"]=training
        details["synthetic_unseen_scene_detector"]=model_qc.model_dump(mode="json")

        # Real, production-style prior Blender scene, absent from all
        # synthetic training/validation/test renders.
        original=ROOT/"data"/"verification"/"v186_multishot_second"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
        original_gt=Path(str(original)+".frame_qc.json")
        older=ROOT/"data"/"verification"/"v188_acoustic_detector"/"train_runs"/"block_actor_v188"/"weights"/"best.pt"
        assert original.is_file() and original_gt.is_file() and older.is_file()
        original_benchmark=HeldoutActorDetectorEvaluator(
            sample_count=12,
            confidence=model_qc.chosen_confidence,
        ).evaluate(
            weights=checkpoint,target_video=original,
            target_annotations=original_gt,
            model_kind="V189_DIVERSE_PROCEDURAL_VOXEL_ON_V186_ACTUAL_BLENDER",
        )
        old_baseline=HeldoutActorDetectorEvaluator(
            sample_count=12,confidence=.20,
        ).evaluate(
            weights=older,target_video=original,
            target_annotations=original_gt,
            model_kind="V188_SINGLE_SCENE_MODEL_BASELINE",
        )
        details["real_existing_cinefactory_blender_video"]=original_benchmark.model_dump(mode="json")
        details["previous_v188_detector_same_real_video"]=old_baseline.model_dump(mode="json")
        details["generalization_limits"]=[
            "ALL_SYNTHETIC_SET_IMAGES_SHARE_ONE_PROCEDURAL_VOXEL_GENERATOR",
            "UNSEEN_FAMILY_DIFFERS_IN_SEEDS_BACKDROPS_LIGHTING_AND_PALETTE_NOT_SOURCE_ENGINE",
            "NO_HUMAN_APPROVED_MASK_BOUNDARY_GROUND_TRUTH",
            "NO_ROBLOX_R6_OR_WAN_GENERATED_DIVERSE_PRODUCTION_VIDEOS_EVALUATED",
            "ULTRALYTICS_LICENSE_AGPL_COMMERCIAL_TERMS_REQUIRE_REVIEW",
        ]
        # Quality gate intentionally not bypassed by synthetic-only heldout.
        gate=PerformanceQualificationGate.assess(
            temporal=None,sync=None,
            v189_required=True,
            blender_mask_dataset=qc,
            diverse_scene_detector=model_qc,
            independent_human_detector_review=None,
        )
        assert not gate.passed
        details["production_gate"]=gate.model_dump(mode="json")
        details["status"]=(
            "REAL_BLENDER_SYNTHETIC_MASKS_PASS_TEST_"
            + ("PASS" if model_qc.passed else "BLOCKED")
            + "_PRODUCTION_BLOCKED"
        )
        print(json.dumps({
            "status":details["status"],
            "rendered_scenes":qc.raw_scenes,
            "actor_masks":details["dataset_qc"]["visible_actor_instances"],
            "calibration_confidence_val_only":model_qc.chosen_confidence,
            "val_sweep":[{
                "threshold":x.confidence,
                "precision":round(x.precision,4),
                "recall":round(x.recall,4),
            } for x in model_qc.validation_sweep],
            "unseen_test_images":model_qc.heldout_test.images,
            "unseen_test_precision":model_qc.heldout_test.precision,
            "unseen_test_recall":model_qc.heldout_test.recall,
            "unseen_test_f1":model_qc.heldout_test.f1,
            "real_cinefactory_video_recall":original_benchmark.recall,
            "old_baseline_real_video_recall":old_baseline.recall,
            "production_gate":gate.status,
            "evidence":str(reportfile),
        },indent=2))
    except Exception as exc:
        details["status"]="FAILED"
        details["error"]=f"{type(exc).__name__}: {exc}"
        raise
    finally:
        reportfile.write_text(json.dumps(details,indent=2),encoding="utf-8")

if __name__=="__main__":
    main()
