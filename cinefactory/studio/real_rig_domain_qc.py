from __future__ import annotations
"""v1.6.30 admission: intra-generator heldout is necessary, not sufficient.

Requires heldout CineFactory *existing* rendered production-style classroom
video detection improvement. Independently human reviewed annotations,
mixed-project robustness, safety and licensing still missing for production.
"""
from pydantic import BaseModel,Field
from cinefactory.studio.multiscene_detector_qc import MultiSceneDetectorReport
from cinefactory.studio.trained_actor_detector_qc import TrainedDetectorEvaluation
from cinefactory.studio.blender_mask_dataset_qc import BlenderMaskDatasetQC


class RealRigDomainDecision(BaseModel):
    status:str
    passed:bool
    measured:bool
    production_qualified:bool=False
    ground_truth_is_human_approved:bool=False
    generalization_to_multiple_independent_projects_verified:bool=False
    license_approved_for_commercial_distribution:bool=False
    actual_cinefactory_rig_source_verified:bool
    synthetic_test_precision:float
    synthetic_test_recall:float
    external_video_precision:float
    external_video_recall:float
    baseline_external_recall:float
    external_recall_delta:float
    blockers:list[str]=Field(default_factory=list)


class RealRigDomainAdmissionQC:
    def __init__(self,*,synthetic_precision_floor:float=.80,
                 synthetic_recall_floor:float=.80,
                 external_precision_floor:float=.60,
                 external_recall_floor:float=.60,
                 minimum_recall_improvement:float=.10):
        self.synthetic_precision_floor=synthetic_precision_floor
        self.synthetic_recall_floor=synthetic_recall_floor
        self.external_precision_floor=external_precision_floor
        self.external_recall_floor=external_recall_floor
        self.minimum_recall_improvement=minimum_recall_improvement

    def assess(self,*,dataset:BlenderMaskDatasetQC,
               scene_benchmark:MultiSceneDetectorReport,
               existing_video:TrainedDetectorEvaluation,
               baseline:TrainedDetectorEvaluation,
               source_worker_hash_valid:bool)->RealRigDomainDecision:
        blockers=[]
        if not dataset.passed or dataset.raw_scenes<12:
            blockers.append("REAL_RIG_BLENDER_DATASET_QC_FAILED")
        if not source_worker_hash_valid:
            blockers.append("ACTUAL_FACTORY_RIG_PROVENANCE_NOT_VERIFIED")
        if not scene_benchmark.measured or not scene_benchmark.passed:
            blockers.append("MULTISCENE_ACTUAL_RIG_HELDOUT_TEST_FAILED")
        test=scene_benchmark.heldout_test
        if test.precision<self.synthetic_precision_floor:
            blockers.append("ACTUAL_RIG_SYNTHETIC_TEST_PRECISION_LOW")
        if test.recall<self.synthetic_recall_floor:
            blockers.append("ACTUAL_RIG_SYNTHETIC_TEST_RECALL_LOW")
        if existing_video.model_sha256!=scene_benchmark.model_sha256:
            blockers.append("EXTERNAL_VIDEO_NOT_EVALUATED_WITH_SAME_CHECKPOINT")
        if existing_video.video_sha256!=baseline.video_sha256:
            blockers.append("EXTERNAL_BASELINE_TARGET_VIDEO_MISMATCH")
        if existing_video.model_kind!="V190_REAL_RIG_WORKER_HELDOUT_V186_VIDEO":
            blockers.append("EXTERNAL_MEDIA_PROVENANCE_INVALID")
        if existing_video.precision<self.external_precision_floor:
            blockers.append("REAL_EXTERNAL_CINEFACTORY_VIDEO_PRECISION_LOW")
        if existing_video.recall<self.external_recall_floor:
            blockers.append("REAL_EXTERNAL_CINEFACTORY_VIDEO_RECALL_LOW")
        delta=existing_video.recall-baseline.recall
        if delta<self.minimum_recall_improvement:
            blockers.append("EXTERNAL_VIDEO_RECALL_NOT_IMPROVED_VS_V189")
        return RealRigDomainDecision(
            status="REAL_RIG_EXTERNAL_VIDEO_DIAGNOSTIC_PASS" if not blockers else "BLOCKED",
            passed=not blockers,measured=True,
            actual_cinefactory_rig_source_verified=source_worker_hash_valid,
            synthetic_test_precision=test.precision,
            synthetic_test_recall=test.recall,
            external_video_precision=existing_video.precision,
            external_video_recall=existing_video.recall,
            baseline_external_recall=baseline.recall,
            external_recall_delta=delta,blockers=sorted(set(blockers)),
        )
