from datetime import datetime, timedelta, timezone
import json
import shutil
import subprocess

import pytest

from cinefactory.research_intelligence.triage import triage_niches, select_departments
from cinefactory.research_intelligence.smart import choose_timestamps, observe_smart
from cinefactory.research_intelligence.core import create_department_tasks


NOW = datetime(2026, 10, 9, tzinfo=timezone.utc)

def iso(offset: int):
    return (NOW + timedelta(days=offset)).isoformat()


def video(ident, views, duration=600, kind="video"):
    return {"video_id": ident, "published_at": iso(-4), "duration_seconds": duration, "kind": kind, "views": views}


def niche(name, ids=("a", "b"), *, age=-10, flags=True):
    return {
        "niche": name, "observed_at": iso(0),
        "novel_format_verified": flags, "recent_evergreen_evidence": flags,
        "business_case_evidence": flags, "newcomer_evidence": flags,
        "evidence_urls": ["https://youtube.com/watch?v=one", "https://youtube.com/watch?v=two"],
        "channels": [{"channel_id": "newchannel", "created_at": iso(age), "videos": [video(ident, 1_100_000) for ident in ids]}]
    }


def test_high_evidence_niche_is_candidate_but_budgeted():
    report = triage_niches([niche("z"), niche("a")], max_deep_reviews=1)
    assert report["deep_review_count"] == 1
    assert [v["deep_review"] for v in report["candidates"]] == [True, False]
    assert all(v["status"] == "AUDIT_READY" for v in report["candidates"])


def test_one_video_not_two_and_duplicate_cannot_trick_gate():
    for ids in (("one",), ("same", "same")):
        item = triage_niches([niche("duplicate", ids)])["candidates"][0]
        assert item["status"] == "WATCHLIST"
        assert not item["gates"]["two_1m_longform_on_new_channel"]


def test_reject_old_channels_shorts_and_short_videos():
    assert triage_niches([niche("old", age=-31)])["candidates"][0]["status"] == "WATCHLIST"
    for duration, kind in ((120, "video"), (600, "shorts"), (600, "live")):
        data = niche("notlong")
        data["channels"][0]["videos"][1].update({"duration_seconds": duration, "kind": kind})
        assert triage_niches([data])["candidates"][0]["status"] == "WATCHLIST"


def test_unverified_demand_and_sources_blocks_costly_deep_review():
    item = niche("needs evidence", flags=False)
    item["evidence_urls"] = []
    out = triage_niches([item])
    assert out["deep_review_count"] == 0
    assert out["candidates"][0]["missing"]


def test_invalid_date_and_future_video():
    item = niche("future")
    item["channels"][0]["videos"][1]["published_at"] = iso(1)
    assert triage_niches([item])["candidates"][0]["status"] == "WATCHLIST"
    with pytest.raises(ValueError):
        triage_niches([{"niche": "bad", "observed_at": "2026-10-09"}])


def test_focused_routing_saves_work(tmp_path):
    assert select_departments("ASMR sleep") == ["research", "audio", "editorial", "quality"]
    assert "animation" in select_departments("Minecraft animation")
    obs = {"schema": "cine.research.observation.v1", "source": "local.mp4"}
    res = create_department_tasks(obs, tmp_path, niche="ASMR", reference_id="id", departments=select_departments("ASMR"))
    assert len(res["tasks"]) == 4
    with pytest.raises(ValueError):
        create_department_tasks(obs, tmp_path, niche="ASMR", reference_id="id", departments=["audio", "audio"])


def test_smart_sampling_covers_hook_and_end_with_budget():
    ts = choose_timestamps(600, max_frames=24, changes=[10, 14, 20, 22, 32])
    assert len(ts) <= 24
    assert 0 in ts
    assert max(ts) > 590
    assert all(0 <= t < 600 for t in ts)
    assert sorted(set(ts)) == ts
    with pytest.raises(ValueError):
        choose_timestamps(0)


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg missing")
def test_smart_observes_real_synthetic_video(tmp_path):
    media = tmp_path / "test.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=5", "-t", "3", "-c:v", "mpeg4", str(media)], check=True, capture_output=True)
    out = observe_smart(media, tmp_path / "observed", max_frames=8)
    assert out["sampling"]["frame_count"] <= 8
    assert out["sampling"]["strategy"] == "opening_plus_changes_plus_coverage"
    assert all(shutil.os.path.exists(f["path"]) for f in out["frames"])
    assert json.loads((tmp_path / "observed" / "observation.json").read_text(encoding="utf-8"))["sampling"]["strategy"] == out["sampling"]["strategy"]


def test_boolean_evidence_cannot_be_faked_by_string():
    candidate = niche("claimed")
    candidate["business_case_evidence"] = "false"
    item = triage_niches([candidate])["candidates"][0]
    assert item["status"] == "WATCHLIST"
    assert not item["gates"]["business_case_documented"]
