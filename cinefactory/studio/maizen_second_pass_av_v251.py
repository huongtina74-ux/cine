"""v251 SECOND PASS: source-original browser A/V engineering audit, not human G02.
Verifies 73 <=30-second windows, hashes and decoded sound-second coverage,
supplemental native-speed replay and separate local AudioSet model predictions.
Refuses to convert machine evidence into human independent film/music signoff.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
from .maizen_full_video_gate_v227 import maizen_full_video_review_gate

ROOT=Path(__file__).resolve().parents[2]
POLICY=ROOT/"config/niches/minecraft/maizen_two_reference_second_pass_v251.json"
EVIDENCE=ROOT/".tools/maizen_two_full_av_v244"
VIDEOS=(("zhPBXzHsLuo",38,1117,157,10,("tail_1116","visual_690_720")),
        ("oX6Azwe5QLg",35,1031,132,9,("audio_682",)))

def load_av_second_pass()->dict:
 d=json.loads(POLICY.read_text(encoding="utf8"))
 if (d.get("schema")!="cine.minecraft.maizen_two_source_av_second_pass.v251" or
     d.get("project_id")!="MAI01_WATERFALL" or
     d.get("source_refs")!=["zhPBXzHsLuo","oX6Azwe5QLg"] or
     len(d.get("films",[]))!=2):
    raise ValueError("SOURCE_SECOND_PASS_INVALID_REFERENCE_COHORT")
 for (vid,windows,seconds,frames,pages,patches),film in zip(VIDEOS,d["films"]):
    if (film.get("video_id")!=vid or film.get("qc_30s_windows")!=windows or
        film.get("full_original_audio_1s_bins")!=seconds or
        film.get("original_visual_frames_now_checked")!=frames or
        film.get("view_pages")!=pages or
        len(film.get("second_pass_observations",[]))<7):
        raise ValueError("SOURCE_SECOND_PASS_FALSE_OR_MISSING_VISUAL_AND_AUDIO_OBSERVATION")
    seq=film["second_pass_observations"]
    if seq[0]["from"]!=0 or seq[-1]["to"]!=film["actual_media_seconds"]:
        raise ValueError("SOURCE_SECOND_PASS_SCENE_ENDPOINTS_NOT_CHECKED")
    for i in range(len(seq)):
        if not seq[i].get("visual") or not seq[i].get("speech_function"):
            raise ValueError("SOURCE_SECOND_PASS_OBSERVATION_PLACEHOLDER")
        if i>0 and seq[i-1]["to"]!=seq[i]["from"]:
            raise ValueError("SOURCE_SECOND_PASS_SCENE_GAP")
 p=d["second_pass"]
 if (p["strict_v227_g02_pass"] or p["g03_plus_production_method_go"] or
     p["source_independent_human_auditor_attestation"] or
     p["no_original_audio_second_review_by_human_listening_entire_duration"] is not True or
     p["new_entire_native_movie_video_frame_by_frame_playback_in_this_pass"] or
     p["paid_provider_spend_usd"]!=0):
    raise ValueError("CANNOT_FABRICATE_HUMAN_NATIVE_MEDIA_AUDIT")
 return d

def _local_source_verification(vid:str,wanted:int,seconds:int,frames:int,pages:int,patches:tuple[str,...])->dict:
 result={"video_id":vid,"independent_pcm_second_pass_complete":False,
         "all_30s_original_visual_sound_evidence_windows_available":False,
         "audio_event_second_model_all_windows_complete":False,
         "native_speed_targeted_browser_replays_hashed":False,
         "actual_human_independent_every_frame_every_sound_signoff":False,
         "recognized_voice_transcript_human_corrected":False}
 root=EVIDENCE/vid
 q=root/"independent_pcm_30second_qc_v249.json"
 if not q.is_file() or q.is_symlink():return result
 try:
  d=json.loads(q.read_text(encoding="utf8"))
  intervals=d["per_window"]
  ok=(d.get("video_id")==vid and
      d.get("independently_checked_30s_intervals")==wanted and len(intervals)==wanted and
      d.get("audio_1s_second_bins_total")==seconds and
      d.get("timed_original_audio_segments_independently_pcm_decoded")==math.ceil(d.get("source_local_seconds",0)/38) and
      d.get("source_browser_original_frames_sampled")>=frames and
      len(d.get("audio_seconds_without_reconstructed_pcm",[0]))==0 and
      not d.get("intervals_with_fewer_than_2_source_video_frame_samples") and
      not d.get("raw_trace_errors") and
      d.get("contact_sheet_pages")==pages and
      all(w.get("status")=="AUTO_REVIEWED_PICTURE_SAMPLES_AUDIO_PCM_AND_SPEECH_NOT_HUMAN_APPROVED" and
          w["audio_second_bins_covered"]==w["seconds_in_window"] and
          w["visual_frames_in_window"]>=2 and
          (w["to_s"]-w["from_s"])<=30.01 for w in intervals))
  # Existing "observations" mean sampled pictures + ASR contextual check, not manually watched every original frame.
  patch_ok=True
  for name in patches:
   f=root/f"qc_{name}.json"
   if not f.is_file():patch_ok=False;continue
   v=json.loads(f.read_text(encoding="utf8"))
   src=root/f"qc_{name}.webm"
   if (v.get("source_video_id")!=vid or not v.get("independent_browser_second_pass") or
       not src.is_file() or hashlib.sha256(src.read_bytes()).hexdigest()!=v["sha256_original_browser_audio"]):
      patch_ok=False
  event_file=root/"ast_audio_event_30s_v250.json"
  ast=False;music=0;speech=0
  if event_file.is_file():
   a=json.loads(event_file.read_text(encoding="utf8"))
   ast=(a.get("video_id")==vid and a.get("window_center_original_audio_samples_classified")==wanted
        and len(a.get("each_window",[]))==wanted
        and not a.get("full_30s_music_sfx_detailed_listening")
        and not a.get("independent_human_listener_signed_off")
        and all(e["window_id"]==w["window_id"] and 0<e["sampled_audio_seconds"]<=10.01 for e,w in zip(a["each_window"],intervals)))
   if ast:
    music=a.get("music_model_above_10percent_windows",0)
    speech=a.get("speech_model_above_10percent_windows",0)
  result.update({"independent_pcm_second_pass_complete":bool(ok),
   "all_30s_original_visual_sound_evidence_windows_available":bool(ok),
   "audio_event_second_model_all_windows_complete":bool(ast),
   "native_speed_targeted_browser_replays_hashed":bool(patch_ok),
   "all_30s_windows":wanted if ok else 0,
   "source_visual_frame_samples":d.get("source_browser_original_frames_sampled",0) if ok else 0,
   "audio_1s_bins_covered":seconds if ok else 0,
   "machine_music_estimate_windows":music,"machine_speech_estimate_windows":speech,
   "audio_classifier_interval_length_note":"10s sample per 30s scene; score uncalibrated, NOT exhaustive Foley/music.",
   "qc_screenshot_pages":pages if ok else 0})
 except (OSError,ValueError,TypeError,KeyError,UnicodeError,ZeroDivisionError):
  return result
 return result

def maizen_second_pass_av_evidence()->dict:
 p=load_av_second_pass()
 checks=[_local_source_verification(*entry) for entry in VIDEOS]
 g=maizen_full_video_review_gate()
 return {
  "schema":"cine.minecraft.maizen_second_pass_av_evidence.v251",
  "project_id":p["project_id"],"source_videos":checks,
  "mechanical_sound_frame_qc_all_73_windows":all(x["independent_pcm_second_pass_complete"] and
       x["native_speed_targeted_browser_replays_hashed"] for x in checks),
  "audio_event_model_second_check_all_73_windows":all(x["audio_event_second_model_all_windows_complete"] for x in checks),
  "visual_sample_second_review_windows":sum(x.get("all_30s_windows",0) for x in checks),
  "original_source_frames_sampled":sum(x.get("source_visual_frame_samples",0) for x in checks),
  "each_video_independent_human_direct_sound_picture_qc_signed_off":False,
  "human_complete_original_SFX_music_listening_achieved":False,
  "v227_strict_g02_gate_passed":g["cohort_gate_passed"],
  "g03_to_g28_rendering_backend_production_method_approved":g["cohort_gate_passed"],
  "known_exact_maizen_software_mod_stack":False,
  "separate_sources_three_format_narrative_conclusions":p["common_verified_story_patterns"],
  "important_corrected_finding":p["films"][1]["corrected_vs_previous"],
  "studio_handoffs":p["cinefactory_handoffs"],
  "no_paid_API_used":True,
  "human_review_and_native_av_requirement":"G02 still needs full original moving/native audio semantic observation in <=30s windows and distinct independent source auditor attestation; machine waveform, ASR and AudioSet cannot certify that."
 }
