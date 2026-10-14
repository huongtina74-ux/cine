from __future__ import annotations

import pytest
from pydantic import ValidationError

from cinefactory.studio.audio_department import (
    AudioCue,
    AudioPlan,
    AudioRole,
    DialogueLineTiming,
    DialogueLock,
    DialogueLockState,
    LipSyncPlanner,
)
from cinefactory.studio.color_department import ColorBible, ColorPlan
from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.contracts import DepartmentId, StudioProjectSpec
from cinefactory.studio.editorial import (
    EditDecision,
    EditDecisionGraph,
    EditReason,
)
from cinefactory.studio.execution import (
    CompanyExecutionEngine,
    ExecutionLedgerStore,
    StageState,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.post_pipeline import (
    PostProductionBundle,
    PostProductionCoordinator,
)
from cinefactory.studio.qc_department import QCLayer, StudioQCFinding


def _animation_blueprint(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    project = StudioProjectSpec(
        prompt="Create an animated cinematic short",
        duration_seconds=60,
    )
    return kernel, CompanyOrchestrator(kernel).build_blueprint(project, professional_governance=False)


def test_company_stage_engine_advances_by_artifact_dependencies(tmp_path):
    _, blueprint = _animation_blueprint(tmp_path)
    engine = CompanyExecutionEngine(blueprint)

    first = engine.schedule()
    assert first.ready_stage_ids == ["INTELLIGENCE"]

    engine.start("INTELLIGENCE")
    engine.succeed(
        "INTELLIGENCE",
        [
            "research_pack",
            "research_confidence",
            "research_portfolio",
            "competitor_profiles",
            "niche_playbook",
        ],
    )

    second = engine.schedule()
    assert "EVIDENCE" in second.ready_stage_ids
    engine.skip_optional("EVIDENCE")
    third = engine.schedule()
    assert "CREATIVE_STRATEGY" in third.ready_stage_ids


def test_company_stage_engine_rejects_missing_declared_outputs(tmp_path):
    _, blueprint = _animation_blueprint(tmp_path)
    engine = CompanyExecutionEngine(blueprint)
    engine.schedule()
    engine.start("INTELLIGENCE")
    with pytest.raises(ValueError, match="MISSING_STAGE_OUTPUTS"):
        engine.succeed("INTELLIGENCE", ["research_pack"])


def test_qc_findings_route_to_earliest_responsible_department(tmp_path):
    _, blueprint = _animation_blueprint(tmp_path)
    engine = CompanyExecutionEngine(blueprint)
    tickets = engine.route_qc_findings(
        "EDITORIAL",
        [
            StudioQCFinding(
                code="AUD_DIALOGUE_MASKED",
                layer=QCLayer.AUDIO,
                message="music masks dialogue",
            )
        ],
    )
    assert tickets[0].owner is DepartmentId.AUDIO
    assert engine.ledger.get("EDITORIAL").state is StageState.NEEDS_REPAIR


def test_execution_ledger_persists_and_resumes(tmp_path):
    kernel, blueprint = _animation_blueprint(tmp_path)
    engine = CompanyExecutionEngine(blueprint)
    engine.schedule()
    engine.start("INTELLIGENCE")
    store = ExecutionLedgerStore(tmp_path / "exec")
    store.save(engine.ledger)

    resumed = CompanyExecutionEngine(
        blueprint,
        ledger=store.load(blueprint.project.studio_project_id),
    )
    assert resumed.ledger.get("INTELLIGENCE").state is StageState.RUNNING
    assert resumed.ledger.get("INTELLIGENCE").attempts == 1
    assert hasattr(kernel, "execution_ledgers")


def test_dialogue_lock_requires_rendered_audio():
    with pytest.raises(ValidationError):
        DialogueLock(
            project_id="P1",
            state=DialogueLockState.LOCKED,
            lines=[
                DialogueLineTiming(
                    line_id="L1",
                    segment_id="S1",
                    speaker_id="HERO",
                    target_entity_id="HERO",
                    start_seconds=0,
                    duration_seconds=1,
                )
            ],
        )


def test_lipsync_planner_requires_locked_dialogue_and_capability():
    dialogue = DialogueLock(
        project_id="P1",
        state=DialogueLockState.LOCKED,
        lines=[
            DialogueLineTiming(
                line_id="L1",
                segment_id="S1",
                speaker_id="HERO",
                target_entity_id="HERO",
                start_seconds=0,
                duration_seconds=1,
                audio_ref="voice/L1.wav",
            )
        ],
    )
    blocked = LipSyncPlanner().plan(dialogue)
    assert blocked.blocked is True
    assert "LIPSYNC_CAPABILITY_UNAVAILABLE" in blocked.jobs[0].blockers

    ready = LipSyncPlanner().plan(
        dialogue,
        capability_id="local.lipsync",
        capability_executable=True,
    )
    assert ready.blocked is False
    assert ready.jobs[0].executable is True


def test_post_preflight_compiles_timeline_when_all_gates_pass():
    bundle = PostProductionBundle(
        project_id="P1",
        editorial=EditDecisionGraph(
            project_id="P1",
            decisions=[
                EditDecision(
                    decision_id="E1",
                    source_id="SRC1",
                    segment_id="SEG1",
                    source_out=2,
                    timeline_order=0,
                    reason=EditReason.INFORMATION,
                )
            ],
        ),
        audio=AudioPlan(project_id="P1"),
        color=ColorPlan(project_id="P1", bible=ColorBible()),
        media_paths={"SRC1": "clip.mp4"},
    )
    result = PostProductionCoordinator().preflight(bundle)
    assert result.executable is True
    assert result.timeline is not None
    assert result.findings == []


def test_post_preflight_turns_audio_failure_into_qc_finding():
    bundle = PostProductionBundle(
        project_id="P1",
        editorial=EditDecisionGraph(
            project_id="P1",
            decisions=[
                EditDecision(
                    decision_id="E1",
                    source_id="SRC1",
                    source_out=2,
                    timeline_order=0,
                    reason=EditReason.RHYTHM,
                )
            ],
        ),
        audio=AudioPlan(
            project_id="P1",
            cues=[
                AudioCue(
                    cue_id="M1",
                    role=AudioRole.MUSIC,
                    start_seconds=0,
                    purpose="tension",
                    duck_under_dialogue=False,
                )
            ],
        ),
        color=ColorPlan(project_id="P1", bible=ColorBible()),
        media_paths={"SRC1": "clip.mp4"},
    )
    result = PostProductionCoordinator().preflight(bundle)
    assert result.executable is False
    assert any(item.layer is QCLayer.AUDIO for item in result.findings)
