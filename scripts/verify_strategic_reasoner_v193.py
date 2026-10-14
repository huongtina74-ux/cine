from __future__ import annotations
"""Evidence-first v1.6.33 intelligent R&D trials on actual CineFactory artifacts.

Do not confuse output decision JSON with videos created/experiments run.
The only empirical study in these research cycles is v192's real H264
encoding benchmark (not generative quality); learning uses real v190 summary.
"""
import hashlib,json,sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.evidence_reasoning_v193 import (
    CitedResearchSource,ClaimObservation,ClaimDimension,ClaimFinding,SourceKind,
)
from cinefactory.studio.production_selection_council import Stage
from cinefactory.studio.strategic_reasoning_v193 import (
    StrategicResearchReasoner,ReasoningRequest,
)
from cinefactory.studio.scientific_learning_v193 import (
    ScientificLearningBridge,ObservedResearchOutcome,
)

def main():
    out=ROOT/"data"/"verification"/"v193_evidence_reasoning"
    out.mkdir(parents=True,exist_ok=True)
    brain=StrategicResearchReasoner(ROOT,today=date(2026,10,9))
    old=ROOT/"data"/"verification"/"v192_department_research"/"codec_ab"/"codec_ab_evidence_v192.json"
    old_json=json.loads(old.read_text(encoding="utf-8"))
    filehash=hashlib.sha256(old.read_bytes()).hexdigest()
    source=CitedResearchSource(
        source_id="REAL_V192_ENCODE_AB_MANIFEST",
        kind=SourceKind.LOCAL_ARTIFACT,
        locator=str(old.resolve()),publisher_or_owner="CINEFACTORY_LOCAL_ENCODE_LAB",
        observed_on=date(2026,10,9),source_sha256=filehash,
        scope="FFmpeg libx264 CRF21 original v185 90-frame 640x360 already lossy video",
        retrieved_and_inspected=True,independently_verified=False,
        license_approved_for_commercial_use=False,
    )
    assert len(old_json["candidates"])==3
    samples={v["preset"]:v for v in old_json["candidates"]}
    assert all(x["decoded_video_frames"]==90 for x in samples.values())
    question="x264 CRF21 veryfast 90-frame encoded bitrate and speed on v185 H264 CineFactory source"
    observation=ClaimObservation(
        claim_id="V192_ACTUAL_CODEC_SPEED_OBSERVED",
        subject_method_id="ffmpeg.x264.veryfast",
        niche_id="minecraft",stage=Stage.EDITORIAL,
        dimension=ClaimDimension.SPEED,
        finding=ClaimFinding.SUPPORTS,
        source_ids=[source.source_id],
        description=(
            f"Measured veryfast {samples['veryfast']['ffmpeg_wallclock_seconds']:.4f}s"
            f", medium {samples['medium']['ffmpeg_wallclock_seconds']:.4f}s"
            " for 90 compressed frames; not proof for 4K, artistic quality or future runs."
        ),exact_scoped_question=question,observed_scope=question,
        direct_empirical_measurement=True,
        linked_benchmark_manifest=str(old.resolve()),
    )
    runs={
        "preschool":brain.deliberate(ReasoningRequest(
            project_id="PRESCHOOL_ORIGINAL_RHYME_RND",
            niche_id="preschool_3d_musical",
            script_text="Scene 1: Original child sings an alphabet song and dances.\nScene 2: Letters appear and singer waves in time.",
            source_rights_cleared=False,made_for_kids=True,max_research_tasks=8,
            max_paid_api_usd=0,budget_usd_for_experiments=0.,
        )),
        "long_slices":brain.deliberate(ReasoningRequest(
            project_id="LONGSLIDE_PHYSICS_RND",niche_id="long_slices_game",
            project_brief="Original animal slide game with obstacle physics and camera tracking",
            source_rights_cleared=False,max_research_tasks=5)),
        "new_unknown_niche":brain.deliberate(ReasoningRequest(
            project_id="UNKNOWN_NEW_NICHE_RND",niche_id="ai_microphysics_documentary_unknown",
            project_brief="Original micro-scale matter and science 3D video",
            source_rights_cleared=True,max_research_tasks=4)),
        "real_codec_evidence":brain.deliberate(ReasoningRequest(
            project_id="CODEC_AB_EVIDENCE_RND",niche_id="minecraft",
            project_brief="Encoder decisions based on measured 90-frame video",
            source_rights_cleared=True,max_research_tasks=4),
            sources=[source],claims=[observation]),
    }
    for label,record in runs.items():
        (out/(label+"_reasoning.json")).write_text(
            record.model_dump_json(indent=2),encoding="utf-8")
        print("REASONER_CASE",label,
              "status",record.status,
              "priority_queue",len(record.experiment_priority_queue),
              "critics",len(record.specialists),
              "contradictions",sum(x.status=="CONFLICT_REQUIRES_TEST" for x in record.experimental_claim_verdicts),
              "autonomous_production",record.production_qualified,flush=True)
    previous=ROOT/"data"/"verification"/"v190_real_rig_dataset"/"v190_qualification_evidence.json"
    v190=json.loads(previous.read_text(encoding="utf-8"))
    assert v190["unseen_existing_cinefactory_video"]["recall"]==1.0
    learning=ScientificLearningBridge().prepare(ObservedResearchOutcome(
        experiment_id="V190_REAL_RIG_DETECTOR_VS_V189",
        niche_id="minecraft",scope="STUDIO",
        claim="Train on real rig occlusion scenes instead of proxy voxel may improve on one heldout v186 video",
        result_summary="V190 video 12 sampled frames 100% recall vs v189 0% on same v186 clip (one project; no independent ground truth reviewer).",
        control={"model_family":"v189","train_domain":"simple_voxel_proxies"},
        challenger={"model_family":"v190","train_domain":"real_worker_seated_occluded"},
        causal_claim=False,
        evidence_refs=[str(previous.resolve())],
        sample_project_ids=["V186_SINGLE_PROJECT"],
        independent_review_passed=False,regression_passed=True,
        license_cleared=False,confidence=.60,
        verified_metric_not_synthetic=True,
    ))
    (out/"scientific_learning_candidate_v193.json").write_text(
        learning.model_dump_json(indent=2),encoding="utf-8")
    assert not learning.ready_for_production_promotion
    assert not learning.learning_policy_eligible
    summary={
        "status":"ADVISORY_REASONING_AND_SCIENTIFIC_LEARNING_EVIDENCE_PASS",
        "version":"v1.6.33",
        "cases":{name:{
            "status":r.status,"tasks_proposed_not_executed":len(r.experiment_priority_queue),
            "deferred":len(r.postponed_task_ids),
            "source_claims_audited":len(r.experimental_claim_verdicts),
            "production_qualified":r.production_qualified,
            "active_model_reasoner_connected":r.active_model_reasoner_connected,
            "live_internet_research_performed":r.live_internet_research_performed,
        } for name,r in runs.items()},
        "real_codec_source_sha256":filehash,
        "learning_production_eligible":False,
        "paid_api_or_external_exec_performed":False,
        "user_generated_assets_modified":False,
    }
    (out/"reasoning_summary_v193.json").write_text(
        json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2),flush=True)

if __name__=="__main__":main()
