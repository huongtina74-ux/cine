from __future__ import annotations

"""v1.6.23 evidence: genuine Wan frames for seeded temporal QC, and
clearly synthetic A/V synchronization positive/negative control clips.
"""
import hashlib
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.studio.audio_visual_sync_qc import (
    MouthRegion, SpeakerWindow, PerformanceQualificationGate,
)


def fixture(out:Path, *, lag_frames:int=0)->Path:
    frames=48
    fps=20
    video=out/("visual_delayed.mp4" if lag_frames else "visual_aligned.mp4")
    raw=out/("visual_delayed_noaudio.mp4" if lag_frames else "visual_aligned_noaudio.mp4")
    writer=cv2.VideoWriter(str(raw),cv2.VideoWriter_fourcc(*"mp4v"),fps,(160,120))
    if not writer.isOpened():
        raise RuntimeError("VIDEO_FIXTURE_WRITER_FAILED")
    bursts=[(.15,.38),(.60,.96),(1.16,1.33),(1.57,1.98)]
    active=lambda t:any(a<=t<b for a,b in bursts)
    for i in range(frames):
        frame=np.full((120,160,3),235,dtype=np.uint8)
        if active((i-lag_frames)/fps):
            cv2.rectangle(frame,(51,84),(109,97),(5,5,5),-1)
        writer.write(frame)
    writer.release()
    rate=16000
    audio=np.zeros(round(rate*frames/fps),dtype=np.int16)
    for i in range(len(audio)):
        t=i/rate
        if active(t):
            audio[i]=round(10000*math.sin(2*math.pi*440*t))
    wav=out/"synthetic_beeps.wav"
    with wave.open(str(wav),"wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(audio.tobytes())
    subprocess.run([
        "ffmpeg","-nostdin","-v","error","-y",
        "-i",str(raw),"-i",str(wav),"-c:v","copy","-c:a","aac",
        "-shortest",str(video),
    ],check=True,timeout=45)
    return video


def main()->None:
    out=ROOT/"data"/"verification"/"v183_temporal_lipsync"
    out.mkdir(parents=True,exist_ok=True)
    ctx=build_context(ROOT)
    source=ROOT/"data"/"verification"/"v182_three_actor_dialogue"/"three_actor_verification.json"
    previous=json.loads(source.read_text(encoding="utf-8"))
    video=Path(previous["wan_path"])
    references=previous["reference_packs"]
    temporal=ctx.temporal_reid.assess_reference_seeded_video(
        factory=ctx.character_factory,
        actor_reference_ids={a:v["reference_id"] for a,v in references.items()},
        global_character_ids={a:v["global_character_id"] for a,v in references.items()},
        video_path=video,max_samples=10,
    )
    mouth=MouthRegion(actor_id="A",box={"x0":.30,"x1":.70,"y0":.68,"y1":.85})
    line=SpeakerWindow(line_id="L_A",actor_id="A",start_seconds=0,end_seconds=2.2)
    aligned=ctx.audio_visual_sync.verify(
        media_path=fixture(out),turns=[line],mouth_regions=[mouth],
    )
    delayed=ctx.audio_visual_sync.verify(
        media_path=fixture(out,lag_frames=6),turns=[line],mouth_regions=[mouth],
    )
    real_video_sync=ctx.audio_visual_sync.verify(
        media_path=video,
        turns=[SpeakerWindow(line_id="S_ABC_NO_REAL_AUDIO",actor_id="A",
                             start_seconds=.1,end_seconds=.7)],
        mouth_regions=[mouth],
    )
    decision=PerformanceQualificationGate.assess(
        temporal=temporal,sync=real_video_sync,
    )
    assert aligned.passed and not aligned.production_qualified
    assert not delayed.passed
    assert "ACTUAL_AUDIO_TRACK_REQUIRED" in real_video_sync.blockers
    assert not temporal.production_qualified
    assert not decision.passed
    hasher=hashlib.sha256()
    with video.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1<<20), b""):
            hasher.update(chunk)
    payload={
        "milestone":"v1.6.23",
        "real_three_actor_wan_sha256":hasher.hexdigest(),
        "status":"DIAGNOSTICS_COMPLETED_PRODUCTION_BLOCKED",
        "real_three_actor_wan":str(video),
        "temporal_reference_seeded":temporal.model_dump(mode="json"),
        "synthetic_envelope_positive":aligned.model_dump(mode="json"),
        "synthetic_envelope_delayed_control":delayed.model_dump(mode="json"),
        "wan_audio_visual_sync":real_video_sync.model_dump(mode="json"),
        "production_decision":decision.model_dump(mode="json"),
        "notes":[
            "Reference-seeded actor windows are not independent reacquisition.",
            "Synthetic A/V uses sine beeps and drawn mouth rectangle, not speech.",
            "Actual Wan sample contains video-only material; phoneme lip-sync unqualified.",
            "Do not remove SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED.",
        ],
    }
    report=out/"qualification_evidence.json"
    report.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    summary={
        "report":str(report),
        "real_temporal_status":temporal.status,
        "real_temporal_blockers":temporal.blockers,
        "fixture_aligned":aligned.status,
        "fixture_delay":delayed.status,
        "wan_sync":real_video_sync.status,
        "production":decision.status,
    }
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
