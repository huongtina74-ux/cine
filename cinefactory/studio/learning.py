from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from cinefactory.studio.contracts import KnowledgeScope


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LearningState(StrEnum):
    OBSERVATION = "OBSERVATION"
    HYPOTHESIS = "HYPOTHESIS"
    CANDIDATE = "CANDIDATE"
    SANDBOXED = "SANDBOXED"
    EVALUATED = "EVALUATED"
    PROMOTED = "PROMOTED"
    REJECTED = "REJECTED"
    DEPRECATED = "DEPRECATED"


class ControlledExperiment(BaseModel):
    experiment_id: str = Field(
        default_factory=lambda: f"EXP_{uuid4().hex[:10]}"
    )
    control: dict[str, Any]
    variant: dict[str, Any]
    causal_claim: bool = True
    evidence: list[str] = Field(default_factory=list)

    @property
    def changed_variables(self) -> list[str]:
        keys = set(self.control) | set(self.variant)
        return sorted(
            key
            for key in keys
            if self.control.get(key) != self.variant.get(key)
        )

    @model_validator(mode="after")
    def enforce_single_variable_causality(
        self,
    ) -> "ControlledExperiment":
        if self.causal_claim and len(self.changed_variables) != 1:
            raise ValueError(
                "CAUSAL_EXPERIMENT_REQUIRES_EXACTLY_ONE_CHANGED_VARIABLE"
            )
        return self


class LearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"LRN_{uuid4().hex[:10]}")
    scope: KnowledgeScope
    state: LearningState = LearningState.OBSERVATION
    subject: str
    observation: str
    hypothesis: str | None = None
    evidence: list[str] = Field(default_factory=list)
    experiment: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_project_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class LearningPolicy:
    """Prevents anecdotal observations from becoming universal production rules."""

    @staticmethod
    def can_promote(record: LearningRecord) -> tuple[bool, list[str]]:
        findings: list[str] = []
        if record.state is not LearningState.EVALUATED:
            findings.append("NOT_EVALUATED")
        if record.confidence < 0.8:
            findings.append("LOW_CONFIDENCE")
        if not record.evidence:
            findings.append("NO_EVIDENCE")
        if record.scope is KnowledgeScope.STUDIO and len(set(record.source_project_ids)) < 3:
            findings.append("STUDIO_RULE_REQUIRES_MULTIPLE_PROJECTS")
        return not findings, findings

class LearningStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, record: LearningRecord) -> LearningRecord:
        record.updated_at = utcnow()
        path = self.root / f"{record.record_id}.json"
        path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
        return record

    def promote(self, record_id: str) -> LearningRecord:
        path = self.root / f"{record_id}.json"
        record = LearningRecord.model_validate_json(path.read_text(encoding="utf-8"))
        passed, findings = LearningPolicy.can_promote(record)
        if not passed:
            raise ValueError(";".join(findings))
        record.state = LearningState.PROMOTED
        return self.save(record)
