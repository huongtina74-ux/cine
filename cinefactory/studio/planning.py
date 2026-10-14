from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .contracts import (
    CapabilityKind,
    MediaFormat,
    MediaProductSpec,
    PlanningInputKind,
    PlanningInputRef,
    StudioProjectSpec,
)


class PlanningMode(StrEnum):
    CINEMATIC_3D = "CINEMATIC_3D"
    AUTHENTIC_GAMEPLAY = "AUTHENTIC_GAMEPLAY"
    HYBRID_GENERATIVE = "HYBRID_GENERATIVE"
    EVIDENCE_DOCUMENTARY = "EVIDENCE_DOCUMENTARY"
    SCREEN_DEMO = "SCREEN_DEMO"
    MOTION_EXPLAINER = "MOTION_EXPLAINER"
    PRODUCT_HYBRID = "PRODUCT_HYBRID"
    TALK_FORMAT = "TALK_FORMAT"
    MUSIC_VISUAL = "MUSIC_VISUAL"


class ReferencePattern(BaseModel):
    source_id: str
    source_kind: str
    category: str
    abstraction: str
    confidence: float = Field(default=0.65, ge=0.0, le=1.0)
    support_count: int = Field(default=1, ge=0)
    sample_count: int = Field(default=1, ge=1)
    evidence_status: str = "HYPOTHESIS"
    reusable: bool = True
    copying_prohibited: bool = True


class ProductionStrategy(BaseModel):
    strategy_id: str
    project_id: str
    planning_mode: PlanningMode
    media_format: MediaFormat
    niche: str
    platform: str
    script_source_mode: str = "PROMPT_FALLBACK"
    script_revision_policy: str = "LOCK"
    script_locked: bool = False
    script_production_profile: dict[str, Any] = Field(default_factory=dict)
    script_required_capabilities: list[CapabilityKind] = Field(default_factory=list)
    conference_lane: str | None = None
    conference_policy: dict[str, Any] = Field(default_factory=dict)
    conference_score: float = Field(default=0.0, ge=0.0, le=1.0)
    input_ids: list[str] = Field(default_factory=list)
    primary_capabilities: list[CapabilityKind] = Field(default_factory=list)
    secondary_capabilities: list[CapabilityKind] = Field(default_factory=list)
    observed_capability_signals: list[CapabilityKind] = Field(default_factory=list)
    hypothesis_capability_signals: list[CapabilityKind] = Field(default_factory=list)
    research_confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    research_confidence_grade: str = "LOW"
    research_decision_ready: bool = False
    research_style_branches: list[dict[str, Any]] = Field(default_factory=list)
    optimization_weights: dict[str, float] = Field(default_factory=dict)
    retention_principles: list[str] = Field(default_factory=list)
    reference_patterns: list[ReferencePattern] = Field(default_factory=list)
    originality_boundaries: list[str] = Field(default_factory=list)
    production_rules: list[str] = Field(default_factory=list)


class CapabilityAssignment(BaseModel):
    capability_kind: CapabilityKind
    ideal_capability_id: str | None = None
    selected_capability_id: str | None = None
    selected_tool_id: str | None = None
    fallback_capability_ids: list[str] = Field(default_factory=list)
    execution_ready: bool = False
    commercial_safe: bool = False
    score: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class SceneProductionPlan(BaseModel):
    scene_id: str
    shot_ids: list[str] = Field(default_factory=list)
    purpose: str
    render_candidate_kinds: list[CapabilityKind] = Field(default_factory=list)
    render_assignment: CapabilityAssignment | None = None
    assignments: list[CapabilityAssignment] = Field(default_factory=list)
    scene_conference_lane: str | None = None
    scene_conference_policy: dict[str, Any] = Field(default_factory=dict)
    scene_conference_metrics: dict[str, Any] = Field(default_factory=dict)
    scene_production_objective: str | None = None
    visual_model_id: str | None = None
    visual_model_fallback_ids: list[str] = Field(default_factory=list)
    visual_model_blockers: list[str] = Field(default_factory=list)
    required_capability_kind: CapabilityKind | None = None
    preferred_capability_kinds: list[CapabilityKind] = Field(default_factory=list)
    optimization_bias: dict[str, float] = Field(default_factory=dict)
    backend_switch_allowed: bool = False
    continuity_priority: bool = True
    quality_target: str = "production"
    notes: list[str] = Field(default_factory=list)

    @property
    def executable(self) -> bool:
        return all(item.execution_ready for item in self.assignments)


class ProductionHandoff(BaseModel):
    project_id: str
    strategy_id: str
    planning_mode: PlanningMode
    scene_plans: list[SceneProductionPlan] = Field(default_factory=list)
    global_assignments: list[CapabilityAssignment] = Field(default_factory=list)
    selected_tool_ids: list[str] = Field(default_factory=list)
    executable: bool = False
    blockers: list[str] = Field(default_factory=list)
    fallback_policy: list[str] = Field(default_factory=list)


class PlanningDepartment:
    """Turns research and references into an original production strategy.

    Competitor material is reduced to abstract patterns. Raw dialogue, exact shot
    order, story events, branding, thumbnails and other protected expression are
    never promoted into the production strategy.
    """

    _ABSTRACT_KEYS = (
        "patterns",
        "production_patterns",
        "format_patterns",
        "retention_patterns",
        "observations",
    )

    def _mode(self, product: MediaProductSpec) -> PlanningMode:
        if product.actual_gameplay_required or product.format is MediaFormat.GAMEPLAY:
            return PlanningMode.AUTHENTIC_GAMEPLAY
        if product.format in {MediaFormat.ANIMATION, MediaFormat.NARRATIVE, MediaFormat.NARRATIVE_FILM}:
            return PlanningMode.CINEMATIC_3D
        if product.format is MediaFormat.DOCUMENTARY:
            return PlanningMode.EVIDENCE_DOCUMENTARY
        if product.format is MediaFormat.TUTORIAL:
            return PlanningMode.SCREEN_DEMO
        if product.format in {MediaFormat.EXPLAINER, MediaFormat.DATA_VISUALIZATION}:
            return PlanningMode.MOTION_EXPLAINER
        if product.format is MediaFormat.COMMERCIAL:
            return PlanningMode.PRODUCT_HYBRID
        if product.format in {MediaFormat.PODCAST, MediaFormat.INTERVIEW}:
            return PlanningMode.TALK_FORMAT
        if product.format is MediaFormat.MUSIC_VIDEO:
            return PlanningMode.MUSIC_VISUAL
        return PlanningMode.HYBRID_GENERATIVE

    def _capabilities(
        self,
        product: MediaProductSpec,
        mode: PlanningMode,
    ) -> tuple[list[CapabilityKind], list[CapabilityKind]]:
        if mode is PlanningMode.AUTHENTIC_GAMEPLAY:
            return (
                [CapabilityKind.GAME_RUNTIME, CapabilityKind.EDITORIAL],
                [CapabilityKind.SPEECH, CapabilityKind.MOTION_GRAPHICS],
            )
        if mode is PlanningMode.CINEMATIC_3D:
            return (
                [CapabilityKind.OFFLINE_3D, CapabilityKind.EDITORIAL],
                [CapabilityKind.AI_IMAGE, CapabilityKind.COMPOSITING, CapabilityKind.COLOR],
            )
        if mode is PlanningMode.EVIDENCE_DOCUMENTARY:
            return (
                [CapabilityKind.FOOTAGE, CapabilityKind.SPEECH, CapabilityKind.EDITORIAL],
                [CapabilityKind.MOTION_GRAPHICS, CapabilityKind.AI_IMAGE, CapabilityKind.COLOR],
            )
        if mode is PlanningMode.SCREEN_DEMO:
            return (
                [CapabilityKind.SCREEN_CAPTURE, CapabilityKind.SPEECH, CapabilityKind.EDITORIAL],
                [CapabilityKind.MOTION_GRAPHICS, CapabilityKind.IMAGE_EDIT],
            )
        if mode is PlanningMode.MOTION_EXPLAINER:
            return (
                [CapabilityKind.SPEECH, CapabilityKind.MOTION_GRAPHICS, CapabilityKind.EDITORIAL],
                [CapabilityKind.AI_IMAGE, CapabilityKind.COMPOSITING, CapabilityKind.COLOR],
            )
        if mode is PlanningMode.PRODUCT_HYBRID:
            return (
                [CapabilityKind.OFFLINE_3D, CapabilityKind.MOTION_GRAPHICS, CapabilityKind.EDITORIAL],
                [CapabilityKind.IMAGE_EDIT, CapabilityKind.DESIGN, CapabilityKind.COLOR],
            )
        if mode is PlanningMode.TALK_FORMAT:
            return (
                [CapabilityKind.SPEECH, CapabilityKind.EDITORIAL],
                [CapabilityKind.MOTION_GRAPHICS, CapabilityKind.DESIGN],
            )
        if mode is PlanningMode.MUSIC_VISUAL:
            return (
                [CapabilityKind.MUSIC, CapabilityKind.AI_VIDEO, CapabilityKind.EDITORIAL],
                [CapabilityKind.COMPOSITING, CapabilityKind.COLOR],
            )
        return (
            [CapabilityKind.AI_VIDEO, CapabilityKind.EDITORIAL],
            [CapabilityKind.AI_IMAGE, CapabilityKind.MOTION_GRAPHICS, CapabilityKind.COLOR],
        )

    @staticmethod
    def _patterns_from_item(
        item: PlanningInputRef,
    ) -> list[ReferencePattern]:
        patterns: list[ReferencePattern] = []
        for key in PlanningDepartment._ABSTRACT_KEYS:
            raw = item.metadata.get(key)
            values = raw if isinstance(raw, list) else [raw] if isinstance(raw, str) else []
            for value in values:
                if not isinstance(value, str) or not value.strip():
                    continue
                patterns.append(
                    ReferencePattern(
                        source_id=item.input_id,
                        source_kind=item.kind.value,
                        category=key,
                        abstraction=value.strip(),
                        confidence=float(
                            item.metadata.get("confidence", 0.65)
                        ),
                        support_count=1,
                        sample_count=1,
                        evidence_status="USER_SUPPLIED_HYPOTHESIS",
                    )
                )
        return patterns

    @staticmethod
    def _capability_signals(
        patterns: list[ReferencePattern],
    ) -> list[CapabilityKind]:
        keyword_map: list[tuple[CapabilityKind, tuple[str, ...]]] = [
            (
                CapabilityKind.GAME_RUNTIME,
                (
                    "real gameplay",
                    "gameplay capture",
                    "in-game footage",
                    "game runtime",
                    "playthrough",
                    "walkthrough",
                ),
            ),
            (
                CapabilityKind.OFFLINE_3D,
                (
                    "3d animation",
                    "character animation",
                    "rigged character",
                    "blender",
                    "cinematic 3d",
                ),
            ),
            (
                CapabilityKind.AI_VIDEO,
                (
                    "generative video",
                    "ai video",
                    "image-to-video",
                    "image to video",
                    "text-to-video",
                    "text to video",
                ),
            ),
            (
                CapabilityKind.MOTION_GRAPHICS,
                (
                    "motion graphics",
                    "kinetic text",
                    "animated chart",
                    "infographic",
                    "data visualization",
                ),
            ),
            (
                CapabilityKind.SCREEN_CAPTURE,
                (
                    "screen recording",
                    "screen capture",
                    "screen demo",
                    "desktop demo",
                ),
            ),
            (
                CapabilityKind.FOOTAGE,
                (
                    "stock footage",
                    "b-roll",
                    "b roll",
                    "archive footage",
                    "live action",
                ),
            ),
            (
                CapabilityKind.COMPOSITING,
                (
                    "compositing",
                    "vfx",
                    "visual effects",
                ),
            ),
            (
                CapabilityKind.IMAGE_EDIT,
                (
                    "photoshop",
                    "thumbnail",
                    "image edit",
                ),
            ),
        ]
        found: list[CapabilityKind] = []
        for pattern in patterns:
            text = pattern.abstraction.lower()
            for kind, keywords in keyword_map:
                if any(keyword in text for keyword in keywords):
                    if kind not in found:
                        found.append(kind)
        return found

    @staticmethod
    def _patterns_from_competitors(
        competitors: Any,
    ) -> list[ReferencePattern]:
        if not isinstance(competitors, list):
            return []
        out: list[ReferencePattern] = []
        for index, profile in enumerate(competitors):
            if not isinstance(profile, dict):
                continue
            source_id = str(
                profile.get("profile_id")
                or profile.get("channel_id")
                or profile.get("video_id")
                or f"COMP_{index + 1:03d}"
            )
            for key in PlanningDepartment._ABSTRACT_KEYS:
                raw = profile.get(key)
                values = raw if isinstance(raw, list) else [raw] if isinstance(raw, str) else []
                for value in values:
                    if isinstance(value, str) and value.strip():
                        out.append(
                            ReferencePattern(
                                source_id=source_id,
                                source_kind="COMPETITOR_RESEARCH",
                                category=key,
                                abstraction=value.strip(),
                                confidence=float(
                                    profile.get("confidence", 0.65)
                                ),
                                support_count=1,
                                sample_count=max(
                                    1,
                                    int(profile.get("sample_count", 1)),
                                ),
                                evidence_status="HYPOTHESIS",
                            )
                        )
        return out

    @staticmethod
    def _patterns_from_portfolio(
        research_portfolio: Any,
    ) -> tuple[list[ReferencePattern], list[dict[str, Any]], bool]:
        if isinstance(research_portfolio, BaseModel):
            payload = research_portfolio.model_dump(mode="json")
        elif isinstance(research_portfolio, dict):
            payload = research_portfolio
        else:
            return [], [], False

        patterns: list[ReferencePattern] = []
        for raw in payload.get("confirmed_patterns") or []:
            if not isinstance(raw, dict):
                continue
            abstraction = str(raw.get("abstraction") or "").strip()
            if not abstraction:
                continue
            support_count = int(raw.get("support_count") or 0)
            sample_count = max(1, int(raw.get("sample_count") or 1))
            tier = str(raw.get("tier") or "CHANNEL_CONFIRMED")
            patterns.append(
                ReferencePattern(
                    source_id=str(raw.get("pattern_id") or "PORTFOLIO_PATTERN"),
                    source_kind="RESEARCH_PORTFOLIO",
                    category=str(
                        raw.get("observation_kind")
                        or "pattern"
                    ).lower(),
                    abstraction=abstraction,
                    confidence=float(raw.get("confidence") or 0.0),
                    support_count=support_count,
                    sample_count=sample_count,
                    evidence_status=tier,
                )
            )
        branches = [
            dict(item)
            for item in (payload.get("style_branches") or [])
            if isinstance(item, dict)
        ]
        decision_ready = bool(payload.get("decision_ready", False))
        return patterns, branches, decision_ready

    @staticmethod
    def _patterns_from_playbook(
        niche_playbook: Any,
    ) -> list[ReferencePattern]:
        if isinstance(niche_playbook, BaseModel):
            payload = niche_playbook.model_dump(mode="json")
        elif isinstance(niche_playbook, dict):
            payload = niche_playbook
        else:
            return []
        out: list[ReferencePattern] = []
        for index, raw in enumerate(payload.get("patterns") or []):
            if not isinstance(raw, dict):
                continue
            abstraction = str(raw.get("abstraction") or "").strip()
            if not abstraction:
                continue
            support_count = int(raw.get("support_count") or 0)
            sample_count = max(
                1,
                int(raw.get("sample_count") or 1),
            )
            ratio = support_count / sample_count
            confidence = float(raw.get("confidence") or 0.0)
            confirmed = (
                support_count >= 2
                and ratio >= 0.4
                and confidence >= 0.30
            )
            out.append(
                ReferencePattern(
                    source_id=str(
                        raw.get("pattern_id")
                        or f"PATTERN_{index + 1:03d}"
                    ),
                    source_kind="NICHE_PATTERN",
                    category=str(
                        raw.get("observation_kind")
                        or "pattern"
                    ).lower(),
                    abstraction=abstraction,
                    confidence=confidence,
                    support_count=support_count,
                    sample_count=sample_count,
                    evidence_status=(
                        "CONFIRMED_PATTERN"
                        if confirmed
                        else "WEAK_PATTERN"
                    ),
                )
            )
        return out

    def compile(
        self,
        *,
        project: StudioProjectSpec,
        product: MediaProductSpec,
        research_pack: dict[str, Any] | None = None,
        competitor_profiles: Any = None,
        niche_playbook: Any = None,
        research_confidence: Any = None,
        research_portfolio: Any = None,
        script_source_pack: Any = None,
    ) -> ProductionStrategy:
        mode = self._mode(product)
        primary, secondary = self._capabilities(product, mode)
        script_mode = "PROMPT_FALLBACK"
        script_policy = "LOCK"
        script_locked = False
        script_profile: dict[str, Any] = {}
        script_required_capabilities: list[CapabilityKind] = []
        script_reference_patterns: list[ReferencePattern] = []
        if script_source_pack is not None:
            if isinstance(script_source_pack, BaseModel):
                script_pack = script_source_pack.model_dump(mode="json")
            elif isinstance(script_source_pack, dict):
                script_pack = script_source_pack
            else:
                script_pack = {}
            script_mode = str(
                script_pack.get("mode") or "PROMPT_FALLBACK"
            )
            script_policy = str(
                script_pack.get("revision_policy") or "LOCK"
            )
            script_locked = (
                script_mode == "LOCKED_SCRIPT"
                and script_policy == "LOCK"
            )
            raw_profile = script_pack.get("production_profile")
            if isinstance(raw_profile, dict):
                script_profile = dict(raw_profile)
                if raw_profile.get("dialogue_present"):
                    script_required_capabilities.append(
                        CapabilityKind.SPEECH
                    )
                    if product.format is MediaFormat.ANIMATION:
                        script_required_capabilities.append(
                            CapabilityKind.LIPSYNC
                        )
                for kind in script_required_capabilities:
                    if kind not in secondary and kind not in primary:
                        secondary.append(kind)
            for index, value in enumerate(
                script_pack.get("reference_script_patterns", [])
            ):
                if not isinstance(value, str) or not value.strip():
                    continue
                script_reference_patterns.append(
                    ReferencePattern(
                        source_id=f"REFERENCE_SCRIPT_{index + 1:02d}",
                        source_kind="REFERENCE_SCRIPT",
                        category="script_structure_pattern",
                        abstraction=value.strip(),
                        confidence=0.72,
                        evidence_status="USER_SUPPLIED_HYPOTHESIS",
                    )
                )
        hypothesis_patterns: list[ReferencePattern] = []
        for item in project.planning_inputs:
            hypothesis_patterns.extend(
                self._patterns_from_item(item)
            )
        hypothesis_patterns.extend(
            self._patterns_from_competitors(
                competitor_profiles
            )
        )
        hypothesis_patterns.extend(script_reference_patterns)
        playbook_patterns = self._patterns_from_playbook(
            niche_playbook
        )
        (
            portfolio_patterns,
            research_style_branches,
            portfolio_decision_ready,
        ) = self._patterns_from_portfolio(
            research_portfolio
        )
        confirmed_patterns = (
            portfolio_patterns
            if portfolio_patterns
            else [
                item
                for item in playbook_patterns
                if item.evidence_status == "CONFIRMED_PATTERN"
            ]
        )

        # Deduplicate while preferring confirmed multi-video evidence over a
        # single-source hypothesis for the same abstraction.
        deduped_map: dict[
            tuple[str, str],
            ReferencePattern,
        ] = {}
        for item in [
            *hypothesis_patterns,
            *playbook_patterns,
            *portfolio_patterns,
        ]:
            key = (
                item.category.lower(),
                item.abstraction.lower(),
            )
            current = deduped_map.get(key)
            if current is None:
                deduped_map[key] = item
                continue
            rank = {
                "CROSS_CHANNEL_CONFIRMED": 5,
                "CHANNEL_CONFIRMED": 4,
                "CONFIRMED_PATTERN": 3,
                "WEAK_PATTERN": 2,
                "USER_SUPPLIED_HYPOTHESIS": 1,
                "HYPOTHESIS": 0,
            }
            if rank.get(
                item.evidence_status,
                0,
            ) > rank.get(
                current.evidence_status,
                0,
            ):
                deduped_map[key] = item
        deduped = [
            deduped_map[key]
            for key in sorted(deduped_map)
        ]

        weights = {
            "quality": 0.48,
            "speed": 0.18,
            "determinism": 0.22,
            "availability": 0.12,
        }
        if project.autonomous:
            weights["speed"] = 0.22
            weights["availability"] = 0.16
            weights["quality"] = 0.42
            weights["determinism"] = 0.20
        if mode in {PlanningMode.CINEMATIC_3D, PlanningMode.PRODUCT_HYBRID}:
            weights["quality"] += 0.08
            weights["speed"] -= 0.04
            weights["availability"] -= 0.04

        retention = [
            "open with a clear audience question, promise, conflict or surprising state",
            "each segment must add new information, escalation or emotional change",
            "protect setup/payoff and reaction beats rather than cutting only for speed",
            "remove dead time that does not improve comprehension, tension, emotion or atmosphere",
        ]
        if mode is PlanningMode.AUTHENTIC_GAMEPLAY:
            retention.append("gameplay events must be authentic runtime events, not simulated replacements")
        if mode is PlanningMode.EVIDENCE_DOCUMENTARY:
            retention.append("visual novelty must never outrun factual evidence or source certainty")

        observed_signals = self._capability_signals(
            confirmed_patterns
        )
        hypothesis_signals = self._capability_signals(
            hypothesis_patterns
        )
        for kind in observed_signals:
            if kind not in primary and kind not in secondary:
                secondary.append(kind)

        confidence_payload: dict[str, Any] = {}
        if isinstance(research_confidence, BaseModel):
            confidence_payload = research_confidence.model_dump(
                mode="json"
            )
        elif isinstance(research_confidence, dict):
            confidence_payload = research_confidence
        elif isinstance(research_pack, dict):
            candidate = research_pack.get(
                "research_confidence",
                {},
            )
            if isinstance(candidate, dict):
                confidence_payload = candidate
        confidence_score = float(
            confidence_payload.get("score", 0.0) or 0.0
        )
        confidence_grade = str(
            confidence_payload.get("grade", "LOW")
        )
        decision_ready = bool(
            confidence_payload.get(
                "decision_ready",
                False,
            )
        )
        if research_portfolio is not None:
            decision_ready = bool(
                decision_ready
                and portfolio_decision_ready
            )

        script_rules: list[str] = []
        if script_profile:
            script_rules.extend(
                str(item)
                for item in script_profile.get(
                    "planning_signals",
                    [],
                )
                if isinstance(item, str) and item.strip()
            )
            if script_profile.get("performance_load", 0.0) >= 0.65:
                script_rules.append(
                    "high script performance load; preserve reaction timing, eyelines and acting continuity before optimizing render speed"
                )
            if script_profile.get("continuity_load", 0.0) >= 0.65:
                script_rules.append(
                    "high script continuity load; lock scene state and asset identity across production handoffs"
                )

        originality = [
            "competitor material is evidence of patterns, not a source script",
            "do not reuse competitor dialogue, narration, story events or exact shot order",
            "do not reproduce competitor branding, thumbnails, character identity or music",
            "reuse only abstract format, pacing, production-method and audience-response patterns",
            "final script, visual design and scene construction must be independently generated",
        ]

        return ProductionStrategy(
            strategy_id=f"PLAN_{project.studio_project_id}",
            project_id=project.studio_project_id,
            planning_mode=mode,
            media_format=product.format,
            niche=project.niche or project.domain or str(product.constraints.get("domain", "generic")),
            platform=project.platform,
            script_source_mode=script_mode,
            script_revision_policy=script_policy,
            script_locked=script_locked,
            script_production_profile=script_profile,
            script_required_capabilities=list(
                dict.fromkeys(script_required_capabilities)
            ),
            input_ids=[item.input_id for item in project.planning_inputs],
            primary_capabilities=primary,
            secondary_capabilities=secondary,
            observed_capability_signals=observed_signals,
            hypothesis_capability_signals=hypothesis_signals,
            research_confidence_score=confidence_score,
            research_confidence_grade=confidence_grade,
            research_decision_ready=decision_ready,
            research_style_branches=research_style_branches,
            optimization_weights=weights,
            retention_principles=retention,
            reference_patterns=deduped,
            originality_boundaries=originality,
            production_rules=[
                "creative intent is chosen before software",
                "ideal tool and currently executable tool are tracked separately",
                "an unavailable ideal tool may be replaced only by an approved fallback that preserves intent",
                "authenticity-sensitive requirements such as real gameplay may not be silently substituted",
                "scene plans are locked before expensive production begins",
                (
                    "single-source observations remain hypotheses and "
                    "cannot independently change the production backend"
                ),
                (
                    "research-derived production-method routing requires "
                    "a confirmed multi-video pattern"
                ),
                (
                    "when research contains repeatable competing style "
                    "branches, choose the branch by scene objective rather "
                    "than averaging incompatible styles"
                ),
                *script_rules,
            ],
        )


class SceneToolPlanner:
    # A runtime adapter proves we can control a tool. A production binding proves
    # the current company departments can consume/produce the required artifact
    # with that tool. Selection requires both; ideal planning may still name a
    # not-yet-bound tool for future upgrades.
    PRODUCTION_BINDINGS: dict[str, set[CapabilityKind]] = {
        "blender": {CapabilityKind.OFFLINE_3D},
        "comfyui": {CapabilityKind.AI_IMAGE, CapabilityKind.AI_VIDEO},
        "ffmpeg": {CapabilityKind.EDITORIAL, CapabilityKind.QC},
    }
    RENDER_KINDS = {
        CapabilityKind.OFFLINE_3D,
        CapabilityKind.REALTIME_3D,
        CapabilityKind.GAME_RUNTIME,
        CapabilityKind.AI_VIDEO,
        CapabilityKind.SCREEN_CAPTURE,
        CapabilityKind.FOOTAGE,
        CapabilityKind.MOTION_GRAPHICS,
    }

    TOOL_PREFIXES = {
        "blender": "blender",
        "comfyui": "comfyui",
        "ffmpeg": "ffmpeg",
        "resolve": "resolve",
        "fusion": "resolve",
        "premiere": "premiere",
        "aftereffects": "aftereffects",
        "photoshop": "photoshop",
        "unreal": "unreal",
        "canva": "canva",
    }

    def __init__(self, kernel) -> None:
        self.kernel = kernel
        self._probe_cache: dict[str, tuple[bool, bool, bool]] = {}

    @classmethod
    def tool_id_for(cls, capability_id: str, provider: str) -> str | None:
        text = f"{capability_id} {provider}".lower().replace(" ", "")
        for token, tool_id in cls.TOOL_PREFIXES.items():
            if token in text:
                return tool_id
        return None

    def _tool_state(self, tool_id: str | None) -> tuple[bool, bool, bool]:
        # available, execution-mastered, production-qualified
        if tool_id is None:
            return False, False, False
        if tool_id in self._probe_cache:
            return self._probe_cache[tool_id]
        try:
            probe = self.kernel.tool_adapters.probe(self.kernel, tool_id)
            available = bool(probe.available)
        except Exception:
            available = False
        try:
            mastery = self.kernel.execution_mastery.get(tool_id)
            mastered = bool(mastery.passed and mastery.regression_passed)
        except KeyError:
            mastered = False
        try:
            decision = self.kernel.production_qualification.decision(tool_id)
            qualified = bool(decision.qualified)
        except KeyError:
            qualified = False
        self._probe_cache[tool_id] = (available, mastered, qualified)
        return self._probe_cache[tool_id]

    def _commercial_safe(self, offer, tool_id: str | None) -> bool:
        if offer.commercial_safe is True:
            return True
        _, _, qualified = self._tool_state(tool_id)
        return qualified

    def _capability_binding_ready(
        self,
        tool_id: str | None,
        kind: CapabilityKind,
    ) -> bool:
        if tool_id is None:
            return False
        if kind not in self.PRODUCTION_BINDINGS.get(tool_id, set()):
            return False
        if tool_id != "comfyui":
            return True

        # ComfyUI qualification is tool-level, but image/video production
        # requires an approved workflow+model for the requested modality.
        target_media = {
            CapabilityKind.AI_IMAGE: "image",
            CapabilityKind.AI_VIDEO: "video",
        }.get(kind)
        if target_media is None:
            return False
        root = getattr(self.kernel, "root", None)
        if root is None:
            return False
        try:
            from cinefactory.models.registry import ModelRegistry
            from cinefactory.workflows.registry import WorkflowRegistry

            workflows = WorkflowRegistry(root / "workflows").load()
            models = ModelRegistry(root / "models" / "registry.yaml").load()
            for manifest in workflows.list():
                if (
                    manifest.executor_id != "local.comfyui"
                    or manifest.media_type.lower() != target_media
                    or not manifest.local_only
                    or not manifest.model_revision
                ):
                    continue
                try:
                    models.require_approved(
                        manifest.model_id,
                        manifest.model_revision,
                    )
                except Exception:
                    continue
                return True
        except Exception:
            return False
        return False

    def _score(self, offer, strategy: ProductionStrategy, ready: bool) -> float:
        w = strategy.optimization_weights
        score = (
            w.get("quality", 0.48) * float(offer.quality)
            + w.get("speed", 0.18) * float(offer.speed)
            + w.get("determinism", 0.22) * float(offer.deterministic)
            + w.get("availability", 0.12) * (1.0 if ready else 0.0)
        )
        cid = offer.capability_id.lower()
        if strategy.planning_mode is PlanningMode.CINEMATIC_3D and "blender" in cid:
            score += 0.08
        if strategy.planning_mode is PlanningMode.AUTHENTIC_GAMEPLAY and "runtime" in cid:
            score += 0.10
        if strategy.planning_mode in {PlanningMode.HYBRID_GENERATIVE, PlanningMode.MUSIC_VISUAL} and "comfyui" in cid:
            score += 0.08
        if strategy.planning_mode is PlanningMode.MOTION_EXPLAINER and (
            "aftereffects" in cid or "fusion" in cid
        ):
            score += 0.08
        return round(score, 4)

    def assign(
        self,
        kind: CapabilityKind,
        strategy: ProductionStrategy,
        *,
        authenticity_sensitive: bool = False,
    ) -> CapabilityAssignment:
        offers = list(self.kernel.capabilities.list(kind))
        if not offers:
            return CapabilityAssignment(
                capability_kind=kind,
                blockers=[f"NO_REGISTERED_CAPABILITY:{kind.value}"],
            )

        ranked_ideal: list[tuple[float, Any, str | None, bool, bool]] = []
        ranked_selected: list[tuple[float, Any, str | None, bool, bool]] = []
        for offer in offers:
            tool_id = self.tool_id_for(offer.capability_id, offer.provider)
            available, mastered, _ = self._tool_state(tool_id)
            if tool_id is None:
                ready = bool(offer.executable)
            else:
                bound = self._capability_binding_ready(
                    tool_id,
                    kind,
                )
                ready = available and mastered and bound
            commercial = self._commercial_safe(offer, tool_id)
            ideal_score = self._score(offer, strategy, False)
            selected_score = self._score(offer, strategy, ready)
            ranked_ideal.append(
                (ideal_score, offer, tool_id, ready, commercial)
            )
            ranked_selected.append(
                (selected_score, offer, tool_id, ready, commercial)
            )

        ranked_ideal.sort(
            key=lambda row: (row[0], row[1].capability_id),
            reverse=True,
        )
        ranked_selected.sort(
            key=lambda row: (row[0], row[1].capability_id),
            reverse=True,
        )
        ideal = ranked_ideal[0]
        executable = [
            row for row in ranked_selected
            if row[3] and row[4]
        ]
        selected = executable[0] if executable else None
        blockers: list[str] = []
        reasons = [
            f"ideal={ideal[1].capability_id}",
            f"planning_mode={strategy.planning_mode.value}",
        ]
        ideal_tool = ideal[2]
        if (
            ideal_tool is not None
            and kind not in self.PRODUCTION_BINDINGS.get(ideal_tool, set())
        ):
            reasons.append(
                f"ideal_not_pipeline_bound={ideal_tool}:{kind.value}"
            )
        if selected is None:
            blockers.append(f"NO_VALIDATED_COMMERCIAL_RUNTIME:{kind.value}")
        elif selected[1].capability_id != ideal[1].capability_id:
            if authenticity_sensitive:
                blockers.append(
                    f"AUTHENTICITY_SENSITIVE_IDEAL_UNAVAILABLE:{ideal[1].capability_id}"
                )
            else:
                reasons.append(
                    f"fallback_selected={selected[1].capability_id}"
                )

        fallback_ids = [
            row[1].capability_id
            for row in executable[1:]
            if selected is not None
        ]
        return CapabilityAssignment(
            capability_kind=kind,
            ideal_capability_id=ideal[1].capability_id,
            selected_capability_id=selected[1].capability_id if selected else None,
            selected_tool_id=selected[2] if selected else None,
            fallback_capability_ids=fallback_ids,
            execution_ready=selected is not None and not blockers,
            commercial_safe=bool(selected and selected[4]),
            score=selected[0] if selected else ideal[0],
            reasons=reasons,
            blockers=blockers,
        )

    @staticmethod
    def _scene_text(scene_shots: list[Any]) -> str:
        parts: list[str] = []
        for shot in scene_shots:
            for value in (
                getattr(shot, "narrative_purpose", None),
                getattr(shot, "audience_endpoint", None),
                getattr(shot, "edit_intent", None),
            ):
                if value:
                    parts.append(str(value))
        return " ".join(parts).lower()

    def _renderer_candidates(
        self,
        *,
        strategy: ProductionStrategy,
        scene_shots: list[Any],
        base_kinds: list[CapabilityKind],
    ) -> list[CapabilityKind]:
        render_base = [
            kind
            for kind in base_kinds
            if kind in self.RENDER_KINDS
        ]
        if (
            CapabilityKind.GAME_RUNTIME in render_base
            or strategy.planning_mode
            is PlanningMode.AUTHENTIC_GAMEPLAY
        ):
            return [CapabilityKind.GAME_RUNTIME]

        candidates = list(dict.fromkeys(render_base))
        for kind in strategy.observed_capability_signals:
            if (
                kind in self.RENDER_KINDS
                and kind not in candidates
            ):
                candidates.append(kind)

        # Scene semantics can introduce a candidate production method even when
        # research has not yet promoted that method to a global strategy rule.
        # It remains only a candidate and still must pass execution/commercial
        # readiness before selection.
        scene_text = self._scene_text(scene_shots)
        semantic_candidates = [
            (
                CapabilityKind.AI_VIDEO,
                (
                    "dream",
                    "dreamlike",
                    "surreal",
                    "abstract montage",
                    "memory montage",
                    "vision",
                    "impossible transformation",
                    "fantasy transition",
                ),
            ),
            (
                CapabilityKind.MOTION_GRAPHICS,
                (
                    "chart",
                    "graph",
                    "infographic",
                    "kinetic text",
                    "data visualization",
                ),
            ),
            (
                CapabilityKind.SCREEN_CAPTURE,
                (
                    "screen demo",
                    "screen recording",
                    "desktop",
                    "software interface",
                    "ui walkthrough",
                ),
            ),
            (
                CapabilityKind.FOOTAGE,
                (
                    "b-roll",
                    "b roll",
                    "archive footage",
                    "live action",
                    "real-world footage",
                    "documentary footage",
                ),
            ),
        ]
        for kind, keywords in semantic_candidates:
            if (
                any(keyword in scene_text for keyword in keywords)
                and kind not in candidates
            ):
                candidates.append(kind)

        if (
            strategy.planning_mode is PlanningMode.CINEMATIC_3D
            and CapabilityKind.OFFLINE_3D not in candidates
        ):
            candidates.insert(0, CapabilityKind.OFFLINE_3D)
        return candidates

    def _scene_renderer_score(
        self,
        assignment: CapabilityAssignment,
        *,
        strategy: ProductionStrategy,
        scene_shots: list[Any],
    ) -> float:
        score = float(assignment.score)
        kind = assignment.capability_kind
        text = self._scene_text(scene_shots)

        if kind in strategy.observed_capability_signals:
            score += 0.08

        performance_heavy = any(
            bool(getattr(shot, "performance", {}))
            for shot in scene_shots
        )
        if (
            performance_heavy
            and kind
            in {
                CapabilityKind.OFFLINE_3D,
                CapabilityKind.REALTIME_3D,
            }
        ):
            score += 0.12

        if any(
            token in text
            for token in (
                "dream",
                "dreamlike",
                "memory",
                "vision",
                "surreal",
                "abstract",
                "montage",
                "transformation",
                "fantasy transition",
            )
        ):
            if kind is CapabilityKind.AI_VIDEO:
                score += 0.45
            elif kind is CapabilityKind.OFFLINE_3D:
                score -= 0.08

        if any(
            token in text
            for token in (
                "chart",
                "graph",
                "data",
                "infographic",
                "kinetic text",
            )
        ) and kind is CapabilityKind.MOTION_GRAPHICS:
            score += 0.35

        if any(
            token in text
            for token in (
                "screen",
                "desktop",
                "software",
                "interface",
                "click",
            )
        ) and kind is CapabilityKind.SCREEN_CAPTURE:
            score += 0.35

        if any(
            token in text
            for token in (
                "archive",
                "b-roll",
                "b roll",
                "real-world",
                "live action",
            )
        ) and kind is CapabilityKind.FOOTAGE:
            score += 0.30

        if (
            strategy.planning_mode
            is PlanningMode.AUTHENTIC_GAMEPLAY
            and kind is CapabilityKind.GAME_RUNTIME
        ):
            score += 1.0
        return round(score, 4)

    def _choose_scene_renderer(
        self,
        *,
        strategy: ProductionStrategy,
        scene_shots: list[Any],
        base_kinds: list[CapabilityKind],
        required_kind: CapabilityKind | None = None,
    ) -> tuple[
        CapabilityAssignment | None,
        list[CapabilityKind],
        list[str],
    ]:
        candidates = self._renderer_candidates(
            strategy=strategy,
            scene_shots=scene_shots,
            base_kinds=(
                [required_kind]
                if required_kind is not None
                else base_kinds
            ),
        )
        if required_kind is not None:
            candidates = [required_kind]
        if not candidates:
            return None, [], ["NO_RENDER_CAPABILITY_REQUIRED"]

        evaluated: list[
            tuple[float, CapabilityAssignment]
        ] = []
        for kind in candidates:
            assignment = self.assign(
                kind,
                strategy,
                authenticity_sensitive=(
                    kind is CapabilityKind.GAME_RUNTIME
                    and (
                        required_kind is CapabilityKind.GAME_RUNTIME
                        or strategy.planning_mode
                        is PlanningMode.AUTHENTIC_GAMEPLAY
                    )
                ),
            )
            scene_score = self._scene_renderer_score(
                assignment,
                strategy=strategy,
                scene_shots=scene_shots,
            )
            evaluated.append((scene_score, assignment))

        executable = [
            item
            for item in evaluated
            if item[1].execution_ready
        ]
        if executable:
            _, selected = max(
                executable,
                key=lambda item: (
                    item[0],
                    item[1].selected_capability_id or "",
                ),
            )
            selected = selected.model_copy(
                update={
                    "score": max(
                        score
                        for score, assignment in executable
                        if assignment is selected
                    ),
                    "reasons": [
                        *selected.reasons,
                        "scene_specific_renderer_selection",
                    ],
                }
            )
            return selected, candidates, []

        _, best = max(
            evaluated,
            key=lambda item: (
                item[0],
                item[1].ideal_capability_id or "",
            ),
        )
        return (
            best,
            candidates,
            list(best.blockers)
            or [
                "NO_EXECUTABLE_SCENE_RENDERER:"
                + ",".join(kind.value for kind in candidates)
            ],
        )

    def compile_handoff(
        self,
        *,
        project_id: str,
        strategy: ProductionStrategy,
        shots: list[Any],
        segment_capabilities: dict[str, list[CapabilityKind]] | None = None,
        scene_policies: dict[str, dict[str, Any]] | None = None,
    ) -> ProductionHandoff:
        by_scene: dict[str, list[Any]] = {}
        for shot in shots:
            by_scene.setdefault(str(shot.scene_id), []).append(shot)

        visual_primary = [
            item
            for item in strategy.primary_capabilities
            if item in self.RENDER_KINDS
        ]
        scene_plans: list[SceneProductionPlan] = []
        blockers: list[str] = []
        selected_tools: set[str] = set()
        previous_render_assignment: CapabilityAssignment | None = None

        for scene_id, scene_shots in by_scene.items():
            kinds = list(visual_primary)
            if segment_capabilities and scene_id in segment_capabilities:
                segment_render_kinds = [
                    item
                    for item in segment_capabilities[scene_id]
                    if item in self.RENDER_KINDS
                ]
                if segment_render_kinds:
                    kinds = segment_render_kinds

            scene_policy_record = (
                (scene_policies or {}).get(scene_id, {})
            )
            selected_policy = scene_policy_record.get(
                "selected_policy",
                {},
            )
            scene_metrics = scene_policy_record.get(
                "metrics",
                {},
            )
            scene_lane = scene_policy_record.get(
                "selected_lane"
            )
            production_objective = scene_policy_record.get(
                "production_objective"
            )
            required_raw = scene_policy_record.get(
                "required_capability_kind"
            )
            try:
                required_capability_kind = (
                    CapabilityKind(required_raw)
                    if required_raw is not None
                    else None
                )
            except ValueError:
                required_capability_kind = None
            preferred_capability_kinds: list[CapabilityKind] = []
            for raw_kind in scene_policy_record.get(
                "preferred_capability_kinds",
                [],
            ):
                try:
                    kind = CapabilityKind(raw_kind)
                except ValueError:
                    continue
                if kind not in preferred_capability_kinds:
                    preferred_capability_kinds.append(kind)
            optimization_bias = scene_policy_record.get(
                "optimization_bias",
                {},
            )
            if not isinstance(optimization_bias, dict):
                optimization_bias = {}
            has_scene_policy = bool(
                scene_policies is not None
                and scene_id in scene_policies
            )
            backend_switch_allowed = bool(
                scene_policy_record.get(
                    "backend_switch_allowed",
                    True if not has_scene_policy else False,
                )
            )
            scene_strategy = strategy
            if isinstance(selected_policy, dict) and selected_policy:
                scene_strategy = strategy.model_copy(
                    update={
                        "optimization_weights": dict(
                            selected_policy.get(
                                "optimization_weights",
                                strategy.optimization_weights,
                            )
                        ),
                        "conference_lane": (
                            str(scene_lane)
                            if scene_lane is not None
                            else strategy.conference_lane
                        ),
                        "conference_policy": dict(selected_policy),
                    },
                    deep=True,
                )
            if optimization_bias:
                weights = dict(scene_strategy.optimization_weights)
                for key, raw_delta in optimization_bias.items():
                    try:
                        delta = float(raw_delta)
                    except (TypeError, ValueError):
                        continue
                    weights[str(key)] = max(
                        0.0,
                        float(weights.get(str(key), 0.0)) + delta,
                    )
                total_weight = sum(weights.values())
                if total_weight > 0:
                    weights = {
                        key: round(value / total_weight, 6)
                        for key, value in weights.items()
                    }
                    scene_strategy = scene_strategy.model_copy(
                        update={"optimization_weights": weights},
                        deep=True,
                    )

            scene_render_kinds = list(
                dict.fromkeys(
                    [*kinds, *preferred_capability_kinds]
                )
            )
            (
                render_assignment,
                render_candidates,
                render_blockers,
            ) = self._choose_scene_renderer(
                strategy=scene_strategy,
                scene_shots=scene_shots,
                base_kinds=scene_render_kinds,
                required_kind=required_capability_kind,
            )

            continuity_override = False
            if (
                previous_render_assignment is not None
                and render_assignment is not None
                and render_assignment.execution_ready
                and previous_render_assignment.execution_ready
                and render_assignment.capability_kind
                is not previous_render_assignment.capability_kind
                and not backend_switch_allowed
                and previous_render_assignment.capability_kind
                in render_candidates
            ):
                pinned = self.assign(
                    previous_render_assignment.capability_kind,
                    scene_strategy,
                    authenticity_sensitive=(
                        previous_render_assignment.capability_kind
                        is CapabilityKind.GAME_RUNTIME
                        and scene_strategy.planning_mode
                        is PlanningMode.AUTHENTIC_GAMEPLAY
                    ),
                )
                if pinned.execution_ready:
                    render_assignment = pinned.model_copy(
                        update={
                            "reasons": [
                                *pinned.reasons,
                                (
                                    "continuity_gate_preserved_previous_"
                                    "renderer_class"
                                ),
                            ]
                        }
                    )
                    continuity_override = True
            blockers.extend(
                f"{scene_id}:{item}"
                for item in render_blockers
            )
            assignments = (
                [render_assignment]
                if render_assignment is not None
                else []
            )
            if (
                render_assignment is not None
                and render_assignment.selected_tool_id
            ):
                selected_tools.add(
                    render_assignment.selected_tool_id
                )
            if (
                render_assignment is not None
                and render_assignment.execution_ready
            ):
                previous_render_assignment = render_assignment

            notes = [
                (
                    "all shots in a continuity scene use the same primary "
                    "renderer unless a locked transition justifies a change"
                ),
                (
                    "renderer choice considered prompt/format, abstract "
                    "research signals, scene semantics and runtime readiness"
                ),
            ]
            if scene_lane is not None:
                notes.append(
                    "scene_conference_lane=" + str(scene_lane)
                )
            if production_objective is not None:
                notes.append(
                    "scene_production_objective="
                    + str(production_objective)
                )
            if required_capability_kind is not None:
                notes.append(
                    "required_capability="
                    + required_capability_kind.value
                )
            if backend_switch_allowed:
                notes.append(
                    "scene_conference_allows_renderer_class_switch"
                )
            if continuity_override:
                notes.append(
                    "continuity gate overrode renderer-class change"
                )
            if len(render_candidates) > 1:
                notes.append(
                    "renderer_candidates="
                    + ",".join(
                        item.value
                        for item in render_candidates
                    )
                )
            scene_plans.append(
                SceneProductionPlan(
                    scene_id=scene_id,
                    shot_ids=[
                        str(shot.shot_id)
                        for shot in scene_shots
                    ],
                    purpose=str(
                        scene_shots[0].narrative_purpose
                    ),
                    render_candidate_kinds=render_candidates,
                    render_assignment=render_assignment,
                    assignments=assignments,
                    scene_conference_lane=(
                        str(scene_lane)
                        if scene_lane is not None
                        else None
                    ),
                    scene_conference_policy=(
                        dict(selected_policy)
                        if isinstance(selected_policy, dict)
                        else {}
                    ),
                    scene_conference_metrics=(
                        dict(scene_metrics)
                        if isinstance(scene_metrics, dict)
                        else {}
                    ),
                    scene_production_objective=(
                        str(production_objective)
                        if production_objective is not None
                        else None
                    ),
                    required_capability_kind=required_capability_kind,
                    preferred_capability_kinds=preferred_capability_kinds,
                    optimization_bias={
                        str(key): float(value)
                        for key, value in optimization_bias.items()
                        if isinstance(value, (int, float))
                    },
                    backend_switch_allowed=backend_switch_allowed,
                    continuity_priority=not backend_switch_allowed,
                    quality_target=(
                        str(scene_lane).lower()
                        if scene_lane is not None
                        else "production"
                    ),
                    notes=notes,
                )
            )

        global_kinds = [
            item for item in strategy.primary_capabilities + strategy.secondary_capabilities
            if item in {
                CapabilityKind.EDITORIAL,
                CapabilityKind.COLOR,
                CapabilityKind.COMPOSITING,
                CapabilityKind.MOTION_GRAPHICS,
                CapabilityKind.IMAGE_EDIT,
                CapabilityKind.DESIGN,
            }
        ]
        global_assignments = [
            self.assign(kind, strategy)
            for kind in dict.fromkeys(global_kinds)
        ]
        for assignment in global_assignments:
            # Secondary finishing capabilities are optional; primary ones must be ready.
            if assignment.capability_kind in strategy.primary_capabilities:
                blockers.extend(
                    f"GLOBAL:{item}" for item in assignment.blockers
                )
            if assignment.selected_tool_id:
                selected_tools.add(assignment.selected_tool_id)

        return ProductionHandoff(
            project_id=project_id,
            strategy_id=strategy.strategy_id,
            planning_mode=strategy.planning_mode,
            scene_plans=scene_plans,
            global_assignments=global_assignments,
            selected_tool_ids=sorted(selected_tools),
            executable=not blockers,
            blockers=blockers,
            fallback_policy=[
                "retry the selected backend only for transient failures",
                "use listed fallback only when it preserves the locked creative intent",
                "do not replace real gameplay with offline 3D or AI-generated imitation",
                "route repeated failures back to TECHNICAL_DIRECTION for replanning",
            ],
        )
