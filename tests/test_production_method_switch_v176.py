from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import (
    ActorPlacement,
    CameraIntent,
    EpisodeSpec,
    ShotPerformanceSpec,
    TransformSpec,
    Vec3,
)
from cinefactory.studio.capabilities import CapabilityRegistry
from cinefactory.studio.contracts import (
    CapabilityKind,
    CapabilityOffer,
)
from cinefactory.studio.production_method_switch import (
    DEFAULT_METHOD_SPECS,
    MethodSwitchPolicy,
    MethodSwitchRequest,
    MethodSwitchStatus,
    ProductionMethodSwitchController,
)
from cinefactory.turbo.contracts import (
    ExecutionCostSample,
    ResourceClass,
    WorkState,
)
from cinefactory.turbo.store import TurboStore


ROOT = Path(__file__).resolve().parents[1]


class _QualificationStore:
    def __init__(self, rows=None):
        self.rows = dict(rows or {})

    def decision(self, tool_id: str):
        if tool_id not in self.rows:
            raise KeyError(tool_id)
        return SimpleNamespace(qualified=self.rows[tool_id])


class _WorkflowRegistry:
    def __init__(self, rows=None):
        self.rows = list(rows or [])

    def list(self):
        return list(self.rows)


class _Models:
    def require_approved(self, model_id: str, revision: str):
        raise KeyError((model_id, revision))


def _ctx(tmp_path: Path):
    registry = CapabilityRegistry(
        offers=[
            CapabilityOffer(
                capability_id="blender.local",
                kind=CapabilityKind.OFFLINE_3D,
                provider="Blender",
                executable=True,
                local=True,
                commercial_safe=True,
                deterministic=0.92,
                quality=0.86,
                speed=0.72,
                vram_gb=12.0,
                tags={"camera_precision", "character_animation"},
            ),
            CapabilityOffer(
                capability_id="comfyui.local.video",
                kind=CapabilityKind.AI_VIDEO,
                provider="ComfyUI",
                executable=True,
                local=True,
                commercial_safe=None,
                deterministic=0.30,
                quality=0.72,
                speed=0.38,
                vram_gb=12.0,
            ),
            CapabilityOffer(
                capability_id="unreal.local",
                kind=CapabilityKind.REALTIME_3D,
                provider="Unreal",
                executable=False,
                local=True,
                commercial_safe=None,
                deterministic=0.90,
                quality=0.94,
                speed=0.72,
                vram_gb=8.0,
            ),
            CapabilityOffer(
                capability_id="minecraft.runtime",
                kind=CapabilityKind.GAME_RUNTIME,
                provider="Minecraft",
                executable=False,
                local=True,
                commercial_safe=None,
                deterministic=0.72,
                quality=0.92,
                speed=0.82,
                vram_gb=4.0,
            ),
            CapabilityOffer(
                capability_id="roblox.studio",
                kind=CapabilityKind.GAME_RUNTIME,
                provider="Roblox",
                executable=False,
                local=True,
                commercial_safe=None,
                deterministic=0.75,
                quality=0.91,
                speed=0.84,
                vram_gb=4.0,
            ),
        ]
    )
    return SimpleNamespace(
        root=tmp_path,
        studio=SimpleNamespace(
            capabilities=registry,
            production_qualification=_QualificationStore(
                {"comfyui": True}
            ),
        ),
        workflows=_WorkflowRegistry(),
        models=_Models(),
    )


def _request(**updates):
    values = dict(
        project_id="P1",
        episode_id="E1",
        shot_id="S01",
        current_tool_id="blender",
        current_method_id="blender.eevee.current",
        policy=MethodSwitchPolicy.QUALITY_FIRST_ALTERNATIVE,
        min_quality=0.92,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        max_additional_gpu_seconds=30.0,
        mean_current_attempt_seconds=4.0,
        continuity_priority=True,
        backend_switch_allowed=False,
        recurring_identity_required=True,
        visual_style="MINECRAFT",
        failure_codes=["LOOKDEV_FAIL"],
    )
    values.update(updates)
    return MethodSwitchRequest(**values)


def _compiled_shot():
    episode = EpisodeSpec(
        project_id="P_SWITCH",
        episode_id="E_SWITCH",
        title="switch",
        fps=24,
        width=320,
        height=180,
        quality_profile="preview",
        shots=[
            ShotPerformanceSpec(
                shot_id="S01",
                scene_template_id="minecraft_classroom",
                duration_seconds=1.0,
                actors=[
                    ActorPlacement(
                        actor_id="A",
                        rig_id="mc_a",
                        transform=TransformSpec(
                            location=Vec3(
                                x=0.0,
                                y=0.5,
                                z=0.0,
                            )
                        ),
                    )
                ],
                camera=CameraIntent(
                    purpose="fidelity_medium",
                    pattern_id="fidelity_medium",
                    targets=["A"],
                ),
                creative_intent={
                    "scene_id": "SC1",
                    "production_class": "HERO",
                },
            )
        ],
    )
    return EpisodeAssembler.from_root(ROOT).compile(
        episode
    ).shots[0]


def test_quality_first_selects_cycles_same_tool_method(tmp_path):
    controller = ProductionMethodSwitchController(
        _ctx(tmp_path)
    )
    decision = controller.deliberate(_request())
    assert decision.status is MethodSwitchStatus.SELECTED
    assert decision.executable is True
    assert decision.selected_method_id == "blender.cycles.quality"
    assert decision.selected_tool_id == "blender"
    selected = next(
        item
        for item in decision.assessments
        if item.method_id == "blender.cycles.quality"
    )
    assert selected.eligible is True
    assert "INCUMBENT_TOOL_TRUST_BOUNDARY" in selected.reasons


def test_comfy_video_is_not_execution_ready_without_video_workflow(tmp_path):
    controller = ProductionMethodSwitchController(
        _ctx(tmp_path)
    )
    spec = next(
        item
        for item in DEFAULT_METHOD_SPECS
        if item.method_id == "comfyui.video.production"
    )
    assessment = controller.assess(
        _request(
            current_tool_id="unreal",
            current_method_id="unreal.current",
            min_quality=0.70,
            recurring_identity_required=False,
            continuity_priority=False,
            backend_switch_allowed=True,
        ),
        spec,
    )
    assert assessment.eligible is False
    assert "VIDEO_WORKFLOW_MISSING" in assessment.blockers
    assert (
        "METHOD_COMMERCIAL_SAFETY_UNVERIFIED"
        in assessment.blockers
    )
    assert (
        "BLOCK_SHOT_NORMALIZATION_ADAPTER_MISSING"
        in assessment.blockers
    )


def test_no_eligible_method_creates_acquisition_request(tmp_path):
    controller = ProductionMethodSwitchController(
        _ctx(tmp_path)
    )
    decision = controller.deliberate(
        _request(
            max_additional_gpu_seconds=0.1,
        )
    )
    assert decision.executable is False
    assert decision.status in {
        MethodSwitchStatus.BLOCKED_ACQUISITION,
        MethodSwitchStatus.BLOCKED_POLICY,
    }
    assert decision.acquisition_request_path is not None
    path = Path(decision.acquisition_request_path)
    assert path.is_file()
    raw = path.read_text(encoding="utf-8")
    assert "METHOD_SWITCH_GPU_BUDGET_EXCEEDED" in raw
    assert "QUALIFIED_LOCAL_VIDEO_WORKFLOW" in raw


def test_cycles_transform_preserves_canonical_shot_and_changes_renderer(tmp_path):
    controller = ProductionMethodSwitchController(
        _ctx(tmp_path)
    )
    decision = controller.deliberate(_request())
    shot = _compiled_shot()
    before_camera = [
        item.model_dump(mode="json")
        for item in shot.camera_takes
    ]
    before_actors = [
        item.model_dump(mode="json")
        for item in shot.actors
    ]
    before_actions = [
        item.model_dump(mode="json")
        for item in shot.actions
    ]

    transformed = controller.transform_block_shot(
        shot,
        decision,
    )
    assert transformed.render_engine == "CYCLES"
    assert transformed.render_quality.engine == "CYCLES"
    assert (
        transformed.render_quality.profile_id
        == "auto_cycles_quality_recovery"
    )
    assert [
        item.model_dump(mode="json")
        for item in transformed.camera_takes
    ] == before_camera
    assert [
        item.model_dump(mode="json")
        for item in transformed.actors
    ] == before_actors
    assert [
        item.model_dump(mode="json")
        for item in transformed.actions
    ] == before_actions
    switch = transformed.creative_intent[
        "production_method_switch"
    ]
    assert switch["preserve_creative_intent"] is True
    assert switch["preserve_camera"] is True
    assert switch["preserve_animation"] is True


def test_cycles_switch_builds_durable_turbo_work_item(tmp_path):
    controller = ProductionMethodSwitchController(
        _ctx(tmp_path)
    )
    decision = controller.deliberate(_request())
    shot = controller.transform_block_shot(
        _compiled_shot(),
        decision,
    )
    compiled = SimpleNamespace(
        project_id="P1",
        episode_id="E1",
    )
    item = controller.build_work_item(
        compiled=compiled,
        shot=shot,
        decision=decision,
        output_path=tmp_path / "out.mp4",
        render_preview=True,
        switch_round=1,
        switch_of_work_id="W0",
        blender_executable="blender",
    )
    assert item.kind == "block.render.method_switch"
    assert item.handler == "blender.animation.render"
    assert item.resource is ResourceClass.GPU
    assert item.payload["method_switch"] is True
    assert item.payload["method_id"] == "blender.cycles.quality"
    assert item.payload["method_switch_of_work_id"] == "W0"
    assert item.payload["job"]["shot"]["render_engine"] == "CYCLES"


def test_execution_metrics_keep_repairs_and_method_switches_separate(tmp_path):
    store = TurboStore(tmp_path / "turbo.db")
    rows = [
        ExecutionCostSample(
            work_id="W0",
            project_id="P",
            worker_id="GPU",
            kind="block.render",
            resource=ResourceClass.GPU,
            state=WorkState.QC_REJECTED,
            duration_seconds=4.0,
            output_units=24.0,
            accepted=False,
            repair_round=0,
        ),
        ExecutionCostSample(
            work_id="W1",
            project_id="P",
            worker_id="GPU",
            kind="block.render.method_switch",
            resource=ResourceClass.GPU,
            state=WorkState.SUCCESS,
            duration_seconds=8.0,
            output_units=24.0,
            accepted=True,
            repair_round=1,
        ),
    ]
    for row in rows:
        store.add_execution_cost(row)

    summary = store.execution_cost_summary(project_id="P")
    assert summary["first_pass_samples"] == 1
    assert summary["first_pass_accepted"] == 0
    assert summary["repair_samples"] == 0
    assert summary["repair_successes"] == 0
    assert summary["method_switch_samples"] == 1
    assert summary["method_switch_successes"] == 1
    assert summary["method_switch_success_rate"] == pytest.approx(1.0)


def test_blocked_switch_builds_durable_agent_acquisition_work(tmp_path):
    controller = ProductionMethodSwitchController(
        _ctx(tmp_path)
    )
    decision = controller.deliberate(
        _request(max_additional_gpu_seconds=0.1)
    )
    assert decision.executable is False
    work = controller.build_acquisition_work_item(
        decision
    )
    assert work.kind == "rnd.capability.acquire"
    assert work.handler == "rnd.capability.acquire"
    assert work.resource is ResourceClass.AGENT
    assert work.max_attempts == 1
    assert Path(work.payload["request_path"]).is_file()
    assert "LICENSE_REVIEW" in work.payload["required_gates"]
    assert "SECURITY_REVIEW" in work.payload["required_gates"]
    assert "SANDBOX_BENCHMARK" in work.payload["required_gates"]
    assert "QUALITY_BENCHMARK" in work.payload["required_gates"]
    assert "PRODUCTION_QUALIFICATION" in work.payload["required_gates"]
    assert "OFFICIAL_DOCS" in work.payload["research_sources"]
    assert "GITHUB" in work.payload["research_sources"]
