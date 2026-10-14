from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .base import ReasoningProvider

T = TypeVar("T", bound=BaseModel)


class CommandReasoningBridge(ReasoningProvider):
    """Run a user-configured local CLI agent without hard-coding a vendor.

    The command receives one JSON request on stdin and MUST emit only JSON on stdout.
    Example configuration can point at a local OpenClaw/Codex wrapper controlled by the user.
    """

    def __init__(self, command: str, timeout_seconds: int = 900) -> None:
        self.argv = shlex.split(command)
        if not self.argv:
            raise ValueError("Reasoning command cannot be empty")
        self.timeout_seconds = timeout_seconds

    def generate(self, stage: str, prompt: str, schema: type[T], context: dict) -> T:
        request = json.dumps({
            "stage": stage,
            "prompt": prompt,
            "schema": schema.model_json_schema(),
            "context": context,
        }, ensure_ascii=False)
        proc = subprocess.run(
            self.argv,
            input=request,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Reasoning command failed ({proc.returncode}): {proc.stderr[-4000:]}")
        try:
            return schema.model_validate_json(proc.stdout)
        except Exception as exc:
            raise RuntimeError(f"Reasoning command returned invalid JSON/schema: {exc}") from exc
