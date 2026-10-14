import shutil
import subprocess
import pytest
from cinefactory.research_intelligence import observe_video, create_department_tasks, assess_production


def test_requires_observed_evidence(tmp_path):
    with pytest.raises(ValueError):
        create_department_tasks({"source": "made-up"}, tmp_path, niche="game", reference_id="v1")
    with pytest.raises(ValueError):
        assess_production({}, {})


def test_department_dispatch(tmp_path):
    obs = {"schema": "cine.research.observation.v1", "source": "test.mp4", "duration_seconds": 20, "frames": [{"second": 0}]}
    result = create_department_tasks(obs, tmp_path, niche="animation", reference_id="v1")
    assert len(result["tasks"]) == 9
    assert all(task["approval_status"] == "pending_approval" for task in result["tasks"])
    assert (tmp_path / "tasks" / "animation.json").exists()


def test_feedback_validations():
    obs = {"schema": "cine.research.observation.v1", "source": "test.mp4", "duration_seconds": 20, "frames": [{"second": 0}]}
    result = assess_production(obs, obs, {"views": 1000, "ctr": 0.05})
    assert result["duration_ratio"] == 1
    with pytest.raises(ValueError):
        assess_production(obs, obs, {"ctr": 12})


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg tools unavailable")
def test_real_video_observation(tmp_path):
    video = tmp_path / "real.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=2", "-t", "2", "-c:v", "mpeg4", str(video)], check=True, capture_output=True)
    observation = observe_video(video, tmp_path / "evidence", interval_seconds=1, max_frames=3)
    assert observation["frames"]
    assert all((tmp_path / "evidence" / "frames").joinpath(f"frame_{i:04d}.jpg").is_file() for i in range(len(observation["frames"])))
    assert observation["semantic_analysis"].startswith("NOT_PERFORMED")


def test_claude_requires_explicit_approval(tmp_path):
    import json
    from cinefactory.research_intelligence.claude_bridge import run_approved_task
    task = {"schema": "cine.research.task.v1", "department": "visual", "task_id": "v1:visual", "approval_status": "pending_approval", "evidence_path": "none"}
    path = tmp_path / "task.json"
    path.write_text(json.dumps(task), encoding="utf-8")
    with pytest.raises(PermissionError):
        run_approved_task(str(path), str(tmp_path / "result.json"))


def test_dispatch_evidence_copy(tmp_path):
    import json
    obs = {"schema": "cine.research.observation.v1", "source": "test.mp4", "duration_seconds": 2, "frames": []}
    create_department_tasks(obs, tmp_path, niche="original", reference_id="123")
    assert json.loads((tmp_path / "observation.json").read_text(encoding="utf-8")) == obs
