from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from cinefactory.canva.runtime import (
    CanvaMasteryFixture,
    CanvaOperationEvidence,
    CanvaRuntimeProbe,
    CanvaSandboxResult,
)
from cinefactory.studio.execution_mastery import (
    CanvaExecutionEvaluator,
    ExecutionMasteryRunner,
)
from cinefactory.studio.kernel import build_studio_kernel


class FakeCanvaAdapter:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def probe(self) -> CanvaRuntimeProbe:
        return CanvaRuntimeProbe(
            authorized=True,
            user_id="user-test",
            team_id="team-test",
            capabilities={
                "brand_template",
                "autofill",
                "resize",
                "export",
            },
        )

    def sandbox_exercise(
        self,
        *,
        fixture: CanvaMasteryFixture,
        output_dir: str | Path,
        timeout_seconds: float = 120.0,
    ) -> CanvaSandboxResult:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        exported = output / "canva_export_1.png"
        exported.write_bytes(b"fake-canva-export")
        provenance = output / "cinefactory_canva_provenance.json"
        provenance.write_text("{}", encoding="utf-8")
        operations = [
            "brand template",
            "text replacement",
            "asset replacement",
            "social derivative",
            "export",
        ]
        return CanvaSandboxResult(
            operation_evidence=[
                CanvaOperationEvidence(
                    operation=operation,
                    passed=True,
                    artifacts=[str(exported)]
                    if operation == "export"
                    else [],
                    metadata={
                        "test": True,
                        "fixture": fixture.model_dump(mode="json"),
                    },
                )
                for operation in operations
            ],
            provenance_path=str(provenance),
        )


def _fixture() -> CanvaMasteryFixture:
    return CanvaMasteryFixture(
        brand_template_id="template-test",
        text_field="headline",
        image_field="hero",
        asset_id="asset-test",
        design_id="design-test",
    )


def test_canva_mastery_validates_all_operations(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original_probe = kernel.tool_adapters.probe
    kernel.tool_adapters.probe = lambda current_kernel, tool_id: (
        SimpleNamespace(runtime_reachable=True)
        if tool_id == "canva"
        else original_probe(current_kernel, tool_id)
    )

    runner = ExecutionMasteryRunner(kernel)
    runner._evaluators["canva"] = CanvaExecutionEvaluator(
        adapter_factory=lambda root: FakeCanvaAdapter(root),
        fixture_provider=lambda root: _fixture(),
    )
    report = runner.evaluate("canva")

    assert report.runtime_available is True
    assert report.passed is True
    assert report.execution_coverage == 1.0
    assert report.missing_operations == []
    assert set(report.passed_operations) == {
        "brand template",
        "text replacement",
        "asset replacement",
        "social derivative",
        "export",
    }
    assert (
        kernel.skills.get(
            "tool.canva.packaging",
            "2026",
        ).status.value
        == "VALIDATED"
    )


def test_canva_real_adapter_is_fail_closed_without_oauth(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    probe = kernel.tool_adapters.probe(kernel, "canva")
    assert probe.available is False
    assert probe.runtime_required is True
    assert probe.runtime_reachable is False
    assert "ADAPTER_EXTERNAL_CONFIGURATION_REQUIRED" in probe.findings
    assert any(
        "CANVA_ACCESS_TOKEN_MISSING" in finding
        for finding in probe.findings
    )


def test_canva_mastery_requires_explicit_fixture(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    original_probe = kernel.tool_adapters.probe
    kernel.tool_adapters.probe = lambda current_kernel, tool_id: (
        SimpleNamespace(runtime_reachable=True)
        if tool_id == "canva"
        else original_probe(current_kernel, tool_id)
    )
    runner = ExecutionMasteryRunner(kernel)
    runner._evaluators["canva"] = CanvaExecutionEvaluator(
        adapter_factory=lambda root: FakeCanvaAdapter(root),
        fixture_provider=lambda root: None,
    )
    report = runner.evaluate("canva", promote_validated=False)
    assert report.passed is False
    assert report.execution_coverage == 0.0
    assert report.missing_operations == [
        "asset replacement",
        "brand template",
        "export",
        "social derivative",
        "text replacement",
    ]
