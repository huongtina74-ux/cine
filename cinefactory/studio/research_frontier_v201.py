"""Autonomous 'unknown emerging format' frontier for CineFactory Branch 1.

Queries are broad format/innovation probes and not sourced from existing
niche manifests. Search engine order is non-exhaustive, NOT "trending".
Video metadata is independently fetched, and classified only into known
format signals or UNKNOWN FORMAT NEEDS HUMAN/CLAUDE REVIEW.
Search results may be ordinary videos; no claim of a new niche is made.
"""
from __future__ import annotations
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any
from .daily_youtube_breakout_v199 import PublicYoutubeClient,VIDEO_RE,UTC
from .niche_competitor_guard_v200 import format_signals

# Global open-ended probes separate from approved niche searches.
FRONTIER_QUERIES=(
    "new viral long form animation full episode",
    "newly trending 3d simulation game animals funny",
    "AI generated cinematic storytelling original movie",
    "viral no talking relaxing visual long video",
    "new creative educational animated story English",
    "original experimental virtual world gameplay challenge",
)
def find_frontier(*,root:Path,client:PublicYoutubeClient|None=None,
                  now:dt.datetime|None=None,
                  queries:int=4,limit_per_query:int=3,max_watch:int=8)->dict:
    if not 1<=queries<=len(FRONTIER_QUERIES) or not 1<=limit_per_query<=4 or not 1<=max_watch<=15:
        raise ValueError("GLOBAL_DISCOVERY_BUDGET_EXCEEDED")
    client=client or PublicYoutubeClient()
    now=now or dt.datetime.now(UTC)
    if now.tzinfo is None:raise ValueError("UTC_AWARE_TIME_REQUIRED")
    now=now.astimezone(UTC)
    search=[]
    ids={}
    errors=[]
    for keyword in FRONTIER_QUERIES[:queries]:
        try:
            rows=client.search(keyword,limit=limit_per_query)
            search.append({"keyword":keyword,"public_results":len(rows)})
            for row in rows:
                vid=row.get("id")
                if isinstance(vid,str) and VIDEO_RE.fullmatch(vid):
                    ids.setdefault(vid,{"search_phrase":keyword,
                                        "title_hint":row.get("title")})
        except Exception as ex:
            errors.append({"keyword":keyword,"error":type(ex).__name__+":"+str(ex)[:120]})
    findings=[]
    for vid,hint in list(ids.items())[:max_watch]:
        try:
            # v199 metadata parser requires a signed existing *search lane*.
            # Here the request is deliberately UNCLASSIFIED so use the public
            # yt-dlp dump read function without inventing a niche.
            raw=client.read([
                "yt-dlp","--skip-download","--dump-single-json","--no-playlist",
                "--no-warnings","--socket-timeout","12","--retries","0",
                "https://www.youtube.com/watch?v="+vid],timeout=38)
            item=json.loads(raw)
            if item.get("id")!=vid or not isinstance(item.get("view_count"),int):continue
            published=item.get("upload_date")
            if not isinstance(published,str) or not re.fullmatch(r"\d{8}",published):continue
            age=(now.date()-dt.date(int(published[:4]),int(published[4:6]),int(published[6:]))).days
            if age<0 or age>30 or float(item.get("duration") or 0)<480 or item.get("was_live") is True:
                continue
            sig=sorted(format_signals(str(item.get("title") or "")))
            findings.append({
                "video_id":vid,
                "url":"https://www.youtube.com/watch?v="+vid,
                "title":str(item.get("title") or "")[:240],
                "channel_id":item.get("channel_id"),
                "published_utc_day":published,
                "approx_age_days":age,"public_view_count":item["view_count"],
                "known_existing_format_signals":sig,
                "format_status":"KNOWN_FORMAT_DO_NOT_REDUPLICATE" if sig else
                    "UNKNOWN_FORMAT_CREATIVE_RESEARCH_REQUIRED",
                "new_niche_verified":False,
                "channel_age_verified":False,
                "two_million_videos_confirmed":False,
                "recurring_demand_confirmed":False,
                "earning_potential_verified":False,
                "public_source":"YT_DLP_YOUTUBE_WATCH_METADATA",
                "actual_video_played":False,
                "query_origin":hint["search_phrase"],
            })
        except Exception as ex:
            errors.append({"video_id":vid,"error":type(ex).__name__+":"+str(ex)[:120]})
    payload={
        "schema":"cinefactory-open-frontier-v1.6.41",
        "status":"FRONTIER_RESEARCH_BACKLOG_NOT_WINNING_NICHES",
        "as_of":now.isoformat(),
        "queries":search,"candidate_videos":findings,
        "unclassified_count":sum(x["format_status"].startswith("UNKNOWN") for x in findings),
        "no_competitor_video_copied":True,
        "needs_novelty_and_two_million_videos_gates":True,
        "search_is_not_latest_or_exhaustive":True,
        "errors":errors,
    }
    root=Path(root)
    folder=root/"data/research/youtube_breakout/frontier"
    folder.mkdir(parents=True,exist_ok=True)
    file=folder/("frontier_"+now.strftime("%Y%m%dT%H%M%S")+".json")
    file.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    return payload
