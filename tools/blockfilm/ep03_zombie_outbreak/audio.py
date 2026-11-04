"""ep03 sound: survival-thriller score + SFX, all synthesised here or by ../sfxkit.py (original, no samples), voices ducked over it, -14 LUFS.

    python audio.py        # -> out/mix.wav
Cue times are derived from web/timeline.json with the same formulas as SH() in web/ep3_story.js.
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sfxkit  # noqa: E402

SR = 48000
tl = json.load(open('web/timeline.json'))
TOTAL = tl['total']
N = int(TOTAL * SR) + 2 * SR
Bt = {b['id']: b for b in tl['beats']}
S = lambda i: Bt[i]['start']  # noqa: E731
E = lambda i: Bt[i]['start'] + Bt[i]['dur']  # noqa: E731
rng = np.random.default_rng(3)
tClose = E('door') + .5
X = dict(a1=3.0, b1=S('run') - .35, tClose=tClose, d1=tClose + .6, e1=S('hungry') - .3, g1=S('thirty') - .1, day2=E('thirty') + .6, h0=E('day2') + .7,
         crunch=S('shh') - 1.6, j0=S('shh') - .15, day3=E('sorry') + .5, k0=E('day3') + .7, knock=E('day3') + 1.25, k1=E('day3') + 2.1,
         o0=S('home') - .3, p0=S('end') - .4)

tt = lambda d: np.arange(int(d * SR)) / SR  # noqa: E731
noise = lambda d: rng.standard_normal(int(d * SR))  # noqa: E731
bp = lambda x, a, b: sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)  # noqa: E731
lp = lambda x, c, o=2: sosfilt(butter(o, c, 'low', fs=SR, output='sos'), x)  # noqa: E731
mid = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731
sfx, mus, amb = np.zeros(N), np.zeros(N), np.zeros(N)


def put(buf, x, t, g=1.0):
    i = int(max(0, t) * SR)
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += np.asarray(x[:j - i], dtype=float) * g


def fade(x, a=.01, r=.05):
    n = len(x); e = np.ones(n); na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr); return x * e


# ---------- SFX ----------
def siren(d):
    t = tt(d); f = 760 + 260 * np.sign(np.sin(2 * np.pi * 1.0 * t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + .4 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return fade(lp(x, 2500) * .35, .3, .5)


def groan(d=None, f0=None):
    d = d or rng.uniform(.8, 1.6); f0 = f0 or rng.uniform(70, 120); t = tt(d)
    f = f0 * (1 + .15 * np.sin(2 * np.pi * rng.uniform(2, 5) * t)) * (1 - .25 * t / d)
    src = 2 * ((np.cumsum(f) / SR) % 1) - 1
    x = bp(src, 300, 900) * .8 + bp(src, 900, 1800) * .35 + bp(noise(d), 400, 2000) * .25
    return fade(x * np.sin(np.linspace(0, np.pi, len(t))) ** .7, .05, .2)


def bang(heavy=1.0):
    t = tt(.5); body = np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 25)) * t) * np.exp(-t * 9)
    rattle = bp(noise(.5), 1500, 6000) * np.exp(-t * 14) * .5
    return (body + lp(noise(.5), 600) * np.exp(-t * 18) * .8 + rattle) * heavy


def rollup(d):
    t = tt(d); am = .6 + .4 * np.sign(np.sin(2 * np.pi * 28 * t))
    return fade(bp(noise(d), 1200, 7000) * am * .5 + bp(noise(d), 200, 800) * .3, .02, .03)


def slam():
    t = tt(1.4); low = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 4)
    clang = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in ((410, 6), (987, 9), (1630, 12))) * .25
    return np.tanh((low * 1.3 + clang + bp(noise(1.4), 800, 5000) * np.exp(-t * 10)) * 1.2)


def knock():
    t = tt(.25); return (np.sin(2 * np.pi * 180 * t) * np.exp(-t * 40) + bp(noise(.25), 900, 3500) * np.exp(-t * 60) * .6)


def impact():
    t = tt(2.5); sub = np.sin(2 * np.pi * np.cumsum(32 + 60 * np.exp(-t * 5)) / SR) * np.exp(-t * 1.6)
    return np.tanh((sub * 1.4 + lp(noise(2.5), 400) * np.exp(-t * 6) * .8) * 1.3)


def step():
    t = tt(.1); return lp(noise(.1), 1500) * np.exp(-t * 45) * .5


S_ = sfxkit.SOUNDS
# cold open: siren + street of groans
put(sfx, siren(X['d1'] + 4), 0, .55)
for _ in range(16):
    put(sfx, groan(), rng.uniform(.2, X['tClose']), .35)
put(sfx, impact(), 0, .6)
# running feet
t = X['b1']
while t < 9.5:
    put(sfx, step(), t, .5); put(sfx, step(), t + .08, .35); t += .17
put(sfx, rollup(.75), tClose - .75, .9)
put(sfx, slam(), tClose, 1.0)
# banging on the door and the glass all night (muffled once the door is shut)
for b in (X['d1'] + .25, X['d1'] + .95, X['d1'] + 1.9):
    put(sfx, bang(1.0), b, .9)
t = X['d1'] + 2.4
while t < X['day2'] - .3:
    put(sfx, lp(bang(.6), 900), t + rng.uniform(-.15, .15), .45); t += rng.uniform(.6, 1.2)
for _ in range(10):
    put(sfx, lp(groan(), 700), rng.uniform(tClose, X['day2'] - 1), .3)
# day cards
for d in (X['day2'], X['day3']):
    put(sfx, sfxkit.riser(1.0), d - 1.0, .25); put(sfx, impact(), d, .85)
# day 2: sneak, heartbeat, CRUNCH, the horde reacts
put(sfx, S_['heartbeat'](), X['h0'], .5)
put(sfx, S_['eat_crunch'](), X['crunch'], 1.3)
put(sfx, S_['eat_crunch'](), X['crunch'] + .35, .7)
for k in range(8):
    put(sfx, groan(f0=rng.uniform(80, 140)), X['crunch'] + .35 + k * .08, .32)
for b in (X['j0'] + .35, X['j0'] + .9, X['j0'] + 1.6, X['j0'] + 2.3, X['j0'] + 3.1):
    put(sfx, bang(.9), b, .75)
# day 3: rain, knock knock, heartbeat, the reveal
r = np.zeros(int((TOTAL - X['day3'] + 1) * SR))
r += bp(rng.standard_normal(len(r)), 1500, 9000) * .18 + lp(rng.standard_normal(len(r)), 500) * .25
put(amb, fade(r, 1.0, .8), X['day3'], .55)
for k in (X['knock'], X['knock'] + .22, X['knock'] + .55, X['knock'] + .77):
    put(sfx, knock(), k, .9)
put(sfx, S_['heartbeat'](4), X['k1'], .45)
put(sfx, groan(1.8, 75), X['p0'] + .9, .5)
for k in range(6):
    put(sfx, groan(f0=rng.uniform(65, 110)), X['p0'] + 1.3 + k * .3, .3)
put(sfx, impact(), S('end') - .1, .8)

# ---------- MUSIC: A minor survival pulse, a quiet beat for the reveal ----------
def saw(f, d):
    t = tt(d); return 2 * ((f * t) % 1) - 1


def pad(notes, d, g=.06):
    x = sum(lp(saw(mid(n) * (1 + .003 * k), d), 1200) for k, n in enumerate(notes)) / len(notes)
    return fade(x, .4, .6) * g


def bassn(m, d, g=.3):
    t = tt(d); x = lp(saw(mid(m), d) + np.sin(2 * np.pi * mid(m) * t), 500) * np.exp(-t * 3)
    return fade(x, .005, .03) * g


def kick():
    t = tt(.3); return np.sin(2 * np.pi * np.cumsum(48 + 100 * np.exp(-t * 30)) / SR) * np.exp(-t * 11)


def tick():
    n = int(.04 * SR); return bp(rng.standard_normal(n), 5000, 11000) * np.exp(-np.arange(n) / SR * 90)


def pulse(t0, t1, bpm=96, drums=True, prog=((45, [57, 60, 64]), (41, [53, 57, 60]), (38, [50, 53, 57]), (40, [52, 56, 59]))):
    b = 60 / bpm; t = t0; bar = 0
    while t < t1 - .2:
        root, ch = prog[bar % 4]; d = min(4 * b, t1 - t)
        put(mus, pad(ch, d + .4), t)
        for q in range(8):
            tq = t + q * b / 2
            if tq >= t1: break
            put(mus, bassn(root, b * .45), tq, .9 if q % 2 == 0 else .55)
            if drums and q % 4 == 0: put(mus, kick(), tq, .5)
            if drums: put(mus, tick(), tq + b / 4, .12)
        t += 4 * b; bar += 1


def tension(t0, t1):  # drone + slow heartbeat-like low pulse
    d = t1 - t0; t = tt(d)
    x = lp(saw(mid(33), d) + saw(mid(33) * 1.005, d), 220) * .25 + np.sin(2 * np.pi * mid(69 + 7) * t) * .015 * (1 + np.sin(2 * np.pi * .3 * t))
    put(mus, fade(x, .5, .6), t0)


pulse(.3, X['d1'] - .1, 112)
tension(X['d1'], X['g1'])
pulse(X['g1'], X['day2'] - .2, 96, drums=False)
tension(X['h0'] - .6, X['crunch'])
pulse(X['crunch'] + .2, X['day3'] - .2, 120)
tension(X['k0'] - .6, X['o0'])
pulse(X['o0'], TOTAL, 72, drums=False, prog=((45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (48, [55, 60, 64, 67]), (43, [55, 59, 62, 67])))

# ---------- VOICES + ducking ----------
voice = np.zeros(N)
for bb in tl['beats']:
    raw = subprocess.check_output(['ffmpeg', '-loglevel', 'error', '-i', bb['file'], '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'])
    a = np.frombuffer(raw, dtype=np.float32); put(voice, a, bb['start'])
act = np.convolve((np.abs(voice) > .02).astype(float), np.ones(int(.15 * SR)) / int(.15 * SR), 'same') > .05
gain = np.convolve(np.where(act, .38, 1.0), np.ones(int(.08 * SR)) / int(.08 * SR), 'same')
mix = voice * 1.05 + mus * gain * .6 + (sfx * .7 + amb) * np.where(act, .7, 1.0)
mix = np.tanh(mix * 1.1) / 1.1
mix = mix[:int(TOTAL * SR)]
os.makedirs('out', exist_ok=True)
open('out/mix.f32', 'wb').write(np.stack([mix, mix], 1).astype(np.float32).tobytes())
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'out/mix.f32',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', 'out/mix.wav'], check=True)
print('MIX_OK', round(TOTAL, 2))
