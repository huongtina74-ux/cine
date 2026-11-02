"""Minecraft (or any) niche survey with the official YouTube Data API v3 - stdlib only.

Measures, per niche, what a watchlist of channels and a few discovery searches really get:
median long-form views, views/day, upload cadence, outlier rate, and which NEW / SMALL channels
broke out recently. Numbers are OBSERVED from the API at run time.

    python tools/cf_youtube_niche_survey.py config/research/minecraft_niche_watchlist.json \
        --out-dir reports/research/minecraft_niche_survey [--env-file .env] [--no-search]

Key: YOUTUBE_DATA_API_KEY / YOUTUBE_API_KEY / GOOGLE_API_KEY from the environment or --env-file.
The key is never printed or written. Quota (10,000 units/day free): channels/playlistItems/videos
cost 1 unit per call, search.list costs 100 - the run prints its estimate first and stops at
--max-units. No scraping: official API only.

Runs on plain Python 3.10+ (also inside Blender's Python) because it uses only the standard library.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import urlopen

API = "https://www.googleapis.com/youtube/v3/"
KEY_NAMES = ("YOUTUBE_DATA_API_KEY", "YOUTUBE_API_KEY", "GOOGLE_API_KEY")
DUR = re.compile(r"^P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")
COST = {"channels": 1, "playlistItems": 1, "videos": 1, "search": 100}


class Quota(Exception):
    pass


class Client:
    """Thin API client; `fetch` is injectable for tests. Counts quota units."""

    def __init__(self, key: str, max_units: int, fetch=None):
        self.key, self.max_units, self.used = key, max_units, 0
        self._fetch = fetch or self._http

    @staticmethod
    def _http(url: str) -> dict:
        try:
            with urlopen(url, timeout=20) as s:
                return json.load(s)
        except HTTPError as e:
            # 400/404 = one bad handle or a channel without an uploads playlist: skip it, keep going.
            # 403 = quota/key problem: stop. Never surface urllib messages (they contain the key).
            if e.code in (400, 404):
                return {"items": [], "_error": e.code}
            raise RuntimeError(f"YouTube API refused the request (HTTP {e.code}: quota or key restriction)") from None
        except Exception:
            raise RuntimeError("YouTube API request failed (network)") from None

    def get(self, endpoint: str, **params) -> dict:
        cost = COST[endpoint]
        if self.used + cost > self.max_units:
            raise Quota(f"would exceed --max-units {self.max_units}")
        self.used += cost
        params["key"] = self.key
        return self._fetch(API + endpoint + "?" + urlencode(params))


def read_key(env_file: str | None) -> str | None:
    for k in KEY_NAMES:
        if os.environ.get(k):
            return os.environ[k]
    if env_file and Path(env_file).is_file():
        for line in Path(env_file).read_text(encoding="utf-8", errors="ignore").splitlines():
            m = re.match(r"\s*([A-Z_]+)\s*=\s*['\"]?([^'\"\s#]+)", line)
            if m and m.group(1) in KEY_NAMES:
                return m.group(2)
    return None


def seconds(iso: str) -> int:
    m = DUR.fullmatch(iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def utc(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def resolve_channels(c: Client, refs: list[str]) -> dict[str, dict]:
    """refs are '@handle' or 'UC...' ids -> {ref: channel item}."""
    out, ids = {}, [r for r in refs if r.startswith("UC")]
    for r in refs:
        if not r.startswith("UC"):
            data = c.get("channels", part="snippet,statistics,contentDetails", forHandle=r.lstrip("@"))
            if data.get("items"):
                out[r] = data["items"][0]
    for i in range(0, len(ids), 50):
        data = c.get("channels", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50]))
        for it in data.get("items", []):
            out[it["id"]] = it
    return out


def videos(c: Client, ids: list[str]) -> list[dict]:
    rows = []
    for i in range(0, len(ids), 50):
        data = c.get("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50]))
        rows += data.get("items", [])
    return rows


def recent_uploads(c: Client, ch: dict, n: int) -> list[str]:
    pl = ch.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    if not pl:
        return []
    data = c.get("playlistItems", part="contentDetails", playlistId=pl, maxResults=min(50, n))
    return [it["contentDetails"]["videoId"] for it in data.get("items", [])]


def row(v: dict, now: datetime, ch: dict | None = None) -> dict:
    st, sn = v.get("statistics", {}), v.get("snippet", {})
    pub = utc(sn["publishedAt"])
    age = max(1.0, (now - pub).total_seconds() / 86400)
    views = int(st.get("viewCount", 0))
    r = {"id": v["id"], "title": sn.get("title", ""), "channel": sn.get("channelTitle", ""),
         "channel_id": sn.get("channelId", ""), "published": pub.date().isoformat(), "age_days": round(age, 1),
         "views": views, "views_per_day": round(views / age, 1), "duration_s": seconds(v.get("contentDetails", {}).get("duration", "")),
         "url": "https://www.youtube.com/watch?v=" + v["id"]}
    if ch:
        cs, cn = ch.get("statistics", {}), ch.get("snippet", {})
        r["channel_subs"] = int(cs.get("subscriberCount", 0)) if not cs.get("hiddenSubscriberCount") else None
        r["channel_created"] = cn.get("publishedAt", "")[:10]
    return r


def channel_summary(ch: dict, rows: list[dict], short_s: int) -> dict:
    longs = [r for r in rows if r["duration_s"] > short_s]
    shorts = [r for r in rows if 0 < r["duration_s"] <= short_s]
    med = statistics.median([r["views"] for r in longs]) if longs else 0
    recent = [r for r in rows if r["age_days"] <= 30]
    st = ch.get("statistics", {})
    return {
        "channel": ch["snippet"]["title"], "channel_id": ch["id"],
        "subs": int(st.get("subscriberCount", 0)) if not st.get("hiddenSubscriberCount") else None,
        "created": ch["snippet"].get("publishedAt", "")[:10], "total_views": int(st.get("viewCount", 0)),
        "sampled": len(rows), "long": len(longs), "shorts": len(shorts),
        "long_median_views": med,
        "long_median_vpd": statistics.median([r["views_per_day"] for r in longs]) if longs else 0,
        "long_median_minutes": round(statistics.median([r["duration_s"] for r in longs]) / 60, 1) if longs else 0,
        "uploads_last_30d": len(recent),
        "long_outliers_3x": sum(1 for r in longs if med and r["views"] >= 3 * med),
        "best": max(rows, key=lambda r: r["views"])["title"] if rows else "",
        "best_views": max((r["views"] for r in rows), default=0),
    }


def survey(cfg: dict, c: Client, now: datetime, per_channel: int = 30, short_s: int = 180,
           search: bool = True, search_days: int = 90, region: str = "US") -> dict:
    niches = cfg["niches"]
    refs = sorted({r for n in niches.values() for r in n.get("channels", [])})
    chans = resolve_channels(c, refs)
    out = {"as_of": now.isoformat(timespec="seconds"), "niches": {}, "unresolved": [r for r in refs if r not in chans]}
    for name, spec in niches.items():
        summ, raw = [], []
        for ref in spec.get("channels", []):
            ch = chans.get(ref)
            if not ch:
                continue
            vids = videos(c, recent_uploads(c, ch, per_channel))
            rows = [row(v, now, ch) for v in vids]
            raw += rows
            summ.append(channel_summary(ch, rows, short_s))
        disc = []
        if search:
            after = (now - timedelta(days=search_days)).isoformat(timespec="seconds").replace("+00:00", "Z")
            for q in spec.get("queries", []):
                data = c.get("search", part="snippet", q=q, type="video", order="viewCount", maxResults=25,
                             publishedAfter=after, regionCode=region, relevanceLanguage="en")
                ids = [it["id"]["videoId"] for it in data.get("items", []) if it.get("id", {}).get("videoId")]
                vids = videos(c, ids)
                cids = sorted({v["snippet"]["channelId"] for v in vids})
                cmap = resolve_channels(c, cids)
                for v in vids:
                    r = row(v, now, cmap.get(v["snippet"]["channelId"]))
                    r["query"] = q
                    disc.append(r)
        out["niches"][name] = {"channels": summ, "discovery": disc, "uploads": raw}
    out["quota_units_used"] = c.used
    return out


def _fmt(n) -> str:
    if n is None:
        return "hidden"
    n = float(n)
    return f"{n / 1e6:.2f}M" if n >= 1e6 else (f"{n / 1e3:.0f}K" if n >= 1e3 else f"{n:.0f}")


def to_markdown(res: dict, new_after: str = "2024-01-01", small_subs: int = 100_000, short_s: int = 180) -> str:
    L = [f"# YouTube niche survey — {res['as_of'][:10]}", "",
         "All numbers OBSERVED from the YouTube Data API at run time (lifetime views; recent videos are still growing).",
         f"Quota units used: {res.get('quota_units_used')}. Unresolved channel refs: {', '.join(res['unresolved']) or 'none'}.", "",
         "## Niche overview", "",
         "| Niche | Channels | Median of channel long-form medians | Median views/day | Median length (min) | Discovery: new (≥" + new_after[:4] + ") & small (<" + _fmt(small_subs) + " subs) channels in top results | Best discovery video |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
    for name, n in res["niches"].items():
        ch = [c for c in n["channels"] if c["long"]]
        med = statistics.median([c["long_median_views"] for c in ch]) if ch else 0
        vpd = statistics.median([c["long_median_vpd"] for c in ch]) if ch else 0
        mins = statistics.median([c["long_median_minutes"] for c in ch]) if ch else 0
        disc = [d for d in n["discovery"] if d["duration_s"] > short_s]
        newsmall = {d["channel"] for d in disc if d.get("channel_created", "9") >= new_after and (d.get("channel_subs") or 0) < small_subs}
        best = max(disc, key=lambda d: d["views"], default=None)
        L.append(f"| {name} | {len(n['channels'])} | {_fmt(med)} | {_fmt(vpd)} | {mins} | {len(newsmall)} | "
                 + (f"{_fmt(best['views'])} · {best['channel']}" if best else "-") + " |")
    for name, n in res["niches"].items():
        L += ["", f"## {name}", "", "| Channel | Subs | Created | Long median | Views/day | Min | Uploads 30d | 3× outliers | Best video |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for c in sorted(n["channels"], key=lambda c: -c["long_median_views"]):
            L.append(f"| {c['channel']} | {_fmt(c['subs'])} | {c['created']} | {_fmt(c['long_median_views'])} | {_fmt(c['long_median_vpd'])} | "
                     f"{c['long_median_minutes']} | {c['uploads_last_30d']} | {c['long_outliers_3x']} | {_fmt(c['best_views'])} {c['best'][:50].replace('|', '/')} |")
        disc = sorted([d for d in n["discovery"] if d["duration_s"] > short_s], key=lambda d: -d["views"])[:12]
        if disc:
            L += ["", "Top long-form discovery results (last 90 days):", "",
                  "| Views | Views/day | Channel | Subs | Created | Views ÷ subs | Title |", "| --- | --- | --- | --- | --- | --- | --- |"]
            for d in disc:
                ratio = f"{d['views'] / d['channel_subs']:.1f}" if d.get("channel_subs") else "?"
                L.append(f"| {_fmt(d['views'])} | {_fmt(d['views_per_day'])} | {d['channel']} | {_fmt(d.get('channel_subs'))} | "
                         f"{d.get('channel_created', '?')} | {ratio} | [{d['title'][:60].replace('|', '/')}]({d['url']}) |")
    L += ["", "Caveats: watchlists pick survivors; search results are YouTube's ranking for one region/language on one day;",
          "lifetime views favour older videos (use views/day); no CTR/retention/RPM in public data."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("watchlist")
    p.add_argument("--out-dir", default="reports/research/niche_survey")
    p.add_argument("--env-file", default=".env")
    p.add_argument("--per-channel", type=int, default=30)
    p.add_argument("--max-units", type=int, default=4000)
    p.add_argument("--no-search", action="store_true")
    p.add_argument("--region", default="US")
    a = p.parse_args(argv)
    cfg = json.loads(Path(a.watchlist).read_text(encoding="utf-8"))
    key = read_key(a.env_file)
    n_ch = len({r for n in cfg["niches"].values() for r in n.get("channels", [])})
    n_q = 0 if a.no_search else sum(len(n.get("queries", [])) for n in cfg["niches"].values())
    est = n_ch * 3 + n_q * (100 + 2)
    print(f"ESTIMATE::channels={n_ch}::queries={n_q}::units~{est}::max={a.max_units}")
    if not key:
        print("NO_API_KEY::set YOUTUBE_DATA_API_KEY in the environment or --env-file (never paste it in chat)")
        return 3
    c = Client(key, a.max_units)
    try:
        res = survey(cfg, c, datetime.now(timezone.utc), a.per_channel, search=not a.no_search, region=a.region)
    except Quota as e:
        print(f"QUOTA_STOP::{e}::used={c.used}")
        return 4
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    day = res["as_of"][:10]
    (out / f"{day}_raw.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / f"{day}_survey.md").write_text(to_markdown(res), encoding="utf-8")
    print(f"SURVEY_OK::{out / (day + '_survey.md')}::units={c.used}::unresolved={len(res['unresolved'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
