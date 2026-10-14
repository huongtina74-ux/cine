"""Mandatory v227 entire-video-and-audio review gate for Maizen Studio A.

No metadata, thumbnails, short excerpt, transcript, or chat model inference can
substitute for watching the entire referenced moving film and listening to its
full original audio. Reviewed material must be authorized/locally available.

The module never fetches third-party media or approves a vendor pipeline from
looks alone. The verifier of actual media is an explicit CLI operation; this
READ-ONLY reporting/gating layer requires both media checksum and an external
decode receipt already generated from the same local file.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import re
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
POLICY_PATH=ROOT/"config/niches/minecraft/maizen_full_video_policy_v227.json"
ALLOWED_IDS={"ZmT0ITUGUII","zhPBXzHsLuo","oX6Azwe5QLg"}
REVIEW_DIR=ROOT/"data/verification/v227_maizen_full_video_reports"
MEDIA_DIR=ROOT/"data/research/maizen_source_media"
MIN_DETAILS=12

def load_full_video_policy() -> dict[str,Any]:
    p=json.loads(POLICY_PATH.read_text(encoding="utf8"))
    if p.get("schema")!="cine.minecraft.maizen_full_video_first.v227":
        raise ValueError("FULL_VIDEO_POLICY_SCHEMA_MISMATCH")
    if p.get("project_id")!="MAI01_WATERFALL" or p.get("policy_status")!="MANDATORY_FAIL_CLOSED":
        raise ValueError("FULL_VIDEO_GATE_DISABLED")
    r=p["rules"]
    must_true=(
        "must_watch_every_selected_reference_from_start_to_end",
        "must_hear_every_selected_original_audio_track",
        "must_verify_original_local_av_source",
        "require_contiguous_visual_and_audio_coverage",
        "require_every_segment_specific_observed_visual_audio",
        "require_video_frame_decode","require_audio_decode",
        "requires_independent_evidence_audit",
        "no_paid_credits_without_approval","no_unauthorized_download",
    )
    must_false=(
        "allow_thumbnail_transcript_metadata_to_replace_av",
        "allow_10_second_excerpt_to_replace_full_video",
        "allow_early_method_conclusion",
        "allow_precise_renderer_claim_from_visuals_alone",
        "allow_script_room_production_design_character_technical_audio_editorial_qc_promotions_before_gate",
    )
    if (any(r.get(x) is not True for x in must_true) or
        any(r.get(x) is not False for x in must_false) or
        r.get("max_segment_seconds")!=30 or
        r.get("minimum_required_reference_videos")!=3):
        raise ValueError("MISSING_FULL_FILM_AND_AUDIO_SAFETY_REQUIREMENTS")
    videos=p["required_references"]
    ids={v["video_id"] for v in videos}
    if (len(videos)<3 or len(ids)!=len(videos)
        or not ALLOWED_IDS.issubset(ids)
        or any(not re.fullmatch(r"[A-Za-z0-9_-]{11}",x) for x in ids)):
        raise ValueError("MAIZEN_FULL_FILM_COHORT_TAMPERED")
    from .minecraft_source_evidence_v224 import load_public_minecraft_evidence
    originals={v["video_id"]:v for v in load_public_minecraft_evidence()["source_video_records"]}
    if any((x["video_id"] in originals and
            x["duration_seconds"]!=originals[x["video_id"]]["duration_seconds"])
           or x["duration_seconds"]<480
           or (x["video_id"] not in originals and
               not x.get("source_metadata_independently_verified",False))
           for x in videos):
        raise ValueError("FULL_FILM_DURATIONS_NOT_SOURCE_GROUNDED")
    if p["no_production_execution_or_publishing_authorized"] is not True:
        raise ValueError("REVIEW_CANNOT_AUTHORIZE_PRODUCTION")
    return p

def selected_maizen_video_ids()->set[str]:
    """Expands when research adds new references; every added title is mandatory."""
    return {v["video_id"] for v in load_full_video_policy()["required_references"]}

def _blank_intervals(duration:int, step:int=30) -> list[dict]:
    items=[]
    for start in range(0,duration,step):
        items.append({
            "start_seconds":start,"end_seconds":min(start+step,duration),
            "visual_observation":"","audio_observation":"",
            "dialogue_or_speech_summary":"","acting_and_movement":"",
            "camera_and_edit":"","scene_or_world":"",
            "source_workflow_hypotheses":"",
            "uncertainties":"",
            "viewed_moving_video":False,"heard_original_audio":False,
            "evidence_frame_timecodes":[],
        })
    return items

def draft_full_review_template(video_id:str)->dict:
    policy=load_full_video_policy()
    if video_id not in selected_maizen_video_ids():
        raise ValueError("UNKNOWN_MAIZEN_REFERENCE_ID")
    v=next(x for x in policy["required_references"] if x["video_id"]==video_id)
    return {
        "schema":"cine.minecraft.maizen_full_watch_report.v227",
        "video_id":video_id,
        "source_url":"https://www.youtube.com/watch?v="+video_id,
        "expected_duration_seconds":v["duration_seconds"],
        "media_relative_path":"data/research/maizen_source_media/"+video_id+".mp4",
        "media_sha256":None,
        "verified_media_decode_receipt_relative_path":"data/verification/v227_maizen_full_video_reports/"+video_id+".media_receipt.json",
        "observed_duration_seconds":None,
        "watch_provenance":"NOT_WATCHED",
        "viewer_attestation":{"reviewer":"","visual_entire_film":False,
                              "audio_entire_film":False,"reviewed_at":""},
        "independent_reviewer_attestation":{"reviewer":"","audited_all_intervals":False,
                                           "signed_at":""},
        "visual_full_watch":False,"audio_full_watch":False,
        "decode_full_video":False,"decode_full_audio":False,
        "intervals":_blank_intervals(v["duration_seconds"]),
        "global_story_arc_observed":"","whole_film_audio_design_observed":"",
        "whole_film_camera_and_edit_patterns_observed":"",
        "production_method_hypotheses_not_attributed_as_fact":"",
        "unresolved_tool_and_asset_provenance":"",
    }

def _confined(root:Path, rel:str) -> Path:
    if not isinstance(rel,str) or not rel or Path(rel).is_absolute():
        raise ValueError("UNTRUSTED_MAIZEN_MEDIA_PATH")
    p=(root/rel).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError("OUT_OF_RESEARCH_REPOSITORY")
    return p

def _meaningful(s:Any) -> bool:
    return isinstance(s,str) and len(" ".join(s.split()))>=MIN_DETAILS and         s.strip().lower() not in {"none","n/a","unknown","not watched","placeholder"}

def _review_file_status(video:dict) -> dict:
    vid=video["video_id"]
    report_file=REVIEW_DIR/(vid+".json")
    blockers=[]
    if report_file.is_symlink():
        return {"video_id":vid,"required_duration_s":video["duration_seconds"],
                "segments_required":len(_blank_intervals(video["duration_seconds"])),
                "observed_segments_passed":0,"source_file_checked":False,
                "complete_audio_video_watched":False,"gate_passed":False,
                "blockers":["UNTRUSTED_FULL_REVIEW_REPORT_SYMLINK"],
                "review_state":"INVALID_NOT_APPROVED"}
    if not report_file.is_file():
        return {"video_id":vid,"required_duration_s":video["duration_seconds"],
                "segments_required":len(_blank_intervals(video["duration_seconds"])),
                "observed_segments_passed":0,"source_file_checked":False,
                "complete_audio_video_watched":False,"gate_passed":False,
                "blockers":["FULL_WATCH_REPORT_NOT_PRESENT"],
                "review_state":"NOT_WATCHED"}
    try:
        x=json.loads(report_file.read_text(encoding="utf8"))
        if x.get("schema")!="cine.minecraft.maizen_full_watch_report.v227" or x.get("video_id")!=vid:
            raise ValueError("INVALID_REPORT_SCHEMA_OR_VIDEO_ID")
        if x.get("source_url")!="https://www.youtube.com/watch?v="+vid or            x.get("expected_duration_seconds")!=video["duration_seconds"]:
            raise ValueError("SOURCE_VIDEO_DURATION_MISMATCH")
        receipt_path=_confined(ROOT,x["verified_media_decode_receipt_relative_path"])
        if receipt_path.parent!=REVIEW_DIR.resolve():
            raise ValueError("MEDIA_RECEIPT_WRONG_DIRECTORY")
        asset=_confined(ROOT,x["media_relative_path"])
        if (asset.parent!=MEDIA_DIR.resolve() or asset.stem!=vid
            or asset.suffix.lower() not in (".mp4",".mkv",".webm")):
            raise ValueError("VIDEO_MEDIA_NOT_IN_PROTECTED_SOURCE_DIRECTORY")
        if not asset.is_file():
            blockers.append("ORIGINAL_FULL_AUDIO_VIDEO_MEDIA_MISSING")
            media_ok=False
        else:
            # Check source bytes still match both the full watch and decode receipt.
            digest=sha256()
            with asset.open("rb") as media_stream:
                for chunk in iter(lambda:media_stream.read(1024*1024),b""):
                    digest.update(chunk)
            actual=digest.hexdigest()
            media_ok=bool(x.get("media_sha256")==actual)
            if not media_ok: blockers.append("SOURCE_VIDEO_SHA256_MISMATCH")
        receipt_ok=False
        if receipt_path.is_file() and media_ok:
            rec=json.loads(receipt_path.read_text(encoding="utf8"))
            receipt_ok=(
                rec.get("schema")=="cine.minecraft.media_full_decode.v227"
                and rec.get("video_id")==vid
                and rec.get("media_sha256")==x.get("media_sha256")
                and rec.get("video_decode_full_success") is True
                and rec.get("audio_decode_full_success") is True
                and rec.get("has_video_stream") is True
                and rec.get("has_audio_stream") is True
                and abs(rec.get("duration_seconds",-999)-video["duration_seconds"])<=2
                and rec.get("decoded_source_full_duration") is True
            )
        if not receipt_ok: blockers.append("FULL_VIDEO_AUDIO_DECODING_RECEIPT_MISSING_OR_INVALID")
        required_watch=all(x.get(k) is True for k in (
            "visual_full_watch","audio_full_watch","decode_full_video","decode_full_audio"
        ))
        witness=x.get("viewer_attestation",{})
        independent=x.get("independent_reviewer_attestation",{})
        signed=(
            bool(witness.get("reviewer")) and witness.get("visual_entire_film") is True
            and witness.get("audio_entire_film") is True and bool(witness.get("reviewed_at"))
            and bool(independent.get("reviewer"))
            and independent.get("audited_all_intervals") is True
            and bool(independent.get("signed_at"))
            and witness.get("reviewer")!=independent.get("reviewer")
            and x.get("watch_provenance")=="AUTHORIZED_COMPLETE_MOVING_MEDIA_AND_ORIGINAL_AUDIO"
        )
        if not required_watch or not signed:
            blockers.append("COMPLETE_FILM_WATCH_AND_INDEPENDENT_ATTESTATION_MISSING")
        items=x.get("intervals",[])
        start=0
        passed=0
        for it in items:
            end=it.get("end_seconds")
            if (it.get("start_seconds")!=start or not isinstance(end,int)
                or end<=start or end-start>30
                or end>video["duration_seconds"]):
                break
            fields=("visual_observation","audio_observation","dialogue_or_speech_summary",
                    "acting_and_movement","camera_and_edit","scene_or_world",
                    "source_workflow_hypotheses","uncertainties")
            if (not all(_meaningful(it.get(k)) for k in fields)
                or it.get("viewed_moving_video") is not True
                or it.get("heard_original_audio") is not True
                or not isinstance(it.get("evidence_frame_timecodes"),list)
                or not it["evidence_frame_timecodes"]
                or any(not isinstance(t,(int,float)) or not start<=t<end
                       for t in it["evidence_frame_timecodes"])):
                break
            start=end
            passed+=1
        if passed!=len(items) or start!=video["duration_seconds"]:
            blockers.append("INCOMPLETE_OR_UNDOCUMENTED_TIMECODE_COVERAGE")
        if passed and len({it["visual_observation"].strip() for it in items})<max(1,(passed+1)//2):
            blockers.append("REPEATED_GENERIC_NOTES_NOT_INDEPENDENT_SCENE_OBSERVATIONS")
        for field in ("global_story_arc_observed","whole_film_audio_design_observed",
                      "whole_film_camera_and_edit_patterns_observed",
                      "production_method_hypotheses_not_attributed_as_fact",
                      "unresolved_tool_and_asset_provenance"):
            if not _meaningful(x.get(field)):
                blockers.append("FULL_FILM_SYNTHESIS_INCOMPLETE")
                break
        if not isinstance(x.get("observed_duration_seconds"),(int,float)) or            abs(x["observed_duration_seconds"]-video["duration_seconds"])>2:
            blockers.append("ACTUAL_OBSERVED_FILM_DURATION_NOT_VERIFIED")
        return {"video_id":vid,"required_duration_s":video["duration_seconds"],
                "segments_required":len(_blank_intervals(video["duration_seconds"])),
                "observed_segments_passed":passed,
                "source_file_checked":media_ok,
                "complete_audio_video_watched":bool(required_watch and signed and media_ok and receipt_ok),
                "gate_passed":not blockers,"blockers":blockers,
                "review_state":"FULL_WATCH_VERIFIED" if not blockers else "PARTIAL_NOT_APPROVED"}
    except (ValueError,KeyError,TypeError,IndexError,UnicodeError,OSError) as exc:
        return {"video_id":vid,"required_duration_s":video["duration_seconds"],
                "segments_required":len(_blank_intervals(video["duration_seconds"])),
                "observed_segments_passed":0,"source_file_checked":False,
                "complete_audio_video_watched":False,"gate_passed":False,
                "blockers":["INVALID_OR_UNTRUSTED_FULL_REVIEW_REPORT:"+str(exc)],
                "review_state":"INVALID_NOT_APPROVED"}

def maizen_full_video_review_gate() -> dict:
    policy=load_full_video_policy()
    status=[_review_file_status(v) for v in policy["required_references"]]
    ok=len(status)>=3 and all(s["gate_passed"] for s in status)
    return {
        "schema":"cine.minecraft.maizen_full_video_review_gate.v227",
        "project_id":policy["project_id"],
        "rule":"COMPLETE_VIDEO_AND_ORIGINAL_AUDIO_FIRST_THEN_ANALYSIS_AND_DOWNSTREAM",
        "required_video_count":len(status),
        "full_verified_videos":sum(s["gate_passed"] for s in status),
        "required_total_seconds":sum(x["required_duration_s"] for x in status),
        "required_total_segments":sum(x["segments_required"] for x in status),
        "videos":status,
        "cohort_gate_passed":ok,
        "g03_competitor_method_analysis_authorized":ok,
        "g04_g28_department_production_workflow_promotions_authorized":ok,
        "exact_private_software_tool_attribution_authorized":False,
        "may_run_independent_internal_quality_experiments":ok,
        "may_claim_video_reference_review_completed":ok,
        "maizen_method_selection_from_competitor_study_authorized":ok,
        "no_10_second_sample_override":True,
        "no_thumbnail_or_transcript_override":True,
        "no_paid_credits_or_external_download_triggered":True,
    }


def prepare_full_watch_templates() -> dict:
    """Write blank workbooks for full-length A/V review, never claim completion."""
    load_full_video_policy()
    REVIEW_DIR.mkdir(parents=True,exist_ok=True)
    files=[]
    for vid in sorted(selected_maizen_video_ids()):
        dest=REVIEW_DIR/(vid+".json")
        if dest.is_symlink():
            raise ValueError("UNTRUSTED_FULL_REVIEW_TEMPLATE_SYMLINK")
        if dest.exists():
            status="PRESERVED_EXISTING_HUMAN_REVIEW"
        else:
            body=draft_full_review_template(vid)
            dest.write_text(json.dumps(body,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
            status="BLANK_NOT_WATCHED_TEMPLATE_CREATED"
        files.append({"video_id":vid,"path":str(dest),
                      "state":status})
    return {"schema":"cine.minecraft.maizen_full_video_templates.v227",
            "template_count":len(files),"templates":files,
            "any_full_video_watched_by_this_command":False,
            "production_gate_passed":maizen_full_video_review_gate()["cohort_gate_passed"]}


def maizen_research_stage_gate(stage_id: str) -> dict:
    """Gate G03..G28 AND production decisions until all selected films are seen."""
    from .minecraft_company_roadmap_v223 import load_minecraft_master_company_plan
    valid={r["step_id"] for r in load_minecraft_master_company_plan()["master_steps"]}
    if stage_id not in valid:
        raise ValueError("UNKNOWN_MAIZEN_COMPANY_STAGE")
    result=maizen_full_video_review_gate()
    metadata_only=stage_id=="G01"
    full_watch_collection=stage_id=="G02"
    can_begin=metadata_only or full_watch_collection or result["cohort_gate_passed"]
    return {
        "schema":"cine.minecraft.maizen_stage_research_lock.v227",
        "requested_stage":stage_id,
        "may_begin_stage":can_begin,
        "may_issue_a_competitor_method_conclusion":bool(result["cohort_gate_passed"] and stage_id!="G01"),
        "blocking_video_ids":[v["video_id"] for v in result["videos"] if not v["gate_passed"]],
        "source_gate":result["schema"],
        "reason":("COLLECT_COMPLETE_AUTHORIZED_FULL_VIDEO_AND_AUDIO" if full_watch_collection
                  else "METADATA_ONLY_NO_METHOD_CONCLUSIONS" if metadata_only
                  else "BLOCKED_COMPLETE_MOVING_VIDEO_AND_AUDIO_REQUIRED" if not can_begin
                  else "SOURCE_VIDEO_REVIEW_PASSED_OTHER_PRODUCTION_GATES_REMAIN"),
        "no_10s_excerpt_override":True,
    }

def require_maizen_full_video_review_for_stage(stage_id:str)->None:
    state=maizen_research_stage_gate(stage_id)
    if not state["may_begin_stage"]:
        raise PermissionError(
            "BLOCKED_MAIZEN_FULL_VIDEO_AUDIO_REVIEW_REQUIRED_FOR_"+stage_id
        )
