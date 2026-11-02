"""cf_youtube_niche_survey: quota accounting, key never leaks, summaries from mocked API responses."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import cf_youtube_niche_survey as s  # noqa: E402

NOW = datetime(2026, 11, 2, tzinfo=timezone.utc)


def _ch(cid, title, subs, created="2025-03-01T00:00:00Z"):
    return {"id": cid, "snippet": {"title": title, "publishedAt": created},
            "statistics": {"subscriberCount": str(subs), "viewCount": "1000"},
            "contentDetails": {"relatedPlaylists": {"uploads": "UU" + cid[2:]}}}


def _v(vid, cid, views, days_ago, dur="PT12M"):
    pub = (NOW.replace(day=1) if days_ago > 0 else NOW).isoformat().replace("+00:00", "Z")
    from datetime import timedelta
    pub = (NOW - timedelta(days=days_ago)).isoformat().replace("+00:00", "Z")
    return {"id": vid, "snippet": {"title": "t" + vid, "channelTitle": "C" + cid, "channelId": cid, "publishedAt": pub},
            "statistics": {"viewCount": str(views)}, "contentDetails": {"duration": dur}}


def fake_api(calls):
    chans = {"UCaaaaaaaaaaaaaaaaaaaaaa": _ch("UCaaaaaaaaaaaaaaaaaaaaaa", "Big", 1_000_000, "2019-01-01T00:00:00Z"),
             "UCbbbbbbbbbbbbbbbbbbbbbb": _ch("UCbbbbbbbbbbbbbbbbbbbbbb", "Tiny", 20_000)}
    vids = {"v1": _v("v1", "UCaaaaaaaaaaaaaaaaaaaaaa", 100_000, 10), "v2": _v("v2", "UCaaaaaaaaaaaaaaaaaaaaaa", 200_000, 20),
            "v3": _v("v3", "UCaaaaaaaaaaaaaaaaaaaaaa", 900_000, 40), "v4": _v("v4", "UCaaaaaaaaaaaaaaaaaaaaaa", 5_000, 5, "PT40S"),
            "d1": _v("d1", "UCbbbbbbbbbbbbbbbbbbbbbb", 400_000, 8)}

    def fetch(url):
        u = urlparse(url)
        ep, q = u.path.rsplit("/", 1)[-1], {k: v[0] for k, v in parse_qs(u.query).items()}
        calls.append(ep)
        assert q["key"] == "SECRET"
        if ep == "channels":
            if "forHandle" in q:
                return {"items": [chans["UCaaaaaaaaaaaaaaaaaaaaaa"]] if q["forHandle"] == "big" else []}
            return {"items": [chans[i] for i in q["id"].split(",") if i in chans]}
        if ep == "playlistItems":
            return {"items": [{"contentDetails": {"videoId": v}} for v in ("v1", "v2", "v3", "v4")]}
        if ep == "videos":
            return {"items": [vids[i] for i in q["id"].split(",") if i in vids]}
        if ep == "search":
            return {"items": [{"id": {"videoId": "d1"}}]}
        raise AssertionError(ep)
    return fetch


def test_survey_summaries_quota_and_new_small_discovery():
    calls = []
    c = s.Client("SECRET", 1000, fake_api(calls))
    cfg = {"niches": {"horror": {"channels": ["@big", "@missing"], "queries": ["minecraft found footage"]}}}
    res = s.survey(cfg, c, NOW, per_channel=10)
    ch = res["niches"]["horror"]["channels"][0]
    assert ch["long"] == 3 and ch["shorts"] == 1 and ch["long_median_views"] == 200_000
    assert ch["long_outliers_3x"] == 1 and ch["uploads_last_30d"] == 3
    assert res["unresolved"] == ["@missing"]
    assert res["quota_units_used"] == sum(s.COST[e] for e in calls) and calls.count("search") == 1
    md = s.to_markdown(res)
    assert "SECRET" not in md and "SECRET" not in json.dumps(res)
    overview = md.split("## horror")[0]
    assert "| horror | 1 | 200K |" in overview and "| 1 | 400K" in overview   # one new (2025) & small channel
    assert "| 20K | 2025-03-01 | 20.0 |" in md                                   # views ÷ subs for the tiny channel


def test_quota_stop_before_overspending():
    c = s.Client("SECRET", 150, fake_api([]))
    with pytest.raises(s.Quota):
        s.survey({"niches": {"x": {"channels": [], "queries": ["a", "b"]}}}, c, NOW)
    assert c.used <= 150


def test_no_key_fails_closed_without_calls(tmp_path, monkeypatch, capsys):
    for k in s.KEY_NAMES:
        monkeypatch.delenv(k, raising=False)
    wl = tmp_path / "w.json"
    wl.write_text(json.dumps({"niches": {"x": {"channels": ["@a"], "queries": ["q"]}}}), encoding="utf-8")
    assert s.main([str(wl), "--env-file", str(tmp_path / "none.env")]) == 3
    assert "NO_API_KEY" in capsys.readouterr().out


def test_env_file_key_and_committed_watchlist(tmp_path, monkeypatch):
    for k in s.KEY_NAMES:
        monkeypatch.delenv(k, raising=False)
    env = tmp_path / ".env"
    env.write_text("OTHER=1\nYOUTUBE_DATA_API_KEY=abc123xyz\n", encoding="utf-8")
    assert s.read_key(str(env)) == "abc123xyz"
    wl = json.loads((ROOT / "config/research/minecraft_niche_watchlist.json").read_text(encoding="utf-8"))
    assert len(wl["niches"]) >= 10 and all(n.get("queries") for n in wl["niches"].values())
    assert s.seconds("PT1H2M3S") == 3723 and s.seconds("P0D") == 0


def test_bad_handle_404_is_skipped_but_403_stops(monkeypatch):
    from urllib.error import HTTPError
    def raiser(code):
        def f(url, timeout=20):
            raise HTTPError(url, code, "x", {}, None)
        return f
    monkeypatch.setattr(s, "urlopen", raiser(404))
    assert s.Client._http("https://x/?key=SECRET") == {"items": [], "_error": 404}
    monkeypatch.setattr(s, "urlopen", raiser(403))
    with pytest.raises(RuntimeError) as e:
        s.Client._http("https://x/?key=SECRET")
    assert "SECRET" not in str(e.value) and "403" in str(e.value)
