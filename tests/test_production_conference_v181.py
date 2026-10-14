from __future__ import annotations

from types import SimpleNamespace

from cinefactory.studio.capabilities import CapabilityRegistry
from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.company_handlers import FilmCompanyHandlers
from cinefactory.studio.company_runner import StageExecutionContext
from cinefactory.studio.contracts import (
    CapabilityKind,
    CapabilityOffer,
    MediaFormat,
    MediaProductSpec,
    MediaPurpose,
    PlanningInputKind,
    PlanningInputRef,
    StudioProjectSpec,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.planning import PlanningDepartment
from cinefactory.studio.production_conference import (
    ConferenceLane,
    ProductionConferenceRoom,
)
from cinefactory.studio.script_intelligence import ScriptInputCompiler


def _registry(*, gameplay_ready: bool = False) -> CapabilityRegistry:
    return CapabilityRegistry(
        [
            CapabilityOffer(
                capability_id="blender.local",
                kind=CapabilityKind.OFFLINE_3D,
                provider="Blender",
                executable=True,
                local=True,
                commercial_safe=True,
                deterministic=0.95,
                quality=0.86,
                speed=0.72,
            ),
            CapabilityOffer(
                capability_id="ffmpeg.editorial",
                kind=CapabilityKind.EDITORIAL,
                provider="FFmpeg",
                executable=True,
                local=True,
                commercial_safe=True,
                deterministic=1.0,
                quality=0.78,
                speed=0.96,
            ),
            CapabilityOffer(
                capability_id="game.runtime",
                kind=CapabilityKind.GAME_RUNTIME,
                provider="Game Runtime",
                executable=gameplay_ready,
                local=True,
                commercial_safe=True if gameplay_ready else None,
                deterministic=0.9,
                quality=0.9,
                speed=0.85,
                tags={"actual_gameplay"},
            ),
        ]
    )


def _animation_product() -> MediaProductSpec:
    return MediaProductSpec(
        purpose=MediaPurpose.ENTERTAIN,
        format=MediaFormat.ANIMATION,
        story_required=True,
        source_modalities=["3d", "voice", "editorial"],
        constraints={"domain": "gaming.roblox"},
    )


def _dialogue_script() -> str:
    return """ROBLOX ANIMATION

INT. CLASSROOM - DAY

MIA
We cannot leave him behind. We need to go back now.

JAY
If we go back, the whole plan changes.

MIA
Then the plan changes. I am not abandoning him.

JAY
Fine. I will cover the door while you get him.

EXT. SCHOOLYARD - DAY

MIA
Stay close to me.

JAY
I am right behind you.
"""


def test_quality_conference_wins_for_cinematic_performance_heavy_script(
    tmp_path,
):
    project = StudioProjectSpec(
        prompt=(
            "Create a professional cinematic 4K Roblox animation "
            "with high quality acting"
        ),
        domain="gaming.roblox",
        planning_inputs=[
            PlanningInputRef(
                kind=PlanningInputKind.SCRIPT,
                content=_dialogue_script(),
            )
        ],
    )
    pack = ScriptInputCompiler(tmp_path).compile(
        project.planning_inputs
    )
    strategy = PlanningDepartment().compile(
        project=project,
        product=_animation_product(),
        script_source_pack=pack,
    )
    decision = ProductionConferenceRoom().deliberate(
        kernel=SimpleNamespace(capabilities=_registry()),
        project=project,
        product=_animation_product(),
        strategy=strategy,
        script_pack=pack,
    )

    assert decision.executable is True
    assert len(decision.proposals) == 3
    assert len(decision.votes) == 21
    assert decision.selected_lane is ConferenceLane.QUALITY_FIRST
    applied = ProductionConferenceRoom.apply(strategy, decision)
    assert applied.conference_lane == "QUALITY_FIRST"
    assert applied.optimization_weights["quality"] == 0.58
    assert applied.conference_policy["candidate_multiplier"] == 1.5


def test_fast_lean_can_win_when_prompt_explicitly_values_speed_and_cost(
    tmp_path,
):
    project = StudioProjectSpec(
        prompt=(
            "Make this video fast, quick, free, low cost and tiết kiệm; "
            "prioritize tốc độ and miễn phí"
        ),
        domain="animation",
        planning_inputs=[
            PlanningInputRef(
                kind=PlanningInputKind.SCRIPT_OUTLINE,
                content="- Show the problem.\n- Show the solution.",
            )
        ],
    )
    pack = ScriptInputCompiler(tmp_path).compile(
        project.planning_inputs
    )
    strategy = PlanningDepartment().compile(
        project=project,
        product=_animation_product(),
        script_source_pack=pack,
    )
    decision = ProductionConferenceRoom().deliberate(
        kernel=SimpleNamespace(capabilities=_registry()),
        project=project,
        product=_animation_product(),
        strategy=strategy,
        script_pack=pack,
    )

    assert decision.executable is True
    assert decision.selected_lane is ConferenceLane.FAST_LEAN
    assert (
        decision.proposal_scores[
            f"{project.studio_project_id}:FAST"
        ]
        >
        decision.proposal_scores[
            f"{project.studio_project_id}:QUALITY"
        ]
    )


def test_authentic_gameplay_is_vetoed_without_game_runtime(tmp_path):
    project = StudioProjectSpec(
        prompt="Record authentic Roblox gameplay",
        domain="gaming.roblox",
    )
    product = MediaProductSpec(
        purpose=MediaPurpose.ENTERTAIN,
        format=MediaFormat.GAMEPLAY,
        story_required=False,
        actual_gameplay_required=True,
        source_modalities=["gameplay", "editorial"],
        constraints={"domain": "gaming.roblox"},
    )
    strategy = PlanningDepartment().compile(
        project=project,
        product=product,
    )
    decision = ProductionConferenceRoom().deliberate(
        kernel=SimpleNamespace(
            capabilities=_registry(gameplay_ready=False)
        ),
        project=project,
        product=product,
        strategy=strategy,
        script_pack=None,
    )

    assert decision.executable is False
    assert decision.selected_lane is None
    assert any(
        "MISSING_PRIMARY_CAPABILITIES" in item
        for item in decision.blockers
    )
    technical_votes = [
        vote
        for vote in decision.votes
        if vote.role.value == "TECHNICAL_DIRECTOR"
    ]
    assert technical_votes
    assert all(vote.veto for vote in technical_votes)


def test_company_planning_writes_conference_and_downstream_budget(tmp_path):
    studio = build_studio_kernel(tmp_path)
    runtime = SimpleNamespace(root=tmp_path, studio=studio)
    project = StudioProjectSpec(
        prompt=(
            "Create a professional cinematic Roblox animation "
            "from my script"
        ),
        domain="gaming.roblox",
        planning_inputs=[
            PlanningInputRef(
                kind=PlanningInputKind.SCRIPT,
                content=_dialogue_script(),
            )
        ],
    )
    blueprint = CompanyOrchestrator(studio).build_blueprint(project)
    handlers = FilmCompanyHandlers(runtime)
    registry = handlers.registry()

    planning_ctx = None
    for stage_id in (
        "INTELLIGENCE",
        "CREATIVE_STRATEGY",
        "PLANNING",
    ):
        stage = next(
            item
            for item in blueprint.stages
            if item.stage_id == stage_id
        )
        ctx = StageExecutionContext(
            blueprint=blueprint,
            stage=stage,
            kernel=runtime,
            project_root=tmp_path / "project",
        )
        result = registry.get(stage_id)(ctx)
        assert result.ok is True, result.error
        if stage_id == "PLANNING":
            planning_ctx = ctx

    assert planning_ctx is not None
    conference = studio.blackboard.get(
        project.studio_project_id,
        "production_conference",
    )["payload"]
    strategy = studio.blackboard.get(
        project.studio_project_id,
        "production_strategy",
    )["payload"]

    assert conference["selected_lane"] in {
        "QUALITY_FIRST",
        "BALANCED",
        "FAST_LEAN",
    }
    assert strategy["conference_lane"] == conference["selected_lane"]
    multiplier = strategy["conference_policy"]["candidate_multiplier"]
    expected = max(
        1,
        min(6, int(round(handlers.config.asset_candidates * multiplier))),
    )
    assert (
        handlers._conference_candidates(
            planning_ctx,
            handlers.config.asset_candidates,
        )
        == expected
    )
    assert (
        handlers._conference_qc_target(planning_ctx)
        >= handlers.config.min_visual_score
    )
