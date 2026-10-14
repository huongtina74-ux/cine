"""Bounded direct shot-boundary measurements from authorized local footage.

FFmpeg detects abrupt visual discontinuities; it does NOT understand camera
grammar, character emotions, the script, music or full cinematic quality.
Always label incomplete sampling accurately and preserve source hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
from datetime import datetime,timezone
from pathlib import Path


def digest(file: Path)->str:
    h=hashlib.sha256()
    with file.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def inspect_shot_timeline(source: str|Path, destination: str|Path, *,
                           permission: str, max_scan_seconds: int=180,
                           fps: int=3, scene_threshold: float=0.28,
                           subprocess_timeout_seconds: int=120)->dict:
    """Create a time-coded research index. No copyrighted footage copied."""
    if permission not in ("OWNED","LICENSED","SOURCE_OWNER_PERMISSION"):
        raise PermissionError("Owned/licensed media or source-owner permission required")
    if not 1<=fps<=12 or not 5<=max_scan_seconds<=10800:
        raise ValueError("Invalid bounded timeline scan resolution or window")
    if not (isinstance(scene_threshold,(int,float)) and
            math.isfinite(scene_threshold) and .05<=scene_threshold<=.95):
        raise ValueError("Invalid shot threshold")
    file=Path(source).resolve(strict=True)
    target=Path(destination)
    if target.exists():raise FileExistsError("Immutable timeline report already exists")
    if file.suffix.lower() not in (".mp4",".mov",".webm",".mkv"):
        raise ValueError("Expected direct local video file")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("Local FFmpeg and FFprobe must exist")
    before=digest(file)
    probe=subprocess.run(["ffprobe","-v","error","-show_streams","-show_format",
                          "-of","json",str(file)],capture_output=True,text=True,
                         timeout=20,check=False)
    if probe.returncode!=0:raise ValueError("FFprobe could not read source")
    try:
        inspected=json.loads(probe.stdout)
        movie=next(s for s in inspected.get("streams",[]) if s.get("codec_type")=="video")
        dur=float(inspected.get("format",{}).get("duration",0))
    except (ValueError,TypeError,KeyError,StopIteration,json.JSONDecodeError) as exc:
        raise ValueError("No readable video duration/stream") from exc
    if not math.isfinite(dur) or dur<=0:
        raise ValueError("Missing positive video duration")
    observed=min(dur,float(max_scan_seconds))
    # FPS is deliberately reduced, so boundaries are approximated within ~1/fps.
    filter_chain=f"fps={fps},select=gt(scene\\,{scene_threshold}),showinfo"
    process=subprocess.run(
        ["ffmpeg","-hide_banner","-nostdin","-v","info","-i",str(file),
         "-t",str(observed),"-an","-vf",filter_chain,"-f","null","-"],
        text=True,capture_output=True,timeout=subprocess_timeout_seconds,check=False)
    if process.returncode!=0:
        raise RuntimeError("Shot segmentation failed: "+process.stderr[-360:])
    frames=set()
    for line in process.stderr.splitlines():
        if "showinfo" not in line:continue
        match=re.search(r"pts_time:\s*([0-9]+(?:\.[0-9]+)?)",line)
        if match:
            stamp=float(match.group(1))
            if 0<stamp<observed:
                frames.add(round(stamp,3))
    points=[0.0]+sorted(frames)+[round(observed,3)]
    shots=[{
        "segment_id":f"SEG_{i:04d}","approx_start_s":points[i],
        "approx_end_s":points[i+1],
        "duration_s":round(points[i+1]-points[i],3),
        "detector":"FFMPEG_ABRUPT_VISUAL_CHANGE",
        "character_expression":"UNKNOWN",
        "screenplay_beat":"UNKNOWN",
        "camera_type":"UNKNOWN",
        "sound_design":"UNKNOWN",
        "source_frame_or_audio_for_semantic_conclusions":"NOT_SAMPLED_BY_THIS_STAGE",
    } for i in range(len(points)-1) if points[i+1]>points[i]]
    if digest(file)!=before:
        raise RuntimeError("Source video bytes changed while being read")
    result={
        "schema":"cine.research.shot_timeline.v1",
        "observed_at_utc":datetime.now(timezone.utc).isoformat(),
        "source_file":str(file),"source_sha256":before,
        "permission_claim":permission,"permission_authenticated":False,
        "original_duration_s":round(dur,3),
        "observed_duration_s":round(observed,3),
        "full_duration_analyzed":observed >=dur-.01,
        "coverage_ratio":round(observed/dur,5),
        "resolution_px":[int(movie.get("width",0)),int(movie.get("height",0))],
        "has_audio_stream":any(s.get("codec_type")=="audio" for s in inspected.get("streams",[])),
        "audio_content_analyzed":False,
        "effective_frame_sampling_fps":fps,"shot_change_threshold":scene_threshold,
        "estimated_boundary_uncertainty_seconds":round(1/fps,3),
        "segments":shots,"segment_count":len(shots),
        "report_state":"VISUAL_BOUNDARIES_ONLY_FULL" if observed>=dur-.01
                       else "VISUAL_BOUNDARIES_ONLY_PARTIAL",
        "semantic_video_analysis_completed":False,
        "production_permission":False,
        "next_departments":["annotate source-bound frames in each shot",
                           "transcribe licensed/owned dialogue/audio",
                           "script/acting/camera/art/editorial review and rebuttal",
                           "cross-video contrast against weak controls"],
    }
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result


def main():
    cli=argparse.ArgumentParser(description="Measure actual authorized video shot boundaries")
    cli.add_argument("source")
    cli.add_argument("output")
    cli.add_argument("--permission",required=True,choices=["OWNED","LICENSED","SOURCE_OWNER_PERMISSION"])
    cli.add_argument("--max-seconds",type=int,default=180)
    cli.add_argument("--fps",type=int,default=3)
    cli.add_argument("--threshold",type=float,default=.28)
    args=cli.parse_args()
    result=inspect_shot_timeline(args.source,args.output,permission=args.permission,
                                 max_scan_seconds=args.max_seconds,fps=args.fps,
                                 scene_threshold=args.threshold)
    print(json.dumps({"state":result["report_state"],"segments":result["segment_count"],
                      "coverage_ratio":result["coverage_ratio"],
                      "semantic_video_analysis_completed":False},ensure_ascii=False))


if __name__=="__main__":
    main()
