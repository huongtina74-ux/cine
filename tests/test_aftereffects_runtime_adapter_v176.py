from __future__ import annotations

from pathlib import Path

from cinefactory.adobe.aftereffects import (
    AfterEffectsOperationEvidence,
    AfterEffectsRuntimeProbe,
    AfterEffectsSandboxResult,
)
from cinefactory.studio.execution_mastery import (
    AfterEffectsExecutionEvaluator,
    ExecutionMasteryRunner,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.knowledge import ToolEnvironment


class FakeAfterEffectsAdapter:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def probe(self) -> AfterEffectsRuntimeProbe:
        return AfterEffectsRuntimeProbe(
            installed=True,
            afterfx_path="C:/fake/AfterFX.exe",
            aerender_path="C:/fake/aerender.exe",
            aerender_version="aerender version 26.5-test",
            scripting_ready=True,
        )

    def sandbox_exercise(
        self,
        *,
        output_dir: str | Path,
        timeout_seconds: float = 180.0,
    ) -> AfterEffectsSandboxResult:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        project = output / "mastery.aep"
        render = output / "mastery.avi"
        mogrt = output / "mastery.mogrt"
        evidence_file = output / "evidence.json"
        project.write_bytes(b"fake-aep")
        render.write_bytes(b"fake-render")
        mogrt.write_bytes(b"fake-mogrt")
        evidence_file.write_text("{}", encoding="utf-8")
        operations = [
            "compositions",
            "layers",
            "keyframes",
            "expressions",
            "templates",
            "render queue",
        ]
        return AfterEffectsSandboxResult(
            project_path=str(project),
            render_output=str(render),
            mogrt_path=str(mogrt),
            evidence_path=str(evidence_file),
            operation_evidence=[
                AfterEffectsOperationEvidence(
                    operation=operation,
                    passed=True,
                    artifacts=[
                        str(render)
                        if operation == "render queue"
                        else str(mogrt)
                    ]
                    if operation in {"render queue", "templates"}
                    else [],
                    metadata={"test": True},
                )
                for operation in operations
            ],
            cleaned_up=True,
        )


def test_aftereffects_mastery_validates_all_operations(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="aftereffects",
            installed=True,
            version="26.5-test",
            executable_path="C:/fake/AfterFX.exe",
            capabilities={
                "compositions",
                "layers",
                "keyframes",
                "expressions",
                "templates",
                "render_queue",
            },
        )
        if tool_id == "aftereffects"
        else original(tool_id)
    )
    runner = ExecutionMasteryRunner(kernel)
    runner._evaluators["aftereffects"] = AfterEffectsExecutionEvaluator(
        adapter_factory=lambda root: FakeAfterEffectsAdapter(root)
    )
    report = runner.evaluate("aftereffects")

    assert report.passed is True
    assert report.execution_coverage == 1.0
    assert report.missing_operations == []
    assert set(report.passed_operations) == {
        "compositions",
        "layers",
        "keyframes",
        "expressions",
        "templates",
        "render queue",
    }
    assert (
        kernel.skills.get(
            "tool.aftereffects.motion",
            "2026",
        ).status.value
        == "VALIDATED"
    )


def test_aftereffects_real_adapter_requires_runtime(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    probe = kernel.tool_adapters.probe(kernel, "aftereffects")
    assert probe.available is False
    assert probe.runtime_required is True
    assert probe.runtime_reachable is False
