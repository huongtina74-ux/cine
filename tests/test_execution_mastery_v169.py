from __future__ import annotations

from pathlib import Path

from cinefactory.studio.execution_mastery import (
    ExecutionMasteryRunner,
    ExecutionMasteryStore,
    OperationEvidence,
    ToolExecutionMasteryReport,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.knowledge import ToolEnvironment
from cinefactory.studio.tooling import ToolDoctor


class PassingEvaluator:
    def __init__(self, operations: list[str]) -> None:
        self.operations = operations

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        sandbox.mkdir(parents=True, exist_ok=True)
        evidence_file = sandbox / "dummy.txt"
        evidence_file.write_text("ok", encoding="utf-8")
        return [
            OperationEvidence(
                operation=operation,
                passed=True,
                artifacts=[str(evidence_file)],
            )
            for operation in self.operations
        ]


def test_execution_mastery_store_roundtrip(tmp_path: Path):
    store = ExecutionMasteryStore(tmp_path / "mastery")
    report = ToolExecutionMasteryReport(
        tool_id="ffmpeg",
        skill_id="tool.ffmpeg.post",
        version="1",
        installed=True,
        sandbox_root=str(tmp_path),
        required_operations=["probe"],
        passed_operations=["probe"],
        execution_coverage=1.0,
        knowledge_coverage=1.0,
        passed=True,
        regression_passed=True,
        operation_evidence=[
            OperationEvidence(operation="probe", passed=True)
        ],
    )
    path = store.save(report)
    assert path.is_file()
    restored = store.get("ffmpeg")
    assert restored == report
    assert store.list() == [report]


def test_complete_operation_evidence_promotes_candidate_to_validated(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="premiere",
            installed=True,
            version="26.test",
            executable_path="C:/fake/Premiere.exe",
        )
        if tool_id == "premiere"
        else original(tool_id)
    )
    operations = kernel.tool_skills.list("premiere")[0].operations
    runner = ExecutionMasteryRunner(kernel)
    runner._evaluators["premiere"] = PassingEvaluator(operations)
    report = runner.evaluate("premiere")
    assert report.passed
    assert report.execution_coverage == 1.0
    assert report.knowledge_coverage == 1.0
    assert report.missing_operations == []
    assert (
        kernel.skills.get("tool.premiere.editorial", "2026").status.value
        == "VALIDATED"
    )


def test_installed_resolve_without_runtime_stays_incomplete(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="resolve",
            installed=True,
            version="20.test",
            executable_path="C:/fake/Resolve.exe",
        )
        if tool_id == "resolve"
        else original(tool_id)
    )
    report = ExecutionMasteryRunner(kernel).evaluate(
        "resolve",
        promote_validated=False,
    )
    assert report.passed is False
    assert report.execution_coverage == 0.0
    assert set(report.missing_operations) == set(
        kernel.tool_skills.list("resolve")[0].operations
    )
    assert all(
        any(
            finding.startswith("RESOLVE_RUNTIME_UNAVAILABLE:")
            for finding in item.findings
        )
        for item in report.operation_evidence
    )


def test_comfyui_doctor_detects_local_main_py(tmp_path: Path):
    main = tmp_path / ".tools" / "ComfyUI" / "main.py"
    main.parent.mkdir(parents=True)
    main.write_text("print('comfy')", encoding="utf-8")
    env = ToolDoctor(tmp_path).inspect("comfyui")
    assert env.installed
    assert Path(env.executable_path or "") == main
    assert "workflow_json" in env.capabilities
