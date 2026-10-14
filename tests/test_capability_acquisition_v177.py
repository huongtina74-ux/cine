from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

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
from cinefactory.studio.capability_acquisition import (
    CapabilityAcquisitionState,
    CapabilityAcquisitionWorker,
    CapabilityResearchCandidate,
    CapabilityResearchResponse,
    ResearchEvidenceTier,
)
from cinefactory.studio.contracts import (
    CapabilityKind,
    CapabilityOffer,
)
from cinefactory.studio.capability_execution_lab import (
    BenchmarkDimension,
)
from cinefactory.studio.production_method_switch import (
    MethodSwitchPolicy,
    MethodSwitchRequest,
    ProductionMethodSwitchController,
)
from cinefactory.turbo.contracts import (
    ResourceClass,
    WorkerSpec,
    WorkState,
)
from cinefactory.turbo.daemon import FactoryDaemon
from cinefactory.turbo.store import TurboStore


ROOT = Path(__file__).resolve().parents[1]


class _QualificationStore:
    def __init__(self, rows=None):
        self.rows = dict(rows or {})

    def decision(self, tool_id: str):
        if tool_id not in self.rows:
            raise KeyError(tool_id)
        return SimpleNamespace(qualified=self.rows[tool_id])

    def list_decisions(self):
        return []


class _MasteryStore:
    def list(self):
        return []

    def get(self, tool_id: str):
        raise KeyError(tool_id)


class _ToolDoctor:
    def inspect(self, tool_id: str):
        return SimpleNamespace(
            installed=False,
            version=None,
            executable_path=None,
        )


class _ToolAdapters:
    def probe(self, kernel, tool_id: str):
        raise KeyError(tool_id)


class _Workflows:
    def list(self):
        return []


class _Models:
    def __init__(self):
        self.items = {}

    def require_approved(self, model_id: str, revision: str):
        raise KeyError((model_id, revision))


def _offers(blender_executable: bool) -> list[CapabilityOffer]:
    return [
        CapabilityOffer(
            capability_id="blender.local",
            kind=CapabilityKind.OFFLINE_3D,
            provider="Blender",
            executable=blender_executable,
            local=True,
            commercial_safe=True,
            deterministic=0.92,
            quality=0.86,
            speed=0.72,
            vram_gb=12.0,
        ),
        CapabilityOffer(
            capability_id="comfyui.local.video",
            kind=CapabilityKind.AI_VIDEO,
            provider="ComfyUI",
            executable=False,
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


def _ctx(tmp_path: Path, *, blender_executable: bool):
    registry = CapabilityRegistry(
        offers=_offers(blender_executable)
    )
    studio = SimpleNamespace(
        root=tmp_path,
        capabilities=registry,
        production_qualification=_QualificationStore(),
        execution_mastery=_MasteryStore(),
        tool_doctor=_ToolDoctor(),
        tool_adapters=_ToolAdapters(),
    )
    workflows = _Workflows()
    models = _Models()
    method_ctx = SimpleNamespace(
        root=tmp_path,
        studio=studio,
        workflows=workflows,
        models=models,
    )
    method_switch = ProductionMethodSwitchController(
        method_ctx
    )
    turbo_store = TurboStore(tmp_path / "turbo.db")
    ctx = SimpleNamespace(
        root=tmp_path,
        studio=studio,
        workflows=workflows,
        models=models,
        method_switch=method_switch,
        turbo_store=turbo_store,
    )
    return ctx


def _method_request(
    *,
    current_method_id: str = "blender.cycles.quality",
) -> MethodSwitchRequest:
    return MethodSwitchRequest(
        project_id="P177",
        episode_id="E177",
        shot_id="S01",
        current_tool_id="blender",
        current_method_id=current_method_id,
        policy=MethodSwitchPolicy.QUALITY_FIRST_ALTERNATIVE,
        min_quality=0.92,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        max_additional_gpu_seconds=60.0,
        mean_current_attempt_seconds=4.0,
        continuity_priority=True,
        backend_switch_allowed=False,
        recurring_identity_required=True,
        visual_style="MINECRAFT",
        failure_codes=["MODEL_CAPABILITY"],
    )


def _compiled_shot():
    episode = EpisodeSpec(
        project_id="P177",
        episode_id="E177",
        title="acquisition",
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


def _blocked_work(ctx, tmp_path: Path):
    request = _method_request()
    decision = ctx.method_switch.deliberate(request)
    assert decision.executable is False
    return ctx.method_switch.build_acquisition_work_item(
        decision,
        resume_context={},
    )


def test_rnd_agent_defers_without_burning_retry_budget(tmp_path):
    ctx = _ctx(tmp_path, blender_executable=True)
    ctx.capability_acquisition = CapabilityAcquisitionWorker(
        ctx,
        research_defer_seconds=30,
    )
    item = _blocked_work(ctx, tmp_path)
    ctx.turbo_store.enqueue_work(item)

    daemon = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="rnd-agent-test",
            resources={ResourceClass.AGENT},
            capabilities={"rnd.capability.acquire"},
        ),
        poll_seconds=0.01,
    )
    assert daemon.tick() is True

    updated = ctx.turbo_store.get_work(item.work_id)
    assert updated.state is WorkState.RETRY
    assert updated.attempts == 0
    assert updated.last_error == (
        "AWAITING_AGENT_RESEARCH_RESPONSE"
    )
    assert "_not_before_utc" in updated.payload
    assert (
        ctx.turbo_store.ready_work_count(
            daemon.worker
        )
        == 0
    )

    case_id = "P177__S01"
    request_path = (
        tmp_path
        / "data"
        / "studio"
        / "capability_acquisition"
        / "reasoning"
        / "requests"
        / f"{case_id}.json"
    )
    assert request_path.is_file()
    request = json.loads(
        request_path.read_text(encoding="utf-8")
    )
    assert request["stage"] == (
        "capability_acquisition_research"
    )
    assert request["context"]["constraints"][
        "metered_generation_api"
    ] is False


def test_research_lead_cannot_self_approve_without_local_evidence(tmp_path):
    ctx = _ctx(tmp_path, blender_executable=True)
    worker = CapabilityAcquisitionWorker(
        ctx,
        research_defer_seconds=5,
        qualification_defer_seconds=5,
    )
    ctx.capability_acquisition = worker
    item = _blocked_work(ctx, tmp_path)

    first = worker.process(item)
    assert first.state is (
        CapabilityAcquisitionState.AWAITING_RESEARCH
    )
    response_path = Path(first.response_path)
    response_path.parent.mkdir(parents=True, exist_ok=True)
    response = CapabilityResearchResponse(
        case_id=first.case_id,
        candidates=[
            CapabilityResearchCandidate(
                candidate_id="candidate.video.local",
                name="Candidate Local Video",
                tool_id="comfyui",
                method_id="comfyui.video.production",
                source_uri="https://example.invalid/repo",
                source_type="MAINTAINER_REPO",
                version="1",
                capabilities=["AI_VIDEO"],
                license_name="Apache-2.0",
                license_evidence_uri=(
                    "https://example.invalid/license"
                ),
                license_evidence_tier=(
                    ResearchEvidenceTier.OFFICIAL
                ),
                commercial_use_allowed=True,
                estimated_vram_gb=12.0,
                local_supported=True,
                automation_interfaces=["ComfyUI workflow"],
                evidence_refs=[
                    "official:model-card",
                    "maintainer:repo",
                ],
            )
        ],
        searched_sources=["OFFICIAL_DOCS", "GITHUB"],
    )
    response_path.write_text(
        response.model_dump_json(indent=2),
        encoding="utf-8",
    )

    second = worker.process(item)
    assert second.deferred is True
    assert second.completed is False
    assert second.state is (
        CapabilityAcquisitionState.SECURITY_REVIEW
    )
    assert "LOCAL_ARTIFACT_NOT_VERIFIED" in second.blockers
    assert "SECURITY_REVIEW_NOT_VERIFIED" in second.blockers
    assert "SANDBOX_NOT_PASSED" in second.blockers
    assert "BENCHMARK_NOT_PASSED" in second.blockers
    assert "ADAPTER_REGRESSION_NOT_PASSED" in second.blockers


def test_even_fully_evidenced_candidate_needs_method_binding(tmp_path):
    ctx = _ctx(tmp_path, blender_executable=True)
    worker = CapabilityAcquisitionWorker(
        ctx,
        research_defer_seconds=5,
        qualification_defer_seconds=5,
    )
    item = _blocked_work(ctx, tmp_path)
    first = worker.process(item)

    artifact = tmp_path / "candidate.bin"
    artifact.write_bytes(b"candidate")
    digest = hashlib.sha256(
        artifact.read_bytes()
    ).hexdigest()

    lab = worker.execution_lab
    provenance = lab.import_local_artifact(
        case_id=first.case_id,
        candidate_id="candidate.approved.unbound",
        source_path=artifact,
        source_uri="https://example.invalid/repo",
        source_type="MAINTAINER_REPO",
        version="1",
        expected_sha256=digest,
    )
    security = lab.static_security_scan(
        case_id=first.case_id,
        manifest=provenance,
    )
    sandbox = lab.sandbox_gate(
        case_id=first.case_id,
        candidate_id="candidate.approved.unbound",
        security=security,
        trusted_executor_id="test.sandbox",
        trusted_executor_passed=True,
    )
    benchmark = lab.benchmark_gate(
        case_id=first.case_id,
        candidate_id="candidate.approved.unbound",
        method_id="newtool.video",
        dimensions=[
            BenchmarkDimension(name="quality", score=0.95),
            BenchmarkDimension(name="identity", score=0.95),
            BenchmarkDimension(name="temporal", score=0.95),
            BenchmarkDimension(name="camera_contract", score=0.95),
            BenchmarkDimension(name="control", score=0.95),
        ],
    )
    adapter = lab.conformance_gate(
        case_id=first.case_id,
        candidate_id="candidate.approved.unbound",
        adapter_registered=True,
        handler_registered=True,
        normalization_passed=True,
        canonical_roundtrip_passed=True,
    )
    reports = {
        "sandbox": str(
            lab.store.report_path(
                first.case_id,
                "candidate.approved.unbound",
                "sandbox",
            )
        ),
        "benchmark": str(
            lab.store.report_path(
                first.case_id,
                "candidate.approved.unbound",
                "benchmark",
            )
        ),
        "adapter": str(
            lab.store.report_path(
                first.case_id,
                "candidate.approved.unbound",
                "conformance",
            )
        ),
    }
    assert sandbox.status.value == "PASS"
    assert benchmark.status.value == "PASS"
    assert adapter.status.value == "PASS"

    response = CapabilityResearchResponse(
        case_id=first.case_id,
        candidates=[
            CapabilityResearchCandidate(
                candidate_id="candidate.approved.unbound",
                name="Approved but Unbound Candidate",
                tool_id="newtool",
                method_id="newtool.video",
                source_uri="https://example.invalid/repo",
                source_type="MAINTAINER_REPO",
                version="1",
                capabilities=["AI_VIDEO"],
                license_name="Apache-2.0",
                license_evidence_uri=(
                    "https://example.invalid/license"
                ),
                license_evidence_tier=(
                    ResearchEvidenceTier.OFFICIAL
                ),
                commercial_use_allowed=True,
                estimated_vram_gb=8.0,
                local_supported=True,
                automation_interfaces=["CLI"],
                local_artifact_path=str(artifact),
                local_artifact_sha256=digest,
                security_evidence_refs=[
                    "local-static-scan:passed"
                ],
                sandbox_report_path=reports["sandbox"],
                benchmark_report_path=reports["benchmark"],
                adapter_regression_report_path=reports["adapter"],
            )
        ],
    )
    response_path = worker.store.research_response_path(
        first.case_id
    )
    response_path.write_text(
        response.model_dump_json(indent=2),
        encoding="utf-8",
    )

    outcome = worker.process(item)
    assert outcome.deferred is True
    assert outcome.state is CapabilityAcquisitionState.ADAPTER
    assert "CONFORMANCE:FAIL" in outcome.blockers
    assert "ADAPTER_REGRESSION_NOT_PASSED" in outcome.blockers


def test_worker_requeues_when_environment_gains_qualified_method(tmp_path):
    ctx = _ctx(tmp_path, blender_executable=False)
    request = _method_request(
        current_method_id="blender.eevee.current"
    )
    blocked = ctx.method_switch.deliberate(request)
    assert blocked.executable is False

    shot = _compiled_shot()
    item = ctx.method_switch.build_acquisition_work_item(
        blocked,
        resume_context={
            "shot": shot.model_dump(mode="json"),
            "output_path": str(
                tmp_path / "resumed.mp4"
            ),
            "render_preview": True,
            "switch_round": 1,
            "switch_of_work_id": "FAILED_RENDER",
            "blender_executable": "blender",
        },
    )

    # Simulate R&D/local environment change after the acquisition was
    # created: the canonical Blender capability becomes executable.
    ctx.studio.capabilities.register(
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
        )
    )

    worker = CapabilityAcquisitionWorker(ctx)
    outcome = worker.process(item)
    assert outcome.completed is True
    assert outcome.deferred is False
    assert outcome.state is CapabilityAcquisitionState.REQUEUED
    assert outcome.requeued_work_id is not None

    requeued = ctx.turbo_store.get_work(
        outcome.requeued_work_id
    )
    assert requeued.kind == "block.render.method_switch"
    assert requeued.handler == "blender.animation.render"
    assert requeued.payload["method_id"] == (
        "blender.cycles.quality"
    )
    assert requeued.payload["job"]["shot"][
        "render_engine"
    ] == "CYCLES"
    assert requeued.payload["method_switch_of_work_id"] == (
        "FAILED_RENDER"
    )
