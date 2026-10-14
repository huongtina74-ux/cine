from __future__ import annotations

from pathlib import Path

from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.qc.technical import TechnicalQC, TechnicalQCResult
from cinefactory.post.upscale import CommandUpscaler


class MasteringService:
    def __init__(self, media: FFmpegToolchain | None = None) -> None:
        self.media = media or FFmpegToolchain()
        self.qc = TechnicalQC(self.media)

    def master(self, source: str | Path, output: str | Path, *, width: int = 3840, height: int = 2160, fps: float = 24.0, upscaler: CommandUpscaler | None = None) -> tuple[Path, TechnicalQCResult]:
        src = Path(source).resolve()
        if upscaler is not None:
            restored = Path(output).resolve().with_name(Path(output).stem + ".restored.mp4")
            src = upscaler.run(src, restored, width=width, height=height)
        out = self.media.master_4k(src, output, width=width, height=height, fps=fps)
        result = self.qc.video(out, require_audio=False)
        if result.probe and (result.probe.width != width or result.probe.height != height):
            result.findings.append("MASTER_RESOLUTION_MISMATCH")
            result.passed = False
        return out, result
