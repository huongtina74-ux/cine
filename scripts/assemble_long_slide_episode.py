"""Assemble rendered Long Slide modules into one finished episode.

    python scripts/assemble_long_slide_episode.py --clips <dir with modules/*.mp4> \
        --title "Episode title" --brand "Zoomi Slide Club" --seed 7 --out episode.mp4

Builds an animated title card and end card (Pillow), cuts the module clips
together in order, synthesises the music bed and the sound effects from each
clip's `.events.json` sidecar (scripts/long_slide_audio.py), adds a whoosh on
every cut, and muxes everything with FFmpeg at YouTube loudness (-14 LUFS).
Only local tools are used.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import long_slide_audio as audio  # noqa: E402
from long_slide_events import sidecar_path  # noqa: E402

FONT_CANDIDATES = ("seguibl.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf")
RAINBOW = ((255, 82, 82), (255, 167, 38), (255, 235, 59), (102, 187, 106), (66, 165, 245), (171, 71, 188))
CARD_SECONDS = 3.0


def _font(size: int) -> ImageFont.FreeTypeFont:
    for name in FONT_CANDIDATES:
        for folder in (Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu"), Path("/Library/Fonts")):
            if (folder / name).is_file():
                return ImageFont.truetype(str(folder / name), size)
    return ImageFont.load_default(size)


def _wrap(draw, text, font, width):
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _ease_back(x: float) -> float:
    """0..1 with a small overshoot, for a bouncy pop-in."""
    x = min(max(x, 0.0), 1.0)
    c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def card_frame(size, headline, subline, brand, t, *, seed=0) -> Image.Image:
    w, h = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(h):  # sky gradient
        k = y / h
        draw.line([(0, y), (w, y)], fill=(int(90 + 120 * k), int(180 + 50 * k), 255))
    stripe = h // 9
    shift = int(t * 60) % (len(RAINBOW) * stripe)
    band_top = int(h * 0.78)
    for i in range(-2, 16):  # moving rainbow band, kept below the horizon line
        y0 = band_top + i * stripe // 3 - shift // 3
        y1 = y0 + stripe // 3
        if y1 <= band_top:
            continue
        draw.rectangle([0, max(y0, band_top), w, y1], fill=RAINBOW[(i + seed) % len(RAINBOW)])
    draw.rectangle([0, int(h * 0.78) - 4, w, int(h * 0.78)], fill=(255, 255, 255))
    for k in range(7):  # floating bubbles
        cx = int((k * 0.15 + 0.07) * w + 18 * math.sin(t * 2 + k))
        cy = int(h * (0.18 + 0.08 * (k % 3)) + 14 * math.cos(t * 2.4 + k))
        r = 14 + 6 * (k % 3)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RAINBOW[(k + seed) % len(RAINBOW)], outline=(255, 255, 255), width=3)
    scale = _ease_back(t / 0.6)
    if scale > 0.02:
        title_font = _font(max(8, int(h * 0.085 * scale)))
        lines = _wrap(draw, headline, title_font, int(w * 0.84))
        line_h = int(h * 0.1 * scale)
        top = int(h * 0.42) - line_h * len(lines) // 2
        for i, line in enumerate(lines):
            x = (w - draw.textlength(line, font=title_font)) / 2
            draw.text((x, top + i * line_h), line, font=title_font, fill=(255, 255, 255),
                      stroke_width=max(2, int(h * 0.008)), stroke_fill=(40, 40, 120))
    if t > 0.45 and subline:
        sub_font = _font(int(h * 0.05))
        x = (w - draw.textlength(subline, font=sub_font)) / 2
        draw.text((x, int(h * 0.64)), subline, font=sub_font, fill=(255, 245, 120), stroke_width=3, stroke_fill=(120, 40, 40))
    brand_font = _font(int(h * 0.04))
    bw = draw.textlength(brand, font=brand_font) + 40
    draw.rounded_rectangle([(w - bw) / 2, h * 0.05, (w + bw) / 2, h * 0.05 + h * 0.07], radius=20, fill=(255, 255, 255))
    draw.text(((w - bw) / 2 + 20, h * 0.058), brand, font=brand_font, fill=(230, 60, 120))
    return img


def render_card(path: Path, size, fps, headline, subline, brand, *, seed=0, seconds=CARD_SECONDS) -> Path:
    frames_dir = Path(tempfile.mkdtemp(prefix="card_", dir=path.parent))
    try:
        for i in range(int(seconds * fps)):
            card_frame(size, headline, subline, brand, i / fps, seed=seed).save(frames_dir / f"f{i:04d}.png")
        _ffmpeg(["-framerate", str(fps), "-i", str(frames_dir / "f%04d.png"),
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(path)])
    finally:
        shutil.rmtree(frames_dir, ignore_errors=True)
    return path


def require_tools() -> None:
    missing = [tool for tool in ("ffmpeg", "ffprobe") if shutil.which(tool) is None]
    if missing:
        raise RuntimeError(f"missing on PATH: {', '.join(missing)}")


def _ffmpeg(args: list[str]) -> None:
    result = subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-1500:]}")


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    num, den = data["streams"][0]["r_frame_rate"].split("/")
    return {"width": int(data["streams"][0]["width"]), "height": int(data["streams"][0]["height"]),
            "fps": round(int(num) / int(den)), "duration": float(data["format"]["duration"])}


def episode_cues(clips: list[Path], durations: list[float], intro: float) -> list[tuple[float, str]]:
    """Absolute (seconds, kind) cues: each clip's sidecar events plus a whoosh on every cut."""
    cues: list[tuple[float, str]] = [(0.25, "race_start")]
    offset = intro
    for clip, duration in zip(clips, durations):
        cues.append((max(0.0, offset - 0.2), "whoosh"))
        side = sidecar_path(clip)
        if side.is_file():
            data = json.loads(side.read_text(encoding="utf-8"))
            fps = float(data.get("fps") or 24)
            for event in data.get("events", []):
                time = offset + (int(event["frame"]) - 1) / fps
                if time < offset + duration:
                    cues.append((time, str(event["kind"])))
        offset += duration
    cues.append((offset + 0.2, "finish"))
    return sorted(cues)


def assemble(clips: list[Path], out: Path, *, title: str, brand: str, seed: int, subline: str = "") -> Path:
    if not clips:
        raise ValueError("no module clips to assemble")
    require_tools()
    info = probe(clips[0])
    size, fps = (info["width"], info["height"]), info["fps"]
    durations = [probe(c)["duration"] for c in clips]
    out.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="assemble_", dir=out.parent))
    try:
        intro = render_card(work / "intro.mp4", size, fps, title, subline or "Let's go!", brand, seed=seed)
        outro = render_card(work / "outro.mp4", size, fps, "Thanks for watching!", "See you next time!", brand, seed=seed + 1)
        parts = [intro, *clips, outro]
        total = CARD_SECONDS * 2 + sum(durations)
        wav = audio.write_wav(work / "mix.wav", audio.mix_episode(total, episode_cues(clips, durations, CARD_SECONDS), seed))
        inputs: list[str] = []
        chains = []
        for index, part in enumerate(parts):
            inputs += ["-i", str(part)]
            chains.append(f"[{index}:v]scale={size[0]}:{size[1]},fps={fps},format=yuv420p,setsar=1[v{index}]")
        joined = "".join(f"[v{i}]" for i in range(len(parts)))
        graph = ";\n".join(chains) + f";\n{joined}concat=n={len(parts)}:v=1:a=0[v]"
        # A script file keeps long episodes under the Windows command-line limit.
        script = work / "graph.txt"
        script.write_text(graph, encoding="utf-8")
        _ffmpeg([*inputs, "-i", str(wav), "-filter_complex_script", str(script), "-map", "[v]",
                 "-map", f"{len(parts)}:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                 "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",
                 "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--clips", required=True, help="folder with module clips (searched recursively for *.mp4)")
    parser.add_argument("--title", required=True)
    parser.add_argument("--brand", required=True)
    parser.add_argument("--subline", default="")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    clips = sorted(
        p for p in Path(args.clips).rglob("*.mp4")
        if not p.name.startswith("episode") and not any(part.startswith(("assemble_", "card_")) for part in p.parts)
    )
    out = assemble(clips, Path(args.out), title=args.title, brand=args.brand, seed=args.seed, subline=args.subline)
    print("EPISODE_OK::" + str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
