from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from pydantic import BaseModel, Field

from .production import ProductionRecipe, ProductionTask


class JobState(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


class ResourceSnapshot(BaseModel):
    gpu_slots: int = Field(default=1, ge=0)
    cpu_slots: int = Field(default=4, ge=0)
    io_slots: int = Field(default=2, ge=0)


class JobRecord(BaseModel):
    task_id: str
    state: JobState = JobState.PENDING
    attempts: int = Field(default=0, ge=0)
    checkpoint_ref: str | None = None
    error: str | None = None


class ScheduleDecision(BaseModel):
    runnable_task_ids: list[str] = Field(default_factory=list)
    blocked_task_ids: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
class QueueManager:
    """Dependency-aware, resource-aware scheduler. It never runs blocked capabilities."""

    def __init__(self, recipe: ProductionRecipe) -> None:
        self.recipe = recipe
        self.records = {task.task_id: JobRecord(task_id=task.task_id) for task in recipe.tasks}
        self.tasks = {task.task_id: task for task in recipe.tasks}

    def mark(self, task_id: str, state: JobState, *, checkpoint_ref: str | None = None, error: str | None = None) -> None:
        record = self.records[task_id]
        if state is JobState.RUNNING:
            record.attempts += 1
        record.state = state
        if checkpoint_ref is not None:
            record.checkpoint_ref = checkpoint_ref
        record.error = error

    def _deps_satisfied(self, task: ProductionTask) -> bool:
        return all(self.records[d].state is JobState.SUCCEEDED for d in task.dependencies)

    def schedule(self, resources: ResourceSnapshot) -> ScheduleDecision:
        available = {
            "GPU": resources.gpu_slots,
            "CPU": resources.cpu_slots,
            "IO": resources.io_slots,
        }
        runnable: list[str] = []
        blocked: list[str] = []
        reasons: list[str] = []

        for task in self.recipe.tasks:
            record = self.records[task.task_id]
            if record.state in {JobState.SUCCEEDED, JobState.RUNNING, JobState.SKIPPED}:
                continue
            if not task.executable:
                record.state = JobState.BLOCKED
                blocked.append(task.task_id)
                reasons.append(f"{task.task_id}:NOT_EXECUTABLE")
                continue
            if record.attempts > task.retry_limit:
                record.state = JobState.FAILED
                blocked.append(task.task_id)
                reasons.append(f"{task.task_id}:RETRY_LIMIT_EXCEEDED")
                continue
            if not self._deps_satisfied(task):
                continue

            resource = task.resource_class
            if available.get(resource, 0) <= 0:
                continue
            available[resource] -= 1
            record.state = JobState.READY
            runnable.append(task.task_id)

        return ScheduleDecision(
            runnable_task_ids=runnable,
            blocked_task_ids=blocked,
            reasons=reasons,
        )
class CostClass(StrEnum):
    FREE_LOCAL = "FREE_LOCAL"
    LICENSED_LOCAL = "LICENSED_LOCAL"
    PAID_API = "PAID_API"
    HUMAN = "HUMAN"


class CostPolicy(BaseModel):
    allowed: set[CostClass] = Field(default_factory=lambda: {CostClass.FREE_LOCAL, CostClass.LICENSED_LOCAL})
    max_paid_api_usd: float = Field(default=0.0, ge=0)


class ResourceManager:
    """Keeps execution policy separate from creative planning."""

    def __init__(self, cost_policy: CostPolicy | None = None) -> None:
        self.cost_policy = cost_policy or CostPolicy()

    def authorize_cost(self, cost_class: CostClass, estimated_usd: float = 0.0) -> tuple[bool, str]:
        if cost_class not in self.cost_policy.allowed:
            return False, f"COST_CLASS_NOT_ALLOWED:{cost_class.value}"
        if cost_class is CostClass.PAID_API and estimated_usd > self.cost_policy.max_paid_api_usd:
            return False, "PAID_API_BUDGET_EXCEEDED"
        return True, "AUTHORIZED"
