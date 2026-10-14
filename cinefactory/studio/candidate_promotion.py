from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from cinefactory.domain.enums import NetworkScope
from cinefactory.turbo.contracts import ResourceClass, WorkItem
from cinefactory.workflows.registry import (
    WorkflowManifest,
    WorkflowRegistry,
)
from cinefactory.workflows.safety import WorkflowSafetyValidator

from .capability_execution_lab import (
    BenchmarkDimension,
    BenchmarkReport,
    CapabilityExecutionLab,
    LabGateStatus,
    QualificationEvidencePackage,
)
from .production_method_switch import (
    MethodSwitchRequest,
    ProductionMethodSpec,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TrustedArtifactClass(StrEnum):
    COMFYUI_WORKFLOW_JSON = "COMFYUI_WORKFLOW_JSON"
    MODEL_SAFETENSORS = "MODEL_SAFETENSORS"
    PURE_DATA_ASSET = "PURE_DATA_ASSET"
    REGISTERED_METHOD_MANIFEST = "REGISTERED_METHOD_MANIFEST"
    PYTHON_CODE = "PYTHON_CODE"
    SCRIPT_CODE = "SCRIPT_CODE"
    NATIVE_BINARY = "NATIVE_BINARY"
    ARCHIVE = "ARCHIVE"
    UNKNOWN = "UNKNOWN"


class CandidateExecutionState(StrEnum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    FAIL = "FAIL"


class PromotionState(StrEnum):
    EVIDENCE_ONLY = "EVIDENCE_ONLY"
    LAB_APPROVED = "LAB_APPROVED"
    REGISTRY_PROMOTED = "REGISTRY_PROMOTED"
    PRODUCTION_EXECUTABLE = "PRODUCTION_EXECUTABLE"
    BLOCKED = "BLOCKED"


class CandidateSandboxProfile(BaseModel):
    profile_id: str = "declarative_local_v1"
    public_network_allowed: bool = False
    loopback_lan_allowed: bool = True
    process_spawn_allowed: bool = False
    source_read_only: bool = True
    scratch_only_writes: bool = True
    max_artifact_bytes: int = 512 * 1024 * 1024
    max_workflow_nodes: int = Field(default=250, ge=1)
    max_runtime_seconds: int = Field(default=900, ge=1)
    max_output_files: int = Field(default=64, ge=1)
    allowed_artifact_classes: set[TrustedArtifactClass] = Field(
        default_factory=lambda: {
            TrustedArtifactClass.COMFYUI_WORKFLOW_JSON,
            TrustedArtifactClass.MODEL_SAFETENSORS,
            TrustedArtifactClass.PURE_DATA_ASSET,
        }
    )


class CandidateClassification(BaseModel):
    artifact_class: TrustedArtifactClass
    path: str
    sha256: str | None = None
    bytes_size: int = Field(default=0, ge=0)
    auto_execution_allowed: bool = False
    findings: list[str] = Field(default_factory=list)


class TrustedCandidateExecution(BaseModel):
    candidate_id: str
    artifact_class: TrustedArtifactClass
    state: CandidateExecutionState
    sandbox_profile_id: str
    preflight_passed: bool = False
    execution_attempted: bool = False
    execution_passed: bool = False
    artifacts: list[str] = Field(default_factory=list)
    workflow_sha256: str | None = None
    object_info_sha256: str | None = None
    findings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=utcnow)
    finished_at: datetime = Field(default_factory=utcnow)


class BenchmarkMatrixRow(BaseModel):
    case_id: str
    benchmark: BenchmarkReport


class BenchmarkMatrixReport(BaseModel):
    matrix_id: str
    method_id: str
    rows: list[BenchmarkMatrixRow] = Field(default_factory=list)
    dimension_means: dict[str, float] = Field(default_factory=dict)
    dimension_minima: dict[str, float] = Field(default_factory=dict)
    aggregate_mean: float = Field(default=0.0, ge=0.0, le=1.0)
    aggregate_minimum: float = Field(default=0.0, ge=0.0, le=1.0)
    required_cases: int = Field(default=2, ge=1)
    minimum_dimension_score: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
    )
    passed: bool = False
    blockers: list[str] = Field(default_factory=list)


class PromotionAttestation(BaseModel):
    attestation_id: str
    candidate_id: str
    state: PromotionState
    artifact_class: TrustedArtifactClass
    workflow_id: str | None = None
    workflow_version: str | None = None
    tool_id: str | None = None
    method_id: str | None = None
    evidence_package_path: str | None = None
    evidence_package_sha256: str | None = None
    execution_evidence: TrustedCandidateExecution | None = None
    benchmark_matrix_path: str | None = None
    promoted_manifest_path: str | None = None
    promoted_workflow_path: str | None = None
    method_assessment: dict[str, Any] = Field(default_factory=dict)
    blockers: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class CandidatePromotionStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.attestations = self.root / "attestations"
        self.matrices = self.root / "benchmark_matrices"
        self.attestations.mkdir(parents=True, exist_ok=True)
        self.matrices.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value)

    def save_attestation(
        self,
        attestation: PromotionAttestation,
    ) -> Path:
        path = self.attestations / (
            f"{self._safe(attestation.attestation_id)}.json"
        )
        path.write_text(
            attestation.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path

    def save_matrix(
        self,
        report: BenchmarkMatrixReport,
    ) -> Path:
        path = self.matrices / (
            f"{self._safe(report.matrix_id)}.json"
        )
        path.write_text(
            report.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path


class TrustedCandidateLabExecutor:
    """Executor for safe declarative candidate classes only.

    This component does not spawn candidate processes. ComfyUI workflow JSON
    may execute only through CineFactory's already-approved local/LAN ComfyUI
    executor, whose own safety + object-info preflight remains authoritative.
    """

    PURE_DATA_SUFFIXES = {
        ".json",
        ".yaml",
        ".yml",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".wav",
        ".flac",
        ".mp3",
        ".obj",
        ".fbx",
        ".glb",
        ".gltf",
        ".blend",
    }
    SCRIPT_SUFFIXES = {
        ".bat",
        ".cmd",
        ".ps1",
        ".sh",
        ".vbs",
        ".js",
    }
    NATIVE_SUFFIXES = {
        ".exe",
        ".dll",
        ".msi",
        ".com",
        ".scr",
        ".so",
        ".dylib",
    }

    def __init__(
        self,
        ctx: Any,
        *,
        profile: CandidateSandboxProfile | None = None,
    ) -> None:
        self.ctx = ctx
        self.profile = profile or CandidateSandboxProfile()
        self.workflow_safety = WorkflowSafetyValidator()

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def classify(
        self,
        path: str | Path,
    ) -> CandidateClassification:
        artifact = Path(path).resolve()
        if not artifact.is_file():
            return CandidateClassification(
                artifact_class=TrustedArtifactClass.UNKNOWN,
                path=str(artifact),
                findings=["ARTIFACT_FILE_MISSING"],
            )
        size = artifact.stat().st_size
        suffix = artifact.suffix.lower()
        findings: list[str] = []
        if suffix == ".py":
            kind = TrustedArtifactClass.PYTHON_CODE
        elif suffix in self.SCRIPT_SUFFIXES:
            kind = TrustedArtifactClass.SCRIPT_CODE
        elif suffix in self.NATIVE_SUFFIXES:
            kind = TrustedArtifactClass.NATIVE_BINARY
        elif suffix == ".safetensors":
            kind = TrustedArtifactClass.MODEL_SAFETENSORS
        elif suffix in {".zip", ".7z", ".rar", ".tar", ".gz"}:
            kind = TrustedArtifactClass.ARCHIVE
        elif suffix == ".json":
            try:
                raw = json.loads(
                    artifact.read_text(encoding="utf-8")
                )
            except Exception:
                raw = None
            looks_comfy = bool(
                isinstance(raw, dict)
                and raw
                and any(
                    isinstance(node, dict)
                    and isinstance(node.get("class_type"), str)
                    for node in raw.values()
                )
            )
            kind = (
                TrustedArtifactClass.COMFYUI_WORKFLOW_JSON
                if looks_comfy
                else TrustedArtifactClass.PURE_DATA_ASSET
            )
        elif suffix in self.PURE_DATA_SUFFIXES:
            kind = TrustedArtifactClass.PURE_DATA_ASSET
        else:
            kind = TrustedArtifactClass.UNKNOWN

        if size > self.profile.max_artifact_bytes:
            findings.append("SANDBOX_ARTIFACT_SIZE_LIMIT_EXCEEDED")
        if kind not in self.profile.allowed_artifact_classes:
            findings.append(
                f"AUTO_EXECUTION_CLASS_BLOCKED:{kind.value}"
            )
        execution_allowed = bool(
            kind is TrustedArtifactClass.COMFYUI_WORKFLOW_JSON
            and not findings
        )
        return CandidateClassification(
            artifact_class=kind,
            path=str(artifact),
            sha256=self._sha256(artifact),
            bytes_size=size,
            auto_execution_allowed=execution_allowed,
            findings=findings,
        )

    def validate_non_executable(
        self,
        path: str | Path,
    ) -> TrustedCandidateExecution:
        classification = self.classify(path)
        passed = bool(
            classification.artifact_class
            in {
                TrustedArtifactClass.MODEL_SAFETENSORS,
                TrustedArtifactClass.PURE_DATA_ASSET,
            }
            and not classification.findings
        )
        return TrustedCandidateExecution(
            candidate_id=Path(path).stem,
            artifact_class=classification.artifact_class,
            state=(
                CandidateExecutionState.PASS
                if passed
                else CandidateExecutionState.BLOCKED
            ),
            sandbox_profile_id=self.profile.profile_id,
            preflight_passed=passed,
            execution_attempted=False,
            execution_passed=False,
            workflow_sha256=classification.sha256,
            findings=list(classification.findings)
            + (
                ["DATA_ONLY_VALIDATION_NO_CODE_EXECUTION"]
                if passed
                else []
            ),
            metadata={
                "bytes_size": classification.bytes_size,
                "process_spawn_allowed": (
                    self.profile.process_spawn_allowed
                ),
                "public_network_allowed": (
                    self.profile.public_network_allowed
                ),
            },
            finished_at=utcnow(),
        )

    def execute_comfyui_workflow(
        self,
        *,
        candidate_id: str,
        workflow_path: str | Path,
        model_id: str,
        model_revision: str,
        output_dir: str | Path,
        execute: bool = True,
    ) -> TrustedCandidateExecution:
        started = utcnow()
        classification = self.classify(workflow_path)
        findings = list(classification.findings)
        if (
            classification.artifact_class
            is not TrustedArtifactClass.COMFYUI_WORKFLOW_JSON
        ):
            findings.append("NOT_COMFYUI_WORKFLOW_JSON")
        if not classification.auto_execution_allowed:
            return TrustedCandidateExecution(
                candidate_id=candidate_id,
                artifact_class=classification.artifact_class,
                state=CandidateExecutionState.BLOCKED,
                sandbox_profile_id=self.profile.profile_id,
                findings=sorted(set(findings)),
                started_at=started,
                finished_at=utcnow(),
            )

        workflow = json.loads(
            Path(workflow_path).read_text(encoding="utf-8")
        )
        node_count = sum(
            1
            for node in workflow.values()
            if isinstance(node, dict)
            and isinstance(node.get("class_type"), str)
        )
        if node_count > self.profile.max_workflow_nodes:
            findings.append("WORKFLOW_NODE_LIMIT_EXCEEDED")

        safety = self.workflow_safety.review(workflow)
        findings.extend(safety.findings)
        try:
            model = self.ctx.models.require_approved(
                model_id,
                model_revision,
            )
        except Exception as exc:
            model = None
            findings.append(
                "MODEL_NOT_PRODUCTION_APPROVED:"
                f"{type(exc).__name__}:{exc}"
            )

        try:
            executor = self.ctx.executors.get("local.comfyui")
        except Exception as exc:
            executor = None
            findings.append(
                "COMFYUI_EXECUTOR_UNAVAILABLE:"
                f"{type(exc).__name__}:{exc}"
            )

        if executor is not None:
            descriptor = executor.descriptor
            if (
                descriptor.network_scope
                is NetworkScope.PUBLIC_INTERNET
            ):
                findings.append(
                    "PUBLIC_NETWORK_EXECUTOR_BLOCKED"
                )
            if (
                descriptor.network_scope
                is NetworkScope.LOOPBACK_LAN
                and not self.profile.loopback_lan_allowed
            ):
                findings.append("LOOPBACK_LAN_NOT_ALLOWED")

        preflight = None
        if executor is not None and not findings:
            preflight = executor.preflight(workflow)
            if not preflight.valid:
                findings.extend(preflight.findings or [])
                findings.append("COMFYUI_PREFLIGHT_FAILED")

        preflight_passed = bool(
            not findings
            and safety.passed
            and model is not None
            and preflight is not None
            and preflight.valid
        )
        if not execute or not preflight_passed:
            return TrustedCandidateExecution(
                candidate_id=candidate_id,
                artifact_class=classification.artifact_class,
                state=(
                    CandidateExecutionState.PASS
                    if preflight_passed
                    else CandidateExecutionState.BLOCKED
                ),
                sandbox_profile_id=self.profile.profile_id,
                preflight_passed=preflight_passed,
                execution_attempted=False,
                execution_passed=False,
                workflow_sha256=(
                    preflight.workflow_sha256
                    if preflight is not None
                    else classification.sha256
                ),
                object_info_sha256=(
                    preflight.object_info_sha256
                    if preflight is not None
                    else None
                ),
                findings=sorted(set(findings)),
                metadata={
                    "node_count": node_count,
                    "model_id": model_id,
                    "model_revision": model_revision,
                    "local_only": True,
                },
                started_at=started,
                finished_at=utcnow(),
            )

        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        result = executor.execute(
            {
                "workflow": workflow,
                "output_dir": str(output),
            }
        )
        artifacts = [
            str(Path(item))
            for item in result.artifacts
            if Path(item).exists()
        ]
        if len(artifacts) > self.profile.max_output_files:
            findings.append("SANDBOX_OUTPUT_FILE_LIMIT_EXCEEDED")
        if not result.ok:
            findings.append(
                "TRUSTED_EXECUTOR_FAILED:"
                + str(result.error or "unknown")
            )
        execution_passed = bool(
            result.ok
            and artifacts
            and len(artifacts) <= self.profile.max_output_files
        )
        return TrustedCandidateExecution(
            candidate_id=candidate_id,
            artifact_class=classification.artifact_class,
            state=(
                CandidateExecutionState.PASS
                if execution_passed
                else CandidateExecutionState.FAIL
            ),
            sandbox_profile_id=self.profile.profile_id,
            preflight_passed=preflight_passed,
            execution_attempted=True,
            execution_passed=execution_passed,
            artifacts=artifacts,
            workflow_sha256=(
                preflight.workflow_sha256
                if preflight is not None
                else classification.sha256
            ),
            object_info_sha256=(
                preflight.object_info_sha256
                if preflight is not None
                else None
            ),
            findings=sorted(set(findings)),
            metadata={
                "node_count": node_count,
                "model_id": model_id,
                "model_revision": model_revision,
                "executor": "local.comfyui",
                "executor_metadata": dict(result.metadata or {}),
                "public_network_allowed": False,
                "process_spawn_allowed": False,
            },
            started_at=started,
            finished_at=utcnow(),
        )


class MultiShotBenchmarkMatrix:
    def __init__(
        self,
        execution_lab: CapabilityExecutionLab,
        *,
        minimum_dimension_score: float = 0.80,
        required_cases: int = 2,
    ) -> None:
        self.execution_lab = execution_lab
        self.minimum_dimension_score = float(
            minimum_dimension_score
        )
        self.required_cases = max(1, int(required_cases))

    def from_runtime_results(
        self,
        *,
        matrix_id: str,
        candidate_id: str,
        method_id: str,
        runtime_results: list[tuple[str, dict[str, Any]]],
    ) -> BenchmarkMatrixReport:
        rows: list[BenchmarkMatrixRow] = []
        for case_id, runtime_result in runtime_results:
            report = (
                self.execution_lab
                .benchmark_block_runtime_result(
                    case_id=case_id,
                    candidate_id=candidate_id,
                    method_id=method_id,
                    runtime_result=runtime_result,
                )
            )
            rows.append(
                BenchmarkMatrixRow(
                    case_id=case_id,
                    benchmark=report,
                )
            )

        dimensions: dict[str, list[float]] = {}
        for row in rows:
            for item in row.benchmark.dimensions:
                dimensions.setdefault(
                    item.name,
                    [],
                ).append(float(item.score))

        means = {
            name: sum(values) / len(values)
            for name, values in dimensions.items()
            if values
        }
        minima = {
            name: min(values)
            for name, values in dimensions.items()
            if values
        }
        aggregates = [
            row.benchmark.aggregate_score
            for row in rows
        ]
        blockers: list[str] = []
        if len(rows) < self.required_cases:
            blockers.append("BENCHMARK_MATRIX_INSUFFICIENT_CASES")
        for required in (
            "quality",
            "identity",
            "temporal",
            "camera_contract",
            "control",
        ):
            if required not in minima:
                blockers.append(
                    f"BENCHMARK_DIMENSION_MISSING:{required}"
                )
            elif minima[required] < self.minimum_dimension_score:
                blockers.append(
                    "BENCHMARK_DIMENSION_BELOW_FLOOR:"
                    f"{required}:{minima[required]:.4f}"
                )
        if any(
            row.benchmark.status is not LabGateStatus.PASS
            for row in rows
        ):
            blockers.append("BENCHMARK_CASE_FAILED")

        return BenchmarkMatrixReport(
            matrix_id=matrix_id,
            method_id=method_id,
            rows=rows,
            dimension_means=means,
            dimension_minima=minima,
            aggregate_mean=(
                sum(aggregates) / len(aggregates)
                if aggregates
                else 0.0
            ),
            aggregate_minimum=(
                min(aggregates)
                if aggregates
                else 0.0
            ),
            required_cases=self.required_cases,
            minimum_dimension_score=(
                self.minimum_dimension_score
            ),
            passed=not blockers,
            blockers=sorted(set(blockers)),
        )


class CandidatePromotionController:
    """Promote safe declarative artifacts without granting extra authority.

    Workflow registration is allowed only after trusted lab evidence, approved
    model, safe local workflow preflight, and successful trusted execution.
    Production executability is a separate MethodSwitch assessment.
    """

    def __init__(
        self,
        ctx: Any,
        *,
        store: CandidatePromotionStore | None = None,
        workflow_registry: WorkflowRegistry | None = None,
    ) -> None:
        self.ctx = ctx
        self.store = store or CandidatePromotionStore(
            Path(ctx.root)
            / "data"
            / "studio"
            / "candidate_promotion"
        )
        self.workflow_registry = (
            workflow_registry
            or ctx.workflows
        )
        self.executor = TrustedCandidateLabExecutor(ctx)

    @staticmethod
    def _file_sha256(path: str | Path) -> str:
        return hashlib.sha256(
            Path(path).read_bytes()
        ).hexdigest()

    def _load_evidence_package(
        self,
        path: str | Path,
    ) -> QualificationEvidencePackage:
        report_path = Path(path).resolve()
        trusted_root = (
            self.ctx.capability_execution_lab
            .store.reports.resolve()
        )
        try:
            report_path.relative_to(trusted_root)
        except ValueError as exc:
            raise RuntimeError(
                "PROMOTION_EVIDENCE_OUTSIDE_TRUSTED_LAB"
            ) from exc
        package = QualificationEvidencePackage.model_validate_json(
            report_path.read_text(encoding="utf-8")
        )
        if not package.passed:
            raise RuntimeError(
                "PROMOTION_EVIDENCE_PACKAGE_NOT_PASSED"
            )
        return package

    def _install_workflow(
        self,
        *,
        workflow_path: str | Path,
        manifest: WorkflowManifest,
    ) -> tuple[Path, Path]:
        source = Path(workflow_path).resolve()
        slug = re.sub(
            r"[^A-Za-z0-9._-]+",
            "_",
            f"{manifest.workflow_id}_{manifest.version}",
        )
        target_dir = (
            self.workflow_registry.root
            / "promoted"
            / slug
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        workflow_target = (
            target_dir / "workflow.json"
        )
        manifest_target = (
            target_dir / "workflow.manifest.yaml"
        )

        source_hash = self._file_sha256(source)
        if workflow_target.exists():
            existing_hash = self._file_sha256(
                workflow_target
            )
            if existing_hash != source_hash:
                raise RuntimeError(
                    "PROMOTION_WORKFLOW_VERSION_COLLISION"
                )
        else:
            shutil.copy2(source, workflow_target)

        manifest_payload = manifest.model_copy(
            update={"workflow_file": workflow_target.name}
        ).model_dump(mode="json")
        if manifest_target.exists():
            existing = WorkflowManifest.model_validate(
                yaml.safe_load(
                    manifest_target.read_text(
                        encoding="utf-8"
                    )
                )
            )
            if existing != WorkflowManifest.model_validate(
                manifest_payload
            ):
                raise RuntimeError(
                    "PROMOTION_MANIFEST_VERSION_COLLISION"
                )
        else:
            manifest_target.write_text(
                yaml.safe_dump(
                    manifest_payload,
                    sort_keys=False,
                    allow_unicode=True,
                ),
                encoding="utf-8",
            )
        self.workflow_registry.load()
        return workflow_target, manifest_target

    def promote_comfyui_workflow(
        self,
        *,
        candidate_id: str,
        workflow_path: str | Path,
        manifest: WorkflowManifest,
        evidence_package_path: str | Path,
        output_dir: str | Path,
        benchmark_matrix_path: str | Path | None = None,
        method_request: MethodSwitchRequest | None = None,
        execute: bool = True,
    ) -> PromotionAttestation:
        blockers: list[str] = []
        package = None
        try:
            package = self._load_evidence_package(
                evidence_package_path
            )
        except Exception as exc:
            blockers.append(
                f"EVIDENCE_GATE:{type(exc).__name__}:{exc}"
            )

        execution = (
            self.executor.execute_comfyui_workflow(
                candidate_id=candidate_id,
                workflow_path=workflow_path,
                model_id=manifest.model_id,
                model_revision=(
                    manifest.model_revision or ""
                ),
                output_dir=output_dir,
                execute=execute,
            )
        )
        if execution.state is not CandidateExecutionState.PASS:
            blockers.extend(execution.findings)
            blockers.append("TRUSTED_CANDIDATE_EXECUTION_NOT_PASSED")
        if not execution.execution_passed and execute:
            blockers.append("TRUSTED_CANDIDATE_RUNTIME_NOT_PASSED")
        if not manifest.local_only:
            blockers.append("PROMOTION_REQUIRES_LOCAL_ONLY_WORKFLOW")
        if manifest.executor_id != "local.comfyui":
            blockers.append("PROMOTION_EXECUTOR_NOT_COMFYUI")
        if not manifest.model_revision:
            blockers.append("PROMOTION_MODEL_REVISION_MISSING")

        matrix_path_str = None
        if benchmark_matrix_path is not None:
            matrix_path = Path(
                benchmark_matrix_path
            ).resolve()
            if not matrix_path.is_file():
                blockers.append(
                    "BENCHMARK_MATRIX_FILE_MISSING"
                )
            else:
                try:
                    matrix = (
                        BenchmarkMatrixReport
                        .model_validate_json(
                            matrix_path.read_text(
                                encoding="utf-8"
                            )
                        )
                    )
                    if not matrix.passed:
                        blockers.append(
                            "BENCHMARK_MATRIX_NOT_PASSED"
                        )
                    matrix_path_str = str(matrix_path)
                except Exception as exc:
                    blockers.append(
                        "BENCHMARK_MATRIX_INVALID:"
                        f"{type(exc).__name__}:{exc}"
                    )

        workflow_target = None
        manifest_target = None
        state = PromotionState.BLOCKED
        if not blockers and package is not None:
            workflow_target, manifest_target = (
                self._install_workflow(
                    workflow_path=workflow_path,
                    manifest=manifest,
                )
            )
            state = PromotionState.REGISTRY_PROMOTED

        method_assessment: dict[str, Any] = {}
        if (
            state is PromotionState.REGISTRY_PROMOTED
            and method_request is not None
        ):
            spec = next(
                (
                    item
                    for item in self.ctx.method_switch.specs
                    if item.method_id == package.method_id
                ),
                None,
            )
            if spec is None:
                blockers.append(
                    "PROMOTED_WORKFLOW_METHOD_SPEC_MISSING"
                )
            else:
                assessment = (
                    self.ctx.method_switch.assess(
                        method_request,
                        spec,
                    )
                )
                method_assessment = assessment.model_dump(
                    mode="json"
                )
                if assessment.execution_ready:
                    if matrix_path_str is None:
                        blockers.append(
                            "PRODUCTION_PROMOTION_REQUIRES_BENCHMARK_MATRIX"
                        )
                    else:
                        state = (
                            PromotionState.PRODUCTION_EXECUTABLE
                        )
                else:
                    blockers.extend(
                        assessment.blockers
                    )

        attestation_id = (
            "PROMOTE_"
            + hashlib.sha256(
                (
                    candidate_id
                    + "|"
                    + manifest.workflow_id
                    + "|"
                    + manifest.version
                ).encode("utf-8")
            ).hexdigest()[:16]
        )
        attestation = PromotionAttestation(
            attestation_id=attestation_id,
            candidate_id=candidate_id,
            state=state,
            artifact_class=(
                TrustedArtifactClass.COMFYUI_WORKFLOW_JSON
            ),
            workflow_id=manifest.workflow_id,
            workflow_version=manifest.version,
            tool_id="comfyui",
            method_id=(
                package.method_id
                if package is not None
                else None
            ),
            evidence_package_path=(
                str(Path(evidence_package_path).resolve())
                if package is not None
                else None
            ),
            evidence_package_sha256=(
                self._file_sha256(evidence_package_path)
                if package is not None
                else None
            ),
            execution_evidence=execution,
            benchmark_matrix_path=matrix_path_str,
            promoted_manifest_path=(
                str(manifest_target)
                if manifest_target is not None
                else None
            ),
            promoted_workflow_path=(
                str(workflow_target)
                if workflow_target is not None
                else None
            ),
            method_assessment=method_assessment,
            blockers=sorted(set(blockers)),
        )
        self.store.save_attestation(attestation)
        return attestation


    def qualify_and_promote_comfyui_workflow(
        self,
        *,
        candidate_id: str,
        workflow_path: str | Path,
        manifest: WorkflowManifest,
        source_uri: str,
        source_type: str,
        expected_sha256: str,
        output_dir: str | Path,
        required_vram_gb: float | None = None,
        benchmark_matrix: BenchmarkMatrixReport | None = None,
        method_request: MethodSwitchRequest | None = None,
        rights_cleared: bool = False,
        execution_evidence: TrustedCandidateExecution | None = None,
    ) -> PromotionAttestation:
        """Build trusted evidence, then promote only if every registry gate passes."""

        if not rights_cleared:
            attestation = PromotionAttestation(
                attestation_id=(
                    "PROMOTE_"
                    + hashlib.sha256(
                        (
                            candidate_id
                            + "|rights-blocked"
                        ).encode("utf-8")
                    ).hexdigest()[:16]
                ),
                candidate_id=candidate_id,
                state=PromotionState.BLOCKED,
                artifact_class=(
                    TrustedArtifactClass
                    .COMFYUI_WORKFLOW_JSON
                ),
                workflow_id=manifest.workflow_id,
                workflow_version=manifest.version,
                tool_id="comfyui",
                blockers=[
                    "COMMERCIAL_RIGHTS_NOT_CLEARED"
                ],
            )
            self.store.save_attestation(attestation)
            return attestation

        lab = self.ctx.capability_execution_lab
        provenance = lab.import_local_artifact(
            case_id=(
                "PROMOTION_" + candidate_id
            ),
            candidate_id=candidate_id,
            source_path=workflow_path,
            source_uri=source_uri,
            source_type=source_type,
            version=manifest.version,
            expected_sha256=expected_sha256,
        )
        sbom = lab.generate_sbom(
            case_id="PROMOTION_" + candidate_id,
            manifest=provenance,
        )
        security = lab.static_security_scan(
            case_id="PROMOTION_" + candidate_id,
            manifest=provenance,
        )
        hardware = lab.hardware_fit(
            case_id="PROMOTION_" + candidate_id,
            candidate_id=candidate_id,
            required_vram_gb=required_vram_gb,
            gpu_snapshot=(
                __import__(
                    "cinefactory.turbo.metrics",
                    fromlist=["gpu_snapshot"],
                ).gpu_snapshot()
            ),
        )

        execution = (
            execution_evidence
            or self.executor.execute_comfyui_workflow(
                candidate_id=candidate_id,
                workflow_path=workflow_path,
                model_id=manifest.model_id,
                model_revision=(
                    manifest.model_revision or ""
                ),
                output_dir=output_dir,
                execute=True,
            )
        )
        if (
            execution.candidate_id != candidate_id
            or execution.artifact_class
            is not TrustedArtifactClass.COMFYUI_WORKFLOW_JSON
        ):
            raise RuntimeError(
                "CANDIDATE_EXECUTION_EVIDENCE_MISMATCH"
            )

        sandbox = lab.sandbox_gate(
            case_id="PROMOTION_" + candidate_id,
            candidate_id=candidate_id,
            security=security,
            trusted_executor_id=(
                "local.comfyui"
                if execution.execution_passed
                else None
            ),
            trusted_executor_passed=(
                execution.execution_passed
            ),
            output_refs=list(execution.artifacts),
        )

        workflow_scores = [
            BenchmarkDimension(
                name="safety",
                score=(
                    1.0
                    if security.status
                    is LabGateStatus.PASS
                    else 0.0
                ),
                evidence_refs=[
                    "static_security_scan",
                ],
            ),
            BenchmarkDimension(
                name="runtime",
                score=(
                    1.0
                    if execution.execution_passed
                    else 0.0
                ),
                evidence_refs=[
                    "trusted_candidate_execution",
                ],
            ),
            BenchmarkDimension(
                name="local_policy",
                score=(
                    1.0
                    if (
                        manifest.local_only
                        and not self.executor.profile
                        .public_network_allowed
                    )
                    else 0.0
                ),
                evidence_refs=[
                    "workflow_manifest.local_only",
                    "candidate_sandbox_profile",
                ],
            ),
            BenchmarkDimension(
                name="model_approval",
                score=(
                    1.0
                    if execution.preflight_passed
                    else 0.0
                ),
                evidence_refs=[
                    "model_registry",
                    "comfyui_preflight",
                ],
            ),
            BenchmarkDimension(
                name="artifact_output",
                score=(
                    1.0
                    if execution.artifacts
                    else 0.0
                ),
                evidence_refs=[
                    "trusted_executor_artifacts",
                ],
            ),
        ]
        benchmark = lab.benchmark_gate(
            case_id="PROMOTION_" + candidate_id,
            candidate_id=candidate_id,
            method_id=(
                method_request.current_method_id
                if method_request is not None
                else None
            ),
            dimensions=workflow_scores,
        )

        adapter_registered = False
        try:
            self.ctx.executors.get(
                manifest.executor_id
            )
            adapter_registered = True
        except Exception:
            pass
        handler_registered = (
            "comfy.execute"
            in self.ctx.method_switch.registered_handlers
        )
        conformance = lab.conformance_gate(
            case_id="PROMOTION_" + candidate_id,
            candidate_id=candidate_id,
            adapter_registered=adapter_registered,
            handler_registered=handler_registered,
            normalization_passed=True,
            canonical_roundtrip_passed=True,
        )
        package = lab.package(
            case_id="PROMOTION_" + candidate_id,
            candidate_id=candidate_id,
            tool_id="comfyui",
            method_id=(
                next(
                    (
                        item.method_id
                        for item
                        in self.ctx.method_switch.specs
                        if item.tool_id == "comfyui"
                    ),
                    None,
                )
                if method_request is not None
                else None
            ),
            provenance=provenance,
            sbom=sbom,
            security=security,
            hardware=hardware,
            sandbox=sandbox,
            benchmark=benchmark,
            conformance=conformance,
        )
        package_path = (
            lab.store.report_path(
                "PROMOTION_" + candidate_id,
                candidate_id,
                "qualification_evidence",
            )
        )

        matrix_path = None
        if benchmark_matrix is not None:
            matrix_path = self.store.save_matrix(
                benchmark_matrix
            )

        return self.promote_comfyui_workflow(
            candidate_id=candidate_id,
            workflow_path=workflow_path,
            manifest=manifest,
            evidence_package_path=package_path,
            output_dir=output_dir,
            benchmark_matrix_path=matrix_path,
            method_request=method_request,
            execute=False,
        )


    def attest_registered_method(
        self,
        *,
        candidate_id: str,
        method_id: str,
        evidence_package_path: str | Path,
        benchmark_matrix: BenchmarkMatrixReport,
        method_request: MethodSwitchRequest,
    ) -> PromotionAttestation:
        blockers: list[str] = []
        try:
            package = self._load_evidence_package(
                evidence_package_path
            )
        except Exception as exc:
            package = None
            blockers.append(
                f"EVIDENCE_GATE:{type(exc).__name__}:{exc}"
            )

        if package is not None and package.method_id != method_id:
            blockers.append(
                "QUALIFICATION_PACKAGE_METHOD_MISMATCH"
            )
        if benchmark_matrix.method_id != method_id:
            blockers.append(
                "BENCHMARK_MATRIX_METHOD_MISMATCH"
            )
        if not benchmark_matrix.passed:
            blockers.extend(benchmark_matrix.blockers)
            blockers.append("BENCHMARK_MATRIX_NOT_PASSED")

        matrix_path = self.store.save_matrix(
            benchmark_matrix
        )
        spec = next(
            (
                item
                for item in self.ctx.method_switch.specs
                if item.method_id == method_id
            ),
            None,
        )
        method_assessment: dict[str, Any] = {}
        if spec is None:
            blockers.append(
                "REGISTERED_METHOD_SPEC_MISSING"
            )
        else:
            assessment = self.ctx.method_switch.assess(
                method_request,
                spec,
            )
            method_assessment = assessment.model_dump(
                mode="json"
            )
            if not assessment.execution_ready:
                blockers.extend(assessment.blockers)

        state = (
            PromotionState.PRODUCTION_EXECUTABLE
            if not blockers
            else PromotionState.BLOCKED
        )
        attestation = PromotionAttestation(
            attestation_id=(
                "METHOD_ATTEST_"
                + hashlib.sha256(
                    (
                        candidate_id
                        + "|"
                        + method_id
                        + "|"
                        + benchmark_matrix.matrix_id
                    ).encode("utf-8")
                ).hexdigest()[:16]
            ),
            candidate_id=candidate_id,
            state=state,
            artifact_class=(
                TrustedArtifactClass
                .REGISTERED_METHOD_MANIFEST
            ),
            tool_id=(
                spec.tool_id
                if spec is not None
                else None
            ),
            method_id=method_id,
            evidence_package_path=(
                str(Path(evidence_package_path).resolve())
                if package is not None
                else None
            ),
            evidence_package_sha256=(
                self._file_sha256(
                    evidence_package_path
                )
                if package is not None
                else None
            ),
            benchmark_matrix_path=str(matrix_path),
            method_assessment=method_assessment,
            blockers=sorted(set(blockers)),
        )
        self.store.save_attestation(attestation)
        return attestation


    def build_comfyui_lab_work_item(
        self,
        *,
        project_id: str,
        case_id: str,
        candidate_id: str,
        workflow_path: str | Path,
        manifest: WorkflowManifest,
        output_dir: str | Path,
        required_vram_gb: float | None = None,
    ) -> WorkItem:
        digest = hashlib.sha256(
            (
                case_id
                + "|"
                + candidate_id
                + "|"
                + manifest.workflow_id
                + "|"
                + manifest.version
            ).encode("utf-8")
        ).hexdigest()[:16]
        return WorkItem(
            work_id=f"WORK_LAB_{digest}",
            project_id=project_id,
            kind="lab.comfyui.candidate",
            handler="lab.comfyui.execute",
            resource=ResourceClass.GPU,
            priority=86,
            model_affinity=(
                "COMFYUI:"
                + manifest.model_id
                + "@"
                + str(manifest.model_revision or "")
            ),
            payload={
                "case_id": case_id,
                "candidate_id": candidate_id,
                "workflow_path": str(
                    Path(workflow_path).resolve()
                ),
                "workflow_manifest": manifest.model_dump(
                    mode="json"
                ),
                "output_dir": str(
                    Path(output_dir).resolve()
                ),
                "required_vram_gb": required_vram_gb,
                "trusted_candidate_lab": True,
            },
            max_attempts=1,
        )

    def execute_comfyui_lab_work_item(
        self,
        item: WorkItem,
    ) -> dict[str, Any]:
        payload = dict(item.payload)
        if not payload.get("trusted_candidate_lab"):
            raise RuntimeError(
                "CANDIDATE_LAB_TRUST_MARKER_MISSING"
            )
        manifest = WorkflowManifest.model_validate(
            payload["workflow_manifest"]
        )
        evidence = (
            self.executor.execute_comfyui_workflow(
                candidate_id=str(
                    payload["candidate_id"]
                ),
                workflow_path=str(
                    payload["workflow_path"]
                ),
                model_id=manifest.model_id,
                model_revision=(
                    manifest.model_revision or ""
                ),
                output_dir=str(payload["output_dir"]),
                execute=True,
            )
        )
        return {
            "candidate_execution": evidence.model_dump(
                mode="json"
            ),
            "passed": (
                evidence.state
                is CandidateExecutionState.PASS
                and evidence.execution_passed
            ),
        }
