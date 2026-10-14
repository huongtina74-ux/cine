from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResourceClass(StrEnum):
    CPU = "CPU"
    GPU = "GPU"
    IO = "IO"
    AGENT = "AGENT"


class WorkState(StrEnum):
    QUEUED = "QUEUED"
    CLAIMED = "CLAIMED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    RETRY = "RETRY"
    QC_REJECTED = "QC_REJECTED"
    BLOCKED = "BLOCKED"
    DEAD_LETTER = "DEAD_LETTER"
    CANCELLED = "CANCELLED"


class EventState(StrEnum):
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    DONE = "DONE"
    FAILED = "FAILED"


class FactoryEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"FEVT_{uuid4().hex[:12]}")
    event_type: str
    project_id: str | None = None
    entity_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=50, ge=0, le=100)
    state: EventState = EventState.PENDING
    created_at: datetime = Field(default_factory=utcnow)


class WorkItem(BaseModel):
    work_id: str = Field(default_factory=lambda: f"WORK_{uuid4().hex[:12]}")
    project_id: str
    kind: str
    handler: str
    resource: ResourceClass = ResourceClass.CPU
    priority: int = Field(default=50, ge=0, le=100)
    model_affinity: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)
    state: WorkState = WorkState.QUEUED
    attempts: int = 0
    max_attempts: int = Field(default=3, ge=1, le=20)
    worker_id: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    last_error: str | None = None
    result: dict[str, Any] = Field(default_factory=dict)


class WorkerSpec(BaseModel):
    worker_id: str
    resources: set[ResourceClass]
    capabilities: set[str] = Field(default_factory=set)
    max_concurrent: int = Field(default=1, ge=1, le=64)
    active_model_affinity: str | None = None
    healthy: bool = True
    last_heartbeat: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RepairMemoryEntry(BaseModel):
    key: str
    failure_code: str
    workflow_id: str | None = None
    shot_class: str | None = None
    strategy: str
    prompt_directive: str | None = None
    attempts: int = 0
    successes: int = 0
    average_score: float = 0.0

    @property
    def success_rate(self) -> float:
        return self.successes / self.attempts if self.attempts else 0.0


class ThroughputSample(BaseModel):
    sample_id: str = Field(default_factory=lambda: f"TPS_{uuid4().hex[:12]}")
    worker_id: str
    kind: str
    model_affinity: str | None = None
    duration_seconds: float = Field(gt=0)
    output_units: float = Field(default=1.0, gt=0)
    created_at: datetime = Field(default_factory=utcnow)


class ExecutionCostSample(BaseModel):
    sample_id: str = Field(
        default_factory=lambda: f"COST_{uuid4().hex[:12]}"
    )
    work_id: str
    project_id: str
    worker_id: str
    kind: str
    resource: ResourceClass
    state: WorkState
    duration_seconds: float = Field(gt=0)
    output_units: float = Field(default=1.0, gt=0)
    accepted: bool
    repair_round: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utcnow)
