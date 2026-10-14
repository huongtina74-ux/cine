"""Unified P0 five-gate evidence reconciliation. One source lineage and one case.

Reuse breakout_proof, known_niches and CineCouncil evidence registry instead
of adding new models/scorers. Review assertions are ADVISORY and never
automatically authenticate reviewer identity, licensing or YouTube earnings.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .breakout_proof import audit_official_artifact
from .core import _write_json
from .council import collect_evidence
from .market_bridge import _slug

MAX_FRESH_HOURS = 48
SOURCE_CHECKED = {"VERIFIED", "VERIFIED_OFFICIAL_API"}
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
CHANNEL_ID = re.compile(r"^UC[A-Za-z0-9_-]{22}$")
GATES = ("novelty", "breakout", "evergreen", "business", "entry")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc(value: str) -> datetime:
    x = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if x.tzinfo is None:
        raise ValueError("Source/review time must include timezone")
    return x.astimezone(timezone.utc)


def _num(value: Any, *, positive: bool = False, zero_ok: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError("Financial assumptions must be finite numeric values")
    if (positive and value <= 0) or (not positive and value < 0) or (not zero_ok and value == 0):
        raise ValueError("Financial assumptions must not be negative/zero")
    return float(value)


def _official_channel(catalog: dict, cid: str, at: datetime, *, min_age=0, max_age=30) -> dict | None:
    channel = catalog.get("channels", {}).get(cid)
    if not isinstance(channel, dict) or channel.get("channel_id") != cid or channel.get("evidence_status") not in SOURCE_CHECKED:
        return None
    try:
        age = (at - _utc(channel["created_at"])).total_seconds()/86400
    except (KeyError, ValueError, TypeError):
        return None
    return channel if min_age <= age <= max_age else None


def _official_video(catalog: dict, cid: str, vid: str, at: datetime,
                    *, min_views: int, max_video_days: float=90, min_duration: int=480,
                    global_video_owners: dict[str,set[str]] | None=None) -> dict | None:
    if global_video_owners is not None and global_video_owners.get(vid) != {cid}:
        return None
    if not isinstance(vid, str) or not VIDEO_ID.fullmatch(vid):
        return None
    for video in catalog.get("catalogs", {}).get(cid, []):
        if not isinstance(video, dict) or video.get("video_id") != vid or video.get("channel_id") != cid:
            continue
        try:
            published = _utc(video["published_at"])
            channel_created = _utc(catalog["channels"][cid]["created_at"])
            views = video["views"]
            duration = video["duration_seconds"]
            if any(isinstance(v, bool) or not isinstance(v, int) for v in (views, duration)):
                return None
            age = (at - published).total_seconds()/86400
        except (KeyError, ValueError, TypeError):
            return None
        if (video.get("evidence_status") not in SOURCE_CHECKED or not 0 <= age <= max_video_days
            or published < channel_created
            or views < min_views or duration < min_duration
            or video.get("is_live") or video.get("is_short")
            or video.get("privacy_status", "public") != "public"
            or video.get("format_proxy") not in ("LONG_FORM", "VIDEO", "STANDARD", "LONG")
            or video.get("video_url") != f"https://www.youtube.com/watch?v={vid}"):
            return None
        return video
    return None


def _semantic_source(item: dict, expected_video_ids: list[str]) -> bool:
    """Explicitly reviewed individual IDs; text semantics still require a human audit."""
    return (isinstance(item, dict)
            and item.get("status") == "REVIEWED"
            and item.get("fit") == "DIRECT"
            and isinstance(item.get("why"), str) and len(item["why"].strip()) >= 25
            and isinstance(item.get("video_ids"), list)
            and all(isinstance(v,str) and VIDEO_ID.fullmatch(v) for v in item["video_ids"])
            and set(expected_video_ids).issubset(set(item["video_ids"])))


def _gate(state: str, reason: str, evidence: list[str] | None=None, **detail) -> dict:
    return {"state": state, "reason": reason, "source_ids": evidence or [], **detail}


def build_five_gate_dossier(official_artifact: str | Path, breakout_audit: str | Path,
                            review_file: str | Path, destination: str | Path,
                            *, as_of: str | None=None, portfolio: list[dict] | None=None) -> dict:
    """Build one versioned dossier/QA task pack; NEVER authorize production."""
    source = Path(official_artifact).resolve(strict=True)
    audit_path = Path(breakout_audit).resolve(strict=True)
    review_path = Path(review_file).resolve(strict=True)
    target = Path(destination)
    when = _utc(as_of) if as_of else datetime.now(timezone.utc)
    source_hash, audit_hash, review_hash = _sha(source), _sha(audit_path), _sha(review_path)
    stored = json.loads(audit_path.read_text(encoding="utf-8"))
    if (stored.get("schema") != "cine.research.official_breakout_audit.v1"
        or stored.get("sha256") != source_hash
        or Path(stored.get("source_file", "")).resolve() != source):
        raise ValueError("Breakout report does not match the official source revision")
    # Full deterministic replay: not merely trusting a user-supplied witness boolean.
    comparison_path = target / "audit_recomputed.json"
    recomputed = audit_official_artifact(source, comparison_path, observed_at=stored["observed_at"])
    if (recomputed["witness_channels"] != stored.get("witness_channels")
        or recomputed["counts"] != stored.get("counts")):
        raise ValueError("Stored breakout report differs from the canonical verifier")
    catalog = json.loads(source.read_text(encoding="utf-8"))
    global_video_owners: dict[str,set[str]] = {}
    for cid, videos in catalog.get("catalogs",{}).items():
        for video in videos:
            if isinstance(video,dict) and isinstance(video.get("video_id"),str):
                global_video_owners.setdefault(video["video_id"],set()).add(cid)
    observed = _utc(stored["observed_at"])
    source_age_h = (when-observed).total_seconds()/3600
    fresh = 0 <= source_age_h <= MAX_FRESH_HOURS

    review = json.loads(review_path.read_text(encoding="utf-8"))
    if not isinstance(review, dict) or not isinstance(review.get("niche"), str) or not _slug(review["niche"]):
        raise ValueError("Named niche review required")
    niche, format_key = review["niche"], review.get("format_key")
    if not isinstance(format_key, str) or not _slug(format_key):
        raise ValueError("Explicit format key required")
    try:
        reviewer_time = _utc(review["reviewed_at"])
        reviewer_fresh = (bool(review.get("reviewed_by"))
                          and observed <= reviewer_time <= when
                          and (when-reviewer_time).total_seconds() <= 30*86400)
    except (ValueError, KeyError, TypeError):
        reviewer_fresh = False

    if portfolio is not None and not isinstance(portfolio, list):
        raise ValueError("Portfolio registry must be a list")
    registry_file = Path(__file__).with_name("known_niches.json")
    known = json.loads(registry_file.read_text(encoding="utf-8"))
    known += portfolio or []
    matching = [row for row in known
                if _slug(niche) in {_slug(row.get("niche","")), *(_slug(a) for a in row.get("aliases", []))}]
    novelty = review.get("novelty", {})
    distinct = all(_slug(x.get("format_key", "")) != _slug(format_key) for x in matching)
    explanation = novelty.get("differentiation", "") if isinstance(novelty, dict) else ""
    novelty_ok = (reviewer_fresh and distinct and isinstance(novelty, dict)
                  and novelty.get("status") == "REVIEWED"
                  and isinstance(explanation, str) and len(explanation.strip()) >= 35)
    gate_novelty = _gate(
        "DOCUMENTED_FOR_COUNCIL" if novelty_ok else "NEEDS_EVIDENCE",
        "Format comparison and differentiation supplied by a reviewer; not independently established"
        if novelty_ok else "Missing reviewed differentiation or format already exists in portfolio",
        ["review", "portfolio"], existing_formats=[x.get("format_key") for x in matching],
        distinct_format_key=distinct,
    )

    witness_ids = []
    for row in recomputed["witness_channels"]:
        if not _official_channel(catalog,row["channel_id"],observed):
            continue
        witness_ids.append(row)
    topic_reviews = review.get("topic_fit", {})
    accepted = []
    if isinstance(topic_reviews, dict):
        for row in witness_ids:
            cid=row["channel_id"]
            video_ids=[v["video_id"] for v in row["witness_videos"]]
            if _semantic_source(topic_reviews.get(cid,{}), video_ids[:2]):
                accepted.append(row)
    # Rights risks are evaluated over ALL official witnesses, even when a
    # reviewer has not yet classified their topic. Missing topic fit cannot hide risk.
    rights_markers = sorted({x for row in witness_ids for x in row.get("rights_risk_markers", [])})
    gate_breakout = _gate(
        "OFFICIAL_METRICS_WITH_UNAUTHENTICATED_TOPIC_REVIEW" if fresh and reviewer_fresh and accepted else "NEEDS_EVIDENCE",
        "Two exact long-form million-view videos on a 0-30 day channel; niche fit is manually reviewed"
        if fresh and reviewer_fresh and accepted else
        "Missing current source or independent video-to-niche review",
        ["official_artifact", "breakout_audit", "review"],
        metadata_witness_channels=[x["channel_id"] for x in witness_ids],
        topic_matched_channels=[x["channel_id"] for x in accepted],
        rights_risk_markers=rights_markers,
    )

    evergreen_claims = review.get("evergreen", [])
    evergreen_ids = []
    evergreen_facts = []
    if isinstance(evergreen_claims, list):
        for obj in evergreen_claims:
            if not isinstance(obj, dict):
                continue
            cid, vid = obj.get("channel_id"), obj.get("video_id")
            if not isinstance(cid,str) or not CHANNEL_ID.fullmatch(cid) or cid in evergreen_ids:
                continue
            if (not _official_channel(catalog,cid,observed,min_age=365,max_age=100000)
                or not _official_video(catalog,cid,vid,observed,min_views=100_000,max_video_days=90,
                                       global_video_owners=global_video_owners)
                or not _semantic_source(obj,[vid])):
                continue
            evergreen_ids.append(cid)
            evergreen_facts.append({"channel_id":cid,"video_id":vid,
                                    "views":next(v["views"] for v in catalog["catalogs"][cid] if v["video_id"]==vid)})
    evergreen_ok = fresh and reviewer_fresh and len(evergreen_ids)>=2
    gate_evergreen = _gate(
        "OFFICIAL_METRICS_WITH_UNAUTHENTICATED_TOPIC_REVIEW" if evergreen_ok else "NEEDS_EVIDENCE",
        "Two independent mature channels have recent long-form >=100k-view videos in reviewed topic"
        if evergreen_ok else "Need two different >=365d channels with last-90d >=100k videos and reviewed topic",
        ["official_artifact","review"], channels=evergreen_facts,
    )

    entry = review.get("entry", {})
    entry_channel = entry.get("channel_id") if isinstance(entry,dict) else None
    entry_video = entry.get("video_id") if isinstance(entry,dict) else None
    new_winner_ids={x["channel_id"] for x in witness_ids}
    entry_ok = (fresh and reviewer_fresh and isinstance(entry_channel,str)
                and entry_channel not in new_winner_ids and entry_channel not in evergreen_ids
                and bool(_official_channel(catalog,entry_channel,observed))
                and bool(_official_video(catalog,entry_channel,entry_video,observed,
                                         min_views=100_000,max_video_days=30,
                                         global_video_owners=global_video_owners))
                and _semantic_source(entry,[entry_video]) if isinstance(entry_video,str) else False)
    gate_entry = _gate(
        "OFFICIAL_METRICS_WITH_UNAUTHENTICATED_TOPIC_REVIEW" if entry_ok else "NEEDS_EVIDENCE",
        "Separate 0-30d entrant exhibits >=100k long-form views in the same reviewed topic"
        if entry_ok else "Need independent new entrant; breakout winner alone cannot validate low entry barriers",
        ["official_artifact","review"], independent_entrant=entry_channel if entry_ok else None,
    )

    model=review.get("business",{})
    scenarios=None
    viable=False
    if isinstance(model,dict) and model.get("status")=="REVIEWED":
        try:
            rpm=_num(model["rpm_usd"],positive=True)
            views=_num(model["monthly_views_assumed"],positive=True)
            fixed=_num(model["monthly_fixed_cost_usd"],zero_ok=True)
            cost_per=_num(model["production_cost_usd_per_video"],zero_ok=True)
            video_qty=_num(model["videos_per_month"],positive=True)
            if not 0.1 <= rpm <= 50 or views > 100_000_000 or video_qty > 120:
                raise ValueError("RPM/views/output exceed review guardrails")
            spend=fixed+cost_per*video_qty
            scenarios=[{"name":name,"assumed_monthly_views":round(views*factor),
                        "revenue_usd":round(views*factor*rpm/1000,2),
                        "cost_usd":round(spend,2),
                        "profit_usd":round(views*factor*rpm/1000-spend,2)}
                       for name,factor in (("downside",0.5),("base",1),("upside",1.5))]
            viable=scenarios[1]["profit_usd"]>=2000 and reviewer_fresh
        except (KeyError,TypeError,ValueError):
            pass
    gate_business = _gate(
        "SCENARIO_DOCUMENTED_NOT_PROVEN" if viable else "NEEDS_EVIDENCE",
        "Assumed RPM and volume yield >=$2000 monthly base profit after disclosed production costs; NOT a payout forecast"
        if viable else "Need reviewed assumptions for RPM, volume, fixed and per-video costs to model base profit >=$2000",
        ["review"], scenarios=scenarios, ypp_eligibility="UNKNOWN",
        expected_profit_is_guaranteed=False,
    )

    gates={
        "novelty":gate_novelty,"breakout":gate_breakout,
        "evergreen":gate_evergreen,"business":gate_business,"entry":gate_entry,
    }
    rights_flag=bool(rights_markers)
    missing=[name for name, g in gates.items() if g["state"]=="NEEDS_EVIDENCE"]
    if rights_flag:
        state="RIGHTS_REVIEW_HOLD"
    elif missing:
        state="WATCHLIST_RESEARCH_INCOMPLETE"
    else:
        state="READY_FOR_CINECOUNCIL_CROSS_EXAMINATION"
    revision=hashlib.sha256(
        json.dumps({"sources":[source_hash,audit_hash,review_hash],
                    "as_of":when.isoformat(),"niche":niche,"format_key":format_key},
                   sort_keys=True).encode("utf-8")).hexdigest()
    case={
        "schema":"cine.research.five_gate_dossier.v1",
        "case_id":f"{_slug(niche)}--{_slug(format_key)}",
        "revision":revision, "as_of":when.isoformat(),"observed_at":observed.isoformat(),
        "niche":niche, "format_key":format_key,"state":state,
        "source_age_hours":round(source_age_h,2), "reviewer_identity_authenticated":False,
        "gates":gates, "missing":missing,
        "source_hashes":{"official_artifact":source_hash,"breakout_audit":audit_hash,
                         "review":review_hash, "portfolio":_sha(registry_file)},
        "originality_and_rights":"MANUAL_CLEARANCE_REQUIRED",
        "council_has_decided":False, "user_has_approved":False,
        "production_permission":False,
        "limitations":[
            "Source hashes prove file integrity, not authentic YouTube account provenance",
            "Semantic fit/differentiation are declared by a reviewer, not AI or objectively authenticated",
            "Two mature channels show recent demand, not guaranteed sustained future demand",
            "Business forecasts are hypothetical and YouTube monetization status is unknown",
            "CineCouncil must examine gate evidence, dissent and competing hypotheses",
            "Do not automatically promote an advisory decision to owner permission",
        ],
    }
    target.mkdir(parents=True, exist_ok=True)
    _write_json(target/"dossier.json",case)
    issue={
        "issue_id":case["case_id"]+"@"+revision[:12],
        "question":f"Should {niche} / {format_key} enter a limited ORIGINAL video experiment given five gates, source integrity, copyright and uncertainty?",
    }
    _write_json(target/"council_issue.json",issue)
    registry=collect_evidence([
        {"evidence_id":"official_artifact","kind":"public_metadata","path":str(source),
         "independent_root":"canonical-company-source","verified_by":"local_machine","scope":"exact_public_metrics"},
        {"evidence_id":"breakout_audit","kind":"public_metadata","path":str(audit_path),
         "independent_root":"canonical-company-source","verified_by":"local_machine","scope":"derived_same_source_not_independent"},
        {"evidence_id":"review","kind":"human_review","path":str(review_path),
         "independent_root":"human_assertions_not_authenticated","verified_by":"local_machine","scope":"reviewer_claims_need_cross_exam"},
    ],target/"council_evidence_registry.json")
    questions={
        "research":["Do two mature independently active channels really match the same subniche?",
                    "Does the alleged new format differ materially from existing niche registry?"],
        "growth":["Is the new entrant independent of the original winner and evidence of real market access?",
                  "Can age-matched snapshots corroborate ongoing demand without treating search rank as causal?"],
        "quality":["Does the canonical evidence actually correspond to these named videos/channels?",
                   "What copyright, licensed-content, YPP, reused-content or AI-content risks remain?"],
        "finance":["What views and RPM assumptions underpin $2000+ modeled base profit?",
                   "How does the forecast change with half the views and uncertain YPP eligibility?"],
    }
    council_tasks={"schema":"cine.research.five_gate_council_pack.v1",
                   "issue":issue,"case_path":str((target/"dossier.json").resolve()),
                   "evidence_registry_path":str((target/"council_evidence_registry.json").resolve()),
                   "dossier_sha256":_sha(target/"dossier.json"),
                   "state":"PENDING_EXPLICIT_REVIEW","questions":questions,
                   "missing":missing,"rights_hold":rights_flag,
                   "instructions":"Review same evidence registry; QUALITY must rebut other roles. Do not simulate consensus or assume earnings."}
    _write_json(target/"council_tasks.json",council_tasks)
    return case


def finalize_five_gate_council(destination: str | Path, opinions_file: str | Path) -> dict:
    """Consolidate actual opinions through existing CineCouncil; never self-approve."""
    from .case_controller import consolidate_case
    from .council import verify_registry

    root=Path(destination).resolve(strict=True)
    case_file=root/"dossier.json"
    dossier=json.loads(case_file.read_text(encoding="utf-8"))
    task_pack=json.loads((root/"council_tasks.json").read_text(encoding="utf-8"))
    if (dossier.get("schema")!="cine.research.five_gate_dossier.v1"
            or task_pack.get("dossier_sha256")!=_sha(case_file)):
        raise ValueError("The canonical five-gate dossier changed after review tasks were created")
    registry=json.loads((root/"council_evidence_registry.json").read_text(encoding="utf-8"))
    verified=verify_registry(registry)
    for ident,expected in dossier["source_hashes"].items():
        if ident not in ("official_artifact","breakout_audit","review"):
            continue
        if ident not in verified or verified[ident]["sha256"]!=expected:
            raise ValueError(f"Five-gate source evidence changed: {ident}")
    issue=json.loads((root/"council_issue.json").read_text(encoding="utf-8"))
    if issue.get("issue_id")!=dossier["case_id"]+"@"+dossier["revision"][:12]:
        raise ValueError("CineCouncil issue and five-gate revision mismatch")
    opinions=json.loads(Path(opinions_file).read_text(encoding="utf-8"))
    if not isinstance(opinions,list):
        raise ValueError("Council opinions must be a JSON list")
    manifest=consolidate_case(issue,registry,opinions,root/"council")
    decision=json.loads(Path(manifest["authoritative_decision"]).read_text(encoding="utf-8"))
    if dossier["state"]!="READY_FOR_CINECOUNCIL_CROSS_EXAMINATION":
        state="GATES_OR_RIGHTS_HOLD"
    elif decision["state"]=="SUPPORTED_FOR_TEST":
        state="ADVISORY_FOR_OWNER_REVIEW"
    else:
        state="CINECOUNCIL_DISAGREEMENT_OR_MISSING_REVIEW"
    outcome={
        "schema":"cine.research.five_gate_authoritative_case.v1",
        "case_id":dossier["case_id"],"five_gate_revision":dossier["revision"],
        "dossier_sha256":_sha(case_file),"issue_id":issue["issue_id"],
        "state":state,"five_gate_state":dossier["state"],
        "council_state":decision["state"],
        "council_decision_path":manifest["authoritative_decision"],
        "council_case_path":str((root/"council"/"case.json").resolve()),
        "human_owner_approved":False,"production_permission":False,
        "truth_certified":False,
        "next_action":"Owner must review original source, rights and controlled experiment"
        if state=="ADVISORY_FOR_OWNER_REVIEW" else
        "Resolve missing five-gate evidence, dissent, rights or council review",
    }
    current=root/"case.json"
    if current.exists():
        prior=json.loads(current.read_text(encoding="utf-8"))
        if prior.get("five_gate_revision")!=outcome["five_gate_revision"]:
            raise FileExistsError("Existing case revision differs; do not overwrite canonical decision")
    _write_json(current,outcome)
    return outcome


def prepare_five_gate_review(official_artifact: str | Path, breakout_audit: str | Path,
                             output: str | Path, *, as_of: str | None=None) -> dict:
    """Prepopulate source-backed REVIEW CANDIDATES, never semantic endorsements."""
    source=Path(official_artifact).resolve(strict=True)
    audit_path=Path(breakout_audit).resolve(strict=True)
    saved=json.loads(audit_path.read_text(encoding="utf-8"))
    if (saved.get("schema")!="cine.research.official_breakout_audit.v1"
            or saved.get("sha256")!=_sha(source)
            or Path(saved.get("source_file","")).resolve()!=source):
        raise ValueError("Official source and strict breakout witness revision mismatch")
    at=_utc(saved["observed_at"])
    target=Path(output)
    checked=audit_official_artifact(source,target.with_name("review_prep_recomputed.json"),
                                    observed_at=saved["observed_at"])
    if checked["witness_channels"]!=saved.get("witness_channels"):
        raise ValueError("Breakout witness was modified")
    data=json.loads(source.read_text(encoding="utf-8"))
    owners: dict[str,set[str]]={}
    for cid,vs in data["catalogs"].items():
        for item in vs:
            if isinstance(item,dict) and isinstance(item.get("video_id"),str):
                owners.setdefault(item["video_id"],set()).add(cid)
    founders={r["channel_id"] for r in checked["witness_channels"]}
    mature=[]
    entrants=[]
    for cid,channel in data["channels"].items():
        if not isinstance(cid,str) or not CHANNEL_ID.fullmatch(cid):
            continue
        if _official_channel(data,cid,at,min_age=365,max_age=100000):
            candidate=[]
            for v in data["catalogs"].get(cid,[]):
                ident=v.get("video_id") if isinstance(v,dict) else ""
                official=_official_video(data,cid,ident,at,min_views=100000,max_video_days=90,
                                         global_video_owners=owners)
                if official:
                    candidate.append(official)
            if candidate:
                best=max(candidate,key=lambda v:v["views"])
                mature.append({"channel_id":cid,"video_id":best["video_id"],
                               "source_views":best["views"],"fit":"UNKNOWN",
                               "status":"PENDING","why":"","video_ids":[best["video_id"]]})
        elif cid not in founders and _official_channel(data,cid,at,min_age=0,max_age=30):
            candidates=[]
            for v in data["catalogs"].get(cid,[]):
                ident=v.get("video_id") if isinstance(v,dict) else ""
                found=_official_video(data,cid,ident,at,min_views=100000,max_video_days=30,
                                      global_video_owners=owners)
                if found:
                    candidates.append(found)
            if candidates:
                best=max(candidates,key=lambda v:v["views"])
                entrants.append({"channel_id":cid,"video_id":best["video_id"],
                                 "source_views":best["views"],"fit":"UNKNOWN",
                                 "status":"PENDING","why":"","video_ids":[best["video_id"]]})
    mature.sort(key=lambda x:(-x["source_views"],x["channel_id"]))
    entrants.sort(key=lambda x:(-x["source_views"],x["channel_id"]))
    topic={row["channel_id"]:{
        "video_ids":[v["video_id"] for v in row["witness_videos"][:2]],
        "status":"PENDING","fit":"UNKNOWN","why":"",
        "rights_risk_markers":row.get("rights_risk_markers",[]),
    } for row in checked["witness_channels"]}
    now=_utc(as_of) if as_of else datetime.now(timezone.utc)
    result={
        "schema":"cine.research.five_gate_review_template.v1",
        "state":"MANUAL_REVIEW_REQUIRED",
        "observed_at":saved["observed_at"],
        "source_age_hours":round((now-at).total_seconds()/3600,2),
        "niche":"","format_key":"","reviewed_by":"","reviewed_at":"",
        "novelty":{"status":"PENDING","differentiation":""},
        "topic_fit":topic,
        "evergreen":mature[:20],
        "entry":entrants[0] if entrants else {"status":"PENDING","fit":"UNKNOWN"},
        "business":{"status":"PENDING","rpm_usd":None,
                    "monthly_views_assumed":None,"monthly_fixed_cost_usd":None,
                    "production_cost_usd_per_video":None,"videos_per_month":None},
        "counts":{"breakout_witness_channels":len(founders),
                  "mature_video_evidence_candidates":len(mature),
                  "new_entrant_evidence_candidates":len(entrants)},
        "source_sha256":_sha(source),
        "instructions":[
            "This is NOT a niche evaluation or source-independent semantic match",
            "Choose a real subniche/format and review source videos before changing PENDING",
            "Evergreen needs TWO independent mature channels in precisely the same subniche",
            "Entry must be a separate newcomer, not the original breakout channel",
            "Model realistic costs, YPP uncertainty, RPM and alternate scenarios",
            "Do not mark rights cleared without verified license/originality review",
        ],
    }
    _write_json(target,result)
    return result
