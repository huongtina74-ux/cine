from __future__ import annotations

from pydantic import BaseModel, Field

from .contracts import CapabilityKind, CapabilityOffer, CapabilityRequirement, CapabilityStatus, RoutingDecision


class CapabilityProvider(BaseModel):
    provider_id: str
    kind: CapabilityKind
    status: CapabilityStatus = CapabilityStatus.PLANNED
    executable: bool = False
    local: bool = True
    deterministic: bool | None = None
    commercial_safe: bool | None = None
    quality_score: float = Field(default=0.5, ge=0.0, le=1.0)
    speed_score: float = Field(default=0.5, ge=0.0, le=1.0)
    control_score: float = Field(default=0.5, ge=0.0, le=1.0)
    vram_gb: float | None = Field(default=None, ge=0)
    tags: set[str] = Field(default_factory=set)
    limitations: list[str] = Field(default_factory=list)

    def as_offer(self) -> CapabilityOffer:
        return CapabilityOffer(
            capability_id=self.provider_id,
            kind=self.kind,
            provider=self.provider_id,
            executable=self.executable and self.status is CapabilityStatus.EXECUTABLE,
            local=self.local,
            commercial_safe=self.commercial_safe,
            deterministic=1.0 if self.deterministic is True else (0.5 if self.deterministic is None else 0.0),
            quality=self.quality_score,
            speed=self.speed_score,
            vram_gb=self.vram_gb,
            tags=set(self.tags),
        )


DEFAULT_CAPABILITIES: list[CapabilityOffer] = [
    CapabilityOffer(
        capability_id="blender.offline3d",
        kind=CapabilityKind.OFFLINE_3D,
        provider="Blender",
        executable=True,
        local=True,
        commercial_safe=True,
        deterministic=0.92,
        quality=0.82,
        speed=0.62,
        vram_gb=1.5,
        tags={"camera_precision", "character_animation", "python", "headless"},
    ),
    CapabilityOffer(
        capability_id="comfyui.image",
        kind=CapabilityKind.AI_IMAGE,
        provider="ComfyUI",
        executable=True,
        local=True,
        commercial_safe=None,
        deterministic=0.45,
        quality=0.78,
        speed=0.70,
        vram_gb=8.0,
        tags={"workflow", "reference_conditioning", "local"},
    ),
    CapabilityOffer(
        capability_id="comfyui.video",
        kind=CapabilityKind.AI_VIDEO,
        provider="ComfyUI",
        executable=True,
        local=True,
        commercial_safe=None,
        deterministic=0.30,
        quality=0.72,
        speed=0.32,
        vram_gb=12.0,
        tags={"workflow", "local"},
    ),
    CapabilityOffer(
        capability_id="ffmpeg.editorial",
        kind=CapabilityKind.EDITORIAL,
        provider="FFmpeg",
        executable=True,
        local=True,
        commercial_safe=True,
        deterministic=1.0,
        quality=0.76,
        speed=0.92,
        tags={"headless", "batch", "encode", "timeline_execution"},
    ),
    CapabilityOffer(
        capability_id="ffmpeg.qc",
        kind=CapabilityKind.QC,
        provider="FFmpeg/ffprobe",
        executable=True,
        local=True,
        commercial_safe=True,
        deterministic=1.0,
        quality=0.70,
        speed=0.95,
        tags={"technical_qc", "probe"},
    ),
    CapabilityOffer(
        capability_id="unreal.realtime3d",
        kind=CapabilityKind.REALTIME_3D,
        provider="Unreal Engine",
        executable=False,
        local=True,
        commercial_safe=None,
        deterministic=0.85,
        quality=0.92,
        speed=0.72,
        vram_gb=8.0,
        tags={"realtime", "large_world", "sequencer"},
    ),
    CapabilityOffer(
        capability_id="minecraft.runtime",
        kind=CapabilityKind.GAME_RUNTIME,
        provider="Minecraft Runtime",
        executable=False,
        local=True,
        commercial_safe=None,
        deterministic=0.72,
        quality=0.88,
        speed=0.82,
        tags={"minecraft", "actual_gameplay", "replay"},
    ),
    CapabilityOffer(
        capability_id="roblox.studio",
        kind=CapabilityKind.GAME_RUNTIME,
        provider="Roblox Studio",
        executable=False,
        local=True,
        commercial_safe=None,
        deterministic=0.75,
        quality=0.86,
        speed=0.80,
        tags={"roblox", "studio", "machinima"},
    ),
    CapabilityOffer(
        capability_id="screen.capture",
        kind=CapabilityKind.SCREEN_CAPTURE,
        provider="Screen Capture",
        executable=False,
        local=True,
        commercial_safe=True,
        deterministic=0.95,
        quality=0.82,
        speed=0.92,
        tags={"desktop", "tutorial"},
    ),
    CapabilityOffer(
        capability_id="resolve.editorial",
        kind=CapabilityKind.EDITORIAL,
        provider="DaVinci Resolve",
        executable=False,
        local=True,
        commercial_safe=None,
        deterministic=0.90,
        quality=0.95,
        speed=0.80,
        tags={"nle", "fusion", "color", "fairlight"},
    ),
    CapabilityOffer(
        capability_id="premiere.editorial",
        kind=CapabilityKind.EDITORIAL,
        provider="Adobe Premiere Pro",
        executable=False,
        local=True,
        commercial_safe=None,
        deterministic=0.90,
        quality=0.94,
        speed=0.82,
        tags={"nle", "uxp", "text_based_editing"},
    ),
    CapabilityOffer(
        capability_id="aftereffects.motion",
        kind=CapabilityKind.MOTION_GRAPHICS,
        provider="Adobe After Effects",
        executable=False,
        local=True,
        commercial_safe=None,
        deterministic=0.90,
        quality=0.94,
        speed=0.64,
        tags={"motion_graphics", "compositing", "scripting"},
    ),
    CapabilityOffer(
        capability_id="fusion.compositing",
        kind=CapabilityKind.COMPOSITING,
        provider="Fusion",
        executable=False,
        local=True,
        commercial_safe=None,
        deterministic=0.91,
        quality=0.94,
        speed=0.70,
        tags={"compositing", "motion_graphics", "nodes"},
    ),
]


class CapabilityRegistry:
    def __init__(self, offers: list[CapabilityOffer] | None = None) -> None:
        self._offers = {o.capability_id: o for o in (offers or DEFAULT_CAPABILITIES)}

    def register(self, offer: CapabilityOffer | CapabilityProvider) -> None:
        normalized = offer.as_offer() if isinstance(offer, CapabilityProvider) else offer
        self._offers[normalized.capability_id] = normalized

    def list(self, kind: CapabilityKind | None = None) -> list[CapabilityOffer]:
        values = list(self._offers.values())
        if kind is not None:
            values = [x for x in values if x.kind is kind]
        return sorted(values, key=lambda x: x.capability_id)
    def route(self, requirement: CapabilityRequirement) -> RoutingDecision:
        candidates: list[tuple[float, CapabilityOffer]] = []
        rejects: list[str] = []
        for offer in self.list(requirement.kind):
            reasons: list[str] = []
            if not offer.executable:
                rejects.append(f"{offer.capability_id}:NOT_EXECUTABLE")
                continue
            if requirement.local_only and not offer.local:
                rejects.append(f"{offer.capability_id}:NOT_LOCAL")
                continue
            if requirement.commercial_safe and offer.commercial_safe is not True:
                rejects.append(f"{offer.capability_id}:COMMERCIAL_SAFETY_UNVERIFIED")
                continue
            if offer.deterministic < requirement.deterministic_min:
                rejects.append(f"{offer.capability_id}:DETERMINISM")
                continue
            if offer.quality < requirement.quality_min:
                rejects.append(f"{offer.capability_id}:QUALITY")
                continue
            if requirement.max_vram_gb is not None and offer.vram_gb is not None and offer.vram_gb > requirement.max_vram_gb:
                rejects.append(f"{offer.capability_id}:VRAM")
                continue
            if not requirement.required_tags.issubset(offer.tags):
                rejects.append(f"{offer.capability_id}:MISSING_TAGS")
                continue
            score = 0.55 * offer.quality + 0.25 * offer.deterministic + 0.20 * offer.speed
            candidates.append((score, offer))

        if not candidates:
            return RoutingDecision(
                requirement=requirement,
                executable=False,
                reasons=["NO_CAPABILITY_SATISFIES_REQUIREMENT"],
                warnings=rejects,
            )
        score, selected = max(candidates, key=lambda x: (x[0], x[1].capability_id))
        return RoutingDecision(
            requirement=requirement,
            selected_capability_id=selected.capability_id,
            executable=True,
            score=round(score, 4),
            reasons=[
                f"provider={selected.provider}",
                f"quality={selected.quality}",
                f"determinism={selected.deterministic}",
                f"speed={selected.speed}",
            ],
            warnings=rejects,
        )


class TechnicalDirector:
    """Translates semantic segment requirements into fail-closed provider choices."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def choose(self, need):
        requirement = CapabilityRequirement(
            kind=need.capability,
            local_only=need.local_only,
            commercial_safe=need.commercial_safe,
            deterministic_min=1.0 if need.deterministic is True else 0.0,
            quality_min=need.min_quality,
            max_vram_gb=need.max_vram_gb,
            required_tags=set(need.metadata.get("required_tags", [])),
        )
        decision = self.registry.route(requirement)
        if not decision.executable or not decision.selected_capability_id:
            return None, [f"NO_EXECUTABLE_PROVIDER:{need.capability.value}"]
        selected = next(
            item for item in self.registry.list(need.capability)
            if item.capability_id == decision.selected_capability_id
        )
        return selected, []

    def compile_segment(self, segment):
        from .segments import SegmentExecutionPlan

        plans = []
        findings = []
        for need in segment.requirements:
            provider, errors = self.choose(need)
            if provider is None:
                findings.extend(f"{segment.segment_id}:{item}" for item in errors)
                continue
            plans.append(
                SegmentExecutionPlan(
                    segment_id=segment.segment_id,
                    capability=need.capability,
                    provider_id=provider.capability_id,
                    executable=True,
                    reason="best approved executable capability",
                    fallback_provider_ids=[],
                )
            )
        return plans, findings
