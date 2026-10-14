from __future__ import annotations

"""v1.6.26 diagnostic qualification, real media and adversarial veto tests."""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
import pytest
from pydantic import ValidationError

from cinefactory.studio.source_speaker_attribution import (
    ActorVoiceStem,SourceConditionedSpeakerVerifier,
)
from cinefactory.studio.face_mouth_observability import (
    ActorFaceSearch,FacePatchMotionMouthDetector,
)
from cinefactory.studio.multishot_render_identity import (
    TwoShotImageIdentityVerifier,
)
from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"verification"


@pytest.fixture
def proof():
    path=DATA/"v186_real_speaker_face_multishot"/"v186_qualification_evidence.json"
    if not path.is_file():
        pytest.skip("On-device real v186 verification artifact missing")
    row=json.loads(path.read_text(encoding="utf-8"))
    assert row["status"]=="REAL_DIAGNOSTICS_AND_NEGATIVE_CONTROLS_PASS_PRODUCTION_BLOCKED"
    return row


@pytest.fixture
def original():
    path=DATA/"v185_alignment_reid"/"v185_render_evidence.json"
    if not path.is_file():
        pytest.skip("On-device v185 render missing")
    row=json.loads(path.read_text(encoding="utf-8"))
    for key in ("blender","speech_video"):
        assert hashlib.sha256(Path(row[key]["path"]).read_bytes()).hexdigest()==row[key]["sha256"]
    return row


def stems(original):
    return [ActorVoiceStem(
        actor_id=s["actor_id"],line_id=s["line_id"],
        source_wav=s["audio_path"],source_sha256=s["audio_sha256"],
        start_seconds=s["line_start_seconds"],
        end_seconds=s["line_start_seconds"]+s["audio_duration_seconds"],
    ) for s in original["speech"]]


def actor_boxes(original):
    video=Path(original["blender"]["path"])
    side=json.loads(Path(str(video)+".frame_qc.json").read_text(encoding="utf-8"))
    result=[]
    for s in original["speech"]:
        box=side["actors"][s["actor_id"]]["screen_box"]
        result.append(ActorFaceSearch(
            line_id=s["line_id"],actor_id=s["actor_id"],
            actor_box_top_left={
                "x0":box["x0"],"x1":box["x1"],
                "y0":1-box["y1"],"y1":1-box["y0"],
            },
            start_seconds=s["line_start_seconds"],
            end_seconds=s["line_start_seconds"]+s["audio_duration_seconds"],
        ))
    return result


def test_speaker_matches_final_mp4_with_known_source_stems(original):
    report=SourceConditionedSpeakerVerifier().verify(
        media_path=original["speech_video"]["path"],stems=stems(original),
    )
    assert report.passed and report.measured
    assert len(report.checks)==2
    assert all(c.score>.95 and c.margin>.2 for c in report.checks)
    assert not report.independent_diarization_verified
    assert not report.production_qualified


def test_real_swapped_audio_control_must_fail(original,proof):
    media=DATA/"v186_real_speaker_face_multishot"/"NEGATIVE_swapped_voices.mp4"
    report=SourceConditionedSpeakerVerifier().verify(
        media_path=media,stems=stems(original),
    )
    assert not report.passed and report.blockers
    assert report.status=="BLOCKED"


def test_source_hash_tampering_blocks_actor_voice(original):
    rows=stems(original)
    rows[0]=rows[0].model_copy(update={"source_sha256":"0"*64})
    report=SourceConditionedSpeakerVerifier().verify(
        media_path=original["speech_video"]["path"],stems=rows,
    )
    assert not report.passed
    assert "SOURCE_STEM_HASH_MISMATCH" in report.blockers


def test_voice_line_overlap_rejected(original):
    rows=stems(original)
    rows[1]=rows[1].model_copy(update={
        "start_seconds":rows[0].end_seconds-.3,
    })
    report=SourceConditionedSpeakerVerifier().verify(
        media_path=original["speech_video"]["path"],stems=rows,
    )
    assert "OVERLAPPING_SPEAKERS_UNATTRIBUTABLE" in report.blockers


def test_speaker_stems_missing_or_duplicate(original):
    svc=SourceConditionedSpeakerVerifier()
    empty=svc.verify(media_path=original["speech_video"]["path"],stems=[])
    assert not empty.passed
    first=stems(original)[0]
    duplicated=svc.verify(
        media_path=original["speech_video"]["path"],stems=[first,first],
    )
    assert not duplicated.passed


def test_real_image_localizes_mouth_without_using_mouth_mesh_projection(original):
    items=actor_boxes(original)
    report=FacePatchMotionMouthDetector().evaluate(
        media_path=original["speech_video"]["path"],searches=items,
    )
    assert report.passed and report.measured
    assert len(report.candidates)==2
    assert all(c.motion_pixel_count>90 for c in report.candidates)
    assert all(c.detector_provenance=="FACE_PATCH_TEMPORAL_VARIANCE" for c in report.candidates)
    assert not report.independent_face_landmarks_verified
    assert not report.production_qualified


def test_frozen_face_frames_negative_control_fails(original,proof):
    media=DATA/"v186_real_speaker_face_multishot"/"NEGATIVE_frozen_mouth.mp4"
    report=FacePatchMotionMouthDetector().evaluate(
        media_path=media,searches=actor_boxes(original),
    )
    assert not report.passed
    assert any("NO_STABLE_MOVING_FACE_COMPONENT" in x for x in report.blockers)


def test_face_search_rejects_invalid_actor_boxes():
    with pytest.raises(ValidationError,match="ACTOR_BOX_INVALID"):
        ActorFaceSearch(
            actor_id="A",line_id="L",start_seconds=.1,end_seconds=1.1,
            actor_box_top_left={"x0":.7,"x1":.2,"y0":.1,"y1":.2},
        )


def test_wrong_tiny_face_roi_blocks_signal(original):
    row=actor_boxes(original)[0]
    small=row.model_copy(update={
        "actor_box_top_left":{"x0":.2,"x1":.21,"y0":.3,"y1":.31},
    })
    result=FacePatchMotionMouthDetector().evaluate(
        media_path=original["speech_video"]["path"],searches=[small],
    )
    assert not result.passed
    assert result.status=="BLOCKED"
    assert any("FACE_CROP_BELOW_PIXEL_FLOOR" in x for x in result.blockers)


def test_actual_second_blender_shot_is_not_same_file(original):
    second=DATA/"v186_multishot_second"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
    assert second.is_file()
    report=TwoShotImageIdentityVerifier().compare(
        first_video=original["blender"]["path"],second_video=second,
    )
    assert report.passed and len(report.matches)==2
    assert all(c.score_margin>.08 for c in report.matches)
    assert report.shot_video_hashes[0]!=report.shot_video_hashes[1]
    assert not report.production_qualified


def test_swapped_actor_appearance_is_rejected(original):
    second=DATA/"v186_multishot_second"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
    other=json.loads(Path(str(second)+".frame_qc.json").read_text(encoding="utf-8"))["actors"]
    report=TwoShotImageIdentityVerifier().compare(
        first_video=original["blender"]["path"],second_video=second,
        second_override={"A":other["B"],"B":other["A"]},
    )
    assert not report.passed
    assert any("CROSS_SHOT_ACTOR" in e for e in report.blockers)


def test_duplicate_video_not_multishot_evidence(original):
    source=original["blender"]["path"]
    report=TwoShotImageIdentityVerifier().compare(
        first_video=source,second_video=source,
    )
    assert not report.passed
    assert "TWO_DISTINCT_RENDER_FILES_REQUIRED" in report.blockers


def test_distinct_actor_wrong_hist_shape_is_rejected(original):
    second=DATA/"v186_multishot_second"/"blender"/"renders"/"block_animation"/"shots"/"0000_SPEAKERS_AB.mp4"
    other=json.loads(Path(str(second)+".frame_qc.json").read_text(encoding="utf-8"))["actors"]
    tampered={k:dict(v) for k,v in other.items()}
    tampered["A"]["hsv_histogram"]=[1.]
    with pytest.raises(ValueError,match="RENDER_ACTOR_HIST_INVALID"):
        TwoShotImageIdentityVerifier().compare(
            first_video=original["blender"]["path"],second_video=second,
            second_override=tampered,
        )


def test_corporate_services_attached_to_same_context():
    from cinefactory.appctx import build_context
    ctx=build_context(ROOT)
    company=ctx.studio.professional_company
    assert company.speaker_stem_qc is ctx.speaker_stem_qc
    assert company.image_mouth_observability is ctx.image_mouth_observability
    assert company.multishot_render_identity is ctx.multishot_render_identity


def test_v186_diagnostic_pass_must_not_unlock_production(original):
    from cinefactory.studio.source_speaker_attribution import SourceSpeakerReport
    from cinefactory.studio.face_mouth_observability import ImageMouthObservabilityReport
    from cinefactory.studio.multishot_render_identity import RealRenderReIDReport
    from types import SimpleNamespace
    diag=SimpleNamespace(passed=True,measured=True,production_qualified=False,
        independent_diarization_verified=False,independent_face_landmarks_verified=False)
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v186_required=True,
        speaker_source=diag,image_mouth=diag,real_multishot=diag,
    )
    assert not gate.passed
    assert "INDEPENDENT_DIARIZATION_NOT_QUALIFIED" in gate.blockers
    assert "FACE_LANDMARK_OBSERVABILITY_NOT_QUALIFIED" in gate.blockers
    assert "REAL_MULTISHOT_UNCONSTRAINED_REID_NOT_QUALIFIED" in gate.blockers
    assert "KNOWN_SOURCE_SPEAKER_ATTRIBUTION_FAILED" not in gate.blockers


def test_v186_mandatory_missing_metrics_block_with_specific_reasons():
    gate=PerformanceQualificationGate.assess(
        temporal=None,sync=None,
        identity_required=False,lipsync_required=False,v186_required=True,
    )
    assert not gate.passed
    assert "KNOWN_SOURCE_SPEAKER_ATTRIBUTION_FAILED" in gate.blockers
    assert "IMAGE_ONLY_FACE_MOUTH_OBSERVABILITY_FAILED" in gate.blockers
    assert "REAL_TWO_SHOT_APPEARANCE_IDENTITY_FAILED" in gate.blockers



def test_real_image_mouth_consistent_with_blender_rig_only_after_image_detection(original):
    from cinefactory.studio.mouth_image_rig_agreement import MouthRigCrossCheck
    from cinefactory.studio.rendered_mouth_qc import RenderedMouthSample
    observed=FacePatchMotionMouthDetector().evaluate(
        media_path=original["speech_video"]["path"],searches=actor_boxes(original),
    )
    side=json.loads(Path(original["blender"]["path"]+".geometry_qc.json").read_text(encoding="utf-8"))
    projection=[RenderedMouthSample.model_validate(x) for x in side["mouth_projection"]]
    report=MouthRigCrossCheck().compare(observed=observed,projected=projection)
    assert report.passed
    assert all(c.iou>.32 for c in report.matches)
    assert not report.production_qualified
    assert not report.independent_landmark_ground_truth


def test_wrong_mouth_coordinates_fail_cross_validation(original):
    from cinefactory.studio.mouth_image_rig_agreement import MouthRigCrossCheck
    from cinefactory.studio.rendered_mouth_qc import RenderedMouthSample
    observed=FacePatchMotionMouthDetector().evaluate(
        media_path=original["speech_video"]["path"],searches=actor_boxes(original),
    )
    assert observed.passed
    # A fake landmark offset could show motion but must not match rig geometry.
    mutated=observed.model_copy(deep=True)
    candidate=mutated.candidates[0]
    candidate.screen_box_top_left={"x0":.02,"y0":.02,"x1":.06,"y1":.06}
    side=json.loads(Path(original["blender"]["path"]+".geometry_qc.json").read_text(encoding="utf-8"))
    projection=[RenderedMouthSample.model_validate(x) for x in side["mouth_projection"]]
    verdict=MouthRigCrossCheck().compare(observed=mutated,projected=projection)
    assert not verdict.passed
    assert any("MOUTH_IMAGE_RIG_LOCATION_DISAGREEMENT" in s for s in verdict.blockers)


def test_v186_company_crosscheck_service_registered():
    from cinefactory.appctx import build_context
    ctx=build_context(ROOT)
    assert ctx.mouth_rig_crosscheck is ctx.studio.professional_company.mouth_rig_crosscheck


def test_production_gate_requires_mouth_crosscheck_when_v186_enabled():
    from types import SimpleNamespace
    diagnostic=SimpleNamespace(passed=True,measured=True,production_qualified=False,
        independent_diarization_verified=False,independent_face_landmarks_verified=False)
    verdict=PerformanceQualificationGate.assess(
        temporal=None,sync=None,identity_required=False,lipsync_required=False,
        v186_required=True,speaker_source=diagnostic,
        image_mouth=diagnostic,real_multishot=diagnostic,
        mouth_rig_agreement=None,
    )
    assert "IMAGE_RIG_MOUTH_LOCALIZATION_DISAGREES_OR_MISSING" in verdict.blockers
    assert not verdict.passed
