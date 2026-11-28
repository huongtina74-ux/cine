"""cf_research_stats --kind skins: rank-weighted skin trends, week-over-week change, IP-safe design brief."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cf_research_stats as rs  # noqa: E402


def _row(rank, arch, pal, feat, ip=False, fav=10, age=5.0, size=4, season=""):
    return {"source": "namemc", "board": "trending_weekly", "board_size": size, "rank": rank, "favorites": fav,
            "age_days": age, "archetype": arch, "palette": pal, "features": feat, "season": season, "third_party_ip": ip}


def _write(path: Path, observed: str, skins: list, tags: list) -> Path:
    path.write_text(json.dumps({"meta": {"observed": observed}, "skins": skins, "tags": tags}), encoding="utf-8")
    return path


def test_rank_weighting_and_ip_rows_never_reach_the_brief(tmp_path):
    f = _write(tmp_path / "now.json", "2026-11-08", [
        _row(1, "slasher-mask", ["black"], ["mask"], ip=True),
        _row(2, "duck-costume", ["yellow"], ["animal-onesie"]),
        _row(3, "duck-costume", ["yellow", "red"], ["animal-onesie", "beanie"]),
        _row(4, "e-girl", ["pink"], ["cat-ears"]),
    ], [])
    skins, tags, meta = rs.load_skin_observations(f)
    a = rs.analyse_skins(skins, tags, None, None)
    assert next(iter(a["archetypes"])) == "duck-costume"          # 0.75 + 0.5 beats the single #1 row (1.0)
    assert a["blocked_ip_archetypes"] == ["slasher-mask"]
    brief_names = [k for k, _ in a["brief"]["archetypes"]]
    assert "slasher-mask" not in brief_names
    assert "mask" not in [k for k, _ in a["brief"]["features"]]   # features of IP rows are not learned either
    assert a["brief"]["palette"][0][0] == "yellow"


def test_previous_snapshot_gives_rising_fading_and_tag_growth(tmp_path):
    before = _write(tmp_path / "w1.json", "2026-11-01",
                    [_row(1, "dark-silhouette", ["black"], ["hood"]), _row(2, "duck-costume", ["yellow"], [])],
                    [{"source": "namemc", "tag": "christmas", "count": 7000}, {"source": "namemc", "tag": "halloween", "count": 5000}])
    now = _write(tmp_path / "w2.json", "2026-11-08",
                 [_row(1, "duck-costume", ["yellow"], []), _row(2, "santa-hat-kid", ["red"], ["santa-hat"])],
                 [{"source": "namemc", "tag": "christmas", "count": 7700}, {"source": "namemc", "tag": "halloween", "count": 5010}])
    out = tmp_path / "r.md"
    code = rs.main([str(now), "--kind", "skins", "--previous", str(before), "--out", str(out), "--json", str(tmp_path / "r.json")])
    assert code == 0
    a = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    rising = {(r["kind"], r["name"]) for r in a["rising"]}
    assert ("archetypes", "santa-hat-kid") in rising and ("archetypes", "duck-costume") in rising
    assert ("archetypes", "dark-silhouette") in {(r["kind"], r["name"]) for r in a["fading"]}
    top_tag = a["tag_growth"][0]
    assert top_tag["tag"] == "christmas" and top_tag["gain"] == 700 and top_tag["per_day"] == 100
    md = out.read_text(encoding="utf-8")
    assert "Rising / fading" in md and "Design brief for ORIGINAL cast" in md


def test_cli_line_and_bad_input(tmp_path):
    f = _write(tmp_path / "s.json", "2026-11-01", [_row(1, "knight", ["gray"], ["armor"])], [])
    res = subprocess.run([sys.executable, str(ROOT / "tools/cf_research_stats.py"), str(f), "--kind", "skins",
                          "--out", str(tmp_path / "o.md")], capture_output=True, text=True)
    assert res.stdout.startswith("SKINS_OK::") and "top=knight" in res.stdout
    empty = _write(tmp_path / "e.json", "2026-11-01", [], [])
    assert rs.main([str(empty), "--kind", "skins"]) == 2


def test_committed_baseline_snapshot_is_observation_only():
    f = ROOT / "config/niches/minecraft/skin_trends/2026-11-01.json"
    data = json.loads(f.read_text(encoding="utf-8"))
    assert "no scraper" in data["meta"]["observer"]
    assert all("http" not in json.dumps(r) for r in data["skins"])   # no skin image URLs or downloads stored
    skins, tags, _ = rs.load_skin_observations(f)
    assert len(skins) >= 40 and len(tags) == 30
    assert all(r["third_party_ip"] for r in skins if r["archetype"] in ("horror-slasher", "superhero"))


def test_video_mode_still_works(tmp_path):
    f = tmp_path / "v.json"
    f.write_text(json.dumps([{"channel": "a", "title": "x", "views": 100, "published": "2026-10-01"}]), encoding="utf-8")
    assert rs.main([str(f), "--out", str(tmp_path / "v.md")]) == 0
