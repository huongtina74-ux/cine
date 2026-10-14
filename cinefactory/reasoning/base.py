from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ReasoningProvider(ABC):
    """Boundary between paid/agent reasoning and deterministic factory execution."""

    @abstractmethod
    def generate(self, stage: str, prompt: str, schema: type[T], context: dict) -> T:
        raise NotImplementedError
