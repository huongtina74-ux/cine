"""Procedural music and sound effects for Long Slide episodes (numpy only).

Everything is synthesised locally, so there is no licence to clear and no
metered API. The music bed is a cheerful major-key loop (bass, strummed
chords, marimba melody, light drums) generated from the episode seed, so each
episode gets its own tempo, key, progression and melody. Sound cues from the
render sidecars become short effects at the exact frame, and the music ducks
slightly under them.
"""
from __future__ import annotations

import random
import wave
from pathlib import Path

import numpy as np

SR = 44100
MAJOR = (0, 2, 4, 5, 7, 9, 11)
PENTATONIC = (0, 2, 4, 7, 9)
PROGRESSIONS = (
    (0, 4, 5, 3),  # I V vi IV
    (0, 3, 4, 0),  # I IV V I
    (0, 5, 3, 4),  # I vi IV V
    (0, 3, 0, 4),  # I IV I V
)
KEYS = (60, 62, 65, 67)  # C, D, F, G
MELODY_RHYTHMS = (
    (1.0, 0.5, 0.5, 1.0, 1.0),
    (0.5, 0.5, 0.5, 0.5, 1.0, 1.0),
    (1.5, 0.5, 1.0, 1.0),
    (0.5, 0.5, 1.0, 0.5, 0.5, 1.0),
)
CUE_GAIN = {
    "pickup_pop": 0.55, "paint_splash": 0.6, "smash": 0.8, "door_open": 0.55,
    "clone_pop": 0.5, "race_start": 0.6, "finish": 0.6, "whoosh": 0.35,
}
CUE_PEAK = 0.9


def hz(midi: float) -> float:
    return 440.0 * 2.0 ** ((midi - 69.0) / 12.0)


def _t(seconds: float) -> np.ndarray:
    return np.arange(int(seconds * SR)) / SR


def _env(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0.0, 1.0)
    return a * np.exp(-t / max(decay, 1e-4))


def _add(buf: np.ndarray, sig: np.ndarray, start: float, gain: float = 1.0) -> None:
    i = int(start * SR)
    if i >= len(buf) or i + len(sig) <= 0:
        return
    j = min(len(buf), i + len(sig))
    lo = max(0, i)
    buf[lo:j] += gain * sig[lo - i:j - i]


def _noise(n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(-1.0, 1.0, n)


def _lowpass(sig: np.ndarray, width: int) -> np.ndarray:
    if width <= 1:
        return sig
    kernel = np.ones(width) / width
    return np.convolve(sig, kernel, mode="same")


# ---------- instruments ----------

def _bass(freq: float, dur: float) -> np.ndarray:
    t = _t(dur)
    tri = 2.0 * np.abs(2.0 * ((t * freq) % 1.0) - 1.0) - 1.0
    sig = 0.7 * tri + 0.5 * np.sin(2 * np.pi * freq * 0.5 * t)
    return sig * _env(len(t), 0.005, dur * 0.6)


def _pluck(freq: float, dur: float) -> np.ndarray:
    t = _t(dur)
    sig = sum(a * np.sin(2 * np.pi * freq * k * t) * np.exp(-t * (3 + 4 * k))
              for k, a in ((1, 1.0), (2, 0.5), (3, 0.28), (4, 0.15), (5, 0.08)))
    return sig * _env(len(t), 0.003, 0.5)


def _marimba(freq: float, dur: float) -> np.ndarray:
    t = _t(dur)
    sig = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 3.93 * t) * np.exp(-t * 18)
    return sig * _env(len(t), 0.002, 0.32)


def _kick(rng: np.random.Generator) -> np.ndarray:
    t = _t(0.3)
    freq = 45 + 90 * np.exp(-t * 28)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    return np.sin(phase) * np.exp(-t * 11)


def _snare(rng: np.random.Generator) -> np.ndarray:
    t = _t(0.18)
    noise = np.diff(_noise(len(t) + 1, rng))
    return (0.7 * noise + 0.4 * np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 24)


def _hat(rng: np.random.Generator) -> np.ndarray:
    t = _t(0.05)
    noise = np.diff(np.diff(_noise(len(t) + 2, rng)))
    return noise * np.exp(-t * 90) * 0.5


REVERB_BLOCK = 1 << 18


def _reverb(sig: np.ndarray, seconds: float = 1.1, mix: float = 0.18, seed: int = 0) -> np.ndarray:
    """Noise-tail convolution reverb, overlap-add in blocks so memory stays flat for long episodes."""
    rng = np.random.default_rng(seed)
    ir_t = _t(seconds)
    ir = (_noise(len(ir_t), rng) * np.exp(-ir_t * 5.0)).astype(np.float32)
    ir[0] = 0.0
    size = 1 << (REVERB_BLOCK + len(ir) - 2).bit_length()
    ir_f = np.fft.rfft(ir, size)
    wet = np.zeros(len(sig) + len(ir), dtype=np.float32)
    for start in range(0, len(sig), REVERB_BLOCK):
        block = sig[start:start + REVERB_BLOCK]
        out = np.fft.irfft(np.fft.rfft(block, size) * ir_f, size)[: len(block) + len(ir) - 1]
        wet[start:start + len(out)] += out.astype(np.float32)
    wet = wet[: len(sig)]
    wet *= np.max(np.abs(sig)) / max(float(np.max(np.abs(wet))), 1e-9)
    return (sig + mix * wet).astype(np.float32)


# ---------- music ----------

def music_plan(seed: int) -> dict:
    rng = random.Random(seed * 2654435761 % (2 ** 31))
    return {
        "bpm": rng.choice((116, 120, 124, 128)),
        "key": rng.choice(KEYS),
        "progression": rng.choice(PROGRESSIONS),
        "melody_seed": rng.randrange(1 << 30),
    }


def _chord(key: int, degree: int) -> list[int]:
    return [key + MAJOR[(degree + step) % 7] + 12 * ((degree + step) // 7) for step in (0, 2, 4)]


def _melody(plan: dict, bars: int) -> list[tuple[float, float, int]]:
    """(beat, length, midi) notes; an A A' B A phrase shape, repeated."""
    rng = random.Random(plan["melody_seed"])
    key = plan["key"] + 12

    def phrase(start_degree):
        notes, beat, degree = [], 0.0, start_degree
        for _ in range(2):  # two bars
            rhythm = rng.choice(MELODY_RHYTHMS)
            for length in rhythm:
                degree = max(0, min(9, degree + rng.choice((-2, -1, 1, 1, 2))))
                octave, step = divmod(degree, 5)
                notes.append((beat, length, key + PENTATONIC[step] + 12 * octave))
                beat += length
        return notes

    a = phrase(2)
    a2 = [(b, l, m + (2 if i == len(a) - 1 else 0)) for i, (b, l, m) in enumerate(a)]
    b = phrase(5)
    shape = [a, a2, b, a]
    out = []
    for bar in range(0, bars, 2):
        for beat, length, midi in shape[(bar // 2) % 4]:
            out.append((bar * 4 + beat, length, midi))
    return out


def synth_music(duration: float, seed: int) -> np.ndarray:
    plan = music_plan(seed)
    beat = 60.0 / plan["bpm"]
    total = int(duration * SR) + SR
    bars = int(np.ceil(duration / (4 * beat))) + 1
    rng = np.random.default_rng(seed)
    bass = np.zeros(total, dtype=np.float32)
    chords = np.zeros(total, dtype=np.float32)
    melody = np.zeros(total, dtype=np.float32)
    drums = np.zeros(total, dtype=np.float32)
    for bar in range(bars):
        degree = plan["progression"][bar % 4]
        chord = _chord(plan["key"], degree)
        t0 = bar * 4 * beat
        for e in range(8):  # eighth notes
            t = t0 + e * beat / 2
            note = chord[0] - 24 if e % 4 != 3 else chord[2] - 24
            _add(bass, _bass(hz(note), beat * 0.45), t, 0.55)
            if e % 2 == 1:  # off-beat strum
                for k, midi in enumerate(chord):
                    _add(chords, _pluck(hz(midi), beat * 0.9), t + k * 0.012, 0.22)
            _add(drums, _hat(rng), t, 0.35 if e % 2 else 0.2)
        for b in range(4):
            t = t0 + b * beat
            if b in (0, 2):
                _add(drums, _kick(rng), t, 0.8)
            else:
                _add(drums, _snare(rng), t, 0.35)
    for start, length, midi in _melody(plan, bars):
        _add(melody, _marimba(hz(midi), max(0.25, length * beat)), start * beat, 0.42)
    chords = _reverb(chords, seed=seed)
    melody = _reverb(melody, seed=seed + 1)
    left = bass + drums * 0.9 + melody + chords * 0.85
    right = bass + drums * 0.9 + melody * 0.95 + np.roll(chords, int(0.013 * SR)) * 0.85
    mix = np.stack([left, right], axis=1)[: int(duration * SR)]
    fade = min(len(mix), int(1.5 * SR))
    mix[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    mix[: int(0.05 * SR)] *= np.linspace(0.0, 1.0, int(0.05 * SR))[:, None]
    return 0.5 * mix / max(np.max(np.abs(mix)), 1e-9)


# ---------- sound effects ----------

def synth_cue(kind: str, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    if kind == "pickup_pop":
        a = _marimba(hz(88), 0.12)
        b = _marimba(hz(95), 0.22)
        out = np.zeros(int(0.3 * SR))
        _add(out, a, 0.0)
        _add(out, b, 0.07)
        return out
    if kind == "paint_splash":
        t = _t(0.45)
        body = _lowpass(_noise(len(t), rng), 18) * np.exp(-t * 9) * 2.5
        for k, f in enumerate((700, 520, 880)):
            blip_t = _t(0.08)
            blip = np.sin(2 * np.pi * np.cumsum(f * (1.6 - 6 * blip_t)) / SR) * np.exp(-blip_t * 40)
            _add(body, blip, 0.05 + 0.07 * k, 0.5)
        return body
    if kind == "smash":
        t = _t(0.6)
        crunch = np.diff(_lowpass(_noise(len(t) + 1, rng), 3)) * np.exp(-t * 10) * 3.0
        thump = _kick(rng)
        out = crunch
        _add(out, thump, 0.0, 0.9)
        for k in range(5):
            _add(out, _hat(rng) * 2, 0.04 + 0.05 * k + rng.uniform(0, 0.03), 0.6)
        return out
    if kind == "door_open":
        t = _t(0.5)
        freq = 260 + 700 * (t / t[-1]) ** 1.5
        sweep = np.sign(np.sin(2 * np.pi * np.cumsum(freq) / SR)) * 0.25 * _env(len(t), 0.02, 0.35)
        rattle = _lowpass(_noise(len(t), rng), 6) * 0.3 * np.exp(-t * 6)
        return sweep + rattle
    if kind == "clone_pop":
        t = _t(0.3)
        freq = 520 * np.exp(-t * 3.5) * (1 + 0.08 * np.sin(2 * np.pi * 18 * t))
        return np.sin(2 * np.pi * np.cumsum(freq) / SR) * _env(len(t), 0.004, 0.16)
    if kind in {"race_start", "finish"}:
        notes = (84, 91) if kind == "race_start" else (72, 76, 79, 84)
        out = np.zeros(int((0.15 * len(notes) + 0.4) * SR))
        for k, midi in enumerate(notes):
            _add(out, _marimba(hz(midi), 0.4) + 0.4 * _pluck(hz(midi), 0.4), 0.13 * k)
        return out
    if kind == "whoosh":
        t = _t(0.45)
        noise = _noise(len(t), rng)
        shape = np.sin(np.pi * t / t[-1]) ** 2
        out = np.zeros_like(noise)
        for width, lo, hi in ((24, 0.0, 0.5), (8, 0.3, 0.8), (3, 0.6, 1.0)):
            band = (t / t[-1] >= lo) & (t / t[-1] <= hi)
            out += _lowpass(noise, width) * band
        return out * shape * 1.6
    raise ValueError(f"unknown cue {kind!r}")


def mix_episode(duration: float, cues: list[tuple[float, str]], seed: int) -> np.ndarray:
    """Music bed plus timed cues, ducked and limited, as float stereo in [-1, 1]."""
    music = synth_music(duration, seed)
    sfx = np.zeros(len(music), dtype=np.float32)
    for index, (time, kind) in enumerate(sorted(cues)):
        sound = synth_cue(kind, seed + index)
        # Every cue is levelled first so CUE_GAIN alone sets loudness (no clipping smash, no buried door).
        sound = sound * (CUE_PEAK / max(float(np.max(np.abs(sound))), 1e-9))
        _add(sfx, sound.astype(np.float32), time, CUE_GAIN.get(kind, 0.5))
    envelope = _lowpass(np.abs(sfx), int(0.08 * SR))
    duck = 1.0 - 0.35 * np.clip(envelope / max(np.max(envelope), 1e-9) * 2.0, 0.0, 1.0)
    mix = music * duck[:, None] + sfx[:, None] * 0.9
    limited = np.tanh(mix * 1.1)
    return limited * (0.95 / max(float(np.max(np.abs(limited))), 1e-9))


def write_wav(path: str | Path, stereo: np.ndarray) -> Path:
    path = Path(path)
    pcm = (np.clip(stereo, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes(pcm.tobytes())
    return path
