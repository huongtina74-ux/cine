"""Cross-check every imported Company claim against its frozen CSV lineage.

Source SHA alone does NOT authenticate derived fields in an editable bridge JSON.
This is a consistency and tamper gate, NOT independent verification that a CSV's
YouTube metadata was true. Independent API/human review remains mandatory.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

from .triage import triage_niches

CHECKED={"VERIFIED","SOURCE_VERIFIED","MANUALLY_VERIFIED"}
ALLOWED_FORMAT={"video","long","longform","long-form","standard"}
ALLOWED_FIT={"direct","direct_match","exact"}


def _ts(value):
    if not isinstance(value,str) or not value:
        raise ValueError("Missing bridge timestamp")
    v=datetime.fromisoformat(value.strip().replace("Z","+00:00"))
    if v.tzinfo is None:raise ValueError("Naive bridge timestamp")
    return v.astimezone(timezone.utc)


def _csv(path,required):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError("Canonical CSV schema missing fields")
        return list(reader)


def _int_source(value):
    if not isinstance(value,str) or not value.isdigit():
        raise ValueError("Malformed source integer")
    return int(value)


def verify_bridge_semantics(bridge:dict, channel_source, video_source)->None:
    """Reject fabricated bridge candidates, channel/video claims and triage gates."""
    now=_ts(bridge["as_of"])
    if (not isinstance(bridge.get("candidates"),list) or
        len(bridge["candidates"])!=1 or not isinstance(bridge["candidates"][0],dict)):
        raise ValueError("Exactly one imported canonical candidate required")
    candidate=bridge["candidates"][0]
    if candidate.get("niche")!=bridge.get("niche") or _ts(candidate.get("observed_at"))!=now:
        raise ValueError("Imported candidate niche/time differs from source")
    flags=bridge.get("review_flags")
    if not isinstance(flags,dict):
        raise ValueError("Imported review flags absent")
    for source, derived in (
        ("novel_format_verified","novel_format_verified"),
        ("recent_evergreen_evidence","recent_evergreen_evidence"),
        ("business_case_evidence","business_case_evidence"),
        ("newcomer_evidence","newcomer_evidence")):
        if type(candidate.get(derived)) is not bool or candidate[derived] is not flags.get(source):
            raise ValueError("Imported review evidence flags were modified")
    channel_rows=_csv(channel_source,{"channel_id","created_at","snapshot_at","channel_url","evidence_status"})
    video_rows=_csv(video_source,{"video_id","channel_id","views","published_at","snapshot_at","duration_seconds",
                                  "video_url","format_proxy","topic_cluster","topic_fit","evidence_status"})
    chan_index=defaultdict(list)
    for row in channel_rows:
        chan_index[row.get("channel_id")].append(row)
    vid_index=defaultdict(list)
    for row in video_rows:
        vid_index[(row.get("channel_id"),row.get("video_id"))].append(row)
    channels=candidate.get("channels")
    if not isinstance(channels,list):
        raise ValueError("Candidate channel records missing")
    known=set();all_video_ids=set();urls=[]
    for channel in channels:
        if not isinstance(channel,dict):
            raise ValueError("Malformed channel record")
        cid=channel.get("channel_id")
        if not isinstance(cid,str) or not cid or cid in known:
            raise ValueError("Duplicate/missing channel ID in imported candidate")
        known.add(cid)
        observed=_ts(channel.get("observed_at"))
        eligible=[]
        for src in chan_index.get(cid,[]):
            try:
                if (_ts(src["snapshot_at"])!=observed or
                    src.get("created_at")!=channel.get("created_at") or
                    src.get("channel_url")!=channel.get("channel_url") or
                    src.get("evidence_status")!=channel.get("evidence_status") or
                    src.get("channel_name","")!=channel.get("channel_name","")):
                    continue
                sub=(_int_source(src["subscriber_count"])
                     if str(src.get("subscriber_count") or "").isdigit() else None)
                if sub!=channel.get("subscriber_count"):
                    continue
                creation=channel.get("created_at")
                age=round((now-_ts(creation)).total_seconds()/86400,3) if creation else -1.0
                if age!=channel.get("age_days"):continue
                eligible.append(src)
            except (KeyError,TypeError,ValueError,OverflowError):
                continue
        if not eligible:
            raise ValueError("Bridge channel metadata is not backed by Company CSV")
        videos=channel.get("videos")
        if not isinstance(videos,list):
            raise ValueError("Bridge channel missing video evidence")
        for v in videos:
            if not isinstance(v,dict) or not isinstance(v.get("video_id"),str):
                raise ValueError("Malformed imported video record")
            vid=v["video_id"]
            if vid in all_video_ids:
                raise ValueError("Duplicate video ID across imported channels")
            all_video_ids.add(vid)
            matches=[]
            for src in vid_index.get((cid,vid),[]):
                try:
                    if (src["video_url"]!=v.get("source_url") or
                        src.get("evidence_status")!=v.get("evidence_status") or
                        src.get("topic_cluster")!=v.get("topic_cluster") or
                        src.get("title","")!=v.get("title","") or
                        _ts(src["snapshot_at"])!=_ts(v["observed_at"]) or
                        _ts(src["published_at"])!=_ts(v["published_at"]) or
                        _int_source(src["views"])!=v.get("views") or
                        _int_source(src["duration_seconds"])!=v.get("duration_seconds") or
                        _int_source(src["duration_seconds"])<480 or
                        src.get("format_proxy","").lower() not in ALLOWED_FORMAT or
                        src.get("topic_fit","").lower() not in ALLOWED_FIT or
                        src.get("topic_cluster","").casefold()!=bridge["niche"].casefold()):
                        continue
                    matches.append(src)
                except (KeyError,ValueError,TypeError,OverflowError):
                    continue
            if not matches:
                raise ValueError("Bridge video metadata is not backed by Company CSV")
            urls.append(v["source_url"])
    if candidate.get("evidence_urls")!=list(dict.fromkeys(urls)):
        raise ValueError("Bridge evidence links were modified")
    permitted={
        "channels":[
            {**ch,"videos":[v for v in ch["videos"]
                               if str(v.get("evidence_status","")).upper() in CHECKED]}
            for ch in channels
            if str(ch.get("evidence_status","")).upper() in CHECKED
        ]
    }
    recomputed=triage_niches([{**candidate,**permitted}],max_deep_reviews=1)["candidates"][0]
    if bridge.get("triage")!=recomputed:
        raise ValueError("Bridge triage/approval gates differ from actual source-linked candidate")
