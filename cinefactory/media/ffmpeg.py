from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MediaProbe:
    path: str
    duration: float
    width: int | None
    height: int | None
    fps: float | None
    video_codec: str | None
    audio_codec: str | None
    sample_rate: int | None
    channels: int | None


class FFmpegToolchain:
    def __init__(self, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe") -> None:
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe

    def _run(self, argv: list[str], timeout: int = 3600) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(argv, text=True, capture_output=True, timeout=timeout, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"Command failed: {shlex.join(argv)}\n{proc.stderr[-8000:]}")
        return proc

    @staticmethod
    def _fps(value: str | None) -> float | None:
        if not value or value == "0/0":
            return None
        if "/" in value:
            a, b = value.split("/", 1)
            return float(a) / float(b) if float(b) else None
        return float(value)

    def probe(self, path: str | Path) -> MediaProbe:
        p = Path(path).resolve()
        proc = self._run([
            self.ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(p)
        ], timeout=60)
        data = json.loads(proc.stdout)
        video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
        audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
        duration = float(data.get("format", {}).get("duration") or (video or {}).get("duration") or 0)
        return MediaProbe(
            path=str(p), duration=duration,
            width=(video or {}).get("width"), height=(video or {}).get("height"),
            fps=self._fps((video or {}).get("avg_frame_rate")),
            video_codec=(video or {}).get("codec_name"), audio_codec=(audio or {}).get("codec_name"),
            sample_rate=int(audio["sample_rate"]) if audio and audio.get("sample_rate") else None,
            channels=(audio or {}).get("channels"),
        )

    def extract_frame(
        self,
        source: str | Path,
        output: str | Path,
        *,
        time_seconds: float,
    ) -> Path:
        src = Path(source).resolve()
        out = Path(output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        self._run([
            self.ffmpeg,
            "-y",
            "-i",
            str(src),
            "-ss",
            f"{max(0.0, float(time_seconds)):.6f}",
            "-frames:v",
            "1",
            "-an",
            str(out),
        ], timeout=120)
        if not out.is_file():
            raise RuntimeError(f"ffmpeg did not create frame: {out}")
        return out

    def concat(self, clips: list[str | Path], output: str | Path, *, fps: float = 24.0) -> Path:
        if not clips:
            raise ValueError("concat requires at least one clip")
        out = Path(output).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
        list_path = out.with_suffix(out.suffix + ".concat.txt")
        lines = []
        for clip in clips:
            path = str(Path(clip).resolve()).replace("'", "'\\''")
            lines.append(f"file '{path}'")
        list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        try:
            # Re-encode for robust mixed local-model outputs.
            self._run([
                self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
                "-r", str(fps), "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)
            ])
        finally:
            list_path.unlink(missing_ok=True)
        return out

    def master_audio(
        self,
        source: str | Path,
        output: str | Path,
        *,
        target_lufs: float = -16.0,
        true_peak_db: float = -1.5,
        loudness_range: float = 11.0,
        speech_denoise: bool = False,
    ) -> Path:
        src = Path(source).resolve()
        out = Path(output).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        probe = self.probe(src)
        if probe.audio_codec is None:
            shutil.copy2(src, out)
            return out
        loudnorm = (
            f"loudnorm=I={target_lufs}:TP={true_peak_db}:"
            f"LRA={loudness_range}"
        )
        audio_filter = (
            f"afftdn=nf=-25,{loudnorm}"
            if speech_denoise
            else loudnorm
        )
        self._run([
            self.ffmpeg, "-y", "-i", str(src),
            "-map", "0:v?", "-map", "0:a?",
            "-c:v", "copy", "-af", audio_filter,
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-movflags", "+faststart", str(out),
        ])
        return out

    def master_4k(self, source: str | Path, output: str | Path, *, width: int = 3840, height: int = 2160, fps: float = 24.0) -> Path:
        src = Path(source).resolve(); out = Path(output).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
        vf = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps={fps}"
        )
        self._run([
            self.ffmpeg, "-y", "-i", str(src), "-vf", vf,
            "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(out)
        ])
        return out


    def make_image_slate(self, text: str, output: str | Path, size: str = "1024x1024") -> Path:
        out = Path(output).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
        safe = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        draw = f"drawtext=text='{safe}':fontcolor=white:fontsize=34:x=(w-text_w)/2:y=(h-text_h)/2"
        self._run([
            self.ffmpeg, "-y", "-f", "lavfi", "-i", f"color=c=0x181818:s={size}",
            "-vf", draw, "-frames:v", "1", str(out)
        ], timeout=120)
        return out

    def make_slate(self, text: str, output: str | Path, duration: float = 2.0, size: str = "1280x720", fps: float = 24.0) -> Path:
        out = Path(output).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
        safe = text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        draw = f"drawtext=text='{safe}':fontcolor=white:fontsize=42:x=(w-text_w)/2:y=(h-text_h)/2"
        self._run([
            self.ffmpeg, "-y", "-f", "lavfi", "-i", f"color=c=0x111111:s={size}:r={fps}:d={duration}",
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={duration}",
            "-vf", draw, "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out)
        ], timeout=120)
        return out
