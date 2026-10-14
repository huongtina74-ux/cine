from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .contracts import CapabilityKind, MediaSegment, RoutingDecision


class ProductionTask(BaseModel):
    task_id: str
    segment_id: str
    task_type: str
    dependencies: list[str] = Field(default_factory=list)
    capability_kind: CapabilityKind
    capability_id: str | None = None
    executable: bool = False
    resource_class: str = "CPU"
    retry_limit: int = Field(default=2, ge=0, le=10)
    payload: dict[str, Any] = Field(default_factory=dict)


class ProductionRecipe(BaseModel):
    project_id: str
    tasks: list[ProductionTask]
    blocked: bool = False
    blockers: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def task_ids_unique(self) -> "ProductionRecipe":
        ids = [x.task_id for x in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("ProductionRecipe task_id values must be unique")
        return self


class SegmentDAG:
    def __init__(self, tasks: list[ProductionTask]) -> None:
        self.tasks = {t.task_id: t for t in tasks}
        self.children: dict[str, set[str]] = defaultdict(set)
        self.indegree: dict[str, int] = {x: 0 for x in self.tasks}
        for task in tasks:
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise KeyError(f"unknown dependency: {dep}")
                self.children[dep].add(task.task_id)
                self.indegree[task.task_id] += 1

    def topological_order(self) -> list[str]:
        indegree = dict(self.indegree)
        queue = deque(sorted([k for k, v in indegree.items() if v == 0]))
        order: list[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for child in sorted(self.children.get(node, ())):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
        if len(order) != len(self.tasks):
            raise ValueError("SEGMENT_DAG_CYCLE")
        return order
class ProductionCompiler:
    RESOURCE_MAP: dict[CapabilityKind, str] = {
        CapabilityKind.OFFLINE_3D: "GPU",
        CapabilityKind.REALTIME_3D: "GPU",
        CapabilityKind.GAME_RUNTIME: "GPU",
        CapabilityKind.AI_IMAGE: "GPU",
        CapabilityKind.AI_VIDEO: "GPU",
        CapabilityKind.MOTION_GRAPHICS: "GPU",
        CapabilityKind.COMPOSITING: "GPU",
        CapabilityKind.EDITORIAL: "IO",
        CapabilityKind.SPEECH: "CPU",
        CapabilityKind.MUSIC: "GPU",
        CapabilityKind.SFX: "CPU",
        CapabilityKind.SCREEN_CAPTURE: "IO",
        CapabilityKind.FOOTAGE: "IO",
        CapabilityKind.COLOR: "GPU",
        CapabilityKind.QC: "CPU",
    }

    def compile(
        self,
        project_id: str,
        segments: list[MediaSegment],
        route_map: dict[str, list[RoutingDecision]],
    ) -> ProductionRecipe:
        tasks: list[ProductionTask] = []
        blockers: list[str] = []
        segment_last_task: dict[str, str] = {}

        for segment in sorted(segments, key=lambda x: x.order):
            prior_task_ids = [segment_last_task[x] for x in segment.dependencies if x in segment_last_task]
            previous_for_segment = list(prior_task_ids)
            routes = route_map.get(segment.segment_id, [])
            by_kind = {r.requirement.kind: r for r in routes}

            if not segment.capability_requirements:
                task_id = f"{segment.segment_id}.NOOP"
                tasks.append(
                    ProductionTask(
                        task_id=task_id,
                        segment_id=segment.segment_id,
                        task_type="NOOP",
                        dependencies=previous_for_segment,
                        capability_kind=CapabilityKind.QC,
                        executable=True,
                    )
                )
                segment_last_task[segment.segment_id] = task_id
                continue
            for idx, kind in enumerate(segment.capability_requirements):
                decision = by_kind.get(kind)
                task_id = f"{segment.segment_id}.{idx + 1:02d}.{kind.value}"
                executable = bool(decision and decision.executable and decision.selected_capability_id)
                if not executable:
                    blockers.append(f"{task_id}:BLOCKED_CAPABILITY")
                task = ProductionTask(
                    task_id=task_id,
                    segment_id=segment.segment_id,
                    task_type=kind.value,
                    dependencies=list(previous_for_segment),
                    capability_kind=kind,
                    capability_id=decision.selected_capability_id if decision else None,
                    executable=executable,
                    resource_class=self.RESOURCE_MAP.get(kind, "CPU"),
                    payload={
                        "purpose": segment.purpose,
                        "creative_intent": segment.creative_intent,
                        "execution_constraints": segment.execution_constraints,
                    },
                )
                tasks.append(task)
                previous_for_segment = [task_id]
                segment_last_task[segment.segment_id] = task_id

        recipe = ProductionRecipe(
            project_id=project_id,
            tasks=tasks,
            blocked=bool(blockers),
            blockers=blockers,
        )
        SegmentDAG(recipe.tasks).topological_order()
        return recipe
