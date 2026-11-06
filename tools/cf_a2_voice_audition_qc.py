#!/usr/bin/env python3
"""Measure and prepare A2-paced audition copies; NEVER approve/overwrite voices.

Pitch-preserving ffmpeg atempo is a QC audition option, not equivalent to
natural TTS-directed slow speech. Keep original WAVs for human A/B review.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
WPM={"bo":112,"me":108,"juno":115,"Lia":112,"bubu":115,"bix":105,
     "ongngoai":98,"bangoai":100,"ongnoi":106,"banoi":108}
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
def probe_duration(path):
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                      "-of","default=nokey=1:noprint_wrappers=1",str(path)],
                     text=True,capture_output=True,timeout=30)
    if r.returncode:raise ValueError(r.stderr[-250:])
    return float(r.stdout.strip())
def atempo_chain(factor):
    filters=[]
    while factor < .5:
        filters.append("atempo=0.5");factor/=0.5
    while factor > 2.:
        filters.append("atempo=2.0");factor/=2
    filters.append(f"atempo={factor:.6f}")
    return ",".join(filters)
def audit(folder,create_paced=False):
    folder=pathlib.Path(folder);reports=[]
    for metadata in sorted(folder.glob("*.candidate.json")):
        x=json.loads(metadata.read_text(encoding="utf-8"))
        tag=x["tag"];wav=folder/(tag+"_CANDIDATE_NOT_APPROVED.wav")
        if not wav.exists() or sha(wav)!=x["sha256"]:raise ValueError("Candidate WAV missing/changed for "+tag)
        dur=probe_duration(wav)
        if not (0.3<=dur<=30):raise ValueError("Candidate duration invalid for "+tag)
        count=len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?",x["transcript"]))
        wpm=60*count/dur;target=WPM[tag];factor=target/wpm
        out=folder/"a2_paced"/(tag+"_A2_PACE_PREVIEW_NOT_APPROVED.wav")
        report={"tag":tag,"transcript":x["transcript"],"words":count,"raw_seconds":round(dur,3),
                "raw_wpm":round(wpm,1),"a2_target_wpm_proposed":target,
                "source_sha256":sha(wav),
                "spoken_pace_status":"AUDITION_REQUIRED_TOO_FAST" if wpm>target*1.15 else "AUDITION_REQUIRED",
                "pitch_preserving_atempo_requested":round(factor,3),
                "voice_approved":False}
        if create_paced:
            if out.exists():raise FileExistsError(str(out))
            out.parent.mkdir(parents=True,exist_ok=True)
            cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-i",str(wav),
                 "-af",atempo_chain(factor),"-ar","48000","-ac","1",
                 "-c:a","pcm_s16le",str(out)]
            r=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
            if r.returncode or not out.is_file():raise RuntimeError("FFmpeg pace copy failed "+tag+": "+r.stderr[-200:])
            report["a2_preview_path"]=str(out)
            report["a2_preview_seconds"]=round(probe_duration(out),3)
            report["a2_preview_sha256"]=sha(out)
            report["preview_review_state"]="PITCH_PRESERVED_AUDITION_REQUIRED_NOT_APPROVED"
        reports.append(report)
    return {"project_id":"slow_english_a2_bell_leaf","audio_approved":0,
            "casting_candidates_reviewed_by_human":False,
            "candidates_found":len(reports),"voices":reports}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dir",type=pathlib.Path,required=True)
    p.add_argument("--make-a2-previews",action="store_true")
    p.add_argument("--out",type=pathlib.Path,required=True)
    args=p.parse_args();a=audit(args.dir,args.make_a2_previews)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(a,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"candidates_found":a["candidates_found"],"approved":0,
                      "raw_wpm":{x["tag"]:x["raw_wpm"] for x in a["voices"]}},ensure_ascii=False))
