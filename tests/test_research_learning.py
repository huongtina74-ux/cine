import json
import pytest
from cinefactory.research_intelligence.learning import ingest_department_result, propose_learning


def task(approved=True):
    return {"schema": "cine.research.task.v1", "approval_status": "approved" if approved else "pending_approval", "task_id": "v1:visual", "department": "visual"}


def test_review_evidence_required(tmp_path):
    payload = {"findings": [{"status": "VERIFIED", "claim": "camera moves", "evidence": []}]}
    with pytest.raises(ValueError):
        ingest_department_result(task(), payload, tmp_path / "out.json")
    with pytest.raises(PermissionError):
        ingest_department_result(task(False), payload, tmp_path / "out.json")


def test_proposals_never_self_promote(tmp_path):
    report = ingest_department_result(task(), {"findings": [{"status": "VERIFIED", "claim": "frame shows overhead camera", "evidence": [{"timestamp_seconds": 10}]}]}, tmp_path / "review.json")
    feedback = {"schema": "cine.research.feedback.v1", "reference_source": "reference.mp4", "produced_source": "owned.mp4", "owned_metrics": {"views": 100}}
    output = propose_learning(feedback, [report], tmp_path / "learning.json")
    assert output["state"] == "awaiting_experiment_and_human_approval"
    assert output["proposals"][0]["decision"] == "pending_validation"
    assert json.loads((tmp_path / "learning.json").read_text(encoding="utf-8"))["schema"] == "cine.research.learning.v1"


def test_missing_feedback_rejected(tmp_path):
    with pytest.raises(ValueError):
        propose_learning({}, [], tmp_path / "bad.json")


def test_claude_bridge_fake_runner(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from cinefactory.research_intelligence import claude_bridge
    evidence = tmp_path / "observation.json"
    evidence.write_text(json.dumps({"schema":"cine.research.observation.v1","frames":[]}), encoding="utf-8")
    t = task()
    t["evidence_path"] = str(evidence)
    path = tmp_path / "task.json"
    path.write_text(json.dumps(t), encoding="utf-8")
    monkeypatch.setattr(claude_bridge.shutil, "which", lambda _: "claude")
    calls = []
    def runner(argv, **kwargs):
        calls.append((argv, kwargs))
        return SimpleNamespace(returncode=0, stdout='{"result":"ok"}', stderr="")
    monkeypatch.setattr(claude_bridge.subprocess, "run", runner)
    output = claude_bridge.run_approved_task(str(path), str(tmp_path / "result.json"))
    assert output["exit_code"] == 0
    assert "--permission-mode" in calls[0][0]
    assert "plan" in calls[0][0]
    assert (tmp_path / "result.json").exists()
