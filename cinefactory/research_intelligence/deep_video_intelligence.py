"""Deep-video evidence intake without inventing unseen footage or competitor analytics.

Public YouTube: only exact video-ID thumbnail (not body frames) and frozen metadata.
Authorized local footage: real bounded frame/audio observation via CineFactory smart.py.
Every semantic conclusion is PENDING REVIEW, not guessed from thumbnail colors.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from urllib.parse import urlsplit

from .core import _write_json, create_department_tasks
from .smart import observe_smart

VIDEO_ID=re.compile(r"^[A-Za-z0-9_-]{11}$")
ROLE_SET=("research","story","visual","animation","audio","editorial","packaging","quality","growth")
MAX_IMAGE_BYTES=3_000_000
MAX_IMAGE_PIXELS=4_000_000


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _public_thumbnail(video_id: str) -> bytes:
    """One allowlisted HTTPs host and one canonical resource, no external URL input."""
    if not isinstance(video_id,str) or not VIDEO_ID.fullmatch(video_id):
        raise ValueError("Invalid YouTube video ID")
    url=f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    with urlopen(url,timeout=12) as response:
        if response.status !=200:
            raise ValueError("Image endpoint did not return HTTP 200")
        final=urlsplit(response.geturl())
        if final.scheme!="https" or final.hostname!="i.ytimg.com" or final.username or final.password:
            raise ValueError("Public thumbnail redirected away from approved YouTube image host")
        mime=response.headers.get("Content-Type","").split(";")[0].strip().lower()
        if mime!="image/jpeg":
            raise ValueError("Unexpected public thumbnail MIME")
        payload=response.read(MAX_IMAGE_BYTES+1)
    if len(payload)>MAX_IMAGE_BYTES or not payload.startswith(b"\xff\xd8"):
        raise ValueError("Invalid or oversized JPEG thumbnail")
    return payload


def _image_facts(data: bytes) -> dict:
    """Basic image measurements, not visual semantics."""
    from PIL import Image, ImageStat, UnidentifiedImageError
    try:
        with Image.open(io.BytesIO(data)) as loaded:
            if loaded.format!="JPEG":
                raise ValueError("Public thumbnail is not JPEG")
            if loaded.width*loaded.height>MAX_IMAGE_PIXELS or loaded.width<100 or loaded.height<70:
                raise ValueError("Thumbnail dimensions out of range")
            img=loaded.convert("RGB")
            colors=ImageStat.Stat(img.resize((64,64))).mean
            grayscale=img.convert("L")
            small=grayscale.resize((64,64))
            extrema=small.getextrema()
            return {"width":img.width,"height":img.height,
                    "mean_rgb_0_255":[round(v,2) for v in colors],
                    "luminance_range_0_255":list(extrema),
                    "semantic_content":"NOT_ANALYZED",
                    "thumbnail_is_full_video_evidence":False}
    except (UnidentifiedImageError,OSError) as exc:
        raise ValueError("Thumbnail image could not be decoded") from exc


def prepare_public_video_review(evidence_json: str | Path, output_dir: str | Path,
                                *, max_videos: int=4, fetch_image=None) -> dict:
    """Shortlist videos for real multimodal HUMAN review; may download exact public thumbs."""
    if not 1<=max_videos<=12:
        raise ValueError("Thumbnail research budget must be 1..12")
    source=Path(evidence_json).resolve(strict=True)
    report=json.loads(source.read_text(encoding="utf-8"))
    if report.get("schema")!="cine.research.automated_evidence.v1":
        raise ValueError("One frozen automated evidence report required")
    if report.get("state")!="PUBLIC_EVIDENCE_READY_FOR_REVIEW":
        raise ValueError("Partial/historical source cannot be promoted into current video reviews")
    for key in ("search","plan","catalog"):
        item=report["source_files"][key]
        raw=Path(item["path"]).resolve(strict=True)
        if _sha(raw)!=item["sha256"]:
            raise ValueError(f"Frozen {key} source mutated")
    valid={}
    for channel in report["channels"]:
        for video in channel["sample_longform_videos"]:
            if video.get("video_id") in valid:
                raise ValueError("Duplicate video across catalog")
            valid[video["video_id"]]=(channel,video)
    work=report.get("per_video_work_packets",{})
    selected=[]
    for bucket,role in (("fresh_million_review","fresh_trend"),
                        ("leader_review","leader"),
                        ("newcomer_review","newcomer")):
        for task in work.get(bucket,[]):
            ids=[task["video_id"]] if "video_id" in task else task.get("candidate_video_ids",[])
            for vid in ids:
                if vid not in valid or vid in selected or not VIDEO_ID.fullmatch(vid):
                    continue
                channel, video=valid[vid]
                if video.get("topic_title_alignment")!="ALL_NICHE_TITLE_TOKENS_PRESENT":
                    continue
                selected.append(vid)
                if len(selected)>=max_videos:break
            if len(selected)>=max_videos:break
        if len(selected)>=max_videos:break
    target=Path(output_dir).resolve()
    if target.exists():
        raise FileExistsError("Deep-video review output must be a new directory")
    target.mkdir(parents=True)
    pull=fetch_image or _public_thumbnail
    videos=[]
    for vid in selected:
        channel,video=valid[vid]
        image_status="THUMBNAIL_UNAVAILABLE"
        thumb_data=None
        facts=None
        try:
            thumb_data=pull(vid)
            if not isinstance(thumb_data,bytes) or len(thumb_data)>MAX_IMAGE_BYTES:
                raise ValueError("Invalid or oversized image data")
            facts=_image_facts(thumb_data)
            (target/(vid+".jpg")).write_bytes(thumb_data)
            image_status="THUMBNAIL_OBSERVED"
        except (OSError,ValueError,HTTPError,URLError,TimeoutError):
            thumb_data=None
        videos.append({
            "video_id":vid, "video_url":"https://www.youtube.com/watch?v="+vid,
            "channel_id":channel["channel_id"],"channel_name":channel["channel_name"],
            "public_approx_views":video["approx_views"],
            "public_video_age_days_proxy":video.get("video_age_days_proxy"),
            "title":video["title"],"source_topic_alignment":video["topic_title_alignment"],
            "thumbnail_status":image_status,
            "thumbnail_path":str(target/(vid+".jpg")) if thumb_data else None,
            "thumbnail_sha256":hashlib.sha256(thumb_data).hexdigest() if thumb_data else None,
            "thumbnail_image_facts":facts,
            "transcript_status":"NOT_OBSERVED",
            "actual_video_frames_status":"NOT_OBSERVED",
            "full_audio_status":"NOT_OBSERVED",
            "story_hook_status":"UNKNOWN",
            "animation_quality_status":"UNKNOWN",
            "copyright_clearance":"NOT_CLEARED",
            "reused_content_risk":"NOT_EVALUATED",
            "analysis_status":"PENDING_MULTIMODAL_REVIEW",
            "instructions":"Inspect actual footage with licensed access; cite exact seconds/frame and distinguish hypotheses. A thumbnail cannot prove pacing, sound, plot or retention.",
        })
    canonical_issue_file=source.parent/"council"/"council_issue.json"
    canonical_issue=None
    if canonical_issue_file.is_file():
        canonical_issue=json.loads(canonical_issue_file.read_text(encoding="utf-8"))
        if (not isinstance(canonical_issue,dict) or not isinstance(canonical_issue.get("issue_id"),str)
            or not isinstance(canonical_issue.get("question"),str)):
            raise ValueError("Invalid original shared council issue")
    tasks={
        "schema":"cine.research.deep_video_review.v1",
        "niche":report["niche"],"state":"PUBLIC_THUMBNAILS_PREPARED_REVIEW_PENDING",
        "source_evidence":{"path":str(source),"sha256":_sha(source)},
        "canonical_council_issue":canonical_issue,
        "canonical_council_issue_sha256":_sha(canonical_issue_file) if canonical_issue else None,
        "videos":videos,"selected_count":len(videos),
        "thumbnails_observed":sum(v["thumbnail_status"]=="THUMBNAIL_OBSERVED" for v in videos),
        "department_roles":list(ROLE_SET),
        "shared_question":"What reproducible ORIGINAL production hypotheses are supported by DIRECT visual/audio/timeline evidence, which claims remain unknown, and what competitor rights risks remain?",
        "review_must_include":["thumbnail visual evidence when available",
                               "actual frame observations when authorized video supplied",
                               "hook/structure/pacing/audio/animation only if directly inspected",
                               "Quality independent evidence challenge",
                               "release withheld without authenticated owner approval"],
        "production_permission":False,"council_decided":False,
        "no_automatic_semantic_claims":True,
        "same_youtube_source_is_not_independent_corroboration":True,
    }
    _write_json(target/"deep_review.json",tasks)
    return tasks


def observe_authorized_footage(source: str | Path, output_dir: str | Path, *,
                               niche: str, video_id: str, authorization: str,
                               max_frames: int=16, detect_changes: bool=True) -> dict:
    """Process a LOCAL file only when rights/user permission were explicitly declared."""
    if authorization not in ("OWNED","LICENSED","USER_PROVIDED_WITH_PERMISSION"):
        raise PermissionError("Explicit owned/licensed/user-authorized local footage required")
    if not isinstance(video_id,str) or not VIDEO_ID.fullmatch(video_id):
        raise ValueError("Exact ID binding required")
    if not isinstance(niche,str) or not niche.strip() or not 2<=max_frames<=48:
        raise ValueError("Niche and sampling limits required")
    src=Path(source).resolve(strict=True)
    dest=Path(output_dir).resolve()
    if dest.exists():
        raise FileExistsError("No overwrite of prior local footage observation")
    result=observe_smart(src,dest,max_frames=max_frames,detect_changes=detect_changes)
    from .scene_measurement import measure_sampled_frames
    measured=measure_sampled_frames(dest/"observation.json",dest/"scene_measurements.json")
    dispatch=create_department_tasks(result,dest/"review_tasks",niche=niche,
                                      reference_id=video_id,approved=False,
                                      departments=["story","visual","animation","audio","editorial","packaging","quality"])
    artifact={
        "schema":"cine.research.authorized_deep_observation.v1",
        "state":"FRAMES_AND_AUDIO_MEASURED_SEMANTICS_PENDING",
        "video_id":video_id,"niche":niche,
        "source_file":str(src),"authorization_claim":authorization,
        "observation_path":str((dest/"observation.json").resolve()),
        "scene_measurement_path":str((dest/"scene_measurements.json").resolve()),
        "pixel_facts_count":measured["frame_count"],
        "mean_sample_change_proxy":measured["average_inter_sample_change_proxy_0_1"],
        "frames_observed":result["sampling"]["frame_count"],
        "audio_measured":result["audio"]["present"],
        "department_task_count":len(dispatch["tasks"]),
        "department_approval_status":"pending_approval",
        "actual_semantic_analysis_completed":False,
        "production_permission":False,
        "limitations":["Frame samples do not establish the entire video narrative",
                       "Audio volume stats do not identify speech/music/sound effects",
                       "Authorization is declared by caller, not independently legally verified"],
    }
    _write_json(dest/"deep_video_manifest.json",artifact)
    return artifact


def verify_deep_video_review(review_json: str | Path) -> dict:
    """Audit original source, council issue and each exact immutable public image."""
    file=Path(review_json).resolve(strict=True)
    data=json.loads(file.read_text(encoding="utf-8"))
    if data.get("schema")!="cine.research.deep_video_review.v1":
        raise ValueError("Deep-video review format required")
    source=Path(data["source_evidence"]["path"]).resolve(strict=True)
    if _sha(source)!=data["source_evidence"]["sha256"]:
        raise ValueError("Source evidence changed after thumbnail research")
    original=json.loads(source.read_text(encoding="utf-8"))
    if original.get("schema")!="cine.research.automated_evidence.v1":
        raise ValueError("Wrong source evidence schema")
    issue_file=source.parent/"council"/"council_issue.json"
    if data.get("canonical_council_issue") is not None:
        if (not issue_file.is_file()
            or _sha(issue_file)!=data["canonical_council_issue_sha256"]
            or json.loads(issue_file.read_text(encoding="utf-8"))!=data["canonical_council_issue"]):
            raise ValueError("The original shared CineCouncil issue was altered")
    allowed={}
    for ch in original["channels"]:
        for v in ch.get("sample_longform_videos",[]):
            allowed[v["video_id"]]=(ch,v)
    checked=[]
    for v in data.get("videos",[]):
        vid=v["video_id"]
        if not VIDEO_ID.fullmatch(vid) or vid not in allowed or vid in checked:
            raise ValueError("Unknown, invalid or duplicated thumbnail video ID")
        ch,source_video=allowed[vid]
        if (v["channel_id"]!=ch["channel_id"]
            or v["video_url"]!="https://www.youtube.com/watch?v="+vid
            or v["title"]!=source_video["title"]
            or source_video.get("topic_title_alignment")!="ALL_NICHE_TITLE_TOKENS_PRESENT"):
            raise ValueError("Thumbnail record no longer matches source video")
        if v["thumbnail_status"]=="THUMBNAIL_OBSERVED":
            thumb=Path(v["thumbnail_path"]).resolve(strict=True)
            if thumb!=file.parent/(vid+".jpg") or _sha(thumb)!=v["thumbnail_sha256"]:
                raise ValueError("Thumbnail image was changed or redirected")
            image=_image_facts(thumb.read_bytes())
            if image!=v["thumbnail_image_facts"]:
                raise ValueError("Thumbnail measurements changed")
        elif v["thumbnail_status"]!="THUMBNAIL_UNAVAILABLE" or v.get("thumbnail_path") is not None:
            raise ValueError("Thumbnail state inconsistent")
        if (v.get("story_hook_status")!="UNKNOWN"
            or v.get("actual_video_frames_status")!="NOT_OBSERVED"
            or v.get("analysis_status")!="PENDING_MULTIMODAL_REVIEW"):
            raise ValueError("Cannot promote uninspected video content to verified semantics")
        checked.append(vid)
    if (len(checked)!=data.get("selected_count") or data.get("production_permission") is not False
        or data.get("council_decided") is not False
        or data.get("no_automatic_semantic_claims") is not True):
        raise ValueError("Deep review contains inconsistent promotion flags")
    return {"schema":"cine.research.deep_video_integrity.v1",
            "state":"SOURCE_AND_THUMBNAILS_INTEGRITY_OK_SEMANTIC_REVIEW_PENDING",
            "video_ids":checked,"verified_thumbnails":sum(
                v["thumbnail_status"]=="THUMBNAIL_OBSERVED" for v in data["videos"]),
            "council_issue_id":(data.get("canonical_council_issue") or {}).get("issue_id"),
            "production_permission":False}
