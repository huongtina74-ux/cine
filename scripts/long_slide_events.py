"""Timed sound cues collected while a Long Slide module is built (no bpy).

FX code records what happens on screen (a coin pops, a ball smashes, a door
opens) and the worker writes the list next to the rendered clip as
`<clip>.events.json`. The episode assembler turns the cues into sound effects
at the exact frame.
"""
from __future__ import annotations

import json
from pathlib import Path

KINDS = {"pickup_pop", "paint_splash", "smash", "door_open", "clone_pop", "race_start", "finish"}

_events: list[dict] = []


def reset() -> None:
    _events.clear()


def record(frame: int, kind: str, **data) -> None:
    if kind not in KINDS:
        raise ValueError(f"unknown sound cue {kind!r}")
    _events.append({"frame": int(frame), "kind": kind, **data})


def events() -> list[dict]:
    return sorted(_events, key=lambda e: (e["frame"], e["kind"]))


def sidecar_path(clip: str | Path) -> Path:
    clip = Path(clip)
    return clip.with_name(clip.stem + ".events.json")


def dump(clip: str | Path, *, fps: int, frames: int) -> Path:
    path = sidecar_path(clip)
    path.write_text(json.dumps({"fps": fps, "frames": frames, "events": events()}, indent=1), encoding="utf-8")
    return path
