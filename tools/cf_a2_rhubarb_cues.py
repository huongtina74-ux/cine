#!/usr/bin/env python3
"""CINE A2 Rhubarb CLI bridge: WAV -> timed mouth cues with SHA binding.

Works on Blender 4.5 via JSON; a rig-specific shape-key adapter must consume
the JSON. Cue extraction is not visual lip-sync verification.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
TOOLS=ROOT.parent/".tools"/"rhubarb_1_14_0"
def file_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def find_binary():
    hits=list(TOOLS.rglob("rhubarb.exe")) if TOOLS.is_dir() else []
    if not hits:raise FileNotFoundError("Rhubarb 1.14.0 Windows CLI is not installed")
    return hits[0]
def make_cues(wav, out, transcript=None, speaker_tag=None, binary=None):
    wav=pathlib.Path(wav).resolve();out=pathlib.Path(out).resolve()
    if not wav.is_file():raise FileNotFoundError(str(wav))
    exe=pathlib.Path(binary) if binary else find_binary()
    with tempfile.TemporaryDirectory() as temp:
        raw=pathlib.Path(temp)/"raw_mouth_cues.json"
        args=[str(exe),"-r","phonetic","-f","json","-o",str(raw),str(wav)]
        # Rhubarb optional transcript uses a UTF-8 text file. Never infer or invent words.
        if transcript is not None:
            p=pathlib.Path(temp)/"script.txt"
            p.write_text(transcript,encoding="utf-8")
            args=[str(exe),"-d",str(p),*args[1:]]
        p=subprocess.run(args,capture_output=True,text=True,timeout=180)
        if p.returncode or not raw.is_file():
            raise RuntimeError("Rhubarb error: "+p.stderr[-350:])
        data=json.loads(raw.read_text(encoding="utf-8"))
        cues=data.get("mouthCues",[])
        if not isinstance(cues,list):raise ValueError("Rhubarb produced no mouthCues list")
        data["source_wav_sha256"]=file_sha(wav)
        data["speaker_tag"]=speaker_tag
        data["transcript_sha256"]=(hashlib.sha256(transcript.encode("utf-8")).hexdigest()
                                    if transcript else None)
        data["rhubarb_release"]="v1.14.0"
        data["production_approved"]=False
        data["review_state"]="AUTO_CUES_REQUIRE_RIG_AND_HUMAN_LIPSYNC_QC"
        out.parent.mkdir(parents=True,exist_ok=True)
        if out.exists():raise FileExistsError("Refuse overwrite: "+str(out))
        out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return {"output":str(out),"count":len(cues),"source_wav_sha256":data["source_wav_sha256"],
                "status":data["review_state"]}
def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--wav",type=pathlib.Path,required=True)
    a.add_argument("--out",type=pathlib.Path,required=True)
    a.add_argument("--transcript")
    a.add_argument("--speaker-tag")
    a.add_argument("--binary",type=pathlib.Path)
    z=a.parse_args()
    print(json.dumps(make_cues(z.wav,z.out,z.transcript,z.speaker_tag,z.binary),ensure_ascii=False))
if __name__=="__main__":main()
