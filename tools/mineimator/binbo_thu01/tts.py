import json, numpy as np, soundfile as sf, sys
from kokoro_onnx import Kokoro
from scipy.signal import resample
K=Kokoro(sys.argv[1]+'/kokoro-v1.0.onnx', sys.argv[1]+'/voices-v1.0.bin')
V={'bin':('am_puck',1.28),'bo':('am_michael',1.22),'zu':('af_sky',1.32)}
lines=[('zu1','zu',"Waaah... I'm lost..."),
       ('bin1','bin',"Huh? Bo, look! A baby zombie!"),
       ('bo1','bo',"Hey, little guy. Are you okay?"),
       ('zu2','zu',"I can't find my house..."),
       ('bin2','bin',"Don't cry! We'll help you!"),
       ('zu3','zu',"Really? Yaaay!"),
       ('bo2','bo',"Group hug!")]
out=[]
for i,w,t in lines:
    v,p=V[w]; a,sr=K.create(t,voice=v,speed=1.0/p*0.92,lang='en-us')
    a=resample(a,int(len(a)/p)).astype(np.float32)  # pitch+speed up (cartoon)
    # trim silence
    e=np.abs(a)>0.01; idx=np.where(e)[0]; a=a[max(0,idx[0]-200):idx[-1]+800]
    sf.write(f'vo/{i}.wav',a,sr)
    # mouth envelope at 24 fps
    hop=sr//24; env=[float(np.sqrt(np.mean(a[k*hop:(k+1)*hop]**2))) for k in range(len(a)//hop+1)]
    out.append(dict(id=i,who=w,text=t,dur=len(a)/sr,env=env))
json.dump(out,open('vo/lines.json','w'))
for o in out: print(o['id'],round(o['dur'],2))
