from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import zipfile
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LabGateStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class SecuritySeverity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ArtifactKind(StrEnum):
    FILE = "FILE"
    ZIP = "ZIP"
    DIRECTORY = "DIRECTORY"


class ProvenanceManifest(BaseModel):
    candidate_id: str
    source_uri: str
    source_type: str
    source_path: str
    imported_path: str
    artifact_kind: ArtifactKind
    sha256: str
    bytes_size: int = Field(ge=0)
    version: str | None = None
    expected_sha256: str | None = None
    hash_verified: bool = False
    captured_at: datetime = Field(default_factory=utcnow)


class SBOMEntry(BaseModel):
    ecosystem: str
    name: str
    version: str | None = None
    evidence_path: str


class SBOMReport(BaseModel):
    status: LabGateStatus
    entries: list[SBOMEntry] = Field(default_factory=list)
    manifests: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class SecurityFinding(BaseModel):
    severity: SecuritySeverity
    code: str
    path: str
    line: int | None = None
    detail: str


class StaticSecurityReport(BaseModel):
    status: LabGateStatus
    scanned_files: int = 0
    scanned_bytes: int = 0
    findings: list[SecurityFinding] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class HardwareFitReport(BaseModel):
    status: LabGateStatus
    target_gpu: str = "NVIDIA RTX 3060 12GB"
    required_vram_gb: float | None = None
    available_vram_gb: float | None = None
    findings: list[str] = Field(default_factory=list)


class SandboxReport(BaseModel):
    status: LabGateStatus
    executor_id: str | None = None
    findings: list[str] = Field(default_factory=list)
    output_refs: list[str] = Field(default_factory=list)


class BenchmarkDimension(BaseModel):
    name: str
    score: float = Field(ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list)


class BenchmarkReport(BaseModel):
    status: LabGateStatus
    method_id: str | None = None
    dimensions: list[BenchmarkDimension] = Field(default_factory=list)
    aggregate_score: float = Field(default=0.0, ge=0.0, le=1.0)
    minimum_required: float = Field(default=0.0, ge=0.0, le=1.0)
    findings: list[str] = Field(default_factory=list)


class ConformanceReport(BaseModel):
    status: LabGateStatus
    checks: dict[str, bool] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)


class QualificationEvidencePackage(BaseModel):
    package_id: str
    candidate_id: str
    tool_id: str | None = None
    method_id: str | None = None
    provenance_path: str
    sbom_path: str
    security_path: str
    hardware_path: str
    sandbox_path: str
    benchmark_path: str
    conformance_path: str
    passed: bool = False
    blockers: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class ExecutionLabPolicy(BaseModel):
    max_import_bytes: int = 4 * 1024 * 1024 * 1024
    max_archive_members: int = 10000
    max_archive_uncompressed_bytes: int = 8 * 1024 * 1024 * 1024
    max_text_scan_bytes_per_file: int = 2 * 1024 * 1024
    block_executable_extensions: set[str] = Field(
        default_factory=lambda: {
            ".exe", ".dll", ".msi", ".scr", ".com",
        }
    )
    block_critical_static_findings: bool = True
    benchmark_floor: float = Field(default=0.80, ge=0.0, le=1.0)


class CapabilityExecutionLabStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.imports = self.root / "imports"
        self.reports = self.root / "reports"
        self.sandboxes = self.root / "sandboxes"
        for path in (self.imports, self.reports, self.sandboxes):
            path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def safe(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value)

    @classmethod
    def compact_key(cls, value: str) -> str:
        safe = cls.safe(value).strip("._-")
        prefix = safe[:18] or "item"
        digest = hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()[:8]
        return f"{prefix}-{digest}"

    def candidate_root(self, case_id: str, candidate_id: str) -> Path:
        root = (
            self.reports
            / self.compact_key(case_id)
            / self.compact_key(candidate_id)
        )
        root.mkdir(parents=True, exist_ok=True)
        return root

    def report_path(
        self,
        case_id: str,
        candidate_id: str,
        name: str,
    ) -> Path:
        return self.candidate_root(case_id, candidate_id) / f"{name}.json"

    def save_model(
        self,
        case_id: str,
        candidate_id: str,
        name: str,
        model,
    ) -> Path:
        path = self.report_path(case_id, candidate_id, name)
        path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
        return path


class CapabilityExecutionLab:
    """Controlled local evidence lab.

    This class never downloads remote artifacts and never executes untrusted
    candidate code. It imports an already-local artifact into a content-addressed
    lab area, produces deterministic supply-chain evidence, and only permits an
    execution benchmark when the candidate points to a method already registered
    as executable by the production MethodSwitchController.
    """

    TEXT_SUFFIXES = {
        ".py", ".pyw", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml",
        ".yml", ".toml", ".ini", ".cfg", ".txt", ".md", ".ps1", ".bat",
        ".cmd", ".sh", ".xml", ".html", ".css",
    }
    STATIC_PATTERNS = [
        (
            re.compile(r"\bos\.system\s*\(", re.I),
            SecuritySeverity.CRITICAL,
            "OS_SYSTEM_EXECUTION",
        ),
        (
            re.compile(r"subprocess\.[A-Za-z_]+\([^\n]{0,300}shell\s*=\s*True", re.I),
            SecuritySeverity.CRITICAL,
            "SUBPROCESS_SHELL_TRUE",
        ),
        (
            re.compile(r"\b(eval|exec)\s*\(", re.I),
            SecuritySeverity.HIGH,
            "DYNAMIC_CODE_EXECUTION",
        ),
        (
            re.compile(r"\bpickle\.loads?\s*\(", re.I),
            SecuritySeverity.HIGH,
            "UNSAFE_PICKLE_LOAD",
        ),
        (
            re.compile(r"Invoke-WebRequest|Invoke-RestMethod", re.I),
            SecuritySeverity.HIGH,
            "POWERSHELL_NETWORK_FETCH",
        ),
        (
            re.compile(r"\b(curl|wget)\s+https?://", re.I),
            SecuritySeverity.HIGH,
            "SHELL_NETWORK_FETCH",
        ),
        (
            re.compile(r"requests\.(get|post|put|delete|patch)\s*\(\s*['\"]https?://", re.I),
            SecuritySeverity.MEDIUM,
            "DIRECT_PUBLIC_HTTP",
        ),
        (
            re.compile(r"socket\.(socket|create_connection)\s*\(", re.I),
            SecuritySeverity.MEDIUM,
            "RAW_SOCKET_USAGE",
        ),
    ]

    def __init__(
        self,
        root: str | Path,
        *,
        policy: ExecutionLabPolicy | None = None,
    ) -> None:
        self.root = Path(root)
        self.policy = policy or ExecutionLabPolicy()
        # Keep this root intentionally compact. The repository is
        # commonly located under a long Windows Downloads path; deeply nested
        # content-addressed evidence paths can otherwise exceed legacy MAX_PATH.
        self.store = CapabilityExecutionLabStore(
            self.root / ".cflab"
        )

    @staticmethod
    def _hash_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _hash_directory(path: Path) -> tuple[str, int]:
        h = hashlib.sha256()
        total = 0
        files = sorted(p for p in path.rglob("*") if p.is_file())
        for file in files:
            rel = file.relative_to(path).as_posix()
            h.update(rel.encode("utf-8"))
            h.update(b"\0")
            with file.open("rb") as fh:
                for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                    total += len(chunk)
                    h.update(chunk)
            h.update(b"\0")
        return h.hexdigest(), total

    def import_local_artifact(
        self,
        *,
        case_id: str,
        candidate_id: str,
        source_path: str | Path,
        source_uri: str,
        source_type: str,
        version: str | None,
        expected_sha256: str | None,
    ) -> ProvenanceManifest:
        source = Path(source_path).resolve()
        if not source.exists():
            raise FileNotFoundError(source)
        if source.is_dir():
            digest, size = self._hash_directory(source)
            kind = ArtifactKind.DIRECTORY
        else:
            size = source.stat().st_size
            if size > self.policy.max_import_bytes:
                raise ValueError("ARTIFACT_IMPORT_SIZE_LIMIT")
            digest = self._hash_file(source)
            kind = (
                ArtifactKind.ZIP
                if source.suffix.lower() == ".zip"
                else ArtifactKind.FILE
            )
        verified = bool(
            expected_sha256
            and digest.lower() == expected_sha256.lower()
        )
        # Imports are content-addressed globally. Keep the physical
        # path extremely short because the repository commonly lives under a
        # long Windows Downloads path and pytest adds another deep temp root.
        # Case/candidate identity remains in the provenance/report metadata.
        dest_root = (
            self.store.imports
            / digest[:20]
        )
        dest_root.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            dest = dest_root / "tree"
            if not dest.exists():
                shutil.copytree(source, dest)
        else:
            suffix = source.suffix.lower()
            if len(suffix) > 12:
                suffix = ".blob"
            dest = dest_root / ("artifact" + suffix)
            if not dest.exists():
                shutil.copy2(source, dest)
        manifest = ProvenanceManifest(
            candidate_id=candidate_id,
            source_uri=source_uri,
            source_type=source_type,
            source_path=str(source),
            imported_path=str(dest),
            artifact_kind=kind,
            sha256=digest,
            bytes_size=size,
            version=version,
            expected_sha256=expected_sha256,
            hash_verified=verified,
        )
        self.store.save_model(
            case_id, candidate_id, "provenance", manifest
        )
        return manifest

    def _archive_members(self, path: Path) -> tuple[list[str], list[str]]:
        members: list[str] = []
        blockers: list[str] = []
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) > self.policy.max_archive_members:
                blockers.append("ARCHIVE_MEMBER_LIMIT_EXCEEDED")
            total = sum(max(0, int(item.file_size)) for item in infos)
            if total > self.policy.max_archive_uncompressed_bytes:
                blockers.append("ARCHIVE_EXPANSION_LIMIT_EXCEEDED")
            for item in infos:
                normalized = item.filename.replace("\\", "/")
                path_obj = Path(normalized)
                if (
                    path_obj.is_absolute()
                    or ".." in path_obj.parts
                    or re.match(r"^[A-Za-z]:", normalized)
                ):
                    blockers.append(
                        f"ARCHIVE_PATH_TRAVERSAL:{normalized}"
                    )
                    continue
                members.append(normalized)
        return members, blockers

    def _iter_text_units(
        self,
        manifest: ProvenanceManifest,
    ):
        imported = Path(manifest.imported_path)
        if manifest.artifact_kind is ArtifactKind.DIRECTORY:
            for file in sorted(imported.rglob("*")):
                if file.is_file() and file.suffix.lower() in self.TEXT_SUFFIXES:
                    yield file.relative_to(imported).as_posix(), file.read_bytes()
            return
        if manifest.artifact_kind is ArtifactKind.ZIP:
            with zipfile.ZipFile(imported) as archive:
                for info in archive.infolist():
                    suffix = Path(info.filename).suffix.lower()
                    if (
                        not info.is_dir()
                        and suffix in self.TEXT_SUFFIXES
                        and info.file_size <= self.policy.max_text_scan_bytes_per_file
                    ):
                        yield info.filename, archive.read(info)
            return
        if imported.suffix.lower() in self.TEXT_SUFFIXES:
            yield imported.name, imported.read_bytes()

    def static_security_scan(
        self,
        *,
        case_id: str,
        manifest: ProvenanceManifest,
    ) -> StaticSecurityReport:
        findings: list[SecurityFinding] = []
        blockers: list[str] = []
        imported = Path(manifest.imported_path)
        if manifest.artifact_kind is ArtifactKind.ZIP:
            members, archive_blockers = self._archive_members(imported)
            blockers.extend(archive_blockers)
            for member in members:
                if Path(member).suffix.lower() in self.policy.block_executable_extensions:
                    findings.append(
                        SecurityFinding(
                            severity=SecuritySeverity.HIGH,
                            code="EMBEDDED_EXECUTABLE",
                            path=member,
                            detail="archive contains an executable binary",
                        )
                    )
        elif manifest.artifact_kind is ArtifactKind.DIRECTORY:
            for file in imported.rglob("*"):
                if (
                    file.is_file()
                    and file.suffix.lower() in self.policy.block_executable_extensions
                ):
                    findings.append(
                        SecurityFinding(
                            severity=SecuritySeverity.HIGH,
                            code="EMBEDDED_EXECUTABLE",
                            path=file.relative_to(imported).as_posix(),
                            detail="directory contains an executable binary",
                        )
                    )
        elif imported.suffix.lower() in self.policy.block_executable_extensions:
            findings.append(
                SecurityFinding(
                    severity=SecuritySeverity.HIGH,
                    code="EXECUTABLE_ARTIFACT",
                    path=imported.name,
                    detail="direct executable imports require a dedicated signed-binary review",
                )
            )

        scanned_files = 0
        scanned_bytes = 0
        for logical_path, raw in self._iter_text_units(manifest):
            scanned_files += 1
            raw = raw[: self.policy.max_text_scan_bytes_per_file]
            scanned_bytes += len(raw)
            text = raw.decode("utf-8", errors="ignore")
            for lineno, line in enumerate(text.splitlines(), 1):
                for pattern, severity, code in self.STATIC_PATTERNS:
                    if pattern.search(line):
                        findings.append(
                            SecurityFinding(
                                severity=severity,
                                code=code,
                                path=logical_path,
                                line=lineno,
                                detail=line.strip()[:300],
                            )
                        )

        if not manifest.hash_verified:
            blockers.append("EXPECTED_HASH_NOT_VERIFIED")
        if self.policy.block_critical_static_findings and any(
            item.severity is SecuritySeverity.CRITICAL for item in findings
        ):
            blockers.append("CRITICAL_STATIC_SECURITY_FINDING")
        status = LabGateStatus.PASS if not blockers else LabGateStatus.FAIL
        report = StaticSecurityReport(
            status=status,
            scanned_files=scanned_files,
            scanned_bytes=scanned_bytes,
            findings=findings,
            blockers=sorted(set(blockers)),
        )
        self.store.save_model(
            case_id, manifest.candidate_id, "security", report
        )
        return report

    @staticmethod
    def _parse_requirement_line(line: str) -> tuple[str, str | None] | None:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            return None
        match = re.match(
            r"^([A-Za-z0-9_.-]+)\s*(?:==|~=|>=|<=|>|<)?\s*([^;\s]+)?",
            line,
        )
        if not match:
            return None
        return match.group(1), match.group(2)

    def generate_sbom(
        self,
        *,
        case_id: str,
        manifest: ProvenanceManifest,
    ) -> SBOMReport:
        entries: list[SBOMEntry] = []
        manifests: list[str] = []
        findings: list[str] = []
        for logical_path, raw in self._iter_text_units(manifest):
            name = Path(logical_path).name.lower()
            if name in {"requirements.txt", "requirements-dev.txt"}:
                manifests.append(logical_path)
                for line in raw.decode("utf-8", errors="ignore").splitlines():
                    parsed = self._parse_requirement_line(line)
                    if parsed:
                        entries.append(
                            SBOMEntry(
                                ecosystem="python",
                                name=parsed[0],
                                version=parsed[1],
                                evidence_path=logical_path,
                            )
                        )
            elif name == "package.json":
                manifests.append(logical_path)
                try:
                    package = json.loads(raw.decode("utf-8"))
                except Exception:
                    findings.append(f"INVALID_PACKAGE_JSON:{logical_path}")
                    continue
                for section in ("dependencies", "devDependencies"):
                    for dep, version in sorted((package.get(section) or {}).items()):
                        entries.append(
                            SBOMEntry(
                                ecosystem="npm",
                                name=str(dep),
                                version=str(version),
                                evidence_path=logical_path,
                            )
                        )
            elif name == "pyproject.toml":
                manifests.append(logical_path)
                findings.append(
                    f"PYPROJECT_PRESENT_MANUAL_LOCK_RESOLUTION_REQUIRED:{logical_path}"
                )
        status = LabGateStatus.PASS
        report = SBOMReport(
            status=status,
            entries=entries,
            manifests=manifests,
            findings=findings,
        )
        self.store.save_model(
            case_id, manifest.candidate_id, "sbom", report
        )
        return report

    def hardware_fit(
        self,
        *,
        case_id: str,
        candidate_id: str,
        required_vram_gb: float | None,
        gpu_snapshot: dict[str, Any] | None,
    ) -> HardwareFitReport:
        available = None
        findings: list[str] = []
        snapshot = gpu_snapshot or {}
        gpus = snapshot.get("gpus") or []
        if gpus:
            available = float(gpus[0].get("vram_mb", 0) or 0) / 1024
        if required_vram_gb is None:
            status = LabGateStatus.PASS
            findings.append("VRAM_REQUIREMENT_UNSPECIFIED")
        elif available is None:
            status = LabGateStatus.BLOCKED
            findings.append("GPU_VRAM_EVIDENCE_UNAVAILABLE")
        elif required_vram_gb <= available:
            status = LabGateStatus.PASS
        else:
            status = LabGateStatus.FAIL
            findings.append("VRAM_REQUIREMENT_EXCEEDS_DEVICE")
        report = HardwareFitReport(
            status=status,
            required_vram_gb=required_vram_gb,
            available_vram_gb=available,
            findings=findings,
        )
        self.store.save_model(
            case_id, candidate_id, "hardware", report
        )
        return report

    def sandbox_gate(
        self,
        *,
        case_id: str,
        candidate_id: str,
        security: StaticSecurityReport,
        trusted_executor_id: str | None = None,
        trusted_executor_passed: bool = False,
        output_refs: list[str] | None = None,
    ) -> SandboxReport:
        if security.status is not LabGateStatus.PASS:
            status = LabGateStatus.BLOCKED
            findings = ["SECURITY_GATE_NOT_PASSED"]
        elif trusted_executor_id and trusted_executor_passed:
            status = LabGateStatus.PASS
            findings = ["TRUSTED_SANDBOX_EXECUTOR_PASSED"]
        else:
            status = LabGateStatus.BLOCKED
            findings = [
                "EXECUTION_SANDBOX_NOT_AVAILABLE",
                "UNTRUSTED_CANDIDATE_CODE_NOT_EXECUTED",
            ]
        report = SandboxReport(
            status=status,
            executor_id=trusted_executor_id,
            findings=findings,
            output_refs=list(output_refs or []),
        )
        self.store.save_model(
            case_id, candidate_id, "sandbox", report
        )
        return report

    def benchmark_block_runtime_result(
        self,
        *,
        case_id: str,
        candidate_id: str,
        method_id: str,
        runtime_result: dict[str, Any],
    ) -> BenchmarkReport:
        rendered = dict(runtime_result.get("rendered_frame_qc") or {})
        identity = dict(runtime_result.get("identity_qc") or {})
        visual = dict(runtime_result.get("visual_qc") or {})
        geometry = dict(runtime_result.get("geometry_qc") or {})
        performance = dict(runtime_result.get("performance_qc") or {})
        render_state = dict(runtime_result.get("render_state") or {})
        duration = max(
            0.0001,
            float(runtime_result.get("duration", 0.0) or 0.0),
        )

        quality_score = 1.0 if (
            bool(runtime_result.get("qc_passed"))
            and bool(rendered.get("passed"))
        ) else 0.0

        identity_score = float(identity.get("score", 0.0) or 0.0)
        if not identity.get("passed", False):
            identity_score = 0.0
        identity_score = max(0.0, min(1.0, identity_score))

        black = float(visual.get("black_seconds", 0.0) or 0.0)
        freeze = float(visual.get("freeze_seconds", 0.0) or 0.0)
        temporal_score = max(
            0.0,
            min(1.0, 1.0 - (black + freeze) / duration),
        )
        if not visual.get("passed", False):
            temporal_score = min(temporal_score, 0.49)

        camera_state = render_state.get("camera") or {}
        geometry_targets = geometry.get("targets") or []
        camera_score = 1.0 if (
            geometry.get("passed", False)
            and camera_state.get("start")
            and camera_state.get("end")
            and all(
                not (target.get("blockers") or [])
                for target in geometry_targets
            )
        ) else 0.0

        performance_score = float(
            performance.get("score", 0.0) or 0.0
        )
        if not performance.get("passed", False):
            performance_score = 0.0
        intent_score = (
            1.0
            if runtime_result.get("creative_intent_bound")
            else 0.0
        )
        control_score = max(
            0.0,
            min(
                1.0,
                0.55 * intent_score
                + 0.45 * performance_score,
            ),
        )

        dimensions = [
            BenchmarkDimension(
                name="quality",
                score=quality_score,
                evidence_refs=[
                    "runtime_result.qc_passed",
                    "runtime_result.rendered_frame_qc",
                ],
            ),
            BenchmarkDimension(
                name="identity",
                score=identity_score,
                evidence_refs=[
                    "runtime_result.identity_qc",
                ],
            ),
            BenchmarkDimension(
                name="temporal",
                score=temporal_score,
                evidence_refs=[
                    "runtime_result.visual_qc",
                    "runtime_result.duration",
                ],
            ),
            BenchmarkDimension(
                name="camera_contract",
                score=camera_score,
                evidence_refs=[
                    "runtime_result.geometry_qc",
                    "runtime_result.render_state.camera",
                ],
            ),
            BenchmarkDimension(
                name="control",
                score=control_score,
                evidence_refs=[
                    "runtime_result.creative_intent_bound",
                    "runtime_result.performance_qc",
                ],
            ),
        ]
        return self.benchmark_gate(
            case_id=case_id,
            candidate_id=candidate_id,
            method_id=method_id,
            dimensions=dimensions,
        )

    def benchmark_gate(
        self,
        *,
        case_id: str,
        candidate_id: str,
        method_id: str | None,
        dimensions: list[BenchmarkDimension] | None = None,
    ) -> BenchmarkReport:
        dims = list(dimensions or [])
        if not dims:
            status = LabGateStatus.BLOCKED
            aggregate = 0.0
            findings = ["GOLDEN_SHOT_BENCHMARK_EVIDENCE_MISSING"]
        else:
            aggregate = sum(item.score for item in dims) / len(dims)
            status = (
                LabGateStatus.PASS
                if aggregate >= self.policy.benchmark_floor
                else LabGateStatus.FAIL
            )
            findings = [] if status is LabGateStatus.PASS else [
                "BENCHMARK_SCORE_BELOW_FLOOR"
            ]
        report = BenchmarkReport(
            status=status,
            method_id=method_id,
            dimensions=dims,
            aggregate_score=aggregate,
            minimum_required=self.policy.benchmark_floor,
            findings=findings,
        )
        self.store.save_model(
            case_id, candidate_id, "benchmark", report
        )
        return report

    def conformance_gate(
        self,
        *,
        case_id: str,
        candidate_id: str,
        adapter_registered: bool,
        handler_registered: bool,
        normalization_passed: bool,
        canonical_roundtrip_passed: bool,
    ) -> ConformanceReport:
        checks = {
            "adapter_registered": adapter_registered,
            "handler_registered": handler_registered,
            "normalization_passed": normalization_passed,
            "canonical_roundtrip_passed": canonical_roundtrip_passed,
        }
        failed = [name for name, passed in checks.items() if not passed]
        report = ConformanceReport(
            status=LabGateStatus.PASS if not failed else LabGateStatus.FAIL,
            checks=checks,
            findings=[f"CONFORMANCE_FAIL:{name}" for name in failed],
        )
        self.store.save_model(
            case_id, candidate_id, "conformance", report
        )
        return report

    def package(
        self,
        *,
        case_id: str,
        candidate_id: str,
        tool_id: str | None,
        method_id: str | None,
        provenance: ProvenanceManifest,
        sbom: SBOMReport,
        security: StaticSecurityReport,
        hardware: HardwareFitReport,
        sandbox: SandboxReport,
        benchmark: BenchmarkReport,
        conformance: ConformanceReport,
    ) -> QualificationEvidencePackage:
        blockers: list[str] = []
        gate_map = {
            "PROVENANCE_HASH": (
                LabGateStatus.PASS
                if provenance.hash_verified
                else LabGateStatus.FAIL
            ),
            "SBOM": sbom.status,
            "SECURITY": security.status,
            "HARDWARE": hardware.status,
            "SANDBOX": sandbox.status,
            "BENCHMARK": benchmark.status,
            "CONFORMANCE": conformance.status,
        }
        for gate, status in gate_map.items():
            if status is not LabGateStatus.PASS:
                blockers.append(f"{gate}:{status.value}")
        package = QualificationEvidencePackage(
            package_id=(
                "LAB_"
                f"{self.store.compact_key(case_id)}_"
                f"{self.store.compact_key(candidate_id)}"
            ),
            candidate_id=candidate_id,
            tool_id=tool_id,
            method_id=method_id,
            provenance_path=str(
                self.store.report_path(case_id, candidate_id, "provenance")
            ),
            sbom_path=str(
                self.store.report_path(case_id, candidate_id, "sbom")
            ),
            security_path=str(
                self.store.report_path(case_id, candidate_id, "security")
            ),
            hardware_path=str(
                self.store.report_path(case_id, candidate_id, "hardware")
            ),
            sandbox_path=str(
                self.store.report_path(case_id, candidate_id, "sandbox")
            ),
            benchmark_path=str(
                self.store.report_path(case_id, candidate_id, "benchmark")
            ),
            conformance_path=str(
                self.store.report_path(case_id, candidate_id, "conformance")
            ),
            passed=not blockers,
            blockers=blockers,
        )
        self.store.save_model(
            case_id, candidate_id, "qualification_evidence", package
        )
        return package
