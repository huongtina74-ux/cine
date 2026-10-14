"""P0 candidate-first filter over the canonical Company's existing youtubei.js outputs.

NO API calls here. Approximate text views / date-only joined timestamps remain
PROVISIONAL, even when the source labels its public HTML collection VERIFIED.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .core import _write_json

CID = re.compile(r"UC[A-Za-z0-9_-]{22}$")
VID = re.compile(r"[A-Za-z0-9_-]{11}$")
RISK_TERMS = ("full movie", "full film", "hindi dubbed", "english dubbed",
              "full episode", "full drama", "movie clips", "movie recap", "reupload")


def _datetime(s: str) -> datetime:
    dt = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("source timestamp must have timezone")
    return dt.astimezone(timezone.utc)


def _read(path: Path, field: str) -> dict:
    x = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(x, dict) or not isinstance(x.get(field), list):
        raise ValueError(f"Malformed {field} collection")
    return x


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _int(value: object) -> int | None:
    if isinstance(value, bool) or not str(value).isdigit():
        return None
    return int(str(value))


def _channel_created(raw: str, observed: datetime) -> tuple[float | None, float | None]:
    try:
        dt = datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        # Day-only source: range for age is 1 day wide; never exact enough for hard gate.
        age_max = (observed - dt).total_seconds() / 86400
        return round(age_max - 1, 3), round(age_max, 3)
    except ValueError:
        return None, None


DISPLAY_VIEWS = re.compile(
    r"^\s*(\d[\d,]*(?:\.\d+)?)\s*([KMB])?\s+views?\s*$",
    flags=re.IGNORECASE
)


DISPLAY_BARE_VIEWS = re.compile(
    r"^\s*(\d[\d,]*(?:\.\d+)?)\s*([KMB])?\s*$", flags=re.IGNORECASE
)
VALID_AGE_LABEL = re.compile(
    r"^\s*\d+\s*(?:[smhdwy]|seconds?|minutes?|hours?|days?|weeks?|months?|years?)\s+ago\s*$",
    flags=re.IGNORECASE
)


def _valid_display_views(text: object, parsed: int, age_text: object = None) -> bool:
    """Require explicit 'views' OR a bare numeric value paired with posting age."""
    match = DISPLAY_VIEWS.fullmatch(str(text or ""))
    if not match and VALID_AGE_LABEL.fullmatch(str(age_text or "")):
        match = DISPLAY_BARE_VIEWS.fullmatch(str(text or ""))
    if not match:
        return False
    number = float(match.group(1).replace(",", ""))
    multiplier = {"":1, "K":1000, "M":1_000_000, "B":1_000_000_000}[match.group(2).upper() if match.group(2) else ""]
    return round(number*multiplier)==parsed


def _catalog_vids(rows: list[dict]) -> list[dict]:
    result = []
    ids = set()
    for v in rows:
        if not isinstance(v, dict):
            continue
        vid = v.get("video_id")
        if not isinstance(vid, str) or not VID.fullmatch(vid) or vid in ids:
            continue
        ids.add(vid)
        duration = _int(v.get("duration_seconds"))
        views = _int(v.get("views"))
        if (not duration or duration < 480 or views is None
                or str(v.get("format_proxy", "")).upper() != "LONG_FORM"
                or not _valid_display_views(v.get("views_text"), views, v.get("age_text"))):
            continue
        url = str(v.get("video_url") or "")
        if url != "https://www.youtube.com/watch?v=" + vid:
            continue
        title = str(v.get("title") or "")
        result.append({
            "video_id": vid, "video_url": url, "title": title,
            "approx_views": views, "displayed_views": str(v.get("views_text") or ""),
            "duration_seconds": duration, "video_age_days_proxy": v.get("video_age_days"),
            "risk_markers": [term for term in RISK_TERMS if term in title.casefold()],
            "views_are_exact": False,
        })
    return sorted(result, key=lambda a: (-a["approx_views"], a["video_id"]))


def prescreen_company_public(company_root: str | Path, run_dir: str | Path,
                             output: str | Path, *, as_of: str | None = None,
                             max_candidates: int = 20, min_near_views: int = 700_000) -> dict:
    root = Path(company_root).resolve(strict=True)
    run = Path(run_dir).resolve(strict=True)
    if not run.is_relative_to(root):
        raise ValueError("Canonical public artifacts must be inside Company Youtube")
    if not 1 <= max_candidates <= 100 or not 100_000 <= min_near_views <= 1_000_000:
        raise ValueError("Unsupported candidate budget")
    original_surface = run / "raw/lane_b_broad_market_surface.json"
    refined = run / "raw/lane_b_broad_market_surface_rechecked.json"
    surface = refined if refined.is_file() else original_surface
    catalogs = run / "raw/lane_b_age_1_90_catalogs.json"
    if not surface.is_file() or not catalogs.is_file():
        return {"schema":"cine.research.public_prescreen.v1", "state":"NOT_COLLECTED",
                "missing":[str(p) for p in (surface, catalogs) if not p.is_file()],
                "requests_for_official_verification":[], "candidates":[]}
    s = _read(surface, "observations")
    if surface == refined:
        lineage = s.get("about_recheck_lineage",{})
        if (not isinstance(lineage,dict) or not original_surface.is_file()
            or lineage.get("original_surface_sha256")!=_sha(original_surface)):
            raise ValueError("Refined public surface lineage does not match original")
    c = _read(catalogs, "channels")
    age_review = run / "processed/lane_b_unknown_age_catalog_age_review.json"
    age_triage = run / "processed/lane_b_unknown_age_catalog_triage.json"
    age_lookup = run / "raw/lane_b_unknown_age_after_catalog_about.json"
    age_catalog = run / "raw/lane_b_unknown_age_catalogs.json"
    unknown_report = None
    if age_review.exists():
        if not (age_triage.is_file() and age_lookup.is_file() and age_catalog.is_file()):
            raise ValueError("Incomplete unknown-age catalog review chain")
        unknown_report = _read(age_review,"channels")
        triage_payload = _read(age_triage,"triage")
        if (unknown_report.get("schema")!="cine.company.unknown_age_catalog_age_review.v1"
            or unknown_report.get("triage_sha256")!=_sha(age_triage)
            or unknown_report.get("about_sha256")!=_sha(age_lookup)
            or triage_payload.get("catalog_sha256")!=_sha(age_catalog)
            or unknown_report.get("official_data_api_verified") is not False
            or unknown_report.get("qualified_niches") != 0
            or unknown_report.get("owner_approval_allowed") is not False):
            raise ValueError("Untrusted unknown-age review or invalid evidence lineage")
    s_time = _datetime(s["generated_at"])
    c_time = _datetime(c["generated_at"])
    when = _datetime(as_of) if as_of else datetime.now(timezone.utc)
    if abs((s_time-c_time).total_seconds()) > 48*3600:
        raise ValueError("Public surface and catalogs are from incompatible run dates")
    if (when-c_time).total_seconds() < -300:
        raise ValueError("Public data is from the future")
    age_h = (when-max(s_time,c_time)).total_seconds()/3600
    current = 0 <= age_h <= 48
    rows_by_channel: dict[str, list[dict]] = {}
    for x in s["observations"]:
        if isinstance(x, dict) and isinstance(x.get("channel_id"),str) and CID.fullmatch(x["channel_id"]):
            rows_by_channel.setdefault(x["channel_id"],[]).append(x)
    global_video_owners: dict[str,set[str]] = {}
    for x in c["channels"]:
        if not isinstance(x,dict):
            continue
        cid = x.get("channel_id")
        if not isinstance(cid,str) or not CID.fullmatch(cid):
            continue
        for v in x.get("videos") or []:
            if isinstance(v,dict) and isinstance(v.get("video_id"),str):
                global_video_owners.setdefault(v["video_id"],set()).add(cid)
    conflicted = {vid for vid,ids in global_video_owners.items() if len(ids)>1}
    invalid_view_display = [
        {"channel_id":str(x.get("channel_id") or ""), "video_id":str(v.get("video_id") or ""),
         "parsed_views":v.get("views"), "raw_view_text":str(v.get("views_text") or "")[:120]}
        for x in c["channels"] if isinstance(x,dict)
        for v in (x.get("videos") or []) if isinstance(v,dict)
        if (_int(v.get("views")) or 0) >= min_near_views
           and not _valid_display_views(v.get("views_text"), _int(v.get("views")), v.get("age_text"))
    ]
    candidates = []
    seen_channels = set()
    for catalog in c["channels"]:
        if not isinstance(catalog,dict):
            continue
        cid = catalog.get("channel_id")
        if (not isinstance(cid,str) or not CID.fullmatch(cid) or cid in seen_channels
                or catalog.get("collection_status") != "VERIFIED"):
            continue
        seen_channels.add(cid)
        public = rows_by_channel.get(cid,[])
        if not public:
            continue
        # The About 'joined_date' is calendar-day resolution only.
        joined = sorted({str(x.get("joined_date") or "") for x in public if x.get("joined_date")})
        if len(joined) != 1:
            continue
        min_age,max_age = _channel_created(joined[0],c_time)
        if min_age is None or min_age > 32 or max_age < -1:
            continue
        videos = [v for v in _catalog_vids(catalog.get("videos") or []) if v["video_id"] not in conflicted]
        if not videos:
            continue
        about = public[0]
        full_million = [v for v in videos if v["approx_views"] >= 1_000_000]
        near_million = [v for v in videos if v["approx_views"] >= min_near_views]
        level = ("TWO_DISPLAY_MILLION" if len(full_million)>=2
                 else "TWO_NEAR_MILLION" if len(near_million)>=2
                 else "SINGLE_DISPLAY_MILLION" if len(full_million)==1
                 else "BELOW_TWO_SIGNAL")
        risk = sorted({t for v in videos for t in v["risk_markers"]})
        candidates.append({
            "channel_id": cid, "channel_name": about.get("channel_name") or catalog.get("channel") or "",
            "channel_url": "https://www.youtube.com/channel/"+cid,
            "joined_date_proxy": joined[0],
            "age_days_range_at_collection": [min_age,max_age],
            "about_evidence": "PUBLIC_ABOUT_DAY_PRECISION_ONLY",
            "catalog_collection_status": catalog.get("collection_status","UNKNOWN"),
            "level": level, "near_million_video_count":len(near_million),
            "display_million_video_count":len(full_million),
            "longform_catalog_count":len(videos), "videos":videos[:12],
            "risk_markers":risk, "rights_status":"NEEDS_RIGHTS_REVIEW",
            "niche": "UNKNOWN_REQUIRES_SEMANTIC_ANALYSIS",
            "verification_state":"PROVISIONAL_PUBLIC_SOURCE",
            "source_queries":list(dict.fromkeys(str(x.get("query") or "") for x in public))[:6],
        })
    rank={"TWO_DISPLAY_MILLION":0,"TWO_NEAR_MILLION":1,"SINGLE_DISPLAY_MILLION":2,"BELOW_TWO_SIGNAL":3}
    candidates.sort(key=lambda x:(rank[x["level"]],-x["display_million_video_count"],
                                  -x["near_million_video_count"],
                                  -sum(v["approx_views"] for v in x["videos"][:2]),x["channel_id"]))
    selected = candidates[:max_candidates]
    queue=[]
    for item in selected:
        if item["level"] not in ("TWO_DISPLAY_MILLION","TWO_NEAR_MILLION"):
            continue
        witnesses=[v["video_id"] for v in item["videos"] if v["approx_views"] >= min_near_views][:4]
        if len(witnesses)<2:
            continue
        queue.append({"channel_id":item["channel_id"], "video_ids":witnesses,
                      "priority":item["level"], "stage":"NEEDS_EXACT_OFFICIAL_METADATA",
                      "why":"Public dates/rounded views and video ownership need exact verification",
                      "required_source":"YOUTUBE_DATA_API_CHANNELS_AND_VIDEOS_LIST"})
    unknown_watch=unknown_report["channels"] if unknown_report is not None else []
    unknown_high_signal=[x for x in unknown_watch if x.get("two_million_longform_proxy") is True]
    catalog_attempts=len(c["channels"])
    catalog_usable=sum(1 for x in c["channels"] if isinstance(x,dict) and
                       x.get("collection_status")=="VERIFIED")
    about_lookup_count=_int(s.get("about_lookup_channel_count"))
    public_unique_count=_int(s.get("unique_channel_count")) or len(rows_by_channel)
    about_coverage=(round(about_lookup_count/public_unique_count,4)
                    if about_lookup_count is not None and public_unique_count else None)
    source_table={"surface":{"path":str(surface),"sha256":_sha(surface)},
                  "catalogs":{"path":str(catalogs),"sha256":_sha(catalogs)}}
    if unknown_report is not None:
        source_table["unknown_age_review"]={"path":str(age_review),"sha256":_sha(age_review)}
    result={
        "schema":"cine.research.public_prescreen.v1",
        "state":("PROVISIONAL_QUEUE_READY" if queue and current
                 else "HISTORICAL_ONLY" if not current
                 else "INSUFFICIENT_CATALOG_COVERAGE" if not catalog_usable
                 else "NO_PROMISING_PUBLIC_CANDIDATES"),
        "collection_at":c_time.isoformat(), "as_of":when.isoformat(),
        "fresh_for_daily":current, "age_hours":round(age_h,2),
        "sources":source_table,
        "counts":{"public_channels_seen":len(rows_by_channel),
                  "unique_channel_count":public_unique_count,
                  "about_lookup_channels":about_lookup_count,
                  "about_lookup_coverage_fraction":about_coverage,
                  "catalog_channels":catalog_attempts,
                  "verified_catalog_channels":catalog_usable,
                  "unknown_age_catalog_review_channels":len(unknown_watch),
                  "unknown_age_two_million_proxy_channels":len(unknown_high_signal),
                  "unknown_age_age_verified_public_two_million_proxy":(
                      unknown_report["candidate_public_two_million_and_age_window"]
                      if unknown_report is not None else None),
                  "screened_channels":len(candidates),
                  "two_display_million_channels":sum(x["level"]=="TWO_DISPLAY_MILLION" for x in candidates),
                  "two_near_million_channels":sum(x["level"]=="TWO_NEAR_MILLION" for x in candidates),
                  "queued_channels":len(queue),
                  "conflicted_public_video_ids":len(conflicted),
                  "suspected_false_viral_view_labels":len(invalid_view_display)},
        "rejected_view_text_samples":invalid_view_display[:10],
        "candidates":selected, "requests_for_official_verification":queue,
        "unknown_age_research_watchlist":[
            {"channel_id":x["channel_id"],"public_age_status":x["status"],
             "longform_two_million_display_proxy":True,
             "official_proof":False,"owner_approval_eligible":False}
            for x in unknown_high_signal[:12]
        ],
        "qualified_niches":0, "eligible_for_cinecouncil_approval":False,
        "coverage_status":"INSUFFICIENT_PUBLIC_VIDEO_CATALOGS" if not catalog_usable else "PUBLIC_CATALOG_SAMPLE_ONLY",
        "limitations":[
            "youtubei.js public metadata is unofficial and view counts are rounded display values",
            "About lookups are budgeted; unexamined channel ages cannot be treated as older or non-winning",
            "About joined date is day-precision only; membership in 0-30d is provisional",
            "No official API request performed; never claim any candidate VERIFIED",
            "No semantic niche fit, evergreen demand, YPP eligibility or RPM evidence",
            "Historical source must never be presented as a current opportunity",
        ]
    }
    _write_json(Path(output),result)
    return result
