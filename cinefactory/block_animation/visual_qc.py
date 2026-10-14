from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from cinefactory.media.ffmpeg import FFmpegToolchain


@dataclass
class BlockVisualQCResult:
    passed: bool
    findings: list[str] = field(default_factory=list)
    black_seconds: float = 0.0
    freeze_seconds: float = 0.0


class BlockVisualQC:
    """Zero-API media QC using FFmpeg signal detectors.

    This catches broken/black/frozen renders locally. Semantic visual defects such as
    hand contact or facial quality can be delegated to CommandVisualQC when a local VLM
    is configured; this class intentionally never calls the network.
    """

    def __init__(self, ffmpeg: FFmpegToolchain | None = None):
        self.media = ffmpeg or FFmpegToolchain()

    def review(self, path: str | Path, *, max_black_ratio: float = .08, max_freeze_ratio: float = .25) -> BlockVisualQCResult:
        p = Path(path).resolve()
        probe = self.media.probe(p)
        findings: list[str] = []
        if probe.duration <= 0:
            return BlockVisualQCResult(False, ["ZERO_DURATION"])

        cmd = [
            self.media.ffmpeg, "-hide_banner", "-nostats", "-i", str(p),
            "-vf", "blackdetect=d=0.15:pix_th=0.08,freezedetect=n=-50dB:d=0.5",
            "-an", "-f", "null", "-",
        ]
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=300)
        log = proc.stderr or ""
        black = sum(float(x) for x in re.findall(r"black_duration:([0-9.]+)", log))
        freeze = sum(float(x) for x in re.findall(r"freeze_duration:([0-9.]+)", log))
        if black / probe.duration > max_black_ratio:
            findings.append("EXCESSIVE_BLACK_FRAMES")
        if freeze / probe.duration > max_freeze_ratio:
            findings.append("EXCESSIVE_FROZEN_FRAMES")
        return BlockVisualQCResult(not findings, findings, black_seconds=black, freeze_seconds=freeze)
