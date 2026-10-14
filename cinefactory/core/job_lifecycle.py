from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from cinefactory.domain.enums import FailureCode, JobState
from cinefactory.domain.models import JobAttempt, RenderJob


RETRYABLE_FAILURES = {
    FailureCode.TRANSIENT_EXECUTOR,
    FailureCode.GPU_OOM,
    FailureCode.PROMPT_FORMAT,
    FailureCode.IDENTITY_DRIFT,
    FailureCode.CONTINUITY_FAIL,
    FailureCode.CAMERA_INTENT_FAIL,
    FailureCode.PERFORMANCE_FAIL,
    FailureCode.ACTION_FAIL,
    FailureCode.TECHNICAL_FAIL,
    FailureCode.MODEL_CAPABILITY,
    FailureCode.OUTPUT_MISSING,
}

HARD_STOP_FAILURES = {
    FailureCode.RIGHTS_FAIL,
    FailureCode.SECURITY_FAIL,
    FailureCode.COST_POLICY_FAIL,
    FailureCode.WORKFLOW_MISSING,
}


class InvalidJobTransition(RuntimeError):
    pass


@dataclass(frozen=True)
class RetryDecision:
    retry: bool
    next_state: JobState
    reason: str


class JobLifecycle:
    def start(self, job: RenderJob, worker_id: str | None = None) -> tuple[RenderJob, JobAttempt]:
        if job.state not in {JobState.QUEUED, JobState.RETRY}:
            raise InvalidJobTransition(f"Cannot start job from {job.state}")
        job.attempt += 1
        job.state = JobState.RUNNING
        job.started_at = datetime.now(timezone.utc)
        job.finished_at = None
        attempt = JobAttempt(
            job_id=job.job_id,
            attempt_number=job.attempt,
            state=JobState.RUNNING,
            worker_id=worker_id,
            started_at=job.started_at,
        )
        return job, attempt

    def succeed(self, job: RenderJob, artifact_ids: list[str]) -> RenderJob:
        if job.state is not JobState.RUNNING:
            raise InvalidJobTransition(f"Cannot succeed job from {job.state}")
        job.state = JobState.SUCCESS
        job.failure_code = None
        job.error_detail = None
        job.output_artifact_ids = list(dict.fromkeys([*job.output_artifact_ids, *artifact_ids]))
        job.finished_at = datetime.now(timezone.utc)
        return job

    def fail(self, job: RenderJob, code: FailureCode, detail: str) -> RetryDecision:
        if job.state is not JobState.RUNNING:
            raise InvalidJobTransition(f"Cannot fail job from {job.state}")
        job.failure_code = code
        job.error_detail = detail
        job.finished_at = datetime.now(timezone.utc)

        if code in HARD_STOP_FAILURES:
            job.state = JobState.BLOCKED
            return RetryDecision(False, JobState.BLOCKED, f"hard-stop failure: {code.value}")

        if code in RETRYABLE_FAILURES and job.attempt < job.max_attempts:
            job.state = JobState.RETRY
            return RetryDecision(True, JobState.RETRY, f"retryable failure: {code.value}")

        job.state = JobState.DEAD_LETTER
        return RetryDecision(False, JobState.DEAD_LETTER, "retry budget exhausted or failure is not retryable")
