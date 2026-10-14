from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from .knowledge import ToolEnvironment


class ToolSkillSpec(BaseModel):
    skill_id: str
    tool_id: str
    craft_skill: str
    operations: list[str] = Field(default_factory=list)
    required_versions: list[str] = Field(default_factory=list)
    validation_tasks: list[str] = Field(default_factory=list)
    automation_interfaces: list[str] = Field(default_factory=list)
    production_ready: bool = False


DEFAULT_TOOL_SKILLS: list[ToolSkillSpec] = [
    ToolSkillSpec(
        skill_id="tool.blender.production",
        tool_id="blender",
        craft_skill="3d-production",
        operations=[
            "scene assembly", "rigging", "animation", "camera", "lighting",
            "render", "compositing", "asset conversion", "headless batch",
        ],
        automation_interfaces=["Python bpy", "command line background mode"],
        validation_tasks=["open scene", "execute python", "render test frame", "verify output"],
    ),
    ToolSkillSpec(
        skill_id="tool.premiere.editorial",
        tool_id="premiere",
        craft_skill="editorial",
        operations=[
            "import media", "create sequence", "place clip", "trim", "markers",
            "captions", "audio edit", "effects", "export",
        ],
        automation_interfaces=["UXP API"],
        validation_tasks=["create sandbox sequence", "perform deterministic edit", "export", "ffprobe verify"],
    ),
    ToolSkillSpec(
        skill_id="tool.resolve.post",
        tool_id="resolve",
        craft_skill="editorial-color-audio",
        operations=["edit", "Fusion comp", "color", "Fairlight mix", "deliver"],
        automation_interfaces=["scripting API", "project/timeline automation"],
        validation_tasks=["create timeline", "render short master", "verify media"],
    ),
    ToolSkillSpec(
        skill_id="tool.aftereffects.motion",
        tool_id="aftereffects",
        craft_skill="motion-graphics-vfx",
        operations=["compositions", "layers", "keyframes", "expressions", "templates", "render queue"],
        automation_interfaces=["ExtendScript/JavaScript", "aerender", "plugin APIs"],
        validation_tasks=["populate template", "aerender", "verify output"],
    ),
    ToolSkillSpec(
        skill_id="tool.photoshop.image",
        tool_id="photoshop",
        craft_skill="production-design-packaging",
        operations=["layers", "masks", "smart objects", "text", "composite", "thumbnail", "batch export"],
        automation_interfaces=["UXP scripting"],
        validation_tasks=["open sandbox PSD", "replace asset", "export PNG", "verify dimensions"],
    ),
    ToolSkillSpec(
        skill_id="tool.canva.packaging",
        tool_id="canva",
        craft_skill="fast-design-packaging",
        operations=["brand template", "text replacement", "asset replacement", "social derivative", "export"],
        automation_interfaces=["Canva developer APIs / connected app where available"],
        validation_tasks=["apply brand constraints", "export design", "verify output"],
    ),
    ToolSkillSpec(
        skill_id="tool.unreal.realtime",
        tool_id="unreal",
        craft_skill="realtime-3d",
        operations=["level assembly", "Sequencer", "camera", "lighting", "Movie Render Pipeline"],
        automation_interfaces=["Python", "Movie Render Queue/Graph", "editor scripting"],
        validation_tasks=["open sandbox project", "render Sequencer shot", "verify frames"],
    ),
    ToolSkillSpec(
        skill_id="tool.ffmpeg.post",
        tool_id="ffmpeg",
        craft_skill="editorial-delivery",
        operations=["probe", "transcode", "concat", "filter", "audio mix", "captions", "master", "delivery QC"],
        automation_interfaces=["command line", "ffprobe", "filtergraph"],
        validation_tasks=["generate test media", "probe", "concat", "transcode", "verify output"],
    ),
    ToolSkillSpec(
        skill_id="tool.comfyui.generative",
        tool_id="comfyui",
        craft_skill="generative-media",
        operations=["workflow load", "node validation", "prompt queue", "seed control", "output collection", "provenance"],
        automation_interfaces=["local server", "workflow JSON", "websocket events"],
        validation_tasks=["load local workflow", "validate nodes/models", "queue render", "collect deterministic output"],
    ),
]


class ToolDoctor:
    """Version-aware local tool discovery. It reports capability; it never installs silently."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    @staticmethod
    def _first_existing(patterns: list[str]) -> str | None:
        for pattern in patterns:
            expanded = os.path.expandvars(pattern)
            matches = sorted(glob.glob(expanded))
            for match in matches:
                if Path(match).exists():
                    return str(Path(match))
        return None

    @staticmethod
    def _version_from_command(path: str, args: list[str]) -> str | None:
        try:
            proc = subprocess.run(
                [path, *args],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        except Exception:
            return None
        text = (proc.stdout or proc.stderr or "").strip().splitlines()
        return text[0][:200] if text else None

    def inspect(self, tool_id: str) -> ToolEnvironment:
        tool = tool_id.lower()
        if tool == "blender":
            portable = sorted((self.root / ".tools").glob("blender*/blender.exe"))
            path = str(portable[0]) if portable else shutil.which("blender")
            return ToolEnvironment(
                tool_id="blender",
                installed=bool(path),
                version=self._version_from_command(path, ["--version"]) if path else None,
                executable_path=path,
                capabilities={"python", "headless", "3d", "animation", "camera", "render"} if path else set(),
            )
        if tool == "ffmpeg":
            path = shutil.which("ffmpeg")
            return ToolEnvironment(
                tool_id="ffmpeg",
                installed=bool(path),
                version=self._version_from_command(path, ["-version"]) if path else None,
                executable_path=path,
                capabilities={"encode", "probe", "filters"} if path else set(),
            )
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        patterns = {
            "premiere": [str(Path(program_files) / "Adobe" / "Adobe Premiere Pro *" / "Adobe Premiere Pro.exe")],
            "aftereffects": [str(Path(program_files) / "Adobe" / "Adobe After Effects *" / "Support Files" / "AfterFX.exe")],
            "photoshop": [str(Path(program_files) / "Adobe" / "Adobe Photoshop *" / "Photoshop.exe")],
            "resolve": [str(Path(program_files) / "Blackmagic Design" / "DaVinci Resolve" / "Resolve.exe")],
            "unreal": [str(Path(program_files) / "Epic Games" / "UE_*" / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe")],
        }
        if tool in patterns:
            path = self._first_existing(patterns[tool])
            if tool == "aftereffects":
                aerender = (
                    str(Path(path).parent / "aerender.exe")
                    if path
                    and (Path(path).parent / "aerender.exe").is_file()
                    else None
                )
                version = (
                    self._version_from_command(aerender, ["-version"])
                    if aerender
                    else None
                )
                capabilities = set()
                if path:
                    capabilities.update(
                        {
                            "compositions",
                            "layers",
                            "keyframes",
                            "expressions",
                            "templates",
                        }
                    )
                if aerender:
                    capabilities.add("render_queue")
                issues = []
                if path and not aerender:
                    issues.append(
                        "AfterFX.exe found but aerender.exe is missing from Support Files."
                    )
                return ToolEnvironment(
                    tool_id=tool,
                    installed=bool(path),
                    version=version,
                    executable_path=path,
                    capabilities=capabilities,
                    known_issues=issues,
                )
            if tool == "unreal":
                command = (
                    str(Path(path).parent / "UnrealEditor-Cmd.exe")
                    if path
                    and (Path(path).parent / "UnrealEditor-Cmd.exe").is_file()
                    else None
                )
                version = (
                    self._version_from_command(command, ["-version"])
                    if command
                    else None
                )
                capabilities = set()
                if path:
                    capabilities.update(
                        {
                            "level_assembly",
                            "sequencer",
                            "camera",
                            "lighting",
                        }
                    )
                if command:
                    capabilities.update(
                        {
                            "python_scripting",
                            "movie_render_pipeline",
                        }
                    )
                issues = []
                if path and not command:
                    issues.append(
                        "UnrealEditor.exe found but UnrealEditor-Cmd.exe is missing."
                    )
                return ToolEnvironment(
                    tool_id=tool,
                    installed=bool(path),
                    version=version,
                    executable_path=path,
                    capabilities=capabilities,
                    known_issues=issues,
                )
            if tool == "resolve":
                program_data = os.environ.get(
                    "PROGRAMDATA",
                    r"C:\ProgramData",
                )
                scripting_roots = [
                    os.environ.get("RESOLVE_SCRIPT_API", ""),
                    str(
                        Path(program_data)
                        / "Blackmagic Design"
                        / "DaVinci Resolve"
                        / "Support"
                        / "Developer"
                        / "Scripting"
                    ),
                ]
                module_path = self._first_existing(
                    [
                        str(Path(root) / "Modules" / "DaVinciResolveScript.py")
                        for root in scripting_roots
                        if root
                    ]
                )
                readme_path = self._first_existing(
                    [
                        str(Path(root) / "README.txt")
                        for root in scripting_roots
                        if root
                    ]
                )
                api_version = None
                if readme_path:
                    try:
                        lines = Path(readme_path).read_text(
                            encoding="utf-8",
                            errors="ignore",
                        ).splitlines()
                        api_version = next(
                            (
                                line.strip()
                                for line in lines[:20]
                                if "Last Updated" in line
                            ),
                            None,
                        )
                    except OSError:
                        api_version = None
                capabilities = set()
                if path:
                    capabilities.update(
                        {
                            "edit",
                            "fusion",
                            "color",
                            "fairlight",
                            "deliver",
                        }
                    )
                if module_path:
                    capabilities.add("python_scripting")
                issues = []
                if path and not module_path:
                    issues.append(
                        "Resolve executable found but DaVinciResolveScript.py was not found in the configured/default Developer/Scripting path."
                    )
                return ToolEnvironment(
                    tool_id=tool,
                    installed=bool(path),
                    api_version=api_version,
                    executable_path=path,
                    capabilities=capabilities,
                    known_issues=issues,
                )
            return ToolEnvironment(tool_id=tool, installed=bool(path), executable_path=path)
        if tool == "comfyui":
            user_profile = os.environ.get("USERPROFILE", str(Path.home()))
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            candidates = [
                str(self.root / ".tools" / "ComfyUI" / "main.py"),
                str(self.root / ".tools" / "comfyui" / "main.py"),
                str(Path(user_profile) / "ComfyUI" / "main.py"),
                str(Path(user_profile) / "Downloads" / "ComfyUI*" / "main.py"),
                str(Path(user_profile) / "Desktop" / "ComfyUI*" / "main.py"),
            ]
            if local_appdata:
                candidates.extend([
                    str(Path(local_appdata) / "Programs" / "ComfyUI*" / "resources" / "ComfyUI" / "main.py"),
                    str(Path(local_appdata) / "ComfyUI*" / "main.py"),
                ])
            path = self._first_existing(candidates)
            version = None
            if path:
                version_file = Path(path).parent / "comfyui_version.py"
                if version_file.is_file():
                    try:
                        match = re.search(
                            r'__version__\s*=\s*["\']([^"\']+)["\']',
                            version_file.read_text(
                                encoding="utf-8",
                                errors="ignore",
                            ),
                        )
                        version = match.group(1) if match else None
                    except OSError:
                        version = None
            return ToolEnvironment(
                tool_id="comfyui",
                installed=bool(path),
                version=version,
                executable_path=path,
                capabilities={
                    "workflow_json",
                    "local_service",
                    "prompt_queue",
                    "provenance",
                } if path else set(),
                known_issues=[] if path else [
                    "ComfyUI local main.py was not found in configured/common locations."
                ],
            )
        if tool == "canva":
            return ToolEnvironment(
                tool_id="canva",
                installed=False,
                executable_path=None,
                known_issues=["Canva is treated as an optional connected/design capability, not a core local dependency."],
            )
        return ToolEnvironment(tool_id=tool, installed=False, known_issues=["unknown tool"])


class ToolSkillRegistry:
    def __init__(self, skills: list[ToolSkillSpec] | None = None) -> None:
        self._items = {item.skill_id: item for item in (skills or DEFAULT_TOOL_SKILLS)}

    def list(self, tool_id: str | None = None) -> list[ToolSkillSpec]:
        values = list(self._items.values())
        if tool_id is not None:
            values = [x for x in values if x.tool_id == tool_id]
        return sorted(values, key=lambda x: x.skill_id)

    def mark_validated(self, skill_id: str) -> ToolSkillSpec:
        item = self._items[skill_id].model_copy(deep=True)
        item.production_ready = True
        self._items[skill_id] = item
        return item
