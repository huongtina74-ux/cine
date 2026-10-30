#!/usr/bin/env python3
"""CINE Bell & Leaf source anchor resolver.

This returns verified local source references for prompt/image *preparation*,
NOT production approval of generated imagery. The Flow/Muse connector must upload
selected local images and pass real media IDs, never invent them.
"""
import argparse, hashlib, json, pathlib, sys

TAGS = ('bo','me','juno','Lia','bubu','bix','ongngoai','bangoai','ongnoi','banoi')
class CanonSourceError(Exception): pass

def sha256(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def resolve(root, active_tags, include_original=False):
    root=pathlib.Path(root).resolve()
    if not isinstance(active_tags,list):raise CanonSourceError('activeCharacterTags must be an explicit list')
    if len(set(active_tags))!=len(active_tags):raise CanonSourceError('Duplicate tags in shot')
    if any(x not in TAGS for x in active_tags):raise CanonSourceError('Unknown character tag')
    if not (root/'metadata/CHARACTER_CURRENT_SOURCE_LOCK.json').is_file():raise CanonSourceError('SOURCE_LOCK_NOT_INSTALLED')
    registry=json.loads((root/'metadata/CHARACTER_CURRENT_SOURCE_LOCK.json').read_text())
    out=[]
    for tag in active_tags:
        character=registry['characters'][tag]
        # Bubu's small front crop is not suitable alone: prefer original hero region plus tail sparkles.
        refs=[character['source_master_crop']]
        if tag=='bubu':
            cues={x['purpose']:x for x in character['mandatory_visual_cues']}
            refs=[cues['HERO_FACE_AND_BODY_SOURCE'],cues['TAIL_SPARKLE_DETAIL_SOURCE']]
        if include_original:refs.insert(0,character['locked_identity_original'])
        for r in refs:
            relative=r.get('path') or r.get('file')
            target=(root/relative).resolve()
            if not target.is_relative_to(root):raise CanonSourceError('REF_PATH_OUTSIDE_CANON_ROOT')
            if not target.is_file() or sha256(target)!=r['sha256']:raise CanonSourceError('MISSING_OR_MODIFIED_SOURCE:'+relative)
            out.append({'tag':tag,'local_path':str(target),'sha256':r['sha256'],'provenance':'PIXEL_IDENTICAL_TO_USER_ORIGINAL','attachment_media_id':None,'requires_flow_or_muse_upload':True,'approval_scope':'SOURCE_IDENTITY_ONLY'})
    return {'activeCharacterTags':active_tags,'reference_count':len(out),'character_references':out,'generated_new_image_qc':'NOT_APPROVED','location_references':'RESOLVE_SEPARATELY_BY_LOCATION_LOCK'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=pathlib.Path,required=True)
    p.add_argument('--tags',nargs='*',default=[])
    p.add_argument('--include-original',action='store_true')
    a=p.parse_args()
    try:print(json.dumps(resolve(a.root,a.tags,a.include_original),indent=2))
    except CanonSourceError as e:print(str(e),file=sys.stderr);sys.exit(2)