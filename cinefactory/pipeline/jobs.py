from __future__ import annotations

from datetime import datetime, timezone

from cinefactory.core.job_lifecycle import JobLifecycle
from cinefactory.domain.enums import FailureCode, JobState
from cinefactory.domain.models import AuditEvent, JobAttempt, RenderJob
from cinefactory.executors.registry import ExecutorRegistry
from cinefactory.storage.database import AuditLogRepository, JobLedgerRepository
from cinefactory.workflows.registry import WorkflowRegistry


class JobService:
    def __init__(
        self,
        ledger: JobLedgerRepository,
        audit: AuditLogRepository,
        executors: ExecutorRegistry,
        workflows: WorkflowRegistry | None = None,
    ) -> None:
        self.ledger = ledger
        self.audit = audit
        self.executors = executors
        self.workflows = workflows
        self.lifecycle = JobLifecycle()

    def enqueue(self, job: RenderJob) -> tuple[RenderJob, bool]:
        # Executor lookup enforces that only registered/approved executors can be enqueued.
        self.executors.get(job.executor_id).validate_policy()
        if self.workflows is not None:
            manifest = self.workflows.get(job.workflow_id, job.workflow_version)
            if manifest.executor_id != job.executor_id:
                raise ValueError(
                    f"Workflow {job.workflow_id}@{job.workflow_version} belongs to {manifest.executor_id}, not {job.executor_id}"
                )
            if not manifest.local_only:
                raise ValueError(f"Workflow {job.workflow_id}@{job.workflow_version} is not approved local-only")
        result, created = self.ledger.create_or_get(job)
        if created:
            self.audit.append(
                AuditEvent(
                    project_id=job.project_id,
                    event_type="JOB_ENQUEUED",
                    actor="factory-core",
                    entity_type="job",
                    entity_id=job.job_id,
                    payload={"idempotency_key": job.idempotency_key, "executor": job.executor_id},
                )
            )
        return result, created

    def execute_now(self, job_id: str, worker_id: str = "local-inline") -> RenderJob:
        job = self.ledger.get(job_id)
        executor = self.executors.get(job.executor_id)
        job, attempt = self.lifecycle.start(job, worker_id=worker_id)
        self.ledger.save(job)
        self.ledger.append_attempt(attempt)

        try:
            result = executor.execute(job.payload)
        except Exception as exc:  # Adapter boundary: exceptions are converted to typed transient failures.
            result = None
            detail = str(exc)
        else:
            detail = result.error or "executor returned failure"

        if result is not None and result.ok:
            self.lifecycle.succeed(job, result.artifacts)
            attempt.state = JobState.SUCCESS
            attempt.finished_at = datetime.now(timezone.utc)
            attempt.metadata = result.metadata
            self.ledger.save(job)
            # append immutable terminal attempt record rather than mutating the RUNNING attempt row
            terminal = JobAttempt(
                job_id=job.job_id,
                attempt_number=job.attempt,
                state=JobState.SUCCESS,
                worker_id=worker_id,
                started_at=attempt.started_at,
                finished_at=attempt.finished_at,
                metadata=result.metadata,
            )
            self.ledger.append_attempt(terminal)
            self.audit.append(
                AuditEvent(
                    project_id=job.project_id,
                    event_type="JOB_SUCCEEDED",
                    actor=worker_id,
                    entity_type="job",
                    entity_id=job.job_id,
                    payload={"artifact_ids": job.output_artifact_ids},
                )
            )
            return job

        decision = self.lifecycle.fail(job, FailureCode.TRANSIENT_EXECUTOR, detail)
        self.ledger.save(job)
        terminal = JobAttempt(
            job_id=job.job_id,
            attempt_number=job.attempt,
            state=job.state,
            worker_id=worker_id,
            failure_code=job.failure_code,
            error_detail=job.error_detail,
            started_at=attempt.started_at,
            finished_at=job.finished_at,
        )
        self.ledger.append_attempt(terminal)
        self.audit.append(
            AuditEvent(
                project_id=job.project_id,
                event_type="JOB_FAILED",
                actor=worker_id,
                entity_type="job",
                entity_id=job.job_id,
                payload={"failure_code": job.failure_code.value if job.failure_code else None, "next": decision.next_state.value},
            )
        )
        return job
