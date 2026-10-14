from __future__ import annotations

from .contracts import LongSlideModuleSpec, LongSlideSceneKind


SCENE_OBSTACLE_COMPATIBILITY: dict[LongSlideSceneKind, set[str]] = {
    LongSlideSceneKind.LONG_SLIDE: {
        "rotating_hammer", "spinning_bar", "ball_pit", "water_pool",
        "break_wall", "bridge", "giant_duck",
    },
    LongSlideSceneKind.SPIRAL_SLIDE: {
        "rotating_hammer", "spinning_bar", "ball_pit", "water_pool",
    },
    LongSlideSceneKind.PAINT_GATE: {
        "paint_gate", "water_pool", "ball_pit",
    },
    LongSlideSceneKind.FOUNTAIN: {
        "water_pool", "paint_gate", "ball_pit",
    },
    LongSlideSceneKind.CAGE: {
        "cage", "break_wall", "bridge",
    },
    LongSlideSceneKind.KEY_DOOR: {
        "cage", "break_wall", "bridge",
    },
    LongSlideSceneKind.BALL_PIT: {
        "ball_pit", "spinning_bar", "rotating_hammer",
    },
    LongSlideSceneKind.GIANT_ANIMAL: {
        "giant_duck", "break_wall", "bridge", "water_pool",
    },
}


class SceneCompatibilityGate:
    @staticmethod
    def compatible(scene_kind: LongSlideSceneKind, obstacle_id: str) -> bool:
        return obstacle_id in SCENE_OBSTACLE_COMPATIBILITY.get(scene_kind, set())

    @classmethod
    def findings(cls, module: LongSlideModuleSpec) -> list[str]:
        return [
            f"INCOMPATIBLE_OBSTACLE:{module.scene_kind.value}:{item.obstacle_id}"
            for item in module.obstacles
            if item.enabled and not cls.compatible(module.scene_kind, item.obstacle_id)
        ]
