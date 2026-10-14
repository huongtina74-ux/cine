"""Build once with CineFactory's real active Minecraft rigs; render SAME .blend.

Uses existing project-trusted blender_animation_worker.py constructors and v190
real-rig config, never competitor assets. No production worker/renderer modified.
All candidate renders open a common .blend bytes SHA; only Blender render engine
and render configuration differ. Does not claim cross-software benchmark.
"""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ap=argparse.ArgumentParser()
ap.add_argument("--mode",choices=["build","render"],required=True)
ap.add_argument("--root",required=True)
ap.add_argument("--out",required=True)
ap.add_argument("--engine",choices=["workbench","eevee"],default="eevee")
ap.add_argument("--fps",type=int,default=12)
ap.add_argument("--frames",type=int,default=24)
ap.add_argument("--width",type=int,default=480)
ap.add_argument("--height",type=int,default=270)
args=ap.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
ROOT=Path(args.root).resolve()
OUT=Path(args.out).resolve()
OUT.mkdir(parents=True,exist_ok=True)
assert args.frames>=12 and args.frames<=72
assert 200<=args.width<=640 and 120<=args.height<=400

def original_factory_functions():
    worker=ROOT/"scripts"/"blender_animation_worker.py"
    raw=worker.read_text(encoding="utf-8")
    marker='emit({"type": "ready"'
    if raw.count(marker)!=1:
        raise RuntimeError("WORKER_FUNCTION_BOUNDARY_CHANGED")
    ns={"__name__":"cf_v196_bench_worker","__file__":str(worker)}
    exec(compile(raw.split(marker)[0],str(worker),"exec"),ns)
    return ns["proc_room"],ns["proc_actor"]

def build():
    proc_room,proc_actor=original_factory_functions()
    data=json.loads((ROOT/"data/verification/v190_real_rig_dataset/rig_snapshot_v190.json").read_text(encoding="utf-8"))
    rig={r["rig_id"]:r for r in data["rigs"]}
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    proc_room({"procedural_kind":"classroom","style":"MINECRAFT","world_scale":1.0})
    members=[]
    fps=args.fps
    for idx,(key,px) in enumerate((("mc_a",-1.3),("mc_b",1.3))):
        trans={"location":{"x":px,"y":0.25,"z":0.0},
               "rotation_euler":{"x":0.0,"y":0.0,"z":0.0},
               "scale":{"x":1.0,"y":1.0,"z":1.0}}
        actor=proc_actor(key+"_V196",trans,rig[key])
        arm=actor["parts"]["arm.R" if idx==0 else "arm.L"]
        torso=actor["parts"]["torso"]
        for f,angle in ((1,-.24),(args.frames//2,.45 if idx==0 else -.44),(args.frames,-.22)):
            arm.rotation_euler.x=angle
            arm.keyframe_insert(data_path="rotation_euler",frame=f)
        for f,angle in ((1,-.025),(args.frames//2,.045 if idx==0 else -.04),(args.frames,-.025)):
            torso.rotation_euler.y=angle
            torso.keyframe_insert(data_path="rotation_euler",frame=f)
        members.append(key)
    bpy.ops.object.camera_add(location=(0.0,-7.2,3.20))
    camera=bpy.context.object
    camera.name="GOLDEN_LOCKED_CINEFACTORY_CAMERA"
    camera.data.type="PERSP"
    camera.data.lens=37
    target=Vector((0,0.6,1.55))
    camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
    # Camera objective same for every engine, with slight original motion.
    for f,loc in ((1,(0.0,-7.2,3.20)),
                  (args.frames,(0.1,-6.75,3.24))):
        camera.location=loc
        camera.keyframe_insert(data_path="location",frame=f)
    bpy.context.scene.camera=camera
    bpy.ops.object.light_add(type="AREA",location=(-2.9,-2.8,4.3))
    key=bpy.context.object
    key.name="GOLDEN_IDENTICAL_KEY_LIGHT"
    key.data.energy=1050
    key.data.shape="DISK";key.data.size=5.0
    key.rotation_euler=(Vector((0,0.7,1.35))-key.location).to_track_quat("-Z","Y").to_euler()
    bpy.ops.object.light_add(type="AREA",location=(3.0,-1.7,3.9))
    fill=bpy.context.object
    fill.name="GOLDEN_IDENTICAL_FILL_LIGHT"
    fill.data.energy=800
    fill.data.shape="DISK";fill.data.size=4.0
    fill.rotation_euler=(Vector((0,0.7,1.3))-fill.location).to_track_quat("-Z","Y").to_euler()
    sc=bpy.context.scene
    sc.world.color=(0.23,0.26,0.29)
    sc.render.engine="BLENDER_EEVEE_NEXT"
    sc.render.resolution_x=args.width
    sc.render.resolution_y=args.height
    sc.render.resolution_percentage=100
    sc.render.fps=fps
    sc.frame_start=1
    sc.frame_end=args.frames
    sc.render.film_transparent=False
    sc.render.image_settings.file_format="PNG"
    sc.render.image_settings.color_mode="RGB"
    try:sc.view_settings.view_transform="AgX"
    except Exception:pass
    sc.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"golden_cinefactory_original_scene.blend"))
    info={"original_content":True,"factory_character_ids":members,
          "same_scene_for_all_backends":True,"frame_start":1,
          "frames":args.frames,"fps":fps,"resolution":[args.width,args.height],
          "actor_count":len(members),"scene":"CineFactory Minecraft classroom",
          "camera_motion":"identical soft push-in",
          "worker_source":"scripts/blender_animation_worker.py",
          "not_independent_asset_or_IP_signoff":True}
    (OUT/"scene_contract_v196.json").write_text(json.dumps(info,indent=2),encoding="utf-8")
    print("GOLDEN_SCENE_BUILT",json.dumps(info),flush=True)

def render():
    sc=bpy.context.scene
    assert bpy.data.objects.get("GOLDEN_LOCKED_CINEFACTORY_CAMERA") is not None
    for actor in ("mc_a_V196","mc_b_V196"):
        assert bpy.data.objects.get("CF_ACTOR_"+actor) is not None
    assert sc.frame_end==args.frames and sc.render.fps==args.fps
    assert sc.render.resolution_x==args.width and sc.render.resolution_y==args.height
    if args.engine=="workbench":
        sc.render.engine="BLENDER_WORKBENCH"
        sc.display.shading.light="STUDIO"
        sc.display.shading.color_type="MATERIAL"
        sc.display.shading.show_shadows=True
        sc.display.shading.show_cavity=True
        sc.display.shading.show_object_outline=False
        sc.view_settings.view_transform="Standard"
    else:
        sc.render.engine="BLENDER_EEVEE_NEXT"
        sc.view_settings.view_transform="AgX"
        sc.render.engine="BLENDER_EEVEE_NEXT"
        sc.render.film_transparent=False
        eevee=getattr(sc,"eevee",None)
        if eevee is not None:
            try:eevee.taa_render_samples=16
            except Exception:pass
    output=OUT/"frames"/args.engine
    output.mkdir(parents=True,exist_ok=True)
    sc.render.image_settings.file_format="PNG"
    sc.render.image_settings.color_mode="RGB"
    sc.render.filepath=str(output/"frame_")
    sc.render.resolution_percentage=100
    print("GOLDEN_RENDER_START",args.engine,sc.render.engine,
          "from loaded same original Blender scene",flush=True)
    bpy.ops.render.render(animation=True)
    print("GOLDEN_RENDER_FINISHED",args.engine,flush=True)

if args.mode=="build":
    build()
else:render()
