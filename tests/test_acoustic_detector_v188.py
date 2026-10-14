from __future__ import annotations
"""v1.6.28 acoustic HMM forced phoneme timings and model-candidate release veto."""
import hashlib
import json
import wave
from pathlib import Path
from types import SimpleNamespace

import pytest

from cinefactory.studio.acoustic_forced_alignment import PocketSphinxAcousticAligner
from cinefactory.studio.phoneme_video_proxy_qc import PhonemeVideoProxyQC
from cinefactory.studio.rendered_mouth_qc import RenderedMouthProjectionQC,RenderedMouthSample
from cinefactory.studio.trained_actor_detector_qc import HeldoutActorDetectorEvaluator
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate

ROOT=Path(__file__).resolve().parents[1]
V185=ROOT/"data"/"verification"/"v185_alignment_reid"
V188=ROOT/"data"/"verification"/"v188_acoustic_detector"


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@pytest.fixture
def render_source():
    return json.loads((V185/"v185_render_evidence.json").read_text(encoding="utf-8"))


@pytest.fixture
def evidence():
    path=V188/"v188_qualification_evidence.json"
    assert path.is_file()
    report=json.loads(path.read_text(encoding="utf-8"))
    assert report["status"].startswith("REAL_ACOUSTIC_ALIGNMENT_PASS_")
    return report


@pytest.fixture
def aligner():
    return PocketSphinxAcousticAligner(ROOT)


def test_real_wav_acoustic_phone_alignment_both_actors(aligner,render_source):
    count={}
    for track in render_source["speech"]:
        result=aligner.align(
            audio_path=track["audio_path"],
            audio_sha256=track["audio_sha256"],transcript=track["text"],
        )
        count[track["actor_id"]]=len(result.phones)
        assert result.passed and result.measured
        assert result.independent_audio_acoustic_timing
        assert result.transcript_conditioned
        assert not result.independent_phoneme_recognition_verified
        assert not result.production_qualified
        assert all(0<=s.start_seconds<s.end_seconds<result.audio_seconds+.08
                   for s in result.phones)
    assert count=={"A":4,"B":6}


def test_real_final_mux_acoustic_phones_have_actual_timestamps(aligner,render_source):
    reports={}
    for line in render_source["speech"]:
        actor=line["actor_id"]
        path=V188/(actor+"_FINAL_MUX_AUDIO.wav")
        assert path.is_file()
        r=aligner.align(audio_path=path,audio_sha256=digest(path),
                        transcript=line["text"])
        reports[actor]=r
        assert r.passed
        assert all(s.phone.isupper() for s in r.phones)
    assert [row.word for row in reports["B"].words]==["let's","go"]


def test_aligner_rejects_tampered_audio_sha(aligner,render_source):
    s=render_source["speech"][0]
    with pytest.raises(ValueError,match="ACOUSTIC_ALIGNMENT_SHA256_MISMATCH"):
        aligner.align(audio_path=s["audio_path"],audio_sha256="0"*64,
                      transcript=s["text"])


def test_aligner_rejects_unknown_word(aligner,render_source):
    s=render_source["speech"][0]
    result=aligner.align(audio_path=s["audio_path"],
                         audio_sha256=s["audio_sha256"],
                         transcript="zzzzzunlikelywordhere")
    assert not result.passed
    assert any("ALIGNMENT_DICTIONARY_WORD_UNKNOWN:" in x for x in result.blockers)


def test_aligner_rejects_real_silent_wav(aligner):
    source=V188/"NEGATIVE_SILENCE.wav"
    assert source.is_file()
    result=aligner.align(audio_path=source,
                         audio_sha256=digest(source),transcript="hello")
    assert not result.passed
    assert "ACOUSTIC_ALIGNMENT_AUDIO_SILENT" in result.blockers


def test_aligner_rejects_missing_wav(aligner,tmp_path):
    with pytest.raises(ValueError,match="ACOUSTIC_ALIGNMENT_AUDIO_MISSING"):
        aligner.align(audio_path=tmp_path/"missing.wav",
                      audio_sha256="0"*64,transcript="hello")


def test_aligner_rejects_empty_words(aligner,render_source):
    s=render_source["speech"][0]
    report=aligner.align(audio_path=s["audio_path"],
                         audio_sha256=s["audio_sha256"],transcript="???")
    assert not report.passed
    assert "ACOUSTIC_ALIGNMENT_TRANSCRIPT_EMPTY" in report.blockers


def test_phone_video_real_pixel_correlation_and_shift_negative(evidence):
    real=evidence["real_mp4_phone_to_pixel_envelope"]
    shifted=evidence["misaligned_350ms_negative"]
    assert real["passed"]
    assert real["independent_acoustic_phone_timings"]
    assert not real["phoneme_shapes_independently_validated"]
    assert all(row["correlation_zero_lag"]>.55 for row in real["checks"])
    assert not shifted["passed"]
    assert any("PHONEME_VIDEO_PROXY_CORRELATION_LOW" in x for x in shifted["blockers"])


def test_actual_phone_image_verifier_does_not_optimize_lag(aligner,render_source):
    shot=Path(render_source["blender"]["path"])
    side=json.loads(Path(str(shot)+".geometry_qc.json").read_text(encoding="utf-8"))
    projections=[RenderedMouthSample.model_validate(x) for x in side["mouth_projection"]]
    pixels=RenderedMouthProjectionQC().evaluate(
        video_path=render_source["speech_video"]["path"],samples=projections,
    )
    assert pixels.passed
    reports={}
    starts={}
    for q in render_source["speech"]:
        actor=q["actor_id"]
        audio=V188/(actor+"_FINAL_MUX_AUDIO.wav")
        reports[actor]=aligner.align(
            audio_path=audio,audio_sha256=digest(audio),transcript=q["text"],
        )
        starts[actor]=q["line_start_seconds"]
    verifier=PhonemeVideoProxyQC()
    true=verifier.verify(pixel=pixels,projections=projections,
                         alignments=reports,audio_start_seconds=starts)
    offset=verifier.verify(pixel=pixels,projections=projections,
                           alignments=reports,audio_start_seconds=starts,
                           shift_seconds=.35)
    assert true.passed,true.blockers
    assert not offset.passed
    assert not true.production_qualified


def test_acoustic_model_disclaimer_not_independent_phone_identity(evidence):
    for x in evidence["final_mux_acoustic_word_phone_alignment"].values():
        assert x["alignment_method"]=="POCKETSPHINX_EN_US_HMM_TWO_PASS_LEXICON_CONDITIONED"
        assert x["phone_labels_from_lexicon"]
        assert x["transcript_conditioned"]
        assert not x["independent_phoneme_recognition_verified"]
        assert not x["visual_phoneme_sync_verified"]


def test_coco_pretrained_person_model_fails_block_characters(evidence):
    baseline=evidence["coco_zero_shot_block_actor_benchmark"]
    assert not baseline["passed"]
    assert baseline["recall"]<.85
    assert baseline["model_kind"]=="COCO_PRETRAINED_PERSON_ONLY"
    assert not baseline["production_qualified"]


def test_domain_adaptation_candidate_does_not_claim_generalization(evidence):
    candidate=evidence["domain_adapter_heldout_second_render_benchmark"]
    manifest=evidence["training_manifest"]
    assert candidate["measured"]
    assert candidate["frames"]>=10
    assert candidate["target_ground_truth"]=="BLENDER_RIG_LABELS_EVALUATION_ONLY"
    assert not candidate["target_actor_labels_used_for_inference"]
    assert not candidate["production_qualified"]
    assert not candidate["general_out_of_domain_actor_detection_verified"]
    assert manifest["train_source_sha256"]!=manifest["heldout_second_video_sha256"]
    assert manifest["same_scene_and_character_rigs"]
    assert not manifest["generalized_actor_detector"]


def test_trained_candidate_model_weights_integrity(evidence):
    record=evidence["training_manifest"]
    assert digest(record["model_path"])==record["model_sha256"]
    assert record["train_images"]>=40
    assert record["in_source_validation_images"]>=10
    assert record["image_size"]==320
    assert record["epochs_requested"]==10


def test_trained_actor_evaluation_reproducible(evidence):
    from cinefactory.studio.trained_actor_detector_qc import HeldoutActorDetectorEvaluator
    rec=evidence["training_manifest"]
    scene=ROOT/"data"/"verification"/"v186_multishot_second"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
    report=HeldoutActorDetectorEvaluator(sample_count=4,confidence=.20).evaluate(
        weights=rec["model_path"],target_video=scene,
        target_annotations=Path(str(scene)+".frame_qc.json"),
        model_kind="BLENDER_FIRST_SHOT_FINETUNED_BLOCK_ACTOR",
    )
    assert report.measured
    assert report.frames==4
    assert not report.production_qualified
    assert report.model_sha256==rec["model_sha256"]


def test_v188_release_gate_requires_far_more_than_acoustic_timing():
    aligned=SimpleNamespace(passed=True,independent_audio_acoustic_timing=True,
          independent_phoneme_recognition_verified=False,production_qualified=False)
    diagnostic=SimpleNamespace(passed=True,phoneme_shapes_independently_validated=False,
          general_out_of_domain_actor_detection_verified=False,production_qualified=False)
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v188_required=True,phoneme_audio={"A":aligned,"B":aligned},
        phoneme_video_proxy=diagnostic,trained_actor_detector=diagnostic,
    )
    assert not gate.passed
    assert "LEXICON_CONDITIONED_PHONEME_GROUND_TRUTH_UNQUALIFIED" in gate.blockers
    assert "PHONEME_TO_MOUTH_SHAPES_NOT_HUMAN_VALIDATED" in gate.blockers
    assert "CROSS_DOMAIN_ACTOR_DETECTION_NOT_QUALIFIED" in gate.blockers
    assert "REAL_AUDIO_ACOUSTIC_PHONE_ALIGNMENT_FAILED" not in gate.blockers


def test_v188_gate_all_missing_blocked():
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,
        lipsync_required=False,v188_required=True,
    )
    assert not gate.passed
    assert "REAL_AUDIO_ACOUSTIC_PHONE_ALIGNMENT_FAILED" in gate.blockers
    assert "ACOUSTIC_PHONE_PIXEL_MOUTH_PROXY_FAILED" in gate.blockers
    assert "TRAINED_HELDOUT_ACTOR_DETECTOR_FAILED" in gate.blockers


def test_company_exposes_v188_services_as_same_instances():
    from cinefactory.appctx import build_context
    c=build_context(ROOT)
    co=c.studio.professional_company
    assert c.acoustic_forced_alignment is co.acoustic_forced_alignment
    assert c.phoneme_video_proxy_qc is co.phoneme_video_proxy_qc
    assert c.trained_actor_detector_qc is co.trained_actor_detector_qc


def test_latest_release_decision_remains_blocked(evidence):
    assert "PRODUCTION_BLOCKED" in evidence["status"]
    assert not evidence["global_production_gate"]["passed"]
    assert evidence["global_production_gate"]["status"]=="BLOCKED"
    assert evidence["production_qualified"] is False


def test_wrong_known_word_can_be_forced_to_unrelated_audio_and_must_not_certify(evidence):
    negative=evidence["wrong_but_dictionary_valid_transcript_control"]
    assert negative["actual_spoken_text"]=="Hello!"
    assert negative["wrong_text"]=="go"
    assert negative["forced_decoder_accepted_wrong_text"]
    assert "CONDITIONED" in negative["significance"]
    assert evidence["independent_content_recognition_checks"]["source_passed"]==[True,False]


def test_v188_mandatory_separate_asr_verification(evidence):
    from types import SimpleNamespace
    aligned=SimpleNamespace(passed=True,independent_audio_acoustic_timing=True,
            independent_phoneme_recognition_verified=False,production_qualified=False)
    diag=SimpleNamespace(passed=True,phoneme_shapes_independently_validated=False,
            general_out_of_domain_actor_detection_verified=False,production_qualified=False)
    insufficient=SimpleNamespace(passed=False,production_qualified=False)
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v188_required=True,phoneme_audio={"A":aligned,"B":aligned},
        phoneme_video_proxy=diag,trained_actor_detector=diag,
        independent_asr_reports=[diag,insufficient],
        final_mux_asr_reports=[diag,insufficient],
    )
    assert "ACOUSTIC_ALIGNMENT_SOURCE_ASR_INDEPENDENCE_NOT_VERIFIED" in gate.blockers
    assert "ACOUSTIC_ALIGNMENT_FINAL_ASR_INDEPENDENCE_NOT_VERIFIED" in gate.blockers
    assert not gate.passed


def test_actual_v188_gate_catches_asr_unqualified_and_detector_failure(evidence):
    blockers=evidence["global_production_gate"]["blockers"]
    assert "ACOUSTIC_ALIGNMENT_SOURCE_ASR_INDEPENDENCE_NOT_VERIFIED" in blockers
    assert "ACOUSTIC_ALIGNMENT_FINAL_ASR_INDEPENDENCE_NOT_VERIFIED" in blockers
    assert "TRAINED_HELDOUT_ACTOR_DETECTOR_FAILED" in blockers
    assert "LEXICON_CONDITIONED_PHONEME_GROUND_TRUTH_UNQUALIFIED" in blockers
    assert "PHONEME_TO_MOUTH_SHAPES_NOT_HUMAN_VALIDATED" in blockers
