"""Read-only follow-up watch for an APPROVED niche pod.

Consumes the SAME market snapshots imported from Company Youtube. No second
collector, no guessed views-per-hour, no competitor private Analytics.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from .core import _write_json
from .market_bridge import verify_imported_company_sources


def _utc(value: str) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamps must include timezone")
    return dt.astimezone(timezone.utc)


def _videos(bridge: dict) -> dict[str, dict]:
    output = {}
    for candidate in bridge.get("candidates", []):
        for channel in candidate.get("channels", []):
            for video in channel.get("videos", []):
                ident = video["video_id"]
                if ident in output and output[ident]["channel_id"] != channel["channel_id"]:
                    raise ValueError("Cross-channel video ID collision")
                output[ident] = {**video, "channel_id": channel["channel_id"],
                                 "channel_age_days": channel.get("age_days"),
                                 "subscribers": channel.get("subscriber_count"),
                                 "channel_url": channel.get("channel_url")}
    return output


def watch_niche(pod: dict, current: dict, destination: str | Path,
                *, previous: dict | None = None, as_of: str | None = None) -> dict:
    if pod.get("schema") != "cine.niche.pod.v1" or pod.get("state") != "CONFIGURED_NOT_SCHEDULED":
        raise ValueError("Matching configured niche pod required")
    if current.get("schema") != "cine.bridge.company_snapshot.v1":
        raise ValueError("Real imported market snapshot required")
    if pod.get("niche") != current.get("niche") or pod.get("format_key") != current.get("format_key"):
        raise ValueError("Cross-niche or cross-format contamination")
    if current.get("source_project") != pod.get("source_company"):
        raise ValueError("Wrong canonical Company data source")
    verify_imported_company_sources(current)
    if previous is not None:
        verify_imported_company_sources(previous)
    at = _utc(as_of) if as_of else datetime.now(timezone.utc)
    current_time = _utc(current["as_of"])
    if not 0 <= (at - current_time).total_seconds() <= 48 * 3600:
        raise ValueError("Current market snapshot too old or future")
    historic = {}
    if previous:
        if (previous.get("schema") != "cine.bridge.company_snapshot.v1"
                or previous.get("niche") != pod["niche"]
                or previous.get("format_key") != pod["format_key"]
                or previous.get("source_project") != current["source_project"]):
            raise ValueError("Previous snapshot must match the SAME niche/format/source")
        previous_at = _utc(previous["as_of"])
        if not previous_at < current_time:
            raise ValueError("Previous snapshot must be strictly earlier")
        historic = _videos(previous)
    videos = _videos(current)
    buckets: dict[tuple[str, str], list[int]] = defaultdict(list)
    for video in videos.values():
        age = (current_time - _utc(video["published_at"])).total_seconds() / 86400
        cohort = "0-2" if age <= 2 else "3-7" if age <= 7 else "8-15" if age <= 15 else "16-30" if age <= 30 else "31-90" if age <= 90 else "90+"
        buckets[(video["channel_id"], cohort)].append(video["views"])
    results = []
    for ident, video in videos.items():
        published_age = (current_time - _utc(video["published_at"])).total_seconds() / 86400
        cohort = "0-2" if published_age <= 2 else "3-7" if published_age <= 7 else "8-15" if published_age <= 15 else "16-30" if published_age <= 30 else "31-90" if published_age <= 90 else "90+"
        sample = buckets[(video["channel_id"], cohort)]
        baseline = median(sample) if len(sample) >= 3 else None
        outlier_ratio = video["views"] / baseline if baseline and baseline > 0 else None
        hour_gain = None
        prev = historic.get(ident)
        if prev:
            # Never infer velocity from total views / lifetime: use two actual snapshots.
            hours = (_utc(video["observed_at"]) - _utc(prev["observed_at"])).total_seconds() / 3600
            if hours > 0 and video["views"] >= prev["views"]:
                hour_gain = round((video["views"] - prev["views"]) / hours, 2)
        subscribers = video.get("subscribers")
        mature = video.get("channel_age_days") is not None and video["channel_age_days"] >= 365
        newcomer = video.get("channel_age_days") is not None and 0 <= video["channel_age_days"] <= 30
        is_leader = mature and isinstance(subscribers, int) and subscribers >= 1_000_000
        checked = video.get("evidence_status", "UNKNOWN").upper() in {"VERIFIED", "SOURCE_VERIFIED", "MANUALLY_VERIFIED"}
        alert = (
            "FRESH_15D_MILLION" if checked and 0 <= published_age <= 15 and video["views"] >= 1_000_000
            else "AGE_MATCHED_OUTLIER" if checked and outlier_ratio is not None and outlier_ratio >= 3 and video["views"] >= 100_000
            else None
        )
        results.append({
            "video_id": ident, "channel_id": video["channel_id"], "video_url": video["source_url"],
            "video_title": video.get("title", ""), "age_days": round(published_age, 3),
            "views": video["views"], "newcomer": newcomer, "million_sub_leader": is_leader,
            "view_velocity_per_hour": hour_gain, "age_cohort": cohort,
            "age_matched_sample_count": len(sample), "outlier_ratio": round(outlier_ratio, 3) if outlier_ratio is not None else None,
            "alert": alert, "evidence_status": video.get("evidence_status", "UNKNOWN"),
        })
    results.sort(key=lambda row: (-int(row["alert"] is not None), -row["views"], row["video_id"]))
    report = {
        "schema": "cine.niche.watch_report.v1",
        "niche_id": pod["niche_id"], "as_of": current["as_of"],
        "source_policy": "read_only_imported_company_snapshots",
        "leader_channels_observed": len({r["channel_id"] for r in results if r["million_sub_leader"]}),
        "newcomer_channels_observed": len({r["channel_id"] for r in results if r["newcomer"]}),
        "fresh_15d_million_videos": sum(r["alert"] == "FRESH_15D_MILLION" for r in results),
        "alerts": [r for r in results if r["alert"]], "videos": results,
        "limitations": [
            "One snapshot is insufficient for genuine view velocity",
            "Age-matched outlier needs >=3 videos in the same channel/cohort; otherwise UNKNOWN",
            "Public sources cannot establish opponent CTR, retention or RPM",
            "This manual analysis does not prove continuous daily monitoring",
        ],
    }
    _write_json(Path(destination), report)
    return report
