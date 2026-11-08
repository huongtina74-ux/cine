#!/usr/bin/env python3
"""Review assistant for a REAL I2V MP4. Produces five sampled frames, NOT an approval.

Never changes the original video, original source still or character Canon.
Treat resulting contact sheet as review-only, NOT an I2V first frame.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

TIMES=(0.0,2.0,5.0,8.0,9.7)
REVIEW_FLAGS=[
 "single_scene_stylized_3d_cgi_all_frames",
 "no_live_action_or_real_person_recast",
 "face_and_eye_geometry_match_original_canon",
 "body_scale_age_hair_outfit_materials_match",
 "set_architecture_furniture_lighting_match",
 "real_visible_character_motion_not_zoom_only",
 "no_extra_unapproved_cast",
 "bubu_spiral_sparkle_and_exactly_one_gold_neck_bell_if_visible",
 "bix_small_robot_without_bell_if_visible",
 "approved_wav_voice_and_mouth_sync_if_dialogue",
]


def run_checked(args:list[str]):
    proc=subprocess.run(args,text=True,capture_output=True,timeout=90)
    if proc.returncode:
        raise RuntimeError(f"MEDIA_COMMAND_FAILED:{args[0]}: {proc.stderr[-400:]}")
    return proc.stdout


def sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(video:Path,outdir:Path,first_frame:Path|None=None,shot_id:str="S001")->dict:
    if not video.is_file():raise ValueError("NO_REAL_VIDEO_PRESENT")
    if not video.suffix.lower() in (".mp4",".mov",".webm"):
        raise ValueError("UNSUPPORTED_VIDEO_FILE")
    outdir.mkdir(parents=True,exist_ok=True)
    data=json.loads(run_checked(["ffprobe","-v","error","-show_entries",
      "stream=index,codec_type,avg_frame_rate,width,height:format=duration",
      "-of","json",str(video)]))
    duration=float(data.get("format",{}).get("duration",0))
    streams=[x for x in data.get("streams",[]) if x.get("codec_type")=="video"]
    if not streams:raise ValueError("NO_VIDEO_STREAM")
    video_stream=streams[0]
    if not 9.7<=duration<=10.4:
        raise ValueError("EXPECTED_10_SECONDS_NOT_A_REAL_10S_CLIP")
    width,height=int(video_stream["width"]),int(video_stream["height"])
    if height<=0 or abs(width/height-16/9)>.02:
        raise ValueError("NOT_16_9_VIDEO")
    thumbs=[]
    for t in TIMES:
        name=f"{shot_id}_t{str(t).replace('.','p')}.png"
        dst=outdir/name
        run_checked(["ffmpeg","-nostdin","-y","-v","error",
                     "-ss",str(t),"-i",str(video),"-frames:v","1",
                     "-vf","scale=960:540:flags=lanczos",str(dst)])
        if not dst.is_file() or dst.stat().st_size<500:
            raise ValueError("VIDEO_REVIEW_FRAME_EXTRACTION_FAILED_AT_"+str(t))
        thumbs.append({"second":t,"path":str(dst),"sha256":sha(dst)})
    # Frame-0 comparisons after resizing can be screened numerically, but
    # no pixel/CLIP metric alone can prove CGI or character identity.
    # We deliberately make no automatic face-match or live-action verdict.
    review={
     "schema":"cine.bell_leaf.i2v.frame_review.v1",
     "shot_id":shot_id,"video_path":str(video.resolve()),
     "video_sha256":sha(video),"duration_seconds_measured":duration,
     "video_dimensions":[width,height],
     "frame_rate_reported":video_stream.get("avg_frame_rate"),
     "first_frame_source":str(first_frame.resolve()) if first_frame else None,
     "first_frame_sha256":sha(first_frame) if first_frame and first_frame.is_file() else None,
     "actual_provider_and_model_verified":False,
     "sampled_frames":thumbs,
     "required_human_qc":{key:None for key in REVIEW_FLAGS},
     "independent_reviewer":None,"reviewed_at_utc":None,
     "QC_status":"AWAITING_INDEPENDENT_VISUAL_AND_AUDIO_REVIEW",
     "production_authorized":False,
     "disclaimer":"A contact sheet is for comparison only. Never use it as model first frame, character sheet, or proof of exact CGI identity."
    }
    dest=outdir/f"{shot_id}_review_pending.json"
    dest.write_text(json.dumps(review,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return review


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--first-frame",type=Path)
    p.add_argument("--shot",default="S001")
    args=p.parse_args(argv)
    try:r=inspect(args.video,args.out_dir,args.first_frame,args.shot)
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status":"BLOCKED","error":str(exc)}))
        return 2
    print(json.dumps({"status":r["QC_status"],"files":[x["path"] for x in r["sampled_frames"]],
                      "review_path":str(args.out_dir/f"{args.shot}_review_pending.json"),
                      "production_authorized":False},indent=2))
    return 0


if __name__=="__main__":sys.exit(main())
