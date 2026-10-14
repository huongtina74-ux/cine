"""v262 fail-closed structural 30-second original-player source audit.
Does NOT independently understand every frame/audio event, hence never promotes G02.
Media held in owner's private .tools; do not commit or redistribute.
"""
from __future__ import annotations
import hashlib
import json
import math
import shutil
import subprocess
import concurrent.futures
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/".tools/maizen_peer_av_v260"
OUT=ROOT/"data/verification/v262_maizen_source_structural_audit"
VIDEOS={"RjyeHZ5hSaE":1561,"7jgzaEmqVQU":1354,"qtWfSIqNfdU":613}

def _check_sound(path:Path)->dict:
    if not path.exists() or path.stat().st_size<=1000:
        return {"file":path.name,"decode_ok":False,"error":"MISSING_OR_EMPTY"}
    exe=shutil.which("ffmpeg")
    if not exe:return {"file":path.name,"decode_ok":False,"error":"FFMPEG_NOT_FOUND"}
    try:
        res=subprocess.run([exe,"-nostdin","-hide_banner","-loglevel","error",
                            "-xerror","-i",str(path),"-map","0:a:0",
                            "-f","null","-"],stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE,timeout=25,check=False)
        return {"file":path.name,"decode_ok":res.returncode==0,
                "bytes":path.stat().st_size,
                "decode_error":res.stderr.decode("utf-8","replace")[-160:]}
    except (OSError,subprocess.TimeoutExpired) as ex:
        return {"file":path.name,"decode_ok":False,"error":type(ex).__name__}

def audit(root:Path=ROOT,write:bool=False,decode_audio:bool=True)->dict:
    folder=root/".tools/maizen_peer_av_v260"
    all_cases=[]
    for vid,length in VIDEOS.items():
        base=folder/vid
        receipt=json.loads((base/"audit.json").read_text(encoding="utf8"))
        if receipt.get("source_id")!=vid or receipt.get("expected_duration")!=length:
            raise ValueError("WRONG_SOURCE_VIDEO_ID_OR_DURATION")
        segments=[]
        sampled_frames=[]
        for n in range(receipt["segments"]):
            segfile=base/f"seg_{n:02d}.json"
            seg=json.loads(segfile.read_text(encoding="utf8"))
            if seg.get("video_id")!=vid or seg.get("status")!="COMPLETE" or seg.get("i")!=n:
                raise ValueError("SOURCE_SEGMENT_NOT_COMPLETE")
            sound_path=base/f"seg_{n:02d}.webm"
            if not sound_path.is_file() or sound_path.stat().st_size!=seg["audio_bytes"]:
                raise ValueError("SEGMENT_AUDIO_SIZE_MISMATCH")
            if hashlib.sha256(sound_path.read_bytes()).hexdigest()!=seg["audio_sha256"]:
                raise ValueError("SEGMENT_AUDIO_HASH_MISMATCH")
            first,last=seg["player_start"],seg["player_end"]
            if not 0<=first<last<=length+2:raise ValueError("BAD_SEGMENT_TIME")
            if segments and first-segments[-1]["end"]>2.0:
                raise ValueError("LARGE_UNRECORDED_SEGMENT_SEAM")
            frames=[]
            for frame in seg["frames"]:
                img=base/"frames"/frame["file"]
                if not img.is_file():raise ValueError("MISSING_SOURCE_IMAGE")
                with Image.open(img) as picture:
                    if picture.width<100 or picture.height<50:
                        raise ValueError("SUSPICIOUS_IMAGE_SIZE")
                    picture.verify()
                if not first-2<=frame["time"]<=last+2:raise ValueError("SOURCE_FRAME_OUT_OF_SEGMENT")
                frames.append(round(float(frame["time"]),3))
                sampled_frames.append({"time":round(float(frame["time"]),3),"file":str(img)})
            segments.append({"index":n,"begin":float(first),"end":float(last),
                             "sound":str(sound_path),"frames":frames})
        if len(sampled_frames)!=receipt["frames"] or len(segments)!=receipt["complete"]:
            raise ValueError("BROWSER_RECEIPT_COUNTER_MISMATCH")
        decode={}
        if decode_audio:
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                status=list(pool.map(_check_sound,[Path(x["sound"]) for x in segments]))
            decode={i:s for i,s in enumerate(status)}
        windows=[]
        for start in range(0,length,30):
            end=min(length,start+30)
            intersects=[x for x in segments if x["end"]>start and x["begin"]<end]
            pictures=[x for x in sampled_frames if start<=x["time"]<end]
            decoded=(all(decode[x["index"]]["decode_ok"] for x in intersects)
                     if decode_audio else None)
            ranges=sorted((max(start,s["begin"]),min(end,s["end"])) for s in intersects)
            # Merge overlapping browser windows; do not double-count overlap.
            merged=[]
            for lo,hi in ranges:
                if merged and lo<=merged[-1][1]:
                    merged[-1]=(merged[-1][0],max(hi,merged[-1][1]))
                else:
                    merged.append((lo,hi))
            covered=sum(max(0,hi-lo) for lo,hi in merged)
            # Track gross gaps even if there is overlap in source player intervals.
            maxgap=max([merged[0][0]-start]+[merged[i+1][0]-merged[i][1]
                       for i in range(len(merged)-1)]+[end-merged[-1][1]]) if merged else end-start
            windows.append({
                "window_index":start//30,"source_begin":start,"source_end":end,
                "frames_collected":len(pictures),
                "frame_timestamps":[p["time"] for p in pictures],
                "audio_segment_ids":[x["index"] for x in intersects],
                "audio_encoded_files_hash_verified":True,
                "audio_decode_ok":decoded,
                "recorded_player_interval_seconds":round(covered,3),
                "maximum_player_timeline_gap_seconds":round(max(0,maxgap),3),
                "independent_native_audio_semantic_review":"PENDING",
                "all_original_motion_frames_semantically_reviewed":False,
                "provisional_machine_status":
                   ("CHECK_SOURCE_GAP_OR_AUDIO" if maxgap>0.3 or decoded is False or not pictures
                    else "SOURCE_MEDIA_STRUCTURALLY_AVAILABLE_NOT_SEMANTIC_QC")
            })
        all_cases.append({
            "video_id":vid,"url":"https://www.youtube.com/watch?v="+vid,
            "expected_duration_sec":length,"source_recording_playback_speed":2,
            "browser_source_segments":len(segments),
            "sparse_original_player_frame_count":len(sampled_frames),
            "30sec_window_count":len(windows),
            "audio_segments_decoded":sum(v.get("decode_ok") is True for v in decode.values()),
            "failed_audio_decodes":[v for v in decode.values() if not v["decode_ok"]],
            "gaps_over_0_3s":[w["window_index"] for w in windows if w["maximum_player_timeline_gap_seconds"]>0.3],
            "first_player_position":segments[0]["begin"],"last_player_position":segments[-1]["end"],
            "full_native_audio_was_listened_at_normal_speed":False,
            "license_ownership_checked":False,
            "windows":windows,
            "qc_gate":"BLOCKED_INDEPENDENT_FRAME_AND_AUDIO_SEMANTICS"})
    result={"schema":"cine.maizen.original_media_structural_audit.v262",
        "video_count":len(all_cases),
        "30_second_windows_count":sum(x["30sec_window_count"] for x in all_cases),
        "browser_segments_count":sum(x["browser_source_segments"] for x in all_cases),
        "sparse_frames_count":sum(x["sparse_original_player_frame_count"] for x in all_cases),
        "audio_decodes_completed":sum(x["audio_segments_decoded"] for x in all_cases),
        "failures_in_audio_decodes":sum(len(x["failed_audio_decodes"]) for x in all_cases),
        "source_playback_was_2x":True,
        "audio_at_2x_capture_is_not_original_speed_listening":True,
        "visual_frame_sampling_is_not_complete_moving_video_review":True,
        "G02":"PENDING_INDEPENDENT_NATIVE_AV_SEMANTIC_QC",
        "reviewer_signoff_exists":False,
        "videos":all_cases}
    if write:
        out=root/"data/verification/v262_maizen_source_structural_audit"
        out.mkdir(parents=True,exist_ok=True)
        p=out/"thirty_second_windows.json"
        p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
        result["report_file"]=str(p)
    return result

if __name__=="__main__":
    r=audit(write=True)
    print(json.dumps({"schema":r["schema"],"videos":r["video_count"],
      "windows":r["30_second_windows_count"],"audio_decoded":r["audio_decodes_completed"],
      "audio_failures":r["failures_in_audio_decodes"],
      "start_end_gaps":{x["video_id"]:x["gaps_over_0_3s"] for x in r["videos"]},
      "G02":r["G02"],"report":r["report_file"]},ensure_ascii=False))
