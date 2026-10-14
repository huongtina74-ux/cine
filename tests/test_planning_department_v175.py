from __future__ import annotations

from types import SimpleNamespace

from cinefactory.studio.company import stage_blueprint
from cinefactory.studio.company_handlers import FilmCompanyHandlers
from cinefactory.studio.contracts import (
    CapabilityKind,
    MediaFormat,
    MediaProductSpec,
    MediaPurpose,
    PlanningInputKind,
    PlanningInputRef,
    StudioProjectSpec,
)
from cinefactory.studio.defaults import build_default_capability_registry
from cinefactory.studio.intelligence import ObservationType
from cinefactory.studio.planning import (
    PlanningDepartment,
    PlanningMode,
    SceneToolPlanner,
)


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
    def __init__(self, qualified: set[str] | None = None) -> None:
        self.qualified = set(qualified or set())

    def decision(self, tool_id: str):
        if tool_id not in self.qualified:
            raise KeyError(tool_id)
        return SimpleNamespace(qualified=True)


def _kernel(
    tmp_path,
    *,
    available: set[str],
    mastered: set[str],
    qualified: set[str] | None = None,
):
    return SimpleNamespace(
        root=tmp_path,
        capabilities=build_default_capability_registry(tmp_path),
        tool_adapters=_Adapters(available),
        execution_mastery=_Mastery(mastered),
        production_qualification=_Qualification(qualified),
    )


def _animation_strategy() -> tuple[StudioProjectSpec, MediaProductSpec]:
    project = StudioProjectSpec(
        prompt="Create an original Roblox animated cinematic story",
        domain="gaming.roblox",
        niche="roblox animation",
        duration_seconds=600,
    )
    product = MediaProductSpec(
        purpose=MediaPurpose.ENTERTAIN,
        format=MediaFormat.ANIMATION,
        story_required=True,
        source_modalities=["3d", "voice", "editorial"],
        constraints={"domain": "gaming.roblox"},
    )
    return project, product


def test_company_has_explicit_planning_stage_before_writing():
    stages = stage_blueprint(
        MediaFormat.ANIMATION,
        evidence_required=False,
    )
    ids = [stage.stage_id for stage in stages]
    assert ids.index("CREATIVE_STRATEGY") < ids.index("PLANNING")
    assert ids.index("PLANNING") < ids.index("WRITING")

    planning = next(
        stage for stage in stages
        if stage.stage_id == "PLANNING"
    )
    assert "competitor_profiles" in planning.artifacts_in
    assert "production_strategy" in planning.artifacts_out

    technical = next(
        stage for stage in stages
        if stage.stage_id == "TECHNICAL_DIRECTION"
    )
    assert "production_handoff" in technical.artifacts_out
    assert "scene_tool_plan" in technical.artifacts_out


def test_competitor_input_promotes_patterns_not_raw_expression():
    project, product = _animation_strategy()
    project.planning_inputs = [
        PlanningInputRef(
            input_id="PIN_COMP_1",
            kind=PlanningInputKind.COMPETITOR_VIDEO,
            uri="https://example.invalid/video",
            metadata={
                "patterns": [
                    "hook immediately with a visible problem",
                    "protect reaction shots after the reveal",
                ],
                "production_patterns": [
                    "reuse persistent character rigs across episodes"
                ],
                "raw_transcript": "DO NOT COPY THIS COMPETITOR DIALOGUE",
                "exact_shot_order": ["A", "B", "C"],
                "confidence": 0.9,
            },
        ),
        PlanningInputRef(
            input_id="PIN_CHANNEL_1",
            kind=PlanningInputKind.CHANNEL_RESEARCH,
            metadata={
                "patterns": [
                    "recurring episodic conflict with a clear payoff"
                ]
            },
        ),
    ]

    strategy = PlanningDepartment().compile(
        project=project,
        product=product,
        research_pack={},
        competitor_profiles=[
            {
                "profile_id": "COMP_RESEARCH",
                "retention_patterns": [
                    "new visual or story information enters before long dead zones"
                ],
                "raw_script": "COPYRIGHTED STORY EXPRESSION",
                "confidence": 0.8,
            }
        ],
    )
    serialized = strategy.model_dump_json()

    assert strategy.planning_mode is PlanningMode.CINEMATIC_3D
    assert any(
        "visible problem" in item.abstraction
        for item in strategy.reference_patterns
    )
    assert any(
        "dead zones" in item.abstraction
        for item in strategy.reference_patterns
    )
    assert "DO NOT COPY THIS COMPETITOR DIALOGUE" not in serialized
    assert "COPYRIGHTED STORY EXPRESSION" not in serialized
    assert all(
        item.copying_prohibited
        for item in strategy.reference_patterns
    )
    assert any(
        "do not reuse competitor dialogue" in rule
        for rule in strategy.originality_boundaries
    )


def test_planner_tracks_ideal_editor_but_selects_proven_local_backend(
    tmp_path,
):
    project, product = _animation_strategy()
    strategy = PlanningDepartment().compile(
        project=project,
        product=product,
    )
    planner = SceneToolPlanner(
        _kernel(
            tmp_path,
            available={"blender", "ffmpeg"},
            mastered={"blender", "ffmpeg"},
        )
    )

    visual = planner.assign(
        CapabilityKind.OFFLINE_3D,
        strategy,
    )
    editorial = planner.assign(
        CapabilityKind.EDITORIAL,
        strategy,
    )

    assert visual.execution_ready is True
    assert visual.selected_tool_id == "blender"
    assert editorial.execution_ready is True
    assert editorial.selected_tool_id == "ffmpeg"
    assert editorial.ideal_capability_id in {
        "premiere.editorial",
        "resolve.editorial",
    }
    assert editorial.selected_capability_id == "ffmpeg.editorial"
    assert any(
        reason.startswith("fallback_selected=")
        for reason in editorial.reasons
    )


def test_scene_handoff_routes_per_scene_and_keeps_fallback_policy(
    tmp_path,
):
    project, product = _animation_strategy()
    strategy = PlanningDepartment().compile(
        project=project,
        product=product,
    )
    planner = SceneToolPlanner(
        _kernel(
            tmp_path,
            available={"blender", "ffmpeg"},
            mastered={"blender", "ffmpeg"},
        )
    )
    shots = [
        SimpleNamespace(
            scene_id="SC_001",
            shot_id="SH_001",
            narrative_purpose="hook",
        ),
        SimpleNamespace(
            scene_id="SC_001",
            shot_id="SH_002",
            narrative_purpose="reaction",
        ),
        SimpleNamespace(
            scene_id="SC_002",
            shot_id="SH_003",
            narrative_purpose="escalation",
        ),
    ]

    handoff = planner.compile_handoff(
        project_id=project.studio_project_id,
        strategy=strategy,
        shots=shots,
    )

    assert handoff.executable is True
    assert len(handoff.scene_plans) == 2
    assert handoff.scene_plans[0].shot_ids == ["SH_001", "SH_002"]
    assert "blender" in handoff.selected_tool_ids
    assert "ffmpeg" in handoff.selected_tool_ids
    assert any(
        "real gameplay" in rule
        for rule in handoff.fallback_policy
    )


def test_authentic_gameplay_fails_closed_without_game_runtime(tmp_path):
    project = StudioProjectSpec(
        prompt="Roblox gameplay survival challenge with real gameplay",
        domain="gaming.roblox",
    )
    product = MediaProductSpec(
        purpose=MediaPurpose.ENTERTAIN,
        format=MediaFormat.GAMEPLAY,
        actual_gameplay_required=True,
        source_modalities=["game_runtime", "editorial"],
        constraints={"domain": "gaming.roblox"},
    )
    strategy = PlanningDepartment().compile(
        project=project,
        product=product,
    )
    assert strategy.planning_mode is PlanningMode.AUTHENTIC_GAMEPLAY

    planner = SceneToolPlanner(
        _kernel(
            tmp_path,
            available={"blender", "ffmpeg"},
            mastered={"blender", "ffmpeg"},
        )
    )
    handoff = planner.compile_handoff(
        project_id=project.studio_project_id,
        strategy=strategy,
        shots=[
            SimpleNamespace(
                scene_id="SC_GAME",
                shot_id="SH_GAME",
                narrative_purpose="survive the obstacle",
            )
        ],
    )

    assert handoff.executable is False
    game_assignment = handoff.scene_plans[0].assignments[0]
    assert game_assignment.capability_kind is CapabilityKind.GAME_RUNTIME
    assert game_assignment.selected_capability_id is None
    assert any(
        "NO_VALIDATED_COMMERCIAL_RUNTIME:GAME_RUNTIME" in blocker
        for blocker in handoff.blockers
    )
    assert "blender" not in [
        item.selected_tool_id
        for item in handoff.scene_plans[0].assignments
        if item.selected_tool_id
    ]


def test_comfyui_image_mastery_does_not_imply_video_readiness(tmp_path):
    models = tmp_path / "models"
    workflows = tmp_path / "workflows" / "comfyui"
    models.mkdir(parents=True)
    workflows.mkdir(parents=True)

    (models / "registry.yaml").write_text(
        """models:
  - model_id: image-model
    revision: rev-image
    modality: image
    commercial_use_reviewed: true
    output_terms_reviewed: true
    approved_for_production: true
""",
        encoding="utf-8",
    )
    (workflows / "image.json").write_text("{}", encoding="utf-8")
    (workflows / "image.manifest.yaml").write_text(
        """workflow_id: image.ready
version: "1"
executor_id: local.comfyui
media_type: image
model_id: image-model
model_revision: rev-image
workflow_file: image.json
local_only: true
""",
        encoding="utf-8",
    )

    kernel = _kernel(
        tmp_path,
        available={"comfyui"},
        mastered={"comfyui"},
    )
    planner = SceneToolPlanner(kernel)

    assert planner._capability_binding_ready(
        "comfyui",
        CapabilityKind.AI_IMAGE,
    ) is True
    assert planner._capability_binding_ready(
        "comfyui",
        CapabilityKind.AI_VIDEO,
    ) is False


def test_research_signals_can_route_different_scenes_to_different_tools(
    tmp_path,
):
    models = tmp_path / "models"
    workflows = tmp_path / "workflows" / "comfyui"
    models.mkdir(parents=True)
    workflows.mkdir(parents=True)
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

    project, product = _animation_strategy()
    project.planning_inputs = [
        PlanningInputRef(
            input_id="PIN_METHOD",
            kind=PlanningInputKind.CHANNEL_RESEARCH,
            metadata={
                "production_patterns": [
                    "use generative video for surreal dream montage transitions"
                ]
            },
        )
    ]
    strategy = PlanningDepartment().compile(
        project=project,
        product=product,
        niche_playbook={
            "patterns": [
                {
                    "pattern_id": "PAT_AI_VIDEO",
                    "abstraction": (
                        "use generative video for surreal dream montage transitions"
                    ),
                    "observation_kind": ObservationType.PRODUCTION_METHOD.value,
                    "sample_video_ids": ["V1", "V2", "V3"],
                    "support_count": 3,
                    "sample_count": 4,
                    "confidence": 0.8,
                }
            ]
        },
        research_confidence={
            "score": 0.72,
            "grade": "MEDIUM",
            "decision_ready": True,
        },
    )
    assert CapabilityKind.AI_VIDEO in strategy.observed_capability_signals
    assert strategy.research_decision_ready is True

    planner = SceneToolPlanner(
        _kernel(
            tmp_path,
            available={"blender", "comfyui", "ffmpeg"},
            mastered={"blender", "comfyui", "ffmpeg"},
            qualified={"comfyui"},
        )
    )
    shots = [
        SimpleNamespace(
            scene_id="SC_DIALOGUE",
            shot_id="SH_DIALOGUE",
            narrative_purpose="character confrontation and reaction",
            audience_endpoint="understand the character decision",
            edit_intent="protect performance continuity",
            performance={"HERO": {"objective": "convince"}},
        ),
        SimpleNamespace(
            scene_id="SC_DREAM",
            shot_id="SH_DREAM",
            narrative_purpose="surreal dream montage transformation",
            audience_endpoint="feel an impossible visual transition",
            edit_intent="abstract montage",
            performance={},
        ),
    ]
    handoff = planner.compile_handoff(
        project_id=project.studio_project_id,
        strategy=strategy,
        shots=shots,
    )

    assert handoff.executable is True
    by_scene = {
        scene.scene_id: scene
        for scene in handoff.scene_plans
    }
    assert (
        by_scene["SC_DIALOGUE"].render_assignment.selected_tool_id
        == "blender"
    )
    assert (
        by_scene["SC_DREAM"].render_assignment.selected_tool_id
        == "comfyui"
    )
    assert CapabilityKind.AI_VIDEO in (
        by_scene["SC_DREAM"].render_candidate_kinds
    )

    groups, unresolved = FilmCompanyHandlers._visual_backend_groups(
        handoff,
        shots,
    )
    assert unresolved == []
    assert [shot.shot_id for shot in groups["blender"]] == [
        "SH_DIALOGUE"
    ]
    assert [shot.shot_id for shot in groups["comfyui"]] == [
        "SH_DREAM"
    ]


def test_single_source_production_signal_stays_hypothesis():
    project, product = _animation_strategy()
    project.planning_inputs = [
        PlanningInputRef(
            input_id="PIN_SINGLE",
            kind=PlanningInputKind.COMPETITOR_VIDEO,
            metadata={
                "production_patterns": [
                    "use generative video for surreal dream montage transitions"
                ],
                "confidence": 0.9,
            },
        )
    ]
    strategy = PlanningDepartment().compile(
        project=project,
        product=product,
        niche_playbook={"patterns": []},
        research_confidence={
            "score": 0.2,
            "grade": "LOW",
            "decision_ready": False,
        },
    )
    assert (
        CapabilityKind.AI_VIDEO
        in strategy.hypothesis_capability_signals
    )
    assert (
        CapabilityKind.AI_VIDEO
        not in strategy.observed_capability_signals
    )
    assert strategy.research_decision_ready is False
    hypothesis = [
        item
        for item in strategy.reference_patterns
        if "generative video" in item.abstraction
    ]
    assert hypothesis
    assert all(
        item.evidence_status != "CONFIRMED_PATTERN"
        for item in hypothesis
    )


def test_planning_prefers_portfolio_confirmed_patterns_and_carries_style_branches():
    project, product = _animation_strategy()
    project.planning_inputs = [
        PlanningInputRef(
            input_id="PIN_WEAK",
            kind=PlanningInputKind.COMPETITOR_VIDEO,
            metadata={
                "production_patterns": [
                    "uses screen recording demonstrations"
                ],
                "confidence": 0.95,
            },
        )
    ]
    portfolio = {
        "decision_ready": True,
        "confirmed_patterns": [
            {
                "pattern_id": "PAT_CROSS_AI",
                "abstraction": (
                    "uses generative video elements as a production method"
                ),
                "observation_kind": ObservationType.PRODUCTION_METHOD.value,
                "support_count": 3,
                "sample_count": 4,
                "confidence": 0.82,
                "tier": "CROSS_CHANNEL_CONFIRMED",
            }
        ],
        "style_branches": [
            {
                "axis": "editing_pace",
                "pattern_ids": ["PAT_FAST", "PAT_SLOW"],
                "poles": ["FAST", "SLOW"],
                "strength_scores": [0.7, 0.68],
                "interpretation": "two repeatable branches",
                "planning_rule": (
                    "select the branch matching the scene objective"
                ),
            }
        ],
    }
    strategy = PlanningDepartment().compile(
        project=project,
        product=product,
        niche_playbook={"patterns": []},
        research_confidence={
            "score": 0.8,
            "grade": "HIGH",
            "decision_ready": True,
        },
        research_portfolio=portfolio,
    )
    assert (
        CapabilityKind.AI_VIDEO
        in strategy.observed_capability_signals
    )
    assert (
        CapabilityKind.SCREEN_CAPTURE
        in strategy.hypothesis_capability_signals
    )
    assert strategy.research_decision_ready is True
    assert strategy.research_style_branches
    confirmed = [
        item
        for item in strategy.reference_patterns
        if item.source_id == "PAT_CROSS_AI"
    ]
    assert confirmed
    assert (
        confirmed[0].evidence_status
        == "CROSS_CHANNEL_CONFIRMED"
    )
