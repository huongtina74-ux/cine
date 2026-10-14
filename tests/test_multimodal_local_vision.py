import json
import subprocess
from pathlib import Path
import pytest

from cinefactory.research_intelligence.smart import observe_smart
from cinefactory.research_intelligence.scene_measurement import measure_sampled_frames
from cinefactory.research_intelligence.local_vision_adapter import review_local_vision
from cinefactory.research_intelligence.vision_quality import quality_review_packet


@pytest.fixture
def scene(tmp_path):
    movie=tmp_path/"owned.mp4"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                    "-f","lavfi","-i","testsrc2=duration=3:size=320x180:rate=10",
                    "-f","lavfi","-i","sine=frequency=330:duration=3",
                    "-c:v","mpeg4","-q:v","5","-c:a","aac","-shortest",str(movie)],
                   check=True,timeout=30)
    observation=tmp_path/"observed"
    observe_smart(movie,observation,max_frames=3,detect_changes=False)
    measure_sampled_frames(observation/"observation.json",tmp_path/"scene.json")
    return tmp_path


def test_metrics_and_blocked_model(scene):
    report=json.loads((scene/"scene.json").read_text(encoding="utf-8"))
    assert report["frame_count"]==3
    assert report["conclusions_about_story_hook"]=="UNKNOWN"
    assert all(0<=s["mean_luminance_0_255"]<=255 for s in report["samples"])
    model=review_local_vision(scene/"scene.json",scene/"blocked.json")
    assert model["state"]=="BLOCKED_NO_LOCAL_VISION_MODEL"
    assert model["findings"]==[]
    task=quality_review_packet(scene/"blocked.json",scene/"qa.json")
    assert task["state"]=="INDEPENDENT_IMAGE_REVIEW_PENDING"
    assert not task["independent_evaluation_completed"]


def test_stubbed_vision_claim_is_pending_not_approved(scene):
    def stub(payload,url,timeout):
        items=payload["messages"][1]["content"]
        assert sum(x["type"]=="image_url" for x in items)==2
        frame=json.loads(items[1]["text"])
        return {"role":"visual","findings":[{
            "evidence_id":frame["evidence_id"],"second":frame["second"],
            "scope":"VISIBLE_IMAGE_ONLY",
            "claim":"The visible frame contains contrasting color regions.",
            "confidence":0.7}]}
    model=review_local_vision(scene/"scene.json",scene/"model.json",
                              role="visual",model="local",max_images=2,
                              execute=True,client=stub)
    assert model["state"]=="MODEL_CLAIMS_PENDING_INDEPENDENT_QUALITY_REVIEW"
    assert model["findings"][0]["status"]=="MODEL_HYPOTHESIS_PENDING_QA"
    qa=quality_review_packet(scene/"model.json",scene/"quality.json")
    assert len(qa["items"])==1
    assert qa["items"][0]["quality_status"]=="NOT_INSPECTED"
    assert qa["production_permission"] is False


def test_wrong_frame_id_fails_closed(scene):
    def fake(payload,url,timeout):
        return {"role":"visual","findings":[{
            "evidence_id":"frame_FAKE","second":0,"scope":"VISIBLE_IMAGE_ONLY",
            "claim":"Invalid frame ID is not a valid citation.","confidence":1.0}]}
    report=review_local_vision(scene/"scene.json",scene/"bad.json",
                                model="local",execute=True,client=fake)
    assert report["state"]=="MODEL_RUN_FAILED"
    assert report["findings"]==[]


def test_remote_api_url_forbidden(scene):
    with pytest.raises(ValueError,match="loopback"):
        review_local_vision(scene/"scene.json",scene/"missing.json",
                            endpoint="https://api.example.com/v1/chat/completions")
    assert not (scene/"missing.json").exists()


def test_modified_original_frame_invalidates_inference(scene):
    packet=json.loads((scene/"scene.json").read_text(encoding="utf-8"))
    picture=Path(packet["samples"][0]["path"])
    picture.write_bytes(picture.read_bytes()+b"tamper")
    with pytest.raises(ValueError,match="hash"):
        review_local_vision(scene/"scene.json",scene/"refused.json")


def test_impossible_story_claim_is_rejected(scene):
    def fake(payload,url,timeout):
        item=json.loads(payload["messages"][1]["content"][1]["text"])
        return {"role":"visual","findings":[{
            "evidence_id":item["evidence_id"],"second":item["second"],
            "scope":"COMPLETE_VIDEO_STORY","claim":"One frame proves retention quality.",
            "confidence":1.0}]}
    result=review_local_vision(scene/"scene.json",scene/"false.json",
                               model="local",execute=True,client=fake)
    assert result["state"]=="MODEL_RUN_FAILED"
    assert result["story_verified"] is False


def test_quality_refuses_fake_production_permission(scene):
    review_local_vision(scene/"scene.json",scene/"blocked.json")
    p=scene/"blocked.json"
    obj=json.loads(p.read_text(encoding="utf-8"))
    obj["production_permission"]=True
    p.write_text(json.dumps(obj),encoding="utf-8")
    with pytest.raises(ValueError,match="promoted"):
        quality_review_packet(p,scene/"refused.json")
