from __future__ import annotations

import hashlib
import json
import math
import wave
from pathlib import Path

import cv2
import numpy as np
import pytest
from pydantic import ValidationError

from cinefactory.studio.audio_constrained_alignment import (
    AudioConstrainedWordVerifier, SynthesizerWordEvent,
)
from cinefactory.studio.independent_actor_detection import (
    ColorSignature, IndependentColorActorDetector,
)
from cinefactory.studio.multi_seed_identity_qc import MultiSeedIdentityLab
from cinefactory.studio.rendered_mouth_qc import (
    RenderedMouthProjectionQC,RenderedMouthSample,
)


def palette():
    return IndependentColorActorDetector([
        ColorSignature(actor_id="A",rgb=(230,40,45),tolerance=28),
        ColorSignature(actor_id="B",rgb=(40,80,230),tolerance=28),
    ])


def test_multi_seed_independent_id_baseline_and_anti_overclaim():
    report=MultiSeedIdentityLab(palette()).evaluate(seeds=[1,7,16])
    assert report.passed,report.blockers
    assert report.status=="CONTROLLED_MULTI_SEED_PASS"
    assert report.worst_precision>=.95
    assert report.worst_recall>=.95
    assert not report.production_qualified
    assert all(x.identity.passed for x in report.scenarios)
    assert all(x.identity.tracks[1].reacquisitions==1 for x in report.scenarios)
    assert len({x.frame_fingerprints[0] for x in report.scenarios})==3


def test_multi_seed_veto_if_one_seed_has_impostor():
    report=MultiSeedIdentityLab(palette()).evaluate(
        seeds=[1,7,16],corrupted_seeds={7},
    )
    assert not report.passed
    assert any(x.startswith("SEED_7:") for x in report.blockers)
    assert report.scenarios[1].detection.false_positives>=1


def test_multi_seed_requires_distinct_three_seeds():
    report=MultiSeedIdentityLab(palette()).evaluate(seeds=[2,2])
    assert not report.passed
    assert "MULTISEED_SEED_SET_INSUFFICIENT_OR_DUPLICATE" in report.blockers


def write_wav(path:Path,*,sound_start=0.0,sound_end=1.4):
    rate=16000
    data=np.zeros(rate*2,dtype=np.int16)
    for i in range(len(data)):
        second=i/rate
        if sound_start<=second<sound_end:
            data[i]=round(11000*math.sin(2*math.pi*430*second))
    with wave.open(str(path),"wb") as dest:
        dest.setnchannels(1)
        dest.setsampwidth(2)
        dest.setframerate(rate)
        dest.writeframes(data.tobytes())
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens():
    return [
        SynthesizerWordEvent(text="hello",time_seconds=.1,
                             character_position=0,character_count=5),
        SynthesizerWordEvent(text="world",time_seconds=.8,
                             character_position=6,character_count=5),
    ]


def test_pcm_constrained_word_consistency_on_real_decodable_wav(tmp_path):
    wav=tmp_path/"voice.wav"
    digest=write_wav(wav,sound_end=1.8)
    report=AudioConstrainedWordVerifier().verify(
        audio_path=wav,audio_sha256=digest,
        transcript="Hello world!",word_events=tokens(),
    )
    assert report.passed,report.blockers
    assert len(report.words)==2
    assert all(w.voice_coverage>.12 for w in report.words)
    assert not report.forced_alignment_verified
    assert not report.phoneme_alignment_verified
    assert not report.production_qualified


def test_pcm_constrained_word_blocks_silent_alignment_and_bad_transcript(tmp_path):
    wav=tmp_path/"voice.wav"
    digest=write_wav(wav,sound_start=0,sound_end=.25)
    report=AudioConstrainedWordVerifier().verify(
        audio_path=wav,audio_sha256=digest,
        transcript="Goodbye world",word_events=tokens(),
    )
    assert not report.passed
    assert "SYNTHESIZER_WORD_TEXT_MISMATCH" in report.blockers
    assert any("WORD_1:WORD_AUDIO" in f for f in report.blockers)


def test_pcm_constrained_word_rejects_audio_tampering(tmp_path):
    wav=tmp_path/"voice.wav"
    digest=write_wav(wav)
    wav.write_bytes(wav.read_bytes()+b"tampered")
    with pytest.raises(ValueError,match="WORD_ALIGNMENT_AUDIO_HASH_MISMATCH"):
        AudioConstrainedWordVerifier().verify(
            audio_path=wav,audio_sha256=digest,
            transcript="hello world",word_events=tokens(),
        )


def test_pcm_constrained_word_missing_events_fails_closed(tmp_path):
    wav=tmp_path/"voice.wav"
    digest=write_wav(wav)
    report=AudioConstrainedWordVerifier().verify(
        audio_path=wav,audio_sha256=digest,
        transcript="hello world",word_events=[],
    )
    assert not report.passed
    assert "SYNTHESIZER_WORD_EVENTS_MISSING" in report.blockers


def mouth_fixture(tmp_path,*,delay_frames=0,freeze=False,zero_region=False,dark_background=False):
    path=tmp_path/("mouth_%s_%s.mp4"%(delay_frames,freeze))
    fps=20
    writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*"mp4v"),fps,(240,140))
    assert writer.isOpened()
    jaws=[0,0,.8,.8,0,0,.7,.7,0,0,.9,.9,0,0,.6,.6,0,0,.9,.9,0,0,.7,.7,0,0,.6,.6,0,0]
    records=[]
    for frame_index,jaw in enumerate(jaws):
        observation=jaws[max(0,frame_index-delay_frames)]
        if freeze:
            observation=0.
        frame=np.full((140,240,3),32 if dark_background else 215,dtype=np.uint8)
        # stable projected mouth union with jaw-driven dark area
        cv2.rectangle(frame,(91,77),(129,80+round(15*observation)),(4,4,4),-1)
        writer.write(frame)
        records.append(RenderedMouthSample(
            line_id="L1",actor_id="A",
            frame_index=frame_index+1,time_seconds=frame_index/fps,
            mouth_box={
                "x0":91/240,"x1":130/240,
                "y0":77/140,"y1":(81+round(15*jaw))/140,
            } if not zero_region else None,
            projected_width_px=39 if not zero_region else 0,
            projected_height_px=4+15*jaw if not zero_region else 0,
            expected_jaw=jaw,
        ))
    writer.release()
    return path,records


def test_rendered_pixel_mouth_measurement_valid_fixture(tmp_path):
    video,records=mouth_fixture(tmp_path)
    result=RenderedMouthProjectionQC().evaluate(video_path=video,samples=records)
    assert result.passed,result.blockers
    assert result.image_mouth_motion_measured
    assert result.checks[0].jaw_pixel_correlation>.35
    assert not result.production_qualified
    assert not result.phoneme_shapes_verified


def test_rendered_pixel_mouth_rejects_shifted_and_frozen(tmp_path):
    delayed,records=mouth_fixture(tmp_path,delay_frames=5)
    result=RenderedMouthProjectionQC().evaluate(
        video_path=delayed,samples=records,
    )
    assert not result.passed
    assert any("CORRELATION_LOW" in x for x in result.blockers)
    frozen,records=mouth_fixture(tmp_path,freeze=True)
    result=RenderedMouthProjectionQC().evaluate(
        video_path=frozen,samples=records,
    )
    assert not result.passed
    assert any("ACTIVITY_INSUFFICIENT" in x for x in result.blockers)


def test_rendered_pixel_mouth_blocks_unresolvable_rig_roi(tmp_path):
    video,records=mouth_fixture(tmp_path,zero_region=True)
    result=RenderedMouthProjectionQC().evaluate(
        video_path=video,samples=records,
    )
    assert not result.passed
    assert "L1:MOUTH_PROJECTED_REGION_TOO_SMALL_OR_HIDDEN" in result.blockers


def test_mouth_rejects_untrusted_coordinate_provenance():
    with pytest.raises(ValidationError,match="UNTRUSTED_MOUTH_REGION_PROVENANCE"):
        RenderedMouthSample(
            line_id="L1",actor_id="A",frame_index=1,
            time_seconds=0,mouth_box=None,projected_width_px=0,
            projected_height_px=0,expected_jaw=0,
            provenance="INVENTED_BY_LLM",
        )


def test_dark_face_saturated_black_pixel_metric_uses_luma_fallback(tmp_path):
    video,records=mouth_fixture(tmp_path,dark_background=True)
    result=RenderedMouthProjectionQC().evaluate(video_path=video,samples=records)
    assert result.passed,result.blockers
    assert result.checks[0].pixel_signal_kind=="INVERSE_MEAN_LUMA_SATURATION_FALLBACK"
    assert result.checks[0].jaw_pixel_correlation>.35
    assert not result.production_qualified


def test_dark_face_luminance_fallback_blocks_frozen_mouth(tmp_path):
    video,records=mouth_fixture(tmp_path,dark_background=True,freeze=True)
    report=RenderedMouthProjectionQC().evaluate(video_path=video,samples=records)
    assert not report.passed
    assert any("MOUTH_PIXEL_ACTIVITY_INSUFFICIENT" in code for code in report.blockers)


def test_v185_evidence_consuming_gate_remains_production_blocked():
    from types import SimpleNamespace
    from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate
    diagnostic=SimpleNamespace(passed=True,production_qualified=False)
    report=PerformanceQualificationGate.assess(
        temporal=None,sync=None,v185_required=True,
        audio_word_reports=[diagnostic,diagnostic],
        mouth_pixels=diagnostic,multi_seed=diagnostic,
    )
    assert not report.passed
    assert "INDEPENDENT_FORCED_ALIGNMENT_UNQUALIFIED" in report.blockers
    assert "RENDERED_PHONEME_SHAPES_UNQUALIFIED" in report.blockers
    assert "MULTISEED_REAL_VIDEO_IDENTITY_UNQUALIFIED" in report.blockers
    assert "REAL_AUDIO_WORD_CONSISTENCY_FAILED_OR_MISSING" not in report.blockers
    assert "RENDERED_MOUTH_PIXEL_QC_FAILED_OR_MISSING" not in report.blockers


def test_v185_failed_signal_blocks_even_diagnostic_qualification():
    from types import SimpleNamespace
    from cinefactory.studio.audio_visual_sync_qc import PerformanceQualificationGate
    failed=SimpleNamespace(passed=False,production_qualified=False)
    report=PerformanceQualificationGate.assess(
        temporal=None,sync=None,v185_required=True,
        audio_word_reports=[failed],mouth_pixels=failed,multi_seed=failed,
    )
    assert not report.passed
    assert "REAL_AUDIO_WORD_CONSISTENCY_FAILED_OR_MISSING" in report.blockers
    assert "RENDERED_MOUTH_PIXEL_QC_FAILED_OR_MISSING" in report.blockers
    assert "MULTISEED_IDENTITY_BENCHMARK_FAILED_OR_MISSING" in report.blockers


def test_sapi_word_timing_character_span_tamper_blocks(tmp_path):
    wav=tmp_path/"voice.wav"
    digest=write_wav(wav,sound_end=1.8)
    bad=tokens()
    bad[1]=bad[1].model_copy(update={"character_position":1})
    result=AudioConstrainedWordVerifier().verify(
        audio_path=wav,audio_sha256=digest,transcript="Hello world!",
        word_events=bad,
    )
    assert not result.passed
    assert "SYNTHESIZER_CHARACTER_SPAN_MISMATCH" in result.blockers


def test_v185_company_services_available_and_shared():
    from cinefactory.appctx import build_context
    root=Path(__file__).resolve().parents[1]
    ctx=build_context(root)
    layer=ctx.studio.professional_company
    assert ctx.audio_word_alignment is layer.audio_word_alignment
    assert ctx.rendered_mouth_qc is layer.rendered_mouth_qc
    lab=ctx.independent_actor_detection.multiseed([
        ColorSignature(actor_id="A",rgb=(230,40,45),tolerance=28),
        ColorSignature(actor_id="B",rgb=(40,80,230),tolerance=28),
    ])
    assert isinstance(lab,MultiSeedIdentityLab)
