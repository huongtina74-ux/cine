"""Light lab: one static two-shot of Bin and Zu, 4 lighting set-ups, 24 frames each (instant switches).

  A  0-23   default (sun only, preset look)
  B 24-47   3-point: sun as key + warm fill point light near camera + cool rim point light behind + subsurface on skin
  C 48-71   golden hour: low warm sun, orange sky, rim light
  D 72-95   night: dark indigo sun/ambient (not the built-in night), warm lamp point light at the faces

Sources: [D: Q7H78ANxC94, Hj4a1avlL9o, EW0STx0lxKw, TbTvGzYP5N8, WC2gTLI34kc] via reports/research/mineimator_study/D_*.md.
Mine-imator facts from the 2.0.2 source: project.render_settings must be "" (Custom) or a preset .mirender is
re-loaded on open and overrides the file's render block; background keys are BG_*; lights are 'pointlight' timelines
with LIGHT_COLOR ('#RRGGBB'), LIGHT_STRENGTH, LIGHT_RANGE (default 250), LIGHT_SIZE, LIGHT_FADE_SIZE.
Usage: python lightlab.py WORKDIR   (WORKDIR already holds proj/ from prep.py + build.py)
"""
import copy
import json
import os
import random
import sys

random.seed(11)
work = sys.argv[1]
src = os.path.join(work, 'proj', 'BinBo MI thu 02.miproject')
d = json.load(open(src))
tl = {t['id']: t for t in d['timelines']}
by_name = {t['name']: t for t in d['timelines'] if t.get('name')}
cam = next(t for t in d['timelines'] if t['type'] == 'camera')


def nid():
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(16))


res_by_file = {r['filename']: r['id'] for r in d['resources']}
for t in d['timelines']:
    t['keyframes'] = {}


def key(t, f, tr='instant', **v):
    k = t['keyframes'].setdefault(str(f), {})
    k.update(v)
    k['TRANSITION'] = tr


def char(name):
    return by_name[name.capitalize()]


def part(name, p):
    c = char(name)
    return next(tl[i] for i in c['parts'] if tl[i].get('model_part_name') == p)


# poses: Bin and Zu stand side by side facing the camera (-Y), Bo parked far away
key(char('bin'), 0, POS_X=10, POS_Y=0, ROT_Z=200)
key(char('zu'), 0, POS_X=-8, POS_Y=-2, ROT_Z=165, SCA_X=.6, SCA_Y=.6, SCA_Z=.6)
key(part('zu', 'head'), 0, SCA_X=1.25, SCA_Y=1.25, SCA_Z=1.25, ROT_X=-4)
key(char('bo'), 0, POS_X=600)
key(part('bin', 'right_arm'), 0, ROT_X=-20, ROT_Z=-8)
key(part('bin', 'left_arm'), 0, ROT_X=8, ROT_Z=6)
for n in ('bin', 'zu'):
    for layer, dy, tex in (('eyes', 4.02, 'eyes_open'), ('pupils', 4.035, 'pupils_normal'),
                           ('brows', 4.045, 'brows_raised'), ('mouth', 4.025, 'mouth_smile')):
        key(by_name[f'{n}_{layer}'], 0, TEXTURE_OBJ=res_by_file[f'face/{n}_{tex}.png'], POS_Y=dy, SCA_X=.5, SCA_Y=.5, SCA_Z=.5)

# static camera: medium two-shot, faces at ~ z 26 (Bin) / ~ z 15 (Zu)
key(cam, 0, 'linear', POS_X=4, POS_Y=-62, POS_Z=22, ROT_X=1.5, ROT_Z=0, CAM_FOV=34)
key(cam, 119, 'linear', POS_X=4, POS_Y=-62, POS_Z=22, ROT_X=1.5, ROT_Z=0, CAM_FOV=34)

# subsurface on the two characters (rim/soft skin) - inherited by body parts
for n in ('bin', 'zu'):
    c = char(n)
    key(c, 24, SUBSURFACE=0.6)
    key(c, 0, SUBSURFACE=0)
    for f in (48, 72, 96):
        key(c, f, SUBSURFACE=0.6)
    # keep the pose values on every key (Mine-imator stores only non-default values per key)
    base = {k: v for k, v in c['keyframes']['0'].items() if k not in ('TRANSITION', 'SUBSURFACE')}
    for f in ('24', '48', '72', '96'):
        c['keyframes'][f].update(base)

base_tl = {k: v for k, v in cam.items() if k != 'keyframes'}


def new_tl(type_, name, idx):
    t = copy.deepcopy(base_tl)
    t.update(id=nid(), type=type_, name=name, temp='null', keyframes={}, parent='root', parent_tree_index=idx)
    d['timelines'].append(t)
    return t


roots = [t for t in d['timelines'] if t['parent'] == 'root']
nxt = max(t['parent_tree_index'] for t in roots) + 1
bg = new_tl('background', 'Environment', nxt)
fill = new_tl('pointlight', 'Fill light', nxt + 1)
rim = new_tl('pointlight', 'Rim light', nxt + 2)
lamp = new_tl('pointlight', 'Night lamp', nxt + 3)

# v2 (after lab v1): BG_SKY_TIME is the sun elevation offset: 0 = zenith, -45 = 45 deg, -78 = low golden sun (SOURCE background_sky_update_sun)
BG = {
 0:  dict(BG_SKY_TIME=-45, BG_SKY_ROTATION=0, BG_SUNLIGHT_STRENGTH=1, BG_SUNLIGHT_COLOR='#FFF7E4', BG_AMBIENT_COLOR='#66708C', BG_SKY_COLOR='#78A7FF'),
 24: dict(BG_SKY_TIME=-45, BG_SKY_ROTATION=0, BG_SUNLIGHT_STRENGTH=1.5, BG_SUNLIGHT_COLOR='#FFE9C4', BG_AMBIENT_COLOR='#6F7FA0', BG_SKY_COLOR='#78A7FF'),
 48: dict(BG_SKY_TIME=-76, BG_SKY_ROTATION=0, BG_SUNLIGHT_STRENGTH=1.6, BG_SUNLIGHT_COLOR='#FF9A4A', BG_AMBIENT_COLOR='#6B5A80', BG_SKY_COLOR='#F2905F',
          BG_FOG_CUSTOM_COLOR=True, BG_FOG_COLOR='#F7B48A', BG_SKY_CLOUDS_COLOR='#FFD2B0'),
 72: dict(BG_SKY_TIME=-76, BG_SKY_ROTATION=180, BG_SUNLIGHT_STRENGTH=1.6, BG_SUNLIGHT_COLOR='#FF9A4A', BG_AMBIENT_COLOR='#6B5A80', BG_SKY_COLOR='#F2905F',
          BG_FOG_CUSTOM_COLOR=True, BG_FOG_COLOR='#F7B48A', BG_SKY_CLOUDS_COLOR='#FFD2B0'),
 96: dict(BG_SKY_TIME=-45, BG_SKY_ROTATION=0, BG_SUNLIGHT_STRENGTH=0.25, BG_SUNLIGHT_COLOR='#3B4C9B', BG_AMBIENT_COLOR='#10152B', BG_SKY_COLOR='#0B1130',
          BG_FOG_CUSTOM_COLOR=True, BG_FOG_COLOR='#0B1022', BG_SKY_CLOUDS_COLOR='#2A3150'),
}
prev = {}
for f in sorted(BG):
    v = dict(prev); v.update(BG[f]); prev = v
    v.setdefault('BG_FOG_CUSTOM_COLOR', False)
    key(bg, f, **v)
# fill near camera; rim behind (stronger/closer than v1, where it was invisible); lamp only at night
for f, s in ((0, 0), (24, 0.6), (48, 0.5), (72, 0.7), (96, 0)):
    key(fill, f, POS_X=-20, POS_Y=-40, POS_Z=30, LIGHT_COLOR='#FFE2C0', LIGHT_STRENGTH=s, LIGHT_RANGE=140, LIGHT_SIZE=6)
for f, s, col in ((0, 0, '#BFD8FF'), (24, 3.0, '#CFE2FF'), (48, 2.5, '#FFC27A'), (72, 2.5, '#FFC27A'), (96, 1.5, '#6F8CFF')):
    key(rim, f, POS_X=2, POS_Y=14, POS_Z=34, LIGHT_COLOR=col, LIGHT_STRENGTH=s, LIGHT_RANGE=60, LIGHT_SIZE=8)
for f, s in ((0, 0), (24, 0), (48, 0), (72, 0), (96, 2.2)):
    key(lamp, f, POS_X=-26, POS_Y=-14, POS_Z=18, LIGHT_COLOR='#FFB24D', LIGHT_STRENGTH=s, LIGHT_RANGE=120, LIGHT_SIZE=3)

# render: Custom (not a preset), more samples, subsurface on
pr = d['project']
pr['render_settings'] = ''
pr['name'] = 'BinBo light lab'
pr['timeline'].update(marker=0, region_start=0, region_end=119)
r = d['render']
r.update(render_samples=48, render_subsurface_samples=16, render_ssao=True, render_shadows=True,
         render_shadows_point_buffer_size=512)
out = os.path.join(work, 'proj', 'BinBo light lab.miproject')
d['project']['name'] = 'BinBo light lab v2'
json.dump(d, open(out, 'w'), indent=1)
print('LIGHTLAB_OK::timelines=%d::setups=5::frames=120' % len(d['timelines']))
