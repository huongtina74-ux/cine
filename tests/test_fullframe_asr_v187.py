from __future__ import annotations
"""v1.6.27 real-video, target-sidecar-blind and Windows ASR tests."""
import hashlib
import json
from pathlib import Path

import pytest

from cinefactory.studio.full_frame_actor_search import FullFrameReferenceActorScanner
from cinefactory.studio.independent_speech_asr import OfflineIndependentASR
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"data"/"verification"/"v187_unseeded_video_asr"


@pytest.fixture
def source_target():
    a=ROOT/"data"/"verification"/"v185_alignment_reid"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
    b=ROOT/"data"/"verification"/"v186_multishot_second"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
    assert a.is_file() and b.is_file()
    return a,b


@pytest.fixture
def real_evidence():
    e=EVIDENCE/"v187_qualification_evidence.json"
    assert e.is_file()
    obj=json.loads(e.read_text(encoding="utf-8"))
    assert obj["status"]=="CONTROLLED_REAL_VIDEO_SEARCH_PASS_AUDIO_ASR_QUALIFICATION_PARTIAL_PRODUCTION_BLOCKED"
    return obj


@pytest.fixture
def source_speech():
    source=ROOT/"data"/"verification"/"v185_alignment_reid"/"v185_render_evidence.json"
    return json.loads(source.read_text(encoding="utf-8"))["speech"]


def test_actual_second_render_detected_without_target_boxes(source_target):
    a,b=source_target
    report=FullFrameReferenceActorScanner().scan(source_video=a,target_video=b)
    assert report.passed and report.measured,report.blockers
    assert report.frames==12
    assert len(report.observations)==24
    assert {x.actor_id for x in report.observations}=={"A","B"}
    assert all(x.template_score>.85 for x in report.observations)
    assert all(x.matched for x in report.observations)
    assert report.target_rig_annotations_used_for_detection is False
    assert report.tracking.passed
    assert all(t.matched_frames==12 for t in report.tracking.tracks)
    assert report.production_qualified is False


def test_target_has_no_sidecars_and_detection_still_passes(source_target):
    a,_=source_target
    missing=EVIDENCE/"target_without_sidecars.mp4"
    assert missing.is_file()
    assert not Path(str(missing)+".frame_qc.json").exists()
    assert not Path(str(missing)+".geometry_qc.json").exists()
    report=FullFrameReferenceActorScanner().scan(source_video=a,target_video=missing)
    assert report.passed,report.blockers
    assert not report.target_rig_annotations_used_for_detection


def test_source_reference_requires_labels_but_not_target(source_target):
    _,b=source_target
    without=EVIDENCE/"target_without_sidecars.mp4"
    with pytest.raises(ValueError,match="REFERENCE_FRAME_ANNOTATIONS_MISSING"):
        FullFrameReferenceActorScanner().reference_templates(source_video=without)


def test_research_rig_labels_used_only_after_detection(source_target):
    a,b=source_target
    scanner=FullFrameReferenceActorScanner()
    detection=scanner.scan(source_video=a,target_video=b)
    verdict=scanner.evaluate_rig_ground_truth(detection,b)
    assert verdict.passed,verdict.blockers
    assert verdict.compared_count==24
    assert verdict.minimum_iou>.70
    assert not verdict.production_qualified
    assert verdict.annotation_source=="TARGET_BLENDER_RIG_FRAME_QC_FOR_EVALUATION_ONLY"


def test_unannotated_target_blocks_benchmark_but_not_detection(source_target):
    a,_=source_target
    target=EVIDENCE/"target_without_sidecars.mp4"
    scanner=FullFrameReferenceActorScanner()
    found=scanner.scan(source_video=a,target_video=target)
    assert found.passed
    evaluated=scanner.evaluate_rig_ground_truth(found,target)
    assert not evaluated.passed
    assert "TARGET_RIG_EVALUATION_ANNOTATIONS_MISSING" in evaluated.blockers


def test_real_lookalike_impostor_blocked(source_target):
    a,_=source_target
    impostor=EVIDENCE/"NEGATIVE_second_actor_lookalike.mp4"
    assert impostor.is_file()
    report=FullFrameReferenceActorScanner().scan(
        source_video=a,target_video=impostor,
    )
    assert not report.passed
    assert any("TWO_SIMILAR_SCREEN_ACTOR_CANDIDATES" in x for x in report.blockers)
    assert not report.production_qualified


def test_same_video_not_cross_shot_evidence(source_target):
    a,_=source_target
    with pytest.raises(ValueError,match="IDENTICAL_SOURCE_AND_TARGET_NOT_CROSS_SHOT"):
        FullFrameReferenceActorScanner().scan(source_video=a,target_video=a)


def test_benchmark_refuses_wrong_target_hash(source_target):
    a,b=source_target
    scanner=FullFrameReferenceActorScanner()
    found=scanner.scan(source_video=a,target_video=b)
    with pytest.raises(ValueError,match="TARGET_EVALUATION_HASH_MISMATCH"):
        scanner.evaluate_rig_ground_truth(found,EVIDENCE/"NEGATIVE_second_actor_lookalike.mp4")


def test_asr_real_hello_pass_and_second_low_confidence_fails(real_evidence):
    asr=real_evidence["independent_speech_recognition"]
    assert asr["A"]["passed"]
    assert asr["A"]["independent_text_recognition_verified"]
    assert asr["A"]["recognized_transcript"].casefold()=="hello"
    assert asr["B"]["status"]=="BLOCKED"
    assert not asr["B"]["passed"]
    assert asr["B"]["recognized_transcript"].casefold()=="let's go"
    assert "INDEPENDENT_RECOGNITION_LOW_CONFIDENCE" in asr["B"]["blockers"]
    assert all(not x["phoneme_alignment_verified"] for x in asr.values())
    assert all(not x["independently_forced_aligned"] for x in asr.values())
    assert all(not x["production_qualified"] for x in asr.values())


def test_asr_actual_native_offline_dictation_does_not_get_reference_transcript(source_speech,tmp_path):
    first=source_speech[0]
    observed=OfflineIndependentASR(ROOT).assess(
        source_wav=first["audio_path"],
        source_sha256=first["audio_sha256"],
        expected_transcript=first["text"],
        output_json=tmp_path/"observed.json",
    )
    assert observed.passed and observed.measured
    assert observed.independent_text_recognition_verified
    assert observed.source=="WINDOWS_SYSTEM_SPEECH_RECOGNITION_DICTATION"
    raw=json.loads((tmp_path/"observed.json").read_text(encoding="utf-8"))
    assert raw["transcript_supplied_to_recognizer"] is False
    assert raw["forced_phoneme_alignment_verified"] is False
    assert raw["time_aligned_words_available"] is False


def test_asr_wrong_expected_words_rejected_even_when_audio_recognized(real_evidence):
    rejected=real_evidence["wrong_text_negative"]
    assert not rejected["passed"]
    assert "INDEPENDENT_RECOGNIZED_TEXT_MISMATCH" in rejected["blockers"]


def test_asr_audio_hash_mismatch_fail_closed(source_speech,tmp_path):
    first=source_speech[0]
    with pytest.raises(ValueError,match="INDEPENDENT_ASR_SOURCE_WAV_TAMPERED"):
        OfflineIndependentASR(ROOT).assess(
            source_wav=first["audio_path"],source_sha256="f"*64,
            expected_transcript=first["text"],
            output_json=tmp_path/"unused.json",
        )


def test_asr_audio_missing_fail_closed(tmp_path):
    with pytest.raises(ValueError,match="INDEPENDENT_ASR_WAV_MISSING"):
        OfflineIndependentASR(ROOT).assess(
            source_wav=tmp_path/"missing.wav",source_sha256="0"*64,
            expected_transcript="hello",output_json=tmp_path/"unused.json",
        )


def test_asr_invalid_confidence_floor_rejected():
    with pytest.raises(ValueError,match="ASR_CONFIDENCE_FLOOR_INVALID"):
        OfflineIndependentASR(ROOT,confidence_floor=2.0)


def test_v187_gate_blocks_even_when_full_frame_search_passes(real_evidence):
    from types import SimpleNamespace
    found=SimpleNamespace(passed=True,production_qualified=False)
    asr=[SimpleNamespace(passed=True,production_qualified=False,phoneme_alignment_verified=False),
         SimpleNamespace(passed=False,production_qualified=False,phoneme_alignment_verified=False)]
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,
        identity_required=False,lipsync_required=False,
        v187_required=True,full_frame_actor=found,
        full_frame_annotated_benchmark=found,independent_asr_reports=asr,
    )
    assert not gate.passed
    assert "UNCONSTRAINED_ACTOR_DETECTOR_NOT_QUALIFIED" in gate.blockers
    assert "INDEPENDENT_HUMAN_VIDEO_GROUND_TRUTH_NOT_QUALIFIED" in gate.blockers
    assert "INDEPENDENT_SPEECH_RECOGNITION_FAILED_OR_LOW_CONFIDENCE" in gate.blockers
    assert "INDEPENDENT_FORCED_PHONEME_ALIGNMENT_NOT_QUALIFIED" in gate.blockers
    assert "FULL_FRAME_REFERENCE_ACTOR_TRACKING_FAILED" not in gate.blockers


def test_v187_gate_missing_evidence_never_passes():
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,
        lipsync_required=False,v187_required=True,
    )
    assert not gate.passed
    assert "FULL_FRAME_REFERENCE_ACTOR_TRACKING_FAILED" in gate.blockers
    assert "REAL_VIDEO_FRAME_BENCHMARK_FAILED" in gate.blockers
    assert "INDEPENDENT_SPEECH_RECOGNITION_FAILED_OR_LOW_CONFIDENCE" in gate.blockers


def test_company_exposes_new_diagnostic_services():
    from cinefactory.appctx import build_context
    ctx=build_context(ROOT)
    assert ctx.full_frame_reference_actor is ctx.studio.professional_company.full_frame_reference_actor
    assert ctx.offline_independent_asr is ctx.studio.professional_company.offline_independent_asr


def test_independent_asr_on_final_deliverable_catches_weak_speech(real_evidence):
    results=real_evidence["final_mux_independent_speech_recognition"]
    assert results["A"]["passed"]
    assert results["A"]["confidence"]>=.55
    assert not results["B"]["passed"]
    assert "INDEPENDENT_RECOGNITION_LOW_CONFIDENCE" in results["B"]["blockers"]
    assert results["A"]["recognized_transcript"].lower()=="hello"
    assert results["B"]["recognized_transcript"].lower()=="let's go"
    assert all(not x["phoneme_alignment_verified"] for x in results.values())


def test_negative_swapped_final_audio_is_independently_recognized_and_rejected(real_evidence):
    swapped=real_evidence["voice_swapped_final_mux_asr_negative"]
    assert set(swapped)=={"A","B"}
    assert all(not x["passed"] for x in swapped.values())
    assert all(x["blockers"] for x in swapped.values())


def test_v187_production_gate_rejects_missing_final_mux_asr():
    from types import SimpleNamespace
    good=SimpleNamespace(passed=True,measured=True,production_qualified=False,
                         phoneme_alignment_verified=False)
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v187_required=True,full_frame_actor=good,
        full_frame_annotated_benchmark=good,
        independent_asr_reports=[good,good],
    )
    assert not gate.passed
    assert "FINAL_MUX_INDEPENDENT_SPEECH_RECOGNITION_FAILED" in gate.blockers
    assert "INDEPENDENT_SPEECH_RECOGNITION_FAILED_OR_LOW_CONFIDENCE" not in gate.blockers


def test_actual_gate_evidence_is_fail_closed_even_with_good_detector(real_evidence):
    row=real_evidence["production_gate"]
    assert row["status"]=="BLOCKED"
    assert not row["passed"]
    assert "FINAL_MUX_INDEPENDENT_SPEECH_RECOGNITION_FAILED" in row["blockers"]
    assert "INDEPENDENT_FORCED_PHONEME_ALIGNMENT_NOT_QUALIFIED" in row["blockers"]
    assert "UNCONSTRAINED_ACTOR_DETECTOR_NOT_QUALIFIED" in row["blockers"]
    assert "INDEPENDENT_HUMAN_VIDEO_GROUND_TRUTH_NOT_QUALIFIED" in row["blockers"]
