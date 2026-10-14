from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProblemHypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=lambda: f"HYP_{uuid4().hex[:10]}")
    cause: str
    evidence: list[str] = Field(default_factory=list)
    test: str
    expected_result: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ProblemRecord(BaseModel):
    problem_id: str = Field(default_factory=lambda: f"PRB_{uuid4().hex[:10]}")
    code: str
    symptoms: list[str] = Field(min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    hypotheses: list[ProblemHypothesis] = Field(default_factory=list)
    root_cause: str | None = None
    solution_steps: list[str] = Field(default_factory=list)
    regression_test: str | None = None
    verified: bool = False
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

class ProblemLibrary:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, record: ProblemRecord) -> ProblemRecord:
        record.updated_at = utcnow()
        path = self.root / f"{record.problem_id}.json"
        path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
        return record

    def get(self, problem_id: str) -> ProblemRecord:
        path = self.root / f"{problem_id}.json"
        return ProblemRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def list(self) -> list[ProblemRecord]:
        values: list[ProblemRecord] = []
        for path in sorted(self.root.glob("*.json")):
            values.append(ProblemRecord.model_validate_json(path.read_text(encoding="utf-8")))
        return values

    def find_by_code(self, code: str, *, verified_only: bool = True) -> list[ProblemRecord]:
        values = [record for record in self.list() if record.code == code]
        if verified_only:
            values = [record for record in values if record.verified]
        return values


class ProblemSolver:
    """Fail-safe problem protocol. Known verified repairs are reusable; unknowns become experiments."""

    def __init__(self, library: ProblemLibrary) -> None:
        self.library = library

    def known_solution(self, code: str) -> ProblemRecord | None:
        matches = self.library.find_by_code(code, verified_only=True)
        if not matches:
            return None
        return sorted(matches, key=lambda item: item.updated_at, reverse=True)[0]
