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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", help="JSON or CSV list of videos")
    p.add_argument("--niche", default="")
    p.add_argument("--as-of", default="", help="YYYY-MM-DD (default today)")
    p.add_argument("--outlier-x", type=float, default=3.0)
    p.add_argument("--short-seconds", type=float, default=180)
    p.add_argument("--out", default="")
    p.add_argument("--json", default="")
    args = p.parse_args(argv)
    src = Path(args.input)
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
