from cinefactory.core.job_lifecycle import JobLifecycle
from cinefactory.domain.enums import FailureCode, JobState
from cinefactory.domain.models import RenderJob


def job(max_attempts=3):
    return RenderJob(
        project_id="P",
        job_type="VIDEO",
        executor_id="local.mock",
        workflow_id="w",
        workflow_version="1",
        dependency_hash="h",
        max_attempts=max_attempts,
    )


def test_retryable_failure_goes_to_retry():
    lifecycle = JobLifecycle()
    j, _ = lifecycle.start(job())
    decision = lifecycle.fail(j, FailureCode.GPU_OOM, "oom")
    assert decision.retry is True
    assert j.state == JobState.RETRY


def test_rights_failure_hard_blocks():
    lifecycle = JobLifecycle()
    j, _ = lifecycle.start(job())
    decision = lifecycle.fail(j, FailureCode.RIGHTS_FAIL, "not cleared")
    assert decision.retry is False
    assert j.state == JobState.BLOCKED


def test_retry_budget_goes_to_dlq():
    lifecycle = JobLifecycle()
    j, _ = lifecycle.start(job(max_attempts=1))
    decision = lifecycle.fail(j, FailureCode.GPU_OOM, "oom")
    assert decision.retry is False
    assert j.state == JobState.DEAD_LETTER
