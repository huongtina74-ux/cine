"""Quota-bounded official recheck of shortlisted candidates only.

Uses 1-unit YouTube Data API channels.list/videos.list calls (no search.list).
No API key? Fail closed with a pending queue and ZERO calls.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from .breakout_proof import audit_official_artifact
from .core import _write_json

CID = re.compile(r"UC[A-Za-z0-9_-]{22}$")
VID = re.compile(r"[A-Za-z0-9_-]{11}$")
DURATION = re.compile(r"^P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")


def _utc(value: str) -> datetime:
    x = datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if x.tzinfo is None: raise ValueError("Timezone required")
    return x.astimezone(timezone.utc)


def _seconds(value: str) -> int:
    m = DURATION.fullmatch(str(value))
    if not m: raise ValueError("Unexpected ISO 8601 video duration")
    d,h,mi,s = (int(x or 0) for x in m.groups())
    return 86400*d+3600*h+60*mi+s


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _api(endpoint: str, ids: list[str], key: str) -> dict:
    if endpoint not in ("channels", "videos") or len(ids)>50 or not ids:
        raise ValueError("Invalid endpoint / batch")
    parts = ("snippet,statistics" if endpoint=="channels"
             else "snippet,contentDetails,statistics,status,liveStreamingDetails")
    url = "https://www.googleapis.com/youtube/v3/"+endpoint+"?"+urlencode(
        {"part":parts,"id":",".join(ids),"key":key,"maxResults":50}
    )
    try:
        with urlopen(url, timeout=15) as stream:
            data=json.load(stream)
    except Exception as exc:
        # Never include urllib exception messages: they may reveal the URL/API key.
        raise RuntimeError("Official verification request failed; inspect quota/network from authorized console") from None
    if not isinstance(data,dict) or not isinstance(data.get("items"),list):
        raise ValueError("Unexpected official API response")
    return data


def verify_targeted_queue(prescreen_file: str | Path, output_dir: str | Path,
                          *, max_channels: int=8, max_requests: int=4,
                          now: str | None=None, api_key: str | None=None,
                          fetch_json=None) -> dict:
    src=Path(prescreen_file).resolve(strict=True)
    obj=json.loads(src.read_text(encoding="utf-8"))
    if obj.get("schema")!="cine.research.public_prescreen.v1":
        raise ValueError("Not a canonical public prescreen report")
    if not 1 <= max_channels <= 50 or not 1 <= max_requests <= 20:
        raise ValueError("Exceeded official verification budget")
    at=_utc(now) if now else datetime.now(timezone.utc)
    collection=_utc(obj["collection_at"])
    age_hours=(at-collection).total_seconds()/3600
    if not 0 <= age_hours <=48 or not obj.get("fresh_for_daily"):
        raise ValueError("Cannot verify old public candidates as newly discovered")
    # Ensure candidate source artifacts have not been substituted after prescreen.
    for srcinfo in obj["sources"].values():
        file=Path(srcinfo["path"]).resolve(strict=True)
        if _sha(file)!=srcinfo["sha256"]:
            raise ValueError("Public source mutated since prescreen")
    queue=obj.get("requests_for_official_verification") or []
    if queue and obj.get("state")!="PROVISIONAL_QUEUE_READY":
        raise ValueError("Queue must originate from a current provisional prescreen")
    candidates={x.get("channel_id"):x for x in obj.get("candidates",[]) if isinstance(x,dict)}
    selected=[]
    for task in queue:
        cid=task.get("channel_id")
        videos=task.get("video_ids")
        if not isinstance(cid,str) or not CID.fullmatch(cid) or not isinstance(videos,list):
            raise ValueError("Malformed verification candidate")
        candidate=candidates.get(cid)
        if (not candidate or candidate.get("verification_state")!="PROVISIONAL_PUBLIC_SOURCE"
                or candidate.get("level") not in ("TWO_DISPLAY_MILLION","TWO_NEAR_MILLION")):
            raise ValueError("Verification ID not backed by a selected public candidate")
        allowed={v.get("video_id") for v in candidate.get("videos",[])
                 if isinstance(v,dict) and (v.get("approx_views") or 0)>=700_000}
        ids=list(dict.fromkeys(videos))
        if not set(ids).issubset(allowed):
            raise ValueError("Verification video IDs do not match observed candidate evidence")
        if len(ids)<2 or len(ids)>12 or any(not isinstance(v,str) or not VID.fullmatch(v) for v in ids):
            raise ValueError("Malformed exact-video verification IDs")
        if cid not in {x["channel_id"] for x in selected}:
            selected.append({"channel_id":cid,"video_ids":ids})
        if len(selected)>=max_channels:
            break
    output=Path(output_dir).resolve()
    output.mkdir(parents=True,exist_ok=True)
    # Individual requests cost 1 unit for channels.list and videos.list. No public search API.
    all_vids=list(dict.fromkeys(vid for item in selected for vid in item["video_ids"]))
    chunks=lambda ids:[ids[i:i+50] for i in range(0,len(ids),50)]
    expected=len(chunks([x["channel_id"] for x in selected]))+len(chunks(all_vids))
    report={
        "schema":"cine.research.targeted_official_verification.v1",
        "prescreen_sha256":_sha(src),"source_path":str(src),
        "candidate_channels":len(selected),"candidate_video_ids":len(all_vids),
        "estimated_quota_units":expected, "max_request_budget":max_requests,
        "actual_api_calls":0,"niches_verified":0,
        "approved_to_produce":False,
    }
    if not selected:
        report["state"]="NO_CANDIDATES_TO_VERIFY"
        _write_json(output/"official_verification_report.json",report)
        return report
    if expected>max_requests:
        report["state"]="BLOCKED_QUOTA_BUDGET"
        _write_json(output/"official_verification_report.json",report)
        return report
    key=api_key if api_key is not None else next(
        (os.environ[k] for k in ("YOUTUBE_DATA_API_KEY","YOUTUBE_API_KEY","GOOGLE_API_KEY") if os.environ.get(k)),None)
    if not key:
        report["state"]="BLOCKED_NEEDS_OFFICIAL_API_KEY"
        _write_json(output/"official_verification_report.json",report)
        return report
    get=fetch_json or _api
    try:
        found_channels={}
        found_videos={}
        for batch in chunks([x["channel_id"] for x in selected]):
            report["actual_api_calls"]+=1
            response=get("channels",batch,key)
            for c in response["items"]:
                found_channels[c["id"]]=c
        for batch in chunks(all_vids):
            report["actual_api_calls"]+=1
            response=get("videos",batch,key)
            for v in response["items"]:
                found_videos[v["id"]]=v
        artifact={"generated_at":at.isoformat(),"source":"targeted_official_youtube_data_api",
                  "channels":{},"catalogs":{}}
        for item in selected:
            cid=item["channel_id"]
            raw=found_channels.get(cid)
            if not raw:continue
            snippet=raw.get("snippet") or {}
            artifact["channels"][cid]={
                "channel_id":cid,"channel_url":"https://www.youtube.com/channel/"+cid,
                "channel_name":snippet.get("title",""),
                "created_at":snippet.get("publishedAt"),
                "subscribers":(raw.get("statistics") or {}).get("subscriberCount"),
                "evidence_status":"VERIFIED",
            }
            catalog=[]
            for vid in item["video_ids"]:
                v=found_videos.get(vid)
                if not v:continue
                s=v.get("snippet") or {}
                if s.get("channelId")!=cid:continue
                stats=v.get("statistics") or {}
                details=v.get("contentDetails") or {}
                status=v.get("status") or {}
                try:
                    views=int(stats["viewCount"])
                    duration=_seconds(details["duration"])
                except (KeyError,ValueError,TypeError):
                    continue
                catalog.append({
                    "video_id":vid,"video_url":"https://www.youtube.com/watch?v="+vid,
                    "channel_id":cid,"title":s.get("title",""),
                    "published_at":s.get("publishedAt"),"views":views,
                    "duration_seconds":duration,"format_proxy":"LONG_FORM" if duration>=480 else "SHORT_PROXY",
                    "privacy_status":status.get("privacyStatus","public"),
                    "is_live":bool(v.get("liveStreamingDetails")) or s.get("liveBroadcastContent") in ("live","upcoming"),
                    "evidence_status":"VERIFIED",
                })
            artifact["catalogs"][cid]=catalog
        art_file=output/"targeted_official_artifact.json"
        _write_json(art_file,artifact)
        audit=audit_official_artifact(art_file,output/"strict_breakout_audit.json",
                                      observed_at=at.isoformat())
        report.update({
            "state":"OFFICIAL_RECHECK_COMPLETE",
            "channels_returned":len(found_channels),
            "videos_returned":len(found_videos),
            "strict_witness_channels":len(audit["witness_channels"]),
            "strict_breakout_audit_file":str(output/"strict_breakout_audit.json"),
            "missing_video_ids":sorted(set(all_vids)-set(found_videos)),
            "limitations":["No full channel catalog enumeration; only shortlisted video IDs checked",
                           "Official public metadata is not niche, ownership, evergreen or RPM evidence",
                           "Candidate prescreen 'joined date' is superseded by exact publishedAt on official recheck"],
        })
    except (ValueError,RuntimeError,KeyError,TypeError) as exc:
        report["state"]="OFFICIAL_RECHECK_FAILED"
        report["error_code"]=type(exc).__name__
        # No user-provided exception text: key material must never surface.
    _write_json(output/"official_verification_report.json",report)
    return report
