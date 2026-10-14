"""v263 original voxel 3D mesh blockouts and editable storyboard plans.
Writes real OBJ+MTL + nine original illustrative PNG frames from original screenplay.
NEVER uses competitor screenshots, logos, skins, music, faces or third-party assets.
"""
from __future__ import annotations
import json,math,hashlib,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"data/verification/v263_maizen_full_story_assets"
MAT={
 "teal":(0.07,0.62,0.64),"navy":(0.05,0.14,0.22),"coral":(0.97,0.35,0.26),
 "cream":(0.97,0.85,0.65),"skin":(0.91,0.73,0.55),"charcoal":(0.14,0.14,0.16),
 "grey":(0.45,0.48,0.50),"stone":(0.60,0.60,0.58),"slate":(0.29,0.32,0.34),
 "brown":(0.37,0.23,0.14),"gold":(0.93,0.62,0.12),"white":(0.94,0.94,0.92),
 "water":(0.10,0.43,0.76),"cyan":(0.17,0.79,0.91),"blue":(0.20,0.24,0.92),
 "amber":(1.0,0.48,0.06),"moss":(0.24,0.40,0.18),"leaf":(0.12,0.53,0.24),
 "red":(0.88,0.12,0.17),"black":(0.04,0.05,0.05),
}
# each subpart=(piece, x,y,z, dimensions x,y,z, material)
def part(name,x,y,z,dx,dy,dz,color):
 return [name,[x,y,z],[dx,dy,dz],color]
ASSETS={
 "NOVA":[part("torso",0,1.55,0,.75,1.0,.44,"teal"),part("head",0,2.34,0,.66,.62,.60,"skin"),
         part("short_black_hair",0,2.67,-.05,.68,.19,.63,"navy"),
         part("left_arm",-.53,1.53,0,.26,.91,.36,"teal"),part("right_arm",.53,1.53,0,.26,.91,.36,"teal"),
         part("left_leg",-.20,.57,0,.30,1.01,.37,"navy"),part("right_leg",.20,.57,0,.30,1.01,.37,"navy"),
         part("left_eye",-.16,2.38,-.313,.08,.07,.02,"charcoal"),
         part("right_eye",.16,2.38,-.313,.08,.07,.02,"charcoal")],
 "PIP":[part("torso",0,1.32,0,.85,.88,.48,"cream"),part("scarf",0,1.77,-.28,.91,.14,.14,"coral"),
        part("head",0,2.0,0,.76,.69,.66,"skin"),part("hair_crown",0,2.37,0,.78,.18,.72,"brown"),
        part("left_arm",-.59,1.31,0,.30,.77,.4,"cream"),part("right_arm",.59,1.31,0,.30,.77,.4,"cream"),
        part("left_leg",-.22,.43,0,.34,.82,.42,"brown"),part("right_leg",.22,.43,0,.34,.82,.42,"brown"),
        part("left_eye",-.18,2.04,-.338,.09,.08,.015,"charcoal"),
        part("right_eye",.18,2.04,-.338,.09,.08,.015,"charcoal")],
 "WATERFALL":[part("left_cliff",-2,2,0,1,4,1.3,"slate"),part("right_cliff",2,2,0,1,4,1.3,"slate"),
              part("upper_lip",0,4.05,0,5,.38,1.3,"stone"),
              part("falling_water",0,2,0,2.9,3.8,.08,"water"),part("mist_floor",0,.22,-.30,3.6,.22,1.0,"cyan")],
 "RIVER_ROCK_SHELF":[part("ground",0,.1,0,3,.25,2,"slate"),part("shelf_left",-1,.30,-.3,1,.45,1,"stone"),
                     part("shelf_right",.7,.21,.5,.9,.34,1,"grey")],
 "BROKEN_BRIDGE":[part("left_support",-1.45,.35,0,.42,.7,.8,"brown"),part("right_support",1.5,.35,0,.42,.7,.8,"brown"),
                  part("left_rail",-1.1,.96,.39,1.3,.15,.15,"brown"),
                  part("loose_plank",-1.0,.27,0,1.15,.14,.65,"brown"),
                  part("right_plank",1.24,.18,0,.92,.14,.65,"brown")],
 "THREE_DOT_SKETCH":[part("wet_paper",0,.03,0,1,.045,.68,"cream"),
                     part("dot_one",-.27,.07,-.07,.09,.035,.09,"black"),
                     part("dot_two",0,.07,-.07,.09,.035,.09,"black"),
                     part("dot_three",.27,.07,-.07,.09,.035,.09,"black")],
 "STONE_01":[part("block_1",0,.19,0,.62,.38,.65,"stone")],
 "STONE_02":[part("block_2",0,.22,0,.68,.44,.58,"stone")],
 "STONE_03":[part("block_3",0,.18,0,.57,.36,.73,"slate")],
 "DOOR_CAVE_CODED":[part("frame_l",-1,.9,0,.2,1.8,.3,"stone"),part("frame_r",1,.9,0,.2,1.8,.3,"stone"),
    part("arch",0,1.88,0,2.3,.23,.35,"stone"),part("door",0,.92,.04,1.82,1.73,.15,"brown"),
    part("code_one",-.65,1.65,-.08,.18,.16,.08,"blue"),
    part("code_two",-0.4,1.65,-.08,.18,.16,.08,"blue"),
    part("code_three",-.15,1.65,-.08,.18,.16,.08,"blue")],
 "DOOR_WORKSHOP_FALSEWALL":[part("hinged_panel",0,1,0,1.8,2,.22,"slate"),part("hinge_l",-1.02,.8,0,.14,.22,.22,"gold"),
     part("hinge_u",-1.02,1.52,0,.14,.22,.22,"gold"),part("hidden_handle",.6,1.08,-.13,.18,.16,.08,"stone")],
 "CRYSTAL_BLUE_SOCKET":[part("socket_base",0,.17,0,.85,.34,.85,"slate"),part("crystal_mid",0,.62,0,.35,.56,.35,"blue"),
          part("crystal_top",0,1.04,0,.23,.3,.23,"cyan"),part("ground_wire",.4,.12,0,.7,.1,.12,"gold")],
 "RESET_PANEL":[part("control_panel",0,.48,0,1.5,.9,.23,"slate"),
       part("button_blue1",-.45,.58,-.16,.27,.25,.12,"blue"),
       part("button_amber",0,.58,-.16,.27,.25,.12,"amber"),
       part("button_blue2",.45,.58,-.16,.27,.25,.12,"blue")],
 "VALVE_MAIN":[part("mount",0,.68,0,.31,1.2,.3,"slate"),part("crossbar",0,1.1,-.21,.95,.18,.12,"red"),
       part("vertical",0,1.1,-.21,.19,.95,.12,"red"),part("hub",0,1.1,-.3,.3,.28,.16,"gold")],
 "HOOK_TOOL":[part("handle",0,.5,0,.14,1.05,.14,"brown"),part("hook_top",0,1.03,0,.54,.16,.15,"stone"),
      part("curved_tip",.26,.84,0,.14,.4,.15,"stone")],
 "WORKSHOP_FLOOR_DRAIN":[part("grate_frame",0,.06,0,1.8,.12,1.3,"slate")]+[
   part(f"bar_{i}",-.7+i*.35,.125,0,.11,.1,1.12,"stone") for i in range(5)],
 "RELIEF_CHANNEL":[part("stone_bottom",0,.07,0,3.0,.15,.8,"stone"),part("left_wall",0,.38,-.48,3,.7,.19,"slate"),
             part("right_wall",0,.38,.48,3,.7,.19,"slate"),part("water_flow",0,.19,0,2.8,.12,.5,"water")],
 "CATCH_GRATE":[part("rail_l",-.78,.45,0,.15,.9,.2,"grey"),part("rail_r",.78,.45,0,.15,.9,.2,"grey")]+[
   part(f"catch_bar_{i}",-.58+i*.29,.49,0,.10,.7,.13,"grey") for i in range(5)],
 "UPPER_HATCH":[part("hatch",0,.09,0,1.6,.18,1.5,"brown"),part("latch",.45,.2,0,.38,.16,.15,"gold")],
 "LOWER_TUNNEL_CLOSED":[part("sealed_wall",0,.95,0,2.2,1.9,.22,"slate"),
           part("lower_seam",0,.18,-.13,1.75,.09,.04,"amber")],
 "FOREST_TREE":[part("trunk",0,1.4,0,.44,2.8,.46,"brown"),part("leaf1",0,3.18,0,2.0,1.35,1.95,"leaf"),
     part("leaf2",0,3.9,0,1.5,1.07,1.4,"moss")],
 "AMBER_PULSE":[part("light_core",0,.4,0,.35,.8,.15,"amber"),part("light_halo",0,.4,.02,.7,1.05,.08,"gold")],
 "THREE_DOT_MARKER":[part("marker_one",-.27,.06,0,.12,.12,.07,"gold"),part("marker_two",0,.06,0,.12,.12,.07,"gold"),
                     part("marker_three",.27,.06,0,.12,.12,.07,"gold")],
 "WORKTABLE":[part("top",0,1.1,0,1.65,.13,.95,"brown")]+[
    part(f"leg_{i}",x,.56,z,.15,1.05,.15,"brown") for i,(x,z) in enumerate([(-.65,-.37),(.65,-.37),(-.65,.37),(.65,.37)])],
 "WARNING_BELL":[part("base",0,.15,0,.65,.30,.65,"slate"),part("bell",0,.53,0,.54,.46,.54,"gold"),part("top",0,.80,0,.20,.16,.20,"gold")],
 "RIVER_RIDGE":[part("ridge_base",0,.33,0,3.2,.65,1.75,"stone"),part("safe_step",-1,.6,-.3,.8,.25,.85,"grey"),
    part("safe_step_middle",0,.82,0,.8,.3,.85,"slate"),part("safe_step_end",1,1.04,.2,.8,.27,.85,"stone")],
 "SKETCH_SHELF":[part("shelf",0,1.30,0,1.2,.14,.5,"brown"),part("wall_l",-0.59,.70,0,.13,1.26,.51,"brown"),
                 part("wall_r",.59,.70,0,.13,1.26,.51,"brown")],
}
def make_mesh(asset_id,components,folder):
 verts=[];surfs=[];groups=[]
 for i,(label,xyz,dims,color) in enumerate(components):
  x,y,z=xyz;dx,dy,dz=dims
  x0=x-dx/2;x1=x+dx/2;y0=y-dy/2;y1=y+dy/2;z0=z-dz/2;z1=z+dz/2
  s=len(verts)
  verts.extend([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
                (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)])
  for face in ((1,2,3,4),(5,8,7,6),(1,5,6,2),(2,6,7,3),(3,7,8,4),(5,1,4,8)):
   surfs.append((label,color,tuple(s+j for j in face)))
 obj=folder/(asset_id+".obj")
 text=[f"# Original procedural asset: {asset_id}",f"mtllib {asset_id}.mtl",f"o {asset_id}"]
 for v in verts:text.append(f"v {v[0]:.5f} {v[1]:.5f} {v[2]:.5f}")
 for label,color,indices in surfs:
  text.extend([f"g {label}",f"usemtl {color}","f "+" ".join(map(str,indices))])
 obj.write_text("\n".join(text)+"\n",encoding="utf8")
 materials=["# Original RGB materials, no image textures"]
 for color in sorted({p[3] for p in components}):
  rgb=MAT[color]
  materials.extend([f"newmtl {color}","Kd "+" ".join(f"{i:.4f}" for i in rgb),"Ka 0.05 0.05 0.05","Ks 0.0 0.0 0.0","illum 1",""])
 (folder/(asset_id+".mtl")).write_text("\n".join(materials),encoding="utf8")
 return {"asset_id":asset_id,"file_obj":f"meshes/{asset_id}.obj",
         "material_file":f"meshes/{asset_id}.mtl","component_count":len(components),
         "vertex_count":len(verts),"face_count":len(surfs),
         "rigged":False,"animated":False,"texture_images":False,"copyright":"ORIGINAL_PROCEDURAL_GEOMETRY",
         "commercial_use_rights":"ORIGINAL_DESIGN_PENDING_HUMAN_SIMILARITY_REVIEW",
         "model_state":"EDITABLE_STATIC_VOXEL_BLOCKOUT_NOT_FINAL_CHARACTER_RIG"}
def fnt(px):
 for name in [r"C:\Windows\Fonts\arial.ttf",r"C:\Windows\Fonts\segoeui.ttf"]:
  try:return ImageFont.truetype(name,px)
  except OSError:pass
 return ImageFont.load_default()
def storyboard(shot,folder):
 w,h=1280,720
 im=Image.new("RGB",(w,h),(231,242,242))
 d=ImageDraw.Draw(im)
 sid=shot["shot_id"];n=int(sid[1:])
 d.rectangle((0,0,w,84),fill=(24,43,51))
 d.text((38,18),f"{sid}   |   {shot['start']:02d}-{shot['end']:02d}s    |    {shot['camera_intent']}",font=fnt(29),fill=(255,255,255))
 # River, cliff, waterfall and constant landmarks: schematic composition (not film frame)
 d.polygon([(0,460),(420,435),(670,500),(1280,400),(1280,575),(0,650)],fill=(48,118,164))
 for q in range(8):d.arc((q*160-60,470+q%3*14,q*160+80,525+q%3*15),15,165,fill=(164,217,237),width=4)
 d.polygon([(700,85),(1200,85),(1200,470),(905,440)],fill=(108,111,104))
 d.rectangle((850,98,1040,470),fill=(100,193,220))
 for x in (882,922,954,990):d.line([(x,109),(x+5,440)],fill=(199,235,240),width=5)
 d.ellipse((898,175,988,270),fill=(238,170,53))
 # near-bank stone ledge
 d.polygon([(0,435),(490,420),(580,485),(0,570)],fill=(112,118,99))
 # broken bridge only after shot P07
 if n>=7:
  for k in range(3):
   x=380+k*60;y=440-k*11
   d.polygon([(x,y),(x+43,y-7),(x+39,y+9),(x,y+14)],fill=(117,71,42))
  d.line([(535,400),(710,342)],fill=(108,67,41),width=13)
 # original character composition markers not final rigs
 def person(x,y,col,label,scale=1.0):
  rad=int(32*scale)
  d.ellipse((x-rad,y-2*rad,x+rad,y),fill=(249,210,163),outline=(42,49,50),width=3)
  d.rectangle((x-rad,y,x+rad,y+int(95*scale)),fill=col,outline=(42,49,50),width=3)
  d.text((x-37,y+int(96*scale)),label,font=fnt(19),fill=(25,37,37))
 person(262,292,(24,153,158),"NOVA",1.1)
 person(404,320,(247,147,90),"PIP",.95)
 if 3<=n<=7:
  x,y=491,310
  if n==3:x,y=550,440
  d.rectangle((x,y,x+96,y+57),fill=(249,233,194),outline=(65,61,49),width=3)
  for j in range(3):d.ellipse((x+17+j*29,y+20,x+25+j*29,y+28),fill=(42,44,41))
 # Director-specific editable staging sketches: nine UNIQUE visual setups,
 # not one reused frame with changing caption text.
 if n==1:
  d.line([(940,130),(950,310)],fill=(255,220,53),width=16)
  d.polygon([(950,310),(929,276),(978,276)],fill=(255,220,53))
  d.text((1024,156),"FLASH",font=fnt(28),fill=(255,255,255))
 elif n==2:
  d.ellipse((145,127,490,467),outline=(250,164,45),width=10)
  d.polygon([(470,257),(600,280),(470,304)],fill=(250,164,45))
  d.text((540,224),"Reaction",font=fnt(27),fill=(19,40,44))
 elif n==3:
  d.ellipse((407,353,626,521),outline=(255,208,61),width=9)
  d.line([(580,365),(700,240)],fill=(255,208,61),width=7)
  d.text((690,195),"Three marks",font=fnt(27),fill=(19,40,44))
 elif n==4:
  d.line([(435,328),(515,369)],fill=(255,212,57),width=12)
  d.ellipse((485,341,592,440),outline=(255,212,57),width=8)
  d.text((589,334),"Pip picks up",font=fnt(24),fill=(19,40,44))
 elif n==5:
  d.rectangle((218,112,1030,555),fill=(250,229,184),outline=(85,64,37),width=9)
  for k in range(3):d.ellipse((398+180*k,305,446+180*k,353),fill=(48,51,46))
  d.text((390,195),"THREE-DOT SKETCH - INSERT",font=fnt(37),fill=(49,47,41))
 elif n==6:
  d.ellipse((80,114,489,536),outline=(229,127,44),width=13)
  d.text((535,182),"NOVA: WARNINGS",font=fnt(30),fill=(20,39,40))
  d.line([(455,263),(610,307)],fill=(229,127,44),width=9)
 elif n==7:
  d.line([(540,325),(855,325)],fill=(248,205,43),width=15)
  d.polygon([(855,325),(808,298),(808,354)],fill=(248,205,43))
  d.text((600,266),"RIVER FORK",font=fnt(30),fill=(19,40,44))
 elif n==8:
  d.line([(410,382),(654,360)],fill=(253,102,70),width=12)
  d.line([(534,367),(568,422)],fill=(253,102,70),width=9)
  d.text((578,420),"BROKEN BRIDGE",font=fnt(29),fill=(20,39,43))
 elif n==9:
  d.line([(432,344),(610,257),(715,170)],fill=(255,220,48),width=14)
  d.polygon([(715,170),(660,190),(686,219)],fill=(255,220,48))
  d.text((510,183),"SAFER RIDGE",font=fnt(28),fill=(20,39,43))
 # frame/safe area and footer
 d.rectangle((24,101,w-24,572),outline=(255,255,255),width=6)
 d.rectangle((0,587,w,h),fill=(24,43,51))
 lines=[shot["blocking"][:120],shot.get("draft_english_voice") or "(No dialogue — visual moment)"]
 for idx,line in enumerate(lines):
  d.text((28,602+idx*45),line,font=fnt(24 if idx==0 else 22),fill=(255,255,255))
 f=folder/(sid+".png");im.save(f,optimize=True)
 return f
def make_assets(root:Path=ROOT,write:bool=False)->dict:
 screenplay=root/"data/verification/v263_maizen_full_story_assets/nova_pip_14min_shooting_script.json"
 alignment=root/"data/verification/v262_maizen_story_alignment/corrected_pilot_and_continuity.json"
 script=json.loads(screenplay.read_text(encoding="utf8"))
 source=json.loads(alignment.read_text(encoding="utf8"))
 if script["runtime_seconds"]!=840 or len(source["corrected_45s_original_pilot"]["shots"])!=9:
  raise ValueError("SCREENPLAY_AND_STORYBOARD_PROVENANCE_FAILED")
 if not write:return {"expected_assets":len(ASSETS),"expected_storyboards":9}
 base=root/"data/verification/v263_maizen_full_story_assets"
 folder=base/"meshes";folder.mkdir(parents=True,exist_ok=True)
 panel=base/"storyboard";panel.mkdir(parents=True,exist_ok=True)
 inventory=[make_mesh(name,comps,folder) for name,comps in sorted(ASSETS.items())]
 for item in inventory:
  obj=folder/(item["asset_id"]+".obj");txt=obj.read_text(encoding="utf8")
  if txt.count("\nv ")!=item["vertex_count"] or txt.count("\nf ")!=item["face_count"]:
   raise ValueError("BROKEN_OBJ_GEOMETRY:"+item["asset_id"])
  item["file_sha256"]=hashlib.sha256(obj.read_bytes()).hexdigest()
 storyboards=[storyboard(s,panel) for s in source["corrected_45s_original_pilot"]["shots"]]
 thumbs=[Image.open(p).convert("RGB") for p in storyboards]
 contact=Image.new("RGB",(1280*3,720*3))
 for i,img in enumerate(thumbs):contact.paste(img,((i%3)*1280,(i//3)*720))
 contact.save(base/"storyboard_9_shots_contact.png",optimize=True)
 frames=[{"shot_id":s["shot_id"],"time_start":s["start"],"time_end":s["end"],
          "storyboard_png":f"storyboard/{s['shot_id']}.png",
          "blocking":s["blocking"],"lens":s["camera_intent"],"source_beat":s["source_beat"],
          "actual_shot_media_exists":False} for s in source["corrected_45s_original_pilot"]["shots"]]
 (base/"storyboard_9shots_editable.json").write_text(json.dumps(
  {"schema":"cine.original.storyboard.v263","project_id":"MAI01_WATERFALL",
   "storyboard_is_schematic_not_actual_film":True,"frames":frames},ensure_ascii=False,indent=2),encoding="utf8")
 (base/"original_voxel_asset_registry.json").write_text(json.dumps(
  {"schema":"cine.original.voxel_blockout_assets.v263",
   "asset_count":len(inventory),"original_only":True,
   "art_state":"BLOCKOUT_STATIC_OBJ_NOT_PRODUCTION_READY_RIGS",
   "licensing_state":"ORIGINAL_GEOMETRY_PENDING_RIGHTS_AND_ORIGINALITY_AUDIT",
   "real_rendered_video":False,"meshes":inventory},ensure_ascii=False,indent=2),encoding="utf8")
 # Cross-tool/OS portable offline package, no third-party source material.
 package=base/"nova_pip_preproduction_blockouts_v263.zip"
 with zipfile.ZipFile(package,"w",compression=zipfile.ZIP_DEFLATED) as zipout:
  for p in [base/"nova_pip_14min_shooting_script.json",
            base/"nova_pip_14min_screenplay.md",base/"nova_pip_shot_edl.csv",
            base/"original_voxel_asset_registry.json",base/"storyboard_9shots_editable.json",
            base/"storyboard_9_shots_contact.png"]+list(folder.glob("*.obj"))+list(folder.glob("*.mtl"))+storyboards:
    zipout.write(p,arcname=p.relative_to(base).as_posix())
 return {"assets":len(inventory),"storyboard_panels":len(storyboards),
  "mesh_components":sum(x["component_count"] for x in inventory),
  "mesh_vertices":sum(x["vertex_count"] for x in inventory),
  "zip":str(package),"zip_bytes":package.stat().st_size,
  "asset_package_level":"REAL_IMPORTABLE_ORIGINAL_STATIC_BLOCKOUTS_NOT_RIGGED_OR_QC_APPROVED",
  "commercial_release_authorized":False}
if __name__=="__main__":
 r=make_assets(write=True)
 print(json.dumps(r,ensure_ascii=False))
