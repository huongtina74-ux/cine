from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from cinefactory.media.ffmpeg import FFmpegToolchain, MediaProbe


@dataclass
class TechnicalQCResult:
    passed: bool
    findings: list[str] = field(default_factory=list)
    probe: MediaProbe | None = None


class TechnicalQC:
    def __init__(self, media: FFmpegToolchain | None = None) -> None:
        self.media = media or FFmpegToolchain()

    def video(self, path: str | Path, *, min_duration: float = 0.25, require_audio: bool = False) -> TechnicalQCResult:
        p = Path(path)
        findings: list[str] = []
        if not p.is_file() or p.stat().st_size == 0:
            return TechnicalQCResult(False, ["OUTPUT_MISSING"])
        try:
            probe = self.media.probe(p)
        except Exception as exc:
            return TechnicalQCResult(False, [f"DECODE_FAIL:{exc}"])
        if probe.duration < min_duration:
            findings.append("DURATION_TOO_SHORT")
        if not probe.width or not probe.height:
            findings.append("VIDEO_STREAM_MISSING")
        if not probe.fps or probe.fps <= 0:
            findings.append("FPS_INVALID")
        if require_audio and not probe.audio_codec:
            findings.append("AUDIO_STREAM_MISSING")
        return TechnicalQCResult(not findings, findings, probe)
