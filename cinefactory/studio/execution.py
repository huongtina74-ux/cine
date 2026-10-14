from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

from .company import CompanyBlueprint, CompanyStage
from .contracts import DepartmentId
from .qc_department import QCDepartment, RepairAssignment, StudioQCFinding


class StageState(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    NEEDS_REPAIR = "NEEDS_REPAIR"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


class StageExecutionRecord(BaseModel):
    stage_id: str
    state: StageState = StageState.PENDING
    attempts: int = Field(default=0, ge=0)
    checkpoint_ref: str | None = None
    produced_artifacts: list[str] = Field(default_factory=list)
    error: str | None = None
    findings: list[str] = Field(default_factory=list)


class CompanyExecutionLedger(BaseModel):
    project_id: str
    records: list[StageExecutionRecord]

    @model_validator(mode="after")
    def unique_stage_ids(self) -> "CompanyExecutionLedger":
        ids = [item.stage_id for item in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("execution ledger stage_id values must be unique")
        return self

    def get(self, stage_id: str) -> StageExecutionRecord:
        for record in self.records:
            if record.stage_id == stage_id:
                return record
        raise KeyError(stage_id)


class StageSchedule(BaseModel):
    ready_stage_ids: list[str] = Field(default_factory=list)
    blocked_stage_ids: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class RepairTicket(BaseModel):
    stage_id: str
    finding_code: str
    owner: DepartmentId
    scope: str
    action: str


class CompanyStageDAG:
    """Infers stage dependencies from declared artifact production/consumption."""

    def __init__(self, stages: list[CompanyStage]) -> None:
        self.stages = {stage.stage_id: stage for stage in stages}
        if len(self.stages) != len(stages):
            raise ValueError("COMPANY_STAGE_ID_DUPLICATE")
        self.producer: dict[str, str] = {}
        for stage in stages:
            for artifact in stage.artifacts_out:
                previous = self.producer.get(artifact)
                if previous is not None and previous != stage.stage_id:
                    raise ValueError(f"ARTIFACT_MULTI_PRODUCER:{artifact}")
                self.producer[artifact] = stage.stage_id
        self.dependencies: dict[str, set[str]] = {}
        for stage in stages:
            deps = {
                self.producer[name]
                for name in stage.artifacts_in
                if name in self.producer and self.producer[name] != stage.stage_id
            }
            self.dependencies[stage.stage_id] = deps

    def topological_order(self) -> list[str]:
        remaining = {key: set(value) for key, value in self.dependencies.items()}
        order: list[str] = []
        while remaining:
            ready = sorted(key for key, deps in remaining.items() if not deps)
            if not ready:
                raise ValueError("COMPANY_STAGE_DAG_CYCLE")
            for stage_id in ready:
                order.append(stage_id)
                remaining.pop(stage_id)
            for deps in remaining.values():
                deps.difference_update(ready)
        return order


class ExecutionLedgerStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def _path(self, project_id: str) -> Path:
        return self.root / f"{project_id}.json"

    def save(self, ledger: CompanyExecutionLedger) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._path(ledger.project_id)
        path.write_text(ledger.model_dump_json(indent=2), encoding="utf-8")
        return path

    def load(self, project_id: str) -> CompanyExecutionLedger:
        return CompanyExecutionLedger.model_validate_json(
            self._path(project_id).read_text(encoding="utf-8")
        )


class CompanyExecutionEngine:
    """Durable stage-level controller for the autonomous media company."""

    TERMINAL_SUCCESS = {StageState.SUCCEEDED, StageState.SKIPPED}

    def __init__(
        self,
        blueprint: CompanyBlueprint,
        *,
        ledger: CompanyExecutionLedger | None = None,
        retry_limit: int = 2,
        qc: QCDepartment | None = None,
    ) -> None:
        self.blueprint = blueprint
        self.retry_limit = retry_limit
        self.qc = qc or QCDepartment()
        self.dag = CompanyStageDAG(blueprint.stages)
        self.stage_map = {stage.stage_id: stage for stage in blueprint.stages}
        self.ledger = ledger or CompanyExecutionLedger(
            project_id=blueprint.project.studio_project_id,
            records=[
                StageExecutionRecord(stage_id=stage.stage_id)
                for stage in blueprint.stages
            ],
        )
        if self.ledger.project_id != blueprint.project.studio_project_id:
            raise ValueError("execution ledger project mismatch")
        if {r.stage_id for r in self.ledger.records} != set(self.stage_map):
            raise ValueError("execution ledger stage set mismatch")

    def _deps_satisfied(self, stage_id: str) -> bool:
        return all(
            self.ledger.get(dep).state in self.TERMINAL_SUCCESS
            for dep in self.dag.dependencies[stage_id]
        )

    def schedule(self) -> StageSchedule:
        ready: list[str] = []
        blocked: list[str] = []
        reasons: list[str] = []
        for stage_id in self.dag.topological_order():
            stage = self.stage_map[stage_id]
            record = self.ledger.get(stage_id)
            if record.state in {
                StageState.RUNNING,
                StageState.SUCCEEDED,
                StageState.SKIPPED,
                StageState.FAILED,
                StageState.BLOCKED,
            }:
                continue
            failed_deps = [
                dep
                for dep in self.dag.dependencies[stage_id]
                if self.ledger.get(dep).state in {StageState.FAILED, StageState.BLOCKED}
            ]
            if failed_deps:
                record.state = StageState.BLOCKED
                blocked.append(stage_id)
                reasons.append(f"{stage_id}:UPSTREAM_FAILED:{','.join(sorted(failed_deps))}")
                continue
            if not self._deps_satisfied(stage_id):
                continue
            if record.state is StageState.NEEDS_REPAIR:
                continue
            record.state = StageState.READY
            ready.append(stage_id)
        return StageSchedule(ready_stage_ids=ready, blocked_stage_ids=blocked, reasons=reasons)

    def start(self, stage_id: str) -> StageExecutionRecord:
        record = self.ledger.get(stage_id)
        if record.state is not StageState.READY:
            raise RuntimeError(f"{stage_id} is not READY")
        record.state = StageState.RUNNING
        record.attempts += 1
        record.error = None
        record.findings = []
        return record

    def skip_optional(self, stage_id: str) -> StageExecutionRecord:
        stage = self.stage_map[stage_id]
        if stage.required:
            raise RuntimeError(f"{stage_id} is required")
        record = self.ledger.get(stage_id)
        if record.state is StageState.RUNNING:
            raise RuntimeError(f"{stage_id} is already RUNNING")
        record.state = StageState.SKIPPED
        return record

    def succeed(
        self,
        stage_id: str,
        produced_artifacts: list[str],
        *,
        checkpoint_ref: str | None = None,
    ) -> StageExecutionRecord:
        record = self.ledger.get(stage_id)
        if record.state is not StageState.RUNNING:
            raise RuntimeError(f"{stage_id} is not RUNNING")
        expected = set(self.stage_map[stage_id].artifacts_out)
        missing = sorted(expected.difference(produced_artifacts))
        if missing:
            raise ValueError(f"{stage_id}:MISSING_STAGE_OUTPUTS:{','.join(missing)}")

        record.state = StageState.SUCCEEDED
        record.produced_artifacts = list(dict.fromkeys(produced_artifacts))
        record.checkpoint_ref = checkpoint_ref
        return record

    def fail(
        self,
        stage_id: str,
        error: str,
        *,
        findings: list[str] | None = None,
    ) -> StageExecutionRecord:
        record = self.ledger.get(stage_id)
        if record.state is not StageState.RUNNING:
            raise RuntimeError(f"{stage_id} is not RUNNING")
        record.error = error
        record.findings = list(findings or [])
        record.state = (
            StageState.NEEDS_REPAIR
            if record.attempts <= self.retry_limit
            else StageState.FAILED
        )
        return record

    def repair_complete(self, stage_id: str) -> StageExecutionRecord:
        record = self.ledger.get(stage_id)
        if record.state is not StageState.NEEDS_REPAIR:
            raise RuntimeError(f"{stage_id} does not need repair")
        record.state = StageState.PENDING
        return record

    def route_qc_findings(
        self,
        stage_id: str,
        findings: list[StudioQCFinding],
    ) -> list[RepairTicket]:
        assignments: list[RepairAssignment] = self.qc.assignments(findings)

        tickets = [
            RepairTicket(
                stage_id=stage_id,
                finding_code=item.finding_code,
                owner=item.owner,
                scope=item.scope,
                action=item.action,
            )
            for item in assignments
        ]
        if tickets:
            record = self.ledger.get(stage_id)
            record.state = StageState.NEEDS_REPAIR
            record.findings = [item.finding_code for item in tickets]
        return tickets

    def is_complete(self) -> bool:
        for stage in self.blueprint.stages:
            state = self.ledger.get(stage.stage_id).state
            if stage.required and state is not StageState.SUCCEEDED:
                return False
            if not stage.required and state not in self.TERMINAL_SUCCESS:
                return False
        return True
