"""Block-character rig for Blender (original Bin / Bo / Zu skins, 64x64 Minecraft-layout PNG).

Hierarchy (all parents keep an identity parent-inverse, so local location == offset from the parent's origin):
    <name>            empty at the feet (root)
      <name>_body     origin at the hip (bottom centre of the body box)
        <name>_head   origin at the neck; face layers are children of the head
        <name>_armR / <name>_armL   origin at the shoulder (top centre); <name>_handR/L empties at the arm tip
      <name>_legR / <name>_legL     origin at the hip joint
The character faces -Y. The character's right side is -X.

Face = 4 stacked planes on the head front (eyes, pupils, brows, mouth). Each plane shows one 32x32 tile of an
atlas; the tile is chosen by a keyframed Mapping-node offset (constant interpolation), so expressions are keyed
like any other channel: set_face(rig, frame, eyes='sparkle', mouth='drool').
"""
from __future__ import annotations

import math
import os

import bpy  # noqa: F401  (must be imported before bmesh)
import bmesh
import bpy
from mathutils import Matrix, Vector

LAYERS = {
    'eyes': ['open', 'wide', 'closed', 'sparkle', 'squeeze', 'heart', 'happy', 'half'],
    'pupils': ['normal', 'big', 'small', 'none'],
    'brows': ['neutral', 'raised', 'curious', 'worried'],
    'mouth': ['rest', 'oh', 'drool', 'open3', 'chew1', 'chew2', 'grin2', 'smile', 'open2'],
}
NO_PUPIL = {'closed', 'happy', 'heart', 'sparkle', 'squeeze'}
# box: (w, h, d) in skin pixels, skin UV origin, overlay UV origin
PARTS = {
    'head': ((8, 8, 8), (0, 0), (32, 0)),
    'body': ((8, 12, 4), (16, 16), (16, 32)),
    'armR': ((4, 12, 4), (40, 16), (40, 32)),
    'armL': ((4, 12, 4), (32, 48), (48, 48)),
    'legR': ((4, 12, 4), (0, 16), (0, 32)),
    'legL': ((4, 12, 4), (16, 48), (0, 48)),
}


def _uvbox(u, v, w, h, d):
    """Pixel rectangles (x0, y0, x1, y1) of each face in the 64x64 skin (image y down)."""
    return {
        'top': (u + d, v, u + d + w, v + d), 'bottom': (u + d + w, v, u + d + 2 * w, v + d),
        'right': (u, v + d, u + d, v + d + h), 'front': (u + d, v + d, u + d + w, v + d + h),
        'left': (u + d + w, v + d, u + 2 * d + w, v + d + h), 'back': (u + 2 * d + w, v + d, u + 2 * d + 2 * w, v + d + h),
    }


def box_mesh(name, size_px, uv0, k, anchor, inflate=0.0):
    """Box mesh with Minecraft-skin UVs. anchor = 'bottom' (origin at bottom centre) or 'top'."""
    w, h, d = size_px
    W, H, D = (w + 2 * inflate) * k, (h + 2 * inflate) * k, (d + 2 * inflate) * k
    z0 = -inflate * k if anchor == 'bottom' else -H + inflate * k
    x0, x1, y0, y1, z1 = -W / 2, W / 2, -D / 2, D / 2, z0 + H
    # corners named by (x side, y side, z side); front = -Y, character's right = -X
    P = lambda x, y, z: Vector((x, y, z))
    faces = {   # each: 4 corners in order image (left-top, right-top, right-bottom, left-bottom)
        'front': [P(x0, y0, z1), P(x1, y0, z1), P(x1, y0, z0), P(x0, y0, z0)],
        'back': [P(x1, y1, z1), P(x0, y1, z1), P(x0, y1, z0), P(x1, y1, z0)],
        'right': [P(x0, y1, z1), P(x0, y0, z1), P(x0, y0, z0), P(x0, y1, z0)],
        'left': [P(x1, y0, z1), P(x1, y1, z1), P(x1, y1, z0), P(x1, y0, z0)],
        'top': [P(x0, y1, z1), P(x1, y1, z1), P(x1, y0, z1), P(x0, y0, z1)],
        'bottom': [P(x0, y0, z0), P(x1, y0, z0), P(x1, y1, z0), P(x0, y1, z0)],
    }
    rects = _uvbox(uv0[0], uv0[1], w, h, d)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new('UVMap')
    for fname, corners in faces.items():
        verts = [bm.verts.new(c) for c in corners]
        f = bm.faces.new(verts)
        rx0, ry0, rx1, ry1 = rects[fname]
        img = [(rx0, ry0), (rx1, ry0), (rx1, ry1), (rx0, ry1)]
        for loop, (ix, iy) in zip(f.loops, img):
            loop[uvl].uv = (ix / 64.0, 1.0 - iy / 64.0)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def skin_material(name, img, overlay=False, bump=.02):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Closest'
    hs = nt.nodes.new('ShaderNodeHueSaturation')   # AgX desaturates; keep the skin colours as drawn
    hs.inputs['Saturation'].default_value = 1.0
    nt.links.new(tex.outputs['Color'], hs.inputs['Color'])
    nt.links.new(hs.outputs['Color'], bsdf.inputs['Base Color'])
    if overlay:
        nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    bsdf.inputs['Roughness'].default_value = .62
    bsdf.inputs['Subsurface Weight'].default_value = .06
    bsdf.inputs['Subsurface Radius'].default_value = (.02, .01, .006)
    # fine "felt" grain so the flat pixels catch light like a real object
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 900
    nz.inputs['Detail'].default_value = 4
    bp = nt.nodes.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = bump
    bp.inputs['Distance'].default_value = .002
    nt.links.new(nz.outputs['Fac'], bp.inputs['Height'])
    nt.links.new(bp.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def _atlas(face_dir, who, layer, states, out_dir):
    from PIL import Image
    n = len(states)
    at = Image.new('RGBA', (32 * n, 32), (0, 0, 0, 0))
    for i, s in enumerate(states):
        p = os.path.join(face_dir, f'{who}_{layer}_{s}.png')
        if os.path.exists(p):
            at.paste(Image.open(p).convert('RGBA'), (32 * i, 0))
    path = os.path.join(out_dir, f'{who}_{layer}_atlas.png')
    at.save(path)
    return path


def face_material(name, img, n, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.name = 'TILE'
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Closest'
    tex.extension = 'CLIP'
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Coat Weight'].default_value = .5 if rough < .3 else 0
    m['tiles'] = n
    return m


def _plane(name, w, h, n_tiles):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new('UVMap')
    vs = [bm.verts.new(v) for v in ((-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h))]
    f = bm.faces.new(vs)   # normal -Y (toward the viewer)
    for loop, uv in zip(f.loops, ((0, 0), (1 / n_tiles, 0), (1 / n_tiles, 1), (0, 1))):
        loop[uvl].uv = uv
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def _obj(name, data, parent=None, loc=(0, 0, 0), coll=None):
    o = bpy.data.objects.new(name, data)
    (coll or bpy.context.scene.collection).objects.link(o)
    if parent is not None:
        o.parent = parent
        o.matrix_parent_inverse = Matrix.Identity(4)
    o.location = loc
    o.rotation_mode = 'XYZ'
    return o


def build(who, skin_png, face_dir, atlas_dir, k=1 / 32, coll=None, bevel=.18):
    """Create the rig; returns dict of objects. k = metres per skin pixel."""
    img = bpy.data.images.load(skin_png)
    img.name = f'{who}_skin'
    mat = skin_material(f'{who}_skin', img)
    ov = skin_material(f'{who}_overlay', img, overlay=True)
    R = {}
    root = _obj(who, None, coll=coll)
    root.empty_display_size = .2
    R['root'] = root
    body = _obj(f'{who}_body', box_mesh(f'{who}_body', PARTS['body'][0], PARTS['body'][1], k, 'bottom'), root, (0, 0, 12 * k), coll)
    R['body'] = body
    head = _obj(f'{who}_head', box_mesh(f'{who}_head', PARTS['head'][0], PARTS['head'][1], k, 'bottom'), body, (0, 0, 12 * k), coll)
    R['head'] = head
    for side, sx in (('R', -1), ('L', 1)):
        arm = _obj(f'{who}_arm{side}', box_mesh(f'{who}_arm{side}', PARTS['arm' + side][0], PARTS['arm' + side][1], k, 'top'),
                   body, (sx * 6 * k, 0, 12 * k), coll)
        hand = _obj(f'{who}_hand{side}', None, arm, (0, 0, -11 * k), coll)
        hand.empty_display_size = .03
        leg = _obj(f'{who}_leg{side}', box_mesh(f'{who}_leg{side}', PARTS['leg' + side][0], PARTS['leg' + side][1], k, 'top'),
                   root, (sx * 2 * k, 0, 12 * k), coll)
        R['arm' + side], R['hand' + side], R['leg' + side] = arm, hand, leg
    for part in ('head', 'body', 'armR', 'armL', 'legR', 'legL'):
        o = R[part]
        o.data.materials.append(mat)
        bv = o.modifiers.new('bevel', 'BEVEL')
        bv.width = bevel * k
        bv.segments = 3
        bv.limit_method = 'ANGLE'
        # overlay (hat / jacket layer) only when the skin has pixels there
        size, _, ov_uv = PARTS[part]
        ux0, uy0 = ov_uv
        w, h, d = size
        a = img.pixels[:]  # flat RGBA, rows bottom-up
        has = False
        for yy in range(uy0, uy0 + d + h):
            for xx in range(ux0, ux0 + 2 * (w + d)):
                if a[((63 - yy) * 64 + xx) * 4 + 3] > 0:
                    has = True
                    break
            if has:
                break
        if has:
            anchor = 'bottom' if part in ('head', 'body') else 'top'
            om = _obj(f'{o.name}_ov', box_mesh(f'{o.name}_ov', size, ov_uv, k, anchor, inflate=.5), o, (0, 0, 0), coll)
            om.data.materials.append(ov)
    # face layers on the head front (y = -4k), stacked forward
    R['face'] = {}
    for i, (layer, states) in enumerate(LAYERS.items()):
        path = _atlas(face_dir, who, layer, states, atlas_dir)
        fimg = bpy.data.images.load(path)
        fm = face_material(f'{who}_{layer}', fimg, len(states), rough=.18 if layer in ('eyes', 'pupils') else .45)
        fp = _obj(f'{who}_{layer}', _plane(f'{who}_{layer}', 8 * k, 8 * k, len(states)), head,
                  (0, -4 * k - (.0006 + .0005 * i) - bevel * 0, 0), coll)
        fp.data.materials.append(fm)
        fp.visible_shadow = False
        R['face'][layer] = fp
    R['k'] = k
    R['who'] = who
    return R


def set_face(R, frame, **states):
    """Key face tiles at a frame (constant). eyes in NO_PUPIL hide the pupils automatically."""
    if 'eyes' in states and 'pupils' not in states:
        states['pupils'] = 'none' if states['eyes'] in NO_PUPIL else 'normal'
    for layer, st in states.items():
        if layer not in LAYERS:
            continue
        idx = LAYERS[layer].index(st)
        mat = R['face'][layer].data.materials[0]
        mp = mat.node_tree.nodes['TILE']
        mp.inputs['Location'].default_value[0] = idx / len(LAYERS[layer])
        mp.inputs['Location'].keyframe_insert('default_value', index=0, frame=frame)
        constant(mat.node_tree)


def look(R, frame, dx=0.0, dz=0.0):
    """Pupil offset in skin pixels (+dx = toward the character's left / screen right when facing camera)."""
    k = R['k']
    p = R['face']['pupils']
    p.location.x = dx * k
    p.location.z = dz * k
    p.keyframe_insert('location', index=0, frame=frame)
    p.keyframe_insert('location', index=2, frame=frame)


def fcurves(idb):
    ad = idb.animation_data
    if not ad or not ad.action:
        return []
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
        return list(cb.fcurves) if cb else []
    except Exception:
        return list(getattr(ad.action, 'fcurves', []))


def constant(idb):
    for fc in fcurves(idb):
        for kp in fc.keyframe_points:
            kp.interpolation = 'CONSTANT'


def key(obj, path, frame, value, index=-1):
    """Set + key a property; value may be a tuple for vector properties."""
    if index >= 0:
        getattr(obj, path)[index] = value
    else:
        setattr(obj, path, value)
    obj.keyframe_insert(path, index=index, frame=frame)


def keyrot(obj, frame, deg):
    obj.rotation_euler = tuple(math.radians(a) for a in deg)
    obj.keyframe_insert('rotation_euler', frame=frame)


def world_chain(objs_local):
    """Compose [(loc, euler_rad), ...] from root to leaf into a world matrix."""
    from mathutils import Euler
    M = Matrix.Identity(4)
    for loc, eul in objs_local:
        M = M @ Matrix.Translation(Vector(loc)) @ Euler(eul, 'XYZ').to_matrix().to_4x4()
    return M
