from __future__ import annotations

from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.company_runner import (
    AutonomousCompanyRunner,
    StageHandlerRegistry,
    StageHandlerResult,
)
from cinefactory.studio.contracts import DepartmentId, StudioProjectSpec
from cinefactory.studio.execution import ExecutionLedgerStore, StageState
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.qc_department import QCLayer, StudioQCFinding


def _setup(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    blueprint = CompanyOrchestrator(kernel).build_blueprint(
        StudioProjectSpec(
            prompt="Create an animated cinematic short",
            duration_seconds=60,
        ),
        professional_governance=False,  # v166 runner contract only
    )
    store = ExecutionLedgerStore(tmp_path / "execution")
    return kernel, blueprint, store


def _success(ctx):
    return StageHandlerResult(
        ok=True,
        produced_artifacts=ctx.stage.artifacts_out,
        checkpoint_ref=f"checkpoint://{ctx.stage.stage_id}",
    )


def test_runner_executes_handler_and_persists_checkpoint(tmp_path):
    kernel, blueprint, store = _setup(tmp_path)
    handlers = StageHandlerRegistry()
    handlers.register("INTELLIGENCE", _success)
    runner = AutonomousCompanyRunner(
        blueprint,
        handlers,
        store=store,
        kernel=kernel,
    )

    tick = runner.tick()
    assert tick.ran_stage_ids == ["INTELLIGENCE"]
    record = store.load(blueprint.project.studio_project_id).get("INTELLIGENCE")
    assert record.state is StageState.SUCCEEDED
    assert record.checkpoint_ref == "checkpoint://INTELLIGENCE"


def test_runner_auto_skips_optional_stage_without_handler(tmp_path):
    kernel, blueprint, store = _setup(tmp_path)
    handlers = StageHandlerRegistry()
    handlers.register("INTELLIGENCE", _success)
    runner = AutonomousCompanyRunner(
        blueprint,
        handlers,
        store=store,
        kernel=kernel,
    )

    runner.tick()
    second = runner.tick()
    assert second.skipped_stage_ids == ["EVIDENCE"]
    assert runner.engine.ledger.get("EVIDENCE").state is StageState.SKIPPED


def test_runner_blocks_required_stage_without_handler(tmp_path):
    kernel, blueprint, store = _setup(tmp_path)
    runner = AutonomousCompanyRunner(
        blueprint,
        StageHandlerRegistry(),
        store=store,
        kernel=kernel,
    )
    tick = runner.tick()
    assert tick.blocked_stage_ids == ["INTELLIGENCE"]
    record = runner.engine.ledger.get("INTELLIGENCE")
    assert record.state is StageState.BLOCKED
    assert record.error == "STAGE_HANDLER_MISSING"


def test_runner_routes_qc_findings_to_repair_ticket(tmp_path):
    kernel, blueprint, store = _setup(tmp_path)
    handlers = StageHandlerRegistry()

    def bad_audio(_ctx):
        return StageHandlerResult(
            ok=False,
            qc_findings=[
                StudioQCFinding(
                    code="AUD_001",
                    layer=QCLayer.AUDIO,
                    message="dialogue is masked",
                )
            ],
        )

    handlers.register("INTELLIGENCE", bad_audio)
    runner = AutonomousCompanyRunner(
        blueprint,
        handlers,
        store=store,
        kernel=kernel,
    )
    report = runner.run_until_blocked_or_complete()
    assert report.complete is False
    assert report.repair_tickets[0].owner is DepartmentId.AUDIO
    assert report.ledger.get("INTELLIGENCE").state is StageState.NEEDS_REPAIR


def test_runner_resume_uses_durable_ledger(tmp_path):
    kernel, blueprint, store = _setup(tmp_path)
    handlers = StageHandlerRegistry()
    handlers.register("INTELLIGENCE", _success)
    first = AutonomousCompanyRunner(
        blueprint,
        handlers,
        store=store,
        kernel=kernel,
    )
    first.tick()

    resumed = AutonomousCompanyRunner.resume(
        blueprint,
        handlers,
        store=store,
        kernel=kernel,
    )
    record = resumed.engine.ledger.get("INTELLIGENCE")
    assert record.state is StageState.SUCCEEDED
    assert record.attempts == 1
