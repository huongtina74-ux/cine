"""CineFactory v1.6.29 actual Blender voxel dataset generator.

Standalone Blender 4.5 Workbench renderer; generates full RGB frames AND
separate per-actor visibility masks (occluders remain black), not projections.
Train/validation/test scenes use disjoint deterministic seeds, camera/scene
conditions and palette sets. Mask images are pixel provenance, never predicted.
Rig label identities remain synthetic; not human ground truth.
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
parser.add_argument("--output",required=True)
parser.add_argument("--train",type=int,default=48)
parser.add_argument("--val",type=int,default=12)
parser.add_argument("--test",type=int,default=20)
parser.add_argument("--width",type=int,default=384)
parser.add_argument("--height",type=int,default=256)
args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
root=Path(args.output).resolve()
root.mkdir(parents=True,exist_ok=True)

scene=bpy.context.scene
scene.render.engine="BLENDER_WORKBENCH"
scene.render.resolution_x=args.width
scene.render.resolution_y=args.height
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.film_transparent=False
scene.render.image_settings.color_depth="8"
scene.view_settings.view_transform="Standard"
scene.view_settings.look="Medium High Contrast" if "Medium High Contrast" in {it.name for it in scene.view_settings.bl_rna.properties["look"].enum_items} else "Medium High Contrast"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="OBJECT"
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.display.shading.show_object_outline=False
scene.display.shading.background_type="VIEWPORT"
scene.display.shading.background_color=(0,0,0)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def cube(name,loc,scale,col,actor=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.color=(*col,1.)
    o["actor_group"]=actor or ""
    return o

def look_at(obj,point):
    direction=Vector(point)-obj.location
    obj.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()

def make_scene(split,index):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    seed_offsets={"train":13100,"val":29100,"test":60100}
    rnd=random.Random(seed_offsets[split]+index*991)
    mode={"train":0,"val":1,"test":2}[split]
    # Different camera and stage families, no exact seed or scene reuse.
    backgrounds=[
        ((.54,.64,.79),(.43,.57,.71)),
        ((.68,.56,.44),(.48,.39,.30)),
        ((.40,.60,.45),(.27,.42,.32)),
    ]
    palette_main=[
        [(.82,.21,.19),(.19,.43,.81),(.27,.71,.31),(.73,.56,.26)],
        [(.51,.30,.73),(.93,.39,.22),(.30,.62,.61),(.80,.65,.35)],
        [(.21,.71,.67),(.65,.26,.40),(.67,.69,.22),(.39,.42,.74)],
    ]
    back,floor=backgrounds[mode]
    colors=palette_main[mode]
    cube("floor",(0,0,-.15),(40,40,.30),floor)
    cube("backwall",(0,5,4.2),(40,.12,12),back)
    for j in range(rnd.randint(2,5)):
        x=rnd.uniform(-4.6,4.6)
        y=rnd.uniform(2.8,4.45)
        h=rnd.uniform(.45,2.0)
        tone=(min(.95,back[0]+.06),min(.95,back[1]+.03),max(.15,back[2]-.05))
        cube(f"background_prop_{j}",(x,y,h/2),(rnd.uniform(.2,.7),.32,h),tone)
    actors={}
    amount=rnd.randint(2,3)
    xs=[-2.,2.] if amount==2 else [-2.65,0.,2.65]
    for i in range(amount):
        actor=f"actor_{i}"
        center_x=xs[i]+rnd.uniform(-.24,.24)
        center_y=rnd.uniform(-.52,.50)
        scale=rnd.uniform(.88,1.15)
        clothing=colors[i]
        skin=(rnd.uniform(.55,.90),rnd.uniform(.43,.74),rnd.uniform(.33,.62))
        trouser=(rnd.uniform(.13,.33),rnd.uniform(.17,.33),rnd.uniform(.16,.34))
        group=[]
        def part(n,x,y,z,sx,sy,sz,c):
            o=cube(actor+"_"+n,(center_x+x*scale,center_y+y*scale,z*scale),
                  (sx*scale,sy*scale,sz*scale),c,actor)
            group.append(o)
            return o
        part("body",0,0,1.38,1.00,.58,1.03,clothing)
        part("head",0,-.02,2.40,.84,.76,.88,skin)
        part("leg_l",-.265,0,.46,.37,.47,.91,trouser)
        part("leg_r",.265,0,.46,.37,.47,.91,trouser)
        lean=rnd.uniform(-.18,.18)
        left=part("arm_l",-.68,0,1.45,.32,.43,.93,clothing)
        right=part("arm_r",.68,0,1.45,.32,.43,.93,clothing)
        left.rotation_euler.y=lean
        right.rotation_euler.y=-lean
        part("eye_l",-.19,-.423,2.48,.105,.05,.13,(.03,.03,.035))
        part("eye_r",.19,-.423,2.48,.105,.05,.13,(.03,.03,.035))
        part("mouth",0,-.432,2.24,.26,.04,.065,(.19,.07,.09))
        if rnd.random()<.60:
            part("hair",0,-.015,2.87,.86,.80,rnd.uniform(.10,.23),(.16,.10,.08))
        if rnd.random()<.40:
            part("belt",0,-.308,1.08,.93,.055,.105,(.12,.12,.12))
        actors[actor]=[o.name for o in group]
    data=bpy.data.cameras.new("camera")
    camera=bpy.data.objects.new("camera",data)
    scene.collection.objects.link(camera)
    scene.camera=camera
    ang=rnd.uniform(-.28,.28) if mode==0 else rnd.uniform(-.35,.35) if mode==1 else rnd.uniform(-.53,.53)
    camera.location=(math.sin(ang)*rnd.uniform(6.0,8.5),
                     -rnd.uniform(10.,13.5),
                     rnd.uniform(3.4,5.8))
    target=(rnd.uniform(-.35,.35),rnd.uniform(-.15,.25),rnd.uniform(1.3,1.65))
    look_at(camera,target)
    camera.data.type="ORTHO"
    camera.data.ortho_scale=rnd.uniform(8.1,9.4) if mode<2 else rnd.uniform(8.2,10.5)
    return actors

def render_png(path,mask_actor=None):
    original_light=scene.display.shading.light
    original_shadows=scene.display.shading.show_shadows
    original_cavity=scene.display.shading.show_cavity
    original_bg=scene.display.shading.background_color[:]
    original_col={o.name:tuple(o.color) for o in scene.objects if o.type=="MESH"}
    if mask_actor is not None:
        scene.display.shading.light="FLAT"
        scene.display.shading.show_shadows=False
        scene.display.shading.show_cavity=False
        scene.display.shading.background_color=(0,0,0)
        for o in scene.objects:
            if o.type=="MESH":
                o.color=(1,1,1,1) if o.get("actor_group","")==mask_actor else (0,0,0,1)
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    for name,color in original_col.items():
        obj=bpy.data.objects.get(name)
        if obj:obj.color=color
    scene.display.shading.light=original_light
    scene.display.shading.show_shadows=original_shadows
    scene.display.shading.show_cavity=original_cavity
    scene.display.shading.background_color=original_bg

index=[]
for split,count in (("train",args.train),("val",args.val),("test",args.test)):
    for i in range(count):
        actors=make_scene(split,i)
        stem=f"{split}_{i:04d}"
        output=root/"raw"/split
        output.mkdir(parents=True,exist_ok=True)
        color=output/(stem+"_rgb.png")
        render_png(color)
        masks={}
        for actor in sorted(actors):
            path=output/(stem+"_"+actor+"_mask.png")
            render_png(path,mask_actor=actor)
            masks[actor]=str(path)
        index.append({
            "split":split,"scene_id":stem,"seed":{"train":13100,"val":29100,"test":60100}[split]+i*991,
            "width":args.width,"height":args.height,
            "image":str(color),"actor_masks":masks,
            "actor_parts":actors,
            "palette_family":{"train":"primary","val":"complementary","test":"unseen_palette"}[split],
            "rig_description":"PROCEDURAL_VOXEL_STYLIZED_DIAGNOSTIC_NOT_EXISTING_CINEFACTORY_RIG",
            "label_source":"INDEPENDENT_BLENDER_PIXEL_MASK_NOT_PROJECTED_BOX",
        })
        print("BLENDER_SCENE",split,i,"actors",len(actors),flush=True)
manifest=root/"raw"/"render_index.json"
manifest.write_text(json.dumps(index,indent=2),encoding="utf-8")
print("BLENDER_DATA_GENERATION_PASS",len(index),flush=True)
