"""v256: assemble per-approved Minecraft rival catalogue from PUBLIC verified metadata snapshots.
Metadata-only. Does not claim full-video watch, verified IP rights, new channel age or live velocity.
"""
from __future__ import annotations
import datetime as dt
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path
from .two_track_research_v201 import DualResearchStore
from .niche_competitor_guard_v200 import validate_video_niche

SNAPSHOT_DATE=dt.date(2026,10,11)
DATASETS=("MINECRAFT_WIDE_RANK_V253.json","MINECRAFT_WIDE_RANK_SEARCH_V253.json")
EXCLUDE=re.compile(r"\b(?:roblox|obby|jenga|livestream|live\s+stream)\b",re.I)

def compile_approved_minecraft_catalog(root:Path,*,as_of:dt.date|None=None)->dict:
    root=Path(root)
    store=DualResearchStore(root/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
    approvals=[a for a in store.approvals()
               if a["state"]=="APPROVED" and a["format_id"] in {"minecraft_gameplay","minecraft_animation"}]
    today=as_of or dt.datetime.now(dt.timezone.utc).date()
    result={"schema":"cinefactory-approved-minecraft-catalog-v256",
            "catalogue_as_of":today.isoformat(),
            "snapshot_observed_on":SNAPSHOT_DATE.isoformat(),
            "snapshot_is_not_real_time_or_full_youtube":True,
            "all_same_niche_competitor_labels_provisional":True,
            "approved_formats":[a["format_id"] for a in approvals],
            "format_reports":[]}
    if not approvals:
        result["status"]="NO_APPROVED_MINECRAFT_FORMATS"
        return result
    seen={}
    present=[]
    for file in DATASETS:
        p=root/"docs"/file
        if not p.is_file():continue
        raw=json.loads(p.read_text(encoding="utf-8"))
        present.append(file)
        for item in raw.get("all",[]):
            if "date" not in item or not item.get("id") or not item.get("channel_id"):continue
            if not 480<=int(item.get("duration_sec") or 0)<=10800:continue
            if item.get("views") is None or item["views"]<0:continue
            age=(today-dt.date.fromisoformat(item["date"])).days
            if not 0<=age<=90:continue
            if EXCLUDE.search(str(item.get("title",""))):continue
            item=dict(item,age_at_original_observation=item.get("age_days"),
                      age_days=age,observed_on=SNAPSHOT_DATE.isoformat())
            if item["id"] not in seen or item["views"]>seen[item["id"]]["views"]:
                seen[item["id"]]=item
    # Continuously add fresh public metadata from the existing approved-keyword
    # daily research ledger. Historical v253 snapshots remain a baseline,
    # NOT a claim that they refresh themselves every day.
    ledger=store.path
    live_count=0
    if ledger.exists():
        with sqlite3.connect(str(ledger)) as db:
            tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if {"videos","observations"}.issubset(tables):
                rows=db.execute("""SELECT v.video_id,v.title,v.upload_date,v.duration_sec,
                        v.channel_id,v.channel_name,o.views,o.observed_at
                        FROM observations o JOIN videos v ON v.video_id=o.video_id
                        ORDER BY o.observed_at DESC""").fetchall()
                for vid,title,posted,duration,cid,name,views,at in rows:
                    try:
                        if not cid or not re.fullmatch(r"\d{8}",posted):continue
                        if not 480<=int(duration)<=10800 or int(views)<0:continue
                        published=dt.datetime.strptime(posted,"%Y%m%d").date()
                        observed=dt.datetime.fromisoformat(at.replace("Z","+00:00")).date()
                        age=(today-published).days
                        if not 0<=age<=90 or EXCLUDE.search(title):continue
                        item={"id":vid,"title":title,"date":published.isoformat(),
                              "channel":name,"channel_id":cid,"views":int(views),
                              "age_days":age,"duration_sec":int(duration),
                              "observed_on":observed.isoformat()}
                        prev=seen.get(vid)
                        if prev is None or (item["observed_on"],item["views"])>(
                           prev.get("observed_on",SNAPSHOT_DATE.isoformat()),prev["views"]):
                            seen[vid]=item
                            live_count+=1
                    except (ValueError,TypeError,AttributeError):continue
    result["source_snapshot_files"]=present
    result["fresh_or_updated_ledger_video_count"]=live_count
    result["historical_metadata_not_equal_to_current_velocity"]=True
    result["unique_metadata_videos_90d_before_format_gate"]=len(seen)
    if not seen:
        result["status"]="NO_HISTORICAL_SNAPSHOT_SAMPLES"
    else:
        result["status"]="PROVISIONAL_CATALOGUE_BUILT_FROM_BOUNDED_METADATA"
    for a in approvals:
        fmt=a["format_id"]
        valid=[]
        excluded=0
        for v in seen.values():
            check=validate_video_niche(v["title"],fmt)
            # The Maizen one-block Pokemon title omits the word Minecraft;
            # admit ONLY its specifically audited Chrome source. Never infer
            # all non-Minecraft titles from channel identity alone.
            special=(fmt=="minecraft_gameplay" and v["id"]=="yuM6o-8gz_4"
                     and v["channel_id"]=="UCJHBJ7F-nAIlMGolm0Hu4vg")
            if special:
                audit_path=root/".tools/minecraft_breakout_av_v252/yuM6o-8gz_4/audit.json"
                try:
                    audit=json.loads(audit_path.read_text(encoding="utf-8"))
                    special=(audit.get("source_id")==v["id"] and
                             audit.get("segments")==audit.get("complete")==31 and
                             not audit.get("seam_gaps") and audit.get("frames",0)>=100)
                except (OSError,ValueError,TypeError):
                    special=False
            if check.status=="MATCHED_METADATA_FORMAT_CANDIDATE" or special:
                valid.append(v)
            else:excluded+=1
        ranked=sorted(valid,key=lambda v:(-v["views"],v["id"]))
        last30=[v for v in ranked if v["age_days"]<=30]
        last14=[v for v in ranked if v["age_days"]<=14 and v["views"]>=1000000]
        bychannel=defaultdict(list)
        for v in valid:bychannel[v["channel_id"]].append(v)
        def brief(v):
            return {"video_id":v["id"],"title":v["title"],"channel":v["channel"],
                    "channel_id":v["channel_id"],"views_observed":v["views"],
                    "published":v["date"],"age_on_catalogue_day":v["age_days"],
                    "observed_on":v.get("observed_on",SNAPSHOT_DATE.isoformat()),
                    "duration_seconds":v["duration_sec"],
                    "url":"https://www.youtube.com/watch?v="+v["id"],
                    "view_growth_rate_observed":False,
                    "video_fully_watched":False,
                    "format_proven_by_full_video":False}
        competitors=[]
        for cid,items in bychannel.items():
            items=sorted(items,key=lambda x:-x["views"])
            meta=store.channel(cid)
            joined=(meta.created_utc_day if meta and meta.has_verified_creation else None)
            age=((today-dt.date.fromisoformat(joined)).days if joined else None)
            competitors.append({"channel_id":cid,"channel_name":items[0]["channel"],
                "candidate_video_count_in_bounded_sample":len(items),
                "sample_million_video_count":sum(v["views"]>=1000000 for v in items),
                "sample_max_views":items[0]["views"],
                "verified_channel_created_day":joined,
                "channel_born_0_30_days_verified":age is not None and 0<=age<=30,
                "channel_creation_research_pending":joined is None,
                "confirmed_competitor_by_full_audio_video":False,
                "representative_videos":[brief(v) for v in items[:4]]})
        competitors.sort(key=lambda x:(-x["sample_million_video_count"],-x["sample_max_views"],x["channel_id"]))
        queue=[]
        seen_queue=set()
        for source in (last14[:9],last30[:7],ranked[:7]):
            for row in source:
                if row["id"] in seen_queue:continue
                seen_queue.add(row["id"])
                queue.append({**brief(row),
                    "recommended_review":"FULL_ORIGINAL_MOVING_VIDEO_AND_AUDIO",
                    "review_state":"PENDING_INDEPENDENT_AV_REVIEW"})
        result["format_reports"].append({
           "format_id":fmt,"niche_id":"minecraft",
           "matching_video_count_90d":len(valid),
           "excluded_or_ambiguous_title_count":excluded,
           "matching_new_30d_count":len(last30),
           "breakouts_1m_within_14d_snapshot_count":len(last14),
           "top_90d":[brief(v) for v in ranked[:35]],
           "top_30d":[brief(v) for v in last30[:30]],
           "confirmed_current_snapshot_million_14d":[brief(v) for v in last14],
           "rival_channel_candidates":competitors,
           "full_video_review_queue":queue,
           "new_channel_two_1m_proven":False,
           "rights_and_originality_not_certified":True,
           "channel_age_requires_official_youtube_creation_date":True,
        })
    target=root/"data/research/youtube_breakout/approved_deep_research"/("minecraft_approved_catalogue_v256_"+SNAPSHOT_DATE.strftime("%Y%m%d")+".json")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    result["report_path"]=str(target)
    return result
