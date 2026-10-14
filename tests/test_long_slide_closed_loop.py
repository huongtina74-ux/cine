"""Closed loop: the plan the owner greenlights is the episode that gets rendered, edited, checked and handed off.

Covers cinefactory.animal_long_slide.capability, scripts/plan_long_slide_series.py (--check/--greenlight),
scripts/make_long_slide_episode.py --varied, scripts/produce_long_slide_episode.py and the tools/cf_* steps.
The end-to-end test swaps Blender for a stand-in that writes a test-pattern clip and a sound-cue sidecar,
so it runs anywhere ffmpeg is installed.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from cinefactory.animal_long_slide.capability import (
    PROVEN_MODULE_SECONDS,
    LongSlideCapability,
    read_greenlight,
    write_greenlight,
)
from cinefactory.animal_long_slide.series import SeriesBible
from cinefactory.animal_long_slide.variation import EpisodeHistory, VariedEpisode

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
FULL_BIBLE = ROOT / "config" / "animal_long_slide" / "series_bible.yaml"
HAS_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


@pytest.fixture(scope="module")
def cap() -> LongSlideCapability:
    return LongSlideCapability.detect(ROOT)


def _plan(cap: LongSlideCapability, *, seconds: float = 40.0, seed: int = 404) -> VariedEpisode:
    bible = SeriesBible.load(cap.default_bible_path())
    return cap.director(bible, EpisodeHistory()).next_episode(
        project_id="CH_test", episode_id="EP_0901", target_duration_seconds=seconds, seed=seed)


def _run(*args: str, cwd: Path = ROOT, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([PY, *args], cwd=cwd, capture_output=True, text=True, env=env)


# ---------------------------------------------------------------- capability

def test_capability_is_measured_from_assets_and_motions(cap):
    assert cap.renderable, "no animal can be rendered: asset registry or motion graph is broken"
    assert cap.module_seconds == PROVEN_MODULE_SECONDS


def test_default_bible_cast_is_renderable(cap):
    bible = SeriesBible.load(cap.default_bible_path())
    assert cap.unrenderable_cast(bible) == []


def test_full_bible_plans_are_flagged_when_cast_cannot_be_animated(cap):
    full = SeriesBible.load(FULL_BIBLE)
    if not cap.unrenderable_cast(full):
        pytest.skip("full cast is renderable now; nothing to flag")
    from cinefactory.animal_long_slide.director import VariationDirector
    varied = VariationDirector(full, EpisodeHistory()).next_episode(
        project_id="CH_test", episode_id="EP_0902", target_duration_seconds=330, seed=101)
    check = cap.check(varied)
    if {m.animal_id for m in varied.episode.modules} <= cap.renderable:
        pytest.skip("this seed happened to pick renderable animals only")
    assert not check.executable
    assert check.unrenderable_animals


def test_capability_plans_are_renderable_and_use_proven_module_length(cap):
    varied = _plan(cap, seconds=90)
    check = cap.check(varied)
    assert check.executable, check.blockers
    assert all(abs(s - 9.0) <= 1.0 for s in check.module_seconds)
    assert not check.blocked_scenes


def test_greenlight_only_counts_for_the_exact_plan(cap, tmp_path):
    varied = _plan(cap)
    write_greenlight(tmp_path, varied, by="owner")
    assert read_greenlight(tmp_path, varied)["by"] == "owner"
    other = _plan(cap, seed=405)
    assert read_greenlight(tmp_path, other) is None


# ---------------------------------------------------------------- CLI flow (no rendering)

@pytest.fixture()
def series_dir(tmp_path) -> Path:
    return tmp_path / "series"


def test_planner_checks_greenlights_and_renderer_renders_the_plan(series_dir):
    out = _run("scripts/plan_long_slide_series.py", "--channel", "testch", "--data-dir", str(series_dir),
               "--duration", "40")
    assert out.returncode == 0, out.stdout + out.stderr
    folder = series_dir / "testch" / "episodes" / "EP_0001"
    assert json.loads((folder / "render_check.json").read_text())["executable"] is True
    title = VariedEpisode.model_validate_json((folder / "varied_episode.json").read_text()).package.title

    refused = _run("scripts/make_long_slide_episode.py", "--varied", str(folder / "varied_episode.json"))
    assert refused.returncode == 8 and "NOT_GREENLIT" in refused.stdout

    ok = _run("scripts/plan_long_slide_series.py", "--channel", "testch", "--data-dir", str(series_dir),
              "--greenlight", "EP_0001", "--by", "owner")
    assert ok.returncode == 0 and (folder / "greenlight.json").is_file(), ok.stdout

    planned = _run("scripts/make_long_slide_episode.py", "--varied", str(folder / "varied_episode.json"), "--plan-only")
    assert planned.returncode == 0, planned.stdout + planned.stderr
    assert f"TITLE::{title}" in planned.stdout  # the rendered episode IS the greenlit plan


def test_greenlight_refuses_a_plan_the_factory_cannot_render(cap, series_dir):
    full = SeriesBible.load(FULL_BIBLE)
    if not cap.unrenderable_cast(full):
        pytest.skip("full cast is renderable now")
    out = _run("scripts/plan_long_slide_series.py", "--channel", "testch", "--data-dir", str(series_dir),
               "--bible", str(FULL_BIBLE), "--duration", "330", "--allow-unrenderable", "--seed", "101")
    assert out.returncode == 0, out.stdout
    check = json.loads((series_dir / "testch" / "episodes" / "EP_0001" / "render_check.json").read_text())
    if check["executable"]:
        pytest.skip("seed picked renderable animals")
    gl = _run("scripts/plan_long_slide_series.py", "--channel", "testch", "--data-dir", str(series_dir),
              "--greenlight", "EP_0001")
    assert gl.returncode == 5 and "REJECTED" in gl.stdout


# ---------------------------------------------------------------- end to end with a stand-in Blender

FAKE_BLENDER = textwrap.dedent('''\
    import json, subprocess, sys
    job = json.load(open(sys.argv[sys.argv.index("--job") + 1]))
    fps, dur = job["fps"], float(job["module"]["duration_seconds"])
    frames = int(round(dur * fps))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"testsrc2=size={job['width']}x{job['height']}:rate={fps}", "-frames:v", str(frames),
                    "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "ultrafast", job["output_path"]], check=True)
    json.dump({"fps": fps, "frames": frames, "events": [{"frame": 1, "kind": "race_start"},
               {"frame": frames // 2, "kind": "pickup_pop"}]}, open(job["output_path"][:-4] + ".events.json", "w"))
''')


@pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg/ffprobe not installed")
def test_one_command_from_greenlit_plan_to_handoff(tmp_path, series_dir):
    worker = tmp_path / "fake_blender.py"
    worker.write_text(FAKE_BLENDER, encoding="utf-8")
    if os.name == "nt":
        blender = tmp_path / "blender.cmd"
        blender.write_text(f'@"{PY}" "{worker}" %*\r\n', encoding="utf-8")
    else:
        blender = tmp_path / "blender"
        blender.write_text(f'#!/bin/sh\nexec "{PY}" "{worker}" "$@"\n', encoding="utf-8")
        blender.chmod(blender.stat().st_mode | stat.S_IEXEC)
    assert _run("scripts/plan_long_slide_series.py", "--channel", "testch", "--data-dir", str(series_dir),
                "--duration", "40").returncode == 0
    assert _run("scripts/plan_long_slide_series.py", "--channel", "testch", "--data-dir", str(series_dir),
                "--greenlight", "EP_0001").returncode == 0
    ledger = ROOT / "data" / "production_ledger.jsonl"
    decisions = ROOT / "data" / "decisions.jsonl"
    before = {p: p.read_bytes() if p.is_file() else None for p in (ledger, decisions)}
    env = {**os.environ, "CF_DECISION_LOG": str(tmp_path / "decisions.jsonl")}
    try:
        out = _run("scripts/produce_long_slide_episode.py", "--channel", "testch", "--episode", "EP_0001",
                   "--data-dir", str(series_dir), "--blender", str(blender), "--res", "1280x720", env=env)
    finally:
        for path, data in before.items():  # never leave test rows in the real ledgers
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(data)
        shutil.rmtree(ROOT / "data" / "animal_long_slide" / "jobs" / "CH_testch", ignore_errors=True)
    folder = series_dir / "testch" / "episodes" / "EP_0001"
    assert out.returncode == 0, out.stdout[-3000:] + out.stderr[-2000:]
    state = json.loads((folder / "production.json").read_text())["stages"]
    assert [s for s in ("gate", "render", "cut", "edit", "qc", "policy", "handoff") if state[s]["status"] != "done"] == []
    assert (folder / "edit" / "EP_0001_edit.mp4").is_file()
    assert "QC: PASS" in (folder / "HANDOFF.md").read_text(encoding="utf-8")
    qc = json.loads((folder / "edit" / "EP_0001_edit.qc.json").read_text())
    assert -16.0 <= qc["analysis"]["loudness"]["integrated_lufs"] <= -12.0  # music bed + real mastering
