#!/usr/bin/env python3
"""Bell & Leaf independent MEDIA RELEASE GATE (no render or false approvals).

Checks immutable character/location/voice evidence, true 240-frame/24fps MP4,
separately approved dialogue audio, phoneme/viseme timing, and human art QC.
A synthetic smoke render is not an approved Muse film.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, sys
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from cinefactory.studio.slow_english_a2 import BellLeafCanon, CanonError

def sha(p:pathlib.Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()
def json_read(p):
    return json.loads(p.read_text(encoding="utf-8"))
def probe(p:pathlib.Path, video:bool):
    command=["ffprobe","-v","error","-of","json"]
    if video:
        command+=["-count_frames","-select_streams","v:0",
                  "-show_entries","stream=codec_type,width,height,avg_frame_rate,nb_read_frames",
                  "-show_entries","format=duration"]
    else:
        command+=["-show_entries","format=duration"]
    command.append(str(p))
    r=subprocess.run(command,capture_output=True,text=True,timeout=30)
    if r.returncode:raise ValueError("FFPROBE_ERROR:"+r.stderr[-250:])
    return json.loads(r.stdout)
def inspection(repo,shot,video=None,dialogue_wav=None,mouth_cues=None,art_review=None,provider_receipt=None):
    repo=pathlib.Path(repo).resolve();blockers=[];evidence={}
    bible=BellLeafCanon(repo)
    try:
        state=bible.resolve_shot(shot);blockers+=state["blockers"]
        evidence["canonical_tags"]=state["activeCharacterTags"]
        evidence["approved_character_image_sources"]=len(state["character_refs"])
    except (CanonError,ValueError,KeyError) as ex:
        blockers.append("INVALID_SHOT:"+str(ex))
    evidence["shot_duration_seconds"]=shot.get("duration_seconds")
    video_sha=None;voice_sha=None
    if video is None or not pathlib.Path(video).is_file():
        blockers.append("REAL_MUSE_MP4_MISSING")
    else:
        try:
            v=pathlib.Path(video);q=probe(v,True);s=q["streams"][0]
            fps=Fraction(s.get("avg_frame_rate","0/1"));frames=int(s.get("nb_read_frames") or 0)
            duration=float(q["format"]["duration"])
            width,height=int(s["width"]),int(s["height"])
            evidence["video"]={"sha256":sha(v),"frames":frames,"fps":str(fps),
                               "duration":duration,"width":width,"height":height}
            video_sha=sha(v)
            if fps!=24 or frames!=240 or abs(duration-10.0)>1/24+1e-5:
                blockers.append("VIDEO_NOT_EXACT_240_FRAMES_24FPS_10S")
            if width<1280 or height<720 or abs(width/height-16/9)>0.012:
                blockers.append("VIDEO_NOT_16_9_MIN_720P")
        except (ValueError,KeyError,IndexError,OSError,subprocess.TimeoutExpired) as ex:
            blockers.append("VIDEO_PROBE_FAILED:"+str(ex))
    if dialogue_wav is None or not pathlib.Path(dialogue_wav).is_file():
        blockers.append("APPROVED_DIALOGUE_WAV_MISSING")
    else:
        try:
            w=pathlib.Path(dialogue_wav);z=probe(w,False);d=float(z["format"]["duration"])
            voice_sha=sha(w);evidence["dialogue_wav"]={"sha256":voice_sha,"duration":d}
            if d<=0.15 or d>10.0:blockers.append("DIALOGUE_WAV_DURATION_OUTSIDE_SHOT")
        except (ValueError,KeyError,OSError,subprocess.TimeoutExpired) as ex:
            blockers.append("DIALOGUE_WAV_PROBE_FAILED:"+str(ex))
    if mouth_cues is None or not pathlib.Path(mouth_cues).is_file():
        blockers.append("LIP_SYNC_CUES_MISSING")
    else:
        try:
            data=json_read(pathlib.Path(mouth_cues));cues=data.get("mouthCues",[])
            if not isinstance(cues,list) or not cues:raise ValueError("empty mouthCues")
            t=0.0
            for c in cues:
                a,b=float(c["start"]),float(c["end"])
                if a<0 or a<t-1e-4 or b<=a or b>10.0:raise ValueError("cue timing invalid")
                t=b
            if not voice_sha or data.get("source_wav_sha256")!=voice_sha:
                blockers.append("LIPSYNC_WAV_HASH_NOT_BOUND")
            evidence["lip_sync_cues"]=len(cues)
        except (ValueError,KeyError,OSError) as ex:
            blockers.append("LIPSYNC_CUES_INVALID:"+str(ex))
    if art_review is None or not pathlib.Path(art_review).is_file():
        blockers.append("HUMAN_ART_LIPSYNC_QC_MISSING")
    else:
        try:
            rev=json_read(pathlib.Path(art_review))
            flags=("approved","original_character_face","original_body_scale","no_morphing",
                   "actual_character_motion","true_camera_topology","lip_sync_visual_match",
                   "voice_emotion_a2_clear")
            if (not video_sha or rev.get("video_sha256")!=video_sha or
                not rev.get("reviewer") or not rev.get("reviewed_at_utc") or
                any(rev.get(x) is not True for x in flags)):
                blockers.append("HUMAN_ART_LIPSYNC_QC_NOT_APPROVED")
            evidence["human_review_present"]=True
        except (ValueError,OSError) as ex:blockers.append("HUMAN_REVIEW_INVALID:"+str(ex))
    # The provider evidence can be self-supplied; it is therefore consistency
    # evidence only, never proof that a real Muse service generated the clip.
    if provider_receipt is None or not pathlib.Path(provider_receipt).is_file():
        blockers.append("REAL_PROVIDER_TASK_RECEIPT_MISSING")
    else:
        try:
            receipt=json_read(pathlib.Path(provider_receipt))
            required=("provider","task_id","completed_at_utc","downloaded_video_sha256")
            if (any(not isinstance(receipt.get(k),str) or not receipt[k].strip() for k in required)
                or receipt.get("shot_id")!=shot.get("shot_id")
                or receipt.get("task_status")!="COMPLETED"
                or not video_sha
                or receipt.get("downloaded_video_sha256")!=video_sha):
                blockers.append("PROVIDER_TASK_RECEIPT_INCOMPLETE_OR_HASH_MISMATCH")
            else:
                evidence["provider_receipt_fields_consistent"]=True
                evidence["provider"]=receipt["provider"]
                evidence["task_id"]=receipt["task_id"]
        except (ValueError,OSError,KeyError,TypeError) as ex:
            blockers.append("PROVIDER_TASK_RECEIPT_INVALID:"+str(ex))
    # This local script cannot contact a provider to authenticate a receipt.
    # Keep production authorization explicitly false even when all local
    # structural checks pass; external tool verification is a separate gate.
    return {"project_id":"slow_english_a2_bell_leaf","shot_id":shot.get("shot_id"),
            "status":"BLOCKED" if blockers else "PROVIDER_AUTHENTICITY_UNVERIFIED",
            "blockers":sorted(set(blockers)),"evidence":evidence,
            "verified_muse_provider":False,"production_authorized":False,
            "note":"All local structural gates are necessary but never sufficient. Authenticate provider task with a separate trusted connector and verify Muse animation/lip-sync."}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo",type=pathlib.Path,default=ROOT)
    p.add_argument("--shots",type=pathlib.Path,required=True)
    p.add_argument("--index",type=int,default=0)
    p.add_argument("--video",type=pathlib.Path)
    p.add_argument("--dialogue-wav",type=pathlib.Path)
    p.add_argument("--mouth-cues",type=pathlib.Path)
    p.add_argument("--art-review",type=pathlib.Path)
    p.add_argument("--provider-receipt",type=pathlib.Path)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    x=json_read(a.shots);arr=x["shots"] if isinstance(x,dict) and "shots" in x else [x]
    result=inspection(a.repo,arr[a.index],a.video,a.dialogue_wav,a.mouth_cues,a.art_review,a.provider_receipt)
    a.out.parent.mkdir(exist_ok=True,parents=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    sys.exit(0 if result["status"]=="MEDIA_EVIDENCE_GATE_PASS" else 2)
if __name__=="__main__":main()
