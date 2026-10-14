from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol

from cinefactory.core.policy import FactoryPolicy, PolicyViolation
from cinefactory.core.state_machine import require_transition
from cinefactory.domain.enums import ProjectState
from cinefactory.domain.models import AuditEvent, ProjectRecord, ProjectSpec


class ProjectRepository(Protocol):
    def save(self, record: ProjectRecord) -> None: ...
    def get(self, project_id: str) -> ProjectRecord: ...


class AuditRepository(Protocol):
    def append(self, event: AuditEvent) -> None: ...


class PipelineOrchestrator:
    def __init__(self, policy: FactoryPolicy, repository: ProjectRepository, audit: AuditRepository | None = None) -> None:
        self.policy = policy
        self.repository = repository
        self.audit = audit

    def _event(self, project_id: str, event_type: str, entity_type: str, entity_id: str, payload: dict) -> None:
        if self.audit is not None:
            self.audit.append(
                AuditEvent(
                    project_id=project_id,
                    event_type=event_type,
                    actor="factory-core",
                    entity_type=entity_type,
                    entity_id=entity_id,
                    payload=payload,
                )
            )

    def create_project(self, spec: ProjectSpec) -> ProjectRecord:
        self.policy.assert_project_cost_policy(
            spec.cost_policy.paid_generation_api_allowed,
            spec.cost_policy.cloud_generation_fallback,
        )
        record = ProjectRecord(spec=spec)
        self.repository.save(record)
        self._event(spec.project_id, "PROJECT_CREATED", "project", spec.project_id, {"profile": spec.profile})
        return record

    def transition(self, project_id: str, target: ProjectState) -> ProjectRecord:
        record = self.repository.get(project_id)
        require_transition(record.state, target)
        before = record.state
        record.state = target
        record.updated_at = datetime.now(timezone.utc)
        self.repository.save(record)
        self._event(project_id, "PROJECT_STATE_CHANGED", "project", project_id, {"from": before.value, "to": target.value})
        return record


    def block(self, project_id: str, reason: str) -> ProjectRecord:
        record = self.repository.get(project_id)
        if record.state is not ProjectState.ARCHIVED:
            record.state = ProjectState.BLOCKED
            record.blocked_reason = reason
            record.updated_at = datetime.now(timezone.utc)
            self.repository.save(record)
            self._event(project_id, "PROJECT_BLOCKED", "project", project_id, {"reason": reason})
        return record

    def policy_check(self, project_id: str) -> ProjectRecord:
        record = self.repository.get(project_id)
        try:
            self.policy.assert_project_cost_policy(
                record.spec.cost_policy.paid_generation_api_allowed,
                record.spec.cost_policy.cloud_generation_fallback,
            )
        except PolicyViolation as exc:
            record.state = ProjectState.BLOCKED
            record.blocked_reason = str(exc)
            record.updated_at = datetime.now(timezone.utc)
            self.repository.save(record)
            self._event(project_id, "PROJECT_BLOCKED", "project", project_id, {"reason": str(exc)})
            return record
        return self.transition(project_id, ProjectState.POLICY_CHECKED)
