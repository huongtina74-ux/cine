"""Evidence research lane for an approved-niche investigation or bounded research demo.

Uses Company's EXISTING public search/catalog outputs, no duplicate collector.
Metadata-based topical fit is always a QUESTION, never verified semantic fit.
Shared council evidence has ONE public-YouTube lineage; no pseudo independence.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

from .core import _write_json
from .council import collect_evidence
from .market_bridge import _slug
from .public_prescreen import _catalog_vids, _valid_display_views

CID = re.compile(r"^UC[A-Za-z0-9_-]{22}$")
VID = re.compile(r"^[A-Za-z0-9_-]{11}$")
SUBSCRIBERS = re.compile(r"^\s*([\d,]+(?:\.\d+)?)\s*([KMB])?\s+subscribers?\s*$",re.IGNORECASE)
MAX_AGE_H = 48


def _dt(value: str) -> datetime:
    x=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    if x.tzinfo is None:
        raise ValueError("All observation timestamps require a timezone")
    return x.astimezone(timezone.utc)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> dict:
    x=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(x,dict):
        raise ValueError("Expected JSON object")
    return x


TITLE_STOPWORDS = {"the","and","for","with","from","videos","video","official",
                   "latest","new","channel","content","best"}


def _title_keyword_alignment(title: str, niche: str) -> str:
    """Conservative metadata proxy; never certifies actual video content."""
    niche_tokens = set(re.findall(r"[a-z0-9]+",niche.casefold())) - TITLE_STOPWORDS
    title_tokens = set(re.findall(r"[a-z0-9]+",str(title or "").casefold()))
    if not niche_tokens:
        return "NO_DISTINCTIVE_NICHE_TOKENS"
    return "ALL_NICHE_TITLE_TOKENS_PRESENT" if niche_tokens.issubset(title_tokens) else "NOT_TITLE_ALIGNED"


def _subscriber_proxy(value: str) -> int | None:
    match=SUBSCRIBERS.fullmatch(str(value or ""))
    if not match:
        return None
    n=float(match.group(1).replace(",",""))
    scale={"":1,"K":1_000,"M":1_000_000,"B":1_000_000_000}[match.group(2).upper() if match.group(2) else ""]
    return round(n*scale)


def _age_range(joined: str, when: datetime) -> tuple[float,float] | None:
    try:
        born=datetime.strptime(joined,"%Y-%m-%d").replace(tzinfo=timezone.utc)
    except (ValueError,TypeError):
        return None
    max_days=(when-born).total_seconds()/86400
    return (round(max_days-1,3),round(max_days,3))


def _source_search(file: Path, niche: str) -> tuple[dict,dict[str,dict]]:
    src=_read(file)
    if src.get("status")!="COMPLETE" or src.get("successful_query_count") != src.get("query_count"):
        raise ValueError("Only finished canonical public search runs may form research plans")
    records={}
    for obs in src.get("observations",[]):
        if not isinstance(obs,dict):
            continue
        if _slug(obs.get("seed_cluster","")) != _slug(niche):
            continue
        cid=obs.get("channel_id")
        vid=obs.get("video_id")
        if not isinstance(cid,str) or not CID.fullmatch(cid) or not isinstance(vid,str) or not VID.fullmatch(vid):
            continue
        record=records.setdefault(cid,{"channel_id":cid, "channel_name":str(obs.get("channel_name") or ""),
                "channel_url":"https://www.youtube.com/channel/"+cid,
                "joined_date":str(obs.get("joined_date") or ""),
                "subscriber_count_text":str(obs.get("subscriber_count_text") or ""),
                "observed_video_ids":set(), "observed_video_titles":[],
                "query_names":set()})
        record["observed_video_ids"].add(vid)
        record["query_names"].add(str(obs.get("query") or ""))
        record["observed_video_titles"].append(str(obs.get("video_title") or ""))
        if obs.get("joined_date") and not record["joined_date"]:
            record["joined_date"]=str(obs["joined_date"])
        if obs.get("subscriber_count_text") and not record["subscriber_count_text"]:
            record["subscriber_count_text"]=str(obs["subscriber_count_text"])
    return src,records


def plan_research_channels(search_json: str | Path, output_dir: str | Path, *,
                           niche: str, max_channels: int=6,
                           as_of: str | None=None) -> dict:
    """Balanced bounded shortlist: new first, mature leaders and unknowns after."""
    if not 1 <= max_channels <= 30 or not _slug(niche):
        raise ValueError("Niche and bounded channel budget required")
    search=Path(search_json).resolve(strict=True)
    src,rows=_source_search(search,niche)
    as_time=_dt(as_of) if as_of else datetime.now(timezone.utc)
    collected=_dt(src["generated_at"])
    age_h=(as_time-collected).total_seconds()/3600
    current=0 <= age_h <= MAX_AGE_H
    categorized={"newcomer":[],"mature_leader":[],"mature":[],"unknown":[]}
    for cid,record in rows.items():
        ages=_age_range(record["joined_date"],collected)
        subs=_subscriber_proxy(record["subscriber_count_text"])
        if ages and ages[1] >= 0 and 0 <= ages[0] <= 30:
            key="newcomer"
        elif ages and ages[0] >= 365 and subs is not None and subs >= 1_000_000:
            key="mature_leader"
        elif ages and ages[0] >= 365:
            key="mature"
        else:
            key="unknown"
        categorized[key].append({**record,"observed_video_ids":sorted(record["observed_video_ids"]),
                                 "query_names":sorted(record["query_names"]),
                                 "age_days_range_at_search":ages,"subscriber_proxy":subs,
                                 "bucket":key})
    for key in categorized:
        categorized[key].sort(key=lambda x:(-len(x["observed_video_ids"]),-(x["subscriber_proxy"] or 0),x["channel_id"]))
    selected=[]
    # Round-robin keeps major established + independent new competitors represented.
    while len(selected)<max_channels and any(categorized.values()):
        for key in ("newcomer","mature_leader","mature","unknown"):
            if len(selected)>=max_channels:break
            if categorized[key]:
                selected.append(categorized[key].pop(0))
    dest=Path(output_dir)
    dest.mkdir(parents=True,exist_ok=True)
    shortlist=dest/"channel_shortlist.csv"
    if shortlist.exists() or (dest/"plan.json").exists():
        raise FileExistsError("Research plan is immutable; create a new run directory")
    with shortlist.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["niche_slug","channel","channel_url","channel_id"])
        w.writeheader()
        for rec in selected:
            w.writerow({"niche_slug":_slug(niche),"channel":rec["channel_name"],
                        "channel_url":rec["channel_url"],"channel_id":rec["channel_id"]})
    result={
        "schema":"cine.research.evidence_plan.v1",
        "niche":niche,"state":"COLLECT_CATALOGS" if current and selected else
                "HISTORICAL_ONLY" if not current else "NO_MATCHING_CHANNELS",
        "search_path":str(search),"search_sha256":_sha(search),
        "search_observed_at":collected.isoformat(),"planned_at":as_time.isoformat(),
        "source_age_hours":round(age_h,2),
        "shortlist_csv":str(shortlist),"shortlist_sha256":_sha(shortlist),
        "max_channels":max_channels,"selected":selected,
        "unique_source_channels":len(rows),
        "collection_kind":"UNOFFICIAL_PUBLIC_METADATA",
        "approval_status":"NOT_REVIEWED",
        "limitations":["Search rank does not prove topic membership or video virality",
                       "Day-precision About date cannot certify exact 0-30 day boundary",
                       "Subscriber display counts and video metrics are rounded proxies"],
    }
    _write_json(dest/"plan.json",result)
    return result


def analyze_research_evidence(plan_json: str | Path, catalog_json: str | Path,
                              output: str | Path, *, as_of: str | None=None) -> dict:
    """Join frozen search -> planned catalog by stable IDs, produce review-only findings."""
    plan_path=Path(plan_json).resolve(strict=True)
    plan=_read(plan_path)
    if plan.get("schema")!="cine.research.evidence_plan.v1":
        raise ValueError("Expected a planned canonical evidence collection")
    search=Path(plan["search_path"]).resolve(strict=True)
    shortlist=Path(plan["shortlist_csv"]).resolve(strict=True)
    if _sha(search)!=plan["search_sha256"] or _sha(shortlist)!=plan["shortlist_sha256"]:
        raise ValueError("Search or shortlist mutated after the plan was created")
    catalog_path=Path(catalog_json).resolve(strict=True)
    raw=_read(catalog_path)
    if not isinstance(raw.get("channels"),list):
        raise ValueError("Canonical channel catalog list absent")
    collected=_dt(raw["generated_at"])
    search_time=_dt(plan["search_observed_at"])
    if not 0 <= (collected-search_time).total_seconds() <= 24*3600:
        raise ValueError("Catalog observations must follow search within 24 hours")
    when=_dt(as_of) if as_of else datetime.now(timezone.utc)
    age_h=(when-collected).total_seconds()/3600
    current=0 <= age_h <= MAX_AGE_H and plan["state"]=="COLLECT_CATALOGS"
    selected={r["channel_id"]:r for r in plan["selected"]}
    seen=set()
    cross_owners:dict[str,set[str]]={}
    for row in raw["channels"]:
        if not isinstance(row,dict):
            raise ValueError("Malformed canonical public channel row")
        cid=row.get("channel_id")
        if cid not in selected or cid in seen:
            raise ValueError("Catalog has unexpected or duplicated channel ID")
        seen.add(cid)
        for video in row.get("videos") or []:
            if isinstance(video,dict) and isinstance(video.get("video_id"),str):
                cross_owners.setdefault(video["video_id"],set()).add(cid)
    shared={ident for ident,owners in cross_owners.items() if len(owners)>1}
    snapshots=[]
    counts={"channels_planned":len(selected),"channels_collected":len(seen),
            "catalog_errors":0,"channels_with_longform_metadata":0,
            "newcomer_channels":0,"leader_channels":0,
            "mature_recent_demand_proxies":0,
            "fresh_0_15d_million_view_proxies":0,
            "two_million_newcomer_proxies":0,"live_status_unknown_videos":0,
            "cross_channel_video_id_conflicts":len(shared),
            "excluded_cross_topic_fresh_million_view_proxies":0}
    for row in raw["channels"]:
        cid=row["channel_id"]
        meta=selected[cid]
        if row.get("collection_status")!="VERIFIED":
            counts["catalog_errors"]+=1
            valid=[]
        else:
            valid=[v for v in _catalog_vids(row.get("videos") or [])
                   if v["video_id"] not in shared]
        for video in valid:
            video["topic_title_alignment"]=_title_keyword_alignment(video["title"],plan["niche"])
        aligned=[v for v in valid if v["topic_title_alignment"]=="ALL_NICHE_TITLE_TOKENS_PRESENT"]
        recent=[v for v in aligned if isinstance(v.get("video_age_days_proxy"),int)
                and 0<=v["video_age_days_proxy"]<=90]
        fresh=[v for v in recent if v["video_age_days_proxy"]<=15
               and v["approx_views"]>=1_000_000]
        million=[v for v in aligned if v["approx_views"]>=1_000_000]
        excluded_fresh=[v for v in valid
                        if v["topic_title_alignment"]!="ALL_NICHE_TITLE_TOKENS_PRESENT"
                        and isinstance(v.get("video_age_days_proxy"),int)
                        and 0<=v["video_age_days_proxy"]<=15
                        and v["approx_views"]>=1_000_000]
        ages=meta["age_days_range_at_search"]
        young=bool(ages and 0<=ages[0] and ages[1]<=30)
        mature=bool(ages and ages[0]>=365)
        channel_had_1m=young and len(million)>=2
        mature_demand=mature and any(v["approx_views"]>=100_000 for v in recent)
        if valid:counts["channels_with_longform_metadata"]+=1
        if young:counts["newcomer_channels"]+=1
        if meta["bucket"]=="mature_leader":counts["leader_channels"]+=1
        if mature_demand:counts["mature_recent_demand_proxies"]+=1
        if channel_had_1m:counts["two_million_newcomer_proxies"]+=1
        counts["fresh_0_15d_million_view_proxies"]+=len(fresh)
        counts["excluded_cross_topic_fresh_million_view_proxies"]+=len(excluded_fresh)
        counts["live_status_unknown_videos"]+=len(valid)
        snapshots.append({
            "channel_id":cid,"channel_name":meta["channel_name"],
            "channel_url":meta["channel_url"],
            "joined_date":meta["joined_date"],
            "channel_age_range_days":ages,
            "subscriber_proxy":meta["subscriber_proxy"],
            "category":meta["bucket"],
            "search_observed_video_ids":meta["observed_video_ids"],
            "catalog_status":row.get("collection_status","UNKNOWN"),
            "sample_longform_videos":valid[:25],
            "longform_sample_count":len(valid),
            "two_million_display_proxy":channel_had_1m,
            "recent_mature_demand_proxy":mature_demand,
            "fresh_0_15d_million_proxy_ids":[v["video_id"] for v in fresh],
            "excluded_cross_topic_fresh_million_video_ids":[v["video_id"] for v in excluded_fresh],
            "topic_fit":"UNKNOWN_REQUIRES_MULTIMODAL_REVIEW",
            "shorts_live_status":"NOT_CONFIRMED_FROM_PUBLIC_VIDEOS_TAB",
            "rights_and_originality":"NOT_CLEARED",
            "public_evidence_only":True,
        })
    work_packets={"leader_review":[],"newcomer_review":[],"fresh_million_review":[],"cross_topic_qa":[]}
    for channel in snapshots:
        cid=channel["channel_id"]
        samples=channel["sample_longform_videos"]
        matching=[v for v in samples if v["topic_title_alignment"]=="ALL_NICHE_TITLE_TOKENS_PRESENT"]
        recent=[v for v in matching if isinstance(v.get("video_age_days_proxy"),int)
                and 0<=v["video_age_days_proxy"]<=90]
        if channel["category"]=="mature_leader" and recent:
            featured=max(recent,key=lambda x:x["approx_views"])
            work_packets["leader_review"].append({
                "channel_id":cid,"video_id":featured["video_id"],
                "video_url":featured["video_url"],"public_approx_views":featured["approx_views"],
                "status":"PENDING_MULTIMODAL_REVIEW","source":"single_youtube_public_lineage",
                "questions":["Why does the video topic/title connect with its audience?",
                             "Analyze script hook, visual progression, scene timing, sound, thumbnail and narrative",
                             "Compare against the channel's actual age-matched baseline; do not infer private retention"]})
        if channel["category"]=="newcomer":
            work_packets["newcomer_review"].append({
                "channel_id":cid,"candidate_video_ids":[v["video_id"] for v in matching[:5]],
                "status":"PENDING_EXACT_CHANNEL_AGE_AND_FORMAT_REVIEW",
                "questions":["Verify official channel creation date and 2 distinct >=1M longform IDs",
                             "Check licensed/original production, format difference and genuine topic fit",
                             "Assess if new entrant is independent rather than a rebrand of established channels"]})
        for vid in samples:
            if vid["video_id"] in channel["fresh_0_15d_million_proxy_ids"]:
                work_packets["fresh_million_review"].append({
                    "channel_id":cid,"video_id":vid["video_id"],"video_url":vid["video_url"],
                    "public_approx_views":vid["approx_views"],
                    "status":"PENDING_ORIGINALITY_TREND_VERIFICATION",
                    "questions":["Confirm exact views, video age, format, live status and topical fit",
                                 "Analyze potential trend versus evergreen demand without copying content"]})
            if vid["video_id"] in channel["excluded_cross_topic_fresh_million_video_ids"]:
                work_packets["cross_topic_qa"].append({
                    "channel_id":cid,"video_id":vid["video_id"],"video_url":vid["video_url"],
                    "reason":"MILLION_VIEW_SEARCH_HIT_WITHOUT_ALL_NICHE_TITLE_TOKENS",
                    "status":"EXCLUDED_FROM_NICHE_METRICS_REQUIRES_HUMAN_REVIEW"})
    if not current:state="HISTORICAL_ONLY"
    elif counts["catalog_errors"] or counts["channels_collected"]<counts["channels_planned"]:
        state="PARTIAL_EVIDENCE"
    else:state="PUBLIC_EVIDENCE_READY_FOR_REVIEW"
    evidence={
        "schema":"cine.research.automated_evidence.v1",
        "state":state,"niche":plan["niche"],
        "topic_alignment_policy":"ALL_NICHE_TITLE_TOKENS_PRESENT_METADATA_PROXY_NOT_SEMANTIC_PROOF",
        "collection_period":{"search":search_time.isoformat(),
                             "catalog":collected.isoformat(),"as_of":when.isoformat()},
        "source_files":{
            "search":{"path":str(search),"sha256":_sha(search)},
            "plan":{"path":str(plan_path),"sha256":_sha(plan_path)},
            "catalog":{"path":str(catalog_path),"sha256":_sha(catalog_path)},
        },
        "counts":counts,"channels":snapshots,
        "per_video_work_packets":work_packets,
        "worklist":[
            {"department":"research","task":"Classify each channel and video by actual niche/format, mark unrelated queries"},
            {"department":"growth","task":"Find truly new 0-30d channels and inspect relative-age view snapshots, not isolated rankings"},
            {"department":"editorial","task":"Review storyboard, pacing, visuals, sound, packaging and title/thumbnail evidence with timestamps"},
            {"department":"quality","task":"Validate rights, source independence, metadata contamination, and contradictory cases"},
            {"department":"finance","task":"Model scenarios only after RPM/channel economics/cost assumptions are grounded"},
        ],
        "five_gate_status":"NOT_EVALUATED",
        "strict_breakout_witnesses":0,
        "supported_to_produce":False,
        "eligible_for_owner_approval":False,
        "known_gaps":[
            "No independently authenticated exact video/channel metadata",
            "Public catalog video age and view count are display-level approximations",
            "No proof of actual YouTube recommendation traffic, CTR, retention or RPM",
            "Matching niche words in titles is only a review signal, not proof of true content",
            "Cross-topic search results are excluded from niche trend tallies",
            "No actual visual/audio semantic review or license verification",
            "No automatic claim of niche novelty, evergreen longevity, or commercial success",
        ],
    }
    dest=Path(output)
    if dest.exists():raise FileExistsError("Evidence report is immutable")
    _write_json(dest,evidence)
    render_evidence_markdown(evidence,dest.with_suffix(".md"))
    return evidence


def prepare_evidence_council(evidence_json: str | Path, output_dir: str | Path) -> dict:
    """Create ONE shared question + same-origin public sources, pending human/AI reviews."""
    source=Path(evidence_json).resolve(strict=True)
    packet=_read(source)
    if packet.get("schema")!="cine.research.automated_evidence.v1":
        raise ValueError("Canonical research evidence report required")
    out=Path(output_dir)
    if (out/"council_evidence_registry.json").exists():
        raise FileExistsError("Council packet already exists; preserve prior revision")
    records=[{"evidence_id":"search","kind":"public_metadata",
              "path":packet["source_files"]["search"]["path"],
              "independent_root":"youtube-public-lineage","verified_by":"local_machine",
              "scope":"same_unofficial_youtube_origin"},
             {"evidence_id":"catalog","kind":"public_metadata",
              "path":packet["source_files"]["catalog"]["path"],
              "independent_root":"youtube-public-lineage","verified_by":"local_machine",
              "scope":"same_unofficial_youtube_origin"},
             {"evidence_id":"analysis","kind":"observation","path":str(source),
              "independent_root":"youtube-public-lineage","verified_by":"local_machine",
              "scope":"derived_not_independent"}]
    for record in records[:2]:
        expected=packet["source_files"][record["evidence_id"]]["sha256"]
        if _sha(Path(record["path"]).resolve(strict=True))!=expected:
            raise ValueError("Original source mutated since research evidence report")
    registry=collect_evidence(records,out/"council_evidence_registry.json")
    issue_id="review-"+_slug(packet["niche"])+"-"+_sha(source)[:12]
    issue={"issue_id":issue_id,
           "question":f"Which claims about {packet['niche']} are supported by the public source and what exact independent evidence is missing to validate the five niche gates?"}
    _write_json(out/"council_issue.json",issue)
    tasks={"schema":"cine.research.automated_evidence_council.v1",
           "state":"PENDING_APPROVED_DEPARTMENT_REVIEW","issue":issue,
           "roles":["research","growth","editorial","quality","finance"],
           "shared_registry":str((out/"council_evidence_registry.json").resolve()),
           "evidence_sha256":_sha(source),"production_permission":False,
           "instructions":"Same canonical source, no fake independence. Challenge unsupported trend/evergreen/RPM and require video/thumbnail analysis. Never mark reviewed automatically."}
    _write_json(out/"council_tasks.json",tasks)
    return tasks


def run_live_evidence_research(company_root: str | Path, queries_json: str | Path,
                               youtubejs_entry: str | Path, output_root: str | Path,
                               *, niche: str, max_channels: int=6,
                               max_results_per_query: int=7, videos_per_channel: int=12,
                               timeout_seconds: int=180,
                               deep_thumbnail_budget: int=0) -> dict:
    """Orchestrate existing canonical Node collectors. NO official API or paid LLM.

    Explicit budgets, subprocess-tree termination, frozen evidence, council pending.
    A failure yields a local run manifest; it never fabricates a complete report.
    """
    import shutil
    from .daily_research import _run_with_timeout_tree

    if (not 1<=max_channels<=10 or not 1<=max_results_per_query<=10
        or not 1<=videos_per_channel<=30 or not 30<=timeout_seconds<=600
        or not 0<=deep_thumbnail_budget<=6):
        raise ValueError("Live probe budgets out of supported range")
    root=Path(company_root).resolve(strict=True)
    search_script=(root/"scripts"/"collect_youtubejs_recent_search.mjs").resolve(strict=True)
    catalog_script=(root/"scripts"/"collect_youtubejs_channel_catalogs.mjs").resolve(strict=True)
    youtubejs=Path(youtubejs_entry).resolve(strict=True)
    if youtubejs.name!="node.js" or "youtubei.js" not in str(youtubejs):
        raise ValueError("A locally installed youtubei.js Node entry is required")
    node=shutil.which("node")
    if not node:
        raise FileNotFoundError("Node.js executable not found")
    source=Path(queries_json).resolve(strict=True)
    queries=json.loads(source.read_text(encoding="utf-8"))
    if (not isinstance(queries,list) or not 1<=len(queries)<=5
        or not _slug(niche)):
        raise ValueError("One to five authorized same-niche queries required")
    for item in queries:
        if (not isinstance(item,dict)
            or _slug(item.get("seed_cluster",""))!=_slug(niche)
            or not isinstance(item.get("query"),str)
            or not 3<=len(item["query"].strip())<=120):
            raise ValueError("All queries must be nonempty and share one niche")
    target=Path(output_root).resolve()
    if target.exists():
        raise FileExistsError("Live research destination exists; cannot overwrite a prior run")
    target.mkdir(parents=True)
    state={"schema":"cine.research.live_evidence_run.v1",
           "state":"RUNNING","niche":niche,
           "query_source":{"path":str(source),"sha256":_sha(source)},
           "company_collector":str(root),
           "max_channels":max_channels,"max_results_per_query":max_results_per_query,
           "videos_per_channel":videos_per_channel,
           "deep_thumbnail_budget":deep_thumbnail_budget,
           "no_official_api_calls":True,"no_paid_model_calls":True,
           "production_permission":False}
    def stage(cmd: list[str], label: str) -> None:
        out,err,code,timed_out=_run_with_timeout_tree(cmd,root,timeout_seconds)
        (target/(label+".stdout.log")).write_text(out[-100_000:],encoding="utf-8")
        (target/(label+".stderr.log")).write_text(err[-100_000:],encoding="utf-8")
        if code!=0 or timed_out:
            raise RuntimeError(label+"_COLLECTOR_"+("TIMEOUT" if timed_out else "FAILED"))
    try:
        stage([node,str(search_script),"--youtubejs-entry",str(youtubejs),
               "--queries-json",str(source),"--output",str(target/"search.json"),
               "--max-results",str(max_results_per_query),
               "--max-about-channels",str(min(30,max_channels*3)),
               "--upload-date","week"],"search")
        plan=plan_research_channels(target/"search.json",target/"plan",niche=niche,
                                    max_channels=max_channels)
        state["search_state"]=plan["state"]
        state["selected_channels"]=len(plan["selected"])
        if plan["state"]!="COLLECT_CATALOGS":
            state["state"]="NO_FRESH_CHANNELS_FOR_CATALOG"
        else:
            stage([node,str(catalog_script),"--youtubejs-entry",str(youtubejs),
                   "--shortlist",str(target/"plan"/"channel_shortlist.csv"),
                   "--output",str(target/"catalog.json"),
                   "--max-videos",str(videos_per_channel)],"catalog")
            report=analyze_research_evidence(target/"plan"/"plan.json",
                                              target/"catalog.json",target/"evidence.json")
            state["evidence_state"]=report["state"]
            state["counts"]=report["counts"]
            prepare_evidence_council(target/"evidence.json",target/"council")
            if deep_thumbnail_budget and report["state"]=="PUBLIC_EVIDENCE_READY_FOR_REVIEW":
                from .deep_video_intelligence import prepare_public_video_review, verify_deep_video_review
                deep=prepare_public_video_review(target/"evidence.json",target/"deep_intelligence",
                                                 max_videos=deep_thumbnail_budget)
                verified=verify_deep_video_review(target/"deep_intelligence"/"deep_review.json")
                state["deep_intelligence"]={
                    "state":deep["state"],"video_candidates":deep["selected_count"],
                    "verified_thumbnail_integrity_count":verified["verified_thumbnails"],
                    "council_issue_id":verified["council_issue_id"],
                    "full_video_semantics_completed":False,
                }
            state["state"]="REVIEW_PACKET_CREATED" if report["state"]=="PUBLIC_EVIDENCE_READY_FOR_REVIEW" else "PARTIAL_REVIEW_PACKET"
    except (OSError,ValueError,RuntimeError,KeyError,TypeError,json.JSONDecodeError) as exc:
        state["state"]="FAILED_OR_INCOMPLETE"
        state["failure_type"]=type(exc).__name__
        state["failure_stage"]=str(exc)[:120] if str(exc).endswith(("_COLLECTOR_FAILED","_COLLECTOR_TIMEOUT")) else "VALIDATION_OR_IO_FAILED"
    state["reported_at"]=datetime.now(timezone.utc).isoformat()
    _write_json(target/"live_run_manifest.json",state)
    return state


def render_evidence_markdown(evidence: dict, output: str | Path) -> Path:
    """Human-readable factual/provisional report; never a verified niche verdict."""
    if evidence.get("schema")!="cine.research.automated_evidence.v1":
        raise ValueError("Automated evidence pack required")
    dest=Path(output)
    if dest.exists():
        raise FileExistsError("Do not overwrite a previous human-readable report")
    def clean(text: object,limit: int=120) -> str:
        return str(text or "").replace("|","\\|").replace("\n"," ").replace("\r"," ")[:limit]
    lines=[
        "# CineFactory — Public Evidence Research",
        "",
        "**Niche under investigation:** "+clean(evidence["niche"]),
        "**Result:** "+clean(evidence["state"])+" (public metadata; NOT niche certification)",
        "**Observed catalog:** "+clean(evidence["collection_period"]["catalog"]),
        "**Authority:** Advisory only; no production approval or channel-revenue claim",
        "",
        "## Observed sample, not market-wide estimates",
        "",
    ]
    counts=evidence["counts"]
    for label,key in [
        ("Channels planned","channels_planned"),
        ("Channels collected","channels_collected"),
        ("Large established-channel signals","leader_channels"),
        ("Mature channels with recent >=100K on-title video signals","mature_recent_demand_proxies"),
        ("New 0-30 day channel date proxies","newcomer_channels"),
        ("0-15d million-view on-title signals (rounded public display)","fresh_0_15d_million_view_proxies"),
        ("Newcomer channels with 2 million-view title signals","two_million_newcomer_proxies"),
        ("High-view hits excluded for wrong topic title","excluded_cross_topic_fresh_million_view_proxies"),
        ("Catalog collector failures","catalog_errors"),
    ]:
        lines.append(f"- **{label}:** {counts.get(key,0)}")
    lines.extend(["","## Candidates pending departmental review","","| Type | Channel | Sample video and observation |",
                  "|---|---|---|"])
    for channel in evidence["channels"]:
        category=channel["category"]
        samples=[v for v in channel["sample_longform_videos"]
                 if v.get("topic_title_alignment")=="ALL_NICHE_TITLE_TOKENS_PRESENT"]
        if samples:
            best=max(samples,key=lambda x:x["approx_views"])
            video_note=f"[{clean(best['title'],65)}]({best['video_url']}) — ~{best['approx_views']:,} public displayed views; {best.get('video_age_days_proxy')}d proxy"
        else:
            video_note="No matching title token evidence; semantic review pending"
        lines.append(f"| {clean(category)} | [{clean(channel['channel_name'],50)}]({channel['channel_url']}) | {video_note} |")
    lines.extend(["","## Explicit cross-topic exclusions",""])
    excluded=evidence["per_video_work_packets"]["cross_topic_qa"]
    if not excluded:
        lines.append("No high-view mismatched-topic titles observed in this bounded sample.")
    for item in excluded:
        lines.append(f"- [Video {clean(item['video_id'])}]({item['video_url']}) excluded from {clean(evidence['niche'])} trend totals. Reason: title lacks all niche tokens; full video still requires manual classification.")
    lines.extend(["","## Research tasks pending",""])
    for label,key in [
        ("Top established channels","leader_review"),
        ("Newly created channel candidates","newcomer_review"),
        ("Fresh on-title million-view candidates","fresh_million_review"),
        ("Potential cross-topic contamination","cross_topic_qa"),
    ]:
        lines.append(f"- {label}: {len(evidence['per_video_work_packets'][key])} tasks")
    lines.extend(["","## Critical evidence limitations",""])
    lines.extend(f"- {clean(item,240)}" for item in evidence["known_gaps"])
    lines.extend(["","## Source integrity","",
                  "These artifacts come from ONE public YouTube origin, not independent corroboration."])
    for key,item in evidence["source_files"].items():
        lines.append(f"- {key}: SHA-256 `{item['sha256']}` — {clean(item['path'],500)}")
    lines.extend(["","**Next decision:** Exact metadata verification, video-specific visual/audio review, rights check, five-gate evidence and CineCouncil cross-examination."])
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text("\n".join(lines)+"\n",encoding="utf-8")
    return dest
