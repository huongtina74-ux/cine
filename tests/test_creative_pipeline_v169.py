from __future__ import annotations

from cinefactory.autopilot.scaffold import LocalScaffoldPlanner
from cinefactory.domain.models import (
    ScriptScene,
    ScriptSpec,
    ShotSpecBatch,
    StoryBeat,
    StorySpec,
)
from cinefactory.studio.company import stage_blueprint
from cinefactory.studio.contracts import MediaFormat
from cinefactory.studio.creative_pipeline import (
    CinematographyBibleCompiler,
    CreativeReviewConference,
    DirectorTreatmentCompiler,
    LayoutTechvisCompiler,
    ScriptReviewer,
    StoryArchitectureCompiler,
    StoryboardAnimaticCompiler,
)
from cinefactory.studio.project_dna import ProjectDNA


def _ids(stages):
    return {stage.stage_id for stage in stages}


def test_minecraft_and_roblox_get_full_cinematic_preproduction():
    for niche in ("minecraft", "roblox_animation"):
        stages = stage_blueprint(
            MediaFormat.NARRATIVE_FILM,
            False,
            professional_governance=True,
            professional_niche=niche,
        )
        ids = _ids(stages)
        assert {
            "CREATIVE_DEVELOPMENT",
            "STORY_ARCHITECTURE",
            "SCRIPT_REVIEW",
            "DIRECTOR_TREATMENT",
            "STORYBOARD_EDITORIAL",
            "LAYOUT_TECHVIS",
            "CREATIVE_REVIEW",
        }.issubset(ids)


def test_audio_storytelling_gets_story_pipeline_without_visual_cinematic_extension():
    stages = stage_blueprint(
        MediaFormat.NARRATIVE_FILM,
        False,
        professional_governance=True,
        professional_niche="audio_storytelling_seniors",
    )
    ids = _ids(stages)
    assert "CREATIVE_DEVELOPMENT" in ids
    assert "STORY_ARCHITECTURE" in ids
    assert "SCRIPT_REVIEW" in ids
    assert "DIRECTOR_TREATMENT" in ids
    assert "STORYBOARD_EDITORIAL" not in ids
    assert "LAYOUT_TECHVIS" not in ids
    assert "CREATIVE_REVIEW" not in ids


def test_non_narrative_niches_are_not_forced_into_deep_film_pipeline():
    for niche in (
        "long_slices_game",
        "asmr_sleep_hands_objects",
        "fishing_silent",
        "rain_sleep_white_noise",
    ):
        stages = stage_blueprint(
            MediaFormat.NARRATIVE_FILM,
            False,
            professional_governance=True,
            professional_niche=niche,
        )
        ids = _ids(stages)
        assert "CREATIVE_DEVELOPMENT" in ids
        assert "STORY_ARCHITECTURE" not in ids
        assert "SCRIPT_REVIEW" not in ids
        assert "DIRECTOR_TREATMENT" not in ids
        assert "STORYBOARD_EDITORIAL" not in ids
        assert "LAYOUT_TECHVIS" not in ids
        assert "CREATIVE_REVIEW" not in ids


def test_legacy_stage_blueprint_remains_unchanged_by_professional_extensions():
    stages = stage_blueprint(
        MediaFormat.NARRATIVE_FILM,
        False,
        professional_governance=False,
    )
    ids = _ids(stages)
    assert "PROJECT_INTAKE" not in ids
    assert "CORPORATE_PREFLIGHT" not in ids
    assert "CREATIVE_DEVELOPMENT" not in ids
    assert "STORY_ARCHITECTURE" not in ids
    assert stages[0].stage_id == "INTELLIGENCE"


def test_story_script_director_storyboard_layout_chain_compiles():
    planner = LocalScaffoldPlanner()
    story = planner.story("A Minecraft hero must rescue a friend before the gate closes.")
    architecture = StoryArchitectureCompiler().compile("P1", story)

    script = planner.script(story)
    script_review = ScriptReviewer().review("P1", script, architecture)
    assert script_review.passed is True

    director = planner.director(script)
    dna = ProjectDNA(project_id="P1")
    treatment = DirectorTreatmentCompiler().compile(
        "P1",
        script,
        director,
        dna,
    )
    assert treatment.scenes

    shots = ShotSpecBatch(shots=planner.shots(script, director))
    storyboard, animatic = StoryboardAnimaticCompiler().compile("P1", shots)
    assert len(storyboard.panels) == len(shots.shots)
    assert len(animatic.beats) == len(shots.shots)
    assert animatic.total_duration_seconds == sum(
        shot.duration_seconds for shot in shots.shots
    )

    cinematography = CinematographyBibleCompiler().compile(
        "P1",
        shots,
        dna,
    )
    assert cinematography.scenes

    layout = LayoutTechvisCompiler().compile("P1", shots)
    assert layout.passed is True

    review = CreativeReviewConference().review(
        project_id="P1",
        script_review=script_review,
        storyboard=storyboard,
        animatic=animatic,
        cinematography=cinematography,
        layout_techvis=layout,
        previs_passed=True,
    )
    assert review.passed is True
    assert review.approved_for_technical_direction is True


def test_independent_script_review_blocks_unplayable_scene():
    story = StorySpec(
        title="Test",
        premise="A character must choose between two costly outcomes.",
        theme="choice",
        protagonist_goal="make the choice",
        central_conflict="both outcomes carry a cost",
        ending_state="the choice changes the character",
        beats=[
            StoryBeat(
                beat_id="B1",
                purpose="force decision",
                change="avoidance becomes commitment",
            )
        ],
    )
    architecture = StoryArchitectureCompiler().compile("P2", story)
    script = ScriptSpec(
        title="Test",
        logline="A difficult choice.",
        scenes=[
            ScriptScene(
                scene_id="SC1",
                heading="INT. ROOM - DAY",
                location_id="ROOM",
                time_of_day="DAY",
                dramatic_event="The choice arrives.",
                action=[],
                dialogue=[],
            )
        ],
    )
    review = ScriptReviewer().review("P2", script, architecture)
    assert review.passed is False
    assert any(issue.code == "SCENE_CONTENT_EMPTY" for issue in review.issues)


def test_layout_techvis_blocks_broken_shot_links():
    planner = LocalScaffoldPlanner()
    story = planner.story("A hero crosses a room to reveal a hidden threat.")
    script = planner.script(story)
    director = planner.director(script)
    source = planner.shots(script, director)
    broken = source[0].model_copy(update={"next_shot_id": "SH_DOES_NOT_EXIST"})
    batch = ShotSpecBatch(shots=[broken, *source[1:]])
    layout = LayoutTechvisCompiler().compile("P3", batch)
    assert layout.passed is False
    assert any("NEXT_SHOT_MISSING" in item for item in layout.findings)


def test_creative_review_blocks_when_previs_not_approved():
    planner = LocalScaffoldPlanner()
    story = planner.story("A hero discovers the truth.")
    architecture = StoryArchitectureCompiler().compile("P4", story)
    script = planner.script(story)
    script_review = ScriptReviewer().review("P4", script, architecture)
    director = planner.director(script)
    shots = ShotSpecBatch(shots=planner.shots(script, director))
    storyboard, animatic = StoryboardAnimaticCompiler().compile("P4", shots)
    cinematography = CinematographyBibleCompiler().compile(
        "P4",
        shots,
        ProjectDNA(project_id="P4"),
    )
    layout = LayoutTechvisCompiler().compile("P4", shots)

    review = CreativeReviewConference().review(
        project_id="P4",
        script_review=script_review,
        storyboard=storyboard,
        animatic=animatic,
        cinematography=cinematography,
        layout_techvis=layout,
        previs_passed=False,
    )
    assert review.passed is False
    assert "PREVIS_NOT_APPROVED" in review.blockers


def test_explicit_minecraft_professional_pipeline_reaches_creative_review(tmp_path):
    import shutil
    from pathlib import Path

    import pytest
    import yaml

    from cinefactory.appctx import build_context
    from cinefactory.studio.company import CompanyOrchestrator
    from cinefactory.studio.company_handlers import FilmCompanyHandlers, FilmHandlerConfig
    from cinefactory.studio.company_runner import (
        AutonomousCompanyRunner,
        StageHandlerResult,
    )
    from cinefactory.studio.contracts import StudioProjectSpec
    from cinefactory.studio.execution import StageState

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("ffmpeg required")

    src = Path(__file__).resolve().parents[1]
    shutil.copytree(src / "config", tmp_path / "config")
    shutil.copytree(src / "models", tmp_path / "models")
    shutil.copytree(src / "workflows", tmp_path / "workflows")

    niche = tmp_path / "config" / "niches" / "minecraft"
    payloads = {
        "research.yaml": {
            "audience_questions": ["why the viewer clicks and stays"],
            "competitor_questions": ["which story formats break out"],
            "trend_sources": ["youtube"],
            "production_forensics_questions": ["how strong videos are made"],
        },
        "competitors.yaml": {
            "channels": [{"channel_id": "C1"}],
            "breakout_channels": [{"channel_id": "C2"}],
        },
        "seo.yaml": {
            "keyword_clusters": {
                "minecraft_story": {
                    "intent": "entertainment",
                    "queries": ["minecraft story"],
                }
            },
            "search_intents": {"entertainment": ["minecraft story"]},
        },
        "production.yaml": {
            "recipes": {"narrative_animation": {"status": "validated"}},
            "approved_toolchains": {"offline_3d": ["blender"]},
        },
        "packaging_retention.yaml": {
            "title_patterns": ["clear character conflict"],
            "retention_baselines": {"opening_30s": "tracked"},
        },
        "risk_analytics.yaml": {
            "rights_and_policy": {"asset_license_required": True},
            "monetization": {"advertiser_safety_review": True},
            "analytics_baselines": {"retention": "tracked"},
        },
    }
    for filename, payload in payloads.items():
        (niche / filename).write_text(
            yaml.safe_dump(payload, sort_keys=False),
            encoding="utf-8",
        )

    blender = tmp_path / ".tools" / "blender-test" / "blender.exe"
    blender.parent.mkdir(parents=True, exist_ok=True)
    blender.write_bytes(b"capability-probe-only")

    runtime = build_context(tmp_path)
    project = StudioProjectSpec(
        # v207 requires explicit film source: "cinematic" may mean real
        # in-game machinima rather than authored Blender animation.
        prompt="Create an original animated Minecraft 3D cinematic story about rescuing a friend.",
        niche="minecraft",
        duration_seconds=12,
    )
    blueprint = CompanyOrchestrator(runtime.studio).build_blueprint(project)
    handlers = FilmCompanyHandlers(
        runtime,
        config=FilmHandlerConfig(
            production_mode="slate",
            asset_candidates=1,
            keyframe_candidates=1,
            pilot_count=1,
            render_width=320,
            render_height=180,
            master_width=320,
            master_height=180,
            fps=24,
        ),
    ).registry()
    if handlers.get("VOICE_PREP") is None:
        handlers.register(
            "VOICE_PREP",
            lambda ctx: StageHandlerResult(
                ok=True,
                produced_artifacts=list(ctx.stage.artifacts_out),
                checkpoint_ref="test://voice_prep_stub",
            ),
        )
    runner = AutonomousCompanyRunner(
        blueprint,
        handlers,
        store=runtime.studio.execution_ledgers,
        kernel=runtime,
        project_root=tmp_path / "data" / "projects" / project.studio_project_id,
    )
    report = runner.run_until_blocked_or_complete(max_cycles=60)

    required_success = [
        "PROJECT_INTAKE",
        "PORTFOLIO_GREENLIGHT",
        "INTELLIGENCE",
        "CORPORATE_PREFLIGHT",
        "CREATIVE_DEVELOPMENT",
        "CREATIVE_STRATEGY",
        "PLANNING",
        "STORY_ARCHITECTURE",
        "WRITING",
        "SCRIPT_REVIEW",
        "LOGIC",
        "DIRECTOR_TREATMENT",
        "DIRECTION",
        "PRODUCTION_DESIGN",
        "CINEMATOGRAPHY",
        "STORYBOARD_EDITORIAL",
        "CRAFT_EXECUTION_DESIGN",
        "ASSET_BUILD",
        "LAYOUT_TECHVIS",
        "PREVIS",
        "CREATIVE_REVIEW",
    ]
    for stage_id in required_success:
        assert report.ledger.get(stage_id).state is StageState.SUCCEEDED, (
            stage_id,
            report.errors,
        )

    approval = runtime.studio.blackboard.get(
        project.studio_project_id,
        "creative_review_approval",
    )["payload"]
    assert approval["passed"] is True
    assert approval["approved_for_technical_direction"] is True

    script_review = runtime.studio.blackboard.get(
        project.studio_project_id,
        "script_review",
    )["payload"]
    assert script_review["passed"] is True

    animatic = runtime.studio.blackboard.get(
        project.studio_project_id,
        "animatic_plan",
    )["payload"]
    assert animatic["total_duration_seconds"] > 0


def test_craft_execution_artifacts_exist_after_professional_e2e_contract():
    stages = stage_blueprint(
        MediaFormat.NARRATIVE_FILM,
        False,
        professional_governance=True,
        professional_niche="minecraft",
    )
    by_id = {stage.stage_id: stage for stage in stages}
    assert by_id["CRAFT_EXECUTION_DESIGN"].artifacts_out == [
        "creative_intent_graph",
        "camera_diagnostics",
        "performance_direction",
        "lighting_color_intent",
        "sound_spotting",
    ]
    assert "camera_diagnostics" in by_id["CREATIVE_REVIEW"].artifacts_in
    assert "sound_spotting" in by_id["AUDIO"].artifacts_in
    assert "lighting_color_intent" in by_id["FINISHING"].artifacts_in
