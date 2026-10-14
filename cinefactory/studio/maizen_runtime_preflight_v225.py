"""v225 local read-only capture readiness check; no sessions, purchases or jobs.

Detects standard installed locations and local loopback OBS WebSocket listening
only. A found binary/port is not an authenticated OBS connection; Minecraft
rights/account/second actor/session are NOT verified here.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import socket
import sys

STANDARD_OBS_PATH=Path(r"C:\Program Files\obs-studio\bin\64bit\obs64.exe")
STANDARD_MC_INSTALLER=Path(r"C:\Program Files\Minecraft Launcher\MinecraftLauncher.exe")

def maizen_runtime_readiness() -> dict:
    obs=str(STANDARD_OBS_PATH) if STANDARD_OBS_PATH.is_file() else shutil.which("obs64.exe")
    ffmpeg=shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    java=shutil.which("java") or shutil.which("java.exe")
    node=shutil.which("node") or shutil.which("node.exe")
    minecraft_profile=Path(os.environ.get("APPDATA",""))/".minecraft"
    launcher=str(STANDARD_MC_INSTALLER) if STANDARD_MC_INSTALLER.is_file() else shutil.which("MinecraftLauncher.exe")
    # Socket dial probes port availability, not authentication, credentials
    # or starting recording. No user-controlled host or port is accepted.
    websocket_open=False
    try:
        with socket.create_connection(("127.0.0.1",4455), timeout=0.3):
            websocket_open=True
    except OSError:
        pass
    return {
        "schema":"cine.minecraft.maizen_runtime_readiness.v225",
        "scope":"READ_ONLY_STANDARD_PATH_AND_LOOPBACK_CHECK",
        "obs_studio_binary_found":bool(obs),
        "obs_studio_path":obs,
        "obs_websocket_port_4455_listening":websocket_open,
        "obs_websocket_authenticated":False,
        "obs_recording_verified":False,
        "ffmpeg_found":bool(ffmpeg),
        "java_on_path":bool(java),
        "node_on_path":bool(node),
        "minecraft_java_default_profile_exists":minecraft_profile.is_dir(),
        "minecraft_launcher_standard_location_found":bool(launcher),
        "game_license_verified":False,
        "game_version_and_mods_verified":False,
        "world_and_two_actors_verified":False,
        "replaymod_or_flashback_validated":False,
        "capture_45s_qualified":False,
        "capture_pipeline_live":False,
        "caveat":"No standardized path evidence does not prove game absent; binary presence does not prove app running/license or functional footage.",
        "next_actions":[
            "Verify a legitimately licensed Minecraft Java game instance and Java/runtime version",
            "Choose pinned Minecraft/Fabric and ONE verified replay camera mod (ReplayMod or Flashback)",
            "Create an original world, two authorized performers, and an in-game take",
            "Launch OBS intentionally; enable password-authenticated local WebSocket only if needed",
            "Record a real 10s then 45s H264/AAC test and inspect full moving footage and sound",
        ],
        "external_spend_authorized":False,
        "install_or_launch_performed":False,
    }
