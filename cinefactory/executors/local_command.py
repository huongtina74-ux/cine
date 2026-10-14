from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any

from cinefactory.core.policy import ExecutorDescriptor
from cinefactory.domain.enums import ExecutorKind, NetworkScope
from cinefactory.executors.base import ExecutionResult, Executor


class LocalCommandExecutor(Executor):
    """Generic network-free adapter for local ASR/TTS/upscale/QC tools.

    It does not invoke a shell; argv is parsed once and appended with payload-provided args.
    Production should register only reviewed commands.
    """

    def __init__(self, policy, executor_id: str, command: str, category: str, timeout: int = 3600) -> None:
        self.descriptor = ExecutorDescriptor(
            executor_id=executor_id, kind=ExecutorKind.LOCAL, category=category, network_scope=NetworkScope.NONE,
            notes="Reviewed local command; no shell and no network fallback.",
        )
        super().__init__(policy)
        self.argv = shlex.split(command)
        if not self.argv:
            raise ValueError("command cannot be empty")
        self.timeout = timeout

    def execute(self, payload: dict[str, Any]) -> ExecutionResult:
        self.validate_policy()
        args = payload.get("args", [])
        if not isinstance(args, list) or not all(isinstance(x, str) for x in args):
            return ExecutionResult(False, [], {}, "payload.args must be list[str]")
        proc = subprocess.run(self.argv + args, text=True, capture_output=True, timeout=self.timeout, check=False)
        artifacts = [str(Path(p)) for p in payload.get("artifacts", []) if Path(p).exists()]
        meta = {"returncode": proc.returncode, "stdout": proc.stdout[-8000:], "stderr": proc.stderr[-8000:]}
        return ExecutionResult(proc.returncode == 0, artifacts, meta, None if proc.returncode == 0 else f"command exit {proc.returncode}")
