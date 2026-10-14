from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.block_animation.contracts import CompiledShot

from .production_method_switch import (
    MethodSwitchDecision,
    MethodSwitchPolicy,
    MethodSwitchRequest,
    ProductionMethodSwitchController,
)


class ShotRouteMode(StrEnum):
    DEFAULT_BLENDER = "DEFAULT_BLENDER"
    CONTROLLED_BLENDER = "CONTROLLED_BLENDER"
    GENERATIVE_VIDEO = "GENERATIVE_VIDEO"
    BLOCKED = "BLOCKED"


class ShotRoutingDecision(BaseModel):
    project_id: str
    episode_id: str
    shot_id: str
    mode: ShotRouteMode
    proactive: bool = False
    strict: bool = False
    requested_backend: str | None = None
    selected_method_id: str | None = None
    selected_handler: str | None = None
    reference_frame_path: str | None = None
    precise_camera_required: bool = False
    semantic_performance_required: bool = False
    recurring_identity_required: bool = False
    method_decision: MethodSwitchDecision | None = None
    reasons: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)

    @property
    def executable_method(self) -> bool:
        return bool(
            self.method_decision is not None
            and self.method_decision.executable
        )

    @property
    def use_default_blender(self) -> bool:
        return self.mode is ShotRouteMode.DEFAULT_BLENDER


class ShotRoutingAdapter:
    """Requirement adapter over the existing MethodSwitch authority.

    The adapter does not score production methods itself. It translates explicit
    shot requirements into a MethodSwitchRequest. Default shots remain on the
    existing Blender-first path. This makes proactive hybrid routing opt-in and
    preserves all existing production behavior unless requested.
    """

    _GENERATIVE_BACKENDS = {
        "AI_VIDEO",
        "WAN",
        "WAN21",
        "COMFYUI",
        "COMFYUI_VIDEO",
        "GENERATIVE_VIDEO",
    }

    def __init__(
        self,
        method_switch: ProductionMethodSwitchController,
        *,
        character_factory: Any | None = None,
    ) -> None:
        self.method_switch = method_switch
        self.character_factory = character_factory

    @staticmethod
    def _bool(meta: dict[str, Any], *keys: str) -> bool:
        return any(bool(meta.get(key)) for key in keys)

    @staticmethod
    def _preferred_backend(meta: dict[str, Any]) -> str:
        value = (
            meta.get("preferred_backend")
            or meta.get("production_backend")
            or meta.get("backend_preference")
            or ""
        )
        return str(value).strip().upper()

    @staticmethod
    def _explicit_reference(
        meta: dict[str, Any],
        episode_metadata: dict[str, Any],
        shot_id: str,
    ) -> str | None:
        for key in (
            "reference_frame_path",
            "reference_media_path",
            "identity_reference_path",
        ):
            value = meta.get(key)
            if value:
                return str(value)
        references = episode_metadata.get(
            "shot_reference_media"
        )
        if isinstance(references, dict):
            value = references.get(shot_id)
            if value:
                return str(value)
        value = episode_metadata.get(
            "reference_frame_path"
        )
        return str(value) if value else None

    def _character_reference(
        self,
        shot: CompiledShot,
    ) -> str | None:
        factory = self.character_factory
        if factory is None or not shot.actors:
            return None

        path_lists: list[list[str]] = []
        for actor in shot.actors:
            try:
                record = factory.record_for_rig(
                    str(actor.rig_id)
                )
            except Exception:
                return None
            paths: list[str] = []
            for reference_id in reversed(
                record.reference_ids
            ):
                try:
                    pack = factory.store.get_reference(
                        record.global_character_id,
                        reference_id,
                    )
                except Exception:
                    continue
                path = str(pack.source_media_path)
                if (
                    path
                    and Path(path).is_file()
                    and path not in paths
                ):
                    paths.append(path)
            if not paths:
                return None
            path_lists.append(paths)

        common = set(path_lists[0])
        for values in path_lists[1:]:
            common.intersection_update(values)
        if not common:
            return None
        for path in path_lists[0]:
            if path in common:
                return path
        return None

    def _reference(
        self,
        shot: CompiledShot,
        *,
        episode_metadata: dict[str, Any],
    ) -> str | None:
        meta = dict(shot.creative_intent or {})
        explicit = self._explicit_reference(
            meta,
            episode_metadata,
            shot.shot_id,
        )
        if explicit:
            return explicit
        return self._character_reference(shot)

    @staticmethod
    def _strict(
        meta: dict[str, Any],
        episode_metadata: dict[str, Any],
    ) -> bool:
        if "hybrid_routing_strict" in meta:
            return bool(meta["hybrid_routing_strict"])
        return bool(
            episode_metadata.get(
                "proactive_hybrid_routing_strict",
                False,
            )
        )

    @staticmethod
    def _proactive_enabled(
        meta: dict[str, Any],
        episode_metadata: dict[str, Any],
    ) -> bool:
        if "proactive_hybrid_routing" in meta:
            return bool(
                meta["proactive_hybrid_routing"]
            )
        return bool(
            episode_metadata.get(
                "proactive_hybrid_routing",
                False,
            )
        )

    def route(
        self,
        *,
        project_id: str,
        episode_id: str,
        shot: CompiledShot,
        episode_metadata: dict[str, Any] | None = None,
    ) -> ShotRoutingDecision:
        episode_metadata = dict(
            episode_metadata or {}
        )
        meta = dict(shot.creative_intent or {})
        proactive = self._proactive_enabled(
            meta,
            episode_metadata,
        )
        strict = self._strict(
            meta,
            episode_metadata,
        )
        precise_camera = self._bool(
            meta,
            "precise_camera_required",
            "exact_camera_required",
            "camera_geometry_required",
        )
        semantic_performance = bool(
            self._bool(
                meta,
                "semantic_performance_required",
                "dialogue_performance_required",
            )
            or shot.performance_directives
        )
        preferred = self._preferred_backend(meta)
        generative = bool(
            self._bool(
                meta,
                "generative_video_preferred",
                "ai_video_preferred",
            )
            or preferred in self._GENERATIVE_BACKENDS
        )
        recurring_identity = bool(
            shot.actors
            and (
                generative
                or self._bool(
                    meta,
                    "recurring_identity_required",
                    "identity_continuity_required",
                )
            )
        )

        if not proactive:
            return ShotRoutingDecision(
                project_id=project_id,
                episode_id=episode_id,
                shot_id=shot.shot_id,
                mode=ShotRouteMode.DEFAULT_BLENDER,
                proactive=False,
                strict=strict,
                precise_camera_required=precise_camera,
                semantic_performance_required=semantic_performance,
                recurring_identity_required=recurring_identity,
                reasons=[
                    "PROACTIVE_HYBRID_ROUTING_DISABLED",
                    "DEFAULT_BLENDER_PATH_PRESERVED",
                ],
            )

        # Performance/camera authority outranks a generative preference.
        if precise_camera or semantic_performance:
            tags: set[str] = set()
            reasons: list[str] = []
            if precise_camera:
                tags.add("camera_precision")
                reasons.append(
                    "PRECISE_CAMERA_REQUIRES_CONTROLLED_3D"
                )
            if semantic_performance:
                tags.add("character_animation")
                reasons.append(
                    "SEMANTIC_PERFORMANCE_REQUIRES_CONTROLLED_3D"
                )
            request = MethodSwitchRequest(
                project_id=project_id,
                episode_id=episode_id,
                shot_id=shot.shot_id,
                current_tool_id="blender",
                current_method_id=(
                    "blender.eevee.current"
                ),
                policy=(
                    MethodSwitchPolicy
                    .QUALITY_FIRST_ALTERNATIVE
                ),
                min_quality=0.80,
                max_vram_gb=float(
                    episode_metadata.get(
                        "max_vram_gb",
                        12.0,
                    )
                ),
                local_only=True,
                commercial_safe=True,
                continuity_priority=True,
                backend_switch_allowed=False,
                recurring_identity_required=bool(
                    shot.actors
                ),
                precise_camera_required=precise_camera,
                semantic_performance_required=(
                    semantic_performance
                ),
                visual_style=shot.visual_style,
                failure_codes=[
                    "PROACTIVE_SHOT_ROUTING",
                ],
                required_tags=tags,
            )
            decision = self.method_switch.deliberate(
                request
            )
            if decision.executable:
                return ShotRoutingDecision(
                    project_id=project_id,
                    episode_id=episode_id,
                    shot_id=shot.shot_id,
                    mode=(
                        ShotRouteMode
                        .CONTROLLED_BLENDER
                    ),
                    proactive=True,
                    strict=strict,
                    requested_backend="BLENDER",
                    selected_method_id=(
                        decision.selected_method_id
                    ),
                    selected_handler=(
                        decision.selected_handler
                    ),
                    precise_camera_required=(
                        precise_camera
                    ),
                    semantic_performance_required=(
                        semantic_performance
                    ),
                    recurring_identity_required=bool(
                        shot.actors
                    ),
                    method_decision=decision,
                    reasons=[
                        *reasons,
                        *decision.reasons,
                    ],
                )

            # Default Eevee is still a controlled Blender backend and preserves
            # geometry/performance semantics. Non-strict routing can safely
            # fall back to it instead of crossing backend boundaries.
            if not strict:
                return ShotRoutingDecision(
                    project_id=project_id,
                    episode_id=episode_id,
                    shot_id=shot.shot_id,
                    mode=ShotRouteMode.DEFAULT_BLENDER,
                    proactive=True,
                    strict=False,
                    requested_backend="BLENDER",
                    precise_camera_required=(
                        precise_camera
                    ),
                    semantic_performance_required=(
                        semantic_performance
                    ),
                    recurring_identity_required=bool(
                        shot.actors
                    ),
                    method_decision=decision,
                    reasons=[
                        *reasons,
                        "CONTROLLED_ROUTE_FALLBACK_DEFAULT_BLENDER",
                    ],
                    blockers=[
                        reason
                        for item in decision.assessments
                        for reason in item.blockers
                    ],
                )
            return ShotRoutingDecision(
                project_id=project_id,
                episode_id=episode_id,
                shot_id=shot.shot_id,
                mode=ShotRouteMode.BLOCKED,
                proactive=True,
                strict=True,
                requested_backend="BLENDER",
                precise_camera_required=precise_camera,
                semantic_performance_required=(
                    semantic_performance
                ),
                recurring_identity_required=bool(
                    shot.actors
                ),
                method_decision=decision,
                reasons=reasons,
                blockers=[
                    "CONTROLLED_3D_ROUTE_UNAVAILABLE",
                    *[
                        reason
                        for item in decision.assessments
                        for reason in item.blockers
                    ],
                ],
            )

        if generative:
            reference = self._reference(
                shot,
                episode_metadata=episode_metadata,
            )
            if not reference:
                blockers = [
                    "GENERATIVE_ROUTE_REFERENCE_REQUIRED"
                ]
                if strict:
                    return ShotRoutingDecision(
                        project_id=project_id,
                        episode_id=episode_id,
                        shot_id=shot.shot_id,
                        mode=ShotRouteMode.BLOCKED,
                        proactive=True,
                        strict=True,
                        requested_backend=(
                            preferred
                            or "AI_VIDEO"
                        ),
                        precise_camera_required=False,
                        semantic_performance_required=False,
                        recurring_identity_required=bool(
                            shot.actors
                        ),
                        blockers=blockers,
                    )
                return ShotRoutingDecision(
                    project_id=project_id,
                    episode_id=episode_id,
                    shot_id=shot.shot_id,
                    mode=ShotRouteMode.DEFAULT_BLENDER,
                    proactive=True,
                    strict=False,
                    requested_backend=(
                        preferred
                        or "AI_VIDEO"
                    ),
                    recurring_identity_required=bool(
                        shot.actors
                    ),
                    reasons=[
                        "GENERATIVE_ROUTE_REQUESTED",
                        "FALLBACK_DEFAULT_BLENDER",
                    ],
                    blockers=blockers,
                )

            request = MethodSwitchRequest(
                project_id=project_id,
                episode_id=episode_id,
                shot_id=shot.shot_id,
                current_tool_id="blender",
                current_method_id=(
                    "blender.cycles.quality"
                ),
                policy=(
                    MethodSwitchPolicy
                    .BALANCED_ALTERNATIVE
                ),
                min_quality=0.70,
                max_vram_gb=float(
                    episode_metadata.get(
                        "max_vram_gb",
                        12.0,
                    )
                ),
                local_only=True,
                commercial_safe=True,
                continuity_priority=True,
                backend_switch_allowed=True,
                recurring_identity_required=bool(
                    shot.actors
                ),
                reference_frame_path=reference,
                precise_camera_required=False,
                semantic_performance_required=False,
                visual_style=shot.visual_style,
                failure_codes=[
                    "PROACTIVE_GENERATIVE_ROUTE",
                ],
                required_tags={
                    "reference_conditioning"
                },
            )
            decision = self.method_switch.deliberate(
                request
            )
            if decision.executable:
                return ShotRoutingDecision(
                    project_id=project_id,
                    episode_id=episode_id,
                    shot_id=shot.shot_id,
                    mode=ShotRouteMode.GENERATIVE_VIDEO,
                    proactive=True,
                    strict=strict,
                    requested_backend=(
                        preferred
                        or "AI_VIDEO"
                    ),
                    selected_method_id=(
                        decision.selected_method_id
                    ),
                    selected_handler=(
                        decision.selected_handler
                    ),
                    reference_frame_path=reference,
                    recurring_identity_required=bool(
                        shot.actors
                    ),
                    method_decision=decision,
                    reasons=[
                        "GENERATIVE_ROUTE_REQUESTED",
                        "REFERENCE_CONDITIONING_AVAILABLE",
                        *decision.reasons,
                    ],
                )
            if not strict:
                return ShotRoutingDecision(
                    project_id=project_id,
                    episode_id=episode_id,
                    shot_id=shot.shot_id,
                    mode=ShotRouteMode.DEFAULT_BLENDER,
                    proactive=True,
                    strict=False,
                    requested_backend=(
                        preferred
                        or "AI_VIDEO"
                    ),
                    reference_frame_path=reference,
                    recurring_identity_required=bool(
                        shot.actors
                    ),
                    method_decision=decision,
                    reasons=[
                        "GENERATIVE_ROUTE_REQUESTED",
                        "GENERATIVE_ROUTE_BLOCKED",
                        "FALLBACK_DEFAULT_BLENDER",
                    ],
                    blockers=[
                        reason
                        for item in decision.assessments
                        for reason in item.blockers
                    ],
                )
            return ShotRoutingDecision(
                project_id=project_id,
                episode_id=episode_id,
                shot_id=shot.shot_id,
                mode=ShotRouteMode.BLOCKED,
                proactive=True,
                strict=True,
                requested_backend=(
                    preferred
                    or "AI_VIDEO"
                ),
                reference_frame_path=reference,
                recurring_identity_required=bool(
                    shot.actors
                ),
                method_decision=decision,
                reasons=[
                    "GENERATIVE_ROUTE_REQUESTED",
                    "GENERATIVE_ROUTE_BLOCKED",
                ],
                blockers=[
                    "GENERATIVE_METHOD_UNAVAILABLE",
                    *[
                        reason
                        for item in decision.assessments
                        for reason in item.blockers
                    ],
                ],
            )

        return ShotRoutingDecision(
            project_id=project_id,
            episode_id=episode_id,
            shot_id=shot.shot_id,
            mode=ShotRouteMode.DEFAULT_BLENDER,
            proactive=True,
            strict=strict,
            requested_backend="BLENDER",
            reasons=[
                "NO_EXPLICIT_CROSS_BACKEND_REQUIREMENT",
                "DEFAULT_BLENDER_PATH_PRESERVED",
            ],
        )
