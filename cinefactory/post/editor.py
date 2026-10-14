from __future__ import annotations

from pathlib import Path

from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.post.timeline import TimelineSpec


class AutoEditor:
    """Deterministic fallback editor. OpenChatCut can replace this through a later bridge."""

    def __init__(self, media: FFmpegToolchain | None = None) -> None:
        self.media = media or FFmpegToolchain()

    def render_rough_cut(self, timeline: TimelineSpec, output: str | Path) -> Path:
        ordered = sorted(timeline.clips, key=lambda c: c.order)
        # v1 fallback supports full-clip hard cuts. Trim/transition semantics remain in the
        # TimelineSpec for OpenChatCut/advanced renderers.
        return self.media.concat([c.path for c in ordered], output, fps=timeline.fps)
