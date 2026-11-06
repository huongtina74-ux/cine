#!/usr/bin/env python3
"""VoxCPM2 voice casting candidates for the EXISTING Bell & Leaf Voice Registry.

Never auto-approve an unreviewed WAV. No model downloading or paid calls in
dry-run. --execute requires an already-installed CUDA VoxCPM2 environment.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config/niches/slow_english_a2/voice_registry.json"
LINES={
"bo":"I have a letter for you. What a wonderful morning!",
"me":"Stay close, Lia. The bell has a special secret.",
"juno":"Look at this small machine. I think it can help us.",
"Lia":"Bubu, listen! I can hear a little bell.",
"bubu":"Oh! The bell is moving! This is so exciting!",
"bix":"I have checked the door. It is safe to go inside.",
"ongngoai":"My dear family, remember what I told you about the bells.",
"bangoai":"Somewhere beyond the hills, our family will meet again.",
"ongnoi":"Come inside! I have a funny story to tell you.",
"banoi":"Would you like some warm tea? You look very tired."
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cast_character(tag,entry):
    desc=", ".join((entry["voice_timbre"],entry["delivery_direction"],
                    "natural American English", "clearly paced for A2 learners",
                    "genuinely expressive but not exaggerated",
                    "original character voice, no recognizable real actor imitation"))
    # VoxCPM2 Voice Design format: parenthesized description before spoken text.
    return f"({desc}){LINES[tag]}"
def create_plan(registry,tags):
    return [{"tag":tag,"name":registry[tag]["display_name"],
             "voice_profile_key":registry[tag]["voice_profile_key"],
             "candidate_text":cast_character(tag,registry[tag]),
             "status":"PENDING_CANDIDATE_AUDIO_NOT_APPROVED"} for tag in tags]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tag",default="all")
    p.add_argument("--out",type=pathlib.Path,default=ROOT/"data/slow_english_a2/voice_cast_candidates")
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    data=json.loads(REGISTRY.read_text(encoding="utf-8"))
    voices=data["voices"];tags=list(voices) if a.tag=="all" else [a.tag]
    if any(x not in voices for x in tags):p.error("Unknown canonical character tag")
    plan=create_plan(voices,tags)
    if not a.execute:
        print(json.dumps({"mode":"DRY_RUN","model":"openbmb/VoxCPM2","voice_approved":0,
                          "candidates":plan},ensure_ascii=False,indent=2));return
    try:
        import torch, soundfile as sf
        from voxcpm import VoxCPM
    except ImportError as ex:
        raise SystemExit(f"BLOCKED_MODEL_RUNTIME_NOT_INSTALLED: {ex}; install dedicated VoxCPM2 CUDA venv")
    if not torch.cuda.is_available():
        raise SystemExit("BLOCKED_NO_CUDA_TORCH: do NOT run 2B VoxCPM2 using CPU-only torch")
    a.out.mkdir(parents=True,exist_ok=True)
    model=VoxCPM.from_pretrained("openbmb/VoxCPM2",load_denoiser=False)
    for item in plan:
        tag=item["tag"];path=a.out/(tag+"_CANDIDATE_NOT_APPROVED.wav")
        if path.exists():raise SystemExit(f"Candidate exists, refusing overwrite: {path}")
        # VoxCPM2 2.0.3 does not accept seed= in _generate; set the
        # PyTorch RNG explicitly, preserving a recorded candidate seed.
        torch.manual_seed(a.seed)
        if torch.cuda.is_available():torch.cuda.manual_seed_all(a.seed)
        wav=model.generate(text=item["candidate_text"],cfg_value=2.0,
                           inference_timesteps=10)
        sf.write(str(path),wav,model.tts_model.sample_rate)
        record={"tag":tag,"model":"openbmb/VoxCPM2","seed":a.seed,
                "candidate_wav":str(path),"sha256":sha(path),
                "voice_approved":False,"source":"VOICE_DESIGN_SYNTHETIC",
                "rights_review_required":True,"artistic_review_required":True,
                "transcript":LINES[tag]}
        path.with_suffix(".candidate.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"tag":tag,"status":"GENERATED_CANDIDATE_AWAITING_REVIEW","path":str(path)},ensure_ascii=False))
if __name__=="__main__":main()
