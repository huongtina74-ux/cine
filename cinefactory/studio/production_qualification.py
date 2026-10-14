from __future__ import annotations

import ipaddress
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from .acquisition import operation_coverage
from .contracts import DepartmentId, SkillStatus
from .tool_knowledge import default_tool_knowledge_packs


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AdapterTransport(StrEnum):
    PYTHON_API = "PYTHON_API"
    COMMAND_LINE = "COMMAND_LINE"
    DESKTOP_PLUGIN = "DESKTOP_PLUGIN"
    SCRIPTING_API = "SCRIPTING_API"
    LOCAL_HTTP = "LOCAL_HTTP"
    CLOUD_API = "CLOUD_API"


class AdapterImplementationStatus(StrEnum):
    CONTRACT_ONLY = "CONTRACT_ONLY"
    EXECUTABLE = "EXECUTABLE"


class AdapterSpec(BaseModel):
    adapter_id: str
    tool_id: str
    transport: AdapterTransport
    implementation_status: AdapterImplementationStatus = (
        AdapterImplementationStatus.CONTRACT_ONLY
    )
    supported_operations: set[str] = Field(default_factory=set)
    delegated_operations: dict[str, str] = Field(default_factory=dict)
    entrypoint: str | None = None
    local: bool = True
    sandbox_required: bool = True
    deterministic: bool | None = None
    version_notes: str | None = None
    limitations: list[str] = Field(default_factory=list)
    runtime_endpoint_env: str | None = None
    default_runtime_endpoint: str | None = None
    health_path: str | None = None


class AdapterProbe(BaseModel):
    adapter_id: str
    tool_id: str
    available: bool
    installed: bool
    detected_version: str | None = None
    supported_operations: set[str] = Field(default_factory=set)
    delegated_operations: dict[str, str] = Field(default_factory=dict)
    missing_operations: set[str] = Field(default_factory=set)
    executable_path: str | None = None
    runtime_endpoint: str | None = None
    runtime_required: bool = False
    runtime_reachable: bool = False
    findings: list[str] = Field(default_factory=list)


class ToolAdapterRegistry:
    def __init__(self, specs: list[AdapterSpec] | None = None) -> None:
        self._items = {
            item.tool_id: item
            for item in (specs or default_adapter_specs())
        }

    def get(self, tool_id: str) -> AdapterSpec:
        try:
            return self._items[tool_id]
        except KeyError as exc:
            raise KeyError(f"tool adapter not registered: {tool_id}") from exc

    def list(self) -> list[AdapterSpec]:
        return sorted(self._items.values(), key=lambda item: item.tool_id)

    @staticmethod
    def _private_http_endpoint(endpoint: str) -> bool:
        parsed = urllib.parse.urlparse(endpoint)
        if parsed.scheme != "http" or not parsed.hostname:
            return False
        if parsed.hostname == "localhost":
            return True
        try:
            address = ipaddress.ip_address(parsed.hostname)
        except ValueError:
            return False
        return address.is_loopback or address.is_private

    def _probe_runtime_endpoint(
        self,
        spec: AdapterSpec,
    ) -> tuple[str | None, bool, list[str]]:
        endpoint = None
        if spec.runtime_endpoint_env:
            endpoint = os.getenv(spec.runtime_endpoint_env)
        endpoint = endpoint or spec.default_runtime_endpoint
        if not endpoint:
            return None, False, []
        endpoint = endpoint.rstrip("/")
        if spec.transport is AdapterTransport.LOCAL_HTTP:
            if not self._private_http_endpoint(endpoint):
                return endpoint, False, ["RUNTIME_ENDPOINT_NOT_PRIVATE_HTTP"]
            if not spec.health_path:
                return endpoint, False, ["RUNTIME_HEALTH_PATH_MISSING"]
            request = urllib.request.Request(
                endpoint + spec.health_path,
                method="GET",
            )
            try:
                with urllib.request.urlopen(request, timeout=2) as response:
                    reachable = 200 <= int(response.status) < 300
            except Exception as exc:
                return endpoint, False, [
                    f"RUNTIME_UNREACHABLE:{type(exc).__name__}"
                ]
            return endpoint, reachable, [] if reachable else [
                "RUNTIME_HEALTH_CHECK_FAILED"
            ]
        return endpoint, False, []

    def probe(self, kernel, tool_id: str) -> AdapterProbe:
        spec = self.get(tool_id)
        env = kernel.tool_doctor.inspect(tool_id)
        required = {
            operation
            for skill in kernel.tool_skills.list(tool_id)
            for operation in skill.operations
        }
        delegated = set(spec.delegated_operations)
        missing = required - spec.supported_operations - delegated
        endpoint, runtime_reachable, runtime_findings = (
            self._probe_runtime_endpoint(spec)
        )
        if (
            tool_id == "canva"
            and spec.transport is AdapterTransport.CLOUD_API
        ):
            try:
                from cinefactory.canva.runtime import CanvaRuntimeAdapter

                runtime = CanvaRuntimeAdapter(kernel.root).probe()
                endpoint = "https://api.canva.com/rest/v1"
                runtime_reachable = runtime.authorized
                runtime_findings = list(runtime.findings)
            except Exception as exc:
                endpoint = "https://api.canva.com/rest/v1"
                runtime_reachable = False
                runtime_findings = [
                    f"CANVA_RUNTIME_PROBE_FAILED:{type(exc).__name__}:{exc}"
                ]
        if spec.transport is AdapterTransport.DESKTOP_PLUGIN:
            bridge_url = os.getenv(
                "CINEFACTORY_ADOBE_BRIDGE",
                "http://127.0.0.1:8791",
            )
            token_path = (
                Path(kernel.root)
                / "data"
                / "studio"
                / "adobe_bridge"
                / "token.txt"
            )
            endpoint = bridge_url
            if not token_path.is_file():
                runtime_reachable = False
                runtime_findings = ["ADOBE_BRIDGE_TOKEN_MISSING"]
            else:
                try:
                    from cinefactory.adobe.bridge import AdobeBridgeHTTPClient

                    client = AdobeBridgeHTTPClient(
                        base_url=bridge_url,
                        token=token_path.read_text(
                            encoding="utf-8"
                        ).strip(),
                        timeout_seconds=2,
                    )
                    registered = client.client(tool_id)
                    if registered is None:
                        runtime_reachable = False
                        runtime_findings = [
                            "ADOBE_PLUGIN_CLIENT_NOT_REGISTERED"
                        ]
                    else:
                        age = (
                            utcnow() - registered.last_seen
                        ).total_seconds()
                        runtime_reachable = age <= 5.0
                        runtime_findings = (
                            []
                            if runtime_reachable
                            else ["ADOBE_PLUGIN_HEARTBEAT_STALE"]
                        )
                except Exception as exc:
                    runtime_reachable = False
                    runtime_findings = [
                        f"ADOBE_BRIDGE_UNREACHABLE:{type(exc).__name__}"
                    ]
        if (
            tool_id == "aftereffects"
            and spec.transport is AdapterTransport.SCRIPTING_API
        ):
            try:
                from cinefactory.adobe.aftereffects import (
                    AfterEffectsRuntimeAdapter,
                )

                runtime = AfterEffectsRuntimeAdapter(kernel.root).probe()
                endpoint = "afterfx.exe+aerender.exe"
                runtime_reachable = runtime.scripting_ready
                runtime_findings = list(runtime.findings)
            except Exception as exc:
                endpoint = "afterfx.exe+aerender.exe"
                runtime_reachable = False
                runtime_findings = [
                    f"AFTER_EFFECTS_RUNTIME_PROBE_FAILED:"
                    f"{type(exc).__name__}:{exc}"
                ]
        if (
            tool_id == "unreal"
            and spec.transport is AdapterTransport.PYTHON_API
        ):
            try:
                from cinefactory.executors.unreal import UnrealRuntimeAdapter

                runtime = UnrealRuntimeAdapter(kernel.root).probe()
                endpoint = "UnrealEditor-Cmd.exe"
                runtime_reachable = runtime.scripting_ready
                runtime_findings = list(runtime.findings)
            except Exception as exc:
                endpoint = "UnrealEditor-Cmd.exe"
                runtime_reachable = False
                runtime_findings = [
                    f"UNREAL_RUNTIME_PROBE_FAILED:{type(exc).__name__}:{exc}"
                ]
        if (
            tool_id == "resolve"
            and spec.transport is AdapterTransport.SCRIPTING_API
        ):
            try:
                from cinefactory.executors.resolve import ResolveRuntimeAdapter

                runtime = ResolveRuntimeAdapter(kernel.root).probe()
                endpoint = "DaVinciResolveScript"
                runtime_reachable = runtime.connected
                runtime_findings = list(runtime.findings)
                if not runtime.module_path:
                    runtime_findings.append(
                        "RESOLVE_SCRIPT_MODULE_NOT_FOUND"
                    )
            except Exception as exc:
                endpoint = "DaVinciResolveScript"
                runtime_reachable = False
                runtime_findings = [
                    f"RESOLVE_RUNTIME_PROBE_FAILED:{type(exc).__name__}:{exc}"
                ]
        findings: list[str] = [*runtime_findings]
        delegation_ready = True
        for operation, backend_tool in spec.delegated_operations.items():
            try:
                delegated_mastery = kernel.execution_mastery.get(
                    backend_tool
                )
            except KeyError:
                delegated_mastery = None
            if (
                delegated_mastery is None
                or not delegated_mastery.passed
                or not delegated_mastery.regression_passed
            ):
                delegation_ready = False
                findings.append(
                    f"DELEGATED_OPERATION_NOT_VALIDATED:"
                    f"{operation}->{backend_tool}"
                )
        runtime_satisfies_local = (
            spec.transport
            in {
                AdapterTransport.LOCAL_HTTP,
                AdapterTransport.SCRIPTING_API,
                AdapterTransport.DESKTOP_PLUGIN,
            }
            and runtime_reachable
        )
        if not env.installed and spec.local and not runtime_satisfies_local:
            findings.append("TOOL_NOT_INSTALLED")
        if spec.implementation_status is not AdapterImplementationStatus.EXECUTABLE:
            findings.append("ADAPTER_IMPLEMENTATION_INCOMPLETE")
        if (
            spec.transport is AdapterTransport.CLOUD_API
            and not runtime_reachable
        ):
            findings.append("ADAPTER_EXTERNAL_CONFIGURATION_REQUIRED")
        if missing:
            findings.append(
                "ADAPTER_OPERATION_GAPS:" + ",".join(sorted(missing))
            )
        runtime_bound = (
            spec.transport
            in {
                AdapterTransport.LOCAL_HTTP,
                AdapterTransport.SCRIPTING_API,
                AdapterTransport.DESKTOP_PLUGIN,
                AdapterTransport.CLOUD_API,
            }
            or tool_id == "unreal"
        )
        availability_base = (
            runtime_reachable
            if runtime_bound
            else (env.installed or not spec.local)
        )
        available = (
            availability_base
            and not missing
            and spec.implementation_status is AdapterImplementationStatus.EXECUTABLE
            and delegation_ready
        )
        return AdapterProbe(
            adapter_id=spec.adapter_id,
            tool_id=tool_id,
            available=available,
            installed=env.installed,
            detected_version=env.version,
            supported_operations=set(spec.supported_operations),
            delegated_operations=dict(spec.delegated_operations),
            missing_operations=missing,
            executable_path=env.executable_path,
            runtime_endpoint=endpoint,
            runtime_required=runtime_bound,
            runtime_reachable=runtime_reachable,
            findings=findings,
        )


class AttestationKind(StrEnum):
    SECURITY = "SECURITY"
    COMMERCIAL_SAFETY = "COMMERCIAL_SAFETY"
    LICENSE = "LICENSE"
    VERSION_COMPATIBILITY = "VERSION_COMPATIBILITY"
    PRODUCTION_OWNER = "PRODUCTION_OWNER"


class QualificationAttestation(BaseModel):
    attestation_id: str
    tool_id: str
    kind: AttestationKind
    approved: bool
    reviewer: str
    rationale: str
    evidence_refs: list[str] = Field(default_factory=list)
    tool_version: str | None = None
    created_at: datetime = Field(default_factory=utcnow)


class QualificationDecision(BaseModel):
    tool_id: str
    skill_id: str
    skill_version: str
    qualified: bool
    knowledge_coverage: float
    execution_coverage: float
    adapter_available: bool
    installed: bool
    skill_status: SkillStatus
    passed_checks: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    attestation_ids: list[str] = Field(default_factory=list)
    decided_at: datetime = Field(default_factory=utcnow)


class ProductionQualificationStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.attestations_dir = self.root / "attestations"
        self.decisions_dir = self.root / "decisions"
        self.attestations_dir.mkdir(parents=True, exist_ok=True)
        self.decisions_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value)

    def add_attestation(
        self,
        attestation: QualificationAttestation,
    ) -> Path:
        path = (
            self.attestations_dir
            / f"{self._safe(attestation.attestation_id)}.json"
        )
        if path.exists():
            existing = QualificationAttestation.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            if existing != attestation:
                raise FileExistsError(attestation.attestation_id)
            return path
        path.write_text(
            attestation.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path

    def attestations(
        self,
        tool_id: str | None = None,
    ) -> list[QualificationAttestation]:
        out: list[QualificationAttestation] = []
        for path in sorted(self.attestations_dir.glob("*.json")):
            item = QualificationAttestation.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            if tool_id is None or item.tool_id == tool_id:
                out.append(item)
        return out

    def save_decision(self, decision: QualificationDecision) -> Path:
        path = self.decisions_dir / f"{self._safe(decision.tool_id)}.json"
        path.write_text(
            decision.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path

    def decision(self, tool_id: str) -> QualificationDecision:
        path = self.decisions_dir / f"{self._safe(tool_id)}.json"
        if not path.exists():
            raise KeyError(tool_id)
        return QualificationDecision.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def list_decisions(self) -> list[QualificationDecision]:
        return [
            QualificationDecision.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            for path in sorted(self.decisions_dir.glob("*.json"))
        ]


class ProductionQualificationBoard:
    REQUIRED_ATTESTATIONS = {
        AttestationKind.SECURITY,
        AttestationKind.COMMERCIAL_SAFETY,
        AttestationKind.LICENSE,
        AttestationKind.VERSION_COMPATIBILITY,
        AttestationKind.PRODUCTION_OWNER,
    }

    def __init__(
        self,
        kernel,
        *,
        adapters: ToolAdapterRegistry | None = None,
        store: ProductionQualificationStore | None = None,
    ) -> None:
        self.kernel = kernel
        self.adapters = adapters or getattr(
            kernel,
            "tool_adapters",
            ToolAdapterRegistry(),
        )
        self.store = store or getattr(
            kernel,
            "production_qualification",
            ProductionQualificationStore(
                Path(kernel.root)
                / "data"
                / "studio"
                / "production_qualification"
            ),
        )

    @staticmethod
    def _pack(tool_id: str):
        return next(
            item
            for item in default_tool_knowledge_packs()
            if item.tool_id == tool_id
        )

    def evaluate(
        self,
        tool_id: str,
        *,
        persist: bool = True,
    ) -> QualificationDecision:
        pack = self._pack(tool_id)
        env = self.kernel.tool_doctor.inspect(tool_id)
        manifest = self.kernel.skills.get(pack.skill_id, pack.version)
        knowledge = operation_coverage(self.kernel, tool_id)
        adapter = self.adapters.probe(self.kernel, tool_id)

        execution_coverage = 0.0
        execution_passed = False
        execution_regression = False
        try:
            mastery = self.kernel.execution_mastery.get(tool_id)
        except KeyError:
            mastery = None
        if mastery is not None:
            execution_coverage = mastery.execution_coverage
            execution_passed = mastery.passed
            execution_regression = mastery.regression_passed

        current_attestations = self.store.attestations(tool_id)
        latest_by_kind: dict[AttestationKind, QualificationAttestation] = {}
        for attestation in sorted(
            current_attestations,
            key=lambda item: item.created_at,
        ):
            latest_by_kind[attestation.kind] = attestation

        blockers: list[str] = []
        passed_checks: list[str] = []

        def check(condition: bool, passed_label: str, blocker: str) -> None:
            if condition:
                passed_checks.append(passed_label)
            else:
                blockers.append(blocker)

        check(
            env.installed
            or adapter.runtime_reachable
            or not self.adapters.get(tool_id).local,
            "TOOL_AVAILABLE",
            "TOOL_NOT_AVAILABLE",
        )
        check(knowledge.coverage == 1.0,
              "KNOWLEDGE_COMPLETE", "KNOWLEDGE_INCOMPLETE")
        check(execution_passed and execution_coverage == 1.0,
              "EXECUTION_MASTERY_COMPLETE", "EXECUTION_MASTERY_INCOMPLETE")
        check(execution_regression,
              "EXECUTION_REGRESSION_PASS", "EXECUTION_REGRESSION_MISSING")
        check(adapter.available,
              "ADAPTER_READY", "ADAPTER_NOT_READY")
        check(manifest.status in {SkillStatus.VALIDATED, SkillStatus.PRODUCTION},
              "SKILL_VALIDATED", "SKILL_NOT_VALIDATED")

        for kind in sorted(self.REQUIRED_ATTESTATIONS, key=lambda item: item.value):
            item = latest_by_kind.get(kind)
            if item is None:
                blockers.append(f"ATTESTATION_MISSING:{kind.value}")
                continue
            if not item.approved:
                blockers.append(f"ATTESTATION_REJECTED:{kind.value}")
                continue
            if (
                kind is AttestationKind.VERSION_COMPATIBILITY
                and item.tool_version
                and env.version
                and item.tool_version not in env.version
            ):
                blockers.append("VERSION_ATTESTATION_STALE")
                continue
            passed_checks.append(f"ATTESTATION_APPROVED:{kind.value}")

        qualified = not blockers
        decision = QualificationDecision(
            tool_id=tool_id,
            skill_id=pack.skill_id,
            skill_version=pack.version,
            qualified=qualified,
            knowledge_coverage=knowledge.coverage,
            execution_coverage=execution_coverage,
            adapter_available=adapter.available,
            installed=env.installed,
            skill_status=manifest.status,
            passed_checks=passed_checks,
            blockers=blockers,
            attestation_ids=[
                item.attestation_id for item in current_attestations
            ],
        )
        if persist:
            self.store.save_decision(decision)
        return decision

    def promote_if_qualified(
        self,
        tool_id: str,
    ) -> QualificationDecision:
        decision = self.evaluate(tool_id)
        if not decision.qualified:
            return decision
        pack = self._pack(tool_id)
        attestations = self.store.attestations(tool_id)
        approved_ids = [
            item.attestation_id
            for item in attestations
            if item.approved
        ]
        self.kernel.skills.authorize_production(
            pack.skill_id,
            pack.version,
            commercial_safe=True,
            security_reviewed=True,
            code_execution_allowed=True,
            evidence_notes=[
                f"production_qualification_attestation:{item}"
                for item in approved_ids
            ],
        )
        manifest = self.kernel.skills.get(pack.skill_id, pack.version)
        if manifest.status is not SkillStatus.PRODUCTION:
            self.kernel.skills.promote_production(
                pack.skill_id,
                pack.version,
                commercial_project=True,
            )
        return self.evaluate(tool_id)


def default_adapter_specs() -> list[AdapterSpec]:
    from .tooling import DEFAULT_TOOL_SKILLS

    operations = {
        item.tool_id: set(item.operations)
        for item in DEFAULT_TOOL_SKILLS
    }
    return [
        AdapterSpec(
            adapter_id="adapter.blender.bpy",
            tool_id="blender",
            transport=AdapterTransport.PYTHON_API,
            implementation_status=AdapterImplementationStatus.EXECUTABLE,
            supported_operations=operations["blender"],
            entrypoint="bpy + Blender background mode",
            deterministic=True,
        ),
        AdapterSpec(
            adapter_id="adapter.ffmpeg.cli",
            tool_id="ffmpeg",
            transport=AdapterTransport.COMMAND_LINE,
            implementation_status=AdapterImplementationStatus.EXECUTABLE,
            supported_operations=operations["ffmpeg"],
            entrypoint="ffmpeg/ffprobe",
            deterministic=True,
        ),
        AdapterSpec(
            adapter_id="adapter.premiere.uxp",
            tool_id="premiere",
            transport=AdapterTransport.DESKTOP_PLUGIN,
            implementation_status=AdapterImplementationStatus.EXECUTABLE,
            supported_operations={
                operation
                for operation in operations["premiere"]
                if operation != "captions"
            },
            delegated_operations={"captions": "ffmpeg"},
            entrypoint=(
                "Premiere UXP plugin + authenticated CineFactory "
                "loopback bridge"
            ),
            deterministic=True,
            limitations=[
                "Requires Premiere 25.6+ with the CineFactory UXP plugin loaded and heartbeating.",
                "Caption authoring is delegated to the validated FFmpeg/SRT pipeline because current Premiere UXP exposes caption-track access but no equivalent native caption-item creation surface.",
            ],
        ),
        AdapterSpec(
            adapter_id="adapter.resolve.scripting",
            tool_id="resolve",
            transport=AdapterTransport.SCRIPTING_API,
            implementation_status=AdapterImplementationStatus.EXECUTABLE,
            supported_operations=operations["resolve"],
            entrypoint="DaVinciResolveScript + Resolve/Fusion scripting API",
            deterministic=True,
            limitations=[
                "Resolve must be installed, running, and permit local scripting access.",
                "Execution mastery uses a disposable sandbox project and deletes it after validation.",
                "No UI automation fallback is used if the scripting surface is unavailable.",
            ],
        ),
        AdapterSpec(
            adapter_id="adapter.aftereffects.script",
            tool_id="aftereffects",
            transport=AdapterTransport.SCRIPTING_API,
            implementation_status=AdapterImplementationStatus.EXECUTABLE,
            supported_operations=operations["aftereffects"],
            entrypoint="AfterFX ExtendScript + aerender command line",
            deterministic=True,
            limitations=[
                "Requires After Effects with aerender.exe in Support Files.",
                "Scripting file/network access must be enabled so the sandbox script can write evidence.",
                "The mastery project is disposable and render output is independently checked.",
            ],
        ),
        AdapterSpec(
            adapter_id="adapter.photoshop.uxp",
            tool_id="photoshop",
            transport=AdapterTransport.DESKTOP_PLUGIN,
            implementation_status=AdapterImplementationStatus.EXECUTABLE,
            supported_operations=operations["photoshop"],
            entrypoint=(
                "Photoshop UXP plugin + authenticated CineFactory "
                "loopback bridge"
            ),
            deterministic=True,
            limitations=[
                "Requires Photoshop with the CineFactory UXP plugin loaded and heartbeating.",
                "The plugin requests full local filesystem access only for deterministic sandbox export paths.",
                "State-changing operations run inside Photoshop executeAsModal.",
            ],
        ),
        AdapterSpec(
            adapter_id="adapter.unreal.editor",
            tool_id="unreal",
            transport=AdapterTransport.PYTHON_API,
            implementation_status=AdapterImplementationStatus.EXECUTABLE,
            supported_operations=operations["unreal"],
            entrypoint="UnrealEditor-Cmd + Python + Movie Render Pipeline",
            deterministic=True,
            limitations=[
                "Requires UnrealEditor-Cmd.exe and a mastery project with Python Scripting and Movie Render Pipeline enabled.",
                "MRQ mastery requires an explicit map, Level Sequence and MoviePipelineConfig fixture.",
            ],
        ),
        AdapterSpec(
            adapter_id="adapter.canva.api",
            tool_id="canva",
            transport=AdapterTransport.CLOUD_API,
            implementation_status=AdapterImplementationStatus.EXECUTABLE,
            supported_operations=operations["canva"],
            entrypoint="Canva Connect REST API v1",
            local=False,
            deterministic=None,
            limitations=[
                "Requires explicit user OAuth authorization and CANVA_ACCESS_TOKEN.",
                "Autofill and resize capabilities can depend on account/plan/template capabilities.",
                "Execution mastery requires a user-provided mastery fixture and creates temporary Canva designs.",
            ],
        ),
        AdapterSpec(
            adapter_id="adapter.comfyui.local",
            tool_id="comfyui",
            transport=AdapterTransport.LOCAL_HTTP,
            implementation_status=AdapterImplementationStatus.EXECUTABLE,
            supported_operations=operations["comfyui"],
            entrypoint="ComfyUIExecutor local API/workflow JSON",
            deterministic=None,
            runtime_endpoint_env="CINEFACTORY_COMFYUI",
            default_runtime_endpoint="http://127.0.0.1:8188",
            health_path="/object_info",
            limitations=[
                "Runtime qualification requires a reachable loopback/private-LAN ComfyUI service.",
                "Workflow/model commercial safety is evaluated separately from adapter execution.",
            ],
        ),
    ]
