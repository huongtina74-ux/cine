from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field

from cinefactory.turbo.contracts import ResourceClass, WorkItem, WorkState
from cinefactory.turbo.metrics import gpu_snapshot
from cinefactory.studio.production_economics import (
    ProductionEconomicsController,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProjectPriority(StrEnum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


PRIORITY_SCORE = {
    ProjectPriority.LOW: 25,
    ProjectPriority.NORMAL: 50,
    ProjectPriority.HIGH: 75,
    ProjectPriority.URGENT: 95,
}


class OperatingProjectState(StrEnum):
    QUEUED = "QUEUED"
    ADMITTED = "ADMITTED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class FactoryProjectRequest(BaseModel):
    project_id: str
    priority: ProjectPriority = ProjectPriority.NORMAL
    sla_seconds: int | None = Field(default=None, gt=0)
    required_vram_gb: float = Field(default=0.0, ge=0.0)
    max_cost_class: str = "FREE_LOCAL"
    metadata: dict = Field(default_factory=dict)


class FactoryProjectRecord(BaseModel):
    project_id: str
    priority: ProjectPriority
    state: OperatingProjectState = OperatingProjectState.QUEUED
    sla_seconds: int | None = None
    required_vram_gb: float = 0.0
    max_cost_class: str = "FREE_LOCAL"
    admitted_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)


class FactoryOperationsPolicy(BaseModel):
    max_active_projects: int = Field(default=3, ge=1, le=64)
    gpu_vram_reserve_gb: float = Field(default=1.5, ge=0.0)
    stale_worker_seconds: int = Field(default=180, ge=30)
    max_dead_letter_recoveries: int = Field(default=1, ge=0, le=5)
    allowed_cost_classes: set[str] = Field(default_factory=lambda: {"FREE_LOCAL"})
    transient_error_tokens: tuple[str, ...] = (
        "timeout",
        "temporarily",
        "connection reset",
        "broken pipe",
        "worker exited",
        "device busy",
    )


class AdmissionDecision(BaseModel):
    admitted: bool
    reasons: list[str] = Field(default_factory=list)
    priority_score: int


class FactoryHealthReport(BaseModel):
    gpu: dict
    active_projects: list[str] = Field(default_factory=list)
    queued_projects: list[str] = Field(default_factory=list)
    stale_workers: list[str] = Field(default_factory=list)
    dead_letters: list[str] = Field(default_factory=list)
    blocked_work: list[str] = Field(default_factory=list)
    sla_breaches: list[str] = Field(default_factory=list)
    throughput: list[dict] = Field(default_factory=list)
    execution_cost: dict = Field(default_factory=dict)
    economics: dict = Field(default_factory=dict)


class FactoryWatchdogReport(BaseModel):
    health: FactoryHealthReport
    recovered_work_ids: list[str] = Field(default_factory=list)


class FactoryOperationsStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, project_id: str) -> Path:
        return self.root / f"{project_id}.json"

    def save(self, record: FactoryProjectRecord) -> FactoryProjectRecord:
        self._path(record.project_id).write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return record

    def get(self, project_id: str) -> FactoryProjectRecord:
        path = self._path(project_id)
        if not path.exists():
            raise KeyError(project_id)
        return FactoryProjectRecord.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def list(self) -> list[FactoryProjectRecord]:
        return [
            FactoryProjectRecord.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            for path in sorted(self.root.glob("*.json"))
        ]


class FactoryOperationsManager:
    def __init__(
        self,
        *,
        turbo_store,
        store: FactoryOperationsStore,
        policy: FactoryOperationsPolicy | None = None,
    ) -> None:
        self.turbo_store = turbo_store
        self.store = store
        self.policy = policy or FactoryOperationsPolicy()
        self.economics = ProductionEconomicsController()

    def _active(self) -> list[FactoryProjectRecord]:
        return [
            item
            for item in self.store.list()
            if item.state in {
                OperatingProjectState.ADMITTED,
                OperatingProjectState.RUNNING,
            }
        ]

    def admission(self, request: FactoryProjectRequest) -> AdmissionDecision:
        reasons: list[str] = []
        if request.max_cost_class not in self.policy.allowed_cost_classes:
            reasons.append("COST_CLASS_NOT_ALLOWED")
        if len(self._active()) >= self.policy.max_active_projects:
            reasons.append("ACTIVE_PROJECT_LIMIT")
        snap = gpu_snapshot()
        if request.required_vram_gb > 0 and snap.get("available"):
            gpus = snap.get("gpus") or []
            if gpus:
                gpu = gpus[0]
                free = (
                    float(gpu.get("vram_mb", 0))
                    - float(gpu.get("vram_used_mb", 0))
                ) / 1024
                usable = max(0.0, free - self.policy.gpu_vram_reserve_gb)
                if request.required_vram_gb > usable:
                    reasons.append("INSUFFICIENT_FREE_VRAM")
        return AdmissionDecision(
            admitted=not reasons,
            reasons=reasons,
            priority_score=PRIORITY_SCORE[request.priority],
        )

    def submit(self, request: FactoryProjectRequest) -> FactoryProjectRecord:
        try:
            return self.store.get(request.project_id)
        except KeyError:
            pass
        decision = self.admission(request)
        record = FactoryProjectRecord(
            project_id=request.project_id,
            priority=request.priority,
            state=(
                OperatingProjectState.ADMITTED
                if decision.admitted
                else OperatingProjectState.QUEUED
            ),
            sla_seconds=request.sla_seconds,
            required_vram_gb=request.required_vram_gb,
            max_cost_class=request.max_cost_class,
            admitted_at=utcnow() if decision.admitted else None,
            metadata={
                **request.metadata,
                "admission_reasons": decision.reasons,
                "priority_score": decision.priority_score,
            },
        )
        return self.store.save(record)

    def prepare_work(self, item: WorkItem) -> WorkItem:
        try:
            record = self.store.get(item.project_id)
        except KeyError:
            return item
        payload = dict(item.payload)
        if item.resource is ResourceClass.GPU and record.required_vram_gb > 0:
            payload.setdefault("required_vram_gb", record.required_vram_gb)
        return item.model_copy(
            update={
                "priority": max(item.priority, PRIORITY_SCORE[record.priority]),
                "payload": payload,
            }
        )

    def enqueue_work(self, item: WorkItem) -> tuple[WorkItem, bool]:
        prepared = self.prepare_work(item)
        return self.turbo_store.enqueue_work(prepared)

    def gpu_launch_allowed(self, required_vram_gb: float = 0.0) -> bool:
        snap = gpu_snapshot()
        if not snap.get("available"):
            return required_vram_gb <= 0
        gpus = snap.get("gpus") or []
        if not gpus:
            return required_vram_gb <= 0
        gpu = gpus[0]
        free = (
            float(gpu.get("vram_mb", 0))
            - float(gpu.get("vram_used_mb", 0))
        ) / 1024
        usable = max(0.0, free - self.policy.gpu_vram_reserve_gb)
        return required_vram_gb <= usable

    def start(self, project_id: str) -> FactoryProjectRecord:
        record = self.store.get(project_id)
        if record.state is not OperatingProjectState.ADMITTED:
            raise RuntimeError(f"{project_id} is not ADMITTED")
        record.state = OperatingProjectState.RUNNING
        record.started_at = utcnow()
        return self.store.save(record)

    def finish(
        self,
        project_id: str,
        *,
        success: bool,
        error: str | None = None,
    ) -> FactoryProjectRecord:
        record = self.store.get(project_id)
        record.state = (
            OperatingProjectState.COMPLETE
            if success
            else OperatingProjectState.FAILED
        )
        record.error = error
        record.finished_at = utcnow()
        return self.store.save(record)


    def reevaluate_queue(self) -> list[str]:
        admitted: list[str] = []
        queued = sorted(
            (
                item
                for item in self.store.list()
                if item.state is OperatingProjectState.QUEUED
            ),
            key=lambda item: (-PRIORITY_SCORE[item.priority], item.project_id),
        )
        for record in queued:
            request = FactoryProjectRequest(
                project_id=record.project_id,
                priority=record.priority,
                sla_seconds=record.sla_seconds,
                required_vram_gb=record.required_vram_gb,
                max_cost_class=record.max_cost_class,
                metadata=record.metadata,
            )
            decision = self.admission(request)
            if not decision.admitted:
                continue
            record.state = OperatingProjectState.ADMITTED
            record.admitted_at = utcnow()
            record.metadata["admission_reasons"] = []
            self.store.save(record)
            admitted.append(record.project_id)
        return admitted

    def recover_transient_dead_letters(self) -> list[str]:
        recovered: list[str] = []
        items = self.turbo_store.list_work(
            states=[WorkState.DEAD_LETTER],
            limit=2000,
        )
        for item in items:
            error = (item.last_error or "").lower()
            if not any(token in error for token in self.policy.transient_error_tokens):
                continue
            count = int(item.payload.get("_recovery_count", 0) or 0)
            if count >= self.policy.max_dead_letter_recoveries:
                continue
            payload = dict(item.payload)
            payload["_recovery_count"] = count + 1
            payload["recovery_of"] = item.work_id
            clone = WorkItem(
                work_id=f"WORK_REC_{uuid4().hex[:12]}",
                project_id=item.project_id,
                kind=item.kind,
                handler=item.handler,
                resource=item.resource,
                priority=min(100, item.priority + 5),
                model_affinity=item.model_affinity,
                dependencies=list(item.dependencies),
                payload=payload,
                max_attempts=item.max_attempts,
            )
            self.turbo_store.enqueue_work(clone)
            recovered.append(clone.work_id)
        return recovered

    def health(self) -> FactoryHealthReport:
        status = self.turbo_store.status()
        now = utcnow()
        stale: list[str] = []
        for worker in status.get("workers", []):
            raw = worker.get("last_heartbeat")
            if not raw:
                stale.append(worker.get("worker_id", "unknown"))
                continue
            heartbeat = datetime.fromisoformat(raw)
            age = (now - heartbeat).total_seconds()
            if age > self.policy.stale_worker_seconds:
                stale.append(worker.get("worker_id", "unknown"))

        work = self.turbo_store.list_work(limit=5000)
        active = [
            item.project_id
            for item in self.store.list()
            if item.state is OperatingProjectState.RUNNING
        ]
        records = self.store.list()
        queued = [
            item.project_id
            for item in records
            if item.state is OperatingProjectState.QUEUED
        ]
        sla_breaches: list[str] = []
        for item in records:
            if (
                item.state is OperatingProjectState.RUNNING
                and item.sla_seconds
                and item.started_at is not None
            ):
                age = (now - item.started_at).total_seconds()
                if age > item.sla_seconds:
                    sla_breaches.append(item.project_id)
        execution_cost = dict(
            status.get("execution_cost") or {}
        )
        return FactoryHealthReport(
            gpu=gpu_snapshot(),
            active_projects=sorted(active),
            queued_projects=sorted(queued),
            stale_workers=sorted(set(stale)),
            dead_letters=sorted(
                item.work_id
                for item in work
                if item.state is WorkState.DEAD_LETTER
            ),
            blocked_work=sorted(
                item.work_id
                for item in work
                if item.state is WorkState.BLOCKED
            ),
            sla_breaches=sorted(sla_breaches),
            throughput=status.get("throughput", []),
            execution_cost=execution_cost,
            economics=self.economics.kpi_report(
                execution_cost
            ),
        )

    def watchdog_tick(self) -> FactoryWatchdogReport:
        initial = self.health()
        for worker_id in initial.stale_workers:
            self.turbo_store.set_worker_health(worker_id, False)
        recovered = self.recover_transient_dead_letters()
        return FactoryWatchdogReport(
            health=self.health(),
            recovered_work_ids=recovered,
        )
