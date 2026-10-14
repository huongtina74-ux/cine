"""Persistent, format-scoped competitor watch + evidence-based outlier signals.

Company Youtube remains the canonical DISCOVERY source. This service is an
approved-niche RESEARCH watchlist fed by its future bridge or public metadata.
No Shorts/live; no auto verification of competitors or video deep reviews.
"""
from __future__ import annotations
import datetime as dt
import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from .two_track_research_v201 import DualResearchStore
from .daily_youtube_breakout_v199 import CHANNEL_RE, VIDEO_RE, valid_utc
from .niche_competitor_guard_v200 import LANE_TO_NICHE

UTC=dt.timezone.utc

class NicheCompetitorWatch:
    def __init__(self,root:Path):
        self.root=Path(root)
        self.store=DualResearchStore(root/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
        self.path=self.store.path
        with self._db() as db:
            db.executescript("""
             CREATE TABLE IF NOT EXISTS niche_watch_channels(
               niche_id TEXT NOT NULL,format_id TEXT NOT NULL,
               channel_id TEXT NOT NULL, channel_name TEXT NOT NULL,
               first_seen TEXT NOT NULL,last_seen TEXT NOT NULL,
               origin TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'CANDIDATE_UNREVIEWED',
               PRIMARY KEY(niche_id,format_id,channel_id));
             CREATE TABLE IF NOT EXISTS niche_watch_videos(
               niche_id TEXT NOT NULL, format_id TEXT NOT NULL,
               video_id TEXT NOT NULL, channel_id TEXT NOT NULL,
               title TEXT NOT NULL, published_day TEXT NOT NULL,
               duration_sec INTEGER NOT NULL,first_seen TEXT NOT NULL,
               source TEXT NOT NULL,
               PRIMARY KEY(niche_id,format_id,video_id));
             CREATE TABLE IF NOT EXISTS niche_watch_snapshots(
               niche_id TEXT NOT NULL,format_id TEXT NOT NULL,
               video_id TEXT NOT NULL,observed_at TEXT NOT NULL,
               views INTEGER NOT NULL, observation_precision TEXT NOT NULL DEFAULT 'INSTANT',
               PRIMARY KEY(niche_id,format_id,video_id,observed_at));
             CREATE INDEX IF NOT EXISTS idx_niche_watch_channel
               ON niche_watch_videos(niche_id,format_id,channel_id);
            """)
    def _db(self):
        db=sqlite3.connect(str(self.path),timeout=30)
        db.execute("PRAGMA busy_timeout=30000")
        return db
    def add(self,*,niche_id:str,format_id:str,video_id:str,channel_id:str,
            channel_name:str,title:str,published_day:str,duration_sec:int,
            views:int,observed_at:str,origin:str,
            observation_precision:str="INSTANT")->bool:
        if LANE_TO_NICHE.get(format_id)!=niche_id or not self.store.approved(niche_id,format_id):
            return False
        if not VIDEO_RE.fullmatch(video_id) or not CHANNEL_RE.fullmatch(channel_id):
            return False
        if duration_sec<480 or views<0 or observation_precision not in ("DATE_ONLY","INSTANT"):return False
        try:
            published=dt.date.fromisoformat(published_day)
            observed=valid_utc(observed_at)
        except ValueError:return False
        if (observed.date()-published).days<0:return False
        with self._db() as db:
            db.execute("""INSERT INTO niche_watch_channels
                (niche_id,format_id,channel_id,channel_name,first_seen,last_seen,origin)
                VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(niche_id,format_id,channel_id) DO UPDATE SET
                channel_name=excluded.channel_name,last_seen=MAX(last_seen,excluded.last_seen)""",
                (niche_id,format_id,channel_id,channel_name,observed_at,observed_at,origin))
            db.execute("""INSERT INTO niche_watch_videos
                (niche_id,format_id,video_id,channel_id,title,published_day,duration_sec,first_seen,source)
                VALUES(?,?,?,?,?,?,?,?,?)
                ON CONFLICT(niche_id,format_id,video_id) DO UPDATE SET
                title=excluded.title,channel_id=excluded.channel_id,
                published_day=excluded.published_day,duration_sec=excluded.duration_sec""",
                (niche_id,format_id,video_id,channel_id,title,published_day,duration_sec,observed_at,origin))
            db.execute("""INSERT INTO niche_watch_snapshots
                (niche_id,format_id,video_id,observed_at,views,observation_precision)
                VALUES(?,?,?,?,?,?)
                ON CONFLICT(niche_id,format_id,video_id,observed_at) DO UPDATE SET
                views=MAX(views,excluded.views)""",
                (niche_id,format_id,video_id,observed_at,views,observation_precision))
        return True
    def seed_from_catalog(self,catalog:dict):
        accepted=0
        for scope in catalog.get("format_reports",[]):
            fmt=scope["format_id"]
            for rival in scope.get("rival_channel_candidates",[]):
                for v in rival.get("representative_videos",[]):
                    if self.add(niche_id="minecraft",format_id=fmt,video_id=v["video_id"],
                                channel_id=rival["channel_id"],channel_name=rival["channel_name"],
                                title=v["title"],published_day=v["published"],
                                duration_sec=v["duration_seconds"],views=v["views_observed"],
                                observed_at=v["observed_on"]+"T00:00:00+00:00",
                                origin="HISTORICAL_BOUNDED_VIDEO_METADATA",
                                observation_precision="DATE_ONLY"):
                        accepted+=1
        return accepted
    def seed_from_keyword_scan(self,scan:dict,*,observed_at:str):
        accepted=0
        # Keyword scan already format-gated; do not classify channel itself as confirmed.
        for row in scan.get("admitted",[]):
            date=row.get("published_date","")
            if len(date)!=8:continue
            try:posted=dt.datetime.strptime(date,"%Y%m%d").date().isoformat()
            except ValueError:continue
            if row.get("duration_sec") is None:continue
            if self.add(niche_id=row["niche_id"],format_id=row["format_id"],
                        video_id=row["video_id"],channel_id=row.get("channel_id") or "",
                        channel_name=row.get("channel_name",""),title=row.get("title",""),
                        published_day=posted,duration_sec=row["duration_sec"],
                        views=row["views"],observed_at=observed_at,
                        origin="APPROVED_KEYWORD_PUBLIC_METADATA"):
                accepted+=1
        return accepted
    def refresh_followed(self,*,client=None,as_of:dt.datetime|None=None,
                         max_channels:int=80,max_metadata:int=160)->dict:
        """Poll existing rival channels, including channels no longer newborn.

        Round-robin metadata budget: first a new/recent video per channel,
        then older popular videos for velocity snapshots. Missing/unavailable
        videos remain UNKNOWN; no failures are silently treated as no hits.
        """
        if not 1<=max_channels<=150 or not 1<=max_metadata<=400:
            raise ValueError("WATCH_BUDGET_OUT_OF_RANGE")
        from .daily_youtube_breakout_v199 import PublicYoutubeClient
        from .niche_competitor_guard_v200 import validate_video_niche
        client=client or PublicYoutubeClient()
        now=(as_of or dt.datetime.now(UTC)).astimezone(UTC)
        with self._db() as db:
            channels=db.execute("""SELECT w.niche_id,w.format_id,w.channel_id
                 FROM niche_watch_channels w
                 JOIN research_niche_approvals a ON
                     a.niche_id=w.niche_id AND a.format_id=w.format_id
                 WHERE a.state='APPROVED'
                 ORDER BY w.last_seen ASC,w.channel_id ASC LIMIT ?""",
                 (max_channels,)).fetchall()
            known=db.execute("""SELECT niche_id,format_id,channel_id,video_id
                      FROM niche_watch_videos""").fetchall()
            highest=db.execute("""SELECT v.niche_id,v.format_id,v.channel_id,v.video_id,
                     MAX(s.views) FROM niche_watch_videos v
                     JOIN niche_watch_snapshots s ON
                      s.niche_id=v.niche_id AND s.format_id=v.format_id
                      AND s.video_id=v.video_id
                     GROUP BY v.niche_id,v.format_id,v.channel_id,v.video_id
                     ORDER BY MAX(s.views) DESC""").fetchall()
        known_ids={(n,f,c,vid) for n,f,c,vid in known}
        popular=defaultdict(list)
        for n,f,c,vid,_ in highest:popular[(n,f,c)].append(vid)
        videos_by_channel={}
        errors=[]
        for n,f,cid in channels:
            ids=[]
            try:
                entries=client.channel_new_videos(cid,limit=8)
                ids.extend(e.get("id") for e in entries if isinstance(e.get("id"),str))
            except Exception as exc:
                errors.append({"channel_id":cid,"stage":"CHANNEL_RECENT_LIST",
                               "error":type(exc).__name__+":"+str(exc)[:130]})
            # Recheck earlier most successful videos, even after 15 days.
            ids.extend(popular.get((n,f,cid),[])[:3])
            videos_by_channel[(n,f,cid)]=list(dict.fromkeys(
                i for i in ids if isinstance(i,str) and VIDEO_RE.fullmatch(i)))[:8]
        checked=accepted=new=0
        max_depth=max((len(v) for v in videos_by_channel.values()),default=0)
        for rank in range(max_depth):
            for (n,f,cid),ids in videos_by_channel.items():
                if checked>=max_metadata:break
                if rank>=len(ids):continue
                vid=ids[rank]
                checked+=1
                try:
                    v=client.video(vid,lane=f)
                    if v.channel_id!=cid or v.is_live or v.duration_sec<480:continue
                    was_known=(n,f,cid,vid) in known_ids
                    if not was_known and validate_video_niche(v.title,f).status!="MATCHED_METADATA_FORMAT_CANDIDATE":
                        continue
                    if self.add(niche_id=n,format_id=f,video_id=vid,
                                channel_id=cid,channel_name=v.channel_name,title=v.title,
                                published_day=dt.datetime.strptime(v.published_date,"%Y%m%d").date().isoformat(),
                                duration_sec=v.duration_sec,views=v.views,
                                observed_at=now.isoformat(),origin="CHANNEL_FOLLOWUP_PUBLIC_VIDEO_METADATA"):
                        accepted+=1
                        if not was_known:
                            new+=1
                            known_ids.add((n,f,cid,vid))
                except Exception as exc:
                    errors.append({"channel_id":cid,"video_id":vid,"stage":"WATCH_METADATA",
                                   "error":type(exc).__name__+":"+str(exc)[:130]})
            if checked>=max_metadata:break
        result={"status":"COMPLETE_WITH_ERRORS" if errors else "BOUNDED_WATCH_REFRESH",
                "observed_at":now.isoformat(),"eligible_channels":len(channels),
                "channels_with_candidate_ids":sum(bool(v) for v in videos_by_channel.values()),
                "metadata_attempted":checked,"accepted_observations":accepted,
                "new_same_format_video_candidates":new,
                "errors":errors,"all_channels_and_catalogue_exhaustively_checked":False,
                "independent_av_certified":False,"paid_credit_calls":0}
        path=self.root/"data/research/youtube_breakout/approved_deep_research"/"watch_refresh_latest.json"
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
        return result

    def report(self,*,as_of:dt.datetime|None=None)->dict:
        now=(as_of or dt.datetime.now(UTC)).astimezone(UTC)
        with self._db() as db:
            channels=db.execute("""SELECT niche_id,format_id,channel_id,channel_name,
                first_seen,last_seen,origin FROM niche_watch_channels
                ORDER BY format_id,first_seen""").fetchall()
            rows=db.execute("""SELECT v.niche_id,v.format_id,v.video_id,v.channel_id,
                v.title,v.published_day,v.duration_sec,s.observed_at,s.views,
                s.observation_precision
                FROM niche_watch_videos v JOIN niche_watch_snapshots s
                ON v.niche_id=s.niche_id AND v.format_id=s.format_id
                AND v.video_id=s.video_id ORDER BY s.observed_at""").fetchall()
        series=defaultdict(list)
        latest={}
        for niche,fmt,vid,cid,title,day,dur,observed,views,precision in rows:
            key=(niche,fmt,vid)
            series[key].append((valid_utc(observed),views,precision))
            if key not in latest or valid_utc(observed)>valid_utc(latest[key]["observed_at"]):
                latest[key]=dict(niche_id=niche,format_id=fmt,video_id=vid,
                                 channel_id=cid,title=title,published=day,
                                 duration_sec=dur,observed_at=observed,views=views)
        channel_to_videos=defaultdict(list)
        for row in latest.values():
            key=(row["niche_id"],row["format_id"],row["channel_id"])
            channel_to_videos[key].append(row)
        out_channels=[]
        out_videos=[]
        for niche,fmt,cid,name,first,last,origin in channels:
            fact=self.store.channel(cid)
            born=fact.created_utc_day if fact and fact.has_verified_creation else None
            sub=fact.subscriber_count if fact and fact.subscriber_count and fact.subscriber_count>0 else None
            # Subscriber numbers can go stale. Keep measured age and source.
            sub_at=fact.subscribers_observed_at if fact else None
            if sub and (not sub_at or (now-valid_utc(sub_at)).days>30):sub=None
            candidate=channel_to_videos.get((niche,fmt,cid),[])
            first_dt=valid_utc(first)
            was_new=bool(born and 0<=(first_dt.date()-dt.date.fromisoformat(born)).days<=30)
            strict_wins=set()
            for v in candidate:
                age=(now.date()-dt.date.fromisoformat(v["published"])).days
                vi=(v["niche_id"],v["format_id"],v["video_id"])
                history=sorted(series[vi])
                # A million views must be observed while video age <=14 days,
                # not inferred from lifetime view when it is older.
                early_million=any(0<=(t.date()-dt.date.fromisoformat(v["published"])).days<=14
                                  and views>=1_000_000 for t,views,_ in history)
                if early_million:strict_wins.add(v["video_id"])
                prior=next(((t,views) for t,views,precision in reversed(history[:-1])
                           if precision=="INSTANT" and history[-1][2]=="INSTANT"
                           and (history[-1][0]-t).total_seconds()>=3600),None)
                vph=None
                if prior:
                    hours=(history[-1][0]-prior[0]).total_seconds()/3600
                    vph=round((history[-1][1]-prior[1])/hours,2)
                ratio=round(v["views"]/sub,2) if sub else None
                peers=[x["views"] for x in candidate if x["video_id"]!=v["video_id"]
                       and abs((now.date()-dt.date.fromisoformat(x["published"])).days-age)<=5]
                peers.sort()
                baseline=peers[len(peers)//2] if len(peers)>=3 else None
                outlier=round(v["views"]/baseline,2) if baseline and baseline>0 else None
                alerts=[]
                if early_million:alerts.append("MILLION_WITHIN_14D_PROVEN_BY_SNAPSHOT")
                if 0<=age<=30 and outlier is not None and outlier>=3:alerts.append("THREE_X_AGE_MATCHED_CHANNEL_BASELINE")
                if ratio is not None and ratio>=5:alerts.append("HIGH_VIEWS_PER_SUBSCRIBER")
                if 0<=age<=5 and vph is not None and vph>=2000:alerts.append("EARLY_5D_MEASURED_MOMENTUM")
                if 0<=age<=15 and v["views"]>=1_000_000:alerts.append("RECENT_MILLION_VIEW_VIDEO")
                out_videos.append({**v,"channel_name":name,"video_url":"https://www.youtube.com/watch?v="+v["video_id"],
                                   "channel_url":"https://www.youtube.com/channel/"+cid,
                                   "age_days":age,"views_per_subscriber":ratio,
                                   "age_matched_baseline":baseline,
                                   "baseline_sample_count":len(peers),
                                   "views_to_baseline_ratio":outlier,
                                   "measured_views_per_hour":vph,"early_million":early_million,
                                   "signals":alerts,"verified_full_av_review":False})
            out_channels.append(dict(niche_id=niche,format_id=fmt,
              channel_id=cid,channel_url="https://www.youtube.com/channel/"+cid,
              name=name,first_seen=first,last_seen=last,
              tracking_state=("NEWLY_ADDED" if first_dt.date()==now.date() else "ONGOING_TRACKING"),
              verified_created_day=born,was_new_at_discovery=was_new,
              subscribers=sub,subscriber_source=("YOUTUBE_PUBLIC_CHANNEL_FACTS" if sub else None),
              subscriber_observed_at=sub_at,
              qualifying_distinct_early_million_videos=len(strict_wins),
              strict_newcomer_winner=bool(was_new and len(strict_wins)>=2),
              channel_same_format_full_av_verified=False,
              video_count_in_watchlist=len(candidate)))
        out_videos.sort(key=lambda v:(-len(v["signals"]),-v["views"],v["video_id"]))
        signal_candidates=[{
            "video_id":v["video_id"],"format_id":v["format_id"],
            "signal_ids":v["signals"],
            "source_observed_at":v["observed_at"],
            "rule_class":"TEMPORARY_MARKET_SIGNAL_PENDING_FULL_VIDEO_AND_REPEATED_CHANNEL_EVIDENCE",
            "explainable_as_verified_long_term_rule":False
        } for v in out_videos if v["signals"] and v["age_days"]<=30]
        report={"schema":"cinefactory.niche_competitor_watch.v258",
                "observed_at":now.isoformat(),"scope":"RESEARCH_WATCHLIST_NOT_PRODUCTION",
                "tracked_channels":len(out_channels),"tracked_videos":len(out_videos),
                "candidate_channels":out_channels,"ranked_video_signals":out_videos,
                "temporary_learning_candidates":signal_candidates,
                "verified_long_term_success_rules":[],
                "long_term_rules_require_multiple_full_av_and_owned_results":True,
                "subscriber_missing_means_ratio_unknown":True,
                "date_only_snapshots_excluded_from_vph":True,
                "baseline_is_age_matched_sample_not_all_channel":True,
                "full_movie_source_review_is_separate_gate":True,
                "success_pattern_rules_are_hypotheses_until_multi-video_full_av_review":True}
        path=self.root/"data/research/youtube_breakout/approved_deep_research"/"persistent_watchlist_latest.json"
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        report["report_path"]=str(path)
        return report
