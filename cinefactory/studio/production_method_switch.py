from __future__ import annotations

import re
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.block_animation.contracts import (
    BlenderAnimationJob,
    CompiledShot,
)
from cinefactory.studio.contracts import CapabilityKind
from cinefactory.turbo.contracts import (
    ResourceClass,
    WorkItem,
)


class MethodSwitchStatus(StrEnum):
    SELECTED = "SELECTED"
    BLOCKED_ACQUISITION = "BLOCKED_ACQUISITION"
    BLOCKED_CONTINUITY = "BLOCKED_CONTINUITY"
    BLOCKED_POLICY = "BLOCKED_POLICY"


class MethodSwitchPolicy(StrEnum):
    QUALITY_FIRST_ALTERNATIVE = "QUALITY_FIRST_ALTERNATIVE"
    BALANCED_ALTERNATIVE = "BALANCED_ALTERNATIVE"
    FAST_LEAN_ALTERNATIVE = "FAST_LEAN_ALTERNATIVE"


class MethodExecutionMode(StrEnum):
    BLENDER_CYCLES = "BLENDER_CYCLES"
    COMFY_VIDEO = "COMFY_VIDEO"
    UNREAL_SEQUENCE = "UNREAL_SEQUENCE"
    GAME_RUNTIME = "GAME_RUNTIME"


class ProductionMethodSpec(BaseModel):
    method_id: str
    tool_id: str
    capability_id: str
    capability_kind: CapabilityKind
    handler: str
    resource: ResourceClass
    execution_mode: MethodExecutionMode
    quality: float = Field(ge=0.0, le=1.0)
    speed: float = Field(ge=0.0, le=1.0)
    control: float = Field(ge=0.0, le=1.0)
    deterministic: float = Field(ge=0.0, le=1.0)
    vram_gb: float | None = Field(default=None, ge=0.0)
    local: bool = True
    commercial_safe: bool | None = None
    same_scene_semantics: bool = False
    requires_video_workflow: bool = False
    requires_block_normalizer: bool = False
    workflow_id: str | None = None
    workflow_version: str | None = None
    normalizer_id: str | None = None
    identity_conditioning_supported: bool = False
    exact_camera_geometry_supported: bool = False
    estimated_time_multiplier: float = Field(default=1.0, gt=0.0)
    tags: set[str] = Field(default_factory=set)


class MethodSwitchRequest(BaseModel):
    project_id: str
    episode_id: str
    shot_id: str
    current_tool_id: str
    current_method_id: str
    policy: MethodSwitchPolicy
    min_quality: float = Field(ge=0.0, le=1.0)
    max_vram_gb: float | None = Field(default=12.0, gt=0.0)
    local_only: bool = True
    commercial_safe: bool = True
    max_additional_gpu_seconds: float | None = Field(
        default=None,
        gt=0.0,
    )
    mean_current_attempt_seconds: float = Field(
        default=0.0,
        ge=0.0,
    )
    continuity_priority: bool = True
    backend_switch_allowed: bool = False
    recurring_identity_required: bool = False
    reference_frame_path: str | None = None
    precise_camera_required: bool = False
    semantic_performance_required: bool = False
    visual_style: str | None = None
    failure_codes: list[str] = Field(default_factory=list)
    required_tags: set[str] = Field(default_factory=set)


class MethodCandidateAssessment(BaseModel):
    method_id: str
    tool_id: str
    capability_id: str
    capability_kind: CapabilityKind
    eligible: bool
    execution_ready: bool
    score: float = Field(default=0.0, ge=0.0)
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    workflow_id: str | None = None
    workflow_version: str | None = None
    projected_gpu_seconds: float | None = Field(
        default=None,
        ge=0.0,
    )


class MethodSwitchDecision(BaseModel):
    request: MethodSwitchRequest
    status: MethodSwitchStatus
    selected_method_id: str | None = None
    selected_tool_id: str | None = None
    selected_capability_id: str | None = None
    selected_handler: str | None = None
    assessments: list[MethodCandidateAssessment] = Field(
        default_factory=list
    )
    reasons: list[str] = Field(default_factory=list)
    acquisition_request_path: str | None = None

    @property
    def executable(self) -> bool:
        return (
            self.status is MethodSwitchStatus.SELECTED
            and self.selected_method_id is not None
            and self.selected_handler is not None
        )


class CapabilityAcquisitionRequest(BaseModel):
    project_id: str
    episode_id: str
    shot_id: str
    current_method_id: str
    requested_policy: MethodSwitchPolicy
    required_quality: float = Field(ge=0.0, le=1.0)
    max_vram_gb: float | None = None
    local_only: bool = True
    commercial_safe: bool = True
    failure_codes: list[str] = Field(default_factory=list)
    candidate_gaps: dict[str, list[str]] = Field(
        default_factory=dict
    )
    required_next_capabilities: list[str] = Field(
        default_factory=list
    )
    research_sources: list[str] = Field(
        default_factory=lambda: [
            "OFFICIAL_DOCS",
            "MODEL_CARDS",
            "GITHUB",
            "COMFYUI_WORKFLOW_REGISTRY",
            "TOOL_ADAPTER_REGISTRY",
        ]
    )
    acceptance_gates: list[str] = Field(
        default_factory=lambda: [
            "LICENSE_REVIEW",
            "SECURITY_REVIEW",
            "HARDWARE_COMPATIBILITY",
            "SANDBOX_BENCHMARK",
            "QUALITY_BENCHMARK",
            "AUTOMATION_READINESS",
            "BLOCK_SHOT_NORMALIZATION",
            "PRODUCTION_QUALIFICATION",
        ]
    )


class ProductionMethodSwitchStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value)

    def save_acquisition(
        self,
        request: CapabilityAcquisitionRequest,
    ) -> Path:
        path = self.root / (
            f"{self._safe(request.project_id)}__"
            f"{self._safe(request.shot_id)}.json"
        )
        path.write_text(
            request.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path


DEFAULT_METHOD_SPECS = [
    ProductionMethodSpec(
        method_id="blender.cycles.quality",
        tool_id="blender",
        capability_id="blender.local",
        capability_kind=CapabilityKind.OFFLINE_3D,
        handler="blender.animation.render",
        resource=ResourceClass.GPU,
        execution_mode=MethodExecutionMode.BLENDER_CYCLES,
        quality=0.95,
        speed=0.32,
        control=0.98,
        deterministic=0.96,
        vram_gb=8.0,
        local=True,
        commercial_safe=True,
        same_scene_semantics=True,
        estimated_time_multiplier=2.5,
        tags={
            "camera_precision",
            "character_animation",
            "canonical_scene",
            "quality_recovery",
        },
    ),
    ProductionMethodSpec(
        method_id="comfyui.video.production",
        tool_id="comfyui",
        capability_id="comfyui.local.video",
        capability_kind=CapabilityKind.AI_VIDEO,
        handler="comfy.execute",
        resource=ResourceClass.GPU,
        execution_mode=MethodExecutionMode.COMFY_VIDEO,
        quality=0.72,
        speed=0.38,
        control=0.58,
        deterministic=0.30,
        vram_gb=12.0,
        local=True,
        commercial_safe=None,
        same_scene_semantics=False,
        requires_video_workflow=True,
        requires_block_normalizer=True,
        estimated_time_multiplier=2.0,
        tags={
            "reference_conditioning",
            "generative_video",
            "generic_unresolved_video_backend",
        },
    ),
    ProductionMethodSpec(
        method_id="comfyui.wan21.fun.inpaint.1.3b",
        tool_id="comfyui",
        capability_id="comfyui.local.video",
        capability_kind=CapabilityKind.AI_VIDEO,
        handler="block.video.comfy",
        resource=ResourceClass.GPU,
        execution_mode=MethodExecutionMode.COMFY_VIDEO,
        quality=0.74,
        speed=0.38,
        control=0.66,
        deterministic=0.55,
        vram_gb=12.0,
        local=True,
        commercial_safe=True,
        same_scene_semantics=False,
        requires_video_workflow=True,
        requires_block_normalizer=True,
        workflow_id="comfy.wan21.fun.inpaint.1.3b",
        workflow_version="1",
        normalizer_id="blockvideo.wan21.fun.inpaint.v1",
        identity_conditioning_supported=True,
        exact_camera_geometry_supported=False,
        estimated_time_multiplier=2.4,
        tags={
            "reference_conditioning",
            "generative_video",
        },
    ),
    ProductionMethodSpec(
        method_id="unreal.sequence.quality",
        tool_id="unreal",
        capability_id="unreal.local",
        capability_kind=CapabilityKind.REALTIME_3D,
        handler="unreal.sequence.render",
        resource=ResourceClass.GPU,
        execution_mode=MethodExecutionMode.UNREAL_SEQUENCE,
        quality=0.94,
        speed=0.72,
        control=0.94,
        deterministic=0.90,
        vram_gb=8.0,
        local=True,
        commercial_safe=None,
        same_scene_semantics=False,
        requires_block_normalizer=True,
        estimated_time_multiplier=1.4,
        tags={"sequencer", "realtime_3d"},
    ),
    ProductionMethodSpec(
        method_id="minecraft.runtime.capture",
        tool_id="minecraft",
        capability_id="minecraft.runtime",
        capability_kind=CapabilityKind.GAME_RUNTIME,
        handler="minecraft.runtime.render",
        resource=ResourceClass.GPU,
        execution_mode=MethodExecutionMode.GAME_RUNTIME,
        quality=0.92,
        speed=0.82,
        control=0.92,
        deterministic=0.72,
        vram_gb=4.0,
        local=True,
        commercial_safe=None,
        same_scene_semantics=False,
        requires_block_normalizer=True,
        estimated_time_multiplier=0.8,
        tags={"minecraft", "actual_gameplay"},
    ),
    ProductionMethodSpec(
        method_id="roblox.studio.capture",
        tool_id="roblox",
        capability_id="roblox.studio",
        capability_kind=CapabilityKind.GAME_RUNTIME,
        handler="roblox.studio.render",
        resource=ResourceClass.GPU,
        execution_mode=MethodExecutionMode.GAME_RUNTIME,
        quality=0.91,
        speed=0.84,
        control=0.91,
        deterministic=0.75,
        vram_gb=4.0,
        local=True,
        commercial_safe=None,
        same_scene_semantics=False,
        requires_block_normalizer=True,
        estimated_time_multiplier=0.8,
        tags={"roblox", "studio"},
    ),
]


class ProductionMethodSwitchController:
    """Fail-closed production-method router.

    It may automatically execute only a method whose capability, runtime,
    qualification, rights/model state, workflow and normalization path are all
    proven. Missing proof becomes an R&D acquisition request, never an assumed
    capability.
    """

    def __init__(
        self,
        ctx: Any,
        *,
        specs: list[ProductionMethodSpec] | None = None,
        store: ProductionMethodSwitchStore | None = None,
        registered_handlers: set[str] | None = None,
    ) -> None:
        self.ctx = ctx
        self.specs = list(specs or DEFAULT_METHOD_SPECS)
        self.store = store or ProductionMethodSwitchStore(
            Path(ctx.root)
            / "data"
            / "studio"
            / "method_switch_requests"
        )
        self.registered_handlers = set(
            registered_handlers
            or {
                "blender.animation.render",
                "comfy.execute",
                "block.video.comfy",
            }
        )

    def _capability_offer(self, capability_id: str):
        for offer in self.ctx.studio.capabilities.list():
            if offer.capability_id == capability_id:
                return offer
        return None

    def _qualification(self, tool_id: str):
        try:
            return self.ctx.studio.production_qualification.decision(
                tool_id
            )
        except KeyError:
            return None

    def _video_workflow(self, spec: ProductionMethodSpec):
        if spec.tool_id != "comfyui":
            return None
        rows = [
            item
            for item in self.ctx.workflows.list()
            if item.executor_id == "local.comfyui"
            and str(item.media_type).lower() == "video"
        ]
        if spec.workflow_id:
            rows = [
                item for item in rows
                if item.workflow_id == spec.workflow_id
                and (
                    spec.workflow_version is None
                    or item.version == spec.workflow_version
                )
            ]
        if not rows:
            return None
        return sorted(
            rows,
            key=lambda item: (
                item.workflow_id,
                item.version,
            ),
        )[0]

    def _workflow_model_approved(self, workflow) -> bool:
        if workflow is None:
            return False
        if not workflow.model_revision:
            return False
        try:
            self.ctx.models.require_approved(
                workflow.model_id,
                workflow.model_revision,
            )
        except (KeyError, RuntimeError):
            return False
        return True

    @staticmethod
    def _score(
        request: MethodSwitchRequest,
        spec: ProductionMethodSpec,
    ) -> float:
        if (
            request.policy
            is MethodSwitchPolicy.QUALITY_FIRST_ALTERNATIVE
        ):
            value = (
                0.48 * spec.quality
                + 0.24 * spec.control
                + 0.20 * spec.deterministic
                + 0.08 * spec.speed
            )
        elif (
            request.policy
            is MethodSwitchPolicy.FAST_LEAN_ALTERNATIVE
        ):
            value = (
                0.24 * spec.quality
                + 0.18 * spec.control
                + 0.13 * spec.deterministic
                + 0.45 * spec.speed
            )
        else:
            value = (
                0.36 * spec.quality
                + 0.23 * spec.control
                + 0.19 * spec.deterministic
                + 0.22 * spec.speed
            )
        if spec.same_scene_semantics:
            value += 0.08
        return round(value, 4)

    def assess(
        self,
        request: MethodSwitchRequest,
        spec: ProductionMethodSpec,
    ) -> MethodCandidateAssessment:
        blockers: list[str] = []
        warnings: list[str] = []
        reasons: list[str] = []

        if spec.method_id == request.current_method_id:
            blockers.append("SAME_METHOD")
        if (
            request.visual_style
            and request.visual_style.upper() == "MINECRAFT"
            and spec.method_id == "roblox.studio.capture"
        ):
            blockers.append("NICHE_STYLE_MISMATCH")
        if (
            request.visual_style
            and request.visual_style.upper().startswith("ROBLOX")
            and spec.method_id == "minecraft.runtime.capture"
        ):
            blockers.append("NICHE_STYLE_MISMATCH")

        same_tool = spec.tool_id == request.current_tool_id
        offer = self._capability_offer(spec.capability_id)
        if offer is None:
            blockers.append("CAPABILITY_NOT_REGISTERED")
        else:
            if not offer.executable:
                blockers.append("CAPABILITY_NOT_EXECUTABLE")
            if request.local_only and not offer.local:
                blockers.append("NON_LOCAL_METHOD")
            if (
                not same_tool
                and offer.quality < request.min_quality
            ):
                blockers.append("CAPABILITY_QUALITY_BELOW_TARGET")
            if (
                request.max_vram_gb is not None
                and offer.vram_gb is not None
                and offer.vram_gb > request.max_vram_gb
            ):
                blockers.append("CAPABILITY_VRAM_EXCEEDED")

        if spec.handler not in self.registered_handlers:
            blockers.append("TURBO_HANDLER_NOT_REGISTERED")

        qualification = self._qualification(spec.tool_id)
        if not same_tool:
            if qualification is None:
                blockers.append("PRODUCTION_QUALIFICATION_MISSING")
            elif not qualification.qualified:
                blockers.append("PRODUCTION_QUALIFICATION_FAILED")
        else:
            # The incumbent tool is already executing the shot in production;
            # switching renderer inside the same canonical tool does not add a
            # new third-party/tool trust boundary.
            reasons.append("INCUMBENT_TOOL_TRUST_BOUNDARY")

        if request.commercial_safe:
            if spec.commercial_safe is not True and not same_tool:
                blockers.append("METHOD_COMMERCIAL_SAFETY_UNVERIFIED")

        if (
            request.max_vram_gb is not None
            and spec.vram_gb is not None
            and spec.vram_gb > request.max_vram_gb
        ):
            blockers.append("METHOD_VRAM_EXCEEDED")

        if not request.required_tags.issubset(spec.tags):
            blockers.append("METHOD_REQUIRED_TAGS_MISSING")

        workflow = None
        if spec.requires_video_workflow:
            workflow = self._video_workflow(spec)
            if workflow is None:
                blockers.append("VIDEO_WORKFLOW_MISSING")
            elif not self._workflow_model_approved(workflow):
                blockers.append("WORKFLOW_MODEL_NOT_PRODUCTION_APPROVED")

        if spec.requires_block_normalizer:
            normalizer = getattr(
                self.ctx,
                "cross_backend_video",
                None,
            )
            if (
                normalizer is None
                or not spec.normalizer_id
                or getattr(
                    normalizer.profile,
                    "normalizer_id",
                    None,
                )
                != spec.normalizer_id
            ):
                blockers.append(
                    "BLOCK_SHOT_NORMALIZATION_ADAPTER_MISSING"
                )
            else:
                blockers.extend(
                    normalizer.assess_method_request(
                        request,
                        spec,
                    )
                )

        if request.continuity_priority and not spec.same_scene_semantics:
            if not request.backend_switch_allowed:
                blockers.append(
                    "CONTINUITY_BACKEND_SWITCH_BLOCKED"
                )
            elif (
                request.recurring_identity_required
                and not spec.identity_conditioning_supported
            ):
                blockers.append(
                    "IDENTITY_CONDITIONING_NOT_SUPPORTED"
                )
            elif (
                request.recurring_identity_required
                and (
                    not request.reference_frame_path
                    or not Path(
                        request.reference_frame_path
                    ).is_file()
                )
            ):
                blockers.append(
                    "RECURRING_IDENTITY_REFERENCE_REQUIRED"
                )

        projected = None
        if request.mean_current_attempt_seconds > 0:
            projected = (
                request.mean_current_attempt_seconds
                * spec.estimated_time_multiplier
            )
            if (
                request.max_additional_gpu_seconds is not None
                and projected
                > request.max_additional_gpu_seconds
            ):
                blockers.append("METHOD_SWITCH_GPU_BUDGET_EXCEEDED")

        if spec.quality < request.min_quality:
            blockers.append("METHOD_QUALITY_BELOW_TARGET")

        reasons.extend(
            [
                f"quality={spec.quality:.3f}",
                f"control={spec.control:.3f}",
                f"determinism={spec.deterministic:.3f}",
                f"speed={spec.speed:.3f}",
                f"same_scene_semantics={spec.same_scene_semantics}",
            ]
        )
        if workflow is not None:
            reasons.append(
                f"workflow={workflow.workflow_id}@{workflow.version}"
            )

        return MethodCandidateAssessment(
            method_id=spec.method_id,
            tool_id=spec.tool_id,
            capability_id=spec.capability_id,
            capability_kind=spec.capability_kind,
            eligible=not blockers,
            execution_ready=not blockers,
            score=(
                self._score(request, spec)
                if not blockers
                else 0.0
            ),
            blockers=sorted(set(blockers)),
            warnings=warnings,
            reasons=reasons,
            workflow_id=(
                workflow.workflow_id
                if workflow is not None
                else None
            ),
            workflow_version=(
                workflow.version
                if workflow is not None
                else None
            ),
            projected_gpu_seconds=projected,
        )

    def deliberate(
        self,
        request: MethodSwitchRequest,
    ) -> MethodSwitchDecision:
        assessments = [
            self.assess(request, spec)
            for spec in self.specs
        ]
        eligible = sorted(
            (
                item
                for item in assessments
                if item.eligible and item.execution_ready
            ),
            key=lambda item: (
                item.score,
                item.method_id,
            ),
            reverse=True,
        )
        if eligible:
            selected = eligible[0]
            spec = next(
                item
                for item in self.specs
                if item.method_id == selected.method_id
            )
            return MethodSwitchDecision(
                request=request,
                status=MethodSwitchStatus.SELECTED,
                selected_method_id=selected.method_id,
                selected_tool_id=selected.tool_id,
                selected_capability_id=selected.capability_id,
                selected_handler=spec.handler,
                assessments=assessments,
                reasons=[
                    f"selected={selected.method_id}",
                    f"score={selected.score:.4f}",
                    "all hard execution gates passed",
                ],
            )

        all_blockers = [
            blocker
            for item in assessments
            for blocker in item.blockers
        ]
        status = MethodSwitchStatus.BLOCKED_ACQUISITION
        if all_blockers and all(
            blocker == "CONTINUITY_BACKEND_SWITCH_BLOCKED"
            for blocker in all_blockers
        ):
            status = MethodSwitchStatus.BLOCKED_CONTINUITY
        elif any(
            blocker in {
                "NON_LOCAL_METHOD",
                "METHOD_COMMERCIAL_SAFETY_UNVERIFIED",
                "METHOD_SWITCH_GPU_BUDGET_EXCEEDED",
            }
            for blocker in all_blockers
        ) and not any(
            blocker in {
                "CAPABILITY_NOT_EXECUTABLE",
                "PRODUCTION_QUALIFICATION_FAILED",
                "PRODUCTION_QUALIFICATION_MISSING",
                "VIDEO_WORKFLOW_MISSING",
                "BLOCK_SHOT_NORMALIZATION_ADAPTER_MISSING",
            }
            for blocker in all_blockers
        ):
            status = MethodSwitchStatus.BLOCKED_POLICY

        decision = MethodSwitchDecision(
            request=request,
            status=status,
            assessments=assessments,
            reasons=["NO_ALTERNATIVE_METHOD_PASSED_ALL_GATES"],
        )
        acquisition = self.create_acquisition_request(decision)
        decision.acquisition_request_path = str(acquisition)
        return decision

    def create_acquisition_request(
        self,
        decision: MethodSwitchDecision,
    ) -> Path:
        gaps = {
            item.method_id: list(item.blockers)
            for item in decision.assessments
            if item.blockers
        }
        required: list[str] = []
        flat = {
            blocker
            for blockers in gaps.values()
            for blocker in blockers
        }
        if "VIDEO_WORKFLOW_MISSING" in flat:
            required.append(
                "QUALIFIED_LOCAL_VIDEO_WORKFLOW"
            )
        if "WORKFLOW_MODEL_NOT_PRODUCTION_APPROVED" in flat:
            required.append(
                "PRODUCTION_APPROVED_VIDEO_MODEL"
            )
        if "BLOCK_SHOT_NORMALIZATION_ADAPTER_MISSING" in flat:
            required.append(
                "BLOCK_SHOT_BACKEND_NORMALIZATION_ADAPTER"
            )
        if "TURBO_HANDLER_NOT_REGISTERED" in flat:
            required.append("TURBO_EXECUTION_HANDLER")
        if any(
            token.startswith("PRODUCTION_QUALIFICATION")
            for token in flat
        ):
            required.append("PRODUCTION_QUALIFICATION")
        if "CAPABILITY_NOT_EXECUTABLE" in flat:
            required.append("EXECUTABLE_CAPABILITY")

        request = decision.request
        return self.store.save_acquisition(
            CapabilityAcquisitionRequest(
                project_id=request.project_id,
                episode_id=request.episode_id,
                shot_id=request.shot_id,
                current_method_id=request.current_method_id,
                requested_policy=request.policy,
                required_quality=request.min_quality,
                max_vram_gb=request.max_vram_gb,
                local_only=request.local_only,
                commercial_safe=request.commercial_safe,
                failure_codes=list(request.failure_codes),
                candidate_gaps=gaps,
                required_next_capabilities=sorted(
                    set(required)
                ),
            )
        )

    def build_acquisition_work_item(
        self,
        decision: MethodSwitchDecision,
        *,
        resume_context: dict[str, Any] | None = None,
    ) -> WorkItem:
        if decision.executable:
            raise RuntimeError(
                "EXECUTABLE_SWITCH_DOES_NOT_NEED_ACQUISITION"
            )
        if not decision.acquisition_request_path:
            decision.acquisition_request_path = str(
                self.create_acquisition_request(decision)
            )
        request_path = str(
            decision.acquisition_request_path
        )
        return WorkItem(
            project_id=decision.request.project_id,
            kind="rnd.capability.acquire",
            handler="rnd.capability.acquire",
            resource=ResourceClass.AGENT,
            priority=88,
            payload={
                "episode_id": decision.request.episode_id,
                "shot_id": decision.request.shot_id,
                "request_path": request_path,
                "method_switch_request": (
                    decision.request.model_dump(mode="json")
                ),
                "resume_context": dict(
                    resume_context or {}
                ),
                "current_method_id": (
                    decision.request.current_method_id
                ),
                "requested_policy": (
                    decision.request.policy.value
                ),
                "required_quality": (
                    decision.request.min_quality
                ),
                "max_vram_gb": (
                    decision.request.max_vram_gb
                ),
                "failure_codes": list(
                    decision.request.failure_codes
                ),
                "research_sources": [
                    "OFFICIAL_DOCS",
                    "MODEL_CARDS",
                    "GITHUB",
                    "COMFYUI_WORKFLOW_REGISTRY",
                    "TOOL_ADAPTER_REGISTRY",
                ],
                "required_gates": [
                    "LICENSE_REVIEW",
                    "SECURITY_REVIEW",
                    "HARDWARE_COMPATIBILITY",
                    "SANDBOX_BENCHMARK",
                    "QUALITY_BENCHMARK",
                    "AUTOMATION_READINESS",
                    "BLOCK_SHOT_NORMALIZATION",
                    "PRODUCTION_QUALIFICATION",
                ],
            },
            max_attempts=1,
        )

    def transform_block_shot(
        self,
        shot: CompiledShot,
        decision: MethodSwitchDecision,
        *,
        repaired_base: CompiledShot | None = None,
    ) -> CompiledShot:
        if not decision.executable:
            raise RuntimeError(
                "METHOD_SWITCH_DECISION_NOT_EXECUTABLE"
            )
        base = (repaired_base or shot).model_copy(deep=True)
        if decision.selected_method_id == "blender.cycles.quality":
            base.render_engine = "CYCLES"
            base.render_quality.engine = "CYCLES"
            base.render_quality.profile_id = (
                "auto_cycles_quality_recovery"
            )
            base.render_quality.render_percentage = 100
            base.render_quality.taa_samples = max(
                64,
                int(base.render_quality.taa_samples),
            )
            metadata = dict(
                base.creative_intent.get(
                    "production_method_switch"
                )
                or {}
            )
            metadata.update(
                {
                    "method_id": decision.selected_method_id,
                    "from_method": (
                        decision.request.current_method_id
                    ),
                    "policy": decision.request.policy.value,
                    "preserve_creative_intent": True,
                    "preserve_camera": True,
                    "preserve_animation": True,
                    "preserve_scene_geometry": True,
                }
            )
            base.creative_intent[
                "production_method_switch"
            ] = metadata
            return base
        if decision.selected_method_id == (
            "comfyui.wan21.fun.inpaint.1.3b"
        ):
            metadata = dict(
                base.creative_intent.get(
                    "production_method_switch"
                )
                or {}
            )
            metadata.update(
                {
                    "method_id": decision.selected_method_id,
                    "from_method": (
                        decision.request.current_method_id
                    ),
                    "policy": decision.request.policy.value,
                    "preserve_creative_intent": True,
                    "preserve_camera_intent": True,
                    "preserve_reference_identity": bool(
                        decision.request.reference_frame_path
                    ),
                    "normalizer_id": (
                        "blockvideo.wan21.fun.inpaint.v1"
                    ),
                }
            )
            base.creative_intent[
                "production_method_switch"
            ] = metadata
            return base
        raise RuntimeError(
            "SELECTED_METHOD_HAS_NO_BLOCK_SHOT_TRANSFORM"
        )

    def build_work_item(
        self,
        *,
        compiled: Any,
        shot: CompiledShot,
        decision: MethodSwitchDecision,
        output_path: Path,
        render_preview: bool,
        switch_round: int,
        switch_of_work_id: str,
        blender_executable: str | None = None,
        continuation: dict[str, Any] | None = None,
    ) -> WorkItem:
        if not decision.executable:
            raise RuntimeError(
                "METHOD_SWITCH_DECISION_NOT_EXECUTABLE"
            )
        spec = next(
            item
            for item in self.specs
            if item.method_id == decision.selected_method_id
        )
        if spec.execution_mode is MethodExecutionMode.BLENDER_CYCLES:
            payload = {
                "job": BlenderAnimationJob(
                    project_id=compiled.project_id,
                    episode_id=compiled.episode_id,
                    shot=shot,
                    output_path=str(output_path),
                    render_preview=render_preview,
                ).model_dump(mode="json"),
                "output_units": max(1, shot.frame_end),
                "repair_round": switch_round,
                "method_switch_round": switch_round,
                "method_switch_of_work_id": switch_of_work_id,
                "method_id": spec.method_id,
                "method_switch": True,
            }
            if blender_executable:
                payload["blender_executable"] = (
                    blender_executable
                )
            if continuation:
                payload["continuation"] = dict(continuation)
            return WorkItem(
                project_id=compiled.project_id,
                kind="block.render.method_switch",
                handler=spec.handler,
                resource=spec.resource,
                priority=max(80, 99 - int(shot.order)),
                model_affinity="BLENDER:CYCLES",
                payload=payload,
                max_attempts=1,
            )
        if spec.execution_mode is MethodExecutionMode.COMFY_VIDEO:
            normalizer = getattr(
                self.ctx,
                "cross_backend_video",
                None,
            )
            if normalizer is None:
                raise RuntimeError(
                    "CROSS_BACKEND_VIDEO_SERVICE_NOT_CONFIGURED"
                )
            return normalizer.build_work_item(
                compiled=compiled,
                shot=shot,
                output_path=output_path,
                render_preview=render_preview,
                switch_round=switch_round,
                switch_of_work_id=switch_of_work_id,
                reference_frame_path=(
                    decision.request.reference_frame_path
                ),
                recurring_identity_required=(
                    decision.request.recurring_identity_required
                ),
                semantic_performance_required=(
                    decision.request.semantic_performance_required
                ),
                precise_camera_required=(
                    decision.request.precise_camera_required
                ),
                continuation=continuation,
            )
        raise RuntimeError(
            "METHOD_SWITCH_EXECUTION_ADAPTER_NOT_IMPLEMENTED"
        )
