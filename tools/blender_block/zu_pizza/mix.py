"""Sound for test 01 (no dialogue): continuous music bed WITH bass + cartoon/food SFX on every beat, -14 LUFS.

    python tools/blender_block/zu_pizza/mix.py OUT.wav
Everything is synthesised here or by tools/blockfilm/sfxkit.py (original, no samples, nothing to license).
Fixes the scorecard gaps: bass share was 0.07-0.11 (MSToons 0.57) and the floor dropped to -39.7 dBFS.
"""
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'blockfilm'))
import sfxkit  # noqa: E402

SR, FPS, FRAMES = 48000, 24, 240
TOTAL = FRAMES / FPS
N = int(TOTAL * SR)
rng = np.random.default_rng(4)
sfx, mus = np.zeros(N + SR), np.zeros(N + SR)
f = lambda fr: (fr - 1) / FPS  # noqa: E731
lp = lambda x, c: sosfilt(butter(2, c, 'low', fs=SR, output='sos'), x)  # noqa: E731
bp = lambda x, a, b: sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)  # noqa: E731


def put(buf, x, t, g=1.0):
    i = int(t * SR)
    j = min(len(buf), i + len(x))
    buf[i:j] += np.asarray(x[:j - i], dtype=float) * g


def sniff(d=.2):
    n = int(d * SR)
    env = np.linspace(0, 1, n) ** 2 * np.hanning(n * 2)[n:] ** .3
    return bp(rng.standard_normal(n), 1800, 6000) * env


def sizzle(d):
    n = int(d * SR)
    x = bp(rng.standard_normal(n), 3000, 9000) * .25
    crack = (rng.random(n) > .9993) * rng.uniform(.5, 1, n)
    x += bp(crack, 1500, 8000) * 3
    return x * np.minimum(1, np.linspace(0, 6, n)) * np.minimum(1, np.linspace(6, 0, n))


def stretch(d=1.2):
    t = np.arange(int(d * SR)) / SR
    fr = 260 + 380 * t / d
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 1.5) * .5 * (1 + .3 * np.sin(2 * np.pi * 9 * t))


S = lambda n, *a: sfxkit.SOUNDS[n](*a) if a else sfxkit.SOUNDS[n]()  # noqa: E731
for fr in (14, 18, 22, 26):
    put(sfx, sniff(), f(fr), .55)
put(sfx, S('pop'), f(30), .5)
put(sfx, S('whoosh'), f(54), .6)
put(sfx, S('sparkle'), f(56), .6)
for fr in range(60, 77, 4):
    put(sfx, S('blink'), f(fr), .25)
put(sfx, sizzle(1.4), f(85), .9)
put(sfx, S('item_pop'), f(126), .4)
put(sfx, stretch(), f(130), .35)
put(sfx, S('pop'), f(156), .35)
put(sfx, S('whoosh'), f(170), .45)
put(sfx, S('eat_crunch'), f(178), .9)
for fr in range(184, 205, 6):
    put(sfx, S('eat_crunch'), f(fr), .45)
put(sfx, S('xp_ding'), f(205), .55)
put(sfx, S('sparkle'), f(207), .5)
for fr in (210, 222):
    put(sfx, S('boing'), f(fr), .4)

# ---- music: 120 bpm, I-vi-IV-V in F, bass + pad + pluck + light drums (continuous, no holes)
mid = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
beat = .5
prog = [(53, [65, 69, 72]), (50, [62, 65, 69]), (46, [58, 62, 65]), (48, [60, 64, 67])]


def tone(freq, d, kind='sin', dec=0.0):
    t = np.arange(int(d * SR)) / SR
    ph = 2 * np.pi * freq * t
    x = np.sin(ph) if kind == 'sin' else 2 * ((freq * t) % 1) - 1
    return x * (np.exp(-t * dec) if dec else 1) * np.minimum(1, t * 200) * np.minimum(1, (d - t) * 60)


def kick():
    t = np.arange(int(.25 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t * 14)


def hat():
    n = int(.05 * SR)
    return bp(rng.standard_normal(n), 6000, 12000) * np.exp(-np.arange(n) / SR * 80)


bar = 0
t0 = 0.0
while t0 < TOTAL:
    root, chord = prog[bar % 4]
    pad = sum(lp(tone(mid(m), 4 * beat, 'saw'), 1400) for m in chord) / 3
    put(mus, pad, t0, .07)
    for q in range(8):
        tq = t0 + q * beat / 2
        put(mus, lp(tone(mid(root - 12), beat * .45, 'saw') + tone(mid(root - 12), beat * .45), 600), tq, .32 if q % 2 == 0 else .2)
        if q % 2 == 0:
            put(mus, kick(), tq, .45)
        else:
            put(mus, hat(), tq, .12)
        if q in (1, 3, 6):
            put(mus, tone(mid(chord[(q + bar) % 3] + 12), .22, 'sin', 9), tq, .1)
    t0 += 4 * beat
    bar += 1
# the bed dips a little under the bite so the crunch reads
duck = np.ones(len(mus))
a, b = int(f(176) * SR), int(f(190) * SR)
duck[a:b] = .6
mus *= duck
mix = np.tanh((mus * .8 + sfx * .9) * 1.2) / 1.2
mix = mix[:N]
out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else 'mix.wav')
raw = out.replace('.wav', '_raw.wav')
sf.write(raw, np.stack([mix, mix], 1).astype(np.float32), SR)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-15.5:TP=-2:LRA=11,alimiter=limit=0.84',
                '-ar', '48000', out], check=True)
print('MIX_OK', out, round(TOTAL, 2))
