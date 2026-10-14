from __future__ import annotations

import shutil
from pathlib import Path

from cinefactory.studio.capabilities import CapabilityProvider, CapabilityRegistry
from cinefactory.studio.contracts import CapabilityKind, CapabilityStatus


def _provider(
    provider_id: str,
    kind: CapabilityKind,
    *,
    executable: bool,
    local: bool = True,
    deterministic: bool | None = None,
    commercial_safe: bool | None = None,
    quality: float = 0.5,
    speed: float = 0.5,
    control: float = 0.5,
    vram_gb: float | None = None,
    notes: list[str] | None = None,
) -> CapabilityProvider:
    return CapabilityProvider(
        provider_id=provider_id,
        kind=kind,
        status=CapabilityStatus.EXECUTABLE if executable else CapabilityStatus.PLANNED,
        executable=executable,
        local=local,
        deterministic=deterministic,
        commercial_safe=commercial_safe,
        quality_score=quality,
        speed_score=speed,
        control_score=control,
        vram_gb=vram_gb,
        limitations=notes or [],
    )

def build_default_capability_registry(root: Path) -> CapabilityRegistry:
    registry = CapabilityRegistry()
    portable_blenders = list((root / ".tools").glob("blender*/blender.exe"))
    blender_available = bool(portable_blenders) or shutil.which("blender") is not None
    ffmpeg_available = shutil.which("ffmpeg") is not None

    registry.register(_provider(
        "blender.local",
        CapabilityKind.OFFLINE_3D,
        executable=blender_available,
        deterministic=True,
        commercial_safe=True,
        quality=0.86,
        speed=0.72,
        control=0.96,
        vram_gb=12.0,
        notes=[] if blender_available else ["Blender executable not found."],
    ))
    registry.register(_provider(
        "ffmpeg.editorial",
        CapabilityKind.EDITORIAL,
        executable=ffmpeg_available,
        deterministic=True,
        commercial_safe=True,
        quality=0.78,
        speed=0.96,
        control=0.92,
        notes=[] if ffmpeg_available else ["FFmpeg executable not found."],
    ))
    registry.register(_provider(
        "ffmpeg.qc",
        CapabilityKind.QC,
        executable=ffmpeg_available,
        deterministic=True,
        commercial_safe=True,
        quality=0.82,
        speed=0.95,
        control=0.94,
    ))
    registry.register(_provider(
        "comfyui.local.image",
        CapabilityKind.AI_IMAGE,
        executable=True,
        deterministic=False,
        commercial_safe=None,
        quality=0.78,
        speed=0.64,
        control=0.72,
        vram_gb=12.0,
        notes=["Runtime health and exact model license must pass preflight."],
    ))
    registry.register(_provider(
        "comfyui.local.video",
        CapabilityKind.AI_VIDEO,
        executable=True,
        deterministic=False,
        commercial_safe=None,
        quality=0.72,
        speed=0.38,
        control=0.58,
        vram_gb=12.0,
        notes=["Runtime health and exact model license must pass preflight."],
    ))
    planned = [
        ("unreal.local", CapabilityKind.REALTIME_3D, True, 0.94, 0.72, 0.90),
        ("minecraft.runtime", CapabilityKind.GAME_RUNTIME, True, 0.92, 0.82, 0.92),
        ("roblox.studio", CapabilityKind.GAME_RUNTIME, True, 0.91, 0.84, 0.91),
        ("roblox.live", CapabilityKind.GAME_RUNTIME, False, 0.90, 0.80, 0.82),
        ("screen.capture", CapabilityKind.SCREEN_CAPTURE, True, 0.88, 0.94, 0.94),
        ("resolve.editorial", CapabilityKind.EDITORIAL, True, 0.96, 0.78, 0.94),
        ("resolve.color", CapabilityKind.COLOR, True, 0.97, 0.72, 0.96),
        ("fusion.motion", CapabilityKind.MOTION_GRAPHICS, True, 0.95, 0.68, 0.94),
        ("fusion.compositing", CapabilityKind.COMPOSITING, True, 0.96, 0.68, 0.95),
        ("premiere.editorial", CapabilityKind.EDITORIAL, True, 0.95, 0.82, 0.93),
        ("aftereffects.motion", CapabilityKind.MOTION_GRAPHICS, True, 0.96, 0.62, 0.94),
        ("aftereffects.compositing", CapabilityKind.COMPOSITING, True, 0.96, 0.60, 0.94),
        ("photoshop.image_edit", CapabilityKind.IMAGE_EDIT, True, 0.96, 0.76, 0.95),
        ("canva.design", CapabilityKind.DESIGN, None, 0.87, 0.91, 0.78),
        ("speech.local", CapabilityKind.SPEECH, True, 0.82, 0.90, 0.90),
        ("music.local", CapabilityKind.MUSIC, False, 0.80, 0.62, 0.66),
        ("sfx.local", CapabilityKind.SFX, True, 0.84, 0.90, 0.90),
        ("lipsync.local", CapabilityKind.LIPSYNC, True, 0.86, 0.72, 0.88),
    ]
    for provider_id, kind, deterministic, quality, speed, control in planned:
        registry.register(_provider(
            provider_id,
            kind,
            executable=False,
            deterministic=deterministic,
            commercial_safe=None,
            quality=quality,
            speed=speed,
            control=control,
            notes=["Runtime adapter may exist; execution still requires local/tool qualification."],
        ))
    return registry
