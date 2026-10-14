from pathlib import Path
import pytest
from cinefactory.research_intelligence import pod_daily_runner as run


def test_daily_runner_persists_immutable_attempts(tmp_path):
    pods=tmp_path/"pods";pods.mkdir()
    bridges=tmp_path/"bridges";bridges.mkdir()
    reports=tmp_path/"state"
    a=run.run_pod_daily(pods,bridges,reports,day="2026-10-10")
    b=run.run_pod_daily(pods,bridges,reports,day="2026-10-10")
    assert a["state"]=="NO_PODS"
    assert a["attempt"]==1 and b["attempt"]==2
    assert Path(a["summary_path"]).is_file()
    assert Path(b["summary_path"]).is_file()
    assert a["production_permission"] is False
    assert not (reports/"2026-10-10"/".dispatcher.lock").exists()


def test_lock_refuses_concurrent_attempt(tmp_path):
    pods=tmp_path/"pods";pods.mkdir()
    bridges=tmp_path/"bridges";bridges.mkdir()
    loc=tmp_path/"state"/"2026-10-10";loc.mkdir(parents=True)
    (loc/".dispatcher.lock").write_text("existing runner",encoding="utf-8")
    with pytest.raises(RuntimeError,match="lock"):
        run.run_pod_daily(pods,bridges,tmp_path/"state",day="2026-10-10")
    assert (loc/".dispatcher.lock").exists()


def test_bad_partition_rejected(tmp_path):
    with pytest.raises(ValueError):
        run.run_pod_daily(tmp_path,tmp_path,tmp_path/"state",day="tomorrow")


def test_scheduler_failure_creates_persistent_blocked_attempt_and_keeps_lock_free(tmp_path):
    pods=tmp_path/"missing_pods"
    bridges=tmp_path/"missing_bridges"
    state=tmp_path/"state"
    result=run.run_pod_daily(pods,bridges,state,day="2026-10-10")
    assert result["state"]=="BLOCKED_DISPATCH_ERROR"
    assert result["production_permission"] is False
    assert result["error_type"]=="FileNotFoundError"
    assert (state/"2026-10-10"/"attempt_001"/"summary.json").exists()
    assert not (state/"2026-10-10"/".dispatcher.lock").exists()
    import json
    persisted=json.loads((state/"2026-10-10"/"latest_run.json").read_text(encoding="utf-8"))
    assert persisted["state"]=="BLOCKED_DISPATCH_ERROR"
    pods.mkdir();bridges.mkdir()
    fresh=run.run_pod_daily(pods,bridges,state,day="2026-10-10")
    assert fresh["state"]=="NO_PODS"
    assert fresh["attempt"]==2
