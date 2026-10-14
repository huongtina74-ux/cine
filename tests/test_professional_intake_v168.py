from __future__ import annotations

from pathlib import Path

import yaml

from cinefactory.studio.company import CompanyOrchestrator, stage_blueprint
from cinefactory.studio.contracts import MediaFormat, StudioProjectSpec
from cinefactory.studio.intake import GreenlightState, ProjectIntakeEngine
from cinefactory.studio.kernel import build_studio_kernel


def _write_yaml(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _complete_minecraft_baseline(root: Path) -> None:
    base = root / "config" / "niches" / "minecraft"
    _write_yaml(
        base / "research.yaml",
        {
            "audience_questions": ["why viewers click and stay"],
            "competitor_questions": ["which formats break out"],
            "trend_sources": ["youtube"],
            "production_forensics_questions": ["how winning videos are produced"],
        },
    )
    _write_yaml(
        base / "competitors.yaml",
        {
            "channels": [{"channel_id": "C1"}],
            "breakout_channels": [{"channel_id": "C2"}],
        },
    )
    _write_yaml(
        base / "seo.yaml",
        {
            "keyword_clusters": {
                "minecraft_story": {
                    "intent": "entertainment",
                    "queries": ["minecraft story"],
                }
            },
            "search_intents": {"entertainment": ["minecraft story"]},
        },
    )
    _write_yaml(
        base / "production.yaml",
        {
            "recipes": {"narrative_animation": {"status": "validated"}},
            "approved_toolchains": {"offline_3d": ["blender"]},
        },
    )
    _write_yaml(
        base / "packaging_retention.yaml",
        {
            "title_patterns": ["clear conflict + character"],
            "retention_baselines": {"opening_30s": "tracked"},
        },
    )
    _write_yaml(
        base / "risk_analytics.yaml",
        {
            "rights_and_policy": {"asset_license_required": True},
            "monetization": {"advertiser_safety_review": True},
            "analytics_baselines": {"retention": "tracked"},
        },
    )


def test_unknown_explicit_niche_is_held(tmp_path):
    engine = ProjectIntakeEngine(tmp_path)
    project = StudioProjectSpec(
        prompt="Make a video",
        niche="unknown_niche",
        duration_seconds=60,
    )
    decision = engine.portfolio_greenlight(project)
    assert decision.state is GreenlightState.HOLD
    assert decision.approved_for_research is False
    assert "UNKNOWN_EXPLICIT_NICHE" in decision.blockers


def test_registered_explicit_niche_can_research_but_not_produce_when_baseline_missing(tmp_path):
    engine = ProjectIntakeEngine(tmp_path)
    project = StudioProjectSpec(
        prompt="Minecraft animated story",
        niche="minecraft",
        duration_seconds=60,
    )
    decision = engine.portfolio_greenlight(project)
    assert decision.state is GreenlightState.PROCEED_RESEARCH
    assert decision.approved_for_research is True
    assert decision.approved_for_production is False
    assert "SEO_DISCOVERY_BASELINE_MISSING" in decision.blockers
    assert "COMPETITOR_BASELINE_MISSING" in decision.blockers


def test_explicit_niche_greenlights_only_after_all_baselines_exist(tmp_path):
    _complete_minecraft_baseline(tmp_path)
    engine = ProjectIntakeEngine(tmp_path)
    project = StudioProjectSpec(
        prompt="Minecraft animated story",
        niche="minecraft",
        duration_seconds=60,
    )
    decision = engine.portfolio_greenlight(project)
    assert decision.state is GreenlightState.GREENLIGHT
    assert decision.approved_for_production is True
    assert decision.blockers == []

    preflight = engine.corporate_preflight(
        project,
        competitor_profiles=[{"video_id": "V1"}],
        research_pack={"promoted_pattern_count": 2},
    )
    assert preflight.approved is True
    assert preflight.seo_discovery_ready is True
    assert preflight.risk_ready is True


def test_inferred_niche_is_advisory_for_backward_compatibility(tmp_path):
    engine = ProjectIntakeEngine(tmp_path)
    project = StudioProjectSpec(
        prompt="Minecraft animated story",
        duration_seconds=60,
    )
    intake = engine.intake(project)
    decision = engine.portfolio_greenlight(project)
    assert intake.resolved_niche == "minecraft"
    assert intake.strict_niche_gate is False
    assert decision.approved_for_production is True
    assert "NICHE_INFERRED_ADVISORY_MODE" in decision.warnings


def test_company_blueprint_contains_real_intake_and_preflight_stages(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    blueprint = CompanyOrchestrator(kernel).build_blueprint(
        StudioProjectSpec(
            # Explicit original animation to avoid accidental real-game capture routing.
            prompt="Minecraft original 3D animated cinematic film",
            niche="minecraft",
            duration_seconds=60,
        )
    )
    ids = [stage.stage_id for stage in blueprint.stages]
    assert ids.index("PROJECT_INTAKE") < ids.index("PORTFOLIO_GREENLIGHT")
    assert ids.index("PORTFOLIO_GREENLIGHT") < ids.index("INTELLIGENCE")
    assert ids.index("INTELLIGENCE") < ids.index("CORPORATE_PREFLIGHT")
    assert ids.index("CORPORATE_PREFLIGHT") < ids.index("CREATIVE_STRATEGY")
    assert blueprint.project_intake is not None
    assert blueprint.portfolio_greenlight is not None


def test_explicit_niche_blueprint_exposes_research_only_state(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    blueprint = CompanyOrchestrator(kernel).build_blueprint(
        StudioProjectSpec(
            prompt="Minecraft animated story",
            niche="minecraft",
            duration_seconds=60,
        )
    )
    assert blueprint.portfolio_greenlight is not None
    assert blueprint.portfolio_greenlight.approved_for_research is True
    assert blueprint.portfolio_greenlight.approved_for_production is False

def test_explicit_niche_runner_stops_at_corporate_preflight_until_research_ready(tmp_path):
    from cinefactory.studio.company_handlers import FilmCompanyHandlers
    from cinefactory.studio.company_runner import AutonomousCompanyRunner
    from cinefactory.studio.execution import StageState

    kernel = build_studio_kernel(tmp_path)
    project = StudioProjectSpec(
        prompt="Minecraft animated story",
        niche="minecraft",
        duration_seconds=60,
    )
    blueprint = CompanyOrchestrator(kernel).build_blueprint(project)
    handlers = FilmCompanyHandlers(kernel).registry()
    runner = AutonomousCompanyRunner(
        blueprint,
        handlers,
        store=kernel.execution_ledgers,
        kernel=kernel,
        project_root=tmp_path / "data" / "projects" / project.studio_project_id,
    )
    report = runner.run_until_blocked_or_complete(max_cycles=10)
    assert report.complete is False
    assert report.ledger.get("PROJECT_INTAKE").state is StageState.SUCCEEDED
    assert report.ledger.get("PORTFOLIO_GREENLIGHT").state is StageState.SUCCEEDED
    assert report.ledger.get("INTELLIGENCE").state is StageState.SUCCEEDED
    assert report.ledger.get("CORPORATE_PREFLIGHT").state is StageState.NEEDS_REPAIR
    assert report.ledger.get("CREATIVE_STRATEGY").state in {
        StageState.PENDING,
        StageState.BLOCKED,
    }
    assert any("CORPORATE_PREFLIGHT_BLOCKED" in item for item in report.errors)
