"""Static, fail-closed cross-department artifact wiring validation.

This module validates declared producers and consumers before company execution.
Runtime artifact integrity (hashes, media QC, signatures) is a separate gate.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from .company import CompanyStage


class ArtifactWiringProblem(BaseModel):
    code: str
    stage_id: str
    artifact: str
    detail: str


class CompanyWiringReport(BaseModel):
    valid: bool
    external_inputs: list[str] = Field(default_factory=list)
    producer_by_artifact: dict[str, str] = Field(default_factory=dict)
    issues: list[ArtifactWiringProblem] = Field(default_factory=list)

    def blocker_codes(self) -> list[str]:
        return [
            f"{item.code}:{item.stage_id}:{item.artifact}"
            for item in self.issues
        ]


# These are owned inputs delivered to the project intake, not generated
# by a department. Performance metrics are separately owner-authorized
# and cannot qualify any unverified learning as successful.
EXTERNAL_PROJECT_INPUTS = frozenset({
    "project_brief", "references", "performance_metrics",
})


def audit_company_wiring(
    stages: list[CompanyStage],
    *,
    external_inputs: frozenset[str] = EXTERNAL_PROJECT_INPUTS,
) -> CompanyWiringReport:
    issues: list[ArtifactWiringProblem] = []
    producers: dict[str, str] = {}
    seen: set[str] = set()

    for stage in stages:
        if stage.stage_id in seen:
            issues.append(ArtifactWiringProblem(
                code="DUPLICATE_STAGE", stage_id=stage.stage_id,
                artifact=stage.stage_id,
                detail="A stage must have exactly one owner and stable id.",
            ))
        seen.add(stage.stage_id)
        for artifact in stage.artifacts_out:
            if artifact in producers:
                issues.append(ArtifactWiringProblem(
                    code="MULTIPLE_PRODUCERS", stage_id=stage.stage_id,
                    artifact=artifact,
                    detail=f"Already declared by {producers[artifact]}",
                ))
            else:
                producers[artifact] = stage.stage_id

    for stage in stages:
        for artifact in stage.artifacts_in:
            if artifact not in producers and artifact not in external_inputs:
                issues.append(ArtifactWiringProblem(
                    code="UNBOUND_INPUT", stage_id=stage.stage_id,
                    artifact=artifact,
                    detail="No producing department or authorized external input.",
                ))
            if producers.get(artifact) == stage.stage_id:
                issues.append(ArtifactWiringProblem(
                    code="SELF_DEPENDENCY", stage_id=stage.stage_id,
                    artifact=artifact,
                    detail="An artifact cannot depend on its own producer.",
                ))
    return CompanyWiringReport(
        valid=not issues,
        external_inputs=sorted(external_inputs),
        producer_by_artifact=producers,
        issues=issues,
    )
