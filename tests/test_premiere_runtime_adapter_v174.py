from __future__ import annotations

import shutil
from pathlib import Path

from cinefactory.adobe.premiere import (
    PremiereOperationEvidence,
    PremiereRuntimeProbe,
    PremiereSandboxResult,
)
from cinefactory.studio.execution_mastery import (
    ExecutionMasteryRunner,
    OperationEvidence,
    PremiereExecutionEvaluator,
    ToolExecutionMasteryReport,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.knowledge import ToolEnvironment


class FakePremiereAdapter:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def probe(self, *, installed: bool) -> PremiereRuntimeProbe:
        return PremiereRuntimeProbe(
            installed=installed,
            bridge_reachable=True,
            plugin_registered=True,
            host_version="26.5.0-test",
            plugin_version="1.0.0",
            capabilities={
                "import media",
                "create sequence",
                "place clip",
                "trim",
                "markers",
                "audio edit",
                "effects",
                "export",
            },
        )

    def sandbox_exercise(
        self,
        *,
        input_media: str | Path,
        output_dir: str | Path,
        timeout_seconds: float = 120.0,
    ) -> PremiereSandboxResult:
        source = Path(input_media)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        export = output_dir / "cinefactory_premiere_mastery.mp4"
        shutil.copy2(source, export)
        provenance = output_dir / "cinefactory_premiere_provenance.json"
        provenance.write_text("{}", encoding="utf-8")
        operations = [
            "import media",
            "create sequence",
            "place clip",
            "trim",
            "markers",
            "audio edit",
            "effects",
            "export",
        ]
        return PremiereSandboxResult(
            project_path=str(output_dir / "mastery.prproj"),
            operation_evidence=[
                PremiereOperationEvidence(
                    operation=operation,
                    passed=True,
                    artifacts=[str(export)] if operation == "export" else [],
                    payload={"test": True},
                )
                for operation in operations
            ],
            export_output=str(export),
            provenance_path=str(provenance),
            cleaned_up=True,
        )


def _seed_ffmpeg_caption_mastery(kernel) -> None:
    required = sorted(
        {
            operation
            for skill in kernel.tool_skills.list("ffmpeg")
            for operation in skill.operations
        }
    )
    kernel.execution_mastery.save(
        ToolExecutionMasteryReport(
            tool_id="ffmpeg",
            skill_id="tool.ffmpeg.post",
            version="1",
            installed=True,
            runtime_available=True,
            sandbox_root="C:/fake/ffmpeg",
            required_operations=required,
            passed_operations=required,
            missing_operations=[],
            execution_coverage=1.0,
            knowledge_coverage=1.0,
            passed=True,
            regression_passed=True,
            operation_evidence=[
                OperationEvidence(
                    operation=operation,
                    passed=True,
                    artifacts=["C:/fake/captions.srt"]
                    if operation == "captions"
                    else [],
                )
                for operation in required
            ],
        )
    )


def test_premiere_mastery_requires_caption_delegation(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="premiere",
            installed=True,
            version="26.5.0-test",
            executable_path="C:/fake/Premiere.exe",
        )
        if tool_id == "premiere"
        else original(tool_id)
    )
    runner = ExecutionMasteryRunner(kernel)
    runner._evaluators["premiere"] = PremiereExecutionEvaluator(
        adapter_factory=lambda root: FakePremiereAdapter(root)
    )
    report = runner.evaluate("premiere", promote_validated=False)
    assert report.passed is False
    assert "captions" in report.missing_operations


def test_premiere_mastery_validates_native_and_delegated_operations(
    tmp_path: Path,
):
    kernel = build_studio_kernel(tmp_path)
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="premiere",
            installed=True,
            version="26.5.0-test",
            executable_path="C:/fake/Premiere.exe",
        )
        if tool_id == "premiere"
        else original(tool_id)
    )
    _seed_ffmpeg_caption_mastery(kernel)
    runner = ExecutionMasteryRunner(kernel)
    runner._evaluators["premiere"] = PremiereExecutionEvaluator(
        adapter_factory=lambda root: FakePremiereAdapter(root)
    )
    report = runner.evaluate("premiere")

    assert report.passed is True
    assert report.execution_coverage == 1.0
    assert report.missing_operations == []
    by_op = {item.operation: item for item in report.operation_evidence}
    assert by_op["captions"].passed is True
    assert by_op["captions"].metadata["delegated_to"] == "ffmpeg"
    assert by_op["export"].metadata["video_streams"] == 1
    assert by_op["export"].metadata["audio_streams"] == 1
    assert (
        kernel.skills.get(
            "tool.premiere.editorial",
            "2026",
        ).status.value
        == "VALIDATED"
    )
