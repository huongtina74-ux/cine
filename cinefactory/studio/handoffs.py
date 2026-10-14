from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class HandoffState(StrEnum):
    OPEN = "OPEN"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class HandoffContract(BaseModel):
    handoff_id: str = Field(default_factory=lambda: f"HOF_{uuid4().hex[:12]}")
    project_id: str
    source_department: str
    destination_department: str
    object_versions: dict[str, int] = Field(min_length=1)
    intent: dict[str, Any] = Field(default_factory=dict)
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    known_risks: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(min_length=1)
    state: HandoffState = HandoffState.OPEN
    rejection_reason: str | None = None

    @model_validator(mode="after")
    def validate_versions(self) -> "HandoffContract":
        if any(version < 1 for version in self.object_versions.values()):
            raise ValueError("handoff object versions must be >= 1")
        if self.source_department == self.destination_department:
            raise ValueError("handoff requires distinct source and destination departments")
        return self


class HandoffRegistry:
    def __init__(self) -> None:
        self._items: dict[str, HandoffContract] = {}

    def create(self, contract: HandoffContract) -> HandoffContract:
        if contract.handoff_id in self._items:
            raise ValueError(f"handoff already exists: {contract.handoff_id}")
        self._items[contract.handoff_id] = contract
        return contract

    def get(self, handoff_id: str) -> HandoffContract:
        return self._items[handoff_id]

    def accept(self, handoff_id: str) -> HandoffContract:
        item = self._items[handoff_id]
        if item.state is not HandoffState.OPEN:
            raise ValueError("only OPEN handoffs can be accepted")
        item.state = HandoffState.ACCEPTED
        item.rejection_reason = None
        return item

    def reject(self, handoff_id: str, reason: str) -> HandoffContract:
        if not reason.strip():
            raise ValueError("handoff rejection requires a reason")
        item = self._items[handoff_id]
        if item.state is not HandoffState.OPEN:
            raise ValueError("only OPEN handoffs can be rejected")
        item.state = HandoffState.REJECTED
        item.rejection_reason = reason
        return item
