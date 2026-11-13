"""MC-S1 Short #01 "Who can bounce the highest?" in Mine-imator 2.0.2 (9:16, 1080x1920 @30, 18 s).

Same beats and timing as the cloud preview (tools/blockfilm/s01_bounce/web/s01_story.js, QC'd v3) so the same audio
(out/mix.wav) and the same transparent overlay (banner, scoreboard, counters) can be laid on top in post.
Set = Mine-imator's own blocks: slime_block pads, red/white wool height tower, grass ground, oak trees, white wool clouds.
Cast = original Bin / Bo / Zu skins + face rig from binbo_thu02/03.

    python prep.py WORK && python build.py WORK     # -> WORK/proj/BinBo MI S01 bounce.miproject

Coordinates: three.js (x right, y up, z toward camera, 1 block = 1) -> Mine-imator (X = -16x, Y = -16z, Z = 16(y - .5)),
because Mine-imator's screen-right is -X when the camera looks along +Y (MEASURED_FACTS.md).
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
random.seed(11)
d = json.load(open(os.path.join(HERE, '..', 'binbo_thu02', 'template.miproject')))
FPS, END = 30, 540
NAME = 'BinBo MI S01 bounce v2'


def nid():
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(16))


def M(x, y, z):
    """three.js point -> Mine-imator point."""
    return (-16 * x, -16 * z, 16 * (y - .5))


# ---------------- story timing (identical to s01_story.js) ----------------
JUMPS = {'bin': [(.30, 2.2, 8)], 'bo': [(4.40, .8, 3), (5.20, 2.2, 16)], 'zu': [(9.00, .5, 1)]}
ZL, ZOFF, ZBACK, ZLAND, ZWIN = 12.40, 14.0, 15.2, 15.65, 16.9
PADX = {'bin': -2.1, 'bo': 0.0, 'zu': 2.1}


def clamp(x, a=0., b=1.):
    return max(a, min(b, x))


def eout(u):
    return 1 - (1 - clamp(u)) ** 3


def ease(u):
    u = clamp(u)
    return 2 * u * u if u < .5 else 1 - (-2 * u + 2) ** 2 / 2


def jumpH(n, t):
    for t0, dd, pk in JUMPS[n]:
        if t0 <= t <= t0 + dd:
            u = (t - t0) / dd
            return 4 * pk * u * (1 - u)
    return 0.


def zuH(t):
    if ZL <= t < ZBACK:
        return 34 * (t - ZL) ** 1.55 + jumpH('zu', t)
    if ZBACK <= t < ZLAND:
        u = (t - ZBACK) / (ZLAND - ZBACK)
        return 46 * (1 - u * u)
    return jumpH('zu', t)


def H(n, t):
    return zuH(t) if n == 'zu' else jumpH(n, t)


def squash(n, t):
    k = 0.
    evs = [(t0, t0 + dd) for t0, dd, _ in JUMPS[n]]
    if n == 'zu':
        evs += [(ZL, 1e9), (1e9, ZLAND)]
    for a, b in evs:
        if a - .28 <= t < a:
            k = max(k, .38 * eout((t - (a - .28)) / .28))
        if b <= t < b + .35:
            u = (t - b) / .35
            k = max(k, .45 * math.exp(-u * 3) * abs(math.cos(u * 7)))
    if n == 'zu' and 11.6 <= t < ZL:
        k = max(k, .62 * eout((t - 11.6) / .8))
    if n == 'bin' and t < .3:
        k = max(k, .25 + .13 * eout(t / .3))
    if n == 'bin' and t > 17.72:
        k = max(k, .25 * eout((t - 17.72) / .28))
    return k


def shake(t, amp):
    return (math.sin(t * 37.1) * amp + math.sin(t * 61.7) * amp * .5, math.sin(t * 43.3) * amp + math.cos(t * 71.9) * amp * .4,
            math.sin(t * 29.3) * amp * .6)


def shot(t):
    """Camera (pos, look, vertical fov) in three.js units - the QC'd v3 shot list."""
    if t < .4 or (ZBACK <= t < ZLAND) or t >= ZWIN:
        u = t / .4 if t < .4 else (0 if t < ZLAND else t - ZWIN)
        return (0, 3.7, 12.2 - u * .3), (0, 2.6, 0), 52
    if ZLAND <= t < ZWIN:
        u = eout((t - ZLAND) / .5)
        return (1.95, 3.0, 5.6 - u * .6), (2.1, 3.05, 0), 46
    if t < 3.6:
        ty = 2.4 + jumpH('bin', t)
        return (-.9, ty + .6, 10.4), (-2.0, ty, 0), 55
    if t < 4.4:
        u = (t - 3.6) / .8
        return (.6, 2.7, 5.6 - u * .6), (0, 2.65, 0), 44
    if t < 7.8:
        ty = 2.4 + jumpH('bo', t)
        return (1.3, ty + .6, 11.4), (.2, ty, 0), 56
    if t < 8.6:
        u = eout((t - 7.8) / .25)
        return (-2.0, 3.15, 3.9), (-2.1, 3.05, 0), 46 - u * 10
    if t < 10:
        y = jumpH('zu', t)
        return (1.85, 2.5 + y * .5, 6.8), (2.1, 2.6 + y * .6, 0), 46
    if t < 11:
        return (-1.05, 3.0, 8.6), (-1.05, 2.75, 0), 50
    if t < ZL:
        u = ease((t - 11) / 1.4)
        return (2.1, 2.35, 4.4 - u * 1.4), (2.1, 2.2 - u * .15, 0), 42 - u * 4
    if t < ZOFF:
        ty = min(1.5 + zuH(t), 26.5)
        s = shake(t, .25 * (1 - (t - ZL) / .35)) if t < ZL + .35 else (0, 0, 0)
        return (1.7 + s[0], max(ty - 1.6, 2.1) + s[1], 10.5 + s[2]), (2.1, max(ty + 1.2, 2.6), 0), 58
    u = (t - ZOFF) / (ZBACK - ZOFF)
    return (-1.05, 2.6, 7.6 - u * .9), (-1.05, 3.75, 0), 56


# ---------------- resources ----------------
res, RID = [], {}
for n in ('bin', 'bo', 'zu'):
    i = nid(); RID[n + '_skin'] = i
    res.append({'id': i, 'type': 'skin', 'filename': f'skins/{n}_faceless.png', 'player_skin': True, 'material_format': 0})
for sub in ('face', 'fx'):
    for f in sorted(os.listdir(f'proj/{sub}')):
        i = nid(); RID[f[:-4]] = i
        res.append({'id': i, 'type': 'texture', 'filename': f'{sub}/{f}', 'material_format': 0})

# ---------------- templates ----------------
steve_t = [t for t in d['templates'] if t['model']['name'] == 'human'][0]
temps, TID = [], {}
for n in ('bin', 'bo', 'zu'):
    t = copy.deepcopy(steve_t); t.update(id=nid(), model_tex=RID[n + '_skin'], name=n.capitalize()); temps.append(t); TID[n] = t['id']


def shape_t(kind, tex, name, face_camera=False):
    t = {'id': nid(), 'type': kind, 'name': name,
         'shape': {'tex': RID[tex], 'tex_mapped': False, 'tex_hoffset': 0, 'tex_voffset': 0, 'tex_hrepeat': 1, 'tex_vrepeat': 1,
                   'tex_hmirror': False, 'tex_vmirror': False, 'closed': True, 'invert': False, 'detail': 32, 'face_camera': face_camera}}
    temps.append(t)
    return t['id']


def block_t(name, state, rep, label):
    t = {'id': nid(), 'type': 'block', 'name': label,
         'block': {'name': name, 'state': state, 'tex': 'default', 'tex_material': 'default', 'tex_normal': 'default',
                   'randomize': False, 'repeat_enable': True, 'repeat': [rep[0], rep[2], rep[1]]}}   # JSON point3D is [x, up, y]
    temps.append(t)
    return t['id']


SURF = shape_t('surface', 'bin_eyes_open', 'face layer')
SPARK_T = shape_t('surface', 'fx_sparkle', 'fx sparkle', face_camera=True)

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


for n in ('bin', 'bo', 'zu'):
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
    for li, (layer, dy) in enumerate((('eyes', 4.02), ('pupils', 4.035), ('brows', 4.045), ('mouth', 4.025))):
        s_ = mk('surface', f'{n}_{layer}', SURF, parent=head, parent_tree_index=li + 1, shadows=False, ssao=False)
        s_['inherit'] = dict(s_['inherit'], texture=False, alpha=True, visibility=True, scale=True, position=True, rotation=True)
        P[n][layer] = s_; P[n][layer + '_y'] = dy

# ---------------- set ----------------
SETTL = {}


def block(label, bn, st, rep, center_xy, z0):
    t = mk('block', label, block_t(bn, st, rep, label))
    t['keyframes'] = {'0': {'POS_X': center_xy[0], 'POS_Y': center_xy[1], 'POS_Z': z0, 'TRANSITION': 'linear'}}
    SETTL[label] = t
    return t


block('Ground', 'grass_block', {}, (70, 44, 1), (0, 200), -16)
for dx, dy, h in ((-150, 330, 3), (170, 360, 4), (-330, 420, 5), (330, 420, 6), (0, 520, 4), (-480, 300, 3), (480, 330, 4)):   # back hills
    block(f'Hill {dx}', 'grass_block', {}, (14, 8, h), (dx, dy), 0)
TREES = ((-150, 150, 5), (150, 180, 6), (-260, 260, 6), (250, 250, 5), (-90, 300, 6), (60, 330, 5))
for i, (tx, ty, h) in enumerate(TREES):
    block(f'Trunk {i}', 'log', {'variant': 'oak', 'axis': 'y'}, (1, 1, h), (tx, ty), 0)
    block(f'Leaves {i}', 'leaves', {'variant': 'oak'}, (5, 5, 3), (tx, ty), (h - 1) * 16)
    block(f'Leaves top {i}', 'leaves', {'variant': 'oak'}, (3, 3, 1), (tx, ty), (h + 2) * 16)
PAD = {}
for n, x in PADX.items():
    X, Y, _ = M(x, 0, 0)
    PAD[n] = block(f'Pad {n}', 'slime_block', {}, (1, 1, 1), (X, Y), 0)
TX, TY, _ = M(5, 0, -2)
for k in range(7):     # height tower: 4-block rings, red / white
    block(f'Tower {k}', 'wool', {'color': 'red' if k % 2 == 0 else 'white'}, (1, 1, 4), (TX, TY), 64 * k)
for n in range(4, 29, 4):   # numbers on the tower face at feet height n (feet height = 16 + 16 n)
    lab = mk('surface', f'Num {n}', shape_t('surface', f'fx_num{n}', f'num {n}'), shadows=False, ssao=False)
    lab['keyframes'] = {'0': {'POS_X': TX, 'POS_Y': TY - 8.2, 'POS_Z': 16 + 16 * n, 'ROT_Z': 180, 'SCA_X': .8, 'SCA_Y': .8, 'SCA_Z': .8,
                              'TRANSITION': 'linear'}}
rnd = random.Random(5)
for i in range(16):     # clouds
    cx, cy, cz = rnd.uniform(-700, 700), rnd.uniform(-80, 420), rnd.uniform(380, 470)
    block(f'Cloud {i}', 'wool', {'color': 'white'}, (rnd.randint(4, 8), rnd.randint(3, 6), 1), (round(cx), round(cy)), round(cz))

# ---------------- keyframe helper (state carried forward; only non-default values written) ----------------
EV = {}
DEF1 = {'SCA_X', 'SCA_Y', 'SCA_Z', 'ALPHA', 'CAM_FOV'}


def K(tl, f, tr='linear', **v):
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


SCALE = {'bin': 1.0, 'bo': 1.0, 'zu': .6}
HEADS = {'bin': 1.0, 'bo': 1.0, 'zu': 1.25}


def look_yaw(n, m):
    return clamp((PADX[m] - PADX[n]) * .22, -.7, .7)


def acting(n, t):
    """Pose for character n at time t (same decisions as act() in s01_story.js). Returns dict."""
    h = H(n, t); air = h > .02
    s = dict(anim='idle', eyes='normal', mouth='closed', yaw=0., pitch=0., glow=False)
    if air:
        up = H(n, t + .02) - h > 0
        s.update(anim='cheer' if up else 'fall', eyes='happy' if up else 'wide', mouth='grin' if up else 'O')
    if n == 'bin':
        if not air and t < .3: s.update(anim='hold', eyes='sly', mouth='smile')
        elif not air and t < 3.6: s.update(anim='cheer', eyes='happy', mouth='grin')
        elif t < 7.8 and not air: s.update(yaw=look_yaw('bin', 'bo'), eyes='wide' if t > 5.2 else 'normal', mouth='O' if t > 5.2 else 'smile')
        elif t < 8.6: s.update(eyes='wide', mouth='O', yaw=.25)
        elif t < 10: s.update(yaw=look_yaw('bin', 'zu'))
        elif t < 11: s.update(anim='laugh', eyes='happy', mouth='grin')
        elif t < ZL: s.update(yaw=look_yaw('bin', 'zu'), eyes='wide', mouth='O')
        elif t < ZBACK:
            gl = 14.4 < t < 14.9
            s.update(anim='lookup', yaw=.55 if gl else .15, pitch=-.1 if gl else -.5,
                     eyes='wide' if t < ZOFF else 'sly' if gl else 'normal', mouth='O' if t < ZOFF else 'frown' if gl else 'closed')
        else:
            s.update(yaw=look_yaw('bin', 'zu'), eyes='wide' if t < ZWIN else 'happy', mouth='O' if t < ZWIN else 'smile')
            if t > 17.72: s.update(anim='hold', eyes='sly', mouth='smile', yaw=0)
    if n == 'bo':
        if t < 3.6 and not air:
            s.update(yaw=look_yaw('bo', 'bin'), eyes='wide' if .6 < t < 3 else 'normal', mouth='O' if .6 < t < 3 else 'closed')
        elif t < 4.4: s.update(anim='point', eyes='sly', mouth='smile')
        elif t < 7.8 and not air: s.update(anim='cheer', eyes='happy', mouth='grin')
        elif t < 10: s.update(yaw=look_yaw('bo', 'zu'))
        elif t < 11: s.update(anim='laugh', eyes='happy', mouth='grin')
        elif t < ZL: s.update(yaw=look_yaw('bo', 'zu'), eyes='wide', mouth='O')
        elif t < ZBACK:
            gl = 14.4 < t < 14.9
            s.update(anim='lookup', yaw=-.55 if gl else -.1, pitch=-.1 if gl else -.5,
                     eyes='wide' if t < ZOFF else 'sly' if gl else 'normal', mouth='O' if t < ZOFF else 'frown' if gl else 'closed')
        else:
            s.update(yaw=look_yaw('bo', 'zu'), eyes='wide' if t < ZWIN else 'happy', mouth='O' if t < ZWIN else 'smile')
    if n == 'zu':
        if t < 8.6:
            s.update(yaw=look_yaw('zu', 'bin' if t < 4.4 else 'bo'))
            if .6 < t < 3 or 5.2 < t < 7.6: s.update(eyes='star', mouth='O')
        elif not air and t < 9.5: s.update(anim='hold', eyes='happy', mouth='smile')
        elif not air and t < 10: s.update(anim='cheer', eyes='happy', mouth='grin')
        elif t < 11: s.update(yaw=look_yaw('zu', 'bin'), eyes='normal', mouth='frown')
        elif t < 11.6: s.update(anim='sad', eyes='sad', mouth='frown')
        elif t < ZL: s.update(anim='hold', eyes='glow', mouth='grin', glow=True)
        elif t >= ZLAND: s.update(anim='cheer', eyes='star', mouth='grin')
        if air and t >= ZL: s.update(eyes='glow', glow=True)
    return s, h, air


# expression map: (eyes, brows, mouth, pupils)
EXPR = {('normal', 'closed'): ('open', 'neutral', 'rest'), ('normal', 'smile'): ('open', 'neutral', 'smile'),
        ('normal', 'frown'): ('open', 'sad', 'frown'), ('wide', 'O'): ('wide', 'raised', 'oh'), ('happy', 'grin'): ('happy', 'raised', 'grin3'),
        ('happy', 'smile'): ('happy', 'raised', 'smile'), ('sly', 'smile'): ('half', 'curious', 'smile'), ('sly', 'frown'): ('half', 'worried', 'frown'),
        ('star', 'O'): ('sparkle', 'raised', 'oh'), ('star', 'grin'): ('sparkle', 'raised', 'grin3'), ('sad', 'frown'): ('sad', 'sad', 'frown'),
        ('glow', 'grin'): ('glow', 'angry', 'grin3'), ('wide', 'grin'): ('wide', 'raised', 'grin3'), ('happy', 'O'): ('happy', 'raised', 'oh')}

last_face = {n: None for n in P}
for f in range(0, END + 1, 2):
    t = f / FPS
    for n in ('bin', 'bo', 'zu'):
        ch = P[n]; s, h, air = acting(n, t); sq = squash(n, t); sc = SCALE[n]
        X, Y, _ = M(PADX[n], 0, 0)
        hop = abs(math.sin(t * 7)) * .22 * 16 if (s['anim'] in ('cheer', 'laugh') and not air) else 0
        Z = 16 * (1 - .55 * sq) + 16 * h + hop
        st = min(.18, abs(H(n, t + .02) - h) * .6) if air else 0
        K(ch['char'], f, 'linear', POS_X=X, POS_Y=Y, POS_Z=Z, ROT_Z=180,
          SCA_X=sc * (1 + sq * .35 - st * .4), SCA_Y=sc * (1 + sq * .35 - st * .4), SCA_Z=sc * (1 - sq * .45 + st))
        K(PAD[n], f, 'linear', SCA_X=1 + sq * .12, SCA_Y=1 + sq * .12, SCA_Z=1 - sq * .55, POS_X=X, POS_Y=Y, POS_Z=0)
        a = s['anim']; w = math.sin(t * 14)
        arms = {'idle': (math.sin(t * 2) * 3, 0), 'cheer': (-165 + w * 10, -24), 'fall': (-150, -45), 'hold': (-40, -6),
                'laugh': (-40 + abs(math.sin(t * 10)) * 15, -30), 'lookup': (-10, -5), 'sad': (5, 2), 'point': (-88, 0)}[a]
        for arm, side in (('right_arm', 1), ('left_arm', -1)):
            rx, rz = arms
            if a == 'point' and arm == 'left_arm':
                rx, rz = 0, 0
            K(ch[arm], f, 'linear', ROT_X=rx, ROT_Z=rz * side)
        legs = {'cheer': (-20 if air else 0), 'fall': 15, 'hold': -18}.get(a, 0)
        K(ch['right_leg'], f, 'linear', ROT_X=legs); K(ch['left_leg'], f, 'linear', ROT_X=-legs if air else legs)
        pitch = {'lookup': -32, 'sad': 22, 'laugh': -12 + abs(math.sin(t * 10)) * 8}.get(a, 0) + math.degrees(s['pitch']) * .3
        K(ch['head'], f, 'linear', ROT_X=pitch, ROT_Z=math.degrees(s['yaw']) * .9,
          SCA_X=HEADS[n], SCA_Y=HEADS[n], SCA_Z=HEADS[n])
        e = EXPR.get((s['eyes'], s['mouth']), EXPR[('normal', 'closed')])
        if e != last_face[n]:
            last_face[n] = e
            eyes = e[0]
            tex = RID[f'zu_eyes_glow'] if eyes == 'glow' else RID[f'{n}_eyes_{eyes}']
            hide_p = eyes in faces.NO_PUPIL or eyes == 'glow'
            K(ch['eyes'], f, 'instant', TEXTURE_OBJ=tex, POS_Y=ch['eyes_y'], SCA_X=.5, SCA_Y=.5, SCA_Z=.5)
            K(ch['pupils'], f, 'instant', TEXTURE_OBJ=RID[f'{n}_pupils_normal'], POS_Y=3.0 if hide_p else ch['pupils_y'],
              POS_Z=-.3 if eyes == 'half' else 0, SCA_X=.5, SCA_Y=.5, SCA_Z=.5)
            K(ch['brows'], f, 'instant', TEXTURE_OBJ=RID[f'{n}_brows_{e[1]}'], POS_Y=ch['brows_y'], SCA_X=.5, SCA_Y=.5, SCA_Z=.5)
            K(ch['mouth'], f, 'instant', TEXTURE_OBJ=RID[f'{n}_mouth_{e[2]}'], POS_Y=ch['mouth_y'], SCA_X=.5, SCA_Y=.5, SCA_Z=.5)

# crown on Zu's head (gold blocks), pops in after the landing
crown = []
for i, (cx, cz, sx, sz) in enumerate(((0, 0, .5, .14), (-3, 2.2, .12, .2), (3, 2.2, .12, .2), (0, 2.6, .12, .26))):
    b = mk('block', f'Crown {i}', block_t('gold_block', {}, (1, 1, 1), f'crown {i}'), parent=P['zu']['head']['id'], parent_tree_index=10 + i)
    K(b, 0, 'instant', VISIBLE=False, POS_X=cx, POS_Y=0, POS_Z=4.6 + cz, SCA_X=.01, SCA_Y=.01, SCA_Z=.01)
    f0 = int((ZLAND + .05) * FPS)
    K(b, f0, 'instant', VISIBLE=True)
    K(b, f0 + 8, 'easeoutback', SCA_X=sx, SCA_Y=sx, SCA_Z=sz)
    crown.append(b)
# sparkles around Zu at the win (root-level billboards)
zx, zy, _ = M(PADX['zu'], 0, 0)
for i in range(5):
    sp = mk('surface', f'Sparkle {i}', SPARK_T, shadows=False, ssao=False)
    ang = i * 72
    K(sp, 0, 'instant', VISIBLE=False, SCA_X=.01, SCA_Y=.01, SCA_Z=.01)
    f0 = int((ZLAND + .05) * FPS) + i * 2
    K(sp, f0, 'instant', VISIBLE=True, POS_X=zx + 10 * math.cos(math.radians(ang)), POS_Y=zy - 6, POS_Z=40 + 6 * math.sin(math.radians(ang)))
    K(sp, f0 + 10, 'easeoutback', SCA_X=.35, SCA_Y=.35, SCA_Z=.35, POS_Z=48 + 8 * math.sin(math.radians(ang)))
    K(sp, f0 + 40, 'easeinquad', SCA_X=.01, SCA_Y=.01, SCA_Z=.01)
    K(sp, f0 + 41, 'instant', VISIBLE=False)
# green power light on Zu's face while charging
GL = mk('pointlight', 'Zu power light', 'null')
K(GL, 0, 'instant', LIGHT_STRENGTH=0., LIGHT_COLOR='#7CFF4F', LIGHT_RANGE=60, POS_X=zx, POS_Y=zy - 14, POS_Z=36)
K(GL, int(11.6 * FPS), 'linear', LIGHT_STRENGTH=0.)
K(GL, int(12.3 * FPS), 'linear', LIGHT_STRENGTH=2.5)
K(GL, int(12.5 * FPS), 'instant', LIGHT_STRENGTH=0.)

# ================= LIGHT =================
BG = mk('background', 'Environment', 'null')
K(BG, 0, 'linear', BG_SKY_TIME=-52, BG_SUNLIGHT_STRENGTH=1.2, BG_SUNLIGHT_COLOR='#FFEBD0', BG_AMBIENT_COLOR='#7586A8', BG_SKY_COLOR='#6FB0FF')
for n in P:
    K(P[n]['char'], 0, 'linear', SUBSURFACE=.6)


# ================= CAMERA =================
def look(p, tg):
    px, py, pz = p; tx, ty, tz = tg
    dx, dy, dz = tx - px, ty - py, tz - pz
    return dict(POS_X=round(px, 2), POS_Y=round(py, 2), POS_Z=round(pz, 2),
                ROT_X=round(-math.degrees(math.atan2(dz, math.hypot(dx, dy))), 2), ROT_Z=round(math.degrees(math.atan2(dx, dy)), 2))


def fov_mi(vfov):
    """Mine-imator CAM_FOV is the vertical field of view like three.js (video is 9:16, so keep it as is)."""
    return vfov


CUTS = (.4, 3.6, 4.4, 7.8, 8.6, 10, 11, ZL, ZOFF, ZBACK, ZLAND, ZWIN)


def shot_no(t):
    return sum(t >= c for c in CUTS)


# key EVERY frame: a skipped key inside a static shot would let Mine-imator slide the camera into the next shot;
# the last frame of each shot is 'instant' so the cut is a hard cut, not a 1-frame blend
for f in range(0, END + 1):
    t = f / FPS
    p, tg, fv = shot(t)
    P3, T3 = M(*p), M(*tg)
    tr = 'instant' if f < END and shot_no((f + 1) / FPS) != shot_no(t) else 'linear'
    K(cam, f, tr, CAM_FOV=round(fov_mi(fv), 2), CAM_VIGNETTE=True, CAM_VIGNETTE_STRENGTH=.35, **look(P3, T3))
flush()

# ---------------- assemble ----------------
cam['parent_tree_index'] = 0
d['templates'] = temps
used = {kf['TEXTURE_OBJ'] for t in [cam] + new for kf in t['keyframes'].values() if 'TEXTURE_OBJ' in kf}
used |= {t.get('model_tex') for t in temps} | {t['shape']['tex'] for t in temps if 'shape' in t}
d['resources'] = res = [r for r in res if r['id'] in used]
d['timelines'] = [cam] + new
d['project']['render_settings'] = ''
d['background']['ground_show'] = False
d['render'].update(render_samples=32, render_subsurface_samples=16, render_ssao=True, render_shadows=True)
pr = d['project']
pr.update(name=NAME, video_width=1080, video_height=1920, tempo=FPS)
pr['timeline'].update(marker=0, zoom=3.5, hor_scroll=0, region_start=0, region_end=END)
os.makedirs('proj', exist_ok=True)
json.dump(d, open(f'proj/{NAME}.miproject', 'w'), indent=1)
nk = sum(len(t['keyframes']) for t in d['timelines'])
print('MIPROJECT_OK::timelines=%d::keyframes=%d::frames=%d::resources=%d::templates=%d' % (len(d['timelines']), nk, END, len(res), len(temps)))
