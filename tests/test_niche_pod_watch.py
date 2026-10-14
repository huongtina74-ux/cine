from datetime import datetime, timedelta, timezone
import json

import pytest

from cinefactory.research_intelligence.pod_watch import watch_niche

NOW = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)


def ts(days=0):
    return (NOW - timedelta(days=days)).isoformat()


def sample(when=0):
    at = ts(when)
    video = lambda vid, view, age: {
        "video_id": vid, "views": view, "published_at": ts(age),
        "observed_at": at, "source_url": f"https://youtube.com/watch?v={vid}",
        "title": "Original test video", "evidence_status": "VERIFIED"
    }
    return {
        "schema": "cine.bridge.company_snapshot.v1", "niche": "Minecraft animation",
        "format_key": "custom-stage", "source_project": "C:/Company Youtube", "as_of": at,
        "candidates": [{"channels": [
            {"channel_id": "UCnew", "channel_url": "https://youtube.com/channel/UCnew",
             "age_days": 10, "subscriber_count": 8000,
             "videos": [video("ABCdef12345", 1350000 if when == 0 else 1200000, 4)]},
            {"channel_id": "UCmature", "channel_url": "https://youtube.com/channel/UCmature",
             "age_days": 1000, "subscriber_count": 2500000,
             "videos": [video("CDEfgh12345", 900000, 18), video("DEFghi12345", 120000, 19),
                        video("EFGhij12345", 100000, 17)]}
        ]}]
    }


def pod():
    return {
        "schema": "cine.niche.pod.v1", "state": "CONFIGURED_NOT_SCHEDULED",
        "niche": "Minecraft animation", "format_key": "custom-stage",
        "niche_id": "minecraft-animation--custom-stage",
        "source_company": "C:/Company Youtube"
    }


def test_manual_watcher_recognizes_fresh_viral_and_leader_outlier(tmp_path):
    report = watch_niche(pod(), sample(), tmp_path / "watch.json", as_of=ts())
    assert report["fresh_15d_million_videos"] == 1
    assert report["leader_channels_observed"] == 1
    assert report["newcomer_channels_observed"] == 1
    leader = next(row for row in report["videos"] if row["video_id"] == "CDEfgh12345")
    assert leader["alert"] == "AGE_MATCHED_OUTLIER"
    assert leader["outlier_ratio"] == 7.5
    assert leader["view_velocity_per_hour"] is None
    assert json.loads((tmp_path / "watch.json").read_text(encoding="utf-8"))["niche_id"] == report["niche_id"]


def test_actual_snapshots_required_for_velocity(tmp_path):
    report = watch_niche(pod(), sample(), tmp_path / "watch.json",
                         previous=sample(1), as_of=ts())
    newcomer = next(row for row in report["videos"] if row["video_id"] == "ABCdef12345")
    assert newcomer["view_velocity_per_hour"] == 6250.0


def test_watcher_rejects_other_niche_and_stale_or_future_data(tmp_path):
    other = sample()
    other["niche"] = "ASMR sleep"
    with pytest.raises(ValueError, match="Cross-niche"):
        watch_niche(pod(), other, tmp_path / "bad.json", as_of=ts())
    with pytest.raises(ValueError, match="too old"):
        watch_niche(pod(), sample(7), tmp_path / "old.json", as_of=ts())
    older = sample(1)
    older["format_key"] = "different"
    with pytest.raises(ValueError, match="SAME niche"):
        watch_niche(pod(), sample(), tmp_path / "badprev.json", previous=older, as_of=ts())


@pytest.fixture(autouse=True)
def mock_verified_sources_for_unit_level_only(monkeypatch):
    # The real end-to-end source-integrity test lives in test_company_cine_bridge.py.
    monkeypatch.setattr("cinefactory.research_intelligence.pod_watch.verify_imported_company_sources", lambda bridge: True)


def test_unknown_evidence_is_watchlist_not_verified_viral_alert(tmp_path):
    current = sample()
    current["candidates"][0]["channels"][0]["videos"][0]["evidence_status"] = "UNKNOWN"
    result = watch_niche(pod(), current, tmp_path / "unknown.json", as_of=ts())
    video = next(x for x in result["videos"] if x["video_id"] == "ABCdef12345")
    assert video["alert"] is None
