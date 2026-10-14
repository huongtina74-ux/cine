"""Auto Edit: cut a finished episode from a Director Cut (tools/cf_director_cut.py).

    python tools/cf_auto_edit.py data/.../director_cut.json
    python tools/cf_auto_edit.py director_cut.json --preview          # fast 640x360 check
    python tools/cf_auto_edit.py director_cut.json --repo .           # synthesize Long Slide cue sounds

What it does, in order:
  1. validates the Director Cut (same rules as `cf_director_cut.py validate`);
  2. trims every shot, scales/pads it to the episode size and frame rate, burns optional
     on-screen text, and fades for dip-to-black cuts;
  3. joins shots with hard cuts or dissolves (xfade);
  4. builds the sound: source audio (when kept), voice-over (file, or local TTS through
     CF_TTS_COMMAND), sound effects (files, or Long Slide cue kinds from scripts/long_slide_audio.py),
     and a music bed that ducks automatically under the voice;
  5. masters to the target loudness (default -14 LUFS) and writes, next to the video:
     <name>.srt (subtitles from the VO lines), <name>.chapters.txt (YouTube chapters from the
     sections) and <name>.edit_report.json (timeline, overflows, warnings).

CF_TTS_COMMAND uses the same template as cinefactory.audio.tts.CommandTTS: the text arrives on
stdin and {output}, {language}, {voice} are replaced, e.g.
    set CF_TTS_COMMAND=piper --model voices\\en_US-amy-medium.onnx --output_file {output}
Only local tools are used (FFmpeg, numpy, Pillow). Nothing is uploaded.
Exit codes: 0 ok, 1 Director Cut invalid, 2 tool/ffmpeg failure.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):  # Windows consoles (cp1252) must not crash on Vietnamese/emoji text
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cf_director_cut as dcmod  # noqa: E402

SR = 48000
FONT_CANDIDATES = ("seguibl.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf")


class EditError(RuntimeError):
    pass


# ----------------------------------------------------------------------------- ffmpeg helpers
def ffmpeg(args: list[str]) -> None:
    proc = subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise EditError("ffmpeg failed: " + proc.stderr[-1500:])


def has_audio(path: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return bool(out.strip())


def decode_audio(path: Path, start: float = 0.0, duration: float | None = None) -> np.ndarray:
    """Any audio/video file -> float32 stereo (n, 2) at 48 kHz."""
    args = ["ffmpeg", "-nostdin", "-loglevel", "error"]
    if start:
        args += ["-ss", f"{start:.3f}"]
    args += ["-i", str(path)]
    if duration is not None:
        args += ["-t", f"{duration:.3f}"]
    args += ["-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    proc = subprocess.run(args, capture_output=True)
    if proc.returncode != 0:
        raise EditError(f"cannot decode audio {path}: {proc.stderr.decode(errors='ignore')[-500:]}")
    return np.frombuffer(proc.stdout, dtype=np.float32).reshape(-1, 2).copy()


def db(x: float) -> float:
    return float(10 ** (x / 20.0))


def place(bus: np.ndarray, clip: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(round(at * SR))
    if i >= len(bus) or len(clip) == 0:
        return
    if i < 0:
        clip, i = clip[-i:], 0
    n = min(len(clip), len(bus) - i)
    bus[i:i + n] += clip[:n] * gain


# ----------------------------------------------------------------------------- text overlay
def font(size: int):
    from PIL import ImageFont
    for name in FONT_CANDIDATES:
        for folder in (Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu"), Path("/Library/Fonts")):
            if (folder / name).is_file():
                return ImageFont.truetype(str(folder / name), size)
    return ImageFont.load_default(size)


def text_png(text: str, width: int, height: int, position: str, out: Path) -> Path:
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f = font(max(18, height // 14))
    lines = textwrap.wrap(text, width=max(10, int(width / (height // 14) * 1.7)))[:3]
    line_h = int(height // 14 * 1.25)
    block = line_h * len(lines)
    y0 = {"top": int(height * 0.08), "center": (height - block) // 2}.get(position, int(height * 0.80) - block)
    for k, line in enumerate(lines):
        x = (width - draw.textlength(line, font=f)) / 2
        draw.text((x, y0 + k * line_h), line, font=f, fill=(255, 255, 255, 255),
                  stroke_width=max(2, height // 240), stroke_fill=(0, 0, 0, 255))
    img.save(out)
    return out


# ----------------------------------------------------------------------------- video
def render_shots(dc: dict, dc_path: Path, work: Path, size: tuple[int, int], fps: int, crf: int, preset: str) -> list[Path]:
    w, h = size
    shots = dc["shots"]
    parts: list[Path] = []
    for i, shot in enumerate(shots):
        src = dcmod.resolve(dc_path, shot["source"])
        a, b = float(shot["in"]), float(shot["out"])
        dur = b - a
        vf = [f"scale={w}:{h}:force_original_aspect_ratio=decrease", f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black",
              f"fps={fps}", "setsar=1", "format=yuv420p"]
        if shot.get("cut") == "dip_black":
            vf.append(f"fade=t=in:st=0:d={float(shot['transition_seconds']) / 2:.3f}")
        nxt = shots[i + 1] if i + 1 < len(shots) else None
        if nxt is not None and nxt.get("cut") == "dip_black":
            d = float(nxt["transition_seconds"]) / 2
            vf.append(f"fade=t=out:st={max(0.0, dur - d):.3f}:d={d:.3f}")
        inputs = ["-ss", f"{a:.3f}", "-t", f"{dur:.3f}", "-i", str(src)]
        txt = shot.get("onscreen_text")
        if isinstance(txt, str):
            txt = {"text": txt}
        if txt and txt.get("text"):
            png = text_png(txt["text"], w, h, txt.get("position", "bottom"), work / f"{shot['id']}_text.png")
            at = float(txt.get("at", 0))
            until = at + float(txt.get("duration", dur - at))
            graph = (f"[0:v]{','.join(vf)}[base];[base][1:v]overlay=0:0:"
                     f"enable='between(t,{at:.3f},{until:.3f})'[v]")
            args = [*inputs, "-loop", "1", "-t", f"{dur:.3f}", "-i", str(png), "-filter_complex", graph, "-map", "[v]"]
        else:
            args = [*inputs, "-vf", ",".join(vf), "-map", "0:v:0"]
        out = work / f"{i:03d}_{shot['id']}.mp4"
        ffmpeg([*args, "-an", "-frames:v", str(max(1, int(round(dur * fps)))), "-c:v", "libx264",
                "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", str(out)])
        parts.append(out)
    return parts


def join_video(dc: dict, parts: list[Path], work: Path, out: Path, fps: int, crf: int, preset: str) -> None:
    shots = dc["shots"]
    if not any(s.get("cut") == "dissolve" for s in shots[1:]):
        listing = work / "concat.txt"
        listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        ffmpeg(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(out)])
        return
    inputs: list[str] = []
    for p in parts:
        inputs += ["-i", str(p)]
    chain, label, acc = [], "[0:v]", dcmod.shot_seconds(shots[0])
    for i in range(1, len(parts)):
        shot = shots[i]
        nxt = f"[x{i}]"
        if shot.get("cut") == "dissolve":
            d = float(shot["transition_seconds"])
            chain.append(f"{label}[{i}:v]xfade=transition=fade:duration={d:.3f}:offset={acc - d:.3f}{nxt}")
            acc += dcmod.shot_seconds(shot) - d
        else:
            chain.append(f"{label}[{i}:v]concat=n=2:v=1:a=0{nxt}")
            acc += dcmod.shot_seconds(shot)
        label = nxt
    chain.append(f"{label}fps={fps},format=yuv420p[v]")
    script = work / "join.txt"
    script.write_text(";\n".join(chain), encoding="utf-8")
    ffmpeg([*inputs, "-filter_complex_script", str(script), "-map", "[v]", "-c:v", "libx264", "-preset", preset,
            "-crf", str(crf), "-pix_fmt", "yuv420p", str(out)])


# ----------------------------------------------------------------------------- sound
def load_cue_synth(repo: Path | None):
    """Long Slide cue synthesizer from the CineFactory repo, when present."""
    candidates = [repo / "scripts" / "long_slide_audio.py"] if repo else []
    here = Path(__file__).resolve()
    candidates += [parent / "scripts" / "long_slide_audio.py" for parent in here.parents]
    for path in candidates:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("long_slide_audio", path)
            mod = importlib.util.module_from_spec(spec)
            sys.path.insert(0, str(path.parent))
            try:
                spec.loader.exec_module(mod)
                return mod
            except Exception:  # noqa: BLE001 - a broken optional synth must not stop the edit
                return None
    return None


def synth_kind(mod, kind: str, seed: int) -> np.ndarray | None:
    if mod is None or not hasattr(mod, "synth_cue"):
        return None
    try:
        mono = np.asarray(mod.synth_cue(kind, seed), dtype=np.float32)
    except (ValueError, KeyError):
        return None
    src_sr = int(getattr(mod, "SR", getattr(mod, "SAMPLE_RATE", SR)))
    if src_sr != SR and len(mono):
        x = np.linspace(0, len(mono) - 1, int(len(mono) * SR / src_sr))
        mono = np.interp(x, np.arange(len(mono)), mono).astype(np.float32)
    if mono.ndim == 2:
        return mono[:, :2] if mono.shape[1] >= 2 else np.repeat(mono, 2, axis=1)
    return np.stack([mono, mono], axis=1)


def synth_music(mod, seconds: float, seed: int) -> np.ndarray | None:
    """Original procedural music bed from the repo synth (scripts/long_slide_audio.py)."""
    if mod is None or not hasattr(mod, "synth_music"):
        return None
    try:
        stereo = np.asarray(mod.synth_music(seconds, seed), dtype=np.float32)
    except Exception:  # noqa: BLE001 - optional synth
        return None
    src_sr = int(getattr(mod, "SR", SR))
    if src_sr != SR and len(stereo):
        x = np.linspace(0, len(stereo) - 1, int(len(stereo) * SR / src_sr))
        stereo = np.stack([np.interp(x, np.arange(len(stereo)), stereo[:, c]) for c in range(2)], axis=1).astype(np.float32)
    return stereo


def tts(text: str, out: Path, language: str, voice: str) -> Path | None:
    template = os.environ.get("CF_TTS_COMMAND", "").strip()
    if not template:
        return None
    parts = [x.strip('"').strip("'") for x in shlex.split(template, posix=os.name != "nt")]
    argv = [part.format(output=str(out), language=language, voice=voice) for part in parts]
    proc = subprocess.run(argv, input=text, text=True, capture_output=True, timeout=900)
    if proc.returncode != 0 or not out.is_file():
        raise EditError(f"TTS failed for {out.name}: {proc.stderr[-500:]}")
    return out


def envelope(active: np.ndarray, attack: float = 0.12, release: float = 0.45) -> np.ndarray:
    """0..1 smoothed voice-activity curve (one value per sample)."""
    env = np.zeros(len(active), dtype=np.float32)
    up, down = 1.0 / max(1, int(attack * SR)), 1.0 / max(1, int(release * SR))
    level = 0.0
    step = 256  # block-wise for speed
    for i in range(0, len(active), step):
        target = 1.0 if active[i:i + step].any() else 0.0
        level = min(target, level + up * step) if target > level else max(target, level - down * step)
        env[i:i + step] = level
    return env


def build_sound(dc: dict, dc_path: Path, timeline: list[tuple[dict, float]], total: float, work: Path,
                repo: Path | None, report: dict) -> Path:
    n = int(total * SR) + SR
    bed = np.zeros((n, 2), dtype=np.float32)
    voice = np.zeros((n, 2), dtype=np.float32)
    synth = load_cue_synth(repo)
    vo_lines = []
    vo_dir = dc_path.parent / "vo"
    for idx, (shot, start) in enumerate(timeline):
        sid, dur = shot["id"], dcmod.shot_seconds(shot)
        src = dcmod.resolve(dc_path, shot["source"])
        if shot.get("keep_source_audio") and has_audio(src):
            place(bed, decode_audio(src, float(shot["in"]), dur), start, db(float(shot.get("source_gain_db") or 0)))
        vo = shot.get("vo") or {}
        text = (vo.get("text") or "").strip()
        audio = dcmod.resolve(dc_path, vo["audio"]) if vo.get("audio") else None
        if text and (audio is None or not audio.is_file()):
            vo_dir.mkdir(parents=True, exist_ok=True)
            audio = tts(text, vo_dir / f"{sid}.wav", dc.get("language", "en"), vo.get("speaker", "")) or None
            if audio is None:
                report["warnings"].append(f"{sid}: VO text has no audio (set CF_TTS_COMMAND or vo.audio); subtitles only")
        at = start + float(vo.get("offset") or 0)
        if audio is not None and audio.is_file():
            clip = decode_audio(audio) * db(float(vo.get("gain_db") or 0))
            place(voice, clip, at)
            vo_len = len(clip) / SR
            overflow = at + vo_len - (start + dur)
            if overflow > 0.05:
                report["warnings"].append(f"{sid}: VO runs {overflow:.2f}s past the end of the shot")
            vo_lines.append({"shot": sid, "start": at, "end": at + vo_len, "text": text})
        elif text:
            words = max(1, dcmod.words(text))
            est = words * 60.0 / float(dc.get("wpm") or 140)
            vo_lines.append({"shot": sid, "start": at, "end": min(at + est, start + dur), "text": text, "estimated": True})
        for k, fx in enumerate(shot.get("sfx") or []):
            t = start + float(fx.get("t", 0))
            gain = db(float(fx.get("gain_db", -6.0)))
            if fx.get("path"):
                p = dcmod.resolve(dc_path, fx["path"])
                if p.is_file():
                    place(bed, decode_audio(p), t, gain)
                else:
                    report["warnings"].append(f"{sid}: sfx file missing {p}")
            else:
                sound = synth_kind(synth, str(fx.get("kind")), idx * 31 + k)
                if sound is None:
                    report["missing_sfx_kinds"].add(str(fx.get("kind")))
                else:
                    place(bed, sound, t, gain)
    music = dc.get("music") or {}
    m = None
    if music.get("path"):
        mp = dcmod.resolve(dc_path, music["path"])
        if mp.is_file():
            m = decode_audio(mp)
        else:
            report["warnings"].append(f"music file missing: {mp}")
    elif music.get("synth"):
        m = synth_music(synth, total, int(music.get("seed") or 0))
        if m is None:
            report["warnings"].append(f"music synth '{music.get('synth')}' unavailable (pass --repo); no music bed")
    if m is not None and len(m):
        reps = int(np.ceil(n / len(m)))
        m = np.tile(m, (reps, 1))[:n]
        fade = int(1.5 * SR)
        ramp = np.linspace(0, 1, fade, dtype=np.float32)[:, None]
        m[:fade] *= ramp
        end = int(total * SR)
        m[max(0, end - fade):end] *= ramp[::-1][: end - max(0, end - fade)]
        m[end:] = 0
        active = np.abs(voice).max(axis=1) > 0.01
        duck = 1.0 - (1.0 - db(float(music.get("duck_db", -10.0)))) * envelope(active)
        bed += m * db(float(music.get("gain_db", -18.0))) * duck[:, None]
    mix = bed + voice
    peak = float(np.abs(mix).max() or 1.0)
    if peak > 0.98:
        mix *= 0.98 / peak  # loudnorm sets the final level; this only prevents clipping in the WAV
    wav = work / "mix.wav"
    pcm = (np.clip(mix, -1, 1) * 32767).astype("<i2")
    import wave
    with wave.open(str(wav), "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(SR)
        fh.writeframes(pcm.tobytes())
    report["vo_lines"] = vo_lines
    return wav


def measure_loudness(path: Path) -> dict | None:
    """Integrated loudness and true peak with the same meter cf_qc uses (ffmpeg ebur128)."""
    probe = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(path), "-map", "a:0", "-af",
                            "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    import re as _re
    i = _re.findall(r"I:\s*([-\d.]+) LUFS", probe.stderr)
    tp = _re.findall(r"Peak:\s*([-\d.]+) dBFS", probe.stderr)
    if not i:
        return None
    return {"i": float(i[-1]), "tp": float(tp[-1]) if tp else None}


def master(wav: Path, out: Path, lufs: float, report: dict, seconds: float | None = None) -> Path:
    """Hit the loudness target for real: gain to target, brick-wall limit below -1.5 dBTP, re-measure.

    A plain linear loudnorm cannot raise dense music (high peak-to-loudness) to -14 LUFS without
    breaking the true-peak ceiling, so it silently stops short (measured -16.1 on a Long Slide edit).
    Gain + limiter, measured again, converges within 0.5 LU in one or two passes.
    """
    if seconds:  # measure exactly what will be delivered (the mix carries 1 s of padding)
        trimmed = out.with_name(out.stem + ".trim.wav")
        ffmpeg(["-i", str(wav), "-t", f"{seconds:.3f}", str(trimmed)])
        wav = trimmed
    meas = measure_loudness(wav)
    if meas is None:
        report["warnings"].append("loudness measurement failed; used single-pass loudnorm")
        ffmpeg(["-i", str(wav), "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11", "-ar", str(SR), str(out)])
        return out
    report["loudness_input_lufs"] = meas["i"]
    gain = lufs - meas["i"]
    current = wav
    for attempt in range(3):
        step = out.with_name(f"{out.stem}.pass{attempt}.wav")
        ffmpeg(["-i", str(current), "-af",
                f"volume={gain:.2f}dB,alimiter=limit=0.79:level=false:attack=5:release=80:asc=1",
                "-ar", str(SR), str(step)])
        got = measure_loudness(step)
        if got is None:
            break
        report["loudness_output_lufs"], report["loudness_output_tp"] = got["i"], got["tp"]
        if abs(got["i"] - lufs) <= 0.5:
            current = step
            break
        gain, current = lufs - got["i"], step
    shutil.copyfile(current, out)
    return out


# ----------------------------------------------------------------------------- subtitles & chapters
def stamp(t: float, comma: bool = True) -> str:
    t = max(0.0, t)
    h, rem = divmod(int(t), 3600)
    m, s = divmod(rem, 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s, ms = s + 1, 0
    return f"{h:02d}:{m:02d}:{s:02d}{',' if comma else '.'}{ms:03d}"


def write_srt(lines: list[dict], path: Path, max_chars: int = 84) -> int:
    cues = []
    lines = sorted(lines, key=lambda x: x["start"])
    for k, line in enumerate(lines):  # a line never runs into the next one
        if k + 1 < len(lines) and line["end"] > lines[k + 1]["start"] - 0.05:
            line = {**line, "end": max(line["start"] + 0.5, lines[k + 1]["start"] - 0.05)}
        chunks = textwrap.wrap(line["text"], width=max_chars) or [line["text"]]
        span = line["end"] - line["start"]
        total_chars = sum(len(c) for c in chunks) or 1
        t = line["start"]
        for chunk in chunks:
            d = span * len(chunk) / total_chars
            cues.append((t, t + d, "\n".join(textwrap.wrap(chunk, width=max_chars // 2 + 2)[:2])))
            t += d
    path.write_text("".join(f"{i}\n{stamp(a)} --> {stamp(b)}\n{txt}\n\n" for i, (a, b, txt) in enumerate(cues, 1)),
                    encoding="utf-8")
    return len(cues)


def chapters(dc: dict, timeline: list[tuple[dict, float]], total: float) -> tuple[list[tuple[float, str]], list[str]]:
    labels = {s["id"]: s.get("label") or s["id"] for s in dc.get("sections", [])}
    marks: list[tuple[float, str]] = []
    for shot, start in timeline:
        sec = shot.get("section")
        if not marks or marks[-1][1] != labels.get(sec, sec):
            marks.append((start, labels.get(sec, sec)))
    if marks:
        marks[0] = (0.0, marks[0][1])
    issues = []
    if len(marks) < 3:
        issues.append("YouTube needs at least 3 chapters")
    ends = [m[0] for m in marks[1:]] + [total]
    short = [lab for (t, lab), e in zip(marks, ends) if e - t < 10]
    if short:
        issues.append("chapters shorter than 10s: " + ", ".join(short))
    return marks, issues


def mmss(t: float) -> str:
    m, s = divmod(int(t), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ----------------------------------------------------------------------------- main
def run(dc_path: Path, out: Path | None, preview: bool, repo: Path | None, keep: bool) -> int:
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            print(f"TOOL_ERROR::{tool} not on PATH")
            return 2
    dc = dcmod.load(dc_path)
    errors, warnings = dcmod.validate(dc, dc_path, strict=False)
    missing = [w for w in warnings if "not found" in w and ("source" in w)]
    if errors or missing:
        for e in errors + missing:
            print("ERROR::" + e)
        return 1
    fps = int(dc["fps"])
    size = (640, 360) if preview else (int(dc["width"]), int(dc["height"]))
    crf, preset = (28, "ultrafast") if preview else (18, "medium")
    name = dc.get("episode_id", "episode") + ("_preview" if preview else "_edit")
    out = out or (dc_path.parent / "edit" / f"{name}.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    report = {"director_cut": str(dc_path), "output": str(out), "preview": preview, "warnings": list(warnings),
              "missing_sfx_kinds": set()}
    timeline = dcmod.timeline(dc)
    total = dcmod.total_seconds(dc)
    work = Path(tempfile.mkdtemp(prefix="autoedit_", dir=out.parent))
    try:
        parts = render_shots(dc, dc_path, work, size, fps, crf, preset)
        video = work / "video.mp4"
        join_video(dc, parts, work, video, fps, crf, preset)
        wav = build_sound(dc, dc_path, timeline, total, work, repo, report)
        lufs = float(dc.get("loudness_lufs") or -14.0)
        mastered = master(wav, work / "master.wav", lufs, report, seconds=total)
        ffmpeg(["-i", str(video), "-i", str(mastered), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)])
        # Measure what actually ships; the AAC encode can move loudness by up to ~0.5 LU.
        final = measure_loudness(out)
        if final and abs(final["i"] - lufs) > 0.4:
            fixed = work / "master_fix.wav"
            ffmpeg(["-i", str(mastered), "-af", f"volume={lufs - final['i']:.2f}dB,"
                    "alimiter=limit=0.79:level=false:attack=5:release=80:asc=1", "-ar", str(SR), str(fixed)])
            ffmpeg(["-i", str(video), "-i", str(fixed), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)])
            final = measure_loudness(out)
        if final:
            report["delivered_lufs"], report["delivered_tp"] = final["i"], final["tp"]
    except EditError as exc:
        print("TOOL_ERROR::" + str(exc))
        return 2
    finally:
        if not keep:
            shutil.rmtree(work, ignore_errors=True)
    srt = out.with_suffix(".srt")
    n_cues = write_srt(report["vo_lines"], srt) if report["vo_lines"] else 0
    marks, chapter_issues = chapters(dc, timeline, total)
    out.with_suffix(".chapters.txt").write_text("".join(f"{mmss(t)} {lab}\n" for t, lab in marks), encoding="utf-8")
    report["warnings"] += chapter_issues
    report["missing_sfx_kinds"] = sorted(report["missing_sfx_kinds"])
    if report["missing_sfx_kinds"]:
        report["warnings"].append("sound effects skipped (no file and no synth): " + ", ".join(report["missing_sfx_kinds"]))
    report["seconds"] = round(total, 3)
    report["timeline"] = [{"shot": s["id"], "section": s.get("section"), "start": round(t, 3),
                           "end": round(t + dcmod.shot_seconds(s), 3), "cut": s.get("cut", "cut")} for s, t in timeline]
    report["chapters"] = [{"t": round(t, 3), "label": lab} for t, lab in marks]
    report["subtitle_cues"] = n_cues
    out.with_suffix(".edit_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for w in report["warnings"]:
        print("WARN::" + w)
    print(f"EDIT_OK::{out}::{total:.1f}s::shots={len(timeline)}::subs={n_cues}::chapters={len(marks)}")
    print("NEXT::python tools/cf_qc.py " + str(out))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dc", help="director_cut.json")
    p.add_argument("--out", default="")
    p.add_argument("--preview", action="store_true", help="640x360 fast render for checking the cut")
    p.add_argument("--repo", default="", help="CineFactory repo root (for Long Slide cue sounds)")
    p.add_argument("--keep-temp", action="store_true")
    args = p.parse_args(argv)
    return run(Path(args.dc).resolve(), Path(args.out).resolve() if args.out else None, args.preview,
               Path(args.repo).resolve() if args.repo else None, args.keep_temp)


if __name__ == "__main__":
    sys.exit(main())
