"""HaoHao Bell & Leaf v2.2: 270 one-line prompt/asset/voice safety checks."""
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"exports/bell_leaf/EP001_HAOHAO_10S_V22_20261109"
BIND=ROOT/"docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json"
VALID={"neutral","happy","sad","angry","fearful","surprised","disgusted"}


def read_prompts(name):
    s=(OUT/name).read_text(encoding="utf8")
    assert s.endswith("\n") and not s.endswith("\n\n")
    chunks=s.rstrip("\n").split("\n\n")
    assert len(chunks)==270 if "PILOT" not in name else len(chunks)==5
    assert all("\n" not in x for x in chunks)
    return chunks


def test_one_single_line_per_shot_and_exact_one_empty_separator():
    vids=read_prompts("EP001_ALL_270_VIDEO_ONE_LINE.txt")
    imgs=read_prompts("EP001_ALL_270_FIRST_FRAME_ONE_LINE.txt")
    for i,(v,im) in enumerate(zip(vids,imgs),1):
        sid=f"S{i:03d}"
        assert v.startswith(f"EP001 {sid} [")
        assert im.startswith(f"EP001 {sid} [FIRST FRAME]")
        assert "10.0 seconds" in v
        assert "24fps" in v and "16:9" in v
        assert "ACTIVE TAGS FOR THIS SHOT: [" in v and "ACTIVE TAGS FOR THIS SHOT: [" in im
        assert "4K" in v and "actual native pixels must be checked by ffprobe" in v
        assert "3x3 grid" in v


def test_correct_cast_for_first_shots_and_no_unapproved_village():
    d=json.loads((OUT/"EP001_QC_MANIFEST.json").read_text(encoding="utf8"))
    assert len(d)==270
    a,b,c=d[0],d[1],d[2]
    assert a["shot_id"]=="S001" and a["status"].startswith("HOLD")
    assert a["haoh ao_runtime_prompt"].count("@Orin")>=1
    assert a["location"]=="VeyloraPast_PENDING"
    assert b["character_tags"]==["MARA","BIX"]
    assert b["location"]=="BellKitchen_Day" and b["status"].startswith("PILOT")
    assert "@Evan" not in b["one_line_video_prompt"]
    assert c["character_tags"]==["BIX","JUNO"]
    assert c["voice_runtime_lines"] and c["voice_runtime_lines"][0].startswith("@Juno [")
    assert all("GrandBellHall" not in x["one_line_video_prompt"] for x in d)


def test_no_false_voice_4k_face_or_media_approval():
    a=json.loads((OUT/"EP001_SUMMARY.json").read_text(encoding="utf8"))
    assert a["total"]==270 and a["eligible"]+a["hold"]==270
    assert a["multispeaker_hold"]>=57
    assert a["missing_location"]>=150
    assert a["missing_aila"]==53
    assert a["phantom_cast"]==0
    assert a["production_authorized"] is False
    assert a["native_4k_proven"] is False and a["voice_lipsync_proven"] is False
    for rec in json.loads((OUT/"EP001_QC_MANIFEST.json").read_text(encoding="utf8")):
        if rec["status"].startswith("PILOT"):
            assert rec["location_matched"]
            assert not rec["blockers"]
            assert len(rec["voice_speakers"])<=1
        for line in rec["voice_runtime_lines"]:
            m=re.fullmatch(r'@(.+?) \[([a-z]+)\]: "(.+)"',line)
            assert m and m.group(2) in VALID


def test_source_and_export_have_same_270_ids():
    source=json.loads(BIND.read_text(encoding="utf8"))["shots"]
    manifest=json.loads((OUT/"EP001_QC_MANIFEST.json").read_text(encoding="utf8"))
    assert [x["shot_id"] for x in manifest]==[x["shot_id"] for x in source]
    assert [x["scene_id"] for x in manifest]==[x["scene_id"] for x in source]


def test_pilot_file_contains_only_audited_shots():
    txt=read_prompts("EP001_PILOT_ELIGIBLE_ONE_LINE.txt")
    ids=[re.match(r"EP001 (S\d{3})",s).group(1) for s in txt]
    assert ids==["S002","S003","S005","S010","S011"]
