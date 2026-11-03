"""Bin & Bo sound kit: original, code-generated cartoon / block-world sound effects (no samples, no licences to track).

    python tools/blockfilm/sfxkit.py --reel out/sfxkit_reel.wav   # every sound once, with a ding between, + cue list

Every function returns a mono float32 numpy array at SR=48000, peak <= 1.
The retro "game" sounds use pyfxr (sfxr port) when it is installed; everything else is numpy/scipy only.
Sounds are original synthesis - no Mojang/Minecraft audio, no meme sounds (vine boom, bruh, Roblox oof...).
"""
from __future__ import annotations

import argparse
import json

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
_rng = np.random.default_rng(11)


def _t(d): return np.arange(int(d * SR)) / SR
def _noise(d): return _rng.standard_normal(int(d * SR))
def _bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def _lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def _hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def _env(n, a=.003, d=None, r=.01):
    x = np.ones(n); na = max(1, min(n, int(a * SR))); x[:na] = np.linspace(0, 1, na)
    if d: x *= np.exp(-np.arange(n) / SR / d)
    nr = max(1, min(n, int(r * SR))); x[-nr:] *= np.linspace(1, 0, nr)
    return x
def _osc(freq, d, kind='sin'):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (int(d * SR),)) if np.ndim(freq) == 0 else np.asarray(freq, dtype=float)
    ph = 2 * np.pi * np.cumsum(f) / SR
    if kind == 'saw': return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if kind == 'square': return np.sign(np.sin(ph))
    if kind == 'tri': return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1
    return np.sin(ph)
def _norm(x, peak=.9):
    x = np.nan_to_num(np.asarray(x, dtype=np.float64)); m = np.max(np.abs(x)) or 1.0
    return (x / m * peak).astype(np.float32)
def _mix(*parts):
    n = max(len(p) for p in parts); y = np.zeros(n)
    for p in parts: y[:len(p)] += p
    return y
def _at(x, t, n):
    y = np.zeros(n); i = int(t * SR); y[i:i + len(x)] += x[:max(0, n - i)]; return y


# ---------- block world ----------
def block_place(material='wood'):
    """Short knock: a filtered noise transient + a body resonance tuned per material."""
    body = {'wood': (310, 620, .05), 'stone': (820, 1900, .03), 'dirt': (140, 380, .03), 'glass': (2200, 5200, .05)}[material]
    d = .22; t = _t(d)
    click = _bp(_noise(d), body[1] * .6, min(body[1] * 2.2, 20000)) * np.exp(-t * 90)
    res = (np.sin(2 * np.pi * body[0] * t) + .4 * np.sin(2 * np.pi * body[0] * 2.7 * t)) * np.exp(-t / body[2])
    return _norm(click * .8 + res * .6)
def block_break(material='stone'):
    d = .45; n = int(d * SR); y = np.zeros(n)
    for k in range(9):
        y += _at(block_place(material) * _rng.uniform(.3, .8), _rng.uniform(0, .18), n)
    y += _lp(_noise(d), 1800) * np.exp(-_t(d) * 9) * .5
    return _norm(y)
def footstep(surface='grass'):
    d = .14; t = _t(d)
    if surface == 'grass': x = _bp(_noise(d), 900, 5000) * np.exp(-t * 32) * (1 + .6 * (_rng.random(len(t)) > .9))
    elif surface == 'wood': x = block_place('wood')[:len(t)] * .7
    else: x = _bp(_noise(d), 300, 2500) * np.exp(-t * 45)
    return _norm(x, .7)
def item_pop():
    d = .1; f = np.linspace(600, 1500, int(d * SR)); return _norm(_osc(f, d) * _env(len(f), .001, .03))
def xp_ding():
    d = .7; t = _t(d); f = 1975.5
    return _norm(sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * k) for m, a, k in [(1, 1, 5), (2.01, .35, 9), (3.0, .15, 14)]))
def door_creak(d=.9):
    t = _t(d); f = 140 + 70 * np.sin(2 * np.pi * 1.3 * t) + 25 * np.sin(2 * np.pi * 7 * t)
    return _norm(_bp(_osc(f, d, 'saw') * (1 + .5 * (_rng.random(len(t)) > .97)), 300, 2400) * _env(len(t), .05, r=.15))
def chest_open():
    n = int(.6 * SR); return _norm(_mix(_at(door_creak(.35), 0, n), _at(block_place('wood'), .3, n)))
def eat_crunch(bites=3):
    n = int((.32 * bites + .2) * SR); y = np.zeros(n)
    for i in range(bites):
        b = _lp(_noise(.11), 2600) * _env(int(.11 * SR), .002, .03); y += _at(b, i * .32, n)
    return _norm(y)
def tnt_fuse(d=1.5):
    t = _t(d); return _norm(_hp(_noise(d), 3500) * (.6 + .4 * np.sin(2 * np.pi * 23 * t)) * _env(len(t), .02, r=.05), .6)
def explosion():
    d = 2.4; t = _t(d)
    low = _osc(40 + 90 * np.exp(-t * 6), d) * np.exp(-t * 2.2)
    body = _lp(_noise(d), 900, 4) * np.exp(-t * 2.6) * 2
    crack = _hp(_noise(d), 2500) * np.exp(-t * 10) * .6
    return _norm(np.tanh((low + body + crack) * 1.5))


# ---------- cartoon accents ----------
def boing():
    d = .7; t = _t(d); f = 180 + 220 * np.exp(-t * 3) * (1 + .5 * np.sin(2 * np.pi * 13 * t))
    return _norm(_osc(f, d) * np.exp(-t * 4) * _env(len(t), .002))
def bonk():
    d = .35; t = _t(d)
    return _norm(_osc(900 * np.exp(-t * 8) + 250, d, 'tri') * np.exp(-t * 14) + _bp(_noise(d), 800, 3000) * np.exp(-t * 60) * .5)
def pop():
    d = .08; f = np.linspace(400, 1800, int(d * SR)); return _norm(_osc(f, d) * _env(len(f), .001, .02))
def whoosh(d=.45):
    x = _bp(_noise(d), 300, 3500); e = np.sin(np.linspace(0, np.pi, len(x))) ** 2; return _norm(x * e, .7)
def zip_run(d=.35):
    t = _t(d); f = 300 * (12 ** (t / d)); return _norm((_osc(f, d, 'square') * .3 + _bp(_noise(d), 2000, 8000) * .4) * _env(len(t), .005, r=.05), .6)
def slide_whistle(up=True, d=.7):
    t = _t(d); f0, f1 = (500, 1800) if up else (1800, 450); f = np.geomspace(f0, f1, len(t)) * (1 + .02 * np.sin(2 * np.pi * 6 * t))
    return _norm((_osc(f, d) + .2 * _osc(f * 2, d)) * _env(len(t), .03, r=.08), .7)
def blink():
    d = .06; t = _t(d); return _norm(np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 80), .5)
def idea_ding():
    n = int(1.2 * SR); return _norm(_mix(_at(xp_ding(), 0, n), _at(xp_ding() * .7, .09, n)))
def sparkle():
    n = int(1.6 * SR); y = np.zeros(n)
    for i, f in enumerate([2093, 2637, 3136, 4186, 3520, 4699]):
        t = _t(.6); y += _at(np.sin(2 * np.pi * f * t) * np.exp(-t * 7) * .5, i * .08, n)
    return _norm(y)
def cha_ching():
    n = int(1.0 * SR); return _norm(_mix(_at(_hp(_noise(.15), 3000) * np.exp(-_t(.15) * 30), 0, n), _at(sparkle()[:int(.9 * SR)], .1, n)))
def sad_trombone():
    notes = [(311.1, .45), (293.7, .45), (277.2, .45), (261.6, 1.2)]; out = []
    for f, d in notes:
        t = _t(d); vib = 1 + (.015 * np.sin(2 * np.pi * 5.5 * t) if d > 1 else 0)
        s = _osc(f * vib, d, 'saw'); w = np.sin(np.pi * t / d)  # "wah": crossfade a dark and a bright filter
        x = (_lp(s, 700) * (1 - w) + _lp(s, 1700) * w) * _env(len(t), .03, r=.08); out.append(x)
    return _norm(np.concatenate(out))
def dun_dun_dun():
    out = []
    for f, d in [(146.8, .35), (146.8, .35), (130.8, 1.3)]:
        t = _t(d); x = sum(_osc(f * m, d, 'saw') * a for m, a in [(1, 1), (1.5, .6), (2, .4)])
        out.append(_lp(x, 1200) * _env(len(t), .01, r=.1)); out.append(np.zeros(int(.05 * SR)))
    return _norm(np.concatenate(out))
def record_scratch():
    d = .45; t = _t(d); m = np.sin(2 * np.pi * (3 + 9 * t) * t)
    return _norm(_bp(_noise(d), 600, 4000) * (.4 + .6 * (m > 0)) * _env(len(t), .005, r=.05), .8)
def heartbeat(beats=3):
    n = int((.8 * beats + .3) * SR); y = np.zeros(n)
    for i in range(beats):
        for off, g in ((0, 1), (.18, .7)):
            t = _t(.2); y += _at(np.sin(2 * np.pi * 55 * t) * np.exp(-t * 22) * g, i * .8 + off, n)
    return _norm(y)
def riser(d=2.0):
    t = _t(d); f = 200 * (8 ** (t / d)); return _norm((_bp(_noise(d), 500, 6000) * .5 + _osc(f, d) * .3) * (t / d) ** 2)
def sob():
    d = .24; t = _t(d); f = 520 + 140 * np.exp(-t * 12)
    return _norm((np.sin(2 * np.pi * np.cumsum(f) / SR) * .4 + _bp(_noise(d), 500, 1800) * .5) * np.exp(-t * 12) * _env(len(t), .01))


# ---------- retro game (pyfxr, optional) ----------
def _fx(name):
    import pyfxr
    b = getattr(pyfxr, name)(); a = np.frombuffer(memoryview(b), dtype=np.int16).astype(np.float64) / 32768
    idx = np.arange(0, len(a), 44100 / SR); return _norm(np.interp(idx, np.arange(len(a)), a))
def retro(name='pickup'):
    try: return _fx(name)
    except Exception: return item_pop()


SOUNDS = {
    'block_place_wood': lambda: block_place('wood'), 'block_place_stone': lambda: block_place('stone'),
    'block_place_dirt': lambda: block_place('dirt'), 'block_place_glass': lambda: block_place('glass'),
    'block_break_stone': lambda: block_break('stone'), 'block_break_wood': lambda: block_break('wood'),
    'step_grass': lambda: footstep('grass'), 'step_wood': lambda: footstep('wood'), 'step_stone': lambda: footstep('stone'),
    'item_pop': item_pop, 'xp_ding': xp_ding, 'door_creak': door_creak, 'chest_open': chest_open, 'eat_crunch': eat_crunch,
    'tnt_fuse': tnt_fuse, 'explosion': explosion,
    'boing': boing, 'bonk': bonk, 'pop': pop, 'whoosh': whoosh, 'zip_run': zip_run,
    'slide_up': lambda: slide_whistle(True), 'slide_down': lambda: slide_whistle(False), 'blink': blink,
    'idea_ding': idea_ding, 'sparkle': sparkle, 'cha_ching': cha_ching, 'sad_trombone': sad_trombone,
    'dun_dun_dun': dun_dun_dun, 'record_scratch': record_scratch, 'heartbeat': heartbeat, 'riser': riser, 'sob': sob,
    'retro_pickup': lambda: retro('pickup'), 'retro_jump': lambda: retro('jump'), 'retro_powerup': lambda: retro('powerup'),
    'retro_hurt': lambda: retro('hurt'), 'retro_laser': lambda: retro('laser'),
}


def reel(path: str) -> list[dict]:
    import soundfile as sf
    gap = np.zeros(int(.5 * SR), np.float32); t = 0.0; parts = []; cues = []
    for name, fn in SOUNDS.items():
        x = fn(); cues.append({'t': round(t, 2), 'name': name, 'dur': round(len(x) / SR, 2)})
        parts += [x, gap]; t += len(x) / SR + .5
    sf.write(path, np.concatenate(parts), SR)
    return cues


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--reel', required=True)
    cues = reel(ap.parse_args().reel)
    print(json.dumps(cues, ensure_ascii=False))
    print(f"SFXKIT_OK::sounds={len(cues)}::seconds={cues[-1]['t'] + cues[-1]['dur']:.1f}")
