from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from pydantic import BaseModel, Field


class AfterEffectsRuntimeProbe(BaseModel):
    installed: bool
    afterfx_path: str | None = None
    aerender_path: str | None = None
    aerender_version: str | None = None
    scripting_ready: bool = False
    findings: list[str] = Field(default_factory=list)


class AfterEffectsOperationEvidence(BaseModel):
    operation: str
    passed: bool
    duration_ms: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)


class AfterEffectsSandboxResult(BaseModel):
    project_path: str | None = None
    render_output: str | None = None
    mogrt_path: str | None = None
    evidence_path: str | None = None
    operation_evidence: list[AfterEffectsOperationEvidence] = Field(default_factory=list)
    cleaned_up: bool = False
    findings: list[str] = Field(default_factory=list)


class AfterEffectsRuntimeAdapter:
    SUPPORTED_OPERATIONS = {
        "compositions",
        "layers",
        "keyframes",
        "expressions",
        "templates",
        "render queue",
    }

    def __init__(
        self,
        root: str | Path,
        *,
        afterfx_path: str | None = None,
        aerender_path: str | None = None,
    ) -> None:
        self.root = Path(root)
        self._afterfx_path = afterfx_path
        self._aerender_path = aerender_path

    def discover(self) -> tuple[Path | None, Path | None]:
        if self._afterfx_path:
            afterfx = Path(self._afterfx_path)
        else:
            program_files = Path(
                os.environ.get("ProgramFiles", r"C:\Program Files")
            )
            candidates = sorted(
                (
                    program_files
                    / "Adobe"
                ).glob("Adobe After Effects */Support Files/AfterFX.exe"),
                reverse=True,
            )
            afterfx = candidates[0] if candidates else None

        if self._aerender_path:
            aerender = Path(self._aerender_path)
        elif afterfx is not None:
            candidate = afterfx.parent / "aerender.exe"
            aerender = candidate if candidate.is_file() else None
        else:
            aerender = None
        return (
            afterfx if afterfx is not None and afterfx.is_file() else None,
            aerender if aerender is not None and aerender.is_file() else None,
        )

    def probe(self) -> AfterEffectsRuntimeProbe:
        afterfx, aerender = self.discover()
        findings: list[str] = []
        if afterfx is None:
            findings.append("AFTERFX_NOT_FOUND")
        if aerender is None:
            findings.append("AERENDER_NOT_FOUND")
        version = None
        if aerender is not None:
            try:
                proc = subprocess.run(
                    [str(aerender), "-version"],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=False,
                )
                lines = (proc.stdout or proc.stderr or "").strip().splitlines()
                version = lines[0][:200] if lines else None
                if proc.returncode != 0:
                    findings.append(f"AERENDER_VERSION_EXIT_{proc.returncode}")
            except Exception as exc:
                findings.append(
                    f"AERENDER_VERSION_FAILED:{type(exc).__name__}:{exc}"
                )
        return AfterEffectsRuntimeProbe(
            installed=afterfx is not None,
            afterfx_path=str(afterfx) if afterfx else None,
            aerender_path=str(aerender) if aerender else None,
            aerender_version=version,
            scripting_ready=bool(afterfx and aerender),
            findings=findings,
        )

    @staticmethod
    def _js_string(value: str | Path) -> str:
        return json.dumps(str(value).replace("\\", "/"))

    def _mastery_script(
        self,
        *,
        project_path: Path,
        evidence_path: Path,
        render_output: Path,
        mogrt_dir: Path,
        comp_name: str,
    ) -> str:
        p_project = self._js_string(project_path)
        p_evidence = self._js_string(evidence_path)
        p_render = self._js_string(render_output)
        p_mogrt_dir = self._js_string(mogrt_dir)
        p_comp = json.dumps(comp_name)
        return f"""(function () {{
    function writeEvidence(obj) {{
        var f = new File({p_evidence});
        f.encoding = "UTF-8";
        if (!f.open("w")) throw new Error("Cannot open evidence file");
        f.write(JSON.stringify(obj, null, 2));
        f.close();
    }}

    var evidence = {{}};
    try {{
        if (app.project) {{
            try {{ app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); }} catch (_) {{}}
        }}
        app.newProject();
        var comp = app.project.items.addComp({p_comp}, 320, 180, 1.0, 2.0, 24.0);
        evidence["compositions"] = {{
            passed: !!comp && comp.width === 320 && comp.height === 180,
            metadata: {{name: comp.name, width: comp.width, height: comp.height, frameRate: comp.frameRate}}
        }};

        var solid = comp.layers.addSolid([0.25, 0.25, 0.25], "CineFactory Solid", 320, 180, 1.0, 2.0);
        var text = comp.layers.addText("CineFactory");
        evidence["layers"] = {{
            passed: comp.numLayers >= 2,
            metadata: {{numLayers: comp.numLayers}}
        }};

        var position = solid.property("ADBE Transform Group").property("ADBE Position");
        position.setValueAtTime(0.0, [120, 90]);
        position.setValueAtTime(1.0, [200, 90]);
        evidence["keyframes"] = {{
            passed: position.numKeys >= 2,
            metadata: {{numKeys: position.numKeys}}
        }};

        var opacity = text.property("ADBE Transform Group").property("ADBE Opacity");
        opacity.expression = "50 + 50*Math.sin(time*3)";
        evidence["expressions"] = {{
            passed: opacity.expressionEnabled && opacity.expression.length > 0,
            metadata: {{expression: opacity.expression, expressionError: opacity.expressionError || ""}}
        }};

        app.project.save(new File({p_project}));
        comp.motionGraphicsTemplateName = "CineFactory_Mastery_Template";
        var mogrtOk = false;
        try {{
            mogrtOk = comp.exportAsMotionGraphicsTemplate(true, {p_mogrt_dir});
        }} catch (mogrtError) {{
            mogrtOk = false;
        }}
        evidence["templates"] = {{
            passed: !!mogrtOk,
            metadata: {{
                name: comp.motionGraphicsTemplateName,
                controllerCount: comp.motionGraphicsTemplateControllerCount
            }}
        }};

        var rq = app.project.renderQueue.items.add(comp);
        rq.outputModule(1).file = new File({p_render});
        evidence["render queue"] = {{
            passed: !!rq && rq.outputModule(1).file !== null,
            metadata: {{queueItem: rq.index, output: rq.outputModule(1).file.fsName}}
        }};

        app.project.save(new File({p_project}));
        writeEvidence(evidence);
        app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
    }} catch (err) {{
        evidence["_fatal"] = {{
            passed: false,
            findings: [String(err), String(err.line || "")]
        }};
        try {{ writeEvidence(evidence); }} catch (_) {{}}
        try {{ app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); }} catch (_) {{}}
    }}
}})();
"""

    @staticmethod
    def _wait_for(path: Path, timeout_seconds: float) -> bool:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if path.is_file() and path.stat().st_size > 0:
                return True
            time.sleep(0.25)
        return False

    def sandbox_exercise(
        self,
        *,
        output_dir: str | Path,
        timeout_seconds: float = 180.0,
    ) -> AfterEffectsSandboxResult:
        runtime = self.probe()
        if not runtime.scripting_ready:
            return AfterEffectsSandboxResult(
                findings=[
                    "AFTER_EFFECTS_RUNTIME_UNAVAILABLE",
                    *runtime.findings,
                ],
            )

        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        mogrt_dir = output / "mogrt"
        mogrt_dir.mkdir(parents=True, exist_ok=True)
        project_path = output / "cinefactory_aftereffects_mastery.aep"
        evidence_path = output / "cinefactory_aftereffects_evidence.json"
        render_output = output / "cinefactory_aftereffects_mastery.avi"
        script_path = output / "cinefactory_aftereffects_mastery.jsx"
        comp_name = f"CineFactory Mastery {uuid4().hex[:8]}"
        script_path.write_text(
            self._mastery_script(
                project_path=project_path,
                evidence_path=evidence_path,
                render_output=render_output,
                mogrt_dir=mogrt_dir,
                comp_name=comp_name,
            ),
            encoding="utf-8",
        )

        findings: list[str] = []
        try:
            subprocess.Popen(
                [str(runtime.afterfx_path)],
                cwd=output,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(3)
            subprocess.run(
                [
                    str(runtime.afterfx_path),
                    "-r",
                    str(script_path),
                ],
                cwd=output,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except Exception as exc:
            findings.append(
                f"AFTERFX_SCRIPT_LAUNCH_FAILED:{type(exc).__name__}:{exc}"
            )

        if not self._wait_for(evidence_path, min(timeout_seconds, 60)):
            return AfterEffectsSandboxResult(
                project_path=str(project_path) if project_path.is_file() else None,
                evidence_path=str(evidence_path),
                findings=[
                    *findings,
                    "AE_EVIDENCE_MISSING:enable scripting file/network access and verify afterfx -r",
                ],
            )

        raw = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence: list[AfterEffectsOperationEvidence] = []
        for operation in sorted(self.SUPPORTED_OPERATIONS):
            item = raw.get(operation, {})
            evidence.append(
                AfterEffectsOperationEvidence(
                    operation=operation,
                    passed=bool(item.get("passed")),
                    metadata=dict(item.get("metadata", {})),
                    findings=list(item.get("findings", [])),
                    artifacts=[],
                )
            )

        render_item = next(
            (item for item in evidence if item.operation == "render queue"),
            None,
        )
        if render_item is not None and render_item.passed:
            started = time.perf_counter()
            proc = subprocess.run(
                [
                    str(runtime.aerender_path),
                    "-project",
                    str(project_path),
                    "-comp",
                    comp_name,
                    "-output",
                    str(render_output),
                    "-v",
                    "ERRORS_AND_PROGRESS",
                ],
                cwd=output,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            render_item.duration_ms = max(
                0,
                int((time.perf_counter() - started) * 1000),
            )
            rendered = (
                proc.returncode == 0
                and render_output.is_file()
                and render_output.stat().st_size > 0
            )
            render_item.passed = render_item.passed and rendered
            if rendered:
                render_item.artifacts.append(str(render_output))
            else:
                render_item.findings.extend(
                    [
                        f"AERENDER_EXIT_{proc.returncode}",
                        (proc.stderr or proc.stdout or "")[-1200:],
                    ]
                )

        mogrt_files = sorted(mogrt_dir.glob("*.mogrt"))
        template_item = next(
            (item for item in evidence if item.operation == "templates"),
            None,
        )
        if template_item is not None:
            template_item.passed = (
                template_item.passed
                and bool(mogrt_files)
                and all(path.stat().st_size > 0 for path in mogrt_files)
            )
            template_item.artifacts.extend(str(path) for path in mogrt_files)
            if not mogrt_files:
                template_item.findings.append("MOGRT_OUTPUT_MISSING")

        provenance_path = output / "cinefactory_aftereffects_provenance.json"
        provenance = {
            "adapter": "afterfx-extendscript+aerender",
            "aerender_version": runtime.aerender_version,
            "project_path": str(project_path),
            "render_output": str(render_output) if render_output.is_file() else None,
            "mogrt_files": [str(path) for path in mogrt_files],
            "operations": [
                item.model_dump(mode="json") for item in evidence
            ],
        }
        provenance_path.write_text(
            json.dumps(
                provenance,
                ensure_ascii=False,
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return AfterEffectsSandboxResult(
            project_path=str(project_path) if project_path.is_file() else None,
            render_output=str(render_output) if render_output.is_file() else None,
            mogrt_path=str(mogrt_files[0]) if mogrt_files else None,
            evidence_path=str(evidence_path),
            operation_evidence=evidence,
            cleaned_up=True,
            findings=findings,
        )
