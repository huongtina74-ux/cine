"""Niche 2: approved format's separate daily keyword research engine.

No approved niche => zero YouTube requests; never scans others in that mode.
Source types: title/metadata snapshots; leader popular uploads from owned
watchlist and historical search are exploratory, not an all-time video ranking.
"""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
from typing import Any
from .two_track_research_v201 import DualResearchStore,LANE_TO_NICHE
from .daily_youtube_breakout_v199 import (
    BreakoutLedger,PublicYoutubeClient,VIDEO_RE,UTC,valid_utc
)
from .niche_competitor_guard_v200 import validate_video_niche

# Dedicated rotating search hypotheses; NOT claims of searchable age sort.
# Search results can be incomplete or sorted by opaque YouTube logic.
KEYWORD_PACKS={
    "minecraft_gameplay":(
        "minecraft 100 days hardcore survival",
        "minecraft 100 days challenge new",
        "minecraft 100 days expanding world",
        "jj mikey minecraft gameplay challenge survival",
    ),
    "minecraft_animation":(
        "minecraft animation full movie story",
        "jj mikey maizen minecraft animation verity mutants",
        "minecraft animation sad origin cursed monster full episode",
        "minecraft animated movie funny",
    ),
    "preschool_musical":(
        "3d nursery rhymes kids songs animation",
        "3d baby songs preschool original",
        "animated abc song nursery kids",
    ),
    "long_slide_game":(
        "3d animal long slide game funny",
        "animals slide race 3d game",
        "animal obstacle mega slide challenge",
    ),
    "roblox_animation":(
        "roblox r6 animation movie",
        "roblox animated story funny",
        "roblox cartoon r15 animation",
    ),
    "animal_animation":(
        "3d animal animation movie",
        "animated animal adventure film",
        "3d animal cartoon original",
    ),
    "gta_gameplay":(
        "gta v gameplay challenge",
        "gta grand theft auto missions gameplay",
        "gta v police chase gameplay",
    ),
    "ai_storytelling":(
        "ai cinematic family drama movie",
        "ai film family story",
        "ai generated original fiction movie",
    ),
    "cartoon_2d":(
        "2d cartoon animation full episode",
        "2d animated original movie",
        "2d cartoon long story",
    ),
    "asmr_sleep":(
        "asmr sleep hand sounds no talking",
        "asmr tapping hand triggers sleep",
        "asmr relaxation sleep long form",
    ),
    "audio_storytelling_seniors":(
        "senior life stories audio full",
        "bedtime stories for adults 2 hours",
        "senior storytelling long listening",
    ),
    "rain_sleep_white_noise":(
        "rain sounds for sleep no ads",
        "rain ambience white noise 3 hours",
        "rain for sleep thunderstorm sounds",
    ),
    "fishing_silent":(
        "silent fishing session no talking",
        "no commentary fishing trip",
        "fishing adventure silent long form",
    ),
    "daily_english":(
        "daily english listening practice long",
        "english conversation speaking practice",
        "learn english daily listening story",
    ),
}
assert set(KEYWORD_PACKS)==set(LANE_TO_NICHE)

def search_approved_formats(*,root:Path,client:PublicYoutubeClient|None=None,
                            as_of:dt.datetime|None=None,
                            per_niche_keywords:int=3,max_total_metadata:int=24,
                            per_query:int=4)->dict:
    if not 1<=per_niche_keywords<=4 or not 1<=max_total_metadata<=48 or not 1<=per_query<=20:
        raise ValueError("DEEP_RESEARCH_BUDGET_INVALID")
    root=Path(root).resolve()
    client=client or PublicYoutubeClient()
    store=DualResearchStore(root/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
    approvals=[row for row in store.approvals() if row["state"]=="APPROVED"]
    now=(as_of or dt.datetime.now(UTC)).astimezone(UTC)
    if not approvals:
        return {"status":"NO_APPROVED_NICHES_NO_NETWORK_CONTACT",
                "api_requests":0,"approved_formats":0,
                "results":[],"errors":[],"cross_niche_not_used":True}
    ledger=BreakoutLedger(store.path)
    watched=[]
    errors=[]
    candidates={}
    research_queries=[]
    for approved in approvals:
        fmt=approved["format_id"]
        if fmt not in KEYWORD_PACKS:continue
        for phrase in KEYWORD_PACKS[fmt][:per_niche_keywords]:
            try:
                entries=client.search(phrase,limit=per_query)
                research_queries.append({"niche_id":approved["niche_id"],
                                         "format_id":fmt,"search_phrase":phrase,
                                         "returned":len(entries)})
                for row in entries:
                    vid=row.get("id")
                    if isinstance(vid,str) and VIDEO_RE.fullmatch(vid):
                        candidates.setdefault((fmt,vid),{"niche_id":approved["niche_id"],
                                                         "keyword":phrase})
            except Exception as e:
                errors.append({"format_id":fmt,"keyword":phrase,
                               "error":type(e).__name__+":"+str(e)[:130]})
    # Purely additive: do not deduplicate across formats by ID as a single
    # creator could make different modes. Format gate decides per video.
    # Round-robin candidates across approved formats. Without this, the first
    # approved format monopolizes all metadata slots and silently starves the
    # others (observed on the real two-format Minecraft activation, 2026-10-11).
    pending={fmt:[key for key in candidates if key[0]==fmt]
             for fmt in sorted({a["format_id"] for a in approvals})}
    keys=[]
    while len(keys)<max_total_metadata and any(pending.values()):
        for fmt in pending:
            if pending[fmt] and len(keys)<max_total_metadata:
                keys.append(pending[fmt].pop(0))
    run_id=ledger.begin(now.isoformat(),sorted(set(fmt for fmt,_ in keys)) or [
                        x["format_id"] for x in approvals])
    admitted=[]
    quarantined=[]
    for fmt,vid in keys:
        meta=candidates[(fmt,vid)]
        try:
            v=client.video(vid,lane=fmt)
            check=validate_video_niche(v.title,fmt)
            if check.status!="MATCHED_METADATA_FORMAT_CANDIDATE":
                quarantined.append({"video_id":vid,"format_id":fmt,"error":check.reason})
                continue
            age=(now.date()-dt.date(
                int(v.published_date[:4]),int(v.published_date[4:6]),int(v.published_date[6:]))).days
            if age<0 or v.duration_sec<480 or v.is_live:continue
            # Allows older videos for leader popularity comparisons, while
            # recent 0-15 days are explicitly computed by Branch 2 evaluator.
            ledger.ingest(run_id,v,now.isoformat(),1)
            admitted.append({"niche_id":meta["niche_id"],"format_id":fmt,
                             "video_id":vid,"age_days":age,"views":v.views,
                             "published_date":v.published_date,
                             "title":v.title,"duration_sec":v.duration_sec,
                             "channel_id":v.channel_id,
                             "channel_name":v.channel_name,
                             "source_level":"TITLE_MATCH_AND_PUBLIC_METADATA_ONLY",
                             "fully_watched":False})
        except Exception as e:
            errors.append({"format_id":fmt,"video_id":vid,
                           "error":type(e).__name__+":"+str(e)[:130]})
    # Extract a rival watchlist from actually retrieved video-channel pairs.
    # Never call these VERIFIED rivals based on titles and metadata alone.
    peers={}
    for v in admitted:
        if not v["channel_id"]:continue
        k=(v["niche_id"],v["format_id"],v["channel_id"])
        row=peers.setdefault(k,{"niche_id":v["niche_id"],"format_id":v["format_id"],
                                "channel_id":v["channel_id"],"channel_name":v["channel_name"],
                                "candidate_video_ids":[],"highest_observed_views":0,
                                "verified_same_format_competitor":False,
                                "needs_full_av_and_channel_origin_review":True})
        row["candidate_video_ids"].append(v["video_id"])
        row["highest_observed_views"]=max(row["highest_observed_views"],v["views"])
    status="APPROVED_DEEP_KEYWORD_RESEARCH_PARTIAL" if errors else "APPROVED_DEEP_KEYWORD_RESEARCH_RECORDED"
    ledger.finish(run_id,now.isoformat(),status,len(errors))
    report={
        "status":status,
        "observed_at":now.isoformat(),
        "approved_format_count":len(approvals),
        "source_search_query_count":len(research_queries),
        "full_metadata_checks":len(keys),
        "admitted":admitted,
        "candidate_competitor_channels":sorted(peers.values(),
                              key=lambda x:(-x["highest_observed_views"],x["channel_id"])),
        "quarantined":quarantined,
        "query_coverage":research_queries,
        "errors":errors,
        "daily_run_id":run_id,
        "never_cross_into_unapproved_niches":True,
        "leader_popular_is_not_complete_all_time_ranking":True,
        "full_video_playback_or_audio_analysis":False,
        "auto_production":False,
    }
    folder=root/"data/research/youtube_breakout/approved_deep_research"
    folder.mkdir(parents=True,exist_ok=True)
    stamp=now.strftime("%Y%m%dT%H%M%S%fZ")
    (folder/("keyword_scan_"+stamp+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
