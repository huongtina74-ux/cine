from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse():
    p=argparse.ArgumentParser()
    p.add_argument("--inspection", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--names", nargs="*", default=[])
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    return p.parse_args(argv)


def bounds():
    pts=[]
    for o in bpy.data.objects:
        if o.type!="MESH" or o.hide_render:
            continue
        try:
            pts.extend([o.matrix_world @ Vector(c) for c in o.bound_box])
        except Exception:
            pass
    if not pts:
        return Vector((0,0,0)), 2.0
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return (mn+mx)*.5, max((mx-mn).x,(mx-mn).y,(mx-mn).z,1.0)


def look(obj,target):
    obj.rotation_euler=(target-obj.location).to_track_quat("-Z","Y").to_euler()


def pick_action():
    prefs=["Idle","Run","Gallop","Walk","Idle_2"]
    names=[a.name for a in bpy.data.actions]
    for p in prefs:
        for a in bpy.data.actions:
            if a.name.lower()==p.lower():
                return a
    return bpy.data.actions[0] if bpy.data.actions else None


def main():
    ns=parse()
    data=json.loads(Path(ns.inspection).read_text(encoding="utf-8"))
    wanted={x.lower() for x in ns.names}
    out=Path(ns.output); out.mkdir(parents=True,exist_ok=True)
    for row in data["assets"]:
        name=row["name"]
        if wanted and name.lower() not in wanted:
            continue
        path=Path(row["path"])
        bpy.ops.wm.open_mainfile(filepath=str(path))
        arm=next((o for o in bpy.data.objects if o.type=="ARMATURE"),None)
        action=pick_action()
        if arm and action:
            arm.animation_data_create()
            try:
                arm.animation_data.action=action
            except Exception:
                pass
            lo,hi=action.frame_range
            bpy.context.scene.frame_set(int((lo+hi)*.5))
        center,extent=bounds()
        world=bpy.context.scene.world or bpy.data.worlds.new("World")
        bpy.context.scene.world=world
        world.color=(0.05,0.05,0.05)
        key_data=bpy.data.lights.new("PREVIEW_KEY_DATA", type="AREA")
        key_data.energy=1000
        key_data.shape="DISK"
        key_data.size=max(2.5,extent)
        key=bpy.data.objects.new("PREVIEW_KEY",key_data)
        bpy.context.scene.collection.objects.link(key)
        key.location=(center.x+extent*.8,center.y-extent*1.1,center.z+extent*1.5)
        look(key,center)

        fill_data=bpy.data.lights.new("PREVIEW_FILL_DATA", type="AREA")
        fill_data.energy=500
        fill_data.size=max(2.5,extent)
        fill=bpy.data.objects.new("PREVIEW_FILL",fill_data)
        bpy.context.scene.collection.objects.link(fill)
        fill.location=(center.x-extent*.8,center.y-extent*.2,center.z+extent*.8)
        look(fill,center)

        cam_data=bpy.data.cameras.new("PREVIEW_CAMERA_DATA")
        cam_data.lens=58
        cam=bpy.data.objects.new("PREVIEW_CAMERA",cam_data)
        bpy.context.scene.collection.objects.link(cam)
        cam.location=(center.x+extent*1.35,center.y-extent*1.7,center.z+extent*.85)
        look(cam,center)
        bpy.context.scene.camera=cam
        scene=bpy.context.scene
        scene.render.engine="BLENDER_EEVEE_NEXT"
        scene.render.resolution_x=360; scene.render.resolution_y=360; scene.render.resolution_percentage=100
        scene.render.image_settings.file_format="PNG"
        source_group = path.parent.parent.name if path.parent.name.lower() == "blends" else path.parent.name
        dst=out/(source_group+"__"+name+".png")
        scene.render.filepath=str(dst)
        bpy.ops.render.render(write_still=True)
        print("PREVIEW",name,dst,flush=True)


if __name__=="__main__":
    main()
