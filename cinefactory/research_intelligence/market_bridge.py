"""Read-only evidence bridge: Company Youtube -> CineFactory.

Does NOT launch another scanner. Imports the existing niche_radar CSV contract.
It never treats a self-declared CSV flag as proof of a verified market fact.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
from urllib.parse import parse_qs, urlsplit
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .core import _write_json
from .triage import triage_niches

CHANNEL_REQUIRED = {
    "snapshot_at", "channel_id", "created_at", "channel_url", "evidence_status"
}
VIDEO_REQUIRED = {
    "snapshot_at", "channel_id", "video_id", "video_url", "published_at",
    "duration_seconds", "format_proxy", "views", "topic_cluster", "topic_fit",
    "evidence_status"
}
ALLOWED_VIDEO_FORMATS = {"video", "long", "longform", "long-form", "standard"}
ALLOWED_TOPIC_FIT = {"direct", "direct_match", "exact"}
SOURCE_CHECKED = {"VERIFIED", "SOURCE_VERIFIED", "MANUALLY_VERIFIED"}


def _utc(value: str) -> datetime:
    if not value or not isinstance(value, str):
        raise ValueError("Missing timestamp")
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("All evidence timestamps need timezone")
    return parsed.astimezone(timezone.utc)


def _rows(path: Path, required: set[str]) -> tuple[list[dict[str, str]], str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    content = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(f"Missing required schema fields in {path.name}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"No usable rows in {path.name}")
    return rows, hashlib.sha256(content).hexdigest()


def _int(value: str, field: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+", value.strip()):
        raise ValueError(f"Invalid {field}: {value!r}")
    return int(value.strip())


def _date_age(born: str, as_of: datetime) -> float:
    return (as_of - _utc(born)).total_seconds() / 86400


def _fresh(recorded: str, as_of: datetime, max_hours: int) -> bool:
    seconds = (as_of - _utc(recorded)).total_seconds()
    return 0 <= seconds <= max_hours * 3600


def _video_link_matches(url: str, video_id: str) -> bool:
    if not isinstance(video_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        return False
    parsed = urlsplit(str(url))
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port:
        return False
    host = (parsed.hostname or "").lower()
    if host in {"youtube.com", "www.youtube.com", "m.youtube.com"}:
        return parsed.path == "/watch" and parse_qs(parsed.query).get("v") == [video_id]
    return host == "youtu.be" and parsed.path == "/" + video_id


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").casefold()).strip("-")


def _assert_child(file: Path, root: Path) -> Path:
    path = file.resolve(strict=True)
    if not path.is_relative_to(root.resolve(strict=True)):
        raise ValueError("Source must remain inside the canonical Company Youtube project")
    return path


def _sources_for_review(review: dict, field: str, when: datetime) -> list[dict]:
    record = review.get(field, {})
    registry = review.get("source_register", {})
    if not isinstance(record, dict) or record.get("supported") is not True or not isinstance(registry, dict):
        return []
    ids = record.get("source_ids")
    if not isinstance(ids, list) or len(ids) != len(set(ids)) or not ids:
        return []
    sources = []
    for ident in ids:
        if not isinstance(ident, str) or ident not in registry or not isinstance(registry[ident], dict):
            return []
        src = registry[ident]
        if src.get("status") != "REVIEWED" or not src.get("reviewed_by"):
            return []
        url = src.get("url")
        if not isinstance(url, str) or not url.startswith("https://") or not urlsplit(url).hostname:
            return []
        try:
            age_days = (when - _utc(src["observed_at"])).total_seconds() / 86400
        except (ValueError, KeyError, TypeError):
            return []
        if not 0 <= age_days <= 30:
            return []
        sources.append(src)
    return sources


def _format_new(niche: str, format_key: str, existing: list[dict[str, str]],
                review: dict, when: datetime) -> bool:
    sources = _sources_for_review(review, "novelty", when)
    if not sources or not all(s.get("type") == "format_review" for s in sources):
        return False
    overlap = [
        x for x in existing
        if _slug(niche) in {_slug(x.get("niche", "")), *(_slug(a) for a in x.get("aliases", []))}
    ]
    if not overlap:
        return True
    previous = {_slug(x.get("format_key", "")) for x in overlap}
    return (_slug(format_key) not in previous and _slug(format_key) not in ("", "default")
            and bool(review.get("novelty", {}).get("differentiation")))


def _gate_review(review: dict, field: str, when: datetime) -> bool:
    sources = _sources_for_review(review, field, when)
    if not sources:
        return False
    if field == "durable":
        if len(sources) < 2 or len({s.get("channel_id") for s in sources}) < 2:
            return False
        for src in sources:
            try:
                created_age = _date_age(src["channel_created_at"], when)
                video_age = _date_age(src["video_published_at"], when)
                views = int(src["video_views"])
            except (ValueError, KeyError, TypeError):
                return False
            if src.get("type") != "mature_recent" or created_age < 365 or not 0 <= video_age <= 90 or views < 100_000:
                return False
        return True
    if field == "entry":
        # One independently checked new entrant is the minimum; multiple are better.
        for src in sources:
            try:
                age = _date_age(src["channel_created_at"], when)
                views = int(src["video_views"])
            except (ValueError, KeyError, TypeError):
                continue
            if src.get("type") == "new_entrant" and 0 <= age <= 30 and views >= 100_000 and src.get("channel_id"):
                return True
        return False
    if field == "business":
        for src in sources:
            try:
                rpm = float(src["rpm_usd"])
                monthly_views = float(src["monthly_views_assumed"])
            except (ValueError, KeyError, TypeError):
                continue
            # Minimum plausible multi-thousand-dollar *scenario*, never actual earnings.
            if (src.get("type") == "revenue_scenario" and 0 < rpm <= 100
                    and 0 < monthly_views <= 1e10 and rpm * monthly_views / 1000 >= 2_000):
                return True
        return False
    return False


def import_company_snapshot(company_root: str | Path, channel_csv: str | Path, video_csv: str | Path,
                            output: str | Path, *, niche: str, format_key: str,
                            review: dict | None = None, existing_niches: list[dict] | None = None,
                            as_of: str | None = None, max_snapshot_age_hours: int = 48) -> dict:
    """No network; no Company Youtube mutations; preserve UNKNOWN instead of manufacturing proof."""
    if not isinstance(niche, str) or not niche.strip() or not _slug(niche):
        raise ValueError("Niche required")
    if not isinstance(format_key, str) or not _slug(format_key):
        raise ValueError("Format key required")
    if not 1 <= max_snapshot_age_hours <= 720:
        raise ValueError("Invalid snapshot freshness window")
    root = Path(company_root).resolve(strict=True)
    when = _utc(as_of) if as_of else datetime.now(timezone.utc)
    channel_path = _assert_child(Path(channel_csv), root)
    video_path = _assert_child(Path(video_csv), root)
    channel_rows, channel_hash = _rows(channel_path, CHANNEL_REQUIRED)
    video_rows, video_hash = _rows(video_path, VIDEO_REQUIRED)
    channels: dict[str, dict[str, Any]] = {}
    seen_channels: set[tuple[str, str]] = set()
    for row in channel_rows:
        channel_id, sampled = row["channel_id"].strip(), row["snapshot_at"]
        if not channel_id or (channel_id, sampled) in seen_channels:
            raise ValueError("Duplicated or missing channel observation")
        seen_channels.add((channel_id, sampled))
        if not _fresh(sampled, when, max_snapshot_age_hours):
            continue
        age = _date_age(row["created_at"], when) if row.get("created_at") else -1
        record = {"channel_id": channel_id, "created_at": row.get("created_at"),
                  "channel_url": row.get("channel_url"), "age_days": round(age, 3),
                  "channel_name": row.get("channel_name", ""),
                  "subscriber_count": int(row["subscriber_count"]) if (row.get("subscriber_count") or "").isdigit() else None,
                  "observed_at": sampled, "evidence_status": row.get("evidence_status", "UNKNOWN"),
                  "videos": []}
        previous = channels.get(channel_id)
        if previous is None or _utc(previous["observed_at"]) < _utc(sampled):
            channels[channel_id] = record
    if not channels:
        raise ValueError("No fresh channel observation; do not reuse stale snapshots")
    selected_videos: dict[str, dict] = {}
    invalid_videos: list[dict] = []
    for row in video_rows:
        video_id = (row.get("video_id") or "").strip()
        channel_id = (row.get("channel_id") or "").strip()
        sampled = row.get("snapshot_at") or ""
        if channel_id not in channels or not _fresh(sampled, when, max_snapshot_age_hours):
            continue
        previous = selected_videos.get(video_id)
        if previous is not None and previous["channel_id"] != channel_id:
            raise ValueError("Video ID is attached to multiple channel IDs")
        if previous is not None and _utc(previous["snapshot_at"]) == _utc(sampled) and previous != row:
            raise ValueError("Conflicting metadata snapshots for same video/time")
        if previous is None or _utc(previous["snapshot_at"]) < _utc(sampled):
            selected_videos[video_id] = row
    candidate_links = []
    for video_id, row in selected_videos.items():
        try:
            duration = _int(row["duration_seconds"], "duration")
            views = _int(row["views"], "views")
            published = _utc(row["published_at"])
            fmt = _slug(row.get("format_proxy", ""))
            fit = _slug(row.get("topic_fit", ""))
            matches = _slug(row.get("topic_cluster", "")) == _slug(niche)
            channel_created = _utc(channels[row["channel_id"]]["created_at"])
            is_valid = (
                bool(video_id) and duration >= 480 and fmt in {_slug(v) for v in ALLOWED_VIDEO_FORMATS}
                and fit in {_slug(v) for v in ALLOWED_TOPIC_FIT} and matches
                and channel_created <= published <= when
                and _video_link_matches(row.get("video_url", ""), video_id)
            )
        except (KeyError, ValueError, TypeError):
            is_valid = False
        if not is_valid:
            invalid_videos.append({"video_id": video_id, "reason": "invalid_duration_format_topic_date_or_url"})
            continue
        channels[row["channel_id"]]["videos"].append({
            "video_id": video_id, "published_at": published.isoformat(),
            "duration_seconds": duration, "views": views, "kind": "video",
            "source_url": row["video_url"], "observed_at": row["snapshot_at"],
            "title": row.get("title", ""), "topic_cluster": row.get("topic_cluster", ""),
            "evidence_status": row.get("evidence_status", "UNKNOWN"),
        })
        candidate_links.append(row["video_url"])
    review = review or {}
    if existing_niches is not None and not isinstance(existing_niches, list):
        raise ValueError("Malformed portfolio registry")
    baseline = json.loads((Path(__file__).with_name("known_niches.json")).read_text(encoding="utf-8"))
    existing_niches = baseline + (existing_niches or [])
    if not isinstance(review, dict):
        raise ValueError("Malformed review packet")
    flags = {
        "novel_format_verified": _format_new(niche, format_key, existing_niches, review, when),
        "recent_evergreen_evidence": _gate_review(review, "durable", when),
        "business_case_evidence": _gate_review(review, "business", when),
        "newcomer_evidence": _gate_review(review, "entry", when),
    }
    # The selected CSV is public metadata only. Review assertions remain separate.
    candidate = {
        "niche": niche, "format_key": format_key, "observed_at": when.isoformat(),
        "channels": list(channels.values()),
        "evidence_urls": list(dict.fromkeys(candidate_links)),
        **flags,
    }
    # A raw snapshot labelled UNKNOWN cannot silently become proof of two million-view uploads.
    qualified_channel_ids = {
        c["channel_id"] for c in candidate["channels"]
        if c["evidence_status"].upper() in SOURCE_CHECKED
    }
    qualifying_input = {
        **candidate, "channels": [
            {**channel, "videos": [
                video for video in channel["videos"]
                if video["evidence_status"].upper() in SOURCE_CHECKED
            ]}
            for channel in candidate["channels"] if channel["channel_id"] in qualified_channel_ids
        ]
    }
    triage = triage_niches([qualifying_input], max_deep_reviews=1)["candidates"][0]
    result = {
        "schema": "cine.bridge.company_snapshot.v1",
        "source_project": str(root), "source_policy": "company_youtube_read_only",
        "channel_source": {"path": str(channel_path), "sha256": channel_hash},
        "video_source": {"path": str(video_path), "sha256": video_hash},
        "niche": niche, "format_key": format_key, "as_of": when.isoformat(),
        "triage": triage, "review_flags": flags,
        "channels_sampled": len(channels), "videos_sampled": len(selected_videos),
        "excluded_videos": invalid_videos,
        "candidates": [candidate],
        "limitations": [
            "AUDIT_READY is not an independently verified niche; public snapshot values may be untrue",
            "Review assertions need independent human/source authentication before final approval",
            "No new YouTube data is collected by this bridge",
        ]
    }
    _write_json(Path(output), result)
    return result


def verify_imported_company_sources(bridge: dict) -> bool:
    """Verify current CSV lineage against the canonical read-only source files."""
    if bridge.get("schema") != "cine.bridge.company_snapshot.v1":
        raise ValueError("Imported Company snapshot contract required")
    root = Path(bridge["source_project"]).resolve(strict=True)
    sources={}
    for key in ("channel_source", "video_source"):
        source = bridge.get(key) or {}
        path = _assert_child(Path(source.get("path", "")), root)
        if hashlib.sha256(path.read_bytes()).hexdigest() != source.get("sha256"):
            raise ValueError(f"Company evidence file was changed: {key}")
        sources[key]=path
    # Hashes bind only source FILES, not the editable claims within the bridge.
    from .bridge_integrity import verify_bridge_semantics
    verify_bridge_semantics(bridge,sources["channel_source"],sources["video_source"])
    return True
