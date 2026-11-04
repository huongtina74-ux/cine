import json, subprocess, numpy as np
tl=json.load(open('web/timeline.json'))
for b in tl['beats']:
    raw=subprocess.check_output(['ffmpeg','-loglevel','error','-i',b['file'],'-f','f32le','-ac','1','-ar','48000','-'])
    a=np.frombuffer(raw,dtype=np.float32); n=1600
    fr=[float(np.sqrt(np.mean(a[i:i+n]**2))) for i in range(0,len(a),n)]
    m=max(fr) or 1
    b['env']=[round(min(1,x/m*1.3),2) for x in fr]
json.dump(tl,open('web/timeline.json','w'),ensure_ascii=False)
print(len(tl['beats']), tl['total'])
