"""Complete-episode pipeline: set pieces in planning, sound cues, music/SFX synthesis, assembly timing."""
from __future__ import annotations

import json
import sys
import wave
from pathlib import Path

import numpy as np
import pytest

from cinefactory.animal_long_slide.contracts import LongSlideSceneKind
from cinefactory.animal_long_slide.director import GIMMICK_SCENES, VariationDirector
from cinefactory.animal_long_slide.motion import MotionCompatibilityGraph
from cinefactory.animal_long_slide.registry import LongSlideAssetRegistry
from cinefactory.animal_long_slide.series import PERIL_OBSTACLES, PERIL_SCENES, SeriesBible
from cinefactory.animal_long_slide.variation import EpisodeHistory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import assemble_long_slide_episode as assembler  # noqa: E402
import long_slide_audio as audio  # noqa: E402
import long_slide_events as cues  # noqa: E402
import make_long_slide_episode as maker  # noqa: E402

PREVIEW_BIBLE = ROOT / "config" / "animal_long_slide" / "series_bible_preview.yaml"


def _plan(seed=21, **kwargs):
    director = VariationDirector(SeriesBible.load(PREVIEW_BIBLE), EpisodeHistory(), nominal_module_seconds=9.5, **kwargs)
    return director.next_episode(project_id="STU_EP", episode_id="EP_T", target_duration_seconds=66, seed=seed)


# ---------- planning ----------

def test_preview_bible_cast_is_renderable_today():
    registry = LongSlideAssetRegistry.load(ROOT)
    renderable = maker.renderable_animals(registry, MotionCompatibilityGraph.load(ROOT))
    bible = SeriesBible.load(PREVIEW_BIBLE)
    assert {c.animal_id for c in bible.cast} <= renderable
    assert bible.brand == SeriesBible.default().brand


def test_short_modules_give_a_full_shot_list():
    varied = _plan()
    assert len(varied.episode.modules) == 7
    assert all(9.0 <= m.duration_seconds <= 10.0 for m in varied.episode.modules)
    with pytest.raises(ValueError):
        VariationDirector(SeriesBible.default(), EpisodeHistory(), nominal_module_seconds=3)


def test_set_pieces_open_and_close_the_episode_without_repeats():
    for seed in range(21, 31):
        modules = _plan(seed).episode.modules
        gimmicks = [m.metadata["gimmicks"] for m in modules]
        assert gimmicks[0][0] == "door_reveal"
        assert all("door_reveal" not in g for g in gimmicks[1:])
        for module, picked in zip(modules, gimmicks):
            peril = module.scene_kind in PERIL_SCENES or any(o.obstacle_id in PERIL_OBSTACLES for o in module.obstacles)
            for g in picked:
                if g != "door_reveal":
                    assert not peril and module.scene_kind in GIMMICK_SCENES[g]
            if "clone_parade" in picked:
                assert module.metadata["companions"] == []
        for a, b in zip(gimmicks, gimmicks[1:]):
            assert not ({x for x in a if x != "door_reveal"} & set(b))
        finale = modules[-1]
        if finale.scene_kind not in PERIL_SCENES:
            assert "clone_parade" in gimmicks[-1] or "clone_parade" in gimmicks[-2]


def test_blocked_scenes_are_never_planned():
    for seed in range(21, 27):
        modules = _plan(seed, blocked_scenes={LongSlideSceneKind.SPIRAL_SLIDE}).episode.modules
        assert all(m.scene_kind is not LongSlideSceneKind.SPIRAL_SLIDE for m in modules)
    with pytest.raises(ValueError):
        VariationDirector(SeriesBible.default(), EpisodeHistory(),
                          blocked_scenes=set(LongSlideSceneKind) - {LongSlideSceneKind.LONG_SLIDE})


# ---------- sound cues ----------

def test_cue_recorder_round_trip(tmp_path):
    cues.reset()
    cues.record(40, "smash", lane=0.0)
    cues.record(12, "door_open")
    with pytest.raises(ValueError):
        cues.record(3, "explosion")
    clip = tmp_path / "0001_LSM_001.mp4"
    path = cues.dump(clip, fps=24, frames=226)
    assert path == tmp_path / "0001_LSM_001.events.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [e["frame"] for e in data["events"]] == [12, 40]
    assert data["fps"] == 24 and data["frames"] == 226
    cues.reset()
    assert cues.events() == []


def test_episode_cues_are_offset_per_clip(tmp_path):
    clips = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
    (tmp_path / "a.events.json").write_text(json.dumps({"fps": 24, "events": [{"frame": 25, "kind": "smash"}]}))
    (tmp_path / "b.events.json").write_text(json.dumps({"fps": 24, "events": [
        {"frame": 1, "kind": "race_start"}, {"frame": 999, "kind": "pickup_pop"}]}))
    timeline = assembler.episode_cues(clips, [10.0, 8.0], intro=3.0)
    assert (4.0, "smash") in timeline
    assert (13.0, "race_start") in timeline
    assert all(kind != "pickup_pop" for _, kind in timeline)  # beyond its clip
    assert [t for t, k in timeline if k == "whoosh"] == [pytest.approx(2.8), pytest.approx(12.8)]
    assert timeline[-1] == (pytest.approx(21.2), "finish")
    assert timeline == sorted(timeline)


# ---------- synthesis ----------

def test_music_varies_by_seed_and_stays_in_range():
    assert audio.music_plan(7) == audio.music_plan(7)
    assert len({tuple(sorted(audio.music_plan(s).items())) for s in range(10)}) > 3
    music = audio.synth_music(6.0, seed=3)
    assert music.shape == (6 * audio.SR, 2)
    assert np.isfinite(music).all() and np.max(np.abs(music)) <= 1.0
    assert np.sqrt(np.mean(music ** 2)) > 0.02


@pytest.mark.parametrize("kind", sorted(cues.KINDS | {"whoosh"}))
def test_every_cue_kind_has_a_sound(kind):
    sound = audio.synth_cue(kind, seed=1)
    assert 0.05 * audio.SR < len(sound) <= 1.2 * audio.SR
    assert np.isfinite(sound).all() and np.max(np.abs(sound)) > 0.05


def test_mix_is_limited_and_written_as_stereo_wav(tmp_path):
    mix = audio.mix_episode(4.0, [(0.5, "smash"), (1.0, "pickup_pop"), (3.9, "finish")], seed=2)
    assert np.max(np.abs(mix)) <= 0.95 + 1e-6
    path = audio.write_wav(tmp_path / "m.wav", mix)
    with wave.open(str(path)) as handle:
        assert handle.getnchannels() == 2 and handle.getframerate() == audio.SR
        assert handle.getnframes() == len(mix)
    with pytest.raises(ValueError):
        audio.synth_cue("explosion")


# ---------- cards ----------

def test_title_card_animates_and_wraps_long_titles():
    size = (640, 360)
    title = "Finn, Pip & Hazel Team Up for the Candy Hills Slide Relay"
    first = assembler.card_frame(size, title, "Let's go!", "Zoomi Slide Club", 0.0)
    settled = assembler.card_frame(size, title, "Let's go!", "Zoomi Slide Club", 1.0)
    assert first.size == size and settled.size == size
    assert first.tobytes() != settled.tobytes()
    assert assembler._ease_back(0.0) == pytest.approx(0.0)
    assert assembler._ease_back(1.0) == pytest.approx(1.0)
    assert max(assembler._ease_back(x / 20) for x in range(21)) > 1.0  # overshoot = bounce


def test_episode_maker_rejects_unsafe_ids(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["make", "--episode", "../evil", "--plan-only"])
    assert maker.main() == maker.EXIT_BAD_INPUT
    assert "BAD_INPUT" in capsys.readouterr().out


# ---------- review hardening ----------

def test_cues_are_levelled_before_mixing():
    loud = audio.mix_episode(2.0, [(0.2, "smash")], seed=1)
    soft = audio.mix_episode(2.0, [(0.2, "door_open")], seed=1)
    assert np.max(np.abs(loud)) <= 0.95 + 1e-6 and np.max(np.abs(soft)) > 0.1
    assert audio.synth_music(3.0, seed=1).dtype == np.float32


def test_long_reverb_matches_one_shot_convolution():
    rng = np.random.default_rng(0)
    sig = rng.uniform(-1, 1, audio.REVERB_BLOCK * 2 + 1234).astype(np.float32)
    chunked = audio._reverb(sig, seconds=0.3, mix=0.5, seed=4)
    ir_rng = np.random.default_rng(4)
    t = audio._t(0.3)
    ir = (audio._noise(len(t), ir_rng) * np.exp(-t * 5.0)).astype(np.float32)
    ir[0] = 0.0
    wet = np.convolve(sig, ir)[: len(sig)]
    wet *= np.max(np.abs(sig)) / np.max(np.abs(wet))
    assert np.allclose(chunked, sig + 0.5 * wet, atol=2e-3)


def test_resume_only_reuses_complete_clips_from_the_same_job(tmp_path, monkeypatch):
    class Job:
        def __init__(self, text):
            self.text = text

        def model_dump_json(self):
            return self.text

    clip = tmp_path / "0001_LSM_001.mp4"
    clip.write_bytes(b"x" * 4096)
    cues.sidecar_path(clip).write_text(json.dumps({"fps": 24, "frames": 226, "events": []}), encoding="utf-8")
    job = Job('{"module": "a", "seed": 21}')
    assert not maker.reusable(job, clip)  # no stamp from a finished render
    maker.stamp_path(clip).write_text(maker.job_stamp(job), encoding="utf-8")
    monkeypatch.setattr(maker, "frame_count", lambda path: 226)
    assert maker.reusable(job, clip)
    assert not maker.reusable(Job('{"module": "a", "seed": 22}'), clip)  # different plan
    monkeypatch.setattr(maker, "frame_count", lambda path: 120)
    assert not maker.reusable(job, clip)  # truncated clip


def test_binder_makes_worker_errors_fatal_and_drops_stale_clips(tmp_path, monkeypatch):
    from cinefactory.animal_long_slide import blender_binder as binder_module

    calls = {}

    class Result:
        returncode = 1
        stdout = ""
        stderr = "boom"

    def fake_run(command, **kwargs):
        calls["command"] = command
        return Result()

    fake_blender = tmp_path / "blender.exe"
    fake_blender.write_bytes(b"")
    binder = binder_module.LongSlideBlenderBinder(ROOT, blender_executable=fake_blender)
    stale = tmp_path / "stale.mp4"
    stale.write_bytes(b"x" * 5000)
    monkeypatch.setattr(binder, "compile_payload", lambda job: {"output_path": str(stale)})

    class Job:
        project_id, episode_id = "P", "E"

        class module:
            module_id = "LSM_TEST"

    monkeypatch.setattr(binder_module.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError):
        binder.execute(Job())
    assert not stale.exists()
    command = calls["command"]
    assert command[command.index("--python-exit-code") + 1] == "1"
    assert command.index("--python-exit-code") < command.index("--python")


def test_assembler_checks_tools_and_skips_leftover_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(assembler.shutil, "which", lambda tool: None)
    with pytest.raises(RuntimeError, match="ffmpeg"):
        assembler.require_tools()
    (tmp_path / "modules").mkdir()
    (tmp_path / "modules" / "0001_LSM_001.mp4").write_bytes(b"")
    (tmp_path / "assemble_x").mkdir()
    (tmp_path / "assemble_x" / "intro.mp4").write_bytes(b"")
    found = []
    monkeypatch.setattr(assembler, "assemble", lambda clips, out, **kw: found.extend(clips) or out)
    monkeypatch.setattr(sys, "argv", ["asm", "--clips", str(tmp_path), "--title", "t", "--brand", "b",
                                      "--out", str(tmp_path / "episode.mp4")])
    assert assembler.main() == 0
    assert [p.name for p in found] == ["0001_LSM_001.mp4"]


def test_episode_maker_reports_bad_lengths(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["make", "--episode", "EP_OK", "--module-seconds", "2", "--plan-only"])
    assert maker.main() == maker.EXIT_BAD_INPUT
    assert "BAD_INPUT" in capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", ["make", "--episode", "EP_OK\n", "--plan-only"])
    assert maker.main() == maker.EXIT_BAD_INPUT
