"""v228: universal full moving VIDEO + original AUDIO before competitor conclusions.

Applies to any niche or channel/video, not just Maizen. Discovery of channel
ages, metadata, view velocity and public title remains allowed as CANDIDATE.
Deep content/shot/camera/audio/acting/workflow conclusions and department
promotions need an *independently audited* 100% A/V timecoded review of EACH
source in the selected cohort. No network calls, data downloads or paid APIs.

Unverified reports never pass. A typed attestation alone cannot prove that a
human genuinely watched the file; SHA/real full decode/continuous evidence and
independent QC add safeguards but cannot provide omniscience.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re

from .maizen_full_video_gate_v227 import (
    _meaningful, _blank_intervals, _confined, maizen_full_video_review_gate,
)

ROOT=Path(__file__).resolve().parents[2]
POLICY_PATH=ROOT/"config/technology/competitor_full_video_first_v228.json"
MEDIA_DIR=ROOT/"data/research/competitor_source_media"
META_DIR=ROOT/"data/research/competitor_source_metadata"
REPORT_DIR=ROOT/"data/verification/v228_competitor_full_video_reports"
VID=re.compile(r"^[A-Za-z0-9_-]{11}$")
NICHE=re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,79}$")
MAX_SELECTED=25


def load_studio_full_video_policy() -> dict:
    p=json.loads(POLICY_PATH.read_text(encoding="utf8"))
    if p.get("schema")!="cine.company.competitor_full_video_first.v228":
        raise ValueError("COMPANY_VIDEO_FIRST_POLICY_MISSING")
    if (p.get("discovery_requires_full_media") is not False
        or p.get("deep_content_analysis_requires_complete_video_and_audio") is not True
        or p.get("one_short_excerpt_is_never_full_video") is not True
        or p.get("metadata_cannot_prove_production_method") is not True
        or p.get("every_selected_reference_must_pass") is not True
        or p.get("no_auto_approve_or_paid_api") is not True
        or p.get("max_visual_audio_segment_seconds")!=30
        or p.get("authoritative_technology_attribution_from_pixels_alone") is not False
        or p.get("allow_auto_publish_after_research") is not False):
        raise ValueError("COMPANY_FULL_FILM_POLICY_FAIL_CLOSED")
    return p


def _status_for_generic(video_id: str)->dict:
    """Validate exact trusted local video and independently documented full watch."""
    missing=lambda reason,duration=0,nseg=0: {
        "video_id":video_id,"gate_passed":False,"duration_seconds":duration,
        "segments_required":nseg,"segments_validated":0,
        "blockers":[reason],
        "review_provenance":"NOT_FULLY_WATCHED_OR_AUTHENTICATED",
    }
    meta=META_DIR/(video_id+".json")
    report=REPORT_DIR/(video_id+".json")
    receipt=REPORT_DIR/(video_id+".media_receipt.json")
    if any(f.is_symlink() for f in (meta,report,receipt)):
        return missing("SOURCE_OR_REPORT_SYMLINK_UNTRUSTED")
    if not meta.is_file():
        return missing("DIRECT_OFFICIAL_SOURCE_METADATA_MISSING")
    try:
        md=json.loads(meta.read_text(encoding="utf8"))
        if (md.get("schema")!="cine.company.competitor_source_metadata.v228"
            or md.get("video_id")!=video_id
            or md.get("source_url")!="https://www.youtube.com/watch?v="+video_id
            or md.get("source") not in ("DIRECT_YOUTUBE_VIDEO_PAGE","OFFICIAL_YOUTUBE_DATA_API")
            or md.get("source_verified") is not True
            or not md.get("checked_at")
            or type(md.get("duration_seconds")) is not int
            or not (1<=md["duration_seconds"]<=12*3600)):
            return missing("UNTRUSTED_VIDEO_SOURCE_METADATA")
        duration=md["duration_seconds"]
        nseg=len(_blank_intervals(duration))
        if not report.is_file():
            return missing("ENTIRE_VIDEO_AND_AUDIO_REVIEW_NOT_PRESENT",duration,nseg)
        x=json.loads(report.read_text(encoding="utf8"))
        if (x.get("schema")!="cine.company.competitor_full_watch_report.v228"
            or x.get("video_id")!=video_id
            or x.get("source_url")!=md["source_url"]
            or x.get("expected_duration_seconds")!=duration):
            return missing("REVIEW_NOT_BOUND_TO_EXACT_SOURCE",duration,nseg)
        path=_confined(ROOT,x.get("media_relative_path",""))
        if (path.parent!=MEDIA_DIR.resolve() or path.stem!=video_id
            or path.suffix.lower() not in (".mp4",".mkv",".webm")
            or not path.is_file() or path.is_symlink()):
            return missing("ORIGINAL_FULL_MOVING_AV_SOURCE_MISSING",duration,nseg)
        digest=sha256()
        with path.open("rb") as inp:
            for part in iter(lambda:inp.read(1024*1024),b""):
                digest.update(part)
        actual=digest.hexdigest()
        if x.get("media_sha256")!=actual:
            return missing("REVIEW_SOURCE_BYTES_SHA256_MISMATCH",duration,nseg)
        if not receipt.is_file():
            return missing("FULL_VIDEO_AUDIO_DECODE_RECEIPT_MISSING",duration,nseg)
        proof=json.loads(receipt.read_text(encoding="utf8"))
        if not all((
            proof.get("schema")=="cine.company.competitor_full_decode.v228",
            proof.get("video_id")==video_id,
            proof.get("media_sha256")==actual,
            proof.get("video_decode_full_success") is True,
            proof.get("audio_decode_full_success") is True,
            proof.get("has_video_stream") is True,
            proof.get("has_audio_stream") is True,
            proof.get("decoded_source_full_duration") is True,
            isinstance(proof.get("duration_seconds"),(float,int)),
        )):
            return missing("FULL_VISUAL_AND_SOUND_DECODING_NOT_VERIFIED",duration,nseg)
        if abs(proof["duration_seconds"]-duration)>2:
            return missing("DECODED_DURATION_NOT_FULL_SOURCE",duration,nseg)
        viewer=x.get("viewer_attestation") or {}
        auditor=x.get("independent_reviewer_attestation") or {}
        if not all((
            x.get("watch_provenance")=="AUTHORIZED_COMPLETE_MOVING_MEDIA_AND_ORIGINAL_AUDIO",
            x.get("visual_full_watch") is True,
            x.get("audio_full_watch") is True,
            viewer.get("visual_entire_film") is True,
            viewer.get("audio_entire_film") is True,
            bool(viewer.get("reviewer")), bool(viewer.get("reviewed_at")),
            bool(auditor.get("reviewer")), bool(auditor.get("signed_at")),
            auditor.get("audited_all_intervals") is True,
            viewer.get("reviewer")!=auditor.get("reviewer"),
        )):
            return missing("REAL_WATCH_AND_INDEPENDENT_REVIEW_MISSING",duration,nseg)
        intervals=x.get("intervals")
        if not isinstance(intervals,list) or len(intervals)!=nseg:
            return missing("INCOMPLETE_FULL_FILM_TIMECODE_WINDOWS",duration,nseg)
        pos=0
        observations=[]
        fields=("visual_observation","audio_observation","dialogue_or_speech_summary",
                "acting_and_movement","camera_and_edit","scene_or_world",
                "source_workflow_hypotheses","uncertainties")
        for it in intervals:
            end=it.get("end_seconds")
            if (it.get("start_seconds")!=pos or type(end) is not int
                or end<=pos or end-pos>30 or end>duration
                or not all(_meaningful(it.get(f)) for f in fields)
                or it.get("viewed_moving_video") is not True
                or it.get("heard_original_audio") is not True
                or not isinstance(it.get("evidence_frame_timecodes"),list)
                or not it["evidence_frame_timecodes"]
                or any(type(t) not in (int,float) or not pos<=t<end
                       for t in it["evidence_frame_timecodes"])):
                return missing("AN_INCOMPLETE_OR_GENERIC_VISUAL_AUDIO_TIMECODE_WINDOW",duration,nseg)
            observations.append(it["visual_observation"].strip())
            pos=end
        if pos!=duration or len(set(observations))<max(1,(nseg+1)//2):
            return missing("NOT_FULL_SOURCE_OR_REPEATED_GENERIC_WINDOW_NOTES",duration,nseg)
        for f in ("global_story_arc_observed","whole_film_audio_design_observed",
                  "whole_film_camera_and_edit_patterns_observed",
                  "production_method_hypotheses_not_attributed_as_fact",
                  "unresolved_tool_and_asset_provenance"):
            if not _meaningful(x.get(f)):
                return missing("WHOLE_EPISODE_SYNTHESIS_MISSING",duration,nseg)
        return {"video_id":video_id,"gate_passed":True,
                "duration_seconds":duration,"segments_required":nseg,
                "segments_validated":nseg,"blockers":[],
                "review_provenance":"SOURCE_SHA_FULL_AV_DECODE_CONTIGUOUS_NOTES_INDEPENDENT_QC"}
    except (OSError,ValueError,TypeError,KeyError,UnicodeError,IndexError) as exc:
        return missing("INVALID_VIDEO_REVIEW_EVIDENCE:"+type(exc).__name__)


def competitor_full_review_gate(niche_id:str,video_ids:list[str]|None=None)->dict:
    """Review all selected references, not just a few favorable or viral samples."""
    policy=load_studio_full_video_policy()
    if not isinstance(niche_id,str) or not NICHE.fullmatch(niche_id):
        raise ValueError("NICHE_SLUG_REQUIRED")
    if video_ids is None:
        video_ids=[]
    if not isinstance(video_ids,list) or len(video_ids)>MAX_SELECTED:
        raise ValueError("COMPETITOR_SELECTED_VIDEO_LIMIT")
    if any(not isinstance(v,str) or not VID.fullmatch(v) for v in video_ids):
        raise ValueError("INVALID_COMPETITOR_SOURCE_VIDEO_ID")
    if len(video_ids)!=len(set(video_ids)):
        raise ValueError("DUPLICATE_COMPETITOR_REFERENCE")
    is_maizen=niche_id in ("maizen_style","minecraft_maizen","MAI01_WATERFALL".lower())
    if is_maizen:
        specific=maizen_full_video_review_gate()
        known={v["video_id"]:v for v in specific["videos"]}
        selected=set(known)|set(video_ids)
        statuses=[{
            "video_id":x,
            "gate_passed":bool(known[x]["gate_passed"]),
            "blockers":known[x]["blockers"],
        } if x in known else _status_for_generic(x) for x in sorted(selected)]
    else:
        statuses=[_status_for_generic(x) for x in video_ids]
    passed=bool(statuses) and all(x["gate_passed"] for x in statuses)
    return {
        "schema":"cine.company.universal_competitor_full_av_review.v228",
        "niche_id":niche_id,
        "discovery_metadata_and_growth_scanning_allowed":True,
        "deep_full_episode_analysis_allowed":passed,
        "competitor_content_method_conclusions_allowed":passed,
        "competitor_production_backend_attribution_proven":False,
        "all_selected_reference_videos_checked":passed,
        "references_required":len(statuses),
        "references_passed":sum(x["gate_passed"] for x in statuses),
        "video_statuses":statuses,
        "default_when_no_videos_selected":"NO_DEEP_RESEARCH_APPROVAL",
        "metadata_thumbnails_short_clips_transcript_can_replace_full_av":False,
        "original_licensed_media_and_independent_full_visual_audio_qc_required":True,
        "seven_company_department_content_and_method_promotions_allowed":passed,
        "exact_hidden_software_needs_separate_first_party_confirmation":True,
        "no_auto_install_no_paid_api_no_publish":True,
    }


def competitor_study_department_gate(niche_id:str,department_id:str,video_ids:list[str]|None=None)->dict:
    from .contracts import DepartmentId
    names={r.value for r in DepartmentId}
    if department_id not in names:
        raise ValueError("UNKNOWN_COMPETITOR_STUDY_DEPARTMENT")
    g=competitor_full_review_gate(niche_id,video_ids)
    is_discovery=department_id in ("INTELLIGENCE","EVIDENCE")
    return {
        "department":department_id,"niche_id":niche_id,
        "may_screen_channel_age_views_metadata":is_discovery,
        "may_conclude_competitor_story_acting_camera_audio_production_methods":g["deep_full_episode_analysis_allowed"],
        "may_promote_competitor_based_production_recipe":False,
        "full_source_review_gate":g,
    }
