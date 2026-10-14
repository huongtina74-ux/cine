from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from .contracts import DepartmentId


class QCLayer(StrEnum):
    TECHNICAL = "TECHNICAL"
    STORY_LOGIC = "STORY_LOGIC"
    FACTUAL = "FACTUAL"
    IDENTITY = "IDENTITY"
    PERFORMANCE = "PERFORMANCE"
    CONTINUITY = "CONTINUITY"
    CAMERA = "CAMERA"
    SCREEN_DIRECTION = "SCREEN_DIRECTION"
    EDITORIAL = "EDITORIAL"
    AUDIO = "AUDIO"
    COLOR = "COLOR"
    RIGHTS = "RIGHTS"
    BRAND = "BRAND"
    PLATFORM = "PLATFORM"
    ORIGINALITY = "ORIGINALITY"


class StudioQCFinding(BaseModel):
    code: str
    layer: QCLayer
    severity: str = "ERROR"
    message: str
    segment_id: str | None = None
    artifact_id: str | None = None
    evidence: list[str] = Field(default_factory=list)
    repairable: bool = True


class RepairAssignment(BaseModel):
    finding_code: str
    owner: DepartmentId
    scope: str
    action: str
OWNER_MAP: dict[QCLayer, DepartmentId] = {
    QCLayer.TECHNICAL: DepartmentId.OPERATIONS,
    QCLayer.STORY_LOGIC: DepartmentId.SCRIPT_LOGIC,
    QCLayer.FACTUAL: DepartmentId.EVIDENCE,
    QCLayer.IDENTITY: DepartmentId.ASSETS,
    QCLayer.PERFORMANCE: DepartmentId.PERFORMANCE,
    QCLayer.CONTINUITY: DepartmentId.DIRECTION,
    QCLayer.CAMERA: DepartmentId.CINEMATOGRAPHY,
    QCLayer.SCREEN_DIRECTION: DepartmentId.CINEMATOGRAPHY,
    QCLayer.EDITORIAL: DepartmentId.EDITORIAL,
    QCLayer.AUDIO: DepartmentId.AUDIO,
    QCLayer.COLOR: DepartmentId.COLOR,
    QCLayer.RIGHTS: DepartmentId.RIGHTS,
    QCLayer.BRAND: DepartmentId.PRODUCTION_DESIGN,
    QCLayer.PLATFORM: DepartmentId.PACKAGING,
    QCLayer.ORIGINALITY: DepartmentId.CREATIVE_STRATEGY,
}


class QCDepartment:
    """Routes each failure to the earliest responsible craft layer."""

    def assign(self, finding: StudioQCFinding) -> RepairAssignment:
        owner = OWNER_MAP[finding.layer]
        if finding.segment_id:
            scope = f"segment:{finding.segment_id}"
        elif finding.artifact_id:
            scope = f"artifact:{finding.artifact_id}"
        else:
            scope = "project"
        return RepairAssignment(
            finding_code=finding.code,
            owner=owner,
            scope=scope,
            action=f"repair {finding.layer.value.lower()} defect at minimum valid scope",
        )

    def assignments(self, findings: list[StudioQCFinding]) -> list[RepairAssignment]:
        return [self.assign(item) for item in findings if item.repairable]
