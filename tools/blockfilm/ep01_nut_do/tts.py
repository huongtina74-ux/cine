import json, os, subprocess, wave, sys
from piper import PiperVoice, SynthesisConfig
T=os.environ.get('PIPER_VOICES','voices').rstrip('/')+'/'
def mk(name):
    d=T+f'vits-piper-{name}/'
    return PiperVoice.load(d+f'{name}.onnx', config_path=d+f'{name}.onnx.json')
voices={'a':mk('vi_VN-vais1000-medium')}
# who -> (voice, speed, pitch factor)
V={'bin':('a',0.98,1.35),'bo':('a',0.9,1.06),'nar':('a',0.95,0.86)}
S=json.load(open('script.json'))
t=0.0; out=[]
for i,b in enumerate(S):
    v,sp,pf=V[b['who']]; sp=b.get('speed',sp) if b['who']=='nar' else sp
    raw=f'audio/raw_{i:02d}.wav'; fin=f'audio/v_{i:02d}.wav'
    with wave.open(raw,'wb') as w:
        voices[v].synthesize_wav(b['text'],w,syn_config=SynthesisConfig(length_scale=1/sp,noise_scale=0.75,noise_w_scale=0.9))
    sr=wave.open(raw).getframerate()
    af=f'asetrate={int(sr*pf)},aresample=48000,atempo={1/pf:.4f},silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',raw,'-af',af,'-ar','48000','-ac','1',fin],check=True)
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',fin]))
    t+=b['pre']; b2=dict(b,i=i,start=round(t,3),dur=round(d,3),file=fin); out.append(b2); t+=d+b['post']
    print(f"{b['id']:8s} {b['start'] if 'start' in b else b2['start']:6.2f} {d:5.2f}")
json.dump({'beats':out,'total':round(t,3)},open('web/timeline.json','w'),ensure_ascii=False,indent=1)
print('TOTAL',t)
