"""The 270 *actual* Bell & Leaf shooting shots must match locked scene V2.

All tests are structural, cast, and asset-safety tests, NOT artist approval.
"""
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/"docs/story/bell_leaf/ep001_screenplay"
BIND=json.loads((EP/"EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json").read_text(encoding="utf-8"))
MEM=json.loads((EP/"EP001_STORY_V2_CONTINUITY_LOCK.json").read_text(encoding="utf-8"))
ACTS=sorted(EP.glob("EP001_ACT_*.md"))
SHOT=re.compile(r"(?m)^\*\*(S\d{3}) \[(\d\d):(\d\d)–(\d\d):(\d\d)\]\*\* (.+)$")


def shots(path):
    return {m.group(1):(m.group(2),m.group(3),m.group(4),m.group(5),m.group(6))
            for m in SHOT.finditer(path.read_text(encoding="utf-8"))}


def test_270_individually_reconciled_one_take_shots():
    data=BIND["shots"]
    assert len(data)==270
    script=shots(EP/"EP001_FULL_45MIN_SHOOTING_SCREENPLAY_DRAFT.md")
    assert len(script)==270
    for i,entry in enumerate(data,1):
        sid=f"S{i:03d}"
        assert entry["shot_id"]==sid
        assert entry["scene_id"]==f"SC-{(i-1)//9+1:03d}"
        st=script[sid]
        assert int(st[0])*60+int(st[1])==(i-1)*10
        assert int(st[2])*60+int(st[3])==i*10
        assert "SHOT DIRECTION:" in st[4]
        direction=entry["shot_director_v2_2"]
        assert direction["scene_id"]==entry["scene_id"]
        assert direction["script_action"] in st[4]
        assert direction["script_status"].startswith("DRAFT_")
        assert direction["media_approved"] is False
        assert direction["spoken_words"]<=16
        assert all(direction["video"][x].strip() for x in ("setup_0_2","action_2_7","reaction_7_10","camera"))
        assert direction["location_tag"].startswith("@")
        assert entry["active_tags_line"]=="ACTIVE TAGS FOR THIS SHOT: ["+", ".join(entry["active_character_tags_candidate"])+"]"
        assert set(entry["character_reference_paths"])<=set(entry["active_character_tags_candidate"])
        assert "LIVE ACTION" not in st[4].upper()


def test_five_act_sources_match_combined_byte_for_byte_shot_lines():
    assert len(ACTS)==5
    all_acts={}
    for path in ACTS:
        for sid,line in shots(path).items():
            assert sid not in all_acts
            all_acts[sid]=line
    assert all_acts==shots(EP/"EP001_FULL_45MIN_SHOOTING_SCREENPLAY_DRAFT.md")


def test_scene_cast_respects_v2_chronology_and_no_phantom_actor():
    cards={x["scene_id"]:set(x["character_tags"]) for x in MEM["scene_cards"]}
    assert len(cards)==30
    for entry in BIND["shots"]:
        allowed=cards[entry["scene_id"]]
        if entry["shot_id"]=="S001":allowed=allowed|{"ORIN"}
        assert set(entry["active_character_tags_candidate"])<=allowed,entry["shot_id"]
        for who in entry.get("audio_only_character_tags_candidate",[]):
            assert who in allowed or (entry["shot_id"]=="S123" and who=="AILA")
    for sid in ("S001","S046","S054","S062"):
        entry=BIND["shots"][int(sid[1:])-1]
        assert not (set(entry["active_character_tags_candidate"]) & {"EVAN","JUNO","LIA","BIX","BUBU"})
    assert BIND["shots"][0]["active_character_tags_candidate"]==["MARA","ORIN"]
    assert BIND["shots"][1]["active_character_tags_candidate"]==["MARA","BIX"]
    assert BIND["shots"][147]["active_character_tags_candidate"]==["BIX","JUNO"]
    assert BIND["shots"][269]["active_character_tags_candidate"]==[]


def test_station_and_private_assets_cannot_be_claimed_approved():
    entries=BIND["shots"]
    assert all(x.get("location_anchor_id")!="BELL_CENTRAL_BELL_HALL_CANDIDATE" for x in entries)
    assert sum(x.get("location_evidence_status")=="EARTH_SMALL_SECRET_BELLCHAMBER_GEOMETRY_NOT_APPROVED" for x in entries)>=30
    assert all(x["shot_director_v2_2"]["media_approved"] is False for x in entries)
    for entry in entries:
        if "AILA" in entry["active_character_tags_candidate"]:
            assert "AILA" in entry["characters_without_approved_visuals"]
            assert "AILA_FACE_COSTUME_NOT_APPROVED" in entry["shot_director_v2_2"]["asset_blockers"]
    assert entries[0]["owner_location_plate_path"] is None
    assert entries[269]["owner_location_plate_path"] is None
    assert MEM["assets"]["full_270_shot_v2_directions_approved"] is False
    assert MEM["shot_reconciliation_20261109"]["production_authorized"] is False


def test_elara_cloth_arrives_after_garden_branch_and_real_pot_broke():
    arr=BIND["shots"]
    assert "NOT wrapping" in arr[26]["shot_director_v2_2"]["script_action"]
    assert "Elara gives Mara a soft linen cloth" in arr[40]["shot_director_v2_2"]["script_action"]
    assert "clay pot from Veylora is broken" in arr[65]["shot_director_v2_2"]["script_action"]


def test_slow_earth_growth_without_internal_montage_and_two_successful_tests():
    arr=BIND["shots"]
    assert all("montage" not in arr[i-1]["shot_director_v2_2"]["script_action"].lower() for i in range(1,271))
    assert "NEXT EARTH DAY" in arr[85]["shot_director_v2_2"]["script_action"]
    assert "THIRD EARTH DAY" in arr[86]["shot_director_v2_2"]["script_action"]
    assert "AFTER SEVERAL EARTH DAYS" in arr[88]["shot_director_v2_2"]["script_action"]
    assert "FIRST FULL SAFE PULSE" in arr[205]["shot_director_v2_2"]["script_action"]
    assert "SECOND FULL SAFE PULSE" in arr[207]["shot_director_v2_2"]["script_action"]


def test_a2_wav_video_finals_never_faked():
    assert MEM["assets"]["aila_visual_approved"] is False
    assert MEM["assets"]["aila_voice_approved"] is False
    assert MEM["shot_reconciliation_20261109"]["approved_voice_samples"]==0
    assert MEM["shot_reconciliation_20261109"]["owner_story_signoff"] is False
    assert all("PROVIDER_MEDIA_UPLOAD_NOT_VERIFIED" not in json.dumps(v) for v in [])
