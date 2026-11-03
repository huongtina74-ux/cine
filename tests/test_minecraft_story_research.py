"""Daily Minecraft-story competitor loop: files the next run reads must stay machine-readable."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH = ROOT / "config" / "research" / "minecraft_story_watchlist.txt"
PRINCIPLES = ROOT / "reports" / "research" / "minecraft_story_principles.md"
SNAPS = ROOT / "reports" / "research" / "snapshots"
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def test_watchlist_rows_have_eight_fields_and_a_role():
    rows = [l for l in WATCH.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    assert len(rows) >= 10
    ids = set()
    for l in rows:
        f = [x.strip() for x in l.split("|")]
        assert len(f) == 8, l
        assert f[0].startswith("UC") and f[2].startswith("@")
        assert f[5] in ("leader", "new") and DATE.search(f[6])
        ids.add(f[0])
    assert len(ids) == len(rows), "duplicate channel in watchlist"


def test_principles_split_long_and_short_term_with_dates_and_evidence():
    md = PRINCIPLES.read_text(encoding="utf-8")
    long_part, short_part = md.split("## Nguyên tắc dài hạn")[1].split("## Nguyên tắc ngắn hạn")
    longs = re.split(r"\n### L\d+", long_part)[1:]
    shorts = re.split(r"\n### S\d+", short_part.split("\n## ")[0])[1:]
    assert longs and shorts
    for block in longs + shorts:
        assert "youtube.com/watch?v=" in block and "OBSERVED" in block
    for block in shorts:
        assert re.search(r"(first seen|Lần đầu thấy):? \d{4}-\d{2}-\d{2}", block)
        assert re.search(r"(last seen|Lần cuối thấy):? \d{4}-\d{2}-\d{2}", block)


def test_snapshots_parse_for_tomorrows_compare():
    files = sorted(SNAPS.glob("*_minecraft_story.csv"))
    assert files
    with files[-1].open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and all(r["url"].startswith("https://") and int(r["views"]) >= 0 and DATE.fullmatch(r["as_of"]) for r in rows)
