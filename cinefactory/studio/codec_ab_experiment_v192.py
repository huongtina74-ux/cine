from __future__ import annotations
"""v1.6.32 real media experiment: compare three H.264 encoder settings.

Local original CineFactory H264/AAC sample -> same codec/CRF and pixel format
with different x264 CPU presets. SSIM measures fidelity to already compressed
source, NOT viewer-perceived artistic quality. Never calls a paid API, never
alters the source or auto-promotes a production method.
"""
import hashlib
import json
import re
import shutil
import subprocess
import time
from pathlib import Path
from pydantic import BaseModel, Field


class EncodeRun(BaseModel):
    preset: str
    crf: int
    output: str
    output_sha256: str
    decoded_video_frames: int
    width: int
    height: int
    output_bytes: int
    ffmpeg_wallclock_seconds: float = Field(gt=0.)
    ssim_all: float | None = Field(default=None,ge=0.,le=1.)
    video_codec: str
    audio_codec: str | None
    acoustic_input_preserved_by_copy: bool = False


class CodecExperimentEvidence(BaseModel):
    status: str
    source: str
    source_sha256: str
    source_exists: bool
    ffmpeg_executable: str
    input_resolution: list[int]
    input_audio_codec: str | None
    candidates: list[EncodeRun]
    narrow_scope: str = "H264_ENCODING_ONLY_FROM_PREENCODED_CINEFACTORY_TEST_VIDEO"
    quality_comparison: str = "FFMPEG_SSIM_TO_ALREADY_COMPRESSED_INPUT_NOT_BLIND_VIEWER_SCORE"
    prices_measured: bool = False
    gpu_vram_measured: bool = False
    accepted_video_minutes_known: bool = False
    model_or_engine_quality_comparison: bool = False
    license_and_royalty_approved: bool = False
    human_creative_quality_approved: bool = False
    production_qualified: bool = False
    blockers: list[str] = Field(default_factory=list)


def _sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def _ffprobe(ffprobe:str,source:Path):
    p=subprocess.run([ffprobe,"-v","error","-show_streams","-show_format",
        "-of","json",str(source)],capture_output=True,text=True,timeout=30,check=True)
    obj=json.loads(p.stdout)
    vid=next((s for s in obj["streams"] if s["codec_type"]=="video"),None)
    aud=next((s for s in obj["streams"] if s["codec_type"]=="audio"),None)
    if vid is None:raise RuntimeError("CODEC_BENCHMARK_NO_VIDEO_STREAM")
    return vid,aud,obj


def _count_frames(ffprobe:str,path:Path)->int:
    p=subprocess.run([ffprobe,"-v","error","-count_frames",
       "-select_streams","v:0","-show_entries","stream=nb_read_frames",
       "-of","default=noprint_wrappers=1:nokey=1",str(path)],
        capture_output=True,text=True,timeout=60,check=True)
    try:return int(p.stdout.strip())
    except ValueError:raise RuntimeError("FRAME_COUNT_UNMEASURABLE")


def run_codec_experiment(*,source:Path,output_dir:Path,
                         presets:tuple[str,...]=("veryfast","fast","medium"),
                         crf:int=21)->CodecExperimentEvidence:
    ffmpeg=shutil.which("ffmpeg")
    ffprobe=shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:raise RuntimeError("FFMPEG_OR_FFPROBE_UNAVAILABLE")
    source=Path(source).resolve()
    if not source.is_file():raise FileNotFoundError(source)
    output_dir=Path(output_dir).resolve()
    output_dir.mkdir(parents=True,exist_ok=True)
    vid,aud,_=_ffprobe(ffprobe,source)
    reference_frames=_count_frames(ffprobe,source)
    if not 1<=reference_frames<=1200:
        raise RuntimeError("BENCHMARK_SOURCE_FRAME_COUNT_OUTSIDE_SAFE_SCOPE")
    sample_audio=aud["codec_name"] if aud else None
    runs=[]
    for preset in presets:
        if preset not in {"ultrafast","superfast","veryfast","faster","fast","medium","slow"}:
            raise ValueError("UNAPPROVED_PRESET")
        name=f"same_crf{crf}_preset_{preset}.mp4"
        target=output_dir/name
        cmd=[ffmpeg,"-hide_banner","-loglevel","error","-y",
             "-i",str(source),"-map","0:v:0","-map","0:a:0?",
             "-c:v","libx264","-preset",preset,"-crf",str(crf),
             "-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",
             str(target)]
        started=time.perf_counter()
        proc=subprocess.run(cmd,capture_output=True,text=True,timeout=120,check=False)
        seconds=time.perf_counter()-started
        if proc.returncode or not target.is_file():
            raise RuntimeError("CODEC_BENCHMARK_ENCODE_FAILED:"+proc.stderr[-800:])
        tv,ta,_=_ffprobe(ffprobe,target)
        count=_count_frames(ffprobe,target)
        if (int(tv["width"]),int(tv["height"]))!=(
            int(vid["width"]),int(vid["height"])):
            raise RuntimeError("ENCODED_DIMENSIONS_CHANGED")
        if count!=reference_frames:raise RuntimeError("ENCODED_FRAME_COUNT_CHANGED")
        if (ta["codec_name"] if ta else None)!=sample_audio:
            raise RuntimeError("AUDIO_STREAM_UNEXPECTED_CODEC_CHANGE")
        score=subprocess.run([ffmpeg,"-hide_banner","-i",str(target),
             "-i",str(source),"-lavfi","[0:v][1:v]ssim",
             "-an","-f","null","-"],
             capture_output=True,text=True,timeout=120,check=False)
        match=re.findall(r"SSIM .*?All:([0-9.]+)",score.stderr)
        if score.returncode or not match:raise RuntimeError(
            "SSIM_BENCHMARK_FAILED:"+score.stderr[-1000:])
        runs.append(EncodeRun(
            preset=preset,crf=crf,output=str(target),
            output_sha256=_sha(target),
            decoded_video_frames=count,width=int(tv["width"]),
            height=int(tv["height"]),output_bytes=target.stat().st_size,
            ffmpeg_wallclock_seconds=seconds,
            ssim_all=float(match[-1]),video_codec=tv["codec_name"],
            audio_codec=ta["codec_name"] if ta else None,
            acoustic_input_preserved_by_copy=(ta is not None and sample_audio is not None)
        ))
        print("CODEC_EXPERIMENT_RUN",preset,
              "frames",count,"SSIM",match[-1],
              "bytes",runs[-1].output_bytes,
              "wall_seconds",round(seconds,3),flush=True)
    evidence=CodecExperimentEvidence(
        status="CODEC_AB_OBSERVED_NO_AUTOMATIC_PROMOTION",
        source=str(source),source_sha256=_sha(source),
        source_exists=True,ffmpeg_executable=ffmpeg,
        input_resolution=[int(vid["width"]),int(vid["height"])],
        input_audio_codec=sample_audio,candidates=runs,
        blockers=[
            "SSIM_ALONE_CANNOT_CERTIFY_ARTISTIC_QUALITY",
            "ENCODE_ONLY_NOT_RENDER_ENGINE_BENCHMARK",
            "H264_LICENSING_AND_DELIVERY_CONTEXT_NOT_REVIEWED",
            "QUALITY_COST_PER_ACCEPTED_MINUTE_UNMEASURED",
            "SOURCE_IS_EXISTING_COMPRESSED_CLIP_NOT_LOSSLESS_GROUND_TRUTH",
            "NO_AUTOMATIC_PRODUCTION_PROMOTION",
        ],
    )
    (output_dir/"codec_ab_evidence_v192.json").write_text(
        evidence.model_dump_json(indent=2),encoding="utf-8")
    return evidence
