"""v263: audit exact 11 real-time 1x source re-observations and issue *unsigned* G02 handoff.
No machine source observation can substitute independent sound and moving-film judgement.
"""
import json,hashlib,subprocess,shutil
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def verify(root:Path=ROOT,write:bool=False,decode:bool=True)->dict:
 base=root/".tools/maizen_1x_window_recheck_v263"
 older=root/"data/verification/v262_maizen_source_structural_audit/thirty_second_windows.json"
 summary=json.loads((base/"recheck_summary.json").read_text(encoding="utf8"))
 original=json.loads(older.read_text(encoding="utf8"))
 requested={(v["video_id"],w["window_index"]) for v in original["videos"]
            for w in v["windows"] if w["provisional_machine_status"]=="CHECK_SOURCE_GAP_OR_AUDIO"}
 if len(requested)!=11 or summary.get("requests")!=11 or summary.get("complete")!=11 or summary.get("source_speed")!=1:
  raise ValueError("UNVERIFIED_11_NATIVE_1X_RECAPTURE")
 if summary.get("independent_native_av_semantic_signoff") is not False:
  raise ValueError("AUTOMATIC_G02_PROMOTION_FORBIDDEN")
 verified=[]
 for vid,idx in sorted(requested):
  folder=base/vid/f"window_{idx:03d}"
  receipt=json.loads((folder/"receipt.json").read_text(encoding="utf8"))
  aud=folder/"real_1x_sound.webm"
  if receipt.get("status")!="COMPLETE" or receipt.get("video_id")!=vid or receipt.get("window_index")!=idx or receipt.get("player_speed")!=1:
   raise ValueError("SOURCE_RECHECK_WRONG_VIDEO_OR_SPEED")
  if not aud.is_file() or aud.stat().st_size!=receipt.get("audio_bytes"):
   raise ValueError("MISSING_NATIVE_1X_AUDIO")
  if hashlib.sha256(aud.read_bytes()).hexdigest()!=receipt["audio_sha256"]:
   raise ValueError("SOURCE_1X_AUDIO_HASH_MISMATCH")
  if not receipt["frame_samples"]:
   raise ValueError("SOURCE_RECHECK_NO_VIDEO_IMAGE")
  for item in receipt["frame_samples"]:
   frame=folder/"frames"/item["name"]
   if not frame.is_file() or frame.stat().st_size<1000:
    raise ValueError("SOURCE_RECHECK_MISSING_FRAME")
  ok=None
  if decode:
   ffmpeg=shutil.which("ffmpeg")
   if not ffmpeg:raise FileNotFoundError("FFMPEG_UNAVAILABLE")
   ps=subprocess.run([ffmpeg,"-nostdin","-hide_banner","-loglevel","error",
     "-xerror","-i",str(aud),"-map","0:a:0","-f","null","-"],
     capture_output=True,timeout=25)
   ok=ps.returncode==0
   if not ok:raise ValueError("SOURCE_RECHECK_AUDIO_DECODE_FAILED")
  verified.append({"video_id":vid,"window_index":idx,
     "native_audio_recording_speed":1,"audio_decoded":ok,
     "sound_hash_verified":True,"frame_count":len(receipt["frame_samples"]),
     "player_start":receipt["playback_setup"]["current_time"],
     "player_end":receipt["player_end"],
     "original_interval":receipt["original_30_second_window"],
     "source_re_observed":True,
     "semantic_listener_status":"NEEDS_QUALIFIED_INDEPENDENT_LISTENER",
     "moving_video_reviewer_status":"NEEDS_QUALIFIED_INDEPENDENT_SOURCE_REVIEWER",
     "rounding_at_original_last_second_possible":True,
     "native_audio_file":str(aud)})
 review=[]
 for v in original["videos"]:
  vid=v["video_id"]
  for window in v["windows"]:
   id=window["window_index"]
   alternate=next((z for z in verified if z["video_id"]==vid and z["window_index"]==id),None)
   review.append({"video_id":vid,"window_id":id,
       "seconds":[window["source_begin"],window["source_end"]],
       "original_sampled_frames":window["frames_collected"],
       "native_1x_rechecked":alternate is not None,
       "native_1x_review_file":alternate["native_audio_file"] if alternate else None,
       "independent_motion_semantic_approved":False,
       "independent_audio_semantic_approved":False,
       "speaker_action_music_foley_licensing_check":"PENDING",
       "source_software_unverified":True,
       "reviewer_signature":None})
 if len(review)!=120:raise ValueError("ORIGINAL_FILMS_ARE_NOT_120_WINDOWS")
 out={"schema":"cine.maizen.g02.unsigned_independent_review_bundle.v263",
   "source_review_video_count":3,
   "original_review_windows":len(review),
   "reopened_source_windows":len(verified),
   "1x_source_sound_files_technically_decoded":sum(x["audio_decoded"] is True for x in verified),
   "new_dense_source_frame_samples":sum(x["frame_count"] for x in verified),
   "reviewer_signoff":"NOT_SIGNED",
   "G02":"BLOCKED_INDEPENDENT_1X_NATIVE_AV_SEMANTIC_SIGNOFF",
   "all_11_flagged_windows_re_observed_1x":True,
   "original_video_all_frames_reobserved_1x":False,
   "independent_native_soundtrack_listening_completed":False,
   "video_production_claim_is_approved":False,
   "technical_source_evidence":verified,"pending_reviewer_windows":review}
 if write:
  target=root/"data/verification/v263_maizen_full_story_assets/g02_unsigned_independent_review_queue.json"
  target.parent.mkdir(parents=True,exist_ok=True)
  target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
  md=["# G02 — independent video and audio review queue",
   "","**Technical re-observation: 11/11 source windows recorded at 1×; original G02 remains BLOCKED.**",
   "","Three original films, 120 ≤30-second timeline windows. These source clips are held privately on the user's device.",
   "","An independent qualified reviewer must open the original moving video, listen at original speed, log narration/FX/music and visual causality, document source timecodes, and sign every window. Sound-track licenses and competitor exact software are not inferred.",
   "","| Video ID | Window | Time | 1× recheck | Independent audio | Independent video |",
   "|---|---:|---|---|---|---|"]
  for i in review:
   a,b=i["seconds"]
   ms=lambda s:f"{s//60:02d}:{s%60:02d}"
   md.append(f"| {i['video_id']} | {i['window_id']:03d} | {ms(a)}–{ms(b)} | "+
    ("RECORDED" if i["native_1x_rechecked"] else "NOT REQUESTED")+
    " | PENDING | PENDING |")
  (target.parent/"g02_independent_review_worklist.md").write_text("\n".join(md)+"\n",encoding="utf8")
  out["written_to"]=str(target)
 return out
if __name__=="__main__":
 result=verify(write=True)
 print(json.dumps({"rechecked":result["reopened_source_windows"],
   "native_audio_decoded":result["1x_source_sound_files_technically_decoded"],
   "dense_frames":result["new_dense_source_frame_samples"],
   "review_windows":result["original_review_windows"],
   "G02":result["G02"],"file":result["written_to"]},ensure_ascii=False))
