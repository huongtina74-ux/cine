from __future__ import annotations

import hashlib
import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.studio.candidate_promotion import (
    CandidatePromotionController,
    CandidatePromotionStore,
    MultiShotBenchmarkMatrix,
    PromotionState,
    TrustedArtifactClass,
    TrustedCandidateExecution,
)
from cinefactory.studio.capability_execution_lab import (
    LabGateStatus,
)
from cinefactory.studio.production_method_switch import (
    MethodSwitchPolicy,
    MethodSwitchRequest,
)
from cinefactory.turbo.contracts import (
    ResourceClass,
    WorkerSpec,
    WorkState,
)
from cinefactory.turbo.daemon import FactoryDaemon
from cinefactory.turbo.metrics import gpu_snapshot
from cinefactory.turbo.store import TurboStore
from cinefactory.workflows.registry import (
    WorkflowManifest,
    WorkflowRegistry,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    verification_root = (
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
    )
    verification_root.mkdir(
        parents=True,
        exist_ok=True,
    )
    turbo_db = verification_root / "turbo_v179.db"
    if turbo_db.exists():
        turbo_db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(turbo_db)

    isolated_workflows = WorkflowRegistry(
        verification_root / "promoted_workflows"
    ).load()
    controller = CandidatePromotionController(
        ctx,
        store=CandidatePromotionStore(
            verification_root / "promotion"
        ),
        workflow_registry=isolated_workflows,
    )
    ctx.candidate_promotion = controller
    ctx.studio.professional_company.candidate_promotion = (
        controller
    )

    # ------------------------------------------------------------
    # A. Trusted declarative ComfyUI candidate through Turbo GPU.
    # ------------------------------------------------------------
    source_manifest = ctx.workflows.get(
        "comfy.mastery.sd15",
        "1",
    )
    source_workflow = (
        ROOT
        / "workflows"
        / "comfyui"
        / "mastery_sd15.json"
    )
    promoted_manifest = source_manifest.model_copy(
        update={
            "workflow_id": "verify.v179.comfy.sd15",
            "version": "1",
            "workflow_file": source_workflow.name,
            "notes": [
                *source_manifest.notes,
                "v1.6.19 isolated promotion verifier",
            ],
        }
    )
    comfy_output = verification_root / "comfy_candidate"
    lab_work = controller.build_comfyui_lab_work_item(
        project_id="VERIFY_PROMOTION_V179",
        case_id="VERIFY_PROMOTION_V179_COMFY",
        candidate_id="verify.comfy.sd15",
        workflow_path=source_workflow,
        manifest=promoted_manifest,
        output_dir=comfy_output,
        required_vram_gb=4.0,
    )
    ctx.turbo_store.enqueue_work(lab_work)

    comfy_gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v179-comfy-lab-gpu",
            resources={ResourceClass.GPU},
            capabilities={"lab.comfyui.execute"},
            active_model_affinity=(
                "COMFYUI:"
                + source_manifest.model_id
                + "@"
                + str(
                    source_manifest.model_revision
                    or ""
                )
            ),
        ),
        poll_seconds=0.01,
    )
    try:
        assert comfy_gpu.tick() is True
    finally:
        comfy_gpu.close()

    lab_done = ctx.turbo_store.get_work(
        lab_work.work_id
    )
    assert lab_done.state is WorkState.SUCCESS
    assert lab_done.result["passed"] is True
    comfy_execution = (
        TrustedCandidateExecution.model_validate(
            lab_done.result["candidate_execution"]
        )
    )
    assert comfy_execution.execution_passed is True
    assert comfy_execution.artifacts
    assert all(
        Path(path).is_file()
        for path in comfy_execution.artifacts
    )

    comfy_attestation = (
        controller
        .qualify_and_promote_comfyui_workflow(
            candidate_id="verify.comfy.sd15",
            workflow_path=source_workflow,
            manifest=promoted_manifest,
            source_uri=(
                "internal://workflows/"
                "comfy.mastery.sd15@1"
            ),
            source_type=(
                "INTERNAL_APPROVED_WORKFLOW"
            ),
            expected_sha256=sha256(
                source_workflow
            ),
            output_dir=comfy_output,
            required_vram_gb=4.0,
            rights_cleared=True,
            execution_evidence=comfy_execution,
        )
    )
    assert comfy_attestation.state is (
        PromotionState.REGISTRY_PROMOTED
    )
    registered = isolated_workflows.get(
        "verify.v179.comfy.sd15",
        "1",
    )
    assert registered.executor_id == "local.comfyui"
    assert Path(
        comfy_attestation.promoted_workflow_path
    ).is_file()
    assert Path(
        comfy_attestation.promoted_manifest_path
    ).is_file()

    # Explicitly prove auto-execution rejects arbitrary Python code.
    unsafe_python = (
        verification_root / "untrusted_plugin.py"
    )
    unsafe_python.write_text(
        "print('should never auto execute')\n",
        encoding="utf-8",
    )
    blocked_classification = (
        controller.executor.classify(
            unsafe_python
        )
    )
    assert blocked_classification.artifact_class is (
        TrustedArtifactClass.PYTHON_CODE
    )
    assert (
        blocked_classification.auto_execution_allowed
        is False
    )

    # ------------------------------------------------------------
    # B. Two real Cycles golden-shot cases -> benchmark matrix.
    # ------------------------------------------------------------
    ns = runpy.run_path(
        str(
            ROOT
            / "tests"
            / "test_block_auto_repair_v173.py"
        )
    )
    source_episode = ns["_episode"]()
    shot1 = source_episode.shots[0].model_copy(
        deep=True,
        update={
            "shot_id": "S01",
            "creative_intent": {
                "scene_id": "SC_GOLDEN_A",
                "golden_case": "A",
            },
        },
    )
    shot2 = source_episode.shots[0].model_copy(
        deep=True,
        update={
            "shot_id": "S02",
            "creative_intent": {
                "scene_id": "SC_GOLDEN_B",
                "golden_case": "B",
            },
        },
    )
    episode = source_episode.model_copy(
        deep=True,
        update={
            "project_id": "VERIFY_PROMOTION_V179",
            "episode_id": "VERIFY_PROMOTION_V179",
            "shots": [shot1, shot2],
        },
    )
    golden_dir = verification_root / "cycles_matrix"
    compiled = EpisodeAssembler.from_root(ROOT).compile(
        episode,
        output_dir=golden_dir,
    )
    request = MethodSwitchRequest(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot_id="S01",
        current_tool_id="blender",
        current_method_id="blender.eevee.current",
        policy=(
            MethodSwitchPolicy
            .QUALITY_FIRST_ALTERNATIVE
        ),
        min_quality=0.92,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        max_additional_gpu_seconds=120.0,
        mean_current_attempt_seconds=4.0,
        continuity_priority=True,
        backend_switch_allowed=False,
        recurring_identity_required=True,
        visual_style="MINECRAFT",
        failure_codes=["MODEL_CAPABILITY"],
    )
    decision = ctx.method_switch.deliberate(
        request
    )
    assert decision.executable is True
    assert decision.selected_method_id == (
        "blender.cycles.quality"
    )

    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    cycle_work_ids: list[str] = []
    for index, shot in enumerate(
        compiled.shots,
        1,
    ):
        switched = (
            ctx.method_switch.transform_block_shot(
                shot,
                decision,
            )
        )
        work = (
            ctx.method_switch.build_work_item(
                compiled=compiled,
                shot=switched,
                decision=decision,
                output_path=(
                    golden_dir
                    / (
                        f"{shot.shot_id}."
                        "cycles.golden.mp4"
                    )
                ),
                render_preview=True,
                switch_round=1,
                switch_of_work_id=(
                    f"GOLDEN_BASE_{index}"
                ),
                blender_executable=str(blender),
            )
        )
        ctx.turbo_store.enqueue_work(work)
        cycle_work_ids.append(work.work_id)

    cycles_gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v179-cycles-matrix-gpu",
            resources={ResourceClass.GPU},
            capabilities={
                "blender.animation.render"
            },
            active_model_affinity="BLENDER:CYCLES",
        ),
        poll_seconds=0.01,
    )
    try:
        assert cycles_gpu.tick() is True
        assert cycles_gpu.tick() is True
    finally:
        cycles_gpu.close()

    cycle_rows = [
        ctx.turbo_store.get_work(work_id)
        for work_id in cycle_work_ids
    ]
    assert all(
        row.state is WorkState.SUCCESS
        for row in cycle_rows
    )
    runtime_results = [
        (
            f"GOLDEN_{index}",
            dict(row.result),
        )
        for index, row in enumerate(
            cycle_rows,
            1,
        )
    ]

    matrix = MultiShotBenchmarkMatrix(
        ctx.capability_execution_lab,
        required_cases=2,
        minimum_dimension_score=0.80,
    ).from_runtime_results(
        matrix_id="MATRIX_V179_CYCLES",
        candidate_id="blender.cycles.quality",
        method_id="blender.cycles.quality",
        runtime_results=runtime_results,
    )
    assert matrix.passed is True
    assert len(matrix.rows) == 2
    assert matrix.aggregate_minimum >= 0.80
    assert all(
        score >= 0.80
        for score in matrix.dimension_minima.values()
    )

    # Build fresh trusted method evidence package using the first
    # real matrix render as sandbox + single-run qualification evidence.
    method_manifest = (
        verification_root
        / "cycles_method_manifest.json"
    )
    method_manifest.write_text(
        json.dumps(
            {
                "method_id": (
                    "blender.cycles.quality"
                ),
                "handler": (
                    "blender.animation.render"
                ),
                "same_scene_semantics": True,
                "target_gpu": (
                    "NVIDIA RTX 3060 12GB"
                ),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    lab = ctx.capability_execution_lab
    case_id = "VERIFY_PROMOTION_V179_CYCLES"
    candidate_id = "blender.cycles.quality"
    provenance = lab.import_local_artifact(
        case_id=case_id,
        candidate_id=candidate_id,
        source_path=method_manifest,
        source_uri=(
            "internal://production_method_registry/"
            "blender.cycles.quality"
        ),
        source_type="INTERNAL_REGISTERED_METHOD",
        version="v1.6.19",
        expected_sha256=sha256(method_manifest),
    )
    sbom = lab.generate_sbom(
        case_id=case_id,
        manifest=provenance,
    )
    security = lab.static_security_scan(
        case_id=case_id,
        manifest=provenance,
    )
    hardware = lab.hardware_fit(
        case_id=case_id,
        candidate_id=candidate_id,
        required_vram_gb=8.0,
        gpu_snapshot=gpu_snapshot(),
    )
    sandbox = lab.sandbox_gate(
        case_id=case_id,
        candidate_id=candidate_id,
        security=security,
        trusted_executor_id=(
            "turbo.blender.animation.render"
        ),
        trusted_executor_passed=True,
        output_refs=[
            str(
                cycle_rows[0].result.get("path")
            )
        ],
    )
    single_benchmark = (
        lab.benchmark_block_runtime_result(
            case_id=case_id,
            candidate_id=candidate_id,
            method_id="blender.cycles.quality",
            runtime_result=dict(
                cycle_rows[0].result
            ),
        )
    )
    conformance = lab.conformance_gate(
        case_id=case_id,
        candidate_id=candidate_id,
        adapter_registered=True,
        handler_registered=True,
        normalization_passed=True,
        canonical_roundtrip_passed=True,
    )
    package = lab.package(
        case_id=case_id,
        candidate_id=candidate_id,
        tool_id="blender",
        method_id="blender.cycles.quality",
        provenance=provenance,
        sbom=sbom,
        security=security,
        hardware=hardware,
        sandbox=sandbox,
        benchmark=single_benchmark,
        conformance=conformance,
    )
    assert package.passed is True
    package_path = lab.store.report_path(
        case_id,
        candidate_id,
        "qualification_evidence",
    )

    method_attestation = (
        controller.attest_registered_method(
            candidate_id=candidate_id,
            method_id="blender.cycles.quality",
            evidence_package_path=package_path,
            benchmark_matrix=matrix,
            method_request=request,
        )
    )
    assert method_attestation.state is (
        PromotionState.PRODUCTION_EXECUTABLE
    )
    assert method_attestation.blockers == []

    # A matrix with a weak identity case must not promote.
    weak_result = dict(runtime_results[1][1])
    weak_result["identity_qc"] = {
        "passed": True,
        "score": 0.50,
    }
    weak_matrix = MultiShotBenchmarkMatrix(
        lab,
        required_cases=2,
        minimum_dimension_score=0.80,
    ).from_runtime_results(
        matrix_id="MATRIX_V179_CYCLES_WEAK",
        candidate_id=candidate_id,
        method_id="blender.cycles.quality",
        runtime_results=[
            runtime_results[0],
            ("GOLDEN_WEAK", weak_result),
        ],
    )
    assert weak_matrix.passed is False
    weak_attestation = (
        controller.attest_registered_method(
            candidate_id=(
                "blender.cycles.quality.weak"
            ),
            method_id="blender.cycles.quality",
            evidence_package_path=package_path,
            benchmark_matrix=weak_matrix,
            method_request=request,
        )
    )
    assert weak_attestation.state is (
        PromotionState.BLOCKED
    )

    payload = {
        "comfyui_candidate": {
            "lab_work_id": lab_work.work_id,
            "lab_state": lab_done.state.value,
            "execution_passed": (
                comfy_execution.execution_passed
            ),
            "artifacts": (
                comfy_execution.artifacts
            ),
            "promotion_state": (
                comfy_attestation.state.value
            ),
            "promoted_workflow": (
                comfy_attestation
                .promoted_workflow_path
            ),
            "promoted_manifest": (
                comfy_attestation
                .promoted_manifest_path
            ),
            "registry_count": len(
                isolated_workflows.list()
            ),
        },
        "blocked_code_candidate": {
            "artifact_class": (
                blocked_classification
                .artifact_class.value
            ),
            "auto_execution_allowed": (
                blocked_classification
                .auto_execution_allowed
            ),
            "findings": (
                blocked_classification.findings
            ),
        },
        "cycles_multi_shot": {
            "work_ids": cycle_work_ids,
            "states": [
                row.state.value
                for row in cycle_rows
            ],
            "paths": [
                row.result.get("path")
                for row in cycle_rows
            ],
            "matrix_passed": matrix.passed,
            "matrix_aggregate_mean": (
                matrix.aggregate_mean
            ),
            "matrix_aggregate_minimum": (
                matrix.aggregate_minimum
            ),
            "dimension_minima": (
                matrix.dimension_minima
            ),
            "method_attestation_state": (
                method_attestation.state.value
            ),
            "weak_matrix_passed": (
                weak_matrix.passed
            ),
            "weak_attestation_state": (
                weak_attestation.state.value
            ),
            "qualification_package": (
                str(package_path)
            ),
        },
        "gpu": gpu_snapshot(),
    }
    out = verification_root / (
        "candidate_promotion_verification.json"
    )
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
