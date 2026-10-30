#!/usr/bin/env python3
"""CINE Muse Image production queue -- DRY RUN by default.

Workflow:
  1. Generate standalone master from USER ORIGINAL image.
  2. Human visually approves each master in metadata/approved_masters.json.
  3. Generate single-frame angle/expression/action/detail plates from that master.

Official: https://dev.meta.ai/docs/cookbook/image-generation-basics
Requires openai package and MODEL_API_KEY for --execute; requests may be billable.
"""
import argparse, base64, csv, hashlib, json, os, mimetypes, pathlib, re, sys, time
from dataclasses import dataclass

TAGS=('bo','me','juno','Lia','bubu','bix','ongngoai','bangoai','ongnoi','banoi')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content_part(p):
    mime=mimetypes.guess_type(p.name)[0] or 'image/png'
    return {'type':'input_image','image_url':f'data:{mime};base64,'+base64.b64encode(p.read_bytes()).decode('ascii')}
def read_rows(p):
    with p.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def read_prompts(p):
    raw=p.read_text(encoding='utf8'); lines=raw.rstrip('\n').split('\n')
    assert len(lines)==539 and all((i%2==0 and lines[i].strip()) or (i%2==1 and lines[i]=='') for i in range(len(lines))), 'Expected 270 one-line prompts, each separated by one blank line'
    return lines[::2]
def save_image(output,base64text):
    data=base64.b64decode(base64text)
    kind=('.png' if data.startswith(b'\x89PNG') else '.jpg' if data.startswith(b'\xff\xd8') else '.webp' if data.startswith(b'RIFF') else None)
    if not kind: raise ValueError('Unrecognized image bytes; not saving arbitrary binary')
    output=output.with_suffix(kind);output.parent.mkdir(parents=True,exist_ok=True)
    tmp=output.with_suffix(output.suffix+'.tmp');tmp.write_bytes(data);tmp.replace(output)
    return output

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-pack',required=True,help='Extracted CINE_A2_CHARACTER_REFERENCE_LIBRARY_V1_1_R1 folder')
    ap.add_argument('--stage',choices=['masters','views'],default='masters')
    ap.add_argument('--tag',choices=list(TAGS)+['all'],default='Lia')
    ap.add_argument('--max-jobs',type=int,default=1)
    ap.add_argument('--execute',action='store_true',help='Real potentially billable API; otherwise dry-run')
    ap.add_argument('--destination',required=True,help='Output directory outside canonical assets; never overwrite original')
    args=ap.parse_args();source=pathlib.Path(args.source_pack);dest=pathlib.Path(args.destination)
    if args.max_jobs<1:ap.error('--max-jobs must be >= 1')
    manifest=json.loads((source/'metadata/CHARACTER_REFERENCE_REGISTRY.json').read_text(encoding='utf8'))
    targets=read_rows(source/'metadata/RENDER_TARGETS_270_SLOTS.csv')
    prompts=read_prompts(source/'prompts/MUSE_270_SINGLE_IMAGE_PROMPTS_ONE_LINE_BLANK.txt')
    if len(targets)!=270 or len(prompts)!=270:raise ValueError('Expected exactly 270 targets/prompts')
    entries=[]
    for i,(target,prompt) in enumerate(zip(targets,prompts)):
        t=target['character_tag'];slot=target['target_slot'];
        if args.tag!='all' and t!=args.tag:continue
        is_master=slot=='MASTER_FRONT_FULL_BODY'
        if (args.stage=='masters') != is_master:continue
        src_original=next(x['original'] for x in manifest['characters'] if x['tag']==t)
        original_file=source/src_original['file']
        if not original_file.is_file() or sha(original_file)!=src_original['sha256']:raise RuntimeError('Original SHA mismatch for '+t)
        if args.stage=='masters':ref=original_file
        else:
            # View images must be produced ONLY from a human-approved new master, not a crop masquerading as one.
            approved=dest/'approved_masters.json'
            if not approved.is_file():raise RuntimeError('Master review registry missing: '+str(approved))
            reg=json.loads(approved.read_text(encoding='utf8'))
            record=reg.get(t)
            if not record or record.get('approved_by') in [None,''] or record.get('status')!='APPROVED_FOR_REFERENCE':raise RuntimeError('Master not approved for '+t)
            ref=dest/record['file']
            if not ref.is_file() or sha(ref)!=record['sha256']:raise RuntimeError('Approved master missing/changed '+t)
        entries.append((i,t,slot,prompt,ref))
    entries=entries[:args.max_jobs]
    if not args.execute:
        for i,t,slot,prompt,ref in entries: print(json.dumps({'mode':'DRY_RUN','tag':t,'slot':slot,'source_file':str(ref),'source_sha256':sha(ref),'prompt_length':len(prompt),'model':'muse-image-1.0','would_cost_credits':'CHECK_PROVIDER_PRICING'},ensure_ascii=False))
        return
    if not os.environ.get('MODEL_API_KEY'):raise RuntimeError('MODEL_API_KEY missing; no paid generation attempted')
    from openai import OpenAI
    client=OpenAI(base_url='https://api.meta.ai/v1',api_key=os.environ['MODEL_API_KEY'])
    dest.mkdir(parents=True,exist_ok=True)
    logpath=dest/'muse_generation_audit.jsonl'
    for i,t,slot,prompt,ref in entries:
        outfile_stub=dest/t/slot
        existing=next((p for ext in ('.png','.jpg','.webp') if (p:=outfile_stub.with_suffix(ext)).exists()),None)
        if existing:
            print(json.dumps({'skip_existing':str(existing),'sha256':sha(existing)}));continue
        request=[{'role':'user','content':[{'type':'input_text','text':prompt},content_part(ref)]}]
        try:
            response=client.responses.create(model='muse-image-1.0',input=request)
            if getattr(response,'status',None)!='completed':raise RuntimeError('Muse status '+str(getattr(response,'status',None)))
            image_item=next((item for item in response.output if getattr(item,'type',None)=='image_generation_call' and getattr(item,'result',None)),None)
            if not image_item:raise RuntimeError('Muse returned no image_generation_call.result')
            file=save_image(outfile_stub,image_item.result)
            report={'tag':t,'slot':slot,'status':'DRAFT_GENERATED_REVIEW_REQUIRED','file':str(file.relative_to(dest)),'sha256':sha(file),'source_sha256':sha(ref),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'model':'muse-image-1.0','response_id':response.id,'human_approved':False}
            with logpath.open('a',encoding='utf8') as f:f.write(json.dumps(report,ensure_ascii=False)+'\n')
            print(json.dumps(report,ensure_ascii=False))
        except Exception as exc:
            with logpath.open('a',encoding='utf8') as f:f.write(json.dumps({'tag':t,'slot':slot,'status':'FAILED','error_type':type(exc).__name__,'error':str(exc)[:300]})+'\n')
            raise

if __name__=='__main__': main()