"""MC-S1 Short #01: the 9:16 page assembles, and the sound cues stay locked to the picture timings."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "tools" / "blockfilm" / "s01_bounce"


def test_build_makes_vertical_page(tmp_path):
    subprocess.run([sys.executable, "build.py"], cwd=ROOT, check=True, capture_output=True)
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    assert "const W=1080,H=1920" in html and 'width="1080" height="1920"' in html
    assert "window.init=" in html and "window.renderAt=renderAt" in html
    assert html.count("const BIN=makeChar") == 1


def test_audio_cues_match_story_constants():
    js = (ROOT / "web" / "s01_story.js").read_text(encoding="utf-8")
    consts = dict(re.findall(r"(ZL|ZOFF|ZBACK|ZLAND)=([\d.]+)", js))
    assert consts == {"ZL": "12.40", "ZOFF": "15.0", "ZBACK": "17.0", "ZLAND": "17.45"}
    audio = (ROOT / "audio.py").read_text(encoding="utf-8")
    for t in ("12.40", "17.45", "0.30" if "0.30" in audio else ".30", "4.40", "5.20", "9.00"):
        assert t in audio, t
    assert "TOTAL = 18.0" in audio and "const TOTAL=18;" in js
