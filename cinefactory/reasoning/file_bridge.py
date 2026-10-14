from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .base import ReasoningProvider

T = TypeVar("T", bound=BaseModel)


class FileReasoningBridge(ReasoningProvider):
    """Offline bridge for OpenClaw/Codex/manual agent reasoning.

    The factory writes stage requests under `requests/`. An external agent may write
    schema-valid JSON under `responses/<stage>.json`. This avoids embedding any paid API
    credentials inside the production runtime.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        (self.root / "requests").mkdir(parents=True, exist_ok=True)
        (self.root / "responses").mkdir(parents=True, exist_ok=True)

    def generate(self, stage: str, prompt: str, schema: type[T], context: dict) -> T:
        request = {
            "stage": stage,
            "prompt": prompt,
            "schema": schema.model_json_schema(),
            "context": context,
        }
        (self.root / "requests" / f"{stage}.json").write_text(
            json.dumps(request, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        response_path = self.root / "responses" / f"{stage}.json"
        if not response_path.exists():
            raise RuntimeError(
                f"Reasoning response missing: {response_path}. Run your reasoning agent, "
                "write schema-valid JSON there, then resume the project."
            )
        return schema.model_validate_json(response_path.read_text(encoding="utf-8"))
