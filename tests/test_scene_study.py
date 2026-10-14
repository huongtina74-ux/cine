from __future__ import annotations
import hashlib
import json
import subprocess
from pathlib import Path
import pytest

from cinefactory.research_intelligence.deep_video_intelligence import observe_authorized_footage
from cinefactory.production.scene_study import (
    prepare_timestamped_study,validate_editorial_annotations,
)

def hash_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

@pytest.fixture
def study(tmp_path):
    mp4=tmp_path/"owned.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                    "-f","lavfi","-i","testsrc2=size=320x180:duration=3:rate=12",
                    "-f","lavfi","-i","sine=frequency=440:duration=3",
                    "-c:v","mpeg4","-q:v","5","-c:a","aac","-shortest",str(mp4)],
                   check=True,timeout=30)
    observe_authorized_footage(mp4,tmp_path/"observed",niche="Minecraft animation",
                               video_id="TESTvid1234",authorization="OWNED",max_frames=4)
    path=tmp_path/"study.json"
    result=prepare_timestamped_study(tmp_path/"observed"/"deep_video_manifest.json",path)
    return tmp_path,path,result

def test_real_frames_have_original_pixel_hash_and_time(study):
    root,path,data=study
    assert data["state"]=="OBSERVED_PIXELS_ANNOTATIONS_PENDING"
    assert len(data["frame_evidence"])==4
    assert data["source_rights_authenticated"] is False
    assert data["observed_full_video_story"] is False
    assert data["frame_evidence"][0]["visible_action"]=="UNKNOWN_REQUIRES_VISUAL_INSPECTION"

def test_direct_frame_review_is_only_a_partial_claim(study):
    root,path,data=study
    point=data["frame_evidence"][0]
    notes={"schema":"cine.studio.direct_frame_annotations.v1",
           "study_sha256":hash_file(path),
           "observations":[{"category":"lighting_art","sample_id":point["sample_id"],
                            "second":point["second"],"scope":"DIRECT_OBSERVATION",
                            "modality":"VISIBLE_FRAME",
                            "description":"The frame has a visible red upper-left region and blue objects in center."}]}
    notes_file=root/"notes.json"
    notes_file.write_text(json.dumps(notes),encoding="utf-8")
    report=validate_editorial_annotations(path,notes_file,root/"checked.json")
    assert report["annotation_count"]==1
    assert report["independent_reviewer_authenticated"] is False
    assert report["narrative_understanding"]=="PARTIAL_FRAME_NOT_FULL_VIDEO"

def test_fake_timestamp_rejected(study):
    root,path,data=study
    notes={"schema":"cine.studio.direct_frame_annotations.v1",
           "study_sha256":hash_file(path),
           "observations":[{"category":"character_expression","sample_id":"frame_FAKE",
                            "second":1234,"scope":"DIRECT_OBSERVATION",
                            "modality":"VISIBLE_FRAME",
                            "description":"Fake evidence wrongly claims an expression."}]}
    nf=root/"notes.json";nf.write_text(json.dumps(notes),encoding="utf-8")
    with pytest.raises(ValueError,match="timestamp"):
        validate_editorial_annotations(path,nf,root/"bad.json")

def test_audio_claim_cannot_be_made_from_still_frame(study):
    root,path,data=study
    x=data["frame_evidence"][1]
    notes={"schema":"cine.studio.direct_frame_annotations.v1",
           "study_sha256":hash_file(path),
           "observations":[{"category":"sound_foley","sample_id":x["sample_id"],
                            "second":x["second"],"scope":"DIRECT_OBSERVATION",
                            "modality":"AUDIBLE_FULL_VIDEO",
                            "description":"Music swells for five seconds, which still frames cannot show."}]}
    nf=root/"notes.json";nf.write_text(json.dumps(notes),encoding="utf-8")
    with pytest.raises(ValueError,match="Sparse frames"):
        validate_editorial_annotations(path,nf,root/"bad.json")

def test_modified_frame_fails_replay(study):
    root,path,data=study
    framefile=Path(root/"observed"/"frames"/"frame_0000.jpg")
    framefile.write_bytes(framefile.read_bytes()+b"mutated")
    with pytest.raises(ValueError,match="hash"):
        prepare_timestamped_study(root/"observed"/"deep_video_manifest.json",root/"bad.json")
