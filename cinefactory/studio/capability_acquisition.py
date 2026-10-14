from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.block_animation.contracts import CompiledShot
from cinefactory.turbo.contracts import WorkItem, WorkState
from cinefactory.turbo.metrics import gpu_snapshot
from cinefactory.workflows.registry import WorkflowManifest

from .execution_mastery import ExecutionMasteryRunner
from .capability_execution_lab import (
    CapabilityExecutionLab,
    LabGateStatus,
)
from .candidate_promotion import (
    PromotionState,
    TrustedCandidateExecution,
)
from .production_method_switch import (
    CapabilityAcquisitionRequest,
    MethodSwitchPolicy,
    MethodSwitchRequest,
)
from .production_qualification import ProductionQualificationBoard
from .rnd import ExternalToolCandidate, ExternalToolIntake, IntakeState


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResearchEvidenceTier(StrEnum):
    OFFICIAL = "OFFICIAL"
    MAINTAINER = "MAINTAINER"
    COMMUNITY = "COMMUNITY"
    UNKNOWN = "UNKNOWN"


class CapabilityAcquisitionState(StrEnum):
    RECEIVED = "RECEIVED"
    LOCAL_INVENTORY = "LOCAL_INVENTORY"
    REEVALUATING = "REEVALUATING"
    AWAITING_RESEARCH = "AWAITING_RESEARCH"
    RESEARCH_RECEIVED = "RESEARCH_RECEIVED"
    AWAITING_LAB = "AWAITING_LAB"
    LICENSE_REVIEW = "LICENSE_REVIEW"
    SECURITY_REVIEW = "SECURITY_REVIEW"
    SANDBOX = "SANDBOX"
    BENCHMARK = "BENCHMARK"
    ADAPTER = "ADAPTER"
    QUALIFICATION = "QUALIFICATION"
    APPROVED = "APPROVED"
    REQUEUED = "REQUEUED"
    BLOCKED = "BLOCKED"


class CapabilityResearchCandidate(BaseModel):
    candidate_id: str
    name: str
    tool_id: str | None = None
    method_id: str | None = None
    source_uri: str
    source_type: str
    version: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    license_name: str | None = None
    license_evidence_uri: str | None = None
    license_evidence_tier: ResearchEvidenceTier = (
        ResearchEvidenceTier.UNKNOWN
    )
    commercial_use_allowed: bool | None = None
    estimated_vram_gb: float | None = Field(
        default=None,
        ge=0.0,
    )
    local_supported: bool | None = None
    automation_interfaces: list[str] = Field(
        default_factory=list
    )
    security_notes: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    local_artifact_path: str | None = None
    local_artifact_sha256: str | None = None
    security_evidence_refs: list[str] = Field(
        default_factory=list
    )
    sandbox_report_path: str | None = None
    benchmark_report_path: str | None = None
    adapter_regression_report_path: str | None = None
    workflow_manifest: dict[str, Any] | None = None
    notes: list[str] = Field(default_factory=list)


class CapabilityResearchResponse(BaseModel):
    case_id: str
    candidates: list[CapabilityResearchCandidate] = Field(
        default_factory=list
    )
    research_notes: list[str] = Field(default_factory=list)
    searched_sources: list[str] = Field(default_factory=list)


class AcquisitionCandidateRecord(BaseModel):
    candidate: CapabilityResearchCandidate
    intake: ExternalToolCandidate
    local_artifact_verified: bool = False
    sandbox_report_passed: bool = False
    benchmark_report_passed: bool = False
    adapter_regression_passed: bool = False
    execution_lab_package_path: str | None = None
    execution_lab_passed: bool = False
    execution_lab_blockers: list[str] = Field(default_factory=list)
    promotion_attestation_id: str | None = None
    promotion_state: str | None = None
    promotion_attestation_path: str | None = None
    lab_work_id: str | None = None
    blockers: list[str] = Field(default_factory=list)


class CapabilityAcquisitionCase(BaseModel):
    case_id: str
    project_id: str
    episode_id: str
    shot_id: str
    request_path: str
    acquisition_work_id: str
    state: CapabilityAcquisitionState = (
        CapabilityAcquisitionState.RECEIVED
    )
    attempts: int = 0
    inventory: dict[str, Any] = Field(default_factory=dict)
    candidate_records: list[AcquisitionCandidateRecord] = Field(
        default_factory=list
    )
    latest_method_decision: dict[str, Any] = Field(
        default_factory=dict
    )
    blockers: list[str] = Field(default_factory=list)
    events: list[dict[str, Any]] = Field(default_factory=list)
    reasoning_request_path: str | None = None
    reasoning_response_path: str | None = None
    requeued_work_id: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class CapabilityAcquisitionOutcome(BaseModel):
    case_id: str
    state: CapabilityAcquisitionState
    completed: bool = False
    deferred: bool = False
    defer_seconds: int = Field(default=0, ge=0)
    reason: str | None = None
    requeued_work_id: str | None = None
    request_path: str | None = None
    response_path: str | None = None
    blockers: list[str] = Field(default_factory=list)


class CapabilityAcquisitionStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.cases_dir = self.root / "cases"
        self.research_requests_dir = (
            self.root / "reasoning" / "requests"
        )
        self.research_responses_dir = (
            self.root / "reasoning" / "responses"
        )
        self.candidates_dir = self.root / "candidates"
        for folder in (
            self.cases_dir,
            self.research_requests_dir,
            self.research_responses_dir,
            self.candidates_dir,
        ):
            folder.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value)

    def case_path(self, case_id: str) -> Path:
        return self.cases_dir / f"{self._safe(case_id)}.json"

    def get(self, case_id: str) -> CapabilityAcquisitionCase:
        path = self.case_path(case_id)
        if not path.exists():
            raise KeyError(case_id)
        return CapabilityAcquisitionCase.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def save(
        self,
        case: CapabilityAcquisitionCase,
    ) -> CapabilityAcquisitionCase:
        case.updated_at = utcnow()
        self.case_path(case.case_id).write_text(
            case.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return case

    def research_request_path(self, case_id: str) -> Path:
        return self.research_requests_dir / (
            f"{self._safe(case_id)}.json"
        )

    def research_response_path(self, case_id: str) -> Path:
        return self.research_responses_dir / (
            f"{self._safe(case_id)}.json"
        )

    def save_candidate(
        self,
        case_id: str,
        record: AcquisitionCandidateRecord,
    ) -> Path:
        folder = self.candidates_dir / self._safe(case_id)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / (
            f"{self._safe(record.candidate.candidate_id)}.json"
        )
        path.write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path


class CapabilityResearchBridge:
    """Non-blocking file bridge for external reasoning agents.

    The production runtime never receives web credentials. It writes a
    schema-valid research request and waits for an external OpenClaw/Codex
    style agent to place a response in the response directory.
    """

    def __init__(self, store: CapabilityAcquisitionStore) -> None:
        self.store = store

    def prepare(
        self,
        case: CapabilityAcquisitionCase,
        request: CapabilityAcquisitionRequest,
        method_request: MethodSwitchRequest,
    ) -> Path:
        path = self.store.research_request_path(case.case_id)
        payload = {
            "stage": "capability_acquisition_research",
            "case_id": case.case_id,
            "prompt": (
                "Research production-capability candidates that can solve "
                "the supplied CineFactory method gap. Prefer free/local or "
                "non-metered options, official documentation, maintainer "
                "repositories and model cards. Do not claim a candidate is "
                "production-approved. Return source-backed candidate facts "
                "only. Installation, license approval, security approval, "
                "sandboxing, benchmark and adapter qualification remain "
                "separate hard gates."
            ),
            "schema": (
                CapabilityResearchResponse.model_json_schema()
            ),
            "context": {
                "acquisition_request": request.model_dump(
                    mode="json"
                ),
                "method_switch_request": method_request.model_dump(
                    mode="json"
                ),
                "local_inventory": case.inventory,
                "current_candidate_gaps": (
                    request.candidate_gaps
                ),
                "required_next_capabilities": (
                    request.required_next_capabilities
                ),
                "research_sources": request.research_sources,
                "acceptance_gates": request.acceptance_gates,
                "constraints": {
                    "free_local_first": True,
                    "metered_generation_api": False,
                    "target_gpu": "NVIDIA RTX 3060 12GB",
                    "do_not_install": True,
                    "do_not_execute_unreviewed_code": True,
                },
            },
        }
        path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return path

    def response(
        self,
        case_id: str,
    ) -> CapabilityResearchResponse | None:
        path = self.store.research_response_path(case_id)
        if not path.exists():
            return None
        return CapabilityResearchResponse.model_validate_json(
            path.read_text(encoding="utf-8")
        )


class LocalCapabilityInventory:
    def __init__(self, ctx: Any) -> None:
        self.ctx = ctx

    def _tool_environment(self, tool_id: str) -> dict[str, Any]:
        try:
            env = self.ctx.studio.tool_doctor.inspect(tool_id)
        except Exception as exc:
            return {
                "tool_id": tool_id,
                "inspect_error": (
                    f"{type(exc).__name__}:{exc}"
                ),
            }
        return {
            "tool_id": tool_id,
            "installed": bool(env.installed),
            "version": env.version,
            "executable_path": env.executable_path,
        }

    def scan(self) -> dict[str, Any]:
        capability_rows = [
            item.model_dump(mode="json")
            for item in self.ctx.studio.capabilities.list()
        ]
        try:
            qualifications = [
                item.model_dump(mode="json")
                for item
                in self.ctx.studio.production_qualification
                .list_decisions()
            ]
        except Exception:
            qualifications = []
        try:
            mastery = [
                item.model_dump(mode="json")
                for item in self.ctx.studio.execution_mastery.list()
            ]
        except Exception:
            mastery = []
        workflows = [
            item.model_dump(mode="json")
            for item in self.ctx.workflows.list()
        ]
        models = [
            item.model_dump(mode="json")
            for item in self.ctx.models.items.values()
        ]
        tool_ids = sorted(
            {
                item.tool_id
                for item in self.ctx.method_switch.specs
            }
        )
        return {
            "captured_at": utcnow().isoformat(),
            "gpu": gpu_snapshot(),
            "capabilities": capability_rows,
            "production_qualification": qualifications,
            "execution_mastery": mastery,
            "workflows": workflows,
            "models": models,
            "tools": [
                self._tool_environment(tool_id)
                for tool_id in tool_ids
            ],
        }


class CapabilityAcquisitionWorker:
    """Durable coordinator for capability research and qualification.

    It can re-use newly available local capabilities immediately. External
    discovery is routed through a non-blocking reasoning bridge. Research
    claims alone never promote a tool into production.
    """

    KNOWN_MASTERY_TOOLS = {
        "blender",
        "ffmpeg",
        "comfyui",
        "resolve",
        "premiere",
        "photoshop",
        "aftereffects",
        "unreal",
        "canva",
    }

    def __init__(
        self,
        ctx: Any,
        *,
        store: CapabilityAcquisitionStore | None = None,
        research_defer_seconds: int = 300,
        qualification_defer_seconds: int = 300,
    ) -> None:
        self.ctx = ctx
        self.store = store or CapabilityAcquisitionStore(
            Path(ctx.root)
            / "data"
            / "studio"
            / "capability_acquisition"
        )
        self.bridge = CapabilityResearchBridge(self.store)
        self.inventory = LocalCapabilityInventory(ctx)
        self.intake = ExternalToolIntake()
        self.execution_lab = CapabilityExecutionLab(
            Path(ctx.root)
        )
        self.research_defer_seconds = max(
            5,
            int(research_defer_seconds),
        )
        self.qualification_defer_seconds = max(
            5,
            int(qualification_defer_seconds),
        )

    @staticmethod
    def _case_id(item: WorkItem) -> str:
        return (
            f"{item.project_id}__"
            f"{item.payload.get('shot_id', 'UNKNOWN_SHOT')}"
        )

    def _load_request(
        self,
        item: WorkItem,
    ) -> CapabilityAcquisitionRequest:
        raw = item.payload.get("request_path")
        if not raw:
            raise RuntimeError(
                "CAPABILITY_ACQUISITION_REQUEST_PATH_MISSING"
            )
        path = Path(str(raw))
        if not path.is_file():
            raise FileNotFoundError(path)
        return CapabilityAcquisitionRequest.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def _method_request(
        self,
        item: WorkItem,
        request: CapabilityAcquisitionRequest,
    ) -> MethodSwitchRequest:
        raw = item.payload.get("method_switch_request")
        if isinstance(raw, dict):
            return MethodSwitchRequest.model_validate(raw)
        policy_raw = str(
            item.payload.get("requested_policy")
            or request.requested_policy.value
        )
        try:
            policy = MethodSwitchPolicy(policy_raw)
        except ValueError:
            policy = MethodSwitchPolicy.QUALITY_FIRST_ALTERNATIVE
        current_method_id = str(
            item.payload.get("current_method_id")
            or request.current_method_id
        )
        current_tool_id = (
            current_method_id.split(".", 1)[0]
            if "." in current_method_id
            else "blender"
        )
        return MethodSwitchRequest(
            project_id=request.project_id,
            episode_id=request.episode_id,
            shot_id=request.shot_id,
            current_tool_id=current_tool_id,
            current_method_id=current_method_id,
            policy=policy,
            min_quality=request.required_quality,
            max_vram_gb=request.max_vram_gb,
            local_only=request.local_only,
            commercial_safe=request.commercial_safe,
            continuity_priority=True,
            backend_switch_allowed=False,
            recurring_identity_required=True,
            failure_codes=list(request.failure_codes),
        )

    def _case(
        self,
        item: WorkItem,
        request: CapabilityAcquisitionRequest,
    ) -> CapabilityAcquisitionCase:
        case_id = self._case_id(item)
        try:
            case = self.store.get(case_id)
        except KeyError:
            case = CapabilityAcquisitionCase(
                case_id=case_id,
                project_id=request.project_id,
                episode_id=request.episode_id,
                shot_id=request.shot_id,
                request_path=str(item.payload["request_path"]),
                acquisition_work_id=item.work_id,
            )
        case.attempts += 1
        case.events.append(
            {
                "at": utcnow().isoformat(),
                "event": "ACQUISITION_TICK",
                "attempt": case.attempts,
                "work_id": item.work_id,
            }
        )
        return case

    def _audit_existing_tools(
        self,
        method_decision,
        case: CapabilityAcquisitionCase,
    ) -> None:
        tool_ids = sorted(
            {
                item.tool_id
                for item in method_decision.assessments
                if item.tool_id in self.KNOWN_MASTERY_TOOLS
            }
        )
        mastery_runner = ExecutionMasteryRunner(
            self.ctx.studio
        )
        qualification = ProductionQualificationBoard(
            self.ctx.studio
        )
        audit_events: list[dict[str, Any]] = []
        for tool_id in tool_ids:
            try:
                env = self.ctx.studio.tool_doctor.inspect(
                    tool_id
                )
            except Exception:
                continue
            runtime_reachable = False
            try:
                probe = self.ctx.studio.tool_adapters.probe(
                    self.ctx.studio,
                    tool_id,
                )
                runtime_reachable = bool(
                    probe.runtime_reachable
                )
            except Exception:
                pass
            if not env.installed and not runtime_reachable:
                continue
            mastery_result = None
            try:
                existing = (
                    self.ctx.studio.execution_mastery.get(
                        tool_id
                    )
                )
            except KeyError:
                existing = None
            if existing is None or not existing.passed:
                try:
                    mastery_result = mastery_runner.evaluate(
                        tool_id
                    )
                except Exception as exc:
                    audit_events.append(
                        {
                            "tool_id": tool_id,
                            "mastery_error": (
                                f"{type(exc).__name__}:{exc}"
                            ),
                        }
                    )
            try:
                qualification_result = (
                    qualification.evaluate(tool_id)
                )
            except Exception as exc:
                qualification_result = None
                audit_events.append(
                    {
                        "tool_id": tool_id,
                        "qualification_error": (
                            f"{type(exc).__name__}:{exc}"
                        ),
                    }
                )
            audit_events.append(
                {
                    "tool_id": tool_id,
                    "mastery_passed": (
                        bool(mastery_result.passed)
                        if mastery_result is not None
                        else (
                            bool(existing.passed)
                            if existing is not None
                            else False
                        )
                    ),
                    "qualified": (
                        bool(qualification_result.qualified)
                        if qualification_result is not None
                        else False
                    ),
                }
            )
        if audit_events:
            case.events.append(
                {
                    "at": utcnow().isoformat(),
                    "event": "LOCAL_TOOL_AUDIT",
                    "tools": audit_events,
                }
            )

    def _trusted_lab_report_passed(
        self,
        path: str | None,
        *,
        case_id: str | None = None,
        candidate_id: str | None = None,
        report_name: str | None = None,
    ) -> bool:
        if not path:
            return False
        report = Path(path).resolve()
        trusted_root = (
            self.execution_lab.store.reports.resolve()
        )
        try:
            report.relative_to(trusted_root)
        except ValueError:
            return False
        if (
            case_id is not None
            and candidate_id is not None
            and report_name is not None
        ):
            expected = (
                self.execution_lab.store.report_path(
                    case_id,
                    candidate_id,
                    report_name,
                ).resolve()
            )
            if report != expected:
                return False
        if not report.is_file():
            return False
        try:
            raw = json.loads(
                report.read_text(encoding="utf-8")
            )
        except Exception:
            return False
        return (
            raw.get("status") == LabGateStatus.PASS.value
            or raw.get("passed") is True
        )

    def _run_static_execution_lab(
        self,
        *,
        case_id: str,
        candidate: CapabilityResearchCandidate,
    ) -> tuple[
        bool,
        str | None,
        bool,
        list[str],
    ]:
        if (
            not candidate.local_artifact_path
            or not candidate.local_artifact_sha256
        ):
            return (
                False,
                None,
                False,
                ["LOCAL_ARTIFACT_OR_EXPECTED_HASH_MISSING"],
            )
        try:
            provenance = (
                self.execution_lab.import_local_artifact(
                    case_id=case_id,
                    candidate_id=candidate.candidate_id,
                    source_path=candidate.local_artifact_path,
                    source_uri=candidate.source_uri,
                    source_type=candidate.source_type,
                    version=candidate.version,
                    expected_sha256=(
                        candidate.local_artifact_sha256
                    ),
                )
            )
            sbom = self.execution_lab.generate_sbom(
                case_id=case_id,
                manifest=provenance,
            )
            security = (
                self.execution_lab.static_security_scan(
                    case_id=case_id,
                    manifest=provenance,
                )
            )
            hardware = self.execution_lab.hardware_fit(
                case_id=case_id,
                candidate_id=candidate.candidate_id,
                required_vram_gb=candidate.estimated_vram_gb,
                gpu_snapshot=gpu_snapshot(),
            )

            trusted_sandbox = (
                self._trusted_lab_report_passed(
                    candidate.sandbox_report_path,
                    case_id=case_id,
                    candidate_id=candidate.candidate_id,
                    report_name="sandbox",
                )
            )
            sandbox = self.execution_lab.sandbox_gate(
                case_id=case_id,
                candidate_id=candidate.candidate_id,
                security=security,
                trusted_executor_id=(
                    "capability_execution_lab"
                    if trusted_sandbox
                    else None
                ),
                trusted_executor_passed=trusted_sandbox,
                output_refs=(
                    [candidate.sandbox_report_path]
                    if trusted_sandbox
                    and candidate.sandbox_report_path
                    else []
                ),
            )

            trusted_benchmark = (
                self._trusted_lab_report_passed(
                    candidate.benchmark_report_path,
                    case_id=case_id,
                    candidate_id=candidate.candidate_id,
                    report_name="benchmark",
                )
            )
            if trusted_benchmark:
                raw_benchmark = json.loads(
                    Path(
                        candidate.benchmark_report_path
                    ).read_text(encoding="utf-8")
                )
                from .capability_execution_lab import (
                    BenchmarkDimension,
                )
                dimensions = [
                    BenchmarkDimension.model_validate(item)
                    for item in (
                        raw_benchmark.get("dimensions") or []
                    )
                ]
            else:
                dimensions = []
            benchmark = self.execution_lab.benchmark_gate(
                case_id=case_id,
                candidate_id=candidate.candidate_id,
                method_id=candidate.method_id,
                dimensions=dimensions,
            )

            trusted_adapter = (
                self._trusted_lab_report_passed(
                    candidate.adapter_regression_report_path,
                    case_id=case_id,
                    candidate_id=candidate.candidate_id,
                    report_name="conformance",
                )
            )
            spec = next(
                (
                    item
                    for item in self.ctx.method_switch.specs
                    if item.method_id == candidate.method_id
                ),
                None,
            )
            adapter_registered = spec is not None
            handler_registered = bool(
                spec
                and spec.handler
                in self.ctx.method_switch.registered_handlers
            )
            normalization_passed = bool(
                spec
                and (
                    spec.same_scene_semantics
                    or trusted_adapter
                )
            )
            canonical_roundtrip_passed = bool(
                spec
                and (
                    spec.same_scene_semantics
                    or trusted_adapter
                )
            )
            conformance = (
                self.execution_lab.conformance_gate(
                    case_id=case_id,
                    candidate_id=candidate.candidate_id,
                    adapter_registered=adapter_registered,
                    handler_registered=handler_registered,
                    normalization_passed=normalization_passed,
                    canonical_roundtrip_passed=(
                        canonical_roundtrip_passed
                    ),
                )
            )
            package = self.execution_lab.package(
                case_id=case_id,
                candidate_id=candidate.candidate_id,
                tool_id=candidate.tool_id,
                method_id=candidate.method_id,
                provenance=provenance,
                sbom=sbom,
                security=security,
                hardware=hardware,
                sandbox=sandbox,
                benchmark=benchmark,
                conformance=conformance,
            )
            package_path = str(
                self.execution_lab.store.report_path(
                    case_id,
                    candidate.candidate_id,
                    "qualification_evidence",
                )
            )
            return (
                provenance.hash_verified,
                package_path,
                package.passed,
                list(package.blockers),
            )
        except Exception as exc:
            return (
                False,
                None,
                False,
                [
                    "EXECUTION_LAB_ERROR:"
                    f"{type(exc).__name__}:{exc}"
                ],
            )

    def _candidate_record(
        self,
        candidate: CapabilityResearchCandidate,
        *,
        case_id: str,
    ) -> AcquisitionCandidateRecord:
        blockers: list[str] = []
        commercial_known = bool(
            candidate.license_name
            and candidate.license_evidence_uri
            and candidate.license_evidence_tier
            in {
                ResearchEvidenceTier.OFFICIAL,
                ResearchEvidenceTier.MAINTAINER,
            }
        )
        commercial_allowed = (
            candidate.commercial_use_allowed
            if commercial_known
            else None
        )
        (
            artifact_verified,
            lab_package_path,
            lab_passed,
            lab_blockers,
        ) = self._run_static_execution_lab(
            case_id=case_id,
            candidate=candidate,
        )
        security_report_path = (
            self.execution_lab.store.report_path(
                case_id,
                candidate.candidate_id,
                "security",
            )
        )
        security_static_passed = (
            self._trusted_lab_report_passed(
                str(security_report_path)
            )
        )
        sandbox_passed = (
            self._trusted_lab_report_passed(
                candidate.sandbox_report_path,
                case_id=case_id,
                candidate_id=candidate.candidate_id,
                report_name="sandbox",
            )
        )
        benchmark_passed = (
            self._trusted_lab_report_passed(
                candidate.benchmark_report_path,
                case_id=case_id,
                candidate_id=candidate.candidate_id,
                report_name="benchmark",
            )
        )
        regression_passed = (
            self._trusted_lab_report_passed(
                candidate.adapter_regression_report_path,
                case_id=case_id,
                candidate_id=candidate.candidate_id,
                report_name="conformance",
            )
        )
        security_reviewed = bool(
            artifact_verified
            and security_static_passed
            and sandbox_passed
            and candidate.security_evidence_refs
        )

        if not commercial_known:
            blockers.append("LICENSE_EVIDENCE_NOT_TRUSTED")
        elif commercial_allowed is not True:
            blockers.append("COMMERCIAL_USE_NOT_APPROVED")
        if not artifact_verified:
            blockers.append("LOCAL_ARTIFACT_NOT_VERIFIED")
        if not security_reviewed:
            blockers.append("SECURITY_REVIEW_NOT_VERIFIED")
        if not sandbox_passed:
            blockers.append("SANDBOX_NOT_PASSED")
        if not benchmark_passed:
            blockers.append("BENCHMARK_NOT_PASSED")
        if not regression_passed:
            blockers.append("ADAPTER_REGRESSION_NOT_PASSED")

        intake = ExternalToolCandidate(
            candidate_id=candidate.candidate_id,
            name=candidate.name,
            source_uri=candidate.source_uri,
            source_type=candidate.source_type,
            version=candidate.version,
            license_name=candidate.license_name,
            commercial_use_known=commercial_known,
            commercial_use_allowed=commercial_allowed,
            security_reviewed=security_reviewed,
            sandbox_passed=sandbox_passed,
            benchmark_passed=benchmark_passed,
            regression_passed=regression_passed,
            capabilities=list(candidate.capabilities),
            risks=list(candidate.security_notes),
            benchmark={
                "estimated_vram_gb": (
                    candidate.estimated_vram_gb
                ),
                "local_supported": (
                    candidate.local_supported
                ),
                "evidence_refs": list(
                    candidate.evidence_refs
                ),
            },
        )
        intake = self.intake.advance(intake)
        return AcquisitionCandidateRecord(
            candidate=candidate,
            intake=intake,
            local_artifact_verified=artifact_verified,
            sandbox_report_passed=sandbox_passed,
            benchmark_report_passed=benchmark_passed,
            adapter_regression_passed=regression_passed,
            execution_lab_package_path=lab_package_path,
            execution_lab_passed=lab_passed,
            execution_lab_blockers=lab_blockers,
            blockers=sorted(
                set(blockers + lab_blockers)
            ),
        )

    def _promotion_attestation_path(
        self,
        attestation_id: str,
    ) -> str | None:
        controller = getattr(
            self.ctx,
            "candidate_promotion",
            None,
        )
        if controller is None:
            return None
        path = (
            controller.store.attestations
            / (
                controller.store._safe(
                    attestation_id
                )
                + ".json"
            )
        )
        return str(path) if path.is_file() else None

    @staticmethod
    def _rights_cleared(
        candidate: CapabilityResearchCandidate,
    ) -> bool:
        return bool(
            candidate.license_name
            and candidate.license_evidence_uri
            and candidate.license_evidence_tier
            in {
                ResearchEvidenceTier.OFFICIAL,
                ResearchEvidenceTier.MAINTAINER,
            }
            and candidate.commercial_use_allowed is True
        )

    def _process_candidate_promotions(
        self,
        *,
        item: WorkItem,
        case: CapabilityAcquisitionCase,
        records: list[AcquisitionCandidateRecord],
        method_request: MethodSwitchRequest,
    ) -> CapabilityAcquisitionOutcome | None:
        controller = getattr(
            self.ctx,
            "candidate_promotion",
            None,
        )
        if controller is None:
            return None

        waiting: list[str] = []
        for record in records:
            candidate = record.candidate
            if not candidate.workflow_manifest:
                continue
            if (
                not candidate.local_artifact_path
                or not candidate.local_artifact_sha256
            ):
                record.blockers.append(
                    "PROMOTION_LOCAL_WORKFLOW_ARTIFACT_MISSING"
                )
                continue
            try:
                manifest = WorkflowManifest.model_validate(
                    candidate.workflow_manifest
                )
            except Exception as exc:
                record.blockers.append(
                    "PROMOTION_WORKFLOW_MANIFEST_INVALID:"
                    f"{type(exc).__name__}:{exc}"
                )
                continue
            if manifest.executor_id != "local.comfyui":
                record.blockers.append(
                    "PROMOTION_EXECUTOR_NOT_SUPPORTED"
                )
                continue

            output_dir = (
                Path(self.store.root)
                / "promotion_runs"
                / self.store._safe(case.case_id)
                / self.store._safe(
                    candidate.candidate_id
                )
            )
            lab_work = (
                controller
                .build_comfyui_lab_work_item(
                    project_id=case.project_id,
                    case_id=case.case_id,
                    candidate_id=(
                        candidate.candidate_id
                    ),
                    workflow_path=(
                        candidate.local_artifact_path
                    ),
                    manifest=manifest,
                    output_dir=output_dir,
                    required_vram_gb=(
                        candidate.estimated_vram_gb
                    ),
                )
            )
            record.lab_work_id = lab_work.work_id
            try:
                existing = self.ctx.turbo_store.get_work(
                    lab_work.work_id
                )
            except KeyError:
                self.ctx.turbo_store.enqueue_work(
                    lab_work
                )
                existing = self.ctx.turbo_store.get_work(
                    lab_work.work_id
                )
                case.events.append(
                    {
                        "at": utcnow().isoformat(),
                        "event": (
                            "CANDIDATE_LAB_WORK_ENQUEUED"
                        ),
                        "candidate_id": (
                            candidate.candidate_id
                        ),
                        "work_id": lab_work.work_id,
                    }
                )

            if existing.state in {
                WorkState.QUEUED,
                WorkState.CLAIMED,
                WorkState.RUNNING,
                WorkState.RETRY,
            }:
                waiting.append(lab_work.work_id)
                continue
            if existing.state is not WorkState.SUCCESS:
                record.blockers.append(
                    "CANDIDATE_LAB_WORK_FAILED:"
                    f"{existing.state.value}"
                )
                continue

            raw_evidence = (
                existing.result.get(
                    "candidate_execution"
                )
            )
            if not isinstance(raw_evidence, dict):
                record.blockers.append(
                    "CANDIDATE_LAB_EVIDENCE_MISSING"
                )
                continue
            try:
                execution = (
                    TrustedCandidateExecution
                    .model_validate(raw_evidence)
                )
            except Exception as exc:
                record.blockers.append(
                    "CANDIDATE_LAB_EVIDENCE_INVALID:"
                    f"{type(exc).__name__}:{exc}"
                )
                continue
            if not (
                execution.state.value == "PASS"
                and execution.execution_passed
            ):
                record.blockers.append(
                    "CANDIDATE_LAB_EXECUTION_REJECTED"
                )
                continue

            attestation = (
                controller
                .qualify_and_promote_comfyui_workflow(
                    candidate_id=(
                        candidate.candidate_id
                    ),
                    workflow_path=(
                        candidate.local_artifact_path
                    ),
                    manifest=manifest,
                    source_uri=candidate.source_uri,
                    source_type=candidate.source_type,
                    expected_sha256=(
                        candidate.local_artifact_sha256
                    ),
                    output_dir=output_dir,
                    required_vram_gb=(
                        candidate.estimated_vram_gb
                    ),
                    method_request=(
                        method_request
                        if str(
                            manifest.media_type
                        ).lower()
                        == "video"
                        else None
                    ),
                    rights_cleared=(
                        self._rights_cleared(
                            candidate
                        )
                    ),
                    execution_evidence=execution,
                )
            )
            record.promotion_attestation_id = (
                attestation.attestation_id
            )
            record.promotion_state = (
                attestation.state.value
            )
            record.promotion_attestation_path = (
                self._promotion_attestation_path(
                    attestation.attestation_id
                )
            )
            if attestation.state is PromotionState.BLOCKED:
                record.blockers.extend(
                    attestation.blockers
                )
            case.events.append(
                {
                    "at": utcnow().isoformat(),
                    "event": (
                        "CANDIDATE_PROMOTION_EVALUATED"
                    ),
                    "candidate_id": (
                        candidate.candidate_id
                    ),
                    "state": (
                        attestation.state.value
                    ),
                    "attestation_id": (
                        attestation.attestation_id
                    ),
                }
            )

        for record in records:
            record.blockers = sorted(
                set(record.blockers)
            )
            self.store.save_candidate(
                case.case_id,
                record,
            )

        if waiting:
            case.state = (
                CapabilityAcquisitionState.AWAITING_LAB
            )
            case.candidate_records = records
            case.blockers = sorted(
                {
                    blocker
                    for record in records
                    for blocker in record.blockers
                }
            )
            self.store.save(case)
            return CapabilityAcquisitionOutcome(
                case_id=case.case_id,
                state=case.state,
                deferred=True,
                defer_seconds=min(
                    60,
                    self.qualification_defer_seconds,
                ),
                reason="AWAITING_CANDIDATE_LAB_EXECUTION",
                blockers=case.blockers,
            )
        return None

    def _research_state(
        self,
        records: list[AcquisitionCandidateRecord],
    ) -> CapabilityAcquisitionState:
        if not records:
            return CapabilityAcquisitionState.BLOCKED
        if any(
            row.intake.state is IntakeState.APPROVED
            for row in records
        ):
            return CapabilityAcquisitionState.APPROVED
        states = {row.intake.state for row in records}
        if IntakeState.LICENSE_REVIEW in states:
            return CapabilityAcquisitionState.LICENSE_REVIEW
        if IntakeState.SECURITY_REVIEW in states:
            return CapabilityAcquisitionState.SECURITY_REVIEW
        if IntakeState.SANDBOX in states:
            return CapabilityAcquisitionState.SANDBOX
        if IntakeState.BENCHMARK in states:
            return CapabilityAcquisitionState.BENCHMARK
        if IntakeState.ADAPTER in states:
            return CapabilityAcquisitionState.ADAPTER
        return CapabilityAcquisitionState.QUALIFICATION

    def _requeue(
        self,
        item: WorkItem,
        case: CapabilityAcquisitionCase,
        decision,
    ) -> str | None:
        if not decision.executable:
            return None
        raw = item.payload.get("resume_context")
        if not isinstance(raw, dict):
            case.blockers.append(
                "RESUME_CONTEXT_MISSING"
            )
            return None
        try:
            shot = CompiledShot.model_validate(raw["shot"])
            compiled = SimpleNamespace(
                project_id=case.project_id,
                episode_id=case.episode_id,
            )
            transformed = (
                self.ctx.method_switch.transform_block_shot(
                    shot,
                    decision,
                    repaired_base=shot,
                )
            )
            work = self.ctx.method_switch.build_work_item(
                compiled=compiled,
                shot=transformed,
                decision=decision,
                output_path=Path(raw["output_path"]),
                render_preview=bool(
                    raw.get("render_preview", False)
                ),
                switch_round=int(
                    raw.get("switch_round", 1)
                ),
                switch_of_work_id=str(
                    raw.get("switch_of_work_id")
                    or item.work_id
                ),
                blender_executable=raw.get(
                    "blender_executable"
                ),
            )
            continuation_id = raw.get(
                "continuation_id"
            )
            continuation_shot_id = raw.get(
                "continuation_shot_id"
            )
            if continuation_id and continuation_shot_id:
                payload = dict(work.payload)
                payload["continuation"] = {
                    "continuation_id": str(
                        continuation_id
                    ),
                    "shot_id": str(
                        continuation_shot_id
                    ),
                }
                work = work.model_copy(
                    update={"payload": payload}
                )
        except Exception as exc:
            case.blockers.append(
                "REQUEUE_BUILD_FAILED:"
                f"{type(exc).__name__}:{exc}"
            )
            return None
        self.ctx.turbo_store.enqueue_work(work)
        continuation = dict(
            work.payload.get("continuation") or {}
        )
        continuation_manager = getattr(
            self.ctx,
            "production_continuation",
            None,
        )
        if (
            continuation_manager is not None
            and continuation.get("continuation_id")
            and continuation.get("shot_id")
        ):
            continuation_manager.mark_requeued(
                continuation_id=str(
                    continuation["continuation_id"]
                ),
                shot_id=str(
                    continuation["shot_id"]
                ),
                render_work_id=work.work_id,
                method_id=decision.selected_method_id,
            )
        case.requeued_work_id = work.work_id
        case.state = CapabilityAcquisitionState.REQUEUED
        case.events.append(
            {
                "at": utcnow().isoformat(),
                "event": "PRODUCTION_REQUEUED",
                "work_id": work.work_id,
                "method_id": decision.selected_method_id,
            }
        )
        return work.work_id

    def process(
        self,
        item: WorkItem,
    ) -> CapabilityAcquisitionOutcome:
        request = self._load_request(item)
        method_request = self._method_request(
            item,
            request,
        )
        case = self._case(item, request)
        case.state = CapabilityAcquisitionState.LOCAL_INVENTORY
        case.inventory = self.inventory.scan()
        self.store.save(case)

        if case.requeued_work_id:
            try:
                queued = self.ctx.turbo_store.get_work(
                    case.requeued_work_id
                )
            except KeyError:
                queued = None
            if queued is not None:
                case.state = CapabilityAcquisitionState.REQUEUED
                self.store.save(case)
                return CapabilityAcquisitionOutcome(
                    case_id=case.case_id,
                    state=case.state,
                    completed=True,
                    requeued_work_id=case.requeued_work_id,
                )

        case.state = CapabilityAcquisitionState.REEVALUATING
        decision = self.ctx.method_switch.deliberate(
            method_request
        )
        case.latest_method_decision = decision.model_dump(
            mode="json"
        )
        self._audit_existing_tools(decision, case)

        # Tool mastery or qualification may have changed the decision.
        decision = self.ctx.method_switch.deliberate(
            method_request
        )
        case.latest_method_decision = decision.model_dump(
            mode="json"
        )
        if decision.executable:
            requeued = self._requeue(
                item,
                case,
                decision,
            )
            if requeued:
                self.store.save(case)
                return CapabilityAcquisitionOutcome(
                    case_id=case.case_id,
                    state=case.state,
                    completed=True,
                    requeued_work_id=requeued,
                )

        response = self.bridge.response(case.case_id)
        if response is None:
            request_path = self.bridge.prepare(
                case,
                request,
                method_request,
            )
            response_path = (
                self.store.research_response_path(
                    case.case_id
                )
            )
            case.state = (
                CapabilityAcquisitionState.AWAITING_RESEARCH
            )
            case.reasoning_request_path = str(
                request_path
            )
            case.reasoning_response_path = str(
                response_path
            )
            case.blockers = sorted(
                {
                    blocker
                    for row in decision.assessments
                    for blocker in row.blockers
                }
            )
            case.events.append(
                {
                    "at": utcnow().isoformat(),
                    "event": "AGENT_RESEARCH_REQUESTED",
                    "request_path": str(request_path),
                    "response_path": str(response_path),
                }
            )
            self.store.save(case)
            return CapabilityAcquisitionOutcome(
                case_id=case.case_id,
                state=case.state,
                deferred=True,
                defer_seconds=self.research_defer_seconds,
                reason="AWAITING_AGENT_RESEARCH_RESPONSE",
                request_path=str(request_path),
                response_path=str(response_path),
                blockers=case.blockers,
            )

        if response.case_id != case.case_id:
            case.state = CapabilityAcquisitionState.BLOCKED
            case.blockers = [
                "RESEARCH_RESPONSE_CASE_ID_MISMATCH"
            ]
            self.store.save(case)
            return CapabilityAcquisitionOutcome(
                case_id=case.case_id,
                state=case.state,
                completed=False,
                deferred=False,
                reason="INVALID_RESEARCH_RESPONSE",
                blockers=case.blockers,
            )

        case.state = CapabilityAcquisitionState.RESEARCH_RECEIVED
        records = [
            self._candidate_record(
                candidate,
                case_id=case.case_id,
            )
            for candidate in response.candidates
        ]
        case.candidate_records = records
        promotion_wait = (
            self._process_candidate_promotions(
                item=item,
                case=case,
                records=records,
                method_request=method_request,
            )
        )
        case.candidate_records = records
        if promotion_wait is not None:
            return promotion_wait
        for record in records:
            self.store.save_candidate(
                case.case_id,
                record,
            )
        case.state = self._research_state(records)
        case.blockers = sorted(
            {
                blocker
                for row in records
                for blocker in row.blockers
            }
        )
        case.events.append(
            {
                "at": utcnow().isoformat(),
                "event": "RESEARCH_RESPONSE_INGESTED",
                "candidate_count": len(records),
                "searched_sources": list(
                    response.searched_sources
                ),
            }
        )
        self.store.save(case)

        # Even a fully evidenced research candidate must be bound to a
        # registered executable method before production can resume.
        decision = self.ctx.method_switch.deliberate(
            method_request
        )
        case.latest_method_decision = decision.model_dump(
            mode="json"
        )
        if decision.executable:
            requeued = self._requeue(
                item,
                case,
                decision,
            )
            if requeued:
                self.store.save(case)
                return CapabilityAcquisitionOutcome(
                    case_id=case.case_id,
                    state=case.state,
                    completed=True,
                    requeued_work_id=requeued,
                )

        if case.state is CapabilityAcquisitionState.APPROVED:
            case.state = CapabilityAcquisitionState.ADAPTER
            case.blockers.append(
                "APPROVED_CANDIDATE_NOT_BOUND_TO_EXECUTABLE_METHOD"
            )
        self.store.save(case)
        return CapabilityAcquisitionOutcome(
            case_id=case.case_id,
            state=case.state,
            deferred=True,
            defer_seconds=self.qualification_defer_seconds,
            reason="CAPABILITY_GATES_STILL_INCOMPLETE",
            request_path=case.reasoning_request_path,
            response_path=case.reasoning_response_path,
            blockers=case.blockers,
        )
