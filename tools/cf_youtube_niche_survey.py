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

Trend scan (what is popular in the last N days, and which NEW channels are in it):

    python tools/cf_youtube_niche_survey.py --trend-keywords config/research/minecraft_trend_keywords.txt \
        --days 7 --expand 12 --out-dir reports/research/minecraft_trend_scan

Each keyword (short, long-tail, related) runs one search.list (order=viewCount, publishedAfter=N days),
then up to --expand related keywords are generated from the most frequent phrases in the result titles.
Every video gets a rule-based genre (GENRES below) and its channel's creation date and subscribers.

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


# Ordered: first match wins. Patterns run on lower-case title + tags + start of description.
GENRES: list[tuple[str, str]] = [
    ("kids_roleplay_maizen_ip", r"\bjj\b|mikey|maizen|cash and nico|cash & nico|\bnico\b"),
    ("arg_found_footage_horror", r"found footage|\barg\b|analog horror|lost footage|creepypasta|haunted|seed .*(cursed|haunted)|something is wrong|don.?t play|disturbing|player \d{2,}|world \d{3,}|entity|verity|herobrine sighting|backrooms"),
    ("horror_mod_gameplay", r"horror mod|scary mod|horror|scary|terrifying|nightmare|creepy|jumpscare"),
    ("player_simulation_war", r"players? (simulate|vs|war|battle)|\d[\d,]* players|civilization|army|\bwar\b"),
    ("manhunt", r"manhunt|hunters|speedrunner vs"),
    ("hardcore_n_days", r"\d+\s*days|hardcore"),
    ("challenge_minecraft_but", r"minecraft,? but|but every|\bbut\b.*(drops|blocks|mobs|i can)|challenge|\bop\b|random"),
    ("smp_series", r"\bsmp\b|lifesteal|server"),
    ("noob_pro_poor_rich", r"noob|\bpro\b|hacker|god|poor|rich"),
    ("animation_story", r"animation|animated|cartoon|\bmovie\b|full movie|short film|story"),
    ("lore_explainer_commentary", r"lore|explained|theory|history of|mystery|why |investigat|truth|documentary|tier list|ranking"),
    ("building_tutorial", r"build|house|base|tutorial|how to|hacks|design|timelapse|interior"),
    ("redstone_technical", r"redstone|farm|machine|computer|technical|contraption"),
    ("speedrun_pvp", r"speedrun|world record|pvp|bedwars|hypixel|skywars|clutch|mace|crystal"),
    ("news_update_snapshot", r"update|snapshot|\b1\.2\d|\b26\.\d|new mob|new block|minecraft live|mojang"),
    ("music_parody", r"song|music|parody|rap|remix"),
    ("prank_funny_meme", r"prank|funny|meme|troll|trolling|brainrot|\blol\b"),
]
_GEN = [(g, re.compile(rx)) for g, rx in GENRES]


def classify(title: str, tags: list | None = None, desc: str = "") -> str:
    text = " ".join([title or "", " ".join(tags or []), (desc or "")[:300]]).lower()
    for g, rx in _GEN:
        if rx.search(text):
            return g
    return "other_minecraft"


STOP = set("minecraft the a an and or of to in on for with is are i my me we you your it this that vs but at by from as be was it's i'm".split())


def related_queries(titles: list[str], seen: set[str], n: int) -> list[str]:
    from collections import Counter
    grams: Counter = Counter()
    for t in titles:
        w = [x for x in re.findall(r"[a-z0-9']+", t.lower()) if x not in STOP and len(x) > 2 and not x.isdigit()]
        for i in range(len(w)):
            grams[w[i]] += 1
            if i + 1 < len(w):
                grams[w[i] + " " + w[i + 1]] += 2   # prefer phrases
    out = []
    for g, _ in grams.most_common(200):
        q = "minecraft " + g
        if q not in seen and all(q not in o and o not in q for o in out):
            out.append(q)
        if len(out) >= n:
            break
    return out


def trend_scan(c: Client, keywords: list[str], now: datetime, days: int = 7, expand: int = 12,
               region: str = "US", per_query: int = 50) -> dict:
    after = (now - timedelta(days=days)).isoformat(timespec="seconds").replace("+00:00", "Z")
    hits: dict[str, set] = {}

    def run(q: str) -> list[str]:
        data = c.get("search", part="snippet", q=q, type="video", order="viewCount", maxResults=per_query,
                     publishedAfter=after, regionCode=region, relevanceLanguage="en")
        ids = [it["id"]["videoId"] for it in data.get("items", []) if it.get("id", {}).get("videoId")]
        for i in ids:
            hits.setdefault(i, set()).add(q)
        return ids

    seen = set(k.strip().lower() for k in keywords if k.strip())
    for k in sorted(seen):
        run(k)
    vids = {v["id"]: v for v in videos(c, list(hits))}
    titles = sorted(vids.values(), key=lambda v: -int(v.get("statistics", {}).get("viewCount", 0)))
    extra = related_queries([v["snippet"]["title"] for v in titles[:300]], seen, expand) if expand else []
    new_ids = []
    for q in extra:
        new_ids += [i for i in run(q) if i not in vids]
    for v in videos(c, sorted(set(new_ids))):
        vids[v["id"]] = v
    chans = resolve_channels(c, sorted({v["snippet"]["channelId"] for v in vids.values()}))
    rows = []
    for v in vids.values():
        r = row(v, now, chans.get(v["snippet"]["channelId"]))
        sn = v.get("snippet", {})
        r["genre"] = classify(sn.get("title", ""), sn.get("tags"), sn.get("description", ""))
        r["keywords"] = sorted(hits.get(v["id"], []))
        r["is_short"] = 0 < r["duration_s"] <= 180
        created = r.get("channel_created") or ""
        r["channel_age_days"] = (now.date() - datetime.fromisoformat(created).date()).days if created else None
        rows.append(r)
    return {"as_of": now.isoformat(timespec="seconds"), "days": days, "region": region,
            "seed_keywords": sorted(seen), "related_keywords": extra, "videos": rows, "quota_units_used": c.used}


def trend_markdown(res: dict, new_days: int = 365, small: int = 100_000, min_views: int = 50_000) -> str:
    rows = [r for r in res["videos"] if r["views"] >= 1]
    by = {}
    for r in rows:
        by.setdefault(r["genre"], []).append(r)
    L = [f"# Minecraft trend scan — last {res['days']} days (as of {res['as_of'][:10]}, region {res['region']})", "",
         f"OBSERVED via YouTube Data API: {len(res['seed_keywords'])} seed + {len(res['related_keywords'])} related keywords, "
         f"{len(rows)} unique videos, quota {res['quota_units_used']} units. Genre = rule-based (INFERRED). "
         f"New channel = created ≤ {new_days} days ago; small = < {_fmt(small)} subs.", "",
         "Related keywords generated from popular titles: " + (", ".join(res["related_keywords"]) or "-"), "",
         f"## Where new channels get in (videos with ≥ {_fmt(min_views)} views in the window)", "",
         "| Genre | Videos | Channels | Median views | Median views/day | Long-form share | New-channel videos | New-channel share | Small-channel videos | Best new-channel video |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    table = []
    for g, rs in by.items():
        pop = [r for r in rs if r["views"] >= min_views]
        if not pop:
            continue
        newv = [r for r in pop if r.get("channel_age_days") is not None and r["channel_age_days"] <= new_days]
        smallv = [r for r in pop if r.get("channel_subs") is not None and r["channel_subs"] < small]
        best = max(newv, key=lambda r: r["views"], default=None)
        table.append((len(newv) / len(pop), g, pop, newv, smallv, best))
    for share, g, pop, newv, smallv, best in sorted(table, key=lambda t: (-t[0], -len(t[2]))):
        L.append(f"| {g} | {len(pop)} | {len({r['channel_id'] for r in pop})} | {_fmt(statistics.median(r['views'] for r in pop))} | "
                 f"{_fmt(statistics.median(r['views_per_day'] for r in pop))} | {100 * sum(not r['is_short'] for r in pop) // len(pop)}% | "
                 f"{len(newv)} | {round(100 * share)}% | {len(smallv)} | "
                 + (f"{_fmt(best['views'])} · {best['channel']} ({best['channel_age_days']} d old)" if best else "-") + " |")
    newall = sorted([r for r in rows if r.get("channel_age_days") is not None and r["channel_age_days"] <= new_days and r["views"] >= min_views],
                    key=lambda r: -r["views"])
    L += ["", f"## Every popular video from a new channel ({len(newall)})", "",
          "| Views | Views/day | Genre | Short? | Channel | Channel age (d) | Subs | Title |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in newall[:120]:
        L.append(f"| {_fmt(r['views'])} | {_fmt(r['views_per_day'])} | {r['genre']} | {'S' if r['is_short'] else 'L'} | {r['channel']} | "
                 f"{r['channel_age_days']} | {_fmt(r.get('channel_subs'))} | [{r['title'][:70].replace('|', '/')}]({r['url']}) |")
    L += ["", "Caveats: one search snapshot (YouTube ranking, one region); 'new channel' uses the channel creation date, so",
          "renamed/repurposed old channels count as old; genre rules can mislabel - read titles before deciding."]
    return "\n".join(L) + "\n"


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
    p.add_argument("watchlist", nargs="?")
    p.add_argument("--trend-keywords", default="", help="text file, one keyword per line (# comments)")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--expand", type=int, default=12)
    p.add_argument("--out-dir", default="reports/research/niche_survey")
    p.add_argument("--env-file", default=".env")
    p.add_argument("--per-channel", type=int, default=30)
    p.add_argument("--max-units", type=int, default=4000)
    p.add_argument("--no-search", action="store_true")
    p.add_argument("--region", default="US")
    a = p.parse_args(argv)
    if a.trend_keywords:
        kws = [x.strip() for x in Path(a.trend_keywords).read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
        print(f"ESTIMATE::keywords={len(kws)}::expand={a.expand}::units~{(len(kws) + a.expand) * 100 + 40}::max={a.max_units}")
        key = read_key(a.env_file)
        if not key:
            print("NO_API_KEY::set YOUTUBE_DATA_API_KEY in the environment or --env-file (never paste it in chat)")
            return 3
        c = Client(key, a.max_units)
        try:
            res = trend_scan(c, kws, datetime.now(timezone.utc), a.days, a.expand, a.region)
        except Quota as e:
            print(f"QUOTA_STOP::{e}::used={c.used}")
            return 4
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        day = res["as_of"][:10]
        (out / f"{day}_trend_raw.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        (out / f"{day}_trend.md").write_text(trend_markdown(res), encoding="utf-8")
        print(f"TREND_OK::{out / (day + '_trend.md')}::videos={len(res['videos'])}::units={c.used}")
        return 0
    if not a.watchlist:
        p.error("watchlist or --trend-keywords required")
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
