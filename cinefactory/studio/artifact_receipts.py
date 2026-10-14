from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from .company import CompanyStage
from .contracts import ArtifactState, DepartmentId
from .contract_integrity import ArtifactWiringProblem


def verify_persisted_outputs(
    blackboard: Any,
    project_id: str,
    stage: CompanyStage,
    reported: list[str],
) -> list[ArtifactWiringProblem]:
    """Verify real owned blackboard data, not just a handler's list of names.

    Safe for historic ledgers because only strict new blueprints opt in.
    Does not substitute for scene quality, model license or editorial review.
    """
    issues: list[ArtifactWiringProblem] = []
    for artifact in stage.artifacts_out:
        if artifact not in reported:
            issues.append(ArtifactWiringProblem(
                code="OUTPUT_NOT_REPORTED", stage_id=stage.stage_id,
                artifact=artifact, detail="Stage handler did not report this output",
            ))
            continue
        try:
            meta = blackboard.get_meta(project_id, artifact)
            envelope = blackboard.get(project_id, artifact, meta.version)
        except (KeyError, OSError, ValueError) as exc:
            issues.append(ArtifactWiringProblem(
                code="OUTPUT_NOT_PERSISTED", stage_id=stage.stage_id,
                artifact=artifact, detail=type(exc).__name__,
            ))
            continue
        if meta.owner != DepartmentId(stage.owner):
            issues.append(ArtifactWiringProblem(
                code="OUTPUT_OWNER_MISMATCH", stage_id=stage.stage_id,
                artifact=artifact, detail=str(meta.owner),
            ))
        if meta.state not in (ArtifactState.VALIDATED, ArtifactState.LOCKED):
            issues.append(ArtifactWiringProblem(
                code="OUTPUT_NOT_VALIDATED", stage_id=stage.stage_id,
                artifact=artifact, detail=str(meta.state),
            ))
        content = envelope.get("payload")
        raw = json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        digest = sha256(raw.encode("utf8")).hexdigest()
        if digest != meta.content_hash:
            issues.append(ArtifactWiringProblem(
                code="OUTPUT_HASH_MISMATCH", stage_id=stage.stage_id,
                artifact=artifact, detail="Persisted content does not match metadata",
            ))
    return issues
