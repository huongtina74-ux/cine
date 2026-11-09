#!/usr/bin/env python3
"""Bell & Leaf CINE v2.2 -> HaoHao 270 video and image prompt batch, fail-closed."""
import json,os,pathlib,re,hashlib,collections
ROOT=pathlib.Path(os.environ.get("CINE_ROOT",str(pathlib.Path(__file__).resolve().parents[2]))).resolve()
EP=ROOT/"docs/story/bell_leaf/ep001_screenplay"
OUT=ROOT/"exports/bell_leaf/EP001_HAOHAO_10S_V22_20261109"
SHOTS=json.loads((EP/"EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json").read_text(encoding="utf8"))["shots"]
STUDIO=json.loads(pathlib.Path(os.environ.get("HAOHAO_STUDIO_JSON",str(pathlib.Path(os.environ["APPDATA"])/"HaoHao/studio.json"))).read_text(encoding="utf8"))
assert len(SHOTS)==270 and STUDIO["current"]=="prj_9044dc20"
CANON={"EVAN":"Evan","MARA":"Mara","JUNO":"Juno","LIA":"Lia","BIX":"BIX","BUBU":"BUBU","ORIN":"Orin","GRANDPA_EARTH":"Arthur","GRANDMA_EARTH":"Rose","ELARA":"Elara","AILA":"Aila"}
SAVED={x["name"].lower():x for x in STUDIO["characters"]}
SETS={x["name"].lower():x for x in STUDIO["locations"]}
MAP={"BELL_KITCHEN_DAY":"BellKitchen_Day","BELL_REAR_GARDEN_DAY":"BackGarden_Day",
     "BELL_MARA_ATELIER_DAY":"MaraWorkshop_Day","BELL_FOYER_DAY":"BellFoyer_Day",
     "BELL_HOUSE_EXTERIOR_DAY":"BellLeafHouse_Exterior_Day",
     "BELL_PARENTS_BEDROOM_DAY":"EvanMaraBedroom_Day"}
EMO={"happy","sad","angry","neutral","fearful","surprised","disgusted"}
TONE={1:"mystery and intimate unease",2:"warm light family comedy",3:"fragile hope",4:"grave discovery",
5:"loving concern",6:"danger and protective courage",7:"frightened loss",8:"lonely survival",
9:"relief and grief",10:"patient earned hope",11:"loving reassurance",12:"ordinary family warmth",
13:"methodical secrecy",14:"cautious hope",15:"gentle hospitality",16:"scientific curiosity",
17:"humble admission",18:"sad remembrance",19:"urgent safe containment",20:"fear of exposing the family secret",
21:"care for living creatures",22:"respect and consent",23:"disciplined testing",
24:"relieved joy",25:"compassion",26:"honest hope",27:"quiet caution",28:"warm belonging",
29:"uncertain midnight wonder",30:"hopeful mystery"}
def tc(s):
 def f(x):return f"{x//60:02d}:{x%60:02d}"
 return f((s-1)*10)+"-"+f(s*10)
def gettime(i):
 sc=(i-1)//9+1
 if i==1:return "VEYLORA_HISTORIC_TEASER"
 if sc<3:return "EARTH_PRESENT_SAME_MORNING"
 if sc<8:return "VEYLORA_PAST"
 if sc<11:return "EARTH_ARRIVAL_PAST"
 if sc<28:return "EARTH_PRESENT_SAME_DAY"
 if sc==28:return "EARTH_PRESENT_EVENING"
 return "EARTH_PRESENT_NIGHT"
def location(row,i):
 key=row.get("location_anchor_id")
 if key in MAP:
  name=MAP[key]
  return name, bool(name.lower() in SETS and SETS[name.lower()]["views"])
 if row.get("site_id")=="VEYLORA" or i==1:return "VeyloraPast_PENDING",False
 if row.get("site_id")=="EARTH_WILDERNESS":return "EarthCreekPast_PENDING",False
 if row.get("site_id")=="ROSE":return "RoseCottage_PENDING",False
 if row.get("space_id") in ("BH-BELLCHAMBER","BH-STAIR-SECRET"):return "BellSecretStation_PENDING",False
 if row.get("space_id")=="UNREGISTERED_GUEST_REFUGE" or i==270:return "BellGuestRoom_PENDING",False
 return "OtherLocation_PENDING",False
def emo(line,action,sc):
 a=(line+" "+action).lower()
 if any(x in a for x in ["lost her","lost my","mother!","i am sorry","i miss","i cannot find"]):return "sad"
 if sc in (6,7) or any(x in a for x in ("help them get out","stay away!","i am afraid")):return "fearful"
 if sc in (2,11,12,24,28) or any(x in a for x in ("funny","i am learning","thank you","i tested","i can fix")):return "happy"
 if "really?" in a or "what is that?" in a:return "surprised"
 return "neutral"
def clean_action(src,active):
 s=re.sub(r"\s+"," ",src).strip()
 s=re.sub(r"No Evan, Juno, Lia, Bix, Bubu or Earth grandparents here\.", "",s,flags=re.I)
 s=re.sub(r"Historical station plate and costumes are not approved; video/image production blocked\.", "",s,flags=re.I)
 s=re.sub(r"Keep the saboteur unidentified\.", "",s,flags=re.I)
 s=re.sub(r"This is the real event shown in detail at SC-006, not a second disaster\.", "",s,flags=re.I)
 s=re.sub(r"By 00:15 the real question is visible: why does this normal sound hurt her\?", "",s,flags=re.I)
 s=re.sub(r"(?:MATCH CUT|COLD-OPEN)\s*/\s*", "",s,flags=re.I)
 s=re.sub(r"cut on the second note", "end this take with the second note",s,flags=re.I)
 s=re.sub(r"\b(?:EVAN|MARA|JUNO|LIA|BIX|BUBU|ORIN|ELARA|AILA|ARTHUR|ROSE)\s*(?:\([^)]*\))?\s*:\s*['\u2018\u201c].+?['\u2019\u201d]", "",s,flags=re.I)
 for k,name in CANON.items():
  if k not in active:
   s=re.sub(r"@?"+re.escape(name)+r"\b","a person off-screen",s,flags=re.I)
 s=re.sub(r"@[A-Z][A-Z0-9_]+\b","the established environment",s)
 s=re.sub(r"\b(no extra actor|live action|ASSET_PENDING|not a second disaster)\b","",s,flags=re.I)
 s=re.sub(r"\s+"," ",s).strip(" .;-")
 return s[:470].rsplit(" ",1)[0] if len(s)>470 else s
def matches_names(text):
 found=[]
 for x in STUDIO["characters"]:
  n=re.escape(x["name"])
  if re.search(r'@'+n+r'(?=$|[^A-Za-z0-9])',text,re.I) or re.search(r'(?<![A-Za-z0-9@])'+n+r'(?=$|[^A-Za-z0-9])',text):
   found.append(x["name"])
 return set(found)
def count_words(s):return len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?",s))
def one(s):return re.sub(r"\s+"," ",s).strip()
def save(name,lines):
 f=OUT/name
 f.write_text("\n\n".join(lines)+"\n",encoding="utf8",newline="\n")
 assert len([z for z in f.read_text(encoding='utf8').splitlines() if z])==len(lines)
 assert f.read_text(encoding='utf8').count("\n\n")==len(lines)-1
 assert all("\n" not in a for a in lines)
 return f
OUT.mkdir(parents=True,exist_ok=True)
videos=[];images=[];rows=[];pilot=[]
for i,row in enumerate(SHOTS,1):
 sid=f"S{i:03d}";assert sid==row["shot_id"]
 dr=row["shot_director_v2_2"];sc=(i-1)//9+1
 active=row.get("active_character_tags_candidate",[])
 visible=[CANON[x] for x in active]
 if len(set(visible))!=len(visible):raise ValueError("duplicate cast "+sid)
 dest,known=location(row,i)
 action=clean_action(dr["script_action"],active)
 speech=dr.get("speaker_utterances",[])
 speaker_set=set(x["speaker_tag"] for x in speech)
 blockers=[]
 if not known:blockers.append("LOCATION_NOT_REGISTERED_NO_OWNER_PLATE")
 if "AILA" in active:blockers.append("AILA_NO_OWNER_FACE_IN_HAOHAO")
 if "ELARA" in active:blockers.append("ELARA_PERFORMANCE_APPROVAL_PENDING")
 if any(n.lower() not in SAVED or not SAVED[n.lower()].get("images") or not pathlib.Path(SAVED[n.lower()]["images"][0]).is_file() for n in visible):
  blockers.append("MISSING_OWNER_FACE_IMAGE")
 if len(speaker_set)>1:blockers.append("MULTISPEAKER_TTS_NOT_SUPPORTED_IN_HAOHAO")
 if any(s not in active for s in speaker_set):blockers.append("OFFSCREEN_SPEAKER_NEEDS_SEPARATE_VOICE_GATE")
 if row.get("audio_only_character_tags_candidate"):blockers.append("OFFSCREEN_AUDIO_QC_PENDING")
 if i==1:blockers.append("VEY LORA HISTORICAL PLATE UNAPPROVED")
 if sc>=28 and known:blockers.append("NIGHT_VIEW_UNAPPROVED")
 if len(speaker_set)==1:
  who=next(iter(speaker_set))
  joined=" ".join(x["text"] for x in speech)
  if count_words(joined)>16:blockers.append("A2_SPEECH_TOO_LONG_FOR_10S")
 else:joined=""
 e=emo(joined,action,sc)
 charprefix=" ".join("@"+n for n in visible)
 if not charprefix:charprefix="ENVIRONMENTAL_INSERT_NO_NAMED_ACTOR"
 sfx="natural sound only from the exact scripted physical action, no unrelated bell or music masking dialogue"
 if len(speaker_set)==1 and next(iter(speaker_set)) in active:
  voice=next(iter(speaker_set))
  voice_note=f"Actual spoken text by {CANON[voice]} only: {json.dumps(joined,ensure_ascii=False)}; emotion {e}; use registered fixed TTS voice; clear General American slow A2. "
 else:
  if not speech:
   voice_note="No spoken words, expressive silent acting. "
  else:
   lines="; ".join(CANON[z["speaker_tag"]]+" ["+emo(z["text"],action,sc)+"]: "+json.dumps(z["text"],ensure_ascii=False) for z in speech if z["speaker_tag"] in active)
   voice_note=("Full SCRIPT dialogue to reconcile: "+lines+". " if lines else "")+"Multi-speaker or off-screen dialogue is pending proper fixed-voice and lipsync routing. DO NOT enqueue before approval. "
 base=(f"EP001 {sid} [{tc(i)}] SC-{sc:03d}, strictly 10.0 seconds, 16:9, 24fps; "
       f"SHOT CAST {charprefix}; EXACT SOURCE LOCATION @{dest}; TIMELINE {gettime(i)}. "
       f"Original premium stylized 3D CGI animated family movie, extremely sharp sculpted faces, unchanged owner original character likeness, body proportions, ages, hairstyles and costumes, correct connected hands and props, identical approved source architectural geometry, realistic animation-film shaders and D55 light appropriate to the story time; no redesigns. "
       f"Source physical action: {action}. "
       f"0-2s show the initial correct pose; 2-7s carry out that story action with genuinely articulated movement, hand contact, head turns, blinks and emotion; 7-10s reveal the consequence and hold the emotion with subtle natural body movement. "
       f"{voice_note}Use natural mouth and jaw motions only for the actual on-camera speaker; all others stay silent. Audio: {sfx}. "
       f"One single uninterrupted 10s animated take, 50mm cinematic composition, gentle DOF, no photo pan, no slideshow, no jumpcut, no extra faces, no captions, no 3x3 grid, no subtitles. "
       f"Request highest native provider quality, intended for 3840x2160 4K postproduction; actual native pixels must be checked by ffprobe, not asserted by text. "
       f"ACTIVE TAGS FOR THIS SHOT: [{', '.join(active)}].")
 img=(f"EP001 {sid} [FIRST FRAME], single full-bleed 16:9 CGI still; @cast {charprefix}, @set @{dest}, "
      f"Premium original stylized 3D animated family film using exact registered character and physical room source frames. "
      f"Starting pose immediately BEFORE: {action}. Hold real owner faces, hair, outfits, relative body scale, room windows, furniture, camera orientation, consistent D55 cinematic light and 50mm composition, crisp material details and natural soft shadows. "
      f"One scene and one original first-frame view; never a collage, text, grid, logo, invented face or reverse room layout. "
      f"ACTIVE TAGS FOR THIS SHOT: [{', '.join(active)}].")
 # One-line source only; never put isolated fixed TTS instruction in the file.
 base=one(base);img=one(img)
 # HaoHao's renderer scans every BARE proper name: sanitise references to people
 # outside the camera view, including words used in dialogue and negations.
 for absent in set(SAVED) - {n.lower() for n in visible}:
  proper=SAVED[absent]["name"]
  pattern=r"(?<![A-Za-z0-9])@?"+re.escape(proper)+r"(?=$|[^A-Za-z0-9])"
  base=re.sub(pattern,"the offscreen person",base,flags=re.I)
  img=re.sub(pattern,"the offscreen person",img,flags=re.I)
 actual=matches_names(base);actual_i=matches_names(img)
 if actual!={n for n in visible if n.lower() in SAVED}:blockers.append("PHANTOM_CAST_VIDEO:"+str(sorted(actual-set(visible))))
 if actual_i!={n for n in visible if n.lower() in SAVED}:blockers.append("PHANTOM_CAST_IMAGE:"+str(sorted(actual_i-set(visible))))
 if known and dest.lower() not in SETS:blockers.append("UNKNOWN_SET")
 if known and len(SETS[dest.lower()]["views"])!=1:blockers.append("NO_LOCKED_SINGLE_SET_VIEW")
 # AILA scenes remain HOLD even if someone accidentally imports a future guest image.
 status="PILOT_ONLY_REQUIRES_HUMAN_QC" if not blockers else "HOLD_DO_NOT_QUEUE"
 voice_lines=[]
 if len(speaker_set)==1 and speaker_set.issubset(set(active)):
  speaker=CANON[next(iter(speaker_set))]
  for x in speech:
   em=emo(x['text'],action,sc)
   voice_lines.append("@"+speaker+" ["+em+"]: "+json.dumps(x["text"],ensure_ascii=False))
 runtime=base+("\n"+"\n".join(voice_lines) if voice_lines else "")
 rows.append({"shot_id":sid,"scene_id":f"SC-{sc:03d}","timeline":gettime(i),
   "character_tags":active,"haohao_names":visible,"location":dest,"location_matched":known,
   "voice_speakers":sorted(speaker_set),"emotion":e,"speaker_count":len(speaker_set),
   "dialogue_plan":[{"speaker_tag":z["speaker_tag"],"haoh ao_name":CANON[z["speaker_tag"]],"text":z["text"],"emotion":emo(z["text"],action,sc),"on_camera":z["speaker_tag"] in active} for z in speech],
   "voice_runtime_lines":voice_lines,"status":status,"blockers":blockers,
   "haoh ao_runtime_prompt":runtime,"one_line_video_prompt":base,
   "video_prompt_sha256":hashlib.sha256(base.encode('utf8')).hexdigest()})
 videos.append(base);images.append(img)
 if status.startswith("PILOT") and sid in ("S002","S003","S005","S010","S011"):pilot.append(base)
save("EP001_ALL_270_VIDEO_ONE_LINE.txt",videos)
save("EP001_ALL_270_FIRST_FRAME_ONE_LINE.txt",images)
save("EP001_PILOT_ELIGIBLE_ONE_LINE.txt",pilot)
(OUT/"EP001_QC_MANIFEST.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
summary={"source":"CINE EP001 v2.2","total":270,"eligible":sum(r['status'].startswith('PILOT') for r in rows),
 "hold":sum(r['status'].startswith('HOLD') for r in rows),
 "multispeaker_hold":sum('MULTISPEAKER_TTS_NOT_SUPPORTED_IN_HAOHAO' in r['blockers'] for r in rows),
 "missing_location":sum('LOCATION_NOT_REGISTERED_NO_OWNER_PLATE' in r['blockers'] for r in rows),
 "missing_aila":sum('AILA_NO_OWNER_FACE_IN_HAOHAO' in r['blockers'] for r in rows),
 "phantom_cast":sum(any(k.startswith("PHANTOM_CAST") for k in r['blockers']) for r in rows),
 "pilot_ids":[r['shot_id'] for r in rows if r['one_line_video_prompt'] in pilot],
 "production_authorized":False,"native_4k_proven":False,"voice_lipsync_proven":False}
(OUT/"EP001_SUMMARY.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
readme=("# Bell & Leaf EP001 / HaoHao prompt batch\n\n"
"Full prompt files have exactly one physical line per shot, with exactly one blank line between shots.\n"
"NEVER PASTE ALL_270 into the live queue before reviewing EP001_QC_MANIFEST.json; many named scene and Aila reference assets are not registered. Render source first frame before final video.\n\n"
"IMPORTANT: HaoHao automatically attaches references on ANY bare registered character name, not just @ tags. "
"Each prompt is checked against intended on-camera cast. A missing scene location is an explicit _PENDING placeholder, not owner-approved artwork.\n\n"
"HaoHao fixed TTS only parses a voice line as an isolated line formatted @Juno [happy]: double-quoted English text. "
"The strict one-line source prompt does NOT by itself activate fixed voice. "
"A pilot submission converts the one-line file into a runtime prompt with separate voice line, then checks saved voicePlan. "
"The native voice replacement mode is NOT proven accurate lipsync; for two speakers in one shot the current engine is blocked. "
"Never claim native 4K just because the prompt requests it. Initial HaoHao videos measured 1248x704 24fps for 10s.\n\n"
"Run proof-of-concept only for approved pilot-eligible shots and actual owner assets. "
"All full-batch media and artistic approval flags remain false.\n")
(OUT/"README.md").write_text(readme,encoding="utf8")
print(json.dumps({"path":str(OUT),**summary,"files":[p.name for p in OUT.iterdir()]},ensure_ascii=True))
