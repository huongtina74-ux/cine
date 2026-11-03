"""Mine-imator 2.0.2 test scene 03 (16 s, no dialogue): "Zu smells pizza" - an expression + camera reel.

Built after a frame-by-frame look at the competitor benchmark (reports/research/2026-11-03_expression_camera_study.md):
the gaps vs our scene 02 were flat faces, upright heads, small poses, eye-level static cameras and an empty set.
New here (each one is a reusable helper):
  faces   heart / sparkle / squeeze / popped eyes, drool / scream / wavy / chew mouths (binbo_thu02/faces.py)
  fx      blush layer, cheeks that puff (head widens per chew), sweat drop that slides, "!" pop-up, floating hearts, crumbs, steam
  acting  head roll (ROT_Y) tilt, squash & stretch on head and body, anticipation crouch -> jump arc -> landing squash,
          brows that jump off the face
  camera  low angle, worm's-eye, high angle, over-the-shoulder, crash zoom (FOV), push-in / pull-out, dutch (ROT_Y),
          shake (CAM_SHAKE), depth of field (CAM_DOF), vignette
  set     floor / walls / table / bookshelf / flower pot from Mine-imator's own blocks (block templates with repeat)
Usage: python build.py WORKDIR   (after prep.py WORKDIR)
"""
import copy
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'binbo_thu02'))
import faces  # noqa: E402

work = sys.argv[1] if len(sys.argv) > 1 else HERE
os.chdir(work)
random.seed(3)
d = json.load(open(os.path.join(HERE, '..', 'binbo_thu02', 'template.miproject')))
FPS, END = 24, 384
NAME = 'BinBo MI thu 03'


def nid():
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(16))


# ---------------- resources ----------------
res, RID = [], {}
for n in ('bin', 'zu'):
    i = nid(); RID[n + '_skin'] = i
    res.append({'id': i, 'type': 'skin', 'filename': f'skins/{n}_faceless.png', 'player_skin': True, 'material_format': 0})
for sub in ('face', 'fx'):
    for f in sorted(os.listdir(f'proj/{sub}')):
        if sub == 'face' and not (f.startswith('bin_') or f.startswith('zu_')):
            continue
        i = nid(); RID[f[:-4]] = i
        res.append({'id': i, 'type': 'texture', 'filename': f'{sub}/{f}', 'material_format': 0})

# ---------------- templates ----------------
steve_t = [t for t in d['templates'] if t['model']['name'] == 'human'][0]
temps, TID = [], {}
for n in ('bin', 'zu'):
    t = copy.deepcopy(steve_t); t.update(id=nid(), model_tex=RID[n + '_skin'], name=n.capitalize()); temps.append(t); TID[n] = t['id']


def shape_t(kind, tex, name, face_camera=False):
    t = {'id': nid(), 'type': kind, 'name': name,
         'shape': {'tex': RID[tex], 'tex_mapped': False, 'tex_hoffset': 0, 'tex_voffset': 0, 'tex_hrepeat': 1, 'tex_vrepeat': 1,
                   'tex_hmirror': False, 'tex_vmirror': False, 'closed': True, 'invert': False, 'detail': 32, 'face_camera': face_camera}}
    temps.append(t)
    return t['id']


SURF = shape_t('surface', 'bin_eyes_open', 'face layer')
BB = {k: shape_t('surface', 'fx_' + k, 'fx ' + k, face_camera=True) for k in ('sparkle', 'steam')}   # world-level only: billboards ignore a parent (RENDER thu03)
SWEAT = shape_t('surface', 'fx_sweat', 'sweat')
PIZZA = shape_t('surface', 'fx_pizza', 'pizza')


def block_t(name, state, rep, label):
    t = {'id': nid(), 'type': 'block', 'name': label,
         'block': {'name': name, 'state': state, 'tex': 'default', 'tex_material': 'default', 'tex_normal': 'default',
                   'randomize': False, 'repeat_enable': True, 'repeat': [rep[0], rep[2], rep[1]]}}   # JSON point3D is [x, up, y] (SOURCE value_get_point3D)
    temps.append(t)
    return t['id']


# ---------------- timelines ----------------
tls = d['timelines']
steve = [t for t in tls if t.get('name') == 'Steve'][0]
parts = {t['id']: t for t in tls if t.get('part_of') == steve['id']}
cam = copy.deepcopy([t for t in tls if t['type'] == 'camera'][0]); cam['keyframes'] = {}
BASE = copy.deepcopy(steve); [BASE.pop(k, None) for k in ('parts', 'lock_bend')]
new, P = [], {}
ROOT_IDX = [0]


def mk(kind, name, temp, parent='root', **extra):
    t = copy.deepcopy(BASE)
    t.update(id=nid(), type=kind, name=name, temp=temp, keyframes={}, parent=parent, **extra)
    if parent == 'root':
        ROOT_IDX[0] += 1; t['parent_tree_index'] = ROOT_IDX[0]
    new.append(t)
    return t


for n in ('bin', 'zu'):
    c = copy.deepcopy(steve); c.update(id=nid(), name=n.capitalize(), temp=TID[n], keyframes={})
    m = {pid: nid() for pid in steve['parts']}
    c['parts'] = [m[p] for p in steve['parts']]
    ROOT_IDX[0] += 1; c['parent_tree_index'] = ROOT_IDX[0]
    new.append(c); P[n] = {'char': c}
    for pid in steve['parts']:
        b = copy.deepcopy(parts[pid]); b.update(id=m[pid], temp=TID[n], part_of=c['id'], keyframes={})
        b['parent'] = m.get(b['parent'], c['id']) if b['parent'] != steve['id'] else c['id']
        new.append(b); P[n][b['model_part_name']] = b
    head = P[n]['head']['id']
    for li, (layer, dy) in enumerate((('eyes', 4.02), ('pupils', 4.035), ('brows', 4.045), ('mouth', 4.025), ('blush', 4.05))):
        s_ = mk('surface', f'{n}_{layer}', SURF, parent=head, parent_tree_index=li + 1, shadows=False, ssao=False)
        s_['inherit'] = dict(s_['inherit'], texture=False, alpha=True, visibility=True, scale=True, position=True, rotation=True)
        P[n][layer] = s_; P[n][layer + '_y'] = dy
    P[n]['sweat'] = mk('surface', f'{n}_sweat', SWEAT, parent=head, parent_tree_index=6, shadows=False, ssao=False)
    P[n]['mark'] = mk('surface', f'{n}_mark', SURF, parent=head, parent_tree_index=7, shadows=False, ssao=False)
    P[n]['mark']['inherit'] = dict(P[n]['mark']['inherit'], texture=False)
# floating hearts (Zu), crumbs (Zu eating), steam (pizza)
ONHEAD = {k: shape_t('surface', 'fx_' + k, 'fx ' + k + ' (head)') for k in ('heart', 'crumb')}
HEARTS = [mk('surface', f'heart_{i}', ONHEAD['heart'], parent=P['zu']['head']['id'], parent_tree_index=9 + i, shadows=False, ssao=False) for i in range(4)]
CRUMBS = [mk('surface', f'crumb_{i}', ONHEAD['crumb'], parent=P['zu']['head']['id'], parent_tree_index=13 + i, shadows=False, ssao=False) for i in range(6)]
STEAM = [mk('surface', f'steam_{i}', BB['steam'], shadows=False, ssao=False) for i in range(3)]
SPARK = [mk('surface', f'sparkle_{i}', BB['sparkle'], shadows=False, ssao=False) for i in range(3)]
PZ = mk('surface', 'Pizza', PIZZA, shadows=True)

# ---------------- set (Mine-imator's own blocks; 16 units = 1 block, timeline position = block corner) ----------------
SET = [  # (block, state, (blocks along X, along Y, high), label), corner position (x, y, z)
    (('planks', {'variant': 'oak'}, (14, 10, 1), 'Floor'), (-112, -80, -16)),
    (('grass_block', {}, (40, 40, 1), 'Yard'), (-320, -320, -16.5)),   # replaces the built-in ground (it z-fought the floor)
    (('planks', {'variant': 'birch'}, (14, 1, 4), 'Back wall'), (-112, 64, 0)),
    (('planks', {'variant': 'birch'}, (1, 9, 4), 'Side wall'), (-112, -80, 0)),
    (('planks', {'variant': 'dark_oak'}, (2, 1, 1), 'Table'), (-16, 8, 0)),
    (('bookshelf', {}, (2, 1, 2), 'Bookshelf'), (48, 48, 0)),
    (('flower_pot', {'contents': 'poppy'}, (1, 1, 1), 'Flower pot'), (-16, 8, 16)),
    (('carpet', {'color': 'red'}, (3, 2, 1), 'Rug'), (24, -40, 0)),
]
SETTL = []
for (bn, st, rep, label), pos in SET:
    t = mk('block', label, block_t(bn, st, rep, label))
    # RENDER-fit (thu03 f383, 67 px total error vs 390 for corner origin): the repeated box is centred on the
    # timeline position in X and Y and rises from it in Z, so convert our min-corner layout to the centre
    t['keyframes'] = {'0': {'POS_X': pos[0] + rep[0] * 8, 'POS_Y': pos[1] + rep[1] * 8, 'POS_Z': pos[2], 'TRANSITION': 'linear'}}
    SETTL.append(t)

# ---------------- keyframe helper (state carried forward; only non-default values are written) ----------------
EV = {}
DEF1 = {'SCA_X', 'SCA_Y', 'SCA_Z', 'ALPHA', 'CAM_FOV'}


def K(tl, f, tr='easeinoutquad', **v):
    e = EV.setdefault(tl['id'], (tl, {}))[1].setdefault(int(f), [{}, tr])
    e[0].update(v); e[1] = tr


def keep(k, v):
    if v is None:
        return False
    if isinstance(v, bool):
        return (v is False) if k == 'VISIBLE' else v
    if isinstance(v, (int, float)) and v == 0:
        return k in DEF1
    return True


def flush():
    for tid, (tl, ev) in EV.items():
        state, out = {}, {}
        for f in sorted(ev):
            vals, tr = ev[f]; state.update(vals)
            kf = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in state.items() if keep(k, v)}
            kf['TRANSITION'] = tr; out[str(f)] = kf
        tl['keyframes'] = out


B, Z = P['bin'], P['zu']
ZS = .6           # Zu body scale
ZH = 1.25         # Zu head scale


def zsca(f, tr, sx=1.0, sz=1.0, **v):
    """Zu squash & stretch around his base scale (volume roughly kept: sx*sx*sz ~ 1)."""
    K(Z['char'], f, tr, SCA_X=ZS * sx, SCA_Y=ZS * sx, SCA_Z=ZS * sz, **v)


# ================= BLOCKING =================
# Zu on the floor facing the table (ROT_Z 50 -> direction (sin50, cos50)); Bin by the rug looking left (-X)
K(Z['char'], 0, 'linear', POS_X=-36, POS_Y=-14, POS_Z=0, ROT_Z=50)
zsca(0, 'linear')
K(Z['head'], 0, 'linear', SCA_X=ZH, SCA_Y=ZH, SCA_Z=ZH, ROT_X=-6)
K(B['char'], 0, 'linear', POS_X=40, POS_Y=-6, POS_Z=0, ROT_Z=-115)
# S1 sniff sniff (head up-down), then the smell hits: head tilts (roll) and sways
for f, rx in ((6, -14), (10, -4), (16, -16), (20, -4), (26, -18), (30, -6)):
    K(Z['head'], f, 'easeoutquad', ROT_X=rx)
K(Z['head'], 40, 'easeoutback', ROT_X=-10, ROT_Y=14)
for i, f in enumerate(range(52, 108, 14)):
    K(Z['head'], f, 'easeinoutsine', ROT_Y=-12 if i % 2 == 0 else 14)
K(Z['head'], 108, 'easeinoutsine', ROT_Y=0, ROT_X=-4)
for arm, s in (('right_arm', 1), ('left_arm', -1)):           # hands clasped under the chin when in love
    K(Z[arm], 38, 'easeinoutquad', ROT_X=0, ROT_Z=0)
    K(Z[arm], 46, 'easeoutback', ROT_X=-52, ROT_Z=-20 * s)
    K(Z[arm], 160, 'easeinoutquad', ROT_X=-52, ROT_Z=-20 * s)
    K(Z[arm], 168, 'easeinoutquad', ROT_X=-20, ROT_Z=0)
# S3 Bin's double take: arms fly up, head stretches then squashes and settles (easeoutelastic)
K(B['head'], 108, 'easeinoutquad', ROT_X=4, ROT_Y=0, SCA_X=1, SCA_Y=1, SCA_Z=1)
K(B['head'], 116, 'easeinoutquad', ROT_X=8)                     # anticipation: dip
K(B['head'], 119, 'easeoutquad', ROT_X=-10, SCA_X=.86, SCA_Y=.86, SCA_Z=1.32)   # stretch
K(B['head'], 123, 'easeoutquad', SCA_X=1.1, SCA_Y=1.1, SCA_Z=.88)               # squash
K(B['head'], 134, 'easeoutelastic', ROT_X=-4, SCA_X=1, SCA_Y=1, SCA_Z=1)
K(B['body'], 116, 'easeinoutquad', ROT_X=4); K(B['body'], 120, 'easeoutback', ROT_X=-8); K(B['body'], 134, 'easeoutquad', ROT_X=0)
for arm, s in (('right_arm', 1), ('left_arm', -1)):
    K(B[arm], 116, 'easeinoutquad', ROT_X=6, ROT_Z=0)
    K(B[arm], 120, 'easeoutback', ROT_X=-172, ROT_Z=-32 * s)
    K(B[arm], 150, 'easeinoutquad', ROT_X=-165, ROT_Z=-28 * s)
    K(B[arm], 164, 'easeinoutquad', ROT_X=-15, ROT_Z=6 * s)
K(B['char'], 116, 'easeinoutquad', POS_Z=0); K(B['char'], 120, 'easeoutquad', POS_Z=5); K(B['char'], 128, 'easeinquad', POS_Z=0)
# S4 Zu: anticipation crouch -> stretch launch -> arc -> landing squash on the table top -> settle
zsca(168, 'easeinoutquad')
zsca(180, 'easeoutquad', sx=1.18, sz=.72, POS_Z=-1.5)              # crouch (squash)
zsca(184, 'easeoutquad', sx=.86, sz=1.3, POS_Z=4)                   # launch (stretch)
def zarc(u):                                                        # floor (4) -> peak ~40 -> table top (16)
    return 4 + 130.8 * u - 118.8 * u * u


for f in range(184, 207, 2):                                        # parabola from floor to table top
    u = (f - 184) / 22
    K(Z['char'], f, 'linear', POS_X=-36 + 36 * u, POS_Y=-14 + 36 * u, POS_Z=zarc(u), ROT_Z=50 + 130 * u)
zsca(206, 'easeoutquad', sx=1.22, sz=.7, POS_X=0, POS_Y=22, POS_Z=16, ROT_Z=180)      # landing squash, now facing camera side
zsca(214, 'easeoutelastic', POS_Z=16)
for leg in ('right_leg', 'left_leg'):
    K(Z[leg], 180, 'easeoutquad', ROT_X=0); K(Z[leg], 188, 'easeoutquad', ROT_X=-70); K(Z[leg], 204, 'easeinquad', ROT_X=0)
for arm, s in (('right_arm', 1), ('left_arm', -1)):
    K(Z[arm], 180, 'easeinoutquad', ROT_X=30, ROT_Z=10 * s)
    K(Z[arm], 186, 'easeoutback', ROT_X=-170, ROT_Z=20 * s)
    K(Z[arm], 206, 'easeinoutquad', ROT_X=-120, ROT_Z=40 * s)
    K(Z[arm], 216, 'easeoutquad', ROT_X=-30, ROT_Z=8 * s)
K(Z['head'], 180, 'easeinoutquad', ROT_X=10); K(Z['head'], 186, 'easeoutquad', ROT_X=-12); K(Z['head'], 206, 'easeoutquad', ROT_X=14)
K(Z['head'], 216, 'easeoutquad', ROT_X=4)
# S5 Zu eats: head dips to the pizza and bobs with every chew; cheeks puff
K(Z['head'], 240, 'easeinoutquad', ROT_X=4, ROT_Y=0)
K(Z['head'], 246, 'easeoutquad', ROT_X=26)                      # bite
for i, f in enumerate(range(252, 312, 6)):
    K(Z['head'], f, 'easeinoutsine', ROT_X=8 if i % 2 == 0 else 14, ROT_Y=6 if i % 4 < 2 else -6)
for arm, s in (('right_arm', 1), ('left_arm', -1)):
    K(Z[arm], 240, 'easeinoutquad', ROT_X=-30, ROT_Z=8 * s); K(Z[arm], 248, 'easeoutback', ROT_X=-50, ROT_Z=6 * s)
# S6 Bin: awkward smile + sweat, then laughs (body bounce, head back)
K(B['char'], 312, 'linear', ROT_Z=-115)
K(B['head'], 312, 'easeinoutquad', ROT_X=0, ROT_Y=0); K(B['head'], 320, 'easeoutquad', ROT_Y=-12)
K(B['head'], 348, 'easeinoutquad', ROT_Y=-12, ROT_X=0)
for i, f in enumerate(range(352, 384, 5)):
    K(B['head'], f, 'easeinoutsine', ROT_X=-14 if i % 2 == 0 else -6, ROT_Y=0)
    K(B['body'], f, 'easeinoutsine', ROT_X=-4 if i % 2 == 0 else 2)
for arm, s in (('right_arm', 1), ('left_arm', -1)):
    K(B[arm], 312, 'easeinoutquad', ROT_X=-15, ROT_Z=6 * s)
    K(B[arm], 352, 'easeoutback', ROT_X=-40, ROT_Z=-30 * s)        # hands on belly-ish
K(B['right_arm'], 318, 'easeoutquad', ROT_X=-150, ROT_Z=-46); K(B['right_arm'], 346, 'easeinoutquad', ROT_X=-150, ROT_Z=-46)   # scratches head
for f in range(322, 346, 4):
    K(B['right_arm'], f, 'easeinoutsine', ROT_X=-150 if (f // 4) % 2 else -140, ROT_Z=-46)
zsca(350, 'easeinoutquad', POS_Z=16); zsca(356, 'easeoutquad', sx=.9, sz=1.15, POS_Z=19); zsca(362, 'easeinquad', POS_Z=16)
zsca(366, 'easeoutelastic', POS_Z=16)

# ================= FACE RIG =================
EXPR = {  # eyes, brows, mouth, pupil size
    'sniff': ('closed', 'raised', 'oh', 'normal'), 'love': ('heart', 'raised', 'drool', 'normal'),
    'neutral': ('open', 'neutral', 'rest', 'normal'), 'shock': ('popped', 'raised', 'scream', 'small'),
    'want': ('sparkle', 'angry', 'grin3', 'normal'), 'yum': ('squeeze', 'raised', 'chew1', 'normal'),
    'awkward': ('half', 'worried', 'wavy', 'normal'), 'laugh': ('happy', 'raised', 'grin3', 'normal'),
    'stuffed_happy': ('happy', 'raised', 'chew1', 'normal'), 'curious': ('open', 'curious', 'rest', 'normal')}
FX = {'bin': {}, 'zu': {}}


def expr(n, f, e, **extra):
    E = EXPR[e]
    FX[n].setdefault(f, {}).update(eyes=E[0], brows=E[1], mouth=E[2], psize=E[3], **extra)


def fx(n, f, **v):
    FX[n].setdefault(f, {}).update(v)


expr('zu', 0, 'sniff', blush=False, brow_dz=0, gaze=(0, 0)); expr('bin', 0, 'curious', blush=False, brow_dz=0, gaze=(-.6, 0))
expr('zu', 40, 'love', blush=True); expr('zu', 168, 'want', blush=False); expr('zu', 240, 'yum', blush=True)
for i, f in enumerate(range(250, 312, 4)):
    fx('zu', f, mouth='chew2' if i % 2 else 'chew1')
expr('zu', 350, 'stuffed_happy', blush=True)
expr('bin', 108, 'neutral', gaze=(-.6, 0)); expr('bin', 119, 'shock', brow_dz=1.4, gaze=(0, 0)); fx('bin', 128, brow_dz=.6)
expr('bin', 140, 'curious', brow_dz=0); expr('bin', 312, 'awkward'); expr('bin', 350, 'laugh', blush=True)
for n, f0 in (('bin', 60), ('bin', 300), ('zu', 226), ('bin', 200)):   # a few blinks where eyes are plain
    st = {}
    for k in sorted(FX[n]):
        if k <= f0:
            st.update(FX[n][k])
    if st.get('eyes') in ('open', 'half'):
        e = st['eyes']; fx(n, f0, eyes='half'); fx(n, f0 + 1, eyes='closed'); fx(n, f0 + 3, eyes='half'); fx(n, f0 + 4, eyes=e)

for n in FX:
    ch, st = P[n], {}
    for f in sorted(FX[n]):
        st.update(FX[n][f])
        hide_p = st['eyes'] in faces.NO_PUPIL
        gx, gz = st.get('gaze', (0, 0))
        K(ch['eyes'], f, 'instant', TEXTURE_OBJ=RID[f"{n}_eyes_{st['eyes']}"], POS_Y=ch['eyes_y'], SCA_X=.5, SCA_Y=.5, SCA_Z=.5)
        K(ch['pupils'], f, 'instant', TEXTURE_OBJ=RID[f"{n}_pupils_{st['psize']}"], POS_X=gx, POS_Y=3.0 if hide_p else ch['pupils_y'],
          POS_Z=gz + (-.3 if st['eyes'] == 'half' else 0), SCA_X=.5, SCA_Y=.5, SCA_Z=.5)
        K(ch['brows'], f, 'easeoutback' if st.get('brow_dz') else 'instant', TEXTURE_OBJ=RID[f"{n}_brows_{st['brows']}"],
          POS_Y=ch['brows_y'], POS_Z=st.get('brow_dz', 0), SCA_X=.5, SCA_Y=.5, SCA_Z=.5)
        K(ch['mouth'], f, 'instant', TEXTURE_OBJ=RID[f"{n}_mouth_{st['mouth']}"], POS_Y=ch['mouth_y'], SCA_X=.5, SCA_Y=.5, SCA_Z=.5)
        K(ch['blush'], f, 'instant', TEXTURE_OBJ=RID['fx_blush'], POS_Y=ch['blush_y'], SCA_X=.5, SCA_Y=.5, SCA_Z=.5,
          VISIBLE=bool(st.get('blush')))

# Zu's cheeks puff: the head widens on every chew (the cube cheeks crossed his mouth in v1)
for i, f in enumerate(range(252, 312, 6)):
    k = 1.12 if i % 2 == 0 else 1.05
    K(Z['head'], f, 'easeinoutsine', SCA_X=ZH * k, SCA_Y=ZH * 1.02, SCA_Z=ZH * (2 - k) ** .5)
K(Z['head'], 314, 'easeoutelastic', SCA_X=ZH, SCA_Y=ZH, SCA_Z=ZH)
# sweat drop on Bin (slides down the side of the face), "!" pop over Bin's head
SW = B['sweat']
K(SW, 0, 'instant', VISIBLE=False, POS_X=-3.1, POS_Y=4.07, POS_Z=2.6, SCA_X=.1, SCA_Y=.1, SCA_Z=.1)
K(SW, 318, 'instant', VISIBLE=True, POS_X=-3.1, POS_Y=4.07, POS_Z=2.6, SCA_X=.03, SCA_Y=.03, SCA_Z=.03)
K(SW, 322, 'easeoutback', SCA_X=.12, SCA_Y=.12, SCA_Z=.12)
K(SW, 346, 'easeinquad', POS_Z=-1.0)
K(SW, 350, 'instant', VISIBLE=False)
MK = B['mark']
K(MK, 0, 'instant', VISIBLE=False, POS_X=0, POS_Y=4.2, POS_Z=9, SCA_X=.01, SCA_Y=.01, SCA_Z=.01)
K(MK, 119, 'instant', VISIBLE=True, TEXTURE_OBJ=RID['fx_mark_excl'])
K(MK, 123, 'easeoutback', SCA_X=.42, SCA_Y=.42, SCA_Z=.42, POS_Z=10)
K(MK, 128, 'easeinoutquad', SCA_X=.34, SCA_Y=.34, SCA_Z=.34)
K(MK, 160, 'easeinquad', SCA_X=.34, SCA_Y=.34, SCA_Z=.34)
K(MK, 164, 'instant', VISIBLE=False)
K(MK, 318, 'instant', VISIBLE=True, TEXTURE_OBJ=RID['fx_mark_q'], SCA_X=.01, SCA_Y=.01, SCA_Z=.01, POS_X=2.5)
K(MK, 322, 'easeoutback', SCA_X=.3, SCA_Y=.3, SCA_Z=.3)
K(MK, 346, 'easeinquad', SCA_X=.3, SCA_Y=.3, SCA_Z=.3)
K(MK, 350, 'instant', VISIBLE=False)
K(Z['mark'], 0, 'instant', VISIBLE=False)
K(Z['sweat'], 0, 'instant', VISIBLE=False)
# hearts rise from Zu's head while in love (40..167), staggered loops
for i, h in enumerate(HEARTS):
    K(h, 0, 'instant', VISIBLE=False, SCA_X=.01, SCA_Y=.01, SCA_Z=.01)
    for loop in range(3):
        f0 = 44 + i * 9 + loop * 40
        if f0 + 36 > 168:
            break
        x0 = (-3, 3, -1, 2)[i]
        K(h, f0, 'instant', VISIBLE=True, POS_X=x0, POS_Y=4.6, POS_Z=4, SCA_X=.05, SCA_Y=.05, SCA_Z=.05)
        K(h, f0 + 8, 'easeoutback', POS_X=x0 * 1.6, POS_Z=7, SCA_X=.2, SCA_Y=.2, SCA_Z=.2)
        K(h, f0 + 34, 'easeinquad', POS_X=x0 * 2.2 + (2 if i % 2 else -2), POS_Z=13, SCA_X=.12, SCA_Y=.12, SCA_Z=.12)
        K(h, f0 + 36, 'instant', VISIBLE=False)
# crumbs fly from the mouth on every other chew (S5)
for i, c in enumerate(CRUMBS):
    K(c, 0, 'instant', VISIBLE=False, SCA_X=.07, SCA_Y=.07, SCA_Z=.07)
    for f0 in range(254 + i * 4, 312, 24):
        a = random.uniform(-1, 1)
        K(c, f0, 'instant', VISIBLE=True, POS_X=a, POS_Y=4.6, POS_Z=-2.4)
        K(c, f0 + 5, 'easeoutquad', POS_X=a * 4, POS_Y=6.5, POS_Z=-1.2)
        K(c, f0 + 11, 'easeinquad', POS_X=a * 6, POS_Y=7.5, POS_Z=-6)
        K(c, f0 + 12, 'instant', VISIBLE=False)
# pizza on the table, steam rising, sparkles on the crash zoom
K(PZ, 0, 'linear', POS_X=3, POS_Y=13, POS_Z=16.15, ROT_X=-90, SCA_X=.8, SCA_Y=.8, SCA_Z=.8)
for i, s in enumerate(STEAM):                                   # thin steam until Zu starts eating (it covered his face in S5)
    K(s, 0, 'instant', VISIBLE=False)
    for loop in range(4):
        f0 = i * 22 + loop * 60
        if f0 + 50 > 236:
            break
        x = 3 + (-4, 0, 4)[i]
        K(s, f0, 'instant', VISIBLE=True, POS_X=x, POS_Y=13, POS_Z=18, SCA_X=.12, SCA_Y=.12, SCA_Z=.12, ALPHA=.0)
        K(s, f0 + 14, 'easeoutquad', POS_Z=22, SCA_X=.2, SCA_Y=.2, SCA_Z=.2, ALPHA=.45)
        K(s, f0 + 50, 'easeinquad', POS_X=x + 2, POS_Z=30, SCA_X=.26, SCA_Y=.26, SCA_Z=.26, ALPHA=.0)
        K(s, f0 + 51, 'instant', VISIBLE=False)
for i, s in enumerate(SPARK):
    p = ((-6, 12, 22), (12, 18, 25), (3, 8, 28))[i]
    K(s, 0, 'instant', VISIBLE=False, POS_X=p[0] + 4, POS_Y=p[1], POS_Z=p[2], SCA_X=.01, SCA_Y=.01, SCA_Z=.01)
    K(s, 78 + i * 3, 'instant', VISIBLE=True)
    K(s, 84 + i * 3, 'easeoutback', SCA_X=.32, SCA_Y=.32, SCA_Z=.32, ROT_Y=0)
    K(s, 100, 'easeinquad', SCA_X=.01, SCA_Y=.01, SCA_Z=.01, ROT_Y=90)
    K(s, 101, 'instant', VISIBLE=False)

# ================= LIGHT =================
BG = mk('background', 'Environment', 'null'); FILL = mk('pointlight', 'Fill light', 'null')
K(BG, 0, 'linear', BG_SKY_TIME=-52, BG_SUNLIGHT_STRENGTH=1.25, BG_SUNLIGHT_COLOR='#FFE6C0', BG_AMBIENT_COLOR='#6A7A9C', BG_SKY_COLOR='#7FB2FF')
for n in ('bin', 'zu'):
    K(P[n]['char'], 0, 'linear', SUBSURFACE=.6)


# ================= CAMERA =================
def look(px, py, pz, tx, ty, tz):
    dx, dy, dz = tx - px, ty - py, tz - pz
    return dict(POS_X=round(px, 2), POS_Y=round(py, 2), POS_Z=round(pz, 2),
                ROT_X=round(-math.degrees(math.atan2(dz, math.hypot(dx, dy))), 2), ROT_Z=round(math.degrees(math.atan2(dx, dy)), 2))


def dist(a):
    return math.dist(a[:3], a[3:])


# shot: start, end, cam start (pos+target), cam end, fov start, fov end, dutch, DOF focus (None = off), ease
SH = [
    (0, 71, (-19, -8, 12, -36, -14, 17), (-22, -9, 13, -36, -14, 17.5), 32, 26, 8, True, 'easeinoutsine'),      # S1 low-angle push-in ECU
    (72, 107, (-60, -38, 36, 2, 13, 17), (-60, -38, 36, 3, 13, 17), 55, 17, 0, False, 'easeoutexpo'),          # S2 OTS crash zoom
    (108, 167, (16, -18, 26, 40, -6, 28), (20, -16, 27, 40, -6, 28.5), 34, 30, -6, True, 'easeinoutsine'),     # S3 Bin MCU, shake on take
    (168, 239, (-22, -46, 3, -30, -10, 14), (2, -46, 3, 0, 16, 24), 52, 48, 10, False, 'easeinoutsine'),          # S4 worm's-eye tracking
    (240, 311, (6, -6, 46, 0, 20, 32), (5, -4, 44, 0, 20, 32), 28, 24, 0, True, 'easeinoutsine'),              # S5 high-angle ECU eating
    (312, 383, (20, -24, 31, 40, -6, 28), (8, -96, 44, 14, 6, 20), 32, 44, -4, True, 'easeinoutsine'),         # S6 Bin MCU -> pull out wide
]
for s, e, a, b, f0, f1, dutch, dof, ease in SH:
    K(cam, s, ease, CAM_FOV=f0, ROT_Y=dutch, CAM_DOF=dof, CAM_DOF_DEPTH=round(dist(a), 1), CAM_DOF_RANGE=10, CAM_DOF_FADE_SIZE=40,
      CAM_DOF_BLUR_SIZE=.012, CAM_SHAKE=False, CAM_VIGNETTE=True, CAM_VIGNETTE_STRENGTH=.55, **look(*a))
    K(cam, e, 'instant', CAM_FOV=f1, ROT_Y=dutch, CAM_DOF_DEPTH=round(dist(b), 1), **look(*b))
K(cam, END, 'linear', CAM_FOV=SH[-1][5], **look(*SH[-1][3]))
# crash zoom lands fast (S2): FOV hits target by frame 78 and holds
K(cam, 78, 'linear', CAM_FOV=17, **look(-60, -38, 36, 3, 13, 17))
# camera shake: Bin's double take (S3), Zu's landing (S4)
for f0, f1, strength in ((119, 131, 2.2), (206, 213, 1.6)):
    K(cam, f0, 'instant', CAM_SHAKE=True, CAM_SHAKE_STRENGTH_X=strength, CAM_SHAKE_STRENGTH_Y=strength, CAM_SHAKE_STRENGTH_Z=strength * .6,
      CAM_SHAKE_SPEED_X=9, CAM_SHAKE_SPEED_Y=9, CAM_SHAKE_SPEED_Z=9)
    K(cam, f1, 'instant', CAM_SHAKE=False)
# S4 the camera follows Zu up the arc (tilt up as he flies), keyed through the jump
for f in range(184, 207, 4):
    u = (f - 184) / 22
    tx, ty, tz = -36 + 36 * u, -14 + 36 * u, zarc(u) + 10
    K(cam, f, 'linear', **look(-22 + 24 * u, -46, 3, tx, ty, tz))
# fill light stays near the camera for every shot
for s, e, a, *_ in SH:
    K(FILL, s, 'instant', POS_X=a[0] - 6, POS_Y=a[1] - 4, POS_Z=a[2] + 10, LIGHT_COLOR='#FFE2C0', LIGHT_STRENGTH=.55, LIGHT_RANGE=150, LIGHT_SIZE=6)
flush()

# debug set view (MI_DEBUG_SET=1): 4 still frames - top-down, 3/4 overview, front, pizza close-up - to check block geometry
if os.environ.get('MI_DEBUG_SET'):
    NAME += ' debug'
    END = 3
    cam['keyframes'] = {}
    for f, (a, fov) in enumerate((((0, -1, 300, 0, 0, 0), 60), ((-170, -190, 150, 0, 0, 0), 50), ((0, -160, 40, 0, 0, 16), 50),
                                  ((3, -20, 40, 3, 13, 16), 40))):
        cam['keyframes'][str(f)] = dict(look(*a), CAM_FOV=fov, TRANSITION='instant')
# ---------------- assemble ----------------
cam['parent_tree_index'] = 0
d['templates'] = temps
used = {kf['TEXTURE_OBJ'] for t in [cam] + new for kf in t['keyframes'].values() if 'TEXTURE_OBJ' in kf}
used |= {t.get('model_tex') for t in temps} | {t['shape']['tex'] for t in temps if 'shape' in t}
d['resources'] = res = [r for r in res if r['id'] in used]          # ship only the textures the scene uses
d['timelines'] = [cam] + new
d['project']['render_settings'] = ''
d['background']['ground_show'] = False
d['render'].update(render_samples=48, render_subsurface_samples=16, render_ssao=True, render_shadows=True)
pr = d['project']
pr.update(name=NAME, video_width=1920, video_height=1080, tempo=FPS)
pr['timeline'].update(marker=0, zoom=3.5, hor_scroll=0, region_start=0, region_end=END)
json.dump(d, open(f'proj/{NAME}.miproject', 'w'), indent=1)
json.dump({'end': END, 'fps': FPS, 'shots': [s[:2] for s in SH]}, open('proj/timing.json', 'w'))
nk = sum(len(t['keyframes']) for t in d['timelines'])
print('MIPROJECT_OK::timelines=%d::keyframes=%d::frames=%d::resources=%d::templates=%d' % (len(d['timelines']), nk, END, len(res), len(temps)))
