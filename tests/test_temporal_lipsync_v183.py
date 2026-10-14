from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import cv2
import numpy as np

from cinefactory.studio.audio_visual_sync_qc import (
    AudioVisualSyncVerifier,
    MouthRegion,
    SpeakerWindow,
)
from cinefactory.studio.temporal_reid import (
    ActorDetection,
    DetectionOrigin,
    TemporalFrame,
    TemporalReIDEngine,
)


def detection(name: str, pos: float, *, swapped=False, origin=DetectionOrigin.INDEPENDENT):
    left_identity = name in ("A", "left")
    scores = (
        {"A": .22, "B": .96} if left_identity and swapped else
        {"A": .96, "B": .22} if left_identity else
        {"A": .20, "B": .95}
    )
    return ActorDetection(
        detection_id=name,
        screen_box={"x0": pos, "y0": .2, "x1": pos+.12, "y1": .8},
        appearance_scores=scores,
        origin=origin,
    )


def test_temporal_independent_association_handles_crossing_and_reentry():
    frames = [
        TemporalFrame(time_seconds=0, detections=[detection("left",.15), detection("right",.70)]),
        TemporalFrame(time_seconds=.25, detections=[detection("left",.30), detection("right",.56)]),
        TemporalFrame(time_seconds=.50, detections=[detection("left",.44)]),  # B briefly occluded
        TemporalFrame(time_seconds=.75, detections=[detection("left",.57), detection("right",.30)]),
        TemporalFrame(time_seconds=1., detections=[detection("left",.70), detection("right",.16)]),
    ]
    report = TemporalReIDEngine(minimum_coverage=.8).assess(
        actor_ids=["A","B"], frames=frames,
    )
    assert report.passed and report.status=="PASS"
    assert next(t for t in report.tracks if t.actor_id=="B").reacquisitions==1
    assert report.production_qualified is False  # no long-form/multi-seed sign-off


def test_temporal_reid_blocks_aliasing_and_missing_actor():
    engine=TemporalReIDEngine()
    frames=[TemporalFrame(time_seconds=i*.25,detections=[
        detection("A",.15),
        detection("B",.16),  # near-identical actor regions
    ]) for i in range(5)]
    report=engine.assess(actor_ids=["A","B"],frames=frames)
    assert not report.passed
    assert any("ACTOR_REGION_COLLISION" in s for s in report.blockers)

    frames=[TemporalFrame(time_seconds=i*.25,detections=[
        detection("A",.15)
    ]) for i in range(5)]
    missing=engine.assess(actor_ids=["A","B"],frames=frames)
    assert not missing.passed
    assert any("TRACK_OCCLUSION_LIMIT:B" in s for s in missing.blockers)


def test_temporal_reference_seeded_is_diagnostic_not_production_qualified():
    frames=[TemporalFrame(time_seconds=i*.25,detections=[
        detection("A",.15,origin=DetectionOrigin.REFERENCE_SEEDED),
        detection("B",.70,origin=DetectionOrigin.REFERENCE_SEEDED),
    ]) for i in range(5)]
    report=TemporalReIDEngine().assess(actor_ids=["A","B"],frames=frames)
    assert report.measured and not report.passed
    assert report.status=="REVIEW_REQUIRED"
    assert "INDEPENDENT_ACTOR_DETECTION_NOT_QUALIFIED" in report.warnings


def test_temporal_invalid_timestamp_and_identity_score_rejected():
    frames=[TemporalFrame(time_seconds=0,detections=[
        detection("A",.1,swapped=True),
        detection("B",.7),
    ]) for _ in range(4)]
    report=TemporalReIDEngine().assess(actor_ids=["A","B"],frames=frames)
    assert not report.passed
    assert "NON_MONOTONIC_TIMESTAMPS" in report.blockers


def make_av(tmp_path: Path, *, delay_frames: int=0, mouth_flat: bool=False,
            audio: bool=True) -> Path:
    fps=20
    duration=2.4
    frames=round(fps*duration)
    raw=tmp_path/"raw.mp4"
    fourcc=cv2.VideoWriter_fourcc(*"mp4v")
    writer=cv2.VideoWriter(str(raw),fourcc,fps,(160,120))
    assert writer.isOpened()
    bursts=[(.15,.38),(.60,.96),(1.16,1.33),(1.57,1.98)]
    is_active=lambda t:any(start<=t<end for start,end in bursts)
    for i in range(frames):
        frame=np.full((120,160,3),235,dtype=np.uint8)
        t=(i-delay_frames)/fps
        if not mouth_flat and is_active(t):
            cv2.rectangle(frame,(51,84),(109,97),(5,5,5),-1)
        writer.write(frame)
    writer.release()
    if not audio:
        return raw
    rate=16000
    y=np.zeros(int(rate*duration),dtype=np.int16)
    for i in range(len(y)):
        t=i/rate
        if is_active(t):
            y[i]=round(10000*math.sin(2*math.pi*440*t))
    wav=tmp_path/"voice.wav"
    with wave.open(str(wav),"wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(y.tobytes())
    target=tmp_path/"mux.mp4"
    subprocess.run(["ffmpeg","-nostdin","-v","error","-y",
                    "-i",str(raw),"-i",str(wav),
                    "-c:v","copy","-c:a","aac","-shortest",str(target)],
                   check=True,timeout=30)
    return target


def request(media:Path):
    return AudioVisualSyncVerifier().verify(
        media_path=media,
        turns=[SpeakerWindow(line_id="L1",actor_id="A",
                             start_seconds=0,end_seconds=2.2)],
        mouth_regions=[MouthRegion(actor_id="A",box={
            "x0":.30,"x1":.70,"y0":.68,"y1":.85,
        })],
    )


def test_lipsync_reports_actual_av_envelope_but_not_phoneme_qualification(tmp_path):
    report=request(make_av(tmp_path))
    assert report.passed,report.blockers
    assert report.status=="ENVELOPE_ONLY_PASS"
    assert report.checks[0].envelope_correlation>.55
    assert abs(report.checks[0].best_offset_seconds)<=.12
    assert report.audio_lipsync_measured is False
    assert report.production_qualified is False
    assert report.phoneme_alignment_verified is False
    assert report.source_media_sha256


def test_lipsync_blocks_delayed_mouth_movement(tmp_path):
    report=request(make_av(tmp_path,delay_frames=6))
    assert not report.passed, report
    assert any("AUDIO_MOUTH_OFFSET_TOO_LARGE" in x for x in report.blockers)


def test_lipsync_blocks_flat_mouth_even_with_real_audio(tmp_path):
    report=request(make_av(tmp_path,mouth_flat=True))
    assert not report.passed
    assert any("MOUTH_VISUAL_ACTIVITY_INSUFFICIENT" in x for x in report.blockers)


def test_lipsync_blocks_video_without_real_audio_track(tmp_path):
    report=request(make_av(tmp_path,audio=False))
    assert not report.passed
    assert "ACTUAL_AUDIO_TRACK_REQUIRED" in report.blockers
    assert report.measured is False


def test_lipsync_rejects_mixed_overlapping_speakers(tmp_path):
    media=tmp_path/"missing.mp4"
    report=AudioVisualSyncVerifier().verify(
        media_path=media,
        turns=[],
        mouth_regions=[],
    )
    assert not report.passed
    # Missing media is checked before any claims about a synthetic track.
    assert "MEDIA_MISSING" in report.blockers


def test_app_context_exposes_shared_temporal_and_sync_qualification():
    from cinefactory.appctx import build_context
    ctx=build_context(Path(__file__).resolve().parents[1])
    assert ctx.temporal_reid is ctx.studio.professional_company.temporal_reid
    assert ctx.audio_visual_sync is ctx.studio.professional_company.audio_visual_sync
    assert ctx.performance_qualification is ctx.studio.professional_company.performance_qualification


def test_production_gate_stays_closed_on_envelope_only_and_sampled_identity(tmp_path):
    from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate
    seeded_frames=[TemporalFrame(time_seconds=i*.25,detections=[
        detection("A",.15,origin=DetectionOrigin.REFERENCE_SEEDED)
    ]) for i in range(5)]
    temporal=TemporalReIDEngine().assess(actor_ids=["A"],frames=seeded_frames)
    sync=request(make_av(tmp_path))
    assert sync.passed and temporal.status=="REVIEW_REQUIRED"
    decision=PerformanceQualificationGate.assess(temporal=temporal,sync=sync)
    assert not decision.passed
    assert "TEMPORAL_REID_PRODUCTION_NOT_QUALIFIED" in decision.blockers
    assert "PHONEME_VISEME_LIPSYNC_NOT_QUALIFIED" in decision.blockers


def test_production_gate_does_not_accept_missing_sync():
    from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate
    result=PerformanceQualificationGate.assess(temporal=None,sync=None)
    assert not result.passed
    assert "TEMPORAL_ACTOR_EVIDENCE_MISSING" in result.blockers
    assert "AUDIO_VIDEO_LIPSYNC_EVIDENCE_MISSING" in result.blockers


def test_lipsync_speaker_windows_carry_real_dialogue_turn_contract():
    from cinefactory.studio.dialogue_performance import (
        DialogueLineIntent,DialoguePerformanceEngine
    )
    line=DialogueLineIntent(
        line_id="L01",speaker_id="A",listener_ids=["B"],
        text="Come with me.",objective="request cooperation",
        action_verb="convince",start_seconds=.2,end_seconds=1.4,
    )
    engine=DialoguePerformanceEngine()
    compiled=engine.compile(
        shot_id="S", duration_seconds=2.,
        actor_ids=["A","B"],lines=[line],
    )
    windows=AudioVisualSyncVerifier.windows_from_dialogue(compiled)
    assert len(windows)==1
    assert windows[0].line_id=="L01"
    assert windows[0].actor_id=="A"
    assert windows[0].start_seconds==.2
    assert windows[0].end_seconds==1.4


def test_invalid_semantic_dialogue_cannot_be_synced():
    import pytest
    from cinefactory.studio.dialogue_performance import (
        DialogueLineIntent, DialoguePerformanceEngine,
    )
    line=DialogueLineIntent(
        line_id="L01",speaker_id="A",listener_ids=["UNREGISTERED"],
        text="Look here.",objective="warn listener",action_verb="warn",
        start_seconds=.2,end_seconds=1.4,
    )
    compilation=DialoguePerformanceEngine().compile(
        shot_id="S",duration_seconds=2,actor_ids=["A","B"],lines=[line]
    )
    with pytest.raises(ValueError,match="DIALOGUE_SEMANTIC_QC_NOT_PASSED"):
        AudioVisualSyncVerifier.windows_from_dialogue(compilation)
