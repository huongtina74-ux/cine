"""CineFactory v1.6.30 — actual CineFactory actor rigs + scene templates.

Loads the REAL procedural actor/scene constructors from the active animation
worker (without starting stdin render service). Full RGB + separate rendered
visible masks preserve desk/chair occlusion. No actor target boxes used at
inference. Split lineage and rig/camera families are recorded per frame.
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path
import bpy
from mathutils import Vector

parser=argparse.ArgumentParser()
parser.add_argument("--root",required=True)
parser.add_argument("--output",required=True)
parser.add_argument("--train",type=int,default=64)
parser.add_argument("--val",type=int,default=16)
parser.add_argument("--test",type=int,default=24)
parser.add_argument("--width",type=int,default=384)
parser.add_argument("--height",type=int,default=256)
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
root=Path(args.root).resolve()
out=Path(args.output).resolve()
out.mkdir(parents=True,exist_ok=True)
cfg=json.loads((out/"rig_snapshot_v190.json").read_text(encoding="utf-8"))
rigs={x["rig_id"]:x for x in cfg["rigs"]}
scene_configs={x["scene_id"]:x for x in cfg["scenes"]}
worker_path=root/"scripts"/"blender_animation_worker.py"
raw=worker_path.read_text(encoding="utf-8")
cut='emit({"type": "ready"'
assert raw.count(cut)==1
# Compiles the exact active rig/scene constructors, without the blocking
# renderer's stdin server loop. Protected repository source is not modified.
ns={"__name__":"cinefactory_worker_dataset", "__file__":str(worker_path)}
exec(compile(raw.split(cut)[0],str(worker_path),"exec"),ns)
proc_actor=ns["proc_actor"]
proc_room=ns["proc_room"]
scene=bpy.context.scene
scene.render.engine="BLENDER_WORKBENCH"
scene.render.resolution_x=args.width
scene.render.resolution_y=args.height
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="OBJECT"
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.show_object_outline=False
scene.display.shading.background_type="VIEWPORT"
scene.display.shading.background_color=(0,0,0)
scene.view_settings.view_transform="Standard"
scene.view_settings.look="Medium High Contrast"

def aim(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()

def clear_all():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for c in list(bpy.data.collections):
        if c.users==0:bpy.data.collections.remove(c)

def actor_kinematics(actor,posture,rnd):
    # Original limb geometry from real factory; controlled pose overrides
    # introduce a visible seated silhouette and cast shadows behind desk.
    if posture!="seated":return
    root_obj=actor["root"]
    root_obj.location.z-=rnd.uniform(.18,.36)
    legs=[(key,obj) for key,obj in actor["parts"].items()
          if key in ("leg.L","leg.R","RightLeg","LeftLeg")]
    for key,leg in legs:
        leg.location.y-=rnd.uniform(.15,.36)
        leg.location.z-=rnd.uniform(.12,.30)
        leg.rotation_euler.x=rnd.uniform(-.40,-.18)
    arms=[(key,obj) for key,obj in actor["parts"].items()
          if key in ("arm.R","arm.L","RightArm","LeftArm")]
    for key,arm in arms:
        arm.rotation_euler.x=rnd.uniform(-.26,.10)

def set_actors(split,index,rnd,scene_style):
    if scene_style=="MINECRAFT":
        ids=["mc_a","mc_b","mc_c","mc_crowd_1","mc_crowd_2"]
    else:
        ids=["r6_a","r6_b","r6_c"]
    amount=2 if rnd.random()<.60 else 3
    choices=rnd.sample(ids,amount)
    placements=[-2.4,0.,2.4] if amount==3 else [-1.6,1.6]
    actors={}
    postures={}
    for n,rig_id in enumerate(choices):
        actor_name=f"actor_{n}"
        rig=rigs[rig_id].copy()
        rig["height_scale"]=rnd.uniform(.88,1.10)
        yaw=rnd.uniform(-.20,.20) if split!="test" else rnd.uniform(-.33,.33)
        loc={
            "location":{"x":placements[n]+rnd.uniform(-.10,.10),
                        "y":rnd.uniform(.62,1.15),"z":0.},
            "rotation_euler":{"x":0.,"y":0.,"z":yaw},
            "scale":{"x":1.,"y":1.,"z":1.},
        }
        actor=proc_actor(actor_name,loc,rig)
        post="seated" if rnd.random()<(.68 if split!="test" else .90) else "standing"
        actor_kinematics(actor,post,rnd)
        root_obj=actor["root"]
        member_names=[]
        for obj in root_obj.children_recursive:
            if obj.type=="MESH":
                obj["actor_group"]=actor_name
                member_names.append(obj.name)
        actors[actor_name]={"rig_id":rig_id,"posture":post,"members":member_names}
        postures[actor_name]=post
    return actors

def build_frame(split,index):
    offsets={"train":19400,"val":41400,"test":76400}
    seed=offsets[split]+index*1903
    rnd=random.Random(seed)
    clear_all()
    # Heldout uses camera family / dark-light configuration not duplicated
    # in the train. All split families still share the CineFactory worker.
    style="MINECRAFT" if index%3!=2 else "ROBLOX_R6"
    scene_id="minecraft_classroom" if style=="MINECRAFT" else "roblox_classroom"
    proc_room(scene_configs[scene_id])
    actors=set_actors(split,index,rnd,style)
    for obj in scene.objects:
        if obj.type=="MESH":
            # Unlike v189 procedural proxies, material properties are created
            # by production worker's actual voxel/Roblox rig builder.
            if obj.active_material is not None:
                diffuse=obj.active_material.diffuse_color
                obj.color=(*diffuse[:3],1.)
            if not obj.get("actor_group"):
                obj["actor_group"]=""
    cam_data=bpy.data.cameras.new("CF_DATASET_CAMERA")
    camera=bpy.data.objects.new("CF_DATASET_CAMERA",cam_data)
    scene.collection.objects.link(camera)
    scene.camera=camera
    if split=="test":
        x=rnd.uniform(-4.5,4.5)
        z=rnd.uniform(1.85,4.70)
        y=rnd.uniform(-10.3,-7.0)
        look=rnd.uniform(1.60,2.25)
    else:
        x=rnd.uniform(-2.2,2.2)
        z=rnd.uniform(2.30,3.90)
        y=rnd.uniform(-11.0,-7.5)
        look=rnd.uniform(1.70,2.10)
    camera.location=(x,y,z)
    aim(camera,(rnd.uniform(-.3,.3),1.0,look))
    camera.data.type="PERSP"
    camera.data.lens=rnd.uniform(27.,34.) if split=="test" else rnd.uniform(31.,38.)
    lighting_family=("low_key" if (index%3==0) else "medium" if index%3==1 else "high_key")
    scene.display.shading.studiolight_rotate_z=rnd.uniform(-math.pi,math.pi)
    scene.display.shading.studiolight_background_alpha=0
    if lighting_family=="low_key":
        scene.display.shading.light="STUDIO"
        scene.view_settings.exposure=-.65
    elif lighting_family=="high_key":
        scene.view_settings.exposure=.42
    else:
        scene.view_settings.exposure=0.
    return {
        "split":split,"scene_id":f"{split}_{index:04d}",
        "seed":seed,"rig_family":style,
        "rig_ids":{k:v["rig_id"] for k,v in actors.items()},
        "postures":{k:v["posture"] for k,v in actors.items()},
        "actor_parts":{k:v["members"] for k,v in actors.items()},
        "lighting_family":lighting_family,
        "camera_family":"HELDOUT_WIDE_HIGH_LOW" if split=="test" else "TRAIN_FRONT_MEDIUM",
        "camera_location":list(camera.location),
        "label_source":"INDEPENDENT_BLENDER_PIXEL_MASK_NOT_PROJECTED_BOX",
        "rig_description":"ACTUAL_CINEFACTORY_WORKER_MINECRAFT_OR_ROBLOX_R6",
        "worker_sha256":__import__("hashlib").sha256(worker_path.read_bytes()).hexdigest(),
        "width":args.width,"height":args.height,
        "palette_family":{"train":"production_base_a","val":"production_base_b","test":"heldout_camera_lighting"}[split],
    }

def render_image(path,actor=None):
    old_light=scene.display.shading.light
    old_shadow=scene.display.shading.show_shadows
    old_cavity=scene.display.shading.show_cavity
    old_bg=tuple(scene.display.shading.background_color)
    old_color={o.name:tuple(o.color) for o in scene.objects if o.type=="MESH"}
    old_exposure=scene.view_settings.exposure
    if actor is not None:
        scene.display.shading.light="FLAT"
        scene.display.shading.show_shadows=False
        scene.display.shading.show_cavity=False
        scene.display.shading.background_color=(0,0,0)
        scene.view_settings.exposure=0
        for o in scene.objects:
            if o.type=="MESH":
                is_actor=o.get("actor_group","")==actor
                o.color=(1,1,1,1) if is_actor else (0,0,0,1)
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    for name,color in old_color.items():
        o=bpy.data.objects.get(name)
        if o is not None:o.color=color
    scene.display.shading.light=old_light
    scene.display.shading.show_shadows=old_shadow
    scene.display.shading.show_cavity=old_cavity
    scene.display.shading.background_color=old_bg
    scene.view_settings.exposure=old_exposure

records=[]
for split,count in (("train",args.train),("val",args.val),("test",args.test)):
    for index in range(count):
        row=build_frame(split,index)
        folder=out/"raw"/split
        folder.mkdir(parents=True,exist_ok=True)
        rgb=folder/(row["scene_id"]+"_rgb.png")
        render_image(rgb)
        masks={}
        for actor in sorted(row["rig_ids"]):
            mask=folder/(row["scene_id"]+"_"+actor+"_mask.png")
            render_image(mask,actor=actor)
            masks[actor]=str(mask)
        row["image"]=str(rgb)
        row["actor_masks"]=masks
        records.append(row)
        print("CF_REAL_RIG_DATASET",split,index,
              list(row["rig_ids"].values()),row["postures"],flush=True)
(out/"raw"/"render_index.json").write_text(json.dumps(records,indent=2),encoding="utf-8")
print("CF_REAL_RIG_DATASET_DONE",len(records),flush=True)
