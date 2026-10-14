from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from cinefactory.core.policy import ExecutorDescriptor, FactoryPolicy


@dataclass
class ExecutionResult:
    ok: bool
    artifacts: list[str]
    metadata: dict[str, Any]
    error: str | None = None


class Executor(ABC):
    descriptor: ExecutorDescriptor

    def __init__(self, policy: FactoryPolicy) -> None:
        self.policy = policy

    def validate_policy(self) -> None:
        self.policy.check_executor(self.descriptor)

    @abstractmethod
    def execute(self, payload: dict[str, Any]) -> ExecutionResult:
        raise NotImplementedError
