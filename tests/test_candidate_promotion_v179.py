from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from cinefactory.domain.enums import NetworkScope
from cinefactory.executors.base import ExecutionResult
from cinefactory.studio.candidate_promotion import (
    BenchmarkMatrixReport,
    CandidateExecutionState,
    CandidatePromotionController,
    MultiShotBenchmarkMatrix,
    PromotionState,
    TrustedArtifactClass,
    TrustedCandidateLabExecutor,
)
from cinefactory.studio.capability_execution_lab import (
    CapabilityExecutionLab,
)
from cinefactory.workflows.registry import (
    WorkflowManifest,
    WorkflowRegistry,
)


class _Models:
    def require_approved(self, model_id: str, revision: str):
        if (
            model_id != "model.safe"
            or revision != "rev1"
        ):
            raise RuntimeError("not approved")
        return SimpleNamespace(
            model_id=model_id,
            revision=revision,
        )


class _FakeComfy:
    descriptor = SimpleNamespace(
        executor_id="local.comfyui",
        network_scope=NetworkScope.LOOPBACK_LAN,
    )

    def preflight(self, workflow):
        return SimpleNamespace(
            valid=True,
            workflow_sha256="workflow-hash",
            object_info_sha256="object-info-hash",
            findings=[],
        )

    def execute(self, payload):
        output = Path(payload["output_dir"])
        output.mkdir(parents=True, exist_ok=True)
        artifact = output / "candidate.png"
        artifact.write_bytes(b"fake-image")
        return ExecutionResult(
            ok=True,
            artifacts=[str(artifact)],
            metadata={"local": True},
        )


class _Executors:
    def __init__(self):
        self.comfy = _FakeComfy()

    def get(self, executor_id: str):
        if executor_id != "local.comfyui":
            raise KeyError(executor_id)
        return self.comfy


class _MethodSwitch:
    def __init__(self):
        self.specs = []
        self.registered_handlers = {
            "comfy.execute",
        }


def _ctx(tmp_path: Path):
    workflows = WorkflowRegistry(
        tmp_path / "workflows"
    ).load()
    lab = CapabilityExecutionLab(tmp_path)
    return SimpleNamespace(
        root=tmp_path,
        models=_Models(),
        executors=_Executors(),
        workflows=workflows,
        method_switch=_MethodSwitch(),
        capability_execution_lab=lab,
    )


def _workflow(tmp_path: Path) -> Path:
    path = tmp_path / "candidate_workflow.json"
    path.write_text(
        json.dumps(
            {
                "1": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {
                        "ckpt_name": "safe.safetensors",
                    },
                },
                "2": {
                    "class_type": "SaveImage",
                    "inputs": {
                        "filename_prefix": "safe",
                        "images": ["1", 0],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def _manifest() -> WorkflowManifest:
    return WorkflowManifest(
        workflow_id="candidate.safe.image",
        version="1",
        executor_id="local.comfyui",
        media_type="image",
        model_id="model.safe",
        model_revision="rev1",
        workflow_file="candidate_workflow.json",
        local_only=True,
    )


def _runtime_result(
    *,
    identity: float = 0.95,
    performance: float = 0.95,
):
    return {
        "qc_passed": True,
        "duration": 1.0,
        "visual_qc": {
            "passed": True,
            "black_seconds": 0.0,
            "freeze_seconds": 0.0,
        },
        "rendered_frame_qc": {"passed": True},
        "identity_qc": {
            "passed": True,
            "score": identity,
        },
        "performance_qc": {
            "passed": True,
            "score": performance,
        },
        "geometry_qc": {
            "passed": True,
            "targets": [{"blockers": []}],
        },
        "creative_intent_bound": True,
        "render_state": {
            "camera": {
                "start": {"lens_mm": 50.0},
                "end": {"lens_mm": 50.0},
            }
        },
    }


def test_classifier_blocks_python_and_native_code(tmp_path):
    ctx = _ctx(tmp_path)
    executor = TrustedCandidateLabExecutor(ctx)

    py = tmp_path / "plugin.py"
    py.write_text("print('x')", encoding="utf-8")
    exe = tmp_path / "plugin.exe"
    exe.write_bytes(b"MZ")

    py_result = executor.classify(py)
    exe_result = executor.classify(exe)

    assert py_result.artifact_class is (
        TrustedArtifactClass.PYTHON_CODE
    )
    assert exe_result.artifact_class is (
        TrustedArtifactClass.NATIVE_BINARY
    )
    assert py_result.auto_execution_allowed is False
    assert exe_result.auto_execution_allowed is False
    assert any(
        item.startswith("AUTO_EXECUTION_CLASS_BLOCKED")
        for item in py_result.findings
    )


def test_declarative_workflow_executes_only_through_trusted_local_executor(
    tmp_path,
):
    ctx = _ctx(tmp_path)
    executor = TrustedCandidateLabExecutor(ctx)
    workflow = _workflow(tmp_path)

    result = executor.execute_comfyui_workflow(
        candidate_id="safe",
        workflow_path=workflow,
        model_id="model.safe",
        model_revision="rev1",
        output_dir=tmp_path / "outputs",
        execute=True,
    )

    assert result.state is CandidateExecutionState.PASS
    assert result.preflight_passed is True
    assert result.execution_attempted is True
    assert result.execution_passed is True
    assert len(result.artifacts) == 1
    assert Path(result.artifacts[0]).is_file()
    assert result.metadata["public_network_allowed"] is False
    assert result.metadata["process_spawn_allowed"] is False


def test_multi_shot_matrix_requires_multiple_good_cases(tmp_path):
    lab = CapabilityExecutionLab(tmp_path)
    matrix = MultiShotBenchmarkMatrix(
        lab,
        required_cases=2,
        minimum_dimension_score=0.80,
    )

    passed = matrix.from_runtime_results(
        matrix_id="M1",
        candidate_id="cycles",
        method_id="blender.cycles.quality",
        runtime_results=[
            ("A", _runtime_result(identity=0.95)),
            ("B", _runtime_result(identity=0.91)),
        ],
    )
    assert passed.passed is True
    assert passed.dimension_minima["identity"] == 0.91

    failed = matrix.from_runtime_results(
        matrix_id="M2",
        candidate_id="cycles",
        method_id="blender.cycles.quality",
        runtime_results=[
            ("A", _runtime_result(identity=0.95)),
            ("B", _runtime_result(identity=0.60)),
        ],
    )
    assert failed.passed is False
    assert any(
        item.startswith(
            "BENCHMARK_DIMENSION_BELOW_FLOOR:identity"
        )
        for item in failed.blockers
    )


def test_rights_gate_blocks_automatic_registry_promotion(tmp_path):
    ctx = _ctx(tmp_path)
    controller = CandidatePromotionController(ctx)
    workflow = _workflow(tmp_path)

    result = controller.qualify_and_promote_comfyui_workflow(
        candidate_id="rights.blocked",
        workflow_path=workflow,
        manifest=_manifest(),
        source_uri="maintainer://repo",
        source_type="MAINTAINER_REPO",
        expected_sha256=controller._file_sha256(workflow),
        output_dir=tmp_path / "out",
        rights_cleared=False,
    )
    assert result.state is PromotionState.BLOCKED
    assert "COMMERCIAL_RIGHTS_NOT_CLEARED" in result.blockers
    assert ctx.workflows.list() == []


def test_safe_workflow_auto_qualifies_and_enters_registry(tmp_path):
    ctx = _ctx(tmp_path)
    controller = CandidatePromotionController(ctx)
    workflow = _workflow(tmp_path)

    result = controller.qualify_and_promote_comfyui_workflow(
        candidate_id="safe.auto",
        workflow_path=workflow,
        manifest=_manifest(),
        source_uri="maintainer://repo",
        source_type="MAINTAINER_REPO",
        expected_sha256=controller._file_sha256(workflow),
        output_dir=tmp_path / "out",
        required_vram_gb=None,
        rights_cleared=True,
    )

    assert result.state is PromotionState.REGISTRY_PROMOTED
    assert result.execution_evidence is not None
    # The second promotion-stage pass is preflight-only, while the
    # qualification package was built from the real trusted run.
    assert result.execution_evidence.preflight_passed is True
    assert Path(result.promoted_manifest_path).is_file()
    assert Path(result.promoted_workflow_path).is_file()

    registered = ctx.workflows.get(
        "candidate.safe.image",
        "1",
    )
    assert registered.executor_id == "local.comfyui"
    assert registered.model_id == "model.safe"


def test_shared_app_context_candidate_promotion_service():
    from cinefactory.appctx import build_context

    root = Path(__file__).resolve().parents[1]
    ctx = build_context(root)
    assert (
        ctx.candidate_promotion
        is ctx.studio.professional_company.candidate_promotion
    )
    assert (
        ctx.candidate_promotion.ctx.capability_execution_lab
        is ctx.capability_execution_lab
    )


def test_candidate_lab_work_is_durable_gpu_work(tmp_path):
    from cinefactory.turbo.contracts import (
        ResourceClass,
        WorkerSpec,
        WorkState,
    )
    from cinefactory.turbo.daemon import FactoryDaemon
    from cinefactory.turbo.store import TurboStore

    ctx = _ctx(tmp_path)
    controller = CandidatePromotionController(ctx)
    ctx.candidate_promotion = controller
    ctx.turbo_store = TurboStore(tmp_path / "turbo.db")

    work = controller.build_comfyui_lab_work_item(
        project_id="P",
        case_id="CASE",
        candidate_id="safe",
        workflow_path=_workflow(tmp_path),
        manifest=_manifest(),
        output_dir=tmp_path / "lab_out",
    )
    assert work.resource is ResourceClass.GPU
    assert work.handler == "lab.comfyui.execute"
    ctx.turbo_store.enqueue_work(work)

    daemon = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="lab-gpu",
            resources={ResourceClass.GPU},
            capabilities={"lab.comfyui.execute"},
        ),
        poll_seconds=0.01,
    )
    try:
        assert daemon.tick() is True
    finally:
        daemon.close()

    done = ctx.turbo_store.get_work(work.work_id)
    assert done.state is WorkState.SUCCESS
    assert done.result["passed"] is True
    evidence = done.result["candidate_execution"]
    assert evidence["execution_passed"] is True
    assert evidence["metadata"]["public_network_allowed"] is False


def test_acquisition_defers_for_gpu_lab_then_promotes(tmp_path):
    import hashlib

    from cinefactory.studio.capability_acquisition import (
        AcquisitionCandidateRecord,
        CapabilityAcquisitionCase,
        CapabilityAcquisitionWorker,
        CapabilityResearchCandidate,
        ResearchEvidenceTier,
    )
    from cinefactory.studio.production_method_switch import (
        MethodSwitchPolicy,
        MethodSwitchRequest,
    )
    from cinefactory.studio.rnd import ExternalToolCandidate
    from cinefactory.turbo.contracts import (
        ResourceClass,
        WorkItem,
        WorkerSpec,
    )
    from cinefactory.turbo.daemon import FactoryDaemon
    from cinefactory.turbo.store import TurboStore

    ctx = _ctx(tmp_path)
    ctx.turbo_store = TurboStore(tmp_path / "turbo.db")
    controller = CandidatePromotionController(ctx)
    ctx.candidate_promotion = controller

    acquisition = CapabilityAcquisitionWorker(
        ctx,
        research_defer_seconds=5,
        qualification_defer_seconds=5,
    )
    workflow = _workflow(tmp_path)
    candidate = CapabilityResearchCandidate(
        candidate_id="auto.lab.workflow",
        name="Auto Lab Workflow",
        tool_id="comfyui",
        source_uri="maintainer://repo",
        source_type="MAINTAINER_REPO",
        version="1",
        license_name="Apache-2.0",
        license_evidence_uri="maintainer://license",
        license_evidence_tier=(
            ResearchEvidenceTier.MAINTAINER
        ),
        commercial_use_allowed=True,
        local_supported=True,
        local_artifact_path=str(workflow),
        local_artifact_sha256=hashlib.sha256(
            workflow.read_bytes()
        ).hexdigest(),
        workflow_manifest=_manifest().model_dump(
            mode="json"
        ),
    )
    # The ExternalToolIntake row is intentionally still conservative;
    # workflow promotion is a separate scoped authority.
    record = AcquisitionCandidateRecord(
        candidate=candidate,
        intake=ExternalToolCandidate(
            candidate_id=candidate.candidate_id,
            name=candidate.name,
            source_uri=candidate.source_uri,
            source_type=candidate.source_type,
        ),
    )
    case = CapabilityAcquisitionCase(
        case_id="CASE_AUTO",
        project_id="P",
        episode_id="E",
        shot_id="S01",
        request_path=str(tmp_path / "request.json"),
        acquisition_work_id="W_ACQ",
    )
    item = WorkItem(
        work_id="W_ACQ",
        project_id="P",
        kind="rnd.capability.acquire",
        handler="rnd.capability.acquire",
        resource=ResourceClass.AGENT,
    )
    request = MethodSwitchRequest(
        project_id="P",
        episode_id="E",
        shot_id="S01",
        current_tool_id="blender",
        current_method_id="blender.cycles.quality",
        policy=MethodSwitchPolicy.QUALITY_FIRST_ALTERNATIVE,
        min_quality=0.90,
    )

    waiting = acquisition._process_candidate_promotions(
        item=item,
        case=case,
        records=[record],
        method_request=request,
    )
    assert waiting is not None
    assert waiting.deferred is True
    assert waiting.reason == "AWAITING_CANDIDATE_LAB_EXECUTION"
    assert record.lab_work_id is not None

    gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="lab-gpu",
            resources={ResourceClass.GPU},
            capabilities={"lab.comfyui.execute"},
        ),
        poll_seconds=0.01,
    )
    try:
        assert gpu.tick() is True
    finally:
        gpu.close()

    second = acquisition._process_candidate_promotions(
        item=item,
        case=case,
        records=[record],
        method_request=request,
    )
    assert second is None
    assert record.promotion_state == (
        PromotionState.REGISTRY_PROMOTED.value
    )
    assert record.promotion_attestation_id
    assert Path(record.promotion_attestation_path).is_file()
    assert ctx.workflows.get(
        "candidate.safe.image",
        "1",
    )
