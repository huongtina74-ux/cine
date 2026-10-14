from __future__ import annotations

import argparse
import math
from pathlib import Path

import bpy
from mathutils import Vector


def reset_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        pass


def mat(name, rgba):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = rgba
    return m


def cube(name, loc, scale, material=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    return o


def cyl(name, loc, radius, depth, material=None, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    return o


def sphere(name, loc, radius, material=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=loc)
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    return o


def empty(name, loc):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = loc
    return o


def look_at(obj, target=(0, 0, 0)):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _visible_bounds():
    points = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    if not points:
        return Vector((0, 0, 0)), 6.0
    mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    center = (mins + maxs) * 0.5
    extent = max((maxs - mins).x, (maxs - mins).y, (maxs - mins).z, 2.0)
    return center, extent


def setup_preview():
    center, extent = _visible_bounds()
    world = bpy.context.scene.world
    world.color = (0.04, 0.04, 0.04)
    bpy.ops.object.light_add(type="AREA", location=(center.x + extent, center.y - extent, center.z + extent * 1.5))
    key = bpy.context.object
    key.name = "PREVIEW_KEY"
    key.data.energy = 1200
    key.data.shape = "DISK"
    key.data.size = max(4.0, extent)
    look_at(key, center)
    bpy.ops.object.light_add(type="AREA", location=(center.x - extent, center.y, center.z + extent))
    fill = bpy.context.object
    fill.name = "PREVIEW_FILL"
    fill.data.energy = 650
    fill.data.size = max(4.0, extent)
    look_at(fill, center)
    bpy.ops.object.camera_add(location=(center.x + extent * 1.15, center.y - extent * 1.55, center.z + extent * 1.0))
    cam = bpy.context.object
    cam.name = "PREVIEW_CAMERA"
    look_at(cam, center)
    cam.data.lens = 52
    bpy.context.scene.camera = cam
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 480
    scene.render.resolution_y = 270
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"


def common_scene_markers():
    empty("ANIMAL_SPAWN", (0, -4.5, 1.2))
    empty("PATH_START", (0, -3.5, 1.0))
    empty("OBSTACLE_SLOT_1", (0, 1.0, 1.0))
    empty("OBSTACLE_SLOT_2", (0, 4.0, 1.0))
    empty("FINISH_ZONE", (0, 7.0, 0.8))
    empty("CAMERA_HERO", (7, -8, 5))
    empty("CAMERA_CHASE", (5, 0, 4))
    empty("CAMERA_FINISH", (7, 8, 5))


def base_ground():
    ground = cube("GROUND", (0, 1.5, -0.3), (8, 11, 0.25), mat("MAT_GROUND", (0.18, 0.55, 0.22, 1)))
    return ground


def build_slide(kind):
    base_ground()
    blue = mat("MAT_SLIDE", (0.12, 0.5, 0.95, 1))
    rail = mat("MAT_RAIL", (0.95, 0.25, 0.2, 1))
    start = cube("START_PLATFORM", (0, -5.2, 2.8), (3.6, 2.0, 0.25), blue)
    finish = cube("FINISH_PLATFORM", (0, 7.2, 0.25), (4.0, 2.2, 0.2), blue)
    if kind == "spiral":
        centers = []
        count = 36
        for i in range(count):
            t = i / (count - 1)
            angle = t * math.pi * 1.65 - math.pi * 0.7
            r = 4.2 - 1.25 * t
            centers.append(Vector((
                math.cos(angle) * r,
                -1.8 + 9.0 * t,
                3.0 - 2.4 * t,
            )))

        width = 4.2
        verts = []
        left_edge = []
        right_edge = []
        for i, p in enumerate(centers):
            prev = centers[max(0, i - 1)]
            nxt = centers[min(count - 1, i + 1)]
            tangent = nxt - prev
            tangent.z = 0
            if tangent.length < 1e-6:
                tangent = Vector((0, 1, 0))
            tangent.normalize()
            side = Vector((-tangent.y, tangent.x, 0))
            left = p + side * (width * 0.5)
            right = p - side * (width * 0.5)
            left_edge.append(left)
            right_edge.append(right)
            verts.extend([tuple(left), tuple(right)])
        faces = [(i * 2, i * 2 + 1, i * 2 + 3, i * 2 + 2) for i in range(count - 1)]
        mesh = bpy.data.meshes.new("SLIDE_BODY_MESH")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new("SLIDE_BODY", mesh)
        bpy.context.collection.objects.link(obj)
        mesh.materials.append(blue)

        for edge_name, edge_points in (("SLIDE_RAIL_L", left_edge), ("SLIDE_RAIL_R", right_edge)):
            curve = bpy.data.curves.new(edge_name + "_CURVE", type="CURVE")
            curve.dimensions = "3D"
            curve.bevel_depth = 0.16
            curve.bevel_resolution = 3
            spline = curve.splines.new("POLY")
            spline.points.add(len(edge_points) - 1)
            for point, co in zip(spline.points, edge_points):
                point.co = (*co, 1)
            rail_obj = bpy.data.objects.new(edge_name, curve)
            bpy.context.collection.objects.link(rail_obj)
            curve.materials.append(rail)

        path_curve = bpy.data.curves.new("SLIDE_PATH_CURVE", type="CURVE")
        path_curve.dimensions = "3D"
        path_spline = path_curve.splines.new("POLY")
        path_spline.points.add(len(centers) - 1)
        for point, co in zip(path_spline.points, centers):
            point.co = (*co, 1)
        path = bpy.data.objects.new("SLIDE_PATH", path_curve)
        bpy.context.collection.objects.link(path)
    else:
        body = cube("SLIDE_BODY", (0, 0.2, 1.45), (2.7, 6.3, 0.22), blue)
        body.rotation_euler.x = math.radians(10)
        left = cube("SLIDE_RAIL_L", (-2.75, 0.2, 1.9), (0.16, 6.3, 0.55), rail)
        right = cube("SLIDE_RAIL_R", (2.75, 0.2, 1.9), (0.16, 6.3, 0.55), rail)
        path = empty("SLIDE_PATH", (0, 0.2, 1.7))
        path["path_kind"] = "straight"
    common_scene_markers()
    start["template_role"] = "start"
    finish["template_role"] = "finish"
    path["template_role"] = "animal_path"


def build_generic_scene(kind):
    build_slide("straight")
    bpy.context.scene["long_slide_scene_kind"] = kind
    if kind == "paint_gate":
        build_paint_gate()
    elif kind == "fountain":
        build_water_pool()
    elif kind == "cage":
        build_cage()
    elif kind == "key_door":
        build_cage()
        empty("KEY_SOCKET", (-2.0, 2.0, 1.0))
    elif kind == "ball_pit":
        build_ball_pit()
    elif kind == "giant_animal":
        build_giant_duck()


def build_rotating_hammer():
    red = mat("MAT_HAMMER", (0.9, 0.15, 0.12, 1))
    grey = mat("MAT_METAL", (0.28, 0.3, 0.34, 1))
    post = cyl("HAMMER_POST", (0, 0, 1.7), 0.35, 3.4, grey)
    rotor = empty("ROTATION_ROOT", (0, 0, 2.5))
    beam = cube("HAMMER_BEAM", (0, 0, 2.5), (3.0, 0.32, 0.32), red)
    world = beam.matrix_world.copy()
    beam.parent = rotor
    beam.matrix_world = world
    rotor["rotation_axis"] = "Z"
    rotor["rotation_speed_deg_s"] = 120.0
    empty("EVENT_ANCHOR", (0, 0, 2.5))
    post["collider"] = "STATIC"
    beam["collider"] = "KINEMATIC"


def build_spinning_bar():
    yellow = mat("MAT_SPINNER", (0.95, 0.75, 0.1, 1))
    rotor = empty("ROTATION_ROOT", (0, 0, 1.0))
    beam = cube("SPINNING_BAR", (0, 0, 1.0), (3.4, 0.22, 0.22), yellow)
    world = beam.matrix_world.copy()
    beam.parent = rotor
    beam.matrix_world = world
    rotor["rotation_axis"] = "Z"
    rotor["rotation_speed_deg_s"] = 160.0
    empty("EVENT_ANCHOR", (0, 0, 1.0))


def build_paint_gate():
    pink = mat("MAT_GATE", (0.95, 0.2, 0.6, 1))
    cube("GATE_L", (-2.2, 0, 1.8), (0.3, 0.4, 1.8), pink)
    cube("GATE_R", (2.2, 0, 1.8), (0.3, 0.4, 1.8), pink)
    cube("GATE_TOP", (0, 0, 3.5), (2.5, 0.4, 0.3), pink)
    trig = cube("TRIGGER_VOLUME", (0, 0, 1.5), (1.9, 0.5, 1.5))
    trig.hide_render = True
    trig["event"] = "paint_transform"
    empty("EVENT_ANCHOR", (0, 0, 2.0))


def build_ball_pit():
    wall = mat("MAT_PIT", (0.2, 0.55, 0.95, 1))
    for x in (-3.2, 3.2):
        cube("PIT_WALL", (x, 0, 0.7), (0.2, 3.0, 0.9), wall)
    cube("PIT_BACK", (0, 3.0, 0.7), (3.4, 0.2, 0.9), wall)
    colors = [
        mat("BALL_RED", (0.9, .1, .1, 1)),
        mat("BALL_YELLOW", (.95, .8, .1, 1)),
        mat("BALL_BLUE", (.1, .4, .95, 1)),
    ]
    for i in range(24):
        x = -2.6 + (i % 6) * 1.0
        y = -1.8 + (i // 6) * 1.0
        sphere(f"BALL_{i:02d}", (x, y, .45), .38, colors[i % 3])
    empty("EVENT_ANCHOR", (0, 0, 1.0))


def build_water_pool():
    blue = mat("MAT_WATER", (0.1, 0.55, 0.95, 0.65))
    rim = mat("MAT_POOL_RIM", (0.9, 0.9, 0.95, 1))
    cube("POOL_BOTTOM", (0, 0, -0.2), (3.5, 3.0, 0.18), rim)
    for x in (-3.5, 3.5):
        cube("POOL_SIDE", (x, 0, 0.5), (0.18, 3.1, 0.7), rim)
    cube("POOL_BACK", (0, 3.0, 0.5), (3.5, 0.18, 0.7), rim)
    water = cube("WATER_SURFACE", (0, 0, 0.22), (3.25, 2.75, 0.08), blue)
    water["event"] = "splash"
    empty("EVENT_ANCHOR", (0, 0, 0.7))


def build_cage():
    grey = mat("MAT_CAGE", (0.35, 0.38, 0.42, 1))
    for x in (-2.5, 2.5):
        for y in (-2.5, 2.5):
            cyl("CAGE_POST", (x, y, 1.6), 0.12, 3.2, grey)
    for x in [-2, -1, 0, 1, 2]:
        cyl("CAGE_BAR", (x, 2.5, 1.6), 0.09, 3.1, grey)
        cyl("CAGE_BAR", (x, -2.5, 1.6), 0.09, 3.1, grey)
    empty("DOOR_HINGE", (0, -2.5, 1.5))
    empty("EVENT_ANCHOR", (0, -2.5, 1.5))


def build_bridge():
    wood = mat("MAT_BRIDGE", (0.45, 0.22, 0.08, 1))
    for i in range(8):
        cube(f"PLANK_{i:02d}", (0, -2.8 + i * .8, 0.4), (2.2, .32, .12), wood)
    empty("EVENT_ANCHOR", (0, 0, 0.8))


def build_giant_duck():
    yellow = mat("MAT_DUCK", (1.0, 0.8, 0.05, 1))
    orange = mat("MAT_BEAK", (1.0, 0.35, 0.05, 1))
    body = sphere("DUCK_BODY", (0, 0, 1.8), 2.3, yellow)
    head = sphere("DUCK_HEAD", (0, -.4, 4.1), 1.35, yellow)
    beak = cube("DUCK_BEAK", (0, -1.65, 3.9), (1.0, .65, .3), orange)
    for o in (body, head, beak):
        o["collider"] = "STATIC"
    empty("EVENT_ANCHOR", (0, -2, 3.5))


def build_break_wall():
    brick = mat("MAT_BRICK", (0.8, 0.22, 0.12, 1))
    for z in range(4):
        for x in range(6):
            offset = 0.45 if z % 2 else 0.0
            o = cube(f"BRICK_{z}_{x}", (-2.5 + x + offset, 0, .45 + z * .85), (.46, .32, .38), brick)
            o["collider"] = "RIGID_BODY"
    empty("EVENT_ANCHOR", (0, 0, 1.6))


BUILDERS = {
    "obstacle.rotating_hammer": build_rotating_hammer,
    "obstacle.spinning_bar": build_spinning_bar,
    "obstacle.paint_gate": build_paint_gate,
    "obstacle.ball_pit": build_ball_pit,
    "obstacle.water_pool": build_water_pool,
    "obstacle.cage": build_cage,
    "obstacle.bridge": build_bridge,
    "obstacle.giant_duck": build_giant_duck,
    "obstacle.break_wall": build_break_wall,
}


def save_asset(asset_id, builder, out_dir, preview_dir):
    reset_scene()
    builder()
    setup_preview()
    bpy.context.scene["asset_id"] = asset_id
    blend_path = out_dir / (asset_id.replace(".", "_") + ".blend")
    preview_path = preview_dir / (asset_id.replace(".", "_") + ".png")
    bpy.context.scene.render.filepath = str(preview_path)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.render.render(write_still=True)
    print(f"BUILT::{asset_id}::{blend_path}::{preview_path}")


def main():
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    out_dir = Path(args.output).resolve()
    preview_dir = out_dir / "previews"
    out_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    save_asset("scene.long_slide", lambda: build_slide("straight"), out_dir, preview_dir)
    save_asset("scene.spiral_slide", lambda: build_slide("spiral"), out_dir, preview_dir)
    for scene_kind in ("paint_gate", "fountain", "cage", "key_door", "ball_pit", "giant_animal"):
        save_asset(f"scene.{scene_kind}", lambda sk=scene_kind: build_generic_scene(sk), out_dir, preview_dir)

    for asset_id, builder in BUILDERS.items():
        save_asset(asset_id, builder, out_dir, preview_dir)


if __name__ == "__main__":
    main()
