"""v263 Nova & Pip full 14-minute original production screenplay and timecoded shot EDL.
Original story architecture: 21 beats / 840 seconds; nine revised pilot shots remain authoritative.
This is a READY_FOR_EDITORIAL_REVIEW script, never an approved/rendered film.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json,csv,datetime as dt
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/"data/verification/v263_maizen_full_story_assets"
CAMERAS=("TRACKING_MEDIUM","INSERT_DETAIL","TWO_SHOT","WIDE_REVEAL")
# each full post-opening beat has 4 sequential on-screen actions and original dialogue.
SCENES={
"B04":([
"Pip tests a rotten edge plank with one foot; wood bends over water.",
"A crack runs across the bridge as Pip's weight shifts forward.",
"Nova grips Pip's sleeve and pulls Pip back onto the same riverbank.",
"Both watch a plank drop downstream; their stone-route alternative is established."],[
"PIP: One quick hop, and we're across.",
"NOVA: Stop! That plank is breaking!",
"PIP: Whoa! I thought it could hold me!",
"NOVA: Fast isn't safe. Show me the stones we packed." ]),
"B05":([
"Nova opens the original pack: three grey blocks. Counter visibly reads THREE.",
"Place original BLOCK_STONE_01 at the first shallows; inventory decreases to TWO.",
"Place BLOCK_STONE_02 beside the bank; remaining counter falls to ONE.",
"Place BLOCK_STONE_03 as final safe step. Both cross; counter now ZERO."],[
"NOVA: Three blocks. No extras. Make each one count.",
"PIP: One stone... and one careful step.",
"NOVA: The next one has to reach that ledge.",
"PIP: All three used. Look—we made a crossing!" ]),
"B06":([
"At the waterfall apron Pip unfolds the wet three-dot sketch, never dropping it.",
"Three dots line up with three boulders in a precisely staged point-of-view.",
"Nova sights along the stones as amber light flashes through a gap in the water.",
"Both move toward the concealed gap, sketch still held by Pip."],[
"PIP: It's the same three dots!",
"NOVA: Line the first mark up with that stone.",
"PIP: Behind the waterfall. That's our path.",
"NOVA: Stay close and keep the paper dry." ]),
"B07":([
"Wide shot holds the physical waterfall threshold and entry geometry.",
"Nova crosses falling water visibly, Pip follows with the sketch.",
"Wet footprints lead into cave; loose gravel falls in the dark ahead.",
"Both stop under a dry lip and investigate a distant cave knock."],[
"NOVA: I'm going first. Watch where I step.",
"PIP: I'm soaked. My map is still here!",
"PIP: Did you hear those stones moving?",
"NOVA: Someone—or something—was here before us." ]),
"B08":([
"Cave splits into bright tile corridor and shadowy ridge; mark true geography.",
"Pip reaches toward bright doorway; floor-level insert reveals pressure plate.",
"Nova tests safety with a small loose pebble without entering or triggering plate.",
"Pip chooses the dark ledge. Both avoid the plate, preserving its untriggered state."],[
"PIP: Bright tunnel. That must be the easy one.",
"NOVA: Look down before you choose.",
"PIP: That square plate could be a trap!",
"NOVA: The quiet route is our route." ]),
"B09":([
"Pip opens sketch in a safe alcove to compare three carved marks.",
"Two marks are on stone, the third hidden behind an original moss patch.",
"Nova touches the distinct coded cave door switches in 1-2-3 order.",
"DOOR_CAVE_CODED opens inward; both see an abandoned workshop beyond."],[
"PIP: Three marks again. It can't be chance.",
"NOVA: There's the last one, under the moss.",
"NOVA: First... second... third.",
"PIP: A workshop! The map was a key." ]),
"B10":([
"Show workshop and the pre-existing opened coded door as one fixed set.",
"Nova lays a distinct wooden pivot and original false-wall panel on the outside.",
"Pip tests DOOR_WORKSHOP_FALSEWALL from both sides as visible hinges move.",
"False-wall looks like rock when shut, but mechanism remains visible to camera."],[
"NOVA: We need a hidden way in—not just that old lock.",
"PIP: Then make this wall open like a door.",
"NOVA: Try it from this side. Now from outside.",
"PIP: It looks like stone. I love it!" ]),
"B11":([
"Nova places original blue crystal in a grounded socket with physical wire.",
"Indicator and bell activate; close shot follows wire to a maintenance panel.",
"A small illustrated safety chart clearly shows BLUE–AMBER–BLUE reset sequence.",
"Pip tests safe test-light button, not flood valve; map stays in Pip's hand."],[
"NOVA: The crystal powers the warning light.",
"PIP: That wire runs all the way to the bell.",
"NOVA: Blue, amber, blue. That's the safety reset.",
"PIP: I'll remember. No touching that big valve." ]),
"B12":([
"Nova points out a second natural tunnel rising above the river flood level.",
"Pip fastens original retrieval HOOK_TOOL to a belt socket on camera.",
"Together they clear exit; show water grate connection drawn on workshop plan.",
"Nova sets map on distinct worktable in view; mark upper hatch chalk symbol."],[
"NOVA: If the main room floods, we escape up there.",
"PIP: And this hook? I'll keep it on my belt.",
"NOVA: That drain runs under the floor to the upper grate.",
"PIP: Exit marked, map on the table. Ready to test." ]),
"B13":([
"Pip accidentally bumps the clearly unlabelled mechanical VALVE_MAIN.",
"Water rises from workshop floor, not instant full-room volume.",
"Map slides off worktable into WORKSHOP_FLOOR_DRAIN visibly in water.",
"Water transports map toward relief channel, characters watch it vanish."],[
"PIP: Wait—this handle wasn't supposed to move!",
"NOVA: Back up. The water's coming through the floor!",
"PIP: My map! It's going into the drain!",
"NOVA: We know the drain route. Get to the upper exit!" ]),
"B14":([
"Nova pulls Pip toward the previously built emergency tunnel.",
"Cut on same-side action: water follows steps at a physically consistent rate.",
"Pip looks back for map but it is still moving through the hidden drain.",
"Both emerge at upper river hatch, wet, breathing hard; no teleport or map."],[
"NOVA: Feet on the dry stairs. Keep moving!",
"PIP: The map is gone. I can still hear the water!",
"NOVA: Leave it for now. We can track the drain.",
"PIP: I'm up. Close the hatch!" ]),
"B15":([
"Nova seals a heavy but grounded upper hatch with latch visibly engaging.",
"Water follows relief channel, decreasing gradually; pressure gauge falls.",
"The channel flows past known upper grate and net, establishing possible map catch.",
"Pip confirms no map in either hand; characters decide to search safely."],[
"NOVA: Hatch locked. The channel takes the pressure.",
"PIP: The water is finally slowing down.",
"NOVA: Everything from that drain ends at the catch grate.",
"PIP: Then our map could still be there!" ]),
"B16":([
"Exterior relief shaft path shown from hatch along upper bank, no jump cut teleport.",
"Nova spots original three-dot marks on stones next to channel.",
"Pip follows three marks downstream while keeping belt hook attached.",
"Both reach relief grate; the map's corner is visible under a stationary rail."],[
"NOVA: Follow that stone shelf. Stay above the water.",
"PIP: Three dots—right here again!",
"NOVA: Same code. The catch net must be close.",
"PIP: I can see the paper under that grate!" ]),
"B17":([
"Pip crouches at reachable maintenance rail, without stepping into fast current.",
"Pip unclips the HOOK_TOOL from belt (previously introduced B12).",
"Hook catches wet paper at fixed grate, pulls it up in one continuous movement.",
"Pip shakes water off sketch, clips hook back to belt; ownership restored."],[
"PIP: If I lean in, I can reach it.",
"NOVA: Use your hook. Keep your feet on the stone!",
"PIP: Got it! The three dots are still there.",
"NOVA: Keep it above the water this time." ]),
"B18":([
"At relief maintenance console, Nova compares map symbols and safety chart.",
"Show that three dots are entrance clue; colored reset is separate mechanism.",
"Nova physically inputs BLUE–AMBER–BLUE at reachable safety panel.",
"Valve closes, drain lowers water, bell stops and workshop becomes safe to inspect."],[
"PIP: Was the map a warning the whole time?",
"NOVA: The dots led to the door. The colors reset the valve.",
"NOVA: Blue. Amber. Blue. Watch the pressure!",
"PIP: The bell stopped! We fixed the flood." ]),
"B19":([
"Characters follow previously revealed dry return route to workshop door.",
"Nova checks the coded entrance and falsewall as two separate moving props.",
"Pip places recovered map on the marked shelf and locks the original hook belt.",
"Blue socket and dry floor verified; DOOR_CAVE_CODED and safety valve in safe state."],[
"NOVA: Test the first lock before we trust the room.",
"PIP: And the hidden wall still opens from both sides.",
"NOVA: Paper on the shelf. Crystal secured. Valve closed.",
"PIP: Next time we test everything twice." ]),
"B20":([
"An original amber pulse emerges between workshop floor seams, not crystal reset lamp.",
"Camera follows pulse down toward LOWER_TUNNEL_CLOSED under workbench.",
"Pip kneels but does not open the lower tunnel; map stays on shelf.",
"Nova marks the new puzzle for tomorrow; warning bell remains off."],[
"PIP: Hey! That's not our blue warning light.",
"NOVA: No. It came from under the floor.",
"PIP: Do we open it now?",
"NOVA: Not without a map and a safer plan." ]),
"B21":([
"Outside waterfall at sunset, physical camera path leaves dry workshop behind.",
"Nova inventories original tools; Pip has hook but no map in hand.",
"They look back at safe river crossing; cave stays sealed, no magical rebuild.",
"Final wide: faint amber pulse under waterfall, original Nova & Pip series mark only."],[
"PIP: The light was a signal all along.",
"NOVA: We solved one mystery, not the next.",
"PIP: Tomorrow, with better supplies?",
"NOVA: With a better plan. And each other." ]),
}
BEAT_ASSETS={
"B04":["BROKEN_BRIDGE","STONE_01","STONE_02","STONE_03","THREE_DOT_SKETCH"],
"B05":["STONE_01","STONE_02","STONE_03","RIVER_ROCK_SHELF","THREE_DOT_SKETCH"],
"B06":["WATERFALL","THREE_DOT_MARKER","THREE_DOT_SKETCH"],
"B07":["WATERFALL","RIVER_ROCK_SHELF","THREE_DOT_SKETCH"],
"B08":["THREE_DOT_SKETCH","THREE_DOT_MARKER"],
"B09":["DOOR_CAVE_CODED","THREE_DOT_MARKER","THREE_DOT_SKETCH"],
"B10":["DOOR_CAVE_CODED","DOOR_WORKSHOP_FALSEWALL"],
"B11":["CRYSTAL_BLUE_SOCKET","RESET_PANEL","WARNING_BELL","THREE_DOT_SKETCH"],
"B12":["UPPER_HATCH","RELIEF_CHANNEL","WORKSHOP_FLOOR_DRAIN","WORKTABLE","HOOK_TOOL","THREE_DOT_SKETCH"],
"B13":["VALVE_MAIN","WORKSHOP_FLOOR_DRAIN","RELIEF_CHANNEL","WORKTABLE","THREE_DOT_SKETCH"],
"B14":["UPPER_HATCH","RELIEF_CHANNEL"],
"B15":["UPPER_HATCH","CATCH_GRATE","RELIEF_CHANNEL"],
"B16":["THREE_DOT_MARKER","RELIEF_CHANNEL","CATCH_GRATE","HOOK_TOOL"],
"B17":["HOOK_TOOL","CATCH_GRATE","THREE_DOT_SKETCH"],
"B18":["RESET_PANEL","VALVE_MAIN","RELIEF_CHANNEL","THREE_DOT_SKETCH"],
"B19":["DOOR_CAVE_CODED","DOOR_WORKSHOP_FALSEWALL","SKETCH_SHELF","CRYSTAL_BLUE_SOCKET","THREE_DOT_SKETCH"],
"B20":["LOWER_TUNNEL_CLOSED","AMBER_PULSE","SKETCH_SHELF"],
"B21":["WATERFALL","AMBER_PULSE","RIVER_ROCK_SHELF","STONE_01","STONE_02","STONE_03"],
}
def make_story(root:Path=ROOT,write:bool=False)->dict:
 src=root/"data/verification/v243_maizen_original_preproduction/original_story_and_21_beats.json"
 v262=root/"data/verification/v262_maizen_story_alignment/corrected_pilot_and_continuity.json"
 old=json.loads(src.read_text(encoding="utf-8"))
 aligned=json.loads(v262.read_text(encoding="utf-8"))
 if sha256(src.read_bytes()).hexdigest()!=aligned["source_original_14m_beats_sha256"]:
  raise ValueError("SOURCE_BEAT_TIMELINE_DRIFT")
 beats=old["beats"]
 if len(beats)!=21 or beats[-1]["end"]!=840 or len(SCENES)!=18:
  raise ValueError("NOT_21_BEAT_840_SECOND_ORIGINAL")
 if sorted(SCENES)!=[f"B{i:02d}" for i in range(4,22)]:
  raise ValueError("ALL_LATER_BEATS_MUST_HAVE_DIALOGUE_AND_ACTION")
 allshots=[]
 # 9-shot original revised pilot, exact 45s retained
 for sh in aligned["corrected_45s_original_pilot"]["shots"]:
  allshots.append({"id":sh["shot_id"],"beat":sh["source_beat"],
   "start":sh["start"],"end":sh["end"],"camera":sh["camera_intent"],
   "action":sh["blocking"],"voice":sh["draft_english_voice"],"set":sh["set_id"],
   "asset_refs":sh["character_and_prop_ids"],"sound_events":sh["sound_event_plan"],
   "state_after":sh["end_state"],"source":"V262_CORRECTED_ORIGINAL_PILOT",
   "needs_live_performance":True})
 # B03 continues another 5s after cliffhanger; opening remains unresolved
 allshots.append({"id":"S010","beat":"B03","start":45,"end":50,
  "camera":"CONTINUITY_TWO_SHOT","action":"Pip checks the rotten bridge from safe side; Nova points uphill. Neither crosses.",
  "voice":"PIP: Ridge first. You were right.","set":"WATERFALL_FORK",
  "asset_refs":["NOVA","PIP","BROKEN_BRIDGE","THREE_DOT_SKETCH"],
  "sound_events":["bridge-creak","river-current"],"state_after":"RIDGE_ROUTE_CHOSEN",
  "source":"ORIGINAL_EPISODE_CONTINUITY_EXTENDER","needs_live_performance":True})
 for beat in beats[3:]:
  bid=beat["id"]
  actions,lines=SCENES[bid]
  if len(actions)!=4 or len(lines)!=4:raise ValueError("FOUR_ACTIONS_AND_LINES_REQUIRED:"+bid)
  duration=beat["end"]-beat["start"]
  # 4 partitions exact timestamps; no gap or overlap
  ends=[beat["start"]+round(duration*j/4) for j in range(5)]
  for i in range(4):
   voice=lines[i]
   if not voice.startswith(("NOVA:","PIP:")):raise ValueError("VO_SPEAKER_UNDEFINED")
   allshots.append({
    "id":f"S{len(allshots)+1:03d}","beat":bid,"start":ends[i],"end":ends[i+1],
    "camera":(beat.get("camera") or CAMERAS[i]) if i==0 else CAMERAS[(i+int(bid[1:]))%4],
    "action":actions[i],"voice":voice,"set":beat["location"],
    "asset_refs":["NOVA","PIP"]+BEAT_ASSETS[bid],
    "sound_events":[beat.get("audio","original location ambience"),"original foley timed to action"],
    "state_after":beat["continuity"],
    "source":"ORIGINAL_REVISED_14M_SCRIPT","needs_live_performance":True})
 if allshots[0]["start"]!=0 or allshots[-1]["end"]!=840 or len(allshots)!=82:
  raise ValueError("NARRATIVE_TIMELINE_NOT_EXACT_840S_82SHOTS")
 for i,s in enumerate(allshots):
  if s["end"]<=s["start"] or (i and allshots[i-1]["end"]!=s["start"]):
   raise ValueError("SCREENPLAY_TIME_GAP_OR_OVERLAP")
  if "Mikey" in s["action"] or "JJ" in s["action"]:raise ValueError("COMPETITOR_IP_IN_ORIGINAL")
 # Key preplant/payoff hard-coded checks, not literary certification
 joined=" ".join(x["action"] for x in allshots)
 for term in ("three grey blocks","HOOK_TOOL","BLUE–AMBER–BLUE",
              "WORKSHOP_FLOOR_DRAIN","DOOR_CAVE_CODED","DOOR_WORKSHOP_FALSEWALL"):
  if term not in joined:raise ValueError("REQUIRED_CAUSAL_SETUP_MISSING:"+term)
 result={"schema":"cine.nova_pip.original_full_screenplay.v263","title":"Nova & Pip: The Secret Below the Waterfall",
    "project_id":"MAI01_WATERFALL","language":"English",
    "format":"ORIGINAL_VOXEL_ADVENTURE_TWO_POTENTIAL_BACKENDS",
    "original_ip_only":True,"main_characters":["NOVA","PIP"],
    "runtime_seconds":840,"story_beats":21,"shooting_script_shots":len(allshots),
    "opening_shots_from_corrected_v262":9,
    "storyboard_opening_seconds":45,
    "source_script_status":"EDIT_COMPLETE_FIRST_PRODUCTION_DRAFT_NOT_FINAL_SIGNOFF",
    "G02":"BLOCKED_NATIVE_AV_SEMANTIC_INDEPENDENT_REVIEW",
    "rendered_media_exists":False,"approved_for_commercial_release":False,
    "legal_assets_cleared":False,
    "rehearsal_note":"Dialogue paced against original visual beats; record scratch VO and retime during rehearsal before shot-lock.",
    "character_state_bible":{
      "NOVA":"Careful problem solver, teal jacket, short dark hair, always holds three original stone blocks before B05.",
      "PIP":"Curious eager partner, coral scarf, retrieval hook on belt from B12, sketch carried B02-B12 and B17-B19.",
      "THREE_DOT_SKETCH":"Seen unowned B01; Pip gets B02; set on worktable B12; lost B13; hooked B17; shelved B19.",
      "THREE_STONES":"Introduced as three owned blocks B03/B04; only B05 placement spends one per step until zero.",
      "DRAIN_PATH":"Workshop floor drain to upper relief grate, established B12; map physically follows B13-B17.",
      "DOORS":"Original coded cave door B09 and different concealed falsewall workshop entrance B10.",
      "VALVE":"Original blue crystal B11 with blue–amber–blue safety-chart reset, B13 flooded accidentally, B18 shut from relief shaft.",
      "LOWER_TUNNEL":"Sealed through final frame; mystery pulse unrelated to reset lamp."},
    "shots":allshots}
 if write:
  out=root/"data/verification/v263_maizen_full_story_assets"
  out.mkdir(parents=True,exist_ok=True)
  path=out/"nova_pip_14min_shooting_script.json"
  path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  lines=[f"# {result['title']}","", "**Original English screenplay – 840 seconds / 21 beats / 82 timed shots**",
   "","Status: first complete timecoded shooting draft; final directing/VO rehearsal, license and independent G02 approvals pending.",
   "","**Do not render or publish as approved source-adapted content.**",""]
  prev=""
  for s in allshots:
   if s["beat"]!=prev:
    prev=s["beat"]
    b=next((x for x in beats if x["id"]==prev),None)
    heading=b["title"] if b else "Pilot B03 intercut"
    lines.extend(["",f"## {prev} — {heading}",""])
   a,c=s["start"],s["end"]
   lines.append(f"**{s['id']} [{a//60:02d}:{a%60:02d}–{c//60:02d}:{c%60:02d}] {s['camera']} | {s['set']}**")
   lines.append(s["action"])
   if s.get("voice"):lines.append(f"*{s['voice']}*")
   lines.append(f"Sound: {', '.join(s['sound_events'])}. Continuity: {s['state_after']}.")
   lines.append("")
  (out/"nova_pip_14min_screenplay.md").write_text("\n".join(lines),encoding="utf-8")
  with (out/"nova_pip_shot_edl.csv").open("w",newline="",encoding="utf-8-sig") as fp:
   writer=csv.DictWriter(fp,fieldnames=["id","beat","start","end","camera","set","action","voice","state_after"])
   writer.writeheader()
   for s in allshots:writer.writerow({k:s.get(k) for k in writer.fieldnames})
  result["output_path"]=str(path)
 return result
if __name__=="__main__":
 r=make_story(write=True)
 print(json.dumps({"status":r["source_script_status"],"seconds":r["runtime_seconds"],
  "shots":r["shooting_script_shots"],"G02":r["G02"],"file":r["output_path"]},ensure_ascii=False))
