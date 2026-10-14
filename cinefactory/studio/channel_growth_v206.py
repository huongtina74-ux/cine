"""Owned-channel, provenance-linked learning; never extrapolate competitor RPM.

Only an authenticated GoogleYouTubeOwnedAnalyticsTransport can ingest source
observations here. Static JSON pretending to be a provider response cannot
cause promotion of company production rules.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re

from .channel_franchise_v206 import ChannelLibrary
from .distribution_learning_v205 import ingest_owned_analytics
from .youtube_oauth_transport_v205 import GoogleYouTubeOwnedAnalyticsTransport


def learning_hypothesis(
    channel_strategy, observation: dict
) -> dict:
    """Write an editor-review experiment, never claim statistical causality."""
    if observation.get("schema") != "cine.youtube.owned_observations.v205":
        raise ValueError("SIGNED_OFF_OWNED_ANALYTICS_OBSERVATION_REQUIRED")
    metrics = observation.get("metrics", {})
    if observation.get("learning_promoted") is not False:
        raise ValueError("LEARNING_MUST_BEGIN_UNPROMOTED")
    if not (isinstance(metrics, dict) and isinstance(metrics.get("views"), (int, float))):
        raise ValueError("OWNED_VIEW_COUNT_NOT_OBSERVED")
    hypothesis = channel_strategy.experiment_hypothesis
    status = "PROPOSED_FOR_HUMAN_REVIEW" if hypothesis else "NEEDS_EXPERIMENT_DESIGN"
    return {
        "schema": "cine.channel.learning_candidate.v206",
        "channel_brand_id": channel_strategy.channel_brand_id,
        "series_id": channel_strategy.series_id,
        "episode_id": channel_strategy.episode_id,
        "source_video_id": observation["video_id"],
        "source_master_sha256": observation["master_sha256"],
        "observed_window": [
            observation["window_start"], observation["window_end"],
        ],
        "actual_owned_metrics": dict(metrics),
        "proposed_hypothesis": hypothesis,
        "state": status,
        "causal_claim_verified": False,
        "rules_automatically_updated": False,
        "requires": [
            "repeat observations over multiple episodes",
            "verified traffic source and country mix",
            "creative/editorial independent analysis",
            "controlled format A/B testing before promotion",
        ],
    }


class ChannelOwnedGrowthLedger:
    def __init__(self, canonical_root: str | Path):
        self.library = ChannelLibrary(canonical_root)

    def record_verified_episode(
        self,
        *,
        brand_id: str,
        series_id: str,
        episode_id: str,
        release_receipt: dict,
        transport: GoogleYouTubeOwnedAnalyticsTransport,
    ) -> dict:
        if not isinstance(transport, GoogleYouTubeOwnedAnalyticsTransport):
            raise PermissionError("REAL_OWNER_OAUTH_ANALYTICS_ADAPTER_REQUIRED")
        bible, _ = self.library.load(brand_id)
        strategy = self.library.resolve_episode(brand_id, series_id, episode_id)
        owned_id = bible.verified_youtube_channel_id
        if not owned_id or owned_id != transport.owned_channel_id:
            raise PermissionError("CHANNEL_YOUTUBE_OWNERSHIP_NOT_BOUND")
        if (release_receipt.get("schema") != "cine.youtube.private_upload_verified.v205"
                or release_receipt.get("source") != "LIVE_AUTHORIZED_YOUTUBE_API_READBACK"
                or release_receipt.get("channel_id") != owned_id
                or release_receipt.get("privacy_status") != "private"):
            raise PermissionError("REAL_OWNED_UPLOAD_RECEIPT_REQUIRED")
        video_id = str(release_receipt.get("video_id") or "")
        if not re.fullmatch(r"[A-Za-z0-9_-]{5,50}", video_id):
            raise ValueError("INVALID_OWNED_VIDEO_ID")
        real = transport.fetch_owned_video_metrics(owned_id, video_id)
        observation = ingest_owned_analytics(
            release_receipt, real["metrics"], real["provenance"],
        )
        learning = learning_hypothesis(strategy, observation)
        record = {
            "schema": "cine.channel.authenticated_observation.v206",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "brand_id": brand_id,
            "series_id": series_id,
            "episode_id": episode_id,
            "source_channel_bible_sha256": strategy.source_sha256,
            "observation": observation,
            "learning_candidate": learning,
            "decision": "OBSERVED_NOT_PROMOTED",
            "channel_earnings_claimed": False,
        }
        folder = self.library.path_for(brand_id).parent / "owned_observations"
        folder.mkdir(parents=True, exist_ok=True)
        file_path = folder / (
            video_id + "_" + observation["window_end"].replace("-", "") + ".json"
        )
        # Don't overwrite existing data or allow a second client to
        # fabricate a successful re-read of a stale observation window.
        with file_path.open("x", encoding="utf8") as f:
            f.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        return {"status": "OWNED_OBSERVATION_RECORDED_UNPROMOTED", "path": str(file_path),
                "candidate": learning}
