#!/usr/bin/env python3
"""Produce a script-faithful EP001 Muse/HaoHao 10-second prompt batch, never auto-run it.

270 shot drafts with per-shot camera/action/dialogue, exact @cast and @location,
separate structured voice lines and downstream SRT plan, plus four one-stream
review lanes. Source screenplay and current story V2 are NOT owner-approved
production masters. NO queues/accounts/proxies are modified by this script.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIND_PATH = ROOT / "docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json"
STORY_PATH = ROOT / "docs/story/bell_leaf/ep001_screenplay/EP001_STORY_V2_CONTINUITY_LOCK.json"
LEGACY_PATH = ROOT / "exports/bell_leaf/EP001_HAOHAO_10S_V22_20261109/EP001_QC_MANIFEST.json"
DEFAULT_OUT = ROOT / "exports/bell_leaf/EP001_MUSE_HAOHAO_DIRECTOR_V3_20261109"

ANIMATION_STYLE = (
    "Original premium cinematic stylized 3D family-fantasy animation, expressive "
    "owner-canon sculpted faces, consistent original design, refined feature-film "
    "materials and lighting, natural contact shadows, nuanced character animation, "
    "clean cinematic depth and detail (4K-style aesthetic, not a native 4K claim)"
)
CHARACTER_LOCK = {
    "JUNO": "Juno is a youthful 13-year-old boy, never an adult, approved dark tousled hair and exact owner face.",
    "LIA": "Lia is an 11-year-old girl, soft youthful owner face and original curls.",
    "BIX": "BIX is a compact teal-and-gold mechanical turtle-pangolin robot with NO bell, small limbs and original shell pattern.",
    "BUBU": "BUBU is the owner's purple magical cat, exactly ONE gold collar bell and continually sparkling purple spiral tail.",
    "MARA": "Mara has the owner's original adult mother face, hair and current scene outfit, not a live-action person.",
    "EVAN": "Evan has the owner's original adult father face, postal outfit only when the scene requires it.",
    "ORIN": "Orin is the original mature wizard with his locked white hair, face, outfit and one travel bell.",
    "GRANDPA_EARTH": "Arthur the Earth grandfather has the owner's fixed older face and familiar home attire, not magic-aware.",
    "GRANDMA_EARTH": "Rose the Earth grandmother has the owner's fixed older face and familiar home attire, not magic-aware.",
    "GRANDMA_MATERNAL": "Elara has the owner's original elderly witch face and exact scene-appropriate approved costume.",
}
# In CINE the real tags and display names are derived from the existing export.
CAMERA_PRESETS = {
    "reveal": ("wide to medium-wide", "35mm-equivalent", "gentle stabilized lateral drift", "grounded geography and believable scale"),
    "object": ("medium-close prop and character composition", "70mm-equivalent", "mostly locked with tiny focus correction", "hands/claws and object interaction in readable focus"),
    "dialogue": ("medium or medium-close on the actual speaker", "50mm-equivalent", "restrained push or nearly locked", "mouth and eye line always readable"),
    "emotion": ("close or medium-close", "75mm-equivalent", "locked with tiny motivated creep", "subtle eyes, brow, breath and natural facial expression"),
    "movement": ("medium-wide tracking composition", "40mm-equivalent", "short stabilized tracking movement", "feet, body and props move in physically believable space"),
    "silent": ("clear medium shot", "50mm-equivalent", "locked or minimal drift", "one clear visual cause and reaction"),
}

def flatten(x: object, limit: int = 520) -> str:
    text = re.sub(r"\s+", " ", str(x or "")).strip()
    # A single physical prompt line is the user's fixed import invariant.
    text = text.replace("\u2028", " ").replace("\u2029", " ")
    if limit and len(text)>limit:
        shortened=text[:limit]
        end=shortened.rfind(" ")
        text=(shortened[:end] if end>limit*0.7 else shortened).rstrip(" .;:,")
    return text

def clean_action(text: str) -> str:
    t = flatten(text, 1300)
    # Strip quoted speech only, preserving physical screenplay cues.
    t = re.sub(r"\b(?:JUNO|LIA|MARA|EVAN|ORIN|BIX|BUBU|ELARA|ARTHUR|ROSE|AILA|GRANDPA_EARTH|GRANDMA_EARTH):\s*['\"][^'\"]+['\"]", "", t, flags=re.I)
    t = re.sub(r"\b(?:CUT TO|MATCH CUT|HARD CUT|SMASH CUT)\b\s*[/:\-]*", "", t, flags=re.I)
    t = re.sub(r"(?i)\bcut on the second note\b", "the second note echoes", t)
    t = re.sub(r"(?i)\bthis is the real event shown in detail.*$", "", t)
    t = re.sub(r"@[A-Za-z0-9_]+", lambda m: m.group(0)[1:].replace("_", " ").title(), t)
    t = re.sub(r"\s{2,}", " ", t).strip(" .;:-")
    if len(t) > 320:
        head = t[:320]
        ends = [m.end() for m in re.finditer(r"[.!?](?=\s|$)|;(?=\s)", head)]
        cut = max(ends) if ends and max(ends) > 165 else head.rfind(" ")
        t = head[:cut].strip(" .;,:-") if cut > 0 else head
    return t

def action_focus(row: dict, source: dict) -> str:
    d = source["shot_director_v2_2"]
    raw = clean_action(d.get("script_action", ""))
    if raw:
        return raw
    # Many writer-room beats consist ONLY of dialogue. Inventing generic
    # 'turns gently and' movement makes every performance look identical.
    # Preserve its exact semantic line for actor-specific visible performance.
    speech=row.get("dialogue_plan",[])
    if speech:
        lead=speech[0]
        name=lead.get("haoh ao_name",lead.get("speaker_tag","Actor"))
        line=flatten(lead.get("text",""),120)
        if lead.get("on_camera"):
            return f"{name} directs a natural attentive gaze toward the established listener, takes a clear acting breath and physically expresses the SCRIPTED thought: {line}; only the present actor's mouth moves"
        return f"The approved visible actor reacts subtly to the actual offscreen spoken thought: {line}; do not attach the offscreen speaker's face"
    video=d.get("video",{})
    fallback=clean_action(video.get("action_2_7",""))
    return fallback if fallback and not fallback.endswith("and") else "The visible character holds a meaningful story-consistent silent reaction, with subtle real body movement"

def emotion_for(row: dict, source: dict) -> str:
    talk = row.get("dialogue_plan", [])
    if talk and talk[0].get("emotion") in ("neutral","happy","sad","angry","surprised","fearful"):
        emo = talk[0]["emotion"]
        if emo != "neutral":return emo
    text = source["shot_director_v2_2"]["script_action"].lower()
    for words, emo in [
        (("proud","smiles","laugh","joke","joy"), "warm pride and restrained delight"),
        (("worry","worried","fears","fright","tremble","crack","shakes"), "quiet worry and care"),
        (("look","watches","bird","examines","test","checks","curious","notices"), "attentive curiosity"),
        (("protect","hold","rescue","safe","careful"), "gentle protective resolve"),
        (("hesitates","remembers","pauses","scar"), "subtle bittersweet concern"),
    ]:
        if any(x in text for x in words):return emo
    return flatten(source["shot_director_v2_2"].get("emotion_target","gentle natural expression"),75)

def camera_for(source: dict, row: dict, i: int) -> tuple[str,str,str,str]:
    a = source["shot_director_v2_2"]
    text = (a.get("script_action","")+" "+a.get("image",{}).get("framing","")).lower()
    if any(x in text for x in ["wide shot","immense forest","the sky","entire hall","from a distance","distant valley"]) or re.search(r"\bestablishing\b",text):
        key="reveal"
    elif any(x in text for x in ["close-up","eye fills","tears","face tightens","hesitates","freezes","remembers"]):
        key="emotion"
    elif any(x in text for x in ["hand","claw","screw","latch","bell","cup","spoon","suitcase","hinge","letter","scarf","leaf","tray","plant","fruit","flower"]):
        key="object" if not row["voice_speakers"] else "dialogue"
    elif any(x in text for x in ["walk","runs","steps","moves","cross","climbs","carries","follows"]):
        key="movement"
    elif row["voice_speakers"]:
        key="dialogue"
    else:key="silent"
    f,l,m,c=CAMERA_PRESETS[key]
    # For the same set avoid identical perspectives on all nine scene shots.
    if key=="dialogue" and i%5==0:
        f="medium over-shoulder from approved viewing side toward the speaking face"
        m="very subtle fixed-axis forward track"
    if key=="silent" and i%4==0:
        f="medium-wide grounded establishing composition";l="35mm-equivalent"
    return f,l,m,c

def sound_for(source: dict, row: dict) -> str:
    t=source["shot_director_v2_2"].get("script_action","").lower()
    loc=row["location"].lower()
    if "spoon" in t or "clink" in t:return "one small porcelain and spoon clink, low natural room tone; clear words above FX"
    if any(s in t for s in ("bell sounds","bell rings","two-note bell","station bell")):
        return "the truthful short scripted two-note bell, controlled volume, subtle atmospheric decay"
    if "kitchen" in loc:return "low morning kitchen room tone, subtle footsteps or dishes ONLY if shown"
    if "workshop" in loc:return "soft cloth and delicate tool contact, no loud repetitive workshop machinery"
    if "garden" in loc:return "distant garden birds, faint wind and leaves below speech"
    if "creek" in loc:return "quiet gentle running water and foliage"
    if "veylora" in loc:return "restrained distant magical-world air, bell only if in this exact scene"
    return "gentle diegetic ambience tied only to visible motion; music must not mask speech"

def location_detail(row: dict, studio: dict) -> str:
    loc=row["location"]
    rec=studio.get(loc)
    if not row["location_matched"] or rec is None:
        return "LOCATION OWNER PLATE UNAPPROVED; keep story geography as a DRAFT only and DO NOT submit to Muse"
    desc=flatten(rec.get("description",""),240)
    if "REVIEW:" in desc or "CONCEPT ONLY" in desc:
        return "LOCATION OWNER ASSIGNMENT UNAPPROVED; do not render before owner approval"
    return desc

def direct_image(row:dict, src:dict, studio:dict, timeline:str, cam:tuple, castlocks:str, beat:str) -> str:
    f,l,m,c=cam
    speaker_state="silent starting pose; no speech text" if not row["voice_speakers"] else "visible mouth relaxed in the moment immediately before speaking"
    parts=[
        f"EP001 {row['shot_id']} [FIRST FRAME], 16:9 one full-bleed image, source revision V2.2, scene {row['scene_id']}, story time {timeline}",
        f"ACTIVE TAGS FOR THIS SHOT: [{', '.join(row['character_tags'])}]",
        " ".join("@"+n for n in row["haohao_names"]) or "NO VISIBLE CAST",
        f"EXACT SOURCE LOCATION @{row['location']}",
        ANIMATION_STYLE,
        "CANON SUBJECTS: "+castlocks if castlocks else "Scene insert with no additional people or creatures",
        "REGISTERED SET BRIEF, verify exact owner plate: "+location_detail(row,studio),
        f"FIRST POSE/STORY: {beat}; {speaker_state}",
        f"COMPOSITION: {f}, {l}, source-verifiable camera side and eye-height, unobstructed facial geometry and contact props",
        "one still composition, original owner face and set topology, no invented unseen angle, no extra figures, no collage, no printed words, no watermark; English subtitles are added only to final postprocessed video",
    ]
    return "; ".join(flatten(s,700) for s in parts if s)

def direct_video(row:dict,src:dict,studio:dict,timeline:str,cam:tuple,castlocks:str,beat:str,emotion:str,speech:str) -> str:
    f,l,m,c=cam
    speakers=", ".join(x.get("haoh ao_name",x["speaker_tag"]) for x in row["dialogue_plan"])
    speech_txt=("EXACT A2 spoken dialogue (only registered speakers): "+speech) if speech else "NO DIALOGUE: only the script-locked reaction and natural ambient sounds"
    parts=[
        f"EP001 {row['shot_id']} [{src['timecode']}], strictly 10.0 seconds, 16:9, 24fps, one continuous cinematic take, revision V2.2, scene {row['scene_id']}",
        f"ACTIVE TAGS FOR THIS SHOT: [{', '.join(row['character_tags'])}]",
        " ".join("@"+n for n in row["haohao_names"]) or "NO VISIBLE CAST",
        f"EXACT SOURCE LOCATION @{row['location']}, STORY TIME {timeline}",
        ANIMATION_STYLE,
        "IDENTITY LOCK: "+castlocks if castlocks else "inanimate setting insert, no extra characters",
        "REGISTERED SET BRIEF, verify source viewpoint: "+location_detail(row,studio),
        f"CAMERA: {f}, {l}, {m}, same approved axis and geography; {c}",
        f"0–2s: begin from the separately owner-validated first-frame pose, establish eye-line and original prop state",
        f"2–7s: one motivated physical beat from THIS SCRIPT ONLY: {beat}",
        f"7–10s: restrained emotionally truthful {emotion} reaction and stable end pose, ready to match next shot",
        speech_txt,
        f"VOICE PERFORMANCE: emotional direction {emotion}, recognizable age-appropriate original character delivery, plain expressive English A2, clear pronunciation, unhurried natural pause, lip motions corresponding to ACTUAL speaker; fixed voice plan delivered separately to HaoHao; never invent another speaker" if speech else "no speaking or artificial mouth movement",
        "SOUND: "+sound_for(src,row),
        "English subtitles REQUIRED in final delivered MP4 for exact accepted audio, synchronized via post-QC SRT with bottom-safe max 2 lines; DO NOT bake unreliable text into native Muse video",
        "preserve exact source faces/hair/outfit/body scale, BUBU spiral sparkle and BIX no-bell rule, stable scene architecture and prop contact; visible true 3D motion, no photo-zoom, no montage, no cut, no new room or person, no photoreal people, no watermark",
    ]
    return "; ".join(flatten(s,700) for s in parts if s)

def read_json(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def make(out:Path) -> dict:
    src=read_json(BIND_PATH)
    canon=read_json(STORY_PATH)
    previous=read_json(LEGACY_PATH)
    assert src["count"]==270 and len(src["shots"])==270
    assert len(previous)==270 and len(canon["scene_cards"])==30
    assert not canon.get("shot_reconciliation_20261109",{}).get("production_authorized", False)
    def script_hash(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
    studio_file=Path(os.environ.get("APPDATA",""))/"HaoHao/studio.json"
    if studio_file.exists():
        st=read_json(studio_file)
        studio={loc["name"]:loc for loc in st.get("locations",[])}
        installed={a["name"] for a in st.get("characters",[])}
        n_accounts=len(read_json(studio_file.parent/"accounts.json").get("accounts",[]))
    else:
        studio={};installed=set();n_accounts=0
    scenes={c["scene_id"]:c for c in canon["scene_cards"]}
    video=[];image=[];manifest=[];subtitle=[];voiceplan=[];held=[];pilot=[]
    seen_id=set()
    for index,(s,p) in enumerate(zip(src["shots"],previous),1):
        assert s["shot_id"]==p["shot_id"] and s["shot_id"]==f"S{index:03d}"
        seen_id.add(s["shot_id"])
        sc=scenes[s["scene_id"]]
        d=s["shot_director_v2_2"]
        # Story-room canon says SC001/SC002 breakfast is Earth's CURRENT morning,
        # with S001 an explicit historic 10-second teaser.
        timeline="VEYLORA_PAST" if index==1 else "EARTH_PRESENT_SAME_MORNING" if index<=18 else s["timeline"]
        timeline_conflict=timeline!=s["timeline"]
        cam=camera_for(s,p,index)
        castlocks=" ".join(CHARACTER_LOCK.get(c,"") for c in p["character_tags"])
        beat=action_focus(p,s)
        emo=emotion_for(p,s)
        dialogue=p.get("dialogue_plan",[])
        spoken=" ".join(f'{x.get("haoh ao_name",x["speaker_tag"])}: "{flatten(x["text"],170)}"' for x in dialogue)
        v=direct_video(p,s,studio,timeline,cam,castlocks,beat,emo,spoken)
        im=direct_image(p,s,studio,timeline,cam,castlocks,beat)
        assert "\n" not in v+im and "\r" not in v+im
        # Do not change or remove any inherited genuine production holds.
        blockers=list(p.get("blockers",[]))
        if timeline_conflict:blockers.append("EDITORIAL_TIMELINE_SOURCE_CONFLICT_PRESENT_MORNING")
        if p["location_matched"] and p["location"] not in studio:blockers.append("REGISTERED_HAOHAO_LOCATION_NOT_FOUND")
        missing=[n for n in p["haohao_names"] if n not in installed]
        if missing:blockers.append("HAOHAO_CAST_REFERENCE_MISSING")
        status="HOLD_DO_NOT_QUEUE" if blockers else p["status"]
        record={
            "shot_id":s["shot_id"],
            "scene_id":s["scene_id"],
            "timecode":s["timecode"],
            "script_revision":"EP001_STORY_V2_2_20261109_UNAPPROVED_DRAFT",
            "story_timeline":timeline,
            "original_source_timeline":s["timeline"],
            "original_source_timeline_conflict":timeline_conflict,
            "character_tags":p["character_tags"],
            "haohao_names":p["haohao_names"],
            "location":p["location"],
            "location_matched":p["location_matched"] and p["location"] in studio,
            "visible_cast_only":True,
            "reference_approval":"NOT_FINAL",
            "voice_speakers":p["voice_speakers"],
            "dialogue_plan":dialogue,
            "voice_runtime_lines":p["voice_runtime_lines"],
            "voice_master_approval":"0_OF_10_APPROVED",
            "on_screen_speaker_count":len(p["voice_speakers"]),
            "subtitle_plan":{
                "required":bool(p["voice_speakers"]),
                "mode":"SRT_AND_BURNED_FINAL_MP4" if p["voice_speakers"] else "NONE_FOR_SILENCE",
                "source":"FINAL_ACCEPTED_AUDIO",
                "max_lines":2,"position":"BOTTOM_SAFE_CENTER",
                "status":"PLANNED_UNTIMED_NOT_RENDERED" if p["voice_speakers"] else "NONE",
                "draft_transcript":spoken if p["voice_speakers"] else "",
            },
            "director_intent":{"camera":cam,"screenplay_beat":beat,"emotion":emo,"background_info":location_detail(p,studio),"sound":sound_for(s,p)},
            "status":status,
            "blockers":sorted(set(blockers)),
            "one_line_video_prompt":v,
            "video_prompt_sha256":hashlib.sha256(v.encode("utf8")).hexdigest(),
            "one_line_image_prompt":im,
            "image_prompt_sha256":hashlib.sha256(im.encode("utf8")).hexdigest(),
            "real_output_video":None,
            "media_qc":"NOT_RUN",
            "owner_approval":"PENDING",
        }
        if status.startswith("HOLD"):held.append(s["shot_id"])
        else:pilot.append(s["shot_id"])
        video.append(v);image.append(im);manifest.append(record)
        subtitle.append({"shot_id":s["shot_id"], **record["subtitle_plan"], "estimated_global_start_seconds":(index-1)*10})
        voiceplan.append({"shot_id":s["shot_id"],"voice_runtime_lines":p["voice_runtime_lines"],"one_speaker_rule_satisfied":len(p["voice_speakers"])<=1,"ready_for_owner_cast_review":len(p["voice_speakers"])<=1 and not status.startswith("HOLD"),"actual_lipsync_qc":"NOT_RUN"})
    assert len(seen_id)==270 and len(manifest)==270
    out.mkdir(parents=True,exist_ok=True)
    def save_txt(path,rows):
        path.write_text("\n\n".join(rows)+"\n",encoding="utf8",newline="\n")
        assert len(path.read_text(encoding="utf8").rstrip("\n").split("\n\n"))==len(rows)
    def save_json(path,obj):
        path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8",newline="\n")
    save_txt(out/"EP001_ALL_270_FIRST_FRAME_ONE_LINE.txt",image)
    save_txt(out/"EP001_ALL_270_VIDEO_ONE_LINE.txt",video)
    save_json(out/"EP001_QC_MANIFEST.json",manifest)
    save_json(out/"EP001_INTERNAL_HAOHAO_VOICE_PLANS.json",voiceplan)
    save_json(out/"EP001_POST_AUDIO_SUBTITLE_PLANS.json",subtitle)
    lanes=[{"lane":i+1,"account_alias":f"Tài khoản {i+1}","max_parallel_streams":1,"review_queue":[],"status":"PLAN_ONLY_NOT_SUBMITTED"} for i in range(4)]
    # Distribute only candidate-review shots; explicit account entitlement checks
    # and human-approved source gates remain prerequisites for any real enqueue.
    for i,sid in enumerate(pilot):
        lanes[i%4]["review_queue"].append(sid)
    for lane in lanes:
        lane_rows=[manifest[int(sid[1:])-1] for sid in lane["review_queue"]]
        lane_id=lane["lane"]
        save_txt(out/f"LANE_{lane_id}_PILOT_REVIEW_ONLY_VIDEO.txt",[r["one_line_video_prompt"] for r in lane_rows])
        save_txt(out/f"LANE_{lane_id}_PILOT_REVIEW_ONLY_FIRST_FRAME.txt",[r["one_line_image_prompt"] for r in lane_rows])
    summary={
        "title":"Bell & Leaf EP001 Muse × HaoHao Director V3 (not approved)",
        "source_screenplay":str(BIND_PATH.relative_to(ROOT)),
        "source_story":str(STORY_PATH.relative_to(ROOT)),
        "original_story_sha256":script_hash(STORY_PATH),
        "original_shot_binding_sha256":script_hash(BIND_PATH),
        "shot_count":270,
        "target_duration_seconds":2700,
        "source_story_production_authorized":False,
        "pilot_review_count":len(pilot),
        "held_count":len(held),
        "held_ids":held,
        "timeline_conflict_count":sum(r["original_source_timeline_conflict"] for r in manifest),
        "multi_speaker_count":sum(len(r["voice_speakers"])>1 for r in manifest),
        "missing_subtitle_plan_count":0,
        "subtitle_plans_requiring_actual_audio_qc":sum(r["subtitle_plan"]["required"] for r in manifest),
        "haohao_accounts_detected":n_accounts,
        "account_proxies_or_secrets_exported":False,
        "lanes":lanes,
        "no_submission_performed":True,
        "production_authorized":False,
        "warning":"Even PILOT REVIEW ONLY rows require independent owner approval of canon frames, voice usage, policy and technical QC before submission; account quota rules must be respected, no proxies or account rotation for limit evasion."
    }
    save_json(out/"EP001_4_ACCOUNT_REVIEW_DISPATCH_PLAN.json",summary)
    lines=[
        "# EP001 — Muse/HaoHao 270 professional prompt drafts",
        "",
        "### Locked facts",
        "- Current source: Canon story V2.2 visual binding, 30 scenes/270 x 10s = 45 minutes DRAFT; not owner-approved.",
        "- Input TXT: exactly one physical prompt per shot, one blank separator, separate video and first-frame files.",
        "- Per-shot actor and exact @location tags, story-specific staging, 10s one take, cinematic camera and A2 exact dialogue.",
        "- Internal HaoHao fixed-voice plan is a separate JSON; plain one-line TXT does not trigger fixed-voice casting by itself.",
        "- English subtitles REQUIRED in final speaking video after actual audio ASR/word alignment; JSON plans are UNTIMED, not finished SRT.",
        "- 4 accounts, one review lane each; no account proxy/password copied; no automatic video generation, no quota bypass.",
        "",
        "### Current gates",
        f"- {len(pilot)} shot candidates for **pilot review only**; {len(held)} HOLD including editorial timeline conflicts.",
        f"- {summary['timeline_conflict_count']} source timeline contradictions (S003-S018 breakfast past vs present) corrected in generated TEXT but still editorial HOLD.",
        f"- {summary['multi_speaker_count']} shots with multiple speakers must be reblocked/split or use validated multi-speaker production.",
        f"- {summary['subtitle_plans_requiring_actual_audio_qc']} spoken slots have mandatory subtitle plans but no final audio timing.",
        "- No real video rendering, Muse account activity, source-image approval, actual voice lip-sync QC or SRT burn-in performed.",
        "",
        "### Safe run order",
        "1. Reconcile screenplay timeline and all holds; owner-approve missing characters, locations and speaking master WAVs.",
        "2. Verify exact reference images/angles and first frames for four different review-candidate shots.",
        "3. Check that each of the 4 independent accounts may concurrently process its own work under provider terms and daily limits.",
        "4. Run one first-frame+video pilot per authorized account (one stream each) and confirm identity, body motion, audio, mouth and subtitles before queuing more.",
        "5. Use bounded retries only for actual technical faults; no account/profile rotation to circumvent safety/quota limits.",
        "6. Render approved SRT from accepted post-conversion audio, check mobile captions, assemble 270 fixed shots then upscale delivery if needed.",
        "",
        "### Offline preflight command",
        "python tools/bell_leaf/muse_haohao_skill_gate.py --video-txt exports/bell_leaf/EP001_MUSE_HAOHAO_DIRECTOR_V3_20261109/EP001_ALL_270_VIDEO_ONE_LINE.txt --image-txt exports/bell_leaf/EP001_MUSE_HAOHAO_DIRECTOR_V3_20261109/EP001_ALL_270_FIRST_FRAME_ONE_LINE.txt --manifest exports/bell_leaf/EP001_MUSE_HAOHAO_DIRECTOR_V3_20261109/EP001_QC_MANIFEST.json",
    ]
    (out/"README_REVIEW_REQUIRED.md").write_text("\n".join(lines)+"\n",encoding="utf8",newline="\n")
    return summary

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUT)
    opts=parser.parse_args()
    res=make(opts.output)
    print(json.dumps({k:v for k,v in res.items() if k not in ("held_ids","lanes")},ensure_ascii=False,indent=2))
    print("LANE_COUNTS",[len(x["review_queue"]) for x in res["lanes"]])
    return 0

if __name__=="__main__":
    raise SystemExit(main())
