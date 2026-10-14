from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .contracts import ChangeRequest, DepartmentId


class ChangeStatus(StrEnum):
    OPEN = "OPEN"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"


class ChangeDecision(BaseModel):
    change_id: str
    status: ChangeStatus
    decider: DepartmentId
    rationale: str
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChangeRequestStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _request_path(self, change_id: str) -> Path:
        return self.root / f"{change_id}.request.json"

    def _decision_path(self, change_id: str) -> Path:
        return self.root / f"{change_id}.decision.json"

    def create(self, request: ChangeRequest) -> ChangeRequest:
        path = self._request_path(request.change_id)
        if path.exists():
            raise FileExistsError(request.change_id)
        path.write_text(request.model_dump_json(indent=2), encoding="utf-8")
        return request

    def decide(
        self,
        change_id: str,
        *,
        decider: DepartmentId,
        approve: bool,
        rationale: str,
    ) -> ChangeDecision:
        request = self.get(change_id)
        if decider != request.owner and decider is not DepartmentId.STUDIO_MANAGEMENT:
            raise PermissionError("only artifact owner or studio management can decide")
        decision = ChangeDecision(
            change_id=change_id,
            status=ChangeStatus.APPROVED if approve else ChangeStatus.REJECTED,
            decider=decider,
            rationale=rationale,
        )
        self._decision_path(change_id).write_text(decision.model_dump_json(indent=2), encoding="utf-8")
        return decision

    def get(self, change_id: str) -> ChangeRequest:
        return ChangeRequest.model_validate_json(self._request_path(change_id).read_text(encoding="utf-8"))

    def decision(self, change_id: str) -> ChangeDecision | None:
        path = self._decision_path(change_id)
        return ChangeDecision.model_validate_json(path.read_text(encoding="utf-8")) if path.exists() else None
class TraceEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"TRC_{uuid4().hex[:12]}")
    project_id: str
    actor: DepartmentId
    action: str
    artifact_id: str | None = None
    segment_id: str | None = None
    decision: str | None = None
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StudioTrace:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: TraceEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json() + "\n")

    def read(self) -> list[TraceEvent]:
        if not self.path.exists():
            return []
        return [
            TraceEvent.model_validate_json(line)
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
