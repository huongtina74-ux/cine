"""Convert canonical Company's official-API artifacts into Cine's common CSV vocabulary.

Read original files only; derived artifacts are kept in an isolated new subdirectory
of the same immutable run. Topic fit is explicitly UNKNOWN, never model-inferred.
"""
from __future__ import annotations
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path

from .core import _write_json

CHANNEL_COLUMNS = (
    "snapshot_at", "channel_id", "channel_name", "handle", "channel_url", "created_at",
    "channel_age_days", "channel_age_bucket", "subscriber_count", "total_public_views",
    "public_video_count", "uploads_playlist_id", "country", "language_proxy",
    "description_reviewed", "custom_links_reviewed", "source_mode", "source_url",
    "data_freshness", "evidence_status"
)
VIDEO_COLUMNS = (
    "snapshot_at", "channel_id", "video_id", "video_url", "title", "published_at",
    "video_age_days", "duration_seconds", "format_proxy", "views", "likes", "comments",
    "subscriber_count", "views_per_day", "view_sub_ratio", "channel_median_direct_views",
    "outlier_ratio", "topic_fit", "topic_cluster", "traffic_hypothesis",
    "source_mode", "evidence_status"
)


def _filehash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _write(path: Path, columns: tuple[str, ...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize_company_run(run_dir: str | Path, *, observed_at: str) -> dict:
    run = Path(run_dir).resolve(strict=True)
    moment = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError("Observation time must have timezone")
    channels_file = run / "processed/channel_snapshot_official_api.csv"
    videos_file = run / "processed/fresh_video_observations_clean_official_api.csv"
    output = run / "cine_p1_normalized"
    if output.exists():
        raise FileExistsError("Never overwrite an already normalized snapshot")
    if not channels_file.is_file() or not videos_file.is_file():
        return {"schema": "cine.research.native_adapter.v1", "status": "NOT_COLLECTED",
                "missing_sources": [str(x) for x in (channels_file, videos_file) if not x.is_file()],
                "source_status": "UNKNOWN", "topic_review_required": True,
                "channel_count": 0, "video_count": 0}
    channel_rows = _read(channels_file)
    video_rows = _read(videos_file)
    if not channel_rows or not video_rows:
        return {"schema": "cine.research.native_adapter.v1", "status": "EMPTY_PUBLIC_EVIDENCE",
                "missing_sources": [], "source_status": "UNKNOWN",
                "topic_review_required": True, "channel_count": len(channel_rows),
                "video_count": len(video_rows)}
    normalized_channels = []
    channels_by_id = {}
    for row in channel_rows:
        ident = row.get("channel_id")
        if not ident:
            continue
        official = str(row.get("evidence_status", "")).upper()
        checked = ("OFFICIAL_API" in official or official == "VERIFIED")
        entry = {
            "snapshot_at": observed_at, "channel_id": ident,
            "channel_name": row.get("channel_name", ""),
            "channel_url": row.get("channel_url", ""),
            "created_at": row.get("created_at", ""),
            "channel_age_days": row.get("channel_age_days", ""),
            "channel_age_bucket": row.get("age_bucket", ""),
            "subscriber_count": row.get("subscribers", ""),
            "total_public_views": row.get("total_views", ""),
            "public_video_count": row.get("video_count", ""),
            "uploads_playlist_id": row.get("uploads_playlist_id", ""),
            "country": row.get("country", ""), "source_mode": "OFFICIAL_API_READ_ONLY",
            "source_url": row.get("channel_url", ""),
            "data_freshness": "CURRENT_RUN",
            "evidence_status": "SOURCE_VERIFIED" if checked else "UNKNOWN",
        }
        if ident in channels_by_id:
            raise ValueError("Duplicate channel IDs in canonical artifact")
        channels_by_id[ident] = entry
        normalized_channels.append(entry)
    normalized_videos = []
    seen = set()
    for row in video_rows:
        ident = row.get("video_id")
        channel_id = row.get("channel_id")
        if not ident or not channel_id or channel_id not in channels_by_id:
            continue
        if ident in seen:
            raise ValueError("Repeated video ID in canonical artifact")
        seen.add(ident)
        fmt = str(row.get("format_proxy", "")).lower()
        if "short" in fmt or "live" in fmt:
            kind = "SHORTS_OR_LIVE"
        elif "long" in fmt:
            kind = "LONG_FORM"
        else:
            kind = "UNKNOWN"
        official = str(row.get("evidence_status", "")).upper()
        checked = "VERIFIED" in official and channels_by_id[channel_id]["evidence_status"] == "SOURCE_VERIFIED"
        normalized_videos.append({
            "snapshot_at": observed_at, "channel_id": channel_id,
            "video_id": ident, "video_url": row.get("video_url", ""),
            "title": row.get("title", ""), "published_at": row.get("published_at", ""),
            "video_age_days": row.get("video_age_days", ""),
            "duration_seconds": row.get("duration_seconds", ""), "format_proxy": kind,
            "views": row.get("views", ""), "subscriber_count": channels_by_id[channel_id]["subscriber_count"],
            "topic_cluster": row.get("seed_cluster", "") or row.get("broad_market", ""),
            "topic_fit": "UNKNOWN",
            "source_mode": "OFFICIAL_API_READ_ONLY",
            "evidence_status": "SOURCE_VERIFIED" if checked else "UNKNOWN",
        })
    if not normalized_channels or not normalized_videos:
        return {"schema": "cine.research.native_adapter.v1", "status": "EMPTY_PUBLIC_EVIDENCE",
                "source_status": "UNKNOWN", "topic_review_required": True,
                "missing_sources": [], "channel_count": len(normalized_channels),
                "video_count": len(normalized_videos)}
    output.mkdir(parents=True, exist_ok=False)
    channel_out = output / "niche_radar_channel_snapshot.csv"
    video_out = output / "niche_radar_video_snapshot.csv"
    _write(channel_out, CHANNEL_COLUMNS, normalized_channels)
    _write(video_out, VIDEO_COLUMNS, normalized_videos)
    record = {
        "schema": "cine.research.native_adapter.v1",
        "status": "SCHEMA_READY_TOPIC_REVIEW_REQUIRED",
        "channel_count": len(normalized_channels),
        "video_count": len(normalized_videos),
        "topic_review_required": True,
        "claimed_niches_qualified": 0,
        "channels": {"path": str(channel_out), "sha256": _filehash(channel_out)},
        "videos": {"path": str(video_out), "sha256": _filehash(video_out)},
        "native_sources": {
            "channels": {"path": str(channels_file), "sha256": _filehash(channels_file)},
            "videos": {"path": str(videos_file), "sha256": _filehash(videos_file)},
        },
        "limitations": [
            "No semantic topic fit is inferred from keyword seed",
            "Official public metadata source status is NOT owner verification",
            "Niche evergreen, independent entry and monetization require explicit research review",
        ],
    }
    _write_json(output / "native_adapter_manifest.json", record)
    return record
