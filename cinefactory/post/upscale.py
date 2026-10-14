from __future__ import annotations

import shlex
import subprocess
from pathlib import Path


class CommandUpscaler:
    """Local perceptual upscaler bridge.

    The command template may use {input}, {output}, {width}, {height}. No shell is used.
    This allows Real-ESRGAN/Video2X/ComfyUI wrappers or another reviewed local tool
    without coupling CineFactory to one model.
    """

    def __init__(self, command_template: str, timeout: int = 7200) -> None:
        self.argv = shlex.split(command_template)
        self.timeout = timeout
        if not self.argv:
            raise ValueError("upscale command cannot be empty")

    def run(self, source: str | Path, output: str | Path, *, width: int, height: int) -> Path:
        src = Path(source).resolve(); out = Path(output).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
        mapping = {"input": str(src), "output": str(out), "width": str(width), "height": str(height)}
        argv = [part.format(**mapping) for part in self.argv]
        proc = subprocess.run(argv, text=True, capture_output=True, timeout=self.timeout, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"Local upscaler failed: {proc.stderr[-4000:]}")
        if not out.is_file():
            raise RuntimeError(f"Local upscaler did not produce {out}")
        return out
