from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from cinefactory.appctx import build_context
from cinefactory.studio.company import CompanyOrchestrator, stage_blueprint
from cinefactory.studio.company_handlers import FilmCompanyHandlers, FilmHandlerConfig
from cinefactory.studio.company_runner import AutonomousCompanyRunner
from cinefactory.studio.contracts import MediaFormat, StudioProjectSpec
from cinefactory.studio.execution import StageState


def test_visual_company_blueprint_has_real_preproduction_departments():
    stages = stage_blueprint(MediaFormat.NARRATIVE, evidence_required=False)
    ids = [stage.stage_id for stage in stages]
    assert ids.index("PERFORMANCE") < ids.index("PRODUCTION")
    assert ids.index("PRODUCTION_DESIGN") < ids.index("ASSET_BUILD")
    assert ids.index("ASSET_BUILD") < ids.index("PREVIS")
    assert ids.index("PREVIS") < ids.index("PRODUCTION")
    voice = next(stage for stage in stages if stage.stage_id == "VOICE_PREP")
    assert voice.required is False


def test_animation_requires_voice_prep_before_production():
    stages = stage_blueprint(MediaFormat.ANIMATION, evidence_required=False)
    voice = next(stage for stage in stages if stage.stage_id == "VOICE_PREP")
    production = next(stage for stage in stages if stage.stage_id == "PRODUCTION")
    assert voice.required is True
    assert "dialogue_lock" in production.artifacts_in


@pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg required",
)
def test_local_company_handlers_complete_isolated_slate_film(tmp_path: Path):
    src = Path(__file__).resolve().parents[1]
    shutil.copytree(src / "config", tmp_path / "config")
    shutil.copytree(src / "models", tmp_path / "models")
    shutil.copytree(src / "workflows", tmp_path / "workflows")
    blender = tmp_path / ".tools" / "blender-test" / "blender.exe"
    blender.parent.mkdir(parents=True)
    blender.write_bytes(b"capability-probe-only")

    runtime = build_context(tmp_path)
    project = StudioProjectSpec(
        prompt="Create a wholly original cinematic family story about a difficult choice",
        duration_seconds=20,
    )
    blueprint = CompanyOrchestrator(runtime.studio).build_blueprint(project, professional_governance=False)
    assert blueprint.blockers == []

    config = FilmHandlerConfig(
        production_mode="slate",
        asset_candidates=1,
        keyframe_candidates=1,
        pilot_count=1,
        render_width=320,
        render_height=180,
        master_width=320,
        master_height=180,
        fps=24,
    )
    handlers = FilmCompanyHandlers(runtime, config=config).registry()
    project_root = tmp_path / "data" / "projects" / project.studio_project_id
    runner = AutonomousCompanyRunner(
        blueprint,
        handlers,
        store=runtime.studio.execution_ledgers,
        kernel=runtime,
        project_root=project_root,
    )
    report = runner.run_until_blocked_or_complete(max_cycles=40)

    assert report.complete is True, report.errors
    assert report.errors == []
    assert report.ledger.get("EVIDENCE").state is StageState.SKIPPED
    assert report.ledger.get("VOICE_PREP").state is StageState.SKIPPED
    assert report.ledger.get("ASSET_BUILD").state is StageState.SUCCEEDED
    assert report.ledger.get("PREVIS").state is StageState.SUCCEEDED
    assert report.ledger.get("PRODUCTION").state is StageState.SUCCEEDED
    assert report.ledger.get("FINAL_QC").state is StageState.SUCCEEDED

    approved = runtime.studio.blackboard.get(
        project.studio_project_id,
        "approved_master",
    )["payload"]
    assert Path(approved["path"]).is_file()

    strategy = runtime.studio.blackboard.get(
        project.studio_project_id,
        "production_strategy",
    )["payload"]
    assert strategy["planning_mode"] == "CINEMATIC_3D"

    scene_conference = runtime.studio.blackboard.get(
        project.studio_project_id,
        "scene_production_conference",
    )["payload"]
    assert scene_conference["scenes"]
    assert scene_conference["global_lane"] in {
        "QUALITY_FIRST",
        "BALANCED",
        "FAST_LEAN",
    }
    assert scene_conference["backend_switch_budget"] >= 0

    handoff = runtime.studio.blackboard.get(
        project.studio_project_id,
        "production_handoff",
    )["payload"]
    assert handoff["executable"] is True
    assert handoff["scene_plans"]
    assert all(
        scene["scene_conference_lane"] is not None
        for scene in handoff["scene_plans"]
    )
    assert any(
        policy.startswith("DIAGNOSTIC_ONLY:")
        for policy in handoff["fallback_policy"]
    )
    memory_advice = runtime.studio.blackboard.get(
        project.studio_project_id,
        "production_memory_advice",
    )["payload"]
    assert memory_advice["project_id"] == project.studio_project_id
    assert "advices" in memory_advice
    assert "adjusted_scene_ids" in memory_advice

    visual_models = runtime.studio.blackboard.get(
        project.studio_project_id,
        "visual_model_conference",
    )["payload"]
    assert "decisions" in visual_models

    format_dna = runtime.studio.blackboard.get(
        project.studio_project_id,
        "format_dna",
    )["payload"]
    assert format_dna["format_id"]
    assert format_dna["source_project_id"] == project.studio_project_id

    production_sheet = runtime.studio.blackboard.get(
        project.studio_project_id,
        "production_sheet",
    )["payload"]
    production_sheet_lock = runtime.studio.blackboard.get(
        project.studio_project_id,
        "production_sheet_lock",
    )["payload"]
    assert production_sheet["state"] == "LOCKED"
    assert production_sheet["sheet_hash"]
    assert (
        production_sheet_lock["sheet_hash"]
        == production_sheet["sheet_hash"]
    )

    spend_gate = runtime.studio.blackboard.get(
        project.studio_project_id,
        "spend_gate",
    )["payload"]
    assert spend_gate["approved"] is True

    human_spend_gate = runtime.studio.blackboard.get(
        project.studio_project_id,
        "human_spend_gate",
    )["payload"]
    assert human_spend_gate["state"] == "AUTO_APPROVED"

    human_final_gate = runtime.studio.blackboard.get(
        project.studio_project_id,
        "human_final_gate",
    )["payload"]
    assert human_final_gate["state"] == "AUTO_APPROVED"

    audio_execution = runtime.studio.blackboard.get(
        project.studio_project_id,
        "audio_execution_report",
    )["payload"]
    assert audio_execution["executed"] is True
    assert Path(audio_execution["output"]).is_file()

    backend = runtime.studio.blackboard.get(
        project.studio_project_id,
        "production_backend",
    )["payload"]
    assert backend["backend"] == "scene_dispatch"
    assert backend["routes"]
    assert all(
        route.get("scene_id")
        for route in backend["routes"]
    )
    assert all(
        route.get("scene_lane")
        for route in backend["routes"]
    )
    assert all(
        {
            "render_width",
            "render_height",
            "qc_target",
            "repair_budget",
            "pilot_count",
        }.issubset(route["execution_budget"])
        for route in backend["routes"]
    )
    assert all(
        "adaptations_triggered" in route
        for route in backend["routes"]
    )
    assert all(
        "production_memory_record" in route
        for route in backend["routes"]
    )
    adaptive = runtime.studio.blackboard.get(
        project.studio_project_id,
        "adaptive_production_report",
    )["payload"]
    assert len(adaptive["outcomes"]) == len(backend["routes"])
    assert backend["adaptive_production"]["outcome_count"] == len(
        adaptive["outcomes"]
    )
    assert backend["adaptive_production"]["adaptation_count"] == len(
        adaptive["changes"]
    )
    assert (
        "never change tool/backend class automatically"
        in adaptive["hard_constraints"]
    )
