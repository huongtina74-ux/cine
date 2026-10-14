"""CineFactory v262: original pilot and 14m story continuity reconciliation.
DESK WORK ONLY: never makes, renders, publishes or certifies video.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/"data/verification/v243_maizen_original_preproduction"
DEST=ROOT/"data/verification/v262_maizen_story_alignment"
OVERLAY_SCHEMA="cine.maizen.original_story_alignment.v262"
# 45-second trailer/pilot follows B01 [0,15), B02 [15,32), B03 [32,50).
# Last five seconds of B03 are for episode continuation, NOT in 45s pilot.
SHOTS=[
 ("P01",0,5, "B01","FOREST_OVERLOOK","WIDE", "Amber pulse behind the waterfall. Nova and Pip face the falling water.",
  "Nova: Did you see that flash?",["WATERFALL","AMBER_PULSE"],"SKETCH_NOT_COLLECTED","distant-waterfall,one-amber-chime"),
 ("P02",5,10,"B01","FOREST_OVERLOOK","TWO_SHOT_REACTION","Pip leans forward; Nova stops Pip before a rash leap.",
  "Pip: Three flashes! Something's there.",["NOVA","PIP"],"SKETCH_NOT_COLLECTED","cloth-step,two-character-voice"),
 ("P03",10,15,"B01","RIVER_ROCK_SHELF","INSERT_RACK_FOCUS",
  "Camera reveals a wet three-dot sketch stuck in reeds on the near bank; nobody grabs it yet.",
  None,["THREE_DOT_SKETCH"],"SKETCH_VISIBLE_UNOWNED","water-droplets,paper-flap"),
 ("P04",15,20,"B02","RIVER_ROCK_SHELF","LOW_MEDIUM",
  "Pip safely steps onto the near-bank rock, retrieves the sketch with one hand, and stays on the same river side.",
  "Pip: Wait. A drawing!",["PIP","THREE_DOT_SKETCH"],"SKETCH_WITH_PIP","footstep-wet,paper-pickup"),
 ("P05",20,25,"B02","RIVER_ROCK_SHELF","OVER_SHOULDER_INSERT",
  "Three dots on the wet sketch are clearly visible, with no invented vault/hidden chest labels.",
  "Pip: Three dots. A clue?",["THREE_DOT_SKETCH"],"SKETCH_WITH_PIP","subtle-paper-motion"),
 ("P06",25,30,"B02","RIVER_ROCK_SHELF","CLOSE_FACE_REACTION",
  "Nova warns Pip not to assume the marks are safe; Pip keeps holding the sketch.",
  "Nova: Or three warnings.",["NOVA","PIP","THREE_DOT_SKETCH"],"SKETCH_WITH_PIP","breath-waterfall,voice"),
 ("P07",30,35,"B02_B03_BOUNDARY_AT_32","RIVER_SHELF_TO_FORK","FOLLOW_TRACK",
  "Follow both characters, sketch visible in Pip's hand; at 32s cut to a broken bridge ahead.",
  None,["NOVA","PIP","BROKEN_BRIDGE","THREE_DOT_SKETCH"],"SKETCH_WITH_PIP_BRIDGE_SEEN","footsteps,wood-creak"),
 ("P08",35,40,"B03","WATERFALL_FORK","WIDE_INSERT",
  "Show rotten missing bridge planks across river; nobody crosses or touches the bridge until B04 at 50s.",
  "Pip: That bridge looks fast.",["BROKEN_BRIDGE","NOVA","PIP"],"SKETCH_WITH_PIP_BRIDGE_UNCROSSED","loose-wood-creak"),
 ("P09",40,45,"B03","WATERFALL_FORK","TWO_SHOT_TO_RIDGE",
  "Nova points toward safe stones along the riverbank; the unresolved choice creates the 45s cliffhanger.",
  "Nova: Fast isn't always safe.",["RIVER_RIDGE","NOVA","PIP","THREE_DOT_SKETCH"],
  "SKETCH_WITH_PIP_CHOICE_PENDING","river-rise,short-transition-sting"),
]
AMENDMENTS=[
 {"beat_id":"B05","risk":"INVENTORY_RESOURCE_CREATION","required_revision":
  "Establish three original grey construction blocks in Nova's starting pack during B03/B04; deduct exactly one at each B05 placement, with no magically appearing material."},
 {"beat_id":"B09_B10","risk":"TWO_DOORS_AMBIGUOUS","required_revision":
  "B09 unlocks pre-existing cavern-to-workshop security door via three dot key. B10 conceals a DISTINCT new false-wall outer entrance; assign unique prop IDs DOOR_CAVE_CODED and DOOR_WORKSHOP_FALSEWALL."},
 {"beat_id":"B11","risk":"COLOR_CODE_NOT_SEEDED","required_revision":
  "Expose the blue-amber-blue warning lamp sequence as a 3-step safe-reset chart beside the real crystal socket. Color cues are original and different from dot entrance-order symbols."},
 {"beat_id":"B12","risk":"UNINTRODUCED_HOOK_AND_WATER_PATH","required_revision":
  "Hang an original hook tool on Pip's belt before B12. Show schematic relief drain connecting workshop floor grate to upper channel/catch net. Map remains on table until B13."},
 {"beat_id":"B13_B15","risk":"MAP_CANNOT_REACH_RELIEF_GRATE_UNEXPLAINED","required_revision":
  "As water sweeps map off table, SHOW map enter workshop FLOOR DRAIN, then upper relief channel carries it to visible catch grate before hatch seal; hatch redirects flow but doesn't teleport map."},
 {"beat_id":"B16_B17","risk":"UNPLOTTED_RETURN_OR_TOOL","required_revision":
  "Show safe route from upper river hatch to relief grate; Pip retrieves stored belt hook and reclaims map without crossing water or appearing in flooded workshop."},
 {"beat_id":"B18_B19","risk":"VALVE_RESET_LOCATION_AND_REENTRY","required_revision":
  "Ensure blue-amber-blue control is reachable from relief shaft maintenance panel, and show inspection of workshop by reopening previously established safe-door route only after draining."},
 {"beat_id":"B20_B21","risk":"END_SCENE_WORLD_AND_ASSET_STATE","required_revision":
  "Map must remain on workshop shelf when Nova/Pip exit at sunset; lower tunnel remains physically closed, warning light not confused with flood-reset lights."},
]
def make_alignment(root:Path=ROOT,write:bool=False)->dict:
    pilot_file=root/"data/verification/v243_maizen_original_preproduction/nine_pilot_shots.json"
    beat_file=root/"data/verification/v243_maizen_original_preproduction/original_story_and_21_beats.json"
    pilot=json.loads(pilot_file.read_text(encoding="utf-8"))
    story=json.loads(beat_file.read_text(encoding="utf-8"))
    if pilot.get("project_id")!="MAI01_WATERFALL" or story.get("project_id")!="MAI01_WATERFALL":
        raise ValueError("PROJECT_ORIGINAL_PROVENANCE")
    beats=story["beats"]
    if len(beats)!=21 or beats[0]["start"]!=0 or beats[0]["end"]!=15 or beats[1]["start"]!=15 or beats[1]["end"]!=32 or beats[2]["start"]!=32 or beats[2]["end"]!=50:
        raise ValueError("SOURCE_BEAT_TIMELINE_DRIFT")
    if pilot["pilot_seconds"]!=45 or len(pilot["shots"])!=9:
        raise ValueError("LEGACY_PILOT_NOT_AS_EXPECTED")
    entries=[]
    for i, (sid,start,end,beat_id,scene,coverage,action,voice,props,state,audio) in enumerate(SHOTS):
        if end-start!=5 or start!=i*5:
            raise ValueError("PILOT_SHOT_SEAMS")
        if not action or not audio or not state or any(x in action.lower() for x in ("jj","mikey","spider-man")):
            raise ValueError("NOT_ORIGINAL_COHERENT_SHOT")
        if voice is not None and len(voice.split())>12:raise ValueError("FIVE_SECOND_VOICE_OVERLOADED")
        entries.append({"shot_id":sid,"start":start,"end":end,"source_beat":beat_id,
            "set_id":scene,"camera_intent":coverage,"blocking":action,
            "draft_english_voice":voice,"character_and_prop_ids":props,
            "end_state":state,"sound_event_plan":audio.split(","),
            "rights_source":"ORIGINAL_ONLY_ASSET_PROVENANCE_PENDING",
            "scene_rendered":False,"real_voice_recorded":False,
            "production_gate":"HOLD_G02_G13_RIGHTS_AND_OWNER"})
    if entries[2]["end_state"]!="SKETCH_VISIBLE_UNOWNED" or entries[3]["end_state"]!="SKETCH_WITH_PIP":
        raise ValueError("SKETCH_PROP_OWNERSHIP")
    if any("CAVE" in x["set_id"] for x in entries):
        raise ValueError("PILOT_TELEPORTS_INTO_LATER_ACT")
    if len({a["beat_id"] for a in AMENDMENTS})!=len(AMENDMENTS):
        raise ValueError("DUPLICATE_AMENDMENT")
    result={"schema":OVERLAY_SCHEMA,"project_id":"MAI01_WATERFALL",
        "source_original_14m_beats_sha256":sha256(beat_file.read_bytes()).hexdigest(),
        "legacy_9shots_sha256":sha256(pilot_file.read_bytes()).hexdigest(),
        "original_scene_plan_preserved_unchanged":True,
        "finding":"LEGACY_45S_PILOT_CONTRADICTS_B01_B03_AND_TELEPORTS_TO_CAVE",
        "gates":{"G02":"PENDING_INDEPENDENT_SOURCE_AV",
                 "G05_G15":"DRAFT_REVISION_ONLY",
                 "G16_G28":"HOLD_NO_RENDER_OR_UPLOAD"},
        "corrected_45s_original_pilot":{"duration_sec":45,"shot_count":9,
            "first_45s_of_14m_beat_coverage":["B01","B02","B03_PARTIAL"],
            "video_exists":False,"shots":entries},
        "episode_story_continuity_amendments":AMENDMENTS,
        "script_14m_fully_written_and_approved":False,
        "pilot_vo_fully_recorded":False,
        "stage":"DESK_CREATIVE_REVISION_FOR_REVIEW_NOT_SCRIPT_LOCK"}
    if write:
        out=root/"data/verification/v262_maizen_story_alignment"
        out.mkdir(parents=True,exist_ok=True)
        target=out/"corrected_pilot_and_continuity.json"
        target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        result["output"]=str(target)
    return result

if __name__=="__main__":
    r=make_alignment(write=True)
    print(json.dumps({"status":r["stage"],"shots":r["corrected_45s_original_pilot"]["shot_count"],
      "amendments":len(r["episode_story_continuity_amendments"]),
      "corrects":r["finding"],"output":r["output"]},ensure_ascii=False))
