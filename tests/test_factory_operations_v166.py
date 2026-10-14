from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from cinefactory.studio.factory_operations import (
    FactoryOperationsManager,
    FactoryOperationsPolicy,
    FactoryOperationsStore,
    FactoryProjectRequest,
    OperatingProjectState,
    ProjectPriority,
)
from cinefactory.turbo.contracts import ResourceClass, WorkerSpec, WorkItem, WorkState
from cinefactory.turbo.store import TurboStore


def _manager(tmp_path: Path, **policy):
    turbo = TurboStore(tmp_path / "turbo.db")
    manager = FactoryOperationsManager(
        turbo_store=turbo,
        store=FactoryOperationsStore(tmp_path / "operations"),
        policy=FactoryOperationsPolicy(**policy),
    )
    return turbo, manager


def test_admission_queue_respects_active_project_limit(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "cinefactory.studio.factory_operations.gpu_snapshot",
        lambda: {
            "available": True,
            "gpus": [{"vram_mb": 12288, "vram_used_mb": 512}],
        },
    )
    _, manager = _manager(tmp_path, max_active_projects=1)
    first = manager.submit(
        FactoryProjectRequest(project_id="P1", priority=ProjectPriority.HIGH)
    )
    second = manager.submit(
        FactoryProjectRequest(project_id="P2", priority=ProjectPriority.NORMAL)
    )
    assert first.state is OperatingProjectState.ADMITTED
    assert second.state is OperatingProjectState.QUEUED
    manager.start("P1")
    manager.finish("P1", success=True)
    assert manager.reevaluate_queue() == ["P2"]
    assert manager.store.get("P2").state is OperatingProjectState.ADMITTED


def test_vram_aware_claim_refuses_oversized_gpu_work(tmp_path: Path):
    turbo = TurboStore(tmp_path / "turbo.db")
    turbo.enqueue_work(
        WorkItem(
            project_id="P1",
            kind="render",
            handler="render",
            resource=ResourceClass.GPU,
            payload={"required_vram_gb": 8.0},
        )
    )
    worker = WorkerSpec(
        worker_id="GPU0",
        resources={ResourceClass.GPU},
        capabilities={"render"},
        metadata={
            "vram_reserve_gb": 1.0,
            "gpu": {
                "available": True,
                "gpus": [{"vram_mb": 12288, "vram_used_mb": 9216}],
            },
        },
    )
    assert turbo.claim_work(worker) is None


def test_transient_dead_letter_is_recovered_once(tmp_path: Path):
    turbo, manager = _manager(
        tmp_path,
        max_dead_letter_recoveries=1,
    )
    item = WorkItem(
        project_id="P1",
        kind="render",
        handler="render",
        resource=ResourceClass.GPU,
        max_attempts=1,
    )
    turbo.enqueue_work(item)
    worker = WorkerSpec(
        worker_id="GPU0",
        resources={ResourceClass.GPU},
        capabilities={"render"},
    )
    claimed = turbo.claim_work(worker)
    assert claimed is not None
    turbo.mark_running(claimed.work_id)
    assert turbo.finish_work(
        claimed.work_id,
        False,
        "worker exited after timeout",
    ) is WorkState.DEAD_LETTER

    recovered = manager.recover_transient_dead_letters()
    assert len(recovered) == 1
    clone = turbo.get_work(recovered[0])
    assert clone.state is WorkState.QUEUED
    assert clone.payload["recovery_of"] == item.work_id
    assert clone.payload["_recovery_count"] == 1


def test_project_priority_and_vram_budget_decorate_work(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "cinefactory.studio.factory_operations.gpu_snapshot",
        lambda: {
            "available": True,
            "gpus": [{"vram_mb": 12288, "vram_used_mb": 512}],
        },
    )
    turbo, manager = _manager(tmp_path)
    manager.submit(
        FactoryProjectRequest(
            project_id="P_HIGH",
            priority=ProjectPriority.HIGH,
            required_vram_gb=5.5,
        )
    )
    item, inserted = manager.enqueue_work(
        WorkItem(
            project_id="P_HIGH",
            kind="render",
            handler="render",
            resource=ResourceClass.GPU,
            priority=20,
        )
    )
    assert inserted is True
    stored = turbo.get_work(item.work_id)
    assert stored.priority == 75
    assert stored.payload["required_vram_gb"] == 5.5


def test_watchdog_marks_stale_workers_unhealthy(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "cinefactory.studio.factory_operations.gpu_snapshot",
        lambda: {"available": False, "reason": "test"},
    )
    turbo, manager = _manager(tmp_path, stale_worker_seconds=30)
    worker = WorkerSpec(
        worker_id="STALE",
        resources={ResourceClass.CPU},
        last_heartbeat=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    turbo.upsert_worker(worker)
    report = manager.watchdog_tick()
    assert "STALE" in report.health.stale_workers
    row = next(item for item in turbo.list_workers() if item["worker_id"] == "STALE")
    assert row["healthy"] == 0


def test_health_exposes_execution_economics(monkeypatch, tmp_path: Path):
    from cinefactory.turbo.contracts import ExecutionCostSample

    monkeypatch.setattr(
        "cinefactory.studio.factory_operations.gpu_snapshot",
        lambda: {"available": False, "reason": "test"},
    )
    turbo, manager = _manager(tmp_path)
    turbo.add_execution_cost(
        ExecutionCostSample(
            work_id="W1",
            project_id="P1",
            worker_id="GPU0",
            kind="block.render",
            resource=ResourceClass.GPU,
            state=WorkState.QC_REJECTED,
            duration_seconds=3.0,
            output_units=24.0,
            accepted=False,
            repair_round=0,
        )
    )
    turbo.add_execution_cost(
        ExecutionCostSample(
            work_id="W2",
            project_id="P1",
            worker_id="GPU0",
            kind="block.render.repair",
            resource=ResourceClass.GPU,
            state=WorkState.SUCCESS,
            duration_seconds=2.0,
            output_units=24.0,
            accepted=True,
            repair_round=1,
        )
    )
    health = manager.health()
    assert health.execution_cost["render_samples"] == 2
    assert health.economics["first_pass_yield"] == 0.0
    assert health.economics["repair_success_rate"] == 1.0
    assert health.economics["gpu_waste_ratio"] == 0.6
