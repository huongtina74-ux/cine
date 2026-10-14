from __future__ import annotations

from pathlib import Path

from cinefactory.studio.contracts import SkillEvaluation
from cinefactory.studio.execution_mastery import ToolExecutionMasteryReport
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.knowledge import ToolEnvironment
from cinefactory.studio.production_qualification import (
    AdapterImplementationStatus,
    AttestationKind,
    ProductionQualificationBoard,
    QualificationAttestation,
)


def _mock_installed_blender(kernel) -> None:
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="blender",
            installed=True,
            version="Blender 4.5.14 LTS",
            executable_path="C:/fake/blender.exe",
        )
        if tool_id == "blender"
        else original(tool_id)
    )


def _seed_blender_mastery(kernel) -> None:
    operations = sorted(
        {
            operation
            for item in kernel.tool_skills.list("blender")
            for operation in item.operations
        }
    )
    kernel.execution_mastery.save(
        ToolExecutionMasteryReport(
            tool_id="blender",
            skill_id="tool.blender.production",
            version="4.5",
            installed=True,
            detected_version="Blender 4.5.14 LTS",
            sandbox_root="C:/fake/sandbox",
            required_operations=operations,
            passed_operations=operations,
            missing_operations=[],
            execution_coverage=1.0,
            knowledge_coverage=1.0,
            passed=True,
            regression_passed=True,
        )
    )
    kernel.skills.record_evaluation(
        SkillEvaluation(
            skill_id="tool.blender.production",
            version="4.5",
            passed=True,
            score=1.0,
            eval_id="qualification_seed",
            findings=[],
            regression_passed=True,
        )
    )
    kernel.skills.validate_skill("tool.blender.production", "4.5")


def _attest_all(kernel) -> None:
    for kind in AttestationKind:
        kernel.production_qualification.add_attestation(
            QualificationAttestation(
                attestation_id=f"ATT_blender_{kind.value.lower()}",
                tool_id="blender",
                kind=kind,
                approved=True,
                reviewer="studio-test-reviewer",
                rationale=f"approved {kind.value} for deterministic test",
                evidence_refs=[f"test://{kind.value.lower()}"],
                tool_version=(
                    "4.5.14"
                    if kind is AttestationKind.VERSION_COMPATIBILITY
                    else None
                ),
            )
        )


def test_all_default_adapters_cover_declared_tool_operations(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    for adapter in kernel.tool_adapters.list():
        required = {
            operation
            for skill in kernel.tool_skills.list(adapter.tool_id)
            for operation in skill.operations
        }
        assert required <= (
            adapter.supported_operations
            | set(adapter.delegated_operations)
        )


def test_only_real_local_adapters_are_marked_executable(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    status = {
        item.tool_id: item.implementation_status
        for item in kernel.tool_adapters.list()
    }
    assert status["blender"] is AdapterImplementationStatus.EXECUTABLE
    assert status["ffmpeg"] is AdapterImplementationStatus.EXECUTABLE
    assert status["comfyui"] is AdapterImplementationStatus.EXECUTABLE
    assert status["resolve"] is AdapterImplementationStatus.EXECUTABLE
    assert status["premiere"] is AdapterImplementationStatus.EXECUTABLE
    assert status["photoshop"] is AdapterImplementationStatus.EXECUTABLE
    assert status["aftereffects"] is AdapterImplementationStatus.EXECUTABLE
    assert status["unreal"] is AdapterImplementationStatus.EXECUTABLE
    assert status["canva"] is AdapterImplementationStatus.EXECUTABLE


def test_qualification_blocks_even_mastered_tool_without_attestations(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    _mock_installed_blender(kernel)
    _seed_blender_mastery(kernel)
    decision = ProductionQualificationBoard(kernel).evaluate("blender")
    assert decision.qualified is False
    assert "EXECUTION_MASTERY_COMPLETE" in decision.passed_checks
    assert "ADAPTER_READY" in decision.passed_checks
    assert any(
        blocker.startswith("ATTESTATION_MISSING:")
        for blocker in decision.blockers
    )
    assert kernel.skills.can_execute("tool.blender.production", "4.5") is False


def test_full_attestation_promotes_validated_skill_to_production(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    _mock_installed_blender(kernel)
    _seed_blender_mastery(kernel)
    _attest_all(kernel)

    board = ProductionQualificationBoard(kernel)
    before = board.evaluate("blender")
    assert before.qualified is True

    after = board.promote_if_qualified("blender")
    assert after.qualified is True
    manifest = kernel.skills.get("tool.blender.production", "4.5")
    assert manifest.status.value == "PRODUCTION"
    assert manifest.commercial_safe is True
    assert manifest.security_reviewed is True
    assert manifest.code_execution_allowed is True
    assert kernel.skills.can_execute("tool.blender.production", "4.5") is True


def test_premiere_runtime_adapter_stays_unavailable_without_bridge(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="premiere",
            installed=True,
            version="26.0",
            executable_path="C:/fake/Premiere.exe",
        )
        if tool_id == "premiere"
        else original(tool_id)
    )
    probe = kernel.tool_adapters.probe(kernel, "premiere")
    assert probe.available is False
    assert any(
        finding in {
            "ADOBE_BRIDGE_TOKEN_MISSING",
            "ADOBE_PLUGIN_CLIENT_NOT_REGISTERED",
        }
        or finding.startswith("ADOBE_BRIDGE_UNREACHABLE:")
        for finding in probe.findings
    )
