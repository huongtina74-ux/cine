import json
import pytest

from cinefactory.research_intelligence.analytics_adapter import import_studio_csv, retention_drop_candidates, select_owned_video


def test_studio_ingest_valid_csv_and_period(tmp_path):
    file = tmp_path / "report.csv"
    file.write_text("Video ID,Views,Impressions,Impressions click-through rate (%),Average view duration,Watch time (hours)\nabcdefghijk,1,500,4.5%,0:03:21,42.5\n", encoding="utf-8")
    report = import_studio_csv(file, tmp_path / "clean.json", period_start="2026-10-01", period_end="2026-10-08", channel_id="UC-owned")
    row = select_owned_video(report, "abcdefghijk")
    assert row["metrics"]["views"] == 1
    assert row["metrics"]["ctr"] == pytest.approx(0.045)
    assert row["metrics"]["average_view_duration_seconds"] == 201
    assert row["source"]["period_start"] == "2026-10-01"
    assert json.loads((tmp_path / "clean.json").read_text(encoding="utf-8"))["schema"] == "cine.research.studio_csv.v1"


def test_bad_studio_csv_fails_closed(tmp_path):
    file = tmp_path / "report.csv"
    file.write_text("Video ID,Views\nabcdefghijk,5\nabcdefghijk,6\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        import_studio_csv(file, tmp_path / "clean.json", period_start="2026-10-01", period_end="2026-10-08", channel_id="UC-owned")
    with pytest.raises(ValueError, match="period"):
        import_studio_csv(file, tmp_path / "clean.json", period_start="2026-10-09", period_end="2026-10-08", channel_id="UC-owned")
    file.write_text("Video ID,Views\nabcdefghijk,-2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        import_studio_csv(file, tmp_path / "clean.json", period_start="2026-10-01", period_end="2026-10-08", channel_id="UC-owned")


def test_retention_is_measured_and_does_not_assert_causes():
    drops = retention_drop_candidates([
        {"second": 0, "retention_pct": 98}, {"second": 20, "retention_pct": 94}, {"second": 30, "retention_pct": 72}
    ], min_drop_percentage_points=10)
    assert len(drops) == 1
    assert drops[0]["from_seconds"] == 20
    assert "does not establish cause" in drops[0]["hypothesis"]
    with pytest.raises(ValueError):
        retention_drop_candidates([{"second": 2, "retention_pct": 90}, {"second": 2, "retention_pct": 80}])


def test_retention_maps_to_nearby_owned_frame():
    from cinefactory.research_intelligence.analytics_adapter import map_retention_to_frames
    observed = {"schema": "cine.research.observation.v1", "source": "owned.mp4",
                "frames": [{"second": 18, "path": "frame18.jpg"}, {"second": 35, "path": "frame35.jpg"}]}
    points = [{"second": 0, "retention_pct": 99}, {"second": 20, "retention_pct": 90}, {"second": 30, "retention_pct": 65}]
    result = map_retention_to_frames(observed, points, max_distance_seconds=6)
    assert result["drops"][1]["nearest_sampled_frame"]["path"] == "frame35.jpg"
    assert result["drops"][0]["nearest_sampled_frame"]["path"] == "frame18.jpg"
    assert "does not" in result["drops"][0]["hypothesis"]
