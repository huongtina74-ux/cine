"""OWNER-locked lanes (2026-11-14): the daily competitor loop reads these files, so they must stay machine-readable."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "research" / "locked_lanes.json").read_text(encoding="utf-8"))
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def test_five_owner_locked_lanes_with_keywords_and_files():
    ids = [l["id"] for l in CFG["lanes"]]
    assert ids == ["mc_survival_movie", "mc_original_horror", "mc_shorts_whocan", "mc_shorts_physics", "explainer3d_shorts"]
    for lane in CFG["lanes"]:
        assert lane["status"] == "OWNER_LOCKED" and lane["format"] in ("long", "short")
        assert len(lane["keywords"]) >= 8 and len(set(lane["keywords"])) == len(lane["keywords"])
        assert (ROOT / lane["watchlist"]).exists() and (ROOT / lane["principles"]).exists()
    total = sum(len(l["keywords"]) for l in CFG["lanes"])
    assert total <= CFG["thresholds"]["search_calls_per_day_max"]


def test_owner_thresholds_match_rules():
    t = CFG["thresholds"]
    assert t["new_channel_days_max"] == 30 and t["new_channel_min_videos_1m"] == 2 and t["million"] == 1_000_000
    assert t["old_competitor_recent_days_max"] == 15 and t["explosive_window_days"] == 5
    assert t["exploding_video_days_max"] == 15 and t["leader_recent_video_days_max"] == 30
    assert (ROOT / CFG["owner_rules"]).exists()


def test_watchlists_have_eight_fields_unique_channels():
    for lane in CFG["lanes"]:
        rows = [l for l in (ROOT / lane["watchlist"]).read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        assert rows, lane["id"]
        seen = set()
        for row in rows:
            f = [x.strip() for x in row.split("|")]
            assert len(f) == 8, row
            assert f[0].startswith("UC") and f[2].startswith("@") and DATE.fullmatch(f[4])
            assert f[5] in ("leader", "new") and DATE.search(f[6])
            assert f[0] not in seen
            seen.add(f[0])


def test_principles_split_long_and_short_term():
    for lane in CFG["lanes"]:
        md = (ROOT / lane["principles"]).read_text(encoding="utf-8")
        assert "## Nguyên tắc dài hạn" in md and "## Nguyên tắc ngắn hạn" in md
        long_part, short_part = md.split("## Nguyên tắc dài hạn")[1].split("## Nguyên tắc ngắn hạn")
        assert re.search(r"\n### L\d+", long_part), lane["id"]
        for block in re.split(r"\n### S\d+", short_part)[1:]:
            assert "thấy lần đầu" in block and "lần cuối" in block and "trạng thái" in block
        assert "OBSERVED" in md
