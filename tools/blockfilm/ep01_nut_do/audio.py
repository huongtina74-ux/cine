import json, subprocess, numpy as np
from scipy.signal import butter, sosfilt
SR = 48000
tl = json.load(open('web/timeline.json'))
TOTAL = tl['total']
N = int(TOTAL * SR) + SR
Bt = {b['id']: b for b in tl['beats']}
S = lambda i: Bt[i]['start']
E = lambda i: Bt[i]['start'] + Bt[i]['dur']
rng = np.random.default_rng(7)

def tt(d): return np.arange(int(d * SR)) / SR
def env(n, a=0.005, r=None, d=None):
    x = np.ones(n); na = max(1, int(a * SR)); x[:na] = np.linspace(0, 1, na)
    if d: x *= np.exp(-np.arange(n) / SR / d)
    if r: nr = min(n, int(r * SR)); x[-nr:] *= np.linspace(1, 0, nr)
    return x
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def noise(d): return rng.standard_normal(int(d * SR))
def sweep(f0, f1, d, kind='exp'):
    t = tt(d); f = f0 * (f1 / f0) ** (t / d) if kind == 'exp' else np.linspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)

# ---------- SFX ----------
def click(): x = noise(.02) * env(int(.02 * SR), .001, d=.004) * .6; return x + np.sin(2*np.pi*2200*tt(.02)) * env(int(.02*SR), .001, d=.005) * .5
def thud(): t = tt(.35); return (np.sin(2*np.pi*(70+60*np.exp(-t*20))*t) * np.exp(-t*12) + lp(noise(.35), 300) * np.exp(-t*25) * .6) * .9
def step(): t = tt(.12); return lp(noise(.12), 900) * np.exp(-t*40) * .35
def tock(): t = tt(.12); return (np.sin(2*np.pi*820*t) + .5*np.sin(2*np.pi*1650*t)) * np.exp(-t*45) * .5 + lp(noise(.12), 2000)*np.exp(-t*60)*.2
def pop(): t = tt(.12); return sweep(500, 1400, .12) * np.exp(-t*25) * .5
def whoosh(d=.5, lo=300, hi=3000): x = bp(noise(d), lo, hi); e = np.sin(np.linspace(0, np.pi, len(x))) ** 2; return x * e * .45
def slide(f0, f1, d):
    t = tt(d); f = np.linspace(f0, f1, len(t)) * (1 + .03*np.sin(2*np.pi*7*t))
    return np.sin(2*np.pi*np.cumsum(f)/SR) * env(len(t), .02, r=.08) * .35
def bell(f, d=1.2, amp=.3):
    t = tt(d); x = sum(a*np.sin(2*np.pi*f*m*t)*np.exp(-t*k) for m, a, k in [(1,1,3),(2.76,.5,5),(5.4,.25,8),(8.9,.12,12)])
    return x * env(len(t), .002) * amp
def chaching(): x = np.zeros(int(1.0*SR)); x[:int(.15*SR)] += hp(noise(.15), 3000)*np.exp(-tt(.15)*30)*.5; b = bell(2093, .9, .25)+bell(2637, .9, .2); x[int(.12*SR):int(.12*SR)+len(b)] += b[:len(x)-int(.12*SR)]; return x
def rumble(d): t = tt(d); return lp(noise(d), 110, 4) * (1 + .5*np.sin(2*np.pi*3*t)) * env(len(t), .3, r=.5) * 3.0
def bubbles(d):
    x = np.zeros(int(d*SR))
    for _ in range(int(d*14)):
        s = rng.uniform(0, d-.1); f = rng.uniform(150, 420); b = sweep(f, f*2.2, .07) * np.exp(-tt(.07)*30) * .25
        i = int(s*SR); x[i:i+len(b)] += b
    return x + lp(noise(d), 250) * .25
def boom():
    d = 2.6; t = tt(d)
    low = np.sin(2*np.pi*np.cumsum(40 + 90*np.exp(-t*6))/SR) * np.exp(-t*2.2) * 1.2
    body = lp(noise(d), 900, 4) * np.exp(-t*2.8) * 2.2
    crack = hp(noise(d), 2500) * np.exp(-t*9) * .5
    deb = np.zeros(len(t))
    for _ in range(26):
        s = rng.uniform(.4, 2.2); tk = tock() * rng.uniform(.2, .5); i = int(s*SR); deb[i:i+len(tk)] += tk[:len(deb)-i]
    return np.tanh((low + body + crack) * 1.4) * .95 + deb * .6
def scratch():
    d = .45; t = tt(d); m = np.sin(2*np.pi*np.cumsum(3 + 9*t)/SR*2*np.pi)
    x = bp(noise(d), 600, 4000) * (.5 + .5*np.sign(m)) ; return x * env(len(t), .005, r=.05) * .5
def wind(d): t = tt(d); return bp(noise(d), 200, 1500) * (.6 + .4*np.sin(2*np.pi*.7*t)) * env(len(t), .1, r=.2) * .35
def chime_arp(): x = np.zeros(int(2.4*SR))
def magic():
    x = np.zeros(int(2.6*SR))
    for k, f in enumerate([1046.5, 1318.5, 1568, 2093, 2637, 3136]):
        b = bell(f, 1.6, .16); i = int(k*.09*SR); x[i:i+len(b)] += b[:len(x)-i]
    return x
def cough():
    x = np.zeros(int(.8*SR))
    for s in (0, .28):
        n = bp(noise(.18), 300, 2500) * env(int(.18*SR), .01, d=.05) * .45; i = int(s*SR); x[i:i+len(n)] += n
    return x

sfx = np.zeros(N)
def put(x, t, g=1.0):
    i = int(t * SR); j = min(N, i + len(x)); sfx[i:j] += x[:j - i] * g

# timings mirroring the picture
tPress = S('press') - 0.32; tTrap = S('press') + 0.15; hang = S('fall') - 0.05
tj = E('jump') + 0.25; tLand = S('wait') - 0.35; tg = S('grab') + 0.8; tRumble = E('grab') + 0.15
c0 = S('climb') - 0.1; sh13 = S('phew') - 0.3; tBlue = S('boom') + 0.35; tBoom = E('boom') + 0.15
sh0 = S('card') - 0.25; sh7 = S('gold') - 0.3; sh16 = E('boom') + 1.0

put(wind(sh0), 0, 1.2)
put(slide(1400, 500, sh0 - .1), 0.05, .5)
put(scratch(), sh0 - .05, 1.0)
put(whoosh(.6, 400, 4000), sh0 + .1, .6)
put(bell(1568, 1.4, .2), S('card'), 1)
# footsteps during the walk
walk_end = S('warn') - 0.1
k = S('see') - 1.6
while k < walk_end - .3:
    put(step(), k, 1.0); k += 0.35
put(pop(), S('see') + .3, .5)
put(click(), tPress, 1.5)
put(tock(), tPress + .02, .8)
put(slide(900, 1400, .25), tTrap - .1, .5)
put(whoosh(.4), tTrap, .7)
for i in range(4): put(thud(), tTrap + .9 + i*.08, .25)
put(slide(1600, 250, 1.1), hang + .05, .9)
put(whoosh(.7, 300, 2500), tj, .9)
put(magic(), sh7 + .05, 1.0)
for i in range(10): put(bell(rng.choice([2093, 2349, 2637, 3136]), .6, .06), sh7 + .4 + i*.37)
put(thud(), tLand, 1.4)
put(chaching(), tg, 1.2)
put(rumble(sh13 - tRumble + .3), tRumble, 1.0)
put(bubbles(sh13 - tRumble - 1.2), tRumble + 1.2, 1.0)
# pillar blocks
for k in range(1, 15): put(tock(), c0 + k*.36, .9)
k = 1
while c0 + .9 + k*.414 < sh13: put(tock(), c0 + .9 + k*.414, .6); k += 1
put(whoosh(.5), sh13, .7); put(whoosh(.5), sh13 + .35, .6)
put(thud(), sh13 + .55, .7); put(thud(), sh13 + .9, .7)
put(pop(), S('blue') + .2, .5)
put(click(), tBlue, 1.5)
put(slide(400, 1500, .6), tBlue + .05, .35)
put(boom(), tBoom, 1.0)
put(cough(), sh16 + .4, .9); put(cough(), sh16 + 1.3, .7)
# end card: subscribe click loops (pressed when (t%2) in [1.55,1.75])
te = S('end') - .3
t0 = np.ceil(te / 2) * 2 + 1.55 - 2
while t0 < TOTAL:
    if t0 > te + .2: put(click(), t0, .9); put(bell(2637, .5, .12), t0 + .02)
    t0 += 2

# ---------- MUSIC ----------
mus = np.zeros(N)
def mput(x, t, g=1.0):
    i = int(t * SR); j = min(N, i + len(x));
    if i < N: mus[i:j] += x[:j - i] * g
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
def pluck(f, d=.25, amp=.3, bright=1.0):
    t = tt(d); x = np.sin(2*np.pi*f*t) + .5*bright*np.sin(4*np.pi*f*t)*np.exp(-t*12) + .25*bright*np.sin(6*np.pi*f*t)*np.exp(-t*20)
    return x * np.exp(-t*9) * env(len(t), .003, r=.02) * amp
def bassn(f, d=.22, amp=.4): t = tt(d); return (np.sin(2*np.pi*f*t) + .3*np.sin(4*np.pi*f*t)) * np.exp(-t*7) * env(len(t), .004, r=.03) * amp
def kick(): t = tt(.25); return np.sin(2*np.pi*np.cumsum(50 + 110*np.exp(-t*30))/SR) * np.exp(-t*14) * .8
def snare(): t = tt(.2); return (bp(noise(.2), 1200, 6000) * .6 + np.sin(2*np.pi*190*t) * .4) * np.exp(-t*22) * .5
def hat(): t = tt(.05); return hp(noise(.05), 7000) * np.exp(-t*80) * .2
def pad(fs, d, amp=.08):
    t = tt(d); x = sum(np.sin(2*np.pi*f*t + np.sin(2*np.pi*.3*t)) + .3*np.sin(2*np.pi*f*2.002*t) for f in fs)
    return x * env(len(t), .6, r=.8) * amp

# Section 1: sneaky pizzicato (walk to button), stops at the press
def sneaky(t0, t1):
    bpm = 118; b = 60 / bpm
    prog = [(57, [69, 72, 76, 72, 74, 72, 69, 68]), (62, [69, 74, 77, 74, 76, 74, 72, 69]), (64, [68, 71, 76, 71, 74, 71, 68, 64]), (57, [69, 72, 76, 81, 80, 76, 72, 69])]
    t = t0; bar = 0
    while t < t1:
        root, mel = prog[bar % 4]
        for q in range(4):
            if t + q*b < t1:
                mput(bassn(mid(root - 12 + (7 if q % 2 else 0))), t + q*b)
                mput(tock() * .25, t + q*b + b/2)
        for e in range(8):
            te_ = t + e*b/2
            if te_ < t1 and (e % 2 == 0 or rng.random() < .7): mput(pluck(mid(mel[e]), .22, .22), te_)
        t += 4*b; bar += 1
sneaky(S('see') - 0.9, tPress - .05)
# Section 2: magic cave
def magic_cave(t0, t1):
    chords = [[60, 64, 67, 71], [65, 69, 72, 76], [57, 60, 64, 67], [62, 65, 69, 72]]
    d = 1.6; t = t0; k = 0
    while t < t1:
        c = chords[k % 4]; mput(pad([mid(n - 12) for n in c], min(d + .6, t1 - t + .3), .045), t)
        for i in range(8):
            if t + i*.2 < t1: mput(bell(mid(c[i % 4] + 12), .7, .05), t + i*.2)
        t += d; k += 1
magic_cave(sh7 + .2, tRumble)
# Section 3: action
def action(t0, t1):
    bpm = 150; b = 60 / bpm; t = t0; bar = 0
    riff = [52, 52, 55, 52, 57, 52, 55, 50]
    lead = [[76, 74, 71, 74], [76, 79, 78, 74], [76, 74, 71, 69], [71, 74, 76, 76]]
    while t < t1:
        for q in range(4):
            tq = t + q*b
            if tq >= t1: break
            mput(kick(), tq); mput(hat(), tq + b/2)
            if q % 2: mput(snare(), tq)
            for e in range(2): mput(bassn(mid(riff[(q*2+e) % 8] - 12), .14, .45), tq + e*b/2)
            mput(pluck(mid(lead[bar % 4][q]), .3, .16, 1.6), tq)
        t += 4*b; bar += 1
action(tRumble + .4, sh13 - .05)
# Section 4: happy bounce
def happy(t0, t1, root=60):
    bpm = 126; b = 60 / bpm; t = t0; bar = 0
    prog = [0, 5, 7, 0]; mel = [[76, 79, 76, 72], [77, 81, 77, 72], [79, 77, 76, 74], [72, 76, 79, 84]]
    while t < t1:
        r = root + prog[bar % 4]
        for q in range(4):
            tq = t + q*b
            if tq >= t1: break
            mput(bassn(mid(r - 12 if q % 2 == 0 else r - 5)), tq)
            mput(pluck(mid(r + 4 + (3 if q % 2 else 0)), .15, .08), tq + b/2)
            mput(bell(mid(mel[bar % 4][q] + (root - 60)), .35, .07), tq)
            if q % 2: mput(snare()*.35, tq)
            else: mput(kick()*.6, tq)
        t += 4*b; bar += 1
happy(sh13 + .6, S('boom') - .1)
happy(S('end') - .3, TOTAL, 65)
mput(slide(300, 120, 1.2) * .8, S('boom') - .1)  # "uh-oh" tuba-ish dive

# ---------- VOICES ----------
voice = np.zeros(N)
for bb in tl['beats']:
    raw = subprocess.check_output(['ffmpeg', '-loglevel', 'error', '-i', bb['file'], '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'])
    a = np.frombuffer(raw, dtype=np.float32); i = int(bb['start'] * SR); voice[i:i + len(a)] += a[:N - i]
# ducking
act = np.abs(voice) > .02
act = np.convolve(act.astype(float), np.ones(int(.15*SR)) / int(.15*SR), 'same') > 0.05
gain = np.where(act, .45, 1.0); gain = np.convolve(gain, np.ones(int(.08*SR)) / int(.08*SR), 'same')
mix = voice * 1.0 + mus * gain * .55 + sfx * .7
mix = np.tanh(mix * 1.1) / 1.1
mix = mix[:int(TOTAL * SR)]
st = np.stack([mix, mix], 1).astype(np.float32)
open('out/mix.f32', 'wb').write(st.tobytes())
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'out/mix.f32', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', 'out/mix.wav'], check=True)
print('ok', TOTAL)
