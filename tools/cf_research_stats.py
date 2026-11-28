"""Research numbers that do not lie: medians, outliers and views per day for a niche.

The nightly-research skill saves what it pulls (vidIQ, YouTube Data API, a CSV export)
as one JSON or CSV file of videos, then runs this to get honest numbers:

    python tools/cf_research_stats.py data/research/raw/2026-10-15.json --niche "kids long slide" \
        --out reports/research/2026-10-15_stats.md [--json reports/research/2026-10-15_stats.json]

Each video needs: channel, title, views, published (ISO date). Optional: duration_s, channel_subs, url.
Field names are matched loosely (view_count, publishedAt, channelTitle, duration ...).

Outputs: niche median and spread (not the best number), per-channel median views,
outliers (>= 3x their own channel median, the formula worth studying), views/day, long vs short,
and the words that repeat in outlier titles. Every number is OBSERVED from the input file as of its date.

Skin trends (Minecraft character design, `minecraft-trend-watch` skill):

    python tools/cf_research_stats.py config/niches/minecraft/skin_trends/2026-11-01.json --kind skins \
        [--previous config/niches/minecraft/skin_trends/2026-10-25.json] --out reports/research/2026-11-01_skins.md

Input is a list of OBSERVATIONS written while a person (or Claude, in an interactive session) looks at public
skin boards by hand - never a scraper. A skin row: source, board, rank, board_size, favorites, age_days,
archetype, palette[], features[], season, third_party_ip (true = a known character: counted as a trend, never used).
A tag row: source, tag, count. Output: rank-weighted archetype/feature/palette shares, rising vs --previous,
tag growth, and a design brief for ORIGINAL characters (third-party IP archetypes are listed as blocked).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):  # Windows consoles (cp1252) must not crash on Vietnamese/emoji text
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

ALIASES = {
    "channel": ("channel", "channel_title", "channelTitle", "channel_name", "author"),
    "title": ("title", "video_title", "name"),
    "views": ("views", "view_count", "viewCount", "views_count"),
    "published": ("published", "published_at", "publishedAt", "upload_date", "date"),
    "duration_s": ("duration_s", "duration", "duration_seconds", "length_seconds"),
    "channel_subs": ("channel_subs", "subscribers", "subscriber_count", "subs"),
    "url": ("url", "video_url", "link", "id", "video_id"),
}
STOP = set("the a an and or of to in on for with is are this that you your my how what why vs from at by it".split())
ISO_DUR = re.compile(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def pick(row: dict, key: str):
    for k in ALIASES[key]:
        if k in row and row[k] not in (None, ""):
            return row[k]
    return None


def to_seconds(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    m = ISO_DUR.fullmatch(s)
    if m and any(m.groups()):
        d, h, mi, se = (int(x or 0) for x in m.groups())
        return d * 86400 + h * 3600 + mi * 60 + se
    if ":" in s:
        parts = [float(p) for p in s.split(":")]
        sec = 0.0
        for p in parts:
            sec = sec * 60 + p
        return sec
    try:
        return float(s)
    except ValueError:
        return None


def to_date(v) -> date | None:
    if v is None:
        return None
    s = str(v).strip()
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        try:
            return date(*(int(x) for x in m.groups()))
        except ValueError:
            return None
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:10] if "-" in s else s[:8], fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def load(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as fh:
            raw = list(csv.DictReader(fh))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            raw = data.get("videos") or data.get("items") or data.get("results") or []
        else:
            raw = data
    rows = []
    for r in raw:
        views = pick(r, "views")
        try:
            views = int(float(str(views).replace(",", ""))) if views is not None else None
        except ValueError:
            views = None
        rows.append({
            "channel": str(pick(r, "channel") or "?"),
            "title": str(pick(r, "title") or ""),
            "views": views,
            "published": to_date(pick(r, "published")),
            "duration_s": to_seconds(pick(r, "duration_s")),
            "channel_subs": pick(r, "channel_subs"),
            "url": str(pick(r, "url") or ""),
        })
    return [r for r in rows if r["views"] is not None]


def q(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def fmt(n: float) -> str:
    return f"{n / 1e6:.2f}M" if n >= 1e6 else (f"{n / 1e3:.1f}K" if n >= 1e3 else f"{n:.0f}")


def analyse(rows: list[dict], as_of: date, outlier_x: float, short_s: float) -> dict:
    by_ch = defaultdict(list)
    for r in rows:
        by_ch[r["channel"]].append(r)
    ch_median = {c: statistics.median(v["views"] for v in vs) for c, vs in by_ch.items()}
    for r in rows:
        age = max(1, (as_of - r["published"]).days) if r["published"] else None
        r["age_days"] = age
        r["views_per_day"] = r["views"] / age if age else None
        med = ch_median[r["channel"]]
        r["x_channel"] = r["views"] / med if med else None
        r["is_short"] = r["duration_s"] is not None and r["duration_s"] <= short_s
    multi = [r for r in rows if len(by_ch[r["channel"]]) >= 3 and r["x_channel"] and r["x_channel"] >= outlier_x]
    multi.sort(key=lambda r: r["x_channel"], reverse=True)
    views = [r["views"] for r in rows]
    words = Counter(w for r in multi for w in set(re.findall(r"[a-zA-ZÀ-ỹ']+", r["title"].lower())) if w not in STOP and len(w) > 2)
    longs = [r["views"] for r in rows if r["duration_s"] is not None and not r["is_short"]]
    shorts = [r["views"] for r in rows if r["is_short"]]
    return {
        "videos": len(rows), "channels": len(by_ch),
        "median": statistics.median(views) if views else 0, "p25": q(views, 0.25), "p75": q(views, 0.75),
        "max": max(views) if views else 0,
        "long_median": statistics.median(longs) if longs else None, "short_median": statistics.median(shorts) if shorts else None,
        "channel_rows": sorted(((c, len(vs), ch_median[c]) for c, vs in by_ch.items()), key=lambda x: -x[2]),
        "outliers": multi, "outlier_words": words.most_common(12),
        "fresh": sorted((r for r in rows if r["age_days"] and r["age_days"] <= 30 and r["views_per_day"]),
                        key=lambda r: -r["views_per_day"])[:10],
    }


def to_markdown(a: dict, niche: str, src: Path, as_of: date, outlier_x: float) -> str:
    L = [f"# Research stats — {niche or src.stem}", "",
         f"As of {as_of.isoformat()} · source `{src.as_posix()}` · {a['videos']} videos from {a['channels']} channels · all numbers OBSERVED from this file.", "",
         "## The niche in one line", "",
         f"Median video {fmt(a['median'])} views (middle half {fmt(a['p25'])}–{fmt(a['p75'])}); the best video ({fmt(a['max'])}) is not the benchmark."]
    if a["long_median"] is not None or a["short_median"] is not None:
        L.append(f"Long videos median {fmt(a['long_median'] or 0)}, shorts median {fmt(a['short_median'] or 0)}.")
    L += ["", f"## Outliers (≥ {outlier_x:g}× their own channel median, channels with ≥ 3 videos)", ""]
    if a["outliers"]:
        L += ["| × channel | Views | Views/day | Age (days) | Channel | Title |", "| --- | --- | --- | --- | --- | --- |"]
        for r in a["outliers"][:20]:
            title = r["title"].replace("|", "/")
            if r["url"].startswith("http"):
                title = f"[{title}]({r['url']})"
            vpd = fmt(r["views_per_day"]) if r["views_per_day"] else "?"
            L.append(f"| {r['x_channel']:.1f} | {fmt(r['views'])} | {vpd} | {r['age_days'] or '?'} | {r['channel']} | {title} |")
        L += ["", "Words that repeat in outlier titles: " + ", ".join(f"{w} ({n})" for w, n in a["outlier_words"])]
    else:
        L.append("No outliers in this sample.")
    L += ["", "## Fastest new videos (≤ 30 days, by views/day)", ""]
    if a["fresh"]:
        L += ["| Views/day | Views | Channel | Title |", "| --- | --- | --- | --- |"]
        L += [f"| {fmt(r['views_per_day'])} | {fmt(r['views'])} | {r['channel']} | {r['title'].replace('|', '/')} |" for r in a["fresh"]]
    else:
        L.append("None in the sample (no publish dates, or nothing newer than 30 days).")
    L += ["", "## Channels by median views", "", "| Channel | Videos | Median views |", "| --- | --- | --- |"]
    L += [f"| {c} | {n} | {fmt(m)} |" for c, n, m in a["channel_rows"][:25]]
    L += ["", "Caveats: public views only (no CTR, retention or RPM); small samples swing; survivorship bias — channels that failed are not in the list."]
    return "\n".join(L) + "\n"


def _as_list(v) -> list[str]:
    if v is None or v == "":
        return []
    if isinstance(v, (list, tuple)):
        return [str(x).strip().lower() for x in v if str(x).strip()]
    return [x.strip().lower() for x in re.split(r"[;,/]", str(v)) if x.strip()]


def load_skin_observations(path: Path) -> tuple[list[dict], list[dict], dict]:
    """Return (skin rows, tag rows, meta) from a JSON file ({meta, skins, tags} or a flat list) or a CSV."""
    meta: dict = {}
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as fh:
            raw = list(csv.DictReader(fh))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            meta = data.get("meta") or {}
            raw = list(data.get("skins") or []) + list(data.get("tags") or [])
        else:
            raw = data
    skins, tags = [], []
    for r in raw:
        if r.get("tag") not in (None, ""):
            try:
                tags.append({"source": str(r.get("source") or "?"), "tag": str(r["tag"]).strip().lower(),
                             "count": int(float(str(r.get("count", 0)).replace(",", "")))})
            except ValueError:
                continue
            continue
        if not r.get("archetype"):
            continue
        try:
            rank = int(r.get("rank") or 0)
        except ValueError:
            rank = 0
        try:
            size = int(r.get("board_size") or 0)
        except ValueError:
            size = 0
        skins.append({
            "source": str(r.get("source") or "?"), "board": str(r.get("board") or "?"),
            "rank": rank, "board_size": size,
            "favorites": int(float(str(r.get("favorites") or 0).replace(",", ""))),
            "age_days": float(r.get("age_days") or 0) or None,
            "archetype": str(r["archetype"]).strip().lower(),
            "palette": _as_list(r.get("palette")), "features": _as_list(r.get("features")),
            "season": str(r.get("season") or "").strip().lower(),
            "third_party_ip": str(r.get("third_party_ip", "")).strip().lower() in ("1", "true", "yes"),
        })
    return skins, tags, meta


def _weight(r: dict) -> float:
    """Rank weight inside its board: #1 of 24 -> 1.0, #24 of 24 -> ~0.04; unknown rank -> 0.5."""
    if r["rank"] <= 0 or r["board_size"] <= 0:
        return 0.5
    return max(0.0, (r["board_size"] + 1 - r["rank"]) / r["board_size"])


def _shares(skins: list[dict], key: str) -> dict[str, float]:
    total = sum(_weight(r) for r in skins) or 1.0
    acc: Counter = Counter()
    for r in skins:
        vals = r[key] if isinstance(r[key], list) else [r[key]]
        for v in set(vals):
            if v:
                acc[v] += _weight(r)
    return {k: v / total for k, v in acc.most_common()}


def analyse_skins(skins: list[dict], tags: list[dict], prev: tuple[list[dict], list[dict], dict] | None,
                  days_between: float | None) -> dict:
    out = {"skins": len(skins), "boards": sorted({f"{r['source']}:{r['board']}" for r in skins}),
           "archetypes": _shares(skins, "archetype"), "features": _shares(skins, "features"),
           "palette": _shares(skins, "palette"), "seasons": _shares([r for r in skins if r["season"]], "season")}
    ip = Counter(r["archetype"] for r in skins if r["third_party_ip"])
    out["blocked_ip_archetypes"] = sorted(ip)
    momentum = [r for r in skins if r["age_days"]]
    out["momentum"] = sorted(({"archetype": r["archetype"], "source": r["source"], "board": r["board"], "rank": r["rank"],
                               "favorites_per_day": r["favorites"] / r["age_days"], "third_party_ip": r["third_party_ip"]}
                              for r in momentum), key=lambda x: -x["favorites_per_day"])[:10]
    out["rising"], out["fading"], out["tag_growth"] = [], [], []
    if prev:
        for key in ("archetypes", "features", "palette"):
            before = _shares(prev[0], key[:-1] if key == "archetypes" else key) if prev[0] else {}
            now = out[key]
            for k in set(now) | set(before):
                d = now.get(k, 0.0) - before.get(k, 0.0)
                row = {"kind": key, "name": k, "now": now.get(k, 0.0), "before": before.get(k, 0.0), "delta": d}
                if d >= 0.05:
                    out["rising"].append(row)
                elif d <= -0.05:
                    out["fading"].append(row)
        out["rising"].sort(key=lambda r: -r["delta"])
        out["fading"].sort(key=lambda r: r["delta"])
        old = {(t["source"], t["tag"]): t["count"] for t in prev[1]}
        for t in tags:
            o = old.get((t["source"], t["tag"]))
            if o is not None and t["count"] >= o:
                gain = t["count"] - o
                out["tag_growth"].append({"tag": t["tag"], "source": t["source"], "gain": gain,
                                          "per_day": gain / days_between if days_between else None,
                                          "pct": gain / o if o else None})
        out["tag_growth"].sort(key=lambda r: -(r["pct"] or 0))
    out["tags_now"] = sorted(tags, key=lambda t: -t["count"])[:30]
    own = [r for r in skins if not r["third_party_ip"]]  # the brief never learns from other people's characters
    allowed = [(k, v) for k, v in out["archetypes"].items() if k not in ip]
    out["brief"] = {
        "archetypes": allowed[:3],
        "features": list(_shares(own, "features").items())[:6],
        "palette": list(_shares(own, "palette").items())[:5],
    }
    return out


def skins_to_markdown(a: dict, src: Path, as_of: date, prev_src: Path | None) -> str:
    pct = lambda x: f"{x * 100:.0f}%"
    L = [f"# Minecraft skin trends — {as_of.isoformat()}", "",
         f"Source `{src.as_posix()}` · {a['skins']} observed skins on {', '.join(a['boards']) or '?'}"
         + (f" · compared with `{prev_src.as_posix()}`" if prev_src else " · first snapshot (no comparison yet)") + ".",
         "Ranks, favorites and tag counts are OBSERVED on the public boards; archetype/feature coding is INFERRED by whoever filled the file.",
         "Shares are rank-weighted (#1 counts most). Trend = what players wear, not proof of what gets YouTube views.", "",
         "## Archetypes", "", "| Archetype | Share | Usable |", "| --- | --- | --- |"]
    L += [f"| {k} | {pct(v)} | {'NO - third-party IP' if k in a['blocked_ip_archetypes'] else 'as inspiration'} |"
          for k, v in list(a["archetypes"].items())[:12]]
    L += ["", "## Features and palette", "",
          "Features: " + ", ".join(f"{k} {pct(v)}" for k, v in list(a["features"].items())[:12]),
          "", "Palette: " + ", ".join(f"{k} {pct(v)}" for k, v in list(a["palette"].items())[:10])]
    if a["seasons"]:
        L += ["", "Seasonal: " + ", ".join(f"{k} {pct(v)}" for k, v in a["seasons"].items())]
    L += ["", "## Momentum (favorites per day on the board)", ""]
    L += [f"- {m['favorites_per_day']:.0f}/day · {m['archetype']} ({m['source']} {m['board']} #{m['rank']})"
          + (" · third-party IP" if m["third_party_ip"] else "") for m in a["momentum"]] or ["- no ages recorded"]
    if prev_src:
        L += ["", "## Rising / fading vs previous snapshot", ""]
        L += [f"- ▲ {r['kind']}: {r['name']} {pct(r['before'])} → {pct(r['now'])}" for r in a["rising"][:10]] or ["- nothing rose by ≥ 5 points"]
        L += [f"- ▼ {r['kind']}: {r['name']} {pct(r['before'])} → {pct(r['now'])}" for r in a["fading"][:10]]
        if a["tag_growth"]:
            L += ["", "Tag growth (catalog counts): " + ", ".join(
                f"{t['tag']} +{t['gain']}" + (f" ({t['pct'] * 100:.1f}%)" if t["pct"] is not None else "") for t in a["tag_growth"][:12])]
    if a["tags_now"]:
        L += ["", "## Biggest tags right now (catalog totals)", "",
              ", ".join(f"{t['tag']} {t['count']:,}" for t in a["tags_now"][:20])]
    b = a["brief"]
    L += ["", "## Design brief for ORIGINAL cast (INFERRED)", "",
          "Combine 2-3 of the top features and the top palette with OUR silhouette, name and story role. "
          "Never trace, recolour or upload an observed skin; third-party characters are excluded below.", "",
          "- Archetypes to riff on: " + (", ".join(f"{k} ({pct(v)})" for k, v in b["archetypes"]) or "-"),
          "- Features: " + (", ".join(k for k, _ in b["features"]) or "-"),
          "- Palette: " + (", ".join(k for k, _ in b["palette"]) or "-"),
          "- Blocked (trend exists, IP belongs to others): " + (", ".join(a["blocked_ip_archetypes"]) or "none")]
    return "\n".join(L) + "\n"


def main_skins(args) -> int:
    src = Path(args.input)
    skins, tags, meta = load_skin_observations(src)
    if not skins and not tags:
        print("BAD_INPUT::no skin or tag rows")
        return 2
    as_of = to_date(args.as_of or meta.get("observed") or "") or datetime.now(timezone.utc).date()
    prev, prev_src, days = None, None, None
    if args.previous:
        prev_src = Path(args.previous)
        if not prev_src.is_file():
            print(f"BAD_INPUT::{prev_src} not found")
            return 2
        prev = load_skin_observations(prev_src)
        pd = to_date(prev[2].get("observed") or "")
        days = float((as_of - pd).days) if pd and as_of > pd else None
    a = analyse_skins(skins, tags, prev, days)
    md = skins_to_markdown(a, src, as_of, prev_src)
    out = Path(args.out) if args.out else src.with_name(src.stem + "_skins.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    if args.json:
        Path(args.json).write_text(json.dumps(a, ensure_ascii=False, indent=2), encoding="utf-8")
    top = next(iter(a["brief"]["archetypes"]), ("-", 0))[0]
    print(f"SKINS_OK::{out}::skins={a['skins']}::tags={len(tags)}::top={top}::blocked_ip={len(a['blocked_ip_archetypes'])}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", help="JSON or CSV list of videos")
    p.add_argument("--niche", default="")
    p.add_argument("--as-of", default="", help="YYYY-MM-DD (default today)")
    p.add_argument("--outlier-x", type=float, default=3.0)
    p.add_argument("--short-seconds", type=float, default=180)
    p.add_argument("--out", default="")
    p.add_argument("--json", default="")
    p.add_argument("--kind", choices=("videos", "skins"), default="videos")
    p.add_argument("--previous", default="", help="skins: earlier observation file to compare with")
    args = p.parse_args(argv)
    src = Path(args.input)
    if args.kind == "skins":
        if not src.is_file():
            print(f"BAD_INPUT::{src} not found")
            return 2
        return main_skins(args)
    if not src.is_file():
        print(f"BAD_INPUT::{src} not found")
        return 2
    rows = load(src)
    if not rows:
        print("BAD_INPUT::no rows with a view count")
        return 2
    as_of = to_date(args.as_of) if args.as_of else datetime.now(timezone.utc).date()
    a = analyse(rows, as_of, args.outlier_x, args.short_seconds)
    md = to_markdown(a, args.niche, src, as_of, args.outlier_x)
    out = Path(args.out) if args.out else src.with_name(src.stem + "_stats.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    if args.json:
        slim = {k: v for k, v in a.items() if k not in ("outliers", "fresh")}
        slim["outliers"] = [{k: (str(v) if isinstance(v, date) else v) for k, v in r.items()} for r in a["outliers"]]
        Path(args.json).write_text(json.dumps(slim, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"STATS_OK::{out}::videos={a['videos']}::median={a['median']:.0f}::outliers={len(a['outliers'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
