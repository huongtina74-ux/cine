"""Reproduction tests for real cross-department wiring and production receipts."""
import json
import pytest
from typer.testing import CliRunner

from cinefactory.cli import app
from cinefactory.studio.artifact_receipts import verify_persisted_outputs
from cinefactory.studio.company import CompanyOrchestrator, CompanyStage, stage_blueprint
from cinefactory.studio.company_runner import (
    AutonomousCompanyRunner, StageHandlerRegistry, StageHandlerResult,
)
from cinefactory.studio.contract_integrity import audit_company_wiring
from cinefactory.studio.contracts import (
    ArtifactState, DepartmentId, MediaFormat, StudioProjectSpec,
)
from cinefactory.studio.execution import ExecutionLedgerStore, StageState
from cinefactory.studio.kernel import build_studio_kernel


def professional(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    project = StudioProjectSpec(
        prompt="Create original Minecraft cinematic animation",
        niche="minecraft",
        duration_seconds=60,
    )
    blueprint = CompanyOrchestrator(kernel).build_blueprint(
        project, professional_governance=True,
    )
    return kernel, blueprint


def test_unbound_stage_input_is_detected_even_when_old_dag_skips_it():
    report = audit_company_wiring([
        CompanyStage(
            stage_id="PRODUCTION", owner="PRODUCTION",
            artifacts_in=["NOT_SUPPLIED"],
            artifacts_out=["finished_scene"],
        )
    ])
    assert not report.valid
    assert "UNBOUND_INPUT:PRODUCTION:NOT_SUPPLIED" in report.blocker_codes()


def test_new_professional_project_enforces_global_governance_even_without_niche(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    blueprint = CompanyOrchestrator(kernel).build_blueprint(
        StudioProjectSpec(prompt="Original cinematic tale", duration_seconds=60),
        professional_governance=True,
    )
    assert blueprint.strict_stage_receipts
    assert {s.stage_id for s in blueprint.stages}.issuperset({
        "PROJECT_INTAKE", "PORTFOLIO_GREENLIGHT", "CORPORATE_PREFLIGHT",
    })
    assert not any(s.startswith("UNBOUND_INPUT:PLANNING:research_portfolio")
                   for s in blueprint.blockers)


def test_unbound_asrm_documentary_is_blocked_not_silently_executed(tmp_path):
    kernel, blueprint = professional(tmp_path)
    complete_stages = stage_blueprint(
        MediaFormat.DOCUMENTARY, False,
        professional_governance=True,
        professional_niche="asmr_sleep_hands_objects",
    )
    # The dedicated ASMR workflow is now complete; deliberately remove its
    # independent rights producer to prove the same guard still fails closed.
    broken_stages = [
        s for s in complete_stages
        if s.stage_id != "NICHE_RIGHTS_AND_SOURCES"
    ]
    broken = blueprint.model_copy(update={"stages": broken_stages})
    with pytest.raises(ValueError, match="COMPANY_STAGE_WIRING_BLOCKED"):
        AutonomousCompanyRunner(
            broken, StageHandlerRegistry(),
            store=ExecutionLedgerStore(tmp_path / "ledger"),
            kernel=kernel,
        )


def test_claimed_outputs_without_blackboard_are_not_accepted(tmp_path):
    kernel, blueprint = professional(tmp_path)
    handlers = StageHandlerRegistry()
    handlers.register("PROJECT_INTAKE", lambda ctx: StageHandlerResult(
        ok=True, produced_artifacts=ctx.stage.artifacts_out,
    ))
    runner = AutonomousCompanyRunner(
        blueprint, handlers,
        store=ExecutionLedgerStore(tmp_path / "execution"),
        kernel=kernel,
    )
    tick = runner.tick()
    assert any("STAGE_RECEIPTS_UNVERIFIED" in x for x in tick.errors)
    assert runner.engine.ledger.get("PROJECT_INTAKE").state is StageState.NEEDS_REPAIR


def test_hashed_persisted_output_is_accepted(tmp_path):
    kernel, blueprint = professional(tmp_path)
    project_id = blueprint.project.studio_project_id
    handlers = StageHandlerRegistry()

    def write(ctx):
        kernel.blackboard.put(
            project_id, "project_intake", DepartmentId.STUDIO_MANAGEMENT,
            {"accepted_scope": "local_3d_diagnostic_only"},
            state=ArtifactState.VALIDATED,
        )
        return StageHandlerResult(
            ok=True, produced_artifacts=list(ctx.stage.artifacts_out),
        )

    handlers.register("PROJECT_INTAKE", write)
    runner = AutonomousCompanyRunner(
        blueprint, handlers,
        store=ExecutionLedgerStore(tmp_path / "execution"),
        kernel=kernel,
    )
    tick = runner.tick()
    assert tick.errors == []
    assert runner.engine.ledger.get("PROJECT_INTAKE").state is StageState.SUCCEEDED
    assert verify_persisted_outputs(
        kernel.blackboard, project_id, blueprint.stages[0],
        ["project_intake"],
    ) == []


def test_company_plan_cli_niche_reaches_specialist_governance():
    # v207 requires explicit source truth: "cinematic" alone can describe
    # real in-game machinima or authored animation, so declare animation.
    result = CliRunner().invoke(app, [
        "company-plan", "--prompt", "Minecraft original animated cinematic episode",
        "--niche", "minecraft", "--duration", "60",
    ])
    assert result.exit_code == 0, result.output[-1200:]
    bp = json.loads(result.output)
    ids = {s["stage_id"] for s in bp["stages"]}
    assert bp["project"]["niche"] == "minecraft"
    assert bp["strict_stage_receipts"] is True
    assert {"SCRIPT_REVIEW", "CREATIVE_REVIEW", "PORTFOLIO_GREENLIGHT"} <= ids

def test_strict_slate_fails_before_final_master_can_be_auto_approved(tmp_path):
    from cinefactory.studio.company_handlers import FilmCompanyHandlers
    from cinefactory.studio.company_runner import StageExecutionContext

    kernel, blueprint = professional(tmp_path)
    qc_stage = next(s for s in blueprint.stages if s.stage_id == "FINAL_QC")
    # No master is present. The strict slate gate must reject prior to reading
    # any output, regardless of a default non-strict handler configuration.
    handler = FilmCompanyHandlers(kernel)
    result = handler.final_qc(StageExecutionContext(
        blueprint=blueprint, stage=qc_stage, kernel=kernel,
    ))
    assert not result.ok
    assert result.error == "DIAGNOSTIC_SLATE_NOT_PUBLISHABLE"


def test_missing_production_greenlight_is_not_render_permission(tmp_path):
    from cinefactory.studio.company_handlers import FilmCompanyHandlers
    from cinefactory.studio.company_runner import StageExecutionContext

    kernel, blueprint = professional(tmp_path)
    assert not blueprint.portfolio_greenlight.approved_for_production
    stage = next(s for s in blueprint.stages if s.stage_id == "PRODUCTION")
    result = FilmCompanyHandlers(kernel).production(StageExecutionContext(
        blueprint=blueprint, stage=stage, kernel=kernel,
    ))
    assert result.error == "NICHE_PRODUCTION_GREENLIGHT_REQUIRED"
