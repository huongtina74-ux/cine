from __future__ import annotations

import re
from enum import StrEnum

from pydantic import BaseModel, Field


class WorkflowFamily(StrEnum):
    ANIMATION = "ANIMATION"
    MACHINIMA = "MACHINIMA"
    GAMEPLAY = "GAMEPLAY"
    AI_VISUAL = "AI_VISUAL"
    SCREEN_COMMENTARY = "SCREEN_COMMENTARY"
    HYBRID = "HYBRID"


class WorldTarget(StrEnum):
    MINECRAFT = "MINECRAFT"
    ROBLOX = "ROBLOX"
    GENERIC = "GENERIC"
    NONE = "NONE"


class ContentPattern(StrEnum):
    STORY = "STORY"
    CINEMATIC = "CINEMATIC"
    ROLEPLAY = "ROLEPLAY"
    CHALLENGE = "CHALLENGE"
    BUILD_BATTLE = "BUILD_BATTLE"
    SURVIVAL = "SURVIVAL"
    HUNDRED_DAYS = "HUNDRED_DAYS"
    PRANK = "PRANK"
    GAMEPLAY_GOAL = "GAMEPLAY_GOAL"
    TUTORIAL = "TUTORIAL"
    GUIDE = "GUIDE"
    COMMENTARY = "COMMENTARY"
    REVIEW = "REVIEW"
    EXPLAINER = "EXPLAINER"
    MUSIC = "MUSIC"
    MEME = "MEME"
    SHORTS = "SHORTS"

class CaptureMode(StrEnum):
    DIRECT_RENDER = "DIRECT_RENDER"
    REPLAY_MULTI_CAMERA = "REPLAY_MULTI_CAMERA"
    GAME_CAPTURE = "GAME_CAPTURE"
    SCREEN_CAPTURE = "SCREEN_CAPTURE"
    HYBRID = "HYBRID"


class BackendKind(StrEnum):
    BLENDER = "BLENDER"
    MINECRAFT_RUNTIME = "MINECRAFT_RUNTIME"
    ROBLOX_STUDIO = "ROBLOX_STUDIO"
    ROBLOX_LIVE = "ROBLOX_LIVE"
    COMFYUI = "COMFYUI"
    SCREEN_CAPTURE = "SCREEN_CAPTURE"
    HYBRID_ROUTER = "HYBRID_ROUTER"


class BackendCapability(BaseModel):
    backend: BackendKind
    executable: bool
    workflow_families: set[WorkflowFamily] = Field(default_factory=set)
    worlds: set[WorldTarget] = Field(default_factory=set)
    capture_modes: set[CaptureMode] = Field(default_factory=set)
    notes: list[str] = Field(default_factory=list)

class ProductionIntent(BaseModel):
    workflow_family: WorkflowFamily
    world: WorldTarget = WorldTarget.NONE
    content_pattern: ContentPattern = ContentPattern.STORY
    capture_mode: CaptureMode = CaptureMode.DIRECT_RENDER
    backend: BackendKind
    executable: bool
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


DEFAULT_BACKEND_CAPABILITIES: dict[BackendKind, BackendCapability] = {
    BackendKind.BLENDER: BackendCapability(
        backend=BackendKind.BLENDER,
        executable=True,
        workflow_families={WorkflowFamily.ANIMATION, WorkflowFamily.MACHINIMA},
        worlds={WorldTarget.GENERIC, WorldTarget.MINECRAFT, WorldTarget.ROBLOX},
        capture_modes={CaptureMode.DIRECT_RENDER, CaptureMode.REPLAY_MULTI_CAMERA},
    ),
    BackendKind.COMFYUI: BackendCapability(
        backend=BackendKind.COMFYUI,
        executable=True,
        workflow_families={WorkflowFamily.AI_VISUAL},
        worlds={WorldTarget.GENERIC, WorldTarget.MINECRAFT, WorldTarget.ROBLOX, WorldTarget.NONE},
        capture_modes={CaptureMode.DIRECT_RENDER},
    ),
    BackendKind.MINECRAFT_RUNTIME: BackendCapability(
        backend=BackendKind.MINECRAFT_RUNTIME,
        executable=False,
        workflow_families={WorkflowFamily.GAMEPLAY, WorkflowFamily.MACHINIMA},
        worlds={WorldTarget.MINECRAFT},
        capture_modes={CaptureMode.GAME_CAPTURE, CaptureMode.REPLAY_MULTI_CAMERA},
        notes=["Runtime adapter is planned; never silently substitute another backend."],
    ),
    BackendKind.ROBLOX_STUDIO: BackendCapability(
        backend=BackendKind.ROBLOX_STUDIO,
        executable=False,
        workflow_families={WorkflowFamily.MACHINIMA},
        worlds={WorldTarget.ROBLOX},
        capture_modes={CaptureMode.REPLAY_MULTI_CAMERA, CaptureMode.GAME_CAPTURE},
    ),
    BackendKind.ROBLOX_LIVE: BackendCapability(
        backend=BackendKind.ROBLOX_LIVE,
        executable=False,
        workflow_families={WorkflowFamily.GAMEPLAY},
        worlds={WorldTarget.ROBLOX},
        capture_modes={CaptureMode.GAME_CAPTURE},
    ),
    BackendKind.SCREEN_CAPTURE: BackendCapability(
        backend=BackendKind.SCREEN_CAPTURE,
        executable=False,
        workflow_families={WorkflowFamily.SCREEN_COMMENTARY},
        worlds={WorldTarget.NONE, WorldTarget.GENERIC},
        capture_modes={CaptureMode.SCREEN_CAPTURE},
    ),
    BackendKind.HYBRID_ROUTER: BackendCapability(
        backend=BackendKind.HYBRID_ROUTER,
        executable=False,
        workflow_families={WorkflowFamily.HYBRID},
        worlds={WorldTarget.NONE, WorldTarget.GENERIC, WorldTarget.MINECRAFT, WorldTarget.ROBLOX},
        capture_modes={CaptureMode.HYBRID},
    ),
}


def backend_capabilities() -> list[BackendCapability]:
    return list(DEFAULT_BACKEND_CAPABILITIES.values())

class ProductionIntentRouter:
    _minecraft = re.compile(r"\bminecraft\b|\bmaizen\b|\bcreeper\b", re.I)
    _roblox = re.compile(r"\broblox\b|\br6\b|\br15\b", re.I)

    @staticmethod
    def _pattern(text: str) -> ContentPattern:
        t = text.lower()
        checks = [
            (("100 days", "hundred days"), ContentPattern.HUNDRED_DAYS),
            (("build battle",), ContentPattern.BUILD_BATTLE),
            (("survival",), ContentPattern.SURVIVAL),
            (("prank",), ContentPattern.PRANK),
            (("tutorial", "how to", "hướng dẫn"), ContentPattern.TUTORIAL),
            (("review", "đánh giá"), ContentPattern.REVIEW),
            (("explain", "giải thích"), ContentPattern.EXPLAINER),
            (("commentary", "bình luận"), ContentPattern.COMMENTARY),
            (("challenge", "thử thách"), ContentPattern.CHALLENGE),
            (("roleplay", "role play"), ContentPattern.ROLEPLAY),
            (("cinematic", "film", "movie", "phim"), ContentPattern.CINEMATIC),
        ]
        for needles, value in checks:
            if any(x in t for x in needles):
                return value
        return ContentPattern.STORY

    @classmethod
    def _world(cls, text: str) -> WorldTarget:
        if cls._minecraft.search(text):
            return WorldTarget.MINECRAFT
        if cls._roblox.search(text):
            return WorldTarget.ROBLOX
        return WorldTarget.NONE

    def route(
        self,
        prompt: str,
        *,
        workflow_family: WorkflowFamily | None = None,
        world: WorldTarget | None = None,
        backend: BackendKind | None = None,
    ) -> ProductionIntent:
        detected_world = world or self._world(prompt)
        pattern = self._pattern(prompt)
        text = prompt.lower()

        if workflow_family is None:
            if any(x in text for x in ("screen recording", "screen capture", "desktop tutorial", "record my screen")):
                workflow_family = WorkflowFamily.SCREEN_COMMENTARY
            elif any(x in text for x in ("gameplay", "play the game", "100 days", "survival challenge")):
                workflow_family = WorkflowFamily.GAMEPLAY
            elif any(x in text for x in ("ai video", "generated video", "text to video")):
                workflow_family = WorkflowFamily.AI_VISUAL
            elif any(x in text for x in ("hybrid", "mixed media", "gameplay + animation", "gameplay and animation")):
                workflow_family = WorkflowFamily.HYBRID
            elif detected_world in {WorldTarget.MINECRAFT, WorldTarget.ROBLOX} and any(
                x in text for x in ("machinima", "runtime cinematic", "in-game cinematic")
            ):
                workflow_family = WorkflowFamily.MACHINIMA
            else:
                workflow_family = WorkflowFamily.ANIMATION

        selected = backend or self._select_backend(workflow_family, detected_world)
        cap = DEFAULT_BACKEND_CAPABILITIES[selected]
        capture = self._capture_mode(workflow_family, selected)
        warnings = [] if cap.executable else [f"BACKEND_NOT_YET_EXECUTABLE:{selected.value}"]
        return ProductionIntent(
            workflow_family=workflow_family,
            world=detected_world,
            content_pattern=pattern,
            capture_mode=capture,
            backend=selected,
            executable=cap.executable,
            reasons=[f"family={workflow_family.value}", f"world={detected_world.value}", f"pattern={pattern.value}"],
            warnings=warnings,
        )

    @staticmethod
    def _select_backend(family: WorkflowFamily, world: WorldTarget) -> BackendKind:
        if family is WorkflowFamily.GAMEPLAY:
            if world is WorldTarget.MINECRAFT:
                return BackendKind.MINECRAFT_RUNTIME
            if world is WorldTarget.ROBLOX:
                return BackendKind.ROBLOX_LIVE
            return BackendKind.HYBRID_ROUTER
        if family is WorkflowFamily.MACHINIMA:
            if world is WorldTarget.ROBLOX:
                return BackendKind.ROBLOX_STUDIO
            if world is WorldTarget.MINECRAFT:
                return BackendKind.MINECRAFT_RUNTIME
            return BackendKind.BLENDER
        if family is WorkflowFamily.AI_VISUAL:
            return BackendKind.COMFYUI
        if family is WorkflowFamily.SCREEN_COMMENTARY:
            return BackendKind.SCREEN_CAPTURE
        if family is WorkflowFamily.HYBRID:
            return BackendKind.HYBRID_ROUTER
        return BackendKind.BLENDER

    @staticmethod
    def _capture_mode(family: WorkflowFamily, backend: BackendKind) -> CaptureMode:
        if family is WorkflowFamily.GAMEPLAY:
            return CaptureMode.GAME_CAPTURE
        if family is WorkflowFamily.SCREEN_COMMENTARY:
            return CaptureMode.SCREEN_CAPTURE
        if family is WorkflowFamily.HYBRID:
            return CaptureMode.HYBRID
        if backend in {BackendKind.MINECRAFT_RUNTIME, BackendKind.ROBLOX_STUDIO}:
            return CaptureMode.REPLAY_MULTI_CAMERA
        return CaptureMode.DIRECT_RENDER
