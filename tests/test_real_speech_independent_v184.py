from __future__ import annotations

import json
from pathlib import Path
import cv2
import numpy as np
import pytest
from pydantic import ValidationError

from cinefactory.studio.independent_actor_detection import (
    ActorGroundTruth, ColorSignature, IndependentColorActorDetector,
)
from cinefactory.studio.temporal_reid import (
    DetectionOrigin,TemporalFrame,TemporalReIDEngine,
)
from cinefactory.studio.real_speech_viseme import (
    RealSpeechVisemeService,SpeechVisemeTrack,SapiVisemeEvent,
)


def sig():
    return IndependentColorActorDetector([
        ColorSignature(actor_id="A",rgb=(230,40,45),tolerance=28,
                       minimum_area_fraction=.005),
        ColorSignature(actor_id="B",rgb=(40,80,230),tolerance=28,
                       minimum_area_fraction=.005),
    ])


def frame(x1=15,x2=105,draw_b=True,extra_red=False):
    image=np.full((100,150,3),210,dtype=np.uint8)
    cv2.rectangle(image,(x1,15),(x1+22,66),(230,40,45),-1)
    if draw_b:
        cv2.rectangle(image,(x2,20),(x2+22,70),(40,80,230),-1)
    if extra_red:
        cv2.rectangle(image,(62,30),(90,78),(230,40,45),-1)
    return image


def test_detects_without_any_seed_or_previous_screen_box():
    found=sig().detect(frame(38,90))
    assert len(found)==2
    assert {x.origin for x in found}=={DetectionOrigin.INDEPENDENT}
    found_a=next(x for x in found if x.appearance_scores["A"]>.5)
    assert abs(found_a.screen_box["x0"]-38/150)<.001


def test_independent_detector_no_colors_no_actors():
    assert sig().detect(np.full((100,150,3),210,dtype=np.uint8))==[]


def test_detector_rejects_ambiguous_actor_palette():
    with pytest.raises(ValueError,match="COLOR_SIGNATURES_NOT_SEPARABLE"):
        IndependentColorActorDetector([
            ColorSignature(actor_id="A",rgb=(230,40,45)),
            ColorSignature(actor_id="B",rgb=(229,41,45)),
        ])


def test_detector_benchmark_counts_false_positives():
    detector=sig()
    frames=[(i*.1,frame(extra_red=True)) for i in range(5)]
    boxes=[
        ActorGroundTruth(
            actor_id="A",time_seconds=t,
            screen_box={"x0":15/150,"y0":15/100,
                        "x1":38/150,"y1":67/100},
        )
        for t,_ in frames
    ]
    report=detector.benchmark(frames=frames,ground_truth=boxes)
    assert not report.passed
    assert report.false_positives>=5
    assert "DETECTOR_PRECISION_BELOW_FLOOR" in report.blockers


def test_detector_benchmark_requires_label_for_every_frame():
    detector=sig()
    frames=[(i*.1,frame(draw_b=False)) for i in range(4)]
    result=detector.benchmark(frames=frames,ground_truth=[
        ActorGroundTruth(
            actor_id="A",time_seconds=0.,
            screen_box={"x0":.1,"y0":.15,"x1":38/150,"y1":.67},
        )
    ])
    assert "GROUND_TRUTH_FRAME_UNLABELED:0.1" in result.blockers


def test_detector_dynamic_video_motion_with_known_occlusion(tmp_path):
    file=tmp_path/"actors.mp4"
    writer=cv2.VideoWriter(str(file),cv2.VideoWriter_fourcc(*"mp4v"),10,(150,100))
    assert writer.isOpened()
    truth=[]
    for i in range(10):
        x=15+2*i
        bx=105-2*i
        writer.write(cv2.cvtColor(frame(x,bx,draw_b=i not in (4,5)),
                                  cv2.COLOR_RGB2BGR))
        t=i/10
        truth.extend([
            ActorGroundTruth(actor_id="A",time_seconds=t,
                screen_box={"x0":x/150,"y0":.15,
                            "x1":(x+23)/150,"y1":.67}),
            ActorGroundTruth(actor_id="B",time_seconds=t,
                visible=i not in (4,5),
                screen_box={"x0":bx/150,"y0":.20,
                            "x1":(bx+23)/150,"y1":.71}),
        ])
    writer.release()
    engine=sig()
    samples=engine.video_frames(video_path=file,sample_count=10)
    benchmark=engine.benchmark(frames=samples,ground_truth=truth)
    assert benchmark.passed,benchmark.blockers
    timeline=TemporalReIDEngine().assess(actor_ids=["A","B"],frames=[
        TemporalFrame(time_seconds=t,detections=engine.detect(img))
        for t,img in samples
    ])
    assert timeline.passed,timeline.blockers
    assert timeline.tracks[1].reacquisitions==1
    assert not timeline.production_qualified


def test_invalid_color_frame_is_rejected():
    with pytest.raises(ValueError,match="RGB_U8_IMAGE_REQUIRED"):
        sig().detect(np.zeros((100,100),dtype=np.uint8))


def mock_track(tmp_path,*,end=2.5):
    import wave
    file=tmp_path/"a.wav"
    with wave.open(str(file),"wb") as dest:
        dest.setnchannels(1)
        dest.setsampwidth(2)
        dest.setframerate(16000)
        dest.writeframes(bytes(2*int(16000*1.3)))
    digest=RealSpeechVisemeService._hash(file)
    track=SpeechVisemeTrack(
        line_id="L_1",actor_id="A",text="Hello.",
        voice="Microsoft David Desktop",audio_path=str(file),
        audio_sha256=digest,audio_duration_seconds=1.3,
        line_start_seconds=.25,timeline_end_seconds=end,
        event_source="SYNTHESIZER_VISEME_REACHED",
        events=[
            SapiVisemeEvent(viseme=0,time_seconds=0,duration_seconds=.1,next_viseme=4),
            SapiVisemeEvent(viseme=4,time_seconds=.25,duration_seconds=.1,next_viseme=0),
        ],
    )
    file.with_suffix(".visemes.json").write_text(json.dumps({
        "wav_sha256":digest,
        "voice":track.voice,
        "text":track.text,
        "event_source":track.event_source,
        "viseme_events":[event.model_dump() for event in track.events],
    }),encoding="utf-8")
    return track


def test_viseme_cue_preserves_real_source_and_approx_shapes(tmp_path):
    track=mock_track(tmp_path)
    cue=RealSpeechVisemeService.blender_cue(track)
    assert cue["event_source"]=="SYNTHESIZER_VISEME_REACHED"
    assert cue["audio_sha256"]==track.audio_sha256
    assert cue["viseme_events"][0]["viseme"]==0
    assert cue["viseme_events"][1]["jaw_open"]>.01


def test_viseme_rejects_unsupported_events_and_invalid_timeline(tmp_path):
    model=mock_track(tmp_path).model_dump()
    model["timeline_end_seconds"]=1.
    with pytest.raises(ValidationError,match="AUDIO_EXCEEDS_LINE_WINDOW"):
        SpeechVisemeTrack.model_validate(model)
    model=mock_track(tmp_path).model_dump()
    model["events"][1]["time_seconds"]=-1.
    with pytest.raises(ValidationError):
        SpeechVisemeTrack.model_validate(model)


def test_viseme_tampered_audio_fails_authorization(tmp_path):
    from cinefactory.block_animation.contracts import (
        ShotPerformanceSpec,ActorPlacement,CameraIntent,
    )
    shot=ShotPerformanceSpec(
        shot_id="T",scene_template_id="minecraft_classroom",
        duration_seconds=3.5,
        actors=[ActorPlacement(actor_id="A",rig_id="mc_a",marker="hero_a")],
        camera=CameraIntent(
            pattern_id="fidelity_group",purpose="actor",
            targets=["A"],
        ),
    )
    service=RealSpeechVisemeService(Path(__file__).resolve().parents[1])
    track=mock_track(tmp_path)
    attached=service.attach_to_shot(shot,[track])
    assert len(attached.creative_intent["speech_viseme_tracks"])==1
    assert attached.creative_intent["speech_viseme_production_qualified"] is False
    Path(track.audio_path).write_bytes(b"tampered!")
    with pytest.raises(ValueError,match="SPEECH_AUDIO_EVIDENCE_HASH_MISMATCH"):
        service.attach_to_shot(shot,[track])


def test_sapi_synthesis_uses_actual_audio_and_event_offsets(tmp_path):
    import sys
    if sys.platform!="win32":
        pytest.skip("Windows SAPI voices")
    root=Path(__file__).resolve().parents[1]
    track=RealSpeechVisemeService(root).synthesize(
        line_id="TTS_REAL",actor_id="A",text="Hello!",
        voice="Microsoft David Desktop",output_dir=tmp_path,
        line_start_seconds=.1,timeline_end_seconds=12.,
    )
    assert Path(track.audio_path).stat().st_size>1000
    assert track.audio_duration_seconds>.15
    assert len(track.events)>=3
    assert any(e.viseme>0 for e in track.events)
    assert track.events==sorted(track.events,key=lambda e:e.time_seconds)
    assert not track.phoneme_alignment_verified
    assert not track.audio_visual_sync_verified
    assert not track.production_qualified


def test_company_exposes_real_speech_and_detector_lab():
    from cinefactory.appctx import build_context
    ctx=build_context(Path(__file__).resolve().parents[1])
    assert ctx.real_speech_viseme is ctx.studio.professional_company.real_speech_viseme
    assert ctx.independent_actor_detection is ctx.studio.professional_company.independent_actor_detection
    detector=ctx.independent_actor_detection.build([
        ColorSignature(actor_id="A",rgb=(230,40,45)),
    ])
    assert isinstance(detector,IndependentColorActorDetector)


def test_execution_planner_carries_speech_visemes_to_render_worker(tmp_path):
    from cinefactory.block_animation.contracts import (
        ActorPlacement, CameraIntent, EpisodeSpec, ShotPerformanceSpec,
        BlenderAnimationJob,
    )
    from cinefactory.block_animation.assembler import EpisodeAssembler
    from cinefactory.block_animation.execution import BlockExecutionPlanner
    root=Path(__file__).resolve().parents[1]
    voice=mock_track(tmp_path)
    shot=ShotPerformanceSpec(
        shot_id="S_VISEME",scene_template_id="minecraft_classroom",
        duration_seconds=3.5,
        actors=[ActorPlacement(actor_id="A",rig_id="mc_a",marker="hero_a")],
        camera=CameraIntent(pattern_id="fidelity_group",purpose="solo",
                            targets=["A"]),
    )
    authorized=RealSpeechVisemeService(root).attach_to_shot(shot,[voice])
    ep=EpisodeSpec(
        project_id="T_VISEME",episode_id="T_VISEME",
        title="Speech plan provenance",fps=24,width=320,height=180,
        quality_profile="preview",shots=[authorized],
    )
    compiled=EpisodeAssembler.from_root(root).compile(ep,output_dir=tmp_path)
    resolved=compiled.shots[0]
    job=BlenderAnimationJob(
        job_id="J_VISEME", project_id=ep.project_id,
        episode_id=ep.episode_id,
        shot=resolved, output_path=str(tmp_path/"render.mp4"),
        temp_dir=str(tmp_path),render_preview=True,
    )
    plan=BlockExecutionPlanner.plan(job)
    assert plan["speech_viseme_tracks"][0]["line_id"]=="L_1"
    assert plan["speech_viseme_tracks"][0]["audio_sha256"]==voice.audio_sha256
    assert plan["creative_intent"]["speech_viseme_production_qualified"] is False
