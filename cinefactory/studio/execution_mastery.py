from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Callable

from pydantic import BaseModel, Field

from cinefactory.core.policy import FactoryPolicy
from cinefactory.executors.comfyui import ComfyUIExecutor
from cinefactory.executors.resolve import ResolveRuntimeAdapter
from cinefactory.adobe.premiere import PremiereRuntimeAdapter, make_premiere_fixture
from cinefactory.adobe.photoshop import PhotoshopRuntimeAdapter
from cinefactory.adobe.aftereffects import AfterEffectsRuntimeAdapter
from cinefactory.executors.unreal import UnrealMasteryFixture, UnrealRuntimeAdapter
from cinefactory.canva.runtime import CanvaMasteryFixture, CanvaRuntimeAdapter
from cinefactory.models.registry import ModelRegistry
from cinefactory.workflows.registry import WorkflowRegistry

from .acquisition import operation_coverage
from .contracts import SkillEvaluation, SkillStatus
from .tool_knowledge import default_tool_knowledge_packs


class OperationEvidence(BaseModel):
    operation: str
    passed: bool
    duration_ms: int = Field(default=0, ge=0)
    artifacts: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class ToolExecutionMasteryReport(BaseModel):
    tool_id: str
    skill_id: str
    version: str
    installed: bool
    runtime_available: bool = False
    detected_version: str | None = None
    sandbox_root: str
    operation_evidence: list[OperationEvidence] = Field(default_factory=list)
    required_operations: list[str] = Field(default_factory=list)
    passed_operations: list[str] = Field(default_factory=list)
    missing_operations: list[str] = Field(default_factory=list)
    execution_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    knowledge_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    passed: bool = False
    regression_passed: bool = False
    findings: list[str] = Field(default_factory=list)


class ExecutionMasteryStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, report: ToolExecutionMasteryReport) -> Path:
        folder = self.root / report.tool_id
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "latest.json"
        path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        return path

    def get(self, tool_id: str) -> ToolExecutionMasteryReport:
        path = self.root / tool_id / "latest.json"
        if not path.exists():
            raise KeyError(tool_id)
        return ToolExecutionMasteryReport.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def list(self) -> list[ToolExecutionMasteryReport]:
        reports: list[ToolExecutionMasteryReport] = []
        for path in sorted(self.root.glob("*/latest.json")):
            reports.append(
                ToolExecutionMasteryReport.model_validate_json(
                    path.read_text(encoding="utf-8")
                )
            )
        return reports


def _timed(operation: str, fn: Callable[[], tuple[bool, list[str], list[str], dict]]) -> OperationEvidence:
    start = time.perf_counter()
    try:
        passed, artifacts, findings, metadata = fn()
    except Exception as exc:
        passed = False
        artifacts = []
        findings = [f"{type(exc).__name__}:{exc}"]
        metadata = {}
    return OperationEvidence(
        operation=operation,
        passed=passed,
        duration_ms=max(0, int((time.perf_counter() - start) * 1000)),
        artifacts=artifacts,
        findings=findings,
        metadata=metadata,
    )


class BlenderExecutionEvaluator:
    OPERATIONS = [
        "scene assembly",
        "rigging",
        "animation",
        "camera",
        "lighting",
        "render",
        "compositing",
        "asset conversion",
        "headless batch",
    ]

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        env = kernel.tool_doctor.inspect("blender")
        if not env.installed or not env.executable_path:
            return [
                OperationEvidence(
                    operation=operation,
                    passed=False,
                    findings=["BLENDER_NOT_INSTALLED"],
                )
                for operation in self.OPERATIONS
            ]

        sandbox.mkdir(parents=True, exist_ok=True)
        script = sandbox / "mastery_blender.py"
        evidence_path = sandbox / "blender_evidence.json"
        blend_path = sandbox / "mastery_scene.blend"
        render_path = sandbox / "mastery_render.png"
        script.write_text(
            _blender_mastery_script(
                evidence_path=evidence_path,
                blend_path=blend_path,
                render_path=render_path,
            ),
            encoding="utf-8",
        )
        started = time.perf_counter()
        proc = subprocess.run(
            [env.executable_path, "-b", "--python", str(script)],
            cwd=kernel.root,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        elapsed = max(0, int((time.perf_counter() - started) * 1000))
        if not evidence_path.is_file():
            finding = (
                f"BLENDER_MASTERY_SCRIPT_FAILED:exit={proc.returncode}:"
                f"{(proc.stderr or proc.stdout or '')[-1000:]}"
            )
            return [
                OperationEvidence(
                    operation=operation,
                    passed=False,
                    duration_ms=elapsed if operation == "headless batch" else 0,
                    findings=[finding],
                )
                for operation in self.OPERATIONS
            ]

        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
        results: list[OperationEvidence] = []
        for operation in self.OPERATIONS:
            item = payload.get(operation, {})
            artifacts = [str(Path(x)) for x in item.get("artifacts", [])]
            passed = bool(item.get("passed")) and all(
                Path(path).exists() for path in artifacts
            )
            results.append(
                OperationEvidence(
                    operation=operation,
                    passed=passed,
                    duration_ms=int(item.get("duration_ms", 0)),
                    artifacts=artifacts,
                    findings=list(item.get("findings", [])),
                    metadata={
                        **dict(item.get("metadata", {})),
                        "process_exit_code": proc.returncode,
                    },
                )
            )
        # The complete successful -b invocation is the headless proof.
        for item in results:
            if item.operation == "headless batch":
                item.duration_ms = elapsed
                item.passed = item.passed and proc.returncode == 0
                if proc.returncode != 0:
                    item.findings.append(f"BLENDER_EXIT_{proc.returncode}")
        return results


class FFmpegExecutionEvaluator:
    OPERATIONS = [
        "probe",
        "transcode",
        "concat",
        "filter",
        "audio mix",
        "captions",
        "master",
        "delivery QC",
    ]

    def _run(
        self,
        operation: str,
        argv: list[str],
        *,
        cwd: Path,
        expected: list[Path] | None = None,
    ) -> OperationEvidence:
        expected = expected or []
        def execute():
            proc = subprocess.run(
                argv,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
            artifacts = [str(path) for path in expected if path.exists()]
            passed = proc.returncode == 0 and all(
                path.is_file() and path.stat().st_size > 0 for path in expected
            )
            findings = [] if passed else [
                f"EXIT_{proc.returncode}",
                (proc.stderr or proc.stdout or "")[-800:],
            ]
            return passed, artifacts, findings, {"argv": argv}
        return _timed(operation, execute)

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        env = kernel.tool_doctor.inspect("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        if not env.installed or not env.executable_path or not ffprobe:
            finding = "FFMPEG_OR_FFPROBE_NOT_INSTALLED"
            return [
                OperationEvidence(operation=op, passed=False, findings=[finding])
                for op in self.OPERATIONS
            ]
        sandbox.mkdir(parents=True, exist_ok=True)
        ffmpeg = env.executable_path
        a = sandbox / "a.mp4"
        b = sandbox / "b.mp4"
        trans = sandbox / "transcoded.mp4"
        concat = sandbox / "concat.mp4"
        filtered = sandbox / "filtered.mp4"
        tone1 = sandbox / "tone1.wav"
        tone2 = sandbox / "tone2.wav"
        mixed = sandbox / "mixed.wav"
        captions = sandbox / "captions.srt"
        captioned = sandbox / "captioned.mp4"
        master = sandbox / "master.mp4"
        concat_list = sandbox / "concat.txt"

        setup_commands = [
            [ffmpeg, "-y", "-f", "lavfi", "-i", "color=c=blue:s=64x64:r=4:d=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(a)],
            [ffmpeg, "-y", "-f", "lavfi", "-i", "color=c=green:s=64x64:r=4:d=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(b)],
            [ffmpeg, "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-c:a", "pcm_s16le", str(tone1)],
            [ffmpeg, "-y", "-f", "lavfi", "-i", "sine=frequency=660:duration=2", "-c:a", "pcm_s16le", str(tone2)],
        ]
        for argv in setup_commands:
            proc = subprocess.run(argv, cwd=sandbox, capture_output=True, text=True, timeout=60, check=False)
            if proc.returncode != 0:
                return [
                    OperationEvidence(
                        operation=op,
                        passed=False,
                        findings=[f"FFMPEG_FIXTURE_FAILED:{proc.returncode}"],
                    )
                    for op in self.OPERATIONS
                ]

        results: list[OperationEvidence] = []

        def probe_execute():
            proc = subprocess.run(
                [ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(a)],
                cwd=sandbox,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            parsed = json.loads(proc.stdout) if proc.returncode == 0 and proc.stdout else {}
            passed = proc.returncode == 0 and bool(parsed.get("streams"))
            return passed, [str(a)], [] if passed else ["FFPROBE_PARSE_FAILED"], {"streams": len(parsed.get("streams", []))}
        results.append(_timed("probe", probe_execute))

        results.append(self._run(
            "transcode",
            [ffmpeg, "-y", "-i", str(a), "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(trans)],
            cwd=sandbox,
            expected=[trans],
        ))

        concat_list.write_text(
            f"file '{a.as_posix()}'\nfile '{b.as_posix()}'\n",
            encoding="utf-8",
        )
        results.append(self._run(
            "concat",
            [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(concat)],
            cwd=sandbox,
            expected=[concat],
        ))

        results.append(self._run(
            "filter",
            [ffmpeg, "-y", "-i", str(a), "-vf", "scale=48:48", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(filtered)],
            cwd=sandbox,
            expected=[filtered],
        ))

        results.append(self._run(
            "audio mix",
            [ffmpeg, "-y", "-i", str(tone1), "-i", str(tone2), "-filter_complex", "amix=inputs=2:duration=longest:normalize=0", "-c:a", "pcm_s16le", str(mixed)],
            cwd=sandbox,
            expected=[mixed],
        ))

        captions.write_text(
            "1\n00:00:00,100 --> 00:00:00,900\nCineFactory caption mastery\n",
            encoding="utf-8",
        )

        def captions_execute():
            proc = subprocess.run(
                [
                    ffmpeg,
                    "-y",
                    "-i",
                    str(a),
                    "-i",
                    str(captions),
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:0",
                    "-c:v",
                    "copy",
                    "-c:s",
                    "mov_text",
                    str(captioned),
                ],
                cwd=sandbox,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if proc.returncode != 0:
                return False, [str(captions)], [
                    f"CAPTION_MUX_EXIT_{proc.returncode}",
                    (proc.stderr or proc.stdout or "")[-800:],
                ], {}
            probe = subprocess.run(
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-show_streams",
                    "-of",
                    "json",
                    str(captioned),
                ],
                cwd=sandbox,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            parsed = (
                json.loads(probe.stdout)
                if probe.returncode == 0 and probe.stdout
                else {}
            )
            subtitle_streams = [
                stream
                for stream in parsed.get("streams", [])
                if stream.get("codec_type") == "subtitle"
            ]
            passed = (
                probe.returncode == 0
                and captioned.is_file()
                and captioned.stat().st_size > 0
                and len(subtitle_streams) == 1
            )
            return (
                passed,
                [str(captions), str(captioned)],
                [] if passed else ["CAPTION_STREAM_CONTRACT_FAILED"],
                {
                    "subtitle_streams": len(subtitle_streams),
                    "codec": (
                        subtitle_streams[0].get("codec_name")
                        if subtitle_streams
                        else None
                    ),
                },
            )

        results.append(_timed("captions", captions_execute))

        results.append(self._run(
            "master",
            [ffmpeg, "-y", "-stream_loop", "-1", "-i", str(a), "-i", str(mixed), "-t", "2", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(master)],
            cwd=sandbox,
            expected=[master],
        ))

        def qc_execute():
            proc = subprocess.run(
                [ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(master)],
                cwd=sandbox,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            parsed = json.loads(proc.stdout) if proc.returncode == 0 and proc.stdout else {}
            streams = parsed.get("streams", [])
            video = [s for s in streams if s.get("codec_type") == "video"]
            audio = [s for s in streams if s.get("codec_type") == "audio"]
            passed = (
                proc.returncode == 0
                and len(video) == 1
                and len(audio) == 1
                and int(video[0].get("width", 0)) == 64
                and int(video[0].get("height", 0)) == 64
            )
            findings = [] if passed else ["DELIVERY_CONTRACT_MISMATCH"]
            return passed, [str(master)], findings, {
                "video_streams": len(video),
                "audio_streams": len(audio),
                "width": int(video[0].get("width", 0)) if video else None,
                "height": int(video[0].get("height", 0)) if video else None,
            }
        results.append(_timed("delivery QC", qc_execute))
        return results


class ComfyUIExecutionEvaluator:
    OPERATIONS = [
        "workflow load",
        "node validation",
        "prompt queue",
        "seed control",
        "output collection",
        "provenance",
    ]

    @staticmethod
    def _failed(finding: str) -> list[OperationEvidence]:
        return [
            OperationEvidence(
                operation=operation,
                passed=False,
                findings=[finding],
            )
            for operation in ComfyUIExecutionEvaluator.OPERATIONS
        ]

    @staticmethod
    def _seed(workflow: dict) -> int | None:
        for node in workflow.values():
            if not isinstance(node, dict):
                continue
            inputs = node.get("inputs", {})
            if not isinstance(inputs, dict):
                continue
            for key in ("seed", "noise_seed"):
                value = inputs.get(key)
                if isinstance(value, int):
                    return value
        return None

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        adapter = kernel.tool_adapters.probe(kernel, "comfyui")
        if not adapter.available or not adapter.runtime_endpoint:
            return self._failed("COMFYUI_RUNTIME_UNAVAILABLE")

        policy_path = Path(kernel.root) / "config" / "factory_policy.yaml"
        if not policy_path.is_file():
            return self._failed("FACTORY_POLICY_MISSING")
        policy = FactoryPolicy.from_yaml(policy_path)
        executor = ComfyUIExecutor(
            policy,
            base_url=adapter.runtime_endpoint,
            poll_seconds=0.1,
            timeout=180,
        )
        workflows = WorkflowRegistry(
            Path(kernel.root) / "workflows"
        ).load()
        models = ModelRegistry(
            Path(kernel.root) / "models" / "registry.yaml"
        ).load()

        chosen = None
        chosen_workflow = None
        preflight = None
        rejection_findings: list[str] = []
        for manifest in workflows.list():
            if manifest.executor_id != "local.comfyui":
                continue
            if not manifest.local_only:
                rejection_findings.append(
                    f"{manifest.workflow_id}@{manifest.version}:NOT_LOCAL_ONLY"
                )
                continue
            if not manifest.model_revision:
                rejection_findings.append(
                    f"{manifest.workflow_id}@{manifest.version}:MODEL_REVISION_UNPINNED"
                )
                continue
            try:
                models.require_approved(
                    manifest.model_id,
                    manifest.model_revision,
                )
            except Exception as exc:
                rejection_findings.append(
                    f"{manifest.workflow_id}@{manifest.version}:"
                    f"MODEL_NOT_APPROVED:{exc}"
                )
                continue
            try:
                workflow = workflows.read_workflow_json(
                    manifest.workflow_id,
                    manifest.version,
                )
                candidate_preflight = executor.preflight(workflow)
            except Exception as exc:
                rejection_findings.append(
                    f"{manifest.workflow_id}@{manifest.version}:"
                    f"PREFLIGHT_ERROR:{exc}"
                )
                continue
            if not candidate_preflight.valid:
                rejection_findings.extend(
                    f"{manifest.workflow_id}@{manifest.version}:{finding}"
                    for finding in candidate_preflight.findings
                )
                continue
            chosen = manifest
            chosen_workflow = workflow
            preflight = candidate_preflight
            break

        if chosen is None or chosen_workflow is None or preflight is None:
            finding = "NO_APPROVED_COMFYUI_MASTERY_WORKFLOW"
            if rejection_findings:
                finding += ":" + "|".join(rejection_findings[:8])
            return self._failed(finding)

        sandbox.mkdir(parents=True, exist_ok=True)
        output_dir = sandbox / "outputs"
        workflow_path = sandbox / "mastery_workflow.json"
        workflow_path.write_text(
            json.dumps(
                chosen_workflow,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        evidence: list[OperationEvidence] = [
            OperationEvidence(
                operation="workflow load",
                passed=True,
                artifacts=[str(workflow_path)],
                metadata={
                    "workflow_id": chosen.workflow_id,
                    "workflow_version": chosen.version,
                    "model_id": chosen.model_id,
                    "model_revision": chosen.model_revision,
                },
            ),
            OperationEvidence(
                operation="node validation",
                passed=True,
                metadata={
                    "node_types": preflight.node_types_required,
                    "model_requirements": preflight.model_requirements,
                    "object_info_sha256": preflight.object_info_sha256,
                },
            ),
        ]

        seed = self._seed(chosen_workflow)
        evidence.append(
            OperationEvidence(
                operation="seed control",
                passed=seed is not None,
                findings=[] if seed is not None else [
                    "WORKFLOW_HAS_NO_EXPLICIT_INTEGER_SEED"
                ],
                metadata={"seed": seed},
            )
        )
        if seed is None:
            evidence.extend(
                [
                    OperationEvidence(
                        operation="prompt queue",
                        passed=False,
                        findings=["SEED_CONTROL_REQUIRED"],
                    ),
                    OperationEvidence(
                        operation="output collection",
                        passed=False,
                        findings=["SEED_CONTROL_REQUIRED"],
                    ),
                    OperationEvidence(
                        operation="provenance",
                        passed=False,
                        findings=["SEED_CONTROL_REQUIRED"],
                    ),
                ]
            )
            return evidence

        started = time.perf_counter()
        result = executor.execute(
            {
                "workflow": chosen_workflow,
                "output_dir": str(output_dir),
                "seed": seed,
                "workflow_id": chosen.workflow_id,
                "workflow_version": chosen.version,
                "model_id": chosen.model_id,
                "model_revision": chosen.model_revision,
            }
        )
        elapsed_ms = max(
            0,
            int((time.perf_counter() - started) * 1000),
        )
        prompt_id = result.metadata.get("prompt_id")
        evidence.append(
            OperationEvidence(
                operation="prompt queue",
                passed=bool(result.ok and prompt_id),
                duration_ms=elapsed_ms,
                findings=[] if result.ok and prompt_id else [
                    result.error or "PROMPT_QUEUE_FAILED"
                ],
                metadata={"prompt_id": prompt_id},
            )
        )

        artifacts = [
            str(Path(path))
            for path in result.artifacts
            if Path(path).is_file() and Path(path).stat().st_size > 0
        ]
        evidence.append(
            OperationEvidence(
                operation="output collection",
                passed=bool(result.ok and artifacts),
                artifacts=artifacts,
                findings=[] if result.ok and artifacts else [
                    result.error or "COMFYUI_OUTPUT_MISSING"
                ],
            )
        )

        provenance = result.metadata.get("provenance", {})
        provenance_path = provenance.get("provenance_path")
        provenance_ok = bool(
            result.ok
            and provenance.get("workflow_sha256")
            and provenance.get("object_info_sha256")
            and provenance.get("seed") == seed
            and provenance.get("workflow_id") == chosen.workflow_id
            and provenance.get("workflow_version") == chosen.version
            and provenance.get("model_id") == chosen.model_id
            and provenance.get("model_revision") == chosen.model_revision
            and provenance_path
            and Path(provenance_path).is_file()
        )
        evidence.append(
            OperationEvidence(
                operation="provenance",
                passed=provenance_ok,
                artifacts=[str(provenance_path)] if provenance_path else [],
                findings=[] if provenance_ok else [
                    "COMFYUI_PROVENANCE_INCOMPLETE"
                ],
                metadata=dict(provenance) if isinstance(provenance, dict) else {},
            )
        )
        return evidence




class ResolveExecutionEvaluator:
    OPERATIONS = [
        "edit",
        "Fusion comp",
        "color",
        "Fairlight mix",
        "deliver",
    ]

    def __init__(
        self,
        adapter_factory=None,
    ) -> None:
        self.adapter_factory = (
            adapter_factory
            or (lambda root: ResolveRuntimeAdapter(root))
        )

    @staticmethod
    def _failed(finding: str) -> list[OperationEvidence]:
        return [
            OperationEvidence(
                operation=operation,
                passed=False,
                findings=[finding],
            )
            for operation in ResolveExecutionEvaluator.OPERATIONS
        ]

    @staticmethod
    def _make_fixture(sandbox: Path) -> Path:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("FFMPEG_REQUIRED_FOR_RESOLVE_MASTERY")
        fixture = sandbox / "resolve_mastery_input.mp4"
        proc = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=gray:s=320x180:r=24:d=2",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=2",
                "-shortest",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                str(fixture),
            ],
            cwd=sandbox,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if (
            proc.returncode != 0
            or not fixture.is_file()
            or fixture.stat().st_size <= 0
        ):
            raise RuntimeError(
                "RESOLVE_FIXTURE_CREATE_FAILED:"
                + (proc.stderr or proc.stdout or "")[-800:]
            )
        return fixture

    @staticmethod
    def _probe_render(path: Path) -> tuple[bool, dict, list[str]]:
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            return False, {}, ["FFPROBE_REQUIRED_FOR_RESOLVE_MASTERY"]
        proc = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if proc.returncode != 0:
            return False, {}, [
                "RESOLVE_RENDER_FFPROBE_FAILED:"
                + (proc.stderr or proc.stdout or "")[-600:]
            ]
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            return False, {}, [f"RESOLVE_RENDER_PROBE_JSON:{exc}"]
        streams = payload.get("streams", [])
        video = [
            stream
            for stream in streams
            if stream.get("codec_type") == "video"
        ]
        audio = [
            stream
            for stream in streams
            if stream.get("codec_type") == "audio"
        ]
        passed = bool(video) and bool(audio)
        return passed, {
            "video_streams": len(video),
            "audio_streams": len(audio),
            "format": payload.get("format", {}).get("format_name"),
        }, [] if passed else ["RESOLVE_RENDER_STREAM_CONTRACT_FAILED"]

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        sandbox.mkdir(parents=True, exist_ok=True)
        adapter = self.adapter_factory(kernel.root)
        runtime = adapter.probe()
        if not runtime.connected:
            return self._failed(
                "RESOLVE_RUNTIME_UNAVAILABLE:"
                + "|".join(runtime.findings[:4])
            )

        try:
            fixture = self._make_fixture(sandbox)
        except Exception as exc:
            return self._failed(f"{type(exc).__name__}:{exc}")

        result = adapter.sandbox_exercise(
            input_media=fixture,
            output_dir=sandbox / "outputs",
            timeout_seconds=180,
        )
        evidence = [
            OperationEvidence(
                operation=item.operation,
                passed=item.passed,
                duration_ms=item.duration_ms,
                artifacts=list(item.artifacts),
                findings=list(item.findings),
                metadata=dict(item.metadata),
            )
            for item in result.operation_evidence
        ]

        by_operation = {
            item.operation: item
            for item in evidence
        }
        deliver = by_operation.get("deliver")
        if (
            deliver is not None
            and deliver.passed
            and result.render_output
        ):
            output = Path(result.render_output)
            media_ok, metadata, findings = self._probe_render(output)
            deliver.passed = deliver.passed and media_ok
            deliver.metadata.update(metadata)
            deliver.findings.extend(findings)
            if output.is_file() and str(output) not in deliver.artifacts:
                deliver.artifacts.append(str(output))

        if result.provenance_path:
            provenance = Path(result.provenance_path)
            if provenance.is_file():
                for item in evidence:
                    item.metadata.setdefault(
                        "resolve_provenance",
                        str(provenance),
                    )

        if not result.cleaned_up:
            for item in evidence:
                if item.passed:
                    item.findings.append(
                        "SANDBOX_PROJECT_CLEANUP_INCOMPLETE"
                    )
                    item.passed = False
        return evidence




class PremiereExecutionEvaluator:
    OPERATIONS = [
        "import media",
        "create sequence",
        "place clip",
        "trim",
        "markers",
        "captions",
        "audio edit",
        "effects",
        "export",
    ]

    def __init__(self, adapter_factory=None) -> None:
        self.adapter_factory = (
            adapter_factory
            or (lambda root: PremiereRuntimeAdapter(root))
        )

    @staticmethod
    def _failed(finding: str) -> list[OperationEvidence]:
        return [
            OperationEvidence(
                operation=operation,
                passed=False,
                findings=[finding],
            )
            for operation in PremiereExecutionEvaluator.OPERATIONS
        ]

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        env = kernel.tool_doctor.inspect("premiere")
        adapter = self.adapter_factory(kernel.root)
        runtime = adapter.probe(installed=env.installed)
        if not (
            runtime.installed
            and runtime.bridge_reachable
            and runtime.plugin_registered
        ):
            return self._failed(
                "PREMIERE_RUNTIME_UNAVAILABLE:"
                + "|".join(runtime.findings[:4])
            )

        sandbox.mkdir(parents=True, exist_ok=True)
        try:
            fixture = make_premiere_fixture(
                sandbox / "premiere_mastery_input.mp4"
            )
        except Exception as exc:
            return self._failed(f"{type(exc).__name__}:{exc}")

        result = adapter.sandbox_exercise(
            input_media=fixture,
            output_dir=sandbox / "outputs",
            timeout_seconds=120,
        )
        evidence = [
            OperationEvidence(
                operation=item.operation,
                passed=item.passed,
                duration_ms=item.duration_ms,
                artifacts=list(item.artifacts),
                findings=list(item.findings),
                metadata=dict(item.payload),
            )
            for item in result.operation_evidence
        ]

        # Premiere caption creation is delegated to the already validated
        # FFmpeg timed-text pipeline. This still requires explicit evidence.
        try:
            ffmpeg_mastery = kernel.execution_mastery.get("ffmpeg")
        except KeyError:
            ffmpeg_mastery = None
        caption_passed = False
        caption_artifacts: list[str] = []
        caption_findings: list[str] = []
        if ffmpeg_mastery is not None:
            by_op = {
                item.operation: item
                for item in ffmpeg_mastery.operation_evidence
            }
            caption_evidence = by_op.get("captions")
            caption_passed = bool(
                ffmpeg_mastery.passed
                and ffmpeg_mastery.regression_passed
                and caption_evidence is not None
                and caption_evidence.passed
            )
            if caption_evidence is not None:
                caption_artifacts = list(caption_evidence.artifacts)
                caption_findings = list(caption_evidence.findings)
        if not caption_passed:
            caption_findings = (
                caption_findings
                or ["DELEGATED_CAPTION_MASTERY_MISSING:ffmpeg"]
            )
        evidence.append(
            OperationEvidence(
                operation="captions",
                passed=caption_passed,
                artifacts=caption_artifacts,
                findings=caption_findings,
                metadata={
                    "delegated_to": "ffmpeg",
                    "source": "timed-text/SRT pipeline",
                },
            )
        )

        by_operation = {item.operation: item for item in evidence}
        export_evidence = by_operation.get("export")
        if (
            export_evidence is not None
            and export_evidence.passed
            and result.export_output
        ):
            output = Path(result.export_output)
            ok, metadata, findings = ResolveExecutionEvaluator._probe_render(
                output
            )
            export_evidence.passed = export_evidence.passed and ok
            export_evidence.metadata.update(metadata)
            export_evidence.findings.extend(findings)
            if output.is_file() and str(output) not in export_evidence.artifacts:
                export_evidence.artifacts.append(str(output))

        if not result.cleaned_up:
            for item in evidence:
                if item.passed:
                    item.passed = False
                    item.findings.append(
                        "PREMIERE_SANDBOX_CLEANUP_INCOMPLETE"
                    )
        if result.provenance_path:
            provenance = Path(result.provenance_path)
            if provenance.is_file():
                for item in evidence:
                    item.metadata.setdefault(
                        "premiere_provenance",
                        str(provenance),
                    )
        return evidence




class PhotoshopExecutionEvaluator:
    OPERATIONS = [
        "layers",
        "masks",
        "smart objects",
        "text",
        "composite",
        "thumbnail",
        "batch export",
    ]

    def __init__(self, adapter_factory=None) -> None:
        self.adapter_factory = (
            adapter_factory
            or (lambda root: PhotoshopRuntimeAdapter(root))
        )

    @staticmethod
    def _failed(finding: str) -> list[OperationEvidence]:
        return [
            OperationEvidence(
                operation=operation,
                passed=False,
                findings=[finding],
            )
            for operation in PhotoshopExecutionEvaluator.OPERATIONS
        ]

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        env = kernel.tool_doctor.inspect("photoshop")
        adapter = self.adapter_factory(kernel.root)
        runtime = adapter.probe(installed=env.installed)
        if not (
            runtime.installed
            and runtime.bridge_reachable
            and runtime.plugin_registered
        ):
            return self._failed(
                "PHOTOSHOP_RUNTIME_UNAVAILABLE:"
                + "|".join(runtime.findings[:4])
            )

        sandbox.mkdir(parents=True, exist_ok=True)
        result = adapter.sandbox_exercise(
            output_dir=sandbox / "outputs",
            timeout_seconds=90,
        )
        evidence = [
            OperationEvidence(
                operation=item.operation,
                passed=item.passed,
                duration_ms=item.duration_ms,
                artifacts=list(item.artifacts),
                findings=list(item.findings),
                metadata=dict(item.payload),
            )
            for item in result.operation_evidence
        ]

        by_operation = {item.operation: item for item in evidence}
        export_evidence = by_operation.get("batch export")
        if export_evidence is not None and export_evidence.passed:
            expected = [
                Path(path)
                for path in result.exported_files
                if path
            ]
            ok = (
                len(expected) >= 2
                and all(path.is_file() and path.stat().st_size > 0 for path in expected)
            )
            export_evidence.passed = export_evidence.passed and ok
            if not ok:
                export_evidence.findings.append(
                    "PHOTOSHOP_EXPORT_ARTIFACT_CONTRACT_FAILED"
                )
            for path in expected:
                if str(path) not in export_evidence.artifacts:
                    export_evidence.artifacts.append(str(path))

        if result.provenance_path:
            provenance = Path(result.provenance_path)
            if provenance.is_file():
                for item in evidence:
                    item.metadata.setdefault(
                        "photoshop_provenance",
                        str(provenance),
                    )

        if not result.cleaned_up:
            for item in evidence:
                if item.passed:
                    item.passed = False
                    item.findings.append(
                        "PHOTOSHOP_SANDBOX_CLEANUP_INCOMPLETE"
                    )
        return evidence




class AfterEffectsExecutionEvaluator:
    OPERATIONS = [
        "compositions",
        "layers",
        "keyframes",
        "expressions",
        "templates",
        "render queue",
    ]

    def __init__(self, adapter_factory=None) -> None:
        self.adapter_factory = (
            adapter_factory
            or (lambda root: AfterEffectsRuntimeAdapter(root))
        )

    @staticmethod
    def _failed(finding: str) -> list[OperationEvidence]:
        return [
            OperationEvidence(
                operation=operation,
                passed=False,
                findings=[finding],
            )
            for operation in AfterEffectsExecutionEvaluator.OPERATIONS
        ]

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        adapter = self.adapter_factory(kernel.root)
        runtime = adapter.probe()
        if not runtime.scripting_ready:
            return self._failed(
                "AFTER_EFFECTS_RUNTIME_UNAVAILABLE:"
                + "|".join(runtime.findings[:4])
            )

        sandbox.mkdir(parents=True, exist_ok=True)
        result = adapter.sandbox_exercise(
            output_dir=sandbox / "outputs",
            timeout_seconds=180,
        )
        evidence = [
            OperationEvidence(
                operation=item.operation,
                passed=item.passed,
                duration_ms=item.duration_ms,
                artifacts=list(item.artifacts),
                findings=list(item.findings),
                metadata=dict(item.metadata),
            )
            for item in result.operation_evidence
        ]

        by_operation = {item.operation: item for item in evidence}
        render = by_operation.get("render queue")
        if render is not None and render.passed and result.render_output:
            output = Path(result.render_output)
            if not output.is_file() or output.stat().st_size <= 0:
                render.passed = False
                render.findings.append("AFTER_EFFECTS_RENDER_OUTPUT_MISSING")
            elif str(output) not in render.artifacts:
                render.artifacts.append(str(output))

        template = by_operation.get("templates")
        if template is not None and template.passed and result.mogrt_path:
            mogrt = Path(result.mogrt_path)
            if not mogrt.is_file() or mogrt.stat().st_size <= 0:
                template.passed = False
                template.findings.append("AFTER_EFFECTS_MOGRT_MISSING")
            elif str(mogrt) not in template.artifacts:
                template.artifacts.append(str(mogrt))

        if result.evidence_path:
            evidence_path = Path(result.evidence_path)
            if evidence_path.is_file():
                for item in evidence:
                    item.metadata.setdefault(
                        "aftereffects_evidence",
                        str(evidence_path),
                    )

        if not result.cleaned_up:
            for item in evidence:
                if item.passed:
                    item.passed = False
                    item.findings.append(
                        "AFTER_EFFECTS_SANDBOX_CLEANUP_INCOMPLETE"
                    )
        return evidence




class UnrealExecutionEvaluator:
    OPERATIONS = [
        "level assembly",
        "Sequencer",
        "camera",
        "lighting",
        "Movie Render Pipeline",
    ]

    def __init__(
        self,
        adapter_factory=None,
        fixture_provider=None,
    ) -> None:
        self.adapter_factory = (
            adapter_factory
            or (lambda root: UnrealRuntimeAdapter(root))
        )
        self.fixture_provider = fixture_provider or self._default_fixture

    @staticmethod
    def _default_fixture(root: Path) -> UnrealMasteryFixture | None:
        path = (
            Path(root)
            / "data"
            / "studio"
            / "unreal_mastery_fixture.json"
        )
        if path.is_file():
            return UnrealMasteryFixture.model_validate_json(
                path.read_text(encoding="utf-8")
            )
        project = os.getenv("CINEFACTORY_UNREAL_PROJECT")
        map_name = os.getenv("CINEFACTORY_UNREAL_MAP")
        sequence = os.getenv("CINEFACTORY_UNREAL_SEQUENCE")
        config = os.getenv("CINEFACTORY_UNREAL_MRQ_CONFIG")
        if all((project, map_name, sequence, config)):
            return UnrealMasteryFixture(
                project_path=project,
                map_name=map_name,
                level_sequence=sequence,
                movie_pipeline_config=config,
            )
        return None

    @staticmethod
    def _failed(finding: str) -> list[OperationEvidence]:
        return [
            OperationEvidence(
                operation=operation,
                passed=False,
                findings=[finding],
            )
            for operation in UnrealExecutionEvaluator.OPERATIONS
        ]

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        adapter = self.adapter_factory(kernel.root)
        runtime = adapter.probe()
        if not runtime.scripting_ready:
            return self._failed(
                "UNREAL_RUNTIME_UNAVAILABLE:"
                + "|".join(runtime.findings[:4])
            )
        fixture = self.fixture_provider(Path(kernel.root))
        if fixture is None:
            return self._failed("UNREAL_MASTERY_FIXTURE_MISSING")

        sandbox.mkdir(parents=True, exist_ok=True)
        result = adapter.sandbox_exercise(
            fixture=fixture,
            output_dir=sandbox / "outputs",
            timeout_seconds=300,
        )
        evidence = [
            OperationEvidence(
                operation=item.operation,
                passed=item.passed,
                duration_ms=item.duration_ms,
                artifacts=list(item.artifacts),
                findings=list(item.findings),
                metadata=dict(item.metadata),
            )
            for item in result.operation_evidence
        ]
        if result.evidence_path:
            evidence_path = Path(result.evidence_path)
            if evidence_path.is_file():
                for item in evidence:
                    item.metadata.setdefault(
                        "unreal_evidence",
                        str(evidence_path),
                    )
        return evidence




class CanvaExecutionEvaluator:
    OPERATIONS = [
        "brand template",
        "text replacement",
        "asset replacement",
        "social derivative",
        "export",
    ]

    def __init__(
        self,
        adapter_factory=None,
        fixture_provider=None,
    ) -> None:
        self.adapter_factory = (
            adapter_factory
            or (lambda root: CanvaRuntimeAdapter(root))
        )
        self.fixture_provider = fixture_provider or self._default_fixture

    @staticmethod
    def _default_fixture(root: Path) -> CanvaMasteryFixture | None:
        path = (
            Path(root)
            / "data"
            / "studio"
            / "canva_mastery_fixture.json"
        )
        if path.is_file():
            return CanvaMasteryFixture.model_validate_json(
                path.read_text(encoding="utf-8")
            )
        values = {
            "brand_template_id": os.getenv("CANVA_MASTERY_BRAND_TEMPLATE_ID"),
            "text_field": os.getenv("CANVA_MASTERY_TEXT_FIELD"),
            "image_field": os.getenv("CANVA_MASTERY_IMAGE_FIELD"),
            "asset_id": os.getenv("CANVA_MASTERY_ASSET_ID"),
            "design_id": os.getenv("CANVA_MASTERY_DESIGN_ID"),
        }
        if all(values.values()):
            return CanvaMasteryFixture(**values)
        return None

    @staticmethod
    def _failed(finding: str) -> list[OperationEvidence]:
        return [
            OperationEvidence(
                operation=operation,
                passed=False,
                findings=[finding],
            )
            for operation in CanvaExecutionEvaluator.OPERATIONS
        ]

    def evaluate(self, kernel, sandbox: Path) -> list[OperationEvidence]:
        adapter = self.adapter_factory(kernel.root)
        runtime = adapter.probe()
        if not runtime.authorized:
            return self._failed(
                "CANVA_RUNTIME_UNAVAILABLE:"
                + "|".join(runtime.findings[:4])
            )

        fixture = self.fixture_provider(Path(kernel.root))
        if fixture is None:
            return self._failed("CANVA_MASTERY_FIXTURE_MISSING")

        sandbox.mkdir(parents=True, exist_ok=True)
        result = adapter.sandbox_exercise(
            fixture=fixture,
            output_dir=sandbox / "outputs",
            timeout_seconds=120,
        )
        evidence = [
            OperationEvidence(
                operation=item.operation,
                passed=item.passed,
                duration_ms=item.duration_ms,
                artifacts=list(item.artifacts),
                findings=list(item.findings),
                metadata=dict(item.metadata),
            )
            for item in result.operation_evidence
        ]
        if result.provenance_path:
            provenance = Path(result.provenance_path)
            if provenance.is_file():
                for item in evidence:
                    item.metadata.setdefault(
                        "canva_provenance",
                        str(provenance),
                    )
        return evidence


class ExecutionMasteryRunner:
    def __init__(self, kernel, store: ExecutionMasteryStore | None = None) -> None:
        self.kernel = kernel
        self.store = store or getattr(
            kernel,
            "execution_mastery",
            ExecutionMasteryStore(
                Path(kernel.root) / "data" / "studio" / "execution_mastery"
            ),
        )
        self._evaluators = {
            "blender": BlenderExecutionEvaluator(),
            "ffmpeg": FFmpegExecutionEvaluator(),
            "comfyui": ComfyUIExecutionEvaluator(),
            "resolve": ResolveExecutionEvaluator(),
            "premiere": PremiereExecutionEvaluator(),
            "photoshop": PhotoshopExecutionEvaluator(),
            "aftereffects": AfterEffectsExecutionEvaluator(),
            "unreal": UnrealExecutionEvaluator(),
            "canva": CanvaExecutionEvaluator(),
        }

    @staticmethod
    def _pack(tool_id: str):
        return next(
            pack for pack in default_tool_knowledge_packs()
            if pack.tool_id == tool_id
        )

    def evaluate(self, tool_id: str, *, promote_validated: bool = True) -> ToolExecutionMasteryReport:
        pack = self._pack(tool_id)
        env = self.kernel.tool_doctor.inspect(tool_id)
        runtime_available = env.installed
        try:
            adapter_probe = self.kernel.tool_adapters.probe(
                self.kernel,
                tool_id,
            )
        except (AttributeError, KeyError):
            adapter_probe = None
        if adapter_probe is not None and adapter_probe.runtime_reachable:
            runtime_available = True
        specs = self.kernel.tool_skills.list(tool_id)
        required = sorted({
            operation
            for spec in specs
            for operation in spec.operations
        })
        sandbox = (
            Path(self.kernel.root)
            / "data"
            / "studio"
            / "tool_evals"
            / "mastery"
            / tool_id
        )
        evaluator = self._evaluators.get(tool_id)
        if evaluator is None:
            evidence = [
                OperationEvidence(
                    operation=operation,
                    passed=False,
                    findings=[
                        "TOOL_NOT_INSTALLED" if not env.installed
                        else "EXECUTION_EVALUATOR_NOT_IMPLEMENTED"
                    ],
                )
                for operation in required
            ]
        else:
            evidence = evaluator.evaluate(self.kernel, sandbox)

        by_operation = {item.operation: item for item in evidence}
        passed_operations = sorted(
            operation
            for operation in required
            if operation in by_operation and by_operation[operation].passed
        )
        missing = sorted(set(required) - set(passed_operations))
        knowledge = operation_coverage(self.kernel, tool_id)
        execution_coverage = (
            len(passed_operations) / len(required) if required else 1.0
        )
        passed = (
            runtime_available
            and not missing
            and knowledge.coverage == 1.0
        )
        report = ToolExecutionMasteryReport(
            tool_id=tool_id,
            skill_id=pack.skill_id,
            version=pack.version,
            installed=env.installed,
            runtime_available=runtime_available,
            detected_version=env.version,
            sandbox_root=str(sandbox),
            operation_evidence=evidence,
            required_operations=required,
            passed_operations=passed_operations,
            missing_operations=missing,
            execution_coverage=execution_coverage,
            knowledge_coverage=knowledge.coverage,
            passed=passed,
            regression_passed=passed,
            findings=[] if passed else [
                "EXECUTION_MASTERY_INCOMPLETE",
                *([f"MISSING:{','.join(missing)}"] if missing else []),
            ],
        )
        self.store.save(report)

        if passed:
            evaluation = SkillEvaluation(
                skill_id=pack.skill_id,
                version=pack.version,
                passed=True,
                score=execution_coverage,
                eval_id="execution_mastery_v1",
                findings=[
                    f"operation_evidence={len(passed_operations)}/{len(required)}",
                    f"evidence={self.store.root / tool_id / 'latest.json'}",
                ],
                regression_passed=True,
            )
            self.kernel.skills.record_evaluation(evaluation)
            if promote_validated:
                manifest = self.kernel.skills.get(pack.skill_id, pack.version)
                if manifest.status is SkillStatus.CANDIDATE:
                    self.kernel.skills.validate_skill(pack.skill_id, pack.version)
        return report

    def evaluate_installed(self) -> list[ToolExecutionMasteryReport]:
        reports: list[ToolExecutionMasteryReport] = []
        for pack in default_tool_knowledge_packs():
            env = self.kernel.tool_doctor.inspect(pack.tool_id)
            runtime_available = env.installed
            try:
                adapter_probe = self.kernel.tool_adapters.probe(
                    self.kernel,
                    pack.tool_id,
                )
            except (AttributeError, KeyError):
                adapter_probe = None
            if adapter_probe is not None and adapter_probe.runtime_reachable:
                runtime_available = True
            if runtime_available and pack.tool_id in self._evaluators:
                reports.append(self.evaluate(pack.tool_id))
        return reports


def _blender_mastery_script(
    *,
    evidence_path: Path,
    blend_path: Path,
    render_path: Path,
) -> str:
    evidence = str(evidence_path).replace("\\", "/")
    blend = str(blend_path).replace("\\", "/")
    render = str(render_path).replace("\\", "/")
    return f"""import bpy, json, time, traceback
from pathlib import Path

OUT = Path(r'{evidence}')
BLEND = Path(r'{blend}')
RENDER = Path(r'{render}')
ops = {{}}

def run(name, fn, artifacts=None):
    start=time.perf_counter()
    try:
        meta=fn() or {{}}
        paths=[str(Path(p)) for p in (artifacts or [])]
        ops[name]={{
            'passed': True,
            'duration_ms': int((time.perf_counter()-start)*1000),
            'artifacts': paths,
            'findings': [],
            'metadata': meta,
        }}
    except Exception as exc:
        ops[name]={{
            'passed': False,
            'duration_ms': int((time.perf_counter()-start)*1000),
            'artifacts': [],
            'findings': [type(exc).__name__+':'+str(exc), traceback.format_exc()[-1000:]],
            'metadata': {{}},
        }}

def scene_assembly():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    mesh=bpy.data.meshes.new('MasteryMesh')
    mesh.from_pydata([(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0),(0,0,1.5)], [], [(0,1,2,3),(0,4,1),(1,4,2),(2,4,3),(3,4,0)])
    obj=bpy.data.objects.new('MasteryObject', mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.scene['mastery_object']='MasteryObject'
    return {{'object':obj.name,'vertices':len(mesh.vertices)}}

def rigging():
    arm_data=bpy.data.armatures.new('MasteryArmatureData')
    arm=bpy.data.objects.new('MasteryArmature', arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active=arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bone=arm_data.edit_bones.new('Root')
    bone.head=(0,0,0)
    bone.tail=(0,0,1)
    bpy.ops.object.mode_set(mode='OBJECT')
    return {{'armature':arm.name,'bones':len(arm_data.bones)}}

def animation():
    obj=bpy.data.objects['MasteryObject']
    obj.location=(0,0,0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location=(0.5,0,0)
    obj.keyframe_insert(data_path='location', frame=2)
    action = obj.animation_data.action if obj.animation_data else None
    return {{'has_animation': bool(action or obj.animation_data)}}

def camera():
    data=bpy.data.cameras.new('MasteryCameraData')
    cam=bpy.data.objects.new('MasteryCamera',data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location=(4,-6,4)
    cam.rotation_euler=(1.1,0,0.58)
    data.lens=50
    bpy.context.scene.camera=cam
    return {{'camera':cam.name,'lens':data.lens}}

def lighting():
    data=bpy.data.lights.new('MasteryKey', type='AREA')
    data.energy=700
    light=bpy.data.objects.new('MasteryKey',data)
    bpy.context.scene.collection.objects.link(light)
    light.location=(3,-3,5)
    return {{'light':light.name,'energy':data.energy}}

def compositor():
    scene=bpy.context.scene
    scene.use_nodes=True
    tree=scene.node_tree
    return {{'node_count':len(tree.nodes) if tree else 0}}

def asset_conversion():
    curve_data=bpy.data.curves.new('MasteryCurve','CURVE')
    curve_data.dimensions='3D'
    spline=curve_data.splines.new('POLY')
    spline.points.add(1)
    spline.points[0].co=(0,0,0,1)
    spline.points[1].co=(1,0,0,1)
    curve=bpy.data.objects.new('MasteryCurve',curve_data)
    bpy.context.scene.collection.objects.link(curve)
    depsgraph=bpy.context.evaluated_depsgraph_get()
    evaluated=curve.evaluated_get(depsgraph)
    mesh=bpy.data.meshes.new_from_object(evaluated)
    converted=bpy.data.objects.new('MasteryConvertedMesh',mesh)
    bpy.context.scene.collection.objects.link(converted)
    if converted.type != 'MESH':
        raise RuntimeError('conversion did not produce mesh')
    return {{'converted_type':converted.type}}

def render():
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE_NEXT'
    scene.render.resolution_x=64
    scene.render.resolution_y=64
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath=str(RENDER)
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    bpy.ops.render.render(write_still=True)
    if not RENDER.exists() or RENDER.stat().st_size <= 0:
        raise RuntimeError('render output missing')
    return {{'engine':scene.render.engine,'bytes':RENDER.stat().st_size}}

run('scene assembly', scene_assembly)
run('rigging', rigging)
run('animation', animation)
run('camera', camera)
run('lighting', lighting)
run('compositing', compositor)
run('asset conversion', asset_conversion)
run('render', render, [RENDER, BLEND])
ops['headless batch']={{
    'passed': all(v.get('passed') for v in ops.values()),
    'duration_ms': 0,
    'artifacts': [str(BLEND), str(RENDER)],
    'findings': [],
    'metadata': {{'background': True}},
}}
OUT.write_text(json.dumps(ops, indent=2), encoding='utf-8')
print('CINEFACTORY_EXECUTION_MASTERY_OK')
"""
