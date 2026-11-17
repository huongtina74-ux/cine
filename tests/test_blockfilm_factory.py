"""blockfilm Shorts factory: every SPEC builds, the page runs, the story timeline is sane and every cue has a sound."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

F = Path(__file__).resolve().parents[1] / "tools" / "blockfilm" / "factory"
sys.path.insert(0, str(F))
SPECS = sorted((F / "specs").glob("*.json"))
NODE_OK = shutil.which("node") and (F.parent / "ep03_zombie_outbreak/web/node_modules/playwright").exists()


@pytest.mark.parametrize("spec", SPECS, ids=[s.stem for s in SPECS])
def test_spec_builds(spec, tmp_path):
    import build
    page = build.build(spec, tmp_path).read_text(encoding="utf-8")
    assert 'width="1080" height="1920"' in page and "const SPEC=" in page
    s = json.loads(spec.read_text(encoding="utf-8"))
    assert s["winner"] in s["lanes"] and {a["who"] for a in s["attempts"]} == set(s["lanes"])


def test_bad_spec_rejected(tmp_path):
    import build
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"id": "x", "title": ["A", "B"], "challenge": "swim", "lanes": ["bin"], "attempts": []}))
    with pytest.raises(AssertionError):
        build.build(bad, tmp_path / "o")


@pytest.mark.skipif(not NODE_OK, reason="node + playwright not installed")
@pytest.mark.parametrize("spec", SPECS, ids=[s.stem for s in SPECS])
def test_page_runs_and_timeline(spec, tmp_path):
    import audio
    import build
    build.build(spec, tmp_path)
    r = subprocess.run(["node", str(F / "render.js"), str(tmp_path / "web"), "cues", str(tmp_path / "cues.json")],
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0 and "PAGEERR" not in r.stdout, r.stdout + r.stderr
    c = json.loads((tmp_path / "cues.json").read_text())
    assert 12 <= c["total"] <= 40 and c["total"] % 2 == 0          # Shorts length, whole bars at 120 bpm
    seg = c["seg"]
    assert seg[0]["t0"] == 0 and abs(seg[-1]["t1"] - c["total"]) < 1e-6
    assert all(abs(a["t1"] - b["t0"]) < 1e-6 for a, b in zip(seg, seg[1:]))   # no gaps, no overlaps
    assert seg[0]["t1"] <= 0.5                                       # the contest starts inside the first half-second
    assert any(s["type"] == "win" for s in seg) and seg[-1]["type"] == "loop"
    assert all(0 <= q["t"] <= c["total"] for q in c["cues"])
    m = audio.mix(str(tmp_path / "cues.json"), str(tmp_path / "mix.wav"))   # raises if a cue has no sound
    assert m["cues"] == len(c["cues"]) and (tmp_path / "mix.wav").stat().st_size > 100_000
