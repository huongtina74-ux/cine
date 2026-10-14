from __future__ import annotations

from types import SimpleNamespace

from cinefactory.domain.enums import ShotComplexity
from cinefactory.studio.contracts import (
    CapabilityKind,
    MediaFormat,
    MediaProductSpec,
    MediaPurpose,
    StudioProjectSpec,
)
from cinefactory.studio.company_handlers import (
    FilmCompanyHandlers,
    FilmHandlerConfig,
)
from cinefactory.studio.defaults import build_default_capability_registry
from cinefactory.studio.planning import PlanningDepartment, SceneToolPlanner
from cinefactory.studio.production_conference import (
    ConferenceLane,
    ProductionConferenceDecision,
    ProductionConferenceRoom,
)
from cinefactory.studio.scene_conference import (
    SceneProductionConference,
    SceneProductionObjective,
)


def _global_decision(
    project_id: str,
    lane: ConferenceLane,
) -> ProductionConferenceDecision:
    proposals = ProductionConferenceRoom.proposals(project_id)
    selected = next(item for item in proposals if item.lane is lane)
    return ProductionConferenceDecision(
        project_id=project_id,
        proposals=proposals,
        votes=[],
        selected_proposal_id=selected.proposal_id,
        selected_lane=selected.lane,
        selected_policy=selected.policy,
        proposal_scores={
            item.proposal_id: (
                0.9 if item.lane is lane else 0.7
            )
            for item in proposals
        },
        executable=True,
    )


def _shot(
    scene_id: str,
    shot_id: str,
    purpose: str,
    *,
    performance: bool = False,
    multi_actor: bool = False,
    complexity: ShotComplexity = ShotComplexity.GREEN,
    action_count: int = 0,
):
    actors = {}
    if performance:
        actors["HERO"] = {"objective": "act"}
    if multi_actor:
        actors["RIVAL"] = {"objective": "react"}
    return SimpleNamespace(
        scene_id=scene_id,
        shot_id=shot_id,
        narrative_purpose=purpose,
        audience_endpoint=purpose,
        edit_intent="preserve the dramatic beat",
        performance=actors,
        complexity=complexity,
        action_beats=[
            SimpleNamespace(action="move")
            for _ in range(action_count)
        ],
        duration_seconds=5.0,
        camera=SimpleNamespace(
            narrative_purpose=purpose,
            shot_size="MEDIUM",
        ),
    )


def test_performance_hero_scene_escalates_to_quality_even_under_fast_global():
    project_id = "STU_SCENE_QUALITY"
    report = SceneProductionConference().deliberate(
        project_id=project_id,
        shots=[
            _shot(
                "SC_HERO",
                "SH_1",
                "character confrontation and emotional reaction",
                performance=True,
                multi_actor=True,
                complexity=ShotComplexity.HERO,
                action_count=2,
            )
        ],
        global_decision=_global_decision(
            project_id,
            ConferenceLane.FAST_LEAN,
        ),
    )

    scene = report.scenes[0]
    assert scene.selected_lane is ConferenceLane.QUALITY_FIRST
    assert scene.metrics.continuity_risk >= 0.7
    assert scene.backend_switch_allowed is False
    assert scene.continuity_anchor is True


def test_simple_connective_scene_can_use_fast_lane():
    project_id = "STU_SCENE_FAST"
    report = SceneProductionConference().deliberate(
        project_id=project_id,
        shots=[
            _shot(
                "SC_BRIDGE",
                "SH_1",
                "brief connective transition to the next location",
            )
        ],
        global_decision=_global_decision(
            project_id,
            ConferenceLane.FAST_LEAN,
        ),
    )

    scene = report.scenes[0]
    assert scene.selected_lane is ConferenceLane.FAST_LEAN
    assert scene.metrics.continuity_risk < 0.4
    assert scene.production_objective is SceneProductionObjective.RETENTION_HOOK
    assert scene.optimization_bias["speed"] > 0


def test_dialogue_scene_gets_performance_continuity_directive():
    project_id = "STU_SCENE_DIALOGUE_DIRECTIVE"
    report = SceneProductionConference().deliberate(
        project_id=project_id,
        shots=[
            _shot("SC_HOOK", "SH_0", "open on the visible problem"),
            _shot(
                "SC_DIALOGUE",
                "SH_1",
                "two characters argue and react",
                performance=True,
                multi_actor=True,
                complexity=ShotComplexity.RED,
            ),
        ],
        global_decision=_global_decision(
            project_id,
            ConferenceLane.BALANCED,
        ),
    )

    scene = report.decision_for("SC_DIALOGUE")
    assert scene is not None
    assert scene.production_objective is SceneProductionObjective.PERFORMANCE_CONTINUITY
    assert CapabilityKind.OFFLINE_3D in scene.preferred_capability_kinds
    assert scene.optimization_bias["quality"] > 0


def test_low_risk_dream_montage_allows_renderer_class_switch():
    project_id = "STU_SCENE_DREAM"
    report = SceneProductionConference().deliberate(
        project_id=project_id,
        shots=[
            _shot(
                "SC_DREAM",
                "SH_1",
                "surreal dream montage with impossible transformation",
                complexity=ShotComplexity.YELLOW,
            )
        ],
        global_decision=_global_decision(
            project_id,
            ConferenceLane.BALANCED,
        ),
    )

    scene = report.scenes[0]
    assert scene.metrics.specialized_objective == "AI_VIDEO"
    assert scene.production_objective is SceneProductionObjective.GENERATIVE_MONTAGE
    assert CapabilityKind.AI_VIDEO in scene.preferred_capability_kinds
    assert scene.backend_switch_allowed is True
    assert report.backend_switch_budget == 1


def test_high_risk_dream_scene_keeps_continuity_anchor():
    project_id = "STU_SCENE_DREAM_ACTING"
    report = SceneProductionConference().deliberate(
        project_id=project_id,
        shots=[
            _shot(
                "SC_DREAM",
                "SH_1",
                "surreal dream montage during a two-character emotional confrontation",
                performance=True,
                multi_actor=True,
                complexity=ShotComplexity.HERO,
                action_count=3,
            )
        ],
        global_decision=_global_decision(
            project_id,
            ConferenceLane.BALANCED,
        ),
    )

    scene = report.scenes[0]
    assert scene.metrics.specialized_objective == "AI_VIDEO"
    assert scene.metrics.continuity_risk >= 0.72
    assert scene.backend_switch_allowed is False
    assert scene.continuity_anchor is True


class _Adapters:
    def __init__(self, available: set[str]) -> None:
        self.available = available

    def probe(self, kernel, tool_id: str):
        return SimpleNamespace(available=tool_id in self.available)


class _Mastery:
    def __init__(self, passed: set[str]) -> None:
        self.passed = passed

    def get(self, tool_id: str):
        if tool_id not in self.passed:
            raise KeyError(tool_id)
        return SimpleNamespace(passed=True, regression_passed=True)


class _Qualification:
    def __init__(self, qualified: set[str]) -> None:
        self.qualified = qualified

    def decision(self, tool_id: str):
        if tool_id not in self.qualified:
            raise KeyError(tool_id)
        return SimpleNamespace(qualified=True)


def _kernel(tmp_path):
    return SimpleNamespace(
        root=tmp_path,
        capabilities=build_default_capability_registry(tmp_path),
        tool_adapters=_Adapters({"blender", "comfyui", "ffmpeg"}),
        execution_mastery=_Mastery({"blender", "comfyui", "ffmpeg"}),
        production_qualification=_Qualification({"comfyui"}),
    )


def _enable_video_comfyui(tmp_path):
    models = tmp_path / "models"
    workflows = tmp_path / "workflows" / "comfyui"
    models.mkdir(parents=True, exist_ok=True)
    workflows.mkdir(parents=True, exist_ok=True)
    (models / "registry.yaml").write_text(
        """models:
  - model_id: video-model
    revision: rev-video
    modality: video
    commercial_use_reviewed: true
    output_terms_reviewed: true
    approved_for_production: true
""",
        encoding="utf-8",
    )
    (workflows / "video.json").write_text("{}", encoding="utf-8")
    (workflows / "video.manifest.yaml").write_text(
        """workflow_id: video.ready
version: "1"
executor_id: local.comfyui
media_type: video
model_id: video-model
model_revision: rev-video
workflow_file: video.json
local_only: true
""",
        encoding="utf-8",
    )


def test_tool_router_obeys_scene_switch_gate(tmp_path):
    _enable_video_comfyui(tmp_path)
    project = StudioProjectSpec(
        prompt="Create an original cinematic Roblox animation",
        domain="gaming.roblox",
    )
    product = MediaProductSpec(
        purpose=MediaPurpose.ENTERTAIN,
        format=MediaFormat.ANIMATION,
        story_required=True,
        source_modalities=["3d", "voice", "editorial"],
        constraints={"domain": "gaming.roblox"},
    )
    strategy = PlanningDepartment().compile(
        project=project,
        product=product,
        competitor_profiles=[
            {
                "profile_id": "RESEARCH",
                "production_patterns": [
                    "use generative video for surreal dream montage transitions"
                ],
                "confidence": 0.9,
            }
        ],
    )
    shots = [
        _shot(
            "SC_DIALOGUE",
            "SH_1",
            "character confrontation and reaction",
            performance=True,
            complexity=ShotComplexity.RED,
        ),
        _shot(
            "SC_DREAM",
            "SH_2",
            "surreal dream montage with impossible transformation",
            complexity=ShotComplexity.GREEN,
        ),
    ]
    global_decision = _global_decision(
        project.studio_project_id,
        ConferenceLane.BALANCED,
    )
    scene_report = SceneProductionConference().deliberate(
        project_id=project.studio_project_id,
        shots=shots,
        global_decision=global_decision,
    )
    policies = scene_report.policy_map()
    assert policies["SC_DREAM"]["backend_switch_allowed"] is True

    planner = SceneToolPlanner(_kernel(tmp_path))
    handoff = planner.compile_handoff(
        project_id=project.studio_project_id,
        strategy=strategy,
        shots=shots,
        scene_policies=policies,
    )
    by_scene = {
        item.scene_id: item
        for item in handoff.scene_plans
    }
    assert (
        by_scene["SC_DIALOGUE"].render_assignment.selected_tool_id
        == "blender"
    )
    assert (
        by_scene["SC_DREAM"].render_assignment.selected_tool_id
        == "comfyui"
    )

    locked_policies = {
        scene_id: dict(value)
        for scene_id, value in policies.items()
    }
    locked_policies["SC_DREAM"]["backend_switch_allowed"] = False
    handoff_locked = planner.compile_handoff(
        project_id=project.studio_project_id,
        strategy=strategy,
        shots=shots,
        scene_policies=locked_policies,
    )
    locked = {
        item.scene_id: item
        for item in handoff_locked.scene_plans
    }
    assert (
        locked["SC_DREAM"].render_assignment.selected_tool_id
        == "blender"
    )
    assert any(
        "continuity gate overrode" in note
        for note in locked["SC_DREAM"].notes
    )


def test_scene_execution_budget_differs_between_quality_and_fast(tmp_path):
    runtime = SimpleNamespace(
        root=tmp_path,
        studio=SimpleNamespace(root=tmp_path),
    )
    handlers = FilmCompanyHandlers(
        runtime,
        config=FilmHandlerConfig(
            render_width=1280,
            render_height=720,
            min_visual_score=0.70,
            max_repair_rounds=3,
            pilot_count=2,
        ),
    )
    proposals = ProductionConferenceRoom.proposals("STU_BUDGET")
    quality = next(
        item for item in proposals
        if item.lane is ConferenceLane.QUALITY_FIRST
    )
    fast = next(
        item for item in proposals
        if item.lane is ConferenceLane.FAST_LEAN
    )

    quality_budget = handlers._scene_batch_budget(
        {
            "scene_id": "SC_HERO",
            "scene_lane": quality.lane.value,
            "policy": quality.policy.model_dump(mode="json"),
        }
    )
    fast_budget = handlers._scene_batch_budget(
        {
            "scene_id": "SC_BRIDGE",
            "scene_lane": fast.lane.value,
            "policy": fast.policy.model_dump(mode="json"),
        }
    )

    assert quality_budget["render_width"] == 1280
    assert quality_budget["render_height"] == 720
    assert fast_budget["render_width"] < quality_budget["render_width"]
    assert fast_budget["render_height"] < quality_budget["render_height"]
    assert quality_budget["qc_target"] > fast_budget["qc_target"]
    assert quality_budget["repair_budget"] > fast_budget["repair_budget"]
    assert quality_budget["pilot_count"] > fast_budget["pilot_count"]


def test_hybrid_gameplay_scene_requires_game_runtime_and_never_falls_back_to_blender(tmp_path):
    project = StudioProjectSpec(
        prompt="Create an original hybrid Roblox story with one real gameplay segment",
        domain="gaming.roblox",
    )
    product = MediaProductSpec(
        purpose=MediaPurpose.ENTERTAIN,
        format=MediaFormat.ANIMATION,
        story_required=True,
        source_modalities=["3d", "voice", "editorial"],
        constraints={"domain": "gaming.roblox"},
    )
    strategy = PlanningDepartment().compile(project=project, product=product)
    shots = [
        _shot("SC_INTRO", "SH_0", "hook with a visible problem"),
        _shot("SC_GAME", "SH_1", "real gameplay playthrough inside the challenge"),
    ]
    global_decision = _global_decision(
        project.studio_project_id,
        ConferenceLane.BALANCED,
    )
    report = SceneProductionConference().deliberate(
        project_id=project.studio_project_id,
        shots=shots,
        global_decision=global_decision,
    )
    game = report.decision_for("SC_GAME")
    assert game is not None
    assert game.production_objective is SceneProductionObjective.AUTHENTIC_GAMEPLAY
    assert game.required_capability_kind is CapabilityKind.GAME_RUNTIME
    assert game.backend_switch_allowed is True

    planner = SceneToolPlanner(_kernel(tmp_path))
    handoff = planner.compile_handoff(
        project_id=project.studio_project_id,
        strategy=strategy,
        shots=shots,
        scene_policies=report.policy_map(),
    )
    game_plan = next(item for item in handoff.scene_plans if item.scene_id == "SC_GAME")
    assert game_plan.required_capability_kind is CapabilityKind.GAME_RUNTIME
    assert game_plan.render_candidate_kinds == [CapabilityKind.GAME_RUNTIME]
    assert game_plan.render_assignment is not None
    assert game_plan.render_assignment.capability_kind is CapabilityKind.GAME_RUNTIME
    assert game_plan.render_assignment.selected_tool_id != "blender"
    assert game_plan.executable is False
