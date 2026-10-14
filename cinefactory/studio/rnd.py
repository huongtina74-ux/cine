from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class IntakeState(StrEnum):
    DISCOVERED = "DISCOVERED"
    LICENSE_REVIEW = "LICENSE_REVIEW"
    SECURITY_REVIEW = "SECURITY_REVIEW"
    SANDBOX = "SANDBOX"
    BENCHMARK = "BENCHMARK"
    ADAPTER = "ADAPTER"
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    DEPRECATED = "DEPRECATED"


class ExternalToolCandidate(BaseModel):
    candidate_id: str
    name: str
    source_uri: str
    source_type: str
    version: str | None = None
    license_name: str | None = None
    commercial_use_known: bool = False
    commercial_use_allowed: bool | None = None
    security_reviewed: bool = False
    sandbox_passed: bool = False
    benchmark_passed: bool = False
    regression_passed: bool = False
    state: IntakeState = IntakeState.DISCOVERED
    capabilities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    benchmark: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def approved_requires_all_gates(self) -> "ExternalToolCandidate":
        if self.state is IntakeState.APPROVED:
            if not (
                self.commercial_use_known
                and self.commercial_use_allowed is True
                and self.security_reviewed
                and self.sandbox_passed
                and self.benchmark_passed
                and self.regression_passed
            ):
                raise ValueError("approved external tool must pass rights, security, sandbox, benchmark and regression")
        return self
class ExternalToolIntake:
    """Controlled external repo/tool intake; discovery never means production approval."""

    @staticmethod
    def next_state(candidate: ExternalToolCandidate) -> IntakeState:
        if not candidate.commercial_use_known or candidate.commercial_use_allowed is not True:
            return IntakeState.LICENSE_REVIEW
        if not candidate.security_reviewed:
            return IntakeState.SECURITY_REVIEW
        if not candidate.sandbox_passed:
            return IntakeState.SANDBOX
        if not candidate.benchmark_passed:
            return IntakeState.BENCHMARK
        if not candidate.regression_passed:
            return IntakeState.ADAPTER
        return IntakeState.APPROVED

    def advance(self, candidate: ExternalToolCandidate) -> ExternalToolCandidate:
        updated = candidate.model_copy(deep=True)
        updated.state = self.next_state(updated)
        return ExternalToolCandidate.model_validate(updated.model_dump())
