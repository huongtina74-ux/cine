from __future__ import annotations

from cinefactory.executors.base import Executor


class ExecutorRegistry:
    def __init__(self) -> None:
        self._executors: dict[str, Executor] = {}

    def register(self, executor: Executor) -> None:
        executor.validate_policy()
        if executor.descriptor.executor_id in self._executors:
            raise ValueError(f"Duplicate executor: {executor.descriptor.executor_id}")
        self._executors[executor.descriptor.executor_id] = executor

    def get(self, executor_id: str) -> Executor:
        try:
            return self._executors[executor_id]
        except KeyError as exc:
            raise KeyError(f"Unknown executor: {executor_id}") from exc

    def ids(self) -> list[str]:
        return sorted(self._executors)
