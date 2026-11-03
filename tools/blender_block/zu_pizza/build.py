"""Test 01: "Baby Zombie Zu tries PIZZA" - 10 s semi-realistic shot in Blender (Cycles), original IP only.

    python tools/blender_block/zu_pizza/build.py OUT_DIR        # needs `pip install bpy==5.2.3`
writes OUT_DIR/zu_pizza.blend (all images packed) + OUT_DIR/build_report.json.
Everything is procedural: no downloaded models, textures or HDRIs. Zu skin/face = our own code-drawn PNGs.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

import bpy  # noqa: F401  (must be imported before bmesh)
import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector, noise
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import rig  # noqa: E402

FPS, END = 24, 240
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out'))
os.makedirs(OUT, exist_ok=True)
REPORT = {}

# ------------------------------------------------------------------ assets (our own skins / faces)
work = os.path.join(OUT, 'assets')
if not os.path.exists(os.path.join(work, 'proj', 'skins', 'zu_faceless.png')):
    subprocess.run([sys.executable, os.path.join(HERE, '..', '..', 'mineimator', 'binbo_thu02', 'prep.py'), work], check=True,
                   stdout=subprocess.DEVNULL)
SKIN = os.path.join(work, 'proj', 'skins', 'zu_faceless.png')
FACE = os.path.join(work, 'proj', 'face')

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, END
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'BEZIER'


# ------------------------------------------------------------------ helpers
def mat(name, color, rough=.5, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    for k, v in kw.items():
        b.inputs[k].default_value = v
    return m


def N(m, t, **kw):
    n = m.node_tree.nodes.new(t)
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def L(m, a, b):
    m.node_tree.links.new(a, b)


def bsdf(m):
    return m.node_tree.nodes['Principled BSDF']


def box(name, size, loc, material, bevel=.004, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new('bv', 'BEVEL')
        b.width, b.segments = bevel, 3
    o.data.materials.append(material)
    return o


def cyl(name, r, h, loc, material, verts=48, bevel=.003):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts)
    o = bpy.context.object
    o.name = name
    if bevel:
        b = o.modifiers.new('bv', 'BEVEL')
        b.width, b.segments = bevel, 3
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return o


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


# ------------------------------------------------------------------ materials
def wood(name, base=(.42, .24, .12), scale=4.0, rough=.42):
    m = mat(name, base, rough, **{'Coat Weight': .25, 'Coat Roughness': .2})
    tc = N(m, 'ShaderNodeTexCoord')
    mp = N(m, 'ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1, 8, 1)
    wv = N(m, 'ShaderNodeTexWave', wave_type='BANDS', bands_direction='X')
    wv.inputs['Scale'].default_value = scale
    wv.inputs['Distortion'].default_value = 6
    wv.inputs['Detail'].default_value = 3
    nz = N(m, 'ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 30
    cr = N(m, 'ShaderNodeValToRGB')
    cr.color_ramp.elements[0].color = (base[0] * .55, base[1] * .5, base[2] * .45, 1)
    cr.color_ramp.elements[1].color = (min(1, base[0] * 1.35), min(1, base[1] * 1.3), min(1, base[2] * 1.2), 1)
    mx = N(m, 'ShaderNodeMath', operation='MULTIPLY_ADD')
    L(m, tc.outputs['Object'], mp.inputs['Vector'])
    L(m, mp.outputs['Vector'], wv.inputs['Vector'])
    L(m, mp.outputs['Vector'], nz.inputs['Vector'])
    L(m, wv.outputs['Fac'], mx.inputs[0])
    mx.inputs[1].default_value = .8
    L(m, nz.outputs['Fac'], mx.inputs[2])
    L(m, mx.outputs['Value'], cr.inputs['Fac'])
    L(m, cr.outputs['Color'], bsdf(m).inputs['Base Color'])
    bp = N(m, 'ShaderNodeBump')
    bp.inputs['Strength'].default_value = .08
    L(m, wv.outputs['Fac'], bp.inputs['Height'])
    L(m, bp.outputs['Normal'], bsdf(m).inputs['Normal'])
    return m


def tiles(name):
    m = mat(name, (.92, .92, .88), .12, **{'Coat Weight': .4})
    tc = N(m, 'ShaderNodeTexCoord')
    br = N(m, 'ShaderNodeTexBrick', offset=.5)
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = .006
    br.inputs['Brick Width'].default_value = .15
    br.inputs['Row Height'].default_value = .075
    br.inputs['Color1'].default_value = (.93, .93, .9, 1)
    br.inputs['Color2'].default_value = (.86, .88, .86, 1)
    br.inputs['Mortar'].default_value = (.55, .53, .5, 1)
    sx = N(m, 'ShaderNodeSeparateXYZ')
    cx = N(m, 'ShaderNodeCombineXYZ')
    L(m, tc.outputs['Object'], sx.inputs['Vector'])
    L(m, sx.outputs['X'], cx.inputs['X'])
    L(m, sx.outputs['Z'], cx.inputs['Y'])
    L(m, cx.outputs['Vector'], br.inputs['Vector'])
    L(m, br.outputs['Color'], bsdf(m).inputs['Base Color'])
    bp = N(m, 'ShaderNodeBump')
    bp.inputs['Strength'].default_value = .35
    L(m, br.outputs['Fac'], bp.inputs['Height'])
    L(m, bp.outputs['Normal'], bsdf(m).inputs['Normal'])
    return m


M = {
    'table': wood('oak_table'),
    'floor': wood('floor', (.33, .2, .11), 2.0, .5),
    'board': wood('pizza_board', (.62, .42, .22), 6.0, .55),
    'tiles': tiles('subway_tiles'),
    'paint': mat('wall_paint', (.86, .76, .6), .8),
    'cabinet': mat('cabinet', (.38, .55, .5), .45),
    'stone': mat('countertop', (.8, .79, .76), .25, **{'Coat Weight': .3}),
    'plate': mat('ceramic', (.95, .95, .93), .08, **{'Coat Weight': .8}),
    'glass': mat('glass', (.95, .98, 1), .02, **{'Transmission Weight': 1, 'IOR': 1.45}),
    'frame': mat('window_frame', (.95, .95, .95), .4),
    'leaf': mat('leaf', (.12, .36, .1), .45, **{'Subsurface Weight': .2}),
    'pot': mat('terracotta', (.62, .3, .18), .7),
    'jar1': mat('jar_beans', (.55, .32, .12), .5),
    'jar2': mat('jar_pasta', (.9, .75, .35), .5),
    'metal': mat('steel', (.8, .8, .82), .2, **{'Metallic': 1}),
    'red': mat('kettle_red', (.7, .08, .06), .25, **{'Coat Weight': .6}),
}
# outside the window: soft daylight
sky = bpy.data.materials.new('window_sky')
sky.use_nodes = True
nt = sky.node_tree
nt.nodes.remove(nt.nodes['Principled BSDF'])
em = nt.nodes.new('ShaderNodeEmission')
em.inputs['Color'].default_value = (.75, .88, 1, 1)
em.inputs['Strength'].default_value = 4
nt.links.new(em.outputs[0], nt.nodes['Material Output'].inputs['Surface'])


# pizza materials
def _objco(m):
    return N(m, 'ShaderNodeTexCoord').outputs['Object']   # slices share the pizza-centre origin -> no seams, metres


def cheese_mat():
    """Melted mozzarella: glossy yellow-orange, a few golden-brown blisters (~2 cm), smooth wet bumps."""
    m = mat('cheese', (1, .7, .2), .3, **{'Subsurface Weight': .25, 'Coat Weight': .2, 'Coat Roughness': .08})
    bsdf(m).inputs['Subsurface Radius'].default_value = (.012, .007, .003)
    co = _objco(m)
    nz = N(m, 'ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 38
    nz.inputs['Detail'].default_value = 3
    L(m, co, nz.inputs['Vector'])
    cr = N(m, 'ShaderNodeValToRGB')
    e = cr.color_ramp.elements
    e[0].position, e[0].color = .5, (1, .74, .24, 1)
    e[1].position, e[1].color = .66, (.72, .36, .06, 1)
    el = cr.color_ramp.elements.new(.74)
    el.color = (.45, .2, .04, 1)
    L(m, nz.outputs['Fac'], cr.inputs['Fac'])
    L(m, cr.outputs['Color'], bsdf(m).inputs['Base Color'])
    n2 = N(m, 'ShaderNodeTexNoise')
    n2.inputs['Scale'].default_value = 90
    n2.inputs['Detail'].default_value = 2
    L(m, co, n2.inputs['Vector'])
    bp = N(m, 'ShaderNodeBump')
    bp.inputs['Strength'].default_value = .12
    L(m, n2.outputs['Fac'], bp.inputs['Height'])
    L(m, bp.outputs['Normal'], bsdf(m).inputs['Normal'])
    return m


def crust_mat():
    """Baked dough: golden with darker oven spots, smooth bread surface (no sponge)."""
    m = mat('crust', (.8, .5, .2), .55, **{'Subsurface Weight': .05})
    co = _objco(m)
    nz = N(m, 'ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 30
    nz.inputs['Detail'].default_value = 3
    L(m, co, nz.inputs['Vector'])
    cr = N(m, 'ShaderNodeValToRGB')
    e = cr.color_ramp.elements
    e[0].position, e[0].color = .45, (.8, .48, .16, 1)
    e[1].position, e[1].color = .66, (.36, .16, .04, 1)
    L(m, nz.outputs['Fac'], cr.inputs['Fac'])
    L(m, cr.outputs['Color'], bsdf(m).inputs['Base Color'])
    n2 = N(m, 'ShaderNodeTexNoise')
    n2.inputs['Scale'].default_value = 120
    n2.inputs['Detail'].default_value = 2
    L(m, co, n2.inputs['Vector'])
    bp = N(m, 'ShaderNodeBump')
    bp.inputs['Strength'].default_value = .06
    L(m, n2.outputs['Fac'], bp.inputs['Height'])
    L(m, bp.outputs['Normal'], bsdf(m).inputs['Normal'])
    return m


PM = [crust_mat(), cheese_mat(), mat('pepperoni', (.26, .03, .018), .38, **{'Coat Weight': .2, 'Coat Roughness': .15}),
      mat('tomato_sauce', (.55, .07, .03), .22, **{'Coat Weight': .4}),
      mat('basil', (.06, .28, .05), .35, **{'Subsurface Weight': .2, 'Coat Weight': .3})]

# ------------------------------------------------------------------ pizza (8 slices, procedural)
PZ = Vector((0, 0, .81))      # pizza centre on the board/plate top
R = .18
RC = R - .026                 # cheese edge
NS = 8
SPAN = 2 * math.pi / NS
A0 = math.pi / 2 - SPAN / 2   # slice 0 points at Zu (+Y)
PEPS = [(.05, .0), (-.05, .02), (.0, .07), (.085, .065), (-.08, .07), (.03, -.06), (-.06, -.06), (.1, -.03),
        (-.105, -.015), (.0, .115), (.06, .11), (-.06, .115), (.03, .03), (.0, -.11), (-.03, -.03),
        (.11, .1), (-.12, .09), (.13, .02), (-.13, -.06), (.08, -.11), (-.09, -.12), (.035, .14), (-.035, .145)]


LEAVES = [(.07, .03, .4), (-.06, .095, 2.1), (.02, -.085, 1.2), (-.1, -.04, 2.8), (.1, .1, .9), (-.02, .05, 3.6),
          (.12, -.07, 5.0), (-.13, .04, 1.7)]


def h_top(r, x, y):
    if r <= RC:
        return .016 + .0022 * noise.noise(Vector((x * 45, y * 45, 0))) + .0008 * noise.noise(Vector((x * 140, y * 140, 1)))
    t = (r - RC) / (R - RC)
    return .009 + .018 * max(0.0, math.sin(math.pi * min(t, 1) * .9)) ** .6 + .001 * noise.noise(Vector((x * 90, y * 90, 3)))


def slice_mesh(name, i, rmin=lambda a: .002):
    a0, a1 = A0 + i * SPAN + .004, A0 + (i + 1) * SPAN - .004
    na, nr = 12, 30
    bm = bmesh.new()
    T, B = [], []
    for ja in range(na + 1):
        a = a0 + (a1 - a0) * ja / na
        r0 = rmin(a)
        rowT, rowB = [], []
        for jr in range(nr + 1):
            r = r0 + (R - r0) * (jr / nr) ** .9
            x, y = r * math.cos(a), r * math.sin(a)
            z = h_top(r, x, y)
            rowT.append(bm.verts.new((x, y, z)))
            rowB.append(bm.verts.new((x, y, .0)))
        T.append(rowT)
        B.append(rowB)
    for ja in range(na):
        for jr in range(nr):
            r_mid = (T[ja][jr].co.xy.length + T[ja][jr + 1].co.xy.length) / 2
            f = bm.faces.new((T[ja][jr], T[ja][jr + 1], T[ja + 1][jr + 1], T[ja + 1][jr]))
            f.material_index = 1 if r_mid < RC - .006 else (3 if r_mid < RC else 0)
            f.smooth = True
            g = bm.faces.new((B[ja][jr], B[ja + 1][jr], B[ja + 1][jr + 1], B[ja][jr + 1]))
            g.material_index = 0
        bm.faces.new((T[ja][nr], B[ja][nr], B[ja + 1][nr], T[ja + 1][nr])).material_index = 0      # outer rim
        bm.faces.new((T[ja][0], T[ja + 1][0], B[ja + 1][0], B[ja][0])).material_index = 1        # inner / bite edge
    for ja in (0, na):
        for jr in range(nr):
            f = bm.faces.new((T[ja][jr], B[ja][jr], B[ja][jr + 1], T[ja][jr + 1]))
            f.material_index = 1 if T[ja][jr].co.xy.length < RC else 0
    # pepperoni (cupped discs) that lie on this slice
    for (px, py) in PEPS:
        r, a = math.hypot(px, py), math.atan2(py, px)
        aa = (a - a0) % (2 * math.pi)
        if aa > (a1 - a0) or r > RC - .02:
            continue
        rr = .02
        # skip if the disc would cross the slice edges or the bite
        ok = all((math.atan2(py + rr * math.sin(t), px + rr * math.cos(t)) - a0) % (2 * math.pi) < (a1 - a0) - .002
                 and math.hypot(px + rr * math.cos(t), py + rr * math.sin(t)) > rmin(a) + .004
                 for t in np.linspace(0, 2 * math.pi, 12, endpoint=False))
        if not ok:
            continue
        z0 = h_top(r, px, py) + .0004
        c = bm.verts.new((px, py, z0 + .0006))
        ring = [bm.verts.new((px + rr * math.cos(t), py + rr * math.sin(t), z0 + .0019)) for t in np.linspace(0, 2 * math.pi, 20, endpoint=False)]
        low = [bm.verts.new((v.co.x, v.co.y, z0 - .0006)) for v in ring]
        for j in range(20):
            k2 = (j + 1) % 20
            f = bm.faces.new((c, ring[j], ring[k2]))
            f.material_index, f.smooth = 2, True
            f = bm.faces.new((ring[j], low[j], low[k2], ring[k2]))
            f.material_index, f.smooth = 2, True
    # basil leaves (flat curved ellipses, a little above the cheese)
    for (lx, ly, la) in LEAVES:
        r, a = math.hypot(lx, ly), math.atan2(ly, lx)
        if (a - a0) % (2 * math.pi) > (a1 - a0) - .05 or r > RC - .015 or r < rmin(a) + .02:
            continue
        z0 = h_top(r, lx, ly) + .0012
        ca, sa = math.cos(la), math.sin(la)
        ring = []
        for t in np.linspace(0, 2 * math.pi, 14, endpoint=False):
            u, v = .016 * math.cos(t), .008 * math.sin(t)
            ring.append(bm.verts.new((lx + u * ca - v * sa, ly + u * sa + v * ca, z0 + .002 * (1 - (u / .016) ** 2))))
        c = bm.verts.new((lx, ly, z0 + .0005))
        for q in range(14):
            f = bm.faces.new((c, ring[q], ring[(q + 1) % 14]))
            f.material_index, f.smooth = 4, True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in PM:
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    sc.collection.objects.link(o)
    o.location = PZ
    return o


slices = [slice_mesh(f'slice_{i}', i) for i in range(NS)]
bite = lambda a: .05 + .014 * abs(math.sin(3 * math.pi * ((a - A0) / SPAN)))
slice_bit = slice_mesh('slice_0_bitten', 0, rmin=bite)

# ------------------------------------------------------------------ set
floor = box('floor', (8, 8, .02), (0, 0, -.01), M['floor'], bevel=0)
TT = .775
box('table_top', (1.6, .9, .05), (0, .15, TT - .025), M['table'], bevel=.01)
for sx in (-.72, .72):
    for sy in (-.24, .54):
        box('table_leg', (.06, .06, TT - .05), (sx, sy, (TT - .05) / 2), M['table'], bevel=.004)
board = cyl('pizza_board', .235, .018, (0, 0, TT + .009), M['board'], bevel=.004)
box('board_handle', (.06, .14, .018), (.0, -.29, TT + .009), M['board'], bevel=.004)
plate = cyl('plate', .21, .012, (0, 0, TT + .018 + .006), M['plate'], bevel=.004)
PZ.z = TT + .018 + .012 + .0005
for s in slices + [slice_bit]:
    s.location = PZ
# back counter, wall, window
YW = 1.9
box('cabinets', (4, .6, .86), (0, YW - .3, .43), M['cabinet'], bevel=.006)
box('countertop', (4.02, .64, .04), (0, YW - .32, .88), M['stone'], bevel=.004)
WX0, WX1, WZ0, WZ1 = -1.05, -.25, 1.5, 2.08
box('wall_low', (4, .04, .6), (0, YW + .02, 1.2), M['tiles'], bevel=0)
box('wall_l', (WX0 + 2, .04, 1.3), ((WX0 - 2) / 2, YW + .02, 2.15), M['paint'], bevel=0)
box('wall_r', (2 - WX1, .04, 1.3), ((WX1 + 2) / 2, YW + .02, 2.15), M['paint'], bevel=0)
box('wall_top', (WX1 - WX0, .04, 2.8 - WZ1), ((WX0 + WX1) / 2, YW + .02, (WZ1 + 2.8) / 2), M['paint'], bevel=0)
for (sx, sz, w, h) in ((WX0, (WZ0 + WZ1) / 2, .04, WZ1 - WZ0), (WX1, (WZ0 + WZ1) / 2, .04, WZ1 - WZ0),
                      ((WX0 + WX1) / 2, (WZ0 + WZ1) / 2, .03, WZ1 - WZ0), ((WX0 + WX1) / 2, WZ0, WX1 - WX0, .04),
                      ((WX0 + WX1) / 2, WZ1, WX1 - WX0, .04), ((WX0 + WX1) / 2, (WZ0 + WZ1) / 2, WX1 - WX0, .025)):
    box('window_frame', (w, .06, h), (sx, YW + .02, sz), M['frame'], bevel=.003)
box('window_sky', (4, .01, 3), (-.6, YW + 1.2, 1.8), sky, bevel=0)
box('ceiling', (8, 8, .02), (0, 0, 2.8), M['paint'], bevel=0)
for sx in (-2.02, 2.02):
    box('wall_side', (.04, 5, 2.8), (sx, -.6, 1.4), M['paint'], bevel=0)
    box('tiles_side', (.03, 3.2, .6), (sx - .03 * (1 if sx > 0 else -1), .3, 1.2), M['tiles'], bevel=0)
# props on the counter (soft background detail)
cyl('jar_a', .05, .16, (.35, YW - .25, .98), M['jar1'], bevel=.006)
cyl('jar_b', .05, .2, (.48, YW - .25, 1.0), M['jar2'], bevel=.006)
cyl('jar_c', .045, .13, (.6, YW - .27, .965), M['glass'], bevel=.004)
box('cutting_board', (.36, .02, .26), (1.0, YW - .08, 1.03), M['board'], bevel=.008, rot=(math.radians(-8), 0, 0))
k = cyl('kettle', .09, .14, (-1.45, YW - .3, .97), M['red'], bevel=.03)
cyl('kettle_lid', .05, .02, (-1.45, YW - .3, 1.05), M['metal'], bevel=.005)
cyl('pot', .07, .12, (-.65, YW - .2, .96), M['pot'], bevel=.008)
for j, (dx, dz, s) in enumerate(((0, .09, .07), (.04, .13, .05), (-.04, .12, .055), (.0, .17, .045))):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=s, location=(-.65 + dx, YW - .2, .96 + dz))
    o = bpy.context.object
    o.name = f'leaf_{j}'
    o.data.materials.append(M['leaf'])
    bpy.ops.object.shade_smooth()
box('shelf', (1.2, .22, .03), (.7, YW - .11, 1.62), M['table'], bevel=.004)
for j in range(4):
    cyl(f'shelf_plate_{j}', .11, .012, (.3 + j * .012, YW - .12, 1.74), M['plate'], bevel=.003).rotation_euler = (math.radians(80), 0, 0)
cyl('mug', .04, .09, (.95, YW - .12, 1.68), M['red'], bevel=.006)
# glass of juice next to the pizza (foreground detail)
cyl('mug_front', .04, .1, (.33, -.05, TT + .05), M['red'], bevel=.006)
cyl('mug_milk', .034, .004, (.33, -.05, TT + .095), mat('milk', (.95, .93, .88), .15, **{'Subsurface Weight': .6}), bevel=0)

# ------------------------------------------------------------------ steam (volume)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, PZ.z + .2))
steam = bpy.context.object
steam.name = 'steam'
steam.scale = (.36, .36, .4)
vm = bpy.data.materials.new('steam')
vm.use_nodes = True
vt = vm.node_tree
vt.nodes.remove(vt.nodes['Principled BSDF'])
vol = vt.nodes.new('ShaderNodeVolumePrincipled')
vol.inputs['Color'].default_value = (1, 1, 1, 1)
vol.inputs['Anisotropy'].default_value = .4
tc = vt.nodes.new('ShaderNodeTexCoord')
mp = vt.nodes.new('ShaderNodeMapping')
mp.name = 'RISE'
nz = vt.nodes.new('ShaderNodeTexNoise')
nz.noise_dimensions = '4D'
nz.name = 'SWIRL'
nz.inputs['Scale'].default_value = 4.5
nz.inputs['Detail'].default_value = 4
nz.inputs['Distortion'].default_value = .6
vt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
vt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
sx = vt.nodes.new('ShaderNodeSeparateXYZ')
vt.links.new(tc.outputs['Object'], sx.inputs['Vector'])


def mnode(op, a=None, b=None, va=None, vb=None):
    n = vt.nodes.new('ShaderNodeMath')
    n.operation = op
    if a is not None:
        vt.links.new(a, n.inputs[0])
    if va is not None:
        n.inputs[0].default_value = va
    if b is not None:
        vt.links.new(b, n.inputs[1])
    if vb is not None:
        n.inputs[1].default_value = vb
    return n


rad = vt.nodes.new('ShaderNodeVectorMath')
rad.operation = 'LENGTH'
cxy = vt.nodes.new('ShaderNodeCombineXYZ')
vt.links.new(sx.outputs['X'], cxy.inputs['X'])
vt.links.new(sx.outputs['Y'], cxy.inputs['Y'])
vt.links.new(cxy.outputs['Vector'], rad.inputs[0])
radial = mnode('SUBTRACT', va=1, b=mnode('MULTIPLY', rad.outputs['Value'], vb=2.6).outputs[0])   # object coords -0.5..0.5
up = mnode('SUBTRACT', va=.5, b=sx.outputs['Z'])                                                # 1 at bottom, 0 at top
base = mnode('MULTIPLY', mnode('MAXIMUM', radial.outputs[0], vb=0).outputs[0], mnode('MAXIMUM', up.outputs[0], vb=0).outputs[0])
wisps = mnode('MULTIPLY', mnode('MAXIMUM', mnode('SUBTRACT', nz.outputs['Fac'], vb=.5).outputs[0], vb=0).outputs[0], vb=6)
dens = mnode('MULTIPLY', base.outputs[0], wisps.outputs[0])
dens2 = mnode('MULTIPLY', dens.outputs[0], vb=1.2)
dens2.name = 'DENSITY'
vt.links.new(dens2.outputs[0], vol.inputs['Density'])
vt.links.new(vol.outputs[0], vt.nodes['Material Output'].inputs['Volume'])
steam.data.materials.append(vm)
for f, w, z in ((1, 0, 0), (END, 4.0, -1.6)):
    nz.inputs['W'].default_value = w
    nz.inputs['W'].keyframe_insert('default_value', frame=f)
    mp.inputs['Location'].default_value[2] = z
    mp.inputs['Location'].keyframe_insert('default_value', index=2, frame=f)
for f, d in ((1, 5.5), (150, 5.5), (200, 3.0), (END, 2.4)):
    dens2.inputs[1].default_value = d
    dens2.inputs[1].keyframe_insert('default_value', frame=f)
for fc in rig.fcurves(vt):
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR'

# ------------------------------------------------------------------ world + lights
w = bpy.data.worlds.new('room')
sc.world = w
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (.55, .6, .66, 1)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = .18


def light(name, kind, loc, target, power, color=(1, 1, 1), size=1.0):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = power
    ld.color = color
    if kind == 'AREA':
        ld.shape, ld.size = 'DISK', size
    if kind == 'SUN':
        ld.angle = math.radians(3)
    o = bpy.data.objects.new(name, ld)
    sc.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    return o


light('sun_window', 'SUN', (-1.3, 3.5, 2.4), (0, .3, 1.1), 4.5, (1, .82, .6))
light('key', 'AREA', (1.1, -1.1, 1.75), (0, .28, 1.1), 110, (1, .93, .85), .9)
light('fill', 'AREA', (-1.6, -1.0, 1.3), (0, .2, 1.0), 14, (.78, .86, 1), 1.6)
light('rim', 'AREA', (.9, 1.25, 1.65), (0, .3, 1.1), 90, (1, .86, .7), .6)
light('food', 'AREA', (.3, -.35, 1.2), (0, 0, PZ.z), 14, (1, .9, .78), .3)
light('steam_back', 'AREA', (-.1, .9, 1.05), (0, 0, PZ.z + .2), 25, (1, .9, .8), .4)

# ------------------------------------------------------------------ Zu
K = 1 / 36
Zu = rig.build('zu', SKIN, FACE, OUT, k=K)
ZY = .30
Zu['root'].location = (0, ZY, TT - 12 * K - .02)
body, head, armR, armL, handR = Zu['body'], Zu['head'], Zu['armR'], Zu['armL'], Zu['handR']

key, keyrot = rig.key, rig.keyrot
REST_ARM = (-22, 0, 0)
# body / head performance -------------------------------------------------
for f, lean in ((1, 0), (30, 0), (40, 9), (112, 9), (120, 14), (150, 8), (168, 4), (180, 6), (204, 3), (240, 0)):
    keyrot(body, f, (lean, 0, 0))
HEAD = [  # frame, (rx down, ry tilt, rz turn)
    (1, (12, 0, 0)), (12, (2, 0, 0)), (14, (-4, 0, 0)), (17, (-1, 0, 2)), (20, (-5, 0, -2)), (23, (-1, 0, 2)), (26, (-6, 0, 0)),
    (30, (-2, 0, 0)), (34, (16, 0, 0)), (54, (18, 0, 0)),
    (55, (10, 0, 0)), (60, (8, 4, 3)), (62, (8, -4, -3)), (64, (8, 4, 3)), (66, (8, -4, -3)), (68, (8, 4, 3)), (70, (8, -4, -3)),
    (72, (8, 0, 0)), (80, (6, 6, 0)), (84, (14, 0, 0)), (112, (18, 0, 0)),
    (126, (20, 0, 0)), (140, (8, 0, 0)), (160, (-2, 0, 0)), (172, (-6, 0, 0)), (178, (-4, 0, 0)),
    (182, (2, 0, 0)), (186, (-2, 3, 0)), (190, (2, -3, 0)), (194, (-2, 3, 0)), (198, (2, -3, 0)), (204, (0, 0, 0)),
    (208, (-8, 0, 0)), (214, (-2, 8, 0)), (220, (-8, 0, 0)), (226, (-2, -8, 0)), (232, (-6, 0, 0)), (240, (-4, 6, 0)),
]
for f, r in HEAD:
    keyrot(head, f, r)
# chew: head widens on each bite (face planes are children, so they follow)
for f in range(180, 205, 3):
    w_ = 1.07 if (f // 3) % 2 else 1.0
    head.scale = (w_, 1, 1.0 / (w_ ** .5))
    head.keyframe_insert('scale', frame=f)
for f in (1, 179, 205, 240):
    head.scale = (1, 1, 1)
    head.keyframe_insert('scale', frame=f)
# root bounce of joy
for f, z in ((1, 0), (205, 0), (210, .035), (215, 0), (220, .035), (225, 0), (240, 0)):
    key(Zu['root'], 'location', f, Zu['root'].location.z if f == 1 else (TT - 12 * K - .02 + z), index=2)
# left arm: rests, then cheers
for f, r in ((1, REST_ARM), (205, REST_ARM), (210, (-155, 0, -12)), (216, (-120, 0, -6)), (222, (-160, 0, -14)), (228, (-125, 0, -6)),
             (236, (-150, 0, -10)), (240, (-145, 0, -10))):
    keyrot(armL, f, (r[0], r[1], -r[2]))
# face ------------------------------------------------------------------
sf, look = rig.set_face, rig.look
for f, st in ((1, dict(eyes='open', brows='neutral', mouth='rest')), (8, dict(eyes='half')), (12, dict(eyes='closed', mouth='oh')),
              (28, dict(eyes='open')), (30, dict(eyes='wide', pupils='big', brows='raised', mouth='oh')),
              (55, dict(eyes='sparkle', mouth='drool', brows='raised')), (84, dict(eyes='wide', pupils='big', mouth='drool')),
              (113, dict(eyes='sparkle', mouth='drool')), (128, dict(eyes='wide', pupils='big', mouth='grin2', brows='raised')),
              (150, dict(eyes='happy', mouth='grin2')), (164, dict(eyes='wide', pupils='big', mouth='open2')),
              (168, dict(eyes='wide', pupils='normal', mouth='open3')), (179, dict(eyes='squeeze', mouth='chew1', brows='neutral'))):
    sf(Zu, f, **st)
for f in range(182, 205, 3):
    sf(Zu, f, mouth='chew2' if (f // 3) % 2 else 'chew1')
sf(Zu, 205, eyes='heart', mouth='grin2', brows='raised')
sf(Zu, 236, eyes='happy', mouth='smile')
for f, dx, dz in ((1, 0, -1), (30, 0, -.5), (34, 0, -1.2), (84, 0, -1.2), (128, .3, -1), (164, 0, 0), (178, 0, 0)):
    look(Zu, f, dx, dz)

# right arm: solve poses so the hand really reaches the slice / mouth ------------------
WIDTH_SOLVE = []


def chain_hand(f, arm_e, hand_e):
    sc.frame_set(f)
    Wb = body.matrix_world.copy()
    return Wb @ Matrix.Translation(armR.location) @ Euler(arm_e, 'XYZ').to_matrix().to_4x4() @ \
        Matrix.Translation(handR.location) @ Euler(hand_e, 'XYZ').to_matrix().to_4x4()


def solve(f, hand_target, tip_target=None, inv=None, x0=None, hw=100.0, tw=100.0, uw=0.0):
    """Find arm + wrist rotation (radians) so the hand (and the slice tip, if given) hit the targets."""
    sc.frame_set(f)
    Wb = body.matrix_world.copy()
    ht = Vector(hand_target)
    tip_local = Vector((0, .01, .016))  # point at the slice tip in slice-object space (pizza centre)
    sl_rest = Matrix.Translation(PZ)    # slice rest pose (no parent, no rotation)

    def cost(v):
        A = Euler(v[:3], 'XYZ').to_matrix().to_4x4()
        H = Euler(v[3:], 'XYZ').to_matrix().to_4x4()
        Wh = Wb @ Matrix.Translation(armR.location) @ A @ Matrix.Translation(handR.location) @ H
        c = (Wh.translation - ht).length_squared * hw
        if tip_target is not None:
            tip = (Wh @ inv @ sl_rest) @ tip_local
            c += (tip - Vector(tip_target)).length_squared * tw
            if uw:   # keep the cheese side up so the camera sees the topping
                c += uw * (1 - (Wh @ inv @ sl_rest).to_3x3().col[2].normalized().z)
        return c + 1e-4 * float(np.dot(v, v))
    best = None
    starts = [x0] if x0 is not None else []
    starts += [np.radians([-60, 0, 0, 0, 0, 0]), np.radians([-90, 0, 20, 0, 0, 0]), np.radians([-80, 0, -30, 0, 90, 0]),
               np.radians([-100, 20, 30, 40, 0, 180]), np.radians([-70, -20, 40, -30, 0, -180])]
    for s in starts:
        r = minimize(cost, s, method='Nelder-Mead', options=dict(maxiter=6000, xatol=1e-5, fatol=1e-9))
        if best is None or r.fun < best.fun:
            best = r
    v = best.x
    A = Euler(v[:3], 'XYZ').to_matrix().to_4x4()
    H = Euler(v[3:], 'XYZ').to_matrix().to_4x4()
    Wh = Wb @ Matrix.Translation(armR.location) @ A @ Matrix.Translation(handR.location) @ H
    e = dict(frame=f, hand_mm=round((Wh.translation - ht).length * 1000, 1))
    if tip_target is not None:
        e['tip_mm'] = round(((Wh @ inv @ sl_rest) @ tip_local - Vector(tip_target)).length * 1000, 1)
    WIDTH_SOLVE.append(e)
    return best.x


def put_arm(f, v):
    armR.rotation_euler = v[:3]
    armR.keyframe_insert('rotation_euler', frame=f)
    handR.rotation_euler = v[3:]
    handR.keyframe_insert('rotation_euler', frame=f)


put_arm(1, np.radians([*REST_ARM, 0, 0, 0]))
put_arm(113, np.radians([*REST_ARM, 0, 0, 0]))
crust = PZ + Vector((0, R * .9, .028))
v_grab = solve(126, crust + Vector((0, .005, .012)))
put_arm(126, v_grab)
put_arm(128, v_grab)
sc.frame_set(128)
INV = handR.matrix_world.inverted()
for s in (slices[0], slice_bit):
    c = s.constraints.new('CHILD_OF')
    c.target = handR
    c.inverse_matrix = INV
    c.influence = 0
    c.keyframe_insert('influence', frame=127)
    c.influence = 1
    c.keyframe_insert('influence', frame=128)
for f, a, b in ((1, False, True), (179, True, False)):
    for s, hid in ((slices[0], a), (slice_bit, b)):
        s.hide_render = s.hide_viewport = hid
        s.keyframe_insert('hide_render', frame=f)
        s.keyframe_insert('hide_viewport', frame=f)
for s in (slices[0], slice_bit):
    rig.constant(s)


def mouth_world(f, ahead=0.0):
    sc.frame_set(f)
    return head.matrix_world @ Vector((0, -4 * K - ahead, 2.3 * K))


v_lift = solve(150, PZ + Vector((0, .17, .2)), PZ + Vector((0, .06, .17)), INV, v_grab, hw=3, uw=.4)
put_arm(150, v_lift)
v_turn = solve(162, PZ + Vector((-.05, .02, .33)), PZ + Vector((.0, .1, .36)), INV, v_lift, hw=3, uw=.4)
put_arm(162, v_turn)
v_near = solve(172, mouth_world(172, .03) + Vector((-.03, -.12, -.04)), mouth_world(172, .03), INV, v_turn, hw=3, uw=.4)
put_arm(172, v_near)
v_bite = solve(178, mouth_world(178, -.004) + Vector((-.03, -.12, -.04)), mouth_world(178, -.004), INV, v_near, hw=3, uw=.4)
put_arm(178, v_bite)
v_back = solve(184, mouth_world(184, .05) + Vector((-.03, -.12, -.06)), mouth_world(184, .05), INV, v_bite, hw=3, uw=.4)
put_arm(184, v_back)
put_arm(204, v_back)
v_hold = solve(214, mouth_world(214, .1) + Vector((-.06, -.06, -.16)), mouth_world(214, .1) + Vector((0, 0, -.08)), INV, v_back, hw=3, uw=.4)
put_arm(214, v_hold)
put_arm(240, v_hold)
REPORT['arm_solve'] = WIDTH_SOLVE

# ------------------------------------------------------------------ cheese pull (3 strands, keyed bezier points)
STR = []
cheese = PM[1]
anchors = [((0, .012), (0, -.004)),          # tip -> centre
           ((-.018, .05), (-.026, .046)),    # left cut side -> neighbour slice
           ((.018, .05), (.026, .046))]      # right cut side -> neighbour slice
for j, (pa, pb) in enumerate(anchors):
    cu = bpy.data.curves.new(f'cheese_pull_{j}', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = .0022 - j * .0004
    cu.bevel_resolution = 3
    sp = cu.splines.new('POLY')
    sp.points.add(8)
    o = bpy.data.objects.new(f'cheese_pull_{j}', cu)
    sc.collection.objects.link(o)
    o.data.materials.append(cheese)
    STR.append((o, pa, pb))
for si, (o, pa, pb) in enumerate(STR):
    pts = o.data.splines[0].points
    for f in range(126, 163, 2):
        sc.frame_set(f)
        Ws = slices[0].matrix_world
        A = Ws @ Vector((pa[0], pa[1], .016))
        B = PZ + Vector((pb[0], pb[1], .016))
        sag = min(.05, (A - B).length * .35)
        thin = min(1.0, (f - 126) / 30)
        for q, p_ in enumerate(pts):
            t = q / (len(pts) - 1)
            c = A.lerp(B, t)
            c.z -= sag * 4 * t * (1 - t)
            p_.co = (c.x, c.y, c.z, 1)
            p_.keyframe_insert('co', frame=f)
            p_.radius = 1 - (1 - .22) * thin * math.sin(math.pi * t)
            p_.keyframe_insert('radius', frame=f)
    for f, hid in ((1, True), (128, False), (155 + si * 3, True)):
        o.hide_render = o.hide_viewport = hid
        o.keyframe_insert('hide_render', frame=f)
        o.keyframe_insert('hide_viewport', frame=f)
    for fc in rig.fcurves(o):
        if 'hide' in fc.data_path:
            for kp in fc.keyframe_points:
                kp.interpolation = 'CONSTANT'

# ------------------------------------------------------------------ cameras (6 shots)
CAMS = []


def camera(name, start, keys, lens, focus, fstop):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = fstop
    e = bpy.data.objects.new(name + '_focus', None)
    sc.collection.objects.link(e)
    cd.dof.focus_object = e
    o = bpy.data.objects.new(name, cd)
    sc.collection.objects.link(o)
    for f, loc, tgt, foc in keys:
        o.location = loc
        look_at(o, tgt)
        o.keyframe_insert('location', frame=f)
        o.keyframe_insert('rotation_euler', frame=f)
        e.location = foc
        e.keyframe_insert('location', frame=f)
    m = sc.timeline_markers.new(name, frame=start)
    m.camera = o
    CAMS.append(o)
    return o


hz = lambda f: head.matrix_world @ Vector((0, -4 * K, 4 * K))


def hp(f):
    sc.frame_set(f)
    return hz(f).copy()


c1 = camera('S1_wide', 1, [(1, (-.62, -1.22, 1.12), (.02, .2, 1.0), hp(1)), (54, (-.5, -1.0, 1.08), (.02, .2, 1.0), hp(54))], 35, None, 4.0)
c2 = camera('S2_face_crash', 55, [(55, (.06, -.68, 1.3), hp(60), hp(60)), (84, (.05, -.6, 1.3), hp(80), hp(80))], 62, None, 2.8)
c2.data.lens = 40
c2.data.keyframe_insert('lens', frame=55)
c2.data.lens = 90
c2.data.keyframe_insert('lens', frame=59)
c3 = camera('S3_pizza_macro', 85, [(85, (.1, -.52, .9), PZ + Vector((0, .04, .02)), PZ + Vector((.0, -.05, .018))),
                                    (112, (.19, -.48, .88), PZ + Vector((0, .04, .02)), PZ + Vector((.0, -.05, .018)))], 55, None, 8.0)
c4 = camera('S4_grab_side', 113, [(113, (-.9, -.55, 1.08), (0, .14, .96), PZ + Vector((0, .12, .1))),
                                   (168, (-.86, -.66, 1.12), (0, .14, 1.0), PZ + Vector((0, .1, .2)))], 40, None, 5.6)
c5 = camera('S5_bite_close', 169, [(169, (.5, -.3, 1.26), hp(172) + Vector((0, 0, -.04)), hp(172)),
                                    (204, (.46, -.27, 1.25), hp(190) + Vector((0, 0, -.04)), hp(190))], 62, None, 3.2)
c6 = camera('S6_joy', 205, [(205, (0, -.92, 1.12), (0, .25, 1.08), hp(205)), (240, (0, -1.1, 1.16), (0, .25, 1.1), hp(232))], 42, None, 4.0)
# punch-in shakes (crash zoom, bite)
for cam, (a, b) in ((c2, (55, 66)), (c5, (178, 186))):
    sc.frame_set(a)
    base_rot = cam.rotation_euler.copy()
    rng = np.random.default_rng(a)
    for f in range(a, b + 1):
        amp = .012 * (1 - (f - a) / (b - a))
        sc.frame_set(f)
        r = cam.rotation_euler.copy()
        cam.rotation_euler = (r.x + rng.uniform(-amp, amp), r.y + rng.uniform(-amp, amp) * .5, r.z + rng.uniform(-amp, amp))
        cam.keyframe_insert('rotation_euler', frame=f)
sc.camera = c1

# ------------------------------------------------------------------ render settings (GPU device is set by render.py on the PC)
sc.render.engine = 'CYCLES'
sc.cycles.samples = 96
sc.cycles.adaptive_threshold = .02
sc.cycles.use_denoising = True
sc.cycles.denoising_use_gpu = True
sc.cycles.max_bounces = 8
sc.cycles.volume_step_rate = 2
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = .4
try:   # measured: keeps food + skin colours saturated where AgX washed them out (render/vw_* tests 2026-11-04)
    sc.view_settings.view_transform = 'Khronos PBR Neutral'
except TypeError:
    sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'None'
sc.view_settings.exposure = -1.0
sc.render.image_settings.file_format = 'PNG'

for m_ in bpy.data.materials:            # EEVEE: refraction + volumes render like Cycles
    if hasattr(m_, 'use_raytrace_refraction'):
        m_.use_raytrace_refraction = m_.name in ('glass', 'juice')
sc.eevee.taa_render_samples = 64
for k_, v_ in (('volumetric_tile_size', '2'), ('volumetric_samples', 128), ('volumetric_end', 6.0), ('volumetric_start', .05)):
    if hasattr(sc.eevee, k_):
        setattr(sc.eevee, k_, v_)
for k_ in ('use_raytracing', 'use_shadows', 'use_volumetric_shadows'):
    if hasattr(sc.eevee, k_):
        setattr(sc.eevee, k_, True)
bpy.ops.file.pack_all()
blend = os.path.join(OUT, 'zu_pizza.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
REPORT.update(blend=blend, frames=END, fps=FPS, cams=[c.name for c in CAMS], look=sc.view_settings.look,
              objects=len(bpy.data.objects), slices=NS)
json.dump(REPORT, open(os.path.join(OUT, 'build_report.json'), 'w'), indent=1)
print('BUILD_OK::' + json.dumps(REPORT))
