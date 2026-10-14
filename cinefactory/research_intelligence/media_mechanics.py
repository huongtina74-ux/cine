"""Authorized full-video mechanical study: cuts, sound silences and open review.

Real evidence about scene boundaries, duration and audio silences. NOT an
automatic screenplay/acting/music/semantic reviewer. Caller declares rights
but the declaration is not independently authenticated.
"""
from __future__ import annotations
import argparse,hashlib,json,math,re,statistics,subprocess
from pathlib import Path
from datetime import datetime,timezone

from .shot_timeline import inspect_shot_timeline

SILENCE_START=re.compile(r"silence_start:\s*([\d.]+)")
SILENCE_END=re.compile(r"silence_end:\s*([\d.]+)")
AUDIO_DEPTS=("dialogue_transcript","soundtrack_origin_and_rights",
             "foley_causality","music_emotion_timing","speech_intelligibility")


def prepare_media_mechanics(source:str|Path, output_dir:str|Path, *,
                             permission:str, max_scan_seconds:int=1800,
                             fps:int=3, min_silence_seconds:float=.5) -> dict:
    if not .2<=min_silence_seconds<=10:
        raise ValueError("Silence gate must be bounded")
    folder=Path(output_dir).resolve()
    if folder.exists():raise FileExistsError("Media mechanics output is immutable")
    # Stage into the same new folder, preserve each intermediate/source hash.
    # Failure may leave partial diagnostic files, but never grants production.
    folder.mkdir(parents=True)
    timeline=inspect_shot_timeline(source, folder/"visual_timeline.json",
                                   permission=permission,max_scan_seconds=max_scan_seconds,
                                   fps=fps)
    observed=timeline["observed_duration_s"]
    source_hash=timeline["source_sha256"]
    silences=[];audio_status="NO_AUDIO_TRACK"
    if timeline["has_audio_stream"]:
        audio_status="SILENCE_MEASURE_PENDING"
        run=subprocess.run([
            "ffmpeg","-hide_banner","-nostdin","-v","info",
            "-i",str(Path(source).resolve()),"-t",str(observed),"-vn",
            "-af",f"silencedetect=noise=-35dB:d={min_silence_seconds}",
            "-f","null","-"
        ],capture_output=True,text=True,timeout=max(30,int(observed*2+20)),check=False)
        if run.returncode!=0:
            audio_status="AUDIO_ANALYSIS_FAILED"
        else:
            starts=[];audio_status="SILENCE_ENVELOPE_MEASURED_NO_SEMANTICS"
            for line in run.stderr.splitlines():
                m=SILENCE_START.search(line)
                if m:starts.append(float(m.group(1)))
                end=SILENCE_END.search(line)
                if end:
                    endtime=float(end.group(1))
                    if starts:
                        from_s=starts.pop(0)
                        silences.append({"start_s":round(from_s,3),
                                         "end_s":round(endtime,3),
                                         "duration_s":round(endtime-from_s,3),
                                         "interpretation":"QUIET_OR_SILENT_AUDIO_NOT_SPEECH_CLASSIFICATION"})
            for first in starts:
                silences.append({"start_s":round(first,3),"end_s":round(observed,3),
                                 "duration_s":round(max(0,observed-first),3),
                                 "interpretation":"QUIET_OR_SILENT_AUDIO_NOT_SPEECH_CLASSIFICATION"})
    durations=[s["duration_s"] for s in timeline["segments"]]
    observations={
        "schema":"cine.research.authorized_media_mechanics.v1",
        "state":"MECHANICS_MEASURED_SEMANTICS_PENDING",
        "observed_at_utc":datetime.now(timezone.utc).isoformat(),
        "source_media":str(Path(source).resolve()),"source_sha256":source_hash,
        "permission_declared":permission,"permission_authenticated":False,
        "timeline_file":str(folder/"visual_timeline.json"),
        "timeline_sha256":hashlib.sha256((folder/"visual_timeline.json").read_bytes()).hexdigest(),
        "observed_duration_s":observed,
        "full_video_duration_covered":timeline["full_duration_analyzed"],
        "coverage_ratio":timeline["coverage_ratio"],
        "segment_count":timeline["segment_count"],
        "cut_rate_per_minute_proxy":round(60*max(0,len(durations)-1)/observed,2) if observed else 0,
        "median_segment_duration_proxy_s":round(statistics.median(durations),2) if durations else None,
        "audio_status":audio_status,"silence_events":silences,
        "sound_semantics_understood":False,
        "script_or_character_understood":False,
        "camera_lenses_verified":False,
        "character_identity_verified":False,
        "story_quality_certified":False,
        "observation_worklist":[
            {"segment_id":x["segment_id"],"start_s":x["approx_start_s"],
             "end_s":x["approx_end_s"],
             "direct_frame_evidence":"REQUIRES_AUTHORIZE_FRAME_OBSERVATION",
             "script":"NOT_OBSERVED","acting_expression":"NOT_OBSERVED",
             "shot_size_camera_motion":"NOT_OBSERVED","world_props":"NOT_OBSERVED",
             "lighting_shading":"NOT_OBSERVED","audio_semantics":"NOT_OBSERVED",
             "editing_purpose":"NOT_OBSERVED","reviewer_authentication":"PENDING"}
            for x in timeline["segments"]
        ],
        "required_audio_research":list(AUDIO_DEPTS),
        "quality_proved_against_competitor":False,
        "production_permission":False,
    }
    (folder/"media_mechanics.json").write_text(json.dumps(observations,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return observations


if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("video");cli.add_argument("output_dir")
    cli.add_argument("--permission",required=True,
                     choices=["OWNED","LICENSED","SOURCE_OWNER_PERMISSION"])
    cli.add_argument("--max-seconds",type=int,default=1800)
    cli.add_argument("--fps",type=int,default=3)
    a=cli.parse_args()
    r=prepare_media_mechanics(a.video,a.output_dir,permission=a.permission,
                              max_scan_seconds=a.max_seconds,fps=a.fps)
    print(json.dumps({"state":r["state"],"segments":r["segment_count"],
                      "audio":r["audio_status"],"quality_proved":False}))
