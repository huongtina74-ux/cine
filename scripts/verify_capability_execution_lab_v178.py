from __future__ import annotations

import hashlib
import json
import runpy
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.studio.capability_execution_lab import (
    CapabilityExecutionLab,
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    verification_root = (
        ROOT
        / "data"
        / "verification"
        / "v178_capability_execution_lab"
    )
    verification_root.mkdir(parents=True, exist_ok=True)

    lab = CapabilityExecutionLab(ROOT)
    case_id = "VERIFY_EXEC_LAB_V178"
    candidate_id = "blender.cycles.quality"

    # ------------------------------------------------------------
    # Supply-chain artifact for the already registered method.
    # This is a method evidence manifest, not a downloaded binary.
    # ------------------------------------------------------------
    method_manifest = verification_root / "cycles_method_manifest.json"
    method_manifest.write_text(
        json.dumps(
            {
                "method_id": "blender.cycles.quality",
                "tool_id": "blender",
                "handler": "blender.animation.render",
                "execution_mode": "BLENDER_CYCLES",
                "same_scene_semantics": True,
                "target_hardware": "RTX 3060 12GB",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    provenance = lab.import_local_artifact(
        case_id=case_id,
        candidate_id=candidate_id,
        source_path=method_manifest,
        source_uri="internal://production_method_registry/blender.cycles.quality",
        source_type="INTERNAL_REGISTERED_METHOD",
        version="v1.6.18",
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
    assert provenance.hash_verified is True
    assert security.status is LabGateStatus.PASS
    assert hardware.status is LabGateStatus.PASS

    # ------------------------------------------------------------
    # Golden-shot real execution through the registered Turbo method.
    # ------------------------------------------------------------
    ctx = build_context(ROOT)
    isolated_db = verification_root / "turbo_v178.db"
    if isolated_db.exists():
        isolated_db.unlink()
    ctx.turbo_store = TurboStore(isolated_db)

    ns = runpy.run_path(
        str(
            ROOT
            / "tests"
            / "test_block_auto_repair_v173.py"
        )
    )
    episode = ns["_episode"]().model_copy(
        deep=True,
        update={
            "project_id": "VERIFY_EXEC_LAB_V178",
            "episode_id": "VERIFY_EXEC_LAB_V178",
        },
    )
    output_dir = verification_root / "golden_shot"
    compiled = EpisodeAssembler.from_root(ROOT).compile(
        episode,
        output_dir=output_dir,
    )
    original = compiled.shots[0]

    request = MethodSwitchRequest(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot_id=original.shot_id,
        current_tool_id="blender",
        current_method_id="blender.eevee.current",
        policy=MethodSwitchPolicy.QUALITY_FIRST_ALTERNATIVE,
        min_quality=0.92,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        max_additional_gpu_seconds=90.0,
        mean_current_attempt_seconds=4.0,
        continuity_priority=True,
        backend_switch_allowed=False,
        recurring_identity_required=True,
        visual_style="MINECRAFT",
        failure_codes=["MODEL_CAPABILITY"],
    )
    decision = ctx.method_switch.deliberate(request)
    assert decision.executable is True
    assert decision.selected_method_id == "blender.cycles.quality"

    switched = ctx.method_switch.transform_block_shot(
        original,
        decision,
    )
    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    render_path = output_dir / "S01.cycles.golden.mp4"
    work = ctx.method_switch.build_work_item(
        compiled=compiled,
        shot=switched,
        decision=decision,
        output_path=render_path,
        render_preview=True,
        switch_round=1,
        switch_of_work_id="GOLDEN_BASELINE",
        blender_executable=str(blender),
    )
    ctx.turbo_store.enqueue_work(work)

    gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v178-golden-gpu",
            resources={ResourceClass.GPU},
            capabilities={"blender.animation.render"},
            active_model_affinity="BLENDER:CYCLES",
        ),
        poll_seconds=0.01,
    )
    try:
        assert gpu.tick() is True
    finally:
        gpu.close()

    rendered = ctx.turbo_store.get_work(work.work_id)
    assert rendered.state is WorkState.SUCCESS
    runtime_result = dict(rendered.result)
    assert runtime_result.get("qc_passed") is True
    assert render_path.is_file()
    assert render_path.stat().st_size > 0

    sandbox = lab.sandbox_gate(
        case_id=case_id,
        candidate_id=candidate_id,
        security=security,
        trusted_executor_id="turbo.blender.animation.render",
        trusted_executor_passed=True,
        output_refs=[str(render_path)],
    )
    benchmark = lab.benchmark_block_runtime_result(
        case_id=case_id,
        candidate_id=candidate_id,
        method_id="blender.cycles.quality",
        runtime_result=runtime_result,
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
        benchmark=benchmark,
        conformance=conformance,
    )
    assert sandbox.status is LabGateStatus.PASS
    assert benchmark.status is LabGateStatus.PASS
    assert conformance.status is LabGateStatus.PASS
    assert package.passed is True

    dimensions = {
        item.name: item.score
        for item in benchmark.dimensions
    }
    for required in (
        "quality",
        "identity",
        "temporal",
        "camera_contract",
        "control",
    ):
        assert required in dimensions
    assert dimensions["quality"] == 1.0
    assert dimensions["identity"] >= 0.90
    assert dimensions["temporal"] >= 0.90
    assert dimensions["camera_contract"] == 1.0
    assert dimensions["control"] >= 0.90

    # ------------------------------------------------------------
    # Malicious package must fail before execution.
    # ------------------------------------------------------------
    malicious = verification_root / "malicious_candidate.zip"
    with zipfile.ZipFile(
        malicious,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.writestr(
            "plugin.py",
            "import os\nos.system('whoami')\n",
        )
        archive.writestr(
            "../escape.py",
            "print('escape')\n",
        )
    malicious_manifest = lab.import_local_artifact(
        case_id=case_id,
        candidate_id="malicious.candidate",
        source_path=malicious,
        source_uri="research://malicious-test",
        source_type="UNTRUSTED_FIXTURE",
        version="1",
        expected_sha256=sha256(malicious),
    )
    malicious_security = lab.static_security_scan(
        case_id=case_id,
        manifest=malicious_manifest,
    )
    malicious_sandbox = lab.sandbox_gate(
        case_id=case_id,
        candidate_id="malicious.candidate",
        security=malicious_security,
    )
    assert malicious_security.status is LabGateStatus.FAIL
    assert malicious_sandbox.status is LabGateStatus.BLOCKED
    assert "CRITICAL_STATIC_SECURITY_FINDING" in (
        malicious_security.blockers
    )
    assert any(
        item.startswith("ARCHIVE_PATH_TRAVERSAL:")
        for item in malicious_security.blockers
    )

    payload = {
        "registered_method": {
            "method_id": "blender.cycles.quality",
            "render_work_id": work.work_id,
            "render_state": rendered.state.value,
            "rendered_path": str(render_path),
            "rendered_bytes": render_path.stat().st_size,
            "gpu": gpu_snapshot(),
            "provenance_hash_verified": (
                provenance.hash_verified
            ),
            "security_status": security.status.value,
            "hardware_status": hardware.status.value,
            "sandbox_status": sandbox.status.value,
            "benchmark_status": benchmark.status.value,
            "benchmark_aggregate": benchmark.aggregate_score,
            "benchmark_dimensions": dimensions,
            "conformance_status": conformance.status.value,
            "qualification_package_passed": package.passed,
            "qualification_package": str(
                lab.store.report_path(
                    case_id,
                    candidate_id,
                    "qualification_evidence",
                )
            ),
        },
        "malicious_candidate": {
            "security_status": malicious_security.status.value,
            "security_blockers": malicious_security.blockers,
            "security_findings": [
                item.model_dump(mode="json")
                for item in malicious_security.findings
            ],
            "sandbox_status": malicious_sandbox.status.value,
            "sandbox_findings": malicious_sandbox.findings,
        },
    }
    out = verification_root / (
        "capability_execution_lab_verification.json"
    )
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
