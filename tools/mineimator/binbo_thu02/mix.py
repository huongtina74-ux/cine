import json, sys, numpy as np, soundfile as sf, subprocess
import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','blockfilm')); import sfxkit
from scipy.signal import resample_poly
SR=48000; T=json.load(open('proj/timing.json')); FPS=T['fps']; TOTAL=T['end']/FPS
N=int(TOTAL*SR)+SR; voice=np.zeros(N); sfx=np.zeros(N); mus=np.zeros(N)
def put(buf,x,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(x)); buf[i:j]+=x[:j-i]*g
f=lambda fr: fr/FPS
for l in json.load(open('vo/lines.json')):
    a,sr=sf.read(f"vo/{l['id']}.wav"); a=resample_poly(a,SR,sr)
    put(voice,a,f(T['start'][l['id']]))
S=lambda n: sfxkit.SOUNDS[n]()
# footsteps while walking in (0..80), two walkers
for fr in range(0,80,6): put(sfx,S('step_grass'),f(fr),.45); put(sfx,S('step_grass'),f(fr+3),.35)
for fr in (2,30,58): put(sfx,S('sob'),f(fr)+.6,.55)
put(sfx,S('pop'),f(66),.5)                      # Bin & Bo notice (wow face)
put(sfx,S('whoosh'),f(96),.35)                  # Bin points
put(sfx,S('slide_down'),f(206)+1.4,.3)          # sad answer
put(sfx,S('idea_ding'),f(262),.5)               # "We'll help you!"
put(sfx,S('sparkle'),f(300),.6); put(sfx,S('slide_up'),f(300),.4)
for fr in (324,338,352): put(sfx,S('boing'),f(fr),.55)
put(sfx,S('xp_ding'),f(356),.5); put(sfx,S('sparkle'),f(384),.5)
# music: sad pad until 12.5s, happy bounce after
t=np.arange(int(SR*8))/SR
mid=lambda m:440*2**((m-69)/12)
def note(fr,d,amp,dec=6):
    tt=np.arange(int(SR*d))/SR; return (np.sin(2*np.pi*fr*tt)+.3*np.sin(4*np.pi*fr*tt))*np.exp(-tt*dec)*amp
def pad(fs,d,amp):
    tt=np.arange(int(SR*d))/SR; x=sum(np.sin(2*np.pi*q*tt) for q in fs); e=np.minimum(1,np.minimum(tt/.5,(d-tt)/.6)); return x*e*amp
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]; b=60/72
tt0=0.2; k=0
while tt0<f(300)-.2:
    c=chords[k%4]; d=min(4*b+.5, f(300)-tt0); 
    if d>1.2: put(mus,pad([mid(n) for n in c],d,.035),tt0)
    for q,m in enumerate([76,74,72,71] if k%2==0 else [72,69,72,74]):
        if tt0+q*b<f(300)-.3: put(mus,note(mid(m),.9,.07,5),tt0+q*b)
    tt0+=4*b; k+=1
b=60/126; tt0=f(300); k=0; prog=[0,5,7,0]
while tt0<TOTAL:
    r=62+prog[k%4]
    for q in range(4):
        tq=tt0+q*b
        if tq>=TOTAL: break
        put(mus,note(mid(r-12),.3,.25,7),tq); put(mus,note(mid([78,81,78,74][q]+prog[k%4]),.3,.06,9),tq)
    tt0+=4*b; k+=1
act=np.convolve((np.abs(voice)>.02).astype(float),np.ones(int(.15*SR))/int(.15*SR),'same')>.05
gain=np.convolve(np.where(act,.35,1.0),np.ones(int(.08*SR))/int(.08*SR),'same')
mix=np.tanh((voice+mus*gain*.6+sfx*.7)*1.1)/1.1; mix=mix[:int(TOTAL*SR)]
sf.write('mix_raw.wav',np.stack([mix,mix],1).astype(np.float32),SR)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','mix_raw.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar','48000','mix.wav'],check=True)
print('MIX_OK', round(TOTAL,2))
