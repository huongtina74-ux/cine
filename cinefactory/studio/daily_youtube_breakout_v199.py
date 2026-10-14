"""CineFactory v1.6.39 — actual daily YouTube breakout scanner and evidence ledger.

This is a bounded, no-paid-API, independently executable CineFactory service.
Public YouTube search results are NON-EXHAUSTIVE. Full video streams may be HTTP
403, so nobody may promote metadata/low-res storyboard to actual watched video.
No search or source text is a command. Claude Code handoff is a local inert JSON
packet, not an automatic model call or production authorization.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sqlite3
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.parse import urlparse
from .niche_competitor_guard_v200 import (
    LANE_TO_NICHE, validate_video_niche,
)

WINDOW_DAYS=(2,3,4,5,6,7,14,30)
VIDEO_RE=re.compile(r"^[a-zA-Z0-9_-]{11}$")
CHANNEL_RE=re.compile(r"^UC[a-zA-Z0-9_-]{22}$")
ISO_DAY=re.compile(r"^\d{8}$")
UTC=dt.timezone.utc

# Distinct, cross-niche queries. These are discovery hypotheses, not a
# guarantee that YouTube search returns all new videos for these niches.
SEARCH_LANES={
    "minecraft_gameplay":"minecraft 100 days challenge",
    "minecraft_animation":"Minecraft animation funny story",
    "preschool_musical":"3D nursery rhymes original kids songs animation",
    "long_slide_game":"3D animal long slide obstacle race game",
    "ai_storytelling":"AI family drama full movie story",
    "asmr_sleep":"ASMR sleep long form relaxing",
    "roblox_animation":"Roblox R6 R15 animation full movie",
    "animal_animation":"3D animated animal adventure full movie",
    "gta_gameplay":"GTA V gameplay challenge",
    "cartoon_2d":"2D cartoon animation full episode",
    "audio_storytelling_seniors":"senior life stories audio long",
    "rain_sleep_white_noise":"rain sounds sleep 3 hours no talking",
    "fishing_silent":"silent fishing no talking fishing trip",
    "daily_english":"daily english listening conversation practice",
}
SOURCE_POLICY={
    "source_type":"YT_DLP_PUBLIC_YOUTUBE_SEARCH_AND_WATCH_METADATA",
    "discovery_is_exhaustive":False,
    "channel_age_confirmed":False,
    "actual_video_frame_decode_done":False,
    "video_soundtrack_listened":False,
    "watchtime_or_retention_known":False,
    "monetization_or_rpm_verified":False,
    "production_method_reliably_inferred":False,
    "model_training_with_competitor_content_permitted":False,
}
DEFAULT_DURATION_MIN=480 # >=8 minutes, long-form
DEFAULT_MODEL_CEILING=24

def utc_now()->dt.datetime:
    return dt.datetime.now(UTC)

def valid_utc(value:str)->dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z","+00:00")).astimezone(UTC)

def _digest(source:dict)->str:
    return hashlib.sha256(json.dumps(source,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()

def command_reader(argv:list[str],*,timeout:int=30)->str:
    if not argv or Path(argv[0]).name.lower() not in ("yt-dlp","yt-dlp.exe"):
        raise ValueError("ONLY_YT_DLP_ALLOWLIST_COMMANDS")
    # No shell, no cookies, no auth, no arbitrary user-defined subprocesses.
    p=subprocess.run(argv,capture_output=True,text=True,
                     timeout=timeout,check=False,encoding="utf-8",errors="replace")
    if p.returncode:
        raise RuntimeError("YTDLP_NO_PUBLIC_ACCESS:"+p.stderr[-220:].replace("\n"," "))
    return p.stdout

@dataclass(frozen=True)
class PublicVideo:
    video_id:str
    title:str
    published_date:str
    duration_sec:int
    views:int
    channel_id:str|None
    channel_name:str
    lane:str
    metadata_sha256:str
    is_live:bool=False

    @classmethod
    def parse(cls,body:dict,lane:str)->"PublicVideo":
        vid=body.get("id")
        if not isinstance(vid,str) or not VIDEO_RE.fullmatch(vid):
            raise ValueError("INVALID_VIDEO_ID")
        posted=body.get("upload_date")
        if not isinstance(posted,str) or not ISO_DAY.fullmatch(posted):
            raise ValueError("UPLOAD_DAY_NOT_PROVEN")
        # Do not silently convert missing/dynamic counts to zero.
        if not isinstance(body.get("view_count"),int) or body["view_count"]<0:
            raise ValueError("VIEWS_UNAVAILABLE")
        length=body.get("duration")
        if not isinstance(length,(int,float)) or length<=0:
            raise ValueError("DURATION_UNAVAILABLE")
        chid=body.get("channel_id")
        if chid is not None and (not isinstance(chid,str) or not CHANNEL_RE.fullmatch(chid)):
            chid=None
        if lane not in SEARCH_LANES:
            raise ValueError("UNAPPROVED_NICHE_LANE")
        evidence={
            "id":vid,"title":str(body.get("title") or "")[:300],
            "published_date":posted,"duration":length,
            "views":body["view_count"],"channel_id":chid,
            "channel_name":str(body.get("channel") or "")[:150],
            "was_live":body.get("was_live"),"live_status":body.get("live_status"),
        }
        live=body.get("was_live") is True or body.get("live_status") in {"is_live","was_live"}
        return cls(video_id=vid,title=evidence["title"],published_date=posted,
                   duration_sec=round(length),views=body["view_count"],
                   channel_id=chid,channel_name=evidence["channel_name"],
                   lane=lane,metadata_sha256=_digest(evidence),is_live=live)

class PublicYoutubeClient:
    def __init__(self,read:Callable[...,str]=command_reader):
        self.read=read

    def channel_new_videos(self,channel_id:str,*,limit:int=5)->list[dict]:
        if not CHANNEL_RE.fullmatch(channel_id) or limit<1 or limit>8:
            raise ValueError("INVALID_CHANNEL_OR_PAGE_BUDGET")
        url="https://www.youtube.com/channel/"+channel_id+"/videos"
        output=self.read([
            "yt-dlp","--flat-playlist","--dump-json",
            "--playlist-end",str(limit),"--no-warnings",
            "--socket-timeout","12","--retries","0",url],timeout=65)
        rows=[]
        for line in output.splitlines():
            try:r=json.loads(line)
            except json.JSONDecodeError:continue
            if isinstance(r,dict) and VIDEO_RE.fullmatch(str(r.get("id",""))):
                rows.append(r)
        return rows[:limit]

    def search(self,keyword:str,*,limit:int)->list[dict]:
        if not keyword or len(keyword)>140 or limit<1 or limit>20:
            raise ValueError("UNBOUNDED_QUERY")
        query=f"ytsearch{limit}:{keyword}"
        output=self.read([
            "yt-dlp","--flat-playlist","--dump-json","--no-playlist",
            "--no-warnings","--socket-timeout","12","--retries","0",
            query],timeout=65)
        entries=[]
        for line in output.splitlines():
            if not line.strip():continue
            try:entry=json.loads(line)
            except json.JSONDecodeError:continue
            if isinstance(entry,dict) and VIDEO_RE.fullmatch(str(entry.get("id",""))):
                entries.append(entry)
        return entries[:limit]

    def video(self,vid:str,*,lane:str)->PublicVideo:
        if not VIDEO_RE.fullmatch(vid):
            raise ValueError("INVALID_VIDEO_ID")
        raw=self.read([
            "yt-dlp","--skip-download","--dump-single-json","--no-playlist",
            "--no-warnings","--socket-timeout","12","--retries","0",
            "https://www.youtube.com/watch?v="+vid],timeout=38)
        obj=json.loads(raw)
        if obj.get("id")!=vid:
            raise ValueError("VIDEO_ID_SOURCE_MISMATCH")
        return PublicVideo.parse(obj,lane)

class BreakoutLedger:
    """Durable SQLite snapshots and sightings, no external database/API."""
    def __init__(self,location:Path):
        self.path=Path(location)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id INTEGER PRIMARY KEY,
                    started_at TEXT NOT NULL UNIQUE,
                    ended_at TEXT,
                    status TEXT NOT NULL,
                    searched_lanes TEXT NOT NULL,
                    error_count INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    upload_date TEXT NOT NULL,
                    duration_sec INTEGER NOT NULL,
                    channel_id TEXT,
                    channel_name TEXT NOT NULL,
                    metadata_sha256 TEXT NOT NULL,
                    was_live INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS observations (
                    run_id INTEGER NOT NULL,
                    video_id TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    views INTEGER NOT NULL,
                    lane TEXT NOT NULL,
                    PRIMARY KEY(run_id,video_id),
                    FOREIGN KEY(video_id) REFERENCES videos(video_id));
                CREATE TABLE IF NOT EXISTS discoveries (
                    run_id INTEGER NOT NULL,
                    lane TEXT NOT NULL,
                    video_id TEXT NOT NULL,
                    source_rank INTEGER NOT NULL,
                    PRIMARY KEY(run_id,lane,video_id));
                CREATE TABLE IF NOT EXISTS review_queue (
                    video_id TEXT PRIMARY KEY,
                    first_queued TEXT NOT NULL,
                    last_queued TEXT NOT NULL,
                    status TEXT NOT NULL,
                    access_level TEXT NOT NULL,
                    lane TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT PRIMARY KEY,
                    channel_name TEXT NOT NULL,
                    lane TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    discovery_video_id TEXT NOT NULL,
                    follow_reason TEXT NOT NULL,
                    channel_created_at TEXT,
                    channel_age_confirmed INTEGER NOT NULL DEFAULT 0);
                CREATE INDEX IF NOT EXISTS idx_obs_video ON observations(video_id,observed_at);
                """)
    def _db(self)->sqlite3.Connection:
        c=sqlite3.connect(str(self.path),timeout=20)
        c.execute("PRAGMA busy_timeout=20000")
        c.execute("PRAGMA foreign_keys=ON")
        return c

    def begin(self,at:str,lanes:list[str])->int:
        with self._db() as db:
            cur=db.execute("INSERT INTO runs(started_at,status,searched_lanes) VALUES(?,?,?)",
                           (at,"RUNNING",json.dumps(lanes)))
            return int(cur.lastrowid)

    def ingest(self,run_id:int,video:PublicVideo,observed_at:str,search_rank:int)->None:
        with self._db() as db:
            db.execute("""INSERT INTO videos(video_id,title,first_seen,upload_date,
                            duration_sec,channel_id,channel_name,metadata_sha256,was_live)
                            VALUES(?,?,?,?,?,?,?,?,?)
                            ON CONFLICT(video_id) DO UPDATE SET
                            title=excluded.title,upload_date=excluded.upload_date,
                            duration_sec=excluded.duration_sec,
                            channel_name=excluded.channel_name,
                            channel_id=COALESCE(excluded.channel_id,videos.channel_id),
                            metadata_sha256=excluded.metadata_sha256,
                            was_live=excluded.was_live""",
                       (video.video_id,video.title,observed_at,video.published_date,
                        video.duration_sec,video.channel_id,video.channel_name,
                        video.metadata_sha256,int(video.is_live)))
            db.execute("""INSERT OR REPLACE INTO observations(run_id,video_id,observed_at,views,lane)
                          VALUES(?,?,?,?,?)""",
                       (run_id,video.video_id,observed_at,video.views,video.lane))
            db.execute("""INSERT OR IGNORE INTO discoveries(run_id,lane,video_id,source_rank)
                          VALUES(?,?,?,?)""",(run_id,video.lane,video.video_id,search_rank))

    def older_sighting(self,video_id:str,at:str)->tuple[int,str]|None:
        with self._db() as db:
            row=db.execute("""SELECT views,observed_at FROM observations
                              WHERE video_id=? AND observed_at<? AND
                              observed_at<=datetime(?, '-1 hours')
                              ORDER BY observed_at DESC LIMIT 1""",(video_id,at,at)).fetchone()
            # SQLite date formats with T vs space are not lexicographically
            # comparable for datetime() — use native parsed timestamps below.
            if row:
                return int(row[0]),str(row[1])
            older=db.execute("""SELECT views,observed_at FROM observations
                                WHERE video_id=? AND observed_at<? ORDER BY observed_at DESC LIMIT 20""",
                             (video_id,at)).fetchall()
        now=valid_utc(at)
        for views,timestamp in older:
            if (now-valid_utc(timestamp)).total_seconds()>=3600:
                return int(views),str(timestamp)
        return None

    def follow_channel(self,video:PublicVideo,at:str,reason:str)->None:
        if video.channel_id is None or not CHANNEL_RE.fullmatch(video.channel_id):
            return
        with self._db() as db:
            db.execute("""INSERT INTO channels(channel_id,channel_name,lane,
                          first_seen,last_seen,discovery_video_id,follow_reason)
                          VALUES(?,?,?,?,?,?,?)
                          ON CONFLICT(channel_id) DO UPDATE SET
                          channel_name=excluded.channel_name,
                          last_seen=excluded.last_seen""",
                       (video.channel_id,video.channel_name,video.lane,
                        at,at,video.video_id,reason))

    def followed(self,limit:int=4)->list[dict]:
        with self._db() as db:
            rows=db.execute("""SELECT channel_id,channel_name,lane,
                               follow_reason,channel_created_at,
                               channel_age_confirmed
                               FROM channels ORDER BY last_seen DESC LIMIT ?""",
                            (min(6,max(0,limit)),)).fetchall()
        return [dict(channel_id=x[0],name=x[1],lane=x[2],
                     reason=x[3],created_at=x[4],
                     age_confirmed=bool(x[5])) for x in rows]

    def queue(self,video_id:str,lane:str,at:str,access_level:str)->None:
        with self._db() as db:
            db.execute("""INSERT INTO review_queue(video_id,first_queued,last_queued,
                            status,access_level,lane) VALUES(?,?,?,?,?,?)
                            ON CONFLICT(video_id) DO UPDATE SET
                            last_queued=excluded.last_queued,
                            lane=excluded.lane,
                            access_level=excluded.access_level""",
                       (video_id,at,at,"RESEARCH_CANDIDATE_NOT_PRODUCTION",access_level,lane))
    def finish(self,run_id:int,at:str,status:str,error_count:int)->None:
        with self._db() as db:
            db.execute("UPDATE runs SET ended_at=?,status=?,error_count=? WHERE run_id=?",
                       (at,status,error_count,run_id))
    def stats(self)->dict:
        with self._db() as db:
            return {
                "runs":db.execute("SELECT COUNT(*) FROM runs").fetchone()[0],
                "unique_videos":db.execute("SELECT COUNT(*) FROM videos").fetchone()[0],
                "observations":db.execute("SELECT COUNT(*) FROM observations").fetchone()[0],
                "review_queue":db.execute("SELECT COUNT(*) FROM review_queue").fetchone()[0],
                "followed_competitor_channels":db.execute("SELECT COUNT(*) FROM channels").fetchone()[0],
            }

def classify(video:PublicVideo,as_of:dt.datetime,older:tuple[int,str]|None)->dict|None:
    publish_day=dt.datetime.strptime(video.published_date,"%Y%m%d").replace(tzinfo=UTC)
    elapsed=(as_of-publish_day).total_seconds()/86400
    if elapsed<0 or elapsed>31 or video.duration_sec<DEFAULT_DURATION_MIN or video.is_live:
        return None
    days=max(.5,elapsed)  # rough average since midnight of posted date
    windows=[w for w in WINDOW_DAYS if elapsed<=w]
    average=round(video.views/days,2)
    observed_delta=None
    observed_vph=None
    if older:
        views,at=older
        hours=(as_of-valid_utc(at)).total_seconds()/3600
        if hours>=1 and video.views>=views:
            observed_delta=video.views-views
            observed_vph=round(observed_delta/hours,2)
    # Heuristic priority, not a YouTube ranking or probabilities.
    proximity=25 if elapsed<=7 else (12 if elapsed<=14 else 0)
    score=int(min(100,round(18*__import__("math").log10(max(1,average))+
                            proximity+(15 if observed_vph and observed_vph>=500 else 0))))
    # Channel age is NOT inferred from video upload date.
    return {
        "video_id":video.video_id,
        "url":"https://www.youtube.com/watch?v="+video.video_id,
        "title":video.title,"lane":video.lane,
        "channel":video.channel_name,"channel_id":video.channel_id,
        "channel_created_at":None,"new_channel_under_30_days":"UNKNOWN",
        "published_utc_day":video.published_date,"age_days_lower_bound":round(elapsed,3),
        "views":video.views,"duration_sec":video.duration_sec,
        "average_views_per_day_since_posting_APPROX":average,
        "observed_views_delta":observed_delta,
        "observed_views_per_hour_from_snapshots":observed_vph,
        "window_membership_days":windows,
        "heuristic_research_priority":score,
        "metadata_sha256":video.metadata_sha256,
        "breakout_verified":bool(observed_delta is not None and observed_delta>=100000),
        "real_growth_curve_verified":observed_vph is not None,
        "exact_publish_time_known":False,
        "source_level":"PUBLIC_YOUTUBE_VIDEO_METADATA_ONLY",
        "actual_video_watched":False,
        "audio_transcript_verified":False,
        "future_claude_research_required":True,
        "production_ready":False,
    }

def scan_daily(
    *,root:Path,client:PublicYoutubeClient|None=None,
    lanes:list[str]|None=None,now:dt.datetime|None=None,
    search_per_lane:int=8,max_metadata:int=22,
    daily_review_cap:int=8
)->dict:
    root=Path(root).resolve()
    now=now or utc_now()
    if now.tzinfo is None:raise ValueError("UTC_AWARE_TIME_REQUIRED")
    now=now.astimezone(UTC)
    lanes=list(SEARCH_LANES) if lanes is None else lanes
    if not lanes or len(lanes)>len(SEARCH_LANES) or len(lanes)!=len(set(lanes)) or any(x not in SEARCH_LANES for x in lanes):
        raise ValueError("INVALID_LANES")
    if search_per_lane<1 or search_per_lane>15 or max_metadata<1 or max_metadata>35:
        raise ValueError("NETWORK_RESEARCH_BUDGET_EXCEEDED")
    if daily_review_cap<1 or daily_review_cap>12:
        raise ValueError("REVIEW_BUDGET_EXCEEDED")
    base=root/"data"/"research"/"youtube_breakout"
    base.mkdir(parents=True,exist_ok=True)
    ledger=BreakoutLedger(base/"cinefactory_breakout.sqlite3")
    client=client or PublicYoutubeClient()
    started=now.isoformat()
    # Non-overlapping unique run timestamps, never reset historical DB.
    runid=ledger.begin(started,lanes)
    candidates={}
    queries={}
    errors=[]
    for lane in lanes:
        try:
            results=client.search(SEARCH_LANES[lane],limit=search_per_lane)
            queries[lane]={"query":SEARCH_LANES[lane],"returned":len(results)}
            for rank,row in enumerate(results,1):
                vid=row.get("id")
                if isinstance(vid,str) and VIDEO_RE.fullmatch(vid):
                    candidates.setdefault(vid,{"lane":lane,"rank":rank,
                                               "channel_hint":row.get("channel"),
                                               "title_hint":row.get("title")})
        except Exception as e:
            errors.append({"lane":lane,"error":type(e).__name__+":"+str(e)[:170]})
    accepted=[]
    quarantine=[]
    attempts=0
    # Prioritize novelty/estimated metadata counts, do not claim exhaustive:
    # rotate one candidate per lane before consuming another same lane.
    by_lane={lane:[(k,v) for k,v in candidates.items() if v["lane"]==lane]
             for lane in lanes}
    ranked=[]
    for i in range(search_per_lane):
        for lane in lanes:
            if i<len(by_lane[lane]):
                ranked.append(by_lane[lane][i])
    # Existing verified competitors are rescanned every day as an additional
    # source of early uploads, not as an age/virality guarantee. Channel
    # pages are public, exact UC IDs from verified source metadata only.
    watched=[]
    for tracked in ledger.followed(limit=3):
        if len(watched)>=3:break
        try:
            entries=client.channel_new_videos(tracked["channel_id"],limit=4)
            watched.append({"channel_id":tracked["channel_id"],
                            "video_entries":len(entries),"error":None})
            for i,row in enumerate(entries,1):
                vid=row.get("id")
                if isinstance(vid,str) and VIDEO_RE.fullmatch(vid):
                    if vid not in candidates:
                        source={"lane":tracked["lane"],
                                "rank":i,"channel_hint":tracked["name"],
                                "title_hint":row.get("title")}
                        candidates[vid]=source
                        # Prioritize the newest followed-channel uploads;
                        # preserve remaining metadata API total hard cap.
                        ranked.insert(i-1,(vid,source))
        except Exception as e:
            watched.append({"channel_id":tracked["channel_id"],
                            "video_entries":0,
                            "error":type(e).__name__+":"+str(e)[:140]})
    for vid,source in ranked:
        if attempts>=max_metadata:break
        attempts+=1
        try:
            video=client.video(vid,lane=source["lane"])
            if video.duration_sec<DEFAULT_DURATION_MIN or video.is_live:continue
            old=ledger.older_sighting(video.video_id,started)
            item=classify(video,now,old)
            if not item:continue
            niche_gate=validate_video_niche(video.title,source["lane"])
            if niche_gate.status!="MATCHED_METADATA_FORMAT_CANDIDATE":
                quarantine.append({
                    "video_id":video.video_id,"title":video.title,
                    "origin_search_lane":source["lane"],
                    "status":niche_gate.status,
                    "reason":niche_gate.reason,
                    "source_metadata_sha256":video.metadata_sha256,
                    "NOT_A_VERIFIED_SAME_NICHE_COMPETITOR":True,
                })
                continue
            item["niche_id"]=niche_gate.niche_id
            item["format_id"]=niche_gate.format_id
            item["format_admission"]="TITLE_ONLY_CANDIDATE_NOT_VISUAL_VERIFIED"
            item["competitor_same_niche_confirmed"]=False
            ledger.ingest(runid,video,started,source["rank"])
            # Follow genuinely high-view recent channels for next day's
            # new-upload scan. DOES NOT assert channel creation age.
            if item["age_days_lower_bound"]<=14 and (
                item["views"]>=100000 or item["average_views_per_day_since_posting_APPROX"]>=15000
            ):
                ledger.follow_channel(video,started,"RECENT_HIGH_TRAFFIC_RESEARCH_CANDIDATE")
            accepted.append(item)
        except Exception as e:
            errors.append({"video_id":vid,"error":type(e).__name__+":"+str(e)[:170]})
    accepted.sort(key=lambda x:(-x["heuristic_research_priority"],-x["views"],x["video_id"]))
    for video in accepted[:daily_review_cap]:
        ledger.queue(video["video_id"],video["lane"],started,"PUBLIC_METADATA_ONLY")
    status=("RESEARCH_PARTIAL" if errors else "DISCOVERY_AND_METADATA_VERIFIED")
    ledger.finish(runid,utc_now().isoformat(),status,len(errors))
    stamp=now.strftime("%Y%m%dT%H%M%S")+"_run"+str(runid)
    report={
        "schema":"cinefactory-breakout-v1.6.39",
        "status":status,"run_id":runid,"started_utc":started,
        "windows_days":list(WINDOW_DAYS),
        "queries":queries,"followed_channels_checked":watched,
        "results_count":len(accepted),
        "cross_niche_quarantine":quarantine,
        "cross_niche_quarantined_count":len(quarantine),
        "niche_format_gate_enabled":True,
        "search_result_candidates":len(candidates),"full_metadata_attempted":attempts,
        "verified_candidates":accepted,
        "errors":errors,
        "persistent_ledger":str(ledger.path),
        "ledger_stats":ledger.stats(),
        "claude_handoff_exists":False,
        "youtube_api_key_required":False,
        "complete_all_youtube_coverage":False,
        "source_scope_limits":SOURCE_POLICY,
        "no_paid_api":True,
        "production_or_upload_permission_granted":False,
    }
    output=base/"runs"/(stamp+".json")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    report["run_report_path"]=str(output.resolve())
    return report

class DailyYouTubeBreakoutResearchService:
    """Lazy company R&D adapter; does no network activity on construction."""
    def __init__(self,root:Path):
        self.root=Path(root).resolve()

    @property
    def db_path(self)->Path:
        return self.root/"data/research/youtube_breakout/cinefactory_breakout.sqlite3"

    def latest_saved_report(self)->dict|None:
        files=sorted((self.root/"data/research/youtube_breakout/runs").glob("*.json"))
        if not files:return None
        return json.loads(files[-1].read_text(encoding="utf-8"))

    def run_explicit(self,*,approve_public_youtube_access:bool=False,
                     lanes:list[str]|None=None,
                     metadata_budget:int=20)->dict:
        if not approve_public_youtube_access:
            raise PermissionError("CINEFACTORY_LIVE_YOUTUBE_RESEARCH_MUST_BE_AUTHORIZED")
        return scan_daily(root=self.root,lanes=lanes,max_metadata=metadata_budget)

    def two_branch_owner_report(self)->dict:
        """Runs LOCAL EVALUATION ONLY, no YouTube/Claude calls."""
        from .two_track_research_v201 import generate_two_track_daily
        return generate_two_track_daily(self.root)

    def niche_research_approvals(self)->list[dict]:
        from .two_track_research_v201 import DualResearchStore
        return DualResearchStore(
            self.root/"data/research/youtube_breakout/cinefactory_breakout.sqlite3"
        ).approvals()
