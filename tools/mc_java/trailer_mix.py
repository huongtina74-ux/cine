import numpy as np, soundfile as sf, subprocess
from scipy.signal import butter, sosfilt
SR=48000; TOT=32.0; N=int(TOT*SR)+SR
rng=np.random.default_rng(5)
tt=lambda d: np.arange(int(d*SR))/SR
lp=lambda x,c: sosfilt(butter(2,c,'low',fs=SR,output='sos'),x)
bp=lambda x,a,b: sosfilt(butter(2,[a,b],'band',fs=SR,output='sos'),x)
mid=lambda m: 440*2**((m-69)/12)
mus=np.zeros(N); sfx=np.zeros(N); vo=np.zeros(N)
def put(b,x,t,g=1.0):
    i=int(t*SR); j=min(len(b),i+len(x)); b[i:j]+=np.asarray(x[:j-i])*g
def saw(f,d): t=tt(d); return 2*((f*t)%1)-1
def fade(x,a,r):
    n=len(x);e=np.ones(n);na,nr=int(a*SR),int(r*SR);e[:na]=np.linspace(0,1,na);e[-nr:]*=np.linspace(1,0,nr);return x*e
def strings(notes,d,g):
    x=sum(lp(saw(mid(n)*(1+.004*k),d)+saw(mid(n)*(1-.004*k),d),1800) for k,n in enumerate(notes))/len(notes)
    t=tt(d); return fade(x*(1+.15*np.sin(2*np.pi*5*t)),.8,.8)*g
def taiko(g=1):
    t=tt(.9); return (np.sin(2*np.pi*np.cumsum(55+80*np.exp(-t*18))/SR)*np.exp(-t*5)+lp(rng.standard_normal(len(t)),400)*np.exp(-t*14)*.6)*g
def boom():
    t=tt(3.5); return np.tanh((np.sin(2*np.pi*np.cumsum(30+70*np.exp(-t*4))/SR)*np.exp(-t*1.2)*1.6+lp(rng.standard_normal(len(t)),300)*np.exp(-t*3)*1.2)*1.3)
def riser(d):
    t=tt(d); return bp(rng.standard_normal(len(t)),400,7000)*(t/d)**2*.5+np.sin(2*np.pi*np.cumsum(200*8**(t/d))/SR)*(t/d)**2*.2
# D minor: Dm - Bb - Gm - A
prog=[[50,57,62,65],[46,53,58,62],[43,50,55,58],[45,52,57,61]]
for i,ch in enumerate(prog*2):
    t0=i*4.0
    if t0>=TOT: break
    put(mus,strings(ch,4.6,.10),t0)
    put(mus,fade(lp(saw(mid(ch[0]-12),4.4),300),.2,.5)*.25,t0)
# taiko pattern grows each section
pat={0:[0,2],1:[0,1,2,3],2:[0,.75,1.5,2,2.75,3.5],3:[0,.5,1,1.5,2,2.5,3,3.25,3.5,3.75]}
for bar in range(8):
    sec=min(3,bar//2)
    for b in pat[sec]: put(mus,taiko(.55+.1*sec),bar*4.0+b*1.0)
cuts=[9.4,16.2,23.0]
for c in cuts: put(sfx,boom(),c,.7); put(sfx,riser(1.2),c-1.2,.35)
put(sfx,boom(),28.8,1.0)
# narration
for f,t in (("am_onyx_n1.wav",.8),("am_onyx_n2.wav",9.9),("am_onyx_n3.wav",17.0),("am_onyx_n4.wav",23.5)):
    a,sr=sf.read(f); 
    if sr!=SR: a=np.interp(np.arange(0,len(a),sr/SR),np.arange(len(a)),a)
    put(vo,a,t)
# simple reverb on voice
ir=np.exp(-np.arange(int(.6*SR))/SR*7)*rng.standard_normal(int(.6*SR))*.02; ir[0]=1
vo2=np.convolve(vo,ir)[:N]
act=np.convolve((np.abs(vo)>.02).astype(float),np.ones(int(.2*SR))/int(.2*SR),'same')>.05
duck=np.convolve(np.where(act,.45,1.0),np.ones(int(.1*SR))/int(.1*SR),'same')
mix=vo2*1.0+(mus*duck)*.8+sfx*.6
e=np.ones(len(mix)); e[-int(1.5*SR):]=np.linspace(1,0,int(1.5*SR)); mix*=e
mix=np.tanh(mix*1.1)/1.1; mix=mix[:int(TOT*SR)]
sf.write('mix_raw.wav',np.stack([mix,mix],1).astype(np.float32),SR)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','mix_raw.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11','-ar','48000','mix.wav'],check=True)
print('ok')
