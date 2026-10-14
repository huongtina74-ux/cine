"""Multimodal evidence collection does not invent inaccessible video semantics."""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from cinefactory.research_intelligence.deep_video_intelligence import (
    prepare_public_video_review, observe_authorized_footage, verify_deep_video_review,
)

VID="Wq6KnyIErYs"
FOREIGN="05IwOFRKYC4"
CID="UC"+"a"*22


def _digest(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()


@pytest.fixture
def inputs(tmp_path):
    files={}
    for key in ("search","plan","catalog"):
        path=tmp_path/f"{key}.json"
        path.write_text(json.dumps({"from":key}),encoding="utf-8")
        files[key]={"path":str(path),"sha256":_digest(path)}
    report={
        "schema":"cine.research.automated_evidence.v1",
        "state":"PUBLIC_EVIDENCE_READY_FOR_REVIEW","niche":"Minecraft animation",
        "source_files":files,
        "channels":[{
            "channel_id":CID,"channel_name":"Animation leader",
            "sample_longform_videos":[
                {"video_id":VID,"title":"Minecraft Animation Original",
                 "approx_views":1_300_000,"video_age_days_proxy":21,
                 "topic_title_alignment":"ALL_NICHE_TITLE_TOKENS_PRESENT"},
                {"video_id":FOREIGN,"title":"Poppy Playtime",
                 "approx_views":1_700_000,"video_age_days_proxy":14,
                 "topic_title_alignment":"NOT_TITLE_ALIGNED"}],
        }],
        "per_video_work_packets":{
            "leader_review":[{"video_id":VID,"channel_id":CID}],
            "fresh_million_review":[],
            "newcomer_review":[],
            "cross_topic_qa":[{"video_id":FOREIGN,"channel_id":CID}],
        }
    }
    path=tmp_path/"evidence.json"
    path.write_text(json.dumps(report),encoding="utf-8")
    return path,files


def image_bytes():
    from PIL import Image
    stream=io.BytesIO()
    Image.new("RGB",(320,180),(80,140,210)).save(stream,format="JPEG")
    return stream.getvalue()


def test_actual_thumbnail_bytes_recorded_but_semantics_unknown(inputs,tmp_path):
    inp,_=inputs
    report=prepare_public_video_review(inp,tmp_path/"out",max_videos=2,fetch_image=lambda _:image_bytes())
    assert report["selected_count"]==1
    assert report["thumbnails_observed"]==1
    row=report["videos"][0]
    assert row["video_id"]==VID
    assert row["thumbnail_image_facts"]["width"]==320
    assert row["thumbnail_image_facts"]["semantic_content"]=="NOT_ANALYZED"
    assert row["story_hook_status"]=="UNKNOWN"
    assert row["actual_video_frames_status"]=="NOT_OBSERVED"
    assert row["copyright_clearance"]=="NOT_CLEARED"
    assert report["production_permission"] is False
    assert (tmp_path/"out"/(VID+".jpg")).is_file()
    assert report["source_evidence"]["sha256"]==_digest(inp)


def test_thumbnail_failure_is_observable_not_fake_success(inputs,tmp_path):
    def unavailable(vid):
        raise TimeoutError("simulated")
    report=prepare_public_video_review(inputs[0],tmp_path/"out",fetch_image=unavailable)
    assert report["selected_count"]==1
    assert report["thumbnails_observed"]==0
    assert report["videos"][0]["thumbnail_status"]=="THUMBNAIL_UNAVAILABLE"
    assert report["videos"][0]["story_hook_status"]=="UNKNOWN"


def test_html_payload_never_saved_as_thumbnail(inputs,tmp_path):
    report=prepare_public_video_review(inputs[0],tmp_path/"out",fetch_image=lambda _:b"<html>fake</html>")
    assert report["thumbnails_observed"]==0
    assert not list((tmp_path/"out").glob("*.jpg"))


def test_edited_original_source_is_rejected(inputs,tmp_path):
    inp,files=inputs
    Path(files["catalog"]["path"]).write_text('{"modified":true}',encoding="utf-8")
    with pytest.raises(ValueError,match="mutated"):
        prepare_public_video_review(inp,tmp_path/"should_not_exist")
    assert not (tmp_path/"should_not_exist").exists()


def test_no_promotion_from_partial_evidence(inputs,tmp_path):
    inp,_=inputs
    packet=json.loads(inp.read_text(encoding="utf-8"))
    packet["state"]="PARTIAL_EVIDENCE"
    inp.write_text(json.dumps(packet),encoding="utf-8")
    with pytest.raises(ValueError,match="Partial/historical"):
        prepare_public_video_review(inp,tmp_path/"failed")


def test_cross_topic_high_view_id_cannot_enter_thumbnail_list(inputs,tmp_path):
    inp,_=inputs
    packet=json.loads(inp.read_text(encoding="utf-8"))
    packet["per_video_work_packets"]["leader_review"].append({"video_id":FOREIGN,"channel_id":CID})
    inp.write_text(json.dumps(packet),encoding="utf-8")
    report=prepare_public_video_review(inp,tmp_path/"out",fetch_image=lambda _:image_bytes())
    assert [x["video_id"] for x in report["videos"]]==[VID]


def test_replay_of_same_output_rejected(inputs,tmp_path):
    inp,_=inputs
    prepare_public_video_review(inp,tmp_path/"out",fetch_image=lambda _:image_bytes())
    with pytest.raises(FileExistsError):
        prepare_public_video_review(inp,tmp_path/"out",fetch_image=lambda _:image_bytes())


def test_local_observation_requires_explicit_rights_before_side_effect(tmp_path):
    movie=tmp_path/"clip.mp4"
    movie.write_bytes(b"dummy")
    with pytest.raises(PermissionError,match="Explicit"):
        observe_authorized_footage(movie,tmp_path/"none",niche="Minecraft animation",
                                   video_id=VID,authorization="PUBLIC_URL")
    assert not (tmp_path/"none").exists()


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"),reason="FFmpeg unavailable")
def test_real_ffmpeg_synthetic_video_frames_and_audio(tmp_path):
    video=tmp_path/"synthetic-owned.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                    "-f","lavfi","-i","testsrc2=duration=4:size=320x180:rate=10",
                    "-f","lavfi","-i","sine=frequency=440:duration=4",
                    "-c:v","mpeg4","-q:v","5","-c:a","aac","-shortest",str(video)],
                   check=True,timeout=30)
    out=observe_authorized_footage(video,tmp_path/"review",niche="Minecraft animation",
                                   video_id=VID,authorization="OWNED",max_frames=4,
                                   detect_changes=False)
    assert out["state"]=="FRAMES_AND_AUDIO_MEASURED_SEMANTICS_PENDING"
    assert out["frames_observed"]==4
    assert out["audio_measured"]
    assert not out["actual_semantic_analysis_completed"]
    assert out["department_task_count"]==7
    observation=json.loads((tmp_path/"review"/"observation.json").read_text(encoding="utf-8"))
    assert len(observation["frames"])==4
    assert all(Path(frame["path"]).is_file() for frame in observation["frames"])
    tasks=json.loads((tmp_path/"review"/"review_tasks"/"dispatch.json").read_text(encoding="utf-8"))
    assert all(t["approval_status"]=="pending_approval" for t in tasks["tasks"])
    assert "NOT_PERFORMED" in observation["semantic_analysis"]


def test_video_review_integrity_verifier_detects_image_tamper(inputs,tmp_path):
    inp,_=inputs
    prepare_public_video_review(inp,tmp_path/"out",fetch_image=lambda _:image_bytes())
    review=tmp_path/"out"/"deep_review.json"
    result=verify_deep_video_review(review)
    assert result["verified_thumbnails"]==1
    assert not result["production_permission"]
    (tmp_path/"out"/(VID+".jpg")).write_bytes(image_bytes()+b"changed")
    with pytest.raises(ValueError,match="changed"):
        verify_deep_video_review(review)


def test_video_review_integrity_preserves_same_council_issue(inputs,tmp_path):
    inp,_=inputs
    council=inp.parent/"council"
    council.mkdir()
    issue={"issue_id":"review-minecraft-animation-abcdef123456",
           "question":"Does the evidence justify a cautious experiment?"}
    path=council/"council_issue.json"
    path.write_text(json.dumps(issue),encoding="utf-8")
    report=prepare_public_video_review(inp,tmp_path/"out",fetch_image=lambda _:image_bytes())
    assert report["canonical_council_issue"]["issue_id"]==issue["issue_id"]
    integrity=verify_deep_video_review(tmp_path/"out"/"deep_review.json")
    assert integrity["council_issue_id"]==issue["issue_id"]
    path.write_text(json.dumps({"issue_id":"fake","question":"Change result"}),encoding="utf-8")
    with pytest.raises(ValueError,match="altered"):
        verify_deep_video_review(tmp_path/"out"/"deep_review.json")


def test_video_review_integrity_blocks_fake_story_analysis(inputs,tmp_path):
    inp,_=inputs
    prepare_public_video_review(inp,tmp_path/"out",fetch_image=lambda _:image_bytes())
    p=tmp_path/"out"/"deep_review.json"
    packet=json.loads(p.read_text(encoding="utf-8"))
    packet["videos"][0]["story_hook_status"]="VERIFIED"
    p.write_text(json.dumps(packet),encoding="utf-8")
    with pytest.raises(ValueError,match="uninspected"):
        verify_deep_video_review(p)


def test_public_thumbnail_redirect_to_non_youtube_host_rejected(monkeypatch):
    from cinefactory.research_intelligence.deep_video_intelligence import _public_thumbnail
    class FakeResponse:
        status=200
        headers={"Content-Type":"image/jpeg"}
        def __enter__(self): return self
        def __exit__(self,*args): return False
        def geturl(self): return "https://evil.example/vi/Wq6KnyIErYs/hqdefault.jpg"
        def read(self,max_bytes): return image_bytes()
    monkeypatch.setattr(
        "cinefactory.research_intelligence.deep_video_intelligence.urlopen",
        lambda *args,**kwargs: FakeResponse(),
    )
    with pytest.raises(ValueError,match="redirected"):
        _public_thumbnail(VID)
