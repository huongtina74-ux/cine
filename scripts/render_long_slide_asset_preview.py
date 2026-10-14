from __future__ import annotations
import argparse, sys
from pathlib import Path
import bpy
from mathutils import Vector

def args():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    return p.parse_args(argv)

def reset():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

def bounds():
    pts=[]
    for o in bpy.data.objects:
        if o.type=="MESH" and not o.hide_render:
            pts.extend([o.matrix_world @ Vector(c) for c in o.bound_box])
    if not pts:
        return Vector((0,0,0)),2.0
    mn=Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return (mn+mx)*.5,max((mx-mn).x,(mx-mn).y,(mx-mn).z,1.0)

def look(o,t):
    o.rotation_euler=(t-o.location).to_track_quat("-Z","Y").to_euler()

def main():
    ns=args()
    path=Path(ns.input).resolve()
    if path.suffix.lower()==".blend":
        bpy.ops.wm.open_mainfile(filepath=str(path))
    else:
        reset()
        if path.suffix.lower() in {".glb",".gltf"}:
            bpy.ops.import_scene.gltf(filepath=str(path))
        else:
            raise SystemExit("unsupported "+path.suffix)

    if bpy.data.actions:
        action=next(iter(bpy.data.actions))
        lo,hi=action.frame_range
        bpy.context.scene.frame_set(int((lo+hi)*.5))

    center,extent=bounds()
    world=bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world=world
    world.color=(0.10,0.10,0.10)

    key_data=bpy.data.lights.new("ASSET_PREVIEW_KEY_DATA",type="AREA")
    key_data.energy=1200; key_data.size=max(3,extent)
    key=bpy.data.objects.new("ASSET_PREVIEW_KEY",key_data)
    bpy.context.scene.collection.objects.link(key)
    key.location=(center.x+extent,center.y-extent,center.z+extent*1.5)
    look(key,center)

    fill_data=bpy.data.lights.new("ASSET_PREVIEW_FILL_DATA",type="AREA")
    fill_data.energy=650; fill_data.size=max(3,extent)
    fill=bpy.data.objects.new("ASSET_PREVIEW_FILL",fill_data)
    bpy.context.scene.collection.objects.link(fill)
    fill.location=(center.x-extent,center.y,center.z+extent)
    look(fill,center)

    cam_data=bpy.data.cameras.new("ASSET_PREVIEW_CAMERA_DATA")
    cam_data.lens=55
    cam=bpy.data.objects.new("ASSET_PREVIEW_CAMERA",cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location=(center.x+extent*1.3,center.y-extent*1.8,center.z+extent*.9)
    look(cam,center); bpy.context.scene.camera=cam

    s=bpy.context.scene
    s.render.engine="BLENDER_EEVEE_NEXT"
    s.render.resolution_x=420; s.render.resolution_y=420; s.render.resolution_percentage=100
    s.render.image_settings.file_format="PNG"
    s.render.filepath=str(Path(ns.output).resolve())
    bpy.ops.render.render(write_still=True)
    print("ASSET_PREVIEW_OK::"+str(ns.output))

if __name__=="__main__":
    main()
