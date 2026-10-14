"""v1.6.37 ORIGINAL minecraft-inspired art direction pilot.

Opens own v196 rig scene, removes the dull test classroom, adds first-party
voxel village/meadow, packed 16x16 pixel textures, cheek/brow/eye expression,
actual shoulder pivot and cinematic Eevee lighting/camera. Not a commercial
production master and NOT the exact workflow of BigSchool/Maizen.
"""
import bpy,sys,math,random,json
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/verification/v197_minecraft_art_direction"
OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene
rng=random.Random(19701)

# Only the sandboxed copy loaded with -b source .blend is modified.
for obj in list(bpy.data.objects):
    if obj.name.startswith("MC_") or obj.type in {"CAMERA","LIGHT"}:
        bpy.data.objects.remove(obj,do_unlink=True)

def colored(name,col,rough=.85,emit=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    principled=m.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value=(*col,1)
    principled.inputs["Roughness"].default_value=rough
    if emit:
        principled.inputs["Emission Color"].default_value=(*col,1)
        principled.inputs["Emission Strength"].default_value=emit
    return m

def pixel_material(name,base,seed,spread=.13):
    rand=random.Random(seed)
    image=bpy.data.images.new("ORIGINAL_16px_"+name,width=16,height=16,alpha=True)
    # Palette + tiny sparse pixels give recognisable Minecraft-style fabric.
    values=[]
    for y in range(16):
        for x in range(16):
            stripe=(1 if (x//4+y//4)%2 else -1)*.023
            fleck=(rand.choice([-.11,-.04,0.,.04,.10]) if rand.random()<.37 else 0.)
            c=[max(.02,min(1.,v+stripe+spread*fleck/.13)) for v in base]
            values.extend([*c,1.])
    image.pixels.foreach_set(values);image.pack()
    m=bpy.data.materials.new(name);m.diffuse_color=(*base,1);m.use_nodes=True
    nd=m.node_tree.nodes;nd.clear()
    tex=nd.new("ShaderNodeTexImage");tex.image=image;tex.interpolation="Closest"
    bsdf=nd.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value=.88
    out=nd.new("ShaderNodeOutputMaterial")
    lk=m.node_tree.links;lk.new(tex.outputs["Color"],bsdf.inputs["Base Color"])
    lk.new(bsdf.outputs["BSDF"],out.inputs["Surface"])
    return m

mats={
 "skin_a":pixel_material("OriginalSkinA",(.94,.67,.47),11,.035),
 "skin_b":pixel_material("OriginalSkinB",(.77,.49,.32),19,.035),
 "blue":pixel_material("OriginalCobaltHoodie",(.12,.32,.92),35),
 "yellow":pixel_material("OriginalSunnyJacket",(.94,.56,.08),43),
 "mint":pixel_material("OriginalMintShirt",(.11,.76,.47),53),
 "purple":pixel_material("OriginalVioletSleeves",(.51,.23,.76),55),
 "navy":pixel_material("OriginalDenim",(.08,.17,.34),59),
 "brown":pixel_material("OriginalBrownPants",(.29,.18,.26),69),
 "hairblue":pixel_material("OriginalBlueHair",(.08,.19,.37),71),
 "hairpurple":pixel_material("OriginalDarkVioletHair",(.25,.11,.31),79),
 "grass":pixel_material("MeadowGrass",(.18,.60,.18),81),
 "dirt":pixel_material("MeadowEarth",(.49,.32,.18),83),
 "path":pixel_material("SunlitCobblePath",(.64,.57,.43),89),
 "wood":pixel_material("WarmOakPlanks",(.64,.37,.14),97),
 "stone":pixel_material("VillageStone",(.48,.51,.54),101),
 "leaf":pixel_material("SunlitForestLeaf",(.12,.47,.18),103),
 "roof":pixel_material("TerracottaRoof",(.78,.26,.15),109),
}
mat={
 "eye":colored("OriginalEyes",(.015,.018,.023)),
 "white":colored("EyeWhite",(.96,.94,.84)),
 "blush":colored("CheekWarm",(.97,.42,.47)),
 "mouth":colored("MouthInterior",(.15,.025,.07)),
 "tongue":colored("TinyTongue",(.95,.38,.46)),
 "gold":colored("GoldTrim",(.99,.79,.18),.58),
 "glow":colored("EmeraldQuestGem",(.04,.93,.62),.16,3.2),
 "flower":colored("BrightFlower",(.98,.41,.55)),
 "sun":colored("WarmSun",(.94,.84,.51),.5),
 "water":colored("BlueWater",(.06,.58,.77),.28),
}

def cube(name,loc,size,material,bevel=0,parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object;ob.name=name
    ob.scale=tuple(float(v) for v in size)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.clear()
    ob.data.materials.append(material)
    if bevel>0:
        bevelmod=ob.modifiers.new("MicroEdgeLight",type="BEVEL")
        bevelmod.width=bevel;bevelmod.segments=1
        ob.modifiers.new("WeightedFaceNormals",type="WEIGHTED_NORMAL")
    if parent is not None:
        world=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=world
    return ob

# Replace scene test swatches with packed 16x16 original pixel materials.
actors=[
    ("mc_a_V196",-1.3,{"shirt":"yellow","pants":"navy","skin":"skin_a","hair":"hairblue","sleeve":"blue"}),
    ("mc_b_V196",1.3,{"shirt":"mint","pants":"brown","skin":"skin_b","hair":"hairpurple","sleeve":"purple"})
]
for i,(ident,x,colors) in enumerate(actors):
    torso=bpy.data.objects.get(ident+"_torso")
    head=bpy.data.objects.get(ident+"_head")
    if torso is None or head is None:raise RuntimeError("V196_SOURCE_ACTOR_RIG_MISSING")
    root=bpy.data.objects.get("CF_ACTOR_"+ident)
    for suffix,key in (("_torso","shirt"),("_head","skin"),
                       ("_armR","sleeve"),("_armL","sleeve"),
                       ("_legR","pants"),("_legL","pants"),
                       ("_hairTop","hair"),("_hairSide","hair")):
        part=bpy.data.objects.get(ident+suffix)
        if part and part.type=="MESH":
            part.data.materials.clear();part.data.materials.append(mats[colors[key]])
    for suffix in ("_eyeR","_eyeL","_mouth"):
        o=bpy.data.objects.get(ident+suffix)
        if o:bpy.data.objects.remove(o,do_unlink=True)

    # Parent shoulder pivots to actor root, preserve world geometry and
    # rotate each limb around an anatomical shoulder instead of box center.
    for lr,xside in (("R",.70),("L",-.70)):
        arm=bpy.data.objects[ident+"_arm"+lr]
        pivot=bpy.data.objects.new("ORIG_SHOULDER_"+ident+"_"+lr,None)
        scene.collection.objects.link(pivot);pivot.empty_display_size=.12
        pivot.parent=root;pivot.location=(xside,0,2.01)
        bpy.context.view_layer.update()
        world=arm.matrix_world.copy();arm.parent=pivot;arm.matrix_world=world
        poses=(.3,-.3,.18) if (i==0 and lr=="R") else (
            (-.32,.1,-.38) if i==0 else (.55,-.24,.62) )
        for f,zrot in ((1,poses[0]),(17,poses[1]),(40,poses[2]),(48,poses[0])):
            pivot.rotation_euler.y= zrot if lr=="R" else -zrot
            pivot.keyframe_insert(data_path="rotation_euler",frame=f)

    # Original expressive pixel face: eyes, brows, eyelids, cheeks and mouth
    # are all separate controllable geometry, consistent with a voxel model.
    # Head face points toward camera (-Y). Position in world coordinates.
    face_y=-.53
    for sign in (-1,1):
        xx=x+sign*.19
        cube("ORIG_EYE_WHITE_"+ident+str(sign),(xx,face_y,2.50),
             (.17,.05,.18),mat["white"])
        cube("ORIG_EYE_PUPIL_"+ident+str(sign),(xx+sign*.018,face_y-.031,2.49),
             (.082,.02,.12),mat["eye"])
        cube("ORIG_HIGHLIGHT_"+ident+str(sign),(xx-sign*.023,face_y-.05,2.53),
             (.026,.012,.034),mat["white"])
        brow=cube("ORIG_BROW_"+ident+str(sign),(xx,face_y-.02,2.70),
             (.19,.07,.05),mats[colors["hair"]])
        brow.rotation_euler.y=(.2*sign if i==0 else -.26*sign)
        cube("ORIG_BLUSH_"+ident+str(sign),
             (x+sign*.35,face_y,2.30),
             (.105,.015,.06),mat["blush"])
    if i==0:
        cube("ORIG_SMILE_"+ident,(x,face_y-.027,2.23),
             (.32,.03,.067),mat["mouth"])
        cube("ORIG_LOWER_SMILE_"+ident,(x,face_y-.055,2.19),
             (.15,.03,.027),mat["tongue"])
    else:
        cube("ORIG_SURPRISED_MOUTH_"+ident,(x,face_y-.035,2.23),
             (.16,.032,.22),mat["mouth"])
        cube("ORIG_TONGUE_"+ident,(x,face_y-.07,2.15),
             (.09,.021,.048),mat["tongue"])
    # Short pixel bangs overlapping the face for character identity.
    for j,xx in enumerate((-.33,-.16,.0,.17,.32)):
        cube("ORIG_HAIR_BANG_"+ident+str(j),
             (x+xx,-.533,2.806-((j+i)%3)*.035),
             (.18,.08,.13),mats[colors["hair"]])
    # Distinguishing clothing layers and accents.
    cube("ORIG_HOODIE_PANEL_"+ident,(x,-.316,1.55),(.42,.035,.54),
         mats[colors["sleeve"]])
    cube("ORIG_ZIPPER_"+ident,(x,-.349,1.57),(.028,.014,.47),mat["gold"])
    cube("ORIG_CREST_"+ident,(x+.17,-.353,1.70),(.16,.014,.14),
         mat["gold"] if i==0 else mat["flower"])
    for sign in (-1,1):
        cx=x+sign*.26
        cube("ORIG_SHOE_"+ident+str(sign),(cx,-.15,.15),
             (.49,.70,.24),mats[colors["hair"]])
    # Head and root motion with small anticipation and reaction.
    for f,tilt,zpos in ((1,0.,0.),(9,-.07,.03),(17,.09,.12),(28,.07,.07),(48,0.,0.)):
        root.rotation_euler.z=tilt*(1 if i==0 else -1)
        root.keyframe_insert(data_path="rotation_euler",frame=f)
        root.location.z=zpos
        root.keyframe_insert(data_path="location",frame=f)

# Original grass, cobblestone path and storybook village props.
cube("ORIGINAL_TURF_FOUNDATION",(0,1.0,-.36),(30,28,.65),mats["dirt"])
cube("ORIGINAL_GRASS_SURFACE",(0,1.0,-.02),(30,28,.18),mats["grass"])
for row in range(10):
    yy=-9+row*1.75
    for j in range(4):
        xx=(-1.4+j*.90)+rng.uniform(-.15,.15)
        stone=cube("ORIG_PATH_TILE_%d_%d"%(row,j),
            (xx,yy,.08),(.83,.98,.055),mats["path"])
        stone.rotation_euler.z=rng.uniform(-.10,.10)
for bx in (-6.4,-5.1,-3.8):
    cube("ORIG_FLOWER_RAISED_BED_"+str(bx),(bx,-.9,.20),
         (.90,.9,.18),mats["dirt"])
# Background little original voxel cottage with chimney, windows, door.
cube("ORIG_COTTAGE_BODY",(-5.0,5.5,1.55),(4.9,3.4,3.2),mats["wood"])
cube("ORIG_COTTAGE_ROOF_LEFT",(-6.3,5.5,3.5),(2.8,3.9,.55),mats["roof"])
cube("ORIG_COTTAGE_ROOF_RIGHT",(-3.7,5.5,3.5),(2.8,3.9,.55),mats["roof"])
cube("ORIG_COTTAGE_FRONT_DOOR",(-4.8,3.73,1.15),(.85,.10,2.25),mats["hairblue"])
cube("ORIG_COTTAGE_WINDOW",(-6.1,3.68,2.1),(.78,.13,.74),mat["water"])
cube("ORIG_COTTAGE_CHIMNEY",(-3.68,6.1,4.48),(.6,.6,1.35),mats["stone"])
# Several blocky stylized trees (vary sizes, coherent shading).
for i,(xx,yy,h) in enumerate(((5.3,5.6,4.8),(7.9,1.4,3.9),
                               (8.6,8.8,5.1),(-8.3,9.2,4.7),(-10.,2.4,3.6))):
    cube("ORIG_TREE_TRUNK_"+str(i),(xx,yy,h*.47),(.65,.65,h*.9),mats["wood"])
    for ii,(ox,oy,z,k) in enumerate(((0.,0.,h,1.5),(.8,0.,h+.65,1.1),(-.8,.1,h+.65,1.1),(0,0,h+1.35,.9))):
        cube("ORIG_TREE_LEAVES_%d_%d"%(i,ii),
             (xx+ox,yy+oy,z), (2.7*k,2.4*k,1.30*k),
             mats["leaf"])

# Sunlit tulips and grasses, original block silhouettes.
flowers=0
for row in range(6):
    for j in range(5):
        xx=-8+j*4.0+rng.uniform(-.35,.35)
        yy=-4.8+row*2.1+rng.uniform(-.3,.3)
        if abs(xx)<2.2 and abs(yy)<2.0:continue
        flowers+=1
        cube("ORIG_FLOWER_STALK_"+str(flowers),(xx,yy,.23),
             (.07,.07,.44),mats["leaf"])
        cube("ORIG_FLOWER_PETAL_"+str(flowers),(xx,yy,.48),
             (.28,.25,.22),mat["flower"] if flowers%2 else mat["sun"])

# Voxel quest focus: original floating emerald/light block with a sparkle.
gem=cube("ORIG_QUEST_EMERALD",(.05,-1.25,2.54),(.58,.58,.58),mat["glow"])
gem.rotation_euler=(.12,.14,math.pi/5)
for f,rot,z in ((1,0,2.48),(17,.55,2.7),(40,1.4,2.5),(48,1.7,2.48)):
    gem.rotation_euler.z=rot;gem.location.z=z
    gem.keyframe_insert(data_path="rotation_euler",frame=f)
    gem.keyframe_insert(data_path="location",frame=f)
# Floating small geometric pixel sparkles
for i in range(5):
    a=i*math.tau/5
    sparkle=cube("ORIG_SPARKLE_"+str(i),
        (.05+cos(a)*.68,-1.28,2.55+sin(a)*.60),
        (.06,.06,.14),mat["gold"])
    sparkle.rotation_euler.y=i*.4

# Cinematic camera + softly lit outdoor world.
for ob in list(bpy.data.objects):
    if ob.type=="CAMERA":bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.object.camera_add(location=(3.05,-9.2,3.95))
camera=bpy.context.object;camera.name="ORIG_CINEMATIC_QUEST_CAMERA"
target=Vector((0.,.2,1.72))
camera.rotation_euler=(target-camera.location).to_track_quat("-Z","Y").to_euler()
camera.data.type="PERSP";camera.data.lens=42
scene.camera=camera
for f,pos in ((1,(3.05,-9.2,3.95)),(48,(2.65,-8.65,3.78))):
    camera.location=pos;camera.keyframe_insert(data_path="location",frame=f)
camera.data.dof.use_dof=False
world=bpy.data.worlds.new("ORIG_CLEAR_SKY") if not scene.world else scene.world
scene.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get("Background");bg.inputs["Color"].default_value=(.35,.59,.90,1)
bg.inputs["Strength"].default_value=.85
bpy.ops.object.light_add(type="SUN",location=(1,-1,8))
sun=bpy.context.object;sun.name="ORIG_SUNLIGHT";sun.data.energy=2.4;sun.data.color=(1.0,.89,.72)
sun.rotation_euler=(.30,-.39,-.24)
bpy.ops.object.light_add(type="AREA",location=(-3.6,-4.5,7.0))
fill=bpy.context.object;fill.name="ORIG_SOFT_FILL"
fill.data.energy=920;fill.data.shape="DISK";fill.data.size=6.5
fill.rotation_euler=(Vector((0,0,1.8))-fill.location).to_track_quat("-Z","Y").to_euler()

scene.render.engine="BLENDER_EEVEE_NEXT"
scene.render.resolution_x=960;scene.render.resolution_y=540;scene.render.resolution_percentage=100
scene.render.fps=24;scene.frame_start=1;scene.frame_end=48
scene.render.image_settings.file_format="PNG";scene.render.image_settings.color_mode="RGBA"
scene.render.film_transparent=False
try:
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
except Exception:pass

# Save isolated candidate, preserving all original v196 benchmarks untouched.
blend=OUT/"minecraft_original_village_visual_pilot.blend"
scene.frame_set(17)
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
scene.render.filepath=str(OUT/"original_village_frame17.png")
bpy.ops.render.render(write_still=True)
spec={
 "project":"Original voxel quest, not competitor model copying",
 "source_scene":"owned CineFactory v196 base",
 "still_image":str((OUT/"original_village_frame17.png").resolve()),
 "still_is_pilot_not_video":True,
 "identities":["mc_a_V196","mc_b_V196"],
 "original_first_party_packed_16px_materials":sum("ORIGINAL_16px" in im.name for im in bpy.data.images),
 "expression_geometry":"new separate eyebrows/eyes/cheeks/open or smile mouth",
 "rig_change":"shoulder pivot parents in isolated pilot; not active factory",
 "world":"original village, trees, cobbles, pixel grass, flowers, emerald quest",
 "target_video_seconds":2.,
 "render_engine":"Blender Eevee Next",
 "human_creative_approval":False,
 "studio_production_ready":False,
 "competitor_video_frames_watched":False,
 "source_checkpoints_and_exact_assets_verified":False,
 "no_training_data_from_competitors":True,
}
(OUT/"visual_pilot_contract.json").write_text(json.dumps(spec,indent=2),encoding="utf-8")
print("MINECRAFT_VISUAL_PILOT",json.dumps(spec),flush=True)
