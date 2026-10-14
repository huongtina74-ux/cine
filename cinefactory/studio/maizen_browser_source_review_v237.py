"""v237: read-only, honestly scoped full source browser playback receipts.

45 original Chrome video-timeline segments plus sampled stills and audio RMS.
This is stronger than public metadata but weaker than a full independently
attested semantic review of entire original moving video AND spoken/sound
tracks. It must NEVER override G02/G03 strict source gate.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"config/niches/minecraft/maizen_browser_visual_evidence_v237.json"
AUDIT=ROOT/".tools/maizen_browser_full_source_audit_v236.json"

def load_maizen_browser_study()->dict:
    d=json.loads(SOURCE.read_text(encoding="utf8"))
    if (d.get("schema")!="cine.minecraft.maizen_real_browser_visual_evidence.v237"
        or d.get("video_id")!="ZmT0ITUGUII"
        or d.get("source_duration_seconds")!=1684.461
        or len(d.get("scene_timeline",[]))!=10
        or d.get("round_count")!=7):
        raise ValueError("MAIZEN_ORIGINAL_BROWSER_STUDY_INVALID")
    c=d["capture"]
    if (c["research_gate_v227_passed"] or
        c["complete_audio_speech_and_sfx_semantically_analyzed"] or
        c["independent_full_audio_qc"] or
        c["raw_full_video_file_available"] or
        c["native_audio_recording_available"] or
        c["other_required_maizen_videos_reviewed"]!=0 or
        not d["no_auto_production_promotions"]):
        raise ValueError("CANNOT_CLAIM_COMPLETE_SOUND_OR_STUDIO_PRODUCTION")
    seq=d["scene_timeline"]
    if seq[0]["from"]!=0 or seq[-1]["to"]!=d["source_duration_seconds"]:
        raise ValueError("MAIZEN_SOURCE_SCENES_INCOMPLETE")
    if any(seq[i+1]["from"]-seq[i]["to"] not in (0,1) for i in range(len(seq)-1)):
        raise ValueError("MAIZEN_SOURCE_SCENE_GAPS")
    return d

def maizen_browser_source_study()->dict:
    d=load_maizen_browser_study()
    local=None
    if AUDIT.is_file() and not AUDIT.is_symlink():
        a=json.loads(AUDIT.read_text(encoding="utf8"))
        if (a.get("source_timeline_playback_covered") is True
            and a.get("indices_contiguous") is True
            and a.get("real_browser_segments_complete")==45
            and not a.get("uncovered_gaps_gt_0_7sec")
            and a.get("last_media_position_s",0)>=1683.7
            and a.get("audio_rms_samples",0)>300):
            local=a
    from .maizen_full_video_gate_v227 import maizen_full_video_review_gate
    strict=maizen_full_video_review_gate()
    return {
        "schema":"cine.minecraft.maizen_browser_source_study.v237",
        "video_id":d["video_id"],
        "original_source_url":d["source_url"],
        "source_browser_full_timeline_verified_by_local_trace":bool(local),
        "source_video_duration_seconds":d["source_duration_seconds"],
        "successful_38s_consecutive_playback_segments":45 if local else 0,
        "captured_video_sample_frames":local["screenshots_sampled"] if local else 0,
        "audio_energy_samples":local["audio_rms_samples"] if local else 0,
        "audible_energy_samples":local["audible_nonzero_rms_samples"] if local else 0,
        "full_native_audio_semantic_listening_verified":False,
        "visual_chapter_timeline":d["scene_timeline"],
        "creative_observations_from_sampled_original_frames":d["notes"],
        "exact_rival_tools_mods_known":False,
        "can_conclude_Maizen_uses_only_gameplay_or_only_Blender":False,
        "independent_media_qc_completed":False,
        "maizen_v227_first_video_final_qc_approved":next(
            (v["gate_passed"] for v in strict["videos"]
             if v["video_id"]==d["video_id"]),False
        ),
        "company_G03_competitor_technique_greenlight":strict["cohort_gate_passed"],
        "additional_two_source_videos_pending":True,
        "release_and_paid_credits_authorized":False,
    }
