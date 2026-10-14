"""v1.6.41: CineFactory two independent research branches.

Branch 1: global opportunity watch. Requires a *verified* channel creation day,
two distinct >=1,000,000-view long-form video IDs, proven sustainable demand
from older-format peers, and a distinguishable niche/format. Income/potential
is modeled as scenarios, never certified or guaranteed.

Branch 2: niche-private watch, only AFTER explicit user approval recorded in the
owned studio SQLite registry. Three evidence cohorts:
(A) leaders and recent overperformers, (B) born<=30d challengers,
(C) million-view videos published 0-15 days ago.

This code is a strict evidence evaluator. It does not claim to browse the full
video, discover all YouTube videos, call Claude, or publish. The prior bounded
public search owns raw collection; this runs only on verified stored evidence.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import math
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from .niche_competitor_guard_v200 import LANE_TO_NICHE
from .daily_youtube_breakout_v199 import VIDEO_RE,CHANNEL_RE,UTC,valid_utc

DAY=re.compile(r"^\d{4}-\d\d-\d\d$")
MILLION=1_000_000
CURRENT_DEMAND_FLOOR=100_000
DEFAULT_LONG_SECONDS=480
REPORT_VERSION="cinefactory-dual-track-v1.6.41"
NEW_PROPOSAL_FORMAT=re.compile(r"^proposal_[0-9a-f]{16}$")

def _day(s:str)->dt.date:
    if not isinstance(s,str) or not DAY.fullmatch(s):
        raise ValueError("EXACT_CHANNEL_CREATION_DAY_REQUIRED")
    return dt.date.fromisoformat(s)

def _age(day:str,now:dt.date)->int:
    return (now-_day(day)).days

def revenue_scenarios(view_counts_per_month:list[int],rpm_scenarios:list[float]|None=None)->list[dict]:
    """Not revenue certification; RPM is unknown and content monetization varies."""
    rpms=rpm_scenarios if rpm_scenarios is not None else [0.5,2.0,5.0,10.0]
    if any(not isinstance(v,int) or v<0 for v in view_counts_per_month):
        raise ValueError("INVALID_VIEW_SCENARIO")
    if any(not isinstance(x,(int,float)) or x<0 for x in rpms):
        raise ValueError("INVALID_RPM_SCENARIO")
    return [
        {"hypothetical_monthly_views":v,"hypothetical_rpm_usd":rpm,
         "gross_ad_revenue_usd_before_costs_ROUGH":round(v/1000*rpm,2),
         "is_observed_revenue":False,"is_earnings_prediction":False}
        for v in view_counts_per_month for rpm in rpms
    ]

@dataclass(frozen=True)
class ChannelEvidence:
    channel_id:str
    channel_name:str
    created_utc_day:str|None
    creation_provenance:str|None
    subscriber_count:int|None=None
    subscribers_observed_at:str|None=None

    @property
    def has_verified_creation(self)->bool:
        return self.created_utc_day is not None and self.creation_provenance in {
            "YOUTUBE_DATA_API_CHANNELS_SNIPPET_PUBLISHED_AT",
            "YOUTUBE_OFFICIAL_CHANNEL_JOIN_DATE_REVIEWED",
        }

    def new_channel_eligible(self,now:dt.date)->bool:
        return self.has_verified_creation and 0<=_age(self.created_utc_day,now)<=30

    def mature_channel_eligible(self,now:dt.date)->bool:
        return self.has_verified_creation and _age(self.created_utc_day,now)>=365

@dataclass(frozen=True)
class VideoEvidence:
    video_id:str
    channel_id:str
    format_id:str
    title:str
    published_utc_day:str
    public_views:int
    duration_sec:int
    observed_at:str
    source: str="PUBLIC_YOUTUBE_WATCH_METADATA"
    media_access:str="METADATA_ONLY"

    def __post_init__(self):
        if not VIDEO_RE.fullmatch(self.video_id):raise ValueError("INVALID_VIDEO_ID")
        if not CHANNEL_RE.fullmatch(self.channel_id):raise ValueError("INVALID_CHANNEL_ID")
        if self.format_id not in LANE_TO_NICHE and not NEW_PROPOSAL_FORMAT.fullmatch(self.format_id):
            raise ValueError("UNKNOWN_FORMAT")
        if self.public_views<0 or self.duration_sec<0:raise ValueError("INVALID_METRICS")
        _day(self.published_utc_day)
        valid_utc(self.observed_at)

    def age_days(self,now:dt.date)->int:
        return (now-_day(self.published_utc_day)).days

class DualResearchStore:
    """Additional evidence tables layered on top of v199's own SQLite DB."""
    def __init__(self,path:Path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self._db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS research_niche_approvals(
                    niche_id TEXT NOT NULL,
                    format_id TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN('APPROVED','PAUSED')),
                    approved_by TEXT NOT NULL,
                    approval_note TEXT NOT NULL,
                    approved_at TEXT NOT NULL,
                    PRIMARY KEY(niche_id,format_id));
                CREATE TABLE IF NOT EXISTS research_channel_facts(
                    channel_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    created_utc_day TEXT,
                    creation_provenance TEXT,
                    subscriber_count INTEGER,
                    subs_observed_at TEXT,
                    updated_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS research_format_proposals(
                    proposal_id TEXT PRIMARY KEY,
                    proposal_label TEXT NOT NULL,
                    format_fingerprint TEXT NOT NULL,
                    parent_niche TEXT NOT NULL,
                    differentiation TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS research_peer_links(
                    niche_id TEXT NOT NULL,
                    format_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    cohort TEXT NOT NULL CHECK(cohort IN('LEADER','NEW_CHALLENGER','MATURE_DEMAND')),
                    evidence_note TEXT NOT NULL,
                    linked_at TEXT NOT NULL,
                    PRIMARY KEY(niche_id,format_id,channel_id,cohort));
                CREATE TABLE IF NOT EXISTS research_format_novelty_reviews(
                    proposal_id TEXT PRIMARY KEY,
                    source_ids_json TEXT NOT NULL,
                    reviewed_by TEXT NOT NULL,
                    reviewed_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS research_format_video_evidence(
                    video_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    format_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    published_utc_day TEXT NOT NULL,
                    views INTEGER NOT NULL,
                    duration_sec INTEGER NOT NULL,
                    observed_at TEXT NOT NULL,
                    source TEXT NOT NULL,
                    media_access TEXT NOT NULL,
                    format_review_provenance TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS research_episodes(
                    run_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL CHECK(kind IN('GLOBAL','APPROVED_NICHE')),
                    niche_id TEXT,
                    at TEXT NOT NULL,
                    result_json TEXT NOT NULL);
            """)
            # Legacy installations used niche_id as the sole primary key.
            # A niche may have multiple separately approved formats, so migrate
            # that constraint transactionally without losing approval history.
            primary_keys=[r[1] for r in sorted(
                (r for r in db.execute("PRAGMA table_info(research_niche_approvals)")
                 if r[5]),key=lambda r:r[5])]
            if primary_keys==["niche_id"]:
                db.execute("BEGIN IMMEDIATE")
                db.execute("""CREATE TABLE research_niche_approvals_v255(
                    niche_id TEXT NOT NULL,
                    format_id TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN('APPROVED','PAUSED')),
                    approved_by TEXT NOT NULL,
                    approval_note TEXT NOT NULL,
                    approved_at TEXT NOT NULL,
                    PRIMARY KEY(niche_id,format_id))""")
                db.execute("""INSERT INTO research_niche_approvals_v255
                    (niche_id,format_id,state,approved_by,approval_note,approved_at)
                    SELECT niche_id,format_id,state,approved_by,approval_note,approved_at
                    FROM research_niche_approvals""")
                db.execute("DROP TABLE research_niche_approvals")
                db.execute("ALTER TABLE research_niche_approvals_v255 RENAME TO research_niche_approvals")
            elif primary_keys!=["niche_id","format_id"]:
                raise RuntimeError("UNRECOGNIZED_RESEARCH_APPROVAL_SCHEMA")
    def _db(self):
        db=sqlite3.connect(str(self.path),timeout=20)
        db.execute("PRAGMA busy_timeout=20000")
        return db

    def approvals(self)->list[dict]:
        with self._db() as db:
            rows=db.execute("SELECT niche_id,format_id,state,approved_by,approved_at FROM research_niche_approvals ORDER BY niche_id").fetchall()
        return [{"niche_id":x[0],"format_id":x[1],"state":x[2],
                 "approved_by":x[3],"approved_at":x[4]} for x in rows]

    def approve(self,niche_id:str,format_id:str,*,actor:str,note:str,at:str):
        if niche_id not in LANE_TO_NICHE.values() or LANE_TO_NICHE.get(format_id)!=niche_id:
            raise ValueError("NICHE_FORMAT_NOT_REGISTERED")
        if actor!="USER_EXPLICIT_APPROVAL" or not note.strip():
            raise PermissionError("NOBODY_CAN_AUTO_APPROVE_NICHE")
        valid_utc(at)
        with self._db() as db:
            existing=db.execute("SELECT state FROM research_niche_approvals WHERE niche_id=? AND format_id=?",(niche_id,format_id)).fetchone()
            if existing and existing[0]=="APPROVED":
                raise ValueError("ALREADY_APPROVED_REQUIRES_EXPLICIT_CHANGE")
            db.execute("""INSERT INTO research_niche_approvals(niche_id,format_id,state,approved_by,approval_note,approved_at)
                          VALUES(?,?,'APPROVED',?,?,?)
                          ON CONFLICT(niche_id,format_id) DO UPDATE SET
                          format_id=excluded.format_id,state=excluded.state,
                          approved_by=excluded.approved_by,approval_note=excluded.approval_note,
                          approved_at=excluded.approved_at""",
                       (niche_id,format_id,actor,note,at))
    def pause(self,niche_id:str,format_id:str,*,actor:str):
        if actor!="USER_EXPLICIT_APPROVAL":raise PermissionError("USER_APPROVAL_REQUIRED")
        with self._db() as db:
            row=db.execute("SELECT state FROM research_niche_approvals WHERE niche_id=? AND format_id=?",(niche_id,format_id)).fetchone()
            if not row:raise ValueError("FORMAT_NOT_APPROVED")
            db.execute("UPDATE research_niche_approvals SET state='PAUSED' WHERE niche_id=? AND format_id=?",
                       (niche_id,format_id))
    def approved(self,niche_id:str,format_id:str)->bool:
        with self._db() as db:
            row=db.execute("SELECT state FROM research_niche_approvals WHERE niche_id=? AND format_id=?",
                           (niche_id,format_id)).fetchone()
        return bool(row and row[0]=="APPROVED")

    def channel(self,channel_id:str)->ChannelEvidence|None:
        if not CHANNEL_RE.fullmatch(channel_id):raise ValueError("INVALID_CHANNEL_ID")
        with self._db() as db:
            row=db.execute("""SELECT channel_id,display_name,created_utc_day,creation_provenance,
                              subscriber_count,subs_observed_at FROM research_channel_facts
                              WHERE channel_id=?""",(channel_id,)).fetchone()
        return ChannelEvidence(*row) if row else None

    def save_channel(self,ch:ChannelEvidence,at:str):
        if not CHANNEL_RE.fullmatch(ch.channel_id):raise ValueError("INVALID_CHANNEL_ID")
        if ch.created_utc_day is not None:_day(ch.created_utc_day)
        if ch.subscriber_count is not None and ch.subscriber_count<0:raise ValueError("INVALID_SUBSCRIBERS")
        valid_utc(at)
        with self._db() as db:
            db.execute("""INSERT INTO research_channel_facts(channel_id,display_name,
                       created_utc_day,creation_provenance,subscriber_count,subs_observed_at,updated_at)
                       VALUES(?,?,?,?,?,?,?)
                       ON CONFLICT(channel_id) DO UPDATE SET
                       display_name=excluded.display_name,
                       created_utc_day=COALESCE(excluded.created_utc_day,research_channel_facts.created_utc_day),
                       creation_provenance=COALESCE(excluded.creation_provenance,research_channel_facts.creation_provenance),
                       subscriber_count=COALESCE(excluded.subscriber_count,research_channel_facts.subscriber_count),
                       subs_observed_at=COALESCE(excluded.subs_observed_at,research_channel_facts.subs_observed_at),
                       updated_at=excluded.updated_at""",
                       (ch.channel_id,ch.channel_name,ch.created_utc_day,ch.creation_provenance,
                        ch.subscriber_count,ch.subscribers_observed_at,at))

    def propose_format(self,label:str,fingerprint:str,parent_niche:str,differentiation:str,at:str)->str:
        if not label.strip() or not fingerprint.strip() or not differentiation.strip():
            raise ValueError("ORIGINAL_FORMAT_FINGERPRINT_AND_DIFFERENTIATION_REQUIRED")
        if parent_niche not in LANE_TO_NICHE.values() and parent_niche!="NEW_CATEGORY":
            raise ValueError("INVALID_PARENT_NICHE")
        key=re.sub(r"\s+"," ",fingerprint.strip().casefold())
        pid="proposal_"+hashlib.sha256(key.encode()).hexdigest()[:16]
        with self._db() as db:
            if db.execute("SELECT proposal_id FROM research_format_proposals WHERE format_fingerprint=?",(key,)).fetchone():
                raise ValueError("DUPLICATE_FORMAT_FINGERPRINT")
            db.execute("""INSERT INTO research_format_proposals VALUES(?,?,?,?,?,?,?)""",
                       (pid,label,key,parent_niche,differentiation,"HYPOTHESIS_UNVERIFIED",at))
        return pid
    def review_format_novelty(self,proposal_id:str,*,source_ids:list[str],
                              actor:str,at:str):
        if actor!="INDEPENDENT_HUMAN_RESEARCH_REVIEW":
            raise PermissionError("NOVEL_FORMAT_REQUIRES_INDEPENDENT_REVIEW")
        if len(set(source_ids))<2 or any(not x.strip() or len(x)>250 for x in source_ids):
            raise ValueError("TWO_INDEPENDENT_SOURCE_REFERENCES_REQUIRED")
        valid_utc(at)
        with self._db() as db:
            exists=db.execute("SELECT proposal_id FROM research_format_proposals WHERE proposal_id=?",
                              (proposal_id,)).fetchone()
            if not exists:raise ValueError("NO_FORMAT_PROPOSAL")
            db.execute("""INSERT INTO research_format_novelty_reviews VALUES(?,?,?,?)
                          ON CONFLICT(proposal_id) DO UPDATE SET
                          source_ids_json=excluded.source_ids_json,
                          reviewed_by=excluded.reviewed_by,reviewed_at=excluded.reviewed_at""",
                       (proposal_id,json.dumps(sorted(set(source_ids))),actor,at))
            db.execute("UPDATE research_format_proposals SET state='DISTINCT_FORMAT_REVIEWED' WHERE proposal_id=?",
                       (proposal_id,))

    def proposals(self)->list[dict]:
        with self._db() as db:
            rows=db.execute("SELECT proposal_id,proposal_label,format_fingerprint,parent_niche,differentiation,state FROM research_format_proposals ORDER BY created_at").fetchall()
        return [dict(zip(("proposal_id","label","fingerprint","parent_niche","difference","state"),r)) for r in rows]

    def store_reviewed_format_video(self,video:VideoEvidence,*,format_review_provenance:str):
        # A new format cannot be inferred from titles alone. Admission into
        # an unlisted proposal requires real media review evidence.
        if video.format_id not in LANE_TO_NICHE:
            with self._db() as db:
                exists=db.execute("SELECT proposal_id FROM research_format_proposals WHERE proposal_id=?",
                                  (video.format_id,)).fetchone()
            if not exists:
                raise ValueError("NO_REGISTERED_FORMAT_PROPOSAL")
            if not format_review_provenance.startswith("VISUAL_REVIEW:") or len(format_review_provenance)<25:
                raise PermissionError("PROPOSAL_FORMAT_REQUIRES_TRACEABLE_MEDIA_REVIEW")
        if not format_review_provenance:
            raise ValueError("SOURCE_PROVENANCE_REQUIRED")
        with self._db() as db:
            db.execute("""INSERT INTO research_format_video_evidence
                       VALUES(?,?,?,?,?,?,?,?,?,?,?)
                       ON CONFLICT(video_id) DO UPDATE SET
                       views=excluded.views,observed_at=excluded.observed_at,
                       media_access=excluded.media_access""",
                       (video.video_id,video.channel_id,video.format_id,
                        video.title,video.published_utc_day,video.public_views,
                        video.duration_sec,video.observed_at,video.source,
                        video.media_access,format_review_provenance))

    def reviewed_videos(self)->list[VideoEvidence]:
        with self._db() as db:
            rows=db.execute("""SELECT video_id,channel_id,format_id,title,
                               published_utc_day,views,duration_sec,observed_at,
                               source,media_access FROM research_format_video_evidence""").fetchall()
        return [VideoEvidence(*row) for row in rows]

    def link_peer(self,niche_id:str,format_id:str,channel_id:str,cohort:str,note:str,at:str):
        if not self.approved(niche_id,format_id):
            raise PermissionError("NICHE_MUST_BE_APPROVED_BEFORE_LINKED_RESEARCH")
        if not CHANNEL_RE.fullmatch(channel_id) or cohort not in {"LEADER","NEW_CHALLENGER","MATURE_DEMAND"} or not note.strip():
            raise ValueError("INVALID_PEER_EVIDENCE")
        with self._db() as db:
            db.execute("INSERT OR REPLACE INTO research_peer_links VALUES(?,?,?,?,?,?)",
                       (niche_id,format_id,channel_id,cohort,note,at))
    def peer_links(self,niche_id:str,format_id:str)->list[dict]:
        if not self.approved(niche_id,format_id):return []
        with self._db() as db:
            rows=db.execute("""SELECT channel_id,cohort,evidence_note FROM research_peer_links
                               WHERE niche_id=? AND format_id=?""",(niche_id,format_id)).fetchall()
        return [{"channel_id":r[0],"cohort":r[1],"note":r[2]} for r in rows]

def verified_opportunity(*,fingerprint:str,format_id:str,
                         channels:dict[str,ChannelEvidence],
                         videos:list[VideoEvidence],
                         mature_peer_channel_ids:set[str],
                         niche_existing_fingerprints:set[str],
                         as_of:dt.date,
                         format_novelty_independently_reviewed:bool=False,
                         broader_parent_format_ids:set[str]|None=None,
                         parent_demand_relationship_reviewed:bool=False)->dict:
    if format_id not in LANE_TO_NICHE and not NEW_PROPOSAL_FORMAT.fullmatch(format_id):
        raise ValueError("UNKNOWN_FORMAT")
    norm=lambda x:" ".join(x.casefold().split())
    novelty=bool(fingerprint.strip()) and norm(fingerprint) not in {norm(x) for x in niche_existing_fingerprints}
    matching=[v for v in videos if v.format_id==format_id and
              0<=v.age_days(as_of)<=30 and v.duration_sec>=DEFAULT_LONG_SECONDS]
    new_winners=[]
    for cid,channel in channels.items():
        if not channel.new_channel_eligible(as_of):continue
        hits={v.video_id for v in matching if v.channel_id==cid
              and v.public_views>=MILLION and
              _day(v.published_utc_day)>=_day(channel.created_utc_day)}
        if len(hits)>=2:
            new_winners.append({"channel_id":cid,"channel_name":channel.channel_name,
                                "created_utc_day":channel.created_utc_day,
                                "million_video_ids":sorted(hits),"million_video_count":len(hits)})
    mature_demand=[]
    for cid in sorted(mature_peer_channel_ids):
        ch=channels.get(cid)
        if not ch or not ch.mature_channel_eligible(as_of):continue
        for v in videos:
            if v.channel_id!=cid or not 0<=v.age_days(as_of)<=30:continue
            if v.duration_sec<DEFAULT_LONG_SECONDS or v.public_views<CURRENT_DEMAND_FLOOR:continue
            source_type=None
            if v.format_id==format_id:
                source_type="EXACT_SAME_FORMAT_RECENT_DEMAND"
            elif (parent_demand_relationship_reviewed and
                  v.format_id in (broader_parent_format_ids or set())):
                source_type="INDEPENDENTLY_REVIEWED_BROADER_PARENT_MARKET_DEMAND"
            if source_type:
                mature_demand.append({
                    "mature_channel":cid,"recent_video_id":v.video_id,
                    "views":v.public_views,"format_id":v.format_id,
                    "relation":source_type})
    gates={
        "NEW_FORMAT_OR_PROVEN_DIFFERENT_IMPLEMENTATION":novelty and format_novelty_independently_reviewed,
        "CHANNEL_CREATED_0_TO_30_DAYS_VERIFIED":bool(new_winners),
        "TWO_DIFFERENT_MILLION_VIDEOS_PER_NEW_CHANNEL":bool(new_winners),
        "MATURE_SAME_FORMAT_STILL_GETS_100K_VIEWS":bool(mature_demand),
        "MONETIZATION_THOUSANDS_PER_MONTH_OBSERVED":False,
        "NEW_CREATORS_CAN_COMPETE_VERIFIED_FROM_SAMPLES":bool(new_winners),
        "SCALE_TO_100K_OR_1M_PER_MONTH_VERIFIED":False,
    }
    # Financial upside is a business hypothesis, NOT a hard condition to
    # claim VERIFIED from video metadata (not observable from competitor stats).
    empirical=all(gates[k] for k in (
        "NEW_FORMAT_OR_PROVEN_DIFFERENT_IMPLEMENTATION",
        "CHANNEL_CREATED_0_TO_30_DAYS_VERIFIED",
        "TWO_DIFFERENT_MILLION_VIDEOS_PER_NEW_CHANNEL",
        "MATURE_SAME_FORMAT_STILL_GETS_100K_VIEWS",
        "NEW_CREATORS_CAN_COMPETE_VERIFIED_FROM_SAMPLES"))
    state=("EMPIRICAL_BREAKOUT_PATTERN_CONFIRMED_FINANCE_REVIEW_REQUIRED"
           if empirical else "WATCHLIST_INSUFFICIENT_EVIDENCE")
    missing=[k for k in (
        "NEW_FORMAT_OR_PROVEN_DIFFERENT_IMPLEMENTATION",
        "CHANNEL_CREATED_0_TO_30_DAYS_VERIFIED",
        "TWO_DIFFERENT_MILLION_VIDEOS_PER_NEW_CHANNEL",
        "MATURE_SAME_FORMAT_STILL_GETS_100K_VIEWS")
        if not gates[k]]
    return {
        "fingerprint":fingerprint,"format_id":format_id,
        "status":state,"gate_results":gates,
        "missing_evidence":missing,"winner_channels":new_winners,
        "mature_current_demand_evidence":mature_demand[:20],
        "broader_parent_market_used":any(
            x["relation"]=="INDEPENDENTLY_REVIEWED_BROADER_PARENT_MARKET_DEMAND"
            for x in mature_demand),
        "parent_relationship_requires_review":True,
        "sample_not_all_youtube":True,
        "novelty_requires_independent_review":not format_novelty_independently_reviewed,
        "channel_start_requires_verified_source":True,
        "exact_revenue_of_competitors_known":False,
        "can_earn_thousands_monthly_proven":False,
        "long_term_100k_to_1m_monthly_proven":False,
        "need_cost_per_accepted_minute":True,
        "need_rpm_geography_policy_originality_and_ownership":True,
        "revenue_scenarios_not_predictions":revenue_scenarios([1_000_000,5_000_000,20_000_000]),
        "hypothetical_monthly_views_needed_before_costs":{
            str(target):[
                {"assumed_rpm_usd":rpm,
                 "monthly_views_required":round(target*1000/rpm)}
                for rpm in (0.5,2.0,5.0,10.0)
            ] for target in (3_000,100_000,1_000_000)},
        "human_greenlight_required":True,
    }

def _context(video:VideoEvidence,as_of:dt.date)->dict:
    return {"video_id":video.video_id,"title":video.title,
            "url":"https://www.youtube.com/watch?v="+video.video_id,
            "views":video.public_views,"age_days_from_utc_day":video.age_days(as_of),
            "format_id":video.format_id,"source":video.source,
            "actual_media_access":video.media_access}

def approved_niche_research(*,store:DualResearchStore,niche_id:str,format_id:str,
                            channels:dict[str,ChannelEvidence],videos:list[VideoEvidence],
                            as_of:dt.date)->dict:
    if not store.approved(niche_id,format_id):
        return {
            "status":"NOT_APPROVED_NO_NICHE_RESEARCH","niche_id":niche_id,
            "format_id":format_id,"rivals_leaders":[],
            "new_challengers":[],
            "recent_0_15_day_million_videos":[],
            "user_approval_required":True,
        }
    subset=[v for v in videos if v.format_id==format_id and 0<=v.age_days(as_of)]
    links=store.peer_links(niche_id,format_id)
    leader_ids={r["channel_id"] for r in links if r["cohort"]=="LEADER"}
    pinned_mature={r["channel_id"] for r in links if r["cohort"]=="MATURE_DEMAND"}
    leaders=[]
    for cid in sorted(leader_ids):
        ch=channels.get(cid)
        if not ch:continue
        channel_clips=[v for v in subset if v.channel_id==cid]
        recent=[v for v in channel_clips if v.age_days(as_of)<=30]
        historical_popular=sorted(channel_clips,key=lambda v:v.public_views,reverse=True)[:5]
        baseline=(sorted([v.public_views for v in recent])[len(recent)//2]
                  if len(recent)>=3 else None)
        outliers=[{"video":_context(v,as_of),
                   "relative_to_recent_median":round(v.public_views/max(baseline,1),2)}
                  for v in recent if baseline is not None and v.public_views>=2*baseline]
        subs=(ch.subscriber_count if isinstance(ch.subscriber_count,int)
              and ch.has_verified_creation and ch.subscribers_observed_at else None)
        leaders.append({
            "channel_id":cid,"channel":ch.channel_name,
            "subscribers":subs,"million_subscribers_verified":subs is not None and subs>=MILLION,
            "popular_videos":[_context(v,as_of) for v in historical_popular],
            "recent_uploads":[_context(v,as_of) for v in recent],
            "recent_outperformance_vs_same_channel_median":outliers,
            "requires_more_samples_if_no_median":baseline is None,
            "relative_to_subscribers":None if subs is None else [
                {"video_id":v.video_id,
                 "views_to_current_subscribers_ratio_NOT_REACH":round(v.public_views/max(subs,1),3)}
                for v in recent],
        })
    challengers=[]
    for cid,ch in channels.items():
        if not ch.new_channel_eligible(as_of):continue
        hits=[v for v in subset if v.channel_id==cid and
              v.age_days(as_of)<=30 and v.public_views>=MILLION]
        if hits:
            challengers.append({
                "channel_id":cid,"channel":ch.channel_name,
                "verified_created_day":ch.created_utc_day,
                "over_1m_videos":[_context(v,as_of) for v in hits],
                "two_million_videos_condition_met":len({v.video_id for v in hits})>=2,
                "format_confirmed_by_full_video":False,
            })
    trending=[v for v in subset if v.public_views>=MILLION and 0<=v.age_days(as_of)<=15
              and v.duration_sec>=DEFAULT_LONG_SECONDS]
    trending.sort(key=lambda v:(-v.public_views,v.video_id))
    return {
        "status":"APPROVED_NICHE_SOURCE_RESEARCH_PENDING_CREATIVE_VERIFICATION",
        "niche_id":niche_id,"format_id":format_id,
        "cohort_A_leaders":leaders,
        "cohort_B_new_channels":challengers,
        "cohort_C_trends_0_15d_million":[_context(v,as_of) for v in trending],
        "per_niche_trend_has_not_been_adopted":True,
        "mature_demand_reference_channel_ids":sorted(pinned_mature),
        "shot_by_shot_audio_analysis_completed":False,
        "creative_hypothesis_work_required":True,
        "originality_and_rights_review_required":True,
        "approved_for_publication":False,
        "continuous_learning_requires_own_channel_analytics":True,
        "no_youtube_views_guarantee":True,
    }

def load_v199_snapshot(root:Path,*,limit:int=300)->tuple[dict[str,ChannelEvidence],list[VideoEvidence]]:
    """Read actually recorded accepted video metadata, not quarantined guesses."""
    base=Path(root)/"data/research/youtube_breakout/cinefactory_breakout.sqlite3"
    if not base.exists():return {},[]
    store=DualResearchStore(base)
    with sqlite3.connect(str(base)) as db:
        tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if not {"videos","observations"}.issubset(tables):
            return {},[]
        rows=db.execute("""SELECT v.video_id,v.title,v.upload_date,v.channel_id,
                         o.lane,v.duration_sec,o.views,o.observed_at,v.channel_name
                         FROM observations o JOIN videos v ON v.video_id=o.video_id
                         WHERE v.channel_id IS NOT NULL
                         ORDER BY o.observed_at DESC LIMIT ?""",(limit,)).fetchall()
    channels={}
    seen=set()
    videos=[]
    for vid,title,posted,cid,lane,duration,views,at,name in rows:
        if vid in seen or lane not in LANE_TO_NICHE:continue
        seen.add(vid)
        if not isinstance(posted,str) or len(posted)!=8:continue
        try:
            publish=f"{posted[:4]}-{posted[4:6]}-{posted[6:8]}"
            video=VideoEvidence(vid,cid,lane,title,publish,int(views),int(duration),at)
            videos.append(video)
            channels[cid]=store.channel(cid) or ChannelEvidence(cid,name,None,None)
        except (ValueError,TypeError):
            continue
    return channels,videos

def generate_two_track_daily(root:Path,*,as_of:dt.date|None=None)->dict:
    now=as_of or dt.datetime.now(UTC).date()
    root=Path(root).resolve()
    base=root/"data/research/youtube_breakout"
    store=DualResearchStore(base/"cinefactory_breakout.sqlite3")
    channels,videos=load_v199_snapshot(root)
    # Independently reviewed novel-format clips are stored with exact
    # proposal identifiers so new niches can be evaluated in Branch 1.
    # No automatic title-based assignment to a novel format.
    existing={v.video_id for v in videos}
    for v in store.reviewed_videos():
        if v.video_id not in existing:
            videos.append(v);existing.add(v.video_id)
        if v.channel_id not in channels:
            channels[v.channel_id]=store.channel(v.channel_id) or ChannelEvidence(v.channel_id,"UNKNOWN",None,None)
    proposals=store.proposals()
    # Global branch: known formats are NOT new niches merely because one
    # new video goes viral. Only explicit, differentiated proposals considered.
    global_results=[]
    for proposal in proposals:
        # New proposals get isolated IDs and MUST have independently reviewed
        # novelty + 2 strong new videos + mature same-format demand.
        global_results.append(verified_opportunity(
            fingerprint=proposal["fingerprint"],
            format_id=proposal["proposal_id"],
            channels=channels,videos=videos,
            mature_peer_channel_ids={
                cid for cid,ch in channels.items() if ch.mature_channel_eligible(now)
            },
            niche_existing_fingerprints=set(LANE_TO_NICHE),
            as_of=now,format_novelty_independently_reviewed=(
                proposal["state"]=="DISTINCT_FORMAT_REVIEWED")))
    approved_results=[]
    for a in store.approvals():
        if a["state"]!="APPROVED":continue
        approved_results.append(approved_niche_research(
            store=store,niche_id=a["niche_id"],format_id=a["format_id"],
            channels=channels,videos=videos,as_of=now))
    result={
        "schema":REPORT_VERSION,"as_of_utc_day":now.isoformat(),
        "branch_1_global_new_niche_scan":{
            "status":"NO_EMPIRICAL_WINNING_NICHE_CONFIRMED" if not any(
                x["status"].startswith("EMPIRICAL") for x in global_results) else
                "EMPIRICAL_CANDIDATE_REQUIRES_FINANCE_AND_CREATIVE_REVIEW",
            "existing_formats_are_not_auto_new_niches":True,
            "candidate_fingerprint_proposals":global_results,
            "unproven_new_formats_need_research_agent_and_source_discovery":True,
            "verified_born_0_30d_channels_in_ledger":sum(
                ch.new_channel_eligible(now) for ch in channels.values()),
            "has_two_million_views_gate":True,
            "has_mature_current_demand_gate":True,
            "revenue_is_scenario_not_certainty":True,
        },
        "branch_2_approved_niche_studies":{
            "status":"NO_USER_APPROVED_NICHES" if not approved_results else "ONLY_USER_APPROVED_NICHES_RUN",
            "approved_research":approved_results,
            "approved_format_count":len(approved_results),
            "not_approved_has_no_deep_study":True,
            "cohort_A_LEADERS":True,"cohort_B_NEW_CHALLENGERS":True,
            "cohort_C_RECENT_MILLION_0_TO_15_DAYS":True,
        },
        "all_14_formats_search_schedule_is_source_limited":True,
        "data_sources":{"public_video_snapshots":len(videos),
                        "known_channels":len(channels),
                        "known_created_day_verified":sum(
                            ch.has_verified_creation for ch in channels.values())},
        "full_competitor_videos_watched":False,
        "claude_code_called":False,
        "automatic_youtube_upload_authorized":False,
    }
    folder=base/"two_track_reports"
    folder.mkdir(parents=True,exist_ok=True)
    created=dt.datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output=folder/("two_track_"+created+".json")
    result["report_path"]=str(output)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result
