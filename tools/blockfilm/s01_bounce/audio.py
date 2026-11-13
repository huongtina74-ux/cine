"""MC-S1 Short #01 sound: original 120-bpm pluck groove + cartoon SFX, all synthesised (numpy + ../sfxkit.py, no samples).

    python audio.py        # -> out/mix.wav (48 kHz stereo, -14 LUFS, true peak -1 dB)
18 s = 9 bars at 120 bpm, so the music loops seamlessly with the picture.
Cue times match web/s01_story.js (JUMPS, ZL=12.4, ZOFF=15.0, ZBACK=17.0, ZLAND=17.45).
"""
import os
import subprocess
import sys

import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sfxkit as fx  # noqa: E402

SR = 48000
TOTAL = 18.0
N = int(TOTAL * SR)
rng = np.random.default_rng(5)
tt = lambda d: np.arange(int(d * SR)) / SR  # noqa: E731
lp = lambda x, c: sosfilt(butter(2, c, 'low', fs=SR, output='sos'), x)  # noqa: E731
hp = lambda x, c: sosfilt(butter(2, c, 'high', fs=SR, output='sos'), x)  # noqa: E731
mid = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
mus, sfx = np.zeros(N), np.zeros(N)


def put(buf, x, t, g=1.0):
    i = int(max(0, t) * SR); j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += np.asarray(x[:j - i], dtype=float) * g


def pitch(x, k):
    """Resample by factor k (k > 1 = higher and shorter)."""
    n = int(len(x) / k); return np.interp(np.arange(n) * k, np.arange(len(x)), x)


# ---------- music: 120 bpm, C major pentatonic pluck + bass + light drums ----------
BEAT = .5
def pluck(f, d=.35):
    t = tt(d); x = np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) + .12 * np.sin(6 * np.pi * f * t)
    return x * np.exp(-t * 9) * np.minimum(1, t / .003)
def bass(f, d=.45):
    t = tt(d); return lp(np.sign(np.sin(2 * np.pi * f * t)) * .6 + np.sin(2 * np.pi * f * t), 700) * np.exp(-t * 4) * np.minimum(1, t / .005)
def kick():
    t = tt(.25); return np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t * 30)) / SR) * np.exp(-t * 14)
def clap():
    t = tt(.18); return hp(rng.standard_normal(len(t)), 1200) * np.exp(-t * 28) * .5
def hat():
    t = tt(.05); return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * 90) * .25

MEL = [72, 76, 79, 76, 81, 79, 76, 74, 72, 74, 76, 79, 76, 74, 72, 67]  # 8th-note riff over two bars
CHORDS = [48, 45, 41, 43]  # C  Am  F  G (bass roots), one per bar


def music_on(t):
    """Arrangement mask: full groove, cut for Zu's charge, suspense drop while waiting, back for the landing."""
    if 11.0 <= t < 12.4 or 15.0 <= t < 17.45:
        return 0.0
    return 1.0


for bar in range(9):
    t0 = bar * 4 * BEAT
    for b in range(4):
        tb = t0 + b * BEAT
        g = music_on(tb)
        if g:
            put(mus, kick(), tb, .9 if b % 2 == 0 else .6)
            if b % 2 == 1:
                put(mus, clap(), tb, .8)
            put(mus, bass(mid(CHORDS[bar % 4])), tb, .55)
        for h in range(2):
            th = tb + h * BEAT / 2
            if music_on(th) or 15.0 <= th < 17.0:  # the hats keep ticking through the wait
                put(mus, hat(), th, 1.0 if h else .6)
    for k in range(8):
        tk = t0 + k * BEAT / 2
        if music_on(tk):
            put(mus, pluck(mid(MEL[(bar % 2) * 8 + k])), tk, .32)
# after the launch the riff jumps an octave for extra energy
for k in range(int((15.0 - 12.4) / (BEAT / 2))):
    tk = 12.5 + k * BEAT / 2
    put(mus, pluck(mid(MEL[k % 16] + 12)), tk, .18)

# ---------- SFX (times match the picture) ----------
put(sfx, fx.boing(), .30, .8); put(sfx, fx.whoosh(.6), .35, .45)
put(sfx, fx.block_place('dirt'), 2.50, .9); put(sfx, pitch(fx.boing(), 1.6)[:int(.3 * SR)], 2.50, .35)
put(sfx, fx.pop(), 3.85, .6); put(sfx, fx.pop(), 4.05, .6)
put(sfx, pitch(fx.boing(), 1.15), 4.40, .7); put(sfx, pitch(fx.boing(), 1.35), 5.20, .9); put(sfx, fx.whoosh(.8), 5.25, .5)
put(sfx, fx.block_place('dirt'), 7.40, .9)
put(sfx, fx.slide_whistle(up=False, d=.6), 7.85, .55)
put(sfx, pitch(fx.boing(), 2.2), 9.00, .6); put(sfx, fx.block_place('wood'), 9.50, .35); put(sfx, fx.pop(), 9.60, .5)
for i in range(6):
    put(sfx, pitch(fx.pop(), 1.6 + .2 * (i % 3)), 10.05 + i * .15, .35)
put(sfx, fx.record_scratch(), 11.00, .8)
put(sfx, fx.heartbeat(1), 11.15, .7)
put(sfx, fx.riser(.85), 11.55, .7)
put(sfx, pitch(fx.boing(), .7), 12.40, 1.0); put(sfx, fx.explosion()[:int(.9 * SR)] * np.linspace(1, 0, int(.9 * SR)), 12.40, .45)
put(sfx, fx.whoosh(1.4), 12.50, .6); put(sfx, fx.sparkle(), 13.6, .35)
for i in range(4):
    put(sfx, fx.blink(), 15.1 + i * .5, .4)
put(sfx, fx.slide_whistle(up=False, d=.45), 17.00, .6)
put(sfx, fx.bonk(), 17.45, .7); put(sfx, fx.boing(), 17.45, .6); put(sfx, fx.sparkle(), 17.52, .5)

# ---------- mix: stereo, music under SFX, -14 LUFS ----------
mix = mus * .55 + sfx * .9
mix = np.tanh(mix * 1.1) / 1.1
st = np.stack([mix, mix], 1)
os.makedirs('out', exist_ok=True)
raw = 'out/mix_raw.wav'
import wave  # noqa: E402
with wave.open(raw, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st / (np.max(np.abs(st)) or 1) * .9, -1, 1) * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1:LRA=11', '-ar', '48000', 'out/mix.wav'], check=True)
print('out/mix.wav', TOTAL, 's')
