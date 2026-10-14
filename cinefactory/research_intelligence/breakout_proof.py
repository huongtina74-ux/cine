"""P0 strict breakout evidence auditor for the ONE canonical Company's official data.

A verified breakout channel is NOT a verified niche. Never infer private
revenue/retention, ownership rights or when a video crossed 1M from one snapshot.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .core import _write_json

CHANNEL_ID = re.compile(r"UC[A-Za-z0-9_-]{22}$")
VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}$")
OFFICIAL_SOURCE = {"VERIFIED", "VERIFIED_OFFICIAL_API"}
VALID_FORMATS = {"LONG_FORM", "LONGFORM", "LONG-FORM", "LONG", "STANDARD", "VIDEO"}
HIGH_RIGHTS_RISK_TITLE_PATTERNS = (
    "full movie", "full film", "hindi dubbed", "english dubbed",
    "full episode", "full drama", "movie clips", "movie recap",
    "official full movie", "full match", "football highlights",
)


def _utc(text: str) -> datetime:
    dt = datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Exact timezone-aware UTC evidence required")
    return dt.astimezone(timezone.utc)


def _as_int(value: object) -> int:
    if isinstance(value, bool) or isinstance(value, float) or not str(value).isdigit():
        raise ValueError("Nonnegative exact integer required")
    return int(str(value))


def _url_matches(url: object, video_id: str) -> bool:
    try:
        parsed = urlsplit(str(url))
        if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port:
            return False
        host = (parsed.hostname or "").lower()
        if host in ("www.youtube.com", "youtube.com", "m.youtube.com"):
            return parsed.path == "/watch" and parse_qs(parsed.query).get("v") == [video_id]
        return host == "youtu.be" and parsed.path == "/" + video_id
    except ValueError:
        return False


def audit_official_artifact(source: str | Path, output: str | Path, *,
                            observed_at: str | None = None, min_views: int = 1_000_000,
                            required_videos: int = 2, max_channel_days: int = 30,
                            duration_seconds: int = 480) -> dict:
    """Read an immutable official API artifact; output one conservative channel-level report."""
    src = Path(source).resolve(strict=True)
    payload = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("channels"), dict) or not isinstance(payload.get("catalogs"), dict):
        raise ValueError("Canonical official scan with channels and catalogs required")
    if not 1 <= required_videos <= 10 or min_views < 1000 or duration_seconds < 61 or not 1 <= max_channel_days <= 90:
        raise ValueError("Invalid strict gate threshold")
    evidence_time = _utc(observed_at or payload["generated_at"])
    generation = _utc(payload["generated_at"])
    if not 0 <= (evidence_time - generation).total_seconds() <= 2 * 86400:
        raise ValueError("Cannot evaluate old scan as if views were observed at a later date")
    channels = payload["channels"]
    catalogs = payload["catalogs"]
    if not all(isinstance(key, str) and isinstance(value, list) for key, value in catalogs.items()):
        raise ValueError("Invalid canonical catalog shape")
    # Detect cross-channel and repeated catalog video IDs even if the
    # conflicting record belongs to an OLD channel processed later.
    occurrence_counts: dict[str, int] = {}
    for rows in catalogs.values():
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("video_id"), str):
                ident = row["video_id"]
                occurrence_counts[ident] = occurrence_counts.get(ident, 0) + 1
    conflicted_ids = {ident for ident, n in occurrence_counts.items() if n > 1}
    seen: dict[str, str] = {}
    winners = []
    watchlist = []
    anomalies = []
    counts = {"channels_total": len(channels), "catalog_channels": len(catalogs),
              "channel_age_0_30": 0, "channels_with_two_valid_million_longform": 0,
              "valid_videos": 0, "rejected_video_records": 0,
              "official_channel_records": 0,
              "channels_two_million_within_14_days_proved": 0}
    for channel_id, channel in channels.items():
        if not isinstance(channel, dict):
            anomalies.append({"channel_id": str(channel_id), "reason": "INVALID_CHANNEL_OBJECT"})
            continue
        if (channel.get("evidence_status") not in OFFICIAL_SOURCE or channel.get("channel_id") != channel_id
                or not CHANNEL_ID.fullmatch(channel_id)):
            anomalies.append({"channel_id": channel_id, "reason": "CHANNEL_SOURCE_OR_ID_UNVERIFIED"})
            continue
        counts["official_channel_records"] += 1
        try:
            created = _utc(channel["created_at"])
            age_days = (evidence_time - created).total_seconds() / 86400
            if not 0 <= age_days <= max_channel_days:
                continue
        except (KeyError, ValueError, TypeError):
            anomalies.append({"channel_id": channel_id, "reason": "UNKNOWN_EXACT_CHANNEL_AGE"})
            continue
        counts["channel_age_0_30"] += 1
        valid = []
        risk_markers = set()
        for video in catalogs.get(channel_id, []):
            if not isinstance(video, dict):
                counts["rejected_video_records"] += 1
                continue
            video_id = video.get("video_id")
            if (not isinstance(video_id, str) or not VIDEO_ID.fullmatch(video_id)
                    or video.get("channel_id") != channel_id):
                counts["rejected_video_records"] += 1
                continue
            if video_id in conflicted_ids:
                anomalies.append({"video_id": video_id, "reason": "DUPLICATE_OR_CROSS_CHANNEL_VIDEO"})
                counts["rejected_video_records"] += 1
                continue
            previous_owner = seen.get(video_id)
            if previous_owner is not None:
                anomalies.append({"video_id": video_id, "reason": "DUPLICATE_OR_CROSS_CHANNEL_VIDEO", "channels": [previous_owner, channel_id]})
                counts["rejected_video_records"] += 1
                # Retract original if a second conflicting record appears.
                for item in winners + watchlist:
                    item["witness_videos"] = [v for v in item["witness_videos"] if v["video_id"] != video_id]
                continue
            seen[video_id] = channel_id
            try:
                published = _utc(video["published_at"])
                views = _as_int(video["views"])
                duration = _as_int(video["duration_seconds"])
            except (ValueError, KeyError, TypeError):
                counts["rejected_video_records"] += 1
                continue
            if (video.get("evidence_status") not in OFFICIAL_SOURCE
                    or video.get("format_proxy", "").upper() not in VALID_FORMATS
                    or str(video.get("privacy_status", "public")).lower() != "public"
                    or bool(video.get("is_live")) or bool(video.get("is_short"))
                    or not created <= published <= evidence_time
                    or duration < duration_seconds
                    or views < min_views
                    or not _url_matches(video.get("video_url"), video_id)):
                counts["rejected_video_records"] += 1
                continue
            counts["valid_videos"] += 1
            days_since_publish = (evidence_time - published).total_seconds() / 86400
            title = str(video.get("title") or "")
            risk_markers.update(
                marker for marker in HIGH_RIGHTS_RISK_TITLE_PATTERNS
                if marker in title.casefold()
            )
            valid.append({
                "video_id": video_id, "url": video["video_url"],
                "views_at_observation": views, "published_at": published.isoformat(),
                "published_age_days_at_observation": round(days_since_publish, 3),
                "million_within_14_days_proved": days_since_publish <= 14,
                "title": title,
                "duration_seconds": duration, "source": "official_public_video_metadata",
            })
        valid.sort(key=lambda x: (-x["views_at_observation"], x["video_id"]))
        entry = {
            "channel_id": channel_id, "channel_url": channel.get("channel_url"),
            "created_at": created.isoformat(), "age_days_at_observation": round(age_days, 3),
            "witness_videos": valid, "witness_count": len(valid),
            "two_million_within_14d_proved": sum(v["million_within_14_days_proved"] for v in valid) >= required_videos,
            "rights_risk_markers": sorted(risk_markers),
            "originality_and_rights": "NEEDS_MANUAL_CLEARANCE" if risk_markers else "UNKNOWN_NOT_CLEARED",
            "production_recommendation": "DO_NOT_PRODUCE_WITHOUT_RIGHTS_AND_ORIGINALITY_REVIEW",
            "witness_source": "same_canonical_official_artifact",
        }
        if len(valid) >= required_videos:
            winners.append(entry)
        elif valid:
            watchlist.append(entry)
    # Always rebuild after cross-channel duplicate retractions.
    all_rows = winners + watchlist
    for row in all_rows:
        row["witness_count"] = len(row["witness_videos"])
        row["two_million_within_14d_proved"] = sum(
            v["million_within_14_days_proved"] for v in row["witness_videos"]
        ) >= required_videos
    winners = [row for row in all_rows if len(row["witness_videos"]) >= required_videos]
    watchlist = [row for row in all_rows if 0 < len(row["witness_videos"]) < required_videos]
    counts["channels_with_two_valid_million_longform"] = len(winners)
    counts["channels_two_million_within_14_days_proved"] = sum(
        row["two_million_within_14d_proved"] for row in winners
    )
    winners.sort(key=lambda r: (-r["witness_count"], r["channel_id"]))
    status = "CHANNEL_BREAKOUT_EVIDENCE_PRESENT" if winners else "NO_CONFIRMED_CHANNEL_BREAKOUT"
    report = {
        "schema": "cine.research.official_breakout_audit.v1",
        "state": status, "source_file": str(src),
        "sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        "observed_at": evidence_time.isoformat(), "original_generated_at": generation.isoformat(),
        "thresholds": {"max_channel_age_days": max_channel_days,
                       "required_distinct_videos": required_videos,
                       "min_views_per_video": min_views,
                       "min_duration_seconds": duration_seconds,
                       "exclude_livestreams_shorts": True},
        "counts": counts, "witness_channels": winners,
        "partial_witness_channels": watchlist, "anomalies": anomalies[:200],
        "research_followup_tasks": [
            {"channel_id": row["channel_id"],
             "status": "PENDING_REVIEW",
             "requirements": [
                 "NICHE_AND_DISTINCT_FORMAT_CLASSIFICATION",
                 "MATURE_CHANNEL_RECENT_DEMAND_PROOF",
                 "NEWCOMER_INDEPENDENCE_AND_ENTRY_REVIEW",
                 "RPM_COST_RIGHTS_AND_YPP_FEASIBILITY",
                 "CINECOUNCIL_CROSS_EXAMINATION",
             ],
             "rights_risk_markers": row["rights_risk_markers"],
             "automatically_approved": False} for row in winners
        ],
        "opportunity_niches_verified": 0,
        "final_niche_gate": "NOT_EVALUATED",
        "limitations": [
            "This audit proves channel/video metadata only, not niche-topic match",
            "A same-day public snapshot proves <=14d breakout only if each video is <=14 days old when observed",
            "No evidence of independent evergreen demand, originality, RPM or monetization",
            "Do not carry historical channel age forward to today's daily research",
            "Source integrity does not independently certify the API artifact's authenticity",
        ],
    }
    _write_json(Path(output), report)
    return report
