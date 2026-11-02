"""Single-source Slow English A2 / Bell & Leaf production profile consistency guard.

The *active* Slow English A2 config is the Bell & Leaf project. Historical
Mia/Grandpa Walter/Biscuit episode files are left intact, but they may NOT be
silently re-rendered with the Bell & Leaf canonical profile.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = "config/niches/slow_english_a2"
CHAR_LOCK = ".claude/skills/cine-a2-muse-reference-anchoring/canon/CHARACTER_CURRENT_SOURCE_LOCK_V1_2.json"
PLACE_LOCK = ".claude/skills/cine-bellfern-location-multiview-lock/registry/CINE_LOCATION_PROP_REGISTRY_v1_1_DRAFT.json"
TAGS = ("bo","me","juno","Lia","bubu","bix","ongngoai","bangoai","ongnoi","banoi")
CORE_TAGS = tuple(x for x in TAGS if x != "bangoai")
PROJECT_ID = "slow_english_a2_bell_leaf"
SUBNICHE = "magical_witch_family_stories"
LEGACY = ("mia","grandpa","biscuit","walter","ken_burns")
DESCRIPTIONS = {
 "bo":("Evan","adult father and postman, around forty, practical, affectionate, not aware of the family magic","adult male with textured curly dark hair and natural warm features, exactly as in the original user-authored Evan character sheet","postal gear with messenger bag, navy or earth-tone clothing matching the approved original user sheet","adjusts mail bag strap, pauses to check address, gentle practical smile"),
 "me":("Mara","adult mother, knowledgeable witch who protects the family","adult woman with curled brown hair and original full-body proportions and distinctive features from Mara source sheet","original Mara blue/gold/earth-toned layered workshop clothes, not Mia raincoat","calm protective gestures; precise magical hand movements"),
 "juno":("Juno","13-year-old son, careful inventor and beginner in magic","13-year-old boy with dark tousled curly hair, original teen face and height from Juno source sheet","original inventor outfit with dark jacket, belt, backpack or repair gear","tests an invention cautiously, checks a dial, thoughtful expression"),
 "Lia":("Lia","11-year-old daughter, animal empath, adventurous and kind","11-year-old girl with distinctive brown curls and original youthful proportions","original earth-toned detailed adventure dress and outerwear from the source sheet","kneels to help animals, curious hand gesture, honest emotional reactions"),
 "bubu":("Bubu","small purple magical cat spirit, playful and mischievous","purple and white cat with original proportions, a visibly spiralling PURPLE TAIL with sparkles","ONE collar bell; no additional bells","sparkling curled tail in every visible rear or side pose; alert ears and expressive eyes"),
 "bix":("Bix","tiny turtle-pangolin mechanical companion, Juno's logical helper","small rounded articulated mechanical turtle-pangolin, expressive light face and original brass/blue body","original compact robot shells and fittings; NO collar bell or chest bell","careful precise mechanical arm movement and dry-humor expression"),
 "ongngoai":("Orin","maternal grandfather, senior wizard seeking his lost family","elder wizard with long silver hair, beard and original aged facial features","rich blue embroidered cloak and ONE personal travel bell","considered gestures, serious but warm gaze"),
 "bangoai":("Maternal Grandmother","lost Veylora relative; appearance only upon a specific approved arc reveal","elderly dignified silver-haired woman from the original source sheet","original intricate older-witch robe, wardrobe colors locked to the source","measured tender movement; never introduce before the story allows"),
 "ongnoi":("Paternal Grandfather","ordinary Earth grandfather, cheerful, not aware of family magic","warm older man with glasses and gray/white hair, original face and proportions","original Earth clothing in brown and moss green","gentle humor, warm body language, no magic"),
 "banoi":("Paternal Grandmother","ordinary Earth grandmother, nurturing and witty, not aware of family magic","older gray-haired woman with glasses, original face, stature and curls","original patterned dresses and cardigan","warm humorous expression, caring daily gestures; no magic")
}

def _read_json(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(root=ROOT):
    root=Path(root)
    prod=_read_json(root/BASE/"production.json")
    char=_read_json(root/CHAR_LOCK)
    loc=_read_json(root/PLACE_LOCK)
    voice=_read_json(root/BASE/"voice_registry.json")
    visual=yaml.safe_load((root/BASE/"visual_bible.yaml").read_text(encoding="utf-8")) or {}
    toolkit=yaml.safe_load((root/BASE/"toolkit.yaml").read_text(encoding="utf-8")) or {}
    return prod,char,loc,voice,visual,toolkit

def build_visual(root=ROOT):
    prod,char,loc,voice,_,_=load(root)
    source_root=prod["source_registries"]["physical_character_files"].strip("/")
    characters=[]
    for tag in TAGS:
        name,role,identity,wardrobe,action=DESCRIPTIONS[tag]
        original=char["characters"][tag]["locked_identity_original"]
        ref=f'{source_root}/{original["path"]}'
        characters.append({
            "id":tag,"name":name,"tag":tag,"identity":identity+"; "+role,
            "wardrobe":wardrobe,"hook":role,
            "interaction":action,
            "expressions":"Curious, worried, joyful, surprised, thoughtful; preserve source face identity and age.",
            "canonical":f"{name}; {identity}; {wardrobe}; only original user source is authoritative.",
            "references":[ref],"references_status":"ORIGINAL_SOURCE_PENDING_LOCAL_INSTALL",
            "original_sha256":original["sha256"],
            "story_permission":"ARC_REVEAL_ONLY" if tag=="bangoai" else "USE_ONLY_WHEN_ACTIVE_TAG_IN_SHOT",
            "image_generation_approved":False
        })
    return {
       "series_id":"bell_leaf","project_id":PROJECT_ID,"parent_niche_id":"slow_english",
       "niche_id":"slow_english_a2","subniche_id":SUBNICHE,
       "canon_source":"config/niches/slow_english_a2/production.json",
       "character_registry":CHAR_LOCK,"location_registry":PLACE_LOCK,
       "style":"Bell & Leaf original family-magic cinematic 3D CGI: rich refined real-world materials, faithful original faces and body sizes; restrained natural bright palette, no amber global grade.",
       "render_tech":"Premium physically-based stylized CGI, plausible skin, fur, fabric and metal shading; single uninterrupted 16:9 shot with shot-specific acting.",
       "palette":{"sky":"#94C8E4","grass":"#78AA7A","wood":"#92775C","stone":"#A3A3A2","accent_purple":"#9569C2"},
       "lighting":"Neutral D55 daylight approximately 5500K, softly balanced; absolutely no global yellow/orange cast.",
       "camera":{
          "lens_mm":50,"f_stop":1.8,"dof":"slight background blur, subjects sharp",
          "shot_sizes":["establishing wide","two-shot","medium","close-up","insert"],
          "heights":["eye-level","motivated low or high only when story calls for it"],
          "moves":["static with acting","motivated slow dolly","motivated tracking shot","character-following pan"],
          "rules":["Exactly 10.0 seconds per shot; continuous performance, not freeze or Ken Burns filler",
                   "True physical reverse angle, never mirror-flipped",
                   "Location view comes from selected approved reference plate, not concept montage",
                   "Only characters listed in explicit activeCharacterTags are present",
                   "No camera-only zoom substituted for meaningful acting"]
       },
       "direction":{"pipeline":"reference_locked_10s_i2v","shot_cards_required":True,
         "prompt_notes":"Bell & Leaf; D55 neutral daylight; 50mm mild DoF; independent full-bleed 16:9; exact original characters, topology, costume; active tags only; expressive acting; no burned-in subtitles; no Ken Burns."},
       "typography":{"caption_box":False,"on_image_text":False,"subtitles_in_image":False},
       "characters":characters,
       "guest_characters":{"rule":"New guest is a role, not a replacement for locked family; obtain explicit source-approved identity and geography before rendering."},
       "locations":{"site_count":len(loc["sites"]),"site_ids":[s["site_id"] for s in loc["sites"]],
         "registry":PLACE_LOCK,"independent_room_plates_target":483,"independent_prop_plates_target":756,
         "concept_sheets_approved_as_production_plates":False},
       "voice":{"voice_registry":"config/niches/slow_english_a2/voice_registry.json",
         "no_narrator":True,"voice_casting_descriptions_complete":len(voice["voices"])==10,"approved_WAV_count":0},
       "prompt_rules":[
          "One shot is exactly one continuous single-line Flow image prompt and one separate single-line Muse video prompt, with exactly one blank line between shots",
          "ACTIVE TAGS FOR THIS SHOT explicit; character, site, space and physical view from Canon registry",
          "Bubu purple spiral tail sparkle and ONE collar bell; Bix NO bell",
          "One cinematic image, never split-screen, collage or identity sheet in actual shot",
          "Dialogue must use approved matching character WAV and real measured lip sync, no narrator",
          "Do not overlay captions, watermarks or fonts on the generated image"
       ],
       "negative":["Mia","Grandpa Walter","Biscuit","Ken Burns","narrator",
         "golden yellow color cast","contact sheet","mirrored reverse","overlaid subtitles","deformed face"]
    }

def build_toolkit():
    def held(id,kind,notes):
        return {"id":id,"kind":kind,"commercial":True,"production":False,"requires":[],
                "notes":notes+" Candidate only; needs model license/rights, reference, media and human QC approval before commercial execution."}
    return {
       "niche":"slow_english_a2","series_id":"bell_leaf",
       "project_id":PROJECT_ID,"subniche_id":SUBNICHE,
       "label":"Bell & Leaf — Slow English A2 Magical Family",
       "targets":{"language":"en-US","level":"A2","aspect":"16:9","resolution":[1920,1080],
                  "shot_duration_seconds":10,"no_narrator":True,
                  "voice_wpm":"TBD after audition and measured A2 listening QC"},
       "stages":{
           "tts":[held("voxcpm2_ten_voice_master","external_verified_wav","Requires ten approved and licensed voice reference WAVs; casting prompts are not WAV evidence")],
           "image":[held("flow_source_locked_image","external_manual","Requires original character sheets and independently approved location plate; never collage")],
           "motion":[held("muse_10s_i2v","external_manual","Requires actual 10-second motion/lip-sync evaluation; Ken Burns forbidden")],
           "hero_motion":[held("muse_10s_acting","external_manual","All character shots require real animation and acting; no three-hero-clip shortcut")],
           "music":[held("licensed_original_score","external_manual","Music must be licensed and matched to the episode")],
           "subtitles":[held("separate_yt_caption_track","artifact_only","Only separate accessible captions after final audio align; no burned-in image subtitles")]
       },
       "hold":[{"id":s,"reason":"Historical Mia/narrator/Ken Burns pipeline is not Bell & Leaf Canon"} for s in ("kokoro","piper","tone_stub","ken_burns","title_cards","manual_drop","owner_clips")],
       "production_policy":"FAIL_CLOSED_UNTIL_REAL_ASSET_AND_VOICE_APPROVAL",
       "references":"config/niches/slow_english_a2/production.json"
    }

def audit(root=ROOT):
    root=Path(root)
    p,c,l,v,b,t=load(root)
    failures=[];blockers=[]
    def must(cond,code):
        if not cond:failures.append(code)
    must(p.get("project_id")==PROJECT_ID and p.get("subniche_id")==SUBNICHE,"PRODUCTION_PROJECT_WRONG")
    must(tuple(p.get("active_tags",[]))==TAGS,"CANON_TAGS_WRONG")
    must(tuple(c.get("tags",[]))==TAGS,"CHARACTER_LOCK_TAGS_WRONG")
    must(b.get("project_id")==PROJECT_ID and b.get("subniche_id")==SUBNICHE,"ACTIVE_VISUAL_ID_WRONG")
    ids=[x.get("id") for x in b.get("characters",[])]
    must(tuple(ids)==TAGS,"ACTIVE_VISUAL_CHARACTERS_NOT_CANON")
    must(not set(("mia","grandpa","biscuit")) & set(ids),"LEGACY_CHARACTERS_IN_ACTIVE_VISUAL")
    must(len(l.get("sites",[]))==12 and len(l.get("spaces",[]))==69 and len(l.get("props",[]))==108,"LOCATION_REGISTRY_COUNTS_WRONG")
    must(b.get("locations",{}).get("site_ids")==[s["site_id"] for s in l["sites"]],"LOCATION_IDS_WRONG")
    must(b.get("voice",{}).get("no_narrator") is True,"VISUAL_NARRATOR_NOT_DISABLED")
    must(t.get("targets",{}).get("no_narrator") is True and t.get("targets",{}).get("shot_duration_seconds")==10,"TOOLKIT_LEGACY_TIMING_OR_NARRATOR")
    must(t.get("subniche_id")==SUBNICHE,"TOOLKIT_WRONG_SUBNICHE")
    for stage,tools in t.get("stages",{}).items():
        if stage in ("tts","motion","hero_motion") and any(x.get("production") for x in tools):
            failures.append("UNAPPROVED_MEDIA_TOOL_ACTIVE:"+stage)
        if any(x.get("id") in ("ken_burns","owner_clips") for x in tools):
            failures.append("LEGACY_CAMERA_MOTION_ACTIVE:"+stage)
    approved=sum(x.get("approval_status")=="APPROVED" for x in v["voices"].values())
    if approved<10:blockers.append(f"VOICE_WAV_APPROVALS:{approved}/10")
    srcbase=root/p["source_registries"]["physical_character_files"]
    existing=0
    for tag in TAGS:
        original=c["characters"][tag]["locked_identity_original"]
        item=srcbase/original["path"]
        if item.is_file() and sha(item)==original["sha256"]:existing+=1
        elif item.is_file():failures.append("CHARACTER_IMAGE_HASH_MISMATCH:"+tag)
    if existing<10:blockers.append(f"ORIGINAL_SOURCE_IMAGES_INSTALLED:{existing}/10")
    if p["readiness"]["location_plates_approved"]<483:blockers.append("INDEPENDENT_ROOM_PLATES_NOT_APPROVED")
    if p["readiness"]["prop_plates_approved"]<756:blockers.append("INDEPENDENT_PROP_PLATES_NOT_APPROVED")
    if not p["readiness"]["muse_10s_e2e_verified"]:blockers.append("MUSE_10S_NOT_E2E_VERIFIED")
    return {"schema":"cine.a2.unified_profile_audit.v1","project_id":PROJECT_ID,
        "source":"CINE Windows current active Slow English A2 profile",
        "logic_consistency":"PASS" if not failures else "FAIL",
        "profile_failures":failures,"production_blockers":blockers,
        "canon_character_tags":list(TAGS),"source_character_originals_verified_on_windows":existing,
        "site_count":len(l["sites"]),"space_count":len(l["spaces"]),"prop_count":len(l["props"]),
        "approved_voice_count":approved,"production_authorized":False}

def main():
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument("--repo",type=Path,default=ROOT)
    args=pa.parse_args()
    print(json.dumps(audit(args.repo),indent=2,ensure_ascii=False))
if __name__=="__main__":main()
