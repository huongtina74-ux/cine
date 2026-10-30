#!/usr/bin/env python3
"""Optional vendor-neutral single-worker generation adapter; DRY RUN unless --execute."""
import argparse, json, pathlib, subprocess, shlex, time, os, hashlib, sys
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parent.parent

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--execute',action='store_true',help='Actually call explicitly configured image provider CLI; may incur fees')
 ap.add_argument('--command-template',default='',help='Argv CLI command with {prompt_file}, {output_file}, {plate_id}; no shell interpolation')
 ap.add_argument('--start',type=int,default=0);ap.add_argument('--limit',type=int,default=1)
 ap.add_argument('--cooldown',type=float,default=1.5);ap.add_argument('--timeout',type=int,default=240)
 ap.add_argument('--output-root',type=pathlib.Path,default=ROOT)
 args=ap.parse_args()
 rows=[json.loads(x) for x in (ROOT/'queue/ALL_1239_ASSET_WORK_ORDERS.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
 if args.start<0 or args.limit<1 or args.start>=len(rows):ap.error('Invalid start/limit')
 batch=rows[args.start:args.start+args.limit]
 if not args.execute:
  print(json.dumps({'mode':'DRY_RUN','scheduled':[x['plate_id'] for x in batch], 'real_images_generated':0,'estimated_cost':'NOT_AVAILABLE_CHECK_PROVIDER'},ensure_ascii=False));return
 if not args.command_template or ('{output_file}' not in args.command_template) or ('{prompt_file}' not in args.command_template):ap.error('Executing requires explicit configured image provider command-template with {output_file} and {prompt_file}')
 prompt_dir=args.output_root/'runtime_prompts';prompt_dir.mkdir(parents=True,exist_ok=True)
 log=args.output_root/'generation_log.jsonl';done=0
 for row in batch:
  target=args.output_root/row['output_relpath'];target.parent.mkdir(parents=True,exist_ok=True)
  promptfile=prompt_dir/(row['plate_id']+'.txt');promptfile.write_text(row['prompt']+'\n',encoding='utf-8')
  cmd=args.command_template.replace('{prompt_file}',str(promptfile)).replace('{output_file}',str(target)).replace('{plate_id}',row['plate_id'])
  argv=shlex.split(cmd)
  try:
   if target.exists():raise RuntimeError('File exists; no overwrite of previous shot')
   r=subprocess.run(argv,timeout=args.timeout,check=False,capture_output=True,text=True)
   if r.returncode!=0:raise RuntimeError(f'Provider failed exit={r.returncode}; stderr={r.stderr[-300:]}')
   if not target.is_file():raise RuntimeError('Provider returned success but no actual image file')
   with Image.open(target) as img:
    img.verify()
   with Image.open(target) as img:w,h=img.size
   if abs(w/h-16/9)>0.012 or w<1280 or h<720:raise RuntimeError(f'Not native 16:9 >=720p; got {w}x{h}. Hold for review, never mark approved.')
   result={'plate_id':row['plate_id'],'status':'RENDERED_REVIEW_REQUIRED','sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'dimensions':[w,h],'output':str(target)};done+=1
  except Exception as exc:
   result={'plate_id':row['plate_id'],'status':'FAILED_PAUSE_QUEUE','error':str(exc)}
  with log.open('a',encoding='utf-8') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n')
  print(json.dumps(result,ensure_ascii=False))
  if result['status']!='RENDERED_REVIEW_REQUIRED':
   print('Paused queue after failure; no bulk credit loss',file=sys.stderr);break
  time.sleep(max(args.cooldown,0))
 print(f'Generated for review {done} images; APPROVED 0 (human QC required)')
if __name__=='__main__':main()