from pathlib import Path
import subprocess

from cinefactory.block_animation.visual_qc import BlockVisualQC


def test_visual_qc_passes_moving_test_pattern(tmp_path):
    out = tmp_path / "moving.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=1.2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)
    ], check=True)
    result = BlockVisualQC().review(out)
    assert result.passed, result.findings


def test_visual_qc_flags_black_render(tmp_path):
    out = tmp_path / "black.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=black:size=320x180:rate=24:duration=1.2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)
    ], check=True)
    result = BlockVisualQC().review(out)
    assert not result.passed
    assert "EXCESSIVE_BLACK_FRAMES" in result.findings
