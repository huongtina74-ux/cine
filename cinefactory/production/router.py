from __future__ import annotations

from dataclasses import dataclass

from cinefactory.domain.enums import ShotComplexity
from cinefactory.domain.models import ShotSpec


@dataclass(frozen=True)
class RouteDecision:
    lane: str
    candidates: int
    reason: str


class ShotRouter:
    """Deterministic first-pass routing. Model choice stays configurable in WorkflowRegistry."""

    def route(self, shot: ShotSpec) -> RouteDecision:
        if shot.complexity == ShotComplexity.GREEN:
            return RouteDecision("standard_i2v", 1, "simple readable shot")
        if shot.complexity == ShotComplexity.YELLOW:
            return RouteDecision("controlled_i2v", 2, "moderate motion/continuity risk")
        if shot.complexity == ShotComplexity.RED:
            return RouteDecision("high_control", 3, "complex action or multi-subject interaction")
        return RouteDecision("hero", 4, "hero/emotional shot merits more takes")
