#!/usr/bin/env python3
"""Fast "watch" of long videos/livestreams: download AUDIO only -> local Whisper on GPU -> transcript -> Claude summary.

No real-time playback: a 1h30 Facebook/YouTube livestream is usually
  ~1 min download (audio only)  +  ~3-8 min transcription on an RTX 3060 (faster-whisper large-v3-turbo)
  +  ~1 min summary with Claude Code (optional).

Install once (PowerShell):
    pip install -U yt-dlp faster-whisper
    # GPU (recommended). If CUDA libs are missing, the script falls back to CPU automatically:
    pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"
    # ffmpeg must be on PATH (you already have it)

Usage:
    python tools/video_digest.py URL [URL ...] --browser "chrome:Profile 1"
    python tools/video_digest.py --urls-file data/research/livestreams.txt --browser chrome --summarize
    python tools/video_digest.py --audio-file some_local.m4a          # transcribe a file you already have

--browser  : read cookies from your logged-in Chrome profile so Facebook videos that need login work.
             Close that Chrome profile first if yt-dlp says the cookie database is locked.
             Find the profile folder name at chrome://version  ("Profile Path" ends with e.g. "Profile 3").
Outputs (default data/research/video_digest/<id>/):
    audio.*, transcript.txt (timestamped), transcript.srt, meta.json, summary.md (with --summarize)

Respect the creator: keep downloads private, for your own study, and delete audio when done (--delete-audio).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SUMMARY_PROMPT = """Bạn là trợ lý nghiên cứu. Dưới đây là transcript (tự động, có thể sai chính tả) của một video/livestream.
Hãy viết bản tóm tắt tiếng Việt, trung thực, chỉ dựa trên transcript:
1. Chủ đề chính (3-5 dòng)
2. Các ý chính theo mốc thời gian [hh:mm:ss] (tối đa 25 gạch đầu dòng)
3. Quy trình / công cụ / con số cụ thể được nhắc tới (bảng: hạng mục | chi tiết | mốc thời gian)
4. Lời khuyên / bài học có thể áp dụng cho một studio sản xuất video tự động
5. Những tuyên bố chưa kiểm chứng được (ghi rõ là tự công bố)
6. Phần nào transcript không rõ nghĩa
Không bịa thêm thông tin không có trong transcript.

TRANSCRIPT:
"""


def ts(sec: float, srt: bool = False) -> str:
    h, rem = divmod(max(sec, 0.0), 3600)
    m, s = divmod(rem, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"


def safe_id(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", text)[:60].strip("_") or "video"


class TooShort(Exception):
    pass


def download_audio(url: str, out_root: Path, browser: str | None, min_seconds: float = 0) -> tuple[Path, dict]:
    if shutil.which("yt-dlp") is None and shutil.which("yt-dlp.exe") is None:
        raise RuntimeError("yt-dlp not found: pip install -U yt-dlp")
    probe = ["yt-dlp", "--dump-single-json", "--no-playlist", url]
    if browser:
        probe[1:1] = ["--cookies-from-browser", browser]
    p = subprocess.run(probe, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"yt-dlp probe failed: {p.stderr.strip()[-400:]}")
    info = json.loads(p.stdout)
    vid = safe_id(str(info.get("id") or info.get("display_id") or url))
    folder = out_root / vid
    folder.mkdir(parents=True, exist_ok=True)
    meta = {k: info.get(k) for k in ("id", "title", "uploader", "upload_date", "duration", "webpage_url",
                                     "description", "view_count")}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    dur = info.get("duration")
    if min_seconds and dur is not None and float(dur) < min_seconds:
        raise TooShort(f"{vid} {float(dur):.0f}s < {min_seconds:.0f}s")
    existing = sorted(folder.glob("audio.*"))
    if existing:
        return existing[0], meta
    cmd = ["yt-dlp", "-f", "bestaudio/best", "-x", "--audio-format", "m4a", "--no-playlist",
           "-N", "8", "-o", str(folder / "audio.%(ext)s"), url]
    if browser:
        cmd[1:1] = ["--cookies-from-browser", browser]
    d = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    files = sorted(folder.glob("audio.*"))
    if d.returncode != 0 or not files:
        raise RuntimeError(f"yt-dlp download failed: {d.stderr.strip()[-400:]}")
    return files[0], meta


def _add_cuda_dll_dirs() -> None:
    """pip-installed nvidia-cublas/cudnn wheels put their DLLs in site-packages/nvidia/*/bin (Windows)."""
    if os.name != "nt":
        return
    import site
    for base in site.getsitepackages() + [site.getusersitepackages()]:
        for sub in ("cublas", "cudnn", "cuda_runtime", "cuda_nvrtc"):
            d = Path(base) / "nvidia" / sub / "bin"
            if d.is_dir():
                os.environ["PATH"] = str(d) + os.pathsep + os.environ.get("PATH", "")
                try:
                    os.add_dll_directory(str(d))
                except Exception:  # noqa: BLE001
                    pass


def load_model(name: str, device: str):
    _add_cuda_dll_dirs()
    from faster_whisper import WhisperModel  # imported lazily so --help works without it
    if device in ("auto", "cuda"):
        try:
            model = WhisperModel(name, device="cuda", compute_type="float16")
            try:  # batched inference is several times faster on GPU (faster-whisper >= 1.1)
                from faster_whisper import BatchedInferencePipeline
                return BatchedInferencePipeline(model=model), "cuda-batched"
            except Exception:  # noqa: BLE001
                return model, "cuda"
        except Exception as exc:  # noqa: BLE001
            if device == "cuda":
                raise
            print(f"[warn] CUDA unavailable ({exc}); falling back to CPU int8 (slower)")
    cpu_model = name if name not in ("large-v3", "large-v3-turbo") else "small"
    return WhisperModel(cpu_model, device="cpu", compute_type="int8"), "cpu"


def transcribe(audio: Path, model, language: str | None) -> tuple[list[tuple[float, float, str]], dict]:
    kwargs = dict(language=language, vad_filter=True, beam_size=1, condition_on_previous_text=False)
    if model.__class__.__name__ == "BatchedInferencePipeline":
        kwargs.pop("condition_on_previous_text")
        kwargs["batch_size"] = 8
    segments, info = model.transcribe(str(audio), **kwargs)
    out = []
    for seg in segments:
        text = seg.text.strip()
        if text:
            out.append((seg.start, seg.end, text))
            if len(out) % 50 == 0:
                print(f"  ... {ts(seg.end)} transcribed", flush=True)
    return out, {"language": info.language, "duration": info.duration}


def write_transcripts(folder: Path, segs: list[tuple[float, float, str]]) -> Path:
    txt = folder / "transcript.txt"
    # merge into ~30 s paragraphs: easier for humans and for Claude
    lines, buf, start = [], [], None
    for s, e, t in segs:
        start = s if start is None else start
        buf.append(t)
        if e - start >= 30:
            lines.append(f"[{ts(start)}] {' '.join(buf)}")
            buf, start = [], None
    if buf:
        lines.append(f"[{ts(start or 0)}] {' '.join(buf)}")
    txt.write_text("\n".join(lines), encoding="utf-8")
    srt = folder / "transcript.srt"
    srt.write_text("\n".join(f"{i}\n{ts(s, True)} --> {ts(e, True)}\n{t}\n"
                             for i, (s, e, t) in enumerate(segs, 1)), encoding="utf-8")
    return txt


def summarize(folder: Path, transcript: Path, meta: dict) -> Path | None:
    claude = shutil.which("claude") or shutil.which("claude.cmd")
    if not claude:
        print("[info] claude CLI not found; skip summary (ask Claude in chat to summarize transcript.txt)")
        return None
    text = transcript.read_text(encoding="utf-8")
    header = f"Tiêu đề: {meta.get('title')}\nNguồn: {meta.get('webpage_url')}\nThời lượng: {meta.get('duration')} giây\n\n"
    proc = subprocess.run([claude, "-p", "--max-turns", "1"], input=SUMMARY_PROMPT + header + text,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
    if proc.returncode != 0:
        print(f"[warn] claude summary failed: {proc.stderr[-500:]}")
        return None
    out = folder / "summary.md"
    out.write_text(f"# {meta.get('title')}\n\n{proc.stdout.strip()}\n", encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--urls-file")
    ap.add_argument("--audio-file", help="transcribe a local audio/video file instead of downloading")
    ap.add_argument("--browser", help='cookies source for yt-dlp, e.g. chrome or "chrome:Profile 3"')
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    ap.add_argument("--language", default="vi", help="vi, en ... or 'auto'")
    ap.add_argument("--out", default="data/research/video_digest")
    ap.add_argument("--summarize", action="store_true", help="also write summary.md with Claude Code (claude -p)")
    ap.add_argument("--delete-audio", action="store_true")
    ap.add_argument("--min-seconds", type=float, default=0, help="skip videos shorter than this (e.g. 60)")
    args = ap.parse_args()

    urls = list(args.urls)
    if args.urls_file:
        urls += [u.strip() for u in Path(args.urls_file).read_text(encoding="utf-8").splitlines()
                 if u.strip() and not u.startswith("#")]
    if not urls and not args.audio_file:
        ap.error("give at least one URL, --urls-file or --audio-file")
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    language = None if args.language == "auto" else args.language

    log_path = out_root / "run.log"

    def log(msg: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    model, device = load_model(args.model, args.device)
    log(f"[whisper] model={args.model} device={device} videos={len(urls) + (1 if args.audio_file else 0)}")

    def process(audio: Path, meta: dict, folder: Path) -> None:
        t0 = time.time()
        segs, info = transcribe(audio, model, language)
        txt = write_transcripts(folder, segs)
        dur = info.get("duration") or 0
        log(f"[transcribe] {folder.name}: {dur / 60:.1f} min audio in {(time.time() - t0) / 60:.1f} min "
            f"({len(segs)} segments)")
        if args.summarize:
            s = summarize(folder, txt, meta)
            if s:
                log(f"[summary] {s}")
        if args.delete_audio and audio.parent == folder:
            audio.unlink(missing_ok=True)

    if args.audio_file:
        a = Path(args.audio_file).resolve()
        folder = out_root / safe_id(a.stem)
        folder.mkdir(parents=True, exist_ok=True)
        process(a, {"title": a.stem, "webpage_url": str(a)}, folder)

    done = failed = short = 0
    for n, url in enumerate(urls, 1):
        vid = safe_id(url.rstrip("/").split("/")[-1].split("v=")[-1])
        if (out_root / vid / "transcript.txt").is_file():
            log(f"[skip] {n}/{len(urls)} {vid} already transcribed")
            done += 1
            continue
        t0 = time.time()
        try:
            audio, meta = download_audio(url, out_root, args.browser, args.min_seconds)
            log(f"[download] {n}/{len(urls)} {meta.get('id')} {meta.get('duration')}s in {time.time() - t0:.0f}s")
            process(audio, meta, audio.parent)
            done += 1
        except TooShort as exc:
            short += 1
            log(f"[short] {n}/{len(urls)} skip {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            log(f"[error] {n}/{len(urls)} {url}: {str(exc)[-300:]}")
    log(f"[done] ok={done} short_skipped={short} failed={failed}")
    return 0 if done else 1


if __name__ == "__main__":
    sys.exit(main())
