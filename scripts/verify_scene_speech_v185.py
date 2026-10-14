from __future__ import annotations

"""v1.6.24 controlled real SAPI speech + Blender viseme render and CV benchmark.

Qualification evidence is diagnostic; never grants autonomous production approval.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.block_animation.contracts import (
    ActorPlacement, CameraIntent, EpisodeSpec, ShotPerformanceSpec,
)
from cinefactory.studio.block_production import BlockAnimationProducer
from cinefactory.studio.real_speech_viseme import RealSpeechVisemeService, SpeechVisemeTrack
from cinefactory.studio.independent_actor_detection import (
    ColorSignature, ActorGroundTruth, IndependentColorActorDetector,
)
from cinefactory.studio.temporal_reid import TemporalReIDEngine,TemporalFrame


def hashfile(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def detector_benchmark(directory:Path)->dict:
    detector=IndependentColorActorDetector([
        ColorSignature(actor_id="A",rgb=(231,40,48),tolerance=35),
        ColorSignature(actor_id="B",rgb=(40,79,232),tolerance=35),
    ])
    out=directory/"independent_actor_control.mp4"
    writer=cv2.VideoWriter(str(out),cv2.VideoWriter_fourcc(*"mp4v"),12,(320,180))
    assert writer.isOpened()
    gt=[]
    for i in range(12):
        frame=np.full((180,320,3),(218,218,218),dtype=np.uint8)
        t=i/12
        x_a=24+7*i
        x_b=246-7*i
        cv2.rectangle(frame,(x_a,48),(x_a+36,112),(48,40,231),-1)
        gt.append(ActorGroundTruth(
            actor_id="A",time_seconds=t,
            screen_box={"x0":x_a/320,"y0":48/180,"x1":(x_a+37)/320,"y1":113/180},
        ))
        visible=i not in (5,6)
        if visible:
            cv2.rectangle(frame,(x_b,50),(x_b+37,113),(232,79,40),-1)
        gt.append(ActorGroundTruth(
            actor_id="B",time_seconds=t,visible=visible,
            screen_box={"x0":x_b/320,"y0":50/180,"x1":(x_b+38)/320,"y1":114/180},
        ))
        writer.write(frame)
    writer.release()
    frames=detector.video_frames(video_path=out,sample_count=12)
    benchmark=detector.benchmark(frames=frames,ground_truth=gt)
    temporal=TemporalReIDEngine(maximum_consecutive_missing=2,
                                minimum_coverage=.80).assess(
        actor_ids=["A","B"],
        frames=[TemporalFrame(
            time_seconds=t,detections=detector.detect(image)
        ) for t,image in frames],
    )
    assert benchmark.passed,benchmark
    assert temporal.passed,temporal
    # Negative control: equally strong actor-colored false object.
    sample=frames[0][1].copy()
    cv2.rectangle(sample,(176,70),(216,123),(48,40,231),-1)
    negative=detector.benchmark(
        frames=[(i/12,sample) for i in range(12)],
        ground_truth=[
            ActorGroundTruth(
                actor_id="A",time_seconds=i/12,
                screen_box=gt[0].screen_box,
            )
            for i in range(12)
        ],
    )
    assert not negative.passed
    return {
        "fixture_video":str(out),
        "fixture_sha256":hashfile(out),
        "positive":benchmark.model_dump(mode="json"),
        "negative_distractor":negative.model_dump(mode="json"),
        "temporal_independent_detection":temporal.model_dump(mode="json"),
        "applicability":"FLAT_COLOR_CONTROLLED_ACTOR_SCENE_ONLY",
    }


def main()->None:
    out=ROOT/"data"/"verification"/"v185_alignment_reid"
    out.mkdir(parents=True,exist_ok=True)
    report_path=out/"v185_render_evidence.json"
    report={"milestone":"v1.6.25","status":"STARTED",
            "production_qualified":False}
    try:
        factory=RealSpeechVisemeService(ROOT)
        a=factory.synthesize(
            line_id="SPEECH_A",actor_id="A",
            voice="Microsoft David Desktop",
            text="Hello!",
            output_dir=out,
            line_start_seconds=.35,timeline_end_seconds=12.,
        )
        a=SpeechVisemeTrack.model_validate({
            **a.model_dump(),"timeline_end_seconds":
            a.line_start_seconds+a.audio_duration_seconds+.12,
        })
        second_start=a.timeline_end_seconds+.30
        b=factory.synthesize(
            line_id="SPEECH_B",actor_id="B",
            voice="Microsoft Zira Desktop",
            text="Let's go!",
            output_dir=out,
            line_start_seconds=second_start,timeline_end_seconds=20.,
        )
        b=SpeechVisemeTrack.model_validate({
            **b.model_dump(),"timeline_end_seconds":
            b.line_start_seconds+b.audio_duration_seconds+.12,
        })
        scene_duration=b.timeline_end_seconds+.20
        report["speech"]=[a.model_dump(mode="json"),b.model_dump(mode="json")]
        shot=ShotPerformanceSpec(
            shot_id="SPEAKERS_AB",scene_template_id="minecraft_classroom",
            duration_seconds=scene_duration,
            actors=[
                ActorPlacement(actor_id="A",rig_id="mc_a",marker="hero_a"),
                ActorPlacement(actor_id="B",rig_id="mc_b",marker="hero_b"),
            ],
            camera=CameraIntent(
                purpose="fidelity_group",pattern_id="fidelity_group",
                targets=["A","B"],alternatives=2,
            ),
            narrative_purpose="real SAPI dialogue animation baseline",
        )
        shot=factory.attach_to_shot(shot,[a,b])
        episode=EpisodeSpec(
            project_id="V185_SAPI",episode_id="V185_SAPI",
            title="Two actor true synthesized speech and procedural viseme keys",
            fps=24,width=1280,height=720,
            quality_profile="preview",shots=[shot],
        )
        blender=ROOT/".tools"/"blender-4.5.14-windows-x64"/"blender.exe"
        producer=BlockAnimationProducer(
            ROOT,blender_executable=str(blender),max_repair_rounds=0,
        )
        try:
            dailies=producer.produce(
                episode,project_root=out/"blender",render_preview=True,
            )
        finally:
            producer.close()
        report["blender_dailies_passed"]=dailies.passed
        if not dailies.passed:
            report["blender_dailies"]=dailies.model_dump(mode="json")
            raise RuntimeError("V184_BLENDER_DAILIES_FAILED")
        mp4=Path(dailies.shots[0].selected_path).resolve()
        sidecar=json.loads(mp4.with_suffix(
            mp4.suffix+".geometry_qc.json"
        ).read_text(encoding="utf-8"))
        applied=sidecar.get("viseme_debug",[])
        assert len(applied)==2 and all(x["animation_applied"] for x in applied),applied
        assert [x["event_count"] for x in applied]==[len(a.events),len(b.events)]
        report["blender"]={
            "path":str(mp4),"sha256":hashfile(mp4),
            "geometry_qc":sidecar["geometry_qc"],
            "performance_qc":sidecar["performance_qc"],
            "viseme_debug":applied,
        }
        audio_video=out/"two_actors_speech_audible.mp4"
        # Explicitly mix separated SAPI voice tracks with their speaking offsets.
        command=[
            "ffmpeg","-nostdin","-v","error","-y",
            "-i",str(mp4),"-i",a.audio_path,"-i",b.audio_path,
            "-filter_complex",
            f"[1:a]adelay={round(a.line_start_seconds*1000)}:all=1[voicea];"
            f"[2:a]adelay={round(b.line_start_seconds*1000)}:all=1[voiceb];"
            "[voicea][voiceb]amix=inputs=2:duration=longest:normalize=0,"
            "apad[dialogue]",
            "-map","0:v:0","-map","[dialogue]",
            "-c:v","copy","-c:a","aac","-t",f"{scene_duration:.4f}",str(audio_video),
        ]
        subprocess.run(command,check=True,timeout=80)
        ffprobe=subprocess.run([
            "ffprobe","-v","error","-show_streams","-of","json",
            str(audio_video),
        ],capture_output=True,text=True,check=True)
        streams=json.loads(ffprobe.stdout)["streams"]
        assert {s["codec_type"] for s in streams} >= {"video","audio"}
        report["speech_video"]={
            "path":str(audio_video),"sha256":hashfile(audio_video),
            "stream_codecs":[s["codec_name"] for s in streams],
            "duration_seconds":scene_duration,
            "real_voice_sources":2,
            "sapi_event_timing_animation_applied":True,
            "phoneme_alignment_verified":False,
            "audio_visual_sync_verified":False,
        }
        report["independent_detector_benchmark"]=detector_benchmark(out)
        report["status"]="REAL_SPEECH_RENDER_AND_CONTROLLED_DETECTOR_PASS_PRODUCTION_BLOCKED"
        print(json.dumps({
            "status":report["status"],
            "tts_event_counts":[len(a.events),len(b.events)],
            "blender_viseme_events":[x["event_count"] for x in applied],
            "detector_precision":report["independent_detector_benchmark"]["positive"]["precision"],
            "detector_recall":report["independent_detector_benchmark"]["positive"]["recall"],
            "production_qualified":False,
        },indent=2))
    except Exception as exc:
        report["status"]="FAILED"
        report["error"]=f"{type(exc).__name__}: {exc}"
        raise
    finally:
        report_path.write_text(json.dumps(report,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
