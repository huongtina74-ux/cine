from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import traceback
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

P = "__CINEFACTORY_JSON__"
ROOT = Path.cwd().resolve()
CACHE_COLL = {}
CACHE_ACT = {}
CACHE_STATS = {
    "collection_hits": 0,
    "collection_misses": 0,
    "action_hits": 0,
    "action_misses": 0,
}


def emit(x):
    print(P + json.dumps(x, ensure_ascii=False, separators=(",", ":")), flush=True)


def argv(flag, default=None):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else default


ROOT = Path(argv("--root", ROOT)).resolve()


def resolve(v):
    if not v:
        return None
    p = Path(v)
    p = (ROOT / p if not p.is_absolute() else p).resolve()
    if p != ROOT and ROOT not in p.parents:
        raise ValueError(f"asset path escapes CineFactory root: {p}")
    return p


def xyz(v, d=(0, 0, 0)):
    if not v:
        return d
    if isinstance(v, dict):
        return (float(v.get("x", d[0])), float(v.get("y", d[1])), float(v.get("z", d[2])))
    return tuple(v)


def apply(obj, t):
    if not t:
        return
    obj.location = xyz(t.get("location"))
    obj.rotation_euler = xyz(t.get("rotation_euler"))
    obj.scale = xyz(t.get("scale"), (1, 1, 1))


def safe_set(obj, name, value):
    if obj is None or not hasattr(obj, name):
        return False
    try:
        setattr(obj, name, value)
        return True
    except Exception:
        return False


def clear_scene_instances():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    root = bpy.context.scene.collection
    for c in list(root.children):
        if c.name.startswith("CF_INST_"):
            try:
                root.children.unlink(c)
            except Exception:
                pass
    for c in list(bpy.data.collections):
        if c.users == 0 and not c.name.startswith("CF_CACHE_"):
            bpy.data.collections.remove(c)


def material(name, color, metallic=0.0, roughness=.55, emission=None, emission_strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF") if m.node_tree else None
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*color, 1)
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        elif emission and "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*emission, 1)
        if emission_strength and "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    m.diffuse_color = (*color, 1)
    return m


def _pixel_material(name, base, accent, *, roughness=.72):
    """Create a tiny deterministic nearest-neighbor texture for voxel assets."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    tree = m.node_tree
    tree.nodes.clear()
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    tex = tree.nodes.new("ShaderNodeTexImage")
    image = bpy.data.images.get(name + "_16PX") or bpy.data.images.new(name + "_16PX", width=16, height=16)
    pixels = []
    for y in range(16):
        for x in range(16):
            stripe = (x // 4 + y // 4) % 2 == 0
            c = base if stripe else accent
            pixels.extend((*c, 1.0))
    image.pixels = pixels
    image.pack()
    tex.image = image
    tex.interpolation = "Closest"
    tex.extension = "CLIP"
    bsdf.inputs["Roughness"].default_value = roughness
    tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    m.diffuse_color = (*base, 1)
    return m


def style_palette(rig):
    identity = rig.get("identity") or {}
    style = rig.get("style", "DEBUG_BLOCK")
    palettes = {
        "blue": (.12, .34, .82), "orange": (.92, .28, .08), "navy": (.06, .10, .26),
        "dark": (.06, .07, .10), "green": (.10, .52, .24), "charcoal": (.12, .14, .18),
        "blonde": (.92, .68, .20), "purple": (.54, .18, .72), "tan": (.58, .38, .20),
        "brown": (.30, .12, .05), "teal": (.05, .52, .52), "red": (.78, .10, .08),
        "yellow": (.95, .68, .08), "slate": (.22, .28, .38), "coral": (.88, .25, .22),
        "olive": (.28, .34, .12), "black": (.015, .02, .03),
    }
    skin = {
        "bright": (.82, .52, .32), "warm": (.62, .31, .18), "light": (.94, .68, .48),
        "dark": (.25, .12, .07),
    }.get(identity.get("face"), (.72, .42, .25))
    def pick(key, fallback):
        return palettes.get(identity.get(key), fallback)
    return {
        "skin": skin,
        "hair": pick("hair", (.10, .08, .06)),
        "shirt": pick("shirt", (.20, .42, .72)),
        "pants": pick("pants", (.16, .18, .25)),
        "accent": pick("shirt", (.80, .35, .10)),
        "style": style,
    }


def voxel_material(name, base, accent):
    return _pixel_material(name, base, accent, roughness=.82)


def roblox_material(name, color, roughness=.48):
    return material(name, color, roughness=roughness)


def add_bevel(obj, width=.03, segments=2):
    if obj.type != "MESH":
        return
    mod = obj.modifiers.new(name="CF_Bevel", type="BEVEL")
    mod.width = width
    mod.segments = segments


def cube(name, loc, scale, mat, parent=None, bevel=.02):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(mat)
    o.parent = parent
    if bevel:
        add_bevel(o, bevel)
    return o


def proc_minecraft_classroom(scale=1.0):
    floor = voxel_material("MC_Floor", (.20, .25, .30), (.16, .20, .25))
    wall = voxel_material("MC_Wall", (.64, .70, .76), (.50, .57, .64))
    ceiling = voxel_material("MC_Ceiling", (.78, .80, .76), (.66, .69, .68))
    wood = voxel_material("MC_Wood", (.42, .20, .08), (.58, .30, .12))
    trim = voxel_material("MC_Trim", (.20, .12, .08), (.34, .20, .10))
    board = voxel_material("MC_Board", (.04, .25, .18), (.02, .16, .11))
    glass = material("MC_Glass", (.16, .46, .72), roughness=.22)
    white = voxel_material("MC_Paper", (.92, .88, .72), (.78, .74, .60))
    cube("MC_FLOOR", (0, 0, -.15), (6.2 * scale, 5.2 * scale, .15), floor, bevel=0)
    cube("MC_BACK_WALL", (0, 5.05 * scale, 2.6 * scale), (6.2 * scale, .12, 2.7 * scale), wall, bevel=0)
    cube("MC_LEFT_WALL", (-6.1 * scale, 0, 2.6 * scale), (.12, 5.2 * scale, 2.7 * scale), wall, bevel=0)
    cube("MC_RIGHT_WALL", (6.1 * scale, 0, 2.6 * scale), (.12, 5.2 * scale, 2.7 * scale), wall, bevel=0)
    cube("MC_CEILING", (0, 0, 5.3 * scale), (6.2 * scale, 5.2 * scale, .12), ceiling, bevel=0)
    cube("MC_BOARD", (0, 4.84 * scale, 2.55 * scale), (2.75 * scale, .06, .95 * scale), board, bevel=0)
    cube("MC_BOARD_TRIM", (0, 4.72 * scale, 1.55 * scale), (2.95 * scale, .08, .08), trim, bevel=0)
    cube("MC_DOOR", (-4.65 * scale, 4.82 * scale, 1.45 * scale), (.80 * scale, .08, 1.45 * scale), trim, bevel=0)
    for x in (-3.0, 0.0, 3.0):
        cube(f"MC_WINDOW_{x}", (x * scale, 4.80 * scale, 3.45 * scale), (1.05 * scale, .06, .78 * scale), glass, bevel=0)
        cube(f"MC_WINDOW_TOP_{x}", (x * scale, 4.68 * scale, 4.28 * scale), (1.16 * scale, .08, .07), trim, bevel=0)
        cube(f"MC_WINDOW_SIDE_{x}", ((x - 1.1) * scale, 4.68 * scale, 3.45 * scale), (.07, .08, .88 * scale), trim, bevel=0)
        cube(f"MC_WINDOW_SIDE2_{x}", ((x + 1.1) * scale, 4.68 * scale, 3.45 * scale), (.07, .08, .88 * scale), trim, bevel=0)
    for row, y in enumerate((-1.0, 1.0, 2.7)):
        for col, x in enumerate((-2.5, 0.0, 2.5)):
            cube(f"MC_DESK_{row}_{col}", (x * scale, y * scale, .72 * scale), (.72 * scale, .45 * scale, .08), wood, bevel=0)
            cube(f"MC_DESK_LEG_{row}_{col}", (x * scale, (y + .28) * scale, .34 * scale), (.07, .07, .34 * scale), trim, bevel=0)
            cube(f"MC_CHAIR_{row}_{col}", (x * scale, (y - .78) * scale, .58 * scale), (.43 * scale, .08, .56 * scale), wood, bevel=0)
    for x in (-4.8, 4.8):
        cube(f"MC_SHELF_{x}", (x * scale, 3.0 * scale, 1.55 * scale), (.48 * scale, .36 * scale, 1.55 * scale), trim, bevel=0)
        for z in (0.65, 1.35, 2.05):
            cube(f"MC_BOOKS_{x}_{z}", (x * scale, 2.58 * scale, z * scale), (.35 * scale, .08, .18 * scale), white, bevel=0)


def proc_roblox_classroom(scale=1.0):
    floor = roblox_material("RBX_Floor", (.22, .28, .38), .62)
    wall = roblox_material("RBX_Wall", (.72, .78, .88), .56)
    ceiling = roblox_material("RBX_Ceiling", (.92, .93, .96), .52)
    wood = roblox_material("RBX_Wood", (.56, .30, .14), .50)
    trim = roblox_material("RBX_Trim", (.12, .17, .26), .42)
    board = roblox_material("RBX_Board", (.06, .24, .31), .48)
    glass = roblox_material("RBX_Glass", (.30, .66, .88), .20)
    accent = roblox_material("RBX_Accent", (.92, .37, .20), .44)
    cube("RBX_FLOOR", (0, 0, -.15), (6.2 * scale, 5.2 * scale, .15), floor, bevel=.08)
    cube("RBX_BACK_WALL", (0, 5.05 * scale, 2.6 * scale), (6.2 * scale, .12, 2.7 * scale), wall, bevel=.08)
    cube("RBX_LEFT_WALL", (-6.1 * scale, 0, 2.6 * scale), (.12, 5.2 * scale, 2.7 * scale), wall, bevel=.08)
    cube("RBX_RIGHT_WALL", (6.1 * scale, 0, 2.6 * scale), (.12, 5.2 * scale, 2.7 * scale), wall, bevel=.08)
    cube("RBX_CEILING", (0, 0, 5.3 * scale), (6.2 * scale, 5.2 * scale, .12), ceiling, bevel=.06)
    cube("RBX_BOARD", (0, 4.84 * scale, 2.55 * scale), (2.8 * scale, .07, .98 * scale), board, bevel=.06)
    cube("RBX_BOARD_TRIM", (0, 4.70 * scale, 1.55 * scale), (3.0 * scale, .09, .08), accent, bevel=.03)
    cube("RBX_DOOR", (-4.65 * scale, 4.82 * scale, 1.45 * scale), (.82 * scale, .09, 1.45 * scale), trim, bevel=.08)
    for x in (-3.0, 0.0, 3.0):
        cube(f"RBX_WINDOW_{x}", (x * scale, 4.80 * scale, 3.45 * scale), (1.08 * scale, .07, .80 * scale), glass, bevel=.05)
        cube(f"RBX_WINDOW_FRAME_{x}", (x * scale, 4.68 * scale, 3.45 * scale), (1.18 * scale, .09, .90 * scale), trim, bevel=.04)
        cube(f"RBX_WINDOW_INSET_{x}", (x * scale, 4.56 * scale, 3.45 * scale), (1.03 * scale, .04, .75 * scale), glass, bevel=.03)
    for row, y in enumerate((-1.0, 1.0, 2.7)):
        for col, x in enumerate((-2.5, 0.0, 2.5)):
            cube(f"RBX_DESK_{row}_{col}", (x * scale, y * scale, .72 * scale), (.76 * scale, .46 * scale, .10), wood, bevel=.07)
            cube(f"RBX_DESK_LEG_{row}_{col}", (x * scale, (y + .28) * scale, .34 * scale), (.09, .09, .34 * scale), trim, bevel=.03)
            cube(f"RBX_CHAIR_{row}_{col}", (x * scale, (y - .78) * scale, .58 * scale), (.46 * scale, .10, .56 * scale), accent, bevel=.07)
    for x in (-4.8, 4.8):
        cube(f"RBX_LOCKER_{x}", (x * scale, 3.0 * scale, 1.55 * scale), (.52 * scale, .40 * scale, 1.55 * scale), trim, bevel=.08)
        for z in (.70, 1.55, 2.35):
            cube(f"RBX_LOCKER_STRIPE_{x}_{z}", (x * scale, 2.57 * scale, z * scale), (.40 * scale, .04, .05), accent, bevel=.02)


def proc_room(scene):
    scale = float(scene.get("world_scale", 1.0))
    kind = scene.get("procedural_kind", "room")
    style = scene.get("style", "DEBUG_BLOCK")
    if kind == "classroom" and style == "MINECRAFT":
        proc_minecraft_classroom(scale)
        return
    if kind == "classroom" and style == "ROBLOX":
        proc_roblox_classroom(scale)
        return
    floor = material("CF_Floor", (.18, .21, .24), roughness=.7)
    wall = material("CF_Wall", (.36, .43, .52), roughness=.65)
    accent = material("CF_Accent", (.82, .47, .20), roughness=.5)
    wood = material("CF_Wood", (.34, .19, .10), roughness=.62)
    green = material("CF_Green", (.14, .42, .23), roughness=.72)
    road = material("CF_Road", (.08, .09, .11), roughness=.88)
    stone = material("CF_Stone", (.28, .30, .34), roughness=.82)

    if kind == "classroom":
        cube("CF_FLOOR", (0, 0, -.15), (6.2*scale, 5.2*scale, .15), floor, bevel=.04)
        cube("CF_BACK_WALL", (0, 5.05*scale, 2.5*scale), (6.2*scale, .12, 2.6*scale), wall, bevel=.03)
        cube("CF_BOARD", (0, 4.86*scale, 2.55*scale), (2.8*scale, .05, 1.0*scale), green, bevel=.04)
        for row_y in (-.3, 1.35):
            for x in (-2.2, 0, 2.2):
                cube(f"CF_DESK_{x}_{row_y}", (x*scale, row_y*scale, .72*scale), (.72*scale, .42*scale, .06), wood, bevel=.04)
                cube(f"CF_DESKLEG_{x}_{row_y}", (x*scale, row_y*scale, .34*scale), (.08, .08, .35*scale), stone, bevel=.02)
        cube("CF_TEACHER_DESK", (0, 3.2*scale, .78*scale), (1.2*scale, .48*scale, .08), wood, bevel=.05)
        return

    if kind == "street":
        cube("CF_GROUND", (0, 0, -.18), (8.0*scale, 9.0*scale, .18), floor, bevel=.02)
        cube("CF_ROAD", (0, 0, -.01), (3.1*scale, 9.0*scale, .04), road, bevel=.01)
        lane = material("CF_Lane", (.92, .78, .22), roughness=.6)
        for y in range(-7, 8, 3):
            cube(f"CF_LANE_{y}", (0, y*scale, .045), (.08, .65*scale, .015), lane, bevel=.005)
        for side in (-1, 1):
            x = side*5.4*scale
            for y in (-5.5, -.8, 4.0):
                h = 1.8 + (abs(int(y*10)) % 3)*.45
                cube(f"CF_BUILD_{side}_{y}", (x, y*scale, h), (1.45*scale, 1.7*scale, h), wall if y < 0 else accent, bevel=.06)
        return

    if kind == "arena":
        cube("CF_ARENA_FLOOR", (0, 0, -.16), (6.0*scale, 6.0*scale, .16), stone, bevel=.04)
        for i in range(12):
            a = i*math.tau/12
            x, y = math.cos(a)*5.3*scale, math.sin(a)*5.3*scale
            cube(f"CF_ARENA_PILLAR_{i}", (x, y, 1.4*scale), (.22,.22,1.4*scale), accent, bevel=.04)
        cube("CF_ARENA_CENTER", (0,0,.03), (2.4*scale,2.4*scale,.05), floor, bevel=.05)
        return

    cube("CF_FLOOR", (0, 0, -.15), (6.0*scale, 5.0*scale, .15), floor, bevel=.04)
    cube("CF_BACK_WALL", (0, 4.9*scale, 2.4*scale), (6.0*scale, .12, 2.5*scale), wall, bevel=.03)
    cube("CF_LEFT_WALL", (-5.9*scale, 0, 2.4*scale), (.12, 5.0*scale, 2.5*scale), wall, bevel=.03)
    cube("CF_RIGHT_WALL", (5.9*scale, 0, 2.4*scale), (.12, 5.0*scale, 2.5*scale), wall, bevel=.03)
    cube("CF_STAGE", (0, 2.7*scale, .18), (2.3*scale, 1.0*scale, .18), accent, bevel=.06)
    for x in (-4.6, 4.6):
        cube(f"CF_PILLAR_{x}", (x*scale, 3.8*scale, 1.7*scale), (.28*scale, .28*scale, 1.7*scale), accent, bevel=.04)

def load_collection(path, name=None):
    key = (str(path), name or "")
    if key not in CACHE_COLL:
        CACHE_STATS["collection_misses"] += 1
        with bpy.data.libraries.load(str(path), link=False) as (src, dst):
            if not src.collections:
                raise ValueError(f"no collections in {path}")
            chosen = name if name in src.collections else src.collections[0]
            dst.collections = [chosen]
        c = dst.collections[0]
        c.name = "CF_CACHE_" + hashlib.sha1((str(path)+str(name)).encode()).hexdigest()[:10]
        CACHE_COLL[key] = c
    else:
        CACHE_STATS["collection_hits"] += 1
    templ = CACHE_COLL[key]
    inst = bpy.data.collections.new("CF_INST_" + templ.name + "_" + str(len(bpy.data.collections)))
    bpy.context.scene.collection.children.link(inst)
    mapping = {}
    for o in templ.all_objects:
        cp = o.copy()
        unique = o.type == "ARMATURE" or (o.type == "MESH" and getattr(o.data, "shape_keys", None) is not None)
        if o.data is not None:
            cp.data = o.data.copy() if unique else o.data
        inst.objects.link(cp)
        mapping[o] = cp
    for o, cp in mapping.items():
        if o.parent in mapping:
            cp.parent = mapping[o.parent]
    return inst


def build_scene(scene):
    if scene.get("source_path"):
        c = load_collection(resolve(scene["source_path"]), scene.get("collection"))
        return {"mode": "library", "collection": c}
    proc_room(scene)
    return {"mode": "procedural", "collection": None}


def _face_parts(aid, root, head_z, front_y, skin, hair, *, voxel=False, accessory=None):
    dark = voxel_material("MC_FACE_" + aid, (.015, .02, .025), (.08, .04, .03)) if voxel else roblox_material("RBX_FACE_" + aid, (.02, .025, .04), .32)
    white = material("FACE_WHITE_" + aid, (.96, .96, .90), roughness=.28)
    parts = {
        "eye.R": cube(aid + "_eyeR", (.17, front_y, head_z + .10), (.065, .025, .075), dark, root, 0 if voxel else .008),
        "eye.L": cube(aid + "_eyeL", (-.17, front_y, head_z + .10), (.065, .025, .075), dark, root, 0 if voxel else .008),
        "mouth": cube(aid + "_mouth", (0, front_y - .01, head_z - .15), (.16, .025, .035), dark, root, 0 if voxel else .006),
    }
    if accessory == "glasses":
        cube(aid + "_glassesR", (.17, front_y - .035, head_z + .10), (.12, .03, .11), white, root, .01)
        cube(aid + "_glassesL", (-.17, front_y - .035, head_z + .10), (.12, .03, .11), white, root, .01)
        cube(aid + "_glassesBridge", (0, front_y - .04, head_z + .10), (.08, .025, .025), white, root, .005)
    return parts


def proc_minecraft_actor(aid, t, rig):
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    root = bpy.context.object
    root.name = f"CF_ACTOR_{aid}"
    apply(root, t)
    height = float(rig.get("height_scale", 1.0))
    root.scale = tuple(v * height for v in root.scale)
    p = style_palette(rig)
    skin = voxel_material("MC_SKIN_" + aid, p["skin"], tuple(min(1.0, c * .72 + .05) for c in p["skin"]))
    hair = voxel_material("MC_HAIR_" + aid, p["hair"], tuple(min(1.0, c * .72 + .03) for c in p["hair"]))
    shirt = voxel_material("MC_SHIRT_" + aid, p["shirt"], tuple(min(1.0, c * .68 + .04) for c in p["shirt"]))
    pants = voxel_material("MC_PANTS_" + aid, p["pants"], tuple(min(1.0, c * .68 + .03) for c in p["pants"]))
    parts = {
        "torso": cube(aid + "_torso", (0, 0, 1.45), (.50, .30, .65), shirt, root, 0),
        "head": cube(aid + "_head", (0, 0, 2.38), (.50, .50, .50), skin, root, 0),
        "arm.R": cube(aid + "_armR", (.70, 0, 1.48), (.19, .19, .62), shirt, root, 0),
        "arm.L": cube(aid + "_armL", (-.70, 0, 1.48), (.19, .19, .62), shirt, root, 0),
        "leg.R": cube(aid + "_legR", (.25, 0, .52), (.24, .24, .52), pants, root, 0),
        "leg.L": cube(aid + "_legL", (-.25, 0, .52), (.24, .24, .52), pants, root, 0),
    }
    # Hard-edged hair blocks make the silhouette read as a voxel skin rather than a mannequin.
    cube(aid + "_hairTop", (0, -.02, 2.90), (.52, .52, .12), hair, root, 0)
    if rig.get("identity", {}).get("hair") in {"blue", "red", "blonde"}:
        cube(aid + "_hairSide", (.43, -.03, 2.62), (.10, .47, .28), hair, root, 0)
    parts.update(_face_parts(aid, root, 2.38, -.505, skin, hair, voxel=True))
    parts["hand.R"] = parts["arm.R"]
    parts["hand.L"] = parts["arm.L"]
    return {"root": root, "armature": None, "parts": parts, "collection": None, "style": "MINECRAFT"}


def proc_roblox_r6_actor(aid, t, rig):
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    root = bpy.context.object
    root.name = f"CF_ACTOR_{aid}"
    apply(root, t)
    height = float(rig.get("height_scale", 1.0))
    root.scale = tuple(v * height for v in root.scale)
    p = style_palette(rig)
    skin = roblox_material("RBX_SKIN_" + aid, p["skin"], .46)
    shirt = roblox_material("RBX_SHIRT_" + aid, p["shirt"], .50)
    pants = roblox_material("RBX_PANTS_" + aid, p["pants"], .56)
    hair = roblox_material("RBX_HAIR_" + aid, p["hair"], .42)
    parts = {
        "Torso": cube(aid + "_Torso", (0, 0, 1.42), (.52, .32, .62), shirt, root, .055),
        "Head": cube(aid + "_Head", (0, 0, 2.36), (.47, .47, .47), skin, root, .09),
        "RightArm": cube(aid + "_RightArm", (.72, 0, 1.42), (.19, .20, .58), skin, root, .06),
        "LeftArm": cube(aid + "_LeftArm", (-.72, 0, 1.42), (.19, .20, .58), skin, root, .06),
        "RightLeg": cube(aid + "_RightLeg", (.26, 0, .52), (.25, .25, .52), pants, root, .06),
        "LeftLeg": cube(aid + "_LeftLeg", (-.26, 0, .52), (.25, .25, .52), pants, root, .06),
    }
    cube(aid + "_Hair", (0, -.01, 2.82), (.49, .49, .17), hair, root, .10)
    if rig.get("accessories") and "cap" in rig["accessories"]:
        cube(aid + "_CapBrim", (0, -.40, 2.72), (.34, .18, .05), hair, root, .03)
    parts.update(_face_parts(aid, root, 2.36, -.475, skin, hair, accessory=(rig.get("accessories") or [None])[0]))
    parts["arm.R"] = parts["RightArm"]
    parts["arm.L"] = parts["LeftArm"]
    parts["leg.R"] = parts["RightLeg"]
    parts["leg.L"] = parts["LeftLeg"]
    parts["hand.R"] = parts["RightArm"]
    parts["hand.L"] = parts["LeftArm"]
    return {"root": root, "armature": None, "parts": parts, "collection": None, "style": "ROBLOX_R6"}


def proc_roblox_r15_actor(aid, t, rig):
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    root = bpy.context.object
    root.name = f"CF_ACTOR_{aid}"
    apply(root, t)
    p = style_palette(rig)
    skin = roblox_material("R15_SKIN_" + aid, p["skin"], .46)
    shirt = roblox_material("R15_SHIRT_" + aid, p["shirt"], .50)
    pants = roblox_material("R15_PANTS_" + aid, p["pants"], .56)
    hair = roblox_material("R15_HAIR_" + aid, p["hair"], .42)
    parts = {
        "UpperTorso": cube(aid + "_UpperTorso", (0, 0, 1.64), (.50, .30, .42), shirt, root, .06),
        "LowerTorso": cube(aid + "_LowerTorso", (0, 0, 1.08), (.46, .29, .28), shirt, root, .055),
        "Head": cube(aid + "_Head", (0, 0, 2.40), (.46, .46, .46), skin, root, .10),
        "UpperArm.R": cube(aid + "_UpperArmR", (.64, 0, 1.68), (.16, .17, .34), skin, root, .05),
        "LowerArm.R": cube(aid + "_LowerArmR", (.64, 0, 1.24), (.15, .16, .28), skin, root, .05),
        "Hand.R": cube(aid + "_HandR", (.64, -.01, .90), (.16, .18, .14), skin, root, .06),
        "UpperArm.L": cube(aid + "_UpperArmL", (-.64, 0, 1.68), (.16, .17, .34), skin, root, .05),
        "LowerArm.L": cube(aid + "_LowerArmL", (-.64, 0, 1.24), (.15, .16, .28), skin, root, .05),
        "Hand.L": cube(aid + "_HandL", (-.64, -.01, .90), (.16, .18, .14), skin, root, .06),
        "UpperLeg.R": cube(aid + "_UpperLegR", (.24, 0, .72), (.22, .23, .34), pants, root, .05),
        "LowerLeg.R": cube(aid + "_LowerLegR", (.24, 0, .29), (.21, .22, .27), pants, root, .05),
        "Foot.R": cube(aid + "_FootR", (.24, -.10, .08), (.23, .34, .12), pants, root, .05),
        "UpperLeg.L": cube(aid + "_UpperLegL", (-.24, 0, .72), (.22, .23, .34), pants, root, .05),
        "LowerLeg.L": cube(aid + "_LowerLegL", (-.24, 0, .29), (.21, .22, .27), pants, root, .05),
        "Foot.L": cube(aid + "_FootL", (-.24, -.10, .08), (.23, .34, .12), pants, root, .05),
    }
    cube(aid + "_Hair", (0, -.01, 2.86), (.48, .48, .16), hair, root, .10)
    parts.update(_face_parts(aid, root, 2.40, -.465, skin, hair))
    parts["arm.R"] = parts["LowerArm.R"]
    parts["arm.L"] = parts["LowerArm.L"]
    parts["leg.R"] = parts["LowerLeg.R"]
    parts["leg.L"] = parts["LowerLeg.L"]
    return {"root": root, "armature": None, "parts": parts, "collection": None, "style": "ROBLOX_R15"}


def proc_actor(aid, t, rig=None):
    rig = rig or {"style": "DEBUG_BLOCK", "identity": {}}
    style = rig.get("style", "DEBUG_BLOCK")
    if style == "MINECRAFT":
        return proc_minecraft_actor(aid, t, rig)
    if style == "ROBLOX_R6":
        return proc_roblox_r6_actor(aid, t, rig)
    if style == "ROBLOX_R15":
        return proc_roblox_r15_actor(aid, t, rig)
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    root = bpy.context.object
    root.name = f"CF_ACTOR_{aid}"
    apply(root, t)
    h = hashlib.sha256(aid.encode()).digest()
    c = (.25+h[0]/510, .25+h[1]/510, .25+h[2]/510)
    skin = material("M_"+aid, c, roughness=.48)
    dark = material("D_"+aid, (.025, .025, .03), roughness=.35)
    pants = material("P_"+aid, (c[0]*.45, c[1]*.45, c[2]*.45), roughness=.6)
    parts = {
        "torso": cube(aid+"_torso", (0, 0, 1.38), (.46, .29, .64), skin, root, .045),
        "head": cube(aid+"_head", (0, 0, 2.26), (.43, .39, .43), skin, root, .055),
        "arm.R": cube(aid+"_armR", (.63, 0, 1.38), (.17, .17, .59), skin, root, .035),
        "arm.L": cube(aid+"_armL", (-.63, 0, 1.38), (.17, .17, .59), skin, root, .035),
        "leg.R": cube(aid+"_legR", (.23, 0, .48), (.20, .22, .48), pants, root, .035),
        "leg.L": cube(aid+"_legL", (-.23, 0, .48), (.20, .22, .48), pants, root, .035),
        "eye.R": cube(aid+"_eyeR", (.15, -.395, 2.35), (.06, .028, .07), dark, root, .008),
        "eye.L": cube(aid+"_eyeL", (-.15, -.395, 2.35), (.06, .028, .07), dark, root, .008),
        "mouth": cube(aid+"_mouth", (0, -.40, 2.09), (.16, .025, .035), dark, root, .006),
    }
    parts["hand.R"] = parts["arm.R"]
    parts["hand.L"] = parts["arm.L"]
    return {"root": root, "armature": None, "parts": parts, "collection": None, "style": "DEBUG_BLOCK"}


def ext_actor(aid, rig, t):
    p = resolve(rig.get("source_path"))
    c = load_collection(p, rig.get("collection"))
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    root = bpy.context.object
    root.name = f"CF_ACTOR_{aid}"
    apply(root, t)
    arm = None
    for o in c.all_objects:
        if o.parent is None:
            o.parent = root
        if o.type == "ARMATURE" and arm is None:
            arm = o
    if arm is None:
        raise ValueError("external rig has no armature")
    return {
        "root": root,
        "armature": arm,
        "parts": {},
        "collection": c,
        "style": rig.get("style", "EXTERNAL"),
    }


def load_action(path, name):
    key = (str(path), name)
    if key in CACHE_ACT:
        CACHE_STATS["action_hits"] += 1
        return CACHE_ACT[key]
    CACHE_STATS["action_misses"] += 1
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        if name not in src.actions:
            raise ValueError(f"action {name} missing")
        dst.actions = [name]
    CACHE_ACT[key] = dst.actions[0]
    return dst.actions[0]


def fr(s, fps):
    return max(1, 1 + round(float(s) * fps))


def kf(o, path, f):
    o.keyframe_insert(data_path=path, frame=f)


def action(actor, cue, clip, fps):
    st = fr(cue.get("start_seconds", 0), fps)
    en = fr(cue.get("end_seconds", cue.get("start_seconds", 0)+.5), fps)
    mid = (st+en)//2
    root = actor["root"]
    name = cue.get("clip_id")
    inten = float(cue.get("intensity", 1))
    if clip.get("source_path"):
        arm = actor["armature"]
        if arm is None:
            return
        act = load_action(resolve(clip["source_path"]), clip["action_name"])
        arm.animation_data_create()
        tr = arm.animation_data.nla_tracks.new()
        tr.name = "CF_"+name
        strip = tr.strips.new(tr.name, st, act)
        strip.action_frame_start = act.frame_range[0]
        strip.action_frame_end = act.frame_range[1]
        if hasattr(strip, "scale") and en > st and act.frame_range[1] > act.frame_range[0]:
            strip.scale = max(.01, (en-st)/(act.frame_range[1]-act.frame_range[0]))
        return

    if name in {"shock_recoil", "flinch"}:
        kf(root, "rotation_euler", st)
        root.rotation_euler.x -= .22*inten
        root.location.z += .06*inten
        kf(root, "rotation_euler", mid); kf(root, "location", mid)
        root.rotation_euler.x += .22*inten
        root.location.z -= .06*inten
        kf(root, "rotation_euler", en); kf(root, "location", en)
    elif name in {"point", "wave", "push", "grab"} and actor["parts"].get("arm.R"):
        a = actor["parts"]["arm.R"]
        kf(a, "rotation_euler", st)
        a.rotation_euler.x -= 1.15*inten
        if name == "wave":
            a.rotation_euler.z += .35*inten
        kf(a, "rotation_euler", mid)
        a.rotation_euler.z -= .7*inten if name == "wave" else 0
        kf(a, "rotation_euler", en)
    elif name in {"walk", "run"}:
        stride = .72 if name == "walk" else 1.25
        leg_r = actor["parts"].get("leg.R"); leg_l = actor["parts"].get("leg.L")
        arm_r = actor["parts"].get("arm.R"); arm_l = actor["parts"].get("arm.L")
        for obj, sign in ((leg_r, 1), (leg_l, -1), (arm_r, -1), (arm_l, 1)):
            if obj:
                kf(obj, "rotation_euler", st)
                obj.rotation_euler.x = sign*stride*inten
                kf(obj, "rotation_euler", mid)
                obj.rotation_euler.x = -sign*stride*inten
                kf(obj, "rotation_euler", en)
        kf(root, "location", st)
        root.location.y += (1.0 if name == "walk" else 1.8) * inten
        kf(root, "location", en)
    elif name == "jump":
        kf(root, "location", st)
        root.location.z += 1.05*inten
        kf(root, "location", mid)
        root.location.z -= 1.05*inten
        kf(root, "location", en)
    elif name == "fall":
        kf(root, "rotation_euler", st)
        root.rotation_euler.x += 1.35*inten
        kf(root, "rotation_euler", en)
    elif name == "turn_head" and actor["parts"].get("head"):
        h = actor["parts"]["head"]
        kf(h, "rotation_euler", st)
        h.rotation_euler.z += .55*inten
        kf(h, "rotation_euler", mid)
        h.rotation_euler.z -= .25*inten
        kf(h, "rotation_euler", en)
    else:
        kf(root, "location", st)
        root.location.z += .05*inten
        kf(root, "location", mid)
        root.location.z -= .05*inten
        kf(root, "location", en)


def expression(actor, rig, cue, fps):
    channels = cue.get("channels", {})
    targets = []
    if actor.get("collection"):
        targets = [o for o in actor["collection"].all_objects if o.type == "MESH" and o.data.shape_keys]
    if targets:
        for ch, val in channels.items():
            keyname = rig.get("expression_map", {}).get(ch, ch)
            for mesh in targets:
                key = mesh.data.shape_keys.key_blocks.get(keyname)
                if key:
                    start = fr(cue.get("start_seconds", 0), fps)
                    end = fr(cue.get("end_seconds", .5), fps)
                    key.value = 0
                    key.keyframe_insert("value", frame=max(1, start-1))
                    key.value = max(0, min(1, float(val)))
                    key.keyframe_insert("value", frame=start)
                    key.keyframe_insert("value", frame=end)
                    key.value = 0
                    key.keyframe_insert("value", frame=end+1)
    else:
        # Procedural fallback maps expressions to eyes/head/mouth transforms.
        mouth = actor["parts"].get("mouth")
        head = actor["parts"].get("head")
        st = fr(cue.get("start_seconds", 0), fps); en = fr(cue.get("end_seconds", .5), fps)
        smile = float(channels.get("mouth_smile", 0)); jaw = float(channels.get("jaw_open", 0)); wide = float(channels.get("eye_wide", 0))
        if mouth:
            kf(mouth, "scale", st); mouth.scale.x = .16*(1+.55*smile); mouth.scale.z = .035*(1+2.2*jaw); kf(mouth, "scale", st+1); kf(mouth, "scale", en)
        if head and wide:
            kf(head, "scale", st); head.scale.z = .43*(1+.03*wide); kf(head, "scale", st+1); kf(head, "scale", en)



def apply_speech_visemes(plan, actors, fps):
    """Apply bounded SAPI-timed mouth keys to procedural Blender faces.

    An animation-conformance record is not independently measured lip-sync.
    Fail if an actor has no actual mouth control instead of inventing success.
    """
    rows = plan.get("speech_viseme_tracks") or []
    if not rows:
        return []
    if len(rows) > 20:
        raise ValueError("TOO_MANY_SPEECH_VISEME_TRACKS")
    observed = []
    duration = float(plan.get("duration_seconds", 0))
    previous: dict[str, float] = {}
    for row in sorted(rows, key=lambda r: r["line_start_seconds"]):
        aid = row["actor_id"]
        if aid not in actors:
            raise ValueError("VISEME_UNKNOWN_ACTOR:" + aid)
        if row.get("event_source") != "SYNTHESIZER_VISEME_REACHED":
            raise ValueError("VISEME_PROVENANCE_INVALID")
        digest = str(row.get("audio_sha256") or "")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower()):
            raise ValueError("VISEME_AUDIO_HASH_INVALID")
        start = float(row["line_start_seconds"])
        stop = float(row["timeline_end_seconds"])
        if not 0 <= start < stop <= duration + 1e-4:
            raise ValueError("VISEME_TIMELINE_OUT_OF_SHOT")
        if start < previous.get(aid, 0.) - 1e-6:
            raise ValueError("VISEME_OVERLAPPING_ACTOR_LINES:" + aid)
        previous[aid] = stop
        mouth = actors[aid]["parts"].get("mouth")
        if mouth is None:
            raise ValueError("VISEME_ACTOR_MOUTH_CONTROL_MISSING:" + aid)
        events = row.get("viseme_events") or []
        if not events or len(events) > 300:
            raise ValueError("VISEME_EVENT_COUNT_INVALID")
        current = -1.
        # Insert baseline before the first sound so non-speakers stay closed.
        first = max(1, fr(start, fps) - 1)
        mouth.scale.x = .16
        mouth.scale.z = .012
        mouth.keyframe_insert("scale", frame=first)
        peak_jaw = 0.
        for item in events:
            offset = float(item["time_seconds"])
            jaw = float(item["jaw_open"])
            width = float(item["mouth_width"])
            if not current <= offset <= float(row["audio_duration_seconds"]) + .12:
                raise ValueError("VISEME_EVENT_NONMONOTONIC_OR_OUTSIDE_AUDIO")
            if not 0 <= jaw <= 1 or not 0 <= width <= 1:
                raise ValueError("VISEME_CHANNEL_OUT_OF_RANGE")
            current = offset
            frame = max(1, fr(start + offset, fps))
            mouth.scale.z = .012 + (.12 * jaw)
            mouth.scale.x = .12 + (.13 * width)
            mouth.keyframe_insert("scale", frame=frame)
            peak_jaw = max(peak_jaw, jaw)
        final = min(fr(stop, fps), fr(duration, fps))
        mouth.scale.x = .16
        mouth.scale.z = .012
        mouth.keyframe_insert("scale", frame=final)
        observed.append({
            "line_id":row["line_id"],"actor_id":aid,
            "event_count":len(events),"peak_jaw":peak_jaw,
            "start_seconds":start,"end_seconds":stop,
            "source":"SYNTHESIZER_VISEME_REACHED",
            "audio_sha256":digest,
            "animation_applied":True,
            "phoneme_alignment_verified":False,
            "audio_video_sync_verified":False,
        })
    return observed



def project_viseme_mouth_samples(plan, actors, camera, scene, fps):
    """Render-space mouth object projection at sampled viseme timestamps.

    NDC is converted from Blender bottom-left to image top-left. This proves
    geometric location only, NOT visibility of the mesh in the final pixels.
    """
    tracks = plan.get("speech_viseme_tracks") or []
    samples = []
    width = scene.render.resolution_x * scene.render.resolution_percentage / 100.
    height = scene.render.resolution_y * scene.render.resolution_percentage / 100.
    for row in tracks:
        actor_id = row.get("actor_id")
        mouth = (actors.get(actor_id) or {}).get("parts", {}).get("mouth")
        if mouth is None:
            raise ValueError("VISEME_PROJECTION_MOUTH_MISSING:" + str(actor_id))
        events = row.get("viseme_events") or []
        # Sample at rendered-frame cadence without inventing a smooth mouth
        # motion curve. The keyframe animation is evaluated by Blender.
        start = max(0., float(row["line_start_seconds"]) - .10)
        end = min(float(plan["duration_seconds"]), float(row["timeline_end_seconds"]) + .05)
        initial=max(1,fr(start,fps))
        final=min(int(scene.frame_end),fr(end,fps))
        stride=max(1,round(fps/12))
        index=list(range(initial,final+1,stride))
        if final not in index:
            index.append(final)
        for frame_id in index:
            scene.frame_set(frame_id)
            bpy.context.view_layer.update()
            projected = [
                world_to_camera_view(
                    scene, camera, mouth.matrix_world @ Vector(corner)
                ) for corner in mouth.bound_box
            ]
            front = [pt for pt in projected if pt.z > 0]
            box = None
            if len(front)==len(projected):
                x0=max(0.,min(1.,min(float(pt.x) for pt in front)))
                x1=max(0.,min(1.,max(float(pt.x) for pt in front)))
                y0=max(0.,min(1.,min(1.-float(pt.y) for pt in front)))
                y1=max(0.,min(1.,max(1.-float(pt.y) for pt in front)))
                if x1 > x0 and y1 > y0:
                    box={"x0":x0,"x1":x1,"y0":y0,"y1":y1}
            abs_time=(frame_id-1)/fps
            expected=0.
            for event in events:
                if float(row["line_start_seconds"])+float(event["time_seconds"]) <= abs_time+.5/fps:
                    expected=float(event["jaw_open"])
                else:
                    break
            if abs_time>float(row["line_start_seconds"])+float(row["audio_duration_seconds"]):
                expected=0.
            samples.append({
                "line_id":row["line_id"], "actor_id":actor_id,
                "frame_index":frame_id,
                "time_seconds":abs_time,
                "mouth_box":box,
                "projected_width_px":(x1-x0)*width if box else 0.,
                "projected_height_px":(y1-y0)*height if box else 0.,
                "expected_jaw":expected,
                "coordinate_system":"NORMALIZED_TOP_LEFT",
                "provenance":"BLENDER_RIG_MOUTH_PROJECTION",
                "visibility_verified":False,
            })
    scene.frame_set(max(1,scene.frame_start))
    bpy.context.view_layer.update()
    return samples


def prop_root(prop_id):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.object
    root.name = "CF_PROP_" + prop_id
    return root


def proc_prop(prop_id, style="DEBUG_BLOCK"):
    if prop_id in {"minecraft_book", "roblox_book", "book"}:
        root = prop_root(prop_id)
        if style == "MINECRAFT":
            cover = voxel_material("MC_BOOK_COVER", (.60, .08, .05), (.34, .025, .02))
            page = voxel_material("MC_BOOK_PAGE", (.92, .82, .58), (.72, .61, .38))
            ribbon = voxel_material("MC_BOOK_RIBBON", (.85, .70, .10), (.48, .30, .03))
            # Open-book silhouette: separating the two covers in X makes the
            # prop read as a book from the front camera instead of a second
            # rectangular forearm.
            cube(prop_id + "_coverA", (-.17, .05, 0), (.15, .045, .38), cover, root, 0)
            cube(prop_id + "_coverB", (.17, .05, 0), (.15, .045, .38), cover, root, 0)
            cube(prop_id + "_pageA", (-.13, .12, 0), (.12, .022, .33), page, root, 0)
            cube(prop_id + "_pageB", (.13, .12, 0), (.12, .022, .33), page, root, 0)
            cube(prop_id + "_ribbon", (.0, .17, 0), (.025, .01, .34), ribbon, root, 0)
        else:
            cover = roblox_material("RBX_BOOK_COVER", (.22, .08, .52), .38)
            page = roblox_material("RBX_BOOK_PAGE", (.95, .86, .68), .64)
            stripe = roblox_material("RBX_BOOK_STRIPE", (.94, .68, .16), .34)
            cube(prop_id + "_coverA", (-.18, .05, 0), (.16, .055, .40), cover, root, .025)
            cube(prop_id + "_coverB", (.18, .05, 0), (.16, .055, .40), cover, root, .025)
            cube(prop_id + "_pageA", (-.14, .13, 0), (.13, .025, .34), page, root, .02)
            cube(prop_id + "_pageB", (.14, .13, 0), (.13, .025, .34), page, root, .02)
            cube(prop_id + "_stripe", (.0, .18, 0), (.04, .012, .35), stripe, root, .008)
        return root
    if prop_id == "minecraft_tool":
        root = prop_root(prop_id)
        handle = voxel_material("MC_TOOL_HANDLE", (.28, .12, .04), (.46, .24, .08))
        head = voxel_material("MC_TOOL_HEAD", (.40, .46, .52), (.22, .28, .34))
        cube(prop_id + "_handle", (0, 0, -.15), (.06, .06, .43), handle, root, 0)
        cube(prop_id + "_head", (0, 0, .30), (.20, .10, .09), head, root, 0)
        return root
    if prop_id == "roblox_classroom_prop":
        root = prop_root(prop_id)
        body = roblox_material("RBX_PROP_BODY", (.10, .55, .80), .38)
        cap = roblox_material("RBX_PROP_CAP", (.96, .50, .12), .32)
        cube(prop_id + "_body", (0, 0, 0), (.20, .20, .20), body, root, .05)
        cube(prop_id + "_cap", (0, 0, .23), (.16, .16, .04), cap, root, .03)
        return root
    matp = material("CF_PROP_" + prop_id, (.82, .64, .18), metallic=.08, roughness=.38)
    if prop_id == "phone":
        return cube("CF_PROP_phone", (0, 0, 0), (.13, .035, .24), matp, bevel=.025)
    if prop_id == "cup":
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.12, depth=.28)
        o = bpy.context.object
        o.name = "CF_PROP_cup"
        o.data.materials.append(matp)
        add_bevel(o, .015)
        return o
    return cube("CF_PROP_" + prop_id, (0, 0, 0), (.15, .15, .15), matp, bevel=.03)


def load_prop(defn):
    if defn.get("source_path"):
        c = load_collection(resolve(defn["source_path"]), defn.get("collection"))
        bpy.ops.object.empty_add(type="PLAIN_AXES")
        root = bpy.context.object
        root.name = "CF_PROP_ROOT_"+defn["prop_id"]
        for o in c.all_objects:
            if o.parent is None:
                o.parent = root
        return root
    return proc_prop(defn.get("prop_id", "prop"), defn.get("style", "DEBUG_BLOCK"))


def attach_prop(binding, defn, actor, fps):
    obj = load_prop(defn)
    off = binding.get("attach_offset") or {}
    arm = actor.get("armature")
    bone = binding.get("bone_name")
    if arm and bone and arm.data.bones.get(bone):
        obj.parent = arm
        obj.parent_type = "BONE"
        obj.parent_bone = bone
        obj.matrix_parent_inverse.identity()
    else:
        target = actor.get("parts", {}).get(bone) or actor.get("parts", {}).get(binding.get("socket")) or actor["root"]
        obj.parent = target
    apply(obj, off)
    # Procedural style rigs expose a hand-shaped mesh rather than a canonical
    # bone socket frame. Resolve a stable camera-facing presentation offset
    # after parenting so the prop cannot disappear behind the forearm when a
    # character turns toward another actor.
    if defn.get("style") in {"MINECRAFT", "ROBLOX"} and obj.parent is not None:
        bpy.context.view_layer.update()
        obj.matrix_world.translation = obj.parent.matrix_world.translation + Vector((0.0, -0.85, -0.10))
        # The procedural arm mesh is itself scaled to a limb-sized cuboid.
        # Compensate that parent scale or the attached prop collapses to a
        # forearm-colored sliver instead of retaining its authored dimensions.
        parent_scale = obj.parent.scale
        obj.scale = tuple(
            obj.scale[i] / max(abs(float(parent_scale[i])), 1e-4)
            for i in range(3)
        )
        obj.scale = tuple(float(value) * 1.35 for value in obj.scale)
    st = fr(binding.get("start_seconds", 0), fps)
    en = fr(binding.get("end_seconds", 999), fps)
    obj.hide_render = True; obj.hide_viewport = True
    obj.keyframe_insert("hide_render", frame=max(1, st-1)); obj.keyframe_insert("hide_viewport", frame=max(1, st-1))
    obj.hide_render = False; obj.hide_viewport = False
    obj.keyframe_insert("hide_render", frame=st); obj.keyframe_insert("hide_viewport", frame=st)
    obj.keyframe_insert("hide_render", frame=en); obj.keyframe_insert("hide_viewport", frame=en)
    obj.hide_render = True; obj.hide_viewport = True
    obj.keyframe_insert("hide_render", frame=en+1); obj.keyframe_insert("hide_viewport", frame=en+1)
    return obj


def average_target(actors, ids):
    pts = [actors[x]["root"].matrix_world.translation for x in ids if x in actors]
    if not pts:
        return Vector((0, 0, 1.55))
    return Vector((sum(p.x for p in pts)/len(pts), sum(p.y for p in pts)/len(pts), sum(p.z for p in pts)/len(pts)+1.45))


def actor_focus_point(actor):
    parts = actor.get("parts", {})
    head = (
        parts.get("head")
        or parts.get("Head")
        or parts.get("UpperHead")
    )
    if head is not None:
        return head.matrix_world.translation.copy()
    return actor["root"].matrix_world.translation + Vector((0, 0, 1.55))


def apply_gaze(actor_id, cue, actors, fps):
    actor = actors.get(actor_id)
    if actor is None:
        return {
            "actor_id": actor_id,
            "applied": False,
            "reason": "ACTOR_MISSING",
        }

    target = None
    target_actor_id = cue.get("target_actor_id")
    if target_actor_id and target_actor_id in actors:
        target = actor_focus_point(actors[target_actor_id])
    elif cue.get("target_point"):
        target = Vector(xyz(cue.get("target_point")))

    if target is None:
        return {
            "actor_id": actor_id,
            "applied": False,
            "reason": "TARGET_MISSING",
        }

    parts = actor.get("parts", {})
    head = (
        parts.get("head")
        or parts.get("Head")
        or parts.get("UpperHead")
    )
    root = actor.get("root")
    if head is None or root is None:
        return {
            "actor_id": actor_id,
            "applied": False,
            "reason": "HEAD_CONTROL_UNAVAILABLE",
        }

    origin = actor_focus_point(actor)
    delta = target - origin
    if delta.length <= 1e-6:
        return {
            "actor_id": actor_id,
            "applied": False,
            "reason": "ZERO_LENGTH_GAZE",
        }

    world_yaw = math.atan2(delta.x, -delta.y)
    local_yaw = world_yaw - float(root.rotation_euler.z)
    while local_yaw > math.pi:
        local_yaw -= math.tau
    while local_yaw < -math.pi:
        local_yaw += math.tau
    local_yaw = max(-0.78, min(0.78, local_yaw))
    horizontal = math.hypot(delta.x, delta.y)
    pitch = math.atan2(delta.z, max(horizontal, 1e-6))
    pitch = max(-0.38, min(0.38, pitch))
    intensity = max(0.0, min(1.0, float(cue.get("intensity", 1.0))))

    start = fr(cue.get("start_seconds", 0), fps)
    end = fr(
        cue.get(
            "end_seconds",
            cue.get("start_seconds", 0) + 0.5,
        ),
        fps,
    )
    head.keyframe_insert("rotation_euler", frame=max(1, start - 1))
    head.rotation_euler.z = local_yaw * intensity
    head.rotation_euler.x = -pitch * intensity
    head.keyframe_insert("rotation_euler", frame=start)
    head.keyframe_insert("rotation_euler", frame=end)
    return {
        "actor_id": actor_id,
        "target_actor_id": target_actor_id,
        "applied": True,
        "local_yaw_radians": float(local_yaw * intensity),
        "pitch_radians": float(-pitch * intensity),
        "start_frame": start,
        "end_frame": end,
    }


def _world_bbox(obj):
    if obj is None or not hasattr(obj, "bound_box"):
        return []
    return [
        obj.matrix_world @ Vector(corner)
        for corner in obj.bound_box
    ]


def _part(actor, *names):
    parts = actor.get("parts", {})
    for name in names:
        if parts.get(name) is not None:
            return parts[name]
    return None


def _foot_parts(actor):
    right = _part(
        actor,
        "Foot.R",
        "RightFoot",
        "leg.R",
        "RightLeg",
        "LowerLeg.R",
    )
    left = _part(
        actor,
        "Foot.L",
        "LeftFoot",
        "leg.L",
        "LeftLeg",
        "LowerLeg.L",
    )
    return [part for part in (right, left) if part is not None]


def _min_world_z(obj):
    pts = _world_bbox(obj)
    return min((float(p.z) for p in pts), default=None)


def _xy_bounds(objects):
    pts = [
        point
        for obj in objects
        for point in _world_bbox(obj)
    ]
    if not pts:
        return None
    return {
        "min_x": min(float(p.x) for p in pts),
        "max_x": max(float(p.x) for p in pts),
        "min_y": min(float(p.y) for p in pts),
        "max_y": max(float(p.y) for p in pts),
    }


def _vec3(v):
    return [float(v.x), float(v.y), float(v.z)]


def _rotation3(obj):
    return [
        float(obj.rotation_euler.x),
        float(obj.rotation_euler.y),
        float(obj.rotation_euler.z),
    ]


def _distance3(a, b):
    return float((Vector(a) - Vector(b)).length)


def _angle_degrees(a, b):
    va = Vector(a)
    vb = Vector(b)
    if va.length <= 1e-8 or vb.length <= 1e-8:
        return None
    return math.degrees(va.normalized().angle(vb.normalized()))


def _frame_sample(scene, frame, obj):
    scene.frame_set(max(1, int(frame)))
    bpy.context.view_layer.update()
    return {
        "location": _vec3(obj.matrix_world.translation),
        "rotation": _rotation3(obj),
    }


def _action_geometry_check(scene, actor, cue, fps):
    clip_id = str(cue.get("clip_id") or "")
    if actor.get("armature") is not None and not actor.get("parts"):
        return {
            "clip_id": clip_id,
            "measured": False,
            "passed": True,
            "reason": "EXTERNAL_RIG_ACTION_GEOMETRY_NOT_MEASURED",
            "metrics": {},
        }
    start = fr(cue.get("start_seconds", 0), fps)
    end = fr(
        cue.get(
            "end_seconds",
            cue.get("start_seconds", 0) + 0.5,
        ),
        fps,
    )
    mid = max(start, int(round((start + end) / 2)))
    root = actor.get("root")
    if root is None:
        return {
            "clip_id": clip_id,
            "passed": False,
            "reason": "ROOT_MISSING",
        }

    before = _frame_sample(scene, start, root)
    middle = _frame_sample(scene, mid, root)
    after = _frame_sample(scene, end, root)
    metrics = {}
    passed = True
    reason = None

    if clip_id in {"point", "push", "grab", "wave"}:
        arm = _part(actor, "arm.R", "RightArm", "LowerArm.R")
        if arm is None:
            passed = False
            reason = "RIGHT_ARM_CONTROL_MISSING"
        else:
            a0 = _frame_sample(scene, start, arm)
            a1 = _frame_sample(scene, mid, arm)
            delta = max(
                abs(a1["rotation"][i] - a0["rotation"][i])
                for i in range(3)
            )
            metrics["arm_rotation_delta"] = float(delta)
            passed = delta >= 0.18
            if not passed:
                reason = "ARM_POSE_CHANGE_TOO_SMALL"

    elif clip_id in {"walk", "run"}:
        displacement = _distance3(
            before["location"],
            after["location"],
        )
        metrics["root_displacement"] = displacement
        passed = displacement >= (0.45 if clip_id == "walk" else 0.80)
        if not passed:
            reason = "LOCOMOTION_DISPLACEMENT_TOO_SMALL"

    elif clip_id == "jump":
        lift = middle["location"][2] - before["location"][2]
        metrics["root_lift"] = float(lift)
        passed = lift >= 0.25
        if not passed:
            reason = "JUMP_LIFT_TOO_SMALL"

    elif clip_id == "fall":
        rotation = abs(
            after["rotation"][0] - before["rotation"][0]
        )
        metrics["root_pitch_delta"] = float(rotation)
        passed = rotation >= 0.45
        if not passed:
            reason = "FALL_ROTATION_TOO_SMALL"

    elif clip_id in {"shock_recoil", "flinch"}:
        pitch = abs(
            middle["rotation"][0] - before["rotation"][0]
        )
        lift = abs(
            middle["location"][2] - before["location"][2]
        )
        metrics["root_pitch_delta"] = float(pitch)
        metrics["root_vertical_delta"] = float(lift)
        passed = pitch >= 0.08 or lift >= 0.025
        if not passed:
            reason = "REACTION_MOTION_TOO_SMALL"

    elif clip_id == "turn_head":
        head = _part(actor, "head", "Head", "UpperHead")
        if head is None:
            passed = False
            reason = "HEAD_CONTROL_MISSING"
        else:
            h0 = _frame_sample(scene, start, head)
            h1 = _frame_sample(scene, mid, head)
            delta = abs(h1["rotation"][2] - h0["rotation"][2])
            metrics["head_yaw_delta"] = float(delta)
            passed = delta >= 0.08
            if not passed:
                reason = "HEAD_TURN_TOO_SMALL"

    return {
        "clip_id": clip_id,
        "start_frame": start,
        "mid_frame": mid,
        "end_frame": end,
        "passed": bool(passed),
        "reason": reason,
        "metrics": metrics,
    }


def _gaze_accuracy_check(scene, cue, actors, fps):
    actor_id = cue.get("actor_id")
    target_actor_id = cue.get("target_actor_id")
    actor = actors.get(actor_id)
    if actor is None:
        return {
            "actor_id": actor_id,
            "passed": False,
            "reason": "ACTOR_MISSING",
        }
    head = _part(actor, "head", "Head", "UpperHead")
    if head is None:
        return {
            "actor_id": actor_id,
            "passed": False,
            "reason": "HEAD_CONTROL_MISSING",
        }
    target = None
    if target_actor_id and target_actor_id in actors:
        target = actor_focus_point(actors[target_actor_id])
    elif cue.get("target_point"):
        target = Vector(xyz(cue.get("target_point")))
    if target is None:
        return {
            "actor_id": actor_id,
            "passed": False,
            "reason": "TARGET_MISSING",
        }

    start = fr(cue.get("start_seconds", 0), fps)
    end = fr(
        cue.get(
            "end_seconds",
            cue.get("start_seconds", 0) + 0.5,
        ),
        fps,
    )
    sample = max(start, int(round((start + end) / 2)))
    scene.frame_set(sample)
    bpy.context.view_layer.update()
    origin = actor_focus_point(actor)
    forward = head.matrix_world.to_quaternion() @ Vector((0, -1, 0))
    desired = target - origin
    angle = _angle_degrees(forward, desired)
    passed = angle is not None and angle <= 28.0
    return {
        "actor_id": actor_id,
        "target_actor_id": target_actor_id,
        "sample_frame": sample,
        "angle_degrees": angle,
        "passed": bool(passed),
        "reason": None if passed else "GAZE_ANGLE_TOO_LARGE",
    }


def identity_scene_qc(plan, actors, rigs):
    required_by_style = {
        "MINECRAFT": {"torso", "head", "arm.R", "arm.L", "leg.R", "leg.L"},
        "ROBLOX_R6": {"Torso", "Head", "RightArm", "LeftArm", "RightLeg", "LeftLeg"},
        "ROBLOX_R15": {"UpperTorso", "LowerTorso", "Head", "Hand.R", "Hand.L"},
    }
    rows = []
    blockers = []
    measured = 0
    passed = 0
    for actor_id, actor in actors.items():
        rig = rigs.get(actor_id) or {}
        expected_style = str(rig.get("style") or "")
        actual_style = str(actor.get("style") or ("EXTERNAL" if actor.get("armature") else "UNKNOWN"))
        required = required_by_style.get(expected_style, set())
        actual_parts = set(actor.get("parts", {}))
        is_external = actor.get("armature") is not None
        missing = (
            []
            if is_external
            else sorted(required - actual_parts)
        )
        style_ok = (not expected_style) or actual_style == expected_style
        structure_ok = (
            actor.get("armature") is not None
            if is_external
            else not missing
        )
        measured += 2
        passed += int(style_ok) + int(structure_ok)
        actor_blockers = []
        if not style_ok:
            actor_blockers.append("RIG_STYLE_MISMATCH")
        if missing:
            actor_blockers.append("REQUIRED_PARTS_MISSING")
        blockers.extend(f"{actor_id}:{x}" for x in actor_blockers)
        rows.append({
            "actor_id": actor_id,
            "expected_style": expected_style,
            "actual_style": actual_style,
            "required_parts": sorted(required),
            "missing_parts": missing,
            "passed": not actor_blockers,
        })
    score = passed / measured if measured else None
    return {
        "passed": not blockers,
        "score": score,
        "score_semantics": "SCENE_RIG_STRUCTURE_CONFORMANCE_NOT_PIXEL_IDENTITY",
        "blockers": blockers,
        "actors": rows,
    }


def _actor_identity_signature(actor):
    payload = {
        "style": actor.get("style") or ("EXTERNAL" if actor.get("armature") else "UNKNOWN"),
        "parts": sorted(actor.get("parts", {}).keys()),
        "materials": {},
    }
    for name, obj in sorted(actor.get("parts", {}).items()):
        mats = []
        if obj is not None and getattr(obj, "data", None) is not None:
            for mat in getattr(obj.data, "materials", []):
                if mat is not None:
                    mats.append([
                        round(float(x), 4)
                        for x in mat.diffuse_color[:4]
                    ])
        if mats:
            payload["materials"][name] = mats
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def performance_geometry_qc(plan, actors, prop_debug, fps):
    scene = bpy.context.scene
    blockers = []
    warnings = []
    action_checks = []
    gaze_checks = []
    contact_checks = []
    balance_checks = []
    prop_checks = []
    semantic_checks = []
    measured = 0
    passed = 0

    actor_actions = {}
    for cue in plan.get("actions", []):
        actor_id = cue.get("actor_id")
        if actor_id in actors:
            actor_actions.setdefault(actor_id, set()).add(
                str(cue.get("clip_id") or "")
            )
            check = _action_geometry_check(
                scene,
                actors[actor_id],
                cue,
                fps,
            )
            check["actor_id"] = actor_id
            action_checks.append(check)
            if check.get("measured", True):
                measured += 1
                if check.get("passed"):
                    passed += 1
                else:
                    blockers.append(
                        f"{actor_id}:ACTION_EXECUTION:{check.get('clip_id')}:{check.get('reason')}"
                    )
            else:
                warnings.append(
                    f"{actor_id}:ACTION_EXECUTION_NOT_MEASURED:{check.get('clip_id')}"
                )

    for cue in plan.get("gaze", []):
        check = _gaze_accuracy_check(scene, cue, actors, fps)
        gaze_checks.append(check)
        measured += 1
        if check.get("passed"):
            passed += 1
        else:
            blockers.append(
                f"{check.get('actor_id')}:GAZE_ACCURACY:{check.get('reason')}"
            )

    sample_frames = sorted({
        1,
        max(1, int(round(scene.frame_end / 2))),
        max(1, int(scene.frame_end)),
    })
    for actor_id, actor in actors.items():
        feet = _foot_parts(actor)
        if not feet:
            warnings.append(f"{actor_id}:FOOT_GEOMETRY_NOT_MEASURED")
            continue
        dynamic = actor_actions.get(actor_id, set())
        contact_required = not bool(dynamic & {"jump", "fall"})
        for frame in sample_frames:
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            mins = [
                _min_world_z(foot)
                for foot in feet
            ]
            mins = [value for value in mins if value is not None]
            if not mins:
                continue
            min_z = min(mins)
            max_z = max(mins)
            penetrates = min_z < -0.12
            has_contact = min_z <= 0.14
            row = {
                "actor_id": actor_id,
                "frame": frame,
                "min_foot_z": float(min_z),
                "max_foot_z": float(max_z),
                "contact_required": contact_required,
                "has_contact": bool(has_contact),
                "penetrates": bool(penetrates),
            }
            contact_checks.append(row)
            measured += 1
            if penetrates:
                blockers.append(
                    f"{actor_id}:FOOT_GROUND_PENETRATION:frame={frame}:z={min_z:.4f}"
                )
            elif contact_required and not has_contact:
                blockers.append(
                    f"{actor_id}:FOOT_CONTACT_LOST:frame={frame}:z={min_z:.4f}"
                )
            else:
                passed += 1

        if "fall" not in dynamic:
            for frame in (1, max(1, int(scene.frame_end))):
                scene.frame_set(frame)
                bpy.context.view_layer.update()
                bounds = _xy_bounds(feet)
                if bounds is None:
                    continue
                root = actor["root"].matrix_world.translation
                margin = 0.28
                balanced = (
                    bounds["min_x"] - margin <= root.x <= bounds["max_x"] + margin
                    and bounds["min_y"] - margin <= root.y <= bounds["max_y"] + margin
                )
                balance_checks.append({
                    "actor_id": actor_id,
                    "frame": frame,
                    "root_xy": [float(root.x), float(root.y)],
                    "support_bounds": bounds,
                    "passed": bool(balanced),
                })
                measured += 1
                if balanced:
                    passed += 1
                else:
                    blockers.append(
                        f"{actor_id}:BALANCE_OUTSIDE_SUPPORT:frame={frame}"
                    )

    debug_by_prop = {
        row.get("prop_id"): row
        for row in prop_debug
        if row.get("prop_id")
    }
    for binding in plan.get("props", []):
        prop_id = binding.get("prop_id")
        actor_id = binding.get("actor_id")
        row = debug_by_prop.get(prop_id)
        measured += 1
        if row is None:
            prop_checks.append({
                "prop_id": prop_id,
                "actor_id": actor_id,
                "passed": False,
                "reason": "PROP_OBJECT_MISSING",
            })
            blockers.append(f"{actor_id}:PROP_CONTACT_MISSING:{prop_id}")
            continue
        prop_obj = bpy.data.objects.get(row.get("object"))
        actor = actors.get(actor_id)
        expected_parent = None
        if actor is not None:
            expected_parent = _part(
                actor,
                str(binding.get("bone_name") or ""),
                str(binding.get("socket") or ""),
            )
            if expected_parent is None and actor.get("armature") is not None:
                expected_parent = actor.get("armature")

        start = fr(binding.get("start_seconds", 0), fps)
        end = fr(
            binding.get(
                "end_seconds",
                binding.get("start_seconds", 0) + 0.5,
            ),
            fps,
        )
        sample = max(start, int(round((start + end) / 2)))
        scene.frame_set(sample)
        bpy.context.view_layer.update()

        actual_parent = prop_obj.parent if prop_obj is not None else None
        expected_bone = str(binding.get("bone_name") or "")
        bone_parenting = (
            prop_obj is not None
            and getattr(prop_obj, "parent_type", "") == "BONE"
        )
        if bone_parenting and actor is not None and actor.get("armature") is not None:
            armature = actor["armature"]
            parent_ok = (
                actual_parent == armature
                and str(getattr(prop_obj, "parent_bone", "")) == expected_bone
            )
            pose_bone = (
                armature.pose.bones.get(expected_bone)
                if expected_bone
                else None
            )
            if pose_bone is not None:
                expected_world = (
                    armature.matrix_world
                    @ pose_bone.matrix
                ).translation
                world_distance = float(
                    (
                        prop_obj.matrix_world.translation
                        - expected_world
                    ).length
                )
            else:
                world_distance = float("inf")
        else:
            parent_ok = (
                prop_obj is not None
                and actual_parent is not None
                and (
                    expected_parent is None
                    or actual_parent == expected_parent
                )
            )
            if (
                prop_obj is not None
                and expected_parent is not None
            ):
                world_distance = float(
                    (
                        prop_obj.matrix_world.translation
                        - expected_parent.matrix_world.translation
                    ).length
                )
            else:
                world_distance = float("inf")

        visible = (
            prop_obj is not None
            and not bool(prop_obj.hide_render)
            and not bool(prop_obj.hide_viewport)
        )
        contact_ok = (
            parent_ok
            and visible
            and world_distance <= 1.35
        )
        prop_checks.append({
            "prop_id": prop_id,
            "actor_id": actor_id,
            "socket": binding.get("socket"),
            "bone_name": binding.get("bone_name"),
            "sample_frame": sample,
            "parent": (
                actual_parent.name
                if actual_parent is not None
                else None
            ),
            "expected_parent": (
                expected_parent.name
                if expected_parent is not None
                else None
            ),
            "world_distance": world_distance,
            "visible": visible,
            "passed": contact_ok,
        })
        if contact_ok:
            passed += 1
        else:
            blockers.append(
                f"{actor_id}:PROP_CONTACT_INVALID:{prop_id}:"
                f"distance={world_distance:.3f}:"
                f"parent_ok={parent_ok}:visible={visible}"
            )

    directives = plan.get("performance_directives") or []
    gaze_plan = plan.get("gaze") or []
    expression_plan = plan.get("expressions") or []
    reaction_plan = plan.get("reactions") or []
    for directive in directives:
        actor_id = str(directive.get("actor_id") or "")
        role = str(directive.get("role") or "")
        start = float(directive.get("start_seconds") or 0.0)
        end = float(directive.get("end_seconds") or start)
        gaze_target = directive.get("gaze_target")
        trigger = directive.get("reaction_trigger")

        measured += 1
        actor_ok = actor_id in actors
        semantic_checks.append({
            "type": "ACTOR_BINDING",
            "actor_id": actor_id,
            "role": role,
            "passed": actor_ok,
        })
        if actor_ok:
            passed += 1
        else:
            blockers.append(
                f"{actor_id}:SEMANTIC_ACTOR_BINDING_MISSING"
            )
            continue

        if gaze_target:
            gaze_match = next(
                (
                    cue
                    for cue in gaze_plan
                    if str(cue.get("actor_id") or "") == actor_id
                    and str(cue.get("target_actor_id") or "")
                    == str(gaze_target)
                    and float(cue.get("start_seconds") or 0.0)
                    <= start + 0.15
                    and float(
                        cue.get("end_seconds")
                        if cue.get("end_seconds") is not None
                        else end
                    )
                    >= end - 0.15
                ),
                None,
            )
            measured += 1
            gaze_ok = gaze_match is not None
            semantic_checks.append({
                "type": "GAZE_COVERAGE",
                "actor_id": actor_id,
                "target_actor_id": gaze_target,
                "passed": gaze_ok,
            })
            if gaze_ok:
                passed += 1
            else:
                blockers.append(
                    f"{actor_id}:SEMANTIC_GAZE_COVERAGE_MISSING:"
                    f"{gaze_target}"
                )

        if role == "SPEAKER":
            expression_match = next(
                (
                    cue
                    for cue in expression_plan
                    if str(cue.get("actor_id") or "") == actor_id
                    and float(cue.get("start_seconds") or 0.0)
                    <= start + 0.15
                    and float(
                        cue.get("end_seconds")
                        if cue.get("end_seconds") is not None
                        else end
                    )
                    >= end - 0.15
                ),
                None,
            )
            measured += 1
            expression_ok = expression_match is not None
            semantic_checks.append({
                "type": "SPEAKER_EXPRESSION_COVERAGE",
                "actor_id": actor_id,
                "passed": expression_ok,
                "expression_id": (
                    expression_match.get("expression_id")
                    if expression_match is not None
                    else None
                ),
            })
            if expression_ok:
                passed += 1
            else:
                blockers.append(
                    f"{actor_id}:SEMANTIC_SPEAKER_EXPRESSION_MISSING"
                )

        if role == "LISTENER" and trigger:
            reaction_match = next(
                (
                    cue
                    for cue in reaction_plan
                    if str(cue.get("trigger") or "") == str(trigger)
                    and (
                        str(cue.get("actor_id") or "") == actor_id
                        or actor_id
                        in [
                            str(x)
                            for x in (
                                cue.get("target_actor_ids") or []
                            )
                        ]
                    )
                    and float(
                        cue.get("start_seconds")
                        if cue.get("start_seconds") is not None
                        else cue.get("at_seconds") or 0.0
                    )
                    >= start
                    and float(
                        cue.get("start_seconds")
                        if cue.get("start_seconds") is not None
                        else cue.get("at_seconds") or 0.0
                    )
                    <= end + 0.15
                ),
                None,
            )
            measured += 1
            reaction_ok = reaction_match is not None
            semantic_checks.append({
                "type": "LISTENER_REACTION_TIMING",
                "actor_id": actor_id,
                "trigger": trigger,
                "passed": reaction_ok,
                "at_seconds": (
                    (
                        reaction_match.get("start_seconds")
                        if reaction_match.get("start_seconds") is not None
                        else reaction_match.get("at_seconds")
                    )
                    if reaction_match is not None
                    else None
                ),
            })
            if reaction_ok:
                passed += 1
            else:
                blockers.append(
                    f"{actor_id}:SEMANTIC_LISTENER_REACTION_MISSING:"
                    f"{trigger}"
                )

    score = passed / measured if measured else None
    return {
        "passed": not blockers,
        "score": score,
        "score_semantics": "MEASURED_3D_ACTION_GAZE_CONTACT_BALANCE_PLUS_SEMANTIC_CUE_CONFORMANCE",
        "blockers": blockers,
        "warnings": warnings,
        "action_checks": action_checks,
        "gaze_checks": gaze_checks,
        "contact_checks": contact_checks,
        "balance_checks": balance_checks,
        "prop_checks": prop_checks,
        "semantic_checks": semantic_checks,
        "semantic_directive_count": len(directives),
        "measured_checks": measured,
        "passed_checks": passed,
    }


def _actor_screen_box(scene, cam, actor):
    points = []
    seen = set()
    for obj in actor.get("parts", {}).values():
        if obj is None or obj.name in seen:
            continue
        seen.add(obj.name)
        points.extend(_world_bbox(obj))
    if not points:
        root = actor.get("root")
        if root is not None:
            p = root.matrix_world.translation
            points = [
                p + Vector((-0.5, 0.0, 0.0)),
                p + Vector((0.5, 0.0, 0.0)),
                p + Vector((0.0, 0.0, 2.8)),
            ]
    if not points:
        return None
    projected = [
        world_to_camera_view(scene, cam, point)
        for point in points
    ]
    in_front = [p for p in projected if p.z > 0]
    if not in_front:
        return None
    x0 = max(0.0, min(float(p.x) for p in in_front))
    x1 = min(1.0, max(float(p.x) for p in in_front))
    y0 = max(0.0, min(float(p.y) for p in in_front))
    y1 = min(1.0, max(float(p.y) for p in in_front))
    if x1 <= x0 or y1 <= y0:
        return None
    return {
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": y1,
        "area": float((x1 - x0) * (y1 - y0)),
    }


def capture_render_state(plan, actors, prop_debug, cam, lighting_debug, rigs):
    scene = bpy.context.scene
    scene_id = (plan.get("creative_intent") or {}).get("scene_id")
    start_frame = 1
    end_frame = max(1, int(scene.frame_end))
    mid_frame = max(start_frame, int(round((start_frame + end_frame) / 2)))
    actors_out = {}
    for actor_id, actor in actors.items():
        root = actor.get("root")
        if root is None:
            continue
        scene.frame_set(start_frame)
        bpy.context.view_layer.update()
        start = {
            "root_location": _vec3(root.matrix_world.translation),
            "root_rotation": _rotation3(root),
            "focus_point": _vec3(actor_focus_point(actor)),
        }
        scene.frame_set(mid_frame)
        bpy.context.view_layer.update()
        mid = {
            "root_location": _vec3(root.matrix_world.translation),
            "root_rotation": _rotation3(root),
            "focus_point": _vec3(actor_focus_point(actor)),
            "screen_box": _actor_screen_box(scene, cam, actor),
        }
        scene.frame_set(end_frame)
        bpy.context.view_layer.update()
        end = {
            "root_location": _vec3(root.matrix_world.translation),
            "root_rotation": _rotation3(root),
            "focus_point": _vec3(actor_focus_point(actor)),
        }
        actors_out[actor_id] = {
            "rig_id": (rigs.get(actor_id) or {}).get("rig_id"),
            "style": actor.get("style"),
            "identity_signature": _actor_identity_signature(actor),
            "start": start,
            "mid": mid,
            "end": end,
        }

    props_out = {}
    for row in prop_debug:
        obj = bpy.data.objects.get(row.get("object"))
        if obj is None:
            continue
        scene.frame_set(start_frame)
        bpy.context.view_layer.update()
        start_loc = _vec3(obj.matrix_world.translation)
        start_hidden = bool(obj.hide_render)
        scene.frame_set(end_frame)
        bpy.context.view_layer.update()
        end_loc = _vec3(obj.matrix_world.translation)
        end_hidden = bool(obj.hide_render)
        props_out[str(row.get("prop_id"))] = {
            "actor_id": row.get("actor_id"),
            "socket": row.get("socket"),
            "parent": obj.parent.name if obj.parent else None,
            "start_location": start_loc,
            "end_location": end_loc,
            "start_hidden": start_hidden,
            "end_hidden": end_hidden,
        }

    scene.frame_set(start_frame)
    bpy.context.view_layer.update()
    camera_start = {
        "location": _vec3(cam.matrix_world.translation),
        "rotation": _rotation3(cam),
        "lens_mm": float(cam.data.lens),
    }
    scene.frame_set(end_frame)
    bpy.context.view_layer.update()
    camera_end = {
        "location": _vec3(cam.matrix_world.translation),
        "rotation": _rotation3(cam),
        "lens_mm": float(cam.data.lens),
    }
    return {
        "shot_id": plan.get("shot_id"),
        "scene_id": scene_id,
        "start_frame": start_frame,
        "mid_frame": mid_frame,
        "end_frame": end_frame,
        "actors": actors_out,
        "props": props_out,
        "camera": {
            "start": camera_start,
            "end": camera_end,
        },
        "lighting": dict(lighting_debug or {}),
        "creative_intent_bound": bool(plan.get("creative_intent")),
    }


def geometry_camera_qc(plan, actors, cam, fps):
    scene = bpy.context.scene
    take = plan.get("camera") or {}
    targets = [
        actor_id
        for actor_id in take.get("targets", [])
        if actor_id in actors
    ]
    if not targets:
        return {
            "passed": False,
            "blockers": ["CAMERA_TARGETS_MISSING"],
            "warnings": [],
            "targets": [],
        }

    debug_frame = max(
        1,
        1 + round(
            float(plan.get("duration_seconds", 1))
            * fps
            / 2
        ),
    )
    scene.frame_set(debug_frame)
    bpy.context.view_layer.update()
    h_margin = float(take.get("horizontal_safe_margin", 0.10))
    v_margin = float(take.get("vertical_safe_margin", 0.10))
    blockers = []
    warnings = []
    rows = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    camera_origin = cam.matrix_world.translation.copy()

    for actor_id in targets:
        actor = actors[actor_id]
        point = actor_focus_point(actor)
        ndc = world_to_camera_view(scene, cam, point)
        target_blockers = []
        target_warnings = []

        if ndc.z <= 0:
            target_blockers.append("TARGET_BEHIND_CAMERA")
        if (
            ndc.x < h_margin
            or ndc.x > 1.0 - h_margin
            or ndc.y < v_margin
            or ndc.y > 1.0 - v_margin
        ):
            target_blockers.append("TARGET_OUTSIDE_SAFE_FRAME")

        direction = point - camera_origin
        distance = float(direction.length)
        hit_name = None
        if distance > 1e-4:
            hit = scene.ray_cast(
                depsgraph,
                camera_origin,
                direction.normalized(),
                distance=max(0.0, distance - 0.03),
            )
            did_hit = bool(hit[0])
            hit_obj = hit[4] if len(hit) > 4 else None
            if did_hit and hit_obj is not None:
                hit_name = hit_obj.name
                acceptable = {
                    actor["root"].name,
                    *[
                        obj.name
                        for obj in actor.get("parts", {}).values()
                        if obj is not None
                    ],
                }
                # Actor-owned attachments (hair, eyewear, accessories) can
                # legitimately intersect the face ray. They must not be
                # mistaken for an external occluder simply because the
                # attachment was not registered as an anatomical rig part.
                hit_owner = hit_obj
                while hit_owner is not None and hit_owner != actor["root"]:
                    hit_owner = hit_owner.parent
                owned_attachment = hit_owner == actor["root"]
                if hit_name not in acceptable and not owned_attachment:
                    target_blockers.append("TARGET_OCCLUDED")

        blockers.extend(
            f"{actor_id}:{code}"
            for code in target_blockers
        )
        warnings.extend(
            f"{actor_id}:{code}"
            for code in target_warnings
        )
        rows.append(
            {
                "actor_id": actor_id,
                "screen_x": float(ndc.x),
                "screen_y": float(ndc.y),
                "camera_depth": float(ndc.z),
                "hit_object": hit_name,
                "blockers": target_blockers,
                "warnings": target_warnings,
            }
        )

    return {
        "passed": not blockers,
        "blockers": blockers,
        "warnings": warnings,
        "targets": rows,
        "debug_frame": debug_frame,
        "camera_location": list(camera_origin),
        "horizontal_safe_margin": h_margin,
        "vertical_safe_margin": v_margin,
    }


def setup_camera(plan, actors, fps):
    take = plan.get("camera") or {"lens_mm": 50, "targets": [], "motion": "static", "dof_fstop": 3.5, "motion_strength": .14}
    scene = plan.get("scene") or {}
    anchor = (scene.get("camera_anchors") or {}).get(take.get("anchor"))
    loc = xyz((anchor or {}).get("location"), (0, -7, 2.4))
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    # The camera is always solved from a world-up tracking basis. Anchor Euler
    # values from the debug grammar are not allowed to leak accidental roll into
    # production orbit/track shots.
    cam.rotation_euler = (0.0, 0.0, math.radians(float(take.get("camera_roll", 0.0))))
    cam.data.lens = float(take.get("lens_mm", 50))
    prop_target = None
    if take.get("prop_id"):
        prefix = "CF_PROP_" + str(take["prop_id"])
        prop = next((o for o in bpy.data.objects if o.name.startswith(prefix)), None)
        if prop is not None:
            prop_target = prop.matrix_world.translation.copy()
    target = None
    if take.get("target_mode") == "prop" and prop_target is not None:
        target = prop_target
    if target is None:
        target = average_target(actors, take.get("targets", []))
        # Keep the paired actors readable while biasing the composition toward
        # the hand-held object. This makes the presentation beat communicate
        # the prop instead of hiding it at the edge of an actor-only frame.
        if prop_target is not None and take.get("target_mode") in {"pair", "group"}:
            target = target * 0.68 + prop_target * 0.32
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=target)
    focus = bpy.context.object
    focus.name = "CF_CAMERA_FOCUS"
    con = cam.constraints.new(type="TRACK_TO")
    con.target = focus
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    if hasattr(cam.data, "dof"):
        cam.data.dof.use_dof = bool(plan.get("render_quality", {}).get("use_dof", True))
        cam.data.dof.focus_object = focus
        cam.data.dof.aperture_fstop = float(take.get("dof_fstop", 3.5))

    st = fr(take.get("start_seconds", 0), fps)
    en = fr(take.get("end_seconds", plan.get("duration_seconds", 1)), fps)
    motion = take.get("motion", "static")
    strength = float(take.get("motion_strength", .14))
    cam.keyframe_insert("location", frame=st)
    d = target - cam.location
    if motion == "push_in":
        cam.location += d * min(.45, strength)
    elif motion == "pull_out":
        cam.location -= d.normalized() * max(.25, d.length*strength)
    elif motion == "track":
        cam.location.x += max(.5, d.length*strength)
    elif motion == "orbit":
        rel = cam.location - target
        # Keep the horizon level and the camera inside the designed scene
        # envelope. A valid, restrained orbit beats a flashy wall-crossing one.
        ang = math.radians(min(8.0, 4.0 + 16.0 * strength))
        cam.location.x = target.x + rel.x*math.cos(ang) - rel.y*math.sin(ang)
        cam.location.y = target.y + rel.x*math.sin(ang) + rel.y*math.cos(ang)
    elif motion == "snap":
        # Snap is intentionally a fast push rather than a discontinuous transform.
        cam.location += d * min(.32, .15 + strength)
    cam.keyframe_insert("location", frame=en)
    bpy.context.scene.camera = cam
    return cam


def add_light(kind, loc, energy, size=4.0, color=(1,1,1)):
    bpy.ops.object.light_add(type=kind, location=loc)
    o = bpy.context.object
    o.data.energy = energy
    o.data.color = color
    if hasattr(o.data, "size"):
        o.data.size = size
    return o


def setup_lighting(q, scene, intent=None):
    style = scene.get("style", "DEBUG_BLOCK")
    intent = intent or {}
    light_state = str(intent.get("light_state") or "").lower()
    time_of_day = str(intent.get("time_of_day") or "").lower()

    multiplier = 1.0 if style == "DEBUG_BLOCK" else (1.28 if style == "MINECRAFT" else 1.16)
    key_scale = 1.0
    fill_scale = 1.0
    rim_scale = 1.0
    world_scale = 1.25 if style != "DEBUG_BLOCK" else 1.0
    key_color = (1.0, .84, .70)
    fill_color = (.62, .76, 1.0)
    rim_color = (1.0, .52, .30)
    world_color = (.035, .055, .085, 1)

    if "soft" in light_state:
        key_scale *= 0.88
        fill_scale *= 1.12
    if any(token in time_of_day for token in ("night", "evening", "dusk")):
        key_scale *= 0.72
        fill_scale *= 0.68
        rim_scale *= 0.85
        world_scale *= 0.55
        key_color = (.60, .70, 1.0)
        fill_color = (.32, .42, .72)
        rim_color = (.74, .52, 1.0)
        world_color = (.012, .022, .055, 1)
    elif any(token in time_of_day for token in ("sunset", "golden")):
        key_scale *= 1.08
        fill_scale *= 0.84
        key_color = (1.0, .60, .30)
        rim_color = (1.0, .34, .12)

    key_energy = float(q.get("key_light_energy", 1200)) * multiplier * key_scale
    fill_energy = float(q.get("fill_light_energy", 450)) * multiplier * fill_scale
    rim_energy = float(q.get("rim_light_energy", 800)) * multiplier * rim_scale
    add_light("AREA", (4.5, -4.5, 7.5), key_energy, 5.5, key_color)
    add_light("AREA", (-4.5, -2.0, 4.5), fill_energy, 5.0, fill_color)
    add_light("AREA", (0, 4.0, 6.5), rim_energy, 3.5, rim_color)

    world = bpy.context.scene.world or bpy.data.worlds.new("CF_WORLD")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background") if world.node_tree else None
    world_strength = float(q.get("world_strength", .35)) * world_scale
    if bg:
        bg.inputs["Color"].default_value = world_color
        bg.inputs["Strength"].default_value = world_strength
    return {
        "light_state": intent.get("light_state"),
        "time_of_day": intent.get("time_of_day"),
        "key_energy": key_energy,
        "fill_energy": fill_energy,
        "rim_energy": rim_energy,
        "world_strength": world_strength,
        "intent_bound": bool(intent),
    }


def event_vfx(event, actors, fps):
    kind = event.get("renderer_event")
    if not kind:
        return
    frame = fr(event.get("at_seconds", 0), fps)
    intensity = float(event.get("intensity", 1))
    source = event.get("source_actor_id")
    pos = average_target(actors, [source]) if source else Vector((0,0,1.5))
    if kind == "impact_flash":
        l = add_light("POINT", pos + Vector((0,-.3,.2)), 0, 1.0, (1.0, .32, .08))
        l.data.keyframe_insert("energy", frame=max(1, frame-1))
        l.data.energy = 2600*intensity
        l.data.keyframe_insert("energy", frame=frame)
        l.data.energy = 0
        l.data.keyframe_insert("energy", frame=frame+3)
    elif kind == "sparkle_burst":
        em = material("CF_SPARK", (1.0,.65,.08), roughness=.2, emission=(1.0,.24,.03), emission_strength=4.0)
        for i in range(6):
            ang = i*math.tau/6
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=.06, location=pos)
            o = bpy.context.object; o.data.materials.append(em); o.scale=(.01,.01,.01); kf(o,"scale",max(1,frame-1))
            o.location += Vector((math.cos(ang)*.55, math.sin(ang)*.55, .15+(i%2)*.25))*intensity
            o.scale=(1,1,1); kf(o,"location",frame+4); kf(o,"scale",frame+2)
            o.scale=(.01,.01,.01); kf(o,"scale",frame+8)


def apply_quality(plan):
    sc = bpy.context.scene
    q = plan.get("render_quality") or {}
    engine = q.get("engine") or plan.get("render_engine") or "BLENDER_EEVEE_NEXT"
    try:
        sc.render.engine = engine
    except Exception:
        sc.render.engine = plan.get("render_engine", "BLENDER_EEVEE_NEXT")
    pct = 50 if plan.get("render_preview") else int(q.get("render_percentage", 100))
    sc.render.resolution_x = int(plan.get("width", 1280))
    sc.render.resolution_y = int(plan.get("height", 720))
    sc.render.resolution_percentage = pct
    sc.render.fps = int(plan.get("fps", 24))
    sc.frame_start = 1
    sc.frame_end = max(1, round(float(plan.get("duration_seconds", 1))*sc.render.fps))
    sc.render.film_transparent = bool(q.get("transparent_film", False))
    safe_set(sc.render, "use_motion_blur", bool(q.get("motion_blur", True)))
    safe_set(sc.render, "motion_blur_shutter", float(q.get("motion_blur_shutter", .35)))
    eevee = getattr(sc, "eevee", None)
    safe_set(eevee, "taa_samples", int(q.get("taa_samples", 64)))
    safe_set(eevee, "use_gtao", bool(q.get("ambient_occlusion", True)))
    safe_set(eevee, "gtao_distance", 3)
    safe_set(eevee, "gtao_factor", 1.25)

    # Cycles is used only as an explicitly selected quality-recovery method.
    # Keep the same scene/camera/animation contract; change only the renderer.
    if engine == "CYCLES":
        cycles = getattr(sc, "cycles", None)
        samples = int(q.get("taa_samples", 64))
        if plan.get("render_preview"):
            samples = min(samples, 16)
        safe_set(cycles, "samples", max(1, samples))
        safe_set(cycles, "use_denoising", True)
        safe_set(cycles, "preview_samples", min(16, max(1, samples)))
        # Prefer GPU when available, but fail safely to Blender's configured
        # device rather than mutating global preferences in the worker.
        safe_set(cycles, "device", "GPU")
    try:
        sc.view_settings.view_transform = q.get("color_management", "AgX")
    except Exception:
        pass
    try:
        sc.view_settings.look = q.get("look", "AgX - Medium High Contrast")
    except Exception:
        pass
    sc.view_settings.exposure = float(q.get("exposure", 0))
    sc.view_settings.gamma = float(q.get("gamma", 1))
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"
    sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.audio_codec = "AAC"
    safe_set(sc.render.ffmpeg, "video_bitrate", int(q.get("bitrate_mbps", 28))*1000)
    safe_set(sc.render.ffmpeg, "gopsize", max(12, sc.render.fps*2))
    return sc


def render(job, plan=None):
    plan = plan or job.get("plan") or {}
    if not plan:
        # Compatibility fallback for older controllers.
        shot = job["shot"]
        plan = {
            **shot,
            "scene_mode": "library" if shot.get("scene", {}).get("source_path") else "procedural",
            "camera": next((x for x in shot.get("camera_takes", []) if x.get("take_id") == job.get("camera_take_id")), None) or (shot.get("camera_takes") or [None])[0],
            "render_quality": shot.get("render_quality", {}),
            "render_preview": job.get("render_preview", False),
            "output_path": job["output_path"],
        }
    out = Path(plan["output_path"]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    clear_scene_instances()
    fps = int(plan.get("fps", 24))

    build_scene(plan.get("scene") or {})
    actors = {}
    rigs = plan.get("rigs", {})
    placements = {a["actor_id"]: a for a in plan.get("actors", [])}
    for a in plan.get("actors", []):
        rig = rigs[a["actor_id"]]
        actors[a["actor_id"]] = ext_actor(a["actor_id"], rig, a.get("transform")) if rig.get("source_path") else proc_actor(a["actor_id"], a.get("transform"), rig)
        # Minimal contact safety: actors cannot start below the ground plane.
        root = actors[a["actor_id"]]["root"]
        if root.location.z < 0:
            root.location.z = 0

    # Facing is solved after every actor exists. This makes dialogue/action blocking
    # deterministic without requiring a human to keyframe each rotation.
    for aid, actor in actors.items():
        target_id = placements.get(aid, {}).get("facing_target")
        if target_id and target_id in actors:
            origin = actor["root"].matrix_world.translation
            target = actors[target_id]["root"].matrix_world.translation
            delta = target - origin
            if delta.length > 1e-6:
                # Procedural faces point along local -Y (the eye/mouth side).
                # atan2(delta.y, delta.x)-pi/2 pointed them exactly backwards.
                actor["root"].rotation_euler.z = math.atan2(delta.x, -delta.y)

    clips = plan.get("clips", {})
    for c in plan.get("actions", []):
        if c["actor_id"] in actors:
            action(actors[c["actor_id"]], c, clips.get(c["clip_id"], {}), fps)
    for e in plan.get("expressions", []):
        if e["actor_id"] in actors:
            expression(actors[e["actor_id"]], rigs[e["actor_id"]], e, fps)

    viseme_debug = apply_speech_visemes(plan, actors, fps)

    gaze_debug = []
    for gaze_cue in plan.get("gaze", []):
        gaze_debug.append(
            apply_gaze(
                gaze_cue.get("actor_id"),
                gaze_cue,
                actors,
                fps,
            )
        )

    prop_defs = plan.get("prop_definitions", {})
    prop_debug = []
    for binding in plan.get("props", []):
        aid = binding.get("actor_id")
        pdef = prop_defs.get(binding.get("prop_id"), {"prop_id": binding.get("prop_id")})
        if aid in actors:
            attached = attach_prop(binding, pdef, actors[aid], fps)
            prop_debug.append({
                "prop_id": binding.get("prop_id"),
                "actor_id": aid,
                "socket": binding.get("socket"),
                "bone_name": binding.get("bone_name"),
                "object": attached.name,
                "parent": attached.parent.name if attached.parent else None,
                "local_location": list(attached.location),
                "local_rotation": list(attached.rotation_euler),
                "world_location": list(attached.matrix_world.translation),
                "child_count": len(attached.children),
                "hide_render": attached.hide_render,
            })

    cam = setup_camera(plan, actors, fps)
    lighting_debug = setup_lighting(
        plan.get("render_quality") or {},
        plan.get("scene") or {},
        plan.get("lighting_intent") or {},
    )
    for ev in plan.get("events", []):
        event_vfx(ev, actors, fps)

    sc = apply_quality(plan)
    sc.render.filepath = str(out)
    debug_frame = max(1, 1 + round(float(plan.get("duration_seconds", 1)) * fps / 2))
    sc.frame_set(debug_frame)
    bpy.context.view_layer.update()

    geometry_qc = geometry_camera_qc(plan, actors, cam, fps)
    identity_qc = identity_scene_qc(plan, actors, rigs)
    performance_qc = performance_geometry_qc(
        plan,
        actors,
        prop_debug,
        fps,
    )
    render_state = capture_render_state(
        plan,
        actors,
        prop_debug,
        cam,
        lighting_debug,
        rigs,
    )
    mouth_projection = project_viseme_mouth_samples(
        plan, actors, cam, sc, fps
    )
    geometry_sidecar = out.with_suffix(
        out.suffix + ".geometry_qc.json"
    )
    geometry_sidecar.write_text(
        json.dumps(
            {
                "shot_id": plan.get("shot_id"),
                "geometry_qc": geometry_qc,
                "identity_qc": identity_qc,
                "performance_qc": performance_qc,
                "render_state": render_state,
                "gaze_debug": gaze_debug,
                "viseme_debug": viseme_debug,
                "mouth_projection": mouth_projection,
                "lighting_debug": lighting_debug,
                "creative_intent": plan.get("creative_intent") or {},
                "performance_directives": (
                    plan.get("performance_directives") or []
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    if not geometry_qc.get("passed", False):
        raise ValueError(
            "GEOMETRY_CAMERA_QC_FAILED:"
            + ",".join(geometry_qc.get("blockers", []))
        )
    if not identity_qc.get("passed", False):
        raise ValueError(
            "SCENE_IDENTITY_QC_FAILED:"
            + ",".join(identity_qc.get("blockers", []))
        )
    if not performance_qc.get("passed", False):
        raise ValueError(
            "PERFORMANCE_GEOMETRY_QC_FAILED:"
            + ",".join(performance_qc.get("blockers", []))
        )
    for item in prop_debug:
        prop = bpy.data.objects.get(item["object"])
        if prop is not None:
            item["debug_frame"] = debug_frame
            item["world_location"] = list(prop.matrix_world.translation)
            item["hide_render_at_debug_frame"] = prop.hide_render
            item["children"] = [
                {"name": child.name, "world_location": list(child.matrix_world.translation)}
                for child in prop.children
            ]
    bpy.ops.render.render(animation=True)

    sidecar = out.with_suffix(out.suffix + ".events.json")
    sidecar.write_text(json.dumps({"shot_id": plan.get("shot_id"), "events": plan.get("events", [])}, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "output_path": str(out),
        "frames": sc.frame_end,
        "pid": os.getpid(),
        "quality_profile": (plan.get("render_quality") or {}).get("profile_id"),
        "scene_mode": plan.get("scene_mode"),
        "event_sidecar": str(sidecar),
        "geometry_qc_sidecar": str(geometry_sidecar),
        "geometry_qc": geometry_qc,
        "identity_qc": identity_qc,
        "performance_qc": performance_qc,
        "render_state": render_state,
        "gaze_debug": gaze_debug,
        "viseme_debug": viseme_debug,
        "mouth_projection_count": len(mouth_projection),
        "lighting_debug": lighting_debug,
        "creative_intent_bound": bool(plan.get("creative_intent")),
        "performance_directive_count": len(
            plan.get("performance_directives") or []
        ),
        "cache_metrics": dict(CACHE_STATS),
        "prop_debug": prop_debug,
    }


emit({"type": "ready", "pid": os.getpid(), "backend": "blender", "blender_version": bpy.app.version_string})
for raw in sys.stdin:
    if not raw.startswith(P):
        continue
    m = None
    try:
        m = json.loads(raw[len(P):])
        rid = m.get("request_id")
        op = m.get("op")
        if op == "ping":
            emit({"request_id": rid, "ok": True, "pid": os.getpid()})
        elif op == "render":
            emit({"request_id": rid, "ok": True, **render(m["job"], m.get("plan"))})
        elif op == "shutdown":
            emit({"request_id": rid, "ok": True, "pid": os.getpid()})
            break
        else:
            emit({"request_id": rid, "ok": False, "error": "unknown op"})
    except Exception as exc:
        emit({
            "request_id": (m or {}).get("request_id"),
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc()[-8000:],
        })
