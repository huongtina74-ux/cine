import json, subprocess, numpy as np  # ep02: same synth kit as ep01
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
    i = int(t * SR)
    if i < 0 or i >= N: return
    j = min(N, i + len(x)); sfx[i:j] += x[:j - i] * g
def sob():
    d = .22; t = tt(d); f = 520 + 120*np.exp(-t*12)
    return (np.sin(2*np.pi*np.cumsum(f)/SR) * .25 + bp(noise(d), 500, 1800) * .35) * np.exp(-t*14) * env(len(t), .01) * .5
def chomp(): x = lp(noise(.09), 1800) * env(int(.09*SR), .002, d=.025) * .7; return x
def creak(d=.6): t = tt(d); f = 180 + 40*np.sin(2*np.pi*3*t); return np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)) * bp(noise(d), 300, 1200) * .15 * env(len(t), .05, r=.1)
def boing(): t = tt(.5); f = 220 + 160*np.sin(2*np.pi*9*t) * np.exp(-t*5); return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*5) * .45

X = dict(s1=S('hook')-.15, s2=E('hook')+.55, s3=S('kick')-.2, s4=S('huh')-.3, s5=S('cry')-.15, s6=S('okay')-.2, s7=S('hide')-.15, s8=S('apple')-.25,
    s9=S('yum')-.4, s10=S('gone')-.2, s11=S('idea')-.2, s12=S('build')-.05, s13=E('build')+.15, s14=S('ouch')-.55, s15=E('ouch')+1.3, s16=S('tada')-.15,
    s17=S('yay')-.4, s18=S('hug')-.3, s19=E('hug')+.9)
tC = .42; kickT = S('kick')-.15; kb = kickT+.05; land = kb+1.15
tClear = X['s13']+.15; tB0 = X['s13']+.35; tB1 = S('tada')-.35; tDrop = S('ouch')-.12
NB = 46 + 49 + 25 + 9 + 2

put(wind(X['s2']), 0, .5)
put(creak(.45), tC-.4, 1.0)
for i in range(6): put(thud(), tC + .05 + i*.11, .5 + .1*(i%2))
for i in range(14): put(tock(), tC + .5 + rng.uniform(0, .9), rng.uniform(.3, .6))
put(rumble(.9), tC, .5); put(whoosh(.5, 300, 2500), tC, .5)
k = X['s1'] + .3
while k < X['s2'] - .2: put(sob(), k, 1.0); k += .5
k = X['s2'] - .6
while k < kickT - .1: put(step(), k, .9); put(pop()*.3, k + .11, .5); k += .22
put(thud(), kickT, .8); put(whoosh(.7, 400, 3500), kickT + .05, .8)
put(thud(), land, .6); put(tock(), land + .32, .4); put(tock(), land + .55, .25)
k = X['s4'] - .5
while k < X['s4'] + .9: put(step(), k, .7); k += .32
put(pop(), S('huh') - .05, .6)
k = X['s5'] + .2
while k < X['s6'] + .4: put(sob(), k, .9); k += .5
k = X['s6'] - .9
while k < X['s6'] + .1: put(step(), k, .6); k += .34
put(slide(900, 1300, .25), X['s7'] + .15, .4)
put(bell(1568, .9, .2), S('apple') + .2)
for i in range(5): put(chomp(), X['s9'] + .35 + i*.3, 1.0)
put(magic(), S('yum') + .05, .7)
put(slide(620, 300, 1.0), S('gone') + 1.5, .45)
put(bell(2093, 1.2, .25), X['s11'] + .05); put(bell(2637, 1.2, .2), X['s11'] + .12)
put(pop(), tClear - .3, .7); put(whoosh(.6), tClear - .25, .6)
dt = (tB1 - tB0) / NB
for i in range(0, NB, 2): put(tock(), tB0 + i*dt, rng.uniform(.35, .55))
put(thud(), tDrop + .18, 1.0); put(tock(), tDrop + .2, 1.0); put(boing(), tDrop + .25, .9)
put(magic(), S('tada') - .15, 1.0); put(chaching(), S('tada') - .05, .8)
for i in range(6): put(pop(), S('tada') - .1 + i*.07, .35)
for i in range(8): put(bell(rng.choice([2093, 2349, 2637, 3136]), .6, .07), S('yay') - .4 + i*.22)
for i, f in enumerate([1046.5, 1318.5, 1568, 2093]): put(bell(f, 1.4, .12), X['s18'] + .1 + i*.18)
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

def sad(t0, t1):
    bpm = 72; b = 60 / bpm; t = t0; bar = 0
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    mel = [[76, 74, 72, 71], [72, 69, 72, 74], [76, 79, 76, 72], [74, 71, 67, 71]]
    while t < t1:
        c = chords[bar % 4]; dd = min(4*b + .6, t1 - t + .4)
        if dd > 1.6: mput(pad([mid(n) for n in c], dd, .04), t)
        mput(bassn(mid(c[0] - 12), 1.2, .25), t)
        for q in range(4):
            if t + q*b < t1: mput(pluck(mid(mel[bar % 4][q]), .9, .13, .6), t + q*b)
        t += 4*b; bar += 1
sad(0.15, X['s2'] - .1)
happy(X['s2'] - .1, S('huh') - .35, 60)
mput(slide(700, 200, .5) * .6, S('huh') - .35)
sad(X['s4'] + .2, X['s11'] - .05)
happy(X['s11'] - .05, S('tada') - .2, 62)
happy(S('tada') - .2, TOTAL, 65)
# ---------- VOICES ----------
voice = np.zeros(N)
for bb in tl['beats']:
    raw = subprocess.check_output(['ffmpeg', '-loglevel', 'error', '-i', bb['file'], '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'])
    a = np.frombuffer(raw, dtype=np.float32); i = int(bb['start'] * SR); voice[i:i + len(a)] += a[:N - i]
# ducking
act = np.abs(voice) > .02
act = np.convolve(act.astype(float), np.ones(int(.15*SR)) / int(.15*SR), 'same') > 0.05
gain = np.where(act, .4, 1.0); gain = np.convolve(gain, np.ones(int(.08*SR)) / int(.08*SR), 'same')
mix = voice * 1.0 + mus * gain * .55 + sfx * .7
mix = np.tanh(mix * 1.1) / 1.1
mix = mix[:int(TOTAL * SR)]
st = np.stack([mix, mix], 1).astype(np.float32)
open('out/mix.f32', 'wb').write(st.tobytes())
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', 'out/mix.f32', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', 'out/mix.wav'], check=True)
print('ok', TOTAL)
