from __future__ import annotations

from cinefactory.core.policy import ExecutorDescriptor
from cinefactory.domain.enums import ExecutorKind, NetworkScope
from cinefactory.executors.base import ExecutionResult, Executor


class LocalMockExecutor(Executor):
    """Development-only executor proving the local-only policy path without calling any external API."""

    descriptor = ExecutorDescriptor(
        executor_id="local.mock",
        kind=ExecutorKind.LOCAL,
        category="development",
        network_scope=NetworkScope.NONE,
    )

    def execute(self, payload: dict) -> ExecutionResult:
        self.validate_policy()
        return ExecutionResult(ok=True, artifacts=[], metadata={"echo": payload, "network": False})
