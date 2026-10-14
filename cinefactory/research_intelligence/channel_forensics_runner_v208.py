"""Bounded free/public yt-dlp channel-first research runner.

Reuses existing PublicYoutubeClient transport, makes no paid API calls, never
downloads third-party media or asserts unseen visual/audio content.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse

from cinefactory.studio.daily_youtube_breakout_v199 import PublicYoutubeClient
from cinefactory.studio.channel_forensics_v208 import (
    ChannelSample, Sample, VID, CID, analyze_channel,
    compare_peer, rank_peer_channels,
)

ALLOWED_HOSTS={"youtube.com","www.youtube.com","m.youtube.com","youtu.be"}
HANDLE=re.compile(r"^@[A-Za-z0-9_.-]{2,60}$")
USER_PATH=re.compile(r"^[A-Za-z0-9_.-]{2,80}$")


def normalize_reference(url: str) -> dict:
    """Allowlist URL parse, no injected paths/query commands forwarded."""
    parsed=urlparse(url.strip())
    if parsed.scheme!="https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("PUBLIC_YOUTUBE_HTTPS_URL_REQUIRED")
    if parsed.username or parsed.password or parsed.port:
        raise ValueError("CREDENTIALS_OR_CUSTOM_PORT_NOT_ALLOWED")
    segments=[s for s in parsed.path.rstrip("/").split("/") if s]
    if parsed.hostname=="youtu.be":
        if len(segments)!=1 or not VID.fullmatch(segments[0]):
            raise ValueError("INVALID_SHORT_VIDEO_LINK")
        return {"kind":"VIDEO","video_id":segments[0]}
    if segments and segments[0]=="watch":
        found=parse_qs(parsed.query).get("v",[])
        if len(found)!=1 or not VID.fullmatch(found[0]):
            raise ValueError("INVALID_VIDEO_URL_ID")
        return {"kind":"VIDEO","video_id":found[0]}
    if not segments:
        raise ValueError("MISSING_CHANNEL_ID_OR_HANDLE")
    if segments[0]=="channel":
        if len(segments)<2 or not CID.fullmatch(segments[1]):
            raise ValueError("INVALID_CHANNEL_ID")
        return {"kind":"CHANNEL","channel_url":
                "https://www.youtube.com/channel/"+segments[1]+"/videos",
                "channel_id":segments[1]}
    if ((HANDLE.fullmatch(segments[0]) and len(segments)<=2)
            or (segments[0] in {"c","user"} and len(segments)>=2
                and USER_PATH.fullmatch(segments[1]) and len(segments)<=3)):
        suffix=segments[0] if segments[0].startswith("@") else "/".join(segments[:2])
        return {"kind":"CHANNEL","channel_url":
                "https://www.youtube.com/"+suffix+"/videos",
                "channel_id":None}
    raise ValueError("UNSUPPORTED_YOUTUBE_CHANNEL_URL")


def _read_video(video_id: str,client: PublicYoutubeClient) -> Sample:
    if not VID.fullmatch(video_id):
        raise ValueError("INVALID_VIDEO_ID")
    output=client.read([
        "yt-dlp","--skip-download","--dump-single-json","--no-playlist",
        "--no-warnings","--socket-timeout","12","--retries","0",
        "https://www.youtube.com/watch?v="+video_id,
    ],timeout=38)
    raw=json.loads(output)
    if raw.get("id")!=video_id:
        raise ValueError("VIDEO_ID_DOES_NOT_MATCH_PUBLIC_SOURCE")
    live=raw.get("live_status")
    if raw.get("is_live") is True or live=="is_live":
        live_state="LIVE"
    elif raw.get("was_live") is True or live=="was_live":
        live_state="PAST_LIVE"
    elif live=="is_upcoming":
        live_state="UPCOMING"
    elif live=="not_live":
        live_state="NOT_LIVE"
    else:
        live_state="UNKNOWN"
    duration=raw.get("duration")
    views=raw.get("view_count")
    channel_id=raw.get("channel_id")
    upload_date=raw.get("upload_date")
    if not isinstance(channel_id,str) or not CID.fullmatch(channel_id):
        channel_id=None
    return Sample(
        video_id=video_id,
        channel_id=channel_id,
        title=str(raw.get("title") or "")[:450],
        description=str(raw.get("description") or "")[:2000],
        duration_seconds=(round(float(duration)) if isinstance(duration,(int,float))
                          and duration>=0 else None),
        views=views if isinstance(views,int) and views>=0 else None,
        published_at=str(upload_date) if upload_date else None,
        live_state=live_state,
        source="YT_DLP_PUBLIC_WATCH_METADATA_NOT_VISUAL_REVIEW",
    )


def _playlist_ids(url: str,client: PublicYoutubeClient,limit: int
                 ) -> tuple[list[str],dict[str,dict]]:
    if not 1<=limit<=16:
        raise ValueError("UNBOUNDED_CHANNEL_CATALOGUE")
    output=client.read([
        "yt-dlp","--flat-playlist","--dump-json",
        "--playlist-end",str(limit),"--no-warnings",
        "--socket-timeout","12","--retries","0",url,
    ],timeout=65)
    ids=[]
    seen=set()
    flat_rows={}
    for line in output.splitlines():
        try:row=json.loads(line)
        except json.JSONDecodeError:continue
        video_id=row.get("id")
        if isinstance(video_id,str) and VID.fullmatch(video_id) and video_id not in seen:
            ids.append(video_id)
            seen.add(video_id)
            flat_rows[video_id]=row
    return ids[:limit],flat_rows


def collect_channel(
    url: str,*,client: PublicYoutubeClient | None=None,
    max_videos: int=10,
) -> tuple[ChannelSample,list[str]]:
    client=client or PublicYoutubeClient()
    if not 2<=max_videos<=16:
        raise ValueError("CATALOGUE_SAMPLE_BUDGET_2_TO_16")
    ref=normalize_reference(url)
    problems=[]
    lead=None
    if ref["kind"]=="VIDEO":
        lead=_read_video(ref["video_id"],client)
        if lead.channel_id is None:
            raise ValueError("VIDEO_CHANNEL_ID_NOT_CONFIRMED")
        channel_url="https://www.youtube.com/channel/"+lead.channel_id+"/videos"
        expected=lead.channel_id
    else:
        channel_url=ref["channel_url"]
        expected=ref["channel_id"]
    ids,flat_rows=_playlist_ids(channel_url,client,max_videos)
    if lead and lead.video_id not in ids:
        ids=[lead.video_id]+ids[:max_videos-1]
    if len(ids)<2:
        raise ValueError("TOO_FEW_CHANNEL_VIDEO_IDS_FOR_CHANNEL_FORMAT_ANALYSIS")
    samples=[]
    if lead:
        samples.append(lead)
    for video_id in ids:
        if lead and lead.video_id==video_id:continue
        try:
            item=_read_video(video_id,client)
            if expected and item.channel_id and item.channel_id!=expected:
                problems.append("OTHER_CHANNEL_VIDEO_EXCLUDED:"+video_id)
                continue
            samples.append(item)
        except (ValueError,RuntimeError,KeyError,OSError) as err:
            problems.append("WATCH_METADATA_UNAVAILABLE:"+video_id+":"+type(err).__name__)
            # A playlist row is only a weak discovery signal, not watched or
            # officially read-back evidence. Preserve it instead of inventing
            # 0 views, a publication date, or a non-live assertion.
            flat=flat_rows.get(video_id,{})
            cid=flat.get("playlist_channel_id")
            if not isinstance(cid,str) or not CID.fullmatch(cid):
                cid=expected
            if not isinstance(cid,str) or not CID.fullmatch(cid):
                problems.append("PLAYLIST_CHANNEL_ID_UNVERIFIED:"+video_id)
                continue
            if expected and cid!=expected:
                problems.append("OTHER_CHANNEL_PLAYLIST_ENTRY_EXCLUDED:"+video_id)
                continue
            title=flat.get("title")
            if not isinstance(title,str) or not title.strip():
                problems.append("PLAYLIST_TITLE_NOT_AVAILABLE:"+video_id)
                continue
            duration=flat.get("duration")
            if not isinstance(duration,(float,int)) or duration<0:
                duration=None
            samples.append(Sample(
                video_id=video_id,channel_id=cid,
                title=title[:450],
                duration_seconds=round(duration) if duration is not None else None,
                live_state="UNKNOWN",
                views=None,
                published_at=None,
                source="FLAT_PLAYLIST_TITLE_DURATION_ONLY_NOT_WATCH_VERIFIED",
            ))
    if len(samples)<2:
        raise ValueError("INSUFFICIENT_CHANNEL_WATCH_METADATA")
    proven_ids={v.channel_id for v in samples if v.channel_id}
    if expected is not None and proven_ids and proven_ids!={expected}:
        raise ValueError("CHANNEL_ID_MISMATCH")
    if expected is None and len(proven_ids)!=1:
        raise ValueError("CHANNEL_ID_COULD_NOT_BE_RESOLVED_UNIQUELY")
    canonical_id=expected or next(iter(proven_ids))
    if any(v.channel_id is None for v in samples):
        problems.append("SOME_SAMPLES_LACK_INDEPENDENT_CHANNEL_ID")
    return (ChannelSample(
        channel_id=canonical_id,submitted_url=url,
        videos=samples,collected_at=datetime.now(timezone.utc).isoformat(),
    ),problems)


def search_peers(
    profile: dict,*,client: PublicYoutubeClient | None=None,
    max_queries: int=3,limit_per_query: int=5,
    max_watch_metadata: int=12,
) -> dict:
    client=client or PublicYoutubeClient()
    if not (1<=max_queries<=4 and 1<=limit_per_query<=8
            and 1<=max_watch_metadata<=24):
        raise ValueError("COMPETITOR_DISCOVERY_REQUEST_LIMIT_EXCEEDED")
    minor=profile.get("dominant_minor_niche")
    query_plan=profile.get("search_plan",{})
    all_queries=query_plan.get("queries",[])[:max_queries]
    if not minor or not all_queries:
        return {"status":"NEEDS_BETTER_CHANNEL_FORMAT_EVIDENCE",
                "peer_matches":None,"queries_run":[],"query_errors":[]}
    if minor=="minecraft_live_gameplay":
        return {"status":"LIVESTREAM_NEEDS_SEPARATE_PEER_RESEARCH_NOT_LONGFORM",
                "peer_matches":None,"queries_run":[],
                "query_errors":[],"live_longform_breakout_excluded":True}
    ids=[]
    observed=set()
    query_events=[]
    errors=[]
    for query in all_queries:
        phrase=query["query"]
        try:
            rows=client.search(phrase,limit=limit_per_query)
            query_events.append({"axis":query["axis"],"query":phrase,
                                 "public_hits":len(rows)})
            for row in rows:
                vid=row.get("id")
                if (isinstance(vid,str) and VID.fullmatch(vid)
                        and vid not in observed):
                    observed.add(vid)
                    ids.append(vid)
        except (ValueError,RuntimeError,OSError) as exc:
            errors.append({"query_axis":query["axis"],
                           "error_type":type(exc).__name__})
    samples=[]
    reference_id=profile.get("source_channel_id")
    for video_id in ids[:max_watch_metadata]:
        try:
            video=_read_video(video_id,client)
            if video.channel_id==reference_id:
                continue
            samples.append(video)
        except (ValueError,RuntimeError,OSError) as exc:
            errors.append({"video_id":video_id,
                           "error_type":type(exc).__name__})
    peer=rank_peer_channels(minor,samples)
    return {
        "status":"PUBLIC_METADATA_SHORTLIST_NOT_VISUALLY_VERIFIED",
        "queries_run":query_events,
        "query_errors":errors,
        "search_results_unique_video_ids":len(ids),
        "watch_metadata_checked":len(samples),
        "peer_matches":peer,
        "no_paid_credits_used":True,
        "no_competitor_video_downloaded":True,
        "actual_video_watch_analysis_done":False,
    }


def run_forensics(
    url: str,*,client: PublicYoutubeClient | None=None,
    sample: ChannelSample | None=None,
    search: bool = False,max_videos: int=10,
) -> dict:
    if sample is None:
        snapshot,errors=collect_channel(
            url,client=client,max_videos=max_videos,
        )
        ingestion="LIVE_PUBLIC_METADATA_NOT_OFFICIAL_VERIFICATION"
    else:
        normalize_reference(url)
        if sample.submitted_url!=url:
            raise ValueError("INPUT_LINK_AND_SNAPSHOT_REFER_TO_DIFFERENT_REQUESTS")
        snapshot=sample
        errors=[]
        ingestion="USER_SUPPLIED_UNTRUSTED_PUBLIC_METADATA_SNAPSHOT"
    analysis=analyze_channel(snapshot)
    # Technical R&D must follow the per-video niche taxonomy. A mixed
    # channel receives separate recommendations; never conflate genuine
    # gameplay, original animation and real livestream capture.
    from cinefactory.studio.technology_discovery_v211 import (
        propose_technology_for_format,
    )
    tech_by_format={
        fmt:propose_technology_for_format(
            fmt,analysis.get("market_major_niche")
        )
        for fmt,count in analysis.get("minor_niche_counts",{}).items()
        if count>=2
    }
    from cinefactory.studio.technology_council_v212 import (
        counsel_for_all_departments,
    )
    department_tech_by_format={
        fmt:counsel_for_all_departments(
            fmt,analysis.get("market_major_niche")
        )
        for fmt in tech_by_format
    }
    digest=sha256(snapshot.model_dump_json().encode("utf8")).hexdigest()
    peers=search_peers(analysis,client=client) if search else {
        "status":"SEARCH_NOT_REQUESTED","queries_run":[],"peer_matches":None,
    }
    return {
        "schema":"cine.research.channel_first_dossier.v208",
        "source_url":url,"ingestion":ingestion,
        "source_snapshot_sha256":digest,
        "snapshot":snapshot.model_dump(mode="json"),
        "classification":analysis,
        "competitor_discovery":peers,
        "technology_advisory":{
            "schema":"cine.research.competitor_technology_handoff.v211",
            "by_metadata_format_candidate":tech_by_format,
            "whole_company_department_options_by_format":department_tech_by_format,
            "actual_competitor_tools_verified":False,
            "source_is_metadata_not_visual_forensics":True,
            "directly_installable":False,
            "new_repos_require_separate_public_discovery":True,
        },
        "source_errors":errors,
        "watch_metadata_readback_complete":all(
            video.source=="YT_DLP_PUBLIC_WATCH_METADATA_NOT_VISUAL_REVIEW"
            for video in snapshot.videos
        ) if sample is None else False,
        "playlist_only_video_count":sum(
            x.source.startswith("FLAT_PLAYLIST_") for x in snapshot.videos
        ),
        "industry_market_winner_verified":False,
        "studio_production_approved":False,
        "need_independent_visual_video_review":True,
        "next_actions":[
            "Review a representative sample with visual/audio/timecoded evidence",
            "Recheck source channels and video IDs with official provider metadata if available",
            "Only compare same-audience-intent and same-media-provenance peer videos",
            "Audit repeatable formats and breakout metrics before signed Studio handoff",
        ],
    }


def store_dossier(dossier: dict,destination: str | Path) -> Path:
    path=Path(destination).resolve()
    path.parent.mkdir(parents=True,exist_ok=True)
    # No reanalysis silently overwrites the previous time-stamped source run.
    with path.open("x",encoding="utf8") as out:
        out.write(json.dumps(dossier,ensure_ascii=False,indent=2)+"\n")
    return path
