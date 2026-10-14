"""Explicit offline local reference-video verification; zero downloading/API spend.

This command may decode the entire user-provided original source video and audio,
which can take minutes on a 28-minute episode. Runs only when directly called
on an allowed video ID. ffprobe/ffmpeg are invoked without shell, network or
credentials, and may read only a file in the fixed local source-media folder.
Successful decoding != a person/vision reviewer watched and understood footage.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import shutil
import subprocess

from .maizen_full_video_gate_v227 import (
    MEDIA_DIR,REVIEW_DIR,load_full_video_policy,selected_maizen_video_ids,
)

def verify_reference_media(video_id:str)->dict:
    if video_id not in selected_maizen_video_ids():
        raise ValueError("UNKNOWN_MAIZEN_REFERENCE_ID")
    policy=load_full_video_policy()
    source=next(v for v in policy["required_references"] if v["video_id"]==video_id)
    matches=[MEDIA_DIR/(video_id+"."+ext) for ext in ("mp4","mkv","webm")]
    present=[f for f in matches if f.is_file() and not f.is_symlink()]
    if len(present)!=1:
        raise ValueError("PROVIDE_EXACTLY_ONE_LOCAL_AUTHORIZED_COMPLETE_VIDEO_WITH_AUDIO")
    path=present[0]
    ffprobe=shutil.which("ffprobe")
    ffmpeg=shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        raise RuntimeError("FFPROBE_AND_FFMPEG_REQUIRED")
    probe=subprocess.run(
        [ffprobe,"-v","error","-show_entries",
         "format=duration:stream=codec_type,duration",
         "-of","json",str(path)],capture_output=True,text=True,
        shell=False,timeout=30,check=False,
    )
    if probe.returncode!=0:
        raise RuntimeError("SOURCE_VIDEO_PROBE_FAILED")
    metadata=json.loads(probe.stdout)
    types=[x.get("codec_type") for x in metadata.get("streams",[])]
    duration=float(metadata.get("format",{}).get("duration",0))
    if "video" not in types or "audio" not in types:
        raise RuntimeError("SOURCE_MUST_HAVE_BOTH_MOVING_VIDEO_AND_AUDIO")
    if abs(duration-source["duration_seconds"])>2:
        raise RuntimeError("SOURCE_DURATION_SHORTER_OR_WRONG_EPISODE")
    # Need full moving visual & audio decoding, NOT first/last 10-second previews.
    def check_map(stream_map:str) -> bool:
        proc=subprocess.run(
            [ffmpeg,"-hide_banner","-nostdin","-v","error","-xerror",
             "-i",str(path),"-map",stream_map,"-f","null","-"],
            capture_output=True,text=True,shell=False,timeout=1800,check=False,
        )
        return proc.returncode==0
    video_ok=check_map("0:v:0")
    audio_ok=check_map("0:a:0")
    if not (video_ok and audio_ok):
        raise RuntimeError("FULL_SOURCE_VIDEO_OR_AUDIO_DECODE_FAILED")
    digest=sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            digest.update(block)
    receipt={
        "schema":"cine.minecraft.media_full_decode.v227",
        "video_id":video_id,"media_sha256":digest.hexdigest(),
        "relative_path":path.relative_to(MEDIA_DIR.parent.parent.parent).as_posix(),
        "duration_seconds":duration,
        "has_video_stream":True,"has_audio_stream":True,
        "video_decode_full_success":video_ok,"audio_decode_full_success":audio_ok,
        "decoded_source_full_duration":True,
        "human_or_model_review_of_all_frames_and_sound":False,
        "production_or_method_research_approved":False,
    }
    REVIEW_DIR.mkdir(parents=True,exist_ok=True)
    target=REVIEW_DIR/(video_id+".media_receipt.json")
    if target.is_symlink():
        raise ValueError("UNTRUSTED_RECEIPT_SYMLINK")
    target.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",
                      encoding="utf8")
    return receipt
