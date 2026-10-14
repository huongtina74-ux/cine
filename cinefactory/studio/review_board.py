from __future__ import annotations

from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class ReviewSeverity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReviewState(StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    WAIVED = "WAIVED"


class ReviewNote(BaseModel):
    note_id: str = Field(default_factory=lambda: f"NOTE_{uuid4().hex[:12]}")
    project_id: str
    object_id: str
    reviewer_department: str
    reviewer_id: str
    owner_department: str
    problem: str = Field(min_length=3)
    evidence: str = Field(min_length=3)
    impact: str = Field(min_length=3)
    acceptance_criteria: str = Field(min_length=3)
    severity: ReviewSeverity = ReviewSeverity.MEDIUM
    state: ReviewState = ReviewState.OPEN
    resolution_evidence: str | None = None

    @model_validator(mode="after")
    def independent_review(self) -> "ReviewNote":
        if self.reviewer_department == self.owner_department and self.severity in {
            ReviewSeverity.HIGH,
            ReviewSeverity.CRITICAL,
        }:
            raise ValueError("high/critical review must be independent from owning department")
        return self


class DailiesReviewBoard:
    def __init__(self) -> None:
        self._notes: dict[str, ReviewNote] = {}

    def add(self, note: ReviewNote) -> ReviewNote:
        if note.note_id in self._notes:
            raise ValueError(f"review note already exists: {note.note_id}")
        self._notes[note.note_id] = note
        return note

    def resolve(self, note_id: str, evidence: str) -> ReviewNote:
        if not evidence.strip():
            raise ValueError("resolution evidence is required")
        note = self._notes[note_id]
        note.state = ReviewState.RESOLVED
        note.resolution_evidence = evidence
        return note

    def blockers(self, project_id: str | None = None) -> list[ReviewNote]:
        out: list[ReviewNote] = []
        for note in self._notes.values():
            if project_id and note.project_id != project_id:
                continue
            if note.state is ReviewState.OPEN and note.severity in {
                ReviewSeverity.HIGH,
                ReviewSeverity.CRITICAL,
            }:
                out.append(note)
        return out

    def list(self, project_id: str | None = None) -> list[ReviewNote]:
        return [
            note for note in self._notes.values()
            if project_id is None or note.project_id == project_id
        ]
