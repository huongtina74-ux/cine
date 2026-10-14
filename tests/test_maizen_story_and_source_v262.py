"""Test preproduction continuity and 30sec evidence accuracy, fail closed."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import pytest
from PIL import Image
from cinefactory.studio.maizen_story_alignment_v262 import make_alignment
from cinefactory.studio import maizen_source_structural_qc_v262 as qc

def _write(path:Path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj),encoding="utf8")

def _originals(root):
    base=root/"data/verification/v243_maizen_original_preproduction"
    beats=[{"id":f"B{i+1:02d}","start":start,"end":end}
           for i,(start,end) in enumerate([(0,15),(15,32),(32,50)]+
             [(50+(i-3)*40,90+(i-3)*40) for i in range(3,21)])]
    _write(base/"original_story_and_21_beats.json",
           {"project_id":"MAI01_WATERFALL","beats":beats})
    _write(base/"nine_pilot_shots.json",
           {"project_id":"MAI01_WATERFALL","pilot_seconds":45,
            "shots":[{"shot_id":f"P{i+1:02d}"} for i in range(9)]})
    return base

def test_revised_original_pilot_matches_b01_to_b03_and_preserves_source(tmp_path):
    old=_originals(tmp_path)
    original=(old/"nine_pilot_shots.json").read_bytes()
    new=make_alignment(root=tmp_path,write=True)
    v=new["corrected_45s_original_pilot"]
    assert (old/"nine_pilot_shots.json").read_bytes()==original
    assert [(s["start"],s["end"]) for s in v["shots"]]==[(i*5,(i+1)*5) for i in range(9)]
    assert v["shots"][2]["end_state"]=="SKETCH_VISIBLE_UNOWNED"
    assert v["shots"][3]["end_state"]=="SKETCH_WITH_PIP"
    assert v["shots"][-1]["end_state"].endswith("CHOICE_PENDING")
    assert len(new["episode_story_continuity_amendments"])==8
    assert new["gates"]["G16_G28"].startswith("HOLD")
    assert not new["pilot_vo_fully_recorded"]
    assert not new["script_14m_fully_written_and_approved"]

def test_missing_original_story_source_cannot_generate_pilot(tmp_path):
    _originals(tmp_path)
    p=tmp_path/"data/verification/v243_maizen_original_preproduction/original_story_and_21_beats.json"
    obj=json.loads(p.read_text());obj["beats"][0]["end"]=14
    _write(p,obj)
    with pytest.raises(ValueError,match="SOURCE_BEAT_TIMELINE_DRIFT"):
        make_alignment(root=tmp_path)

def test_bad_project_id_rejected(tmp_path):
    base=_originals(tmp_path)
    p=base/"original_story_and_21_beats.json"
    obj=json.loads(p.read_text());obj["project_id"]="OTHER"
    _write(p,obj)
    with pytest.raises(ValueError,match="PROJECT_ORIGINAL_PROVENANCE"):
        make_alignment(root=tmp_path)

def _fake_media(root:Path):
    p=root/".tools/maizen_peer_av_v260/SOURCE1"
    (p/"frames").mkdir(parents=True)
    sounds=[]
    segments=[(.6,19.9),(19.7,35.0)]
    for i,(start,end) in enumerate(segments):
        sound=b"placeholder-audio-data"*120
        fp=p/f"seg_{i:02d}.webm";fp.write_bytes(sound)
        pic=p/"frames"/f"seg_{i:02d}_0009.jpg"
        Image.new("RGB",(320,180)).save(pic)
        _write(p/f"seg_{i:02d}.json",{
           "video_id":"SOURCE1","status":"COMPLETE","i":i,
           "player_start":start,"player_end":end,
           "frames":[{"time":9+i*18,"file":pic.name}],
           "audio_bytes":len(sound),
           "audio_sha256":hashlib.sha256(sound).hexdigest()})
    _write(p/"audit.json",{"source_id":"SOURCE1","expected_duration":35,
            "segments":2,"complete":2,"frames":2})
    return p

def test_structural_audit_never_mistakes_audio_files_for_full_listening(tmp_path,monkeypatch):
    _fake_media(tmp_path)
    monkeypatch.setattr(qc,"VIDEOS",{"SOURCE1":35})
    r=qc.audit(root=tmp_path,write=True,decode_audio=False)
    assert r["30_second_windows_count"]==2
    assert r["browser_segments_count"]==2
    assert r["sparse_frames_count"]==2
    assert r["G02"]=="PENDING_INDEPENDENT_NATIVE_AV_SEMANTIC_QC"
    assert r["reviewer_signoff_exists"] is False
    assert r["source_playback_was_2x"]
    assert r["videos"][0]["windows"][0]["maximum_player_timeline_gap_seconds"]>0.3
    assert all(x["audio_encoded_files_hash_verified"] for x in r["videos"][0]["windows"])

def test_tampered_audio_hash_fails_closed(tmp_path,monkeypatch):
    path=_fake_media(tmp_path)
    monkeypatch.setattr(qc,"VIDEOS",{"SOURCE1":35})
    (path/"seg_00.webm").write_bytes(b"tampered"*400)
    with pytest.raises(ValueError,match="SEGMENT_AUDIO_(HASH|SIZE)_MISMATCH"):
        qc.audit(root=tmp_path,decode_audio=False)
