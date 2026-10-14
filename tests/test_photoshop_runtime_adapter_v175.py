from __future__ import annotations

from pathlib import Path

from cinefactory.adobe.photoshop import (
    PhotoshopOperationEvidence,
    PhotoshopRuntimeProbe,
    PhotoshopSandboxResult,
)
from cinefactory.studio.execution_mastery import (
    ExecutionMasteryRunner,
    PhotoshopExecutionEvaluator,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.knowledge import ToolEnvironment


class FakePhotoshopAdapter:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def probe(self, *, installed: bool) -> PhotoshopRuntimeProbe:
        return PhotoshopRuntimeProbe(
            installed=installed,
            bridge_reachable=True,
            plugin_registered=True,
            host_version="27.0-test",
            plugin_version="1.0.0",
            capabilities={
                "layers",
                "masks",
                "smart objects",
                "text",
                "composite",
                "thumbnail",
                "batch export",
            },
        )

    def sandbox_exercise(
        self,
        *,
        output_dir: str | Path,
        timeout_seconds: float = 90.0,
    ) -> PhotoshopSandboxResult:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        png = output / "mastery.png"
        psd = output / "mastery.psd"
        png.write_bytes(b"fake-png")
        psd.write_bytes(b"fake-psd")
        provenance = output / "cinefactory_photoshop_provenance.json"
        provenance.write_text("{}", encoding="utf-8")
        operations = [
            "layers",
            "masks",
            "smart objects",
            "text",
            "composite",
            "thumbnail",
            "batch export",
        ]
        return PhotoshopSandboxResult(
            operation_evidence=[
                PhotoshopOperationEvidence(
                    operation=operation,
                    passed=True,
                    artifacts=[str(png), str(psd)]
                    if operation == "batch export"
                    else [],
                    payload={"test": True},
                )
                for operation in operations
            ],
            exported_files=[str(png), str(psd)],
            provenance_path=str(provenance),
            cleaned_up=True,
        )


def test_photoshop_mastery_validates_all_operations(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="photoshop",
            installed=True,
            version="27.0-test",
            executable_path="C:/fake/Photoshop.exe",
        )
        if tool_id == "photoshop"
        else original(tool_id)
    )
    runner = ExecutionMasteryRunner(kernel)
    runner._evaluators["photoshop"] = PhotoshopExecutionEvaluator(
        adapter_factory=lambda root: FakePhotoshopAdapter(root)
    )
    report = runner.evaluate("photoshop")

    assert report.passed is True
    assert report.execution_coverage == 1.0
    assert report.missing_operations == []
    assert set(report.passed_operations) == {
        "layers",
        "masks",
        "smart objects",
        "text",
        "composite",
        "thumbnail",
        "batch export",
    }
    assert (
        kernel.skills.get(
            "tool.photoshop.image",
            "2026",
        ).status.value
        == "VALIDATED"
    )


def test_photoshop_real_adapter_requires_bridge_runtime(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original = kernel.tool_doctor.inspect
    kernel.tool_doctor.inspect = lambda tool_id: (
        ToolEnvironment(
            tool_id="photoshop",
            installed=True,
            version="27.0-test",
            executable_path="C:/fake/Photoshop.exe",
        )
        if tool_id == "photoshop"
        else original(tool_id)
    )
    probe = kernel.tool_adapters.probe(kernel, "photoshop")
    assert probe.available is False
    assert probe.runtime_required is True
    assert any(
        finding in {
            "ADOBE_BRIDGE_TOKEN_MISSING",
            "ADOBE_PLUGIN_CLIENT_NOT_REGISTERED",
        }
        or finding.startswith("ADOBE_BRIDGE_UNREACHABLE:")
        for finding in probe.findings
    )
