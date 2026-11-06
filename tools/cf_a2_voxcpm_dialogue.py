#!/usr/bin/env python3
"""Bell & Leaf guarded VoxCPM2 dialogue worker (voice-locked, 10-second shot).

Only generates dialogue after human approval and SHA-verified reference voice.
Plans may be generated without approved audio; never silently fall back to a new
speaker/model/voice, use generic narrator, or fake approval.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
REGISTRY="config/niches/slow_english_a2/voice_registry.json"
def file_sha(p:pathlib.Path):return hashlib.sha256(p.read_bytes()).hexdigest()
def read_json(path):return json.loads(path.read_text(encoding="utf-8"))
def clean_style(s):
    s=re.sub(r"\s+"," ",str(s or "")).strip()
    if len(s)>160 or any(c in s for c in "()<>[]{}"):raise ValueError("Unsafe or overlong emotion direction")
    return s
def plan_shot(repo,shot):
    repo=pathlib.Path(repo).resolve()
    reg=read_json(repo/REGISTRY)["voices"]
    active=shot.get("activeCharacterTags")
    if shot.get("duration_seconds")!=10:raise ValueError("FIXED_10S_REQUIRED")
    if not isinstance(active,list) or len(active)!=len(set(active)) or any(t not in reg for t in active):
        raise ValueError("INVALID_CHARACTER_TAGS")
    lines=shot.get("dialogue",[])
    if not isinstance(lines,list):raise ValueError("DIALOGUE_MUST_BE_LIST")
    blockers=[];orders=[]
    for i,line in enumerate(lines):
        tag=line.get("speaker_tag")
        text=" ".join(str(line.get("text") or "").split()).strip()
        if tag not in active or not text:raise ValueError("DIALOGUE_SPEAKER_OR_TEXT_INVALID")
        v=reg[tag];vpath=v.get("reference_wav_path") or v.get("sample_wav")
        sha=v.get("reference_wav_sha256") or v.get("sample_sha256")
        ref=(repo/vpath).resolve() if vpath else None
        blocked=[]
        if v.get("approval_status")!="APPROVED":blocked.append("VOICE_NOT_HUMAN_APPROVED:"+tag)
        if not (v.get("approved_by") and v.get("approved_at")):blocked.append("VOICE_APPROVAL_EVIDENCE_MISSING:"+tag)
        if v.get("voice_provider")!="VoxCPM2":blocked.append("VOICE_PROVIDER_NOT_VOXCPM2:"+tag)
        if not v.get("voice_model_version"):blocked.append("MODEL_VERSION_NOT_LOCKED:"+tag)
        if not v.get("voice_id"):blocked.append("VOICE_ID_NOT_LOCKED:"+tag)
        if not (ref and ref.is_relative_to(repo) and ref.is_file() and sha and file_sha(ref)==sha):
            blocked.append("MASTER_WAV_MISSING_OR_HASH_INVALID:"+tag)
        if not (v.get("transcript") and isinstance(v.get("transcript"),str)):
            blocked.append("MASTER_WAV_TRANSCRIPT_MISSING:"+tag)
        # Require traceable rights clearance, not simply an approved name.
        rights=v.get("rights_provenance") or v.get("rights_record")
        if not rights:blocked.append("VOICE_RIGHTS_RECORD_MISSING:"+tag)
        style=clean_style(line.get("delivery") or line.get("emotion") or "calm, clear, naturally expressive")
        prompt=f"({style}; slow and clear American English A2, warm natural speaking pace){text}"
        orders.append({"line_index":i,"tag":tag,"text":text,"voice_profile_key":v.get("voice_profile_key"),
                       "voice_id":v.get("voice_id"),"model":"openbmb/VoxCPM2",
                       "version":v.get("voice_model_version"),"reference_wav_path":str(ref) if ref else None,
                       "reference_sha256":sha,"text_for_model":prompt,"blockers":blocked})
        blockers.extend(blocked)
    # A 10s shot can contain >1 line, but stitching requires approved dialogue
    # start times. Fail closed to avoid overlapping lips/voices.
    if len(lines)>1:
        start_times=[x.get("start_seconds") for x in lines]
        if any(not isinstance(t,(int,float)) or t<0 or t>=10 for t in start_times) or start_times!=sorted(start_times):
            blockers.append("MULTISPEAKER_DIALOGUE_CUE_TIMINGS_REQUIRED")
    return {"shot_id":shot.get("shot_id"),"duration_seconds":10,"status":"BLOCKED" if blockers else "READY_FOR_CANDIDATE_GENERATION",
            "blockers":sorted(set(blockers)),"orders":orders,"voice_approved_in_this_run":False}
def execute(repo,shot,folder,seed=42):
    data=plan_shot(repo,shot)
    if data["blockers"]:raise RuntimeError("BLOCKED_CANONICAL_VOICE: "+",".join(data["blockers"]))
    try:
        import torch, soundfile as sf
        from voxcpm import VoxCPM
    except ImportError as e:raise RuntimeError("CUDA_TTS_ENV_NOT_INSTALLED: "+str(e))
    if not torch.cuda.is_available():raise RuntimeError("CUDA_TTS_ENV_REQUIRED")
    folder=pathlib.Path(folder).resolve();folder.mkdir(parents=True,exist_ok=True)
    model=VoxCPM.from_pretrained("openbmb/VoxCPM2",load_denoiser=False)
    outputs=[]
    for item in data["orders"]:
        f=folder/f"{data['shot_id']}_line_{item['line_index']:02d}_{item['tag']}_REVIEW.wav"
        if f.exists():raise FileExistsError("Refuse overwrite "+str(f))
        torch.manual_seed(seed)
        if torch.cuda.is_available():torch.cuda.manual_seed_all(seed)
        wav=model.generate(text=item["text_for_model"],reference_wav_path=item["reference_wav_path"],
                           cfg_value=2.0,inference_timesteps=10)
        sf.write(str(f),wav,model.tts_model.sample_rate)
        import subprocess
        q=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of",
                          "default=nokey=1:noprint_wrappers=1",str(f)],
                         capture_output=True,text=True,timeout=20)
        if q.returncode:raise RuntimeError("FFPROBE_FAILED:"+q.stderr[-200:])
        duration=float(q.stdout.strip())
        if duration<=0 or duration>8.0:
            outputs.append({"path":str(f),"sha256":file_sha(f),"duration":duration,"status":"REJECT_TIMING_8S_LIMIT"})
            break
        outputs.append({"path":str(f),"sha256":file_sha(f),"duration":duration,
                        "status":"REVIEW_REQUIRED_NOT_APPROVED","speaker_tag":item["tag"],
                        "master_reference_sha256":item["reference_sha256"]})
    result={"shot_id":data["shot_id"],"output_files":outputs,
            "status":"CANDIDATE_REVIEW_REQUIRED","production_authorized":False}
    (folder/f"{data['shot_id']}_voice_gen_report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--shots",type=pathlib.Path,required=True)
    a.add_argument("--index",type=int,default=0)
    a.add_argument("--repo",type=pathlib.Path,default=ROOT)
    a.add_argument("--out",type=pathlib.Path,default=ROOT/"data/slow_english_a2/generated_dialogue")
    a.add_argument("--execute",action="store_true")
    args=a.parse_args()
    j=read_json(args.shots);shots=j.get("shots") if isinstance(j,dict) else None
    if not shots or args.index>=len(shots):raise SystemExit("MISSING_SHOT_INDEX")
    s=shots[args.index]
    if args.execute:
        try:
            result=execute(args.repo,s,args.out)
            print(json.dumps(result,ensure_ascii=False))
        except (RuntimeError,ValueError,OSError) as e:raise SystemExit(str(e))
    else:
        print(json.dumps(plan_shot(args.repo,s),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
