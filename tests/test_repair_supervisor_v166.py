from __future__ import annotations

from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.company_runner import (
    AutonomousCompanyRunner,
    StageHandlerRegistry,
    StageHandlerResult,
)
from cinefactory.studio.contracts import StudioProjectSpec
from cinefactory.studio.execution import ExecutionLedgerStore, StageState
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.qc_department import QCLayer, StudioQCFinding
from cinefactory.studio.repair_supervisor import (
    AutonomousRepairSupervisor,
    RepairHandlerRegistry,
    RepairResult,
    run_with_repairs,
)


def _runner(tmp_path, handler):
    kernel = build_studio_kernel(tmp_path)
    blueprint = CompanyOrchestrator(kernel).build_blueprint(
        StudioProjectSpec(
            prompt="Create an original cinematic family story",
            duration_seconds=30,
        ),
        professional_governance=False,  # v166 repair harness
    )
    handlers = StageHandlerRegistry()
    handlers.register("INTELLIGENCE", handler)
    return AutonomousCompanyRunner(
        blueprint,
        handlers,
        store=ExecutionLedgerStore(tmp_path / "exec"),
        kernel=kernel,
    )


def test_supervisor_applies_registered_repair_then_retries_stage(tmp_path):
    state = {"broken": True}

    def intelligence(ctx):
        if state["broken"]:
            return StageHandlerResult(
                ok=False,
                qc_findings=[
                    StudioQCFinding(
                        code="TRANSIENT_SOURCE",
                        layer=QCLayer.TECHNICAL,
                        message="transient local source failure",
                    )
                ],
            )
        return StageHandlerResult(
            ok=True,
            produced_artifacts=ctx.stage.artifacts_out,
        )

    runner = _runner(tmp_path, intelligence)
    repairs = RepairHandlerRegistry()

    def repair(_ctx):
        state["broken"] = False
        return RepairResult(repaired=True, detail="reset transient source")

    repairs.register_code("TRANSIENT_SOURCE", repair)
    supervisor = AutonomousRepairSupervisor(repairs, max_rounds_per_stage=2)
    first = runner.tick()
    assert first.repair_tickets
    rr = supervisor.repair(runner, first.repair_tickets)
    assert rr.repaired == 1
    assert runner.engine.ledger.get("INTELLIGENCE").state is StageState.PENDING

    second = runner.tick()
    assert second.ran_stage_ids == ["INTELLIGENCE"]
    assert runner.engine.ledger.get("INTELLIGENCE").state is StageState.SUCCEEDED


def test_unknown_repair_stays_fail_closed(tmp_path):
    def intelligence(_ctx):
        return StageHandlerResult(
            ok=False,
            qc_findings=[
                StudioQCFinding(
                    code="UNKNOWN_DEFECT",
                    layer=QCLayer.TECHNICAL,
                    message="unknown",
                )
            ],
        )

    runner = _runner(tmp_path, intelligence)
    supervisor = AutonomousRepairSupervisor(RepairHandlerRegistry())
    first = runner.tick()
    rr = supervisor.repair(runner, first.repair_tickets)
    assert rr.repaired == 0
    assert rr.unresolved == [
        "INTELLIGENCE:UNKNOWN_DEFECT:NO_REPAIR_HANDLER"
    ]
    assert runner.engine.ledger.get("INTELLIGENCE").state is StageState.NEEDS_REPAIR


def test_run_with_repairs_stops_at_bounded_repair_limit(tmp_path):
    def intelligence(_ctx):
        return StageHandlerResult(
            ok=False,
            qc_findings=[
                StudioQCFinding(
                    code="ALWAYS_BAD",
                    layer=QCLayer.TECHNICAL,
                    message="still broken",
                )
            ],
        )

    runner = _runner(tmp_path, intelligence)
    registry = RepairHandlerRegistry()
    registry.register_code(
        "ALWAYS_BAD",
        lambda _ctx: RepairResult(repaired=True),
    )
    supervisor = AutonomousRepairSupervisor(
        registry,
        max_rounds_per_stage=1,
    )
    report = run_with_repairs(
        supervisor,
        runner,
        max_supervisor_rounds=4,
    )
    assert report.complete is False
    assert any("REPAIR_LIMIT" in item for item in report.unresolved)
