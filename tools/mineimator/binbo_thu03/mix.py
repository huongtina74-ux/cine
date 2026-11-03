"""Sound for scene 03 (no dialogue): cartoon SFX on every acting beat + a light bouncy loop, mastered to -14 LUFS.
Usage (in WORKDIR): python mix.py   -> mix.wav
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'blockfilm'))
import sfxkit  # noqa: E402

SR = 48000
T = json.load(open('proj/timing.json'))
FPS = T['fps']
TOTAL = T['end'] / FPS
N = int(TOTAL * SR) + SR
sfx = np.zeros(N)
mus = np.zeros(N)


def put(buf, x, t, g=1.0):
    i = int(t * SR)
    j = min(N, i + len(x))
    buf[i:j] += x[:j - i] * g


S = lambda n: sfxkit.SOUNDS[n]()  # noqa: E731
f = lambda fr: fr / FPS            # noqa: E731
for fr in (6, 16, 26):
    put(sfx, S('blink'), f(fr), .45)                         # sniff sniff
put(sfx, S('sparkle'), f(40), .6); put(sfx, S('pop'), f(44), .45)   # heart eyes, blush
for fr in (52, 70, 88):
    put(sfx, S('item_pop'), f(fr), .25)                      # floating hearts
put(sfx, S('whoosh'), f(72), .6); put(sfx, S('sparkle'), f(78), .5)   # crash zoom on the pizza
put(sfx, S('record_scratch'), f(118), .45); put(sfx, S('boing'), f(119), .55)   # Bin's double take
put(sfx, S('slide_down'), f(172), .35)                       # crouch
put(sfx, S('retro_jump'), f(184), .5); put(sfx, S('whoosh'), f(186), .4)
put(sfx, S('bonk'), f(206), .6)                              # landing
for fr in range(250, 312, 8):
    put(sfx, S('eat_crunch'), f(fr), .45)
put(sfx, S('slide_down'), f(322), .3)                        # sweat drop
put(sfx, S('xp_ding'), f(350), .45)                          # laugh beat

mid = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731


def note(fr_, d, amp, dec=7):
    tt = np.arange(int(SR * d)) / SR
    return (np.sin(2 * np.pi * fr_ * tt) + .3 * np.sin(4 * np.pi * fr_ * tt)) * np.exp(-tt * dec) * amp


b = 60 / 120
t0, k = 0.0, 0
prog = [0, 5, 7, 5]
while t0 < TOTAL:
    r = 60 + prog[k % 4]
    for q in range(4):
        tq = t0 + q * b
        if tq >= TOTAL:
            break
        put(mus, note(mid(r - 12), .3, .2), tq)
        put(mus, note(mid([72, 76, 79, 76][q] + prog[k % 4]), .25, .05, 9), tq + b / 2)
    t0 += 4 * b
    k += 1
mix = np.tanh((mus * .55 + sfx * .8) * 1.1) / 1.1
mix = mix[:int(TOTAL * SR)]
sf.write('mix_raw.wav', np.stack([mix, mix], 1).astype(np.float32), SR)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', 'mix.wav'], check=True)
print('MIX_OK', round(TOTAL, 2))
