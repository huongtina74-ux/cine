"""G01/G02 Minecraft source evidence from direct metadata and public preview mosaics.

NOT full video playback or full audio. A storyboard mosaic is a compressed
set of sparse thumbnail samples; zero precise shot cut/audio/rig claims.
Live views and dates must be refetched for a new snapshot and never imply
the upload reached one million views within its first fourteen days.
"""
from __future__ import annotations
from datetime import date
import json
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"config/niches/minecraft/g01_g02_public_evidence_v224.json"
IDS={
    "ZmT0ITUGUII","zhPBXzHsLuo","X09yxFuKLAs",
    "oX6Azwe5QLg","w2U4rcZlKnQ","cSrlIx-rT0Y","le0yTRqFRro",
}

def load_public_minecraft_evidence() -> dict[str,Any]:
    d=json.loads(SOURCE.read_text(encoding="utf-8"))
    if d.get("schema")!="cine.minecraft.g01_g02_public_evidence.v224":
        raise ValueError("UNSUPPORTED_MINECRAFT_PUBLIC_EVIDENCE")
    if d.get("channel_age_and_14day_breakout_verification_complete") is not False:
        raise ValueError("NO_PROOF_OF_EARLY_BREAKOUT")
    video=d["source_video_records"]
    if len(video)!=7 or {r["video_id"] for r in video}!=IDS:
        raise ValueError("MINECRAFT_METADATA_CASES_CHANGED")
    for r in video:
        if (r["official_youtube_url"]!="https://www.youtube.com/watch?v="+r["video_id"]
            or r["duration_seconds"]<480 or r["view_count_snapshot"]<0
            or r["full_frames_played"] or r["full_audio_heard"]
            or r["verified_1m_within_14d"]!="UNKNOWN_NO_DAILY_VIDEO_HISTORY"):
            raise ValueError("MINECRAFT_FAKE_VIDEO_EVIDENCE")
        ch=r["chapters"]
        if any(k["end_seconds"]<=k["start_seconds"] or k["start_seconds"]<0
               or k["end_seconds"]>r["duration_seconds"]
               for k in ch):
            raise ValueError("MINECRAFT_CHAPTER_TIMES_BAD")
    g01=d["g01"]
    if (g01["state"]!="PARTIAL_PUBLIC_METADATA_VERIFIED_CONTROLS_CHOSEN"
        or g01["primary_case_count"]!=3):
        raise ValueError("MINECRAFT_G01_NOT_PROVEN_COMPLETE")
    g02=d["g02"]
    if (g02["state"]!="PARTIAL_PUBLIC_THUMBNAIL_SAMPLE_ONLY_NOT_FULL_VIDEO_WATCH"
        or g02["full_video_frames_reviewed"] or g02["full_video_audio_listened"]
        or g02["frame_scenes_timecoded_continuously"]):
        raise ValueError("PREVIEW_NOT_FULL_VIDEO")
    samples=g02["thumbnail_preview_samples"]
    if len(samples)!=3:
        raise ValueError("MISSING_PREVIEW_SAMPLES")
    for p in samples:
        if (p["video_id"] not in IDS or len(p["tile_sha256"])!=3 or
            len(p["sampled_fragment_indices"])!=3 or
            p["sampled_video_audio"] or
            "NOT_VIDEO_PLAYBACK" not in p["observation_scope"]):
            raise ValueError("PREVIEW_STATUS_OVERSTATED")
    if not all(d["qc_policy"][x] is True for x in (
        "no_partner_paid_credits","do_not_clone_reference_skins",
        "do_not_claim_full_video_watched","do_not_claim_14day_breakout",
        "do_not_switch_backend","owner_approval_for_install",
        "local_demo_preview_only",
    )):
        raise ValueError("MINECRAFT_RESEARCH_PERMISSION_ESCALATION")
    return d

def minecraft_g01_g02_evidence(video_id:str|None=None) -> dict[str,Any]:
    d=load_public_minecraft_evidence()
    if video_id is not None and video_id not in IDS:
        raise ValueError("UNKNOWN_RESEARCH_VIDEO_ID")
    refs=[{
        "video_id":r["video_id"],"channel":r["channel"],
        "video_title":r["title"],"source":r["official_youtube_url"],
        "upload_date_as_extracted":r["upload_date_extracted"],
        "duration_seconds":r["duration_seconds"],
        "views_at_snapshot":r["view_count_snapshot"],
        "snapshot_date":r["view_count_as_of_date"],
        "source_type":r["metadata_source_type"],
        "role":r["role"],"chapter_status":r["chapter_status"],
        "chapters":r["chapters"],
        "has_8min_video":r["verified_8min_plus"],
        "has_two_1m_14day_breakouts":False,
        "full_video_watched":False,"full_audio_heard":False,
    } for r in d["source_video_records"] if video_id is None or r["video_id"]==video_id]
    previews=[{
        "video_id":x["video_id"],
        "mode":"OFFICIAL_PUBLIC_SPARSE_THUMBNAILS_ONLY",
        "sample_fragment_indices":x["sampled_fragment_indices"],
        "thumbnail_tile_hashes":x["tile_sha256"],
        "observations":x["sampled_visual_observations"],
        "interpretation":x["bounded_interpretation"],
        "preview_thumbnails_not_playback":True,
        "has_sound":False,
    } for x in d["g02"]["thumbnail_preview_samples"]
       if video_id is None or x["video_id"]==video_id]
    return {
        "schema":"cine.minecraft.g01_g02_evidence_report.v224",
        "selected_video_id":video_id,
        "verified_public_video_count":len(refs),
        "snapshot_date":d["as_of"],
        "phase_g01_status":d["g01"]["state"],
        "phase_g02_status":d["g02"]["state"],
        "channels_created_within_30days_verified":0,
        "new_channel_2x_1m_in_14days_verified":0,
        "full_competitor_video_audio_watches":0,
        "case_metadata":refs,
        "visual_preview_reports":previews,
        "g01_discrepancies":d["g01"]["discrepancies"],
        "g01_missing":d["g01"]["missing_acceptance"],
        "g02_missing":d["g02"]["missing_acceptance"],
        "selected_actual_render_engines_verified":0,
        "vendor_paid_credits_spent":0,
        "next_actions":[
            "Confirm original channel age, first 14-day velocity and weaker >=8min control videos",
            "Obtain permissioned full moving footage and sound then timecode screen actions and SFX",
            "Research Minecraft Fabric/ReplayMod/Flashback/OBS and test local game capture separately",
            "Research original 3D character rigs, movement, cameras and props vs v197 art blocker receipts",
        ],
        "promote_competitor_breakdown_to_verified":False,
        "production_permission":False,
    }
