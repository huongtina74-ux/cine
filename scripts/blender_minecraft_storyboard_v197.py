"""Refine ORIGINAL v197 visual candidate: emerald brightness, 3-shot coverage.

Renders actual 48-frame pilot at 960x540/24 fps; audio assembled separately.
Never touches the original v196 or production scene.
"""
import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/verification/v197_minecraft_art_direction"
scene=bpy.context.scene
gem=bpy.data.objects.get("ORIG_QUEST_EMERALD")
if gem is None:raise RuntimeError("NO_QUEST_GEM")
gem.scale=(.67,.67,.67)
mat=bpy.data.materials.get("EmeraldQuestGem")
if mat and mat.use_nodes:
    pr=mat.node_tree.nodes.get("Principled BSDF")
    pr.inputs["Emission Color"].default_value=(.0,.40,.15,1.)
    pr.inputs["Emission Strength"].default_value=.18
    pr.inputs["Base Color"].default_value=(.05,.50,.16,1.)
# Loosen over-clipped high-contrast levels.
scene.view_settings.view_transform="AgX"
try:scene.view_settings.look="AgX - Medium High Contrast"
except Exception:pass

def cam(name,position,target,lens):
    bpy.ops.object.camera_add(location=position)
    obj=bpy.context.object;obj.name=name
    obj.data.lens=lens
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    return obj
wide=bpy.data.objects.get("ORIG_CINEMATIC_QUEST_CAMERA")
wide.data.lens=39
# 3 original camera framings convey sequence: discovery -> hero reaction -> surprised partner.
close_hero=cam("ORIG_SHOT_B_HERO",(1.15,-5.45,3.26),(-1.05,-.3,2.18),57)
close_reaction=cam("ORIG_SHOT_C_REACTION",(3.4,-5.4,3.05),(1.35,0,2.08),56)
scene.timeline_markers.clear()
for i,f,c in ((1,1,wide),(2,17,close_hero),(3,33,close_reaction)):
    m=scene.timeline_markers.new("ORIG_SHOT_%02d"%i,frame=f);m.camera=c
scene.camera=wide

# Original brow and eye microgesture: quick look/eye blink as the treasure appears.
for name,obj in bpy.data.objects.items():
    if name.startswith("ORIG_EYE_WHITE_") or name.startswith("ORIG_EYE_PUPIL_"):
        original=obj.scale.copy()
        for frame,mul in ((1,1.),(20,1.),(23,.14),(25,1.),(48,1.)):
            obj.scale.z=original.z*mul
            obj.keyframe_insert(data_path="scale",frame=frame)
        obj.scale=original

scene.render.engine="BLENDER_EEVEE_NEXT"
scene.render.resolution_x=960;scene.render.resolution_y=540
scene.render.resolution_percentage=100
scene.render.fps=24
scene.frame_start=1;scene.frame_end=48
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.filepath=str(OUT/"frames"/"v197_")
(OUT/"frames").mkdir(parents=True,exist_ok=True)
scene.frame_set(17)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"minecraft_original_storyboard_3shot.blend"))
bpy.ops.render.render(animation=True)
spec={
 "status":"3_SHOT_ORIGINAL_MINECRAFT_VISUAL_PILOT_RENDERED",
 "shots":[{"start_frame":1,"camera":wide.name},
          {"start_frame":17,"camera":close_hero.name},
          {"start_frame":33,"camera":close_reaction.name}],
 "frames_expected":48,"fps":24,"resolution":[960,540],
 "art_style":"original first-party voxel village pixel texturing",
 "expressions":"facial meshes and animated blinking",
 "sound":"original procedural chime assembled separately",
 "independent_human_review":False,
 "public_licensing_review":False,
 "full_30_second_episode_ready":False,
 "professional_animated_series_approved":False,
}
(OUT/"3shot_visual_contract.json").write_text(json.dumps(spec,indent=2),encoding="utf-8")
print("V197_3SHOT_RENDER_RESULT",json.dumps(spec),flush=True)
