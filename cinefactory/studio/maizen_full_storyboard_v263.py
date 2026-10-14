"""82-shot full-episode original-IP storyboard: editable SVG plus preview PNG.
Illustrative planning boards (not AI stills, screenshot footage, or actual animation).
"""
from __future__ import annotations
from pathlib import Path
import json,math,textwrap,zipfile,html,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"data/verification/v263_maizen_full_story_assets"
WIDTH,HEIGHT=1280,720
def font(n):
 for p in (r"C:\Windows\Fonts\arial.ttf",r"C:\Windows\Fonts\segoeui.ttf"):
  try:return ImageFont.truetype(p,n)
  except OSError:pass
 return ImageFont.load_default()
def bg(name):
 n=name.lower()
 if any(x in n for x in ("cave","shaft","workshop","grate","relief","valve","symbol","lower")):
  return ("CAVE_LAB",(35,57,73),(79,100,107))
 if "river" in n or "waterfall" in n or "forest" in n:
  return ("RIVER",(119,177,176),(59,124,157))
 return ("EXTERIOR",(119,163,185),(74,125,151))
def render_frame(shot:dict,out:Path)->dict:
 sid=shot["id"];sec=shot["start"];end=shot["end"]
 setting,sky,ground=bg(shot["set"])
 im=Image.new("RGB",(WIDTH,HEIGHT),sky)
 d=ImageDraw.Draw(im)
 d.rectangle((0,460,WIDTH,592),fill=ground)
 cam=shot["camera"].upper()
 # stage cue each panel slightly different and shot-matched
 h=190 if any(c in cam for c in ("CLOSE","INSERT","DETAIL")) else 145
 w=int(h*.42)
 left=190+((sec//10)%3)*25
 right=515+((sec//9)%3)*25
 def actor(x,c,label,offset=0):
  y=443+offset
  d.ellipse((x-w//2,y-2*h,x+w//2,y-h),fill=(245,208,168),outline=(18,36,43),width=4)
  d.rectangle((x-w//2,y-h,x+w//2,y),fill=c,outline=(18,36,43),width=4)
  d.text((x-36,y+5),label,font=font(18),fill=(255,255,255))
 actor(left,(27,151,152),"NOVA",0)
 actor(right,(246,139,100),"PIP",12)
 props=shot.get("asset_refs",[])
 seen=[x for x in props if x not in ("NOVA","PIP")][:4]
 # meaningful scene labels are spatial placeholders for blockout assets, not rendered geometry
 for i,name in enumerate(seen):
  x=778+(i%2)*213;y=191+(i//2)*127
  d.rounded_rectangle((x,y,x+198,y+94),radius=9,outline=(243,207,68),width=4,fill=(36,71,85))
  for j,line in enumerate(textwrap.wrap(name.replace("_"," "),18)[:2]):
   d.text((x+12,y+15+24*j),line,font=font(18),fill=(250,238,200))
 # camera motion arrow and actor/prop relationships
 edge=500 if any(c in cam for c in ("TRACK","FOLLOW","MOVE")) else 430
 d.line([(right+70,edge),(727,edge)],fill=(252,211,55),width=9)
 d.polygon([(727,edge),(701,edge-16),(701,edge+16)],fill=(252,211,55))
 # animated background sketch cues
 if setting=="RIVER":
  for i in range(5):d.arc((i*255,445,i*255+190,530),8,175,fill=(169,218,239),width=5)
  d.polygon([(1090,115),(1240,160),(1240,450),(1095,440)],fill=(165,207,224))
 elif setting=="CAVE_LAB":
  d.line([(27,145),(970,145)],fill=(121,135,155),width=12)
  d.line([(950,145),(950,450)],fill=(121,135,155),width=12)
  d.ellipse((1028,365,1160,475),fill=(69,156,188),outline=(231,174,55),width=9)
 d.rectangle((0,0,WIDTH,82),fill=(18,39,52))
 d.text((28,16),f"{sid}  |  {sec//60:02d}:{sec%60:02d} - {end//60:02d}:{end%60:02d}  |  {shot['beat']}   |   {cam}",font=font(27),fill="white")
 d.rectangle((0,590,WIDTH,HEIGHT),fill=(18,39,52))
 description=shot["action"]
 lines=textwrap.wrap(description,99)[:2]
 for i,line in enumerate(lines):d.text((20,597+i*31),line,font=font(19),fill=(238,246,243))
 vo=shot["voice"] or "(visual beat — no spoken dialogue)"
 d.text((20,665),vo[:125],font=font(22),fill=(250,218,112))
 (out/(sid+".png")).parent.mkdir(parents=True,exist_ok=True)
 file=out/(sid+".png");im.save(file,optimize=True)
 # SVG source is editable and inspectable; all illustrative elements are original shapes.
 shape_text="".join(f'<text x="770" y="{215+i*39}" fill="#ffe0a1" font-size="18">{html.escape(v)}</text>' for i,v in enumerate(seen))
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">
 <rect width="1280" height="720" fill="#779eaa"/><rect y="445" width="1280" height="145" fill="#407d96"/>
 <rect width="1280" height="82" fill="#122734"/><text x="24" y="48" fill="#ffffff" font-size="29">{html.escape(sid+"  |  "+cam+"  |  "+str(sec)+"-"+str(end)+" s")}</text>
 <rect x="{left-40}" y="255" width="80" height="185" fill="#1b9798"/><circle cx="{left}" cy="211" r="40" fill="#f4d1a8"/>
 <rect x="{right-40}" y="270" width="80" height="170" fill="#f68b64"/><circle cx="{right}" cy="229" r="40" fill="#f4d1a8"/>
 <text x="{left-33}" y="460" font-size="19">NOVA</text><text x="{right-33}" y="460" font-size="19">PIP</text>
 <g>{shape_text}</g>
 <rect x="0" y="590" width="1280" height="130" fill="#122734"/>
 <text x="23" y="620" fill="#ffffff" font-size="19">{html.escape(description[:110])}</text>
 <text x="23" y="679" fill="#ffe0a1" font-size="22">{html.escape(vo[:115])}</text>
 </svg>'''
 (out/(sid+".svg")).write_text(svg,encoding="utf8")
 return {"shot_id":sid,"source_seconds":[sec,end],"source_beat":shot["beat"],
  "camera":shot["camera"],"scene_set":shot["set"],
  "png":"storyboard_full/"+sid+".png","editable_svg":"storyboard_full/"+sid+".svg",
  "referenced_asset_ids":shot["asset_refs"],
  "actual_media_rendered":False}
def make_full(root:Path=ROOT,write:bool=False)->dict:
 base=root/"data/verification/v263_maizen_full_story_assets"
 screenplay=json.loads((base/"nova_pip_14min_shooting_script.json").read_text(encoding="utf8"))
 registry=json.loads((base/"original_voxel_asset_registry.json").read_text(encoding="utf8"))
 shots=screenplay["shots"];asset_ids={a["asset_id"] for a in registry["meshes"]}
 if len(shots)!=82 or screenplay["runtime_seconds"]!=840:
  raise ValueError("MISSING_FULL_EPISODE_SCREENPLAY")
 if any(not set(s["asset_refs"]).issubset(asset_ids) for s in shots):
  raise ValueError("PRODUCTION_ASSET_LOOKUP_UNRESOLVED")
 if not write:return {"expected":82,"assets":len(asset_ids)}
 folder=base/"storyboard_full";folder.mkdir(parents=True,exist_ok=True)
 entries=[render_frame(s,folder) for s in shots]
 index={"schema":"cine.original.full_840s_82_shot_storyboard.v263",
   "actual_film_frames":False,"original_vector_editable":True,
   "shot_count":82,"runtime_sec":840,"asset_count":len(asset_ids),
   "g02_not_independently_approved":True,"frames":entries}
 (base/"storyboard_full_82_editable.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf8")
 # 7 review montage contact sheets, each at original 1280 panels resized
 from PIL import Image
 for batch in range(7):
  selected=entries[batch*12:(batch+1)*12]
  if not selected:break
  montage=Image.new("RGB",(1600,900),(20,36,48))
  for j,item in enumerate(selected):
   im=Image.open(base/item["png"]).convert("RGB")
   im.thumbnail((390,219))
   montage.paste(im,((j%4)*400+5,(j//4)*300+7))
  montage.save(base/f"storyboard_full_contact_{batch+1:02d}.png",optimize=True)
 final=base/"nova_pip_full_14min_preproduction_v263.zip"
 paths=[base/"nova_pip_14min_screenplay.md",base/"nova_pip_14min_shooting_script.json",
  base/"nova_pip_shot_edl.csv",base/"original_voxel_asset_registry.json",
  base/"storyboard_9shots_editable.json",base/"storyboard_full_82_editable.json",
  base/"storyboard_9_shots_contact.png",base/"g02_unsigned_independent_review_queue.json",
  base/"g02_independent_review_worklist.md"]
 paths+=list((base/"meshes").glob("*.obj"))+list((base/"meshes").glob("*.mtl"))
 paths+=list((base/"storyboard").glob("*.png"))
 paths+=list(folder.glob("*.png"))+list(folder.glob("*.svg"))
 paths+=list(base.glob("storyboard_full_contact_*.png"))
 with zipfile.ZipFile(final,"w",compression=zipfile.ZIP_DEFLATED) as archive:
  for p in paths:
   if not p.is_file():raise ValueError("MISSING_PACKAGED_DELIVERABLE:"+str(p))
   archive.write(p,p.relative_to(base).as_posix())
 with zipfile.ZipFile(final) as archive:
  if archive.testzip():raise ValueError("ZIP_INTEGRITY_FAILED")
 return {"frames":len(entries),"source_seconds":840,"editable_vectors":len(list(folder.glob("*.svg"))),
  "original_assets":len(asset_ids),"package":str(final),"bytes":final.stat().st_size,
  "production_stage":"COMPLETE_DESK_BLOCKOUT_PACKAGE_NOT_RELEASE_READY",
  "G02":"BLOCKED_INDEPENDENT_NATIVE_AV"}
if __name__=="__main__":
 print(json.dumps(make_full(write=True),ensure_ascii=False))
