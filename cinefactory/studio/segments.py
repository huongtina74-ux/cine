from __future__ import annotations

from collections import defaultdict, deque
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from cinefactory.studio.contracts import CapabilityKind, SegmentKind


class SegmentRequirement(BaseModel):
    capability: CapabilityKind
    required: bool = True
    deterministic: bool | None = None
    local_only: bool = False
    commercial_safe: bool = True
    min_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    max_vram_gb: float | None = Field(default=None, gt=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MediaSegment(BaseModel):
    segment_id: str = Field(default_factory=lambda: f"SEG_{uuid4().hex[:10]}")
    kind: SegmentKind
    purpose: str = Field(min_length=3)
    duration_seconds: float | None = Field(default=None, gt=0)
    dependencies: list[str] = Field(default_factory=list)
    requirements: list[SegmentRequirement] = Field(default_factory=list)
    input_artifact_ids: list[str] = Field(default_factory=list)
    persistent_entity_ids: list[str] = Field(default_factory=list)
    creative_intent: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

class SegmentGraph(BaseModel):
    segments: list[MediaSegment] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_graph(self) -> "SegmentGraph":
        ids = [segment.segment_id for segment in self.segments]
        if len(ids) != len(set(ids)):
            raise ValueError("segment_id values must be unique")
        known = set(ids)
        for segment in self.segments:
            missing = set(segment.dependencies) - known
            if missing:
                raise ValueError(f"unknown segment dependencies: {sorted(missing)}")
            if segment.segment_id in segment.dependencies:
                raise ValueError("segment cannot depend on itself")
        if self._has_cycle():
            raise ValueError("segment graph contains a cycle")
        return self

    def _has_cycle(self) -> bool:
        children: dict[str, list[str]] = defaultdict(list)
        indegree = {segment.segment_id: 0 for segment in self.segments}
        for segment in self.segments:
            for parent in segment.dependencies:
                children[parent].append(segment.segment_id)
                indegree[segment.segment_id] += 1
        queue = deque([key for key, value in indegree.items() if value == 0])
        visited = 0
        while queue:
            node = queue.popleft()
            visited += 1
            for child in children[node]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        return visited != len(indegree)

    def topological_order(self) -> list[str]:
        children: dict[str, list[str]] = defaultdict(list)
        indegree = {segment.segment_id: 0 for segment in self.segments}
        for segment in self.segments:
            for parent in segment.dependencies:
                children[parent].append(segment.segment_id)
                indegree[segment.segment_id] += 1
        queue = deque(sorted(key for key, value in indegree.items() if value == 0))
        order: list[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for child in sorted(children[node]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        if len(order) != len(self.segments):
            raise ValueError("segment graph contains a cycle")
        return order


class SegmentExecutionPlan(BaseModel):
    segment_id: str
    capability: CapabilityKind
    provider_id: str
    executable: bool
    reason: str
    fallback_provider_ids: list[str] = Field(default_factory=list)


class ProductionRecipe(BaseModel):
    project_id: str
    graph: SegmentGraph
    execution: list[SegmentExecutionPlan] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
