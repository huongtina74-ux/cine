# Runs inside Blender. Creates a deterministic whitebox previs from a safe JSON contract.
import json, math, sys
from pathlib import Path
import bpy

args=sys.argv[sys.argv.index("--")+1:]
job=json.loads(Path(args[0]).read_text(encoding="utf-8"))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def apply_transform(obj,t):
    obj.location=t.get('location',[0,0,0]); obj.rotation_euler=t.get('rotation_euler',[0,0,0]); obj.scale=t.get('scale',[1,1,1])
for ent in job.get('entities',[]):
    prim=ent.get('primitive','cube')
    if prim=='sphere': bpy.ops.mesh.primitive_uv_sphere_add()
    elif prim=='cylinder': bpy.ops.mesh.primitive_cylinder_add()
    else: bpy.ops.mesh.primitive_cube_add()
    obj=bpy.context.object; obj.name=ent['entity_id']; apply_transform(obj,ent.get('transform',{}))
# floor
bpy.ops.mesh.primitive_plane_add(size=30); floor=bpy.context.object; floor.name='FLOOR'
# camera
bpy.ops.object.camera_add(); cam=bpy.context.object; apply_transform(cam,job.get('camera',{}).get('transform',{})); cam.data.lens=float(job.get('camera',{}).get('lens_mm',50)); bpy.context.scene.camera=cam
# light
bpy.ops.object.light_add(type='AREA', location=(2,-2,6)); bpy.context.object.data.energy=1200; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=5
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE_NEXT'; scene.render.resolution_x=int(job.get('width',640)); scene.render.resolution_y=int(job.get('height',360)); scene.render.resolution_percentage=100
scene.render.filepath=str(Path(job['output_path']))
scene.render.image_settings.file_format='PNG'; bpy.ops.render.render(write_still=True)
