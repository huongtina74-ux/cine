from __future__ import annotations

import shlex
import subprocess
from pathlib import Path


class LocalTTS:
    def synthesize(self, text: str, output: str | Path, *, language: str = "en", voice: str | None = None) -> Path:
        raise NotImplementedError


class EspeakTTS(LocalTTS):
    """Diagnostic zero-network TTS fallback. Production can replace it with CosyVoice/Piper."""

    def __init__(self, command: str = "espeak") -> None:
        self.command = command

    def synthesize(self, text: str, output: str | Path, *, language: str = "en", voice: str | None = None) -> Path:
        out = Path(output).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
        selected = voice or language
        proc = subprocess.run([self.command, "-v", selected, "-w", str(out), text], text=True, capture_output=True, check=False, timeout=300)
        if proc.returncode != 0:
            raise RuntimeError(f"espeak failed: {proc.stderr[-4000:]}")
        return out


class CommandTTS(LocalTTS):
    """Vendor-neutral local TTS command bridge.

    Command receives text on stdin. `{output}`, `{language}`, `{voice}` tokens in argv are replaced.
    No shell is used.
    """

    def __init__(self, command_template: str, timeout: int = 900) -> None:
        self.argv = shlex.split(command_template); self.timeout = timeout
        if not self.argv: raise ValueError("TTS command cannot be empty")

    def synthesize(self, text: str, output: str | Path, *, language: str = "en", voice: str | None = None) -> Path:
        out = Path(output).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
        mapping={"output":str(out),"language":language,"voice":voice or ""}
        argv=[part.format(**mapping) for part in self.argv]
        proc=subprocess.run(argv,input=text,text=True,capture_output=True,timeout=self.timeout,check=False)
        if proc.returncode!=0: raise RuntimeError(f"Local TTS command failed: {proc.stderr[-4000:]}")
        if not out.is_file(): raise RuntimeError(f"Local TTS did not produce {out}")
        return out
