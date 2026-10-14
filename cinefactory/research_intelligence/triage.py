"""Decision gates: spend deep-analysis budget only on independently promising evidence.

Input must be metadata snapshots supplied by an authorized collector. No YouTube scraping,
subscriber-to-view causality, or private analytics claims.
"""
from __future__ import annotations
import math
from datetime import datetime, timezone
from pathlib import Path
from .core import _write_json

def _utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("Timestamp must be ISO8601")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timezone-aware timestamp required")
    return parsed.astimezone(timezone.utc)

def _age_days(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() / 86400.0

def _valid_video(video: dict, observed: datetime) -> bool:
    try:
        published = _utc(video["published_at"])
        return (
            isinstance(video["video_id"], str) and bool(video["video_id"].strip())
            and isinstance(video["duration_seconds"], (int, float))
            and not isinstance(video["duration_seconds"], bool)
            and math.isfinite(video["duration_seconds"]) and video["duration_seconds"] >= 480
            and isinstance(video["views"], int) and not isinstance(video["views"], bool)
            and video["views"] >= 0 and _age_days(published, observed) >= 0
            and video.get("kind", "video") == "video"
        )
    except (ValueError, KeyError, TypeError, OverflowError):
        return False

def triage_niches(candidates: list[dict], *, max_deep_reviews: int = 3) -> dict:
    """Rank niche opportunities conservatively. No VERIFIED without five documented gates.

    Evidence flags must come from a researcher's validated records, not the scorer's inference.
    """
    if not isinstance(candidates, list) or not 0 <= max_deep_reviews <= 100:
        raise ValueError("Invalid candidates/budget")
    result = []
    for candidate in candidates:
        observed = _utc(candidate["observed_at"])
        name = str(candidate["niche"]).strip()
        if not name:
            raise ValueError("Niche required")
        seen = set()
        qualifying = []
        channel_records = candidate.get("channels", [])
        for channel in channel_records:
            try:
                created = _utc(channel["created_at"])
                age = _age_days(created, observed)
            except (KeyError, ValueError, TypeError):
                continue
            if not 0 <= age <= 30 or not channel.get("channel_id"):
                continue
            breakout_videos = []
            for video in channel.get("videos", []):
                if not _valid_video(video, observed) or video["views"] < 1_000_000:
                    continue
                vid = video["video_id"]
                if vid in seen:
                    continue
                seen.add(vid)
                breakout_videos.append({"video_id": vid, "views": video["views"]})
            if len(breakout_videos) >= 2:
                qualifying.append({"channel_id": channel["channel_id"], "age_days": round(age, 2), "videos": breakout_videos})
        # All five gates are explicit. A high numeric score never overrules missing evidence.
        flags = {
            "distinct_niche_or_format": candidate.get("novel_format_verified") is True,
            "two_1m_longform_on_new_channel": bool(qualifying),
            "durable_recent_demand": candidate.get("recent_evergreen_evidence") is True,
            "business_case_documented": candidate.get("business_case_evidence") is True,
            "newcomer_competition_evidence": candidate.get("newcomer_evidence") is True
        }
        supporting = candidate.get("evidence_urls", [])
        sources_ok = isinstance(supporting, list) and all(isinstance(s, str) and s.startswith(("https://", "http://")) for s in supporting) and len(supporting) >= 2
        score = 20 * int(flags["two_1m_longform_on_new_channel"]) + 20 * int(flags["durable_recent_demand"]) + 20 * int(flags["newcomer_competition_evidence"]) + 15 * int(flags["business_case_documented"]) + 15 * int(flags["distinct_niche_or_format"])
        if sources_ok:
            score += 10
        status = "AUDIT_READY" if all(flags.values()) and sources_ok else "WATCHLIST"
        result.append({"niche": name, "status": status, "score": score, "gates": flags, "source_links_present": sources_ok, "qualifying_channels": qualifying, "missing": [k for k,v in flags.items() if not v] + ([] if sources_ok else ["source_links"]), "deep_review": False})
    result.sort(key=lambda x: (-x["score"], x["niche"]))
    count = 0
    for item in result:
        if item["status"] == "AUDIT_READY" and count < max_deep_reviews:
            item["deep_review"] = True
            count += 1
    return {"schema": "cine.research.triage.v1", "policy": "evidence_before_expense", "max_deep_reviews": max_deep_reviews, "candidates": result, "deep_review_count": count, "note": "Candidate gates require independent source verification; source URLs alone are not proof."}

def triage_to_file(candidates: list[dict], output: str | Path, *, max_deep_reviews: int = 3) -> dict:
    result = triage_niches(candidates, max_deep_reviews=max_deep_reviews)
    _write_json(Path(output), result)
    return result

def select_departments(niche: str) -> list[str]:
    """Only relevant departments; others can be requested after the first review."""
    key = niche.lower()
    if any(s in key for s in ("asmr", "rain", "white noise", "sleep sound")):
        return ["research", "audio", "editorial", "quality"]
    if any(s in key for s in ("minecraft", "roblox", "animation", "long slide", "gta")):
        return ["research", "story", "visual", "animation", "quality"]
    if any(s in key for s in ("podcast", "audiobook", "storytelling")):
        return ["research", "story", "audio", "quality"]
    return ["research", "story", "visual", "quality"]
