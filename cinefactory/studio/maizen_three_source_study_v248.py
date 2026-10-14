"""v248 Maizen 3-video first-party Chrome source study, read-only and fail-closed.

The browser playback+MediaRecorder+local ASR are an independent source research
route (not vidIQ) but are NOT a separate independent critic's original native
media semantic frame-by-frame/SFX/music signoff. v227 G02 remains mandatory.
"""
from __future__ import annotations
import json
from pathlib import Path
from .maizen_full_video_gate_v227 import maizen_full_video_review_gate

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"config/niches/minecraft/maizen_three_reference_av_study_v248.json"
LOCAL=ROOT/".tools/maizen_two_full_av_v244"
FIRST_AUDIO_AUDIT=ROOT/".tools/maizen_audio_full_v239/maizen_audio_audit_v242.json"
IDS=("zhPBXzHsLuo","oX6Azwe5QLg")

def load_three_source_study()->dict:
    p=json.loads(SOURCE.read_text(encoding="utf8"))
    if p.get("schema")!="cine.minecraft.maizen_three_references_first_party_study.v248":
        raise ValueError("THREE_SOURCE_STUDY_SCHEMA")
    if p.get("project_id")!="MAI01_WATERFALL" or p["first_source"]["video_id"]!="ZmT0ITUGUII":
        raise ValueError("MAIZEN_SOURCE_COHORT_IDENTITY")
    sources=p.get("remaining_references",[])
    if len(sources)!=2 or tuple(x["video_id"] for x in sources)!=IDS:
        raise ValueError("MAIZEN_TWO_MISSING_OR_WRONG_IDS")
    for film,intervals,duration in zip(sources,(30,28),(1116.601,1030.741)):
        if (film["complete_browser_segments"]!=intervals or
            film["original_audio_segments"]!=intervals or
            film["whisper_segments_complete"]!=intervals or
            abs(film["duration_local_s"]-duration)>.15 or
            film["original_video_frames_sampled"]<100 or
            film["recognized_words_uncorrected"]<1000 or
            "NOT_INDEPENDENT_ART_SOUND_QC" not in film["source_visual_audio_status"]):
            raise ValueError("SOURCE_CANNOT_BE_MISREPORTED_AS_FULL_AUDIO_SEMANTIC_QC")
        scenes=film.get("scenes",[])
        if len(scenes)<7 or scenes[0]["start"]!=0 or scenes[-1]["end"]!=film["duration_local_s"]:
            raise ValueError("SOURCE_SCENE_START_END_MISSING")
        if any(
            scenes[i]["end"]!=scenes[i+1]["start"]
            or not scenes[i]["visual"] or not scenes[i]["voice_story"]
            for i in range(len(scenes)-1)
        ):
            raise ValueError("TIMELINE_OR_VISUAL_VOICE_NOT_COVERED")
    flags=p["safety"]
    if (flags["exact_competitor_software_confirmed"] or
        flags["independent_full_media_30sec_interval_review_signed_off"] or
        flags["strict_v227_cohort_gate_passed"] or
        not flags["local_audio_and_screenshots_git_ignored"] or
        not flags["zero_new_external_api_spend"] or
        not flags["original_competitor_movies_not_redistributed"]):
        raise ValueError("UNAUTHORIZED_COMPETITOR_TECHNOLOGY_OR_SOURCE_APPROVAL")
    return p

def _local_source_status(source:dict)->dict:
    vid=source["video_id"]
    basic={"video_id":vid,"whole_original_browser_av_position_trace_verified":False,
           "automatic_local_asr_all_segments_verified":False,
           "original_first_5s_audio_patch_verified":False,
           "actual_native_audio_human_review_completed":False,
           "independent_source_auditor_signed_off":False}
    folder=LOCAL/vid
    auditfile=folder/"independent_audio_visual_audit.json"
    patchfile=folder/"original_first_5s.json"
    if not auditfile.is_file() or not patchfile.is_file():
        return basic
    try:
        audit=json.loads(auditfile.read_text(encoding="utf8"))
        patch=json.loads(patchfile.read_text(encoding="utf8"))
        segments=source["complete_browser_segments"]
        valid=(audit["source_id_from_browser"]==vid and
               audit["total_segments_required"]==segments and
               audit["complete_av_segments"]==segments and
               audit["recorded_opus_audio_segments"]==segments and
               audit["whisper_segments_transcribed"]==segments and
               audit["frame_samples"]>=source["original_video_frames_sampled"] and
               audit["audio_sha_unique"] and
               not audit["seam_errors"] and
               abs(audit["source_actual_media_duration"]-source["duration_local_s"])<.2 and
               audit["source_end"]>=source["duration_local_s"]-.8 and
               audit["source_begin"]<=1.5)
        validpatch=(patch["video_id"]==vid and patch["start"]<=.1 and
                    patch["end"]>=4.0 and len(patch["sha256"])==64 and
                    (folder/"original_first_5s.webm").is_file())
        basic.update({
            "whole_original_browser_av_position_trace_verified":bool(valid),
            "automatic_local_asr_all_segments_verified":bool(valid),
            "original_first_5s_audio_patch_verified":bool(validpatch),
            "segments_verified":segments if valid else 0,
            "original_frames_sampled":audit["frame_samples"] if valid else 0,
            "asr_words_uncorrected":audit["uncorrected_recognized_words"] if valid else 0,
        })
    except (KeyError,ValueError,TypeError,UnicodeError,OSError):
        pass
    return basic

def maizen_three_source_video_study()->dict:
    p=load_three_source_study()
    from .maizen_browser_source_review_v237 import maizen_browser_source_study
    first=maizen_browser_source_study()
    rest=[_local_source_status(x) for x in p["remaining_references"]]
    first_audio=False
    if FIRST_AUDIO_AUDIT.is_file() and not FIRST_AUDIO_AUDIT.is_symlink():
        try:
            evidence=json.loads(FIRST_AUDIO_AUDIT.read_text(encoding="utf8"))
            first_audio=(evidence.get("audio_segments_captured")==45 and
                         evidence.get("automatic_asr_all_complete") is True and
                         evidence.get("full_original_audio_source_timeline_path_0_to_1684_461") is True)
        except (OSError,ValueError,UnicodeError):
            pass
    enough=(first["source_browser_full_timeline_verified_by_local_trace"] and first_audio and
           all(x["whole_original_browser_av_position_trace_verified"] and
               x["automatic_local_asr_all_segments_verified"] and
               x["original_first_5s_audio_patch_verified"] for x in rest))
    g=maizen_full_video_review_gate()
    return {
       "schema":"cine.minecraft.three_video_original_browser_research.v248",
       "project_id":p["project_id"],
       "three_selected_original_browser_timeline_audio_data_acquired":bool(enough),
       "first_source_browser_video_id":"ZmT0ITUGUII",
       "first_source_original_timeline_verified":first["source_browser_full_timeline_verified_by_local_trace"],
       "first_source_original_audio_and_asr_local_receipt_verified":bool(first_audio),
       "additional_reference_videos":rest,
       "total_original_browser_segmentation_windows":(45+sum(x.get("segments_verified",0) for x in rest)) if enough else None,
       "first_party_video_frame_samples":first["captured_video_sample_frames"]+sum(x["original_frames_sampled"] for x in rest) if enough else None,
       "format_comparison":p["comparison"],
       "creative_generalizable_lessons":p["generalizable_lessons"],
       "company_handoffs":p["production_studio_handoffs"],
       "source_specific_visual_speech_summaries":[{"video_id":x["video_id"],"title":x["title"],"scenes":x["scenes"]} for x in p["remaining_references"]],
       "native_audio_music_sfx_comprehensively_human_approved":False,
       "every_visual_frame_independently_reviewed":False,
       "exact_software_mods_game_versions_proven":False,
       "secondary_independent_auditor_signed_off":False,
       "strict_v227_independent_3video_av_gate_passed":g["cohort_gate_passed"],
       "g03_to_g28_competitor_method_production_promotion_allowed":g["cohort_gate_passed"],
       "credits_spent_by_this_study":0,
       "no_film_uploaded_or_published":True,
       "note":"First-party local browser playback and automatic speech are demonstrated across all three selected sources; this is not proof of complete per-frame human picture/audio QC or rival private technique."
    }
