"""v230: preserved external vidIQ whole-length walkthrough of Maizen case one.

A provider-generated full-duration time-coded summary is NOT a complete review
of raw moving frames and native audio. Preserve original source markdown,
distinct audio gaps, and untouched v227 source-A/V evidence gate.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"config/niches/minecraft/maizen_first_vidiq_review_v230.json"
PROVIDER_REPORT=ROOT/"data/research/maizen_vidiq_watch_v230/ZmT0ITUGUII_vidiq_walkthrough.md"

def load_vidiq_watch_case()->dict:
    data=json.loads(SOURCE.read_text(encoding="utf-8"))
    if (data.get("schema")!="cine.minecraft.maizen_vidiq_source_analysis.v230"
        or data.get("video_id")!="ZmT0ITUGUII"
        or data.get("video_duration_seconds")!=1684
        or data.get("source_provider")!="vidIQ"
        or data.get("tool_name")!="vidiq_video_watch"
        or data.get("job_status")!="completed"
        or data.get("job_id")!="job_df6b1ec3-a667-4957-adb5-5ca85bd9de76"):
        raise ValueError("VIDIQ_PROVIDER_PROVENANCE_NOT_VALID")
    if (len(data.get("rounds",[]))!=7
        or len(data.get("chronological_scenes",[]))!=23
        or any(data.get(k) is not False for k in (
            "full_original_video_bytes_available",
            "full_original_audio_stream_available",
            "interval_30s_source_frame_coverage_verified",
            "third_party_auditor_approved",
            "original_audio_full_listening_independently_verified",
            "v227_gate_approved","no_automatic_software_install",
        ) if k != "no_automatic_software_install")):
        raise ValueError("EXTERNAL_REPORT_MUST_NOT_CLAIM_TRUE_MEDIA_REVIEW")
    if not data.get("no_automatic_software_install") or not data.get("no_production_promotion"):
        raise ValueError("NO_UNAPPROVED_PRODUCTION")
    scenes=data["chronological_scenes"]
    if scenes[0]["begin_seconds"]!=0 or scenes[-1]["end_seconds"]!=1684:
        raise ValueError("PROVIDER_SUMMARY_OMITS_START_OR_END")
    for i,s in enumerate(scenes):
        if (s["end_seconds"]<=s["begin_seconds"]
            or s["source"]!="VIDIQ_AI_SYNTHESIZED_NOT_INDEPENDENT_FRAMES"
            or s["independently_verified_picture"]
            or s["independently_verified_audio"]
            or s["actual_decode_frame_timestamps"]):
            raise ValueError("VIDIQ_GENERATED_REPORT_FALSE_FRAME_PROOF")
        if i and s["begin_seconds"]-scenes[i-1]["end_seconds"]>1:
            raise ValueError("VIDIQ_GENERATED_REPORT_UNCOVERED_DURATION")
    if not PROVIDER_REPORT.is_file():
        raise ValueError("ORIGINAL_WATCH_ANALYSIS_TEXT_NOT_PRESERVED")
    original=PROVIDER_REPORT.read_text(encoding="utf8")
    for check in ("00:00 – 03:35","27:51 – 28:04","Evidence Gaps / Unverified Aspects"):
        if check not in original:
            raise ValueError("ORIGINAL_PROVIDER_TEXT_INCOMPLETE")
    return data

def maizen_vidiq_provider_evidence()->dict:
    data=load_vidiq_watch_case()
    from .maizen_full_video_gate_v227 import maizen_full_video_review_gate
    gate=maizen_full_video_review_gate()
    scenes=data["chronological_scenes"]
    audios=[
        s for s in scenes
        if "not itemized" not in s["provider_audio_claim"].lower()
        and "no exact" not in s["provider_audio_claim"].lower()
    ]
    digest=sha256(PROVIDER_REPORT.read_bytes()).hexdigest()
    return {
        "schema":"cine.minecraft.maizen_vidiq_whole_video_provisional_analysis.v230",
        "video_id":data["video_id"],
        "video_duration_seconds":data["video_duration_seconds"],
        "source_url":data["source_url"],
        "provider_job_id":data["job_id"],
        "provider_watch_job_completed":True,
        "provider_report_sha256":digest,
        "provider_report_path":str(PROVIDER_REPORT),
        "provider_summary_scene_sections":len(scenes),
        "provider_explicit_audio_detail_segments":len(audios),
        "provider_summary_longest_scene_seconds":max(s["end_seconds"]-s["begin_seconds"] for s in scenes),
        "requires_30s_or_shorter_evidence_windows":True,
        "main_rounds":data["rounds"],
        "scene_summaries":scenes,
        "source_film_audio_stream_independently_verified":False,
        "independent_av_auditor_approved":False,
        "official_mods_software_tools_identified":False,
        "unverified_technology_labels":data["unverified_specific_software_claims"],
        "provider_advertised_credits":data["meta"]["provider_advertised_credit_cost"],
        "observed_balance_before":data["meta"]["credits_balance_before"],
        "observed_balance_after":data["meta"]["credits_balance_after"],
        "actual_charge_cannot_be_inferred_from_advertised_pricing":True,
        "v227_all_three_full_video_gate_passed":gate["cohort_gate_passed"],
        "v227_first_video_gate_passed":next(
            (v["gate_passed"] for v in gate["videos"]
             if v["video_id"]==data["video_id"]),False
        ),
        "may_promote_competitor_workflow_to_production":False,
        "note":"External AI reports entire-video walkthrough with 23 coarse segments; the user-mandated independent frame+original-audio windows and source media are NOT verified.",
    }
