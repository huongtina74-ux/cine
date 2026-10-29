#!/usr/bin/env python3
"""Install the Bell & Leaf user-source character anchor pack into a local CINE repo.

No newly generated Muse images are approved. Never change existing original assets.
"""
import argparse,hashlib,json,pathlib,shutil,sys,tempfile,zipfile,os,stat

def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()

def load_pack(arg,workspace):
    if arg.is_file() and arg.suffix=='.zip':
        with zipfile.ZipFile(arg) as z:
            for member in z.infolist():
                p=pathlib.PurePosixPath(member.filename)
                if p.is_absolute() or '..' in p.parts or (member.external_attr>>16)&0o170000==stat.S_IFLNK:raise ValueError('Unsafe ZIP member '+member.filename)
            z.extractall(workspace)
        return next(iter(pathlib.Path(workspace).rglob('metadata/CHARACTER_CURRENT_SOURCE_LOCK.json'))).parent.parent
    if arg.is_dir():return arg
    raise ValueError('Pack must be ZIP or directory')

def install(cine_repo,pack,verify_only=False):
    cine_repo=cine_repo.resolve()
    if not (cine_repo/'.git').exists():raise ValueError('Require an existing CINE Git worktree')
    with tempfile.TemporaryDirectory() as tmp:
        base=load_pack(pack,pathlib.Path(tmp))
        registry=json.loads((base/'metadata/CHARACTER_CURRENT_SOURCE_LOCK.json').read_text())
        tags=['bo','me','juno','Lia','bubu','bix','ongngoai','bangoai','ongnoi','banoi']
        if list(registry['characters'])!=tags:raise ValueError('Canonical tag order invalid')
        # Validate EVERY intended identity asset before any modification.
        checked=[]
        for tag in tags:
            entry=registry['characters'][tag]
            for part in [entry['locked_identity_original'],entry['source_master_crop']]+entry.get('mandatory_visual_cues',[]):
                f=base/part['path'] if 'path' in part else base/part['file']
                if not f.is_file() or digest(f)!=part['sha256']:raise ValueError('Missing/modified original or crop '+str(f))
                checked.append(part)
            if entry['approved_new_ai_images']:raise ValueError('Generated draft should never be auto-approved')
        print('PASS',len(checked),'exact user-source hash assets verified')
        target=cine_repo/'assets/canon/character_refs/slow_english_a2/bell_leaf/v1_2_user_source'
        if verify_only:
            print('VERIFY_ONLY: would install',target)
            return
        if target.exists():
            for part in checked:
                f=target/(part.get('path') or part.get('file'))
                if not f.exists() or digest(f)!=part['sha256']:raise ValueError('Existing canonical asset differs; installation refused')
            print('Already installed. Existing immutable files unchanged.');return
        target.parent.mkdir(parents=True,exist_ok=True)
        staging=target.with_name(target.name+'.partial_'+str(os.getpid()))
        if staging.exists():raise ValueError('Previous partial installation exists; abort')
        try:
            staging.mkdir()
            for sub in ['assets/originals','assets/masters','metadata','reports']:
                if (base/sub).exists():shutil.copytree(base/sub,staging/sub)
            staging.rename(target)
        finally:
            if staging.exists():shutil.rmtree(staging)
        print('Installed SOURCE_CANON anchors:',str(target))
        print('New Muse images approved: 0. Character visuals are locked to ORIGINAL SOURCE only.')
        print('Next: integrate verified source refs with runtime resolver; approve shot-specific generated views separately.')

if __name__=='__main__':
    pa=argparse.ArgumentParser()
    pa.add_argument('--cine-repo',required=True,type=pathlib.Path)
    pa.add_argument('--pack',required=True,type=pathlib.Path)
    pa.add_argument('--verify-only',action='store_true')
    a=pa.parse_args()
    install(a.cine_repo,a.pack,a.verify_only)