from __future__ import annotations

from pathlib import Path

from cinefactory.executors.unreal import (
    UnrealMasteryFixture,
    UnrealOperationEvidence,
    UnrealRuntimeProbe,
    UnrealSandboxResult,
)
from cinefactory.studio.execution_mastery import (
    ExecutionMasteryRunner,
    UnrealExecutionEvaluator,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.knowledge import ToolEnvironment


class FakeUnrealAdapter:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def probe(self) -> UnrealRuntimeProbe:
        return UnrealRuntimeProbe(
            installed=True,
            editor_path="C:/fake/UnrealEditor.exe",
            command_path="C:/fake/UnrealEditor-Cmd.exe",
            version="Unreal Engine 5.8-test",
            scripting_ready=True,
        )

    def sandbox_exercise(
        self,
        *,
        fixture: UnrealMasteryFixture,
        output_dir: str | Path,
        timeout_seconds: int = 300,
    ) -> UnrealSandboxResult:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        evidence_path = output / "cinefactory_unreal_evidence.json"
        evidence_path.write_text("{}", encoding="utf-8")
        render = output / "render" / "frame0001.png"
        render.parent.mkdir(parents=True, exist_ok=True)
        render.write_bytes(b"fake-render")
        operations = [
            "level assembly",
            "Sequencer",
            "camera",
            "lighting",
            "Movie Render Pipeline",
        ]
        return UnrealSandboxResult(
            operation_evidence=[
                UnrealOperationEvidence(
                    operation=operation,
                    passed=True,
                    artifacts=[str(render)]
                    if operation == "Movie Render Pipeline"
                    else [str(evidence_path)],
                    metadata={"fixture": fixture.model_dump(mode="json")},
                )
                for operation in operations
            ],
            evidence_path=str(evidence_path),
            render_artifacts=[str(render)],
        )


def _fixture(tmp_path: Path) -> UnrealMasteryFixture:
    project = tmp_path / "Mastery.uproject"
    project.write_text("{}", encoding="utf-8")
    return UnrealMasteryFixture(
        project_path=str(project),
        map_name="/Game/CineFactoryMastery/MasteryMap",
        level_sequence="/Game/CineFactoryMastery/MasterySequence.MasterySequence",
        movie_pipeline_config="/Game/CineFactoryMastery/MasteryPreset.MasteryPreset",
    )


def test_unreal_mastery_validates_all_operations(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="unreal",
            installed=True,
            version="5.8-test",
            executable_path="C:/fake/UnrealEditor.exe",
            capabilities={
                "level_assembly",
                "sequencer",
                "camera",
                "lighting",
                "python_scripting",
                "movie_render_pipeline",
            },
        )
        if tool_id == "unreal"
        else original(tool_id)
    )
    runner = ExecutionMasteryRunner(kernel)
    runner._evaluators["unreal"] = UnrealExecutionEvaluator(
        adapter_factory=lambda root: FakeUnrealAdapter(root),
        fixture_provider=lambda root: _fixture(tmp_path),
    )
    report = runner.evaluate("unreal")

    assert report.passed is True
    assert report.execution_coverage == 1.0
    assert report.missing_operations == []
    assert set(report.passed_operations) == {
        "level assembly",
        "Sequencer",
        "camera",
        "lighting",
        "Movie Render Pipeline",
    }
    assert (
        kernel.skills.get(
            "tool.unreal.realtime",
            "5.8",
        ).status.value
        == "VALIDATED"
    )


def test_unreal_requires_runtime_and_mastery_fixture(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    report = ExecutionMasteryRunner(kernel).evaluate(
        "unreal",
        promote_validated=False,
    )
    assert report.passed is False
    assert report.execution_coverage == 0.0
