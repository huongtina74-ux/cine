#!/usr/bin/env python3
"""Compile location/prop work orders from authoritative CINE multi-view manifests.
No invented APPROVED statuses, images, output files, or provider API claims.
"""
import csv, json, hashlib, pathlib, re
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parent.parent
SNAP=ROOT.parent/'cine-bellfern-location-multiview-lock'/'registry'; OUT=ROOT/'queue'

VIEWS={
 'MASTER_WIDE':'Use one wide camera establishing the entire actual space. Keep all architectural anchors readable.',
 'FORWARD':'Use a camera looking forward toward the principal functional anchor from the documented entrance.',
 'REVERSE_TRUE':'Place the camera physically on the far side, pointing opposite to FORWARD, preserving door, window, and room topology; NEVER mirror an existing image.',
 'LEFT_3_4':'Use a real camera at the front-left three-quarter position looking diagonally into the same space.',
 'RIGHT_3_4':'Use a real camera at the front-right three-quarter position looking diagonally into the same space.',
 'DETAIL_ANCHORS':'One detailed close-up composition with recognizable permanent architectural and prop anchors, not multiple inset panels.',
 'PLAN_TOP':'One clean top-down physical plan/roofless spatial view with correct entrances, windows, and circulation; no labels, grids, lettering, or captions.',
 'FRONT':'One frontal orthographic-like identity view, keep true dimensions, silhouette, and material.',
 'THREE_QUARTER_LEFT':'One real three-quarter view from the prop front-left, consistent handedness.',
 'SIDE_RIGHT':'One true right side view, consistent shape and size.',
 'BACK':'One genuine back view revealing the same real object; not a flipped front.',
 'TOP':'One direct true top-down view; no exploded diagrams or labels.',
 'MACRO_DETAIL':'One close-up of the signature physical material/hardware only, isolated as one single photo.',
 'PLACED_IN_SCENE':'One view of this exact prop occupying its canonical location at plausible size relative to fixed set landmarks, no cast characters.'
}

VISUAL='Premium photoreal-material stylized 3D CGI for Bell & Leaf, detailed physically credible construction and surfaces, natural color science, neutral D55 daylight reference about 5500K when naturally lit, neutral whites and greys, no global yellow/amber/orange cast, no unnatural orange rim lighting, 50mm full-frame perspective as a starting point with enough depth of field to keep physical anchors crisp, soft realistic shadows, appealing restrained colors.'
NEG='Output exactly ONE native full-frame 16:9 image as a single camera view, not a concept board, collage, split-screen, contact sheet, floor-plan montage, title, graphic panel, page layout, subtitle, caption, watermark, border, or side-fill; no added random people, invented magical bells, or duplicated objects.'

def clean(s):return re.sub(r'\s+',' ',str(s or '')).strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(name):
 with (SNAP/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_lines(path, items):
 with path.open('w',encoding='utf-8',newline='\n') as f:f.write('\n\n'.join(x['prompt'] for x in items)+'\n')
def main():
 reg=json.loads((SNAP/'CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json').read_text('utf-8'))
 rooms=rows('LOCATION_MULTIVIEW_MANIFEST.csv');props=rows('PROP_MULTIVIEW_MANIFEST.csv')
 assert len(rooms)==483 and len(props)==756 and len(reg['sites'])==12 and len(reg['spaces'])==69 and len(reg['props'])==108
 site={x['site_id']:x for x in reg['sites']}; space={x['space_id']:x for x in reg['spaces']}; prop={x['prop_id']:x for x in reg['props']}
 work=[]
 for r in rooms:
  assert r['view'] in VIEWS, r['view']
  s=site[r['site_id']];z=space[r['space_id']]
  prompt=f"PLATE_ID {r['plate_id']}. PRODUCTION REFERENCE STILL REQUEST, NOT AN APPROVED CANON IMAGE. Location {clean(s['name'])}, exact space {clean(z['name'])}; building architecture {clean(s['architecture'])}; material specification {clean(s['materials_palette'])}; site geography and spatial topology {clean(s['topology_draft'])}; space placement {clean(z['placement'])}; immovable spatial anchors {clean(z['fixed_visual_anchors'])}; forbidden changes {clean(z['forbidden_change'])}; frame {r['view']}: {VIEWS[r['view']]} {VISUAL} {NEG} No characters in reference plates."
  work.append({'plate_id':r['plate_id'],'type':'location','site_id':r['site_id'],'space_id':r['space_id'],'view':r['view'],'prompt':clean(prompt),'output_relpath':f"output/location/{r['site_id']}/{r['space_id']}/{r['plate_id']}.png",'status':'PENDING_NOT_GENERATED','origin_manifest':'LOCATION_MULTIVIEW_MANIFEST.csv','reference_status':'TOPOLOGY_AND_SOURCE_NOT_APPROVED','requires_human_QC':True})
 for r in props:
  assert r['view'] in VIEWS,r['view']
  s=site[r['site_id']];p=prop[r['prop_id']]
  z=space.get((r.get('default_space_id') or r.get('space_id')),{})
  prompt=f"PLATE_ID {r['plate_id']}. SINGLE ORIGINAL HERO PROP REFERENCE STILL REQUEST, NOT AN APPROVED CANON IMAGE. Prop {clean(p['name'])}, physical identity {clean(p['design_anchor'])}, immutable rule {clean(p['immutable_rule'])}, permitted states {clean(p['states'])}, size rule {clean((r.get('dimensions') or r.get('size_cm') or p['dimensions']))}; belongs to location {clean(s['name'])}, space {clean(z.get('name',(r.get('default_space_id') or r.get('space_id'))))}, canonical site materials {clean(s['materials_palette'])}. View {r['view']}: {VIEWS[r['view']]} {VISUAL} {NEG} One prop only unless physical room landmarks are necessary for PLACED_IN_SCENE; not a model sheet or text-labelled comparison."
  work.append({'plate_id':r['plate_id'],'type':'prop','site_id':r['site_id'],'space_id':(r.get('default_space_id') or r.get('space_id')),'prop_id':r['prop_id'],'view':r['view'],'prompt':clean(prompt),'output_relpath':f"output/prop/{r['site_id']}/{r['prop_id']}/{r['plate_id']}.png",'status':'PENDING_NOT_GENERATED','origin_manifest':'PROP_MULTIVIEW_MANIFEST.csv','reference_status':'SOURCE_PROP_NOT_APPROVED','requires_human_QC':True})
 assert len(work)==1239 and len({x['plate_id'] for x in work})==1239
 for x in work: assert '\n' not in x['prompt']
 OUT.mkdir(exist_ok=True)
 with (OUT/'ALL_1239_ASSET_WORK_ORDERS.jsonl').open('w',encoding='utf-8') as f:
  for x in work:f.write(json.dumps(x,ensure_ascii=False)+'\n')
 write_lines(OUT/'FLOW_483_LOCATION_ONE_LINE_BLANK.txt',work[:483]);write_lines(OUT/'FLOW_756_PROP_ONE_LINE_BLANK.txt',work[483:])
 counts={t:dict(Counter(x['site_id'] for x in work if x['type']==t)) for t in ('location','prop')}
 report={'generator':'cine.a2.fixed10s.location_prop_queue.r2','actual_new_images_created_by_this_generator':0,'expected_images':1239,'location_slots':483,'prop_slots':756,'all_slots_pending_render':1239,'required_human_review':True,'counts':counts,'registry_sha256':{a:sha(SNAP/a) for a in ['CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json','LOCATION_MULTIVIEW_MANIFEST.csv','PROP_MULTIVIEW_MANIFEST.csv']},'overlap_policy':'Only visible characters in final shot; no character refs for pure location/prop plates','dependency':'Location and prop multiview sources must be human approved before shots are production-ready'}
 (OUT/'COVERAGE_AND_PROVENANCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'total':len(work),'room':len(rooms),'props':len(props),'counts':counts,'prompt_example':work[0]['prompt'][:100]},ensure_ascii=False))
if __name__=='__main__':main()