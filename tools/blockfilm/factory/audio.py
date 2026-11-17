"""Cue-driven sound for a factory Short: original 120-bpm groove + cartoon SFX, all synthesised (numpy + ../sfxkit.py).

    python audio.py OUT/cues.json OUT/mix.wav      # cues.json comes from `node render.js WEB cues ...`

The picture engine (web/contest.js) writes every sound moment as a cue {t, type, g}; this file only maps cue types
to sounds, so a new SPEC needs no audio editing. 'music_off' / 'music_on' cues mute and restore the groove (the
hi-hats keep ticking through a mute so the suspense still has a pulse); 'octave' adds a high riff layer from then on.
Output: 48 kHz stereo WAV, loudness-normalised to -14 LUFS, true peak -1 dB.
"""
import json
import os
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import sfxkit as fx  # noqa: E402

SR = 48000
BEAT = .5
rng = np.random.default_rng(5)
tt = lambda d: np.arange(int(d * SR)) / SR  # noqa: E731
lp = lambda x, c: sosfilt(butter(2, c, 'low', fs=SR, output='sos'), x)  # noqa: E731
hp = lambda x, c: sosfilt(butter(2, c, 'high', fs=SR, output='sos'), x)  # noqa: E731
mid = lambda m: 440 * 2 ** ((m - 69) / 12)  # noqa: E731


def put(buf, x, t, g=1.0):
    i = int(max(0, t) * SR); j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += np.asarray(x[:j - i], dtype=float) * g


def pitch(x, k):
    n = int(len(x) / k); return np.interp(np.arange(n) * k, np.arange(len(x)), x)


def fade(x, d):
    n = min(len(x), int(d * SR)); return x[:n] * np.linspace(1, 0, n)


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


# cue type -> sound (each returns a mono array); the picture engine never needs to know about samples
_rand = np.random.default_rng(11)
SFX = {
    'place': lambda: pitch(fx.block_place('wood'), .9 + .25 * _rand.random()),
    'top': lambda: pitch(fx.boing(), 1.6)[:int(.3 * SR)],
    'thud': lambda: fx.block_place('dirt'),
    'ding': fx.idea_ding,
    'boing': fx.boing,
    'boing_big': lambda: pitch(fx.boing(), .7),
    'blast': lambda: fade(fx.explosion(), .9),
    'whoosh': lambda: fx.whoosh(.6),
    'whoosh_long': lambda: fx.whoosh(1.2),
    'slide_down': lambda: fx.slide_whistle(up=False, d=.55),
    'pop': lambda: pitch(fx.pop(), 1.5 + .4 * _rand.random()),
    'scratch': fx.record_scratch,
    'heartbeat': lambda: fx.heartbeat(1),
    'riser': lambda: fx.riser(.85),
    'sparkle': fx.sparkle,
    'blink': fx.blink,
    'bonk': fx.bonk,
    'chaching': fx.cha_ching,
    'creak': lambda: fx.door_creak(.7),
    'crumble': lambda: _crumble(),
}


def _crumble():
    """Five stone breaks tumbling over ~0.9 s."""
    a = fx.block_break('stone'); b = pitch(fx.block_break('stone'), .8)
    out = np.zeros(int(.9 * SR))
    for i, t in enumerate((0, .07, .16, .28, .41)):
        put(out, a if i % 2 == 0 else b, t, 1 - .12 * i)
    return out


MEL = [72, 76, 79, 76, 81, 79, 76, 74, 72, 74, 76, 79, 76, 74, 72, 67]
CHORDS = [48, 45, 41, 43]  # C Am F G


def mix(cues_path, out_wav):
    c = json.loads(open(cues_path, encoding='utf-8').read())
    total = float(c['total']); n = int(total * SR)
    cues = sorted(c['cues'], key=lambda q: q['t'])
    unknown = sorted({q['type'] for q in cues} - set(SFX) - {'music_off', 'music_on', 'octave', 'slow'})
    assert not unknown, f'no sound for cue types {unknown}'
    sw = [(q['t'], q['type']) for q in cues if q['type'] in ('music_off', 'music_on')]
    octave = min([q['t'] for q in cues if q['type'] == 'octave'] or [1e9])

    def on(t):
        state = 1
        for ts, k in sw:
            if ts <= t + 1e-6:
                state = 1 if k == 'music_on' else 0
        return state

    mus, sfx = np.zeros(n), np.zeros(n)
    for bar in range(int(np.ceil(total / (4 * BEAT)))):
        t0 = bar * 4 * BEAT
        for b in range(4):
            tb = t0 + b * BEAT
            if on(tb):
                put(mus, kick(), tb, .9 if b % 2 == 0 else .6)
                if b % 2:
                    put(mus, clap(), tb, .8)
                put(mus, bass(mid(CHORDS[bar % 4])), tb, .55)
            for h in range(2):
                put(mus, hat(), tb + h * BEAT / 2, (1.0 if h else .6) * (1 if on(tb) else .7))
        for k in range(8):
            tk = t0 + k * BEAT / 2
            if on(tk):
                put(mus, pluck(mid(MEL[(bar % 2) * 8 + k])), tk, .32)
                if tk >= octave:
                    put(mus, pluck(mid(MEL[(bar % 2) * 8 + k] + 12)), tk, .16)
    for q in cues:
        if q['type'] in SFX:
            put(sfx, SFX[q['type']](), q['t'], q['g'])
    m = np.tanh((mus * .55 + sfx * .9) * 1.1) / 1.1
    # 15 ms fade at both ends so the loop point never clicks
    k = int(.015 * SR); m[:k] *= np.linspace(0, 1, k); m[-k:] *= np.linspace(1, 0, k)
    st = np.stack([m, m], 1)
    raw = out_wav.replace('.wav', '_raw.wav')
    with wave.open(raw, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(st / (np.max(np.abs(st)) or 1) * .9, -1, 1) * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1:LRA=11', '-ar', '48000', '-t', str(total), out_wav], check=True)
    os.remove(raw)
    return {'total': total, 'cues': len(cues), 'music_mutes': sum(1 for _, k in sw if k == 'music_off')}


if __name__ == '__main__':
    print('AUDIO_OK', sys.argv[2], mix(sys.argv[1], sys.argv[2]))
