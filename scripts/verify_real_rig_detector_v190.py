from __future__ import annotations
"""v1.6.30 controlled scene holdout AND v186 existing rendered video test.

No uses of v186 nor test data for training/checkpoint selection/calibration.
Video ground truth is rig-projected after inference, NOT human-approved.
"""
import hashlib,json,sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.blender_mask_dataset_qc import (
    BlenderMaskDatasetQC,BlenderVisibleMaskDatasetAssembler,
)
from cinefactory.studio.multiscene_detector_qc import MultiSceneDetectorEvaluator
from cinefactory.studio.trained_actor_detector_qc import HeldoutActorDetectorEvaluator
from cinefactory.studio.real_rig_domain_qc import RealRigDomainAdmissionQC
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate

OUT=ROOT/"data"/"verification"/"v190_real_rig_dataset"

def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def main():
    outfile=OUT/"v190_qualification_evidence.json"
    evidence={"milestone":"v1.6.30","status":"STARTED","production_qualified":False}
    try:
        dataset=BlenderMaskDatasetQC.model_validate_json(
            (OUT/"mask_dataset_qc.json").read_text(encoding="utf-8"))
        assert dataset.passed and dataset.raw_scenes==114
        changes=BlenderVisibleMaskDatasetAssembler.verify_preinference_integrity(
            dataset_dir=OUT/"dataset",report=dataset)
        if changes:raise RuntimeError("V190_PREINFERENCE_DATASET_CHANGED:"+str(changes[:5]))
        train=json.loads((OUT/"training_manifest_v190.json").read_text(encoding="utf-8"))
        weights=Path(train["model_path"])
        original=ROOT/"scripts"/"blender_animation_worker.py"
        snap=OUT/"rig_snapshot_v190.json"
        assert train["model_sha256"]==sha(weights)
        assert train["real_worker_sha256"]==sha(original)
        assert train["scene_rig_manifest_sha256"]==sha(snap)
        assert train["mask_dataset_manifest_sha256"]==dataset.manifest_sha256
        assert train["training_uses_test"] is False
        assert train["training_uses_v186_external_video"] is False
        scene_benchmark=MultiSceneDetectorEvaluator().evaluate(
            checkpoint=weights,dataset_dir=OUT/"dataset",
            dataset_manifest_sha256=dataset.manifest_sha256,
        )
        external=ROOT/"data"/"verification"/"v186_multishot_second"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
        gt=Path(str(external)+".frame_qc.json")
        baseline=ROOT/"data"/"verification"/"v189_scene_diversity"/"model_runs"/"v189_multiscene"/"weights"/"best.pt"
        assert weights.is_file() and external.is_file() and gt.is_file() and baseline.is_file()
        # Validation threshold is LOCKED before touching external video.
        q=HeldoutActorDetectorEvaluator(sample_count=12,
            confidence=scene_benchmark.chosen_confidence,
            iou_floor=.50,precision_floor=.80,recall_floor=.80)
        real=q.evaluate(weights=weights,target_video=external,
            target_annotations=gt,model_kind="V190_REAL_RIG_WORKER_HELDOUT_V186_VIDEO")
        previous=q.evaluate(weights=baseline,target_video=external,
            target_annotations=gt,model_kind="V189_PROCEDURAL_VOXEL_PREVIOUS_BASELINE")
        admitted=RealRigDomainAdmissionQC().assess(
            dataset=dataset,scene_benchmark=scene_benchmark,
            existing_video=real,baseline=previous,
            source_worker_hash_valid=True,
        )
        records=json.loads((OUT/"raw"/"render_index.json").read_text(encoding="utf-8"))
        per_split={}
        for split in ("train","val","test"):
            subset=[r for r in records if r["split"]==split]
            per_split[split]={
                "scenes":len(subset),
                "rig_families":dict(Counter(r["rig_family"] for r in subset)),
                "postures":dict(Counter(y for x in subset for y in x["postures"].values())),
                "lighting":dict(Counter(r["lighting_family"] for r in subset)),
                "camera_groups":dict(Counter(r["camera_family"] for r in subset)),
            }
        evidence["dataset"]={
            "passed":dataset.passed,"scenes":dataset.raw_scenes,
            "total_actor_masks":sum(len(s.boxes) for s in dataset.samples),
            "split_counts":dataset.split_counts,
            "overlapping_mask_pixels":sum(s.mask_overlap_pixels for s in dataset.samples),
            "dataset_lineage_hash":dataset.manifest_sha256,
            "anti_tamper_findings":changes,
            "sourced_from_actual_cinefactory_worker":True,
            "human_labels_verified":False,
            "per_split":per_split,
        }
        evidence["trained_model"]=train
        evidence["sealed_holdout_render"]=scene_benchmark.model_dump(mode="json")
        evidence["unseen_existing_cinefactory_video"]=real.model_dump(mode="json")
        evidence["previous_v189_model_same_video"]=previous.model_dump(mode="json")
        evidence["real_domain_admission"]=admitted.model_dump(mode="json")
        # No human reviewer may be fabricated or inferred from benchmark.
        gate=PerformanceQualificationGate.assess(
            temporal=None,sync=None,v190_required=True,
            actual_rig_dataset=dataset,real_rig_domain=admitted,
            human_approved_dataset=None,
        )
        evidence["production_gate"]=gate.model_dump(mode="json")
        assert not gate.passed
        evidence["known_limits"]=[
            "CINEFACTORY_REAL_WORKER_RIGS_AND_SCENES_YET_WORKBENCH_DIAGNOSTIC_RENDER",
            "TEST_CAMERA_SEEDS_HELD_OUT_BUT_ALL_GENERATED_FROM_SAME_BLENDER_WORKER",
            "VIDEO_V186_GROUND_TRUTH_RIG_BBOX_NOT_HUMAN_MASK_ANNOTATION",
            "PENDING_MULTI_EPISODE_MULTI_CAMERA_PRODUCTION_STYLE_CONSISTENCY_QC",
            "ULTRALYTICS_AGPL_COMMERCIAL_LICENSE_REVIEW_REQUIRED",
            "GENERALIZED_ROBLOX_AND_EXTERNAL_AI_VIDEO_TESTS_NOT_VERIFIED",
        ]
        evidence["status"]=(
            "ACTUAL_WORKER_RIG_DATASET_PASS_SYNTHETIC_HELDOUT_"
            + ("PASS" if scene_benchmark.passed else "BLOCKED")
            + "_EXTERNAL_VIDEO_"
            + ("PASS" if admitted.passed else "BLOCKED")
            + "_PRODUCTION_BLOCKED"
        )
        print(json.dumps({
            "milestone":"v1.6.30",
            "status":evidence["status"],
            "train_val_test":dataset.split_counts,
            "mask_instances":evidence["dataset"]["total_actor_masks"],
            "validated_confidence":scene_benchmark.chosen_confidence,
            "heldout_test_precision":scene_benchmark.heldout_test.precision,
            "heldout_test_recall":scene_benchmark.heldout_test.recall,
            "original_v186_precision":real.precision,
            "original_v186_recall":real.recall,
            "v189_baseline_external_recall":previous.recall,
            "improvement_recall":admitted.external_recall_delta,
            "admission":admitted.status,
            "production":gate.status,
            "report":str(outfile),
        },indent=2),flush=True)
    except Exception as exc:
        evidence["status"]="FAILED"
        evidence["error"]=f"{type(exc).__name__}: {exc}"
        raise
    finally:
        outfile.write_text(json.dumps(evidence,indent=2),encoding="utf-8")

if __name__=="__main__":main()
