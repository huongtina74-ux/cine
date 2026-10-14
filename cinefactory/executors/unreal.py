from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class UnrealRuntimeProbe(BaseModel):
    installed: bool
    editor_path: str | None = None
    command_path: str | None = None
    version: str | None = None
    scripting_ready: bool = False
    findings: list[str] = Field(default_factory=list)


class UnrealMasteryFixture(BaseModel):
    project_path: str
    map_name: str
    level_sequence: str
    movie_pipeline_config: str


class UnrealOperationEvidence(BaseModel):
    operation: str
    passed: bool
    duration_ms: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)


class UnrealSandboxResult(BaseModel):
    operation_evidence: list[UnrealOperationEvidence] = Field(default_factory=list)
    evidence_path: str | None = None
    render_artifacts: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class UnrealRuntimeAdapter:
    SUPPORTED_OPERATIONS = {
        "level assembly",
        "Sequencer",
        "camera",
        "lighting",
        "Movie Render Pipeline",
    }

    def __init__(
        self,
        root: str | Path,
        *,
        editor_path: str | None = None,
        command_path: str | None = None,
    ) -> None:
        self.root = Path(root)
        self._editor_path = editor_path
        self._command_path = command_path

    def discover(self) -> tuple[Path | None, Path | None]:
        if self._editor_path:
            editor = Path(self._editor_path)
        else:
            program_files = Path(
                os.environ.get("ProgramFiles", r"C:\Program Files")
            )
            candidates = sorted(
                (
                    program_files / "Epic Games"
                ).glob("UE_*/Engine/Binaries/Win64/UnrealEditor.exe"),
                reverse=True,
            )
            editor = candidates[0] if candidates else None

        if self._command_path:
            command = Path(self._command_path)
        elif editor is not None:
            candidate = editor.parent / "UnrealEditor-Cmd.exe"
            command = candidate if candidate.is_file() else None
        else:
            command = None
        return (
            editor if editor is not None and editor.is_file() else None,
            command if command is not None and command.is_file() else None,
        )

    def probe(self) -> UnrealRuntimeProbe:
        editor, command = self.discover()
        findings: list[str] = []
        if editor is None:
            findings.append("UNREAL_EDITOR_NOT_FOUND")
        if command is None:
            findings.append("UNREAL_EDITOR_CMD_NOT_FOUND")
        version = None
        if command is not None:
            try:
                proc = subprocess.run(
                    [str(command), "-version"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                lines = (proc.stdout or proc.stderr or "").strip().splitlines()
                version = lines[0][:200] if lines else None
            except Exception as exc:
                findings.append(
                    f"UNREAL_VERSION_PROBE_FAILED:{type(exc).__name__}:{exc}"
                )
        return UnrealRuntimeProbe(
            installed=editor is not None,
            editor_path=str(editor) if editor else None,
            command_path=str(command) if command else None,
            version=version,
            scripting_ready=bool(editor and command),
            findings=findings,
        )

    @staticmethod
    def _python_script(evidence_path: Path) -> str:
        evidence = json.dumps(str(evidence_path).replace("\\", "/"))
        return f"""import json
import traceback
import unreal

OUT = {evidence}
results = {{}}

def record(name, fn):
    try:
        metadata = fn() or {{}}
        results[name] = {{"passed": True, "metadata": metadata, "findings": []}}
    except Exception as exc:
        results[name] = {{
            "passed": False,
            "metadata": {{}},
            "findings": [type(exc).__name__ + ":" + str(exc), traceback.format_exc()[-1200:]],
        }}

state = {{}}

def level_assembly():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if level_subsystem is None:
        raise RuntimeError("LevelEditorSubsystem unavailable")
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if actor_subsystem is None:
        raise RuntimeError("EditorActorSubsystem unavailable")
    actor = actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        unreal.Vector(0.0, 0.0, 0.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    if actor is None:
        raise RuntimeError("failed to spawn StaticMeshActor")
    actor.set_actor_label("CineFactory_Master_Actor")
    state["actor"] = actor
    return {{"actor": actor.get_actor_label()}}

def sequencer():
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.LevelSequenceFactoryNew()
    sequence = tools.create_asset(
        "CineFactory_Master_Sequence",
        "/Game/CineFactoryMastery",
        unreal.LevelSequence,
        factory,
    )
    if sequence is None:
        raise RuntimeError("failed to create LevelSequence")
    sequence.set_display_rate(unreal.FrameRate(24, 1))
    state["sequence"] = sequence
    return {{"sequence": sequence.get_path_name()}}

def camera():
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    camera = actor_subsystem.spawn_actor_from_class(
        unreal.CineCameraActor,
        unreal.Vector(300.0, -300.0, 200.0),
        unreal.Rotator(-15.0, -45.0, 0.0),
    )
    if camera is None:
        raise RuntimeError("failed to spawn CineCameraActor")
    camera.set_actor_label("CineFactory_Master_Camera")
    sequence = state.get("sequence")
    binding = sequence.add_possessable(camera) if sequence else None
    state["camera"] = camera
    return {{
        "camera": camera.get_actor_label(),
        "bound": binding is not None,
    }}

def lighting():
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    light = actor_subsystem.spawn_actor_from_class(
        unreal.PointLight,
        unreal.Vector(0.0, 0.0, 300.0),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    if light is None:
        raise RuntimeError("failed to spawn PointLight")
    light.set_actor_label("CineFactory_Master_Light")
    component = light.get_component_by_class(unreal.PointLightComponent)
    if component:
        component.set_editor_property("intensity", 1500.0)
    return {{"light": light.get_actor_label()}}

record("level assembly", level_assembly)
record("Sequencer", sequencer)
record("camera", camera)
record("lighting", lighting)

with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(results, handle, indent=2, default=str)
"""

    def run_editor_sandbox(
        self,
        *,
        fixture: UnrealMasteryFixture,
        output_dir: str | Path,
        timeout_seconds: int = 180,
    ) -> tuple[list[UnrealOperationEvidence], Path]:
        runtime = self.probe()
        if not runtime.scripting_ready:
            return (
                [
                    UnrealOperationEvidence(
                        operation=operation,
                        passed=False,
                        findings=["UNREAL_RUNTIME_UNAVAILABLE"],
                    )
                    for operation in (
                        "level assembly",
                        "Sequencer",
                        "camera",
                        "lighting",
                    )
                ],
                Path(output_dir) / "cinefactory_unreal_evidence.json",
            )
        project = Path(fixture.project_path)
        if not project.is_file():
            raise FileNotFoundError(project)
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        evidence_path = output / "cinefactory_unreal_evidence.json"
        script_path = output / "cinefactory_unreal_mastery.py"
        script_path.write_text(
            self._python_script(evidence_path),
            encoding="utf-8",
        )
        started = time.perf_counter()
        proc = subprocess.run(
            [
                str(runtime.command_path),
                str(project),
                f"-ExecutePythonScript={script_path}",
                "-unattended",
                "-nop4",
                "-nosplash",
                "-nullrhi",
            ],
            cwd=output,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        elapsed = max(0, int((time.perf_counter() - started) * 1000))
        if not evidence_path.is_file():
            finding = (
                f"UNREAL_PYTHON_EXIT_{proc.returncode}:"
                + (proc.stderr or proc.stdout or "")[-1200:]
            )
            return (
                [
                    UnrealOperationEvidence(
                        operation=operation,
                        passed=False,
                        duration_ms=elapsed,
                        findings=[finding],
                    )
                    for operation in (
                        "level assembly",
                        "Sequencer",
                        "camera",
                        "lighting",
                    )
                ],
                evidence_path,
            )
        raw = json.loads(evidence_path.read_text(encoding="utf-8"))
        evidence = []
        for operation in (
            "level assembly",
            "Sequencer",
            "camera",
            "lighting",
        ):
            item = raw.get(operation, {})
            evidence.append(
                UnrealOperationEvidence(
                    operation=operation,
                    passed=bool(item.get("passed")),
                    duration_ms=elapsed,
                    metadata=dict(item.get("metadata", {})),
                    findings=list(item.get("findings", [])),
                    artifacts=[str(evidence_path)],
                )
            )
        return evidence, evidence_path

    def render_mrq(
        self,
        *,
        fixture: UnrealMasteryFixture,
        output_dir: str | Path,
        timeout_seconds: int = 300,
    ) -> UnrealOperationEvidence:
        runtime = self.probe()
        if not runtime.scripting_ready:
            return UnrealOperationEvidence(
                operation="Movie Render Pipeline",
                passed=False,
                findings=["UNREAL_RUNTIME_UNAVAILABLE"],
            )
        project = Path(fixture.project_path)
        if not project.is_file():
            return UnrealOperationEvidence(
                operation="Movie Render Pipeline",
                passed=False,
                findings=["UNREAL_PROJECT_MISSING"],
            )
        output = Path(output_dir).resolve()
        output.mkdir(parents=True, exist_ok=True)
        before = {
            path.resolve()
            for path in output.rglob("*")
            if path.is_file()
        }
        started = time.perf_counter()
        proc = subprocess.run(
            [
                str(runtime.command_path),
                str(project),
                fixture.map_name,
                "-game",
                f"-LevelSequence={fixture.level_sequence}",
                f"-MoviePipelineConfig={fixture.movie_pipeline_config}",
                "-unattended",
                "-nop4",
                "-nosplash",
                "-windowed",
                "-resx=320",
                "-resy=180",
                "-log",
                "-notexturestreaming",
            ],
            cwd=output,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        duration = max(0, int((time.perf_counter() - started) * 1000))
        after = {
            path.resolve()
            for path in output.rglob("*")
            if path.is_file() and path.stat().st_size > 0
        }
        artifacts = sorted(str(path) for path in (after - before))
        passed = proc.returncode == 0 and bool(artifacts)
        return UnrealOperationEvidence(
            operation="Movie Render Pipeline",
            passed=passed,
            duration_ms=duration,
            artifacts=artifacts,
            findings=[] if passed else [
                f"UNREAL_MRQ_EXIT_{proc.returncode}",
                (proc.stderr or proc.stdout or "")[-1500:],
            ],
            metadata={
                "map": fixture.map_name,
                "level_sequence": fixture.level_sequence,
                "movie_pipeline_config": fixture.movie_pipeline_config,
            },
        )

    def sandbox_exercise(
        self,
        *,
        fixture: UnrealMasteryFixture,
        output_dir: str | Path,
        timeout_seconds: int = 300,
    ) -> UnrealSandboxResult:
        evidence, evidence_path = self.run_editor_sandbox(
            fixture=fixture,
            output_dir=output_dir,
            timeout_seconds=min(timeout_seconds, 180),
        )
        if all(item.passed for item in evidence):
            evidence.append(
                self.render_mrq(
                    fixture=fixture,
                    output_dir=Path(output_dir) / "render",
                    timeout_seconds=timeout_seconds,
                )
            )
        else:
            evidence.append(
                UnrealOperationEvidence(
                    operation="Movie Render Pipeline",
                    passed=False,
                    findings=["EDITOR_SANDBOX_PREREQUISITE_FAILED"],
                )
            )
        render_artifacts = [
            artifact
            for item in evidence
            if item.operation == "Movie Render Pipeline"
            for artifact in item.artifacts
        ]
        return UnrealSandboxResult(
            operation_evidence=evidence,
            evidence_path=str(evidence_path),
            render_artifacts=render_artifacts,
        )
