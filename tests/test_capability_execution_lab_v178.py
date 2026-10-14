from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from cinefactory.studio.capability_acquisition import (
    CapabilityAcquisitionWorker,
    CapabilityResearchCandidate,
    ResearchEvidenceTier,
)
from cinefactory.studio.capability_execution_lab import (
    BenchmarkDimension,
    CapabilityExecutionLab,
    LabGateStatus,
)


def _zip(
    path: Path,
    files: dict[str, str],
) -> Path:
    with zipfile.ZipFile(
        path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for name, body in files.items():
            archive.writestr(name, body)
    return path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_artifact(tmp_path: Path) -> Path:
    return _zip(
        tmp_path / "safe_candidate.zip",
        {
            "requirements.txt": (
                "pydantic==2.11.7\n"
                "numpy>=2.0\n"
            ),
            "adapter.py": (
                "def normalize(value):\n"
                "    return {'value': value}\n"
            ),
            "package.json": json.dumps(
                {
                    "dependencies": {
                        "ws": "^8.18.0",
                    }
                }
            ),
        },
    )


def test_content_addressed_import_security_sbom_and_hardware(tmp_path):
    artifact = _safe_artifact(tmp_path)
    lab = CapabilityExecutionLab(tmp_path)

    provenance = lab.import_local_artifact(
        case_id="CASE1",
        candidate_id="safe",
        source_path=artifact,
        source_uri="https://example.invalid/repo",
        source_type="MAINTAINER_REPO",
        version="1.0",
        expected_sha256=_sha256(artifact),
    )
    assert provenance.hash_verified is True
    assert Path(provenance.imported_path).is_file()
    assert provenance.sha256 == _sha256(artifact)

    security = lab.static_security_scan(
        case_id="CASE1",
        manifest=provenance,
    )
    assert security.status is LabGateStatus.PASS
    assert security.blockers == []

    sbom = lab.generate_sbom(
        case_id="CASE1",
        manifest=provenance,
    )
    assert sbom.status is LabGateStatus.PASS
    names = {(item.ecosystem, item.name) for item in sbom.entries}
    assert ("python", "pydantic") in names
    assert ("python", "numpy") in names
    assert ("npm", "ws") in names

    hardware = lab.hardware_fit(
        case_id="CASE1",
        candidate_id="safe",
        required_vram_gb=8.0,
        gpu_snapshot={
            "available": True,
            "gpus": [{"vram_mb": 12288.0}],
        },
    )
    assert hardware.status is LabGateStatus.PASS
    assert hardware.available_vram_gb == pytest.approx(12.0)


def test_zip_slip_is_hard_security_failure(tmp_path):
    artifact = _zip(
        tmp_path / "traversal.zip",
        {
            "../escape.py": "print('no')\n",
            "safe.py": "print('safe')\n",
        },
    )
    lab = CapabilityExecutionLab(tmp_path)
    provenance = lab.import_local_artifact(
        case_id="CASE2",
        candidate_id="traversal",
        source_path=artifact,
        source_uri="https://example.invalid/repo",
        source_type="MAINTAINER_REPO",
        version="1",
        expected_sha256=_sha256(artifact),
    )
    security = lab.static_security_scan(
        case_id="CASE2",
        manifest=provenance,
    )
    assert security.status is LabGateStatus.FAIL
    assert any(
        item.startswith("ARCHIVE_PATH_TRAVERSAL:")
        for item in security.blockers
    )


def test_critical_shell_execution_is_blocked(tmp_path):
    artifact = _zip(
        tmp_path / "danger.zip",
        {
            "plugin.py": (
                "import os\n"
                "os.system('echo unsafe')\n"
            ),
        },
    )
    lab = CapabilityExecutionLab(tmp_path)
    provenance = lab.import_local_artifact(
        case_id="CASE3",
        candidate_id="danger",
        source_path=artifact,
        source_uri="https://example.invalid/repo",
        source_type="MAINTAINER_REPO",
        version="1",
        expected_sha256=_sha256(artifact),
    )
    security = lab.static_security_scan(
        case_id="CASE3",
        manifest=provenance,
    )
    assert security.status is LabGateStatus.FAIL
    assert "CRITICAL_STATIC_SECURITY_FINDING" in security.blockers
    assert any(
        item.code == "OS_SYSTEM_EXECUTION"
        for item in security.findings
    )


def test_hash_mismatch_cannot_pass_security_gate(tmp_path):
    artifact = _safe_artifact(tmp_path)
    lab = CapabilityExecutionLab(tmp_path)
    provenance = lab.import_local_artifact(
        case_id="CASE4",
        candidate_id="hash_mismatch",
        source_path=artifact,
        source_uri="https://example.invalid/repo",
        source_type="MAINTAINER_REPO",
        version="1",
        expected_sha256="0" * 64,
    )
    assert provenance.hash_verified is False
    security = lab.static_security_scan(
        case_id="CASE4",
        manifest=provenance,
    )
    assert security.status is LabGateStatus.FAIL
    assert "EXPECTED_HASH_NOT_VERIFIED" in security.blockers


def test_vram_over_target_fails_hardware_gate(tmp_path):
    lab = CapabilityExecutionLab(tmp_path)
    report = lab.hardware_fit(
        case_id="CASE5",
        candidate_id="too_large",
        required_vram_gb=16.0,
        gpu_snapshot={
            "available": True,
            "gpus": [{"vram_mb": 12288.0}],
        },
    )
    assert report.status is LabGateStatus.FAIL
    assert "VRAM_REQUIREMENT_EXCEEDS_DEVICE" in report.findings


def test_untrusted_candidate_code_is_never_executed_by_default(tmp_path):
    artifact = _safe_artifact(tmp_path)
    lab = CapabilityExecutionLab(tmp_path)
    provenance = lab.import_local_artifact(
        case_id="CASE6",
        candidate_id="no_executor",
        source_path=artifact,
        source_uri="https://example.invalid/repo",
        source_type="MAINTAINER_REPO",
        version="1",
        expected_sha256=_sha256(artifact),
    )
    security = lab.static_security_scan(
        case_id="CASE6",
        manifest=provenance,
    )
    sandbox = lab.sandbox_gate(
        case_id="CASE6",
        candidate_id="no_executor",
        security=security,
    )
    assert sandbox.status is LabGateStatus.BLOCKED
    assert "EXECUTION_SANDBOX_NOT_AVAILABLE" in sandbox.findings
    assert "UNTRUSTED_CANDIDATE_CODE_NOT_EXECUTED" in sandbox.findings


def test_complete_internal_evidence_package_can_pass(tmp_path):
    artifact = _safe_artifact(tmp_path)
    lab = CapabilityExecutionLab(tmp_path)
    provenance = lab.import_local_artifact(
        case_id="CASE7",
        candidate_id="qualified",
        source_path=artifact,
        source_uri="https://example.invalid/repo",
        source_type="MAINTAINER_REPO",
        version="1",
        expected_sha256=_sha256(artifact),
    )
    sbom = lab.generate_sbom(
        case_id="CASE7",
        manifest=provenance,
    )
    security = lab.static_security_scan(
        case_id="CASE7",
        manifest=provenance,
    )
    hardware = lab.hardware_fit(
        case_id="CASE7",
        candidate_id="qualified",
        required_vram_gb=8.0,
        gpu_snapshot={
            "available": True,
            "gpus": [{"vram_mb": 12288.0}],
        },
    )
    sandbox = lab.sandbox_gate(
        case_id="CASE7",
        candidate_id="qualified",
        security=security,
        trusted_executor_id="test.trusted.sandbox",
        trusted_executor_passed=True,
        output_refs=["sandbox://evidence"],
    )
    benchmark = lab.benchmark_gate(
        case_id="CASE7",
        candidate_id="qualified",
        method_id="tool.method",
        dimensions=[
            BenchmarkDimension(name="quality", score=0.94),
            BenchmarkDimension(name="identity", score=0.96),
            BenchmarkDimension(name="temporal", score=0.91),
            BenchmarkDimension(name="camera_contract", score=0.93),
            BenchmarkDimension(name="control", score=0.95),
        ],
    )
    conformance = lab.conformance_gate(
        case_id="CASE7",
        candidate_id="qualified",
        adapter_registered=True,
        handler_registered=True,
        normalization_passed=True,
        canonical_roundtrip_passed=True,
    )
    package = lab.package(
        case_id="CASE7",
        candidate_id="qualified",
        tool_id="tool",
        method_id="tool.method",
        provenance=provenance,
        sbom=sbom,
        security=security,
        hardware=hardware,
        sandbox=sandbox,
        benchmark=benchmark,
        conformance=conformance,
    )
    assert package.passed is True
    assert package.blockers == []


def test_runtime_benchmark_uses_measured_block_evidence(tmp_path):
    lab = CapabilityExecutionLab(tmp_path)
    result = {
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
            "score": 0.97,
        },
        "performance_qc": {
            "passed": True,
            "score": 0.93,
        },
        "geometry_qc": {
            "passed": True,
            "targets": [{"blockers": []}],
        },
        "creative_intent_bound": True,
        "render_state": {
            "camera": {
                "start": {"lens_mm": 48.0},
                "end": {"lens_mm": 48.0},
            }
        },
    }
    benchmark = lab.benchmark_block_runtime_result(
        case_id="CASE8",
        candidate_id="cycles",
        method_id="blender.cycles.quality",
        runtime_result=result,
    )
    assert benchmark.status is LabGateStatus.PASS
    by_name = {
        item.name: item.score
        for item in benchmark.dimensions
    }
    assert by_name["quality"] == 1.0
    assert by_name["identity"] == pytest.approx(0.97)
    assert by_name["temporal"] == 1.0
    assert by_name["camera_contract"] == 1.0
    assert by_name["control"] > 0.95
    assert benchmark.aggregate_score > 0.95


def test_arbitrary_pass_json_outside_lab_root_is_not_trusted(tmp_path):
    fake = tmp_path / "fake_pass.json"
    fake.write_text(
        json.dumps({"passed": True, "status": "PASS"}),
        encoding="utf-8",
    )
    worker = CapabilityAcquisitionWorker(
        SimpleNamespace(root=tmp_path)
    )
    assert worker._trusted_lab_report_passed(
        str(fake)
    ) is False


def test_worker_auto_generates_static_lab_package(tmp_path):
    artifact = _safe_artifact(tmp_path)
    method_switch = SimpleNamespace(
        specs=[],
        registered_handlers=set(),
    )
    worker = CapabilityAcquisitionWorker(
        SimpleNamespace(
            root=tmp_path,
            method_switch=method_switch,
        )
    )
    fake_pass = tmp_path / "external_claim.json"
    fake_pass.write_text(
        json.dumps({"passed": True}),
        encoding="utf-8",
    )
    candidate = CapabilityResearchCandidate(
        candidate_id="candidate.static.lab",
        name="Static Lab Candidate",
        tool_id="newtool",
        method_id="newtool.video",
        source_uri="https://example.invalid/repo",
        source_type="MAINTAINER_REPO",
        version="1",
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
        local_artifact_path=str(artifact),
        local_artifact_sha256=_sha256(artifact),
        security_evidence_refs=[
            "external-security-review-reference"
        ],
        sandbox_report_path=str(fake_pass),
        benchmark_report_path=str(fake_pass),
        adapter_regression_report_path=str(fake_pass),
    )
    record = worker._candidate_record(
        candidate,
        case_id="CASE9",
    )
    assert record.local_artifact_verified is True
    assert record.execution_lab_package_path is not None
    assert Path(record.execution_lab_package_path).is_file()
    assert record.execution_lab_passed is False
    assert record.sandbox_report_passed is False
    assert record.benchmark_report_passed is False
    assert record.adapter_regression_passed is False
    assert "SANDBOX_NOT_PASSED" in record.blockers
    assert "BENCHMARK_NOT_PASSED" in record.blockers


def test_app_context_exposes_one_shared_execution_lab(tmp_path):
    from cinefactory.appctx import build_context

    root = Path(__file__).resolve().parents[1]
    ctx = build_context(root)
    assert ctx.capability_execution_lab is (
        ctx.capability_acquisition.execution_lab
    )
    assert (
        ctx.studio.professional_company.capability_execution_lab
        is ctx.capability_execution_lab
    )


def test_lab_evidence_cannot_be_replayed_across_candidates(tmp_path):
    method_switch = SimpleNamespace(
        specs=[],
        registered_handlers=set(),
    )
    worker = CapabilityAcquisitionWorker(
        SimpleNamespace(
            root=tmp_path,
            method_switch=method_switch,
        )
    )
    lab = worker.execution_lab
    artifact = _safe_artifact(tmp_path)
    provenance = lab.import_local_artifact(
        case_id="CASE10",
        candidate_id="candidate.a",
        source_path=artifact,
        source_uri="internal://candidate-a",
        source_type="TEST",
        version="1",
        expected_sha256=_sha256(artifact),
    )
    security = lab.static_security_scan(
        case_id="CASE10",
        manifest=provenance,
    )
    sandbox = lab.sandbox_gate(
        case_id="CASE10",
        candidate_id="candidate.a",
        security=security,
        trusted_executor_id="test.sandbox",
        trusted_executor_passed=True,
    )
    assert sandbox.status is LabGateStatus.PASS
    path = str(
        lab.store.report_path(
            "CASE10",
            "candidate.a",
            "sandbox",
        )
    )
    assert worker._trusted_lab_report_passed(
        path,
        case_id="CASE10",
        candidate_id="candidate.a",
        report_name="sandbox",
    ) is True
    assert worker._trusted_lab_report_passed(
        path,
        case_id="CASE10",
        candidate_id="candidate.b",
        report_name="sandbox",
    ) is False
