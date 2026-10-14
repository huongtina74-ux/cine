from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from .capabilities import CapabilityRegistry
from .contracts import (
    CapabilityRequirement,
    MediaProductSpec,
    MediaSegment,
    RoutingDecision,
    PlanningInputKind,
    StudioProjectSpec,
)
from .format_director import FormatDirector, UniversalMediaClassifier


class SegmentExecutionPlan(BaseModel):
    segment: MediaSegment
    routes: list[RoutingDecision] = Field(default_factory=list)
    executable: bool = False
    blockers: list[str] = Field(default_factory=list)


class StudioPlan(BaseModel):
    project: StudioProjectSpec
    product: MediaProductSpec
    segments: list[SegmentExecutionPlan]
    executable: bool
    blockers: list[str] = Field(default_factory=list)


class StudioControlPlane:
    """Universal planning layer above the legacy story-first Autopilot."""

    def __init__(
        self,
        *,
        classifier: UniversalMediaClassifier | None = None,
        director: FormatDirector | None = None,
        capabilities: CapabilityRegistry | None = None,
        max_vram_gb: float = 12.0,
    ) -> None:
        self.classifier = classifier or UniversalMediaClassifier()
        self.director = director or FormatDirector()
        self.capabilities = capabilities or CapabilityRegistry()
        self.max_vram_gb = max_vram_gb

    @staticmethod
    def _owned_script_signal(project: StudioProjectSpec) -> str:
        parts: list[str] = [project.prompt]
        max_chars = 24000
        used = len(project.prompt)
        for item in project.planning_inputs:
            if item.kind not in {
                PlanningInputKind.SCRIPT,
                PlanningInputKind.SCRIPT_OUTLINE,
            }:
                continue
            for key in ("media_format", "format_hint", "domain"):
                value = item.metadata.get(key)
                if isinstance(value, str) and value.strip():
                    parts.append(value.strip())
                    used += len(value)
            content = (item.content or "").strip()
            if not content:
                content = str(
                    item.metadata.get("content") or ""
                ).strip()
            if (
                not content
                and item.uri
                and not item.uri.startswith(("http://", "https://"))
            ):
                uri = item.uri[7:] if item.uri.startswith("file://") else item.uri
                path = Path(uri).expanduser()
                try:
                    if path.is_file() and path.suffix.lower() in {
                        ".txt",
                        ".md",
                        ".markdown",
                        ".fountain",
                        ".json",
                    }:
                        content = path.read_text(
                            encoding="utf-8-sig",
                            errors="ignore",
                        ).lstrip("\ufeff")
                except OSError:
                    content = ""
            if content and used < max_chars:
                remaining = max_chars - used
                parts.append(content[:remaining])
                used += min(len(content), remaining)
        return "\n".join(parts)

    def plan(self, project: StudioProjectSpec) -> StudioPlan:
        classification_text = self._owned_script_signal(project)
        product = self.classifier.classify(classification_text)
        segments = self.director.compile(product, duration_seconds=project.duration_seconds)
        execution: list[SegmentExecutionPlan] = []
        global_blockers: list[str] = []

        for segment in segments:
            routes: list[RoutingDecision] = []
            blockers: list[str] = []
            for kind in segment.capability_requirements:
                requirement = CapabilityRequirement(
                    kind=kind,
                    local_only=True,
                    commercial_safe=True,
                    max_vram_gb=self.max_vram_gb,
                    required_tags={"actual_gameplay"} if (
                        product.actual_gameplay_required and kind.value == "GAME_RUNTIME"
                    ) else set(),
                )
                decision = self.capabilities.route(requirement)
                routes.append(decision)
                if not decision.executable:
                    blockers.append(
                        f"{segment.segment_id}:{kind.value}:NO_APPROVED_EXECUTABLE_CAPABILITY"
                    )

            if product.evidence_required and not segment.creative_intent.get("evidence_ready", False):
                # Planning is allowed, execution waits for Evidence Department to lock an EvidenceMap.
                blockers.append(f"{segment.segment_id}:EVIDENCE_MAP_REQUIRED")

            item = SegmentExecutionPlan(
                segment=segment,
                routes=routes,
                executable=not blockers,
                blockers=blockers,
            )
            execution.append(item)
            global_blockers.extend(blockers)

        return StudioPlan(
            project=project,
            product=product,
            segments=execution,
            executable=not global_blockers,
            blockers=global_blockers,
        )
