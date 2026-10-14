import json,os,sys
from pathlib import Path
P='__CINEFACTORY_JSON__'; print(P+json.dumps({'type':'ready','pid':os.getpid(),'backend':'mock'}),flush=True)
for raw in sys.stdin:
    if not raw.startswith(P):continue
    m=json.loads(raw[len(P):]); rid=m.get('request_id'); op=m.get('op')
    if op=='ping':print(P+json.dumps({'request_id':rid,'ok':True,'pid':os.getpid()}),flush=True)
    elif op=='render':
        out=Path(m['job']['output_path']); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps({'pid':os.getpid(),'shot_id':m['job']['shot']['shot_id']})); print(P+json.dumps({'request_id':rid,'ok':True,'pid':os.getpid(),'output_path':str(out)}),flush=True)
    elif op=='shutdown': print(P+json.dumps({'request_id':rid,'ok':True,'pid':os.getpid()}),flush=True); break
