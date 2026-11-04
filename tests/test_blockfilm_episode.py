"""blockfilm episodes: script, recorded timeline and picture code must agree on beat ids and timing."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "tools" / "blockfilm"
EPISODES = sorted(p for p in ROOT.iterdir() if (p / "script.json").exists()) if ROOT.exists() else []


@pytest.mark.parametrize("ep", EPISODES, ids=[p.name for p in EPISODES])
def test_script_timeline_picture_agree(ep):
    script = json.loads((ep / "script.json").read_text(encoding="utf-8"))
    ids = [b["id"] for b in script]
    assert len(ids) == len(set(ids)), "duplicate beat ids"
    for b in script:
        assert b["who"] and b["text"].strip()

    tl = json.loads((ep / "web" / "timeline.json").read_text(encoding="utf-8"))
    assert [b["id"] for b in tl["beats"]] == ids, "timeline out of date: re-run tts.py"
    prev_end = 0.0
    for b in tl["beats"]:
        assert b["start"] >= prev_end - 1e-6, f"beat {b['id']} overlaps the previous line"
        assert b["dur"] > 0
        prev_end = b["start"] + b["dur"]
    assert tl["total"] >= prev_end

    html = (ep / "web" / "index.html").read_text(encoding="utf-8")
    used = set(re.findall(r"\b[SE]\('([A-Za-z0-9_]+)'\)", html))
    assert used, "picture code references no beats"
    assert used <= set(ids), f"picture references unknown beats: {sorted(used - set(ids))}"

    audio = ep / "audio.py"
    if audio.exists():
        cues = set(re.findall(r"\b[SE]\('([A-Za-z0-9_]+)'\)", audio.read_text(encoding="utf-8")))
        assert cues <= set(ids), f"sound cues reference unknown beats: {sorted(cues - set(ids))}"


def test_episodes_exist():
    assert EPISODES, "no blockfilm episode folders found"
